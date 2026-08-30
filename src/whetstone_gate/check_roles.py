"""``make check-roles`` — the repository's structural invariants.

These are the properties later chunks *depend on* and that no unit test would otherwise
own, because they are facts about the repository rather than about any module:

  A. ``.gitattributes`` exists, says exactly ``* text=auto eol=lf``, and is **in the first
     commit**. Without it the pre-registration fingerprint fails for every reviewer who
     clones on anything but Windows — silently, at the moment of judging, looking like
     fraud rather than a line-ending bug. The property it buys is asserted two ways: no
     CRLF in any file **git classifies as text**, and — over **every** tracked file, text
     or binary — the working tree and the object store holding the *same bytes*.
  B. No ``.env`` is tracked, and ``.env.example`` carries key **names** with **no values**.
  C. No secret-shaped string appears in any tracked file. (The *history* scan is C21's,
     and its remedy is constrained: revoke at the provider, never rewrite history.)
  D. ``gates/`` and ``scorer/`` share no first-party module. **This one line is the whole
     moat** — in the spike, the gate and the invariant checker both called
     ``world.js:intentKey``, so the invariant could not have fired unless the gate had a
     bug. That is not a result; it is a definition.
  E. Session-token discipline (`PROCESS.md` §7a): no commit carries a token that was never
     issued, and no token is reused across roles or shared by a chunk's build and review.
  F. Outstanding ``TODO_`` sentinels in ``config/`` are reported, so "somebody still owes
     this project a value" is a printed number rather than something to remember.

It exits non-zero on a violation. Checks that cannot yet apply report ``n/a`` with the
reason, and ``n/a`` is never silently a pass.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from . import config as cfg
from ._console import say

GITATTRIBUTES_REQUIRED = "* text=auto eol=lf"

#: Secret shapes. Each requires a PAYLOAD, never a bare prefix — `CONTEXT.md` §13.1 and
#: this repository's own prose both mention `rzp_live_` as a word, and a scanner that
#: fired on the word would be untrustworthy on its first run and disabled by its second.
SECRET_PATTERNS: tuple[tuple[str, str], ...] = (
    ("Groq API key", r"\bgsk_[A-Za-z0-9]{20,}"),
    ("Google API key", r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    ("Razorpay LIVE key", r"\brzp_live_[A-Za-z0-9]{10,}"),
    ("Razorpay test key", r"\brzp_test_[A-Za-z0-9]{10,}"),
    ("OpenAI key", r"\bsk-[A-Za-z0-9]{32,}"),
    ("GitHub token", r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    ("AWS access key id", r"\bAKIA[0-9A-Z]{16}\b"),
    ("private key block", r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
)

#: Where `gates/` and `scorer/` may live. Both layouts are checked because `CONTEXT.md`
#: §16's tree is ambiguous about it and the architect has not yet ruled — see
#: QUESTIONS.md Q-004. Checking both means this file needs no edit when the ruling lands.
_PACKAGE_LAYOUTS = (
    ("src/whetstone_gate/gates", "src/whetstone_gate/scorer"),
    ("src/gates", "src/scorer"),
)


@dataclass
class Result:
    """One check's outcome. ``ok is None`` means *not applicable yet*, never *passed*."""

    check: str
    ok: bool | None
    detail: str

    @property
    def symbol(self) -> str:
        return {True: "PASS", False: "FAIL", None: " n/a"}[self.ok]


def _git(*args: str, root: Path) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def _tracked_files(root: Path) -> list[str]:
    return [line for line in _git("ls-files", root=root).splitlines() if line]


def _eol_classification(root: Path) -> dict[str, str]:
    """Ask **git itself** how it classifies each tracked path's working-tree content.

    Returns ``{path: eolinfo}`` where ``eolinfo`` is git's own token — ``lf``, ``crlf``,
    ``mixed``, ``none``, or **``-text``, which means git treats the content as BINARY and
    applies no end-of-line conversion to it at all.**

    `[VERIFIED HERE, 2026-08-30]` on the two dashboard screenshots: ``git ls-files --eol``
    reports ``i/-text w/-text attr/text=auto eol=lf``, and ``git hash-object`` with and
    without ``--no-filters`` returns the same blob id — so ``* text=auto`` already detects
    them as binary and converts nothing. **`.gitattributes` needed no image rule.**

    ⚠️ **Why this asks git rather than deciding for itself.** A3 asserts a property *of
    git's own conversion behaviour*. A check that reimplemented git's text/binary
    heuristic (a NUL byte within the first 8000) would be a second copy of the predicate
    under test, free to drift from the real one — the same shape of mistake as
    `CLAUDE.md` hard rule 8's spike defect, where ``gate.js`` and ``invariants.js`` both
    called ``world.js:intentKey`` and so the invariant could not fire unless the gate had
    a bug. ``git ls-files --eol`` is the authority, so no second copy exists.
    """
    classification: dict[str, str] = {}
    for record in _git("ls-files", "--eol", "-z", root=root).split("\x00"):
        if not record:
            continue
        # Fields are space-padded and a single TAB precedes the path, so partition on the
        # FIRST tab: a tab inside a path then stays with the path instead of eating it.
        fields, _, rel = record.partition("\t")
        for field in fields.split():
            if field.startswith("w/"):
                classification[rel] = field[2:]
                break
    return classification


