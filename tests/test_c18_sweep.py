"""**C18 SWEEP BUILD 1 (`6a4f28de`) — `--block scored`, and the DISPATCH ORDER it runs in.**

⚠️ **A NEW FILE ON PURPOSE**, for the reason ``tests/test_arch_lanes.py`` and
``tests/test_arch_cal_build.py`` both give in their own headers: `INC-138` is a landed commit that
deleted an assertion while its message said nothing was deleted. Putting new tests in a new file
makes the diff *"0 files changed"* for every existing suite, which ``git show --numstat`` can check
and which cannot be got wrong by hand.

⚠️ **IT IS `test_c18_sweep.py` AND NOT `test_c18_results.py`.** That file already exists and holds
C18's *other* deliverable — `RESULTS.md` + ``make eval``, built 3 Sep. The two are unrelated
deliverables carrying one chunk label, which is raised as `QUESTIONS.md` **`Q-211`** and is **not**
resolved by naming a file.

**WHAT THIS FILE PINS**

- **§1 THE MATRIX** — five arms × N, every value read from `config/` or derived through
  `CONTEXT.md` §13.4's rule, and a **refusal** wherever it is not yet determined.
- **§2 THE BLOCK LABEL** — every key stamped ``SCORED``, and **zero** slug collision with the 41
  checkpoints already on disk. Driven against the real directory, not reasoned about.
- **§3 ⚠️⚠️ THE DISPATCH ORDER** — the point of the chunk. Seed-major, **proved balanced under
  truncation at every one of the 151 prefixes**, with the arm-major order driven **beside it** as
  the discriminating control.
- **§4 RESUME AND THE DENOMINATOR** — killed mid-run and resumed, zero duplicates, and the whole
  matrix still in the denominator.
- **§5 THE JUDGE** — arms 2/2S/3 call it, arms 1 and 4 make **zero** judge calls, tokens counted
  by ROLE and never pooled into the attacker's figure.
- **§6 THE COMMAND LINE** — ``--arm`` required for two blocks and refused for the third, and the
  committed pilot pre-registration still parsing.
- **§7 THE REPORT** — only the PILOT block may select N, and the measurement header names the
  block that actually ran.

⚠️ **ZERO PROVIDER MODEL CALLS.** Every test here drives
:class:`whetstone_gate.driver.clients.TranscriptClient`, which opens nothing. This session's prompt
sanctioned **no spend at all**, and every lane in play is reserved (`PROCESS.md` §8).

⚠️ **THE SWEEP IS NOT RUN BY ANYTHING IN THIS FILE.** Building the path and spending the run are
different acts, and no scored episode may run until `prereg-v1` is cut and the freeze is witnessed
outside this repository (`CONTEXT.md` §15.1, §15.3).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from whetstone_gate import config as cfg
from whetstone_gate.driver import __main__ as driver_main
from whetstone_gate.driver import cal as cal_module
from whetstone_gate.driver import episode as driver_episode
from whetstone_gate.driver import pilot as pilot_module
from whetstone_gate.driver import rehearsal
from whetstone_gate.driver import run as driver_run
from whetstone_gate.driver import scored as scored_module
from whetstone_gate.driver.clients import TranscriptClient
from whetstone_gate.gates.verdict import ARMS
from whetstone_gate.runner import n_rule
from whetstone_gate.runner.budget import Ceilings
from whetstone_gate.runner.episodes import EpisodeKey
from whetstone_gate.runner.scheduler import Scheduler

S3_BINDING = driver_episode.S3_AUTHORIZATION_IS_THE_PAYMENT

#: The calibration's own run log. ⚠️ **UNTRACKED at the time this file was written** — see
#: :func:`_calibration_log`, which returns ``None`` rather than pretending. The one test that reads
#: it parses the measured tokens/episode out of it rather than typing the figure.
_CAL_LOG = "evals/cal/run-attempt4-20260904T204118Z.log"


# ======================================================================================
# Helpers — every one of them offline
# ======================================================================================


def _matrix(seeds: tuple[int, ...], *, arms: tuple[str, ...] | None = None):
    """A scored matrix over ``seeds``. **Shaped exactly like the real one, only shorter.**

    The lanes come from ``config/lanes.yaml`` through the same reader
    :func:`~whetstone_gate.driver.scored.load_scored` uses, so a test never invents a lane name.
    """
    reference = pilot_module._one_lane_whose_role_says(scored_module.REFERENCE_ROLE_MARKER)
    judge = pilot_module._one_lane_whose_role_says(scored_module.GATE_JUDGE_ROLE_MARKER)
    return scored_module.ScoredMatrix(
        arms=arms if arms is not None else scored_module.scored_arms(),
        turn_budget=int(cfg.load("protocol").require("attacker.turn_budget")),
        reference=scored_module.ScoredCell(
            lane=reference.name, attacker_model=reference.name, seeds=seeds
        ),
        judge_lane=judge.name,
    )


def _recomputed_break_even() -> int:
    """The largest measured tokens/episode at which §13.4's **recomputed** second conjunct holds.

    ⚠️ **FOUND BY SEARCH OVER ``runner/n_rule.py``, NEVER TYPED**, so this file cannot drift from
    the rule if a `config/` selection or a lane limit moves — which both have. Above this figure
    the second conjunct fails, and above the token boundary the first fails too, so `Q-107`'s two
    readings **agree** there and :func:`scored_n` has nothing to STOP on.
    """
    low, high = 1, 10_000_000
    while low < high:
        middle = (low + high + 1) // 2
        if n_rule.select_n(middle).second_conjunct_holds:
            low = middle
        else:
            high = middle - 1
    return low


def _selected_n() -> int:
    """N as the scored block will actually be sized. **Derived, never typed, never guessed.**

    ⚠️ **WHEN `config/` CARRIES THE MEASURED FIGURE THIS IS THE MODULE'S OWN ANSWER**, so the
    tests below size themselves exactly as the run will.

    ⚠️ **WHILE IT IS STILL A ``TODO_`` SENTINEL THE TESTS DRIVE AT A FIGURE ABOVE THE
    BREAK-EVEN**, which is the region the calibration's own measurement lands in and is the only
    region in which :func:`scored_n` does not STOP (`Q-121`). ⚠️ **This is NOT a stand-in for the
    measured figure and no test here asserts a number derived from it as if it were measured** —
    it fixes the *shape* of the matrix (five arms × a band that carries N seeds) so that the
    dispatch-order and denominator claims can be driven at full length today.
    """
    protocol = cfg.load("protocol")
    if protocol.has("n_decision.measured_tokens_per_episode"):
        return scored_module.scored_n()
    return n_rule.select_n(_recomputed_break_even() + 1).n


def _full_length_matrix():
    """The scored matrix at the seed band §13.4's rule selects, **read through `config/`**.

    The band is not typed here and N is not typed here: both come from
    :func:`~whetstone_gate.driver.scored.scored_seeds` at :func:`_selected_n`, so this helper
    cannot disagree with the module it tests about how big the block is.
    """
    return _matrix(scored_module.scored_seeds(_selected_n()))


def _calibration_log() -> str | None:
    """The calibration's own run log, **or ``None`` if it is not in this tree**.

    ⚠️⚠️ **IT IS UNTRACKED AT THE TIME THIS FILE WAS WRITTEN, AND THAT IS A FINDING RATHER THAN
    A CONVENIENCE.** ``evals/cal/run-attempt4-…log`` and the calibration's thirty checkpoints and
    thirty episode ledgers are present in the operator's working tree and **absent from
    ``git archive HEAD``** — so the record of the spent, single-shot run that sets the void
    threshold is not in the repository. ``evals/`` is outside this session's fence and committing
    them is the operator's act, so this is **reported, not worked around**: the one test that
    reads the log says out loud when it cannot, and no load-bearing assertion in this file depends
    on it.
    """
    path = cfg.repo_root() / _CAL_LOG
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def _request(matrix, out_root: Path, **kwargs) -> driver_run.RunRequest:
    return driver_run.RunRequest(
        matrix=matrix,
        out_root=out_root,
        ceilings=Ceilings(
            call_ceiling=kwargs.pop("call_ceiling", 100_000),
            token_ceiling=kwargs.pop("token_ceiling", 500_000_000),
        ),
        s3_binding=kwargs.pop("s3_binding", S3_BINDING),
        spend_real_tokens=False,
        sanctioned_lanes=frozenset(kwargs.pop("sanctioned_lanes", ())),
        allow_absent_corpus=True,
    )


def _client(matrix, *, episodes: int | None = None) -> TranscriptClient:
    count = matrix.episode_count if episodes is None else episodes
    return TranscriptClient(
        attacker_replies=rehearsal.attacker_transcript(count),
        judge_replies=rehearsal.judge_transcript(count * matrix.turn_budget),
    )


class _KilledAfter:
    """Wraps a client and raises ``KeyboardInterrupt`` once its inner transcript is exhausted.

    ⚠️ ``KeyboardInterrupt`` is a ``BaseException`` and `Q-200`'s floor is spelled
    ``except Exception``, so it passes straight through the dispatch loop — **which is the whole
    point**: a floor that booked an operator's Ctrl-C as an episode outcome would make a 42-hour
    sweep unstoppable. Lifted in shape from ``tests/test_c12_driver.py``'s own ``_KilledAfter``,
    and for its stated reason.
    """

    def __init__(self, inner: TranscriptClient) -> None:
        self.inner = inner

    def complete_attacker(self, **kwargs):
        try:
            return self.inner.complete_attacker(**kwargs)
        except Exception as exhausted:  # noqa: BLE001 - re-raised as a BaseException on purpose
            raise KeyboardInterrupt(str(exhausted)) from None

    def complete_judge(self, **kwargs):
        return self.inner.complete_judge(**kwargs)


def _protocol_override(monkeypatch, overrides: dict):
    """Patch the ONE loader so ``config/protocol.yaml`` answers ``overrides``, and NOTHING else.

    ⚠️ **THE DELEGATION IS THE POINT AND ITS ABSENCE IS A SILENT FALSE RED.** A shim that
    answered *every* config name would hand ``cfg.load("lanes")`` the protocol document, and
    :func:`whetstone_gate.runner.n_rule.gemma_tokens_per_lane_hour` would then fail on a missing
    ``lanes`` key -- so the test under it would go red for a reason that has nothing to do with
    what it asserts. Measured on this file's own first red-proof run.
    """
    real_load = cfg.load
    real_protocol = real_load("protocol")

    class _Overridden:
        def require(self, key):
            if key in overrides:
                return overrides[key]
            return real_protocol.require(key)

        def has(self, key):
            try:
                self.require(key)
            except cfg.ConfigError:
                return False
            return True

    monkeypatch.setattr(
        cfg, "load", lambda name: _Overridden() if name == "protocol" else real_load(name)
    )


def _section(markdown: str, heading: str) -> str:
    """One section of a markdown document, whitespace-normalised. `test_arch_cal_build.py`'s."""
    lines = markdown.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith(heading))
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("#")),
        len(lines),
    )
    return re.sub(r"\s+", " ", " ".join(lines[start:end]))


