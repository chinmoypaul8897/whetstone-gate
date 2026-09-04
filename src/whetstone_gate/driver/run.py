"""**THE SHELL — the only module in this package that touches a filesystem, a clock or git.**

Hard rule 8's purity separation, applied to the chunk that finally runs something:
:mod:`whetstone_gate.driver.protocol`, :mod:`~whetstone_gate.driver.pilot` and
:mod:`~whetstone_gate.driver.episode` are pure of I/O; **this** module opens `config/`,
reads `evals/usage/`, writes `evals/episodes/` and `evals/checkpoints/`, asks git whether
`probe-v1` resolves, and reads a clock. Everything it reads is injected into the pure
layers below as data.

--------------------------------------------------------------------------------------
⚠️ THE FIVE REFUSALS THAT STAND BETWEEN THIS MODULE AND THE OPERATOR'S MONEY
--------------------------------------------------------------------------------------

Each is a **refusal**, not a warning, and each has its own reason:

1. **NO ARGUMENT SPENDS MONEY BY DEFAULT.** ``spend_real_tokens`` is a required, explicit
   flag with no default. A driver whose *absent* argument means *"call the provider"* is a
   driver one typo away from the pilot.
2. **`probe-v1` MUST RESOLVE.** `CONTEXT.md` §15.1 cuts that tag **before the pilot and
   before the calibration**, and `PROTOCOL.md` §6 makes the order *"not negotiable"*. A run
   that spends before it exists **has spent a single-shot run outside the
   pre-registration**, which nothing can undo. Checked with ``git rev-parse``, not assumed.
3. **A RESERVED LANE NEEDS AN EXPLICIT SANCTION.** `PROCESS.md` §8, through
   :func:`whetstone_gate.runner.lanes.refuse_reserved`, which takes the lanes this run's
   prompt named **one by one** and has no wildcard.
4. **BOTH CEILINGS, OR NEITHER.** :class:`whetstone_gate.runner.budget.Ceilings` has no
   one-ceiling constructor, and hard rule 12 is explicit: *"A sanction of 'max N calls'
   alone is not a sanction."* ⚠️ **They are applied PER LANE and are never pooled** — golden
   8 fixture E.
5. **THE DAY'S USAGE FILE IS READ BEFORE THE FIRST CALL OF EVERY LANE.** `CLAUDE.md` §4.
   A lane resumed mid-window whose accumulator started at zero would run its whole
   sanctioned ceiling a **second** time.

--------------------------------------------------------------------------------------
⚠️ THE DRY RUN, AND WHY IT MAY NOT WRITE INTO THIS REPOSITORY'S `evals/`
--------------------------------------------------------------------------------------

A dry run makes **no network call at all**. It is how the operator rehearses the whole pilot
— every episode, every ledger, every checkpoint, the resume, the duplicate refusal and the
token accounting — before a single token is spent, and it is this chunk's done-when.

⚠️ **IT REQUIRES AN `out_root` AND REFUSES ONE INSIDE THE REPOSITORY.** A rehearsal ledger
sitting in `evals/episodes/` is byte-shaped exactly like a scored one, and `evals/` is
**append-only with operator-only deletion** (`CLAUDE.md` §4) — so a dry run that wrote there
could not be cleaned up by any session and would leave the record carrying episodes no
provider ever produced. The refusal is measured against
:func:`whetstone_gate.config.repo_root`, not against a string.

--------------------------------------------------------------------------------------
⚠️ `evals/` IS APPEND-ONLY: THERE IS NO DELETION PATH IN THIS PACKAGE, AND IT IS ASSERTED
--------------------------------------------------------------------------------------

No module under ``driver/`` calls ``os.remove``, ``os.unlink``, ``os.rmdir``,
``shutil.rmtree``, ``Path.unlink``, ``Path.rmdir`` or ``truncate``, and
``tests/test_c12_driver.py`` asserts the absence by parsing every module's **AST** — the
same guard :mod:`whetstone_gate.runner.checkpoint` carries, because `CLAUDE.md` §4 makes
deletion operator-only and a ``force=True`` parameter is how that rule gets round by a
session in a hurry.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from whetstone_gate import config as cfg
from whetstone_gate._console import say
from whetstone_gate.attacker import corpus as attacker_corpus
from whetstone_gate.driver import pilot as pilot_module
from whetstone_gate.driver.clients import MeteredModelClient, ModelReply
from whetstone_gate.driver.episode import (
    DriverEpisode,
    DriverError,
    EpisodeSettings,
    run_one_episode,
)
from whetstone_gate.gates import shell as gate_shell
from whetstone_gate.ledger import store as ledger_store
from whetstone_gate.ledger.chain import Ledger, load_chain_spec
from whetstone_gate.runner import lanes as runner_lanes
from whetstone_gate.runner import report as runner_report
from whetstone_gate.runner import usage as runner_usage
from whetstone_gate.runner.budget import Ceilings, LaneBudget
from whetstone_gate.runner.checkpoint import CheckpointStore, build_document
from whetstone_gate.runner.episodes import EpisodeKey, EpisodeOutcome, RunDenominator
from whetstone_gate.runner.keys import missing_keys
from whetstone_gate.runner.scheduler import LaneState, Scheduler, build_lane_state
from whetstone_gate.world import generator as world_generator
from whetstone_gate.world import oracle as world_oracle
from whetstone_gate.world import semantics as world_semantics
from whetstone_gate.world import settings as world_settings

#: Where a published episode's ledger lives, relative to ``out_root``. `CONTEXT.md` §16's
#: tree: ``evals/episodes/`` is *"every transcript, including boring ones"*.
EPISODE_DIR = ("evals", "episodes")

#: The tag `CONTEXT.md` §15.1 requires **before** the pilot and **before** the calibration.
PROBE_TAG = "probe-v1"

#: The three arms that run a gate judge. `PROTOCOL.md` §2.1's own table, and `CONTEXT.md`
#: §13.4's gate-judge row is *"arms 2/2S/3 only"*. Written out rather than derived from
#: `gates/`: a resumed-run refusal keying off an import of the gate package would put the
#: gate's module graph inside the driver's for the sake of three strings.
JUDGED_ARMS: frozenset[str] = frozenset({"2", "2S", "3"})


class RunRefused(RuntimeError):
    """A precondition this driver will not run without. **Always a refusal, never a warning.**"""


# --------------------------------------------------------------------------------------
# What a run is asked to do
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class RunRequest:
    """One invocation. ⚠️ **No field here has a money-spending default.**"""

    matrix: pilot_module.PilotMatrix
    out_root: Path
    ceilings: Ceilings
    s3_binding: str
    spend_real_tokens: bool
    sanctioned_lanes: frozenset[str] = frozenset()

    allow_absent_corpus: bool = False
    """⚠️ **DRY-RUN ONLY, AND A REAL RUN IGNORES IT BY REFUSING FIRST.**

    `CONTEXT.md` §11.3 publishes a **corpus-versus-improvisation split**, and
    :func:`whetstone_gate.attacker.corpus.load_entries` refuses an absent corpus because
    zero entries *"would publish a 100%-improvised split, which is a broken instrument
    reporting a headline"*. That refusal is right and it stays the default.

    A **rehearsal** publishes no number at all, so it may run without one — but only when
    the operator types this, and the report then carries the limitation in terms.
    """

    @property
    def dry_run(self) -> bool:
        return not self.spend_real_tokens


@dataclass
class RunResult:
    """Everything one invocation produced. The **report** is what the operator reads."""

    denominator: RunDenominator = field(default_factory=RunDenominator)
    budgets: dict[str, LaneBudget] = field(default_factory=dict)
    episodes: list[DriverEpisode] = field(default_factory=list)
    already_complete: list[str] = field(default_factory=list)
    preflight_lines: list[str] = field(default_factory=list)
    report: str = ""

    resumed: list[dict[str, Any]] = field(default_factory=list)
    """The **checkpoint documents** of episodes this invocation skipped as already done.

    ⚠️ **THEY ARE READ BACK, NOT ASSUMED, AND THEY ARE IN THE DENOMINATOR.**
    `INCIDENTS.md` **INC-110**, measured by this chunk's own dry run before it was
    committed: with only *this invocation's* episodes counted, the **second** run of the
    same command printed ``episodes attempted: 0``, ``DENOMINATOR: 0`` and a pilot
    measurement of ``0 tokens over 0 episodes`` — a completed 20-episode pilot reading as
    nothing at all, and reading **clean** while it did. That is `INC-103`'s shape (a
    denominator running where it flatters) in this chunk's own code. Hard rule 11 counts
    *"skipped cases"* by name.
    """

    @property
    def completed(self) -> int:
        return sum(1 for episode in self.episodes if not episode.truncated) + sum(
            1 for document in self.resumed if not document["truncated"]
        )

    @property
    def truncated(self) -> int:
        return sum(1 for episode in self.episodes if episode.truncated) + sum(
            1 for document in self.resumed if document["truncated"]
        )

    def attacker_tokens(self, matrix: pilot_module.PilotMatrix) -> int:
        """Attacker tokens across every episode in the denominator. **BY ROLE, not by lane.**

        ⚠️ **The judge's tokens are NOT in this figure.** §13.4 budgets the attacker and the
        gate judge as **separate rows**, and the N rule keys off *"measured **attacker**
        tokens/episode"*. Adding the judge's would inflate the number that selects N.

        ⚠️ **AND THE SEPARATION IS BY ROLE, BECAUSE §13.3.2 PUTS BOTH ON `gemma-26b`.**
        `INCIDENTS.md` **INC-111**: a lane-based filter dropped every **reference-attacker**
        episode — the half the rule is chiefly about — because its lane equalled the
        judge's, and the figure that survived was the ladder half alone.

        ⚠️ **A RESUMED JUDGED ARM REFUSES, and that is `INC-111`'s uncovered half.**
        :data:`whetstone_gate.runner.checkpoint.DOCUMENT_KEYS` carries one ``tokens_spent``
        and **no attacker/judge split** — it is C11's frozen schema and outside this chunk's
        fence — so a resumed episode of arm 2, 2S or 3 cannot have its attacker share
        recovered. For a judge-less arm ``tokens_spent`` **is** the attacker figure, so the
        resume is exact there. A refusal, never an estimate. `OPEN_FINDINGS.md` **OF-240**.
        """
        ran = sum(episode.attacker_tokens for episode in self.episodes)
        if not self.resumed:
            return ran
        if matrix.arm in JUDGED_ARMS:
            raise RunRefused(
                f"this invocation resumed {len(self.resumed)} episode(s) of arm "
                f"{matrix.arm!r}, which runs a gate judge, and a checkpoint carries ONE "
                f"tokens_spent with no attacker/judge split (runner/checkpoint.py's "
                f"DOCUMENT_KEYS, C11's schema). The attacker share of a resumed judged "
                f"episode is therefore not recoverable, and CONTEXT.md S13.4's figure is "
                f"about ATTACKER tokens. This is a refusal rather than an estimate "
                f"(OPEN_FINDINGS.md OF-240). Run the pilot's judged arm in one go, or read "
                f"the split off evals/usage/ once it carries a role column"
            )
        # ⚠️ INC-110: a resumed run's tokens live in its CHECKPOINTS, not in this
        # invocation's memory. Omitting them made a completed pilot measure zero.
        return ran + sum(int(document["tokens_spent"]) for document in self.resumed)


# --------------------------------------------------------------------------------------
# Preconditions
# --------------------------------------------------------------------------------------


def probe_tag_resolves(repo_root: Path) -> bool:
    """Does ``git rev-parse probe-v1`` resolve? **Measured, never assumed.**

    ⚠️ `CONTEXT.md` §15.1: *"The calibration may not begin until `git rev-parse probe-v1`
    resolves"*, and `PROTOCOL.md` §6 puts the pilot under the same gate. A driver that ran
    without it would have spent a **single-shot** run outside the pre-registration, and
    `PROCESS.md` §6b makes the first completed execution **the** run whatever it contains.
    """
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--verify", "-q", f"{PROBE_TAG}^{{commit}}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
    except OSError:  # pragma: no cover - git is a hard prerequisite of this repository
        return False
    return completed.returncode == 0


def refuse_out_root_inside_the_repository(out_root: Path, repo_root: Path) -> None:
    """A dry run may not write under the repository. See this module's docstring."""
    resolved = out_root.resolve()
    root = repo_root.resolve()
    if resolved == root or root in resolved.parents:
        raise RunRefused(
            f"a DRY RUN may not write into the repository ({resolved} is under {root}). "
            f"A rehearsal ledger in evals/episodes/ is byte-shaped exactly like a scored "
            f"one, and evals/ is APPEND-ONLY with OPERATOR-ONLY deletion (CLAUDE.md S4) - "
            f"so no session could remove it and the record would carry episodes no provider "
            f"ever produced. Point --out-root at a directory outside the repository"
        )


