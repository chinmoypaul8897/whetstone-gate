"""**THE HASH CHAIN, AND THE VERIFIER THAT RECOMPUTES RATHER THAN COMPARES.**

`CONTEXT.md` §16, verbatim:

    `src/ledger/` computes ``entry_hash = SHA-256(prev_hash ‖ canonical-JSON(entry, sorted
    keys, no whitespace))``.

`tests/goldens/golden5_tamper.json`'s ``hash_rule`` closes the two ambiguities that sentence
leaves — **both operands are UTF-8 strings, concatenated**, and **the canonicalised entry
EXCLUDES ``prev_hash`` and ``hash``** — and its four cases are this module's oracle. The rule
is implemented from §16's sentence and *then* checked against the golden, which is the order
`PROCESS.md` §5.2 requires: a rule read off its own test is not a rule.

---

## ⚠️ THE VERIFIER RECOMPUTES EACH ENTRY'S DIGEST FROM ITS CONTENTS

It does **not** compare an entry's stored ``prev_hash`` against the previous entry's stored
``hash`` field and stop there. `PROCESS.md` §5.2's golden 5 names the mutation that
distinguishes the two:

    an entry whose stored ``prev_hash`` still matches the previous entry's stored ``hash``
    field while that previous entry's *contents* have been altered. A verifier that compares
    stored fields instead of recomputing the previous entry's digest passes this and must not.

**That is golden 5's case D, and case C is the same defect one entry along.** Golden 5 also
ships **case B, the CONTROL** — the link broken outright — which both a correct verifier and
a stored-field one detect. Without B, a verifier that always returned ``DETECTED`` would score
three out of three on A's absence and be indistinguishable from a working one. Every case
carries the defective verifier's answer in its own ``stored_field_verifier_returns`` field,
and ``tests/test_c7_ledger.py`` implements that defective verifier and shows it returning
``VALID`` on C and D — so *"this verifier is not the broken one"* is a measurement rather than
a claim about the code's intent.

---

## THE GENESIS ROOT IS LOADED, NEVER HARDCODED AND NEVER CACHED AT IMPORT

Hard rule 9: *a missing required value is a hard refusal, never a silent fallback.*
:func:`load_chain_spec` reads ``ledger.genesis_hash`` through the one loader and raises when it
is absent — there is no default to fall back to, because
:meth:`whetstone_gate.config.Config.require` has none to give.

⚠️ **AND IT IS RE-READ ON EVERY CALL, WHICH IS THE POINT RATHER THAN AN OVERSIGHT.**
`config/protocol.yaml`'s own comment says why:

    Before the freeze this is the literal "PRE-FREEZE"; from `probe-v1` it is that tag's
    object id; at `prereg-v1` C14 sets it to the prereg-v1 TAG OBJECT ID and every scored
    episode chains from it. A ledger cannot contain the hash of a tag that did not exist when
    it was written, so pre-freeze episodes are CRYPTOGRAPHICALLY DISTINGUISHABLE from scored
    ones. This is the one free proof available and it costs a single line.

A value captured into a module-level constant at import would survive C14's edit inside any
long-running process, and the episodes written afterwards would chain from a root the freeze
does not name — which is precisely the distinction the binding exists to make. So there is no
module-level genesis constant here, and a test asserts that changing ``config/`` between two
calls changes what the second one returns.

---

## ⚠️ WHAT THIS CHAIN DOES NOT DETECT, STATED BEFORE ANYBODY CLAIMS OTHERWISE

**A hash chain anchors its START. Nothing here anchors its END.** What :func:`verify` detects is
a **STALE DIGEST** — an entry whose stored ``hash`` no longer matches its contents, or whose
stored ``prev_hash`` no longer matches where the chain has reached. Every mutation that leaves
such a digest behind is caught, which is all four of golden 5's cases and every alteration,
insertion or deletion **in the middle** of a chain.

⚠️ **What is NOT caught is any edit that leaves NO stale digest, and there are exactly two
shapes of it.** Both are the same fact — *nothing commits to the end of the chain* — and this
paragraph states them rather than letting the stronger sentence stand:

  1. **Truncation.** Dropping entries from the tail leaves a shorter chain that is internally
     perfect, and :func:`verify` returns ``VALID`` — correctly, because every entry still
     present really does hash to its stored digest from the root the document names.
  2. **A RE-DERIVED SUFFIX.** Altering entry *k* and then recomputing the digests of *k*
     onward produces a chain that also verifies. ⚠️ **So "any alteration is detected" would be
     FALSE and is not claimed here**: what is detected is an alteration that is not followed
     through, which is what a careless edit looks like and is not what a determined one does.

`tests/test_c7_ledger.py::test_a_truncated_tail_is_NOT_detected_and_that_is_a_stated_limitation`
and `…::test_a_re_derived_suffix_is_NOT_detected_and_that_is_the_same_limitation` assert both
shapes rather than hiding them, and they are recorded in `docs/reviews/OPEN_FINDINGS.md`.
**The remedy is not cryptographic and is not this chunk's**: it is an external commitment to
each episode's head hash and entry count — the same mechanism `PROCESS.md` §6a already builds
for `config/`, where the answer to *"a git timestamp is forgeable"* was **witness it outside
this repository**, not a better hash. Until something publishes those where the operator cannot
quietly revise them, *"the ledger is tamper-evident"* means **evident against an edit that
leaves a stale digest, and against nothing else** — and the README must not say more.

⚠️ **What the chain DOES buy, stated so the limitation is not read as "it buys nothing":** the
genesis binding means a pre-freeze episode cannot be presented as a scored one without
re-deriving **every** digest in it, and the four render fields and four harm components are
inside those digests. The bar is not "impossible"; it is "no longer a text edit".
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from .. import config as cfg
from .entry import (
    ARMS,
    CHAIN_FIELDS,
    CONTENT_FIELDS,
    WIDENED_FIELDS,
    VERDICTS_BY_ARM,
    LedgerEntry,
    LedgerEntryError,
    validate_content,
)

#: The one content key :func:`verify` needs, because a verdict has to name a row.
LEDGER_SEQ = "ledger_seq"

#: The verifier's two verdicts. Golden 5's own words, in its ``expected_verdict`` field.
VALID = "VALID"
DETECTED = "DETECTED"


class ChainError(RuntimeError):
    """Base: the chain cannot be built or read as specified. Always a refusal."""


class ChainConfigError(ChainError):
    """``config/`` does not describe a hash chain this module can compute."""


class NotCanonicalisable(ChainError):
    """A value reached the digest that canonical JSON cannot represent deterministically."""


class TamperDetected(ChainError):
    """A stored chain did not verify. Carries the :class:`ChainVerdict` that says where.

    ⚠️ **This exists because a rebuild that silently re-chains is worse than no rebuild at
    all.** `INCIDENTS.md` **INC-33**: the read path used to re-append stored rows through
    :meth:`Ledger.append`, which recomputes every digest — so it returned a **self-consistent**
    ledger for a **tampered** document, and `verify_ledger` on the result could not fail. The
    read path now verifies the stored bytes first and raises this instead.
    """

    def __init__(self, verdict: "ChainVerdict") -> None:
        super().__init__(
            f"the stored chain does not verify at ledger_seq "
            f"{verdict.first_bad_ledger_seq}: {verdict.reason}"
        )
        self.verdict = verdict


@dataclass(frozen=True)
class ChainSpec:
    """What ``config/protocol.yaml``'s ``ledger:`` block says, resolved. **Data, not state.**"""

    genesis_hash: str
    """The root every entry ultimately chains from. ``PRE-FREEZE`` today; the ``prereg-v1``
    tag object id from C14 onward. **Never written into source.**"""

    algorithm: str
    """``ledger.hash_algorithm``. Passed to :func:`hashlib.new`, never spelled here."""


