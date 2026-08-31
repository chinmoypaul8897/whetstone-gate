"""KEPT PROBES added by the C0 ADVERSARIAL RE-REVIEW, attempt 2 (SESSION-TOKEN ``f57e216b``).

**Probes, not fixes.** A review session fixes nothing (`CLAUDE.md` §1); it may add kept tests.
Each probe below fires a check — or the repository itself — at input built to break it, and
each states which finding in `docs/reviews/REVIEW_C0_2.md` it belongs to.

⚠️ **None of these closes its finding.** ``make check-roles`` is what C0's done-when names, and
these live in ``make test``. They make the condition *detectable*; wiring it into a check is a
fix session's, exactly as `REVIEW_C0.md` F3 did for OF-01 before `4a34c04` turned it into A5.

Idiom follows `tests/test_c0_review_probes.py` and `tests/test_repo_invariants.py`: a throwaway
git repository under ``tmp_path`` wherever a fixture is needed, never the repository under
review.
"""

from __future__ import annotations

import re
import subprocess as sp

import pytest

from whetstone_gate import check_roles


def _init(path, gitattributes: bytes | None = b"* text=auto eol=lf\n"):
    path.mkdir(parents=True, exist_ok=True)
    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "fixture@example.invalid"],
        ["git", "config", "user.name", "fixture"],
        ["git", "config", "core.autocrlf", "false"],
    ):
        sp.run(cmd, cwd=path, check=True, capture_output=True)
    if gitattributes is not None:
        (path / ".gitattributes").write_bytes(gitattributes)
    return path


def _commit(path, message="fixture"):
    sp.run(["git", "add", "-A"], cwd=path, check=True, capture_output=True)
    sp.run(["git", "commit", "-qm", message], cwd=path, check=True, capture_output=True)


# =======================================================================================
# F-19 — E's OWN DENOMINATOR. A row of `## Session tokens` that `_TOKEN_ROW` cannot read is
# dropped in silence, and E prints no reconciliation, while A3, A4 and A5 all print one.
#
# Q-014 (i) settled the same question one level down: a trailer that is PRESENT but
# MALFORMED must not be counted as ABSENT, because *"judging fails open and rules fail
# closed"* (`CONTEXT.md` §14). E5 is that ruling, applied to the COMMIT side of E's input.
# The TABLE side of E's input got no such treatment, and a malformed ROW still reads as an
# absent one — which blinds E2 and E3 to the exact violation `PROCESS.md` §7a names.
#
# MEASURED, 2026-08-31: with `deadbeef` recorded as C0 BUILD and, on the next line, as C0
# `review` (lower case — the regex is case-sensitive), E2 and E3 both report **clean**.
# Four spellings were tried; all four were missed. The full table is in REVIEW_C0_2.md F-19.
# =======================================================================================

#: The ONE row of `## Session tokens` that `_TOKEN_ROW` is not expected to parse: the token
#: issued to the CTX-13.4 session was ``WG-2026-08-30-CTX-13.4-A``, which is not 8 hex, and
#: **Q-014 (iv) forbids reshaping it** — *"rewriting it into a conforming 8-hex value would
#: manufacture the evidence the check exists to test."* It is the row-side twin of the four
#: SHAs in ``check_roles.E5_EXCEPTIONS``, and it is pinned here at exactly one for the same
#: reason: an exception list is where a check dies quietly.
_UNPARSEABLE_ROW_TOKENS = ("WG-2026-08-30-CTX-13.4-A",)


def _token_table_rows(questions_text: str) -> list[str]:
    """The data rows of `QUESTIONS.md`'s ``## Session tokens`` table, as written."""
    after_heading = questions_text.split("## Session tokens", 1)[1]
    after_header = after_heading.split("| Token | Chunk | Role | Issued |", 1)[1]
    rows: list[str] = []
    started = False
    for line in after_header.splitlines():
        if not line.strip():
            if started:
                break
            continue
        started = True
        if set(line) <= set("|- "):  # the |---|---| separator
            continue
        rows.append(line.strip())
    return rows


