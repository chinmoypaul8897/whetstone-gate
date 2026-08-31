"""C2 REVIEW 1 — KEPT PROBES. Session `94116fe2`.

⚠️ **These are the review's tests, not the build's, and they FIX NOTHING.** Every one of
them passes against C2 as written. Each exists because the mutation run of
`docs/reviews/mutants/c2_mutants.md` found a mutation the build's own suite did not kill,
or a figure the specification publishes that no test binds to a computation. A review that
reports a survivor and leaves nothing behind has reported a survivor twice — once now and
once at the next regression.

**What each probe closes, and which mutant it would have killed:**

  * :func:`test_the_world_is_unchanged_under_a_hostile_ambient_decimal_context_on_EVERY_seed`
    — **M12**. `whetstone_gate.world.amounts`'s module docstring claims *"Every context is
    passed explicitly. Not one operation here depends on the ambient `decimal` context, so
    nothing a caller has done to `decimal.getcontext()` … can move a published number."*
    C2's own guard, `test_the_world_does_not_depend_on_the_ambient_decimal_context`, checks
    that on **seed 2001 alone** — whose eleven ordinary amounts are all ≤ 1,648,691, i.e.
    at most seven significant digits. Dropping the explicit context from the final
    `exp()` therefore moves **nothing** on that seed under `Context(prec=8)` and the guard
    stays green, while **14 of the 660 amounts the project actually publishes** move. The
    claim is about the package; the check was about one seed.

  * :func:`test_the_note_assignment_follows_the_pool_size_rather_than_a_written_down_six`
    — **M7**. `_note_template` uses `index % len(spec.note_templates)`, which is right.
    Replacing it with `index % 6` — a bare literal for a `CONTEXT.md` §8.6 row, which hard
    rule 9 forbids — survived the entire suite byte-for-byte. `spec_constants.py`'s own
    `world_note_templates` row admits the gap (*"the realistic hardcoding shape … is not
    matched by the CONTEXTUAL regex anyway"*), so this is the check that was missing rather
    than a surprise.

  * :func:`test_q_023s_published_measurement_re_derives_from_the_frozen_seed_set`
    — no mutant; a **persona 1** finding. `CONTEXT.md` §8.6a publishes four figures for the
    libm margin and `QUESTIONS.md` Q-023 republishes them. C2's
    `test_the_libm_margin_on_the_frozen_seed_set_is_measured_rather_than_assumed` re-derives
    the 660 draws but asserts only *"greater than one ULP"*, so **not one of the four
    published figures is bound to the computation** and all four could go stale silently the
    next time §13.4's N rule moves the seed list — which Q-023's own reasoning names as the
    thing that will happen.

**Every expected value here is parsed or computed, never transcribed.** The figures come
out of `CONTEXT.md`; the seeds come out of `config/`; the margin is recomputed from the
generator. A probe that carried its own copy of the number it checks would be the second
copy this project keeps finding.
"""

from __future__ import annotations

import dataclasses
import decimal
import math
import re
from decimal import Context, Decimal
from pathlib import Path

import pytest

from whetstone_gate import config as cfg
from whetstone_gate.world import amounts
from whetstone_gate.world.generator import generate
from whetstone_gate.world.spec import WorldSpec, load_world_spec


def _exactly_one(matches: list, what: str):
    assert len(matches) == 1, (
        f"expected exactly one {what} in the source document, found {len(matches)}. A "
        f"parser that silently reads nothing is the same class of defect as the check it "
        f"replaces."
    )
    return matches[0]


@pytest.fixture(scope="module")
def protocol() -> cfg.Config:
    return cfg.load("protocol")


@pytest.fixture(scope="module")
def spec(protocol: cfg.Config) -> WorldSpec:
    return load_world_spec(protocol)


@pytest.fixture(scope="module")
def context_md() -> str:
    return (cfg.repo_root() / "CONTEXT.md").read_text(encoding="utf-8")


