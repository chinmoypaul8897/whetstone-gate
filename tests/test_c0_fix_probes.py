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


# =======================================================================================
# B-02 — THE MOAT. `check_roles.py`'s own docstring calls D "the whole moat", and three of
# the four attack forms the review built walked straight through it.
#
# ⚠️ Q-004 ruled OPTION 1: the layout is src/whetstone_gate/{gates,scorer}/. Every fixture
# below is built there, which is also the layout in which the defect is worst — under it
# the package root is the COMMONEST import string in the project, and the old code
# subtracted the package root away.
# REVIEW_C0.md B-02 · Q-015's ruling · INCIDENTS.md INC-14.
# =======================================================================================


def _moat_tree(tmp_path, gates_src: str, scorer_src: str, extra: dict[str, str] | None = None):
    """A throwaway ``src/whetstone_gate/{gates,scorer}/`` tree, in Q-004's ruled layout."""
    root = tmp_path / "tree"
    pkg = root / "src" / "whetstone_gate"
    for sub in ("gates", "scorer"):
        (pkg / sub).mkdir(parents=True, exist_ok=True)
        (pkg / sub / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "gates" / "arm4_kernel.py").write_text(gates_src, encoding="utf-8")
    (pkg / "scorer" / "replay.py").write_text(scorer_src, encoding="utf-8")
    for rel, source in (extra or {}).items():
        target = pkg / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
    return root


_SHARED_PREDICATE = "def intent_key(action):\n    return (action['tool'], action['payment_id'])\n"


@pytest.mark.parametrize(
    "form, gates_src, scorer_src, extra",
    [
        (
            "1 — both import the module directly (the ONE form the old code caught)",
            "from whetstone_gate.shared_predicate import intent_key\n",
            "from whetstone_gate.shared_predicate import intent_key\n",
            {"shared_predicate.py": _SHARED_PREDICATE},
        ),
        (
            "2 — both import it THROUGH the package root (the spike defect, in Python)",
            "from whetstone_gate import shared_predicate\n\nk = shared_predicate.intent_key\n",
            "from whetstone_gate import shared_predicate\n\nk = shared_predicate.intent_key\n",
            {"shared_predicate.py": _SHARED_PREDICATE},
        ),
        (
            "3 — a RELATIVE import crossing the moat",
            "from .. import scorer\n",
            "x = 1\n",
            {},
        ),
        (
            "4 — ONE HOP: each side imports its own helper, both helpers import the predicate",
            "from whetstone_gate.gate_helper import prepare\n",
            "from whetstone_gate.scorer_helper import prepare\n",
            {
                "shared_predicate.py": _SHARED_PREDICATE,
                "gate_helper.py": "from whetstone_gate.shared_predicate import intent_key\n"
                "\n\ndef prepare(a):\n    return intent_key(a)\n",
                "scorer_helper.py": "from whetstone_gate.shared_predicate import intent_key\n"
                "\n\ndef prepare(a):\n    return intent_key(a)\n",
            },
        ),
    ],
)
def test_d3_fires_on_every_one_of_b02s_four_attack_forms(
    tmp_path, form, gates_src, scorer_src, extra
):
    """⚠️ **THE ONE LINE THAT IS THE WHOLE MOAT** (`CLAUDE.md` hard rule 8).

    Forms **2, 3 and 4 all PASSED** before this fix. Each has its own cause and Q-015's
    ruling names all three:

      * form 2 — ``from whetstone_gate import X`` recorded the bare package root for both
        sides, and ``shared = … - {"whetstone_gate"}`` then discarded it. That subtraction
        was an unruled one-entry allow-list holding a **package**, which hard rule 8 permits
        only for *"pure value types … that carry no predicate logic"*.
      * form 3 — ``module.lstrip(".").split(".")[0]`` is ``""`` for ``from .. import
        scorer``, so an import crossing the moat was **not recorded at all**.
      * form 4 — the walk was **one hop deep** where hard rule 8 says **transitive**.

    Form 1 is included deliberately: it is the one form that already worked, so a fix that
    broke it would be caught here rather than at C8.
    """
    root = _moat_tree(tmp_path, gates_src, scorer_src, extra)
    results = _results(check_roles.check_gate_scorer_isolation(root))
    d3 = results["D3 no shared first-party module"]
    d1 = results["D1 gates/ imports nothing from scorer/"]

    if form.startswith("3"):
        assert d1.ok is False, (
            f"D1 passed over `from .. import scorer` — a relative import straight across the "
            f"moat. detail: {d1.detail}"
        )
    assert d3.ok is False, (
        f"D3 passed on attack form {form}. That is hard rule 8's own named spike defect "
        f"reaching the repository through the check written to stop it. detail: {d3.detail}"
    )
    assert "written TWICE" in d3.detail, (
        "D3's failure must say WHAT to do about it — write it twice, on purpose — or the "
        f"next reader's cheapest move is the allow-list. detail: {d3.detail}"
    )


