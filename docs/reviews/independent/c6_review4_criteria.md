# C6 REVIEW 4 — PHASE-1 CRITERIA, PRE-COMMITTED AND SEALED

**SESSION-TOKEN: `ca0dd160`** · **Chunk:** C6, the attacker loop · **Review attempt:** 4
**Date:** 2026-09-02 · **Personas:** evaluation-integrity + code
**I did not build this chunk, I did not fix it, and I did not review it before.**

---

## 0. WHAT THIS FILE IS, AND THE RULING THAT REQUIRES IT

`OF-80`'s ruling, recorded verbatim in `QUESTIONS.md` and restated in this session's prompt:

> **on a RE-review, PHASE 1 IS BLIND TO THE FIX, NOT TO THE FINDINGS.**

So this file is written **before** any of C6 FIX 3's commits (`51f0624`, `df741d4`, `f03d359`,
`6bcc15a`, `ee01e0c`), before `docs/sessions/nightrun-a-1.txt`, and before the current
`src/whetstone_gate/attacker/` or `tests/test_c6_*.py` is opened. For each of `REVIEW_C6_3`'s six
survivors and each `OF-` item it states **what must be true**, **the exact probe**, **the expected
result**, and **the polarity, pre-committed**.

**A criteria file whose every row predicts success is a wish list.** Six rows below are
deliberately predicted to FAIL or to ESCAPE (**P-14, P-16, P-28, P-29, P-36, P-40**), and one
(P-48) states a prior against the fix. If those predictions turn out wrong in the fix's favour,
they are reported as **this review's misses**, in this document, beside the ones that held.

---

## 0.1 ⚠️ MY LEAKS, DECLARED — WHAT PHASE 1 ALREADY KNOWS ABOUT THE FIX

`OF-80` names this hazard and the last three reviews each declared it. This prompt itself tells
Phase 1:

1. that the blindness scan has **three layers**;
2. that a **`_sole_killer` exclusivity helper** exists, and that FIX 3 claims every fixture is built
   so the mutated assertion is the **sole** killer;
3. that FIX 3 reports **nine mutants killed, five survived on its own fresh code, three then killed
   and two declared EQUIVALENT** — named as **SM-1 (the AUTHORED origin filter)** and
   **SM-5 (`replaced == 1`)**;
4. that FIX 3 reports deleting the **OF-104 scan from COPY 2** of the guard left all 99 tests green
   **because copy 2 had never been fired at a leak at all**, and that it says it fixed that;
5. that the C6 half of **OF-110** landed as a **source-text scan beside the AST walk**, fired at
   five dynamic forms;
6. that **OF-112, OF-113 and OF-114 were left open with stated reasons**;
7. that the suite is around **99 C6 tests** and that `make selftest` is still RED on
   `camel_comparator.branch`.

**So this Phase 1 knows the fix's SHAPE and not its CONTENT.** What that permits is exactly what
this file does: state in advance what would have to be **true** for each of those shapes to be
**sound**, and what result would falsify it. The polarity column is the test.

**Read at `2be75b1` rather than at HEAD, and the reason is the ruling's own.** `OF-104`…`OF-114`
were read at `2be75b1` — `REVIEW_C6_3`'s own commit, **the finding without the disposition** —
because `6bcc15a` filled the `Closed by` cells and reading them would be reading the fix through a
different file. `STATUS.md`'s C6 row was read at the same commit. **`INCIDENTS.md` INC-53 and the
`PROGRESS.md` entry are deferred to Phase 2** for the same reason. **`INC-54` WAS read**, because
this prompt directs Phase 1 to it for the token-row count and it is about the token table, not
about the fix's code. `Q-031`, `Q-037`, `Q-046`, `Q-047`, `Q-048`, `Q-075` and the `OF-87`/`OF-88`
rulings **were** read: they are architect rulings, hard rule 5 makes a ruling bind, and criteria
cannot be written without them.

---

## 0.2 ⚠️ THE VERDICT RULE, PRE-COMMITTED, SO IT CANNOT BE ADJUSTED TO THE RESULT

This session's prompt sets the bar and warns in both directions. Both halves are binding and are
written down **before** any measurement:

