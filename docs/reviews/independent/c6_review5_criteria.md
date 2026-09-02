# C6 REVIEW 5 — PHASE 1, SEALED. Criteria, the OWNED-PROPERTY SET, and pre-committed polarities.

**SESSION-TOKEN: `0ca97bbb`** · **Chunk:** C6, the attacker loop · **Attempt:** 5, after FIX 4
(`4b7f21ae`) · **Review type:** FULL · **Token row:** 50, counted from `QUESTIONS.md`'s table in the
operator's working tree at HEAD `0dfb6fb`.

**I did not build this chunk, I did not fix it, and I have not reviewed it before.**

---

## 0. THE SEAL — what was read, what was not, and the leaks declared

`OF-80`'s ruling, carried in this session's prompt: **on a re-review, PHASE 1 IS BLIND TO THE FIX,
NOT TO THE FINDINGS.**

**Read before this file was written:** `CLAUDE.md`; `docs/reviews/README.md` in full; all three
personas; `PROCESS.md` §5.3 and §12.1's C6 card; `CONTEXT.md` §8.6 in full, §8.6a, §10.1, §10.2,
§10.3, §13.3, §13.4; `QUESTIONS.md` Q-031, Q-037, Q-046, Q-047, Q-048, Q-063, Q-082 (both
renderings) and Q-083, and the `OF-87`/`OF-88` rulings; `docs/reviews/REVIEW_C6_4.md` in full;
`config/protocol.yaml`; `data/*.txt`; `corpora/seed_index.json`; `tests/goldens/`'s file list.

**`OPEN_FINDINGS.md`'s `OF-124`…`OF-135` were read AT `4100a36`** — C6 REVIEW 4's own last commit,
**the findings without their dispositions** — because the disposition column is FIX 4 speaking, and
reading it is reading the fix through a different file. This is the identical boundary
`REVIEW_C6_4` drew at `2be75b1`, and it is named here rather than left to be inferred.

**NOT read before this file was sealed:** any commit of C6 FIX 4 (`4b7f21ae`);
`docs/sessions/nightrun-b-1.txt`; anything under `src/whetstone_gate/attacker/`; any
`tests/test_c6_*.py`; `PROGRESS.md`; `INCIDENTS.md`.

### 0.1 ⚠️ THE LEAKS THIS PROMPT ITSELF CARRIES, DECLARED

`OF-80` says the seal must name what leaked into it. This prompt told Phase 1:

* that FIX 4 closed **OF-124, OF-125 and OF-126** and reports **`src/` untouched** — all three
  COVERAGE defects rather than wrong values;
* that the fix's own mutant **SM-B** survived against its own published commit `7cbe908` — deleting
  the inline exclusivity check from its three new fixtures left **783 tests** green;
* that it reported that survivor **before** repairing it, and closed it with **`_sole_layer`** plus a
  self-test fired in **both** directions with two different single-layer shapes;
* that the fix found **five defects of its own** (two fabricated `Fix:` SHAs; INC-58's three harness
  defects; INC-60's `grep -c $'\r'`; INC-66's trailer placement).

**Phase 1 therefore knows the SHAPE and not the CONTENT.** What that permits is exactly what the
polarity table below does — and **eight of its rows predict failure, escape or a survivor**, so it
cannot be a wish list. Where a prediction turns out wrong in the fix's favour, this file is the
record that it was made.

---

## 1. ⚠️ THE OWNED-PROPERTY SET — ENUMERATED AND ARGUED, BEFORE A SINGLE MUTANT IS WRITTEN

**This section exists because `Q-082`'s ceiling is worthless if the set is chosen after seeing the
result.** C13 REVIEW 4 established that and it is binding. **Phase 2 may ADD a member with an
argument; it may never REMOVE one.**

