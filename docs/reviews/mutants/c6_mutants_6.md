# `c6_mutants_6.md` — C6 REVIEW 6's mutants, and C6 FIX 5's twelve, which were OWED

**SESSION-TOKEN: `7f4b0e93`** · C6, REVIEW, attempt 6 · **Written 2026-09-02 → 2026-09-03.**

⚠️ **THIS FILE DISCHARGES A DEBT AS WELL AS RECORDING A RUN.** `INCIDENTS.md` **INC-70**:
*"`docs/reviews/mutants/` is outside this session's fence, so `c6_mutants_6.md` is OWED to the next
review — the same debt C6 FIX 4 named rather than skipped."* **§1 is C6 FIX 5's twelve, transcribed
from `docs/sessions/c6-fix-5.txt` without alteration. §2 onward is this review's own.**

---

## 0. HOW EVERY NUMBER HERE WAS PRODUCED

`docs/reviews/independent/c6_review6_mutants.py`. **Seven fresh OS temp clones**, one per slice,
under
`…\scratchpad\c6r6\tree_{A,B,C,D,E,F,G}`. **This repository was never mutated.**

| rule | how this harness obeys it |
|---|---|
| **`INC-69`** — the clone environment must reach `subprocess.run` **itself** | `run_suite` builds one `env` dict and passes it to `subprocess.run(..., env=env)`. ⚠️ **The provenance print and the pytest run are the SAME `-c` script in the SAME subprocess**, so a transcript showing the tree is evidence about the tree that was measured. `INC-69`'s harness printed four true provenance lines from a *different* subprocess and measured the live repository. |
| **`OF-139`** — the package under test must be the tree under test | `tests/test_repo_invariants.py::test_the_package_under_test_is_the_tree_under_test` is the fourth item of **every** measurement, control runs included. |
| **`OF-159`** — a positive control that MUST die | **TWO.** `N-PC` widens the folded state's JSON separators in `src/` (proves the clone's **source** is under test); `N-PC2` is a bare `assert False` in copy 2's own helper (**OF-159's `CTRL-LIVE`** — proves the clone's **test file** is under test). **A slice in which either survives is VOID and unscored.** |
| **`INC-17` / REVIEW 4's inverse** — restore by writing the original bytes | Bytes are captured before each mutation and written back after it; the restore is verified by **SHA-256 equality**, and a mismatch VOIDs the slice on the spot. |
| pre- and post-run control | **136 passed / 0 failed** — 135 C6 tests plus the `OF-139` guard — before the first mutant and after the last restore of every slice. |

⚠️ **AND THE FIRST LAUNCH OF THIS HARNESS PRODUCED AN INVALID SLICE, WHICH IS REPORTED RATHER THAN
DISCARDED SILENTLY.** `tree_C`'s clone had been interrupted by a tool timeout and contained **no
`src/`**. Its pre-run control read **0 passed** and its provenance line named
`C:\Users\chinm\whetstone-gate` — **the live repository** — so the harness declared the slice VOID
and reported nothing from it. **That is `INC-69`'s exact failure mode, detected in 17 seconds by the
provenance print rather than by a human distrusting an implausible result.** The clone was rebuilt
and slice C re-run from a verified control. **This is the direction `OF-159` calls the honest one:
it announces itself.**

---

## 1. C6 FIX 5's TWELVE — TRANSCRIBED, NOT RE-MEASURED HERE

**Source: `docs/sessions/c6-fix-5.txt`, the session's own committed record.** Five fresh clones,
eleven killed, one survivor **reported before it was repaired**. Transcribed verbatim in substance;
this review re-runs six of them independently in §2 and reports its own numbers beside them.

