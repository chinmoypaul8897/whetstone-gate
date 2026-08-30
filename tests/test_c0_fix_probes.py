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


# =======================================================================================
# B-03 — the F group reported `config/` COMPLETE over a `config/` that had lost
# `protocol.yaml`, a PRE-REGISTRATION ARTEFACT, while printing a hardcoded string naming a
# file it never opened. Five sentinels vanished from the count — among them the void
# threshold, which `config.py`'s own docstring calls "the single number that decides whether
# the whole run is publishable" — and check-roles EXITED 0.
# REVIEW_C0.md B-03 · ARCHITECT_CHECK_0.md §3 · INCIDENTS.md INC-14.
# =======================================================================================


def _config_fixture(tmp_path, monkeypatch, files: dict[str, str]):
    """A throwaway ``config/`` reached through ``WHETSTONE_CONFIG_DIR``.

    ⚠️ The repository's own ``config/`` is a **frozen pre-registration artefact** and is
    never edited by a test. The loader honours this variable precisely so that it need not
    be.
    """
    where = tmp_path / "config"
    where.mkdir(parents=True, exist_ok=True)
    for name, body in files.items():
        (where / name).write_text(body, encoding="utf-8")
    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(where))
    return where


_MINIMAL_LANES = (
    "schema_version: 1\n"
    "lanes:\n"
    "  - name: gemma-26b\n"
    "    api_model_id: models/gemma-4-26b-a4b-it\n"
    "camel_comparator:\n"
    "  branch: TODO_C13_RUN1\n"
)
_MINIMAL_PROTOCOL = (
    "schema_version: 1\n"
    "probe:\n"
    "  void_threshold_breach_rate: TODO_C14_CALIBRATION\n"
    "vendor:\n"
    "  agentdojo_sha: TODO_C13_C16\n"
)


def test_a_missing_REQUIRED_config_is_a_refusal_and_F1_fails(tmp_path, monkeypatch):
    """`protocol.yaml` deleted. F1 must FAIL, and the sentinel count must NOT drop quietly.

    `CLAUDE.md` hard rule 9 makes ``config/`` a pre-registration artefact and hard rule 11
    forbids silent denominator shrinkage — *"every dropped episode is counted, categorised
    and printed as a number"* — which applies to a check's own denominator too. The old
    sweep's blanket ``if not path.is_file(): continue`` deliberately bypassed ``load()``'s
    own ``ConfigFileMissing``, so the answer went from six sentinels to one and the report
    said **PASS**.
    """
    _config_fixture(tmp_path, monkeypatch, {"lanes.yaml": _MINIMAL_LANES})

    with pytest.raises(cfg.ConfigFileMissing):
        cfg.outstanding_sentinels()

    results = _results(check_roles.check_config_sentinels(tmp_path))
    f1 = results["F1 config/ loads"]
    assert f1.ok is False, (
        f"F1 reported config/ loading over a config/ with no protocol.yaml: {f1.detail}"
    )
    assert "protocol.yaml" in f1.detail

    f2 = results["F2 undetermined values are DECLARED, not defaulted"]
    assert f2.ok is not True, (
        f"F2 reported a sentinel count over a config/ it could not read: {f2.detail}"
    )
    assert "not evaluated" in f2.detail, (
        "OF-03/INC-07: a check's ABSENCE and a check's PASS must not be the same thing to a "
        f"caller. F2 must say it was not evaluated. detail: {f2.detail}"
    )
    assert len(results) == 4, (
        "the F group must still EMIT all four checks when F1 fails, or the summary line "
        f"silently prints fewer checks than the group owns. got {len(results)}"
    )


def test_F1_reports_what_actually_loaded_rather_than_a_hardcoded_string(tmp_path, monkeypatch):
    """F1's detail was the fixed string *"protocol.yaml and lanes.yaml parse"*.

    It named a file it had never opened, and it said so identically whether that file was
    there or not. A check whose output is a conclusion rather than an observation cannot be
    read as evidence of anything.
    """
    _config_fixture(
        tmp_path,
        monkeypatch,
        {"protocol.yaml": _MINIMAL_PROTOCOL, "lanes.yaml": _MINIMAL_LANES, "ladder.yaml": "a: 1\n"},
    )
    f1 = _results(check_roles.check_config_sentinels(tmp_path))["F1 config/ loads"]
    assert f1.ok is True, f1.detail
    assert "3 file(s) opened and parsed" in f1.detail, (
        f"F1 must report the files it OPENED, and there are three here: {f1.detail}"
    )
    assert "ladder.yaml" in f1.detail


