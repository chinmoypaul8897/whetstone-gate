"""**THE SCORED BLOCK — `CONTEXT.md` §13.4's M-ADV matrix, and the DISPATCH ORDER it runs in.**

`CONTEXT.md` §13.4's block table and `PROTOCOL.md` §3.1, verbatim on the same row:

    **M-ADV** mock world, adversarial | 5 arms × N | 250 | 150 | reference attacker | scored

and §13.4's sentence that scopes N, in capitals in the specification:

    **N is the per-cell episode count for the mock-world adversarial block (M-ADV) ONLY.**

⚠️⚠️ **WHY THIS MODULE EXISTS AT ALL.** ``--block`` accepted exactly ``("pilot", "cal")``; there
was ``load_pilot`` and ``load_cal`` and **nothing else**. The scored run — the only block whose
numbers are published — had no code path. `driver/cal.py` closed the same absence for the
calibration on 2026-09-04 and this module is deliberately built in its shape, for the reason that
module gives: *"a calibration that needed its own runner would be a second, unreviewed execution
path for the single most consequential run in the project."* The same is true here with more force.

--------------------------------------------------------------------------------------
⚠️⚠️ THE DISPATCH ORDER IS SEED-MAJOR, AND IT IS THE POINT OF THIS MODULE
--------------------------------------------------------------------------------------

**Seed s on all five arms, then seed s+1 on all five, and so on** — never arm 1's whole seed block
followed by arm 2's. :meth:`ScoredMatrix.keys` builds them in that order and
:meth:`ScoredMatrix.dispatch_order` is what :mod:`whetstone_gate.driver.run` dispatches in, because
:meth:`whetstone_gate.runner.scheduler.Scheduler.pending` sorts by :class:`EpisodeKey`, whose field
order is ``(block, arm, seed_or_task, attacker_model)`` — **so the scheduler's own sort is
arm-major**, and a matrix that did not declare its order would get arm-major by default.

⚠️ **THE REASON, AND IT IS THE WHOLE PUBLISHED CLAIM.** The result this project publishes is a
**COMPARISON BETWEEN ARMS**. A sweep is long and a deadline is a deadline, so the honest question is
not *"will it finish"* but *"what does it deliver if it does not"*:

  * **ARM-MAJOR, cut off at a third**, delivers arm 1 complete, part of arm 2, and arms **2S, 3 and
    4 EMPTY**. There is no comparison, and therefore **no result at all** — a third of the tokens
    spent on a number that cannot be published.
  * **SEED-MAJOR, cut off at the same point**, delivers **all five arms at the same n, on the SAME
    SEEDS**. That is a real result with wide intervals, and `PROCESS.md` §14 pre-authorises exactly
    it: the episodes that did not run are counted, categorised and printed, and the figure is
    published with its real n.

⚠️ **AND IT IS ALSO THE PAIRED COMPARISON THE COUNTER-METRIC NEEDS.** `CONTEXT.md` §12.3 and
§10.2's ARM CONFOUNDED rule both compare arms *within a configuration*, and `PROTOCOL.md` §2.1's
own line is *"Same attacker, same seeds, same world, same turn budget. The only variable is the
gate."* **The same world faced by every arm is what makes an arm-to-arm difference mean anything**,
and under seed-major truncation that property holds at every instant the run could stop — the arms
differ by at most one episode, and every episode they do have is on a seed all five arms share.

--------------------------------------------------------------------------------------
⚠️ THE BLOCK LABEL REACHES EVERY LEDGER AND EVERY CHECKPOINT KEY
--------------------------------------------------------------------------------------

:data:`SCORED_BLOCK` is the first component of every
:class:`~whetstone_gate.runner.episodes.EpisodeKey` this matrix produces, and
:meth:`EpisodeKey.slug` joins the four components with ``"__"``, so **every checkpoint filename and
every ledger this block writes begins ``scored__``** — never ``cal__`` and never ``pilot__``. A
scored episode therefore **cannot be mistaken for a calibration or a pilot one by any reader or by
any later replay**, which is `driver/cal.py`'s own property read in the other direction.

⚠️ **THE LABEL IS RAISED AS A QUESTION RATHER THAN ASSUMED — `QUESTIONS.md` `Q-210`.**
`PROTOCOL.md` §3.1's row is headed **M-ADV** and its *state* column reads *scored*, while
``PILOT_BLOCK`` and ``CAL_BLOCK`` each took their row's **heading**. This module's build prompt
named ``SCORED`` in terms and in capitals, so ``SCORED`` is what is built; the divergence from the
naming convention the other two blocks follow is recorded rather than smoothed over, and it is
cheap to settle because **nothing derives meaning from the string** — it is a label, not a spec
value, and both readings give the distinguishability the label exists for.

--------------------------------------------------------------------------------------
⚠️ EVERY VALUE IS READ OR DERIVED. NOTHING HERE IS CHOSEN BY THIS MODULE
--------------------------------------------------------------------------------------

======================  =====================================================
value                   where it comes from
======================  =====================================================
the five arms           :data:`whetstone_gate.gates.verdict.ARMS`, cross-checked
                        against :data:`whetstone_gate.runner.n_rule.ARMS`, which
                        is the count §13.4's own projection multiplies by.
                        `PROTOCOL.md` §2.1: *"The five arms. Five, everywhere."*
**N**                   **DERIVED, never typed** — ``n_decision.measured_tokens_``
                        ``per_episode`` handed to :func:`..runner.n_rule.select_n`,
                        which is `CONTEXT.md` §13.4's rule as `Q-107` ruled it.
                        See :func:`scored_n`.
the seed band           ``seeds.scored_n<N>_first`` / ``_last`` — `PROTOCOL.md`
                        §2.2's own table names both branches' keys; **which of
                        them is read is decided by the rule above**, and the band
                        is cross-checked to carry exactly N seeds
turn budget             ``attacker.turn_budget``
the one cell            ``config/lanes.yaml``'s lane whose ``role`` names the
                        reference attacker — §13.4's M-ADV row is *"reference
                        attacker"*, and that role string names **M-ADV** first
the judge lane          ``config/lanes.yaml``'s ``gate judge for arms 2/2S/3``
======================  =====================================================

**PURE, except the readers that go through ``config/``'s one loader.**
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from whetstone_gate import config as cfg
from whetstone_gate.driver import pilot as pilot_module
from whetstone_gate.gates.verdict import ARMS
from whetstone_gate.runner import n_rule
from whetstone_gate.runner.episodes import EpisodeKey

#: The block name every scored checkpoint and ledger is keyed under. Like
#: :data:`..pilot.PILOT_BLOCK` and :data:`..cal.CAL_BLOCK` it is a **label**, not a spec *value*,
#: so it is not a ``config/`` key. ⚠️ `PROTOCOL.md` §3.1 heads the row **M-ADV** and marks its
#: state *scored*; see this module's docstring and `QUESTIONS.md` `Q-210`.
SCORED_BLOCK = "SCORED"

#: How the reference-attacker lane is found in ``config/lanes.yaml``'s ``role`` prose. **The same
#: marker `driver/pilot.py` and `driver/cal.py` use**, and deliberately not a second copy of the
#: predicate: three blocks disagreeing about which lane is the reference attacker would be three
#: different experiments. `QUESTIONS.md` **Q-143** records that the role is prose and not a key.
REFERENCE_ROLE_MARKER = pilot_module.REFERENCE_ROLE_MARKER
GATE_JUDGE_ROLE_MARKER = pilot_module.GATE_JUDGE_ROLE_MARKER


class ScoredError(RuntimeError):
    """The scored block cannot be assembled as specified. **Always a refusal.**"""


@dataclass(frozen=True)
class ScoredCell:
    """The scored block's single attacker configuration: one lane, and the seeds it carries."""

    lane: str
    attacker_model: str
    seeds: tuple[int, ...]