| id | target | FIX 5's verdict |
|---|---|---|
| `M-12` | copy 2's gate-VOCABULARY scan (`OF-146`) | KILLED, 3 |
| `M-16` | copy 2's denial-VALUE exact equality (`OF-147`) | KILLED, 3 |
| `M-12d` | copy 2's verbatim-POLICY-CLAUSE scan (`OF-148`) | KILLED, 3 |
| `M-39` | copy 2's probe-note-on-AUTHORED check (`OF-149`) | KILLED, 1 |
| `M-RES` | copy 2's NEW residue layer, deleted (`OF-150`) | KILLED, 3 |
| `SM-1` | the residue layer stops EXEMPTING the state JSON | KILLED, 22 |
| `SM-5` | the residue layer stops SUBTRACTING the denial VALUE | KILLED, 22 |
| `SM-2` | the residue layer's NON-CASCADE removed | KILLED, 1 |
| `SM-6` | the denial-line COUNT finding deleted | KILLED, 4 |
| `SM-3` | `M-12` **plus** `_sole_layer` deleted from FIX 5's own vocabulary fixture | KILLED, 3 |
| `SM-4` | `M-RES` **plus** `_sole_layer` deleted from FIX 5's own residue fixture | KILLED, 3 |
| **`SM-7`** | the residue layer's own LOCATOR report disarmed | ⚠️ **SURVIVED**, then closed at `4d5a836` |


---

## 2. THIS REVIEW'S 48 — every row measured by me

**48 scored mutants across 13 slices. 40 KILLED, 8 survivors: 2 PROVEN EQUIVALENT, 1 NOT A VALID
MUTANT (mine), 2 NOT-OWNED, 3 OWNED.** Plus **22 positive-control runs, every one dead.**

**Slice validity** — every row read `136 passed / 0 failed` at both controls, both positive controls
died, and every restore matched its pre-mutation SHA-256:

| slice | tree | PRE | POST | positive controls |
|---|---|---|---|---|
| A | `tree_A` | 136/0/0 | 136/0/0 | `N-PC` ✅ (`N-PC2` run as A2) |
| A2 | `tree_A` | 136/0/0 | 136/0/0 | `N-PC` ✅ `N-PC2` ✅ |
| B / B2 | `tree_B` | 136/0/0 | 136/0/0 | both ✅ |
| C | `tree_C` | 136/0/0 | 136/0/0 | both ✅ |
| D / D2 | `tree_D` | 136/0/0 | 136/0/0 | both ✅ |
| E / E2 | `tree_E` | 136/0/0 | 136/0/0 | both ✅ |
| F | `tree_F` | 136/0/0 | 136/0/0 | both ✅ |
| G | `tree_G` | 136/0/0 | 136/0/0 | both ✅ |
| H | `tree_A` | 136/0/0 | 136/0/0 | both ✅ |
| I | `tree_B` | 136/0/0 | 136/0/0 | both ✅ |
| ⚠️ **C, attempt 1** | `tree_C` (broken clone) | **0 passed** | — | **VOID, and nothing from it is reported** |

### 2.1 THE SIX CELLS THE PROMPT REQUIRED KILLED

| id | ref | target | verdict | killed by |
|---|---|---|---|---|
| `N-11` | `M-12` | copy 2's gate-VOCABULARY scan (`OF-146`) | ✅ **KILLED, 3** | `test_the_LOOP_copys_GATE_VOCABULARY_scan_FIRES_on_a_reason_that_leaks_nothing_else` |
| `N-17` | `M-16` | copy 2's denial-VALUE exact equality (`OF-147`) | ✅ **KILLED, 3** | `test_the_LOOP_copys_DENIAL_EQUALITY_FIRES_on_a_DRIFTED_fold_constant` |
| `N-13` | `M-12d` | copy 2's verbatim-CLAUSE scan (`OF-148`) | ✅ **KILLED, 3** | `test_the_LOOP_copys_VERBATIM_CLAUSE_scan_FIRES_on_a_TOOL_RESULT_that_echoes_one` |
| `N-21` | `M-39` | copy 2's probe-note-on-AUTHORED check (`OF-149`) | ✅ **KILLED, 1** | `test_the_LOOP_copys_PROBE_NOTE_check_FIRES_when_WE_write_it_and_NOT_when_the_WORLD_does` |
| `N-15` | `M-RES` | copy 2's residue layer (`OF-150`) | ✅ **KILLED, 3** | `test_the_LOOP_copys_RESIDUE_layer_FIRES_on_authored_text_carrying_NO_policy_word` |
| `N-33` | `SM-7` | copy 2's summary LOCATOR | ✅ **KILLED, 1** | `test_the_LOOP_copys_RESIDUE_layer_SAYS_SO_when_it_cannot_LOCATE_the_summary` |

