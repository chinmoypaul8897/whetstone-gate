# C13 mutants — REVIEW 4 (`7a1e6c84`), 2026-09-02

**27 mutants. 25 KILLED · 1 SURVIVED · 1 SURVIVED BY DESIGN (the negative control) · 0 VOID.**
Driver: [`../independent/c13_review4_mutants.py`](../independent/c13_review4_mutants.py).
Raw output: [`../independent/c13_review4_mutants_output.txt`](../independent/c13_review4_mutants_output.txt).

---

## 0. THE HARNESS, AND THE TWO WAYS IT COULD HAVE LIED

Both failure directions are named, because each was live in this repository this week.

**(a) The FLATTERING one — a defeated restore reports every mutant as KILLED.**
C6 REVIEW 4's harness restored with `git checkout --` from a HEAD that already held the
mutation, so the tree never went back. **This harness never calls `git checkout --`.** It
captures the target file's **original bytes** before mutating, writes those bytes back
afterwards, re-hashes to confirm the restore, and **re-runs the full control**. A run whose
post-restore control is not green is printed **VOID** and is not scored. **0 VOID in 27.**

**(b) ⚠️ THE OTHER ONE, WHICH THIS REVIEW HIT FIRST-HAND AND WHICH WOULD HAVE REPORTED
EVERY MUTANT AS *SURVIVED*.** `.venv/Lib/site-packages/__editable__.whetstone_gate-0.1.0.pth`
contains one line — `C:\Users\chinm\whetstone-gate\src`. A bare `python -m pytest` **inside a
fresh clone** therefore imports the **real repository's** package, and `config.repo_root()`
is `Path(__file__).resolve().parents[2]`, so `repo_root()` resolves to the **real repository
too**. **Measured, not inferred:**

```
(clone, before the fix)  PKG : C:\Users\chinm\whetstone-gate\src\whetstone_gate\__init__.py
                         ROOT: C:\Users\chinm\whetstone-gate
```

Every `src/`, `config/` and `CONTEXT.md` mutation applied in the clone would have had **no
effect at all**. The control still read *100 passed*, so nothing would have looked wrong.
**Fixed by `PYTHONPATH=<clone>/src`**, which precedes site-packages in `sys.path`, and the
resolved paths are **printed at the head of every run** rather than assumed:

```
whetstone_gate.__file__ = ...\scratchpad\c13r4clone\src\whetstone_gate\__init__.py
config.repo_root()      = ...\scratchpad\c13r4clone
```

The driver **aborts with rc=3** if the package under test is not the clone's.

**(c) The vendored trees are gitignored (`vendor/*/`), so a clone has none of them.** They are
attached as **NTFS junctions** to the real ones. ⚠️ **Consequently NO MUTANT WRITES INTO
`vendor/`** — a write there would land in the operator's repository. `OWN-10` is attacked
through the **pin** instead, which exercises the same guard and touches nothing outside the
clone.

**(d) The negative control.** `NS-14` changes no behaviour and **must survive**. It did. A
harness in which every mutant dies is not measuring anything, and this row is what makes the
other twenty-six readable.

---

## 1. REVIEW 3's FIVE SURVIVORS — 5 / 5 KILLED

Clone 1. Control before any mutation: **100 passed**. Each mutation **committed inside the
clone**; each restore by **original bytes**; control green after every restore.

| id | OWN | file | the mutation | result |
|---|---|---|---|---|
| **N-B** | OWN-3 | `invocation.py` | requirement 1 phrase → `"cause"` | ✅ **KILLED** — 1 failed, 33 passed |
| **N-C** | OWN-3 | `invocation.py` | requirement 3 phrase → `"harness"` | ✅ **KILLED** — 1 failed, 33 passed |
| **N-D** | OWN-3 | `invocation.py` | requirement 4 phrase → `"md"` | ✅ **KILLED** — 1 failed, 33 passed |
| **N-E** | OWN-3 | `invocation.py` | one whole `BRANCH_B_REQUIREMENTS` entry deleted | ✅ **KILLED** — 1 failed, 33 passed |
| **N-I2** | OWN-6 | `invocation.py` | `lanes.require(…)` → `lanes.data.get(…, "")` | ✅ **KILLED** — 1 failed, 34 passed |

All five die in
`test_the_pre_registered_branch_condition_carries_the_DIAGNOSIS_requirement` /
`test_a_SENTINEL_branch_condition_is_a_REFUSAL_and_never_flows_in_as_a_VALUE`.

⚠️ **N-C WAS CHECKED HARDEST, AS THE PROMPT ASKED, AND ITS KILL IS ON THE RIGHT EXHIBIT.**
The weak-form fixture for requirement 3 is the **real** `branch_b_condition` with
`"a harness defect is NEVER Branch B"` replaced by **`"a harness defect is SOMETIMES Branch
B"`** — the direct inversion of `Q-057`'s ruling, the string that passed the entire
repository under REVIEW 3. Under N-C the mutated phrase `"harness"` is still present in that
inverted string, so the guard raises **zero** complaints and
`assert len(problems) == 1` fires. The kill is on the inversion itself, not on a generically
degraded neighbour.

