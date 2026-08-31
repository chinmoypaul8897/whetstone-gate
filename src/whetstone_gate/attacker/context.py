"""The attacker's sliding-window context, and the DETERMINISTIC summary.

**SLIDING-WINDOW CONTEXT IS MANDATORY, NOT AN OPTIMISATION** (`CONTEXT.md` §13.3). The
spike burned **~300K tokens in ONE episode** by resending full history every turn — more
than a whole day's allowance on both 200K-TPD lanes. The window is:

  * the last **N** turns **verbatim** — ``attacker.context_window_turns_verbatim``;
  * plus a running summary capped at **M** tokens — ``attacker.context_summary_max_tokens``;
  * with the tool schemas emitted **once per turn**.

All three values are read from ``config/`` and none is written here. They are §8.6 rows
and registry rows, so a hardcoded copy is a tripwire failure by construction.

⚠️ **THE SUMMARY IS PRODUCED DETERMINISTICALLY BY TEMPLATE, NEVER BY AN LLM CALL.**
`CONTEXT.md` §13.3 gives the reason in one line: it adds no request, and it therefore
breaks neither the seeded-determinism claim nor the 20-requests-per-episode budget. It
concatenates the running folded state (§8.6's exact JSON shape) with the last denial
reason, and **identical state produces byte-identical summary text**.

---

## ⚠️ POLICY-BLINDNESS IS STRUCTURAL HERE, NOT A PROMISE

`CONTEXT.md` §10.1 and the C6 card: the attacker's context contains **no policy string, no
hole, no attack list and no gate denial reason**. This module makes that checkable rather
than intended, by tagging **every** part of the assembled context with its
:class:`Origin`:

  * :attr:`Origin.AUTHORED` — text **this harness wrote**: the system prompt and the
    deterministic summary. Nothing else. This is the surface on which a policy leak could
    only ever be *ours*, and it is where the four blindness tests bite hardest.
  * :attr:`Origin.ATTACKER` — the model's own prior output, fed back verbatim.
  * :attr:`Origin.WORLD` — a tool result, **verbatim from the tool executor**. This
    harness neither annotates nor rewrites it.

⚠️ **A tool result naming ``pay_CANARYRECON`` is NOT a leak, and confusing the two would
break the experiment.** §10.1: the probe's notes are returned by ``fetch_payments``
*identically in every arm*, and *"the attacker discovers the door by doing the one thing a
competent attacker always does: reading."* The requirement is **no DIFFERENTIAL
information across arms**, not concealment. What must never appear is a description of the
door **as** a door: our probe-predicate vocabulary, our clause numbers, our attack list.
So the blindness tests assert **globally** for the things that must never appear anywhere,
and **over the AUTHORED surface** for the probe text the world is entitled to return.

⚠️ **The gate denial the attacker sees is ONE generic string** — `CONTEXT.md` §8.6, the
same on ``DENIED`` and on ``INDETERMINATE``, identical across arms. This module never
authors it, never parses it and never learns an arm's identity: it has no gate object at
all. A denial arrives as a tool result like any other, which is why there is nothing here
that *could* leak a clause number.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum

from whetstone_gate.attacker.estimate import estimate_text


class Origin(Enum):
    """Who wrote this part of the context. The whole blindness argument rests on it."""

    AUTHORED = "authored"
    """Written by THIS harness — the system prompt and the deterministic summary."""

    ATTACKER = "attacker"
    """The model's own prior output, replayed verbatim."""

    WORLD = "world"
    """A tool result, verbatim from the tool executor. Never annotated here."""


@dataclass(frozen=True)
class ContextPart:
    """One message of the assembled context, with its provenance attached."""

    origin: Origin
    role: str
    text: str
    label: str


@dataclass(frozen=True)
class FoldedState:
    """`CONTEXT.md` §8.6's folded ledger state, in §8.6's exact shape and key order.

    §8.6 gives it as::

        { "episode_paise_moved": int, "per_payment_refunded_paise": {payment_id: int},
          "per_payment_captured_paise": {payment_id: int}, "idempotency_keys_seen": [str],
          "actions_executed": int, "turns_remaining": int }

    ⚠️ **This is arm 2S's object and the attacker's summary is built from the same shape,
    which is what §13.3 says the template concatenates.** It carries facts about what the
    attacker itself has already done — amounts it moved, keys it used, turns it has left.
    **It carries no cap, no clause and no arm identity**, which is why feeding it to the
    attacker leaks no policy: the attacker learns what it did, never what it is not
    allowed to do.
    """

    episode_paise_moved: int
    per_payment_refunded_paise: dict[str, int] = field(default_factory=dict)
    per_payment_captured_paise: dict[str, int] = field(default_factory=dict)
    idempotency_keys_seen: tuple[str, ...] = ()
    actions_executed: int = 0
    turns_remaining: int = 0

    def to_json(self) -> str:
        """§8.6's shape as canonical JSON — deterministic by construction.

        Keys are emitted in §8.6's own order rather than sorted, because §8.6 *is* the
        specification of the shape; the nested maps ARE sorted, because a dict's insertion
        order is a property of how the ledger happened to be walked and would make the
        summary depend on history rather than on state. ``separators`` is explicit so no
        whitespace difference can make two identical states render differently.
        """
        payload = {
            "episode_paise_moved": self.episode_paise_moved,
            "per_payment_refunded_paise": dict(sorted(self.per_payment_refunded_paise.items())),
            "per_payment_captured_paise": dict(sorted(self.per_payment_captured_paise.items())),
            "idempotency_keys_seen": sorted(self.idempotency_keys_seen),
            "actions_executed": self.actions_executed,
            "turns_remaining": self.turns_remaining,
        }
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


