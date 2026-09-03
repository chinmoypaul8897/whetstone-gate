"""The repository's structural invariants, as unit tests.

``make check-roles`` runs the same checks as a script with human-readable output; this
file runs them under pytest so that ``make test`` cannot go green while one is broken.
Same code, two entry points — not two implementations.
"""

from __future__ import annotations

import dataclasses
import os
import re
import subprocess
from pathlib import Path

import pytest

import whetstone_gate
from whetstone_gate import check_roles
from whetstone_gate import config as cfg


def _results(group):
    return {r.check: r for r in group}


# -- .gitattributes: the freeze prerequisite -------------------------------------------


def test_gitattributes_is_correct_and_in_the_first_commit(repo_root):
    """`PROCESS.md` §6a, the whole reason this file exists.

    On this machine ``core.autocrlf`` is ``true``, set **system-wide** by the Git for
    Windows installer, so a file committed with LF is checked out with CRLF and the two
    hash differently. The pre-registration fingerprint is computed from **git objects**,
    and without ``* text=auto eol=lf`` a fingerprint published from the operator's working
    tree would fail verification for every reviewer who clones on Linux or macOS — at the
    moment of judging, silently, looking like fraud rather than a line-ending bug.

    It is fixable **only in the first commit**.
    """
    results = _results(check_roles.check_gitattributes(repo_root))

    assert results["A1 .gitattributes content"].ok is True, results["A1 .gitattributes content"].detail
    assert results["A2 .gitattributes in the FIRST commit"].ok is True, (
        results["A2 .gitattributes in the FIRST commit"].detail
    )
    assert results["A3 no CRLF in any tracked file"].ok is True, (
        results["A3 no CRLF in any tracked file"].detail
    )
    assert results["A4 working tree and object store hold identical bytes"].ok is True, (
        results["A4 working tree and object store hold identical bytes"].detail
    )


def test_the_crlf_check_still_fires_on_text_and_no_longer_lies_about_binary(tmp_path):
    """⚠️ The proof that A3's narrowing is **exactly** the false positive and nothing more.

    A3 used to scan every tracked file's raw bytes for ``\\r\\n``. A PNG's deflate stream
    contains those bytes as *data*, so committing the two dashboard screenshots turned
    ``make check-roles`` and ``make test`` red on a repository that was sound
    (`INCIDENTS.md` INC-09). A3 now asks **git** which files are text.

    `CLAUDE.md` hard rule 6 forbids loosening an assertion to get green, so the narrowing
    is not taken on trust — it is asserted, in a throwaway repository, that:

      * a **text** file carrying CRLF still fails A3 (the assertion is intact), **and**
      * a **binary** file carrying the same bytes does not (the false positive is gone),
        while A4 covers it with the stronger byte-identity assertion instead.

    Run this against the old code and the binary case fails. That is what makes the change
    provably meaningful rather than merely convenient.
    """
    import subprocess as sp

    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "fixture@example.invalid"],
        ["git", "config", "user.name", "fixture"],
    ):
        sp.run(cmd, cwd=tmp_path, check=True, capture_output=True)

    (tmp_path / ".gitattributes").write_bytes(b"* text=auto eol=lf\n")
    # Text: CRLF here is a line ending, and it is a real defect.
    (tmp_path / "text_with_crlf.md").write_bytes(b"one\r\ntwo\r\n")
    # Binary: the NUL byte is what makes git say `-text`, exactly as in a PNG. The same
    # CRLF bytes here are payload, not line endings.
    (tmp_path / "binary_with_crlf.bin").write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\r\npayload\r\n"
    )
    sp.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
    sp.run(["git", "commit", "-qm", "fixture"], cwd=tmp_path, check=True, capture_output=True)

    # Exactly two offenders exist, so the detail's [:5] truncation cannot be what hides the
    # binary file. Asserted, not assumed — otherwise a >5-offender detail would let this
    # test pass against the OLD code and the proof would be worthless.
    results = _results(check_roles.check_gitattributes(tmp_path))
    a3 = results["A3 no CRLF in any tracked file"]

    assert a3.ok is False, (
        "A3 passed on a text file that genuinely carries CRLF — the assertion has been "
        f"gutted, which is hard rule 6's forbidden move. detail: {a3.detail}"
    )
    assert "more)" not in a3.detail, (
        "the detail is truncated, so 'binary_with_crlf.bin not in detail' would prove "
        f"nothing. detail: {a3.detail}"
    )
    assert "text_with_crlf.md" in a3.detail, (
        f"A3 no longer names the real CRLF offender. detail: {a3.detail}"
    )
    assert "binary_with_crlf.bin" not in a3.detail, (
        "A3 still reports a binary file's payload bytes as a line-ending defect — this is "
        f"INC-09 unfixed. detail: {a3.detail}"
    )

    # And A4 catches the real defect on the text file (git would rewrite it on checkin).
    #
    # ⚠️ A4 does NOT "check the binary file harder" — that claim was made and is FALSE.
    # On `-text` content git converts nothing, so A4's two hashes are equal BY
    # CONSTRUCTION and A4 cannot fail there. What justifies the narrowing is that the
    # removed failures were false positives, which the next test asserts directly.
    a4 = results["A4 working tree and object store hold identical bytes"]
    assert a4.ok is False, (
        f"A4 passed on a file git would rewrite on checkin. detail: {a4.detail}"
    )
    assert "text_with_crlf.md" in a4.detail, f"A4 does not name the offender: {a4.detail}"
    assert "binary_with_crlf.bin" not in a4.detail, (
        f"A4 claims git rewrites a binary file, which it does not: {a4.detail}"
    )


