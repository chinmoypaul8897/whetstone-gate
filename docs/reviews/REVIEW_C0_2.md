# REVIEW_C0_2 — adversarial re-review of chunk C0, attempt 2

**SESSION-TOKEN:** `f57e216b` · **Role:** REVIEW · **Chunk:** C0 · **Date:** 2026-08-31
**Review type:** `code` (persona 2 — CODE REVIEWER), per `PROCESS.md` §12.1's C0 row.
**Fix span:** `9663247..HEAD`. **Chunk under review: all of C0** — the checks, the loader, the
tripwire and the Makefile targets.
**Predecessor:** `docs/reviews/REVIEW_C0.md` (attempt 1, token `52f5307b`, **FAIL**). That file is
**not** overwritten, renamed or deleted, and nothing in it is edited by this session.
**Concurrent:** pair **P-02**, the C1 review (token `a0cc0212`), ran alongside this one. Its chunk
is disjoint; where its work touched my measurements it is named, and it is never rounded up.

---

# VERDICT: **PASS**

**B-01, B-02 and B-04 are CLOSED. B-03 is closed in the form that made it a BLOCKER and leaves a
residue that attempt 1 itself graded MEDIUM.** Thirteen mutants, all killed, control surviving.
Zero BLOCKER findings. Four findings go to `OPEN_FINDINGS.md` — three MEDIUM, one LOW — and none
of them is a check reporting PASS over nothing, which is what attempt 1's four had in common.

**`c0-pass` is cut. It is the first tag this project has ever cut.**

**What this verdict is not.** It is not a statement that C0 is finished or that the repository is
clean. `make test` **is red today** on one test, and there is a test C0 owns whose name promises
more than it checks. Both are recorded below, at their real severity, with the one that is C0's
carried into `OPEN_FINDINGS.md`.

| | attempt 1's BLOCKER | status after my own re-run |
|---|---|---|
| **B-01** | E2 and E3 structurally unable to fire | **CLOSED** — both FAIL on the violation, verbatim, and the real table is clean for the right reason |
| **B-02** | the moat defeated by hard rule 8's own named spike defect | **CLOSED** — all four attack forms FAIL, **two hops** FAIL, the clean control still PASSES |
| **B-03** | the F group reports `config/` complete over a `config/` missing a pre-registration artefact | **CLOSED in both reachable forms.** Residue: `check-prereg` still exits 0 over a non-repository — attempt 1's own **F-12**, i.e. **OF-09**, MEDIUM, and it stays open |
| **B-04** | the pre-spend gate flips GREEN when the key it guards is deleted | **CLOSED** — RED in both fixtures, and RED for the right reason in the real tree |

---

# 1. How this review was run, and the two traps it had to avoid first

## 1.1 INC-17 — reproduced independently before any measurement was taken

This repository is installed **editable**: `C:\Users\chinm\whetstone-gate\src` sits on `sys.path`
through a `.pth` file in the active venv. Standing inside a clone of an old commit and running
`python`/`pytest` therefore imports **the live repository**, not the checkout.

```
$ cd <clone at 864c621>                       # PRE-FIX source on disk
$ python -c "import whetstone_gate; print(whetstone_gate.__file__)"
C:\Users\chinm\whetstone-gate\src\whetstone_gate\__init__.py        <- THE LIVE REPOSITORY

$ PYTHONPATH=<clone>/src python -c "import whetstone_gate; print(whetstone_gate.__file__)"
<clone>\src\whetstone_gate\__init__.py                              <- the checkout
$ PYTHONPATH=<clone>/src python -c "from whetstone_gate import config; print(config.repo_root())"
<clone>                                                             <- and repo_root follows it
```

**Confirmed, and it matters more than it looks:** `config.repo_root()` is
`Path(__file__).resolve().parents[2]`, so it follows `PYTHONPATH` into the clone and the entire
run — loader, `config_dir()`, every check — is self-consistent with the tree under test.

**Every OLD-beside-NEW pair below was produced this way, and `whetstone_gate.__file__` was printed
on every single run.** Where a figure is quoted in this file, the tree it came from is named.

## 1.2 INC-11 — a mutant that only has to exist on disk to look killed

`test_the_object_store_and_the_working_tree_agree` fires on **any** uncommitted edit to a tracked
file. **Every mutant was committed**, `git status --porcelain` was captured for each, and a
**semantics-preserving control** was included. Full method and both traps I fell into myself are in
`docs/reviews/mutants/c0_mutants.md`.

## 1.3 Baselines, measured on the live repository at `68fcfff`

| command | result | |
|---|---|---|
| `python -m whetstone_gate.tasks check-roles` | **17 passed, 0 failed, 4 n/a**, exit 0 | ✅ |
| `make check-roles` (through the `~/bin/make.exe` shim, GNU Make 3.82.90) | identical | ✅ |
| `python -m whetstone_gate.tasks selftest` | **1 failed, 1 passed** — RED, on the **CaMeL branch**, through `require()` raising `UndeterminedValue` | ✅ Q-009 upheld |
| `python -m whetstone_gate.tasks test`, **C0's view** (`--ignore=tests/test_c1_review_probes.py`) | **215 passed, 1 skipped, 2 deselected** | ✅ |
| `python -m whetstone_gate.tasks test`, **as a stranger runs it** | **1 failed, 222 passed, 1 skipped, 2 deselected** | ⚠️ see **I-02** |

⚠️ **The one red is `tests/test_c1_review_probes.py::test_section_0_states_its_own_quoted_line_count_correctly`
— a C1 review probe standing over C1's own BLOCKER, landed by the concurrent session while this
review was running.** It is not C0's, and it is not silently excluded: it is stated here, both
counts are given, and it is recorded as **I-02**.

