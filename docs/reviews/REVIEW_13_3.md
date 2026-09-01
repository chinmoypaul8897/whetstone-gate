# REVIEW 13, attempt 3 — C13, THE CaMeL COMPARATOR

**Verdict: FAIL — with ZERO BLOCKERS.** · Session `c09c385b` · 2026-09-02 · Review type **full**,
re-review after C13 FIX 2 (`91eb51c1`)
**Phase-1 criteria seal:** `90abb2de9666d426799880ee8d381b479a4c0463`
**Token row registered BEFORE the seal:** `87a4aec` (row 41)
**Personas:** evaluation-integrity (1) + code (2), `PROCESS.md` §5.3
**Tag `c13-pass`: NOT CUT.**

> ⚠️ **BOTH OF REVIEW 2's BLOCKERS ARE CLOSED, AND CLOSED BETTER THAN THEY HAD TO BE.** B-3's
> correction goes red **eight** independent ways, including — the one that matters — an amendment to
> `CONTEXT.md` §8.5.1 alone, which turns the suite red **at the law** with a message telling the
> reader that `config/` is not the thing to correct. **All six of REVIEW 2's mutant survivors are
> KILLED.** Every figure in `Q-057`'s new correction note reproduces at the pin, checked here by
> `ast` over the git blob. `INC-39`'s `Action` is corrected in place with its original words left
> standing, and its measured claim — *"total deletions to `QUESTIONS.md` across all of FIX 1's
> commits are ZERO"* — is **reproduced independently here**.
>
> ⚠️ **THE FAIL IS ON THE ONE CLAUSE OF THE PASS BAR THAT IS NOT ABOUT THE BLOCKERS: five
> non-equivalent survivors in the fix's own new code**, all five tracing to **two assertions that
> compare a list against itself and therefore cannot fail.** Under them, a `branch_b_condition`
> reading *"a harness defect is **SOMETIMES** Branch B"* — the direct inversion of `Q-057`'s ruling —
> passes the entire repository.

---

## 0. Verdict, and exactly what it turns on

| PASS condition (from the prompt) | result |
|---|---|
| both BLOCKERs closed by changes that go red when reverted | ✅ **B-3 and B-4 both CLOSED**, 8 reverts red, every sealed polarity held |
| all six of REVIEW 2's survivors killed | ✅ **6 / 6 KILLED** |
| **every new-surface mutant killed or proven equivalent** | ❌ **16 run: 11 killed, 5 SURVIVED**, and all five are **non-equivalent by exhibit** |
| the scoped reimplementation agreeing | ✅ **8 / 8** branch-condition checks, **43 / 43** provenance vectors |
| **zero BLOCKERs** | ✅ **ZERO** |

**Every pre-committed polarity in the seal came out where it was written down.** The FAIL is not a
polarity that flipped; it is the mutation clause, on a surface no review had seen.

⚠️ **THIS IS NOT A JUDGEMENT ON THE FIX'S QUALITY, and the shape of the verdict says so: zero
BLOCKERs.** The fix closed two BLOCKERs, killed six survivors, corrected its own predecessor's
`Action` field **in place** rather than quietly, declared a red it caused and stopped on it rather
than working around it, and declared two of its own fixtures wrong — one of which
(**`INC-50`**) it found by re-reading a test it had just written to close a survivor. The five
survivors below are what is left when that work is checked at the standard the prompt sets.

⚠️ **CONSISTENCY, STATED BECAUSE IT IS THE ONLY DEFENCE AGAINST A SCHEDULE-DRIVEN VERDICT.** C6
REVIEW 3, six hours earlier and in this same repository, returned **FAIL with zero BLOCKERs on six
non-equivalent survivors in a fix's own new code** — the same clause, the same shape of work. Five
of the same class here cannot be a PASS. It is 02:30 with two days left; that is exactly the
condition under which the standing instruction *"do not pass because the project is behind
schedule"* earns its place, and it is also why the reverse — a manufactured third FAIL — is named
and answered in §7.

---

## 1. Phase 1 — the seal, and the ordering `OF-89` kept breaking

**`OF-80`'s ruling: on a re-review, Phase 1 is blind to the FIX, not to the FINDINGS.**

`docs/reviews/independent/c13_review3_criteria.md`, committed at **`90abb2d`**, states for **B-3**,
**B-4** and every `OF-` item REVIEW 2 left open what must be true, the exact probe, and the expected
result **with its polarity pre-committed** — plus the standard the Class B predicate would be judged
against (**J-1…J-4**), the ten new-surface mutant shapes (**N-1…N-10**), and the rule of decision
for the `Action` audit.

