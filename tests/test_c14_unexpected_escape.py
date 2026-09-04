"""⚠️⚠️ **THE FLOOR: ANY EXCEPTION ESCAPING THE MODEL CALL IS BOOKED, AND THE RUN CONTINUES.**

`QUESTIONS.md` **`Q-200`**, RULED 2026-09-04, verbatim in part:

    "⚠️ ANY exception escaping the model call is BOOKED AS A COUNTED, NAMED OUTCOME AND THE RUN
    CONTINUES TO THE NEXT EPISODE. Not a longer list of caught types — a catch-all that books
    whatever escapes. Three named types have now escaped in three days and the third destroyed
    an unrepeatable run; a fourth name would be the same defect wearing a new label."

`INCIDENTS.md` **`INC-159`** is the third escape and it is what this file exists because of: the
single-shot arm-1 calibration's attempt 2 died at `2026-09-04T14:41:51Z`, **13 calls and 56,855
tokens into episode 1 of 30**, on a `TimeoutError` raised by the SSL read inside
`driver/clients.py:_http_post`. No report, no denominator, 29 episodes never attempted.
`INC-160` is the fourth, found while placing this floor.

--------------------------------------------------------------------------------------
⚠️ WHY THE SECOND TEST USES A BARE `RuntimeError`, AND WHY THAT IS THE POINT
--------------------------------------------------------------------------------------

A file that tested only `TimeoutError` would close the **instance** — which is precisely the
mistake `INC-159`'s `Missed` field records twice, once for `Q-174`'s `DriverClientError` and once
for `Q-179`(2)'s `BucketError`. **Both fixes added one more name to a catch list, and the class
arrived a third time and killed a single-shot run.** So the second test raises a type named in no
client, no cause table and no ruling. **It goes red the moment the floor is narrowed back into a
list**, which is the only property that distinguishes a floor from a fourth name.

--------------------------------------------------------------------------------------
⚠️ ZERO PROVIDER CALLS, ASSERTED RATHER THAN INTENDED
--------------------------------------------------------------------------------------

Every test here drives the **real** :class:`~whetstone_gate.driver.clients.MeteredProviderClient`
over a **fake** :data:`~whetstone_gate.driver.clients.Transport`, and the ``_no_provider_call``
fixture replaces the real one with a function that raises. The reference-attacker lanes are
reserved (`PROCESS.md` §8) and no session may spend on them.

⚠️ **A TRUE `--dry-run` HAS NO TRANSPORT TO FAKE**, because it dispatches through a
``TranscriptClient`` and never constructs a provider client at all. What is driven here is the
**pilot matrix** — the same multi-episode matrix, the same `execute` dispatch loop, the same pacer
(`Q-179`(3) made the pacer build on every run) — over a transport that answers from memory. It
costs nothing and it reaches the frame that killed the calibration, which a dry run cannot.
"""

from __future__ import annotations

import dataclasses
import datetime
import json
from pathlib import Path

import pytest

from whetstone_gate.driver import clients as driver_clients
from whetstone_gate.driver import episode as driver_episode
from whetstone_gate.driver import pilot as pilot_module
from whetstone_gate.driver import run as driver_run
from whetstone_gate.runner import episodes as ep_module
from whetstone_gate.runner import usage as runner_usage
from whetstone_gate.runner.buckets import BucketError
from whetstone_gate.runner.budget import Ceilings, LaneBudget
from whetstone_gate.runner.episodes import EpisodeKey

#: The call at which the injected fault fires. Chosen so it lands **after** the first episode's
#: 20 turns and **before** the last, which is what makes "later episodes still complete" a real
#: assertion rather than a vacuous one. ⚠️ It is a property of this fixture, not a spec value —
#: hard rule 9 is about `config/`-owned figures and this is a test's own arithmetic.
_FAULT_AT_CALL = 25


# ======================================================================================
# The fixtures. ⚠️ Deliberately this file's own, not imported from `test_c12_driver.py`:
# a helper shared with another suite can be changed there and silently change what this
# file measures, and this file is the guardrail for a defect that cost a single-shot run.
# ======================================================================================


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


def _google_ok(total=1234):
    return json.dumps(
        {
            "candidates": [{"content": {"parts": [{"text": "the reply"}], "role": "model"}}],
            "usageMetadata": {
                "promptTokenCount": 1000,
                "candidatesTokenCount": 200,
                "totalTokenCount": total,
            },
        }
    ).encode("utf-8")


