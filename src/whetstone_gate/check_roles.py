"""``make check-roles`` — the repository's structural invariants.

These are the properties later chunks *depend on* and that no unit test would otherwise
own, because they are facts about the repository rather than about any module:

  A. ``.gitattributes`` exists, says exactly ``* text=auto eol=lf``, and is **in the first
     commit**. Without it the pre-registration fingerprint fails for every reviewer who
     clones on anything but Windows — silently, at the moment of judging, looking like
     fraud rather than a line-ending bug. The property it buys is asserted two ways: no
     CRLF in any file **git classifies as text**, and — over **every** tracked file, text
     or binary — the working tree and the object store holding the *same bytes*.
     **A5 adds the byte-sanity pair neither of those can see**: no C0 control byte in a
     text-classified file (INC-13's 0x08 BACKSPACE, which sat inside `CONTEXT.md` §16 for
     two days), and no binary-classified file without a NUL (OF-01's lone CR, which makes
     git call textual content binary and so lands it where A3 does not scan and A4 cannot
     fail).
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

     ⚠️ **THE GUARD IS AST *PLUS* SOURCE TEXT, SINCE 2026-09-02, AND THE AST HALF ALONE WAS
     MEASURED TO BE EVADABLE.** `OF-110`, raised by **C6 REVIEW 3** (`3605d31c`), measured
     that ``__import__(…)``, ``importlib.import_module(…)`` and ``getattr(pkg, "name")``
     escape an AST import walk **by construction** — a call expression is not an
     ``ast.Import`` node — and named four *other* walkers. Pointed at **this** check, in a
     fresh OS temp clone, all three shapes made a ``gates/`` module execute a ``scorer/``
     predicate while **D1, D2 and D3 every one reported PASS** (`INCIDENTS.md` **INC-51**).
     **D4** therefore scans both packages' **raw source text** for
     :data:`MOAT_REFUSED_DYNAMIC` and refuses the whole vocabulary of dynamic reach.
     **The two halves see different things and neither is the moat alone:** the AST walk
     sees every static import exactly and cannot see a call; the text scan sees the
     vocabulary and cannot see semantics.
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
import traceback
from collections.abc import Callable
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


#: Bytes that no prose document should contain: **C0 controls other than TAB, LF and CR.**
#: Built by construction rather than typed out, so no escape sequence in this file can be
#: eaten on the way to disk — which is the very defect A5 exists to catch (INC-13, INC-16).
#: CR (``0x0D``) is excluded because **A3 owns it**; TAB and LF are legitimate text.
_C0_CONTROL_BYTES = frozenset(b for b in range(0x20) if b not in (0x09, 0x0A, 0x0D))

#: git decides text-vs-binary on the first 8000 bytes, so the NUL search matches its window.
_GIT_BINARY_SNIFF_BYTES = 8000

A5_CHECK = "A5 no control byte in text; no NUL-free binary"


def check_gitattributes(root: Path) -> list[Result]:
    out: list[Result] = []
    path = root / ".gitattributes"
    if not path.is_file():
        # ⚠️ OPEN_FINDINGS OF-03 / INCIDENTS.md INC-07. This used to `return` ONE result, so
        # A2…A5 were not reported at all — weaker than `n/a`, and against this module's own
        # docstring: *"Checks that cannot yet apply report `n/a` with the reason, and `n/a`
        # is never silently a pass."* They reported NOTHING, and the summary line silently
        # printed four fewer checks than the group owns. INC-07 diagnosed exactly this shape
        # in `check_secrets`, fixed it there, and named this function as the surviving
        # instance with *"Systemic guardrail: none — accepted"*. REVIEW_C0_1 did not accept
        # it, and neither does this.
        #
        # ⚠️ A1 keeps THE SAME check name in both branches. Emitting a different key on pass
        # and on fail is INC-07's other half — it made a caller's lookup raise KeyError
        # instead of reporting a failure — and it was still present here.
        unevaluated = "not evaluated — .gitattributes is missing; see A1"
        return [
            Result(
                "A1 .gitattributes content",
                False,
                "missing — PROCESS.md §6a makes it a first-commit deliverable, and it is "
                "fixable only in the first commit",
            ),
            Result("A2 .gitattributes in the FIRST commit", None, unevaluated),
            Result("A3 no CRLF in any tracked file", None, unevaluated),
            Result("A4 working tree and object store hold identical bytes", None, unevaluated),
            Result(A5_CHECK, None, unevaluated),
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
    #
    # ⚠️ A5 CLOSES THE GAP THE PARAGRAPH ABOVE LEAVES OPEN, IN TWO BRANCHES, BECAUSE IT IS
    # TWO HOLES ON OPPOSITE SIDES OF GIT'S OWN VERDICT AND ONE BRANCH WOULD CLOSE NEITHER
    # HONESTLY:
    #
    #   BRANCH T — files git classifies as TEXT must carry no C0 control byte other than
    #     TAB, LF or CR. This is INCIDENTS.md **INC-13**: `CONTEXT.md` §16 carried a literal
    #     0x08 BACKSPACE — the eaten `\b` of a Windows path — for two days, inside the
    #     project's own specification, read by three build sessions and one full adversarial
    #     review and written up by one of them as a spelling mistake. A backspace does not
    #     survive rendering, so every display tool showed a plausible wrong path; and every
    #     check this repository owned asked about line endings or worktree-versus-blob
    #     equality, **both of which a lone 0x08 satisfies perfectly**.
    #
    #   BRANCH B — files git classifies as BINARY (`-text`) must carry at least one NUL in
    #     their first 8000 bytes. This is OPEN_FINDINGS **OF-01**: a single stray CR makes
    #     git call an otherwise-textual file binary on CR statistics alone, and it then lands
    #     in the bucket A3 does not scan and A4 cannot fail on.
    #
    # ⚠️ ONE BRANCH WOULD NOT DO. A control-byte scan over TEXT-classified files is **not** a
    # superset of OF-01's discriminator: OF-01's whole point is that the file in question is
    # classified BINARY, so a text-only scan skips exactly the file OF-01 is about. INC-13's
    # byte, conversely, sits in a file git correctly calls TEXT. Building one branch would
    # close OF-01 on paper and leave it open — which is this chunk's entire failure mode.
    #
    # ⚠️ The text/binary verdict comes FROM GIT (`git ls-files --eol`, the `w/` side), never
    # from a reimplementation of git's heuristic. A second copy of the predicate under test
    # is hard rule 8's spike defect, and INC-09 already made that mistake once. Branch B's
    # NUL search is **not** such a copy: it compares git's verdict against an INDEPENDENT
    # signal, which is the opposite of circularity.
    classification = _eol_classification(root)
    crlf_in_text: list[str] = []
    divergent: list[str] = []
    unverifiable: list[str] = []
    unread: list[str] = []
    not_regular: list[str] = []
    control_bytes: list[str] = []
    nul_free_binaries: list[str] = []
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
            unread.append(rel)
            continue

        if classification.get(rel) == "-text":
            binary_checked += 1
            # BRANCH B — git calls it binary. A binary file with no NUL in git's own sniff
            # window is textual content classified binary on CR statistics alone (OF-01).
            if 0 not in worktree[:_GIT_BINARY_SNIFF_BYTES]:
                nul_free_binaries.append(rel)
        else:
            text_checked += 1
            if b"\r\n" in worktree:
                crlf_in_text.append(rel)
            # BRANCH T — git calls it text. Set intersection so the scan runs in C, and the
            # LOWEST offending byte is reported at its first offset, so the answer is
            # deterministic and a reader can go straight to it (INC-13 took three attempts
            # to locate by hand).
            offenders = set(worktree) & _C0_CONTROL_BYTES
            if offenders:
                byte = min(offenders)
                control_bytes.append(
                    f"{rel}: byte 0x{byte:02X} at offset {worktree.find(bytes([byte]))}"
                )

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

    # ⚠️ A5's OWN denominator, reconciled out loud exactly as A3's and A4's are (hard rule
    # 11). A path A5 did not look at is NAMED, and it is a FAILURE, not a footnote.
    a5_skipped = sorted(set(not_regular) | set(unread))
    a5_limit = (
        " ⚠️ WHAT A5 DOES NOT CATCH, stated because a check is worth only what its limit is "
        "honest about. (1) An escape sequence that resolves to a PRINTABLE character, or to "
        "a TAB, is invisible to it: A5 is a CONTROL-BYTE check, NOT a content check, and it "
        "could not have caught INC-10's eaten sentence had the CR been a space. (2) A NUL "
        "(0x00) inside a prose document is invisible to BOTH branches — a NUL makes git "
        "classify the file binary at any size (MEASURED, 2026-08-31), so branch T never sees "
        "it and branch B accepts it as the very signal it looks for. Closing that needs a "
        "judgement about which paths are prose, which is a second copy of a decision this "
        "check deliberately takes from git. So INCIDENTS.md INC-10's `Missing` field — "
        "'nothing checks a tracked document's CONTENT, only its line endings' — STAYS OPEN. "
        "A5 narrows it; it does not close it."
    )
    out.append(
        Result(
            A5_CHECK,
            not (control_bytes or nul_free_binaries or a5_skipped),
            (
                f"BRANCH T: none of the {text_checked} file(s) git classifies as TEXT carries "
                f"a byte in 0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F (TAB, LF and CR excluded; A3 "
                f"owns CR) — the class that put a literal 0x08 BACKSPACE inside CONTEXT.md "
                f"§16 for two days (INC-13). BRANCH B: each of the {binary_checked} file(s) "
                f"git classifies as BINARY carries a NUL in its first "
                f"{_GIT_BINARY_SNIFF_BYTES} bytes, so none is textual content made binary by "
                f"stray CR statistics alone (OF-01). {reconciliation}.{a5_limit}"
                if not (control_bytes or nul_free_binaries or a5_skipped)
                else (
                    (
                        f"CONTROL BYTE in {len(control_bytes)} TEXT file(s): "
                        f"{sorted(control_bytes)[:5]}. A byte no prose document should hold, "
                        f"invisible to every renderer — see INCIDENTS.md INC-13. "
                        if control_bytes
                        else ""
                    )
                    + (
                        f"{len(nul_free_binaries)} file(s) git classifies as BINARY hold NO "
                        f"NUL byte in their first {_GIT_BINARY_SNIFF_BYTES}: "
                        f"{sorted(nul_free_binaries)[:5]}. That is the signature of textual "
                        f"content made binary by stray CR statistics — and in that state "
                        f"NEITHER A3 NOR A4 will look at it (OPEN_FINDINGS OF-01; INC-06, "
                        f"INC-10). "
                        if nul_free_binaries
                        else ""
                    )
                    + (
                        f"{len(a5_skipped)} tracked path(s) A5 could not read and therefore "
                        f"did not check: {a5_skipped[:5]} — reported as a FAILURE, never as a "
                        f"pass. "
                        if a5_skipped
                        else ""
                    )
                    + reconciliation
                    + a5_limit
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

#: ⚠️ **THE SECOND HALF OF THE MOAT, ADDED 2026-09-02 — `OF-110`, RAISED BY C6 REVIEW 3
#: (`3605d31c`), MEASURED AGAINST **THIS** CHECK AND FOUND TO PASS. `INCIDENTS.md` INC-51.**
#:
#: `OF-110` measured that ``__import__("openai")``, ``importlib.import_module("openai")`` and
#: ``getattr(pkg, "name")`` **all escape an AST import walk BY CONSTRUCTION** — a call
#: expression is not an ``ast.Import`` node — and named C2's, C3's, C6's and C13's walkers.
#: It did **not** name D3. This session pointed it at D3 and measured, in a fresh OS temp
#: clone: a minimal ``gates/`` reaching a minimal ``scorer/`` predicate by
#: ``importlib.import_module``, by ``__import__`` and by ``getattr`` + ``sys.modules``
#: **passed D1, D2 AND D3, all three, on all three shapes**, while
#: ``gates.arm2.decide(6_000_000, 5_000_000)`` really did return ``DENY`` computed by the
#: scorer's module. **The line `CLAUDE.md` calls "the whole moat" printed `clean` over the
#: spike defect it exists to make impossible.**
#:
#: So the guard is now **AST *plus* source text**, and the two halves cover different
#: things: the AST walk sees every *static* import exactly and cannot see a call; this scan
#: sees the *vocabulary* of dynamic reach and cannot see semantics. **Neither is the moat
#: alone.**
#:
#: ⚠️ **THIS IS A REFUSAL, NOT A PUZZLE TO RESOLVE.** `gates/` and `scorer/` are pure
#: predicate packages — hard rule 8's "core logic takes data in and returns results" — and
#: **neither has any legitimate need for a dynamic import, for reflection, or for `exec`.**
#: The scan therefore refuses the whole vocabulary rather than trying to decide, from text,
#: whether a particular ``getattr`` reaches a module: the cost of a false positive is a
#: rewording, and the cost of a false negative is the submission's central argument.
#: **Both packages are still unwritten (C8 and C9), so this lands BEFORE their builders
#: rather than as a retrofit.**
#:
#: **Removing a name from this list is a Class A deviation requiring an architect ruling in
#: `QUESTIONS.md`, exactly as adding to `MOAT_ALLOW_LIST` is**, and
#: ``tests/test_c0_fix_probes.py`` pins the set so that narrowing it means editing an
#: assertion a review will see.
MOAT_REFUSED_DYNAMIC: tuple[tuple[str, str], ...] = (
    ("importlib", r"\bimportlib\b"),
    ("__import__", r"\b__import__\b"),
    ("sys.modules", r"\bsys\s*\.\s*modules\b"),
    ("getattr", r"\bgetattr\b"),
    ("setattr", r"\bsetattr\b"),
    ("exec", r"\bexec\s*\("),
    ("eval", r"\beval\s*\("),
    ("compile", r"\bcompile\s*\("),
    ("runpy", r"\brunpy\b"),
    ("pkgutil", r"\bpkgutil\b"),
    ("imp", r"\bimp\s*\.\s*load_"),
    ("globals", r"\bglobals\s*\(\s*\)"),
    ("locals", r"\blocals\s*\(\s*\)"),
    ("vars", r"\bvars\s*\("),
)


def _refused_dynamic_lines(where: str, text: str) -> list[tuple[str, int, str, str]]:
    """Every :data:`MOAT_REFUSED_DYNAMIC` name appearing in one file's SOURCE TEXT.

    The single place the refusal is actually applied, so that the two callers below — the
    package-directory walk and the transitive-closure walk — cannot drift into scanning
    for *different* vocabularies. ``OF-249`` is what a scan set that drifts looks like.
    """
    hits: list[tuple[str, int, str, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for name, pattern in MOAT_REFUSED_DYNAMIC:
            if re.search(pattern, line):
                hits.append((where, number, name, line.strip()[:120]))
    return hits


def _dynamic_reach_hits(packages: dict[str, Path]) -> list[tuple[str, int, str, str]]:
    """Every :data:`MOAT_REFUSED_DYNAMIC` name appearing in either package's SOURCE TEXT.

    Returns ``(relative path, line number, refused name, the line)``, sorted. The scan is
    over **raw text**, deliberately: the whole point of `OF-110` is that the AST cannot see
    these forms, so a second AST pass would reproduce the blind spot in a different shape.

    ⚠️ **THIS FUNCTION WALKS DIRECTORIES, AND A DIRECTORY IS NOT THE MOAT'S SCAN SET.** It
    is kept, unchanged, because four other chunks' tests point it at *their own* package
    directory, which is exactly what they mean. **D4 no longer uses it alone** — see
    :func:`_dynamic_reach_hits_in_modules` and `OF-249`.
    """
    hits: list[tuple[str, int, str, str]] = []
    for label, package in packages.items():
        for py in sorted(package.rglob("*.py")):
            try:
                text = py.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:  # pragma: no cover - unreadable file, reported not skipped
                hits.append((f"{label}/{py.name}", 0, "UNREADABLE", f"{type(exc).__name__}"))
                continue
            hits.extend(
                _refused_dynamic_lines(f"{label}/{py.relative_to(package).as_posix()}", text)
            )
    return sorted(hits)


def _dynamic_reach_hits_in_modules(
    modules: dict[str, Path],
) -> list[tuple[str, int, str, str]]:
    """The same refusal, applied to an EXPLICIT set of first-party modules by dotted name.

    ⚠️ **THIS EXISTS BECAUSE `OF-249` MEASURED THE TWO HALVES OF THE MOAT SCANNING
    DIFFERENT SETS, AND THE SMALLER SET WAS THE ONE MEANT TO COVER THE OTHER'S KNOWN BLIND
    SPOT.** `D1`–`D3` walk the **transitive closure** of both packages; `D4` walked the two
    package **directories**. C19 README BUILD 1 (`9f31d708`) measured this tree: 118
    first-party modules indexed, ``gates/`` closure 15, ``scorer/`` closure 6, intersection
    empty — and ``(gates_closure | scorer_closure) - gates_dir - scorer_dir`` was
    ``{whetstone_gate.config}``. **Exactly one module, inside the gate side of the moat,
    text-scanned by nothing: a dynamic hop planted there would have passed D1, D2, D3 AND
    D4 over a live ``gates/`` → ``scorer/`` reach**, which is `INC-51`'s measured class one
    module further out.

    ⚠️ **`OF-249` AS RAISED WAS STRUCTURAL, NOT EXPLOITED** — C19 read the call site and
    measured the closure difference, and its own row says that is weaker evidence than
    `INC-51`'s planted reach. **This session then planted it**, in a `git clone` in a fresh
    OS temp directory: the pre-fix `D4` printed **PASS** while
    ``gates.of249_probe.decide(6_000_000, 5_000_000)`` returned ``DENY`` computed by
    ``scorer/invariants.py``. ⚠️ **NOTHING WAS EVER PLANTED IN THIS REPOSITORY** (`INC-11`,
    `INC-17`), so what is demonstrated is a breach of the **check**, in a throwaway tree —
    not a breach that existed in this tree's own history. `INCIDENTS.md` `INC-132` records
    both facts and all four drives.

    Returns the same ``(where, line number, refused name, the line)`` tuple shape, with
    ``where`` the **dotted module name** so a reader can tell a closure-only hit from a
    directory hit at a glance.
    """
    hits: list[tuple[str, int, str, str]] = []
    for where, py in sorted(modules.items()):
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:  # pragma: no cover - unreadable file, reported not skipped
            hits.append((where, 0, "UNREADABLE", f"{type(exc).__name__}"))
            continue
        hits.extend(_refused_dynamic_lines(where, text))
    return sorted(hits)


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

    absent = (
        "neither directory exists yet — gates/ is built by C9, scorer/ by C8. Q-004 "
        "ruled OPTION 1 on 2026-08-31: both live UNDER the package, at "
        "src/whetstone_gate/gates/ and src/whetstone_gate/scorer/. Both candidate "
        "layouts are still checked — it costs nothing and the ruled one is now first"
    )
    return [
        Result("D1 gates/ and scorer/ share no first-party module", None, absent),
        # ⚠️ OF-03's doctrine, which this file already applies to F2–F4: a check's ABSENCE
        # and a check's PASS must never be the same thing to a caller. D4 is emitted here
        # as `n/a` so that a reviewer reading this output learns the source-text half
        # EXISTS and has not run, rather than learning nothing about it at all.
        Result(
            "D4 no dynamic import in gates/ or scorer/",
            None,
            f"{absent}. This is the source-text half of the moat added for OF-110 "
            f"(C6 REVIEW 3, 3605d31c) and INC-51: it refuses "
            f"{len(MOAT_REFUSED_DYNAMIC)} names outright",
        ),
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

    # ⚠️ D4 — THE SOURCE-TEXT HALF, OVER THE SAME SET D1–D3 WALK. OF-110 / INC-51 / OF-249.
    #
    # ⚠️ THE SCAN SET IS THE CLOSURE, NOT THE TWO DIRECTORIES, AND THAT IS THE WHOLE OF
    # OF-249's REMEDY. Until 2026-09-03 this line read
    # `_dynamic_reach_hits({gates_rel: gates, scorer_rel: scorer})` — two directories —
    # while D1–D3 walked the transitive closure. Any first-party module inside a closure
    # but outside both directories was therefore scanned by NOTHING, and there was exactly
    # one: `whetstone_gate.config`, on the GATE side. The directories are still walked as
    # well, so a `.py` file that no import reaches — dead in the graph, live on disk — is
    # not silently dropped by widening.
    directory_hits = _dynamic_reach_hits({gates_rel: gates, scorer_rel: scorer})
    in_a_directory = {
        py.resolve()
        for package in (gates, scorer)
        for py in package.rglob("*.py")
    }
    closure_only = {
        module: known[module]
        for module in sorted(gate_closure | scorer_closure)
        if module in known and known[module].resolve() not in in_a_directory
    }
    dynamic = sorted(directory_hits + _dynamic_reach_hits_in_modules(closure_only))
    scan_set = (
        f"SCANNED: both package directories PLUS the {len(closure_only)} module(s) inside "
        f"either TRANSITIVE CLOSURE but outside them "
        f"({sorted(closure_only) if closure_only else 'none'}) — OF-249, which measured "
        f"that scanning the directories alone left exactly one closure module "
        f"(whetstone_gate.config, on the GATE side) text-scanned by nothing"
    )
    results.append(
        Result(
            "D4 no dynamic import in gates/ or scorer/",
            not dynamic,
            f"neither package names any of the {len(MOAT_REFUSED_DYNAMIC)} refused "
            f"dynamic-reach forms in its source text. D1–D3 walk the AST, which cannot see "
            f"a call expression BY CONSTRUCTION; this walks the text, which cannot see "
            f"semantics. Neither is the moat alone (OF-110, INC-51). {scan_set}"
            if not dynamic
            else (
                "REFUSED DYNAMIC REACH: "
                + "; ".join(
                    f"{where}:{number} uses {name!r} — {line!r}"
                    for where, number, name, line in dynamic[:6]
                )
                + f" ({len(dynamic)} hit(s) total). ⚠️ gates/ and scorer/ are PURE "
                "PREDICATE packages and neither has any legitimate need for a dynamic "
                "import, for reflection, or for exec. MEASURED 2026-09-02 (INC-51): a "
                "gates/ module reaching scorer/ by importlib.import_module, by __import__ "
                "or by getattr on the package root PASSES D1, D2 AND D3 — a call "
                "expression is not an ast.Import node, so the AST walk cannot see it. "
                "In the spike, gate.js and invariants.js both called world.js:intentKey, "
                "so the invariant COULD NOT HAVE FIRED unless the gate had a bug: that is "
                "not a result, it is a definition. Write it statically so D1–D3 can see "
                "it, or write it twice on purpose. Removing a name from "
                "MOAT_REFUSED_DYNAMIC is a CLASS A deviation requiring an architect "
                "ruling in QUESTIONS.md. " + scan_set
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

#: A **trailer-shaped** line, as git itself shapes one: a key of ASCII letters, digits and
#: hyphens, optional space, then the separator. `[VERIFIED HERE, 2026-09-02]` against
#: ``git interpret-trailers --parse`` on seven synthetic messages — see :func:`_trailer_block`.
_TRAILER_SHAPED = re.compile(r"^[A-Za-z0-9-]+[ \t]*:")


def _trailer_block(body: str) -> str:
    """The commit message's **trailer block** — where a trailer may be read from.

    ⚠️ **`QUESTIONS.md` Q-080, RULED 2026-09-02, remedy 3.** ``_TOKEN_TRAILER_ANY`` cannot
    tell **a trailer** from **a quotation of one**, and this project *requires* sessions to
    write about their own tokens in their own commit messages, so a quoted line at column 0
    turned E5 red on a commit that was correctly tokened (`INCIDENTS.md` **INC-49**). The
    ruling's remedy: read the trailer block, not the whole body. **Neither pattern above is
    widened — Q-014 (i) is not reopened — only *where* they are applied narrows.**

    ⚠️ **AND THE RULING'S PARENTHETICAL GLOSS IS REFINED IN EXACTLY ONE DIRECTION, WHICH IS
    A DECLARED CLASS A DEVIATION RECORDED IN `QUESTIONS.md` Q-081 AND `INCIDENTS.md`
    INC-52.** The gloss reads *"the message's LAST PARAGRAPH (`git interpret-trailers`)"*.
    **That was implemented literally first and MEASURED over the whole log before anything
    shipped: it changes the verdict on 74 of 277 commits**, because

      * `git interpret-trailers` stops at the **first blank line** — verified against git
        itself, not inferred: ``A-Key: 1`` + blank + ``B-Key: 2`` parses to **`B-Key` only**,
        and the same two lines with no blank between them parse to **both**; and
      * **this project's own convention puts a blank line between `Session-Token:` and the
        harness's `Co-Authored-By:`**, so under the literal gloss the token sits one
        paragraph too high and becomes invisible.

    Shipping that would take **E1 — the check that catches a token that was never issued —
    from 261 of 277 commits to 187**, and make E4 print a false statement about 74 commits
    that *do* carry a trailer: `Q-014 (ii)`'s recorded defect at eighteen times the scale,
    which is **hard rule 6**. So what this returns is git's own criterion for a *trailer
    paragraph*, extended across a blank line **only between paragraphs that are themselves
    entirely trailers**:

      the maximal trailing run of paragraphs — the subject paragraph excluded, as in git —
      in which **every** line is trailer-shaped or a whitespace continuation of one.

    Measured effect against the previous whole-body scan: **1 of 277 commits** changes
    verdict (`97a5981`, whose message carries a stray bare ``@`` from a leaked here-string
    delimiter, and whose trailer **git itself** has never been able to read either), plus
    `c4d4460`'s quotation, which is the defect being fixed.

    ⚠️ **The residual is named rather than hoped away:** a quotation still escapes if it is
    alone in its own paragraph *and* contiguous with the trailing trailer run. That shape is
    fired at, and asserted still-caught, in ``tests/test_c0_fix_probes.py``.
    """
    lines = body.replace("\r\n", "\n").split("\n")
    paragraphs: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.strip():
            current.append(line)
        elif current:
            paragraphs.append(current)
            current = []
    if current:
        paragraphs.append(current)

    # git: "the first paragraph is the title and cannot be trailers". A one-paragraph
    # message therefore has no trailer block at all, which is git's answer too.
    def _is_trailer_paragraph(paragraph: list[str]) -> bool:
        if not _TRAILER_SHAPED.match(paragraph[0]):
            return False
        return all(
            _TRAILER_SHAPED.match(line) or line[:1].isspace() for line in paragraph[1:]
        )

    block: list[str] = []
    for paragraph in reversed(paragraphs[1:]):
        if not _is_trailer_paragraph(paragraph):
            break
        block.insert(0, "\n".join(paragraph))
    return "\n".join(block)

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
    outside_block: list[str] = []
    malformed: list[tuple[str, str]] = []
    for record in filter(None, (r.strip() for r in log.split("\x1e"))):
        sha, _, body = record.partition("\x1f")
        # ⚠️ Q-080's ruling: a trailer is read from the TRAILER BLOCK, never from the whole
        # body, so a commit message that QUOTES a trailer at column 0 in a prose paragraph
        # is no longer parsed as carrying one. Q-081/INC-52 record the one refinement to
        # the ruling's wording, and `_trailer_block` carries the measurement.
        block = _trailer_block(body)
        strict = _TOKEN_TRAILER.findall(block)
        # ⚠️ Q-014 (i): the PERMISSIVE pattern is applied ONLY where the strict one did not
        # match, and a trailer it catches that the strict one did not is MALFORMED — not
        # absent. `_TOKEN_TRAILER` is the authority for "well formed"; there is deliberately
        # no second copy of the 8-hex predicate here to drift away from it.
        for value in _TOKEN_TRAILER_ANY.findall(block):
            if value not in strict:
                malformed.append((sha, value))
        tokens = [t.lower() for t in strict]
        if not tokens and not any(s == sha for s, _ in malformed):
            untrailered.append(sha)
            # ⚠️ Q-014 (ii) applied to the NEW parser, and INC-52's second half. "No
            # trailer" and "a trailer this parser will not read" must not collapse into one
            # list again: that collapse is the false statement Q-014 (ii) was ruled about.
            # A commit here has a `Session-Token:`-shaped line somewhere OUTSIDE its trailer
            # block — a prose quotation, or a real trailer that a stray non-trailer line in
            # the same paragraph disqualifies, which is `97a5981` and which git itself
            # cannot read either. It is REPORTED, with its count, never rounded into the
            # untrailered prose.
            if _TOKEN_TRAILER_ANY.search(body):
                outside_block.append(sha)
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
        absent = [s for s in untrailered if s not in set(outside_block)]
        out.append(
            Result(
                "E4 every commit carries a Session-Token trailer",
                None,
                f"{len(untrailered)} commit(s) carry no trailer IN THEIR TRAILER BLOCK. "
                f"{len(absent)} of them carry no Session-Token: line ANYWHERE: "
                f"{[s[:7] for s in absent[:6]]}. "
                "The C0 build prompt issued no SESSION-TOKEN and this session did not "
                "fabricate one — a fabricated token would be exactly the 'token that was "
                "never issued' that E1 exists to catch. See QUESTIONS.md Q-001. "
                "⚠️ This list holds ONLY commits with no trailer at all: a trailer that is "
                "present but malformed is E5's, not this list's (Q-014 (i))"
                + (
                    f". ⚠️ AND {len(outside_block)} commit(s) DO carry a Session-Token: "
                    f"line, OUTSIDE the trailer block, so this parser does not read it: "
                    f"{[s[:7] for s in outside_block[:6]]}. That is a prose QUOTATION "
                    "(correct, and the whole point of Q-080) or a real trailer whose "
                    "paragraph holds a stray non-trailer line — 97a5981 carries a bare "
                    "'@' from a leaked here-string delimiter, and `git interpret-trailers "
                    "--parse` returns nothing for it either. Counted and NAMED rather than "
                    "folded into the sentence above, because folding them together is "
                    "exactly the false statement Q-014 (ii) was ruled about "
                    "(QUESTIONS.md Q-081; INCIDENTS.md INC-52)"
                    if outside_block
                    else ""
                ),
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
    where = cfg.config_dir()
    try:
        sweep = cfg.sweep_configs()
    except cfg.ConfigError as exc:
        # ⚠️ OF-03's remedy, applied here too: when F1 fails, the other three are still
        # EMITTED, as `n/a` with the reason. A check's absence and a check's pass must not
        # be the same thing to a caller (INCIDENTS.md INC-07), and the summary line must not
        # silently print fewer checks than the group owns.
        unevaluated = "not evaluated — config/ did not load; see F1"
        return [
            Result("F1 config/ loads", False, f"{where}: {exc}"),
            Result("F2 undetermined values are DECLARED, not defaulted", None, unevaluated),
            Result("F3 OPERATOR-owed values", None, unevaluated),
            Result("F4 config files not yet written", None, unevaluated),
        ]

    outstanding = list(sweep.outstanding)
    operator_owed = [s for s in outstanding if s[2] == "TODO_OPERATOR"]
    # ⚠️ OF-06. A BLANK is not a declared sentinel and must not be reported as one: a
    # sentinel is a declaration with an owner, a blank is an omission with nobody's name on
    # it. Reporting them together under "undetermined values are DECLARED" would relabel a
    # defect as a plan — which is the shape of every finding in this review.
    blanks = [s for s in outstanding if cfg.is_blank_marker(s[2])]
    declared = [s for s in outstanding if not cfg.is_blank_marker(s[2])]
    detail = (
        "no undetermined values remain"
        if not declared
        else "; ".join(f"{name}:{path} = {sentinel}" for name, path, sentinel in declared)
    ) + (
        f" ⚠️ AND {len(blanks)} BLANK value(s), which are NOT declared and are a hard-rule-9 "
        f"defect — written down and never supplied, invisible to the TODO_ mechanism, and "
        f"returned as None by a loader that had no way to see them (OPEN_FINDINGS OF-06): "
        + "; ".join(f"{name}:{path} = {marker}" for name, path, marker in blanks)
        if blanks
        else ""
    )
    # ⚠️ F1 now reports WHAT ACTUALLY LOADED. It used to be the hardcoded string
    # "protocol.yaml and lanes.yaml parse" — a conclusion, naming a file it had never
    # opened, printed unchanged over a config/ from which protocol.yaml had been deleted.
    loaded = ", ".join(f"{name}.yaml" for name in sweep.loaded) or "(nothing)"
    return [
        Result(
            "F1 config/ loads",
            True,
            f"{where} — {len(sweep.loaded)} file(s) opened and parsed: {loaded}. "
            f"REQUIRED: {', '.join(f'{n}.yaml' for n in cfg.REQUIRED_CONFIGS)} — a missing "
            f"one is a hard refusal, never a skip",
        ),
        Result(
            "F2 undetermined values are DECLARED, not defaulted",
            not blanks,
            f"{len(declared)} explicit TODO_ sentinel(s) across {len(sweep.loaded)} "
            f"parsed file(s); the loader RAISES on each rather than substituting a value "
            f"(hard rule 9). {detail}",
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
        Result(
            "F4 config files not yet written",
            None if sweep.not_yet else True,
            "; ".join(f"{name}.yaml — {who}" for name, who in sweep.not_yet)
            + ". Reported as NOT-YET, never as nothing: an absent file contributes zero "
            "sentinels, and 'zero' must not be readable as 'clean'"
            if sweep.not_yet
            else f"every known config exists: {', '.join(cfg.KNOWN_CONFIGS)}",
        ),
    ]


# --------------------------------------------------------------------------------------


def check_examined_root(root: Path) -> list[Result]:
    """⚠️ `OPEN_FINDINGS.md` **OF-09** — *which* repository did this run actually look at?

    ``cfg.repo_root()`` is ``Path(__file__).resolve().parents[2]``, correct only for an
    **editable src-layout install**. Two live consequences, both reproduced by the review:

      * ``pip install .`` (non-editable — what someone not told about ``-e`` will type)
        resolves it to ``…/.venv/Lib``. `check-roles` then printed
        **``PASS F1 config/ loads``** over **zero** config files.
      * One venv, two checkouts: run from inside clone B with clone A's venv active, it
        reports on **clone A**. It printed a full green report while the reviewer stood in a
        clone with a deliberately corrupted ``.gitattributes``. **It fooled the reviewer for
        one experiment**, which is the strongest available evidence that it will fool
        somebody else.

    For a tool whose entire output is *"this repository is sound"*, not naming the
    repository is a reporting defect on its own — and passing vacuously over a directory
    that is not a repository is worse than that.
    """
    has_git = (root / ".git").exists()
    has_config = (root / "config").is_dir()
    missing = [
        name for name, present in ((".git", has_git), ("config/", has_config)) if not present
    ]
    return [
        Result(
            "R1 the examined root IS this repository",
            not missing,
            f"{root} holds .git and config/"
            if not missing
            else (
                f"{root} holds no {' and no '.join(missing)}. THIS IS NOT THE REPOSITORY — "
                f"every check below would report on it anyway, and a green report over the "
                f"wrong directory is worse than a red one. The root is resolved from "
                f"src/whetstone_gate/config.py's own location (parents[2]), which is correct "
                f"ONLY for an editable src-layout install: `pip install -e \".[dev]\"`. "
                f"See OPEN_FINDINGS.md OF-09"
            ),
        )
    ]


def run(root: Path | None = None) -> int:
    """Run every check. Returns a process exit code."""
    root = root or cfg.repo_root()

    say("check-roles — the repository's structural invariants\n")
    # ⚠️ OF-09: NAME THE ROOT. A tool that reports "this repository is sound" must say which.
    say(f"  ROOT EXAMINED: {root}")
    say(f"  CONFIG DIR   : {cfg.config_dir()}")
    say()

    # ⚠️ OF-10: the groups are built LAZILY, one at a time, each inside its own try. They
    # used to be built in one eager list expression with
    # `check_gitattributes(root) + check_secrets(root)` as a SINGLE element — so a
    # `.gitattributes` carrying a non-UTF-8 byte made `read_text` raise and took **the secret
    # scan** down with it, along with D, E and F: a bare traceback, exit 1, and ZERO check
    # output. Fail-closed on the exit code, no information in the report. A and B/C are also
    # separated here so that neither can silence the other at all.
    groups: list[tuple[str, str, Callable[[Path], list[Result]]]] = [
        ("R", "the root this run examined (OF-09)", check_examined_root),
        ("A", "the freeze prerequisite (PROCESS.md §6a)", check_gitattributes),
        ("B/C", "secrets", check_secrets),
        ("D", "the gate/scorer moat", check_gate_scorer_isolation),
        ("E", "session identity (PROCESS.md §7a)", check_session_tokens),
        ("F", "config/ completeness (hard rule 9)", check_config_sentinels),
    ]

    failures = 0
    not_applicable = 0
    total = 0
    for letter, title, build in groups:
        say(f"  {letter} — {title}")
        try:
            results = build(root)
        except Exception as exc:  # noqa: BLE001 — a raising group must not silence the rest
            where = ""
            frames = traceback.extract_tb(exc.__traceback__)
            if frames:
                where = f", raised at {Path(frames[-1].filename).name}:{frames[-1].lineno}"
            results = [
                Result(
                    f"{letter}! this check GROUP raised and did not run",
                    False,
                    f"{type(exc).__name__}: {exc}{where}. The other groups below still ran — "
                    f"OPEN_FINDINGS OF-10: one group's failure must not silence another, and "
                    f"a `.gitattributes` problem must never be able to suppress the secret "
                    f"scan",
                )
            ]
        for r in results:
            total += 1
            say(f"    [{r.symbol}] {r.check}")
            say(f"           {r.detail}")
            if r.ok is False:
                failures += 1
            elif r.ok is None:
                not_applicable += 1
        say()

    say(f"  ROOT EXAMINED: {root}")
    say(f"  {total - failures - not_applicable} passed, {failures} failed, {not_applicable} n/a")
    if failures:
        say("\n  FAIL — a structural invariant is broken. This is not a style issue.")
        return 1
    say("\n  OK — no structural invariant is broken. `n/a` is never a pass; see the reasons above.")
    return 0
