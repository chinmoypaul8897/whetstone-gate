"""**THE TWO-CEILING ACCUMULATOR. Hard rule 12, and golden 8 is its oracle.**

`CLAUDE.md` hard rule 12, and `PROCESS.md` §8, verbatim on the four clauses golden 8
transcribes:

    **EVERY SANCTION CARRIES A TOKEN CEILING, NOT ONLY A CALL CEILING.** … one episode
    burned ~300K tokens against a 200K-TPD lane: twenty sanctioned calls can cost a whole
    day. … **The session reads `evals/usage/<model>-<date>.jsonl` before its first call,
    aborts at whichever ceiling it hits first, and reports actual tokens by model.**

    **A 429 MEANS THE WINDOW IS ALREADY SPENT: STOP and report — never retry into another
    lane.** (The *runner* backs off and re-queues within its own lane; a *session* does not.)

**PURE.** No I/O, no clock, no network, no randomness. Every value in this module arrives as
an argument and every result is returned.

--------------------------------------------------------------------------------------
⚠️ THE ADMISSION TEST IS PROSPECTIVE, AND THE READING IS THE ARCHITECT'S
--------------------------------------------------------------------------------------

Golden 8, `fixture_ceilings.why_the_admission_test_is_PROSPECTIVE`, verbatim:

    Hard rule 12 says ABORT, not 'overspend and then abort'. The cost t is the call's OWN
    measured usage, so an accumulator that admits first and checks afterwards has already
    spent past the ceiling by the time it stops — which is precisely the failure the rule's
    own example records (~300K tokens against a 200K-TPD lane).

So the rule is, exactly:

    A call costing t tokens is ADMITTED iff
        calls_used + 1 <= call_ceiling  AND  tokens_spent + t <= token_ceiling.
    The lane STOPS on the first refusal — it does not skip the offending call and continue.

⚠️ **BOTH CEILINGS ARE INCLUSIVE.** A call that lands the lane **exactly** on a ceiling is
legal; the next token and the next call are not. Written with ``>=`` instead of ``>``, golden
8 fixture C part 1 refuses the second 50,000-token call and reports 50,000 spent, **leaving
half the sanctioned budget unusable**. Inclusiveness is therefore not a flag on this class —
there is no exclusive mode to configure, because an exclusive mode would be wrong.

--------------------------------------------------------------------------------------
⚠️ HOW A PROSPECTIVE TEST IS RUN AGAINST A COST THAT IS ONLY KNOWN AFTERWARDS
--------------------------------------------------------------------------------------

**Stated rather than left as a hole, because it is the one place the fixture's framing and a
live provider come apart.** Golden 8's fixtures hand the accumulator a list of *offered*
costs and ask what it admits — the cost is given. Against a live provider it is not: a call's
`usage.total_tokens` exists only after the call returns.

The live path therefore runs in two steps and **neither of them estimates the accounting**:

  1. :meth:`LaneBudget.admit` is called with a **RESERVATION** — a declared worst-case cost
     for one call, supplied by the caller from `config/` (`gate_judge.target_tokens_per_call`
     for a judge call; the per-episode target divided across the turn budget for an attacker
     call). This is the prospective abort, and because a reservation is an **upper** bound it
     can only make the lane stop **earlier**, never later.
  2. :meth:`LaneBudget.settle` is called with the API's own `usage.total_tokens`, and **that**
     is what is accounted. The reservation is never accounted and never reported.

⚠️ **AND THE GAP BETWEEN THEM IS A COUNTED NUMBER, NOT A SILENCE.** If a settled cost exceeds
its reservation the lane is stopped by :attr:`STOP_BY_RESERVATION_SHORTFALL` and the overrun
is carried on :attr:`LaneBudget.reservation_shortfall_tokens`, so *"the ceiling was crossed by
at most one call's overrun"* is a figure a reader can see rather than a claim a reader must
take. A reservation that is honest makes this zero; a reservation that is not is visible.

**Golden 8's fixtures A–F drive :meth:`admit` and :meth:`settle` with the same number**, which
is the fixture's own framing (*"the cost t is the call's OWN measured usage"*), so this
module's extra step costs the oracle nothing.

--------------------------------------------------------------------------------------
⚠️ THE 429, AND THE TWO LEVELS IT IS TRUE AT
--------------------------------------------------------------------------------------

Golden 8 fixture D: a 429 at call 2 leaves the lane with **1,000 tokens spent, 99,000 unspent
and NINE of ten calls unused**, `stopped_by: "429"`, `retried: false`, `other_lane_used:
false`. A 429'd call contributes **zero** tokens and consumes **no** call — the request was
refused by the rate limiter and never ran, which is why nine calls are unused rather than
eight.

    ! THE LANE STOPS WITH 99,000 OF 100,000 TOKENS AND 9 OF 10 CALLS UNUSED, AND THAT IS
    CORRECT BEHAVIOUR RATHER THAN WASTE. An accumulator that retries, or that spills into
    another model's lane to use the remaining budget, produces a HIGHER number here and
    violates hard rule 12 to do it.

**This class is the SESSION-level rule: it stops.** The re-queue lives one level up, in
:mod:`.scheduler`, is **lane-internal**, and never crosses into another model's budget —
golden 8's own `runner_versus_session` note draws exactly that line.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

# --------------------------------------------------------------------------------------
# Stop reasons. Golden 8's own strings where golden 8 states one, so a report and the answer
# key read the same way and a diff between them is a string comparison rather than a
# translation exercise.
# --------------------------------------------------------------------------------------

#: Golden 8 fixtures A and C part 1: ``"stopped_by": "token ceiling"``.
STOP_BY_TOKEN_CEILING = "token ceiling"

#: Golden 8 fixtures B and C part 2: ``"stopped_by": "call ceiling"``.
STOP_BY_CALL_CEILING = "call ceiling"

#: Golden 8 fixture D: ``"stopped_by": "429"``.
STOP_BY_429 = "429"

#: ⚠️ **NOT A GOLDEN 8 STRING.** This module's own, for the one condition golden 8's framing
#: does not produce because its fixtures hand the accumulator the true cost: a settled cost
#: that exceeded the reservation it was admitted against. Named distinctly so nobody reads it
#: as an architect-stated outcome.
STOP_BY_RESERVATION_SHORTFALL = "reservation shortfall"

#: Every reason a lane can stop, in print order. **Declared**, so a report can print each one
#: as a number including the zeros — `OF-03`'s doctrine: an absent line and a zero are not the
#: same statement.
STOP_REASONS: tuple[str, ...] = (
    STOP_BY_TOKEN_CEILING,
    STOP_BY_CALL_CEILING,
    STOP_BY_429,
    STOP_BY_RESERVATION_SHORTFALL,
)


class BudgetError(RuntimeError):
    """The accumulator was asked for something hard rule 12 forbids. Always a refusal."""


# --------------------------------------------------------------------------------------
# Reading the provider's own usage block
# --------------------------------------------------------------------------------------


def usage_total_tokens(usage: Mapping[str, Any]) -> int:
    """Return ``usage.total_tokens``. **And nothing else.**

    Golden 8, `recorded_api_response.what_the_accumulator_reads`, verbatim:

        usage.total_tokens, and nothing else. ! IT DOES NOT ADD prompt_tokens AND
        completion_tokens ITSELF: providers differ on whether total_tokens includes
        reasoning or cached-read tokens, so a reconstructed total can silently disagree
        with the one the provider bills.

    So a block **without** ``total_tokens`` is a **refusal**, never a reconstruction from the
    two parts that happen to be present. Hard rule 9's shape applied to a provider reply:
    a missing required value is a hard refusal, never a silent fallback.

    Integer only. A float token count is not a token count.
    """
    if "total_tokens" not in usage:
        raise BudgetError(
            "the provider's usage block carries no 'total_tokens'. It is NOT reconstructed "
            "from prompt_tokens + completion_tokens: providers differ on whether the total "
            "includes reasoning or cached-read tokens, so a reconstructed total can silently "
            "disagree with the one the provider bills, and golden 8 says this accumulator "
            f"reads total_tokens 'and nothing else'. Got keys: {sorted(usage)}"
        )
    value = usage["total_tokens"]
    if isinstance(value, bool) or not isinstance(value, int):
        raise BudgetError(
            f"usage.total_tokens must be an integer token count; got {value!r} "
            f"({type(value).__name__}). Golden 8: 'Integer tokens throughout; there is no "
            f"float in this file.'"
        )
    if value < 0:
        raise BudgetError(f"usage.total_tokens must not be negative; got {value}")
    return value


# --------------------------------------------------------------------------------------
# The ceilings and the admission verdict
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Ceilings:
    """One lane's sanctioned ceilings. **Both are required and both are inclusive.**

    ⚠️ There is no constructor that takes only one of them. Hard rule 12: *"A sanction of
    'max N calls' alone is not a sanction"* — and a sanction of max T tokens alone is not one
    either, which is golden 8 fixture B's whole point. Making one optional here would put the
    unsanctioned case one keyword argument away.
    """

    call_ceiling: int
    token_ceiling: int

    def __post_init__(self) -> None:
        for name, value in (
            ("call_ceiling", self.call_ceiling),
            ("token_ceiling", self.token_ceiling),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise BudgetError(f"{name} must be an integer; got {value!r}")
            if value < 0:
                raise BudgetError(f"{name} must not be negative; got {value}")


@dataclass(frozen=True)
class Admission:
    """The prospective verdict on one offered call, and **why**.

    ``refused_by`` is ``None`` when admitted, and otherwise one of
    :data:`STOP_BY_CALL_CEILING` / :data:`STOP_BY_TOKEN_CEILING`.

    ⚠️ **When BOTH ceilings would be breached, the CALL ceiling is reported.** Stated because
    it is arbitrary and a reader is entitled to know it was chosen rather than fallen into:
    the call ceiling is the one that does not depend on the offered cost, so it is the stabler
    of the two to report, and golden 8 has no fixture in which both bind at once. Either
    answer stops the lane at the same instant and no fixture's expected value moves.
    """

    admitted: bool
    refused_by: str | None
    calls_after: int
    tokens_after: int


# --------------------------------------------------------------------------------------
# The accumulator itself — PER MODEL, NEVER POOLED
# --------------------------------------------------------------------------------------


@dataclass
class LaneBudget:
    """One model's call and token accounting. **Ceilings are per model and never pooled.**

    Golden 8 fixture E: `gemma-26b` at 60,000 and `gpt-oss-20b` at 50,000 pool to **110,000**,
    which is over a 100,000 ceiling, while **neither exceeds it alone** — and the correct
    outcome is *"BOTH LANES CONTINUE"*. A pooling accumulator aborts a lane that has budget.
    This class holds **one model's** figures and has no field, method or constructor that can
    add a second model's, so pooling is not a bug this class can have — it is a shape a caller
    would have to build on purpose, and :func:`.report.per_model_lines` is what prints the
    per-model breakdown hard rule 12 requires (*"Report actual tokens BY MODEL"*).

    Mutable on purpose: it accumulates across a lane's window. It holds no predicate logic
    beyond the admission rule, which is the thing it exists to be.
    """

    model: str
    ceilings: Ceilings
    calls_used: int = 0
    tokens_spent: int = 0
    stopped_by: str | None = None

    #: 429s seen. They cost **no** call and **no** token; the count exists so a report can
    #: show that the lane stopped because the window was spent, not because it ran dry.
    rate_limited: int = 0

    #: ⚠️ Settled minus reserved, when a settled cost exceeded its reservation. See this
    #: module's docstring. Zero when every reservation was honest.
    reservation_shortfall_tokens: int = 0

    #: The reservation the most recent :meth:`admit` was granted against, or ``None``.
    _pending_reservation: int | None = None

    # -- what a reader gets ------------------------------------------------------------

    @property
    def calls_unused(self) -> int:
        """Golden 8's ``calls_unused``. ⚠️ **The unspent budget is the point** (fixture D)."""
        return self.ceilings.call_ceiling - self.calls_used

    @property
    def tokens_unspent(self) -> int:
        """Golden 8's ``tokens_unspent``. What a correct implementation LEAVES ON THE TABLE."""
        return self.ceilings.token_ceiling - self.tokens_spent

    @property
    def stopped(self) -> bool:
        return self.stopped_by is not None

    # -- the prospective admission rule ------------------------------------------------

    def admit(self, cost: int) -> Admission:
        """Prospective verdict on a call costing ``cost`` tokens. **Does not spend.**

        ⚠️ A **refusal STOPS the lane** — golden 8: *"The lane STOPS on the first refusal - it
        does not skip the offending call and continue."* An accumulator that skipped the
        offending call and took the next cheaper one would run past a ceiling it had already
        been told about, one small call at a time.
        """
        if isinstance(cost, bool) or not isinstance(cost, int):
            raise BudgetError(f"an offered cost must be an integer; got {cost!r}")
        if cost < 0:
            raise BudgetError(f"an offered cost must not be negative; got {cost}")
        if self.stopped:
            raise BudgetError(
                f"lane {self.model!r} has already stopped ({self.stopped_by!r}) and may not "
                f"be offered another call. Hard rule 12: a stopped lane STOPS and reports"
            )

        calls_after = self.calls_used + 1
        tokens_after = self.tokens_spent + cost

        if calls_after > self.ceilings.call_ceiling:
            self.stopped_by = STOP_BY_CALL_CEILING
            return Admission(False, STOP_BY_CALL_CEILING, self.calls_used, self.tokens_spent)
        if tokens_after > self.ceilings.token_ceiling:
            self.stopped_by = STOP_BY_TOKEN_CEILING
            return Admission(False, STOP_BY_TOKEN_CEILING, self.calls_used, self.tokens_spent)

        self._pending_reservation = cost
        return Admission(True, None, calls_after, tokens_after)

    # -- accounting, from the provider's own number ------------------------------------

    def settle(self, actual_tokens: int) -> None:
        """Account one admitted call at the API's **own** ``usage.total_tokens``.

        ⚠️ **NEVER an estimate.** The caller obtains ``actual_tokens`` from
        :func:`usage_total_tokens` over the provider's reply.
        """
        if self._pending_reservation is None:
            raise BudgetError(
                f"lane {self.model!r}: settle() with no admitted call outstanding. A call is "
                f"admitted BEFORE it is made (hard rule 12 says ABORT, not 'overspend and "
                f"then abort'), and settled from the provider's own usage afterwards"
            )
        if isinstance(actual_tokens, bool) or not isinstance(actual_tokens, int):
            raise BudgetError(f"actual_tokens must be an integer; got {actual_tokens!r}")
        if actual_tokens < 0:
            raise BudgetError(f"actual_tokens must not be negative; got {actual_tokens}")

        reserved = self._pending_reservation
        self._pending_reservation = None
        self.calls_used += 1
        self.tokens_spent += actual_tokens

        if actual_tokens > reserved:
            self.reservation_shortfall_tokens += actual_tokens - reserved
            if self.tokens_spent > self.ceilings.token_ceiling:
                self.stopped_by = STOP_BY_RESERVATION_SHORTFALL

    def record_429(self) -> None:
        """A 429, **at the SESSION level**: zero tokens, zero calls, and the lane **STOPS**.

        ⚠️ **THIS IS GOLDEN 8 FIXTURE D's ORACLE.** `PROCESS.md` §8 and `CLAUDE.md` §4:
        *"A 429 MEANS THE WINDOW IS ALREADY SPENT: STOP and report — never retry into another
        lane."* Nine of ten calls and 99,000 of 100,000 tokens are left unused **and that is
        correct behaviour rather than waste**: an accumulator that retries, or that spills
        into another model's lane to use the remaining budget, produces a HIGHER number here
        and violates hard rule 12 to do it.

        ⚠️ **THE RUNNER'S RULE IS DIFFERENT AND IT IS A DIFFERENT METHOD —**
        :meth:`record_429_requeued_in_lane`. Golden 8 fixture D's own `runner_versus_session`
        note draws the line: *"The RUNNER backs off with jitter and re-queues WITHIN ITS OWN
        LANE, and a 429 storm parks the lane. A SESSION stops and reports."* Two rules, two
        methods, each named for the level it belongs to — rather than one method with a flag,
        which is how the session rule would eventually be switched off by a caller in a hurry.
        """
        self._record_rate_limit()
        self.stopped_by = STOP_BY_429

    def record_429_requeued_in_lane(self) -> None:
        """A 429, **at the RUNNER level**: zero tokens, zero calls, and the lane is **NOT
        stopped** — the episode is re-queued **within this lane** and the caller backs off.

        `CONTEXT.md` §13.5(3): *"429 is backoff-and-resume, never failure. Exponential backoff
        with jitter, capped; the episode is re-queued, not marked failed. A 429 storm parks
        that lane and the scheduler moves to another."*

        ⚠️ **IT STILL SPENDS NOTHING AND IT STILL CANNOT REACH ANOTHER LANE.** This object
        holds exactly one model's figures; there is no argument here that names a destination,
        so *"never retry into another lane"* is a property of the type rather than a rule a
        caller must remember. Parking and backoff are :mod:`.scheduler`'s — a budget does not
        own a clock (hard rule 8).
        """
        self._record_rate_limit()

    def _record_rate_limit(self) -> None:
        """The half both 429 paths share: **zero tokens, zero calls, one counted refusal.**

        Golden 8 fixture D, verbatim: *"a 429'd call contributes ZERO tokens. It also consumes
        NO call - the request was refused by the rate limiter and never ran, which is why NINE
        calls are unused rather than eight."*
        """
        if self.stopped:
            raise BudgetError(
                f"lane {self.model!r} has already stopped ({self.stopped_by!r})"
            )
        self._pending_reservation = None
        self.rate_limited += 1

    # -- the golden-8 state block ------------------------------------------------------

    def state(self) -> dict[str, Any]:
        """The accumulator state, in **golden 8's own field names**.

        Field-for-field with the golden's ``accumulator_state_after_it`` and every fixture's
        ``expected`` block, so a test compares dictionaries rather than translating names —
        and a rename on either side is a failing test rather than a quiet mismatch.
        """
        return {
            "calls_used": self.calls_used,
            "calls_unused": self.calls_unused,
            "tokens_spent": self.tokens_spent,
            "tokens_unspent": self.tokens_unspent,
            "stopped_by": self.stopped_by,
        }


def run_offers(model: str, ceilings: Ceilings, offers: list[int]) -> LaneBudget:
    """Drive ``offers`` through a fresh :class:`LaneBudget` until it stops. **Pure.**

    This is golden 8's fixtures A, B and C in one function: each offered cost is admitted
    prospectively and, if admitted, settled at that same cost — which is the fixtures' own
    framing, *"the cost t is the call's OWN measured usage"*.

    Returns the budget in whatever state it reached. It does **not** raise on a refusal: a
    refusal is the answer being measured, not an error.
    """
    budget = LaneBudget(model=model, ceilings=ceilings)
    for cost in offers:
        if not budget.admit(cost).admitted:
            break
        budget.settle(cost)
    return budget
