"""THE STATISTICS MODULE — every interval this project publishes, computed rather than quoted.

`PROCESS.md` §12.1's C10 done-when: *"the statistics module reproduces `CONTEXT.md` §12.4's
published table **by computation** — ±13.9 pp at n=50 / ±17.9 at n=30 / ±43.8 at n=5, and
6.0% / 10.0% / 45.1% upper bounds for an observed 0/n"*, together with *"Wilson score interval,
McNemar exact, paired bootstrap over seeds (10,000 resamples), rule-of-three at n ≥ 30 and exact
one-sided Clopper–Pearson below it"*.

⚠️ **THE INTERVALS IN THIS FILE ARE NOT THE SAME INTERVAL, AND CONFLATING THEM IS THE EASIEST
WAY TO GET IT WRONG. THERE ARE THREE, AND THEY DO NOT SHARE A ``z``.**

  * The **±pp half-width column** is the textbook **normal-approximation (Wald)** half-width,
    ``z × sqrt(p(1−p)/n)``, quoted *at* a stated ``p`` — §12.4's own column headings are *"95% CI
    half-width **at p≈0.5**"* and *"**at p=0.8**"*. A Wilson interval is **not symmetric**, so it
    has no single half-width and cannot produce that table at all. **TWO-SIDED.**
  * The **published ceiling on a measured non-zero rate** is the **two-sided Wilson score
    interval** — :func:`wilson_interval`, consumed by
    :func:`whetstone_gate.results.figures.ceiling_for`, which publishes *both* its ends.
    **TWO-SIDED, and correctly so:** §12.4.4 attaches an interval to a measurement.
  * The **void threshold** is the Wilson **LOWER BOUND** (§10.3) — :func:`wilson_lower_bound`.
    ⚠️ **ONE-SIDED, z ≈ 1.645, BY ARCHITECT RULING `Q-189`(d), 2026-09-04.** A 95% *lower* bound
    is a one-sided bound; taking the lower end of a two-sided 95% interval yields a **97.5%**
    bound, which sets a **lower** threshold and makes a scored run **less likely to VOID** —
    the self-serving direction. See :func:`one_sided_z`.

⚠️ **WHY :func:`wilson_interval` AND :func:`wilson_lower_bound` DO NOT SHARE THEIR ``z``, WHICH IS
THE WHOLE POINT OF THIS FILE'S SHAPE.** Until 2026-09-04 they did: ``wilson_lower_bound`` was
``wilson_interval(...).lower``, so **one ``z`` fed two different published numbers**. Implementing
`Q-189`(d) by changing :func:`wilson_interval`'s ``z`` — or by changing
``statistics.confidence_level`` in ``config/`` — would have satisfied the ruling **and silently
moved §12.4's published ceiling**, which `PROCESS.md` §12's C10 done-when pins *by computation*.
The algebra is shared through :func:`_wilson_bounds`; **the quantile is not**. `Q-189`(d) residual 2
records the coupling; `INCIDENTS.md` **INC-155** records that no test would have caught the move.

All three are implemented separately, and :func:`published_table` regenerates §12.4's grid from
``config/``'s confidence level so that the six published half-widths and the three published
ceilings are **checked, not transcribed**.

⚠️ **WHY THE UPPER-BOUND COLUMN CHANGES METHOD AT n = 30.** §12.4: *"the rule of three (3/n) at
n ≥ 30 and the exact one-sided Clopper–Pearson bound below it — they diverge sharply at small n,
which is why the ladder uses the exact form."* Measured here: at n=5 the rule of three would say
60.0% and the exact bound says **45.1%**; at n=30 they are 10.0% against 9.50%. The switch point
is ``statistics.rule_of_three_min_n`` in ``config/``, not a number in this file.

**On floats.** `PROCESS.md` §5.1's precision-critical domain is money, the harm vector, the
ledger, seeds, timestamps, token accounting and the gate verdicts — **statistics is not in it**,
and a Wilson bound has no exact rational form. So this module computes in ``float`` and renders
through :class:`~decimal.Decimal` with an explicit ``ROUND_HALF_UP``. What is **not** here is any
money and any decision: the confounded floor and the void comparison are exact integer and
rational arithmetic in :mod:`~whetstone_gate.probe.reach` and :mod:`~whetstone_gate.probe.void`.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from statistics import NormalDist  # the STANDARD LIBRARY module, not this one
from typing import Sequence

import numpy as np

from .. import config as _config

#: `CONTEXT.md` §12.4's table is published to one decimal place in percentage points.
_PP = Decimal("0.1")
_PCT = Decimal("0.1")


def _round(value: float, quantum: Decimal) -> Decimal:
    """Render a computed float for publication. ROUND_HALF_UP, never banker's rounding."""
    return Decimal(repr(value)).quantize(quantum, rounding=ROUND_HALF_UP)


