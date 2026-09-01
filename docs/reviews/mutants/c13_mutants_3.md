# C13 — mutation record, REVIEW 3

**Session `c09c385b`, 2026-09-02.** Third mutation run on C13. `c13_mutants.md` is REVIEW 1's
(20 mutants), `c13_mutants_2.md` is REVIEW 2's (25). **This one runs 24**: REVIEW 2's six
survivors re-run, sixteen on the fix's own new code and on the two `config/` keys, the ordering
probe against the law, and the control.

---

## 0. THE HARNESS, AND WHY EACH PRECAUTION IS THERE

| precaution | why |
|---|---|
| a **fresh OS temp clone**, never the repository | `CLAUDE.md` §4 — throwaway work goes to a fresh OS temp directory |
| **`whetstone_gate.__file__` PRINTED** on every run and asserted to lie inside the clone | a mutation run against the unmutated installed package measures nothing |
| every mutation **committed inside the clone** before pytest | REVIEW 1 records that editing without committing produced **three false SURVIVORS**, because the harness reads `git cat-file blob` |
| the **control run first in every clone** | a mutation run whose control is red measures nothing |
| `vendor/` supplied as **NTFS junctions** to the real trees | the trees are 250 MB and are read-only to the suite — verified first: `test_a_real_edit_to_the_vendored_tree_breaks_the_triple` `copytree`s to `tmp_path` and never writes to `vendor/` |
| **no `git clean` anywhere**, and `git reset --hard` only inside the temp clone | `CLAUDE.md` §4's no-destructive-commands rule |

```
whetstone_gate.__file__ = ...\scratchpad\mut\wg\src\whetstone_gate\__init__.py
CONTROL (unmutated, same clone): 98 passed, 0 failed
```

**Driver:** `docs/reviews/independent/c13_review3_mutants.py` (committed).

---

## 1. REVIEW 2's SIX SURVIVORS — re-run, and **ALL SIX KILLED**

Every polarity below was pre-committed in the Phase-1 seal `90abb2d`
(`independent/c13_review3_criteria.md` §3) before any fix artefact was opened.

| # | finding | file | the mutation | expected (sealed) | **measured** | the test that killed it |
|---|---|---|---|---|---|---|
| **M1** | **OF-96** (`N11`) | `invocation.py` | delete `or PureWindowsPath(root).is_absolute()` from `_is_relative_literal` | **KILLED** | ✅ **KILLED** 1 failed / 97 passed | `test_BOTH_path_flavours_are_pinned_including_the_WINDOWS_half` |
| **M2** | **OF-97** (`N13`) | `invocation.py` | add `"glob"` to `crashes_loudly`'s loud set `{"read_text","read_bytes","open"}` | **KILLED**, by an assertion that a glob claim is **NOT** loud | ✅ **KILLED** 1 / 97 | `test_crashes_loudly_is_pinned_in_its_FALSE_direction_too` |
| **M3** | **OF-98** (`N8`) | `invocation.py` | `len(live) != 1` → `len(live) < 1` | **KILLED**, and only a **two-construction** fixture can do it | ✅ **KILLED** 1 / 97 | `test_the_refusal_is_EXACTLY_ONE_reachable_and_not_merely_AT_LEAST_ONE` |
| **M4** | **OF-100** | `invocation.py` | `found[node.name] = node` → `found.setdefault(node.name, node)` — i.e. **restore** keeping the FIRST module-level definition, the defect direction | **KILLED** | ✅ **KILLED** 1 / 97 | `test_a_shadowed_module_function_resolves_to_the_definition_PYTHON_binds` |
| **M5** | **OF-101** (`N14`) | `branch_b.py` | `TABLE_NUMBER.fullmatch` → `.match` | **KILLED**, by a **singular-range** fixture | ✅ **KILLED** 4 / 94 | `test_the_figure_provenance_gate_goes_red_on_each_field_in_turn` (+3) |
| **M6** | **OF-102** (`N6`) | `branch_b.py` | drop `figure.table == table` from `banking_rows`' key | **KILLED**, by a size or `(table,row)` assertion — **and REVIEW 2 proved it equivalent TODAY**, so a survivor here would have needed an exhibit | ✅ **KILLED** 1 / 97 | `test_banking_rows_is_keyed_on_the_TABLE_and_not_saved_by_tuple_ORDER` |