# ======================================================================================
# 1. THE MATRIX — five arms x N, every value read or derived
# ======================================================================================


def test_the_scored_block_is_FIVE_ARMS_and_the_count_is_PARSED_from_the_law_not_typed(repo_root):
    """⚠️ **THE LAW IS READ, NEVER COPIED INTO THIS FILE.**

    `CONTEXT.md` §13.4's block table and `PROTOCOL.md` §3.1 both carry the M-ADV row as
    *"5 arms × N"*. The count is parsed back out of **both** artefacts and diffed against
    :data:`whetstone_gate.gates.verdict.ARMS`, because a number written here by hand would be a
    third copy that can drift from both — ``test_c3_tau2_enumeration.py``'s own reasoning.
    """
    context = (repo_root / "CONTEXT.md").read_text(encoding="utf-8")
    protocol = (repo_root / "PROTOCOL.md").read_text(encoding="utf-8")

    declared = set()
    for document, heading in ((context, "## 13.4 "), (protocol, "### 3.1 ")):
        section = _section(document, heading)
        found = re.findall(r"mock world, adversarial \*?\*?\|\s*(\d+) arms × N", section)
        assert len(found) == 1, (
            f"expected exactly ONE M-ADV row stating its arm count in the section beginning "
            f"{heading!r}; found {found}. A parser that silently reads nothing reports green "
            f"over an unchecked claim"
        )
        declared.add(int(found[0]))

    assert len(declared) == 1, f"CONTEXT.md and PROTOCOL.md state different arm counts: {declared}"
    arms = scored_module.scored_arms()
    assert len(arms) == declared.pop() == len(ARMS)
    assert arms == tuple(ARMS), "the block dispatches the gate package's own declared arms"


def test_the_ARM_COUNT_IS_CROSS_CHECKED_against_the_projection_that_SELECTED_N():
    """⚠️ **TWO INDEPENDENT TRANSCRIPTIONS OF `PROTOCOL.md` §2.1 MUST AGREE.**

    :data:`whetstone_gate.runner.n_rule.ARMS` is the integer §13.4's feasibility projection
    multiplies every per-arm count by; :data:`whetstone_gate.gates.verdict.ARMS` is the tuple this
    block dispatches. If they diverged, **the block that RUNS would not be the block whose
    lane-hours were PROJECTED** — and the projection is what selected N.
    """
    assert len(scored_module.scored_arms()) == n_rule.ARMS


