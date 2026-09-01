# C13 REVIEW 3 — PHASE-1 CRITERIA SEAL

**Session `c09c385b` · C13 REVIEW, attempt 3 · 2026-09-02 · review type `full`, re-review after
C13 FIX 2 (`91eb51c1`).**

**This file is the seal.** It states, for each BLOCKER and each `OF-` item REVIEW 2 left open,
**what must be true**, **the exact probe**, and **the expected result with its polarity
pre-committed** — written and committed **before** any fix artefact was opened. Phase 2 then runs
the probes and records where each landed. A polarity that is written down afterwards is a
description; one written down before is a test.

---

## 0. THE BLINDNESS BOUNDARY, DECLARED SO IT IS CHECKABLE

`OF-80`'s ruling, recorded verbatim in `QUESTIONS.md` under the C6 REVIEW 3 heading and restated in
this session's prompt: **on a re-review, Phase 1 is blind to the FIX, not to the FINDINGS.**

**NOT OPENED BEFORE THIS FILE WAS COMMITTED** — no `git show`, no `git diff`, no `git log -p`, no
read of any kind:

| not opened | why it is on the list |
|---|---|
| **C13 FIX 2's thirteen commits** | they are the fix |
| **`docs/sessions/c13-fix-2.txt`** | the fix's own account of itself |
| **`src/whetstone_gate/camel_comparator/`** (the whole package, at any revision) | the changed surface |
| **`tests/test_c13_camel_comparator.py`** (at any revision) | the changed surface |
| **`config/lanes.yaml`** | ⚠️ **tighter than the ruling requires.** The scoped-reimplementation ruling names `config/` as a permitted *input*. It is excluded from **Phase 1** anyway, because `config/lanes.yaml`'s `camel_comparator` block **is** B-3's changed surface, and a criterion written after reading the answer is not a criterion. The reimplementation committed beside this file **reads it at run time in Phase 2**; the predicate it applies is fixed here, before the values are seen. |
| **`INCIDENTS.md` INC-46…INC-50** | written by the FIX; `Fix:` fields carry its SHAs |
| **`docs/reviews/OPEN_FINDINGS.md` at HEAD** | the `Closed by` cells were filled in by the FIX |

**READ, and named rather than left to be inferred:**

* `CLAUDE.md`, `docs/reviews/README.md`, all three personas, `PROCESS.md` §5.2/§5.3/§9.
* `CONTEXT.md` **v1.9** §4's AgentDojo row, §8.5, §8.5.1, §8.5.2 — **the file, never the diff**.
* `QUESTIONS.md` Q-057 (with its dated correction note), Q-058, Q-058 (Table 4), Q-064, Q-074,
  Q-079, Q-080, and the `## Session tokens` preamble.
* `docs/reviews/REVIEW_13_1.md` and `REVIEW_13_2.md` **in full**.
* `docs/reviews/OPEN_FINDINGS.md` **at `24e26e5`** — C13 REVIEW 2's own commit, **before** the
  disposition — for `OF-96`…`OF-103` as the review that raised them wrote them. This is the same
  reading C6 REVIEW 3 took at `29f40e3`, and it is what makes *"blind to the fix, not to the
  findings"* mean something.

### 0.1 ⚠️ THREE DECLARED LEAKS — the prompt's own read order discloses part of the fix

Declared here rather than discovered later. In each case the criteria below are written as **what
must be true**, never as *what was done*, and every polarity is pre-committed regardless.

1. **`Q-079`'s *"What landed under it (C13 FIX 2, `91eb51c1`)"* paragraph** is inside a mandated
   read. It states that `branch_a_condition` was amended, that a **`branch_b_condition` key was
   ADDED**, and it names the test
   `test_the_pre_registered_branch_condition_carries_the_DIAGNOSIS_requirement`. **So the shape of
   B-3's remedy is known to this session.** Its *content* is not: the criteria below are derived
   from `CONTEXT.md` v1.9 §8.5.1's own words, and B-3's probes are written to fail if the config
   merely *mentions* diagnosis without carrying the law's phrases.
