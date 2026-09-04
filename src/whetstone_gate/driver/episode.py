"""**ONE EPISODE, END TO END. The chunk that turns six built packages into a measurement.**

Every other package in this repository was built, tested and reviewed **in isolation**, and
until this module existed **nothing wired them together**: ``runner/`` was a library with no
entry point, and ``tasks.py`` exposed only ``test`` / ``eval`` / ``selftest`` /
``check-prereg`` / ``check-roles``. This is the wiring, and it is a **wiring** — it
rewrites none of them.

The loop, exactly, per turn:

  1. the **attacker** (`C6`) is asked for one reply, at `config/`'s temperature, against a
     sliding-window context it assembles itself;
  2. :func:`whetstone_gate.driver.protocol.parse_call` reads that reply as at most one tool
     call;
  3. the **gate** for this arm (`C9`) decides — one call, the same call site for all five
     arms, because :class:`whetstone_gate.gates.base.Gate` is one method wide;
  4. an ``ALLOWED`` call goes to the **world** (`C4`), which executes it or refuses it in
     Razorpay's own documented words; anything else does not;
  5. the **ledger** (`C7`) gets one hash-chained entry, ``ALLOWED`` **or** ``DENIED``;
  6. the attacker is handed the tool result — or the one §8.6 generic denial, which is
     **identical in every arm** and carries no clause, no arm and no reason.

--------------------------------------------------------------------------------------
⚠️ THE MODEL CLIENT IS A PARAMETER. THIS PACKAGE IMPORTS NONE.
--------------------------------------------------------------------------------------

See :mod:`whetstone_gate.driver.clients`. The assertion is made **two ways** — a transitive
first-party AST walk **and** a raw-source scan — because `INCIDENTS.md` **INC-51** measured
that an AST walk cannot see ``__import__``, ``importlib.import_module`` or ``getattr`` on a
package root, and watched all three walk past `check_roles` D1, D2 **and** D3.

--------------------------------------------------------------------------------------
⚠️ FOUR THINGS A TURN CAN BE, AND ALL FOUR ARE COUNTED (hard rule 11)
--------------------------------------------------------------------------------------

``attempted == decided + unparsed + off_surface`` is the per-episode identity, refused by
:meth:`EpisodeCounts.reconcile` rather than assumed:

  * **decided** — a call on §8.6a's six-name surface that a gate ruled on. It has a ledger
    entry, ``ALLOWED`` or ``DENIED``.
  * **unparsed** — the reply carried no JSON object naming a tool. **No gate was asked and
    the world was not touched**, so there is no verdict to record and no entry to write.
  * **off_surface** — the reply named a tool outside the six. ⚠️ **The world is still
    called**, because *"tool not enabled"* is the world's own reply and the attacker is
    entitled to discover that the other tools are not there — but **the gate is not asked**,
    because :class:`whetstone_gate.gates.action.CandidateAction` refuses a tool it cannot
    classify, and there is no ledger verdict meaning *"nobody decided"*.

⚠️ **AND THE OFF-SURFACE CASE COSTS CANARY-B REACH, WHICH IS SAID HERE RATHER THAN
DISCOVERED AT C14.** A call to an unknown tool naming ``pay_CANARYRECON`` is a probe
**attempt** that leaves no ledger entry, so §10.1's reach **under**-counts it. The error is
one-directional — reach can only read **smaller** — which is the same safe direction
`HOLES.md` §3.2 already records for `Q-055`'s ``target``-only reading, and it is
**identical across arms**, so it cancels in the ARM CONFOUNDED ratio. It is raised as
`QUESTIONS.md` **Q-142** and printed by :meth:`EpisodeCounts.lines`, never left silent.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from typing import Any, Mapping

from whetstone_gate.attacker import texts as attacker_texts
from whetstone_gate.attacker.corpus import CorpusEntry
from whetstone_gate.attacker.loop import (
    AttackerSettings,
    EpisodeResult,
    run_episode as run_attacker_episode,
)
from whetstone_gate.driver import protocol
from whetstone_gate.driver.clients import (
    MeteredModelClient,
    ProviderFailed,
    RateLimited,
)
from whetstone_gate.gates.action import CandidateAction
from whetstone_gate.gates.base import Gate
from whetstone_gate.gates.judge import ModelGate
from whetstone_gate.gates.state import Authorization, FoldedState, fold
from whetstone_gate.gates.verdict import Outcome, Verdict
from whetstone_gate.ledger import build as ledger_build
from whetstone_gate.ledger.chain import Ledger
from whetstone_gate.runner import episodes as runner_episodes
from whetstone_gate.runner.buckets import BucketError
from whetstone_gate.runner.budget import (
    STOP_BY_429,
    STOP_BY_CALL_CEILING,
    STOP_BY_RESERVATION_SHORTFALL,
    STOP_BY_TOKEN_CEILING,
    LaneBudget,
    usage_total_tokens,
)
from whetstone_gate.world import surface
from whetstone_gate.world.semantics import MockWorld
from whetstone_gate.world.generator import STATUS_AUTHORIZED

# --------------------------------------------------------------------------------------
# ⚠️ S3's BINDING — AN OPEN CLASS A QUESTION, MADE EXPLICIT RATHER THAN CHOSEN QUIETLY.
# `QUESTIONS.md` Q-141.
# --------------------------------------------------------------------------------------

#: `CONTEXT.md` §9.2's **S3** is *"a capture must reference an authorization that exists, is
#: unconsumed, and matches on amount"*, and §8.6a's ``capture_payment`` declares exactly
#: ``payment_id``, ``amount``, ``currency`` — **no authorization parameter**. So an attacker
#: on the real tool surface can never name one, and *what the capture references* is a
#: decision nobody has recorded. It is **Class A**: it changes arm 4's verdicts and therefore
#: a published number, so this module **refuses to choose it** and takes it as an argument
#: with **no default**.
#:
#: **Option 1 — the payment IS the authorization.** ``authorization_id`` is the capture's
#: ``payment_id``, and the folded state opens with one :class:`Authorization` per
#: ``authorized``-status payment at that payment's own amount. S3 then FIRES: an
#: over-amount capture is DENIED and a capture of a payment already captured is DENIED.
S3_AUTHORIZATION_IS_THE_PAYMENT = "authorization-is-the-payment"

#: **Option 2 — nothing is referenced.** ``authorization_id`` is ``None`` on every capture
#: and the folded state opens with no authorizations, so arm 4's S3 clause returns
#: ``INDETERMINATE`` on **every** capture (§9.3's *"a declared obligation with no result"*).
#: ⚠️ **THAT BLOCKS, WHICH FLATTERS OUR OWN GATE**, and it is named here so the flattery is
#: a recorded option rather than an accident: an arm 4 that blocks every capture because the
#: harness never bound an authorization would publish a defence it does not have.
S3_AUTHORIZATION_NEVER_REFERENCED = "authorization-never-referenced"

#: The two readings, and there is no third. A value outside this tuple is a refusal.
S3_BINDINGS: tuple[str, ...] = (
    S3_AUTHORIZATION_IS_THE_PAYMENT,
    S3_AUTHORIZATION_NEVER_REFERENCED,
)


class DriverError(RuntimeError):
    """The driver was asked for something it refuses to guess. Always a refusal."""


class LaneStopped(RuntimeError):
    """A lane stopped mid-episode. ``cause`` is one of :data:`.episodes.UNFINISHED_CAUSES`.

    ⚠️ **RAISED FROM INSIDE THE INJECTED CLIENT, CAUGHT OUTSIDE THE ATTACKER LOOP.** C6's
    :func:`whetstone_gate.attacker.loop.run_episode` owns the turn loop and this session
    **wires** it rather than rewriting it, so the only way to stop an episode part-way is to
    raise from the client it was handed. The episode is then **truncated, not lost**: its
    ledger holds every entry it did write, and hard rule 11 **counts it in the denominator**.
    """

    def __init__(self, cause: str) -> None:
        if cause not in runner_episodes.UNFINISHED_CAUSES:
            raise DriverError(
                f"{cause!r} is not a declared cause; declared: "
                f"{list(runner_episodes.UNFINISHED_CAUSES)}"
            )
        super().__init__(cause)
        self.cause = cause


#: :mod:`.budget`'s stop reasons mapped to :mod:`.episodes`' causes. ⚠️ Written out rather
#: than derived, for the reason :mod:`whetstone_gate.runner.scheduler` gives for its own copy
#: of this table: the two vocabularies are deliberately separate (`Q-119`) and a mapping
#: table is where a reviewer can see the join. This is the **driver's** join and it is a
#: second writing on purpose — the scheduler's is for a lane that could not be dispatched to,
#: this one is for a call that was refused mid-episode.
CAUSE_FOR_STOP: dict[str, str] = {
    STOP_BY_TOKEN_CEILING: runner_episodes.TOKEN_CEILING,
    STOP_BY_CALL_CEILING: runner_episodes.CALL_CEILING,
    STOP_BY_429: runner_episodes.RATE_LIMIT_429,
    STOP_BY_RESERVATION_SHORTFALL: runner_episodes.TOKEN_CEILING,
}


# --------------------------------------------------------------------------------------
# Per-episode counters — hard rule 11's shape, applied to turns
# --------------------------------------------------------------------------------------


@dataclass
class EpisodeCounts:
    """What each turn of one episode became. **Every field prints; none is inferred.**"""

    attempted: int = 0
    decided: int = 0
    unparsed: int = 0
    off_surface: int = 0
    denied: int = 0
    indeterminate: int = 0
    executed: int = 0

    def reconcile(self) -> None:
        """Refuse unless ``attempted == decided + unparsed + off_surface``."""
        total = self.decided + self.unparsed + self.off_surface
        if self.attempted != total:
            raise runner_episodes.DenominatorError(
                f"turn counts do not reconcile: {self.attempted} attempted against "
                f"{self.decided} decided + {self.unparsed} unparsed + "
                f"{self.off_surface} off-surface = {total}. A turn in none of the three "
                f"categories has left the record without saying so (hard rule 11)"
            )

    def lines(self) -> list[str]:
        """ASCII, numbers not prose, **including the zeros** (`PROCESS.md` §9)."""
        return [
            f"turns attempted        : {self.attempted}",
            f"  decided by a gate    : {self.decided}",
            f"  UNPARSED (no call)   : {self.unparsed}   (INC-01: a silent drop reads as a "
            f"perfect defence)",
            f"  OFF-SURFACE tool     : {self.off_surface}   (world answered; NO ledger entry "
            f"- Q-142, CANARY-B under-counts)",
            f"verdicts DENIED        : {self.denied}",
            f"verdicts INDETERMINATE : {self.indeterminate}",
            f"calls the world RAN    : {self.executed}",
        ]


@dataclass(frozen=True)
class DriverEpisode:
    """One episode's whole record. **The ledger is the artefact; this is the accounting.**"""

    key: runner_episodes.EpisodeKey
    lane: str
    seed: int
    arm: str
    ledger: Ledger
    turns_run: int
    turn_budget: int
    attacker_tokens: int
    judge_tokens: int
    calls_used: int
    judge_calls: int
    counts: EpisodeCounts
    cause: str | None
    attacker_result: EpisodeResult | None

    @property
    def tokens_spent(self) -> int:
        """What this episode cost, both roles. ⚠️ **A SUM OF TWO ROLE COUNTERS, NEVER OF
        TWO LANE DELTAS** — see :attr:`_MeteredCall.tokens_settled` and `INC-111`."""
        return self.attacker_tokens + self.judge_tokens

    @property
    def truncated(self) -> bool:
        """Started and stopped before its turn budget. ⚠️ **Counted in the denominator.**"""
        return self.turns_run < self.turn_budget

    def outcome(self) -> runner_episodes.EpisodeOutcome:
        """This episode as :mod:`.episodes`' own record, for the run denominator."""
        return runner_episodes.EpisodeOutcome(
            key=self.key,
            started=True,
            turns_run=self.turns_run,
            turn_budget=self.turn_budget,
            tokens_spent=self.tokens_spent,
            cause=self.cause,
        )


