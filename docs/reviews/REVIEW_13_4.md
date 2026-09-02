# REVIEW 13, attempt 4 — C13, THE CaMeL COMPARATOR

**Verdict: PASS.** · Session `7a1e6c84` · 2026-09-02 · Review type **full**, re-review after
C13 FIX 3 (`e9dd0346`)
**Phase-1 criteria seal:** `9e16d87b843e4d67d7e5242a8e47f298e6520fd5`
**Token row registered BEFORE the seal:** `2a86849` (row 46)
**Personas:** evaluation-integrity (1) + code (2), `PROCESS.md` §5.3
**Tag `c13-pass`: CUT.**

> **All five of REVIEW 3's survivors are KILLED**, each re-run in a fresh OS temp clone with
> the mutation committed inside it, restored by **writing back the original bytes**, and the
> control re-run green after every restore. **The SHAPE is removed, not only its instances** —
> `len(BRANCH_B_REQUIREMENTS) == 4` is pinned against a **literal**, there is a **weak-form
> fixture per requirement** each asserted rejected, and a scan of the whole C13 test file for
> the `INC-50`/`INC-55` shape returns **zero true instances**. **FIX 3's own three
> self-directed mutants (SD-11, SD-13, SD-14) are re-run here and all three are KILLED.**
> **OF-118 is GENUINELY REALISED**, judged against a rule of decision pre-committed in the
> seal. **Seventeen new-surface mutants, one or more per each of the ten properties C13 owns
> — sixteen KILLED, one survivor, and that survivor is NOT-OWNED on an argued determination.**
>
> ⚠️ **UNDER `Q-082` THAT IS A PASS, AND THE TAG IS CUT.** The required set is clean. Three
> MEDIUM and two LOW findings go to `OPEN_FINDINGS.md` as `OF-136`…`OF-140` and do not hold
> the tag — including one, `OF-139`, that is a finding **about this repository's review
> method** and not about C13 at all.

---

## 0. Verdict, and exactly what it turns on

| PASS condition (from the prompt) | result |
|---|---|
| the five survivors killed by changes that go red when reverted | ✅ **5 / 5 KILLED**, 0 VOID |
| the SHAPE removed, not just the instances | ✅ **removed**, and the file re-scanned for it |
| FIX 3's three self-found mutants killed | ✅ **3 / 3 KILLED**, re-run here |
| every REQUIRED-SET new-surface mutant killed or proven equivalent | ✅ **required set COMPLETE and CLEAN** — 10 owned properties, 17 mutants, 16 killed; the 1 survivor is **NOT-OWNED** (§6) |
| the scoped reimplementation agreeing | ⚠️ **22 / 24 sealed vectors agree; 2 differ only in the project being STRICTER; 3 Phase-2 discriminators DIVERGE** → `OF-136`, MEDIUM (§5) |
| **zero BLOCKERs** | ✅ **ZERO** |

**Every pre-committed polarity is listed in §2 with what it measured.** Thirty-six held, **two
did not hold as written** and both are reported as this review's own mis-prediction rather
than smoothed over.

⚠️ **THE STANDING INSTRUCTION CUTS BOTH WAYS AND THIS REVIEW WAS GIVEN BOTH HALVES.** *"Do
not pass because the project is behind schedule"* — and *"do not manufacture a fourth FAIL.
If the required set is clean, that is a PASS and you cut the tag."* The required set was
**enumerated and argued in the seal, before any mutant was written** (`Q-082`'s termination
condition is worthless otherwise), and it came out clean. The one survivor is examined at
length in §6 precisely because it would have been the cheapest available fourth FAIL.

---

## 1. Phase 1 — the seal, the boundary, and the seven declared leaks

**`OF-80`'s ruling: on a re-review, Phase 1 is blind to the FIX, not to the FINDINGS.**

`docs/reviews/independent/c13_review4_criteria.md`, committed at **`9e16d87`**, states the
ten properties C13 owns, the required set, ~40 criteria with polarities, the rule of decision
for `OF-118`, the restore rule, and the verdict rule — **before** FIX 3's commits,
`docs/sessions/c13-fix-3.txt`, `tests/test_c13_camel_comparator.py`,
`src/whetstone_gate/camel_comparator/` or `OPEN_FINDINGS.md` at HEAD was opened.

⚠️ **THE BOUNDARY WAS DRAWN TIGHTER THAN THE RULING REQUIRED, in one place, and named rather
than left to be inferred: NOTHING UNDER `src/` OR `tests/` WAS OPENED AT ALL.** The ruling
fences only the fix's own surface; `docs/reviews/README.md`'s own Phase-1 rule is stricter,
and where the two differ this session took the stricter one. **The consequence is stated in
the seal:** the `UndeterminedValue` refusal shape was re-derived from `CLAUDE.md` hard rule 9
and the two tracebacks `REVIEW_13_3.md` prints, not from reading the loader.

⚠️ **SEVEN LEAKS ARE DECLARED IN THE SEAL, AND `L-2` IS THE LARGEST THIS PROJECT HAS HAD TO
DECLARE.** The prompt does not merely name SD-11/SD-13/SD-14; it **describes their
mechanism**, naming an identifier (`repr(required)`), a data shape (`problems[0]`) and the
existence of an **AST call-site check**. Every criterion touched by that leak is written as
*"does it do the thing it was for"*, never *"was it done"* — which is already known.

⚠️ **AND THE ORDERING HELD, for the third consecutive review.** Row 46 is `2a86849`, the seal
is `9e16d87`, and `check-roles` E1 was never red on this session.

---

