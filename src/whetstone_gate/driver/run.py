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
from whetstone_gate.runner.buckets import ObservedCost
from whetstone_gate.runner.budget import Ceilings, LaneBudget, usage_total_tokens
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


def preflight(
    request: RunRequest,
    *,
    repo_root: Path,
    utc_date: str,
    liveness_probe: Callable[[str], int] | None = None,
) -> Preflight:
    """Every precondition, in order, as printable lines. **Raises on the first refusal.**

    ⚠️⚠️ **``liveness_probe`` IS `QUESTIONS.md` `Q-193`'s WIRING, AND ON A REAL RUN IT IS
    REQUIRED.** It takes a lane name and returns an HTTP status;
    :meth:`whetstone_gate.driver.clients.MeteredProviderClient.liveness_probe` is the one the
    driver ships. Passing ``None`` to a ``--spend-real-tokens`` request is a **refusal**, not
    a skip — hard rule 9's *"a missing value is a hard refusal, never a silent fallback"*
    applied to a callable, because a default of *"then don't check"* would restore the
    pre-`Q-193` behaviour for every caller that forgot it **while the suite stayed green.**

    ⚠️ **A DRY RUN NEVER CALLS IT**, and the report says so on its own line. ``--dry-run``
    dispatches to a :class:`~whetstone_gate.driver.clients.TranscriptClient` and promises no
    network call; a probe there would be the only real provider call in a rehearsal. **The
    cost of that choice is that the rehearsal still cannot tell an operator whether the lanes
    are alive** — `INC-142`'s own `Expectation` — and this is not claimed to close it.
    """
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
        # ⚠️ SAID OUT LOUD, because an UNMENTIONED skip reads exactly like a pass. Q-193.
        lines.append("  liveness probe (Q-193) : NOT EXERCISED - a dry run makes no provider")
        lines.append("                           call, so it CANNOT tell you whether a lane")
        lines.append("                           is alive. That gap is INC-142's own")
        lines.append("                           Expectation and is NOT closed by Q-193")
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

    # ⚠️⚠️ LAST, AND THE ORDER IS THE POINT (`Q-193`). This is the ONLY precondition that
    # itself SPENDS. Every check above is free — the tag, the reservations, the key NAMES,
    # the day's usage file, the corpus — so running this before any of them would spend one
    # call per lane to reach a refusal that cost nothing. A guardrail against wasted spend
    # that wastes spend to run is the wrong shape.
    lines.extend(_refuse_dead_lanes(lanes_in_play, probe=liveness_probe))
    return Preflight(lines=lines, corpus_entries=entries)