def test_a_not_yet_config_is_reported_as_not_yet_and_never_as_nothing(tmp_path, monkeypatch):
    """`ladder.yaml` is legitimately absent until C15 — and its absence is REPORTED.

    This is the distinction the blanket ``continue`` erased. A not-yet file contributes zero
    sentinels, and *"zero"* must never be readable as *"clean"*: `check_roles.py`'s own
    docstring says ``n/a`` is never silently a pass, and here it is not silent at all.
    """
    _config_fixture(
        tmp_path, monkeypatch, {"protocol.yaml": _MINIMAL_PROTOCOL, "lanes.yaml": _MINIMAL_LANES}
    )
    results = _results(check_roles.check_config_sentinels(tmp_path))
    f4 = results["F4 config files not yet written"]
    assert f4.ok is None, f"a not-yet file must be n/a, never a pass: {f4.detail}"
    assert "ladder.yaml" in f4.detail and "C15" in f4.detail, f4.detail
    assert results["F1 config/ loads"].ok is True


# =======================================================================================
# B-04 — THE PRE-SPEND GATE FLIPPED GREEN WHEN THE KEY IT GUARDS WAS DELETED.
#
# PROCESS.md §8: "A spend-free self-test runs before any token is spent. If the harness is
# broken, it fails for free." `.data.get("camel_comparator", {}).get("branch")` reached
# AROUND the loader with the defaulting accessor config.py's own docstring says "does not
# exist and must not be added", and `is_sentinel(None)` is False — so absence read as
# DECIDED. Both probes below PASSED before the fix.
# REVIEW_C0.md B-04 · ARCHITECT_CHECK_0.md §3 · INCIDENTS.md INC-15.
# =======================================================================================


def test_the_camel_gate_goes_RED_when_the_key_it_guards_is_deleted(tmp_path, monkeypatch):
    """Delete the ``camel_comparator:`` block; the gate must still refuse.

    As shipped: ``1 failed, 1 passed`` — correctly RED. With the block removed it was
    ``2 passed`` — **GREEN**, declaring the CaMeL branch *decided* because the key did not
    exist. Q-009's split is what created this gate, and the gate the split created was
    itself vacuous.
    """
    import test_lanes_operator_placeholders as gate  # noqa: PLC0415  (tests/ is on sys.path)

    lanes_without_camel = "schema_version: 1\nlanes:\n  - name: gemma-26b\n"
    _config_fixture(
        tmp_path,
        monkeypatch,
        {"protocol.yaml": _MINIMAL_PROTOCOL, "lanes.yaml": lanes_without_camel},
    )

    problem = gate.camel_branch_problem()
    assert problem is not None, (
        "the pre-spend gate declared the CaMeL branch DECIDED over a config/lanes.yaml "
        "from which camel_comparator was deleted. Absence is not a decision."
    )
    assert "MissingRequiredValue" in problem, (
        f"the gate must go through require(), so absence is a typed refusal: {problem}"
    )


def test_the_camel_gate_goes_RED_when_lanes_yaml_is_gone_entirely(tmp_path, monkeypatch):
    """And the file-level case: no ``lanes.yaml`` at all is not a decision either."""
    import test_lanes_operator_placeholders as gate  # noqa: PLC0415  (tests/ is on sys.path)

    _config_fixture(tmp_path, monkeypatch, {"protocol.yaml": _MINIMAL_PROTOCOL})
    problem = gate.camel_branch_problem()
    assert problem is not None and "ConfigFileMissing" in problem, (
        f"the gate passed with no config/lanes.yaml on disk at all: {problem}"
    )


def test_the_operator_placeholder_gate_goes_RED_when_lanes_yaml_is_gone(tmp_path, monkeypatch):
    """`REVIEW_C0.md` B-04, second half — and it is the half that guards the money.

    ``test_no_operator_placeholder_remains_in_config`` is the check that stopped a token
    being spent against a guessed model id. With `config/lanes.yaml` removed it **still
    passed**, because ``outstanding_sentinels()`` skipped missing files (B-03's cause). The
    two BLOCKERs meet here: the sweep's silent skip made the spending gate vacuous.
    """
    import test_lanes_operator_placeholders as gate  # noqa: PLC0415  (tests/ is on sys.path)

    _config_fixture(tmp_path, monkeypatch, {"protocol.yaml": _MINIMAL_PROTOCOL})
    problem = gate.operator_placeholder_problem()
    assert problem is not None, (
        "the operator-placeholder gate passed with no config/lanes.yaml on disk. That is "
        "the gate between this project and spending its finite free tier against a guessed "
        "model id, passing over the file it guards."
    )
    assert "CONFIG REFUSAL" in problem, problem


