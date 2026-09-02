# `c6_mutants_4.md` — C6, mutation record, REVIEW 4

**SESSION-TOKEN: `ca0dd160`** · **Date:** 2026-09-02 · **Chunk:** C6, the attacker loop
**Reviewed at:** `bd2107f` + this session's own two commits (`daefb31`, `11193bd`)
**Baseline on the unmutated clone: `111 passed`.**

⚠️ **THIS FILE IS ALSO THE OWED `c6_mutants_4.md` FOR C6 FIX 3 (`363a2e9f`).** That session ran
fourteen self-directed mutants and could not write them here — `docs/reviews/mutants/` was outside
its fence — so it named the debt in `docs/sessions/nightrun-a-1.txt` rather than skipping it.
**Its fourteen are transcribed in §4 below, from its own record, and this session's independent
re-run of the ones that matter is in §1 and §3.** The debt is discharged here.

---

## 0. METHOD, AND WHICH TREE EVERY NUMBER CAME FROM

Every mutation ran in a **fresh OS temp clone**, never in this repository:

```
whetstone_gate.__file__ = C:\Users\chinm\AppData\Local\Temp\claude\...\scratchpad\c6r4\tree\src\whetstone_gate\__init__.py
working tree            = C:\Users\chinm\whetstone-gate\src\whetstone_gate\__init__.py
```

Per mutant: applied by **exact-string replacement** (the anchor asserted to match **exactly once**,
so a mutant that silently applied nowhere is impossible), file SHA-256 asserted **changed**, the
mutation **committed inside the clone**, the suite run, the original bytes written back, the digest
asserted **back**, and `git status --porcelain` asserted **empty**.

⚠️ **THE FIRST RUN OF THIS SESSION'S HARNESS WAS INVALID AND IS RECORDED RATHER THAN QUIETLY
REPLACED.** The restore step ended with `git checkout -- <path>`, which restores from **HEAD** — and
HEAD held the mutation, because the harness commits it. So every mutant re-applied its predecessor
and the failure counts ran **2, 4, 8, 11, 15, 18** instead of **2, 2, 4, 3, 4, 3**. Caught by the
monotone count, fixed by restoring **by writing the original bytes and committing them**, and the
clone was reset to the sealed content and re-baselined at **111 passed** before anything was
re-measured. Both runs are in this session's record; only the second is cited.

**Suite run per mutant:** `tests/test_c6_attacker.py`, `tests/test_c6_fix_probes.py`,
`tests/test_c6_review_probes.py` — C6's three files. `vendor/` is git-ignored, so a clone has no
τ²-bench and C3's tests error there; they are excluded for `REVIEW_C6_1`'s stated reason (they
would "kill" every mutant including the control) and **no C6 mutant touches τ².**

**SPEND: ZERO. NO PROVIDER MODEL CALL WAS MADE.** Every client in every run is a mock.

---

## 1. `REVIEW_C6_3`'s SIX SURVIVORS — RE-RUN BY THIS SESSION. **ALL SIX KILLED.**

| id | file:target | operator | verdict | killed by |
|---|---|---|---|---|
| **N4** | `attacker/estimate.py` `CrossoverSeries.crossing` | `> target` → `>= target` | ✅ **KILLED** `2 failed` | `test_the_crossing_is_STRICTLY_over_the_target_and_is_pinned_at_the_boundary_BOTH_WAYS`, `test_the_crossing_returns_ZERO_when_the_base_alone_already_exceeds_the_target` |
| **N9** | `tests/test_c6_attacker.py` `_imported_modules` | the whole `if node.level:` relative resolution deleted | ✅ **KILLED** `2 failed` | `test_the_import_scan_fires_on_a_RELATIVE_import_too[×2]` |
| **N12** | `_denial_findings` | LAYER 3, the residue catch-all, deleted | ✅ **KILLED** `4 failed` | `test_LAYER_3_is_the_SOLE_killer_of_authored_text_carrying_no_policy_word[×4]` |
| **N13** | `_denial_findings` | `refusal_lines != 1` → `< 1` | ✅ **KILLED** `3 failed` | `test_the_denial_line_COUNT_is_the_SOLE_killer_of_a_summary_with_more_than_one[two, three, five]` |
| **N14** | `_denial_findings` | the `value != generic` block deleted | ✅ **KILLED** `4 failed` | `test_the_denial_equality_is_the_SOLE_killer_of_a_value_that_leaks_nothing_else[×3]`, `test_the_sole_killer_helper_REJECTS_a_shape_that_two_layers_catch` |
| **N15** | `_denial_findings` | LAYER 1's exemption widened from the state **JSON** to the whole state **LINE** | ✅ **KILLED** `3 failed` | `test_LAYER_1_scans_the_state_LABEL_and_exempts_only_the_state_JSON[×3]` |

