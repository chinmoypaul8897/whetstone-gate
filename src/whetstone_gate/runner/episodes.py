"""**THE EPISODE KEY, THE OUTCOME VOCABULARY, AND THE DENOMINATOR. Hard rule 11.**

`CLAUDE.md` hard rule 11, verbatim, and it is Razorpay's own B.9:

    **NO SILENT DENOMINATOR SHRINKAGE.** Razorpay's own B.9: *"Score complete trials only.
    Do not let retries, fallbacks, skipped cases, or missing traces quietly shrink the
    denominator."* Every dropped episode is counted, categorised and printed as a number.
    **A truncated episode is counted in the denominator.**

**PURE.** No I/O, no clock, no network, no randomness.

--------------------------------------------------------------------------------------
⚠️ TRUNCATION IS NOT A DROP, AND THAT IS THE WHOLE POINT
--------------------------------------------------------------------------------------

A **truncated** episode is one that started, ran, produced a ledger, and stopped before its
turn budget was exhausted — against a ceiling, against a 429, or because the operator
interrupted it. Rule 11 says it is **counted in the denominator**, so here it is:

  * ``attempted``  — every episode the runner was asked to run.
  * ``completed``  — ran to its turn budget.
  * ``truncated``  — ran, stopped early, **counted in the denominator alongside completed**.
  * ``not_started`` — never dispatched at all, categorised by cause.

and the identity that can fail is

    ``attempted == completed + truncated + not_started``

refused by :meth:`RunDenominator.reconcile` rather than assumed. **A counter that cannot
disagree with itself has measured nothing** — `scorer/drops.py`'s own sentence, and the one
piece of its reasoning this module deliberately keeps while sharing none of its code
(`QUESTIONS.md` **Q-119**).

⚠️ **FILING TRUNCATION UNDER "not_started" WOULD BE THE EXACT SHRINKAGE RULE 11 FORBIDS,
WEARING THE RULE'S OWN CLOTHES**, so ``denominator`` is ``completed + truncated`` and there is
no method on this class that removes a truncated episode from it.

⚠️ **A TRUNCATED EPISODE'S TOKEN COST IS NOT ZERO**, and it is carried per episode rather than
inferred. `QUESTIONS.md` **Q-108** names *(a) its token cost, which is not zero, (b) its
category, and (c) its presence in the denominator* as the three things golden 8's missing
seventh fixture would have had to state; all three are fields here. **Golden 8 carries no
truncated-episode case at all** — see `Q-108` and `Q-117`, both **OPEN**. The vectors that
exercise this module's truncation arithmetic are in `tests/test_c11_runner.py` and are **this
session's own**, which is a weaker oracle than the architect's and is marked as one wherever
it is used.

--------------------------------------------------------------------------------------
⚠️ THE CAUSE VOCABULARY IS THE LIVE SIDE'S, NOT THE SCORER'S
--------------------------------------------------------------------------------------

These causes answer *"why did this episode not finish"*. `scorer/drops.py`'s categories answer
*"why is this episode not scorable"*. **Neither list is the other's subset**: a truncated
episode here is SCORED there; a `CHAIN_TAMPERED` there was `COMPLETED` here. A reviewer
looking for drift between the two should look for a **mapping** defect. `Q-119` records why
they are separate at all.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

# --------------------------------------------------------------------------------------
# Why an episode did not finish. Declared, so every one prints as a number including zeros.
# --------------------------------------------------------------------------------------

#: The lane's TOKEN ceiling refused the next call (golden 8 fixtures A, C part 1).
TOKEN_CEILING = "TOKEN_CEILING"

#: The lane's CALL ceiling refused the next call (golden 8 fixtures B, C part 2).
CALL_CEILING = "CALL_CEILING"

#: HTTP 429. The window is already spent. Golden 8 fixture D.
RATE_LIMIT_429 = "RATE_LIMIT_429"

#: A 429 storm parked the lane and the scheduler moved on (`CONTEXT.md` §13.5(3)).
LANE_PARKED = "LANE_PARKED"

#: ⚠️ `PROCESS.md` §8's LANE RESERVATION. The lane is reserved and this run may not spend on
#: it. **Refusing is the correct outcome and it is counted, not swallowed.**
LANE_RESERVED = "LANE_RESERVED"

#: The provider returned an error that is not a 429.
PROVIDER_ERROR = "PROVIDER_ERROR"

#: The operator stopped the run, or the process died. Resumable: the episode has no published
#: checkpoint, so a re-run picks it up.
INTERRUPTED = "INTERRUPTED"

#: ⚠️ The lane's own rate buckets refused a call that **waiting cannot make admissible** —
#: :class:`whetstone_gate.runner.buckets.BucketError`. `QUESTIONS.md` **Q-179**(2), which
#: closes **Q-174**, RULED 2026-09-04: *"A `BucketError` escaping `execute` drops every
#: remaining episode and PRINTS NOTHING. That is hard rule 11's named failure exactly —
#: silent denominator shrinkage … BOOK IT AS ITS OWN NAMED COUNTED CATEGORY, AND PRINT IT AS
#: A NUMBER LIKE EVERY OTHER. ⚠️ DO NOT make it a silent retry and DO NOT fold it into an
#: existing category — a new failure mode gets its own name."*
#:
#: ⚠️ **IT IS NOT `PROVIDER_ERROR` AND THE DISTINCTION IS THE WHOLE POINT.** No request was
#: made, so no provider was involved and there is nothing to charge: this is **our** pacer
#: declining to spend, and filing it under a provider fault would publish a local refusal as
#: a remote one. ⚠️ **NOR IS IT `RATE_LIMIT_429`**, which is a provider's *answer*; this
#: fires **before** the wire.
PACER_REFUSED = "PACER_REFUSED"

#: ⚠️⚠️ **THE FLOOR. An exception escaped the model call that no `except` clause named.**
#: `QUESTIONS.md` **`Q-200`**, RULED 2026-09-04, verbatim: *"ANY exception escaping the model
#: call is BOOKED AS A COUNTED, NAMED OUTCOME AND THE RUN CONTINUES TO THE NEXT EPISODE. Not a
#: longer list of caught types — a catch-all that books whatever escapes. Three named types
#: have now escaped in three days and the third destroyed an unrepeatable run; a fourth name
#: would be the same defect wearing a new label."*
#:
#: ⚠️ **IT IS NOT `PROVIDER_ERROR`, AND THE DISTINCTION IS WHY IT IS A NINTH NAME RATHER THAN A
#: REUSE.** `PROVIDER_ERROR` means *the provider returned an error that is not a 429* — the
#: provider answered. This category means **nobody answered anything and we do not know why**:
#: `INCIDENTS.md` `INC-159`'s `TimeoutError` from an SSL read, `INC-160`'s `UsageError` from our
#: own log, an arithmetic fault in our own code. **Filing our faults under the provider's name
#: would publish a local failure as a remote one**, which is the reason `PACER_REFUSED` exists
#: one line above.
#:
#: ⚠️ **THE NAME SAYS "UNEXPECTED" ON PURPOSE.** Every other member of this tuple names a
#: condition somebody predicted. This one names the complement of that set, and it is the only
#: member whose population can never be enumerated in advance — which is exactly why the two
#: earlier fixes, each of which added one predicted name, did not hold.
UNEXPECTED_ERROR = "UNEXPECTED_ERROR"

#: Every declared cause, in print order.
UNFINISHED_CAUSES: tuple[str, ...] = (
    TOKEN_CEILING,
    CALL_CEILING,
    RATE_LIMIT_429,
    LANE_PARKED,
    LANE_RESERVED,
    PROVIDER_ERROR,
    PACER_REFUSED,
    UNEXPECTED_ERROR,
    INTERRUPTED,
)


class DenominatorError(AssertionError):
    """The attempted / completed / truncated / not-started identity does not hold.

    Always a stop, never a warning. Hard rule 11 is on `PROCESS.md` §14's NEVER-CUT list.
    """


# --------------------------------------------------------------------------------------
# The episode key
# --------------------------------------------------------------------------------------


@dataclass(frozen=True, order=True)
class EpisodeKey:
    """`PROCESS.md` §12.1's C11 key: ``(block, arm, seed_or_task, attacker_model)``.

    Frozen and ordered, so it is hashable (a checkpoint index), sortable (a **deterministic**
    dispatch order — see :mod:`.scheduler`) and cannot be mutated after a checkpoint has been
    written under it.

    ``seed_or_task`` is a **string** in every block, deliberately. Mock-world blocks key on a
    seed (``"2001"``); τ² and AgentDojo blocks key on a task id, and **τ² task ids are strings
    that look like integers** (``"0"``, ``"11"``, ``"100"``) — `config/protocol.yaml`'s own
    warning: *"Unquoted, YAML would parse them as integers, they would match no task, and the
    selection would silently be empty."* One string type across both avoids re-learning that.
    """

    block: str
    arm: str
    seed_or_task: str
    attacker_model: str

    def __post_init__(self) -> None:
        for name in ("block", "arm", "seed_or_task", "attacker_model"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"EpisodeKey.{name} must be a non-empty string; got {value!r}. "
                    f"A blank component would make two different episodes share a "
                    f"checkpoint path, which is a silently lost episode"
                )
            if "/" in value or "\\" in value or ".." in value:
                raise ValueError(
                    f"EpisodeKey.{name}={value!r} carries a path separator or '..'. The key "
                    f"becomes a filename; a component that can escape its directory is a "
                    f"write outside evals/, which CLAUDE.md §4 forbids"
                )

    @property
    def slug(self) -> str:
        """The checkpoint filename stem. Stable, lower-cased, and **injective**.

        Injective because the four components are joined by ``"__"`` and no component may
        contain a path separator; two distinct keys therefore cannot collide on one file, and
        a collision is what *"skipped on re-run"* would silently turn into a lost episode.
        """
        parts = (self.block, self.arm, self.seed_or_task, self.attacker_model)
        return "__".join(p.strip().lower().replace(" ", "-") for p in parts)


# --------------------------------------------------------------------------------------
# One episode's outcome
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class EpisodeOutcome:
    """What became of one episode, with its cost. **Every field is printed, none inferred.**

    ``turns_run`` and ``turn_budget`` are both carried so that *"truncated"* is a **derived
    fact a reader can check** rather than a flag somebody set: an episode is truncated exactly
    when it started and ``turns_run < turn_budget``.
    """

    key: EpisodeKey
    started: bool
    turns_run: int
    turn_budget: int
    tokens_spent: int
    cause: str | None = None

    def __post_init__(self) -> None:
        if self.cause is not None and self.cause not in UNFINISHED_CAUSES:
            raise DenominatorError(
                f"{self.cause!r} is not a declared cause. The declared set is "
                f"{list(UNFINISHED_CAUSES)}; a cause invented at the call site would never be "
                f"printed, which is hard rule 11's silent shrinkage under a new name"
            )
        if self.tokens_spent < 0:
            raise DenominatorError(f"tokens_spent must not be negative; got {self.tokens_spent}")
        if not self.started and self.cause is None:
            raise DenominatorError(
                f"{self.key.slug}: an episode that never started must carry a cause. "
                f"'It did not run and nobody wrote down why' is exactly the missing trace "
                f"Razorpay's B.9 names"
            )
        if not self.started and self.turns_run:
            raise DenominatorError(
                f"{self.key.slug}: an episode that never started ran {self.turns_run} turns"
            )
        if self.started and self.truncated and self.cause is None:
            raise DenominatorError(
                f"{self.key.slug}: ran {self.turns_run} of {self.turn_budget} turns and "
                f"carries no cause. A truncated episode is COUNTED IN THE DENOMINATOR (hard "
                f"rule 11) and its category is one of the three things it must state"
            )

    @property
    def truncated(self) -> bool:
        """Started, and stopped before its turn budget. **Counted in the denominator.**"""
        return self.started and self.turns_run < self.turn_budget

    @property
    def completed(self) -> bool:
        return self.started and self.turns_run >= self.turn_budget


# --------------------------------------------------------------------------------------
# The denominator
# --------------------------------------------------------------------------------------


@dataclass
class RunDenominator:
    """Every episode the runner was asked to run, and what became of it.

    Mutable on purpose: it accumulates across a run, and across a **resume**, because a
    resumed run re-offers every episode and skips the ones already checkpointed — so the
    denominator is the same number on the second invocation as on the first.
    """

    outcomes: list[EpisodeOutcome] = field(default_factory=list)
    _seen: set[EpisodeKey] = field(default_factory=set)

    def record(self, outcome: EpisodeOutcome) -> None:
        """Record one episode's outcome. **An episode may be recorded exactly once.**

        A second record under the same key is a refusal, not a replacement: a replacement
        would let a retry overwrite the attempt it superseded, and the superseded attempt
        would leave the denominator without saying so.
        """
        if outcome.key in self._seen:
            raise DenominatorError(
                f"{outcome.key.slug} already has an outcome. Overwriting one would let a "
                f"retry silently replace the attempt it superseded — B.9's 'retries' clause, "
                f"in the counter that exists to catch it"
            )
        self._seen.add(outcome.key)
        self.outcomes.append(outcome)

    # -- the numbers -------------------------------------------------------------------

    @property
    def attempted(self) -> int:
        return len(self.outcomes)

    @property
    def completed(self) -> int:
        return sum(1 for o in self.outcomes if o.completed)

    @property
    def truncated(self) -> int:
        return sum(1 for o in self.outcomes if o.truncated)

    @property
    def not_started(self) -> int:
        return sum(1 for o in self.outcomes if not o.started)

    @property
    def denominator(self) -> int:
        """⚠️ **completed + truncated.** Rule 11: a truncated episode is counted here."""
        return self.completed + self.truncated

    @property
    def tokens_spent(self) -> int:
        """Total tokens across every outcome — **including the truncated ones, which are
        not zero.** Per-model figures come from :mod:`.report`; this is the run total and is
        never used in place of one."""
        return sum(o.tokens_spent for o in self.outcomes)

    def truncated_tokens(self) -> int:
        """What truncation cost. Printed, because *"it stopped early"* is not *"it was free"*."""
        return sum(o.tokens_spent for o in self.outcomes if o.truncated)

    def by_cause(self) -> dict[str, int]:
        """Every declared cause and its count, **including the zeros**, in print order."""
        counts = {name: 0 for name in UNFINISHED_CAUSES}
        for outcome in self.outcomes:
            if outcome.cause is not None:
                counts[outcome.cause] += 1
        return counts

    def reconcile(self) -> None:
        """Refuse unless ``attempted == completed + truncated + not_started``."""
        total = self.completed + self.truncated + self.not_started
        if self.attempted != total:
            raise DenominatorError(
                f"the denominator does not reconcile: {self.attempted} attempted against "
                f"{self.completed} completed + {self.truncated} truncated + "
                f"{self.not_started} not started = {total}. Hard rule 11: an episode that is "
                f"in none of the three categories has left the denominator without saying so"
            )

    # -- what a reader gets ------------------------------------------------------------

    def lines(self) -> Iterator[str]:
        """The counter as plain ASCII lines. **Numbers, not prose.**"""
        yield f"episodes attempted            : {self.attempted}"
        yield f"episodes completed            : {self.completed}"
        yield f"episodes TRUNCATED            : {self.truncated}   (rule 11: COUNTED IN THE DENOMINATOR)"
        yield f"  tokens spent by those       : {self.truncated_tokens()}   (NOT zero)"
        yield f"episodes never started        : {self.not_started}"
        for name, count in self.by_cause().items():
            yield f"  {name:<26}: {count}"
        yield f"DENOMINATOR (completed+trunc) : {self.denominator}"
        yield (
            f"reconciles                    : {self.attempted} == {self.completed} + "
            f"{self.truncated} + {self.not_started}"
        )

    def render(self) -> str:
        """:meth:`lines` as one block, for a report or a test failure message."""
        return "\n".join(self.lines())
