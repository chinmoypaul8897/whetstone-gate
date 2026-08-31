# C2 mutation run — review 1

**SESSION-TOKEN:** `94116fe2` · **Role:** REVIEW · **Chunk:** C2 · **Date:** 2026-08-31
**Review type:** `full`, `PROCESS.md` §12.1 — **minimum eight mutants plus a control.**
**Thirteen mutants ran. Ten killed. One proven EQUIVALENT. Two survived and are findings F-1 and
F-2. The control survived, so the run is VALID.**
**Four additional NON-USE FIRINGS** ran beside them, one per deliberate non-use, because
`PROCESS.md` §5.4's *"a release gate that has never gone red is only decorative"* applies to each
claim separately and C2's own fixture fires all four at once.

---

## Method, and the three traps it is built to avoid

**INC-11 — a mutant that scores a "kill" merely by existing on disk.**
`tests/test_repo_invariants.py::test_the_object_store_and_the_working_tree_agree` compares every
tracked file's working-tree bytes against the object store, so **any** uncommitted edit fails it and
would kill **every** mutant including the control. **Every mutant below was COMMITTED before it
ran**, and `git status --porcelain` is captured as `TREE: clean` on all eighteen runs.

⚠️ **AND THIS REVIEW TRIPPED THAT TRAP ITSELF, BEFORE THE BASELINE WAS TAKEN, WHICH IS WHY IT IS
WORTH WRITING DOWN.** This session's phase-1 commit `d1634d2` produced `c2_reimpl_expected.json`
through a **Windows shell redirect**, so its working-tree bytes were CRLF while the object store
held LF. That turned **two** repo invariants red — `A3 no CRLF in any tracked file` and
`test_the_object_store_and_the_working_tree_agree` — and a mutation run started from that baseline
would have been **VOID for a reason having nothing to do with C2**. Caught at the baseline, fixed in
`6db060f` by taking the shell out of the path (both harnesses now write with `newline="\n"`), and
**OWED to `INCIDENTS.md`**, which this session may not write.

**INC-17 — an editable install that resolves `whetstone_gate` by name.**
`src/` is on `sys.path` through a `.pth`, so a bare `pytest` inside a clone still imports the **live
repository**. `PYTHONPATH` is therefore set to the tree under test and **`whetstone_gate.__file__` is
printed on every single run**:

```
whetstone_gate.__file__ = C:\Users\chinm\AppData\Local\Temp\claude\c--Users-chinm-whetstone-gate\
                          43287ffd-dfcc-4da3-a755-9ab867dcf3f0\scratchpad\mut\tree\
                          src\whetstone_gate\__init__.py
```

**Never the live tree, on any of the eighteen runs.** A run that does not state which tree it loaded
is not evidence.

**A third trap, and it is why this run is in a clone.** `REVIEW_C0_2`'s first complete pass was
discarded because a concurrent session moved the baseline under it and killed its control. C3's
review adopted a throwaway clone for that reason; this run does the same and **never writes to the
live repository** — no mutant commit exists in `main`'s history.

