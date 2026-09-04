"""**INDEPENDENT TOKEN BUCKETS FOR RPM, TPM AND RPD — refilled on their own clocks.**

`CONTEXT.md` §13.5(1) and `PROTOCOL.md` §2.4, verbatim:

    **Token-bucket pacing per model, per limit.** Independent buckets for RPM, TPM and RPD,
    refilled on their own clocks. **A call is admitted only when all three buckets permit it.**

**PURE.** ⚠️ **THE CLOCK IS AN ARGUMENT.** Hard rule 8 forbids a clock inside core logic, and a
rate limiter is exactly the module that wants one. Every method here takes ``now`` — a float
of monotonic seconds — from its caller, so a whole day's pacing can be driven deterministically
in a test at whatever instants the test chooses, and the shell (:mod:`.scheduler`) is the only
place a real clock is read.

--------------------------------------------------------------------------------------
⚠️ THESE ARE PACING BUCKETS. THEY ARE NOT THE CEILING, AND THE DISTINCTION IS THE CHUNK
--------------------------------------------------------------------------------------

Two different mechanisms live next to each other here and confusing them would defeat both:

  * **These buckets** are the **provider's** published rate limits — RPM, TPM, RPD from
    `config/lanes.yaml`, which came off the operator's own dashboards. They say *"not yet"*:
    a call they refuse can be made a moment later, when the bucket has refilled.
  * :mod:`.budget`'s ceilings are **hard rule 12's sanction** — the call ceiling and token
    ceiling this run was granted. They say ***"no"***: a call they refuse stops the lane.

A refusal from a bucket is a **wait**; a refusal from the budget is an **abort**. An
implementation that treated a bucket refusal as an abort would park a lane that is merely
pacing; one that treated a budget refusal as a wait would spin against a ceiling forever and
spend past it the moment the bucket refilled. :meth:`Buckets.wait_seconds` returns the first
and :class:`.budget.Admission` returns the second, and nothing converts between them.

--------------------------------------------------------------------------------------
⚠️ ``tpd: null`` MEANS "NO SUCH LIMIT EXISTS", NOT "UNKNOWN" AND NOT "ZERO"
--------------------------------------------------------------------------------------

`config/lanes.yaml`'s own header, and `config.py`'s ``NULL_IS_A_VALUE`` records it as a
**determined** value. Google's free tier publishes no daily token cap at all. A bucket built
from ``None`` as zero would park both Gemma lanes — which carry almost all of the sweep's
volume — permanently, on the first call. :class:`Buckets` therefore has **no TPD bucket at all**
when ``tpd`` is ``None``, rather than one with a capacity of zero, and :meth:`Buckets.limits`
prints which buckets exist so a reader can see that a lane has three rather than four.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: Seconds in the window each limit is expressed over. Not spec constants; unit conversions.
_SECONDS_PER_MINUTE = 60.0
_SECONDS_PER_DAY = 24.0 * 60.0 * 60.0


class BucketError(RuntimeError):
    """A bucket was built or driven wrongly. Always a refusal."""


@dataclass
class Bucket:
    """One limit: ``capacity`` units per ``window_seconds``, refilled continuously.

    Continuous refill rather than a hard window reset, because a hard reset lets a lane spend
    a whole window's allowance in the last second of one window and again in the first second
    of the next — twice the rate the provider published, which is how a runner earns a 429 it
    did not have to.
    """

    name: str
    capacity: int
    window_seconds: float
    available: float = field(init=False)
    last_refill: float = 0.0

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise BucketError(
                f"bucket {self.name!r} has capacity {self.capacity}. A zero-capacity bucket "
                f"parks its lane forever; if the limit does not exist, do not build a bucket "
                f"for it (see this module's docstring on `tpd: null`)"
            )
        if self.window_seconds <= 0:
            raise BucketError(f"bucket {self.name!r} has window {self.window_seconds}")
        self.available = float(self.capacity)

    @property
    def refill_per_second(self) -> float:
        return self.capacity / self.window_seconds

    def refill_to(self, now: float) -> None:
        """Advance this bucket's own clock to ``now``. **Its own** — hence *independent*."""
        if now < self.last_refill:
            raise BucketError(
                f"bucket {self.name!r} was asked to refill to {now}, which is BEFORE its last "
                f"refill at {self.last_refill}. Time does not run backwards and a runner that "
                f"accepted this would credit itself an allowance it never earned"
            )
        elapsed = now - self.last_refill
        self.last_refill = now
        self.available = min(float(self.capacity), self.available + elapsed * self.refill_per_second)

    def wait_seconds(self, cost: float, now: float) -> float:
        """How long until ``cost`` units are available. ``0.0`` means *now*.

        A cost larger than the whole capacity is a refusal rather than an infinite wait: no
        amount of waiting makes it admissible, and returning a very large number would look
        like patience.
        """
        if cost > self.capacity:
            raise BucketError(
                f"bucket {self.name!r} was offered a cost of {cost}, which exceeds its whole "
                f"capacity of {self.capacity}. Waiting cannot help. A single call larger than "
                f"a per-minute limit must be made smaller, not retried"
            )
        self.refill_to(now)
        if self.available >= cost:
            return 0.0
        return (cost - self.available) / self.refill_per_second

    def take(self, cost: float, now: float) -> None:
        """Spend ``cost``. **Refuses** if the bucket does not currently permit it."""
        if self.wait_seconds(cost, now) > 0.0:
            raise BucketError(
                f"bucket {self.name!r} does not permit {cost} now ({self.available:.2f} "
                f"available). Ask wait_seconds() first; a bucket refusal is a WAIT, not an "
                f"abort, and the two must not be confused (see this module's docstring)"
            )
        self.available -= cost

    def settle(self, cost: float, now: float) -> None:
        """Charge ``cost`` **unconditionally**, even into deficit. ⚠️ **NOT** :meth:`take`.

        ⚠️⚠️ **THIS IS THE ONLY METHOD THAT MAY DRIVE A BUCKET BELOW ZERO, AND THE REASON IS
        ARITHMETIC RATHER THAN POLICY.** :meth:`take` runs **before** a call and refuses what
        the bucket cannot afford, because at that moment refusing is a *wait* and nothing has
        been spent. ``settle`` runs **after** the provider has answered: **those tokens are
        already billed.** A bucket that declined to record them would be describing a spend
        that did not happen, and the runner would go on believing it had an allowance it had
        already used — which is exactly `INCIDENTS.md` **INC-143**.

        The deficit is not damage; it is a **delay**. :meth:`refill_to` credits it back at the
        published rate like any other shortfall, so the next :meth:`wait_seconds` simply
        returns a longer wait. **That is the whole self-correction**, and it introduces no
        constant of any kind (hard rule 9): every number here is either the reservation the
        run already used or a figure the provider itself returned.
        """
        if cost < 0:
            raise BucketError(
                f"bucket {self.name!r} was asked to settle {cost}, which is negative. A "
                f"settle CHARGES; a refund would hand back an allowance the provider has "
                f"already billed"
            )
        self.refill_to(now)
        self.available -= cost


