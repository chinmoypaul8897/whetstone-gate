"""⚠️⚠️ **PREFLIGHT LIVENESS — THE WIRING, NOT THE FUNCTION.** `QUESTIONS.md` `Q-193`.

``tests/test_arch_lanes.py`` §5 already drives
:func:`whetstone_gate.driver.run.liveness_refusal` and its four tests pass. ⚠️ **Every one
of them calls it DIRECTLY, and that is exactly why the defect they were written against
survived them:** the function was fully specified, fully tested and **called from nothing**.

    grep -rn "liveness_refusal" --include=*.py src/ | grep -v "def liveness_refusal"
      -> EMPTY, on the tree these tests were written against.

**So not one test in this file calls ``liveness_refusal``.** Every one drives
:func:`whetstone_gate.driver.run.preflight`, because *reachability from the operator's
command* is the whole content of `Q-193`'s ruling and is the only thing the old tests could
not see.

⚠️ **THE RULING, VERBATIM, on what these tests are for:** *"The pilot's two failures were a
lane that 429'd at turn 8 and a lane that 403'd on every call, and BOTH would have been
refused before a token was spent. … ⚠️ IT MUST REFUSE, NOT WARN, and it must NAME EVERY DEAD
LANE rather than only the first."*
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from whetstone_gate.driver import cal as cal_module
from whetstone_gate.driver import clients
from whetstone_gate.driver import pilot as pilot_module
from whetstone_gate.driver import run as driver_run
from whetstone_gate.runner import usage as usage_module
from whetstone_gate.runner.budget import Ceilings

S3_BINDING = "authorization-is-the-payment"


# --------------------------------------------------------------------------------------
# The harness. ⚠️ It makes the REAL preflight path reachable and NOTHING ELSE.
# --------------------------------------------------------------------------------------


def _real_request(matrix, out_root: Path, **kwargs) -> driver_run.RunRequest:
    """A ``--spend-real-tokens`` request. ⚠️ Ceilings are `Q-189`(b)'s, so a reader of a
    failure sees the calibration's own numbers rather than a test's round ones."""
    return driver_run.RunRequest(
        matrix=matrix,
        out_root=out_root,
        ceilings=Ceilings(
            call_ceiling=kwargs.pop("call_ceiling", 600),
            token_ceiling=kwargs.pop("token_ceiling", 4_800_000),
        ),
        s3_binding=kwargs.pop("s3_binding", S3_BINDING),
        spend_real_tokens=True,
        sanctioned_lanes=frozenset(kwargs.pop("sanctioned_lanes", ("gemma-26b", "qwen-27b"))),
        allow_absent_corpus=False,
    )


def _open_the_real_path(monkeypatch, *, corpus: bool = True) -> None:
    """⚠️ **STUB ONLY THE PRECONDITIONS THAT ARE NOT UNDER TEST**, so what is measured here
    is the liveness wiring and not the state of this working tree.

    ⚠️ **MEASURED IN THIS TREE ON 2026-09-04, because the earlier draft of this docstring
    asserted the opposite and was wrong: ``probe-v1`` DOES resolve and ``corpora/fetched/``
    DOES exist.** What still refuses a real preflight here is the API **key names**, which a
    test may not supply — `CLAUDE.md` §4 — so ``missing_keys`` is stubbed to *nothing absent*
    rather than a key being read. ``probe_tag_resolves`` and ``_resolve_corpus`` are stubbed
    too, so that these tests keep measuring the liveness wiring on the day the tag is cut or
    the corpora move, rather than quietly changing what they assert.
    """
    monkeypatch.setattr(driver_run, "probe_tag_resolves", lambda _root: True)
    monkeypatch.setattr(driver_run, "missing_keys", lambda _providers: ())
    if corpus:
        monkeypatch.setattr(
            driver_run,
            "_resolve_corpus",
            lambda _request: ((), "  corpus                 : STUBBED BY THE TEST"),
        )


class _Probe:
    """A liveness probe that RECORDS what it was asked, so a test can assert on the calls
    that were **not** made as well as on the ones that were."""

    def __init__(self, statuses: dict[str, int] | None = None, default: int = 200) -> None:
        self.statuses = statuses or {}
        self.default = default
        self.asked: list[str] = []

    def __call__(self, lane: str) -> int:
        self.asked.append(lane)
        return self.statuses.get(lane, self.default)


# ======================================================================================
# 1. ⚠️ THE REFUSAL — IT MUST REFUSE, NOT WARN
# ======================================================================================


def test_preflight_REFUSES_A_REAL_RUN_ON_A_DEAD_LANE_AND_NAMES_IT(
    tmp_path, repo_root, monkeypatch
):
    """⚠️⚠️ **THE TEST `INC-142` IS OWED.** ``qwen-27b`` answered **HTTP 403 to every one of
    its ten calls** and the pilot — this project's single, unrepeatable artefact — was spent
    discovering it. Preflight passed all seven of `RUN_DECLARED.md` §7.3's preconditions on
    the way, because **not one of them makes a call.**

    ⚠️ **A ``RunRefused``, NOT A PRINTED LINE.** `PROCESS.md` §6b makes the first completed
    execution *the* run, so a warning above a single-shot run is a warning above a spent
    artefact. ``__main__`` turns this exception into exit 2; a ``lines`` entry would scroll
    past."""
    _open_the_real_path(monkeypatch)
    probe = _Probe({"qwen-27b": 403})
    request = _real_request(pilot_module.load_pilot(arm="1"), tmp_path / "real")
    with pytest.raises(driver_run.RunRefused) as refused:
        driver_run.preflight(
            request, repo_root=repo_root, utc_date="2026-09-04", liveness_probe=probe
        )
    text = str(refused.value)
    assert "qwen-27b" in text, "the refusal must NAME the lane, not merely count it"
    assert "403" in text, "INC-142's Missing field is that the status could not be read"
    assert "gemma-26b answered" not in text, "a live lane must not be reported dead"


def test_preflight_NAMES_EVERY_DEAD_LANE_not_just_the_first(tmp_path, repo_root, monkeypatch):
    """⚠️ **The pilot's two lanes were broken in two DIFFERENT ways** — one 429, one 403.
    A check that stopped at the first would have sent the operator back for a second
    single-shot run to discover the second, **and there is no second single-shot run.**"""
    _open_the_real_path(monkeypatch)
    probe = _Probe({"gemma-26b": 500, "qwen-27b": 403})
    request = _real_request(pilot_module.load_pilot(arm="1"), tmp_path / "real")
    with pytest.raises(driver_run.RunRefused) as refused:
        driver_run.preflight(
            request, repo_root=repo_root, utc_date="2026-09-04", liveness_probe=probe
        )
    text = str(refused.value)
    assert "gemma-26b" in text and "500" in text
    assert "qwen-27b" in text and "403" in text
    assert sorted(set(probe.asked)) == ["gemma-26b", "qwen-27b"], (
        "every lane must be PROBED even after the first is found dead - otherwise the "
        "refusal cannot name them all"
    )


def test_preflight_counts_a_429_as_a_refusal_before_the_run_starts(
    tmp_path, repo_root, monkeypatch
):
    """A lane already rate-limited **before** the run starts cannot complete it, and
    `CLAUDE.md` §4 forbids waiting it out by retrying into another lane."""
    _open_the_real_path(monkeypatch)
    request = _real_request(pilot_module.load_pilot(arm="1"), tmp_path / "real")
    with pytest.raises(driver_run.RunRefused, match="429"):
        driver_run.preflight(
            request,
            repo_root=repo_root,
            utc_date="2026-09-04",
            liveness_probe=_Probe(default=429),
        )


def test_preflight_PASSES_and_SAYS_SO_when_every_lane_answers(tmp_path, repo_root, monkeypatch):
    """A guardrail that refused a healthy run would be switched off within a day — and one
    that passed **silently** would be indistinguishable from one that never ran."""
    _open_the_real_path(monkeypatch)
    probe = _Probe()
    checks = driver_run.preflight(
        _real_request(pilot_module.load_pilot(arm="1"), tmp_path / "real"),
        repo_root=repo_root,
        utc_date="2026-09-04",
        liveness_probe=probe,
    )
    assert sorted(set(probe.asked)) == ["gemma-26b", "qwen-27b"]
    assert any("liveness" in line.lower() for line in checks.lines), (
        "a check that leaves no line in the preflight report cannot be shown to have run"
    )


# ======================================================================================
# 2. ⚠️ THE CALIBRATION'S OWN SHAPE — ONE LANE, ONE CALL
# ======================================================================================


def test_the_CALIBRATION_probes_exactly_ONE_lane(tmp_path, repo_root, monkeypatch):
    """⚠️ **The disclosed cost, asserted rather than left in prose.** `Q-189`(b) rules the
    calibration onto **one** lane, so its liveness cost is **one call** against a 600-call
    ceiling. If this ever probes two, the declaration's cost line is wrong."""
    _open_the_real_path(monkeypatch)
    probe = _Probe()
    driver_run.preflight(
        _real_request(cal_module.load_cal(), tmp_path / "cal", sanctioned_lanes=("gemma-26b",)),
        repo_root=repo_root,
        utc_date="2026-09-04",
        liveness_probe=probe,
    )
    assert probe.asked == ["gemma-26b"], (
        "the calibration dispatches on ONE lane and its judge lane is the same one; "
        "evals/cal/RUN_DECLARED.md S5 publishes 'ONE liveness call' on that basis"
    )


