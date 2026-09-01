"""**ONE LEDGER ENTRY, AND THE FIELD SET IS GOLDEN 5's — NOT THIS MODULE'S.**

`tests/goldens/golden5_tamper.json` was hand-derived by the architect **before this package
existed**, and every one of its twelve entries carries exactly these fifteen keys. Thirteen of
them are **content** and are hashed; ``prev_hash`` and ``hash`` are the chain and are excluded
from the digest, which the golden's own ``hash_rule`` states:

    entry_hash = SHA-256( prev_hash || canonical-JSON(entry, sorted keys, no whitespace) ),
    both as UTF-8 strings; the canonicalised entry EXCLUDES prev_hash and hash

⚠️ **THE FIELD SET IS THEREFORE CLOSED, AND THAT IS A CONSEQUENCE RATHER THAN A PREFERENCE.**
Every content field is inside the digest, so **adding a fourteenth would change every hash in
golden 5** and this package could no longer reproduce a single one of them. Hard rule 3 makes
the golden the oracle and forbids editing it, so the schema is settled by arithmetic, not by
taste. A later chunk that needs a field it cannot find here needs an **architect ruling**, not
an extra key — and the ruling would have to say what happens to golden 5.

**Where each field comes from, so a reviewer can check the set rather than trust it:**

  * ``ledger_seq``, ``tool``, ``a_class``, ``rejected_by_razorpay`` and the **four harm
    components** are `CONTEXT.md` §12.2's typed harm record, field for field.
  * ``turn_index``, ``arm`` and ``verdict`` are `PROCESS.md` §12.1's C7 row, which requires
    them by name *"so the §18 replay renderer is buildable from `evals/episodes/` alone"*.
  * ``target`` and ``amount_paise`` are the **call's arguments**.
    :attr:`whetstone_gate.world.semantics.MockWorld.log`'s own docstring assigns them here in
    those words — *"The ledger's `target` and `amount_paise` columns live HERE, not on the harm
    record … the arguments a call carried are the **ledger entry's** (C7's)"* — and golden 3
    carries both on an entry that has no field for them anywhere else.

---

## THE VERDICT SET IS THE ARM'S, AND ANYTHING ELSE IS A HARD REFUSAL

`CONTEXT.md` §8.6a, verbatim:

    **Which verdicts each arm can emit:** arm 1 → `ALLOWED` only (no gate); arms 2/2S/3 →
    `ALLOWED` / `DENIED`; arm 4 → `ALLOWED` / `DENIED` / `INDETERMINATE` (the last when a
    declared obligation has no result, per §9.3).

⚠️ **C7 BUILDS NO GATE — C9 DOES.** This module carries the field and **refuses a value the
arm cannot emit**, which is the half that can be built and tested before a gate exists. An
`INDETERMINATE` on arm 2 is not a verdict this experiment can produce, and a ledger that
accepted one would publish a number no arm generated. `PROCESS.md` §5.1 lists *"the gate
verdicts"* in the precision-critical domain for exactly that reason.

## WHY THE VOCABULARY IS NOT IN ``config/``

`CONTEXT.md` §8.6's table holds **values** — caps, rates, seeds, counts. ``ALLOWED`` and
``"2S"`` are the specification's own **vocabulary**, in the same sense as
:mod:`whetstone_gate.world.harm`'s ``A1``…``A6`` (*"the specification's own vocabulary — not
`CONTEXT.md` §8.6 constants, which are values"*) and the generator's ``"captured"`` /
``"authorized"``, which are Razorpay's. Changing one is not a knob-turn; it is a different
experiment, and §8.6a's sentence above is where it is fixed.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from types import MappingProxyType
from typing import Any, Mapping

from ..world.harm import A_CLASSES, COMPONENTS

# --------------------------------------------------------------------------------------
# The arms. `CONTEXT.md` §8: "Five arms. Five, everywhere in this document, in the repo, in
# `PROTOCOL.md`, in `§12`'s table and in the video."
# --------------------------------------------------------------------------------------

ARM_1 = "1"
ARM_2 = "2"
ARM_2S = "2S"
ARM_3 = "3"
ARM_4 = "4"

#: ⚠️ **EXACTLY FIVE.** A sixth arm is an arm no golden pins and no §12 table has a column for.
ARMS: tuple[str, ...] = (ARM_1, ARM_2, ARM_2S, ARM_3, ARM_4)

# --------------------------------------------------------------------------------------
# The verdicts. `CONTEXT.md` §9.3: "A verdict is a TYPE, not a boolean."
# --------------------------------------------------------------------------------------

ALLOWED = "ALLOWED"
DENIED = "DENIED"

#: §9.3, stolen outright with attribution: *"A declared obligation with no result becomes
#: `INDETERMINATE` **at construction**, and `INDETERMINATE` blocks exactly as hard as
#: `DENIED`. 'Checked and passed' must be distinguishable from 'never checked.'"*
INDETERMINATE = "INDETERMINATE"

VERDICTS: tuple[str, ...] = (ALLOWED, DENIED, INDETERMINATE)

#: §8.6a's sentence as a table. ⚠️ **Arm 1 is the strict one and it is the one that matters
#: most**: arm 1 is the no-gate floor *and* the probe-validity arm, so a `DENIED` appearing on
#: it would mean the calibration that sets the frozen void threshold ran against something
#: other than an open door.
VERDICTS_BY_ARM: Mapping[str, frozenset[str]] = MappingProxyType(
    {
        ARM_1: frozenset({ALLOWED}),
        ARM_2: frozenset({ALLOWED, DENIED}),
        ARM_2S: frozenset({ALLOWED, DENIED}),
        ARM_3: frozenset({ALLOWED, DENIED}),
        ARM_4: frozenset({ALLOWED, DENIED, INDETERMINATE}),
    }
)

#: What ``target`` holds when a call names no payment. Golden 5's and golden 3's
#: ``create_instant_settlement`` entries carry exactly this string.
NO_TARGET = "-"


class LedgerEntryError(ValueError):
    """An entry was offered that the specification cannot produce. **Always a refusal.**

    Hard rule 9's shape applied to a record rather than to a config value: the alternative is
    a ledger that accepts a verdict no arm emits, or a float on the money path, and then
    publishes a number derived from it. There is no lenient mode and no coercion.
    """


@dataclass(frozen=True)
class LedgerEntry:
    """One appended entry. **Frozen: a written entry is never mutated in place.**

    The field ORDER is golden 5's own key order, so :meth:`to_dict` writes a document that
    reads like the golden. The digest does not depend on it — canonical JSON sorts keys — but
    a reviewer diffing a stored ledger against the golden should not have to sort by eye.
    """

    ledger_seq: int
    turn_index: int
    arm: str
    verdict: str
    tool: str
    target: str
    amount_paise: int | None
    a_class: str | None
    rejected_by_razorpay: bool
    customer_overcharge_paise: int
    merchant_irrecoverable_outflow_paise: int
    merchant_float_moved_paise: int
    fees_incurred_paise: int
    prev_hash: str
    hash: str

    def __post_init__(self) -> None:
        """Validate on **every** construction path, including :meth:`from_dict`.

        Deliberately here rather than in :meth:`whetstone_gate.ledger.chain.Ledger.append`:
        a check that lives on one write path is a check a second write path does not have.
        """
        _validate(
            {name: getattr(self, name) for name in (*CONTENT_FIELDS, *CHAIN_FIELDS)},
            require_chain=True,
        )

    # -- the two views -----------------------------------------------------------------

    def body(self) -> dict[str, Any]:
        """The **content** fields — what the digest is taken over.

        ⚠️ ``prev_hash`` and ``hash`` are excluded, which is the golden's ``hash_rule``
        verbatim. Everything else is in, so a tampered field of any kind moves the digest.
        """
        return {name: getattr(self, name) for name in CONTENT_FIELDS}

    def to_dict(self) -> dict[str, Any]:
        """The whole entry, in golden 5's key order, as it is stored and replayed."""
        return {name: getattr(self, name) for name in (*CONTENT_FIELDS, *CHAIN_FIELDS)}

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "LedgerEntry":
        """Rebuild an entry from a stored document. **Refuses an unknown or missing key.**

        A silently-ignored extra key would be a field inside somebody's digest and outside
        this type, which is the one way a replay could disagree with the chain it replays.
        """
        expected = set(CONTENT_FIELDS) | set(CHAIN_FIELDS)
        supplied = set(raw)
        if supplied != expected:
            missing = sorted(expected - supplied)
            extra = sorted(supplied - expected)
            raise LedgerEntryError(
                f"a stored entry does not carry golden 5's field set: missing={missing}, "
                f"unexpected={extra}. The set is closed because every content field is inside "
                f"the digest (see this module's docstring)."
            )
        return cls(**{name: raw[name] for name in expected})


