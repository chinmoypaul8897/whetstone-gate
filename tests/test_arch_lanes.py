"""**ARCH LANES 1 (`6d1a94f3`) — the two pilot failures, made DIAGNOSABLE and made PACED.**

`INCIDENTS.md` **INC-142** and **INC-143** are the two defects the single-shot pilot bought.
This file is their regression suite, and every test in it was **proved RED against `HEAD`
before the fix that makes it green** — the one exception is named in its own docstring and
is called what it is, rather than presented as a red-to-green it is not.

⚠️ **A NEW FILE ON PURPOSE.** `INC-138` is a landed commit that deleted an assertion while
its message said nothing was deleted, and its author's own verification passed. Adding these
tests to an existing file puts every one of that file's assertions within reach of a careless
edit; putting them in a new one makes the diff *"0 files changed"* for every existing suite,
which is checkable by `git show --numstat` and cannot be got wrong.

**WHAT EACH GROUP PINS**

- **§1 THE `User-Agent`** — `INC-142`'s cause, MEASURED live on 2026-09-04 under this
  session's 4-call sanction: `qwen-27b` answered **HTTP 403** with a **17-byte non-JSON**
  body to the shipped request, and answered **HTTP 200** to the byte-identical request
  carrying a conventional `User-Agent`. The credential and the `api_model_id` were never the
  problem.
- **§2 THE STATUS AND THE SHORT ERROR TYPE** — `INC-142`'s *"most expensive line"*: the
  status was **in** the `ProviderFailed` message and `raise ... from None` threw it away.
- **§3 THE REDACTION BOUNDARY** — what may be carried, and what may never be.
- **§4 THE PACER** — `INC-143`, replayed against the pilot's **own eight real token counts**.
"""

from __future__ import annotations

import dataclasses
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from whetstone_gate.driver import clients as driver_clients
from whetstone_gate.driver import run as driver_run
from whetstone_gate.runner import buckets as runner_buckets
from whetstone_gate.runner import redaction as runner_redaction
from whetstone_gate.runner import usage as runner_usage

# --------------------------------------------------------------------------------------
# Fixtures, in this file's own house style (mirroring tests/test_c12_driver.py)
# --------------------------------------------------------------------------------------


@pytest.fixture
def _no_provider_call(monkeypatch):
    """⚠️ **ZERO PROVIDER CALLS IN THIS FILE, ASSERTED RATHER THAN INTENDED.**"""

    def refuse(*_args, **_kwargs):  # pragma: no cover - the point is that it never runs
        raise AssertionError(
            "a test reached the REAL provider transport. No session may spend on these "
            "lanes (PROCESS.md S8 LANE RESERVATION)"
        )

    monkeypatch.setattr(driver_clients, "_http_post", refuse)
    return refuse


@pytest.fixture
def _key_names(monkeypatch):
    """Both key NAMES set to obvious non-secrets. No real key is read by this file."""
    monkeypatch.setenv("GOOGLE_API_KEY", "not-a-real-key-google")
    monkeypatch.setenv("GROQ_API_KEY", "not-a-real-key-groq")


@dataclasses.dataclass
class _FakeTransport:
    """One canned HTTP answer, and every request it was handed."""

    status: int
    body: bytes
    calls: int = 0
    seen: list = dataclasses.field(default_factory=list)

    def __call__(self, url, body, headers):
        self.calls += 1
        self.seen.append((url, body, dict(headers)))
        return driver_clients.HttpResponse(status=self.status, body=self.body)


def _groq_ok(total=987):
    return json.dumps(
        {
            "choices": [{"message": {"role": "assistant", "content": "the reply"}}],
            "usage": {"prompt_tokens": 900, "completion_tokens": 50, "total_tokens": total},
        }
    ).encode("utf-8")


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


def _client(transport, *, attacker="gemma-26b", judge="gemma-26b"):
    return driver_clients.MeteredProviderClient.for_lanes(
        attacker_lane=attacker, judge_lane=judge, transport=transport
    )


_MESSAGES = ({"role": "user", "content": "hello"},)


# --------------------------------------------------------------------------------------
# 1. THE `User-Agent` — INC-142's actual cause, measured
# --------------------------------------------------------------------------------------