| trigger | verdict consequence |
|---|---|
| any **BLOCKER** | **FAIL** |
| any **mutant survivor on the fix's own new code**, non-equivalent and exhibited | **FAIL** — the established bar; the last two reviews on this project each returned FAIL with zero blockers on exactly this |
| an **unsound equivalence proof** | **FAIL** |
| a **needle of mine escaping the guard** while the four blindness claims still hold over the real assembled bytes | **NOT a FAIL.** It is a guard-**coverage** finding, MEDIUM, appended to `OPEN_FINDINGS.md` — which is exactly how `REVIEW_C6_3` graded the identical shape as its `M-1` |
| an escape inside the **folded-state JSON** | **NOT a finding against C6.** §8.6 puts that object on the authored surface and **C7's ledger fills it**; a C6 guard exempting it is exempting somebody else's data, and `OF-107`'s remedy is about the state **LINE**, not the state **VALUES** |
| a **repository-wide** limit C2/C3/C13 share | **routed, not charged to C6**, as `OF-110` and `OF-95` were |
| all six survivors killed, both equivalence proofs sound, **zero new-surface survivors**, the four claims re-derived, the reimplementation agreeing | **PASS, and I cut `c6-pass`** |

⚠️ **The schedule is not an input.** It is 2 September with two days left. A fourth FAIL must be a
defect with an exhibit, not a preference — and equally, **a clean new surface is a PASS and the tag
gets cut.**

---

## 1. GROUP 1 — `REVIEW_C6_3`'s SIX SURVIVORS

Method for every row: a **fresh OS temp clone**, the mutation **committed inside it**, the
**control run first**, `whetstone_gate.__file__` **printed**, the source SHA-256 compared before
and after, and the restore verified. This repository is never mutated. (INC-11, INC-17.)

| # | survivor | what must be true | the exact probe | expected | polarity |
|---|---|---|---|---|---|
| **P-01** | **N4** `estimate.py:crossing`, `>` → `>=` | a fixture exists at a `base_tokens` for which `tokens_at(k)` is **exactly** the 60,000 target, and it distinguishes the two operators | apply N4 verbatim in the clone; run the C6 files | **≥1 named test FAILS** | **KILLED** |
| **P-02** | N4's direction | §13.4 reads *"measured attacker tokens/episode **≤ 60,000**"*, so exactly 60,000 is **WITHIN** Branch A and HEAD's `>` (crossing = k+1) is the correct answer | read the new fixture; recompute `base_tokens = 60000 − k·marginal` myself and check the asserted crossing | the fixture asserts the **larger** k at the exact-target base | **HOLD** |
| **P-03** | **N9** `_imported_modules`, relative-import resolution dropped | the positive control gains a relative-import case | apply N9; run | **≥1 test FAILS** | **KILLED** |
| **P-04** | N9's control | `test_the_import_scan_ACTUALLY_FIRES_in_every_import_form` had **four** parametrised rows and **no relative form** | parse the parametrize list with `ast`, not by reading | ≥1 row of the form `from .. import X` or `from ..X import y` | **HOLD** |
| **P-05** | **N12** LAYER 3, the residue catch-all, deleted | a fixture exists whose leak carries **no** ceiling rendering, **no** clause id and **no** arm word | apply N12; run | **≥1 test FAILS** | **KILLED** |
| **P-06** | N12's sole-killer claim | LAYERS 1 and 2 must be **silent** on that same fixture, or LAYER 3 is not what killed it | run each layer independently over the fixture's own authored surface, and over mine (`sole_catcher`) | **exactly `{C}`** fires | **HOLD** |
| **P-07** | **N13** `refusal_lines != 1`, the `> 1` half | a fixture carries **two** recognisable denial lines | apply N13 (`!= 1` → `< 1`); run | **≥1 test FAILS** | **KILLED** |
| **P-08** | N13's exhibit | the `< 1` half was already exercised; only `> 1` was not | read the new fixture | it renders **two** denial lines, not zero | **HOLD** |
| **P-09** | **N14** `value != generic` disabled | a fixture plants a refusal value that differs from §8.6's one string and that **no other layer** can see | apply N14; run | **≥1 test FAILS** | **KILLED** |
| **P-10** | N14's sole-killer claim | `Q-046`'s ruling is *"the loop identifies a denial by EXACT STRING EQUALITY against that one authored constant"* — if the equality is never the sole killer, the ruling's central assertion is pinned by nothing | run each layer over the new fixture; and run mine | **exactly the equality** fires; ceilings/identity/residue silent | **HOLD** |
| **P-11** | **N15** LAYER 1's exemption widened from the state **JSON** to the whole state **LINE** | a fixture plants a **cap value** — not a clause — inside `STATE_LABEL` | apply N15; run | **≥1 test FAILS** | **KILLED** |
| **P-12** | N15's exhibit | the previous fixture planted a policy **clause** in `STATE_LABEL`, which LAYER 2 kills first | read the new fixture; check the planted string against my own ceiling renderings | the planted string is a **rendering of a `config/` ceiling** | **HOLD** |