---

# 2. B-01 … B-04 — attempt 1's evidence, re-run, OLD beside NEW

## B-01 — E2 and E3. **CLOSED.**

Attempt 1's fixture, verbatim: into a **fixture copy** of `QUESTIONS.md`'s `## Session tokens`
table (never the real file — it was restored and byte-compared afterwards, `True` both times), the
two violations `PROCESS.md` §7a names.

```
| `deadbeef` | C0 | BUILD  | 2026-08-30 |
| `deadbeef` | C0 | REVIEW | 2026-08-30 |     <- E2's exact condition
| `cafebabe` | C1 | BUILD  | 2026-08-30 |
| `cafebabe` | C2 | FIX    | 2026-08-30 |     <- E3's exact condition
```

| | **OLD** — `864c621`, `__file__` → `…\old\src\…` | **NEW** — HEAD, `__file__` → `…\new\src\…` |
|---|---|---|
| rows parsed by `_TOKEN_ROW` | 8, **all four violations among them** | 22, **all four violations among them** |
| **E2** | `PASS  clean` | **`FAIL  SHARED on ['C0'] — build and review are never the same session`** |
| **E3** | `PASS  clean` | **`FAIL  REUSED: cafebabe appears as [('C1','BUILD'),('C2','FIX')]; deadbeef appears as [('C0','BUILD'),('C0','REVIEW')]`** |

The rows parsed on both sides. The violations were present on both sides. **Old said clean; new
names the chunk and the pairs.** The mechanism is `_issued_tokens` returning
`dict[str, set[tuple[str, str]]]` instead of `dict[str, tuple[str, str]]`, read in source and then
confirmed by mutant **M28**, which restores the old shape and is killed by three tests.

**And the harder test the fix invites — is the REAL table clean for the right reason?**

```
ROWS PRESENT in the `## Session tokens` table : 19
ROWS PARSED  by _TOKEN_ROW                    : 18
ROWS SILENTLY DROPPED                         : 1
  [DROPPED] | `WG-2026-08-30-CTX-13.4-A` | *(none — CONTEXT.md §13.4 correction…)* | BUILD | … |

C0 BUILD  -> ['e210c6f5']
C0 REVIEW -> ['52f5307b', 'f57e216b']        <- mine, and attempt 1's
C0 FIX    -> ['c9521aac']
BUILD ∩ REVIEW = []            E2 clean, CORRECTLY — the sets are genuinely disjoint
tokens holding >1 (chunk, role) pair = []    E3 clean, CORRECTLY
```

**E2 has real input for the first time and it is clean because the tokens really are different**,
not because a row went missing. The one dropped row is the CTX-13.4 token Q-014 (iv) **forbids
reshaping** — the row-side twin of `E5_EXCEPTIONS`.

**But the drop is silent, and that is a new finding: F-19.** See §5.

## B-02 — the moat. **CLOSED.**

All four attack forms from `REVIEW_C0.md` B-02, plus a **two-hop** form of my own and a **clean
control**, built under `src/whetstone_gate/{gates,scorer}/` — **Q-004's ruled layout** — and fired
at `check_gate_scorer_isolation`. Every fixture was torn down and `leftovers: none` was asserted.

| # | what `gates/` and `scorer/` do | **OLD** `864c621` | **NEW** HEAD |
|---|---|---|---|
| 1 | both `from whetstone_gate.shared_predicate import intent_key` | **FAIL D3** | **FAIL D3** — `SHARED: ['whetstone_gate.shared_predicate']` |
| 2 | both `from whetstone_gate import shared_predicate` — **the spike defect, in Python** | **PASS** ❌ | **FAIL D3** — same module named |
| 3 | `gates/` does `from .. import scorer` | **PASS** ❌ | **FAIL D1 and D3** — `CROSSES: ['whetstone_gate.scorer']` |
| 4 | each imports its own helper; both helpers import the predicate (**ONE hop**) | **PASS** ❌ | **FAIL D3** |
| 5 | **TWO hops** — helper → hop → predicate *(mine; attempt 1 did not test it)* | **PASS** ❌ | **FAIL D3** — `SHARED: ['whetstone_gate.deep_predicate']` |
| 6 | **CLEAN CONTROL** — each side has its own private copy | **PASS** ✅ | **PASS** ✅ |

**The transitivity claim is specifically tested and it holds at two hops.** Form 6 is the half that
matters just as much: D3 is not hard-wired to fail, so its FAILs mean something. Confirmed again by
mutant **M21**, which stops the walk after one hop and is killed by form 4's probe alone.

**`MOAT_ALLOW_LIST` — a pin over a list that does nothing would be decoration. It is not:**

```
MOAT_ALLOW_LIST as shipped = set()  ->  0 entries
  allow-list EMPTY (as shipped)                        D3 = FAIL
  allow-list holding the one shared module             D3 = PASS      <- it really can blind D3
  allow-list restored to EMPTY                         D3 = FAIL
