# REVIEW 13, attempt 2 — C13, THE CaMeL COMPARATOR

**Verdict: FAIL.** · Session `8c49c4d3` · 2026-09-01 · Review type **full**, re-review after
C13 FIX 1 (`fd8a67e9`)
**Phase-1 criteria seal:** `e2f8aabff92150a9b26c52c80cafd293738b154e`
**Personas:** evaluation-integrity (1) + code (2), `PROCESS.md` §5.3
**Tag `c13-pass`: NOT CUT.**

> **BOTH BLOCKERS FROM REVIEW 1 ARE CLOSED, AND THEY ARE CLOSED PROPERLY.** Every one of the
> seven polarities this session pre-committed before opening the fix came out where it was
> written down. `CONTEXT.md` v1.9 audits clean to the byte. Table 4's figures were re-derived
> from the paper by this session's own reader and **every one matches**. The ceiling is
> attributed **per table** and swapping it in either direction is a red test.
>
> ⚠️ **The FAIL is for two things nobody has looked at: an uncorrected Class-A string in a
> pre-registration artefact that `Q-064` names in terms, and a correction that three separate
> records say was made and was not.**

---

## 0. Verdict, and exactly what it turns on

| PASS condition (from the prompt) | result |
|---|---|
| both BLOCKERs closed by changes that go red when reverted | ✅ **B-1 and B-2 both closed**, 12 mutants, every polarity as pre-committed |
| every new-surface mutant killed or proven equivalent | ❌ **14 run: 10 killed, 4 survived**, and four are **non-equivalent by exhibit** |
| v1.9 audited clean | ✅ **clean** — 0 control bytes but LF, LF delta = numstat exactly, P1/P3 byte-identical, no section moved |
| Table 4 independently re-derived | ✅ **all six blocks reproduce exactly** from this session's own fetch |
| **zero BLOCKERs** | ❌ **TWO** |
| no published figure lacking table, appendix, base model, row and its ceiling | ✅ **29 of 29 complete**; the ceiling gate is a refusal and it fires |

**Neither BLOCKER is about a number, a figure, or `CONTEXT.md`.** Both are about a string nobody
re-read.

⚠️ **THIS IS NOT A JUDGEMENT ON THE FIX'S QUALITY.** The fix took a guard that was *anti-correlated*
with the property it was named for and made every one of five mutants land the right way round; it
replaced a test that was named for a renderer and called a helper with one that is bound three ways
and dies three ways; it published Table 4 in full **including the four blocks that do not help this
project**; and it found and declared two bugs in its own new code by rendering the artefact and
reading it. That is a high standard. The two BLOCKERs are what is left when the work is checked at
that standard.

---

## BLOCKER B-3 — `config/lanes.yaml`'s `branch_a_condition` STILL ENCODES THE UN-NARROWED BRANCH-B TRIGGER, in the artefact that will outrank `CONTEXT.md`, and nothing declares it

**Severity: BLOCKER.** **File:** `config/lanes.yaml:202`. **Owner:** the C13 FIX's own commit
`3c5ef93`, whose subject is *"Q-064 — the four surviving pre-v1.8 citation sites"*.

`Q-064` names **two** defects in the same `config/` block, and says so in a heading:

> ⚠️ **AND THE SAME KEY IS BEHIND `Q-057` TOO, WHICH IS THE HALF THAT IS EASY TO MISS.**
> `camel_comparator.branch_a_condition` reads *"the model id is still served AND the run completes
> inside the 90-minute box"*. v1.8 **narrowed Branch B's trigger** to *"a cause that has been
> DIAGNOSED"*, with *"it errored is not a cause, and a harness defect is never Branch B."* The
> `config/` pair still encodes the **un-narrowed** trigger — the one `Q-057` records as reachable by
> our own bug. **So a freeze taken now would lock in BOTH corrected facts in their uncorrected form,
> not one.**

**Measured at HEAD:**

```
config/lanes.yaml:202
  branch_a_condition: "the model id is still served AND the run completes inside the 90-minute box"
config/lanes.yaml:203
  branch_b_action: "ship as a citation of Table 2, Appendix B ('Full results tables'), the o3 High
                    block, banking column ... out of 949 attacks in total"     <-- CORRECTED
```

`git show 3c5ef93 -- config/lanes.yaml` changes **the comment and `branch_b_action` only**.
`branch_a_condition` is not in the diff. The session's own FINAL OUTPUT mentions it exactly once, at
line 315, and only as a **parse** check: *"config/lanes.yaml still parses; branch_a_condition and
branch_b_action still read through the loader."*

