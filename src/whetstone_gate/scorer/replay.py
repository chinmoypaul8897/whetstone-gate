"""The scorer's own read model of a stored ledger, and the world state it opens against.

⚠️ **EVERY NAME IN THIS FILE IS WRITTEN A SECOND TIME ON PURPOSE.** `CLAUDE.md` hard rule 8:
*"`scorer/` imports nothing from `gates/`; `gates/` imports nothing from `scorer/`; neither
imports a shared predicate helper. Any logic they both need is written twice, on purpose — once
against the live call, once against the replayed ledger."* The tool names, the verdict string
and the field names below all exist elsewhere in this repository, and this package reaches for
none of them. **In the spike, `gate.js` and `invariants.js` both called `world.js:intentKey`, so
the invariant could not have fired unless the gate had a bug. That is not a result; it is a
definition.**

⚠️ **AND THE DUPLICATION IS NOT FREE, WHICH IS WHY IT IS NAMED HERE RATHER THAN CELEBRATED.**
A second copy of the tool surface can drift from the first, and nothing in this package would
notice. What makes the trade worth taking is that a drift produces a **disagreement** — a
predicate that stops firing where the world says it should — while a shared helper produces
**agreement by construction**, which is unfalsifiable. A test in ``tests/test_c8_scorer.py``
re-reads the surface from `CONTEXT.md` §8.6a's own prose and asserts this copy still matches
it, so drift is detected without either side importing the other.

⚠️ **`executed` IS READ, NEVER INFERRED** (`QUESTIONS.md` **Q-062**; `INCIDENTS.md` **INC-67**).
A null ``a_class`` does **not** imply a refusal — golden 3's seq 3 and seq 4 both carry a null
``a_class`` with ``rejected_by_razorpay`` false and golden 3 counts **both** executed and
**both** productive. The one place ``executed`` may come from is the ledger's own ``executed``
field, and :meth:`ReplayEntry.from_ledger_row` refuses a row that does not carry it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

# --------------------------------------------------------------------------------------
# The tool surface, written twice on purpose. CONTEXT.md §8.6a's five write/read tools.
# --------------------------------------------------------------------------------------

#: The refund tool. S1, S2, S2-amt and S4 all take their subject from rows carrying it.
REFUND_TOOL = "create_refund"

#: The capture tool. S3's subject.
CAPTURE_TOOL = "capture_payment"

#: The settlement sweep. It moves money — so E1, E2 and E3 see it — and no sequence
#: invariant does.
SETTLEMENT_TOOL = "create_instant_settlement"

#: Every tool that MOVES money, and therefore every tool E1, E2 and E3 are scored over.
#: The two read tools (``fetch_payment``, ``fetch_payments``) and the ``initiate_payment``
#: stub move nothing and are not here — but they ARE tool calls, so they still occupy a
#: ``ledger_seq`` and therefore still advance S4's in-flight window.
MONEY_TOOLS: frozenset[str] = frozenset({REFUND_TOOL, CAPTURE_TOOL, SETTLEMENT_TOOL})

#: The gate verdict that means the action was ISSUED — the gate let it be attempted.
#: `CONTEXT.md` §9.2's S2, as Q-027 redefined it, is scored at **issue**: *"an invariant
#: should measure WHAT THE GATE COULD HAVE PREVENTED, and the gate acts at issue, not at
#: execution."*
ALLOWED_VERDICT = "ALLOWED"

#: The fields :meth:`ReplayEntry.from_ledger_row` requires. Fewer than the fifteen the writer
#: emits, deliberately: a scorer that demanded the whole schema would refuse a ledger the
#: schema had legitimately widened, which is `INCIDENTS.md` INC-32's class.
REQUIRED_ROW_FIELDS: tuple[str, ...] = (
    "ledger_seq",
    "verdict",
    "tool",
    "target",
    "receipt",
    "amount_paise",
    "executed",
)


class ReplayError(ValueError):
    """A stored row cannot be read as a scoreable action. Always a refusal, never a guess."""


@dataclass(frozen=True)
class ReplayEntry:
    """One ledger row, as the scorer reads it.

    ``issued`` and ``executed`` are **separate facts** and the whole of `QUESTIONS.md` Q-027
    and Q-062 lives in the gap between them: golden 2's F6 seq 2 is ISSUED and NOT EXECUTED,
    and **S2 fires on it anyway**. A scorer that collapsed the two returns ``[]`` on F6 and
    passes every other fixture in the file.
    """

    ledger_seq: int
    tool: str
    target: str
    receipt: str | None
    amount_paise: int | None
    issued: bool
    executed: bool

    @property
    def is_refund(self) -> bool:
        return self.tool == REFUND_TOOL

    @property
    def is_capture(self) -> bool:
        return self.tool == CAPTURE_TOOL

    @property
    def moves_money(self) -> bool:
        return self.tool in MONEY_TOOLS


def entry_from_row(row: Mapping[str, Any]) -> ReplayEntry:
    """Read one stored ledger row. Refuses anything it would have to guess at.

    ``issued`` is derived from the row's own ``verdict`` — the gate ALLOWED it — and from
    nothing else. ``executed`` is **read**, and a row missing the field is a refusal rather
    than a ``False``: Q-062's ruling is that ``False`` is *a value with a meaning*, so
    defaulting it would record every executed action as one that never happened.
    """
    missing = [name for name in REQUIRED_ROW_FIELDS if name not in row]
    if missing:
        raise ReplayError(
            f"ledger row {row.get('ledger_seq', '?')!r} is missing field(s) {missing}. "
            f"`executed` in particular is READ and never inferred (Q-062, INC-67): a null "
            f"a_class does NOT imply a refusal, and defaulting the field would record every "
            f"executed action as one that never happened"
        )

    seq = row["ledger_seq"]
    if isinstance(seq, bool) or not isinstance(seq, int):
        raise ReplayError(f"ledger_seq {seq!r} is not an integer row number")

    executed = row["executed"]
    if not isinstance(executed, bool):
        raise ReplayError(
            f"row {seq}'s `executed` is {executed!r}, not a bool. It is the world's own "
            f"execution fact and there is nothing else to read it from"
        )

    amount = row["amount_paise"]
    if amount is not None and (isinstance(amount, bool) or not isinstance(amount, int)):
        raise ReplayError(
            f"row {seq}'s amount_paise is {amount!r}. PROCESS.md S5.1: integer paise end to "
            f"end - never a float, never a rupee decimal"
        )

    receipt = row["receipt"]
    if receipt is not None and not isinstance(receipt, str):
        raise ReplayError(f"row {seq}'s receipt is {receipt!r}, neither a string nor absent")

    target = row["target"]
    if not isinstance(target, str):
        raise ReplayError(f"row {seq}'s target is {target!r}, not a string")

    return ReplayEntry(
        ledger_seq=seq,
        tool=str(row["tool"]),
        target=target,
        receipt=receipt,
        amount_paise=amount,
        issued=row["verdict"] == ALLOWED_VERDICT,
        executed=executed,
    )


def entries_from_rows(rows: Iterable[Mapping[str, Any]]) -> tuple[ReplayEntry, ...]:
    """:func:`entry_from_row` over a document's rows, in the order they are stored."""
    return tuple(entry_from_row(row) for row in rows)


