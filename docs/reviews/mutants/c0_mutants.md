# C0 mutation run — re-review, attempt 2

**SESSION-TOKEN:** `f57e216b` · **Role:** REVIEW · **Chunk:** C0 · **Date:** 2026-08-31
**Review type:** `code` (persona 2), `PROCESS.md` §12.1 — **minimum four mutants**. Fourteen ran.

---

## Method, stated so it can be re-run, and so its two known traps are visibly avoided

**INC-11's trap — a mutant that only has to EXIST ON DISK to look killed.**
`tests/test_repo_invariants.py::test_the_object_store_and_the_working_tree_agree` fires on **any**
uncommitted edit to a tracked file. Attempt 1's first run scored 18/18 that way — **control mutant
included** — and had to be discarded. **Every mutant here is applied to a fresh clone and
COMMITTED**, and `git status --porcelain` is captured and reported as `tree clean` for each. That is
the state a real defect actually lives in.

**INC-17's trap — an editable install that resolves `whetstone_gate` BY NAME.**
`C:\Users\chinm\whetstone-gate\src` is on `sys.path` through a `.pth` file, so standing inside a
clone and running `pytest` imports **the live repository**, not the checkout. Reproduced
independently by this session before any measurement was taken:

```
$ cd <clone at 864c621> && python -c "import whetstone_gate; print(whetstone_gate.__file__)"
C:\Users\chinm\whetstone-gate\src\whetstone_gate\__init__.py     <- THE LIVE REPOSITORY

$ PYTHONPATH=<clone>/src python -c "import whetstone_gate; print(whetstone_gate.__file__)"
<clone>\src\whetstone_gate\__init__.py                            <- the checkout
```

So **`PYTHONPATH` is set to the tree under test for every run, and `whetstone_gate.__file__` is
printed for every run.** `config.repo_root()` is `Path(__file__).resolve().parents[2]`, so it
follows `PYTHONPATH` into the clone and the whole run is self-consistent. A run that does not state
which tree it loaded is not evidence, and every row below states it.

**A third trap, found and fixed inside this run, recorded because it invalidated a first pass.**
The harness first wrote each mutant with `pathlib.Path.write_text`, which on Windows translates
`\n` to `\r\n`. Every mutant therefore also became a **CRLF defect** and was killed through A3/A4
rather than through its own semantics — the tell was
`test_the_object_store_and_the_working_tree_agree` failing on mutants that touch no line-ending
code at all, and `check-roles` exiting 1 on every row. The harness now writes **bytes** and asserts
`b"\r\n" not in` the mutated file. Same family as INC-06, INC-09 and INC-16.

**A fourth, and this one voided a complete pass.** The first pinned run cloned from the live
repository, which the **concurrent C1 review (pair P-02, token `a0cc0212`)** was committing to at
the same time. The baseline moved under the run, a new C1 probe
(`test_section_0_states_its_own_quoted_line_count_correctly`) began failing in the baseline, and
**the control mutant was scored KILLED by it.** Per the prompt's own rule — *a run whose control is
killed is void* — that pass was discarded. **The source is now pinned at one commit and the whole
set was re-run against it.**

```
MUTATION SOURCE PINNED AT: 68fcfff1db1af6d6bb1c546140f697b49a430680
BASELINE at that pin:      171 passed, 1 skipped, 2 deselected · check-roles rc=0
COMMAND:                   pytest -q -m "not operator_gate"
                             --ignore=tests/test_c3_tau2_enumeration.py
                             --ignore=tests/test_c1_review_probes.py
                           python -m whetstone_gate.tasks check-roles
```

**Why those two files are ignored, stated rather than quietly dropped (hard rule 11):**

* `tests/test_c3_tau2_enumeration.py` — needs `vendor/tau2-bench`, which is git-ignored under
  Q-010 and is therefore **absent from any clone**. It contributes **8 failures and 12 collection
  errors to the BASELINE**, identically on every row, so including it would add twenty constant
  failures and distinguish nothing. It is C3's chunk, not C0's. See REVIEW_C0_2.md I-01.
* `tests/test_c1_review_probes.py` — one test in it is **red in the live repository right now**,
  standing over the C1 review's own BLOCKER. It is C1's chunk, not C0's, and it is baseline noise
  for a C0 mutation oracle. See REVIEW_C0_2.md I-02.

With both excluded the baseline is **completely green**, so every failure in every row below is
attributable to the mutation and to nothing else.

---

## The table

`__file__` was `…\scratchpad\mut\<ID>\src\whetstone_gate\__init__.py` — **the mutant's own
clone** — on every one of the fourteen runs, and `tree clean` was `yes` on every one.