# ======================================================================================
# 3. ⚠️ IT RUNS LAST, BECAUSE IT IS THE ONLY PRECONDITION THAT SPENDS
# ======================================================================================


def test_a_FREE_refusal_fires_WITHOUT_SPENDING_A_PROBE_CALL(tmp_path, repo_root, monkeypatch):
    """⚠️ **`Q-193`'s choice (1), pinned.** An absent corpus is a refusal; so is an
    unresolved `probe-v1`. **Both are free.** A liveness check ordered before them would
    spend one call per lane to reach a refusal that cost nothing — *a guardrail against
    wasted spend that wastes spend to run.*"""
    _open_the_real_path(monkeypatch, corpus=False)

    def refuse(_request):
        raise driver_run.RunRefused("the pinned corpora are not fetched")

    # ⚠️ FORCED, NOT OBSERVED. `corpora/fetched/` EXISTS in this tree, so a test that
    # `pytest.skip`ped on that condition would be silent in the very tree the calibration
    # runs in — which is the only tree whose ordering matters.
    monkeypatch.setattr(driver_run, "_resolve_corpus", refuse)
    probe = _Probe()
    with pytest.raises(driver_run.RunRefused, match="corpora"):
        driver_run.preflight(
            _real_request(pilot_module.load_pilot(arm="1"), tmp_path / "real"),
            repo_root=repo_root,
            utc_date="2026-09-04",
            liveness_probe=probe,
        )
    assert probe.asked == [], "a FREE refusal must not have spent a provider call first"


