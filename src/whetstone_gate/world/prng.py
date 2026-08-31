"""`mulberry32`, REIMPLEMENTED IN PYTHON from `CONTEXT.md` §8.6a's four-line step.

⚠️ **REIMPLEMENTED, NOT PORTED, AND THE DISTINCTION IS THE WHOLE REASON GOLDEN 7 EXISTS.**
`CONTEXT.md` §16 requires the JavaScript spike's PRNG to be *rewritten*, and `PROCESS.md`
§5.2 says why in one sentence: *"A mis-ported `mulberry32` gives every arm a different
exam, every reported number moves, and nothing else in this process would detect it."*
This module was written from §8.6a's four lines of prose and checked against the
architect's independently-derived golden afterwards — never the other way round.

**The step, verbatim from §8.6a:**

```
a   = (a + 0x6D2B79F5) mod 2^32
t   = (a XOR (a >>> 15)) * (1 | a)                            mod 2^32
t   = ((t + ((t XOR (t >>> 7)) * (61 | t))) mod 2^32) XOR t
raw = (t XOR (t >>> 14)) mod 2^32
```

`>>>` is a **logical** shift on the 32-bit value and every product is mod 2^32 (JavaScript
`Math.imul`). Python's `>>` on a non-negative `int` is already logical, and the state is
kept masked to 32 bits, so the two agree by construction rather than by luck. The
generator yields `raw`, a 32-bit **unsigned** integer.

**Where the four magic numbers come from, and why they are not `config/` keys.**
Hard rule 9 puts every *spec-specified* value in `config/`. `0x6D2B79F5`, the shifts 15, 7
and 14, and the odd-forcing masks `1 |` and `61 |` are not spec-specified values in that
sense: they are **the definition of the algorithm named `mulberry32`**, a third-party
public-domain generator. Changing one does not express a different merchant policy — it
produces a different PRNG under the same name. What *is* an author choice is **which**
generator the world uses, and that choice lives in `config/protocol.yaml` at
``world.prng``. :func:`for_seed` reads it and **refuses** on any other value rather than
silently generating from something the pre-registration did not name.

**No I/O, no clock, no ambient randomness.** The whole of `whetstone_gate.world`'s
determinism claim (hard rule 10, `PROCESS.md` §5.1's *"Seeds and determinism"* row) starts
here: the sequence is a pure function of the integer seed.
"""

from __future__ import annotations

#: The generator's output width, as a modulus. `u` is the exact rational ``raw / U32_RANGE``
#: (§8.6a), so this value is also the denominator of every amount draw.
U32_RANGE = 1 << 32

#: ``U32_RANGE - 1``. Masking after every operation is what makes Python's arbitrary-width
#: integers behave as the 32-bit machine words the algorithm is defined over.
U32_MASK = U32_RANGE - 1

_INCREMENT = 0x6D2B79F5
_SHIFT_A = 15
_SHIFT_B = 7
_SHIFT_C = 14
_ODD_MASK_A = 1
_ODD_MASK_B = 61

#: The one generator name this module implements. Compared against ``world.prng``.
ALGORITHM = "mulberry32"


class UnknownGenerator(RuntimeError):
    """``config/`` names a PRNG this module does not implement.

    A hard refusal, never a fallback (hard rule 9). A world generated from an unnamed
    generator would reproduce nothing and would still look like a world.
    """


class Mulberry32:
    """A seeded `mulberry32` stream.

    Stateful by nature — that is what a PRNG is — but the state is entirely internal and
    is a pure function of the seed and of the number of draws taken, so two instances
    built from the same seed produce identical sequences forever.
    """

    __slots__ = ("_state", "_taken")

    def __init__(self, seed: int) -> None:
        self._state = seed & U32_MASK
        self._taken = 0

    @property
    def draws_taken(self) -> int:
        """How many values this instance has yielded.

        Exposed because §8.6a's draw budget — *"EXACTLY ELEVEN DRAWS PER SEED … THE PROBE
        CONSUMES NO DRAW"* — is a property of the generator's use, and a claim that is
        merely asserted in prose is a claim nothing checks. The world records it and
        `tests/test_c2_world.py` reads it back.
        """
        return self._taken

    def next_u32(self) -> int:
        """Advance the stream and return the next raw 32-bit unsigned integer."""
        state = (self._state + _INCREMENT) & U32_MASK
        self._state = state

        t = ((state ^ (state >> _SHIFT_A)) * (_ODD_MASK_A | state)) & U32_MASK
        t = ((t + (((t ^ (t >> _SHIFT_B)) * (_ODD_MASK_B | t)) & U32_MASK)) & U32_MASK) ^ t
        raw = (t ^ (t >> _SHIFT_C)) & U32_MASK

        self._taken += 1
        return raw

    def take(self, count: int) -> tuple[int, ...]:
        """Return the next ``count`` raw values, in order."""
        return tuple(self.next_u32() for _ in range(count))


def for_seed(seed: int, algorithm: str) -> Mulberry32:
    """Build the generator ``algorithm`` names, seeded with ``seed``.

    ``algorithm`` comes from ``world.prng`` in `config/protocol.yaml`, which is a
    pre-registration artefact. Anything other than :data:`ALGORITHM` is
    :class:`UnknownGenerator` — the choice is the pre-registration's to make and this
    module's to obey, and a silent substitution here would move every number the project
    publishes while every test still passed.
    """
    if algorithm != ALGORITHM:
        raise UnknownGenerator(
            f"config/protocol.yaml names world.prng={algorithm!r}, and this module "
            f"implements only {ALGORITHM!r}. Hard rule 9: a value config/ supplies is "
            f"obeyed or refused, never quietly substituted. CONTEXT.md §8.6a fixes the "
            f"generator, and config/ is frozen from `prereg-v1`."
        )
    return Mulberry32(seed)