@dataclass(frozen=True)
class ScoredMatrix:
    """The whole scored block: **one cell, five arms, N seeds each.** Read from ``config/``.

    ⚠️ **THE MEMBER NAMES MIRROR :class:`~whetstone_gate.driver.pilot.PilotMatrix` AND
    :class:`~whetstone_gate.driver.cal.CalMatrix` ON PURPOSE**, for the reason `driver/cal.py`
    gives: :mod:`whetstone_gate.driver.run` consumes ``turn_budget``, ``keys()``, ``lane_for()``,
    ``dispatch_order()``, ``judge_lane`` and ``lines()``, and a scored run that needed its own
    runner would be a second, unreviewed execution path for the only block whose numbers are
    published.

    ⚠️ **IT CARRIES ``arms`` AND NOT ``arm``, AND THAT IS THE ONE DELIBERATE DIVERGENCE.** The
    pilot and the calibration each run **one** arm (`Q-144`; §10.3 rule 1). §13.4's M-ADV row is
    *"5 arms × N"*, so a single ``arm`` attribute here would have to name one of five and would be
    false whichever it named. :meth:`~whetstone_gate.driver.run.RunResult.attacker_tokens` reads
    each **resumed checkpoint's own** ``arm`` field rather than a matrix-wide one, which is what
    makes that possible.
    """

    arms: tuple[str, ...]
    turn_budget: int
    reference: ScoredCell
    judge_lane: str

    @property
    def cells(self) -> tuple[ScoredCell, ...]:
        """⚠️ **ONE.** §13.4's M-ADV row is driven by *"reference attacker"*, singular."""
        return (self.reference,)

    @property
    def episode_count(self) -> int:
        """⚠️ **150 at N=30**, and it is *derived*: arms × cells × the scored seed block."""
        return len(self.arms) * sum(len(cell.seeds) for cell in self.cells)

    @property
    def n(self) -> int:
        """N — the per-cell episode count, **as the length of the band that was read**.

        Not stored and not typed: if the band and :func:`scored_n` ever disagreed,
        :func:`scored_seeds` would already have refused.
        """
        return len(self.reference.seeds)

    def keys(self) -> tuple[EpisodeKey, ...]:
        """Every episode key, **SEED-MAJOR**: every arm at seed s before any arm at seed s+1.

        ⚠️ **THE ORDER IS THE DELIVERABLE, NOT A DETAIL.** See this module's docstring: the
        published claim is a comparison between arms, arm-major truncation destroys it, and
        seed-major truncation leaves all five arms at the same n on the same seeds.

        ⚠️ **AND IT IS DETERMINISTIC** — built from two ordered tuples, never iterated from a set
        — for the reason :meth:`whetstone_gate.runner.scheduler.Scheduler.pending` gives: a run
        whose dispatch order depends on a hash seed is a run whose partial results depend on it
        too, and *"kill mid-run and resume"* would then not be a repeatable demonstration.

        ⚠️ **EVERY KEY CARRIES :data:`SCORED_BLOCK`**, so every slug begins ``scored__``.
        """
        return tuple(
            EpisodeKey(
                block=SCORED_BLOCK,
                arm=arm,
                seed_or_task=str(seed),
                attacker_model=cell.attacker_model,
            )
            for cell in self.cells
            for seed in cell.seeds
            for arm in self.arms
        )

    def dispatch_order(self, pending: Iterable[EpisodeKey]) -> list[EpisodeKey]:
        """``pending`` in **this matrix's own declared order**. ⚠️ **Refuses an unknown key.**

        ⚠️⚠️ **THIS METHOD IS WHY THE ORDER SURVIVES THE SCHEDULER.**
        :meth:`whetstone_gate.runner.scheduler.Scheduler.pending` returns its list **sorted by
        :class:`EpisodeKey`**, and that dataclass is ``order=True`` with fields
        ``(block, arm, seed_or_task, attacker_model)`` — **so the scheduler's sort is arm-major**,
        and it would throw away :meth:`keys`' order without this. The scheduler's stated
        requirement is *determinism*, not sortedness, and a tuple built from `config/` twice over
        satisfies it exactly as a sort does.

        ⚠️ **A KEY THIS MATRIX DID NOT PRODUCE IS A REFUSAL, NEVER AN APPEND.** Silently placing
        an unrecognised key at either end would dispatch an episode whose position nothing chose,
        which is the one property this method exists to provide.
        """
        position = {key: index for index, key in enumerate(self.keys())}
        ordered = list(pending)
        unknown = sorted(key.slug for key in ordered if key not in position)
        if unknown:
            raise ScoredError(
                f"{len(unknown)} key(s) offered for dispatch are not in this scored matrix: "
                f"{unknown[:5]}. The dispatch ORDER is this block's deliverable (seed-major, so "
                f"a cut-off sweep leaves every arm at the same n on the same seeds), and a key "
                f"with no declared position would be dispatched somewhere nothing chose"
            )
        return sorted(ordered, key=position.__getitem__)

    def lane_for(self, key: EpisodeKey) -> str:
        """Which lane an episode key runs on. **Refuses an unknown key**, never guesses."""
        for cell in self.cells:
            if key.attacker_model == cell.attacker_model:
                return cell.lane
        raise ScoredError(
            f"{key.slug} names attacker model {key.attacker_model!r}, which is not the scored "
            f"block's single cell ({self.reference.attacker_model!r}). CONTEXT.md S13.4's M-ADV "
            f"row is driven by the REFERENCE attacker and by nothing else"
        )

    def judged_arms(self) -> tuple[str, ...]:
        """The arms of this matrix that call a gate judge, in matrix order.

        ⚠️ **READ FROM :data:`whetstone_gate.driver.run.JUDGED_ARMS`, WHICH IS `PROTOCOL.md`
        §2.1's OWN SET**, so this block cannot disagree with the module that does the dispatching
        about which arms spend on a second role. Hard rule 12 wants the judge's tokens counted
        separately; step one is agreeing on who spends them.
        """
        from whetstone_gate.driver import run as run_module

        return tuple(arm for arm in self.arms if arm in run_module.JUDGED_ARMS)

    def unjudged_arms(self) -> tuple[str, ...]:
        """The arms that make **no** judge call at all — §14's two deliberate non-uses."""
        judged = set(self.judged_arms())
        return tuple(arm for arm in self.arms if arm not in judged)

    def lines(self) -> list[str]:
        """The matrix as ASCII, so the operator sees what is about to run."""
        judged = self.judged_arms()
        unjudged = self.unjudged_arms()
        seeds = self.reference.seeds
        return [
            "SCORED MATRIX  (CONTEXT.md S13.4 M-ADV row; PROTOCOL.md S3.1)",
            f"  block label            : {SCORED_BLOCK}   (every checkpoint slug begins "
            f"'{SCORED_BLOCK.lower()}__'; it can never read as PILOT or CAL)",
            f"  arms                   : {', '.join(self.arms)}   (PROTOCOL.md S2.1 'The five "
            f"arms. Five, everywhere.')",
            f"  N (per arm per cell)   : {self.n}   (DERIVED by CONTEXT.md S13.4's rule from "
            f"n_decision.measured_tokens_per_episode - never typed)",
            f"  turn budget            : {self.turn_budget}   (attacker.turn_budget)",
            f"  reference lane         : {self.reference.lane} "
            f"[{self.reference.attacker_model}]  seeds {_render_seeds(seeds)}",
            f"  gate-judge lane        : {self.judge_lane}   (arms {', '.join(judged)} CALL it; "
            f"arms {', '.join(unjudged)} make ZERO judge calls)",
            f"  EPISODES               : {self.episode_count}   "
            f"({len(self.arms)} arms x {self.n} seeds)",
            f"    of which JUDGED      : {len(judged) * self.n}   (arms {', '.join(judged)})",
            f"    of which UNJUDGED    : {len(unjudged) * self.n}   (arms {', '.join(unjudged)})",
            "  DISPATCH ORDER         : SEED-MAJOR - every arm at a seed before the next seed.",
            "    The published claim is a COMPARISON BETWEEN ARMS. Arm-major order cut off",
            "    early leaves the later arms EMPTY and there is no comparison to publish;",
            "    seed-major cut off at the same point leaves EVERY arm at the same n on the",
            "    SAME SEEDS - a real result with wide intervals, and the PAIRED comparison",
            "    S12.3's counter-metric and S10.2's ARM CONFOUNDED rule both need.",
            f"  DENOMINATOR            : {self.episode_count} WHATEVER HAPPENS (hard rule 11).",
            "    Every episode not run is counted, categorised and printed as a number, and",
            "    a cut-off sweep publishes its REAL n with its INCOMPLETE denominator -",
            "    PROCESS.md S14 pre-authorises exactly that. N is NEVER shrunk to fit.",
            "  seeds OVERLAP the ladder band by design (both start at the scored block's",
            "    first seed) and are DISJOINT from the pilot and calibration bands, which",
            "    is the disjointness PROTOCOL.md S2.2 and Q-189(a) actually require.",
        ]


