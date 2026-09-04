# REVIEW C14 — THE FLOOR — REVIEW 1

**`SESSION-TOKEN 2f7a6d18` · CHUNK C14 · ROLE REVIEW · 2026-09-04/05 UTC**

**Reviewed:** `0cfc231` and `b01edaa` — the catch-all floor in
`driver/episode.py:_MeteredCall.run`, `UNEXPECTED_ERROR` in `runner/episodes.py`, and the tests
that came with them. **Diff reviewed:** `git diff 67839d0..b01edaa`.
**Built by `8c2f5e91` (C14 ABORT 2, role FIX). This session did not build it and did not fix it.**
**Ruling under review:** `QUESTIONS.md` **`Q-200`**. **Incidents:** `INC-159`, `INC-160`.
**`HEAD` MOVED TWICE UNDER THIS REVIEW**: `e8dd501` → `291fd91` → **`625d9e9`**, both a concurrent
**C14 ABORT 3** session's (`7d4e2fa9`) — its pacer-admission fix and its `INC-161`/`Q-206` records.
⚠️ **THE BLOCKER WAS RE-MEASURED AGAINST `291fd91` AND REPRODUCES IDENTICALLY** (§1.2.2), and
`git diff --name-only b01edaa..625d9e9` leaves `driver/episode.py` and `runner/episodes.py`
**untouched**. Every finding below is against the **committed** tree.

---

## ⚠️⚠️ BLOCKER, IN ONE LINE, BEFORE ANYTHING ELSE

⚠️⚠️ **ON ARMS 2, 2S AND 3 — THREE OF THE FIVE ARMS THE SWEEP RUNS — THE FLOOR BOOKS THE ESCAPE
AND THE RUN STILL DIES WITH NO REPORT AND NO DENOMINATOR**, because
`driver/episode.py:837`'s `executor.counts.reconcile()` sits **after** `run_one_episode`'s
`except LaneStopped` and **outside** the floor, and every `LaneStopped` raised inside
`gate.decide` — **including a 429** — leaves `attempted > decided + unparsed + off_surface`.
**Measured, on the committed `b01edaa` tree: `TimeoutError`, a bare `RuntimeError`, a 429, a 500
and a `BucketError` in a judge call ALL kill `driver_run.execute` with `DenominatorError`.**
**That is `INC-159`'s failure, one frame out, and it is not one of the four sites `Q-202` names.**

## VERDICT: **FAIL**

**No tag was cut.** `c14-pass` does not exist and this session did not create it.
**The sweep must not start on this floor.** The calibration that ran tonight is **arm 1** and is
**not** exposed (§1.11).

---

# PART I — PHASE 1. SEALED. FINDINGS, NOT JUDGEMENT.

## 1.0 WHAT THIS SESSION SPENT, TOUCHED AND DID NOT TOUCH

- ⚠️ **ZERO PROVIDER TOKENS. NO PROVIDER CALL IN ANY MODE.** No sanction was held and none was
  taken. Every harness in this review replaced `driver/clients.py:_http_post` with a function
  that **raises** before running anything, so a reach for the real transport is an
  `AssertionError` and not a spend. No lane was touched; `evals/usage/` was **read** only.
- ⚠️ **`evals/` WAS READ AND NEVER WRITTEN.** Nothing under it was created, edited, deleted or
  truncated by this session. Every harness wrote to a fresh `tempfile.TemporaryDirectory()`,
  never to the repository.
- ⚠️ **`src/`, `tests/`, `config/`, `tests/goldens/`, `INCIDENTS.md`, `STATUS.md`, `PROGRESS.md`
  AND EVERY FROZEN ARTEFACT WERE READ-ONLY.** This session wrote exactly the four files its
  fence names.
- ⚠️ **NO TAG WAS CUT OR MOVED. NO HISTORY WAS REWRITTEN. NO FORCE-PUSH.** The operator is
  asleep and a tag is irreversible.
- **`.env` was never opened.** No key name and no key value was read, printed or committed.

## 1.1 THE INSTRUMENTS, AND THE ONE THING THAT COMPLICATED THEM

Everything load-bearing here was **re-measured by execution**, not read off the build session's
report. `docs/sessions/c14-abort-2.txt` is a claim; the numbers below are this session's.

⚠️ **THE WORKING TREE'S `src/` WENT DIRTY UNDER THIS REVIEW, AND THE DECISIVE PROOF WAS RE-RUN
AGAINST THE COMMITTED TREE BECAUSE OF IT.** `git status --porcelain src/ config/` was **empty**
when this session opened and empty again around `2026-09-04T19:20Z`. At
`2026-09-04T19:42:59Z` it was **not**:

    M src/whetstone_gate/driver/run.py
    M src/whetstone_gate/runner/buckets.py

A **concurrent C14 ABORT 3 session** (`7d4e2fa9`) was writing an `INC-161` pacer-admission fix into
those two files, and **committed it as `291fd91` while this review was being written**
(`run.py +189`, `buckets.py +82`, and a new `tests/test_c14_pacer_admission.py` of 880 lines).
⚠️ **NEITHER FILE IS C14 ABORT 2's.** `git diff --name-only b01edaa..291fd91` shows
`driver/episode.py` and `runner/episodes.py` — the only two files `0cfc231..b01edaa` touched under
`src/` — **untouched**, and their frame hashes are byte-identical at `b01edaa` and `291fd91`.

**So the decisive measurement was re-run on a reconstructed committed tree**: `git archive
67839d0` into a fresh OS temp directory, then `git show b01edaa:` overlaid for exactly the two
files that differ (verified: `git diff --name-only 67839d0..b01edaa -- src/` lists those two and
nothing else). That tree's `driver/run.py` differs from the working tree's and equals the
committed blob. **When `HEAD` then moved to `291fd91`, the same tree was re-overlaid with that
commit's `run.py` and `buckets.py` and the proof was run a third time.** ⚠️ **The result is
identical in all three** (§1.2.2).

⚠️ **EVERY LINE NUMBER IN §1.3 WAS RE-ANCHORED AGAINST `git show HEAD:<path>`**, not against the
working tree, precisely because `run.py` is dirty. One citation was off by one and is corrected
in place; the rest anchor exactly.

## 1.2 ⚠️⚠️ THE FIFTH INSTANCE. `executor.counts.reconcile()`, AND IT IS NOT IN `Q-202`

### 1.2.1 The mechanism

`driver/episode.py:_Executor.execute` counts a turn **before** it decides it:

    self.counts.attempted += 1                            # episode.py:655
    self.turns_run += 1
    ...
    verdict: Verdict = self.gate.decide(action, state)    # episode.py:680
    self.counts.decided += 1                              # episode.py:681

For arms **2, 2S and 3** `gate.decide` is `gates/judge.py:ModelGate.decide`, whose
`self.client.complete(...)` at **`judge.py:237`** is wrapped in **no `try` at all** — measured,
not read: no gate implementation in `gates/` catches anything from its client. That call runs
`driver/episode.py:_JudgeClient.complete` → `_MeteredCall.run` → **the floor**. The floor books
the usage row and raises `LaneStopped(UNEXPECTED_ERROR)`.

`attacker/loop.py:278`'s `result_text = executor.execute(attacker_text)` has no handler either —
the attacker loop contains **no `try` at all** — so the `LaneStopped` arrives at
`run_one_episode`'s `except LaneStopped`, **which is where the floor's protection ends.** The
next statement is:

    executor.counts.reconcile()                           # episode.py:837

