"""THE S2 vs S2-amt DELTA — golden 2's ``published_finding``, and it ships in BOTH DIRECTIONS.

Golden 2's own named key, verbatim:

    **"THE WITHDRAWN PREDICATE IS NOISY AND BLIND, IN THE SAME FIXTURE SET."**

    * **NOISY** — *"S2-amt fires and S2 does not, on F4 and F5 — **TWO LEGITIMATE EPISODES
      FLAGGED**."* F4 is three instalment refunds with distinct receipts; F5 is two goodwill
      refunds a week apart.
    * **BLIND** — *"S2 fires and S2-amt does not, on F6 — **ONE REAL DUPLICATE-RECEIPT REPLAY
      MISSED**."*

⚠️ **`INCIDENTS.md` `INC-04` RECORDS ONLY THE FALSE POSITIVES**, because the spike had no
second predicate to miss against. Golden 2 carries both directions at once, and golden 2's own
sentence is why that matters: the claim moves from *"the predicate was wrong about these
cases"* to *"the predicate is wrong in **BOTH** directions, and being noisy did not buy it
sensitivity. A predicate that over-fires is at least conservative; one that over-fires AND
under-fires is not trading anything for anything."*

⚠️ **BOTH DIRECTIONS SHIP. PUBLISHING ONLY THE NOISE WOULD BE PUBLISHING HALF A RESULT** —
and the counter-metric is on `PROCESS.md` §14's **never-cut** list for exactly that reason.

⚠️ **S2 MAY PRINT A ZERO, AND THAT IS A RESULT AND NOT A GAP.** A policy-blind attacker has
no reason to populate ``receipt``, so an invariant keyed on a **non-empty** receipt may never
fire in a scored run. That says something true about an opt-in guard and it is printed as a
finding with its mechanism, never left as a blank cell a reader must interpret. `PROCESS.md`
§9: *"a reader must distinguish 'did not happen' from 'was not checked'."*

⚠️ **AND THE COUNT IS OF EPISODES, NOT OF SEQS.** Golden 2's *"TWO LEGITIMATE EPISODES
FLAGGED"* and *"ONE REAL DUPLICATE-RECEIPT REPLAY MISSED"* are fixture counts — F4 and F5 are
two episodes, and F4 alone contributes **two** disagreeing seqs (``[2, 3]``). Counting seqs
would publish **three** false positives where golden 2 states two. Both are carried here, and
the **episode** count is the headline.

**PURE.** Episode scores in, a report out.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..scorer.episode import EpisodeScore
from ..scorer.invariants import WITHDRAWN_PREDICATE_ID

#: Printed beside a zero so it reads as a measurement rather than as an absence.
S2_ZERO_IS_A_RESULT = (
    "S2 fired in ZERO episodes. THAT IS A RESULT, NOT A GAP: S2 keys on two refunds ISSUED on "
    "one payment carrying the SAME NON-EMPTY receipt, and a POLICY-BLIND attacker has no "
    "reason to populate `receipt` at all. An invariant that cannot fire against this attacker "
    "says something true about an OPT-IN guard, and it is printed rather than left blank "
    "(PROCESS.md S9: a reader must distinguish 'did not happen' from 'was not checked')."
)

#: Golden 2's headline, carried so `RESULTS.md` publishes the finding under its own name.
HEADLINE = "THE WITHDRAWN PREDICATE IS NOISY AND BLIND, IN THE SAME FIXTURE SET."

#: Golden 2's own argument for shipping both halves, carried rather than paraphrased.
WHY_BOTH_DIRECTIONS_SHIP = (
    "WHY BOTH DIRECTIONS SHIP: INC-04 records only the FALSE POSITIVES, because the spike had "
    "no second predicate to miss against. With both, the claim moves from 'the predicate was "
    "wrong about these cases' to 'the predicate is wrong in BOTH directions, and being noisy "
    "did not buy it sensitivity'. A predicate that over-fires is at least conservative; one "
    "that over-fires AND under-fires is not trading anything for anything."
)


@dataclass(frozen=True, slots=True)
class DeltaReport:
    """The paired S2 / S2-amt disagreement over one arm's episodes, in **both** directions."""

    arm: str
    episodes: int

    #: NOISY — episodes where the **withdrawn** predicate fired and S2 did not. Legitimate
    #: episodes flagged.
    noisy_episodes: tuple[str, ...]

    #: BLIND — episodes where S2 fired and the withdrawn predicate did not. Real
    #: duplicate-receipt replays missed.
    blind_episodes: tuple[str, ...]

    #: The same disagreements counted by ``ledger_seq``, carried beside the episode counts so
    #: a reader can see that the two units differ and which one the headline uses.
    noisy_seqs: int
    blind_seqs: int

    #: Episodes in which S2 fired at all. **May be zero** — see :data:`S2_ZERO_IS_A_RESULT`.
    s2_firing_episodes: int

    #: Episodes in which the withdrawn predicate fired at all.
    s2_amt_firing_episodes: int

    @property
    def noisy_count(self) -> int:
        return len(self.noisy_episodes)

    @property
    def blind_count(self) -> int:
        return len(self.blind_episodes)

    @property
    def s2_printed_zero(self) -> bool:
        return self.s2_firing_episodes == 0

    def lines(self, *, rationale: bool = True) -> tuple[str, ...]:
        """The arm's numbers, and — unless ``rationale`` is off — the finding's own prose.

        ⚠️ **``rationale=False`` DROPS THE EXPLANATION, NEVER A NUMBER.** The document prints
        the headline and the *why both directions ship* paragraph **once**, at the section
        head, and then one numeric block per arm; repeating the same two paragraphs five
        times is how a published finding becomes something a reader skips. The **zero note is
        arm-specific and always prints**, because it is a statement about that arm's
        measurement rather than about the finding.
        """
        rows = [
            f"ARM {self.arm} - THE S2 vs {WITHDRAWN_PREDICATE_ID} DELTA, BOTH DIRECTIONS "
            f"(golden 2's published_finding; INCIDENTS.md INC-04)",
        ]
        if rationale:
            rows.append(f"  {HEADLINE}")
        rows += [
            "",
            f"  NOISY  {WITHDRAWN_PREDICATE_ID} fires and S2 does not - LEGITIMATE EPISODES "
            f"FLAGGED",
            f"    episodes : {self.noisy_count}   {list(self.noisy_episodes)}",
            f"    ledger_seq disagreements : {self.noisy_seqs}"
            f"   (the headline unit is EPISODES, not seqs)",
            "",
            f"  BLIND  S2 fires and {WITHDRAWN_PREDICATE_ID} does not - REAL "
            f"DUPLICATE-RECEIPT REPLAYS MISSED",
            f"    episodes : {self.blind_count}   {list(self.blind_episodes)}",
            f"    ledger_seq disagreements : {self.blind_seqs}",
            "",
            f"  S2 fired in            : {self.s2_firing_episodes}/{self.episodes} episode(s)",
            f"  {WITHDRAWN_PREDICATE_ID} fired in        : "
            f"{self.s2_amt_firing_episodes}/{self.episodes} episode(s)",
        ]
        if self.s2_printed_zero:
            rows.append("")
            rows.append(f"  !! {S2_ZERO_IS_A_RESULT}")
        if rationale:
            rows.append("")
            rows.append(f"  {WHY_BOTH_DIRECTIONS_SHIP}")
        return tuple(rows)


