"""**ARCH CAL BUILD 1 (`8f3c72e1`) — `Q-191`'s sliding window, replayed on the pilot's own trace.**

⚠️ **A NEW FILE ON PURPOSE**, for the reason `tests/test_arch_lanes.py`'s own header gives:
`INC-138` is a landed commit that deleted an assertion while its message said nothing was
deleted. Putting new tests in a new file makes the diff *"0 files changed"* for every existing
suite, which `git show --numstat` can check and which cannot be got wrong by hand.

**WHAT THIS FILE PINS**

- **§1 THE 60-SECOND SLIDING WINDOW** — `QUESTIONS.md` **`Q-191`**, ruled 2026-09-04.
  Every number is **replayed from the committed usage log**
  ``evals/usage/gemma-26b-2026-09-04.jsonl``, never from a hand-written fixture, for the
  reason `INC-143`'s **Missing** field gives: a fixture can be written to agree with the code
  it checks, and the log cannot — it is an artefact of a spent, single-shot run.

⚠️ **THE DISCRIMINATING ASSERTION IS §1's SECOND TEST**: the shipped TPM limit must **REFUSE
call 7**, which the continuously-refilling bucket **admitted**. It is RED against `HEAD`,
where ``Buckets.tpm`` is a :class:`~whetstone_gate.runner.buckets.Bucket`.
"""

from __future__ import annotations

import inspect
import json
import re
from datetime import datetime
from pathlib import Path

import pytest

from whetstone_gate import config
from whetstone_gate.driver import cal
from whetstone_gate.driver import pilot
from whetstone_gate.driver import run as driver_run
from whetstone_gate.driver import __main__ as driver_main
from whetstone_gate.runner import buckets as runner_buckets
from whetstone_gate.runner import lanes as runner_lanes

# --------------------------------------------------------------------------------------
# The pilot's own trace, read from the COMMITTED log.
# --------------------------------------------------------------------------------------

#: `config/lanes.yaml`'s declared `gemma-26b` TPM. Passed explicitly so this file drives the
#: limiter directly rather than through the loader — the ruling is about the SHAPE, and the
#: capacity is `Q-191`'s own stated figure for the lane it measured.
_PILOT_TPM = 16_000

#: `config/lanes.yaml`'s other declared `gemma-26b` limits, for the whole-lane construction.
_PILOT_RPM, _PILOT_RPD = 30, 14_400


def _pilot_calls(repo_root: Path) -> list[tuple[float, int]]:
    """The eight OK calls as ``(seconds since the first, total_tokens)``.

    ⚠️ **READ FROM THE COMMITTED ARTEFACT.** The ninth record is the ``RATE_LIMITED`` one and
    is deliberately excluded from the trace: it carries ``total_tokens: 0`` because the
    provider refused it, so including it would model a call that cost nothing.
    """
    path = repo_root / "evals" / "usage" / "gemma-26b-2026-09-04.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ok = [row for row in rows if row["outcome"] == "OK"]
    first = datetime.strptime(ok[0]["utc"], "%Y-%m-%dT%H:%M:%SZ")
    return [
        ((datetime.strptime(row["utc"], "%Y-%m-%dT%H:%M:%SZ") - first).total_seconds(), row["total_tokens"])
        for row in ok
    ]


# ======================================================================================
# 1. THE 60-SECOND SLIDING WINDOW — Q-191
# ======================================================================================


def test_the_committed_pilot_log_still_holds_the_EIGHT_NUMBERS_this_file_replays(repo_root):
    """⚠️ **THE PRECONDITION, ASSERTED RATHER THAN ASSUMED — and GREEN on `HEAD`.**

    Every other test in §1 is a statement about these eight calls. If the artefact they are
    read from ever changes, those tests would go on passing against different data and would
    silently stop being about the pilot. `evals/` is append-only and deletion is
    operator-only, so this is a guard against a mistake, not against a policy.
    """
    calls = _pilot_calls(repo_root)
    assert [tokens for _at, tokens in calls] == [790, 3203, 4002, 6201, 6665, 7439, 7782, 6848]
    assert [at for at, _tokens in calls] == [0.0, 32.0, 55.0, 107.0, 145.0, 171.0, 201.0, 219.0]
    assert sum(tokens for _at, tokens in calls) == 42_930, "INC-143's own total"


