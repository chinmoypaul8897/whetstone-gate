# STATUS.md — the single glance-state

**One row per chunk. The review-history column is APPEND-ONLY and is never erased or rewritten.**
`C7: built → FAIL(1) → fixed → PASS(2)` stays readable forever. That is the point of it.

**Status values:** `todo` · `in-flight` · `built (unreviewed)` · `in-review` · `FAILED` ·
`fixing` · **`PASS`** (tagged `cN-pass`).
**Review types:** `full` = personas 1 + 2, two sealed phases, a committed reimplementation, ≥8
mutants · `code` = persona 2 only, ≥4 mutants · `submission` = persona 3 + persona 1.
**No chunk is `PASS` without `docs/reviews/ARCHITECT_CHECK_<N>.md`.** An unrecorded gate is not a
gate.

*Last updated: 2026-08-31, end of the **ARCH WORLD-GENERATION** session (`0811c64a`) — specification,
config, one architect-authored golden and four question-log entries; **no logic**. Before it: the
**C0 FIX** session (`c9521aac`), which ran concurrently with the **C1 BUILD** session (`20cd5b79`) as
pair **P-01**, and before them the ARCHITECT-ARTEFACT LANDING session (`e210c6f5`).*

⚠️ **UPDATE, 2026-08-31, ARCH WORLD-GENERATION (`0811c64a`): `CONTEXT.md` IS v1.3, GOLDEN 7 EXISTS,
AND C2 IS UNBLOCKED — TO BE BUILT AND REVIEWED, NOT TO BE TAGGED.**
`CONTEXT.md` §8.6 **did not determine a world**: it fixed no draw order, no exact log-uniform
formula, no id format, no non-amount field and no status-assignment rule, so `PROCESS.md` §5.2's
**golden 7 could not be authored from it**. New **§8.6a** states the algorithm exactly; §8.6's
constants table gains **nine** rows and `config/protocol.yaml` the matching keys; the tripwire
registry gains nine rows; and **`tests/goldens/world_seed_2001.json`** is committed — SHA-256
`649e54ca446e8308f5fcd69ebba56eda5faea8d58246be7277cdb8b42227dd2b`, 4,879 bytes, derived by the
**architect** independently of any project code. **`QUESTIONS.md` Q-019** is the ruling.
🚩 **OPERATOR ACTION OWED, AND IT GATES THE TAG CHAIN.** Q-019 is **Class A** and carries the
operator's own three conditions. Two of them bind what happens next:
**(ii)** the ruling is **explicitly re-opened for the operator's review before `prereg-v1`** — it
does not pass silently into the frozen set because it was written overnight; and
**(iii)** ⚠️ **NO CHUNK WHOSE NUMBERS DERIVE FROM THIS ALGORITHM MAY BE TAGGED `cN-pass` UNTIL THE
OPERATOR HAS CONFIRMED IT.** That is **C2 and C14 directly**, and every chunk downstream of the
world. **Build on it and review against it; do not tag.**
Also landed: **two false attributions corrected** in `CONTEXT.md` (§2's *"none is a key"* about
`create_refund`, which was **false**, and §6's A4 doc-source line, whose quoted string is on
**neither** page it credited) — both found by **C1 BUILD**, both re-verified by the architect at
source. ⚠️ §2's was the **fourth** false claim about third-party behaviour to reach this
specification; **INC-05** is the entry that made that class a rule. **§9.2's definition of S2 was NOT
touched** — that is **Q-017**, OPEN, and the operator's.

⚠️ **UPDATE, 2026-08-31, C0 FIX (`c9521aac`): ALL FOUR BLOCKERs ARE CLOSED AND C0 IS `fixing →
fixed (unreviewed)`. THERE IS STILL NO `c0-pass` TAG AND THE TAG CHAIN HAS STILL NOT STARTED** — a
fix session does not certify its own work, and only a REVIEW session cuts that tag. The paragraph
below is left standing, unedited, because it is the record of what was found; what follows it in the
C0 row is the record of what was done about it, with the review's own §4 evidence re-run old beside
new. **A fresh adversarial review of C0 is owed before anything is tagged.**

