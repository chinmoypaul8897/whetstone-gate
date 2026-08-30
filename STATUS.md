# STATUS.md — the single glance-state

**One row per chunk. The review-history column is APPEND-ONLY and is never erased or rewritten.**
`C7: built → FAIL(1) → fixed → PASS(2)` stays readable forever. That is the point of it.

**Status values:** `todo` · `in-flight` · `built (unreviewed)` · `in-review` · `FAILED` ·
`fixing` · **`PASS`** (tagged `cN-pass`).
**Review types:** `full` = personas 1 + 2, two sealed phases, a committed reimplementation, ≥8
mutants · `code` = persona 2 only, ≥4 mutants · `submission` = persona 3 + persona 1.
**No chunk is `PASS` without `docs/reviews/ARCHITECT_CHECK_<N>.md`.** An unrecorded gate is not a
gate.

*Last updated: 2026-08-30, end of the C0 ADVERSARIAL REVIEW (`52f5307b`).*

⚠️ **C0 IS `FAILED`. NO `c0-pass` TAG EXISTS AND THE TAG CHAIN HAS NOT STARTED.** Four BLOCKERs, all
the same shape — a check that reports PASS over nothing: `check-roles` **E2 and E3 cannot fire at
all**; **D3, "the whole moat", is defeated by hard rule 8's own named spike defect**; the **F group
reports `config/` complete over a `config/` missing `protocol.yaml`**; and **`make selftest`, the
pre-spend gate, flips GREEN when the key it guards is deleted.** Full evidence, all re-runnable:
`docs/reviews/REVIEW_C0.md`. **A FIX session is owed** — `INCIDENTS.md` entries first (hard rule 13),
then the four BLOCKERs, then a fresh review. Every dependent chunk (C1, C2, C3, C6, C11, C13, C15)
lists C0 as a dependency.

**Specification: `CONTEXT.md` v1.1.** See *Specification version* below — it matters because **C14 selects the N branch from §13.4 and writes it into `PROTOCOL.md` before the freeze.**

---

## Chunks

| # | Date | Chunk | Review | Status | Review history (append-only) |
|---|---|---|---|---|---|
| **C0** | 30 Aug | Repo, toolchain, remote, canonical files, day-one setup | `code` | ⚠️ **FAILED** | built → completed (3 operator-owed items landed; Q-006 + Q-008 closed) → **REVIEW_C0_1 = FAIL** (`52f5307b`, 4 BLOCKERs; no tag) |
| **C1** | 30 Aug | `RAZORPAY_SEMANTICS.md` + `PROVENANCE.md` attack rows A1–A6 | `full` | todo | — |
| **C2** | 30 Aug | World generator + **the probe planted** (`pay_CANARYRECON`) | `full` | todo | — |
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

**What v1.1 changed, in one line:** *"~71M ≈ 37 h"* → **69.10M = 35.99 h** and *"−6M → ~34 h"* →
**59.30M = 30.89 h**. **The N=50 headline (76.90M / 40.05 h) was correct and is unchanged, and so
is the decision rule** — its thresholds are criteria, not projections. ⚠️ **Why it was worth a
session:** as published the reduction chain ran **40 → 37 → 34 h against a 32 h budget and never
reached its own budget**, with *"No other branch. No post-hoc adjustment."* leaving nothing to try;
corrected, the final rung lands at **30.89 h and fits**.

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