def _round_trips_unchanged(root: Path, rel: str) -> bool | None:
    """Would git store this file's **working-tree bytes unchanged**? ``None`` = cannot say.

    This is `PROCESS.md` §6a's property asked directly: hash the file **through** the
    filter chain (``git hash-object``) and **around** it (``--no-filters``). Equal ids mean
    the conversion machinery is a no-op on this path, so ``sha256(checked-out bytes)`` and
    ``sha256(git show <ref>:<path>)`` agree — on every OS, which is the whole point.

    ⚠️ **Why not compare against the index or ``HEAD``.** Both would report every
    *uncommitted edit* as a line-ending defect, conflating "you have unsaved work" with
    "your files are being corrupted", and would make this check red through the ordinary
    middle of any session. The round-trip question is the one §6a actually asks, and it is
    answerable on a dirty tree.

    A text file carrying CRLF **does** fail this — under ``* text=auto eol=lf`` the filtered
    id normalises to LF and the raw id does not. That is INC-06's defect, and it is still
    caught. A binary file passes, because git converts nothing on it.

    ``None`` is never read as agreement — the caller reports it, because *"could not
    verify"* is not a pass.
    """
    try:
        filtered = subprocess.run(
            ["git", "hash-object", "--", rel], cwd=root, capture_output=True, text=True
        )
        raw = subprocess.run(
            ["git", "hash-object", "--no-filters", "--", rel],
            cwd=root, capture_output=True, text=True,
        )
    except OSError:
        return None
    if filtered.returncode != 0 or raw.returncode != 0:
        return None
    return filtered.stdout.strip() == raw.stdout.strip()


# --------------------------------------------------------------------------------------
# A. .gitattributes
# --------------------------------------------------------------------------------------