⚠️ **AND THE KILLS ARE BY THE RIGHT TESTS, WHICH IS THE HALF A COUNT DOES NOT SHOW.** Every killer
names the property its mutant attacks; none is an incidental byte-count kill, which is what
`REVIEW_C6_3` measured for the label class (*"they die on one test … because a longer label changes
the summary's character count"*). **N4's fixture derives its boundary base from `config/`** —
`base = target − 8 × per_read` = **17,616**, recomputed here independently and agreeing exactly with
`OF-108`'s exhibit — rather than writing `17616` down, so it cannot drift silently.

---

## 2. `_sole_killer` ITSELF — MUTATED THREE WAYS, ALL THREE KILLED

The claim under test: *"every fixture is built so the mutated assertion is the **SOLE** killer, and
`_sole_killer` asserts exactly that."* A helper that asserts exclusivity is worth only what its own
exclusivity check is worth.

| id | operator | verdict | killed by |
|---|---|---|---|
| **R-01** | `assert len(matched) == len(findings)` → `>= 1` — **the exclusivity half deleted** | ✅ **KILLED** `1 failed` | `test_the_sole_killer_helper_REJECTS_a_shape_that_two_layers_catch` |
| **R-02** | `matched = [f for f in findings if fragment in f]` → `list(findings)` — **the identity half deleted** | ✅ **KILLED** `1 failed` | same |
| **R-03** | the helper made a **no-op** (`return` at the top) | ✅ **KILLED** `1 failed` | same |

⚠️ **PHASE 1 PREDICTED R-01 AND R-02 WOULD SURVIVE, AND THEY DO NOT. THAT PREDICTION WAS SEALED AT
`11193bd` AND IS REPORTED AS A MISS.** The reasoning was sound — a suite whose fixtures are all
single-layer cannot notice the exclusivity clause going away *unless a self-test exists* — and the
self-test exists. `test_the_sole_killer_helper_REJECTS_a_shape_that_two_layers_catch` fires the
helper at `"STATE SO FAR [DENIED once]: "`, a shape caught **twice** (LAYER 2's `denied` and the
surface scan's `DENIED`), asserts `pytest.raises(AssertionError, match="caught by more than one
layer")`, **and fires it in the other direction too** so it cannot be satisfied by a helper that
always raises. C6 FIX 3 found this itself as its own survivor `SM-2` and closed it. **It is the
strongest single thing in this fix.**

---

## 3. NEW-SURFACE MUTANTS — 22 RUN, 10 KILLED, **5 EQUIVALENT (boundary named), 7 NON-EQUIVALENT SURVIVORS**

Targets: `_sole_killer`, the three-layer scan's subtraction-by-identity, the residue parser, the
copy-2 route, `OF-110`'s source-text scan, and `crossing()`. **No review had seen any of it.**

### 3.1 KILLED — 10

| id | target | operator | verdict | killed by |
|---|---|---|---|---|
| R-01, R-02, R-03 | `_sole_killer` | §2 | ✅ KILLED | §2 |
| **R-04** | LAYER 2 | the §8.6 system-prompt subtraction **removed entirely** | ✅ **KILLED** `20 failed` | `test_the_attackers_context_contains_no_gate_denial_reason` + 19 others |
| **R-10** | LAYER 2b | the `\barms?\s*[1-4]S?\b` alternative removed | ✅ **KILLED** `3 failed` | `test_the_denial_guard_sees_an_arm_identity_in_a_LABEL_not_only_in_the_value[×3]` |
| **R-11** | LAYER 2b, **COPY 1** | `OF-104`'s scan removed entirely | ✅ **KILLED** `5 failed` | same + `test_the_sole_killer_helper_REJECTS…` |
| **R-13** | LAYER 2b, **COPY 2** | `OF-104`'s scan removed entirely (`N-M1b`) | ✅ **KILLED** `3 failed` | `test_the_LOOP_copys_own_claim_4_scan_ACTUALLY_FIRES_on_a_leaky_label[×3]` |
| **R-16** | `_dynamic_reach_findings` | the source-text scan disabled | ✅ **KILLED** `5 failed` | `test_the_dynamic_reach_scan_ACTUALLY_FIRES_on_every_form_the_ast_walk_misses[×5]` |
| **R-17** | `_REFUSED_DYNAMIC_REACH` | `("getattr", …)` removed | ✅ **KILLED** `2 failed` | same + `test_the_dynamic_reach_refusal_list_is_pinned` |
| **R-19** | `crossing()` | `range(0, …)` → `range(1, …)` — the **k = 0** case (`SM-6`) | ✅ **KILLED** `1 failed` | `test_the_crossing_returns_ZERO_when_the_base_alone_already_exceeds_the_target` |

⚠️ **`R-13` IS THE ONE THAT MATTERS MOST AND IT DIES.** `N-M1b` — deleting `OF-104`'s scan from
**copy 2** — left all 99 tests green when C6 FIX 3 mutated its own work, *because copy 2 had never
been fired at a leak at all*. It is fired at three leaky labels now, **through `run_episode`'s real
output**, and the mutant dies with three named failures. That closure is real.

### 3.2 EQUIVALENT — 5, each with the boundary NAMED

An equivalence claim must enumerate the reachable inputs, show agreement on all of them, **and name
the input that WOULD separate them.** That is `REVIEW_C6_3`'s own `N6` standard.

| id | operator | proof | the boundary, named |
|---|---|---|---|
| **R-06** | LAYER 3: the STATE line contributes **no** residue | **BY CONSTRUCTION.** When the line is untruncated, `state_json` **is the whole body**, so `line − STATE_LABEL − state_json` is empty; when it is truncated, the residue is the mark, which the following `re.sub` removes. **The STATE line can never contribute residue under HEAD either.** Measured: HEAD `[]`, mutant `[]` | **none exists** — but see §5 **F-2**: that is *why* an appended same-line leak escapes all three layers |
| **R-07** | LAYER 3: the REFUSAL line contributes **no** residue | **BY CONSTRUCTION.** `value = line[len(label):].strip()`, so `line − label − value` is whitespace for every line that starts with the label. Measured over **9** constructed refusal shapes (three suffixes × three values, including `NO_REFUSAL` and the empty value): **0 separating inputs** | `label` not a prefix of the line — impossible, the branch is entered on `startswith` |
| **R-09** | `state_json = body` always (the truncation mark stops delimiting) | **BY EXHIBIT.** With an 80-key state the mark lands at char 972 of 1125; the only text after it is the authored mark plus its dropped-entry count, and **no `config/` ceiling rendering appears there** | `entries_dropped ∈ {50000, 5000000, 200000, 20000000}` — a 20-turn episode's folded state cannot reach 50,000 entries |
| **R-21** (`SM-1`) | `_with_extra_summary_line`: the `Origin.AUTHORED` filter dropped | ⚠️ **C6 FIX 3's proof is INCOMPLETE and the correct one is supplied here.** Its claim — *"1 WITH the origin filter and 1 WITHOUT it, EVERY TIME, so the helper returns a byte-identical context either way"* — is **FALSE in general**: an `ATTACKER` part echoing `"STATE SO FAR: "`, or a `WORLD` tool result carrying it, gives HEAD `replaced=1` and the mutant `replaced=2`. **The sound proof is different and stronger: on every such input the mutant's own `assert replaced == 1` RAISES, so the mutant is *identical or louder*, never silently different — and the AUTHORED surface is byte-identical even then** | an `ATTACKER`/`WORLD`/`CORPUS` part containing `STATE_LABEL`, **with `replaced == 1` also disarmed** |
| **R-22** (`SM-5`) | `assert replaced == 1` → `>= 0` | **BY CONSTRUCTION**, and it matches `REVIEW_C6_3`'s own `N10` precedent exactly: disarming an assertion true on every input the suite supplies cannot fail for any suite | a context with **zero** parts carrying `STATE_LABEL`; measured, HEAD's assertion would fire and the mutant would return the context unchanged |

### 3.3 ⚠️ NON-EQUIVALENT SURVIVORS — 7, each with a CONCRETE distinguishing exhibit

**Three carry the FAIL. Four do not, and this file says which.**

| id | severity | target | the exhibit on which HEAD and the mutant differ | carries the FAIL? |
|---|---|---|---|---|
| **R-14** | **MEDIUM** | **COPY 2**: `mandated.replace(line[len(STATE_LABEL):], …)` → `replace(line, …)` — LAYER 1's exemption widened from the state **JSON** to the whole state **LINE** | `STATE_LABEL = "STATE SO FAR (5000000): "` over a real 20-turn episode → **HEAD 40 findings, mutant 0.** ⚠️ **THIS IS `N15` / `OF-107`'s CLASS, IN COPY 2.** Copy 1 got `test_LAYER_1_scans_the_state_LABEL_and_exempts_only_the_state_JSON` with three cap formattings **and** the other-side test; copy 2 got neither. Measured over the file: `exempts_only_the_state_JSON` → **absent**; a copy-2 test planting a cap in `STATE_LABEL` → **absent** | ✅ **YES** |
| **R-15** | **MEDIUM** | **COPY 2**: `refusal_lines != 1` → `< 1` | a summary carrying **two** recognisable last-denial lines → **HEAD 20 findings, mutant 0.** ⚠️ **THIS IS `N13` / `OF-111`'s CLASS, IN COPY 2.** Copy 1 got a three-count fixture (2, 3, 5); copy 2 got none | ✅ **YES** |
| **R-20** | **MEDIUM** | `crossing()`: `range(0, turn_budget + 1)` → `range(0, turn_budget)` | a series with `full_listing_chars = 1600` (a **paginated** read, not the 12-payment listing), `displaced = 240`, `base_tokens = 5521` — **all positive and realistic**: `tokens_at(19) = 57,277 ≤ 60,000 < tokens_at(20) = 60,001`. **HEAD returns `20`; the mutant returns `None`.** ⚠️ `None` makes `crossover_note()` print *"NO number of full-listing reads inside 20 turns crosses 60,000"* — **a sentence instead of a number, which its own docstring calls a different finding for C14.** `OF-108` pinned the **target** boundary in both directions and `R-19` shows the **k = 0** end is pinned; **the `turn_budget` end is pinned by nothing** | ✅ **YES** |
| **R-18** | LOW | `_dynamic_reach_findings`: `package.rglob("*.py")` → `glob` | a dynamic import in `attacker/sub/reach.py` → **HEAD 2 findings, mutant 0.** Latent: `attacker/` is flat today, and all five positive-control packages put `reach.py` at the top level | no — latent |
| **R-08** | LOW | `assert len(summaries) == 1` → `>= 1` | a **second** AUTHORED part carrying `STATE_LABEL` → HEAD's parser assertion fires (loud), the mutant proceeds silently on `summaries[0]`. No code path builds two | no |
| **R-12** | LOW | LAYER 2b run over `values_scan` instead of `scan` | `idempotency_keys_seen = ("arm 2S",)` inside the **folded state** → HEAD `["2b 'arm 2S'"]`, mutant `[]`. **HEAD is the stricter one**, and the surface is §8.6's folded state, which **C7's ledger fills** — this review pre-committed at `11193bd` (P-29) that an escape *there* is not a C6 defect | no — and it is named so the count is not padded |
| **R-05** | LOW | LAYER 2: `.replace(system_prompt, "\n")` → `count=1` | the §8.6 system prompt present **twice** → HEAD `[]`, mutant `["vocab 'limits'"]`. ⚠️ **The mutant is STRICTER and WRONG** — it reports the second copy's own tradecraft words as a leak. HEAD is correct; only the strictness choice is unpinned | no — the mutant is a false-positive generator |

---

## 4. C6 FIX 3's OWN FOURTEEN — THE OWED TABLE, TRANSCRIBED

From `docs/sessions/nightrun-a-1.txt` §2c, verbatim in content. **First run: 9 KILLED / 5 SURVIVED,
and every survivor was on code that session had just written.**

| id | what | first run | final | verified independently here |
|---|---|---|---|---|
| `N-M1a` | `OF-104`'s scan removed from **COPY 1** | KILLED | KILLED, 5 failed | ✅ **R-11**, 5 failed — agrees exactly |
| `N-M1b` | `OF-104`'s scan removed from **COPY 2** | **SURVIVED** | KILLED, 3 failed | ✅ **R-13**, 3 failed — agrees exactly |
| `SM-1` | `_with_extra_summary_line`: AUTHORED filter dropped | **SURVIVED** | EQUIVALENT | ⚠️ **R-21** — survives; the claim is **incomplete**, §3.2 supplies the sound proof |
| `SM-2` | `_sole_killer`'s exclusivity assertion weakened | **SURVIVED** | KILLED, 1 failed | ✅ **R-01**, 1 failed — agrees exactly |
| `SM-3` | `OF-104`'s scan narrowed: `arms?` alternative removed | KILLED | KILLED, 3 failed | ✅ **R-10**, 3 failed — agrees exactly |
| `SM-4` | the `N9` sibling row's client not planted | KILLED | KILLED, 1 failed | not re-run — a fixture-integrity mutant |
| `SM-5` | `_with_extra_summary_line`: `replaced == 1` disarmed | **SURVIVED** | EQUIVALENT | ✅ **R-22** — survives; the proof is **SOUND**, §3.2 |
| `SM-6` | `crossing()`'s k = 0 case removed | **SURVIVED** | KILLED, 1 failed | ✅ **R-19**, 1 failed — agrees exactly |

**Its remaining six** (the un-named KILLED rows of its first run) are not individually listed in its
session file and are not invented here.

⚠️ **EVERY ONE OF ITS SIX CLAIMS THIS SESSION COULD RE-RUN REPRODUCES, INCLUDING THE FAILURE
COUNTS.** The one claim that does not survive audit is `SM-1`'s **equivalence argument**, not its
verdict: the mutant does survive and is safe, but for a different and better reason than the one it
gave.

---

## 5. WHAT THE MUTANTS SURFACED THAT IS NOT A MUTANT

Recorded here because the exhibits were built by the same harness.

* **F-1 — two of `OF-104`'s own three measured exhibits still escape BOTH copies.** `OF-104`'s
  measurement table lists three shapes; the remedy it ruled — *run the arm/clause regex over `scan`*
  — was verified in `OF-104` against two **digit-bearing** shapes (`arm 2S`, `arm 4`). Measured here
  against all four guards in both copies: `"LAST TOOL REFUSAL (the gate judge rejected it; arm one
  would have allowed it): "` → **copy1 0, copy2 0**; `"STATE SO FAR (this arm runs a live judge): "`
  → **copy1 0, copy2 0**; `"LAST TOOL REFUSAL (arm 2S): "` → **copy1 1, copy2 20**.
* **F-2 — authored text appended to the STATE LINE escapes all three layers.** `"operator note:
  reviewed"`, `"[reviewed by the standing checker]"` and `"a judge looked at this one"` each escape
  when appended to the state **line**, and each is caught when added as a **new** line. `R-06`'s
  by-construction proof is the mechanism: `state_json` is the whole body, so the state line yields
  no residue, and `_with_extra_summary_line` only ever adds a new line.
* **F-3 — of 118 needles planted inside `LAST_REFUSAL_LABEL`, 72 are caught and 46 escape**; all 118
  are caught in the refusal **value** and all 118 as a **new-line residue**. The label is the weak
  surface, and the escaping families are answer-key vocabulary (5 of 15), config key names (0 of 6),
  extra folded-state field names (0 of 8) and paraphrases (2 of 7).

---

## 6. TOTALS

| | |
|---|---|
| mutants run by this session | **28** (6 re-runs + 22 new-surface) |
| **KILLED** | **16** |
| **EQUIVALENT, boundary named** | **5** |
| **NON-EQUIVALENT SURVIVORS** | **7** — three MEDIUM (`R-14`, `R-15`, `R-20`), four LOW |
| baseline on the unmutated clone | **111 passed** |
| control | the baseline itself: the unmutated clone is green, and every mutant's anchor is asserted to match **exactly once** |
| provider model calls | **ZERO** |

**`docs/reviews/README.md`'s bar — *"every mutant killed or proven equivalent"* — is NOT met. Seven
survive and are not equivalent.**