# --------------------------------------------------------------------------------------
# The confidence level, and the z it implies. Neither is written down in this file.
# --------------------------------------------------------------------------------------


def confidence_level() -> float:
    """``statistics.confidence_level`` from ``config/``. Hard rule 9: no default."""
    return float(_config.load("protocol").require("statistics.confidence_level"))


def two_sided_z(level: float | None = None) -> float:
    """The two-sided normal quantile for ``level``.

    ⚠️ **DERIVED, NOT WRITTEN DOWN.** ``1.96`` is the single most-hardcoded constant in applied
    statistics and it is a *rounding* of 1.9599639845400545. It is computed here from the
    configured confidence level through the standard library's own inverse normal CDF, so
    changing ``statistics.confidence_level`` in ``config/`` moves every interval this project
    publishes, which is what hard rule 9 is for.
    """
    if level is None:
        level = confidence_level()
    return NormalDist().inv_cdf(1.0 - (1.0 - level) / 2.0)


def one_sided_z(level: float | None = None) -> float:
    """The **one-sided** normal quantile for ``level``. ⚠️ **`Q-189`(d), 2026-09-04.**

    ⚠️ **THIS IS NOT :func:`two_sided_z` AND THE DIFFERENCE IS THE RULING.** At the configured
    95%, this is ``Φ⁻¹(0.95) ≈ 1.6449`` where :func:`two_sided_z` is ``Φ⁻¹(0.975) ≈ 1.9600``.
    The ruling, verbatim: *"ONE-SIDED, z = 1.645. The implementation uses two-sided z = 1.959964,
    whose lower end is really a 97.5% bound — ⚠️ WHICH SETS A LOWER THRESHOLD AND MAKES A SCORED
    RUN LESS LIKELY TO VOID. That is the self-serving direction. A 95% LOWER bound is one-sided."*

    ⚠️ **IT COSTS US AND CAN ONLY EVER COST US, WHICH IS WHY IT IS SAFE TO RULE AFTER A FREEZE.**
    The one-sided bound is **higher at every observed rate** (measured across 9/30 … 30/30), and
    `HOLES.md` §3.5 makes *below* the calibrated threshold the VOID condition — so a higher
    threshold makes voiding **our own run** more likely. It is the self-critical direction.

    ⚠️ **DERIVED, NEVER WRITTEN DOWN — hard rule 9.** ``1.645`` is as hardcoded in practice as
    ``1.96`` and is a rounding of 1.6448536269514715. It comes from the **same**
    ``statistics.confidence_level`` in ``config/`` that :func:`two_sided_z` reads, through the
    standard library's own inverse normal CDF. There is **one** configured level; what differs
    between the two functions is the tail, which is a property of the *question*, not a constant.

    ⚠️ **AND NO FROZEN ARTEFACT CONTRADICTS IT — CHECKED, NOT ASSUMED.** The ruling withdraws
    itself if any frozen artefact states a sidedness *in terms*. Six frozen statements name this
    bound — `PROTOCOL.md`:630 and :649, `HOLES.md`:284, `PROVENANCE.md`:324 and :719, and
    ``config/protocol.yaml``:349 — and **not one states a sidedness or a z**. Five of the six say
    *"95% Wilson **lower bound**"*; only `HOLES.md` says *"the lower bound of the 95% Wilson
    **interval**"*. `PROTOCOL.md`'s two sidedness words are about **different tests** — McNemar
    (two-sided) and Clopper–Pearson (one-sided). Rule 4 was applied and did not fire.
    """
    if level is None:
        level = confidence_level()
    return NormalDist().inv_cdf(level)