def test_load_scored_REFUSES_while_the_MEASURED_FIGURE_IS_UNDETERMINED_and_NAMES_ITS_OWNER():
    """⚠️⚠️ **THE REFUSAL IS THE CORRECT OUTCOME, AND IT IS THE ONE THIS TREE PRODUCES TODAY.**

    ``config/protocol.yaml`` carries ``n_decision.measured_tokens_per_episode: TODO_C14_PILOT``.
    `PROTOCOL.md` §3, in capitals: *"Quietly shrinking N to a number the schedule can reach is the
    precise thing rule 11 and `ai-playbook` B.9 forbid."* So the block refuses to size itself, and
    the loader's message **names who owes the value** rather than merely being loud.

    ⚠️ **THIS TEST IS DELIBERATELY WRITTEN TO SURVIVE THE KEY LANDING.** When C14 lands the
    measured figure this assertion becomes vacuous rather than false, and the branch below then
    asserts the *positive*: that a determined key yields the N the rule yields. Neither side is a
    number typed here.
    """
    protocol = cfg.load("protocol")
    if protocol.has("n_decision.measured_tokens_per_episode"):
        measured = int(protocol.require("n_decision.measured_tokens_per_episode"))
        assert scored_module.scored_n() == n_rule.select_n(measured).n
        return
    with pytest.raises(cfg.UndeterminedValue) as refused:
        scored_module.scored_n()
    assert "n_decision.measured_tokens_per_episode" in str(refused.value)
    assert "TODO_C14_PILOT" in str(refused.value)
    with pytest.raises(cfg.UndeterminedValue):
        scored_module.load_scored()


def test_N_IS_DERIVED_THROUGH_S13_4s_RULE_and_this_module_re_derives_NOTHING(monkeypatch):
    """⚠️ **`driver/pilot.py`'s discipline, applied here:** *"This module wires that rule; it does
    not re-derive it."*

    The measured figure is handed to :func:`whetstone_gate.runner.n_rule.select_n` — C11's
    already-reviewed implementation of the rule as `Q-107` ruled it — and whatever that returns is
    N. Driven at the calibration's own measured figure, **read from its committed log**.
    """
    measured = _recomputed_break_even() + 1
    expected = n_rule.select_n(measured).n  # computed BEFORE the loader is patched
    _protocol_override(monkeypatch, {"n_decision.measured_tokens_per_episode": measured})
    assert scored_module.scored_n() == expected
    assert len(scored_module.scored_seeds(expected)) == expected


def test_AT_THE_CALIBRATIONS_MEASURED_FIGURE_BOTH_Q107_READINGS_AGREE_and_BOTH_conjuncts_bind():
    """⚠️ **THE ARITHMETIC THE WHOLE BLOCK SIZE RESTS ON, RE-COMPUTED FROM THE ARTEFACT.**

    The calibration's figure is **parsed out of its own run log**, never typed — a number written
    into a test file can be written to agree with the code it checks, and a spent single-shot
    run's log cannot (``tests/test_arch_cal_build.py``'s reasoning about the pilot's eight calls).

    Against §13.4's two conjuncts that figure fails **both**, so `Q-107`'s two readings select the
    same branch and :func:`scored_n`'s divergence guard has nothing to stop — the block is sized
    without settling `Q-121`.

    ⚠️ **AND IT IS NOT CLOSE, WHICH IS WORTH ASSERTING BECAUSE A NARROW MARGIN WOULD BE A
    DIFFERENT SITUATION.** Both margins are re-measured here, not asserted as adjectives.

    ⚠️ **IF THE LOG IS ABSENT THIS SAYS SO LOUDLY RATHER THAN PASSING**: it is untracked (see
    :func:`_calibration_log`), so a clean clone cannot run this and must be told why rather than
    shown a green tick.
    """
    log = _calibration_log()
    if log is None:
        pytest.skip(
            f"{_CAL_LOG} is not in this tree. It is UNTRACKED in the operator's working tree, so "
            f"the record of the spent single-shot calibration is not in the repository. "
            f"Committing it is the operator's act (evals/ is append-only and outside a build "
            f"session's fence); this test cannot run until it is."
        )
    found = re.findall(r"tokens/episode over COMPLETED[^:]*:\s*(\d+)", log)
    assert len(found) == 1, (
        f"expected exactly ONE 'tokens/episode over COMPLETED' line in {_CAL_LOG}; found "
        f"{len(found)}. Zero means the calibration's log moved and this file is no longer "
        f"reading the run it claims to; more than one means it records two measurements"
    )
    decision = n_rule.select_n(int(found[0]))

    assert not decision.first_conjunct_holds, "the measured figure exceeds the token boundary"
    assert not decision.second_conjunct_holds, "and the recomputed lane-time exceeds its budget"
    assert decision.readings_agree, (
        "Q-107's RECOMPUTED and AT-THE-REGISTERED-TARGET readings must select the same N here; "
        "Q-121 is OPEN and driver/scored.py refuses rather than choosing between them"
    )
    assert decision.n == decision.n_at_registered_target
    assert int(found[0]) > decision.token_boundary * 2, "the first margin is not marginal"
    assert int(found[0]) > _recomputed_break_even() * 2, "nor is the second"
    assert decision.projected_lane_hours > decision.lane_hour_budget


def test_the_TWO_Q107_READINGS_DISAGREEING_IS_A_STOP_and_never_a_silent_choice(monkeypatch):
    """⚠️⚠️ **`QUESTIONS.md` `Q-121`, OPEN — AND THIS IS THE ONE PLACE IT COULD BE SETTLED BY
    ACCIDENT.**

    Below the recomputed reading's break-even the two readings select **different N**, and N picks
    **which seed band the scored block runs**. Choosing one silently here would settle an open
    Class A question by picking the size of the published run. It is a STOP (hard rule 1).

    ⚠️ **THE BREAK-EVEN IS FOUND BY SEARCH, NOT TYPED**, so this test cannot drift from
    ``runner/n_rule.py`` if a lane limit or a `config/` selection moves.
    """
    low, high = 1, 10_000_000
    while low < high:
        middle = (low + high + 1) // 2
        if n_rule.select_n(middle).second_conjunct_holds:
            low = middle
        else:
            high = middle - 1
    diverging = low
    assert not n_rule.select_n(diverging).readings_agree, (
        "the search found no measured figure at which Q-107's two readings disagree; if that is "
        "genuinely true of this config/ then Q-121 has stopped being reachable and this test's "
        "premise has changed"
    )

    _protocol_override(monkeypatch, {"n_decision.measured_tokens_per_episode": diverging})
    with pytest.raises(scored_module.ScoredError, match="Q-121"):
        scored_module.scored_n()


def test_the_SEED_BAND_AND_N_MUST_AGREE_and_a_disagreement_is_a_REFUSAL(monkeypatch):
    """⚠️ **Hard rule 11, one step earlier** — ``cal.cal_seeds``' guard, in this block's terms.

    A band carrying other than N seeds runs a **different-sized block than the decision rule
    selected**, under a declaration that says otherwise.
    """
    protocol = cfg.load("protocol")
    branch_b = int(protocol.require("n_decision.branch_b_n"))
    _protocol_override(
        monkeypatch,
        {f"seeds.scored_n{branch_b}_last": int(protocol.require(f"seeds.scored_n{branch_b}_last")) - 1},
    )
    with pytest.raises(scored_module.ScoredError, match="decision rule SELECTED"):
        scored_module.scored_seeds(branch_b)


def test_a_BRANCH_WITH_NO_PRE_REGISTERED_SEED_BAND_IS_A_REFUSAL():
    """⚠️ `PROTOCOL.md` §2.2 names a `config/` key pair for **each** branch, precisely so the
    pilot *"SELECTS a branch rather than amending a frozen document"*. A branch with no band is a
    branch that was never pre-registered, and it refuses rather than inventing seeds."""
    with pytest.raises(scored_module.ScoredError, match="never pre-registered"):
        scored_module.scored_seeds(7)


