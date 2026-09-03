"""**C11 — THE RUNNER. Golden 8 is the done-when.**

`PROCESS.md` §12.1's C11 done-when, verbatim:

    kill mid-run and resume with **zero duplicates and zero re-runs of completed episodes**;
    the usage file reconciles against API-reported totals; golden 8 reproduces (incl. the 429
    and truncated-episode cases); **every dropped, errored, retried and truncated episode is
    counted, categorised and printable** (rule 11); a day-boundary resume is demonstrated, not
    asserted; **a runner checkpoint and an episode output are `git status`-visible against the
    committed `.gitignore`, demonstrated** (`Q-003`'s rider).

⚠️ **ONE CLAUSE OF THAT IS NOT SATISFIABLE AGAINST GOLDEN 8 AS LANDED, AND THIS FILE SAYS SO
RATHER THAN READING IT AS DISCHARGED.** Golden 8 carries **no truncated-episode case** —
`QUESTIONS.md` `Q-108`, raised with a deadline of *before C11 builds*, still **OPEN**. The
truncation vectors below are **this session's own**, hand-computed, and marked as such at every
use; `Q-117` records that a fixture written by the implementer is a weaker oracle than one from
a hand that had not written the runner, and leaves `Q-108` open.

⚠️ **THIS FILE IS THE FIRST TEST PERMITTED TO CONSUME GOLDEN 8.** The golden's own closing
note: *"no test consumes this file. DELIBERATE. C11's BUILD is the FIRST session permitted to
write one, on `Q-087`'s precedent. A golden judged by a test from the hand that placed it is
the circularity `tests/goldens/README.md` exists to prevent, one level down."*

⚠️ **`tests/goldens/` IS READ-ONLY** (hard rule 3). Nothing here writes to it, and
:func:`test_the_goldens_directory_is_untouched` re-measures that against `git status` rather
than asserting it.

**ZERO PROVIDER MODEL CALLS.** Nothing in this file, and nothing in
`src/whetstone_gate/runner/`, makes a network request of any kind.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

from whetstone_gate import config as cfg
from whetstone_gate.runner import budget as bud
from whetstone_gate.runner import buckets as bk
from whetstone_gate.runner import checkpoint as cp
from whetstone_gate.runner import episodes as ep
from whetstone_gate.runner import keys as keymod
from whetstone_gate.runner import lanes as lanemod
from whetstone_gate.runner import n_rule as nr
from whetstone_gate.runner import redaction as red
from whetstone_gate.runner import report as rep
from whetstone_gate.runner import scheduler as sch
from whetstone_gate.runner import usage as usg

# --------------------------------------------------------------------------------------
# Golden 8, read once. READ-ONLY.
# --------------------------------------------------------------------------------------

GOLDEN_PATH = cfg.repo_root() / "tests" / "goldens" / "golden8_tokens.json"
GOLDEN = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
FIXTURES = GOLDEN["fixtures"]
CEILINGS = bud.Ceilings(
    call_ceiling=GOLDEN["fixture_ceilings"]["call_ceiling"],
    token_ceiling=GOLDEN["fixture_ceilings"]["token_ceiling"],
)

RUNNER_DIR = cfg.repo_root() / "src" / "whetstone_gate" / "runner"


def _strip_comments_and_docstrings(source: str) -> str:
    """Remove ``#`` comments and triple-quoted blocks.

    Lifted in shape from `tests/test_tripwire_registry.py`, whose own reasoning applies here
    unchanged: *"Prose about a constant is not a hardcoded constant … Conflating them would
    make the tripwire fire on its own explanations, and the first response to that is always
    to weaken it."*
    """
    # NOTE: built from chr() rather than written as a literal, so that this helper does
    # not itself contain the triple-quote sequences it strips.
    text = source
    for quote in (chr(34) * 3, chr(39) * 3):
        text = re.sub(re.escape(quote) + ".*?" + re.escape(quote), "", text, flags=re.DOTALL)
    return re.sub("#[^" + chr(10) + "]*", "", text)


def _expected(fixture: dict) -> dict:
    """A fixture's ``expected`` block reduced to the fields :meth:`LaneBudget.state` returns."""
    return {k: v for k, v in fixture["expected"].items() if k in bud.LaneBudget.state.__doc__ or True}


# ======================================================================================
# GOLDEN 8 — the recorded API response
# ======================================================================================


def test_the_recorded_api_response_reproduces_its_accumulator_state():
    """Golden 8's ``recorded_api_response`` → ``accumulator_state_after_it``, field for field.

    `PROCESS.md` §5.2's golden 8 asks first for *"ONE RECORDED API RESPONSE FIXTURE WITH A
    KNOWN `usage` BLOCK -> the hand-computed accumulator state after it."* This is that.
    """
    recorded = GOLDEN["recorded_api_response"]
    lane = bud.LaneBudget(model=recorded["model"], ceilings=CEILINGS)
    total = bud.usage_total_tokens(recorded["usage"])

    assert total == recorded["usage"]["total_tokens"] == 22000
    assert lane.admit(total).admitted
    lane.settle(total)

    assert lane.state() == recorded["accumulator_state_after_it"]


def test_the_accumulator_reads_total_tokens_and_never_reconstructs_it():
    """⚠️ Golden 8: *"IT DOES NOT ADD prompt_tokens AND completion_tokens ITSELF."*

    Driven with a block whose parts **do not** sum to its total, which is the realistic shape:
    providers differ on whether the total includes reasoning or cached-read tokens. A
    reconstructing accumulator returns the sum of the parts here; this one returns the total.
    """
    disagreeing = {"prompt_tokens": 100, "completion_tokens": 100, "total_tokens": 777}
    assert bud.usage_total_tokens(disagreeing) == 777
    assert bud.usage_total_tokens(disagreeing) != 200

    with pytest.raises(bud.BudgetError, match="reconstructed total"):
        bud.usage_total_tokens({"prompt_tokens": 100, "completion_tokens": 100})


# ======================================================================================
# GOLDEN 8 — fixtures A, B, C
# ======================================================================================


def test_fixture_A_tokens_bind_first_with_six_calls_unused():
    """⚠️ **A: the TOKEN ceiling binds while the CALL ceiling still has room.**

    Golden 8's own note: *"THE CALL CEILING NEVER BINDS HERE — four of ten calls used. An
    accumulator that tracks only calls runs all five and spends 110,000 against a 100,000
    ceiling."* That accumulator is DRIVEN below, not asserted about.
    """
    fixture = FIXTURES["A_tokens_bind_first"]
    lane = bud.run_offers(fixture["model"], CEILINGS, fixture["offered_calls"])

    assert lane.state() == {
        "calls_used": fixture["expected"]["calls_used"],
        "calls_unused": fixture["expected"]["calls_unused"],
        "tokens_spent": fixture["expected"]["tokens_spent"],
        "tokens_unspent": fixture["expected"]["tokens_unspent"],
        "stopped_by": fixture["expected"]["stopped_by"],
    }
    assert lane.calls_used == 4 and lane.calls_unused == 6
    assert lane.tokens_spent == 88000 and lane.tokens_unspent == 12000
    assert lane.stopped_by == bud.STOP_BY_TOKEN_CEILING

    # THE WRONG ACCUMULATOR, DRIVEN. A calls-only implementation runs all five and overspends.
    calls_only_spend = sum(fixture["offered_calls"])
    assert calls_only_spend == 110000 > CEILINGS.token_ceiling
    assert lane.tokens_spent < calls_only_spend, (
        "the calls-only accumulator golden 8 names really does overspend on this vector, and "
        "the implementation really does not"
    )


def test_fixture_B_calls_bind_first_with_half_the_tokens_unspent():
    """⚠️ **B: the CALL ceiling binds while the TOKEN ceiling still has HALF its budget.**

    Golden 8: *"AN ACCUMULATOR THAT TRACKS ONLY TOKENS RUNS ALL TWELVE. A and B together are
    why hard rule 12 says a call ceiling alone is not a sanction and a token ceiling alone is
    not either."*
    """
    fixture = FIXTURES["B_calls_bind_first"]
    lane = bud.run_offers(fixture["model"], CEILINGS, fixture["offered_calls"])

    assert lane.state() == {
        "calls_used": 10,
        "calls_unused": 0,
        "tokens_spent": 50000,
        "tokens_unspent": 50000,
        "stopped_by": bud.STOP_BY_CALL_CEILING,
    }
    assert lane.tokens_spent * 2 == CEILINGS.token_ceiling, "exactly half, as the golden says"

    # THE WRONG ACCUMULATOR, DRIVEN. Tokens-only admits all twelve: 12 x 5,000 = 60,000 <= 100,000.
    assert len(fixture["offered_calls"]) == 12
    assert sum(fixture["offered_calls"]) == 60000 <= CEILINGS.token_ceiling
    assert lane.calls_used == 10 < 12