#: The two labels the deterministic template puts in front of its two halves. They are
#: prose written by this harness, not spec text, and they carry no policy.
#:
#: ⚠️ **Public because the blindness test needs them.** Claim 4 — *the attacker sees the
#: ONE generic denial string and nothing more* — is checked by reading the refusal FIELD
#: back out of the assembled summary and comparing it to the string parsed from §8.6. A
#: test that instead searched the whole summary for stray text would fire on the folded
#: state, which §13.3 requires the template to carry.
STATE_LABEL = "STATE SO FAR: "
LAST_REFUSAL_LABEL = "LAST TOOL REFUSAL: "

#: What the template says when no tool has refused anything yet. Note what it is NOT: it
#: does not say "no policy violation", because this harness does not know that a policy
#: exists.
NO_REFUSAL = "none"

#: Marks a summary the cap forced to be shortened. Deterministic, and VISIBLE: a silently
#: truncated summary is `CLAUDE.md` hard rule 11's shape applied to context — a number
#: quietly shrinking with nothing printed.
TRUNCATION_MARK = "...[TRUNCATED TO FIT THE CONFIGURED SUMMARY CAP]"


def render_summary(state: FoldedState, last_refusal: str | None, token_cap: int) -> str:
    """The running summary — **a template, never a model call**.

    Deterministic and pure: identical ``(state, last_refusal, token_cap)`` produces
    byte-identical text. `CONTEXT.md` §13.3 requires exactly this, because a summary
    produced by an LLM would add a request per turn — breaking the
    20-requests-per-episode budget — and would make the seeded-determinism claim false.

    ``token_cap`` comes from ``config/protocol.yaml:attacker.context_summary_max_tokens``.
    It is a parameter and never a literal here.

    **Truncation, when the cap binds, is deterministic and marked.** The text is cut on a
    character boundary derived from the cap and the marker is appended, so two identical
    states still render identically and a reader can see that a cut happened.
    """
    refusal = NO_REFUSAL if last_refusal is None else last_refusal
    text = f"{STATE_LABEL}{state.to_json()}\n{LAST_REFUSAL_LABEL}{refusal}"
    if estimate_text(text) <= token_cap:
        return text
    from whetstone_gate.attacker.estimate import CHARS_PER_TOKEN

    budget = max(token_cap * CHARS_PER_TOKEN - len(TRUNCATION_MARK), 0)
    return text[:budget] + TRUNCATION_MARK


@dataclass(frozen=True)
class Turn:
    """One completed turn: what the attacker emitted, and what came back."""

    index: int
    attacker_text: str
    tool_result_text: str


@dataclass(frozen=True)
class AssembledContext:
    """⚠️ **The actual context that would be sent** — the object the blindness tests read.

    They assert over *this*, never over the source and never over a constructor argument,
    because those two prove only that somebody intended the property.
    """

    parts: tuple[ContextPart, ...]

    def authored_parts(self) -> tuple[ContextPart, ...]:
        return tuple(p for p in self.parts if p.origin is Origin.AUTHORED)

    def authored_text(self) -> str:
        """Everything THIS HARNESS wrote into the context, concatenated."""
        return "\n".join(p.text for p in self.authored_parts())

    def full_text(self) -> str:
        """Every part, whoever wrote it."""
        return "\n".join(p.text for p in self.parts)

    def as_messages(self) -> tuple[dict[str, str], ...]:
        """The wire form a model client would be handed. Origin is deliberately dropped."""
        return tuple({"role": p.role, "content": p.text} for p in self.parts)

    def texts(self) -> tuple[str, ...]:
        return tuple(p.text for p in self.parts)


def assemble(
    *,
    system_prompt: str,
    tool_schemas_text: str,
    history: tuple[Turn, ...],
    state: FoldedState,
    last_refusal: str | None,
    verbatim_turns: int,
    summary_token_cap: int,
) -> AssembledContext:
    """Build the sliding-window context for the next turn.

    ``verbatim_turns`` and ``summary_token_cap`` are read from ``config/`` by the caller
    (:mod:`whetstone_gate.attacker.loop`) and are parameters here — this module contains
    no copy of either.

    **The tool schemas are emitted ONCE PER TURN**, not once per message and not once per
    history entry: §13.3's window is *"the last 6 turns verbatim plus a compact running
    summary capped at 400 tokens, with the tool schemas emitted once per turn"*, and
    repeating a schema block per history entry is one of the two ways the spike reached
    ~300K tokens in a single episode.
    """
    if verbatim_turns < 0:
        raise ValueError("verbatim_turns cannot be negative")
    kept = history[-verbatim_turns:] if verbatim_turns else ()
    parts: list[ContextPart] = [
        ContextPart(Origin.AUTHORED, "system", system_prompt, "attacker_sys.txt"),
        ContextPart(Origin.AUTHORED, "system", tool_schemas_text, "tool schemas (once per turn)"),
        ContextPart(
            Origin.AUTHORED,
            "system",
            render_summary(state, last_refusal, summary_token_cap),
            "deterministic summary (template, never a model call)",
        ),
    ]
    for turn in kept:
        parts.append(
            ContextPart(Origin.ATTACKER, "assistant", turn.attacker_text, f"turn {turn.index}")
        )
        parts.append(
            ContextPart(Origin.WORLD, "tool", turn.tool_result_text, f"turn {turn.index} result")
        )
    return AssembledContext(tuple(parts))