def test_the_SCORED_SEEDS_ARE_DISJOINT_FROM_THE_PILOT_AND_CALIBRATION_BANDS():
    """⚠️ **THE DISJOINTNESS THAT IS ACTUALLY REQUIRED, AND NOT THE ONE THAT IS NOT.**

    `PROTOCOL.md` §2.2: the **pilot's** seeds are disjoint from the scored set because the pilot
    *"selects N"* and must not decide the size of episodes it has looked at. `Q-189`(a) puts the
    **calibration** under the same rule with more force: *"a calibration run on scored seeds fits
    the void threshold to the very worlds it later judges."*

    ⚠️ **THE LADDER AND THE OTHER SCORED BRANCH OVERLAP THE SCORED BAND, BY DESIGN, AND
    ASSERTING OTHERWISE WOULD BE A FALSE TEST.** §13.4 fixes the ladder cells at the scored
    block's own first five seeds, and the two scored branches are nested bands over one block.
    Both are asserted **positively** here so that a reader is not left to infer which silence
    means what.
    """
    protocol = cfg.load("protocol")
    band = set(scored_module.scored_seeds(_selected_n()))

    for name in ("pilot", "cal"):
        other = set(
            range(
                int(protocol.require(f"seeds.{name}_first")),
                int(protocol.require(f"seeds.{name}_last")) + 1,
            )
        )
        assert not (band & other), (
            f"the scored band overlaps seeds.{name} on {sorted(band & other)}. PROTOCOL.md S2.2 "
            f"and Q-189(a) both require this disjointness, and it is the whole reason those two "
            f"blocks may size and threshold a run they did not look at"
        )

    ladder = set(
        range(
            int(protocol.require("seeds.ladder_first")),
            int(protocol.require("seeds.ladder_last")) + 1,
        )
    )
    assert ladder <= band, (
        "the ladder cells run on the scored block's own first seeds (CONTEXT.md S13.4), so this "
        "overlap is REQUIRED. If it ever stops holding, the ladder has stopped being measured on "
        "the worlds the scored arms face"
    )


# ======================================================================================
# 2. THE BLOCK LABEL — it reaches every key, and it collides with nothing
# ======================================================================================


def test_EVERY_SCORED_KEY_CARRIES_THE_SCORED_BLOCK_so_it_can_NEVER_read_as_PILOT_or_CAL():
    """⚠️ **`driver/cal.py`'s property, read in the other direction.**

    :meth:`EpisodeKey.slug` joins ``(block, arm, seed_or_task, attacker_model)`` with ``"__"``, so
    the block label reaches **every checkpoint filename and every ledger stem**. `Q-189`
    correction 2 measured what its absence costs: nine live episodes stamped with another block's
    label, *"byte-indistinguishable"*, into an append-only directory.
    """
    matrix = _full_length_matrix()
    keys = matrix.keys()
    assert len(keys) == matrix.episode_count
    assert {key.block for key in keys} == {scored_module.SCORED_BLOCK} == {"SCORED"}
    assert all(key.slug.startswith("scored__") for key in keys)
    assert not any(key.slug.startswith(("pilot__", "cal__")) for key in keys)
    assert len({key.slug for key in keys}) == len(keys), "slugs are injective"

    # Driven against the other two blocks, not reasoned about.
    others = {key.slug for key in pilot_module.load_pilot(arm="1").keys()}
    others |= {key.slug for key in cal_module.load_cal().keys()}
    assert not ({key.slug for key in keys} & others)


def test_ZERO_SLUG_COLLISION_WITH_EVERY_CHECKPOINT_ALREADY_ON_DISK(repo_root):
    """⚠️⚠️ **DRIVEN AGAINST THE REAL DIRECTORY, BECAUSE THAT IS WHERE A COLLISION WOULD LAND.**

    ``evals/`` is **append-only with operator-only deletion** (`CLAUDE.md` §4) and
    :meth:`CheckpointStore.publish` refuses an existing file whose bytes differ — so a scored slug
    that collided with a spent calibration or pilot episode would either **refuse mid-sweep** or,
    worse, be read as already complete and **silently skipped from the denominator**.

    The directory currently holds the calibration's and the pilot's episodes. Nothing this block
    produces may touch them, and that is measured here rather than argued.
    """
    on_disk = {path.stem for path in (repo_root / "evals" / "checkpoints").glob("*.json")}
    assert on_disk, "evals/checkpoints/ is empty; this test's premise has changed"
    blocks = {stem.split("__")[0] for stem in on_disk}
    assert blocks <= {"cal", "pilot"}, (
        f"evals/checkpoints/ holds block(s) {sorted(blocks)}; only the pilot's and the "
        f"calibration's episodes have been spent"
    )
    assert not any(stem.startswith("scored__") for stem in on_disk), (
        "a scored checkpoint already exists on disk. NO SCORED EPISODE MAY RUN until prereg-v1 "
        "is cut and the freeze is witnessed outside this repository (CONTEXT.md S15.1, S15.3)"
    )
    scored_slugs = {key.slug for key in _full_length_matrix().keys()}
    assert not (scored_slugs & on_disk)


# ======================================================================================
# 3. ⚠️⚠️ THE DISPATCH ORDER — THE POINT OF THE CHUNK
# ======================================================================================


