# `c6_mutants_5.md` — C6 REVIEW 5's mutants, and C6 FIX 4's own thirteen

**SESSION-TOKEN: `0ca97bbb`** · **Chunk:** C6, the attacker loop · **Review attempt 5**
**Phase-1 seal:** `615993d` · **Subject measured at:** `615993d` (= C6 FIX 4's `41f554b` plus this
review's own three doc commits; `src/` and `tests/` are byte-identical to `41f554b`)

This file is **owed**: C6 FIX 4 could not write it because `docs/reviews/mutants/` was outside its
fence, and it named the debt rather than skipping it. It carries **both tables** — this review's,
and FIX 4's thirteen transcribed from `docs/sessions/nightrun-b-1.txt`.

---

## 0. METHOD, AND BOTH FLATTERING DIRECTIONS CLOSED BY CONSTRUCTION

`Q-082`'s ruling makes the **required set** the gate, so the set was enumerated and argued in
`independent/c6_review5_criteria.md` §1 **before a single mutant was written** and sealed at
`615993d`. Sixteen owned properties; thirty-four planned mutants; **Phase 2 added seven and removed
none.**

**The harness.** Four fresh `git clone`s into an OS temp directory. This repository was **never
mutated**.

* **INC-64 / OF-139 — the clone that imports the LIVE package reports every mutant SURVIVED.**
  `PYTHONPATH` was set to each clone's `src`, and **`whetstone_gate.__file__` and
  `config.repo_root()` are printed at the head of every slice** (they are in the raw outputs).
  ⚠️ **The test that now catches this was RUN, in both directions:**
  `tests/test_repo_invariants.py::test_the_package_under_test_is_the_tree_under_test` is **GREEN**
  in the clone with `PYTHONPATH` set and **RED** without it — it names
  `C:/Users/chinm/whetstone-gate/src/whetstone_gate/__init__.py` as the package it resolved.
* **INC-57 — restoring with `git checkout --` from a HEAD that holds the mutation reports every
  mutant KILLED.** Restoration writes **the original bytes** back and re-hashes; the harness never
  commits, so no clone's HEAD ever held a mutation.
* **Controls.** Every slice ran a control before and after. **All four slices: 121 passed, 0 failed,
  before and after.** A slice whose post-restore control was not green would be VOID.

### 0.1 ⚠️ THIS REVIEW'S OWN HARNESS DEFECT, RECORDED BECAUSE THE CONTROL IS WHAT CAUGHT IT

The **first** parallel run was launched in the foreground, exceeded the tool's ten-minute limit and
was **killed mid-mutant**, leaving a mutation applied in all four clones. The next launch's
**pre-run control read `117 passed, 4 failed` and the harness declared the slice VOID and stopped**;
two other slices aborted on `anchor is not unique`, which is the same defect seen from the other
side. **Nothing from that run is reported.** All four clones were reset and re-run from a verified
control of 121.

⚠️ **The direction matters and is the reason this is recorded rather than merely fixed:** this
failure mode is the **honest** one — it makes mutants look KILLED-by-a-dirty-tree and it announces
itself in the control. `INC-57`'s and `INC-64`'s both look clean. **A harness is only as good as the
control it runs before it believes itself**, and that is the third time in three sessions a C6
mutation harness has needed one.

⚠️ **The reset used `git checkout -- .` inside the CLONES, and that is NOT `INC-57`'s defect.**
`INC-57` is a harness that **commits** the mutation and then restores from a HEAD that holds it.
These clones' HEAD is `615993d`, which holds no mutation, and the harness commits nothing — verified
by `git rev-parse HEAD` and a clean `git status --porcelain` in each clone before the re-run.

---

## 1. THE REQUIRED SET — 45 MUTANTS RUN, 38 PLANNED IN THE SEAL AND 7 ADDED

**Legend:** `OP-n` is the owned property from the seal's §1. Every survivor is marked **OWNED** or
**NOT-OWNED** and argued in §2.

### 1.1 The sealed thirty-eight

| id | OP | file | operator | verdict | failures |
|---|---|---|---|---|---|
| **M-01** | OP-1 | `context.py` | window width `+1` | ✅ KILLED | 8 |
| **M-02** | OP-1 | `context.py` | window taken as a PREFIX, not a suffix | ✅ KILLED | 5 |
| **M-05** | OP-3 | `context.py` | the cap comparison TIGHTENED by one (`OF-87`'s M19) | ✅ KILLED | 1 |
| **M-06** | OP-3 | `context.py` | the cap comparison LOOSENED by one (`OF-87`'s M3) | ✅ KILLED | 1 |
| **M-07** | OP-4 | `context.py` | truncation DROPS the mandated denial line | ✅ KILLED | 2 |
| **M-08** | OP-4 | `context.py` | the hard refusal below the floor becomes a silent trim | ✅ KILLED | 1 |
| **M-09** | OP-5 | copy 1 | LAYER 1's exemption widened from the state JSON to the state LINE | ✅ KILLED | 3 |
| **M-10** | OP-5 | copy 2 | the same widening — **`R-14` / `OF-124`** | ✅ KILLED | 4 |
| **M-11** | OP-6 | copy 1 | LAYER 2's gate VOCABULARY deleted | ✅ KILLED | 1 |
| **M-11b** | OP-6 | copy 1 | LAYER 2's policy-CLAUSE scan deleted | 🟡 **SURVIVED** | 0 |
| **M-11c** | OP-6 | copy 1 | LAYER 2b's arm/clause identity scan disarmed | ✅ KILLED | 5 |
| **M-12** | OP-6 | copy 2 | the gate VOCABULARY deleted | 🔴 **SURVIVED** | 0 |
| **M-12b** | OP-6 | copy 2 | the `config/` money-ceiling scan deleted | ✅ KILLED | 4 |
| **M-12c** | OP-6 | copy 2 | the arm/clause identity scan disarmed | ✅ KILLED | 4 |
| **M-12d** | OP-6 | copy 2 | CLAIM 1's verbatim policy-clause scan deleted | 🔴 **SURVIVED** | 0 |
| **M-13** | OP-7 | copy 1 | LAYER 3, the residue catch-all, deleted (`N12` / `OF-106`) | ✅ KILLED | 4 |
| **M-15** | OP-8 | copy 1 | the denial-VALUE equality block deleted (`N14` / `OF-105`) | ✅ KILLED | 4 |
| **M-16** | OP-8 | copy 2 | the denial-VALUE equality block deleted | 🔴 **SURVIVED** | 0 |
| **M-17** | OP-8 | copy 1 | the refusal-line COUNT loosened (`N13` / `OF-111`) | ✅ KILLED | 3 |
| **M-18** | OP-8 | copy 2 | the refusal-line COUNT loosened — **`R-15` / `OF-125`** | ✅ KILLED | 3 |
| **M-19** | OP-9 | copy 2 | **`SM-B` RE-APPLIED**: `_sole_layer`'s EXCLUSIVITY half deleted | ✅ KILLED | 1 |
| **M-19e** | OP-9 | copy 2 | `==` → `>=` on the same comparison | ⚪ **EQUIVALENT** | 0 |
| **M-20** | OP-9 | copy 2 | `_sole_layer`'s IDENTITY half deleted — accepts any layer | ✅ KILLED | 1 |
| **M-21** | OP-9 | copy 2 | `_sole_layer` made a NO-OP | ✅ KILLED | 1 |
| **M-22** | OP-9 | copy 2 | `_sole_layer` INVERTED | ✅ KILLED | 8 |
| **M-19c1** | OP-9 | copy 1 | `_sole_killer`'s EXCLUSIVITY half deleted | ✅ KILLED | 1 |
| **M-20c1** | OP-9 | copy 1 | `_sole_killer`'s IDENTITY half deleted | ✅ KILLED | 1 |
| **M-23** | OP-10 | copy 2 | ⚠️ **THE DOOR-SHUTTING MUTANT** — the probe note banned from the WORLD surface too | ✅ KILLED | 7 |
| **M-24** | OP-11 | `corpus.py` | `Q-047`'s stride collapsed to 1 | ✅ KILLED | 2 |
| **M-24b** | OP-11 | `corpus.py` | the EPISODE-SEED term dropped | ✅ KILLED | 4 |
| **M-25** | OP-11 | `corpus.py` | the four-corpus round robin collapsed to one (`INC-27`'s defect) | ✅ KILLED | 7 |
| **M-26** | OP-12 | `estimate.py` | the divisor hardcoded instead of resolved through the loader (`Q-048`) | ✅ KILLED | 1 |
| **M-27** | OP-12 | `estimate.py` | `ceil` → `floor` | ✅ KILLED | 6 |
| **M-28** | OP-13 | `estimate.py` | `range(0, turn_budget + 1)` → `range(0, turn_budget)` — **`R-20` / `OF-126`** | ✅ KILLED | 1 |
| **M-29** | OP-13 | `estimate.py` | `> target` → `>= target` (`N4` / `OF-108`) | ✅ KILLED | 3 |
| **M-30** | OP-14 | copy 1 | the dynamic scan's refusal list shortened by one entry | ✅ KILLED | 2 |
| **M-31** | OP-14 | copy 1 | `rglob` → `glob` (`R-18` / `OF-129`) | 🔵 **SURVIVED** | 0 |
| **M-08b** | OP-15 | copy 1 | `assert len(summaries) == 1` → `>= 1` (`R-08` / `OF-130`) | 🔵 **SURVIVED** | 0 |

**Sealed thirty-eight: 31 KILLED · 1 EQUIVALENT · 6 SURVIVED.**

### 1.2 The seven ADDED in Phase 2 — REAL LEAKS, not guard mutations

⚠️ **These ask a harder question than any guard mutation: plant an ACTUAL leak in `src/` and see
whether the SUITE goes red.** A guard that is pinned but never fired at a real leak is `INC-43`'s
decorative gate. Six of the seven are leaks in the **subject**, not in a guard.

| id | OP | file | operator | verdict | failures |
|---|---|---|---|---|---|
| **M-35** | OP-7 | `context.py` | **A REAL LEAK** — an unexplained AUTHORED line appended to the summary | ✅ **KILLED** | **20** |
| **M-36** | OP-7 | `context.py` | **A REAL LEAK on the STATE LINE** (`OF-128`'s class) | 🟠 **KILLED — BUT BY A BYTE-COUNT FIXTURE** | 2 |
| **M-37** | OP-5 | `context.py` | **A REAL LEAK** — the E1 cap planted in `STATE_LABEL`, **`INC-42`'s M17 shape** | ✅ **KILLED** | **22** |
| **M-38** | OP-8 | `context.py` | **A REAL LEAK** — arm identity in `LAST_REFUSAL_LABEL` (`OF-104`'s first exhibit) | ✅ **KILLED** | **27** |
| **M-39** | OP-10 | copy 2 | the probe-note-on-AUTHORED check disarmed | 🔴 **SURVIVED** | 0 |
| **M-40** | OP-2 | `context.py` | the summary stops being a pure function of `(state, refusal, cap)` | ✅ **KILLED** | **31** |
| **M-41** | OP-16 | `loop.py` | **`Q-046`'s EXACT-EQUALITY fold widened to containment** | ✅ **KILLED** | 3 |

**Added seven: 6 KILLED · 1 SURVIVED.**

⚠️ **`M-37` IS THE MOST REASSURING RESULT IN THIS FILE, AND IT IS SAID SO.** `INC-42` records that
mutant **M17** — *"blocked because the action exceeded the configured per-action ceiling of 5000000
paise"* **inside the label**, on the authored surface, every turn, every arm — left **all 65 C6 tests
green**. The same shape today dies with **22 failures**. That is the whole arc of four reviews and
four fixes, measured in one number.

⚠️ **`M-36` IS KILLED FOR THE WRONG REASON AND THAT IS REPORTED RATHER THAN COUNTED.** Its two
killers are `test_the_cap_is_INCLUSIVE_and_pinned_in_BOTH_directions` and
`test_the_crossover_series_reproduces_against_the_REAL_seed_2001_world` — **both byte-count
fixtures**. **No blindness layer sees it.** That is `REVIEW_C6_3`'s own named complaint — *"they die
on one test … because a longer label changes the summary's CHARACTER COUNT. Nothing in that kill is
about the label's content"* — and it confirms `OF-128` by construction: text appended **inside** the
state line can never contribute residue, because `state_json` is the whole body of an untruncated
line.

---

### 1.3 THE FOUR COMBINED EXPERIMENTS — a survivor applied TOGETHER WITH a real leak

A guard-side survivor only matters if it costs the suite the ability to catch a real leak.

| id | what | verdict |
|---|---|---|
| **E1** | `M-12` **plus** a real gate-reason leak in `LAST_REFUSAL_LABEL` | **RED, 19 failures** |
| **E1c** | control — the same leak, copy 2's vocabulary **intact** | **RED, 29 failures** |
| **E2** | `M-16` **plus** a real drift in `texts.generic_denial()` | **RED, 2 failures** |
| **E2c** | control — the same drift, copy 2's equality **intact** | **RED, 2 failures, the SAME two** |

**No real leak escapes the suite today.** `E1` costs ten failures of depth and keeps the kill; `E2`'s
coverage is entirely duplicated. **This does not lift the survivors** — `Q-082` rules a survivor on
an owned property a FAIL *"even when the subject measures clean today"*, and `R-14`, ruled OWNED, has
the identical property — but it bounds the risk and `REVIEW_C6_5.md` §6.1a states it first.

---

## 2. EVERY SURVIVOR, MARKED **OWNED** OR **NOT-OWNED**, AND ARGUED

| id | determination | one-line argument |
|---|---|---|
| **`M-12`** | 🔴 **OWNED (OP-6)** | copy 2's gate-vocabulary scan; three exhibits at 40/20/20 findings → 0, all from that scan alone; **copy 2 is the only guard over `run_episode`'s own contexts** |
| **`M-16`** | 🔴 **OWNED (OP-8)** | copy 2's denial-VALUE equality; exhibit 19 → 0 with **no other layer firing**; copy 1's fixture hard-codes the spec string as the refusal, so it cannot see a drift in what the loop folds |
| **`M-12d`** | 🔴 **OWNED (OP-6)** | copy 2's verbatim-clause scan; exhibit 19 → 0 **with no source mutation at all** — a tool result echoing clause P4 |
| **`M-39`** | 🔴 **OWNED (OP-10)** | copy 2's probe-note-on-AUTHORED check, fired at nothing; copy 1's twin is fired in both directions but never at a `run_episode` context |
| **`M-11b`** | ⚪ **EQUIVALENT (suite level), boundary named** | the deleted clause half is a strict subset of `_policy_findings`, which has its own firing test; no clause can span the seam because the subtraction inserts a **newline** |
| **`M-19e`** | ⚪ **EQUIVALENT, proven** | `matched ⊆ findings`, so `>=` and `==` are the same predicate; **the separating input does not exist** |
| **`M-31`** | 🔵 **NOT-OWNED** | `rglob` → `glob`: a directory layout that does not exist (`R-18` / `OF-129`) |
| **`M-08b`** | 🔵 **NOT-OWNED** | `len(summaries) == 1` → `>= 1`: no code path builds two (`R-08` / `OF-130`) |

*(The full argument, with every exhibit, is `REVIEW_C6_5.md` §6.)*

---

## 3. C6 FIX 4's OWN THIRTEEN — TRANSCRIBED, AS OWED

From `docs/sessions/nightrun-b-1.txt` §3, verbatim in substance. FIX 4's method is recorded there as
*"fresh OS temp clones; `whetstone_gate.__file__` PRINTED for every lane; this repository was NEVER
mutated; every anchor asserted to match EXACTLY ONCE; RESTORE BY WRITING THE ORIGINAL BYTES … after
every restore … a FULL UNMUTATED CONTROL asserted equal to the baseline (784 passed, 0 failed)."*

| id | target | FIX 4's verdict | kills in C6 files |
|---|---|---|---|
| `R-14` | copy 2 LAYER 1's exemption widened to the state LINE | KILLED | 4 |
| `R-15` | copy 2's `refusal_lines != 1` → `< 1` | KILLED | 3 |
| `R-20` | `crossing()`'s `turn_budget` end narrowed | KILLED | 1 |
| `SM-A` | a cap shape drifted OUT of the guard's vocabulary | KILLED | collection abort |
| **`SM-B`** | **THE INLINE EXCLUSIVITY CHECK NEUTERED** | ⚠️ **SURVIVED** | 0 |
| `SM-B2` | `_sole_layer`'s EXCLUSIVITY clause dropped | KILLED | 1 |
| `SM-B3` | `_sole_layer`'s IDENTITY clause dropped | KILLED | 1 |
| `SM-B4` | `_sole_layer` INVERTED (always raises) | KILLED | 8 |
| `SM-C` | copy 2's state-JSON exemption DELETED outright | KILLED | 1 |
| `SM-D` | `crossing()`'s range WIDENED past the budget | KILLED | 1 |
| `SM-E` | copy 2's denial count narrowed to AUTHORED parts | KILLED | 3 |
| `SM-F` | copy 2's `refusal_lines != 1` → `> 1` | KILLED | 1 |
| `SM-G` | copy 1's `_sole_killer` identity half deleted | KILLED | 1 |

**Independently re-run by this review, and every one reproduces:**

| FIX 4's id | this review's equivalent | FIX 4 said | I measure |
|---|---|---|---|
| `R-14` | `M-10` | KILLED, 4 | ✅ **KILLED, 4** |
| `R-15` | `M-18` | KILLED, 3 | ✅ **KILLED, 3** |
| `R-20` | `M-28` | KILLED, 1 | ✅ **KILLED, 1** |
| `SM-B` | `M-19` (the repair) | SURVIVED against `7cbe908`, repaired at `da9fc96` | ✅ **KILLED, 1**, by `test_the_sole_layer_helper_REJECTS_a_shape_that_TWO_of_copy_2s_layers_catch` |
| `SM-B2` | `M-19` | KILLED, 1 | ✅ **KILLED, 1** |
| `SM-B3` | `M-20` | KILLED, 1 | ✅ **KILLED, 1** |
| `SM-B4` | `M-22` | KILLED, 8 | ✅ **KILLED, 8** — the same eight |
| `SM-D` | *(the widening direction)* | KILLED, 1 | ✅ pinned by the same both-ways fixture that kills `M-28` |
| `SM-G` | `M-19c1` / `M-20c1` | KILLED, 1 | ✅ **KILLED, 1** each |

**Every FIX 4 claim this review could independently re-run reproduces, including the failure
counts.** `SM-A`, `SM-C`, `SM-E` and `SM-F` were not re-run in this form; `M-12b` (copy 2's ceiling
scan deleted, 4 failures) covers `SM-A`/`SM-C`'s territory from the other side and dies.
