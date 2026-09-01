# C13 — mutation table. REVIEW 2, session `8c49c4d3`, 2026-09-01

**`docs/reviews/README.md`: minimum 8 mutants on a `full` chunk, each killed by a named test or
given an explicit equivalence proof. A SURVIVOR IS A FINDING.** **Twenty-five were run: 18 killed,
6 survived, 1 equivalent.** Fourteen of them land on **code the FIX added, which no review had
seen**.

⚠️ **EVERY MUTATION WAS APPLIED TO A COPY IN A FRESH OS TEMP DIRECTORY AND — for the vendored ones —
COMMITTED THERE.** REVIEW 1 records that editing files without committing produced **three false
SURVIVORS**, because the harness reads `git cat-file blob HEAD:<path>` and never the working tree.
Workspace proved isolated before a single mutant ran:

```
whetstone_gate.__file__ = …\scratchpad\rev13_2\mut\src\whetstone_gate\__init__.py
cfg.repo_root()         = …\scratchpad\rev13_2\mut
vendor_root()           = …\scratchpad\rev13_2\mut\vendor\camel-prompt-injection
agentdojo_root()        = …\scratchpad\rev13_2\mut\vendor\agentdojo
pinned_sha()            = f083b6b396399d3b3c7f2ddaf613a5945eaf32d8
head_sha(vendor_root)   = f083b6b396399d3b3c7f2ddaf613a5945eaf32d8
```

**Baseline in that workspace: `tests/test_c13_camel_comparator.py` → 87 passed, 0 failed.**
(Whole suite in the temp workspace is 14 failed / 675 passed / 1 skipped / 12 errors; every one of
those traces to `vendor/tau2-bench` being absent from the copy, and none is used in any judgement
below.)

⚠️ **THE KILL CONVENTION WAS FIXED IN THE PHASE-1 SEAL (`e2f8aab`) BEFORE ANY MUTANT RAN**, so it
could not be chosen afterwards. Any commit inside the vendored copy moves it off its pin, so five
**vendor-integrity** tests are expected collateral on every vendored mutant and are **excluded from
the kill judgement**, which is taken over the tests that name the log-path property. Both numbers
are reported. Each vendored mutant was therefore run **twice**: once with the pin left alone, and
once with `config/protocol.yaml`'s `camel_sha` repointed at the mutated HEAD so that the **property**
is all that is measured.

---

## A. B-1 — the vendored tree. The three the prompt names, plus two extra forms

| # | mutation | **PRE-COMMITTED** | property tests that died | **MEASURED** |
|---|---|---|---|---|
| **M15** | delete the three DEAD helpers `replay_user_task`, `replay_suite`, `replay_benchmark` | ⚠️ **MUST SURVIVE** | *(none)* | ✅ **SURVIVED** |
| **M16-abs-posix** | live path → `Path("/var/logs")` | **MUST BE KILLED** | `…share_one_working_directory…` | ✅ **KILLED** |
| **M16-abs-win** | live path → `Path("C:/logs")` | **MUST BE KILLED** | `…share_one_working_directory…` | ✅ **KILLED** |
| **M16-resolve** | live path → `Path("logs").resolve()` | **MUST BE KILLED** | both log-path tests | ✅ **KILLED** |
| **M16-dunder-file** | REVIEW 1's own literal form: `Path(__file__).resolve().parent / "logs"` | *(extra)* | both log-path tests | ✅ **KILLED** |
| **M17** | live replayer stops reading pass 1's logs: `trace_path.read_text()` → `'{}'` | **MUST BE KILLED** | both log-path tests | ✅ **KILLED** |
| **M17-glob** | the live read becomes a **glob** — INC-39's silent-zero shape | *(extra)* | both log-path tests | ✅ **KILLED** |

**Repinned runs, where the property is all that is measured** (the one residual red is
`test_the_committed_empty_diff_proof_regenerates_byte_for_byte`, which embeds the old SHA and is a
pure artefact of repinning):