### 2.2 EVERY OTHER MUTANT

| id | OP | target | verdict | first killer |
|---|---|---|---|---|
| `N-01` | 1 | the window width hardcoded, not read from `config/` | ✅ 1 | `test_the_window_sizes_are_read_from_config_and_not_from_source` |
| `N-02` | 1 | the verbatim window narrowed by one turn | ✅ 7 | `test_the_window_keeps_exactly_the_configured_number_of_verbatim_turns` |
| `N-03` | 2 | the summary stops being a pure function of state | ✅ 1 | `test_identical_state_produces_byte_identical_summary_text` |
| `N-04` | 3 | the 400-token cap made EXCLUSIVE | ✅ 1 | `test_the_cap_is_INCLUSIVE_and_pinned_in_BOTH_directions` |
| `N-05` | 3 | the cap loosened by one token, the other way | ✅ 1 | the same fixture — **it pins both directions** |
| `N-06` | 4 | `OF-88`'s truncation floor removed | ✅ 1 | `test_the_cap_is_a_HARD_REFUSAL_below_the_marker_rather_than_silently_unenforced` |
| `N-08` | 5 | **copy 1's** LAYER 1 deleted | ✅ 4 | `test_LAYER_1_scans_the_state_LABEL_and_exempts_only_the_state_JSON` |
| `N-09` | 5 | **copy 2's** LAYER 1 deleted | ✅ 4 | `test_the_LOOP_copys_LAYER_1_scans_the_state_LABEL_and_exempts_only_the_state_JSON` |
| `N-10` | 6 | **copy 1's** `_GATE_VOCABULARY` emptied | ✅ 1 | `test_the_sole_killer_helper_REJECTS_a_shape_that_two_layers_catch` |
| `N-12` | 6 | **copy 1's** verbatim-clause scan deleted | ⚪ **PROVEN EQUIVALENT** | = `REVIEW_C6_5`'s `M-11b`; boundary = the newline at the seam, re-verified by my vector **V45** |
| `N-12c` | 6 | **copy 2's** LAYER 2b arm/clause scan neutered | ✅ 4 | `test_the_LOOP_copys_own_claim_4_scan_ACTUALLY_FIRES_on_a_leaky_label` |
| `N-14` | 7 | **copy 1's** residue layer deleted | ✅ 4 | `test_LAYER_3_is_the_SOLE_killer_of_authored_text_carrying_no_policy_word` |
| `N-16` | 8 | **copy 1's** denial-VALUE equality deleted | ✅ 4 | `test_the_denial_equality_is_the_SOLE_killer_of_a_value_that_leaks_nothing_else` |
| `N-18` | 8 | **copy 2's** refusal-line COUNT loosened | ✅ 4 | `test_the_LOOP_copys_denial_line_COUNT_ALSO_fires_when_the_summary_carries_NONE` |
| `N-40` | 8 | **copy 2's** denial-VALUE arm/clause regex neutered | ⚪ **PROVEN EQUIVALENT** | §8.6's denial string matches none of the four alternatives, so the equality check always co-fires. Measured: 57 → 38 findings, no assertion depends on the difference |
| `N-19` | 9 | `_sole_layer`'s exclusivity half deleted (`SM-B` re-applied) | ✅ 1 | `test_the_sole_layer_helper_REJECTS_a_shape_that_TWO_of_copy_2s_layers_catch` |
| `N-20` | 9 | `_sole_layer`'s identity half deleted | ✅ 1 | the same fixture |
| `N-22` | 10 | ⚠️ **THE GLOBAL BAN `Q-046` FORBIDS** — the probe note banned from the WORLD surface too | ✅ **12** | `test_the_LOOP_copys_GATE_VOCABULARY_scan_FIRES…` and 11 more. **Arm 4 cannot be voided silently** |
| `N-37` | 10 | **copy 1's** probe-note-on-AUTHORED check disarmed | ✅ 1 | `test_the_attackers_context_contains_no_hole` |
| `N-23` | 11 | `Q-047`'s stride perturbed by one | ✅ 2 | `test_the_offered_reach_is_MEASURED_per_episode_and_across_the_whole_seed_set` |
| `N-24` | 11 | the offer made SEED-INDEPENDENT | ✅ 4 | `test_coverage_ACCUMULATES_across_the_seed_set_instead_of_being_frozen` |
| `N-25` | 12 | the divisor hardcoded instead of resolved through the loader | ✅ 1 | `test_the_estimator_divisor_is_READ_FROM_CONFIG_and_not_from_source` |
| `N-26` | 13 | `crossing()`'s strictness `>` → `>=` | ✅ 3 | `test_the_crossing_is_STRICTLY_over_the_target_and_is_pinned_at_the_boundary_BOTH_WAYS` |
| `N-27` | 13 | `crossing()`'s range end moved off `turn_budget` | ✅ 1 | `test_the_crossing_is_pinned_at_the_TURN_BUDGET_END_of_its_range_BOTH_WAYS` |
| `N-28` | 14 | the dynamic-import scan narrowed | ✅ 1 | `test_the_dynamic_reach_scan_ACTUALLY_FIRES_on_every_form` |
| `N-29` | 15 | the authored-text byte comparison deleted | ⚠️ **NOT A VALID MUTANT** — it removes the fixture rather than unpinning a catcher; every such mutant survives. Replaced by `N-29b` |
| `N-29b` | 15 | ⚠️ **`data/attacker_sys.txt` DRIFTED** — the real form | ✅ 2 | `test_the_three_authored_texts_are_character_identical_to_context_md` |
| `N-30` | 16 | `Q-046`'s exact-equality fold widened to containment | ✅ 3 | `test_the_LOOP_copys_denial_line_COUNT_fires_on_a_summary_carrying_MORE_than_one` |
| `N-31` | 17 | ⚠️ **`data/generic_denial.txt` DRIFTED** — the `OF-147` seam, from the file side | ✅ **8** | `test_the_LOOP_copys_DENIAL_EQUALITY_FIRES_on_a_DRIFTED_fold_constant` — **copy 2 among the killers** |
| **`N-32`** | **18** | **`corpus_turns` over `records[1:]`** | 🔴 **SURVIVED** | **OWNED. Exhibit: 20/20 → 19/20, partition FALSE, suite green** |
| `N-34a` | 19 | copy 2's `_cap_formattings` returns an empty set | ✅ collection error | `_cap_label_shapes` asserts each shape is in the guard's own vocabulary |
| `N-34b` | 19 | copy 1's `assert len(summaries) == 1` → `>= 1` | 🔵 **SURVIVED, NOT-OWNED** | `M-08b`/`OF-130`; pre-classified in the seal's §2.1 with its rider, and the rider is satisfied |
| `N-34c` | 19 | copy 1's cap-formatting collapse guard removed and the set emptied | ✅ 4 | `test_LAYER_1_scans_the_state_LABEL_and_exempts_only_the_state_JSON` |
| `N-35` | 20 | **copy 1's** `_HOLE_VOCABULARY` emptied | ✅ 1 | `test_the_attackers_context_contains_no_hole` |
| **`N-35b`** | **20** | **copy 2's probe-vocabulary tuple emptied** | 🔴 **SURVIVED** | **OWNED. Four exhibits, 20 findings each, sole-layer, control 0** |
| **`N-38`** | **22** | copy 2's claim-1 clause-IDENTIFIER regex neutered | 🔵 **SURVIVED, NOT-OWNED** | its only separating inputs are ones where HEAD is the false positive - `REVIEW_C6_6.md` §6.3 |
| **`N-39`** | **21** | **copy 2's claim-3 attack-list patterns emptied** | 🔴 **SURVIVED** | **OWNED. Four exhibits, 20 findings each, sole-layer, control 0** |
| `N-SM1` | - | `OF-153`'s obvious widening (`SM-1` re-run) | ✅ **23** | the first killer is `test_the_four_blindness_claims_hold_over_the_LOOPS_OWN_contexts` - **the CLEAN episode.** `OF-153`'s reasoning holds |
| `N-RES2` | 7 | copy 2's residue layer gated off at its `elif` rather than its `if` | ✅ 3 | `test_the_LOOP_copys_RESIDUE_layer_FIRES_on_authored_text_carrying_NO_policy_word` |

