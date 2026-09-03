"""**`CONTEXT.md` §13.4's N DECISION RULE — BOTH CONJUNCTS. `QUESTIONS.md` `Q-107`, RULED.**

The rule, `CONTEXT.md` §13.4 and `PROTOCOL.md` §3 and `config/protocol.yaml`'s
``n_decision.branch_a_condition``, all verbatim on the same sentence:

    **N = 50 per arm per configuration IF the 31 Aug pilot's measured attacker
    tokens/episode is ≤ 60,000 AND the projected total Gemma lane-time (§13.4) is ≤ 32 h.**
    **Otherwise N = 30.**

**PURE.** No I/O, no clock, no network, no randomness. Every constant is read from `config/`
or parsed from `CONTEXT.md`; see THE PROVENANCE OF EVERY NUMBER below.

--------------------------------------------------------------------------------------
⚠️ `Q-107` IS RULED, AND IT CHANGES A PUBLISHED NUMBER
--------------------------------------------------------------------------------------

The ruling, recorded verbatim in `QUESTIONS.md` before a line of this module was written:

    ⚠️ Q-107 IS RULED AND IT CHANGES A PUBLISHED NUMBER: S13.4's N rule has TWO conjuncts —
    tokens per episode ≤ 60,000 AND projected Gemma lane-time ≤ 32 h. Golden 8's vectors pin
    the FIRST. On S13.4's own figures N=50 is 40.05 h and **fails the second regardless of
    what the pilot measures**, so the rule yields **N=30**. Implement BOTH conjuncts, record
    which one bound, and pin the boundary as INCLUSIVE at 60,000. That limitation is
    published, not buried.

So this module answers **three** questions on every call, and :class:`NDecision` carries all
three, because *"record which one bound"* is a requirement and not a courtesy:

  1. does the **first** conjunct hold — measured tokens/episode ≤ the target, **inclusive**;
  2. does the **second** hold — projected Gemma lane-time ≤ the lane-hour budget;
  3. **which of them bound**, named.

⚠️ **AND THE RULING'S "REGARDLESS" CLAUSE IS TRUE UNDER ONE OF ITS TWO ARITHMETICS AND FALSE
UNDER THE OTHER — MEASURED, NOT ASSUMED. `QUESTIONS.md` `Q-121`.**

The second conjunct can be evaluated two ways, and `Q-107`'s options 2 and 3 are exactly
these two:

  * **RECOMPUTED** (`Q-107` option 2) — the projection is re-evaluated with the attacker's
    per-episode figure replaced by the **measured** one. This is what `Q-107`'s own published
    table does, and :func:`select_n` reproduces all four of its rows.
  * **AT THE REGISTERED TARGET** (`Q-107` option 3) — the projection is §13.4's own **published
    table for the N=50 branch**, computed at the pre-registered 60,000-token target, i.e.
    **40.05 h whatever the pilot measures**.

⚠️ **MEASURED BY THIS SESSION, and it is why `Q-121` exists:** under the RECOMPUTED reading the
second conjunct **holds** at any measured figure up to **31,908** tokens/episode (32.00 h) and
fails from **31,909** (32.01 h). Golden 8 fixture F's own first vector is **24,310**, which is
below that break-even — so at that vector the RECOMPUTED reading selects **N=50** and the
ruling's *"fails the second regardless of what the pilot measures"* **does not hold**. Under
the AT-THE-REGISTERED-TARGET reading it holds at every measurement, and `branch_a_n: 50` is
unreachable.

**BOTH ARE COMPUTED AND BOTH ARE CARRIED** on :class:`NDecision`, and neither is adjusted
toward the other. :attr:`NDecision.n` is the RECOMPUTED reading, because that is the one that
reproduces the architect's own `Q-107` table on 4 of 4 vectors;
:attr:`NDecision.n_at_registered_target` is the other, beside it, so the ruling's own sentence
is a **checkable claim in the run record** rather than a premise nobody re-ran. `Q-121` raises
the divergence; this session settles nothing.

`Q-107`'s last sentence says what to do with the limitation either way: **published, not
buried.** :func:`limitation` is that sentence as a string, so a report can print it and cannot
forget to.

⚠️ **THIS MODULE DOES NOT EDIT `config/`.** It is a frozen pre-registration artefact and hard
rule 4 says a frozen artefact that is wrong is *not* edited — the run continues under the
frozen protocol and the defect is published as a limitation.

⚠️ **AND IT DOES NOT RESOLVE `n_decision.selected_branch`.** That sentinel is C14's, set by
the single-shot pilot. This module computes what the rule yields; it writes nothing.

--------------------------------------------------------------------------------------
⚠️ THE DIVERGENCE FROM GOLDEN 8 FIXTURE F, AND WHY NEITHER SIDE IS ADJUSTED
--------------------------------------------------------------------------------------

Golden 8 fixture F states four vectors and they reproduce **exactly** under the first conjunct
alone — which is the conjunct `PROCESS.md` §5.2 names golden 8 as pinning (*"the N decision
rule KEYS OFF MEASURED TOKENS/EPISODE"*). Under the ruled two-conjunct rule the **60,000**
vector yields **N=30** where the golden says **N=50**.

`tests/goldens/` is read-only. **Neither side is adjusted.** :func:`select_n_first_conjunct_only`
exists so the golden's four vectors have a function that reproduces them, and :func:`select_n`
is the ruled rule; `tests/test_c11_runner.py` asserts **both**, and asserts that they disagree
on exactly one vector — so the divergence is pinned as an assertion and a reader is told, by a
failing test, if either side later moves.

--------------------------------------------------------------------------------------
THE PROVENANCE OF EVERY NUMBER IN THE PROJECTION
--------------------------------------------------------------------------------------

**Read from `config/` (hard rule 9):**
  ``attacker.target_tokens_per_episode``     the first conjunct's boundary
  ``benign_solver.target_tokens_per_episode`` the solver column
  ``gate_judge.target_tokens_per_call``       the judge column
  ``attacker.turn_budget``                    calls per judged / user-simulated episode
  ``probe.n_cal``                             the CAL block's episodes
  ``selections.tau2_must_not_write_task_count`` T-NEG per arm
  ``selections.agentdojo_user_task_count``      AD-CMP per arm
  ``selections.tfp_task_count``                 T-FP per configuration
  ``n_decision.branch_a_n`` / ``branch_b_n``    the two branches

**Derived from `config/lanes.yaml`, not asserted:**
  the Gemma lane-hour rate = the combined TPM of the lanes whose dashboard label names
  Gemma, × 60 minutes. §13.4 states it as *"1.92M tokens/h (the two Gemma lanes' combined 32K
  TPM)"*, and 16,000 + 16,000 = 32,000 → 1,920,000/h. **It is computed, so a lane-limit change
  moves it**, and the loader **refuses** unless exactly two Gemma lanes are found.

**Parsed out of `CONTEXT.md` §13.4, because it is in NEITHER `config/` NOR §8.6's constants
table:**
  the **lane-hour budget** (*"≤ 32 h"*). ⚠️ `config/protocol.yaml`'s own header says *"A
  constant that is not in that table and not in this file is a defect, and finding one is a
  review BLOCKER"*, and this is one — raised as `QUESTIONS.md` **Q-120**. It is **parsed**
  rather than transcribed for the reason `tests/test_tripwire_registry.py` gives about §8.6
  itself: *"A transcription would be one more copy of the table that can drift from it."*
  Parsing also means a missing sentence is a **refusal**, never a default.

**§13.4's own component table, transcribed with the cells that have no config key named as
such** — :data:`S13_4_COMPONENTS`. ⚠️ **The control on that transcription is that all THREE of
§13.4's published branch totals reproduce from it** — 76.90M/40.05 h, 69.10M/35.99 h and
59.30M/30.89 h — so a wrong cell would have to be wrong in a way that leaves three independent
sums right. `tests/test_c11_runner.py` asserts all three.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from .. import config as cfg

# --------------------------------------------------------------------------------------
# §13.4's component table. Transcribed; each cell's provenance named.
# --------------------------------------------------------------------------------------

#: The five arms. `PROTOCOL.md` §2.1: *"The five arms. Five, everywhere."* Not in `config/`.
ARMS = 5

#: Arms 2 / 2S / 3 — the three that run a gate judge. `PROTOCOL.md` §2.1. Not in `config/`.
JUDGED_ARMS = 3

#: The PILOT's reference-attacker half: *"1 ref arm + L2 × 10"*, §13.4's block table, of which
#: the reference attacker carries ten. Not in `config/`.
PILOT_REFERENCE_EPISODES = 10

#: The reference attacker's own ladder cell: *"2 arms × 4 points × 5"*, of which REF holds
#: two cells of five = ten episodes. §13.4's feasibility bullet says *"10 (its ladder cell)"*.
LADDER_REFERENCE_EPISODES = 10

#: M-BEN: *"5 configs × 30 scenarios"*. The scenario count is C12's deliverable and is in
#: neither `config/` nor §8.6. Not in `config/`.
BENIGN_SCENARIOS_PER_CONFIG = 30

#: The one pre-declared further reduction: T-FP cut from 40 to 20 τ² tasks.
#: `config/protocol.yaml`'s ``n_decision.fallback_if_branch_b_still_exceeds``. The **40** is in
#: `config/` at ``selections.tfp_task_count``; **this** is the reduced figure and is not.
TFP_REDUCED = 20

#: Minutes in an hour. Not a spec constant; arithmetic.
_MINUTES_PER_HOUR = 60

#: Which cells above carry no `config/` key, named so a reader does not have to work it out.
#: ⚠️ `QUESTIONS.md` **Q-120**.
S13_4_COMPONENTS: dict[str, int] = {
    "arms": ARMS,
    "judged_arms": JUDGED_ARMS,
    "pilot_reference_episodes": PILOT_REFERENCE_EPISODES,
    "ladder_reference_episodes": LADDER_REFERENCE_EPISODES,
    "benign_scenarios_per_config": BENIGN_SCENARIOS_PER_CONFIG,
    "tfp_reduced": TFP_REDUCED,
}


class NRuleError(RuntimeError):
    """A value the rule needs is absent or ambiguous. Always a refusal, never a default."""


# --------------------------------------------------------------------------------------
# The two constants that are not in config/
# --------------------------------------------------------------------------------------

#: ⚠️ The sentence in `CONTEXT.md` §13.4 that carries the lane-hour budget. Anchored on the
#: rule's own wording so it cannot match §13.4's *projected* figures, which are also hours.
_LANE_HOUR_BUDGET_PATTERN = re.compile(
    r"projected total Gemma lane-time \(§13\.4\) is\s*≤\s*(\d+)\s*h"
)


def lane_hour_budget(context_md: Path | None = None) -> Decimal:
    """The second conjunct's threshold, **parsed** out of `CONTEXT.md` §13.4's own rule.

    ⚠️ **REFUSES** on zero matches and on more than one. Two different budgets in the law is a
    contradiction a session must STOP on (hard rule 1), not average.
    """
    path = context_md or (cfg.repo_root() / "CONTEXT.md")
    if not path.is_file():
        raise NRuleError(
            f"{path} does not exist, and the lane-hour budget lives in NEITHER config/ NOR "
            f"CONTEXT.md §8.6's constants table — it is only in §13.4's prose (Q-120). There "
            f"is no default: hard rule 9 makes a missing required value a hard refusal"
        )
    matches = _LANE_HOUR_BUDGET_PATTERN.findall(path.read_text(encoding="utf-8"))
    if len(matches) != 1:
        raise NRuleError(
            f"expected exactly ONE statement of the projected-lane-time threshold in "
            f"{path.name} §13.4's decision rule; found {len(matches)}: {matches}. Zero means "
            f"the sentence moved and this rule no longer has its threshold; more than one "
            f"means the law states two, which is a STOP under hard rule 1, not an average"
        )
    return Decimal(matches[0])


def gemma_tokens_per_lane_hour() -> int:
    """The Gemma lanes' combined throughput per hour, **computed from `config/lanes.yaml`**.

    §13.4: *"Lane-time is `total ÷ 1.92M tokens/h` (the two Gemma lanes' combined 32K TPM)."*
    So this is a **derived** figure, not a constant, and it moves if a lane limit moves.

    ⚠️ **REFUSES unless exactly two Gemma lanes are found.** §13.4's arithmetic is stated over
    *"the two Gemma lanes"*; a third, or a rename that leaves one, would silently change every
    projected hour, and a silent change to the number that decides N is the failure mode this
    whole chunk exists around.
    """
    lanes = cfg.load("lanes").require("lanes")
    gemma = [lane for lane in lanes if str(lane.get("dashboard_label", "")).startswith("Gemma")]
    if len(gemma) != 2:
        raise NRuleError(
            f"CONTEXT.md §13.4 computes lane-time over 'the two Gemma lanes'; config/lanes.yaml "
            f"has {len(gemma)}: {[lane.get('name') for lane in gemma]}. This is not defaulted"
        )
    combined_tpm = 0
    for lane in gemma:
        if "tpm" not in lane:
            raise NRuleError(f"lane {lane.get('name')!r} states no tpm; hard rule 9 refuses")
        combined_tpm += int(lane["tpm"])
    return combined_tpm * _MINUTES_PER_HOUR


# --------------------------------------------------------------------------------------
# The projection — §13.4's component table, re-evaluated at a branch
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Projection:
    """One branch's projected token total and Gemma lane-hours, **broken out by component**.

    ⚠️ **BY COMPONENT, BECAUSE A BARE TOTAL IS WHAT HID THE LAST ERROR.** §13.4's own words,
    about its own corrected arithmetic (`Q-013`): until v1.1 two fallback rows were wrong, and
    *"each subtracted the reference attacker's reduction and omitted the gate judge's"*. A
    total that cannot be checked against its parts is a number nobody can audit.
    """

    n: int
    tfp_tasks: int
    measured_tokens_per_episode: int
    attacker_episodes: int
    attacker_tokens: int
    benign_episodes: int
    benign_tokens: int
    judge_episodes: int
    judge_tokens: int
    user_sim_episodes: int
    user_sim_tokens: int

    @property
    def total_tokens(self) -> int:
        return (
            self.attacker_tokens + self.benign_tokens + self.judge_tokens + self.user_sim_tokens
        )

    def lane_hours(self, tokens_per_lane_hour: int) -> Decimal:
        """Projected Gemma lane-hours, quantised to two places, ROUND_HALF_UP.

        Two places because §13.4 publishes two — 40.05 h, 35.99 h, 30.89 h — and a comparison
        against the budget must be made on the same figure the spec published, not on a
        longer one that could fall the other side of it.
        """
        return (Decimal(self.total_tokens) / Decimal(tokens_per_lane_hour)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def lines(self) -> list[str]:
        """The projection as ASCII lines, component by component."""
        return [
            f"branch N={self.n}, T-FP={self.tfp_tasks}, "
            f"measured tokens/episode={self.measured_tokens_per_episode}",
            f"  attacker      : {self.attacker_episodes:>4} ep = {self.attacker_tokens:>12,}",
            f"  benign solver : {self.benign_episodes:>4} ep = {self.benign_tokens:>12,}",
            f"  gate judge    : {self.judge_episodes:>4} ep = {self.judge_tokens:>12,}",
            f"  tau2 user sim : {self.user_sim_episodes:>4} ep = {self.user_sim_tokens:>12,}",
            f"  TOTAL                    = {self.total_tokens:>12,}",
        ]


def project_total_tokens(
    *, n: int, tfp_tasks: int, measured_tokens_per_episode: int
) -> Projection:
    """§13.4's component table, re-evaluated at ``n`` and ``tfp_tasks``. **Pure but for config.**

    Every episode count moves exactly as §13.4's block table requires:

      * **attacker** = CAL + pilot-ref + (arms × N) M-ADV + (arms × T-NEG) + (arms × AD-CMP)
        + its ladder cell. At N=50 that is 30 + 10 + 250 + 170 + 80 + 10 = **550**;
        at N=30, **450**.
      * **benign solver** = (configs × scenarios) M-BEN + (configs × T-FP). At T-FP 40 that is
        150 + 200 = **350**; at T-FP 20, **250**.
      * **gate judge** = judged arms × (N + T-NEG + AD-CMP + M-BEN + T-FP) episodes, each
        costing turn-budget judge calls. At N=50/T-FP 40 that is 3 × 170 = **510**.
      * **τ² user simulator** = (T-NEG + configs × T-FP) episodes, each of turn-budget turns.
        At T-FP 40 that is 170 + 200 = **370**.

    ⚠️ **AD-CMP IS INCLUDED, AND IT IS *NOT RUN*.** `PROTOCOL.md` §5.2 records the whole block
    cut at degradation rung 3 (`INC-62`). It is included here anyway, deliberately: `Q-107`'s
    ruling reasons *"on S13.4's own figures"*, and §13.4's own figures are the ones that carry
    AD-CMP. A projection that quietly dropped it would no longer reproduce the 76.90M and
    40.05 h the ruling is stated against, and the rule would stop being checkable against the
    published table. **The cut is a fact about what runs; this is a projection about what
    §13.4 published.** They are different claims and this note is here so nobody merges them.
    """
    protocol = cfg.load("protocol")
    turn_budget = int(protocol.require("attacker.turn_budget"))
    judge_tokens_each = int(protocol.require("gate_judge.target_tokens_per_call"))
    solver_per_episode = int(protocol.require("benign_solver.target_tokens_per_episode"))
    cal_episodes = int(protocol.require("probe.n_cal"))
    tneg_per_arm = int(protocol.require("selections.tau2_must_not_write_task_count"))
    adcmp_per_arm = int(protocol.require("selections.agentdojo_user_task_count"))

    attacker_episodes = (
        cal_episodes
        + PILOT_REFERENCE_EPISODES
        + ARMS * n
        + ARMS * tneg_per_arm
        + ARMS * adcmp_per_arm
        + LADDER_REFERENCE_EPISODES
    )
    benign_episodes = ARMS * BENIGN_SCENARIOS_PER_CONFIG + ARMS * tfp_tasks
    judge_episodes = JUDGED_ARMS * (
        n + tneg_per_arm + adcmp_per_arm + BENIGN_SCENARIOS_PER_CONFIG + tfp_tasks
    )
    user_sim_episodes = ARMS * tneg_per_arm + ARMS * tfp_tasks

    return Projection(
        n=n,
        tfp_tasks=tfp_tasks,
        measured_tokens_per_episode=measured_tokens_per_episode,
        attacker_episodes=attacker_episodes,
        attacker_tokens=attacker_episodes * measured_tokens_per_episode,
        benign_episodes=benign_episodes,
        benign_tokens=benign_episodes * solver_per_episode,
        judge_episodes=judge_episodes,
        judge_tokens=judge_episodes * turn_budget * judge_tokens_each,
        user_sim_episodes=user_sim_episodes,
        user_sim_tokens=user_sim_episodes * turn_budget * judge_tokens_each,
    )


# --------------------------------------------------------------------------------------
# The rule
# --------------------------------------------------------------------------------------

#: Names for what bound, so *"record which one bound"* is a value and not a sentence.
BOUND_BY_NEITHER = "neither - branch A holds"
BOUND_BY_TOKENS = "first conjunct - measured tokens/episode"
BOUND_BY_LANE_TIME = "second conjunct - projected Gemma lane-time"
BOUND_BY_BOTH = "both conjuncts"


@dataclass(frozen=True)
class NDecision:
    """What the rule yields, and **which conjunct bound**. `Q-107`'s ruling in one object.

    ⚠️ It carries the second conjunct **twice**, under both of `Q-107`'s readings, because
    they disagree below 31,909 measured tokens/episode and this session may not pick one
    silently. See this module's docstring and `Q-121`.
    """

    n: int
    measured_tokens_per_episode: int
    first_conjunct_holds: bool
    token_boundary: int
    second_conjunct_holds: bool
    projected_lane_hours: Decimal
    lane_hour_budget: Decimal
    bound_by: str
    projection: Projection

    #: `Q-107` option 3: the second conjunct against §13.4's **published** N=50 figures,
    #: computed at the pre-registered target rather than at the measured figure.
    second_conjunct_holds_at_registered_target: bool
    lane_hours_at_registered_target: Decimal
    n_at_registered_target: int

    @property
    def readings_agree(self) -> bool:
        """True when `Q-107`'s two readings select the same N at this measurement."""
        return self.n == self.n_at_registered_target

    def lines(self) -> list[str]:
        """The decision as ASCII lines. Both conjuncts, both readings, and what bound."""
        first = "HOLDS" if self.first_conjunct_holds else "FAILS"
        second = "HOLDS" if self.second_conjunct_holds else "FAILS"
        fixed = "HOLDS" if self.second_conjunct_holds_at_registered_target else "FAILS"
        return [
            f"N DECISION RULE (CONTEXT.md S13.4, Q-107 RULED) -> N = {self.n}",
            f"  measured tokens/episode   : {self.measured_tokens_per_episode}",
            f"  conjunct 1  measured <= {self.token_boundary}   : {first}  (INCLUSIVE)",
            f"  conjunct 2  {self.projected_lane_hours} h <= {self.lane_hour_budget} h : {second}"
            f"   [RECOMPUTED from the measured figure - Q-107 option 2]",
            f"  conjunct 2  {self.lane_hours_at_registered_target} h <= "
            f"{self.lane_hour_budget} h : {fixed}"
            f"   [AT THE REGISTERED TARGET - Q-107 option 3 -> N = "
            f"{self.n_at_registered_target}]",
            f"  BOUND BY                  : {self.bound_by}",
            f"  THE TWO READINGS AGREE    : {self.readings_agree}"
            + ("" if self.readings_agree else "   !! Q-121 - NEITHER SIDE ADJUSTED"),
            *[f"  {line}" for line in self.projection.lines()],
        ]


