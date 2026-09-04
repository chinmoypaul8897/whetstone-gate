# RESULTS.md — ⚠️ PARTIAL. NO RESULT IS PUBLISHED HERE, BECAUSE NO RUN HAS PRODUCED ONE.

⚠️⚠️ **READ THIS BOX BEFORE ANYTHING ELSE. THIS IS NOT THE RESULTS DOCUMENT.**

**This file exists for exactly one reason:** `PROCESS.md` §14 says *"a cut item is never silently
lost: it is named in `RESULTS.md` and in the README as **not run**, with why."* **Four degradation
rungs have fired and this file did not exist**, so that requirement was unmet on rungs 1, 3 and 5
since 2026-09-02 and on rung 4 since 2026-09-04. **This file discharges §14's `RESULTS.md` half and
nothing else.**

**What is in it:** the four fired cuts, in the words the record requires. **What is NOT in it:** any
escape rate, any harm figure, any false-positive delta, any arm comparison, any ladder cell, any
token table, any void determination, any `check-prereg` PASS/FAIL line — **because none of them has
been measured, and a number no run produced must not appear in a file named `RESULTS.md`.**

| | |
|---|---|
| **Created by** | `ARCH PUBLISH 1`, session token `2e5b8a47`, role FIX, 2026-09-04 |
| **Owner of the real file** | **C18** (`PROCESS.md` §12). C18 has **not run** |
| **How the real file is produced** | `make eval` / `python -m whetstone_gate.tasks eval`, which writes `RESULTS.md` **from stored ledgers** — `src/whetstone_gate/tasks.py:202` |
| **What happens to this file** | ⚠️ **It is OVERWRITTEN, in place, the first time `make eval` succeeds.** That is intended: this is a transitional stub, not a draft of C18's output |
| **Today `make eval` refuses** | there is no run directory — `evals/results/` does not exist |

⚠️ **AND THE REASON THIS FILE IS AS SHORT AS IT IS, STATED RATHER THAN LEFT TO INFERENCE.**
`src/whetstone_gate/results/__main__.py`'s own docstring says: *"IT WRITES TO STDOUT BY DEFAULT, NOT
TO `RESULTS.md`. `RESULTS.md` **is written by the run**, and a build session that created one would
be publishing numbers no sweep produced."* **That instruction is obeyed here: this session created a
file containing no number a sweep would have produced.** The cuts below are declarations with dates
and incident numbers, not measurements.

⚠️ **THE DEGRADATION RECORD IN THE REAL FILE IS PARSED, NOT TRANSCRIBED.**
`src/whetstone_gate/results/degradation.py` **reads `PROTOCOL.md` §5.1's rung table** rather than
carrying a copy, and refuses on anything but six rows. **`PROTOCOL.md` §5.1 already carries rung 4 as
FIRED**, so when C18 assembles the real `RESULTS.md` the cut below is republished from the frozen
artefact automatically. **This stub is the interim, not the mechanism.**

---

## 1. THE DEGRADATION LADDER — EVERY CUT NAMED

**`PROCESS.md` §14, verbatim:** *"When the schedule slips, cut in this order. Record every cut in
`INCIDENTS.md` at the moment it is made, with the time, the rung, and the reason. A cut item is never
silently lost: it is named in `RESULTS.md` and in the README as **not run**, with why."*

**State of the ladder, as recorded in `PROTOCOL.md` §5.1 — a frozen artefact, which outranks this
file (hard rule 4):**

| Rung | Cut | State |
|---|---|---|
| **1** | Collapse a `code`-review chunk into its neighbour's review — C15's ladder harness into C18's, C20's video into C21's | ⚠️ **FIRED** 2026-09-02, 08:10 IST = 02:40 UTC. `INC-61` |
| **2** | The L2 ladder cell stays at n=5 instead of 20 | **NOT FIRED** |
| **3** | **C16 / AD-CMP, the AgentDojo comparator — 80 episodes** | ⚠️ **FIRED** 2026-09-02, 08:10 IST = 02:40 UTC — **C16 IS NOT RUN.** `INC-62` |
| **4** | **T-FP 40 → 20 τ² tasks** | ⚠️ **FIRED** 2026-09-04, 05:27 UTC. `INC-144` |
| **5** | Downgrade C17's and C19's reviews from `full` to `code` | ⚠️ **FIRED** 2026-09-02, 08:10 IST = 02:40 UTC. `INC-63` |
| **6** | C13 / CaMeL live run → Branch B citation | **NOT FIRED** |