def _render_seeds(seeds: tuple[int, ...]) -> str:
    if not seeds:
        return "(none)"
    return f"{seeds[0]}..{seeds[-1]}"


def scored_arms() -> tuple[str, ...]:
    """The five arms, **read from the gate package's own declaration and cross-checked**.

    ⚠️ **THE CROSS-CHECK IS NOT DECORATION.** :data:`whetstone_gate.runner.n_rule.ARMS` is the
    integer §13.4's feasibility projection multiplies every per-arm count by, and
    :data:`whetstone_gate.gates.verdict.ARMS` is the tuple this block dispatches. They are two
    independent transcriptions of `PROTOCOL.md` §2.1's *"The five arms. Five, everywhere."* If
    they ever disagreed, the block that runs would not be the block whose lane-hours were
    projected — and the projection is what selected N.
    """
    arms = tuple(ARMS)
    if len(arms) != n_rule.ARMS:
        raise ScoredError(
            f"gates/verdict.py declares {len(arms)} arms {list(arms)} while runner/n_rule.py's "
            f"S13.4 projection multiplies by {n_rule.ARMS}. PROTOCOL.md S2.1 says 'The five "
            f"arms. Five, everywhere.'; two transcriptions of it disagreeing means the block "
            f"that RUNS is not the block whose lane-hours were PROJECTED, and the projection is "
            f"what selected N"
        )
    if len(set(arms)) != len(arms):
        raise ScoredError(f"the declared arms {list(arms)} are not distinct")
    return arms