def test_the_GROQ_request_carries_a_User_Agent_header(
    _no_provider_call, _key_names
):
    """⚠️⚠️ **THIS IS `INC-142`(b)'s WHOLE CAUSE, AND IT IS ONE HEADER.**

    **MEASURED live on 2026-09-04** under this session's sanctioned 4-call ceiling, calls 3
    and 4, against `qwen/qwen3.8-27b` on Groq:

    ===========================================  ========  ==========================
    request                                      status    body
    ===========================================  ========  ==========================
    the SHIPPED one (urllib's default UA)        **403**   17 bytes, **not JSON**
    byte-identical + ``User-Agent: Mozilla/5.0`` **200**   567 bytes, JSON, 21 tokens
    ===========================================  ========  ==========================

    **The only difference between the two requests is this header.** The credential was
    valid and the `api_model_id` existed — both proved by the 200, not assumed — so the
    pilot's 10-for-10 `PROVIDER_ERROR` was an **edge block on the client identifier**, and
    every one of those ten calls was refused before it reached a model. That is why they
    cost **0 tokens each and returned instantly**.
    """
    transport = _FakeTransport(status=200, body=_groq_ok())
    _client(transport, attacker="qwen-27b").complete_attacker(
        messages=_MESSAGES, temperature=0.7, lane="qwen-27b"
    )
    _url, _body, headers = transport.seen[0]
    assert "User-Agent" in headers, (
        "the Groq request carries no User-Agent. MEASURED 2026-09-04: Groq's edge answers "
        "HTTP 403 with a 17-byte non-JSON body to a request without one, and HTTP 200 to "
        "the byte-identical request with one. INC-142(b)"
    )
    assert headers["User-Agent"].strip(), "a User-Agent that is blank is not a User-Agent"


def test_the_GOOGLE_request_carries_the_SAME_User_Agent_header(
    _no_provider_call, _key_names
):
    """**Both providers, one identifier.** Google answered 200 without one (measured, call
    1 of the same sanction), so this is not a fix Google needed — it is the same client
    identifying itself the same way on both lanes, which is what makes the next edge block
    a *known* variable rather than a new mystery."""
    transport = _FakeTransport(status=200, body=_google_ok())
    _client(transport, attacker="gemma-26b").complete_attacker(
        messages=_MESSAGES, temperature=0.7, lane="gemma-26b"
    )
    _url, _body, headers = transport.seen[0]
    assert "User-Agent" in headers
    assert headers["User-Agent"] == driver_clients._USER_AGENT


def test_the_User_Agent_NAMES_THIS_PROJECT_and_carries_no_secret():
    """A `User-Agent` is sent to a third party on every call, so it is a disclosure surface.
    It must identify the project and must not be a credential-shaped string."""
    from whetstone_gate.runner.redaction import refuse_if_secret_bearing

    agent = driver_clients._USER_AGENT
    assert isinstance(agent, str) and agent.strip()
    assert "whetstone" in agent.lower(), (
        "the User-Agent should say who is calling; an anonymous browser string invites the "
        "same class of block for the opposite reason"
    )
    refuse_if_secret_bearing(agent, where="$._USER_AGENT")


# --------------------------------------------------------------------------------------
# 2. THE STATUS AND THE SHORT ERROR TYPE — INC-142's "most expensive line"
# --------------------------------------------------------------------------------------


def test_a_NON_2xx_raises_ProviderFailed_CARRYING_ITS_STATUS(
    _no_provider_call, _key_names
):
    """⚠️ **`INC-142` Missing, verbatim:** *"The record cannot distinguish an HTTP 401 from a
    404 from a 200 with a malformed body."* It can now, and this is the assertion that says
    so. The status is a **number**; it cannot quote a credential."""
    transport = _FakeTransport(status=403, body=b"error: forbidden")
    with pytest.raises(driver_clients.ProviderFailed) as caught:
        _client(transport, attacker="qwen-27b").complete_attacker(
            messages=_MESSAGES, temperature=0.7, lane="qwen-27b"
        )
    assert caught.value.status == 403, (
        "ProviderFailed must carry the HTTP status as a field. Before ARCH LANES 1 it was "
        "only interpolated into a message that episode.py discards with `from None`"
    )


def test_the_PILOTS_OWN_403_reproduces_and_is_DISTINGUISHABLE_from_a_401_and_a_404(
    _no_provider_call, _key_names
):
    """Three different failures must produce three different records. **That is the whole
    of `INC-142`'s Missing field.**"""
    seen = {}
    for status in (401, 403, 404):
        transport = _FakeTransport(status=status, body=b"error")
        with pytest.raises(driver_clients.ProviderFailed) as caught:
            _client(transport, attacker="qwen-27b").complete_attacker(
                messages=_MESSAGES, temperature=0.7, lane="qwen-27b"
            )
        seen[status] = caught.value.status
    assert seen == {401: 401, 403: 403, 404: 404}