def _every_seed(protocol: cfg.Config) -> list[int]:
    """Every seed the project generates a world for — scored, ladder and pilot, from `config/`."""
    pairs = [
        ("seeds.scored_n50_first", "seeds.scored_n50_last"),
        ("seeds.ladder_first", "seeds.ladder_last"),
        ("seeds.pilot_first", "seeds.pilot_last"),
    ]
    seeds: set[int] = set()
    for first, last in pairs:
        seeds.update(range(protocol.require(first), protocol.require(last) + 1))
    assert len(seeds) == 60, f"expected 60 distinct seeds, config/ gives {len(seeds)}"
    return sorted(seeds)


def test_the_world_is_unchanged_under_a_hostile_ambient_decimal_context_on_EVERY_seed(
    spec: WorldSpec, protocol: cfg.Config
) -> None:
    """The ambient-context claim, checked over the seeds the claim is about.

    ⚠️ **Why the seed set is the whole point of this probe.** `Context(prec=8)` truncates
    to eight significant digits. An amount below 10,000,000 still carries a fractional
    digit at that precision, so a half-up rounding still lands where it should; an amount
    **at or above** 10,000,000 does not, and `ROUND_FLOOR` then eats the fraction that
    decides the paise integer. Seed 2001's largest ordinary amount is 1,648,691, so seed
    2001 **cannot exhibit the failure**, and a guard that only looks there cannot see it.

    The hostile context is `Context(prec=8, rounding=ROUND_FLOOR)` — the same one C2's own
    guard uses, deliberately, so that the difference between the two tests is the seed set
    and nothing else.
    """
    seeds = _every_seed(protocol)
    reference = {seed: generate(seed, spec) for seed in seeds}

    previous = decimal.getcontext()
    decimal.setcontext(Context(prec=8, rounding=decimal.ROUND_FLOOR))
    try:
        under_hostile = {seed: generate(seed, spec) for seed in seeds}
    finally:
        decimal.setcontext(previous)

    moved = [seed for seed in seeds if under_hostile[seed] != reference[seed]]
    assert not moved, (
        f"the ambient decimal context moved the world on {len(moved)} of {len(seeds)} "
        f"seeds: {moved}. `whetstone_gate.world.amounts` claims every context is passed "
        f"explicitly; one of them is not. This is a finding, not a failure of the test."
    )

    # And the probe would be worthless if seed 2001 could have shown this by itself.
    hardest = max(
        p.amount_paise for p in reference[seeds[0]].payments[: spec.probe_index]
    )
    assert hardest < 10_000_000, (
        "seed 2001's ordinary amounts now reach eight significant digits, so C2's "
        "single-seed guard would catch what this probe was added for. Re-check the finding."
    )


def test_the_note_assignment_follows_the_pool_size_rather_than_a_written_down_six(
    spec: WorldSpec,
) -> None:
    """`index mod <pool size>` — the pool's own length, not a literal (hard rule 9).

    Driven with a **five**-template pool, which `WorldSpec._check_consistent` accepts
    because `note_template_assignment` is moved with it. Index 5 must therefore wrap to
    template 0. An implementation carrying a hardcoded `% 6` reaches past the end of a
    five-entry pool instead, which is how this probe kills mutant **M7**.

    No `config/` file is touched: the spec is a frozen dataclass and
    :func:`dataclasses.replace` builds a second one, which is exactly the seam C2 built for
    `test_every_world_constant_is_actually_read_from_the_spec`.
    """
    smaller = dataclasses.replace(
        spec,
        note_templates=spec.note_templates[:5],
        note_template_assignment="index_mod_5",
    )
    world = generate(2001, smaller)
    ordinary = world.payments[: smaller.probe_index]

    for payment in ordinary:
        key, text = smaller.note_templates[payment.index % 5]
        assert payment.notes == {key: text}, (
            f"payment {payment.index} took its note from a pool of "
            f"{len(spec.note_templates)} while `config/` supplied 5 — the modulus is a "
            f"written-down number rather than the pool's length."
        )

    # The wrap is what a hardcoded `% 6` cannot produce: index 5 -> template 0, not 5.
    assert ordinary[5].notes == {smaller.note_templates[0][0]: smaller.note_templates[0][1]}
    assert ordinary[5].notes != {
        spec.note_templates[5][0]: spec.note_templates[5][1]
    }


