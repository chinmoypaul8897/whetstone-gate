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

**A hash chain anchors its START. Nothing here anchors its END.** Deleting entries from the
**tail** of a stored ledger leaves a shorter chain that is internally perfect, and
:func:`verify` returns ``VALID`` on it — correctly, because every entry still present really
does hash to its stored digest from the root the document names. Deleting from the middle, or
altering anything, breaks the chain and is detected; truncation is the one operation that does
not, and it is exactly the operation `CLAUDE.md` hard rule 11 is about.

`tests/test_c7_ledger.py::test_a_truncated_tail_is_NOT_detected_and_that_is_a_stated_limitation`
asserts the limitation rather than hiding it, and it is recorded in
`docs/reviews/OPEN_FINDINGS.md`. **The remedy is not cryptographic and is not this chunk's**: it
is an external commitment to each episode's head — the same mechanism `PROCESS.md` §6a already
builds for `config/`, where the answer to *"a git timestamp is forgeable"* was **witness it
outside this repository**, not a better hash. Until something publishes an episode's head hash
and entry count where the operator cannot quietly revise them, *"the ledger is tamper-evident"*
means **tamper-evident against modification, and against deletion anywhere but the end.**
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
    VERDICTS_BY_ARM,
    LedgerEntry,
    validate_content,
)

#: The verifier's two verdicts. Golden 5's own words, in its ``expected_verdict`` field.
VALID = "VALID"
DETECTED = "DETECTED"


class ChainError(RuntimeError):
    """Base: the chain cannot be built or read as specified. Always a refusal."""


class ChainConfigError(ChainError):
    """``config/`` does not describe a hash chain this module can compute."""


class NotCanonicalisable(ChainError):
    """A value reached the digest that canonical JSON cannot represent deterministically."""


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

    ⚠️ **``ensure_ascii=False``, and it is a decision rather than a default.** §16 and golden
    5's ``hash_rule`` both say the operands are **UTF-8 strings**, and escaping a non-ASCII
    character to ``\\uXXXX`` would be to hash a re-encoding of the entry rather than the entry.
    It is also RFC 8785's reading. **Golden 5 cannot discriminate the two** — every byte of it
    is ASCII, on which the two agree exactly — so the choice is recorded as a **Class B**
    deviation with its reasoning here and raised in `QUESTIONS.md` **Q-053**, because the one
    field that can carry attacker-authored text is ``target``: an attacker may call
    ``fetch_payment`` with any string it likes as ``payment_id``.

    ⚠️ **A float is refused rather than serialised.** ``json`` writes ``repr``-shaped floats,
    so a binary float in an entry would put a platform-dependent string inside a digest that
    is supposed to be identical everywhere — and `PROCESS.md` §5.1 forbids one on the money
    path in the first place. ``allow_nan=False`` closes the same door for the three values
    that have no JSON spelling at all.
    """
    for name, value in body.items():
        if isinstance(value, float):
            raise NotCanonicalisable(
                f"{name}={value!r} is a binary float. PROCESS.md §5.1: money is integer paise "
                f"end to end, and a float's JSON spelling is not portable enough to hash."
            )
    return json.dumps(
        dict(body),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def entry_digest(prev_hash: str, body: Mapping[str, Any], *, algorithm: str) -> str:
    """``SHA-256( prev_hash ‖ canonical-JSON(body) )``, both operands UTF-8 strings.

    The concatenation is of the **strings**, then encoded once — which is what golden 5's
    ``hash_rule`` says and what reproduces its twelve digests.
    """
    digest = hashlib.new(algorithm)
    digest.update((prev_hash + canonical_json(body)).encode("utf-8"))
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
        amount_paise: int | None,
        a_class: str | None,
        rejected_by_razorpay: bool,
        customer_overcharge_paise: int,
        merchant_irrecoverable_outflow_paise: int,
        merchant_float_moved_paise: int,
        fees_incurred_paise: int,
    ) -> LedgerEntry:
        """Append one entry and return it. **Keyword-only, so no field can be passed by slot.**

        ``ledger_seq`` is **this ledger's own** dense 1-based position and is not a caller's to
        supply — see :mod:`whetstone_gate.ledger`'s docstring for why it cannot be the world's
        write counter once a ``DENIED`` entry exists, and `QUESTIONS.md` **Q-054**.
        """
        content = {
            "ledger_seq": len(self._entries) + 1,
            "turn_index": turn_index,
            "arm": self._arm,
            "verdict": verdict,
            "tool": tool,
            "target": target,
            "amount_paise": amount_paise,
            "a_class": a_class,
            "rejected_by_razorpay": rejected_by_razorpay,
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

        missing = [name for name in (*CONTENT_FIELDS, *CHAIN_FIELDS) if name not in stored]
        if missing:
            return ChainVerdict(
                DETECTED,
                label,
                f"entry at position {position} is missing field(s) {missing}: the digest is "
                f"taken over the content set and an absent field is a changed entry",
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
        # smuggled fourteenth key from the digest and return VALID on an entry somebody had
        # added a field to. `INCIDENTS.md` INC-32.
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
    """Rebuild a :class:`Ledger` by **re-appending** stored entries through :meth:`append`.

    Every digest is recomputed on the way in, so a document that survives this round trip
    unchanged is one whose contents really do produce its stored chain. Used by the store's
    read path and by the determinism test; it is not a shortcut around :func:`verify`, it is
    the same arithmetic reached from the write side.

    Refuses a stored entry whose ``arm`` disagrees with the episode's — the read-side half of
    the guard :class:`Ledger`'s docstring describes.
    """
    ledger = Ledger(spec=spec, seed=seed, arm=arm)
    for position, raw in enumerate(entries, start=1):
        stored = dict(raw)
        if stored.get("arm") != arm:
            raise ChainError(
                f"stored entry at position {position} carries arm {stored.get('arm')!r} in a "
                f"ledger whose episode ran arm {arm!r}. One episode is one arm (CONTEXT.md §8)."
            )
        ledger.append(**{name: stored[name] for name in APPEND_FIELDS})
    return ledger
