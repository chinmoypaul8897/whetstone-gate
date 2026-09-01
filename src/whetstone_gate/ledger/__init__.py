"""`whetstone_gate.ledger` — **the append-only, hash-chained substrate every number reads.**

`CONTEXT.md` §12.2 opens with the reason this package exists before any other:

    ⚠️ **This must be defined BEFORE the first commit, because the ledger is hash-chained and
    cannot be back-filled.**

The scorer (C8) replays it; the probe (C10) counts CANARY-B over it; the §18 renderer (C17)
draws the RACE beat from `evals/episodes/` **alone**, with no network call and no model; and
`make eval`'s claim — hard rule 10's *"every number regenerates from the stored ledgers"* — is
a claim about this structure. **A field omitted here is a number no later chunk can recover, on
any day, by any means.**

---

## THE FOUR THINGS THIS PACKAGE IS

1. **A chain.** ``entry_hash = SHA-256( prev_hash ‖ canonical-JSON(entry, sorted keys, no
   whitespace) )`` (`CONTEXT.md` §16), rooted at a genesis hash **loaded from `config/` with no
   default** and re-read on every use, because C14 changes it to the `prereg-v1` tag object id
   and that change is what makes a pre-freeze episode cryptographically distinguishable from a
   scored one. :mod:`whetstone_gate.ledger.chain`.
2. **A verifier that recomputes.** It rebuilds each entry's digest from that entry's own
   contents; it does not compare stored ``prev_hash`` against stored ``hash``.
   `PROCESS.md` §5.2's golden 5 is the oracle and its cases **C** and **D** are exactly the
   mutation a stored-field verifier cannot see. :mod:`whetstone_gate.ledger.chain`.
3. **A closed entry schema** — **fourteen** content fields since `QUESTIONS.md` **Q-062** was
   RULED on 2026-09-01, all inside the digest, plus ``prev_hash`` and ``hash``.
   :mod:`whetstone_gate.ledger.entry`.
4. **A builder that reads `MockWorld.log`, never `harm_records`** — `REVIEW_C4_1.md` INFO-2, and
   the reason is a measured undercount of the denominator the void threshold is calibrated on.
   :mod:`whetstone_gate.ledger.build`.

Plus one shell, :mod:`whetstone_gate.ledger.store`, which is the only module here that opens a
file, and one derivation, :mod:`whetstone_gate.ledger.control`.

---

## ⚠️ THE FOURTEENTH FIELD, AND WHAT IT MADE COMPUTABLE

**`QUESTIONS.md` Q-062, RULED 2026-09-01:** ``executed`` — *"boolean, non-null on every entry,
positioned IMMEDIATELY AFTER `rejected_by_razorpay`"* — is **TRUE if and only if the world
ACTUALLY PERFORMED the action against mock Razorpay state**, read from the world's own
:attr:`~whetstone_gate.world.results.ToolResult.ok` and **never inferred**.

C7 BUILD 1 stopped on its absence under hard rule 1 and measured why: a ``capture_payment`` that
moved ₹665.23 and one the MCP tool layer refused were **identical in all thirteen content fields
and carried the same digest**. *A ledger in which an action that happened and an action that
never happened are the same bytes is not a ledger.* What the field makes computable:

  * `CONTEXT.md` §8.6a's **productive action** — §8's mandatory confound control and §12.1's own
    column — :func:`whetstone_gate.ledger.control.productive_action`;
  * **E1, E2, E3**, which are about money **moved**, and **S3**, which needs to know whether a
    capture consumed the authorization. Those are **C8's** to score; C7 carries the field.
  * the **three refusal sources**, jointly derivable for the first time —
    :func:`whetstone_gate.ledger.control.refusal_source`, which also names the one shape that
    decomposition cannot separate.

⚠️ **Golden 5 is NOT reopened and its entries stay at thirteen.** It is `PROCESS.md` §5.2's
**tamper test — a verifier oracle** — and :func:`whetstone_gate.ledger.chain.verify` recomputes
whatever each entry carries, so all four of its cases reproduce with their first-bad seqs. What a
13-field document can no longer do is come back through
:func:`whetstone_gate.ledger.store.from_document`; that is a typed schema refusal, not a tamper
verdict, and **golden 5B** re-pins the writer under this schema.

---

## ⚠️ ``ledger_seq`` IS THIS LEDGER'S OWN POSITION, AND IT IS NOT THE WORLD'S WRITE COUNTER

`CONTEXT.md` §12.2 defines ``ledger_seq`` on the harm record as the *"de-duplication key: one
ledger entry may breach several invariants"* — that is, **it names a ledger entry**.
:class:`whetstone_gate.world.semantics.MockWorld` numbers its harm records with a counter that
advances only on **writes that reached Razorpay**, which is the right number for the world to
know and **is not an entry number**: this ledger holds one entry per *call*, plus entries for
calls the gate **denied**, which never reach the world at all and therefore cannot be numbered
by it. The two sequences coincide exactly when every call in an episode is an executed write —
which is true of golden 3 and golden 5 case A, and is why neither golden discriminates them.

So ``ledger_seq`` here is the dense 1-based position in **this** ledger, assigned by
:meth:`~whetstone_gate.ledger.chain.Ledger.append` and never supplied by a caller. It is unique
per entry, which is what §12.2's reporting rule 3 needs — *"De-duplicate by `ledger_seq`"*, the
rule that took a spike figure from ₹42,93,534 to ₹24,69,796.

⚠️ **`QUESTIONS.md` Q-054, RULED by the architect on 2026-09-01, verbatim:**

    Q-054 RULED: `ledger_seq` (the ledger's row) and C4's world write-counter are SEPARATE
    SPACES and NO CHUNK MAY JOIN THEM ON THAT KEY. Build 1 measured the divergence — harm
    records [1,2] against ledger entries [1,2,3]. Write the prohibition as a docstring on the
    field.

**It is on the field**, at :attr:`whetstone_gate.ledger.entry.LedgerEntry.ledger_seq`, because
that is where C8, C10, C17 and C18 will look. A join would succeed silently on a short episode
and mis-attribute silently on a real one, which is why the prohibition is absolute rather than
a caution.

## WHAT THIS PACKAGE DOES NOT DO

**It builds no gate.** ``verdict`` is C9's, and this package carries the field, refuses a value
`CONTEXT.md` §8.6a does not give the arm, and stops there. **It scores nothing** — E1–E3, S1,
S2, S2-amt, S3 and S4 are C8's, at replay. **It sums nothing**: §12.2's reporting rule 1 is
*"The four components are reported SEPARATELY and are NEVER summed"*, there is no ``total()``
in this package, and `tests/test_c7_ledger.py` walks the AST to keep it that way.
"""