```

Q-015 landed **as ruled**: created empty, pinned empty by `test_the_moat_allow_list_is_empty`, with
`"whetstone_gate" not in MOAT_ALLOW_LIST` asserted separately — the unruled one-entry allow-list
that was B-02's cause. Mutant **M32** puts the package root back and is killed.

## B-03 — the `config/` group. **CLOSED in both reachable forms; one residue, MEDIUM.**

**Form 1 — `git rm config/protocol.yaml`, committed, in a clone.**

| | **OLD** `864c621` | **NEW** HEAD |
|---|---|---|
| F1 | `PASS  protocol.yaml and lanes.yaml parse` ← **naming a file it never opened** | **`FAIL  …\config: …\config\protocol.yaml does not exist. config/ is a pre-registration artefact (CONTEXT.md §15.0); it is not optional and has no fallback.`** |
| F2 | `PASS  1 explicit TODO_ sentinel(s)` ← **it was 6; five vanished, including the void threshold** | `n/a  not evaluated — config/ did not load; see F1` |
| F3 / F4 | `PASS  none outstanding` / — | `n/a` / `n/a`, each with the reason |
| summary | `14 passed, 0 failed, 3 n/a` · **exit 0** | `14 passed, 1 failed, 6 n/a` · **exit 1** |

**No silent count drop: the count is not smaller, it is absent, and its absence is reported.**
That is hard rule 11 applied to a check's own denominator, which was B-03's diagnosis.

**Form 2 — `pip install .` (NON-EDITABLE), a real venv, so `repo_root()` resolves into it.**

```
$ <venv>/Scripts/python -c "import whetstone_gate.config as c; print(c.repo_root())"
…\nonedit_venv\Lib                       <- exactly what attempt 1 found
$ <venv>/Scripts/python -c "…; print(c.config_dir().is_dir())"
False
```

| target | **OLD** (attempt 1's measurement) | **NEW**, measured here |
|---|---|---|
| `check-roles` | `PASS F1 · PASS F2 · PASS F3` over **zero** config files, exit 0 | **`FAIL R1 the examined root IS this repository`** naming the directory and the cause, **`FAIL F1`**, `n/a F2/F3/F4`, **exit 1** |
| `tasks test` | green | **exit 1** — `ConfigFileMissing`, an unhandled traceback but a loud, non-zero refusal |
| `check-prereg` | `config/ holds 0 file(s):` · **exit 0** | ⚠️ **`config/ holds 0 file(s):` · exit 0 — UNCHANGED** |
| `tasks eval` | — | ⚠️ **exit 0**, carrying that `check-prereg` |

**The BLOCKER is closed.** The false statement — the word `PASS` beside *"protocol.yaml and
lanes.yaml parse"* over a file that was never opened — is gone in both forms, and `R1` fails rather
than reporting green over the wrong directory.

**The residue is `check-prereg` and `eval`, and it is attempt 1's own F-12 → OF-09.** My decision
and its reasoning are in **§4**. It stays **OPEN**, at **MEDIUM**, with a deadline.

## B-04 — the pre-spend gate. **CLOSED.**

| fixture | **OLD** `864c621` | **NEW** HEAD |
|---|---|---|
| as shipped | `1 failed, 1 passed` — RED | `1 failed, 1 passed` — RED |
| **`camel_comparator:` block deleted** | **`2 passed` — GREEN** ❌ | **`1 failed, 1 passed` — RED**, on `MissingRequiredValue: required value 'camel_comparator.branch' is missing (stopped at 'camel_comparator')` |
| **`config/lanes.yaml` deleted entirely** | `1 failed, 1 passed` — the camel test errored, but **`test_no_operator_placeholder_remains_in_config` PASSED over a file that was not there** ❌ | **`2 failed`** — *"CONFIG REFUSAL — the pre-spend gate cannot even READ config/, so it certainly cannot certify that no placeholder remains"* |

**RED for the right reason in the real tree**, which the prompt asks for specifically:

```
UndeterminedValue: lanes.yaml: 'camel_comparator.branch' is not determined yet
  (sentinel 'TODO_C13_RUN1'). Resolved by: C13 / RUN-1 — the 90-minute timeboxed CaMeL
  branch test on 31 Aug decides Branch A (live) or Branch B (citation).
```

That is the **CaMeL branch**, through `require()`, exactly as Q-009 says it should be until RUN-1.
`.data.get(…, {}).get(…)` — the defaulting accessor `config.py`'s docstring says *"does not exist
and must not be added"* — is gone from the gate. A green selftest here would have been a FAIL; it
is not green.

---

# 3. The ruling-driven changes — ruled, or merely landed?

**Every one of them: ruled.** Each was fired at input, not read.

## Q-014 (i) — a PRESENT but MALFORMED trailer must FAIL. **AS RULED.**

End-to-end, not at unit level: a real commit made in a clone carrying
`Session-Token: WG-2026-09-01-NOT-EIGHT-HEX`, then `check-roles`:

```
[FAIL] E5 malformed Session-Token trailer
       MALFORMED and NOT on the dated exception list: 4098e2a carries
       'WG-2026-09-01-NOT-EIGHT-HEX'. …The exception list holds exactly 4 SHAs and is
       not extended without an architect ruling
