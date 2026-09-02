# `c7_mutants_2.md` — C7 REVIEW 2's MUTATION SWEEP

**Session `b8c31a57` · C7 · REVIEW attempt 2 · 2026-09-02/03 · ZERO provider model calls.**

**Harness** `docs/reviews/mutants/c7_review2_mutants.py` · **transcript**
`c7_review2_mutants_output.txt` · **machine-readable result** `c7_review2_mutants_result.json` ·
**survivor exhibits** `c7_review2_survivors.py` + `_output.txt` · **batch 2**
`c7_review2_mutants_batch2.txt` · **full-suite confirmation** `c7_review2_fullsuite_check.txt`.

**The required set is `docs/reviews/independent/c7_review2_criteria.md` §3 — THIRTY-EIGHT owned
properties, sealed at `37ecb90` BEFORE a single mutant was written.**

---

## §1. THE RUN'S OWN INTEGRITY, BEFORE ANY RESULT

```
CLONE            C:\Users\chinm\AppData\Local\Temp\c7rev2.65K6vp   (git archive HEAD | tar -x)
provenance       whetstone_gate.ledger.chain resolved IN THE SAME SUBPROCESS, WITH THE SAME
                 env OBJECT, immediately before EVERY suite run              <- INC-69
restores         by WRITING the captured pre-run bytes and re-hashing        <- INC-57
scoring          by FAILING-TEST-ID IDENTITY, never by a count delta         <- OF-163
BASELINE         8 failed, 203 passed, 1 skipped   (8 clone artefacts: no vendor/, no .git)
POST-RESTORE     8 failed, 203 passed, 1 skipped   identical to baseline: True
seven touched files byte-identical to their pre-run bytes: True
```

⚠️ **THREE CONTROLS, AND `OF-159` IS WHY TWO OF THEM ARE POSITIVE.** *"This project's mutation
discipline has negative controls everywhere and positive controls nowhere."*

| control | requirement | result |
|---|---|---|
| **`CTRL-KILL`** | `sort_keys=True` → `False`, which golden 5 MUST kill | **DIED** — 14 new failures |
| **`CTRL-LIVE`** | a bare `assert False` injected into the CLONE's OWN test file | **DIED** — so the tests being run are the clone's, which no `__file__` line can show |
| **`CTRL-NOOP`** | one comment word changed | **SURVIVED** |

**RUN IS SCORED.** Had either positive control survived, or the negative one died, the run would
be VOID and unscored.

⚠️ **AND ONE HARNESS DEFECT OF THIS SESSION'S OWN, RECORDED RATHER THAN SMOOTHED.** The first
launch aborted inside `run_pytest` with `UnicodeDecodeError: 'charmap' codec` —
`subprocess.run(..., text=True)` decodes with the Windows ANSI codepage and this suite's output
carries `§`, `⚠` and `₹`. **It produced NO numbers; it stopped.** `encoding="utf-8",
errors="replace"` was added, the clone was re-verified byte-identical to the live tree, and the
sweep was restarted. It is recorded because a harness that had *swallowed* that error would have
silently mis-parsed the `FAILED` lines it scores on — which is `INC-69`'s class one layer over.

---

## §2. THE FORTY-SEVEN MUTANTS