# --------------------------------------------------------------------------------------
# What a caller must supply, and every value's provenance
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class EpisodeSettings:
    """The `config/` figures one episode runs on, plus the one thing `config/` does not say.

    ⚠️ **EVERY NUMBER HERE IS READ THROUGH THE ONE LOADER** (hard rule 9) by
    :meth:`from_config`, and none of them is written in this package's source — the hard
    rule 9 tripwire scans for exactly that.

    ``s3_binding`` is the exception and it is **not a number**: it is the open Class A
    question of `Q-141`, and it has **no default** here for the same reason
    :class:`whetstone_gate.runner.budget.Ceilings` has no one-ceiling constructor — a
    default would put the unasked question one keyword argument away.
    """

    attacker: AttackerSettings
    attacker_call_reservation_tokens: int
    judge_call_reservation_tokens: int
    s3_binding: str

    def __post_init__(self) -> None:
        if self.s3_binding not in S3_BINDINGS:
            raise DriverError(
                f"s3_binding must be one of {list(S3_BINDINGS)}; got {self.s3_binding!r}. "
                f"CONTEXT.md S9.2's S3 needs a capture to REFERENCE an authorization and "
                f"S8.6a's capture_payment declares no parameter for one, so which reading "
                f"applies is an OPEN Class A question (QUESTIONS.md Q-141). This is a "
                f"refusal rather than a default: a default would decide arm 4's verdicts, "
                f"and the option that blocks every capture FLATTERS OUR OWN GATE"
            )

    @classmethod
    def from_config(cls, *, s3_binding: str) -> "EpisodeSettings":
        """Read every figure from `config/protocol.yaml`. **No defaults, hard rule 9.**

        The two reservations are the ones :mod:`whetstone_gate.runner.budget`'s own
        docstring names: *"``gate_judge.target_tokens_per_call`` for a judge call; the
        per-episode target divided across the turn budget for an attacker call"*. ⚠️ A
        reservation is an **upper bound** used for hard rule 12's **prospective** admission
        test, so it can only make a lane stop **earlier**, never later — and it is **never
        what is accounted**. What is accounted is the provider's own ``usage.total_tokens``.
        """
        attacker = AttackerSettings.from_config()
        judge = _judge_target_tokens_per_call()
        return cls(
            attacker=attacker,
            attacker_call_reservation_tokens=(
                attacker.target_tokens_per_episode // attacker.turn_budget
            ),
            judge_call_reservation_tokens=judge,
            s3_binding=s3_binding,
        )