def test_the_operator_placeholder_gate_still_fires_on_a_real_placeholder(tmp_path, monkeypatch):
    """The gate must still do its ORIGINAL job — a fix that only added refusals could hide
    a regression in the thing the gate was built for. Q-006 is why it exists."""
    import test_lanes_operator_placeholders as gate  # noqa: PLC0415  (tests/ is on sys.path)

    _config_fixture(
        tmp_path,
        monkeypatch,
        {
            "protocol.yaml": _MINIMAL_PROTOCOL,
            "lanes.yaml": "schema_version: 1\nlanes:\n  - name: gemma-26b\n"
            "    api_model_id: TODO_OPERATOR\ncamel_comparator:\n  branch: A\n",
        },
    )
    problem = gate.operator_placeholder_problem()
    assert problem is not None and "OPERATOR ACTION REQUIRED" in problem, problem
    assert "lanes[gemma-26b].api_model_id" in problem, problem
    assert gate.camel_branch_problem() is None, (
        "a DECIDED branch must satisfy the gate, or `make selftest` can never go green"
    )


# =======================================================================================
# Q-012's RIDER (REVIEW_C0.md F2, closing paragraph) — A4's honesty sentence, PINNED.
#
#   "A4's honesty depends on that printed sentence. If a later chunk trims the detail
#    strings, A4 silently becomes an assertion over 38 files wearing a label that says 40.
#    Worth a note in the fix session."
#
# A note is not a check. This is the check.
# =======================================================================================


def test_a4_still_says_it_asserts_nothing_on_binary_files(tmp_path):
    """⚠️ A4 is **VACUOUS on binary content**, and the only place that is said is its output.

    The first justification written for INC-09's narrowing — *"a binary file is not skipped
    here; it is checked harder"* — **was false, and it was the load-bearing sentence of the
    hard-rule-6 defence.** On ``-text`` content git applies no conversion, so A4's two
    hashes are equal BY CONSTRUCTION and **A4 cannot fail there.** `b0a4855` withdrew the
    overclaim in the one place a future reader cannot skip: A4's own printed detail.

    So the honesty of this check now rests on a **string**. Trim it and A4 becomes an
    assertion over N text files wearing a label that says N + B. This probe fails if that
    sentence goes, which is the only way a note in a review survives contact with a later
    chunk. See QUESTIONS.md Q-012 and INCIDENTS.md INC-09.
    """
    repo = _init(tmp_path / "r")
    (repo / "note.md").write_bytes(b"plain text\n")
    # A PNG-shaped binary: the NUL is what makes git say `-text`, and the CRLF bytes are
    # payload. It carries a NUL in its first 8000 bytes, so A5 branch B is satisfied too.
    (repo / "shot.png").write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00payload\r\n"
    )
    _commit(repo)

    a4 = _results(check_roles.check_gitattributes(repo))[
        "A4 working tree and object store hold identical bytes"
    ]
    assert a4.ok is True, f"the fixture must be a PASSING A4 for this to test anything: {a4.detail}"
    assert "1 binary file(s) this holds BY CONSTRUCTION" in a4.detail, (
        "A4 no longer says that it asserts NOTHING on binary content. That sentence is the "
        "whole of Q-012's honesty: without it A4 is an assertion over the text files "
        f"wearing a label that counts every tracked file. detail: {a4.detail}"
    )
    assert "asserts nothing" in a4.detail and "cannot fail on" in a4.detail, a4.detail
    # Two text files: `.gitattributes` and `note.md`. One binary: `shot.png`.
    assert "It is a real assertion on the 2 text file(s) only" in a4.detail, (
        "A4 must state the size of the set it REALLY asserts over, not only the size of the "
        f"set it walked. detail: {a4.detail}"
    )


# =======================================================================================
# A5 — ONE CHECK, TWO BRANCHES, on OPPOSITE SIDES OF GIT'S OWN TEXT/BINARY VERDICT.
#
# There was no A5 before this session, so each probe below is fired at a fixture built to
# violate it and would fail against a tree with no A5 at all.
#
# ⚠️ Branch T is NOT a superset of branch B, and the argument that it is must not be
# rebuilt: OF-01's whole point is that a lone CR makes git classify the file BINARY, so a
# control-byte scan over TEXT-classified files SKIPS EXACTLY THE FILE OF-01 IS ABOUT.
# INC-13's byte sits in a file git correctly calls TEXT. Two holes, opposite sides of one
# verdict. Closing one and claiming both is this chunk's own failure mode repeated.
# =======================================================================================

