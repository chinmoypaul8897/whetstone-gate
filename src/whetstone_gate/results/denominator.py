"""HARD RULE 11'S DENOMINATOR, AT PUBLICATION TIME — and it is Razorpay's own B.9.

    **NO SILENT DENOMINATOR SHRINKAGE.** *"Score complete trials only. Do not let retries,
    fallbacks, skipped cases, or missing traces quietly shrink the denominator."* Every
    dropped episode is counted, categorised and printed as a number. **A truncated episode
    is counted in the denominator.**

⚠️ **THIS IS THE THING THIS PROJECT CRITICISES IN EVERYBODY ELSE'S NUMBERS**, so it is an
**identity that can fail** rather than a habit: :meth:`BlockDenominator.reconcile` refuses
unless ``offered == scored + dropped``, and it is driven at a broken input in
``tests/test_c18_results.py``. A counter that cannot disagree with itself has measured
nothing.

⚠️ **AND C18 ADDS THE ONE TERM THE SCORER'S OWN COUNTER CANNOT SEE: THE PRE-REGISTERED N.**
:class:`~whetstone_gate.scorer.drops.DropLedger` reconciles what the scorer was *offered*.
It cannot know that the protocol pre-registered **fifty** and the sweep offered **forty-one**
— that fact lives in `PROTOCOL.md`, not in any ledger. `PROCESS.md` §14, verbatim:

    **N IS NOT A RUNG.** … *"If the sweep cannot finish the pre-registered N, the episodes
    that did not run are reported as an incomplete denominator — counted, categorised and
    printed (rule 11) — and the number is published with its real n. Quietly shrinking N to
    a number the schedule can reach is the precise thing rule 11 and B.9 forbid."*

So :attr:`BlockDenominator.never_offered` is printed **as a number, including when it is
zero**, and :meth:`reconcile` refuses a block that claims more episodes than the protocol
registered.

⚠️ **EVERY DECLARED DROP CATEGORY PRINTS, INCLUDING THE ZEROS.** An absent line and a zero
are not the same statement: the first says nothing was measured, the second says something
was measured and came to nothing. That is `OPEN_FINDINGS.md` **OF-03**'s doctrine, applied
to a denominator.

⚠️ **TRUNCATION IS NOT A DROP CATEGORY AND THAT IS THE POINT.** Rule 11 says a truncated
episode is **counted in the denominator**, so it is SCORED and carries a flag whose total is
printed beside the drops. Filing truncation under *"dropped"* would be the exact shrinkage
the rule forbids, wearing the rule's own clothes.

**PURE.** Values in, lines out.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from ..scorer.drops import DROP_CATEGORIES, DropLedger


class DenominatorRefusal(AssertionError):
    """The denominator does not reconcile, or a block claims episodes nobody registered.

    Always a stop. A published number whose denominator does not add up is the failure this
    project's whole thesis is about, and warning about it would be a way of shipping it.
    """


@dataclass(frozen=True, slots=True)
class BlockDenominator:
    """One measurement block's denominator, whole: registered, offered, scored, dropped.

    ``block`` is the pre-registered block name — ``M-ADV``, ``T-NEG``, ``T-FP``, ``CAL``,
    ``AD-CMP`` — so a reader can line each row up against `PROTOCOL.md` §3's own table.
    """

    block: str
    pre_registered_n: int
    offered: int
    scored: int
    truncated_and_scored: int
    dropped_by_category: Mapping[str, int]

    @property
    def dropped(self) -> int:
        return sum(self.dropped_by_category.values())

    @property
    def never_offered(self) -> int:
        """§14's *"the episodes that did not run"*, as a number. **Printed even at zero.**"""
        return max(0, self.pre_registered_n - self.offered)

    @property
    def is_incomplete(self) -> bool:
        return self.never_offered > 0

    def reconcile(self) -> None:
        """Refuse unless the identity holds **and** the block fits inside its registered N."""
        if self.offered != self.scored + self.dropped:
            raise DenominatorRefusal(
                f"{self.block}: the denominator does not reconcile - {self.offered} offered "
                f"against {self.scored} scored + {self.dropped} dropped = "
                f"{self.scored + self.dropped}. Hard rule 11: an episode that is neither "
                f"scored nor dropped has left the denominator without saying so"
            )
        undeclared = sorted(set(self.dropped_by_category) - set(DROP_CATEGORIES))
        if undeclared:
            raise DenominatorRefusal(
                f"{self.block}: {undeclared} are not declared drop categories. The declared "
                f"set is {list(DROP_CATEGORIES)}; a category invented at the call site would "
                f"never be printed, which is hard rule 11's silent shrinkage under a new name"
            )
        if self.offered > self.pre_registered_n:
            raise DenominatorRefusal(
                f"{self.block}: {self.offered} episodes were offered against a "
                f"PRE-REGISTERED N of {self.pre_registered_n}. N is a frozen artefact "
                f"(PROTOCOL.md, CLAUDE.md hard rule 4); running MORE than was registered is "
                f"not a bonus, it is an unregistered sample, and publishing it as if it were "
                f"the registered one is the shape of every result this project criticises"
            )
        if self.truncated_and_scored > self.scored:
            raise DenominatorRefusal(
                f"{self.block}: {self.truncated_and_scored} truncated episodes against "
                f"{self.scored} scored. Truncation is a FLAG ON A SCORE, never a drop "
                f"category - rule 11 counts a truncated episode IN the denominator"
            )

    def lines(self) -> tuple[str, ...]:
        """The counter as ASCII lines. **Numbers, not prose. Every category, including zero.**"""
        rows = [
            f"  block                          : {self.block}",
            f"  pre-registered N               : {self.pre_registered_n}",
            f"  episodes offered               : {self.offered}",
            f"  episodes NEVER OFFERED         : {self.never_offered}"
            f"   (PROCESS.md S14: N is not a rung and is never quietly shrunk)",
            f"  episodes scored                : {self.scored}",
            f"    of which TRUNCATED           : {self.truncated_and_scored}"
            f"   (rule 11: counted IN the denominator, never a drop)",
            f"  episodes dropped               : {self.dropped}",
        ]
        for name in DROP_CATEGORIES:
            rows.append(f"    {name:<28}: {self.dropped_by_category.get(name, 0)}")
        rows.append(
            f"  RECONCILES                     : {self.offered} == {self.scored} + "
            f"{self.dropped}"
        )
        rows.append(
            f"  COMPLETE                       : "
            f"{'NO - published with its real n' if self.is_incomplete else 'YES'}"
        )
        return tuple(rows)