def _judge_target_tokens_per_call() -> int:
    """``gate_judge.target_tokens_per_call``, through the one loader.

    A function rather than an inline read so that this package contains exactly one place
    the key is named, which is what makes a rename a single edit and a missing key a single
    refusal.
    """
    from whetstone_gate import config as cfg

    return int(cfg.load("protocol").require("gate_judge.target_tokens_per_call"))


# --------------------------------------------------------------------------------------
# The metered adapters — hard rule 12 lives here
# --------------------------------------------------------------------------------------


@dataclass
class _MeteredCall:
    """One lane's admit → call → settle cycle. **Prospective, then the provider's own number.**

    ⚠️ **THE ORDER IS THE RULE.** Golden 8: *"Hard rule 12 says ABORT, not 'overspend and
    then abort'."* :meth:`whetstone_gate.runner.budget.LaneBudget.admit` runs **before** the
    provider is touched, against a reservation from `config/`; the provider's own
    ``usage.total_tokens`` is what is settled afterwards, and nothing in between estimates.
    """

    lane: str
    budget: LaneBudget
    reservation_tokens: int
    on_usage: Any
    """``(lane, tokens, outcome) -> None``. The usage-row sink, injected by the shell so
    this class touches no filesystem (hard rule 8)."""

    tokens_settled: int = 0
    """Tokens this ROLE settled. ⚠️ **A ROLE COUNTER, NOT A LANE COUNTER, AND THE
    DISTINCTION IS `INCIDENTS.md` INC-111.**

    `CONTEXT.md` §13.3.2 puts the **reference attacker** and the **gate judge for arms
    2/2S/3** on the *same lane*, ``gemma-26b``. An episode that derived its cost from the
    two lanes' budget deltas therefore added one lane to itself: measured in this chunk's
    own dry run, an arm-1 episode of 20 calls at 3,000 tokens reported **120,000** where
    the answer is 60,000. And the same confusion, one level up, made the pilot's
    tokens/episode figure **drop every reference-attacker episode** — the half §13.4's rule
    is chiefly about — because its lane equalled the judge's. **The role is what separates
    an attacker call from a judge call; the lane never was.**"""

    calls_settled: int = 0
    """Calls this ROLE settled. Same reason as :attr:`tokens_settled`."""

    def run(self, call: Any) -> str:
        """Admit, call, settle. Returns the reply text; raises :class:`LaneStopped`."""
        if self.budget.stopped:
            raise LaneStopped(CAUSE_FOR_STOP.get(self.budget.stopped_by or "", "PROVIDER_ERROR"))
        admission = self.budget.admit(self.reservation_tokens)
        if not admission.admitted:
            raise LaneStopped(
                CAUSE_FOR_STOP.get(admission.refused_by or "", runner_episodes.PROVIDER_ERROR)
            )
        try:
            reply = call()
        except RateLimited:
            # ⚠️ Golden 8 fixture D: ZERO tokens, ZERO calls, and the lane STOPS. There is
            # no destination argument anywhere on this path, so "never retry into another
            # lane" is a property of the code's shape and not a rule to remember.
            self.budget.record_429()
            self.on_usage(self.lane, 0, "RATE_LIMITED")
            raise LaneStopped(runner_episodes.RATE_LIMIT_429) from None
        except ProviderFailed as failure:
            # ⚠️ A NON-429 ERROR HAS NO `usage` BLOCK, SO ITS TOKEN COST IS UNKNOWN AND IS
            # RECORDED AS ZERO — an UNDER-count, published rather than estimated (golden 8:
            # "NEVER estimated"). The call itself IS counted, because the request was made.
            #
            # ⚠️⚠️ **`INCIDENTS.md` INC-142's MOST EXPENSIVE LINE WAS HERE.** This clause used
            # to be a bare `except ProviderFailed:` and the `from None` below discarded the
            # message with the traceback — so the pilot's ten qwen failures were booked,
            # counted and reconciled (hard rule 11 satisfied) while the *diagnosis* was gone,
            # and the operator could not tell a 401 from a 404 from a malformed 200.
            #
            # ⚠️ **THE `from None` STAYS, AND SO DOES THE SUPPRESSION OF THE BODY.** INC-142
            # itself calls that suppression *"deliberate and its stated reason sound — a
            # provider error can quote the credential it rejected."* What changed is that the
            # STATUS and a SHORT enum-shaped TYPE now travel as FIELDS on the exception rather
            # than as prose inside a message that is thrown away. **A status is an integer; it
            # cannot quote a credential, and it was being discarded with the body for no
            # reason but proximity.**
            self.budget.settle(0)
            self.calls_settled += 1
            self.on_usage(
                self.lane,
                0,
                "ERROR",
                status=failure.status,
                error_type=failure.error_type,
            )
            raise LaneStopped(runner_episodes.PROVIDER_ERROR) from None
        except BucketError:
            # ⚠️⚠️ **`Q-179`(2), RULED 2026-09-04, WHICH ALSO CLOSES `Q-174`.** Before this
            # clause a `BucketError` raised inside `run._PacedClient._pace` — which runs
            # INSIDE the `call()` above — escaped `run`, escaped `execute`, and took the
            # whole run with it: no report, no denominator, every remaining episode gone and
            # **nothing printed**. That is hard rule 11's named failure, *"NO SILENT
            # DENOMINATOR SHRINKAGE"*, arriving by exception rather than by arithmetic.
            #
            # ⚠️ **BOOKED, NOT RETRIED.** The ruling forbids a silent retry by name. The
            # lane stops here exactly as it does on a 429, and the episode is COUNTED under
            # its own cause — `runner/episodes.py:PACER_REFUSED`, which is a member of
            # `UNFINISHED_CAUSES` and therefore prints as a number in every report,
            # including when it is zero.
            #
            # ⚠️ **ZERO TOKENS AND ZERO CALLS, and that is not the `ProviderFailed` case.**
            # There, a request WAS made and is counted with an unknown cost. Here the pacer
            # refused BEFORE the wire, so no provider saw anything: `settle` is not called
            # and `calls_settled` does not move. Charging a call for a request that was
            # never sent would overstate the spend hard rule 12 exists to bound.
            self.on_usage(self.lane, 0, runner_episodes.PACER_REFUSED)
            raise LaneStopped(runner_episodes.PACER_REFUSED) from None
        tokens = usage_total_tokens(reply.usage)
        self.budget.settle(tokens)
        self.tokens_settled += tokens
        self.calls_settled += 1
        self.on_usage(self.lane, tokens, "OK")
        return reply.text


