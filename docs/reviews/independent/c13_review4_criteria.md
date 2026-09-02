# C13 REVIEW 4 - PHASE 1 CRITERIA, SEALED BEFORE THE FIX WAS OPENED

**Session `7a1e6c84` - C13 REVIEW, attempt 4 - 2026-09-02**
**Token row registered BEFORE this seal: row 46, commit `2a86849`.**

This file is written under **OF-80's ruling**: *on a re-review, PHASE 1 IS BLIND TO THE FIX, NOT TO
THE FINDINGS.* It states, for every item C13 FIX 3 was asked to close and for every property this
review will mutate, **what must be true, the exact probe, and the expected result with its polarity
written down in advance.** Phase 2 then measures. A criterion whose polarity is decided after the
measurement is a description, not a test.

Everything below is ASCII. `S` means the section sign; `->` means "becomes".

---

## 0. WHAT WAS NOT OPENED, AND THE BOUNDARY DRAWN TIGHTER THAN THE RULING REQUIRED

**NOT opened before this file is committed:**

* C13 FIX 3's commits - **no `git show`, no `git diff`, no `git log -p`, no `git log --stat`** on any
  commit after `c09c385b`'s last. The only thing read from `git log` was the **subject line list**,
  which arrives unavoidably in `git log --oneline` at session start and is declared as leak **L-1**.
* `docs/sessions/c13-fix-3.txt` - **not opened.** It is open in the operator's editor; it was not
  read.
* `tests/test_c13_camel_comparator.py` - **not opened.**
* `src/whetstone_gate/camel_comparator/` - **not opened.**
* `docs/reviews/OPEN_FINDINGS.md` at HEAD - **not opened.** `OF-115`...`OF-119` are taken from
  `REVIEW_13_3.md` S10, which states all five in full. FIX 3's `Closed by` cells are a reading of
  the fix through a different file and are deferred to Phase 2.
* `PROGRESS.md`'s FIX 3 entry, `STATUS.md`'s C13 row, `INCIDENTS.md` INC-55 onward - **not opened.**