[ n/a] E4 …  16 commit(s) carry no trailer: […]     <- and the malformed one is NOT in it
```

E4's list did not grow, so *"carries no trailer"* now means what it says. `check-roles` exit 1.

## Q-014 (ii) — `_TOKEN_TRAILER` stays STRICT 8-hex. **AS RULED.**

`^Session-Token:\s*([0-9a-fA-F]{8})\s*$` — unchanged, and pinned by attempt 1's own probe. Fired at
six inputs: `f57e216b` ✓, `F57E216B` ✓, `f57e216` ✗, `f57e216bc` ✗, `g57e216b` ✗,
`WG-2026-08-30-CTX-13.4-A` ✗. **A NEW malformed trailer FAILS** (above).

## Q-014 (iii) — `_TOKEN_ROW` widens to `(C\d+|ARCH)` **and nothing wider**. **AS RULED.**

`^\|\s*`?([0-9a-fA-F]{8})`?\s*\|\s*(C\d+|ARCH)\s*\|\s*(BUILD|REVIEW|FIX)\s*\|`

| row | parses |
|---|---|
| `| `e210c6f5` | C0 | BUILD | … |` | ✅ yes |
| `| `0811c64a` | ARCH | BUILD | … |` | ✅ yes — the case Q-021 was about |
| `| `WG-2026-08-30-CTX-13.4-A` | ARCH | BUILD | … |` | ✅ **no** — a non-hex token in an ARCH row is still unparseable |
| `| `not-hex-token` | ARCH | REVIEW | … |` | ✅ **no** |
| `| `deadbeef` | ARCHITECT | BUILD | … |` | ✅ **no** — `(C\d+|ARCH)`, not a prefix match |

**The token group was not touched.** A forged token cannot hide behind the widened chunk cell.

## Q-014 (iv) — the exception list pinned at **exactly four**. **AS RULED, and the pin fires.**

Not read — mutated. **M27** adds a fifth entry and is killed by
`test_the_e5_exception_list_is_exactly_the_four_ctx_13_4_commits`. **M26** makes E5 treat every
malformed trailer as excepted and is killed by the E5 firing probe.

## Q-015 — the allow-list created EMPTY, adding to it Class A. **AS RULED.** See B-02.

## Q-012's rider — a test pins A4's binary-honesty sentence. **AS RULED.**

`test_a4_still_says_it_asserts_nothing_on_binary_files` (`c51bc64`) builds a fixture with one
binary and two text files and asserts on a **passing** A4 that it still says *"1 binary file(s)
this holds BY CONSTRUCTION"*, *"asserts nothing"*, *"cannot fail on"* and *"a real assertion on the
2 text file(s) only"*. Attempt 1's rider was that A4's honesty rests on a string with nothing
holding it in place. **It is held now, and it asserts the size of the set A4 really covers, not the
size of the set it walked.**

## A5's two branches — **both real, both fired, and the gap it declares is REAL**

| fixture | git's `w/` verdict | **OLD** `864c621` | **NEW** HEAD |
|---|---|---|---|
| a TEXT file carrying **0x08** (INC-13's byte) | `lf` | A3 PASS, A4 PASS, **A5 does not exist** | A3 **PASS**, A4 **PASS**, **A5 FAIL** — `byte 0x08 at offset 14` |
| **OF-01's lone CR**, `printf 'line one\rline two\nline three\n'` | `-text` | A3 PASS, A4 PASS | A3 **PASS**, A4 **PASS**, **A5 FAIL** — `1 file(s) … hold NO NUL byte` |
| the two dashboard PNGs | `-text` | — | **branch B PASSES both** — NUL present in the IHDR of each |

**A3 and A4 both PASS in both firing cases. That gap is precisely why A5 exists**, and it is why
one branch would not have done: the two holes sit on **opposite sides of git's own verdict**.
Mutants **M24** (branch T off) and **M25** (branch B off) are both killed.

### ⚠️ The gap the fix declares — verified, and judged

The fix prints, and asserts by test, that **a NUL inside a prose document is invisible to BOTH
branches**. I did not take that on trust:

```
fixture: b"A sentence that has\x00 eaten something, and nothing here can see it.\n"
git ls-files --eol (w/ side) = '-text'
A3 = PASS      A4 = PASS      A5 = PASS
```

**The claim is true.** A NUL makes git call the file binary at any size, so branch T never sees it
and branch B *accepts* it as the very signal it looks for. A prose file with an eaten sentence goes
green through all three A checks.

**Is printing it sufficient? Partly — and the reason given for not closing it does not survive.**
Printing a limit is the right instinct and it is done well: the limit is in A5's own output, where
a future reader cannot skip it, and a test pins the sentence. But A5's stated reason is that
closing it *"needs a judgement about which paths are prose, which is a second copy of a decision
this check deliberately takes from git."* **It does not.** The set of tracked files git classifies
as binary is, today, **exactly two dashboard PNGs**. Pinning that set closes the gap with **no**
judgement about prose and **no** second copy of git's heuristic — the verdict still comes from
`git ls-files --eol`, compared against an explicit list. It is the same instrument this project
already uses three times: `TRIPWIRE_SELF_EXCLUSION` pinned at 1, `NULL_IS_A_VALUE` at 2,
`E5_EXCEPTIONS` at 4. **Finding F-21.** I added it as a kept probe, which detects it in `make test`;
wiring it into `check-roles` is a fix session's, exactly as attempt 1 did for OF-01 before A5
existed.

---

# 4. The MEDIUMs — and the OF-09 decision the prompt asks for

## OF-03 — A2…A5 emitted as `n/a`. **VERIFIED CLOSED.**

| | **OLD** `864c621` | **NEW** HEAD |
|---|---|---|
| `.gitattributes` deleted | `FAIL A1 .gitattributes exists` — **and nothing else from the A group at all** | `FAIL A1 .gitattributes content` · `n/a A2` · `n/a A3` · `n/a A4` · `n/a A5`, each *"not evaluated — .gitattributes is missing; see A1"* |

**And INC-07's other half, which OF-03 did not state, is real and is fixed:** the old code emitted
A1 under the check name `A1 .gitattributes exists` on the failing branch and `A1 .gitattributes
content` on the passing one — reproduced above, in the two cells. A caller's lookup by name raised
`KeyError` instead of reporting a failure. **A1 now keeps one name on both branches.**

## OF-06 — blank values. **VERIFIED CLOSED, and the `tpd: null` exclusion is intact.**

The scenario `config.py`'s own docstring names, applied: `void_threshold_breach_rate:` left blank.

| | **OLD** `864c621` | **NEW** HEAD |
|---|---|---|
| `require('probe.void_threshold_breach_rate')` | **returned `None`** — no refusal | **raises `BlankValue`** |
| F2 | `PASS  5 explicit TODO_ sentinel(s)` — the void threshold simply gone from the count | **`FAIL`** — 5 declared sentinels **plus** *"⚠️ AND 1 BLANK value(s), which are NOT declared and are a hard-rule-9 defect"* |

Blanks are counted under `BLANK_`, deliberately **separate** from `TODO_`: a sentinel is a
declaration with an owner, a blank is an omission with nobody's name on it, and one heading for
both would relabel a defect as a plan. Correct, and it is the distinction OF-06 was about.

**The exclusion is intact and the count is unchanged.** `blank_marker(0)`, `blank_marker(False)`
and `blank_marker([])` all return `None` — supplied values, still passing, which is the classic way
hard rule 9 is got wrong. `NULL_IS_A_VALUE` holds exactly `{('lanes','tpd'), ('lanes','reserved_from')}`
and is pinned at two. **`tpd: null` is not broken, no `BLANK_` marker appears in the shipped
config, and F2's count is still 6.** Mutant **M29** removes the null refusal and is killed.

## OF-10 — one group's exception cannot silence another. **VERIFIED CLOSED.**

Fixture: a non-UTF-8 byte in `.gitattributes`.

| | **OLD** `864c621` | **NEW** HEAD |
|---|---|---|
| output | a bare `UnicodeDecodeError` traceback, **zero check output**, exit 1 | `FAIL A! this check GROUP raised and did not run — UnicodeDecodeError: … raised at check_roles.py:<line>` |
| the secret scan | **silenced** | **`PASS B1` · `PASS B2` · `PASS B3` · `PASS C1` all still printed**, and D, E, F all ran |

Also confirmed in the wild: under the non-editable install, `B/C` and `E` both raised
(`not a git repository`) and were **each reported by name**, while `R`, `A`, `D` and `F` all still
produced their checks. Mutant **M31** is the R1 half and is killed.

## OF-01 — the lone CR. **VERIFIED CLOSED** by A5 branch B (§3).

## OF-02 — the mutation finding. **VERIFIED CLOSED by this review's own run.**

Attempt 1: 12 of 19 survivors, closed to 17/19 by its probes, **M15 deliberately left alive** and
M20 proved equivalent. **M15 is killed** — by all four B-02 attack-form probes at once. Thirteen
mutants aimed at code that did not exist at attempt 1 are **all killed**, and the control survives.
Full table, and an honest statement of what is *not* claimed, in
`docs/reviews/mutants/c0_mutants.md`.

## ⚠️ OF-09 — the half-closure. **MY DECISION: it is a MEDIUM, not a BLOCKER. It stays OPEN, with a deadline.**

The prompt asks me to decide, and records that this defect **fooled the reviewer for one
experiment** at attempt 1. Here is the decision and every step of the reasoning, so it can be
overruled.

**What is closed, measured:** `check-roles` prints `ROOT EXAMINED` and `CONFIG DIR` at the top and
at the bottom, and **`R1 the examined root IS this repository` FAILS** — with the cause and the
remedy in its detail — over a directory holding no `.git` and no `config/`. Under `pip install .`,
`check-roles` exits 1 and `tasks test` exits 1. The thing that fooled the reviewer — a *green*
report over the wrong directory — cannot happen in either target.

**What is not closed, measured:** `check-prereg` still prints `config/ holds 0 file(s):` and exits
**0** over the venv's `Lib`, naming no root, and `tasks eval` carries that and exits **0**.
`tasks.py` was outside the FIX session's scope fence, and the fix said so rather than rounding up.

**Why MEDIUM and not BLOCKER — four reasons, and the fourth is the one that decides it.**

1. **Attempt 1's own grading.** B-03's headline was the F group's **false statement** — the word
   `PASS` beside *"protocol.yaml and lanes.yaml parse"* over a file never opened. That is gone.
   The `check-prereg` sentence appears in B-03's body **with an explicit cross-reference: "See also
   F-12"** — and attempt 1 graded **F-12 MEDIUM**, where it became OF-09. I am applying the
   predecessor review's own severity to its own residue, not inventing a lower one.
2. **No printed statement is false.** `check-prereg` says, in its own words, *"This is not a PASS;
   it is 'not yet'."* Its exit 0 is also its **correct** pre-freeze value in the real repository,
   so the exit code carries no PASS claim in either direction today. What is wrong is the
   *attribution* — it blames C14 for an absence caused by the wrong root — which is E4's old sin,
   and attempt 1 ranked that MEDIUM too.
3. **The remedy exists and is proven to fire.** `check_examined_root` is built, is red on exactly
   this condition, and is killed-when-disabled by mutant M31. What is missing is **calling it from
   three more entry points** — a wiring gap of a few lines, not an absent capability. That is a
   materially different object from a check that cannot go red, which is what all four of attempt
   1's BLOCKERs were.
4. **Hard rule 9's clause is not yet in force.** The rule is that `check-prereg` *"recomputes
   them"* — the SHA-256 of every `config/` file's git blob against `PROTOCOL.md`. **`PROTOCOL.md`
   does not exist**, `prereg-v1` does not exist, and C14 writes both. There is nothing to
   recompute, so there is nothing yet being silently skipped.

**And the condition under which it becomes a BLOCKER, written down now so it is not rediscovered
on a run day:** ⚠️ **the moment `PROTOCOL.md` exists, `check-prereg` exiting 0 over the wrong root
is a pre-registration verification that silently did not happen** — hard rule 9's actual clause,
failing open, inside `make eval`, whose entire published claim is that every number regenerates.
**OF-09 must be closed before C14 is reviewed.** I have written that deadline into its row.

## OF-11 — `import a, b`. **Half verified closed.** The `ast.parse` walk sees every alias, and
`test_the_walk_sees_import_forms_a_single_capture_group_missed` is one of the five tests that kill
M15. `importlib.import_module(…)` remains open and is not closeable by parsing imports; the row
already says so.

---

# 5. Findings

Severity key: **BLOCKER** — cannot PASS with it open. **MEDIUM** / **LOW** — goes to
`OPEN_FINDINGS.md`. **INFO** — recorded here only.

## **BLOCKER: none.**

---

## F-19 · MEDIUM · a PRESENT but MALFORMED **row** is treated as ABSENT, and E prints no row denominator

**Citation.** `CLAUDE.md` hard rule 11 (*"no silent denominator shrinkage"*); `CONTEXT.md` §14
(*"judging fails open and rules fail closed"*), which is the ruling **Q-014 (i)** applied to the
commit side of E's input and which the table side never received.

**Reproduced.** The same violation as B-01 — one token as a chunk's BUILD and as its REVIEW — with
one cell written in a spelling `_TOKEN_ROW` cannot read. All measurements on HEAD,
`__file__` → `…\new\src\whetstone_gate\__init__.py`.

| the second row | E2 | E3 | |
|---|---|---|---|
| `| `deadbeef` | C0 | REVIEW | … |` *(control)* | **FAIL** | **FAIL** | caught |
| `| `deadbeef` | C0 | review | … |` — lower case | PASS | PASS | ❌ **missed** |
| `| `deadbeef` | C0 | RE-REVIEW | … |` | PASS | PASS | ❌ **missed** |
| `| `deadbeef` | C0 (re-review) | REVIEW | … |` | PASS | PASS | ❌ **missed** |
| `| `deadbeef0` | C0 | REVIEW | … |` — 9 hex | PASS | PASS | ❌ **missed** |

E1's detail prints *"18 issued row(s) covering 18 token(s) parsed from QUESTIONS.md"* and **never
prints how many rows the table holds**, so the two numbers cannot be reconciled by a reader. A3, A4
and A5 each reconcile their denominator out loud — `65 text + 2 binary + 0 non-regular = 67
tracked`. **E does not**, and E is the group whose input is hand-typed by every session.

⚠️ **`role.upper()` is applied after a match on `(BUILD|REVIEW|FIX)`, so it is dead code** — the
intent to be case-insensitive is in the source and the regex does not implement it. That is the
lower-case row above.

**Why MEDIUM and not BLOCKER, measured rather than assumed.** The common shape of this mistake
**fails closed** through E1. A token recorded *only* in a malformed row and then used on a commit:

```
[FAIL] E1 no commit carries an UNISSUED token
       FORGED/UNISSUED: {'beefcafe': ['9a98e65']} — not present in QUESTIONS.md ## Session tokens