def select_n(measured_tokens_per_episode: int, *, context_md: Path | None = None) -> NDecision:
    """§13.4's rule with **BOTH** conjuncts. `Q-107`, RULED.

    The boundary on the first conjunct is **inclusive** — §13.4's own wording is *"tokens/episode
    is ≤ 60,000"* and golden 8 fixture F carries ``boundary_is_inclusive: true``.
    """
    if isinstance(measured_tokens_per_episode, bool) or not isinstance(
        measured_tokens_per_episode, int
    ):
        raise NRuleError(
            f"measured tokens/episode must be an integer; got "
            f"{measured_tokens_per_episode!r}. It is a MEASURED token count, and golden 8 is "
            f"integer tokens throughout"
        )

    protocol = cfg.load("protocol")
    boundary = int(protocol.require("attacker.target_tokens_per_episode"))
    branch_a_n = int(protocol.require("n_decision.branch_a_n"))
    branch_b_n = int(protocol.require("n_decision.branch_b_n"))
    tfp_tasks = int(protocol.require("selections.tfp_task_count"))

    first_holds = measured_tokens_per_episode <= boundary

    projection = project_total_tokens(
        n=branch_a_n,
        tfp_tasks=tfp_tasks,
        measured_tokens_per_episode=measured_tokens_per_episode,
    )
    budget = lane_hour_budget(context_md)
    rate = gemma_tokens_per_lane_hour()
    hours = projection.lane_hours(rate)
    second_holds = hours <= budget

    # Q-107 option 3, computed BESIDE option 2 rather than instead of it: S13.4's own
    # published figures for the N=50 branch, at the PRE-REGISTERED target. The ruling's
    # "regardless of what the pilot measures" is true of THIS reading and, measured, false
    # of the one above below 31,909 tokens/episode. Q-121. Neither side is adjusted.
    at_target = project_total_tokens(
        n=branch_a_n, tfp_tasks=tfp_tasks, measured_tokens_per_episode=boundary
    )
    hours_at_target = at_target.lane_hours(rate)
    second_holds_at_target = hours_at_target <= budget

    if first_holds and second_holds:
        bound_by = BOUND_BY_NEITHER
    elif not first_holds and not second_holds:
        bound_by = BOUND_BY_BOTH
    elif not first_holds:
        bound_by = BOUND_BY_TOKENS
    else:
        bound_by = BOUND_BY_LANE_TIME

    return NDecision(
        n=branch_a_n if (first_holds and second_holds) else branch_b_n,
        measured_tokens_per_episode=measured_tokens_per_episode,
        first_conjunct_holds=first_holds,
        token_boundary=boundary,
        second_conjunct_holds=second_holds,
        projected_lane_hours=hours,
        lane_hour_budget=budget,
        bound_by=bound_by,
        projection=projection,
        second_conjunct_holds_at_registered_target=second_holds_at_target,
        lane_hours_at_registered_target=hours_at_target,
        n_at_registered_target=(
            branch_a_n if (first_holds and second_holds_at_target) else branch_b_n
        ),
    )