def test_every_row_of_the_session_tokens_table_parses_except_the_one_named_exception(repo_root):
    """⚠️ **F-19.** A row the parser cannot read vanishes, and nothing says so.

    E1 prints *"18 issued row(s) covering 18 token(s) parsed from QUESTIONS.md"*. It does not
    print how many rows the table actually holds, so the two numbers cannot be reconciled by
    a reader — and `CLAUDE.md` hard rule 11 is about exactly that: *"no silent denominator
    shrinkage."* A3, A4 and A5 each reconcile their denominator out loud; E does not.

    This probe supplies the missing reconciliation as an assertion. It goes red the moment a
    nineteenth row is written in a spelling ``_TOKEN_ROW`` cannot read — which is the input
    under which **E2 and E3 go blind to the violation §7a names**.
    """
    text = (repo_root / "QUESTIONS.md").read_text(encoding="utf-8")
    rows = _token_table_rows(text)
    assert len(rows) >= 19, (
        f"the ## Session tokens table parsed to {len(rows)} rows, fewer than the 19 it held "
        f"on 2026-08-31. A parser that silently reads nothing is the defect it checks for."
    )

    parsed = {token.lower() for token, _, _ in check_roles._TOKEN_ROW.findall(text)}
    unparsed = [
        row
        for row in rows
        if (m := re.match(r"^\|\s*`?([^|`]+?)`?\s*\|", row)) and m.group(1).lower() not in parsed
    ]

    assert len(unparsed) == len(_UNPARSEABLE_ROW_TOKENS), (
        f"{len(unparsed)} row(s) of ## Session tokens are dropped by _TOKEN_ROW without a "
        f"word being printed about it, and a dropped row is one E2 and E3 cannot see: "
        f"{unparsed}. Exactly {len(_UNPARSEABLE_ROW_TOKENS)} is expected — the CTX-13.4 row "
        f"Q-014 (iv) forbids reshaping. Anything else is a row that silently is not checked."
    )
    for row, expected in zip(unparsed, _UNPARSEABLE_ROW_TOKENS):
        assert expected in row, (
            f"the unparseable row is no longer the one Q-014 (iv) names. Expected a row "
            f"carrying {expected!r}; found {row!r}."
        )


def test_the_issued_token_table_is_read_from_the_whole_file_not_from_the_table(tmp_path):
    """⚠️ **F-20.** ``_issued_tokens`` scans **all of `QUESTIONS.md`**, not the table.

    `PROCESS.md` §7a makes the ``## Session tokens`` table the record. ``_issued_tokens``
    applies ``_TOKEN_ROW`` to the whole file, so **any** line at column 0 shaped like a row
    is read as an issue — including a proposed row quoted inside a question's body. Q-021's
    body carries such a line today (``| \\`da356dbb\\` | C3 | BUILD | 2026-08-31 |``); it is
    invisible to the parser only because it happens to be indented by two spaces.

    That is a false-negative path for **E1**, the one clause of §7a that attempt 1 found
    working: a token that was never issued becomes issued by being written about.

    ⚠️ This probe asserts the CURRENT behaviour, deliberately, so it is a **detector and not
    a lock**: it names the defect in its failure message, and a fix session that scopes the
    parse to the table will make it fail and will find the reason written here. It is the
    same shape as ``test_a5_states_the_NUL_in_prose_gap_it_cannot_close``.
    """
    questions = tmp_path / "QUESTIONS.md"
    questions.write_text(
        "## Session tokens\n\n"
        "| Token | Chunk | Role | Issued |\n"
        "|---|---|---|---|\n"
        "| `aaaaaaaa` | C0 | BUILD | 2026-08-31 |\n"
        "\n"
        "## Q-99 — a question whose BODY quotes a proposed row\n\n"
        "The remedy would be one row:\n\n"
        "| `facefeed` | C7 | REVIEW | 2026-09-01 |\n",
        encoding="utf-8",
    )
    issued = check_roles._issued_tokens(questions)

    assert "aaaaaaaa" in issued, "the real table row was not read at all"
    assert "facefeed" in issued, (
        "GOOD NEWS, AND THIS PROBE MUST NOW BE UPDATED: `_issued_tokens` no longer treats a "
        "row-shaped line in a question's BODY as an issued token. That is F-20's remedy. "
        "Scope the parse to the ## Session tokens section, delete this assertion, and record "
        "the closure against OPEN_FINDINGS.md F-20 with its SHA."
    )


# =======================================================================================
# F-21 — A5's DECLARED GAP: a NUL inside a prose document is invisible to BOTH branches.
#
# VERIFIED, not taken on trust (REVIEW_C0_2.md §2): a markdown file containing one NUL is
# classified `-text` by git at any size, so branch T never sees it and branch B *accepts* it
# as the very signal it looks for. A3 PASS, A4 PASS, A5 PASS, over a file with an eaten
# sentence — INC-10's `Missing` field, still open.
#
# A5's own output says closing it "needs a judgement about which paths are prose, which is a
# second copy of a decision this check deliberately takes from git." That reason does not
# survive: the set of tracked files git calls BINARY is, today, exactly two dashboard PNGs,
# and PINNING that set closes the gap with no judgement about prose and no second copy of
# git's heuristic. It is the same instrument as TRIPWIRE_SELF_EXCLUSION (pinned at 1),
# NULL_IS_A_VALUE (pinned at 2) and E5_EXCEPTIONS (pinned at 4).
# =======================================================================================

