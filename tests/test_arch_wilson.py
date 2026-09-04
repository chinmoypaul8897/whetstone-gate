"""⚠️ `Q-189`(d) — THE VOID THRESHOLD'S WILSON BOUND IS ONE-SIDED, AND §12.4's CEILING IS NOT.

**The ruling** (`QUESTIONS.md`, architect, 2026-09-04, recorded verbatim before implementation):

    "ONE-SIDED, z = 1.645. The implementation uses two-sided z = 1.959964, whose lower end is
    really a 97.5% bound — WHICH SETS A LOWER THRESHOLD AND MAKES A SCORED RUN LESS LIKELY TO
    VOID. That is the self-serving direction. A 95% LOWER bound is one-sided. VERIFY AGAINST
    CONTEXT.md S10.3 RULE 2 AND HOLES.md BEFORE IMPLEMENTING: if either FROZEN artefact
    specifies two-sided in terms, THE FROZEN ARTEFACT WINS, this ruling is withdrawn, and you
    STOP and say so."

⚠️ **WHY THIS FILE IS NOT JUST "TESTS FOR A ONE-LINE CHANGE".** `Q-189`(d)'s residual 2 measured
that **one ``z`` fed two different published numbers**:

    probe/statistics.py:143   wilson_lower_bound  ->  wilson_interval(...).lower
    probe/statistics.py:135   wilson_interval     ->  z = two_sided_z(level)
    results/figures.py:142    wilson_interval     ->  §12.4's PUBLISHED CEILING

So both obvious implementations were wrong. Changing ``statistics.confidence_level`` in
``config/`` yields z = 1.645 **and moves §12.4's published table** *and* edits a pre-registration
artefact. Changing :func:`wilson_interval`'s ``z`` satisfies the ruling **and moves §12.4's
published ceiling**, which `PROCESS.md` §12's C10 done-when pins *by computation*.

⚠️ **AND NOTHING WOULD HAVE GONE RED.** Before this file, the only test over that ceiling was
``tests/test_c18_results.py::test_a_nonzero_figure_gets_a_TWO_SIDED_Wilson_interval``, which
asserts *"Wilson" in ceiling.method* and *lower < upper* — **both of which survive a change of
``z``**. A one-sided ``wilson_interval`` would have moved every published non-zero ceiling in
`RESULTS.md` with a **green suite**. `INCIDENTS.md` **INC-155**.
:func:`test_S12_4s_PUBLISHED_CEILING_is_PINNED_to_its_exact_values` is that missing guard, and it
is the reason this file exists at all.

**How the expected values here were obtained — hard rule 3, and it matters.**
*"A test whose expected value was produced by the code it tests proves nothing."* Every number
below was derived on a **second, independent arithmetic path**: the normal quantile by **bisection
on** :func:`math.erf` (not :class:`statistics.NormalDist`, which is what the subject uses), and the
Wilson algebra written out longhand from ``(p + z^2/2n)/(1 + z^2/n) +/- (z/(1 + z^2/n))*sqrt(...)``.
The two routes agree to the last bit on ``z`` — 1.6448536269514715 — which is itself the check that
neither is wrong.
"""

from __future__ import annotations

import ast
import math
import re
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from pathlib import Path

import pytest

from whetstone_gate.probe import statistics as stats_module
from whetstone_gate.results import figures as figures_module

REPO_ROOT = Path(__file__).resolve().parents[1]
STATISTICS_PY = REPO_ROOT / "src" / "whetstone_gate" / "probe" / "statistics.py"

#: The frozen set, verbatim from `CLAUDE.md` §4's *"Never edit a frozen artefact"* list.
FROZEN_DOCS = (
    "INVARIANTS.md",
    "PROTOCOL.md",
    "HOLES.md",
    "PROVENANCE.md",
    "RAZORPAY_SEMANTICS.md",
)

#: ⚠️ **`CONTEXT.md` IS SCANNED TOO, AND IT IS NOT IN THE FROZEN SET.** `Q-189`(d)'s withdrawal
#: condition names it **first**: *"VERIFY AGAINST CONTEXT.md S10.3 RULE 2 AND HOLES.md BEFORE
#: IMPLEMENTING."* Scanning only `CLAUDE.md` §4's frozen list checks a set the ruling did not ask
#: about — which is exactly what one earlier pass did.
RULING_NAMED_DOCS = FROZEN_DOCS + ("CONTEXT.md", "config/protocol.yaml", "config/lanes.yaml")