**AND THE BOUNDARY IS TIGHTER THAN OF-80 REQUIRES, in one place, named rather than left to be
inferred: NOTHING UNDER `src/` OR `tests/` WAS OPENED AT ALL** - not the config loader, not
`check_roles.py`, not any test file. The ruling only fences the fix's own surface. `docs/reviews/`'s
own Phase-1 rule is stricter (*"may not open ... anything under `src/` or `tests/` other than the
goldens"*) and where the two differ this session took the stricter one. The consequence is that the
`UndeterminedValue` refusal shape below is re-derived from `CLAUDE.md` hard rule 9 and from the two
verbatim tracebacks `REVIEW_13_3.md` prints, **not** from reading the loader.

### 0.1 THE LEAKS, DECLARED - the prompt discloses part of the fix and pretending otherwise would void the seal

| # | leak | what it discloses |
|---|---|---|
| **L-1** | `git log --oneline` at session start | FIX 3's commit **subjects**, including *"C13 FIX 3's OWN mutants found TWO survivors in its OWN new code, and this kills both"* (`73de008`). Bodies not read. |
| **L-2** | this session's prompt, item 3 | that FIX 3 self-generated mutants and names **SD-11**, **SD-13**, **SD-14**; and it describes SD-11's and SD-13's **mechanism**: *"the guard quoting every requirement rather than the one that failed, so `repr(required) in problems[0]` is satisfied for all four at once"* and *"keeping the OF-118 call and discarding its result, passing an AST call-site check while telling the operator nothing"*. ⚠️ **This is the largest leak and it is a substantial disclosure of the fix's internals** - it names an identifier (`repr(required)`), a data shape (`problems[0]`) and the existence of an **AST call-site check**. |
| **L-3** | this session's prompt, items 3 and 4 | that an `OF-118` **call** now exists (so a non-test caller was added), and that `OF-115`'s remedy and `OF-119`'s remedy were attempted. |
| **L-4** | `REVIEW_13_3.md` S13 | the checklist FIX 3 was handed, in its own words. This is the leak OF-80's ruling **intends** - blind to the fix, not to the findings. |
| **L-5** | `QUESTIONS.md` (mandatory read order item 6) | `Q-079`'s *"What landed under it"* names a FIX **2** test by name. Already known to REVIEW 3 and not a FIX 3 disclosure. |
| **L-6** | `INCIDENTS.md` INC-54, read for the token-row rule | the **heading** of INC-55 was visible in the same output. It describes **REVIEW 3's finding**, not FIX 3's remedy. Body not read. |
| **L-7** | `config/lanes.yaml` **was** read in Phase 1 | its `camel_comparator` block. ⚠️ **This adds no disclosure:** `REVIEW_13_3.md` S2 already quotes both branch conditions verbatim, and FIX 3's checklist (S13) touches `config/` nowhere. Declared because the seal is worth nothing if it is selective. |

**Every criterion below is written as *what must be true*, never as *what was done*.** Where a leak
makes the fact of a remedy visible (L-2, L-3), the criterion is deliberately **not** *"was it done"*
- that is already known - but *"does it do the thing it was for"*, which is the part only a review
can add. That is the same move `REVIEW_13_3.md` S1 made with B-4.

---

## 1. THE REQUIRED SET UNDER Q-082 - enumerated BEFORE any mutant is written

`Q-082` is ruled and recorded verbatim at `2a86849`:

> "THE GATE IS THE REQUIRED SET: at least one mutant per property or invariant the chunk owns,
> minimum eight (PROCESS.md S5.3). SURVIVORS BEYOND THAT SET ARE MEDIUM FINDINGS IN
> OPEN_FINDINGS.md AND DO NOT HOLD THE TAG."

⚠️ **The ruling's termination condition only works if the required set is fixed BEFORE the mutants
are generated.** A set enumerated afterwards is the same unbounded regress with an extra step. So it
is fixed here, in the seal, and Phase 2 may **add** members with an argument but may not remove one.

**The properties C13 OWNS.** Derived from `PROCESS.md` S12.1's C13 card and `CONTEXT.md` S8.5/S8.5.1/
S8.5.2, not from the code:

| # | property C13 owns | why it is C13's, argued |
|---|---|---|
| **OWN-1** | **RUN-1 is a TWO-PASS protocol**, pass 2 reading the `logs/` tree pass 1 wrote, from the same working directory | `Q-057`'s ruling; the card's *"the branch decision is made and recorded"* is unreachable without the right command |
| **OWN-2** | **Branch A's condition is IT RUNS** and carries no *"model id is still served"* clause | `Q-079`'s ruling, landed in `config/` by C13 FIX 2. C13 is the only chunk that reads this key |
| **OWN-3** | **Branch B's trigger is a STATED condition carrying ALL FOUR requirements** - diagnosed cause; "it errored is not a cause"; a harness defect is NEVER Branch B; recorded in `PROTOCOL.md` BEFORE the branch is selected | `CONTEXT.md` v1.9 S8.5.1, installed by `Q-057`'s ruling. **This is the property the FAIL was about** |
| **OWN-4** | **The LAW is asserted BEFORE `config/`** - the guard requires each phrase of `CONTEXT.md` S8.5.1 first, and of `config/` only because the law says so | `REVIEW_13_3.md` S2.2; hard rule 4's ordering made checkable |
| **OWN-5** | **The superseded trigger string is ABSENT** from `config/` | `Q-079`, `Q-057` |
| **OWN-6** | **`config/` is read through the loader's `require()`, so a sentinel is a REFUSAL, never a value** | `CLAUDE.md` hard rule 9: *"a missing value is a hard refusal, never a silent fallback"* |
| **OWN-7** | **The branch is UNDECIDED until RUN-1** - `camel_comparator.branch` is `TODO_C13_RUN1` and `make selftest` is RED on it, for that reason | the card; `CONTEXT.md` S15.4 single-shot |
| **OWN-8** | **Every published figure carries URL, date, digest, table/figure number, appendix, base model and row, and the renderer REFUSES one that does not** | `Q-058`'s ruling, in its own words |
| **OWN-9** | **The Branch-B citation is Table 2 / Appendix B / `o3 High` / banking, and NOT Tables 5-7**; Table 7 remains S8.5.2's P2 citation | `Q-058`, `Q-064`, the card |
| **OWN-10** | **The vendored CaMeL tree is UNMODIFIED at its pinned SHA** - the diff is empty and is committed as proof | the card, in terms |

**Ten owned properties, so the required set is TEN mutants minimum, not eight.** The floor in
`PROCESS.md` S5.3 is eight; the ruling's rule is one per owned property; ten is the larger and it
governs. Phase 2's mutant table will carry an `OWN-n` column and **every one of OWN-1..OWN-10 must
have at least one mutant against it.**

⚠️ **AND THE DETERMINATION THAT DECIDES THE VERDICT IS PRE-COMMITTED TOO.** For a survivor to carry
a FAIL under `Q-082` it must attack a property in the table above. A survivor that attacks
**something else** - a reviewer's convenience assertion, a message string, a property belonging to
C0/C6/C7 - is a MEDIUM in `OPEN_FINDINGS.md` and does **not** hold the tag. Phase 2 will state, for
each survivor, **which row of the table it attacks or that it attacks none**, with the argument.

---

## 2. PRE-COMMITTED POLARITIES - REVIEW 3's FIVE SURVIVORS

Each is re-run by this session **in a fresh OS temp clone**, the mutation **committed inside the
clone**, control first, `whetstone_gate.__file__` **printed**.

⚠️ **THE RESTORE METHOD IS PRE-COMMITTED, BECAUSE THE FAILURE DIRECTION IS FLATTERING.** C6 REVIEW
4's harness was defeated by restoring with `git checkout --` from a HEAD that already held the
mutation, and **a defeated restore reports every mutant as KILLED**. So: **restore by writing back
the ORIGINAL BYTES captured before the mutation**, and prove the restore by re-running the control
after it. **A run in which the post-restore control is not green is VOID and is reported as void,
not as a kill.**

| id | mutation (from `REVIEW_13_3.md` S5.2) | property attacked | **PRE-COMMITTED EXPECTATION** |
|---|---|---|---|
| **N-B** | `"on a cause that has been diagnosed"` -> `"cause"` | **OWN-3** | **KILLED** |
| **N-C** | `"a harness defect is never branch b"` -> `"harness"` | **OWN-3** | **KILLED** |
| **N-D** | `"protocol.md"` -> `"md"` | **OWN-3** | **KILLED** |
| **N-E** | delete one whole `BRANCH_B_REQUIREMENTS` entry | **OWN-3** | **KILLED** |
| **N-I2** | `lanes.require(...)` -> `lanes.data.get("camel_comparator", {}).get(key, "")` | **OWN-6** | **KILLED** |

⚠️ **N-C IS THE ONE TO CHECK HARDEST AND IT IS SAID HERE RATHER THAN AFTERWARDS.** Under N-C a
`branch_b_condition` reading *"a harness defect is SOMETIMES Branch B"* - **the direct inversion of
`Q-057`'s ruling** - passed the whole repository. Its kill must be demonstrated **on that exact
exhibit string**, not on a generically weakened one. **Expected: the suite goes RED with that string
in `config/`, and the failure names the harness-defect requirement specifically.**

**If any of the five survives: that is a survivor on OWN-3 or OWN-6, both of which are in the
required set, and it is a FAIL.** Written down now.

---

## 3. PRE-COMMITTED POLARITIES - THE DEFECT'S SHAPE, NOT ITS INSTANCES

`REVIEW_13_3.md` S5.3 found **one** defect behind four survivors: two assertions comparing the
predicate's **output** against its **own input list**, so neither can fail when that list changes.

| id | probe | **PRE-COMMITTED EXPECTATION** |
|---|---|---|
| **S-1** | is `len(BRANCH_B_REQUIREMENTS)` pinned against a **LITERAL** `4`, not against itself? | **YES**, and a literal is present |
| **S-2** | mutate that literal `4 -> 3` (or delete the entry and leave the literal at 4) | **RED** |
| **S-3** | is there a weak-form fixture **PER requirement**, each asserted **REJECTED**? | **YES, four of them** |
| **S-4** | delete each weak-form fixture in turn | **RED on each individually** - four separate reds, not one lump |
| **S-5** | does any assertion in the C13 test file still compare a predicate's output against the same module-level list that produced it? | **NO occurrence.** ⚠️ **Polarity pre-committed as NO. If Phase 2 finds one, that is the SHAPE surviving and it is reported as such even if every named instance is closed.** |
| **S-6** | the class repository-wide: how many times has "an assertion that cannot fail because both sides move together" now been recorded? | **SIX** if a new one is found here, **FIVE** if not. `REVIEW_13_3.md` says five to date. The count is a measurement, not a prediction, and is reported either way |

⚠️ **S-5 IS THE CRITERION THAT MATTERS AND ITS POLARITY IS THE RISKY ONE TO PRE-COMMIT.** A fix that
closes four named instances and leaves the shape is exactly what `INC-50` is about. Writing **NO**
here means Phase 2 has to look, in a file this session has not opened, and report what it finds
rather than what it hoped.

---

## 4. PRE-COMMITTED POLARITIES - FIX 3's OWN SELF-DIRECTED MUTANTS

Known only from leak **L-2**. Re-run by this session; not taken on report.

| id | what the prompt says it is | property attacked | **PRE-COMMITTED EXPECTATION** |
|---|---|---|---|
| **SD-11** | the guard quotes **every** requirement rather than the one that failed, so `repr(required) in problems[0]` is satisfied for all four at once | **OWN-3** | **KILLED** |
| **SD-13** | the `OF-118` call is kept and **its result discarded** - passes an AST call-site check while telling the operator nothing | **OWN-6** (the refusal must reach a human) | **KILLED** |
| **SD-14** | unnamed in the prompt | to be determined in Phase 2 | **KILLED** |

⚠️ **SD-13 CARRIES ITS OWN SEPARATE QUESTION AND THE ANSWER IS NOT PRE-COMMITTED.** *"Is `OF-118`
genuinely realised, or merely syntactically satisfied?"* A call whose result is discarded satisfies
*"has a non-test caller"* while delivering nothing. **No polarity is written here deliberately** -
the same move `REVIEW_13_3.md` S3.2 made for the `Action` audit - because pre-committing an answer
to a judgement question is pre-committing the judgement. **The RULE OF DECISION is pre-committed
instead, and Phase 2 is bound by it:**

> **OF-118 is GENUINELY REALISED only if all three hold:** (a) `branch_conditions_are_stale` (or its
> successor) is reachable from outside the test suite - exported, and called by a non-test caller;
> (b) that caller **uses** the result - it changes what the program does or what it prints, and
> deleting the *use* while keeping the *call* goes RED; (c) there exists an input on which the
> non-test path **behaves differently** because the function returned a non-empty answer.
> **Anything less is MERELY SATISFIED, and it is reported in those words.**

---

## 5. PRE-COMMITTED POLARITIES - OF-115, OF-117, OF-119

| id | probe | **PRE-COMMITTED EXPECTATION** |
|---|---|---|
| **F-115a** | `grep -c "OF-104" tests/test_c13_camel_comparator.py` | **0** |
| **F-115b** | the docstring at the same site cites `OF-62` and/or `Q-079`, or no `OF-` number | **one of those two** |
| **F-115c** | `OF-104` at HEAD is still C6 REVIEW 3's finding (i.e. the collision was real) | **YES** |
| **F-117a** | with `branch_b_condition` set to a `TODO_` sentinel, the stale-check raises an `UndeterminedValue`-shaped **refusal** | **REFUSAL**, hard rule 9 |
| **F-117b** | an assertion exists that pins F-117a | **YES**, and deleting it is RED |
| **F-117c** | the sentinel is **never** returned as a string value on any path the guard reads | **never** |
| **F-119a** | the S8.5.1 window now ends at `"### 8.5.2"` | **YES** |
| **F-119b** | the window width, measured in characters | ⚠️ **~3,592 chars** - S8.5.1's own length as `REVIEW_13_3.md` S10.2 measured it. **Pre-committed as "materially narrower than 6,759, and within 10% of 3,592"** |
| **F-119c** | all four phrases still live inside the narrowed window | **YES** - otherwise the narrowing breaks the guard |

⚠️ **F-119b IS A NUMBER AND IT IS WRITTEN DOWN BEFORE IT IS MEASURED.** `INC-54` is exactly about a
figure that was derived and formatted as a measurement. This one is a **prediction**, labelled as a
prediction, and Phase 2 prints the measured value beside it whichever way it comes out.

---

## 6. PRE-COMMITTED POLARITIES - STANDING PROPERTIES

| id | property | **PRE-COMMITTED EXPECTATION** |
|---|---|---|
| **T-1** | `make selftest` RED on `camel_comparator.branch`, **and for that reason** | **RED**, sole failure `test_the_camel_branch_is_decided_before_any_camel_run`, on `UndeterminedValue ... (sentinel 'TODO_C13_RUN1')` |
| **T-2** | all three vendored pins clean - CaMeL `f083b6b3`, AgentDojo `928bbae8`, tau2 `a2c0247` | **all three `git status --porcelain` EMPTY, diffs 0 bytes** (**OWN-10**) |
| **T-3** | `git status --porcelain tests/goldens/` | **empty** |
| **T-4** | `CONTEXT.md` still **v1.9** and byte-identical to REVIEW 3's audit | **blob `8e820384afbb1de7de3892eb6b90a8e6dce1f378`, 224,645 bytes, LF 2,361, CR 0** |
| **T-5** | `make check-prereg` | **NOT-YET-FROZEN, exit 0**; `prereg-v1` does not resolve |
| **T-6** | `evals/` empty -> C13 spent nothing | **0 files under `evals/`** |
| **T-7** | `config/lanes.yaml` carries the diagnosis requirement in **BOTH** branch conditions | **YES in `branch_b_condition`.** ⚠️ **The prompt says "in BOTH branch conditions" and that is checked as written**; Phase 2 states what each key actually carries rather than asserting the prompt's phrasing |
| **T-8** | the law is asserted **before** the config | **YES** (**OWN-4**) |
| **T-9** | `Q-074`'s fifth site (`tests/test_lanes_operator_placeholders.py:141`, *"Tables 5-7"*) and `OF-99` | ⚠️ **NO POLARITY PRE-COMMITTED** - the prompt says Session A closed them and asks this session to verify. **Either way they were never C13's**, and that determination **is** pre-committed: whatever the state, it does not touch this verdict |
| **T-10** | this review spends **zero** provider calls; CaMeL is not run and the model id is **not** checked | **zero**; the model-id check is Branch A's condition and RUN-1's alone |

---

## 7. THE SCOPED REIMPLEMENTATION - what it must do, pre-committed

`docs/reviews/independent/c13_review4_reimpl.py`, committed in this same seal.

**Scope, per OF-80's second ruling:** the **changed surface** - the four `BRANCH_B_REQUIREMENTS`
phrases and the sentinel refusal path. Not the whole chunk; `REVIEW_13_2`'s and `REVIEW_13_3`'s
reimplementations stand and are not superseded.

**Constraints, asserted at run time by the file itself:**

* imports **nothing** from `src/`; asserts `whetstone_gate` is not in `sys.modules`;
* parses `config/lanes.yaml` with **its own** minimal reader, because the project's loader is `src/`;
* **derives the four requirements from `CONTEXT.md` S8.5.1 at run time**, never transcribing them, so
  its expectations move with the law rather than becoming a third copy;
* implements the sentinel refusal path **twice** - a `require`-shaped read that RAISES and a
  `get`-shaped read that returns the sentinel as a value - so N-I2's exhibit is reproducible without
  the project's loader.

**Pre-committed expectations:**

| id | | expected |
|---|---|---|
| **R-1** | the four requirements derived from the law | **exactly 4**: diagnosed-cause, it-errored-is-not-a-cause, harness-never-B, PROTOCOL.md-before-the-branch |
| **R-2** | HEAD's `branch_b_condition` against the predicate | **0 problems** |
| **R-3** | HEAD's `branch_a_condition` carries the superseded trigger | **NO** |
| **R-4** | the four **strong-form** vectors, one per requirement | **0 problems each** |
| **R-5** | the four **weak-form** vectors (`"cause"`, `"harness"`, `"md"`, and the SOMETIMES inversion) | ⚠️ **each flags exactly the ONE requirement it weakens - not four, not zero.** This is SD-11's shape, derived independently here |
| **R-6** | the requirement-dropped vector | **the predicate's own size check fails**, independently of the problem list |
| **R-7** | the sentinel vector through the `require`-shaped read | **RAISES**, message names the key and the sentinel |
| **R-8** | the same through the `get`-shaped read | **returns the sentinel as a value** - the exhibit N-I2 rests on |
| **R-9** | total vectors | **>= 20** (`docs/reviews/README.md`) |

⚠️ **R-5 IS THE INTERESTING PRE-COMMITMENT AND IT IS MADE BEFORE THE FIX IS SEEN.** Leak L-2 tells
this session that FIX 3 found a guard that quotes **every** requirement rather than the one that
failed. **R-5 says what the correct behaviour is, derived from the law rather than from the fix**,
and Phase 2 diffs the project's predicate against it. If the project's predicate names all four on a
single-phrase weakening, this file disagrees with it and that disagreement is a finding.

---

## 8. THE RULE OF DECISION FOR THE VERDICT - fixed here, before any measurement

1. **ZERO BLOCKERS is necessary but not sufficient.** REVIEW 3 returned FAIL with zero blockers.
2. **A survivor on a property in S1's table (OWN-1..OWN-10) is a FAIL**, even where the subject
   measures clean today. `Q-082`'s ruling, first sentence.
3. **A survivor outside that table is a MEDIUM in `OPEN_FINDINGS.md` and does NOT hold the tag.**
   `Q-082`'s ruling, third sentence. **Every survivor is reported either way.**
4. **If the required set is clean, that is a PASS and the tag is cut.** Written down now, before any
   mutant is run, so that a clean result is not talked into a fourth FAIL. C13 has failed three
   times and every fail was right; a manufactured fourth would be the same defect pointing the other
   way.
5. **The scoped reimplementation disagreeing with the project on any vector is a finding**, and
   whether it is a BLOCKER depends on whether the divergence changes a published value or a
   pre-registered condition.
6. **A defeated mutation harness voids its own run.** S2's restore rule. A void run is reported as
   void and re-done, never scored.

**Nothing below this line was written after Phase 2 began.** The seal is this file's commit SHA.