# --------------------------------------------------------------------------------------
# The opening state — what the world looked like BEFORE the first tool call.
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Authorization:
    """One authorization, as S3's three clauses need to see it.

    ``exists`` is carried explicitly rather than being implied by presence in the mapping,
    because golden 2's F7 states the clause that way and because *"the id is absent"* and
    *"the id is present and refers to nothing"* are two different facts a fixture may wish to
    separate.
    """

    exists: bool
    consumed: bool
    amount_paise: int


@dataclass(frozen=True)
class OpeningState:
    """The world's state before the episode's first call. **Data, not a world.**

    ⚠️ **THIS PACKAGE DOES NOT REGENERATE THE WORLD AND MUST NOT** — see this module's
    sibling :mod:`whetstone_gate.scorer.episode` and `QUESTIONS.md` **Q-071**. The caller
    regenerates the world from the episode's stored seed and hands the result in here as
    plain integers. `whetstone_gate.world` therefore stays out of `scorer/`'s import
    closure, which is what keeps `check_roles` **D3** able to say something.

    ``captured_paise`` is S1's denominator: the amount captured on each payment. Eight of
    seed 2001's twelve payments are ``captured`` **positionally, before the episode starts**
    (`CONTEXT.md` §8.6a), so no ``capture_payment`` call exists to carry it and no ledger
    field can. That is Q-071's whole subject.
    """

    captured_paise: Mapping[str, int] = field(default_factory=dict)
    authorizations: Mapping[str, Authorization] = field(default_factory=dict)
    payment_ids: frozenset[str] = frozenset()

    def known_payment_ids(self) -> frozenset[str]:
        """Every payment id this state knows about, from whichever field named it.

        ``payment_ids`` is the regenerated world's full roster and is what the seed
        cross-check compares against; the two money mappings are folded in so a fixture that
        supplies only balances is still usable.
        """
        return (
            frozenset(self.payment_ids)
            | frozenset(self.captured_paise)
            | frozenset(self.authorizations)
        )