**Four fired: 1, 3, 4 and 5. Two not fired: 2 and 6.**

---

## 2. THE WORDS EACH CUT IS PUBLISHED IN

⚠️ **Every row below is carried VERBATIM from the record that fired it.** `PROCESS.md` §14's own
table fixes the words for rungs 1, 3 and 5; `INCIDENTS.md` `INC-144` fixes the words for rung 4, and
says why it fixes them there: *"THE EXACT WORDS `RESULTS.md` AND `README.md` MUST CARRY, WRITTEN HERE
BECAUSE BOTH FILES ARE OUTSIDE THIS SESSION'S FENCE AND §14 SAYS A CUT ITEM IS NEVER SILENTLY LOST."*
**Nothing here is reworded, softened or improved.**

| what | where §14 requires it | the words |
|---|---|---|
| **C16 / AD-CMP, 80 episodes** | `RESULTS.md` **and** `README.md` | **NOT RUN** — degradation rung 3, fired 2026-09-02 08:10 IST. The second external environment is lost; **τ²-bench remains, so the externally-authored-answer-key claim is intact.** `INCIDENTS.md` `INC-62` |
| **C15's and C20's `code` reviews** | `RESULTS.md` | **FOLDED** into C18's and C21's reviews — rung 1, `INC-61`. Neither publishes a number |
| **C17's and C19's review type** | `RESULTS.md` | **DOWNGRADED** `full` → `code` — rung 5, `INC-63`. Neither publishes a number |
| **T-FP, the τ² false-positive block** | `RESULTS.md` **and** `README.md` | **REDUCED — 40 τ² write tasks → 20, stratified 10 airline / 10 retail.** Degradation rung 4, fired by the operator 2026-09-04 05:27 UTC, on **schedule**, and **not** by `CONTEXT.md` §13.4's decision rule, whose input the pilot never produced (`INC-142`). The surviving 20 are the **first 10 ids per domain** under the same bytewise-ascending string sort that selected the 40, so they are an **exact prefix** of the pre-registered sample and nothing was substituted in. ⚠️ **τ²-bench is NOT cut** — `PROCESS.md` §14 and `CONTEXT.md` §21.4 both forbid dropping it, and **only the breadth of this one block is staged**; the T-NEG must-not-write control keeps all 34 tasks and **the externally-authored-answer-key claim is intact**. The false-positive sample is halved, so the paired FP delta is reported on **n=20 per configuration, 100 episodes**, and every table caption states that cell size. `INCIDENTS.md` `INC-144` |
| **The counter-metric** | `RESULTS.md` | **NOT cut.** §14's never-cut list keeps the benign solver and the paired FP delta — *"a project that publishes only what it blocked has published half a result"*. Rung 4 **narrows** it; it does not remove it |

---

## 3. ⚠️ RUNG 4 — THE THREE THINGS A READER MUST NOT GET WRONG

**These are not additions to the words above.** They are the three misreadings the record itself
names, restated here because this is the file a reader who greps `tau2` or `T-FP` will land in.

### 3.1 ⚠️ τ²-BENCH IS **NOT** CUT. ONLY ONE BLOCK'S BREADTH IS STAGED.

`PROCESS.md` §14's *"NEVER CUT, at any rung, for any reason"* list **opens** with τ²-bench, and
`CONTEXT.md` §21.4 says of it *"**It is never dropped.**"* — adding, in the same sentence, that its
**scope** is staged. §14's own never-cut row spells the distinction out: *"τ²-bench — the external
answer key; spec §21.4 says 'never dropped', and **only its breadth is staged**"*.

**What rung 4 reduces is the BREADTH of ONE block — T-FP, the false-positive block — from 40 tasks to
20. The comparator itself, the external answer key, and the T-NEG must-not-write control (all 34
tasks, untouched) remain.** **The externally-authored-answer-key claim — the project's thesis — is
UNAFFECTED.**

**A staged breadth is not a dropped comparator**, and that sentence is here, in the file a reader who
greps `tau2` lands in, rather than in a footnote.

### 3.2 ⚠️ WHAT FIRED IT WAS THE OPERATOR, ON SCHEDULE. **THE MEASUREMENT DID NOT CHOOSE THIS CUT.**

**Two instruments can order this same reduction and only one of them fired.**