@dataclass
class SlidingWindow:
    """One limit enforced as a **strict rolling window**: at most ``capacity`` units may fall
    inside any ``window_seconds``-long interval ending at the instant of admission.

    ⚠️ **WHY THIS EXISTS, AND WHY IT IS *SLOWER* THAN THE BUCKET IT REPLACES FOR TPM —
    `QUESTIONS.md` `Q-191`, RULED 2026-09-04. Class B: it changes PACING, not any published
    number.**

    :class:`Bucket`'s continuous refill and this rolling window are **two different limiter
    shapes**, and on the pilot's own trace they disagree. Replayed against the eight real
    calls in ``evals/usage/gemma-26b-2026-09-04.jsonl`` at ``tpm = 16,000``:

      * the **continuous bucket never empties** — its minimum level is **6,170 of 16,000**,
        so it would have admitted every call and sent a ninth immediately;
      * a **60-second rolling window is exceeded at call 7** (21,886 in the trailing minute)
        **and again at call 8** (22,069, 1.38x the limit) — **the two calls immediately
        before the provider answered HTTP 429.**

    ⚠️ **THE EVIDENCE CANNOT SAY WHICH SHAPE GOOGLE ACTUALLY USES** — `Q-191` is explicit
    that sliding, aligned-with-admission-counting and a burst rule are all consistent with
    nine data points. **The ruling picks the stricter shape on purpose:** a paced wait costs
    seconds, a 429 costs the lane, and hard rule 12 forbids retrying into another one. Ours
    was the permissive model; the provider's is at least as strict.

    ⚠️ **NO NEW CONSTANT (hard rule 9).** The capacity is ``config/lanes.yaml``'s existing
    ``tpm`` key and the window is :data:`_SECONDS_PER_MINUTE` — the same two arguments the
    TPM :class:`Bucket` was already built from. The *"per minute"* in *"tokens per minute"*
    **is** the window; nothing here was invented.

    ⚠️ **SCOPE, STATED EXACTLY: TPM ONLY.** RPM and RPD stay continuous buckets, because
    `Q-191` measured requests as *"not remotely implicated"* — a maximum of **3** requests in
    any 60-second window against a declared 30, and 9 that day against 14,400. TPD stays a
    continuous bucket too: the ruling names TPM, and a rolling *day* would hold a full day of
    events in memory to model a limit no evidence has implicated.
    """

    name: str
    capacity: int
    window_seconds: float
    #: ``(admitted_at, cost)``, oldest first. Pruned on every clock advance.
    _events: list[tuple[float, float]] = field(default_factory=list, init=False, repr=False)
    last_refill: float = 0.0

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise BucketError(
                f"window {self.name!r} has capacity {self.capacity}. A zero-capacity window "
                f"parks its lane forever; if the limit does not exist, do not build one "
                f"for it (see this module's docstring on `tpd: null`)"
            )
        if self.window_seconds <= 0:
            raise BucketError(f"window {self.name!r} has window {self.window_seconds}")

    def refill_to(self, now: float) -> None:
        """Advance to ``now``, **expiring** every event that has left the window.

        Named ``refill_to`` rather than ``prune`` so that it is interface-compatible with
        :class:`Bucket`: the scheduler and the driver call one protocol and must not have to
        know which shape a given limit is enforced with.
        """
        if now < self.last_refill:
            raise BucketError(
                f"window {self.name!r} was asked to refill to {now}, which is BEFORE its "
                f"last refill at {self.last_refill}. Time does not run backwards and a "
                f"runner that accepted this would credit itself an allowance it never earned"
            )
        self.last_refill = now
        horizon = now - self.window_seconds
        # Half-open: an event exactly `window_seconds` old has LEFT the window. A call at
        # t=60 is not inside the minute that began at t=0.
        self._events = [(at, cost) for at, cost in self._events if at > horizon]

    @property
    def used(self) -> float:
        """Units currently inside the window, as of the last :meth:`refill_to`."""
        return sum(cost for _at, cost in self._events)

    @property
    def available(self) -> float:
        """``capacity - used``. ⚠️ **May be NEGATIVE**, for the same reason
        :meth:`Bucket.settle` may drive a bucket below zero: a settle records tokens the
        provider has **already billed**, and a window that declined to record them would
        describe a spend that did not happen (`INCIDENTS.md` **INC-143**)."""
        return float(self.capacity) - self.used

    def wait_seconds(self, cost: float, now: float) -> float:
        """How long until ``cost`` units fit inside the window. ``0.0`` means *now*.

        ⚠️ **THE WAIT IS UNTIL EVENTS EXPIRE, NOT A LINEAR REFILL — and that is the whole
        behavioural difference from :class:`Bucket`.** A continuous bucket pays a debt down
        smoothly at ``capacity / window`` per second; a rolling window pays it in **steps**,
        as each admitted call reaches its ``window_seconds`` birthday and drops out.
        """
        if cost > self.capacity:
            raise BucketError(
                f"window {self.name!r} was offered a cost of {cost}, which exceeds its whole "
                f"capacity of {self.capacity}. Waiting cannot help. A single call larger "
                f"than a per-minute limit must be made smaller, not retried"
            )
        self.refill_to(now)
        if self.used + cost <= self.capacity:
            return 0.0
        # Expire events oldest-first until `cost` fits. Each event leaves the window
        # `window_seconds` after it was admitted.
        remaining = self.used
        for at, spent in self._events:
            remaining -= spent
            if remaining + cost <= self.capacity:
                return max(0.0, (at + self.window_seconds) - now)
        # Unreachable: `cost <= capacity` is checked above, so emptying the window suffices.
        raise BucketError(  # pragma: no cover - defensive
            f"window {self.name!r} could not admit {cost} even when empty; capacity "
            f"{self.capacity}. This is a bug in the expiry walk, not a rate limit"
        )

    def take(self, cost: float, now: float) -> None:
        """Record ``cost`` at ``now``. **Refuses** if the window does not currently permit it."""
        if self.wait_seconds(cost, now) > 0.0:
            raise BucketError(
                f"window {self.name!r} does not permit {cost} now ({self.available:.2f} "
                f"available in the trailing {self.window_seconds:.0f}s). Ask wait_seconds() "
                f"first; a refusal here is a WAIT, not an abort (see this module's docstring)"
            )
        self._events.append((now, float(cost)))

    def settle(self, cost: float, now: float) -> None:
        """Record ``cost`` **unconditionally**, even past capacity. ⚠️ **NOT** :meth:`take`.

        The provider has already billed these tokens (`INCIDENTS.md` **INC-143**). Recording
        them may push :attr:`used` above :attr:`capacity` — i.e. :attr:`available` negative —
        and that debt clears when the events carrying it **expire**, not gradually.
        """
        if cost < 0:
            raise BucketError(
                f"window {self.name!r} was asked to settle {cost}, which is negative. A "
                f"settle CHARGES; a refund would hand back an allowance the provider has "
                f"already billed"
            )
        self.refill_to(now)
        self._events.append((now, float(cost)))