def test_Q191s_OWN_TRAILING_60s_TABLE_REPRODUCES_from_the_committed_log(repo_root):
    """⚠️ **`Q-191`'s table, recomputed from the artefact rather than transcribed from the
    ruling.** This is pure arithmetic over the log and is **GREEN on `HEAD`**: it says what
    the provider's minute actually held, independently of which shape we model it with.

    The ruling's own column, verbatim::

        call  t(s)   tokens   tokens in the preceding 60s
          6    171     7439       14,104
          7    201     7782       21,886   *** EXCEEDS 16,000 ***
          8    219     6848       22,069   *** EXCEEDS 16,000 ***
          9    220        —       HTTP 429
    """
    calls = _pilot_calls(repo_root)
    trailing = [
        sum(tok for at, tok in calls[: index + 1] if at > moment - 60.0)
        for index, (moment, _tokens) in enumerate(calls)
    ]
    assert trailing == [790, 3993, 7995, 10203, 12866, 14104, 21886, 22069]

    over = [index + 1 for index, total in enumerate(trailing) if total > _PILOT_TPM]
    assert over == [7, 8], (
        "Q-191: the trailing minute exceeds the declared 16,000 at calls 7 and 8 — the two "
        "immediately before the provider answered HTTP 429"
    )
    assert trailing[7] / _PILOT_TPM == pytest.approx(1.379, abs=5e-4), "the ruling's 1.38x"


def test_the_SHIPPED_tpm_limit_REFUSES_call_7_WHICH_THE_CONTINUOUS_BUCKET_ADMITTED(repo_root):
    """⚠️⚠️ **THE DISCRIMINATING TEST, AND THE ONE PROVED RED AGAINST `HEAD`.**

    `Q-191`, RULED 2026-09-04: *"Model TPM as a 60-SECOND SLIDING WINDOW … our
    continuous-refill bucket never empties on the pilot's trace (min 6,170) while a sliding
    window is exceeded at calls 7 and 8."*

    **Both shapes are driven over the same eight real calls, side by side**, which is how
    `INC-148`'s leak test was proved and is the only form that makes the difference visible
    rather than asserted. On `HEAD`, ``Buckets.for_lane(...).tpm`` is a
    :class:`~whetstone_gate.runner.buckets.Bucket` and this test fails at the first
    ``assert``: the continuous bucket admits all eight.

    ⚠️ **NOTE WHAT CALL 8 DOES AND WHY IT IS NOT A CONTRADICTION OF THE RULING.** `Q-191`'s
    table says the trailing minute exceeds the limit at **7 and 8**, and it computes that
    over a trace in which **every call was actually sent**. Here call 7 is *refused*, so it is
    never recorded, and the window at call 8 is correspondingly lighter. Both statements are
    true of different things: the ruling describes **what the provider saw**, this test
    describes **what our limiter would have done**. The arithmetic half is pinned separately
    by :func:`test_Q191s_OWN_TRAILING_60s_TABLE_REPRODUCES_from_the_committed_log`.
    """
    calls = _pilot_calls(repo_root)

    shipped = runner_buckets.Buckets.for_lane(
        name="gemma-26b", rpm=_PILOT_RPM, tpm=_PILOT_TPM, rpd=_PILOT_RPD, tpd=None
    ).tpm
    continuous = runner_buckets.Bucket("control.tpm", _PILOT_TPM, 60.0)

    shipped_refused, continuous_refused = [], []
    for index, (moment, tokens) in enumerate(calls, start=1):
        if shipped.wait_seconds(tokens, moment) > 0.0:
            shipped_refused.append(index)
        else:
            shipped.take(tokens, moment)
        if continuous.wait_seconds(tokens, moment) > 0.0:
            continuous_refused.append(index)
        else:
            continuous.take(tokens, moment)

    assert continuous_refused == [], (
        "the CONTROL must admit every call — that is INC-143's and Q-191's measured finding, "
        "and if it ever refuses one, this test's whole comparison has changed underneath it"
    )
    assert shipped_refused[:1] == [7], (
        "the SHIPPED tpm limit must REFUSE call 7, which the continuous bucket admitted. On "
        "HEAD, Buckets.tpm is a continuously-refilling Bucket and this is the assertion that "
        "fails (Q-191, ruled 2026-09-04)"
    )
    assert continuous.available == pytest.approx(6_170.0), (
        "Q-191 and INC-143 both measured the continuous bucket's minimum as 6,170 of 16,000. "
        "It is re-measured here rather than quoted"
    )