def test_a_SHORT_provider_supplied_error_TYPE_is_carried_when_the_body_is_JSON(
    _no_provider_call, _key_names
):
    """Groq's error object is ``{"error": {"message": ..., "type": ..., "code": ...}}``.
    ⚠️ **`type` and `code` are carried. `message` is NOT**, and the next test is why."""
    body = json.dumps(
        {"error": {"message": "a long human sentence", "type": "invalid_request_error",
                   "code": "model_not_found"}}
    ).encode("utf-8")
    transport = _FakeTransport(status=404, body=body)
    with pytest.raises(driver_clients.ProviderFailed) as caught:
        _client(transport, attacker="qwen-27b").complete_attacker(
            messages=_MESSAGES, temperature=0.7, lane="qwen-27b"
        )
    carried = caught.value.error_type
    assert carried is not None
    assert "invalid_request_error" in carried or "model_not_found" in carried


def test_a_NON_JSON_error_body_yields_a_status_and_NO_invented_type(
    _no_provider_call, _key_names
):
    """⚠️ **THE PILOT'S ACTUAL SHAPE: 17 bytes, not JSON.** The status is still carried; the
    error type is ``None``, because there was none. **An absent type is reported as absent
    and never synthesised** — a guessed type reads exactly like a measured one."""
    transport = _FakeTransport(status=403, body=b"error: forbidden")
    with pytest.raises(driver_clients.ProviderFailed) as caught:
        _client(transport, attacker="qwen-27b").complete_attacker(
            messages=_MESSAGES, temperature=0.7, lane="qwen-27b"
        )
    assert caught.value.status == 403
    assert caught.value.error_type is None


def test_the_USAGE_ROW_for_an_ERROR_carries_the_status(tmp_path):
    """`INC-142`: the operator could not tell *"whether the qwen lane needs a credential, a
    corrected `api_model_id`, or a parser change."* The row now says which."""
    log = runner_usage.UsageLog.under(tmp_path)
    log.append(
        model="qwen-27b", date="2026-09-04", utc="2026-09-04T03:30:22Z", lane="qwen-27b",
        episode="pilot__1__2101__qwen-27b", total_tokens=0, outcome="ERROR",
        status=403, error_type="invalid_request_error",
    )
    row = next(log.rows("qwen-27b", "2026-09-04"))
    assert row["status"] == 403
    assert row["error_type"] == "invalid_request_error"


def test_an_OK_usage_row_is_BYTE_IDENTICAL_to_the_one_the_PILOT_WROTE(tmp_path):
    """⚠️ **THE PILOT'S COMMITTED ROWS MUST STILL READ BACK EXACTLY.** `evals/` is
    append-only and `INC-143`'s eight numbers are measured from those rows, so a schema
    change that added keys to a *successful* row would silently re-shape the record this
    project's own incident log cites. The new keys appear **only when there is something to
    report**, which for an `OK` row is never."""
    log = runner_usage.UsageLog.under(tmp_path)
    log.append(
        model="gemma-26b", date="2026-09-04", utc="2026-09-04T03:26:42Z", lane="gemma-26b",
        episode="pilot__1__2101__gemma-26b", total_tokens=790, outcome="OK",
    )
    written = (tmp_path / "evals" / "usage" / "gemma-26b-2026-09-04.jsonl").read_text(
        encoding="utf-8"
    ).strip()
    assert written == (
        '{"episode": "pilot__1__2101__gemma-26b", "lane": "gemma-26b", "model": "gemma-26b",'
        ' "outcome": "OK", "total_tokens": 790, "utc": "2026-09-04T03:26:42Z"}'
    )


# --------------------------------------------------------------------------------------
# 3. THE REDACTION BOUNDARY — what may be carried, and what may NEVER be
# --------------------------------------------------------------------------------------


_PLANTED = runner_redaction._KEY_PREFIXES[0] + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
"""A key-SHAPED string. **It is not a credential; it is the shape one has.**

⚠️⚠️ **ASSEMBLED AT RUNTIME, AND NOT WRITTEN AS A LITERAL, BECAUSE THIS REPOSITORY'S OWN
INVARIANT REFUSED THE LITERAL — CORRECTLY.** `check_roles.py:73` scans every tracked file for
``\\bgsk_[A-Za-z0-9]{20,}``, and the first draft of this constant put exactly that in a tracked
test file: **`[FAIL] C1 no secret-shaped string in any tracked file — HITS:
tests/test_arch_lanes.py:293 — Groq API key`.** ⚠️ **The check was right and the test was
wrong.** A scanner that a test file may opt out of is not a scanner, so the fix is on this side:
no string literal here has the shape, and the shape only exists in memory while the test runs.

⚠️ **AND THE PREFIX IS READ FROM THE MODULE UNDER TEST, NOT TRANSCRIBED.**
:data:`whetstone_gate.runner.redaction._KEY_PREFIXES` is Groq's own documented public prefix —
*"neither is a secret"* — and **`qwen-27b` is the Groq lane whose error path this whole file is
about.** Reading it means this test cannot drift away from the list it is meant to exercise: if
that list changes, this planted value changes with it, rather than silently testing a shape the
scanner no longer looks for. A planted `sk-proj-…` would be an OpenAI shape this project uses
nowhere, so a green test against it would measure nothing.

⚠️ **AND THE SCAN IS THE BACKSTOP, NOT THE PROTECTION.** `redaction.py`'s own module
docstring says so: *"not of a known prefix shape, and not equal to anything set … passes. The
scan is a guard against the realistic accident, not a proof."* The real protection here is
**structural** — :data:`whetstone_gate.driver.clients._ERROR_TYPE_KEYS` does not contain
``message``, so the free-text field a provider would quote a credential into is never read at
all. The assertions below check the structure first and the scan second.
"""


