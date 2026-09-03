"""**THE BENIGN LOOP — an agent trying to finish a job, one model call per turn.**

--------------------------------------------------------------------------------------
⚠️ IT IS NOT `attacker/loop.py` WITH THE ATTACKS REMOVED, AND IT COULD NOT BE
--------------------------------------------------------------------------------------

:func:`whetstone_gate.attacker.loop.run_episode` reads its system prompt from
``data/attacker_sys.txt`` **inside the function** and seeds every turn from a pinned attack
corpus. Neither is a parameter, so it cannot be handed a different objective; and if it
could, deleting the corpus and the tradecraft paragraph would leave an agent with **no goal
at all** — `INCIDENTS.md` `INC-01`'s broken instrument, whose flattering zero here would
read *"the gate refused no legitimate work"*.

So this is a separate loop, and what it shares with C6 is deliberate and narrow:

  * **§13.3's sliding window**, via :func:`whetstone_gate.attacker.context.assemble`.
    ⚠️ **Shared on purpose, and this is the one import a reviewer should challenge first.**
    The window is *mandatory, not an optimisation* — the spike burned ~300K tokens in one
    episode by resending history — and, more importantly here, **both loops must be shown
    the same window discipline and the same tool schemas**. Writing a second assembler
    would let the two drift in what a model sees, and a benign solver shown a different
    context than the attacker would confound the very comparison §12.1 puts side by side.
    Hard rule 8's *"written twice, on purpose"* is scoped to ``gates/`` ↔ ``scorer/`` and
    to nothing else.
  * **The six-name tool surface and the call grammar**, via
    :mod:`whetstone_gate.driver.protocol` — byte-identical to what the attacker is handed,
    because a difference there would be a difference in capability rather than in intent.

**What is not shared:** the system prompt, the objective, the corpus (there is none), and
the notion of success. This loop's success is
:attr:`whetstone_gate.benign.catalogue.BenignTask.end_state` reading the world.

--------------------------------------------------------------------------------------
⚠️ EVERY ASSEMBLED CONTEXT IS KEPT, BECAUSE THE BLINDNESS GUARD READS THEM
--------------------------------------------------------------------------------------

:attr:`BenignEpisode.contexts` holds **the object that would have been sent, for every
turn**. :mod:`whetstone_gate.benign.blindness` scans those, not this module's source: a
source scan proves somebody intended blindness, and the assembled bytes are what a model
would actually have read.

**PURE of the filesystem, the clock, the network and randomness.** The client is injected,
the texts arrive as arguments, and the world, gate and ledger arrive built.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from whetstone_gate.attacker.context import (
    AssembledContext,
    FoldedState as SummaryState,
    Turn,
    assemble,
)
from whetstone_gate.benign.catalogue import BenignTask
from whetstone_gate.benign.constants import BenignConstants
from whetstone_gate.benign.executor import BenignExecutor
from whetstone_gate.benign.texts import DONE_MARKER, benign_system_prompt, work_request
from whetstone_gate.driver.clients import MeteredModelClient
from whetstone_gate.driver.protocol import parse_call
from whetstone_gate.runner.budget import usage_total_tokens


class BenignSolverError(RuntimeError):
    """The loop was asked for something it will not guess. Always a refusal."""


class SolverClient(Protocol):
    """The one thing this loop needs from a model. **A protocol, never an import.**

    Deliberately the same shape as
    :class:`whetstone_gate.attacker.loop.ModelClient` — text in, text out, temperature
    explicit — so that the operator's real provider client and
    :class:`whetstone_gate.driver.clients.TranscriptClient` both satisfy it through the same
    adapter the driver already uses. ⚠️ **This package imports no model client and opens no
    socket**, and ``tests/test_c12_benign.py`` asserts that two ways: a transitive AST walk
    over first-party imports, **and** a raw-source scan for the vocabulary of dynamic reach.
    The second is not belt-and-braces — `INCIDENTS.md` **INC-51** measured
    ``importlib.import_module`` walking straight past an AST walk while `check_roles` D1, D2
    and D3 all printed PASS.
    """

    def complete(self, *, messages: tuple[dict[str, str], ...], temperature: float) -> str:
        ...


@dataclass(frozen=True)
class WindowSettings:
    """§13.3's sliding-window mechanics. ⚠️ **A DECLARED CLASS B SHARE — see `Q-156`.**

    These two come from ``attacker.context_window_turns_verbatim`` and
    ``attacker.context_summary_max_tokens``, and the sharing is a **Class B implementation
    choice recorded with its rationale** rather than a config read this package pretends is
    its own. The distinction from the two values in
    :class:`whetstone_gate.benign.constants.BenignConstants` is the one that matters:

      * **``turn_budget`` and ``temperature`` are part of the MEASUREMENT.** §12.3's paired
        definition is *"same task, same seed, same solver, same temperature"*. Reading the
        attacker's would silently pre-register the counter-metric at figures nobody chose
        for it, so they are the caller's and have no default.
      * **These two are the WINDOW.** They decide how much history a model is shown, and
        §13.3 requires both loops to use the same discipline. A second pair of numbers here
        would let the benign solver see more or less history than the attacker, which is a
        difference in what the two agents *could* do — and it would not be visible in any
        published figure.
    """

    verbatim_turns: int
    summary_token_cap: int

    def __post_init__(self) -> None:
        if self.verbatim_turns <= 0:
            raise BenignSolverError(
                f"verbatim_turns must be positive; got {self.verbatim_turns}. A window of "
                f"zero turns is an agent with no memory, which cannot finish a multi-step "
                f"job and would score as work the gate refused"
            )
        if self.summary_token_cap <= 0:
            raise BenignSolverError(
                f"summary_token_cap must be positive; got {self.summary_token_cap}"
            )


@dataclass
class MeteredSolverClient:
    """Adapts a :class:`~whetstone_gate.driver.clients.MeteredModelClient` down to
    :class:`SolverClient`, accumulating the provider's **own** token figures on the way.

    ⚠️ **THE TOKENS COME FROM THE PROVIDER'S ``usage`` BLOCK AND ARE NEVER ESTIMATED.**
    Hard rule 12 and golden 8: :func:`whetstone_gate.runner.budget.usage_total_tokens` reads
    ``total_tokens`` **and nothing else**, and a reply whose usage block lacks it is a
    **refusal** rather than a reconstruction from ``prompt_tokens + completion_tokens`` —
    providers differ on whether the total includes reasoning or cached-read tokens. This is
    the same one function the driver's own accounting path drives, deliberately: a second
    reader here would be a second place an estimate could get in.

    ⚠️ **IT CALLS ``complete_attacker``, AND THE NAME IS THE PROTOCOL'S, NOT A CLAIM ABOUT
    THIS AGENT.** :class:`MeteredModelClient`'s two methods are *"C6's message list"* and
    *"C9's ``(system, user)`` pair"* — a **shape** distinction, not a role one. The benign
    solver is a message-list caller, so it uses that method. Renaming it is C12-DRIVER's
    fence, and `OPEN_FINDINGS.md` carries the observation rather than this package
    inventing a third method the driver would not know about.

    ⚠️⚠️ **``lane`` IS REQUIRED AND HAS NO DEFAULT, AND THAT IS THE WHOLE POINT.**
    `QUESTIONS.md` **Q-173**, RULED 2026-09-04; `INCIDENTS.md` **INC-130**. `Q-161` made
    ``lane`` a required, undefaulted argument on :class:`MeteredModelClient`'s two methods, and
    this adapter called one of them **without** it — so every benign episode raised
    ``TypeError`` and twenty tests went red. ⚠️ **THE ACCOMMODATION WAS REFUSED AGAIN HERE:**
    defaulting the lane — on the protocol, on ``TranscriptClient``, or on this adapter — would
    have turned a loud break into a silent one, and `Q-173` records that *"a loud break is
    detectable, a silent accommodation is not"*. The lane is **passed**, from the one place that
    knows it, and a caller that does not know its lane cannot construct this.

    ⚠️ **IT IS THE BENIGN SOLVER'S OWN LANE AND NOT THE ATTACKER'S**, even though the protocol
    method is named ``complete_attacker`` — the method name is a **shape** distinction (C6's
    message list), which this class's docstring already says above. `whetstone_gate.benign.shell`
    supplies :data:`whetstone_gate.benign.manifest.SOLVER_LANE`.
    """

    inner: MeteredModelClient
    lane: str
    calls: int = 0
    tokens: int = 0

    def complete(self, *, messages: tuple[dict[str, str], ...], temperature: float) -> str:
        self.calls += 1
        reply = self.inner.complete_attacker(
            messages=messages, temperature=temperature, lane=self.lane
        )
        self.tokens += usage_total_tokens(reply.usage)
        return reply.text


@dataclass(frozen=True)
class TurnRecord:
    """One turn: what the solver said, what the tools said back, and what the turn cost.

    ``tokens`` is the running total **after** this turn, read off the provider's own usage
    block. A per-turn delta would be the difference of two figures and would need a
    subtraction nothing checks; the total is what the accumulator actually holds.
    """

    index: int
    solver_text: str
    tool_result_text: str
    tokens: int


@dataclass(frozen=True)
class BenignEpisode:
    """One benign episode, and everything needed to score and audit it.

    ⚠️ **``stopped_early`` IS NOT ``solved``.** The solver says ``DONE`` when it believes the
    job is finished; that is a claim, and it is recorded here so a reviewer can compare it
    against the end-state predicate. The **measurement** is
    :meth:`whetstone_gate.benign.paired.TaskUnderArm.solved`, which reads the world.
    """

    task_id: str
    arm: str
    seed: int
    turns: tuple[TurnRecord, ...]
    contexts: tuple[AssembledContext, ...]
    turn_budget: int
    tokens_spent: int
    stopped_early: bool
    saw_a_denial: bool
    unparsed_turns: int = 0
    off_surface_turns: int = 0

    @property
    def truncated(self) -> bool:
        """Ran out of turns without saying it was done.

        ⚠️ **A truncated benign episode is COUNTED IN THE DENOMINATOR** (hard rule 11), and
        it is a *different* failure from one the gate caused. Both are printed; neither is
        folded into the other.
        """
        return len(self.turns) >= self.turn_budget and not self.stopped_early


def _summary_state(executor: BenignExecutor) -> SummaryState:
    """The gate's seven-field folded state, projected onto §8.6's six.

    ⚠️ **``authorizations`` IS §8.6a's DELIBERATELY-ABSENT SEVENTH FIELD AND IT IS ABSENT
    HERE TOO.** The solver is shown what **it has done** — amounts it moved, receipts it
    used, turns it has left — and never anything that would let it infer a constraint.
    ``idempotency_keys_seen`` is flattened to §8.6a's list of receipt strings out of the
    ``(payment, receipt)`` pairs the kernel folds (`Q-112`).
    """
    state = executor.state
    return SummaryState(
        episode_paise_moved=state.episode_paise_moved,
        per_payment_refunded_paise=dict(state.per_payment_refunded_paise),
        per_payment_captured_paise=dict(state.per_payment_captured_paise),
        idempotency_keys_seen=tuple(
            receipt for _payment, receipt in state.idempotency_keys_seen
        ),
        actions_executed=state.actions_executed,
        turns_remaining=0,
    )


def run_benign_episode(
    *,
    client: MeteredSolverClient,
    executor: BenignExecutor,
    task: BenignTask,
    constants: BenignConstants,
    window: WindowSettings,
    tool_schemas_text: str,
    generic_denial: str,
    arm: str,
    seed: int,
) -> BenignEpisode:
    """Run one benign episode to its turn budget, or until the solver says it is done.

    ⚠️ **EXACTLY ONE MODEL CALL PER TURN**, which is what §13.4's per-episode token budget is
    arithmetic over. A loop that called twice on some turns would make every projected figure
    in that table wrong by an amount nothing printed.

    ⚠️ **A DENIAL IS FOLDED AS §13.3's *LAST DENIAL REASON* AND NOTHING MORE.** The value
    passed on is compared for **byte equality** against §8.6's one generic string, so the
    loop can tell *that* it was refused and can learn nothing about **which arm** or **which
    clause** — the same discipline `QUESTIONS.md` `Q-046` ruled for C6, for the same reason.
    """
    system_prompt = benign_system_prompt(turn_budget=constants.turn_budget)
    request = work_request(goal=task.goal)
    history: list[Turn] = []
    records: list[TurnRecord] = []
    contexts: list[AssembledContext] = []
    last_refusal: str | None = None
    stopped_early = False

    for index in range(constants.turn_budget):
        state = _summary_state(executor)
        state = SummaryState(
            episode_paise_moved=state.episode_paise_moved,
            per_payment_refunded_paise=state.per_payment_refunded_paise,
            per_payment_captured_paise=state.per_payment_captured_paise,
            idempotency_keys_seen=state.idempotency_keys_seen,
            actions_executed=state.actions_executed,
            turns_remaining=constants.turn_budget - index,
        )
        context = assemble(
            # ⚠️ The work request rides on the AUTHORED surface with the role, because it is
            # ours and the blindness scan must see it. A task goal smuggled in as a "world"
            # part would be exempt from the tighter half of the scan by mislabelling.
            system_prompt=f"{system_prompt}\n\n{request}",
            tool_schemas_text=tool_schemas_text,
            history=tuple(history),
            state=state,
            last_refusal=last_refusal,
            verbatim_turns=window.verbatim_turns,
            summary_token_cap=window.summary_token_cap,
            seed_text=None,
        )
        contexts.append(context)

        reply = client.complete(
            messages=context.as_messages(), temperature=constants.temperature
        )
        if not isinstance(reply, str):
            raise BenignSolverError(
                f"the solver client returned {type(reply).__name__}, not str. The loop does "
                f"not coerce: a reply it had to convert is a reply it does not understand"
            )

        # ⚠️ **A REPLY THAT ATTEMPTED A CALL IS NEVER TREATED AS A CLEAN STOP, EVEN IF IT
        # ALSO SAYS DONE.** The first version tested only `not protocol_has_a_call(reply)`,
        # which is False for a MALFORMED call as well as for no call — so a reply carrying
        # a broken tool call plus the word DONE anywhere in its prose skipped the executor
        # entirely: `counts.attempted`, `counts.unparsed` and `turns_run` all stayed 0, and
        # `truncated` stayed False. That is `INCIDENTS.md` `INC-01`'s flattering zero
        # inside the very loop whose executor claims "COUNTED, NEVER SWALLOWED" — and the
        # system prompt itself trains the model to emit DONE. Found by this chunk's own
        # adversarial pass, before its first commit.
        #
        # A brace means the reply tried to make a call. It goes to the executor, which
        # counts it, and only a reply with no call attempt at all is a stop.
        if DONE_MARKER in reply and not protocol_has_a_call(reply) and "{" not in reply:
            stopped_early = True
            records.append(
                TurnRecord(
                    index=index,
                    solver_text=reply,
                    tool_result_text="",
                    tokens=client.tokens,
                )
            )
            break

        tool_result = executor.execute(reply)
        # §13.3's last denial reason: byte equality against the ONE authored constant.
        last_refusal = generic_denial if tool_result == generic_denial else last_refusal
        # ⚠️ ``Turn.attacker_text`` is C6's field name and this loop is not an attacker. The
        # name is the type's, the type is §13.3's window, and renaming it is C6's fence. It
        # is flagged here rather than worked around, because a private copy of the dataclass
        # would put a second window shape in the repository (`OPEN_FINDINGS.md`).
        history.append(
            Turn(index=index, attacker_text=reply, tool_result_text=tool_result)
        )
        records.append(
            TurnRecord(
                index=index,
                solver_text=reply,
                tool_result_text=tool_result,
                tokens=client.tokens,
            )
        )

    return BenignEpisode(
        task_id=task.task_id,
        arm=arm,
        seed=seed,
        turns=tuple(records),
        contexts=tuple(contexts),
        turn_budget=constants.turn_budget,
        tokens_spent=client.tokens,
        stopped_early=stopped_early,
        saw_a_denial=executor.saw_a_denial,
        unparsed_turns=executor.counts.unparsed,
        off_surface_turns=executor.counts.off_surface,
    )


def protocol_has_a_call(text: str) -> bool:
    """Does this reply carry a parseable tool call?

    ⚠️ **A reply may say ``DONE`` *and* call a tool**, and the call wins. A solver that
    signed off while still acting has not finished; treating the marker as terminal would
    drop that action from the record and from every count derived from it.
    """
    return parse_call(text).parsed
