"""The two gate constants — supplied to this package as DATA, never read from disk by it.

⚠️ **HARD RULE 8's PURITY SEPARATION, APPLIED TO `config/`, AND WRITTEN TWICE ON PURPOSE.**
*"Core logic takes data in and returns results — no I/O, clock, network, or randomness
inside it. Side effects live in a thin outer shell."* Reading `config/protocol.yaml` is
I/O, so it happens in :mod:`whetstone_gate.gates.shell` and the two values arrive here as
an argument. `whetstone_gate.scorer.constants` does the same thing for the scorer's four,
and **the duplication is the moat**: the two packages share no first-party module, so any
logic they both need is written twice.

⚠️ **HARD RULE 9 IS NOT WEAKENED BY THAT, IT IS ENFORCED ONE LAYER DOWN.** *"no default
for a required value — a missing value is a hard refusal, never a silent fallback."*
:func:`constants_from` has **no** default for either value and refuses on absence, on the
wrong type, and on a ``TODO_`` sentinel. There is no ``get(name, fallback)`` in this module
and none may be added: a gate that fell back to a cap of its own would enforce an envelope
nobody pre-registered, and every escape number in `RESULTS.md` would be against the wrong
denominator.

**The two, with the `config/` key paths they must be read from.** The paths are recorded
because golden 9's own ``constants`` block records that *"a value quoted here under the
WRONG key path is the same defect one level down"*.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

#: ``(attribute, config/ key path)`` for every constant the six live clauses need.
#: ``per_action_cap_paise`` is E1's, i.e. policy clause P1; ``episode_cap_paise`` is E2's
#: and E3's, i.e. clauses P2 and P3.
REQUIRED_CONSTANTS: tuple[tuple[str, str], ...] = (
    ("per_action_cap_paise", "protocol.yaml:money.per_action_cap_paise"),
    ("episode_cap_paise", "protocol.yaml:money.episode_cap_paise"),
)

#: The sentinel prefix `whetstone_gate.config` writes for a value that is not decided yet.
#: Recognised here **again**, on purpose: this module does not import that loader, so a
#: caller who read a sentinel through some other path would otherwise hand it to a clause.
#: Hard rule 8's *"written twice, on purpose"* applied to a five-character string.
UNDETERMINED_PREFIX = "TODO_"


class GateConfigError(ValueError):
    """A required gate constant is absent, undetermined, or of the wrong type.

    A hard refusal in every case. `CLAUDE.md` hard rule 9: *"a missing value is a hard
    refusal, never a silent fallback."*
    """


@dataclass(frozen=True)
class GateConstants:
    """The two values the six live clauses read. Frozen, built only by :func:`constants_from`."""

    per_action_cap_paise: int
    episode_cap_paise: int


def constants_from(values: Mapping[str, Any]) -> GateConstants:
    """Build :class:`GateConstants` from ``values``, refusing anything short of complete.

    ``values`` is what the caller read out of `config/` through the one loader. Three
    refusals, each a hard rule 9 case: **absent**, **undetermined** (a ``TODO_`` sentinel),
    and **the wrong type** — an integer cap that arrived as a string would compare as text
    and silently allow everything.
    """
    resolved: dict[str, int] = {}
    for name, key_path in REQUIRED_CONSTANTS:
        if name not in values:
            raise GateConfigError(
                f"gate constant {name!r} is missing. Read it from {key_path} through "
                f"whetstone_gate.config and pass it in. Hard rule 9: a missing required "
                f"value is a hard refusal, never a silent fallback — this function has no "
                f"default to give you."
            )
        value = values[name]
        if isinstance(value, str) and value.startswith(UNDETERMINED_PREFIX):
            raise GateConfigError(
                f"gate constant {name!r} is not determined yet (sentinel {value!r}), read "
                f"from {key_path}. Hard rule 9 forbids substituting a value here."
            )
        if not isinstance(value, int) or isinstance(value, bool):
            raise GateConfigError(
                f"gate constant {name!r} must be an int in paise, not "
                f"{type(value).__name__} ({value!r}), read from {key_path}. Hard rule 7: "
                f"integer paise end to end."
            )
        resolved[name] = value
    return GateConstants(**resolved)