#: ⚠️ **THE ONLY SIDEDNESS STATEMENTS IN SCOPE THAT ARE NOT ABOUT THE WILSON BOUND.** Each names a
#: *different estimator*, listed individually rather than matched by a loose pattern, so that a
#: **new** sidedness claim cannot hide behind one of them. Growing this tuple is a visible act and
#: the guard below pins its length.
#:
#:   * ``mcnemar``      — §12.4's pre-registered headline test, *"McNemar exact, two-sided"*.
#:   * ``clopper`` / ``pearson`` — the **upper** ceiling on an observed 0/n, *"exact one-sided"*.
#:   * ``0.05^(1/5)``   — `CONTEXT.md` §12.4's ladder row states that same Clopper–Pearson bound
#:     as *"45.1% (exact one-sided, 1 − 0.05^(1/5))"* **without naming Clopper**, so the name-based
#:     exemptions above do not reach it and it needs its own.
OTHER_ESTIMATORS = ("mcnemar", "clopper", "pearson", "0.05^(1/5)")


# ======================================================================================
# The SECOND implementation. Nothing below imports a quantile or an interval from the subject.
# ======================================================================================


def _phi(z: float) -> float:
    """The standard normal CDF, from :func:`math.erf`. **Not** :class:`statistics.NormalDist`."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _inv_phi(p: float) -> float:
    """The inverse normal CDF by bisection on :func:`_phi` — a different algorithm from the
    subject's ``NormalDist().inv_cdf``, so agreement between them is evidence rather than
    tautology."""
    low, high = -6.0, 6.0
    for _ in range(300):
        middle = (low + high) / 2.0
        if _phi(middle) < p:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def _wilson_by_hand(successes: int, n: int, z: float) -> tuple[float, float]:
    """The Wilson score algebra, written out longhand as a second implementation."""
    p = successes / n
    denominator = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    half = (z / denominator) * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def _pct(value: float) -> Decimal:
    """§12.4 publishes to one decimal place, ROUND_HALF_UP — never banker's."""
    return Decimal(repr(value * 100.0)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


#: The two quantiles at the configured 95%, from the independent route above.
Z_ONE_SIDED_BY_HAND = _inv_phi(0.95)
Z_TWO_SIDED_BY_HAND = _inv_phi(0.975)


# ======================================================================================
# 1. RULE 4 FIRST. The ruling withdraws itself if a FROZEN artefact states a sidedness.
# ======================================================================================


def test_NO_FROZEN_ARTEFACT_STATES_A_SIDEDNESS_so_Q189d_was_never_withdrawn():
    """⚠️ **THE WITHDRAWAL CONDITION, RE-RUN AS A TEST RATHER THAN AS A ONE-OFF GREP.**

    `CLAUDE.md` rule 4: *"If a frozen artefact and `CONTEXT.md` disagree -> the frozen artefact
    wins."* A frozen artefact outranks an architect ruling too. `Q-189`(d) says so itself: *"if
    either FROZEN artefact specifies two-sided in terms, THE FROZEN ARTEFACT WINS, this ruling is
    withdrawn, and you STOP."*

    ⚠️ **THIS IS A STANDING GUARD, NOT A RECORD OF A PAST CHECK.** Two sessions have now run that
    grep by hand and reported *"no hit"*. A hand-run grep protects the day it was run. If a later
    session ever writes a sidedness into a frozen artefact, the ruling is withdrawn **and this
    file's implementation becomes illegal** — and nothing but this test would say so.

    ⚠️ **AND THE SCAN INCLUDES `CONTEXT.md`, WHICH IS NOT FROZEN, BECAUSE THE RULING NAMES IT
    FIRST.** *"VERIFY AGAINST CONTEXT.md S10.3 RULE 2 AND HOLES.md."* An earlier pass checked
    `CLAUDE.md` §4's frozen list only, then defended the ruling by counting phrasings across it —
    *"five of the six say 'lower bound', only one says 'interval'"*. ⚠️ **That count is true and
    it is not the argument.** On the **two** artefacts the ruling actually named — `CONTEXT.md`
    §10.3 rule 2 and `HOLES.md` §3.5 rule 2 — the wording is *"the lower bound of the 95% Wilson
    **interval**"*, **both of them**, the same sentence twice. The ruling survives on its own
    stated test, *"specifies two-sided **in terms**"*, which neither does: neither states a
    sidedness and neither states a ``z``. It does **not** survive on a head-count of phrasings,
    and recording it that way would be a stronger claim than the evidence carries. `Q-189`(d)
    RESIDUAL 1 already says the honest version: *"the architect chose, and chose the stricter of
    the two available readings."*

    Sidedness statements about **other estimators** are exempted by :data:`OTHER_ESTIMATORS`,
    individually and by name, so a *new* claim cannot hide behind one of them.
    """
    sidedness = re.compile(r"one[- ]sided|two[- ]sided|1\.645|1\.6449|1\.959|1\.96\b", re.I)
    assert len(OTHER_ESTIMATORS) == 4, (
        "OTHER_ESTIMATORS has changed size. Every entry exempts a line from the sidedness "
        "scan, so growing it is how this guard gets switched off one quiet edit at a time. "
        "A new entry needs an architect ruling and a comment naming which estimator it is"
    )

    offending: list[str] = []
    wilson_mentions: list[str] = []
    scanned = 0
    for name in RULING_NAMED_DOCS:
        path = REPO_ROOT / name
        assert path.is_file(), f"{name} is named by CLAUDE.md §4 or Q-189(d) and is missing"
        scanned += 1
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            lowered = line.lower()
            if "wilson" in lowered:
                wilson_mentions.append(f"{name}:{number}")
            if sidedness.search(line) and not any(k in lowered for k in OTHER_ESTIMATORS):
                offending.append(f"{name}:{number}: {line.strip()}")

    assert scanned == 8, (
        "the scan is CLAUDE.md §4's five frozen documents, plus config/'s two files, plus "
        f"CONTEXT.md which Q-189(d) names FIRST — eight in all, got {scanned}"
    )
    assert len(wilson_mentions) >= 5, (
        "the frozen set used to carry at least five statements of the Wilson void-threshold "
        f"rule and now carries {len(wilson_mentions)}: {wilson_mentions}. A frozen artefact was "
        "edited, which CLAUDE.md §4 forbids outright"
    )
    assert offending == [], (
        "⚠️ A FROZEN ARTEFACT NOW STATES A SIDEDNESS OR A z. Under hard rule 4 the frozen "
        "artefact WINS, Q-189(d) is WITHDRAWN BY ITS OWN TERMS, and probe/statistics.py's "
        "one_sided_z must be reverted rather than defended:\n  " + "\n  ".join(offending)
    )


# ======================================================================================
# 2. THE RULING, IMPLEMENTED. One-sided, and derived rather than typed.
# ======================================================================================


def test_Q189d_the_void_threshold_bound_is_ONE_SIDED_z_1_645():
    """⚠️ **THE RULING ITSELF.** ``wilson_lower_bound`` uses the one-sided quantile.

    Hand-computed on the independent route: at 95% the one-sided quantile is
    **1.6448536269514715**, the two-sided is **1.9599639845400545**, and the ruling's *"z = 1.645"*
    is a rounding of the first.
    """
    assert Z_ONE_SIDED_BY_HAND == pytest.approx(1.6448536269514715, abs=1e-15)
    assert stats_module.one_sided_z() == pytest.approx(Z_ONE_SIDED_BY_HAND, abs=1e-12)
    assert round(stats_module.one_sided_z(), 3) == 1.645, "the ruling's own stated value"

    # ⚠️ THE BOUND ITSELF, at three rates, each written out longhand above and NOT read off
    # the subject. The old two-sided values are stated beside them so the flip is visible.
    for successes, n, one_sided, two_sided in (
        (3, 30, 0.040676967009230874, 0.03459988874733416),
        (15, 30, 0.3561908311988599, 0.3315412564053376),
        (24, 30, 0.657489091321207, 0.6269430358685175),
    ):
        by_hand, _upper = _wilson_by_hand(successes, n, Z_ONE_SIDED_BY_HAND)
        assert by_hand == pytest.approx(one_sided, abs=1e-12)
        assert stats_module.wilson_lower_bound(successes, n) == pytest.approx(by_hand, abs=1e-12)
        # ⚠️ AND IT IS NOT THE OLD NUMBER. Without this line the test could pass on the old code
        # at any tolerance loose enough to swallow the difference (hard rule 6's "provably
        # meaningful" flip).
        assert abs(stats_module.wilson_lower_bound(successes, n) - two_sided) > 1e-9, (
            f"{successes}/{n} still reports the TWO-SIDED bound; Q-189(d) is not implemented"
        )


def test_the_one_sided_z_is_DERIVED_from_config_and_is_NOT_A_LITERAL_in_the_source():
    """⚠️ **HARD RULE 9 APPLIED TO THE NEW CONSTANT.** *"Every spec-specified value lives in
    ``config/`` ... no default for a required value."*

    ``1.645`` is as reflexively hardcoded as ``1.96``. It is **derived** from the same
    ``statistics.confidence_level`` that :func:`two_sided_z` reads — there is **one** configured
    level and two tails — so moving the level in ``config/`` moves both, and neither is typed.

    The assertion is made **on the AST**, over executable code only: the ruling's *"z = 1.645"* is
    quoted in the subject's docstrings on purpose, and a text grep would fire on the quotation.
    """
    level = stats_module.confidence_level()
    assert level == 0.95, "config/protocol.yaml's statistics.confidence_level"
    # Derived: change the level and the quantile moves with it, with no edit to the source.
    assert stats_module.one_sided_z(0.90) == pytest.approx(_inv_phi(0.90), abs=1e-12)
    assert stats_module.one_sided_z(0.99) == pytest.approx(_inv_phi(0.99), abs=1e-12)
    assert stats_module.one_sided_z() == stats_module.one_sided_z(level)

    tree = ast.parse(STATISTICS_PY.read_text(encoding="utf-8"))
    banned = {1.645, 1.6449, 1.96, 1.959964, 1.9599639845400545, 0.95, 0.975}
    found = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, float)
        and node.value in banned
    ]
    assert found == [], (
        f"probe/statistics.py now types a quantile or a confidence level as a literal: {found}. "
        "Hard rule 9: it comes from config/ through one loader, or it does not exist"
    )