def check_gitattributes(root: Path) -> list[Result]:
    out: list[Result] = []
    path = root / ".gitattributes"
    if not path.is_file():
        return [
            Result(
                "A1 .gitattributes exists",
                False,
                "missing — PROCESS.md §6a makes it a first-commit deliverable, and it is "
                "fixable only in the first commit",
            )
        ]

    content = path.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    exact = lines == [GITATTRIBUTES_REQUIRED]
    out.append(
        Result(
            "A1 .gitattributes content",
            exact,
            f"contains exactly {GITATTRIBUTES_REQUIRED!r}"
            if exact
            else f"expected exactly [{GITATTRIBUTES_REQUIRED!r}], found {lines!r}",
        )
    )

    # In the FIRST commit? `--diff-filter=A` finds the commit that ADDED it; compare that
    # against the root commit.
    added = _git(
        "log", "--diff-filter=A", "--format=%H", "--", ".gitattributes", root=root
    ).split()
    roots = _git("rev-list", "--max-parents=0", "HEAD", root=root).split()
    in_first = bool(added) and bool(roots) and added[-1] == roots[-1]
    out.append(
        Result(
            "A2 .gitattributes in the FIRST commit",
            in_first,
            f"added in {added[-1][:7] if added else '(never)'}; root commit is "
            f"{roots[-1][:7] if roots else '(none)'}"
            + ("" if in_first else " — these must be the same commit (PROCESS.md §6a)"),
        )
    )

    # And the property it exists for: the working tree agrees with the object store, so a
    # fingerprint taken from git objects reproduces on every OS.
    #
    # ⚠️ CRLF-absence is a PROXY for that property, and the proxy is meaningful only for
    # content git treats as TEXT. For BINARY content git applies no conversion whatsoever,
    # so a 0x0D 0x0A pair inside a PNG's deflate stream is DATA, not a line ending, and
    # reading it as one reports the repository broken when it is sound.
    # See INCIDENTS.md INC-09 and QUESTIONS.md Q-012.
    #
    # The property is therefore asserted TWICE, and nothing here is narrower than what this
    # check asserted before:
    #   A3 keeps the CRLF assertion, UNCHANGED, over every file GIT says is text;
    #   A4 asserts the UNDERLYING property directly — worktree bytes == stored bytes —
    #      over EVERY tracked file, text and binary alike. On every file it covers, A4 is
    #      strictly stronger than A3 ever was: it catches any divergence, not only the
    #      CRLF-shaped kind. A binary file is not skipped here; it is checked harder.
    classification = _eol_classification(root)
    crlf_in_text: list[str] = []
    divergent: list[str] = []
    unverifiable: list[str] = []
    text_checked = 0
    binary_checked = 0

    for rel in _tracked_files(root):
        p = root / rel
        if not p.is_file():
            continue
        try:
            worktree = p.read_bytes()
        except OSError:
            unverifiable.append(rel)
            continue

        if classification.get(rel) == "-text":
            binary_checked += 1
        else:
            text_checked += 1
            if b"\r\n" in worktree:
                crlf_in_text.append(rel)

        round_trips = _round_trips_unchanged(root, rel)
        if round_trips is None:
            unverifiable.append(rel)
        elif not round_trips:
            divergent.append(rel)

    out.append(
        Result(
            "A3 no CRLF in any tracked file",
            not crlf_in_text,
            f"{text_checked} tracked file(s) that git classifies as TEXT are LF in the "
            f"working tree; {binary_checked} binary file(s) hold no line endings to "
            f"normalise and are covered by A4 instead — counted here, never silently "
            f"dropped"
            if not crlf_in_text
            else f"CRLF found in {len(crlf_in_text)} TEXT file(s): {crlf_in_text[:5]}",
        )
    )
    out.append(
        Result(
            "A4 working tree and object store hold identical bytes",
            not (divergent or unverifiable),
            f"git's filter chain is a no-op on all {text_checked + binary_checked} tracked "
            f"file(s) ({binary_checked} binary), so `git show <ref>:<path>` and the "
            f"checked-out bytes agree on every OS — the property PROCESS.md §6a's "
            f"fingerprint depends on"
            if not (divergent or unverifiable)
            else (
                (
                    f"git would REWRITE {len(divergent)} file(s) on checkin: "
                    f"{divergent[:5]}. "
                    if divergent
                    else ""
                )
                + (
                    f"COULD NOT VERIFY {len(unverifiable)} file(s): {unverifiable[:5]} — "
                    f"'could not verify' is reported as a failure, never as a pass"
                    if unverifiable
                    else ""
                )
            ),
        )
    )
    return out


# --------------------------------------------------------------------------------------
# B / C. secrets
# --------------------------------------------------------------------------------------


def check_secrets(root: Path) -> list[Result]:
    out: list[Result] = []
    tracked = _tracked_files(root)

    env_tracked = [f for f in tracked if f == ".env" or f.startswith(".env.") and f != ".env.example"]
    out.append(
        Result(
            "B1 no .env tracked",
            not env_tracked,
            "none tracked" if not env_tracked else f"TRACKED: {env_tracked} — revoke and untrack",
        )
    )

    example = root / ".env.example"
    out.append(
        Result(
            "B2 .env.example exists",
            example.is_file(),
            "present" if example.is_file() else "missing — a session must be able to learn "
            "which keys exist by reading NAMES, never by reading a value",
        )
    )
    if example.is_file():
        with_values = []
        for raw in example.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            _, _, value = line.partition("=")
            if value.strip():
                with_values.append(line.split("=", 1)[0])
        out.append(
            Result(
                "B3 .env.example holds NAMES only",
                not with_values,
                "every entry is a bare NAME= with no value"
                if not with_values
                else f"these entries carry a value: {with_values}",
            )
        )
    else:
        out.append(
            Result(
                "B3 .env.example holds NAMES only",
                False,
                "cannot check — the file is missing",
            )
        )

    hits: list[str] = []
    for rel in tracked:
        p = root / rel
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for label, pattern in SECRET_PATTERNS:
            for match in re.finditer(pattern, text):
                line_no = text.count("\n", 0, match.start()) + 1
                hits.append(f"{rel}:{line_no} — {label}")
    out.append(
        Result(
            "C1 no secret-shaped string in any tracked file",
            not hits,
            f"scanned {len(tracked)} tracked files against {len(SECRET_PATTERNS)} patterns"
            if not hits
            else "HITS: " + "; ".join(hits[:10]),
        )
    )
    out.append(
        Result(
            "C2 git-HISTORY secret scan",
            None,
            "owned by C21, run BEFORE the visibility flip, output committed to "
            "docs/submission/. Its remedy is constrained: revoke the key at the provider "
            "and record the incident — the history is NOT rewritten, because a rewrite "
            "would destroy probe-v1, prereg-v1 and every cN-pass tag",
        )
    )
    return out