def test_d3_stays_clean_when_the_two_sides_genuinely_share_nothing(tmp_path):
    """The other half of a usable check: it must not cry wolf.

    Each side imports its **own** helper and the helpers share nothing. A check that fired
    here would be switched off inside a day, and then form 2 would ship.
    """
    root = _moat_tree(
        tmp_path,
        "from whetstone_gate.gate_helper import prepare\n",
        "from whetstone_gate.scorer_helper import prepare\n",
        {
            "gate_helper.py": "def prepare(a):\n    return a\n",
            "scorer_helper.py": "def prepare(a):\n    return a\n",
        },
    )
    results = _results(check_roles.check_gate_scorer_isolation(root))
    for key in (
        "D1 gates/ imports nothing from scorer/",
        "D2 scorer/ imports nothing from gates/",
        "D3 no shared first-party module",
    ):
        assert results[key].ok is True, f"{key} fired on a clean tree: {results[key].detail}"
    assert "TRANSITIVELY" in results["D3 no shared first-party module"].detail


def test_the_moat_allow_list_is_empty(tmp_path):
    """⚠️ Q-015: *"THE ALLOW-LIST … IS CREATED, AND IT IS CREATED EMPTY."*

    None of hard rule 8's three named pure value types exists yet — the harm-record
    dataclass is C4's, the enums and the paise wrapper are C4's and C8's. C4, C8 and C9 will
    each ask for entries; **each ask is a separate ruling and none is ever granted in bulk.**
    Pinning it empty means the first entry cannot arrive as a quiet line in a diff.

    The second half of this probe is the one that matters: an allow-list entry must actually
    be able to make D3 blind, or pinning it proves nothing.
    """
    assert check_roles.MOAT_ALLOW_LIST == frozenset(), (
        f"MOAT_ALLOW_LIST holds {sorted(check_roles.MOAT_ALLOW_LIST)}. Adding an entry is a "
        f"CLASS A DEVIATION (CLAUDE.md hard rule 8) and requires an architect ruling in "
        f"QUESTIONS.md naming that one module. It may not be widened in a code change."
    )
    assert "whetstone_gate" not in check_roles.MOAT_ALLOW_LIST, (
        "the PACKAGE ROOT may never be allow-listed: Q-015 rejected that explicitly, and "
        "under Q-004's ruling it is the commonest import string in the project, so the "
        "entry would make D3 permanently blind."
    )

    root = _moat_tree(
        tmp_path,
        "from whetstone_gate.shared_predicate import intent_key\n",
        "from whetstone_gate.shared_predicate import intent_key\n",
        {"shared_predicate.py": _SHARED_PREDICATE},
    )
    import unittest.mock

    with unittest.mock.patch.object(
        check_roles, "MOAT_ALLOW_LIST", frozenset({"whetstone_gate.shared_predicate"})
    ):
        d3 = _results(check_roles.check_gate_scorer_isolation(root))[
            "D3 no shared first-party module"
        ]
    assert d3.ok is True, (
        "an allow-list entry did not suppress the finding it names, so MOAT_ALLOW_LIST is "
        "decorative and pinning it empty proves nothing."
    )


def test_a_file_the_parser_cannot_read_is_reported_as_a_failure_not_a_pass(tmp_path):
    """*"Could not verify"* is not a pass — the doctrine A4 already applies to a bad path.

    A first-party file the parser chokes on is a file whose imports nobody has seen. The
    moat is the one claim in this repository that may not rest on an unread file, and the
    textual scan this replaced would have silently recorded zero imports for it.
    """
    root = _moat_tree(tmp_path, "x = 1\n", "y = 2\n", {"broken.py": "def f(:\n"})
    results = _results(check_roles.check_gate_scorer_isolation(root))
    d3 = results["D3 no shared first-party module"]
    assert d3.ok is False, f"D3 passed while a first-party file did not parse: {d3.detail}"
    assert "COULD NOT PARSE" in d3.detail and "broken.py" in d3.detail


def test_the_walk_sees_import_forms_a_single_capture_group_missed(tmp_path):
    """`OPEN_FINDINGS.md` **OF-11**, first half: ``import a, b`` recorded only ``a``.

    The regex had one capture group per alternative, so the second name on a comma-separated
    ``import`` line was invisible. Parsing sees every alias. ⚠️ **OF-11's second half —
    ``importlib.import_module(…)`` — is NOT closed by this**: it is a runtime call, not an
    import statement, and no parser of import statements can see it.
    """
    root = _moat_tree(
        tmp_path,
        "import whetstone_gate.other, whetstone_gate.shared_predicate\n",
        "from whetstone_gate.shared_predicate import intent_key\n",
        {"shared_predicate.py": _SHARED_PREDICATE, "other.py": "z = 0\n"},
    )
    d3 = _results(check_roles.check_gate_scorer_isolation(root))[
        "D3 no shared first-party module"
    ]
    assert d3.ok is False, (
        "the SECOND name on an `import a, b` line was invisible, so a shared predicate "
        f"imported that way crossed the moat unrecorded. detail: {d3.detail}"
    )
    assert "whetstone_gate.shared_predicate" in d3.detail