# ======================================================================================
# 3. ⚠️ THE GUARD THIS WHOLE FINDING EXISTS TO INSTALL. §12.4's PUBLISHED CEILING.
# ======================================================================================


def test_S12_4s_PUBLISHED_CEILING_is_PINNED_to_its_exact_values():
    """⚠️⚠️ **THE GUARD. IF A LATER CHANGE MOVES §12.4's PUBLISHED CEILING, THIS GOES RED.**

    ``results/figures.py:142`` attaches a **two-sided** Wilson interval to every published
    non-zero rate — §12.4.4's *"'Blocked 100%' never ships without its ceiling"* applied to the
    rates that are not zero. That interval is a **published number**: it is what `RESULTS.md`
    prints beside every escape count.

    ⚠️ **BEFORE THIS TEST, NOTHING PINNED IT.**
    ``test_a_nonzero_figure_gets_a_TWO_SIDED_Wilson_interval`` asserts only *"Wilson" in method*
    and *lower < upper*, and **both survive a change of ``z``** — so the naive implementation of
    `Q-189`(d) would have moved every one of these numbers with a green suite. That is the defect
    this file was written for.

    Every value below is hand-derived from :func:`_wilson_by_hand` at the two-sided quantile from
    :func:`_inv_phi`, then rendered by §12.4's own ROUND_HALF_UP — never read off ``figures.py``.
    """
    level = stats_module.confidence_level()
    minimum = 30

    # ⚠️ n = 30 and n = 50 are the TWO LIVE N BRANCHES (§13.4); the pilot selects between them
    # and `both_branch_ceilings` publishes both, so both are pinned. n = 5 is the ladder cell.
    # 19/30, 21/30 and 24/30 are CALIBRATION-SHAPED rates — the region §10.3's rule actually
    # operates in — because a guard that only covers the tails is not a guard over the middle.
    expected = {
        (1, 30): (Decimal("0.6"), Decimal("16.7")),
        (3, 30): (Decimal("3.5"), Decimal("25.6")),
        (15, 30): (Decimal("33.2"), Decimal("66.8")),
        (19, 30): (Decimal("45.5"), Decimal("78.1")),
        (21, 30): (Decimal("52.1"), Decimal("83.3")),
        (24, 30): (Decimal("62.7"), Decimal("90.5")),
        (29, 30): (Decimal("83.3"), Decimal("99.4")),
        (1, 50): (Decimal("0.4"), Decimal("10.5")),
        (25, 50): (Decimal("36.6"), Decimal("63.4")),
        (3, 5): (Decimal("23.1"), Decimal("88.2")),
    }
    for (successes, n), (lower_pct, upper_pct) in expected.items():
        low, high = _wilson_by_hand(successes, n, Z_TWO_SIDED_BY_HAND)
        assert (_pct(low), _pct(high)) == (
            lower_pct,
            upper_pct,
        ), f"the hand-derivation itself disagrees at {successes}/{n}"
        ceiling = figures_module.ceiling_for(
            successes, n, level=level, rule_of_three_min_n=minimum
        )
        assert ceiling.method == figures_module.WILSON_SCORE
        assert (ceiling.lower_pct, ceiling.upper_pct) == (lower_pct, upper_pct), (
            f"⚠️ §12.4's PUBLISHED CEILING MOVED at {successes}/{n}: expected "
            f"{lower_pct}%-{upper_pct}%, got {ceiling.lower_pct}%-{ceiling.upper_pct}%. "
            "This is the two-sided Wilson interval that results/figures.py publishes beside "
            "every non-zero rate. Q-189(d) made the VOID THRESHOLD one-sided and left this "
            "alone ON PURPOSE; if this assertion is red, a change to wilson_interval's z has "
            "corrupted a published number, which is exactly what this test exists to catch"
        )

        # ⚠️ AND `phrase()`, WHICH IS THE STRING THAT ACTUALLY REACHES `RESULTS.md` — AND WHICH
        # CARRIES THE CONFIDENCE LABEL. This is the assertion that catches the *other* naive
        # implementation of Q-189(d): editing ``statistics.confidence_level`` in ``config/`` to
        # 0.90 makes this read "90.0% CI", and `results/` reads that key on a path
        # (``results/loader.py``) that never passes through
        # :func:`whetstone_gate.probe.statistics.confidence_level` at all. Pinning only the two
        # Decimals would catch the moved bounds but not name the cause.
        assert ceiling.phrase() == f"95.0% CI {lower_pct}%-{upper_pct}%"

    # ⚠️ AND THE RENDERED SENTENCE, because a ceiling nobody prints is not a published number.
    figure = figures_module.figure(
        "arm 1 escape", 3, 30, level=level, rule_of_three_min_n=minimum
    )
    assert figure.render() == "3/30 = 10.0% - 95.0% CI 3.5%-25.6% [Wilson score interval]"