```

The open case is narrower: a token recorded **once well-formed and once malformed under a second
role**. E2 and E3 now fire on well-formed input, which is what B-01 was about; no printed statement
is false today; and the one row that does not parse today is the one Q-014 (iv) forbids reshaping.

**Kept probe added:** `test_every_row_of_the_session_tokens_table_parses_except_the_one_named_exception`
— supplies the missing reconciliation as an assertion and pins the unparseable set at one.
Demonstrated red on a nineteenth unparseable row and green on the clean tree.

**The remedy is E5's, one level up:** a permissive row pattern applied only where the strict one
did not match, feeding a check that FAILS and names the row.

## F-20 · MEDIUM · `_issued_tokens` reads all of `QUESTIONS.md`, so a row quoted in prose becomes an issued token

**Citation.** `PROCESS.md` §7a — the `## Session tokens` **table** is the record.

`_TOKEN_ROW.findall(questions.read_text(...))` is applied to the whole file. Any line at column 0
shaped like a row is read as an issue, wherever it sits. **Measured on HEAD:**

```
appended to QUESTIONS.md, far outside the table, inside prose:
    | `facefeed` | C7 | REVIEW | 2026-09-01 |
=>  facefeed is treated as ISSUED: True -> {('C7', 'REVIEW')}
```