#: A5's check name, written out rather than read from the module, for two reasons: a probe
#: must fail INDIVIDUALLY against a tree with no A5 (a module-level attribute read would
#: break collection and take every other probe in this file with it), and the name itself is
#: worth pinning — `check-roles`' output is what a reviewer reads.
_A5 = "A5 no control byte in text; no NUL-free binary"


def test_a5_branch_T_fires_on_a_control_byte_in_a_text_file(tmp_path):
    """INCIDENTS.md **INC-13**: a literal 0x08 BACKSPACE inside the specification.

    It sat in `CONTEXT.md` §16 from **v1.0** — which is a byte-identical copy of
    `PROJECT_SPEC.md`, whose digest has been verified at source twice, **so the corruption
    predates this repository** — and it was read by three build sessions and one full
    adversarial review. Nothing could see it: a backspace does not survive rendering, so
    every display tool showed a *plausible wrong path* rather than a corrupted one, and A1
    through A4 all pass over it because it is not a CR and it round-trips unchanged.
    """
    assert check_roles.A5_CHECK == _A5, (
        f"A5's check name changed to {check_roles.A5_CHECK!r}. That name is what a reviewer "
        f"reads in `make check-roles` output; renaming it is a reporting change, not a "
        f"refactor."
    )
    repo = _init(tmp_path / "r")
    # The exact shape: a Windows path whose `\b` was eaten as a backspace escape.
    (repo / "spec.md").write_bytes(b"the shim lives at C:" + bytes([92]) + b"MinGW" + bytes([8]) + b"in\n")
    (repo / "clean.md").write_bytes(b"ordinary prose\n")
    _commit(repo)

    results = _results(check_roles.check_gitattributes(repo))
    a5 = results[_A5]
    assert a5.ok is False, (
        f"A5 passed over a text file carrying a 0x08 BACKSPACE — INC-13's byte: {a5.detail}"
    )
    assert "spec.md" in a5.detail and "0x08" in a5.detail, (
        f"A5 must name the FILE and the BYTE, or it is not actionable: {a5.detail}"
    )

    # ⚠️ And the reason A5 had to exist at all: every other A-check is happy with this file.
    assert results["A3 no CRLF in any tracked file"].ok is True
    assert results["A4 working tree and object store hold identical bytes"].ok is True, (
        "A4 passes on a lone control byte because it is not a line ending and git converts "
        "nothing — which is exactly why INC-13 survived four checks for two days."
    )


#: Enough printable prose either side of the offending byte that git's ratio heuristic still
#: calls the file TEXT — i.e. the situation INC-13 actually was: ONE 0x08 in 158 KB of spec.
_PROSE_PAD = b"the quick brown fox jumps over the lazy dog. " * 45


@pytest.mark.parametrize("byte", [0x01, 0x07, 0x08, 0x0B, 0x0C, 0x0E, 0x1B, 0x1F])
def test_a5_branch_T_covers_the_control_range_and_spares_tab_and_lf(tmp_path, byte):
    """The range, asserted rather than assumed — and its exclusions asserted too.

    ⚠️ **The padding is not decoration.** git's text/binary verdict is a ratio, not a
    lookup: MEASURED on 2026-08-31, ``before\\x1bafter\\n`` is classified **binary** while the
    same byte inside a page of prose is classified **text**. Branch T is defined over what
    git calls text, so the fixture must be the shape the defect really takes — one control
    byte in a document, which is exactly INC-13 (one 0x08 in 158 KB of specification).

    TAB and LF are legitimate text and A3 owns CR, so a file made only of those must pass —
    a check that flagged a tab would be switched off on its first run.
    """
    repo = _init(tmp_path / "r")
    (repo / "f.md").write_bytes(_PROSE_PAD + bytes([byte]) + _PROSE_PAD)
    (repo / "tabs.md").write_bytes(b"a\tb\nc\td\n")
    _commit(repo)

    classification = check_roles._eol_classification(repo)
    assert classification.get("f.md") != "-text", (
        f"git classifies the 0x{byte:02X} fixture as BINARY, so it does not exercise branch "
        f"T at all: {classification}"
    )

    a5 = _results(check_roles.check_gitattributes(repo))[_A5]
    assert a5.ok is False, f"A5 passed over byte 0x{byte:02X} in a text file: {a5.detail}"
    assert "f.md" in a5.detail and f"0x{byte:02X}" in a5.detail, a5.detail
    assert "tabs.md" not in a5.detail, (
        "A5 fired on TAB or LF. A check that flags a tab would be switched off on its first "
        f"run, and then the real control byte ships. detail: {a5.detail}"
    )


