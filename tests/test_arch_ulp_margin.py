"""§8.6a's ULP margin, measured on every seed this project generates a world for.

**Why this file exists.** `CONTEXT.md` §8.6a used to justify its `decimal.Decimal`
requirement with the sentence *"near ₹1,50,000 one ULP flips the rounded paise integer."*
**C2 BUILD (`f0c50283`) measured it instead of repeating it, and it overstated its own
margin by about five orders of magnitude for the frozen seed set** — `QUESTIONS.md`
**Q-023**, UPHELD. §8.6a was corrected in `CONTEXT.md` **v1.4**, and the architect's ruling
requires the measurement to be *"kept as a committed test, whose failure message reads as a
finding rather than an instruction to relax the assertion."* **This is that test.**

⚠️ **THIS FILE DOES NOT LICENSE A FLOAT IMPLEMENTATION, AND THE DISTINCTION IS THE WHOLE
POINT OF Q-023's RULING.** Hard rule 10 and `PROCESS.md` §5.1 do not claim the world is
*probably* byte-identical across platforms — they **claim and test** that it **is**.
`Decimal.ln()`/`Decimal.exp()` are required by the General Decimal Arithmetic specification
to be **correctly rounded**, so that claim is **provable**. A float world's claim would rest
on the margin measured below, and **a margin argument has to be recomputed every time the
seed list changes** — which **§13.4's N decision rule is expressly allowed to do**.
**Provable beats comfortable.** The measurement is the *evidence*, never the *justification*.

**Relationship to `tests/test_c2_world.py`, stated rather than left to be discovered.** C2
ships its own margin test over the **scored** seeds, normalising the distance against
`amount_max_paise`. This one runs over **scored *and* pilot** — the full 660 draws §8.6a now
quotes — and normalises against **the amount itself**, which is the figure §8.6a states.
**Two tests measuring the same quantity by different routes is a property worth having, not
a duplication to collapse:** they would have to be wrong in the same direction to agree
falsely, and C2's is outside this session's fence and was not touched.
"""

from __future__ import annotations

import math
from decimal import ROUND_HALF_UP, Context, Decimal

import pytest

from whetstone_gate import config as cfg
from whetstone_gate.world import WorldSpec, amounts, generate, load_world_spec

#: ⚠️ **THE ASSERTION'S FAILURE MESSAGE, VERBATIM AS Q-023's RULING REQUIRES IT.** It is
#: named here rather than inlined so that it cannot be softened in passing while the
#: assertion around it is being edited for some other reason. **A test whose failure text
#: tells the reader to relax the test is not a test**, and the whole reason this measurement
#: is committed rather than quoted is that a future seed list may change the answer.
_FINDING_NOT_FAILURE = (
    "this is a finding, not a failure of the world: report it, do not relax the assertion."
)


@pytest.fixture(scope="module")
def protocol() -> cfg.Config:
    return cfg.load("protocol")


@pytest.fixture(scope="module")
def spec(protocol: cfg.Config) -> WorldSpec:
    return load_world_spec(protocol)


def _every_seed(protocol: cfg.Config) -> list[int]:
    """Every seed this project generates a world for: the scored 50, then the pilot 10.

    Read from `config/` rather than written here. **The pilot seeds are included on
    purpose** — §8.6a's corrected paragraph quotes a figure over **660** draws, and the
    scored set alone is 550. A test that measured a smaller set than the sentence it
    guards would leave the difference unguarded.
    """
    scored = range(
        protocol.require("seeds.scored_n50_first"),
        protocol.require("seeds.scored_n50_last") + 1,
    )
    pilot = range(
        protocol.require("seeds.pilot_first"), protocol.require("seeds.pilot_last") + 1
    )
    return [*scored, *pilot]


def _decimal_amount(raw: int, spec: WorldSpec, context: Context) -> Decimal:
    """§8.6a's amount formula, in `Decimal` — the world's own path."""
    low = Decimal(spec.amount_min_paise).ln(context=context)
    span = context.subtract(Decimal(spec.amount_max_paise).ln(context=context), low)
    u = amounts.exact_u(raw, context)
    return context.add(low, context.multiply(u, span)).exp(context=context)


