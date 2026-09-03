"""The verdict grammar, and the arm verdict sets **refused at construction**.

`CONTEXT.md` §9.3, verbatim::

    Verdict = ALLOWED | DENIED(reason) | INDETERMINATE(obligation)

*"A verdict is a TYPE, not a boolean."* A declared obligation with no result becomes
``INDETERMINATE`` **at construction**, and ``INDETERMINATE`` blocks exactly as hard as
``DENIED``. *"Checked and passed" must be distinguishable from "never checked."*

⚠️ **THE ATTACKER CANNOT TELL THEM APART, AND THAT IS THE POINT.** `CONTEXT.md` §8.6,
lines 995-996: the generic denial message every gate returns on DENY is
*"This action was blocked by policy."* and *"An `INDETERMINATE` verdict returns the same
string."* So the distinction is **internal to the ledger and invisible to the attacker**.
A gate that returned a different string for ``INDETERMINATE`` would leak that a check was
skipped, which is a policy oracle. :meth:`Verdict.attacker_message` is the one channel to
the attacker and it reads **neither** ``reason`` **nor** ``obligation`` — asserted by a
test that parses this module rather than by trusting this sentence.

⚠️ **A VERDICT OUTSIDE ITS ARM'S SET IS REFUSED AT CONSTRUCTION**, not filtered at the
boundary and not logged and dropped. `tests/goldens/golden9_arm4_kernel.json`'s
``arm_verdict_sets`` block states why, and it is the reason this refusal lives in
``__post_init__`` and not in a factory a caller could route around:

    *An arm-1 gate that can CONSTRUCT a `DENIED` has a code path that could deny, and
    "arm 1 has no gate" would then be a claim about which branch happened to run rather
    than about what the type permits.*

C7 built exactly this shape for the ledger entry and it is the stronger form.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# --------------------------------------------------------------------------------------
# The arms
# --------------------------------------------------------------------------------------

#: `CONTEXT.md` §8.6a's five arms, by the identifiers golden 9 and the ledger use.
ARM_1 = "1"
ARM_2 = "2"
ARM_2S = "2S"
ARM_3 = "3"
ARM_4 = "4"

ARMS: tuple[str, ...] = (ARM_1, ARM_2, ARM_2S, ARM_3, ARM_4)


class Outcome(Enum):
    """The three verdict constructors of `CONTEXT.md` §9.3, and there are no others."""

    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    INDETERMINATE = "INDETERMINATE"


#: `CONTEXT.md` §8.6a, verbatim: *"Which verdicts each arm can emit: arm 1 -> `ALLOWED`
#: only (no gate); arms 2/2S/3 -> `ALLOWED` / `DENIED`; arm 4 -> `ALLOWED` / `DENIED` /
#: `INDETERMINATE` (the last when a declared obligation has no result, per §9.3)."*
#:
#: ⚠️ Written here as data and **compared against golden 9's own ``arm_verdict_sets``
#: block by a test**, so this table is checkable rather than asserted.
ARM_VERDICT_SETS: dict[str, frozenset[Outcome]] = {
    ARM_1: frozenset({Outcome.ALLOWED}),
    ARM_2: frozenset({Outcome.ALLOWED, Outcome.DENIED}),
    ARM_2S: frozenset({Outcome.ALLOWED, Outcome.DENIED}),
    ARM_3: frozenset({Outcome.ALLOWED, Outcome.DENIED}),
    ARM_4: frozenset({Outcome.ALLOWED, Outcome.DENIED, Outcome.INDETERMINATE}),
}


class VerdictOutsideArmSet(ValueError):
    """The arm cannot emit that outcome. Raised **at construction**, never at a boundary.

    A hard refusal with no permissive path, for the reason golden 9 states: an arm whose
    type permits a verdict has a code path that could produce it, and the claim *"arm 1
    has no gate"* would then be about which branch ran rather than about what the type
    allows.
    """


class MalformedVerdict(ValueError):
    """A verdict was built without the payload its own constructor requires.

    ``DENIED`` carries a reason; ``INDETERMINATE`` carries an obligation; ``ALLOWED``
    carries neither. A ``DENIED`` with an empty reason is a denial nobody can audit, and
    an ``INDETERMINATE`` with no obligation has lost the only thing that distinguishes it
    from a denial in the ledger — which is the whole of §9.3.
    """


class UnknownArm(ValueError):
    """The arm identifier is not one of `CONTEXT.md` §8.6a's five.

    Refused rather than defaulted: a typo that fell through to a permissive set would give
    a sixth, unpre-registered arm the union of everybody's verdicts.
    """


@dataclass(frozen=True)
class Verdict:
    """One gate decision, bound to the arm that made it.

    The arm is a **field and not a caller's convention** precisely so the refusal can live
    in ``__post_init__``: there is no way to obtain a ``Verdict`` object at all without
    passing through the check.
    """

    arm: str
    outcome: Outcome
    reason: str | None = None
    obligation: str | None = None

    def __post_init__(self) -> None:
        permitted = ARM_VERDICT_SETS.get(self.arm)
        if permitted is None:
            raise UnknownArm(
                f"arm {self.arm!r} is not one of CONTEXT.md S8.6a's five arms {ARMS}. "
                f"A verdict carries the arm that made it so that the arm's verdict set "
                f"can be enforced HERE, at construction."
            )
        if self.outcome not in permitted:
            raise VerdictOutsideArmSet(
                f"arm {self.arm} may emit only "
                f"{sorted(o.value for o in permitted)}, never {self.outcome.value}. "
                f"CONTEXT.md S8.6a fixes each arm's verdict set and golden 9 pins it: a "
                f"verdict outside an arm's set is REFUSED AT CONSTRUCTION, because an "
                f"arm-1 gate that can CONSTRUCT a DENIED has a code path that could deny."
            )
        if self.outcome is Outcome.DENIED:
            if not self.reason:
                raise MalformedVerdict("DENIED requires a non-empty reason (S9.3).")
            if self.obligation is not None:
                raise MalformedVerdict("DENIED carries no obligation (S9.3).")
        elif self.outcome is Outcome.INDETERMINATE:
            if not self.obligation:
                raise MalformedVerdict(
                    "INDETERMINATE requires a non-empty obligation: S9.3's whole point is "
                    "that 'never checked' is a DIFFERENT ledger fact from 'checked and "
                    "denied', and the obligation is the field that carries the difference."
                )
            if self.reason is not None:
                raise MalformedVerdict("INDETERMINATE carries no reason (S9.3).")
        else:
            if self.reason is not None or self.obligation is not None:
                raise MalformedVerdict("ALLOWED carries neither reason nor obligation.")

    # -- the two properties every caller actually asks ----------------------------------

    @property
    def allows(self) -> bool:
        """True only for ``ALLOWED``.

        ⚠️ ``INDETERMINATE`` blocks **exactly as hard as** ``DENIED`` (§9.3), so this is
        deliberately not ``outcome is not DENIED``.
        """
        return self.outcome is Outcome.ALLOWED

    @property
    def blocks(self) -> bool:
        """True for ``DENIED`` **and** for ``INDETERMINATE``. The complement of :attr:`allows`."""
        return not self.allows

    # -- the ONE channel to the attacker ------------------------------------------------

    def attacker_message(self, generic_denial: str) -> str | None:
        """What the attacker is told. ``None`` when the action was allowed.

        ⚠️ **THIS FUNCTION READS NEITHER ``reason`` NOR ``obligation``, AND A TEST PARSES
        THIS MODULE TO ASSERT IT.** §8.6's generic denial message is *"identical across
        arms, leaking no policy"*, and an ``INDETERMINATE`` returns the **same string** —
        so a `DENIED` and an `INDETERMINATE` are byte-identical from where the attacker
        stands. `CONTEXT.md` §8.6 lines 995-996; golden 9's ``verdict_type`` block.

        ``generic_denial`` is passed in rather than read from disk: this module is core
        logic and hard rule 8 keeps the file read in the shell.
        """
        if self.outcome is Outcome.ALLOWED:
            return None
        return generic_denial


def allowed(arm: str) -> Verdict:
    """``ALLOWED`` for ``arm``. Legal for every arm."""
    return Verdict(arm=arm, outcome=Outcome.ALLOWED)


def denied(arm: str, reason: str) -> Verdict:
    """``DENIED(reason)`` for ``arm``. Refused at construction for arm 1."""
    return Verdict(arm=arm, outcome=Outcome.DENIED, reason=reason)


def indeterminate(arm: str, obligation: str) -> Verdict:
    """``INDETERMINATE(obligation)`` for ``arm``. Legal for arm 4 alone."""
    return Verdict(arm=arm, outcome=Outcome.INDETERMINATE, obligation=obligation)