## 2. Every pre-committed polarity, and whether it held

| sealed in `9e16d87` | expected | measured | held? |
|---|---|---|---|
| **N-B, N-C, N-D, N-E** | KILLED | KILLED, 1 failed / 33 passed each | ✅ |
| **N-I2** | KILLED | KILLED, 1 failed / 34 passed | ✅ |
| **N-C on its own exhibit** (*"a harness defect is SOMETIMES Branch B"*) | RED, naming the harness requirement | RED, `assert len(problems) == 1` on that exact string | ✅ |
| **S-1** `len(BRANCH_B_REQUIREMENTS)` pinned against a LITERAL | YES | `assert len(...) == 4` at `:1173`, literal | ✅ |
| **S-2** mutate the literal / delete an entry | RED | N-E KILLED | ✅ |
| **S-3** a weak-form fixture per requirement, each REJECTED | YES, four | four, `:1177-1195`, each the **real** value with one phrase degraded | ✅ |
| **S-4** each weak form load-bearing individually | RED on each | N-B/N-C/N-D each die on their own fixture | ✅ |
| ⚠️ **S-5** no assertion still compares a predicate's output against the list that produced it | **NO occurrence** | **0 true instances**; 4 candidates from a deliberately over-broad scanner, all four judged and rejected (§4) | ✅ |
| **S-6** the class count repository-wide | 5 or 6 | **5** — no sixth instance found | ✅ (reported, not predicted) |
| **SD-11, SD-13, SD-14** | KILLED | KILLED | ✅ |
| **F-115a** `grep -c OF-104` in the C13 test file | **0** | ⚠️ **2** | ❌ **did NOT hold as written** — §7.1 |
| **F-115b** cites `OF-62` / `Q-079` | one of those | **both**, `OF-62` ×2, `Q-079` ×8 | ✅ |
| **F-117a/b/c** sentinel → `UndeterminedValue` refusal, pinned, never a value | REFUSAL | **1 item, `UndeterminedValue: … (sentinel 'TODO_C14_PENDING')`**; missing key → `MissingRequiredValue`; real config → 0 | ✅ |
| **F-119a** window ends at `### 8.5.2 ` | YES | YES, line 617 | ✅ |
| ⚠️ **F-119b** the window width | **~3,592 chars, within 10 %** | **3,646 — +1.5 %** | ✅ |
| **F-119c** all four phrases inside the narrowed window | YES | YES | ✅ |
| **T-1** `make selftest` RED on `camel_comparator.branch`, for that reason | RED | **1 failed, 1 passed, 784 deselected**; sole failure `test_the_camel_branch_is_decided_before_any_camel_run` on `UndeterminedValue … (sentinel 'TODO_C13_RUN1')` | ✅ |
| **T-2** three vendored pins clean | all clean | CaMeL `f083b6b3…` · AgentDojo `928bbae8…` · τ² `a2c02472…`; all `status` **empty**, all diffs **0 bytes** | ✅ |
| **T-3** `git status --porcelain tests/goldens/` | empty | **empty** | ✅ |
| **T-4** `CONTEXT.md` v1.9, byte-identical | blob `8e820384…` | **`8e820384afbb1de7de3892eb6b90a8e6dce1f378` — IDENTICAL**; 224,645 bytes, LF 2,361, CR 0, TAB 0 | ✅ |
| **T-5** `check-prereg` NOT-YET-FROZEN | NOT-YET | **NOT-YET-FROZEN**, exit 0; `git tag -l` = `c0-pass`…`c4-pass`; `prereg-v1` **does not resolve** | ✅ |
| **T-6** `evals/` empty | 0 files | **0** | ✅ |
| ⚠️ **T-7** the diagnosis requirement in **BOTH** branch conditions | *no polarity — state what each key carries* | **`branch_b_condition` YES; `branch_a_condition` NO** — §7.2 | ✅ (as sealed) |
| **T-8** the law asserted before the config | YES | YES, and **NS-6** proves it: amending `CONTEXT.md` **alone** goes RED **at the law** | ✅ |
| **T-9** `Q-074`'s fifth site / `OF-99` | *no polarity* | **CLOSED** by Session A's `ea3bd12`; and never C13's | ✅ (as sealed) |
| **T-10** zero provider calls; model id NOT checked | zero | **zero**; the model id was not checked | ✅ |
| **R-1** four requirements derived from the law | 4 | 4 | ✅ |
| **R-2/R-3** HEAD accepted, superseded trigger absent | 0 / NO | 0 / NO | ✅ |
| **R-4/R-5/R-6** vectors, one weakening → one problem | 24 / 24 | **24 / 24**, and 8 of 8 single-weakening vectors give exactly one problem | ✅ |
| **R-7/R-8** the two readers | RAISE / return-as-value | RAISE / `'TODO_C14_PENDING'` | ✅ |
| **R-9** ≥ 20 vectors | ≥ 20 | **24** sealed + 3 Phase-2 discriminators | ✅ |
| ⚠️ **the reimplementation AGREEING with the project** | *rule of decision pre-committed* | **22 / 24 agree; 3 discriminators DIVERGE** | ❌ **`OF-136`** — §5 |

**Thirty-six of thirty-eight held. The two that did not are `F-115a` and the reimplementation
agreement, and both are reported below rather than reframed.**

---

## 3. THE FIVE SURVIVORS — 5 / 5 KILLED, and how the harness was kept honest

Full table: [`mutants/c13_mutants_4.md`](mutants/c13_mutants_4.md) §1.