**Why this is a BLOCKER and not a LOW.** The fix's own commit message states the danger in its own
words — *"hard rule 4 says a FROZEN one OUTRANKS `CONTEXT.md`… the moment C14 cuts it, this stops
being a stale string and becomes the higher authority"* — and then closes one half of it. Branch B
is the negation of `branch_a_condition`; as written, the config binds the project to taking Branch B
whenever *"the run does not complete"*, with **no diagnosis requirement** — which is exactly what
`Q-057`'s ruling forbade, for a reason it stated in terms: *"a pre-registration whose negative branch
can be reached by our own bug measures nothing."* And `"the model id is still served"` is the very
phrasing the ruling warns is indistinguishable from a harness defect.

⚠️ **It is also undeclared.** `OPEN_FINDINGS.md` records `OF-62` as **PART-CLOSED — "four of five
sites; the fifth is Q-074"**, which counts only *citation* sites. A reader of that line believes one
docstring remains. **Nothing anywhere says `branch_a_condition` was left un-narrowed.**

**Owed:** narrow `branch_a_condition` to v1.9's language (or add a `branch_b_condition` carrying the
diagnosed-cause requirement) **before `prereg-v1`** — legal today, illegal tomorrow — or obtain an
architect ruling to freeze it as-is with the contradiction published. Raised here as **`Q-079`**.

---

## BLOCKER B-4 — `Q-057`'s fact 4 STILL CITES `:321`, and INC-39, the FIX's FINAL OUTPUT and REVIEW 1's remedy list all say it was corrected

**Severity: BLOCKER.** **Files:** `QUESTIONS.md` Q-057 fact 4 (line 4716); `INCIDENTS.md` INC-39's
**`Action`** field; `docs/sessions/c13-fix-1.txt:91`.

REVIEW 1's remedy named **five** sites: *"in `invocation.py`'s docstring,
`Run1Plan.same_working_directory`, pass 2's `purpose`, and `QUESTIONS.md` `Q-057`'s fact 4."*

**Four landed.** Verified: `:321` now survives in `src/` only as explicitly-labelled history
(*"Builds 1 and 2 cited `replay_privileged_llm.py:321` … **Both halves were wrong**"*), and the live
citation is generated by `live_log_path`. **The fifth did not.** At HEAD:

```
QUESTIONS.md:4716
  4. `replay_privileged_llm.py:321` reads
     `Path("logs") / pipeline_name / suite_name / user_task_id / (attack_name or "none")` — the
     stored logs of the earlier `+camel` pass — and `models.py:179` hands it the `+camel` name.
```

