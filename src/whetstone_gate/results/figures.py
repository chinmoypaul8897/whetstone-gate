"""EVERY PUBLISHED FIGURE CARRIES ITS CEILING, OR IT DOES NOT RENDER.

`CONTEXT.md` §12.4.4, which is the whole of this module's reason to exist:

    **"Blocked 100%" never ships without its ceiling.** Arm 4's expected 0/N is reported as
    *"0/N - 95% upper bound 6.0% at N=50, 10.0% at N=30"*, always, in the table and out loud
    in the video, using whichever branch the pilot selected.

⚠️ **A BARE COUNT IS A REFUSAL HERE, NOT A FORMATTING CHOICE.** :class:`Figure` accepts a
``None`` ceiling so that a careless caller *can* build one — and then :meth:`Figure.render`
raises :class:`CeilingMissing`, and
:func:`refuse_unless_every_figure_carries_its_ceiling` raises over a whole document. Both
refusals are **driven** at inputs built to break them in ``tests/test_c18_results.py``; a
guard that has never fired has measured nothing (`INCIDENTS.md` **INC-14**).

⚠️ **THE TWO CEILING METHODS ARE NOT INTERCHANGEABLE AND THE SWITCH IS `config/`'s.**
§12.4: *"the rule of three (3/n) at n ≥ 30 and the exact one-sided Clopper–Pearson bound
below it — they diverge sharply at small n, which is why the ladder uses the exact form."*
This module never names ``30``: ``rule_of_three_min_n`` arrives as an argument from the
shell, which read it through hard rule 9's one loader.

⚠️ **AND BOTH BRANCHES OF N ARE PRINTED, WITH THE ONE TAKEN NAMED.** `PROCESS.md` §12.1's
C18 row and §12.4.4 both quote the ceiling *at N=50 and at N=30*. C10 computed them; C18
prints both and says which bound — or says the pilot has not run, which is `QUESTIONS.md`
**Q-107**/**Q-121**'s standing state and is never rounded up to a decision.

**PURE.** No file, no clock, no network, no randomness. The confidence level and the switch
point are arguments, because the caller did the I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from typing import Iterable, Sequence

from ..probe.statistics import (
    clopper_pearson_zero_upper,
    rule_of_three_upper,
    wilson_interval,
)

#: Percentages are published to one decimal place, as `CONTEXT.md` §12.4's own table is.
_PCT = Decimal("0.1")

#: The two ceiling methods, **named in the output** rather than left implicit. A reader who
#: cannot tell which bound produced a number cannot check it.
RULE_OF_THREE = "rule of three (3/n)"
EXACT_ONE_SIDED = "exact one-sided Clopper-Pearson"
WILSON_SCORE = "Wilson score interval"

#: What :class:`ZeroCeilingBranches` prints when the pilot has not run. ⚠️ **NOT a default
#: and not a guess** — `Q-107`/`Q-121`: no session may say N is decided before the pilot,
#: and the architect's *"regardless"* clause is WITHDRAWN.
UNDECIDED = "UNDECIDED - the pilot has not run (Q-107, Q-121)"

#: `config/`'s ``statistics.quartile_method``. Named, because an unnamed method is an
#: unreproducible number — median and IQR on small samples swing materially between linear
#: interpolation, nearest-rank and Tukey hinges.
LINEAR = "linear"


class CeilingMissing(AssertionError):
    """A figure was asked to render without its ceiling. **Always a stop, never a warning.**

    §12.4.4's sentence is unconditional, and the number this project is most likely to
    publish is a column of zeros. A zero without its interval is the exact claim ~40 other
    Track 01 entrants publish and this project exists to criticise.
    """


def _round_pct(value: float) -> Decimal:
    """Render a computed proportion as a published percentage. ROUND_HALF_UP, never banker's."""
    return Decimal(repr(value * 100.0)).quantize(_PCT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True, slots=True)
class Ceiling:
    """What bounds a published rate, and by which method.

    :attr:`lower_pct` is ``None`` for the one-sided ceilings on an observed zero, where
    §12.4's own column is an **upper bound** and inventing a lower one would publish a
    second number nobody computed.
    """

    method: str
    upper_pct: Decimal
    level_pct: Decimal
    lower_pct: Decimal | None = None

    def phrase(self) -> str:
        if self.lower_pct is None:
            return f"{self.level_pct}% upper bound {self.upper_pct}%"
        return f"{self.level_pct}% CI {self.lower_pct}%-{self.upper_pct}%"


