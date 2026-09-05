"""**THE ARM-1 CALIBRATION BLOCK — the run that sets the void threshold, declared in code.**

`CONTEXT.md` §10.3 rule 1 and frozen `HOLES.md` §3.5 rule 1, verbatim on the same point:

    **ARM-1 CALIBRATION RUN** — arm 1 only, mock world, reference attacker, **turn budget
    20**, ``probe.n_cal = 30`` episodes, against the world that **already contains
    `pay_CANARYRECON`**. No other arm or configuration runs inside the calibration block.

⚠️⚠️ **WHY THIS MODULE EXISTS AT ALL — `QUESTIONS.md` `Q-189`, BLOCKER 1, MEASURED BY ARCH
PILOT RUN 5 AND RE-MEASURED BY ITS OWN ADVERSARIAL PASS:** *"There is no code path that runs
a calibration. This is not an ambiguity; it is an absence."* ``driver/pilot.py`` hardcodes
``PILOT_BLOCK``, ``load_pilot`` **always** builds two cells and **always** ten seeds, and
there was no ``load_cal``, no ``--block``, no ``--lane`` and no ``--seed-first``.
**`PROCESS.md` §12's C14 card step (c) had no implementation.**

⚠️ **AND THE HAZARD THAT MADE IT URGENT RATHER THAN TIDY (`Q-189` CORRECTION 2, MEASURED):**
forcing a calibration through the pilot path would **not** have been a harmless no-op. Only
11 of the pilot's 20 keys were checkpointed before its 429, so **nine `gemma-26b` episodes
would have been dispatched for real** — nine live episodes writing ledgers stamped
``block=PILOT`` at slugs ``pilot__1__<seed>__gemma-26b``, **byte-indistinguishable from the
pilot's own, in the same directory, with `evals/` append-only and deletion operator-only.**
A calibration run that way would have contaminated a completed single-shot record and could
not afterwards have been separated from it.

--------------------------------------------------------------------------------------
⚠️ THE BLOCK LABEL IS THE WHOLE POINT, AND IT REACHES EVERY KEY
--------------------------------------------------------------------------------------

:data:`CAL_BLOCK` is the first component of every
:class:`~whetstone_gate.runner.episodes.EpisodeKey` this matrix produces, and
:meth:`EpisodeKey.slug` joins the four components with ``"__"``, so **every checkpoint
filename and every ledger this block writes begins ``cal__``** — never ``pilot__`` and never
a scored block's stem. A CAL episode therefore **cannot be mistaken for a PILOT or a SCORED
one by any reader or by any later replay**, which is the property `Q-189`'s correction 2
found the pilot path could not offer.

--------------------------------------------------------------------------------------
⚠️ EVERY VALUE IS READ. NOTHING HERE IS CHOSEN BY THIS MODULE
--------------------------------------------------------------------------------------

======================  =====================================================
value                   where it comes from
======================  =====================================================
seeds 2201–2230         ``seeds.cal_first`` / ``seeds.cal_last`` — `Q-189`(a),
                        RULED 2026-09-04, Class A
episode count 30        ``probe.n_cal``; cross-checked against the seed block
turn budget 20          ``attacker.turn_budget``; §10.3 rule 1 says *"turn budget 20"*
arm ``"1"``             `CONTEXT.md` §10.3 rule 1 and **frozen** `HOLES.md` §3.5 rule 1,
                        both *"arm 1 only"* — see :data:`CAL_ARM`
the one cell            ``config/lanes.yaml``'s lane whose ``role`` names the reference
                        attacker; that role string literally contains **CAL**
======================  =====================================================

⚠️ **THE ARM IS NOT THE PILOT'S SITUATION AND THE DIFFERENCE IS DELIBERATE.**
:func:`whetstone_gate.driver.pilot.load_pilot` **requires the arm from its caller** because
`CONTEXT.md` §13.4 and `PROTOCOL.md` §3.1 both say *"1 ref arm"* and **neither says which**
(`QUESTIONS.md` **Q-144**). **The calibration's arm is not ambiguous in the same way**: two
artefacts, one of them frozen, both say *"arm 1"* **in terms**. So it is named here, with
both citations, and a test parses `CONTEXT.md` back and asserts it rather than trusting this
sentence.

⚠️ **ONE CELL, AND ITS EXCLUSIVITY WAS CONFIRMED RATHER THAN INFERRED.** `Q-189` CORRECTION 3
recorded, against itself, that *"ONE lane"* had been listed as **fixed** while its exclusivity
was **inferred** — §10.3's *"No other arm or configuration runs inside this calibration
block"* is about arms and configurations, and `gemma-31b` exists with the role
``reference-attacker overflow``. **The architect confirmed one cell on `gemma-26b` on
2026-09-04**, and that confirmation is what this module implements.

**PURE, except the readers that go through ``config/``'s one loader.**
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from whetstone_gate import config as cfg
from whetstone_gate.driver import pilot as pilot_module
from whetstone_gate.gates.verdict import ARMS
from whetstone_gate.runner.episodes import EpisodeKey

#: The block name every calibration checkpoint and ledger is keyed under. `PROTOCOL.md` §3.1
#: names the blocks; this is that row's own label. Like :data:`..pilot.PILOT_BLOCK` it is a
#: **label**, not a spec *value*, so it is not a ``config/`` key.
CAL_BLOCK = "CAL"

#: ⚠️ **`CONTEXT.md` §10.3 rule 1 — *"Arm 1 only, mock world, reference attacker"* — and
#: **frozen** `HOLES.md` §3.5 rule 1, *"arm 1 only"*. Two artefacts, one of them inside
#: `probe-v1`, both in terms.** Unlike the pilot's arm (`Q-144`), this one is not a choice.
CAL_ARM = "1"


class CalError(RuntimeError):
    """The calibration cannot be assembled as specified. **Always a refusal.**"""


@dataclass(frozen=True)
class CalCell:
    """The calibration's single attacker configuration: one lane, and the seeds it carries."""

    lane: str
    attacker_model: str
    seeds: tuple[int, ...]