def test_an_unresolved_probe_v1_refuses_WITHOUT_SPENDING_A_PROBE_CALL(
    tmp_path, repo_root, monkeypatch
):
    """⚠️ **`probe-v1` DOES resolve in this tree**, so the condition is FORCED rather than
    waited for. `CONTEXT.md` §15.1 cuts that tag before the calibration and `PROTOCOL.md` §6
    calls the order *"not negotiable"* — the refusal must arrive with **zero** provider calls
    behind it, whichever way the tag happens to sit on the day the suite runs."""
    monkeypatch.setattr(driver_run, "probe_tag_resolves", lambda _root: False)
    probe = _Probe()
    with pytest.raises(driver_run.RunRefused, match="probe-v1"):
        driver_run.preflight(
            _real_request(pilot_module.load_pilot(arm="1"), tmp_path / "real"),
            repo_root=repo_root,
            utc_date="2026-09-04",
            liveness_probe=probe,
        )
    assert probe.asked == []


# ======================================================================================
# 4. ⚠️ A MISSING PROBE ON A REAL RUN IS A REFUSAL, NEVER A SKIP
# ======================================================================================


def test_a_real_run_with_NO_PROBE_REFUSES_rather_than_skipping_the_check(
    tmp_path, repo_root, monkeypatch
):
    """⚠️⚠️ **THE FAILURE MODE THIS GUARDRAIL WOULD OTHERWISE HAVE.** If ``liveness_probe``
    defaulted to *"then don't check"*, every caller that forgot it would get the pre-`Q-193`
    behaviour back **with a green suite** — hard rule 9's *"a missing value is a hard
    refusal, never a silent fallback"*, applied to a callable instead of a config value."""
    _open_the_real_path(monkeypatch)
    with pytest.raises(driver_run.RunRefused, match="liveness"):
        driver_run.preflight(
            _real_request(pilot_module.load_pilot(arm="1"), tmp_path / "real"),
            repo_root=repo_root,
            utc_date="2026-09-04",
        )