def test_a5_states_the_NUL_in_prose_gap_it_cannot_close(tmp_path):
    """⚠️ **A KNOWN GAP, ASSERTED SO IT CANNOT BE FORGOTTEN OR OVERCLAIMED.**

    A NUL (``0x00``) makes git classify a file binary **at any size** — measured here, not
    assumed. Branch T therefore never sees it, and branch B *accepts* it, because a NUL is
    the very signal branch B looks for. **So a NUL inside a prose document is invisible to
    both branches of A5.**

    Closing it would need a judgement about which tracked paths are prose, which is a second
    copy of a decision A5 deliberately takes from git — hard rule 8's circularity, and the
    mistake INC-09 already made once. So it is not closed; it is **printed**, in A5's own
    detail, where a future reader cannot skip it. That is the same remedy Q-012 applied to
    A4's vacuity on binary content, for the same reason.
    """
    repo = _init(tmp_path / "r")
    (repo / "prose.md").write_bytes(_PROSE_PAD + bytes([0]) + _PROSE_PAD)
    _commit(repo)

    classification = check_roles._eol_classification(repo)
    assert classification.get("prose.md") == "-text", (
        "git no longer classifies a NUL-bearing prose file as binary. If that is true, this "
        "gap may be closeable and A5's stated limit must be revisited."
    )

    a5 = _results(check_roles.check_gitattributes(repo))[_A5]
    assert a5.ok is True, (
        "A5 unexpectedly caught a NUL in prose. If a later change made it do so, this test "
        "and A5's printed limit must both be updated — do not simply delete the assertion."
    )
    assert "A NUL (0x00) inside a prose document is invisible to BOTH branches" in a5.detail, (
        f"A5 must PRINT the gap it cannot close, or the check overstates its reach: {a5.detail}"
    )


def test_a5_branch_B_fires_on_the_OF01_reproduction(tmp_path):
    """`OPEN_FINDINGS.md` **OF-01**, reproduced exactly as the review wrote it.

        printf 'line one\\rline two\\nline three\\n' > loneCR.md

    git reports ``i/-text w/-text``. The file then lands in the BINARY bucket, where **A3
    does not scan it** and **A4 cannot fail on it** — git converts nothing on ``-text``
    content, so its two hashes are equal by construction. INC-06's and INC-10's defect class
    goes green, and INC-10 was caught only because that CR happened to be followed by LF.

    ⚠️ Branch T cannot catch this, and that is why there are two branches: git calls this
    file BINARY, so a control-byte scan over TEXT-classified files never looks at it.
    """
    repo = _init(tmp_path / "r")
    (repo / "loneCR.md").write_bytes(b"line one" + bytes([13]) + b"line two\nline three\n")
    _commit(repo)

    eol = sp.run(
        ["git", "ls-files", "--eol", "loneCR.md"],
        cwd=repo, check=True, capture_output=True, text=True,
    ).stdout
    assert "w/-text" in eol, (
        f"the fixture is not exercising the binary branch at all; git says: {eol!r}"
    )

    results = _results(check_roles.check_gitattributes(repo))
    a5 = results[_A5]
    assert a5.ok is False, (
        f"A5 passed over OF-01's reproduction — the file both A3 and A4 are blind to: {a5.detail}"
    )
    assert "loneCR.md" in a5.detail, a5.detail

    assert results["A3 no CRLF in any tracked file"].ok is True, (
        "A3 is not supposed to catch this and OF-01 says so — do not re-litigate Q-012."
    )
    assert results["A4 working tree and object store hold identical bytes"].ok is True


def test_a5_branch_B_passes_the_two_dashboard_pngs(repo_root):
    """The false-positive half. Both committed PNGs carry NULs in their IHDR.

    OF-01's discriminator was kept out of `check_roles` on an anti-circularity objection —
    that it would be a second copy of git's text/binary heuristic. It is not: it compares
    **git's own verdict** against an **independent** signal, which is the opposite of hard
    rule 8's circularity. This probe is the evidence that it costs no false positive on the
    only binary files this repository holds.
    """
    classification = check_roles._eol_classification(repo_root)
    pngs = sorted(rel for rel, kind in classification.items() if rel.endswith(".png"))
    assert pngs, "the two dashboard screenshots are not tracked, so this proves nothing"
    for rel in pngs:
        assert classification[rel] == "-text", f"{rel} is not classified binary by git"
        assert 0 in (repo_root / rel).read_bytes()[:8000], (
            f"{rel} carries no NUL in its first 8000 bytes, so A5 branch B would fire on a "
            f"genuine binary file — a false positive, and the fastest way to get a check "
            f"switched off."
        )

    a5 = _results(check_roles.check_gitattributes(repo_root))[_A5]
    assert a5.ok is True, f"A5 fires on this repository as it stands: {a5.detail}"