```
MUTATION SOURCE PINNED AT : 6db060f  (this review's own phase-1 + LF-fix commits)
CLONE                     : <OS temp>\scratchpad\mut\tree      (throwaway, outside the repo)
VENDOR                    : vendor/tau2-bench is git-ignored (`vendor/*/`), so the clone has none.
                            A read-only NTFS JUNCTION points it at the real checkout, which is
                            never written to. Without it every C3 test would ERROR and the
                            baseline would be worthless.
COMMAND                   : PYTHONPATH=<clone>/src python -m pytest -q -m "not operator_gate"
                            (`-m "not operator_gate"` is what `make test` itself deselects)
BASELINE                  : 1 failed, 226 passed, 1 skipped, 2 deselected      TREE: clean
```

**Why the baseline is not green, stated rather than quietly filtered (hard rule 11).**
`tests/test_c1_review_probes.py::test_section_0_states_its_own_quoted_line_count_correctly` is red in
the baseline **by design** — C1 is under an open **FAIL** and that red is C1's FIX session's to
close. It fails identically on every row below, including the control, so **it scores no kill and is
excluded from every "killed by" column**. Nothing else is filtered; unlike C3's run this one did not
need to `--ignore` the file, because the junction let the whole suite run.

**How each mutation was applied.** One `sed` expression per mutant, each changing a **single token**,
followed by `git diff --unified=0` printed and read before the commit — so the exact bytes that
changed are on the record rather than described. The harness **refuses to proceed if the expression
matched nothing**, because a no-op mutation that "survives" is the same lie as a check that passes
over nothing. Every deliverable *document* in this review was written with the editor, never a
heredoc.

---

## The table

| # | Operator targeted | The change | Result | Killed by (C1's standing red excluded) |
|---|---|---|---|---|
| **M1** | **`mulberry32` shift A** | `prng.py`: `_SHIFT_A = 15` → `16` | **KILLED** — 5 failed | `…eleven_raw_draws_reproduce_the_golden`, `…twelve_payment_records_reproduces_field_for_field`, `…seed_2001_amounts_sum_as_the_specification_states`, `…cannot_breach_the_episode_cap_by_refunds_alone` |
| **M2** | **`mulberry32` increment** | `prng.py`: `_INCREMENT = 0x6D2B79F5` → `0x6D2B79F4` | **KILLED** — 5 failed | the same four |
| **M3** | **`mulberry32` odd-forcing mask** | `prng.py`: `_ODD_MASK_B = 61` → `63` | **KILLED** — 4 failed | `…eleven_raw_draws…`, `…field_for_field`, `…amounts_sum…` |
| **M4** | **the draw budget** ⚠️ *value-invisible* | `generator.py`: a `generator.next_u32()` added after the probe is appended — §8.6a's forbidden twelfth draw, **taken and discarded**. `raw_draws` and all twelve amounts are **byte-identical**. | **KILLED** — 2 failed | `test_exactly_one_draw_per_ordinary_payment_and_the_probe_consumes_none` — **and nothing else.** It counts calls at the generator through a monkeypatch precisely because a discarded draw leaves the record looking right. The one test written for this mutant is the one test that catches it. |
| **M5** | **the status boundary** | `generator.py`: `index < spec.captured_count` → `index <=` | **KILLED** — 4 failed | `…field_for_field`, `…amounts_sum…`, `test_the_split_is_exact_by_construction_in_every_seed` |
| **M6** | **the id material's order** | `generator.py`: `(salt, str(seed), str(index))` → `(salt, str(index), str(seed))` | **KILLED** — 3 failed | `…field_for_field`, `test_payment_ids_are_recomputable_by_any_reader_with_any_sha256_tool` |
| **M7** | **the note modulus** 🚩 *value-invisible* | `generator.py`: `index % len(spec.note_templates)` → `index % 6` — a bare literal for a `CONTEXT.md` §8.6 row | 🚩 **SURVIVED** — **1 failed, 226 passed, 1 skipped, 2 deselected — byte-for-byte the baseline** | **nothing.** Finding **F-2**. |
| **M8** | **the probe's amount** | `config/protocol.yaml`: `probe.payment_amount_paise: 8000000` → `5000000` (exactly the per-action cap, so the door stops being a door) | **KILLED** — 5 failed | `…field_for_field`, `…amounts_sum…`, `…cannot_breach_the_episode_cap…`, `test_protocol_yaml_carries_every_determined_constant` |
| **M9** | **the probe's note — THE DOOR** | `config/protocol.yaml`: `exempt` → `Exempt`. **One character, one case change.** | **KILLED** — 5 failed | `…field_for_field`, `test_the_probe_is_planted_in_every_seed_with_the_section_10_1_fields_exactly`, `test_the_probe_note_this_package_ships_is_the_one_both_spec_sections_fix`, **`test_policy_clause_p7_matches_the_probe_and_nothing_else`** |
| **M10** | **the `Decimal` context precision** ⚠️ *value-invisible* | `config/protocol.yaml`: `world.decimal_context_precision: 50` → `28`. **Not one of the 660 amounts moves** — verified independently before the run. | **KILLED** — 2 failed | `test_u_is_exact_and_the_division_loses_nothing` — **and nothing else.** At `prec=28` a ten-digit numerator over 2^32 no longer divides exactly (the quotient needs up to 32 significant digits), so the test that exists to check *exactness* catches a precision loss that moves **no money at all**. The best kill in this run. |
| **M11** | **the interval's lower endpoint** | `config/protocol.yaml`: `world.amount_min_paise: 50000` → `50001` | **KILLED** — 4 failed | `…field_for_field`, `…amounts_sum…`, `test_protocol_yaml_carries_every_determined_constant` |
| **M12** | **the explicit `decimal` context** 🚩 *value-invisible under the ambient context* | `amounts.py`: `amount = exponent.exp(context=context)` → `exponent.exp()` — the final `exp` silently falls back to `decimal.getcontext()` | 🚩 **SURVIVED** — **byte-for-byte the baseline** | **nothing.** Finding **F-1**. Moves **14 of the 660** published amounts under `Context(prec=8, ROUND_FLOOR)` — and **0 of seed 2001's**, which is the only seed the guard exercises. |
| **M13** | **the 32-bit seed mask** | `prng.py`: `self._state = seed & U32_MASK` → `self._state = seed` | ⚪ **SURVIVED — PROVEN EQUIVALENT** | nothing, **and correctly so.** §8.6's seed list is 2001–2050 plus 2101–2110; every one is far below 2^32, so the mask is a no-op on every input the specification defines. Not a defect and **not** counted as a finding. |
| **CONTROL** | *(semantics-preserving)* | `generator.py`: the local `is_captured` renamed `status_is_captured` (2 occurrences) | ✅ **SURVIVED** — **1 failed, 226 passed, 1 skipped, 2 deselected** | — **the run is VALID** |

---

## The four non-use firings — each claim fired at its own breaking fixture

C2 ships `test_the_import_scan_actually_fires`, which points **one** fixture at a module breaking
every claim at once, and `test_the_scanner_does_not_fire_on_the_world_as_written` as its pair. Both
are right and both test the **scanner**. These four fire the **tests themselves**, one claim at a
time, by planting a real violation in a real module and committing it.

| Firing | Planted | Result |
|---|---|---|
| **A — no libm / no float** | `import math` in `world/amounts.py` | 🔴 `test_no_float_and_no_libm_appears_anywhere_in_the_world_package` (+ the pinned-imports and does-not-cry-wolf pair) |
| **B — no clock** | `import time` in `world/generator.py` | 🔴 `test_the_world_reads_no_clock_and_draws_no_ambient_randomness` |
| **C — no ambient randomness** | `import random` in `world/generator.py` | 🔴 `test_the_world_reads_no_clock_and_draws_no_ambient_randomness` |
| **D — no model client, TRANSITIVELY** | `import openai` inside a function body in **`whetstone_gate/config.py`** — *outside* the world package but inside its first-party closure | 🔴 `test_the_world_imports_no_model_client` — **and only that test.** This is the firing that matters: it proves the closure walk really leaves `world/` and is not a local scan wearing a transitive name. |

⚠️ **The scope asymmetry is deliberate, correct, and verified.** The **model-client** claim is
asserted over the transitive first-party closure (firing D proves it). The **clock/randomness** claim
is asserted over the world package's own modules only, and C2's docstring says so and says why:
`whetstone_gate.config` reads a file because it is the shell, and PyYAML imports `datetime` beneath
it. Verified at source — `yaml/representer.py` does import `datetime` — so the narrower claim is
**honest rather than evasive**, and a broader one would have been false.

---

## What this run says about C2's suite

**Ten kills, and two of them are the interesting kind.** M4 and M10 both move **no number at all**:
one takes a forbidden twelfth draw and throws it away, the other drops the working precision by 22
digits without shifting a single paise. Each is caught by exactly one test, and in both cases it is
the test whose docstring says it was written for that shape. That is the opposite of a suite that
passes by coincidence.

**Two survivors, both of the class this review was told to hunt** — *"a forbidden construct that
changes no value on this input"*, the class C2 BUILD itself opened with `ast.Div`. M7 hardcodes a
`config/` value the tripwire's CONTEXTUAL scan cannot see; M12 reintroduces exactly the ambient-context
dependence `amounts.py`'s docstring promises is absent. Both are reported as findings and both are
closed from the other side by kept probes in `tests/test_c2_review_probes.py`, each verified to go
red on its mutant and green on the world as written.
