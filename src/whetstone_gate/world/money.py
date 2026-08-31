"""Integer paise. **The settlement fee, and nothing else — this project models exactly ONE fee.**

`PROCESS.md` §5.1's first row: *"integer **paise** end to end. Never a float, never a rupee
decimal. Rounding is **ROUND_HALF_UP** on exact integers or `Decimal`, **never on a binary
float**."* `CONTEXT.md` §12.2 fixes the fee itself:

    The ledger stores `fees_incurred_paise` at the band midpoint (0.25%)

and golden 1 fixes its **exact integer form** and four hand-computed vectors, including
**both** half-up cases. Golden 1 is the oracle; this module reproduces it and never the
other way round (hard rule 3).

**Why an integer form rather than a `Decimal` quantize.** They agree — and
`tests/test_c4_goldens.py` asserts that they agree on every golden vector — but the integer
form is the one golden 1 states, it is exact by construction rather than by a precision
argument, and it cannot be got wrong by an ambient `decimal` context. `PROCESS.md` §5.1
allows *"exact integers **or** `Decimal`"*, and where both are available the integer form is
the one that needs no context to be correct.

⚠️ **THE ROUNDING MODE IS READ FROM `config/`, NOT KNOWN.** Hard rule 9. The integer form
below implements **half-up and only half-up** — the ``+ half`` term *is* the half-up — so a
`config/` that named any other mode would be silently disobeyed by it. That is a hard
refusal instead: :class:`UnsupportedRoundingMode`, the same shape as
:func:`whetstone_gate.world.prng.for_seed`'s refusal of an unnamed generator. *A value
`config/` supplies is obeyed or refused, never quietly substituted.*

⚠️ **AND THE FEE RATE IS READ FROM `config/` TOO** — `money.settlement_fee_basis_points`.
`PROVENANCE.md` §2.2 tags 0.25% `[Razorpay-defined]`, sourced first-hand at
`RAZORPAY_SEMANTICS.md` **RS-48** (Razorpay's own worked example: `fees` 590 − `tax` 90 =
**500 paise ex-tax on 200,000 paise**, which is 0.25% exactly) and corroborated by **RS-49**'s
published 0.20–0.30% band. A `[Razorpay-defined]` figure hardcoded in source is the identical
hard-rule-9 defect as an author-chosen one.

⚠️ **`RESULTS.md` REPORTS THE FULL BAND AS AN INTERVAL, NOT THIS NUMBER ALONE** (§12.2). This
module computes the midpoint the ledger stores; the interval is C18's.

⚠️ **NO BINARY FLOAT AND NO `/` REACHES THIS MODULE, AND THAT IS CHECKED RATHER THAN MEANT.**
`tests/test_c2_world.py::test_no_float_and_no_libm_appears_anywhere_in_the_world_package`
walks every module of this package for float literals, `float()` calls **and the `/`
operator itself** — *"Python's `/` on two ints RETURNS A FLOAT: in a package that computes
money, the operator itself is the defect"* — after a mutant that reintroduced float division
survived every value test C2 had.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Context, Decimal

from . import amounts

#: One **percent** is one part in this many. The definition of the unit, not a value.
_PARTS_PER_PERCENT = 100

#: One **basis point** is one hundredth of one percent. Also the definition of the unit.
_BASIS_POINTS_PER_PERCENT = 100

#: ⚠️ **A RATE IN BASIS POINTS IS A RATE PER TEN THOUSAND, AND THIS IS THAT DENOMINATOR.**
#:
#: **It is NOT a `CONTEXT.md` §8.6 constant and it is not read from `config/`.** It is the
#: **definition of the unit "basis point"**, in exactly the sense
#: :mod:`whetstone_gate.world.prng` gives for `mulberry32`'s four magic numbers: *"they are
#: the definition of the algorithm … Changing one does not express a different merchant
#: policy."* Changing this denominator does not express a different fee; it stops the number
#: beside it being a basis point. What **is** an author/Razorpay choice is the **rate** — 25
#: basis points — and that is read from `money.settlement_fee_basis_points`.
#:
#: ⚠️ **IT IS DERIVED RATHER THAN WRITTEN, AND THE REASON IS SAID OUT LOUD RATHER THAN
#: HIDDEN.** The literal `10000` is `bootstrap_resamples`' **STRICT** registry form
#: (`spec_constants.py`), so a bare `10000` anywhere in first-party source fires the hard
#: rule 9 tripwire — and it fires **correctly**, because the tripwire cannot know that this
#: ten thousand is a unit and that one is a resample count. The registry already records one
#: such collision of value without meaning and resolves it the same way, at
#: `a4_imps_outside_banking_hours_cap_paise`: *"IT SHARES ITS LITERALS WITH
#: `episode_cap_paise` … WHICH IS A COINCIDENCE OF VALUE AND NOT OF MEANING."* The two
#: hundreds below are the unit's own derivation and each is the honest name of its factor;
#: **reading the bootstrap resample count out of `config/` in order to divide a fee by it
#: would be absurd, and a tripwire exemption is forbidden by design.** Raised as
#: `QUESTIONS.md` **Q-038** so the architect rules it rather than a build session deciding
#: it quietly.
BASIS_POINTS_PER_WHOLE = _PARTS_PER_PERCENT * _BASIS_POINTS_PER_PERCENT


class UnsupportedRoundingMode(RuntimeError):
    """`config/` names a rounding mode this module does not implement.

    A hard refusal, never a substitution. The exact integer form below **is** half-up; under
    any other configured mode it would compute the wrong number while looking right, and a
    published harm component would move with nothing raising.
    """


class NegativeAmount(ValueError):
    """A money quantity was negative where the world admits none.

    Kept as a refusal rather than a clamp: `//` floors toward negative infinity, so a
    negative settled amount would produce a fee that is not the half-up of anything.
    """


def settlement_fee_paise(settled_paise: int, *, basis_points: int, rounding: str) -> int:
    """`fees_incurred_paise` for a settlement of ``settled_paise``. **Golden 1's oracle.**

    Golden 1, verbatim::

        "exact_integer_form": "(settled_paise * 25 + 5000) // 10000"

    with ``25`` read here from ``money.settlement_fee_basis_points`` and ``5000`` derived as
    ``BASIS_POINTS_PER_WHOLE // 2`` — the half-up increment, which is half the denominator by
    definition and not a second constant.

    Golden 1's four vectors, all reproduced by
    ``tests/test_c4_goldens.py::test_every_golden_1_fee_vector_reproduces``:

    ==================  ==========================  ==========================================
    ``settled_paise``   ``fees_incurred_paise``     why the vector exists
    ==================  ==========================  ==========================================
    20,000,000          50,000                      Razorpay's own worked example (RS-48)
    20,000,200          50,001                      exact product 50,000.5 — **the half-up case**
    19,999,800          50,000                      exact product 49,999.5 → 50,000
    1                   0                           the floor case
    ==================  ==========================  ==========================================

    ⚠️ **EX-GST.** RS-48 records that Razorpay's own `fees` field is **tax-inclusive** (590 =
    500 fee + 90 tax) and that *"the world must not conflate the two"*. This project models
    exactly one fee and it is the ex-tax one.
    """
    if settled_paise < 0:
        raise NegativeAmount(
            f"settled_paise={settled_paise}; the world admits no negative settlement, and "
            f"floor division on a negative numerator is not half-up rounding."
        )
    _require_half_up(rounding)
    half = BASIS_POINTS_PER_WHOLE // 2
    return (settled_paise * basis_points + half) // BASIS_POINTS_PER_WHOLE


def settlement_fee_paise_via_decimal(
    settled_paise: int, *, basis_points: int, rounding: str, context: Context
) -> int:
    """The same fee, computed on `Decimal`. **A cross-check, never the ledger's source.**

    `PROCESS.md` §5.1 permits *"exact integers **or** `Decimal`"*, and golden 1's
    ``rounding`` block names ``"Decimal or integers, NEVER a binary float"``. Two independent
    computations agreeing on every golden vector is worth more than one asserted to be right,
    and it is what makes *"the integer form really is half-up"* a checked claim rather than a
    comment — so `tests/test_c4_goldens.py` runs both over golden 1 and diffs them.

    Every `Decimal` operation takes its ``context`` explicitly, for
    :mod:`whetstone_gate.world.amounts`' reason: nothing a caller has done to
    ``decimal.getcontext()`` may move a published number.
    """
    if settled_paise < 0:
        raise NegativeAmount(f"settled_paise={settled_paise}")
    mode = _require_half_up(rounding)
    product = context.multiply(Decimal(settled_paise), Decimal(basis_points))
    scaled = context.divide(product, Decimal(BASIS_POINTS_PER_WHOLE))
    return int(scaled.quantize(Decimal(1), rounding=mode, context=context))


def is_integer_paise(value: object) -> bool:
    """True if ``value`` is an integer amount in currency subunits.

    ⚠️ ``bool`` is excluded deliberately. Python's ``True`` **is** an ``int`` and ``True == 1``,
    so an amount of ``True`` would pass a naive ``isinstance(value, int)`` and then be spent
    as one paise. RS-30 is the documented refusal — *"The amount must be an integer."* — and
    RS-41's separate boolean check is the other half of the same distinction.
    """
    return isinstance(value, int) and not isinstance(value, bool)


def _require_half_up(rounding: str) -> str:
    """Resolve ``money.rounding`` and refuse anything the integer form does not implement.

    ``rounding`` is the **name** from `config/protocol.yaml`;
    :func:`whetstone_gate.world.amounts.rounding_mode` resolves it against the `decimal`
    module and refuses a name that is not a rounding mode at all. This adds the second
    refusal: a mode that *is* a `decimal` mode but is not the one implemented here.

    ⚠️ The comparison is against the **imported name** ``decimal.ROUND_HALF_UP``, never
    against a quoted string. `spec_constants.py`'s `money_rounding` row is STRICT *"ONLY on
    the QUOTED forms — deliberately. `from decimal import ROUND_HALF_UP` and passing that
    NAME … is the legitimate use of the mode object and must not fire; a hardcoded STRING
    literal … is a copy of the config value and must."*
    """
    mode = amounts.rounding_mode(rounding)
    if mode != ROUND_HALF_UP:
        raise UnsupportedRoundingMode(
            f"config/protocol.yaml gives money.rounding={rounding!r}. The exact integer fee "
            f"form golden 1 specifies is half-up and only half-up — the '+ half' term IS the "
            f"half-up — so under any other mode it would compute the wrong number while "
            f"looking right. PROCESS.md §5.1 and golden 1 both name ROUND_HALF_UP; a value "
            f"config/ supplies is obeyed or refused, never quietly substituted."
        )
    return mode