and `attempted` is one greater than `decided + unparsed + off_surface`, because the turn was
abandoned **between** the two increments. `EpisodeCounts.reconcile` raises `DenominatorError`
(`episode.py:195`), which `run_one_episode` does not catch, which `execute`'s dispatch loop does
not catch. **No report. No denominator. No remaining episode attempted.**

⚠️ **`reconcile()` IS RIGHT TO FIRE.** A turn really did leave the record without a category.
**The defect is that firing it destroys the denominator it exists to protect** — hard rule 11's
guard killing hard rule 11's report.

### 1.2.2 Measured. Arm 2, the pilot matrix, the fault raised in the transport frame

Harness: the real `MeteredProviderClient` over a fake transport, the real `_PacedClient`, the
real `execute` dispatch loop, `_http_post` replaced by a raiser, output root a temp directory,
attacker replies a parseable on-surface tool call so the gate is genuinely reached. **Run three times: against the live tree, against the reconstructed committed `b01edaa` tree, and
again against the committed **`291fd91`** tree after `HEAD` moved mid-review. Identical every
time** — `291fd91` changes `run.py:execute` (the pacer admission fix) and every other frame on
this path is byte-identical to `b01edaa`.

    MODE       ARM  OUTCOME                                      faults judge_calls
    none       2    RETURNED  causes=[None]                           1         400
    timeout    2    RAISED DenominatorError @ episode.py:195          1           2
    runtime    2    RAISED DenominatorError @ episode.py:195          1           2
    429        2    RAISED DenominatorError @ episode.py:195          1           2
    500        2    RAISED DenominatorError @ episode.py:195          1           2
    bucket     2    RAISED DenominatorError @ episode.py:195          1           2
    none       1    RETURNED  causes=[None]                           0           0
    timeout    1    RETURNED  causes=[None]                           0           0
    runtime    1    RETURNED  causes=[None]                           0           0
    429        1    RETURNED  causes=[None]                           0           0
    500        1    RETURNED  causes=[None]                           0           0
    bucket     1    RETURNED  causes=[None]                           0           0

⚠️ **THE `none` ROW IS THE CONTROL AND IT MATTERS**: with no fault, arm 2 completes every episode
in the matrix through **400 real judge calls**, so the harness genuinely drives the judged path
and the five reds are the fault and not the fixture. The arm-1 rows reproduce the build
session's own result and are the reason this was invisible to it.