⚠️ **C0 IS `FAILED`. NO `c0-pass` TAG EXISTS AND THE TAG CHAIN HAS NOT STARTED.** Four BLOCKERs, all
the same shape — a check that reports PASS over nothing: `check-roles` **E2 and E3 cannot fire at
all**; **D3, "the whole moat", is defeated by hard rule 8's own named spike defect**; the **F group
reports `config/` complete over a `config/` missing `protocol.yaml`**; and **`make selftest`, the
pre-spend gate, flips GREEN when the key it guards is deleted.** Full evidence, all re-runnable:
`docs/reviews/REVIEW_C0.md`. **A FIX session is owed** — `INCIDENTS.md` entries first (hard rule 13),
then the four BLOCKERs, then a fresh review. Every dependent chunk (C1, C2, C3, C6, C11, C13, C15)
lists C0 as a dependency.

**Specification: `CONTEXT.md` v1.3.** See *Specification version* below — it matters because **C14 selects the N branch from §13.4 and writes it into `PROTOCOL.md` before the freeze.**

⚠️ **TWELVE RULINGS LANDED 2026-08-31** (`e210c6f5`): Q-001, Q-002, Q-003, Q-004, Q-005, Q-007,
Q-009, Q-010, Q-011, Q-012, Q-014, Q-015 are all **RULED**. Only **Q-006** and **Q-008** remain
OPEN, and both are **OPERATOR** actions, not architect rulings. ⚠️ **Q-014 was RAISED TO BLOCKER for
this fix cycle** — from C1 onward, E1 is the only thing standing between the log and an invented
credential. **`docs/reviews/ARCHITECT_CHECK_0.md` now exists** and **UPHOLDS C0's FAIL.**

---

## Chunks

