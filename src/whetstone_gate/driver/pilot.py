"""**THE PILOT, DECLARED IN CODE AND READ FROM `config/` — never from a comment.**

`CONTEXT.md` §13.4's block table and `PROTOCOL.md` §3.1, verbatim on the same row:

    **PILOT** (31 Aug) | 1 ref arm + L2 × 10 | **20** episodes | ref + L2 (`qwen`)

and `PROTOCOL.md` §2.2:

    ⚠️ **THE PILOT SEEDS ARE DISJOINT FROM THE SCORED SET ON PURPOSE.** The pilot measures
    tokens/episode and **selects N**; running it on scored seeds would let the branch
    decision be made on a look at the episodes it decides the size of.

**Every figure below is read through the one loader** (hard rule 9): the seeds from
``seeds.pilot_first`` / ``seeds.pilot_last``, the turn budget from ``attacker.turn_budget``,
the lanes from ``config/lanes.yaml``. **Nothing here is a literal**, which is what the hard
rule 9 tripwire scans this file for.

--------------------------------------------------------------------------------------
⚠️ THE PILOT'S PURPOSE IS ONE NUMBER, AND THAT NUMBER SELECTS N
--------------------------------------------------------------------------------------

`CONTEXT.md` §13.4: *"the pilot MUST measure the actual figure and it selects the N branch"*.
:func:`measure_tokens_per_episode` produces it and :func:`decide_n` hands it to
:func:`whetstone_gate.runner.n_rule.select_n`, **which C11 already implements with BOTH
conjuncts** (`Q-107`, RULED; `Q-121`, OPEN). ⚠️ **This module wires that rule; it does not
re-derive it**, and it contains no arithmetic that could disagree with it.

⚠️ **THREE REFUSALS GUARD THE FIGURE, AND EACH ONE IS A WAY THE NUMBER COULD BE FLATTERED:**

  1. **A DRY RUN MAY NEVER SELECT N.** A transcript client's token counts are *the caller's
     numbers* (:mod:`whetstone_gate.driver.clients`), so a dry run measures the **harness**
     and never `CONTEXT.md` §13.4's tokens/episode. :func:`decide_n` refuses one outright.
  2. **A TRUNCATED EPISODE MAY NOT ENTER THE AVERAGE.** A truncated episode cost **less than
     a whole episode**, so dividing its cost by one whole episode reads **LOW** — and low is
     the direction that selects the **larger** N. That is `INCIDENTS.md` **INC-103**'s shape
     exactly: a denominator error running *backwards*, where it flatters. The truncated
     count is printed either way (hard rule 11); the **figure refuses**.
  3. **THE DIVISION ROUNDS UP.** ``ceil``, never ``floor``: §13.4's branch A is *"measured
     tokens/episode ≤ 60,000"*, so rounding **down** is the unsafe direction — it can select
     N=50 on a run that measured 60,000.4. Rounding up can only select the smaller N.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from whetstone_gate import config as cfg
from whetstone_gate.runner import lanes as runner_lanes
from whetstone_gate.runner import n_rule
from whetstone_gate.runner.episodes import EpisodeKey

#: The block name the pilot's checkpoints and episode files are keyed under. `PROTOCOL.md`
#: §3.1 names the blocks; this is that row's own label and it is not a spec **value**, so it
#: is not a `config/` key.
PILOT_BLOCK = "PILOT"

#: How the two pilot attacker roles are found in ``config/lanes.yaml``'s ``role`` prose.
#: ⚠️ **A SUBSTRING MATCH THAT REFUSES ON ZERO MATCHES AND ON MORE THAN ONE**, which is the
#: shape :func:`whetstone_gate.runner.n_rule.lane_hour_budget` already used for §13.4's
#: prose. `config/lanes.yaml` carries no machine-readable role **key** — only this sentence
#: — and that is raised as `QUESTIONS.md` **Q-143**, not worked around silently.
REFERENCE_ROLE_MARKER = "attacker: REFERENCE"
LADDER_L2_ROLE_MARKER = "ladder L2"
GATE_JUDGE_ROLE_MARKER = "gate judge for arms"


class PilotError(RuntimeError):
    """The pilot cannot be assembled or measured as specified. Always a refusal."""


@dataclass(frozen=True)
class PilotCell:
    """One attacker configuration of the pilot: a lane, and the seeds it carries."""

    lane: str
    attacker_model: str
    seeds: tuple[int, ...]


@dataclass(frozen=True)
class PilotMatrix:
    """The whole pilot: two cells, ten seeds each, one arm. **Read from `config/`.**

    ``arm`` has **no default and is not derived**. `CONTEXT.md` §13.4 and `PROTOCOL.md` §3.1
    both say *"1 ref arm"* and **neither says which**, and `config/` carries no key for it —
    so :func:`load_pilot` requires it from the caller and `QUESTIONS.md` **Q-144** asks the
    architect to rule it before the single-shot pilot runs. Choosing it here would be
    choosing a pre-registered parameter by preference.
    """

    arm: str
    turn_budget: int
    reference: PilotCell
    ladder_l2: PilotCell
    judge_lane: str

    @property
    def cells(self) -> tuple[PilotCell, ...]:
        return (self.reference, self.ladder_l2)

    @property
    def episode_count(self) -> int:
        """⚠️ **20**, and it is a *derived* number: two cells × the pilot seed block."""
        return sum(len(cell.seeds) for cell in self.cells)

    def keys(self) -> tuple[EpisodeKey, ...]:
        """Every episode key, in **deterministic** order — cell, then seed ascending.

        Sorted rather than iterated from a set, for the reason
        :meth:`whetstone_gate.runner.scheduler.Scheduler.pending` gives: a run whose
        dispatch order depends on a hash seed is a run whose partial results depend on it
        too, and *"kill mid-run and resume"* would then not be a repeatable demonstration.
        """
        return tuple(
            EpisodeKey(
                block=PILOT_BLOCK,
                arm=self.arm,
                seed_or_task=str(seed),
                attacker_model=cell.attacker_model,
            )
            for cell in self.cells
            for seed in cell.seeds
        )

    def dispatch_order(self, pending: Iterable[EpisodeKey]) -> list[EpisodeKey]:
        """``pending`` in dispatch order: **the scheduler's own key sort, unchanged.**

        ⚠️ **DECLARED RATHER THAN INHERITED, AND THAT IS THE WHOLE REASON THIS METHOD EXISTS.**
        :mod:`whetstone_gate.driver.run` used to dispatch whatever
        :meth:`whetstone_gate.runner.scheduler.Scheduler.pending` returned, so **every** block
        silently got that method's sort — which is arm-major, because :class:`EpisodeKey` is
        ordered on ``(block, arm, seed_or_task, attacker_model)``. For a block whose arms are a
        published comparison that default is wrong (:mod:`whetstone_gate.driver.scored`), and a
        matrix now says which order it runs in rather than receiving one.

        ⚠️ **FOR THE PILOT THE ANSWER IS THE ONE IT ALREADY HAD, AND IT MUST STAY THAT WAY.**
        ``evals/pilot/RUN_DECLARED.md`` is a committed, pushed pre-registration of a run that has
        already been spent (`INC-142`), so this block's dispatch order is a matter of record and
        not of preference. ``sorted`` here reproduces it exactly, and
        ``tests/test_c18_sweep.py`` asserts that it does — byte for byte against the list
        ``Scheduler.pending`` returns.
        """
        return sorted(pending)

    def lane_for(self, key: EpisodeKey) -> str:
        """Which lane an episode key runs on. **Refuses an unknown key**, never guesses."""
        for cell in self.cells:
            if key.attacker_model == cell.attacker_model:
                return cell.lane
        raise PilotError(
            f"{key.slug} names attacker model {key.attacker_model!r}, which is neither "
            f"pilot cell ({self.reference.attacker_model!r}, "
            f"{self.ladder_l2.attacker_model!r})"
        )

    def lines(self) -> list[str]:
        """The matrix as ASCII, so the operator sees what is about to run."""
        return [
            f"PILOT MATRIX  (CONTEXT.md S13.4 block table; PROTOCOL.md S3.1)",
            f"  arm                    : {self.arm}   (NOT in config/ - QUESTIONS.md Q-144)",
            f"  turn budget            : {self.turn_budget}   (attacker.turn_budget)",
            f"  reference lane         : {self.reference.lane} "
            f"[{self.reference.attacker_model}]  seeds {_render_seeds(self.reference.seeds)}",
            f"  ladder L2 lane         : {self.ladder_l2.lane} "
            f"[{self.ladder_l2.attacker_model}]  seeds {_render_seeds(self.ladder_l2.seeds)}",
            f"  gate-judge lane        : {self.judge_lane}",
            f"  EPISODES               : {self.episode_count}",
            f"  seeds are DISJOINT from the scored block on purpose (PROTOCOL.md S2.2)",
        ]


def _render_seeds(seeds: tuple[int, ...]) -> str:
    if not seeds:
        return "(none)"
    return f"{seeds[0]}..{seeds[-1]}"


def _one_lane_whose_role_says(marker: str) -> runner_lanes.Lane:
    """The single lane whose ``role`` contains ``marker``. **Refuses on 0 and on >1.**"""
    matches = [
        lane for lane in runner_lanes.load_lanes().values() if marker in lane.role
    ]
    if len(matches) != 1:
        raise PilotError(
            f"config/lanes.yaml has {len(matches)} lane(s) whose role contains {marker!r} "
            f"({sorted(lane.name for lane in matches)}). Exactly one is required: a role "
            f"that matches none leaves the pilot with no lane, and one that matches two "
            f"leaves it choosing. See QUESTIONS.md Q-143 - lanes.yaml carries this role as "
            f"PROSE and not as a key, and hard rule 9 makes the ambiguity a refusal"
        )
    return matches[0]


def pilot_seeds() -> tuple[int, ...]:
    """``seeds.pilot_first`` … ``seeds.pilot_last``, inclusive. **Through the one loader.**"""
    protocol = cfg.load("protocol")
    first = int(protocol.require("seeds.pilot_first"))
    last = int(protocol.require("seeds.pilot_last"))
    if last < first:
        raise PilotError(
            f"config/protocol.yaml gives seeds.pilot_first={first} above "
            f"seeds.pilot_last={last}; the pilot block would be empty"
        )
    return tuple(range(first, last + 1))


def load_pilot(*, arm: str) -> PilotMatrix:
    """Assemble the pilot from `config/`. ``arm`` is the caller's and has no default."""
    if not isinstance(arm, str) or not arm.strip():
        raise PilotError(
            "the pilot's arm must be named by the caller. CONTEXT.md S13.4 and PROTOCOL.md "
            "S3.1 both say '1 ref arm' and neither says WHICH, and config/ carries no key "
            "for it - QUESTIONS.md Q-144. Choosing it here would choose a pre-registered "
            "parameter by preference"
        )
    seeds = pilot_seeds()
    reference = _one_lane_whose_role_says(REFERENCE_ROLE_MARKER)
    ladder_l2 = _one_lane_whose_role_says(LADDER_L2_ROLE_MARKER)
    judge = _one_lane_whose_role_says(GATE_JUDGE_ROLE_MARKER)
    return PilotMatrix(
        arm=arm,
        turn_budget=int(cfg.load("protocol").require("attacker.turn_budget")),
        reference=PilotCell(
            lane=reference.name, attacker_model=reference.name, seeds=seeds
        ),
        ladder_l2=PilotCell(
            lane=ladder_l2.name, attacker_model=ladder_l2.name, seeds=seeds
        ),
        judge_lane=judge.name,
    )