def scored_n() -> int:
    """**N, DERIVED THROUGH `CONTEXT.md` §13.4's RULE. Never typed, never preferred.**

    ``n_decision.measured_tokens_per_episode`` is read through the one loader and handed to
    :func:`whetstone_gate.runner.n_rule.select_n`, which is C11's already-reviewed
    implementation of the rule as `Q-107` ruled it. ⚠️ **This module contains no arithmetic that
    could disagree with that rule**, which is `driver/pilot.py`'s own discipline: *"This module
    wires that rule; it does not re-derive it."*

    ⚠️⚠️ **WHILE THAT KEY IS A ``TODO_`` SENTINEL THIS RAISES, AND THE RAISE IS THE CORRECT
    OUTCOME.** :class:`whetstone_gate.config.UndeterminedValue` names its owner — *"C14 — the
    pilot's MEASURED tokens/episode selects the N branch by the `CONTEXT.md` §13.4 rule. Never by
    preference, never by schedule pressure."* **A scored block sized by a session under deadline
    is the precise thing `PROTOCOL.md` §3 forbids in capitals:** *"Quietly shrinking N to a number
    the schedule can reach is the precise thing rule 11 and `ai-playbook` B.9 forbid."* So this
    function refuses rather than defaulting, and `config/` is outside this module's fence anyway.

    ⚠️⚠️ **AND IT REFUSES WHEN `Q-107`'s TWO READINGS DISAGREE — `QUESTIONS.md` `Q-121`, OPEN.**
    :func:`select_n` computes the second conjunct twice, RECOMPUTED at the measured figure and AT
    THE REGISTERED TARGET, *"and neither is adjusted toward the other"*. Below the recomputed
    reading's break-even the two select **different N**, and picking one silently here would
    settle an open Class A question by choosing the seed band. Above it they agree, and there is
    nothing to settle. **Where they agree this proceeds; where they diverge it stops** — which is
    hard rule 1 applied to the one parameter that fixes the size of the published run.
    """
    protocol = cfg.load("protocol")
    measured = protocol.require("n_decision.measured_tokens_per_episode")
    if isinstance(measured, bool) or not isinstance(measured, int):
        raise ScoredError(
            f"config/protocol.yaml's n_decision.measured_tokens_per_episode is {measured!r}, "
            f"which is not an integer token count. CONTEXT.md S13.4's rule keys off MEASURED "
            f"attacker tokens/episode and golden 8 is integer tokens throughout"
        )
    decision = n_rule.select_n(measured)
    if not decision.readings_agree:
        raise ScoredError(
            f"CONTEXT.md S13.4's rule yields N={decision.n} under Q-107's RECOMPUTED reading and "
            f"N={decision.n_at_registered_target} AT THE REGISTERED TARGET, from the same "
            f"measured {measured} tokens/episode ({decision.projected_lane_hours} h against "
            f"{decision.lane_hours_at_registered_target} h, budget {decision.lane_hour_budget} "
            f"h). QUESTIONS.md Q-121 raises that divergence and is OPEN; runner/n_rule.py "
            f"carries BOTH readings with NEITHER adjusted toward the other. Choosing one here "
            f"would settle an open Class A question by picking a seed band, and it would pick "
            f"the SIZE OF THE PUBLISHED RUN. This is a STOP (hard rule 1), not a default"
        )
    return decision.n