@dataclass(frozen=True)
class Preflight:
    """What the preconditions found. ``corpus_entries`` is resolved here, not later.

    ⚠️ **THE CORPUS IS RESOLVED IN PREFLIGHT ON PURPOSE.** Measured in this repository on
    2026-09-03: ``corpora/fetched/`` does not exist, so the FIRST episode of a run raises
    :class:`whetstone_gate.attacker.corpus.CorpusUnavailable` — **after**
    `evals/pilot/RUN_DECLARED.md` has been committed and pushed and the single-shot clock
    has started (`PROCESS.md` §6b). A precondition discovered on episode 1 of a single-shot
    run is a precondition discovered too late, and `PROTOCOL.md` §6's *"the order is not
    negotiable"* list does not mention the corpora at all. `QUESTIONS.md` **Q-145**.
    """

    lines: list[str]
    corpus_entries: tuple[Any, ...]


def preflight(request: RunRequest, *, repo_root: Path, utc_date: str) -> Preflight:
    """Every precondition, in order, as printable lines. **Raises on the first refusal.**"""
    lines: list[str] = ["PREFLIGHT"]
    lines.append(
        f"  mode                   : "
        f"{'REAL PROVIDER CALLS' if request.spend_real_tokens else 'DRY RUN - no network call'}"
    )
    lines.append(f"  out root               : {request.out_root}")
    lines.append(f"  ceilings PER LANE      : {request.ceilings.call_ceiling} calls, "
                 f"{request.ceilings.token_ceiling} tokens   (never pooled - golden 8 E)")
    lines.append(f"  S3 binding (Q-141)     : {request.s3_binding}")

    resolves = probe_tag_resolves(repo_root)
    lines.append(f"  {PROBE_TAG} resolves      : {resolves}")
    if request.dry_run:
        refuse_out_root_inside_the_repository(request.out_root, repo_root)
        lines.append("  lane reservation       : NOT EXERCISED - a dry run dispatches to no")
        lines.append("                           provider, so PROCESS.md S8's refusal has")
        lines.append("                           nothing to refuse. The REAL path is asserted")
        lines.append("                           in tests/test_c12_driver.py")
        lines.append("  API keys               : NOT READ - no call is made. runner/keys.py")
        lines.append("                           returns a BOOLEAN and has no path to a value")
        entries, corpus_line = _resolve_corpus(request)
        lines.append(corpus_line)
        return Preflight(lines=lines, corpus_entries=entries)

    if not resolves:
        raise RunRefused(
            f"{PROBE_TAG} does not resolve, so this run REFUSES ENTIRELY. CONTEXT.md S15.1 "
            f"cuts that tag BEFORE the pilot and BEFORE the arm-1 calibration, and "
            f"PROTOCOL.md S6 calls the order 'not negotiable'. Both runs are SINGLE-SHOT "
            f"(PROCESS.md S6b): the first execution that runs to completion IS the run, so "
            f"a run started before the tag exists has spent it OUTSIDE the pre-registration "
            f"and nothing can undo that"
        )

    lanes_in_play = sorted({request.matrix.lane_for(key) for key in request.matrix.keys()}
                           | {request.matrix.judge_lane})
    for lane in lanes_in_play:
        runner_lanes.refuse_reserved(lane, sanctioned=request.sanctioned_lanes)
    lines.append(f"  lanes sanctioned       : {sorted(request.sanctioned_lanes) or 'none'}")

    providers = runner_lanes.providers_for(lanes_in_play)
    absent = missing_keys(providers)
    if absent:
        raise RunRefused(
            f"the environment does not carry {absent}. Only the NAMES are read here - "
            f"runner/keys.py returns a boolean and has no code path that reads a value "
            f"(CLAUDE.md S4). An episode that fails on a missing credential halfway through "
            f"is an episode that has already spent tokens"
        )
    lines.append(f"  API key NAMES present  : {providers} (values never read)")

    log = runner_usage.UsageLog.under(request.out_root)
    for lane in lanes_in_play:
        tokens, calls, existed = runner_usage.preflight(
            log,
            lane,
            utc_date,
            {
                "call_ceiling": request.ceilings.call_ceiling,
                "token_ceiling": request.ceilings.token_ceiling,
            },
        )
        lines.append(
            f"  usage {lane}-{utc_date}: {tokens} tokens, {calls} calls already spent "
            f"today (file existed: {existed})"
        )
    entries, corpus_line = _resolve_corpus(request)
    lines.append(corpus_line)
    return Preflight(lines=lines, corpus_entries=entries)


