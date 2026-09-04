# C21 — THE SUBMISSION FORM ANSWERS

**Rewritten by C21 BUILD 2, `SESSION-TOKEN 6f2d47ba`, 2026-09-04. Measured at `HEAD` = `686a224`;
⚠️ `HEAD` MOVED TO `259ca6b` DURING THE SESSION — C17 REVIEW 1, verdict FAIL — and the rows that
moved with it were RE-MEASURED rather than left standing (§0.0, §5, §9).
Supersedes the C21 BUILD 1 version (`9e2c81d4`, `685ca50`) — which is not deleted, and whose
reasoning stands in `docs/sessions/c21-build-1.txt`. NOT SELF-CERTIFIED: a fresh adversarial review
(`full` + `submission`, persona 3) follows and has not run.**

This file is what the operator pastes. `PROCESS.md` §12's C21 card (`PROCESS.md`:1343) requires it
"verbatim and final", and `PROCESS.md`:1344's SUBMIT row makes **"the reviewed artefact is what is
pasted"** the gate. A paragraph re-drafted in the form box has never been reviewed, and the form is
one-shot.

⚠️ **WHY IT WAS REWRITTEN RATHER THAN AMENDED.** BUILD 1 wrote it at 07:46 IST. Between then and
this session **the pilot ran and was spent, `RESULTS.md` came into existence, degradation rung 4
fired and was executed, C17's replay renderer was built, `INCIDENTS.md` grew by eighteen entries, and
the single-shot calibration was declared and attempted twice.** Counted precisely rather than
estimated: of BUILD 1's seven state rows, **two had become false** (`evals/` "one file";
`RESULTS.md` "does not exist") and **three more carried line numbers that had moved**; its published
incident count was **137** and is now **155**. **Every factual claim below was re-measured by this
session against the tree as it stands tonight; none was inherited.**

---

## 0. READ THIS BEFORE THE PARAGRAPHS

### 0.0 THE STATE, RE-MEASURED TONIGHT — the box that governs every word below

⚠️ **NO SCORED EPISODE HAS RUN. THERE IS NO SWEEP AND NO COMPLETED CALIBRATION.**
⚠️ **THE PILOT HAS RUN, IT IS SPENT, AND IT MEASURED NOTHING.** That last clause is new since
BUILD 1 and it is the one a panelist will grep for.

Measured by this session at `HEAD` = `686a224afa85eb92d7b3b1cefa233d214fcd6f79`, 2026-09-04, between
`14:45Z` and `15:25Z`:

| Fact | How this session measured it | State tonight | Moved since BUILD 1? |
|---|---|---|---|
| `git tag -l` | `git tag -l` | **seven tags**: `c0-pass c1-pass c2-pass c3-pass c4-pass c13-pass` **and `probe-v1`** | no |
| **`prereg-v1`** | `git rev-parse prereg-v1` | ⚠️ **DOES NOT RESOLVE** — *"unknown revision or path not in the working tree"* | no |
| **the witness gist** | `git tag -l`; the repository's own row at `README.md`:42 | ⚠️ **DOES NOT EXIST.** No `prereg-v1.sha256`, no OTS receipt, no gist id — the only gist id in the tree is the unfilled placeholder in `README.md`:1491's `curl` | no |
| **the pilot** | `find evals -type f`; `README.md` STATUS box, `evals/` row | ⚠️ **RAN. SPENT. IT IS THE RECORD, AND IT MEASURED NOTHING.** **20 attempted · 0 completed · 11 truncated · 9 never started.** `INC-142` | ⚠️ **YES — BUILD 1 said "no pilot"** |
| `evals/` | `find evals -type f \| wc -l` | ⚠️ **31 files** — 11 episode ledgers, 11 checkpoints, 5 usage logs, 2 declarations, 2 attempt logs | ⚠️ **YES — BUILD 1 said "one file"** |
| **`RESULTS.md`** | `ls RESULTS.md`; read in full | ⚠️ **EXISTS** — a transitional stub by `ARCH PUBLISH 1` (`2e5b8a47`) that discharges `PROCESS.md` §14's *"a cut item is named in `RESULTS.md`"* half **and publishes no number** | ⚠️ **YES — BUILD 1 said "does not exist"** |
| **degradation rung 4** | `INCIDENTS.md` `INC-144`; `config/protocol.yaml`:445, :497-498 | ⚠️ **FIRED 2026-09-04 05:27 UTC AND NOW EXECUTED.** T-FP 40 → 20 τ² write tasks. `tfp_task_count: 20`; `tfp_task_ids` holds 10 airline + 10 retail. ⚠️ **τ²-bench is NOT cut** — see §0.3 | ⚠️ **YES — did not exist in BUILD 1's file at all** |
| **C17's replay renderer** | `ls docs/render/`; `git log --oneline -- docs/render/`; `docs/reviews/REVIEW_C17_1.md` §2.3 | ⚠️ **EXISTS AND HAS NOW FAILED ITS REVIEW.** `race.py`, `audit.py`, `replay.py`, `README.md`, commit `b332853` **`(unreviewed)`**. **`REVIEW_C17_1` verdict: ⛔ FAIL — two BLOCKERs, five HIGH, five MEDIUM, five LOW.** No `c17-pass` tag; `STATUS.md`:2196 reads *"REVIEW 1 FAILED 2026-09-04 (`4e8b91d3`) - TWO BLOCKERs. AWAITING FIX."* | ⚠️ **YES — did not exist when BUILD 1 wrote, and its review landed while THIS session was writing** |
| `probe.void_threshold_breach_rate` | `config/protocol.yaml`:352 | **`TODO_C14_CALIBRATION`** — an explicit sentinel; the loader **raises** on it, never defaults | value unchanged; **line moved** `335` → `352` |
| **the calibration** | `ls -la evals/cal/`; both logs read in full; `find evals -name '*cal__*'` | ⚠️ **DECLARED AND ATTEMPTED. NO COMPLETED CALIBRATION RUN EXISTS.** **Zero calibration episode ledgers.** See §0.2 — this is a rule-1 STOP | ⚠️ **YES — BUILD 1 said "no calibration"** |
| `n_decision.selected_branch` | `config/protocol.yaml`:406 | **`TODO_C14_PILOT`** — the pilot **refused** to select N | no |
| `INCIDENTS.md` entries | `grep -c "^## INC-" INCIDENTS.md` | ⚠️ **155 headings, 154 distinct ids** — `## INC-139` appears **twice** (:10224, :10531); `INC-104`/`105`/`106` were reserved and never issued; highest id `INC-157` | ⚠️ **YES — BUILD 1 published 137** |
| the review trail | `docs/reviews/REVIEW_*.md`, top level, each verdict read | ⚠️ **21 files · 15 FAIL · 6 PASS · 0 unrecorded** — `REVIEW_C17_1.md` landed at `259ca6b` **during this session** | ⚠️ **YES — it was 20 / 14 / 6 an hour ago** |
| the video | `STATUS.md`:2199, the C20 row | **`todo - review folded`**; no video URL exists anywhere in this repository | value unchanged; **line moved** `1834` → `2199` |
| the repository's visibility | `PROCESS.md`:862 | **still PRIVATE.** The flip is C21's other half and the operator's act | no |

**Consequence, stated rather than implied:** every number either paragraph would want is written as
an explicit named placeholder in the form `<<PENDING-RUN: name>>` — the convention `README.md`:28
fixes: *"every one of them is spelled `<<PENDING-RUN: name>>` so you can find them all with one
grep."* **A placeholder is never a result.** §8 lists every one in the repository, not only this
file's.

### 0.1 ⚠️ CITATION POLICY, BECAUSE LINE NUMBERS IN THIS REPOSITORY MOVE HOURLY

**Every `file:line` below was re-opened and re-read by this session at `686a224`.** BUILD 1's
citations were correct when written and **a majority of the volatile ones had moved within nine
hours** — `config/protocol.yaml`:335 → :352, :396 → :413; `tests/test_c10_probe.py`:1092/:1106 →
:1127/:1141; `README.md`:56-58 → :120-124, :1222 → :1491; `STATUS.md`:1830 → :2195, :1834 → :2199.
**So each citation here carries its section or its heading as well as its line**, and §9 states the
`HEAD` it was taken at. A reviewer who finds a line number off by a few should search the quoted
heading before concluding the claim is wrong — and should treat a claim whose *heading* has vanished
as wrong.

### 0.2 ⚠️ THE SINGLE-SHOT CALIBRATION — WHAT IS TRUE, AND THE ONE THING THIS FILE REFUSES TO DO

**What is true, measured, not inferred:**

- `evals/cal/RUN_DECLARED.md` was filled, committed (`63c70ec`) and **pushed before any attempt** —
  the direction `PROCESS.md` §6b protects. Its declared start is `2026-09-04T13:29:25Z`.
- **Attempt 1** aborted nine seconds later on a bare `python` that resolved to an interpreter without
  the package. `INCIDENTS.md` `INC-157`, written **before** any retry as §6b requires:
  **0 of 30 episodes, 0 tokens.**
