"""**C14 ABORT 3 (`7d4e2fa9`) — the pacer's ADMISSION, replayed against the trace that died.**

`INCIDENTS.md` **INC-161**. The single-shot calibration's attempt 3 stopped on an HTTP 429
after **one** truncated episode; **29 of 30 declared episodes never started.** The cause was
not the limit and not the accounting — both had already been corrected — it was the
**estimate the admission decides on**:

    `INC-143` (2026-09-04)  the reservation is a MEAN, not an upper bound; 7 of 8 pilot
                            calls cost more than it. **Fixed the SETTLE.** Its own fix note:
                            the top-up *"does not explain, and would not have prevented,
                            the pilot's 429"*.
    `Q-191`  (2026-09-04)   TPM is a 60-second SLIDING window, not a refilling bucket.
                            **Fixed the LIMIT.**
    ⚠️ **INC-161**          nothing had fixed the **ADMISSION**. `_pace` still asked the
                            window for room for **3,000** while real calls cost three times
                            that and rise with context. Attempt 3 admitted **8,421** and
                            then **9,037** twenty-six seconds apart — **17,458 against a
                            declared ``tpm`` of 16,000.**

⚠️ **A NEW FILE ON PURPOSE**, for the reason `tests/test_arch_lanes.py` and
`tests/test_arch_cal_build.py` each give in their own headers: `INC-138` is a landed commit
that deleted an assertion while its message said nothing was deleted. A new file makes the
diff *"0 files changed"* for every existing suite, which `git show --numstat` checks and
which cannot be got wrong by hand. **This file changes no existing test, and the AST diff in
`docs/sessions/c14-abort-3.txt` is how that is checked rather than claimed.**

**WHAT THIS FILE PINS**

- **§1 THE TRACE** — the real per-call costs, and their provenance against the artefact.
- **§2 THE ESTIMATOR** — :class:`~whetstone_gate.runner.buckets.ObservedCost`: pure,
  monotone, floored by the figure `config/` already produces, and fed only the provider's
  own ``usage.total_tokens``.
- **§3 ⚠️ THE SPEC, AS A TEST** — the whole 32-call trace driven through the **real**
  ``_PacedClient`` and the **real** ``Buckets``, asserting that **no trailing 60-second
  window ever holds more than ``tpm``**. **RED against the pre-fix pacer at 18,175.**
- **§3b ⚠️ THE ESTIMATE'S LIFETIME** — it is scoped to the **lane**, not the episode,
  because the window it paces against is. And **§3b's last test publishes the residual**:
  a cold lane can still overshoot once, by a bounded amount, and no estimate can fix that.
- **§4 ⚠️ A COST THE TRACE DOES NOT CONTAIN** — one call larger than ``tpm`` itself. The
  decision, made in the open: it **stops the lane**, booked as ``PACER_REFUSED`` with zero
  tokens and zero calls, and **it does not 429**.
- **§5 THE CHARGE IS UNCHANGED** — `INC-143`'s no-refund rule survives this fix untouched,
  and this is the assertion that says so rather than the docstring that claims it.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from whetstone_gate.driver import clients as driver_clients
from whetstone_gate.driver import episode as driver_episode
from whetstone_gate.driver import run as driver_run
from whetstone_gate.runner import buckets as runner_buckets
from whetstone_gate.runner import episodes as runner_episodes
from whetstone_gate.runner import usage as runner_usage
from whetstone_gate.runner.budget import Ceilings, LaneBudget

# --------------------------------------------------------------------------------------
# 1. THE TRACE
# --------------------------------------------------------------------------------------

#: `config/lanes.yaml`'s declared figures for `gemma-26b`, as every other replay in this
#: suite spells them. ⚠️ Not a new spec value: `config/` is a frozen pre-registration
#: artefact and these are transcribed from it so the replay is about the same lane the run
#: was paced against. `test_the_replayed_lane_still_matches_config` checks that.
_TPM = 16_000
_RPM = 30
_RPD = 14_400

#: The reservation the run computes: ``attacker.target_tokens_per_episode // turn_budget``.
_RESERVATION = 60_000 // 20

#: ⚠️ **THE REAL TRACE, TRANSCRIBED FROM `evals/usage/gemma-26b-2026-09-04.jsonl`** as
#: ``(seconds since the first call, usage.total_tokens)`` over every row whose outcome is
#: ``OK``. **Thirty-two calls: the pilot's 8, attempt 2's 13 and attempt 3's 11.** The two
#: ``RATE_LIMITED`` rows carry ``total_tokens: 0`` and are not calls the pacer admitted;
#: they are the provider's answers, and they appear here only as the reason the trace stops.
#:
#: ⚠️ **WHY THIS IS A LITERAL AND NOT A READ, WHEN EVERY OTHER REPLAY IN THIS SUITE READS.**
#: `INC-143`'s *Missing* field is right that a hand-written fixture can be written to agree
#: with the code it checks — and every existing replay reads the artefact for exactly that
#: reason. **But the artefact is no longer closed.** It is UNCOMMITTED at the time of
#: writing (git HEAD holds the pilot's 9 rows; the working tree holds 34) and **attempt 4
#: will append to it**, so a test that reads it is a test whose subject changes underneath
#: it — which is precisely why six of this suite's thirteen standing failures are the tests
#: that do read it. ⚠️ **The guarantee is not abandoned, it is moved:**
#: :func:`test_the_pinned_trace_is_a_verbatim_PREFIX_of_the_artefact` re-derives every
#: number below from the artefact whenever the artefact is present, and `evals/` being
#: **append-only** is exactly what makes a *prefix* check the right shape.
_TRACE: tuple[tuple[float, int], ...] = (
    # -- the pilot, 2026-09-04T03:26:42Z .. 03:30:21Z (INC-143's own eight) --------------
    (0.0, 790),
    (32.0, 3_203),
    (55.0, 4_002),
    (107.0, 6_201),
    (145.0, 6_665),
    (171.0, 7_439),
    (201.0, 7_782),
    (219.0, 6_848),
    # -- calibration attempt 2, 14:33:30Z .. 14:38:50Z (INC-159's thirteen) --------------
    (40_008.0, 512),
    (40_033.0, 2_882),
    (40_045.0, 3_333),
    (40_061.0, 3_918),
    (40_082.0, 4_251),
    (40_101.0, 4_831),
    (40_117.0, 5_175),
    (40_129.0, 3_994),
    (40_164.0, 3_780),
    (40_223.0, 4_874),
    (40_253.0, 5_305),
    (40_302.0, 6_819),
    (40_328.0, 7_181),
    # -- calibration attempt 3, 19:11:35Z .. 19:15:57Z (INC-161's eleven) ----------------
    (56_693.0, 564),
    (56_723.0, 3_176),
    (56_729.0, 3_288),
    (56_744.0, 3_881),
    (56_767.0, 4_679),
    (56_790.0, 5_749),
    (56_806.0, 6_451),
    (56_822.0, 5_716),
    (56_841.0, 4_925),
    # ⚠️⚠️ THE PAIR. 8,421 + 9,037 = 17,458 in 26 seconds, against a tpm of 16,000.
    (56_929.0, 8_421),
    (56_955.0, 9_037),
    # 56,956.0 — HTTP 429. The lane stopped; 29 of 30 episodes never started.
)

#: The artefact the trace above was transcribed from. Resolved from this file rather than
#: from the ``repo_root`` fixture so that a replay driven against a copy of ``src/`` — which
#: is how the RED proof was run — still checks provenance against the real record.
_ARTEFACT = (
    Path(__file__).resolve().parents[1]
    / "evals"
    / "usage"
    / "gemma-26b-2026-09-04.jsonl"
)


def _artefact_ok_calls() -> list[tuple[float, int]] | None:
    """The artefact's ``OK`` rows as ``(offset_seconds, tokens)``, or ``None`` if absent."""
    if not _ARTEFACT.is_file():
        return None
    from datetime import datetime, timezone

    rows = [
        json.loads(line)
        for line in _ARTEFACT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ok = [row for row in rows if row["outcome"] == "OK"]
    if not ok:
        return None

    def moment(row):
        return datetime.strptime(row["utc"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )

    zero = moment(ok[0])
    return [((moment(r) - zero).total_seconds(), int(r["total_tokens"])) for r in ok]


def test_the_pinned_trace_is_a_verbatim_PREFIX_of_the_artefact():
    """⚠️ **THE PROVENANCE CHECK, AND THE REASON A LITERAL IS ALLOWED HERE AT ALL.**

    `INC-143`'s *Missing* field: *"a dry run's `TranscriptClient` returns the token counts
    the fixture was built with, so the fixture and the reservation can agree forever while
    the provider disagrees with both."* The defence against that is **provenance**, not
    file-reading as such — and a **prefix** is the exactly-right shape here because
    `CLAUDE.md` §4 makes `evals/` **append-only**: attempt 4 may add rows, and may never
    change one. If the record is ever rewritten, this fails and every number in §3 stops
    being about the run that died.
    """
    artefact = _artefact_ok_calls()
    if artefact is None:  # pragma: no cover - the artefact is present in this tree
        pytest.skip(
            "evals/usage/gemma-26b-2026-09-04.jsonl is absent. It is UNCOMMITTED at the "
            "time of writing, so a clean clone legitimately has no copy; the pinned trace "
            "stands alone there and every other test in this file still runs."
        )
    assert len(artefact) >= len(_TRACE), (
        f"the artefact holds {len(artefact)} OK rows and the pinned trace holds "
        f"{len(_TRACE)}. evals/ is APPEND-ONLY, so the record can only grow; a shorter one "
        f"means rows were deleted or truncated, which CLAUDE.md S4 forbids"
    )
    assert artefact[: len(_TRACE)] == list(_TRACE), (
        "the pinned trace is not a verbatim prefix of the artefact. Either the transcription "
        "is wrong or the append-only record was rewritten; INC-161's every figure is read "
        "from these rows and neither case may pass silently"
    )


def test_the_trace_holds_the_PAIR_THAT_EARNED_THE_429():
    """⚠️ **The two calls INC-161 is about, as an assertion rather than a sentence.**"""
    last_two = _TRACE[-2:]
    assert [tokens for _at, tokens in last_two] == [8_421, 9_037]
    assert sum(tokens for _at, tokens in last_two) == 17_458
    assert last_two[1][0] - last_two[0][0] == 26.0, "twenty-six seconds apart"
    assert 17_458 > _TPM, (
        "the pair exceeds the declared tpm — that is the whole of INC-161, and if this ever "
        "stops being true the file is replaying something else"
    )
    assert sum(tokens for _at, tokens in _TRACE) == 155_672, "the day's whole OK spend"
    assert len(_TRACE) == 32


def test_the_replayed_lane_still_matches_config(repo_root):
    """⚠️ **The replay must be about the lane the run was actually paced against.**

    `config/lanes.yaml` is a frozen pre-registration artefact; these three numbers are
    transcribed from it, and a transcription that drifts would make every figure in §3 a
    statement about a lane that does not exist.
    """
    text = (repo_root / "config" / "lanes.yaml").read_text(encoding="utf-8")
    block = text.split("gemma-26b", 1)[1]
    for key, value in (("rpm", _RPM), ("tpm", _TPM), ("rpd", _RPD)):
        assert f"{key}: {value}" in block, (
            f"config/lanes.yaml no longer declares {key}: {value} for gemma-26b, so this "
            f"file is replaying a lane the run was not paced against"
        )


# --------------------------------------------------------------------------------------
# 2. THE ESTIMATOR — ObservedCost
# --------------------------------------------------------------------------------------


def test_the_estimator_FALLS_BACK_to_the_existing_formula_until_there_is_data():
    """⚠️ **Hard rule 9: no new spec value.** Before any call has answered, the reservation
    is exactly the figure the run already computed from `config/` — so a lane's first call
    is paced precisely as it was before this fix."""
    observed = runner_buckets.ObservedCost(floor=_RESERVATION)
    assert observed.reservation == _RESERVATION == 3_000
    assert observed.largest == 0, "zero means NO CALL HAS ANSWERED, not a limit of zero"


def test_the_estimator_RISES_TO_WHAT_THE_LANE_ACTUALLY_COST():
    observed = runner_buckets.ObservedCost(floor=_RESERVATION)
    for _at, tokens in _TRACE:
        observed.observe(tokens)
    assert observed.reservation == 9_037 == max(t for _a, t in _TRACE)


def test_the_formula_is_a_FLOOR_and_never_a_SEED():
    """⚠️⚠️ **THE CLASS B CHOICE, PINNED SO IT CANNOT BE QUIETLY REVERSED.**

    The obvious reading of *"fall back to the formula until there is data"* is to **replace**
    it with the data. On this lane's own trace that makes the reservation **fall to 512**
    after one cheap opening turn — a worse estimate than the one it replaces, and one that
    would pace the runner **faster** than it was paced before the fix. Taking the ``max``
    instead means this change is **one-directional**: it can only ever slow the runner down.

    ⚠️ **That one-directionality is the exact property `INC-143` found the old `_PacedClient`
    docstring claiming falsely** — *"it can only make the runner slower … never faster"* —
    and here it is a consequence of the arithmetic rather than a promise in prose.
    """
    observed = runner_buckets.ObservedCost(floor=_RESERVATION)
    observed.observe(512)
    assert observed.reservation == _RESERVATION, (
        "a 512-token opening turn must NOT drop the reservation to 512; the config figure "
        "is a floor beneath the estimate, not a seed the first observation replaces"
    )


def test_the_estimator_is_MONOTONE_so_a_cheap_turn_cannot_buy_headroom_for_an_expensive_one():
    observed = runner_buckets.ObservedCost(floor=_RESERVATION)
    observed.observe(8_421)
    assert observed.reservation == 8_421
    observed.observe(4_925)
    assert observed.reservation == 8_421, (
        "the estimate must not fall. INC-143's own reasoning about the settle applies here "
        "one level up: letting a cheap turn lower the bar is the same under-charge in the "
        "other direction"
    )


def test_the_estimator_REFUSES_a_nonsense_floor_rather_than_defaulting():
    with pytest.raises(runner_buckets.BucketError, match="is not a reservation"):
        runner_buckets.ObservedCost(floor=0)


def test_the_estimator_REFUSES_a_negative_cost_because_a_provider_bills_a_COUNT():
    observed = runner_buckets.ObservedCost(floor=_RESERVATION)
    with pytest.raises(runner_buckets.BucketError, match="never a credit"):
        observed.observe(-1)


def test_the_estimator_IS_PURE_no_clock_no_io_no_randomness():
    """⚠️ **Hard rule 8.** The pacing module's own docstring makes the clock an argument;
    an estimator that read one would put it straight back.

    ⚠️ **THE PROSE IS STRIPPED BEFORE THE SCAN, FOR `tests/test_tripwire_registry.py`'s own
    stated reason:** *"Prose ABOUT a constant is not a hardcoded constant … Conflating them
    would make the tripwire fire on its own explanations, and the first response to that is
    always to weaken it."* This test's first draft fired on the word *"randomness"* inside
    the very sentence promising there is none.
    """
    import inspect
    import re

    source = inspect.getsource(runner_buckets.ObservedCost)
    code = re.sub(r"(\"\"\"|\'\'\')(?:.|\n)*?\1", '""', source)
    code = re.sub(r"#[^\n]*", "", code)
    for forbidden in ("time.", "monotonic", "datetime", "random", "open(", "Path("):
        assert forbidden not in code, (
            f"ObservedCost's CODE mentions {forbidden!r}. It takes every number from its "
            f"caller; hard rule 8 keeps the clock and the I/O in the shell"
        )
    # ⚠️ And the strip must not be so eager that the scan can no longer see anything.
    assert "self.largest = max(self.largest, actual)" in code, (
        "the docstring strip removed the body too, so the scan above would pass on any code"
    )


# --------------------------------------------------------------------------------------
# 3. ⚠️ THE SPEC, AS A TEST — no trailing 60-second window may exceed `tpm`
# --------------------------------------------------------------------------------------


@dataclasses.dataclass
class _WitnessBuckets:
    """A real :class:`Buckets`, plus an **independent** record of every charge and when.

    ⚠️ **THE WINDOW IS RECOMPUTED HERE RATHER THAN READ OFF THE LIMITER.** Asking
    ``buckets.tpm.used`` would be asking the implementation under test whether it agrees
    with itself. This wrapper records ``(instant, tokens)`` for every ``take`` and every
    ``settle`` and §3 sums them itself, so the assertion is about what the lane **spent**,
    not about what the limiter **believes**.
    """

    inner: runner_buckets.Buckets
    charges: list = dataclasses.field(default_factory=list)
    taken: list = dataclasses.field(default_factory=list)
    settled: list = dataclasses.field(default_factory=list)

    @property
    def admissions(self) -> list[float]:
        """The instant each call was **admitted**, read back from the charges themselves.

        ⚠️ **NOT THE INSTANT IT ARRIVED, AND THE DIFFERENCE IS THE ENTIRE POINT OF THE
        FIX.** A call arrives when the previous one finished and is admitted when the window
        can hold it; on this trace the pacer holds the last call back for 38 seconds, and an
        instrument that recorded arrival would report the pre-fix schedule while the fixed
        pacer ran underneath it. Each call contributes exactly two charges — the ``take``
        and its ``settle`` — at the same reading, so the even-indexed entries are the
        admissions.
        """
        assert len(self.charges) % 2 == 0, "every call charges a take and a settle"
        return [self.charges[i][0] for i in range(0, len(self.charges), 2)]

    @property
    def lane(self):
        return self.inner.lane

    def wait_seconds(self, *, tokens, now):
        return self.inner.wait_seconds(tokens=tokens, now=now)

    def take(self, *, tokens, now):
        self.taken.append(tokens)
        self.charges.append((now, float(tokens)))
        return self.inner.take(tokens=tokens, now=now)

    def settle(self, *, extra_tokens, now):
        self.settled.append(extra_tokens)
        self.charges.append((now, float(extra_tokens)))
        return self.inner.settle(extra_tokens=extra_tokens, now=now)


@dataclasses.dataclass
class _ReplayClient:
    """Answers with the trace's real ``usage.total_tokens``, in the trace's real order."""

    tokens: list
    index: int = 0
    seen: int = 0

    def complete_attacker(self, *, messages, temperature, lane):
        total = self.tokens[self.index]
        self.index += 1
        self.seen += 1
        return driver_clients.ModelReply(text="the reply", usage={"total_tokens": total})

    def complete_judge(self, *, system, user, lane):  # pragma: no cover - unused here
        raise AssertionError("this replay drives the attacker path only")


class _ReplayWallClock:
    """A monotonic clock that **advances when the pacer sleeps**, as
    `tests/test_arch_lanes.py`'s own scaffold does and for the reason its docstring gives:
    a ``sleep`` that does not move a clock models a runner that can never wait, and
    `Q-191`'s window makes this one wait."""

    def __init__(self) -> None:
        self.now = 0.0
        self.slept: list[float] = []

    def arrive(self, at: float) -> None:
        self.now = max(self.now, at)

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds


_MESSAGES = ({"role": "user", "content": "the attacker's turn"},)


def _replay_the_trace():
    """Drive the whole 32-call trace through the **real** pacer and the **real** buckets."""
    buckets = _WitnessBuckets(
        runner_buckets.Buckets.for_lane(
            name="gemma-26b", rpm=_RPM, tpm=_TPM, rpd=_RPD, tpd=None
        )
    )
    wall = _ReplayWallClock()
    paced = driver_run._PacedClient(
        inner=_ReplayClient([tokens for _at, tokens in _TRACE]),
        attacker_buckets=buckets,
        judge_buckets=buckets,
        attacker_reservation=_RESERVATION,
        judge_reservation=_RESERVATION,
        clock=wall.clock,
        sleep=wall.sleep,
    )
    for at, _tokens in _TRACE:
        wall.arrive(at)
        paced.complete_attacker(messages=_MESSAGES, temperature=0.7, lane="gemma-26b")
    return buckets, wall, paced


def _worst_trailing_window(charges) -> tuple[float, float]:
    """``(worst total, the instant it was reached)`` over every trailing 60 s window."""
    worst, at_worst = 0.0, 0.0
    for instant, _tokens in charges:
        total = sum(t for when, t in charges if instant - 60.0 < when <= instant)
        if total > worst:
            worst, at_worst = total, instant
    return worst, at_worst


def test_NO_TRAILING_60_SECOND_WINDOW_EVER_EXCEEDS_TPM():
    """⚠️⚠️⚠️ **THIS IS THE SPEC, AND IT IS THE TEST. `INCIDENTS.md` INC-161.**

    *"THE PACER MUST NOT ADMIT A CALL THE LANE CANNOT AFFORD. Over any trailing 60-second
    window, the tokens the runner actually spends must not exceed the lane's declared
    ``tpm``."*

    ⚠️ **PROVED RED AGAINST THE PRE-FIX PACER**, driven over this same trace with the same
    scaffold:

        worst trailing-60s window, PRE-FIX  : **18,175**   — over ``tpm`` by **2,175**
        worst trailing-60s window, FIXED    : **15,221**   — inside ``tpm``

    The pre-fix pacer asked the window for room for **3,000** on every one of the 32 calls,
    whatever the call was about to cost. The fixed pacer asks for
    :class:`~whetstone_gate.runner.buckets.ObservedCost` — the worst this role has actually
    been billed — and waits when the window cannot hold it.

    ⚠️ **THE WINDOW IS SUMMED FROM THIS TEST'S OWN RECORD OF THE CHARGES**, not read off the
    limiter, so a limiter that miscounted could not make this pass.
    """
    buckets, _wall, _paced = _replay_the_trace()
    worst, at_worst = _worst_trailing_window(buckets.charges)

    assert worst <= _TPM, (
        f"the runner spent {worst:,.0f} tokens inside the 60 seconds ending at "
        f"t={at_worst:,.0f}s, against a declared tpm of {_TPM:,}. That is INC-161: on the "
        f"real trace the pre-fix pacer reached 18,175 here and the provider answered 429"
    )
    assert worst == pytest.approx(15_221.0), (
        "the measured worst window. Pinned exactly so that a change which merely moves the "
        "breach somewhere else cannot pass by staying under the limit by accident"
    )


def test_THE_PAIR_THAT_EARNED_THE_429_IS_NO_LONGER_ADMITTED_INTO_ONE_MINUTE():
    """⚠️ **The specific failure, as its own assertion.** 8,421 and 9,037 were admitted 26
    seconds apart. After the fix the pacer **waits** so that the first has left the window
    before the second is sent."""
    buckets, _wall, _paced = _replay_the_trace()
    # The last two calls' ADMISSION instants, in the replay's own clock.
    first, second = buckets.admissions[-2], buckets.admissions[-1]
    window_at_second = sum(
        tokens for when, tokens in buckets.charges if second - 60.0 < when <= second
    )
    assert window_at_second <= _TPM
    assert window_at_second == pytest.approx(9_037.0), (
        "at the moment the 9,037-token call is sent the trailing minute must hold that call "
        "alone: the 8,421 before it has expired. Pre-fix the two sat together at 17,458"
    )
    assert second - first == pytest.approx(60.0), (
        f"the pacer separated the pair by only {second - first:.1f}s. INC-161's whole "
        f"finding is that 26 seconds was not enough, and a SLIDING window clears its debt "
        f"by EXPIRY rather than on a ramp — so the wait is to the 8,421's 60-second "
        f"birthday, exactly, and not one second more"
    )
    assert first == pytest.approx(56_933.0) and second == pytest.approx(56_993.0), (
        "the admission instants, pinned. The 8,421 call ARRIVED at t=56,929 and the 9,037 "
        "at t=56,955 — 26 seconds apart, as the record says. The pacer moved the second to "
        "t=56,993, which is the whole of the fix expressed as two numbers"
    )


def test_THE_FIX_IS_SLOWER_AND_THAT_IS_THE_RULED_TRADE():
    """⚠️ **`Q-191`, RULED 2026-09-04, in capitals:** *"IT WILL SLOW THE SWEEP AND THAT IS
    THE CORRECT TRADE: a paced wait costs seconds, a 429 costs the lane, and hard rule 12
    forbids retrying into another."*

    **MEASURED, so the cost is a number the operator can decide against rather than a
    warning:** across these 32 real calls the pre-fix pacer slept **43 s** and the fixed one
    sleeps **339 s** — **+296 s, about 9.3 s per call.**
    """
    _buckets, wall, _paced = _replay_the_trace()
    assert sum(wall.slept) == pytest.approx(339.0), (
        "the pacing cost of the fix, pinned. If it ever falls to 43 s the adaptive "
        "admission has stopped being used; if it climbs a great deal further, the estimate "
        "has stopped being an estimate"
    )
    assert sum(wall.slept) > 43.0, "the pre-fix figure, on the same trace"


def test_the_estimate_the_pacer_ADMITTED_AGAINST_rose_with_the_lane():
    """The mechanism, so a green §3 cannot be explained by the pacer having stopped."""
    _buckets, _wall, paced = _replay_the_trace()
    assert paced.attacker_observed.reservation == 9_037
    assert paced.attacker_observed.largest == 9_037
    assert paced.judge_observed.reservation == _RESERVATION, (
        "no judge call was made, so the judge's estimate must still be the config floor. "
        "One estimate per ROLE, never one per lane — INC-111"
    )


# --------------------------------------------------------------------------------------
# 3b. ⚠️ THE ESTIMATE MUST OUTLIVE THE EPISODE, BECAUSE THE WINDOW DOES
# --------------------------------------------------------------------------------------

#: The trace, split at the run boundaries the artefact records.
_PILOT = _TRACE[:8]
_ATTEMPT_2 = _TRACE[8:21]
_ATTEMPT_3 = _TRACE[21:]


def _two_episodes(*, injected: bool):
    """Two episodes over **one** lane's buckets — which is how ``execute`` runs.

    ``injected=False`` reproduces the shape in which ``_PacedClient`` builds its own
    estimate: a new client per episode, and therefore a new estimate per episode.
    """
    buckets = _WitnessBuckets(
        runner_buckets.Buckets.for_lane(
            name="gemma-26b", rpm=_RPM, tpm=_TPM, rpd=_RPD, tpd=None
        )
    )
    wall = _ReplayWallClock()
    shared = runner_buckets.ObservedCost(floor=_RESERVATION) if injected else None
    opening_estimates = []
    for episode in (_ATTEMPT_2, _ATTEMPT_3):
        extra = (
            {"attacker_observed": shared, "judge_observed": shared} if injected else {}
        )
        paced = driver_run._PacedClient(
            inner=_ReplayClient([tokens for _at, tokens in episode]),
            attacker_buckets=buckets,
            judge_buckets=buckets,
            attacker_reservation=_RESERVATION,
            judge_reservation=_RESERVATION,
            clock=wall.clock,
            sleep=wall.sleep,
            **extra,
        )
        opening_estimates.append(paced.attacker_observed.reservation)
        for at, _tokens in episode:
            wall.arrive(at)
            paced.complete_attacker(
                messages=_MESSAGES, temperature=0.7, lane="gemma-26b"
            )
    return opening_estimates, buckets, wall


def test_THE_ESTIMATE_SURVIVES_THE_END_OF_AN_EPISODE():
    """⚠️⚠️ **THE SECOND HALF OF `INC-161`, AND IT WAS FOUND BY READING THE LOOP RATHER
    THAN THE CLASS.**

    ``driver/run.py:execute`` rebuilds ``_PacedClient`` **inside** its ``for key in
    pending`` loop — `Q-179`(3) requires the pacer to be built on every run, including a dry
    one — while ``lane_states[...].buckets`` are built **once per lane, before** it. An
    adaptive reservation held on the per-episode client therefore **forgets, thirty times,
    everything the window it paces against still remembers**, and every episode's opening
    turns are admitted against the same falsified 3,000 that stopped attempt 3.

    ⚠️ **MEASURED, on the two calibration attempts replayed back to back over one lane's
    buckets:**

        estimate at episode 2's FIRST call, per-episode : **3,000**  (the config floor)
        estimate at episode 2's FIRST call, run-scoped  : **7,181**  (what episode 1 cost)

    **A fix scoped to the episode would have passed every other test in this file** — §3
    replays one continuous stretch — **and would have been worth very little in the run.**
    """
    per_episode, _b1, _w1 = _two_episodes(injected=False)
    run_scoped, _b2, _w2 = _two_episodes(injected=True)

    assert per_episode == [_RESERVATION, _RESERVATION], (
        "the un-injected shape must reset to the config floor at each episode — this is the "
        "defect being pinned, and if it ever stops happening this test has lost its control"
    )
    assert run_scoped[0] == _RESERVATION, "a cold lane starts at the floor, as it must"
    assert run_scoped[1] == 7_181, (
        "episode 2 must open knowing what episode 1's calls actually cost. 7,181 is "
        "attempt 2's largest call, read from the artefact"
    )
    assert run_scoped[1] > per_episode[1], (
        "the whole point: the run-scoped estimate enters episode 2 strictly better informed"
    )


def test_execute_BUILDS_THE_ESTIMATES_OUTSIDE_ITS_EPISODE_LOOP():
    """⚠️ **The structural half, because the behavioural half above cannot see ``execute``.**

    A refactor that moved the dictionary inside the loop would restore the defect silently
    and every behavioural test would stay green, because they all drive ``_PacedClient``
    directly. This is the one assertion that reads the loop.
    """
    import inspect

    source = inspect.getsource(driver_run.execute)
    built = source.index("observed_costs: dict")
    loop = source.index("for key in pending:")
    assert built < loop, (
        "execute builds its per-(lane, role) estimates INSIDE the episode loop, so each "
        "episode gets a fresh one. That is INC-161 repeating once per episode; the "
        "dictionary must outlive the loop, as lane_states does"
    )
    assert "attacker_observed=_observed(" in source, (
        "execute no longer injects the estimate, so _PacedClient falls back to building its "
        "own per-episode one and the run forgets between episodes"
    )


def test_A_COLD_LANE_CAN_STILL_OVERSHOOT_ONCE_AND_THAT_IS_PUBLISHED_NOT_HIDDEN():
    """⚠️⚠️ **THE RESIDUAL, ASSERTED RATHER THAN OMITTED. THE FIX IS NOT A GUARANTEE.**

    The estimate is *"the worst this role has actually cost"*, so it can only ever be
    exceeded by a call that costs more than **every** call the lane has made before it. On a
    **cold** lane — before any call has answered — the estimate is the `config/` floor, and
    the opening calls of a run can therefore still push the trailing window over ``tpm``.

    ⚠️ **MEASURED, on the two calibration attempts alone (i.e. with the pilot's eight calls
    removed, so the lane starts cold): the worst window reaches 16,333 — over ``tpm`` by
    333, or 2.1%.** On the full 32-call trace of §3 it does not happen at all, because the
    pilot's calls warm the estimate before attempt 2 begins.

    ⚠️ **THIS CANNOT BE FIXED BY A BETTER ESTIMATE, AND SAYING SO IS THE POINT.** No
    measurement of past calls bounds a future one; the only estimate that could guarantee
    the window is ``tpm`` itself, which admits one call per minute and is not a runner. What
    the fix buys is that the overshoot is **bounded by a single call's excess over the
    lane's own record, happens once per lane per run rather than once per episode, and is
    repaid immediately** — the settle records the truth, so the next admission waits it off.

    **Published here, and in `INCIDENTS.md` INC-161's `Systemic guardrail`, rather than left
    for a reviewer to find.**
    """
    buckets = _WitnessBuckets(
        runner_buckets.Buckets.for_lane(
            name="gemma-26b", rpm=_RPM, tpm=_TPM, rpd=_RPD, tpd=None
        )
    )
    wall = _ReplayWallClock()
    shared = runner_buckets.ObservedCost(floor=_RESERVATION)
    cold = _ATTEMPT_2 + _ATTEMPT_3
    paced = driver_run._PacedClient(
        inner=_ReplayClient([tokens for _at, tokens in cold]),
        attacker_buckets=buckets,
        judge_buckets=buckets,
        attacker_reservation=_RESERVATION,
        judge_reservation=_RESERVATION,
        clock=wall.clock,
        sleep=wall.sleep,
        attacker_observed=shared,
        judge_observed=shared,
    )
    for at, _tokens in cold:
        wall.arrive(at)
        paced.complete_attacker(messages=_MESSAGES, temperature=0.7, lane="gemma-26b")

    worst, _at = _worst_trailing_window(buckets.charges)
    assert worst == pytest.approx(16_333.0), (
        "the cold-start residual, pinned at the number it actually is. It is recorded so "
        "that the claim in section 3 is read as what it is — a property of the real trace, "
        "not a guarantee about every trace"
    )
    assert worst > _TPM, "and it IS over the limit; the honest word for that is a residual"
    assert worst / _TPM < 1.05, (
        "bounded, though: 2.1% over, against the 13.6% the pre-fix pacer reached on the "
        "very same calls"
    )


# --------------------------------------------------------------------------------------
# 4. ⚠️ A COST THE TRACE DOES NOT CONTAIN — one call larger than `tpm` itself
# --------------------------------------------------------------------------------------


def test_a_call_LARGER_THAN_TPM_STOPS_THE_LANE_and_does_NOT_reach_a_provider():
    """⚠️⚠️ **THE DECISION, MADE IN THE OPEN: IT STOPS THE LANE. IT DOES NOT 429.**

    The trace contains no call larger than ``tpm``; the largest is 9,037 against 16,000. But
    the adaptive estimate makes such a call **matter** in a way it did not before: pre-fix
    ``_pace`` only ever asked for 3,000, so
    :meth:`~whetstone_gate.runner.buckets.SlidingWindow.wait_seconds`'s
    ``cost > capacity`` branch was **unreachable on this lane**. It is reachable now, and
    this test is what decides what it does.

    ⚠️ **THE THREE OPTIONS, AND WHY THIS ONE:**

      1. **Clamp the estimate down to ``tpm`` and send anyway.** ⚠️ **Rejected.** It sends a
         request we have *measured* the lane cannot afford — deliberately buying the 429
         that `Q-191` ruled we do not buy (*"a paced wait costs seconds, a 429 costs the
         lane"*), and hard rule 12 then forbids retrying into another lane.
      2. **Wait.** ⚠️ **Impossible, and the module says so in its own words:** *"Waiting
         cannot help. A single call larger than a per-minute limit must be made smaller, not
         retried."* An empty window still cannot hold it.
      3. **Stop the lane, booked.** ⚠️ **Chosen**, and it is what the shipped code already
         does: :class:`~whetstone_gate.runner.buckets.BucketError` from the pacer is caught
         by `driver/episode.py`'s ``except BucketError`` branch — `Q-179`(2), `INC-160` — and
         booked as ``PACER_REFUSED``: **counted in the denominator under its own name, zero
         tokens, zero calls, and no packet on the wire.** Hard rule 11 is satisfied because
         the episode is counted, not dropped; hard rule 12 because nothing was spent.

    **This test drives the REAL pacer, the REAL sliding window and the REAL ``_MeteredCall``
    over a REAL ``UsageLog``** — no doubles — because `INC-160` is the entry about a branch
    that was green through a permissive stub and broken in the program.
    """
    booked: list[dict] = []
    buckets = runner_buckets.Buckets.for_lane(
        name="gemma-26b", rpm=_RPM, tpm=_TPM, rpd=_RPD, tpd=None
    )
    wall = _ReplayWallClock()
    # ⚠️ One call that costs MORE than the lane's whole per-minute capacity, then a second
    #    ordinary one. The first is admitted (the estimate is still the 3,000 floor) and the
    #    provider bills it; the SECOND is the one that cannot be paced.
    client = _ReplayClient([_TPM + 1, 1_000])
    paced = driver_run._PacedClient(
        inner=client,
        attacker_buckets=buckets,
        judge_buckets=buckets,
        attacker_reservation=_RESERVATION,
        judge_reservation=_RESERVATION,
        clock=wall.clock,
        sleep=wall.sleep,
    )

    # -- call 1: admitted, and it teaches the estimator a cost bigger than the lane --------
    paced.complete_attacker(messages=_MESSAGES, temperature=0.7, lane="gemma-26b")
    assert paced.attacker_observed.reservation == _TPM + 1 > _TPM

    # -- call 2: the pacer refuses BEFORE the wire, and the lane stops ---------------------
    metered = driver_episode._MeteredCall(
        lane="gemma-26b",
        budget=LaneBudget(
            model="gemma-26b",
            ceilings=Ceilings(call_ceiling=10, token_ceiling=100_000),
        ),
        reservation_tokens=_RESERVATION,
        on_usage=lambda lane, tokens, outcome, **extra: booked.append(
            {"lane": lane, "tokens": tokens, "outcome": outcome, **extra}
        ),
    )
    seen_before = client.seen
    with pytest.raises(driver_episode.LaneStopped) as stopped:
        metered.run(
            lambda: paced.complete_attacker(
                messages=_MESSAGES, temperature=0.7, lane="gemma-26b"
            )
        )

    # (1) IT STOPS THE LANE, under its own name — never folded into the provider's.
    assert stopped.value.cause == runner_episodes.PACER_REFUSED
    assert stopped.value.cause != runner_episodes.RATE_LIMIT_429, (
        "⚠️ THE POINT OF THE WHOLE FIX: this must never be published as a 429. A 429 is the "
        "provider's answer; this is our own refusal, made before the wire"
    )

    # (2) ⚠️ AND NOTHING WAS SENT. The estimate refused it before the request existed.
    assert client.seen == seen_before, (
        "the provider was called. The refusal must happen at admission, not after — that is "
        "the difference between a paced runner and one that discovers the limit by 429"
    )
    assert wall.slept == [], "no wait was attempted: waiting cannot help"

    # (3) IT IS COUNTED, at zero tokens and zero calls, in a DECLARED usage outcome.
    assert len(booked) == 1
    assert booked[0]["lane"] == "gemma-26b"
    assert booked[0]["tokens"] == 0
    assert booked[0]["outcome"] in runner_usage.OUTCOMES, "INC-160"
    assert booked[0]["error_type"] == "BucketError"
    assert metered.calls_settled == 0, "no request was sent, so no call is charged"


def test_the_window_itself_REFUSES_a_cost_larger_than_its_capacity_and_says_why():
    """The limiter's own half of §4, at its own level — `runner/buckets.py`'s contract."""
    window = runner_buckets.SlidingWindow("gemma-26b.tpm", _TPM, 60.0)
    with pytest.raises(runner_buckets.BucketError, match="exceeds its whole capacity"):
        window.wait_seconds(_TPM + 1, 0.0)
    assert window.wait_seconds(_TPM, 0.0) == 0.0, (
        "a call of exactly the capacity into an empty window is admissible; the refusal is "
        "for what cannot fit, not for what only just fits"
    )


# --------------------------------------------------------------------------------------
# 5. THE CHARGE IS UNCHANGED — INC-143's no-refund rule survives this fix
# --------------------------------------------------------------------------------------


def test_THE_BUCKETS_ARE_STILL_CHARGED_EXACTLY_WHAT_INC_143_CHARGED_THEM():
    """⚠️⚠️ **THE RE-EXAMINATION OF `INC-143`'s NO-REFUND RULE, AS AN ASSERTION.**

    The rule was re-examined rather than inherited, and it is **kept** — but only because
    this fix deliberately keeps the adaptive number **out of the charge**. The pacer now
    *waits* for :class:`~whetstone_gate.runner.buckets.ObservedCost` and still *takes* the
    reservation, which :meth:`_settle` tops up to the provider's own figure. **So the charge
    is byte-for-byte the rule `INC-143` installed:** ``take`` is always the reservation and
    ``settle`` is always ``max(0, actual - reservation)``.

    ⚠️ **WHY THAT MATTERS, MEASURED RATHER THAN ARGUED.** Had the adaptive figure been
    *taken* as well as *waited for*, with no refund, this same trace would pin the trailing
    window at **15,564 for twenty-one consecutive calls**, charge **234,736** for **155,672**
    of real spend (**+51%**), sleep **633 s** instead of 339 s — **and still breach ``tpm``
    by 203.** That is the *"throttle the run to a crawl"* failure exactly, and it is what
    inheriting the rule onto an adaptive **charge** would have cost.

    ⚠️ **A REFUND WOULD ALSO WORK (15,221; 313 s) AND WAS REJECTED ON ITS MERITS.** It buys
    26 seconds across 32 calls and costs a new direction of travel through ``settle``, whose
    refusal of a negative charge is the line that makes *"the buckets are never told less
    than the provider billed"* checkable at all.
    """
    buckets, _wall, _paced = _replay_the_trace()
    actuals = [tokens for _at, tokens in _TRACE]

    assert set(buckets.taken) == {_RESERVATION}, (
        "the TAKE is still the reservation, unchanged. If the adaptive estimate ever "
        "reaches the charge, INC-143's no-refund rule starts over-charging every call"
    )
    assert buckets.settled == [max(0, n - _RESERVATION) for n in actuals], (
        "the SETTLE is still INC-143's max(0, actual - reservation), unchanged"
    )
    per_call = [t + s for t, s in zip(buckets.taken, buckets.settled)]
    assert per_call == [max(_RESERVATION, n) for n in actuals]
    for index, (got, want) in enumerate(zip(per_call, actuals), start=1):
        assert got >= want, (
            f"call {index} cost {want} and the buckets were charged {got}. INC-143's "
            f"property — the buckets are never told LESS than the provider billed — must "
            f"survive this fix untouched"
        )
    assert sum(per_call) == 162_924
    assert sum(actuals) == 155_672


def test_the_pacer_TAKES_NO_MORE_THAN_IT_WAITED_FOR_so_the_admission_cannot_be_refused():
    """⚠️ **Why the two-argument ``_pace`` is safe.** ``wait_seconds`` is monotone in cost,
    so an admission granted for the larger estimate can never be refused for the smaller
    reservation — and `Q-179`(1)'s single clock reading is untouched."""
    window = runner_buckets.SlidingWindow("gemma-26b.tpm", _TPM, 60.0)
    window.take(10_000, 0.0)
    assert window.wait_seconds(6_000, 0.0) == 0.0
    assert window.wait_seconds(3_000, 0.0) == 0.0, (
        "room for the larger figure implies room for the smaller; if this ever stops "
        "holding, _pace's take could be refused by the very window that just admitted it"
    )
    assert window.wait_seconds(6_001, 0.0) > 0.0, "and the boundary is where it should be"