```
M15              1 failed, 86 passed   PROPERTY-FAILED = NONE          <-- SURVIVES
M16-abs-posix    2 failed, 85 passed   PROPERTY-FAILED = 1
M16-abs-win      2 failed, 85 passed   PROPERTY-FAILED = 1
M16-resolve      6 failed, 81 passed   PROPERTY-FAILED = 2
M16-dunder-file  6 failed, 81 passed   PROPERTY-FAILED = 2
M17              6 failed, 81 passed   PROPERTY-FAILED = 2
M17-glob         3 failed, 84 passed   PROPERTY-FAILED = 2
```

⚠️ **THE POLARITY IS NOW THE RIGHT WAY ROUND.** REVIEW 1 measured M15 **KILLED** and M16/M17
**SURVIVING** — a guard anti-correlated with the property it was named for. Every one of the seven
now lands where it should. **B-1's guard half is closed.**

### A.1 The two-rule `is_relative` check, probed directly rather than inferred from a kill

```
'/var/logs'   PurePosix.is_absolute=True   PureWindows.is_absolute=False  -> _is_relative_literal=False
'C:/logs'     PurePosix.is_absolute=False  PureWindows.is_absolute=True   -> _is_relative_literal=False
'logs'        PurePosix.is_absolute=False  PureWindows.is_absolute=False  -> _is_relative_literal=True
```

**The function evaluates both rulesets and each absolute form is caught by exactly one of them**, so
the claim in its docstring is true of the code. ⚠️ **But see N11: only ONE of the two halves is
pinned by a test**, and the end-to-end kill of `M16-abs-win` comes from
`claim.root_literal == "logs"`, not from `is_relative` — established by running **N11 + M16-abs-win
together**, where the property test still dies.

### A.2 The corrected failure mode, verified independently of the FIX

Mechanically, over the blob at the pin:

* `replay_task` spans **129–238**; its only `Try` is **185–198**, catching `SecurityPolicyDeniedError`;
  **line 148 is not inside it**.
* `PrivilegedLLMReplayer.query` spans **287–315** and contains **zero** `Try` blocks.
* AgentDojo's `run_task_with_pipeline` wraps `agent_pipeline.query(...)` in `except AbortAgentError`
  **only**.

→ **an unhandled `FileNotFoundError`. It crashes loudly.** The corrected sentence is right.

---

## B. B-2 — each refusal deleted SEPARATELY, and the control

| # | mutation | **PRE-COMMITTED** | **MEASURED** | killed by |
|---|---|---|---|---|
| **D1** | delete `assert_provenance(HEADLINE_FIGURES)` alone | **RED ON ITS OWN** | ✅ **6 failed** | `test_the_RENDERER_refuses_each_incomplete_figure_in_turn` |
| **D2** | delete `assert_provenance(CITED_TABLE_FIGURES)` alone | **RED ON ITS OWN** | ✅ **6 failed** | same |
| **D3** | delete `assert_provenance(TABLE_4_BANKING_FIGURES)` alone | **RED ON ITS OWN** | ✅ **6 failed** | same |
| **D-all** | delete all three | RED, strictly more | ✅ **18 failed** | same |
| **C-ctl** | ⚠️ **CONTROL — no mutation** | **MUST STILL RENDER** | ✅ **renders** | — |

**The control, measured:** `render_branch_b` returns **17,103 characters / 199 lines**, raising
nothing; **29 figures** are guarded (6 + 11 + 12); **zero** figures fail `provenance_failures()`.
**A gate that refuses everything is not a gate, and this one does not.**

The killing test **calls the renderer** — the exact defect INC-40 records was a test named for the
renderer that called only the helper. **B-2 is closed.**

---

## C. THE NEW SURFACE — fourteen mutants on code no review had seen