# --------------------------------------------------------------------------------------
# D. gates / scorer isolation — the moat
# --------------------------------------------------------------------------------------


def _first_party_imports(py: Path, package_roots: set[str]) -> set[str]:
    """Return first-party modules imported by ``py``, by source inspection.

    Deliberately textual rather than import-driven: importing ``gates`` to find out what
    ``gates`` imports would execute it, and this check must work on a tree that does not
    yet run.
    """
    found: set[str] = set()
    try:
        text = py.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return found
    for match in re.finditer(
        r"^\s*(?:from\s+([.\w]+)\s+import|import\s+([.\w]+))", text, re.MULTILINE
    ):
        module = match.group(1) or match.group(2)
        head = module.lstrip(".").split(".")[0]
        if head in package_roots:
            found.add(module)
    return found


def check_gate_scorer_isolation(root: Path) -> list[Result]:
    for gates_rel, scorer_rel in _PACKAGE_LAYOUTS:
        gates, scorer = root / gates_rel, root / scorer_rel
        if gates.is_dir() and scorer.is_dir():
            return _walk_isolation(root, gates, scorer, gates_rel, scorer_rel)

    return [
        Result(
            "D1 gates/ and scorer/ share no first-party module",
            None,
            "neither directory exists yet — gates/ is built by C9, scorer/ by C8. Both "
            "candidate layouts were checked (src/whetstone_gate/… and src/…) because "
            "CONTEXT.md §16's tree is ambiguous; see QUESTIONS.md Q-004",
        )
    ]


def _walk_isolation(
    root: Path, gates: Path, scorer: Path, gates_rel: str, scorer_rel: str
) -> list[Result]:
    package_roots = {"whetstone_gate", "gates", "scorer"} | {
        p.name for p in (root / "src").iterdir() if p.is_dir()
    }
    gate_imports = set().union(
        *(_first_party_imports(f, package_roots) for f in gates.rglob("*.py")), set()
    )
    scorer_imports = set().union(
        *(_first_party_imports(f, package_roots) for f in scorer.rglob("*.py")), set()
    )

    results = []
    crossing_into_scorer = {m for m in gate_imports if "scorer" in m.split(".")}
    crossing_into_gates = {m for m in scorer_imports if "gates" in m.split(".")}
    results.append(
        Result(
            "D1 gates/ imports nothing from scorer/",
            not crossing_into_scorer,
            "clean" if not crossing_into_scorer else f"CROSSES: {sorted(crossing_into_scorer)}",
        )
    )
    results.append(
        Result(
            "D2 scorer/ imports nothing from gates/",
            not crossing_into_gates,
            "clean" if not crossing_into_gates else f"CROSSES: {sorted(crossing_into_gates)}",
        )
    )

    shared = (gate_imports & scorer_imports) - {"whetstone_gate"}
    results.append(
        Result(
            "D3 no shared first-party module",
            not shared,
            f"{gates_rel} and {scorer_rel} share no first-party import"
            if not shared
            else (
                f"SHARED: {sorted(shared)}. Any logic they both need is written TWICE, on "
                f"purpose. Adding to the allow-list of pure value types is a Class A "
                f"deviation requiring an architect ruling in QUESTIONS.md"
            ),
        )
    )
    return results


# --------------------------------------------------------------------------------------
# E. session tokens
# --------------------------------------------------------------------------------------

_TOKEN_TRAILER = re.compile(r"^Session-Token:\s*([0-9a-fA-F]{8})\s*$", re.MULTILINE)
_TOKEN_ROW = re.compile(
    r"^\|\s*`?([0-9a-fA-F]{8})`?\s*\|\s*(C\d+)\s*\|\s*(BUILD|REVIEW|FIX)\s*\|", re.MULTILINE
)