from __future__ import annotations

from .build import (
    append_call,
    append_log,
    content_from_call,
    entries_naming,
    executed_of,
    harm_fields,
    amount_of,
    target_of,
)
from .chain import (
    APPEND_FIELDS,
    DETECTED,
    VALID,
    ChainConfigError,
    ChainError,
    ChainSpec,
    ChainVerdict,
    Ledger,
    NotCanonicalisable,
    canonical_json,
    entry_digest,
    load_chain_spec,
    rebuild,
    verify,
    verify_ledger,
)
from .control import (
    EXECUTED_NOT_REFUSED,
    GATE_REFUSED,
    RAZORPAY_REFUSED,
    REFUSAL_SOURCES,
    TOOL_LAYER_REFUSED,
    moved_money,
    productive_action,
    productive_actions,
    refusal_source,
)
from .entry import (
    ALLOWED,
    ARM_1,
    ARM_2,
    ARM_2S,
    ARM_3,
    ARM_4,
    ARMS,
    CHAIN_FIELDS,
    CONTENT_FIELDS,
    DENIED,
    EXECUTED,
    GOLDEN_5_CONTENT_FIELDS,
    INDETERMINATE,
    NO_TARGET,
    VERDICTS,
    VERDICTS_BY_ARM,
    LedgerEntry,
    LedgerEntryError,
    validate_content,
)
from .store import (
    DOCUMENT_KEYS,
    LEDGER_KEY,
    LedgerStoreError,
    from_document,
    read,
    read_document,
    render,
    stored_entries,
    to_document,
    write,
)

__all__ = [
    "ALLOWED",
    "APPEND_FIELDS",
    "ARMS",
    "ARM_1",
    "ARM_2",
    "ARM_2S",
    "ARM_3",
    "ARM_4",
    "CHAIN_FIELDS",
    "CONTENT_FIELDS",
    "ChainConfigError",
    "ChainError",
    "ChainSpec",
    "ChainVerdict",
    "DENIED",
    "DETECTED",
    "DOCUMENT_KEYS",
    "EXECUTED",
    "EXECUTED_NOT_REFUSED",
    "GATE_REFUSED",
    "GOLDEN_5_CONTENT_FIELDS",
    "INDETERMINATE",
    "LEDGER_KEY",
    "Ledger",
    "LedgerEntry",
    "LedgerEntryError",
    "LedgerStoreError",
    "NO_TARGET",
    "NotCanonicalisable",
    "RAZORPAY_REFUSED",
    "REFUSAL_SOURCES",
    "TOOL_LAYER_REFUSED",
    "VALID",
    "VERDICTS",
    "VERDICTS_BY_ARM",
    "amount_of",
    "append_call",
    "append_log",
    "canonical_json",
    "content_from_call",
    "entries_naming",
    "entry_digest",
    "executed_of",
    "from_document",
    "harm_fields",
    "load_chain_spec",
    "moved_money",
    "productive_action",
    "productive_actions",
    "read",
    "read_document",
    "rebuild",
    "refusal_source",
    "render",
    "stored_entries",
    "target_of",
    "to_document",
    "validate_content",
    "verify",
    "verify_ledger",
    "write",
]