# --------------------------------------------------------------------------------------
# The one number the pilot exists to produce
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class TokensPerEpisode:
    """The pilot's measurement, with **both** denominators and the refusal between them.

    ``over_completed`` is the figure §13.4's rule takes. ``over_denominator`` is the same
    tokens divided by hard rule 11's denominator (completed **+** truncated) and is carried
    **beside** it, never instead of it, so a reader can see the gap rather than take one
    number on trust.
    """

    attacker_tokens: int
    completed: int
    truncated: int

    @property
    def denominator(self) -> int:
        """Hard rule 11's denominator: **completed + truncated**."""
        return self.completed + self.truncated

    @property
    def over_completed(self) -> int:
        """Tokens ÷ completed episodes, **rounded UP**. Raises when nothing completed."""
        if self.completed <= 0:
            raise PilotError(
                "no pilot episode completed, so there is no tokens/episode figure. An "
                "average over zero episodes is not a small number, it is no number, and "
                "CONTEXT.md S13.4's N branch may not be selected from one"
            )
        return _ceil_div(self.attacker_tokens, self.completed)

    @property
    def over_denominator(self) -> int:
        """The same tokens over completed **+** truncated. ⚠️ **Reads LOW; disclosure only.**"""
        if self.denominator <= 0:
            raise PilotError("the pilot denominator is zero")
        return _ceil_div(self.attacker_tokens, self.denominator)

    @property
    def is_usable_for_n(self) -> bool:
        """True only when **every** pilot episode completed. See this module's docstring."""
        return self.completed > 0 and self.truncated == 0

    def lines(self, *, block: str = PILOT_BLOCK) -> list[str]:
        """ASCII. Both denominators, and the refusal stated as a value.

        ⚠️ **``block`` EXISTS BECAUSE THE CALIBRATION'S OWN REPORT MISNAMED ITSELF, MEASURED.**
        ``evals/cal/run-attempt4-20260904T204118Z.log`` prints ``block label : CAL`` at the top
        and then, at the bottom, ``PILOT MEASUREMENT`` over the calibration's thirty episodes —
        because this header was a literal. The slugs were right throughout (``cal__…``), so
        nothing computed was wrong, but **the printed record named the wrong run**, and a record
        that misnames the run it describes is the kind of thing a reader is entitled to hold
        against every other number beside it. It is a **label**, not a spec value (`cal.py` says
        so in terms), so its default is this class's own home block and every caller that knows
        better passes what it knows.
        """
        rendered = [
            f"{block} MEASUREMENT - attacker tokens per episode (CONTEXT.md S13.4)",
            f"  attacker tokens (API's OWN usage.total_tokens, never estimated) : "
            f"{self.attacker_tokens}",
            f"  episodes COMPLETED                                             : "
            f"{self.completed}",
            f"  episodes TRUNCATED (counted, hard rule 11)                     : "
            f"{self.truncated}",
        ]
        if self.completed > 0:
            rendered.append(
                f"  tokens/episode over COMPLETED  (the S13.4 figure, ceil)        : "
                f"{self.over_completed}"
            )
        if self.denominator > 0:
            rendered.append(
                f"  tokens/episode over DENOMINATOR (disclosure; reads LOW)         : "
                f"{self.over_denominator}"
            )
        rendered.append(
            f"  USABLE TO SELECT N                                             : "
            f"{self.is_usable_for_n}"
        )
        return rendered