def test_S12_4s_PUBLISHED_TABLE_is_PINNED_and_did_not_move_either():
    """C10's done-when, restated as a guard rather than trusted: *"±13.9 pp at n=50 / ±17.9 at
    n=30 / ±43.8 at n=5, and 6.0% / 10.0% / 45.1% upper bounds for an observed 0/n."*

    ``published_table`` runs on :func:`two_sided_z` (the Wald column) and on
    :func:`clopper_pearson_zero_upper` (the ceiling column). Neither was touched by `Q-189`(d),
    and this asserts it rather than assuming it. ``tests/test_c10_probe.py`` pins the same grid;
    **that duplication is deliberate** — this file's subject is the *split*, and a guard that
    lives only in the file being changed is a guard that moves with the change.
    """
    rows = {row.n: row for row in stats_module.published_table()}
    assert (rows[50].half_width_at_half, rows[50].half_width_at_point_eight) == (
        Decimal("13.9"),
        Decimal("11.1"),
    )
    assert (rows[30].half_width_at_half, rows[30].half_width_at_point_eight) == (
        Decimal("17.9"),
        Decimal("14.3"),
    )
    assert (rows[5].half_width_at_half, rows[5].half_width_at_point_eight) == (
        Decimal("43.8"),
        Decimal("35.1"),
    )
    assert rows[50].upper_bound_for_zero == Decimal("6.0")
    assert rows[30].upper_bound_for_zero == Decimal("10.0")
    assert rows[5].upper_bound_for_zero == Decimal("45.1")
    assert stats_module.zero_of_n_phrase(50) == "0/50 - 95.0% upper bound 6.0%"