def ceiling_for(
    successes: int,
    n: int,
    *,
    level: float,
    rule_of_three_min_n: int,
) -> Ceiling:
    """The ceiling `CONTEXT.md` §12.4 attaches to an observed ``successes/n``.

    * **successes == 0** — §12.4's ceiling column: the rule of three at
      ``n >= rule_of_three_min_n`` and the exact one-sided Clopper–Pearson bound below it.
    * **successes > 0** — the two-sided **Wilson score** interval. §12.4's own ±pp column is
      a Wald half-width quoted *at a stated p*, which is a property of a design rather than
      of a measurement; a figure that has been measured gets the interval that covers it.

    A zero denominator is a refusal rather than a ceiling of zero: an arm with no episodes
    has measured nothing, and hard rule 11 is precisely about not letting an empty
    population read as a result.
    """
    if n <= 0:
        raise CeilingMissing(
            f"a ceiling over {n} observations is undefined, not zero. An arm with no "
            f"episodes has measured nothing, and publishing a bound over it would make an "
            f"absent denominator read as evidence (hard rule 11)"
        )
    if successes < 0 or successes > n:
        raise CeilingMissing(
            f"{successes}/{n} is not a proportion: the numerator is bounded by the "
            f"denominator, so a violation means the two were counted over different "
            f"populations"
        )
    level_pct = Decimal(repr(level * 100.0)).quantize(_PCT, rounding=ROUND_HALF_UP)
    if successes == 0:
        if n >= rule_of_three_min_n:
            return Ceiling(
                method=RULE_OF_THREE,
                upper_pct=_round_pct(rule_of_three_upper(n)),
                level_pct=level_pct,
            )
        return Ceiling(
            method=EXACT_ONE_SIDED,
            upper_pct=_round_pct(clopper_pearson_zero_upper(n, level)),
            level_pct=level_pct,
        )
    interval = wilson_interval(successes, n, level)
    return Ceiling(
        method=WILSON_SCORE,
        upper_pct=_round_pct(interval.upper),
        level_pct=level_pct,
        lower_pct=_round_pct(interval.lower),
    )


@dataclass(frozen=True, slots=True)
class Figure:
    """One published rate: a numerator, a denominator, and **its ceiling**.

    ``ceiling=None`` is constructible on purpose. It is how a caller gets a figure wrong,
    and it is how ``tests/test_c18_results.py`` **drives** the refusal instead of asserting
    that one exists.
    """

    name: str
    numerator: int
    denominator: int
    ceiling: Ceiling | None
    note: str = ""

    @property
    def exact(self) -> Fraction:
        """The rate as an exact rational. ⚠️ ``1/30`` does not terminate; the decimal is a view."""
        if self.denominator <= 0:
            raise CeilingMissing(
                f"{self.name}: a rate over {self.denominator} episodes is undefined, not zero"
            )
        return Fraction(self.numerator, self.denominator)

    @property
    def percent(self) -> Decimal:
        return _round_pct(float(self.exact))

    def render(self) -> str:
        """``k/n = p% - <ceiling>``. ⚠️ **Raises unless the ceiling is present.**"""
        if self.ceiling is None:
            raise CeilingMissing(
                f"{self.name}: {self.numerator}/{self.denominator} was about to be published "
                f"with NO CEILING. CONTEXT.md S12.4.4: a 'blocked 100%' never ships without "
                f"one. A bare count is a REFUSAL here, not a formatting choice - it is the "
                f"exact claim this project exists to criticise in ~40 other entrants' numbers"
            )
        body = (
            f"{self.numerator}/{self.denominator} = {self.percent}% - "
            f"{self.ceiling.phrase()} [{self.ceiling.method}]"
        )
        return f"{body}  {self.note}".rstrip()


def figure(
    name: str,
    numerator: int,
    denominator: int,
    *,
    level: float,
    rule_of_three_min_n: int,
    note: str = "",
) -> Figure:
    """Build a :class:`Figure` **with** its ceiling computed. The ordinary constructor."""
    return Figure(
        name=name,
        numerator=numerator,
        denominator=denominator,
        ceiling=ceiling_for(
            numerator, denominator, level=level, rule_of_three_min_n=rule_of_three_min_n
        ),
        note=note,
    )