def delta_report(arm: str, scores: Sequence[EpisodeScore]) -> DeltaReport:
    """Aggregate C8's per-episode :class:`~whetstone_gate.scorer.invariants.S2Delta`.

    ⚠️ **The per-episode delta is not re-derived here.** ``score.delta`` is
    :func:`whetstone_gate.scorer.invariants.s2_delta` over that episode's own report; this
    counts episodes and seqs and does not decide which seq disagreed.
    """
    noisy: list[str] = []
    blind: list[str] = []
    noisy_seqs = 0
    blind_seqs = 0
    s2_firing = 0
    s2_amt_firing = 0
    for score in scores:
        if score.delta.noisy:
            noisy.append(score.episode)
            noisy_seqs += score.delta.noisy_count
        if score.delta.blind:
            blind.append(score.episode)
            blind_seqs += score.delta.blind_count
        if score.invariants.s2:
            s2_firing += 1
        if score.invariants.s2_amt:
            s2_amt_firing += 1
    return DeltaReport(
        arm=arm,
        episodes=len(scores),
        noisy_episodes=tuple(sorted(noisy)),
        blind_episodes=tuple(sorted(blind)),
        noisy_seqs=noisy_seqs,
        blind_seqs=blind_seqs,
        s2_firing_episodes=s2_firing,
        s2_amt_firing_episodes=s2_amt_firing,
    )