def test_wilson_interval_STAYS_TWO_SIDED_and_is_pinned_to_the_hand_derivation():
    """The other half of the split, asserted directly on the interval rather than through
    ``figures.py``, so a regression is attributed to the right module."""
    assert stats_module.two_sided_z() == pytest.approx(Z_TWO_SIDED_BY_HAND, abs=1e-12)
    for successes, n in ((1, 30), (3, 30), (15, 30), (29, 30), (25, 50)):
        low, high = _wilson_by_hand(successes, n, Z_TWO_SIDED_BY_HAND)
        interval = stats_module.wilson_interval(successes, n)
        assert interval.lower == pytest.approx(low, abs=1e-12)
        assert interval.upper == pytest.approx(high, abs=1e-12)
        assert interval.point == successes / n


# ======================================================================================
# 4. THE SPLIT ITSELF — that the two quantities no longer share a z.
# ======================================================================================


def test_the_two_bounds_NO_LONGER_SHARE_A_z_which_is_the_whole_shape_of_the_fix():
    """⚠️ **`Q-189`(d) RESIDUAL 2, ASSERTED.** *"The only implementation that satisfies the ruling
    without moving a second published number is a SEPARATE one-sided quantile used by
    ``wilson_lower_bound`` ALONE."*

    Stated as an inequality rather than as two equalities, because the failure mode is
    **re-coupling**: a later session tidying the module by routing ``wilson_lower_bound`` back
    through ``wilson_interval`` would restore the exact defect, and both values would still be
    *"a Wilson bound"*.
    """
    assert stats_module.one_sided_z() < stats_module.two_sided_z()
    for successes, n in ((3, 30), (15, 30), (24, 30), (25, 50)):
        assert (
            stats_module.wilson_lower_bound(successes, n)
            != stats_module.wilson_interval(successes, n).lower
        ), (
            f"at {successes}/{n} the void threshold's bound equals the published interval's "
            "lower end again — the two have been re-coupled and one z feeds two published "
            "numbers, which is the defect Q-189(d) residual 2 named"
        )


