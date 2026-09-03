"""**THE INJECTED MODEL CLIENT — AND THE DRY-RUN CLIENT THAT MAKES NO NETWORK CALL.**

⚠️⚠️ **THIS PACKAGE IMPORTS NO MODEL CLIENT AND NO NETWORK LIBRARY, AND THE ASSERTION IS
MADE TWO WAYS.** ``tests/test_c12_driver.py`` walks the driver's **transitive first-party
imports** with :mod:`ast` *and* scans every module's **raw source text** for the vocabulary
of dynamic reach. **The second half is not belt-and-braces:** `INCIDENTS.md` **INC-51**
measured that ``__import__(…)``, ``importlib.import_module(…)`` and ``getattr(pkg, "name")``
walk straight past an AST import walk — a call expression is not an ``ast.Import`` node —
and made a ``gates/`` module execute a ``scorer/`` predicate while `check_roles` **D1, D2
and D3 all reported PASS**. An AST walk cannot see a dynamic reach; a text scan cannot see
semantics; **neither is the guarantee alone.**

The consequence is the one `PROCESS.md` §8 asks for: **a build session cannot spend a
lane's quota by accident**, because there is nothing in this package that could open a
socket. The client is a **parameter**, typed as a two-method Protocol, and the driver never
learns what is behind it.

--------------------------------------------------------------------------------------
⚠️ THE CLIENT RETURNS THE PROVIDER'S OWN `usage` BLOCK, AND THAT IS WHY IT IS A NEW PROTOCOL
--------------------------------------------------------------------------------------

:class:`whetstone_gate.attacker.loop.ModelClient` returns **text alone**, which is right for
C6 — the attacker loop has no business knowing what a call cost. But hard rule 12's
accounting is *"tokens are taken from the API's OWN `usage` field, NEVER estimated"* (golden
8), so the driver needs the block itself. :class:`MeteredModelClient` returns
:class:`ModelReply`, which carries the text **and** the raw ``usage`` mapping, and
:mod:`whetstone_gate.driver.episode` adapts it down to C6's narrower protocol at the
boundary.

⚠️ **THE ADAPTER IS THE ONLY PLACE THE TWO MEET, AND IT DOES NOT ESTIMATE.**
:func:`whetstone_gate.runner.budget.usage_total_tokens` is what reads the block, it reads
``total_tokens`` **and nothing else**, and a reply whose usage block lacks it is a
**refusal** — never a reconstruction from ``prompt_tokens + completion_tokens``, because
providers differ on whether the total includes reasoning or cached-read tokens.

--------------------------------------------------------------------------------------
⚠️ THE DRY-RUN CLIENT: DETERMINISTIC, OFFLINE, AND HONEST ABOUT WHAT IT IS NOT
--------------------------------------------------------------------------------------

:class:`TranscriptClient` replays a **caller-supplied list of replies**, in order, with a
**caller-supplied** token count on each. It is how the operator rehearses the whole pilot —
20 episodes, ledgers, checkpoints, resume, the token accounting — **without a provider**.

**What it is:** a deterministic stand-in that exercises every line of the driver except the
provider call itself.
**What it is NOT, said plainly** (`PROCESS.md` §9: *"every evidence pack states what it is
NOT"*): it is **not a model**, its token counts are **the caller's numbers and not a
provider's**, and a dry run therefore measures **the harness**, never
`CONTEXT.md` §13.4's tokens/episode. ⚠️ **A dry run may never select the N branch**, and
:mod:`whetstone_gate.driver.pilot` refuses to hand a dry run's figures to
:func:`whetstone_gate.runner.n_rule.select_n` for exactly that reason.

--------------------------------------------------------------------------------------
⚠️⚠️ THE PROVIDER BOUNDARY — ADDED 2026-09-03 BY `Q-150`'s RULING, AND IT IS THE ONE
EXCEPTION TO EVERYTHING THE THREE PARAGRAPHS ABOVE SAY
--------------------------------------------------------------------------------------

⚠️ **THE SENTENCE "THIS PACKAGE IMPORTS NO MODEL CLIENT AND NO NETWORK LIBRARY" IS NO
LONGER TRUE OF THIS FILE, AND IT IS STILL TRUE OF EVERY OTHER FILE IN THIS PACKAGE.**
Saying which is the point. `QUESTIONS.md` **Q-150**, RULED 2026-09-03, option 1:

    A real ``MeteredModelClient`` is written into ``src/whetstone_gate/driver/clients.py``,
    and ``driver/__main__.py``'s ``--spend-real-tokens`` branch constructs it instead of
    refusing. … ⚠️ IT SHIPS UNREVIEWED AND DISCLOSED, exactly as C8, C9, C10, C11 and C14
    do, and C19's README names it.

:class:`MeteredProviderClient` is that client. **It is the ONLY module in this package that
may name a network library or read the environment**, and both halves of the original
guarantee are kept for every *other* module — `tests/test_c12_driver.py` still walks the
transitive first-party imports **and** still scans the raw source text, with **this one file
named as the exception and nothing else widened**. Two tests were **added** rather than
loosened: one asserts this file reaches ``urllib.request``/``urllib.error`` and **nothing
else** in the forbidden set, one asserts it touches ``os.environ`` and never ``os`` by any
other route. **The whole of `_DYNAMIC_REACH` still applies to this file.**

⚠️ **NO RETRY LOGIC OF ANY KIND LIVES HERE, AND THAT IS A REQUIREMENT RATHER THAN AN
OMISSION.** Hard rule 12 and `CLAUDE.md` §4: *"A 429 means the window is already spent: STOP
and report — never retry into another lane."* A 429 raises :class:`RateLimited` at the
provider boundary and the **runner** decides what that means; a client that quietly retried
would defeat the one rule that keeps a spent window visible, and it would do so invisibly.
:class:`RateLimited` deliberately carries no field naming a lane to move to.

⚠️ **THE PROVIDER'S OWN `usage` BLOCK IS CARRIED VERBATIM, AND `total_tokens` IS LIFTED FROM
THE PROVIDER'S OWN REPORTED TOTAL — NEVER SUMMED FROM PARTS.** Google reports
``usageMetadata.totalTokenCount``; Groq reports ``usage.total_tokens``. Both are *the
provider's own total*, and neither is reconstructed: golden 8's rule is that the accumulator
reads ``total_tokens`` *"and nothing else"*, and Google's own definition of
``totalTokenCount`` is *"prompt + thoughts + response candidates"* — a **third** component
that ``promptTokenCount + candidatesTokenCount`` silently drops. A parts-sum would understate
every reasoning reply, against a lane whose TPM is 16,000.
⚠️ **A REPLY WITH NO USAGE BLOCK IS A REFUSAL, NOT A ZERO** — a zero would spend a lane's
quota and report that it had not.

⚠️ **THE KEY VALUE IS READ HERE AND NOWHERE ELSE, AND IT IS NEVER PRINTED.**
:mod:`whetstone_gate.runner.keys` deliberately has **no code path that returns a value** —
its only public function returns a boolean — so a live call has to read the environment
somewhere, and *somewhere* is this one file, at the boundary, on the line before the header
is built. The **name** is derived from `config/lanes.yaml`'s ``provider`` field through
:func:`whetstone_gate.runner.keys.env_var_for_provider`, so no key name is spelled in this
source either. ⚠️ **Google's key goes in the ``x-goog-api-key`` HEADER and never in a
``?key=`` query string**, and that is a safety property rather than a style choice:
:class:`urllib.error.HTTPError` carries the request URL on ``.url``/``.filename`` and prints
it in its own ``repr``, so a key in the query string would leak into every logged traceback.
:func:`whetstone_gate.runner.redaction.refuse_if_secret_bearing` is wired across every reply
before it is returned — **it refuses, it does not mask** — so a provider that echoed a
credential back stops the run instead of writing it into a ledger.

⚠️ **ENDPOINTS ARE LITERALS HERE AND HARD RULE 9 WAS CHECKED BEFORE THEY WERE WRITTEN.**
`config/lanes.yaml` carries ``provider`` and ``api_model_id`` — **the model ids are read from
it and are never literals here** — but it carries **no** ``base_url``, ``endpoint`` or
``timeout`` field, it is a pre-registration artefact, and `PROTOCOL.md` pins `config/` to
**exactly two files**. An endpoint is a *provider fact*, not one of `CONTEXT.md` §8.6's
spec-specified values, and §8.6's constants table — *the tripwire's authoritative list* — has
no row for one. This is the same reasoning `tasks.py`'s ``EVAL_RUN_DIR`` is written under.
**It is recorded as a Class B deviation and raised at `QUESTIONS.md` `Q-163` rather than
decided quietly.**

⚠️ **WHAT THIS CLIENT CANNOT DO, SAID HERE RATHER THAN DISCOVERED AT RUN TIME**
(`PROCESS.md` §9: *"every evidence pack states what it is NOT"*): **it cannot work out which
lane a call belongs to, and it does not try.** ``lane`` is a **required, undefaulted**
argument on both protocol methods — `QUESTIONS.md` **Q-161**, ruled 2026-09-03, option 1 —
and this client is a **lookup**, not a router: a name outside the map it was built for is a
refusal, never a fallback. Until that ruling the two methods distinguished *role* and never
*lane*, so a matrix with **two attacker cells on two providers** — exactly the pilot's —
could not be routed at all, and `driver/__main__.py` refused by name. ⚠️ **The two rejected
sources of the lane are still rejected:** dispatch order, and a walk up the caller's frame
(verified to work, **not built** — `INCIDENTS.md` **INC-51**'s species).
⚠️ **AND IT HAS NEVER BEEN RUN AGAINST EITHER PROVIDER.** No session may call these
endpoints, so every request and reply shape below is built from the published REST references
and exercised against a **fake transport**, never against a provider. `QUESTIONS.md` `Q-162`.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Protocol, Sequence

from whetstone_gate.runner.keys import env_var_for_provider
from whetstone_gate.runner.lanes import load_lanes
from whetstone_gate.runner.redaction import refuse_if_secret_bearing


class DriverClientError(RuntimeError):
    """The injected client was asked for something it cannot honestly supply."""


class RateLimited(RuntimeError):
    """The provider answered **429**. The window is already spent.

    ⚠️ **RAISED, NOT RETURNED, AND IT CARRIES NO DESTINATION.** `PROCESS.md` §8 and
    `CLAUDE.md` §4: *"A 429 means the window is already spent: STOP and report — never retry
    into another lane."* There is no field on this exception naming a lane to move to, so
    *"never retry into another lane"* is a property of the type rather than a rule a caller
    has to remember — the same shape
    :meth:`whetstone_gate.runner.budget.LaneBudget.record_429` gives it one layer down.
    """


class ProviderFailed(RuntimeError):
    """The provider returned an error that is **not** a 429.

    Counted under :data:`whetstone_gate.runner.episodes.PROVIDER_ERROR`, never swallowed:
    hard rule 11 counts *"retries, fallbacks, skipped cases, or missing traces"* alike.
    """


@dataclass(frozen=True)
class ModelReply:
    """One provider reply: the text, and **the provider's own usage block**.

    ``usage`` is passed through **verbatim**. This class does not read it, does not add its
    parts together and does not fill anything in — golden 8's rule is that the accumulator
    reads ``total_tokens`` *"and nothing else"*, and a wrapper that helpfully synthesised a
    total would put an estimate where a billed figure belongs.
    """

    text: str
    usage: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise DriverClientError(
                f"a model reply's text must be a string; got {type(self.text).__name__}"
            )
        if not isinstance(self.usage, Mapping):
            raise DriverClientError(
                "a model reply must carry the provider's own usage block as a mapping. "
                "Hard rule 12 and golden 8: tokens are taken from the API's OWN usage "
                "field, NEVER estimated"
            )


def _required_lane(lane: str, *, role: str) -> str:
    """⚠️ **Q-161. A LANE MUST BE A NON-EMPTY NAME, AND AN EMPTY ONE IS A REFUSAL.**

    Python's keyword-only, undefaulted parameter already makes *omitting* the lane a
    ``TypeError`` at the call site — that is the ruling's *"required argument with no
    default"*, enforced by the language rather than by a check. **This closes the one hole the
    language leaves open:** a caller that passes ``""`` or ``None`` has satisfied the
    signature and supplied no routing information at all, and on the provider client that is
    a `KeyError` deep inside a lane map rather than a named refusal here.

    It refuses rather than substituting anything, because every substitution available —
    a first lane, a default lane, the previously used lane — is a **guess about which
    provider the traffic belongs to**, which is the whole of what `Q-161` exists to prevent.
    """
    if not isinstance(lane, str) or not lane:
        raise DriverClientError(
            f"a {role} call arrived with lane={lane!r}. THE LANE IS REQUIRED AND IS NEVER "
            f"SUBSTITUTED: QUESTIONS.md Q-161 ruled it onto both protocol methods precisely "
            f"so that one client serving two providers cannot misroute, and every available "
            f"substitute (a first lane, a default lane, the last lane used) is a guess about "
            f"which provider this traffic belongs to. A misroute is silent until the "
            f"published per-lane token figures are read, and CLAUDE.md S4's 429 rule would "
            f"stop the wrong lane"
        )
    return lane


class MeteredModelClient(Protocol):
    """The one thing the driver needs from a provider. **A protocol, never an import.**

    Two methods, because the attacker and the gate judge are called with different shapes
    and `CONTEXT.md` §13.3.2 puts them on their own lanes with their own budgets:

      * :meth:`complete_attacker` — C6's message list, at `config/`'s temperature.
      * :meth:`complete_judge` — C9's ``(system, user)`` pair.

    A caller supplies anything with this shape: the operator's real provider client in a
    scored run, :class:`TranscriptClient` in a dry run. **This package never learns which.**

    ⚠️⚠️ **``lane`` IS ON BOTH METHODS, IT IS REQUIRED, AND IT HAS NO DEFAULT.**
    `QUESTIONS.md` **Q-161**, RULED 2026-09-03, **option 1**. Before the ruling these two
    methods distinguished the **role** and nothing else, so one client serving a matrix whose
    attacker cells sit on **two** providers could not know which model a given call was for —
    and `driver/pilot.py` gives both cells the **same** seed block, so the messages are
    byte-identical and content-based inference is impossible **in principle**, not merely
    unwise.

    ⚠️ **A DEFAULT WOULD BE WORSE THAN THE OLD REFUSAL.** A defaulted lane sends one
    provider's traffic to another silently, and `CLAUDE.md` §4's 429 rule would then stop the
    **wrong** lane — the failure would be invisible until the published per-lane token figures
    were read, which is after the single-shot window is spent. So the argument is required on
    the protocol and on **every** implementation of it.

    ⚠️ **THE LANE IS PASSED, NEVER DERIVED.** It comes from
    :class:`whetstone_gate.driver.episode._MeteredCall`'s ``lane`` — the authoritative
    per-role value, built in ``run.py``'s dispatch loop from ``request.matrix.lane_for(key)``.
    Recovering it from dispatch order, or by walking up to a caller's frame, was found to work
    and was **rejected**: `INCIDENTS.md` **INC-51**'s exact species.
    """

    def complete_attacker(
        self, *, messages: tuple[dict[str, str], ...], temperature: float, lane: str
    ) -> ModelReply:
        ...

    def complete_judge(self, *, system: str, user: str, lane: str) -> ModelReply:
        ...


@dataclass
class TranscriptClient:
    """A deterministic offline client. **It opens nothing and it computes nothing.**

    ``attacker_replies`` and ``judge_replies`` are consumed in order. Each is a
    ``(text, total_tokens)`` pair, and the ``total_tokens`` is written into a ``usage`` block
    so that the accounting path under test is **exactly** the one a provider would drive —
    :func:`whetstone_gate.runner.budget.usage_total_tokens` reading ``total_tokens`` off a
    mapping. A dry run that fed the accumulator a bare integer would leave the one function
    hard rule 12 depends on untested.

    ⚠️ **EXHAUSTION IS A REFUSAL, NEVER A REPEAT OF THE LAST REPLY.** A transcript that runs
    out mid-episode is a transcript that does not describe the episode it was handed to, and
    silently looping would make a dry run of 20 episodes prove something about 1.

    ``rate_limit_at`` makes the client raise :class:`RateLimited` on the *n*-th attacker
    call, which is how golden 8 fixture D's shape is driven end to end through the real
    wiring rather than against the accumulator alone. ``None`` means it never fires.
    """

    attacker_replies: Sequence[tuple[str, int]]
    judge_replies: Sequence[tuple[str, int]] = field(default_factory=tuple)
    rate_limit_at: int | None = None

    attacker_calls: int = 0
    judge_calls: int = 0

    # ⚠️ Q-161. THE LANES THE DRIVER ACTUALLY ROUTED TO, IN ORDER, RECORDED RATHER THAN
    # INTERPRETED. A transcript that behaved differently by lane would be a router, and this
    # is deliberately not one — but a dry run that could not SHOW the lane arriving would
    # leave the threading untested on the only path a session may execute.
    attacker_lanes: list[str] = field(default_factory=list)
    judge_lanes: list[str] = field(default_factory=list)

    def complete_attacker(
        self, *, messages: tuple[dict[str, str], ...], temperature: float, lane: str
    ) -> ModelReply:
        """The next attacker reply. ``messages``, ``temperature`` and ``lane`` are **accepted
        and recorded, never interpreted** — a transcript that behaved differently by prompt
        would be a model, and this is deliberately not one.

        ⚠️ ``lane`` is **required and undefaulted here too**, and that is not ceremony: a dry
        run whose client tolerated a missing lane would prove the wiring on a shape the scored
        run does not use. `QUESTIONS.md` **Q-161**."""
        self.attacker_calls += 1
        self.attacker_lanes.append(_required_lane(lane, role="attacker"))
        if self.rate_limit_at is not None and self.attacker_calls == self.rate_limit_at:
            raise RateLimited(
                f"transcript client: simulated 429 on attacker call {self.attacker_calls}"
            )
        return self._next(self.attacker_replies, self.attacker_calls, "attacker")

    def complete_judge(self, *, system: str, user: str, lane: str) -> ModelReply:
        """The next judge reply. Same contract, same refusal on exhaustion."""
        self.judge_calls += 1
        self.judge_lanes.append(_required_lane(lane, role="judge"))
        return self._next(self.judge_replies, self.judge_calls, "judge")

    def _next(
        self, replies: Sequence[tuple[str, int]], position: int, role: str
    ) -> ModelReply:
        if position > len(replies):
            raise DriverClientError(
                f"the transcript has {len(replies)} {role} reply/replies and call "
                f"{position} was asked for. A transcript is exhausted, not repeated: "
                f"looping the last reply would make a 20-episode dry run prove something "
                f"about one episode"
            )
        text, total = replies[position - 1]
        return ModelReply(text=text, usage={"total_tokens": total})


def cycle(replies: Iterable[tuple[str, int]], times: int) -> tuple[tuple[str, int], ...]:
    """``replies`` repeated ``times`` over, as a flat tuple. **A test and rehearsal helper.**

    Written here rather than at each call site so that a rehearsal transcript for a whole
    pilot is one expression, and so that :class:`TranscriptClient`'s refusal on exhaustion
    stays a real refusal rather than something a caller works around with a generator.
    """
    if times < 0:
        raise DriverClientError(f"cannot repeat a transcript {times} times")
    materialised = tuple(replies)
    return tuple(reply for _ in range(times) for reply in materialised)


# ======================================================================================
# ⚠️⚠️ THE PROVIDER BOUNDARY. Everything below this line may touch the network; nothing
# above it does, and no other module in this package does. See the module docstring.
# ======================================================================================


#: The two providers' HTTPS entry points. ⚠️ **LITERALS, AND HARD RULE 9 WAS CHECKED**:
#: `config/lanes.yaml` carries ``provider`` and ``api_model_id`` but **no** endpoint field,
#: it is a pre-registration artefact, and `PROTOCOL.md` pins `config/` to exactly two files.
#: An endpoint is a provider fact rather than one of `CONTEXT.md` §8.6's spec-specified
#: values, and §8.6's table — the tripwire's authoritative list — carries no row for one.
#: Same reasoning as ``tasks.py:EVAL_RUN_DIR``. Recorded as Class B; raised at `Q-163`.
#:
#: ⚠️ Google's method separator is a literal ``:`` and the ``models/`` prefix is part of
#: ``api_model_id`` itself, so the URL is a plain concatenation and is **never** passed
#: through a quoter: ``%3A`` returns 404, and so does a doubled ``models/models/``.
_GOOGLE_BASE = "https://generativelanguage.googleapis.com/v1beta"
_GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

#: The providers this client speaks. Keyed by `config/lanes.yaml`'s own ``provider`` string.
_PROVIDERS = ("google", "groq")

#: Seconds to wait on one provider call. ⚠️ **Not a spec value and not in §8.6's table** —
#: it is a transport detail with no bearing on any published number, written here for the
#: same reason as the endpoints above. It exists so a hung socket cannot stall a lane
#: forever; it is deliberately generous, because a timeout that fired early would book a
#: completed call as a failure and hard rule 11 counts every dropped episode.
_TIMEOUT_SECONDS = 180

#: What the two providers call each turn. Google's ``contents[].role`` accepts **exactly**
#: ``user`` and ``model``; Groq's ``messages[].role`` accepts OpenAI's
#: ``system``/``user``/``assistant``. ⚠️ **An unmapped role is a REFUSAL, never a coercion**
#: — silently rewriting a role the caller did not ask for is how an attacker prompt becomes
#: a different prompt on one lane than on another, and `CONTEXT.md` §10.1 forbids exactly
#: that: *"no DIFFERENTIAL information across arms"*.
#:
#: ⚠️⚠️ **``tool`` MAPS TO ``user`` ON BOTH, AND THE MAPPING IS IDENTICAL ON BOTH.**
#: `QUESTIONS.md` **Q-171**, RULED 2026-09-04; `INCIDENTS.md` **INC-129**. C6 emits every tool
#: result as ``ContextPart(Origin.WORLD, "tool", …)`` (`attacker/context.py:505`), so **every
#: turn after the first** carries one and, before the ruling, neither map had the key — no
#: episode could reach turn 2 on **either** provider.
#:
#: ⚠️ **THE REASON IS THE PROTOCOL'S SHAPE, NOT CONVENIENCE.** This attacker uses **no
#: native tool-calling**: C6's protocol is text-only, so a tool result here is *text the harness
#: hands the attacker* — which is what a ``user`` message is. There is **no ``tool_call_id`` to
#: mint**, because no tool call was ever made on the wire; Groq's OpenAI-compatible ``tool`` role
#: **requires** one, so the faithful-looking option is the one that 400s. And Google's
#: ``contents[].role`` has **no tool role at all**. Any other choice therefore forces a
#: per-provider difference — §10.1's own prohibition, rejected on the record at `Q-171`.
#:
#: ⚠️ **THE REFUSAL BELOW IS UNCHANGED FOR EVERY OTHER ROLE**, and that is the half of
#: this that must not be weakened: an unknown role still raises, naming the role and the legal
#: values. The defect `INC-129` records was the **missing mapping**, never the refusal.
_GOOGLE_ROLE = {"system": "user", "user": "user", "assistant": "model", "tool": "user"}
_GROQ_ROLE = {"system": "system", "user": "user", "assistant": "assistant", "tool": "user"}


@dataclass(frozen=True)
class HttpResponse:
    """One HTTP answer, reduced to the only two things this module reads.

    ⚠️ **A NON-2xx IS A VALUE HERE, NOT AN EXCEPTION**, so that every status-to-outcome
    decision below is a pure function of ``(status, body)`` and can be driven by a fake in
    a test with no exception plumbing at all. Hard rule 8's shape: the I/O is
    :func:`_http_post` and nothing else in this package.
    """

    status: int
    body: bytes


#: The transport a client calls. ⚠️ **THE ONE SEAM** — tests pass a fake and the suite makes
#: **zero** provider calls; production passes :func:`_http_post`, and nothing else does.
Transport = Callable[[str, bytes, Mapping[str, str]], HttpResponse]


def _http_post(url: str, body: bytes, headers: Mapping[str, str]) -> HttpResponse:
    """POST ``body`` and return the status and bytes. ⚠️ **THE ONLY I/O IN THIS PACKAGE.**

    ⚠️ **NO RETRY, NO BACKOFF, NO FALLBACK.** A 429 comes back as a *status*, and
    :meth:`MeteredProviderClient._reply` turns it into :class:`RateLimited`. Hard rule 12:
    *"A 429 means the window is already spent: STOP and report — never retry into another
    lane."* The runner owns re-queueing within a lane; a client that retried here would
    defeat that rule **silently**, which is the worst way to defeat it.

    ⚠️ ``urllib.request.urlopen`` **raises** on any status outside 200-299, so the
    :class:`urllib.error.HTTPError` branch is the normal path for a 429 and for every
    provider error, not an exceptional one. The error body is read **once**, into a
    variable — a second read returns ``b""``.
    """
    request = urllib.request.Request(
        url, data=body, headers=dict(headers), method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
            return HttpResponse(status=int(response.status), body=response.read())
    except urllib.error.HTTPError as failure:
        return HttpResponse(status=int(failure.code), body=failure.read())
    except urllib.error.URLError as failure:
        # ⚠️ The reason is included and the URL is NOT: a URL can carry a query string, and
        # this project's one hard promise about keys is that no value reaches a log.
        raise ProviderFailed(
            f"the provider could not be reached: {failure.reason}. This is counted under "
            f"PROVIDER_ERROR and never swallowed (hard rule 11)"
        ) from None


def _decode(response: HttpResponse, *, lane: str) -> Mapping[str, Any]:
    """The JSON body, or a refusal naming the lane. **A malformed body is never guessed at.**"""
    try:
        payload = json.loads(response.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as broken:
        raise ProviderFailed(
            f"lane {lane!r} returned HTTP {response.status} with a body this client could "
            f"not parse as JSON ({broken.__class__.__name__}). The body is NOT reproduced "
            f"here: a provider error can quote the credential it rejected, and CLAUDE.md S4 "
            f"is that secrets never reach a log. Counted under PROVIDER_ERROR"
        ) from None
    if not isinstance(payload, Mapping):
        raise ProviderFailed(
            f"lane {lane!r} returned HTTP {response.status} whose JSON body is a "
            f"{type(payload).__name__}, not an object. Counted under PROVIDER_ERROR"
        )
    return payload


def _google_body(
    messages: tuple[dict[str, str], ...], temperature: float
) -> dict[str, Any]:
    """C6's message list as Google's ``generateContent`` body. **A pure function.**

    ⚠️ **EVERY PART GOES INTO ``contents`` AND NOTHING GOES INTO ``systemInstruction``.**
    Google's ``contents[].role`` has exactly two legal values, ``user`` and ``model``, and
    ``system`` is not one of them; the documented home for system text is the top-level
    ``systemInstruction``. This client does **not** use it, deliberately: whether a given
    Gemma build accepts ``systemInstruction`` is a per-model capability **no session may
    verify**, because no session may call the endpoint (`PROCESS.md` §8), and a single-shot
    run is the wrong place to discover a 400. Folding system text in as a ``user`` part is
    accepted by every model and loses nothing — C6's own
    :meth:`AssembledContext.full_text` joins its parts with a newline in exactly this way.

    ⚠️ **CONSECUTIVE SAME-ROLE PARTS ARE MERGED, NOT SEPARATED BY AN INVENTED TURN.**
    Google expects alternation. Merging is lossless; synthesising a filler turn would put
    text in front of the model that no arm authored.
    """
    contents: list[dict[str, Any]] = []
    for message in messages:
        role = _GOOGLE_ROLE.get(message["role"])
        if role is None:
            raise DriverClientError(
                f"role {message['role']!r} has no Google equivalent. The legal values are "
                f"{sorted(set(_GOOGLE_ROLE))}. This is a refusal rather than a coercion: "
                f"silently rewriting a role sends a different prompt on one lane than on "
                f"another, and CONTEXT.md S10.1 forbids differential information across arms"
            )
        if contents and contents[-1]["role"] == role:
            contents[-1]["parts"][0]["text"] += "\n" + message["content"]
            continue
        contents.append({"role": role, "parts": [{"text": message["content"]}]})
    # ⚠️ maxOutputTokens is DELIBERATELY ABSENT. It is not in config/ and not in S8.6's
    # table, so choosing one here would be hard rule 9's "hardcoded spec value" — and a cap
    # this file invented would truncate replies and move a published number.
    return {"contents": contents, "generationConfig": {"temperature": temperature}}


def _google_reply(payload: Mapping[str, Any], *, lane: str) -> ModelReply:
    """Google's ``generateContent`` answer as a :class:`ModelReply`. **Pure.**

    ⚠️ **THE USAGE BLOCK IS CARRIED VERBATIM AND ``total_tokens`` IS A RENAME OF THE
    PROVIDER'S OWN ``totalTokenCount`` — never a sum.** Google defines ``totalTokenCount``
    as *prompt + thoughts + response candidates*, so ``promptTokenCount +
    candidatesTokenCount`` silently drops the third term.
    """
    usage = payload.get("usageMetadata")
    if not isinstance(usage, Mapping) or "totalTokenCount" not in usage:
        raise ProviderFailed(
            f"lane {lane!r} answered with no usage block carrying 'totalTokenCount'. THIS "
            f"IS A REFUSAL, NOT A ZERO: a zero would spend the lane's quota and report that "
            f"it had not, and hard rule 12 takes tokens from the API's OWN usage field and "
            f"never estimates them. It is NOT reconstructed from promptTokenCount + "
            f"candidatesTokenCount, which drops thoughtsTokenCount entirely"
        )
    total = usage["totalTokenCount"]
    if isinstance(total, bool) or not isinstance(total, int):
        raise ProviderFailed(
            f"lane {lane!r} reported a total token count that is not an integer "
            f"({type(total).__name__}). Golden 8: 'Integer tokens throughout'"
        )
    candidates = payload.get("candidates")
    text = ""
    if isinstance(candidates, list) and candidates:
        content = candidates[0].get("content")
        if isinstance(content, Mapping):
            parts = content.get("parts")
            if isinstance(parts, list):
                # ⚠️ Joined across parts, and a part WITHOUT a "text" key is skipped rather
                # than indexed: a thought part or a functionCall part has none, and
                # parts[0]["text"] would raise on a reply that is otherwise fine. A
                # candidate can also arrive with NO content at all when finishReason is
                # MAX_TOKENS or SAFETY — that is an empty reply, and hard rule 11 counts
                # the episode rather than dropping it.
                text = "".join(
                    part["text"]
                    for part in parts
                    if isinstance(part, Mapping) and "text" in part
                )
    return ModelReply(text=text, usage={**usage, "total_tokens": total})


def _groq_body(
    model_id: str, messages: tuple[dict[str, str], ...], temperature: float | None
) -> dict[str, Any]:
    """C6's message list as Groq's OpenAI-compatible chat body. **A pure function.**

    ⚠️ **THE MODEL ID GOES IN THE BODY, NOT THE PATH**, and it is read from
    `config/lanes.yaml`. ⚠️ ``logprobs``, ``logit_bias``, ``top_logprobs`` and
    ``messages[].name`` are documented as **unsupported** here and are never emitted, and
    ``max_completion_tokens`` is deliberately absent for the same reason ``maxOutputTokens``
    is on the Google path. ``stream`` is never set, because with streaming the usage block
    leaves ``payload["usage"]`` and the token accounting **disappears silently** — which is
    the one failure hard rule 12 cannot tolerate.
    """
    wire: list[dict[str, str]] = []
    for message in messages:
        role = _GROQ_ROLE.get(message["role"])
        if role is None:
            raise DriverClientError(
                f"role {message['role']!r} has no Groq equivalent. The legal values are "
                f"{sorted(set(_GROQ_ROLE))}. A refusal, never a coercion — see the Google "
                f"path for why"
            )
        wire.append({"role": role, "content": message["content"]})
    body: dict[str, Any] = {"model": model_id, "messages": wire}
    if temperature is not None:
        body["temperature"] = temperature
    return body


def _groq_reply(payload: Mapping[str, Any], *, lane: str) -> ModelReply:
    """Groq's chat answer as a :class:`ModelReply`. **Pure.**

    ⚠️ ``content`` can be JSON ``null`` when a model emits tool calls, and qwen3 is a
    reasoning family that may put its chain of thought in a sibling ``reasoning`` field.
    **``content`` is the reply and ``reasoning`` is not read** — the graded text has to be
    one thing, decided here rather than by whichever field happened to be populated.
    """
    usage = payload.get("usage")
    if not isinstance(usage, Mapping) or "total_tokens" not in usage:
        raise ProviderFailed(
            f"lane {lane!r} answered with no usage block carrying 'total_tokens'. THIS IS A "
            f"REFUSAL, NOT A ZERO: hard rule 12 takes tokens from the API's OWN usage field "
            f"and never estimates them, and it is NOT reconstructed from prompt_tokens + "
            f"completion_tokens"
        )
    total = usage["total_tokens"]
    if isinstance(total, bool) or not isinstance(total, int):
        raise ProviderFailed(
            f"lane {lane!r} reported a total token count that is not an integer "
            f"({type(total).__name__}). Golden 8: 'Integer tokens throughout'"
        )
    choices = payload.get("choices")
    text = ""
    if isinstance(choices, list) and choices:
        message = choices[0].get("message")
        if isinstance(message, Mapping):
            content = message.get("content")
            if isinstance(content, str):
                text = content
    return ModelReply(text=text, usage=dict(usage))


@dataclass(frozen=True)
class _LaneCall:
    """Everything one lane needs for one call. Built from `config/lanes.yaml`, never typed."""

    lane: str
    provider: str
    api_model_id: str
    key_env_var: str


def _lane_call(lane_name: str) -> _LaneCall:
    """Resolve one lane from `config/lanes.yaml`. ⚠️ **Refuses an unknown provider.**"""
    lanes = load_lanes()
    if lane_name not in lanes:
        raise DriverClientError(
            f"lane {lane_name!r} is not in config/lanes.yaml. Known lanes: {sorted(lanes)}"
        )
    lane = lanes[lane_name]
    if lane.provider not in _PROVIDERS:
        raise DriverClientError(
            f"lane {lane_name!r} sits on provider {lane.provider!r}, which this client has "
            f"no endpoint for. It speaks {sorted(_PROVIDERS)} and REFUSES rather than "
            f"guessing a URL: a guessed endpoint fails in a way indistinguishable from a "
            f"dead credential"
        )
    return _LaneCall(
        lane=lane_name,
        provider=lane.provider,
        api_model_id=lane.api_model_id,
        # ⚠️ The NAME, derived from config/lanes.yaml's provider field. Never a literal in
        # this file, and never a value: runner/keys.py has no code path that returns one.
        key_env_var=env_var_for_provider(lane.provider),
    )


@dataclass
class MeteredProviderClient:
    """⚠️ **THE REAL PROVIDER CLIENT.** Routed by lane, no retry, no estimate.

    ⚠️⚠️ **IT SERVES EVERY LANE THE MATRIX NAMES, AND THE CALLER SAYS WHICH ON EVERY CALL.**
    `QUESTIONS.md` **Q-161**, RULED 2026-09-03, **option 1**. Until that ruling landed,
    :class:`MeteredModelClient`'s two methods distinguished the **role** — attacker or
    judge — and carried nothing that distinguished a *lane*, so this class held exactly one
    attacker lane and one judge lane and `driver/__main__.py` **refused by name** on the
    pilot's own matrix, whose attacker cells sit on `google` and `groq`. The refusal is gone
    because its cause is: ``lane`` is now a required, undefaulted argument on both methods,
    and it is resolved here against a map built from `config/lanes.yaml`.

    ⚠️ **AN UNKNOWN LANE IS A NAMED REFUSAL, NEVER A FALLBACK.** The routing table is what
    the run was constructed for; a call naming something outside it is a wiring bug, and
    every alternative to refusing is a guess about which provider the traffic belongs to.

    ⚠️ **NEVER RUN AGAINST EITHER PROVIDER.** No session may call these endpoints, so every
    request and reply shape here is built from the published REST references and exercised
    against a fake :data:`Transport`. `QUESTIONS.md` **Q-162**. It ships **unreviewed and
    disclosed**, exactly as `Q-150`'s ruling says it does — and `Q-161`'s threading is
    likewise exercised only against that fake.
    """

    lanes: Mapping[str, _LaneCall]
    transport: Transport = _http_post

    @classmethod
    def for_lanes(
        cls,
        *,
        attacker_lane: str,
        judge_lane: str,
        transport: Transport | None = None,
    ) -> "MeteredProviderClient":
        """Build from one attacker lane and one judge lane, resolved through
        `config/lanes.yaml`. A convenience over :meth:`for_lane_names` for the single-cell
        case. The two names may be equal — `CONTEXT.md` §13.3.2 puts the reference attacker
        and the gate judge on the same lane — and the map is keyed by name, so that is one
        entry rather than a conflict."""
        return cls.for_lane_names(
            attacker_lanes=(attacker_lane,), judge_lane=judge_lane, transport=transport
        )

    @classmethod
    def for_lane_names(
        cls,
        *,
        attacker_lanes: Iterable[str],
        judge_lane: str,
        transport: Transport | None = None,
    ) -> "MeteredProviderClient":
        """⚠️ **Q-161: BUILD FOR EVERY LANE THE MATRIX DISPATCHES ON.**

        Each name is resolved through `config/lanes.yaml` **at construction time**, so an
        unknown lane or an unsupported provider is a refusal **before** the first episode
        rather than partway through a single-shot run that has already spent tokens.
        """
        names = list(attacker_lanes)
        if not names:
            raise DriverClientError(
                "a provider client was asked for zero attacker lanes. A client serving no "
                "attacker lane would refuse every call it received, at the far end of a run "
                "that had already been declared and started"
            )
        resolved = {name: _lane_call(name) for name in [*names, judge_lane]}
        return cls(lanes=resolved, transport=transport or _http_post)

    def complete_attacker(
        self, *, messages: tuple[dict[str, str], ...], temperature: float, lane: str
    ) -> ModelReply:
        """One attacker turn on the lane **the caller names**, at `config/`'s temperature."""
        return self._call(self._route(lane, role="attacker"), messages, temperature)

    def complete_judge(self, *, system: str, user: str, lane: str) -> ModelReply:
        """One judge call on the lane **the caller names**.

        ⚠️ **NO TEMPERATURE IS SENT, BECAUSE `config/` CARRIES NONE FOR THE JUDGE.**
        ``gate_judge`` has no temperature key and hard rule 9 forbids inventing one here, so
        the provider's own default applies and `QUESTIONS.md` **Q-164** asks for the key.
        ⚠️ The pilot runs **arm 1**, which has no gate, so this method makes **zero** calls
        in that run — but a judged arm would inherit a temperature nobody declared.
        """
        return self._call(
            self._route(lane, role="judge"),
            ({"role": "system", "content": system}, {"role": "user", "content": user}),
            None,
        )

    def _route(self, lane: str, *, role: str) -> _LaneCall:
        """⚠️ **THE WHOLE OF THE ROUTING, AND IT IS A LOOKUP RATHER THAN A DECISION.**

        Nothing here reads the messages, the call order, or the caller's frame. `Q-161`
        records that the stack-walk was verified to work and **rejected** as `INC-51`'s
        species; content-based inference is impossible in any case, because
        `driver/pilot.py` hands both cells the same seed block and turn 1 of each is
        byte-identical.
        """
        name = _required_lane(lane, role=role)
        if name not in self.lanes:
            raise DriverClientError(
                f"this client was built for lanes {sorted(self.lanes)} and a {role} call "
                f"named {name!r}. THAT IS A REFUSAL, NOT A FALLBACK: routing it to any lane "
                f"in the map would put one provider's traffic on another provider's row, "
                f"which is silent until the published per-lane token figures are read and "
                f"would make CLAUDE.md S4's 429 rule stop the wrong lane (QUESTIONS.md "
                f"Q-161)"
            )
        return self.lanes[name]

    def _call(
        self,
        lane: _LaneCall,
        messages: tuple[dict[str, str], ...],
        temperature: float | None,
    ) -> ModelReply:
        """Build, send, decode. ⚠️ **The key is read on one line and never leaves it.**"""
        if lane.key_env_var not in os.environ:
            raise DriverClientError(
                f"the environment does not carry {lane.key_env_var}. Only the NAME appears "
                f"here and in this message; the value is never printed (CLAUDE.md S4)"
            )
        secret = os.environ[lane.key_env_var]
        if lane.provider == "google":
            url = f"{_GOOGLE_BASE}/{lane.api_model_id}:generateContent"
            body = _google_body(messages, temperature if temperature is not None else 0.0)
            # ⚠️ THE HEADER, NEVER A ?key= QUERY STRING. urllib.error.HTTPError carries the
            # request URL on .url and prints it in its own repr, so a key in the query
            # string would leak into every logged traceback. That is the reason, not taste.
            headers = {"Content-Type": "application/json", "x-goog-api-key": secret}
        else:
            url = _GROQ_CHAT_URL
            body = _groq_body(lane.api_model_id, messages, temperature)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {secret}",
            }
        response = self.transport(url, json.dumps(body).encode("utf-8"), headers)
        return self._reply(lane, response)

    def _reply(self, lane: _LaneCall, response: HttpResponse) -> ModelReply:
        """Status to outcome. **Pure**, and the 429 branch is the reason it is separate.

        ⚠️ **A 429 RAISES AND DOES NOT RETRY.** `CLAUDE.md` §4: *"A 429 means the window is
        already spent: STOP and report — never retry into another lane."* Nothing is read
        off the ``retry-after`` header, because obeying it here is precisely the behaviour
        that rule forbids.
        """
        if response.status == 429:
            raise RateLimited(
                f"lane {lane.lane!r} answered HTTP 429. THE WINDOW IS ALREADY SPENT: this "
                f"client does not retry, does not back off and has no path to another lane "
                f"(CLAUDE.md S4, hard rule 12). The runner decides what happens next, and "
                f"only within this lane"
            )
        if not 200 <= response.status < 300:
            raise ProviderFailed(
                f"lane {lane.lane!r} answered HTTP {response.status}. The body is NOT "
                f"reproduced: a provider error can quote the credential it rejected. "
                f"Counted under PROVIDER_ERROR and never swallowed (hard rule 11)"
            )
        payload = _decode(response, lane=lane.lane)
        reply = (
            _google_reply(payload, lane=lane.lane)
            if lane.provider == "google"
            else _groq_reply(payload, lane=lane.lane)
        )
        # ⚠️ REFUSES, DOES NOT MASK. A provider that echoed a credential back — in a reply,
        # in an error string it embedded, in a usage field somebody widened — stops the run
        # here rather than writing it into a ledger. runner/redaction.py's own rule.
        refuse_if_secret_bearing(reply.text, where=f"$.{lane.lane}.text")
        refuse_if_secret_bearing(dict(reply.usage), where=f"$.{lane.lane}.usage")
        return reply