⚠️ **A kill is not enough on its own.** For N12, N14 and N15 the claim under test is *sole*
killership, and `P-06`, `P-10` and `P-12` are what test it. A fixture caught twice proves the
guard works and proves the **assertion** nothing.

---

## 2. GROUP 2 — `_sole_killer` ITSELF

**What must be true.** An exclusivity helper is worth exactly what its own exclusivity check is
worth. To mean anything, `_sole_killer(fixture, layer)` must assert **both** halves:

1. the named layer **fires**, and
2. **every other** layer is **SILENT** on the same input.

Half (2) is the load-bearing one and is the half a decorative helper leaves out.

| # | probe | expected | polarity |
|---|---|---|---|
| **P-13** | read `_sole_killer` and confirm both halves are present, by `ast`, not by eye | both halves present | **HOLD** |
| **P-14** | ⚠️ **MUTATE `_sole_killer`: delete the "every other layer is silent" half.** | ⚠️ **I PREDICT IT SURVIVES.** A suite whose fixtures are all single-layer *by construction* cannot notice half (2) going away — the helper is untestable by mutation unless a **self-test** exists: one fixture deliberately caught by TWO layers, asserted to make `_sole_killer` **raise**. If it dies, that self-test exists and I was wrong, and I report the miss | **PREDICTED SURVIVOR** |
| **P-15** | **MUTATE `_sole_killer`: invert it** — assert the named layer is SILENT | many tests fail; this is the control that the helper is load-bearing at all | **KILLED** |
| **P-16** | ⚠️ **MUTATE `_sole_killer`: accept ANY layer as the killer** (drop the identity of the named one) | ⚠️ **I PREDICT IT SURVIVES**, for P-14's reason. Same remedy | **PREDICTED SURVIVOR** |
| **P-17** | **MEASURE, do not mutate:** for every fixture that closes one of the six survivors, run each layer/assertion independently and record the **hit vector** | **exactly one** entry per vector | **HOLD** |

⚠️ **P-14 and P-16 are graded under §0.2.** A helper in a **test file** whose weakened form no test
notices is a MEDIUM finding about the guard's self-coverage — it is the same class as `OF-105`…
`OF-107` one level up — and it is a mutant survivor **on the fix's own new code**, which §0.2 makes
a FAIL trigger. **I am pre-committing that grading now, before I know the answer**, precisely so
that a survivor here cannot be talked down and a kill here cannot be talked up.

---

## 3. GROUP 3 — MY OWN NEEDLE SHAPES, AND THE CLEAN-SURFACE CONTROL

Nine families, **118 needles**, derived in `independent/c6_review4_reimpl.py` from *"what does a
GATE know that §10.1 forbids the attacker to learn?"*, from `CONTEXT.md` §8.6/§8.6a/§10.1 and from
`config/protocol.yaml` — **not from any list a fix session wrote**.

