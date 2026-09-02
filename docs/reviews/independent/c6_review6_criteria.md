# C6 REVIEW 6 — PHASE 1, SEALED. Criteria, the OWNED-PROPERTY SET, and the mutant plan.

**SESSION-TOKEN: `7f4b0e93`** · **Date:** 2026-09-02 · **Role:** REVIEW, attempt 6 (C6's last)
**Personas:** 1 (evaluation integrity) + 2 (code).
**I did not build this chunk, I did not fix it, and I have not reviewed it before.**

---

## 0. WHAT PHASE 1 READ, AND WHAT IT DID NOT

`OF-80`, as this session's prompt restates it: **PHASE 1 IS BLIND TO THE FIX, NOT TO THE FINDINGS.**

**READ** — `CLAUDE.md`; `docs/reviews/README.md`; all three `docs/personas/`; `PROCESS.md` §5.3 and
§12.1's C6 card; `CONTEXT.md` §8.6 in full, §8.6a, §10.1, §10.2, §13.3, §13.4, §11.3, §9.1/§9.2;
`QUESTIONS.md` Q-046, Q-047, Q-048, Q-082, Q-084, Q-085; `docs/reviews/REVIEW_C6_5.md` in full;
`docs/reviews/OPEN_FINDINGS.md` `OF-146`…`OF-156`; `data/policy.txt`, `data/attacker_sys.txt`,
`data/generic_denial.txt`; `config/protocol.yaml`; `git tag -l`.

**NOT READ AT THIS SEAL** — anything under `src/` or `tests/`; `git diff` of any C6 FIX 5 commit;
`INCIDENTS.md` INC-70/71/72 (they are FIX 5's own journals and describe the fix); the
`OPEN_FINDINGS.md` disposition block headed *"DISPOSITION BY C6 FIX 5"*; `PROGRESS.md`;
`docs/sessions/c6-fix-5.txt`.

**`STATUS.md` was read for WHICH CHUNKS ARE TAGGED AND NOTHING ELSE** — `OF-145`, as the prompt
directs. The review-history column of C6's row narrates every build round and would leak the fix, so
the tag set was taken from `git tag -l` instead: `c0-pass c1-pass c13-pass c2-pass c3-pass c4-pass`.
**Neither `probe-v1` nor `prereg-v1` is cut**, so no reported figure of C6's can contradict a frozen
artefact.

### 0.1 THE LEAKS THIS PROMPT ITSELF CARRIES, DECLARED

A re-review's prompt necessarily names what the fix attempted. Declared, so that nothing below reads
as independent that is not:

1. FIX 5 closed *"all five cells"* and reports `git diff -- src/` empty per commit.
2. A survivor of FIX 5's own mutation is named — **`SM-7`**, *"disarming `if len(summaries) != 1:`
   left all 134 tests green"*. So Phase 1 knows the suite is now ~134 C6 tests and that a locator of
   that shape exists in copy 2.
3. `Q-084` ACCEPTED and `Q-085` REJECTED are carried in the prompt and are recorded in
   `QUESTIONS.md`; both were read.
4. `docs/reviews/mutants/c6_mutants_6.md` is owed and FIX 5 named the debt.

**Phase 1 knows the SHAPE of the fix and not its CONTENT.** The pre-committed polarities in §5 are
written so that a wish list is impossible: several predict SURVIVAL or ABSENCE.

---

## 1. THE BAR THIS REVIEW APPLIES, FIXED BEFORE ANY MEASUREMENT

### 1.1 `Q-084`, ACCEPTED — and it REPLACES the gate, it does not merely extend it

> *"THE GATE IS EVERY OWNED PROPERTY PINNED, NOT EVERY MUTANT KILLED. Mutants are the INSTRUMENT,
> not the definition."*

Operationally, for every property in §2 this review asks **two** questions and both must answer yes:

* **(a) DOES A CATCHER EXIST**, in every copy of the guard the chunk owns? An absent catcher is the
  strongest form of unpinned and produces **no mutant at all**, so it is asked directly and first.
* **(b) IS THE CATCHER FIRED** — does deleting or disarming it meet a red test?

**A property failing (a) or (b) is a FAIL.** `Q-085` is REJECTED, so *"another test happens to cover
it"* is not an answer to either, and the `E1`/`E2` duplication bound REVIEW 5 measured is **not**
available as an argument for doing less.

### 1.2 The OWNED / NOT-OWNED rule, fixed here so it cannot be chosen after the result

A property is **OWNED** iff it satisfies **all three**:

1. **It is stated in a clause I can quote** — from `CONTEXT.md`, `PROCESS.md` §12.1's C6 card, or a
   RULED `QUESTIONS.md` entry. Not from the code, which Phase 1 has not read.
2. **The clause is about C6's subject** — the attacker loop, its context, its corpus, its estimator,
   or the four blindness claims. A property whose owner is another chunk is NOT-OWNED here even if
   C6's tests happen to touch it.
3. **The mutation changes behaviour on an input the property's own statement reaches.** A mutant that
   differs only on a state no code path can construct is EQUIVALENT, and one that differs only on a
   layout that does not exist is NOT-OWNED.

⚠️ **Clause 4, binding against my own convenience:** *if I can quote the clause, the property gates.*
**Schedule, this being C6's last review, effort, and the chunk's history are NOT arguments.** The
prompt's own sentence is adopted verbatim as this review's rule: *do not pass because this is the
last review, and do not fail to avoid deciding.*

### 1.3 What a PASS requires — the list, fixed now

1. `git diff -- src/` across FIX 5's commits is **EMPTY**, verified by me.
2. The five cells — `M-12`, `M-16`, `M-12d`, `M-39`, `M-RES` — re-run by me, **each KILLED**.
3. Each of those fixtures **exercises what it claims** (see §4's fixture-honesty tests).
4. **`SM-7` re-run and KILLED**, and the one-level-out question answered: is there any other locator
   in either copy whose failure mode is *inspect nothing silently*?
5. Every property in §2 **PINNED** — (a) present in every owned copy and (b) fired — with every
   survivor killed or proven equivalent.
6. The four blindness claims re-derived **by my own method, my own needle shapes**, with a
   CLEAN-SURFACE control and the MUST-REACH control. **REVIEW 5's 110 needles are not reused.**
7. A **POSITIVE CONTROL** that must die (`OF-159`), in the same harness, in the same subprocess.
8. My scoped reimplementation agreeing on ≥20 vectors.
9. **ZERO BLOCKERS.**

---

## 2. ⚠️ THE OWNED-PROPERTY SET, AS SEALED — nineteen properties

**Each is stated with the clause that makes it owned.** Phase 2 may **ADD** a member; it may
**NEVER REMOVE** one. Under §1.1 each carries both questions.

| # | OWNED PROPERTY | THE CLAUSE THAT OWNS IT | copies it must hold in |
|---|---|---|---|
| **OP-1** | **The sliding window is the last 6 turns VERBATIM**, its width read from `config/`, steady beyond 6 | C6 card: *"the sliding-window context (last 6 turns verbatim …)"*; §13.3; §8.6 row *attacker context window - verbatim turns = 6* | source |
| **OP-2** | **The summary is a pure DETERMINISTIC template, never an LLM call**; byte-identical for identical state; exactly one model call per turn | C6 card done-when: *"the summary is byte-identical for identical state (proving it adds no request…)"*; §13.3 *"produced DETERMINISTICALLY … not by an LLM call"* | source |
| **OP-3** | **The 400-token cap is INCLUSIVE and pinned BOTH ways** — at the cap kept, one over truncated | §8.6 row *attacker context summary cap 400 tokens*; `OF-87` | source |
| **OP-4** | **Truncation RESERVES the denial**; a denial that alone exceeds the cap is a HARD REFUSAL, never a silent drop | §13.3 *"concatenates the running folded state … with the last denial reason"*; hard rule 11; `OF-88` | source |
| **OP-5** | **BLINDNESS LAYER 1 — the structural-label scan, state JSON exempt** | C6 card: *"the attacker's context provably contains no policy string, no hole, no attack list and no gate reason"* | **copy 1 AND copy 2** |
| **OP-6** | **BLINDNESS LAYER 2 — the defender VOCABULARY scan and the VERBATIM POLICY-CLAUSE scan** | same clause (*"no gate reason"*, *"no policy string"*) | **copy 1 AND copy 2** |
| **OP-7** | **BLINDNESS LAYER 3 — the RESIDUE catch-all**: nothing authored is left over that the spec did not mandate. The only layer that sees authored text carrying **no policy word at all** | same clause; `OF-106`; `OF-150` | **copy 1 AND copy 2** |
| **OP-8** | **The denial pair — EXACT string equality against the one authored constant, and EXACTLY ONE denial line** | `Q-046` RULED Class A: *"THE LOOP THEREFORE IDENTIFIES A DENIAL BY EXACT STRING EQUALITY AGAINST THAT ONE AUTHORED CONSTANT"* | **copy 1 AND copy 2** |
| **OP-9** | **The exclusivity helper** — a fixture must be about ITS OWN catcher; a shape two layers catch must be rejected | `INC-43` / `ai-playbook` B.9 as the project applies it; `SM-B`'s history | both helpers |
| **OP-10** | **MUST-REACH, both directions.** The probe note reaches the WORLD surface **in every arm**; it is **never** written onto the AUTHORED surface; **a global ban must FAIL an assertion** | §10.1 *"Every arm leaves it open — including the kernel… arm 4 is VOID by construction"*; `Q-046` *"Do not 'fix' the guard by banning it globally"* | **copy 1 AND copy 2** |
| **OP-11** | **The corpus selection rule** — stratified over all four corpora, round-robin by turn, a deterministic function of (episode seed, turn index); byte-identical from the same seed; arms sharing a seed get identical offers | `Q-047` RULED Class A, verbatim | source |
| **OP-12** | **The token estimator, and the chars-per-token divisor resolved THROUGH THE LOADER** — never a module-level eager read, never a literal | `Q-048` RULED Class A; hard rule 9 | source |
| **OP-13** | **The crossover series: `≤ 60,000` is a CLOSED bound**, so the crossing is the first point **STRICTLY** over and a series landing exactly ON the target has none; the range is pinned at **both** ends including `turn_budget` | §13.3 *"Pre-registered target: ≤ 60,000"*; §13.4's decision rule *"IF … is ≤ 60,000"* | source |
| **OP-14** | **The dynamic-import scan** — an import hidden behind `importlib`/`__import__` is caught, not only a static one | hard rule 8; `OF-110`'s C6 half | source |
| **OP-15** | **`attacker_sys.txt` is VERBATIM §8.6**, and the AUTHORED-SURFACE INVENTORY is exactly what the spec mandates and nothing else | C6 card: *"`attacker_sys.txt` verbatim from spec §8.6"*; `Q-046`'s consequence clause | source |
| **OP-16** | **The structural no-gate-object property** — the loop holds no gate object and imports no gate; that is what makes claim 4 structural rather than asserted | `Q-046`: *"No gate object is needed, so the structural argument that makes claim 4 hold is PRESERVED INTACT"* | source |
| **OP-17** | ⚠️ **NEW, MINE.** **The folded constant's PROVENANCE:** the loop folds `data/generic_denial.txt`, and that file is character-identical to §8.6's string. **The seam between "the string parsed out of `CONTEXT.md`" and "the string read from `data/`" is where a drift hides** — `OF-147` names it, and it is a property, not a fixture detail | `Q-046`: *"read from `data/` and never inlined"*; §8.6's generic-denial paragraph | source + **copy 2** (copy 1 cannot see it by construction) |
| **OP-18** | ⚠️ **NEW, MINE.** **The corpus-vs-improvisation split is INSTRUMENTED and its denominator does not silently shrink** — every turn is classified, and a turn with no offer is counted rather than dropped | C6 card: *"the corpus-vs-improvisation split instrumented"*; §11.3 *"Report the split"*; hard rule 11 | source |
| **OP-19** | ⚠️ **NEW, MINE, AND IT IS `SM-7` GENERALISED.** **No guard may silently inspect nothing.** Every locator that selects the object a guard examines must fail LOUDLY when it finds zero or more than one — otherwise the guard reports clean because it looked at nothing | hard rule 11's shape applied to a guard's denominator; `INC-43`; `Q-084`'s own argument that the unseeable failure is absence | **copy 1 AND copy 2** |

**Nineteen properties against `PROCESS.md` §5.3's minimum of eight.**

⚠️ **OP-17, OP-18 and OP-19 are this review's own additions** and are sealed here **before** any
mutant and before the fix was opened. OP-19 exists because the prompt asks the one-level-out
question and a property that is asked only in Phase 2 is a property chosen after the result.

### 2.1 Properties DELIBERATELY MARKED NOT-OWNED, sealed now so the call is not made later

| candidate | why it is NOT-OWNED here |
|---|---|
| `rglob` → `glob` on the import scan (`OF-129`) | Clause 3: differs only on a **nested package layout that does not exist**. The architect's own disposition agrees. |
| `assert len(summaries) == 1` → `>= 1` in **copy 1** (`OF-130`/`R-08`) | Clause 3 **as it applied to copy 1**. ⚠️ **BUT SEE OP-19:** if a locator of that shape exists in **copy 2** over `run_episode`'s own contexts, clause 3 no longer excuses it, because a real episode can plausibly produce zero or two summaries where a hand-assembled fixture cannot. **This distinction is drawn HERE, before measuring.** |
| the world's PRNG, the payment record, golden 7 | C2's, not C6's. |
| `FRAMING_TOKENS_PER_MESSAGE` | §8.6 says in terms it changes what the project **reports** and not one byte of what the attacker is **sent**. |
| `camel_comparator.branch` red in `make selftest` | C13/RUN-1's, and it is **supposed** to be red until the branch is decided. |

---

## 3. THE MUTANT PLAN — planned in Phase 1, by id

**Minimum ≥1 per owned property (`Q-082`'s termination condition), minimum eight
(`PROCESS.md` §5.3).** Phase 2 may add; it may not drop a planned one silently — an unrun plan row
is reported as unrun.

| id | OP | operator |
|---|---|---|
| `N-01` | OP-1 | the verbatim-window width hardcoded instead of read from `config/` |
| `N-02` | OP-1 | window width 6 → 5 |
| `N-03` | OP-2 | the summary made impure — a counter/nonce in the rendered text |
| `N-04` | OP-3 | the cap comparison `>` → `>=` (the INCLUSIVE boundary, one direction) |
| `N-05` | OP-3 | the cap comparison the other way |
| `N-06` | OP-4 | the denial's reservation removed from the truncation budget |
| `N-07` | OP-4 | the hard refusal on an over-cap denial softened to a silent drop |
| `N-08` | OP-5 | **copy 1** LAYER 1 deleted |
| `N-09` | OP-5 | **copy 2** LAYER 1 deleted |
| `N-10` | OP-6 | **copy 1** vocabulary scan deleted |
| **`N-11`** | OP-6 | ⚠️ **`M-12` RE-RUN — copy 2's vocabulary scan deleted.** REQUIRED KILLED |
| `N-12` | OP-6 | **copy 1** verbatim-clause scan deleted |
| **`N-13`** | OP-6 | ⚠️ **`M-12d` RE-RUN — copy 2's verbatim-clause scan deleted.** REQUIRED KILLED |
| `N-14` | OP-7 | **copy 1** residue layer deleted |
| **`N-15`** | OP-7 | ⚠️ **`M-RES` — copy 2's residue layer deleted.** REQUIRED KILLED. **If there is nothing to delete, `OF-150` is UNCLOSED and that is a FAIL under `Q-084`** |
| `N-16` | OP-8 | **copy 1** denial equality deleted |
| **`N-17`** | OP-8 | ⚠️ **`M-16` RE-RUN — copy 2's denial equality deleted.** REQUIRED KILLED |
| `N-18` | OP-8 | **copy 2** refusal-line COUNT loosened |
| `N-19` | OP-9 | the exclusivity helper's exclusivity half deleted |
| `N-20` | OP-9 | the exclusivity helper's identity half deleted |
| **`N-21`** | OP-10 | ⚠️ **`M-39` RE-RUN — copy 2's probe-note-on-AUTHORED check disarmed.** REQUIRED KILLED |
| `N-22` | OP-10 | ⚠️ **THE GLOBAL BAN** — the probe note banned from the WORLD surface too. **MUST DIE**; this is the mutation `Q-046` says voids arm 4 by construction |
| `N-23` | OP-11 | `Q-047`'s stride/round-robin arithmetic perturbed |
| `N-24` | OP-11 | the offer made seed-independent (coverage frozen at one slice) |
| `N-25` | OP-12 | the divisor hardcoded instead of resolved through the loader |
| `N-26` | OP-13 | `crossing()`'s strictness `>` → `>=` |
| `N-27` | OP-13 | `crossing()`'s range end moved off `turn_budget` |
| `N-28` | OP-14 | the dynamic-import scan narrowed |
| `N-29` | OP-15 | one byte changed in the authored system prompt's comparison |
| `N-30` | OP-16 | the exact-equality fold widened to containment (world text becomes foldable) |
| `N-31` | OP-17 | **`data/generic_denial.txt` drifted from §8.6** — the seam. Must die **through copy 2** |
| `N-32` | OP-18 | a turn dropped from the split's denominator |
| **`N-33`** | OP-19 | ⚠️ **`SM-7` RE-RUN — copy 2's summary locator disarmed.** REQUIRED KILLED |
| `N-34` | OP-19 | ⚠️ **THE ONE-LEVEL-OUT SWEEP** — every other locator of that shape, in either copy, disarmed one at a time |
| **`N-PC`** | — | ⚠️ **THE POSITIVE CONTROL (`OF-159`).** A mutant that MUST die by construction. **Any slice whose positive control lives, or whose post-restore control is not green, is VOID and nothing from it is reported.** |
| `N-RL` | — | **REAL LEAKS IN `src/`**, not guard mutations — the `INC-42`/M17 shape and others, to answer *is the guard fired at anything real* |

---

## 4. FIXTURE-HONESTY TESTS — sealed, because a fixture can close a cell without pinning it

A cell is closed only if its fixture **exercises what it claims**. Named checks, from the prompt and
from `Q-046`:

* **F-H1 — `OF-147`'s fixture must inject the drift at `texts.generic_denial`**, the seam
  `run_episode` actually reads. A fixture that drifts *the string parsed out of `CONTEXT.md`* pins
  nothing, because that is copy 1's route and `OF-147`'s whole point is that copy 1 cannot see this.
* **F-H2 — `OF-149`'s fixture must fire in BOTH directions**, and **a global ban on the probe note
  must FAIL an assertion.** A guard that merely bans the note everywhere voids arm 4 by construction
  and is the *"fix"* `Q-046` explicitly forbids.
* **F-H3 — every new fixture must be routed through the exclusivity helper** or otherwise shown to
  be about its own catcher, so that a fixture cannot be satisfied by a different layer firing.
* **F-H4, and it is mine:** for each of the five cells the number of findings HEAD produces on the
  exhibit must come **from the catcher under test alone** — the same *sole-layer* discipline REVIEW 5
  used on itself — measured, not assumed.

---

## 5. PRE-COMMITTED POLARITIES — 48 rows, sealed at this commit

**A prediction only means something if it can be wrong.** Rows marked ⚠️ predict failure, absence or
a survivor. Every row is scored in Phase 2 and the ones that did **not** hold are named individually,
never absorbed into a count.

| id | prediction |
|---|---|
| P-01 | `git diff -- src/` across FIX 5's commits is EMPTY |
| P-02 | `M-12` is KILLED |
| P-03 | `M-16` is KILLED |
| P-04 | `M-12d` is KILLED |
| P-05 | `M-39` is KILLED |
| P-06 | ⚠️ a copy-2 residue layer now EXISTS and `M-RES` is KILLED — **but I predict its fixture will be the weakest of the five**, because a residue assertion over a real `run_episode` context has to enumerate what the spec mandates, and that enumeration is the hardest thing in this chunk to get right |
| P-07 | `SM-7` is KILLED |
| P-08 | ⚠️ **at least one OTHER locator of `SM-7`'s shape exists** and at least one of them is unpinned |
| P-09 | the C6 suite alone in a clean clone is GREEN at some count ≥ 130 |
| P-10 | `make selftest` is RED on `camel_comparator.branch` and on nothing else |
| P-11 | `git status --porcelain tests/goldens/` is EMPTY |
| P-12 | `evals/` does not exist |
| P-13 | `make check-roles` exits 0 |
| P-14 | ⚠️ `make test` will show at least one failure attributable to a CONCURRENT session's uncommitted edits, not to C6 |
| P-15 | the four blindness claims hold: **0 AUTHORED hits** of my needles over real assembled bytes |
| P-16 | my clean-surface control fires **0** needles |
| P-17 | the probe note reaches the FULL surface on turns ≥2 and the AUTHORED surface on none |
| P-18 | `pay_CANARYRECON` DOES reach the AUTHORED surface once the fold is non-empty — **and that is NOT a finding**, for §13.3/§8.6's reason (the folded state is keyed by payment id, identically in every arm, from ids the attacker itself supplied) |
| P-19 | `N-22`, the global-ban mutant, DIES |
| P-20 | `N-PC`, the positive control, DIES in every slice |
| P-21 | my reimplementation agrees with the package on every vector |
| P-22 | ⚠️ **the label carriers still escape** — a needle carried inside a structural LABEL rather than inside the refusal VALUE escapes both copies at a rate well above zero. `OF-127`/`OF-133`'s class. **PRE-COMMITTED AS NOT THE GATE** |
| P-23 | ⚠️ text placed INSIDE the state line still escapes both copies — `OF-128`/`OF-153`'s class, and it stays open |
| P-24 | copy 1 and copy 2 import nothing from each other |
| P-25 | copy 1's guards are still never fired at a `run_episode` context |
| P-26 | ⚠️ the five new fixtures live in copy 2 and `src/` is untouched, so **no REVIEW 4 or REVIEW 5 exhibit needs re-measuring** |
| P-27 | `R-05` and `R-12` are untouched and HEAD is the stricter of each pair |
| P-28 | `N-25` (the divisor hardcoded) DIES |
| P-29 | `N-26` and `N-27` (`crossing()`'s two boundaries) both DIE |
| P-30 | `N-23`/`N-24` (`Q-047`'s arithmetic) both DIE |
| P-31 | `N-30` (the fold widened to containment) DIES |
| P-32 | ⚠️ `N-32` (a turn dropped from the split's denominator) — I predict this SURVIVES or is not constructible, because nothing in the findings suggests the split has a denominator test |
| P-33 | `N-08`/`N-09` (LAYER 1, both copies) both DIE |
| P-34 | `N-10` (copy 1's vocabulary) DIES |
| P-35 | ⚠️ `N-12` (copy 1's verbatim-clause scan) SURVIVES and is EQUIVALENT at the suite level — REVIEW 5 proved this as `M-11b` and I expect to reproduce the equivalence, not the kill |
| P-36 | `N-16` (copy 1's denial equality) DIES |
| P-37 | `N-19`/`N-20` (the exclusivity helper) both DIE |
| P-38 | `N-29` (the system prompt compared byte-wise) DIES |
| P-39 | `N-31` (the `data/` constant drifted) DIES, **and copy 2 is among its killers** |
| P-40 | `N-RL`'s `INC-42`/M17 shape DIES with ≥20 failures |
| P-41 | INC-47's test applied a fourth time across INC-70/71/72 finds **no** `Action` overstatement — ⚠️ but I record that it has fired once already (on INC-56) and that two prior sessions found nothing before the third found something, so a null result here is weak evidence |
| P-42 | INC-70 quotes INC-56's false sentence and states the measured matrix |
| P-43 | ⚠️ INC-70 will claim something it cannot prove — **I predict NO**, i.e. it claims only what it can |
| P-44 | `OF-153` stays OPEN and the measured reason (the obvious widening dying with 22 failures on a CORRECT context) holds |
| P-45 | ⚠️ my needle corpus will be SMALLER than REVIEW 5's 110 and will find the same shape of result — if mine finds a hit REVIEW 5's did not, that is a finding against the fix; if it finds none, that is agreement and not novelty |
| P-46 | ⚠️ **at least one thing in this review will be wrong in the FIX's favour.** Recorded so its absence is itself reportable |
| P-47 | the verdict will NOT be decided by anything in `src/` |
| P-48 | ⚠️ **I predict PASS is the more likely outcome and I record that BEFORE measuring**, because FIX 5 addressed the exact five cells named. **That prediction is not a commitment**, and §1.2 clause 4 governs if the measurement disagrees |

⚠️ **P-48 is deliberately uncomfortable.** A reviewer who predicts PASS and then measures a FAIL has
evidence the FAIL is real; a reviewer who predicts FAIL and delivers one has evidence of nothing.

---

## 6. THE NEEDLE FAMILIES — MINE, and NOT REVIEW 5's 110

**Derived from a different question than REVIEW 5's.** REVIEW 5 asked *"what does a defender know
that §10.1 forbids the attacker to learn?"* I ask the **inverse**: *"if a defender's knowledge had
already leaked, what is the SHORTEST string that proves it?"* — which biases towards fragments, not
sentences, and towards the forms a template would actually emit.

| family | what it is | source |
|---|---|---|
| **H1** | **clause bodies as fragments** — the distinctive noun phrase of each of P1–P7, without its id | `data/policy.txt` |
| **H2** | **the exemption discriminator and its decoy** — *exempt from transaction limits* against *standard limits apply* | §8.6a's template-4 argument |
| **H3** | **ceilings as template output** — the forms a Python f-string produces from `config/` | §8.6's constants table |
| **H4** | **verdict tokens** — `ALLOWED`, `DENIED`, `INDETERMINATE`, in the casing §8.6 fixes | §8.6's verdict-set paragraph |
| **H5** | **arm identity without a digit** — *the kernel*, *the folded state*, *the safety prompt*, *no gate* | §8.6's arm descriptions |
| **H6** | **invariant ids as bare tokens** — `E1`,`E2`,`E3`,`S1`,`S2`,`S2-amt`,`S3`,`S4` | §9 |
| **H7** | **probe machinery** — `CANARY-A`, `CANARY-B`, `reach`, `void`, `confounded` | §10.2 |
| **H8** | **`config/` key paths** as a template would print them | `config/protocol.yaml` |
| **H9** | **the folded-state field names §8.6 does NOT fix** — a seventh key would be a leak | §8.6's arm-2S JSON |
| **H10** | **gate-reason prose with no keyword and no digit** — *this was refused because of a standing rule* | the C6 card's *"no gate reason"* |
| **H11** | **attack-list vocabulary** — `A1`…`A6`, *over-capture*, *instalment*, *idempotency key* | §6/§9.2 |
| **H12** | **defender-side artefact names** — `policy.txt`, `arm3_safety.txt`, `HOLES.md`, `PROTOCOL.md` | §15.0 |

⚠️ **DELIBERATELY EXCLUDED, and the exclusion is the control's whole point:** every word that
appears in `attacker_sys.txt` itself — *limits, exceptions, special, refuses, annotations, notes,
metadata, over-captures, refunds, settlements, duplicated* — because a needle that fires on a clean
authored surface is measuring the **spec**, not a leak. **The CLEAN-SURFACE CONTROL is what makes
that checkable rather than a promise, and it is run first.**

---

## 7. THE HARNESS RULES — from `INC-69` and `OF-159`, fixed before it is written

1. **The clone environment is passed to `subprocess.run` ITSELF.** `INC-69` built an env, never
   passed it, and measured the LIVE repository while printing four True provenance lines — because
   the probe ran in a **different subprocess** from the measurement. **The provenance print and the
   measurement must be the SAME `subprocess.run` call.**
2. **A POSITIVE CONTROL rides in every slice** (`OF-159`) — a mutant that must die by construction.
   **A slice whose positive control survives is VOID.**
3. **Restore by WRITING THE ORIGINAL BYTES BACK**, never by patching the patch. **Any run whose
   post-restore control is not green is VOID** and nothing from it is reported.
4. **Every mutation runs in a fresh OS temp clone.** This repository is never mutated.
5. **The pre-run control must be green before a slice counts.**
6. **`_console.say()` or an ASCII route SET ON THE STREAM** — cp1252 is this machine's default and a
   `UnicodeEncodeError` mid-slice is indistinguishable from a failure.

---

## 8. THE SCOPED REIMPLEMENTATION — what it covers, written from spec text alone

`docs/reviews/independent/c6_review6_reimpl.py`, sealed with this file. **It imports nothing from
`src/`.** It re-derives, from `CONTEXT.md` and `config/protocol.yaml` only:

1. the **token estimator** at eight lengths, from §8.6's divisor row;
2. the **400-token cap in characters**, and the INCLUSIVE boundary either side;
3. the **6-turn window** at 0, 1, 5, 6, 7 and 20 turns;
4. **`Q-047`'s selection function**, transcribed from the ruling's five lines of arithmetic, over 20
   turns at two corpus shapes and two seeds;
5. the **crossover series** and the first point **STRICTLY** over 60,000, plus the exactly-on-target
   case which must answer **None**;
6. the **`mulberry32` → amount** chain for seed 2001 from §8.6a, as the anchor that the world payloads
   my needle measurement uses are the real ones and not something I invented.

**≥20 vectors.** Any divergence is a finding.

---

**SEALED. Phase 2 begins only after this file and the reimplementation are committed.**

---

## 9. TWO PHASE-1 CORRECTIONS, MADE BEFORE THE SEAL AND NAMED RATHER THAN SMOOTHED

The reimplementation was run before this file was committed and **three of my own vectors were
wrong**. They are corrected in the file and named here, because a seal that quietly repairs itself
is not a seal.

1. **`V39`/`V40` — mine, over-precise.** I demanded seed 2001's eight captured payments total
   **4,414,800 paise exactly**. The measured figure is **4,414,803**. §8.6a prints **rupees**
   (*"total ₹44,148"*), and `4,414,803 // 100 = 44,148`. **The spec is right and my vector carried a
   precision its sentence does not.** Re-stated to the rupee, and the paise figure is recorded
   beside it.
2. ⚠️ **`V21` — mine, and it turned into a PHASE-1 OBSERVATION about `Q-047` that is carried into
   Phase 2.** I predicted consecutive seeds would **tile without overlap**, which is the ruling's own
   claim: *"consecutive seeds **tile** each corpus without gap or overlap and coverage accumulates
   linearly across the seed set."* On a 4×5 corpus set the overlap is **total, 20 of 20** — and the
   ruling's own arithmetic says why: with `stride = turn_budget // len(corpora) = 5` and a group of
   exactly **5** entries, `within = (episode_seed * 5 + k) % 5 == k % 5` **for every seed**, so the
   seed term vanishes and coverage does **not** accumulate. At a realistic group size (124) the
   claim holds exactly — `V21b` measures 0 overlap between seeds 2001 and 2002.
   **CARRIED INTO PHASE 2 AS A QUESTION, NOT AS A FINDING:** what are the REAL per-corpus counts?
   If any corpus's entry count divides the stride, `Q-047`'s accumulation claim is false **for that
   corpus** and the corpus-vs-improvisation split is measured over a frozen slice of it.
   ⚠️ **Derived from the ruling's five lines of arithmetic and from no code**, which is what Phase 1
   is for.

**`V21` is added to the mutant plan as `N-24b`** — *is the accumulation claim true for the real
corpus sizes?* — and to the polarities as **P-49: I predict the real per-corpus counts are large
enough that the claim holds, and that this is therefore a note and not a finding.**
