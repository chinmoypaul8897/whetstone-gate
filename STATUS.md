# STATUS.md — the single glance-state

**One row per chunk. The review-history column is APPEND-ONLY and is never erased or rewritten.**
`C7: built → FAIL(1) → fixed → PASS(2)` stays readable forever. That is the point of it.

**Status values:** `todo` · `in-flight` · `built (unreviewed)` · `in-review` · `FAILED` ·
`fixing` · **`PASS`** (tagged `cN-pass`).
**Review types:** `full` = personas 1 + 2, two sealed phases, a committed reimplementation, ≥8
mutants · `code` = persona 2 only, ≥4 mutants · `submission` = persona 3 + persona 1.
**No chunk is `PASS` without `docs/reviews/ARCHITECT_CHECK_<N>.md`.** An unrecorded gate is not a
gate.

*Last updated: 2026-08-30, end of C0 build.*

---

## Chunks

| # | Date | Chunk | Review | Status | Review history (append-only) |
|---|---|---|---|---|---|
| **C0** | 30 Aug | Repo, toolchain, remote, canonical files, day-one setup | `code` | **built (unreviewed)** | built |
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

## Tags

| Tag | What it fixes | Cut | Exists |
|---|---|---|---|
| `probe-v1` | `HOLES.md` alone — CANARY-A, CANARY-B, S4's window width (2) | **before** the pilot **and before** the calibration command runs | **no** |
| `prereg-v1` | the full frozen set: `INVARIANTS.md`, `PROTOCOL.md`, `HOLES.md`, `PROVENANCE.md`, `RAZORPAY_SEMANTICS.md`, **`config/`** | after the pilot and the calibration, **before every scored episode** | **no** |
| `cN-pass` | chunk N passed adversarial review | by the review session, on PASS only | **none yet** |

⚠️ **No calibration episode runs before `probe-v1` exists. No scored episode runs before `prereg-v1`
exists.** The freeze never moves earlier to fit the schedule; it is the one thing the project is
staked on.