### 2.3 FOUR REAL LEAKS IN `src/` - not guard mutations

A guard that is pinned but never fired at a real leak is `INC-43`'s decorative gate.

| id | the real leak | verdict |
|---|---|---|
| **`N-RL1`** | **E1's cap inside `LAST_REFUSAL_LABEL` - `INC-42`'s mutant M17, verbatim in shape** | ✅ **KILLED, 40** |
| `N-RL2` | arm identity in `STATE_LABEL` - `OF-104`'s shape | ✅ **KILLED, 34** |
| `N-RL3` | unexplained AUTHORED text appended as a NEW LINE, carrying no policy word | ✅ **KILLED, 43** |
| `N-31` | the `data/` denial constant drifted | ✅ **KILLED, 8** |

⚠️ **`N-RL1` IS THE MOST REASSURING NUMBER HERE.** `INC-42` records that this exact shape once left
**all 65 C6 tests green**. It now dies with **40**.

### 2.4 THE POSITIVE CONTROLS - `OF-159`, BOTH PARTS

| id | what it proves | runs | verdict |
|---|---|---|---|
| `N-PC` | the clone's **SOURCE** is under test - the folded state's JSON separators widened, so every summary's bytes move | 13 | **KILLED in all 13**, 1 failure each, on `test_the_crossover_series_reproduces_against_the_REAL_seed_2001_world` |
| **`N-PC2`** | ⚠️ **`OF-159`'s `CTRL-LIVE` BY NAME** - the clone's **TEST FILE** is under test: a bare `assert False` in copy 2's own helper | 9 | **KILLED in all 9**, **14 failures each** |

