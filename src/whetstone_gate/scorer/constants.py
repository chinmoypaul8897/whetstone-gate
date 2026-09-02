"""The scoring constants — supplied to this package as DATA, never read from disk by it.

⚠️ **HARD RULE 8's PURITY SEPARATION, APPLIED TO `config/`.** *"Core logic takes data in and
returns results — no I/O, clock, network, or randomness inside it. Side effects live in a thin
outer shell."* Reading `config/protocol.yaml` is I/O, so it happens in the caller and the four
values arrive here as an argument. `whetstone_gate.config` is therefore **not** in
`scorer/`'s import closure, which is the strongest form of the moat this package can hold:
`check_roles` **D3** can find nothing shared with `gates/` because there is nothing under
`whetstone_gate` in `scorer/`'s closure at all.

⚠️ **HARD RULE 9 IS NOT WEAKENED BY THAT, IT IS ENFORCED ONE LAYER DOWN.** *"no default for a
required value — a missing value is a hard refusal, never a silent fallback."*
:func:`constants_from` has **no** default for any of the four, and refuses on absence, on the
wrong type, and on a ``TODO_`` sentinel. There is no ``get(name, fallback)`` anywhere in this
module and none may be added: a scorer that fell back to a cap of its own would publish a
number nobody pre-registered.

**The four, with the `config/` key paths they must be read from** — the paths are recorded
because :file:`tests/goldens/golden2_invariants.json`'s own constants block records that a
value quoted under the *wrong* key path is hard rule 9's defect one level down, and because
S4's width lives at ``invariants.s4_in_flight_window_width`` and **not** under ``world.``
(`QUESTIONS.md` **Q-091**).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

#: ``(attribute, config/ key path)`` for every constant the eight predicates need.
#: ``per_action_cap_paise`` is E1's; ``episode_cap_paise`` is E2's and E3's;
#: ``s4_in_flight_window_width`` is S4's; ``currency`` is the third term of S2-amt's
#: withdrawn ``(payment_id, amount, currency)`` TRIPLE.
REQUIRED_CONSTANTS: tuple[tuple[str, str], ...] = (
    ("per_action_cap_paise", "protocol.yaml:money.per_action_cap_paise"),
    ("episode_cap_paise", "protocol.yaml:money.episode_cap_paise"),
    ("s4_in_flight_window_width", "protocol.yaml:invariants.s4_in_flight_window_width"),
    ("currency", "protocol.yaml:world.currency"),
)

#: The sentinel prefix `whetstone_gate.config` writes for a value that is not decided yet.
#: Recognised here **again**, on purpose: this package does not import that loader, so a
#: caller who read a sentinel through some other path would otherwise hand it to a
#: predicate. Hard rule 8's "written twice, on purpose" applied to a three-character string.
UNDETERMINED_PREFIX = "TODO_"


class ScorerConfigError(ValueError):
    """A required scoring constant is absent, undetermined, or of the wrong type.

    A hard refusal in every case. `CLAUDE.md` hard rule 9: *"a missing value is a hard
    refusal, never a silent fallback."*
    """


@dataclass(frozen=True)
class ScoringConstants:
    """The four values the eight predicates read. Frozen, and built only by :func:`constants_from`.

    ⚠️ **THE CURRENCY IS CARRIED EVEN THOUGH IT CANNOT DISCRIMINATE IN THIS WORLD, AND THAT IS
    STATED RATHER THAN QUIETLY EXPLOITED.** `CONTEXT.md` §8.6a: *"`currency` is `INR`
    throughout"*, so every term of S2-amt's triple that is a currency is the same value and the
    triple behaves exactly like the pair on any ledger this project can produce. It is kept
    because the **withdrawn predicate** is the triple — golden 2 pins that wording — and
    dropping the term would quietly redefine the predicate whose false positives are the
    published finding. What it does **not** do is add discriminating power, and no reader
    should be left to work that out.
    """

    per_action_cap_paise: int
    episode_cap_paise: int
    s4_in_flight_window_width: int
    currency: str


def constants_from(values: Mapping[str, Any]) -> ScoringConstants:
    """Build :class:`ScoringConstants` from ``values``, refusing anything short of complete.

    ``values`` is what the caller read out of `config/` through the one loader. Three
    refusals, each a hard rule 9 case:

      * a key is **absent** — the caller never read it;
      * a value is a ``TODO_`` sentinel — `config/` has it, undecided;
      * a value is the **wrong type** — an integer cap arriving as a string would compare
        as text and silently change every breach list.

    ``bool`` is refused where an ``int`` is required: ``True`` is an ``int`` in Python and a
    cap of ``True`` would compare as ``1``.
    """
    missing = [name for name, _ in REQUIRED_CONSTANTS if name not in values]
    if missing:
        paths = {name: path for name, path in REQUIRED_CONSTANTS}
        raise ScorerConfigError(
            "the scorer was handed an incomplete constants mapping: "
            + ", ".join(f"{name} (read it from {paths[name]})" for name in missing)
            + ". Hard rule 9: a missing required value is a HARD REFUSAL, never a silent "
            "fallback. This package deliberately does not read config/ itself, so it cannot "
            "repair the omission and must not guess a cap."
        )

    for name, path in REQUIRED_CONSTANTS:
        value = values[name]
        if isinstance(value, str) and value.startswith(UNDETERMINED_PREFIX):
            raise ScorerConfigError(
                f"{name} is the sentinel {value!r} from {path}: the value is not decided "
                f"yet, and scoring an episode against an undecided constant would publish a "
                f"number that was never pre-registered"
            )

    for name in ("per_action_cap_paise", "episode_cap_paise", "s4_in_flight_window_width"):
        value = values[name]
        if isinstance(value, bool) or not isinstance(value, int):
            raise ScorerConfigError(
                f"{name} must be an integer (paise, or a count of tool calls); received "
                f"{value!r} of type {type(value).__name__}. PROCESS.md S5.1: integer paise "
                f"end to end, never a float and never a rupee decimal"
            )
        if value < 0:
            raise ScorerConfigError(f"{name} must not be negative; received {value!r}")

    currency = values["currency"]
    if not isinstance(currency, str) or not currency:
        raise ScorerConfigError(
            f"currency must be a non-empty string; received {currency!r}"
        )

    return ScoringConstants(
        per_action_cap_paise=values["per_action_cap_paise"],
        episode_cap_paise=values["episode_cap_paise"],
        s4_in_flight_window_width=values["s4_in_flight_window_width"],
        currency=currency,
    )