def _groq_ok(total=987):
    return json.dumps(
        {
            "choices": [{"message": {"role": "assistant", "content": "the reply"}}],
            "usage": {"prompt_tokens": 900, "completion_tokens": 50, "total_tokens": total},
        }
    ).encode("utf-8")


@dataclasses.dataclass
class _TransportThatFaultsOnce:
    """A fake transport that answers 200 for every call **except one**, where it RAISES.

    ⚠️ **THE FAULT IS RAISED FROM THE TRANSPORT, WHICH IS THE FRAME THAT KILLED THE
    CALIBRATION.** `INC-159`'s traceback bottoms out inside
    ``clients.py:542 urlopen(...)`` — i.e. inside the callable this class stands in for. An
    injection at the client or the episode layer would be testing a shape the failure did not
    have.

    ⚠️ **IT ANSWERS NORMALLY AGAIN AFTERWARDS.** A transport that stayed broken could not
    distinguish *"the run continued"* from *"the run stopped for another reason"*, and
    continuing is half of what `Q-200` ruled.
    """

    fault: BaseException
    fault_at: int = _FAULT_AT_CALL
    calls: int = 0
    faults_raised: int = 0

    def __call__(self, url, body, headers):
        self.calls += 1
        if self.calls == self.fault_at:
            self.faults_raised += 1
            raise self.fault
        is_google = url.startswith(driver_clients._GOOGLE_BASE)
        return driver_clients.HttpResponse(
            status=200, body=_google_ok() if is_google else _groq_ok()
        )


def _liveness_answers_200(_lane: str) -> int:
    """`Q-193`: a real-shaped run refuses without a liveness probe, so one is injected.

    ⚠️ **AN ADDED ARGUMENT, NOT A LOOSENED ASSERTION.** The refusal itself is pinned in
    ``tests/test_arch_cal_prep.py``; a probe dispatched through the fake transport here would
    consume a reply this fixture budgeted for an episode and shift `_FAULT_AT_CALL`.
    """
    return 200


def _run_the_matrix_with(fault: BaseException, tmp_path: Path):
    """Drive the whole pilot matrix over a transport that faults once. Returns
    ``(result, transport)``."""
    transport = _TransportThatFaultsOnce(fault=fault)
    matrix = pilot_module.load_pilot(arm="1")
    attacker_lanes = sorted({matrix.lane_for(key) for key in matrix.keys()})
    client = driver_clients.MeteredProviderClient.for_lane_names(
        attacker_lanes=attacker_lanes,
        judge_lane=matrix.judge_lane,
        transport=transport,
    )
    request = driver_run.RunRequest(
        matrix=matrix,
        out_root=tmp_path,
        ceilings=Ceilings(call_ceiling=400, token_ceiling=2_000_000),
        s3_binding="authorization-is-the-payment",
        spend_real_tokens=True,
        sanctioned_lanes=frozenset(attacker_lanes) | {matrix.judge_lane},
        allow_absent_corpus=True,
    )
    result = driver_run.execute(
        request,
        client=client,
        clock=_a_clock_that_does_not_wait(),
        sleep=lambda _seconds: None,
        liveness_probe=_liveness_answers_200,
    )
    return result, transport


def _a_clock_that_does_not_wait():
    """A monotonic clock that advances an hour per read, so the pacer never actually sleeps.

    ⚠️ **THE PACER IS STILL BUILT AND STILL DRIVEN** — `Q-179`(3) requires that of every run,
    including a rehearsal — and its arithmetic runs in full. Only the wall clock is virtual,
    which is the same device ``driver/run.py:_pacing_clock`` uses for a dry run.
    """
    state = {"t": 0.0}

    def clock() -> float:
        state["t"] += 3600.0
        return state["t"]

    return clock