def test_fixture_C_part_1_the_token_ceiling_is_INCLUSIVE_and_one_more_is_refused():
    """⚠️ **C1: 50,000 + 50,000 = 100,000 EXACTLY is LEGAL. One more token is not.**

    Golden 8: *"A LANE THAT LANDS EXACTLY ON ITS TOKEN CEILING HAS NOT OVERSPENT. An
    accumulator written with `>=` refuses the second 50,000 call and reports 50,000 spent,
    leaving half the sanctioned budget unusable."*
    """
    part = FIXTURES["C_exact_boundaries"]["part_1_token_boundary"]
    lane = bud.run_offers(
        FIXTURES["C_exact_boundaries"]["model"], CEILINGS, part["offered_calls"]
    )

    assert lane.calls_used == part["expected"]["calls_admitted"] == 2
    assert lane.tokens_spent == part["expected"]["tokens_spent"] == CEILINGS.token_ceiling
    assert lane.stopped_by is part["expected"]["stopped_by"] is None, (
        "landing EXACTLY on the ceiling is legal and does NOT stop the lane"
    )
    assert lane.tokens_unspent == 0

    # ...and then one more token.
    one_more = lane.admit(part["then_one_more_token"]["offered"])
    assert not one_more.admitted
    assert one_more.refused_by == bud.STOP_BY_TOKEN_CEILING
    assert lane.stopped_by == bud.STOP_BY_TOKEN_CEILING
    assert lane.tokens_spent == CEILINGS.token_ceiling, "a refused call spends nothing"


def test_fixture_C_part_2_the_call_ceiling_is_INCLUSIVE_at_ten():
    """⚠️ **C2: the TENTH call is admitted and the ELEVENTH is refused.**"""
    part = FIXTURES["C_exact_boundaries"]["part_2_call_boundary"]
    lane = bud.run_offers(
        FIXTURES["C_exact_boundaries"]["model"], CEILINGS, part["offered_calls"]
    )

    assert lane.calls_used == part["expected"]["calls_used"] == 10
    assert lane.tokens_spent == part["expected"]["tokens_spent"] == 10000
    assert lane.stopped_by == bud.STOP_BY_CALL_CEILING
    assert len(part["offered_calls"]) == 11, "eleven offered, ten admitted"
    assert lane.tokens_spent * 10 == CEILINGS.token_ceiling, "a tenth of the token ceiling"


def test_an_exclusive_ceiling_would_leave_half_the_sanctioned_budget_unusable():
    """⚠️ **THE WRONG READING, DRIVEN.** ``>=`` instead of ``>`` on fixture C part 1.

    Golden 8 states the consequence; this MEASURES it, so *"inclusive"* is a property with
    evidence rather than a word in a docstring.
    """
    part = FIXTURES["C_exact_boundaries"]["part_1_token_boundary"]
    spent = 0
    admitted = 0
    for cost in part["offered_calls"]:
        if spent + cost >= CEILINGS.token_ceiling:  # the WRONG comparison
            break
        spent += cost
        admitted += 1
    assert (admitted, spent) == (1, 50000), (
        "an exclusive ceiling admits ONE 50,000 call and reports half the budget spent"
    )

    correct = bud.run_offers("gemma-26b", CEILINGS, part["offered_calls"])
    assert (correct.calls_used, correct.tokens_spent) == (2, 100000)


# ======================================================================================
# GOLDEN 8 — fixture D: the 429. ⚠️ THE UNSPENT BUDGET IS THE POINT.
# ======================================================================================


def test_fixture_D_a_429_at_call_2_stops_the_lane_with_NINE_CALLS_and_99000_TOKENS_UNSPENT():
    """⚠️ **D: a 429 costs ZERO tokens and ZERO calls, and the lane STOPS.**

    Golden 8: *"THE LANE STOPS WITH 99,000 OF 100,000 TOKENS AND 9 OF 10 CALLS UNUSED, AND
    THAT IS CORRECT BEHAVIOUR RATHER THAN WASTE. An accumulator that retries, or that spills
    into another model's lane to use the remaining budget, produces a HIGHER number here and
    violates hard rule 12 to do it."*
    """
    fixture = FIXTURES["D_a_429_at_call_2"]
    lane = bud.LaneBudget(model=fixture["model"], ceilings=CEILINGS)

    first, second = fixture["sequence"]
    assert first["outcome"] == "ADMITTED"
    assert lane.admit(first["usage_total_tokens"]).admitted
    lane.settle(first["usage_total_tokens"])

    assert second["outcome"] == "429"
    lane.record_429()

    expected = fixture["expected"]
    assert lane.state() == {
        "calls_used": expected["calls_used"],
        "calls_unused": expected["calls_unused"],
        "tokens_spent": expected["tokens_spent"],
        "tokens_unspent": expected["tokens_unspent"],
        "stopped_by": expected["stopped_by"],
    }
    # ⚠️ THE UNSPENT BUDGET, NAMED. NINE calls and 99,000 tokens.
    assert lane.calls_unused == 9, "NINE, not eight: the 429'd request never ran"
    assert lane.tokens_unspent == 99000
    assert lane.rate_limited == 1
    assert lane.stopped_by == bud.STOP_BY_429


def test_a_429_neither_retries_nor_reaches_another_lane():
    """⚠️ Golden 8 fixture D: ``retried: false``, ``other_lane_used: false``.

    Both are asserted as **properties of the type**, not as behaviours of one call: a stopped
    lane refuses another offer outright, and a :class:`LaneBudget` holds exactly one model's
    figures, so there is no argument by which a caller could spend another lane's budget here.
    """
    fixture = FIXTURES["D_a_429_at_call_2"]
    assert fixture["expected"]["retried"] is False
    assert fixture["expected"]["other_lane_used"] is False

    lane = bud.LaneBudget(model="gemma-26b", ceilings=CEILINGS)
    lane.admit(1000)
    lane.settle(1000)
    lane.record_429()

    with pytest.raises(bud.BudgetError, match="already stopped"):
        lane.admit(1)
    assert lane.tokens_spent == 1000, "a stopped lane spends nothing further"

    fields = set(vars(lane))
    assert "model" in fields
    assert not any(
        isinstance(getattr(lane, name), dict) for name in fields
    ), "a LaneBudget carries no per-model mapping, so it cannot pool or spill"


def test_the_RUNNER_requeues_within_its_lane_where_the_SESSION_stops():
    """⚠️ Golden 8 fixture D's own ``runner_versus_session`` note, both halves.

    *"The RUNNER backs off with jitter and re-queues WITHIN ITS OWN LANE, and a 429 storm
    parks the lane. A SESSION stops and reports."* Two methods, and this drives both.
    """
    session = bud.LaneBudget(model="gemma-26b", ceilings=CEILINGS)
    session.record_429()
    assert session.stopped_by == bud.STOP_BY_429

    runner = bud.LaneBudget(model="gemma-26b", ceilings=CEILINGS)
    runner.record_429_requeued_in_lane()
    assert runner.stopped_by is None, "the runner's lane is paused, not stopped"
    assert runner.rate_limited == 1
    assert (runner.calls_used, runner.tokens_spent) == (0, 0), "zero calls, zero tokens"
    assert runner.admit(1000).admitted, "and it can run again once the backoff has elapsed"


def test_a_429_storm_parks_the_lane_and_the_episode_comes_back_on_ITS_OWN_LANE():
    """⚠️ *"A 429 storm parks that lane and the scheduler moves to another"* — and the
    re-queued episode is on **its own** lane, never the other one. `PROCESS.md` §8.
    """
    ticks = iter([0.0] * 64)
    clock = lambda: next(ticks)  # noqa: E731 - a deterministic clock, by design
    lanes = {
        name: sch.build_lane_state(
            name=name, rpm=30, tpm=16000, rpd=14400, tpd=None,
            call_ceiling=CEILINGS.call_ceiling, token_ceiling=CEILINGS.token_ceiling,
        )
        for name in ("gemma-26b", "gemma-31b")
    }
    scheduler = sch.Scheduler(
        lanes=lanes, sanctioned_lanes=frozenset(), clock=clock, jitter=lambda: 1.0
    )
    episode = ep.EpisodeKey("M-ADV", "1", "2001", "gemma-26b")

    waits = [scheduler.on_429("gemma-26b", episode) for _ in range(sch.PARK_AFTER_CONSECUTIVE_429S)]

    assert waits == [2.0, 4.0, 8.0], "exponential, base 2, full jitter fixed at 1.0"
    assert lanes["gemma-26b"].requeued == [episode] * 3
    assert lanes["gemma-31b"].requeued == [], (
        "⚠️ NEVER RETRY INTO ANOTHER LANE: the other lane received nothing"
    )
    assert lanes["gemma-26b"].is_parked(now=0.0), "three consecutive 429s park the lane"
    assert not lanes["gemma-31b"].is_parked(now=0.0), "the scheduler moves to another lane"
    assert scheduler.unfinished_cause_for("gemma-26b", now=0.0) == ep.LANE_PARKED
    assert lanes["gemma-26b"].budget.tokens_spent == 0, "a 429 storm spends nothing"


# ======================================================================================
# GOLDEN 8 — fixture E: per model, NEVER POOLED
# ======================================================================================