2. **`Q-057`'s dated correction note** *is* B-4's remedy. It could not be excluded — the prompt
   names it in terms (*"INCLUDING the dated correction note under fact 4"*) and it is item 6 of
   `CLAUDE.md` §1's read order. **So B-4's criteria are not *"was a note written"*** — that is
   already visible — **but *"is every figure in it true at the pin"***, which is the only part a
   review can add.
3. **`Q-079` also names one thing NOT changed**: `camel_comparator.branch` still holds its
   `TODO_C13_RUN1` sentinel. That is a standing property below, not a finding.

---

## 1. BLOCKER B-3 — the un-narrowed trigger in `config/`

**What REVIEW 2 found.** `config/lanes.yaml:202`'s `branch_a_condition` read *"the model id is still
served AND the run completes inside the 90-minute box"* — the trigger `Q-057`'s ruling **narrowed**,
surviving in the artefact that outranks `CONTEXT.md` the moment `prereg-v1` exists. Branch B is the
**negation** of Branch A's condition, so as written `config/` bound the project to taking Branch B
whenever *"the run does not complete"*, **with no diagnosis requirement**.

**THE LAW THE FIX MUST MATCH — `CONTEXT.md` v1.9 §8.5.1, quoted here so the criteria are derived
from it and not from the fix:**

> **Branch A — it runs.**
> **Branch B — the run does not complete, ON A CAUSE THAT HAS BEEN DIAGNOSED.** ⚠️ **"It errored"
> is not a cause, and a harness defect is never Branch B.** RUN-1 records the diagnosed cause in
> `PROTOCOL.md` before it selects a branch.

### 1.1 WHAT MUST BE TRUE

| # | criterion |
|---|---|
| **B3-a** | `branch_a_condition` **no longer contains** the substring `the model id is still served` — the exact phrasing `Q-057`'s ruling identifies as indistinguishable from a harness defect. |
| **B3-b** | `branch_a_condition` states Branch A's condition as **the run completing**, in §8.5.1's own terms. |
| **B3-c** | A **`branch_b_condition`** key exists and Branch B's trigger is a **stated condition**, not only the negation of another key. |
| **B3-d** | `branch_b_condition` carries the **diagnosis requirement** — a cause that has been DIAGNOSED. |
| **B3-e** | `branch_b_condition` carries **"it errored is not a cause"** and **"a harness defect is never Branch B"**, the ruling's own words. |
| **B3-f** | `branch_b_condition` carries the **`PROTOCOL.md`-before-the-branch ordering**. |
| **B3-g** | ⚠️ **BOTH keys resolve THROUGH THE LOADER**, not by reading the YAML file directly — a `config/` value that only a raw parse can see is not a configured value under hard rule 9. |
| **B3-h** | ⚠️ **A TEST ASSERTS ALL OF THE ABOVE.** `Q-064` measured the cause and printed it as a number — *"nothing reads either key"* — and REVIEW 1 measured the same. **A pre-registered condition that nothing asserts is a comment.** |
| **B3-i** | ⚠️ **THE ORDER OF ASSERTION.** The assertion must be made **of `CONTEXT.md` §8.5.1 FIRST and only then of `config/`**, so neither side is transcribed and an amendment to the law goes red **at the law**. A test that hardcodes the phrase list and checks only `config/` is a **copy of the config into a test file**, and it goes green forever after §8.5.1 changes. |

### 1.2 THE EXACT PROBES, AND THE PRE-COMMITTED POLARITY