| # | site | operator / property | disposition |
|---|---|---|---|
| `CTRL-KILL` | `chain.py:231` | POSITIVE CONTROL - must DIE | **KILLED** by `test_ENTRY_1s_LINK_TO_THE_GENESIS_ROOT_IS_CHECKED_AND_ITS_BREAK_IS_DETECTED_AT_SEQ_1` +13 more |
| `CTRL-NOOP` | `control.py:132` | NEGATIVE CONTROL - must SURVIVE | **SURVIVED** |
| `M01` | `chain.py:232` | RP-01 sorted keys | **KILLED** by `test_ENTRY_1s_LINK_TO_THE_GENESIS_ROOT_IS_CHECKED_AND_ITS_BREAK_IS_DETECTED_AT_SEQ_1` +13 more |
| `M02` | `chain.py:233` | RP-02 ensure_ascii=False | **KILLED** by `test_a_non_ascii_target_is_hashed_as_utf8_and_not_escaped` +2 more |
| `M03` | `chain.py:571` | RP-03 prev_hash/hash excluded from the digest | **KILLED** by `test_ENTRY_1s_LINK_TO_THE_GENESIS_ROOT_IS_CHECKED_AND_ITS_BREAK_IS_DETECTED_AT_SEQ_1` +16 more |
| `M04` | `chain.py:571` | RP-04 the exclusion is BY KEY, not by SCHEMA (INC-32) | **KILLED** by `test_the_round_trip_is_a_check_and_not_a_tautology` +1 more |
| `M05` | `chain.py:268` | RP-05 concatenation ORDER | **KILLED** by `test_ENTRY_1s_LINK_TO_THE_GENESIS_ROOT_IS_CHECKED_AND_ITS_BREAK_IS_DETECTED_AT_SEQ_1` +12 more |
| `M06` | `chain.py:268` | RP-05 operands encoded UTF-16 | **KILLED** by `test_ENTRY_1s_LINK_TO_THE_GENESIS_ROOT_IS_CHECKED_AND_ITS_BREAK_IS_DETECTED_AT_SEQ_1` +12 more |
| `M07` | `chain.py:228` | RP-06 a binary float is SERIALISED rather than refused | **KILLED** by `test_a_float_anywhere_in_an_entry_is_refused_rather_than_serialised` +1 more |
| `M08` | `chain.py:579` | RP-07 THE RECOMPUTATION DISABLED OUTRIGHT (PROCESS.md S5.4's defect) | **KILLED** by `test_all_four_golden_5_cases_reproduce_verdict_and_first_bad_seq[C]` +6 more |
| `M09` | `chain.py:588` | RP-07 the walk carries the STORED digest forward (REVIEW 1's M08) | **SURVIVED** |
| `M10` | `chain.py:580` | RP-08 the first-bad ledger_seq is OFF BY ONE | **KILLED** by `test_all_four_golden_5_cases_reproduce_verdict_and_first_bad_seq[C]` +5 more |
| `M11` | `chain.py:583` | RP-09 case D's REASON reworded to the LINK, which is the wrong reason | **SURVIVED** |
| `M12` | `chain.py:553` | RP-10 ENTRY 1's GENESIS LINK UNCHECKED (REVIEW 1's M12 / OF-141) | **KILLED** by `test_ENTRY_1s_LINK_TO_THE_GENESIS_ROOT_IS_CHECKED_AND_ITS_BREAK_IS_DETECTED_AT_SEQ_1` |
| `M13` | `chain.py:553` | RP-10 the genesis link unchecked ONLY for the PRE-FREEZE sentinel | **KILLED** by `test_the_genesis_value_appears_in_no_string_literal_in_the_package` |
| `M14` | `chain.py:590` | RP-11 the EMPTY chain reported DETECTED | **KILLED** by `test_an_empty_ledger_is_valid_and_its_head_is_the_genesis` |
| `M15` | `chain.py:639` | RP-12 the READ path re-appends WITHOUT verifying (INC-33) | **KILLED** by `test_the_read_path_REFUSES_every_tampered_golden_5_case[B]` +3 more |
| `M16` | `chain.py:343` | RP-13 `entries` hands back the LIVE list | **KILLED** by `test_entries_are_handed_back_as_a_tuple_and_a_caller_cannot_reach_the_list` +1 more |
| `M17` | `entry.py:202` | RP-14 the entry record is NOT frozen | **KILLED** by `test_a_written_entry_cannot_be_mutated_in_place` |
| `M18` | `chain.py:397` | RP-15 ledger_seq becomes 0-based (Q-054) | **KILLED** by `test_ASSERTION_1_executed_true_implies_verdict_ALLOWED[DENIED]` +93 more |
| `M19` | `chain.py:266` | RP-16/RP-34 A CLOCK IS READ INTO THE DIGEST | **KILLED** by `test_ENTRY_1s_LINK_TO_THE_GENESIS_ROOT_IS_CHECKED_AND_ITS_BREAK_IS_DETECTED_AT_SEQ_1` +13 more |
| `M20` | `chain.py:174` | RP-17 a missing genesis_hash DEFAULTS instead of refusing | **KILLED** by `test_a_missing_genesis_hash_in_config_is_a_hard_refusal_not_a_default` +1 more |
| `M21` | `chain.py:174` | RP-18 the genesis root HARDCODED in source | **KILLED** by `test_a_missing_genesis_hash_in_config_is_a_hard_refusal_not_a_default` +2 more |
| `M22` | `build.py:268` | RP-19 ! THE FORBIDDEN INFERENCE - executed read from the harm record | **KILLED** by `test_ASSERTION_2_holds_in_the_WORLD_and_not_only_in_the_validator` +9 more |
| `M23` | `build.py:268` | RP-20 a missing `ok` becomes False instead of a refusal | **KILLED** by `test_a_log_row_whose_result_carries_no_ok_is_a_REFUSAL_and_never_a_False` |
| `M24` | `control.py:159` | RP-21 INDETERMINATE is not a GATE refusal | **KILLED** by `test_the_three_refusal_sources_are_jointly_derivable` |
| `M25` | `control.py:161` | RP-21 the residual reported as RAZORPAY | **KILLED** by `test_a_RAZORPAY_REFUSED_READ_lands_in_the_tool_layer_bucket_and_that_is_measured` +2 more |
| `M26` | `build.py:246` | RP-22 `""` normalised to None (INC-04 rebuilt) | **KILLED** by `test_receipt_is_read_from_the_calls_own_arguments_for_every_row` |
| `M27` | `entry.py:374` | RP-23 the field ORDER is sorted, so `receipt` no longer follows `target` | **KILLED** by `test_golden_5_carries_the_THIRTEEN_pre_Q062_fields_and_this_package_carries_fifteen` |
| `M28` | `entry.py:567` | RP-24 assertion 1 disabled | **KILLED** by `test_ASSERTION_1_executed_true_implies_verdict_ALLOWED[DENIED]` +2 more |
| `M29` | `entry.py:567` | RP-24 assertion 1 misses INDETERMINATE | **KILLED** by `test_ASSERTION_1_executed_true_implies_verdict_ALLOWED[INDETERMINATE]` +1 more |
| `M30` | `entry.py:574` | RP-25 assertion 2 disabled | **KILLED** by `test_ASSERTION_2_executed_true_implies_rejected_by_razorpay_False` +1 more |
| `M31` | `entry.py:582` | RP-26 assertion 3 on the FIRST COMPONENT ONLY | **KILLED** by `test_ASSERTION_3_any_non_zero_harm_component_implies_executed[fees_incurred_paise]` +2 more |
| `M32` | `entry.py:581` | RP-27 assertion 4 - a REJECTED record may carry non-zero harm | **SURVIVED** |
| `M33` | `control.py:233` | RP-28 term 1 dropped - the gate ALLOWED | **KILLED** by `test_productive_action_term_by_term_each_clause_varied_ALONE` |
| `M34` | `control.py:233` | RP-28 term 2 dropped - the world EXECUTED | **KILLED** by `test_a_RAZORPAY_REFUSED_READ_lands_in_the_tool_layer_bucket_and_that_is_measured` +4 more |
| `M35` | `control.py:233` | RP-28 term 3 dropped - no documented Razorpay error | **KILLED** by `test_productive_action_term_by_term_each_clause_varied_ALONE` |
| `M36` | `control.py:233` | RP-29 ! Q-067 REVERSED - money actions only | **KILLED** by `test_productive_action_term_by_term_each_clause_varied_ALONE` +1 more |
| `M37` | `build.py:444` | RP-31 CANARY-B's selector drops DENIED entries | **KILLED** by `test_every_log_row_becomes_exactly_one_entry_including_the_tool_layer_refusal` +1 more |
| `M38` | `entry.py:433` | RP-32 the arm/verdict table not enforced | **KILLED** by `test_a_refused_append_leaves_the_head_and_the_ledger_exactly_as_they_were` +6 more |
| `M39` | `chain.py:398` | RP-33 `turn_index` dropped from the stored entry | **KILLED** by `test_ASSERTION_1_executed_true_implies_verdict_ALLOWED[DENIED]` +93 more |
| `M40` | `__init__.py:3` | RP-35 Q-069's prohibition DELETED from the package docstring | **KILLED** by `test_Q069_the_scorer_side_prohibition_is_stated_in_the_package_itself` |
| `M41` | `chain.py:88` | RP-36 ! THE CLAIM CEILING RAISED TO AN OVERCLAIM (REVIEW 1's M39 / OF-142) | **KILLED** by `test_the_TAMPER_EVIDENCE_CLAIM_CEILING_IS_STATED_IN_chain_py_AND_IS_NOT_EXCEEDED` |
| `M42` | `build.py:419` | RP-37 `append_log` FILTERS OUT non-executed rows (hard rule 11) | **KILLED** by `test_ASSERTION_2_holds_in_the_WORLD_and_not_only_in_the_validator` +10 more |
| `M43` | `control.py:264` | RP-38 the four harm components SUMMED into a total | **SURVIVED** |
| `M44` | `build.py:401` | NOT OWNED (sealed §4) - `append_log`'s all-or-nothing batch semantics | **SURVIVED** |
| `M45` | `store.py:161` | OUTSIDE THE SEALED SET - store.write is not publish-on-complete (hard rule 10) | **SURVIVED** |

**45 mutants + 2 controls. 41 KILLED, 4 SURVIVED** (`M09`, `M11`, `M32`, `M43`), plus `M44`
(sealed NOT OWNED) and `M45` (outside the sealed set).

⚠️ **`M12` AND `M41` ARE THE FIX'S TWO FINDINGS AND BOTH ARE DEAD.** `M12` — entry 1's genesis
link unchecked, `REVIEW_7_1`'s `H-1`/`OF-141` — is killed by
`test_ENTRY_1s_LINK_TO_THE_GENESIS_ROOT_IS_CHECKED_AND_ITS_BREAK_IS_DETECTED_AT_SEQ_1`. `M41` —
the tamper-evidence claim ceiling raised to an overclaim, `H-2`/`OF-142` — is killed by
`test_the_TAMPER_EVIDENCE_CLAIM_CEILING_IS_STATED_IN_chain_py_AND_IS_NOT_EXCEEDED`. Each is
killed by **exactly one** test, and in both cases that test is the one the FIX wrote.

---

## §3. BATCH 2 — the gaps the property audit named, and one HONESTY re-run

⚠️ **`M13` IN BATCH 1 WAS KILLED BY THE WRONG TEST, AND THAT IS REPORTED RATHER THAN BANKED.** It
skipped the entry-1 link check only when `prev_hash == "PRE-FREEZE"`, and it died on
`test_the_genesis_value_appears_in_no_string_literal_in_the_package` — because the mutant
*introduced the literal*. **That kill says nothing about the link check.** `MX5` is the same
attack carrying no literal, and it is the `SM-I` shape the FIX's own comment names: the link check
skipped at entry 1 for any **non-64-hex** `prev_hash`.

Baseline `8 failed, 203 passed, 1 skipped`; post-restore identical; all six files byte-identical.

| # | operator | disposition |
|---|---|---|
| `CTRL-KILL` | `sort_keys=True` → `False` | **DIED** — required |
| `MX1` | **RP-17** — the `TODO_` **sentinel** half of the genesis refusal, bypassed by catching `UndeterminedValue` and re-reading `protocol.data` | ⚠️ **SURVIVED** |
| `MX2` | **RP-13** — a **mutator** (`drop_last`) added to the append-only API | ⚠️ **SURVIVED** |
| `MX3` | **RP-04** — the by-key exclusion made sensitive to the key's NAME (`not name.startswith("_")`) | **SURVIVED** *(bounded — see §4)* |
| `MX4` | **RP-33** — every entry stamped `ALLOWED` regardless of the gate | **KILLED** by `test_ASSERTION_1_…[DENIED]` +25 |
| `MX5` | **RP-10** — `SM-I`'s shape, no literal: the entry-1 link unchecked for a non-64-hex `prev_hash` | **KILLED** by `test_ENTRY_1s_LINK_TO_THE_GENESIS_ROOT_IS_CHECKED_AND_ITS_BREAK_IS_DETECTED_AT_SEQ_1` |
| `CTRL-NOOP` | one comment word | **SURVIVED** — required |

**`MX5`'s kill is the load-bearing result of batch 2:** the FIX's H-1 fixture pins the attack
`SM-I` found, and it pins it through its **short** shapes (`"b"*40`, `""`, `"PRE-FREEZE-2"`), not
only through the 64-hex one.

---

## §4. THE SURVIVORS, EACH DRIVEN — `c7_review2_survivors.py`

| # | property | equivalent? | disposition |
|---|---|---|---|
| **`M09`** | RP-07 | ⚠️ **YES, PROVED** | the assignment is reached **only** by falling through `if recomputed != stored["hash"]: return …`, so the two names hold the same value **by construction**; confirmed by an **18-shape** search on which the two verifiers disagree **0** times. **This is REVIEW 1's `M08`, and its verdict is confirmed independently rather than inherited.** The mutant that actually removes the recomputation is `M08`, and `M08` was **KILLED** |
| **`M11`** | **RP-09** | **NO** | ⚠️ **OWNED SURVIVOR.** The stale-digest branch's `reason` reworded to *"the link is broken"*. On golden 5 case D the verdict and seq are unchanged and the reason becomes **FALSE** — case D's link IS intact (`prev_hash == genesis`, measured). **Every `.reason` assertion in the suite is about the LINK branch or about "not an entry"; none mentions the stale digest.** `INCIDENTS.md` INC-34 is exactly *"the right verdict at the right seq for an entirely fabricated reason"* |
| **`M32`** | **RP-27** | **NO** | ⚠️ **OWNED SURVIVOR, AND THE MOST SERIOUS FINDING OF THIS REVIEW.** `if not executed:` → `if not executed and not rejected:`. A **Razorpay-REJECTED** record claiming **₹75,000** of irrecoverable outflow: HEAD refuses it, the mutant writes it. **12 of 60 writable shapes diverge.** The suite carries `test_ASSERTION_1`, `_2` and `_3` **and no assertion-4 test at all** — the parametrised assertion-3 test drives `rejected_by_razorpay=False` on every row |
| **`M43`** | RP-38 | ⚠️ **YES, PROVED** | `any(c != 0)` → `sum(c) != 0`. Every component is validated **`>= 0`** on every construction path (`entry._validate`), and over non-negative integers the two are the same predicate; **81 patterns, 0 disagreements**. §12.2's rule is about what is **REPORTED**, and `moved_money` returns a `bool`. The stronger *"there is no `total()` in this package"* is a **comment in the code**, which sealed criterion C2 does not admit as a mandate |
| **`M44`** | *(none)* | NO | **NOT OWNED**, per the seal — see §5 |
| **`M45`** | *(none)* | NO | **OUTSIDE the sealed set** — `store.write`'s publish-on-complete, which hard rule 10 names in terms and this reviewer's Phase-1 table omits. The omission is reported as this review's own |
| **`MX1`** | RP-17 | NO | the `TODO_`-sentinel clause of the genesis refusal is pinned by nothing. RP-17's **missing-key** clause **is** pinned — `M20` and `M21` both KILLED |
| **`MX2`** | **RP-13** | **NO** | ⚠️ **OWNED SURVIVOR.** Nothing in the repository enumerates `Ledger`'s public surface, so a `drop_last` lands green. `CONTEXT.md` §16 and the C7 card both say **append-only**, and §9.2's **S4** rests on the ledger being *"the one thing in the run that cannot be quietly revised"* |
| **`MX3`** | RP-04 | NO | ⚠️ **BOUNDED, AND THE BOUND IS MEASURED.** Every extra-key fixture in the repository uses the single literal `"smuggled"`, so a **name-sensitive** exclusion survives `chain.verify`. **It does NOT survive the READ path:** driven on a 15-field document, `store.from_document` returns `TamperDetected@2` for a `_smuggled` key under the mutated verifier, because `rebuild`'s round-trip identity check is independent of `verify`. **LOW** |

⚠️ **`M11` AND `M32` WERE RE-RUN AGAINST THE WHOLE SUITE**, because *"no test catches it"* measured
over four files is a claim about four files. Full suite in the clone, `c7_review2_fullsuite_check.txt`:
baseline **25 failed, 720 passed, 1 skipped, 58 errors**; under `M32` and under `M11`, **identical**
— **0 new failing ids each**; `CTRL-KILL` over the same suite produced **14**. Post-restore identical
to baseline.

---

## §5. `M44` / `OF-143` — the disposition RE-TESTED, and the FIX's five-route argument JUDGED

**The seal (`c7_review2_criteria.md` §4) recorded this determination BEFORE the mutant ran**, which
is the only thing that makes it checkable: `CONTEXT.md` §16 says *append-only, hash-chained* and
nothing about batches; no C7 card clause, no ruling and no golden mentions one. It fails criterion
**C2**. **NOT OWNED. MEDIUM. `OF-143` stays open, and this review did not touch `append_log`.**

**The FIX named four routes and added a fifth argument. Judged one by one:**

1. **`CONTEXT.md` §16** — correct; it says nothing about batches. **Sound.**
2. **Hard rule 10's *"atomic writes, publish-on-complete"*** — the FIX says this binds the **file**
   and `store.write` already satisfies it. **Sound**, and this review measured the `.partial` +
   `os.replace` implementation directly rather than accepting it.
3. **Hard rule 11** — **sound, but thinner than the argument deserves, because the builder's own
   docstring argues the OPPOSITE about the same twenty lines**: *"a refusal half way through a log
   would leave a SHORT ledger that still verifies — an episode silently missing its tail, which is
   hard rule 11's exact shape."* ⚠️ **The builder and the fix session read hard rule 11 in opposite
   directions on one function, and neither names the other.** This review's reading, and it is why
   the FIX's conclusion survives: hard rule 11's operative sentence is *"every dropped episode is
   COUNTED, categorised and printed"* — a **counting** obligation on the scorer, not an atomicity
   obligation on an in-memory batch API. The caller is refused either way and nothing goes uncounted.
4. **The builder's docstring** — correct; hard rule 2 makes a Class B choice *"recorded with
   rationale, judged at review"*, and a rationale in a docstring is **the code**. **Sound.**
5. ⚠️ **THE FIFTH, THE FIX'S OWN ADDITION: *"`M16`'s loss is silent ONLY through `OF-57`, which
   ruling 4 forbids failing C7 on, so holding the tag on `M16` would be failing C7 on `OF-57` at one
   remove."*** **PARTLY SOUND, AND THE WEAKEST OF THE FIVE.** The *silence* is indeed `OF-57`'s. But
   the **property** at stake is the batch's atomicity, not the chain's end-anchoring, and the two
   have **different remedies**: `OF-143`'s is one fixture asserting `len(ledger) == 0`; `OF-57`'s is
   an external commitment to each episode's head hash. A finding whose remedy is unrelated to
   `OF-57`'s is not `OF-57` at one remove — its **consequence** is merely amplified by `OF-57`.
   **The disposition is right and route 5 is not needed to reach it; routes 1, 2 and 4 carry it.**

⚠️ **AND THIS DISPOSITION COSTS THIS REVIEW NOTHING, WHICH IS SAID SO IT CAN BE CHECKED.** The
verdict is already **FAIL** on `M32`, `M11` and `MX2`, so marking `M44` NOT OWNED changes no
outcome. A reviewer narrowing a set on the day it would cost a verdict is the failure `Q-082`'s
safeguard exists for; there is no such incentive here.