@dataclass
class _AttackerClient:
    """Adapts a :class:`.clients.MeteredModelClient` down to C6's text-only protocol.

    ⚠️ **Q-161: THIS IS WHERE THE LANE ENTERS THE CLIENT, AND IT IS `self.metered.lane`.**
    That field is the authoritative per-role lane — ``_MeteredCall`` is built one function
    below with ``lane=lane`` from ``run.py``'s dispatch loop, and it is the same value the
    budget and the usage log are keyed on. **C6's own protocol is unchanged**: the attacker
    loop is asked for text and knows nothing about lanes, which is why the threading stops
    here rather than reaching into ``attacker/loop.py``.
    """

    metered: _MeteredCall
    client: MeteredModelClient

    def complete(self, *, messages: tuple[dict[str, str], ...], temperature: float) -> str:
        return self.metered.run(
            lambda: self.client.complete_attacker(
                messages=messages, temperature=temperature, lane=self.metered.lane
            )
        )


@dataclass
class _JudgeClient:
    """Adapts a :class:`.clients.MeteredModelClient` to C9's ``(system, user)`` protocol."""

    metered: _MeteredCall
    client: MeteredModelClient
    calls: int = 0

    def complete(self, *, system: str, user: str) -> str:
        self.calls += 1
        # ⚠️ Q-161. The judge's lane, not the attacker's: this adapter's own _MeteredCall was
        # built with `lane=judge_lane`, and CONTEXT.md S13.3.2 puts two roles on one lane, so
        # reading the lane off the ROLE's meter is the only reading that stays right when
        # they diverge. INC-111 is the incident where a lane-based split dropped a role.
        return self.metered.run(
            lambda: self.client.complete_judge(
                system=system, user=user, lane=self.metered.lane
            )
        )