- **Attempt 2** ran, and unlike attempt 1 it reached the provider. Measured from
  `evals/usage/gemma-26b-2026-09-04.jsonl`: **13 calls, all `outcome: OK`, 56,855 tokens**, between
  `14:33:30Z` and `14:38:50Z`, every one on episode `cal__1__2201__gemma-26b` — plus a 232-token
  preflight liveness call at `14:33:18Z` (`evals/usage/liveness-CAL-2026-09-04.jsonl`), **57,087
  tokens on the lane in total.** Its log is `evals/cal/run-attempt2-20260904T143317Z.log`.
- ⚠️ **`find evals -name '*cal__*'` returns 0. There is no calibration episode ledger and no
  calibration checkpoint.** `evals/` is publish-on-complete, so **no calibration episode has
  completed.**
- ⚠️ **`config/protocol.yaml`:352 still reads `TODO_C14_CALIBRATION`, and the loader raises rather
  than defaulting** — so **no VOID verdict is computable from `config/` on any input.**

**And the one thing this file refuses to do:** it does not state, predict, estimate, round, hedge or
illustrate a breach rate, a threshold, or a void verdict. **What a completed calibration would
produce is NOT YET KNOWN**, and a submission that anticipated it would be committing, in miniature,
the exact offence this project exists to measure in others. **Nothing below leaves room to infer
one.**

⚠️ **A RULE-1 STOP, RAISED AND NOT RESOLVED BY THIS SESSION.** Measured at `14:45Z` and again at
`14:57Z`: `ps -W | grep -c python.exe` returns **0**; `evals/cal/run-attempt2-20260904T143317Z.log`
ends in a traceback whose final line is `TimeoutError: The read operation timed out`; the newest
write anywhere under `evals/` is that log at `14:41:51Z`; and the 13 usage rows above stop at
`14:38:50Z`. **On that evidence attempt 2 is not running.**
`PROCESS.md` §6b requires that *"if an attempt aborts before completion, the abort, its cause and
its partial episode count are written to `INCIDENTS.md` **before** any retry"* — and `INCIDENTS.md`'s last entry is `INC-157`, which covers attempt 1 only. **`INCIDENTS.md`
and `evals/` are both outside this session's fence, so this session wrote neither.** It is
**operator item O-0** in §7 and the first item in this session's report. **This file states no
verdict about attempt 2's outcome beyond the two facts that no calibration episode completed and no
threshold exists** — both of which are true whatever happens next.

### 0.3 ⚠️ RUNG 4 FIRED — AND WHAT DID *NOT* CHOOSE IT

`INCIDENTS.md` `INC-144`, and the same words in `README.md` §9.3 (:810) and `RESULTS.md` §1:

- **What was cut:** the **breadth of one block**. T-FP, the τ² false-positive sample, from **40 write
  tasks to 20, stratified 10 airline / 10 retail.** The paired FP delta is therefore reported on
  **n=20 per configuration**, and every table caption must state that cell size.
- **Which 20 survive was derived, not chosen:** the same rule at K=20 — *first K/2 per domain,
  bytewise-ascending string sort, within each domain separately* (`CONTEXT.md` §13.4;
  `PROTOCOL.md` §3.2). Each surviving list is an **exact prefix** of its domain's pre-registered 20.
  **A prefix cut is not a re-registration**, and it was made **before** `prereg-v1`, which is what
  `PROCESS.md` §14's rung-4 row says to do *"if at all possible"*.
- ⚠️ **τ²-BENCH IS NOT CUT.** It is the **first** entry on `PROCESS.md` §14's *"NEVER CUT, at any
  rung, for any reason"* list, and `CONTEXT.md` §21.4 says of it *"**It is never dropped.**"* — adding
  in the same sentence that its **scope** is staged. **T-NEG, the must-not-write control, keeps all
  34 tasks** (`config/protocol.yaml`:447 `tau2_must_not_write_task_count: 34`). **The
  externally-authored-answer-key claim is intact.**
- ⚠️ **THE MEASUREMENT DID NOT CHOOSE THIS CUT, AND NOTHING IN THIS FILE MAY IMPLY IT DID.** Two
  instruments can order the same reduction and only one fired. `CONTEXT.md` §13.4's decision rule
  fires on the pilot's **measured** tokens/episode — and **its input does not exist**: the pilot
  completed **0 of 20** and `n_decision.selected_branch` is still `TODO_C14_PILOT` (`INC-142`).
  **`PROCESS.md` §14 rung 4 fires on SCHEDULE, at the operator's decision, and that is the one that
  fired.** The reason that sentence is written so flatly is `QUESTIONS.md` **Q-099**: an earlier
  session's prompt asserted rung 4 had already fired when it had not, and that session **stopped
  rather than transcribe it into a frozen artefact.**
- **Execution state:** ⚠️ **BUILD 1's file predates this entirely, and `INC-144` recorded the
  execution half as operator-owed.** Measured tonight, **it has landed**:
  `config/protocol.yaml`:445 `tfp_task_count: 20`; :497-498 `tfp_task_ids` holds ten ids per domain;
  and `tests/test_c3_tau2_enumeration.py`:269-316 asserts both that `CONTEXT.md` §13.4 **still** says
  40/20/20 and that `config/` carries rung 4's half — *"It fails on the old `config/`"*.

### 0.4 THE FIVE STOPS BUILD 1 RAISED ARE STILL OPEN, AND THIS SESSION ADDS FOUR

`QUESTIONS.md` is outside this session's fence — a concurrent session holds it — so every item below
is owed to it and appears in this session's report under **QUESTIONS OWED**. BUILD 1's `Q-A`…`Q-I`
are recorded verbatim in `docs/sessions/c21-build-1.txt` §7 and its addendum, and **none has been
answered**: the filename (`FORM.md` vs `FORM_ANSWERS.md`), which "§9 limitation sentence" is meant,
that the canonical limitation sentence names a **cut** component (AgentDojo), the card's five
incident fields against hard rule 13's eight, and the constitution's description of an allow-list
that is in fact empty.

**This session's four new ones**, stated here so a reviewer does not have to find them:

- **Q-J — the calibration abort has no `INCIDENTS.md` entry, and §6b forbids a retry until it does.**
  §0.2 above.
- **Q-K — the prompt that opened this session described `docs/sessions/c21-build-1.txt` §7 as
  carrying "TEN QUESTIONS". It carries eight** (`Q-A`…`Q-H`), **plus `Q-I` raised in that file's
  addendum — nine.** Counted twice. Recorded rather than reconciled, because a session that quietly
  matches a count to its prompt is the failure `Q-099` records.
- **Q-L — `CONTEXT.md` §1 carries the unnarrowed form of method claim 1.** It reads *"an attacker
  that has never seen the policy **or any attack list**"*. §6.1(1) below establishes that the second
  clause is **false**: the attacker is deliberately seeded from published third-party corpora and the
  system prompt we authored names attack families in plain English. **`CONTEXT.md` is the law and is
  outside this fence, so it was not edited.** No form paragraph carries the unnarrowed form.
- **Q-M — this file's own line-number citations are a maintenance hazard.** §0.1. The remedy is
  cheap — cite the heading, not only the line — and it is applied here, but the same drift is live in
  `README.md` and `STATUS.md`, which this session may not edit.

---

## 1. THE PROJECT NAME

```
WHETSTONE GATE
```

Repository name: `whetstone-gate`. `[CONTEXT.md:86 — "## NAME — WHETSTONE GATE. Repository
whetstone-gate. Decided 2026-08-30; do not revisit."]`

---

## 2. PROJECT OBJECTIVES — paste verbatim

> ⚠️ Opens on the merchant's loss, never on the methodological critique — `CONTEXT.md` §21.3:
> *"Problem taste is the weakest rubric line and their first. Mitigated only by leading … with §2 —
> the merchant's loss — and never with the methodological critique."*

---

A merchant connects Razorpay's official MCP server to an AI assistant so it can handle refunds and
reconcile settlements. That assistant now reads text the merchant did not write — support tickets,
order notes, customer messages — and it holds live API credentials. Razorpay's official MCP server
caps how many payments an agent may **list** at 100, and places no cap on how many rupees it may
**move**. Read first-hand in the Go source at
`github.com/razorpay/razorpay-mcp-server@7950d51d118ca164c32b7cf0cfaa14f34f24849f` (HEAD of `main`,
committed 2026-03-26, read 2026-08-30): nine `mcpgo.Max()` constraints exist and **not one bounds a
rupee amount** — six bound pagination at 100, the others a 40-character receipt, a 0/1 filter flag
and a 30-character settlement description; `capture_payment.amount` has neither ceiling nor floor;
`READ_ONLY` defaults to `false`. The loss is concrete: an over-capture, an over-refund, a duplicated
refund, or an early balance sweep — each triggered by text the merchant never wrote, each executed
with the merchant's own credentials, each landing in a settlement report as a legitimate-looking
line.

WHETSTONE GATE builds the missing policy gate — five gate designs behind one interface — and then
spends most of its effort trying to prove that its own "blocked" number means nothing. **The gate is
commodity, and we say so first.** At least 43 entrants in this buildathon built the same missing
limit — a floor, not a census — and of 43 Track 01 READMEs read in full on 30 August, a 13–14%
sample (43 of the 312 Track 01 repos identified when the corpus stood at 1,723), every one authored
its own world **and** its own answer key, and the recurring headline is *100% blocked*. **Those
occupancy figures are floors, not a census, and neither can be enumerated. The corpus definition
misses precisely the repos most likely to be near neighbours.** Better things than ours already
exist in public:
**CaMeL and PRAMANA both have better gates, and PRAMANA's audit log is stronger than ours**; and
`jboiie/argus`, `adthya-anil/AgentProof` and `Chavan-Kartik/HydraLoop` all ship generated
adversaries, which we did not invent either. (Each is named in the repository with its URL and the
date it was read; CaMeL is arXiv 2503.18813, read 2026-08-30.)