def test_q_023s_published_measurement_re_derives_from_the_frozen_seed_set(
    spec: WorldSpec, protocol: cfg.Config, context_md: str
) -> None:
    """§8.6a's four libm-margin figures, bound to the computation that produced them.

    ⚠️ **Why this is persona 1's and not a nicety.** Q-023 exists because §8.6a's previous
    ULP sentence was an overclaim *in a document whose subject is overclaims*. The remedy
    replaced it with four measured figures — and a measured figure with no check is the
    same shape of risk one sentence later. §13.4's N decision rule may change the seed
    list; when it does, this test says so.

    All four are **parsed from `CONTEXT.md`**, never transcribed here.
    """
    published_distance = Decimal(
        _exactly_one(
            re.findall(
                r"closest any amount comes to a `\.5` rounding boundary \| \*\*([\d.]+)\*\* paise",
                context_md,
            ),
            "§8.6a's published closest approach",
        )
    )
    published_seed, published_index, published_raw = _exactly_one(
        re.findall(
            r"\*\*seed (\d+), draw index (\d+)\*\*; raw `(\d+)`", context_md
        ),
        "§8.6a's published location for the closest approach",
    )

    context = Context(prec=spec.decimal_context_precision)
    ln_low = Decimal(spec.amount_min_paise).ln(context=context)
    span = context.subtract(
        Decimal(spec.amount_max_paise).ln(context=context), ln_low
    )
    half = Decimal("0.5")

    closest = None
    float_disagreements = 0
    draws = 0
    lo_f, hi_f = float(spec.amount_min_paise), float(spec.amount_max_paise)

    for seed in _every_seed(protocol):
        world = generate(seed, spec)
        for index, raw in enumerate(world.raw_draws):
            draws += 1
            u = amounts.exact_u(raw, context)
            amount = context.add(ln_low, context.multiply(u, span)).exp(context=context)
            distance = abs((amount - int(amount)) - half)
            if closest is None or distance < closest[0]:
                closest = (distance, seed, index, raw, amount)

            # The fourth published figure: "a float implementation of this same formula …
            # identical integer paise on all 660". Computed with the platform libm the
            # world refuses to use, which is the only way to check the claim at all.
            as_float = math.exp(
                math.log(lo_f) + (raw / 2**32) * (math.log(hi_f) - math.log(lo_f))
            )
            float_paise = int(
                Decimal(repr(as_float)).quantize(
                    Decimal(1), rounding=amounts.rounding_mode(spec.rounding)
                )
            )
            if float_paise != world.payments[index].amount_paise:
                float_disagreements += 1

    assert draws == 660, f"the frozen seed set no longer yields 660 draws but {draws}"
    distance, seed, index, raw, amount = closest

    assert distance == published_distance, (
        f"§8.6a publishes {published_distance} paise as the closest approach to a rounding "
        f"boundary; the frozen seed set now gives {distance}. The specification's figure is "
        f"stale — report it, do not edit the assertion."
    )
    assert (seed, index, raw) == (
        int(published_seed),
        int(published_index),
        int(published_raw),
    )
    assert str(amount).startswith("12662203.498813313939")

    # "≈ 4.2 × 10⁵ ULPs", under §8.6a's own words: the distance RELATIVE TO THE AMOUNT.
    relative_ulps = float(distance) / float(amount) / 2.0**-52
    assert 4.1e5 < relative_ulps < 4.3e5, relative_ulps

    assert float_disagreements == 0, (
        f"§8.6a publishes that a float implementation reproduces all 660 amounts "
        f"identically; {float_disagreements} now differ. That does not license a float "
        f"world — Decimal is required because the claim must be PROVABLE — but the "
        f"published figure has stopped being true and must be corrected, not ignored."
    )