def load_chain_spec(protocol: cfg.Config | None = None) -> ChainSpec:
    """Resolve the ledger's genesis root and hash algorithm from ``config/``.

    Raises :class:`whetstone_gate.config.MissingRequiredValue` when ``ledger.genesis_hash`` is
    absent — hard rule 9, and there is deliberately no ``except`` around it that would turn the
    refusal into a default.
    """
    protocol = cfg.load("protocol") if protocol is None else protocol
    genesis = protocol.require("ledger.genesis_hash")
    algorithm = protocol.require("ledger.hash_algorithm")
    if not isinstance(genesis, str) or not genesis.strip():
        raise ChainConfigError(
            f"ledger.genesis_hash resolved to {genesis!r}, which is not a root a ledger can "
            f"chain from. Hard rule 9: supply it, or declare it as a TODO_ sentinel."
        )
    if not isinstance(algorithm, str) or not algorithm.strip():
        raise ChainConfigError(f"ledger.hash_algorithm resolved to {algorithm!r}")
    try:
        hashlib.new(algorithm)
    except ValueError as exc:
        raise ChainConfigError(
            f"ledger.hash_algorithm={algorithm!r} is not available to hashlib on this "
            f"interpreter ({exc}). A ledger is not written under a substituted algorithm."
        ) from exc
    return ChainSpec(genesis_hash=genesis, algorithm=algorithm)