# ======================================================================================
# 5. ⚠️ A DRY RUN PROBES NOTHING
# ======================================================================================


def test_a_DRY_RUN_MAKES_ZERO_PROBE_CALLS(tmp_path, repo_root):
    """⚠️ **`Q-193`'s choice (2), pinned — and its COST is pinned with it.** ``--dry-run``
    promises no network call; a liveness probe would be the only real provider call in a
    rehearsal. **So the rehearsal still cannot tell the operator whether the lanes are
    alive**, which is `INC-142`'s own `Expectation` and is NOT closed by this work."""
    probe = _Probe()
    request = driver_run.RunRequest(
        matrix=pilot_module.load_pilot(arm="1"),
        out_root=tmp_path / "dry",
        ceilings=Ceilings(call_ceiling=600, token_ceiling=4_800_000),
        s3_binding=S3_BINDING,
        spend_real_tokens=False,
        sanctioned_lanes=frozenset(),
        allow_absent_corpus=True,
    )
    checks = driver_run.preflight(
        request, repo_root=repo_root, utc_date="2026-09-04", liveness_probe=probe
    )
    assert probe.asked == [], "a dry run must make NO provider call, liveness included"
    assert any(
        "NOT EXERCISED" in line and "liveness" in line.lower() for line in checks.lines
    ), (
        "the dry run must SAY the liveness check did not run, exactly as it already says so "
        "of the lane reservations and the API keys - an unmentioned skip reads as a pass"
    )


# ======================================================================================
# 6. ⚠️ THE COST IS DISCLOSED IN A SEPARATE FILE, NEVER IN THE RUN'S OWN LOG
# ======================================================================================


def _client_with(transport, lane: str = "gemma-26b"):
    """The real client over a FAKE transport — ``clients.Transport`` is *"THE ONE SEAM"*, so
    this exercises the shipped body, headers, status handling and usage row and makes **zero**
    provider calls."""
    return clients.MeteredProviderClient.for_lane_names(
        attacker_lanes=[lane], judge_lane=lane, transport=transport
    )


