"""HARD RULE 11 FOR THE STATISTICS MODULE — every episode it drops, counted and printed.

    **NO SILENT DENOMINATOR SHRINKAGE.** Razorpay's own B.9: *"Score complete trials only. Do
    not let retries, fallbacks, skipped cases, or missing traces quietly shrink the
    denominator."* Every dropped episode is counted, categorised and printed as a number.
    **A truncated episode is counted in the denominator.**

⚠️ **THIS IS THE STATISTICS MODULE'S OWN DENOMINATOR, NOT THE SCORER'S.**
:mod:`whetstone_gate.scorer.drops` is the scorer's ledger of dropped episodes and it is not
imported here — see :mod:`whetstone_gate.probe.entries` for why ``probe/`` keeps its first-party
import closure to :mod:`~whetstone_gate.config` and :mod:`~whetstone_gate._console` alone.
What is **not** duplicated is the category vocabulary: this module declares none of its own, it
takes the categories as data, and
``test_c10_probe.py::test_the_census_categories_are_the_scorer_s_own_and_have_not_drifted``
imports ``scorer/drops.py`` and asserts they still agree. **The test couples; the module does
not.**

⚠️ **TRUNCATION IS NOT A DROP CATEGORY, AND ITS ABSENCE IS THE POINT.** Rule 11's last sentence
is explicit — a truncated episode is **counted in the denominator** — so a truncated episode is
*scored*, and :attr:`Census.truncated` is a memo about the scored population, never a subtrahend.
It is carried separately and printed separately so that a reader can see it was not quietly
dropped.

⚠️ **AND EVERY DECLARED CATEGORY PRINTS, INCLUDING THE ZEROS.** `PROCESS.md` §9: *"Zero-occurrence
branches are printed as zeros, never omitted. A reader must distinguish 'did not happen' from
'was not checked.'"* An absent line and a zero are not the same claim.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from .._console import ascii_safe


class DenominatorError(AssertionError):
    """The partition does not sum to its total. A published number is wrong until it does."""


@dataclass(frozen=True, slots=True)
class Census:
    """Attempted, scored, dropped-by-category, and the memo columns — one block's arithmetic."""

    block: str
    attempted: int
    dropped: Mapping[str, int]
    truncated: int = 0
    categories: tuple[str, ...] = field(default_factory=tuple)

    @property
    def dropped_total(self) -> int:
        return sum(self.dropped.values())

    @property
    def scored(self) -> int:
        """⚠️ **Attempted minus dropped. Truncated episodes are IN here, by rule 11.**"""
        return self.attempted - self.dropped_total

    def check(self) -> None:
        """Refuse a census whose parts do not reconcile. Raises :class:`DenominatorError`."""
        problems: list[str] = []
        if self.scored + self.dropped_total != self.attempted:
            problems.append(
                f"{self.scored} scored + {self.dropped_total} dropped != "
                f"{self.attempted} attempted"
            )
        if self.scored < 0:
            problems.append(f"{self.dropped_total} dropped exceeds {self.attempted} attempted")
        if self.truncated > self.scored:
            problems.append(
                f"{self.truncated} truncated exceeds {self.scored} scored - a truncated "
                f"episode is COUNTED IN the denominator (rule 11), so it cannot outnumber it"
            )
        unknown = sorted(set(self.dropped) - set(self.categories)) if self.categories else []
        if unknown:
            problems.append(
                f"categories invented at the call site would never print: {unknown}; "
                f"declared categories are {list(self.categories)}"
            )
        if problems:
            raise DenominatorError(
                f"block {self.block!r} does not reconcile: " + "; ".join(problems)
            )

    def lines(self) -> tuple[str, ...]:
        """The printable block. **Every declared category appears, zero or not.**"""
        self.check()
        out = [
            f"BLOCK {self.block}",
            f"  attempted            {self.attempted}",
            f"  scored               {self.scored}",
            f"    of which truncated {self.truncated}   "
            f"(COUNTED IN the denominator - hard rule 11)",
            f"  dropped              {self.dropped_total}",
        ]
        for category in self.categories or tuple(sorted(self.dropped)):
            out.append(f"    {category:<20} {self.dropped.get(category, 0)}")
        out.append(
            f"  reconciles           {self.scored} + {self.dropped_total} = {self.attempted}"
        )
        return tuple(ascii_safe(line) for line in out)

    def report(self) -> str:
        return "\n".join(self.lines())


def total_over(blocks: Sequence[Census]) -> Census:
    """Sum a set of blocks into one census, checking each and then the total.

    Every partition summing to its total is persona 1's *"denominator integrity"* checklist
    item, and it is checked here rather than asserted in prose.
    """
    if not blocks:
        raise DenominatorError("a total over zero blocks is not zero, it is nothing to report.")
    categories: tuple[str, ...] = blocks[0].categories
    merged: dict[str, int] = {}
    for block in blocks:
        block.check()
        for category, count in block.dropped.items():
            merged[category] = merged.get(category, 0) + count
    total = Census(
        block="ALL BLOCKS",
        attempted=sum(b.attempted for b in blocks),
        dropped=merged,
        truncated=sum(b.truncated for b in blocks),
        categories=categories,
    )
    total.check()
    if total.scored != sum(b.scored for b in blocks):
        raise DenominatorError(
            f"the total's scored count ({total.scored}) does not equal the sum of the blocks' "
            f"({sum(b.scored for b in blocks)}) - a partition that does not sum to its total"
        )
    return total