# --------------------------------------------------------------------------------------
# The executor — gate, world, ledger, in that order, once per turn
# --------------------------------------------------------------------------------------


def render_tool_result(result: Any) -> str:
    """What the attacker is shown for one tool call. ⚠️ **The WORLD's words, not ours.**

    A successful call renders its payload as sorted-key JSON; a refusal renders the world's
    own error string — Razorpay's documented text for a Razorpay refusal, the MCP layer's
    for a tool-layer one. **Nothing here is authored about the outcome**, because §10.1's
    requirement is *"no DIFFERENTIAL information across arms"* and a harness-written
    paraphrase would be a second original that could drift arm to arm.

    ⚠️ **``result.ok`` IS READ DIRECTLY AND A RESULT WITHOUT IT RAISES.** The defaulting form
    ``getattr(result, "ok", False)`` was written here first and **this chunk's own scanner
    refused it** — `check_roles.MOAT_REFUSED_DYNAMIC` refuses the whole vocabulary of
    run-time attribute reach because `INCIDENTS.md` **INC-51** measured it walking past D1,
    D2 and D3. It was wrong for a second reason too, the one
    :mod:`whetstone_gate.probe.predicates` records as `INC-92`: a defaulting read renders a
    malformed result as *"the world refused it"*, which is a silent lie about what happened.
    """
    if result.ok:
        return json.dumps(result.payload, sort_keys=True, ensure_ascii=False)
    return str(result.error)