def _ceil_div(numerator: int, denominator: int) -> int:
    """Integer ceiling division. ⚠️ **UP, because DOWN is the unsafe direction here.**"""
    return -((-numerator) // denominator)


def measure_tokens_per_episode(
    *, attacker_tokens: int, completed: int, truncated: int
) -> TokensPerEpisode:
    """The pilot's figure, from **counted** episodes and the provider's **own** token totals."""
    for name, value in (
        ("attacker_tokens", attacker_tokens),
        ("completed", completed),
        ("truncated", truncated),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise PilotError(f"{name} must be a non-negative integer; got {value!r}")
    return TokensPerEpisode(
        attacker_tokens=attacker_tokens, completed=completed, truncated=truncated
    )


def decide_n(measurement: TokensPerEpisode, *, dry_run: bool) -> n_rule.NDecision:
    """Hand the measured figure to §13.4's rule. ⚠️ **C11's rule, wired — never re-derived.**

    Refuses a dry run outright and refuses a measurement that carries a truncated episode.
    Both refusals are stated in this module's docstring with the direction each error runs.
    """
    if dry_run:
        raise PilotError(
            "a DRY RUN may not select the N branch. Its token counts are the caller's "
            "numbers, not a provider's (see driver/clients.py), so it measures the HARNESS "
            "and never CONTEXT.md S13.4's tokens/episode. The pilot is SINGLE-SHOT "
            "(PROCESS.md S6b) and its output directory is the record"
        )
    if not measurement.is_usable_for_n:
        raise PilotError(
            f"the pilot measured {measurement.completed} completed and "
            f"{measurement.truncated} TRUNCATED episode(s), so tokens/episode may not be "
            f"averaged: a truncated episode cost LESS than a whole one and divides as if it "
            f"were whole, which reads LOW - and low is the direction that selects the LARGER "
            f"N. That is INCIDENTS.md INC-103's shape, running where it flatters. The counts "
            f"are printed either way (hard rule 11); the figure refuses"
        )
    return n_rule.select_n(measurement.over_completed)


def exact_tokens_per_episode(measurement: TokensPerEpisode) -> Decimal:
    """The unrounded ratio, for a report that wants to show what the rounding did.

    ``Decimal`` and not a float: this repository does not put a binary float next to a
    number that decides a pre-registered branch (hard rule 7, §5.1), even when the number
    itself is only being printed.
    """
    if measurement.completed <= 0:
        raise PilotError("no completed episode; there is no ratio to render")
    return Decimal(measurement.attacker_tokens) / Decimal(measurement.completed)


def total_attacker_tokens(values: Iterable[int]) -> int:
    """Sum of per-episode attacker tokens. **A sum of measured integers, never an estimate.**"""
    total = 0
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise PilotError(f"a per-episode token count must be a non-negative int; got {value!r}")
        total += value
    return total