- **`CONTEXT.md` §13.4's decision rule** fires on the pilot's **measured** attacker tokens/episode.
  ⚠️ **Its input does not exist.** The pilot completed **0 of 20** episodes; `select_n` returned
  **`USABLE TO SELECT N: False`**; `config/protocol.yaml`'s `n_decision.selected_branch` is still
  `TODO_C14_PILOT`. `INCIDENTS.md` `INC-142`.
- **`PROCESS.md` §14 rung 4** fires on **schedule**, at the operator's decision. ⚠️ **That is the one
  that fired** — 2026-09-04, 05:27 UTC, recorded in `INC-144` at the moment of the cut.

⚠️ **NOTHING IN THIS REPOSITORY MAY SAY THE PILOT SELECTED THIS CUT, AND NOTHING DOES.** The reason
that sentence is written so flatly is `QUESTIONS.md` **`Q-099`**: a previous session's prompt asserted
that rung 4 had already fired when it had not, and that session **stopped rather than transcribe it
into a frozen artefact**. **A cut attributed to a measurement that never happened is the same defect
wearing better clothes.**

### 3.3 ⚠️ AT THE COMMIT THAT CARRIES THIS FILE, THE CUT IS **DECLARED AND RECORDED** AND **NOT YET EXECUTED IN `config/`** — AND IT IS BEING EXECUTED AS THIS IS WRITTEN

**This is a fact about a moving tree, so it is stated against a named commit rather than against
"today".** The list the code actually reads is `config/protocol.yaml`'s `selections.tfp_task_ids`,
with `selections.tfp_task_count` and `selections.tfp_stratification` beside it. `config/` is a
pre-registration artefact and the session that fired the rung was fenced out of it (`INC-144`,
`INC-146`), so it declared the cut and could not execute it.

| | |
|---|---|
| **At `HEAD` = `3f07907`**, measured by this session with `git show HEAD:config/protocol.yaml` | `tfp_task_count: 40` (line 421), stratification `{airline: 20, retail: 20}`, twenty ids per domain |
| **In the working tree at the same moment**, measured with `git diff -- config/protocol.yaml` | ⚠️ **`tfp_task_count: 20`, `{airline: 10, retail: 10}`, ten ids per domain — an UNCOMMITTED edit held by a CONCURRENT session (`8f3c72e1`)**, executing exactly the ids printed below |

⚠️ **SO A READER WHO GREPS `tfp_task_count` GETS ONE OF TWO ANSWERS DEPENDING ON WHEN THEY LOOK, AND
THIS PARAGRAPH IS HOW THEY TELL WHICH.** ⚠️ **AN EARLIER VERSION OF IT SAID `git log -1 --
config/protocol.yaml` SETTLES IT. THAT WAS WRONG, AND WRONG IN EXACTLY THE STATE THIS PARAGRAPH
EXISTS FOR: `git log` CANNOT SEE A WORKING TREE.** While the edit was uncommitted, `git log` returned
an older commit and a reader would have concluded the cut had not landed — with `tfp_task_count: 20`
sitting in the file in front of them. **Read the value, not the history:**

```
grep -n 'tfp_task_count' config/protocol.yaml     # the number the code actually reads
git status --porcelain config/protocol.yaml       # non-empty => uncommitted, git log will mislead
```