| id | file | mutation | pytest | check-roles | verdict | killed by |
|---|---|---|---|---|---|---|
| **M15** | `check_roles.py` | **D3 hard-wired to `shared = set()`** — attempt 1's deliberate survivor | 5 failed, 166 passed | rc=0 | **KILLED** | all four `test_d3_fires_on_every_one_of_b02s_four_attack_forms[…]` + `test_the_walk_sees_import_forms_a_single_capture_group_missed` |
| **M21** | `check_roles.py` | `_transitive_closure` recurses only from the seeds — **the walk stops after ONE hop** | 1 failed, 170 passed | rc=0 | **KILLED** | `…four_attack_forms[4 — ONE HOP: each side imports its own helper…]` |
| **M22** | `check_roles.py` | relative imports no longer resolved (`if node.level:` → `if False:`) | 1 failed, 170 passed | rc=0 | **KILLED** | `…four_attack_forms[3 — a RELATIVE import crossing the moat]` |
| **M23** | `check_roles.py` | `from whetstone_gate import X` no longer resolved to `whetstone_gate.X` | 1 failed, 170 passed | rc=0 | **KILLED** | `…four_attack_forms[3 — a RELATIVE import crossing the moat]` |
| **M32** | `check_roles.py` | the **package root** put back into `MOAT_ALLOW_LIST` — the entry Q-015 rejected | 1 failed, 170 passed | rc=0 | **KILLED** | `test_the_moat_allow_list_is_empty` |
| **M24** | `check_roles.py` | **A5 branch T disabled** — no control-byte scan over TEXT files | 9 failed, 162 passed | rc=0 | **KILLED** | `test_a5_branch_T_covers_the_control_range_and_spares_tab_and_lf[1,11,12,14,27,31,…]` (9 of them) |
| **M25** | `check_roles.py` | **A5 branch B disabled** — every binary file accepted, NUL or not | 1 failed, 170 passed | rc=0 | **KILLED** | `test_a5_branch_B_fires_on_the_OF01_reproduction` |
| **M26** | `check_roles.py` | **E5 treats every malformed trailer as excepted** | 1 failed, 170 passed | rc=0 | **KILLED** | `test_e5_fires_on_a_malformed_trailer_that_is_not_on_the_exception_list` |
| **M27** | `check_roles.py` | **a FIFTH entry added to `E5_EXCEPTIONS`** — Q-014 (iv)'s pin must fire | 1 failed, 170 passed | rc=0 | **KILLED** | `test_the_e5_exception_list_is_exactly_the_four_ctx_13_4_commits` |
| **M28** | `check_roles.py` | **B-01's original defect restored**: `issued[token] = {(chunk, role)}`, so one token keeps only its LAST pair | 3 failed, 168 passed | rc=0 | **KILLED** | `test_e2_fires_when_one_token_is_a_chunks_BUILD_and_its_REVIEW`, `test_e3_fires_when_one_token_appears_under_two_different_roles`, `test_the_issued_parse_keeps_every_row_not_only_the_last` |
| **M29** | `config.py` | **the loader stops refusing a YAML null** (`blank_marker` returns `None`) | 3 failed, 168 passed | rc=0 | **KILLED** | `test_a_blank_value_is_a_refusal_and_is_counted[… null / ~ / (empty) …]` |
| **M30** | `config.py` | **B-03's cause restored**: the sweep skips a REQUIRED file it cannot open | 2 failed, 169 passed | rc=0 | **KILLED** | `test_a_missing_REQUIRED_config_is_a_refusal_and_F1_fails`, `test_the_operator_placeholder_gate_goes_RED_when_lanes_yaml_is_gone` |
| **M31** | `check_roles.py` | **R1 can no longer fail** — the examined root is never checked | 1 failed, 170 passed | rc=0 | **KILLED** | `test_check_roles_FAILS_rather_than_passing_vacuously_on_a_non_repository` |
| **CTRL** | `config.py` | **CONTROL** — `value.startswith(P)` → `value[:len(P)] == P`. Semantically identical. **It must SURVIVE.** | **171 passed, 1 skipped, 2 deselected** | rc=0 | **SURVIVED — correct** | — |

**13 real mutants, 13 killed. Kill rate 13/13. The control survived, so the run is not void.**

Every mutant was killed by a test that **names its defect**, not by a coincidence: M15 by the four
B-02 attack forms, M28 by the E2/E3 probes, M27 by the exception-list pin, M31 by the
non-repository probe. That is what distinguishes a suite that kills from a suite that merely goes
red.

---

## What this run does and does not say about `OF-02`

`OF-02` recorded **12 of 19 survivors** at attempt 1, closed to 17/19 by that review's own probes,
with **M15 deliberately left alive** and **M20 an equivalent mutant**. The C0 FIX session then
claimed M15 killed and explicitly did **not** re-run the rest — correctly, since a fix session
scoring its own work is the act this project exists to reject.

**What is measured here:** M15 is killed, confirmed against the pinned source with `__file__`
printed. Thirteen mutants aimed at the code that did **not** exist at attempt 1 — the transitive
import walk, both A5 branches, E5 and its pin, the blank-value refusal, the required-config
refusal, R1 — are **all killed**.

**What is NOT measured here, said plainly:** attempt 1's other eighteen mutants were **not**
re-run one for one. Several no longer apply — the code they mutated has been rewritten (M11's E1
predicate, M12's trailer regex, M4/M5/M6's loader paths and M15's D3 all sit in reworked
functions) — and the ones that still apply were closed by attempt 1's own kept probes, which are
still in the repository and still green. **No combined mutation score across both runs is claimed**,
because the two runs are over different code and adding them would be arithmetic with no meaning.

**One claim of the FIX session was checked directly instead**, because it is the load-bearing one
and INC-17 is exactly the trap that would have made it look false:

```
$ cd <clone at 864c621>   # PRE-FIX source on disk
$ cp <HEAD>:tests/test_c0_fix_probes.py tests/
$ PYTHONPATH=<clone>/src python -c "import whetstone_gate; print(whetstone_gate.__file__)"
<clone>\src\whetstone_gate\__init__.py                       <- the PRE-FIX tree, not the live repo
$ PYTHONPATH=<clone>/src python -m pytest -q tests/test_c0_fix_probes.py
49 failed, 6 passed in 16.32s
```

The fix session claimed *"52 probes, of which 46 fail against `864c621`'s source and the 6 that
pass there are regression guards by design."* Measured today: **55 probes, 49 fail, 6 pass** — the
three extra failures are the §8.6-registry probes the ARCH session later added to the same file.
**The claim reconciles exactly, and it was verified the one way that could have shown it false.**