def _assert_the_ruling_holds(result, transport, out_root, *, expected_type_name: str):
    """`Q-200`'s five requirements, asserted as five separate statements.

    ⚠️ **THE FIRST ONE HAS NO `assert`, AND THAT IS DELIBERATE.** *"`execute` returns rather
    than raising"* is proved by this function being reachable at all: against the pre-floor
    code ``_run_the_matrix_with`` never returns, ``result`` is never bound, and every
    assertion below is unreachable. `INC-138` is this project's own precedent for writing that
    sentence down rather than leaving it to a reader.
    """
    # (0) the fault really fired. Without this the whole test could pass vacuously.
    assert transport.faults_raised == 1, (
        f"the injected fault never fired ({transport.calls} calls made), so nothing was "
        f"measured -- INC-138's species of vacuous green"
    )

    # (1) the affected episode is booked with its OWN named cause.
    booked = [e for e in result.episodes if e.cause == ep_module.UNEXPECTED_ERROR]
    assert len(booked) == 1, (
        f"expected exactly one episode booked under {ep_module.UNEXPECTED_ERROR}; got "
        f"{[(e.key.slug, e.cause) for e in result.episodes]}"
    )
    assert ep_module.UNEXPECTED_ERROR in ep_module.UNFINISHED_CAUSES, (
        "a cause outside UNFINISHED_CAUSES cannot be printed in the denominator, which is "
        "hard rule 11's whole requirement"
    )

    # (2) ⚠️ THE RUN CONTINUED, AND LATER EPISODES COMPLETED. This is the half of Q-200 that
    #     the calibration lost: 29 episodes were never attempted.
    index = result.episodes.index(booked[0])
    after = result.episodes[index + 1 :]
    assert after, "the faulted episode was the last dispatched; 'the run continues' is untested"
    assert any(e.cause is None for e in after), (
        f"no episode completed after the fault: {[(e.key.slug, e.cause) for e in after]}"
    )
    assert len(result.episodes) == matrix_episode_count(), (
        "the run did not attempt every episode in the matrix"
    )

    # (3) the cause APPEARS IN THE PRINTED DENOMINATOR WITH ITS COUNT.
    printed = result.denominator.render()
    assert f"{ep_module.UNEXPECTED_ERROR:<26}: 1" in printed, printed
    assert ep_module.UNEXPECTED_ERROR in result.report

    # (4) and the denominator still RECONCILES.
    result.denominator.reconcile()
    counted = (
        result.denominator.completed
        + result.denominator.truncated
        + result.denominator.not_started
    )
    assert result.denominator.attempted == counted == matrix_episode_count()

    # (5) ⚠️ THE RECORD CARRIES THE EXCEPTION'S TYPE NAME. `Q-200`, and INC-147's
    #     prefix-anchored redaction scan is why it may not carry the message.
    rows = _usage_rows_under(out_root)
    errors = [r for r in rows if r.get("outcome") == runner_usage.OUTCOME_ERROR]
    assert errors, "the booked call wrote no usage row at all"
    assert any(r.get("error_type") == expected_type_name for r in errors), (
        f"no usage row carries error_type={expected_type_name!r}; got "
        f"{[r.get('error_type') for r in errors]}"
    )


def matrix_episode_count() -> int:
    return pilot_module.load_pilot(arm="1").episode_count


def _usage_rows_under(out_root: Path) -> list[dict]:
    rows: list[dict] = []
    usage_dir = out_root.joinpath(*runner_usage.USAGE_DIR)
    for path in sorted(usage_dir.glob("*.jsonl")) if usage_dir.is_dir() else ():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


# ======================================================================================
# ⚠️ THE TWO TESTS THE RULING ORDERS
# ======================================================================================


def test_a_TimeoutError_FROM_THE_TRANSPORT_IS_BOOKED_AND_THE_RUN_CONTINUES(
    tmp_path, _no_provider_call, _key_names
):
    """⚠️⚠️ **`INC-159` REPRODUCED, THEN SURVIVED.**

    The exact exception, from the exact frame, at the exact shape: a `TimeoutError` raised
    inside the transport partway through a multi-episode matrix.

    ⚠️ **THIS BODY IS RED ON THE PRE-FLOOR CODE, AND RED IN THE ONE WAY THAT MATTERS** —
    ``driver_run.execute`` raises `TimeoutError` and never returns, which is byte-for-byte
    what happened at `2026-09-04T14:41:51Z`. It is not possible for both the pre-floor and
    post-floor code to pass this body.
    """
    result, transport = _run_the_matrix_with(
        TimeoutError("The read operation timed out"), tmp_path
    )
    _assert_the_ruling_holds(
        result, transport, tmp_path, expected_type_name="TimeoutError"
    )


def test_a_BARE_RuntimeError_NOBODY_NAMED_IS_BOOKED_THE_SAME_WAY(
    tmp_path, _no_provider_call, _key_names
):
    """⚠️⚠️ **THE TYPE NOBODY PREDICTED — WHICH IS THE ENTIRE POINT OF THE RULING.**

    `RuntimeError` is named in no ``except`` clause on this path, in no member of
    :data:`~whetstone_gate.runner.episodes.UNFINISHED_CAUSES`, and in no ruling. `Q-200`:
    *"a fourth name would be the same defect wearing a new label."*

    ⚠️ **THIS TEST IS WHAT MAKES THE FIX A FLOOR RATHER THAN A LIST.** If a later session
    narrows the catch-all back to named types, the sibling `TimeoutError` test above may well
    stay green while this one goes red. **That asymmetry is the guardrail.**
    """
    result, transport = _run_the_matrix_with(
        RuntimeError("something nobody wrote an except clause for"), tmp_path
    )
    _assert_the_ruling_holds(
        result, transport, tmp_path, expected_type_name="RuntimeError"
    )


