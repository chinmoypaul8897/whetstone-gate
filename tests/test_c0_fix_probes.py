"""KEPT PROBES added by the C0 **FIX** session (``SESSION-TOKEN: c9521aac``).

`REVIEW_C0_1` failed C0 with four BLOCKERs of one shape — *a check that reports PASS over
nothing* — and named the cause in its own **F-05**:

    only THREE tests in the whole suite build a fixture intended to make a check FAIL,
    and all three came from INC-09's CRLF work.

So every fix in this session ships with a probe that **fails on the old code and passes on
the new**, which is `CLAUDE.md` hard rule 6's *"provably meaningful"* bar applied in the one
direction that matters here. A probe that only asserts the check still passes would be one
more of exactly what the review found.

Idiom follows ``tests/test_repo_invariants.py`` and ``tests/test_c0_review_probes.py``: a
throwaway git repository under ``tmp_path``, or a throwaway ``config/`` directory reached
through ``WHETSTONE_CONFIG_DIR`` — **never** the repository or the ``config/`` under review.
``tests/goldens/`` is read-only to a build session and nothing here touches it.
"""

from __future__ import annotations

import subprocess as sp

import pytest

from whetstone_gate import check_roles
from whetstone_gate import config as cfg


def _results(group):
    return {r.check: r for r in group}


def _init(path):
    path.mkdir(parents=True, exist_ok=True)
    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "fixture@example.invalid"],
        ["git", "config", "user.name", "fixture"],
        ["git", "config", "core.autocrlf", "false"],
    ):
        sp.run(cmd, cwd=path, check=True, capture_output=True)
    (path / ".gitattributes").write_bytes(b"* text=auto eol=lf\n")
    return path


def _commit(path, message="fixture"):
    sp.run(["git", "add", "-A"], cwd=path, check=True, capture_output=True)
    sp.run(["git", "commit", "-qm", message], cwd=path, check=True, capture_output=True)


def _questions(rows: str) -> str:
    return (
        "## Session tokens\n\n"
        "| Token | Chunk | Role | Issued |\n"
        "|---|---|---|---|\n" + rows
    )


# =======================================================================================
# B-01 — E2 and E3 were STRUCTURALLY UNABLE TO FAIL
#
# `issued[token] = (chunk, role)` is keyed by TOKEN, so a token in two rows kept only the
# last and every token landed in exactly one bucket: E3's count was always 1 and E2's
# BUILD∩REVIEW was always empty. Both probes below PASS (i.e. the check stays green, i.e.
# they FAIL as probes) against the pre-fix parse — that is the point of them.
# REVIEW_C0.md B-01 · ARCHITECT_CHECK_0.md §3 · INCIDENTS.md INC-14.
# =======================================================================================


def test_e2_fires_when_one_token_is_a_chunks_BUILD_and_its_REVIEW(tmp_path):
    """`PROCESS.md` §7a, clause 1: *"any chunk's build and review commits share a token."*

    `CLAUDE.md` §1: **build and review are never the same session.** This is the condition
    that makes that sentence checkable, and it could not fire.
    """
    repo = _init(tmp_path / "r")
    (repo / "QUESTIONS.md").write_text(
        _questions(
            "| `deadbeef` | C0 | BUILD  | 2026-08-30 |\n"
            "| `deadbeef` | C0 | REVIEW | 2026-08-30 |\n"
        ),
        encoding="utf-8",
    )
    _commit(repo)

    results = _results(check_roles.check_session_tokens(repo))
    e2 = results["E2 no token shared by a chunk's BUILD and REVIEW"]
    assert e2.ok is False, (
        "E2 reported clean over the exact condition PROCESS.md §7a says check-roles fails "
        f"on: one token issued as both C0 BUILD and C0 REVIEW. detail: {e2.detail}"
    )
    assert "C0" in e2.detail


def test_e3_fires_when_one_token_appears_under_two_different_roles(tmp_path):
    """`PROCESS.md` §7a, clause 3: *"a token is reused across roles."*"""
    repo = _init(tmp_path / "r")
    (repo / "QUESTIONS.md").write_text(
        _questions(
            "| `cafebabe` | C1 | BUILD | 2026-08-30 |\n"
            "| `cafebabe` | C2 | FIX   | 2026-08-30 |\n"
        ),
        encoding="utf-8",
    )
    _commit(repo)

    e3 = _results(check_roles.check_session_tokens(repo))["E3 no token reused across roles"]
    assert e3.ok is False, (
        f"E3 reported clean over a token issued under two different roles: {e3.detail}"
    )
    assert "cafebabe" in e3.detail