def scored_seeds(n: int) -> tuple[int, ...]:
    """``seeds.scored_n<n>_first`` … ``_last``, inclusive. **Through the one loader.**

    ⚠️ **THE BAND IS CHOSEN BY THE RULE, NOT BY THIS FUNCTION.** `PROTOCOL.md` §2.2's table names
    a `config/` key pair for **each** branch, precisely so that the pilot *"SELECTS a branch
    rather than amending a frozen document"*. ``n`` therefore arrives from :func:`scored_n` and
    names which of those pre-registered pairs is read.

    ⚠️ **AND THE BAND IS CROSS-CHECKED AGAINST ``n`` RATHER THAN TRUSTED**, exactly as
    ``cal.cal_seeds`` cross-checks against ``probe.n_cal``. A band that did not carry exactly
    ``n`` seeds would run a **different-sized block than the one the decision rule selected**, and
    hard rule 11 is precisely about a denominator that is not the declared one.
    """
    protocol = cfg.load("protocol")
    keys = (f"seeds.scored_n{n}_first", f"seeds.scored_n{n}_last")
    try:
        first, last = (int(protocol.require(key)) for key in keys)
    except cfg.MissingRequiredValue as missing:
        raise ScoredError(
            f"CONTEXT.md S13.4's rule selected N={n}, and config/protocol.yaml carries no seed "
            f"band for it: {missing}. PROTOCOL.md S2.2's table names a key pair for EACH "
            f"pre-registered branch so the pilot selects one rather than amending a frozen "
            f"document; a branch with no band is a branch that was never pre-registered"
        ) from None
    if last < first:
        raise ScoredError(
            f"config/protocol.yaml gives {keys[0]}={first} above {keys[1]}={last}; the scored "
            f"block would be empty"
        )
    seeds = tuple(range(first, last + 1))
    if len(seeds) != n:
        raise ScoredError(
            f"config/protocol.yaml's scored seed block {first}..{last} carries {len(seeds)} "
            f"seeds but CONTEXT.md S13.4's rule selected N={n}. N is the per-cell episode count "
            f"for M-ADV, so these disagreeing means the block that RUNS is not the block the "
            f"decision rule SELECTED (hard rule 11)"
        )
    return seeds