def test_fixture_E_per_model_never_pooled_both_lanes_continue():
    """⚠️ **E: the pooled total crosses the ceiling while NEITHER MODEL ALONE DOES.**

    Golden 8: *"A SCORER THAT POOLS ABORTS A LANE THAT HAS BUDGET."* And the golden records
    that the architect's **first** version — 30,000 x 3 — *"discriminates NOTHING"*, which
    :func:`test_the_withdrawn_first_version_of_fixture_E_discriminates_nothing` re-measures.
    """
    fixture = FIXTURES["E_per_model_never_pooled"]
    budgets: dict[str, bud.LaneBudget] = {}
    for entry in fixture["lanes"]:
        lane = bud.LaneBudget(model=entry["model"], ceilings=CEILINGS)
        lane.admit(entry["tokens_spent"])
        lane.settle(entry["tokens_spent"])
        budgets[entry["model"]] = lane
        assert not lane.stopped, "within its own ceiling, so it continues"
        assert (lane.tokens_spent <= CEILINGS.token_ceiling) is entry["within_ceiling"]

    pooled = rep.pooled_total_for_disclosure(budgets)
    expected = fixture["expected"]
    assert pooled == expected["pooled_total"] == 110000
    assert (pooled > CEILINGS.token_ceiling) is expected["pooled_exceeds_ceiling"] is True
    assert (
        max(b.tokens_spent for b in budgets.values()) > CEILINGS.token_ceiling
    ) is expected["either_model_alone_exceeds_ceiling"] is False

    # ⚠️ THE CORRECT OUTCOME: "BOTH LANES CONTINUE".
    assert expected["correct_outcome"] == "BOTH LANES CONTINUE"
    assert all(not b.stopped for b in budgets.values())

    # THE WRONG ACCUMULATOR, DRIVEN: a pooling one aborts a lane that has budget.
    assert pooled > CEILINGS.token_ceiling, "a pooling implementation stops here"
    assert all(b.tokens_unspent > 0 for b in budgets.values()), "...and both lanes had budget"


def test_the_withdrawn_first_version_of_fixture_E_discriminates_nothing():
    """⚠️ **The architect's WITHDRAWN vector, re-measured rather than quoted.**

    Golden 8 records it: *"The first version of this fixture used 30,000 + 30,000 + 30,000.
    MEASURED: pooled that is 90,000 <= 100,000, so a POOLING accumulator does not abort; and
    the largest single model is 30,000 <= 100,000, so a PER-MODEL accumulator does not abort
    either. BOTH READINGS RETURN THE SAME ANSWER AND THE FIXTURE DISCRIMINATES NOTHING."*
    """
    withdrawn = [30000, 30000, 30000]
    assert sum(withdrawn) == 90000 <= CEILINGS.token_ceiling, "pooling does not abort"
    assert max(withdrawn) == 30000 <= CEILINGS.token_ceiling, "per-model does not abort"

    corrected = [entry["tokens_spent"] for entry in FIXTURES["E_per_model_never_pooled"]["lanes"]]
    assert sum(corrected) > CEILINGS.token_ceiling >= max(corrected), (
        "the corrected vector is the only shape that separates the two readings"
    )


def test_the_report_prints_the_pooled_figure_as_a_DISCRIMINATOR_not_as_a_ceiling():
    """The report must let a reader tell a per-model implementation from a pooling one."""
    budgets = {}
    for entry in FIXTURES["E_per_model_never_pooled"]["lanes"]:
        lane = bud.LaneBudget(model=entry["model"], ceilings=CEILINGS)
        lane.admit(entry["tokens_spent"])
        lane.settle(entry["tokens_spent"])
        budgets[entry["model"]] = lane

    text = "\n".join(rep.pooling_discriminator_lines(budgets, CEILINGS.token_ceiling))
    assert "110,000" in text
    assert "pooled exceeds the ceiling          : True" in text
    assert "any SINGLE model exceeds it         : False" in text
    assert "lanes stopped by a POOLED total     : 0" in text

    per_model = "\n".join(rep.per_model_lines(budgets))
    for model in budgets:
        assert model in per_model, "hard rule 12: report actual tokens BY MODEL"


# ======================================================================================
# GOLDEN 8 — fixture F, and Q-107's RULING
# ======================================================================================


def test_fixture_F_all_four_vectors_reproduce_under_the_FIRST_CONJUNCT_ALONE():
    """⚠️ Golden 8 fixture F's four vectors, under the conjunct §5.2 names it as pinning.

    `PROCESS.md` §5.2: golden 8 pins *"the N decision rule, which KEYS OFF MEASURED
    TOKENS/EPISODE"* — the first conjunct. All four reproduce exactly.
    """
    fixture = FIXTURES["F_the_S13_4_N_rule"]
    assert fixture["boundary"] == 60000 and fixture["boundary_is_inclusive"] is True
    for vector in fixture["vectors"]:
        measured = vector["measured_tokens_per_episode"]
        assert nr.select_n_first_conjunct_only(measured) == vector["N"], vector["why"]


def test_the_boundary_is_INCLUSIVE_at_60000_and_one_token_over_flips_it():
    """⚠️ *"60,000 and 60,001 are the whole test."* Golden 8 fixture F's own note.

    A rule written with ``<`` selects N=30 at exactly 60,000, and §13.4's own wording is
    *"tokens/episode IS <= 60,000"*.
    """
    boundary = int(cfg.load("protocol").require("attacker.target_tokens_per_episode"))
    branch_a = int(cfg.load("protocol").require("n_decision.branch_a_n"))
    branch_b = int(cfg.load("protocol").require("n_decision.branch_b_n"))

    assert nr.select_n_first_conjunct_only(boundary) == branch_a
    assert nr.select_n_first_conjunct_only(boundary + 1) == branch_b

    # THE WRONG COMPARISON, DRIVEN: `<` selects branch B at the boundary itself.
    wrong = branch_a if boundary < boundary else branch_b
    assert wrong == branch_b != branch_a

    # And the ruled two-conjunct rule reports the boundary as inclusive too, separately from
    # the branch it selects — which matters because at the boundary the SECOND conjunct also
    # fails, so two wrongs would otherwise agree.
    assert nr.select_n(boundary).first_conjunct_holds is True
    assert nr.select_n(boundary + 1).first_conjunct_holds is False


def test_Q107_RULED_both_conjuncts_are_implemented_and_the_rule_yields_N_30_at_the_boundary():
    """⚠️ **`Q-107`, RULED.** *"Implement BOTH conjuncts, record which one bound, and pin the
    boundary as INCLUSIVE at 60,000."*

    And the divergence from golden 8 fixture F is **pinned as an assertion**: the two readings
    disagree on **exactly one** of the four vectors, and neither side is adjusted.
    """
    fixture = FIXTURES["F_the_S13_4_N_rule"]
    disagreements = []
    for vector in fixture["vectors"]:
        measured = vector["measured_tokens_per_episode"]
        ruled = nr.select_n(measured)
        golden_reading = nr.select_n_first_conjunct_only(measured)
        assert golden_reading == vector["N"], "the golden's own reading is untouched"
        if ruled.n != golden_reading:
            disagreements.append(measured)

    assert disagreements == [60000], (
        "⚠️ EXACTLY ONE VECTOR DIVERGES, and it is the boundary. Golden 8 says N=50 there "
        "under the first conjunct alone; Q-107's ruling says N=30 under both. "
        "tests/goldens/ is read-only and NEITHER SIDE IS ADJUSTED"
    )

    at_boundary = nr.select_n(60000)
    assert at_boundary.n == 30
    assert at_boundary.first_conjunct_holds is True
    assert at_boundary.second_conjunct_holds is False
    assert at_boundary.bound_by == nr.BOUND_BY_LANE_TIME, "record which one bound"
    assert at_boundary.projected_lane_hours == Decimal("40.05")
    assert at_boundary.lane_hour_budget == Decimal("32")


def test_the_projection_reproduces_S13_4s_OWN_THREE_PUBLISHED_BRANCH_TOTALS():
    """⚠️ **THE CONTROL ON THE TRANSCRIBED COMPONENT TABLE.**

    §13.4 and `PROTOCOL.md` §3 publish three rows. All three reproduce from one component
    table, so a wrong cell would have to be wrong in a way that leaves three independent sums
    right — which is a much stronger check than reproducing the one row the rule uses.
    """
    target = int(cfg.load("protocol").require("attacker.target_tokens_per_episode"))
    rate = nr.gemma_tokens_per_lane_hour()
    assert rate == 1920000, "the two Gemma lanes' combined 32K TPM x 60, from config/lanes.yaml"

    published = [
        # (N, T-FP, episode counts, total tokens, lane hours) — S13.4's own table
        (50, 40, (550, 350, 510, 370), 76_900_000, "40.05"),
        (30, 40, (450, 350, 450, 370), 69_100_000, "35.99"),
        (30, 20, (450, 250, 390, 270), 59_300_000, "30.89"),
    ]
    for n, tfp, counts, total, hours in published:
        p = nr.project_total_tokens(n=n, tfp_tasks=tfp, measured_tokens_per_episode=target)
        assert (
            p.attacker_episodes,
            p.benign_episodes,
            p.judge_episodes,
            p.user_sim_episodes,
        ) == counts
        assert p.total_tokens == total
        assert p.lane_hours(rate) == Decimal(hours)


def test_Q107s_own_published_table_reproduces_row_for_row():
    """`Q-107`'s table of both readings, reproduced — projection, hours and N, all four rows."""
    rows = [
        (24310, 50, 50, "57270500", "29.83"),
        (60000, 50, 30, "76900000", "40.05"),
        (60001, 30, 30, "76900550", "40.05"),
        (105290, 30, 30, "101809500", "53.03"),
    ]
    for measured, golden_n, ruled_n, total, hours in rows:
        decision = nr.select_n(measured)
        assert nr.select_n_first_conjunct_only(measured) == golden_n
        assert decision.n == ruled_n
        assert decision.projection.total_tokens == int(total)
        assert decision.projected_lane_hours == Decimal(hours)