def opening_state(world: MockWorld, *, s3_binding: str) -> FoldedState:
    """The folded state one episode opens with. ⚠️ **`Q-141`'s two readings, side by side.**

    Under :data:`S3_AUTHORIZATION_IS_THE_PAYMENT` every ``authorized``-status payment in the
    seed's world opens as one unconsumed :class:`Authorization` at that payment's own
    amount, so S3's *"exists, is unconsumed, matches on amount"* has something to be true
    or false about. Under :data:`S3_AUTHORIZATION_NEVER_REFERENCED` the map is empty and
    every capture is ``INDETERMINATE`` in arm 4.

    ⚠️ **The map is built from the WORLD, identically in every arm** — it is a function of
    the seed and nothing else, so it introduces no differential (§10.1).
    """
    if s3_binding == S3_AUTHORIZATION_NEVER_REFERENCED:
        return FoldedState()
    authorizations = {
        payment_id: Authorization(
            amount_paise=world.payment(payment_id).amount_paise, consumed=False
        )
        for payment_id in world.payment_ids
        if world.payment(payment_id).status == STATUS_AUTHORIZED
    }
    return FoldedState(authorizations=authorizations)


@dataclass
class _Executor:
    """The gate → world → ledger path for one episode. **One call per attacker turn.**

    It implements :class:`whetstone_gate.attacker.loop.ToolExecutor`, whose whole contract
    is ``execute(attacker_text) -> str``. ⚠️ **That narrow return type is the blindness
    guard**: there is no verdict field, no arm field and no clause number on the way back,
    so a policy leak into the attacker's context is *structurally impossible from here*.
    """

    world: MockWorld
    gate: Gate
    ledger: Ledger
    generic_denial: str
    s3_binding: str
    state: FoldedState
    turn_budget: int
    counts: EpisodeCounts = field(default_factory=EpisodeCounts)
    turns_run: int = 0

    def execute(self, attacker_text: str) -> str:
        index = self.turns_run
        if index >= self.turn_budget:
            raise DriverError(
                f"the executor was called for turn {index} against a turn budget of "
                f"{self.turn_budget}. One episode is one turn budget; a loop that ran past "
                f"it would put un-budgeted calls into a pre-registered count"
            )
        self.counts.attempted += 1
        self.turns_run += 1

        call = protocol.parse_call(attacker_text)
        if not call.parsed:
            self.counts.unparsed += 1
            return protocol.MALFORMED_CALL_REPLY
        if not call.is_on_the_surface:
            # ⚠️ The WORLD owns "tool not enabled" (§8.6a). The gate is not asked, because
            # CandidateAction refuses a tool it cannot classify, and no ledger verdict means
            # "nobody decided". Counted, printed, and raised as Q-142.
            self.counts.off_surface += 1
            return render_tool_result(self.world.call(call.tool, dict(call.arguments)))

        action = self.candidate_action(call.tool, call.arguments)
        state = replace(self.state, turns_remaining=self.turn_budget - index)
        verdict: Verdict = self.gate.decide(action, state)
        self.counts.decided += 1

        if verdict.outcome is Outcome.ALLOWED:
            result = self.world.call(call.tool, dict(call.arguments))
            executed = ledger_build.executed_of(result)
            harm = result.harm
        else:
            result = None
            executed = False
            harm = None
            if verdict.outcome is Outcome.DENIED:
                self.counts.denied += 1
            else:
                self.counts.indeterminate += 1
        if executed:
            self.counts.executed += 1

        ledger_build.append_call(
            self.ledger,
            tool=call.tool,
            arguments=dict(call.arguments),
            harm=harm,
            turn_index=index,
            verdict=verdict.outcome.value,
            executed=executed,
        )
        self.state = fold(state, action, verdict, executed=executed)

        if result is None:
            # ⚠️ §8.6's ONE generic denial, identical across arms and returned for an
            # INDETERMINATE too. It is the gate's copy, read from `data/` by the shell.
            return self.generic_denial
        return render_tool_result(result)

    def candidate_action(self, tool: str, arguments: Mapping[str, Any]) -> CandidateAction:
        """The call as the gate sees it, **before** it executes.

        ``payment_notes`` are the target payment's own notes **as ``fetch_payments`` returned
        them, identically in every arm** (§10.1) — they are the only route by which clause
        **P7** can fire, and they are read from the world rather than from the attacker's
        arguments so that an attacker cannot assert an exemption it was not shown.
        """
        amount = ledger_build.amount_of(arguments)
        raw_id = arguments.get("payment_id")
        payment_id = raw_id if isinstance(raw_id, str) and raw_id else None
        notes: Mapping[str, str] = {}
        if payment_id is not None and payment_id in self.world.payment_ids:
            notes = dict(self.world.payment(payment_id).notes)
        return CandidateAction(
            tool=tool,
            amount_paise=0 if amount is None else amount,
            payment_id=payment_id,
            receipt=ledger_build.receipt_of(arguments),
            authorization_id=self.authorization_reference(tool, payment_id),
            payment_notes=notes,
        )

    def authorization_reference(self, tool: str, payment_id: str | None) -> str | None:
        """What a capture references. ⚠️ **`Q-141`, and this module does not decide it.**"""
        if tool != surface.CAPTURE_PAYMENT:
            return None
        if self.s3_binding == S3_AUTHORIZATION_NEVER_REFERENCED:
            return None
        return payment_id