No correction note, no annotation, nothing. `git show` on all seven fix commits: `f17709c` is
**+214 / −0** on `QUESTIONS.md` and `ef4b8d5` is **+1 / −0`**; **no fix commit deletes a line from
Q-057.**

**And three records say otherwise:**

| record | what it says |
|---|---|
| `INCIDENTS.md` INC-39, **`Action`** | *"the citation is corrected … at all four first-party sites **and in `Q-057`'s fact 4**"* |
| `docs/sessions/c13-fix-1.txt:91` | *"THE CITATION, corrected at all four first-party sites … **and in Q-057's recorded fact 4**"* |
| `OPEN_FINDINGS.md` | B-1 recorded as closed |

**Why this is a BLOCKER.** The substance is one line number. The **class** is what makes it one.
`Q-057`'s own status reads **"BLOCKING RUN-1 if unread"**, `CLAUDE.md` §1 makes `QUESTIONS.md` item 6
of the mandatory read order for every session, and RUN-1 is a single-shot 90-minute box. So the
surviving text is **a false `file:line` about third-party code, pointing into a function with no
caller, in the document RUN-1 is directed to read** — which is B-1, verbatim, in the one place B-1
was supposed to have been fixed.

And hard rule 13 exists to make `INCIDENTS.md` trustworthy: *"the pressure runs **both** ways — to
under-report a failure that costs a fix session, and to **dramatise** one that reads well. An
invented incident has no commit."* ⚠️ **This is a third failure mode the format does not yet catch:
a real incident whose `Action` field claims more than was done.** In a submission whose thesis is
that other people's self-reports are unsound, that is the most expensive kind of small error.

**Owed, and deliberately narrow.** `Q-057` is a **historical record** of what `c2b7f419` found, so
the remedy is **not** a silent edit. Either (a) append a dated correction note to `Q-057` naming
`replay_task` 140–145 / read `:148` / called `:305` and stating that `:321` is unreachable, or
(b) restate INC-39's `Action` and the session record to say four of five, with the fifth declared.
**One or the other must happen; what may not stand is three records asserting a fifth correction
that does not exist.**

---

## 1. Phase 1 — the seal, moved rather than pretended

**`OF-80` is RULED and this review is the first to run under it.** The two sealed phases do not
survive a re-review in their original form: `STATUS.md`'s review-history column and `QUESTIONS.md`'s
rulings are both mandatory Phase-1 reading and both carry the prior findings. What the seal protects
is preserved by moving it — **Phase 1 is blind to the FIX, not to the FINDINGS.**

`docs/reviews/independent/c13_review2_criteria.md`, committed at **`e2f8aab`** before a single fix
artefact was opened, states for B-1, B-2 and every `OF-` item what must now be true, the exact probe,
and the expected result.

⚠️ **NOT OPENED BEFORE THAT COMMIT**, declared so the seal is checkable: the seven fix commits (no
`git show`, no `git diff`, no `git log -p`), `docs/sessions/c13-fix-1.txt`,
`src/whetstone_gate/camel_comparator/`, `tests/test_c13_camel_comparator.py`.
⚠️ **ONE PARTIAL LEAK, DECLARED IN THE FILE ITSELF:** a `grep -n "OF-7[1-9]"` run to locate rows
`OF-71`…`OF-79` returned, in its match lines, the **first line of eleven disposition bullets**, so
eleven headline verdicts were seen. No body text was read, and every criterion is written as *what
must be true*, never as *what was done*.
⚠️ **`CONTEXT.md` at v1.9 WAS read — the FILE, never the DIFF** — because the prompt's read order
mandates §4, §8.5, §8.5.1 and §8.5.2 and the blindness list does not name it.

### 1.1 Every pre-committed polarity, and whether it held

| pre-committed in `e2f8aab` | expected | measured | held? |
|---|---|---|---|
| **M15** delete the three dead helpers | **SURVIVE** | SURVIVED | ✅ |
| **M16-abs-posix** `Path("/var/logs")` | **KILLED** | KILLED | ✅ |
| **M16-abs-win** `Path("C:/logs")` | **KILLED** | KILLED | ✅ |
| **M16-resolve** `Path("logs").resolve()` | **KILLED** | KILLED | ✅ |
| **D1** delete refusal 1 alone | **RED alone** | 6 failed | ✅ |
| **D2** delete refusal 2 alone | **RED alone** | 6 failed | ✅ |
| **D3** delete refusal 3 alone | **RED alone** | 6 failed | ✅ |
| **C-ctl** the control | **MUST RENDER** | renders, 17,103 chars | ✅ |

**Eight for eight.** The criteria were written before the fix was seen, so this is a test and not a
description.

---

## 2. B-1, re-run by this session in a fresh OS temp directory

Full table and the workspace-isolation proof: `docs/reviews/mutants/c13_mutants_2.md`. Mutations were
**committed inside the temp copy** — REVIEW 1 records that editing without committing produced three
false SURVIVORS, because the harness reads `git cat-file blob`. Each was run twice, once with the pin
left alone and once with `camel_sha` repointed so the **property** is all that is measured.

```
                  pin left alone            repinned          PROPERTY tests that died
