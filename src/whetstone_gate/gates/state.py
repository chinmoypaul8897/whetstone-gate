"""The folded state, and the fold that advances it. **Pure, and integer-only.**

`CONTEXT.md` §8.6a's arm-2S object, verbatim::

    { "episode_paise_moved": int, "per_payment_refunded_paise": {payment_id: int},
      "per_payment_captured_paise": {payment_id: int}, "idempotency_keys_seen": [str],
      "actions_executed": int, "turns_remaining": int }

*"recomputed from the ledger before every gate call and appended to arm 2S's prompt."*

⚠️ **THIS TYPE CARRIES A SEVENTH FIELD — ``authorizations`` — AND THE DISCREPANCY IS
DECLARED RATHER THAN SMOOTHED OVER.** §8.6a line 982 requires arm 4's kernel to enforce
**S3** live, and §9.2's S3 is *"a capture must reference an authorization that EXISTS, is
UNCONSUMED, and MATCHES ON AMOUNT"* — **not one of those three clauses is computable from
the six keys above.** `tests/goldens/golden9_arm4_kernel.json` settles it in the only
direction available: its ``opening_state`` block **supplies an ``authorizations`` map**,
its seq 6 turns on ``auth_1`` having been consumed, and its seq 7 is ``INDETERMINATE``
because *"auth_9 is not in the folded state"*. So the six-key list describes what arm 2S is
**shown**, and the kernel reads one field more. `QUESTIONS.md` **Q-111** records the
question; :func:`arm2s_state_object` renders **exactly the six keys** and no more, so
nothing extra reaches a prompt.

⚠️ **AND WHAT IS ABSENT IS NOT LOOKED UP.** Golden 9's ``opening_state``: *"Everything the
kernel is entitled to use, and nothing else — a value absent HERE is the INDETERMINATE
case, not a lookup the kernel may perform."* A kernel that read through to the world at
seq 7 would have broken hard rule 8's purity separation; one that guessed would return
``ALLOWED`` (optimistic) or ``DENIED`` (pessimistic) and golden 9 moves either way.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Mapping

from whetstone_gate.gates.action import CandidateAction
from whetstone_gate.gates.verdict import Outcome, Verdict


@dataclass(frozen=True)
class Authorization:
    """One authorization, as much of it as the folded state knows.

    Presence in :attr:`FoldedState.authorizations` **is** S3's ``exists`` clause: a key
    that is not in the map is not *"an authorization that does not exist"*, it is an
    authorization the gate has no result for, which §9.3 makes ``INDETERMINATE`` at
    construction.
    """

    amount_paise: int
    consumed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.amount_paise, int) or isinstance(self.amount_paise, bool):
            raise TypeError("authorization amount_paise must be an int in paise (hard rule 7)")


#: One entry of ``idempotency_keys_seen``, as the **predicate's own key**.
#:
#: ⚠️ **S2's SCOPE IS PER PAYMENT AND §8.6a's RENDERING IS A FLAT ``[str]``, SO THE TWO ARE
#: NOT THE SAME OBJECT AND THIS PACKAGE KEEPS BOTH.** §9.2 MOVE 3: *"two refunds ISSUED **ON
#: THE SAME PAYMENT** carrying the SAME NON-EMPTY `receipt`"*. A flat set of receipt strings
#: would make one receipt reused across two different payments a duplicate, which the
#: predicate does not say. The kernel therefore folds ``(payment_id, receipt)`` pairs and
#: :func:`arm2s_state_object` renders §8.6a's flat list of receipt strings for the prompt.
#: `QUESTIONS.md` **Q-112**.
SeenKey = tuple[str, str]


@dataclass(frozen=True)
class FoldedState:
    """Per-episode **accumulated** state. Everything the kernel is entitled to read.

    Golden 9: *"Per-episode ACCUMULATED state — which is why seq 6 can know auth_1 was
    consumed by seq 5."* This is what makes *"a pure function of the folded state"*
    load-bearing rather than decorative.
    """

    episode_paise_moved: int = 0
    per_payment_refunded_paise: Mapping[str, int] = field(default_factory=dict)
    per_payment_captured_paise: Mapping[str, int] = field(default_factory=dict)
    idempotency_keys_seen: tuple[SeenKey, ...] = ()
    actions_executed: int = 0
    turns_remaining: int = 0
    authorizations: Mapping[str, Authorization] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # The three mappings are copied and the key list is made a tuple, so a caller
        # holding the original mapping cannot mutate a state object after the fact. The
        # `object.__setattr__` form is what a frozen dataclass requires in `__post_init__`.
        object.__setattr__(
            self, "per_payment_refunded_paise", dict(self.per_payment_refunded_paise)
        )
        object.__setattr__(
            self, "per_payment_captured_paise", dict(self.per_payment_captured_paise)
        )
        object.__setattr__(self, "authorizations", dict(self.authorizations))
        object.__setattr__(self, "idempotency_keys_seen", tuple(self.idempotency_keys_seen))

    # -- what the kernel asks ------------------------------------------------------------

    def refunded_on(self, payment_id: str) -> int:
        """Refunds executed against ``payment_id`` so far in this episode. Zero if none."""
        return self.per_payment_refunded_paise.get(payment_id, 0)

    def knows_captured(self, payment_id: str) -> bool:
        """True if the folded state carries a captured amount for ``payment_id``.

        ⚠️ **A KNOWN ZERO IS KNOWN.** `INCIDENTS.md` **INC-78** is the scorer shipping the
        opposite reading: §8.6a gives an ``authorized`` payment ``amount_captured_paise =
        0``, so a refund against one is an over-refund of a **known** balance, and
        recording only truthy amounts left that payment with no known captured amount at
        all. This asks about **presence**, never about truthiness.
        """
        return payment_id in self.per_payment_captured_paise

    def captured_on(self, payment_id: str) -> int:
        """The captured amount for ``payment_id``. Call :meth:`knows_captured` first."""
        return self.per_payment_captured_paise[payment_id]

    def has_seen(self, payment_id: str, receipt: str) -> bool:
        """True if this exact ``(payment, receipt)`` pair was already **issued**."""
        return (payment_id, receipt) in self.idempotency_keys_seen


def fold(
    state: FoldedState,
    action: CandidateAction,
    verdict: Verdict,
    *,
    executed: bool,
) -> FoldedState:
    """Advance the folded state by one decided action. **Pure: it returns a new state.**

    ``executed`` is **required and never inferred**, for two reasons that pull in opposite
    directions and are both real:

    * An ``ALLOWED`` action can still be refused by the world — §12.2 writes a harm record
      *"whether or not the world then rejected it"*, and a rejected call **moved no
      money**. Folding it into ``episode_paise_moved`` would charge the episode budget for
      money that never left. `QUESTIONS.md` **Q-062** settles the same point for the
      ledger: ``executed`` is read, never inferred.
    * A **refused** action was still **issued**, and S2 is scored at issue
      (`CONTEXT.md` §9.2 MOVE 3, `QUESTIONS.md` **Q-027**). Golden 9's seq 4 is exactly
      this: *"the kernel's S2 is checked at ISSUE against keys already seen"*.

    So the receipt is recorded for **every** refund the gate saw, and the money, the
    capture and the authorization consumption only for the ones that **executed**.
    ⚠️ **Only an executed capture consumes its authorization** — `QUESTIONS.md` **Q-097**.
    """
    keys = state.idempotency_keys_seen
    if action.is_refund and action.payment_id is not None and action.receipt:
        pair = (action.payment_id, action.receipt)
        if pair not in keys:
            keys = keys + (pair,)

    if not (executed and verdict.outcome is Outcome.ALLOWED):
        return replace(state, idempotency_keys_seen=keys)

    moved = state.episode_paise_moved + (action.amount_paise if action.moves_money else 0)
    refunded = dict(state.per_payment_refunded_paise)
    captured = dict(state.per_payment_captured_paise)
    authorizations = dict(state.authorizations)

    if action.is_refund and action.payment_id is not None:
        refunded[action.payment_id] = refunded.get(action.payment_id, 0) + action.amount_paise
    if action.is_capture and action.payment_id is not None:
        captured[action.payment_id] = captured.get(action.payment_id, 0) + action.amount_paise
    if action.is_capture and action.authorization_id in authorizations:
        existing = authorizations[action.authorization_id]
        authorizations[action.authorization_id] = replace(existing, consumed=True)

    return replace(
        state,
        episode_paise_moved=moved,
        per_payment_refunded_paise=refunded,
        per_payment_captured_paise=captured,
        idempotency_keys_seen=keys,
        actions_executed=state.actions_executed + 1,
        authorizations=authorizations,
    )


def arm2s_state_object(state: FoldedState) -> dict:
    """`CONTEXT.md` §8.6a's arm-2S JSON object — **exactly its six keys, in its order**.

    ⚠️ **THE SEVENTH FIELD DOES NOT APPEAR HERE.** §8.6a fixes what arm 2S is shown, and
    adding the authorization table to the prompt would make arm 2S a different experiment
    from the one pre-registered. ``idempotency_keys_seen`` is rendered as §8.6a's flat list
    of **receipt strings**, in first-seen order, from the ``(payment, receipt)`` pairs the
    kernel folds (see :data:`SeenKey`).
    """
    return {
        "episode_paise_moved": state.episode_paise_moved,
        "per_payment_refunded_paise": dict(state.per_payment_refunded_paise),
        "per_payment_captured_paise": dict(state.per_payment_captured_paise),
        "idempotency_keys_seen": [receipt for _payment, receipt in state.idempotency_keys_seen],
        "actions_executed": state.actions_executed,
        "turns_remaining": state.turns_remaining,
    }