**Six for six. Every sealed polarity held.** M4's direction is worth one line: HEAD now keeps the
**last** module-level definition, which is what Python binds, so the mutation that had to be written
was the *restoration* of `setdefault` — the defect — and it dies.

---

## 2. THE `config/` REVERTS AND THE ORDERING PROBE — **ALL EIGHT KILLED**

These are B-3's *"goes red when reverted"* proof. Sealed at §1.2 of the criteria.

| # | id | what | expected (sealed) | **measured** |
|---|---|---|---|---|
| **M7** | `P-B3-4-revert-a` | `branch_a_condition` reverted to REVIEW 2's measured string *"the model id is still served AND the run completes inside the 90-minute box"* | **RED** | ✅ **KILLED** 1 / 97 |
| **M8** | `P-B3-5-delete-b` | the `branch_b_condition` key deleted entirely | **RED** | ✅ **KILLED** 1 / 97 |
| **M9** | `P-B3-6a` | delete *"ON A CAUSE THAT HAS BEEN DIAGNOSED AND "* from the config value | **RED** | ✅ **KILLED** 1 / 97 |
| **M10** | `P-B3-6b` | delete *"'It errored' is not a cause, and "* | **RED** | ✅ **KILLED** 1 / 97 |
| **M11** | `P-B3-6c` | delete *"a harness defect is NEVER Branch B - "* | **RED** | ✅ **KILLED** 1 / 97 |
| **M12** | `P-B3-6d` | delete *"RECORDED IN PROTOCOL.md BEFORE A BRANCH IS SELECTED. "* | **RED** | ✅ **KILLED** 1 / 97 |
| **M13** | ⚠️ **`P-B3-7-law`** | **amend `CONTEXT.md` §8.5.1 ONLY** — remove *"ON A CAUSE THAT HAS BEEN DIAGNOSED"* — and leave `config/` untouched | ⚠️ **RED, AND RED AT THE LAW.** If it stayed green the phrase list would be a copy. | ✅ **KILLED**, and the message is the law's: `AssertionError: CONTEXT.md §8.5.1 no longer carries the diagnosis requirement ('on a cause that has been diagnosed'). This test requires it of config/ ONLY because the law states it; if the law moved, config/ is not the thing to correct and this assertion is the one that must be read first.` |
| **M14** | `C-ctl` | the control | **GREEN** | ✅ **98 passed, 0 failed** |

**M13 is the one that decides B3-i**, and it lands exactly where it was pre-committed to land.
Each phrase of `config/` dies **individually** (M9–M12), so the guard is not a single lump.

---

## 3. THE FIX'S OWN NEW CODE — **16 run, 11 killed, 5 NON-EQUIVALENT SURVIVORS**

⚠️ **No review has seen any of this code.** The surface is `branch_condition_problems`,
`branch_conditions_are_stale`, `BRANCH_B_REQUIREMENTS`, `SUPERSEDED_BRANCH_TRIGGER` and the new
test. The minimum the prompt asks for is 8.

### 3.1 Killed

| # | id | the mutation | **measured** |
|---|---|---|---|
| **M15** | `N-A-superseded` | `SUPERSEDED_BRANCH_TRIGGER` → a string that never occurs | ✅ **KILLED** 1 / 97 |
| **M16** | `N-F-no-refusal` | the predicate stops refusing the superseded trigger (`if False and …`) | ✅ **KILLED** 1 / 97 |
| **M17** | `N-G-empty-is-pass` | a blank / non-string condition reads as a **pass** — `Q-079`'s actual HEAD state | ✅ **KILLED** 1 / 97 |
| **M18** | `N-H-skip-b-half` | the whole `branch_b_condition` half of the predicate never runs | ✅ **KILLED** 1 / 97 |
| *(M7–M13 above also exercise this surface end to end.)* | | | |

### 3.2 ⚠️ SURVIVORS — five, each **NON-EQUIVALENT BY EXHIBIT**

The exhibit is a `branch_b_condition` on which HEAD and the mutant **disagree**, measured by calling
the predicate directly. `A` is held at HEAD's `branch_a_condition` throughout.