def _float_paise(raw: int, spec: WorldSpec) -> int:
    """The same formula down the **binary64 / platform-libm** path §8.6a rejects.

    Deliberately written with `math.log`/`math.exp` and a float division, which is exactly
    what `whetstone_gate.world` is forbidden to contain and is asserted not to contain
    (`tests/test_c2_world.py`'s deliberate-non-uses block). **It lives in a test so the
    comparison can be made without the package ever growing the import.**
    """
    lo = math.log(spec.amount_min_paise)
    hi = math.log(spec.amount_max_paise)
    value = math.exp(lo + (raw / 2.0**32) * (hi - lo))
    # repr() round-trips the float exactly, so this rounds the FLOAT's own value rather
    # than re-introducing decimal precision the float path never had.
    return int(Decimal(repr(value)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _closest_approach(spec: WorldSpec, seeds: list[int]) -> tuple[Decimal, int, int, int, Decimal]:
    """Return the closest approach to a `.5` boundary, and where it happens."""
    context = Context(prec=spec.decimal_context_precision)
    half = Decimal("0.5")

    closest: tuple[Decimal, int, int, int, Decimal] | None = None
    for seed in seeds:
        for index, raw in enumerate(generate(seed, spec).raw_draws):
            amount = _decimal_amount(raw, spec, context)
            distance = abs((amount - int(amount)) - half)
            if closest is None or distance < closest[0]:
                closest = (distance, seed, index, raw, amount)

    assert closest is not None, "no draws were examined — see the count assertion below"
    return closest


def test_the_ulp_margin_over_every_generated_seed_exceeds_one_ulp(
    spec: WorldSpec, protocol: cfg.Config
) -> None:
    """The measurement `CONTEXT.md` §8.6a v1.4 states, re-derived rather than quoted.

    §8.6a's withdrawn sentence claimed *"near ₹1,50,000 one ULP flips the rounded paise
    integer."* **It does not, for these seeds, by about five orders of magnitude.** This
    asserts the direction that matters — that the margin is comfortably **greater** than one
    ULP — and reports the number when it is not.
    """
    seeds = _every_seed(protocol)
    draws = len(seeds) * spec.draws_per_seed
    assert draws == 660, (
        f"§8.6a v1.4 quotes its margin over 660 draws; `config/` now yields {draws} "
        f"({len(seeds)} seeds × {spec.draws_per_seed}). The seed list or the draw budget "
        f"changed, so §8.6a's stated figure no longer describes the set it names — and "
        f"{_FINDING_NOT_FAILURE}"
    )

    distance, seed, index, raw, amount = _closest_approach(spec, seeds)

    # Relative distance in binary64 units in the last place, normalised against the amount
    # itself — the figure §8.6a states. 2**-52 is binary64's relative spacing.
    relative_ulps = float(distance) / float(amount) / 2.0**-52

    assert relative_ulps > 1.0, (
        f"an amount in the generated seed set lies within one binary64 ULP of a rounding "
        f"boundary: seed {seed}, draw index {index}, raw {raw}, amount {amount}, distance "
        f"{distance} paise ({relative_ulps:.3g} ULPs). The float path could now flip it, so "
        f"§8.6a's withdrawn ULP sentence would be LIVE for these seeds rather than an "
        f"overclaim, and the margin argument a float implementation would need has just "
        f"failed. {_FINDING_NOT_FAILURE}"
    )

    # The measured margin is ~4.2e+05 ULPs. Asserting a floor several orders below it keeps
    # the test from becoming a brittle transcription of one number while still failing long
    # before the margin approaches one ULP — the point at which the risk becomes real.
    assert relative_ulps > 1.0e3, (
        f"the margin has collapsed to {relative_ulps:.3g} ULPs, from the ~4.2e+05 §8.6a "
        f"records at v1.4 — closest at seed {seed}, draw index {index}. Nothing is broken "
        f"yet, but the seed list has moved somewhere §8.6a's paragraph no longer describes. "
        f"{_FINDING_NOT_FAILURE}"
    )


def test_the_float_path_reproduces_every_amount_on_this_machine(
    spec: WorldSpec, protocol: cfg.Config
) -> None:
    """§8.6a v1.4's other measured claim: *"identical integer paise on all 660."*

    ⚠️ **THIS IS THE CLAIM THAT IS EASIEST TO MISREAD, SO IT IS STATED TWICE.** It says the
    overclaim *was* an overclaim — **not** that a float world would be acceptable. A float
    world's byte-identity would rest on this agreement holding on **every reviewer's
    platform**, which this test cannot check and which no amount of local green establishes;
    correctly-rounded `Decimal` needs no such argument. **`whetstone_gate.world` imports no
    `math` and this file is where that comparison is allowed to live.**

    A failure here is **not** a reason to change the world. It means this machine's libm now
    disagrees with correctly-rounded arithmetic somewhere in the frozen seed set — which is
    §8.6a's original concern arriving late, and is worth a line in `INCIDENTS.md`.
    """
    seeds = _every_seed(protocol)
    context = Context(prec=spec.decimal_context_precision)

    mismatches: list[str] = []
    examined = 0
    for seed in seeds:
        for index, raw in enumerate(generate(seed, spec).raw_draws):
            examined += 1
            exact = int(
                _decimal_amount(raw, spec, context).quantize(
                    Decimal(1), rounding=ROUND_HALF_UP
                )
            )
            approximate = _float_paise(raw, spec)
            if exact != approximate:
                mismatches.append(
                    f"seed {seed} draw {index} (raw {raw}): Decimal {exact} != float "
                    f"{approximate}"
                )

    assert examined == 660, f"expected 660 draws, examined {examined}"
    assert not mismatches, (
        "the float path no longer reproduces the world's amounts on this machine, so "
        "§8.6a v1.4's measured sentence — 'a float implementation reproduces all 660 "
        "amounts identically on this machine' — is no longer true here:\n  "
        + "\n  ".join(mismatches)
        + f"\n\n⚠️ The world is UNAFFECTED: it computes in Decimal and this is a statement "
        f"about the path it does NOT take. {_FINDING_NOT_FAILURE}"
    )