def test_the_issued_parse_keeps_every_row_not_only_the_last(tmp_path):
    """The mechanism itself, asserted directly rather than only through E2 and E3.

    ``issued[token] = (chunk, role)`` silently discarded every row but the last for a
    duplicated token. Asserting on the parse means a future rewrite that reintroduces a
    dict-of-tuples fails here with an intelligible message, not only two checks away.
    """
    repo = _init(tmp_path / "r")
    (repo / "QUESTIONS.md").write_text(
        _questions(
            "| `deadbeef` | C0 | BUILD  | 2026-08-30 |\n"
            "| `deadbeef` | C0 | REVIEW | 2026-08-30 |\n"
            "| `deadbeef` | C0 | BUILD  | 2026-08-30 |\n"   # a byte-identical repeat
        ),
        encoding="utf-8",
    )
    issued = check_roles._issued_tokens(repo / "QUESTIONS.md")
    assert issued == {"deadbeef": {("C0", "BUILD"), ("C0", "REVIEW")}}, (
        "one token must hold MANY (chunk, role) pairs, and a byte-identical repeated row "
        f"must collapse rather than count as reuse. got: {issued}"
    )


def test_a_chunk_cell_of_ARCH_parses_and_leaves_E1_clean(tmp_path):
    """Q-014 (iii): ``_TOKEN_ROW``'s chunk group is ``(C\\d+|ARCH)`` and nothing else.

    A session that is not a numbered chunk — a spec correction, an architect-artefact
    landing — could not have a parseable row at all, so **E1 FAILED on that session's own
    commits** and the honest cell had to be falsified to `C0` to keep the check green.
    `QUESTIONS.md`'s own preamble records that trade being made.

    ⚠️ **THE TOKEN GROUP IS NOT TOUCHED**, and the second half of this probe says so: a
    non-hex token in an `ARCH` row is still unparseable, so the widening cannot be used to
    smuggle a token past E1's format.
    """
    repo = _init(tmp_path / "r")
    (repo / "QUESTIONS.md").write_text(
        _questions(
            "| `abcd1234` | ARCH | BUILD | 2026-08-31 |\n"
            "| `WG-2026-08-30-X` | ARCH | BUILD | 2026-08-30 |\n"
        ),
        encoding="utf-8",
    )
    _commit(repo, "fixture")
    (repo / "note.md").write_text("second\n", encoding="utf-8")
    sp.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    sp.run(
        ["git", "commit", "-qm", "arch work\n\nSession-Token: abcd1234"],
        cwd=repo, check=True, capture_output=True,
    )

    issued = check_roles._issued_tokens(repo / "QUESTIONS.md")
    assert issued == {"abcd1234": {("ARCH", "BUILD")}}, (
        "an ARCH chunk cell must parse, and a non-8-hex TOKEN cell must still not: "
        f"{issued}"
    )
    e1 = _results(check_roles.check_session_tokens(repo))["E1 no commit carries an UNISSUED token"]
    assert e1.ok is True, (
        f"E1 failed on a commit whose ARCH row it should have parsed: {e1.detail}"
    )


# =======================================================================================
# Q-014 (i) / (ii) / (iv) — E5, and the four-SHA exception list
# =======================================================================================


def test_e5_fires_on_a_malformed_trailer_that_is_not_on_the_exception_list(tmp_path):
    """A trailer that is PRESENT but MALFORMED must FAIL, not be read as absent.

    `CONTEXT.md` §14 closes on Prabu Ram's formula, quoted with its source: *"judging fails
    open and rules fail closed."* This is a rule. Before Q-014 (i) it failed open **and
    printed a false statement** — naming four commits that do carry a trailer among
    *"commit(s) carry no trailer"*, and offering Q-001's cause, which is a different
    session's different cause.
    """
    repo = _init(tmp_path / "r")
    (repo / "QUESTIONS.md").write_text(
        _questions("| `abcd1234` | C0 | BUILD | 2026-08-31 |\n"), encoding="utf-8"
    )
    _commit(repo)
    (repo / "note.md").write_text("second\n", encoding="utf-8")
    sp.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    sp.run(
        ["git", "commit", "-qm", "malformed\n\nSession-Token: WG-2026-09-01-SOMETHING"],
        cwd=repo, check=True, capture_output=True,
    )
    malformed_sha = sp.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()

    results = _results(check_roles.check_session_tokens(repo))
    e5 = results["E5 malformed Session-Token trailer"]
    assert e5.ok is False, (
        f"E5 passed over a trailer no matcher in this project can read: {e5.detail}"
    )
    assert "WG-2026-09-01-SOMETHING" in e5.detail, (
        f"E5 must NAME the value it could not parse, or it is not actionable: {e5.detail}"
    )
    assert malformed_sha[:7] in e5.detail, f"E5 must name the SHA: {e5.detail}"

    # And the other half of Q-014 (ii): the commit that DOES carry a trailer must not be
    # named among those that carry none. (The root commit here genuinely carries none, so
    # E4 is correctly non-empty — what must not appear in it is `malformed_sha`.)
    e4 = results["E4 every commit carries a Session-Token trailer"]
    assert malformed_sha[:7] not in e4.detail, (
        "E4 named a commit that DOES carry a trailer among those that carry none — that is "
        f"the false statement Q-014 (ii) names. detail: {e4.detail}"
    )