# --------------------------------------------------------------------------------------
# 1. The Wald half-width — §12.4's ±pp column, and ONLY that column.
# --------------------------------------------------------------------------------------


def wald_half_width(n: int, p: float, level: float | None = None) -> float:
    """``z × sqrt(p(1−p)/n)`` as a proportion. §12.4's *"95% CI half-width at p"* column."""
    if n <= 0:
        raise ValueError(f"a half-width over {n} observations is undefined, not zero.")
    return two_sided_z(level) * math.sqrt(p * (1.0 - p) / n)


def wald_half_width_pp(n: int, p: float, level: float | None = None) -> Decimal:
    """The same, in **percentage points**, rounded as §12.4 publishes it."""
    return _round(wald_half_width(n, p, level) * 100.0, _PP)


# --------------------------------------------------------------------------------------
# 2. The Wilson score interval — what §10.3 calibrates the void threshold from.
# --------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Interval:
    """A two-sided interval on a proportion. ⚠️ **Asymmetric in general.**"""

    lower: float
    upper: float
    point: float

    @property
    def is_symmetric_about_point(self) -> bool:
        """True only within floating tolerance. A Wilson interval usually is **not**."""
        return math.isclose(self.point - self.lower, self.upper - self.point, abs_tol=1e-12)


def _refuse_unless_a_proportion(successes: int, n: int) -> None:
    """The two refusals every Wilson computation owes, **held here so neither can lose them**.

    ⚠️ **EXTRACTED ON PURPOSE, AND THIS IS THE FAILURE MODE IT EXISTS TO PREVENT.**
    :func:`wilson_lower_bound` used to inherit these by *delegating* to :func:`wilson_interval`.
    Splitting the ``z`` broke that delegation, and the obvious rewrite — inlining the algebra into
    :func:`wilson_lower_bound` — would have **silently dropped both refusals** from the one
    function whose output is frozen into ``config/``. A refusal lost in a refactor is invisible
    until the input that needed it arrives, which for ``n = 0`` is exactly hard rule 11's
    *"an empty population must not read as a result"*.
    """
    if n <= 0:
        raise ValueError(f"a Wilson interval over {n} observations is undefined.")
    if not 0 <= successes <= n:
        raise ValueError(f"{successes} successes out of {n} is not a proportion.")


def _wilson_bounds(successes: int, n: int, z: float) -> tuple[float, float, float]:
    """The Wilson score algebra, **parameterised by ``z``**, returned as ``(lower, upper, p)``.

    ⚠️ **THE ALGEBRA IS SHARED; THE QUANTILE IS NOT.** This is the whole shape of `Q-189`(d)'s
    correct implementation. Writing the algebra twice would invite the two copies to drift;
    sharing the ``z`` is what produced the defect the ruling's residual 2 names. So exactly one
    thing is shared, exactly one thing is not, and each caller states its own tail.

    Not a public name: nothing outside this module should be choosing a ``z`` for itself.
    """
    p = successes / n
    denominator = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    half = (z / denominator) * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half), p)


def wilson_interval(successes: int, n: int, level: float | None = None) -> Interval:
    """The **two-sided Wilson score interval** on ``successes/n``.

    ⚠️ **TWO-SIDED, AND IT MUST STAY TWO-SIDED.** Its consumer is
    :func:`whetstone_gate.results.figures.ceiling_for`, which publishes **both** ends as §12.4.4's
    ceiling on a measured non-zero rate. `Q-189`(d) is about the **void threshold**, which is
    :func:`wilson_lower_bound` — a different function, a different tail, and since 2026-09-04 a
    different ``z``. **Changing the quantile here moves a published number**, and
    ``tests/test_c10_probe.py`` pins these values precisely so that it cannot happen quietly.

    Wilson rather than Wald because the calibration observes a rate that may sit near 0 or 1,
    where the Wald interval famously runs outside ``[0, 1]`` and undercovers badly.
    """
    _refuse_unless_a_proportion(successes, n)
    lower, upper, p = _wilson_bounds(successes, n, two_sided_z(level))
    return Interval(lower=lower, upper=upper, point=p)