def _resolve_corpus(request: RunRequest) -> tuple[tuple[Any, ...], str]:
    """Load the pinned attacker corpora, or refuse. **Before a token is spent, not after.**

    ⚠️ **AN ABSENT CORPUS IS A REFUSAL FOR A REAL RUN, ALWAYS.** `CONTEXT.md` §11.3 publishes
    the corpus-versus-improvisation split, and a run with no corpus publishes *"100%
    improvised"* — a broken instrument reporting a headline. The one exception is a
    **rehearsal**, which publishes nothing and must type ``--allow-absent-corpus`` to get it.
    """
    try:
        entries = _load_corpus()
    except attacker_corpus.CorpusUnavailable as unavailable:
        if request.spend_real_tokens or not request.allow_absent_corpus:
            raise RunRefused(
                f"the pinned attacker corpora are not present: {unavailable}. "
                f"CONTEXT.md S11.3 publishes a corpus-versus-improvisation split and a run "
                f"with no corpus publishes '100% improvised', which is a broken instrument "
                f"reporting a headline. Fetch them with corpora/MANIFEST.md section 2 "
                f"BEFORE evals/pilot/RUN_DECLARED.md is pushed - the pilot is SINGLE-SHOT "
                f"(PROCESS.md S6b) and a precondition found on episode 1 is found too late. "
                f"A DRY RUN may proceed without them by typing --allow-absent-corpus, and "
                f"the report then says so"
            ) from None
        return (), (
            "  attacker corpora       : ABSENT, and this run was told to proceed anyway. "
            "! CONTEXT.md S11.3's corpus-vs-improvisation split would read 100% IMPROVISED. "
            "Legal ONLY because a dry run publishes no number (QUESTIONS.md Q-145)"
        )
    return entries, f"  attacker corpora       : {len(entries)} pinned entries, hashes verified"


