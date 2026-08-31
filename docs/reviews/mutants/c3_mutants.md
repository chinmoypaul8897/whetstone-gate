# C3 mutation run — review 1

**SESSION-TOKEN:** `a66c389d` · **Role:** REVIEW · **Chunk:** C3 · **Date:** 2026-08-31
**Review type:** `full`, `PROCESS.md` §12.1 — **minimum eight mutants plus a control.**
**Eleven ran. Ten killed. One survived and is finding F-1. The control survived.**

---

## Method, and the three traps it is built to avoid

**INC-11 — a mutant that looks killed merely by existing on disk.**
`tests/test_repo_invariants.py::test_the_object_store_and_the_working_tree_agree` hashes every
**tracked** file's working-tree bytes against `git show HEAD:<path>`, so *any* uncommitted edit
kills *any* mutant, control included. **Every mutant below was COMMITTED before it was run**, and
`git status --porcelain` is captured as `tree clean` for each.

**INC-17 — an editable install that resolves `whetstone_gate` by name.**
`C:\Users\chinm\whetstone-gate\src` is on `sys.path` through a `.pth`, so running `pytest` inside a
clone still imports **the live repository**. `PYTHONPATH` is therefore set to the tree under test
and **`whetstone_gate.__file__` is printed on every single run**, and every row states it. A run
that does not say which tree it loaded is not evidence.

**A third trap, and it is why this run is in a clone at a pinned commit.**
C2's review may be running concurrently as pair **P-03**. `REVIEW_C0_2`'s first complete pass was
voided because a concurrent session moved the baseline under it and killed its control. This run
therefore never touches the live repository: it clones it at one commit and stays there.

```
MUTATION SOURCE PINNED AT : e89f63c  (this review's own Phase-1 commit)
CLONE                     : <OS temp>\scratchpad\mut\tree      (throwaway, outside the repo)
whetstone_gate.__file__   : ...\scratchpad\mut\tree\src\whetstone_gate\__init__.py
                            — PRINTED AND CHECKED ON ALL 13 RUNS (baseline, 11 mutants, control)
COMMAND                   : PYTHONPATH=<clone>/src python -m pytest -q -m "not operator_gate"
                                --ignore=tests/test_c1_review_probes.py
BASELINE                  : 215 passed, 1 skipped, 2 deselected      tree clean
```

⚠️ **`vendor/` is git-ignored (`vendor/*/`, only `MANIFEST.md` is tracked), so a clone has no
τ²-bench and every C3 test would error.** The pinned checkout's `src/`, `data/tau2/domains/` and
`.git/HEAD` were **copied in read-only** and each file's SHA-256 verified byte-identical against the
original before the baseline was taken. **The real `vendor/tau2-bench` was never written to**, and
its `rev-parse HEAD` / `status --porcelain` are re-verified at both ends of this session.

**Why `tests/test_c1_review_probes.py` is excluded, stated rather than quietly dropped (rule 11):**
C1 is under an open **FAIL** and `test_section_0_states_its_own_quoted_line_count_correctly` is red
in the baseline by design — it is C1's FIX session's to close. Leaving it in would score a "kill"
on every row including the control. `-m "not operator_gate"` is what `make test` itself deselects.
**Nothing else is excluded, and the full unfiltered suite is reported in the review file.**

---

## The table

Each mutant is a single committed edit, applied with the editor, its `git diff` printed and checked,
and the file asserted free of CRLF. Sixteen distinct tests appear as killers across the eleven rows.