# ======================================================================================
# ⚠️ THE THREE PROPERTIES THE RULING ATTACHED, EACH ASSERTED RATHER THAN ASSUMED
# ======================================================================================


def _metered(on_usage) -> driver_episode._MeteredCall:
    return driver_episode._MeteredCall(
        lane="gemma-26b",
        budget=LaneBudget(
            model="gemma-26b",
            ceilings=Ceilings(call_ceiling=600, token_ceiling=4_800_000),
        ),
        reservation_tokens=3000,
        on_usage=on_usage,
    )


@pytest.mark.parametrize("escaping", [KeyboardInterrupt, SystemExit])
def test_the_floor_DOES_NOT_SWALLOW_KeyboardInterrupt_OR_SystemExit(escaping):
    """⚠️ **`Q-200`: "DO NOT swallow a KeyboardInterrupt or a SystemExit."**

    Both derive from `BaseException` and not from `Exception`, so a floor spelled
    ``except Exception`` cannot see them — but *"it happens to be true"* and *"it is asserted"*
    are different things, and only the second survives someone widening the clause to
    ``except BaseException`` to be thorough. `runner/episodes.py` already declares an
    ``INTERRUPTED`` cause for an operator stop; a floor that booked one as an episode outcome
    would make Ctrl-C **unable to stop a 32-hour sweep**.
    """
    metered = _metered(lambda *_a, **_k: None)

    def boom():
        raise escaping("the operator stopped the run")

    with pytest.raises(escaping):
        metered.run(boom)


def test_the_booked_record_carries_THE_TYPE_NAME_AND_NEVER_THE_MESSAGE():
    """⚠️⚠️ **`INC-147`: `runner/redaction.py`'s KEY SCAN IS PREFIX-ANCHORED**, so a
    credential embedded in a longer string passes it — and *"a provider error message quoting
    the credential it rejected"* is that module's own stated reason for existing. `INC-148`
    measured a whole credential getting through that scan in code written the same hour to
    carry provider errors.

    So the floor stores ``type(exc).__name__`` and **nothing else from the exception**. A type
    name is a Python identifier; it cannot contain a credential. This test raises an exception
    whose message is deliberately key-shaped and asserts that not one byte of it is booked.
    """
    booked: list[tuple] = []
    metered = _metered(lambda *args, **kwargs: booked.append((args, kwargs)))
    secret_shaped = "provider rejected AIzaSyD-EXAMPLE-NOT-A-REAL-KEY-000000000000"

    def boom():
        raise TimeoutError(secret_shaped)

    with pytest.raises(driver_episode.LaneStopped) as stopped:
        metered.run(boom)

    assert stopped.value.cause == ep_module.UNEXPECTED_ERROR
    assert booked, "nothing was booked, so hard rule 11 counted nothing"
    flat = repr(booked)
    assert "TimeoutError" in flat, flat
    assert secret_shaped not in flat, (
        "the exception's MESSAGE reached the booked record. INC-147: the redaction scan is "
        "prefix-anchored and would not have caught a credential inside it"
    )
    assert "AIzaSy" not in flat


def test_the_floor_DOES_NOT_RETRY_AND_DOES_NOT_STOP_THE_LANE():
    """⚠️ **`Q-200`'s two negatives, both asserted.**

    *"IT DOES NOT RETRY THE CALL. A read timeout may already have been billed AND may already
    have mutated the world."* — so the callable is invoked **exactly once**.

    *"IT DOES NOT STOP THE LANE. A 429 stops a lane because the window is genuinely spent; a
    transient network failure is not that, and a run that dies on one is a run that can never
    finish."* — so ``budget.stopped`` stays **False** and the next episode is dispatchable.
    """
    attempts = {"n": 0}
    metered = _metered(lambda *_a, **_k: None)

    def boom():
        attempts["n"] += 1
        raise TimeoutError("the read operation timed out")

    with pytest.raises(driver_episode.LaneStopped):
        metered.run(boom)

    assert attempts["n"] == 1, f"the call was made {attempts['n']} times; the ruling forbids a retry"
    assert not metered.budget.stopped, (
        "the lane STOPPED on a transient fault. Q-200: a 429 stops a lane because the window "
        "is spent; this is not that"
    )
    assert metered.budget.rate_limited == 0, "a timeout is not a 429 and must not be counted as one"


