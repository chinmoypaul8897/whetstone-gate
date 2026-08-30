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
  D. ``gates/`` and ``scorer/`` share no first-party module, on **any** path. **This one
     line is the whole moat** — in the spike, the gate and the invariant checker both called
     ``world.js:intentKey``, so the invariant could not have fired unless the gate had a
     bug. That is not a result; it is a definition. The walk is over both packages'
     **transitive** first-party imports, with relative imports resolved against the
     importing file's own package and ``from whetstone_gate import X`` resolved to
     ``whetstone_gate.X``, against an allow-list (:data:`MOAT_ALLOW_LIST`) that is **empty**
     and that may not be added to without an architect ruling.
  E. Session-token discipline (`PROCESS.md` §7a): no commit carries a token that was never
     issued, and no token is reused across roles or shared by a chunk's build and review.
     **E5 additionally FAILS on a trailer that is PRESENT but MALFORMED** — Q-014 (i):
     *"judging fails open and rules fail closed"* (`CONTEXT.md` §14). Silence there used to
     be indistinguishable from absence, and E4 printed a false statement about four commits
     that do carry a trailer.
  F. Outstanding ``TODO_`` sentinels in ``config/`` are reported, so "somebody still owes
     this project a value" is a printed number rather than something to remember.

It exits non-zero on a violation. Checks that cannot yet apply report ``n/a`` with the
reason, and ``n/a`` is never silently a pass.
"""

from __future__ import annotations

import ast
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

#: Where `gates/` and `scorer/` may live. **Q-004 ruled OPTION 1 on 2026-08-31** — the
#: subpackages are CHILDREN of `whetstone_gate/`, on a fact verified at source: tau2-bench
#: installs a top-level package called `tau2`, so a sibling layout would publish a second
#: one in collision with the benchmark §21.4 calls undroppable. **The ruled layout is
#: therefore first.** The sibling layout is still checked because doing so costs nothing and
#: this file then needs no edit if a stray tree ever appears there.
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
    # The property is therefore asserted TWICE:
    #   A3 keeps the CRLF assertion, UNCHANGED, over every file GIT says is text;
    #   A4 asserts the UNDERLYING property directly — would git's filter chain rewrite
    #      these bytes? — over EVERY tracked file.
    #
    # ⚠️ CORRECTION, 2026-08-30, from an adversarial re-check of this very comment. An
    # earlier version of it claimed *"on every file it covers A4 is strictly stronger than
    # A3 ever was … a binary file is not skipped here; it is checked harder."* **THAT WAS
    # FALSE, and it was the load-bearing sentence of the hard-rule-6 defence.** On `-text`
    # content git applies no conversion, so `git hash-object` and `--no-filters` are equal
    # BY CONSTRUCTION: **A4 cannot fail on a binary file.** Four adversarial binary shapes
    # were tried and none could make it fire. The honest statement is:
    #
    #     A4 is strictly STRONGER than old A3 on TEXT files.
    #     On BINARY files A4 is VACUOUS — and binary files are exactly the set whose
    #     treatment changed.
    #
    # **What still makes this not a rule-6 weakening is a different argument, and it is the
    # one that actually holds:** every failure removed was a FALSE POSITIVE. git applies no
    # conversion to `-text` content, so the §6a property — a fresh clone reproduces the
    # committed bytes — holds there unconditionally. Verified end-to-end: a text-shaped file
    # with CRLF endings and one NUL byte, on which old A3 failed, hashes identically in the
    # working tree, in `git show HEAD:`, and in a **fresh `git clone`**. No true positive was
    # lost. See QUESTIONS.md Q-012 and INCIDENTS.md INC-09.
    #
    # ⚠️ KNOWN GAP, NOT CLOSED HERE (OPEN_FINDINGS OF-01): a single stray CR makes git
    # classify an otherwise-textual file `-text`, so neither A3 nor A4 fires on it. That is
    # NOT a regression — old A3 searched for CRLF pairs and missed a lone CR too — but it is
    # precisely INC-06's and INC-10's defect class. Closing it needs a new check and belongs
    # to C0's review, not to this session's fence.
    classification = _eol_classification(root)
    crlf_in_text: list[str] = []
    divergent: list[str] = []
    unverifiable: list[str] = []
    not_regular: list[str] = []
    text_checked = 0
    binary_checked = 0
    tracked = _tracked_files(root)

    for rel in tracked:
        p = root / rel
        if not p.is_file():
            # ⚠️ Hard rule 11 applies to a CHECK's denominator too. A tracked path with no
            # regular file behind it — deleted-but-not-staged, a submodule gitlink — is
            # skipped, and it is therefore COUNTED AND NAMED. The earlier wording said
            # "never silently dropped" and "all N tracked file(s)" over a denominator that
            # quietly excluded these, which is the exact shape rule 11 forbids.
            not_regular.append(rel)
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

    # The denominator, reconciled out loud. len(tracked) is the only honest total.
    skipped = (
        f"; {len(not_regular)} tracked path(s) have no regular file behind them and were "
        f"checked by NEITHER: {not_regular[:5]}"
        if not_regular
        else ""
    )
    reconciliation = (
        f"{text_checked} text + {binary_checked} binary + {len(not_regular)} non-regular "
        f"= {len(tracked)} tracked"
    )

    out.append(
        Result(
            "A3 no CRLF in any tracked file",
            not crlf_in_text,
            f"{text_checked} file(s) git classifies as TEXT carry no CRLF in the working "
            f"tree. {binary_checked} file(s) git classifies as BINARY (`-text`) are NOT "
            f"scanned for CRLF, because git applies no end-of-line conversion to them and "
            f"a CR-LF pair there is data, not a line ending{skipped}. {reconciliation}"
            if not crlf_in_text
            else (
                f"CRLF found in {len(crlf_in_text)} TEXT file(s): "
                f"{sorted(crlf_in_text)[:5]}"
                + (f" (+{len(crlf_in_text) - 5} more)" if len(crlf_in_text) > 5 else "")
            ),
        )
    )
    out.append(
        Result(
            "A4 working tree and object store hold identical bytes",
            not (divergent or unverifiable or not_regular),
            f"git's filter chain is a no-op on all {text_checked + binary_checked} tracked "
            f"file(s) checked, so `git show <ref>:<path>` and the checked-out bytes agree "
            f"on every OS — the property PROCESS.md §6a's fingerprint depends on. "
            f"⚠️ On the {binary_checked} binary file(s) this holds BY CONSTRUCTION and so "
            f"asserts nothing: git converts nothing there, and A4 cannot fail on `-text` "
            f"content. It is a real assertion on the {text_checked} text file(s) only. "
            f"{reconciliation}"
            if not (divergent or unverifiable or not_regular)
            else (
                (
                    f"git would REWRITE {len(divergent)} file(s) on checkin: "
                    f"{sorted(divergent)[:5]}. "
                    if divergent
                    else ""
                )
                + (
                    f"COULD NOT VERIFY {len(unverifiable)} file(s): "
                    f"{sorted(unverifiable)[:5]} — 'could not verify' is reported as a "
                    f"failure, never as a pass. "
                    if unverifiable
                    else ""
                )
                + (
                    f"{len(not_regular)} tracked path(s) have no regular file behind them "
                    f"and were checked by nothing: {not_regular[:5]}. "
                    if not_regular
                    else ""
                )
                + reconciliation
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


#: ⚠️ **THE ALLOW-LIST HARD RULE 8 DESCRIBES. IT IS CREATED EMPTY, AND IT IS EMPTY TODAY.**
#:
#: Hard rule 8, verbatim: the module-graph walk fails *"on any shared first-party module
#: **outside a short, explicit allow-list of pure value types (enums, the harm-record
#: dataclass, the paise integer wrapper) that carry no predicate logic**. **Adding to that
#: allow-list is a Class A deviation** requiring an architect ruling in `QUESTIONS.md`."*
#:
#: **NONE OF THE THREE NAMED VALUE TYPES EXISTS YET** — the harm-record dataclass is C4's,
#: the enums and the paise wrapper are C4's and C8's — so this ships empty and a test pins
#: it empty. **ADDING AN ENTRY IS A CLASS A DEVIATION AND REQUIRES AN ARCHITECT RULING IN
#: `QUESTIONS.md`, RECORDED VERBATIM (hard rule 5), NAMING THAT ONE MODULE.** C4, C8 and C9
#: will each ask; **each ask is a separate ruling, judged on whether that specific module
#: carries predicate logic, and none is ever granted in bulk** (Q-015's ruling).
#:
#: ⚠️ **THERE IS NO ENTRY FOR THE PACKAGE ROOT AND NONE MAY BE CREATED.** The first version
#: of this code ended with ``shared = (gate_imports & scorer_imports) - {"whetstone_gate"}``,
#: an unruled one-entry allow-list holding a *package*, not a pure value type — and under
#: Q-004's ruling the package root is now the **commonest import string in the project**, so
#: allow-listing it would make D3 permanently blind. Q-015 rejected that explicitly. The
#: root stops being a value either side can record because ``from whetstone_gate import X``
#: is RESOLVED to ``whetstone_gate.X`` below, which is the module the two sides actually
#: share.
MOAT_ALLOW_LIST: frozenset[str] = frozenset()


def _module_name(py: Path, src_root: Path) -> str:
    """The dotted first-party module name of ``py``, relative to ``src/``.

    ``src/whetstone_gate/gates/arm4_kernel.py`` → ``whetstone_gate.gates.arm4_kernel``;
    ``src/whetstone_gate/gates/__init__.py`` → ``whetstone_gate.gates``.
    """
    parts = list(py.relative_to(src_root).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _first_party_modules(src_root: Path) -> dict[str, Path]:
    """Every first-party module under ``src/``, as ``{dotted name: file}``."""
    index: dict[str, Path] = {}
    for py in sorted(src_root.rglob("*.py")):
        if ".venv" in py.parts or "vendor" in py.parts:
            continue
        name = _module_name(py, src_root)
        if name:
            index[name] = py
    return index


def _resolve_imports(
    py: Path, module: str, known: dict[str, Path], package_roots: set[str]
) -> set[str]:
    """First-party modules ``py`` imports, **resolved**, by parsing — never by importing.

    ⚠️ **Parsing, not importing.** Importing ``gates`` to learn what ``gates`` imports would
    execute it, and this check must work on a tree that does not yet run. ``ast.parse``
    executes nothing; it only reads. That was the original textual scan's whole argument and
    it is preserved — what changes is that a parser sees the import forms a single regex
    with one capture group did not (``import a, b``; a parenthesised multi-line
    ``from x import (a, b)``; every alias form).

    **Three resolutions, and each closes one of `REVIEW_C0.md` B-02's causes:**

    1. ``from whetstone_gate import X`` resolves to ``whetstone_gate.X`` **when that is a
       real first-party module**, and to ``whetstone_gate`` otherwise. The old code recorded
       the bare string ``whetstone_gate`` for both sides and then subtracted it away, so
       ``gates/`` and ``scorer/`` both importing one ``shared_predicate`` — **hard rule 8's
       own named spike defect, in Python** — reported ``PASS``. (Q-015's ruling, option 1.)
    2. A **relative** import is resolved against the importing file's own package.
       ``head = module.lstrip(".").split(".")[0]`` yielded ``""`` for ``from .. import
       scorer``, and ``""`` is in no package root, so **an import crossing the moat was not
       recorded at all**.
    3. Every recorded edge is followed **transitively** by the caller, because hard rule 8
       says *transitive* and the old walk was one hop deep — so the one-hop attack (each
       side imports its own helper; both helpers import the shared predicate) passed.

    Raises :class:`SyntaxError` if the file does not parse. The caller reports that as a
    **failure**, never as a pass: *"could not verify"* is not agreement.
    """
    tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"), filename=str(py))
    package = module if py.name == "__init__.py" else module.rpartition(".")[0]

    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in package_roots:
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package
                for _ in range(node.level - 1):
                    base = base.rpartition(".")[0]
                target = f"{base}.{node.module}" if node.module else base
            else:
                target = node.module or ""
            if not target or target.split(".")[0] not in package_roots:
                continue
            for alias in node.names:
                candidate = f"{target}.{alias.name}"
                found.add(candidate if candidate in known else target)
    return found


def _transitive_closure(seeds: set[str], graph: dict[str, set[str]]) -> set[str]:
    """Every first-party module reachable from ``seeds``. Hard rule 8 says *transitive*."""
    seen: set[str] = set()
    stack = list(seeds)
    while stack:
        module = stack.pop()
        if module in seen:
            continue
        seen.add(module)
        stack.extend(graph.get(module, ()))
    return seen


def check_gate_scorer_isolation(root: Path) -> list[Result]:
    for gates_rel, scorer_rel in _PACKAGE_LAYOUTS:
        gates, scorer = root / gates_rel, root / scorer_rel
        if gates.is_dir() and scorer.is_dir():
            return _walk_isolation(root, gates, scorer, gates_rel, scorer_rel)

    return [
        Result(
            "D1 gates/ and scorer/ share no first-party module",
            None,
            "neither directory exists yet — gates/ is built by C9, scorer/ by C8. Q-004 "
            "ruled OPTION 1 on 2026-08-31: both live UNDER the package, at "
            "src/whetstone_gate/gates/ and src/whetstone_gate/scorer/. Both candidate "
            "layouts are still checked — it costs nothing and the ruled one is now first",
        )
    ]


def _walk_isolation(
    root: Path, gates: Path, scorer: Path, gates_rel: str, scorer_rel: str
) -> list[Result]:
    src_root = root / "src"
    package_roots = {"whetstone_gate", "gates", "scorer"} | {
        p.name for p in src_root.iterdir() if p.is_dir()
    }
    known = _first_party_modules(src_root)

    graph: dict[str, set[str]] = {}
    unparseable: list[str] = []
    for module, py in known.items():
        try:
            graph[module] = _resolve_imports(py, module, known, package_roots)
        except (SyntaxError, OSError, ValueError) as exc:
            unparseable.append(f"{py.relative_to(root).as_posix()} ({type(exc).__name__})")
            graph[module] = set()

    gates_pkg = _module_name(gates / "__init__.py", src_root)
    scorer_pkg = _module_name(scorer / "__init__.py", src_root)

    def _under(prefix: str) -> set[str]:
        return {m for m in known if m == prefix or m.startswith(prefix + ".")}

    def _crosses(closure: set[str], prefix: str) -> set[str]:
        return {m for m in closure if m == prefix or m.startswith(prefix + ".")}

    gate_seeds, scorer_seeds = _under(gates_pkg), _under(scorer_pkg)
    gate_closure = _transitive_closure(gate_seeds, graph)
    scorer_closure = _transitive_closure(scorer_seeds, graph)

    # "Could not verify" is reported as a failure, never as a pass — the same doctrine A4
    # applies to a tracked path it could not hash. A file the parser choked on is a file
    # whose imports nobody has seen, and the moat is the one claim that may not rest on one.
    blocked = (
        f" ⚠️ COULD NOT PARSE {len(unparseable)} first-party file(s), so this verdict is "
        f"NOT supported by evidence: {sorted(unparseable)[:5]}"
        if unparseable
        else ""
    )
    reconciliation = (
        f"{len(known)} first-party module(s) indexed; {len(gate_closure)} reachable from "
        f"{gates_rel} ({len(gate_seeds)} seed(s)), {len(scorer_closure)} from {scorer_rel} "
        f"({len(scorer_seeds)} seed(s)), TRANSITIVELY"
    )

    results = []
    crossing_into_scorer = _crosses(gate_closure, scorer_pkg)
    crossing_into_gates = _crosses(scorer_closure, gates_pkg)
    results.append(
        Result(
            "D1 gates/ imports nothing from scorer/",
            not (crossing_into_scorer or unparseable),
            f"clean. {reconciliation}"
            if not (crossing_into_scorer or unparseable)
            else f"CROSSES: {sorted(crossing_into_scorer)}.{blocked} {reconciliation}",
        )
    )
    results.append(
        Result(
            "D2 scorer/ imports nothing from gates/",
            not (crossing_into_gates or unparseable),
            f"clean. {reconciliation}"
            if not (crossing_into_gates or unparseable)
            else f"CROSSES: {sorted(crossing_into_gates)}.{blocked} {reconciliation}",
        )
    )

    shared = (gate_closure & scorer_closure) - MOAT_ALLOW_LIST
    results.append(
        Result(
            "D3 no shared first-party module",
            not (shared or unparseable),
            f"{gates_rel} and {scorer_rel} share no first-party module on any path. "
            f"The allow-list holds {len(MOAT_ALLOW_LIST)} entr(y/ies). {reconciliation}"
            if not (shared or unparseable)
            else (
                f"SHARED: {sorted(shared)}. **Any logic they both need is written TWICE, on "
                f"purpose** — once against the live call, once against the replayed ledger. "
                f"In the spike, gate.js and invariants.js both called world.js:intentKey, so "
                f"the invariant COULD NOT HAVE FIRED unless the gate had a bug: that is not a "
                f"result, it is a definition. Adding to MOAT_ALLOW_LIST is a CLASS A "
                f"deviation requiring an architect ruling in QUESTIONS.md, naming that one "
                f"module and judging whether it carries predicate logic.{blocked} "
                f"{reconciliation}"
            ),
        )
    )
    return results


# --------------------------------------------------------------------------------------
# E. session tokens
# --------------------------------------------------------------------------------------

#: The STRICT matcher. `PROCESS.md` §7a specifies 8 random hex, and the architect's Q-014
#: ruling declined to widen it — *"`_TOKEN_TRAILER` IS NOT WIDENED. That stands and is not
#: reopened."* ``tests/test_c0_review_probes.py`` pins it.
_TOKEN_TRAILER = re.compile(r"^Session-Token:\s*([0-9a-fA-F]{8})\s*$", re.MULTILINE)

#: The PERMISSIVE matcher, applied **only where the strict one did not match** — Q-014 (i)'s
#: named mechanism. It exists to distinguish *"this commit carries no trailer"* from
#: *"this commit carries a trailer nobody can read"*, which E4 used to conflate while
#: printing a false statement about four commits that do carry one.
_TOKEN_TRAILER_ANY = re.compile(r"^Session-Token:\s*(\S.*?)\s*$", re.MULTILINE)

#: ⚠️ Q-014 (iii): the CHUNK group is widened to ``(C\d+|ARCH)`` **and no further**. ``ARCH``
#: denotes an architect-artefact session that is not a numbered chunk — a spec correction,
#: an artefact landing — which previously could not have a parseable row at all, so E1
#: FAILED on that session's own commits. **THE TOKEN GROUP IS NOT TOUCHED:** Q-014's
#: protection is of the token format, so a forged token cannot hide behind a loose pattern.
_TOKEN_ROW = re.compile(
    r"^\|\s*`?([0-9a-fA-F]{8})`?\s*\|\s*(C\d+|ARCH)\s*\|\s*(BUILD|REVIEW|FIX)\s*\|",
    re.MULTILINE,
)

#: ⚠️ **THE E5 EXCEPTION LIST — EXPLICIT, DATED, NAMED, AND PINNED AT EXACTLY FOUR ENTRIES.**
#:
#: Q-014 (iv) forbids reshaping `WG-2026-08-30-CTX-13.4-A`: *"Rewriting it into a conforming
#: 8-hex value would manufacture the evidence the check exists to test, which is the same act
#: Q-001 correctly refused."* So E5 would be **permanently red** on these four commits, and a
#: permanently red check is one people learn to ignore — Q-009's own argument, turned on this
#: check.
#:
#: The remedy is the same shape as ``TRIPWIRE_SELF_EXCLUSION``, which is pinned at one entry
#: for the same reason: an exception list is the natural place for a check to die quietly.
#: ``tests/test_c0_fix_probes.py`` asserts this dict has **exactly four** keys and that they
#: are **exactly these four commits**, so widening it requires editing an assertion a review
#: will see. **E5 FAILS on any NEW malformed trailer, on any commit, from now on.**
E5_EXCEPTIONS: dict[str, str] = {
    "966324740c4d9de40e407a356bcf24d3d76af65d": (
        "the four CTX-13.4 commits, 2026-08-30: the token ISSUED to that session was "
        "`WG-2026-08-30-CTX-13.4-A`, which is not 8 hex. Q-014 (iv) records it as a "
        "ONE-OFF exception and forbids reshaping it"
    ),
    "6d08cf3ff75189db5e9f49fdc6f59a20466b26d4": "same session, same issued token (Q-014 (iv))",
    "d67550e46282af4f513810c1cc812ed91dfeac90": "same session, same issued token (Q-014 (iv))",
    "ec3064dc74c999dec0bc5277e1ca96705b907547": "same session, same issued token (Q-014 (iv))",
}


def _issued_tokens(questions: Path) -> dict[str, set[tuple[str, str]]]:
    """Parse `QUESTIONS.md`'s ``## Session tokens`` table into ``{token: {(chunk, role)}}``.

    ⚠️ **ONE TOKEN MAY HOLD MANY ``(chunk, role)`` PAIRS, AND THAT IS THE WHOLE POINT.**
    The first version of this built ``issued[token] = (chunk, role)`` — keyed by TOKEN — so
    a token appearing in two rows kept only the **last** one. Every token then landed in
    exactly one bucket, which made **E3's count always 1** and **E2's BUILD∩REVIEW always
    empty**: two of `PROCESS.md` §7a's three named conditions were *structurally unable to
    fire*, and both printed ``clean`` over input that contains the violation verbatim.
    See `REVIEW_C0.md` **B-01**, `ARCHITECT_CHECK_0.md` §3 and `INCIDENTS.md` **INC-14**.

    A row repeated byte-for-byte is not reuse, so the value is a **set**: the same
    ``(chunk, role)`` twice collapses, two different ones do not.
    """
    issued: dict[str, set[tuple[str, str]]] = {}
    if not questions.is_file():
        return issued
    for token, chunk, role in _TOKEN_ROW.findall(questions.read_text(encoding="utf-8")):
        issued.setdefault(token.lower(), set()).add((chunk, role.upper()))
    return issued


def check_session_tokens(root: Path) -> list[Result]:
    questions = root / "QUESTIONS.md"
    issued = _issued_tokens(questions)
    rows = sum(len(pairs) for pairs in issued.values())

    log = _git("log", "--format=%H%x1f%B%x1e", root=root)
    used: dict[str, list[str]] = {}
    untrailered: list[str] = []
    malformed: list[tuple[str, str]] = []
    for record in filter(None, (r.strip() for r in log.split("\x1e"))):
        sha, _, body = record.partition("\x1f")
        strict = _TOKEN_TRAILER.findall(body)
        # ⚠️ Q-014 (i): the PERMISSIVE pattern is applied ONLY where the strict one did not
        # match, and a trailer it catches that the strict one did not is MALFORMED — not
        # absent. `_TOKEN_TRAILER` is the authority for "well formed"; there is deliberately
        # no second copy of the 8-hex predicate here to drift away from it.
        for value in _TOKEN_TRAILER_ANY.findall(body):
            if value not in strict:
                malformed.append((sha, value))
        tokens = [t.lower() for t in strict]
        if not tokens and not any(s == sha for s, _ in malformed):
            untrailered.append(sha)
        for token in tokens:
            used.setdefault(token, []).append(sha[:7])

    out: list[Result] = []

    unissued = {t: shas for t, shas in used.items() if t not in issued}
    out.append(
        Result(
            "E1 no commit carries an UNISSUED token",
            not unissued,
            f"clean — {rows} issued row(s) covering {len(issued)} token(s) parsed from "
            f"QUESTIONS.md; {len(used)} token(s) appear in the log"
            if not unissued
            else f"FORGED/UNISSUED: {unissued} — not present in QUESTIONS.md ## Session tokens",
        )
    )

    by_chunk_role: dict[tuple[str, str], set[str]] = {}
    for token, pairs in issued.items():
        for pair in pairs:
            by_chunk_role.setdefault(pair, set()).add(token)

    shared_build_review = sorted(
        chunk
        for chunk in {c for c, _ in by_chunk_role}
        if by_chunk_role.get((chunk, "BUILD"), set()) & by_chunk_role.get((chunk, "REVIEW"), set())
    )
    # §7a's preamble is "never reused", so ANY second (chunk, role) pairing is reuse. A
    # token under two ROLES is the case §7a names; a token under two CHUNKS in the same
    # role is reuse too, and reporting it here is stricter than the clause, never looser.
    reused = sorted(
        (token, sorted(pairs)) for token, pairs in issued.items() if len(pairs) > 1
    )
    out.append(
        Result(
            "E2 no token shared by a chunk's BUILD and REVIEW",
            not shared_build_review,
            f"clean — {rows} issued row(s) checked"
            if not shared_build_review
            else f"SHARED on {shared_build_review} — build and review are never the same session",
        )
    )
    out.append(
        Result(
            "E3 no token reused across roles",
            not reused,
            f"clean — no token holds more than one (chunk, role) pair across {rows} row(s)"
            if not reused
            else "REUSED: "
            + "; ".join(f"{token} appears as {pairs}" for token, pairs in reused),
        )
    )

    if untrailered:
        out.append(
            Result(
                "E4 every commit carries a Session-Token trailer",
                None,
                f"{len(untrailered)} commit(s) carry no trailer: "
                f"{[s[:7] for s in untrailered[:6]]}. "
                "The C0 build prompt issued no SESSION-TOKEN and this session did not "
                "fabricate one — a fabricated token would be exactly the 'token that was "
                "never issued' that E1 exists to catch. See QUESTIONS.md Q-001. "
                "⚠️ This list holds ONLY commits with no trailer at all: a trailer that is "
                "present but malformed is E5's, not this list's (Q-014 (i))",
            )
        )
    else:
        out.append(Result("E4 every commit carries a Session-Token trailer", True, "clean"))

    out.append(_malformed_trailer_result(malformed))
    return out


def _malformed_trailer_result(malformed: list[tuple[str, str]]) -> Result:
    """E5 — `QUESTIONS.md` **Q-014 (i)**: a PRESENT but MALFORMED trailer must FAIL.

    *"Judging fails open and rules fail closed"* (`CONTEXT.md` §14, Prabu Ram, quoted with
    its source). This is a rule and it used to fail open — worse, it printed a **false
    statement**, naming four commits that *do* carry a trailer among *"commit(s) carry no
    trailer"* and attributing them to Q-001, which is a different session's different
    cause. The architect's 8-hex mandate is exactly what makes failing closed safe: after
    it, a non-conforming trailer is a strictly abnormal condition.
    """
    unexcepted = [(sha, value) for sha, value in malformed if sha not in E5_EXCEPTIONS]
    excepted = sorted({sha for sha, _ in malformed if sha in E5_EXCEPTIONS})
    if unexcepted:
        return Result(
            "E5 malformed Session-Token trailer",
            False,
            "MALFORMED and NOT on the dated exception list: "
            + "; ".join(f"{sha[:7]} carries {value!r}" for sha, value in unexcepted[:6])
            + f". PROCESS.md §7a specifies 8 random hex and Q-014 declined to widen "
            f"_TOKEN_TRAILER. Either a prompt issued a malformed token or somebody typed "
            f"one by hand; both stop the build. The exception list holds exactly "
            f"{len(E5_EXCEPTIONS)} SHAs and is not extended without an architect ruling",
        )
    return Result(
        "E5 malformed Session-Token trailer",
        True,
        f"no NEW malformed trailer. {len(excepted)} commit(s) carry the ONE-OFF exception "
        f"recorded in Q-014 (iv): {[s[:7] for s in excepted]} — "
        + (next(iter(E5_EXCEPTIONS.values())) if E5_EXCEPTIONS else "")
        + f". The list is pinned at {len(E5_EXCEPTIONS)} entries by "
        f"tests/test_c0_fix_probes.py so it cannot grow into an amnesty",
    )


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
