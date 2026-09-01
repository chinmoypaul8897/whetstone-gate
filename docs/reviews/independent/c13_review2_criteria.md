# C13 REVIEW 2 — PHASE-1 ACCEPTANCE CRITERIA, WRITTEN BLIND TO THE FIX

**Session `8c49c4d3` · 2026-09-01 · C13 REVIEW, attempt 2 (re-review after C13 FIX 1 `fd8a67e9`)**

> **THE SEAL, AS REDEFINED FOR A RE-REVIEW.** `OF-80` is RULED. The two sealed phases do not
> survive a re-review in their original form. What the seal protects is preserved by moving it:
> **Phase 1 is blind to the FIX, not to the FINDINGS.** This file is that seal. It is written
> from `REVIEW_13_1.md`, `INCIDENTS.md` INC-39/INC-40, `QUESTIONS.md` Q-057/Q-058/Q-058 (Table
> 4)/Q-064/Q-065/Q-073/Q-074, `CONTEXT.md` §4/§8.5/§8.5.1/§8.5.2, `PROCESS.md` §5.2/§5.3/§9/§12.1
> and `docs/reviews/OPEN_FINDINGS.md` rows `OF-71`…`OF-79` — **and from nothing produced by the
> FIX.**

## What was NOT opened before this file was committed

Declared, so the seal is checkable and not merely asserted:

* the seven fix commits `ef4b8d5 f4a38b7 f17709c 041abe4 5d13fcd 3c5ef93 4a75bf7` — **no
  `git show`, no `git diff`, no `git log -p` against any of them**;
* `docs/sessions/c13-fix-1.txt`;
* `src/whetstone_gate/camel_comparator/` — **no file in that package**;
* `tests/test_c13_camel_comparator.py`;
* `docs/reviews/OPEN_FINDINGS.md` lines 660–780, the FIX's own disposition prose. ⚠️ **Partial
  leak, declared:** a `grep -n "OF-7[1-9]"` run to locate rows `OF-71`…`OF-79` returned, in its
  match lines, the FIRST LINE of eleven disposition bullets (`"OF-71 — CLOSED by f4a38b7"` and
  similar). Those eleven headline verdicts were therefore seen. **No body text was read**, and
  every criterion below is stated as *what must be true*, never as *what was done*. The leak
  changes what this session knows and not what it will accept — which is `OF-80`'s own remedy.