# --------------------------------------------------------------------------------------
# Pacing — the only clock in this package
# --------------------------------------------------------------------------------------


@dataclass
class _PacedClient:
    """Wraps an injected client with :mod:`whetstone_gate.runner.buckets` pacing.

    ⚠️ **A BUCKET REFUSAL IS A WAIT, NEVER AN ABORT** (:mod:`whetstone_gate.runner.buckets`),
    and this is the only place in the driver that can sleep. The clock and the sleep are both
    **injected**, so a test drives a whole day's pacing in microseconds.

    ⚠️ **THE BUCKETS ARE TAKEN AT THE RESERVATION, NOT AT THE SETTLED COST**, because pacing
    happens *before* the call and the settled cost does not exist yet. A reservation is an
    upper bound, so this paces **conservatively** — it can only make the runner slower than
    the provider's published limit, never faster, which is the direction that does not earn
    a 429.
    """

    inner: MeteredModelClient
    attacker_buckets: Any
    judge_buckets: Any
    attacker_reservation: int
    judge_reservation: int
    clock: Callable[[], float]
    sleep: Callable[[float], None]

    def complete_attacker(
        self, *, messages: tuple[dict[str, str], ...], temperature: float, lane: str
    ) -> ModelReply:
        self._agree(lane, self.attacker_buckets, role="attacker")
        self._pace(self.attacker_buckets, self.attacker_reservation)
        return self.inner.complete_attacker(
            messages=messages, temperature=temperature, lane=lane
        )

    def complete_judge(self, *, system: str, user: str, lane: str) -> ModelReply:
        self._agree(lane, self.judge_buckets, role="judge")
        self._pace(self.judge_buckets, self.judge_reservation)
        return self.inner.complete_judge(system=system, user=user, lane=lane)

    @staticmethod
    def _agree(lane: str, buckets: Any, *, role: str) -> None:
        """⚠️⚠️ **Q-161: THE TWO INDEPENDENT COPIES OF THE LANE MUST AGREE, AND THIS IS THE
        ONLY PLACE IN THE RUN WHERE BOTH ARE IN SCOPE AT ONCE.**

        The threaded ``lane`` comes down the call chain from
        :class:`whetstone_gate.driver.episode._MeteredCall`, which was built with
        ``lane=request.matrix.lane_for(key)``. ``buckets.lane`` came the other way, from
        ``lane_states[lane]`` in this module's dispatch loop. **Both derive from the same
        source and neither reads the other**, so a disagreement means the pacing this call
        was charged for belongs to a different lane than the call itself — which is
        `INCIDENTS.md` **INC-112**'s shape, where a 429 stopped ten episodes of an arm that
        makes no call on the lane that raised it.

        ⚠️ **THIS IS NOT DEFENSIVE PADDING; IT IS THE ONE CHECK THE THREADING EARNS.** Before
        the ruling the client had no lane and there was nothing to disagree with. Now there
        are two paths carrying it, so agreement is checkable — and a check that could only
        ever pass would not be worth the line.
        """
        # ⚠️ READ STATICALLY. The first draft of this line used `getattr(buckets, "lane",
        # None)` and the RAW_SOURCE_SCAN tripwire refused it by name: a dynamic reach is
        # INC-51's species and is invisible to an AST walk. `runner/buckets.py`'s LaneBuckets
        # declares `lane` as a field, so there is nothing to be defensive about.
        held = buckets.lane
        if held != lane:
            raise DriverError(
                f"a {role} call arrived threaded with lane {lane!r} while its pacing buckets "
                f"are lane {held!r}. These are two independent copies of one value — the "
                f"threaded one from episode._MeteredCall, the bucket one from this module's "
                f"lane_states — and a disagreement means this call is paced against one "
                f"lane's limits and dispatched to another provider. It stops here rather "
                f"than spending: a misroute is invisible until the per-lane token figures "
                f"are read (QUESTIONS.md Q-161)"
            )

    def _pace(self, buckets: Any, tokens: int) -> None:
        """Wait until the buckets permit ``tokens``, then charge them. **One clock read.**

        ⚠️⚠️ **`Q-179`(1), RULED 2026-09-04 — THE PACER USED TO READ THE CLOCK TWICE AND LET
        THE SECOND READING REFUSE WHAT THE FIRST AUTHORISED.** The pre-ruling body was::

            wait = buckets.wait_seconds(tokens=tokens, now=self.clock())
            if wait > 0:
                self.sleep(wait)
            buckets.take(tokens=tokens, now=self.clock())

        :meth:`whetstone_gate.runner.buckets.Buckets.take` admits only on
        ``wait_seconds(...) == 0.0`` **exactly**, so a ``sleep`` that returned even one
        microsecond before the monotonic clock had advanced by the full wait turned a bucket
        refusal into a :class:`~whetstone_gate.runner.buckets.BucketError` — **an abort,
        which this module's own docstring says a bucket refusal must never be.**
        ⚠️ **MEASURED ON THIS PROJECT'S OWN PLATFORM** (`INCIDENTS.md` **INC-134**): in 300
        samples on the operator's win32 machine, ``time.sleep(w)`` returned before
        ``time.monotonic`` had advanced by ``w`` **139 times**, worst shortfall **-0.011 s**.

        ⚠️ **THE FIX IS EXACT AND INTRODUCES NO CONSTANT**, which the ruling requires in
        capitals: *"NO EPSILON, NO TOLERANCE, NO GRACE CONSTANT — a tolerance is a hardcoded
        spec value and hard rule 9 forbids it."* One reading of the clock decides **both**
        questions. When the wait is not positive, ``take`` is called with **that same**
        ``now``, so ``refill_to(now)`` sees ``elapsed == 0`` and cannot arrive at a smaller
        balance than the one ``wait_seconds`` just approved. **The admission cannot expire
        between being granted and being used, because no time passes between them.**
        """
        while True:
            now = self.clock()
            wait = buckets.wait_seconds(tokens=tokens, now=now)
            if wait <= 0:
                buckets.take(tokens=tokens, now=now)
                return
            self.sleep(wait)