def opening_state_from_payments(payments: Sequence[Mapping[str, Any]]) -> OpeningState:
    """Fold a regenerated world's payment records into an :class:`OpeningState`.

    ⚠️ **THE ARGUMENT IS A SEQUENCE OF PLAIN MAPPINGS AND NOT A WORLD OBJECT**, so the caller
    converts and this package still imports nothing first-party. Each mapping needs ``id``,
    ``status``, ``amount_captured_paise`` and ``amount_paise`` — the field names
    `CONTEXT.md` §8.6a gives them.

    A payment that is ``captured`` contributes its captured amount to S1's denominator. A
    payment that is ``authorized`` contributes an **unconsumed** authorization at its own
    amount, which is S3's subject.

    ⚠️ **EVERY PAYMENT'S CAPTURED AMOUNT IS RECORDED, INCLUDING THE ZEROS**, and that is a
    behaviour and not a formality. §8.6a's own table gives an ``authorized`` payment
    ``amount_captured_paise = 0``, so a refund against one is an over-refund **of a known
    balance** and S1 must fire on it. Dropping the zeros would leave that payment with **no
    known captured amount**, and a refund on it would be SKIPPED as unjudgeable rather than
    reported — an invariant silently under-counting exactly where `CONTEXT.md` §12.2's **A6**
    class lives. Golden 2's fixtures are unaffected: they build their opening state from the
    fixture's own ``world.captured`` map, which declares what it models and no more.
    """
    captured: dict[str, int] = {}
    authorizations: dict[str, Authorization] = {}
    ids: list[str] = []
    for payment in payments:
        identifier = str(payment["id"])
        ids.append(identifier)
        status = payment["status"]
        captured_amount = payment["amount_captured_paise"]
        if isinstance(captured_amount, bool) or not isinstance(captured_amount, int):
            raise ReplayError(
                f"payment {identifier}'s amount_captured_paise is {captured_amount!r}; "
                f"integer paise end to end (PROCESS.md S5.1)"
            )
        captured[identifier] = captured_amount
        if status == "authorized":
            authorizations[identifier] = Authorization(
                exists=True, consumed=False, amount_paise=int(payment["amount_paise"])
            )
    return OpeningState(
        captured_paise=captured,
        authorizations=authorizations,
        payment_ids=frozenset(ids),
    )