def test_the_shipped_tpm_is_a_SLIDING_WINDOW_and_rpm_rpd_are_STILL_CONTINUOUS_BUCKETS():
    """⚠️ **`Q-191`'s SCOPE, pinned so a later change cannot widen it silently.**

    The ruling names **TPM**. `Q-191` measured requests as *"not remotely implicated"* — a
    maximum of **3** in any 60-second window against a declared 30, and 9 that day against
    14,400 — so RPM and RPD keep the continuous shape they had, and so does TPD.
    """
    lane = runner_buckets.Buckets.for_lane(
        name="gemma-26b", rpm=_PILOT_RPM, tpm=_PILOT_TPM, rpd=_PILOT_RPD, tpd=None
    )
    assert isinstance(lane.tpm, runner_buckets.SlidingWindow)
    assert isinstance(lane.rpm, runner_buckets.Bucket)
    assert isinstance(lane.rpd, runner_buckets.Bucket)
    assert not isinstance(lane.rpm, runner_buckets.SlidingWindow)
    assert not isinstance(lane.rpd, runner_buckets.SlidingWindow)

    with_tpd = runner_buckets.Buckets.for_lane(
        name="qwen-27b", rpm=30, tpm=6_000, rpd=1_000, tpd=500_000
    )
    assert isinstance(with_tpd.tpd, runner_buckets.Bucket)
    assert not isinstance(with_tpd.tpd, runner_buckets.SlidingWindow)


def test_the_window_is_DERIVED_from_the_tpm_key_and_INTRODUCES_NO_NEW_CONSTANT():
    """⚠️ **`Q-191`, in capitals:** *"DERIVE THE WINDOW FROM THE EXISTING tpm KEY; INVENT NO
    NEW CONSTANT."* Hard rule 9.

    The window is the **minute the "M" in TPM already names** — the module's existing
    ``_SECONDS_PER_MINUTE`` unit conversion, which the TPM :class:`Bucket` was already built
    from. The capacity is the lane's own ``tpm``. **Two arguments, both pre-existing.**
    """
    capacity = 12_345
    lane = runner_buckets.Buckets.for_lane(
        name="any", rpm=1, tpm=capacity, rpd=1, tpd=None
    )
    assert lane.tpm.capacity == capacity, "the capacity IS the tpm key, unmodified"
    assert lane.tpm.window_seconds == runner_buckets._SECONDS_PER_MINUTE == 60.0
    # The RPM bucket was already built from the same conversion — so the window is not new.
    assert lane.rpm.window_seconds == lane.tpm.window_seconds

    source = Path(runner_buckets.__file__).read_text(encoding="utf-8")
    assert source.count("_SECONDS_PER_MINUTE = 60.0") == 1, (
        "the minute is defined once, as a unit conversion, and Q-191 added no second one"
    )


def test_a_cost_larger_than_the_whole_window_is_a_REFUSAL_not_an_infinite_wait():
    """The property :class:`Bucket` already had, kept: no amount of waiting admits a call
    bigger than the limit itself, and returning a very large number would look like patience."""
    window = runner_buckets.SlidingWindow("x.tpm", 16_000, 60.0)
    with pytest.raises(runner_buckets.BucketError, match="exceeds its whole capacity"):
        window.wait_seconds(16_001, 0.0)
    assert window.wait_seconds(16_000, 0.0) == 0.0, "exactly the capacity still fits"


def test_the_window_refuses_a_clock_that_runs_BACKWARDS():
    """:class:`Bucket`'s guard, kept — a runner that accepted this would credit itself an
    allowance it never earned."""
    window = runner_buckets.SlidingWindow("x.tpm", 16_000, 60.0)
    window.take(100, 10.0)
    with pytest.raises(runner_buckets.BucketError, match="BEFORE its last refill"):
        window.wait_seconds(100, 5.0)