| # | Date | Chunk | Review | Status | Review history (append-only) |
|---|---|---|---|---|---|
| **C0** | 30 Aug | Repo, toolchain, remote, canonical files, day-one setup | `code` | ⚠️ **fixed (unreviewed)** | built → completed (3 operator-owed items landed; Q-006 + Q-008 closed) → **REVIEW_C0_1 = FAIL** (`52f5307b`, 4 BLOCKERs; no tag) → **ARCHITECT_CHECK_0 committed** (`e210c6f5`, 31 Aug — **FAIL UPHELD**; B-01…B-04 each re-confirmed from source; §13.4 recomputed = MATCH; **no `c0-pass`**) → **fix owed** (`c9521aac`) → **FIXED, UNREVIEWED** (`c9521aac`, 31 Aug — all four BLOCKERs closed with the review's own §4 evidence re-run old-beside-new: **B-01** E2/E3 go `PASS/PASS` → `FAIL/FAIL` on §7a's two named violations; **B-02** attack forms 2, 3 and 4 go `PASS` → `FAIL` (form 1 already failed); **B-03** `config/` minus `protocol.yaml` goes `14 passed, 0 failed, exit 0` → `14 passed, 1 failed, exit 1`; **B-04** `make selftest` with `camel_comparator:` deleted goes `2 passed` (GREEN) → `1 failed, 1 passed` (RED), and with `lanes.yaml` deleted the operator gate goes `1 passed` → `1 failed`. Plus **A5** (2 branches, closes **OF-01** and is **INC-13**'s guardrail), **E5** + a 4-SHA exception list (Q-014, BLOCKER), the **empty** `MOAT_ALLOW_LIST` (Q-015), the **§8.6 → registry** direction with the **8** missing constants, and **OF-03/04/06/10 CLOSED** · **OF-02/09/11 updated, still OPEN**. **INC-13, INC-14, INC-15** written *before* any code changed; **INC-16** written when `check-roles` A3 caught this session writing CRLF. `make test` **61 → 116 passed**; `check-roles` **14/0/3 → 17 passed, 0 failed, 4 n/a, exit 0**; `make selftest` **still RED**, correctly. **52 kept probes, 46 of which fail against the pre-fix source.** ⚠️ **NO `c0-pass` TAG. Nothing is self-certified — a fresh review re-runs the evidence**) → **re-review owed** |
| **C1** | 30 Aug | `RAZORPAY_SEMANTICS.md` + `PROVENANCE.md` attack rows A1–A6 | `full` | **built (unreviewed)** | built (`20cd5b79`, 31 Aug — **71 rows, 0 `[UNFETCHED]`**; 10 pages + 2 pinned source trees fetched first-hand, each page fetched twice and byte-identical; **0 Razorpay pages changed since 2026-08-30**; **6 findings raised against this project's own records**, F-06 HIGH; **Q-016 / Q-017 / Q-018 owed**; **no `INCIDENTS.md` entry owed**) → **review owed** |
| **C2** | 30 Aug | World generator + **the probe planted** (`pay_CANARYRECON`) | `full` | todo | ⚠️ **UNBLOCKED TO BUILD, 31 Aug** (`0811c64a`) — its golden and its specification both now exist, and neither did before. `CONTEXT.md` **§8.6a** states the generation algorithm exactly (mulberry32 step; `u` as the exact rational `raw/2^32`; the amount in `decimal.Decimal` at `prec=50`; **eleven** draws, the probe consuming none; positional status; sha256 ids; `created_at`; the six-template notes pool with its **deliberate decoy**; return order), and **`tests/goldens/world_seed_2001.json`** is committed — SHA-256 `649e54ca…dd2b`, 4,879 bytes, **architect-derived independently of any project code**, cross-checked against two `mulberry32` formulations. Ruling: **Q-019**. 🚩 **NOT UNBLOCKED TO BE TAGGED — Q-019 (iii): no chunk whose numbers derive from this algorithm may be tagged `cN-pass` until the OPERATOR has confirmed the ruling.** Build on it, review against it, **do not tag**. ⚠️ Two limitations are published with it, not hidden: `pay_CANARYRECON`'s **id shape** biases CANARY-B reach **upward** (§10.1 fixes that id), and **seed 2001 is one of only four in 2001–2050 that cannot breach E2 by refunds alone** — recorded so it is not later read as a defect. C0 remains a dependency and is still `fixed (unreviewed)` |
| **C3** | 30 Aug | τ² adapter A — the 34/164 must-not-write enumeration, the T-FP id list | `full` | todo | — |
| **C4** | 30 Aug | World semantics, the five-tool surface, the typed harm record, the spend-free self-test | `full` | todo | — |
| **C5** | 30 Aug | τ² adapter B — `HalfDuplexAgent` + the Gemini 3.5 Flash Lite user simulator | `full` | todo | — |
| **C6** | 30 Aug | Attacker loop — policy-blind, sliding-window context | `full` | todo | — |
| **C7** | 31 Aug | Ledger — append-only, hash-chained ⚠️ **the seeded-defect chunk** | `full` | todo | — |
| **C8** | 31 Aug | Scorer — deterministic replay, E1–E3 / S1 / S2 / S2-amt / S3 / S4 | `full` | todo | — |
| **C9** | 31 Aug | Gates — arms 1, 2, 2S, 3, 4 as five modules behind one interface | `full` | todo | — |
| **C10** | 31 Aug | Probe machinery + the statistics module + the four non-use tests | `full` | todo | — |
| **C11** | 31 Aug | Runner — lane-aware scheduler, token buckets, day-resumable | `full` | todo | — |
| **C12** | 31 Aug | Benign solver + the 30 benign scenarios + the paired-FP harness | `full` | todo | — |
| **C13** | 31 Aug | `src/camel_comparator/` — CaMeL, unmodified, on AgentDojo banking | `full` | todo | — |
| **C14** | 31 Aug | ⚠️ **THE FREEZE** — `probe-v1`, pilot, calibration, `prereg-v1`, the external witness | `full` *(verification)* | todo | — |
| **C15** | 31 Aug | Attacker-strength ladder harness + launch | `code` | todo | — |
| **C16** | 1 Sep | AgentDojo banking adapter (AD-CMP) | `full` | todo | — |
| **C17** | 1 Sep | `docs/render/` — the replay renderer (video RACE beat + the readable audit log) | `full` | todo | — |
| **C18** | 2 Sep | `RESULTS.md` + `make eval` | `full` | todo | — |
| **C19** | 3 Sep | README + architecture + PROVENANCE final pass + Agent-Ready conventions | `full` | todo | — |
| **C20** | 3 Sep | The video | `code` + `submission` | todo | — |
| **C21** | 4 Sep | The submission pack, the history secret scan, the visibility flip | `full` + `submission` | todo | — |

---

## Operator runs and audits

These are not chunks — they execute in the **operator's terminal**, never inside a session
(`PROCESS.md` §1). Listed here because they are plan items with their own done-when.

| # | Date | Run | Audited by | Status |
|---|---|---|---|---|
| **RUN-1** | 31 Aug 16:30–18:00 | The 90-minute CaMeL branch test | inside C13's review | todo |
| **RUN-2** | 31 Aug from 23:30 | Ladder L1 + L3, window 1 | SWEEP-AUDIT-1 | todo |
| **RUN-3** | 1 Sep 08:00 → | **Sweep day one** — M-ADV, T-NEG, T-FP begins, ladder window 2 | SWEEP-AUDIT-1 | todo |
| **SWEEP-AUDIT-1** | 1 Sep 22:00–23:00 | 🔍 persona-1 **denominator audit** over day one's output | *is itself a `full` review* | todo |
| **RUN-4** | 2 Sep 08:00 → | **Sweep day two** — M-BEN, T-FP, AD-CMP, CaMeL, ladder window 3 | inside C18's review | todo |
| **SUBMIT** | 4 Sep by 18:00 IST | 🚩 Operator action. **Gated on `REVIEW_21` = PASS** | — | todo |

---

## Specification version

`CONTEXT.md` is **the law** and is **not** a frozen artefact — `PROCESS.md` §6 leaves it amendable
until `prereg-v1` exists, and it does not. Every amendment is a numbered row in its own change log
and a row here. **Amendments are architect-authored only.**

| Version | Date | Sections touched | Ruling | Session |
|---|---|---|---|---|
| **v1.0** | 2026-08-30 | — (initial copy of the audited `PROJECT_SPEC.md`) | — | C0 |
| **v1.1** | 2026-08-30 | **§13.4 only** — the two N=30 fallback projections, plus a per-branch component breakdown and the consequence note | **Q-013, UPHELD** | `WG-2026-08-30-CTX-13.4-A` (BUILD) |
| **v1.2** | 2026-08-31 | **§16** (the tree re-nested; the mingw path) and **§8.6** (eight constants added; the warning paragraph amended) | **Q-004 (OPTION 1)**, **Q-005 (Class C)**, and the architect's §8.6 finding in `ARCHITECT_CHECK_0.md` §5 | `e210c6f5` (BUILD, architect-artefact landing) |
| **v1.3** | 2026-08-31 | **NEW §8.6a** (world generation, stated exactly); **§8.6** (nine constants added); **§2** (the `create_refund` row's *"none is a key"*, which was false); **§6** (A4's doc-source attribution); **§9.2** (a one-line pointer to Q-017 — **S2's definition untouched**) | **Q-019 (RULED, Class A)** for §8.6a and §8.6; **C1 BUILD's findings F-06 and F-01** for §2 and §6, each re-verified by the architect at source | `0811c64a` (BUILD, ARCH world-generation) |

**What v1.1 changed, in one line:** *"~71M ≈ 37 h"* → **69.10M = 35.99 h** and *"−6M → ~34 h"* →
**59.30M = 30.89 h**. **The N=50 headline (76.90M / 40.05 h) was correct and is unchanged, and so
is the decision rule** — its thresholds are criteria, not projections. ⚠️ **Why it was worth a
session:** as published the reduction chain ran **40 → 37 → 34 h against a 32 h budget and never
reached its own budget**, with *"No other branch. No post-hoc adjustment."* leaving nothing to try;
corrected, the final rung lands at **30.89 h and fits**.

**What v1.2 changed, in one line:** **§16's tree is re-nested** so the eleven subpackages are drawn
as children of `whetstone_gate/` (Q-004 — the deciding fact is that tau2-bench installs a top-level
package named `tau2`, which a sibling layout would collide with); **§16's mingw path is corrected**
(Q-005); and **§8.6 gains eight constants**, two of which — the **gate-judge 1,500 tokens/call** and
the **benign-solver 50,000 tokens/episode** targets — were in **neither §8.6 nor `config/`**, which
§8.6's own sentence calls *a defect, and finding one is a review BLOCKER*. Both are load-bearing in
**every row of §13.4's arithmetic** and are added to `config/protocol.yaml` in the same amendment.
**No number §13.4 publishes moves; §13.4 itself is untouched.**

**What v1.3 changed, in one line:** **§8.6 did not determine a world** — it fixed no draw order, no
exact log-uniform formula, no id format, no non-amount field and no status-assignment rule — so
`PROCESS.md` §5.2's **golden 7 could not be authored from it**; **§8.6a now states the algorithm
exactly**, its nine constants are in §8.6's table and in `config/protocol.yaml`, and golden 7 is
committed. **Plus two false attributions corrected**: §2 claimed of `create_refund`'s five
parameters that *"none is a key"* — Razorpay documents `receipt` **as** an idempotency key — and §6
credited *"will settle the maximum amount possible and ignore amount parameter"* to two doc pages it
is **on neither** of (it is `settlements.go:231-232`, which **§2's own table cites correctly**).
⚠️ **Two load-bearing decisions inside §8.6a, both recorded in Q-019 rather than left implicit:** the
amount is computed in **`decimal.Decimal`, not binary float**, because libm `exp`/`log` may differ by
one ULP across platforms and near ₹1,50,000 one ULP flips the rounded paise integer — **the spec as
written would have shipped a world reproducible only on the machine that generated the golden**,
while hard rule 10 and §5.1 both *claim and test* a byte-identical one; and the notes pool carries a
**deliberate decoy**, because the attacker's own tradecraft paragraph says *"**SOME** describe
exceptions to normal limits"* and a single annotated payment would turn that paragraph into a
signpost, **making CANARY-A a reading test rather than a competence test**. **No published number
moves.** 🚩 **Q-019 is Class A and is RE-OPENED for the operator before `prereg-v1`; nothing built on
it may be tagged until he confirms it.**

⚠️ **AND A FINDING THAT WAS NOT A TYPO.** Q-005 reported `C:\MinGWin\mingw32-make.exe` as a prose
typo. At byte level it was a literal **`0x08` BACKSPACE control byte** standing where the `\b` of
`\bin` belongs, **present since v1.0 (`104fc74`)** — a backspace renders as nothing, so every viewer
displayed `MinGWin`. **It was the only C0 control byte in any tracked text file** and it is now gone.
**Neither `check-roles` A3 nor A4 could ever have seen it**: it is not a line ending, and the
worktree bytes and the blob agreed exactly, so §6a's fingerprint property genuinely held. This is
`INCIDENTS.md` **INC-10's `Missing` field** — *"nothing checks a tracked document's CONTENT"* —
arriving a second time, and **OF-01's proposed discriminator would NOT have caught it** (that one
keys on *"git calls it binary yet it holds no NUL"*; here git correctly calls `CONTEXT.md` text).
⚠️ **AN `INCIDENTS.md` ENTRY IS OWED FOR THIS.** It is not written here because the concurrent C0
FIX session owns that file tonight; the full rule-13 entry is in this session's report and in
`docs/sessions/c0-arch-landing-1.txt`.

⚠️ **The header's byte-identity claim against `PROJECT_SPEC.md` is SUPERSEDED from v1.1.**
`CONTEXT.md` has deliberately diverged, **in §13.4 only**. The v1.0 digest is retained, not deleted:
it is the record of the common ancestor and reproduces against commit `310488d`. **`CONTEXT.md`, not
`PROJECT_SPEC.md`, is the authority on the diverged section** — hard rule 4 names this file.

---

⚠️ **OWED TO THE ARCHITECT — a C21 done-when that does not exist yet.** `PROVENANCE.md` §1.5's
no-payment-method attestation is dated **2026-08-30** and is the **only claim in the frozen set that
can go stale without any file changing**: a card attached on 3 September would convert every
subsequent 429 into a bill, and this repository would still read *"NONE ATTACHED"*. `PROCESS.md`
§12.1's C21 row names the submission pack, the history secret scan and the visibility flip — and
**does not name a billing re-check** `[VERIFIED 2026-08-30]`. C0-COMPLETION did not add one, because
`PROCESS.md` was outside its scope fence. **Until the architect adds it, the re-confirmation depends
on somebody reading `PROVENANCE.md` §1.5.**

✅ **CLOSED 2026-08-31 (`e210c6f5`).** `PROCESS.md` §12.1's **C21 row now carries the billing
re-check** in its done-when: *"no payment method is attached to either provider account,
RE-CONFIRMED on 4 September and recorded in `PROVENANCE.md` §1.5 with the new date."* The paragraph
above is kept, not deleted, because it is the record of how long the gap stood and who found it.

---

## Tags

| Tag | What it fixes | Cut | Exists |
|---|---|---|---|
| `probe-v1` | `HOLES.md` alone — CANARY-A, CANARY-B, S4's window width (2) | **before** the pilot **and before** the calibration command runs | **no** |
| `prereg-v1` | the full frozen set: `INVARIANTS.md`, `PROTOCOL.md`, `HOLES.md`, `PROVENANCE.md`, `RAZORPAY_SEMANTICS.md`, **`config/`** | after the pilot and the calibration, **before every scored episode** | **no** |
| `cN-pass` | chunk N passed adversarial review | by the review session, on PASS only | **none yet** — ⚠️ **C0's review returned FAIL on 2026-08-30, so `c0-pass` was NOT cut. The chain has not started.** |

⚠️ **No calibration episode runs before `probe-v1` exists. No scored episode runs before `prereg-v1`
exists.** The freeze never moves earlier to fit the schedule; it is the one thing the project is
staked on.

---

## Pre-spend readiness — what `make selftest` is still waiting on

`make selftest` is the **pre-spend gate**. It is *supposed* to be red until every value it guards is
determined; `make test` deselects it and prints the count rather than hiding it (`QUESTIONS.md`
Q-009).

| Gate | State | Owner |
|---|---|---|
| `test_no_operator_placeholder_remains_in_config` | ⚠️ **GREEN, AND GREEN VACUOUSLY IF `lanes.yaml` IS ABSENT** (`REVIEW_C0.md` B-04) — `outstanding_sentinels()` skips a missing config file, so this gate passes when the file it guards is gone. As of 2026-08-30 — the four Google API model ids landed; `cfg.outstanding_sentinels()` reports **0** `TODO_OPERATOR` values | ~~OPERATOR~~ — **done**, Q-006 closed |
| `test_the_camel_branch_is_decided_before_any_camel_run` | ❌ **RED** — `camel_comparator.branch` is `TODO_C13_RUN1` | **C13 / RUN-1**, 31 Aug, inside the 90-minute box |

⚠️ **BUT SEE `REVIEW_C0.md` B-04 BEFORE TRUSTING THIS TABLE.** Deleting the `camel_comparator:`
block from `config/lanes.yaml` takes `make selftest` from `1 failed, 1 passed` to **`2 passed`** —
the pre-spend gate flips **RED → GREEN** when the key it guards is removed, because
`.data.get("camel_comparator", {}).get("branch")` reaches around the loader with a default and
`is_sentinel(None)` is `False`. **Until that is fixed, a green `selftest` is not evidence that
anything was decided.**

⚠️ **`make selftest` therefore still exits non-zero, and that is correct.** The remaining failure is
**not** the operator's and **not** the model ids — it is the CaMeL branch, which RUN-1 decides. **Do
not read a red `selftest` as "the ids are still missing."**

**Remaining `TODO_` sentinels in `config/`, all with named owners:**
`protocol:probe.void_threshold_breach_rate` (C14 calibration) · `protocol:n_decision.selected_branch`
and `protocol:n_decision.measured_tokens_per_episode` (C14 pilot) · `protocol:vendor.agentdojo_sha`
and `protocol:vendor.camel_sha` (C13 / C16) · `lanes:camel_comparator.branch` (C13 / RUN-1).
**Six sentinels, zero of them operator-owed.**