| # | SHA | Operator targeted | The change | Result | Killed by |
|---|---|---|---|---|---|
| **M1** | `27088c9` | **the WRITE-tool decorator match** | `WRITE_TOOL_TYPE = "WRITE"` → `"GENERIC"` (a mistyped `ToolType` member; the write set becomes `calculate` + `transfer_to_human_agents`) | **KILLED** — 7 failed | `test_the_must_not_write_split_reproduces_from_the_pinned_sha`, `…write_task_count_reproduces_as_the_complement`, `…config_counts_agree_with_the_checkout`, `…tfp_selection_is_the_first_n_of_the_bytewise_string_sort`, `…ruled_sort_is_not_the_sort_a_numeric_reading_would_give`, `…committed_selections_still_match_the_pinned_checkout`, `…report_runs_and_exits_zero` |
| **M2** | `b0a1551` | **the empty-vs-read-only split** | `classify_task`: an empty trajectory returns `READ_ONLY` instead of `EMPTY_ACTIONS` | **KILLED** — 5 failed | `test_the_must_not_write_split_reproduces_from_the_pinned_sha`, the three `test_classify_task_on_hand_built_trajectories[…empty_actions]` cases, `test_a_task_with_no_evaluation_criteria_at_all_is_empty_not_a_crash` |
| **M3** | `90e4819` | **the domain filter** | `DOMAINS = ("airline","retail")` → `+ ("telecom",)` | **KILLED** — 3 failed, 12 errors | the enumeration fixture refuses on telecom; `test_the_domains_config_pre_registers_are_the_domains_this_adapter_reads` and every count test go with it |
| **M4** | `f0b5df9` | **the sort direction** | `sort_task_ids`: `sorted(ids)` → `sorted(ids, reverse=True)` | **KILLED** — 2 failed | `…tfp_selection_is_the_first_n_of_the_bytewise_string_sort`, `…committed_selections_still_match_the_pinned_checkout` |
| **M5** | `3b5c27c` | **the slice bound** | `tfp_selection`: `[:wanted]` → `[: wanted + 1]` (21 per domain, 42 total) | **KILLED** — 2 failed | `…tfp_selection_is_the_first_n_of_the_bytewise_string_sort`, `…committed_selections_still_match_the_pinned_checkout` |
| **M6** | `f9ce596` | **the strings-not-ints guard** | `config/protocol.yaml`: `tfp_task_ids.airline` opens `["11",` → `[11,` — the exact YAML slip C3's comment warns about | **KILLED** — 3 failed | `…committed_selections_still_match_the_pinned_checkout`, **`test_every_committed_id_is_a_string`**, `…report_runs_and_exits_zero` |
| **M7** | `a0abd45` | **the unknown-tool refusal** | `enumerate_domain`: `if unknown:` → `if False and unknown:` — an unclassifiable action name stops being a refusal | **KILLED** — 1 failed | `test_an_action_naming_an_unknown_tool_is_a_refusal` |
| **M8** | `fe475b1` | **the db_reward closure walk** | `DB_REWARD_MODULE` → `"tau2.evaluator.evaluator_nl_assertions"` — the walk is pointed at the LLM-judged path we do not use | **KILLED** — 1 failed | `test_the_db_reward_path_reaches_no_text_generation_client` (finds `litellm`) |
| **M9** | `85b5b86` | **the no-reimplementation scan** | a real `scored_reward()` planted in `enumerate.py`, `hashlib.sha256(...).hexdigest()` compared to a target | **KILLED** — 1 failed | `test_the_adapter_does_not_reimplement_the_hash_comparison` |
| **M10** | `1eedda1` | **the ruled sort itself** | `sort_task_ids`: `sorted(ids)` → `sorted(ids, key=int)` — the numeric reading the architect ruled against | **KILLED** — 3 failed | `…tfp_selection_is_the_first_n_of_the_bytewise_string_sort`, `test_non_ascii_ids_are_a_refusal_because_the_ruled_sort_is_bytewise`, `…committed_selections_still_match_the_pinned_checkout` |
| **M11** | `bcc5a08` | **the unreadable-decorator refusal** | `tool_types`: `else: raise EnumerationError(…)` → `elif False: raise …` — a decorator this parser cannot read is **silently skipped** instead of refused | 🚩 **SURVIVED** — **215 passed, 1 skipped, 2 deselected — byte-for-byte the baseline** | **nothing.** This is finding **F-1**. |
| **CONTROL** | `1152872` | *(semantics-preserving)* | `enumerate_domain`'s local `ids_seen` renamed `seen_task_ids` (3 occurrences) | ✅ **SURVIVED** — **215 passed, 1 skipped, 2 deselected** | — the run is **VALID** |

---

## M11 — the survivor, and exactly what it does and does not mean

The branch M11 disables is the one whose own error message reads:

> *"Refusing rather than guessing its type: a misread write tool silently moves a task into the
> must-not-write control, and that control is a published number."*

Disabling it changes nothing the suite can see. The reason is that its only test —
`test_a_tool_whose_decorator_cannot_be_read_is_a_refusal_not_a_silent_read_tool` — feeds a fixture
whose **only** decorated `def` is the unreadable one. Under the mutation `found` is `{}`, so the
*other*, unrelated refusal (`"no decorated tools were found at all"`) raises instead, and a bare
`pytest.raises(EnumerationError)` with no `match=` cannot tell the two apart.

**What this is NOT.** It is **not** a wrong number and **not** a missing guard. The production
refusal is intact in HEAD; and at the pinned SHA the mutant is genuinely **equivalent** — every
airline and retail decorator is a plain `@is_tool(ToolType.MEMBER)`, so the branch is never entered.
The pin itself is separately enforced by `test_a_checkout_that_is_not_at_the_pin_is_a_refusal`,
which **can** go red (verified), and the vendored tree is verified unmodified at both ends of this
session. **No figure C3 publishes is affected.**

**What it IS.** An equivalence that holds *only* at the pin, on the guard that exists precisely for
the moment the pin moves — and `PROCESS.md` §5.4 is explicit that a gate which has never gone red is
decorative. The fix is one line (`match="cannot read"`, or a readable tool added to the fixture so
`found` is non-empty under the mutation) and belongs to whoever next touches C3. Graded **MEDIUM**,
not BLOCKER, on that reasoning; see `REVIEW_C3_1.md` **F-1**.

⚠️ **A second, narrower gap in the same parser is recorded as F-3 and is *not* a mutant**, because
demonstrating it would require editing `vendor/`, which is read-only to every session:
`@is_tool(tool_type=ToolType.WRITE)` has no positional argument, so `tool_types` takes the
`not decorator.args` branch and records **`READ`** — it does not refuse. That shape does not occur at
the pin, and `tests/test_c3_review_probes.py::test_no_pinned_domain_toolkit_uses_the_keyword_form_of_the_tool_decorator`
(added by this review) now asserts it does not, so a benchmark bump cannot introduce it silently.

## One observation the table cannot show

Under **M1**, `test_write_tools_are_read_from_tau2s_own_decorator` did **not** fail — it re-derives
the write set with its own `ast` walk but keys that walk off `tau2_enum.WRITE_TOOL_TYPE`, the very
constant M1 mutates, so both sides moved together. Seven other tests killed M1 regardless, so
nothing is unguarded; it is recorded because a test that imports the constant it is checking is one
step nearer hard rule 3's boundary than it looks. (`REVIEW_C3_1.md` F-1, closing note.)