| probe | what is done | ⚠️ **EXPECTED, PRE-COMMITTED** |
|---|---|---|
| **P-B3-1** | `grep -c "the model id is still served" config/lanes.yaml` | **0** |
| **P-B3-2** | load `camel_comparator.branch_a_condition` and `…branch_b_condition` **through the project's config loader** (the loader only — no direct YAML read) | **both resolve to non-empty strings; neither raises `UndeterminedValue`** |
| **P-B3-3** | for each of the phrases B3-d/e/f name, assert its presence in the loaded `branch_b_condition` | **all present** |
| **P-B3-4** | **REVERT `branch_a_condition`** in a fresh temp clone to REVIEW 2's measured string and run the C13 file | ⚠️ **RED.** If it stays green the correction is unguarded and B-3 is **NOT** closed. |
| **P-B3-5** | **REVERT `branch_b_condition`** — delete the key entirely — and run the C13 file | ⚠️ **RED** |
| **P-B3-6** | **DELETE EACH REQUIRED PHRASE from `branch_b_condition` one at a time**, leaving the key present and the rest intact | ⚠️ **RED on EVERY phrase, individually.** A phrase whose deletion leaves the suite green is a phrase the test does not require, and B3-e/f are then unmet for that phrase. |
| **P-B3-7** | ⚠️ **THE ORDERING PROBE, which is the one that separates a test from a copy.** In a fresh temp clone, **remove one required phrase from `CONTEXT.md` §8.5.1** while leaving `config/lanes.yaml` untouched, and run the C13 file | ⚠️ **RED — AND RED AT THE LAW.** The failure must name §8.5.1 / the spec side, not the config side. **If it stays GREEN, the phrase list is hardcoded in the test and B3-i is UNMET.** If it goes red but only because config no longer matches a hardcoded list, that is the same defect wearing a different message. |
| **P-B3-8** | read the source of whatever asserts this and determine **whether the requirement is derived from `CONTEXT.md` before it is applied to `config/`, or the reverse** | **derived from `CONTEXT.md` first** |

### 1.3 THE CLASS B PREDICATE — pre-committed judgement criteria, not a verdict

`Q-079` discloses that the fix added a predicate **in `src/`** beyond the test that was asked for,
and declared it a **Class B deviation** on the rationale *"a property enforced only in a test file
holds until someone skips the tests."* **This session pre-commits the standard it will judge that
against, before seeing the code**, so the judgement cannot be fitted to what is there:

| # | the standard |
|---|---|
| **J-1** | **The rationale is sound in this repository, not merely in general**, if and only if the same argument is already load-bearing here. ⚠️ **It is:** `REVIEW_13_1.md`'s **BLOCKER B-2** is exactly this — a refusal that only a test asserted, where `render_branch_b`'s own docstring said *"a property enforced only in a test file is a property that holds until somebody adds a figure without running the tests"* — and the FIX closed it by making the renderer **refuse**. **So a predicate in `src/` that refuses is the remedy this chunk's own prior BLOCKER established.** Pre-committed: **if the new predicate refuses (raises/returns a failure that a caller acts on), J-1 is MET.** |
| **J-2** | **It is scope creep** if the predicate is **inert** — computed and never consulted — or if it duplicates spec text as a third copy that can drift. A predicate that only *returns* something nobody reads is a comment with a docstring, and it is then creep **and** ineffective. |
| **J-3** | It is scope creep if it **widens C13's fence**: touching a module outside `camel_comparator/`, or adding a dependency the package did not have. |
| **J-4** | ⚠️ **The deciding question, pre-committed:** *does the predicate make the property hold when the tests are not run?* If yes → sound, and the Class B classification is right. If no → creep, and it should have been the test alone. |

---

## 2. BLOCKER B-4 — the correction note, and the `Action` fields

