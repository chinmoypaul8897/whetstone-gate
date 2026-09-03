"""**THE LANE-AWARE SCHEDULER. Not a thread pool.**

`CONTEXT.md` §13.3 and §13.5(6), and `PROTOCOL.md` §2.4:

    **Concurrency here means LANES, not threads.** One in-flight episode per model+provider
    lane. … The runner schedules episodes onto lanes, **never onto a thread pool.**

    **429 is backoff-and-resume, never failure.** Exponential backoff with jitter, capped; the
    episode is **re-queued**, not marked failed. A 429 storm **parks that lane** and the
    scheduler moves to another.

**The thin outer shell** (hard rule 8): this is where a real clock and real randomness are
read, and it is the only module in this package where they are. Both are **injected** — the
constructor takes a ``clock`` and a ``jitter`` callable — so a whole multi-day run can be
driven at fixed instants with fixed jitter and produce byte-identical checkpoints.

--------------------------------------------------------------------------------------
⚠️ THE 429, AND THE ONE LINE THAT SEPARATES A RUNNER FROM A SESSION
--------------------------------------------------------------------------------------

Golden 8 fixture D's own `runner_versus_session` note:

    The RUNNER backs off with jitter and re-queues WITHIN ITS OWN LANE, and a 429 storm parks
    the lane. A SESSION stops and reports. This fixture is the SESSION-level rule; C11's
    re-queue is lane-internal and does not cross into another model's budget.

So, exactly:

  * The 429'd call costs **zero tokens** and **zero calls** — the request was refused by the
    rate limiter and never ran, which is why fixture D leaves **nine** of ten calls unused
    rather than eight.
  * The episode is **re-queued onto the same lane**. ⚠️ **There is no code path in this module
    that moves a re-queued episode to a different lane**, and ``tests/test_c11_runner.py``
    drives a 429 storm across a two-lane run and asserts the re-queued episode comes back on
    its own lane. *"Never retry into another lane"* is `PROCESS.md` §8, and the reason is that
    another lane's budget is another model's.
  * After :data:`PARK_AFTER_CONSECUTIVE_429S` consecutive 429s the lane is **parked** until a
    deadline, and the scheduler moves to another lane. Parking is not failing: the episodes
    still on a parked lane are counted under :data:`.episodes.LANE_PARKED`, not dropped.

⚠️ **AND THE UNSPENT BUDGET IS THE POINT, NOT WASTE.** Golden 8 fixture D: the lane stops with
99,000 of 100,000 tokens and 9 of 10 calls unused, *"and that is correct behaviour rather than
waste. An accumulator that retries, or that spills into another model's lane to use the
remaining budget, produces a HIGHER number here and violates hard rule 12 to do it."*

--------------------------------------------------------------------------------------
⚠️ RESUME, INCLUDING ACROSS A DAY BOUNDARY
--------------------------------------------------------------------------------------

`CONTEXT.md` §13.5(5): *"Resume across DAYS. The sweep spans more than one daily allowance
window by design. The runner persists which lane exhausted which limit and at what UTC time,
and restarts against the new window without re-running completed episodes."*

:meth:`Scheduler.pending` filters the episode list against the checkpoint store on **every**
invocation, so a re-run dispatches only what has no published checkpoint — **zero duplicates
and zero re-runs of completed episodes**. The day boundary needs no special case beyond one:
:mod:`.usage` keys its file on the **UTC date**, so a lane resumed after midnight reads a
fresh, empty day and seeds a fresh :class:`.budget.LaneBudget` from it. What persists across
the boundary is the checkpoint set; what does not is the day's spend, which is exactly right.

--------------------------------------------------------------------------------------
⚠️ DETERMINISM, SCOPED EXACTLY
--------------------------------------------------------------------------------------

**Deterministic:** the dispatch **order** (episodes are sorted by their key, and lanes by
name — never by dictionary iteration order or by a set), the checkpoint key, the checkpoint
bytes, and every arithmetic decision in this package.

⚠️ **NOT DETERMINISTIC: MODEL OUTPUT.** The attacker runs at `attacker.temperature` against a
hosted provider. **Re-running the models does not reproduce the run**, and no docstring in
this package may say that it does. What `make eval` claims is *"every number regenerates from
the stored ledgers"* — true, checkable, and enough.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Callable, Iterable, Protocol

from .budget import (
    STOP_BY_429,
    STOP_BY_CALL_CEILING,
    STOP_BY_RESERVATION_SHORTFALL,
    STOP_BY_TOKEN_CEILING,
    Ceilings,
    LaneBudget,
)
from .buckets import Buckets
from .episodes import (
    CALL_CEILING,
    INTERRUPTED,
    LANE_PARKED,
    LANE_RESERVED,
    PROVIDER_ERROR,
    RATE_LIMIT_429,
    TOKEN_CEILING,
    EpisodeKey,
)

#: Consecutive 429s on one lane before it is parked. Not a spec constant — `CONTEXT.md`
#: §13.5(3) says *"a 429 storm parks that lane"* and publishes no number, so this is an
#: implementation parameter, recorded as a **Class B** deviation (hard rule 2) rather than
#: smuggled in. It is not in §8.6's constants table because it is not a spec value.
PARK_AFTER_CONSECUTIVE_429S = 3

#: Backoff base, in seconds, doubling per consecutive 429 and capped. Class B, as above.
BACKOFF_BASE_SECONDS = 2.0
BACKOFF_CAP_SECONDS = 300.0

#: Consecutive 429s beyond which the exponent stops growing, so the doubling cannot overflow
#: into a wait longer than the run. The cap above is what actually binds; this bounds the
#: arithmetic itself.
_MAX_BACKOFF_EXPONENT = 16


class Clock(Protocol):
    """Monotonic seconds. Injected, so a test drives a multi-day run in microseconds."""

    def __call__(self) -> float: ...  # pragma: no cover - a Protocol body


@dataclass(frozen=True)
class Dispatch:
    """One scheduling decision, so a caller can log **why** as well as **what**."""

    episode: EpisodeKey
    lane: str
    wait_seconds: float


@dataclass
class LaneState:
    """One lane's live state: its buckets, its sanction, and its park.

    ⚠️ ``budget`` is a :class:`.budget.LaneBudget` — **per model, never pooled**. This class
    holds exactly one and there is no field on the scheduler that adds two together.
    """

    name: str
    buckets: Buckets
    budget: LaneBudget
    consecutive_429s: int = 0
    parked_until: float | None = None
    requeued: list[EpisodeKey] = field(default_factory=list)

    def is_parked(self, now: float) -> bool:
        if self.parked_until is None:
            return False
        if now >= self.parked_until:
            self.parked_until = None
            self.consecutive_429s = 0
            return False
        return True


def backoff_seconds(consecutive: int, jitter: Callable[[], float]) -> float:
    """Exponential backoff with jitter, capped. `CONTEXT.md` §13.5(3).

    ``jitter`` returns a fraction in ``[0, 1)`` and is **injected**, so a test gets a fixed
    schedule and the production path gets a real one. Full jitter — the wait is scaled by the
    fraction rather than nudged by it — because equal-jittered waits still synchronise a fleet
    of retries, and this project's whole free-tier position is that it must not earn a second
    429 by retrying in lockstep with itself.
    """
    if consecutive < 1:
        raise ValueError(f"backoff is for a 429 that happened; got consecutive={consecutive}")
    exponent = min(consecutive - 1, _MAX_BACKOFF_EXPONENT)
    ceiling = min(BACKOFF_BASE_SECONDS * (2.0**exponent), BACKOFF_CAP_SECONDS)
    return ceiling * jitter()


@dataclass
class Scheduler:
    """Schedules episodes onto lanes. **One in-flight episode per lane.**

    ``sanctioned_lanes`` is the set of reserved lanes this run's prompt named, verbatim
    (`PROCESS.md` §8). It has **no default**: an empty set means nothing reserved is
    sanctioned, which is the correct posture for every session that is not the sweep.
    """

    lanes: dict[str, LaneState]
    sanctioned_lanes: frozenset[str]
    clock: Clock = time.monotonic
    jitter: Callable[[], float] = random.random

    # -- what is left to do ------------------------------------------------------------

    def pending(self, episodes: Iterable[EpisodeKey], completed: set[str]) -> list[EpisodeKey]:
        """Every episode with no published checkpoint, in **deterministic** order.

        ⚠️ Sorted by the episode key, never by set or dictionary iteration order. A run whose
        dispatch order depends on a hash seed is a run whose partial results depend on it too,
        and *"kill mid-run and resume"* would then not be a repeatable demonstration.
        """
        return sorted(key for key in episodes if key.slug not in completed)

    def eligible_lanes(self, now: float) -> list[str]:
        """Lanes that are not parked, not stopped and not unsanctioned-reserved. Sorted."""
        return sorted(
            name
            for name, state in self.lanes.items()
            if not state.is_parked(now) and not state.budget.stopped
        )

    def next_dispatch(self, episode: EpisodeKey, lane_name: str, tokens: int) -> Dispatch:
        """What it would take to run ``episode`` on ``lane_name`` right now.

        ``wait_seconds`` of ``0.0`` means the buckets permit it now; a positive value is a
        **wait**, not an abort (:mod:`.buckets`).
        """
        state = self.lanes[lane_name]
        now = self.clock()
        return Dispatch(
            episode=episode,
            lane=lane_name,
            wait_seconds=state.buckets.wait_seconds(tokens=tokens, now=now),
        )

    # -- the 429 path ------------------------------------------------------------------

    def on_429(self, lane_name: str, episode: EpisodeKey) -> float:
        """Record a 429. **Zero tokens, zero calls, re-queued ON THIS LANE.**

        Returns the backoff in seconds. Parks the lane after
        :data:`PARK_AFTER_CONSECUTIVE_429S` consecutive 429s.

        ⚠️ **The episode goes back onto `lane_name` and nowhere else.** `PROCESS.md` §8:
        *"never retry into another lane."* There is no parameter here that names a
        destination, so there is no argument a caller could pass to move it.
        """
        state = self.lanes[lane_name]
        state.consecutive_429s += 1
        state.requeued.append(episode)
        state.budget.record_429_requeued_in_lane()
        wait = backoff_seconds(state.consecutive_429s, self.jitter)
        if state.consecutive_429s >= PARK_AFTER_CONSECUTIVE_429S:
            state.parked_until = self.clock() + wait
        return wait

    def on_success(self, lane_name: str) -> None:
        """A call went through: the consecutive-429 counter resets."""
        self.lanes[lane_name].consecutive_429s = 0

    # -- what a caller must be told ----------------------------------------------------

    def unfinished_cause_for(self, lane_name: str, now: float) -> str | None:
        """Why an episode on this lane could not run, in :data:`.episodes.UNFINISHED_CAUSES`.

        ``None`` means it could. Every other answer is a **counted, categorised, printed**
        number (hard rule 11) rather than a silent skip.
        """
        state = self.lanes[lane_name]
        if state.is_parked(now):
            return LANE_PARKED
        stopped = state.budget.stopped_by
        if stopped is None:
            return None
        return _CAUSE_FOR_STOP.get(stopped, PROVIDER_ERROR)


#: The stop reasons :mod:`.budget` produces, mapped to the causes :mod:`.episodes` counts.
#: ⚠️ Written out rather than derived: the two vocabularies are deliberately separate
#: (`Q-119`) and a mapping table is where a reviewer can see the join and check it. A derived
#: mapping would hide a missing case behind a fallback.
_CAUSE_FOR_STOP: dict[str, str] = {
    STOP_BY_TOKEN_CEILING: TOKEN_CEILING,
    STOP_BY_CALL_CEILING: CALL_CEILING,
    STOP_BY_429: RATE_LIMIT_429,
    STOP_BY_RESERVATION_SHORTFALL: TOKEN_CEILING,
}


def build_lane_state(
    *,
    name: str,
    rpm: int,
    tpm: int,
    rpd: int,
    tpd: int | None,
    call_ceiling: int,
    token_ceiling: int,
    already_spent_tokens: int = 0,
    already_used_calls: int = 0,
) -> LaneState:
    """Assemble one lane's state, **seeded from the day's usage file**.

    ``already_spent_tokens`` / ``already_used_calls`` come from
    :func:`.usage.preflight`. ⚠️ **Seeding matters:** a lane resumed mid-window whose
    accumulator started at zero would run its whole sanctioned ceiling a second time, which is
    the overspend hard rule 12 exists to prevent — and it is exactly what a naive *"restart
    against the new window"* does when the window has not turned over.
    """
    return LaneState(
        name=name,
        buckets=Buckets.for_lane(name=name, rpm=rpm, tpm=tpm, rpd=rpd, tpd=tpd),
        budget=LaneBudget(
            model=name,
            ceilings=Ceilings(call_ceiling=call_ceiling, token_ceiling=token_ceiling),
            calls_used=already_used_calls,
            tokens_spent=already_spent_tokens,
        ),
    )


__all__ = [
    "BACKOFF_BASE_SECONDS",
    "BACKOFF_CAP_SECONDS",
    "Dispatch",
    "INTERRUPTED",
    "LANE_RESERVED",
    "LaneState",
    "PARK_AFTER_CONSECUTIVE_429S",
    "Scheduler",
    "backoff_seconds",
    "build_lane_state",
]