@dataclass
class Buckets:
    """One lane's three (or four) independent limits. **All must permit a call.**

    RPM and RPD are request buckets; TPM and TPD are token limits. TPD exists only when the
    lane publishes one.

    ⚠️ **TPM IS A :class:`SlidingWindow`, NOT A :class:`Bucket`** — `QUESTIONS.md` `Q-191`,
    ruled 2026-09-04. Everything else is still a continuously-refilling :class:`Bucket`. The
    two shapes share a method protocol so that :mod:`.scheduler` and :mod:`..driver.run` do
    not branch on which is which.
    """

    lane: str
    rpm: Bucket
    tpm: SlidingWindow
    rpd: Bucket
    tpd: Bucket | None

    @classmethod
    def for_lane(
        cls, *, name: str, rpm: int, tpm: int, rpd: int, tpd: int | None
    ) -> "Buckets":
        return cls(
            lane=name,
            rpm=Bucket(f"{name}.rpm", rpm, _SECONDS_PER_MINUTE),
            # ⚠️ Q-191: the SAME two arguments the TPM Bucket took — the lane's own `tpm`
            # key and the minute that the "M" in TPM already names. No new constant.
            tpm=SlidingWindow(f"{name}.tpm", tpm, _SECONDS_PER_MINUTE),
            rpd=Bucket(f"{name}.rpd", rpd, _SECONDS_PER_DAY),
            tpd=None if tpd is None else Bucket(f"{name}.tpd", tpd, _SECONDS_PER_DAY),
        )

    def limits(self) -> dict[str, int]:
        """Which buckets this lane actually has, and their capacities. ⚠️ A lane with no
        published daily token cap has **three**, and this is how a reader sees that."""
        found = {"rpm": self.rpm.capacity, "tpm": self.tpm.capacity, "rpd": self.rpd.capacity}
        if self.tpd is not None:
            found["tpd"] = self.tpd.capacity
        return found

    def wait_seconds(self, *, tokens: int, now: float) -> float:
        """The longest wait across every bucket. ⚠️ **The MAXIMUM, never the sum.**

        A call is admitted only when **all** buckets permit it, so the wait is however long the
        slowest one needs — the buckets refill in parallel, on their own clocks, and adding
        their waits would idle a lane for a stretch none of its limits asked for.
        """
        waits = [
            self.rpm.wait_seconds(1, now),
            self.tpm.wait_seconds(tokens, now),
            self.rpd.wait_seconds(1, now),
        ]
        if self.tpd is not None:
            waits.append(self.tpd.wait_seconds(tokens, now))
        return max(waits)

    def permits(self, *, tokens: int, now: float) -> bool:
        return self.wait_seconds(tokens=tokens, now=now) == 0.0

    def take(self, *, tokens: int, now: float) -> None:
        """Spend one request and ``tokens`` tokens across every bucket. **Atomic in effect:**
        it checks all of them before spending any, so a partial take cannot leave a lane's
        buckets disagreeing about what happened."""
        if not self.permits(tokens=tokens, now=now):
            raise BucketError(
                f"lane {self.lane!r} does not permit a {tokens}-token call now; "
                f"wait {self.wait_seconds(tokens=tokens, now=now):.2f}s. A bucket refusal is "
                f"a WAIT, not an abort"
            )
        self.rpm.take(1, now)
        self.tpm.take(tokens, now)
        self.rpd.take(1, now)
        if self.tpd is not None:
            self.tpd.take(tokens, now)

    def settle(self, *, extra_tokens: int, now: float) -> None:
        """Charge the **token** buckets ``extra_tokens`` more, after the provider has billed.

        ⚠️ **THE TOKEN BUCKETS ONLY. NEVER THE REQUEST BUCKETS.** One call is **one** request
        however many tokens it turned out to cost; charging RPM or RPD a second time on the
        settle would park a lane on a limit it never came near.

        ⚠️ **WHY THIS EXISTS —** `INCIDENTS.md` **INC-143**, measured on the pilot's own log.
        A call is admitted at a *reservation*, which `driver/episode.py` computes as
        ``attacker.target_tokens_per_episode // attacker.turn_budget``. That expression is a
        **mean**, not an upper bound: a multi-turn conversation's per-call cost rises with
        context, so the reservation is above the real cost early and below it for the rest of
        the episode. On the pilot's eight real calls it was exceeded **seven** times, the
        largest by **2.59x**, and the buckets were under-charged by **18,930 tokens** in
        total. The ninth call was an HTTP 429.

        ``extra_tokens`` is ``max(0, actual - reservation)``, computed by the caller from the
        provider's own ``usage.total_tokens``. **A zero is normal** — it is what an
        under-budget call settles — and it is charged rather than special-cased so the call
        graph has one shape.
        """
        if extra_tokens:
            self.tpm.settle(extra_tokens, now)
            if self.tpd is not None:
                self.tpd.settle(extra_tokens, now)