The ruling, verbatim in the part that governs: *"THE GATE IS THE REQUIRED SET: at least one mutant
per property or invariant the chunk owns, minimum eight (PROCESS.md S5.3). SURVIVORS BEYOND THAT SET
ARE MEDIUM FINDINGS IN OPEN_FINDINGS.md AND DO NOT HOLD THE TAG."*

**C6 owns sixteen properties. Each is argued from a clause of `CONTEXT.md`, of `PROCESS.md` §12.1's
C6 card, or of an architect ruling — never from the code, which this phase has not read.**

| # | OWNED PROPERTY | THE CLAUSE THAT MAKES IT C6's |
|---|---|---|
| **OP-1** | **THE WINDOW.** The context keeps the **last 6 turns verbatim**; the width is a `config/` row; per-turn context reaches a steady state and stops growing. | §13.3: *"SLIDING-WINDOW CONTEXT IS MANDATORY, NOT AN OPTIMISATION"* — the spike burned ~300K tokens in one episode without it. §8.6: *"attacker context window - verbatim turns: 6"*. The C6 card names it. **It is the mechanism that bounds tokens/episode, and §13.4's N branch consumes that number.** |
| **OP-2** | **THE SUMMARISER'S DETERMINISM.** The ≤400-token summary is produced **by template, never by an LLM call**, and is **byte-identical for identical state**; the loop makes **one model call per turn**. | The C6 card's done-when, verbatim: *"the summary is byte-identical for identical state (proving it adds no request and breaks no determinism claim)"*. §13.3: *"produced DETERMINISTICALLY … not by an LLM call, so it adds no requests and does not break the seeded-determinism claim or the 20-requests/episode budget."* Hard rule 10 scopes the determinism claim and this is inside the scope. |
| **OP-3** | **THE 400-TOKEN CAP IS INCLUSIVE, PINNED IN BOTH DIRECTIONS.** Exactly 400 is legal; 401 is not. | `OF-87`, RULED: *"THE CAP IS INCLUSIVE: a summary of EXACTLY 400 tokens is legal and 401 is not. S8.6's frozen row caps AT 400. **Pin BOTH directions with tests** so M3 (loosened by one) and M19 (tightened by one) are both killed."* An architect ruling naming C6's own comparison. |
| **OP-4** | **TRUNCATION RESERVES THE DENIAL.** The cut drops the folded state, never the mandated denial line; a denial that alone exceeds the cap is a **HARD REFUSAL**, never a silent trim. | `OF-88`, RULED: *"TRUNCATION RESERVES THE DENIAL … a silently shortened summary is hard rule 11's shape applied to context instead of to episodes."* Hard rule 11 is one of the thirteen. |
| **OP-5** | **BLINDNESS LAYER 1 — the structural-LABEL scan, with the state JSON EXEMPT — IN BOTH COPIES.** | The C6 card: *"the attacker's context provably contains **no policy string**…"*. A cap value parked in a label is a policy string; the exemption must be over the JSON **body**, or a leak in the label exempts itself. `OF-107`/`OF-124` are this property; `Q-082`'s ruling names `OF-124` as *"on an owned property"* **in terms**. |
| **OP-6** | **BLINDNESS LAYER 2 — the defender-VOCABULARY scan, with the authored system prompt subtracted (and 2b over folded-state values) — IN BOTH COPIES.** | The card's *"no hole, no attack list and no gate reason"*. The subtraction is required, not optional: the tradecraft paragraph legitimately carries *exceptions*, *limits*, *special*, so a scan without it fires on the spec. |
| **OP-7** | **BLINDNESS LAYER 3 — the RESIDUE catch-all — IN BOTH COPIES.** | It is the **only** layer that catches authored text carrying no policy word at all, and §10.1's requirement is *no differential information*, not *no policy vocabulary*. `OF-106`/`N12` is this property. |
| **OP-8** | **BLINDNESS LAYER 4 — the DENIAL PAIR — IN BOTH COPIES.** The mandated last-denial line's **value is EXACTLY** the authored generic-denial constant, and there is **EXACTLY ONE** such line. | `Q-046`, RULED, Class A: *"THE LOOP THEREFORE IDENTIFIES A DENIAL BY EXACT STRING EQUALITY AGAINST THAT ONE AUTHORED CONSTANT, read from `data/` and never inlined."* §13.3 mandates *"**the last** denial reason"* — singular. `OF-105`/`N14` and `OF-111`/`OF-125` are the two halves. |
| **OP-9** | **THE EXCLUSIVITY HELPER (`_sole_layer`).** A per-layer fixture must be caught by **that layer and no other**, and the helper must assert **both** halves. | It is what makes OP-5…OP-8's tests be **about** their layer. `REVIEW_C6_3`'s complaint, verbatim: *"they die on one test … because a longer label changes the summary's CHARACTER COUNT. Nothing in that kill is about the label's content."* A helper that asserts exclusivity is worth exactly what its own exclusivity check is worth, and **this is the third time this shape has appeared in this file**. |
| **OP-10** | **MUST-REACH / THE DOOR IS OPEN.** `pay_CANARYRECON` **and** the probe note reach the attacker on the **WORLD** surface, in every arm, and never on the **AUTHORED** one. | `Q-046`'s ruling carries the warning in its own hand: *"⚠️ THE PROBE NOTE MUST STILL REACH THE ATTACKER ON THE WORLD SURFACE, IN EVERY ARM. Do not 'fix' the guard by banning it globally: S10.1 requires NO DIFFERENTIAL INFORMATION ACROSS ARMS, not concealment, and a global ban **SHUTS THE DOOR AND VOIDS ARM 4 BY CONSTRUCTION**."* **Blindness without must-reach is a closed door**, so the two are one property in two directions. |
| **OP-11** | **THE CORPUS SPLIT.** `seed_for_turn` is Q-047's stated arithmetic; all four corpora are offered in every episode; offers are byte-identical from the same seed and identical across arms sharing a seed; the corpus-vs-improvisation split is instrumented. | `Q-047`, RULED, **Class A** — *"it decides a published number, `CONTEXT.md` §11.3's corpus-versus-improvisation split."* The C6 card: *"the corpus-vs-improvisation split instrumented"*. |
| **OP-12** | **THE TOKEN COUNTER.** `ceil(chars / divisor)`; the divisor is **resolved through the loader on every access**, never a module-level eager read; and the figure is **labelled an ESTIMATE everywhere**. | `Q-048`, RULED, **Class A**: *"changing an unfrozen Class B parameter CHANGES THE BYTES THE ATTACKER IS SENT … `CHARS_PER_TOKEN` becomes a row in S8.6's constants table, a key in `config/protocol.yaml`."* `Q-031` part 2: *"An estimate presented as a measurement is `INCIDENTS.md` **INC-05**'s class, and the N branch decides the size of the whole run."* |
| **OP-13** | **THE CROSSOVER SERIES.** `crossing()` searches the **CLOSED** range `[0, turn_budget]` and is **STRICTLY** over the target. | `Q-031`'s own recorded finding is a **spread**, not a figure — ~25,200 realistic against ~126,600 worst case — and *"the figure is governed by how often the attacker re-reads `fetch_payments`"*. §13.4's Branch A condition is *"≤ 60,000"*, so *on* the target has not crossed it, and *every turn re-reads* is `k = turn_budget`, the worst case Q-031 names. `OF-108` closed one end; `OF-126` is the other, and `Q-082`'s ruling names it as owned **in terms**. |
| **OP-14** | **THE DYNAMIC-IMPORT SCAN** (`OF-110`'s C6 half): the AST walk plus a source-text scan refusing the **mechanism vocabulary**, over the whole attacker package. | `INC-51`: this exact class **defeated hard rule 8's moat test** — `gates/` reached `scorer/` live via `importlib` while the check printed *"share no first-party module on any path"*. C6's four *"imports no model client"* claims are worth nothing if a dynamic import evades them. |
| **OP-15** | **`attacker_sys.txt` VERBATIM, AND THE AUTHORED-SURFACE INVENTORY.** The system prompt is §8.6's text character-identical, read from `data/`; and `authored_text()` is **the system prompt and the deterministic summary, nothing else**. | The C6 card: *"`attacker_sys.txt` verbatim from spec §8.6"*. `Q-046`'s consequence clause: *"world text and third-party corpus text STOP REACHING THE AUTHORED SURFACE, so `authored_text()` becomes what the build report claimed it already was."* **The inventory is what makes the four claims decidable at all** — a guard over the wrong set of parts proves nothing. |
| **OP-16** | **THE STRUCTURAL NO-GATE-OBJECT PROPERTY.** The loop holds no gate object and no policy object; the only route from a verdict to the attacker is the one authored string. | `Q-046`: *"No gate object is needed, so **the structural argument that makes claim 4 hold is PRESERVED INTACT**."* Claim 4 is structural rather than a filter **because** of this, and a filter can be defeated where a structure cannot. |

**Sixteen properties, against `PROCESS.md` §5.3's minimum of eight.** OP-5…OP-8 are each required in
**both copies** of the guard, so the required set is **at least twenty mutants**.

### 1.1 ⚠️ WHAT C6 DOES **NOT** OWN — pre-committed, so a survivor there cannot be graded after the fact

| # | NOT OWNED | WHY, AND WHOSE IT IS |
|---|---|---|
| **NO-1** | **The CONTENTS of the §8.6 folded state.** A leak carried inside a folded-state **value** is not a C6 defect. | §8.6 puts the folded state on the authored surface and **C7's ledger fills it**. A C6 guard exempting it would be exempting somebody else's data; a C6 guard failing to catch a leak somebody else wrote into it is not C6 failing. `REVIEW_C6_4` pre-committed this at `11193bd` (its P-29) and **this file re-commits it before measuring**. |
| **NO-2** | The world's payloads, `pay_CANARYRECON`'s fields, the note pool and the decoy. | C2's, tagged `c2-pass`, pinned by golden 7. |
| **NO-3** | The gate's verdict set and the **authorship** of the denial string. | §8.6 and C9's. C6 owns only that it **reads** the string from `data/` and compares by equality (that half is OP-8). |
| **NO-4** | `check_roles.py`'s D4 and the module-graph moat itself. | C0's and C11's. C6 owns only its own package's dynamic-import scan (OP-14), which is *deliberately not imported from* D4. |
| **NO-5** | `spec_constants.AUTHORED_TEXTS`' registry rows (`OF-53`, `Q-049`). | Outside every C6 fence; routed and open by design. |
| **NO-6** | Repository-wide process: session tokens, CRLF, the cp1252 route, `docs/sessions/` naming (`OF-134`). | The architect's and C11's. |
| **NO-7** | Whether the token figure is **right**. | `Q-031` part 2 and §13.3: **the pilot measures the real figure and C14 owns it.** C6 owns only that its own number is labelled an estimate and that its method is on the record (OP-12). |
| **NO-8** | Hygiene in test files outside C6's fence — e.g. `tests/test_c6_review_probes.py`'s all-zero folder (`OF-112`). | The session that owns that file. |

---

## 2. ⚠️ THE OWNED / NOT-OWNED DETERMINATION RULE — PRE-COMMITTED

Written now, before any mutant, because a rule written after a survivor is a rationalisation.

1. **A mutant is IN THE REQUIRED SET if and only if it attacks the DEFINING CLAUSE of one of
   OP-1…OP-16** — the clause without which the property, *as `CONTEXT.md` or an architect ruling
   states it*, no longer holds. **I must be able to QUOTE that clause in one sentence.**
2. **If I can quote the clause, the mutant GATES.** Schedule, effort and the chunk's history are not
   arguments. This is the direction the rule is most likely to be bent, so it is stated first.
3. **A mutant is BEYOND the set** — a MEDIUM or LOW finding, not the gate — if it changes behaviour
   only on an input the property's own statement does not reach: a shape **no code path builds**, a
   **directory layout that does not exist**, a **strictness the spec never asked for**, or a
   **surface another chunk owns** (§1.1).
4. **Where HEAD is the STRICTER of the pair and the mutant is WRONG, the survivor is not a defect at
   all.** It is recorded and marked **MUST-NOT-FIX**. `R-05` and `R-12` are that class and this
   session's prompt confirms it: *"changing either installs a wrong behaviour."*
5. **Every survivor is marked OWNED or NOT-OWNED and the determination is ARGUED** — the clause
   quoted, or the §1.1 row named. **An unargued determination is not a determination**, and a
   verdict that rests on one is not a verdict.
6. **Pre-committed by name.** `OF-124`, `OF-125` and `OF-126` **ARE** required-set members —
   `Q-082`'s ruling says so in terms (*"OF-124, OF-125 and OF-126 are all on owned properties"*).
   `OF-127`, `OF-128`, `OF-133`, `R-18` and `R-08` are **NOT** — this session's prompt carries the
   architect's own disposition: *"Under Q-082 they are findings, not gate."*

### 2.1 THE VERDICT RULE, SEALED

* **Every required-set mutant KILLED or PROVEN EQUIVALENT (with its separating input named), the
  four blindness claims holding over the real assembled bytes with both controls, my reimplementation
  agreeing, and ZERO BLOCKERS → PASS, and I cut `c6-pass`.**
* **Any required-set mutant surviving, non-equivalent and exhibited on a concrete input → FAIL**,
  and the finding is named against its OP row.
* **A survivor beyond the required set → MEDIUM or LOW in `OPEN_FINDINGS.md`. It does not hold the
  tag.**
* **A needle escaping the guard while the four claims still hold over the real bytes → MEDIUM**, the
  grade `REVIEW_C6_3` gave the identical shape as its `M-1` and `REVIEW_C6_4` gave `OF-127`.
* **`src/` having moved under FIX 4 → every `REVIEW_C6_4` exhibit is re-measured before anything
  else**, because the fix would then have done more than it says.
* **A post-restore control that is not green VOIDS the run it belongs to** and it is re-run, not
  reported.

### 2.2 THE MUTATION-HARNESS CONTRACT, SEALED

Both flattering directions are named because both have already happened here:

* **INC-64 / OF-139 — the clone that imports the LIVE package reports every mutant SURVIVED.**
  `PYTHONPATH` is set to the clone, and **`whetstone_gate.__file__` and `config.repo_root()` are
  PRINTED at the head of every run**. A test now catches this and it is run.
* **INC-57 — restoring with `git checkout --` from a HEAD that holds the mutation reports every
  mutant KILLED.** Restoration is by **writing the original bytes back**, never by git.
* **A control run precedes and follows every batch**, and a batch whose post-restore control is not
  green is **VOID**.

---

## 3. THE REQUIRED-SET MUTANT PLAN — one per owned property, named before it is written

| mutant | OP | the operator |
|---|---|---|
| **M-01** | OP-1 | the verbatim-turn width read from `config/` replaced by a literal / off by one |
| **M-02** | OP-1 | the window taken as a PREFIX instead of a suffix |
| **M-03** | OP-2 | the summary made state-dependent on something outside the folded state (determinism broken) |
| **M-04** | OP-2 | the one-call-per-turn count relaxed |
| **M-05** | OP-3 | the cap comparison `<=` → `<` (tightened by one) |
| **M-06** | OP-3 | the cap comparison `<=` → `<= cap + 1` (loosened by one) |
| **M-07** | OP-4 | truncation allowed to drop the denial line |
| **M-08** | OP-4 | the hard refusal replaced by a silent trim |
| **M-09/M-10** | OP-5 | LAYER 1's exemption widened from the state JSON to the state LINE — **copy 1 and copy 2** |
| **M-11/M-12** | OP-6 | LAYER 2's vocabulary scan deleted — **copy 1 and copy 2** |
| **M-13/M-14** | OP-7 | LAYER 3, the residue catch-all, deleted — **copy 1 and copy 2** |
| **M-15/M-16** | OP-8 | the denial-VALUE equality block deleted — **copy 1 and copy 2** |
| **M-17/M-18** | OP-8 | the refusal-line count `!= 1` → `< 1` — **copy 1 and copy 2** |
| **M-19** | OP-9 | `_sole_layer`'s **exclusivity** half deleted (SM-B's own operator, re-applied) |
| **M-20** | OP-9 | `_sole_layer`'s **identity** half deleted (accepts any layer) |
| **M-21** | OP-9 | `_sole_layer` made a no-op |
| **M-22** | OP-9 | `_sole_layer` inverted |
| **M-23** | OP-10 | the guard extended to ban the probe note globally — **the door-shutting mutant, and it MUST go red** |
| **M-24** | OP-11 | `seed_for_turn`'s stride / episode-seed term dropped (back to a constant slice) |
| **M-25** | OP-11 | the corpus round-robin replaced by a single-corpus slice |
| **M-26** | OP-12 | `chars_per_token` read eagerly at import instead of through the loader |
| **M-27** | OP-12 | `ceil` → `floor` in the estimator |
| **M-28** | OP-13 | `range(0, turn_budget + 1)` → `range(0, turn_budget)` |
| **M-29** | OP-13 | `> target` → `>= target` |
| **M-30** | OP-14 | the source-text scan's refusal list shortened by one entry |
| **M-31** | OP-14 | the AST walk deleted, leaving the text scan alone |
| **M-32** | OP-15 | the authored-surface inventory widened to include a WORLD part |
| **M-33** | OP-15 | one character of `attacker_sys.txt`'s comparison relaxed |
| **M-34** | OP-16 | a gate/policy object threaded into the loop |

