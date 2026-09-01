# `mutants/c6_mutants_2.md` — C6 REVIEW 2's mutation testing

**SESSION-TOKEN: `ec8e57ad`** · 2026-09-01 · **19 mutants · 15 KILLED · 4 SURVIVORS · 0 equivalent**

⚠️ **EVERY MUTANT RAN IN A FRESH OS TEMP CLONE, NEVER IN THIS REPOSITORY.** The clone was driven
with `PYTHONPATH` set to its own `src/` and the clone's `whetstone_gate.__file__` printed for every
run, so no measurement can have come from the working tree (INC-17's lesson, and the review prompt's
explicit instruction). Harness: `docs/reviews/independent/c6_review2_mutants.py`.

`docs/reviews/README.md`'s bar is *"minimum 8 mutants on a `full` chunk, ≥1 per invariant the chunk
touches … each killed by a named test or given an explicit equivalence proof."* The review prompt
names the properties C6 owns: **the window size, the summary budget, the determinism of the
summariser, each of the four blindness filters, the corpus split, the token counter.** All eight are
covered, several twice.

**A SURVIVOR IS A FINDING, AND FOUR SURVIVED.** Every one is proved NON-EQUIVALENT below, so none can
be discharged as a mutation that changes nothing.

Baseline on the unmutated clone: `65 passed`.

---

## The table

| id | file | operator | property attacked | verdict | killed by |
|---|---|---|---|---|---|
| **M1** | `attacker/context.py` | `history[-n:]` → `history[-(n+1):]` | window size, off-by-one | KILLED | `test_the_window_keeps_exactly_the_configured_number_of_verbatim_turns` |
| **M2** | `attacker/context.py` | `kept = history` (window removed) | window size — the spike's ~300K defect | KILLED | same |
| **M3** | `attacker/context.py` | `<= token_cap` → `<= token_cap + 1` | **summary budget** | ⚠️ **SURVIVOR** | — |
| **M4** | `attacker/context.py` | `sorted(keys)` → `list(keys)` | determinism of the summariser | KILLED | `test_identical_state_produces_byte_identical_summary_text` |
| **M5** | `attacker/context.py` | `dict(sorted(items))` → `dict(items)` | determinism — insertion order | KILLED | same |
| **M6** | `attacker/context.py` | a P1 clause appended to the system prompt | **blindness 1 — no policy string** | KILLED | `test_the_attackers_context_contains_no_policy_string` |
| **M7** | `attacker/context.py` | the door described *as* a door, on the schemas part | **blindness 2 — no hole** | KILLED | `test_the_attackers_context_contains_no_hole` |
| **M8** | `attacker/context.py` | `" (clause E1: per-action cap)"` appended to the refusal **value** | blindness 4 — a clause id | KILLED | `test_the_attackers_context_contains_no_attack_list` |
| **M9** | `attacker/loop.py` | the equality guard removed — `last_refusal = result_text` | **`REVIEW_C6_1`'s BLOCKER F-1, reverted** | KILLED | `test_the_summary_folds_ONLY_the_generic_denial_and_never_a_tool_result` |
| **M10** | `attacker/corpus.py` | the fixed 20-entry slice restored | **`REVIEW_C6_1`'s BLOCKER F-2, reverted** | KILLED | `test_the_seed_rotation_is_deterministic` |
| **M11** | `attacker/corpus.py` | case folding added to `classify_provenance` | corpus split — moves a published number | KILLED | `test_the_splits_operational_definition_names_the_TWO_UNDECLARED_bias_classes` |
| **M12** | `attacker/estimate.py` | `math.ceil` → `round` | **token counter** — under-counts | KILLED | `test_the_estimator_uses_the_divisor_its_calibration_selected` |
| **M13** | `attacker/estimate.py` | framing allowance dropped from the sum | token counter | KILLED | `test_the_estimator_applies_its_per_message_framing_allowance` |
| **M14** | `attacker/texts.py` | `return text[:-1]` → `return text` | Q-046 — byte equality never matches again | KILLED | `test_the_generic_denial_file_is_character_identical_to_CONTEXT_MD` |
| **M15** | `attacker/corpus.py` | `if not report.every_corpus_reachable:` → `if False:` | corpus split — INC-27's guard disarmed | KILLED | `test_the_guard_now_watches_REACHABILITY_and_not_merely_EMPTINESS` |
| **M16** | `attacker/context.py` | §6's answer-key columns appended to `STATE_LABEL` | **blindness 3 — no attack list** | KILLED | `test_the_attackers_context_contains_no_attack_list` |
| **M17** | `attacker/context.py` | a policy-revealing reason appended to `LAST_REFUSAL_LABEL` | **blindness 4 — no gate reason** | ⚠️ **SURVIVOR** | — |
| **M18** | `attacker/context.py` | truncation RESERVES the denial instead of tail-cutting | summary budget / §13.3's contents | ⚠️ **SURVIVOR** | — |
| **M19** | `attacker/context.py` | `<= token_cap` → `< token_cap` | **summary budget** (the other side of M3) | ⚠️ **SURVIVOR** | — |

