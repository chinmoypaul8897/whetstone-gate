# C13 — mutation table. REVIEW 1, session `b450df0a`, 2026-09-01

**`docs/reviews/README.md`: minimum 8 mutants on a `full` chunk, ≥1 per invariant the chunk
touches, each killed by a named test or given an explicit equivalence proof. A SURVIVOR IS A
FINDING.** Twenty were run; **16 killed, 3 survived, 1 proven equivalent.**

⚠️ **EVERY MUTATION WAS APPLIED TO A COPY IN A FRESH OS TEMP DIRECTORY.** Nothing in this
repository and nothing in this repository's `vendor/` was edited (`INCIDENTS.md` **INC-11**,
**INC-17**). The workspace was proved isolated before a single mutant ran:

```
whetstone_gate.__file__ = …\scratchpad\rev13\mut\src\whetstone_gate\__init__.py
cfg.repo_root()         = …\scratchpad\rev13\mut
vendor_root()           = …\scratchpad\rev13\mut\vendor\camel-prompt-injection
```

**Baseline in that workspace: 74 passed, 1 failed** — and the one failure is
`test_the_camel_branch_is_decided_before_any_camel_run`, which is **supposed** to be red until
RUN-1 decides the branch. It is excluded from every kill judgement below.

⚠️ **M15–M17 MUTATE THE VENDORED TREE, AND THEY HAD TO BE COMMITTED TO COUNT.** C13's harness
reads `git cat-file blob HEAD:<path>` and never the working tree — a deliberate, correct design
that makes every line number OS-independent. A working-tree edit is therefore *invisible* to it,
and a first attempt that only edited the file produced three false SURVIVEDs. The mutants below
commit inside the temp copy of the CaMeL checkout and reset it afterwards; the copy ends at
`f083b6b3…` with an empty `git status`.

---

## The table