def test_a5_reconciles_its_denominator_and_states_its_own_limit(repo_root):
    """Hard rule 11 applies to a check's own denominator, and honesty applies to its claim.

    A3 and A4 both print ``<text> + <binary> + <non-regular> = <tracked>``; A5 must too, or
    *"no control byte found"* is unreadable without knowing how many files were looked at.
    And A5's stated limit is load-bearing in the same way A4's is: **it is a control-byte
    check, not a content check**, so an escape resolving to a printable character or a TAB
    is invisible to it and INC-10's `Missing` field stays open. Claiming otherwise would
    close OF-01 and INC-10 on paper.
    """
    a5 = _results(check_roles.check_gitattributes(repo_root))[_A5]
    assert "= " in a5.detail and "tracked" in a5.detail, a5.detail
    assert "text +" in a5.detail and "binary +" in a5.detail and "non-regular" in a5.detail, (
        f"A5 does not reconcile its denominator out loud: {a5.detail}"
    )
    assert "WHAT A5 DOES NOT CATCH" in a5.detail, a5.detail
    assert "PRINTABLE" in a5.detail and "TAB" in a5.detail, a5.detail
    assert "INC-10" in a5.detail and "STAYS OPEN" in a5.detail, (
        "A5 must say that INC-10's Missing field is NOT closed by it. A check that "
        f"overstates its reach is how OF-01 was left open under a green report: {a5.detail}"
    )


def test_a5_fails_rather_than_skips_a_path_it_could_not_read(tmp_path):
    """A tracked path with no regular file behind it is COUNTED, NAMED and FAILED.

    Hard rule 11: *"Every dropped episode is counted, categorised and printed as a number."*
    The same applies to a check's denominator — `b0a4855` established that for A4 and A5
    must not reintroduce the shape A4 was fixed to avoid.
    """
    repo = _init(tmp_path / "r")
    (repo / "kept.md").write_bytes(b"kept\n")
    (repo / "vanished.md").write_bytes(b"gone\n")
    _commit(repo)
    (repo / "vanished.md").unlink()

    a5 = _results(check_roles.check_gitattributes(repo))[_A5]
    assert a5.ok is False, f"A5 passed while one tracked path was checked by nothing: {a5.detail}"
    assert "vanished.md" in a5.detail


# =======================================================================================
# OF-03 — the early return removed A2…A5 from the report with no `n/a` at all
# =======================================================================================


def test_every_A_check_is_still_emitted_when_gitattributes_is_missing(tmp_path):
    """`OPEN_FINDINGS.md` **OF-03**; `INCIDENTS.md` **INC-07**, whose diagnosis this is.

    With `.gitattributes` deleted the function returned **one** result, so A2, A3, A4 (and
    now A5) reported **nothing at all** — weaker than `n/a`, and against this module's own
    docstring: *"Checks that cannot yet apply report `n/a` with the reason, and `n/a` is
    never silently a pass."* The summary line then silently printed four fewer checks than
    the group owns. INC-07 fixed exactly this in `check_secrets`, named this function as the
    surviving instance, and accepted it with *"none — accepted"*. It is not accepted here.

    ⚠️ The second assertion is INC-07's OTHER half: A1 used to be emitted under a DIFFERENT
    check name on the failing branch (*"A1 .gitattributes exists"*) from the passing one
    (*"A1 .gitattributes content"*), so a caller's lookup raised `KeyError` instead of
    reporting a failure. That is INC-07's literal one-line diagnosis, still present here.
    """
    repo = _init(tmp_path / "r")
    (repo / "a.md").write_bytes(b"hello\n")
    _commit(repo)
    (repo / ".gitattributes").unlink()

    results = check_roles.check_gitattributes(repo)
    by_name = _results(results)
    assert len(results) == 5, (
        f"the A group owns five checks and emitted {len(results)}. A check's ABSENCE and a "
        f"check's PASS must not be the same thing to a caller (INC-07)."
    )
    assert by_name["A1 .gitattributes content"].ok is False, (
        "A1 must be emitted under the SAME check name on both branches, or a caller's "
        "lookup raises KeyError instead of reporting a failure — INC-07's own diagnosis."
    )
    for name in (
        "A2 .gitattributes in the FIRST commit",
        "A3 no CRLF in any tracked file",
        "A4 working tree and object store hold identical bytes",
        _A5,
    ):
        assert by_name[name].ok is None, f"{name} must be n/a, not absent and not a pass"
        assert "not evaluated" in by_name[name].detail, by_name[name].detail


