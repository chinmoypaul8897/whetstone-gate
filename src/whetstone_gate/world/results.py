"""What a tool call returns, and the two ways it can be refused.

**Two refusals, and the difference is load-bearing rather than tidy.**

  * :class:`ToolRefusal` — **the MCP server's own**. An unknown tool (*"tool not enabled"*),
    the read-only stub, a parameter the tool declares ``Required`` and did not receive. The
    request **never reached Razorpay**, so no documented Razorpay error fired and **no harm
    record is written**: `CONTEXT.md` §12.2 writes a record for a *money action*, and a call
    the tool itself rejected never became one.
  * :class:`RazorpayRefusal` — **Razorpay's**, carrying the `RAZORPAY_SEMANTICS.md` row id
    that fired. A harm record **is** written, with ``rejected_by_razorpay=True`` and four
    zeros (`INCIDENTS.md` INC-03).

⚠️ **THE BOUNDARY BETWEEN THEM IS EXACTLY WHERE `rejected_by_razorpay` GETS ITS MEANING.**
§12.2 defines the field as *"a documented Razorpay error fired"* — not *"the call failed"* —
so folding the two refusals together would make the field mean something looser than the
specification says while every test still passed.

⚠️ **A `RazorpayRefusal` CARRIES AN ID, NEVER A MESSAGE.** The words come from the row that
id names, in `RAZORPAY_SEMANTICS.md`, through :class:`whetstone_gate.world.oracle.Oracle`.
**No Razorpay error string is written anywhere in this package**, so *"this project invented
no Razorpay error text"* is establishable by reading a diff.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .harm import HarmRecord


class ToolRefusal(Exception):
    """The MCP tool layer refused the call before any request reached Razorpay."""


class RazorpayRefusal(Exception):
    """Razorpay refused the call, per the `RAZORPAY_SEMANTICS.md` row named by :attr:`rs_id`."""

    def __init__(
        self,
        rs_id: str,
        quote_index: int = 0,
        detail: str = "",
        a_class: str | None = None,
    ) -> None:
        super().__init__(rs_id)
        self.rs_id = rs_id
        self.a_class = a_class
        """The `CONTEXT.md` §12.2 attack class the **attempt** belongs to, or ``None``.

        ⚠️ **The class survives the refusal; the harm does not.** Golden 3's ``ledger_seq`` 2
        is ``a_class`` ``A2`` with ``rejected_by_razorpay`` ``true`` and four zeros, and its
        ``ledger_seq`` 5 is ``A3`` the same way. Carrying the class on the refusal is what
        lets :mod:`whetstone_gate.world.harm` book it beside a zero — which is
        `QUESTIONS.md` Q-027's publishable gap, *"RAZORPAY'S OWN GUARD DOING WORK"*.
        """
        self.quote_index = quote_index
        """Which of the row's documented strings applies.

        ⚠️ **Several rows document more than one string for one condition and they are not
        interchangeable.** RS-32 carries four for *"capture on a non-`authorized` payment"*;
        RS-53 carries two with **different World labels**, so emitting its first would emit
        the `RECORDED` credential half in place of the `MUST-FIRE` extra-field half. The
        index selects; :class:`~whetstone_gate.world.oracle.Row` carries the ordered set.
        """
        self.detail = detail
        """This project's own words about *this* call — never presented as Razorpay's."""


@dataclass(frozen=True)
class ToolResult:
    """One tool call's outcome, as the caller sees it."""

    tool: str
    ok: bool
    """True only if the world executed the call. A refusal of either kind is False."""

    payload: dict = field(default_factory=dict)
    """What a read returned, or the entity a successful write created. Empty on refusal."""

    error: str = ""
    """The refusal text: Razorpay's own verbatim string, or the MCP layer's."""

    rs_id: str = ""
    """The `RAZORPAY_SEMANTICS.md` row that fired, or empty for a :class:`ToolRefusal`.

    ⚠️ **This is what the spend-free self-test counts, and it is why the count cannot be
    faked by a green test.** A row *"fires"* when a call to this world returned it here.
    """

    http: str = ""
    """The row's own declared HTTP field, verbatim from the oracle. Never a literal in source."""

    detail: str = ""
    """This project's commentary on the refusal, kept separate from Razorpay's words."""

    harm: HarmRecord | None = None
    """The typed harm record, for a money action. ``None`` for reads, the stub and
    :class:`ToolRefusal` — none of which is a money action (§12.2)."""