| # | id | the mutation | the exhibit | HEAD flags | mutant flags |
|---|---|---|---|---|---|
| **M19** | `N-B-req-diagnosed` | `"on a cause that has been diagnosed"` → `"cause"` | *"THE RUN DOES NOT COMPLETE **for some cause**. 'It errored' is not a cause, and a harness defect is never Branch B; recorded in PROTOCOL.md before a branch is selected."* | **1** | ⚠️ **0** |
| **M20** | `N-C-req-harness` | `"a harness defect is never branch b"` → `"harness"` | *"… and a harness defect is **SOMETIMES** Branch B …"* — **the direct inversion of `Q-057`'s ruling** | **1** | ⚠️ **0** |
| **M21** | `N-D-req-protocol` | `"protocol.md"` → `"md"` | *"… recorded in **CONTEXT.md** before a branch is selected …"* — the wrong file | **1** | ⚠️ **0** |
| **M22** | `N-E-drop-one-req` | delete one whole `BRANCH_B_REQUIREMENTS` entry (the harness-defect exclusion) | same as M20's | **1** | ⚠️ **0** |
| **M23** | `N-I2-loader-bypass` | `lanes.require(…)` → `lanes.data.get("camel_comparator", {}).get(key, "")` | `config/lanes.yaml`'s `branch_b_condition` set to the **sentinel** `TODO_C14_PENDING` | **1**, and it is `UndeterminedValue: … is not determined yet (sentinel 'TODO_C14_PENDING')` — hard rule 9's **refusal** | ⚠️ **4**, four content complaints — **the sentinel is USED as a value, not refused** |

⚠️ **AND THEY SURVIVE THE WHOLE REPOSITORY, NOT ONLY THE C13 FILE.** M19+M20+M21+M23 applied
**together**, full suite: **2 failed, 722 passed, 1 skipped** — and both failures are the two
pre-existing reds (the deliberate `camel_comparator.branch` sentinel and `Q-080`/`INC-49`'s E5).
M22 alone, full suite: **2 failed, 722 passed, 1 skipped** — the same two. **Nothing anywhere kills
them.**

**The mechanism, which is one defect and not five.** `tests/test_c13_camel_comparator.py:1116-1121`:

```python
undiagnosed = invocation.branch_condition_problems(condition_a, "the run does not complete")
assert len(undiagnosed) == len(invocation.BRANCH_B_REQUIREMENTS)      # <-- tautological
for what, _ in invocation.BRANCH_B_REQUIREMENTS:
    assert any(what in problem for problem in undiagnosed)            # <-- tautological
```

Both assertions compare the predicate's **output** against the predicate's **own input list**, so
neither can fail when that list changes. And the law-side assertion — `assert phrase in section` —
passes for every weakened phrase, because `"cause"`, `"harness"` and `"md"` all occur in §8.5.1.
The one fixture, `"the run does not complete"`, contains none of the four phrases in **any**
strength, so it cannot separate a strong requirement from a weak one. ⚠️ **That is `INC-50`'s class,
in the fix's own new code, on the same night `INC-50` was written about it.**

### 3.3 One mutant withdrawn as EQUIVALENT — **and it is this reviewer's error, not the fix's**

| # | id | why it is equivalent |
|---|---|---|
| **M24** | `N-I-loader-bypass` (first form) | it was guarded by `hasattr(lanes, "get")`, and `Config`'s public surface is `['data','has','name','path','require','sentinels']` — **no `get`** — so the expression falls through to `require()` and the mutation is a **no-op**. Withdrawn and **replaced by M23**, which uses the real API. Recorded rather than deleted: a mutant that cannot change behaviour is not evidence, and dropping it silently would inflate the survivor count by one. |

---

## 4. TALLY

| | count |
|---|---|
| mutants run | **24** (plus 1 withdrawn as equivalent-by-construction) |
| **KILLED** | **18** |
| **SURVIVED, non-equivalent by exhibit** | ⚠️ **5** |
| proven equivalent | **1** (M24, this reviewer's own ill-formed mutant) |
| control | **GREEN — 98 passed, 0 failed**, in every clone |

**REVIEW 2's six survivors: 6 / 6 KILLED.**
**B-3's revert proof: 8 / 8 RED, including the ordering probe against the law.**
**The fix's own new surface: 11 killed, 5 survived.**
