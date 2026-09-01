"""**ONE LEDGER ENTRY. FOURTEEN CONTENT FIELDS SINCE `QUESTIONS.md` Q-062 WAS RULED.**

`tests/goldens/golden5_tamper.json` was hand-derived by the architect **before this package
existed**, and every one of its twelve entries carries exactly **fifteen** keys — the
**thirteen** content fields this schema had until 2026-09-01, plus ``prev_hash`` and ``hash``.
The chain fields are excluded from the digest, which the golden's own ``hash_rule`` states:

    entry_hash = SHA-256( prev_hash || canonical-JSON(entry, sorted keys, no whitespace) ),
    both as UTF-8 strings; the canonicalised entry EXCLUDES prev_hash and hash

---

## ⚠️ THE FOURTEENTH FIELD — `executed` — AND WHY IT LANDED

**`QUESTIONS.md` Q-062, RULED by the architect on 2026-09-01, verbatim:**

    Q-062 is RULED: the fourteenth content field LANDS. `executed`, boolean, non-null on every
    entry, positioned IMMEDIATELY AFTER `rejected_by_razorpay`. … A ledger in which an action
    that happened and an action that never happened are the same bytes is not a ledger.

    DEFINITION, and it is the ruling's operative half: `executed` is TRUE if and only if the
    world ACTUALLY PERFORMED the action against mock Razorpay state. It is therefore FALSE for
    all three refusal sources, which become jointly derivable for the first time:
        gate refused        -> executed false, verdict DENIED or INDETERMINATE
        Razorpay refused    -> executed false, rejected_by_razorpay true
        TOOL LAYER refused  -> executed false, verdict ALLOWED, rejected_by_razorpay false
                               <- the row that was previously indistinguishable from success

⚠️ **C7 BUILD 1 STOPPED HERE UNDER HARD RULE 1 AND DID NOT TAKE A DEFAULT, AND THAT IS WHY THIS
PARAGRAPH EXISTS RATHER THAN A SILENT FOURTEENTH KEY.** Its measurement is what decided the
ruling: two `capture_payment` entries on seed 2001, one that moved ₹665.23 and one the MCP tool
layer refused, **identical in all thirteen content fields and carrying the same digest**
`3c54446376764d88ea82c17ea56b31716ed1fdf1de9a77536f4ba55ab09cd16b`. Under this schema they
differ, and `tests/test_c7_ledger.py::test_an_EXECUTED_capture_and_an_MCP_LAYER_REFUSAL_NOW_DIFFER`
prints both digests beside build 1's identical pair.

⚠️ **GOLDEN 5 IS NOT REOPENED AND ITS ENTRIES STAY AT THIRTEEN.** `PROCESS.md` §5.2 specifies it
as a **tamper test — a verifier oracle** — and never as a writer oracle, and
:func:`whetstone_gate.ledger.chain.verify` **recomputes whatever each entry carries**, so all
four of its cases still reproduce with their first-bad seqs under the wider schema. What a
13-field golden-5 document can no longer do is come back through
:func:`whetstone_gate.ledger.store.from_document`, which builds **this type** — that is a typed,
Q-062-naming refusal rather than a tamper verdict, and the architect is authoring **golden 5B**
to re-pin the writer under this schema. See :data:`GOLDEN_5_CONTENT_FIELDS`.

**Where each field comes from, so a reviewer can check the set rather than trust it:**

  * ``ledger_seq``, ``tool``, ``a_class``, ``rejected_by_razorpay`` and the **four harm
    components** are `CONTEXT.md` §12.2's typed harm record, field for field.
  * ``turn_index``, ``arm`` and ``verdict`` are `PROCESS.md` §12.1's C7 row, which requires
    them by name *"so the §18 replay renderer is buildable from `evals/episodes/` alone"*.
  * ``executed`` is **`QUESTIONS.md` Q-062's ruling**, read from
    :attr:`whetstone_gate.world.results.ToolResult.ok` on the world's own log row — *"True
    only if the world executed the call. A refusal of either kind is False."* ⚠️ It is
    **never inferred** from ``verdict`` and ``rejected_by_razorpay``: that inference is the
    exact reasoning that produced the defect, because it cannot see the tool-layer refusal,
    which is the whole finding. See :func:`whetstone_gate.ledger.build.executed_of`.
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
    """This ledger's own dense 1-based row number.

    ⚠️ **`QUESTIONS.md` Q-054, RULED 2026-09-01: `ledger_seq` (the ledger's row) and C4's world
    write-counter are SEPARATE SPACES and NO CHUNK MAY JOIN THEM ON THAT KEY.**

    :class:`whetstone_gate.world.harm.HarmRecord` carries a field of the same name and the same
    type, numbered by a counter that advances only on **writes that reached Razorpay**. This
    ledger holds **one entry per call** — reads, the stub, unknown tools, MCP-layer refusals and
    calls the gate **denied**, none of which the world numbers. C7 BUILD 1 measured the
    divergence on its own fixture: **harm records [1, 2] against ledger entries [1, 2, 3]**.

    The two coincide exactly when every call in an episode is an executed write, which is true
    of golden 3 and of golden 5 case A — **so neither golden discriminates them**, and a join
    would succeed silently on a short episode and mis-attribute silently on a real one. The
    prohibition is written here, on the field, because that is where C8, C10, C17 and C18 will
    look. It is §12.2's reporting rule 3 — *"De-duplicate by `ledger_seq`"* — that makes this
    number load-bearing, and that rule is about **this** object.
    """

    turn_index: int
    arm: str
    verdict: str
    tool: str
    target: str
    amount_paise: int | None
    a_class: str | None
    rejected_by_razorpay: bool
    """§12.2: *"a documented Razorpay error fired"* — **not** *"the call failed"*.

    ⚠️ **It is written from a HARM RECORD, and a harm record exists only for a MONEY ACTION**, so
    a **read** that Razorpay refused (RS-44, RS-45, RS-52, RS-53) carries ``False`` here. See
    :func:`whetstone_gate.ledger.control.refusal_source`, which measures that and says so.
    """

    executed: bool
    """⚠️ **`QUESTIONS.md` Q-062, RULED 2026-09-01. TRUE if and only if the world ACTUALLY
    PERFORMED the action against mock Razorpay state.**

    Read from :attr:`whetstone_gate.world.results.ToolResult.ok` on the world's own log row —
    whose own docstring is *"True only if the world executed the call. A refusal of either kind
    is False."* — and **never inferred** from the two fields above it.

    ⚠️ **A SUCCESSFUL READ CARRIES ``True``, AND THAT IS STATED HERE BECAUSE THE RULING DOES NOT
    STATE IT.** ``fetch_payments`` and ``fetch_payment`` mutate nothing; the world still
    *performed* them, they are not one of the ruling's three refusal sources, and
    `CONTEXT.md` §8.6a's *"productive action"* says *"any tool call … that the world executed"* —
    **any tool call**, not *any money action*. So the count of ``executed`` entries is **not**
    the count of executed *writes*, and anything that wants the latter must also read ``tool``.
    :func:`whetstone_gate.ledger.control.productive_action` and
    `docs/reviews/OPEN_FINDINGS.md` carry the measured consequence.
    """

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
            hint = ""
            if missing == [EXECUTED] and not extra:
                # ⚠️ THE ONE MISMATCH THAT IS NOT TAMPERING AND MUST NOT READ LIKE IT.
                # Golden 5's twelve entries are PRE-Q-062 13-field rows. `verify` still
                # returns their four expected verdicts — it recomputes whatever each entry
                # carries — but they cannot become an entry of THIS type, and a reader who
                # is told only "does not carry the field set" would go looking for a tamper.
                hint = (
                    " ⚠️ The only field missing is 'executed', which is the schema this "
                    "package carried until QUESTIONS.md Q-062 was RULED on 2026-09-01. This "
                    "is a PRE-Q-062 document — tests/goldens/golden5_tamper.json is the one "
                    "in this repository — and it is NOT a tampered one: chain.verify still "
                    "returns its stored verdict, because verify recomputes whatever each "
                    "entry carries. Golden 5B re-pins the writer under this schema."
                )
            raise LedgerEntryError(
                f"a stored entry does not carry this package's field set: missing={missing}, "
                f"unexpected={extra}. The set is closed because every content field is inside "
                f"the digest (see this module's docstring).{hint}"
            )
        return cls(**{name: raw[name] for name in expected})


#: The fourteenth content field, named once so nothing spells it twice. `QUESTIONS.md` Q-062.
EXECUTED = "executed"

#: The fourteen hashed fields, derived from the dataclass so the two cannot drift.
CONTENT_FIELDS: tuple[str, ...] = tuple(
    f.name for f in fields(LedgerEntry) if f.name not in ("prev_hash", "hash")
)

#: The two chain fields, excluded from the digest by the golden's ``hash_rule``.
CHAIN_FIELDS: tuple[str, ...] = ("prev_hash", "hash")

#: ⚠️ **The THIRTEEN content fields golden 5's entries carry** — this schema minus ``executed``.
#:
#: Golden 5 is `PROCESS.md` §5.2's **tamper test**, hand-derived before this package existed and
#: **read-only** (hard rule 3). Q-062's ruling is explicit that it *"IS UNAFFECTED AND IS NOT
#: REOPENED"*: its entries stay at thirteen and a correct verifier must still verify them.
#: This constant exists so the test that pins the golden's key order can say **which** schema it
#: is pinning, instead of drifting whenever :data:`CONTENT_FIELDS` changes — a golden pinned
#: against a constant derived from the code under test pins nothing.
GOLDEN_5_CONTENT_FIELDS: tuple[str, ...] = tuple(
    name for name in CONTENT_FIELDS if name != EXECUTED
)


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

    executed = values[EXECUTED]
    if not isinstance(executed, bool):
        # ⚠️ NON-NULL ON EVERY ENTRY, in the ruling's own words, and `None` is refused here
        # rather than treated as "unknown". A tri-state would reintroduce exactly the
        # ambiguity Q-062 exists to remove: a reader would have to guess what an unknown
        # meant, and the guess available to them is the discredited inference from
        # `verdict` and `rejected_by_razorpay`.
        raise LedgerEntryError(
            f"executed must be a bool, got {executed!r}. QUESTIONS.md Q-062 (RULED "
            f"2026-09-01): 'boolean, non-null on every entry'. It is read from the world's "
            f"ToolResult.ok and is never inferred."
        )

    # ⚠️ THE FOUR ARE VALIDATED SEPARATELY AND ARE NEVER ADDED TOGETHER. §12.2's reporting
    # rule 1. There is no total() in this package and there must never be one.
    for component in COMPONENTS:
        value = values[component]
        if not _is_int(value) or value < 0:
            raise LedgerEntryError(
                f"{component} must be an integer >= 0 paise, got {value!r}"
            )

    _validate_executed_consistency(values)

    if require_chain:
        for name in CHAIN_FIELDS:
            value = values[name]
            if not isinstance(value, str) or not value:
                raise LedgerEntryError(f"{name} must be a non-empty string, got {value!r}")


def _validate_executed_consistency(values: Mapping[str, Any]) -> None:
    """⚠️ **THREE OF `QUESTIONS.md` Q-062's FOUR CONSISTENCY ASSERTIONS, ENFORCED AT WRITE.**

    The fourth is not a constraint but a **classification** — ``executed`` false with
    ``verdict`` ``ALLOWED`` and ``rejected_by_razorpay`` false is the row the tool layer
    refused — and it lives in :func:`whetstone_gate.ledger.control.refusal_source`.

    ⚠️ **THEY ARE ENFORCED AND NOT MERELY ASSERTED IN A TEST, AND THE REASON IS THE THIRD ONE.**
    A test says *"the entries we happened to build satisfy this"*; a refusal says *"an entry
    that does not cannot be written"*. Q-062's whole finding is that the ledger accepted two
    different histories as the same bytes, and a rule that is only a test is a rule the next
    write path does not have — which is `INCIDENTS.md` **INC-32**'s shape exactly.

    **1. ``executed`` ⇒ ``verdict`` is ``ALLOWED``.** A call the gate refused never reached the
    world, so the world cannot have performed it. `CONTEXT.md` §9.3: *"`INDETERMINATE` blocks
    exactly as hard as `DENIED`"*, so both are refusals here.

    **2. ``executed`` ⇒ ``rejected_by_razorpay`` is ``False``.** Structural in the world and
    checked here anyway: every ``harm.rejected(...)`` construction sits inside an
    ``except RazorpayRefusal`` branch whose only exit is ``_refused``, which hardcodes
    ``ok=False``; every ``ok=True`` site passes ``rejected=False`` as a literal.

    **3. ⚠️ ANY NON-ZERO HARM COMPONENT ⇒ ``executed``. MONEY CANNOT MOVE ON A CALL THAT DID NOT
    HAPPEN.** This is the one that is an **integrity check** rather than a restatement of the
    ruling's table, and it is the one that would have caught the original defect **from the
    other side**: it constrains the four numbers §12.2 publishes against the field that says
    whether the action occurred, so a ledger cannot carry harm attributed to a call the world
    never made. In the world it holds because :func:`whetstone_gate.world.harm._record` zeroes
    all four components whenever ``rejected`` — *"THIS `if` IS INC-03, IN ONE PLACE"* — and
    because a harm record with a non-zero component is only ever produced on a success path.
    **Here it holds because an entry that violates it is not writable.**
    """
    executed = values[EXECUTED]
    verdict = values["verdict"]
    rejected = values["rejected_by_razorpay"]

    if executed and verdict != ALLOWED:
        raise LedgerEntryError(
            f"executed=True with verdict={verdict!r}: a call the gate refused never reached "
            f"the world, so the world cannot have performed it. QUESTIONS.md Q-062: "
            f"'gate refused -> executed false, verdict DENIED or INDETERMINATE'."
        )

    if executed and rejected:
        raise LedgerEntryError(
            "executed=True with rejected_by_razorpay=True: QUESTIONS.md Q-062 gives "
            "'Razorpay refused -> executed false, rejected_by_razorpay true'. A documented "
            "Razorpay error fired means the world did not perform the action."
        )

    if not executed:
        moved = [c for c in COMPONENTS if values[c] != 0]
        if moved:
            raise LedgerEntryError(
                f"executed=False with non-zero harm {sorted(moved)}: money cannot move on a "
                f"call that did not happen. CONTEXT.md §12.2 zeroes all four components for "
                f"an action the world did not perform, and this entry claims otherwise."
            )


def validate_content(values: Mapping[str, Any]) -> None:
    """Validate the fourteen content fields of a proposed entry, before it is chained."""
    missing = [name for name in CONTENT_FIELDS if name not in values]
    if missing:
        raise LedgerEntryError(f"missing content field(s): {missing}")
    extra = [name for name in values if name not in CONTENT_FIELDS]
    if extra:
        raise LedgerEntryError(
            f"unexpected field(s) {extra}: the content set is "
            f"{list(CONTENT_FIELDS)} and every one of them is inside the digest."
        )
    _validate(values, require_chain=False)