---

## The four survivors, each proved NON-EQUIVALENT

### M3 — the cap loosened by one token

```
raw summary = 1201 chars = 401 estimated tokens   (the cap is 400)
HEAD  (`<= token_cap`)  : emitted 1200 chars = 400 tokens, truncated=True
M3    (`<= token_cap+1`): emitted 1201 chars = 401 tokens, truncated=False
```

Different bytes on the same input, and the mutant emits a summary **over** `CONTEXT.md` §8.6's row
*"attacker context summary cap = 400 tokens"* — a frozen constant. **NOT EQUIVALENT.**

### M19 — the cap tightened by one token

```
raw summary = 1198 chars = 400 estimated tokens   (EXACTLY the cap)
HEAD  (`<=`): emitted whole, 1198 chars, truncated=False
M19   (`< `): TRUNCATES the same input
```

Different bytes. **NOT EQUIVALENT.**

⚠️ **M3 AND M19 TOGETHER ARE THE FINDING, NOT EITHER ALONE.** The cap boundary is unpinned in **both**
directions: §8.6's 400-token row can be off by one either way and the entire suite stays green.
Review finding **M-7**.

### M17 — a policy-revealing gate reason in the LABEL — **BLOCKER B-2**

The mutated authored part, measured:

```
STATE SO FAR: {"episode_paise_moved":0,...,"turns_remaining":3}
LAST TOOL REFUSAL (blocked because the action exceeded the configured per-action ceiling of
5000000 paise): This action was blocked by policy.
```

C6's own claim-4 guard, `_denial_findings`, run verbatim over that text: **`NONE`**. It splits on
`LAST_REFUSAL_LABEL` and inspects only what **follows** it, so a leak **in** the delimiter is read
past by the guard's own scoping mechanism. The other three guards miss it because the text carries no
clause id, no line of `data/policy.txt` and no attack noun — measured: `"5000000" in data/policy.txt`
= **False**, `"per-action ceiling" in data/policy.txt` = **False**, any `policy.txt` line inside the
label = **False**.

**NOT EQUIVALENT**, and it puts E1's cap — `config/protocol.yaml:money.per_action_cap_paise`, a §8.6
constant — on the attacker's authored surface, on every turn, in every arm. The docstring beside the
constant asserts exactly what nothing checks: *"They are prose written by this harness, not spec text,
and **they carry no policy**."*

### M18 — truncation reserves the denial instead of tail-cutting

On a folded state that overruns the cap, HEAD's summary **drops** the denial and the mutant **keeps**
it. Different bytes. **NOT EQUIVALENT** — and it shows that nothing pins the truncation semantics in
**either** direction, which is review finding **M-8**. `CONTEXT.md` §13.3 requires the summary to
carry the folded state **and** the last denial reason and is silent on which survives a cut, so this
one needs an architect ruling before it needs a test.

---

## Coverage against the properties the prompt names

| property | mutants | outcome |
|---|---|---|
| the window size | M1, M2 | both killed |
| **the summary budget** | **M3, M18, M19** | ⚠️ **all three SURVIVE** |
| the determinism of the summariser | M4, M5 | both killed |
| blindness filter 1 — no policy string | M6 | killed |
| blindness filter 2 — no hole | M7 | killed |
| blindness filter 3 — no attack list | M8, M16 | both killed |
| **blindness filter 4 — no gate reason** | **M17** | ⚠️ **SURVIVES** |
| the corpus split | M10, M11, M15 | all killed |
| the token counter | M12, M13 | both killed |
| Q-046's denial constant | M14 | killed |
| `REVIEW_C6_1`'s two BLOCKERs, reverted as mutants | M9, M10 | both killed |

---

## A twentieth mutation, run separately because it is not a source edit

**The spend-safety walk, defeated by a planted module rather than by an operator change** — review
BLOCKER **B-3**. Planted in the temp clone: `src/whetstone_gate/provider_client.py` containing a bare
`import openai`, reached from `estimate.py` by `from whetstone_gate import provider_client as _pc` —
**the exact import form `estimate.py:86` already uses for `config`**.