def _refuse_dead_lanes(
    lanes: Sequence[str], *, probe: Callable[[str], int] | None
) -> list[str]:
    """⚠️ **`Q-193`'s WIRING, IN ONE PLACE.** Probe every lane; refuse naming every dead one.

    `INCIDENTS.md` `INC-142`, whose `Expectation` field this closes for a **real** run:
    *"`RUN_DECLARED.md` §7.3 lists seven preconditions 'each a refusal and not a warning',
    and preflight passed all seven … ⚠️ What no precondition tests is whether either lane
    ANSWERS."* The pilot — single-shot, unrepeatable — was spent discovering that one lane
    answered HTTP 403 to every call it ever made.
    """
    if probe is None:
        raise RunRefused(
            "a real run reached the liveness check with NO PROBE. QUESTIONS.md Q-193 wires "
            "INC-142's guardrail into preflight and a real run may not skip it: a probe that "
            "defaulted to 'then do not check' would restore the pre-Q-193 behaviour for "
            "every caller that forgot it, WITH A GREEN SUITE. Hard rule 9's 'a missing value "
            "is a hard refusal, never a silent fallback', applied to a callable. Pass "
            "MeteredProviderClient.liveness_probe, which is what __main__ supplies"
        )
    refusal = liveness_refusal(lanes, probe=probe)
    if refusal is not None:
        raise RunRefused(refusal)
    return [
        f"  liveness (Q-193)       : {len(lanes)} lane(s) ANSWERED - {sorted(lanes)}",
        "                           ONE call per lane, and it is SPEND: recorded in",
        "                           evals/usage/liveness-<block>-<date>.jsonl, never in",
        "                           the run's own lane log (INC-143's record is read from",
        "                           that file). A later preflight reading <lane>-<date>",
        "                           will NOT see these calls and under-counts by them",
    ]


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

    ⚠️ **THE BUCKETS ARE TAKEN AT THE RESERVATION AND THEN TOPPED UP AT THE SETTLED COST.**
    Pacing happens *before* the call, when the real cost does not exist yet, so admission is
    charged the reservation; the provider then returns ``usage.total_tokens`` and the
    difference is charged too. See :meth:`_settle`.

    ⚠️⚠️ **THE RESERVATION IS NOT AN UPPER BOUND, AND THIS DOCSTRING USED TO SAY IT WAS.**
    `INCIDENTS.md` **INC-143**. The removed sentence read, in its own emphasis: *"A reservation
    is an upper bound, so this paces conservatively — it can only make the runner slower than
    the provider's published limit, **never faster**, which is the direction that does not
    earn a 429."* **MEASURED against the pilot's own eight calls, that was false on seven of
    them:**

        reservation, every call : 3,000   (`attacker.target_tokens_per_episode // turn_budget`)
        ACTUAL, in order        : 790 3203 4002 6201 6665 7439 7782 6848
        exceeded it             : 7 of 8, the largest 7,782 = **2.59x**
        buckets under-charged by: **18,930** tokens across the eight

    The ninth call was an HTTP 429. ``target // turn_budget`` is **by construction the MEAN**,
    and a multi-turn conversation's per-call cost rises with context, so the reservation is
    above the real cost early and below it for the whole rest of an episode.

    ⚠️ **THE CLAIM IS NOT RESTATED IN A WEAKER FORM; IT IS EARNED.** :meth:`_settle` charges
    ``max(0, actual - reservation)`` once the real cost is known, so the buckets are charged
    ``max(reservation, actual)`` per call — **never less than the provider billed**.
    `tests/test_arch_lanes.py` asserts exactly that, replayed against the pilot's own eight
    numbers read from the committed usage log, and it fails against the code this replaced.

    ⚠️ **AND IT INTRODUCES NO NEW SPEC VALUE**, which is hard rule 9's requirement and the
    reason the fix is not a bigger constant: every charge is either the reservation the run
    already used or a figure the **provider** returned. There is no multiplier, no headroom
    factor and no safety margin to put in `config/`.

    ⚠️⚠️ **AND IT FIXED THE ACCOUNTING WHILE LEAVING THE *ADMISSION* DECIDING ON THE SAME
    FALSIFIED 3,000. `INCIDENTS.md` INC-161 IS THE COST OF THAT.** `INC-143`'s own fix note
    says it in its own words -- the top-up *"does not explain, and would not have prevented,
    the pilot's 429"* -- and `Q-191`'s sliding window then made the **limit** correct while
    leaving the **estimate** wrong. The calibration's attempt 3 admitted **8,421** and then
    **9,037** tokens **26 seconds apart** -- **17,458 against a declared ``tpm`` of 16,000** --
    because :meth:`_pace` asked the window for room for **3,000** both times. HTTP 429 one
    second later; **29 of 30 declared episodes never started.**

    ⚠️ **THE TWO NUMBERS ARE NOW SEPARATE, BECAUSE THEY ANSWER TWO DIFFERENT QUESTIONS.**

        what the pacer WAITS FOR   :class:`~whetstone_gate.runner.buckets.ObservedCost` --
                                   ``max(config's reservation, the worst this ROLE has
                                   actually cost)``. **Prospective**, so it can only ever be
                                   an estimate; derived from measurement, not from a guess.
        what the buckets are CHARGED
                                   ``max(reservation, actual)``, **exactly as before**.
                                   **Retrospective**, so it is the provider's own number.

    ⚠️⚠️ **`INC-143`'s NO-REFUND RULE WAS RE-EXAMINED RATHER THAN INHERITED, AND IT IS
    KEPT -- BUT ONLY BECAUSE THE ADAPTIVE NUMBER NEVER REACHES THE CHARGE.** The objection to
    inheriting it is real and was **measured**, not argued: replaying this lane's 32 real
    calls with the adaptive figure *taken* as well as *waited for*, and no refund, pins the
    trailing window at **15,564 for twenty-one consecutive calls**, charges **234,736** for
    **155,672** of real spend (**+51%**), sleeps **633 s** instead of **339 s** -- **and still
    breaches ``tpm``, by 203.** That is precisely the *"throttle the run to a crawl"* failure,
    and it is what inheriting the rule onto an adaptive **charge** would have bought.

    ⚠️ **A REFUND -- settling the SIGNED difference -- ALSO WORKS (15,221; 313 s) AND WAS
    REJECTED ON ITS MERITS RATHER THAN IGNORED.** It buys **26 seconds** across 32 calls, and
    it costs a new direction of travel through
    :meth:`~whetstone_gate.runner.buckets.SlidingWindow.settle`, whose refusal of a negative
    charge is the line that makes *"the buckets are never told less than the provider billed"*
    checkable at all. **Keeping the reservation out of the charge reaches the same number
    without opening that door**, so the rule stands for the regime it was written for -- which
    is still the regime the *charge* is in, even though it is no longer the regime the
    *admission* is in. **That is the whole re-examination, and it is why the answer is "keep"
    rather than "inherit".**

    ⚠️ **MEASURED ON THE REAL 32-CALL TRACE** (`tests/test_c14_pacer_admission.py`):

        worst trailing-60s window BEFORE : **18,175**   -- over ``tpm`` by 2,175
        worst trailing-60s window AFTER  : **15,221**   -- inside ``tpm``
        pacer sleep, before / after      : 43 s / 339 s  (`Q-191`: *"IT WILL SLOW THE SWEEP
                                           AND THAT IS THE CORRECT TRADE"*)
    """

    inner: MeteredModelClient
    attacker_buckets: Any
    judge_buckets: Any
    attacker_reservation: int
    judge_reservation: int
    clock: Callable[[], float]
    sleep: Callable[[float], None]

    #: ⚠️⚠️ **OPTIONAL, AND THE DEFAULT IS THE DANGEROUS ONE — WHICH IS WHY IT IS ONLY EVER
    #: THE DEFAULT IN A TEST.** :func:`execute` builds **one estimate per (lane, role) for
    #: the whole run** and injects it here, because :class:`_PacedClient` **is rebuilt for
    #: every episode** while the :class:`~whetstone_gate.runner.buckets.Buckets` it paces
    #: against are built **once per lane**. An estimate constructed here instead would reset
    #: to the `config/` floor at the start of each of the 30 episodes and re-learn this
    #: lane's cost from scratch every time — **which is `INC-161` happening thirty times
    #: instead of once**, against a window that remembers everything. The estimate must have
    #: the lifetime of the limit it is estimating for, and that lifetime is the lane's.
    #:
    #: ⚠️ **ONE PER ROLE, NEVER ONE PER LANE, AND THAT IS `INC-111`'s DISTINCTION.**
    #: `CONTEXT.md` §13.3.2 puts the reference attacker and the gate judge on the **same**
    #: lane, `gemma-26b`. A single shared estimate would make every small judge call wait for
    #: the room the attacker's largest turn needed, and would file the attacker's cost under
    #: the judge's name — the same conflation that made an arm-1 episode of 20 calls report
    #: 120,000 tokens where the answer is 60,000.
    attacker_observed: ObservedCost | None = None
    judge_observed: ObservedCost | None = None

    def __post_init__(self) -> None:
        # A caller that supplies no estimate gets a fresh one floored at the reservation it
        # did supply, so a client built in isolation paces exactly as the injected one does
        # on its first call. It simply does not REMEMBER across episodes, and only
        # :func:`execute` has episodes.
        if self.attacker_observed is None:
            self.attacker_observed = ObservedCost(floor=self.attacker_reservation)
        if self.judge_observed is None:
            self.judge_observed = ObservedCost(floor=self.judge_reservation)

    def complete_attacker(
        self, *, messages: tuple[dict[str, str], ...], temperature: float, lane: str
    ) -> ModelReply:
        self._agree(lane, self.attacker_buckets, role="attacker")
        admitted_at = self._pace(
            self.attacker_buckets,
            admit_tokens=self.attacker_observed.reservation,
            take_tokens=self.attacker_reservation,
        )
        reply = self.inner.complete_attacker(
            messages=messages, temperature=temperature, lane=lane
        )
        self._settle(
            self.attacker_buckets,
            self.attacker_reservation,
            self.attacker_observed,
            reply,
            admitted_at,
        )
        return reply

    def complete_judge(self, *, system: str, user: str, lane: str) -> ModelReply:
        self._agree(lane, self.judge_buckets, role="judge")
        admitted_at = self._pace(
            self.judge_buckets,
            admit_tokens=self.judge_observed.reservation,
            take_tokens=self.judge_reservation,
        )
        reply = self.inner.complete_judge(system=system, user=user, lane=lane)
        self._settle(
            self.judge_buckets,
            self.judge_reservation,
            self.judge_observed,
            reply,
            admitted_at,
        )
        return reply

    def _settle(
        self,
        buckets: Any,
        reservation: int,
        observed: ObservedCost,
        reply: ModelReply,
        admitted_at: float,
    ) -> None:
        """Charge the buckets ``max(0, actual - reservation)`` now the real cost is known,
        **and teach the next admission what this call actually cost**.

        ⚠️ **`INCIDENTS.md` INC-143's OWN PROPOSED GUARDRAIL, VERBATIM:** *"THE HONEST FIX IS
        NOT A BIGGER CONSTANT — IT IS TO CHARGE THE BUCKET THE DIFFERENCE ONCE THE REAL COST
        IS KNOWN. The provider returns `usage.total_tokens` on every successful call and the
        run already books it; a `settle`-side top-up of `max(0, actual - reservation)` against
        the same bucket makes the pacing self-correcting and needs no new spec value at all."*

        ⚠️ **ONLY ON A SUCCESSFUL CALL, AND THAT IS NOT AN OMISSION.** A `ProviderFailed` or a
        `RateLimited` never reaches here — both raise out of ``self.inner`` — and neither has
        a `usage` block to read. `driver/episode.py` books those at **zero** tokens, an
        under-count *published rather than estimated* (golden 8: *"NEVER estimated"*), and
        inventing a settle figure for them here would put an estimate exactly where hard rule
        12 forbids one.

        ⚠️ **``max(0, ...)`` AND NOT A SIGNED DIFFERENCE.** A call that came in **under** its
        reservation — the pilot's first, 790 against 3,000 — does **not** hand the surplus
        back. The reservation was genuinely committed at admission, and refunding it would let
        a cheap opening turn buy headroom for an expensive later one, which is the same
        under-charge in the other direction.

        ⚠️ **THE TOP-UP IS CHARGED AT THE ADMISSION CLOCK READING, NOT A FRESH ONE, AND THAT
        IS DELIBERATE ON BOTH COUNTS.** `Q-179`(1) already ruled that this class reads the
        clock **once per call** — a second reading is what turned a bucket refusal into a
        `BucketError` on this project's own platform (`INC-134`: 139 short sleeps in 300
        samples). It is also the **conservative** direction: settling at the earlier moment
        credits the bucket *less* refill than settling at the later one, so the lane ends up
        slightly more paced rather than slightly less — and "less" is the direction that earns
        a 429.
        """
        actual = usage_total_tokens(reply.usage)
        buckets.settle(extra_tokens=max(0, actual - reservation), now=admitted_at)
        # ⚠️ **THE ONE NEW LINE, AND IT CHARGES NOTHING.** `INC-161`: the settle already had
        # the provider's own figure in hand and threw it away after spending it. It is now
        # also remembered, so the NEXT call's admission asks the window for room the size of
        # the worst call this role has actually made rather than the size of a mean that the
        # run had already falsified. **This is the only place the estimate is ever written**,
        # and it is written from `usage.total_tokens` and nothing else.
        observed.observe(actual)

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

    def _pace(self, buckets: Any, *, admit_tokens: int, take_tokens: int) -> float:
        """Wait until the buckets permit ``admit_tokens``, then charge them ``take_tokens``.
        **One clock read.**

        ⚠️⚠️ **TWO ARGUMENTS BECAUSE THERE ARE TWO QUESTIONS, AND `INCIDENTS.md` INC-161 IS
        WHAT ONE ARGUMENT COST.** ``admit_tokens`` is the *prospective* estimate -- what this
        call is expected to cost, from
        :class:`~whetstone_gate.runner.buckets.ObservedCost`. ``take_tokens`` is the
        *reservation* the run has always charged, which :meth:`_settle` then tops up to the
        provider's own figure at this same instant. **The window therefore still ends up
        holding ``max(reservation, actual)`` -- unchanged -- while the WAIT is now decided by
        a number the lane's own calls produced.**

        ⚠️ **``take_tokens <= admit_tokens`` IS WHY THE TAKE CANNOT FAIL.**
        :meth:`~whetstone_gate.runner.buckets.SlidingWindow.wait_seconds` is monotone in
        cost: if there is room for the larger figure there is room for the smaller. The
        admission the wait just granted therefore cannot be refused by the take, and no
        second clock reading is involved in either -- `Q-179`(1) again.

        ⚠️ **THE GAP BETWEEN THE TAKE AND THE TOP-UP IS ZERO SECONDS AND ZERO EVENTS.**
        :meth:`_settle` runs immediately after the provider answers and charges at
        ``admitted_at``, the *same* reading, so no other admission can observe the window
        holding only the reservation. Under-recording is momentary in the code and
        non-existent in the arithmetic.

        ⚠️ **A CALL LARGER THAN ``tpm`` ITSELF STOPS THE LANE, AND THAT IS THE DECISION
        RATHER THAN AN OVERSIGHT.** Once this role has been billed more for one call than the
        lane's whole per-minute capacity, ``admit_tokens`` exceeds that capacity and
        :meth:`~whetstone_gate.runner.buckets.SlidingWindow.wait_seconds` raises
        :class:`~whetstone_gate.runner.buckets.BucketError` -- *"waiting cannot help"* --
        which `driver/episode.py` books as ``PACER_REFUSED``: **counted, named, zero tokens,
        zero calls, and no packet on the wire** (`Q-179`(2), `INC-160`). ⚠️ **The alternative
        was to clamp the estimate down to ``tpm`` and send anyway, which is deliberately
        buying the 429 that `Q-191` ruled we do not buy** -- *"a paced wait costs seconds, a
        429 costs the lane"* -- and hard rule 12 forbids retrying into another. ⚠️ **This
        branch was UNREACHABLE on this lane before `INC-161`**, because ``_pace`` only ever
        asked for 3,000 against a 16,000 ``tpm``; it is reachable now, it is pinned by
        `tests/test_c14_pacer_admission.py`, and it is disclosed at `QUESTIONS.md` `Q-206`.

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
            wait = buckets.wait_seconds(tokens=admit_tokens, now=now)
            if wait <= 0:
                buckets.take(tokens=take_tokens, now=now)
                # ⚠️ RETURNED so :meth:`_settle` can charge the top-up against **this** same
                # reading rather than taking a second one. See its docstring, and `Q-179`(1).
                return now
            self.sleep(wait)