# ======================================================================================
# ⚠️ INC-160 — THE FOURTH INSTANCE, WHICH LIVED INSIDE THE FIX FOR THE SECOND
# ======================================================================================


def test_INC160_the_BucketError_branch_BOOKS_THROUGH_A_REAL_UsageLog(tmp_path):
    """⚠️⚠️ **`INC-160`: `Q-179`(2)'s OWN FIX COULD NOT BOOK ITS OUTCOME.**

    The branch passed ``episodes.PACER_REFUSED`` to ``usage.append``, whose ``OUTCOMES`` are
    exactly ``("OK", "RATE_LIMITED", "ERROR")`` — so it raised ``UsageError``, **from inside an
    ``except`` handler**, which escapes `run`, `run_one_episode` and `execute` exactly as the
    ``BucketError`` it was installed to contain.

    ⚠️ **THE SINK HERE IS A REAL `UsageLog` WRITING TO A REAL DIRECTORY, AND THAT IS THE WHOLE
    TEST.** `INC-160`'s `Missing` field: every existing test of this branch injects a stub sink
    that accepts any string, so the assertion *"the pacer refusal is booked"* was true of the
    double and false of the program. A test whose double is more permissive than the real
    collaborator proves the caller compiles, not that the system works.
    """
    log = runner_usage.UsageLog(root=tmp_path / "evals" / "usage")
    key = EpisodeKey(block="cal", arm="1", seed_or_task="2201", attacker_model="gemma-26b")
    sink = driver_run._usage_sink(
        log,
        key,
        date="2026-09-04",
        now=lambda: datetime.datetime(2026, 9, 4, tzinfo=datetime.timezone.utc),
    )
    metered = _metered(sink)

    def boom():
        raise BucketError("a bucket refusal is a WAIT, not an abort")

    with pytest.raises(driver_episode.LaneStopped) as stopped:
        metered.run(boom)

    # ⚠️ THE CAUSE IS UNCHANGED. Q-201: only the usage OUTCOME moved; the episode is still
    #    booked, counted and printed under PACER_REFUSED, which is Q-179(2)'s ruling.
    assert stopped.value.cause == ep_module.PACER_REFUSED

    rows = _usage_rows_under(tmp_path)
    assert len(rows) == 1, f"expected exactly one row; got {rows}"
    assert rows[0]["outcome"] in runner_usage.OUTCOMES, (
        f"{rows[0]['outcome']!r} is not a declared usage outcome, which is INC-160 exactly"
    )
    assert rows[0]["error_type"] == "BucketError", rows[0]
    assert rows[0]["total_tokens"] == 0, "the pacer refuses BEFORE the wire; no provider saw it"
    # ⚠️ And no CALL is charged either -- the request was never sent. That is the one place
    #    this branch differs from the floor above, and INC-160's fix does not blur it.
    assert metered.calls_settled == 0


def test_every_declared_cause_that_reaches_a_usage_row_IS_A_DECLARED_USAGE_OUTCOME():
    """⚠️ **THE GENERAL FORM OF `INC-160`, ASSERTED ONCE SO THE NEXT ONE CANNOT SHIP.**

    There are **three** string vocabularies in this program — `episodes.py`'s causes,
    `usage.py`'s outcomes, `scorer/drops.py`'s categories — and `INC-160` is a cause that
    reached an outcome parameter. `episodes.py`'s module docstring warns about drift between
    one of the three pairs and **this is the pair nobody wrote the warning for.**

    This asserts the two vocabularies are **disjoint**, which is the fact that makes the
    confusion detectable at all: if they ever overlap, a cause smuggled into an outcome
    parameter would start passing validation and the next `INC-160` would be silent instead of
    loud. ⚠️ **It is not a claim that they should be merged.** `Q-201` records why they are
    separate and proposes the join table; it is the architect's to install.
    """
    overlap = set(ep_module.UNFINISHED_CAUSES) & set(runner_usage.OUTCOMES)
    assert not overlap, (
        f"the cause and outcome vocabularies now overlap on {sorted(overlap)}. A cause passed "
        f"to usage.append would validate by accident, and INC-160 would have been silent"
    )