**So the objective is the whetstone, not the blade: to measure what a "blocked" number is worth.**
One attacker that has never seen our policy text, our pre-registered holes, our attack-and-invariant
taxonomy or any gate's denial reason — the only refusal it sees is a single generic string, identical
across all five arms — run against every arm on the same seeds, with escapes found by deterministic
replay of a hash-chained ledger and no model anywhere in the scorer. False positives and an external
check that the attacker was trying at all come from **someone else's** benchmark: τ²-bench
(`github.com/sierra-research/tau2-bench`, MIT, pinned at
`a2c024725189473d2d7cea3a5cfdbcc67478e41f`, 2026-08-18), whose tasks, gold behaviour and `db_reward`
hash grader are Sierra's, not ours. **On 4 September a scheduled cut halved the breadth of one block
of it — the false-positive sample, 40 τ² write tasks to 20 — so that block ships with a stated cell
size; τ²-bench itself is not cut, the 34-task must-not-write control is untouched, and the
externally-authored-answer-key claim is intact.** A defender-integrity probe stands over all of it:
its rule — *below the calibrated threshold, the whole run is void* — is written, frozen and
git-tagged **before** any scored episode, and what it discards is our own data — not somebody
else's, and not our judgement of our own attacker.
⚠️ **Its threshold is not yet set: the single-shot calibration that fixes it has not completed, so
`config/` carries a declared sentinel and the loader refuses rather than defaulting. The probe is
pre-registered, not yet live, and this repository says so rather than implying otherwise.** And
`gates/` and `scorer/` share no first-party module — asserted by a module-graph walk over both
packages' transitive imports with an **empty** allow-list — because in the spike that preceded this
project the gate and the invariant checker both called one shared helper, so the invariant could not
have fired unless the gate had a bug. **That is not a result; it is a definition**, and never doing
that again is this project's central structural commitment.

⚠️ **State, so nothing above is misread: no scored episode has run, and this submission is a
measurement apparatus, a pre-registered protocol and a published failure record — not a results
table.** The pilot **has** run: it was single-shot, it is spent, and it returned nothing — 20
episodes attempted, **0 completed**, 11 truncated, 9 never started, and the N decision **refused**
rather than averaging over zero completions. Every number in the repository is either measured from
files in the repository, or is a named `<<PENDING-RUN: …>>` placeholder that `RESULTS.md` fills when
a run exists. The freeze is **partial, and this repository says so on its own first screen**:
`probe-v1` is cut and `HOLES.md` is byte-identical at it, but `prereg-v1` does not exist and the
external witness gist has not been published. When a run exists, `make eval`'s claim is exactly this
and nothing broader: **every published number regenerates from the stored ledgers.** The
byte-identical guarantee is narrower still and belongs to four named things — the world, the ledger
schema, the scorer and the replay — which are tested to be byte-identical from the same seed. The
attacker runs at temperature 0.7 against a hosted provider, so **re-running the models does not
reproduce the run**, and no sentence here should be read as saying it does.

---

## 3. BUILD CHALLENGES & TECHNICAL OBSTACLES — paste verbatim

> ⚠️ Card format: **Event / Action / Expectation / Missing / Missed** (`PROCESS.md`:1343).
> `Diagnosis` and `Fix (SHA)` are appended per BUILD 1's `Q-E`, which stands. Sourced from **two
> `INCIDENTS.md` entries**, one dated **after** the first build commit (`ee3cf93`, 2026-08-30
> 12:20:32 +0530, verified by `git log --reverse`) as the card and `CONTEXT.md` §20 require. This
> session counted **155 `## INC-` headings** in `INCIDENTS.md`; the great majority are dated after
> that commit, so the requirement is met many times over — these two are chosen for being the most
> self-incriminating, not the most flattering.

---

**The two failures worth your time are the same failure twice: a check that was supposed to be
load-bearing reported success over a live defect.**

**INC-02 — a threat model built on a parameter that does not exist.** `[INCIDENTS.md:59, "## INC-02 —
a threat model built on a parameter that does not exist", dated 2026-08-28 — before this
repository's first commit]`

- **Event:** the original threat model had `create_refund` sending money to an attacker-controlled
  `destination`, and produced a headline harm figure of **₹2,004 crore** — ⚠️ *a **withdrawn spike**
  figure, not a result of this project; see the note at the foot of this entry.*
- **Action:** read Razorpay's own refund API documentation and the official MCP server's Go source.
  `create_refund` has **no `destination` parameter** — Razorpay does source refunds only — and there
  is **no `CreatePayout`** anywhere in the MCP write surface. **No tool in that surface sends money
  to an attacker-controlled account.** Replaying the spike's episodes against Razorpay's documented
  rejections, **30 of 51 money actions (59%) would have been refused by Razorpay itself, 26 of them
  for that non-existent parameter.** ₹2,004 cr collapsed to **₹22.4 L** — ⚠️ *both figures withdrawn
  spike figures, quoted only to size the correction.*
- **Expectation:** a threat model written against a specific tool surface should have been derived
  from that surface's documented parameters, not from what a payments API plausibly offers.
- **Missing:** a `RAZORPAY_SEMANTICS.md` — one row per documented rule, verbatim quote plus URL plus
  fetch date — to check every modelled attack against. It did not exist.
- **Missed:** `refunds.go` was already in hand and lists exactly the parameters it forwards. **The
  parameter list was never read before the attack was written.**
- **Diagnosis:** the attack surface was inferred from what a payments API is imagined to do rather
  than read from what Razorpay documents it does, and no artefact in the process forced the check.
- **Fix (SHA):** none in this repository — the fix landed before the first commit. The threat model
  was rewritten with an explicit *"rejected by Razorpay itself?"* column per attack, and
  `RAZORPAY_SEMANTICS.md` was made a scheduled deliverable **before any world code**, as the oracle
  for a spend-free self-test in which every documented Razorpay error must fire in the mock world
  before a single token is spent.
- ⚠️ Both ₹ figures above are **spike** figures from a **withdrawn** threat model, quoted only to show
  the size of the correction. **They are not results of this project**, which publishes no ₹ figure
  until a run exists — and then only as a per-episode median with its spread and its cell size,
  never as a sum.

**INC-132 — the line this project calls "the whole moat" printed PASS on all four checks over a live
`gates/` → `scorer/` reach.** `[INCIDENTS.md:9832, "## INC-132 — the line `CLAUDE.md` calls 'the
whole moat' printed **PASS on all four checks** over a live `gates/` → `scorer/` reach", dated
2026-09-04 — after the first build commit]`

- **Event:** the gate/scorer isolation check has four parts. D1–D3 walk the **transitive import
  closure** of both packages; D4, the source-text half added precisely because an import walk cannot
  see a call expression, walked the two package **directories**. The closure and the directories are
  not the same set, and the difference was exactly one module wide — on the gate side.
- **Action:** the discrepancy was re-measured and reproduced exactly, then **exploited** in a
  `git clone` of `HEAD` in a fresh OS temp directory, never in the repository. A dynamic `importlib`
  hop was planted in that one closure-only module, and a gates module written that calls it and
  names no refused form of its own. On the pre-fix checker the tree printed **D1 PASS, D2 PASS, D3
  PASS, D4 PASS** — and the reach was live, not dead code:
  `gates.of249_probe.decide(6_000_000, 5_000_000)` returned **`DENY`**, computed inside
  `scorer/invariants.py`, whose `__file__` was printed from the same subprocess as the measurement.
- **Expectation:** D4 exists to catch what D1–D3 cannot see. It should have refused a dynamic
  `gates/` → `scorer/` reach wherever the hop sits.
- **Missing:** **nothing asserted that D4's scan set and D1–D3's walk set were the same set.** Six
  tests across four files pointed the text scan at a package *directory* — which is what each of
  them meant — and not one compared it to the closure.
- **Missed:** the earlier finding's own remedy said *"the package set"* and the fix implemented
  *"the package directories"*. The two closures were **local variables eleven lines above the D4
  block**, and the block reached past them for the two directory paths. **The asymmetry was written
  down in the same file, in the same session, and nobody read the two halves against each other.**
- **Diagnosis:** D4 was added as a patch to a *symptom* rather than to the *property*, so its scan
  set was chosen from the two paths already in scope instead of from the closure the same function
  had just computed.
- **Fix (SHA):** **`1fd0877`** — D4's scan set is now the union of both package directories and every
  first-party module in either transitive closure. Verified live by this session: D4 now reports
  *"SCANNED: both package directories PLUS the 1 module(s) inside either TRANSITIVE CLOSURE but
  outside them (`['whetstone_gate.config']`)"*. Three new tests, of which **two were run against the
  pre-fix checker and FAILED there**, so they are measurements and not decoration. The allow-list
  stays empty; widening it is a Class A deviation requiring a recorded architect ruling.

