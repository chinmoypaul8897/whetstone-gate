"""**THE EPISODE DRIVER — the chunk that turns eight built packages into a measurement.**

⚠️ **NOTHING IN THIS PROJECT COULD SPEND A TOKEN UNTIL THIS PACKAGE EXISTED.** Every other
chunk was built, tested and reviewed **in isolation** and **nothing wired them together**:
``runner/`` was a library with no entry point, and ``tasks.py`` exposed only ``test`` /
``eval`` / ``selftest`` / ``check-prereg`` / ``check-roles``. There was no command that ran
an episode. This is that command's engine.

--------------------------------------------------------------------------------------
LAYOUT — hard rule 8's purity separation
--------------------------------------------------------------------------------------

**Core (no I/O, no clock, no network, no randomness):**
  :mod:`.protocol`   the tool-call grammar and the derived schema block (`Q-140`, Class B)
  :mod:`.episode`    one episode: attacker → gate → world → ledger, once per turn
  :mod:`.pilot`      `CONTEXT.md` §13.4's pilot matrix and the one figure it exists to produce

**Thin outer shell (the only modules that touch a filesystem, a clock or git):**
  :mod:`.run`        preflight, the episode loop, checkpoints, resume, the report
  :mod:`.__main__`   the command line, and the flag that has to be typed to spend money

**Neither, and labelled so:**
  :mod:`.clients`    the injected-client Protocol, and the offline transcript client
  :mod:`.rehearsal`  a scripted transcript — ⚠️ **a fixture, never a model**

--------------------------------------------------------------------------------------
⚠️ THE SIX CLAIMS THIS PACKAGE MAKES, EACH SCOPED EXACTLY
--------------------------------------------------------------------------------------

**1. IT IMPORTS NO MODEL CLIENT AND MAKES NO PROVIDER CALL OF ITS OWN.** The client is a
parameter typed as :class:`.clients.MeteredModelClient`. ``tests/test_c12_driver.py`` asserts
it **two ways** — a transitive first-party AST walk **and** a raw-source scan — because
`INCIDENTS.md` **INC-51** measured that ``__import__``, ``importlib.import_module`` and
``getattr`` on a package root walk straight past an AST walk, and made a ``gates/`` module
run a ``scorer/`` predicate while `check_roles` **D1, D2 and D3 all reported PASS**.

**2. IT WAS BUILT AND TESTED WITH ZERO PROVIDER MODEL CALLS**, which is what its build prompt
sanctioned. Every lane is reserved (`PROCESS.md` §8); the pilot and the calibration are
**single-shot** (§6b) and the **operator** starts them, in their own terminal, with a
`RUN_DECLARED.md` committed and pushed first.

**3. NO ARGUMENT SPENDS MONEY BY DEFAULT.** :mod:`.run` refuses to touch a provider without
an explicit flag, without **both** ceilings, without an explicit sanction for every reserved
lane, and **entirely** if ``git rev-parse probe-v1`` does not resolve — because
`CONTEXT.md` §15.1 cuts that tag *before* the pilot and *before* the calibration, and a run
that spends before it exists has spent a single-shot run **outside the pre-registration**.

**4. `evals/` IS APPEND-ONLY AND DELETION IS OPERATOR-ONLY.** **There is no deletion path in
this package at all** — no ``os.remove``, ``os.unlink``, ``os.rmdir``, ``shutil.rmtree``,
``Path.unlink``, ``Path.rmdir`` or ``truncate``, in any module — and the absence is asserted
by parsing every module's AST rather than promised in this docstring.

**5. RESUMABLE AND IDEMPOTENT.** Checkpoint per episode, published on complete by an atomic
rename; re-running the same command re-runs **zero** completed episodes and writes **zero**
duplicates; a crash costs one episode rather than the run. ⚠️ **And a skipped episode is
still counted and printed** (hard rule 11) — a resumed run that reported only what it re-ran
would publish a smaller denominator every time it was restarted.

**6. DETERMINISM, AT ITS EXACT SCOPE AND NO WIDER.** The world, the ledger schema, the
dispatch order, the checkpoint key and bytes, and every arithmetic decision here are
byte-identical from the same seed. ⚠️ **MODEL OUTPUT IS NOT** — the attacker runs at
`config/`'s temperature against a hosted provider, so **re-running the models does not
reproduce the run**, and nothing sourced from this package may say that it does. What
`make eval` claims is *"every number regenerates from the stored ledgers"*, which is true,
checkable, and enough.

--------------------------------------------------------------------------------------
⚠️ FOUR THINGS THIS PACKAGE REFUSED TO DECIDE, AND WHERE EACH IS RECORDED
--------------------------------------------------------------------------------------

Hard rule 1: *"a session that stops on a real ambiguity has succeeded."* Each of these is a
**required argument with no default**, so the question cannot be answered by forgetting it:

  * **`Q-147`** — the call ceiling and the token ceiling are **not in `config/`**. Hard rule
    12's sanction comes from the prompt, so :mod:`.run` requires both explicitly.
  * **`Q-141`** — what a capture **references** for §9.2's **S3**. ``capture_payment``
    declares no authorization parameter, so the binding is unstated, and it is **Class A**:
    it changes arm 4's verdicts. One of its two readings **flatters our own gate**.
  * **`Q-142`** — a probe attempt made through a tool outside §8.6a's six-name surface gets
    **no ledger entry**, so CANARY-B reach under-counts it. One-directional, identical
    across arms, printed as a number.
  * **`Q-144`** — **which arm the pilot runs.** §13.4 and `PROTOCOL.md` §3.1 both say
    *"1 ref arm"* and neither says which; `config/` has no key for it.
"""

