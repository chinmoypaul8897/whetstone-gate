# ARCHITECT_CHECK_0 — the architect's verification of chunk C0

**Date:** 2026-08-31 · **Chunk:** C0 · **Verdict recorded:** C0's review FAIL is **UPHELD**; no
`c0-pass`.

`PROCESS.md` §11: *"After every build and review report the architect emits a VERIFICATION block —
the numbers recomputed, the value obtained, the value claimed — and the operator commits it to
`docs/reviews/ARCHITECT_CHECK_<N>.md`. No chunk is tagged `cN-pass` without one."*

> **Vehicle note.** This file was transcribed into the repository by the architect-artefact landing
> session (`SESSION-TOKEN: e210c6f5`), which performed no verification of its own and added no
> finding of its own. **The verification below is the architect's.**

---

## 1. A PROCESS DEVIATION, RECORDED FIRST BECAUSE IT IS THIS FILE'S OWN

`PROCESS.md` §11 and §1 require the architect to recompute a chunk's build report and commit its
`ARCHITECT_CHECK` **before that chunk's review begins**. §1, verbatim: *"a chunk's review may not
begin before the architect has recomputed that chunk's build report and committed its
`ARCHITECT_CHECK`."*

**C0's review ran on 2026-08-30 under token `52f5307b`. This file is written on 2026-08-31, AFTER
it.** The gate was not in place when it was supposed to be.

It cannot be undone and it is not smoothed over. It is recorded here, at the top, before any
finding this file reports. The architect notes that **the review's quality was not harmed by the
omission** — `REVIEW_C0_1` returned four independently reproduced BLOCKERs and did not need the
architect's numbers to find them — **but that is luck, not process.** The next chunk's
`ARCHITECT_CHECK` precedes its review.

---

## 2. NUMBERS RECOMPUTED INDEPENDENTLY BY THE ARCHITECT

Value obtained beside value claimed. `CONTEXT.md` §13.4, **all three branches**, re-derived from
the four feasibility bullets rather than read off the component table:

| Branch | Attacker @ 60K/ep | Benign solver @ 50K/ep | Gate judge, 3 arms × 20 calls × 1.5K | τ² user sim, 20 turns × 1.5K | Total | ÷ 1.92M/h |
|---|---|---|---|---|---|---|
| **N=50, T-FP 40** | 550 ep × 60K = **33.00M** | 350 × 50K = **17.50M** | 3 × 170 = 510 ep × 20 × 1.5K = **15.30M** | 370 ep × 20 × 1.5K = **11.10M** | **76.90M** | **40.05 h** |
| **N=30, T-FP 40** | 450 × 60K = **27.00M** | 350 × 50K = **17.50M** | 3 × 150 = 450 ep = **13.50M** | 370 ep = **11.10M** | **69.10M** | **35.99 h** |
| **N=30, T-FP 20** | 450 × 60K = **27.00M** | 250 × 50K = **12.50M** | 3 × 130 = 390 ep = **11.70M** | 270 ep = **8.10M** | **59.30M** | **30.89 h** |

**Episode totals reconcile to the block table: 940 at N=50, 840 at N=30.**

**CLAIMED by `CONTEXT.md` v1.1 and by `REVIEW_C0.md` §10: identical on every cell.**

> **RESULT: MATCH.** The v1.1 correction is arithmetically sound, and the corrected chain
> **40.05 → 35.99 → 30.89 h terminates inside the 32 h budget** as Q-013's ruling claims.

---

## 3. THE FOUR BLOCKERS, CONFIRMED BY THE ARCHITECT'S OWN READING OF THE SOURCE

Not accepted from the review. Each was re-derived from `src/whetstone_gate/check_roles.py` and
`src/whetstone_gate/config.py` directly.

### B-01 — **CONFIRMED**
`check_session_tokens` builds `issued[token] = (chunk, role)`, **keyed by TOKEN**, so a duplicated
token keeps only the last row. `by_chunk_role` is then built from `issued.items()`, so **every
token lands in exactly one bucket**: the **E3** count is always 1 and never > 1, and the **E2**
intersection of a chunk's BUILD and REVIEW sets is always empty. **Both checks are structurally
unable to fire.**