M15               5 failed, 82 passed       1 failed, 86      NONE            <-- SURVIVES
M16-abs-posix     6 failed, 81 passed       2 failed, 85      1
M16-abs-win       6 failed, 81 passed       2 failed, 85      1
M16-resolve      10 failed, 77 passed       6 failed, 81      2
M16-dunder-file  10 failed, 77 passed       6 failed, 81      2     (REVIEW 1's own M16 form)
M17              10 failed, 77 passed       6 failed, 81      2
M17-glob          7 failed, 80 passed       3 failed, 84      2
```

⚠️ **The polarity is the right way round now.** REVIEW 1 measured M15 killed and M16/M17 surviving.

### 2.1 Both M16 forms, and the two-rule check probed directly

The prompt asks whether `is_relative` really is evaluated under POSIX **and** Windows rules. Probed
at the function, not inferred from a kill:

```
'/var/logs'   PurePosix=True   PureWindows=False  -> _is_relative_literal=False
'C:/logs'     PurePosix=False  PureWindows=True   -> _is_relative_literal=False
'logs'        PurePosix=False  PureWindows=False  -> _is_relative_literal=True
```

**The code does evaluate both**, and each absolute flavour is caught by exactly one rule — so the
claim is true and the check is not vacuous. ⚠️ **But only one half is pinned by a test** (see M-A):
running **N11 + M16-abs-win together**, the property test still dies, because the end-to-end kill
comes from `claim.root_literal == "logs"` and not from `is_relative`.

### 2.2 The corrected failure mode, verified independently

Traced mechanically over the blob rather than accepted from the fix:

* `replay_task` spans **129–238**; its only `Try` is **185–198**, catching
  `SecurityPolicyDeniedError`; **line 148 is not inside it**.
* `PrivilegedLLMReplayer.query` spans **287–315** and contains **zero** `Try` blocks.
* AgentDojo's `run_task_with_pipeline` wraps `agent_pipeline.query(...)` in
  `except AbortAgentError` **only**.

→ **unhandled `FileNotFoundError`; it crashes loudly.** ✅ **RUN-1 can act on that sentence.**

---

## 3. B-2 — each refusal deleted separately, and the control

```
D1     delete assert_provenance(HEADLINE_FIGURES)        ->  6 failed
D2     delete assert_provenance(CITED_TABLE_FIGURES)     ->  6 failed
D3     delete assert_provenance(TABLE_4_BANKING_FIGURES) ->  6 failed
D-all  delete all three                                  -> 18 failed
C-ctl  CONTROL, unmutated                                -> RENDERS: 17,103 chars / 199 lines,
                                                            29 figures guarded, 0 failing
```

Every deletion dies **on its own**, and the killing test **calls `render_branch_b`** — the precise
defect INC-40 records (a test named for the renderer that called only the helper). And the control
proves the gate is not merely a refusal machine: **a gate that refuses everything is not a gate.**

---

## 4. `CONTEXT.md` v1.9, audited — a FIX session amended the law

| check | result |
|---|---|
| **control bytes, counted as BYTES, whole file, before and after** | v1.8 **215,473 B** · LF 2,339 · **CR 0 · TAB 0 · 0x08 0 · no other `<0x20` or `0x7f`**<br>v1.9 **224,645 B** · LF 2,361 · **CR 0 · TAB 0 · 0x08 0 · none**<br>HEAD blob **identical** to v1.9 |
| **LF delta = numstat insertions − deletions** | numstat **+29 / −7 = 22**; LF **2,361 − 2,339 = 22**. ✅ **exact** |
| **P1 and P3 byte-identical to v1.8** | ✅ P1 **282 bytes**, P3 **283 bytes**, both unchanged byte for byte |
| **no section moved** | ✅ **37 headings before, 37 after, sequence identical** |
| **the hunks** | five: title, Version line, Amended list, **two Change-log rows** (v1.8's missing row + v1.9), and §8.5.2's P2. **Exactly the sanctioned edits.** |
| **every §8.5 parser re-runs; every anchor resolves exactly once** | ✅ all 8 anchors of `claims.spec_line_references`; `spec_interpreter_size` → `(100476, 2716)`; `spec_deny_by_default_string`; `spec_model_id` → `gemini-2.0-flash-lite-001`; `spec_max_tokens` → `8192`; `spec_timebox_minutes` → `90`; `branch_b_reason`; `parse_predictions` → **P1, P2, P3** |

**v1.9 is clean.** INC-13's class (a raw `0x08` that sat in this file for two days) does not recur.

---

## 5. Table 4, re-derived by this session from the paper

**Fetched by this session, not accepted from anybody:**

| | |
|---|---|
| URL | `https://arxiv.org/html/2503.18813v2` |
| status | **HTTP 200** |
| fetched | **2026-09-01T17:41:00Z** |
| bytes | **2,554,718** |
| **SHA-256** | **`b5cd7970e905f1504439c3eddb3855ab18d951d10bf806ec2f5f3baa02ca8a51`** |

Parsed with this session's own reader (`independent/c13_review2_paper_reader.py`), which resolves
each table's appendix from the `<h2 class="ltx_title_appendix">` of its enclosing `<section>` — from
the document structure, never from anybody's say-so.

**Table 4 — `A2.T4`, resolved to Appendix B, *"Full results tables"*, caption *"Number of successful
attacks."*, `banking` column, ALL SIX blocks:**

| base model | `CaMeL (no policies)` | `CaMeL` | agrees with v1.9? |
|---|---|---|---|
| `Claude 4 Sonnet` | **0 ± 0.0** | **0 ± 0.0** | ✅ |
| `Claude 4 Sonnet*` | **0 ± 0.0** | **0 ± 0.0** | ✅ |
| `Gemini 2.5 Flash` | **0 ± 0.0** | **0 ± 0.0** | ✅ |
| `Gemini 2.5 Pro` | **0 ± 0.0** | **0 ± 0.0** | ✅ |
| `o3 High` | **1 ± 0.0** | **0 ± 0.0** | ✅ |
| `o4 Mini High` | **1 ± 0.0** | ⚠️ **1 ± 0.0** | ✅ |

**The two claims P2 now rests on, checked:**
✅ **BOTH Gemini models record 0 for `CaMeL (no policies)` on banking.**
✅ **`o4 Mini High` records 1 for `CaMeL` ITSELF.**
**→ v1.9 is right. This is not a BLOCKER.**

Also re-derived and matching: **Table 2** (`A2.T2`, Appendix B, `o3 High`, banking — Native
**62.5 % ± 23.7**, CaMeL **81.2 % ± 19.1**, Difference **+18.8 % ± 4.6**); **Table 5** (Appendix C —
undefended **81.25 % ± 19.12** vs CaMeL **75.00 % ± 21.22**); **Table 6** (undefended
**84.03 % ± 5.98** vs CaMeL **70.83 % ± 7.42**); **Table 7** (Appendix C — `CaMeL` **0**,
`CaMeL (no policies)` **1** on Banking). Tables 5–7 all resolve to **Appendix C, "Baseline
results"**; Tables 2 and 4 to **Appendix B**.

⚠️ **And "exactly two of seven" is DERIVED, not asserted.** `p2_holds_for`, run over the carried
figures: `o3 High` **True**, Table 7 / `Claude 3.5 Sonnet` **True**, the other five **False**.
Matches this session's own extraction exactly.

---

## 6. The ceiling attribution, PER TABLE

| check | result |
|---|---|
| `949` occurrences | **4 raw substring hits in the HTML, in exactly 2 captions.** Figure 11's caption renders it once but LaTeXML emits the math three times (alt + presentation). ⚠️ The prompt's *"exactly twice"* is right **as captions**; as bytes it is four, and that distinction is recorded rather than smoothed over. |
| **Figure 9's caption** | *"…the number of successful attacks (out of **949** attacks in total)…"* and *"**The full results are presented in Table 4 and Table 3**."* → **Table 4's ceiling** ✅ |
| **Figure 11's caption** | *"The total number of attacks is **949** and the y axis is symlog scale"*; sub-caption **(a)** *"Utility, full results in **Table 5**"*, sub-caption **(b)** *"Number of successful attacks, full results in **Table 7**"* → **Table 7's ceiling** ✅ |
| the code | `_t4(...)` → `CEILING_SOURCE_F9`; `_T7` → `CEILING_SOURCE_F11`. **Correct per table.** |
| ⚠️ **is it asserted PER TABLE or once?** | **PER TABLE, proven by mutation.** **N3** (Table 4's ceiling → Figure 11) **KILLED**; **N4** (Table 7's ceiling → Figure 9) **KILLED**. Both die on `test_every_published_COUNT_carries_its_ceiling_and_the_ceilings_source` and `test_the_branch_b_artefact_regenerates_byte_for_byte`. |

**The fix's claim that attributing Table 4's ceiling to Figure 11 would be "Q-058's own defect one
level smaller" is correct, and it is guarded in both directions.**

---

## 7. Q-074 — the fifth site, and the repository-wide grep as a number

**`grep -rn -E "Tables? 5[-–—]7"`, whole repository, excluding `.git`, `.venv`, `vendor`,
`__pycache__`: **66 hits**.** Every one classified:

| classification | count | where |
|---|---|---|
| ⚠️ **LIVE TEXT — asserts the superseded citation as current** | **1** | `tests/test_lanes_operator_placeholders.py:141` |
| **FIXED** — now states what Tables 5–7 actually are, or cites Table 2 instead | **6** | `config/lanes.yaml` ×2, `QUESTIONS.md:4932`, `STATUS.md:7`, and 2 in `branch_b.py`'s corrected prose |
| **GUARD / FIXTURE** — the string as the shape the code *refuses* | **9** | `branch_b.py` ×4 (error messages, docstrings), `tests/test_c13_camel_comparator.py` ×7 *(overlaps counted once each)* |
| **HISTORICAL RECORD** — append-only journals, session reports, prior reviews, verbatim rulings | **50** | `docs/sessions/` ×32, `docs/reviews/` ×8, `PROGRESS.md` ×5, `QUESTIONS.md` ×2, `STATUS.md` ×2, `docs/reviews/mutants/` ×2 (approx. split; all append-only) |

✅ **`tests/test_lanes_operator_placeholders.py:141` is still there and it is now the ONLY live-text
site.** Confirmed at HEAD, and confirmed **read**: `make selftest` prints it in full —

```
    ! **Branch B is published as a result, not hidden as a failure** - the comparator
    ships as a citation of Tables 5-7 of arXiv 2503.18813v2 with the `CONTEXT.md` S8.5.1
    reason verbatim. ...
>       assert problem is None, problem
```

⚠️ **Whose it is, stated plainly: NOT C13's.** It is outside the FIX's fence (*"NOT: … any other test
file"*), the FIX **stopped on it and declared it** as `Q-074` rather than working around it, which is
correct conduct under hard rule 1. **It is the repository's, and it belongs to whichever session's
fence next includes that file** — `C14` is the natural place, since C14 already touches the freeze.
**It is not a reason to fail C13** and it is not counted as one.

### 7.1 ⚠️ Q-064's ACTUAL REMEDY DOES NOT EXIST

`Q-064` names it and `Q-074` repeats it: *"A grep for the superseded string, run as a test, would
have caught all four in one line."* **It is still not built.** `tests/test_repo_invariants.py`
carries repository-wide scans for CRLF, secret-shaped strings, forged session tokens, the
`gates/`↔`scorer/` module graph, undetermined config values and hardcoded spec values — and **nothing
for a superseded citation**. Searched: no occurrence of `superseded` anywhere under `tests/`, `src/`
or the `Makefile`.

**The class has now bitten twice and no mechanism knows a citation has copies.** Recorded as `OF-99`,
and it belongs to whichever chunk owns the repository-wide tripwires, not to C13.

---

## 8. Q-073 — was the stop right? **YES.**

The three instructions were read as written and they **genuinely collide**:

| # | instruction | verified |
|---|---|---|
| 1 | the FIX's scope fence, labelled *(hard)*: **`CONTEXT.md` (TASK 2 ONLY)**, TASK 2 enumerating its edits and saying *"P1 AND P3 ARE NOT TOUCHED"* | ✅ recorded in the FIX's own FINAL OUTPUT at lines 463–464 — **and obeyed**: this review's §4 confirms P1 and P3 are byte-identical |
| 2 | `Q-058`'s ruling: *"S4 is CLEAN and is not touched **except as TASK 1c specifies**"* | ✅ verbatim in `QUESTIONS.md`; **TASK 1c was C13 BUILD 2's**, and it is spent — `2b376ee` made the §4 AgentDojo edit in v1.8. What remains is *"S4 is CLEAN and is not touched."* |
| 3 | `OF-77`'s own status cell, written by the review that raised it | ✅ `OPEN_FINDINGS.md:633`, verbatim: **"OPEN — for C19, not for the C13 FIX"** |

Against those three, **one line of the same prompt** (TASK 4) orders the §4 edit.

**That is a real collision, not an excuse.** A fence drawn to the sentence, a ruling, and the
finding's own self-assignment all say the same thing; one line says the opposite. A session that
resolved that in its own favour would be choosing which of its instructions to obey.

⚠️ **And the evidence that it is not work-avoidance is in `Q-073` itself: it writes out the exact
one-line replacement**, with the four provenance fields, so landing it is an edit and not a research
task. **A session dodging work does not do the research and then decline to paste it.**
**The stop was right. `OF-77` stays open, correctly, for C19.**

---

## 9. Regressions and standing properties — all measured by this session

| property | measured |
|---|---|
| `make selftest` **RED on `camel_comparator.branch`, and FOR THAT REASON** | ✅ **1 failed, 1 passed, 707 deselected**; the sole failure is `test_the_camel_branch_is_decided_before_any_camel_run`, on `UndeterminedValue: lanes.yaml: 'camel_comparator.branch' … (sentinel 'TODO_C13_RUN1')` — the loader **refusing**, not defaulting |
| both vendored trees at their pins | ✅ CaMeL `f083b6b3…` · AgentDojo `928bbae8…` · both `git status --porcelain` **empty** · `git diff <pin>` **0 bytes** |
| `git status --porcelain tests/goldens/` | ✅ **empty** |
| no `evals/` path in any fix commit | ✅ **0** across all seven |
| C13 spent no tokens | ✅ **`evals/usage/` holds 0 files**; no usage ledger exists |
| **this review** spent no tokens | ✅ **zero provider calls.** CaMeL not run, not installed, not imported. ⚠️ **Whether the model id is still served was NOT checked** — Branch A's condition and RUN-1's alone |

### 9.1 Suite counts, MEASURED — and the two contaminations, separated

⚠️ **`make test` at HEAD is RED: 7 failed, 699 passed, 1 skipped, 2 deselected.** **NONE of it is
C13's.** Decomposed:

| failures | cause | whose |
|---|---|---|
| `test_check_roles_exits_zero`, `test_no_commit_carries_a_forged_or_reused_session_token` | `check_roles` **E1 FORGED/UNISSUED: {'8c49c4d3': ['e2f8aab']}` — **this review's own Phase-1 seal commit**, made before its token row was registered | ⚠️ **MINE.** Fixed in this session's journal commit, which appends token row 38. Declared, not hidden — it is `OF-89`'s class landing on a reviewer for the second consecutive review |
| `test_the_object_store_and_the_working_tree_agree`, `tests/test_c6_fix_probes.py::test_the_cap_is_INCLUSIVE_and_pinned_in_BOTH_directions`, `test_no_spec_value_is_hardcoded_in_implementation_source` | the **concurrent C6 FIX 2 session (`4e1c8a92`)**'s uncommitted in-flight edits to `src/whetstone_gate/attacker/context.py`, `…/estimate.py`, `tests/test_c6_attacker.py`, `tests/test_c6_fix_probes.py` — exactly the paths this session's prompt assigns to it | **not this review's and not C13's** |

**The C13 file alone, in this review's isolated temp clone: 87 passed, 0 failed.** That is the number
every mutation judgement above is taken against.

⚠️ **The failure count moved between two runs minutes apart** (7 → 5 visible `FAILED` lines) because
a concurrent session is editing the tree while it is measured. **Both figures are stated rather than
the more convenient one.**

---

## 10. The declared sequencing slip — verified, and it checks out

The FIX declared that `CONTEXT.md` was edited in the working tree **before** the ruling was written,
and that the **commit order** is ruling-then-amendment. From `git log`:

```
1  ef4b8d5  20:18:59  INC-39 and INC-40 WRITTEN FIRST, before a line of code changes
2  f4a38b7  20:33:51  the B-1 / B-2 code fix
3  f17709c  20:39:41  the Q-058 (Table 4) RULING recorded VERBATIM
4  041abe4  20:40:06  CONTEXT.md v1.9                                <-- 25 s after the ruling
5  5d13fcd  20:45:47  Table 4 published in full
6  3c5ef93  20:49:14  Q-064's citation sites
7  4a75bf7  20:53:12  end-of-session duties
```

✅ **The audit trail reads correctly.** Hard rule 13's *entry before the code* holds (1 before 2), and
hard rule 5's *ruling before the amendment it authorises* holds (3 before 4 and 5). The code fix at
#2 precedes the ruling at #3, but it is governed by REVIEW 1's findings and not by that ruling, so
the ordering is right with respect to what each authorises. **A declared slip is evidence of honesty
only if it checks out, and this one does.**

---

## 11. MEDIUM findings

**M-A · The Windows half of `_is_relative_literal` is pinned by NO test.** (`invocation.py:354-363`;
mutant **N11**, SURVIVED.) Deleting `PureWindowsPath(root).is_absolute()` leaves the whole suite
green. **Non-equivalent by exhibit:** `C:/logs` and `C:\logs` both flip `is_relative` from `False` to
`True`. The fixture in `test_the_live_log_path_is_located_by_ast_and_proved_reachable` fires only a
POSIX-absolute form (`Path("/var/logs")`) and a `.resolve()` form. ⚠️ **The end-to-end kill of
M16-abs-win comes from `claim.root_literal == "logs"`, not from `is_relative`** — proven by running
N11 + M16-abs-win together, where the property test still dies. So the code's claim is true and the
suite cannot see half of it. **This is B-2's shape one level smaller, inside the code written to
close B-2.**

**M-B · `crashes_loudly`'s whole discrimination is pinned by no test.** (`invocation.py:319-326`;
mutant **N13**, SURVIVED.) Adding `"glob"` to the loud set inverts INC-39's central distinction and
nothing fails. Non-equivalent by exhibit (`read_call='glob'`: `False` → `True`). M17-glob dies on
`claim.read_call == "read_text"`, so the field RUN-1's guidance is generated from is never asserted
in its **False** direction. **Remedy: one assertion that a glob claim is not loud.**

**M-C · The *"exactly one reachable"* refusal weakens to *"at least one"* undetected.**
(`invocation.py:502`; mutant **N8**, SURVIVED.) Non-equivalent by exhibit: on a source with **two**
reachable constructions HEAD refuses and the mutant silently takes `sorted(live)[0]`. Nothing
constructs that state — the fixture's M17 case has **zero**, and `0 < 1` still raises. That refusal
is the sentence INC-39's remedy rests on.

**M-D · `_named_functions` keeps the FIRST module-level definition where Python keeps the LAST —
and the last method.** (`invocation.py:425-435`.) `setdefault` for module functions, `[…] =` for
methods: the two halves disagree with each other, and the module half disagrees with the
interpreter. Demonstrated on a shadowed redefinition: the derivation reports `root_literal='logs'`,
`is_relative=True` while the definition Python actually binds uses `/var/logs`. **Latent, not live**
— CaMeL has no shadowed redefinition at the pin — but it is *analysing code the run does not
execute*, which is the sentence INC-39 was written about. **This is the quiet-collapse class the
prompt asked to be swept for, and it is the only instance found beyond the two the fix reported.**

**M-E · The span the records cite and the span the artefact generates differ.** INC-39, the FIX's
FINAL OUTPUT and REVIEW 1 all say **139–146**; `live_log_path_from_source` derives **140–145** (the
expression, not the assignment statement) and `citation()` emits `…:140-145`. **`140-145` appears
nowhere in the repository as text** and `139-146` appears nowhere in `src/`, `tests/` or `config/`,
so nothing is *wrong* — but a reader comparing the incident record to the artefact finds two spans
for one construction, neither labelled statement-vs-expression.

---

## 12. LOW findings

**L-A · `fullmatch` is load-bearing and pinned by no test.** (`branch_b.py:180`; mutant **N14**,
SURVIVED.) `fullmatch` → `match` accepts **`Table 5-7`** (singular) while still rejecting
**`Tables 5-7`** (plural) — which is the only range the parametrised fixture fires. REVIEW 1's M6
equivalence proof said in terms that *"the strength of the check is `fullmatch`, not the absence of
`s?`"*, and that strength is unasserted.

**L-B · `banking_rows`' table key is load-bearing only by tuple ordering.** (mutant **N6**,
SURVIVED, equivalent **today**.) `CaMeL` collides across Tables 5, 6 and 7 in `CITED_TABLE_FIGURES`;
last-wins picks Table 7 because Table 7's rows happen to be last. Append a table after it, or
reorder, and `p2_holds_for` silently reads another table's row. **The fix repaired exactly this class
in this exact function and the repair is one ordering away from being invisible again.**

**L-C · `Q-074`'s fifth site.** Confirmed present, confirmed the only live-text site, and confirmed
**printed in full by `make selftest`** — the most-read copy of the five. **Not C13's** (§7).

---

## 13. What the fix got right, recorded because a FAIL that lists only faults is not a review

* **Every polarity this review pre-committed came out where it was written down** — eight for eight,
  including the M16 form REVIEW 1 itself used and two extra forms it did not.
* **The guard is bound by structure, not by substring.** `live_log_path_from_source` finds the path
  by `ast` inside the function `PrivilegedLLMReplayer.query` can actually reach, proves the call site
  exists, and reports the dead helpers **as unreachable** rather than asserting they exist — so
  deleting them changes no verdict. That is precisely why M15 now survives.
* **The refusals are bound three ways and die three ways**, and the killing test calls the renderer.
  The control proves the gate still passes what it should.
* **Table 4 is published IN FULL, including the four base-model blocks that do not help this
  project** — the selection this submission exists to criticise, declined on its own artefact.
* **"Exactly two of seven" is computed from the carried figures**, so it cannot rot away from the
  numbers above it.
* **The ceiling is attributed per table**, and citing the easier caption is a red test in both
  directions.
* **`CONTEXT.md` v1.9 is byte-clean** and P1/P3 are untouched exactly as the fence required.
* **Two bugs in its own new code were found by rendering the artefact and reading it**, and reported
  rather than quietly repaired — including the `banking_rows` collapse that printed a Table 5 label
  on a Table 7 row.
* **`Q-073` and `Q-074` are stops, not dodges**, and `Q-073` writes out the replacement line it
  declined to land.

---

## 14. Artefacts

| path | what |
|---|---|
| `docs/reviews/independent/c13_review2_criteria.md` | the **Phase-1 seal** — acceptance criteria and pre-committed polarities, `e2f8aab` |
| `docs/reviews/independent/c13_review2_paper_reader.py` | this session's own arXiv reader; imports nothing from `src/` |
| `docs/reviews/independent/c13_review2_table_extraction.txt` | its committed output — Tables 2, 4, 5, 6, 7 |
| `docs/reviews/independent/c13_review2_audit_v19.py` | the `CONTEXT.md` v1.9 byte audit |
| `docs/reviews/independent/c13_review2_mutants_vendored.py` | the vendored-tree mutation driver |
| `docs/reviews/independent/c13_review2_mutants_firstparty.py` | the first-party mutation driver |
| `docs/reviews/mutants/c13_mutants_2.md` | **25 mutants** — 18 killed, 6 survived, 1 equivalent |

**Tag `c13-pass` is NOT cut.** A FAIL that is not in the repository did not happen; this one is.