def wilson_lower_bound(successes: int, n: int, level: float | None = None) -> float:
    """§10.3's input to the frozen void threshold. ⚠️ **ONE-SIDED — `Q-189`(d), 2026-09-04.**

    ⚠️ **NOT** ``wilson_interval(...).lower``, which is what it was until this ruling landed and
    which is a **97.5%** bound wearing a 95% label. See :func:`one_sided_z` for the ruling
    verbatim, the direction-of-harm argument, and the frozen-artefact check that had to pass
    before it could be implemented.

    The step after this one is :func:`round_down_to_5pp`; they are kept separate so C14 can print
    the observed rate, the bound and the rounded threshold as three distinct numbers.
    """
    _refuse_unless_a_proportion(successes, n)
    lower, _upper, _point = _wilson_bounds(successes, n, one_sided_z(level))
    return lower


def round_down_to_5pp(proportion: float) -> Fraction:
    """§10.3's *"rounded DOWN to the nearest 5 pp"*, returned as an **exact** rational.

    ⚠️ **DOWN, NEVER TO-NEAREST, AND THE DIRECTION IS THE SAFEGUARD.** Rounding down can only
    make the threshold *easier* to clear, so the rule cannot manufacture a VOID; it can only
    fail to catch a marginal degradation, which §3.6 already admits is the rule's limit.

    Returned exact because it becomes a **frozen** value: C14 writes it into ``PROTOCOL.md``,
    ``HOLES.md`` and ``config/``, and every later comparison is
    :func:`whetstone_gate.probe.void.is_void`, which compares rationals.
    """
    if not 0.0 <= proportion <= 1.0:
        raise ValueError(f"{proportion!r} is not a proportion.")
    twentieths = math.floor(proportion * 20.0 + 1e-12)
    return Fraction(int(twentieths), 20)


# --------------------------------------------------------------------------------------
# 3. The ceiling on an observed zero. ⚠️ "Blocked 100%" NEVER ships without it (§12.4.4).
# --------------------------------------------------------------------------------------


def rule_of_three_upper(n: int) -> float:
    """``3/n`` — the standard large-sample ceiling for an observed 0/n."""
    if n <= 0:
        raise ValueError(f"a ceiling over {n} observations is undefined.")
    return 3.0 / n


def clopper_pearson_zero_upper(n: int, level: float | None = None) -> float:
    """The **exact** one-sided Clopper–Pearson upper bound for 0 successes: ``1 − α^(1/n)``.

    For zero successes the exact binomial bound collapses to a closed form, so no incomplete
    beta function is needed: ``P(X = 0) = (1 − p)^n = α`` solves to ``p = 1 − α^(1/n)``.
    """
    if n <= 0:
        raise ValueError(f"a ceiling over {n} observations is undefined.")
    if level is None:
        level = confidence_level()
    alpha = 1.0 - level
    return 1.0 - alpha ** (1.0 / n)


def upper_bound_for_zero(n: int, level: float | None = None) -> float:
    """§12.4's ceiling column: rule of three at ``n ≥ rule_of_three_min_n``, exact below it."""
    minimum = int(_config.load("protocol").require("statistics.rule_of_three_min_n"))
    return rule_of_three_upper(n) if n >= minimum else clopper_pearson_zero_upper(n, level)


def zero_of_n_phrase(n: int, level: float | None = None) -> str:
    """§12.4.4's mandatory rendering: *"0/N — 95% upper bound 6.0% at N=50"*.

    ⚠️ **THIS IS THE SENTENCE THAT MAY NOT BE OMITTED.** §12.4: *"'Blocked 100%' never ships
    without its ceiling."* Arm 4's expected result is a column of zeros, and a zero without its
    ceiling is the exact claim this project exists to criticise in other people's numbers.
    """
    if level is None:
        level = confidence_level()
    pct = _round(upper_bound_for_zero(n, level) * 100.0, _PCT)
    return f"0/{n} - {_round(level * 100.0, _PCT)}% upper bound {pct}%"