⚠️ **THE RESTORE METHOD, STATED BECAUSE THE FAILURE DIRECTION IS FLATTERING.** C6 REVIEW 4's
harness was defeated by restoring with `git checkout --` from a HEAD that already held the
mutation, and **a defeated restore reports every mutant as KILLED**. **This harness never
calls `git checkout --`.** It captures the target file's **original bytes** before mutating,
writes those bytes back afterwards, re-hashes to confirm, and **re-runs the full control**. A
run whose post-restore control is not green is printed **VOID** and is not scored.
**27 mutations, 29 control runs, every one `100 passed`, 0 VOID.**

⚠️ **AND THE OTHER FAILURE DIRECTION, WHICH THIS REVIEW HIT FIRST-HAND AND WHICH WOULD HAVE
REPORTED EVERY MUTANT AS *SURVIVED*.** `.venv/…/__editable__.whetstone_gate-0.1.0.pth` holds
one line — `C:\Users\chinm\whetstone-gate\src` — so a bare `python -m pytest` **inside a fresh
clone imports the real repository's package**, and because `config.repo_root()` is
`Path(__file__).resolve().parents[2]`, `repo_root()` follows it. **Measured in the clone before
the fix:**

```
PKG : C:\Users\chinm\whetstone-gate\src\whetstone_gate\__init__.py
ROOT: C:\Users\chinm\whetstone-gate
```

**The control still read `100 passed`, so nothing would have looked wrong.** Fixed with
`PYTHONPATH=<clone>/src`; the resolved paths are **printed at the head of every run** and the
driver **aborts** if the package under test is not the clone's. Recorded as **`OF-139`**,
because the knowledge that this is necessary lives in one previous reviewer's script and in
nothing else — `REVIEW_13_3`'s driver sets `PYTHONPATH`, and there is no guard, no `Makefile`
target and no line of `docs/reviews/README.md` that would have told a new one.

**And a NEGATIVE CONTROL, because a harness in which every mutant dies is not measuring
anything.** `NS-14` (`passes = [` → `passes = [] or [`) changes no behaviour and **must
survive**. It did.

| id | the mutation | result |
|---|---|---|
| **N-B** | requirement 1 phrase → `"cause"` | ✅ **KILLED** |
| **N-C** | requirement 3 phrase → `"harness"` | ✅ **KILLED**, on the SOMETIMES exhibit itself |
| **N-D** | requirement 4 phrase → `"md"` | ✅ **KILLED** |
| **N-E** | one whole `BRANCH_B_REQUIREMENTS` entry deleted | ✅ **KILLED**, by the literal `== 4` |
| **N-I2** | `lanes.require(…)` → `lanes.data.get(…, "")` | ✅ **KILLED**, by the sentinel refusal test |

⚠️ **N-C was checked hardest, as the prompt directed, and its kill is on the right exhibit.**
The fixture is the **real** `branch_b_condition` with `"a harness defect is NEVER Branch B"`
replaced by **`"a harness defect is SOMETIMES Branch B"`** — the direct inversion of
`Q-057`'s ruling, the string that passed the entire repository under REVIEW 3. Under N-C the
weakened phrase `"harness"` still occurs in that inverted string, so the guard raises **zero**
complaints and `assert len(problems) == 1` fires. **The kill is on the inversion, not on a
generically degraded neighbour.**

---

## 4. THE DEFECT'S SHAPE — removed, and the file re-scanned to say so

REVIEW 3 found **one** defect behind four survivors: two assertions comparing the predicate's
**output** against its **own input tuple**, so neither could fail when that tuple changed.

**Both are gone from live code.** Searched by their own text: `live=[]` for each, and each
survives only as **quoted text inside the explanatory comment at `:1152-1153`** that says why
it was removed — which is this project's convention, and the right one.

**What replaces them, and each part is load-bearing:**

* `assert len(invocation.BRANCH_B_REQUIREMENTS) == 4` — **against a literal.** N-E dies here.
* **four weak-form fixtures**, each the **real** `branch_b_condition` with exactly one
  requirement degraded, each asserted to produce **exactly one** complaint **quoting that
  requirement** — against a literal written in the test, never against `invocation`'s tuple.
