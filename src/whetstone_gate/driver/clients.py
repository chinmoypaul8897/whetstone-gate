"""**THE INJECTED MODEL CLIENT — AND THE DRY-RUN CLIENT THAT MAKES NO NETWORK CALL.**

⚠️⚠️ **THIS PACKAGE IMPORTS NO MODEL CLIENT AND NO NETWORK LIBRARY, AND THE ASSERTION IS
MADE TWO WAYS.** ``tests/test_c12_driver.py`` walks the driver's **transitive first-party
imports** with :mod:`ast` *and* scans every module's **raw source text** for the vocabulary
of dynamic reach. **The second half is not belt-and-braces:** `INCIDENTS.md` **INC-51**
measured that ``__import__(…)``, ``importlib.import_module(…)`` and ``getattr(pkg, "name")``
walk straight past an AST import walk — a call expression is not an ``ast.Import`` node —
and made a ``gates/`` module execute a ``scorer/`` predicate while `check_roles` **D1, D2
and D3 all reported PASS**. An AST walk cannot see a dynamic reach; a text scan cannot see
semantics; **neither is the guarantee alone.**

The consequence is the one `PROCESS.md` §8 asks for: **a build session cannot spend a
lane's quota by accident**, because there is nothing in this package that could open a
socket. The client is a **parameter**, typed as a two-method Protocol, and the driver never
learns what is behind it.

--------------------------------------------------------------------------------------
⚠️ THE CLIENT RETURNS THE PROVIDER'S OWN `usage` BLOCK, AND THAT IS WHY IT IS A NEW PROTOCOL
--------------------------------------------------------------------------------------

:class:`whetstone_gate.attacker.loop.ModelClient` returns **text alone**, which is right for
C6 — the attacker loop has no business knowing what a call cost. But hard rule 12's
accounting is *"tokens are taken from the API's OWN `usage` field, NEVER estimated"* (golden
8), so the driver needs the block itself. :class:`MeteredModelClient` returns
:class:`ModelReply`, which carries the text **and** the raw ``usage`` mapping, and
:mod:`whetstone_gate.driver.episode` adapts it down to C6's narrower protocol at the
boundary.

⚠️ **THE ADAPTER IS THE ONLY PLACE THE TWO MEET, AND IT DOES NOT ESTIMATE.**
:func:`whetstone_gate.runner.budget.usage_total_tokens` is what reads the block, it reads
``total_tokens`` **and nothing else**, and a reply whose usage block lacks it is a
**refusal** — never a reconstruction from ``prompt_tokens + completion_tokens``, because
providers differ on whether the total includes reasoning or cached-read tokens.

--------------------------------------------------------------------------------------
⚠️ THE DRY-RUN CLIENT: DETERMINISTIC, OFFLINE, AND HONEST ABOUT WHAT IT IS NOT
--------------------------------------------------------------------------------------

:class:`TranscriptClient` replays a **caller-supplied list of replies**, in order, with a
**caller-supplied** token count on each. It is how the operator rehearses the whole pilot —
20 episodes, ledgers, checkpoints, resume, the token accounting — **without a provider**.

**What it is:** a deterministic stand-in that exercises every line of the driver except the
provider call itself.
**What it is NOT, said plainly** (`PROCESS.md` §9: *"every evidence pack states what it is
NOT"*): it is **not a model**, its token counts are **the caller's numbers and not a
provider's**, and a dry run therefore measures **the harness**, never
`CONTEXT.md` §13.4's tokens/episode. ⚠️ **A dry run may never select the N branch**, and
:mod:`whetstone_gate.driver.pilot` refuses to hand a dry run's figures to
:func:`whetstone_gate.runner.n_rule.select_n` for exactly that reason.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Protocol, Sequence


class DriverClientError(RuntimeError):
    """The injected client was asked for something it cannot honestly supply."""


class RateLimited(RuntimeError):
    """The provider answered **429**. The window is already spent.

    ⚠️ **RAISED, NOT RETURNED, AND IT CARRIES NO DESTINATION.** `PROCESS.md` §8 and
    `CLAUDE.md` §4: *"A 429 means the window is already spent: STOP and report — never retry
    into another lane."* There is no field on this exception naming a lane to move to, so
    *"never retry into another lane"* is a property of the type rather than a rule a caller
    has to remember — the same shape
    :meth:`whetstone_gate.runner.budget.LaneBudget.record_429` gives it one layer down.
    """


class ProviderFailed(RuntimeError):
    """The provider returned an error that is **not** a 429.

    Counted under :data:`whetstone_gate.runner.episodes.PROVIDER_ERROR`, never swallowed:
    hard rule 11 counts *"retries, fallbacks, skipped cases, or missing traces"* alike.
    """


@dataclass(frozen=True)
class ModelReply:
    """One provider reply: the text, and **the provider's own usage block**.

    ``usage`` is passed through **verbatim**. This class does not read it, does not add its
    parts together and does not fill anything in — golden 8's rule is that the accumulator
    reads ``total_tokens`` *"and nothing else"*, and a wrapper that helpfully synthesised a
    total would put an estimate where a billed figure belongs.
    """

    text: str
    usage: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise DriverClientError(
                f"a model reply's text must be a string; got {type(self.text).__name__}"
            )
        if not isinstance(self.usage, Mapping):
            raise DriverClientError(
                "a model reply must carry the provider's own usage block as a mapping. "
                "Hard rule 12 and golden 8: tokens are taken from the API's OWN usage "
                "field, NEVER estimated"
            )


class MeteredModelClient(Protocol):
    """The one thing the driver needs from a provider. **A protocol, never an import.**

    Two methods, because the attacker and the gate judge are called with different shapes
    and `CONTEXT.md` §13.3.2 puts them on their own lanes with their own budgets:

      * :meth:`complete_attacker` — C6's message list, at `config/`'s temperature.
      * :meth:`complete_judge` — C9's ``(system, user)`` pair.

    A caller supplies anything with this shape: the operator's real provider client in a
    scored run, :class:`TranscriptClient` in a dry run. **This package never learns which.**
    """

    def complete_attacker(
        self, *, messages: tuple[dict[str, str], ...], temperature: float
    ) -> ModelReply:
        ...

    def complete_judge(self, *, system: str, user: str) -> ModelReply:
        ...


@dataclass
class TranscriptClient:
    """A deterministic offline client. **It opens nothing and it computes nothing.**

    ``attacker_replies`` and ``judge_replies`` are consumed in order. Each is a
    ``(text, total_tokens)`` pair, and the ``total_tokens`` is written into a ``usage`` block
    so that the accounting path under test is **exactly** the one a provider would drive —
    :func:`whetstone_gate.runner.budget.usage_total_tokens` reading ``total_tokens`` off a
    mapping. A dry run that fed the accumulator a bare integer would leave the one function
    hard rule 12 depends on untested.

    ⚠️ **EXHAUSTION IS A REFUSAL, NEVER A REPEAT OF THE LAST REPLY.** A transcript that runs
    out mid-episode is a transcript that does not describe the episode it was handed to, and
    silently looping would make a dry run of 20 episodes prove something about 1.

    ``rate_limit_at`` makes the client raise :class:`RateLimited` on the *n*-th attacker
    call, which is how golden 8 fixture D's shape is driven end to end through the real
    wiring rather than against the accumulator alone. ``None`` means it never fires.
    """

    attacker_replies: Sequence[tuple[str, int]]
    judge_replies: Sequence[tuple[str, int]] = field(default_factory=tuple)
    rate_limit_at: int | None = None

    attacker_calls: int = 0
    judge_calls: int = 0

    def complete_attacker(
        self, *, messages: tuple[dict[str, str], ...], temperature: float
    ) -> ModelReply:
        """The next attacker reply. ``messages`` and ``temperature`` are **accepted and
        recorded, never interpreted** — a transcript that behaved differently by prompt
        would be a model, and this is deliberately not one."""
        self.attacker_calls += 1
        if self.rate_limit_at is not None and self.attacker_calls == self.rate_limit_at:
            raise RateLimited(
                f"transcript client: simulated 429 on attacker call {self.attacker_calls}"
            )
        return self._next(self.attacker_replies, self.attacker_calls, "attacker")

    def complete_judge(self, *, system: str, user: str) -> ModelReply:
        """The next judge reply. Same contract, same refusal on exhaustion."""
        self.judge_calls += 1
        return self._next(self.judge_replies, self.judge_calls, "judge")

    def _next(
        self, replies: Sequence[tuple[str, int]], position: int, role: str
    ) -> ModelReply:
        if position > len(replies):
            raise DriverClientError(
                f"the transcript has {len(replies)} {role} reply/replies and call "
                f"{position} was asked for. A transcript is exhausted, not repeated: "
                f"looping the last reply would make a 20-episode dry run prove something "
                f"about one episode"
            )
        text, total = replies[position - 1]
        return ModelReply(text=text, usage={"total_tokens": total})


def cycle(replies: Iterable[tuple[str, int]], times: int) -> tuple[tuple[str, int], ...]:
    """``replies`` repeated ``times`` over, as a flat tuple. **A test and rehearsal helper.**

    Written here rather than at each call site so that a rehearsal transcript for a whole
    pilot is one expression, and so that :class:`TranscriptClient`'s refusal on exhaustion
    stays a real refusal rather than something a caller works around with a generator.
    """
    if times < 0:
        raise DriverClientError(f"cannot repeat a transcript {times} times")
    materialised = tuple(replies)
    return tuple(reply for _ in range(times) for reply in materialised)