def test_every_failure_the_narrowing_removed_was_a_false_positive(tmp_path):
    """⚠️ The REAL hard-rule-6 defence for INC-09's narrowing, asserted rather than argued.

    The first justification written for it — *"a binary file is not skipped; it is checked
    harder"* — **was false**, and it was the load-bearing sentence. A4 cannot fail on
    `-text` content, because git applies no conversion there and its two hashes are equal
    by construction.

    What actually justifies the change is narrower and checkable: **every failure the
    narrowing removed was a false positive with respect to the property being asserted.**
    `PROCESS.md` §6a's property is *"a reviewer who clones this gets the committed bytes"*,
    and this test asserts exactly that, end to end, on the adversarial case — a file that
    LOOKS textual (plain ASCII, CRLF endings) but that git calls binary because of a single
    NUL byte. Old A3 failed on it. It round-trips perfectly.

    If this ever fails, the narrowing really did lose a true positive and Q-012's default
    must be reverted.
    """
    import hashlib
    import subprocess as sp

    origin = tmp_path / "origin"
    origin.mkdir()
    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "fixture@example.invalid"],
        ["git", "config", "user.name", "fixture"],
    ):
        sp.run(cmd, cwd=origin, check=True, capture_output=True)

    (origin / ".gitattributes").write_bytes(b"* text=auto eol=lf\n")
    # Plain ASCII, CRLF-terminated, ONE NUL byte. git calls the whole file `-text`.
    payload = b"header\r\n" + b"\x00" + b"value=1\r\nvalue=2\r\n"
    (origin / "operator_note.txt").write_bytes(payload)
    sp.run(["git", "add", "-A"], cwd=origin, check=True, capture_output=True)
    sp.run(["git", "commit", "-qm", "fixture"], cwd=origin, check=True, capture_output=True)

    eol = sp.run(
        ["git", "ls-files", "--eol", "operator_note.txt"],
        cwd=origin, check=True, capture_output=True, text=True,
    ).stdout
    assert "w/-text" in eol, (
        f"the fixture is not exercising the binary branch at all; git says: {eol!r}"
    )

    # The property, end to end: a FRESH CLONE reproduces the committed bytes exactly.
    clone = tmp_path / "clone"
    sp.run(
        ["git", "clone", "-q", str(origin), str(clone)], check=True, capture_output=True
    )
    cloned = (clone / "operator_note.txt").read_bytes()

    assert cloned == payload, (
        "a fresh clone did NOT reproduce the working-tree bytes for a file git calls "
        "binary. The narrowing in INC-09 would then have removed a TRUE positive, and "
        "Q-012's default must be reverted. "
        f"origin sha256={hashlib.sha256(payload).hexdigest()} "
        f"clone sha256={hashlib.sha256(cloned).hexdigest()}"
    )

    # And the check agrees: no CRLF complaint, no rewrite predicted.
    results = _results(check_roles.check_gitattributes(origin))
    assert results["A3 no CRLF in any tracked file"].ok is True
    assert results["A4 working tree and object store hold identical bytes"].ok is True