**This is a false-negative path for E1** — the one clause of §7a attempt 1 found working. A token
that was never issued becomes issued by being *written about*.

**It is not hypothetical.** Q-021's body carries such a line **today** —
`| `da356dbb` | C3 | BUILD | 2026-08-31 |`, quoted as the proposed remedy — and it is invisible to
the parser **only because it happens to be indented by two spaces**. Remove that indentation in a
future edit and the row silently becomes an issuance. The project's own record of *"a habit is not
a guardrail"* (INC-16, the fifth of its class) is the argument for closing it mechanically.

**Kept probe added:** `test_the_issued_token_table_is_read_from_the_whole_file_not_from_the_table`,
written as a **detector, not a lock** — it asserts today's behaviour and its failure message names
the remedy and tells the fix session to delete the assertion and record the closure.

**Remedy:** scope the parse to the section between `## Session tokens` and the next heading.

## F-21 · MEDIUM · A5's declared NUL-in-prose gap is real, and the reason given for not closing it does not survive

Full evidence and reasoning in §3. The gap is verified (`A3 PASS, A4 PASS, A5 PASS` over a prose
file with an embedded NUL). The stated blocker to closing it — *"a judgement about which paths are
prose"* — is not required: pinning the set of tracked files git calls binary (today **exactly two**)
closes it, takes the verdict from git as A5 already does, and is the same instrument the project
already uses three times.

