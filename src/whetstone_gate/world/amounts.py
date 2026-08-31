"""The log-uniform amount, computed in `decimal.Decimal`. **This is correctness, not style.**

`CONTEXT.md` §8.6a, and `QUESTIONS.md` Q-019's first load-bearing decision:

    `math.exp` and `math.log` call the platform libm, which may differ by one unit in the
    last place between platforms, and near ₹1,50,000 one ULP flips the rounded paise
    integer. Hard rule 10 and §5.1 both **claim and test** a byte-identical world, so a
    libm-dependent world would pass its own test on the machine that produced the golden
    and **fail on a reviewer's**. `Decimal.ln()` and `Decimal.exp()` are required by the
    General Decimal Arithmetic specification to be **correctly rounded** to the context
    precision, and are therefore identical on every platform.

So the rule for this module is absolute and is asserted by a test rather than trusted:
**no `math.exp`, no `math.log`, and no binary `float` appears anywhere on the amount
path.** `PROCESS.md` §5.1's money row says the same thing from the other side — *"Rounding
is ROUND_HALF_UP on exact integers or `Decimal`, never on a binary float."*

**Every context is passed explicitly.** Not one operation here depends on the ambient
`decimal` context, so nothing a caller has done to `decimal.getcontext()` — in this
process, in a test, or in some future runner thread — can move a published number.

The formula, §8.6a verbatim::

    amount       = exp( ln(lo) + u * ( ln(hi) - ln(lo) ) )
    amount_paise = int(amount.quantize(Decimal(1), rounding=ROUND_HALF_UP))

Boundary behaviour, asserted by golden 7: ``u = 0`` gives exactly the minimum and
``u -> 1`` gives exactly the maximum. Log-uniform over the **closed** paise interval.
"""

from __future__ import annotations

import decimal
from decimal import Context, Decimal

#: Every `decimal` rounding mode's name begins with this. The prefix — not a list of mode
#: names — is what :func:`rounding_mode` validates against, so that ``money.rounding`` is
#: read from `config/` (hard rule 9) without this module carrying a second copy of the
#: mode's name that could drift from the frozen one.
_ROUNDING_PREFIX = "ROUND_"


class UnknownRoundingMode(RuntimeError):
    """``money.rounding`` in `config/` is not a `decimal` rounding mode.

    A hard refusal. `PROCESS.md` §5.1: money rounding is ROUND_HALF_UP on `Decimal` or on
    integers and **never** on a binary float; a rounding mode nobody recognises must stop
    the run, not pick one.
    """


def rounding_mode(name: str) -> str:
    """Resolve the `decimal` rounding mode ``name`` names.

    ``name`` is ``money.rounding`` from `config/protocol.yaml`. It is resolved rather than
    hardcoded because hard rule 9 puts *every spec-specified value* in `config/`, and
    because `config/` is the artefact the pre-registration freezes: a rounding mode written
    into source is a rounding mode the freeze does not cover.
    """
    if not name.startswith(_ROUNDING_PREFIX) or not hasattr(decimal, name):
        raise UnknownRoundingMode(
            f"config/protocol.yaml gives money.rounding={name!r}, which is not a "
            f"decimal rounding mode. Hard rule 9: a missing or unreadable required value "
            f"is a hard refusal, never a silent fallback."
        )
    return getattr(decimal, name)


def exact_u(raw: int, context: Context) -> Decimal:
    """Return ``u`` — the **exact rational** ``raw / 2^32`` — as a `Decimal`.

    ⚠️ §8.6a: *"`u` IS THE EXACT RATIONAL `raw / 2^32`, NEVER THE JAVASCRIPT FLOAT
    DIVISION."* The spike returned ``raw / 4294967296`` as a binary float; this project
    does not, because the value feeds a money computation.

    The division is exact at the configured precision rather than merely accurate:
    ``2^-32`` terminates in 32 decimal places and ``raw`` carries at most 10 digits, so 42
    significant digits suffice and §8.6a's ``prec=50`` leaves room to spare. A test
    asserts the round trip ``u * 2^32 == raw`` on every draw of the golden seed, so
    "exact" is checked rather than reasoned about.
    """
    from .prng import U32_RANGE

    return context.divide(Decimal(raw), Decimal(U32_RANGE))


def log_uniform_paise(
    u: Decimal,
    *,
    minimum_paise: int,
    maximum_paise: int,
    context: Context,
    rounding: str,
) -> int:
    """Map ``u`` in [0, 1) onto the closed log-uniform paise interval.

    All five inputs come from `config/` by way of :class:`~whetstone_gate.world.spec.WorldSpec`;
    this function chooses nothing. It returns integer **paise** — `PROCESS.md` §5.1's first
    row, *"integer paise end to end. Never a float, never a rupee decimal."*
    """
    low = Decimal(minimum_paise)
    high = Decimal(maximum_paise)

    ln_low = low.ln(context=context)
    span = context.subtract(high.ln(context=context), ln_low)
    exponent = context.add(ln_low, context.multiply(u, span))
    amount = exponent.exp(context=context)

    return int(amount.quantize(Decimal(1), rounding=rounding, context=context))