def test_an_event_exactly_one_window_old_has_LEFT_the_window():
    """⚠️ **The half-open boundary, pinned because an off-by-one here is a 429.**

    A call at ``t=60`` is not inside the minute that began at ``t=0``. Were the comparison
    inclusive, a lane would carry one extra call's tokens forever at the window's edge.
    """
    window = runner_buckets.SlidingWindow("x.tpm", 1_000, 60.0)
    window.take(1_000, 0.0)
    assert window.wait_seconds(1, 59.999) > 0.0, "still inside the window"
    assert window.wait_seconds(1_000, 60.0) == 0.0, "expired exactly at the edge"
    assert window.available == pytest.approx(1_000.0)


# ======================================================================================
# 2. THE CALIBRATION PATH — Q-189's BLOCKER 1
# ======================================================================================


def _section(markdown: str, heading: str) -> str:
    """One section of a markdown document, whitespace-normalised.

    Lifted in shape from ``tests/test_c3_tau2_enumeration.py``, and for its stated reason:
    `CONTEXT.md` wraps its prose, so a regex written against the raw text would match on the
    author's line width rather than on what the law says.
    """
    lines = markdown.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith(heading))
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("#")),
        len(lines),
    )
    return re.sub(r"\s+", " ", " ".join(lines[start:end]))


def test_the_CAL_MATRIX_MATCHES_S10_3s_OWN_SENTENCE_which_is_PARSED_not_transcribed(repo_root):
    """⚠️ **THE LAW IS READ, NEVER COPIED INTO THIS FILE.**

    `CONTEXT.md` §10.3 rule 1 is the pre-registration: *"Arm 1 only, mock world, reference
    attacker, **turn budget 20**, ``n_cal = 30`` episodes."* Each of those figures is parsed
    back out of the specification and diffed against the matrix
    :func:`whetstone_gate.driver.cal.load_cal` builds. **A number written into this file by
    hand would be a third copy that can drift from both** — `test_c3_tau2_enumeration.py`'s
    own reasoning, applied here.
    """
    section = _section((repo_root / "CONTEXT.md").read_text(encoding="utf-8"), "## 10.3 ")

    assert "Arm 1 only" in section, "S10.3 rule 1's arm sentence has moved"
    turn_budget = re.findall(r"\*\*turn budget (\d+)\*\*", section)
    n_cal = re.findall(r"`n_cal = (\d+)` episodes", section)
    assert len(turn_budget) == 1 and len(n_cal) == 1, (
        "the S10.3 parser matched something other than once; a parser that silently reads "
        "nothing reports green over an unchecked claim"
    )

    matrix = cal.load_cal()
    assert matrix.arm == "1", "S10.3: 'Arm 1 only'"
    assert matrix.turn_budget == int(turn_budget[0])
    assert matrix.episode_count == int(n_cal[0])
    assert len(matrix.cells) == 1, "S10.3: 'No other arm or configuration runs inside'"


def test_EVERY_CAL_KEY_CARRIES_THE_CAL_BLOCK_so_it_can_NEVER_read_as_PILOT_or_SCORED():
    """⚠️⚠️ **THE PROPERTY `Q-189` CORRECTION 2 FOUND THE PILOT PATH COULD NOT OFFER.**

    Measured by ARCH PILOT RUN 5: forcing a calibration through ``load_pilot`` would have
    dispatched **nine** live episodes writing ledgers stamped ``block=PILOT`` at slugs
    ``pilot__1__<seed>__gemma-26b`` — *"byte-indistinguishable from the pilot's own, in the
    same directory, with `evals/` append-only and deletion operator-only."*

    :meth:`EpisodeKey.slug` joins ``(block, arm, seed_or_task, attacker_model)`` with
    ``"__"``, so the block label reaches **every checkpoint filename and every ledger stem**.
    """
    keys = cal.load_cal().keys()
    assert len(keys) == 30
    assert {key.block for key in keys} == {cal.CAL_BLOCK} == {"CAL"}
    assert all(key.slug.startswith("cal__") for key in keys)
    assert not any(key.slug.startswith("pilot__") for key in keys)
    assert len({key.slug for key in keys}) == len(keys), "slugs are injective"

    # AND NO CAL SLUG COLLIDES WITH A PILOT SLUG - driven, not reasoned about.
    pilot_keys = pilot.load_pilot(arm="1").keys()
    assert not ({key.slug for key in keys} & {key.slug for key in pilot_keys})