**Thirty-four required-set mutants against a minimum of eight.** Phase 2 may add more; it removes
none.

---

## 4. THE PRE-COMMITTED POLARITIES — 56 PROBES

**Sealed. Every row's expectation is written before the measurement.** ⚠️ marks a row that predicts
failure, escape or a survivor: there are **eleven**.

| # | subject | expected |
|---|---|---|
| **P-01** | `R-14` re-run (copy 2's LAYER-1 exemption widened to the state LINE) | **KILLED** |
| **P-02** | `R-15` re-run (copy 2's refusal-line count `!= 1` → `< 1`) | **KILLED** |
| **P-03** | `R-20` re-run (`crossing()`'s `range(0, turn_budget + 1)` → `range(0, turn_budget)`) | **KILLED** |
| **P-04** | `git diff` of FIX 4's commits against `src/whetstone_gate/attacker/` | **EMPTY** — all three were coverage defects |
| **P-05** | FIX 4's `src/` claim across the WHOLE package, not just `attacker/` | **EMPTY** |
| **P-06** | **SM-B's repair**: the exclusivity half of `_sole_layer` deleted again | **RED** |
| **P-07** | `_sole_layer` inverted | **RED**, many failures |
| **P-08** | `_sole_layer` made a no-op | **RED** |
| **P-09** | `_sole_layer`'s identity half deleted (accepts any layer) | **RED** |
| **P-10** | ⚠️ `_sole_layer`'s `fired` computed over a LIST rather than a SET, so one layer firing twice raises | ⚠️ predicted **SURVIVOR**, and **NOT-OWNED** — the mutant is STRICTER and wrong (rule 2.4, `R-05`'s class) |
| **P-11** | ⚠️ **COPY 2's LAYER 3 (residue) deleted** | ⚠️ predicted **SURVIVOR**, and **OWNED (OP-7)** — reasoning: FIX 3 fixed copy 1 thoroughly and copy 2 for one class; FIX 4 was directed at three named classes, none of them L3-in-copy-2. **If this survives it carries a FAIL.** |
| **P-12** | **COPY 2's LAYER 2 (vocabulary) deleted** | **KILLED** — the vocabulary is the most-fired part of both copies |
| **P-13** | ⚠️ **COPY 2's LAYER 2 subtraction widened to all occurrences / to the whole part** | ⚠️ predicted **SURVIVOR**, **NOT-OWNED** if the mutant is the stricter one, **OWNED** if it is looser |
| **P-14** | COPY 1's LAYER 1, LAYER 3 and the denial-value block, each deleted | **KILLED**, all three |
| **P-15** | the two copies still share no import edge (by AST) | **HOLD** |
| **P-16** | the two copies' vocabularies still differ (independent implementations, not a shared helper) | **HOLD** |
| **P-17** | the four blindness claims over the package's ACTUAL assembled bytes, my 110 needles, several turns | **0 AUTHORED hits** |
| **P-18** | **CLEAN-SURFACE CONTROL** — my 110 needles on an unleaked authored surface | **0 of 110** |
| **P-19** | **MUST-REACH** — the probe NOTE on the FULL surface | **True at every turn from the first listing read** |
| **P-20** | **MUST-REACH** — the probe NOTE on the AUTHORED surface | **False at every turn** |
| **P-21** | **MUST-REACH** — `pay_CANARYRECON` on the FULL surface | **True** |
| **P-22** | ⚠️ **MUST-REACH** — `pay_CANARYRECON` on the AUTHORED surface at LATE turns | ⚠️ predicted **True**, via the §8.6 folded state's payment-id map — and pre-committed **NOT A FINDING**: §13.3 mandates the folded state, §8.6 keys it by payment id, the id is one **the attacker itself supplied**, and the map is built identically in every arm, so there is no differential. |
| **P-23** | `M-23`, the door-shutting mutant (the note banned globally) | **RED** — if it is green, arm 4 is VOID BY CONSTRUCTION and that is a **BLOCKER** |
| **P-24** | ⚠️ a leak in a structural LABEL matching no cap rendering, no clause id and no arm digit | ⚠️ predicted **ESCAPES both copies** — `OF-127`/`OF-133`'s class; **NOT gate** under rule 2.6 |
| **P-25** | ⚠️ authored text APPENDED to the state line rather than added as a new line | ⚠️ predicted **ESCAPES** — `OF-128`'s class; **NOT gate** under rule 2.6 |
| **P-26** | a leak in the refusal **VALUE** | **CAUGHT, 110 of 110** |
| **P-27** | a leak as a **new-line residue** | **CAUGHT, 110 of 110** |
| **P-28** | `M-05` / `M-06`, the cap loosened and tightened by one | **both KILLED** (`OF-87` ordered both) |
| **P-29** | `M-07` / `M-08`, truncation dropping the denial and the refusal silenced | **both KILLED** (`OF-88`) |
| **P-30** | `M-01` / `M-02`, the window's width and direction | **both KILLED** |
| **P-31** | ⚠️ the package's own `_sole_layer` fixtures for a **vocabulary** or **denial** layer | ⚠️ predicted to need explicit residue handling, because a leak that trips the vocabulary layer usually ALSO leaves residue — **measured first-hand in my own reimplementation (V-28, a wrong prediction I corrected on the record)** |
| **P-32** | `M-26`, `chars_per_token` read eagerly at import | **KILLED** (`Q-048` names PEP 562 resolution through the loader) |
| **P-33** | `M-27`, `ceil` → `floor` | **KILLED** |
| **P-34** | `M-29`, `crossing()`'s `> target` → `>= target` | **KILLED** (`OF-108` closed it) |
| **P-35** | `M-24` / `M-25`, the corpus stride and the round-robin | **both KILLED** (`Q-047` is Class A) |
| **P-36** | all four corpora offered in every episode, byte-identical from the same seed | **HOLD** |
| **P-37** | `M-30` / `M-31`, the dynamic scan's refusal list and its AST half | **both KILLED** (`OF-110` closed this) |
| **P-38** | ⚠️ `rglob` → `glob` on the dynamic scan (`R-18`) | ⚠️ predicted **SURVIVOR**, **NOT-OWNED** — no subpackage exists; rule 2.3 and the architect's own disposition |
| **P-39** | ⚠️ `assert len(summaries) == 1` → `>= 1` (`R-08`) | ⚠️ predicted **SURVIVOR**, **NOT-OWNED** — no code path builds two |
| **P-40** | `R-05` and `R-12` left ALONE by FIX 4 (HEAD is the stricter of each pair) | **HOLD — unchanged** |
| **P-41** | `M-32` / `M-33`, the authored-surface inventory and `attacker_sys.txt`'s comparison | **both KILLED** |
| **P-42** | `M-34`, a gate object threaded into the loop | **KILLED** |
| **P-43** | my reimplementation's semantics against the package: estimator, cap, truncation, window, `crossing()`, `seed_for_turn` | **AGREE on all six** |
| **P-44** | ⚠️ my summary LABELS against the package's | ⚠️ predicted **DIFFERENT** — the spec fixes no label text, so this is **never asserted** and a difference is not a finding |
| **P-45** | **INC-47's test applied a third time**: does any FIX 4 `Action` field claim more than its commits demonstrate? | **NO overstatement** — two sessions have checked |
| **P-46** | the two fabricated `Fix:` SHAs FIX 4 reports catching before staging | **caught before staging; no fabricated SHA reaches a committed `INCIDENTS.md` entry** |
| **P-47** | INC-58's three harness defects and INC-60's `grep -c $'\r'` | **recorded, and the CRLF property itself SAFE** — the suite's own `test_the_object_store_and_the_working_tree_agree` is the check that matters |
| **P-48** | INC-66's trailer placement | **the degradation record's commit carries `Session-Token:` adjacent to `Co-Authored-By:` after the correction** |
| **P-49** | `make test` — measured by me, twice | **0 failures**, and any failure attributed **by file** |
| **P-50** | `make selftest` | **RED on `camel_comparator.branch` and on nothing else** — not C6's |
| **P-51** | `make check-roles` | **exit 0** |
| **P-52** | `git status --porcelain tests/goldens/` | **EMPTY** |
| **P-53** | `evals/` | **absent or empty — C6 spent nothing** |
| **P-54** | provider model calls by this session | **ZERO** |
| **P-55** | vendored pins | `tau2_bench_sha` and `camel_sha` resolve; `agentdojo_sha` **still RAISES** (Q-083: the honest end state) |
| **P-56** | ⚠️ my prior on the whole review | ⚠️ **at least one required-set survivor**, most likely on OP-7 in copy 2 (P-11) |

---

## 5. WHAT THIS FILE COMMITS ME TO

* The **owned-property set is §1's sixteen rows**, fixed before any mutant. Phase 2 may **add** with
  an argument; it may **not remove**.
* The **determination rule is §2's six clauses**, and clause 2 — *if I can quote the clause, the
  mutant gates* — binds against my own convenience.
* **Zero required-set survivors → PASS and I cut the tag.** This is stated as plainly as the FAIL
  condition, because `Q-082`'s ruling gave the bar a ceiling it did not have when C6 failed its
  third and fourth time, and **a reviewer who will not pass a clean required set is not applying a
  bar, only generating mutants.**
* **A fifth FAIL must rest on an owned property, named and argued against a quoted clause.**