---

## 2. FIX 3's OWN SELF-DIRECTED MUTANTS — 3 / 3 KILLED

Re-run by this review from FIX 3's own descriptions, not taken on report.

| id | OWN | the mutation | result |
|---|---|---|---|
| **SD-11** | OWN-3 | `{phrase!r}` → `{BRANCH_B_REQUIREMENTS!r}` in the guard's message | ✅ **KILLED** — 1 failed, 33 passed |
| **SD-13** | OWN-6 | `__main__`: keep the `branch_conditions_are_stale()` call, `del` its result, print a constant | ✅ **KILLED** — 1 failed, 35 passed |
| **SD-14** | OWN-6 | `__main__`: `_n = len(stale)` — the result is **read** but never reaches `say()` | ✅ **KILLED** — 1 failed, 35 passed |

⚠️ **SD-11's kill is NOT vacuous, checked rather than assumed.** The guard's message ends with
prose that spells all four requirements — *"…on a cause that has been DIAGNOSED and recorded
in PROTOCOL.md before a branch is selected; 'it errored' is not a cause, and a harness defect
is never Branch B."* If any of those matched `repr(other)`, FIX 3's new
`assert repr(other) not in problems[0]` would be satisfied by accident. It is not:
`repr` requires the quote characters, and the prose spells every phrase **unquoted and in
different case** (`PROTOCOL.md`, `DIAGNOSED`, `Branch B`), while `'it errored' is not a cause`
puts a **space** between the closing quote and `is`. **Verified character by character.**

---

## 3. NEW-SURFACE MUTANTS — one per property C13 OWNS

The ten owned properties were enumerated and argued **in the Phase-1 seal**
(`../independent/c13_review4_criteria.md` §1, committed at `9e16d87`), **before any mutant was
written** — because `Q-082`'s termination condition is worthless if the set is chosen after
the measurement.

| id | OWN | file | the mutation | result |
|---|---|---|---|---|
| **NS-1** | **OWN-1** | `invocation.py` | pass 2 drops `--replay-with-policies`; the two passes become one command | ✅ **KILLED** — 1 failed, 21 passed |
| **NS-15** | **OWN-1** | `invocation.py` | pass 1 stops declaring the pipeline name pass 2 replays | ✅ **KILLED** — 1 failed, 21 passed |
| **NS-2** | **OWN-2** | `config/lanes.yaml` | Branch A re-acquires *"the model id is still served"* | ✅ **KILLED** — 1 failed, 33 passed |
| **NS-3** | **OWN-3** | `invocation.py` | requirement **2**'s phrase — the one REVIEW 3 never mutated — → `"a cause"` | ✅ **KILLED** — 1 failed, 33 passed |
| **NS-4** | **OWN-3** | `invocation.py` | the complaint quotes the **label** instead of the **phrase** | ✅ **KILLED** — 1 failed, 33 passed |
| **NS-5** | **OWN-3** | `invocation.py` | the case fold dropped → the guard goes case-sensitive | ✅ **KILLED** — 1 failed, 33 passed |
| **NS-6** | **OWN-4** | `CONTEXT.md` | **the LAW alone** amended, `config/` untouched | ✅ **KILLED** — 1 failed, 33 passed, **at the law** |
| **NS-7** | **OWN-5** | `invocation.py` | `SUPERSEDED_BRANCH_TRIGGER` made unreachable | ✅ **KILLED** — 1 failed, 33 passed |
| **NS-8** | **OWN-6** | `invocation.py` | the loader's refusal **swallowed** — `except ConfigError: return []` | ✅ **KILLED** — 1 failed, 34 passed |
| **NS-9** | **OWN-7** | `config/lanes.yaml` | `branch: TODO_C13_RUN1` → `branch: "A"` | ⚠️ **SURVIVED** — see §4 |
| **NS-9b** | **OWN-7** | `invocation.py` | **this package** writes `config/lanes.yaml` | ✅ **KILLED** — 1 failed, 36 passed |
| **NS-10** | **OWN-8** | `branch_b.py` | the provenance gate stops requiring an **appendix** | ✅ **KILLED** — 1 failed, 62 passed |
| **NS-11** | **OWN-8** | `branch_b.py` | `TABLE_NUMBER` starts accepting the **range** `Tables 5-7` | ✅ **KILLED** — 1 failed, 65 passed |
| **NS-17** | **OWN-8** | `branch_b.py` | the provenance gate stops requiring a **base model** | ✅ **KILLED** — 1 failed, 63 passed |
| **NS-12** | **OWN-9** | `branch_b.py` | the headline pair re-attributed to **Table 5** | ✅ **KILLED** — 1 failed, 56 passed |
| **NS-16** | **OWN-9** | `branch_b.py` | the headline pair moved to **Appendix C** — `Q-058`'s defect one field over | ✅ **KILLED** — 1 failed, 56 passed |
| **NS-13** | **OWN-10** | `config/protocol.yaml` | the pinned CaMeL SHA no longer matches the checkout | ✅ **KILLED** — see below |
| **NS-14** | *control* | `invocation.py` | `passes = [` → `passes = [] or [` — **no behaviour change** | ✅ **SURVIVED, AS REQUIRED** |

