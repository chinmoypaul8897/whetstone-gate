"""The categorised drop counter — hard rule 11, and it is Razorpay's own B.9.

    **NO SILENT DENOMINATOR SHRINKAGE.** Razorpay's own B.9: *"Score complete trials only.
    Do not let retries, fallbacks, skipped cases, or missing traces quietly shrink the
    denominator."* Every dropped episode is counted, categorised and printed as a number.
    **A truncated episode is counted in the denominator.**

⚠️ **THIS IS THE THING THIS PROJECT CRITICISES IN EVERYBODY ELSE'S NUMBERS**, so it is built
now rather than later, and it is built as an **identity that can fail** rather than as a habit:
:meth:`DropLedger.reconcile` refuses unless ``offered == scored + dropped``. A counter that
cannot disagree with itself has measured nothing.

⚠️ **TRUNCATION IS NOT A DROP CATEGORY AND THAT IS THE POINT.** Rule 11 says a truncated
episode is **counted in the denominator**, so it is SCORED and carries a flag; the flag's total
is printed beside the drops because a reader judging the denominator needs it. Filing truncation
under "dropped" would be the exact shrinkage the rule forbids, wearing the rule's own clothes.

⚠️ **EVERY DECLARED CATEGORY PRINTS, INCLUDING THE ZEROS.** An absent line and a zero are not
the same statement: the first says nothing was measured, the second says something was measured
and came to nothing. That is `docs/reviews/OPEN_FINDINGS.md` OF-03's doctrine, applied to a
denominator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Mapping

# --------------------------------------------------------------------------------------
# The categories. B.9's four named causes, plus the four this project's own machinery has.
# --------------------------------------------------------------------------------------

#: The runner never executed the episode at all.
SKIPPED = "SKIPPED"

#: The episode ran and its ledger cannot be found. B.9's *"missing traces"*.
MISSING_TRACE = "MISSING_TRACE"

#: A superseded attempt. B.9's *"retries"* — the surviving attempt IS the episode, and this
#: category exists so the superseded one is visible rather than absent.
RETRY_SUPERSEDED = "RETRY_SUPERSEDED"

#: B.9's *"fallbacks"* — the episode ran against something other than the declared lane or
#: model, so it is not the episode the protocol names.
PROVIDER_FALLBACK = "PROVIDER_FALLBACK"

#: The ledger's hash chain did not verify. A tampered or corrupt ledger is **not scored**,
#: because every number this project publishes is a claim about what that chain says.
CHAIN_TAMPERED = "CHAIN_TAMPERED"

#: The stored seed does not regenerate a world containing the ledger's own targets. See
#: :func:`whetstone_gate.scorer.episode.seed_cross_check`.
SEED_MISMATCH = "SEED_MISMATCH"

#: A row could not be read as an action at all — a missing ``executed``, a non-integer
#: ``ledger_seq``, an amount that is not integer paise.
MALFORMED_LEDGER = "MALFORMED_LEDGER"

#: Everything the scorer refused, in print order. **Declared, so each one prints as a number
#: even when it is zero.**
DROP_CATEGORIES: tuple[str, ...] = (
    SKIPPED,
    MISSING_TRACE,
    RETRY_SUPERSEDED,
    PROVIDER_FALLBACK,
    CHAIN_TAMPERED,
    SEED_MISMATCH,
    MALFORMED_LEDGER,
)


class DenominatorError(AssertionError):
    """The offered / scored / dropped identity does not hold. Always a stop, never a warning."""


@dataclass(frozen=True)
class Drop:
    """One dropped episode: which one, which category, and why — in that episode's own words."""

    episode: str
    category: str
    reason: str


@dataclass
class DropLedger:
    """Every episode the scorer was offered, and what became of it.

    Mutable on purpose: it accumulates across a run. It is the one object in this package that
    is not frozen, and it holds no predicate logic.
    """

    offered: int = 0
    scored: int = 0
    truncated_and_scored: int = 0
    drops: list[Drop] = field(default_factory=list)

    def offer(self, count: int = 1) -> None:
        """Record that ``count`` episodes were handed to the scorer."""
        self.offered += count

    def score(self, *, truncated: bool) -> None:
        """Record one episode SCORED. A truncated one is scored and counted, per rule 11."""
        self.scored += 1
        if truncated:
            self.truncated_and_scored += 1

    def drop(self, episode: str, category: str, reason: str) -> None:
        """Record one episode NOT scored, under a **declared** category.

        An undeclared category is a refusal rather than a new bucket: a category invented at
        the call site would not appear in :attr:`DROP_CATEGORIES` and so would never print,
        which is the silent shrinkage this class exists to prevent.
        """
        if category not in DROP_CATEGORIES:
            raise DenominatorError(
                f"{category!r} is not a declared drop category. The declared set is "
                f"{list(DROP_CATEGORIES)}; a category invented at the call site would never "
                f"be printed, which is hard rule 11's silent shrinkage under a new name"
            )
        self.drops.append(Drop(episode=episode, category=category, reason=reason))

    # -- what a reader gets ------------------------------------------------------------

    @property
    def dropped(self) -> int:
        return len(self.drops)

    def by_category(self) -> dict[str, int]:
        """Every declared category and its count, **including the zeros**, in print order."""
        counts = {name: 0 for name in DROP_CATEGORIES}
        for entry in self.drops:
            counts[entry.category] += 1
        return counts

    def reconcile(self) -> None:
        """Refuse unless ``offered == scored + dropped``. The identity, checkable."""
        if self.offered != self.scored + self.dropped:
            raise DenominatorError(
                f"denominator does not reconcile: {self.offered} offered against "
                f"{self.scored} scored + {self.dropped} dropped = "
                f"{self.scored + self.dropped}. Hard rule 11: every dropped episode is "
                f"counted, categorised and printed as a number, and an episode that is "
                f"neither scored nor dropped has left the denominator without saying so"
            )

    def lines(self) -> Iterator[str]:
        """The counter as plain ASCII lines. **Numbers, not prose.**"""
        yield f"episodes offered              : {self.offered}"
        yield f"episodes scored               : {self.scored}"
        yield f"  of which TRUNCATED          : {self.truncated_and_scored}   (rule 11: counted in the denominator)"
        yield f"episodes dropped              : {self.dropped}"
        for name, count in self.by_category().items():
            yield f"  {name:<26}: {count}"
        yield f"reconciles                    : {self.offered} == {self.scored} + {self.dropped}"

    def render(self) -> str:
        """:meth:`lines` as one block, for a report or a test failure message."""
        return "\n".join(self.lines())

    def reasons(self) -> Mapping[str, tuple[str, ...]]:
        """Each dropped episode's category and reason, so a count is never the whole story."""
        return {entry.episode: (entry.category, entry.reason) for entry in self.drops}
