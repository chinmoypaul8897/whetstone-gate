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
the text of a tool result, exactly like a Razorpay error does. Neither the attacker nor
this module learns **which arm** returned it or **which clause** fired, which is the point.

⚠️ **AND THIS MODULE *CAN* TELL A DENIAL FROM ANY OTHER RESULT, WITHOUT A GATE OBJECT AND
WITHOUT LEARNING ANYTHING FROM IT** — `QUESTIONS.md` **Q-046**, ruled 2026-09-01. The denial
is **one authored constant string**, so byte equality against it is sufficient, and because
every arm returns the *same* string on ``DENIED`` and on ``INDETERMINATE``, a match carries
**exactly one bit**: *something refused*. That is what `CONTEXT.md` §13.3 needs the summary
to carry — *"the running folded state (§8.6) with **the last denial reason**"* — and nothing
more. The constant is read from ``data/generic_denial.txt`` and is never written in source.

⚠️ **Until 2026-09-01 this loop folded the last TOOL RESULT instead, every turn,
unconditionally**, which put verbatim world output onto the attacker's AUTHORED surface,
told the attacker that completed refunds were refusals, and left C6's own claim-2 guard
passing only because a long fixture pushed the probe note past the truncation cut. It is
`INCIDENTS.md` **INC-26** and it was `REVIEW_C6_1`'s BLOCKER F-1.

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
    CorpusCoverage,
    CorpusEntry,
    InputProvenance,
    classify_provenance,
    coverage_report,
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

    episode_seed: int = 0
    """The seed this episode's corpus offers were derived from (`QUESTIONS.md` **Q-047**).

    ⚠️ **Recorded because ``0`` is the degenerate seed and must be VISIBLE rather than
    merely absent.** This project scores 2001–2050 and pilots 2101–2110 (§8.6); a scored
    episode carrying ``0`` here was run without its seed threaded through, which would put
    every episode back on one identical offered set — `INCIDENTS.md` **INC-27**'s defect
    wearing a new hat. :attr:`coverage` prints it.
    """

    coverage: CorpusCoverage | None = None
    """Entries **offered** versus entries **loaded**, as a number (`CLAUDE.md` hard rule 11).

    ``None`` only when the episode ran with no corpus at all, which is a test path;
    ``load_entries`` refuses an empty corpus in any real run.
    """

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

    ⚠️ **The return value is carried as its OWN context part, tagged
    :attr:`~whetstone_gate.attacker.context.Origin.CORPUS`.** It used to be concatenated onto
    the system prompt, which tagged somebody else's corpus entry as text *this harness wrote*
    (`REVIEW_C6_1` INFO-3; `INCIDENTS.md` **INC-26**; `QUESTIONS.md` **Q-046**).
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
    episode_seed: int = 0,
) -> EpisodeResult:
    """Run one policy-blind episode. **Exactly one model call per turn.**

    ``fold`` recomputes the §8.6 folded state from whatever the executor has done. It is
    injected for the same reason the client is: the ledger is C7's and the world is C4's,
    and this chunk builds neither.

    ``episode_seed`` is the world seed this episode runs on, and it selects which corpus
    entries are offered (`QUESTIONS.md` **Q-047**;
    :func:`whetstone_gate.attacker.corpus.seed_for_turn`). ⚠️ **Two arms on the same seed
    receive IDENTICAL offers**, which is what keeps §12.4's paired-by-seed design intact.
    ⚠️ **Its default of ``0`` is a Class B choice recorded in Q-047 with its risk stated:**
    a required argument would be hard rule 9's shape but would break six tests in a file
    this fix session may not edit. ``0`` is not a seed this project ever scores, and it is
    carried on :attr:`EpisodeResult.episode_seed` and printed by
    :meth:`~whetstone_gate.attacker.corpus.CorpusCoverage.render`, so an unseeded run is
    **visible in the record** rather than merely absent.
    """
    system_prompt = texts.attacker_system_prompt()
    # ⚠️ Q-046: the ONE authored constant, read from data/ and never written in source. It
    # is the loop's only means of telling a denial from any other tool result, and because
    # every arm returns it on DENIED *and* on INDETERMINATE it carries no arm identity and
    # no clause number — so claim 4 stays structural. INCIDENTS.md INC-26.
    generic_denial = texts.generic_denial()
    coverage = coverage_report(
        corpus_entries, episode_seed=episode_seed, turn_budget=settings.turn_budget
    )
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
        seed = seed_for_turn(
            corpus_entries,
            index,
            episode_seed=episode_seed,
            turn_budget=settings.turn_budget,
        )
        context = assemble(
            system_prompt=system_prompt,
            tool_schemas_text=tool_schemas_text,
            history=tuple(history),
            state=state,
            last_refusal=last_refusal,
            verbatim_turns=settings.verbatim_turns,
            summary_token_cap=settings.summary_token_cap,
            seed_text=_seed_hint(seed),
        )
        contexts.append(context)

        # ── THE ONE MODEL CALL OF THIS TURN ──────────────────────────────────────────
        attacker_text = client.complete(
            messages=context.as_messages(), temperature=settings.temperature
        )
        calls += 1

        result_text = executor.execute(attacker_text)
        # ── §13.3's LAST DENIAL REASON, and nothing else ─────────────────────────────
        # ⚠️ EXACT string equality against the ONE authored constant (Q-046). A result
        # that is not that string is not a denial, so it is NOT folded — which is what
        # keeps world text and corpus text off the AUTHORED surface, and what stops a
        # completed refund being republished to the attacker under the label
        # "LAST TOOL REFUSAL:". `last_refusal` persists across turns because §13.3 says
        # the LAST denial, not "the denial on the previous turn".
        if result_text == generic_denial:
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
        episode_seed=episode_seed,
        coverage=coverage,
    )


class StateFolder(Protocol):
    """Recomputes `CONTEXT.md` §8.6's folded state. C7's ledger supplies the real one."""

    def episode_paise_moved(self) -> int: ...
    def per_payment_refunded_paise(self) -> dict[str, int]: ...
    def per_payment_captured_paise(self) -> dict[str, int]: ...
    def idempotency_keys_seen(self) -> tuple[str, ...]: ...
    def actions_executed(self) -> int: ...