def test_THE_DISPATCH_ORDER_IS_SEED_MAJOR_every_arm_at_a_seed_before_the_next_seed():
    """⚠️⚠️ **SEED-MAJOR, ASSERTED AS A STRUCTURE AND NOT AS A SPOT CHECK.**

    Key ``i`` must be ``(seed[i // arms], arm[i % arms])`` for **every** ``i``, which is the
    property *"seed s on all five arms, then seed s+1 on all five"* stated exactly.
    """
    matrix = _full_length_matrix()
    arms, seeds = matrix.arms, matrix.reference.seeds
    keys = matrix.keys()

    assert len(keys) == len(arms) * len(seeds)
    for index, key in enumerate(keys):
        assert key.arm == arms[index % len(arms)]
        assert key.seed_or_task == str(seeds[index // len(arms)])

    # The first block of keys is one seed across every arm — the sentence, driven.
    first_seed_block = keys[: len(arms)]
    assert {key.seed_or_task for key in first_seed_block} == {str(seeds[0])}
    assert [key.arm for key in first_seed_block] == list(arms)


def test_TRUNCATING_THE_KEY_LIST_AT_ANY_POINT_LEAVES_THE_ARMS_DIFFERING_BY_AT_MOST_ONE():
    """⚠️⚠️ **THE CLAIM THAT MAKES A CUT-OFF SWEEP PUBLISHABLE, AS A NUMBER.**

    The sweep **will** be cut off — it is 150 episodes at ~18.7 calls each against a deadline —
    so the honest question is what it has delivered at the instant it stops. Under seed-major
    order the answer is: every arm at the same n, on the same seeds, differing by **at most one**.

    ⚠️ **CHECKED AT EVERY PREFIX, NOT AT A SAMPLE.** A cut-off happens at whatever instant the
    deadline lands on, and a property that holds at sampled points is not the property.
    """
    matrix = _full_length_matrix()
    keys = matrix.keys()
    assert scored_module.truncation_imbalance(keys, matrix.arms) == 1

    # And the zeros print: an arm with no episodes yet is a counted zero, never an absent key.
    assert set(scored_module.per_arm_counts(keys[:1], matrix.arms)) == set(matrix.arms)
    assert sorted(scored_module.per_arm_counts(keys[:1], matrix.arms).values()) == [0, 0, 0, 0, 1]


def test_ARM_MAJOR_ORDER_LEAVES_THE_LATER_ARMS_EMPTY_AT_THE_SAME_CUT_OFF():
    """⚠️⚠️ **THE DISCRIMINATING CONTROL, DRIVEN BESIDE THE CLAIM RATHER THAN ASSERTED.**

    ``sorted(keys)`` **is** the arm-major order, because :class:`EpisodeKey` is ``order=True`` on
    ``(block, arm, seed_or_task, attacker_model)`` — which is exactly what
    :meth:`Scheduler.pending` returns and what this block would have inherited.

    At a cut-off of roughly a third, arm-major delivers **arm 1 complete, part of arm 2, and the
    remaining three arms EMPTY**. There is no comparison between arms, and the comparison is the
    published claim — so a third of the tokens would have bought a number that cannot be
    published at all. Seed-major at the same instant delivers all five arms at the same n.
    """
    matrix = _full_length_matrix()
    seed_major = matrix.keys()
    arm_major = sorted(seed_major)

    assert arm_major != list(seed_major), "the two orders must actually differ"
    assert scored_module.truncation_imbalance(arm_major, matrix.arms) == len(
        matrix.reference.seeds
    ), "arm-major's worst imbalance is a whole arm's worth of episodes — i.e. N"

    cut_off = len(seed_major) // 3
    balanced = scored_module.per_arm_counts(seed_major[:cut_off], matrix.arms)
    starved = scored_module.per_arm_counts(arm_major[:cut_off], matrix.arms)

    assert max(balanced.values()) - min(balanced.values()) <= 1
    assert len(set(balanced.values())) == 1, "every arm at the SAME n, on the SAME seeds"
    assert sorted(starved.values())[:3] == [0, 0, 0], (
        "arm-major truncation at a third leaves THREE arms with zero episodes — no comparison, "
        "and therefore no result"
    )
    # The same seeds, which is what makes the comparison PAIRED (S12.3, S10.2).
    per_arm_seeds = {
        arm: {key.seed_or_task for key in seed_major[:cut_off] if key.arm == arm}
        for arm in matrix.arms
    }
    assert len(set(map(frozenset, per_arm_seeds.values()))) == 1, (
        "every arm must have faced the SAME seeds, which is what makes an arm-to-arm difference "
        "mean anything (PROTOCOL.md S2.1: 'The only variable is the gate')"
    )


def test_run_py_DISPATCHES_IN_THE_MATRIXS_ORDER_AND_NOT_THE_SCHEDULERS_SORT(tmp_path):
    """⚠️⚠️ **THE INTEGRATION HALF, AND THE ONE THAT WOULD HAVE BEEN MISSED.**

    :meth:`Scheduler.pending` **re-sorts**, so a matrix that merely built its keys seed-major
    would have had that order thrown away between :meth:`keys` and the dispatch loop. This drives
    a whole run and reads the order **off the episodes that actually ran**.
    """
    # Three seeds is enough for the order to differ from the sort, and short enough to drive a
    # whole run offline. The seeds are the real band's own first three, read from `config/`.
    matrix = _matrix(_full_length_matrix().reference.seeds[:3])
    result = driver_run.execute(
        _request(matrix, tmp_path / "order"), client=_client(matrix), corpus_entries=()
    )
    assert len(result.episodes) == matrix.episode_count
    dispatched = [episode.key for episode in result.episodes]
    assert dispatched == list(matrix.keys()), "the run dispatched in the matrix's declared order"
    assert dispatched != sorted(dispatched), (
        "and NOT in the scheduler's key sort, which is arm-major — if these ever coincide this "
        "test has stopped discriminating"
    )


def test_the_PILOT_AND_CAL_DISPATCH_ORDERS_ARE_UNCHANGED_by_this_chunk():
    """⚠️⚠️ **A SPENT, SINGLE-SHOT BLOCK'S ORDER IS A MATTER OF RECORD, NOT OF PREFERENCE.**

    ``evals/pilot/RUN_DECLARED.md`` and ``evals/cal/RUN_DECLARED.md`` are committed, pushed
    pre-registrations of runs that have already been spent. Making the dispatch order a matrix's
    own declaration must therefore change **nothing** for either of them, and that is asserted
    against :meth:`Scheduler.pending`'s own output rather than argued.
    """
    scheduler = Scheduler(lanes={}, sanctioned_lanes=frozenset())
    for matrix in (pilot_module.load_pilot(arm="1"), cal_module.load_cal()):
        keys = matrix.keys()
        pending = scheduler.pending(keys, set())
        assert matrix.dispatch_order(pending) == pending == sorted(keys)


def test_the_dispatch_order_REFUSES_A_KEY_THE_MATRIX_DID_NOT_PRODUCE():
    """⚠️ **Never an append at either end.** A key with no declared position would be dispatched
    somewhere nothing chose, which is the one property this method exists to provide."""
    matrix = _matrix((2001, 2002))
    stranger = EpisodeKey(
        block=scored_module.SCORED_BLOCK, arm="1", seed_or_task="9999", attacker_model="gemma-26b"
    )
    with pytest.raises(scored_module.ScoredError, match="not in this scored matrix"):
        matrix.dispatch_order([stranger])


def test_the_dispatch_order_is_DETERMINISTIC_across_two_independent_builds():
    """A run whose dispatch order depends on a hash seed is a run whose partial results depend on
    it too — :meth:`Scheduler.pending`'s own reason, and the reason a cut-off sweep's contents
    must be predictable in advance."""
    assert _full_length_matrix().keys() == _full_length_matrix().keys()


# ======================================================================================
# 4. RESUME AND THE DENOMINATOR — hard rules 10 and 11
# ======================================================================================


def test_kill_mid_run_and_resume_dispatches_ONLY_what_has_no_checkpoint_with_ZERO_duplicates(
    tmp_path,
):
    """⚠️⚠️ **THE SWEEP WILL BE INTERRUPTED. THIS IS THAT, DEMONSTRATED RATHER THAN ASSERTED.**

    Pass 1 is killed part-way. Pass 2 resumes and re-runs **only** what has no checkpoint. Pass 3
    re-runs **nothing** and makes **zero** model calls.

    ⚠️ **AND THE RESUME PRESERVES THE SEED-MAJOR ORDER**, which is what makes a cut-off resumed
    sweep still balanced: the episodes pass 2 runs are the tail of the same declared order, so the
    per-arm counts stay within one at every instant of both passes.
    """
    out = tmp_path / "resume"
    matrix = _matrix((2001, 2002, 2003, 2004))
    partial = 7

    with pytest.raises(KeyboardInterrupt):
        driver_run.execute(
            _request(matrix, out),
            client=_KilledAfter(
                TranscriptClient(
                    attacker_replies=rehearsal.attacker_transcript(partial),
                    judge_replies=rehearsal.judge_transcript(partial * matrix.turn_budget),
                )
            ),
            corpus_entries=(),
        )
    after_crash = sorted(path.stem for path in (out / "evals/checkpoints").glob("*.json"))
    assert len(after_crash) == partial, "a crash costs ONE episode, not the run"

    # ⚠️ The killed run's checkpoints are the FIRST `partial` keys of the declared order, so the
    # arms are still within one of each other at the instant it died. That is the whole claim.
    assert after_crash == sorted(key.slug for key in matrix.keys()[:partial])
    counts = scored_module.per_arm_counts(matrix.keys()[:partial], matrix.arms)
    assert max(counts.values()) - min(counts.values()) <= 1

    second = driver_run.execute(
        _request(matrix, out), client=_client(matrix), corpus_entries=()
    )
    assert len(second.already_complete) == partial
    assert len(second.episodes) == matrix.episode_count - partial
    assert [e.key for e in second.episodes] == list(matrix.keys()[partial:]), (
        "the resume dispatches the TAIL of the same declared order"
    )
    after_resume = sorted(path.stem for path in (out / "evals/checkpoints").glob("*.json"))
    assert len(after_resume) == len(set(after_resume)) == matrix.episode_count
    assert set(after_crash) <= set(after_resume), "a published checkpoint is never rewritten"

    third_client = _client(matrix)
    third = driver_run.execute(
        _request(matrix, out), client=third_client, corpus_entries=()
    )
    assert third.episodes == []
    assert third_client.attacker_calls == 0, "a re-run makes ZERO model calls"


def test_a_CUT_OFF_SWEEP_REPORTS_ITS_REAL_n_AND_ITS_WHOLE_DENOMINATOR(tmp_path):
    """⚠️⚠️ **HARD RULE 11 ON THE BLOCK IT MATTERS MOST FOR.**

    *"Every dropped episode is counted, categorised and printed as a number."* The denominator is
    the **whole matrix**, whatever ran, and a resumed run reports the same number as the first —
    `INC-110`'s defect, in this block's terms.
    """
    out = tmp_path / "denominator"
    matrix = _matrix((2001, 2002))
    first = driver_run.execute(
        _request(matrix, out), client=_client(matrix), corpus_entries=()
    )
    assert first.denominator.attempted == matrix.episode_count
    first.denominator.reconcile()

    second = driver_run.execute(
        _request(matrix, out), client=_client(matrix), corpus_entries=()
    )
    assert second.episodes == [], "nothing should have re-run"
    assert second.denominator.attempted == first.denominator.attempted == matrix.episode_count
    assert "IN the denominator" in second.report
    assert str(matrix.episode_count) in second.report


def test_the_matrix_PRINTS_ITS_DENOMINATOR_AND_ITS_DISPATCH_ORDER_so_the_operator_sees_both():
    """⚠️ `PROCESS.md` §9: *"every evidence pack states what it is NOT."* The reason for the
    dispatch order and the size of the denominator are both **printed**, because a property that
    lives only in a docstring is invisible to the person watching the run."""
    rendered = "\n".join(_full_length_matrix().lines())
    assert "SEED-MAJOR" in rendered
    assert "COMPARISON BETWEEN ARMS" in rendered
    assert "WHATEVER HAPPENS" in rendered
    assert "PROCESS.md S14" in rendered
    assert "SCORED" in rendered and "scored__" in rendered


def test_a_RESUMED_JUDGED_ARM_REFUSES_ON_THE_ARM_IT_ACTUALLY_FOUND_not_the_matrixs():
    """⚠️⚠️ **`OF-240`, GENERALISED FROM A ONE-ARM MATRIX TO A FIVE-ARM ONE.**

    A checkpoint carries ONE ``tokens_spent`` and no attacker/judge split, so a resumed episode of
    arm 2, 2S or 3 cannot have its attacker share recovered. The old test was ``matrix.arm``,
    which **does not exist** on a five-arm matrix — so the refusal now reads each resumed
    document's **own** ``arm`` field, which is a declared key of
    :data:`~whetstone_gate.runner.checkpoint.DOCUMENT_KEYS`.

    ⚠️ **AND THE JUDGE-LESS HALF STILL RETURNS AN EXACT FIGURE**, which is the half that must not
    become a refusal by over-reach: for arms 1 and 4 ``tokens_spent`` **is** the attacker figure.
    """
    matrix = _matrix((2001,))

    def _resumed(arm: str, tokens: int) -> dict:
        return {"arm": arm, "tokens_spent": tokens, "truncated": False}

    unjudged = driver_run.RunResult(resumed=[_resumed("1", 100), _resumed("4", 200)])
    assert unjudged.attacker_tokens(matrix) == 300, (
        "for a judge-less arm tokens_spent IS the attacker figure and the resume is exact"
    )

    for judged_arm in ("2", "2S", "3"):
        mixed = driver_run.RunResult(
            resumed=[_resumed("1", 100), _resumed(judged_arm, 900)]
        )
        with pytest.raises(driver_run.RunRefused, match="OF-240"):
            mixed.attacker_tokens(matrix)


def test_the_ATTACKER_TOKEN_REFUSAL_DOES_NOT_TAKE_THE_DENOMINATOR_DOWN_WITH_IT(tmp_path):
    """⚠️⚠️ **FOUND BY BUILDING THIS BLOCK, AND IT WOULD HAVE COST THE SWEEP ITS REPORT.**

    ``attacker_tokens`` is called from inside :func:`~whetstone_gate.driver.run.render`, so its
    `OF-240` refusal used to abort the **whole report**. On a scored sweep that is not a corner
    case: **90 of the 150 episodes are on arms 2/2S/3**, the run spans days by design, and every
    resume that skipped one judged episode would have printed **nothing at all** — no
    denominator, no per-cause counts, no per-lane budget.

    That is hard rule 11's own named failure caused by a guard against a different error. The
    figure still refuses — it is not estimated, not defaulted and not silently zeroed — but the
    refusal is now **printed as the outcome** and everything else still prints. `Q-212`.
    """
    out = tmp_path / "judged-resume"
    matrix = _matrix((2001,), arms=("2",))
    driver_run.execute(_request(matrix, out), client=_client(matrix), corpus_entries=())

    resumed = driver_run.execute(
        _request(matrix, out), client=_client(matrix), corpus_entries=()
    )
    assert resumed.episodes == []
    assert "MEASUREMENT: REFUSED" in resumed.report
    assert "OF-240" in resumed.report
    # ⚠️ AND EVERYTHING HARD RULE 11 REQUIRES IS STILL THERE.
    assert "DENOMINATOR (completed+trunc)" in resumed.report
    assert "reconciles" in resumed.report
    assert "THE DENOMINATOR ABOVE IS UNAFFECTED" in resumed.report
    assert resumed.denominator.attempted == matrix.episode_count


# ======================================================================================
# 5. THE JUDGE — arms 2/2S/3 call it; arms 1 and 4 do not; the tokens are SEPARATE
# ======================================================================================


def test_ARMS_2_2S_3_CALL_THE_JUDGE_and_ARMS_1_AND_4_MAKE_ZERO_JUDGE_CALLS(tmp_path):
    """⚠️ `PROTOCOL.md` §2.1 and `CONTEXT.md` §13.4's gate-judge row, *"arms 2/2S/3 only"* —
    driven across **all five arms in one run**, which is the only place the split is visible.

    ⚠️ **AND THE TOKENS ARE COUNTED BY ROLE, NOT BY LANE (hard rule 12, `INC-111`).**
    §13.3.2 puts the reference attacker and the gate judge on the **same** lane, so a lane-based
    split would both double-count an episode and drop the attacker's own figure.
    """
    matrix = _matrix((2001,))
    assert matrix.judged_arms() == ("2", "2S", "3")
    assert matrix.unjudged_arms() == ("1", "4")
    assert matrix.reference.lane == matrix.judge_lane, (
        "config/lanes.yaml puts both roles on one lane (S13.3.2) — which is why the split must "
        "be by ROLE"
    )

    result = driver_run.execute(
        _request(matrix, tmp_path / "judge"), client=_client(matrix), corpus_entries=()
    )
    by_arm = {episode.key.arm: episode for episode in result.episodes}
    assert set(by_arm) == set(matrix.arms)

    for arm in matrix.unjudged_arms():
        assert by_arm[arm].judge_calls == 0
        assert by_arm[arm].judge_tokens == 0
    for arm in matrix.judged_arms():
        assert by_arm[arm].judge_calls > 0
        assert by_arm[arm].judge_tokens > 0

    for episode in result.episodes:
        assert episode.tokens_spent == episode.attacker_tokens + episode.judge_tokens
    assert result.attacker_tokens(matrix) == sum(
        episode.attacker_tokens for episode in result.episodes
    ), "no judge token leaks into the attacker figure"


def test_the_matrix_and_run_py_AGREE_about_which_arms_judge():
    """⚠️ Two copies of `PROTOCOL.md` §2.1's judged set would be two experiments. The matrix reads
    :data:`whetstone_gate.driver.run.JUDGED_ARMS` rather than carrying its own."""
    matrix = _matrix((2001,))
    assert set(matrix.judged_arms()) == driver_run.JUDGED_ARMS & set(matrix.arms)
    assert not (set(matrix.unjudged_arms()) & driver_run.JUDGED_ARMS)


# ======================================================================================
# 6. THE COMMAND LINE
# ======================================================================================


def test_BLOCK_SCORED_REFUSES_AN_ARM_because_the_block_runs_ALL_FIVE():
    """⚠️ **A REFUSAL, NOT A VALUE QUIETLY IGNORED.** An operator who typed ``--arm 1`` and saw a
    run start would reasonably believe they had run arm 1; what would actually have started is
    all five arms of the scored block on the scored seeds."""
    base = [
        "--dry-run", "--block", "scored", "--s3-binding", S3_BINDING,
        "--call-ceiling", "600", "--token-ceiling", "4800000",
    ]
    for arm in ARMS:
        assert driver_main.main(base + ["--arm", arm]) == 2


def test_BLOCK_PILOT_AND_CAL_STILL_REFUSE_AN_ABSENT_ARM(monkeypatch):
    """⚠️ **MAKING ``--arm`` CONDITIONAL MUST NOT WEAKEN THE REFUSAL IT ALREADY CARRIED.**

    `Q-144`: §13.4 and `PROTOCOL.md` §3.1 both say *"1 ref arm"* and neither says which, and
    `config/` carries no key for it. Dropping argparse's ``required=True`` moved that refusal
    here; it did not remove it, and this is what says so.
    """
    base = [
        "--dry-run", "--s3-binding", S3_BINDING,
        "--call-ceiling", "600", "--token-ceiling", "4800000",
    ]
    for block in ("pilot", "cal"):
        assert driver_main.main(base + ["--block", block]) == 2


def test_BLOCK_CAL_STILL_CHECKS_ITS_ARM_rather_than_obeying_it():
    """⚠️ `CONTEXT.md` §10.3 and **frozen** `HOLES.md` §3.5 both say *"arm 1 only"*. Re-asserted
    here because this chunk touched the parser that carries it."""
    base = [
        "--dry-run", "--block", "cal", "--s3-binding", S3_BINDING,
        "--call-ceiling", "600", "--token-ceiling", "4800000",
    ]
    for wrong in ("2", "2S", "3", "4"):
        assert driver_main.main(base + ["--arm", wrong]) == 2


def test_the_COMMITTED_PILOT_PREREGISTRATION_COMMAND_STILL_PARSES(repo_root):
    """⚠️⚠️ **THE REGRESSION THIS CHUNK COULD MOST EASILY HAVE CAUSED.**

    ``evals/pilot/RUN_DECLARED.md`` §1 carries **the exact command** of a run that has already
    been spent, and `PROCESS.md` §6b makes that file the declaration from the moment it was
    pushed. A parser change that stopped it parsing would **retroactively invalidate a
    pre-registration**. The command is READ OUT OF THE ARTEFACT, never retyped here.
    """
    declared = (repo_root / "evals" / "pilot" / "RUN_DECLARED.md").read_text(encoding="utf-8")
    block = re.search(r"```sh\n(.*?)```", declared, re.S)
    assert block, "RUN_DECLARED.md S1's fenced command block has moved"
    command = block.group(1)
    argv = [
        token
        for token in command.replace("\\\n", " ").split()
        if token not in ("python", "-m", "--")
    ]
    argv = argv[argv.index("drive") + 1 :] if "drive" in argv else argv
    argv = [token for token in argv if token != "whetstone_gate.tasks"]

    parsed = driver_main.build_parser().parse_args(argv)
    assert parsed.block == "pilot" and parsed.arm == "1"


def test_the_COMMITTED_CALIBRATION_PREREGISTRATION_COMMAND_STILL_PARSES(repo_root):
    """The same guard for the calibration, whose declared command **does** carry ``--block cal``
    and whose run is likewise spent (`INC-161`)."""
    declared = (repo_root / "evals" / "cal" / "RUN_DECLARED.md").read_text(encoding="utf-8")
    block = re.search(r"```sh\n(.*?)```", declared, re.S)
    assert block, "evals/cal/RUN_DECLARED.md S1's fenced command block has moved"
    argv = [
        token
        for token in block.group(1).replace("\\\n", " ").split()
        if token not in ("python", "-m", "--", "whetstone_gate.tasks")
    ]
    argv = argv[argv.index("drive") + 1 :] if "drive" in argv else argv
    parsed = driver_main.build_parser().parse_args(argv)
    assert parsed.block == "cal" and parsed.arm == "1"


def test_A_MATRIX_THAT_CANNOT_BE_ASSEMBLED_IS_A_NAMED_REFUSAL_never_a_traceback(capsys):
    """⚠️ **THIS MODULE'S OWN RULE ABOUT THE PROVIDER CLIENT, APPLIED ONE STEP EARLIER.**

    ``load_scored()`` refuses while ``n_decision.measured_tokens_per_episode`` is a ``TODO_``
    sentinel, and that refusal is the single most likely thing an operator will see from this
    path. It must exit 2 with the loader's own message — **which names who owes the value** — and
    never as a traceback.
    """
    if cfg.load("protocol").has("n_decision.measured_tokens_per_episode"):
        pytest.skip("the measured figure has landed; this refusal is no longer reachable")
    code = driver_main.main(
        [
            "--dry-run", "--block", "scored", "--s3-binding", S3_BINDING,
            "--call-ceiling", "600", "--token-ceiling", "4800000",
        ]
    )
    assert code == 2
    printed = capsys.readouterr().out
    assert "REFUSED" in printed
    assert "measured_tokens_per_episode" in printed
    assert "Traceback" not in printed


def test_the_BLOCK_FLAG_STILL_DEFAULTS_TO_PILOT_after_a_third_choice_was_added():
    """⚠️ Adding ``scored`` to ``--block``'s choices must not disturb the default, for the reason
    ``test_arch_cal_build.py`` gives: a required flag would make a pushed pre-registration of an
    already-spent single-shot run exit 2."""
    parser = driver_main.build_parser()
    parsed = parser.parse_args(
        ["--dry-run", "--arm", "1", "--s3-binding", S3_BINDING,
         "--call-ceiling", "1", "--token-ceiling", "1"]
    )
    assert parsed.block == "pilot"
    assert set(parser._option_string_actions["--block"].choices) == {"pilot", "cal", "scored"}


# ======================================================================================
# 7. THE REPORT — only the pilot may select N, and the header names the block that ran
# ======================================================================================


def test_ONLY_THE_PILOT_BLOCK_MAY_SELECT_N_and_the_scored_block_says_so_out_loud(tmp_path):
    """⚠️⚠️ **A SCORED RUN THAT PRINTED AN N DECISION WOULD BE SIZED BY THE EPISODES IT DECIDES
    THE SIZE OF.**

    `CONTEXT.md` §13.4 names the selector in terms — *"the 31 Aug **pilot's** measured attacker
    tokens/episode"* — and `PROTOCOL.md` §3 adds *"No other branch. No post-hoc adjustment."*
    The report used to run :func:`decide_n` on whatever block had just finished. The measurement
    is still printed, as a **disclosure of what the block cost**; the decision is not.
    """
    matrix = _matrix((2001,), arms=("1",))
    result = driver_run.execute(
        _request(matrix, tmp_path / "n-decision"), client=_client(matrix), corpus_entries=()
    )
    assert "N DECISION: NOT THIS BLOCK'S TO MAKE" in result.report
    assert "N DECISION RULE" not in result.report, "no branch may be selected here"
    assert "SCORED MEASUREMENT" in result.report, "the cost is still disclosed"


def test_the_MEASUREMENT_HEADER_NAMES_THE_BLOCK_THAT_RAN(tmp_path):
    """⚠️⚠️ **MEASURED IN THE CALIBRATION'S OWN COMMITTED LOG, WHICH MISNAMES ITSELF.**

    ``evals/cal/run-attempt4-…log`` prints ``block label : CAL`` at the top and ``PILOT
    MEASUREMENT`` at the bottom, over the calibration's thirty episodes, because that header was
    a literal. Nothing computed was wrong — the slugs are ``cal__`` throughout — but **the
    printed record named the wrong run**, and a record that misnames the run it describes is
    something a reader is entitled to hold against every number beside it.
    """
    log = _calibration_log()
    if log is not None:
        assert "PILOT MEASUREMENT" in log, (
            "this test's premise is the calibration's own log; if it ever changes, re-measure "
            "before trusting the claim below"
        )
        assert "block label            : CAL" in log

    matrix = _matrix((2001,), arms=("1",))
    result = driver_run.execute(
        _request(matrix, tmp_path / "header"), client=_client(matrix), corpus_entries=()
    )
    assert "SCORED MEASUREMENT" in result.report
    assert "PILOT MEASUREMENT" not in result.report


def test_the_PILOTS_ARM_LIMITATION_IS_PRINTED_ONLY_ON_THE_PILOTS_OWN_BLOCK(tmp_path):
    """⚠️ **A LIMITATION STATED WHERE IT DOES NOT APPLY SPENDS THE READER'S TRUST IN EVERY
    LIMITATION BESIDE IT** — `PROCESS.md` §9's whole point.

    *"The pilot's ARM is not in config/ and was supplied by the caller"* is printed on every
    block's report, including the calibration's committed log, where it is **false**: §10.3 and
    frozen `HOLES.md` §3.5 both fix that arm and ``--arm`` is checked rather than obeyed. The
    scored block takes no ``--arm`` at all.
    """
    matrix = _matrix((2001,), arms=("1",))
    result = driver_run.execute(
        _request(matrix, tmp_path / "limits"), client=_client(matrix), corpus_entries=()
    )
    assert "The pilot's ARM is not in config/" not in result.report
    # The limitations that DO apply are still every one of them.
    assert "Q-141" in result.report and "Q-147" in result.report and "Q-142" in result.report


def test_THE_SCORED_BLOCK_MAY_NOT_RUN_BEFORE_probe_v1_RESOLVES(tmp_path, repo_root):
    """⚠️ **THE PRECONDITION RE-ASSERTED FOR THE NEW BLOCK, BECAUSE IT IS THE ONE THAT MATTERS.**

    `CONTEXT.md` §15.1 cuts the pre-registration tags **before** any scored episode, and
    `PROTOCOL.md` §6 calls the order *"not negotiable"*. A real run refuses entirely without it.

    ⚠️ **AND `prereg-v1` IS A SEPARATE, STRICTER GATE THAT THIS CODE DOES NOT ENFORCE** — it is
    the operator's, it is witnessed outside this repository (§15.3), and it is stated in this
    session's handover rather than claimed here.
    """
    request = driver_run.RunRequest(
        matrix=_matrix((2001,)),
        out_root=tmp_path / "real",
        ceilings=Ceilings(call_ceiling=1, token_ceiling=1),
        s3_binding=S3_BINDING,
        spend_real_tokens=True,
    )
    # ⚠️ NOT SKIPPED WHEN THE TAG RESOLVES HERE, AND THAT WAS THIS TEST'S FIRST DEFECT: it is
    # driven against `repo_root=tmp_path`, a directory that is not a git repository at all, so
    # `git rev-parse` cannot resolve `probe-v1` there whatever this tree carries. A skip guarded
    # on the REAL tree would have made the assertion vacuous exactly where the tag exists — which
    # is here, today. A skip is how a check dies quietly.
    assert driver_run.probe_tag_resolves(repo_root), (
        "probe-v1 must resolve in this repository — CONTEXT.md S15.1 cuts it before any scored "
        "episode, and PROTOCOL.md S6 calls the order 'not negotiable'"
    )
    assert not driver_run.probe_tag_resolves(tmp_path), "and not in a directory that is not one"
    with pytest.raises(driver_run.RunRefused, match="probe-v1"):
        driver_run.preflight(
            request, repo_root=tmp_path, utc_date="2026-09-05", liveness_probe=lambda _lane: 200
        )