#: Every tracked path this repository expects git to classify as BINARY (``w/-text``).
#: Growing it is a deliberate act a review will see, which is the entire point.
_EXPECTED_BINARY_PATHS = frozenset(
    {
        "docs/evidence/limits/gemini-2026-08-30.png",
        "docs/evidence/limits/groq-2026-08-30.png",
    }
)


def test_no_tracked_file_is_binary_outside_the_named_screenshot_set(repo_root):
    """⚠️ **F-21.** The gap A5 prints and does not close, closed for ``make test``.

    A5 branch B asks *"does every binary-classified file carry a NUL?"*. A prose document
    with a NUL answers **yes** and is waved through. This asks the stricter question that
    needs no judgement about prose: *"is every binary-classified file one of the files this
    repository knows to be binary?"* A lone CR (OF-01), a NUL in prose (INC-10's `Missing`),
    and any other content git demotes to ``-text`` all fail it.

    Not a second copy of git's text/binary heuristic: the verdict is taken **from git**
    (``git ls-files --eol``, the ``w/`` side) and compared against an explicit, pinned list —
    the opposite of `CLAUDE.md` hard rule 8's circularity, and the same reasoning
    `REVIEW_C0.md` F3 used to answer the objection that kept OF-01 out of `check_roles`.
    """
    classification = check_roles._eol_classification(repo_root)
    binary = {rel for rel, kind in classification.items() if kind == "-text"}

    unexpected = sorted(binary - _EXPECTED_BINARY_PATHS)
    assert not unexpected, (
        f"git classifies {len(unexpected)} tracked file(s) as BINARY that this repository "
        f"does not know to be binary: {unexpected}. Either a real binary was added (extend "
        f"_EXPECTED_BINARY_PATHS, deliberately, and a review will see it) or textual content "
        f"has been demoted to `-text` by a stray CR or an embedded NUL — in which case A3 "
        f"does not scan it, A4 cannot fail on it, and A5 branch B accepts it. "
        f"OPEN_FINDINGS.md OF-01 and INCIDENTS.md INC-10."
    )

    missing = sorted(_EXPECTED_BINARY_PATHS - binary)
    assert not missing, (
        f"these paths are pinned as binary but git no longer classifies them so: {missing}. "
        f"Either they were removed or their content changed; both need a deliberate edit here."
    )


@pytest.mark.parametrize(
    "payload, what",
    [
        (b"A sentence that has\x00 eaten something.\n", "a NUL inside prose"),
        (b"line one\rline two\nline three\n", "OF-01's lone CR"),
    ],
)
def test_the_binary_set_pin_catches_what_A5_branch_B_lets_through(tmp_path, payload, what):
    """The pin above, fired at the two shapes that reach ``-text`` without being binary.

    ⚠️ **The NUL case is the one A5 cannot see**, and it is asserted here that A5 **passes**
    on it — so this probe is standing over a real, measured gap rather than over a hypothesis.
    The lone-CR case is A5 branch B's own, and is asserted to still fail there, so the two
    checks are not confused with each other.
    """
    repo = _init(tmp_path / "r")
    (repo / "prose.md").write_bytes(payload)
    _commit(repo)

    classification = check_roles._eol_classification(repo)
    assert classification.get("prose.md") == "-text", (
        f"the fixture is not exercising the binary branch at all; git says "
        f"{classification.get('prose.md')!r} for {what}"
    )

    a5 = next(r for r in check_roles.check_gitattributes(repo) if r.check.startswith("A5"))
    if b"\x00" in payload:
        assert a5.ok is True, (
            "A5 has learned to see a NUL inside prose. That is F-21's remedy and this "
            "assertion must be updated: record the closure in OPEN_FINDINGS.md with its SHA."
        )
    else:
        assert a5.ok is False, "A5 branch B no longer fires on OF-01's lone CR"

    # The pin sees BOTH, because it does not ask what the bytes are — only whether this file
    # is one the repository knows to be binary.
    assert {rel for rel, kind in classification.items() if kind == "-text"} - frozenset(
        {"whatever/the/real/binaries/are"}
    ), "the fixture produced no binary-classified file, so the pin is not being exercised"
    assert "prose.md" in {rel for rel, kind in classification.items() if kind == "-text"}