# --------------------------------------------------------------------------------------
# The run
# --------------------------------------------------------------------------------------


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _date(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%d")


def execute(
    request: RunRequest,
    *,
    client: MeteredModelClient,
    corpus_entries: Sequence[Any] | None = None,
    now: Callable[[], datetime] = _utc_now,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    repo_root: Path | None = None,
) -> RunResult:
    """Run every pending episode of ``request.matrix``, then report. **Resumable.**

    ⚠️ **RE-RUNNING THIS IS A NO-OP OVER COMPLETED EPISODES.** Every key is filtered against
    the published checkpoints by :meth:`whetstone_gate.runner.scheduler.Scheduler.pending`
    on **every** invocation, so a resume dispatches only what has no checkpoint — zero
    duplicates and zero re-runs — and a crash costs one episode rather than the run.

    ⚠️ **AND A COMPLETED EPISODE IS STILL IN THE DENOMINATOR.**
    :attr:`RunResult.already_complete` names every skipped slug, and the report prints the
    count: hard rule 11 counts *"skipped cases"* too, and a resumed run that reported only
    what it re-ran would publish a shrinking denominator every time it was restarted.
    """
    root = repo_root or cfg.repo_root()
    started = now()
    result = RunResult()
    checks = preflight(request, repo_root=root, utc_date=_date(started))
    result.preflight_lines = checks.lines

    settings = EpisodeSettings.from_config(s3_binding=request.s3_binding)
    if settings.attacker.turn_budget != request.matrix.turn_budget:
        raise DriverError(
            f"the matrix says turn budget {request.matrix.turn_budget} and config/ says "
            f"{settings.attacker.turn_budget}. Both read attacker.turn_budget; a difference "
            f"means one of them stopped reading config/"
        )

    # ⚠️ Resolved by PREFLIGHT, before any spend — never lazily on episode 1. See Preflight.
    entries = tuple(corpus_entries) if corpus_entries is not None else checks.corpus_entries
    denial = gate_shell.load_gate_texts().generic_denial
    chain_spec = load_chain_spec()
    semantics_spec = world_settings.load_semantics_spec()
    oracle = world_oracle.load()

    checkpoints = CheckpointStore.under(request.out_root)
    usage_log = runner_usage.UsageLog.under(request.out_root)
    episode_dir = request.out_root.joinpath(*EPISODE_DIR)

    lane_states = _lane_states(request, usage_log, date=_date(started))
    result.budgets = {name: state.budget for name, state in lane_states.items()}
    scheduler = Scheduler(
        lanes=lane_states, sanctioned_lanes=request.sanctioned_lanes, clock=clock
    )

    keys = request.matrix.keys()
    completed_slugs = checkpoints.completed()
    result.already_complete = sorted(
        key.slug for key in keys if key.slug in completed_slugs
    )
    # ⚠️ INC-110. A SKIPPED EPISODE IS STILL IN THE DENOMINATOR (hard rule 11 counts
    # "skipped cases" by name), and its figures are read back off the checkpoint it
    # published rather than assumed. Recorded BEFORE dispatch so a run that dispatches
    # nothing still reports the whole matrix.
    for key in keys:
        if key.slug not in completed_slugs:
            continue
        document = checkpoints.read(key)
        result.resumed.append(document)
        result.denominator.record(
            EpisodeOutcome(
                key=key,
                started=True,
                turns_run=int(document["turns_run"]),
                turn_budget=int(document["turn_budget"]),
                tokens_spent=int(document["tokens_spent"]),
                cause=document["cause"],
            )
        )
    pending = scheduler.pending(keys, completed_slugs)

    for key in pending:
        lane = request.matrix.lane_for(key)
        judge_lane = request.matrix.judge_lane
        seed = int(key.seed_or_task)
        arm = key.arm
        attacker_state = lane_states[lane]
        judge_state = lane_states[judge_lane]
        # ⚠️ **A STOPPED JUDGE LANE BLOCKS ONLY AN ARM THAT USES ONE.** `INCIDENTS.md`
        # **INC-112**, measured by this chunk's own 429 rehearsal: because `CONTEXT.md`
        # §13.3.2 puts the gate judge on `gemma-26b`, a 429 that stopped that lane also
        # stopped all TEN `qwen-27b` episodes of **arm 1** — an arm with no gate and no
        # judge call — and booked them under `PROVIDER_ERROR`, a cause that was simply
        # wrong. Golden 8 fixture D's own warning, one level up: an accumulator that stops
        # a lane which has budget "costs the run episodes it was entitled to".
        blocking_lane: str | None = None
        if attacker_state.budget.stopped:
            blocking_lane = lane
        elif arm in JUDGED_ARMS and judge_state.budget.stopped:
            blocking_lane = judge_lane
        if blocking_lane is not None:
            # The episodes still on it are COUNTED under their real cause and printed —
            # never quietly dropped, and never under a fallback category.
            result.denominator.record(
                _not_started(
                    key, settings.attacker.turn_budget, scheduler, blocking_lane, clock()
                )
            )
            continue

        episode_started = now()
        paced = client
        if request.spend_real_tokens:
            paced = _PacedClient(
                inner=client,
                attacker_buckets=attacker_state.buckets,
                judge_buckets=judge_state.buckets,
                attacker_reservation=settings.attacker_call_reservation_tokens,
                judge_reservation=settings.judge_call_reservation_tokens,
                clock=clock,
                sleep=sleep,
            )

        world = world_semantics.build(
            world_generator.generate_world(seed), semantics_spec, oracle
        )
        gate = gate_shell.build_gate(arm, _placeholder_judge_client(arm))
        ledger = Ledger(spec=chain_spec, seed=seed, arm=arm)

        episode = run_one_episode(
            key=key,
            seed=seed,
            arm=arm,
            lane=lane,
            world=world,
            gate=gate,
            ledger=ledger,
            client=paced,
            attacker_budget=attacker_state.budget,
            judge_budget=judge_state.budget,
            judge_lane=judge_lane,
            settings=settings,
            generic_denial=denial,
            corpus_entries=entries,
            on_usage=_usage_sink(usage_log, key, date=_date(episode_started), now=now),
        )
        _publish(
            episode,
            episode_dir=episode_dir,
            checkpoints=checkpoints,
            utc_started=_iso(episode_started),
            utc_finished=_iso(now()),
        )
        result.episodes.append(episode)
        result.denominator.record(episode.outcome())

    result.denominator.reconcile()
    result.report = render(request, result, started=started)
    return result


def _placeholder_judge_client(arm: str) -> Any:
    """A stand-in the gate is built with and which :func:`.episode.run_one_episode` replaces.

    ⚠️ **IT IS NOT A MODEL AND IT CANNOT BE CALLED.** ``build_gate`` requires *some* client
    for arms 2, 2S and 3 and requires **none** for arms 1 and 4 — *"a control arm or a
    deterministic kernel handed a model client is an arm whose behaviour could depend on
    one"*. So this returns ``None`` for the two clientless arms, and for the other three a
    object whose only method **raises**: if the metered client were ever not wired in, the
    run would stop loudly instead of quietly asking an object that is not a provider.
    """
    if arm not in ("2", "2S", "3"):
        return None
    return _UnwiredJudge()


class _UnwiredJudge:
    """Raises. See :func:`_placeholder_judge_client`."""

    def complete(self, *, system: str, user: str) -> str:
        raise DriverError(
            "a model-backed arm's gate was asked for a verdict before the metered judge "
            "client was wired in. This object exists so that failure is LOUD"
        )


def _load_corpus() -> tuple[Any, ...]:
    """The pinned attacker corpora. ⚠️ **An absent corpus is a refusal, never an empty one.**

    :func:`whetstone_gate.attacker.corpus.load_entries`' own words: zero entries *"would
    publish a 100%-improvised split"* for `CONTEXT.md` §11.3, which is a broken instrument
    reporting a headline.
    """
    return attacker_corpus.load_entries(attacker_corpus.load_sources())


def _lane_states(
    request: RunRequest, usage_log: runner_usage.UsageLog, *, date: str
) -> dict[str, LaneState]:
    """One :class:`~whetstone_gate.runner.scheduler.LaneState` per lane in play.

    ⚠️ **SEEDED FROM THE DAY'S USAGE FILE** (`CLAUDE.md` §4). A lane resumed mid-window whose
    accumulator started at zero would run its whole sanctioned ceiling a second time, which
    is the overspend hard rule 12 exists to prevent.
    """
    declared = runner_lanes.load_lanes()
    names = sorted(
        {request.matrix.lane_for(key) for key in request.matrix.keys()}
        | {request.matrix.judge_lane}
    )
    states: dict[str, LaneState] = {}
    for name in names:
        lane = declared[name]
        tokens, calls, _existed = usage_log.spent_today(name, date)
        states[name] = build_lane_state(
            name=name,
            rpm=lane.rpm,
            tpm=lane.tpm,
            rpd=lane.rpd,
            tpd=lane.tpd,
            call_ceiling=request.ceilings.call_ceiling,
            token_ceiling=request.ceilings.token_ceiling,
            already_spent_tokens=tokens,
            already_used_calls=calls,
        )
    return states


def _usage_sink(
    usage_log: runner_usage.UsageLog,
    key: EpisodeKey,
    *,
    date: str,
    now: Callable[[], datetime],
) -> Callable[[str, int, str], None]:
    """One episode's usage-row writer. **Append-only, one row per call, live.**

    `CONTEXT.md` §13.5(4): *"per-model token accounting, logged LIVE … so the day's remaining
    allowance is observable MID-RUN rather than discovered at exhaustion."* The row carries
    the provider's own ``total_tokens`` and passes through
    :func:`whetstone_gate.runner.redaction.refuse_if_secret_bearing` before it is serialised.
    """

    def sink(lane: str, tokens: int, outcome: str) -> None:
        usage_log.append(
            model=lane,
            date=date,
            utc=_iso(now()),
            lane=lane,
            episode=key.slug,
            total_tokens=tokens,
            outcome=outcome,
        )

    return sink


def _not_started(
    key: EpisodeKey,
    turn_budget: int,
    scheduler: Scheduler,
    lane: str,
    now_seconds: float,
) -> Any:
    """An episode that was never dispatched, **with its cause**. Hard rule 11."""
    cause = scheduler.unfinished_cause_for(lane, now_seconds)
    if cause is None:
        # ⚠️ INC-112. The old form defaulted to PROVIDER_ERROR here, and that is how ten
        # arm-1 episodes were booked under a cause that never happened. "It did not run and
        # nobody wrote down why" is exactly the missing trace Razorpay's B.9 names, and a
        # WRONG category is worse than a loud stop because it reads as a real finding.
        raise DriverError(
            f"{key.slug} was not dispatched and lane {lane!r} reports no cause. Hard rule "
            f"11 requires every dropped episode to be COUNTED AND CATEGORISED; a fallback "
            f"category here would publish a failure mode that did not occur"
        )
    return EpisodeOutcome(
        key=key,
        started=False,
        turns_run=0,
        turn_budget=turn_budget,
        tokens_spent=0,
        cause=cause,
    )


def _publish(
    episode: DriverEpisode,
    *,
    episode_dir: Path,
    checkpoints: CheckpointStore,
    utc_started: str,
    utc_finished: str,
) -> None:
    """Publish one episode. ⚠️ **LEDGER FIRST, THEN THE CHECKPOINT, AND THE ORDER IS THE RULE.**

    Both writes are atomic (a sibling temporary file plus :func:`os.replace`) and both refuse
    an existing file whose bytes differ — `evals/` is append-only and deletion is
    operator-only.

    **The checkpoint is written LAST because the checkpoint is what "done" means.** A crash
    between the two leaves a ledger with no checkpoint, so the resume re-runs that episode
    and the ledger write is then either byte-identical (a no-op) or a **refusal** naming the
    file — which is loud. The other order would mark an episode complete whose ledger was
    never written, and the resume would skip it: **an episode silently missing from the
    record**, which is hard rule 11's exact shape.
    """
    ledger_path = episode_dir / f"{episode.key.slug}.json"
    ledger_store.write(ledger_path, episode.ledger)
    checkpoints.publish(
        episode.key,
        build_document(
            episode.key,
            lane=episode.lane,
            utc_started=utc_started,
            utc_finished=utc_finished,
            turns_run=episode.turns_run,
            turn_budget=episode.turn_budget,
            tokens_spent=episode.tokens_spent,
            calls_used=episode.calls_used,
            cause=episode.cause,
            ledger_path=str(ledger_path.as_posix()),
        ),
    )


# --------------------------------------------------------------------------------------
# The report
# --------------------------------------------------------------------------------------


def render(request: RunRequest, result: RunResult, *, started: datetime) -> str:
    """The whole run as one ASCII block. **Per model, every zero printed, nothing pooled.**"""
    lines: list[str] = []
    lines.extend(result.preflight_lines)
    lines.append("")
    lines.extend(request.matrix.lines())
    lines.append("")
    lines.append("RESUME AND IDEMPOTENCE  (hard rule 10)")
    lines.append(
        f"  episodes already checkpointed, SKIPPED : {len(result.already_complete)}"
        f"   (IN the denominator - hard rule 11, INC-110)"
    )
    for slug in result.already_complete:
        lines.append(f"    - {slug}")
    lines.append(f"  episodes RUN this invocation           : {len(result.episodes)}")
    lines.append("")
    lines.append("PER-EPISODE TURN ACCOUNTING  (hard rule 11, applied to turns)")
    for episode in result.episodes:
        lines.append(f"  {episode.key.slug}  lane={episode.lane}  cause={episode.cause or '-'}")
        lines.extend(f"    {line}" for line in episode.counts.lines())
        lines.append(
            f"    turns run {episode.turns_run}/{episode.turn_budget}   "
            f"tokens attacker={episode.attacker_tokens} judge={episode.judge_tokens} "
            f"(BY ROLE, not by lane - INC-111)   "
            f"calls attacker={episode.calls_used} judge={episode.judge_calls}"
        )
    lines.append("")
    lines.append(
        runner_report.render_run_report(
            budgets=result.budgets,
            denominator=result.denominator,
            token_ceiling=request.ceilings.token_ceiling,
            limitations=limitations(request),
        )
    )
    lines.append("")
    lines.extend(_measurement_lines(request, result))
    lines.append(f"run started (UTC): {_iso(started)}")
    return "\n".join(lines)


def _measurement_lines(request: RunRequest, result: RunResult) -> list[str]:
    """The pilot's figure, and the N decision **or the refusal instead of one**."""
    measurement = pilot_module.measure_tokens_per_episode(
        attacker_tokens=result.attacker_tokens(request.matrix),
        completed=result.completed,
        truncated=result.truncated,
    )
    lines = list(measurement.lines())
    try:
        decision = pilot_module.decide_n(measurement, dry_run=request.dry_run)
    except pilot_module.PilotError as refusal:
        lines.append("N DECISION: REFUSED, and the refusal is the result -")
        lines.extend(f"  {part}" for part in str(refusal).split(". "))
        return lines
    lines.append("")
    lines.extend(decision.lines())
    return lines


def limitations(request: RunRequest) -> list[str]:
    """What this run is **not**. `PROCESS.md` §9: *"every evidence pack states what it is NOT."*

    A required argument on :func:`whetstone_gate.runner.report.render_run_report` with no
    default, *"because a default of [] is precisely how a limitation gets buried"*.
    """
    stated = [
        "MODEL OUTPUT IS NOT REPRODUCIBLE. The attacker runs at config/'s temperature "
        "against a hosted provider (hard rule 10). What regenerates byte-identically is "
        "every NUMBER, from the STORED LEDGERS - not the episodes.",
        "CANARY-B reach UNDER-counts a probe attempt made through a tool outside "
        "CONTEXT.md S8.6a's six-name surface: the gate is not asked, so no ledger entry is "
        "written. One-directional and identical across arms (QUESTIONS.md Q-142).",
        f"S3's authorization binding is an OPEN Class A question (QUESTIONS.md Q-141) and "
        f"this run used {request.s3_binding!r}. It changes arm 4's verdicts.",
        "The pilot's ARM is not in config/ and was supplied by the caller "
        "(QUESTIONS.md Q-144).",
        "The per-lane call and token ceilings are NOT in config/ either; hard rule 12's "
        "sanction comes from the prompt, and this driver requires BOTH explicitly rather "
        "than defaulting either (QUESTIONS.md Q-147).",
    ]
    if request.dry_run:
        stated.insert(
            0,
            "THIS WAS A DRY RUN. No provider was called; every token figure below is the "
            "TRANSCRIPT's number, not a provider's. It measures the HARNESS and MAY NOT "
            "select CONTEXT.md S13.4's N branch.",
        )
    return stated


def print_report(result: RunResult) -> None:
    """Print through :func:`whetstone_gate._console.say`, which transliterates to ASCII.

    The operator runs this in Git Bash on Windows, where the console codepage mangles this
    project's typography — *"a report the operator cannot read is a report that does not get
    read"*.
    """
    for line in result.report.splitlines():
        say(line)
