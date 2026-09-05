"""⚠️⚠️ **A LANE STOP INSIDE THE GATE JUDGE'S CALL, ON A JUDGED ARM, THROUGH A REAL MATRIX.**

`docs/reviews/REVIEW_C14_FLOOR_1.md` **`B-1`** (verdict **FAIL**), `INCIDENTS.md` **`INC-171`**,
and the architect's ruling at `QUESTIONS.md` **`Q-226`**, verbatim in part:

    "⚠️ A `LaneStopped` raised inside a judge call MUST BE BOOKED AND REPORTED, exactly as one
    raised inside an attacker call already is. The run must print a reconciling denominator and
    every remaining episode must be counted and categorised (hard rule 11)."

--------------------------------------------------------------------------------------
⚠️⚠️ WHY THIS FILE EXISTS BESIDE `test_c14_unexpected_escape.py` RATHER THAN INSIDE IT
--------------------------------------------------------------------------------------

That file asserts `Q-200`'s floor and asserts it correctly — **on arm 1, whose matrix has no
gate and no judge**, over a fake transport whose reply `driver/protocol.py:parse_call` refuses.
The review measured the consequence: **384 of 384 turns counted `unparsed`**, and
``gate.decide``, ``candidate_action``, ``world.call`` and ``ledger_build.append_call`` never
executed once. Its five unit tests build a bare ``_MeteredCall`` with ``lane="gemma-26b"``,
**which is the judge lane** — and there is no judge, no :class:`ModelGate` and no ``gate.decide``
anywhere in the file. **The lane name creates the appearance of judge coverage without any.**

⚠️ **SO THIS FILE'S WHOLE CONTRIBUTION IS THE ARM AND THE TURN SHAPE.** It drives
``load_pilot(arm="2")`` — a **judged** arm — with attacker replies that genuinely parse as
on-surface tool calls, and :func:`_assert_the_judge_was_really_driven` refuses to let any test
here pass without the gate having actually decided turns. `INC-138`'s species of vacuous green
is the failure mode this guards against, and `INC-160`'s `Missing` field is the general form:
*"a test whose double is more permissive than the real collaborator proves the caller compiles,
not that the system works."* **Here it was the MATRIX that was more permissive than the sweep.**

--------------------------------------------------------------------------------------
⚠️ ZERO PROVIDER CALLS, ASSERTED RATHER THAN INTENDED
--------------------------------------------------------------------------------------

Every test drives the **real** :class:`~whetstone_gate.driver.clients.MeteredProviderClient`
over a **fake** :data:`~whetstone_gate.driver.clients.Transport`, the real ``_PacedClient`` and
the real ``execute`` dispatch loop, and the ``_no_provider_call`` fixture replaces the real
transport with a function that **raises**. The reference-attacker and gate-judge lanes are
reserved (`PROCESS.md` §8, `CLAUDE.md` §4) and no session may spend on them. Every output root
is a ``tmp_path``; nothing under ``evals/`` is read or written.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from whetstone_gate.driver import clients as driver_clients
from whetstone_gate.driver import episode as driver_episode
from whetstone_gate.driver import pilot as pilot_module
from whetstone_gate.driver import run as driver_run
from whetstone_gate.gates import judge as gates_judge
from whetstone_gate.runner import episodes as ep_module
from whetstone_gate.runner import usage as runner_usage
from whetstone_gate.runner.buckets import BucketError
from whetstone_gate.runner.budget import Ceilings

#: The judge call the injected fault fires on. One episode is 20 turns and therefore **20 judge
#: calls**, so call 25 is **episode 2, turn 5** — after a whole episode has completed and long
#: before the last, which is what makes *"the run continues"* and *"later episodes complete"*
#: real assertions rather than vacuous ones. ⚠️ A property of this fixture, not a spec value:
#: hard rule 9 is about `config/`-owned figures and this is a test's own arithmetic.
_FAULT_AT_JUDGE_CALL = 25

#: The arm under test. ⚠️ **2, 2S AND 3 ARE THE JUDGED ARMS AND THEY ARE 90 OF THE SWEEP'S 150
#: EPISODES** (`Q-218`). Arm 2 is the cheapest of the three to drive — arm 2S additionally sends
#: the folded state and arm 3 a different preamble, and neither difference touches the metered
#: judge call this file is about.
_JUDGED_ARM = "2"

#: The one line of :data:`~whetstone_gate.gates.judge.JUDGE_REPLY_INSTRUCTION` the fake transport
#: looks for to tell a **judge** request from an **attacker** one. ⚠️ **READ OFF THE REAL
#: CONSTANT, NEVER RETYPED**: a copy would keep matching after the real instruction changed, and
#: the fault would silently start firing on attacker calls instead — which is the arm-1 mistake
#: this file exists because of, in a new costume.
_JUDGE_MARKER = gates_judge.JUDGE_REPLY_INSTRUCTION.splitlines()[1]

#: ⚠️ **THE ATTACKER'S REPLY PARSES, AND THAT IS THE POINT.** `fetch_payments` is on §8.6a's
#: six-name surface, so the executor takes the third branch — ``candidate_action`` and then
#: ``gate.decide`` — instead of returning at ``unparsed``. The existing C14 file's fixture text
#: returns ``parsed=False`` and never reaches the gate at all.
_ON_SURFACE_TOOL_CALL = json.dumps({"tool": "fetch_payments", "arguments": {"count": 2}})

#: The judge's reply. ``DENY`` parses under `gates/judge.py:parse_reply`'s grammar, so the gate
#: returns a real verdict and the turn is counted ``decided``. A ``DENY`` keeps the world out of
#: the loop, which makes every turn identical and the arithmetic below checkable by hand.
_JUDGE_DENIES = "DENY"


@pytest.fixture
def _no_provider_call(monkeypatch):
    """⚠️ **ZERO PROVIDER CALLS, ASSERTED.** The real transport is replaced by one that raises."""

    def refuse(*_args, **_kwargs):  # pragma: no cover - the point is that it never runs
        raise AssertionError(
            "a test reached the REAL provider transport. No session may spend on these "
            "lanes (PROCESS.md S8 LANE RESERVATION)"
        )

    monkeypatch.setattr(driver_clients, "_http_post", refuse)
    return refuse


@pytest.fixture
def _key_names(monkeypatch):
    """Both key NAMES set to obvious non-secrets, so the client's presence check passes.

    ⚠️ No real key is read, printed or committed by this suite, and these values are not
    credential-shaped.
    """
    monkeypatch.setenv("GOOGLE_API_KEY", "not-a-real-key-google")
    monkeypatch.setenv("GROQ_API_KEY", "not-a-real-key-groq")


def _ok_body(url: str, text: str, total: int) -> bytes:
    """A 200 in whichever provider's shape the URL belongs to, carrying ``text``."""
    if url.startswith(driver_clients._GOOGLE_BASE):
        return json.dumps(
            {
                "candidates": [{"content": {"parts": [{"text": text}], "role": "model"}}],
                "usageMetadata": {
                    "promptTokenCount": 100,
                    "candidatesTokenCount": 20,
                    "totalTokenCount": total,
                },
            }
        ).encode("utf-8")
    return json.dumps(
        {
            "choices": [{"message": {"role": "assistant", "content": text}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": total},
        }
    ).encode("utf-8")


@dataclasses.dataclass
class _TransportThatFaultsOnOneJUDGECall:
    """A fake transport that answers 200 for everything **except one judge call**.

    ⚠️ **THE FAULT IS RAISED FROM THE TRANSPORT FRAME, WHICH IS THE FRAME THAT KILLED THE
    CALIBRATION.** `INC-159`'s traceback bottoms out inside ``clients.py:542 urlopen(...)`` —
    the callable this class stands in for — and `INC-161`'s 429 arrived as a status from the
    same place. An injection at the client or the gate layer would test a shape neither failure
    had.

    ⚠️ **ATTACKER CALLS ARE NEVER FAULTED.** A `LaneStopped` out of an *attacker* call was
    already booked correctly before `B-1` — it happens **outside** ``_Executor.execute``, so the
    turn was never counted and the identity held. The whole finding is that a stop out of a
    **judge** call happens **inside** it, between ``attempted += 1`` and the categorisation.

    ⚠️ **IT ANSWERS NORMALLY AGAIN AFTERWARDS**, so *"the run continued"* is distinguishable
    from *"the run stopped for some other reason"*.
    """

    raises: BaseException | None = None
    """Raised from inside the transport on the armed judge call. `INC-159`'s shape."""

    answers_status: int | None = None
    """Returned as an HTTP status on the armed judge call instead. `INC-161`'s shape — a 429
    and a 500 are **statuses**, and the client turns them into `RateLimited` / `ProviderFailed`
    itself, which is the path a hand-raised exception would skip."""

    fault_at_judge_call: int = _FAULT_AT_JUDGE_CALL

    judge_calls: int = 0
    attacker_calls: int = 0
    faults_raised: int = 0

    @property
    def armed(self) -> bool:
        return self.raises is not None or self.answers_status is not None

    def __call__(self, url, body, headers):
        if _JUDGE_MARKER.encode("utf-8") in body:
            self.judge_calls += 1
            if self.armed and self.judge_calls == self.fault_at_judge_call:
                self.faults_raised += 1
                if self.answers_status is not None:
                    return driver_clients.HttpResponse(
                        status=self.answers_status, body=b'{"error":"injected"}'
                    )
                raise self.raises
            return driver_clients.HttpResponse(
                status=200, body=_ok_body(url, _JUDGE_DENIES, 111)
            )
        self.attacker_calls += 1
        return driver_clients.HttpResponse(
            status=200, body=_ok_body(url, _ON_SURFACE_TOOL_CALL, 222)
        )


def _a_clock_that_does_not_wait():
    """A monotonic clock that advances an hour per read, so the pacer never actually sleeps.

    ⚠️ **THE PACER IS STILL BUILT AND STILL DRIVEN** — `Q-179`(3) requires that of every run —
    and its arithmetic runs in full. Only the wall clock is virtual, which is the same device
    ``driver/run.py:_pacing_clock`` uses for a dry run.
    """
    state = {"t": 0.0}

    def clock() -> float:
        state["t"] += 3600.0
        return state["t"]

    return clock


def _drive_the_judged_matrix(transport, out_root: Path):
    """Drive the **whole pilot matrix on arm 2** over ``transport``. Returns the ``RunResult``.

    ⚠️ The matrix is the real one, read from `config/`: 20 episodes of 20 turns. It is not
    shrunk for the test, because a matrix smaller than the one that ships is exactly the
    permissive double `H-2` failed this chunk for.
    """
    matrix = pilot_module.load_pilot(arm=_JUDGED_ARM)
    attacker_lanes = sorted({matrix.lane_for(key) for key in matrix.keys()})
    client = driver_clients.MeteredProviderClient.for_lane_names(
        attacker_lanes=attacker_lanes,
        judge_lane=matrix.judge_lane,
        transport=transport,
    )
    request = driver_run.RunRequest(
        matrix=matrix,
        out_root=out_root,
        # ⚠️ Deliberately generous, so that nothing in these tests stops for a CEILING the
        # test did not mean to exercise. The ceiling-stop path is exercised by its own cause
        # (a 429 stops the lane) rather than by starving this one.
        ceilings=Ceilings(call_ceiling=2000, token_ceiling=20_000_000),
        s3_binding="authorization-is-the-payment",
        spend_real_tokens=True,
        sanctioned_lanes=frozenset(attacker_lanes) | {matrix.judge_lane},
        allow_absent_corpus=True,
    )
    return driver_run.execute(
        request,
        client=client,
        clock=_a_clock_that_does_not_wait(),
        sleep=lambda _seconds: None,
        liveness_probe=lambda _lane: 200,
    )


def _episode_count() -> int:
    return pilot_module.load_pilot(arm=_JUDGED_ARM).episode_count


def _usage_rows_under(out_root: Path) -> list[dict]:
    rows: list[dict] = []
    usage_dir = out_root.joinpath(*runner_usage.USAGE_DIR)
    for path in sorted(usage_dir.glob("*.jsonl")) if usage_dir.is_dir() else ():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _assert_the_judge_was_really_driven(result, transport) -> None:
    """⚠️⚠️ **THE ANTI-VACUITY GUARD, AND IT IS THE WHOLE REASON THIS FILE IS SEPARATE.**

    `H-2`: the existing suite's arm-1 matrix counted **384 of 384 turns `unparsed`** and never
    executed ``gate.decide`` once, so its headline property was asserted on episodes that never
    reached a gate. Every test here calls this, and it fails loudly if the same thing happens
    again — a fixture that stopped parsing, a marker that stopped matching, an arm that lost its
    gate.
    """
    assert transport.attacker_calls > 0, "no attacker call was made at all"
    assert transport.judge_calls >= _FAULT_AT_JUDGE_CALL, (
        f"only {transport.judge_calls} judge call(s) were made, so the gate judge was barely "
        f"reached and nothing about a JUDGED arm was measured (H-2)"
    )
    unparsed = sum(episode.counts.unparsed for episode in result.episodes)
    decided = sum(episode.counts.decided for episode in result.episodes)
    assert unparsed == 0, (
        f"{unparsed} turn(s) were counted UNPARSED, so the attacker's reply stopped parsing "
        f"and the gate was never asked. That is exactly the arm-1 fixture H-2 failed this "
        f"chunk for"
    )
    assert decided > 0, "no turn was ever decided by a gate, so gate.decide never ran"


def _assert_the_denominator_RECONCILES_AND_PRINTS(result) -> None:
    """Hard rule 11, end to end: every episode counted, categorised, **and printed**."""
    result.denominator.reconcile()
    counted = (
        result.denominator.completed
        + result.denominator.truncated
        + result.denominator.not_started
    )
    assert result.denominator.attempted == counted == _episode_count(), (
        f"the run denominator does not account for the whole matrix: "
        f"attempted={result.denominator.attempted} counted={counted} "
        f"matrix={_episode_count()}"
    )
    for episode in result.episodes:
        # ⚠️ The per-EPISODE identity too, not only the per-RUN one. This is the assertion that
        # used to raise DenominatorError out of `execute` instead of being reachable at all.
        episode.counts.reconcile()
    assert result.report, "the run produced no report"


def _the_booked_episode(result, cause: str):
    booked = [episode for episode in result.episodes if episode.cause == cause]
    assert len(booked) == 1, (
        f"expected exactly one episode booked under {cause}; got "
        f"{[(e.key.slug, e.cause) for e in result.episodes]}"
    )
    return booked[0]


# ======================================================================================
# ⚠️ THE RULING, ON THE ARM IT WAS FALSE ON
# ======================================================================================


@pytest.mark.parametrize(
    "escaping",
    [
        TimeoutError("The read operation timed out"),
        RuntimeError("something nobody wrote an except clause for"),
    ],
    ids=["TimeoutError", "bare-RuntimeError"],
)
def test_an_ESCAPE_INSIDE_THE_JUDGE_CALL_IS_BOOKED_AND_THE_RUN_CONTINUES(
    escaping, tmp_path, _no_provider_call, _key_names
):
    """⚠️⚠️ **`B-1` REPRODUCED ON A JUDGED ARM, THEN SURVIVED.**

    ⚠️ **THIS BODY IS RED ON THE PRE-FIX CODE, AND RED IN THE ONE WAY THAT MATTERS**:
    ``driver_run.execute`` raises ``DenominatorError: turn counts do not reconcile: 5 attempted
    against 4 decided`` from ``episode.py:reconcile`` and never returns, so ``result`` is never
    bound and every assertion below is unreachable. **It is not possible for both the pre-fix
    and the post-fix code to pass this body.**

    ⚠️ **THE `RuntimeError` CASE IS THE ONE THAT KEEPS THE FLOOR A FLOOR.** `Q-200`: *"a fourth
    name would be the same defect wearing a new label."* It is named in no client, no cause
    table and no ruling, and it must be booked identically to the `TimeoutError` that cost the
    calibration.
    """
    transport = _TransportThatFaultsOnOneJUDGECall(raises=escaping)
    result = _drive_the_judged_matrix(transport, tmp_path)

    # (0) the fault really fired, in a judge call, exactly once.
    assert transport.faults_raised == 1, (
        f"the injected fault never fired ({transport.judge_calls} judge calls), so nothing "
        f"was measured -- INC-138's species of vacuous green"
    )
    _assert_the_judge_was_really_driven(result, transport)

    # (1) the episode is BOOKED under Q-200's own named cause.
    booked = _the_booked_episode(result, ep_module.UNEXPECTED_ERROR)
    assert ep_module.UNEXPECTED_ERROR in ep_module.UNFINISHED_CAUSES

    # (2) ⚠️ THE ABANDONED TURN IS COUNTED AND CATEGORISED. Q-226; hard rule 11.
    assert booked.counts.abandoned == 1, (
        f"the turn abandoned inside gate.decide was not booked: {booked.counts}"
    )
    assert booked.counts.attempted == booked.counts.categorised(), (
        "the per-episode identity does not hold on the very episode the stop hit"
    )

    # (3) ⚠️ THE RUN CONTINUED AND LATER EPISODES COMPLETED. This is the half of Q-200 that
    #     was false on this arm: `execute` died and every remaining episode went unattempted.
    index = result.episodes.index(booked)
    after = result.episodes[index + 1 :]
    assert after, "the faulted episode was the last dispatched; 'the run continues' is untested"
    assert any(episode.cause is None for episode in after), (
        f"no episode completed after the fault: {[(e.key.slug, e.cause) for e in after]}"
    )
    assert len(result.episodes) == _episode_count()

    # (4) the whole denominator reconciles and is rendered.
    _assert_the_denominator_RECONCILES_AND_PRINTS(result)

    # (5) ⚠️ THE CAUSE **AND ITS COUNT** REACH THE PRINTED REPORT. An outcome booked and never
    #     printed is the same silence in a new place.
    assert f"{ep_module.UNEXPECTED_ERROR:<26}: 1" in result.denominator.render()
    assert ep_module.UNEXPECTED_ERROR in result.report
    assert "ABANDONED mid-turn   : 1" in result.report, (
        "the abandoned turn is counted but never printed, which is hard rule 11's own failure "
        "one field over"
    )

    # (6) ⚠️ THE CALL IS COUNTED, WITH ZERO TOKENS — `Q-200`(a)'s argued choice, asserted where
    #     it is visible: the abandoned turn adds one settled judge call over the decided turns,
    #     because the request may already have been billed and a ceiling that binds EARLIER is
    #     the safe side. The `PACER_REFUSED` test asserts the opposite for its own branch.
    assert booked.judge_calls == booked.counts.decided + 1, (
        f"{booked.judge_calls} judge calls settled against {booked.counts.decided} decided "
        f"turns; the escaping call must be COUNTED (Q-200(a)) and it was not"
    )

    # (7) ⚠️ THE RECORD CARRIES THE EXCEPTION'S TYPE NAME AND NOTHING ELSE FROM IT (INC-147).
    errors = [
        row for row in _usage_rows_under(tmp_path)
        if row.get("outcome") == runner_usage.OUTCOME_ERROR
    ]
    assert any(row.get("error_type") == type(escaping).__name__ for row in errors), (
        f"no usage row carries error_type={type(escaping).__name__!r}; got "
        f"{[row.get('error_type') for row in errors]}"
    )


def test_a_429_ON_THE_JUDGE_LANE_STAYS_A_429_AND_THE_RUN_STOPS_AND_REPORTS(
    tmp_path, _no_provider_call, _key_names
):
    """⚠️⚠️ **THE ROW TO READ TWICE. HARD RULE 12 SAYS A 429 MEANS *STOP AND REPORT*.**

    On a judged arm it did neither: it crashed. And `PROTOCOL.md` §2.1 puts the reference
    attacker **and** the gate judge for arms 2/2S/3 on the same lane, so
    ``lane_states[lane]`` and ``lane_states[judge_lane]`` are the **same `LaneBudget` object** —
    when the shared window is spent, whichever role is offered next raises, and on a judged arm
    the judge's raise is inside ``gate.decide``. `INC-161` records a real 429 on that exact lane
    at the calibration's **second call**.

    ⚠️ **AND IT IS THE CAUSE-LAUNDERING TEST.** The stop arrives at the executor **already
    booked** by the meter that raised it. If the fix had wrapped, re-raised or re-categorised
    it, a spent window would be published as an unexplained fault with its accounting already
    settled — the one way this change could make the record *worse* than the crash it replaces.

    ⚠️ **RED ON THE PRE-FIX CODE AS `DenominatorError` out of `execute`.**
    """
    transport = _TransportThatFaultsOnOneJUDGECall(answers_status=429)
    result = _drive_the_judged_matrix(transport, tmp_path)

    assert transport.faults_raised == 1
    _assert_the_judge_was_really_driven(result, transport)

    # ⚠️ (1) THE CAUSE IS UNCHANGED. Not UNEXPECTED_ERROR. Not PROVIDER_ERROR.
    booked = _the_booked_episode(result, ep_module.RATE_LIMIT_429)
    assert booked.cause != ep_module.UNEXPECTED_ERROR, (
        "a 429 on the judge lane was relabelled as an unexplained fault. Q-226 forbids it by "
        "name and b01edaa's guard exists for it one layer down"
    )
    assert booked.counts.abandoned == 1
    assert booked.counts.attempted == booked.counts.categorised()

    # (2) ⚠️ THE RUN STOPS AS THE CAUSE REQUIRES — a 429 means the window is genuinely spent —
    #     AND EVERY REMAINING EPISODE IS STILL COUNTED AND CATEGORISED (hard rule 11).
    assert len(result.episodes) < _episode_count(), (
        "the lane did not stop on a 429, so the run kept spending a window hard rule 12 says "
        "is already gone"
    )
    assert result.denominator.not_started > 0
    _assert_the_denominator_RECONCILES_AND_PRINTS(result)

    # (3) the cause and its count reach the printed report, and so does the abandoned turn.
    printed = result.denominator.render()
    assert ep_module.RATE_LIMIT_429 in printed
    assert f"{ep_module.RATE_LIMIT_429:<26}: {result.denominator.attempted - 1}" in printed, printed
    assert "ABANDONED mid-turn   : 1" in result.report

    # (4) and it is booked as a RATE_LIMITED usage row, not an ERROR one.
    outcomes = {row.get("outcome") for row in _usage_rows_under(tmp_path)}
    assert "RATE_LIMITED" in outcomes, outcomes


def test_a_PACER_REFUSAL_INSIDE_THE_JUDGE_CALL_KEEPS_ITS_OWN_CAUSE(
    tmp_path, _no_provider_call, _key_names
):
    """⚠️ **`Q-179`(2)'s `PACER_REFUSED` IS A THIRD DISTINCT CAUSE ON THE SAME PATH.**

    `BucketError` is raised by ``run.py:_PacedClient._pace``, which runs **inside** the
    ``call()`` the meter wraps, so on a judged arm it too abandons a counted turn. Booking it
    under anything but ``PACER_REFUSED`` would publish **our own pacer's** refusal as the
    provider's answer, which is the confusion `INC-160` and `Q-201` are both about.

    ⚠️ **RED ON THE PRE-FIX CODE AS `DenominatorError` out of `execute`.**
    """
    transport = _TransportThatFaultsOnOneJUDGECall(
        raises=BucketError("a bucket refusal is a WAIT, not an abort")
    )
    result = _drive_the_judged_matrix(transport, tmp_path)

    assert transport.faults_raised == 1
    _assert_the_judge_was_really_driven(result, transport)

    booked = _the_booked_episode(result, ep_module.PACER_REFUSED)
    assert booked.counts.abandoned == 1
    _assert_the_denominator_RECONCILES_AND_PRINTS(result)
    assert f"{ep_module.PACER_REFUSED:<26}: 1" in result.denominator.render()
    assert "ABANDONED mid-turn   : 1" in result.report

    # ⚠️ ZERO CALLS AND ZERO TOKENS ARE CHARGED FOR IT — the pacer refuses BEFORE the wire, so
    #    no provider saw the request. That is the one place this branch differs from the floor,
    #    and `Q-201` is explicit that `INC-160`'s fix does not blur it. Every OTHER judge call
    #    in that episode is one decided turn, so the abandoned turn added nothing.
    assert booked.judge_calls == booked.counts.decided, (
        f"the pacer refusal was charged as a call ({booked.judge_calls} settled against "
        f"{booked.counts.decided} decided turns), which overstates the spend hard rule 12 "
        f"exists to bound"
    )


def test_a_RESUMED_JUDGED_ARM_FINISHES_THE_MATRIX_AND_STILL_PRINTS_A_DENOMINATOR(
    tmp_path, _no_provider_call, _key_names
):
    """⚠️⚠️ **THE REVIEW'S OWN PRECONDITION, IN ONE TEST: A JUDGED ARM PLUS A RESUME.**

    `Q-144`'s ruling says of `OF-240` that it *"cannot fire on this run … it is merely not on
    this run's path"*, naming that precondition — and `INC-171`'s `Missed` field is that two
    sessions read the sentence as reassurance. `INC-166` is the same precondition firing in
    ``render`` hours earlier. **The sweep is the first block with both, and it is the only block
    whose numbers are published.**

    The first invocation takes a 429 inside a judge call: one episode completes, one is
    truncated and booked, the lane stops and the rest are never dispatched. The second
    invocation is a **resume** over the same output root with a healthy transport, and must
    finish the matrix and print a reconciling denominator that counts the skipped episodes.

    ⚠️ **RED ON THE PRE-FIX CODE, AND AT THE FIRST INVOCATION**: it raises `DenominatorError`
    out of `execute`, so there is no checkpoint to resume from and the resume never happens.
    """
    stopped = _drive_the_judged_matrix(
        _TransportThatFaultsOnOneJUDGECall(answers_status=429), tmp_path
    )
    _assert_the_denominator_RECONCILES_AND_PRINTS(stopped)
    published = sorted(p.stem for p in tmp_path.joinpath("evals", "checkpoints").glob("*.json"))
    assert len(published) == len(stopped.episodes) >= 2, (
        f"the stopped run published {len(published)} checkpoint(s) for "
        f"{len(stopped.episodes)} dispatched episode(s); a resume needs both to agree"
    )

    healthy = _TransportThatFaultsOnOneJUDGECall()
    resumed = _drive_the_judged_matrix(healthy, tmp_path)

    assert healthy.faults_raised == 0
    _assert_the_judge_was_really_driven(resumed, healthy)

    # (1) ⚠️ EVERY EPISODE OF THE MATRIX IS ACCOUNTED FOR, SKIPPED ONES INCLUDED (INC-110).
    assert sorted(resumed.already_complete) == published
    assert len(resumed.episodes) == _episode_count() - len(published)
    _assert_the_denominator_RECONCILES_AND_PRINTS(resumed)

    # (2) ⚠️ AND THE REPORT IS ACTUALLY PRINTED ON A RESUMED JUDGED ARM. INC-166: the OF-240
    #     refusal used to escape `render` and take the whole denominator with it.
    assert "RESUME AND IDEMPOTENCE" in resumed.report
    assert f"episodes already checkpointed, SKIPPED : {len(published)}" in resumed.report
    assert "PER-EPISODE TURN ACCOUNTING" in resumed.report

    # (3) the resumed episodes are clean, and the abandoned counter prints at ZERO for them —
    #     PROCESS.md S9: every zero prints, or a reader cannot tell absent from unmeasured.
    assert all(episode.cause is None for episode in resumed.episodes)
    assert all(episode.counts.abandoned == 0 for episode in resumed.episodes)
    assert "ABANDONED mid-turn   : 0" in resumed.report


# ======================================================================================
# ⚠️ AND THE DETECTOR IS STILL A DETECTOR
# ======================================================================================


def test_reconcile_STILL_REFUSES_A_TURN_THAT_REACHED_NO_CATEGORY_AT_ALL():
    """⚠️⚠️ **`Q-207`'s OPTION 4 WAS TO CATCH THE `DenominatorError`, AND IT WAS REFUSED.**

    This is the **one** assertion in the program that notices a turn leaving the record without
    saying so (hard rule 11). Booking the abandoned turn into a category is not the same thing
    as silencing the check, and only a test can tell the two apart: if a later session
    "fixes" a reconciliation failure by widening this identity or by swallowing the refusal,
    this goes red.

    ⚠️ **HONESTLY LABELLED: THIS ONE IS NOT A BEHAVIOURAL RED-TO-GREEN AND IS NOT PRESENTED AS
    ONE.** Measured on the pre-fix tree it fails on the **message** assertion below — the old
    refusal reads *"a turn in none of the three categories"* — and had it got past that line the
    ``abandoned=`` keyword would be a ``TypeError``. Neither is the `DenominatorError` escaping
    `execute`, which is what the five tests above are red with. **This test is a guard against a
    future regression, not evidence that `B-1` was fixed.**
    """
    counts = driver_episode.EpisodeCounts(attempted=2, decided=1)
    with pytest.raises(ep_module.DenominatorError) as refusal:
        counts.reconcile()
    assert "abandoned" in str(refusal.value), (
        "the refusal message does not name the fourth category, so an operator reading it "
        "cannot tell which identity was broken"
    )

    # ⚠️ AND A TURN THAT **WAS** BOOKED RECONCILES. Both halves, or the test proves only that
    #    the identity is strict and not that it is satisfiable.
    driver_episode.EpisodeCounts(attempted=2, decided=1, abandoned=1).reconcile()
    assert driver_episode.EpisodeCounts(attempted=2, decided=1, abandoned=1).categorised() == 2