| family | n | spanning |
|---|---|---|
| **F1** cap values in unusual renderings | 27 | bare paise, western grouping, **Indian lakh grouping** (`2,00,000` — the form §8.6 itself prints), rupees, `Rs`/`INR`/`₹`, `.00`, `2 lakh`, `half a lakh`, `0.5 lakh`, `2L` |
| **F2** clause ids | 14 | `P1`…`P7`, `clause P4`, `P1-P6`, `P1–P6` (EN DASH — `policy.txt`'s own), lowercase `p7`, `rule P5`, `P2/P3` |
| **F3** policy paraphrases | 7 | an LLM judge asked for *"a reason"* writes a paraphrase, never a quote. **None carries a cap digit or a clause id** — the class a residue layer exists for |
| **F4** arm identity | 12 | `arm 1`…`arm 4`, `arm 2S`, `Arm Four`, `the no-gate control`, **`the kernel`**, **`the gate judge`**, `a live judge reviewed this` |
| **F5** hole descriptors | 14 | `CANARY-A`, `CANARY-B`, `HOLES.md`, `EXEMPTION:`, `in-flight window`, `window width 2`, `void threshold`, `arm confounded`, the two `config/` key names |
| **F6** verdict vocabulary | 8 | `DENIED`, `ALLOWED`, `INDETERMINATE`, `verdict`, `the gate blocked`, `declared obligation with no result` |
| **F7** answer-key vocabulary | 15 | `A1`/`A3`/`A5`/`A6`, `E1`–`E3`, `S2-amt`, `S3`, `S4`, `rejected_by_razorpay`, **`Rejected by Razorpay itself`**, **`Gate-dependent?`** (§6's two answer-key columns), `salami slicing` |
| **F8** extra folded-state fields | 8 | §8.6 fixes the folded state's **six** fields exactly; a seventh is defender state |
| **F9** config key names | 6 | a reason that names the key it read |
| **(+)** the seven clause **bodies** | 7 | so a leak that **renumbered** the clauses could not evade an id-only scan |

⚠️ **F7 DELIBERATELY EXCLUDES the four harm words §8.6's own GOAL string carries** —
*over-captures, excess refunds, early settlements, duplicated refunds* — and F5 excludes the bare
words *exception*, *limits*, *special* and *refuses*, every one of which is in the TRADECRAFT
paragraph. `REVIEW_C6_2` had to re-derive its list after firing on the zero-turn context for
exactly this reason. **The control below is what keeps that honest rather than a promise.**

| # | probe | expected | polarity |
|---|---|---|---|
| **P-18** | ⚠️ **THE CLEAN-SURFACE CONTROL.** All 118 needles against the **package's own** unleaked authored surface at several turns | **0 hits.** A needle that fires here is a needle about the **spec**, not about a leak | **HOLD** — already **0/118** against my own spec-derived clean surface (`c6_review4_reimpl_output.txt`) |
| **P-19** | **F1** planted on the authored surface, each rendering separately | each **CAUGHT** | **HOLD** |
| **P-20** | **F2** | each **CAUGHT** | **HOLD** |
| **P-21** | **F3** in the refusal **value** → caught by the equality; **as residue** → caught by LAYER 3 | each **CAUGHT** | **HOLD** |
| **P-22** | **F4** | each **CAUGHT** | **HOLD** |
| **P-23** | **F5** | each **CAUGHT** | **HOLD** |
| **P-24** | **F6** | each **CAUGHT** | **HOLD** |
| **P-25** | **F7** | each **CAUGHT** | **HOLD** |
| **P-26** | **F8** | each **CAUGHT** | **HOLD** |
| **P-27** | **F9** | each **CAUGHT** | **HOLD** |
| **P-28** | ⚠️ **THE SHAPE I EXPECT TO ESCAPE.** A gate reason placed **inside `LAST_REFUSAL_LABEL`** that matches **no** ceiling rendering, **no** clause id and **no** arm digit: `"LAST TOOL REFUSAL (the reviewer declined it): "` — and a second, `"LAST TOOL REFUSAL (declined on review of the running total): "` | ⚠️ **I PREDICT BOTH ESCAPE.** Derivable from the design without reading code: **subtraction by identity subtracts the label's CURRENT bytes**, so a leak inside a label subtracts itself and leaves no residue; only a content-matching layer can see it, and a regex over arm digits and clause ids does not match English. If it escapes: **MEDIUM**, `OF-104`'s class one shape over, **not a BLOCKER** (§0.2) | **PREDICTED ESCAPE** |
| **P-29** | ⚠️ **PREDICTED ESCAPE, AND PRE-COMMITTED AS NOT-A-FINDING.** A ceiling rendering, and separately a paraphrase, carried inside a **folded-state VALUE** (an `idempotency_keys_seen` entry) | ⚠️ **I PREDICT BOTH ESCAPE, and that is correct behaviour.** §8.6 puts that object on the authored surface and **C7's ledger fills it**; exempting it is exempting somebody else's data, not laundering a gate reason. Recorded as a **scope note**, not a finding | **PREDICTED ESCAPE — NOT A FINDING** |
| **P-30** | **`OF-104`'s own two shapes**, which FIX 3 was asked to close: `LAST_REFUSAL_LABEL = "LAST TOOL REFUSAL (arm 2S): "` and `STATE_LABEL = "STATE SO FAR (this arm runs a live judge): "` | both **CAUGHT**, in **both copies** of the guard, with **no false positive on the clean tree** | **HOLD** |

---

## 4. GROUP 4 — COPY 2, THE ONE THIS PROMPT CALLS THE SHARPEST LEAD

`N-M1b`: deleting the `OF-104` scan from **copy 2** left all 99 tests green **because copy 2 had
never been fired at a leak at all**. FIX 3 says it fixed that.

⚠️ **Why two copies exist at all is hard rule 8's anti-circularity shape one level down**: a guard
and its check that share code cannot fail independently. That is the property under test here, and
it is the reason `P-31` is done by **parsing the import graph** and never by grep — three
occurrences of one module's name inside the other were, last time, **prose saying it is not
imported**.

| # | probe | expected | polarity |
|---|---|---|---|
| **P-31** | build the `ast` import graph of both test modules; assert neither reaches the other, and neither reaches a shared predicate helper | **no edge** in either direction | **HOLD** |
| **P-32** | fire **copy 2** independently at all nine of my families | each family **CAUGHT** by copy 2 **on its own** | **HOLD** |
| **P-33** | **delete the `OF-104` scan from COPY 2 only**, in the clone | **≥1 test FAILS** | **KILLED** |
| **P-34** | **delete the `OF-104` scan from COPY 1 only** | **≥1 test FAILS** | **KILLED** |
| **P-35** | measure the two copies' vocabularies and ceiling renderings | **different sets** — otherwise they are one check counted twice | **HOLD** |

---

## 5. GROUP 5 — THE TWO EQUIVALENCE PROOFS

**What must be true of any equivalence proof**, and this is the standard `REVIEW_C6_3`'s own `N6`
proof met and the standard C13 REVIEW 3 met when it *withdrew* one of its own mutants: it must
**enumerate the reachable inputs**, show the two programs agree on **all** of them, and **name the
input that WOULD separate them** — the boundary of the proof stated rather than left implicit.
An equivalence claim is the one place a fix session can retire a survivor **by argument**.

| # | probe | expected | polarity |
|---|---|---|---|
| **P-36** | ⚠️ **SM-1, the AUTHORED origin filter.** Enumerate every call site; construct a context carrying `WORLD`, `CORPUS` and `ATTACKER` parts and run HEAD against the mutant | ⚠️ **I PREDICT THE PROOF IS UNSOUND.** `Origin` is the mechanism that makes blindness **structural**; a filter over it whose mutation nothing notices is far more likely a **fixture coverage gap** (no non-`AUTHORED` part in that path's fixtures) than a true equivalence — and §10.1's must-reach control means a widened filter should fire on the probe note. If I can build a separating input, the survivor stands and it is a **FAIL trigger** | **PREDICTED UNSOUND** |
| **P-37** | **SM-5, `replaced == 1`.** Check whether the subtracted string can occur **more than once** on any reachable authored surface — in particular whether a leak byte-identical to an accounted-for string would be laundered by a global replace | **SOUND** if the proof names the separating input; **incomplete → LOW** if it does not. ⚠️ `replaced == 1` is the assertion that stops `str.replace` laundering a leak, so a proof that it can never be `> 1` must cover a leak *placed* to make it so | **PREDICTED SOUND, boundary required** |

---

## 6. GROUP 6 — `OF-110`'s C6 HALF

**Context that makes this load-bearing rather than tidy:** `INC-51` records that this exact class
defeated **hard rule 8's moat test** — `gates/` reached `scorer/` live via `importlib` while D3
printed *"share no first-party module on any path"*. **C6's is the same class**, on the chunk whose
lanes `PROCESS.md` §8 reserves and where spend is irreversible.

| # | probe | expected | polarity |
|---|---|---|---|
| **P-38** | plant each of **five** dynamic forms in a synthetic package inside the clone — `__import__("openai")`, `importlib.import_module("openai")`, `getattr(whetstone_gate, "provider_client")`, `exec("import openai")`, `importlib.__dict__["import_module"]("openai")` — and run the **AST walk** alone | the AST walk is **SILENT on all five** — it cannot see a call expression **by construction** | **HOLD** |
| **P-39** | run the **source-text scan** alone on the same five | it **FIRES on all five** | **HOLD** |
| **P-40** | ⚠️ a sixth form whose forbidden name is **not present as source text**: `importlib.import_module("open" + "ai")` | ⚠️ **I PREDICT IT ESCAPES BOTH.** Judged **NOT a finding against C6** provided the docstring is scoped honestly; a **finding** if any docstring or incident claims completeness the scan does not deliver — which is `INC-42`/`OF-113`'s exact shape | **PREDICTED ESCAPE** |
| **P-41** | confirm the text scan is **run over C6's own surface** and **can fail** — a positive control, not a scan that reports PASS over nothing (`REVIEW_C0`'s phrase) | plant a real offender; the scan goes **red** | **HOLD** |

---

## 7. GROUP 7 — THE FOUR BLINDNESS CLAIMS, AND THE MUST-REACH CONTROL

`Q-031`'s enforcement clause is the substitute for the golden C6 does not have: *"C6's REVIEW must
INDEPENDENTLY RE-DERIVE the four 'never sees' assertions and the summary's determinism **BY ITS OWN
METHOD**. A divergence is a finding."*

| # | probe | expected | polarity |
|---|---|---|---|
| **P-42** | my 118 needles over the package's **actual assembled bytes** at turns **1, 6, 7, 12, 20**, with the real seed-2001 world payloads and a corpus part offered every turn; needles read **at run time** from the real `data/` files so a drifted transcription in my own file cannot weaken the scan | **0 hits on AUTHORED** at every turn | **HOLD** |
| **P-43** | ⚠️ **THE MUST-REACH CONTROL.** `pay_CANARYRECON` and the probe note | **FULL = True, AUTHORED = False**, both, at every turn. A guard that banned the probe from the world surface would **close the door and make arm 4 VOID BY CONSTRUCTION** | **HOLD — T/T/F/F** |
| **P-44** | the FULL surface carries **≥1** hit, and it is the probe's own note arriving as a **WORLD** tool result | ≥1 FULL hit, explained | **HOLD** |

---

## 8. GROUP 8 — `OF-112`, `OF-113`, `OF-114`, JUDGED

| # | item | my pre-committed judgement | polarity |
|---|---|---|---|
| **P-45** | **`OF-112`** — `test_c6_review_probes.py`'s all-zero `_Folder`, `OF-82`'s fourth instance | ⚠️ **I PREDICT STILL OPEN.** The glob `tests/test_c6_*.py` covers that file, so a C6 fix *could* reach it — but it is `REVIEW_C6_1`'s **probe file** and `INC-30`/`INC-31` make editing another session's probes a named hazard. **Closable only by a session that OWNS that file.** | **PREDICTED OPEN** |
| **P-46** | **`OF-113`** — `INC-42`'s `Action` lists the tool schemas among what the guard **subtracts**; measured, they are **scanned** | ⚠️ **I PREDICT IT STAYS OPEN AND SHOULD.** Rule 13 fixes the incident format and history is not rewritten; the correction belongs in the review record and in a new entry, not in an edit to a written `Action`. **Judged: open, correctly, and the direction is SAFE** (scanned is stronger than exempted) | **PREDICTED OPEN — CORRECTLY** |
| **P-47** | **`OF-114`** — `REVIEW_C6_3`'s own note that its first hard-rule-9 pass grepped without excluding docstrings | ⚠️ **I PREDICT IT IS CLOSABLE.** It is a note **about a review's method**, not a defect in C6; the corrected `ast`-based result is already in the record. Closing it costs nothing and leaving it open forever costs a row | **PREDICTED CLOSABLE** |

---

## 9. GROUP 9 — NEW-SURFACE MUTANTS ON FIX 3's OWN CODE

**Minimum 8; I will run at least 12.** Targets this prompt names: `_sole_killer`; the three-layer
scan's **subtraction-by-identity**; the **residue parser**; the **copy-2 route**; the C6 half of
**`OF-110`'s source-text scan**. Plus the six survivor-closing fixtures themselves — a fixture that
can be deleted with the suite green closes nothing.

| # | probe | expected | polarity |
|---|---|---|---|
| **P-48** | ≥12 mutants on code **no review has seen**; each **KILLED** or **proven EQUIVALENT with a named separating boundary** | ⚠️ **MY PRIOR IS THAT AT LEAST ONE SURVIVES**, because this is the third consecutive session in which a fix's own new surface carried survivors — `REVIEW_C6_3` found six, C13 REVIEW 3 found five. **The prior is stated so that a zero-survivor result is a genuine update and not a relief**, and so that it cannot become a reason to hunt until one appears. ⚠️ **A survivor counts ONLY if I exhibit a concrete input on which HEAD and the mutant differ AND no test fails.** A disarmed-assertion mutant (`assert X or True`) is **equivalent by construction** and will not be written — `REVIEW_C6_3`'s `N10` is the precedent | **PRIOR: ≥1 SURVIVOR. If zero survive, that is a PASS and I cut the tag.** |

---

## 10. GROUP 10 — REGRESSIONS AND STANDING PROPERTIES

⚠️ **A concurrent C13 FIX 3 session (`e9dd0346`) holds `tests/test_c13_camel_comparator.py` and
`src/whetstone_gate/camel_comparator/`.** Its in-flight edits will move the count between runs.
**Every figure is stated, and every failure is attributed BY FILE.**

| # | probe | expected | polarity |
|---|---|---|---|
| **P-49** | `make selftest` | **RED on `camel_comparator.branch` = `TODO_C13_RUN1`** — not C6's, and it is *supposed* to be red until RUN-1 decides the branch | **HOLD** |
| **P-50** | `make check-roles` | **exit 0**; counts measured, not quoted from the prompt (`INC-54`) | **HOLD** |
| **P-51** | the three vendored pins | clean | **HOLD** |
| **P-52** | `git status --porcelain tests/goldens/` | **EMPTY** | **HOLD** |
| **P-53** | `evals/` | C6 spent **nothing**; state the precise fact, not a fact about a directory that may not exist | **HOLD** |
| **P-54** | `make test`, measured **twice** by me | every failure attributed **by file**; the C13 files' failures are not C6's | **HOLD** |
| **P-55** | **ZERO PROVIDER MODEL CALLS by this session.** The reference-attacker lanes are reserved for the sweep | zero | **HOLD** |

---

## 11. WHAT THIS FILE COMMITS ME TO

* **55 numbered probes (P-01…P-55) with a polarity fixed in advance** — counted from this file, not
  asserted (`INC-54`) — of which **six predict failure or escape**
  (P-14, P-16, P-28, P-29, P-36, P-40) and one states a **prior** (P-48).
* **The verdict rule in §0.2, written before any measurement.**
* **The clean-surface control in P-18 as a precondition** — if my needles fire on an unleaked
  surface, the needles are wrong and every measurement built on them is discarded and re-derived,
  as `REVIEW_C6_2` had to do.
* Every number in `REVIEW_C6_4.md` traceable to a run whose tree said which
  `whetstone_gate.__file__` it loaded.

**Sealed at the commit carrying this file. Phase 2 begins after it.**