@dataclass(frozen=True)
class CalMatrix:
    """The whole calibration: **one cell, thirty seeds, arm 1.** Read from ``config/``.

    ⚠️ **THE MEMBER NAMES MIRROR :class:`~whetstone_gate.driver.pilot.PilotMatrix` ON
    PURPOSE.** :mod:`whetstone_gate.driver.run` consumes ``arm``, ``turn_budget``, ``keys()``,
    ``lane_for()``, ``judge_lane`` and ``lines()``, and a calibration that needed its own
    runner would be a second, unreviewed execution path for the single most consequential run
    in the project.
    """

    arm: str
    turn_budget: int
    reference: CalCell
    judge_lane: str

    @property
    def cells(self) -> tuple[CalCell, ...]:
        """⚠️ **ONE.** §10.3: *"No other arm or configuration runs inside this block."*"""
        return (self.reference,)

    @property
    def episode_count(self) -> int:
        """⚠️ **30**, and it is *derived*: one cell × the CAL seed block."""
        return sum(len(cell.seeds) for cell in self.cells)

    def keys(self) -> tuple[EpisodeKey, ...]:
        """Every episode key, in **deterministic** order — cell, then seed ascending.

        Sorted rather than iterated from a set, for the reason
        :meth:`whetstone_gate.runner.scheduler.Scheduler.pending` gives: a run whose dispatch
        order depends on a hash seed is a run whose partial results depend on it too.

        ⚠️ **EVERY KEY CARRIES :data:`CAL_BLOCK`**, so every slug begins ``cal__``.
        """
        return tuple(
            EpisodeKey(
                block=CAL_BLOCK,
                arm=self.arm,
                seed_or_task=str(seed),
                attacker_model=cell.attacker_model,
            )
            for cell in self.cells
            for seed in cell.seeds
        )

    def dispatch_order(self, pending: Iterable[EpisodeKey]) -> list[EpisodeKey]:
        """``pending`` in dispatch order: **the scheduler's own key sort, unchanged.**

        ⚠️ **DECLARED RATHER THAN INHERITED.** See
        :meth:`whetstone_gate.driver.pilot.PilotMatrix.dispatch_order` for why every matrix now
        states its order instead of receiving :meth:`Scheduler.pending`'s.

        ⚠️ **FOR A ONE-ARM, ONE-CELL BLOCK THE TWO ORDERS ARE THE SAME LIST AND CANNOT DIVERGE.**
        Every key here shares a ``block``, an ``arm`` and an ``attacker_model``, so
        :class:`EpisodeKey`'s ordering reduces to ``seed_or_task`` ascending — which is exactly
        the order :meth:`keys` builds. The calibration is **spent and single-shot**
        (`PROCESS.md` §6b), so this method is required to change nothing, and
        ``tests/test_c18_sweep.py`` asserts the identity rather than reasoning about it.
        """
        return sorted(pending)

    def lane_for(self, key: EpisodeKey) -> str:
        """Which lane an episode key runs on. **Refuses an unknown key**, never guesses."""
        for cell in self.cells:
            if key.attacker_model == cell.attacker_model:
                return cell.lane
        raise CalError(
            f"{key.slug} names attacker model {key.attacker_model!r}, which is not the "
            f"calibration's single cell ({self.reference.attacker_model!r}). §10.3: 'No "
            f"other arm or configuration runs inside this calibration block'"
        )

    def lines(self) -> list[str]:
        """The matrix as ASCII, so the operator sees what is about to run."""
        return [
            "CAL MATRIX  (CONTEXT.md S10.3 rule 1; HOLES.md S3.5 rule 1 - FROZEN)",
            f"  block label            : {CAL_BLOCK}   (every checkpoint slug begins "
            f"'{CAL_BLOCK.lower()}__'; it can never read as PILOT or SCORED)",
            f"  arm                    : {self.arm}   (S10.3 'arm 1 only' - NOT the pilot's "
            f"Q-144 ambiguity)",
            f"  turn budget            : {self.turn_budget}   (attacker.turn_budget)",
            f"  reference lane         : {self.reference.lane} "
            f"[{self.reference.attacker_model}]  seeds "
            f"{_render_seeds(self.reference.seeds)}",
            f"  gate-judge lane        : {self.judge_lane}   (ZERO judge calls: arm 1 has no "
            f"gate. Named because run.py's preflight checks it)",
            f"  EPISODES               : {self.episode_count}   (probe.n_cal)",
            "  seeds are DISJOINT from the scored, ladder AND pilot blocks (Q-189(a)):",
            "    a calibration on scored seeds would fit the void threshold to the very",
            "    worlds it later judges",
            "  ⚠️ SINGLE-SHOT (PROCESS.md S6b): the FIRST execution that runs to completion",
            "    IS the run, and its output directory is the record whatever it contains",
        ]