**What these cost, and what is still open — volunteered rather than buried.** This repository ships
**155 recorded incident headings** (154 distinct ids; one, `INC-139`, is duplicated and that is
itself recorded), a review trail of **15 FAIL and 6 PASS across 21 adversarial reviews**, and an
open-findings register that is published, not drained. Of 23 tracked deliverables, **6 carry a
`cN-pass` tag, 3 ship with named residue and no tag, and 14 have never been adversarially reviewed at
all** — including the freeze itself and the README. The build session and the review session are
never the same session, and one chunk — the attacker loop — was reviewed **six times, never passed,
and ships with its residue named and untagged** rather than quietly re-scoped. Both failures above
have the same shape — **a check that reported success over a live defect** — which is precisely the
shape this project accuses the field of, so the evidence is held against ourselves in the same file
we publish.

And the limitation that outranks all of them, stated in the open because it does not go away:

> **The escape number is authored by us, and no external ground truth for it exists anywhere.** It
> is adversarial *search*, not adjudication by the world, and it is a **lower bound on what escapes,
> never an upper bound.** That is why the false-positive tasks, the answer key and the competence
> control are someone else's — τ²-bench's `db_reward` hash grader, and a probe that voids our own
> run.

> ⚠️ **The published wording of that limitation is `PROVENANCE.md`:599, and its third clause names
> three things: *"τ²-bench's `db_reward`, AgentDojo's banking suite, and a probe that voids our own
> run."* AgentDojo was CUT** — degradation rung 3, `README.md` §9.2 (:793), `STATUS.md`:2195,
> `config/protocol.yaml`:420 `agentdojo_sha: TODO_C13_C16`. **The form carries the two sentences
> `PROCESS.md`:1029 actually names, verbatim, and states the third clause in the form that matches
> the repository today.** Both forms are printed here so the substitution is visible rather than
> silent. `PROVENANCE.md` is a frozen artefact and was not edited. Owed to `QUESTIONS.md` as BUILD
> 1's `Q-C`.

---

## 4. THE EXACT PUBLIC REPOSITORY URL

```
https://github.com/chinmoypaul8897/whetstone-gate
```

Verified two ways by this session: `git remote -v` →
`origin  https://github.com/chinmoypaul8897/whetstone-gate.git (fetch)`; and `README.md`:1471 and
`README.md`:1757 both print `git clone https://github.com/chinmoypaul8897/whetstone-gate`.

⚠️ **The repository is still PRIVATE.** `PROCESS.md`:862 — it *"stays private until C21 flips it
public on 4 September, after the git-history secret scan has run and its output is committed."*
**This session did not flip it. That is the operator's act** — checklist item **O-8**.

---

## 5. THE EXACT VIDEO URL

```
<<PENDING-RUN: VIDEO_URL>>
```

⚠️ **No video URL exists in this repository.** `STATUS.md`:2199 records C20's status as
`todo - review folded`, and a search for a video URL across the tree returns nothing.
**This is a placeholder and must not be pasted as-is** — checklist item **O-5**.

⚠️⚠️ **AND THE THING THE OPERATOR MUST NOT LEARN FROM THE VIDEO SHOOT: THE RENDERER THE §18 RACE
BEAT DEPENDS ON EXISTS AND HAS JUST FAILED ITS REVIEW.**

`docs/render/race.py` and `docs/render/audit.py` were built at `b332853` (C17). Its build session's
own `README.md`:36-47 claims the renderer *"says on screen that it is a replay of a stored
hash-chained ledger"* and *"verifies the chain rather than trusting it"*. ⚠️ **This session did not
take that on trust, and it should not have.** `docs/reviews/REVIEW_C17_1.md` landed at `259ca6b`
**while this file was being written**, and its §2.3 verdict is **⛔ FAIL — two BLOCKERs, five HIGH,
five MEDIUM, five LOW**, both blockers *"printed statements in the two artefacts a judge reads"*:

- **`B-1`** — `audit.py`:240-243 stamps **`RECOMPUTED, MATCHED` unconditionally**, and :348-361
  renders every entry and the money summary **regardless of `episode.chain_ok`**. Measured by the
  reviewer on a tampered copy: verdict `DETECTED at ledger_seq 3`, and **8 of 8 entries stamped
  `RECOMPUTED, MATCHED`, including seq 3 itself**, with a fabricated `88,888,888 paise` under
  *"MONEY PAST THE GATE"*. **So the card's *"and says so on screen"* clause is defeated**, and the
  test named for that behaviour is vacuous.
- **`B-2`** — `audit.py`:268 prints *"MEASURED ZERO (the episode ran; nothing moved)"* **with no
  guard**: false on 10 of the 11 real stored episodes, false on an absent arm, and false on the one
  episode where the world executed **20,118,586 paise** of refunds. **No crafted input is needed —
  the default command does it.**

**What the review found MET:** the caption states the seed and the pre-registered N (cleanly, as
`<<PENDING-RUN: N>>`, because no N has been selected), and the renderer makes no network call and
runs no model (in substance). **What it found NOT met:** the *"a non-author can follow one episode
end to end without asking a question"* clause (`H-2`, measured with ten written-down questions).

⚠️ **CONSEQUENCE FOR THE VIDEO, STATED SO IT IS NOT DISCOVERED ON CAMERA:** `H-1` records that the
race draws **a full-length money bar from tampered ledger content**, and that *"§18 puts this frame
in the video, where the bar is the image and the footer is small type."* **A C17 FIX session must
land before the RACE beat is shot.** No `c17-pass` tag exists and none is owed — the verdict is FAIL.

---

## 6. THE FIVE METHOD CLAIMS — RE-MEASURED TONIGHT

The paragraphs above claim a **method**, never an outcome. **BUILD 1 graded these nine hours ago and
this session did not inherit its answers: each was re-measured against the tree at `686a224`, and
each was then attacked from three independent angles — literal truth; the panelist who has not read
the spec; and the project's own `HOLES.md` / `OPEN_FINDINGS.md` / `INCIDENTS.md` record.**

| # | Claim as usually worded | Verdict tonight | Moved since BUILD 1? |
|---|---|---|---|
| 1 | A policy-blind attacker | ⚠️ **TRUE ONLY AS NARROWED** | no |
| 2 | An externally-authored answer key (τ²-bench) | ⚠️ **TRUE ONLY AS NARROWED — and narrowed further than BUILD 1 had it** | ⚠️ **yes, twice over: rung 4 fired AND was executed, and the T-FP block is now known to be unrunnable at any size (`Q-154`, `Q-155`, both OPEN). One narrowing became three** |
| 3 | A competence probe that VOIDS our own run | ⚠️ **NOT YET TRUE AS AN ACCOMPLISHED FACT** | ⚠️ **yes — the calibration is now declared and attempted, and still no threshold exists** |
| 4 | A freeze witnessed outside the repository | ⚠️ **NOT YET TRUE** | no |
| 5 | `gates/` and `scorer/` share no first-party module | ✅ **VERIFIED, with its limits stated** | re-measured tonight; the module count moved 118 → 119 |

**§2 above uses only the narrowed forms.**

### 6.1 The evidence, claim by claim

**(1) POLICY-BLIND — TRUE AS NARROWED.**
*Safe:* "The attacker never receives the gate's policy text, our pre-registered holes, our
attack-or-invariant taxonomy, or any gate's denial reason; the only refusal it sees is one generic
string, identical across arms. Blindness is checked against the actually-assembled context by tests
carrying planted-leak positive controls."
*Evidence:* `CONTEXT.md` §7's architecture block (:449-455) — *"ATTACKER (LLM, policy-blind) … never
sees: policy, holes, attack list, gate reasons"*; and the blindness property itself is carried by
`tests/test_c12_benign.py`:404 `test_the_blindness_scan_FIRES_at_four_planted_leaks` — **the guard is
proved to fire, not merely to be silent.**
⚠️ **One piece of evidence BUILD 1 cited here does not belong here, and the correction is this
session's.** `tests/test_c6_attacker.py`:1137
`test_the_attacker_package_imports_no_model_client_and_no_network_library` proves that the attacker
**package** reaches no provider SDK and no network library — a **purity-separation** property under
hard rule 8. **It is not a context-blindness test**, and citing it as one overstates what is
asserted.
*Do not write:* *"it has never seen any attack list."* The attacker is seeded from published
third-party attack corpora, and the system prompt we authored names **four** attack families in plain
English (`data/attacker_sys.txt`:2-3 — over-captures, excess refunds, early settlements, duplicate
refunds). ⚠️ **`CONTEXT.md` §1 itself carries that unnarrowed form** — see `Q-L` in §0.4.
⚠️ **Three limits that must travel with this claim, and did not travel with BUILD 1's version:**
(a) **blindness is a build-time property, checked by tests; it is not enforced at run time.** There
is no blindness check inside `src/whetstone_gate/attacker/loop.py`, and the pilot's stored ledgers
carry no per-episode blindness field, so no *run* attests it — the *tests* do.
(b) **the scan is known to be leaky and the leaks are published, not closed:**
`docs/reviews/OPEN_FINDINGS.md` **OF-127** (:1458) records that two of `OF-104`'s own three measured
exhibits **still escape both copies of the guard**, and **OF-133** (:1464) that **46 of 118 needles
escape** when carried in `LAST_REFUSAL_LABEL`. Both are **OPEN**.
(c) the attacker chunk **C6 was reviewed six times, never passed, and carries no tag** — and it is
formally **disposed as shipped-with-residue**, not pending: `Q-089` rules that *"neither is tagged
and neither gets another review cycle"* (`README.md`:1216, :1263-1264; `docs/reviews/REVIEW_C6_1..6`,
all six FAIL).