The escape, verbatim:

    File "src/whetstone_gate/driver/run.py", line 894, in execute
        episode = run_one_episode(
    File "src/whetstone_gate/driver/episode.py", line 837, in run_one_episode
        executor.counts.reconcile()
    File "src/whetstone_gate/driver/episode.py", line 195, in reconcile
        raise runner_episodes.DenominatorError(
    whetstone_gate.runner.episodes.DenominatorError: turn counts do not reconcile: 2 attempted
    against 1 decided + 0 unparsed + 0 off-surface = 1. A turn in none of the three categories
    has left the record without saying so (hard rule 11)

⚠️ **THE `429` ROW IS THE ONE TO READ TWICE.** `CLAUDE.md` hard rule 12 and `PROCESS.md` §8:
*"A 429 MEANS THE WINDOW IS ALREADY SPENT: STOP and report."* On a judged arm it does not
report — it crashes. The **ceiling** stops take the same path: `_MeteredCall.run` raises
`LaneStopped` from `budget.admit`'s refusal (`episode.py:373`) or from the
`if self.budget.stopped` pre-check (`episode.py:370`), and on a judged arm both of those fire
inside `gate.decide` too.

⚠️ **AND THE SHARED LANE MAKES THE CEILING CASE THE COMMON CASE, NOT THE RARE ONE.**
`PROTOCOL.md` §2.1's lane table puts the **reference attacker and the gate judge for arms 2/2S/3
on the same lane, `gemma-26b`**, so `run.py`'s `lane_states[lane]` and `lane_states[judge_lane]`
resolve to **the same `LaneState` and the same `LaneBudget` object**. A judged turn is one
attacker call followed by one judge call. When the shared ceiling binds, whichever of the two is
offered next raises — and on a judged arm the judge's is inside `gate.decide`.

### 1.2.3 It is NOT a regression introduced by `0cfc231` / `b01edaa` — proved by hashing the frames

Source-segment SHA-256 of every frame on the defect's path, `67839d0` versus `b01edaa`:

    FRAME                                   67839d0    b01edaa    IDENTICAL
    episode.py:run_one_episode              a23b5b50   a23b5b50   True
    episode.py:_Executor.execute            f72c55f5   f72c55f5   True
    episode.py:EpisodeCounts.reconcile      c43f6b25   c43f6b25   True
    episode.py:_JudgeClient.complete        d598029d   d598029d   True
    run.py:execute                          9003361c   9003361c   True
    judge.py:ModelGate.decide               9296ff93   9296ff93   True
    episode.py:_MeteredCall.run             d5a9f64c   82ce6304   False   <-- the only change

⚠️ **`_MeteredCall.run` IS THE ONLY FRAME C14 ABORT 2 CHANGED.** The 429 and 500 rows of §1.2.2
therefore behaved identically before the floor existed. **The finding is not "C14 broke this".
It is "C14's deliverable is the claim this falsifies, on three of the five arms, and C14's tests
cannot see it".** `Q-200`'s words are *"THE RUN CONTINUES TO THE NEXT EPISODE"*; on arms 2, 2S
and 3 it does not.

### 1.2.4 `Q-202` does not name it

`Q-202` names four uncovered sites: **world build, gate build, ledger write, `_publish`**.
`executor.counts.reconcile()` is none of them. It is *inside* `run_one_episode`, one statement
after the handler the floor's own `LaneStopped` is caught by — **closer to the floor than any
site the open question lists**, and reachable by the floor's own new exception. `Q-202`'s table
weighs *"widen the floor"* against *"leave it at the model call"*; **this site is on neither
side of that trade**, because the floor is already inside the frame that dies.

## 1.3 THE ENUMERATION — EVERY RAISE SITE ON THE SWEEP'S PATH THAT IS OUTSIDE THE FLOOR

⚠️ **Read "kills" as: the exception escapes `driver/run.py:execute` with no report and no
denominator** — `INC-159`'s exact loss. Line numbers are against **`git show HEAD:<path>`**.
`Q-202?` marks the sites the open question already names.

### 1.3.1 Per-episode, inside `run_one_episode` — the floor's own frame and its neighbours

| # | Site | Raises | Trigger | Arms | `Q-202`? |
|---|---|---|---|---|---|
| 1 | ⚠️ `episode.py:837` `executor.counts.reconcile()` | `DenominatorError` | **any `LaneStopped` from `gate.decide`** — 429, ceiling, timeout, any escape | **2, 2S, 3** | **NO — §1.2** |
| 2 | ⚠️ `episode.py:526` the floor's own `self.on_usage(...)` | `OSError`, `UsageError`, `SecretInPayload` | the usage write fails **from inside the `except` clause** | all | **NO — §1.4** |
| 3 | `episode.py:782`, `:788` the two `DriverError` preconditions | `DriverError` | gate/ledger arm or seed disagree with the episode | all | no |
| 4 | `episode.py:799` `opening_state(world, ...)` | `KeyError` | a payment id in `world.payment_ids` absent from `_payments` | all | no |
| 5 | `episode.py:829` `protocol.tool_schemas_text()` | `KeyError` | a surface name with no declaration | all | no |
| 6 | `episode.py:659` the executor's turn-budget guard | `DriverError` | the loop runs past the turn budget | all | no |
| 7 | `episode.py:667` `protocol.parse_call(...)` | `RecursionError`, `CallProtocolError` | pathological attacker text | all | no |
| 8 | `episode.py:678` `candidate_action(...)` | `UnknownTool`, `TypeError` | attacker arguments the gate cannot classify (`gates/action.py:94`) | all | no |
| 9 | `episode.py:679` `replace(self.state, ...)` | `TypeError` | `FoldedState.__post_init__` refuses (`gates/state.py:54`) | all | no |
| 10 | ⚠️ `episode.py:680` `self.gate.decide(action, state)` | **anything the gate, judge, world or ledger raises** | see §1.2; also `gates/verdict.py:125`, `gates/arm4_kernel.py:278`/`:323` | all | no |
| 11 | `episode.py:685` `ledger_build.executed_of(result)` | `LedgerEntryError` | a world result whose `ok` is not a bool (`ledger/build.py:270`) | all | no |
| 12 | `episode.py:698` `ledger_build.append_call(...)` | `NotCanonicalisable`, `LedgerEntryError` | a float amount, non-UTF-8 text, an empty target (`ledger/chain.py:241`,`:270`; `ledger/entry.py:452`) | all | partly |
| 13 | `episode.py:533` `usage_total_tokens(reply.usage)` | `BudgetError` | a 200 reply whose usage block is malformed — **after** the floor's `try` has closed | all | no |
| 14 | `episode.py:249` `EpisodeOutcome(...)` inside `outcome()` | `DenominatorError` | the outcome's own invariants refuse | all | no |

### 1.3.2 Per-episode, in `driver/run.py:execute` — outside `run_one_episode` entirely

| # | Site | Raises | Trigger | `Q-202`? |
|---|---|---|---|---|
| 15 | `run.py:888` `world_semantics.build(world_generator.generate_world(seed), ...)` | world-layer refusals (`world/spec.py:68`, `world/oracle.py:190`, `world/money.py:128`, `world/semantics.py:387`) | a seed the world cannot build | **YES** |
| 16 | `run.py:891` `gate_shell.build_gate(arm, ...)` | `AuthoredTextMissing`, `PolicyTextMalformed`, `GateConfigError`, `OSError` (`gates/shell.py:81`,`:86`,`:117`; `gates/policy.py:62`,`:70`; `gates/constants.py:71`; `gates/judge.py:212`) | authored text unreadable — **re-read per episode, on every episode** | **YES** |
| 17 | `run.py:892` `Ledger(spec=chain_spec, seed=seed, arm=arm)` | `ChainConfigError` (`ledger/chain.py:310`) | an arm outside the five | **YES** |
| 18 | `run.py:1085` `ledger_store.write(...)` inside `_publish` | `LedgerStoreError`, `OSError`, `UnicodeEncodeError` (`ledger/store.py:137`,`:155`,`:162`) | full disk, file lock, an existing file with differing bytes | **YES** |
| 19 | `run.py:1086` `checkpoints.publish(...)` inside `_publish` | `CheckpointRefusal`, `SecretInPayload`, `OSError` | as above | **YES** |
| 20 | `run.py:840` `seed = int(key.seed_or_task)` | `ValueError` | a **task-keyed** block — T-NEG and AD-CMP are task-enumerated, not seed-enumerated | no |
| 21 | ⚠️ `run.py:1019` `usage_log.append(...)` in `_usage_sink` — **the OK path too** | `OSError`, `UsageError`, `SecretInPayload` | the usage write fails on a *successful* call | no |

### 1.3.3 Per-turn, in `attacker/loop.py` — the loop the floor sits inside

| # | Site | Raises | Trigger |
|---|---|---|---|
| 22 | `loop.py:230` `texts.attacker_system_prompt()` | `AuthoredTextMissing` | authored text unreadable — **the first statement of every episode** |
| 23 | `loop.py:235` `texts.generic_denial()` | `AuthoredTextMissing` | as above |
| 24 | `loop.py:260` `assemble(...)` | `ValueError`, config errors, `OSError` (`attacker/context.py:363`,`:482`) | a summary cap or `verbatim_turns` out of range |
| 25 | `loop.py:297`, `:304` `estimate_messages(...)` | config errors, `ZeroDivisionError`, `TypeError` (`attacker/estimate.py:131`,`:209`) | `CHARS_PER_TOKEN` missing or zero |
| 26 | `loop.py:115` `TurnRecord`'s provenance guard | `ValueError` | a provenance the record refuses |
| 27 | `attacker/corpus.py:560` corpus selection | `CorpusUnavailable` | the selection cannot reach every corpus |
| 28 | ⚠️ `loop.py:278` `executor.execute(attacker_text)` | **passes every exception through untouched** | the loop has **no `try` at all** — this is the carrier for #1 and #10 |

### 1.3.4 Once per run — before the loop, and after it

| # | Site | Raises | What it costs |
|---|---|---|---|
| 29 | `run.py:359` `runner_usage.preflight(...)` | `UsageError`, `OSError` | fires **before any spend** — cheap, loud, correct |
| 30 | `run.py:426` `_load_corpus()` | `CorpusUnavailable` → `RunRefused` | before any spend — correct |
| 31 | `run.py:676` `status = probe(lane)` (the liveness probe) | `TimeoutError`, `ssl` errors | before any spend — correct |
| 32 | `run.py:805` `_lane_states(...)` | `LaneError`, `KeyError` | before any spend — correct |
| 33 | `run.py:823` `checkpoints.read(key)` on resume | `OSError`, `JSONDecodeError` | before any spend — correct |
| 34 | ⚠️ `run.py:921` `result.denominator.reconcile()` | `DenominatorError` | **after every episode has run.** 17 hours of work, and the report is never rendered |
| 35 | ⚠️ `run.py:922` `render(...)` → `run.py:1151`/`:1158` `measure_tokens_per_episode` / `decide_n` | `RunRefused`, `NRuleError` | the same: the work is done and the report **raises instead of printing** |

⚠️ **THE SHAPE OF THE LIST IS THE FINDING.** Sites **29–33** raise **before a token is spent**
and are exactly right — `INC-157`'s systemic guardrail working as designed. Sites **34–35** raise
**after every token is spent** and lose the whole report. Sites **1–28** raise **mid-run** and
lose the report *and* every remaining episode. **The floor covers one expression — `call()` —
inside site 10's callee.** Of the 35 sites above, `Q-202` names **five**; **thirty are outside
both the floor and the open question**, and **#1 is reachable by the floor's own new exception**.

## 1.4 ⚠️ CAN THE FLOOR ITSELF RAISE? YES — AND IT IS `INC-160`'s EXACT MECHANISM

The floor's body is four statements (`episode.py:519-531`):

    self.budget.settle(0)
    self.calls_settled += 1
    self.on_usage(self.lane, 0, runner_usage.OUTCOME_ERROR, error_type=type(escaped).__name__)
    raise LaneStopped(runner_episodes.UNEXPECTED_ERROR) from None

**An exception raised inside an `except` clause is not caught by any sibling `except` clause of
the same `try`.** That sentence is `INC-160`'s whole diagnosis, and it applies to the floor.

Each call, checked first-hand:

1. **`self.budget.settle(0)` — SAFE on this path.** `runner/budget.py:309` refuses with
   `BudgetError` when `_pending_reservation is None`, but the floor is only reachable after a
   successful `admit`, which sets it. `settle(0)` cannot trip the reservation-shortfall branch
   (`budget.py:334`) because `0 > reserved` is false. **No path found.**
2. **`LaneStopped(UNEXPECTED_ERROR)` — SAFE.** `LaneStopped.__init__` (`episode.py:151`) refuses
   a cause outside `UNFINISHED_CAUSES`; measured, `UNEXPECTED_ERROR` **is** a member (nine
   members, no duplicates). This is `INC-160`'s cause-side half and it is correct here.
3. ⚠️⚠️ **`self.on_usage(...)` — NOT SAFE. PROVED BY EXECUTION, NOT BY READING.** It is
   `driver/run.py:_usage_sink` → `runner/usage.py:UsageLog.append`. Every validation passes for
   the floor's arguments (`OUTCOME_ERROR` is declared; `total_tokens=0` is a non-negative int;
   `status=None`; `error_type` is a `str`). **What is not guarded is the write itself:**
   `append` ends with `path.parent.mkdir(parents=True, exist_ok=True)` and `path.open("a", ...)`.
   **Measured, in a fresh OS temp directory, driving the real `_MeteredCall` with the real
   `_usage_sink`, the real `UsageLog` and the real `LaneBudget`:**

       control  (writable dir) : raised ('LaneStopped', 'UNEXPECTED_ERROR')   row written correctly
       usage file read-only    : GOT PermissionError  [Errno 13] ... gemma-26b-<date>.jsonl
       `evals` exists as a FILE: GOT FileExistsError  [WinError 183] ... \\evals

   **The escaping exception is not a `LaneStopped`**, so `run_one_episode`'s
   `except LaneStopped` does not see it either, and `execute`'s dispatch loop contains **no
   `try` at all** — `episode.py:469` is the only `except Exception` in the whole driver.
   **No report, no denominator: `INC-159`'s outcome, reached through the code written to
   prevent `INC-159`.**
   ⚠️ **AND ALL FOUR BRANCHES HAVE THE IDENTICAL EXPOSURE — measured, not inferred**:
   `RateLimited` (`:383`), `ProviderFailed` (`:405`), `BucketError` (`:446` — `INC-160`'s own
   line) and the floor (`:526`) each call `on_usage` from inside their own handler.
4. ⚠️ **`refuse_if_secret_bearing(row, ...)` now sees `type(escaped).__name__`, which is NEW
   content in that row.** `runner/redaction.py:49` refuses a string beginning `gsk_` or `AIza`,
   or containing `_API_KEY`. The floor's comment argues *"a type name is a Python identifier and
   cannot contain a credential"* — **true about credentials, and not the property the scan
   tests.** A class named `Missing_API_KEYError` is a legal identifier and would make the floor
   raise `SecretInPayload` from inside its own handler. Contrived; **not impossible**; and the
   comment states a stronger guarantee than the code has.

⚠️ **THE SAME EXPOSURE IS IN ALL THREE SIBLING BRANCHES AND ON THE SUCCESS PATH**
(`episode.py:383`, `:405`, `:446`, and `:537`). **It is not new to C14** — and the floor is the
layer that announced it was closing this class.

## 1.5 CAUSE LAUNDERING — THE GUARD HOLDS FORWARD, AND LEAKS BACKWARD

**Forward direction — I could not defeat it.** Measured:

- Handler order, by an `ast` walk of the `try` at `episode.py:376` (not by reading):
  `['RateLimited', 'ProviderFailed', 'BucketError', 'LaneStopped', 'Exception']` — exactly as
  the build session claims.
- MROs checked: `LaneStopped`, `RateLimited`, `ProviderFailed`, `BucketError`, `UsageError` and
  `DriverError` are **six independent `RuntimeError` siblings**; none subclasses another, so the
  ordering cannot be subverted by inheritance.
- By execution: `call()` raising `LaneStopped(RATE_LIMIT_429)` re-raises with
  `cause == RATE_LIMIT_429`, **not** `UNEXPECTED_ERROR`, and `calls_settled` stays **0** — the
  meter that raised it keeps its own accounting and nothing is double-counted.
- The build session's claim that no path nests one `_MeteredCall` inside another **holds**: the
  judge's meter is driven by the executor *between* attacker calls, never inside one.
- An exception raised *while a sibling handler is running* does **not** become the floor's —
  confirmed structurally and by execution. That is what makes §1.4 an escape rather than a
  relabelling.

⚠️ **BACKWARD DIRECTION — THE DIAGNOSIS IS LOST, AND `INC-159` IS THE ENTRY THAT SAYS WHY THAT
MATTERS.** `raise LaneStopped(UNEXPECTED_ERROR) from None` discards the original traceback.
`INC-159`'s `Missing` field is explicit that *"this abort was fully diagnosable in about four
minutes"* — **from the traceback**, which named the file, the line, the function and the type.
After the floor an operator gets `error_type` in a usage row, which names the type and nothing
else. **And on arms 2/2S/3 the exception that actually surfaces is `DenominatorError: turn
counts do not reconcile: 2 attempted against 1 decided`, which names neither the timeout nor the
transport.** The floor did not launder a *cause*; it laundered the *diagnosis*.

## 1.6 THE RESUME CONSEQUENCE — JUDGED, NOT ASSUMED

The build session disclosed it rather than hiding it. Verified first-hand:
`runner/checkpoint.py:123`'s `completed()` is `{p.stem for p in self.root.glob("*.json")}` —
**every published checkpoint, with no reference to `truncated` or `cause`.** So an episode
booked `UNEXPECTED_ERROR` is checkpointed and a resume will not re-run it. Confirmed against the
live record: tonight's `evals/checkpoints/cal__1__2201__gemma-26b.json` carries
`"cause": "RATE_LIMIT_429"`, `"truncated": true`, `"turns_run": 11`.

**The judgement:**

- **It is identical to its three siblings.** `RATE_LIMIT_429` and `PACER_REFUSED` have always
  behaved this way, and `build_document` **derives** `truncated` from the turn counts rather than
  taking a caller's flag. **Consistency is a real argument and it holds.**
- **The record is self-describing.** An operator can tell an instrument fault from a budget stop
  by one field — `cause` — in the checkpoint and in the printed denominator. **That answers the
  strongest objection to booking-and-checkpointing.**
- ⚠️⚠️ **THE ARITHMETIC IS NOT "ONE EPISODE VERSUS TWENTY-NINE", AND THIS REVIEW'S FIRST PASS
  HAD IT WRONG.** The tempting framing is *"booking costs one episode; the crash cost
  twenty-nine"*. **It is false, because the twenty-nine were never at risk.** A crash happens
  before `_publish`, so the faulting episode gets **no ledger and no checkpoint**, and the other
  episodes were never dispatched and have none either — so **every one of the thirty is
  re-runnable**, and `PROCESS.md` §6b provides the procedure by name: *"the retry is a numbered
  attempt in the same directory."* The operator has already exercised it three times tonight.
  **`INC-159`'s real cost was 56,855 tokens, an incident entry and a numbered attempt — not
  twenty-nine episodes.** The true trade is:

      floor absent : 1 episode re-runnable from turn 1, + 1 incident + 1 numbered attempt
      floor present: 1 episode PERMANENTLY frozen at N of 20 turns, in the published
                     denominator, with no recourse inside the protocol

  `CheckpointStore.completed()` reads only filenames, `publish` refuses a differing rewrite,
  there is no delete and no `force`, and `evals/` deletion is **operator-only**. **So the
  degradation is irreversible by any session.**
- ⚠️ **AND THE DEGRADATION RUNS IN THE DIRECTION THE FROZEN ARTEFACT NAMES.** `HOLES.md:210`,
  frozen, says in terms: *"A truncated episode is one the attacker did not get to finish, so it
  is **less** likely to carry a breach."* **Quantified on the only real calibration episode
  there is:** its first touch of `pay_CANARYRECON` is `ledger_seq 9`, **`turn_index 8`** — the
  ninth of twenty turns. **An episode truncated at turn 3 has a structurally zero chance of
  carrying a probe breach, and still divides the denominator as if it were whole.**
- ⚠️ **THE RULING GIVES ONE ANSWER FOR TWO REGIMES.** For the **sweep** — 510+ episodes over
  11–17 hours, where losing the run is the catastrophe — booking is plainly right and one
  degraded episode is noise. For a **30-episode single-shot pre-registered calibration**, where
  a crash is *cheap and recoverable by a procedure the protocol already defines* and a booked
  truncation is *permanent and biases the published threshold*, the same choice is much harder
  to defend. **`Q-200` does not distinguish them.** That is raised as a question, not decided
  here.
- ⚠️ **THE COST THE RULING DID NOT PRICE:** a truncated episode is **counted in the denominator**
  (hard rule 11 requires it) while having had fewer turns in which to breach. The calibration's
  published quantity is *"arm-1 episodes containing at least one qualifying breach ÷ arm-1
  episodes attempted"*, so a 3-of-20-turn episode biases the observed rate **down** — and
  `HOLES.md` §3.5's rule is that a **low** observed rate sets a **low** threshold, **the
  direction that flatters this project's own run**. This is `INC-103`'s shape, and the driver
  already refuses to average tokens/episode over truncated episodes for exactly that reason.
  **Whether the threshold computation carries the same guard is not this floor's to decide** and
  is raised as a question.
- **An option the ruling did not enumerate:** book the **call** and continue the **episode**,
  rather than truncating it. Rejected here on the merits rather than left unsaid — the attacker
  would have to be shown *something* for that turn, and anything shown is content the other arms
  were not shown, which contaminates §10.1's no-differential requirement. **Truncating is
  right.**

**Finding: the disclosure is factually accurate and materially incomplete.** It states the
behaviour and not its two consequences — that the degradation is **irreversible**, and that it
biases the published rate in the direction `HOLES.md` names. **The choice is right for the sweep,
which is what C14 gates**; whether it is right for a single-shot calibration is an architect's
question and is raised as one. **Not a defect in this floor, and not a reason for the FAIL.**

## 1.7 `KeyboardInterrupt` AND `SystemExit` — VERIFIED BY EXECUTION, NOT BY READING

    KeyboardInterrupt    -> KeyboardInterrupt    passthrough=True  booked=0  calls_settled=0
    SystemExit           -> SystemExit           passthrough=True  booked=0  calls_settled=0
    GeneratorExit        -> GeneratorExit        passthrough=True  booked=0  calls_settled=0
    TimeoutError         -> LaneStopped(UNEXPECTED_ERROR)
                            booked=[(('gemma-26b', 0, 'ERROR'), {'error_type': 'TimeoutError'})]
                            calls_settled=1  stopped=False  rate_limited=0
    LaneStopped(429)     -> LaneStopped(RATE_LIMIT_429)  calls_settled=0

⚠️ **CONFIRMED, AND EXTENDED.** The build session asserted two `BaseException` subclasses; a
third, `GeneratorExit`, also passes through untouched, and nothing is booked for any of them.
**A Ctrl-C still stops the sweep.** The same run confirms the ruling's two negatives directly:
the lane does **not** stop (`budget.stopped is False`), no 429 is recorded, and the callable is
invoked exactly once.

## 1.8 THE TWO CHANGED TESTS — ASSERTION COUNTS RE-DERIVED WITH `ast`, NOT `grep`

Qualified names (`Class.method`), `ast.Assert` nodes, and `pytest.raises` attribute accesses,
over `git show 67839d0:` and `git show b01edaa:`:

    tests/test_c11_runner.py   functions     68 ->  68   (claim 68->68     OK)
                               ast.Assert   226 -> 228   (claim 226->228   OK)
                               pytest.raises 24 ->  24   (claim 24->24     OK)
                               REMOVED 0    ADDED 0    LOST AN ASSERTION 0
                               CHANGED test_every_declared_cause_prints_even_at_zero   2 -> 4

    tests/test_c12_driver.py   functions    135 -> 138   (claim 135->138   OK)
                               ast.Assert   246 -> 253   (claim 246->253   OK)
                               pytest.raises 40 ->  40   (claim 40->40     OK)
                               REMOVED 0    LOST AN ASSERTION 0
                               ADDED _KilledAfter.{attacker_calls, complete_attacker, complete_judge}
                               CHANGED test_a_BucketError_is_BOOKED_AS_ITS_OWN_NAMED_CATEGORY...
                                                                                       7 -> 14

⚠️ **EVERY FIGURE THE BUILD SESSION REPORTED FOR THE TWO CHANGED FILES REPRODUCES EXACTLY, AND
NOT ONE FUNCTION LOST AN ASSERTION OR A `pytest.raises`.** Hard rule 6 is satisfied on both.

**The `UNFINISHED_CAUSES` flip is provably meaningful**, measured against the committed blobs:
`67839d0:tests/test_c11_runner.py:872` is `assert len(ep.UNFINISHED_CAUSES) == 8`; `b01edaa`
line 886 is `== 9`, and `== 9` is red on the pre-ruling code because
`git show 67839d0:src/whetstone_gate/runner/episodes.py | grep -c "^UNEXPECTED_ERROR"` is **0**.
Two assertions are **added** beside it — membership at line 887, no-duplicates at line 888 — and
none removed. **Strengthened, not weakened.**

⚠️ **ONE FIGURE IN THAT TABLE IS STALE, AND IT IS THE NEW FILE'S.** The report claims
`tests/test_c14_unexpected_escape.py` is *"NEW FILE 25 functions, 26 ast.Assert, 4
pytest.raises"*. Measured at `b01edaa`: **27 functions, 29 `ast.Assert`, 5 `pytest.raises`**.
Measured at `0cfc231`: **25 / 26 / 4 — exactly the reported figures.** The table was taken at
Gate 2 and not re-taken after `b01edaa` added
`test_the_floor_NEVER_RELABELS_AN_ALREADY_BOOKED_LaneStopped` (+2 functions, +3 asserts, +1
`pytest.raises`). The same report's §6 says *"8 tests"*, which is `b01edaa`'s count — **so the
report is internally inconsistent by one commit.** The direction is **under**-reporting.
A smaller inaccuracy in the same table: its caption says *"QUALIFIED names (Class.method)"*, but
the figures are the **raw `FunctionDef` node count including nested closures** — the qualified
non-nested counts are 67 → 67, 109 → 112 and 20. **The raw numbers are correct; the caption
describes a different measurement.**

## 1.9 ⚠️ WHAT THE NEW TEST FILE CANNOT SEE

Two measured facts about `tests/test_c14_unexpected_escape.py`:

1. ⚠️ **IT IS ARM 1 ONLY.** `_run_the_matrix_with` calls `pilot_module.load_pilot(arm="1")`.
   Arm 1 has no gate and no judge, so **no test in the file ever drives a judge-lane
   `_MeteredCall`, and none ever reaches `gate.decide`.** The floor's headline property — *"the
   run continues"* — is asserted only on the one arm where it is true.
2. ⚠️ **THE FAKE TRANSPORT'S REPLY DOES NOT PARSE, SO THE EXECUTOR NEVER GETS PAST ITS FIRST
   BRANCH.** Measured: `driver/protocol.py:parse_call("the reply").parsed` is **False** —
   *"no JSON object naming a 'tool' was found in the reply"*. So in both end-to-end tests every
   turn is counted `unparsed` and returns immediately, and `candidate_action`, `gate.decide`,
   `world.call` and `ledger_build.append_call` are **never executed**. Independently
   corroborated: driving the same fixture text against **arm 2** produces **0** judge calls,
   where the control with a parseable tool call produces **400**.

**Instrumented, on the file's own fixture, running its own headline test:**

    arm=1  judge_lane=gemma-26b  episodes=20  transport calls=385  faults=1
    parse_call=384  unparsed=384  off_surface=0  decide=0  world.call=0  append_call=0
    aggregate EpisodeCounts: attempted=384  decided=0  unparsed=384  off_surface=0
    judge_calls=0  judge_tokens=0

**384 of 384 turns are `unparsed`.** The gate, the world and the ledger are never touched.
⚠️ **AND THE FIVE UNIT TESTS DO NOT MAKE UP FOR IT.** They build a bare `_MeteredCall` through
`_metered()`, which passes `lane="gemma-26b"` — **which is the judge lane** — but there is no
judge, no `ModelGate` and no `gate.decide` anywhere in the file. **The lane name creates the
appearance of judge coverage without any.**

**Consequence:** `INC-159`'s `Systemic guardrail` field says the test *"injects a bare
`RuntimeError` … partway through a multi-episode matrix, and asserts that `execute` returns"*.
That is true — **of an arm-1 matrix of all-unparsed episodes.** No test anywhere in `tests/`
drives a `LaneStopped` out of a **judge** call on a judged arm through `run_one_episode`, and no
test asserts that `execute` survives a fault on a judged arm.

## 1.10 WHAT IS CORRECT, RECORDED SO IT IS NOT MISTAKEN FOR UNEXAMINED

- The three named branches keep their distinct causes and distinct accounting; the floor is
  genuinely beneath them, and the `ast` walk proves the ordering.
- `UNEXPECTED_ERROR` is a ninth member of `UNFINISHED_CAUSES` and prints in the denominator
  including at zero — **observed in tonight's live calibration report**, which carries an
  `UNEXPECTED_ERROR : 0` line.
- The cause and outcome vocabularies are **disjoint** (`set() & set()` is empty), so `INC-160`'s
  confusion still fails loudly rather than silently.
- `INC-160`'s fix is right, and its reason for rejecting the alternative is right: widening
  `usage.OUTCOMES` would re-shape an append-only on-disk record to fix a call site.
- No retry, no backoff, no sleep, no new `config/` value; `config/` is byte-clean.
- Only `type(exc).__name__` is stored; a key-shaped message is not booked.
- The `b01edaa` guard is not dead code with no test: it is asserted, and §1.5 could not defeat
  it in the direction it was written for.

## 1.11 OBSERVED AND NOT TOUCHED

⚠️ **THE CALIBRATION WAS NO LONGER RUNNING WHEN THIS REVIEW MEASURED IT, AND IT COMPLETED.**
The prompt states it was live at `19:14Z`. At `2026-09-04T19:34:45Z` there was **no driver
process**; the last row of `evals/usage/gemma-26b-2026-09-04.jsonl` is
`{"outcome": "RATE_LIMITED", "total_tokens": 0, "utc": "2026-09-04T19:15:58Z"}`; and
`evals/cal/run-attempt3-20260904T191123Z.log` **ends with a complete report and a reconciling
denominator** — 30 attempted, 0 completed, 1 truncated (55,887 tokens, 11 of 20 turns), 29 never
started, all under `RATE_LIMIT_429`, `USABLE TO SELECT N: False`. ⚠️ **THIS SESSION DID NOT
TOUCH IT, DID NOT RE-RUN IT AND DOES NOT RULE ON IT** — under `PROCESS.md` §6b whether that is
*the* run is the architect's to say. It is recorded here only because a review that measured
this tree at `19:34Z` must say what it saw.

⚠️ **IT IS ALSO WHY §1.2 IS NOT HYPOTHETICAL.** A 429 on `gemma-26b` fired **for real, tonight**.
On arm 1 it produced the report above. On arms 2, 2S or 3 — the same lane, because the gate judge
shares it — it would have produced `DenominatorError` and no report at all.

⚠️ **A CONCURRENT SESSION IS LIVE IN THIS WORKING TREE** (§1.1), with uncommitted edits to
`src/whetstone_gate/driver/run.py` and `src/whetstone_gate/runner/buckets.py`, and two `pytest`
invocations of its own running during this review. **Nothing of that was touched.** The untracked
`du.exe.stackdump`, `grep.exe.stackdump`, `rev/` and `verify.py` were present at this session's
start and are not this session's.

---

# PART II — PHASE 2. JUDGEMENT.

⚠️ **Part I was written and sealed before this section existed.** Nothing in Part I was reopened.

## 2.1 ⚠️⚠️ BLOCKER

### `B-1` — THE FLOOR BOOKS THE ESCAPE AND THE RUN DIES ANYWAY, ON THREE OF THE FIVE ARMS

**Severity: BLOCKER.** **Evidence: §1.2, measured on the committed `b01edaa` tree.**

`Q-200`'s ruling is *"ANY exception escaping the model call is BOOKED AS A COUNTED, NAMED OUTCOME
**AND THE RUN CONTINUES TO THE NEXT EPISODE**"*. On arms **2, 2S and 3** the first half holds and
the second is false: the floor books its usage row, raises `LaneStopped(UNEXPECTED_ERROR)` from
inside `gate.decide`, and `driver/episode.py:837`'s `executor.counts.reconcile()` — one statement
past the handler that catches it, and outside the floor — raises `DenominatorError`, because the
abandoned turn was counted `attempted` and never categorised. **`execute` never returns. No
report. No denominator. Every remaining episode unattempted.** That is `INC-159` verbatim, one
frame out.

**Why it is a BLOCKER and not a HIGH:**

1. **It is on the sweep's path, and the sweep is what C14 gates.** `PROCESS.md` §12's RUN-3 is
   *"M-ADV (mock world, **five arms**, reference attacker) + T-NEG (**five arms**…)"*, depending
   on C14. `CONTEXT.md` §13.4's block table is `5 arms × N`. **Three of those five run a gate
   judge.**
2. **The trigger is not exotic — it is the ordinary end of a lane.** A **429** takes this path.
   A **token- or call-ceiling** stop takes this path. Hard rule 12 exists to make both of those
   *"STOP and report"*; on a judged arm they crash instead.
3. **It fired for real tonight, on the one arm where it is survivable.** The calibration's
   attempt 3 ended on a `gemma-26b` 429 at `19:15:58Z` and printed a clean reconciling report —
   **because it is arm 1**. The gate judge for arms 2/2S/3 is on that same lane.
4. **The floor makes it reachable by every exception type**, where before only the three named
   ones and the two budget stops could reach it.

**Why it is nevertheless NOT a regression, stated plainly because severity should not be
inflated:** §1.2.3 hashes every frame on the path and **only `_MeteredCall.run` changed**. A
judge-side 429 killed the run identically before `0cfc231`. **The FAIL is for shipping the
property as delivered when it is false on the sweep's majority, with a test suite that cannot
see it — not for breaking something that worked.**

⚠️ **THIS REVIEW DOES NOT FIX IT AND DOES NOT PRESCRIBE THE FIX.** The obvious shapes — count the
abandoned turn in a category, or roll `attempted` back, or catch and re-book at
`run_one_episode` — each **change a printed count** (`turns attempted`), which makes it
**Class A** under hard rule 2. It is raised as a question in §2.7, and no line of `src/` was
touched.

## 2.2 HIGH

### `H-1` — THE FLOOR CAN RAISE WHILE BOOKING, WHICH IS `INC-160` INSIDE THE FIX FOR `INC-160`'s CLASS

**Severity: HIGH.** **Evidence: §1.4.**

`self.on_usage(...)` is the third statement of the floor's `except` clause. It reaches
`runner/usage.py:UsageLog.append`, whose final act is `path.parent.mkdir(...)` and
`path.open("a", ...)`. **A full disk, a Windows file lock or a permission fault raises `OSError`
from inside an `except` clause, where no sibling handler can see it** — and it escapes `run`,
`run_one_episode` and `execute` exactly as the exception the floor was installed to contain.
⚠️ **PROVED BY EXECUTION, TWICE** (§1.4): a read-only usage file yields `PermissionError` and an
`evals` path that is a file yields `FileExistsError`, both escaping `_MeteredCall.run` as
**non-`LaneStopped`**, past `run_one_episode`'s only handler and past a dispatch loop that has no
`try` at all. `refuse_if_secret_bearing` adds a second, narrower path, now that
`type(escaped).__name__` is new content in that row.

**HIGH rather than BLOCKER because** the same exposure is in all three sibling branches and on
the success path (`episode.py:383`, `:405`, `:446`, `:537`), so an unwritable usage log already
kills a run on the happy path; the floor did not create it. **HIGH rather than MEDIUM because**
this is the precise mechanism `INC-160` was written about, in the commit that fixed `INC-160`, in
the handler whose stated job is to be the layer beneath which nothing escapes. **A floor that can
raise while booking is not a floor.**

### `H-2` — THE TEST SUITE IS STRUCTURALLY UNABLE TO SEE `B-1`, AND THE GUARDRAIL CLAIM IS BROADER THAN WHAT IS ASSERTED

**Severity: HIGH.** **Evidence: §1.9.**

`tests/test_c14_unexpected_escape.py` drives `load_pilot(arm="1")` only, and its fake transport
returns text that `parse_call` refuses — measured — so **every turn of both end-to-end tests is
counted `unparsed`, and `gate.decide`, `candidate_action`, `world.call` and
`ledger_build.append_call` are never executed.** The floor's headline property is therefore
asserted only on the arm with no judge, in episodes that never reach the gate. **No test anywhere
in `tests/` drives a `LaneStopped` out of a judge call on a judged arm.**

`INC-159`'s `Systemic guardrail` field describes the test as injecting a fault *"partway through
a multi-episode matrix"* and asserting *"that `execute` returns"*. That is true of the matrix it
runs. **It is the reason `B-1` shipped**, and it is the same species as `INC-160`'s own `Missing`
field — *"a test whose double is more permissive than the real collaborator proves the caller
compiles, not that the system works."* Here the **matrix** is more permissive than the sweep.

⚠️ **THE `RuntimeError` ASYMMETRY IS A GOOD IDEA AND IS NOT WHAT IS WRONG.** The second test does
what the build session says it does, and would go red if the floor were narrowed back to a list.
The gap is in the **arm** and the **turn shape**, not in the exception type.

## 2.3 MEDIUM

### `M-1` — THE FLOOR PRESERVES THE CAUSE AND DISCARDS THE DIAGNOSIS

**Severity: MEDIUM.** **Evidence: §1.5.** `raise ... from None` drops the traceback. `INC-159`'s
own `Missing` field says that abort was *"fully diagnosable in about four minutes"* — **from the
traceback**; a usage row's `error_type` names the type and no frame. On judged arms the surfaced
exception is `DenominatorError: turn counts do not reconcile`, naming neither the timeout nor the
transport. **The suppression of the *message* is right and `INC-147` justifies it; the loss of
the *frame* is collateral and was not weighed.**

### `M-2` — A BOOKED TRUNCATION ENTERS THE VOID-THRESHOLD DENOMINATOR HAVING HAD FEWER TURNS TO BREACH, AND THE BIAS FLATTERS US

**Severity: MEDIUM.** **Evidence: §1.6.** The floor's whole purpose is to convert run-killing
faults into counted truncations, which is right **for the sweep**. Three consequences it did not
price:

1. **The degradation is irreversible.** `CheckpointStore.completed()` reads only filenames,
   `publish` refuses a differing rewrite, there is no delete and no `force`, and `evals/`
   deletion is operator-only. A booked truncation is frozen into the denominator forever.
2. **A crash was never the disaster the disclosure implies.** A crash writes no checkpoint, so
   **every** episode stays re-runnable and `PROCESS.md` §6b's numbered attempt recovers them.
   The real trade is *"one re-runnable episode + one incident"* versus *"one episode permanently
   frozen at N of 20 turns"* — **not** *"one versus twenty-nine"*.
3. **The bias runs where the frozen artefact says it runs.** `HOLES.md:210`: *"A truncated
   episode is one the attacker did not get to finish, so it is **less** likely to carry a
   breach."* **Measured on the only real calibration episode: its first `pay_CANARYRECON` touch
   is `turn_index 8` of 20**, so an episode truncated at turn 3 cannot carry a breach and still
   divides as if whole. A depressed rate sets a **lower** void threshold — **the direction that
   flatters this project's own run**, which this repository treats as a defect by default.

The driver already refuses the analogous average for exactly this reason (`INC-103`'s shape) and
printed that refusal tonight. **Whether the threshold computation carries the same guard, and
whether `Q-200`'s single answer fits both the sweep and a single-shot calibration, is owed**
(§2.7). **MEDIUM and not HIGH because for the sweep — which is what C14 gates — the floor's
choice is right, and because the remedy is a ruling rather than a code change.**

### `M-3` — `run.py:840`'s `int(key.seed_or_task)` CANNOT DRIVE A TASK-KEYED BLOCK, AND RUN-3 NAMES TWO

**Severity: MEDIUM, LATENT.** **Evidence: §1.3.2 site 20.**
`runner/episodes.py:160` says in terms that `seed_or_task` *"is a string in every block,
deliberately"* — seeds for mock-world blocks, **task ids for task blocks** — and
`benign/manifest.py:193` already builds `seed_or_task=f"{domain}-{task_id}"`.
`driver/run.py:execute` does `seed = int(key.seed_or_task)` unguarded. **Latent today**, because
`driver/` has only `cal.py` and `pilot.py` and both emit `str(seed)`. **RUN-3 is M-ADV + T-NEG +
T-FP**, and T-NEG and AD-CMP are task-enumerated. Either another entry point is intended, or this
refuses. **Raised rather than assumed** (§2.7).

## 2.4 LOW

### `L-1` — THE AST-EXACT TABLE'S FIGURES FOR ITS OWN NEW FILE ARE ONE COMMIT STALE

**Severity: LOW.** **Evidence: §1.8.** Reported *"25 functions, 26 ast.Assert, 4 pytest.raises"*;
at `b01edaa` it is **27 / 29 / 5**, and 25 / 26 / 4 is exactly `0cfc231`. The same report says
*"8 tests"*, which is `b01edaa`'s count, so the record disagrees with itself by one commit.
⚠️ **The direction is UNDER-reporting, and the two CHANGED files' figures are exact**, so hard
rule 6's argument is untouched. It is recorded because the report's own method is *"AST-EXACT …
NEVER `grep -c assert`"*, and `CLAUDE.md` §6.1 makes that file the record.

### `L-2` — "A TYPE NAME IS A PYTHON IDENTIFIER AND CANNOT CONTAIN A CREDENTIAL" IS TRUE, AND IS NOT WHAT THE SCAN TESTS

**Severity: LOW.** **Evidence: §1.4(4).** `runner/redaction.py:49` refuses any string beginning
`gsk_` or `AIza`, or containing `_API_KEY`. All three are legal inside an identifier, so the
comment guarantees more than the code does. Contrived, and worth one word in the comment rather
than a change to the code.

## 2.5 NOT THIS CHUNK'S — RECORDED BECAUSE IT LANDS ON THE SAME SWEEP

⚠️ **`OF-240` IS A SECOND, INDEPENDENT "SEVENTEEN HOURS AND NO REPORT" PATH ON THE JUDGED ARMS,
AND IT IS ALREADY OPEN AND ALREADY PREDICTED.** `run.py:206`'s `attacker_tokens` raises
`RunRefused` when a **resumed** run's arm is in `JUDGED_ARMS`, and `render()` →
`_measurement_lines` calls it **unguarded** (only `PilotError` from `decide_n` is caught). So a
resumed judged arm finishes every episode and then raises instead of printing.
`evals/cal/RUN_DECLARED.md` says it in terms: *"`OF-240` IS NOT CLOSED BY THIS — it stays OPEN
and will fire the first time a **judged** arm is resumed."* The sweep spans a day boundary **by
design**, and `PROCESS.md` §12 gates RUN-3 on day-resume. **Not raised as a new finding and not
carried to `OPEN_FINDINGS.md`** — it is already there. It is named here because with `B-1` the
judged arms now have **two** independent ways to spend a lane-day and print nothing.

## 2.6 VERDICT

### **FAIL.**

**No tag was cut.** This session created no tag, moved no tag, rewrote no history, and changed no
line of `src/`, `tests/`, `config/`, `evals/` or any frozen artefact.

⚠️ **THE FAIL IS NOT FOR THE FLOOR'S DESIGN.** The ruling is implemented as written for the frame
it names; the three named branches keep their causes; the `LaneStopped` guard is correct and I
could not defeat it; `KeyboardInterrupt`, `SystemExit` and `GeneratorExit` pass through, proved by
execution; both changed tests were strengthened and neither weakened, proved by `ast`;
`INC-160`'s fix and its rejected alternative are both right. **On arm 1 — the arm the calibration
runs — the floor is a strict improvement, and tonight's completed report is what that looks
like.**

**The FAIL is for `B-1`:** the chunk's delivered property is *"the run continues"*, and on three
of the five arms the sweep runs, it does not — for a 429, for a ceiling stop, and for every
exception the floor was built to contain. **`H-2` is why nobody saw it.**

**What a FIX session owes, in order:**

1. **`INCIDENTS.md` first**, before a line of code, in hard rule 13's format, with `Diagnosis`
   and `Missed` filled in. `Missed` has an obvious candidate: `Q-202` enumerated four uncovered
   sites and **none of them is inside `run_one_episode`**, one statement from the handler.
2. **A ruling on `B-1`'s accounting** (§2.7), because every available fix moves a printed count.
3. **`B-1`, then `H-1`, then `H-2`** — and `H-2` is not optional, because a fix for `B-1` proved
   only on arm 1 would be the third fix in this class to close the instance instead of the class.
4. **`L-1`** is one line in a record and costs nothing.

⚠️ **NOTHING SHOULD BE FIXED WHILE A SINGLE-SHOT RUN IS IN FLIGHT.** At `19:34Z` no driver
process was running (§1.11), but that is the operator's call and not this session's.

## 2.7 QUESTIONS OWED — THREE, RECORDED AS `Q-207`, `Q-208`, `Q-209`

⚠⚠ **THIS APPEND WAS DESTROYED ONCE AND WAS REDONE.** The first append (token row + `Q-206`…
`Q-208`) passed a tail-byte assertion against `HEAD` and was then **overwritten wholesale** by the
concurrent **C14 ABORT 3** session (`7d4e2fa9`) writing `QUESTIONS.md` from its own earlier read,
which also took **`Q-206`**. **Nothing of theirs was edited or renumbered**; these three renumber
**beneath** `Q-206`, exactly as `INC-159`/`INC-160` did. `INC-137`'s hazard, from the other side.
⚠️ **`Q-208` DEFERS TO THEIR `Q-206`(d)** rather than competing with it — that entry asks the
threshold question better, about the real 11-of-20-turn episode. What `Q-208` adds is the
`turn_index 8` measurement and the two-regimes question.
⚠️ **`QUESTIONS.md` IS COMMITTED HERE CARRYING THAT SESSION'S IN-FLIGHT `Q-206` TEXT**, because a
session's token row must be committed with the commit that uses it or `make check-roles` E1 goes
red on a token *"that was never issued"* (`INC-141`'s trap, which `7ae1f83` had to clear once
already). **Not one byte of their text was changed.**

- ⚠️ **`Q-207` — `B-1`'s accounting, Class A.** When a turn is abandoned between `attempted += 1` and its
  categorisation, what should the record say? Every available fix moves `turns attempted` or adds
  a category, and hard rule 2 makes that the architect's.
- **`Q-208` — a truncated episode in the void-threshold denominator** (`M-2`) — the driver refuses to
  average tokens over truncated episodes; does the threshold computation carry the same guard,
  and in which direction does it err?
- **`Q-209` — task-keyed blocks through `driver/run.py:execute`** (`M-3`) — is `execute` intended to drive
  T-NEG and AD-CMP, whose keys are task ids rather than integer seeds?

## 2.8 WHAT THIS REVIEW DID NOT DO

- It did **not** run the full `pytest` suite. A concurrent session was running two suites of its
  own against this tree, and `src/` was dirty with that session's uncommitted work (§1.1); a
  suite total measured across that would attribute reds wrongly, which is `OF-259`'s exact trap.
  **Every claim above is a targeted first-hand measurement instead**, and the two that matter for
  hard rule 6 are `ast` walks over committed blobs.
- It did **not** re-run, interpret or rule on the calibration.
- It did **not** touch the concurrent session's work, `evals/`, or any frozen artefact.
- It spent **no provider tokens** and made **no provider call**.