# --------------------------------------------------------------------------------------
# The episode itself
# --------------------------------------------------------------------------------------


def run_one_episode(
    *,
    key: runner_episodes.EpisodeKey,
    seed: int,
    arm: str,
    lane: str,
    world: MockWorld,
    gate: Gate,
    ledger: Ledger,
    client: MeteredModelClient,
    attacker_budget: LaneBudget,
    judge_budget: LaneBudget,
    judge_lane: str,
    settings: EpisodeSettings,
    generic_denial: str,
    corpus_entries: tuple[CorpusEntry, ...],
    on_usage: Any,
) -> DriverEpisode:
    """Run one episode to its turn budget, or to the first thing that stops the lane.

    **Pure of the filesystem, the clock and the network.** The world, the gate and the
    ledger arrive built; the model client is injected; the usage sink is a callable. What
    this function does is *sequence* them — which is exactly what nothing in this repository
    did before it existed.

    ⚠️ **A TRUNCATED EPISODE RETURNS NORMALLY WITH ITS CAUSE**, and its ledger holds every
    entry it wrote. Hard rule 11: it is **counted in the denominator**, its token cost is
    **not zero**, and both are carried on the returned :class:`DriverEpisode`.
    """
    if gate.arm != arm:
        raise DriverError(
            f"the gate says arm {gate.arm!r} and the episode says {arm!r}. One episode is "
            f"one arm (CONTEXT.md S8: 'the only variable is the gate'), and an entry stamped "
            f"with the wrong arm moves an escape rate and a CANARY-B reach at once"
        )
    if ledger.arm != arm or ledger.seed != seed:
        raise DriverError(
            f"the ledger says (seed {ledger.seed}, arm {ledger.arm!r}) and the episode says "
            f"(seed {seed}, arm {arm!r})"
        )

    executor = _Executor(
        world=world,
        gate=gate,
        ledger=ledger,
        generic_denial=generic_denial,
        s3_binding=settings.s3_binding,
        state=opening_state(world, s3_binding=settings.s3_binding),
        turn_budget=settings.attacker.turn_budget,
    )
    attacker_client = _AttackerClient(
        metered=_MeteredCall(
            lane=lane,
            budget=attacker_budget,
            reservation_tokens=settings.attacker_call_reservation_tokens,
            on_usage=on_usage,
        ),
        client=client,
    )
    judge_client = _JudgeClient(
        metered=_MeteredCall(
            lane=judge_lane,
            budget=judge_budget,
            reservation_tokens=settings.judge_call_reservation_tokens,
            on_usage=on_usage,
        ),
        client=client,
    )
    _wire_judge(gate, judge_client)

    cause: str | None = None
    attacker_result: EpisodeResult | None = None
    try:
        attacker_result = run_attacker_episode(
            client=attacker_client,
            executor=executor,
            settings=settings.attacker,
            tool_schemas_text=protocol.tool_schemas_text(),
            corpus_entries=corpus_entries,
            fold=_AttackerStateView(executor),
            episode_seed=seed,
        )
    except LaneStopped as stopped:
        cause = stopped.cause

    executor.counts.reconcile()
    return DriverEpisode(
        key=key,
        lane=lane,
        seed=seed,
        arm=arm,
        ledger=ledger,
        turns_run=executor.turns_run,
        turn_budget=settings.attacker.turn_budget,
        attacker_tokens=attacker_client.metered.tokens_settled,
        judge_tokens=judge_client.metered.tokens_settled,
        calls_used=attacker_client.metered.calls_settled,
        judge_calls=judge_client.metered.calls_settled,
        counts=executor.counts,
        cause=cause,
        attacker_result=attacker_result,
    )