| # | target | mutation | verdict | killed by / finding |
|---|---|---|---|---|
| **N1** | `PublishedFigure.provenance_failures` | count with **no ceiling** accepted | **KILLED** | `test_the_ceiling_gate_goes_red_on_a_count_missing_it` |
| **N2** | same | ceiling with **no source** accepted | **KILLED** | same |
| **N3** | `_t4` | **Table 4's ceiling attributed to Figure 11** | **KILLED** | `test_every_published_COUNT_carries_its_ceiling_and_the_ceilings_source`, `test_the_branch_b_artefact_regenerates_byte_for_byte` |
| **N4** | `_T7` | **Table 7's ceiling attributed to Figure 9** | **KILLED** | same |
| **N5** | `banking_rows` | drop the **suite** filter | **KILLED** | `test_table_4_is_published_IN_FULL_and_P2s_shape_is_COUNTED_not_asserted` |
| **N6** | `banking_rows` | drop the **table** key | ⚠️ **SURVIVED** | equivalent **today only, by tuple ordering** — see C.1 |
| **N7** | `p2_holds_for` | drop the *"with-policies blocks it"* half | **KILLED** | `test_table_4_is_published_IN_FULL…` |
| **N8** | `live_log_path_from_source` | `len(live) != 1` → `< 1` | ⚠️ **SURVIVED** | **non-equivalent** — see C.1 |
| **N9** | same | reachability walk neutered | **KILLED** | 6 tests incl. `test_the_live_log_path_is_located_by_ast_and_proved_reachable` |
| **N10** | `_is_relative_literal` | drop the **POSIX** rule | **KILLED** | `test_the_live_log_path_is_located_by_ast_and_proved_reachable` |
| **N11** | `_is_relative_literal` | drop the **WINDOWS** rule | ⚠️ **SURVIVED** | **non-equivalent** — see C.1 |
| **N12** | `_absolutises` | always `False` | **KILLED** | `test_the_live_log_path_is_located_by_ast_and_proved_reachable` |
| **N13** | `LogPathClaim.crashes_loudly` | `glob` counted as a loud read | ⚠️ **SURVIVED** | **non-equivalent** — see C.1 |
| **N14** | `TABLE_NUMBER` guard | `fullmatch` → `match` | ⚠️ **SURVIVED** | **non-equivalent** — see C.1 |

⚠️ **N3 and N4 are the ceiling result the prompt asks for.** Swapping the attribution **in either
direction** is killed, so the source is asserted **per table** and not once. Citing Figure 11 for
Table 4's ceiling — *"`Q-058`'s own defect one level smaller"* — is a red test.

### C.1 The survivors, each characterised BY EXHIBIT

```
N11  drop the WINDOWS rule
     root='C:/logs'    HEAD.is_relative=False   N11.is_relative=True   <== DIFFER
     root='C:\logs'    HEAD.is_relative=False   N11.is_relative=True   <== DIFFER
     root='/var/logs'  HEAD.is_relative=False   N11.is_relative=False
  NOT EQUIVALENT. The fixture in test_the_live_log_path_is_located_by_ast_and_proved_reachable
  fires only a POSIX-absolute form (`Path("/var/logs")`) and a `.resolve()` form. No Windows-
  absolute form is fired anywhere, so half the disjunction is pinned by nothing.

N14  fullmatch -> match
     table='Tables 5-7'  HEAD=False  N14=False
     table='Table 5-7'   HEAD=False  N14=True    <== DIFFER: a RANGE is accepted
  NOT EQUIVALENT. The parametrised fixture uses the PLURAL `Tables 5-7`, which the mutant still
  rejects on the `s`. REVIEW 1's M6 equivalence proof said in terms that "the strength of the
  check is `fullmatch`" — and `fullmatch` is pinned by no test.

N13  crashes_loudly gains 'glob'
     read_call='read_text'  HEAD=True   N13=True
     read_call='glob'       HEAD=False  N13=True  <== DIFFER
  NOT EQUIVALENT. `crashes_loudly` exists ONLY to tell read_text from glob — INC-39's whole
  distinction — and no test constructs a glob claim and asserts it is False. M17-glob dies on
  `claim.read_call == "read_text"`, not on this.

N8   len(live) != 1  ->  len(live) < 1
     HEAD  : REFUSES -> "PrivilegedLLMReplayer.query reaches 2 function(s) ... not exactly one"
     N8    : 2 < 1 is False -> no refusal -> silently takes sorted(live)[0]
  NOT EQUIVALENT. Nothing in the suite constructs a TWO-reachable-construction source; the
  fixture's M17 case has ZERO, and 0 < 1 is True, so the mutant still raises there.

N6   banking_rows drops the TABLE key
     HEAD (table-keyed) : {'CaMeL': '0 +/- 0.0', 'CaMeL (no policies)': '1 +/- 0.0'}
     N6   (table-free)  : {'CaMeL': '0 +/- 0.0', 'Undefended model': '84.03% +/- 5.98',
                           'CaMeL (no policies)': '1 +/- 0.0'}
     same p2_holds_for? True
  EQUIVALENT TODAY ONLY. `CaMeL` collides across Tables 5, 6 and 7 in CITED_TABLE_FIGURES and
  last-wins picks Table 7 — by luck of ordering, not by the key. Append a table after Table 7,
  or reorder, and p2_holds_for silently reads another table's row.
```