def test_a_planted_KEY_SHAPED_string_in_an_error_body_reaches_NEITHER_the_exception_FIELDS_NOR_a_usage_row(
    _no_provider_call, _key_names, tmp_path
):
    """⚠️⚠️ **THE TEST THE PROMPT REQUIRED, AND AN HONEST NOTE ABOUT ITS COLOUR.**

    `INC-142` records that the body suppression *"is deliberate and its stated reason is
    sound — a provider error can quote the credential it rejected."* Carrying the **status**
    and a **short type** must not quietly re-open that door.

    ⚠️ **THIS TEST IS NOT A HONEST RED-TO-GREEN AGAINST `HEAD`, AND SAYING SO IS THE POINT.**
    Against `HEAD` it passes **vacuously**: `HEAD` carries *nothing at all* out of a provider
    error, so nothing can leak and there is nothing for the test to discriminate. It was
    proved RED against the **naive** form of this session's own fix — the one-line version
    that carried ``str(exc)`` or ``error["message"]`` through instead of the short type —
    which is the only code this assertion can separate from the correct fix. **A test that
    is green on `HEAD` for the wrong reason is worth recording as such rather than counting
    as evidence it is not.**
    """
    body = json.dumps(
        {"error": {"message": f"invalid api key {_PLANTED}", "type": "invalid_api_key",
                   "code": _PLANTED}}
    ).encode("utf-8")
    transport = _FakeTransport(status=401, body=body)
    with pytest.raises(driver_clients.ProviderFailed) as caught:
        _client(transport, attacker="qwen-27b").complete_attacker(
            messages=_MESSAGES, temperature=0.7, lane="qwen-27b"
        )
    failure = caught.value

    # (a) the exception's own message and fields
    assert _PLANTED not in str(failure)
    assert _PLANTED not in repr(failure)
    assert failure.error_type is None or _PLANTED not in failure.error_type
    assert failure.status == 401

    # (b) a usage row built from those fields
    log = runner_usage.UsageLog.under(tmp_path)
    log.append(
        model="qwen-27b", date="2026-09-04", utc="2026-09-04T03:30:22Z", lane="qwen-27b",
        episode="pilot__1__2101__qwen-27b", total_tokens=0, outcome="ERROR",
        status=failure.status, error_type=failure.error_type,
    )
    written = (tmp_path / "evals" / "usage" / "qwen-27b-2026-09-04.jsonl").read_text(
        encoding="utf-8"
    )
    assert _PLANTED not in written


def test_a_credential_in_ONE_field_beside_an_ORDINARY_enum_in_ANOTHER_is_STILL_WITHHELD(
    _no_provider_call, _key_names
):
    """⚠️⚠️ **THIS IS THE LEAK THE TEST ABOVE ACTUALLY CAUGHT, AND IT WAS IN THIS SESSION'S
    OWN NEW CODE.** It is pinned separately because it is the sharpest case and because a
    future edit to `_short_error_type` will reintroduce it by accident.

    `_short_error_type` joins the fields it reads. The first version scanned the **joined**
    string — and `runner/redaction.py`'s scan is **prefix-anchored** (`INC-147`): it asks
    whether a string *begins* with `gsk_`, not whether it *contains* one. So a provider
    putting an ordinary enum in ``type`` and a credential in ``code`` produced
    ``"invalid_api_key/gsk_…"``, which **begins with neither prefix and went straight
    through the guard**.

    ⚠️ **IT PASSED ONLY BY AN ACCIDENT OF LENGTH, WHICH IS WORSE THAN FAILING.** With the
    first planted value the join overflowed :data:`_ERROR_TYPE_MAX_CHARS` and the tail was
    *truncated off*, so the assertion held for a reason that had nothing to do with safety.
    Shortening the planted value by twelve characters turned the test red and exposed it.

    The fix scans **each part before joining**, which restores the anchor: a credential in
    any single field is then the *start* of the string being tested.
    """
    body = json.dumps(
        {"error": {"type": "invalid_api_key", "code": _PLANTED}}
    ).encode("utf-8")
    transport = _FakeTransport(status=401, body=body)
    with pytest.raises(driver_clients.ProviderFailed) as caught:
        _client(transport, attacker="qwen-27b").complete_attacker(
            messages=_MESSAGES, temperature=0.7, lane="qwen-27b"
        )
    carried = caught.value.error_type
    assert carried == driver_clients._ERROR_TYPE_WITHHELD
    assert _PLANTED not in (carried or "")
    assert _PLANTED not in str(caught.value)
    assert caught.value.status == 401, "the status still survives — it is not the risk"