⚠️ **`N-PC2` was added after slices A/B/D/E had begun**, so it was run separately against all four of
their clones as `A2`, `B2`, `D2` and `E2`. **Every clone in this run has had both controls demonstrated
inside it.** So far as this file's author can see from the rest of `docs/reviews/mutants/`, **this is
the first mutation run in this project to carry a positive control at all**, which is what `OF-159`
says and is why it is HIGH.

### 2.5 THE THREE SURVIVORS THAT CARRY THE FAIL, WITH THEIR REMEDIES

| id | property | remedy |
|---|---|---|
| `N-32` | `OP-18` - the corpus/improvisation split's partition | **one line**: give `test_every_turn_records_corpus_or_improvisation` a client that reuses the entry, or move its partition assertion into `test_a_verbatim_corpus_reuse_is_recorded_as_corpus_with_its_reference`, which already builds the all-corpus episode |
| `N-35b` | `OP-20` - copy 2's claim-2 probe vocabulary | **one fixture in copy 2**, through `_sole_layer`, mirroring copy 1's `named_leak` |
| `N-39` | `OP-21` - copy 2's claim-3 attack-list patterns | **one fixture in copy 2**, through `_sole_layer`, mirroring copy 1's |

**Raw output: `docs/reviews/independent/c6_review6_mutants_output.txt`, which carries every slice's
control lines, both provenance lines per slice, and every killer by name.**