def block_from_drop_ledger(
    block: str, pre_registered_n: int, ledger: DropLedger
) -> BlockDenominator:
    """Lift C8's own counter into a published block, adding the pre-registered N term.

    ⚠️ **The scorer's counter is not re-implemented here.** It is the authority on offered /
    scored / dropped and this reads it; the one thing C18 adds is the term no ledger can
    carry — how many episodes the protocol registered and the sweep never reached.
    """
    return BlockDenominator(
        block=block,
        pre_registered_n=pre_registered_n,
        offered=ledger.offered,
        scored=ledger.scored,
        truncated_and_scored=ledger.truncated_and_scored,
        dropped_by_category=dict(ledger.by_category()),
    )


@dataclass(frozen=True, slots=True)
class DenominatorReport:
    """Every block's denominator, and the run total. ⚠️ **Refuses over the whole run.**"""

    blocks: tuple[BlockDenominator, ...]

    def reconcile(self) -> None:
        if not self.blocks:
            raise DenominatorRefusal(
                "a denominator report over ZERO blocks is not an empty result, it is an "
                "absent one. Rule 11's identity has nothing to hold, and a RESULTS.md "
                "printing no denominator at all is the omission the rule exists to prevent"
            )
        for block in self.blocks:
            block.reconcile()

    @property
    def offered(self) -> int:
        return sum(b.offered for b in self.blocks)

    @property
    def scored(self) -> int:
        return sum(b.scored for b in self.blocks)

    @property
    def dropped(self) -> int:
        return sum(b.dropped for b in self.blocks)

    @property
    def never_offered(self) -> int:
        return sum(b.never_offered for b in self.blocks)

    @property
    def pre_registered_n(self) -> int:
        return sum(b.pre_registered_n for b in self.blocks)

    def totals_by_category(self) -> dict[str, int]:
        """Run-wide totals, **every declared category, including the zeros.**"""
        counts = {name: 0 for name in DROP_CATEGORIES}
        for block in self.blocks:
            for name in DROP_CATEGORIES:
                counts[name] = counts[name] + block.dropped_by_category.get(name, 0)
        return counts

    def incomplete_blocks(self) -> tuple[str, ...]:
        return tuple(b.block for b in self.blocks if b.is_incomplete)

    def lines(self) -> tuple[str, ...]:
        rows: list[str] = []
        for block in self.blocks:
            rows.extend(block.lines())
            rows.append("")
        rows.append("RUN TOTAL")
        rows.append(f"  pre-registered N (all blocks)  : {self.pre_registered_n}")
        rows.append(f"  offered                        : {self.offered}")
        rows.append(f"  NEVER OFFERED                  : {self.never_offered}")
        rows.append(f"  scored                         : {self.scored}")
        rows.append(f"  dropped                        : {self.dropped}")
        for name, count in self.totals_by_category().items():
            rows.append(f"    {name:<28}: {count}")
        rows.append(
            f"  RECONCILES                     : {self.offered} == {self.scored} + "
            f"{self.dropped}"
        )
        incomplete = self.incomplete_blocks()
        rows.append(
            f"  INCOMPLETE BLOCKS              : "
            f"{', '.join(incomplete) if incomplete else 'none'}"
        )
        return tuple(rows)


def report_from_blocks(blocks: Sequence[BlockDenominator]) -> DenominatorReport:
    """Order the blocks by name so the same input renders byte-identically every time."""
    return DenominatorReport(blocks=tuple(sorted(blocks, key=lambda b: b.block)))