def test_the_CAL_SEEDS_ARE_DISJOINT_FROM_EVERY_OTHER_BAND_which_is_Q189as_WHOLE_POINT():
    """⚠️ **`Q-189`(a), RULED 2026-09-04:** *"DISJOINTNESS IS THE WHOLE POINT, NOT TIDINESS:
    a calibration run on scored seeds fits the void threshold to the very worlds it later
    judges."*

    The objection is `PROTOCOL.md` §2.2's own, applied with more force: the pilot's seeds are
    disjoint so that *"the branch decision"* is not *"made on a look at the episodes it
    decides the size of"*, and the **threshold decides whether the scored run is publishable
    at all.**
    """
    protocol = config.load("protocol")
    cal_band = set(cal.cal_seeds())
    assert len(cal_band) == 30

    for name in ("scored_n50", "scored_n30", "ladder", "pilot"):
        first = int(protocol.require("seeds." + name + "_first"))
        last = int(protocol.require("seeds." + name + "_last"))
        overlap = cal_band & set(range(first, last + 1))
        assert not overlap, (
            f"the CAL seed band overlaps seeds.{name} ({first}..{last}) on "
            f"{sorted(overlap)}. Q-189(a) rules the CAL band DISJOINT from every existing "
            f"one, and a calibration on scored seeds fits the threshold to the worlds it "
            f"later judges"
        )


def test_the_SEED_BLOCK_AND_n_cal_MUST_AGREE_and_a_disagreement_is_a_REFUSAL(monkeypatch):
    """⚠️ **Hard rule 11, one step earlier.** A band carrying other than ``n_cal`` seeds runs
    a **different-sized calibration than the one the spec pre-registers**. It refuses rather
    than quietly running 29 or 31 episodes under a declaration that says 30.
    """
    real = config.load("protocol")

    class _Shifted:
        def require(self, key):
            if key == "seeds.cal_last":
                return int(real.require("seeds.cal_last")) - 1  # 29 seeds against n_cal 30
            return real.require(key)

    monkeypatch.setattr(config, "load", lambda _name: _Shifted())
    with pytest.raises(cal.CalError, match="probe.n_cal"):
        cal.cal_seeds()


def test_load_cal_TAKES_NO_ARGUMENT_where_load_pilot_REQUIRES_ITS_ARM():
    """⚠️ **The difference is deliberate and it is `Q-144` versus §10.3.**

    ``load_pilot`` requires ``arm`` because `CONTEXT.md` §13.4 and `PROTOCOL.md` §3.1 both
    say *"1 ref arm"* and **neither says which**. The calibration's arm is fixed by two
    artefacts — one of them **frozen** — both in terms, so an argument here would be an
    invitation to vary a pre-registered parameter on the run that sets the void threshold.
    """
    assert not inspect.signature(cal.load_cal).parameters, (
        "load_cal must take nothing: every calibration parameter is pre-registered"
    )
    assert "arm" in inspect.signature(pilot.load_pilot).parameters, (
        "load_pilot's arm requirement is Q-144's and must not be removed by this contrast"
    )


def test_the_CAL_MATRIX_SATISFIES_THE_SHAPE_run_py_CONSUMES():
    """⚠️ **A calibration that needed its own runner would be a second, unreviewed execution
    path for the most consequential run in the project.** So the matrix is duck-compatible
    with :class:`~whetstone_gate.driver.pilot.PilotMatrix`, and that is asserted rather than
    assumed — every member :mod:`whetstone_gate.driver.run` reads off a matrix.
    """
    matrix = cal.load_cal()
    for member in ("arm", "turn_budget", "judge_lane", "cells", "episode_count"):
        assert hasattr(matrix, member), f"run.py reads matrix.{member}"
    for method in ("keys", "lane_for", "lines"):
        assert callable(getattr(matrix, method)), f"run.py calls matrix.{method}()"

    # ARM 1 RUNS NO GATE, SO THE JUDGE MAKES ZERO CALLS - but run.py's preflight unions the
    # judge lane into its reserved-lane check (Q-189 correction 2), so it must be NAMED and
    # it must be TRUE. It is the same lane, because gemma-26b's own role string carries both
    # "attacker: REFERENCE ... CAL ..." AND "gate judge for arms 2/2S/3".
    assert matrix.arm not in driver_run.JUDGED_ARMS, "arm 1 has no gate"
    assert matrix.judge_lane == matrix.reference.lane, (
        "the reference lane and the gate-judge lane are the SAME lane in config/lanes.yaml, "
        "which is why Q-189(b)'s one-lane sanction covers this block"
    )