**This session did not make that edit and may not — `config/` is outside its fence** — and it reports
the edit rather than claiming or omitting it. ⚠️ **It has since landed, at `c5a83fd`.**
(`README.md`'s own STATUS box set this precedent for `ledger.genesis_hash`: a value *"changing as
this was written"* is named, not smoothed.)

⚠️⚠️ **AND ONE CONSEQUENCE OF THE CUT THAT NOTHING HERE HAD DISCLOSED, FOUND BY THIS SESSION'S OWN
ADVERSARIAL PASS AFTER IT HAD ALREADY PUBLISHED THE CUT.** `selections.tfp_task_count` is **not read
only by the T-FP block**: `src/whetstone_gate/runner/n_rule.py:441` reads it —
`tfp_tasks = int(protocol.require("selections.tfp_task_count"))` — so **`select_n`, the N decision
rule, consumes the value rung 4 changes**, and executing the cut mechanically moves that rule's own
projections. ⚠️ **The coupling runs the opposite way to the one §3.2 is careful about.** §3.2 says
the decision rule **did not fire the cut**, which is true. **What was unsaid is that the cut moves
the decision rule.** No published number is wrong because of it and no branch flips — it is a
**disclosure gap**, disclosed here because the coupling lives in code and no grep for the forbidden
*sentence* would have found it. **Any republished N projection must state the T-FP size it was
computed at.**

**The execution is owed as ONE ATOMIC ACT, before `prereg-v1`,** because the tests re-derive from the
config: `INC-144`'s **Fix** field names the three test sites that pin 40 and `PROTOCOL.md` §1.1's
manifest digest for `config/protocol.yaml` must be **re-measured, never copied**. ⚠️ **After
`prereg-v1` none of it is legal**, and §14 rung 4 then requires the block to be published as
**incomplete with its denominator**, never as a re-registration.

**The twenty ids that survive** — derived, not chosen. ⚠️ **`CONTEXT.md` §13.4 CONTAINS TWO RULES AND
ONLY ONE OF THEM IS IN PLAY HERE, SO IT IS QUOTED RATHER THAN CITED BY SECTION NUMBER.** §3.2 above
denies that §13.4's **decision rule** — *"Otherwise N = 30, and if the projection at N=30 still
exceeds 32 h, T-FP is cut from 40 to 20 τ² tasks"* — fired. What the twenty ids come from is §13.4's
**selection rule**, a different sentence in the same section: *"**T-FP** takes the **first 40
write-task ids after sorting, stratified 20 airline / 20 retail.**"* ⚠️ **Citing "§13.4's rule" for
both, forty lines apart in one file, would let a reader join the denial to the derivation and read
the measurement as having chosen the cut** — which is the exact thing `Q-099` exists about. **The
selection rule, evaluated at K=20, under `PROTOCOL.md` §3.2's bytewise-ascending string sort within
each domain separately:**

```
airline (10) : 11 12 14 15 16 17 18 19 20 21
retail  (10) : 0 1 100 101 102 103 104 105 106 107
```

**Each is an EXACT PREFIX of that domain's pre-registered 20.** Nothing entered the sample that was
not already in it; ten ids leave the tail of each domain. **A prefix cut is not a re-registration**,
which is the precise hazard §14 names for a cut made *after* the tag — and this one was made
**before** it, which §14 says to do *"if at all possible"* for exactly this reason.

---

## 4. ⚠️ THE VISIBLE CONSEQUENCE OF RUNG 3, NAMED SO IT IS NOT READ AS A DEFECT

`PROCESS.md` §14, verbatim: *"`vendor.agentdojo_sha` stays at its sentinel and the loader **keeps
raising**. **Do not report that as a defect, and do not edit `config/` to resolve it** — `config/` is
a pre-registration artefact (hard rule 9, §6a). **Report it as the visible consequence of a published
cut.** A reader who greps `agentdojo` must find the cut, not a mystery."*

**`config/protocol.yaml`'s `vendor.agentdojo_sha` reads `TODO_C13_C16` and the loader raises on it.
That is rung 3, and it is the correct end state.**

---

## 5. WHAT IS **NOT** IN THIS FILE, AND WHO OWES IT

**`PROCESS.md` §12's C18 card lists what the real `RESULTS.md` publishes. None of it is here, because
none of it has been measured.** Named rather than omitted:

the five-arm trade-off table · the **reach** column · **CONFOUNDED** flags · the four harm components
as per-episode medians with IQR, never summed · the paired-Δ false positives · the void determination
· the turn-indexed escape curve (1→20) · escape conditioned on probe reach · the τ² DB-hash write rate
labelled explicitly as a negative control · CaMeL's P1–P3 predictions scored against the result · the
S2-vs-S2-amt FP delta · the productive-actions confound · the corpus-vs-improvisation split · the
per-model token table · the `check-prereg` PASS/FAIL line.

⚠️ **AND THE VOID DETERMINATION IS NOT MERELY UNMEASURED — IT IS NOT COMPUTABLE TODAY, ON ANY INPUT.**
`config/protocol.yaml`'s `probe.void_threshold_breach_rate` is the explicit sentinel
`TODO_C14_CALIBRATION` and the loader **raises** rather than defaulting. The single-shot arm-1
calibration that would set it **has not run**. `README.md` §7 and `HOLES.md` §3 carry the rule; this
file carries the fact that its threshold does not yet exist.

**There is no VOID banner on this file. A VOID is a determination made about a run, and there is no
run.** If a run happens and voids, `HOLES.md` §4 fixes exactly what is published, and the banner goes
at the top of both this file and `README.md`.

---

<sub>`ARCH PUBLISH 1` · `Session-Token: 2e5b8a47` · 2026-09-04 · **UNREVIEWED**, like every commit that
has not been through a fresh adversarial review. Nothing in this file is self-certified and no tag was
cut for it.</sub>