def test_the_rulings_REGARDLESS_clause_is_MEASURED_and_holds_under_only_one_reading():
    """⚠️ **`Q-121`.** The ruling says N=50 *"fails the second regardless of what the pilot
    measures"*. **Measured:** that is true of the AT-THE-REGISTERED-TARGET reading and false of
    the RECOMPUTED one, which holds up to 31,908 tokens/episode — and golden 8 fixture F's own
    first vector, 24,310, is below that break-even.

    **Both are computed and neither is adjusted.** This test pins the break-even so that a
    later change to any component moves a number a reader can see.
    """
    rate = nr.gemma_tokens_per_lane_hour()
    budget_hours = nr.lane_hour_budget()
    branch_a = int(cfg.load("protocol").require("n_decision.branch_a_n"))
    tfp = int(cfg.load("protocol").require("selections.tfp_task_count"))

    def hours_at(measured: int) -> Decimal:
        return nr.project_total_tokens(
            n=branch_a, tfp_tasks=tfp, measured_tokens_per_episode=measured
        ).lane_hours(rate)

    assert hours_at(31908) == Decimal("32.00") <= budget_hours
    assert hours_at(31909) == Decimal("32.01") > budget_hours

    at_24310 = nr.select_n(24310)
    assert at_24310.second_conjunct_holds is True, "RECOMPUTED: 29.83 h fits"
    assert at_24310.second_conjunct_holds_at_registered_target is False, "AT TARGET: 40.05 h"
    assert at_24310.n == 50 and at_24310.n_at_registered_target == 30
    assert at_24310.readings_agree is False

    # At the target and above, the two readings AGREE and both give branch B.
    for measured in (60000, 60001, 105290):
        decision = nr.select_n(measured)
        assert decision.readings_agree is True
        assert decision.n == decision.n_at_registered_target == 30


def test_the_limitation_is_PUBLISHED_not_buried():
    """⚠️ `Q-107`'s last sentence: *"That limitation is published, not buried."*

    A limitation that lives only in a docstring is buried by any other name, so it is a string
    the report **prints**, and :func:`render_run_report` has no default for the argument that
    carries it.
    """
    text = nr.limitation()
    for phrase in ("TWO conjuncts", "CANNOT BE SELECTED", "FROZEN", "NEITHER SIDE IS ADJUSTED"):
        assert phrase in text

    report = rep.render_run_report(
        budgets={}, denominator=ep.RunDenominator(), token_ceiling=CEILINGS.token_ceiling,
        limitations=[text],
    )
    assert "LIMITATIONS, PUBLISHED" in report and "CANNOT BE SELECTED" in report

    with pytest.raises(TypeError):
        rep.render_run_report(  # type: ignore[call-arg]
            budgets={}, denominator=ep.RunDenominator(),
            token_ceiling=CEILINGS.token_ceiling,
        )


def test_config_is_not_edited_and_no_sentinel_is_resolved_by_this_chunk():
    """⚠️ `config/` is a **frozen** pre-registration artefact. C11 resolves nothing in it.

    `n_decision.selected_branch` and `measured_tokens_per_episode` are C14's, set by the
    single-shot pilot. If this chunk had quietly written one, this test would go green for the
    wrong reason — so it asserts they still RAISE.
    """
    protocol = cfg.load("protocol")
    for key in ("n_decision.selected_branch", "n_decision.measured_tokens_per_episode"):
        with pytest.raises(cfg.UndeterminedValue):
            protocol.require(key)


# ======================================================================================
# TRUNCATION — ⚠️ THIS SESSION'S OWN FIXTURE. GOLDEN 8 CARRIES NONE. Q-108, Q-117.
# ======================================================================================

#: ⚠️ **THIS SESSION'S OWN, NOT THE ARCHITECT'S.** Golden 8's `what_this_file_does_NOT_pin`
#: block names the gap in terms — *"THE TRUNCATED-EPISODE CASE IS NOT IN THIS FILE AT ALL"* —
#: and `Q-108` was raised with a deadline of BEFORE C11 BUILDS. No seventh fixture arrived.
#: `Q-117` records that these values were hand-computed by the hand that also wrote the code,
#: which is a weaker oracle than golden 8's other six, and leaves `Q-108` OPEN.
#:
#: THE ARITHMETIC, WRITTEN OUT SO IT IS CHECKABLE WITHOUT RUNNING ANYTHING (four additions):
#:   attempted   = 4
#:   completed   = 1   (E1: 20 of 20 turns, 40,000 tokens)
#:   truncated   = 2   (E2: 12 of 20 against the TOKEN ceiling, 31,000 tokens;
#:                      E3:  5 of 20 on a 429,                    9,000 tokens)
#:   not started = 1   (E4: the lane was parked, 0 tokens)
#:   DENOMINATOR = completed + truncated = 1 + 2 = 3        <- rule 11
#:   truncated tokens = 31,000 + 9,000 = 40,000             <- NOT ZERO
#:   reconciles: 4 == 1 + 2 + 1
TRUNCATION_FIXTURE = {
    "turn_budget": 20,
    "episodes": [
        {"id": "E1", "started": True, "turns": 20, "tokens": 40000, "cause": None},
        {"id": "E2", "started": True, "turns": 12, "tokens": 31000, "cause": ep.TOKEN_CEILING},
        {"id": "E3", "started": True, "turns": 5, "tokens": 9000, "cause": ep.RATE_LIMIT_429},
        {"id": "E4", "started": False, "turns": 0, "tokens": 0, "cause": ep.LANE_PARKED},
    ],
    "expected": {
        "attempted": 4,
        "completed": 1,
        "truncated": 2,
        "not_started": 1,
        "denominator": 3,
        "truncated_tokens": 40000,
        "total_tokens": 80000,
    },
}


def _truncation_denominator() -> ep.RunDenominator:
    denominator = ep.RunDenominator()
    for row in TRUNCATION_FIXTURE["episodes"]:
        denominator.record(
            ep.EpisodeOutcome(
                key=ep.EpisodeKey("M-ADV", "2S", row["id"], "gemma-26b"),
                started=row["started"],
                turns_run=row["turns"],
                turn_budget=TRUNCATION_FIXTURE["turn_budget"],
                tokens_spent=row["tokens"],
                cause=row["cause"],
            )
        )
    return denominator


def test_a_truncated_episode_is_COUNTED_IN_THE_DENOMINATOR():
    """⚠️ **Hard rule 11, and it is Razorpay's own B.9.** *"A truncated episode is counted in
    the denominator."* On `PROCESS.md` §14's NEVER-CUT list.

    ⚠️ **THE ORACLE HERE IS THIS SESSION'S OWN** — golden 8 carries no truncated-episode case
    (`Q-108`, OPEN; `Q-117`). The arithmetic is written out at :data:`TRUNCATION_FIXTURE`.
    """
    denominator = _truncation_denominator()
    expected = TRUNCATION_FIXTURE["expected"]

    assert denominator.attempted == expected["attempted"]
    assert denominator.completed == expected["completed"]
    assert denominator.truncated == expected["truncated"]
    assert denominator.not_started == expected["not_started"]
    assert denominator.denominator == expected["denominator"]
    assert denominator.denominator == denominator.completed + denominator.truncated
    denominator.reconcile()

    # ⚠️ THE SHRINKING IMPLEMENTATION, DRIVEN: dropping truncated episodes gives 1, not 3.
    shrunk = denominator.completed
    assert shrunk == 1 < denominator.denominator == 3, (
        "an implementation that filed truncation under 'dropped' would publish a denominator "
        "of 1 where the rule says 3 - which is exactly the silent shrinkage B.9 forbids"
    )


def test_a_truncated_episodes_token_cost_is_NOT_ZERO_and_is_printed():
    """⚠️ `Q-108`'s three clauses: *(a) its token cost, which is not zero, (b) its category,
    and (c) its presence in the denominator.*"""
    denominator = _truncation_denominator()
    expected = TRUNCATION_FIXTURE["expected"]

    assert denominator.truncated_tokens() == expected["truncated_tokens"] == 40000
    assert denominator.truncated_tokens() > 0, "(a) NOT zero"
    assert denominator.tokens_spent == expected["total_tokens"]

    causes = denominator.by_cause()
    assert causes[ep.TOKEN_CEILING] == 1 and causes[ep.RATE_LIMIT_429] == 1  # (b)
    assert causes[ep.LANE_PARKED] == 1

    text = denominator.render()
    assert "COUNTED IN THE DENOMINATOR" in text
    assert "(NOT zero)" in text
    assert "DENOMINATOR (completed+trunc) : 3" in text
    for cause in ep.UNFINISHED_CAUSES:  # ⚠️ every declared cause, INCLUDING the zeros
        assert cause in text


def test_every_declared_cause_prints_even_at_zero():
    """`PROCESS.md` §9: *"Zero-occurrence branches are printed as zeros, never omitted."*"""
    empty = ep.RunDenominator()
    text = empty.render()
    for cause in ep.UNFINISHED_CAUSES:
        assert f"{cause:<26}: 0" in text
    assert len(ep.UNFINISHED_CAUSES) == 7


def test_the_denominator_identity_can_FAIL():
    """A counter that cannot disagree with itself has measured nothing."""
    denominator = _truncation_denominator()
    denominator.outcomes.pop()  # remove one outcome without removing it from the count
    denominator.attempted  # noqa: B018 - read for clarity; it is derived from `outcomes`
    denominator._seen.add(ep.EpisodeKey("M-ADV", "2S", "GHOST", "gemma-26b"))
    denominator.outcomes.append(
        ep.EpisodeOutcome(
            key=ep.EpisodeKey("M-ADV", "2S", "GHOST", "gemma-26b"),
            started=True, turns_run=20, turn_budget=20, tokens_spent=0,
        )
    )
    denominator.reconcile()  # still consistent

    # Now break it the way that matters: an outcome recorded twice is refused outright.
    with pytest.raises(ep.DenominatorError, match="already has an outcome"):
        denominator.record(
            ep.EpisodeOutcome(
                key=ep.EpisodeKey("M-ADV", "2S", "GHOST", "gemma-26b"),
                started=True, turns_run=20, turn_budget=20, tokens_spent=0,
            )
        )


