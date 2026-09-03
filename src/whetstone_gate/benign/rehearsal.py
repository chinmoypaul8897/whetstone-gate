"""**THE DRY-RUN TRANSCRIPT — ⚠️ A FIXTURE, NEVER A MODEL.**

This module turns a :class:`whetstone_gate.benign.catalogue.BenignTask`'s reference call
plan into a list of replies for
:class:`whetstone_gate.driver.clients.TranscriptClient`, so the whole benign harness — the
paired matrix, the blindness scan, the counters, the report — can be driven end to end with
**no provider call of any kind**.

--------------------------------------------------------------------------------------
⚠️ WHAT IT IS NOT, SAID BEFORE ANYTHING ELSE
--------------------------------------------------------------------------------------

`PROCESS.md` §9: *"every evidence pack states what it is NOT."* This is `driver/rehearsal.py`'s
own warning, restated because it applies with more force here:

  * **It is not a model.** It does not read the context it is handed. A benign task
    completes in a dry run because a script said the calls, not because an agent worked out
    what to do.
  * **It measures the HARNESS.** It measures no solver competence, no completion rate, and
    no false-positive rate. What it does prove is that the wiring runs, that the counters
    reconcile, that the pairing invariant holds, and that the refusals fire — which is
    exactly what a dry run is for.
  * **Its token figures are the caller's numbers**, not a provider's. §13.4's
    tokens/episode cannot be measured from here, and this package's dry run therefore
    **refuses to publish any figure at all** — see
    :func:`whetstone_gate.benign.report.refuse_to_publish`.

⚠️ **THE SOLVER'S COMPETENCE IS THE ONE THING A DRY RUN CANNOT SHOW, AND IT IS THE THING
THE COUNTER-METRIC DEPENDS ON.** `INCIDENTS.md` `INC-01` is the attacker-side version: a
loop that never reached the tool where the holes were scored *"0 escapes in 20 episodes"*
and was a broken instrument. The benign mirror is a solver that cannot finish an ordinary
job, whose failures would then read as *"the gate blocked legitimate work"* — or, with the
two counters kept apart as they are here, as a large
``failed_because_it_could_not_solve``. **A reviewer should attack this first.**

--------------------------------------------------------------------------------------
⚠️ WHY THE TRANSCRIPT IS BUILT FROM THE TASK AND NOT WRITTEN OUT
--------------------------------------------------------------------------------------

A transcript typed at the call site would be a **different agent in every test**, and its
amounts would be literals — which is both hard rule 9's hardcoded spec value and a call
that does not match the payment it names. Deriving it from
:attr:`~whetstone_gate.benign.catalogue.BenignTask.plan` means the fixture is a function of
the world the seed produced, and one task's fixture cannot drift from that task's goal.

**PURE.** No I/O, no clock, no network, no randomness.
"""

from __future__ import annotations

import json

from whetstone_gate.benign.catalogue import BenignTask
from whetstone_gate.benign.texts import DONE_MARKER
from whetstone_gate.driver.protocol import ARGUMENTS_KEY, TOOL_KEY


class RehearsalError(RuntimeError):
    """The fixture was asked for something that would make a dry run prove less than it says."""


def reply_for(tool: str, arguments: dict) -> str:
    """One reply in the call grammar :mod:`whetstone_gate.driver.protocol` parses.

    ⚠️ **THE KEYS COME FROM THE PROTOCOL MODULE, NOT FROM STRINGS HERE.**
    :data:`~whetstone_gate.driver.protocol.TOOL_KEY` and
    :data:`~whetstone_gate.driver.protocol.ARGUMENTS_KEY` are that module's own names, and
    they exist there for this reason: *"named rather than repeated, so the parser and the
    grammar string cannot drift apart."* A fixture that spelled them itself could go on
    producing replies the parser had stopped accepting, and every turn would then be counted
    as ``unparsed`` — a dry run that proved the parser rejects things.
    """
    return json.dumps({TOOL_KEY: tool, ARGUMENTS_KEY: arguments}, sort_keys=True)


def transcript_for(task: BenignTask, *, turn_budget: int) -> tuple[tuple[str, int], ...]:
    """The ``(text, total_tokens)`` replies that drive ``task`` to completion, then stop.

    The last reply is :data:`whetstone_gate.benign.texts.DONE_MARKER` with no tool call, so
    the loop exercises its own early-stop path rather than always running to the budget —
    a fixture that always truncated would leave
    :attr:`whetstone_gate.benign.solve.BenignEpisode.truncated` untested in the one
    direction that matters.

    ⚠️ **THE TOKEN FIGURE IS ZERO AND THAT IS DELIBERATE.** A non-zero number here would be
    an invented per-call cost that then appears in a report next to real ones. The driver's
    rehearsal charges ``config/``'s *reservation* per call and says so; this fixture charges
    nothing, so no figure it produces can be mistaken for a measurement. The accounting path
    is still exercised, because :class:`~whetstone_gate.driver.clients.TranscriptClient`
    wraps even a zero in a real ``usage`` block and
    :func:`whetstone_gate.runner.budget.usage_total_tokens` still reads it.

    ⚠️ **A PLAN LONGER THAN THE TURN BUDGET IS A REFUSAL, NOT A TRUNCATION.** Silently
    cutting it would make the task unsolvable for a reason nothing printed, and it would
    land in ``failed_because_it_could_not_solve`` — a fixture defect wearing a finding's
    clothes.
    """
    if not task.plan:
        raise RehearsalError(
            f"task {task.task_id!r} has an empty plan, so the fixture would drive zero "
            f"calls and the task would score as one the gate prevented"
        )
    needed = len(task.plan) + 1
    if needed > turn_budget:
        raise RehearsalError(
            f"task {task.task_id!r} needs {len(task.plan)} call(s) plus one turn to say "
            f"{DONE_MARKER}, which is {needed} turns against a budget of {turn_budget}. "
            f"Refusing rather than cutting the plan: a cut plan fails the task for a reason "
            f"nothing prints, and it would be counted as a failure the solver caused"
        )
    replies = [
        (reply_for(call.tool, dict(call.arguments)), 0) for call in task.plan
    ]
    replies.append((f"{DONE_MARKER} — the work request has been carried out.", 0))
    return tuple(replies)


def longest_transcript(tasks: tuple[BenignTask, ...], *, turn_budget: int) -> int:
    """How many replies the longest task needs. **For sizing a shared client, not a claim.**"""
    if not tasks:
        raise RehearsalError("no tasks were supplied, so there is nothing to rehearse")
    return max(len(transcript_for(task, turn_budget=turn_budget)) for task in tasks)