# =======================================================================================
# OF-06 — the loader returned YAML null, empty and whitespace-only values SILENTLY
# =======================================================================================


@pytest.mark.parametrize(
    "written, marker",
    [
        ("probe:\n  void_threshold_breach_rate:\n", "BLANK_NULL"),
        ("probe:\n  void_threshold_breach_rate: null\n", "BLANK_NULL"),
        ("probe:\n  void_threshold_breach_rate: ~\n", "BLANK_NULL"),
        ('probe:\n  void_threshold_breach_rate: ""\n', "BLANK_EMPTY_STRING"),
        ('probe:\n  void_threshold_breach_rate: "   "\n', "BLANK_WHITESPACE"),
    ],
)
def test_a_blank_value_is_a_refusal_and_is_counted(tmp_path, monkeypatch, written, marker):
    """`OPEN_FINDINGS.md` **OF-06**, on the exact key `config.py`'s docstring names.

    *"The void threshold is the single number that decides whether the whole run is
    publishable. If a missing threshold silently read as 0.0, every run would pass the void
    check and the project's central control would be inert — and nothing would have
    raised."* A ``TODO_`` sentinel is caught. A key left **blank** was not: ``require()``
    returned ``None``, ``outstanding_sentinels()`` counted nothing, F2 reported *"no
    undetermined values remain"* and `make selftest` passed over it. Found by an independent
    re-implementation written from the spec text alone (`REVIEW_C0.md` §7).
    """
    _config_fixture(tmp_path, monkeypatch, {"protocol.yaml": written, "lanes.yaml": _MINIMAL_LANES})

    with pytest.raises(cfg.BlankValue) as excinfo:
        cfg.load("protocol").require("probe.void_threshold_breach_rate")
    assert "written down and never supplied" in str(excinfo.value)

    swept = dict(
        (path, m) for name, path, m in cfg.outstanding_sentinels() if name == "protocol"
    )
    assert swept.get("probe.void_threshold_breach_rate") == marker, (
        f"the sweep did not COUNT the blank; it reported {swept}"
    )

    f2 = _results(check_roles.check_config_sentinels(tmp_path))[
        "F2 undetermined values are DECLARED, not defaulted"
    ]
    assert f2.ok is False, (
        "F2 reported 'undetermined values are DECLARED' over a value that was written down "
        f"and never supplied. A blank is not a declaration. detail: {f2.detail}"
    )
    assert "BLANK" in f2.detail and "OF-06" in f2.detail, f2.detail


@pytest.mark.parametrize("supplied", ["0", "false", "[]", "0.0"])
def test_zero_false_and_empty_list_are_SUPPLIED_values_and_must_pass(
    tmp_path, monkeypatch, supplied
):
    """⚠️ The classic way hard rule 9 is got wrong, guarded in the same breath.

    A truthiness test would treat ``0``, ``False`` and ``[]`` as missing, and a
    ``per_action_cap_paise: 0`` would then silently become a refusal — a config value the
    author really chose, rejected by the mechanism meant to protect it. The independent
    re-implementation and this loader **agree** on all three, and `REVIEW_C0.md` §7 says so
    explicitly: *"That is correct and I would not change it."* OF-06's fix must not break it.
    """
    _config_fixture(
        tmp_path, monkeypatch, {"protocol.yaml": f"money:\n  per_action_cap_paise: {supplied}\n"}
    )
    value = cfg.load("protocol").require("money.per_action_cap_paise")
    assert value in (0, False, [], 0.0), value
    assert list(cfg.load("protocol").sentinels()) == [], (
        "a supplied falsy value was counted as undetermined"
    )


def test_the_null_is_a_value_exemption_is_exactly_two_entries_and_covers_tpd():
    """⚠️ Pinned, for the same reason ``TRIPWIRE_SELF_EXCLUSION`` is pinned at one file.

    `config/lanes.yaml`'s ``tpd: null`` means *"no such limit exists"* — a documented,
    separately tested fact about Google's free tier, **explicitly excluded from OF-06 by the
    review** — not an omission. The exemption that keeps it out of the blank sweep is the
    natural place for OF-06's fix to be quietly widened until it covers the omission too.
    """
    assert cfg.NULL_IS_A_VALUE == frozenset({("lanes", "tpd"), ("lanes", "reserved_from")}), (
        f"the null exemption holds {sorted(cfg.NULL_IS_A_VALUE)}. Widening it is a decision "
        f"about what counts as a supplied value, and it belongs in a review, not a diff."
    )
    # And the exemption really is doing its job on the file it was written for.
    lanes = cfg.load("lanes")
    tpds = {lane["name"]: lane["tpd"] for lane in lanes.require("lanes")}
    assert None in tpds.values(), "no lane states `tpd: null`, so this proves nothing"
    assert [p for p, _ in lanes.sentinels() if ".tpd" in p] == [], (
        "`tpd: null` is being reported as a blank. It is a documented 'no such limit "
        "exists', and REVIEW_C0.md F-09 excludes it from OF-06 by name."
    )