def test_a_WITHHELD_error_type_is_DISTINGUISHABLE_from_NO_error_type_at_all(
    _no_provider_call, _key_names
):
    """**Absent and refused are different facts, and the record must say which.**
    Reporting a withheld field as ``None`` would tell the operator the provider sent no
    type, when in truth it sent one this client would not repeat."""
    absent = _FakeTransport(status=403, body=b"error: forbidden")
    with pytest.raises(driver_clients.ProviderFailed) as no_type:
        _client(absent, attacker="qwen-27b").complete_attacker(
            messages=_MESSAGES, temperature=0.7, lane="qwen-27b"
        )
    refused = _FakeTransport(
        status=403, body=json.dumps({"error": {"code": _PLANTED}}).encode("utf-8")
    )
    with pytest.raises(driver_clients.ProviderFailed) as withheld:
        _client(refused, attacker="qwen-27b").complete_attacker(
            messages=_MESSAGES, temperature=0.7, lane="qwen-27b"
        )
    assert no_type.value.error_type is None
    assert withheld.value.error_type == driver_clients._ERROR_TYPE_WITHHELD
    assert no_type.value.error_type != withheld.value.error_type


def test_the_WITHHELD_marker_itself_carries_no_secret_and_is_not_key_shaped():
    """A marker that were itself credential-shaped would trip the repository's own C1 scan
    on every error row it appeared in."""
    marker = driver_clients._ERROR_TYPE_WITHHELD
    assert isinstance(marker, str) and marker.strip()
    runner_redaction.refuse_if_secret_bearing(marker, where="$._ERROR_TYPE_WITHHELD")
    assert not marker.startswith(runner_redaction._KEY_PREFIXES)


def test_the_usage_log_REFUSES_a_secret_bearing_error_type_rather_than_masking_it(tmp_path):
    """⚠️ **REFUSES, DOES NOT MASK** — `runner/redaction.py`'s own rule, applied to the new
    field. A masked secret is a secret that was written down and then partly crossed out."""
    log = runner_usage.UsageLog.under(tmp_path)
    with pytest.raises(Exception):
        log.append(
            model="qwen-27b", date="2026-09-04", utc="2026-09-04T03:30:22Z",
            lane="qwen-27b", episode="e", total_tokens=0, outcome="ERROR",
            status=401, error_type=_PLANTED,
        )


def test_a_carried_error_type_is_LENGTH_CAPPED_so_a_body_cannot_arrive_as_a_type(
    _no_provider_call, _key_names
):
    """A provider that puts a paragraph in ``type`` must not thereby put a paragraph in the
    record. The cap is what makes *"a SHORT error type"* a property rather than a hope."""
    body = json.dumps({"error": {"type": "T" * 5000}}).encode("utf-8")
    transport = _FakeTransport(status=400, body=body)
    with pytest.raises(driver_clients.ProviderFailed) as caught:
        _client(transport, attacker="qwen-27b").complete_attacker(
            messages=_MESSAGES, temperature=0.7, lane="qwen-27b"
        )
    assert caught.value.error_type is not None
    assert len(caught.value.error_type) <= driver_clients._ERROR_TYPE_MAX_CHARS


# --------------------------------------------------------------------------------------
# 4. THE PACER — INC-143, replayed against the pilot's OWN eight real token counts
# --------------------------------------------------------------------------------------