**Kept probes added:** `test_no_tracked_file_is_binary_outside_the_named_screenshot_set` and
`test_the_binary_set_pin_catches_what_A5_branch_B_lets_through` (parametrised over the NUL case and
OF-01's lone CR). Demonstrated red on a lone-CR file added to a clone, green on the clean tree.
The probe asserts that **A5 currently passes** on the NUL case, so it stands over a measured gap
rather than a hypothesis, and it tells a fix session to update it when A5 learns to see one.

**Severity.** MEDIUM, not LOW: it silences **all three** A checks at once, on a document, in a
project that has recorded **five** occurrences of a byte being eaten on the way to disk (INC-06,
INC-10, INC-12, INC-13, INC-16) — and `INCIDENTS.md` INC-10's `Missing` field is exactly this.

## F-22 · LOW · `test_every_target_prints_the_root_it_examined` exercises exactly one target

The test calls `check_roles.run(repo_root)` and asserts on its output. **It never touches
`check-prereg`, `test` or `eval`** — the three targets OF-09 says are still open, and the three a
`check_roles`-only assertion cannot see. Its name says *every target*.

In a chunk whose entire failure mode is checks that claim more than they check, a **test name** that
does so is worth a line. It also actively obscures OF-09: the row honestly says the finding stays
open, but a later reader greps the suite, finds a green test called *every target*, and concludes
otherwise. Rename it to what it asserts (`…run_prints_the_root_it_examined`), or widen it; either
closes this.

---

## I-01 · INFO · `make test` no longer runs green from a clean clone — and it is **not** C0's

Measured in a fresh clone with `PYTHONPATH` set to it: **8 failed, 12 collection errors**, all
twenty inside `tests/test_c3_tau2_enumeration.py`, which needs `vendor/tau2-bench` — git-ignored
under **Q-010** and therefore absent from any clone.

C0's done-when box says *"`make test` **and** `python -m whetstone_gate.tasks test` both run green
from a clean clone"*, and today they do not. **The breakage is C3's, not C0's**: attempt 1 verified
that nothing in `tests/` imported the vendored tree, and C3's tests now do. It is recorded here
because (a) the box is on C0's card and a future reader will look for it here, and (b) it is
**exactly the consequence attempt 1 predicted** when it raised Q-010's unruled Class A default as
**F-11 → OF-08**: *"it moves a whole dependency out of the artefact a judge clones… It needs a
ruling before C19's clean-clone test."* **That ruling is now overdue, and the cost of not having it
is measurable.** Not carried as a new OF row — OF-08 already carries it, and the C3 review owns the
tests.

## I-02 · INFO · one test is red in the live suite, and it is C1's

`tests/test_c1_review_probes.py::test_section_0_states_its_own_quoted_line_count_correctly`, landed
by the concurrent C1 review (`4cfddc0`) while this review was running, standing over C1's own
BLOCKER. **`make test` is therefore `1 failed, 222 passed, 1 skipped, 2 deselected` as a stranger
runs it**, and `215 passed, 1 skipped, 2 deselected` with that file excluded. Both numbers are
given in §1.3 rather than the convenient one. Not C0's, not carried.

## I-03 · INFO · no frozen artefact exists, so the frozen-artefact check is vacuous — said rather than skipped

The prompt requires that no reported figure contradicts any frozen artefact, and requires me to say
so rather than skip it. **`git tag` returns nothing: there is no `probe-v1`, no `prereg-v1` and no
`cN-pass`.** `INVARIANTS.md`, `PROTOCOL.md` and `HOLES.md` do not exist. `PROVENANCE.md`,
`RAZORPAY_SEMANTICS.md` and `config/` exist but are not yet frozen, because freezing is what a tag
does. **The check is therefore vacuously satisfied, and it is vacuous for a reason that will stop
being true at C14.**

## I-04 · INFO · two methodological traps I fell into myself, recorded because a clean transcript would have hidden both

1. The mutation harness first wrote mutants with `Path.write_text`, which translates `\n` to `\r\n`
   on Windows. **Every mutant became a CRLF defect** and was killed through A3/A4 rather than
   through its own semantics. The tell was `test_the_object_store_and_the_working_tree_agree`
   failing on mutants that touch no line-ending code. Same family as INC-06, INC-09, INC-16.
2. The first pinned run cloned from the **live** repository, which the concurrent C1 review was
   committing to. The baseline moved mid-run and **the control mutant was scored KILLED** by a C1
   probe that had just gone red. Per the prompt's own rule, that pass was **void** and was
   discarded. The source is now pinned at `68fcfff` and the whole set was re-run.

Both are in `docs/reviews/mutants/c0_mutants.md`. Neither is an `INCIDENTS.md` entry: nothing in
the repository broke, and `INCIDENTS.md` is not this session's file.

---

# 6. Mutation testing

**14 mutants: 13 real, all KILLED; 1 semantics-preserving CONTROL, SURVIVED.** Source pinned at
`68fcfff`. Baseline `171 passed, 1 skipped, 2 deselected`, `check-roles` rc=0. `PYTHONPATH` set to
each mutant's own clone and `whetstone_gate.__file__` printed for every one of the fourteen runs;
`git status --porcelain` empty on every one.

| id | mutation | verdict |
|---|---|---|
| M15 | D3 hard-wired to `shared = set()` — **attempt 1's deliberate survivor** | **KILLED** |
| M21 | the import walk stops after one hop | **KILLED** |
| M22 | relative imports no longer resolved | **KILLED** |
| M23 | `from whetstone_gate import X` no longer resolved | **KILLED** |
| M32 | the package root back in `MOAT_ALLOW_LIST` | **KILLED** |
| M24 | A5 branch T disabled | **KILLED** |
| M25 | A5 branch B disabled | **KILLED** |
| M26 | E5 excepts every malformed trailer | **KILLED** |
| M27 | a fifth entry in `E5_EXCEPTIONS` | **KILLED** |
| M28 | B-01's original defect restored | **KILLED** |
| M29 | the loader stops refusing a YAML null | **KILLED** |
| M30 | B-03's cause restored | **KILLED** |
| M31 | R1 can no longer fail | **KILLED** |
| **CTRL** | `startswith` → equivalent slice | **SURVIVED — correct** |

Every kill is by a test that **names the defect**, not by a coincidence. Full table, method, both
traps, and what is deliberately **not** claimed: `docs/reviews/mutants/c0_mutants.md`.

**One further check, aimed at the tripwire rather than at a mutant:** a file under `src/` carrying
`PER_ACTION_CAP_PAISE = 5000000` and `BALANCE = 500000000`, committed in a clone, makes
`test_no_spec_value_is_hardcoded_in_implementation_source` fail with *"hard rule 9 violation — a
CONTEXT.md §8.6 constant is hardcoded in implementation source"*. **The tripwire fires end to end,
not only in its unit fixtures.** And the §8.6 → registry direction the fix added goes red on an
untranscribed row: inserting `| a constant nobody transcribed [ADDED 31 Aug] | 4242 | §13.4 |` into
a clone's §8.6 table produces
`AssertionError: CONTEXT.md §8.6 carries constants the tripwire's registry has never heard of…`.

---

# 7. Secrets, spend, and persona 2's four additions

**Spend: ZERO.** No provider model call was made by this session. The only network operations were
`git clone` against the project's own local repository and one `pip install .` from PyPI into a
throwaway venv, which is not a provider call and spends no token budget. `evals/` still does not
exist and nothing under it is tracked.

**Secrets — clean, scanned independently rather than taken from `check-roles`.** My own scan over
**72 tracked files** against the eight `SECRET_PATTERNS` shapes plus `Authorization: Bearer …` and
`api_key = "…"`: **0 hits.** `.env` does not exist in the working tree and is not tracked;
`.env.example` carries bare names. No key value appears in this review, in
`docs/reviews/mutants/c0_mutants.md`, in the probe file, or in `docs/sessions/c0-review-2.txt`.

**Persona 2's four additions:**

* **The scorer imports no model client — asserted?** `scorer/` does not exist yet (C8). The
  assertion is C8's done-when. What C0 owes is the *mechanism*, and D1/D2/D3 correctly report
  `n/a` with the reason rather than PASS.
* **The scorer and the gates share no first-party module — asserted?** **Yes, and it now works**:
  six fixtures, five hostile and one clean, in §2's B-02 table.
* **The runner resumes across a day boundary.** C11's. Out of range.
* **No API key in any log, transcript, report or committed file.** Verified above.

---

# 8. What I could not verify

1. **That the sessions were genuinely different.** Nothing can; `PROCESS.md` §7a says so. What I
   *can* now say, and could not at attempt 1, is that **all three** of §7a's named conditions fire
   on well-formed input, and that one of them (E1) also fires on the commonest malformed input.
2. **What the two dashboard PNGs depict.** A session cannot read an image. I verified them as
   *files*: both are git-classified `-text`, both carry NULs in their IHDR, both pass A5 branch B.
3. **That no payment method is attached to either provider account.** Operator-attested; C21
   re-checks it.
4. **Whether `pip install -e vendor/tau2-bench` completes from scratch.** Outside a review's remit;
   its consequence for the clean-clone box is I-01.
5. **Attempt 1's other eighteen mutants, one for one.** Several no longer apply — the code they
   mutated has been rewritten. Stated in the mutants file rather than papered over with a combined
   score.
6. **Anything about C1–C21.** Out of range. Where C1's concurrent work touched my numbers it is
   named (I-02).

---

# 9. Disposition

**PASS.** Four BLOCKERs re-tested against attempt 1's own evidence; three closed outright and one
closed in the form that made it a BLOCKER, its residue carried at the severity attempt 1 itself
assigned it. Thirteen mutants killed, control surviving. **Zero BLOCKER findings.** No reported
figure contradicts a frozen artefact, because **none is frozen yet** (I-03).

**`c0-pass` is cut on this review's commit.**

**Carried to `OPEN_FINDINGS.md`:** **F-19**, **F-20**, **F-21** as MEDIUM and **F-22** as LOW, as
new rows. **OF-01, OF-02, OF-03, OF-04, OF-06 and OF-10 are closed** with my own OLD-beside-NEW
evidence rather than by accepting the fix session's word. **OF-05, OF-07, OF-08, OF-09, OF-11,
OF-12, OF-13 and OF-14 stay OPEN** — and **OF-09 now carries a deadline: it must be closed before
C14 is reviewed**, because from the moment `PROTOCOL.md` exists it is a pre-registration check
failing open inside `make eval`.

*This review changed no source file and fixed nothing. It added `tests/test_c0_review_2_probes.py`
(5 kept probes, all passing, each demonstrated red on the condition it detects),
`docs/reviews/mutants/c0_mutants.md` and this file. Its `SESSION-TOKEN` `f57e216b` was already
recorded in `QUESTIONS.md` by the architect's token batch; this session did not write that row, and
did not touch `QUESTIONS.md` or `INCIDENTS.md` at all.*
