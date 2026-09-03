"""**THE LANE-AWARE CHECKPOINTED RUNNER.** Nothing runs without this package.

`PROCESS.md` §12.1's C11 row, and it is the whole of what this package owes:

    Runner — a **lane-aware scheduler, not a thread pool**; independent token buckets for
    RPM/TPM/RPD per model; per-episode checkpoint keyed `(block, arm, seed_or_task,
    attacker_model)`, skipped on re-run; **resume across DAY boundaries**; 429 =
    backoff-with-jitter and re-queue **within the lane**, a 429 storm parks the lane; live
    per-model usage to `evals/usage/<model>-<date>.jsonl`; **lane reservation enforced**
    (§8); the ladder's arms-{1,4} × 4-points × n=5 matrix is a supported run mode.

--------------------------------------------------------------------------------------
⚠️ THE FIVE CLAIMS THIS PACKAGE MAKES, EACH SCOPED EXACTLY, BECAUSE THE LOOSER FORM OF
EVERY ONE OF THEM IS FALSE
--------------------------------------------------------------------------------------

**1. DETERMINISM — hard rule 10, at its own stated scope and no wider.**
The world, the ledger schema, the scorer and the replay are **byte-identical from the same
seed**, and are tested to be. **MODEL OUTPUT IS NOT.** The attacker runs at
`attacker.temperature` against a hosted provider, so re-running the models does **not**
reproduce the run, and nothing in this package — no docstring, no report line, no README
sentence sourced from here — may say that it does. What `make eval` claims is *"every
number regenerates from the stored ledgers"*, which is true, checkable, and enough.
What **this package** contributes to that claim is narrower still and is stated as such:
**the scheduler's dispatch ORDER, the checkpoint key, the checkpoint bytes and the
accounting arithmetic are deterministic given the same inputs and the same injected
clock.** The provider's replies are not an input this package controls.

**2. IDEMPOTENCE.** Re-running the same command re-runs **zero** completed episodes and
writes **zero** duplicates. A completed episode's checkpoint is *published on complete* by
an atomic rename, so a reader never observes a half-written one, and a crash costs one
episode rather than the run — including across a **day boundary**, which this sweep spans
by design.

**3. `evals/` IS APPEND-ONLY AND DELETION IS OPERATOR-ONLY** (`CLAUDE.md` §4). This package
contains **no** code that deletes, truncates or rewrites a completed episode's output. A
write whose bytes differ from an existing file is a **refusal**, not an overwrite; an
identical re-write is the no-op idempotence asks for. :mod:`.checkpoint` carries the
refusal and `tests/test_c11_runner.py` asserts the absence of every removal call.

**4. THE RUNNER TOUCHES NO KEY.** It never reads, prints, echoes or commits `.env` or any
API key **value**. To confirm a key exists it reads only the **name** — :mod:`.keys` returns
a boolean and has no code path that can return a value. Every checkpoint and every usage row
passes through a redaction refusal before it is serialised, so a key value cannot reach a
log or a checkpoint even if a caller hands one in.

**5. TOKENS COME FROM THE API's OWN `usage` FIELD, NEVER FROM AN ESTIMATE.**
`tests/goldens/golden8_tokens.json`: *"Tokens are taken from the API's OWN `usage` field.
NEVER estimated. The project's own character-per-token estimator (`attacker.chars_per_token`,
`Q-048`) exists for CONTEXT SIZING and is not what this accumulator reads."* And it reads
`usage.total_tokens` **and nothing else** — it does not add `prompt_tokens` and
`completion_tokens` itself, because providers differ on whether the total includes reasoning
or cached-read tokens and a reconstructed total can silently disagree with the billed one.

--------------------------------------------------------------------------------------
⚠️ HARD RULE 12 IS THIS CHUNK'S SPINE AND IT IS THE RULE THAT PROTECTS THE OPERATOR'S MONEY
--------------------------------------------------------------------------------------

A **token** ceiling as well as a call ceiling, per model, **abort at whichever comes first**,
and the admission test is **PROSPECTIVE** — hard rule 12 says ABORT, not *"overspend and then
abort"*. The rule's own example is what happens otherwise: one spike episode burned ~300K
tokens against a 200K-TPD lane. :mod:`.budget` is that accumulator, it is **pure**, and
golden 8's fixtures A–F are its oracle.

⚠️ **CEILINGS ARE PER MODEL AND ARE NEVER POOLED.** Golden 8 fixture E: two lanes at 60,000
and 50,000 pool to 110,000 — over a 100,000 ceiling — while **neither exceeds it alone**, and
the correct outcome is that **both lanes continue**. A pooling accumulator aborts a lane that
has budget, and costs the run episodes it was entitled to.

--------------------------------------------------------------------------------------
⚠️ HARD RULE 11 — THE DENOMINATOR, AND WHY THIS PACKAGE COUNTS EPISODES TWICE ON PURPOSE
--------------------------------------------------------------------------------------

Razorpay's own B.9: *"Score complete trials only. Do not let retries, fallbacks, skipped
cases, or missing traces quietly shrink the denominator."* Every dropped episode is counted,
categorised and printed as a number, and **a truncated episode is COUNTED IN THE
DENOMINATOR** — it is *attempted* and it is *counted*, never quietly removed.

⚠️ **`scorer/drops.py` ALREADY IMPLEMENTS A DENOMINATOR AND THIS PACKAGE DOES NOT IMPORT IT.**
That is a deliberate Class B decision recorded at `QUESTIONS.md` **Q-119**, on hard rule 8's
own argument applied one step out: the runner counts episodes **as they run against the live
provider**, the scorer counts them **at replay off the stored ledgers**, and if they shared a
class **they could not disagree** — which is exactly what rule 8 says about `gate.js` and
`invariants.js` both calling `world.js:intentKey` (*"that is not a result; it is a
definition"*). The two vocabularies are **not** copies of one another and neither is the
other's subset: this package's categories answer *"why did this episode not finish"*
(:mod:`.episodes`), the scorer's answer *"why is this episode not scorable"*. A reviewer
looking for drift should look for a **mapping** defect, not for a copy that fell behind.

--------------------------------------------------------------------------------------
LAYOUT — hard rule 8's purity separation
--------------------------------------------------------------------------------------

**Core (no I/O, no clock, no network, no randomness):**
  :mod:`.budget`     the two-ceiling accumulator — golden 8's A–F oracle
  :mod:`.buckets`    RPM/TPM/RPD token buckets; **the clock is an argument**
  :mod:`.episodes`   the episode key, the outcome vocabulary and the denominator
  :mod:`.n_rule`     `CONTEXT.md` §13.4's N decision rule — **both** conjuncts (`Q-107`)
  :mod:`.report`     the printable accounting; per model, never pooled

**Thin outer shell (the only modules that touch a filesystem or a clock):**
  :mod:`.lanes`      reads `config/lanes.yaml`; lane reservations (`PROCESS.md` §8)
  :mod:`.usage`      `evals/usage/<model>-<date>.jsonl`, append-only
  :mod:`.checkpoint` per-episode checkpoints; atomic, publish-on-complete, idempotent
  :mod:`.keys`       key **presence** by name; there is no path here that returns a value
  :mod:`.scheduler`  the lane-aware scheduler; 429 backoff, park, re-queue **within** the lane

⚠️ **THIS PACKAGE IMPORTS NO MODEL CLIENT** and it makes no provider call. It is handed a
callable and it drives it; the callable's identity is the caller's business. The runner is
**not** one of `CONTEXT.md` §14's four deliberate non-uses — those are the scorer, the probe,
the void rule, the world and the arm-4 kernel — and this package does not claim to be. What
it claims is only that it was **built and tested with zero provider model calls**, which is
what its build prompt sanctioned: TOKEN SPEND: NONE.
"""

from __future__ import annotations

from .budget import (
    Admission,
    Ceilings,
    LaneBudget,
    STOP_BY_429,
    STOP_BY_CALL_CEILING,
    STOP_BY_TOKEN_CEILING,
    usage_total_tokens,
)
from .episodes import (
    EpisodeKey,
    EpisodeOutcome,
    RunDenominator,
    UNFINISHED_CAUSES,
)
from .n_rule import NDecision, project_total_tokens, select_n

__all__ = [
    "Admission",
    "Ceilings",
    "EpisodeKey",
    "EpisodeOutcome",
    "LaneBudget",
    "NDecision",
    "RunDenominator",
    "STOP_BY_429",
    "STOP_BY_CALL_CEILING",
    "STOP_BY_TOKEN_CEILING",
    "UNFINISHED_CAUSES",
    "project_total_tokens",
    "select_n",
    "usage_total_tokens",
]
