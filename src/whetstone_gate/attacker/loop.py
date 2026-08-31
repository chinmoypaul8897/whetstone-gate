"""The attacker loop — policy-blind, sliding-window, corpus-seeded.

⚠️ **THIS IS `INCIDENTS.md` INC-01's chunk.** The spike's first attacker scored **0
escapes in 20 episodes**, which read as a perfect defence and was a broken instrument: in
**19 of 20** episodes it never called the tool where the holes lived. One paragraph of
policy-agnostic tradecraft took it to **16/20**. That paragraph is ``data/attacker_sys.txt``
and this module is what carries it. **A weak attacker here does not produce a weak result;
it produces a FLATTERING one.**

---

## What this module imports, and what it deliberately does not

**It takes its model client injected and imports none.** There is no ``groq``, no
``google``, no ``openai``, no ``httpx``, no ``requests`` and no ``urllib`` anywhere in
this package, and ``tests/test_c6_attacker.py`` walks the package's transitive first-party
imports and its module source to assert it — so a build or test run **cannot** spend a
lane's quota by accident. `PROCESS.md` §8 reserves the Gemma lanes for the sweep from 31
August and no build session may spend on them.

**It has no gate object.** :class:`ToolExecutor` returns a tool result and nothing else —
no verdict, no arm identity, no clause number. That is not politeness; it is why a policy
leak into the attacker's context is *structurally impossible from this module*, rather
than merely absent today. `CONTEXT.md` §8.6's single generic denial —
identical across arms on ``DENIED`` **and** on ``INDETERMINATE`` — reaches the attacker as
the text of a tool result, exactly like a Razorpay error does, and this module cannot tell
the two apart. Neither can the attacker, which is the point.

**Exactly ONE model call per turn.** `CONTEXT.md` §13.3's budget is 20 requests per
episode and the deterministic summary is what protects it: *"it adds no requests"* is a
claim about a number, so ``tests/test_c6_attacker.py`` asserts the number against the
mock rather than reading the code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from whetstone_gate import config as cfg
from whetstone_gate.attacker import texts
from whetstone_gate.attacker.context import (
    AssembledContext,
    FoldedState,
    Turn,
    assemble,
)
from whetstone_gate.attacker.corpus import (
    CorpusEntry,
    InputProvenance,
    classify_provenance,
    seed_for_turn,
)
from whetstone_gate.attacker.estimate import BudgetComparison, TokenEstimate, estimate_messages


class ModelClient(Protocol):
    """The injected attacker model. **Mocked for every test in this chunk.**"""

    def complete(self, *, messages: tuple[dict[str, str], ...], temperature: float) -> str:
        """Return the attacker's next output as text. One call, one turn."""
        ...


class ToolExecutor(Protocol):
    """The world behind whatever gate is in front of it — opaque to this module.

    It returns the tool result **text** and nothing else. There is no verdict field and no
    arm field, by design: see this module's docstring.
    """

    def execute(self, attacker_text: str) -> str:
        ...


@dataclass(frozen=True)
class TurnRecord:
    """One turn of the ledger's attacker side.

    ⚠️ ``provenance`` and ``corpus_ref`` are `CONTEXT.md` §11.3's instrumented split, and
    they are recorded **from the first episode** because C18 publishes the fraction and a
    fraction cannot be recovered from transcripts that never carried it.
    """

    turn_index: int
    provenance: InputProvenance
    corpus_ref: str | None
    seed_offered_ref: str | None
    attacker_text: str
    tool_result_text: str
    context_estimate: TokenEstimate

    def __post_init__(self) -> None:
        # The one invariant that keeps the published fraction meaningful: a CORPUS turn
        # names its entry, and an IMPROVISED turn names none. Anything else would let a
        # ref go missing while the count stayed the same.
        corpus_turn = self.provenance is InputProvenance.CORPUS
        if corpus_turn != (self.corpus_ref is not None):
            raise ValueError(
                f"turn {self.turn_index}: provenance {self.provenance.value!r} and "
                f"corpus_ref {self.corpus_ref!r} disagree. A CORPUS turn names its entry; "
                f"an IMPROVISED turn names none. CONTEXT.md section 11.3's split is "
                f"computed from these two fields together."
            )


@dataclass(frozen=True)
class EpisodeResult:
    """Everything one episode produced, including what it cost — as an ESTIMATE."""

    records: tuple[TurnRecord, ...]
    model_calls: int
    episode_estimate: TokenEstimate
    budget: BudgetComparison
    contexts: tuple[AssembledContext, ...]

    @property
    def corpus_turns(self) -> int:
        return sum(1 for r in self.records if r.provenance is InputProvenance.CORPUS)

    @property
    def improvised_turns(self) -> int:
        return sum(1 for r in self.records if r.provenance is InputProvenance.IMPROVISED)