### B-02 — **CONFIRMED**
Three distinct causes, all present:
- `shared = (gate_imports & scorer_imports) - {"whetstone_gate"}` is an **allow-list holding the
  package root** — unruled, and not a pure value type (ruled in Q-015).
- `head = module.lstrip(".").split(".")[0]` yields `""` for `from .. import scorer`, so a relative
  import crossing the moat is **not recorded at all**.
- The walk collects only the **direct** imports of files under the two directories, **where hard
  rule 8 says TRANSITIVE.**

### B-03 — **CONFIRMED**
`outstanding_sentinels()` carries a blanket `if not path.is_file(): continue`, written so a
legitimately-absent `ladder.yaml` is not an error — and it **silently excuses `protocol.yaml` and
`lanes.yaml` too**. `load()` itself **does** raise `ConfigFileMissing`, so the sweep **deliberately
bypasses the loader's own refusal.** **F1's detail is additionally a hardcoded string naming a file
it never opened.**

### B-04 — **CONFIRMED**
`cfg.load("lanes").data.get("camel_comparator", {}).get("branch")` **reaches around the loader to
`.data`** and uses `dict.get` with a default: **the exact accessor `config.py`'s own docstring says
"does not exist and must not be added"**, used in the one test that guards spending.

---

## 4. STATE MEASURED ON THE MACHINE BY THE ARCHITECT, 2026-08-31

| Command | Result |
|---|---|
| `python -m whetstone_gate.tasks test` | **61 passed, 1 skipped, 2 deselected** |
| `python -m whetstone_gate.tasks check-roles` | **14 passed, 0 failed, 3 n/a, exit 0** — with **E2 and E3 both printing `clean`**, which is **B-01, printed** |
| `check-prereg` | `config/ holds 2 file(s)`, **STATUS NOT-YET-FROZEN** |

---

## 5. THE CONSTANTS TABLE, CHECKED ROW BY ROW

`CONTEXT.md` §8.6 vs `config/protocol.yaml` vs `src/whetstone_gate/spec_constants.py`.

- **All 13 §8.6 rows are present in `config/protocol.yaml` with the correct values.**
- The registry carries **14** rows because it faithfully splits *"world generation"* into
  `world_generation` and `world_split`. **That is a transcription choice, not an addition.**

⚠️ **EIGHT AUTHORED CONSTANTS ARE MISSING FROM §8.6 — found by the architect, and by no session and
no review.**

**Six are in `config/` but in neither §8.6 nor the registry:**

| Constant | Value |
|---|---|
| `attacker.context_window_turns_verbatim` | 6 |
| `attacker.context_summary_max_tokens` | 400 |
| `attacker.target_tokens_per_episode` | 60000 |
| `statistics.confidence_level` | 0.95 |
| `statistics.rule_of_three_min_n` | 30 |
| `money.rounding` | ROUND_HALF_UP |

**TWO ARE IN NEITHER §8.6 NOR `config/` AT ALL** — which, by §8.6's own sentence (*"Any constant
that is not in this table and not in `config/` is a defect, and finding one is a review
BLOCKER"*), **makes them a defect as of today:**

| Constant | Value | Where it is load-bearing |
|---|---|---|
| **gate-judge per-call target** | **1,500 tokens** | §13.3; **every row of §13.4's arithmetic** |
| **benign-solver per-episode target** | **50,000 tokens** | §13.3; **every row of §13.4's arithmetic** |

**Amended in this session's Task 4** (§8.6 gains all eight rows, `config/protocol.yaml` gains the
two missing keys). **The registry side is the C0 FIX session's**, and is not done here.

---

## 6. WHAT THE ARCHITECT COULD NOT VERIFY

1. **What the two dashboard PNGs depict** — operator-attested, and `PROVENANCE.md` already labels
   it so.
2. **That no payment method is attached** — operator-attested, and **C21 now re-checks it** (added
   to C21's done-when in this session's Task 5).
3. **That the sessions were genuinely different** — nothing can, and `PROCESS.md` §7a says so.

---

## 7. DISPOSITION

**C0's review FAIL is UPHELD.**

**No `c0-pass` tag is cut, and none may be cut until a fix session closes B-01 … B-04 and a fresh
review re-runs the evidence.**