* **the needle is asserted PRESENT before it is degraded** (`INC-50`'s mirror move), so a
  `.replace()` that matched nothing cannot leave a valid condition behind.
* **the undegraded value is asserted ACCEPTED** — the control without which four rejections
  are also what a guard that refuses everything looks like.
* and (FIX 3's own `SD-11`) the complaint must quote the failed requirement **and not the
  other three**.

⚠️ **`SD-11`'s new assertion is NOT VACUOUS, verified character by character rather than
assumed.** The guard's message ends with prose spelling all four requirements. If any matched
`repr(other)` the assertion would be satisfied by accident. It is not: `repr` requires the
quote characters, the prose spells every phrase **unquoted and in different case**
(`PROTOCOL.md`, `DIAGNOSED`, `Branch B`), and `'it errored' is not a cause` puts a **space**
between the closing quote and `is`.

### 4.1 ⚠️ The same shape, looked for ELSEWHERE in the file — the class has appeared FIVE times

Scanned with an AST walk over every `assert` in `tests/test_c13_camel_comparator.py`, looking
for an assertion whose expected side reads a module-level object of `invocation`/`branch_b`
that also produced the actual side. **Four candidates; all four judged and rejected:**

| line | the assertion | judged |
|---|---|---|
| `:2346`, `:2359` | `branch_b.p2_holds_for(branch_b.CITED_TABLE_FIGURES, "Table 7", …) is True` | ❌ not the shape — the constant is an **input**; the expected side is a **literal** |
| `:2283`, `:2289` | `banking_rows(reversed_figures, …) == banking_rows(figures, …)` | ❌ not the shape — a **metamorphic** assertion (`OF-102`'s remedy: keyed on the table, not saved by tuple order). It **can** fail, and a mutant that made ordering load-bearing would fail it |

**And one near-instance the scanner did not flag, judged by hand and named rather than
skipped:** `:1146`, `assert any(invocation.SUPERSEDED_BRANCH_TRIGGER in problem for problem in
stale)` — the constant that produced the message compared against the message. **It is not
vacuous, and that was measured, not argued:** `NS-7` (make the constant unreachable) is
**KILLED**, because the fixture two lines above is a **literal** string containing the
superseded trigger, so weakening the constant empties `stale` and `assert stale` fires first.

**S-5's pre-committed polarity (NO occurrence) HOLDS. The class count stays at FIVE; this
review found no sixth.**

---

## 5. ⚠️ THE SCOPED REIMPLEMENTATION — and the one place it disagrees (`OF-136`, MEDIUM)

`docs/reviews/independent/c13_review4_reimpl.py`. Stdlib only; asserts at import that
`whetstone_gate` is not in `sys.modules`; parses `config/lanes.yaml` with **its own** minimal
reader because the project's loader is `src/`; and — the point — **derives the four
requirements from `CONTEXT.md` §8.5.1 at run time** rather than transcribing them, so its
expectations move with the law instead of becoming a third copy.

**Sealed result: 24 vectors, 24 / 24 internally consistent, 0 checks failed.**

**Phase 2 then diffs it against the project's predicate.** Two derivations, side by side:

| | Phase-1, derived from the law | the project's `BRANCH_B_REQUIREMENTS` |
|---|---|---|
| 1 | `'on a cause that has been diagnosed'` | `'on a cause that has been diagnosed'` |
| 2 | ⚠️ `'it errored is not a cause'` | ⚠️ **`'is not a cause'`** |
| 3 | `'a harness defect is never branch b'` | `'a harness defect is never branch b'` |
| 4 | `'protocol.md'` | `'protocol.md'` |

* **22 of the 24 sealed vectors agree.** The two that differ — the empty condition and
  whitespace-only — differ **only because the project reports one MORE problem** (it also names
  `branch_b_condition is '', which states no condition`). Both reject. **Not a divergence in
  judgement.**
* **Three Phase-2 discriminators, added to separate the two derivations, DIVERGE — and in the
  direction where the project is the looser one:**

| | the `branch_b_condition` | Phase-1 | the project |
|---|---|---|---|
| **D1** | *"…**A provider timeout** is not a cause…"* | **rejects** | ⚠️ **accepts** |
| **D2** | *"…**a slow network** is not a cause…"* | **rejects** | ⚠️ **accepts** |
| **D3** | *"…**that** is not a cause…"* | **rejects** | ⚠️ **accepts** |

### `OF-136` — MEDIUM. **Requirement 2 is pinned to a 14-character generic fragment while the other three are pinned near-exactly, and the EXPORTED predicate is the loose one**

**The finding, precisely.** `CONTEXT.md` v1.9 §8.5.1 states the clause as ⚠️ ***"It errored" is
not a cause***. The project requires only `"is not a cause"`. So
`invocation.branch_condition_problems` — **the exported predicate, the one `python -m
whetstone_gate.camel_comparator` runs on RUN-1 night** — returns **zero problems** and prints
**"OK — both keys agree with the law"** on a pre-registered condition from which the ruling's
own example has been deleted. D3's exhibit is content-free and passes.

**What is right about it, said first.** A looser phrase permits **paraphrase**, and a
requirement about a *concept* arguably should. **The finding is the ASYMMETRY:** the other
three requirements permit no paraphrase at all, so the guard is not applying a policy — it has
one requirement pinned two orders of magnitude more loosely than its siblings, and it is the
one no review had mutated.

**Why it is a MEDIUM and not a BLOCKER, and this was decided by the seal, not afterwards.**
Rule of decision 5, pre-committed: *a reimplementation divergence is a BLOCKER only where it
changes a published value or a pre-registered condition.* **It changes neither today**, and
this review ran the decisive experiment rather than reasoning about it:

> `config/lanes.yaml`'s `"'It errored' is not a cause"` → `"A provider timeout is not a
> cause"`, committed in a fresh clone: **1 failed, 99 passed.** The drift **IS** caught.

**But look at where and by what.** It is caught at `:1202` by `assert needle in condition_b` —
the **fixture-integrity** assertion — whose failure message reads *"…so this fixture degrades
nothing. **Re-derive the weak form from the value as written.**"* ⚠️ **That message tells the
reader to weaken the test.** `REVIEW_13_3` §2.2 praised this file for the opposite property —
a failure message that tells the reader `config/` is not the thing to correct. **Here the two
guards disagree about what the requirement is, and the operator-facing one is the weaker.**

**Remedy, and it is one line:** requirement 2's phrase becomes `"it errored"` (or
`"'it errored' is not a cause"`), which occurs in §8.5.1 and in `config/` today, and the
weak-form fixture's `required` literal moves with it. **Under `Q-082` this does not hold the
tag**: no mutant survives on it — `NS-3` weakens requirement 2 further and is **KILLED** — so
it is not a survivor, and it is filed as a MEDIUM.

---

## 6. ⚠️ THE ONE SURVIVOR — `NS-9`, and the OWNED / NOT-OWNED determination, ARGUED

`config/lanes.yaml`: `branch: TODO_C13_RUN1` → `branch: "A"`.

**Measured against the whole repository, because the C13 file alone cannot see it:**

| run | result |
|---|---|
| `tests/test_c13_camel_comparator.py` | **100 passed** |
| bare `python -m pytest` (FULL) | **776 passed, 1 skipped** |
| `-m operator_gate` (what `make selftest` runs) | **2 passed, 775 deselected** — ⚠️ **was 1 failed** |

**Non-equivalent by exhibit:** `make selftest` flips **RED → GREEN** and the whole repository
is green. Nothing anywhere fails.

### THE DETERMINATION: **NOT-OWNED.** It does not hold the tag.

Under `Q-082` this is the sentence the verdict rests on, so it is argued in three checkable
steps rather than asserted.

1. **The mutation edits the one key C13 is FORBIDDEN to write and RUN-1 is REQUIRED to
   write.** `PROCESS.md` §12.1's RUN-1 row: *"at 18:00 the branch is decided either way and
   written into `PROTOCOL.md`"*. `Q-079` and `INC-46` both record `camel_comparator.branch` as
   left a sentinel **because a session that decided it would be inventing a result from a
   chair**. A mutant that writes `A` there is **byte-identical to RUN-1 doing its job.**
2. **The artefact that would tell the two apart does not exist, and it is not C13's.** That
   artefact is `PROTOCOL.md`'s diagnosed cause, *recorded before a branch is selected* —
   §8.5.1's own words, carried in `config/`'s `branch_b_condition`. **`make check-prereg`
   reports NOT-YET-FROZEN**, `PROTOCOL.md` does not exist, and `git rev-parse prereg-v1` does
   not resolve. **`PROTOCOL.md` is C14's deliverable.** Failing C13 for not building C14's
   guard would fail a chunk for another chunk's scope — which is the regress `Q-082` was ruled
   to stop.
3. **The half of OWN-7 that C13 *does* own is defended, and `NS-9b` proves it rather than
   asserting it.** Mutating `invocation.py` so that **this package** writes
   `config/lanes.yaml` is **KILLED** (1 failed, 36 passed) by
   `test_this_chunk_does_not_decide_the_branch`, which walks the package's AST for
   `write_text` / `write_bytes` / `dump` / `open(…, "w")`. ⚠️ **And that test is structural on
   purpose** — its own docstring says *"so this test does not invert the moment RUN-1
   legitimately writes it"*. **The builder drew the same line this determination turns on,
   first, and wrote down why.**

**It is real, non-equivalent, and recorded as `OF-137`, addressed to C14 / RUN-1**: nothing in
the repository ties a **decided** `camel_comparator.branch` to a `PROTOCOL.md` that records
its cause **beforehand**, so the ordering the pre-registration is built on is asserted by no
test. That guard is buildable today (it would be vacuous now and firable at a constructed
state, exactly as `OF-117`'s test is), and it belongs to the session whose fence holds
`PROTOCOL.md`.

---

## 7. The two polarities that did not hold, and one the prompt got wrong

### 7.1 `F-115a` — pre-committed **0**, measured **2**. The prediction was wrong; the finding is closed

`grep -c "OF-104" tests/test_c13_camel_comparator.py` returns **2**, at `:1049-1050`. Both are
inside the **correction prose**:

> *"⚠️ **THIS DOCSTRING SAID `OF-104` UNTIL 2026-09-02, AND THAT NUMBER WAS NEVER ALLOCATED TO
> IT** (`OF-115`). `OF-104` at HEAD is **C6 REVIEW 3's** arm-identity finding, written **55
> minutes after** this file already carried the number…"*

**The docstring's own citation is now `Q-079` / `OF-62`** (`OF-62` ×2, `Q-079` ×8), and the
superseded number survives only as the **record of what it said** — this project's convention
everywhere else (`Q-057`'s fact 4, `INC-39`'s `Action`, `INC-54`'s figure). **`OF-115` is
CLOSED.** ⚠️ **This reviewer's criterion was written as a `grep` count when the property is
*"does it cite `OF-104` as its own finding"*, and a count cannot express that.** Recorded as
this review's own mis-specified probe, not as a defect in the fix.

### 7.2 ⚠️ The prompt's `T-7` is inaccurate, and the accurate statement is Q-079's ruling

The prompt asks to verify that `config/lanes.yaml` *"still carries the diagnosis requirement in
**BOTH** branch conditions"*. **Measured, per key:**

| key | carries a diagnosis word? |
|---|---|
| `branch_a_condition` | **NO** — *"IT RUNS: both passes … complete inside the 90-minute box, from the same working directory…"* |
| `branch_b_condition` | **YES** — *"…ON A CAUSE THAT HAS BEEN DIAGNOSED AND RECORDED IN PROTOCOL.md BEFORE A BRANCH IS SELECTED. 'It errored' is not a cause, and a harness defect is NEVER Branch B…"* |

**That is exactly what `Q-079`'s ruling requires**, in its own words: *"`branch_a_condition` no
longer names the model id: it states Branch A's condition as **the run completing**. A
`branch_b_condition` key is **ADDED**, so Branch B's trigger exists in `config/` as a **stated
condition** rather than only as the negation of another key."* **Branch A's condition is *it
runs*; the diagnosis requirement belongs to Branch B and is there.** The seal pre-committed
that this key would be *stated as measured rather than asserted from the prompt's phrasing*,
and it is. **No finding.**

### 7.3 `Q-074`'s fifth site and `OF-99` — verified CLOSED, and never C13's

`tests/test_lanes_operator_placeholders.py:147` now reads *"⚠️ **NOT Tables 5-7.** Those are
Appendix C ("Baseline results"), base model `Claude 3.5 Sonnet` … **Table 7 is RETAINED as
§8.5.2's P2 citation**"*, above a corrected citation of **Table 2, Appendix B, `o3 High`,
banking**. Closed by Session A's `ea3bd12`. **`git grep "Tables 5"` over `tests/`, `src/`,
`config/` and `PROCESS.md` returns five hits and every one is the corrected form** — the
"NOT Tables 5-7" clause. **Neither was ever C13's**: that file is named under **NOT** in every
C13 fence, and `REVIEW_13_3` §10.3 already carried both as not-C13's.

---

## 8. `OF-118` — **GENUINELY REALISED**, judged against the rule pre-committed in the seal

The seal deliberately pre-committed **no polarity** here — *"pre-committing an answer to a
judgement question is pre-committing the judgement"* — and pre-committed a **three-part rule of
decision** instead. Measured against it, part by part:

| the pre-committed rule | measured |
|---|---|
| **(a)** exported, and the export **is** the predicate | ✅ `"branch_conditions_are_stale" in package.__all__`; `package.branch_conditions_are_stale is invocation.branch_conditions_are_stale` |
| **(b)** a non-test caller **uses** the result — deleting the *use* while keeping the *call* goes RED | ✅ bound as `stale` in `__main__.py`; **`stale` itself reaches a `say(...)` call**. **`SD-13`** (`del stale`) and **`SD-14`** (`_n = len(stale)`, never reaching `say`) are **both KILLED** |
| **(c)** an input on which the non-test path **behaves differently** | ✅ real config → 0 problems → prints *"OK — both keys agree with the law"*; a broken pair → 5 problems → prints *"5 PROBLEM(S)"* and then each one |

**All three hold. `OF-118` is GENUINELY REALISED, not merely syntactically satisfied.**

⚠️ **THE RESIDUAL, STATED RATHER THAN GLOSSED, BECAUSE IT IS THE INTERESTING HALF.** `main()`'s
**return code** is unchanged by `stale`: `python -m whetstone_gate.camel_comparator` **exits 0**
with a stale pre-registered condition, and only the printed line moves. **FIX 3 names that
omission in terms** — *"`main()`'s return contract is **not** changed — that is more than
`OF-118` asked for, and it is named so the absence is not read as an oversight"* — which is the
right way to leave it, and it is recorded as **`OF-140`, LOW**, for whichever session decides
the command should fail on it.

---

## 9. Standing properties — all measured by this session

| property | measured |
|---|---|
| `make selftest` **RED on `camel_comparator.branch`, and FOR THAT REASON** | ✅ **1 failed, 1 passed, 784 deselected**; sole failure `test_the_camel_branch_is_decided_before_any_camel_run` on `UndeterminedValue: lanes.yaml: 'camel_comparator.branch' is not determined yet (sentinel 'TODO_C13_RUN1')` — the loader **refusing**, not defaulting |
| all three vendored trees at their pins | ✅ CaMeL `f083b6b396399d3b3c7f2ddaf613a5945eaf32d8` · AgentDojo `928bbae820a89556b03de5cf818eb350cd6082d1` · τ² `a2c024725189473d2d7cea3a5cfdbcc67478e41f`; all three `git status --porcelain` **EMPTY**; all three diffs **0 bytes** |
| `git status --porcelain tests/goldens/` | ✅ **empty** |
| `CONTEXT.md` still **v1.9** and byte-identical | ✅ blob **`8e820384afbb1de7de3892eb6b90a8e6dce1f378`** — identical to REVIEW 3's and REVIEW 2's; **224,645 bytes, LF 2,361, CR 0, TAB 0** |
| `make check-prereg` | ✅ **NOT-YET-FROZEN**, exit 0 — `PROTOCOL.md` does not exist. `git tag -l` = `c0-pass`…`c4-pass`; **`prereg-v1` does not resolve** |
| `evals/` empty → C13 spent nothing | ✅ **0 files under `evals/`** |
| `config/lanes.yaml`'s branch conditions | ✅ §7.2 — the diagnosis requirement is in `branch_b_condition`, which is where `Q-079`'s ruling put it |
| **the law asserted BEFORE the config** | ✅ **NS-6 proves it**: amending `CONTEXT.md` §8.5.1 **alone** turns the suite RED **at the law** |
| **this review** spent no tokens | ✅ **ZERO provider calls.** CaMeL not run, not installed, not imported. ⚠️ **Whether the model id is still served was NOT checked** — Branch A's condition and RUN-1's alone |

### 9.1 Suite counts, measured — with every failure attributed BY FILE

⚠️ **A concurrent Session A (C6 FIX 4, tokens `4b7f21ae` / `d5c8039f`) is editing this tree**,
so every figure is stated as measured at its moment and each run is named.

| run | result | attribution |
|---|---|---|
| `tests/test_c13_camel_comparator.py` at HEAD | **100 passed, 0 failed** | — |
| the same file in **each** temp clone, unmutated (the control every mutation is judged against) | **100 passed** × 29 runs | — |
| `make selftest` | **1 failed, 1 passed, 784 deselected** | `tests/test_lanes_operator_placeholders.py` — **deliberate**, the `TODO_C13_RUN1` sentinel, and it MUST stay red |
| bare `python -m pytest` in a clone, unmutated | **776 passed, 1 skipped** | — |
| ⚠️ **`make test` at HEAD** | **1 failed, 782 passed, 1 skipped, 2 deselected** in 441 s | the sole failure is `tests/test_repo_invariants.py::test_the_object_store_and_the_working_tree_agree`, and it **names its cause**: `assert not ['INCIDENTS.md']`. ⚠️ **`INCIDENTS.md` is the CONCURRENT SESSION A's uncommitted edit** — verified by reading the test, which walks `git ls-files` and compares tracked working-tree bytes to `HEAD:<path>`, so untracked files (this review's own artefacts, `grep.exe.stackdump`) cannot cause it. **NOT C13's and NOT this review's** |
| `make check-roles` | **17 passed, 0 failed, 5 n/a — OK** | — |

**No failure in any run is C13's.** ⚠️ **And one count is stated with its own caveat, because
`INC-54` is exactly about not doing so:** `make check-roles` printed E1 = *"47 issued row(s)"*
when it was run, **but that reads the WORKING TREE**, which at that moment held Session A's two
uncommitted token rows. **At this session's own commit `2a86849` the figure is 45** — 46 data
rows less the `WG-2026-08-30-CTX-13.4-A` row, which `check_roles._TOKEN_ROW` does not parse.
Both numbers are right about different trees, and **which tree was counted is stated rather
than left to be inferred.**

---

## 10. Findings

### 10.1 MEDIUM

**`OF-136` · ⚠️ `BRANCH_B_REQUIREMENTS`'s SECOND PHRASE IS A 14-CHARACTER GENERIC FRAGMENT
WHILE THE OTHER THREE ARE PINNED NEAR-EXACTLY, AND THE EXPORTED PREDICATE IS THE LOOSE ONE.**
§5. Three exhibits (D1/D2/D3) on which the Phase-1 law-derived predicate rejects and
`invocation.branch_condition_problems` **accepts**. The property is defended today, but by the
test's **fixture-integrity** assertion at `:1202`, whose failure message directs the reader to
**re-derive the fixture** rather than restore the law's clause; the exported predicate — the
one `python -m whetstone_gate.camel_comparator` runs on RUN-1 night — prints *"OK — both keys
agree with the law"*. **No mutant survives on it (`NS-3` is KILLED), so under `Q-082` it does
not hold the tag.** **Remedy: requirement 2's phrase becomes `"it errored"`, and the weak-form
fixture's literal moves with it.**

**`OF-137` · ⚠️ NOTHING TIES A DECIDED `camel_comparator.branch` TO A `PROTOCOL.md` THAT
RECORDS ITS CAUSE BEFOREHAND.** §6. `NS-9` — writing `branch: "A"` into `config/lanes.yaml` —
survives the **full** suite (776 passed) and flips `make selftest` **RED → GREEN**. **NOT-OWNED
by C13** on the argument in §6, and **addressed to C14 / RUN-1**, whose artefact `PROTOCOL.md`
is. **Remedy: one conditional guard — if `camel_comparator.branch` resolves, `PROTOCOL.md` must
exist and record the branch and its diagnosed cause.** It is vacuous today and firable at a
constructed state, exactly as `OF-117`'s test is.

**`OF-139` · ⚠️ A FRESH CLONE'S `pytest` IMPORTS THE **REAL** REPOSITORY'S PACKAGE, AND
NOTHING IN THIS REPOSITORY SAYS SO.** §3. `.venv/…/__editable__.whetstone_gate-0.1.0.pth`
holds `C:\Users\chinm\whetstone-gate\src`, and `config.repo_root()` follows `__file__`, so a
mutation-testing clone measures the **wrong tree** unless the reviewer sets `PYTHONPATH` —
**and the control still reads `100 passed`, so nothing looks wrong.** The failure direction is
"every mutant SURVIVED", which a reviewer would notice; but a *partial* set-up (say, `src/`
mutations only) fails silently. `REVIEW_13_3`'s driver sets `PYTHONPATH`; **that knowledge
exists only inside that one script.** ⚠️ **This is a finding about the REVIEW METHOD, not
about C13**, and it is filed here because this review hit it and no `docs/reviews/README.md`
line, `Makefile` target or test would have warned the next one. **Remedy: one paragraph in
`docs/reviews/README.md`, or a `make mutate-clone` target that does the three set-up steps
(`PYTHONPATH`, the `vendor/` junctions, the printed `repo_root()`).**

### 10.2 LOW

**`OF-138` · `vendor.pinned_sha()` RETURNS WHATEVER YAML MADE OF THE VALUE, WITH NO SHAPE
CHECK.** A `camel_sha` of all digits is parsed as an **int** and surfaces as
`TypeError: expected str, bytes or os.PathLike object, not int` from inside `subprocess`,
rather than as a refusal naming the key. Measured — it is how `NS-13`'s first form died, and
why it was re-run as `NS-13b`. ⚠️ **It is a 40-hex value in a `config/` file that becomes a
FROZEN pre-registration artefact at C14**, so the cheapest moment to shape-check it is before
the freeze. Hard rule 9's spirit: *a missing value is a hard refusal*; a **mistyped** one
should be too. **Remedy: one `re.fullmatch(r"[0-9a-f]{40}", …)` in `pinned_sha`.**

**`OF-140` · `main()`'s RETURN CODE IS UNCHANGED BY A STALE PRE-REGISTERED CONDITION.** §8.
`python -m whetstone_gate.camel_comparator` **exits 0** while printing *"N PROBLEM(S)"*.
⚠️ **FIX 3 named this omission deliberately** — *"that is more than `OF-118` asked for"* —
which is the correct call for a fix session and is why this is LOW and not MEDIUM. **Remedy,
for whichever session owns it: fold `stale` into `main()`'s non-zero return beside `failed`.**

### 10.3 Carried forward — **not C13's**, and not counted against it

* **`Q-074` / `OF-62`'s fifth site** — ✅ **CLOSED** by Session A's `ea3bd12`. §7.3.
* **`OF-99`** — the repository-wide superseded-string tripwire. `ea3bd12`'s subject names
  `OF-110`'s source-text moat scan and `tests/test_lanes_operator_placeholders.py:154-155`
  states the tripwire *"now scans for it, and was fired at this docstring's previous text to
  prove it would have caught it."* **Closed by Session A, and never C13's.**
* **`OF-67` / `OF-70` / `OF-78`** — `check_roles.py` counting the session-token table itself,
  the **seventeenth** consecutive session to carry the total by hand. `check_roles.py` is under
  **NOT** in this fence, and a review session fixes nothing.

---

## 11. What the fix got right — recorded, because a PASS that lists only faults is not a review either

* **Every one of REVIEW 3's five survivors is closed by a change that is load-bearing
  individually**, not by one lump that any edit trips.
* **The shape, not the instances.** `len(...) == 4` against a literal; a weak-form fixture per
  requirement; the needle asserted present **before** it is degraded (`INC-50`'s move); the
  undegraded value asserted **accepted** as a control. The two assertions `INC-55` is about
  survive only as **quoted text in the comment that explains why they are gone.**
* ⚠️ **FIX 3 MUTATED ITS OWN NEW CODE AND FOUND TWO DEFECTS IN ITS OWN REMEDY**, both surviving
  the full suite, and closed both. **This review re-ran all three (SD-11, SD-13, SD-14) and all
  three are dead.** `SD-11`'s remedy is **non-vacuous**, which FIX 3 checked before relying on
  it and which is verified again here character by character.
* **`OF-118` is genuinely realised**, judged against a rule this review committed to in
  advance — and the one thing it does **not** do (change `main()`'s exit code) is **named by
  the fix itself** rather than left to be discovered.
* **`OF-119`'s boundary is pinned TWICE** — structurally (`end == subsection[0]`) and **by
  content** (`"policy coverage"` is §8.5.2's P3 and must not be in the window) — *"because a
  boundary asserted only by the rule that computed it asserts nothing."* Measured: the window
  narrows from **6,817 to 3,646 characters**, all four phrases stay inside it, and
  `"policy coverage"` is out.
* **`OF-115`'s correction is legible rather than silent** — the superseded number is kept with
  a dated explanation of what happened, which is why this reviewer's `grep`-count criterion was
  the wrong probe and the fix was right.
* **`OF-117` closes hard rule 9's clause on the two keys `Q-079` was raised about**, and pins
  **both** halves: a sentinel is one `UndeterminedValue`, a **missing key** is
  `MissingRequiredValue` — the state `Q-079` actually found. **`config/` never holds either
  state**; the mapping is constructed in the test (`INC-11`, `INC-17`).
* **FIX 3 deliberately opened NO new `OF-` number** because a concurrent session was allocating
  against the same file, and recorded its two self-found defects in `OPEN_FINDINGS.md`,
  `PROGRESS.md` and `73de008`'s message with the mutants named. ⚠️ **That was the right call
  and this review verified it was not a hiding place: both mutants are named precisely enough
  that they were re-run here from the record alone.** **Their numbers are allocated now** —
  they are **not** given `OF-` rows, because `SD-11` and `SD-13` were **found and closed inside
  one session** and `OPEN_FINDINGS.md` is for findings a review could not close. **Said
  explicitly, because the prompt asked and the answer is "no rows, and here is why".**

---

## 12. Artefacts

| path | what |
|---|---|
| `independent/c13_review4_criteria.md` | the **Phase-1 seal** — ten owned properties, the required set, ~40 pre-committed polarities, the restore rule, the `OF-118` rule of decision, seven declared leaks. `9e16d87` |
| `independent/c13_review4_reimpl.py` | the **scoped reimplementation** — the four requirements **derived from the law at run time**, the sentinel refusal path implemented twice, 24 vectors, stdlib only, nothing from `src/` |
| `independent/c13_review4_reimpl_output.txt` | its committed output — 24 / 24, 0 failed |
| `independent/c13_review4_mutants.py` | the mutation driver — original-bytes restore, printed `repo_root()`, `PYTHONPATH` fix, negative control |
| `independent/c13_review4_mutants_output.txt` | both rounds' raw output, plus `NS-9`'s whole-repository characterisation and the `D1` config-drift experiment |
| `independent/c13_review4_probes.py` + `_output.txt` | the Phase-2 probes — the reimplementation diff, the shape scan, `OF-115/117/118/119`, the standing properties |
| `mutants/c13_mutants_4.md` | **27 mutants** — 25 killed, 1 survivor, 1 negative control, 0 VOID |

---

## 13. The tag

**`c13-pass` is CUT.** The five survivors are dead, the shape is gone, FIX 3's own three are
dead, the required set of seventeen new-surface mutants across all ten owned properties is
clean, the reimplementation agrees except on one MEDIUM that no mutant survives, and there are
**zero BLOCKERs**.

⚠️ **C13 failed three times and every fail was right. This is not a fourth, and the reason is
stated rather than felt:** `Q-082`'s ruling gave the bar a termination condition it did not
have, this review fixed its required set **in the seal before measuring**, and the set came out
clean. **The one survivor was examined at the length it deserved precisely because it was the
cheapest available fourth FAIL, and it is NOT-OWNED on an argument the builder had already
written down first.**