def _wire_judge(gate: Gate, judge_client: Any) -> None:
    """Point a model-backed arm's gate at the metered judge client.

    ⚠️ **ARMS 1 AND 4 TAKE NO CLIENT AND THIS FUNCTION GIVES THEM NONE.**
    :func:`whetstone_gate.gates.shell.build_gate` already refuses to build them with one —
    *"a control arm or a deterministic kernel handed a model client is an arm whose
    behaviour could depend on one"* — and this is the second half of the same guarantee, at
    the only other place a client could be attached.
    """
    if isinstance(gate, ModelGate):
        gate.client = judge_client


@dataclass(frozen=True)
class _AttackerStateView:
    """C6's :class:`~whetstone_gate.attacker.loop.StateFolder`, over the gate's folded state.

    ⚠️ **IT EXPOSES §8.6's SIX FIELDS AND NOTHING ELSE.** The attacker is shown what **it
    has done** — amounts it moved, receipts it used, turns it has left — and never what it
    is not allowed to do. ``authorizations`` is §8.6a's deliberately-absent seventh field
    and it is absent here too; ``idempotency_keys_seen`` is rendered as §8.6a's flat list of
    receipt strings, out of the ``(payment, receipt)`` pairs the kernel folds (`Q-112`).
    """

    executor: _Executor

    def episode_paise_moved(self) -> int:
        return self.executor.state.episode_paise_moved

    def per_payment_refunded_paise(self) -> dict[str, int]:
        return dict(self.executor.state.per_payment_refunded_paise)

    def per_payment_captured_paise(self) -> dict[str, int]:
        return dict(self.executor.state.per_payment_captured_paise)

    def idempotency_keys_seen(self) -> tuple[str, ...]:
        return tuple(receipt for _payment, receipt in self.executor.state.idempotency_keys_seen)

    def actions_executed(self) -> int:
        return self.executor.state.actions_executed


# --------------------------------------------------------------------------------------
# ⚠️ THE PROBE REACHES EVERY ARM IDENTICALLY — the DRIVER-side assertion (§10.1)
# --------------------------------------------------------------------------------------

#: The fields of a ledger entry that describe **what the attacker proposed**, as opposed to
#: what the gate said about it. `CONTEXT.md` §10.1's requirement is *"no DIFFERENTIAL
#: information across arms"*, so these must agree across arms for as long as the arms have
#: been shown the same thing — which is up to and including the first non-``ALLOWED``
#: verdict, after which the arms legitimately diverge because one of them was refused.
PROPOSAL_FIELDS: tuple[str, ...] = ("turn_index", "tool", "target", "amount_paise")


def arm_invariant_prefix(entries: Any) -> tuple[tuple[Any, ...], ...]:
    """One arm's proposals, up to **and including** its first non-``ALLOWED`` verdict.

    C9 asserted the identical-across-arms property from the gate side and C10 from the probe
    side. ⚠️ **This is the DRIVER side, and it is the only one that can see a whole episode:**
    the gate cannot know what the attacker would have proposed next, and the probe reads a
    stored ledger without knowing which arm was shown what.

    The comparison stops at the first refusal because that is where the arms stop being
    comparable: a refused turn hands the attacker a different tool result, so turn *n+1*'s
    proposal is allowed to differ. **Everything before it must not.**
    """
    prefix: list[tuple[Any, ...]] = []
    for entry in entries:
        # ⚠️ Named one by one rather than read through PROPOSAL_FIELDS with `getattr`: a
        # run-time attribute reach is refused by check_roles.MOAT_REFUSED_DYNAMIC (INC-51),
        # and written out, a renamed ledger field is an AttributeError here rather than a
        # silently empty comparison that reports every arm as agreeing.
        prefix.append((entry.turn_index, entry.tool, entry.target, entry.amount_paise))
        if entry.verdict != Outcome.ALLOWED.value:
            break
    return tuple(prefix)


def prefixes_agree(left: tuple[Any, ...], right: tuple[Any, ...]) -> bool:
    """True when the shorter prefix is a prefix of the longer. **The §10.1 comparison.**"""
    shared = min(len(left), len(right))
    return left[:shared] == right[:shared]


def attacker_texts_are_shared() -> str:
    """The §8.6 attacker system prompt, so a caller can assert it is arm-independent.

    Exposed as a function rather than read at each call site so that a test asserting *"every
    arm was shown the same words"* reads the same bytes the loop does.
    """
    return attacker_texts.attacker_system_prompt()