# --------------------------------------------------------------------------------------
# 4. McNemar's exact test — the PAIRED design §12.4.3 says the old formulas got wrong.
# --------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class McNemarResult:
    """Discordant counts and an **exact rational** p-value."""

    b: int
    c: int
    p_value: Fraction

    @property
    def discordant(self) -> int:
        return self.b + self.c

    @property
    def p_value_float(self) -> float:
        """For printing only. Every comparison against alpha uses :attr:`p_value`, exact."""
        return float(self.p_value)


def mcnemar_exact(b: int, c: int) -> McNemarResult:
    """Two-sided **exact** McNemar (a binomial sign test on the discordant pairs).

    ``b`` and ``c`` are the two discordant cells: pairs where arm A escaped and arm B did not,
    and the reverse. Concordant pairs carry no information about a difference and are **not**
    in the denominator — that is what makes this a paired test.

    ⚠️ **EXACT, AND EXACTLY RATIONAL.** ``p = min(1, 2 × P(X ≤ min(b,c)))`` for
    ``X ~ Binomial(b+c, ½)``, computed with :func:`math.comb` over integers and returned as a
    :class:`~fractions.Fraction`. §12.4 requires the *exact* test rather than the chi-square
    approximation because *"real cell sizes are far below N"* and the approximation is unusable
    when the discordant count is small — which, on a strong gate, it will be.

    With no discordant pairs at all the p-value is exactly 1: **the design saw no evidence
    either way**, which is not the same as "the arms are the same" and is not rounded to 0.
    """
    if b < 0 or c < 0:
        raise ValueError(f"discordant counts cannot be negative: b={b}, c={c}.")
    n = b + c
    if n == 0:
        return McNemarResult(b=b, c=c, p_value=Fraction(1))
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1))
    p = Fraction(2 * tail, 2**n)
    return McNemarResult(b=b, c=c, p_value=min(p, Fraction(1)))


def mcnemar_from_pairs(left: Sequence[bool], right: Sequence[bool]) -> McNemarResult:
    """McNemar over two equal-length, **seed-aligned** outcome vectors.

    Refuses unequal lengths rather than zipping to the shorter: §12.4's design is *"paired by
    seed"*, and a silent truncation would drop the tail of one arm from the denominator, which
    is hard rule 11's shrinkage in its purest form.
    """
    if len(left) != len(right):
        raise ValueError(
            f"a PAIRED test needs the same seeds on both sides: {len(left)} vs {len(right)}. "
            f"Zipping to the shorter would drop episodes from the denominator silently "
            f"(hard rule 11)."
        )
    b = sum(1 for x, y in zip(left, right) if x and not y)
    c = sum(1 for x, y in zip(left, right) if y and not x)
    return mcnemar_exact(b, c)


# --------------------------------------------------------------------------------------
# 5. The paired bootstrap over seeds — §12.4.3, for the harm-component medians.
# --------------------------------------------------------------------------------------

#: `PROCESS.md` §5.2's golden 6 and ``config/protocol.yaml``'s ``statistics.quartile_method``.
#: ⚠️ **NAMED because an unnamed method is an unreproducible number** — median and IQR on small
#: samples swing materially between linear interpolation, nearest-rank and Tukey hinges.
QUARTILE_METHOD_KEY = "statistics.quartile_method"


def quartile_method() -> str:
    return str(_config.load("protocol").require(QUARTILE_METHOD_KEY))


def median(values: Sequence[float]) -> float:
    """The median, under ``config/``'s **named** quartile method."""
    return float(np.percentile(np.asarray(values, dtype=float), 50, method=quartile_method()))


def iqr(values: Sequence[float]) -> tuple[float, float]:
    """``(Q1, Q3)`` under the same named method. §5.1: every ₹ figure is a median **with IQR**."""
    array = np.asarray(values, dtype=float)
    method = quartile_method()
    return (
        float(np.percentile(array, 25, method=method)),
        float(np.percentile(array, 75, method=method)),
    )