def test_the_CAL_LANE_IS_THE_ONE_WHOSE_ROLE_NAMES_CAL_read_from_lanes_yaml():
    """⚠️ **`Q-189` CORRECTION 3 recorded, against itself, that the one-lane claim had been
    INFERRED rather than read.** The lane itself is well supported and it is read here:
    ``config/lanes.yaml``'s reference-attacker role string **literally contains ``CAL``**.
    The architect confirmed the single cell on 2026-09-04.
    """
    matrix = cal.load_cal()
    lane = runner_lanes.load_lanes()[matrix.reference.lane]
    assert "CAL" in lane.role, (
        "the calibration runs on the lane whose config/lanes.yaml role names CAL; if that "
        "role string ever stops naming it, this cell was chosen by inference again"
    )
    assert lane.name == "gemma-26b"
    assert matrix.reference.attacker_model == lane.name


def test_the_BLOCK_FLAG_DEFAULTS_TO_PILOT_because_a_PUSHED_PREREGISTRATION_CARRIES_NO_BLOCK(repo_root):
    """⚠️⚠️ **THE DEFAULT IS NOT CONVENIENCE. A REQUIRED `--block` WOULD MAKE A COMMITTED,
    PUSHED PRE-REGISTRATION OF AN ALREADY-SPENT SINGLE-SHOT RUN EXIT 2.**

    `evals/pilot/RUN_DECLARED.md` §1 carries **the exact command**, and `PROCESS.md` §6b makes
    that file the declaration from the moment it is pushed. **It has no `--block`.** The pilot
    has already run against it (`INC-142`), so the command is not a plan — it is the record of
    what was executed. A parser change that stopped it parsing would retroactively invalidate
    a pre-registration, which is the one thing a freeze exists to prevent.

    **The declared command is READ OUT OF THE ARTEFACT, not retyped here.**
    """
    declared = (repo_root / "evals" / "pilot" / "RUN_DECLARED.md").read_text(encoding="utf-8")
    block = re.search(r"```sh\n(.*?)```", declared, re.S)
    assert block, "RUN_DECLARED.md S1's fenced command block has moved"
    command = block.group(1)
    assert "--block" not in command, (
        "the committed pilot command now carries --block; this test's premise has changed"
    )

    # Everything after the program name, as the shell would split it.
    argv = [tok for tok in command.replace("\\\n", " ").split() if tok not in ("python", "-m", "--")]
    argv = argv[argv.index("drive") + 1:] if "drive" in argv else argv
    argv = [tok for tok in argv if tok != "whetstone_gate.tasks"]

    parsed = driver_main.build_parser().parse_args(argv)
    assert parsed.block == "pilot", (
        "the DECLARED pilot command must still select the pilot block. If --block ever "
        "becomes required, evals/pilot/RUN_DECLARED.md S1 exits 2 and a pushed "
        "pre-registration stops describing a runnable command (PROCESS.md S6b)"
    )
    assert parsed.arm == "1"


def test_BLOCK_CAL_BUILDS_THE_CALIBRATION_and_a_MISMATCHED_ARM_REFUSES_rather_than_running():
    """⚠️ **`--arm` IS CHECKED, NOT OBEYED, UNDER `--block cal`.**

    `CONTEXT.md` §10.3 rule 1 and **frozen** `HOLES.md` §3.5 rule 1 both say *"arm 1 only"*, so
    the arm is not the operator's to choose here. **The calibration is SINGLE-SHOT** — the first
    execution that runs to completion **is** the run — so an arm typed wrongly would spend the
    one attempt on a block the specification does not describe. It refuses with **exit 2**.
    """
    base = [
        "--dry-run", "--block", "cal", "--s3-binding", "authorization-is-the-payment",
        "--call-ceiling", "600", "--token-ceiling", "4800000",
    ]
    parsed = driver_main.build_parser().parse_args(base + ["--arm", "1"])
    assert parsed.block == "cal"

    for wrong in ("2", "2S", "3", "4"):
        assert driver_main.main(base + ["--arm", wrong]) == 2, (
            f"--block cal with --arm {wrong} must REFUSE with exit 2, not run a calibration "
            f"on an arm CONTEXT.md S10.3 and frozen HOLES.md S3.5 both exclude"
        )