⚠️ **What WAS read, because the read order mandates it and the blindness list does not name it:**
`CONTEXT.md` at v1.9 (§4's rows, §8.5, §8.5.1, §8.5.2 in full) — the FILE, never the DIFF. The
version-line and P2 text are therefore known; the commit that produced them is not.

---

## 0. THE STANDARD THIS REVIEW WILL APPLY

PASS requires **all** of:

1. **B-1 and B-2 closed by changes that go red when reverted** — every mutant below lands on its
   pre-committed polarity.
2. **Every new-surface mutant killed or proven equivalent** — minimum 8 mutants aimed at code the
   FIX added, not at code REVIEW 1 already mutated.
3. **`CONTEXT.md` v1.9 audited clean** — control-byte scan, LF arithmetic, P1/P3 byte-identity,
   no section moved, every §8.5 parser anchor resolving exactly once.
4. **Table 4's figures independently re-derived** by this session's own fetch of the paper.
5. **ZERO BLOCKERS.**
6. **No published figure lacking table, appendix, base model, row and — where it is a count —
   its ceiling.**

Anything else is FAIL. Schedule pressure is not an input.

---

## 1. B-1 — THE DEAD-CODE CITATION

### 1.1 What must now be true

| # | Criterion |
|---|---|
| **B1-a** | Every first-party site that cites where pass 2 reads pass 1's logs names the **LIVE** construction — `replay_privileged_llm.py` **139–146**, read at **:148**, reached from `PrivilegedLLMReplayer.query` at **:305**. No first-party prose asserts `:321` (or `:341`) is the live path. The four sites REVIEW 1 named: `invocation.py`'s module docstring, `Run1Plan.same_working_directory`'s docstring, that field's **runtime value**, and pass 2's `Invocation.purpose`. Plus `QUESTIONS.md` Q-057 fact 4. |
| **B1-b** | The stated failure mode for a pass 2 started from the wrong working directory is an **unhandled `FileNotFoundError`** — NOT *"reads an empty tree and reports nothing rather than failing — a silent zero"*. |
| **B1-c** | The guard is **bound to the live path by structure, not by substring**: the log-path construction is located inside the function `PrivilegedLLMReplayer.query` actually calls, by `ast` (or an equivalent structural walk), and the existence of that call site is itself asserted. A guard that can be satisfied by text in an uncalled function fails this criterion. |
| **B1-d** | The relativity judgement is **not one-rule**. `PureWindowsPath("/var/logs").is_absolute()` is `False` and `PurePosixPath("C:/logs").is_absolute()` is `False`, so a check evaluated under one ruleset passes vacuously for absolute paths of the other flavour. A path absolute under **either** ruleset must be judged **not relative**. |
| **B1-e** | The plan's own prose is checked against the derivation, so a stale citation is a red test rather than a sentence nobody re-reads. |
| **B1-f** | **Independently established by this session, not accepted from the FIX:** the live path really does raise an unhandled `FileNotFoundError`. `PrivilegedLLMReplayer.query` has no `try`/`except` around the `replay_task` call, and AgentDojo's `run_task_with_pipeline` catches only `AbortAgentError`. |

### 1.2 The exact probes, and the PRE-COMMITTED expected results

Every mutation is applied to a **copy of the CaMeL tree in a fresh OS temp directory** and
**COMMITTED there** — REVIEW 1 records that editing without committing produced **three false
SURVIVORS**, because the harness reads `git cat-file blob HEAD:<path>` and never the working tree.
`whetstone_gate.__file__` is printed before any mutant runs, to prove the workspace is isolated.

| id | mutation | **EXPECTED, pre-committed** |
|---|---|---|
| **M15** | delete the three dead helpers `replay_user_task`, `replay_suite`, `replay_benchmark` from `src/camel/pipeline_elements/replay_privileged_llm.py` | ⚠️ **SURVIVE** — live behaviour is byte-identical, so a correctly bound guard must NOT fire |
| **M16-abs-posix** | the LIVE path literal `Path("logs")` → `Path("/var/logs")` — a **POSIX-absolute literal**, the form `PureWindowsPath` calls relative | ⚠️ **KILLED** |
| **M16-abs-win** | the LIVE path literal `Path("logs")` → `Path("C:/logs")` — a **Windows-absolute literal**, the form `PurePosixPath` calls relative | ⚠️ **KILLED** |
| **M16-resolve** | the LIVE path `Path("logs")` → `Path("logs").resolve()` — the same-cwd requirement destroyed with the literal still relative | ⚠️ **KILLED** |
| **M17** | the LIVE replayer stops reading pass 1's logs: `trace_path.read_text()` → `'{}'` | ⚠️ **KILLED** |

⚠️ **THE KILL CONVENTION, FIXED HERE SO IT CANNOT BE CHOSEN AFTERWARDS.** Any commit inside the
vendored copy moves it off its pin, so the vendor-integrity tests (`diff_against_pin == ""` and
siblings) are **expected to go red on every one of M15–M17** as collateral. They are **excluded
from the kill judgement**, which is taken over the tests that name the log-path / two-pass
property. **Both numbers are reported**: the full failure list, and the property-specific verdict.
An M15 whose *only* red tests are vendor-integrity tests **SURVIVES** for this purpose.

⚠️ **A SURVIVOR ON M16 (ANY FORM) OR M17 IS A BLOCKER. A KILL ON M15 IS A BLOCKER** — it would
mean the guard is still anti-correlated with the property, which is what B-1 was.

---

## 2. B-2 — THE UNBOUND GUARDRAIL

### 2.1 What must now be true

| # | Criterion |
|---|---|
| **B2-a** | `render_branch_b` **itself** refuses a figure with incomplete provenance. A test that calls only `assert_provenance` does not satisfy this — that is exactly the defect. |
| **B2-b** | **Each** `assert_provenance` call in `render_branch_b` is bound by its own cases, so deleting any ONE of them alone goes red. A single test that dies only when all are removed is not a binding. |
| **B2-c** | ⚠️ **THE CONTROL.** With every guarded tuple complete, `render_branch_b` **still renders**. A gate that refuses everything is not a gate, and a renderer that raises unconditionally would kill all three deletion mutants for the wrong reason. |

### 2.2 The exact probes, and the PRE-COMMITTED expected results

| id | mutation | **EXPECTED, pre-committed** |
|---|---|---|
| **D1** | delete the **1st** `assert_provenance(...)` call from `render_branch_b`, leaving the others | ⚠️ **RED — ≥1 test fails, and the failing test(s) call `render_branch_b`** |
| **D2** | delete the **2nd** call only | ⚠️ **RED, on its own** |
| **D3** | delete the **3rd** call only | ⚠️ **RED, on its own** |
| **D-all** | delete **all** calls | RED (strictly more failures than any single deletion) |
| **C-ctl** | ⚠️ **CONTROL — no mutation.** Call `render_branch_b()` on the unmutated tree with every tuple complete | ⚠️ **RENDERS — returns text, raises nothing.** The suite is green apart from the single standing `camel_comparator.branch` failure |

⚠️ **If `render_branch_b` has FEWER than three `assert_provenance` calls, the count is reported as
a number and each existing call is deleted separately.** The prompt and INC-40 both say three; the
criterion is *each one, separately*, whatever the count turns out to be.

⚠️ **ANY DELETION THAT LEAVES THE SUITE GREEN IS A BLOCKER — it is B-2, unclosed.**
⚠️ **A CONTROL THAT REFUSES IS A BLOCKER** — it makes the three kills meaningless.

---

## 3. `CONTEXT.md` v1.9 — A FIX SESSION AMENDED THE LAW

| # | Criterion | Expected |
|---|---|---|
| **V-a** | **Every byte** of `CONTEXT.md` scanned for control characters other than LF, **before and after**, **counted as BYTES** — `CR`, `TAB`, `0x08`, any `< 0x20`, `0x7f`. (INC-13 put a raw `0x08` in this file and it sat two days.) | **0** of every class except LF, at `041abe4^` and at HEAD |
| **V-b** | The LF delta equals `git diff --numstat`'s **insertions − deletions** for the amendment | exact equality; any mismatch is a line-ending or hidden-byte defect |
| **V-c** | **P1 and P3 are byte-identical to v1.8** and **no section moved** | P1/P3 unchanged byte for byte; every `^## `/`^### ` heading present in v1.8 still present, same order |
| **V-d** | **Every §8.5 parser re-run and every anchor resolving EXACTLY ONCE** | every anchor count `== 1`; the whole C13 test file green apart from the standing `camel_comparator.branch` red |
| **V-e** | The version line carries v1.9 and its ruling reference; the Change log gains **both** the v1.9 row and the missing v1.8 row (`OF-63`/`Q-065`) | both rows present, in the log's stated format |

---

## 4. TABLE 4 — RE-DERIVED BY THIS SESSION FROM THE PAPER

⚠️ **This session fetches the paper itself and parses it with its own reader.** Nothing is
accepted from `REVIEW_13_1.md`, from Q-058 (Table 4), or from the FIX. URL, fetch date and the
**SHA-256 of what was fetched** are recorded.

### 4.1 What must be true

| # | Criterion |
|---|---|
| **T4-a** | **All six** base-model blocks of Table 4's `banking` column are published — **including the four that do not help this project**. Publishing only the helpful rows is the selection defect this project exists to criticise. |
| **T4-b** | **Every figure checked against this session's own extraction**, cell by cell. |
| **T4-c** | The claim P2 now rests on holds: **BOTH** Gemini models record **0** for `CaMeL (no policies)` on banking, **and** `o4 Mini High` records **1** for `CaMeL` **itself**. ⚠️ **If either is wrong, v1.9 is wrong and that is a BLOCKER.** |
| **T4-d** | Every count carries its **ceiling**. |

### 4.2 The expectation this session will test against (from REVIEW 1 and Q-058 (Table 4) — to be CONFIRMED or CONTRADICTED, not assumed)

| base model | `CaMeL (no policies)` | `CaMeL` |
|---|---|---|
| `Claude 4 Sonnet` | 0 | 0 |
| `Claude 4 Sonnet*` | 0 | 0 |
| `Gemini 2.5 Flash` | 0 | 0 |
| `Gemini 2.5 Pro` | 0 | 0 |
| `o3 High` | 1 | 0 |
| `o4 Mini High` | 1 | **1** |
| *Table 7, Appendix C, `Claude 3.5 Sonnet`* | 1 | 0 |

---

## 5. THE CEILING ATTRIBUTION, **PER TABLE**

| # | Criterion | Expected |
|---|---|---|
| **CEIL-a** | `949` occurs **exactly twice** in the paper | count = **2**, measured by this session |
| **CEIL-b** | **Table 4's** ceiling is attributed to **Figure 9's** caption — whose own text names Table 4 and Table 3 | Figure 9, not Figure 11 |
| **CEIL-c** | **Table 7's** ceiling is attributed to **Figure 11's** caption — whose sub-captions tie it to Table 5 and Table 7 | Figure 11, not Figure 9 |
| **CEIL-d** | ⚠️ **A test asserts the attribution PER TABLE, not once.** A single global "the ceiling is 949" assertion satisfies neither B nor C and would be Q-058's own defect one level smaller. | per-table assertion present; a mutant that swaps the two attributions is **KILLED** |

---

## 6. Q-064 / Q-074 — THE CITATION'S COPIES

| # | Criterion | Expected |
|---|---|---|
| **CIT-a** | A **repository-wide grep** for the superseded string, run by this session, reported **as a number**, with **every hit listed and classified** as live text / historical record / fixed | a number, not a impression |
| **CIT-b** | `tests/test_lanes_operator_placeholders.py:141` still carries it, and is now the **ONLY** live-text site | confirmed |
| **CIT-c** | ⚠️ **Q-064'S ACTUAL REMEDY: a repository-wide tripwire TEST that greps for a superseded string.** If it does not exist, say so plainly — the class has bitten twice and no mechanism knows a citation has copies. | present, or reported absent |

⚠️ **`CIT-b`'s site is OUTSIDE the FIX's fence and is NOT a reason to fail C13.** It is judged as
an open finding against the repository, and whose it is is stated plainly.

---

## 7. Q-073 — WAS THE STOP RIGHT?

Read all three instructions and say whether they **genuinely** collide:

1. the FIX prompt's own scope fence — `CONTEXT.md` **TASK 2 ONLY**, enumerated to the sentence;
2. `Q-058`'s ruling — *"S4 is CLEAN and is not touched except as TASK 1c specifies"*, TASK 1c
   being C13 BUILD 2's and closed;
3. `OF-77`'s recorded status — *"OPEN — for C19, not for the C13 FIX"*.

**Criterion:** a session that stops on a real collision has succeeded; one that stops to avoid work
has not. The test is whether the three, read as written, can be satisfied simultaneously.

---

## 8. THE REMAINING `OF-` ITEMS THE FIX WAS ASKED TO CLOSE

| finding | what must now be true | probe | **EXPECTED** |
|---|---|---|---|
| **OF-71** (M-1) | the rendered proof carries the diff it was **given**, not `(empty)` unconditionally | **M1b** — delete the conditional at `vendor.py:211` | **KILLED** |
| **OF-72** (M-2) | P2 carries all four provenance fields **and** its ceiling; Table 4 published in full; the Gemini caveat reaches C18 | §3, §4, §5 above | as above |
| **OF-73** (M-3) | the suite version read is the one `main.py` loads (`v1_2`), **derived** — or `v1` is read with the reason stated and the predicates asserted identical | **M18** — change the version literal in `main.py`'s `get_suite(...)` in the vendored blob | **KILLED** if derived; SURVIVE is a finding |
| **OF-74** (L-1) | `banking_suite_exists` checks the version in play | inspection + M18 | version parameterised |
| **OF-75** (L-2) | the blank/non-string guard in `branch_is_undecided` is reachable and tested | **M12** — delete the guard | **KILLED** if closed; equivalence proof otherwise |
| **OF-76** (L-3) | Table 7's counts carry **949** | inspection + a ceiling-deletion mutant | ceiling present; mutant **KILLED** |
| **OF-77** | ⚠️ **NOT the FIX's** — `OF-77`'s own status assigns it to C19 | §7 | stays open, correctly |
| **OF-78, OF-79** | process/cosmetic; not C13's to close | — | carried |

---

## 9. NEW-SURFACE MUTANTS — MINIMUM 8, ON CODE NEVER REVIEWED

The FIX added `live_log_path_from_source`'s **reachability refusal**, `branch_value_problem`, the
`PublishedFigure` **ceiling gate**, and the **per-table attribution**. That code has never been
reviewed. At least eight mutants land on it, **not** on the surface REVIEW 1 already mutated.

⚠️ **THE QUIET-COLLAPSE CLASS, PRE-COMMITTED AS A SEARCH.** The FIX reports finding two bugs in
its own new code by rendering the output and reading it — `banking_rows` keyed on **base model
alone**, collapsing five suites to the last row, so the artefact printed a Table 5 label on a Table
7 row. **This review will enumerate every dict/mapping in the new code keyed on fewer fields than
uniquely identify a row** and report the list as a number, whether or not any is live.

---

## 10. REGRESSIONS AND STANDING PROPERTIES

| # | property | expected |
|---|---|---|
| **R-a** | `make selftest` **RED on `camel_comparator.branch`, and FOR THAT REASON** | exactly one failure, on the loader **refusing** an unresolved sentinel |
| **R-b** | both vendored trees at their pins, **empty status and empty diff** | `git status --porcelain` empty; `git diff <pin>` 0 bytes |
| **R-c** | `git status --porcelain tests/goldens/` | **empty** |
| **R-d** | no `evals/` path in any fix commit | 0 paths |
| **R-e** | C13 spent no tokens | no usage ledger written by any C13 session |
| **R-f** | ⚠️ **suite counts MEASURED BY THIS SESSION and stated** — this project's prompts have twice carried counts that were arithmetically impossible | numbers, from this session's own runs |

---

## 11. THE SEQUENCING SLIP

The FIX declared that `CONTEXT.md` was edited in the working tree **before** the ruling was
written, and that the **commit order** is ruling-then-amendment. **Criterion:** verify the commit
order from `git log` and say whether the audit trail reads correctly. A declared slip is evidence
of honesty **only if it checks out** — a declaration that does not match the log is worse than
none.

---

## 12. WHAT THIS SESSION WILL NOT DO

* **ZERO provider model calls.** CaMeL is not run, not installed, not imported.
* ⚠️ **Whether the model id is still served is NOT checked** — that is Branch A's condition and
  RUN-1's alone.
* HTTP GETs to `github.com` and `arxiv.org` are permitted and are **required** for §4 and §5.
* Nothing under `src/`, `tests/`, `CONTEXT.md`, `PROCESS.md`, `config/`, `vendor/`,
  `INCIDENTS.md` or `docs/reviews/REVIEW_13_1.md` is edited. **A review session fixes nothing.**
* The untracked `grep.exe.stackdump` at the repo root belongs to no session and **is not deleted**.

---

**Committed before the fix was opened. The commit SHA of this file is the seal.**