from __future__ import annotations

from .clients import (
    DriverClientError,
    MeteredModelClient,
    ModelReply,
    ProviderFailed,
    RateLimited,
    TranscriptClient,
)
from .episode import (
    S3_AUTHORIZATION_IS_THE_PAYMENT,
    S3_AUTHORIZATION_NEVER_REFERENCED,
    S3_BINDINGS,
    DriverEpisode,
    DriverError,
    EpisodeCounts,
    EpisodeSettings,
    LaneStopped,
    arm_invariant_prefix,
    prefixes_agree,
    run_one_episode,
)
from .pilot import (
    PILOT_BLOCK,
    PilotError,
    PilotMatrix,
    TokensPerEpisode,
    decide_n,
    load_pilot,
    measure_tokens_per_episode,
)
from .protocol import (
    CALL_FORMAT_INSTRUCTION,
    MALFORMED_CALL_REPLY,
    CallProtocolError,
    ParsedCall,
    parse_call,
    tool_schemas_text,
)
from .run import (
    PROBE_TAG,
    RunRefused,
    RunRequest,
    RunResult,
    execute,
    preflight,
    probe_tag_resolves,
)

__all__ = [
    "CALL_FORMAT_INSTRUCTION",
    "CallProtocolError",
    "DriverClientError",
    "DriverEpisode",
    "DriverError",
    "EpisodeCounts",
    "EpisodeSettings",
    "LaneStopped",
    "MALFORMED_CALL_REPLY",
    "MeteredModelClient",
    "ModelReply",
    "PILOT_BLOCK",
    "PROBE_TAG",
    "ParsedCall",
    "PilotError",
    "PilotMatrix",
    "ProviderFailed",
    "RateLimited",
    "RunRefused",
    "RunRequest",
    "RunResult",
    "S3_AUTHORIZATION_IS_THE_PAYMENT",
    "S3_AUTHORIZATION_NEVER_REFERENCED",
    "S3_BINDINGS",
    "TokensPerEpisode",
    "TranscriptClient",
    "arm_invariant_prefix",
    "decide_n",
    "execute",
    "load_pilot",
    "measure_tokens_per_episode",
    "parse_call",
    "prefixes_agree",
    "preflight",
    "probe_tag_resolves",
    "run_one_episode",
    "tool_schemas_text",
]