# =======================================================================================
# OF-09 — repo_root() reported on the wrong directory and no target named the one it used
# OF-10 — one raising check group destroyed the entire report, INCLUDING THE SECRET SCAN
# =======================================================================================


def test_check_roles_FAILS_rather_than_passing_vacuously_on_a_non_repository(tmp_path, capsys):
    """`OPEN_FINDINGS.md` **OF-09**. *"It fooled the reviewer for one experiment."*

    ``repo_root()`` is ``Path(__file__).resolve().parents[2]``, correct only for an editable
    src-layout install. Under ``pip install .`` it resolves to ``…/.venv/Lib``, and
    `check-roles` printed **`PASS F1 config/ loads — protocol.yaml and lanes.yaml parse`**
    over **zero** config files. With one venv and two checkouts it reports on the venv's
    checkout — it printed a full green report while the reviewer stood in a clone with a
    deliberately corrupted `.gitattributes`.
    """
    empty = tmp_path / "not-a-repo"
    empty.mkdir()

    rc = check_roles.run(empty)
    printed = capsys.readouterr().out

    assert rc != 0, "check-roles exited 0 over a directory that is not this repository"
    assert str(empty) in printed, (
        "check-roles did not NAME the root it examined. For a tool whose entire output is "
        "'this repository is sound', not naming the repository is a reporting defect."
    )
    assert "R1 the examined root IS this repository" in printed
    assert "THIS IS NOT THE REPOSITORY" in printed


def test_every_target_prints_the_root_it_examined(repo_root, capsys):
    """The other half of OF-09: naming the root even when everything passes."""
    check_roles.run(repo_root)
    printed = capsys.readouterr().out
    assert printed.count("ROOT EXAMINED") >= 2, (
        "the examined root must be printed at the TOP and at the BOTTOM: a reader who "
        f"scrolls to the verdict must see which directory it is about. output: {printed[:400]}"
    )
    assert str(repo_root) in printed
    assert str(cfg.config_dir()) in printed


def test_one_raising_group_cannot_silence_the_secret_scan(tmp_path, capsys, monkeypatch):
    """`OPEN_FINDINGS.md` **OF-10**, reproduced and then fixed.

    ``run()`` built all four groups in one eager list expression, and
    ``check_gitattributes(root) + check_secrets(root)`` was a **single element** of it. So a
    ``.gitattributes`` carrying a non-UTF-8 byte made ``read_text`` raise and took the
    **secret scan** down with it, along with D, E and F: a bare traceback, exit 1, and **no
    check output at all**. Fail-closed on the exit code; zero information in the report.
    ``_git()``'s ``RuntimeError`` had the same blast radius.
    """
    repo = _init(tmp_path / "r")
    (repo / ".env.example").write_bytes(b"GROQ_API_KEY=\n")
    (repo / "config").mkdir()
    (repo / "config" / "protocol.yaml").write_text(_MINIMAL_PROTOCOL, encoding="utf-8")
    (repo / "config" / "lanes.yaml").write_text(_MINIMAL_LANES, encoding="utf-8")
    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(repo / "config"))
    _commit(repo)
    # A non-UTF-8 byte: `read_text(encoding="utf-8")` raises UnicodeDecodeError.
    (repo / ".gitattributes").write_bytes(b"* text=auto eol=lf\n" + bytes([0xFF, 0xFE]))

    rc = check_roles.run(repo)
    printed = capsys.readouterr().out

    assert rc != 0, "a group that raised must still fail the run"
    assert "this check GROUP raised and did not run" in printed, (
        f"the group that raised is not named in the report: {printed[:600]}"
    )
    assert "UnicodeDecodeError" in printed, printed[:600]
    # ⚠️ THE POINT: the secret scan still ran, and so did D, E and F.
    assert "C1 no secret-shaped string in any tracked file" in printed, (
        "a .gitattributes problem silenced the SECRET SCAN. That is OF-10, and it is the "
        f"reason the finding is not cosmetic. output: {printed[:800]}"
    )
    assert "B1 no .env tracked" in printed
    assert "E1 no commit carries an UNISSUED token" in printed
    assert "F1 config/ loads" in printed