@dataclass(frozen=True)
class AttackerSettings:
    """The four `config/` values this loop runs on. **Loaded, never written here.**"""

    turn_budget: int
    verbatim_turns: int
    summary_token_cap: int
    temperature: float
    target_tokens_per_episode: int

    @classmethod
    def from_config(cls) -> AttackerSettings:
        """Read every value through the one loader. No defaults — hard rule 9.

        Each of these is a `CONTEXT.md` §8.6 row and a tripwire registry row, so a
        hardcoded copy anywhere in this package fails
        ``test_no_spec_value_is_hardcoded_in_implementation_source``.
        """
        protocol = cfg.load("protocol")
        return cls(
            turn_budget=protocol.require("attacker.turn_budget"),
            verbatim_turns=protocol.require("attacker.context_window_turns_verbatim"),
            summary_token_cap=protocol.require("attacker.context_summary_max_tokens"),
            temperature=protocol.require("attacker.temperature"),
            target_tokens_per_episode=protocol.require("attacker.target_tokens_per_episode"),
        )


def _seed_hint(entry: CorpusEntry | None) -> str:
    """How a corpus entry is put in front of the attacker.

    It is offered as raw material with no framing that names a policy, a hole or an arm —
    there is nothing here for one to leak from.
    """
    if entry is None:
        return ""
    return f"\nMATERIAL YOU MAY ADAPT OR IGNORE:\n{entry.text}\n"


def run_episode(
    *,
    client: ModelClient,
    executor: ToolExecutor,
    settings: AttackerSettings,
    tool_schemas_text: str,
    corpus_entries: tuple[CorpusEntry, ...],
    fold: "StateFolder",
) -> EpisodeResult:
    """Run one policy-blind episode. **Exactly one model call per turn.**

    ``fold`` recomputes the §8.6 folded state from whatever the executor has done. It is
    injected for the same reason the client is: the ledger is C7's and the world is C4's,
    and this chunk builds neither.
    """
    system_prompt = texts.attacker_system_prompt()
    history: list[Turn] = []
    records: list[TurnRecord] = []
    contexts: list[AssembledContext] = []
    last_refusal: str | None = None
    calls = 0

    for index in range(settings.turn_budget):
        state = FoldedState(
            episode_paise_moved=fold.episode_paise_moved(),
            per_payment_refunded_paise=fold.per_payment_refunded_paise(),
            per_payment_captured_paise=fold.per_payment_captured_paise(),
            idempotency_keys_seen=fold.idempotency_keys_seen(),
            actions_executed=fold.actions_executed(),
            turns_remaining=settings.turn_budget - index,
        )
        seed = seed_for_turn(corpus_entries, index)
        context = assemble(
            system_prompt=system_prompt + _seed_hint(seed),
            tool_schemas_text=tool_schemas_text,
            history=tuple(history),
            state=state,
            last_refusal=last_refusal,
            verbatim_turns=settings.verbatim_turns,
            summary_token_cap=settings.summary_token_cap,
        )
        contexts.append(context)

        # ── THE ONE MODEL CALL OF THIS TURN ──────────────────────────────────────────
        attacker_text = client.complete(
            messages=context.as_messages(), temperature=settings.temperature
        )
        calls += 1

        result_text = executor.execute(attacker_text)
        last_refusal = result_text
        provenance, corpus_ref = classify_provenance(attacker_text, seed)
        records.append(
            TurnRecord(
                turn_index=index,
                provenance=provenance,
                corpus_ref=corpus_ref,
                seed_offered_ref=seed.ref if seed is not None else None,
                attacker_text=attacker_text,
                tool_result_text=result_text,
                context_estimate=estimate_messages(context.texts()),
            )
        )
        history.append(
            Turn(index=index, attacker_text=attacker_text, tool_result_text=result_text)
        )

    episode_estimate = estimate_messages(
        tuple(t for context in contexts for t in context.texts())
    )
    return EpisodeResult(
        records=tuple(records),
        model_calls=calls,
        episode_estimate=episode_estimate,
        budget=BudgetComparison(
            estimated_tokens=episode_estimate.tokens,
            target_tokens=settings.target_tokens_per_episode,
        ),
        contexts=tuple(contexts),
    )


class StateFolder(Protocol):
    """Recomputes `CONTEXT.md` §8.6's folded state. C7's ledger supplies the real one."""

    def episode_paise_moved(self) -> int: ...
    def per_payment_refunded_paise(self) -> dict[str, int]: ...
    def per_payment_captured_paise(self) -> dict[str, int]: ...
    def idempotency_keys_seen(self) -> tuple[str, ...]: ...
    def actions_executed(self) -> int: ...