# --------------------------------------------------------------------------------------
# The run
# --------------------------------------------------------------------------------------


def liveness_refusal(
    lanes: Sequence[str], *, probe: Callable[[str], int]
) -> str | None:
    """⚠️⚠️ **ONE LIVENESS CALL PER LANE. `INCIDENTS.md` INC-142's OWN PROPOSED GUARDRAIL.**

    Returns ``None`` when every lane answered, or a **refusal string naming every lane that
    did not and the status it gave**. It is a refusal and not a warning: `PROCESS.md` §6b
    makes the first completed execution *the* run, so a warning printed above a single-shot
    pilot is a warning printed above a spent artefact.

    ⚠️ **WHY THIS EXISTS, IN `INC-142`'s OWN WORDS.** *"`RUN_DECLARED.md` §7.3 lists seven
    preconditions 'each a refusal and not a warning', and preflight passed all seven —
    including §7.3 #5, 'Every provider key NAME set', and #7, the provider client. ⚠️ **What
    no precondition tests is whether either lane ANSWERS.** Preflight reads a key's name,
    never makes a call, and the dry run dispatches to a `TranscriptClient`. So the entire
    ladder of checks between the operator and a single-shot run can pass while one of the two
    lanes is incapable of returning a single usable reply, which is exactly what happened."*

    **Both of the pilot's failures were of this kind, and both would have been refused here:**

    - `qwen-27b` answered **HTTP 403** to every one of its ten calls — measured on 2026-09-04
      to be an edge block on the missing `User-Agent`, since fixed (`INC-145`), and a lane
      that answers 403 to a one-token probe answers 403 to an episode.
    - `gemma-26b` was alive, and a probe would have said so — which matters just as much: it
      is what separates *"the lane is dead"* from *"the lane was paced too fast"* **before**
      six minutes of single-shot run rather than after.

    ⚠️ **EVERY DEAD LANE IS NAMED, NOT JUST THE FIRST.** The pilot's two lanes were broken in
    two *different* ways. A check that stopped at the first would have sent the operator back
    for a second single-shot run to discover the second — **and there is no second single-shot
    run.**

    ⚠️ **A 429 IS A REFUSAL TOO.** A lane already rate-limited before the run starts cannot
    complete it, and `CLAUDE.md` §4 forbids waiting it out by retrying.

    ``probe`` is injected — it takes a lane name and returns an HTTP status — so this function
    is pure, and so that a test drives it without a socket. ⚠️ **The status is ALL that
    crosses this boundary: no body, no header, nothing that could carry a credential**
    (`INC-142`, and :class:`whetstone_gate.driver.clients.ProviderFailed`).
    """
    dead: list[str] = []
    for lane in lanes:
        status = probe(lane)
        if not 200 <= int(status) < 300:
            dead.append(f"{lane} answered HTTP {int(status)}")
    if not dead:
        return None
    return (
        "REFUSED before spending: "
        + "; ".join(dead)
        + ". A lane that does not answer a one-token probe does not answer an episode, and "
        "PROCESS.md S6b makes the first completed execution THE run. INCIDENTS.md INC-142: "
        "the pilot spent its single, unrepeatable artefact discovering this."
    )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _date(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%d")


class _VirtualClock:
    """A clock that advances **only when it is slept on**. `Q-179`(3).

    ⚠️ **THIS IS WHAT MAKES PACING A DRY RUN FREE.** The pacer's arithmetic is driven in
    full — every ``rpm``/``tpm``/``rpd`` refill, every wait the buckets ask for — while the
    wall clock does not move, so a rehearsal of the declared matrix pays the lane-hours it
    simulates in microseconds. With ``time.sleep`` on that path a 20-episode rehearsal would
    sit out every rate-limit wait it rehearses, which is why the ruling names an injected
    clock and an injected sleep in the same sentence as the requirement itself.

    ⚠️ **IT IS EXACT, AND THAT IS DELIBERATE.** It advances by precisely what it was asked
    for, so it never undershoots and `Q-179`(1)'s race cannot fire on a dry run *by accident*
    — a rehearsal must not report a defect the real clock would not produce. The undershoot
    is injected explicitly by the tests that mean to study it.
    """

    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.t += max(0.0, seconds)


def _pacing_clock(
    request: RunRequest,
    clock: Callable[[], float] | None,
    sleep: Callable[[float], None] | None,
) -> tuple[Callable[[], float], Callable[[float], None]]:
    """The clock and sleep the pacer runs on. **A caller's own always wins.**

    ⚠️ **A REAL RUN GETS THE REAL PAIR AND A DRY RUN GETS THE VIRTUAL ONE**, because
    `Q-179`(3) requires the dry run to build the pacer *"WITH AN INJECTED CLOCK AND AN
    INJECTED SLEEP so it costs no wall-clock time"*. Resolving it here rather than at each
    call site means every entry point — the CLI, the tests, a future harness — gets the
    behaviour the ruling describes without having to remember to ask for it.
    """
    if clock is not None and sleep is not None:
        return clock, sleep
    if request.dry_run:
        virtual = _VirtualClock()
        return (clock or virtual), (sleep or virtual.sleep)
    return (clock or time.monotonic), (sleep or time.sleep)


def execute(
    request: RunRequest,
    *,
    client: MeteredModelClient,
    corpus_entries: Sequence[Any] | None = None,
    now: Callable[[], datetime] = _utc_now,
    clock: Callable[[], float] | None = None,
    sleep: Callable[[float], None] | None = None,
    repo_root: Path | None = None,
    liveness_probe: Callable[[str], int] | None = None,
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
    # ⚠️ `Q-179`(3): a dry run that named no clock gets the VIRTUAL pair, so building the
    # pacer on its path — which the ruling requires — costs it no wall-clock time.
    clock, sleep = _pacing_clock(request, clock, sleep)
    root = repo_root or cfg.repo_root()
    started = now()
    result = RunResult()
    checks = preflight(
        request,
        repo_root=root,
        utc_date=_date(started),
        liveness_probe=liveness_probe,
    )
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

    # ⚠️⚠️ **RUN-SCOPED, KEYED BY (LANE, ROLE) — `INCIDENTS.md` INC-161's SECOND HALF.**
    # `_PacedClient` is rebuilt inside the loop below (`Q-179`(3) requires it to be built on
    # every run, including a dry one), but `lane_states[...].buckets` are built **once per
    # lane** before it. An adaptive reservation held on the per-episode client would
    # therefore forget, at the start of every episode, everything the window it paces
    # against still remembers — and the first turns of all 30 episodes would be admitted
    # against the same falsified 3,000 that stopped attempt 3. **The estimate is scoped to
    # the limit it estimates for.**
    # ⚠️ The ROLE is part of the key and not folded away: `CONTEXT.md` §13.3.2 puts the
    # attacker and the judge on one lane, and their per-call costs are nothing like each
    # other (`INC-111`).
    observed_costs: dict[tuple[str, str], ObservedCost] = {}

    def _observed(lane_name: str, role: str, floor: int) -> ObservedCost:
        return observed_costs.setdefault((lane_name, role), ObservedCost(floor=floor))

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
        # ⚠️⚠️ **`Q-179`(3), RULED 2026-09-04 — THE PACER IS BUILT ON EVERY RUN, INCLUDING A
        # DRY ONE.** This used to read `paced = client` and wrap it only
        # `if request.spend_real_tokens:`, so a `--dry-run` dispatched through the **raw**
        # client and `_PacedClient.__init__`, `_agree` and `_pace` were **never executed**.
        # ⚠️ **A REHEARSAL THAT CANNOT ENTER THE PATH THE REAL RUN TAKES IS NOT A
        # REHEARSAL** — and it is not a theoretical gap: `Q-179`(1)'s pacer race lived on
        # exactly the lines a dry run skipped, so no amount of rehearsing could have found
        # it and only spending could.
        # ⚠️ **IT COSTS NO WALL-CLOCK TIME**, which is the ruling's own condition: a dry run
        # that names no clock is given the virtual pair built in :func:`_pacing_clock`, so
        # the buckets' arithmetic is driven in full while the wall clock does not move.
        paced = _PacedClient(
            inner=client,
            attacker_buckets=attacker_state.buckets,
            judge_buckets=judge_state.buckets,
            attacker_reservation=settings.attacker_call_reservation_tokens,
            judge_reservation=settings.judge_call_reservation_tokens,
            clock=clock,
            sleep=sleep,
            # ⚠️ INC-161: injected, so the estimate survives this episode ending. See the
            # dictionary's own comment above the loop.
            attacker_observed=_observed(
                lane, "attacker", settings.attacker_call_reservation_tokens
            ),
            judge_observed=_observed(
                judge_lane, "judge", settings.judge_call_reservation_tokens
            ),
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

    def sink(
        lane: str,
        tokens: int,
        outcome: str,
        *,
        status: int | None = None,
        error_type: str | None = None,
    ) -> None:
        # ⚠️ `status` / `error_type` arrive ONLY from the `ProviderFailed` path (INC-142) and
        # are dropped from the row when absent, so an `OK` row stays byte-identical to the
        # ones the pilot committed. See `runner/usage.py:append`.
        usage_log.append(
            model=lane,
            date=date,
            utc=_iso(now()),
            lane=lane,
            episode=key.slug,
            total_tokens=tokens,
            outcome=outcome,
            status=status,
            error_type=error_type,
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
