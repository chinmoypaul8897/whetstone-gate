"""The repository's structural invariants, as unit tests.

``make check-roles`` runs the same checks as a script with human-readable output; this
file runs them under pytest so that ``make test`` cannot go green while one is broken.
Same code, two entry points — not two implementations.
"""

from __future__ import annotations

import subprocess

import pytest

from whetstone_gate import check_roles


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

    results = _results(check_roles.check_gitattributes(tmp_path))
    a3 = results["A3 no CRLF in any tracked file"]

    assert a3.ok is False, (
        "A3 passed on a text file that genuinely carries CRLF — the assertion has been "
        f"gutted, which is hard rule 6's forbidden move. detail: {a3.detail}"
    )
    assert "text_with_crlf.md" in a3.detail, (
        f"A3 no longer names the real CRLF offender. detail: {a3.detail}"
    )
    assert "binary_with_crlf.bin" not in a3.detail, (
        "A3 still reports a binary file's payload bytes as a line-ending defect — this is "
        f"INC-09 unfixed. detail: {a3.detail}"
    )

    # And A4 — the assertion that REPLACED the proxy — catches the real defect on the text
    # file (git would rewrite it on checkin) and leaves the binary file alone.
    a4 = results["A4 working tree and object store hold identical bytes"]
    assert a4.ok is False, (
        f"A4 passed on a file git would rewrite on checkin. detail: {a4.detail}"
    )
    assert "text_with_crlf.md" in a4.detail, f"A4 does not name the offender: {a4.detail}"
    assert "binary_with_crlf.bin" not in a4.detail, (
        f"A4 claims git rewrites a binary file, which it does not: {a4.detail}"
    )


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
    """
    results = check_roles.check_gate_scorer_isolation(repo_root)
    for result in results:
        assert result.ok is not False, result.detail

    if len(results) == 1 and results[0].ok is None:
        pytest.skip(
            "gates/ and scorer/ do not exist yet (C9 and C8). Both candidate layouts were "
            "checked — see QUESTIONS.md Q-004 for the unresolved CONTEXT.md §16 ambiguity."
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