#: The thirteen hashed fields, derived from the dataclass so the two cannot drift.
CONTENT_FIELDS: tuple[str, ...] = tuple(
    f.name for f in fields(LedgerEntry) if f.name not in ("prev_hash", "hash")
)

#: The two chain fields, excluded from the digest by the golden's ``hash_rule``.
CHAIN_FIELDS: tuple[str, ...] = ("prev_hash", "hash")


def _is_int(value: Any) -> bool:
    """⚠️ ``bool`` is excluded deliberately. ``True`` **is** an ``int`` in Python and
    ``True == 1``, so a boolean amount would otherwise pass as one paise —
    :func:`whetstone_gate.world.money.is_integer_paise` draws the same line for the same
    reason, and RS-30 and RS-41 are Razorpay drawing it twice."""
    return isinstance(value, int) and not isinstance(value, bool)


def _validate(values: Mapping[str, Any], *, require_chain: bool) -> None:
    """Refuse anything the specification cannot have produced. Never coerces."""
    seq = values["ledger_seq"]
    if not _is_int(seq) or seq < 1:
        raise LedgerEntryError(f"ledger_seq must be an integer >= 1, got {seq!r}")

    turn = values["turn_index"]
    if not _is_int(turn) or turn < 0:
        raise LedgerEntryError(f"turn_index must be an integer >= 0, got {turn!r}")

    arm = values["arm"]
    if arm not in VERDICTS_BY_ARM:
        raise LedgerEntryError(
            f"arm {arm!r} is not one of the five CONTEXT.md §8 arms {list(ARMS)}"
        )

    verdict = values["verdict"]
    allowed = VERDICTS_BY_ARM[arm]
    if verdict not in allowed:
        raise LedgerEntryError(
            f"arm {arm!r} cannot emit verdict {verdict!r}. CONTEXT.md §8.6a gives it exactly "
            f"{sorted(allowed)} and no other. C7 builds no gate; it refuses a verdict the "
            f"specification does not give this arm."
        )

    tool = values["tool"]
    # ⚠️ ANY string, INCLUDING THE EMPTY ONE, and that is hard rule 11 rather than laxity.
    # `MockWorld.call("")` is a legal call: it is not one of the six names, so the world
    # answers "tool not enabled" and LOGS it with its arguments. Refusing to record it would
    # drop a call the attacker made out of the ledger CANARY-B reach is counted over — silent
    # denominator shrinkage, in the control that decides whether the run is publishable. A
    # non-`str` is still refused: that is a caller passing the wrong type, not an attacker
    # action, and no path from the tool surface can produce one.
    if not isinstance(tool, str):
        raise LedgerEntryError(f"tool must be a string, got {tool!r}")

    target = values["target"]
    if not isinstance(target, str) or not target:
        raise LedgerEntryError(f"target must be a non-empty string, got {target!r}")

    amount = values["amount_paise"]
    # ⚠️ NOT bounded below at zero. It records what the call ASKED FOR, and an attacker may ask
    # for a negative amount — RS-28 is the documented refusal. Clamping it, or refusing the
    # entry, would lose the attempt from the record and shrink a denominator (hard rule 11).
    if amount is not None and not _is_int(amount):
        raise LedgerEntryError(
            f"amount_paise must be an integer number of paise or None, got {amount!r}. "
            f"PROCESS.md §5.1: integer paise end to end, never a float, never a rupee decimal."
        )

    a_class = values["a_class"]
    if a_class is not None and a_class not in A_CLASSES:
        raise LedgerEntryError(
            f"a_class {a_class!r} is not one of CONTEXT.md §12.2's classes {list(A_CLASSES)}"
        )

    rejected = values["rejected_by_razorpay"]
    if not isinstance(rejected, bool):
        raise LedgerEntryError(
            f"rejected_by_razorpay must be a bool, got {rejected!r}. §12.2 defines it as "
            f"'a documented Razorpay error fired', which is a fact and not a count."
        )

    # ⚠️ THE FOUR ARE VALIDATED SEPARATELY AND ARE NEVER ADDED TOGETHER. §12.2's reporting
    # rule 1. There is no total() in this package and there must never be one.
    for component in COMPONENTS:
        value = values[component]
        if not _is_int(value) or value < 0:
            raise LedgerEntryError(
                f"{component} must be an integer >= 0 paise, got {value!r}"
            )

    if require_chain:
        for name in CHAIN_FIELDS:
            value = values[name]
            if not isinstance(value, str) or not value:
                raise LedgerEntryError(f"{name} must be a non-empty string, got {value!r}")


def validate_content(values: Mapping[str, Any]) -> None:
    """Validate the thirteen content fields of a proposed entry, before it is chained."""
    missing = [name for name in CONTENT_FIELDS if name not in values]
    if missing:
        raise LedgerEntryError(f"missing content field(s): {missing}")
    extra = [name for name in values if name not in CONTENT_FIELDS]
    if extra:
        raise LedgerEntryError(
            f"unexpected field(s) {extra}: golden 5 fixes the content set at "
            f"{list(CONTENT_FIELDS)} and every one of them is inside the digest."
        )
    _validate(values, require_chain=False)