| # | file:line | operator | killed by | verdict |
|---|---|---|---|---|
| **M1** | `camel_comparator/vendor.py:210` | `f"$ git diff {proof.pinned_sha}"` → `…{proof.pinned_sha[:12]}` — abbreviate the SHA in the rendered proof | `test_the_committed_empty_diff_proof_regenerates_byte_for_byte` | **KILLED** |
| **M1b** | `camel_comparator/vendor.py:211` | delete `*([proof.diff_against_pin] if proof.diff_against_pin else [])` — always print `(empty)` for the diff | — | ⚠️ **SURVIVED** |
| **M2** | `camel_comparator/branch_b.py:140` | `if not TABLE_NUMBER.fullmatch(self.table):` → `if False:` — delete Q-058's **table** check | `…goes_red_on_each_field_in_turn[a-RANGE-not-a-table]`, `[no-table]`, `test_the_renderer_REFUSES_a_figure_with_incomplete_provenance` | **KILLED** |
| **M3** | `camel_comparator/branch_b.py:146` | delete Q-058's **appendix** check | `…goes_red_on_each_field_in_turn[no-appendix]` | **KILLED** |
| **M4** | `camel_comparator/branch_b.py:152` | delete Q-058's **base-model** check | `…goes_red_on_each_field_in_turn[no-base-model]` | **KILLED** |
| **M5** | `camel_comparator/branch_b.py:165` | delete Q-058's **row** check | `…goes_red_on_each_field_in_turn[no-row]` | **KILLED** |
| **M6** | `camel_comparator/branch_b.py:97` | `TABLE_NUMBER = r"(Table\|Figure) \d+"` → `r"(Table\|Figure)s? \d+"` | — | **EQUIVALENT — proof below** |
| **M6b** | `camel_comparator/branch_b.py:140` | weaken the check so a **range** passes (`Tables 5-7` → accepted) — **Q-058 itself, as a regex** | `…goes_red_on_each_field_in_turn[a-RANGE-not-a-table]`, `test_the_renderer_REFUSES_a_figure_with_incomplete_provenance` | **KILLED** |
| **M7** | `camel_comparator/branch_b.py:158` | delete the **base-model-source** check (build 2's own addition) | `…goes_red_on_each_field_in_turn[no-source]` | **KILLED** |
| **M8 / M8b** | `camel_comparator/branch_b.py:373-374` | **delete `assert_provenance(HEADLINE_FIGURES)` and `assert_provenance(CITED_TABLE_FIGURES)` from `render_branch_b`** — the ruling's refusal becomes a no-op | — | ⚠️ **SURVIVED — BLOCKER B-2** |
| **M9** | `camel_comparator/claims.py:…base_url_hits` | `root.rglob("*.py")` → `root.rglob("*.nope")` — the scan globs nothing | `test_the_base_url_scan_actually_fires` | **KILLED** |
| **M10** | `camel_comparator/invocation.py` pass 2 | `argv=[*common, replay_flag]` → `argv=list(common)` — the two-pass protocol collapses to one | `test_run1_is_two_passes_and_the_second_replays_the_first` | **KILLED** |
| **M11** | `camel_comparator/invocation.py:secpol_pipeline_name` | drop `+ "+secpol"` — pass 2 claims pass 1's pipeline name | `test_run1_is_two_passes_and_the_second_replays_the_first` | **KILLED** |
| **M12** | `camel_comparator/invocation.py:branch_is_undecided` | `if not isinstance(branch, str) or not branch.strip():` → `if False:` | — | **EQUIVALENT — proof below** |
| **M13** | `camel_comparator/claims.py:deny_by_default` | `func.body[-1]` → *last `Return` anywhere in the body* — "terminating" weakened to "present" | `test_the_deny_by_default_derivation_notices_a_denial_that_is_not_last` | **KILLED** |
| **M14** | `whetstone_gate/config.py:_walk_sentinels` | `if is_sentinel(node):` → `… and "agentdojo" not in prefix` — **C16's sentinel silently resolved early** | `test_protocol_sentinels_are_a_shrinking_subset_of_the_known_undecided_ones`, `test_the_sentinel_invariant_actually_goes_red[a-key-changing-owner]` | **KILLED** |
| **M14b** | `config/protocol.yaml` | add `mystery_key: TODO_NOBODY` — a **new, unowned** sentinel drifts in | `test_every_sentinel_in_config_names_who_resolves_it`, `test_protocol_sentinels_are_a_shrinking_subset_of_the_known_undecided_ones` | **KILLED** |
| **M15** | `vendor/camel-prompt-injection` blob, `replay_privileged_llm.py:318-356` | **DELETE the three DEAD helpers** `replay_user_task`, `replay_suite`, `replay_benchmark`. **The live two-pass path is byte-identical.** | `test_both_passes_share_one_working_directory_and_the_plan_says_why`, `test_run1_is_two_passes_and_the_second_replays_the_first` | ⚠️ **KILLED — AND THAT IS THE DEFECT** |
| **M16** | `vendor/camel-prompt-injection` blob, `replay_privileged_llm.py:140` | make the **LIVE** log path absolute: `Path("logs")` → `Path(__file__).resolve().parent / "logs"` — **the same-working-directory requirement is DESTROYED** | — | ⚠️ **SURVIVED — BLOCKER B-1** |
| **M17** | `vendor/camel-prompt-injection` blob, `replay_privileged_llm.py:148` | the **LIVE** replayer stops reading pass 1's logs entirely: `trace_path.read_text()` → `'{}'` | — | ⚠️ **SURVIVED — BLOCKER B-1** |

---

## The three survivors, and why each is a finding

### ⚠️ M15 / M16 / M17 — the guards are ANTI-CORRELATED with the property. **BLOCKER B-1.**

Read the three rows together, because separately none of them is damning and together they are
conclusive:

* **M15** removes code that **cannot affect the run** — `replay_benchmark` has no caller
  anywhere in the tree and is never imported, so `replay_suite` and `replay_user_task` are
  unreachable from `main.py`. Deleting all three leaves the two-pass protocol byte-identical.
  **Both guarding tests go RED.**
* **M16** destroys **the exact property the tests are named for** — the log path stops being
  relative to the working directory, so pass 2 no longer needs pass 1's cwd. **Both stay GREEN.**
* **M17** makes pass 2 **stop reading pass 1's logs at all**, which is the entire content of
  "the second replays the first". **Both stay GREEN.**

The mechanism is one line. Both tests assert on the substring `Path("logs") / pipeline_name`:

```python
replay = vendor.blob_text(camel_root, "src/camel/pipeline_elements/replay_privileged_llm.py")
assert 'Path("logs") / pipeline_name' in replay          # test_run1_is_two_passes…
line = next((n for n, t in enumerate(replay.splitlines(), 1)
             if 'Path("logs") / pipeline_name' in t), None)
assert line is not None                                   # test_both_passes_share_one_working_dir…
```

That substring occurs at **exactly two lines in the file — 321 and 341 — and both are in dead
functions.** The live construction (`replay_task`, 139-146) never matches it, because it is
split across lines: 140 is `Path("logs")` alone and 141 is `/ pipeline_name`.

```
$ git cat-file blob HEAD:src/camel/pipeline_elements/replay_privileged_llm.py \
    | grep -n 'Path("logs") / pipeline_name'
321:    path = Path("logs") / pipeline_name / suite_name / user_task_id / (attack_name or "none")
341:    path = Path("logs") / pipeline_name / suite_name
```

A gate that fires when nothing broke and stays silent when the property is destroyed is not
merely decorative — `PROCESS.md` §5.4's word for a gate that has never gone red — it is
**misleading in the direction that costs the most**, inside a run that happens exactly once.

### ⚠️ M8 / M8b — Q-058's guardrail is a refusal that nothing tests. **BLOCKER B-2.**

`branch_b.py`'s own header states the standard this must meet:

> *"**A REFUSAL, NOT AN ASSERTION.** Q-058's ruling makes the four fields a property of every
> published third-party figure; a property enforced only in a test file is a property that holds
> until somebody adds a figure without running the tests."*

The refusal exists — `render_branch_b` opens with two `assert_provenance` calls. **Delete both
lines and the entire suite stays green.** The test named for it,
`test_the_renderer_REFUSES_a_figure_with_incomplete_provenance`, calls
`branch_b.assert_provenance(...)` **directly and never calls `render_branch_b`**, though its
docstring says the rule has been *"moved into the renderer"* and that the test *"proves the
refusal actually happens."* It proves that `assert_provenance` raises. It does not prove the
renderer calls it.

The C13 REVIEW prompt puts the standard in one sentence: *"C13 BUILD 1 wrote the figure test ONE
FIELD SHORT of catching its own finding. The extension is Q-058's guardrail. If it can be mutated
and survive, the guardrail is decorative."* M2–M7 and M6b show the **field checks** are genuinely
guarded — six mutants, six kills, one per field. M8b shows the **refusal** is not.

**One line of test would close it**, e.g. monkeypatching `branch_b.assert_provenance` to record
its calls and asserting `render_branch_b` made both — or rendering with a deliberately broken
figure list and asserting `BranchBError`.

### ⚠️ M1b — the empty-diff proof can be made to lie, and only a sibling test catches it. **MEDIUM.**

Removing the conditional that emits `proof.diff_against_pin` makes `render_unmodified_proof`
print `(empty)` **whatever the tree says**. `test_the_committed_empty_diff_proof_regenerates_byte_for_byte`
then passes over a dirty tree — the exact failure it exists to prevent.

It is not a hole in the suite as a whole: `test_the_verification_triple_holds_head_clean_and_empty_diff`
asserts `proof.diff_against_pin == ""` on the object, independently of the renderer, and
`test_the_regeneration_check_actually_fires` checks `dirty.holds` and `len(dirty.failures()) == 2`
the same way. So "CaMeL is unmodified" stays guarded; what is unguarded is **the rendered file's
faithfulness to it**. Recorded as MEDIUM because the committed proof is the artefact a reader
reads, and the defence that survives is not the one the file's own header advertises
(*"THIS FILE IS REGENERATED, NOT STORED"*).

Note `test_the_regeneration_check_actually_fires`'s dirty fixture still differs from `good`
under M1b — but only via the **status** line, not the diff line. It passes for the wrong reason.

---

## The two equivalence proofs

### M6 — EQUIVALENT, and the proof says which half of the check is load-bearing

Widening `TABLE_NUMBER` from `(Table|Figure) \d+` to `(Table|Figure)s? \d+` changes nothing,
because the guard uses **`fullmatch`**: `Tables 5-7` still fails under both patterns, on the
trailing `-7` rather than on the `s`. The strength of the check is `fullmatch`, not the absence
of `s?`. **M6b** is the non-equivalent form of the same idea — weaken the *call* so a range
passes — and it is **KILLED**, twice. So the property is genuinely guarded; M6 simply did not
touch it.

### M12 — EQUIVALENT while the sentinel stands, and that is itself a LOW finding

`branch_is_undecided()` reads through `cfg.load("lanes").require("camel_comparator.branch")`,
which **raises `UndeterminedValue` first** and is caught by the enclosing `except`:

```
$ python -c "from whetstone_gate import config as cfg; cfg.load('lanes').require('camel_comparator.branch')"
require() RAISES first: UndeterminedValue
=> the isinstance / blank-string guard is UNREACHABLE while the sentinel stands
```

So `if not isinstance(branch, str) or not branch.strip():` cannot execute today, and deleting it
is behaviourally equivalent. ⚠️ **It stops being equivalent the moment RUN-1 writes the key** —
if RUN-1 writes an empty string or a non-string, that guard is the only thing that would notice,
and **no test constructs that state.** Recorded as LOW: an untested guard on the one value a
single-shot operator run writes by hand.

---

## What the mutants say about coverage, as a number

| what was mutated | mutants | killed | survived | equivalent |
|---|---|---|---|---|
| the empty-diff regeneration | 2 | 1 | 1 | 0 |
| Q-058's figure-metadata gate (one per required field) | 7 | 6 | 0 | 1 |
| the renderer's **refusal** | 1 | 0 | **1** | 0 |
| the sentinel-set invariant (Q-061's rewrite) | 2 | 2 | 0 | 0 |
| the two-pass invocation (first-party side) | 2 | 2 | 0 | 0 |
| the two-pass invocation (**upstream** side) | 3 | 1 *(false positive)* | **2** | 0 |
| the branch-not-decided structural test | 1 | 0 | 0 | 1 |
| the `base_url` scan | 1 | 1 | 0 | 0 |
| the deny-by-default "terminating" claim | 1 | 1 | 0 | 0 |
| **total** | **20** | **14 + 2 misdirected** | **3** | **2** |

The field-level gate is strong: **six mutants, six kills, one per field**, and the range case —
Q-058's own defect shape — is killed twice. What is weak is everything that guards a claim about
**upstream code**: the property is asserted by substring against a file, and a substring cannot
tell a live line from a dead one.