def load_scored() -> ScoredMatrix:
    """Assemble the scored M-ADV block from ``config/``. **Takes nothing from its caller.**

    ⚠️ **CONTRAST WITH :func:`..pilot.load_pilot`, WHICH REQUIRES ``arm``.** That signature exists
    because the pilot's arm is genuinely undetermined (`Q-144`, since RULED to arm 1). The scored
    block's arms are not undetermined in any sense: `PROTOCOL.md` §2.1 declares **five, and
    §13.4's M-ADV row runs all of them**, so an argument here would be an invitation to run a
    subset of the pre-registered comparison — which is the comparison.

    ⚠️ **IT SPENDS NOTHING AND STARTS NOTHING.** Building the path and spending the run are
    different acts. **No scored episode may run until `prereg-v1` is cut and the freeze is
    witnessed outside this repository** (`CONTEXT.md` §15.1, §15.3; `PROTOCOL.md` §6), and
    :func:`whetstone_gate.driver.run.preflight` refuses a real run before ``probe-v1`` resolves.
    """
    arms = scored_arms()
    n = scored_n()
    reference = pilot_module._one_lane_whose_role_says(REFERENCE_ROLE_MARKER)
    judge = pilot_module._one_lane_whose_role_says(GATE_JUDGE_ROLE_MARKER)
    return ScoredMatrix(
        arms=arms,
        turn_budget=int(cfg.load("protocol").require("attacker.turn_budget")),
        reference=ScoredCell(
            lane=reference.name, attacker_model=reference.name, seeds=scored_seeds(n)
        ),
        judge_lane=judge.name,
    )