def _render_seeds(seeds: tuple[int, ...]) -> str:
    if not seeds:
        return "(none)"
    return f"{seeds[0]}..{seeds[-1]}"


def cal_seeds() -> tuple[int, ...]:
    """``seeds.cal_first`` … ``seeds.cal_last``, inclusive. **Through the one loader.**

    ⚠️ **AND CROSS-CHECKED AGAINST ``probe.n_cal`` RATHER THAN TRUSTED.** `CONTEXT.md` §10.3
    rule 1 and `HOLES.md` §3.5 rule 1 both fix the calibration at ``n_cal`` episodes, and the
    seed block is what actually produces them. A band that did not carry exactly ``n_cal``
    seeds would run a **different-sized calibration than the one the spec pre-registers**,
    and hard rule 11 is precisely about a denominator that is not the declared one.
    """
    protocol = cfg.load("protocol")
    first = int(protocol.require("seeds.cal_first"))
    last = int(protocol.require("seeds.cal_last"))
    if last < first:
        raise CalError(
            f"config/protocol.yaml gives seeds.cal_first={first} above "
            f"seeds.cal_last={last}; the calibration block would be empty"
        )
    seeds = tuple(range(first, last + 1))
    declared = int(protocol.require("probe.n_cal"))
    if len(seeds) != declared:
        raise CalError(
            f"config/protocol.yaml's CAL seed block {first}..{last} carries {len(seeds)} "
            f"seeds but probe.n_cal is {declared}. CONTEXT.md S10.3 rule 1 and HOLES.md "
            f"S3.5 rule 1 both fix the calibration at n_cal episodes, so these two keys "
            f"disagreeing means the block that runs is not the block the spec "
            f"pre-registers (hard rule 11)"
        )
    return seeds


def load_cal() -> CalMatrix:
    """Assemble the arm-1 calibration from ``config/``. **Takes nothing from its caller.**

    ⚠️ **CONTRAST WITH :func:`..pilot.load_pilot`, WHICH REQUIRES ``arm``.** That signature
    exists because the pilot's arm is genuinely undetermined (`Q-144`). Every one of the
    calibration's parameters is fixed by `CONTEXT.md` §10.3 or by frozen `HOLES.md` §3.5, so
    an argument here would be an **invitation to vary a pre-registered parameter** on the one
    run that is single-shot and sets the threshold deciding whether the whole project's
    numbers are publishable.
    """
    if CAL_ARM not in ARMS:
        raise CalError(
            f"the calibration arm {CAL_ARM!r} is not one of the declared arms {list(ARMS)}"
        )
    reference = pilot_module._one_lane_whose_role_says(pilot_module.REFERENCE_ROLE_MARKER)
    judge = pilot_module._one_lane_whose_role_says(pilot_module.GATE_JUDGE_ROLE_MARKER)
    return CalMatrix(
        arm=CAL_ARM,
        turn_budget=int(cfg.load("protocol").require("attacker.turn_budget")),
        reference=CalCell(
            lane=reference.name, attacker_model=reference.name, seeds=cal_seeds()
        ),
        judge_lane=judge.name,
    )