def test_liveness_calls_are_written_to_a_SEPARATE_usage_file(tmp_path, monkeypatch):
    """⚠️ **THE RULING, VERBATIM:** *"each run's own liveness calls are spend, and they are
    written to a SEPARATE usage file as arch-lanes-1 did, never into the run's own log."*

    `arch-lanes-1`'s reason, restated: ``evals/usage/gemma-26b-<date>.jsonl`` is the file
    `INC-143`'s eight measured numbers are read from **and** the file this project's own tests
    replay. Appending to it would alter an artefact the incident log cites.

    ⚠️ **THE TOKEN COUNT IS THE PROVIDER'S OWN AND IS NEVER ESTIMATED** — which is why the
    probe lives on the client at all: ``preflight`` sees a status and could only have guessed."""
    monkeypatch.setenv("GOOGLE_API_KEY", "not-a-real-key-and-never-read-back")
    body = json.dumps(
        {
            "candidates": [{"content": {"parts": [{"text": "pong"}]}}],
            "usageMetadata": {"totalTokenCount": 21},
        }
    ).encode("utf-8")
    client = _client_with(lambda _u, _b, _h: clients.HttpResponse(status=200, body=body))
    log = usage_module.UsageLog.under(tmp_path)
    status = client.liveness_probe(
        "gemma-26b", usage=log, block="CAL", date="2026-09-04", utc="2026-09-04T09:00:00Z"
    )
    assert status == 200
    written = sorted(p.name for p in (tmp_path / "evals" / "usage").glob("*.jsonl"))
    assert written == ["liveness-CAL-2026-09-04.jsonl"], (
        "exactly one file, stamped with the BLOCK, and NOT the run's own lane log"
    )
    rows = [
        json.loads(line)
        for line in (tmp_path / "evals" / "usage" / written[0]).read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    assert len(rows) == 1
    assert rows[0]["lane"] == "gemma-26b"
    assert rows[0]["status"] == 200
    assert rows[0]["total_tokens"] == 21, "the PROVIDER's own count, never an estimate"
    assert rows[0]["episode"] == "PREFLIGHT_LIVENESS", (
        "it must not look like an episode slug - a reader or a replay that mistook a "
        "preflight call for an episode would put a call in a denominator no episode produced"
    )
    blob = json.dumps(rows)
    assert "not-a-real-key" not in blob and "Bearer" not in blob, (
        "the STATUS is all that crosses this boundary - no body, no header (INC-142)"
    )


def test_a_dead_lane_is_RECORDED_as_spend_even_though_it_REFUSES(tmp_path, monkeypatch):
    """⚠️ **A REFUSED RUN STILL SPENT THE PROBE, AND HARD RULE 11 COUNTS IT.** *"Every dropped
    episode is counted, categorised and printed as a number."* A guardrail whose own cost
    vanished from the record whenever it fired would under-report exactly when it mattered."""
    monkeypatch.setenv("GOOGLE_API_KEY", "not-a-real-key-and-never-read-back")
    client = _client_with(
        lambda _u, _b, _h: clients.HttpResponse(
            status=403, body=b'{"error":{"type":"forbidden"}}'
        )
    )
    log = usage_module.UsageLog.under(tmp_path)
    status = client.liveness_probe(
        "gemma-26b", usage=log, block="CAL", date="2026-09-04", utc="2026-09-04T09:00:00Z"
    )
    assert status == 403, "the STATUS is returned so liveness_refusal can NAME it"
    rows = [
        json.loads(line)
        for line in (
            tmp_path / "evals" / "usage" / "liveness-CAL-2026-09-04.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows[0]["outcome"] == "ERROR" and rows[0]["status"] == 403
    assert rows[0]["total_tokens"] == 0


def test_a_429_on_the_probe_is_recorded_with_ZERO_tokens(tmp_path, monkeypatch):
    """Golden 8 fixture D, verbatim: *"a 429'd call contributes ZERO tokens"* — the request
    was refused by the rate limiter and never ran. ``UsageLog.append`` refuses any other
    claim, so this pins the mapping rather than the arithmetic."""
    monkeypatch.setenv("GOOGLE_API_KEY", "not-a-real-key-and-never-read-back")
    client = _client_with(lambda _u, _b, _h: clients.HttpResponse(status=429, body=b"{}"))
    log = usage_module.UsageLog.under(tmp_path)
    assert (
        client.liveness_probe(
            "gemma-26b", usage=log, block="CAL", date="2026-09-04", utc="2026-09-04T09:00:00Z"
        )
        == 429
    )
    rows = [
        json.loads(line)
        for line in (
            tmp_path / "evals" / "usage" / "liveness-CAL-2026-09-04.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows[0]["outcome"] == "RATE_LIMITED" and rows[0]["total_tokens"] == 0
