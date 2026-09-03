"""**THE BENIGN SOLVER'S CONSTANTS — and the two the specification does not contain.**

Hard rule 9: *"Every spec-specified value lives in ``config/``, loaded through one loader,
with **no default for a required value** — a missing value is a hard refusal, never a
silent fallback."* This module is the **pure** half of that: it takes a mapping and returns
a frozen record, refusing anything absent, blank, sentinel-shaped or of the wrong type. The
reading is :mod:`whetstone_gate.benign.shell`'s, which is the only module in this package
that opens a file. The shape is `gates/constants.py`'s and `scorer/constants.py`'s,
deliberately — those two are the same idea written twice on purpose (hard rule 8's moat),
and this is a third reader that shares no module with either.

--------------------------------------------------------------------------------------
⚠️ THE FINDING THIS MODULE EXISTS TO MAKE UNMISSABLE — `QUESTIONS.md` `Q-156`
--------------------------------------------------------------------------------------

**MEASURED, 2026-09-03, over both files in ``config/``:** the only benign-solver key that
exists anywhere is ``benign_solver.target_tokens_per_episode``. There is **no**
``benign_solver.turn_budget``, **no** ``benign_solver.temperature``, **no**
``benign_solver.lane`` and **no** ``benign_solver.model``.

`CONTEXT.md` §12.3 defines the counter-metric as a paired delta measured at *"same task,
same seed, same solver, **same temperature**"* — so the temperature is **load-bearing on a
published number** and it is not written down anywhere. §8.6's own rule is that *"any
constant that is not in this table and not in ``config/`` is a defect, and finding one is a
review BLOCKER"*, and `config/protocol.yaml` itself names occurrences **4, 6 and 7** of
that table being found incomplete. This is the next one.

⚠️ **AND BORROWING THE ATTACKER'S VALUES IS A CLASS A DEVIATION, NOT A CONVENIENCE.**
``attacker.temperature`` and ``attacker.turn_budget`` are the *attacker's* pre-registered
figures. Reading them here would silently pre-register the benign solver at the same
numbers **and would look exactly like a config read while doing it** — the flattering
direction, because it makes a missing pre-registration indistinguishable from a present
one. So this module does **not** read them, and the two values are required **from the
caller**, which on the command line means a flag with ``required=True`` and no default.
That is the shape `Q-141`, `Q-144` and `Q-147` were each already answered in.

⚠️ **``config/`` IS NOT EDITED TO FIX THIS.** It is a pre-registration artefact
(`CLAUDE.md` §4, hard rule 9). The defect is recorded and published; it is not tidied away.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping

#: Every benign-solver value that **does** exist in ``config/``, as ``(field, key path)``.
#:
#: Written as a table rather than as calls scattered through a reader so that the set of
#: things this package takes from the pre-registration is one greppable list — and so that
#: the *absence* of a temperature row is visible **here**, rather than inferable from
#: silence somewhere else.
REQUIRED_CONSTANTS: tuple[tuple[str, str], ...] = (
    ("target_tokens_per_episode", "protocol.yaml:benign_solver.target_tokens_per_episode"),
)

#: The two values `CONTEXT.md` §12.3 needs and ``config/`` does not carry, each with the
#: reason it matters. **Named, so that a reader greps for them and finds the question
#: rather than nothing.** `Q-156`.
ABSENT_FROM_CONFIG: tuple[tuple[str, str], ...] = (
    ("turn_budget", "how many turns one benign episode may take"),
    ("temperature", "S12.3's 'same temperature' — part of the paired FP definition itself"),
)


class BenignConstantError(RuntimeError):
    """A benign-solver constant is absent, blank, undetermined or the wrong type.

    **Always a refusal, never a warning**, and never a default. A solver that ran with a
    guessed temperature would publish a counter-metric measured at a figure nobody
    pre-registered — which is `INCIDENTS.md` `INC-04`'s own lesson, pointed at the fix for
    `INC-04`.
    """


#: `whetstone_gate.config`'s sentinel prefix, restated as a **check** rather than imported
#: as a value: this module is pure and takes a plain mapping, so it cannot assume the
#: mapping arrived through the loader that already refuses sentinels. Belt for the shell's
#: braces — and the belt is what catches a caller that built the mapping by hand.
_SENTINEL_PREFIX = "TODO_"


def _require_int(values: Mapping[str, Any], field: str) -> int:
    """One positive integer, or a refusal naming the field."""
    if field not in values:
        raise BenignConstantError(
            f"benign-solver constant {field!r} is missing. Hard rule 9: a missing required "
            f"value is a hard refusal, never a silent fallback"
        )
    value = values[field]
    if isinstance(value, str) and value.startswith(_SENTINEL_PREFIX):
        raise BenignConstantError(
            f"benign-solver constant {field!r} is an undetermined sentinel ({value!r}). "
            f"Hard rule 9 forbids substituting a value here"
        )
    # ⚠️ `bool` is an `int` in Python, and every integer here is a count. A `True` that
    # read as 1 would be a turn budget of one turn, reported as if it were the real one.
    if isinstance(value, bool) or not isinstance(value, int):
        raise BenignConstantError(
            f"benign-solver constant {field!r} must be an int; got "
            f"{type(value).__name__} ({value!r})"
        )
    if value <= 0:
        raise BenignConstantError(
            f"benign-solver constant {field!r} must be positive; got {value}. A "
            f"non-positive turn budget or token target is an episode that cannot happen, "
            f"and it would divide into a rate as though it could"
        )
    return value


def _require_temperature(values: Mapping[str, Any], field: str) -> float:
    """The sampling temperature, or a refusal. **Not defaulted, on purpose** — see `Q-156`."""
    if field not in values:
        raise BenignConstantError(
            f"benign-solver constant {field!r} is missing. CONTEXT.md S12.3's paired "
            f"definition is 'same task, same seed, same solver, SAME TEMPERATURE', so the "
            f"temperature is part of the measurement and not an implementation detail. "
            f"config/ carries no benign_solver.temperature (Q-156): supply it explicitly"
        )
    value = values[field]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BenignConstantError(
            f"benign-solver constant {field!r} must be a number; got "
            f"{type(value).__name__} ({value!r})"
        )
    if value < 0:
        raise BenignConstantError(
            f"benign-solver constant {field!r} must not be negative; got {value}"
        )
    # ⚠️ **NaN AND inf ARE NUMBERS AND NEITHER IS A TEMPERATURE.** `NaN < 0` is False, so
    # the check above lets both through, and §12.3's paired definition turns on this figure
    # being the SAME across two runs — a value that is not equal to itself cannot satisfy
    # that. Found by this chunk's own adversarial pass, before its first commit.
    if not math.isfinite(value):
        raise BenignConstantError(
            f"benign-solver constant {field!r} must be finite; got {value}. S12.3's "
            f"definition is 'same task, same seed, same solver, SAME TEMPERATURE', and NaN "
            f"is not equal to itself"
        )
    return float(value)


@dataclass(frozen=True)
class BenignConstants:
    """Everything the benign solver runs on, with the provenance of each field stated.

    ``target_tokens_per_episode`` is ``config/``'s and is **pre-registered**.
    ``turn_budget`` and ``temperature`` are the **caller's**, because ``config/`` does not
    carry them (`Q-156`), and :attr:`supplied_by_caller` names them so that every report
    this package prints can say which figures were pre-registered and which were typed.
    """

    target_tokens_per_episode: int
    turn_budget: int
    temperature: float

    @property
    def supplied_by_caller(self) -> tuple[str, ...]:
        """The fields that came from a flag rather than from the pre-registration.

        ⚠️ **Printed beside every number this package produces.** A reader must be able to
        tell a pre-registered figure from one an operator typed, and the difference is
        invisible in the value itself.
        """
        return tuple(name for name, _why in ABSENT_FROM_CONFIG)


def constants_from(values: Mapping[str, Any]) -> BenignConstants:
    """Build the frozen record from a plain mapping. **Pure: no file, no clock, no default.**"""
    return BenignConstants(
        target_tokens_per_episode=_require_int(values, "target_tokens_per_episode"),
        turn_budget=_require_int(values, "turn_budget"),
        temperature=_require_temperature(values, "temperature"),
    )