def select_n_first_conjunct_only(measured_tokens_per_episode: int) -> int:
    """The rule **as golden 8 fixture F pins it** — the first conjunct alone.

    ⚠️ **THIS IS NOT THE RULED RULE.** It exists so the architect's four stated vectors have a
    function that reproduces them exactly, because `tests/goldens/` is read-only and
    `PROCESS.md` §5.2 names golden 8 as pinning *"the N decision rule, which KEYS OFF MEASURED
    TOKENS/EPISODE"* — the first conjunct, named. :func:`select_n` is what the runner uses.
    `Q-107` records both answers with neither side adjusted; ``test_c11_runner.py`` asserts
    both and pins the one vector on which they disagree.
    """
    protocol = cfg.load("protocol")
    boundary = int(protocol.require("attacker.target_tokens_per_episode"))
    if measured_tokens_per_episode <= boundary:
        return int(protocol.require("n_decision.branch_a_n"))
    return int(protocol.require("n_decision.branch_b_n"))


def limitation() -> str:
    """The published limitation. **`Q-107`'s ruling: *published, not buried*.**

    A string rather than a comment so a report **prints** it, and so a test can assert that a
    report does. A limitation that lives only in a docstring is buried by any other name.

    ⚠️ **IT STATES BOTH READINGS AND THE BREAK-EVEN, AND IT DOES NOT REPEAT THE RULING'S
    *"regardless"* AS AN UNQUALIFIED CLAIM.** An earlier version of this string did, and this
    module's own test refutes it under one of the two arithmetics — which would have made the
    published limitation carry a sentence the repository's own suite disproves. That is the
    exact failure `PROCESS.md` §9 exists about (*"three false claims about other people's code
    reached the specification before an audit caught them"*), committed against our own ruling
    instead of somebody else's paper. `Q-121`.
    """
    return (
        "LIMITATION, PUBLISHED (QUESTIONS.md Q-107 RULED, Q-121 OPEN): CONTEXT.md S13.4's N "
        "rule has TWO conjuncts - measured attacker tokens/episode <= the pre-registered "
        "target AND projected total Gemma lane-time <= the lane-hour budget. "
        "! THE SECOND CONJUNCT CAN BE EVALUATED TWO WAYS AND THEY DISAGREE, AND BOTH ARE "
        "PRINTED RATHER THAN ONE BEING CHOSEN SILENTLY. (a) AT THE REGISTERED TARGET - "
        "S13.4's own published figures for the N=50 branch, 76.90M = 40.05 h - the conjunct "
        "FAILS whatever the pilot measures, so n_decision.branch_a_n = 50 is a branch that "
        "CANNOT BE SELECTED and the rule yields N=30. S13.4 states this itself: 'N=50 is "
        "40.05 h on either arithmetic and fails the <= 32 h test either way.' "
        "(b) RECOMPUTED from the measured figure - which is what QUESTIONS.md Q-107's own "
        "published table does - the conjunct HOLDS up to 31,908 tokens/episode (32.00 h) and "
        "fails from 31,909 (32.01 h), so N=50 IS reachable below that break-even. Golden 8 "
        "fixture F's own first vector, 24,310 (29.83 h), is below it. "
        "! MEASURED BY C11, PINNED AS A TEST, AND NOT SETTLED HERE: which reading is the rule "
        "is QUESTIONS.md Q-121, deadline BEFORE C14's pilot selects a branch. "
        "config/ is a FROZEN pre-registration artefact and is NOT edited to tidy any of this "
        "away (hard rule 4): the defect is recorded and published. Golden 8 fixture F's 60,000 "
        "vector says N=50 under the FIRST CONJUNCT ALONE, which is the conjunct PROCESS.md "
        "S5.2 names golden 8 as pinning; tests/goldens/ is read-only and NEITHER SIDE IS "
        "ADJUSTED."
    )