def paired_bootstrap_median_difference(
    left: Sequence[float],
    right: Sequence[float],
    seed: int,
    resamples: int | None = None,
    level: float | None = None,
) -> Interval:
    """Percentile bootstrap CI for the **median difference**, resampling **seeds**, not episodes.

    ⚠️ **THE PAIRING IS THE WHOLE POINT AND IT LIVES IN THE RESAMPLING, NOT IN THE STATISTIC.**
    §12.4.3: the old formulas *"were independent-proportion, applied to a PAIRED design (arms
    share seeds)"*. One index is drawn and **both** arms are read at that index, so the
    correlation the shared seed induces is preserved. Resampling the two arms independently
    would inflate the interval and quietly re-introduce the very error §12.4 corrected.

    ⚠️ **DETERMINISTIC, BECAUSE HARD RULE 10 SCOPES DETERMINISM TO THE SCORER AND THE REPLAY.**
    ``make eval``'s claim is *"every number regenerates from the stored ledgers"*, so a bootstrap
    seeded from the clock would break it on this module alone. ``seed`` is required — there is
    no default — and :class:`random.Random` is instantiated locally, never the global
    :mod:`random` state, so an unrelated caller cannot perturb a published interval.

    ``resamples`` defaults to ``statistics.bootstrap_resamples`` in ``config/`` (10,000).
    """
    if len(left) != len(right):
        raise ValueError(
            f"a PAIRED bootstrap needs the same seeds on both sides: {len(left)} vs "
            f"{len(right)}."
        )
    n = len(left)
    if n == 0:
        raise ValueError("a bootstrap over zero seeds is undefined, not zero.")
    if resamples is None:
        resamples = int(_config.load("protocol").require("statistics.bootstrap_resamples"))
    if level is None:
        level = confidence_level()

    rng = random.Random(seed)
    method = quartile_method()
    left_array = np.asarray(left, dtype=float)
    right_array = np.asarray(right, dtype=float)

    differences = np.empty(resamples, dtype=float)
    for i in range(resamples):
        picks = [rng.randrange(n) for _ in range(n)]
        differences[i] = float(
            np.percentile(left_array[picks], 50, method=method)
            - np.percentile(right_array[picks], 50, method=method)
        )

    alpha = 1.0 - level
    return Interval(
        lower=float(np.percentile(differences, 100 * alpha / 2, method=method)),
        upper=float(np.percentile(differences, 100 * (1 - alpha / 2), method=method)),
        point=float(
            np.percentile(left_array, 50, method=method)
            - np.percentile(right_array, 50, method=method)
        ),
    )


# --------------------------------------------------------------------------------------
# 6. §12.4's published table, regenerated.
# --------------------------------------------------------------------------------------

#: The rows §12.4 publishes. The **ladder** cell is n=5 and §12.4.2 requires its ±44 pp to be
#: *"printed on the figure, not in a footnote"*.
PUBLISHED_N: tuple[int, ...] = (50, 30, 5)

#: §12.4's two quoted operating points. ``p≈0.5`` is where the escape metric lives; ``p=0.8``
#: is the column the previous draft computed its ±4.5 pp at, which is the error §12.4 opens by
#: naming.
PUBLISHED_P: tuple[float, ...] = (0.5, 0.8)


@dataclass(frozen=True, slots=True)
class PublishedRow:
    n: int
    half_width_at_half: Decimal
    half_width_at_point_eight: Decimal
    upper_bound_for_zero: Decimal
    ceiling_method: str


def published_table(level: float | None = None) -> tuple[PublishedRow, ...]:
    """Regenerate `CONTEXT.md` §12.4's grid **by computation**, as C10's done-when requires."""
    if level is None:
        level = confidence_level()
    minimum = int(_config.load("protocol").require("statistics.rule_of_three_min_n"))
    rows = []
    for n in PUBLISHED_N:
        rows.append(
            PublishedRow(
                n=n,
                half_width_at_half=wald_half_width_pp(n, 0.5, level),
                half_width_at_point_eight=wald_half_width_pp(n, 0.8, level),
                upper_bound_for_zero=_round(upper_bound_for_zero(n, level) * 100.0, _PCT),
                ceiling_method="rule of three (3/n)" if n >= minimum else "exact one-sided",
            )
        )
    return tuple(rows)