def refuse_unless_every_figure_carries_its_ceiling(figures: Iterable[Figure]) -> None:
    """Document-level enforcement, over every figure the assembler is about to print."""
    bare = [f.name for f in figures if f.ceiling is None]
    if bare:
        raise CeilingMissing(
            f"{len(bare)} figure(s) carry no ceiling and would be published bare: {bare}. "
            f"CONTEXT.md S12.4.4 makes the ceiling unconditional, and PROCESS.md S12.1's C18 "
            f"row repeats it as \"every '0/N' ships its ceiling\""
        )


@dataclass(frozen=True, slots=True)
class ZeroCeilingBranches:
    """§12.4.4's *"6.0% at N=50, 10.0% at N=30"* — **both printed, and the one taken named.**

    ⚠️ **:attr:`taken` MAY BE :data:`UNDECIDED`, AND THAT IS A RESULT.** `Q-107` ruled the N
    rule has two conjuncts and `Q-121` measured that its two readings disagree below
    **31,908** measured tokens/episode. Until the single-shot pilot runs there is no
    selected branch, and printing one would be the sin `CONTEXT.md` §10.3 records — moving a
    pre-registered number after the fact.
    """

    branch_a_n: int
    branch_b_n: int
    branch_a: Ceiling
    branch_b: Ceiling
    taken: str

    def lines(self) -> tuple[str, ...]:
        return (
            f"  0/{self.branch_a_n}  (branch A)  {self.branch_a.phrase()}  "
            f"[{self.branch_a.method}]",
            f"  0/{self.branch_b_n}  (branch B)  {self.branch_b.phrase()}  "
            f"[{self.branch_b.method}]",
            f"  BRANCH TAKEN : {self.taken}",
        )


def both_branch_ceilings(
    *,
    branch_a_n: int,
    branch_b_n: int,
    level: float,
    rule_of_three_min_n: int,
    taken: str,
) -> ZeroCeilingBranches:
    """C10 computed both ceilings; C18 **prints both and the one taken** (`PROCESS.md` §12.1)."""
    return ZeroCeilingBranches(
        branch_a_n=branch_a_n,
        branch_b_n=branch_b_n,
        branch_a=ceiling_for(
            0, branch_a_n, level=level, rule_of_three_min_n=rule_of_three_min_n
        ),
        branch_b=ceiling_for(
            0, branch_b_n, level=level, rule_of_three_min_n=rule_of_three_min_n
        ),
        taken=taken,
    )


def median_and_iqr(values: Sequence[int], method: str) -> tuple[Decimal, Decimal, Decimal]:
    """The per-episode **median with IQR** §12.2 reporting rule 2 makes mandatory for money.

    Implemented on sorted integers with explicit **linear** interpolation in
    :class:`~decimal.Decimal` rather than through a third-party array library, because
    `PROCESS.md` §5.1's precision-critical domain includes money and a median of paise is
    money. ``method`` is passed in and **refused** if it is not the one `config/` names — a
    silently different quartile rule is an unreproducible rupee figure, which is exactly
    what naming the method was for.
    """
    if method != LINEAR:
        raise CeilingMissing(
            f"config/ names the quartile method {method!r}; this module implements "
            f"{LINEAR!r}, which is what statistics.quartile_method records and what "
            f"numpy.percentile uses by that name. A median and IQR computed under an unnamed "
            f"method is an unreproducible number"
        )
    if not values:
        raise CeilingMissing(
            "a median over zero episodes is undefined, not zero. S12.2 reporting rule 2 is a "
            "PER-EPISODE median, and with no episodes there is nothing to take one of"
        )
    ordered = sorted(values)
    return (
        _percentile_linear(ordered, Decimal(50)),
        _percentile_linear(ordered, Decimal(25)),
        _percentile_linear(ordered, Decimal(75)),
    )


def _percentile_linear(ordered: Sequence[int], pct: Decimal) -> Decimal:
    """Linear-interpolation percentile over an already sorted sequence, in :class:`Decimal`.

    Exact decimal arithmetic on integer paise — never a float — so the published figure is
    reproducible on any platform. This is the same rule ``numpy.percentile(...,
    method="linear")`` applies, and ``tests/test_c18_results.py`` cross-checks it against
    :func:`whetstone_gate.probe.statistics.median` so the duplication is a **disagreement
    detector** rather than a second opinion nobody compares.
    """
    n = len(ordered)
    if n == 1:
        return Decimal(ordered[0])
    position = (pct / Decimal(100)) * Decimal(n - 1)
    low = int(position)
    high = min(low + 1, n - 1)
    weight = position - Decimal(low)
    return Decimal(ordered[low]) + weight * (Decimal(ordered[high]) - Decimal(ordered[low]))