def test_wilson_lower_bound_does_not_ROUTE_THROUGH_the_two_sided_interval():
    """The same guard on the **source**, because the numeric one can be satisfied by accident.

    An AST walk over ``wilson_lower_bound``'s body: it may not name :func:`wilson_interval` or
    :func:`two_sided_z`, and it must name :func:`one_sided_z`. The converse is asserted too — the
    published interval must not have picked up the one-sided quantile.
    """
    tree = ast.parse(STATISTICS_PY.read_text(encoding="utf-8"))
    functions = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "one_sided_z" in functions, "Q-189(d)'s quantile is not defined"

    called = {
        node.func.id
        for node in ast.walk(functions["wilson_lower_bound"])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert (
        "one_sided_z" in called
    ), "wilson_lower_bound does not call one_sided_z, so it is not implementing Q-189(d)"
    assert "two_sided_z" not in called and "wilson_interval" not in called, (
        f"wilson_lower_bound reaches the two-sided path again: {sorted(called)}. That is the "
        "shared z Q-189(d) residual 2 exists about"
    )

    interval_calls = {
        node.func.id
        for node in ast.walk(functions["wilson_interval"])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "two_sided_z" in interval_calls and "one_sided_z" not in interval_calls, (
        f"wilson_interval's quantile changed: {sorted(interval_calls)}. §12.4's published "
        "ceiling is computed from it and must stay two-sided"
    )


# ======================================================================================
# 5. THE REFACTOR'S OWN HAZARDS — the refusal that delegation used to supply.
# ======================================================================================


def test_wilson_lower_bound_KEPT_ITS_REFUSALS_through_the_split():
    """⚠️ **THE FAILURE MODE OF THE FIX, DRIVEN RATHER THAN ASSUMED.**

    ``wilson_lower_bound`` inherited its two refusals by **delegating** to ``wilson_interval``.
    Splitting the ``z`` broke that delegation, and the obvious rewrite — inlining the algebra —
    would have silently dropped both from the one function whose output is frozen into
    ``config/``. A dropped refusal is invisible until the input that needs it arrives, and for
    ``n = 0`` that input is hard rule 11's *"an empty population must not read as a result"*.
    """
    for successes, n in ((0, 0), (1, 0), (0, -5)):
        with pytest.raises(ValueError, match="undefined"):
            stats_module.wilson_lower_bound(successes, n)
    for successes, n in ((5, 3), (-1, 10), (31, 30)):
        with pytest.raises(ValueError, match="not a proportion"):
            stats_module.wilson_lower_bound(successes, n)
    # The published interval keeps them too — same refusals, same messages, one source.
    with pytest.raises(ValueError, match="undefined"):
        stats_module.wilson_interval(0, 0)
    with pytest.raises(ValueError, match="not a proportion"):
        stats_module.wilson_interval(5, 3)


def test_the_one_sided_bound_is_HIGHER_EVERYWHERE_which_is_the_SELF_CRITICAL_direction():
    """⚠️ **WHY A RULING MADE AFTER A FREEZE IS SAFE HERE: IT CAN ONLY EVER COST US.**

    `HOLES.md` §3.5 makes *below* the calibrated threshold the VOID condition, and `HOLES.md`
    itself names the incentive: *"a high observed arm-1 breach rate sets a high threshold, which
    makes a later VOID more likely — so re-running the calibration until it comes out low is
    rational, invisible, and violated no stated rule until this one."*

    The one-sided bound is **higher at every observed rate**, so this change makes voiding **our
    own run** more likely. Asserted over the whole domain rather than at a sample, because *"is it
    higher at every k"* is the property and a spot check is not that property.

    ⚠️ **This is arithmetic about the RULE. It says nothing about any observed rate**, which is
    `TODO_C14_CALIBRATION` and is the architect's to write after the calibration reports.
    """
    n = 30
    for successes in range(n + 1):
        one_sided, _ = _wilson_by_hand(successes, n, Z_ONE_SIDED_BY_HAND)
        two_sided, _ = _wilson_by_hand(successes, n, Z_TWO_SIDED_BY_HAND)
        assert one_sided >= two_sided, f"the one-sided bound is LOWER at {successes}/{n}"
        assert stats_module.wilson_lower_bound(successes, n) == pytest.approx(
            one_sided, abs=1e-12
        )
    # Strictly higher wherever the bound is not pinned at the 0 floor.
    assert stats_module.wilson_lower_bound(1, n) > 0.0
    for successes in range(1, n + 1):
        one_sided, _ = _wilson_by_hand(successes, n, Z_ONE_SIDED_BY_HAND)
        two_sided, _ = _wilson_by_hand(successes, n, Z_TWO_SIDED_BY_HAND)
        assert one_sided > two_sided, f"not STRICTLY higher at {successes}/{n}"


def test_the_void_threshold_RULE_still_rounds_DOWN_and_still_returns_an_exact_rational():
    """The step after the bound is unchanged by `Q-189`(d), asserted so a reader can see the
    ruling reached the quantile and nothing else. ``round_down_to_5pp`` returns a
    :class:`~fractions.Fraction` because the result becomes a **frozen** value in ``config/`` and
    every later comparison is exact."""
    bound = stats_module.wilson_lower_bound(24, 30)
    assert bound == pytest.approx(0.657489091321207, abs=1e-12)
    assert stats_module.round_down_to_5pp(bound) == Fraction(13, 20)
    assert isinstance(stats_module.round_down_to_5pp(bound), Fraction)
    # DOWN, never to-nearest: rounding down can only make the threshold easier to clear.
    assert stats_module.round_down_to_5pp(0.6499999) == Fraction(60, 100)