# --------------------------------------------------------------------------------------
# Canonicalisation and the digest.
# --------------------------------------------------------------------------------------


def canonical_json(body: Mapping[str, Any]) -> str:
    """``canonical-JSON(entry, sorted keys, no whitespace)`` — §16's phrase, exactly.

    ``sort_keys=True`` is *sorted keys*; ``separators=(",", ":")`` is *no whitespace*.

    ⚠️ **``ensure_ascii=False``, AND IT IS NOW A RULING RATHER THAN A CLASS B CHOICE.**
    `QUESTIONS.md` **Q-053, RULED CONFIRMED by the architect on 2026-09-01**, verbatim:

        Q-053 RULED CONFIRMED: `ensure_ascii=False`. UTF-8, per S16, golden 5's hash_rule and
        RFC 8785. C7's derivation was correct; it is now a ruling rather than a Class B choice.

    The derivation the ruling confirms: §16 and golden 5's ``hash_rule`` both say the operands
    are **UTF-8 strings**, and escaping a non-ASCII character to ``\\uXXXX`` would be to hash a
    re-encoding of the entry rather than the entry. **Golden 5 cannot discriminate the two** —
    every byte of it is ASCII, on which they agree exactly — so the ruling settles what no
    fixture could, and **no digest moves**, which is the whole content of *confirmed*. It is not
    academic: the one field that can carry attacker-authored text is ``target``, and an attacker
    may call ``fetch_payment`` with any string it likes as ``payment_id``, so the two readings
    differ on **reachable input** and a reviewer re-verifying a published ledger with their own
    JSON writer is exactly the audience `PROCESS.md` §6a.3 is written for.

    ⚠️ **A float is refused rather than serialised, at ANY depth.** ``json`` writes
    ``repr``-shaped floats, so a binary float in an entry would put a platform-dependent string
    inside a digest that is supposed to be identical everywhere — and `PROCESS.md` §5.1 forbids
    one on the money path in the first place. The scan **recurses into lists and mappings**: a
    top-level-only check would have let a float inside a container through while a test named
    *"a float anywhere in an entry"* passed, which is a claim larger than its check.
    ``allow_nan=False`` is kept as the second door, for the three values that have no JSON
    spelling at all.
    """
    _refuse_floats(body, path="entry")
    return json.dumps(
        dict(body),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _refuse_floats(value: Any, *, path: str) -> None:
    """Walk ``value`` and refuse the first binary float, naming where it was found."""
    if isinstance(value, float):
        raise NotCanonicalisable(
            f"{path} = {value!r} is a binary float. PROCESS.md §5.1: money is integer paise "
            f"end to end, and a float's JSON spelling is not portable enough to hash."
        )
    if isinstance(value, Mapping):
        for key, child in value.items():
            _refuse_floats(child, path=f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _refuse_floats(child, path=f"{path}[{index}]")


def entry_digest(prev_hash: str, body: Mapping[str, Any], *, algorithm: str) -> str:
    """``SHA-256( prev_hash ‖ canonical-JSON(body) )``, both operands UTF-8 strings.

    The concatenation is of the **strings**, then encoded once — which is what golden 5's
    ``hash_rule`` says and what reproduces its twelve digests.

    ⚠️ **Text that is not encodable as UTF-8 is a typed refusal, not a traceback.** ``target``
    carries an attacker-authored ``payment_id``, and a JSON decoder will hand back a **lone
    surrogate** for ``"\\ud800"`` — which ``str.encode("utf-8")`` raises ``UnicodeEncodeError``
    on. An untyped error there would take down the episode *and* the verifier reading it, and
    would look like a crash rather than a finding. It is refused with the reason instead, so
    hard rule 11's *"every dropped episode is counted, categorised"* has something to count.
    """
    digest = hashlib.new(algorithm)
    try:
        payload = (prev_hash + canonical_json(body)).encode("utf-8")
    except UnicodeEncodeError as exc:
        raise NotCanonicalisable(
            f"an entry carries text that is not encodable as UTF-8 ({exc}). The hash rule's "
            f"operands are UTF-8 strings; a lone surrogate is not one, and it is refused here "
            f"rather than escaping as an untyped error."
        ) from exc
    digest.update(payload)
    return digest.hexdigest()


# --------------------------------------------------------------------------------------
# The ledger itself. APPEND-ONLY IN THE API, not merely by convention.
# --------------------------------------------------------------------------------------


class Ledger:
    """An append-only, hash-chained sequence of entries.

    ⚠️ **THE API HAS ONE WRITE PATH AND NO OTHERS.** :meth:`append` is the whole of it. There
    is no ``update``, no ``delete``, no ``insert``, no ``__setitem__``, no ``pop``, no
    ``clear`` and no way to reach the private list through a returned object:
    :attr:`entries` hands back a ``tuple`` of **frozen** dataclasses, so a caller who mutates
    what they were given mutates a copy of nothing.

    *Why the API and not a convention:* `CONTEXT.md` §9.2's S4 — the project's only remaining
    moat — is *"a violation established by the ledger where every live read the gate could have
    made returned a compliant value."* The whole claim rests on the ledger being the one thing
    in the run that cannot be quietly revised, and a comment saying so is not a mechanism.

    ⚠️ **THE ARM IS THE LEDGER'S, NOT THE APPEND CALL'S, SO A MIXED-ARM EPISODE IS UNBUILDABLE
    RATHER THAN MERELY WRONG.** `CONTEXT.md` §8: *"Same attacker, same seeds, same world, same
    turn budget. The only variable is the gate."* One episode is one arm, every §12 number is
    reported per arm, and §18's RACE beat draws five bars from **five** ledgers on one seed. An
    entry stamped with a different arm from the one the episode ran under would move an escape
    rate, a CANARY-B reach and the ARM CONFOUNDED comparison at once, and nothing downstream
    could see it. Recorded as a **Class B** deviation: golden 5 carries ``arm`` on the entry,
    which this does too — it is only the *source* of the value that is fixed here.
    """

    def __init__(self, *, spec: ChainSpec, seed: int, arm: str) -> None:
        if arm not in VERDICTS_BY_ARM:
            raise ChainConfigError(
                f"arm {arm!r} is not one of the five CONTEXT.md §8 arms {list(ARMS)}"
            )
        self._spec = spec
        self._seed = seed
        self._arm = arm
        self._entries: list[LedgerEntry] = []
        self._head = spec.genesis_hash

    # -- what a caller can observe ------------------------------------------------------

    @property
    def seed(self) -> int:
        """The episode's seed. Carried so a stored ledger names the world it was written in."""
        return self._seed

    @property
    def arm(self) -> str:
        """The arm every entry in this ledger carries. Fixed at construction."""
        return self._arm

    @property
    def genesis_hash(self) -> str:
        """The root this ledger chained from — ``PRE-FREEZE``, or a tag object id after C14."""
        return self._spec.genesis_hash

    @property
    def algorithm(self) -> str:
        return self._spec.algorithm

    @property
    def entries(self) -> tuple[LedgerEntry, ...]:
        """Every entry, in order. A ``tuple`` of frozen records: read-only all the way down."""
        return tuple(self._entries)

    @property
    def head_hash(self) -> str:
        """The digest the next entry will chain from. The genesis root while empty."""
        return self._head

    def __len__(self) -> int:
        return len(self._entries)

    # -- the one write path ------------------------------------------------------------

    def append(
        self,
        *,
        turn_index: int,
        verdict: str,
        tool: str,
        target: str,
        receipt: str | None,
        amount_paise: int | None,
        a_class: str | None,
        rejected_by_razorpay: bool,
        executed: bool,
        customer_overcharge_paise: int,
        merchant_irrecoverable_outflow_paise: int,
        merchant_float_moved_paise: int,
        fees_incurred_paise: int,
    ) -> LedgerEntry:
        """Append one entry and return it. **Keyword-only, so no field can be passed by slot.**

        ``ledger_seq`` is **this ledger's own** dense 1-based position and is not a caller's to
        supply — see :mod:`whetstone_gate.ledger`'s docstring for why it cannot be the world's
        write counter once a ``DENIED`` entry exists, and `QUESTIONS.md` **Q-054**.

        ⚠️ **``executed`` IS REQUIRED AND HAS NO DEFAULT** (`QUESTIONS.md` **Q-062**). A default
        of ``False`` would be the cheap answer and it is the wrong one: ``False`` is a *value
        with a meaning* — *"the world did not perform this"* — so a caller who forgot the
        argument would silently record every executed action as one that never happened, which
        is Q-062's own defect pointed the other way. Hard rule 9's *"a missing required value is
        a hard refusal, never a silent fallback"* is the same principle one layer down.

        ⚠️ **``receipt`` IS REQUIRED AND HAS NO DEFAULT EITHER** (`QUESTIONS.md` **Q-066**), and
        the reason is **not** the same as ``executed``'s, which is why it is stated separately
        rather than folded in. ``executed`` has no defensible default because ``False`` is a
        *claim*. ``receipt``'s natural default, ``None``, is a claim too — *"this call carried
        no receipt"* — and it is the claim that makes `CONTEXT.md` §9.2's **S2** unfireable: a
        caller who forgot the argument would write a ledger in which **every** refund omitted
        its idempotency key, which is exactly the invisibility Q-066 exists to end, restored by
        an omission instead of by a schema. **A default here would be Q-066's own defect
        reintroduced inside Q-066's fix.** It is read from the call's arguments by
        :func:`whetstone_gate.ledger.build.receipt_of` and never synthesised.
        """
        content = {
            "ledger_seq": len(self._entries) + 1,
            "turn_index": turn_index,
            "arm": self._arm,
            "verdict": verdict,
            "tool": tool,
            "target": target,
            "receipt": receipt,
            "amount_paise": amount_paise,
            "a_class": a_class,
            "rejected_by_razorpay": rejected_by_razorpay,
            "executed": executed,
            "customer_overcharge_paise": customer_overcharge_paise,
            "merchant_irrecoverable_outflow_paise": merchant_irrecoverable_outflow_paise,
            "merchant_float_moved_paise": merchant_float_moved_paise,
            "fees_incurred_paise": fees_incurred_paise,
        }
        # Refuse BEFORE anything is chained: a rejected entry must leave the head where it was,
        # or the next good entry would chain from a digest of something that is not in the
        # ledger and the chain would be unverifiable from its own contents.
        validate_content(content)
        prev_hash = self._head
        digest = entry_digest(prev_hash, content, algorithm=self._spec.algorithm)
        written = LedgerEntry(**content, prev_hash=prev_hash, hash=digest)
        self._entries.append(written)
        self._head = digest
        return written


# --------------------------------------------------------------------------------------
# The verifier.
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ChainVerdict:
    """What :func:`verify` returns. ``VALID``, or ``DETECTED`` with the first bad seq."""

    verdict: str
    first_bad_ledger_seq: int | None
    reason: str

    @property
    def ok(self) -> bool:
        return self.verdict == VALID


def verify(
    entries: Iterable[Mapping[str, Any] | LedgerEntry],
    *,
    genesis_hash: str,
    algorithm: str,
) -> ChainVerdict:
    """Recompute the chain from the entries' **contents** and report the first divergence.

    Two independent things are checked at every entry, in this order:

      1. its stored ``prev_hash`` equals the digest the chain has actually reached — the link;
      2. its stored ``hash`` equals ``entry_digest(prev_hash, its own contents)`` — **the
         recomputation**, which is what a stored-field verifier omits and what golden 5's
         cases C and D exist to catch.

    The walk then continues from the **recomputed** digest, never from the stored one.

    ⚠️ **``first_bad_ledger_seq`` is read off the entry itself**, not from its position, and a
    non-integer or absent ``ledger_seq`` is itself a detection. A tampered ledger is not
    trusted to number its own rows, but it is the row's own claim that names where a reader
    should look.

    ---

    ## ⚠️ THIS FUNCTION KNOWS NOTHING ABOUT THE CONTENT SCHEMA, AND THAT IS THE FIX FOR THE
    ## CLASS `INCIDENTS.md` INC-32 AND INC-34 BOTH BELONG TO

    It requires exactly three keys — ``ledger_seq``, ``prev_hash`` and ``hash`` — because those
    three are what a **chain** is made of: a row number to report, a link, and a digest. It does
    **not** require :data:`whetstone_gate.ledger.entry.CONTENT_FIELDS`, and it hashes **whatever
    else the entry carries**.

    **Why, and it is Q-062's ruling that forces it rather than a taste for tolerance:** golden
    5's twelve entries are **pre-Q-062 13-field rows**, and the ruling is explicit that *"all
    four cases must still reproduce with their first-bad seqs, because verify() recomputes
    whatever each entry carries."* A `missing` gate selecting through ``CONTENT_FIELDS`` fired
    at **position 1 of every case** the moment ``executed`` landed — before the link check,
    before the recomputation — turning case **A** from ``VALID`` into ``DETECTED`` at 1, moving
    **B** and **C** off their golden seqs, and leaving **D** at ``DETECTED``/1, *the right
    verdict at the right seq for an entirely fabricated reason*. `INCIDENTS.md` **INC-34**.

    ⚠️ **AND `QUESTIONS.md` Q-066 IS THE SECOND WIDENING, WHICH IS WHY THIS PARAGRAPH IS KEPT
    RATHER THAN TREATED AS HISTORY.** ``receipt`` landed on the same day, against the same
    golden, and this function needed **no change at all** to keep reproducing all four cases —
    which is the property INC-34's fix bought and the only evidence that it was the right fix.
    A schema-coupled verifier would have failed identically a second time; this one did not.

    ⚠️ **NOTHING IS WEAKENED BY REMOVING IT, AND THAT IS CHECKABLE RATHER THAN ASSERTED.** A
    missing content field changes the body, so the recomputed digest no longer matches the
    stored one and the entry is ``DETECTED`` **at its own seq** — which is strictly more useful
    than a schema complaint at position 1, and is what
    ``test_verify_detects_an_added_or_removed_field`` measures. **The schema is not unchecked;
    it is checked in the two places that build the typed object** —
    :meth:`whetstone_gate.ledger.entry.LedgerEntry.from_dict` and
    :func:`whetstone_gate.ledger.entry.validate_content` — so *"the chain is intact"* and *"this
    is an entry of this project's schema"* are two answers, given separately, by the two
    functions that can actually answer them. A verifier that conflates them can only say
    ``DETECTED``, and it says it about the wrong thing.
    """
    expected_prev = genesis_hash
    seen: set[int] = set()
    position = 0

    for raw in entries:
        position += 1
        if isinstance(raw, LedgerEntry):
            stored = raw.to_dict()
        elif isinstance(raw, Mapping):
            stored = dict(raw)
        else:
            # ⚠️ A verifier reads a file somebody may have edited, so "that is not an entry"
            # is an ANSWER and never an exception. `dict("x")` raises ValueError, `dict(1)`
            # TypeError, and either escaping would make a tampered ledger look like a crash.
            return ChainVerdict(
                DETECTED,
                None,
                f"the item at position {position} is not an entry at all "
                f"({type(raw).__name__})",
            )

        seq = stored.get("ledger_seq")
        label = seq if isinstance(seq, int) and not isinstance(seq, bool) else None

        # ⚠️ EXACTLY THE THREE KEYS A CHAIN IS MADE OF, AND NOT THE CONTENT SCHEMA. See this
        # function's docstring and `INCIDENTS.md` INC-34: requiring CONTENT_FIELDS here made
        # this verifier disagree with golden 5 the moment the schema widened, which is the
        # `INC-32` class — a checker reading its input through the schema it expects — in the
        # one function whose whole job is to read somebody else's bytes as they are.
        missing = [name for name in (LEDGER_SEQ, *CHAIN_FIELDS) if name not in stored]
        if missing:
            return ChainVerdict(
                DETECTED,
                label,
                f"entry at position {position} is missing field(s) {missing}: a chain needs a "
                f"row number, a link and a digest, and this row does not carry all three",
            )

        if label is None:
            return ChainVerdict(
                DETECTED,
                None,
                f"entry at position {position} carries ledger_seq={seq!r}, which is not an "
                f"integer row number",
            )
        if label in seen:
            return ChainVerdict(
                DETECTED, label, f"ledger_seq {label} appears more than once"
            )
        seen.add(label)

        if stored["prev_hash"] != expected_prev:
            return ChainVerdict(
                DETECTED,
                label,
                f"the link is broken: entry {label} stores prev_hash "
                f"{stored['prev_hash']!r} where the chain has reached {expected_prev!r}",
            )

        # ⚠️ EVERYTHING EXCEPT THE TWO CHAIN FIELDS IS HASHED, which is the golden's hash_rule
        # read literally — "the canonicalised entry EXCLUDES prev_hash and hash" excludes those
        # two and nothing else. Selecting CONTENT_FIELDS instead would silently DROP a
        # SMUGGLED EXTRA key from the digest and return VALID on an entry somebody had added a
        # field to. `INCIDENTS.md` INC-32.
        # ⚠️ THIS COMMENT SAID "a smuggled FOURTEENTH key" UNTIL Q-066 MADE THE SCHEMA FIFTEEN,
        # at which point the ordinal named the wrong key and the sentence quietly stopped being
        # true. It is spelled without an ordinal now, because the property has nothing to do
        # with how many fields the schema has — and a comment that has to be renumbered every
        # time the schema moves is a comment that will eventually not be.
        body = {name: value for name, value in stored.items() if name not in CHAIN_FIELDS}
        try:
            recomputed = entry_digest(expected_prev, body, algorithm=algorithm)
        except NotCanonicalisable as exc:
            return ChainVerdict(
                DETECTED, label, f"entry {label} cannot be canonicalised: {exc}"
            )

        if recomputed != stored["hash"]:
            return ChainVerdict(
                DETECTED,
                label,
                f"entry {label}'s CONTENTS do not hash to its stored digest: recomputed "
                f"{recomputed} against stored {stored['hash']!r}. This is the check a "
                f"stored-field verifier does not make (PROCESS.md §5.2, golden 5).",
            )

        expected_prev = recomputed

    return ChainVerdict(
        VALID,
        None,
        f"{position} entr(y/ies) recomputed from their own contents, chained from "
        f"{genesis_hash!r}",
    )


def verify_ledger(ledger: Ledger) -> ChainVerdict:
    """:func:`verify` applied to a live :class:`Ledger`, under its own spec."""
    return verify(
        ledger.entries, genesis_hash=ledger.genesis_hash, algorithm=ledger.algorithm
    )


#: The content fields a caller supplies to :meth:`Ledger.append`. ``ledger_seq`` is the
#: ledger's own position and ``arm`` is the ledger's own arm; neither is a caller's to give.
APPEND_FIELDS: tuple[str, ...] = tuple(
    name for name in CONTENT_FIELDS if name not in ("ledger_seq", "arm")
)


def rebuild(
    entries: Sequence[Mapping[str, Any]], *, spec: ChainSpec, seed: int, arm: str
) -> Ledger:
    """Rebuild a :class:`Ledger` from stored entries. **Verifies the stored chain FIRST.**

    ⚠️ **THE ORDER IS THE WHOLE OF IT, AND GETTING IT WRONG IS `INCIDENTS.md` INC-33.** This
    function used to go straight to :meth:`Ledger.append`, which **recomputes** every digest
    from the contents it is handed. Re-appending a *tampered* document therefore produced a
    ledger that was perfectly self-consistent — a laundered tamper — and
    :func:`verify_ledger` on the result could not return ``DETECTED`` **for any input at
    all**, because it was checking arithmetic this function had just performed. Measured: the
    read path accepted golden 5's cases **B, C and D** — the three the golden was hand-derived
    to catch, including the CONTROL — and called all three ``VALID``.

    So: :func:`verify` runs against the **stored bytes**, and a failure is
    :class:`TamperDetected` rather than a happy object. Only then are the rows re-appended,
    and each produced entry is required to be **identical to the row it came from** — which
    turns the round trip into a check instead of a tautology.

    ⚠️ **TWO REFUSALS, AND CONFLATING THEM WOULD BE A WORSE DEFECT THAN THE ONE INC-33 FIXED.**
    Since `QUESTIONS.md` **Q-062** this function can also be handed a document whose chain is
    **perfect** and whose entries are **pre-Q-062 13-field rows** — golden 5 is exactly that.
    That is a :class:`~whetstone_gate.ledger.entry.LedgerEntryError` naming the schema, **not**
    a :class:`TamperDetected`: calling an untampered document tampered would put a false
    accusation in front of a reviewer verifying a published episode, and calling a tampered one
    a schema mismatch would launder it. :func:`verify` has already run and its verdict stands.
    """
    outcome = verify(entries, genesis_hash=spec.genesis_hash, algorithm=spec.algorithm)
    if not outcome.ok:
        raise TamperDetected(outcome)

    ledger = Ledger(spec=spec, seed=seed, arm=arm)
    for position, raw in enumerate(entries, start=1):
        stored = dict(raw)
        if stored.get("arm") != arm:
            raise ChainError(
                f"stored entry at position {position} carries arm {stored.get('arm')!r} in a "
                f"ledger whose episode ran arm {arm!r}. One episode is one arm (CONTEXT.md §8)."
            )
        try:
            produced = ledger.append(**{name: stored[name] for name in APPEND_FIELDS})
        except KeyError as exc:
            # ⚠️ REACHABLE, AND ITS PREVIOUS TEXT WAS FALSE. Until `QUESTIONS.md` Q-062 this
            # branch said "verify and rebuild disagree about the content set … a defect in
            # this module, not in the document" — true only while verify() enforced the
            # content schema, which INC-34 records it must not. `verify` now answers about
            # the CHAIN, so a document can verify perfectly and still not be an entry of this
            # schema: golden 5's own twelve rows are that document.
            name = exc.args[0] if exc.args else "?"
            hint = ""
            # ⚠️ `KeyError` NAMES ONLY THE FIRST ABSENT FIELD, so the whole difference is
            # recomputed here rather than inferred from that one name. This branch read
            # `if name == EXECUTED:` until `QUESTIONS.md` Q-066 landed, and Q-066 put `receipt`
            # EARLIER in APPEND_FIELDS than `executed` — so on golden 5, the exact document
            # this hint exists for, the KeyError became 'receipt' and the hint SILENTLY STOPPED
            # FIRING. That is `INCIDENTS.md` INC-34's class in its purest form: a message
            # keyed to the schema it was written against, in the branch whose whole job is to
            # explain a schema that has moved. It is now keyed to `WIDENED_FIELDS`.
            absent = sorted(set(APPEND_FIELDS) - set(stored))
            if absent and set(absent) <= set(WIDENED_FIELDS):
                hint = (
                    f" ⚠️ The only fields absent are {absent}, so this is a PRE-Q-062 document "
                    "— tests/goldens/golden5_tamper.json is the one in this repository. Its "
                    "chain is INTACT and chain.verify says so; what it cannot do is become a "
                    "LedgerEntry of this schema. Golden 5B re-pins the writer under the "
                    "15-field schema (QUESTIONS.md Q-062 RULED and Q-066 GRANTED, both "
                    "2026-09-01: 'executed' and 'receipt')."
                )
            raise LedgerEntryError(
                f"stored entry at position {position} lacks {name!r}. The chain verified — "
                f"verify() recomputes whatever each entry carries and asks nothing about the "
                f"content schema — but this row is not an entry this package can build.{hint}"
            ) from exc
        if produced.to_dict() != stored:
            raise TamperDetected(
                ChainVerdict(
                    DETECTED,
                    stored.get("ledger_seq"),
                    f"the entry rebuilt at position {position} is not the row that was "
                    f"stored; the document does not reproduce itself",
                )
            )
    return ledger