**Every one of OWN-1 … OWN-10 carries at least one mutant. The required set is COMPLETE:
seventeen new-surface mutants against a floor of ten, itself above `PROCESS.md` §5.3's eight.**

### 3.1 ⚠️ NS-13 was re-run because its first kill was the WRONG SHAPE, and saying so is the point

`camel_sha: 0000000000000000000000000000000000000000` is parsed by YAML as an **integer**, so
the kill was `TypeError: expected str, bytes or os.PathLike object, not int` from inside
`subprocess`, not the pin check refusing. **Re-run as `NS-13b` with a string SHA one hex digit
from the pin:**

```
VendorError: `git diff f083b6b396399d3b3c7f2ddaf613a5945eaf32d9` failed in
vendor/camel-prompt-injection (exit 128): fatal: bad object f083b...d9
```

**A typed refusal naming the bad object. OWN-10 is defended.** ⚠️ **And the first form is
itself a LOW finding (`OF-138`):** `vendor.pinned_sha()` returns whatever YAML made of the
value with **no shape check**, so a mistyped SHA in a **frozen pre-registration artefact**
surfaces as a `TypeError` deep in `subprocess` rather than as a refusal naming the key.

---

## 4. ⚠️ THE ONE REAL SURVIVOR — NS-9, and why it is **NOT-OWNED**

`config/lanes.yaml`: `branch: TODO_C13_RUN1` → `branch: "A"`.

**Measured against the whole repository, because the C13 file alone cannot see it:**

| run | result |
|---|---|
| `tests/test_c13_camel_comparator.py` | **100 passed** |
| bare `python -m pytest` (FULL) | **776 passed, 1 skipped** in 335s |
| `-m operator_gate` (what `make selftest` runs) | **2 passed, 775 deselected** — ⚠️ **was 1 failed** |

**Non-equivalent by exhibit:** `make selftest` flips **RED → GREEN**, and the whole repository
is green. Nothing anywhere fails.

### ⚠️ THE DETERMINATION, ARGUED RATHER THAN ASSERTED — `Q-082` makes this the verdict

**NOT-OWNED. It does not hold the tag.** Three steps, and each is checkable:

1. **The mutation edits the one key C13 is FORBIDDEN to write and RUN-1 is REQUIRED to write.**
   `PROCESS.md` §12.1: RUN-1 *"decides the branch either way and writes it into `PROTOCOL.md`"*.
   `INC-46` and `Q-079` both name `camel_comparator.branch` as deliberately left a sentinel
   *because a fix session that decided it would be inventing a result*. A mutant that writes
   `A` there is **byte-identical to RUN-1 doing its job**.
2. **There is no artefact against which the two could be told apart, and it is not C13's.**
   The record that would distinguish them is `PROTOCOL.md`'s diagnosed cause, *recorded before
   a branch is selected*. **`PROTOCOL.md` does not exist** — `make check-prereg` reports
   **NOT-YET-FROZEN** and `git rev-parse prereg-v1` does not resolve. It is **C14's**
   deliverable. Failing C13 for not building C14's guard would fail a chunk for another
   chunk's scope.
3. **The half of OWN-7 that C13 *does* own is defended, and `NS-9b` proves it.** Mutating
   `invocation.py` so that **this package** writes `config/lanes.yaml` is **KILLED** by
   `test_this_chunk_does_not_decide_the_branch`, which walks the package's AST for
   `write_text` / `write_bytes` / `dump` / `open(..., "w")`. That test is deliberately
   structural *"so this test does not invert the moment RUN-1 legitimately writes it"* — which
   is the same distinction this determination turns on, made by the builder first.

**It is real, it is non-equivalent, and it is recorded as `OF-137`, addressed to C14 / RUN-1.**
Under `Q-082`'s third sentence it is a MEDIUM in `OPEN_FINDINGS.md` and does not hold the tag.

---

## 5. Every restore, and the proof that none was defeated

| | |
|---|---|
| mutations applied | **27** (21 clone 1 · 6 clone 2), each **committed inside its clone** |
| restore method | **the original bytes, captured before the mutation and written back.** `git checkout --` is never called |
| restore verified | SHA-256 of the restored file re-compared to the pre-mutation digest, **and** the full control re-run |
| **VOID runs** | **0** |
| controls run | 27 post-restore + 2 pre-run = **29**, every one **100 passed** |
| negative control | **NS-14 SURVIVED**, as required |
| package under test | printed at the head of every run; **the clone's**, never the real repository's |
| writes into `vendor/` | **none** — the junctions make that unsafe and no mutant does it |