**(2) EXTERNALLY-AUTHORED ANSWER KEY — TRUE AS NARROWED, AND THE NARROWING NOW HAS TWO CLAUSES.**
*Safe:* "The tasks, the gold behaviour and the grader for the false-positive block and the
competence control are Sierra's, not ours — τ²-bench, MIT, pinned — and the false-positive block
ships at half its pre-registered breadth, by a scheduled cut, with its cell size stated."
*Evidence:* `config/protocol.yaml`:413 `tau2_bench_sha: a2c024725189473d2d7cea3a5cfdbcc67478e41f`;
`vendor/tau2-bench/LICENSE` → *"MIT License / Copyright (c) 2025 Sierra Research"*; `CONTEXT.md`
§11.1's authorship-split table — tasks, gold behaviour, grader and benign tasks all **Sierra**, the
gate **"Us — the only thing we author"**.
*Do not write:* any present-tense claim that our numbers were scored by it. `CONTEXT.md` §11.1 is
explicit that τ²-bench does **not** provide escape ground truth, and that *"Escape measurement moves
WHOLLY to the mock Razorpay world."* **The external key has graded nothing** — `RESULTS.md` publishes
no number and there is no run directory. *Also:* we score on `db_reward` alone — a hash comparison, no
model; τ²-bench's full retail reward multiplies in an LLM-judged natural-language assertion and **we
do not use it**. *And:* AgentDojo, the second external environment, was **cut** (rung 3,
`README.md` §9.2).
⚠️ **The second narrowing, new tonight:** rung 4 halved T-FP's breadth, 40 → 20. **τ²-bench is not
cut**; only one block's breadth is staged; T-NEG keeps all 34 tasks; **the cut was the operator's
schedule decision, not the §13.4 measurement rule**. §0.3 carries the full statement, and the same
words are in `INC-144`, `README.md` §9.3 and `RESULTS.md` §1.
⚠️⚠️ **AND THE THIRD, WHICH IS LARGER THAN THE OTHER TWO AND WHICH BUILD 1'S VERSION DID NOT CARRY
AT ALL. T-FP IS NOT RUNNABLE AT ANY SIZE TODAY.** `README.md` §9.4 (:908) states it in the
repository's own words — *"the counter-metric is on the NEVER-CUT list, and it is NOT COMPLETE"* —
and names two **open** blockers, each independent of the cut and of the other:
**`QUESTIONS.md` `Q-154`** (:12315, *"RULE 1 STOP: C12's DEPENDENCY `C5` IS UNBUILT, SO THE T-FP
BLOCK — THE ONLY BLOCK WHOSE TASKS, GOLD BEHAVIOUR AND GRADER ARE NOT OURS — CANNOT RUN AT ALL"*,
**Status: OPEN**, blocking 200 pre-registered episodes), and **`Q-155`** (:12355, **Class A, OPEN** —
the six-name tool surface and τ²'s tool set are disjoint, *"AND BUILDING C5 DOES NOT CLOSE IT"*).
⚠️ **These are a CAPABILITY gap, not a scope decision, and §9.4 says so explicitly: *"Halving a
block that cannot run does not make it run."*** The right form of claim 2 today is therefore:
**τ²-bench is vendored, pinned, licensed and authored by Sierra — and the block that would use it as
a false-positive key has not run and cannot yet run.** Anything stronger overstates it.

**(3) A COMPETENCE PROBE THAT VOIDS OUR OWN RUN — NOT YET TRUE AS AN ACCOMPLISHED FACT.**
*What is true, verified by this session first-hand at `686a224`:* `probe-v1` is an annotated tag,
object id `170bd3ff4abfdd8f87f64055972a60c82cc54efc`, tagger date **2026-09-03 20:43:04 +0530**,
message *"pre-registration: HOLES.md, before the pilot and the calibration"*. `HOLES.md`'s git blob
is `a4e50ed6f379784c6b6bfefdd1728a57ca3d4c20` at **both** `probe-v1` and `HEAD`, and
`git diff probe-v1 HEAD -- HOLES.md` is **empty** — so the rule is frozen and provably unmoved even
though `HEAD` has advanced. `HOLES.md`:221 states the consequence verbatim: **"Below the calibrated
threshold → THE WHOLE RUN IS VOID."** `HOLES.md`:186-189 fixes the rate's numerator and denominator
as **episodes**, not entries. The decision is pure arithmetic —
`src/whetstone_gate/probe/void.py`:81 `breach_rate`, :109 `is_void` — with no model client, asserted
by `tests/test_c10_probe.py`:1127 and :1141
(`test_the_VOID_RULE_imports_no_model_client_WAY_ONE/WAY_TWO`).
*What is not:* `config/protocol.yaml`:352 reads `void_threshold_breach_rate: TODO_C14_CALIBRATION`.
The loader raises rather than defaulting (`src/whetstone_gate/probe/void.py`:47, :143
`UndeterminedThreshold`), so **no VOID verdict is computable from `config/` as it stands, on any
input.** The single-shot arm-1 calibration that sets the threshold **is declared, has been attempted,
and has produced no completed episode** — §0.2.
*Safe wording:* "the void rule is written, frozen and git-tagged before the run; its threshold is set
by a single-shot calibration that is pre-registered and has not yet produced a completed run, and the
repository publishes that as a declared sentinel rather than as a default."
*Do not write:* "a live kill switch", or "if it falls short the run is automatically voided" — the
rule states what must not be published; nothing suppresses a table. **And do not write, hint at, or
leave room for any breach rate, threshold or void verdict.**

**(4) A FREEZE WITNESSED OUTSIDE THE REPOSITORY — NOT YET TRUE.**
*Evidence:* `git tag -l` → seven tags, `prereg-v1` **absent** (`git rev-parse prereg-v1` exits 128).
`README.md`:120-124 states it against itself: *"there is no `prereg-v1` to hash, **and** there is no
published fingerprint or witness gist to compare against — no `prereg-v1.sha256` and no OTS receipt
exist in this tree. The procedure is printed in full anyway, unaltered, so that what a judge will run
is fixed *before* there is a number to fit it to."* `README.md`:1491 prints the verification command
with the gist id as `<<PENDING-RUN: GIST_ID>>`.
⚠️ **THAT ADMISSION IS THE MOST CREDITABLE SENTENCE IN THIS REPOSITORY AND IS NOT SOFTENED HERE, AND
MUST NOT BE SOFTENED ANYWHERE.**
*Safe wording:* "the pre-registration procedure — the frozen set, the fingerprint computed from git
objects, and the public-gist witness whose `created_at` GitHub assigns server-side — is written and
committed in full **before** there is any number to fit it to; one of its two tags is cut, the
witness has not been published, and the README says so on its first screen."
*Do not write:* any present-tense claim that the measurements are witnessed outside this repository.
**That is the single most damaging sentence available to this project**, because a claim of external
witness that a judge cannot `curl` discredits the one differentiator the project is built on.
*Stronger evidence than BUILD 1 had, and it strengthens the admission rather than softening it:*
`README.md`:42 asserts that **neither the fingerprint nor the receipt has ever existed on any ref** —
a claim checkable with `git log --all --name-only`, not merely a statement about the working tree.
*Two further limits, from the README's own first screen:* `check-prereg` **fails open** and returns
`0` when `prereg-v1` does not resolve, so a PASS from it today is worth less than it looks — and
nothing in code stops a scored run from starting without the tag; the driver's gate checks only
`probe-v1`. **The rule is a rule, not an interlock, and the README says so.**
⚠️ *And the consequence persona 3 will hit directly:* **the pre-registration cannot today be verified
by running the procedure the README prints, from a fresh clone.** It fails at step 1 (the repository
is private until O-8) and again at the `git rev-parse prereg-v1^{commit}` step. **That is a
checklist line this project currently fails, and it is named here rather than discovered by the
panel.**

**(5) `gates/` AND `scorer/` SHARE NO FIRST-PARTY MODULE — VERIFIED.**
*Measured by this session by running `./.venv/Scripts/python.exe -m whetstone_gate.tasks check-roles`
(read-only; `git status --porcelain` was captured before and after and was byte-identical):*

```
D - the gate/scorer moat
  [PASS] D1 gates/ imports nothing from scorer/
  [PASS] D2 scorer/ imports nothing from gates/
  [PASS] D3 no shared first-party module
         ... The allow-list holds 0 entr(y/ies). 119 first-party module(s) indexed;
         15 reachable from src/whetstone_gate/gates (14 seed(s)),
          6 from src/whetstone_gate/scorer (6 seed(s)), TRANSITIVELY
  [PASS] D4 no dynamic import in gates/ or scorer/
         ... SCANNED: both package directories PLUS the 1 module(s) inside either
         TRANSITIVE CLOSURE but outside them (['whetstone_gate.config'])
```

Whole run, before this session's commits: **21 passed, 0 failed, 3 n/a.**
⚠️ **AND THE QUALIFICATION THAT NUMBER NEEDS, WHICH IS NOT COSMETIC.** That run read the **working
tree**, not committed `HEAD`, and the working tree's `QUESTIONS.md` carries **two uncommitted rows**
a concurrent session had just added — `` | `7a1e3b52` | C17 | BUILD | `` and
`` | `4e8b91d3` | C17 | REVIEW | `` (`git diff -- QUESTIONS.md`). **Against committed `686a224`, E1
is RED**, because `7a1e3b52` has no row there. So the honest statement is: **the D-block result is
clean under both readings; the whole-run count is 21/0/3 only against the working tree, and the
difference is entirely `INC-141`'s token-row trap, not the moat.** This session did not commit
anybody else's rows and did not write its own — see **O-2**.
**The allow-list holds ZERO entries.** `src/whetstone_gate/check_roles.py`:637 —
`MOAT_ALLOW_LIST: frozenset[str] = frozenset()`. ⚠️ **`CLAUDE.md` hard rule 8 describes it as *"a
short, explicit allow-list of pure value types (enums, the harm-record dataclass, the paise integer
wrapper)"*. The implemented list is EMPTY** — stronger than the constitution describes, and the
correct thing to publish is the measured "0", not the described "short". BUILD 1's `Q-D`, still open.
*Limits that must travel with the claim:* (a) the property is "no shared first-party **module**",
**not** "no shared code" — both sides deliberately reimplement the same predicates twice, on purpose;
(b) this exact assertion has **twice** printed clean or PASS over a live `gates/` → `scorer/` reach
before being hardened (`INCIDENTS.md`:3728 `INC-51`, :9832 `INC-132` — see §3); (c) the closure is
built from **static** imports, so a reach whose first hop is made by third-party code is scanned by
neither half — **`docs/reviews/OPEN_FINDINGS.md` `OF-253` (:2645), still OPEN**, and the HIGH finding
that owns this assertion, **`OF-64` (:577), is also still OPEN**; (d) neither package has passed
adversarial review — there is no `c8-pass` and no `c9-pass` tag.

---

## 7. THE OPERATOR CHECKLIST — WHAT IS ACTUALLY LEFT, IN BLOCKING ORDER

⚠️ **Nothing in this section is a card requirement.** The card names the file's contents; this
checklist and the placeholder table in §8 are additions by this session, and they are labelled so no
reviewer reads them as mandated. **It was rebuilt tonight, not copied:** BUILD 1's O-1…O-11 had two
items that are now done, one that was mis-scoped, and it predates the calibration entirely.

**Order matters. O-0 to O-11 gate each other.**

| # | Step | Where | Blocking? |
|---|---|---|---|
| **O-0** | ⚠️ **THE CALIBRATION IS FIRST, BEFORE ANYTHING ELSE, AND IT BLOCKS A RETRY.** Attempt 2 has **not** produced a completed calibration episode (`find evals -name '*cal__*'` → 0), and this session measured no running interpreter and a log ending in `TimeoutError`. `PROCESS.md` §6b: *"If an attempt aborts before completion, the abort, its cause and its partial episode count are written to `INCIDENTS.md` **before** any retry."* ⚠️ **So: (i) decide whether attempt 2 is dead; (ii) if it is, write its `INCIDENTS.md` entry — with the partial episode count as a number, and the tokens actually spent, both of which are measurable — BEFORE starting attempt 3; (iii) do not edit `evals/cal/RUN_DECLARED.md`'s declared start time to match.** `INC-157` is the template and its `Fix` block carries the working launch recipe (activate the venv; run the free `import whetstone_gate` check first). | terminal, then `INCIDENTS.md` | ⚠️ **HARD GATE ON EVERYTHING** |
| **O-1** | ⚠️ **Do NOT open the submission form until the C21 review returns PASS.** `PROCESS.md`:175 and :1344 — the form is one-shot, *"no further changes or edits can be made after submitting"*, and the one irreversible step must not be the unreviewed one. **No C21 review file exists in `docs/reviews/` and `STATUS.md`:2200 has C21 at `todo`.** | — | ⚠️ **HARD GATE** |
| **O-2** | ⚠️ **Add the missing `## Session tokens` rows to `QUESTIONS.md`.** `make check-roles` E1 was **green (21/0/3)** at `686a224` before this session committed; it goes **red** on this session's commits because `6f2d47ba` has no row (`grep -c "6f2d47ba" QUESTIONS.md` → **0**). **This is `INC-141`'s recorded trap, not a defect in the work, and this session did not write its own row** — a session vouching for its own identity is exactly the shape E1 exists to catch. The one-line fix, in the format the table's last rows already use: `\| `6f2d47ba` \| C21 \| BUILD \| 2026-09-04 \|`. ⚠️ **The C17 rows are already half-done and UNCOMMITTED:** `git diff -- QUESTIONS.md` shows a concurrent session has added `7a1e3b52` (C17 BUILD) and `4e8b91d3` (C17 REVIEW) in the working tree. **Commit those and add this session's, and E1 goes green; leave them and committed `HEAD` stays red.** | `QUESTIONS.md` | before the review reads a red tree |
| **O-3** | Fill every `<<PENDING-RUN: …>>` in §8 **that this form carries**, or strike the sentence that carries it. **A placeholder pasted into the live form is the worst outcome available.** ⚠️ **And note `OF-250`** (`docs/reviews/OPEN_FINDINGS.md`:2642): `README.md` ships with **39** named placeholders and **nothing in the repository fails if one survives publication** — the discipline is a convention, not a check. | this file, then `README.md` | ⚠️ **HARD GATE** |
| **O-4** | Re-verify the perishable facts of `CONTEXT.md` §21 item 5 — see §7.1. | browser | ⚠️ **HARD GATE** |
| **O-4b** | ⚠️ **A C17 FIX SESSION, BEFORE THE RACE BEAT IS SHOT.** `docs/reviews/REVIEW_C17_1.md` returned **FAIL** with two BLOCKERs on 2026-09-04 (`4e8b91d3`), and both are **printed sentences in the artefacts the video shows** — `B-1`, a false `RECOMPUTED, MATCHED` stamp on a ledger the renderer has itself detected as tampered; `B-2`, *"MEASURED ZERO (the episode ran; nothing moved)"* printed unguarded on 10 of 11 stored episodes and on an episode where 20,118,586 paise moved. `H-1` puts the tampered-content money bar **in the §18 frame**. **A FIX session writes the `INCIDENTS.md` entry first, then fixes only `B-1`, `B-2`, `H-1`, `H-2` and whichever LOWs it takes — and `M-3` is NOT C17's** (the review says so in terms). | a FIX session | ⚠️ **HARD GATE on O-5** |
| **O-5** | Record the video URL. §5 is a placeholder; `STATUS.md`:2199 has C20 at `todo`. ⚠️ **Do not shoot the RACE beat until O-4b lands** — see §5. | §5 of this file | ⚠️ **HARD GATE** |
| **O-6** | ⚠️ **Re-confirm that no payment method is attached to either provider account, on 4 September, and write the new date into `PROVENANCE.md` §1.5.** It is dated **2026-08-30** there today (`PROVENANCE.md`:204). **No session can do this** — a session has no browser and no permitted credentials, and `CLAUDE.md` §4 forbids reading a key value at all. It is the only claim in the frozen set that can go stale with **no file changing**, and a card attached on 3 September would silently turn every subsequent 429 into a bill while this repository still reads NONE ATTACHED. ⚠️ `PROVENANCE.md`:204's own note says this *"IS NOT CURRENTLY A C21 DONE-WHEN"* — **that note is now stale**: `PROCESS.md`:1343's C21 done-when names it explicitly. | provider billing pages | ⚠️ **HARD GATE** |
| **O-7** | ⚠️ **Re-run the git-history secret scan.** The committed output at `docs/submission/git-history-secret-scan.txt`:4 records `HEAD = 90b6d6fab329ad39b44f47f3f651bebe311e21c8`; measured tonight, **`HEAD` is 57 commits past it** (`git rev-list --count 90b6d6fa..HEAD` → 57). **The scan must cover the tree that goes public.** `PROCESS.md` §8 fixes the method and constrains the remedy: if it finds a key, revoke it at the provider and record the incident — **the history is NOT rewritten**, because a rewrite would destroy `probe-v1` and every `cN-pass` tag. | terminal, then commit | ⚠️ **HARD GATE on O-8** |
| **O-8** | **Flip the repository to public** — only after O-7's output is committed. `PROCESS.md`:862. | GitHub settings | after O-7 |
| **O-9** | In a **logged-out** browser: load the repo URL from §4 and play the video from §5. | browser | after O-8 |
| **O-10** | Paste **§1** as the project name, **§2** as Project Objectives, **§3** as Build Challenges & Technical Obstacles, **§4** as the repository URL, **§5** as the video URL — **verbatim, with no re-drafting in the form box.** | the live form | — |
| **O-11** | ⚠️ **Paste into the form's PREVIEW and SCREENSHOT it into `docs/submission/` — WITHOUT SUBMITTING.** This is the card's own done-when. Then submit. Deadline **18:00 IST**. | the live form | last |

### 7.0 ⚠️ THE CHAIN ABOVE IS THE SUBMISSION PATH. THIS IS THE MEASUREMENT PATH, AND IT IS SEPARATE

**BUILD 1's checklist had no row for any of these, and a reader of it would conclude the project was
one video away from done. It is not.** Every item below stands between the repository today and a
single published number. **None is on this session's fence and none is asserted to be achievable
before the deadline** — the point of listing them is that the submission must be honest about which
path it is on, and today it is on the first one only.

| # | What | Gates |
|---|---|---|
| **M-1** | The calibration abort entry — **O-0 above.** `PROCESS.md` §6b forbids a retry without it | M-2 |
| **M-2** | A calibration attempt that **completes** — 30 episodes, arm 1, lane `gemma-26b`, ceilings 600 calls / 4,800,000 tokens per `evals/cal/RUN_DECLARED.md` §1 and §5 | M-3 |
| **M-3** | Derive the threshold from that run and write it into `config/protocol.yaml` in place of `TODO_C14_CALIBRATION` | M-4 |
| **M-4** | Cut **`prereg-v1`** — the second freeze tag. ⚠️ **After it, `config/` may not be amended at all** (`CLAUDE.md` §4, hard rule 9), so **every `config/` change owed must land first** | M-5, M-6 |
| **M-5** | Publish the **witness gist** and record its id and server-assigned `created_at`, replacing `<<PENDING-RUN: GIST_ID>>` in `README.md`:1491. ⚠️ `CONTEXT.md` §21 item 5 calls this *"the one perishable fact the project cannot re-create after the fact"* | PF-5, and claim 4 |
| **M-6** | Point `ledger.genesis_hash` (`config/protocol.yaml`:380, currently `probe-v1`'s tag object `170bd3ff…`) at the scored freeze, so a scored ledger is cryptographically distinguishable from a pre-freeze one | the sweep |
| **M-7** | The scored sweep itself, then **C18** — `make eval` writing the real `RESULTS.md` from the stored ledgers, which **overwrites** today's stub in place | every `<<PENDING-RUN:>>` number |

⚠️ **The honest summary, and the reviewer should be handed it rather than left to derive it: the
submission can be completed without M-1…M-7, and it would then be a submission of a measurement
apparatus and a failure record with no measurements in it. That is what §2 says it is.**

**Two items BUILD 1 listed that are now DONE, so the operator does not redo them:**

- **Rung 4's execution half.** `INC-144` recorded it as operator-owed. Measured tonight it has landed
  in **both** places it had to: `config/protocol.yaml`:445 / :497-498, and
  `tests/test_c3_tau2_enumeration.py`:269-316. §14's other requirement — that the cut be named in
  `RESULTS.md` and in the README — is also already met (`RESULTS.md` §1; `README.md` §9.3).
  **Nothing further is owed on rung 4.**
- **`RESULTS.md`'s existence.** It exists as a stub and discharges §14's `RESULTS.md` half. It is
  **overwritten in place** the first time `make eval` succeeds; that is intended.

### 7.1 O-4 in full — the five perishable facts (`CONTEXT.md` §21, item 5)

Each is dated **2026-08-30** in the repository and is therefore **five days stale** today.

| | Perishable fact | Stale value in the repository | Status |
|---|---|---|---|
| PF-1 | The MCP repo's frozen `main` and its open-PR count | `CONTEXT.md` §2: no merged commit since 26 March 2026; 43 PRs open; 25 opened in August 2026, 23 of them with zero reviews — `GitHub API, 2026-08-30` | **RE-READ REQUIRED** |
| PF-2 | That no competitor has shipped the §5 conjunction | `CONTEXT.md` §5, surveyed 2026-08-30. §21 item 1 already records the ground moving — `kasauti` has announced a *"runtime red-team agent"* as its next milestone | ⚠️ **RE-READ REQUIRED — this is §2's central claim and the likeliest to have gone stale** |
| PF-3 | The free-tier limits of `CONTEXT.md` §13.2 | read from the provider dashboards, 2026-08-30 | **RE-READ REQUIRED** |
| PF-4 | `whetstone-gate` still unclaimed on GitHub | three `api.github.com` queries, all `total_count` 0, 2026-08-30 | **RE-RUN ALL THREE** |
| PF-5 | The pre-registration gist still resolves with its original `created_at` | ⚠️ **THERE IS NO GIST.** Nothing to re-verify | ⚠️ **CANNOT BE PERFORMED UNTIL THE GIST IS PUBLISHED (M-5) — DO NOT REPORT PASS.** It is not dead; it is not yet reachable |

---

## 8. THE PLACEHOLDER TABLE — every unfilled value in the repository

⚠️ **Not a card requirement** (see §7's preamble). Convention per `README.md`:28. **A placeholder is
never a result. Do not invent, estimate, round, hedge or illustrate one.**
⚠️ **BUILD 1's table listed only this file's two. This one is the whole tree**, because `OF-250`
records that a placeholder surviving into a published README is a live risk and nothing checks for it.

**In the form itself — these two block the paste:**

| Placeholder | Where it appears | What fills it | Filled by |
|---|---|---|---|
| `<<PENDING-RUN: VIDEO_URL>>` | §5 of this file | the unlisted video URL, playable logged-out | **C20 / operator** |
| `<<PENDING-RUN: GIST_ID>>` | referenced in §0.0 and §6.1(4); lives in `README.md`:1491 | the public witness gist id and its server-assigned `created_at` | **C14 / operator** |

**Elsewhere in the repository — measured tonight, so O-3's second half is mechanical:**

| Placeholder | Occurrences | Where |
|---|---|---|
| `<<PENDING-RUN: arm1>>` … `arm4>>` (five arms × seven columns) | **35** | `README.md`:289-293, the §3.1 headline-table shell |
| `<<PENDING-RUN>>` (bare, no name) | 1 | `README.md`:281 |
| `<<PENDING-RUN: N-branch>>` | 1 | `README.md`:324 |
| `<<PENDING-RUN: GIST_ID>>` | 1 | `README.md`:1491 |
| `<<PENDING-RUN: N>>` | 4 | `docs/render/README.md`:46; `docs/render/audit.py`:44; `docs/render/race.py`:81; and `STATUS.md`:20, :2196 |
| `<<PENDING-RUN: VIDEO_URL>>` | 1 | `STATUS.md`:2510 |
| `<<PENDING-RUN: name>>` (the convention itself, not a value) | several | `README.md`:28 and the files that quote it |

⚠️ **`README.md` carries exactly 39 placeholder occurrences over 9 lines** — lines 28, 281, 289-293,
324 and 1491, **counted first-hand by this session**, agreeing with the figure `OF-250` and
`README.md`:28 both publish. **They are correct today** (no run exists) and become a defect the
moment a run does — which is precisely what `OF-250` says nothing checks for.

**And the numbers this file deliberately does NOT print, because printing any of them today would be
a fabricated result.** None appears in §2 or §3; each is listed so a later session filling
`RESULTS.md` can see what the form was written around:

| Number | Why it is absent |
|---|---|
| escape rate per arm (arms 1, 2, 2S, 3, 4) | no scored episode has run |
| money past the gate, per harm component | ditto — and every ₹ figure must ship as a per-episode median with its spread and its cell size, never as a sum |
| false positives per arm (paired Δ) | ditto — and when it exists it is reported on **n=20 per configuration** after rung 4 |
| probe breach rate, probe reach, and the VOID verdict | the threshold is `TODO_C14_CALIBRATION`; no calibration episode has completed; no VOID verdict is computable |
| the selected N | `n_decision.selected_branch` is `TODO_C14_PILOT`; the pilot ran and **refused** |
| the attacker-strength ladder | not run |
| any "blocked N%" or "0/N" | ⚠️ and when one exists it **never** ships without its rule-of-three ceiling |

---

## 9. EVERY FACTUAL CLAIM IN THIS FILE, AND WHERE IT WAS READ

**Verified first-hand at `HEAD` = `686a224afa85eb92d7b3b1cefa233d214fcd6f79` by C21 BUILD 2 on
2026-09-04.** `INCIDENTS.md` **INC-05** is the entry that makes this mandatory: *"a precise-sounding
third-party number that exists in no third-party source."*

| Claim | Read in |
|---|---|
| ⚠️ **The review trail: 21 files, 15 FAIL, 6 PASS** | `docs/reviews/REVIEW_*.md` (21 files, top level only); `docs/reviews/REVIEW_C17_1.md` §2.3, added at `259ca6b` |
| ⚠️ **C17's renderer FAILED review — two BLOCKERs `B-1`, `B-2`** | `docs/reviews/REVIEW_C17_1.md`:426, :447, §2.3 (:532); `STATUS.md`:2196 |
| Project name WHETSTONE GATE; repo `whetstone-gate` | `CONTEXT.md`:86 |
| Deliverable filename is `FORM_ANSWERS.md` | `PROCESS.md`:1343; `CONTEXT.md`:2187 |
| The §9 limitation sentence and its three destinations | `PROCESS.md`:1029-1031; published wording `PROVENANCE.md`:599 |
| Objectives must open on the merchant's loss | `CONTEXT.md` §21 item 3 |
| Razorpay MCP: list capped at 100, no rupee cap; nine `mcpgo.Max()`, none on a rupee amount; six bound pagination at 100; 40-char receipt, 0/1 flag, 30-char settlement description; `capture_payment.amount` unbounded; `READ_ONLY` defaults false | `CONTEXT.md` §2's evidence table, rows at :172-183, against `razorpay/razorpay-mcp-server@7950d51d…`, committed 2026-03-26T09:52:36Z, read 2026-08-30. ⚠️ **Most rows carry a `file:line`; a reviewer should confirm the nine-`mcpgo.Max()` row does before quoting it as one** |
| The concrete loss (over-capture / over-refund / duplicate refund / early sweep) | `CONTEXT.md` §2 |
| 43 Track 01 READMEs, a 13–14% sample of 312 Track 01 repos at a corpus of 1,723; every one authored its own world and answer key; "100% blocked" | `CONTEXT.md`:138-142 (§1) |
| The mandatory occupancy caveat sentence, verbatim | `CONTEXT.md` §21 item 2 |
| CaMeL / PRAMANA better; `argus`, `AgentProof`, `HydraLoop` ship generated adversaries | `CONTEXT.md` §5 and §21 item 1 |
| Attacker never sees policy, holes, attack list or gate reasons; one generic refusal message | `CONTEXT.md` §7 architecture block; §9.3 |
| Blindness guard is proved to FIRE | `tests/test_c12_benign.py`:404; `tests/test_c6_attacker.py`:1137 |
| The four deliberate non-uses each have a test | `tests/test_c9_gates.py`:1282, :1298; `tests/test_c8_scorer.py`:741; `tests/test_c10_probe.py`:1100, :1110, :1127, :1141; `tests/test_c2_world.py`:827 |
| τ²-bench MIT, pinned `a2c0247…`, 2026-08-18; Sierra authored tasks/gold/grader | `config/protocol.yaml`:413; `vendor/tau2-bench/LICENSE`; `CONTEXT.md` §11.1 |
| τ²-bench provides FP ground truth + competence control, **not** escape ground truth | `CONTEXT.md` §11.1 |
| `db_reward` alone, no model | `CONTEXT.md` §11.1 |
| **Rung 4 fired 2026-09-04 05:27 UTC, by the operator on schedule, NOT by §13.4** | `INCIDENTS.md` `INC-144`; `README.md` §9.3 (:810); `RESULTS.md` §1; `QUESTIONS.md` `Q-099` |
| **Rung 4 executed: `tfp_task_count: 20`; 10 ids per domain; T-NEG still 34** | `config/protocol.yaml`:445, :447, :497-498; `tests/test_c3_tau2_enumeration.py`:269-316 |
| AgentDojo cut (rung 3) | `README.md` §9.2 (:793); `STATUS.md`:2195; `config/protocol.yaml`:420 `agentdojo_sha: TODO_C13_C16` |
| The spike's shared-helper failure — "not a result; it is a definition" | `CONTEXT.md` §7; `CLAUDE.md` §2 rule 8 |
| D1-D4 all PASS; allow-list 0 entries; 119 modules indexed / 15 / 6; D4 also scans `whetstone_gate.config`; whole run 21/0/3 | this session ran `./.venv/Scripts/python.exe -m whetstone_gate.tasks check-roles`; `src/whetstone_gate/check_roles.py`:637 |
| `probe-v1` tag object `170bd3ff…`, 2026-09-03 20:43:04 +0530 | `git for-each-ref refs/tags/probe-v1` |
| `HOLES.md` byte-identical at `probe-v1` and `HEAD` (`a4e50ed6…`) | `git rev-parse probe-v1:HOLES.md` == `git rev-parse HEAD:HOLES.md`; `git diff` empty |
| "Below the calibrated threshold → THE WHOLE RUN IS VOID"; the rate is per-episode | `HOLES.md`:221; :186-189 |
| Void threshold is the sentinel `TODO_C14_CALIBRATION`; the loader raises | `config/protocol.yaml`:352; `src/whetstone_gate/probe/void.py`:47, :143 |
| Void rule is pure arithmetic | `src/whetstone_gate/probe/void.py`:81, :109 |
| The calibration is declared, attempted, and has **no completed episode** | `evals/cal/RUN_DECLARED.md`; `evals/cal/*.log`; `find evals -name '*cal__*'` → 0; `INCIDENTS.md` `INC-157` |
| The pilot ran: 20 attempted, 0 completed, 11 truncated, 9 never started; N refused | `README.md` STATUS box, the pilot and N-decision rows; `INCIDENTS.md` `INC-142` |
| `prereg-v1` does not exist; seven tags total | `git tag -l`; `git rev-parse prereg-v1` (exit 128) |
| No witness gist; `<<PENDING-RUN: GIST_ID>>`; `check-prereg` fails open | `README.md`:120-124, :1491; `check-prereg` fails open at `README.md`:113-116 |
| `evals/` holds 31 files; `RESULTS.md` exists and publishes no number | `find evals -type f`; `RESULTS.md` read in full |
| Review trail **as it stood at `686a224`**: 14 FAIL / 6 PASS over 20 files; 6 tagged; 3 with residue; 14 unreviewed of 23 rows | `docs/reviews/REVIEW_*.md`; `README.md`:1175, :1235-1237. ⚠️ **Now 21 / 15 / 6 — see the first row of this table** |
| C6 reviewed six times, never passed, no tag | `README.md`:1263-1264; `docs/reviews/REVIEW_C6_1..6` |
| 155 `## INC-` headings, 154 distinct ids, `INC-139` duplicated | `grep -c "^## INC-" INCIDENTS.md`; `grep -o "^## INC-[0-9]*" \| sort \| uniq -d` |
| INC-02 content and date (2026-08-28) | `INCIDENTS.md`:59 |
| INC-132 content, date (2026-09-04) and Fix SHA `1fd0877` | `INCIDENTS.md`:9832 |
| INC-51 — the first time this assertion reported clean over a live reach | `INCIDENTS.md`:3728 |
| INC-141 — a fenced session cannot commit without turning E1 red | `INCIDENTS.md`:10717 |
| First build commit `ee3cf93`, 2026-08-30 12:20:32 +0530 | `git log --reverse --format="%h %ci %s"` |
| Repo URL | `git remote -v`; `README.md`:1471, :1757 |
| Repository still private until C21's flip | `PROCESS.md`:862 |
| Video URL absent; C20 `todo - review folded` | `STATUS.md`:2199 |
| C17's renderer exists, is `(unreviewed)`, verifies the chain, renders N as a placeholder | `ls docs/render/`; `git log --oneline -- docs/render/` → `b332853 … (unreviewed)`; `docs/render/README.md`:36-47 |
| No payment method attached, attested 2026-08-30, operator-only | `PROVENANCE.md`:204 (§1.5) |
| Secret scan committed at `HEAD = 90b6d6fa…`; 57 commits behind | `docs/submission/git-history-secret-scan.txt`:4; `git rev-list --count 90b6d6fa..HEAD` |
| Determinism scope; model output is not reproducible | `CLAUDE.md` §2 rule 10; `README.md` §9.11 (:1074); `CONTEXT.md` §20 |
| Placeholder convention `<<PENDING-RUN: name>>`; 39 in `README.md` | `README.md`:28; `docs/reviews/OPEN_FINDINGS.md`:2642 (`OF-250`) |
| Form is one-shot; no form until the review returns PASS | `PROCESS.md`:175, :1344 |
| Single-shot rule for calibration and pilot; abort written before any retry | `PROCESS.md` §6b; `CLAUDE.md` §3 |

---

## 10. WHAT THIS SESSION DID NOT DO — so no reviewer has to infer it

- **Did not fill a single placeholder.** Every `<<PENDING-RUN: …>>` that was unfilled when this
  session opened is unfilled now.
- **Did not anticipate the calibration.** No breach rate, no threshold, no void verdict, no
  prediction of one, and no wording that leaves room to infer one. §0.2 states only what a file
  literally contains.
- **Did not flip the repository public.** That is C21's other half and the operator's act.
- **Did not cut any tag**, including `prereg-v1`.
- **Did not write `INCIDENTS.md`**, including the entry `PROCESS.md` §6b owes for the calibration
  attempt — it is outside this session's fence and is operator item **O-0**.
- **Did not write its own `## Session tokens` row.** `make check-roles` E1 will be red on this
  session's commits and that is `INC-141`'s recorded trap, not a defect in the work. Turning it green
  by self-recording would be the exact shape of the defect E1 exists to catch.
- **Did not touch `evals/`, `config/`, `src/`, `tests/`, `tests/goldens/`, `docs/reviews/`,
  `QUESTIONS.md`, `INCIDENTS.md`, `README.md`, `RESULTS.md`, `PROTOCOL.md`, `HOLES.md`,
  `CONTEXT.md`, `PROCESS.md` or `corpora/`.** Two concurrent sessions were live in this working tree
  throughout — one reviewing C17 and holding `QUESTIONS.md`, and the operator's calibration terminal.
- **Did not re-run the git-history secret scan.** `docs/submission/` is inside this session's fence,
  but the scan must cover the tree that actually goes public, and it is checklist item **O-7** — an
  operator act ordered immediately before the visibility flip.
- **Spent zero provider tokens.** No sanction was held and none was taken. `.env` was never opened;
  no key name was paired with a value; no key value was read, printed or committed.
- **Did not run the pilot, the calibration or the sweep**, and did not disturb the operator's
  terminal.
- **Did not self-certify.** A fresh adversarial review follows and should read §0.2 and §6 first.