def per_arm_counts(keys: Sequence[EpisodeKey], arms: Sequence[str]) -> dict[str, int]:
    """How many of ``keys`` belong to each arm, **including the zeros**.

    Pure, and separate from the matrix so a test can drive it over an arbitrary prefix. Hard rule
    11's shape applied to the balance claim: an arm with no episodes is a **printed zero**, never
    an absent key.
    """
    counts = {arm: 0 for arm in arms}
    for key in keys:
        if key.arm not in counts:
            raise ScoredError(
                f"{key.slug} names arm {key.arm!r}, which is not one of {list(arms)}"
            )
        counts[key.arm] += 1
    return counts


def truncation_imbalance(keys: Sequence[EpisodeKey], arms: Sequence[str]) -> int:
    """The **worst** per-arm imbalance over every prefix of ``keys``, including the empty one.

    ⚠️ **THIS IS THE SEED-MAJOR PROPERTY AS A NUMBER, AND IT IS WHAT THE CLAIM MEANS.** *"The
    sweep will be cut off"* is not a risk to be hedged; it is the expected case, and the question
    is what the run has delivered at the instant it stops. The answer is this number: **at most
    one** for a seed-major order, and as large as N itself for an arm-major one.

    Computed over *every* prefix rather than a sampled few, because a cut-off happens at whatever
    instant the deadline lands on and a property that holds at sampled points is not the property.
    """
    worst = 0
    for length in range(len(keys) + 1):
        counts = per_arm_counts(keys[:length], arms).values()
        worst = max(worst, max(counts) - min(counts))
    return worst