```
test_the_attacker_package_imports_no_model_client_and_no_network_library   ->  1 passed
tests/test_c6_fix_probes.py -k "no_model_client or network_import"         ->  1 passed
tests/test_c6_attacker.py + fix_probes + review_probes                     ->  65 passed
```

The test's docstring says the guarantee *"cannot be evaded by putting the client one module away."*
It can. `_imported_modules` records `node.module` only, so `from whetstone_gate import X` is recorded
as `"whetstone_gate"` and resolves to the empty `__init__.py`, where the walk dies. `test_c2_world.py`
additionally queues `f"{node.module}.{alias.name}"` and catches it. C6 also has **no positive
control** — no seeded-offender test proving the scanner fires — where C2 has
`test_the_import_scan_actually_fires`.

---

## The raw run

```
============================================================================================
C6 REVIEW 2 -- MUTATION TESTING -- SESSION-TOKEN ec8e57ad
============================================================================================
clone: C:\Users\chinm\AppData\Local\Temp\c6mut-3ianrytu\tree
clone whetstone_gate.__file__ = C:\Users\chinm\AppData\Local\Temp\c6mut-3ianrytu\tree\src\whetstone_gate\__init__.py
repo  whetstone_gate.__file__ = C:\Users\chinm\whetstone-gate\src\whetstone_gate\__init__.py

BASELINE on the unmutated clone (-k c6): rc=0  failures=none
  65 passed, 626 deselected in 27.84s

id    property attacked                                                verdict  killed by
--------------------------------------------------------------------------------------------
M1    WINDOW SIZE: off-by-one, one extra turn kept verbatim            KILLED   test_the_window_keeps_exactly_the_configured_number_of_verbatim_turns
M2    WINDOW SIZE: the window removed entirely - the spike's ~300K def KILLED   test_the_window_keeps_exactly_the_configured_number_of_verbatim_turns
M3    SUMMARY BUDGET: the cap loosened by one token                    SURVIVOR -
M4    DETERMINISM: the summariser stops sorting a set-like field       KILLED   test_identical_state_produces_byte_identical_summary_text
M5    DETERMINISM: insertion order leaks into the summary bytes        KILLED   test_identical_state_produces_byte_identical_summary_text
M6    BLINDNESS 1 (no policy string): a clause leaks onto the AUTHORED KILLED   test_the_attackers_context_contains_no_policy_string
M7    BLINDNESS 2 (no hole): the door described AS a door on the autho KILLED   test_the_attackers_context_contains_no_hole
M8    BLINDNESS 4 (no gate reason): a clause id appended to the denial KILLED   test_the_attackers_context_contains_no_attack_list
M9    BLINDNESS 3 + Q-046: world text folded onto the AUTHORED surface KILLED   test_the_summary_folds_ONLY_the_generic_denial_and_never_a_tool_result
M10   CORPUS SPLIT: the fixed 20-entry slice restored (REVIEW_C6_1's B KILLED   test_the_seed_rotation_is_deterministic
M11   CORPUS SPLIT: case folding added, moving the published fraction  KILLED   test_the_splits_operational_definition_names_the_TWO_UNDECLARED_bias_classes
M12   TOKEN COUNTER: ceil -> round, so the estimator under-counts      KILLED   test_the_estimator_uses_the_divisor_its_calibration_selected
M13   TOKEN COUNTER: the per-message framing allowance dropped         KILLED   test_the_estimator_applies_its_per_message_framing_allowance
M14   Q-046: the denial constant keeps its trailing newline, so byte e KILLED   test_the_generic_denial_file_is_character_identical_to_CONTEXT_MD
M15   CORPUS SPLIT: the reachability refusal disarmed (INC-27's guard) KILLED   test_the_guard_now_watches_REACHABILITY_and_not_merely_EMPTINESS
M16   BLINDNESS 3 (no attack list): S6's answer-key COLUMNS on the aut KILLED   test_the_attackers_context_contains_no_attack_list
M17   BLINDNESS 4 (no gate reason): a POLICY-REVEALING reason, no atta SURVIVOR -
M18   SUMMARY BUDGET: truncation RESERVES the denial instead of tail-c SURVIVOR -
M19   SUMMARY BUDGET: cap TIGHTENED by one token (the other side of M3 SURVIVOR -

TOTAL 19 mutants  |  KILLED 15  |  SURVIVORS 4 ['M3', 'M17', 'M18', 'M19']  |  ANCHOR ERRORS 0 
clone removed.
```