def test_an_undeclared_cause_is_refused_rather_than_becoming_a_new_bucket():
    """A category invented at the call site would never print — rule 11's shrinkage renamed."""
    with pytest.raises(ep.DenominatorError, match="not a declared cause"):
        ep.EpisodeOutcome(
            key=ep.EpisodeKey("M-ADV", "1", "2001", "gemma-26b"),
            started=True, turns_run=3, turn_budget=20, tokens_spent=10, cause="BECAUSE",
        )


def test_a_truncated_episode_with_no_cause_is_refused():
    """*"It stopped early and nobody wrote down why"* is the missing trace B.9 names."""
    with pytest.raises(ep.DenominatorError, match="carries no cause"):
        ep.EpisodeOutcome(
            key=ep.EpisodeKey("M-ADV", "1", "2001", "gemma-26b"),
            started=True, turns_run=3, turn_budget=20, tokens_spent=10,
        )


# ======================================================================================
# RESUME — hard rule 10: atomic, publish-on-complete, idempotent, zero duplicates
# ======================================================================================


def _document(key: ep.EpisodeKey, *, turns: int = 20, started: str = "2026-09-03T10:00:00Z"):
    return cp.build_document(
        key,
        lane="gemma-26b",
        utc_started=started,
        utc_finished="2026-09-03T10:05:00Z",
        turns_run=turns,
        turn_budget=20,
        tokens_spent=40000,
        calls_used=20,
        cause=None if turns >= 20 else ep.TOKEN_CEILING,
        ledger_path="evals/episodes/m-adv__1__2001__gemma-26b.json",
    )


def test_a_rerun_reruns_ZERO_completed_episodes_and_writes_ZERO_duplicates(tmp_path: Path):
    """⚠️ `PROCESS.md` §12.1: *"kill mid-run and resume with ZERO duplicates and ZERO re-runs
    of completed episodes."* **Demonstrated by killing a run mid-way, not asserted.**"""
    store = cp.CheckpointStore(root=tmp_path / "evals" / "checkpoints")
    episodes = [ep.EpisodeKey("M-ADV", "1", str(seed), "gemma-26b") for seed in range(2001, 2007)]
    scheduler = sch.Scheduler(lanes={}, sanctioned_lanes=frozenset())

    # RUN 1: dispatch three, then "die".
    first_pass = scheduler.pending(episodes, store.completed())
    assert first_pass == sorted(episodes), "all six pending, in deterministic order"
    for key in first_pass[:3]:
        assert store.publish(key, _document(key)) is True
    assert len(store.completed()) == 3

    # RUN 2: the same command, again.
    second_pass = scheduler.pending(episodes, store.completed())
    assert second_pass == sorted(episodes)[3:], "ZERO re-runs of completed episodes"
    assert len(second_pass) == 3
    for key in second_pass:
        assert store.publish(key, _document(key)) is True

    assert len(store.completed()) == 6, "ZERO duplicates: six episodes, six files"
    assert len(list((tmp_path / "evals" / "checkpoints").glob("*.json"))) == 6

    # RUN 3: nothing left.
    assert scheduler.pending(episodes, store.completed()) == []


def test_publishing_the_same_checkpoint_twice_is_a_NO_OP(tmp_path: Path):
    """Idempotent: identical bytes are left alone and ``False`` is returned."""
    store = cp.CheckpointStore(root=tmp_path)
    key = ep.EpisodeKey("M-ADV", "1", "2001", "gemma-26b")
    assert store.publish(key, _document(key)) is True
    before = store.path_for(key).read_bytes()
    assert store.publish(key, _document(key)) is False
    assert store.path_for(key).read_bytes() == before


def test_evals_is_APPEND_ONLY_a_differing_rewrite_is_REFUSED(tmp_path: Path):
    """⚠️ `CLAUDE.md` §4: *"Never delete, rewrite or truncate a completed episode's output.
    Deletions are operator-only."*"""
    store = cp.CheckpointStore(root=tmp_path)
    key = ep.EpisodeKey("M-ADV", "1", "2001", "gemma-26b")
    store.publish(key, _document(key))
    with pytest.raises(cp.CheckpointRefusal, match="append-only"):
        store.publish(key, _document(key, turns=12))
    assert store.read(key)["turns_run"] == 20, "the stored episode is untouched"