### C.2 The quiet-collapse sweep the prompt asks for, as a number

Every dict comprehension in the package, with its key and filter — **four**:

| site | key | uniquely identifies a row? |
|---|---|---|
| `branch_b.py:366` (`banking_rows`) | `figure.row` | ✅ yes, given the table + base_model + suite filter |
| `claims.py:392` | `str(k.value)` | ✅ AST dict literal keys |
| `invocation.py:481` (`constructions`) | `name` | ✅ but see below |
| `invocation.py:592` | `arg.arg` | ✅ unique within a signature |

⚠️ **ONE MORE, AND IT IS B-1's OWN CLASS.** `invocation._named_functions` keys module-level
functions with **`setdefault` (FIRST definition wins)** and methods with **`[…] =` (LAST wins)** —
the two halves disagree with each other, and the module half disagrees with **Python**, which binds
the last. Demonstrated:

```
source defines replay_task TWICE; the second (absolute "/var/logs") is what Python binds.
  live_log_path_from_source reports: root_literal='logs'  is_relative=True
  _named_functions['replay_task'].lineno = 2   (the FIRST def)
=> the derivation analysed a definition the interpreter never runs, and reported the path
   RELATIVE while the code that would actually run uses an ABSOLUTE one.
```

**Latent, not live** — CaMeL has no shadowed redefinition at the pin — but it is *analysing code the
run does not execute*, which is the sentence INC-39 was written about.

---

## D. Coverage, as a number

| what was mutated | mutants | killed | survived | equivalent |
|---|---|---|---|---|
| B-1, the vendored log path (incl. two extra M16/M17 forms) | 7 | 6 | 1 *(M15, correctly)* | 0 |
| B-2, the renderer's three refusals + the control | 5 | 4 | 0 | 0 *(control renders)* |
| the ceiling gate and its per-table attribution | 4 | 4 | 0 | 0 |
| `banking_rows` / `p2_holds_for` | 3 | 2 | 1 | 0 |
| the reachability derivation | 3 | 1 | 1 | 0 |
| `_is_relative_literal` / `_absolutises` / `crashes_loudly` | 4 | 2 | 2 | 0 |
| the table-number guard | 1 | 0 | 1 | 0 |
| **total** | **25** | **18** | **6** | **1** |

*(M15's survival is a KILL of the old defect and is counted as a survivor only because that is what
the operator did; N6 is the one counted as equivalent-today.)*

**What is strong:** every refusal the two BLOCKERs are about now dies when reverted, separately, and
the control proves the gate still passes what it should. **What is weak:** four guards on the new
surface are correct in the code and pinned by no test — `is_relative`'s Windows half, `fullmatch`,
`crashes_loudly`'s discrimination, and the *"exactly one"* refusal. Each is the same shape as B-2 —
**a property the code has and the suite cannot see** — one level smaller, inside the code written to
close B-2.