def test_e4_no_longer_counts_a_malformed_trailer_as_an_absent_one(tmp_path):
    """Q-014 (ii), asserted on the count rather than on the prose.

    Two commits, one with **no** trailer and one with a **malformed** one. ``untrailered``
    must name exactly the first. Before the fix it named both, which is how four commits
    that do carry a trailer ended up in a list that says they do not.
    """
    repo = _init(tmp_path / "r")
    (repo / "QUESTIONS.md").write_text(_questions(""), encoding="utf-8")
    _commit(repo, "root with NO trailer")
    (repo / "a.md").write_text("a\n", encoding="utf-8")
    sp.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    sp.run(
        ["git", "commit", "-qm", "malformed\n\nSession-Token: not-eight-hex"],
        cwd=repo, check=True, capture_output=True,
    )

    e4 = _results(check_roles.check_session_tokens(repo))[
        "E4 every commit carries a Session-Token trailer"
    ]
    assert "1 commit(s) carry no trailer" in e4.detail, (
        "exactly ONE of the two fixture commits carries no trailer; the other carries a "
        f"malformed one and belongs to E5. detail: {e4.detail}"
    )


def test_the_e5_exception_list_is_exactly_the_four_ctx_13_4_commits():
    """⚠️ An exception list is where a check dies quietly. This one is pinned.

    Same pattern, and the same reason, as ``TRIPWIRE_SELF_EXCLUSION`` being pinned at one
    file: widening it must require editing an assertion a review will see. Q-014 (iv)
    records `WG-2026-08-30-CTX-13.4-A` as a **one-off** and forbids reshaping it, so the
    list is finite by construction and may never grow into an amnesty.
    """
    assert len(check_roles.E5_EXCEPTIONS) == 4, (
        f"the E5 exception list holds {len(check_roles.E5_EXCEPTIONS)} entries, not 4. "
        f"Adding one is an architect ruling in QUESTIONS.md, not a code change."
    )
    assert set(check_roles.E5_EXCEPTIONS) == {
        "966324740c4d9de40e407a356bcf24d3d76af65d",
        "6d08cf3ff75189db5e9f49fdc6f59a20466b26d4",
        "d67550e46282af4f513810c1cc812ed91dfeac90",
        "ec3064dc74c999dec0bc5277e1ca96705b907547",
    }
    for sha, reason in check_roles.E5_EXCEPTIONS.items():
        assert len(sha) == 40, f"{sha} is not a full SHA; an abbreviation can collide"
        assert "Q-014" in reason, f"{sha[:7]}'s exception states no ruling: {reason!r}"


def test_the_permissive_trailer_matcher_does_not_widen_the_strict_one():
    """The two matchers must stay distinct, or Q-014's format protection dissolves.

    ``_TOKEN_TRAILER`` is the authority for *"well formed"* and there is deliberately no
    second copy of the 8-hex predicate anywhere in this module to drift away from it.
    """
    body = "subject\n\nSession-Token: {}\n"
    assert check_roles._TOKEN_TRAILER.findall(body.format("deadbeef")) == ["deadbeef"]
    assert check_roles._TOKEN_TRAILER.findall(body.format("WG-2026-08-30-CTX-13.4-A")) == []
    assert check_roles._TOKEN_TRAILER_ANY.findall(body.format("deadbeef")) == ["deadbeef"]
    assert check_roles._TOKEN_TRAILER_ANY.findall(
        body.format("WG-2026-08-30-CTX-13.4-A")
    ) == ["WG-2026-08-30-CTX-13.4-A"]