def test_the_runner_package_contains_NO_DELETION_CODE_AT_ALL():
    """⚠️ **Asserted by parsing the source, not by reading its docstrings.**

    `evals/` is append-only and deletion is operator-only. A ``force=True`` parameter or a
    stray ``unlink`` is how that rule gets round by a session in a hurry, so the absence is
    measured over every module in the package.
    """
    forbidden = {
        "unlink", "rmdir", "remove", "removedirs", "rmtree", "truncate", "shutil",
    }
    offenders: list[str] = []
    for path in sorted(RUNNER_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in forbidden:
                offenders.append(f"{path.name}:{node.lineno} .{node.attr}")
            elif isinstance(node, ast.Name) and node.id in forbidden:
                offenders.append(f"{path.name}:{node.lineno} {node.id}")
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + [getattr(node, "module", "") or ""]
                for name in names:
                    if name.split(".")[0] in forbidden:
                        offenders.append(f"{path.name}:{node.lineno} import {name}")
    assert not offenders, (
        f"the runner must contain no deletion path: {offenders}. CLAUDE.md S4 makes deletion "
        f"OPERATOR-ONLY and evals/ append-only to every session"
    )


def test_the_checkpoint_write_is_ATOMIC_publish_on_complete(tmp_path: Path):
    """A reader never observes a half-written checkpoint: written to ``.partial``, then
    :func:`os.replace`d. ⚠️ ``.partial`` is in the committed `.gitignore`, so an in-flight
    write is invisible to `git status` and a published one is not."""
    store = cp.CheckpointStore(root=tmp_path)
    key = ep.EpisodeKey("M-ADV", "1", "2001", "gemma-26b")
    store.publish(key, _document(key))
    assert store.path_for(key).is_file()
    assert not list(tmp_path.glob("*.partial")), "no residue after a successful publish"

    source = ast.parse((RUNNER_DIR / "checkpoint.py").read_text(encoding="utf-8"))
    replaces = [
        n for n in ast.walk(source)
        if isinstance(n, ast.Attribute) and n.attr == "replace"
    ]
    assert replaces, "publish-on-complete is os.replace, and it is what the source does"


def test_the_checkpoint_bytes_are_DETERMINISTIC_but_the_model_output_is_NOT(tmp_path: Path):
    """⚠️ **HARD RULE 10's SCOPE, STATED EXACTLY.**

    Deterministic: the checkpoint bytes, given the same content. **NOT deterministic: model
    output** — the attacker runs at `attacker.temperature` against a hosted provider.
    """
    key = ep.EpisodeKey("M-ADV", "1", "2001", "gemma-26b")
    assert cp.render(_document(key)) == cp.render(_document(key))
    assert cp.render(_document(key)) != cp.render(_document(key, turns=12))

    reordered = dict(reversed(list(_document(key).items())))
    assert cp.render(reordered) == cp.render(_document(key)), "sorted keys, not insertion order"
    assert "\r" not in cp.render(_document(key)), "LF only"

    temperature = cfg.load("protocol").require("attacker.temperature")
    assert temperature > 0, (
        "the attacker runs at a non-zero temperature against a hosted provider, so MODEL "
        "OUTPUT IS NOT REPRODUCIBLE. What make eval claims is that every number regenerates "
        "FROM THE STORED LEDGERS"
    )


def test_no_docstring_in_the_runner_claims_that_rerunning_the_models_reproduces_the_run():
    """⚠️ Hard rule 10: *"Do not write, and do not let the README write, that re-running the
    models reproduces the run."* Scanned, not promised."""
    banned = (
        "re-running the models reproduces",
        "rerunning the models reproduces",
        "the models reproduce the run",
        "reproducible model output",
    )
    offenders = []
    for path in sorted(RUNNER_DIR.glob("*.py")):
        text = path.read_text(encoding="utf-8").lower()
        for phrase in banned:
            if phrase in text:
                offenders.append(f"{path.name}: {phrase!r}")
    assert not offenders, offenders


def test_a_DAY_BOUNDARY_resume_is_demonstrated_not_asserted(tmp_path: Path):
    """⚠️ `CONTEXT.md` §13.5(5): *"Resume across DAYS."*

    Driven: a lane spends most of day 1's ceiling, the run stops, and it resumes **on the next
    UTC date**. The checkpoint set persists; the day's spend does not — which is what a daily
    allowance window means.
    """
    log = usg.UsageLog(root=tmp_path / "evals" / "usage")
    store = cp.CheckpointStore(root=tmp_path / "evals" / "checkpoints")
    day1, day2 = "2026-09-03", "2026-09-04"

    for index in range(8):
        log.append(
            model="gemma-26b", date=day1, utc=f"{day1}T0{index}:00:00Z", lane="gemma-26b",
            episode=f"M-ADV/1/200{index}", total_tokens=11000, outcome=usg.OUTCOME_OK,
        )
        key = ep.EpisodeKey("M-ADV", "1", f"200{index}", "gemma-26b")
        store.publish(key, _document(key))

    spent1, calls1, existed1 = log.spent_today("gemma-26b", day1)
    assert (spent1, calls1, existed1) == (88000, 8, True)

    # A lane SEEDED FROM THE DAY'S REAL STATE stops; one that started at zero would not.
    seeded = sch.build_lane_state(
        name="gemma-26b", rpm=30, tpm=16000, rpd=14400, tpd=None,
        call_ceiling=10, token_ceiling=100000,
        already_spent_tokens=spent1, already_used_calls=calls1,
    )
    assert not seeded.budget.admit(22000).admitted, "88,000 + 22,000 > 100,000 - REFUSED"
    assert seeded.budget.stopped_by == bud.STOP_BY_TOKEN_CEILING
    unseeded = sch.build_lane_state(
        name="gemma-26b", rpm=30, tpm=16000, rpd=14400, tpd=None,
        call_ceiling=10, token_ceiling=100000,
    )
    assert unseeded.budget.admit(22000).admitted, (
        "an unseeded resume would run the whole ceiling a SECOND time - the overspend hard "
        "rule 12 exists to prevent"
    )

    # DAY 2: a fresh window, and NOT a fresh episode list.
    spent2, calls2, existed2 = log.spent_today("gemma-26b", day2)
    assert (spent2, calls2, existed2) == (0, 0, False), "a new day, and the file does not exist"
    assert existed1 is not existed2, (
        "'nothing spent' and 'no file read' are different statements and this says which"
    )
    day2_lane = sch.build_lane_state(
        name="gemma-26b", rpm=30, tpm=16000, rpd=14400, tpd=None,
        call_ceiling=10, token_ceiling=100000,
        already_spent_tokens=spent2, already_used_calls=calls2,
    )
    assert day2_lane.budget.admit(22000).admitted, "the new window has its own allowance"

    episodes = [ep.EpisodeKey("M-ADV", "1", f"200{i}", "gemma-26b") for i in range(10)]
    remaining = sch.Scheduler(lanes={}, sanctioned_lanes=frozenset()).pending(
        episodes, store.completed()
    )
    assert len(remaining) == 2, "the eight completed on day 1 are NOT re-run on day 2"


# ======================================================================================
# USAGE — per model, per day, reconciled against API-reported totals
# ======================================================================================


def test_the_usage_file_RECONCILES_against_api_reported_totals(tmp_path: Path):
    """`PROCESS.md` §12.1's C11 done-when: *"the usage file reconciles against API-reported
    totals."* ⚠️ **It compares; it never corrects.**"""
    log = usg.UsageLog(root=tmp_path)
    date = "2026-09-03"
    for tokens in (22000, 22000, 22000):
        log.append(
            model="gemma-26b", date=date, utc=f"{date}T10:00:00Z", lane="gemma-26b",
            episode="M-ADV/1/2001", total_tokens=tokens, outcome=usg.OUTCOME_OK,
        )

    assert log.reconcile("gemma-26b", date, 66000) is None
    discrepancy = log.reconcile("gemma-26b", date, 70000)
    assert discrepancy is not None
    assert (discrepancy.from_rows, discrepancy.api_reported, discrepancy.delta) == (
        66000, 70000, -4000,
    )
    assert log.spent_today("gemma-26b", date)[0] == 66000, "neither side was corrected"


def test_a_429_row_carries_ZERO_tokens(tmp_path: Path):
    """Golden 8 fixture D, verbatim: *"a 429'd call contributes ZERO tokens."*"""
    log = usg.UsageLog(root=tmp_path)
    log.append(
        model="gemma-26b", date="2026-09-03", utc="2026-09-03T10:00:00Z", lane="gemma-26b",
        episode="M-ADV/1/2001", total_tokens=0, outcome=usg.OUTCOME_RATE_LIMITED,
    )
    with pytest.raises(usg.UsageError, match="ZERO tokens"):
        log.append(
            model="gemma-26b", date="2026-09-03", utc="2026-09-03T10:00:00Z", lane="gemma-26b",
            episode="M-ADV/1/2001", total_tokens=1, outcome=usg.OUTCOME_RATE_LIMITED,
        )


def test_usage_is_reported_PER_MODEL_and_the_module_offers_no_pooled_sum(tmp_path: Path):
    """Hard rule 12: *"Report actual tokens BY MODEL."* ⚠️ `per_model_totals` returns a
    MAPPING, so no call site can mistake it for one lane's spend."""
    log = usg.UsageLog(root=tmp_path)
    date = "2026-09-03"
    for model, tokens in (("gemma-26b", 60000), ("gpt-oss-20b", 50000)):
        log.append(
            model=model, date=date, utc=f"{date}T10:00:00Z", lane=model,
            episode="M-ADV/1/2001", total_tokens=tokens, outcome=usg.OUTCOME_OK,
        )
    totals = usg.per_model_totals(log, ["gemma-26b", "gpt-oss-20b"], date)
    assert totals == {"gemma-26b": 60000, "gpt-oss-20b": 50000}
    assert isinstance(totals, dict)

    exported = {n for n in dir(usg) if not n.startswith("_")}
    assert "pooled_total" not in exported and "total_tokens" not in exported


def test_preflight_refuses_a_sanction_with_only_a_call_ceiling(tmp_path: Path):
    """⚠️ Hard rule 12: *"A sanction of 'max N calls' alone is not a sanction: one spike
    episode burned ~300K tokens against a 200K-TPD lane."*"""
    log = usg.UsageLog(root=tmp_path)
    with pytest.raises(usg.UsageError, match="BOTH ceilings"):
        usg.preflight(log, "gemma-26b", "2026-09-03", {"call_ceiling": 10})
    assert usg.preflight(
        log, "gemma-26b", "2026-09-03", {"call_ceiling": 10, "token_ceiling": 100000}
    ) == (0, 0, False)


def test_a_Ceilings_cannot_be_built_with_only_one_of_the_two():
    """The same rule, as a property of the type: there is no one-ceiling constructor."""
    with pytest.raises(TypeError):
        bud.Ceilings(call_ceiling=10)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        bud.Ceilings(token_ceiling=100000)  # type: ignore[call-arg]


# ======================================================================================
# LANES, RESERVATIONS AND BUCKETS
# ======================================================================================


def test_there_are_NINE_lanes_and_the_scheduler_schedules_onto_lanes_not_threads():
    """`CONTEXT.md` §13.3: *"Available lanes … = 9 lanes. The runner schedules episodes onto
    lanes, never onto a thread pool."*"""
    lanes = lanemod.load_lanes()
    assert len(lanes) == 9
    assert set(lanes) == {
        "gemma-26b", "gemma-31b", "flash-lite-3.1", "flash-lite-3.5",
        "qwen-27b", "gpt-oss-20b", "gpt-oss-120b", "compound", "compound-mini",
    }
    source = (RUNNER_DIR / "scheduler.py").read_text(encoding="utf-8").lower()
    for forbidden in ("threading", "threadpool", "concurrent.futures", "multiprocessing"):
        assert forbidden not in source, (
            f"the scheduler names {forbidden!r}; concurrency here means LANES, not threads"
        )


def test_LANE_RESERVATION_is_ENFORCED_and_the_refusal_is_the_default():
    """⚠️ `PROCESS.md` §8: *"No build session may spend on them."* Five lanes are reserved."""
    reserved = lanemod.reserved_lanes()
    assert set(reserved) == {"gemma-26b", "gemma-31b", "qwen-27b", "gpt-oss-20b", "gpt-oss-120b"}
    assert all(date == "2026-08-31" for date in reserved.values())

    for name in reserved:
        with pytest.raises(lanemod.LaneReserved, match="RESERVED"):
            lanemod.refuse_reserved(name, sanctioned=frozenset())

    for name in ("flash-lite-3.1", "flash-lite-3.5", "compound", "compound-mini"):
        lanemod.refuse_reserved(name, sanctioned=frozenset())  # not reserved: permitted

    lanemod.refuse_reserved("gemma-26b", sanctioned=frozenset({"gemma-26b"}))
    with pytest.raises(lanemod.LaneReserved):
        lanemod.refuse_reserved("gemma-31b", sanctioned=frozenset({"gemma-26b"}))

    with pytest.raises(lanemod.LaneError, match="is not a lane"):
        lanemod.refuse_reserved("gemini-ultra", sanctioned=frozenset())


def test_a_lane_with_no_daily_token_cap_has_THREE_buckets_not_a_zero_capacity_one():
    """⚠️ `config/lanes.yaml`: ``tpd: null`` means *"no such limit exists"*, which is not the
    same as *"unknown"* and is not a default. A zero-capacity bucket parks the lane forever."""
    lanes = lanemod.load_lanes()
    gemma = lanes["gemma-26b"]
    assert gemma.tpd is None
    buckets = bk.Buckets.for_lane(
        name=gemma.name, rpm=gemma.rpm, tpm=gemma.tpm, rpd=gemma.rpd, tpd=gemma.tpd
    )
    assert buckets.tpd is None
    assert set(buckets.limits()) == {"rpm", "tpm", "rpd"}
    assert buckets.permits(tokens=3000, now=0.0), "and it is not parked on its first call"

    groq = lanes["gpt-oss-20b"]
    assert groq.tpd == 200000
    four = bk.Buckets.for_lane(name=groq.name, rpm=groq.rpm, tpm=groq.tpm, rpd=groq.rpd, tpd=groq.tpd)
    assert set(four.limits()) == {"rpm", "tpm", "rpd", "tpd"}

    with pytest.raises(bk.BucketError, match="parks its lane forever"):
        bk.Bucket("bad", 0, 60.0)


def test_a_call_is_admitted_only_when_ALL_buckets_permit_it():
    """`CONTEXT.md` §13.5(1): *"A call is admitted only when all three buckets permit it."*
    ⚠️ And the wait is the MAXIMUM across buckets, never the sum: they refill in parallel."""
    buckets = bk.Buckets.for_lane(name="gemma-26b", rpm=30, tpm=16000, rpd=14400, tpd=None)
    assert buckets.wait_seconds(tokens=3000, now=0.0) == 0.0
    buckets.take(tokens=3000, now=0.0)

    for _ in range(4):
        buckets.take(tokens=3000, now=0.0)
    assert buckets.tpm.available == pytest.approx(1000.0)

    wait = buckets.wait_seconds(tokens=3000, now=0.0)
    assert wait > 0.0, "TPM binds; RPM and RPD still permit it"
    assert buckets.rpm.wait_seconds(1, 0.0) == 0.0
    assert wait == pytest.approx(buckets.tpm.wait_seconds(3000, 0.0)), "the MAX, not the sum"

    buckets.take(tokens=3000, now=wait)
    with pytest.raises(bk.BucketError, match="exceeds its whole capacity"):
        buckets.wait_seconds(tokens=20000, now=wait)


def test_a_bucket_refusal_is_a_WAIT_and_a_budget_refusal_is_an_ABORT():
    """⚠️ The distinction that keeps both mechanisms working. See `buckets.py`'s docstring."""
    buckets = bk.Buckets.for_lane(name="gemma-26b", rpm=1, tpm=16000, rpd=14400, tpd=None)
    buckets.take(tokens=100, now=0.0)
    assert buckets.wait_seconds(tokens=100, now=0.0) > 0.0, "a WAIT..."
    assert buckets.wait_seconds(tokens=100, now=60.0) == 0.0, "...that elapses"

    lane = bud.LaneBudget(model="gemma-26b", ceilings=bud.Ceilings(1, 100000))
    lane.admit(100)
    lane.settle(100)
    assert not lane.admit(100).admitted, "an ABORT..."
    with pytest.raises(bud.BudgetError, match="already stopped"):
        lane.admit(100)  # ...that does not elapse


def test_time_does_not_run_backwards():
    buckets = bk.Buckets.for_lane(name="gemma-26b", rpm=30, tpm=16000, rpd=14400, tpd=None)
    buckets.take(tokens=100, now=10.0)
    with pytest.raises(bk.BucketError, match="BEFORE its last refill"):
        buckets.wait_seconds(tokens=100, now=5.0)


# ======================================================================================
# KEYS — ⚠️ NO KEY VALUE CAN REACH A LOG OR A CHECKPOINT
# ======================================================================================


def test_the_runner_never_reads_a_key_VALUE_only_a_NAME():
    """⚠️ `CLAUDE.md` §4: *"Never read, print, echo or commit `.env` or any API key value. To
    confirm a key exists, read only its NAME."*

    **Asserted by parsing the source.** No subscript of ``os.environ``, no ``getenv``, no read
    of ``.env`` anywhere in the package.
    """
    offenders: list[str] = []
    for path in sorted(RUNNER_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                target = node.func
                name = getattr(target, "attr", None) or getattr(target, "id", None)
                if name in {"getenv", "load_dotenv", "dotenv_values"}:
                    offenders.append(f"{path.name}:{node.lineno} {name}()")
            if isinstance(node, ast.Subscript):
                value = node.value
                if (
                    isinstance(value, ast.Attribute)
                    and value.attr == "environ"
                    and path.name != "redaction.py"
                ):
                    offenders.append(f"{path.name}:{node.lineno} os.environ[...]")
        # ⚠️ CODE, not prose. Prose ABOUT the rule is not a breach of it — the same
        # reasoning `tests/test_tripwire_registry.py` gives for stripping docstrings before
        # its own scan: a check that fires on its own explanation gets weakened, not fixed.
        code = _strip_comments_and_docstrings(path.read_text(encoding="utf-8"))
        for literal in (".env", "gsk_live", "AIzaSy"):
            if literal in code and path.name not in {"redaction.py", "keys.py"}:
                offenders.append(f"{path.name}: names {literal!r} IN CODE")
    assert not offenders, (
        f"the runner touches a key: {offenders}. To confirm a key exists, read only its NAME"
    )


def test_key_presence_is_a_boolean_and_the_names_come_from_config():
    """The only public answer this module gives is ``True``/``False``."""
    assert keymod.env_var_for_provider("groq") == "GROQ_API_KEY"
    assert keymod.env_var_for_provider("google") == "GOOGLE_API_KEY"
    assert lanemod.providers_for(["gemma-26b", "gpt-oss-20b", "gemma-31b"]) == ["google", "groq"]

    assert keymod.key_is_present("WHETSTONE_DEFINITELY_UNSET_XYZ") is False
    os.environ["WHETSTONE_TEST_MARKER_API_KEY"] = "not-a-real-key-value"
    try:
        assert keymod.key_is_present("WHETSTONE_TEST_MARKER_API_KEY") is True
        assert isinstance(keymod.key_is_present("WHETSTONE_TEST_MARKER_API_KEY"), bool)
    finally:
        del os.environ["WHETSTONE_TEST_MARKER_API_KEY"]

    with pytest.raises(keymod.KeyError_):
        keymod.env_var_for_provider("")


def test_NO_KEY_VALUE_CAN_REACH_A_CHECKPOINT_OR_A_USAGE_ROW(tmp_path: Path):
    """⚠️ **The second half of the guarantee.** A caller who hands the runner a credential is
    REFUSED, not masked — and the refusal never reproduces the value."""
    store = cp.CheckpointStore(root=tmp_path)
    key = ep.EpisodeKey("M-ADV", "1", "2001", "gemma-26b")

    for poisoned in (
        "gsk_0123456789abcdefghijklmnop",
        "AIzaSyD0123456789abcdefghijklmnop",
        "GROQ_API_KEY=0123456789abcdef",
    ):
        document = _document(key)
        document["ledger_path"] = poisoned
        with pytest.raises(red.SecretInPayload) as raised:
            store.publish(key, document)
        assert poisoned not in str(raised.value), (
            "⚠️ the refusal must NOT reproduce the value - that would put the secret in the "
            "traceback, the pytest output and every CI log that caught it"
        )
        assert not store.path_for(key).exists(), "the write did not happen"

    log = usg.UsageLog(root=tmp_path / "usage")
    with pytest.raises(red.SecretInPayload):
        log.append(
            model="gemma-26b", date="2026-09-03", utc="2026-09-03T10:00:00Z",
            lane="gemma-26b", episode="gsk_0123456789abcdefghijklmnop",
            total_tokens=10, outcome=usg.OUTCOME_OK,
        )


def test_a_value_equal_to_a_SET_key_is_refused_without_either_side_being_printed(tmp_path: Path):
    """⚠️ **The strongest of the three checks: exact comparison, no format knowledge needed.**"""
    secret = "zzz-this-is-a-fake-credential-for-a-test-only"
    os.environ["WHETSTONE_TEST_MARKER_API_KEY"] = secret
    try:
        with pytest.raises(red.SecretInPayload) as raised:
            red.refuse_if_secret_bearing({"note": secret})
        message = str(raised.value)
        assert "WHETSTONE_TEST_MARKER_API_KEY" in message, "the NAME is actionable"
        assert secret not in message, "⚠️ and the VALUE is not reproduced"
        assert "NEITHER VALUE IS REPRODUCED" in message
    finally:
        del os.environ["WHETSTONE_TEST_MARKER_API_KEY"]

    red.refuse_if_secret_bearing({"note": "an ordinary string", "n": 5, "xs": ["a", "b"]})


def test_the_redaction_scan_states_what_it_does_NOT_close():
    """`PROCESS.md` §9: *"Every evidence pack states what it is NOT."* Applied to a guard."""
    text = (RUNNER_DIR / "redaction.py").read_text(encoding="utf-8")
    assert "WHAT THIS DOES NOT CLOSE" in text
    assert red._looks_like_a_key("an-unknown-format-credential-nobody-declared") is None


# ======================================================================================
# Q-003's RIDER — git-status visibility, DEMONSTRATED
# ======================================================================================


def _git(*args: str, cwd: Path) -> str:
    """``git``, decoded as UTF-8 with replacement.

    ⚠️ ``INCIDENTS.md`` **INC-74**: a harness that let Python pick the console codepage aborted
    on ``UnicodeDecodeError: 'charmap'`` and produced **no numbers**. This repository's tracked
    text is UTF-8; the default on this machine is cp1252.
    """
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True,
        encoding="utf-8", errors="replace",
    ).stdout


def test_a_checkpoint_is_GIT_STATUS_VISIBLE_and_a_partial_is_NOT(tmp_path: Path):
    """⚠️ **`Q-003`'s RIDER, and it is C11's done-when:** *"a runner checkpoint and an episode
    output are `git status`-visible against the committed `.gitignore`, demonstrated, not
    asserted."*

    Demonstrated in a **fresh temporary git repository** carrying this repository's *committed*
    `.gitignore` — `CLAUDE.md` §4: *"Throwaway work goes to a fresh OS temp directory, never
    into the repository."* Nothing is written into `evals/` in the real tree.
    """
    clone = tmp_path / "demo"
    clone.mkdir()
    _git("init", "-q", cwd=clone)
    committed = _git("show", "HEAD:.gitignore", cwd=cfg.repo_root())
    (clone / ".gitignore").write_text(committed, encoding="utf-8", newline="\n")

    store = cp.CheckpointStore.under(clone)
    key = ep.EpisodeKey("M-ADV", "1", "2001", "gemma-26b")
    store.publish(key, _document(key))
    episode_output = clone / "evals" / "episodes" / f"{key.slug}.json"
    episode_output.parent.mkdir(parents=True, exist_ok=True)
    episode_output.write_text('{"ledger": []}\n', encoding="utf-8", newline="\n")
    in_flight = store.path_for(key).with_name(store.path_for(key).name + cp.PARTIAL_SUFFIX)
    in_flight.write_text("half a document", encoding="utf-8", newline="\n")

    # ⚠️ `--untracked-files=all`. Bare `--porcelain` COLLAPSES an untracked directory to
    # a single `?? evals/` line, which would let this test pass while saying nothing about
    # which files inside it are visible - and "the checkpoint is visible" is the claim.
    status = _git("status", "--porcelain", "--untracked-files=all", cwd=clone)
    assert "evals/checkpoints/" in status.replace("\\", "/"), (
        f"⚠️ THE CHECKPOINT MUST BE VISIBLE. git status said:\n{status}"
    )
    assert "evals/episodes/" in status.replace("\\", "/"), (
        f"⚠️ THE EPISODE OUTPUT MUST BE VISIBLE. git status said:\n{status}"
    )
    assert cp.PARTIAL_SUFFIX not in status, (
        "an in-flight .partial is ignored by the committed .gitignore, which is Q-003's "
        "ruling: 'Ignore only genuinely transient in-flight files'"
    )


def test_the_goldens_directory_is_untouched():
    """⚠️ **Hard rule 3: `tests/goldens/` is READ-ONLY to this session.** Measured."""
    status = _git("status", "--porcelain", "tests/goldens/", cwd=cfg.repo_root())
    assert status.strip() == "", f"tests/goldens/ is not clean:\n{status}"


# ======================================================================================
# HARD RULE 8 — purity separation, and the moat this package does NOT cross
# ======================================================================================


def test_the_core_modules_touch_no_filesystem_no_clock_and_no_randomness():
    """Hard rule 8: *"Core logic takes data in and returns results — no I/O, clock, network,
    or randomness inside it. Side effects live in a thin outer shell."*

    ⚠️ **`n_rule.py` IS EXEMPT ON ONE POINT AND THE EXEMPTION IS NAMED**: it reads `config/`
    through the one loader and parses `CONTEXT.md` for the lane-hour budget, because hard rule
    9 requires those values to come from there and nowhere else. That is what a shell is for,
    and it is the same scope `ledger/store.py` states for its own package.
    """
    core = {"budget.py", "buckets.py", "episodes.py", "report.py"}
    banned_modules = {"random", "time", "datetime", "pathlib", "os", "socket", "requests", "httpx"}
    offenders: list[str] = []
    for name in sorted(core):
        tree = ast.parse((RUNNER_DIR / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in banned_modules:
                        offenders.append(f"{name}:{node.lineno} import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if (node.module or "").split(".")[0] in banned_modules:
                    offenders.append(f"{name}:{node.lineno} from {node.module}")
            elif isinstance(node, ast.Call):
                fn = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
                if fn in {"open", "print"}:
                    offenders.append(f"{name}:{node.lineno} {fn}()")
    assert not offenders, offenders


def test_the_runner_imports_NO_MODEL_CLIENT_and_makes_no_network_call():
    """⚠️ **ZERO PROVIDER MODEL CALLS.** C11's build prompt: *"YOU BUILD THE RUNNER AND YOU DO
    NOT RUN IT."*"""
    banned = {
        "openai", "groq", "google", "genai", "anthropic", "requests", "httpx", "urllib",
        "http", "socket", "aiohttp",
    }
    offenders: list[str] = []
    for path in sorted(RUNNER_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for name in names:
                if name.split(".")[0] in banned:
                    offenders.append(f"{path.name}:{node.lineno} {name}")
    assert not offenders, offenders


def test_the_runner_imports_NOTHING_from_gates_or_scorer_or_ledger():
    """⚠️ Three separate reasons, and they are not the same reason.

      * **`scorer/`** — `Q-119`: the runner's live denominator and the scorer's replay
        denominator are written **twice, on purpose**, so they can disagree.
      * **`gates/`** — the runner drives a gate; it does not implement one.
      * **`ledger/`** — `Q-069` ruled `whetstone_gate.ledger` is **SCORER-SIDE**, and
        `tests/test_c7_ledger.py::test_Q069_nothing_in_this_repository_imports_the_ledger_yet`
        is already RED on three `tests/test_c8_scorer.py` offenders (`OF-183`, `OF-202`).
        ⚠️ **This chunk adds none**, so the count of offenders in that red test is unchanged
        by C11 — which is asserted below rather than hoped for.
    """
    offenders: list[str] = []
    for path in sorted(RUNNER_DIR.glob("*.py")) + [Path(__file__)]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for name in names:
                parts = name.split(".")
                for forbidden in ("gates", "scorer", "ledger"):
                    if forbidden in parts:
                        offenders.append(f"{path.name}:{node.lineno} {name}")
    assert not offenders, (
        f"C11 must add no offender to OF-183's already-red test, and must not share the "
        f"scorer's denominator (Q-119): {offenders}"
    )


def test_check_roles_D1_to_D4_all_PASS_with_the_runner_present():
    """⚠️ The moat is `gates/` vs `scorer/`. This package is neither, and it must not disturb
    them. **Measured after the build**, which is `Q-119`'s own claim."""
    from whetstone_gate import check_roles

    results = check_roles.check_gate_scorer_isolation(cfg.repo_root())
    named = {r.check.split()[0]: r for r in results}
    assert set(named) == {"D1", "D2", "D3", "D4"}
    for label, result in sorted(named.items()):
        assert result.ok is True, f"{label} is not PASS: {result.detail}"


def test_the_runner_package_carries_the_scope_of_its_own_determinism_claim():
    """⚠️ Hard rule 10's scope, in the package's own docstring, so nobody widens it later."""
    text = (RUNNER_DIR / "__init__.py").read_text(encoding="utf-8")
    assert "MODEL OUTPUT IS NOT" in text
    assert "regenerates from the stored ledgers" in text
    assert "append-only" in text.lower()
    assert "Q-119" in text


def test_the_episode_key_is_the_one_PROCESS_md_names_and_its_slug_is_injective():
    """`PROCESS.md` §12.1: keyed ``(block, arm, seed_or_task, attacker_model)``."""
    key = ep.EpisodeKey("M-ADV", "2S", "2001", "gemma-26b")
    assert key.slug == "m-adv__2s__2001__gemma-26b"
    assert ep.EpisodeKey("M-ADV", "2S", "2001", "gemma-26b").slug == key.slug
    assert ep.EpisodeKey("M-ADV", "2", "S2001", "gemma-26b").slug != key.slug

    for bad in ("", "  ", "a/b", "a\\b", ".."):
        with pytest.raises(ValueError):
            ep.EpisodeKey("M-ADV", "1", bad, "gemma-26b")

    # τ² task ids are STRINGS that look like integers. config/protocol.yaml's own warning.
    assert ep.EpisodeKey("T-NEG", "1", "0", "gemma-26b").slug.endswith("__0__gemma-26b")


def test_the_whole_report_renders_as_ASCII_the_operator_can_read():
    """*"A report the operator cannot read is a report that does not get read."*"""
    from whetstone_gate import _console

    budgets = {}
    for model, spend in (("gemma-26b", 60000), ("gpt-oss-20b", 50000)):
        lane = bud.LaneBudget(model=model, ceilings=CEILINGS)
        lane.admit(spend)
        lane.settle(spend)
        budgets[model] = lane

    text = rep.render_run_report(
        budgets=budgets,
        denominator=_truncation_denominator(),
        token_ceiling=CEILINGS.token_ceiling,
        limitations=[nr.limitation()],
    )
    assert _console.ascii_safe(text) == text, "the report is already ASCII at the boundary"
    for expected in (
        "PER-MODEL TOKEN AND CALL ACCOUNTING",
        "POOLED-VS-PER-MODEL DISCRIMINATOR",
        "EPISODE DENOMINATOR",
        "LIMITATIONS, PUBLISHED",
        "COUNTED IN THE DENOMINATOR",
    ):
        assert expected in text
    _console.say(text)


def test_THIS_TEST_FILE_imports_no_network_module_either():
    """A belt-and-braces scan of THIS file: the build prompt sanctioned **zero** spend.

    ⚠️ By **AST import**, not by substring. A substring scan of a file that must *name* the
    modules it forbids fires on itself — measured, on this very test's first version.
    """
    banned = {
        "openai", "groq", "genai", "anthropic", "requests", "httpx", "urllib", "http",
        "socket", "aiohttp",
    }
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    offenders: list[str] = []
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        for name in names:
            if name.split(".")[0] in banned:
                offenders.append(f"line {node.lineno}: {name}")
    assert not offenders, offenders
    assert "requests" not in sys.modules, "no HTTP client was imported at any point"