**What REVIEW 2 found.** `Q-057`'s fact 4 still cited `replay_privileged_llm.py:321`; three separate
records (`INCIDENTS.md` INC-39's `Action`, `docs/sessions/c13-fix-1.txt:91`, `OPEN_FINDINGS.md`)
said the correction had been made. REVIEW 2's owed remedy was **either** (a) a dated correction note
appended beneath fact 4, **or** (b) INC-39's `Action` restated to say four of five.

⚠️ **The note exists — that is leak 2 above.** So the criteria are about **whether every figure in
it is true at the pin**, which is the part no record yet establishes, plus the second half of the
remedy.

### 2.1 WHAT MUST BE TRUE, AND THE PROBES

⚠️ **Every one of these is verified against the CaMeL checkout at the pin `f083b6b3…`, by this
session, with `whetstone_gate.__file__` irrelevant — the vendored tree is read as text and as a git
blob, never imported.**

| # | what must be true | probe | ⚠️ **EXPECTED, PRE-COMMITTED** |
|---|---|---|---|
| **B4-a** | fact 4 is **left standing**, not edited | `git log -p`-free check: the original four sentences of fact 4 are present verbatim at HEAD | **present, unaltered** |
| **B4-b** | the correction sits **directly beneath the line it corrects**, not at the end of the entry | read `Q-057` positionally | **immediately beneath fact 4, before the *"So the run is two passes"* paragraph** |
| **B4-c** | the live function is **`replay_task`** | `ast`-parse `replay_privileged_llm.py` at the pin; find the function whose body contains the `Path("logs") / …` chain that is read | **`replay_task`** |
| **B4-d** | the construction span is **140–145** | `ast`: the `Assign` node's `.value` `lineno`…`end_lineno` | **(140, 145)**; and the enclosing `Assign` is **(139, 146)** — `OF-103`'s two spans, both true |
| **B4-e** | the read is at **:148** | locate `trace_path.read_text()` | **line 148** |
| **B4-f** | the call site is **:305** | locate the call to `replay_task` inside `PrivilegedLLMReplayer.query` | **line 305**, and `query` spans **287–315** |
| **B4-g** | **`replay_benchmark` has no caller in the tree** | `git grep -n "replay_benchmark"` across the whole vendored CaMeL tree | ⚠️ **exactly ONE hit: its own `def`** |
| **B4-h** | `:321` is genuinely unreachable | walk `replay_task`←`query`; and `replay_user_task`←`replay_suite`←`replay_benchmark`←∅ | **`:321` is in `replay_user_task`; its only path to a caller terminates at `replay_benchmark`, which has none** |
| **B4-i** | the failure mode is **an unhandled `FileNotFoundError`, loud** | `ast`: enumerate `Try` nodes in `replay_task` and in `query`; check whether line 148 is inside any | **`replay_task`'s only `Try` is 185–198 and 148 is OUTSIDE it; `query` has ZERO `Try` nodes → loud** |
| **B4-j** | INC-39's `Action` is **corrected IN PLACE with its original words left standing** | read INC-39 | **the original `Action` text is still present AND a correction is attached to it; neither a silent overwrite nor a bare append at the end of the file** |

### 2.2 ⚠️ INC-47'S OWN FINDING, APPLIED TO THIS FIX — the third pressure

`INC-47` records the class: **an `Action:` field that claims more than was done.** Hard rule 13 binds
`Fix:` to a commit and binds `Action:` to nothing.

| # | what must be true | probe | ⚠️ **EXPECTED, PRE-COMMITTED** |
|---|---|---|---|
| **B4-k** | **no `Action:` field in `INC-46`…`INC-50` claims more than its commits demonstrate** | for each of the five entries, extract every factual claim in `Action:` and check each against the tree and against the entry's own `Fix:` SHA | ⚠️ **NO POLARITY IS PRE-COMMITTED HERE, AND THAT IS DELIBERATE.** This is the one check whose answer cannot be guessed without reading the entries. What **is** pre-committed is the **rule of decision**: an `Action` claim of the form *"corrected at N sites"* is **overstated** unless all N are verifiable at HEAD; a claim naming a file is overstated unless that file changed in a commit of this session; and a claim in the past tense about another session's artefact is overstated unless that artefact carries it. **A single overstatement is a finding. Whether it is a BLOCKER depends on whether the overstated claim is load-bearing for RUN-1 or for a published number** — B-4 was a BLOCKER precisely because `Q-057` is *"BLOCKING RUN-1 if unread"*. |
| **B4-l** | `INC-49` (the declared STOP, `Q-080`) states a red that is **real and this session's own** | reproduce `make check-roles`, read the E5 output | **E5 FAILS naming `c4d4460`; E1/E2/E3 PASS** |

---

## 3. THE SIX SURVIVORS FROM REVIEW 2 — re-run, and each must now be KILLED

**Method, fixed here so it cannot be adjusted to the result.** Every mutant is applied in a **fresh
OS temp clone**, **committed inside that clone** (REVIEW 1 records that editing without committing
produced three false SURVIVORS, because the harness reads `git cat-file blob`), and
`whetstone_gate.__file__` is **printed** so the run is provably against the mutated copy. A mutant
is **KILLED** only if at least one test fails **that would not fail on the unmutated control in the
same clone**; the control is run first in every clone.

| finding | REVIEW 2's mutant | the mutation, restated from `OF-96`…`OF-102` alone | ⚠️ **EXPECTED, PRE-COMMITTED** |
|---|---|---|---|
| **OF-96** | **N11** | delete the `PureWindowsPath(root).is_absolute()` disjunct from `_is_relative_literal` | **KILLED** — and killed by a fixture with a **drive-letter root**, not by `root_literal == "logs"`. ⚠️ **Sub-criterion: run `N11` TOGETHER WITH a Windows-absolute root mutation.** If the property test dies only via `root_literal`, `OF-96` is **not** closed — that is exactly what REVIEW 2 measured. |
| **OF-97** | **N13** | add `"glob"` to `crashes_loudly`'s loud set | **KILLED** — by an assertion that a **glob** claim is **NOT** loud (the `False` direction of the field). |
| **OF-98** | **N8** | `len(live) != 1` → `len(live) < 1` | **KILLED** — and it can only be killed by a fixture with **two** reachable constructions; `0 < 1` still raises, so a zero-construction fixture cannot discriminate. ⚠️ **If it is killed, the killing test must construct two.** |
| **OF-100** | *(demonstrated, not numbered)* | make `_named_functions` disagree with Python's binding: shadow a module-level definition and check which one is analysed | **KILLED** — the derivation must report the **last** module-level definition (what Python binds). ⚠️ **`OF-100` is the only one of the six whose remedy could legitimately be a documented refusal instead** (refuse a source with a shadowed redefinition). **Either is acceptable; silence is not.** |
| **OF-101** | **N14** | `TABLE_NUMBER.fullmatch` → `.match` | **KILLED** — by a **singular-range** fixture (`Table 5-7`), because the plural `Tables 5-7` is rejected either way. |
| **OF-102** | **N6** | drop `figure.table == table` from `banking_rows`' key | **KILLED** — by an assertion on the dict's **size**, or by keying on `(table, row)`. ⚠️ **REVIEW 2 proved it EQUIVALENT TODAY.** So a survival here is **not automatically a finding**: it is a finding **unless** the fix has made the key non-colliding, in which case the mutant is genuinely equivalent and must be **proven** so by exhibit — a construction under which HEAD and the mutant differ, shown not to exist. **Pre-committed: equivalence claimed without an exhibit is treated as a SURVIVOR.** |

**`OF-99` and `OF-103` are NOT in this table and are not this chunk's.** `OF-99` is the
repository-wide superseded-string tripwire — `Q-064`'s named remedy, belonging to whichever chunk
owns the tripwires, and the prompt states Session A is closing it. `OF-103` is `140-145` vs
`139-146`, ruled a **labelling** matter by `Q-057`'s own correction note. **Neither is a reason to
fail C13**, and each is carried forward to `OPEN_FINDINGS.md` rather than closed here.

---

## 4. THE FIX'S OWN NEW CODE — minimum 8 mutants, no review has seen any of it

⚠️ **This is where REVIEW 3 of C6 found six survivors on exactly this shape of work.** The surface is
the **ten new tests** and the **branch-condition predicate**. Line numbers cannot be pre-committed
blind; the **shapes** can, and they are, so the mutant set cannot be chosen after seeing which ones
would pass.

| # | the shape | ⚠️ **EXPECTED, PRE-COMMITTED** |
|---|---|---|
| **N-1** | **delete each new test's strongest single assertion, one at a time** | the mutated file's own test **fails** in a way that shows the assertion was load-bearing; an assertion whose deletion changes nothing is **dead weight** and is a finding |
| **N-2** | **weaken each required-phrase check to a substring of itself** (e.g. require `"diagnos"` where the law says `"a cause that has been DIAGNOSED"`) | **KILLED.** A phrase check that passes on a prefix does not require the phrase. |
| **N-3** | **invert the source of truth**: make the phrase list a literal in the test instead of read from `CONTEXT.md` | **KILLED by P-B3-7** (the §8.5.1 ordering probe). If it survives, B3-i is unmet — **this is the same mutation as P-B3-7 from the other end, and both are run.** |
| **N-4** | **make the predicate in `src/` return its failure instead of refusing** (or: never consult it) | **KILLED** — otherwise J-2/J-4 fail and the Class B deviation bought nothing |
| **N-5** | **case-fold or whitespace-normalise the phrase comparison** | **KILLED or PROVEN EQUIVALENT.** A normalisation that is deliberate must be asserted. |
| **N-6** | **delete the `branch_b_condition` half of the assertion, keeping `branch_a_condition`** | **KILLED** — `Q-079`'s whole point is that Branch B's trigger must exist as a stated condition |
| **N-7** | **swap the two conditions' values** (A's string into B's key and vice versa) | **KILLED** — a test that asserts a phrase set without asserting *which key carries it* is half a test |
| **N-8** | **loosen the loader path**: read the YAML directly instead of through the loader | **KILLED** — hard rule 9; a value not read through the loader is not a configured value |
| **N-9** | **the six survivors' killing tests, mutated at their fixtures** — the drive-letter root, the glob claim, the two-construction source, the singular range | **KILLED.** ⚠️ **This is the check `INC-50` is about**: a test green by accident of its fixture. It has appeared **four** times in this repository and the prompt asks for a third instance to be looked for. |
| **N-10** | **the control** — unmutated, in the same fresh clone | ⚠️ **GREEN.** A mutation run whose control is red measures nothing. |

⚠️ **PRE-COMMITTED VERDICT RULE, so the count cannot be argued afterwards:** **any survivor on this
surface that is not proven equivalent by exhibit is a finding, and a survivor that defeats the
property the fix's own commit message claims is a BLOCKER.**

---

## 5. `INC-48` — the swept content

| # | what must be true | probe | ⚠️ **EXPECTED, PRE-COMMITTED** |
|---|---|---|---|
| **S-1** | `3605d31c`'s token row is **present exactly once** | `grep -c` on the row | **1** |
| **S-2** | its 41-line paragraph is **intact and complete** | compare against `3605d31c`'s own account of what it wrote | **complete; no truncation at either end** |
| **S-3** | **no counter collided** | check that no `Q-` or `OF-` number is used twice, and that `3605d31c`'s `OF-104`…`OF-114` and this session's allocation do not overlap | **no duplicate** |
| **S-4** | the sweep is **recorded, not repaired by rewriting history** | `e2b4778` still exists, unamended; `INC-48` exists | **both true** |

---

## 6. STANDING PROPERTIES — pre-committed, all measured by this session

| # | property | ⚠️ **EXPECTED, PRE-COMMITTED** |
|---|---|---|
| **T-1** | `make selftest` **RED on `camel_comparator.branch`, and FOR THAT REASON** | **RED**; the failure is `test_the_camel_branch_is_decided_before_any_camel_run` on `UndeterminedValue … 'camel_comparator.branch' … TODO_C13_RUN1` — **the loader refusing, not defaulting**. ⚠️ **A GREEN `make selftest` is a FAIL**: it would mean a session decided Branch A or B without RUN-1. |
| **T-2** | all three vendored trees at their pins, `git status --porcelain` **empty**, `git diff <pin>` **0 bytes** | **all three clean** |
| **T-3** | `git status --porcelain tests/goldens/` | **empty** |
| **T-4** | no `evals/` path in any C13 commit | **0** |
| **T-5** | `evals/usage/` empty → C13 spent nothing | **0 files** |
| **T-6** | `CONTEXT.md` still **v1.9** and byte-identical to the blob REVIEW 2 audited clean | **identical** |
| **T-7** | this review spends **zero** provider calls; CaMeL not run, not installed, not imported; **whether the model id is still served is NOT checked** | **zero** |
| **T-8** | `Q-080` / `INC-49` — `make test` is red at HEAD on `test_check_roles_exits_zero` | **RED, and it is Session A's task 1, NOT C13's.** Recorded, attributed by file, and **not a reason to fail C13**. |

---

## 7. THE PASS BAR, RESTATED FROM THE PROMPT AND FIXED HERE

**PASS requires ALL of:** both BLOCKERs closed by changes that **go red when reverted** (P-B3-4/5/6
and B4-a…B4-j); **all six survivors KILLED**; **every new-surface mutant killed or proven equivalent
by exhibit**; the scoped reimplementation **agreeing**; and **ZERO BLOCKERS**.

⚠️ **Two pressures are named here so that neither can operate unnoticed.** It is 02:30 with two days
left, and C13 has failed twice. **A PASS bought by the schedule is worthless.** **A third FAIL
manufactured to look rigorous is worse** — it is the same defect as a wall of PASSes, pointed the
other way. The rule this session binds itself to: **a third FAIL must rest on a defect that is
demonstrable by a probe in this file, with its polarity pre-committed here. A preference is not a
defect.**