def check_session_tokens(root: Path) -> list[Result]:
    questions = root / "QUESTIONS.md"
    issued: dict[str, tuple[str, str]] = {}
    if questions.is_file():
        for token, chunk, role in _TOKEN_ROW.findall(questions.read_text(encoding="utf-8")):
            issued[token.lower()] = (chunk, role.upper())

    log = _git("log", "--format=%H%x1f%B%x1e", root=root)
    used: dict[str, list[str]] = {}
    untrailered: list[str] = []
    for record in filter(None, (r.strip() for r in log.split("\x1e"))):
        sha, _, body = record.partition("\x1f")
        tokens = [t.lower() for t in _TOKEN_TRAILER.findall(body)]
        if not tokens:
            untrailered.append(sha[:7])
        for token in tokens:
            used.setdefault(token, []).append(sha[:7])

    out: list[Result] = []

    unissued = {t: shas for t, shas in used.items() if t not in issued}
    out.append(
        Result(
            "E1 no commit carries an UNISSUED token",
            not unissued,
            "clean"
            if not unissued
            else f"FORGED/UNISSUED: {unissued} — not present in QUESTIONS.md ## Session tokens",
        )
    )

    by_chunk_role: dict[tuple[str, str], set[str]] = {}
    for token, (chunk, role) in issued.items():
        by_chunk_role.setdefault((chunk, role), set()).add(token)
    reused_across_roles = [
        token
        for token in issued
        if sum(1 for (c, r), toks in by_chunk_role.items() if token in toks) > 1
    ]
    shared_build_review = [
        chunk
        for chunk in {c for c, _ in by_chunk_role}
        if by_chunk_role.get((chunk, "BUILD"), set()) & by_chunk_role.get((chunk, "REVIEW"), set())
    ]
    out.append(
        Result(
            "E2 no token shared by a chunk's BUILD and REVIEW",
            not shared_build_review,
            "clean"
            if not shared_build_review
            else f"SHARED on {shared_build_review} — build and review are never the same session",
        )
    )
    out.append(
        Result(
            "E3 no token reused across roles",
            not reused_across_roles,
            "clean" if not reused_across_roles else f"REUSED: {reused_across_roles}",
        )
    )

    if untrailered:
        out.append(
            Result(
                "E4 every commit carries a Session-Token trailer",
                None,
                f"{len(untrailered)} commit(s) carry no trailer: {untrailered[:6]}. "
                "The C0 build prompt issued no SESSION-TOKEN and this session did not "
                "fabricate one — a fabricated token would be exactly the 'token that was "
                "never issued' that E1 exists to catch. See QUESTIONS.md Q-001",
            )
        )
    else:
        out.append(Result("E4 every commit carries a Session-Token trailer", True, "clean"))
    return out


# --------------------------------------------------------------------------------------
# F. outstanding config sentinels
# --------------------------------------------------------------------------------------


def check_config_sentinels(root: Path) -> list[Result]:
    try:
        outstanding = cfg.outstanding_sentinels()
    except cfg.ConfigError as exc:
        return [Result("F1 config/ loads", False, str(exc))]

    operator_owed = [s for s in outstanding if s[2] == "TODO_OPERATOR"]
    detail = (
        "no undetermined values remain"
        if not outstanding
        else "; ".join(f"{name}:{path} = {sentinel}" for name, path, sentinel in outstanding)
    )
    return [
        Result("F1 config/ loads", True, "protocol.yaml and lanes.yaml parse"),
        Result(
            "F2 undetermined values are DECLARED, not defaulted",
            True,
            f"{len(outstanding)} explicit TODO_ sentinel(s); the loader RAISES on each "
            f"rather than substituting a value (hard rule 9). {detail}",
        ),
        Result(
            "F3 OPERATOR-owed values",
            None if operator_owed else True,
            f"{len(operator_owed)} awaiting the operator: "
            + "; ".join(f"{n}:{p}" for n, p, _ in operator_owed)
            + " — see QUESTIONS.md Q-006"
            if operator_owed
            else "none outstanding",
        ),
    ]


# --------------------------------------------------------------------------------------


def run(root: Path | None = None) -> int:
    """Run every check. Returns a process exit code."""
    root = root or cfg.repo_root()
    groups = [
        ("A/B/C — the freeze prerequisite and secrets", check_gitattributes(root) + check_secrets(root)),
        ("D — the gate/scorer moat", check_gate_scorer_isolation(root)),
        ("E — session identity (PROCESS.md §7a)", check_session_tokens(root)),
        ("F — config/ completeness (hard rule 9)", check_config_sentinels(root)),
    ]

    failures = 0
    not_applicable = 0
    say("check-roles — the repository's structural invariants\n")
    for title, results in groups:
        say(f"  {title}")
        for r in results:
            say(f"    [{r.symbol}] {r.check}")
            say(f"           {r.detail}")
            if r.ok is False:
                failures += 1
            elif r.ok is None:
                not_applicable += 1
        say()

    total = sum(len(rs) for _, rs in groups)
    say(f"  {total - failures - not_applicable} passed, {failures} failed, {not_applicable} n/a")
    if failures:
        say("\n  FAIL — a structural invariant is broken. This is not a style issue.")
        return 1
    say("\n  OK — no structural invariant is broken. `n/a` is never a pass; see the reasons above.")
    return 0