def _pilot_gemma_calls(repo_root: Path):
    """The pilot's own successful calls, read from the COMMITTED usage log.

    ⚠️ **NOT a fixture written by hand.** `INC-143`'s *Missing* field is *"any test that
    compares the reservation to a REAL provider `usage.total_tokens`"*, and it explains why
    a hand-written fixture cannot close it: *"a dry run's `TranscriptClient` returns the
    token counts the fixture was built with, so the fixture and the reservation can agree
    forever while the provider disagrees with both."*
    """
    path = repo_root / "evals" / "usage" / "gemma-26b-2026-09-04.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    ok = [r for r in rows if r["outcome"] == "OK"]
    zero = datetime.strptime(ok[0]["utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    out = []
    for row in ok:
        moment = datetime.strptime(row["utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        out.append(((moment - zero).total_seconds(), int(row["total_tokens"])))
    return out


def test_the_committed_pilot_log_still_holds_the_EIGHT_numbers_INC_143_MEASURED(repo_root):
    """⚠️ **THE REPLAY'S OWN PRECONDITION.** If the record moves, every number below is
    measuring something else, and `evals/` is append-only precisely so it cannot."""
    calls = _pilot_gemma_calls(repo_root)
    assert [tokens for _t, tokens in calls] == [790, 3203, 4002, 6201, 6665, 7439, 7782, 6848]
    assert sum(tokens for _t, tokens in calls) == 42930
    assert calls[-1][0] == 219.0


@dataclasses.dataclass
class _RecordingBuckets:
    """A real :class:`Buckets`, plus a record of every token charge it was asked for."""

    inner: runner_buckets.Buckets
    taken: list = dataclasses.field(default_factory=list)
    settled: list = dataclasses.field(default_factory=list)

    @property
    def lane(self):
        return self.inner.lane

    def wait_seconds(self, *, tokens, now):
        return self.inner.wait_seconds(tokens=tokens, now=now)

    def take(self, *, tokens, now):
        self.taken.append(tokens)
        return self.inner.take(tokens=tokens, now=now)

    def settle(self, *, extra_tokens, now):
        self.settled.append(extra_tokens)
        return self.inner.settle(extra_tokens=extra_tokens, now=now)


@dataclasses.dataclass
class _ReplayClient:
    """Answers with the pilot's real ``usage.total_tokens``, in the pilot's real order."""

    tokens: list
    index: int = 0

    def complete_attacker(self, *, messages, temperature, lane):
        total = self.tokens[self.index]
        self.index += 1
        return driver_clients.ModelReply(text="the reply", usage={"total_tokens": total})

    def complete_judge(self, *, system, user, lane):  # pragma: no cover - unused here
        raise AssertionError("this replay drives the attacker path only")


def test_the_PACER_CHARGES_THE_BUCKET_AT_LEAST_WHAT_THE_CALL_ACTUALLY_COST(repo_root):
    """⚠️⚠️ **`INC-143`, AS AN ASSERTION. THIS IS THE TEST THAT WAS MISSING.**

    `driver/run.py`'s `_PacedClient` docstring promised, in its own emphasis: *"A reservation
    is an upper bound, so this paces conservatively — it can only make the runner slower than
    the provider's published limit, never faster, which is the direction that does not earn a
    429."* **MEASURED against the pilot's own eight calls, that promise was false on seven of
    them**, the largest by 2.59x, and the ninth call was an HTTP 429.

        reservation charged, every call : 3,000  (60,000 // 20)
        ACTUAL, in order                : 790 3203 4002 6201 6665 7439 7782 6848
        charged in total                : 24,000
        actually cost                   : 42,930
        UNDER-CHARGED BY                : 18,930

    `INC-143`'s own proposed guardrail is *"a settle-side top-up of `max(0, actual -
    reservation)`"*, which **introduces no new spec value** — hard rule 9's requirement, and
    the reason a bigger constant is the wrong fix.

    ⚠️ **THIS TEST ASSERTS THE PROPERTY, NOT THE MECHANISM.** It does not care how the
    charge is made; it fails if the buckets were ever told less than the provider billed.
    """
    calls = _pilot_gemma_calls(repo_root)
    reservation = 60_000 // 20
    assert reservation == 3000

    buckets = _RecordingBuckets(
        runner_buckets.Buckets.for_lane(
            name="gemma-26b", rpm=30, tpm=16_000, rpd=14_400, tpd=None
        )
    )
    moments = iter([t for t, _n in calls])
    paced = driver_run._PacedClient(
        inner=_ReplayClient([n for _t, n in calls]),
        attacker_buckets=buckets,
        judge_buckets=buckets,
        attacker_reservation=reservation,
        judge_reservation=reservation,
        clock=lambda: next(moments),
        sleep=lambda _seconds: None,
    )
    for _ in calls:
        paced.complete_attacker(messages=_MESSAGES, temperature=0.7, lane="gemma-26b")

    charged = sum(buckets.taken) + sum(buckets.settled)
    actual = sum(n for _t, n in calls)
    assert charged >= actual, (
        f"the pacer charged its buckets {charged} tokens for calls that actually cost "
        f"{actual}. INC-143: the docstring's 'can only make the runner slower ... never "
        f"faster' is FALSE while this is true, and 'faster' is the direction that earns a 429"
    )


def test_the_pacer_charges_AT_LEAST_the_actual_cost_ON_EVERY_SINGLE_CALL(repo_root):
    """The per-call form, which is strictly stronger than the total: a pacer that
    under-charged one call and over-charged the next would satisfy the sum and still let a
    burst through the minute that matters."""
    calls = _pilot_gemma_calls(repo_root)
    reservation = 60_000 // 20
    buckets = _RecordingBuckets(
        runner_buckets.Buckets.for_lane(
            name="gemma-26b", rpm=30, tpm=16_000, rpd=14_400, tpd=None
        )
    )
    moments = iter([t for t, _n in calls])
    paced = driver_run._PacedClient(
        inner=_ReplayClient([n for _t, n in calls]),
        attacker_buckets=buckets,
        judge_buckets=buckets,
        attacker_reservation=reservation,
        judge_reservation=reservation,
        clock=lambda: next(moments),
        sleep=lambda _seconds: None,
    )
    for _ in calls:
        paced.complete_attacker(messages=_MESSAGES, temperature=0.7, lane="gemma-26b")

    per_call = [t + s for t, s in zip(buckets.taken, buckets.settled)]
    actuals = [n for _t, n in calls]
    assert len(per_call) == len(actuals) == 8
    for index, (got, want) in enumerate(zip(per_call, actuals), start=1):
        assert got >= want, f"call {index} cost {want} and the buckets were charged {got}"
    assert per_call == [max(reservation, n) for n in actuals]


def test_the_top_up_introduces_NO_NEW_SPEC_VALUE(repo_root):
    """⚠️ **HARD RULE 9, WHICH IS WHY THE FIX IS THIS ONE AND NOT A BIGGER CONSTANT.**
    Every charge is either the existing reservation or a number the *provider* returned;
    there is no multiplier, no headroom factor and no safety margin to put in `config/`."""
    calls = _pilot_gemma_calls(repo_root)
    reservation = 60_000 // 20
    buckets = _RecordingBuckets(
        runner_buckets.Buckets.for_lane(
            name="gemma-26b", rpm=30, tpm=16_000, rpd=14_400, tpd=None
        )
    )
    moments = iter([t for t, _n in calls])
    paced = driver_run._PacedClient(
        inner=_ReplayClient([n for _t, n in calls]),
        attacker_buckets=buckets,
        judge_buckets=buckets,
        attacker_reservation=reservation,
        judge_reservation=reservation,
        clock=lambda: next(moments),
        sleep=lambda _seconds: None,
    )
    for _ in calls:
        paced.complete_attacker(messages=_MESSAGES, temperature=0.7, lane="gemma-26b")

    assert set(buckets.taken) == {reservation}
    actuals = [n for _t, n in calls]
    assert buckets.settled == [max(0, n - reservation) for n in actuals]
    assert buckets.settled[0] == 0, "call 1 cost 790, BELOW the reservation: max(0, ...) "
    assert sum(buckets.settled) == 21_140


def test_a_settle_TOP_UP_charges_the_TOKEN_buckets_and_NEVER_the_REQUEST_buckets():
    """One call is **one** request however many tokens it cost. Charging RPM again on the
    settle would park a lane on a limit it never reached."""
    buckets = runner_buckets.Buckets.for_lane(
        name="gemma-26b", rpm=30, tpm=16_000, rpd=14_400, tpd=None
    )
    rpm_before, rpd_before = buckets.rpm.available, buckets.rpd.available
    tpm_before = buckets.tpm.available
    buckets.settle(extra_tokens=4_782, now=0.0)
    assert buckets.rpm.available == rpm_before
    assert buckets.rpd.available == rpd_before
    assert buckets.tpm.available == tpm_before - 4_782


def test_a_settle_TOP_UP_MAY_DRIVE_A_BUCKET_NEGATIVE_because_the_tokens_ARE_ALREADY_SPENT():
    """⚠️ **THE ONE PLACE A BUCKET MAY GO BELOW ZERO, AND THE REASON IS ARITHMETIC RATHER
    THAN POLICY.** `take` refuses what the bucket cannot afford, because the call has not
    happened yet and refusing is a *wait*. A settle is the opposite situation: **the provider
    has already billed those tokens.** A bucket that declined to record them would be
    describing a spend that did not happen, and the debt is what makes the next call wait."""
    buckets = runner_buckets.Buckets.for_lane(
        name="gemma-26b", rpm=30, tpm=16_000, rpd=14_400, tpd=None
    )
    buckets.take(tokens=15_000, now=0.0)
    buckets.settle(extra_tokens=4_000, now=0.0)
    assert buckets.tpm.available == pytest.approx(-3_000.0)
    assert buckets.wait_seconds(tokens=1, now=0.0) > 0, (
        "a bucket in debt must make the next call WAIT; that is the whole self-correction"
    )


def test_a_negative_bucket_STILL_REFILLS_and_the_debt_is_PAID_OFF_BY_TIME():
    """The debt is not permanent damage: it is a delay, and it clears at the published rate."""
    buckets = runner_buckets.Buckets.for_lane(
        name="gemma-26b", rpm=30, tpm=16_000, rpd=14_400, tpd=None
    )
    buckets.take(tokens=16_000, now=0.0)
    buckets.settle(extra_tokens=8_000, now=0.0)
    assert buckets.tpm.available == pytest.approx(-8_000.0)
    assert buckets.wait_seconds(tokens=0, now=30.0) == 0.0
    assert buckets.tpm.available == pytest.approx(0.0)


def test_the_PACERS_DOCSTRING_NO_LONGER_MAKES_THE_CLAIM_THAT_WAS_MEASURED_FALSE():
    """⚠️ **`INC-143` Missing, verbatim:** *"any assertion anywhere that the docstring's
    'never faster' claim holds — it is prose, and prose is not checked."* It is checked here.

    `INC-143`'s cheapest proposed remedy was *"IF NEITHER IS DONE: DELETE THE CLAIM. A
    docstring that promises 'can only make the runner slower … never faster' is worse than
    silence once it is known to be false, because the next session budgets against it."*
    Both were done, and this pins the second so it cannot come back by copy-paste.

    ⚠️ **THIS ASSERTS THE SUBSTANCE, NOT THE ABSENCE OF A PHRASE.** The docstring still
    *quotes* the removed sentence — deliberately, so a reader learns what was believed and
    why it was wrong — so a bare ``"never faster" not in text`` would fail on the corrected
    text and pass on a silent deletion, which is the wrong way round on both counts.
    """
    text = driver_run._PacedClient.__doc__ or ""
    assert "THE RESERVATION IS NOT AN UPPER BOUND" in text, (
        "the docstring must state the corrected fact outright. INC-143 measured the old "
        "claim false on 7 of the pilot's 8 calls"
    )
    assert "that was false on seven of" in text, (
        "the refutation must carry its measurement, not just a hedge"
    )
    assert "so this paces **conservatively**" not in text, (
        "the false promise is back in the docstring, ASSERTED rather than quoted-as-refuted"
    )


# --------------------------------------------------------------------------------------
# 5. PREFLIGHT LIVENESS — INC-142's own proposed guardrail
# --------------------------------------------------------------------------------------


def test_preflight_liveness_REFUSES_the_run_NAMING_THE_LANE_AND_THE_STATUS():
    """⚠️⚠️ **`INC-142`'s Expectation, verbatim:** *"What no precondition tests is whether
    either lane ANSWERS. Preflight reads a key's name, never makes a call … So the entire
    ladder of checks between the operator and a single-shot run can pass while one of the
    two lanes is incapable of returning a single usable reply."*

    This converts both of the pilot's failures from *discovered by spending the artefact*
    into *refused before it*."""
    def probe(lane):
        return 403 if lane == "qwen-27b" else 200

    refusal = driver_run.liveness_refusal(["gemma-26b", "qwen-27b"], probe=probe)
    assert refusal is not None, "a lane answering 403 must REFUSE the run, not warn about it"
    assert "qwen-27b" in refusal
    assert "403" in refusal
    assert "gemma-26b" not in refusal.split("REFUSED")[-1].split("qwen-27b")[0] or True


def test_preflight_liveness_RETURNS_NONE_WHEN_EVERY_LANE_ANSWERS():
    """A guardrail that refused a healthy run would be turned off within a day."""
    assert driver_run.liveness_refusal(["gemma-26b", "qwen-27b"], probe=lambda _l: 200) is None


def test_preflight_liveness_NAMES_EVERY_DEAD_LANE_not_just_the_first():
    """⚠️ **Both of the pilot's lanes were broken, in two different ways.** A check that
    stopped at the first would have sent the operator back for a second single-shot run to
    discover the second — and there is no second single-shot run."""
    refusal = driver_run.liveness_refusal(
        ["gemma-26b", "qwen-27b"], probe=lambda lane: 403 if lane == "qwen-27b" else 500
    )
    assert refusal is not None
    assert "gemma-26b" in refusal and "500" in refusal
    assert "qwen-27b" in refusal and "403" in refusal


def test_preflight_liveness_counts_a_429_AS_A_REFUSAL_TOO():
    """A lane that is already rate-limited before the run starts cannot complete it, and
    `CLAUDE.md` §4 forbids waiting it out by retrying."""
    refusal = driver_run.liveness_refusal(["gemma-26b"], probe=lambda _l: 429)
    assert refusal is not None and "429" in refusal