def test_a4_does_not_fire_merely_because_the_tree_is_dirty(tmp_path):
    """A4 must not confuse *"you have unsaved work"* with *"your files are corrupting"*.

    A4 asks git's round-trip question — would the filter chain rewrite these bytes? — which
    is `PROCESS.md` §6a's actual property and is answerable on a dirty tree. Comparing
    against the index or ``HEAD`` instead would report every uncommitted edit as a
    line-ending defect and leave this check red through the ordinary middle of a session,
    which is how a check earns its way onto the ignore list.
    """
    import subprocess as sp

    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "fixture@example.invalid"],
        ["git", "config", "user.name", "fixture"],
    ):
        sp.run(cmd, cwd=tmp_path, check=True, capture_output=True)

    (tmp_path / ".gitattributes").write_bytes(b"* text=auto eol=lf\n")
    (tmp_path / "clean.md").write_bytes(b"committed\n")
    sp.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
    sp.run(["git", "commit", "-qm", "fixture"], cwd=tmp_path, check=True, capture_output=True)

    # Now dirty the tree — an ordinary uncommitted edit, still LF.
    (tmp_path / "clean.md").write_bytes(b"committed\nand then edited\n")

    # Assert the tree really IS dirty, or this test passes vacuously and proves nothing.
    dirty = sp.run(
        ["git", "status", "--porcelain"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout
    assert "clean.md" in dirty, f"the fixture is not dirty, so this proves nothing: {dirty!r}"

    results = _results(check_roles.check_gitattributes(tmp_path))
    assert results["A3 no CRLF in any tracked file"].ok is True
    assert results["A4 working tree and object store hold identical bytes"].ok is True, (
        "A4 fired on an ordinary uncommitted LF edit — it is asking the wrong question. "
        f"detail: {results['A4 working tree and object store hold identical bytes'].detail}"
    )


def test_the_object_store_and_the_working_tree_agree(repo_root):
    """The property `.gitattributes` buys, asserted end to end.

    ``sha256(working-tree bytes)`` must equal ``sha256(git show HEAD:<path>)`` for every
    tracked text file. If these ever diverge, `PROCESS.md` §6a.3's reviewer procedure
    stops reproducing the published fingerprint.
    """
    import hashlib

    tracked = subprocess.run(
        ["git", "ls-files"], cwd=repo_root, capture_output=True, text=True, check=True
    ).stdout.split()

    mismatched = []
    for rel in tracked:
        path = repo_root / rel
        if not path.is_file():
            continue
        worktree = hashlib.sha256(path.read_bytes()).hexdigest()
        blob = subprocess.run(
            ["git", "show", f"HEAD:{rel}"], cwd=repo_root, capture_output=True, check=True
        ).stdout
        if worktree != hashlib.sha256(blob).hexdigest():
            mismatched.append(rel)

    assert not mismatched, (
        "the working tree and the git object store disagree for: "
        f"{mismatched}. A fingerprint taken from either would then depend on which OS "
        "computed it (PROCESS.md §6a)."
    )


# -- secrets ----------------------------------------------------------------------------


def test_no_env_file_is_tracked_and_the_example_holds_names_only(repo_root):
    results = _results(check_roles.check_secrets(repo_root))
    assert results["B1 no .env tracked"].ok is True, results["B1 no .env tracked"].detail
    assert results["B2 .env.example exists"].ok is True, results["B2 .env.example exists"].detail
    assert results["B3 .env.example holds NAMES only"].ok is True, (
        results["B3 .env.example holds NAMES only"].detail
    )


def test_no_secret_shaped_string_in_any_tracked_file(repo_root):
    results = _results(check_roles.check_secrets(repo_root))
    result = results["C1 no secret-shaped string in any tracked file"]
    assert result.ok is True, result.detail


def test_the_secret_scanner_actually_fires(tmp_path):
    """`ai-playbook` B.9 again: a scanner that has never fired is only decorative.

    Every pattern requires a **payload**, never a bare prefix — this repository's own
    prose says ``rzp_live_`` as a word, and a scanner that fired on the word would be
    disabled on its first run.
    """
    import re

    planted = {
        "Groq API key": "gsk_" + "a" * 40,
        "Google API key": "AIza" + "B" * 35,
        "Razorpay LIVE key": "rzp_live_" + "c" * 14,
        "GitHub token": "ghp_" + "d" * 36,
        "AWS access key id": "AKIA" + "E" * 16,
    }
    patterns = dict(check_roles.SECRET_PATTERNS)
    for label, sample in planted.items():
        assert re.search(patterns[label], sample), f"{label} pattern failed to match a real shape"

    for benign in ("rzp_live_", "the AIza prefix", "gsk_", "a GitHub gho_ token"):
        for _label, pattern in check_roles.SECRET_PATTERNS:
            assert not re.search(pattern, benign), (
                f"pattern {pattern!r} fired on benign prose {benign!r} — a scanner that "
                f"cries wolf on its own documentation gets switched off"
            )


# -- the moat ---------------------------------------------------------------------------


def test_gates_and_scorer_share_no_first_party_module(repo_root):
    """⚠️ THE ONE LINE THAT IS THE WHOLE MOAT (`CLAUDE.md` hard rule 8).

    In the spike, ``gate.js`` and ``invariants.js`` both called ``world.js:intentKey``, so
    **the invariant could not have fired unless the gate had a bug. That is not a result;
    it is a definition.** Anything the two need is written twice, on purpose — once
    against the live call, once against the replayed ledger.

    Today neither directory exists (``scorer/`` is C8, ``gates/`` is C9), so this reports
    ``n/a``. ``n/a`` is asserted as ``n/a`` — never quietly as a pass.

    ⚠️ **THE MOAT IS AST *PLUS* SOURCE TEXT SINCE 2026-09-02 — `OF-110`, `INCIDENTS.md`
    INC-51.** D1–D3 walk the module graph and **cannot see a call expression by
    construction**; measured in a fresh temp clone, a ``gates/`` module reaching a
    ``scorer/`` predicate by ``importlib.import_module``, by ``__import__`` or by
    ``getattr`` on the package root made **all three report PASS**. **D4** must therefore be
    present in this group, whatever its verdict — an absent check and a passing one are not
    the same thing to a caller (`INC-07`), and D4's absence is the state the moat was in
    while it was evadable.
    """
    results = check_roles.check_gate_scorer_isolation(repo_root)
    for result in results:
        assert result.ok is not False, result.detail

    checks = {result.check[:2] for result in results}
    assert "D4" in checks, (
        "D4 — the source-text half of the moat — is not being reported. OF-110 measured "
        "that three dynamic-import shapes escape the AST walk BY CONSTRUCTION, and INC-51 "
        "measured D1, D2 and D3 all reporting PASS over a gates/ module that really did "
        f"execute a scorer/ predicate. Group reported: {sorted(checks)}"
    )

    if all(result.ok is None for result in results):
        pytest.skip(
            "gates/ and scorer/ do not exist yet (C9 and C8). Both candidate layouts were "
            "checked — see QUESTIONS.md Q-004 for the unresolved CONTEXT.md §16 ambiguity. "
            "D1 and D4 are both reported as n/a rather than omitted."
        )


# -- session identity -------------------------------------------------------------------


def test_no_commit_carries_a_forged_or_reused_session_token(repo_root):
    """`PROCESS.md` §7a. The control is an honour system **with an artefact**.

    It does not prove the sessions were different — nothing can, and this repository says
    so in the README rather than implying enforcement it does not have. What it does is
    make reuse **visible** and the claim falsifiable by anyone reading the log.

    Note what is asserted and what is not: a commit with **no** trailer is reported, not
    failed (C0's prompt issued no token and this session refused to invent one — see
    QUESTIONS.md Q-001). A commit with a **forged** token — one that appears in no
    `QUESTIONS.md` row — fails.
    """
    results = _results(check_roles.check_session_tokens(repo_root))
    assert results["E1 no commit carries an UNISSUED token"].ok is True, (
        results["E1 no commit carries an UNISSUED token"].detail
    )
    assert results["E2 no token shared by a chunk's BUILD and REVIEW"].ok is True
    assert results["E3 no token reused across roles"].ok is True


# -- config completeness ----------------------------------------------------------------


def test_undetermined_config_values_are_declared_not_defaulted(repo_root):
    results = _results(check_roles.check_config_sentinels(repo_root))
    assert results["F1 config/ loads"].ok is True, results["F1 config/ loads"].detail
    assert results["F2 undetermined values are DECLARED, not defaulted"].ok is True


# -- the entry points --------------------------------------------------------------------


def test_check_roles_exits_zero(repo_root):
    """``make check-roles`` must run, and must not be failing today."""
    assert check_roles.run(repo_root) == 0


def test_the_makefile_contains_no_logic(repo_root):
    """`CONTEXT.md` §16: *"The Makefile contains no build logic."*

    A reviewer with no ``make`` — on any OS — must get a byte-identical result from
    ``python -m whetstone_gate.tasks <target>``. Logic here is logic they cannot run,
    which silently breaks §20's reproducibility box.
    """
    lines = (repo_root / "Makefile").read_text(encoding="utf-8").splitlines()
    recipes = [line for line in lines if line.startswith("\t")]

    assert recipes, "the Makefile has no recipes at all"
    for recipe in recipes:
        assert "whetstone_gate.tasks" in recipe, (
            f"recipe is not a delegation: {recipe!r}. Put the logic in "
            f"src/whetstone_gate/tasks.py instead."
        )
        # One command, no shell chaining, no conditionals.
        for forbidden in ("&&", "||", ";", "if ", "for ", "|"):
            assert forbidden not in recipe, (
                f"recipe {recipe!r} contains {forbidden!r} — that is logic, and it belongs "
                f"in tasks.py where a reviewer without make can run it"
            )


def test_every_declared_make_target_exists_in_both_entry_points(repo_root):
    """The five targets C0 owes, wired in both places, or the README's two forms diverge."""
    from whetstone_gate import tasks

    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    for target in ("test", "eval", "selftest", "check-prereg", "check-roles"):
        assert f"\n{target}:" in makefile, f"Makefile has no `{target}` target"
        assert target in tasks.TARGETS, f"tasks.py does not dispatch `{target}`"
        assert target in tasks._DISPATCH


def test_python_is_312(repo_root):
    """⚠️ 3.12 is REQUIRED, not preferred.

    ``tau2-bench`` at the pinned SHA declares ``requires-python = ">=3.12,<3.14"`` in its
    own ``pyproject.toml``, and `CONTEXT.md` §21.4 forbids ever dropping τ²-bench. 3.11
    makes the project's spine uninstallable.
    """
    import sys

    assert sys.version_info[:2] == (3, 12), (
        f"running on {sys.version_info.major}.{sys.version_info.minor}; the pinned "
        f"tau2-bench requires >=3.12,<3.14"
    )


# =======================================================================================
# OF-99 / Q-064 / Q-074 — THE SUPERSEDED-STRING TRIPWIRE.
#
# ⚠️ `Q-064`'s NAMED REMEDY HAS NEVER EXISTED, AND THE SAME DEFECT GOT THROUGH TWICE.
# Both `Q-064` and `Q-074` say the same sentence — *"A grep for the superseded string, run
# as a test, would have caught all four in one line."* `OF-99` then searched first-hand and
# found nothing: this file already carries repository-wide scans for CRLF, secret-shaped
# strings, forged session tokens, the gates/scorer module graph, undetermined config values
# and hardcoded spec values — **and nothing for a citation.**
#
# The hard part is not the grep. `OF-99` measured **66 hits** for the superseded citation
# and exactly **one** was live text; a tripwire that cannot tell a **live claim** from a
# **recorded one** fires 65 times on its first run and is disabled by its second. So the
# discrimination is explicit and has two parts, both of them reviewable:
#
#   1. **PATH.** Append-only history — `docs/sessions/`, `docs/reviews/`, and the journals —
#      records what was said. A superseded citation there is the record working correctly.
#   2. **QUOTATION.** A line that QUOTES the superseded claim in order to say it is wrong is
#      not making it. That is `Q-080`'s own logic, three days later and in a second file:
#      *a quotation of X is not X.* `src/whetstone_gate/camel_comparator/branch_b.py:39` —
#      *So a Branch-B artefact that says "cite Tables 5-7, banking column" would point a
#      panelist at a table stating the opposite* — is the case that forced it.
#
# ⚠️ AND THE PATTERN MATCHES THE **CLAIM**, NOT THE STRING. The defect `Q-058` ruled on is
# not the words *Tables 5-7*; it is *citing* them for the CaMeL/native banking pair. Live
# text must stay free to name them — `CONTEXT.md` §8.5.1's own ⚠️ NOT-Tables-5-7 clause
# depends on it — so the pattern requires a citing verb immediately in front.
# =======================================================================================


@dataclasses.dataclass(frozen=True)
class SupersededString:
    """One superseded claim, with everything a reader needs to judge a hit."""

    label: str
    #: The superseded CLAIM as a regex — a citing verb, then the superseded citation.
    superseded: str
    #: What live text must say instead.
    replacement: str
    #: The ruling that superseded it. A hit is a violation *of this ruling*, and the message
    #: says so, because "wrong" without a ruling is an opinion.
    ruling: str
    #: Paths where it may legitimately still appear: append-only history.
    history_paths: tuple[str, ...]


#: ⚠️ **THE LIST. ONE ENTRY TODAY, AND THE SHAPE IS THE POINT** — a second superseded string
#: is four lines, not a new test. Adding one is ordinary work; **removing one, or widening a
#: `history_paths` tuple, is where this check would die quietly** and is a Class A deviation.
SUPERSEDED_STRINGS: tuple[SupersededString, ...] = (
    SupersededString(
        label="the pre-v1.8 CaMeL table citation",
        # Built by concatenation so THIS FILE does not carry the live phrase and trip its
        # own scan — the same self-exclusion problem `TRIPWIRE_SELF_EXCLUSION` solves by
        # naming a file, solved here without an exemption list, which is strictly better:
        # an exemption list is the natural place for a check to die.
        superseded=(
            r"(?:cit" + r"ation of|cit" + r"e[sd]?|cit" + r"ing|ships? as|shipping as)"
            r"\s+(?:a\s+)?(?:CaMeL's\s+published\s+)?\**Tab" + r"les? 5[-–—]7"
        ),
        replacement=(
            "Table 2, Appendix B ('Full results tables'), the `o3 High` block, `banking` "
            "column of arXiv 2503.18813v2 — CaMeL 81.2% +/- 19.1 against Native Tool "
            "Calling API 62.5% +/- 23.7. Tables 5-7 are Appendix C, `Claude 3.5 Sonnet`, "
            "where CaMeL is BEHIND on banking; Table 7 remains CONTEXT.md 8.5.2's P2 "
            "citation."
        ),
        ruling="Q-058 (Class A, RULED 2026-09-01); carried to five sites by Q-064 and Q-074",
        history_paths=(
            "docs/sessions/",
            "docs/reviews/",
            "QUESTIONS.md",
            "PROGRESS.md",
            "STATUS.md",
            "INCIDENTS.md",
        ),
    ),
)

#: Quotation marks that mark a line as *reporting* the superseded claim rather than making
#: it. Deliberately three characters and no cleverness: if a future entry needs more, the
#: entry says so rather than this constant growing invisibly.
_QUOTE_CHARACTERS = "\"'`"


def _is_quoted(line: str, start: int, end: int) -> bool:
    """Is the span ``line[start:end]`` enclosed in quotation marks **on its own line**?

    ⚠️ `Q-080`'s logic, applied to a citation instead of a trailer: *a quotation of X is not
    X*. A line that reproduces the superseded claim in order to say it is wrong — which is
    what `branch_b.py` and the C13 tests do throughout — is the check working, not failing.
    """
    return any(q in line[:start] for q in _QUOTE_CHARACTERS) and any(
        q in line[end:] for q in _QUOTE_CHARACTERS
    )


def superseded_string_hits(files: dict[str, str]) -> list[tuple[str, str, int, str]]:
    """Every LIVE occurrence of a superseded claim in ``{path: text}``.

    Returns ``(entry label, path, line number, the line)``. A hit under an entry's
    ``history_paths``, or quoted on its own line, is **recorded** rather than live and is
    not returned — which is the whole difference between a tripwire and a nuisance.
    """
    hits: list[tuple[str, str, int, str]] = []
    for entry in SUPERSEDED_STRINGS:
        pattern = re.compile(entry.superseded, re.IGNORECASE)
        for path, text in files.items():
            posix = path.replace("\\", "/")
            if any(
                posix == where or posix.startswith(where) for where in entry.history_paths
            ):
                continue
            for number, line in enumerate(text.splitlines(), start=1):
                match = pattern.search(line)
                if match and not _is_quoted(line, match.start(), match.end()):
                    hits.append((entry.label, posix, number, line.strip()))
    return hits


def _tracked_text(repo_root) -> dict[str, str]:
    """Every tracked file this scan can read, as ``{path: text}``. Binaries are skipped."""
    listing = subprocess.run(
        ["git", "ls-files"], cwd=repo_root, check=True, capture_output=True, text=True
    ).stdout
    files: dict[str, str] = {}
    for path in filter(None, listing.splitlines()):
        candidate = repo_root / path
        try:
            files[path] = candidate.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
    return files


def test_no_superseded_string_survives_in_live_text(repo_root):
    """⚠️ **`Q-064`'s REMEDY, WHICH HAS NEVER EXISTED AND LET THE SAME DEFECT THROUGH TWICE.**

    `Q-058` ruled that citing Tables 5-7 for the CaMeL/native banking pair *"would point a
    panelist at a table stating the opposite of the claim it is offered to support, in a
    submission whose thesis is that other people's numbers are unsound."* Four sites were
    corrected under `Q-064`. A **fifth** — `tests/test_lanes_operator_placeholders.py` —
    survived, because it was outside every fence that met it (`Q-074`), and it is the copy
    a human actually reads: it is printed in full in every ``make selftest`` failure.

    **Nothing in this repository knew a citation had copies.** This is that mechanism.
    """
    hits = superseded_string_hits(_tracked_text(repo_root))
    assert not hits, "\n".join(
        [f"{len(hits)} LIVE occurrence(s) of a superseded claim:"]
        + [f"  {path}:{number}\n      {line}" for _, path, number, line in hits]
        + [
            f"\nSuperseded by {entry.ruling}.\nIt must now say: {entry.replacement}"
            for entry in SUPERSEDED_STRINGS
        ]
    )


def test_the_superseded_string_tripwire_fires_on_a_planted_live_occurrence():
    """⚠️ **FIRED, IN BOTH DIRECTIONS.** A tripwire nobody has seen go red is decoration.

    The planted text is `Q-074`'s site **as it stood before this session corrected it** —
    the real defect, not an invented one — and it is assembled from fragments so this file
    never carries the live phrase and cannot trip its own scan.
    """
    live = (
        "    the comparator\n"
        "    ships as a cit" + "ation of Tab" + "les 5-7 of arXiv 2503.18813v2 with the\n"
        "    `CONTEXT.md` S8.5.1 reason verbatim.\n"
    )
    hits = superseded_string_hits({"tests/some_live_test.py": live})
    assert len(hits) == 1, f"the tripwire did not fire on the real pre-fix text: {hits}"
    assert hits[0][2] == 2, f"it must name the LINE, or it is not actionable: {hits}"


def test_the_tripwire_does_not_fire_on_the_append_only_history_or_on_a_quotation():
    """⚠️ **THE HALF THAT DECIDES WHETHER THIS CHECK SURVIVES A WEEK.**

    `OF-99` measured **66 hits, of which exactly one was live text.** A tripwire that cannot
    tell a live claim from a recorded one fires 65 times on its first run and is switched
    off on its second — `Q-009`'s own argument, turned on this check. Both discriminators
    are fired here at text that MUST NOT trip them:

      1. the identical live sentence, sitting in `docs/sessions/` — append-only history;
      2. the identical claim, **quoted** inside a passage saying it is wrong, which is
         `branch_b.py:39` and is `Q-080`'s logic in a second file.
    """
    live = "ships as a cit" + "ation of Tab" + "les 5-7 of arXiv 2503.18813v2\n"

    for where in ("docs/sessions/c13-fix-1.txt", "docs/reviews/REVIEW_13_2.md",
                  "QUESTIONS.md", "PROGRESS.md", "STATUS.md", "INCIDENTS.md"):
        assert superseded_string_hits({where: live}) == [], (
            f"the tripwire fired on {where}, which is append-only history. It records what "
            f"was said; a superseded citation there is the record working correctly."
        )

    quoted = (
        'So a Branch-B artefact that says *"cit' + "e Tab" + 'les 5-7, banking column"* '
        "would point a panelist at a table stating the opposite.\n"
    )
    assert superseded_string_hits({"src/whetstone_gate/camel_comparator/branch_b.py": quoted}) == [], (
        "the tripwire fired on a QUOTATION of the superseded claim inside a passage "
        "explaining why it is wrong — branch_b.py:39's real text. A quotation of X is not X "
        "(Q-080's own logic), and firing here would make the check unusable in exactly the "
        "module that documents the ruling."
    )


def test_the_tripwire_would_have_caught_q074s_site_and_that_site_is_now_correct(repo_root):
    """⚠️ **`Q-074`, CLOSED — and the closure is checked against the mechanism, not asserted.**

    Two halves, and the second is the one `Q-074` is really about:

      1. the docstring at `tests/test_lanes_operator_placeholders.py` **as it stood** trips
         the tripwire — so 1c would have caught 1d; and
      2. the file **as it stands now** does not, and carries the four fields `Q-058`'s
         ruling requires of every published third-party figure: table number, appendix,
         base model and row.
    """
    before = (
        "    ships as a cit" + "ation of Tab" + "les 5-7 of arXiv 2503.18813v2 with the "
        "`CONTEXT.md` S8.5.1\n"
    )
    assert superseded_string_hits({"tests/test_lanes_operator_placeholders.py": before}), (
        "the tripwire does not fire on Q-074's site as it stood — then it would not have "
        "caught the defect it exists for, and 1c proves nothing about 1d"
    )

    now = (repo_root / "tests" / "test_lanes_operator_placeholders.py").read_text(
        encoding="utf-8"
    )
    assert superseded_string_hits({"tests/test_lanes_operator_placeholders.py": now}) == [], (
        "Q-074's fifth site still carries the superseded citation"
    )
    for field in ("Table 2", "Appendix B", "o3 High", "banking"):
        assert field in now, (
            f"Q-058's ruling requires every published third-party figure to carry the table "
            f"number, its appendix, its base model and its row. {field!r} is missing."
        )
    assert "Table 7" in now, (
        "Q-058's ruling RETAINS Tables 5-7 where they are right: Table 7 is CONTEXT.md "
        "8.5.2's P2 citation and C13 verified it exactly. Dropping it would over-correct."
    )


# -- ⚠️ THE PACKAGE UNDER TEST IS THE TREE UNDER TEST (OF-139, INC-17) -----------------


def _tree_under_test() -> Path:
    """The repository **this test file** belongs to.

    ``<tree>/tests/test_repo_invariants.py`` → up two parents. This is the one anchor that
    cannot lie: the file being executed *is* the tree being exercised, by definition. Every
    other candidate — the working directory, ``config.repo_root()``, the imported package —
    is exactly what this check exists to doubt.
    """
    return Path(__file__).resolve().parents[1]


def _same_path(a: Path, b: Path) -> bool:
    """Case-insensitive on Windows, exact elsewhere. Both sides are already resolved."""
    return os.path.normcase(str(a)) == os.path.normcase(str(b))


def test_the_package_under_test_is_the_tree_under_test(pytestconfig):
    """⚠️ A mutation run inside a clone measures the LIVE repository unless told not to.

    ``.venv/Lib/site-packages/__editable__.whetstone_gate-0.1.0.pth`` holds one line — the
    **real** repository's ``src`` — and :func:`whetstone_gate.config.repo_root` is
    ``Path(__file__).resolve().parents[2]``, so it follows the package wherever the package
    resolves. A bare ``python -m pytest`` inside a fresh clone therefore imports the real
    tree's package **and** resolves the real tree's root. C13 REVIEW 4 measured exactly that
    in its own first clone, before it recorded any result::

        PKG : C:/Users/chinm/whetstone-gate/src/whetstone_gate/__init__.py
        ROOT: C:/Users/chinm/whetstone-gate

    **Every mutation to ``src/``, ``config/`` or ``CONTEXT.md`` inside that clone would have
    had no effect, and the control would still have read green — so every mutant would have
    been reported as SURVIVED.** It is `INCIDENTS.md` **INC-17** inverted, and it reaches
    every review that has run mutants in a clone. `INC-17` named a guard of this shape as
    **OWED** and left it unbuilt; this is it, and `docs/reviews/OPEN_FINDINGS.md` **OF-139**
    is the finding that re-raised it.

    ⚠️ **THE REMEDY, WRITTEN WHERE THE NEXT MUTATION SESSION WILL HIT IT.**

      1. **Point the interpreter at the tree you are actually testing.** POSIX shell::

             PYTHONPATH=<clone>/src python -m pytest <clone>/tests/<file>

         PowerShell::

             $env:PYTHONPATH = "<clone>/src"; python -m pytest <clone>/tests/<file>

         Forward slashes are accepted by Python on Windows. ``vendor/`` is reached by
         junction in a clone; create it before the first run, not after the first red.

      2. **PRINT the resolved paths at the head of EVERY mutation run** — the package's
         ``__file__``, ``config.repo_root()`` and the tree the suite is running from — into
         the run's own committed output. A transcript that *shows* which tree was loaded is
         evidence; a harness that *asserts* it is a claim. This is `INC-17`'s own procedure.

      3. **A run whose POST-RESTORE CONTROL is not green is VOID and is not scored.**
         Restore each mutant by **WRITING BACK THE ORIGINAL BYTES** captured before the
         mutation, re-hash to confirm, and re-run the full control before the next mutant.

      4. ⚠️ **AND THE OTHER FAILURE DIRECTION, WHICH IS FLATTERING IN THE OPPOSITE WAY.**
         C6 REVIEW 4's harness restored with ``git checkout --`` from a HEAD that **already
         held the mutation**, so every restore re-applied its predecessor and **every mutant
         was reported KILLED**. Both defects produce a clean-looking transcript: this one
         reports 0 killed, that one reports 100%. Neither is measuring anything. **Re-baseline
         before measuring** — capture the bytes, write them back, prove the control green.

    What this test asserts is only the first of the four, because it is the only one a test
    can see: the package under test, the repo root it resolves, and pytest's own rootdir all
    name the tree this file lives in. Fired in **both** directions before it was committed —
    RED in a clone with no ``PYTHONPATH``, GREEN in the real repository.
    """
    tree = _tree_under_test()
    package = Path(whetstone_gate.__file__).resolve()
    root = cfg.repo_root().resolve()
    rootdir = Path(pytestconfig.rootpath).resolve()

    observed = (
        f"\n    TREE    (this test file's own repository) : {tree}"
        f"\n    PKG     (whetstone_gate.__file__)         : {package}"
        f"\n    ROOT    (config.repo_root())              : {root}"
        f"\n    ROOTDIR (pytest)                          : {rootdir}"
    )
    remedy = (
        "\n\n  REMEDY: run with PYTHONPATH=<tree>/src so the interpreter imports the tree "
        "you are\n  testing, and print these four paths at the head of the run. See this "
        "test's docstring,\n  INCIDENTS.md INC-17 and its OF-139 entry."
    )

    assert _same_path(package, tree / "src" / "whetstone_gate" / "__init__.py"), (
        "⚠️ THE PACKAGE UNDER TEST IS NOT THE TREE UNDER TEST. `import whetstone_gate` "
        "resolved OUTSIDE the repository this test file belongs to, so every edit to `src/` "
        "in this tree — a mutant included — is invisible to this run." + observed + remedy
    )
    assert _same_path(root, tree), (
        "⚠️ `config.repo_root()` DOES NOT NAME THE TREE UNDER TEST, so every read of "
        "`config/`, `CONTEXT.md` and every other repository artefact is coming from a "
        "different repository than the one whose tests are running." + observed + remedy
    )
    assert _same_path(rootdir, tree), (
        "⚠️ pytest's rootdir is not the tree this test file belongs to. The suite and the "
        "file disagree about which repository is under test." + observed + remedy
    )


# -- D4's scan set: the CLOSURE, not the two directories (OF-249) -----------------------
#
# ⚠️ **THE LINE `CLAUDE.md` HARD RULE 8 CALLS "THE WHOLE MOAT", AND UNTIL 2026-09-03 ITS TWO
# HALVES SCANNED DIFFERENT SETS.** `D1`–`D3` walk the **transitive closure** of both
# packages; `D4` — the source-text half added for `OF-110` / `INC-51`, precisely because the
# AST walk cannot see a call expression — walked the two package **directories**. Any
# first-party module inside a closure but outside both directories was therefore scanned by
# **nothing**, and `OF-249` measured that there was exactly one: `whetstone_gate.config`, on
# the **gate** side, reached by `gates/shell.py`.
#
# ⚠️ **THAT IS `INC-51`'S MEASURED CLASS, ONE MODULE FURTHER OUT** — and this session
# planted the hop in a throwaway clone and watched the pre-fix `D4` print **PASS** over a
# live `gates/` → `scorer/` reach that really returned `DENY` computed by
# `scorer/invariants.py`. `INCIDENTS.md` **INC-132**.


def _closure_of(root: Path) -> tuple[set[str], set[str], dict[str, Path]]:
    """The two closures and the module index, computed with `check_roles`' OWN walker.

    Re-implementing the walk here would prove something about a second implementation.
    """
    src_root = root / "src"
    package_roots = {"whetstone_gate", "gates", "scorer"} | {
        p.name for p in src_root.iterdir() if p.is_dir()
    }
    known = check_roles._first_party_modules(src_root)
    graph = {
        module: check_roles._resolve_imports(py, module, known, package_roots)
        for module, py in known.items()
    }

    def under(prefix: str) -> set[str]:
        return {m for m in known if m == prefix or m.startswith(prefix + ".")}

    gates = check_roles._transitive_closure(under("whetstone_gate.gates"), graph)
    scorer = check_roles._transitive_closure(under("whetstone_gate.scorer"), graph)
    return gates, scorer, known


def test_d4_text_scans_every_module_in_either_closure_not_just_the_two_directories(
    repo_root,
):
    """⚠️ `OF-249`. The two halves of the moat must scan the SAME SET or they do not compose.

    `D4` exists to cover a blind spot `D1`–`D3` have **by construction**. A `D4` whose scan
    set is *smaller* than the set `D1`–`D3` walk cannot do that job on the difference, and
    the difference is not hypothetical: it is `whetstone_gate.config`, inside the gate side
    of the moat, imported by `gates/shell.py`.

    This test measures the difference with `check_roles`' own walker and asserts every
    module in it is **named in `D4`'s own printed detail** — so the day a sixth module joins
    the closure, this assertion sees it whether or not it carries a hop.
    """
    gate_closure, scorer_closure, known = _closure_of(repo_root)
    gates_dir = repo_root / "src" / "whetstone_gate" / "gates"
    scorer_dir = repo_root / "src" / "whetstone_gate" / "scorer"
    in_a_directory = {
        py.resolve() for package in (gates_dir, scorer_dir) for py in package.rglob("*.py")
    }
    outside = sorted(
        module
        for module in gate_closure | scorer_closure
        if module in known and known[module].resolve() not in in_a_directory
    )

    results = _results(check_roles.check_gate_scorer_isolation(repo_root))
    d4 = results["D4 no dynamic import in gates/ or scorer/"]
    if d4.ok is None:
        pytest.skip("gates/ and scorer/ do not both exist in this tree")

    assert d4.ok is True, d4.detail
    for module in outside:
        assert module in d4.detail, (
            f"{module} is inside a package's TRANSITIVE CLOSURE and outside both package "
            f"DIRECTORIES, and D4's detail does not name it as scanned. That is OF-249: "
            f"D1-D3 would walk it and D4 would not, so a dynamic hop placed there passes "
            f"all four over a live gates->scorer reach (INC-51's class, one module further "
            f"out). D4 said: {d4.detail}"
        )


def _closure_hop_tree(tmp_path: Path, shim_body: str) -> Path:
    """A throwaway tree whose `gates/` reaches a module OUTSIDE both package directories.

    ⚠️ **NOTHING IS PLANTED IN THIS REPOSITORY** (`INCIDENTS.md` `INC-11`, `INC-17`). The
    shape is `OF-249`'s exactly: `gates/arm4_kernel.py` names **no refused form at all**, so
    a directory-only scan of `gates/` and `scorer/` reads clean; the reach lives one module
    out, in `whetstone_gate.settings_shim`, which is in the gate closure and in neither
    directory.
    """
    root = tmp_path / "tree"
    pkg = root / "src" / "whetstone_gate"
    for sub in ("gates", "scorer"):
        (pkg / sub).mkdir(parents=True, exist_ok=True)
        (pkg / sub / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "settings_shim.py").write_text(shim_body, encoding="utf-8")
    (pkg / "gates" / "arm4_kernel.py").write_text(
        "from whetstone_gate import settings_shim\n"
        "def decide(paise, cap):\n"
        "    return settings_shim.reach(paise, cap)\n",
        encoding="utf-8",
    )
    (pkg / "scorer" / "replay.py").write_text(
        "def over_cap(paise, cap):\n    return paise > cap\n", encoding="utf-8"
    )
    return root


_CLEAN_SHIM = "def reach(paise, cap):\n    return paise > cap\n"
_HOP_SHIM = (
    "import importlib\n"
    "def reach(paise, cap):\n"
    '    module = importlib.import_module("whetstone_gate.scorer.replay")\n'
    "    return module.over_cap(paise, cap)\n"
)


def test_d4_goes_RED_on_a_dynamic_hop_one_module_OUTSIDE_both_directories(tmp_path):
    """⚠️ `PROCESS.md` §5.4: a gate that has never gone red is only decorative. This is it.

    Three assertions, and the middle one is the finding:

      * **`D1`, `D2` and `D3` still PASS** — a call expression is not an `ast.Import` node,
        so the module graph cannot see this reach, exactly as `INC-51` measured.
      * **the DIRECTORY-ONLY scan still returns NOTHING** — `check_roles._dynamic_reach_hits`
        pointed at the two package directories, which is what `D4` used to be, reads the
        planted tree **clean**. That is `OF-249`, measured rather than argued.
      * **`D4` now FAILS and names the module** — the closure half sees what the directory
        half cannot.
    """
    root = _closure_hop_tree(tmp_path, _HOP_SHIM)
    results = _results(check_roles.check_gate_scorer_isolation(root))

    assert results["D1 gates/ imports nothing from scorer/"].ok is True, (
        "D1 caught a dynamic reach - if that is now true, INC-51's measurement has changed "
        "and D4's justification must be re-read, not deleted"
    )
    assert results["D3 no shared first-party module"].ok is True, "see the note on D1"

    directory_only = check_roles._dynamic_reach_hits(
        {
            "src/whetstone_gate/gates": root / "src/whetstone_gate/gates",
            "src/whetstone_gate/scorer": root / "src/whetstone_gate/scorer",
        }
    )
    assert directory_only == [], (
        "the pre-OF-249 D4 - a scan of the two package DIRECTORIES - was supposed to read "
        f"this planted tree CLEAN, and it did not: {directory_only}. If that is now false "
        "the premise of this test has changed and OF-249 must be re-measured, not deleted."
    )

    d4 = results["D4 no dynamic import in gates/ or scorer/"]
    assert d4.ok is False, (
        f"D4 did NOT refuse a dynamic gates->scorer hop placed one module outside both "
        f"package directories. That is OF-249, reopened: {d4.detail}"
    )
    assert "whetstone_gate.settings_shim" in d4.detail, (
        f"D4 must NAME the closure module it refused: {d4.detail}"
    )


def test_d4_does_not_fire_on_the_same_tree_with_a_CLEAN_module_outside_both_directories(
    tmp_path,
):
    """The negative control. A widened scan that refuses everything is not a check.

    Same tree, same `gates/` → `settings_shim` → `scorer/` topology, shim written without a
    refused form: all four must PASS. Without this, `test_d4_goes_RED_...` above would be
    satisfied by a `D4` that had simply been broken.
    """
    root = _closure_hop_tree(tmp_path, _CLEAN_SHIM)
    results = check_roles.check_gate_scorer_isolation(root)
    assert {r.check.split()[0] for r in results} == {"D1", "D2", "D3", "D4"}
    for result in results:
        assert result.ok is True, f"{result.check}: {result.detail}"