⚠️ **NOT OPENED BEFORE THAT COMMIT**, declared so the seal is checkable: FIX 2's commits (no
`git show`, no `git diff`, no `git log -p`), `docs/sessions/c13-fix-2.txt`,
`src/whetstone_gate/camel_comparator/`, `tests/test_c13_camel_comparator.py`, **`config/lanes.yaml`**
(tighter than the ruling required — see the criteria's §0), `INCIDENTS.md` INC-46…INC-50, and
`OPEN_FINDINGS.md` at HEAD. `OF-96`…`OF-103` were read **at `24e26e5`** — REVIEW 2's own commit,
before the disposition — which is the reading C6 REVIEW 3 took at `29f40e3`.

⚠️ **THREE LEAKS ARE DECLARED IN THE SEAL ITSELF**, because the prompt's mandated read order
discloses part of the fix: `Q-079`'s *"What landed under it"* paragraph (which names the added key
**and the test's name**), `Q-057`'s dated correction note (**which IS B-4's remedy**), and `Q-079`'s
note that `camel_comparator.branch` is unchanged. Every criterion is written as *what must be true*,
never as *what was done*, and B-4's criteria are consequently **not** *"was a note written"* — that
was already visible — but *"is every figure in it true at the pin"*, which is the part only a review
can add.

⚠️ **AND THE ORDERING HELD.** `8c49c4d3` sealed before registering its token row and turned
`make test` red on two invariants; `91eb51c1` registered its row after four commits already carried
its trailer. `3605d31c` was the first to reverse it. **This session is the second**: row 41 is
`87a4aec`, the seal is `90abb2d`, and `check-roles` E1 was never red on this session.

### 1.1 Every pre-committed polarity, and whether it held

| sealed in `90abb2d` | expected | measured | held? |
|---|---|---|---|
| **P-B3-1** `grep -c "the model id is still served" config/lanes.yaml` | **0** | 0 | ✅ |
| **P-B3-2** both keys resolve through the loader | both non-empty, neither raises | both | ✅ |
| **P-B3-3** every §8.5.1 phrase present in `branch_b_condition` | all present | all 4 | ✅ |
| **P-B3-4** revert `branch_a_condition` | **RED** | 1 failed / 97 | ✅ |
| **P-B3-5** delete `branch_b_condition` | **RED** | 1 / 97 | ✅ |
| **P-B3-6a–d** delete each phrase from config, one at a time | **RED on EVERY phrase individually** | 4 × (1 / 97) | ✅ |
| ⚠️ **P-B3-7** amend the **LAW** only | **RED, and RED AT THE LAW** | RED, on `assert phrase in section` | ✅ |
| **P-B3-8** requirement derived from `CONTEXT.md` before `config/` | derived from the law first | confirmed in source | ✅ |
| **OF-96** `N11` | **KILLED** | KILLED | ✅ |
| **OF-97** `N13` | **KILLED** | KILLED | ✅ |
| **OF-98** `N8` | **KILLED** | KILLED | ✅ |
| **OF-100** | **KILLED** | KILLED | ✅ |
| **OF-101** `N14` | **KILLED** | KILLED | ✅ |
| **OF-102** `N6` | **KILLED or proven equivalent by exhibit** | KILLED | ✅ |
| **T-1** `make selftest` RED on `camel_comparator.branch` | **RED, for that reason** | 1 failed, 1 passed, 735 deselected | ✅ |
| **T-2/3/5/6** vendored pins · goldens · `evals/` · v1.9 | all clean | all clean | ✅ |
| **C-ctl** the control | **GREEN** | 98 passed, 0 failed | ✅ |

**Twenty for twenty.** The criteria were written before the fix was seen, so this is a test and not
a description.

---

## 2. BLOCKER B-3 — **CLOSED.** The trigger is narrowed, and the correction goes red eight ways

`config/lanes.yaml`, read **through the loader** by this session's own reimplementation:

```
branch_a_condition: "IT RUNS: both passes of the two-pass protocol complete inside the 90-minute
                     box, from the same working directory. Pass 1 is `--model
                     google:gemini-2.0-flash-lite-001 --suites banking --run-attack`; pass 2 is the
                     same command with --replay-with-policies, and it reads the logs/ tree pass 1
                     wrote. Publish the live table"
branch_b_condition: "THE RUN DOES NOT COMPLETE, ON A CAUSE THAT HAS BEEN DIAGNOSED AND RECORDED IN
                     PROTOCOL.md BEFORE A BRANCH IS SELECTED. 'It errored' is not a cause, and a
                     harness defect is NEVER Branch B - a provider error on the suffixed string is a
                     HARNESS DEFECT, because dispatch succeeds on substring containment and the
                     suffixed string reaches genai.Client as a model id (Q-057). A
                     pre-registration whose negative branch can be reached by our own bug measures
                     nothing"                                                        <-- ADDED
```

`"the model id is still served"` — the phrasing `Q-057`'s ruling identifies as indistinguishable
from a harness defect — **occurs zero times in the file.** Branch B's trigger is now a **stated
condition**, not the negation of another key, which is `Q-079`'s option 1 exactly.

### 2.1 The revert proof, run by this session in a fresh temp clone

Every one of the eight goes **red**, each on its own (`mutants/c13_mutants_3.md` §2). The four
phrase deletions die **individually**, so the guard is not one lump that any change trips.

### 2.2 ⚠️ THE ORDER OF ASSERTION — verified in the source **and** by mutation

The prompt asks whether the fix really requires each phrase **of `CONTEXT.md` §8.5.1 first and only
then of `config/`**, *"the difference between a test and a copy."* **It does, and it is not a
claim — it is the code's order:**

```python
# -- 1. The law still says it. Asserted BEFORE anything is required of `config/`. -----
for what, phrase in invocation.BRANCH_B_REQUIREMENTS:
    assert phrase in section, "CONTEXT.md §8.5.1 no longer carries {what} ..."
assert invocation.SUPERSEDED_BRANCH_TRIGGER not in section, ...
# -- 2. `config/` agrees with it, read THROUGH THE LOADER. ---------------------------
assert invocation.branch_condition_problems(condition_a, condition_b) == []
assert invocation.branch_conditions_are_stale() == []
```

**Probed, not read:** amending `CONTEXT.md` §8.5.1 alone — *"ON A CAUSE THAT HAS BEEN DIAGNOSED"*
removed, `config/lanes.yaml` untouched — turns the suite red, and the failure is the law's:

```
AssertionError: CONTEXT.md §8.5.1 no longer carries the diagnosis requirement
('on a cause that has been diagnosed'). This test requires it of config/ ONLY because the law
states it; if the law moved, config/ is not the thing to correct and this assertion is the one
that must be read first.
```

⚠️ **THAT IS THE RIGHT PLACE AND THE RIGHT MESSAGE.** The fix's claim is true. `Q-064`'s
generalisable half — *"no mechanism knows that a citation has copies"* — is answered here for this
one pair: there are two copies and the law is the one that wins.

### 2.3 ⚠️ THE CLASS B PREDICATE — the rationale is SOUND; the implementation is one step short

Judged against **J-1…J-4**, pre-committed in the seal before the code was opened.

| | verdict |
|---|---|
| **J-1 — is the rationale sound *in this repository*?** | ✅ **YES, and it is this chunk's own.** `REVIEW_13_1.md`'s **BLOCKER B-2** was exactly *"a property enforced only in a test file is a property that holds until somebody adds a figure without running the tests"*, and the remedy accepted there was to make `render_branch_b` **refuse**. A predicate in `src/` is the remedy C13's own prior BLOCKER established. |
| **J-3 — did it widen the fence?** | ✅ **NO.** `invocation.py`'s import set is **byte-identical** before and after: `['.', '..', '__future__', 'ast', 'dataclasses', 'pathlib', 're']`. No new dependency, no module outside `camel_comparator/`. |
| **J-2 — is it inert?** | **Partly.** It is exercised — and it buys something real: the guard is **firable at a constructed value**, so it is proved red without `config/` ever holding the defective string (`INC-11`, `INC-17`), and the test uses that. But it is **not consulted by any non-test caller.** |
| ⚠️ **J-4 — the deciding question: does it make the property hold when the tests are NOT run?** | ❌ **NOT YET.** Measured: `branch_conditions_are_stale`'s only caller anywhere is `tests/test_c13_camel_comparator.py:1099`, and it is **not in `camel_comparator.__all__`**. Contrast the two precedents it cites: `branch_value_problem` is called by `branch_is_undecided` (`invocation.py:324`), which **is** exported and is what `make selftest` fires; `branch_b.assert_provenance` is called by `render_branch_b` (`branch_b.py:556-558`), which is why deleting it is red. |

**So: not scope creep — it adds no import, widens no fence, follows an established shape in the same
module, and does real work the test relies on. But the rationale over-claims.** *"RUN-1 can call it;
CI is not the only reader"* is a statement about possibility; today there is no reader but CI, and
the module does not export it. **The Class B classification is correct; the deviation has not yet
bought what it was declared for.** One line — export it and call it from `branch_is_undecided`'s
neighbourhood, as `branch_value_problem` already is — closes the gap. Recorded as `OF-118`.

---

## 3. BLOCKER B-4 — **CLOSED.** Every figure re-derived at the pin by this session

`Q-057`'s fact 4 is **left standing**, and a dated correction note sits **directly beneath it**,
before the *"So the run is two passes"* paragraph — not at the end of the entry, which matters
because that entry's status is *"BLOCKING RUN-1 if unread"*.

**Verified first-hand against the CaMeL blob at `f083b6b396399d3b3c7f2ddaf613a5945eaf32d8`, by
`ast` over `git cat-file blob`. The tree is never imported.**

| the note says | measured here | ✓ |
|---|---|---|
| the live function is **`replay_task`** | `replay_task` spans **129–238** | ✅ |
| the construction is at **140–145** | `Assign.value` = **(140, 145)**; the enclosing `Assign` = **(139, 146)**; line 139 is `trace_path = (`, line 146 is `)` | ✅ **both `OF-103` spans true, and labelled** |
| the read is at **`:148`** | `execution_trace = TaskResults.model_validate_json(trace_path.read_text())` at **148** | ✅ |
| the call site is **`:305`** | `replay_task(...)` at **305**, inside `PrivilegedLLMReplayer.query` (**287–315**) | ✅ |
| **`replay_benchmark` has no caller in the tree** | `git grep replay_benchmark` at the pin returns **exactly one hit — its own `def` at :347**. Chain: `replay_user_task` ← `replay_suite` (:344) ← `replay_benchmark` (:356) ← ∅. `models.py:16` imports only `PrivilegedLLMReplayer` and `UserInjectionTasksGetter` | ✅ |
| **`:321` is inside `replay_user_task`** | `:321` = `path = Path("logs") / pipeline_name / …`, owned by `replay_user_task` (318–337) | ✅ |
| the failure is **an unhandled `FileNotFoundError`, loud** | `replay_task`'s **only** `Try` is **(185, 198)** and **148 is outside it**; `PrivilegedLLMReplayer.query` has **ZERO** `Try` nodes | ✅ |

**Every figure in the note is true.** RUN-1 can act on that sentence.

### 3.1 `INC-39`'s `Action` — corrected **in place**, original words standing

The original `Action` text is present, unaltered, with a dated correction block attached beneath it
that names what landed and what did not, and says why the entry is not silently repaired: *"an entry
that quietly repairs its own false claim is the failure this correction is about."*

⚠️ **Its load-bearing measurement, reproduced independently here rather than accepted:**

```
commits carrying `Session-Token: fd8a67e9` (C13 FIX 1), QUESTIONS.md numstat:
  ef4b8d5   1 0     f17709c   214 0     f4a38b7 041abe4 5d13fcd 3c5ef93 4a75bf7 9152cca  (untouched)
  TOTAL DELETIONS TO QUESTIONS.md ACROSS ALL OF THEM = 0
```

**A correction to an existing line is a deletion; there were none; so the claim of a fifth
correction could not have been true.** The entry's argument is sound and its arithmetic is right.
*(One number to note without weight: the scan finds **eight** FIX 1 commits, not the "seven" REVIEW 2
and this entry both say — the eighth is `9152cca`, the FINAL OUTPUT commit. It touches nothing this
turns on.)*

### 3.2 ⚠️ `INC-47`'s OWN FINDING, APPLIED TO THIS FIX — does any `Action` in INC-46…INC-50 overstate?

The rule of decision was fixed in the seal (**B4-k**) with **no polarity pre-committed**, deliberately.

| entry | every checkable `Action` claim | verdict |
|---|---|---|
| **INC-46** | ruling recorded before the edit (`e2b4778` 01:08:45 → `778c8f2` 01:10:31 ✅); `branch_a_condition` narrowed ✅; `branch_b_condition` added ✅; a test reads both **through the loader** ✅; file still parses ✅; `camel_comparator.branch` still `TODO_C13_RUN1` ✅; `make selftest` still RED on that sentinel ✅; `check-prereg` **NOT-YET-FROZEN, exit 0** ✅ | ✅ **no overstatement** |
| **INC-47** | note appended to `Q-057` beneath fact 4 ✅; names `replay_task` / 140-145 / `:148` / `:305` / `:321`-has-no-caller — **all five re-derived at the pin above** ✅; fact 4 not edited ✅; `INC-39`'s `Action` corrected in place with original words standing ✅ | ✅ **no overstatement** |
| **INC-48** | `e2b4778` not amended ✅ (`git log -1` shows it unchanged); nothing reverted ✅; `3605d31c`'s row present **exactly once** ✅; its paragraph **whole — 40 lines, first and last line intact** ✅; carried in this entry + `PROGRESS.md` + FINAL OUTPUT ✅. ⚠️ *"from the next commit onward this session stopped using `git commit -- <paths>` entirely"* is a claim about a **command**, which git records the result of but not the form of. Its checkable consequence holds: **no FIX-2 commit after `eb17627` carries foreign content** — every `3605d31c` marker in those diffs is the session's own prose *about* the sweep, checked line by line | ✅ **no overstatement**; one clause unverifiable in principle, and its consequence checks out |
| **INC-49** | *"NOTHING WAS FIXED, AND THAT IS THE ACTION."* — measured: **no FIX-2 commit touches `check_roles.py` or `test_repo_invariants.py`**; `E5_EXCEPTIONS` still holds **exactly four** C0-era SHAs; the red is declared in the FINAL OUTPUT and in `Q-080` | ✅ **no overstatement** |
| **INC-50** | *"`dfffba7` adds the mirror … asserts that the reversal actually happened"* — read at HEAD: the fixture is split and re-joined, `assert mirrored.index('"/var/logs"') < mirrored.index('"logs"')` pins the reversal, and `reflected.root_literal == "logs"` pins the outcome | ✅ **no overstatement** |

⚠️ **ANSWER: NO `Action` FIELD IN `INC-46`…`INC-50` OVERSTATES WHAT ITS COMMITS DEMONSTRATE.**
`INC-47`'s class does not recur here. Two entries go further than the format requires and **name what
they did not do** — `INC-49`'s `Fix:` is *"NONE, AND THE ABSENCE IS THE ENTRY"*, and `INC-46` names
`camel_comparator.branch` as unchanged so it is not read as covered.

---

## 4. THE SIX SURVIVORS — **6 / 6 KILLED**

Re-run by this session in a fresh OS temp clone, `whetstone_gate.__file__` printed, each mutation
**committed inside the clone**, control green first. Full table: `mutants/c13_mutants_3.md` §1.

| finding | mutation | killed by |
|---|---|---|
| **OF-96** | delete the Windows disjunct of `_is_relative_literal` | `test_BOTH_path_flavours_are_pinned_including_the_WINDOWS_half` |
| **OF-97** | add `"glob"` to `crashes_loudly`'s loud set | `test_crashes_loudly_is_pinned_in_its_FALSE_direction_too` |
| **OF-98** | `len(live) != 1` → `< 1` | `test_the_refusal_is_EXACTLY_ONE_reachable_and_not_merely_AT_LEAST_ONE` |
| **OF-100** | restore `setdefault` (keep the FIRST definition) | `test_a_shadowed_module_function_resolves_to_the_definition_PYTHON_binds` |
| **OF-101** | `fullmatch` → `match` | `test_the_figure_provenance_gate_goes_red_on_each_field_in_turn` (+3) |
| **OF-102** | drop the table key from `banking_rows` | `test_banking_rows_is_keyed_on_the_TABLE_and_not_saved_by_tuple_ORDER` |

**And the two fixtures the fix declared wrong are both corrected, verified here:**

* **The APPENDIX regex fixture that pinned nothing** — `OF-101`. The parametrised case fired only
  the **plural** `Tables 5-7`, which `match` rejects anyway, so `fullmatch` was unpinned. Measured
  independently by this session's reimplementation: of 28 table/figure vectors, **6 discriminate
  `fullmatch` from `match`**, and the **singular** `Table 5-7` is one of them while the plural is
  not. The fix's added singular fixture is the right one, and `N14` now dies.
* **`INC-50` — a test green by accident of its fixture.** One definition order cannot separate
  *"keep the last"* from *"keep whichever is absolute"*. The mirror reverses the two definitions and
  **asserts the reversal happened**, so it cannot degrade into a copy of the case above it.

⚠️ **AND A THIRD INSTANCE OF THAT CLASS WAS LOOKED FOR, AS THE PROMPT ASKED. IT EXISTS, AND IT IS IN
THE FIX'S OWN NEW TEST** — §5 below. **That class has now appeared five times in this repository.**

---

## 5. ⚠️ THE FIX'S OWN NEW CODE — 16 mutants, **11 killed, 5 NON-EQUIVALENT SURVIVORS**

No review had seen any of this. **This is the FAIL.**

### 5.1 Killed

`N-A` (the superseded trigger made unreachable), `N-F` (the predicate stops refusing it), `N-G` (a
blank condition reads as a pass — `Q-079`'s actual HEAD state), `N-H` (the `branch_b` half never
runs), plus the eight config/law probes of §2.1–2.2. **Eleven.**

### 5.2 ⚠️ The five survivors, each non-equivalent **by exhibit**

`A` held at HEAD's `branch_a_condition`; the exhibit is a `branch_b_condition` on which HEAD and the
mutant disagree, measured by calling the predicate directly.

| mutant | the weakening | the exhibit | HEAD | mutant |
|---|---|---|---|---|
| **N-B** | `"on a cause that has been diagnosed"` → `"cause"` | *"THE RUN DOES NOT COMPLETE **for some cause** …"* | flags **1** | ⚠️ **0** |
| **N-C** | `"a harness defect is never branch b"` → `"harness"` | *"… a harness defect is **SOMETIMES** Branch B …"* — **the direct inversion of `Q-057`'s ruling** | flags **1** | ⚠️ **0** |
| **N-D** | `"protocol.md"` → `"md"` | *"… recorded in **CONTEXT.md** before a branch is selected …"* — the wrong file | flags **1** | ⚠️ **0** |
| **N-E** | delete one whole `BRANCH_B_REQUIREMENTS` entry | as N-C | flags **1** | ⚠️ **0** |
| **N-I2** | `lanes.require(…)` → `lanes.data.get("camel_comparator", {}).get(key, "")` | `branch_b_condition` set to the **sentinel** `TODO_C14_PENDING` | **`UndeterminedValue: … (sentinel 'TODO_C14_PENDING')`** — hard rule 9's **refusal** | ⚠️ four content complaints — **the sentinel is USED as a value, not refused** |

⚠️ **THEY SURVIVE THE WHOLE REPOSITORY, NOT ONLY THE C13 FILE.** N-B+N-C+N-D+N-I2 applied together,
full suite: **2 failed, 722 passed, 1 skipped** — both failures pre-existing. N-E alone, full suite:
**2 failed, 722 passed, 1 skipped** — the same two. **Nothing anywhere kills them.**

### 5.3 One defect, not five — and it is `INC-50`'s class again

`tests/test_c13_camel_comparator.py:1116-1121`:

```python
undiagnosed = invocation.branch_condition_problems(condition_a, "the run does not complete")
assert len(undiagnosed) == len(invocation.BRANCH_B_REQUIREMENTS)      # <-- compares the list to itself
for what, _ in invocation.BRANCH_B_REQUIREMENTS:
    assert any(what in problem for problem in undiagnosed)            # <-- compares the list to itself
```

**Both assertions compare the predicate's output against the predicate's own input list, so neither
can fail when that list changes.** Drop an entry and both sides move together (N-E). Weaken a phrase
and the `what` labels are untouched, so the loop still passes (N-B/C/D). The law-side assertion does
not catch it either: `"cause"`, `"harness"` and `"md"` **all occur in §8.5.1**, so `assert phrase in
section` is satisfied by every weakened form. And the single fixture, `"the run does not complete"`,
contains none of the four phrases **at any strength**, so it cannot separate a strong requirement
from a weak one — **which is exactly `INC-50`: a test green by accident of its fixture, written the
same night, by the session that wrote `INC-50`.**

**Remedy, and it is small.** One fixture per requirement that carries the *weak* form and not the
strong one — e.g. a `branch_b_condition` saying *"a harness defect is SOMETIMES Branch B"* — asserted
to be **rejected**; and one assertion that `len(BRANCH_B_REQUIREMENTS) == 4` against a literal, so
the list's size is pinned by something outside itself. For **N-I2**: one assertion that
`branch_conditions_are_stale()` returns an `UndeterminedValue`-shaped refusal when the key is a
sentinel.

**Withdrawn as equivalent, and it is this reviewer's error:** the first form of the loader-bypass
mutant was guarded by `hasattr(lanes, "get")`, and `Config`'s surface is
`['data','has','name','path','require','sentinels']` — **no `get`** — so it was a no-op. Replaced by
**N-I2**, which uses the real API. Recorded rather than deleted, because dropping it silently would
have inflated the survivor count by one.

---

## 6. The scoped reimplementation — **agreeing**

`docs/reviews/independent/c13_review3_reimpl.py`. Stdlib only; asserts at run time that
`whetstone_gate` is **not** in `sys.modules`; parses `config/lanes.yaml` with **its own** minimal
YAML reader rather than the project's loader, because the loader is `src/`.

⚠️ **The requirements are DERIVED FROM `CONTEXT.md` §8.5.1 at run time, never transcribed** — so the
file's expectations move with the law rather than becoming a third copy.

| | result |
|---|---|
| requirements derived from §8.5.1 | Branch A: `run-completes`; prohibited in A: `the model id is still served`; Branch B: `diagnosed-cause`, `it-errored-is-not-a-cause`, `harness-defect-is-never-branch-b`, `protocol-md-before-the-branch` |
| **branch-condition predicate** | ✅ **8 / 8 hold** |
| **table/figure regex, 28 vectors** | ✅ **28 / 28 agree** |
| **appendix regex, 15 vectors, both readings** | ✅ **15 / 15 agree** |
| total vectors | **43** (`docs/reviews/README.md` asks for ≥ 20) |

⚠️ **ONE DIVERGENCE, AND IT IS THIS FILE'S, NOT THE PROJECT'S — declared rather than absorbed.** The
sealed form of the `run-completes` recogniser was `\brun\b[^.]{0,60}\bcomplet` and it reported FAIL
against a config reading *"IT **RUNS**: both passes … **complete** inside the 90-minute box"*:
`\brun\b` cannot match `RUNS`. The recogniser was widened to `\bruns?\b[^.]{0,80}\bcomplet`, **the
sealed original is preserved in a comment at the site**, and the requirement it recognises is
unchanged. **The config met B3-b all along; the reviewer's pattern did not.**

⚠️ **And the two readings of the appendix field both computed, because both are defensible.**
`CONTEXT.md` v1.9 writes *`Appendix B ("Full results tables")`* while the field itself is
*`Appendix B`*; the strict and with-title recognisers differ on exactly those two vectors and agree
on the other thirteen. Recorded as a datum, not asserted as a defect.

---

## 7. Q-080 / INC-49 — the declared STOP, judged. **STOPPING WAS RIGHT, on all three remedies**

`make test` is red at HEAD on `tests/test_repo_invariants.py::test_check_roles_exits_zero`, because
`check_roles` E5 reads `c4d4460`'s **line 22** — prose beginning `Session-Token:` at column 0 — as a
malformed trailer. **E1, E2 and E3 all PASS**: the commit is correctly tokened and role separation is
not in doubt.

`INC-49` claims all three real remedies were the architect's. **Checked, each on its own:**

| remedy | blocked? |
|---|---|
| **1. amend `c4d4460`** | ✅ `CLAUDE.md` §5: *"No history rewrite, **ever**"*, with no exception for an untagged tip. The entry names the gap between the rule's rationale and its wording and declines to close it — which is hard rule 1's own instruction. |
| **2. add it to `E5_EXCEPTIONS`** | ✅ measured at FIX 2's own HEAD: the dict holds **exactly four** SHAs, all C0-era `WG-2026-08-30-CTX-13.4-A` commits, and its comment forbids extension without a ruling. |
| **3. fix the parser** | ✅ `src/whetstone_gate/check_roles.py` is named under **NOT** in FIX 2's fence, and widening `_TOKEN_TRAILER` was already declined by **`Q-014 (i)`**, recorded verbatim as *"That stands and is not reopened."* |

⚠️ **AND THE ARCHITECT HAS SINCE RULED, WHICH SETTLES IT RATHER THAN LEAVING IT TO JUDGEMENT.**
`Q-080` is **RULED: REMEDY 3**, and the ruling rejects 1 and 2 **on the entry's own grounds, nearly
in its own words** — *"amending is a history rewrite, forbidden absolutely by `CLAUDE.md` S5 with no
exception for an untagged tip; and `E5_EXCEPTIONS` is pinned at four by its own comment, whose four
entries are C0-era commits with no prompt token to carry — a different thing from a session that had
one and quoted it."* It also holds that remedy 3 **does not reopen `Q-014 (i)`** — a determination
only the architect could make, which is precisely why a fix session could not take it.

⚠️ **IT IS NOT A REASON TO FAIL C13, AND IT IS NOT COUNTED AS ONE.** It was Session A's task 1, and
**it was CLOSED during this review**: **NIGHT RUN SESSION A / C0 FIX (`9c7c5973`)** landed `061dcd9`,
`28b6eec`, **`ea3bd12`** (the parser fix) and `867b571` in this tree while Phase 2 ran. Measured
after them: `make check-roles` = **17 passed, 0 failed, 5 n/a — OK**. **The red `INC-49` declared is
gone, and not by anything C13 did or should have done.**

---

## 8. `INC-48` — the swept content is intact

| check | result |
|---|---|
| `3605d31c`'s token row present **exactly once** | ✅ `grep -c` = **1** |
| its paragraph **intact and complete** | ✅ **40 lines**, heading through *"…carry **0 CR bytes**."*, one occurrence of the heading |
| **no counter collided** in the token table | ✅ `3605d31c` = row 39, `91eb51c1` = row 40, this session = row 41; each predecessor's count reconciles against the table |
| recorded, **not repaired by rewriting history** | ✅ `e2b4778` stands unamended; `INC-48` exists |
| ⚠️ **a counter DID collide elsewhere** | ❌ see `OF-115` below |

---

## 9. Standing properties — all measured by this session

| property | measured |
|---|---|
| `make selftest` **RED on `camel_comparator.branch`, and FOR THAT REASON** | ✅ **1 failed, 1 passed, 735 deselected**; sole failure `test_the_camel_branch_is_decided_before_any_camel_run` on `UndeterminedValue: lanes.yaml: 'camel_comparator.branch' … (sentinel 'TODO_C13_RUN1')` — the loader **refusing**, not defaulting |
| all three vendored trees at their pins, status empty, zero-byte diffs | ✅ CaMeL `f083b6b3…` · AgentDojo `928bbae8…` · τ²-bench `a2c02472…`; all three `git status --porcelain` **EMPTY**; diffs **0 bytes each** |
| `git status --porcelain tests/goldens/` | ✅ **empty** |
| no `evals/` path in any C13 commit | ✅ **0** across all 14 FIX-2 commits |
| `evals/usage/` empty → C13 spent nothing | ✅ **0 files under `evals/` at all** |
| `CONTEXT.md` still **v1.9** and untouched since REVIEW 2 audited it | ✅ blob `8e820384afbb1de7de3892eb6b90a8e6dce1f378` — **identical** at HEAD, at REVIEW 2's `24e26e5`, and at the v1.9 amendment `041abe4`. 224,645 bytes, **LF 2,361 · CR 0 · TAB 0 · 0x08 0 · no other control byte** — REVIEW 2's figures exactly |
| **this review** spent no tokens | ✅ **zero provider calls.** CaMeL not run, not installed, not imported — parsed as a git blob. ⚠️ **Whether the model id is still served was NOT checked** — Branch A's condition and RUN-1's alone |
| `check-prereg` | ✅ **NOT-YET-FROZEN** — `PROTOCOL.md` does not exist; exit 0. `git tag -l` = `c0-pass`…`c4-pass`; **`prereg-v1` does not resolve** |
| FIX 2's file scope | ✅ nine paths, all inside its fence; **no `src/` outside `camel_comparator/`**, no `check_roles.py`, no `CONTEXT.md`, no `config/` beyond `lanes.yaml` |

### 9.1 Suite counts, measured — with every failure attributed BY FILE

⚠️ **A concurrent Session A is editing this tree**, so figures are stated as measured and each run is
named.

| run | result | attribution |
|---|---|---|
| `tests/test_c13_camel_comparator.py` at HEAD | **98 passed, 0 failed** | — |
| the same file in this review's **isolated temp clone** (the control every mutation is judged against) | **98 passed, 0 failed** | — |
| bare `python -m pytest` at HEAD, before Session A's commits | **3 failed, 721 passed, 1 skipped** | `test_lanes_operator_placeholders.py::test_the_camel_branch_is_decided_before_any_camel_run` — **deliberate**, deselected by `make test`; `test_repo_invariants.py::test_check_roles_exits_zero` — **`Q-080`/`INC-49`, Session A's**; `test_repo_invariants.py::test_the_object_store_and_the_working_tree_agree` — ⚠️ **MINE**, this review's own uncommitted edit to `docs/reviews/independent/c13_review3_reimpl.py`, cleared by committing it |
| full suite in the temp clone, unmutated | **2 failed, 722 passed, 1 skipped** | the two above, minus this review's own |
| ⚠️ **`make test` at HEAD, AFTER Session A's `ea3bd12`** — run **twice**, minutes apart | **1 failed, 737 passed, 1 skipped, 2 deselected** *(both runs identical)* | the sole failure is `test_repo_invariants.py::test_the_object_store_and_the_working_tree_agree`, on `docs/reviews/independent/c13_review3_reimpl.py` — ⚠️ **THIS REVIEW'S OWN uncommitted artefact**, and it clears when this session commits. ✅ `test_check_roles_exits_zero` is **GREEN**: `make check-roles` = **17 passed, 0 failed, 5 n/a** |

**No failure in any run is C13's.** The counts moved between runs exactly as the prompt predicted,
because Session A was committing throughout; **every figure above is the one measured, and each is
attributed to the file that caused it.**

---

## 10. Findings

### 10.1 MEDIUM

**`OF-115` · ⚠️ A LIVE SOURCE DOCSTRING CITES `OF-104`, WHICH IS ANOTHER SESSION'S FINDING, AND B-3
HAS NO `OF-` ROW AT ALL.** `tests/test_c13_camel_comparator.py:1047` opens
*"⚠️ **`Q-079` / `OF-104`**, and the reason it existed is that NOTHING READ THIS KEY."* **`OF-104` at
HEAD is C6 REVIEW 3's** *"CLAIM 4'S GUARD IS BLIND TO AN ARM IDENTITY…"*, written by `3605d31c` at
`2be75b1` (02:16:52) — **55 minutes after** `4be0b86` (01:21:36) put the number into a live file.
And FIX 2's own disposition says in terms *"**THIS SESSION OPENS NO NEW `OF-` ROW**"*, so `OF-104`
was **never allocated to B-3**; B-3's actual `OF-` home is **`OF-62`**, whose second half this is.
**A forward reference to an unallocated number, which another session has since taken.** It is
`Q-063`/`INC-36`'s counter-collision class, in a source file rather than a journal, and it is the
same shape as `INC-39`/B-1 — a citation pointing at the wrong thing — inside the test written to
close B-3. **Not load-bearing for a number or for RUN-1**, which is why it is MEDIUM and not a
BLOCKER. **Remedy: cite `OF-62` and `Q-079`, or no `OF-` number at all.**

**`OF-116` · ⚠️ THE FOUR `BRANCH_B_REQUIREMENTS` PHRASES CAN EACH BE WEAKENED TO A SHORT SUBSTRING,
OR ONE DROPPED ENTIRELY, AND NOTHING IN THE REPOSITORY NOTICES.** Mutants **N-B, N-C, N-D, N-E**, all
four **non-equivalent by exhibit** (§5.2), all four surviving the **full suite**. Cause: the test's
two assertions over the list compare it **against itself** (`invocation.py` §5.3), and the law-side
`assert phrase in section` is satisfied by `"cause"`, `"harness"` and `"md"`, each of which occurs in
§8.5.1. **Under N-C and N-E a `branch_b_condition` reading *"a harness defect is SOMETIMES Branch B"*
— the inversion of the ruling this guard exists to enforce — passes.** **Remedy: one weak-form
fixture per requirement, asserted rejected; and `len(BRANCH_B_REQUIREMENTS) == 4` against a literal.**

**`OF-117` · `branch_conditions_are_stale()` READS THROUGH `require()` AND NOTHING ASSERTS IT.**
Mutant **N-I2**: replacing it with `lanes.data.get(…, "")` survives the full suite. **Non-equivalent
by exhibit:** with `branch_b_condition` set to the sentinel `TODO_C14_PENDING`, HEAD returns
`UndeterminedValue` — hard rule 9's refusal — while the mutant lets the sentinel flow in **as a
value** and reports four content complaints. The function's own docstring makes `require()` the
point (*"the only read path, so a missing file and a missing key are the same answer rather than two
different silences"*) and that property is unpinned. **Remedy: one assertion on the sentinel case.**

**`OF-118` · THE CLASS B PREDICATE IS NOT REACHABLE BY THE READER IT WAS DECLARED FOR.**
`branch_conditions_are_stale`'s only caller anywhere is the test, and it is **not in
`camel_comparator.__all__`** — so *"RUN-1 can call it; CI is not the only reader"* is not yet true.
Both precedents it cites do better: `branch_value_problem` ← `branch_is_undecided` (exported, fired
by `make selftest`), `assert_provenance` ← `render_branch_b`. **The deviation is correctly classed
and correctly reasoned; it has not yet bought what it was declared for.** **Remedy: export it and
give it one non-test caller.**

### 10.2 LOW

**`OF-119` · THE "LAW" WINDOW IS §8.5.1 **PLUS** §8.5.2, WHILE THE ERROR MESSAGE SAYS §8.5.1.**
`tests/test_c13_camel_comparator.py` ends the section at the next line starting `"## "`, and
`"### 8.5.2"` does not match that prefix — so the window runs to `## 8.6`. **Measured: 6,759 chars
against §8.5.1's own 3,592 — 88 % wider.** All four phrases live in §8.5.1 today (checked
individually), so the check is **correct now**; a phrase that moved into §8.5.2 would satisfy an
assertion whose message says §8.5.1 no longer carries it. **Latent, not live. Remedy: end the
section at `"### 8.5.2"`.**

### 10.3 Carried forward — **not C13's**, and not counted against it

* **`OF-99`** — the repository-wide superseded-string tripwire `Q-064` names and nobody has built.
  The prompt states Session A is closing it tonight.
* **`Q-074` / `OF-62`'s fifth site** — `tests/test_lanes_operator_placeholders.py:141` still says
  *"a citation of Tables 5-7"*, still the only live-text site, still printed in full by every
  `make selftest`. **Confirmed untouched by any C13 FIX 2 commit**, correctly: that file is outside
  the fence. It belongs to whichever session's fence next includes it.
* **`OF-103`** — the `140-145` / `139-146` spans. **Both re-derived here and both true**; `Q-057`'s
  correction note now labels them statement-vs-expression and states which to prefer. **Addressed.**

---

## 11. What the fix got right — recorded, because a FAIL that lists only faults is not a review

* **Every one of the twenty polarities this review pre-committed came out where it was written
  down**, including all eight of B-3's reverts and all six of REVIEW 2's survivors.
* **The law is asserted before the config, and it goes red at the law** — proved by amending
  `CONTEXT.md` alone, with a failure message that tells the reader `config/` is not the thing to
  correct. That is the difference between a test and a copy, and the fix's claim is true.
* **Branch B's trigger is a stated condition**, not the negation of another key — `Q-079`'s option 1,
  taken rather than argued around, **and each of its four phrases dies individually**.
* **Every figure in `Q-057`'s correction note is true at the pin**, re-derived here by `ast` over the
  git blob, including the `Try`-span arithmetic that turns a "silent zero" into a loud crash.
* **`INC-39`'s `Action` is corrected IN PLACE with its original words standing**, and its
  zero-deletions measurement reproduces exactly. **An entry that quietly repaired its own false claim
  would have been the failure `INC-47` is about, one turn later** — and it did not.
* **No `Action` field in `INC-46`…`INC-50` overstates what its commits demonstrate**, checked claim
  by claim. `INC-47`'s class does not recur.
* **Two of its own fixtures were declared wrong by the fix itself**, one of them found by re-reading
  a test it had just written — `INC-50`. That is the standard this project asks for.
* **The declared STOP was right on all three remedies**, and the architect's subsequent ruling
  rejects the two the entry rejected, **on the entry's own grounds**.
* **`CONTEXT.md` v1.9 is byte-identical** to what REVIEW 2 audited; `evals/` is empty; the vendored
  pins are clean; `make selftest` is still red on the sentinel **and for that reason**.

---

## 12. Artefacts

| path | what |
|---|---|
| `docs/reviews/independent/c13_review3_criteria.md` | the **Phase-1 seal** — every criterion and pre-committed polarity, `90abb2d` |
| `docs/reviews/independent/c13_review3_reimpl.py` | the **scoped reimplementation** — branch-condition predicate + the two provenance regexes, stdlib only, nothing from `src/` |
| `docs/reviews/independent/c13_review3_reimpl_output.txt` | its committed output — 8/8 and 43/43 |
| `docs/reviews/independent/c13_review3_mutants.py` | the mutation driver |
| `docs/reviews/mutants/c13_mutants_3.md` | **24 mutants** — 18 killed, 5 survived, 1 withdrawn as equivalent |

---

## 13. For the FIX session — the shortest path to a PASS

**Nothing below touches `config/`, `CONTEXT.md`, a number, or a figure. All of it is in
`tests/test_c13_camel_comparator.py` except `OF-118`'s one line.**

1. **`OF-116`** — replace the single `"the run does not complete"` fixture with **one weak-form
   fixture per requirement**, each asserted **rejected**: a condition containing `"cause"` but not
   *"on a cause that has been diagnosed"*; one saying *"a harness defect is SOMETIMES Branch B"*; one
   citing `CONTEXT.md` where `PROTOCOL.md` belongs. And assert `len(BRANCH_B_REQUIREMENTS) == 4`
   against a **literal**, so the list's size is pinned by something outside itself.
2. **`OF-117`** — one assertion that a **sentinel** `branch_b_condition` produces an
   `UndeterminedValue`-shaped refusal from `branch_conditions_are_stale()`.
3. **`OF-118`** — export `branch_conditions_are_stale` and give it one non-test caller, as
   `branch_value_problem` already has.
4. **`OF-115`** — cite `OF-62`/`Q-079`, not `OF-104`.
5. **`OF-119`** — end the §8.5.1 window at `"### 8.5.2"`.

**Tag `c13-pass` is NOT cut.** A FAIL that is not in the repository did not happen; this one is.
