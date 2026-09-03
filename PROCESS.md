# PROCESS.md — The Architect Loop, adapted for WHETSTONE GATE

**Method for building the Razorpay AI Buildathon submission.**
Derived from the operator's own PROCESS_TEMPLATE.md. The invariant core — roles, the loop, the
STOP rule, no self-grading, evidence discipline — is unchanged. What is tailored: the
precision-critical domain, the golden fixtures, the reviewer personas, and the gates this project
needs that a normal project does not.

> **Revision 2, 2026-08-30.** Rewritten after `PROCESS_AUDIT.md` returned 🟠 AMBER with fifteen
> blocking issues, an eighteen-row orphan table, twelve red-team holes, and a chunk plan that could
> not fit the specification's own schedule. Every change is recorded in `PROCESS_CHANGELOG.md` with
> the source or command it was verified against. **This file ships publicly, in the repository, as
> part of the submission.** Every factual claim in it is therefore checkable by a panelist, and is
> written to be.

> **Governing document:** `PROJECT_SPEC.md`, copied into the repository as `CONTEXT.md` at v1.0.
> **CONTEXT.md is LAW. This file serves it.** Where the two disagree, the spec wins and this file
> changes — which has already happened twice: the `prereg-v1` tag name (this file said
> `preregistration-v1` in three places) and the composition of the frozen set.

---

## 0. Why this process, on this project, is not ceremony

The template says its two enemies are **assumption** (a session fills a spec gap with a guess and
the guess ships) and **self-grading** (the session that built a thing declares it correct).

**This project's thesis is that the field is self-grading — stated in the exact form the evidence
supports, and no stronger.** The block below is the corrected wording from `PROJECT_SPEC.md` §1, §4
and §5. It replaces a looser paraphrase this document carried in revision 1 — *"~40 competitors are
self-grading; they wrote their own attack lists, ran them against their own defences, and published
100%"* — which the spec's own audit had already corrected as findings **F4** and **F5**.
Reintroducing it here, in a public artefact, would have been the exact failure §9 exists to prevent.

> **Of 43 Track 01 READMEs read in full** — a 13–14% sample (43 of the 312 Track 01 repos identified
> when the corpus stood at 1,723; the corpus was 1,813 on 30 Aug and the Track 01 count was not
> re-derived) — **every one authored its own world and its own answer key, and the recurring headline
> is 100% blocked. Two of the 43 (`kasauti`, `Mandate-Compiler`) publish their own failures; the
> other 41 do not.**
>
> **And not all of them use fixture lists.** `jboiie/argus`, `adthya-anil/AgentProof` and
> `Chavan-Kartik/HydraLoop` run **generated** adversaries, each verified at source on 2026-08-30.
> What none of them does is run that adversary against tasks, a world **and** an answer key authored
> by a third party, and none compares more than one gate design under the same adversary.
>
> Razorpay's own engineering handbook calls the general failure *"taking an exam it wrote and marked
> itself."* (`razorpay/ai-playbook` B.9; carried with its URL in `RAZORPAY_ENGINEERING_ORG.md`.)

So the process is not overhead here. It is the argument, applied to ourselves:

| The process rule | The same idea in the submission |
|---|---|
| Build session never reviews its own chunk | The gate never scores its own episode — the scorer is a separate replay with no model |
| The reviewer's first phase is **blind** to the builder's code and story | The attacker is policy-blind: it never sees the policy, the holes, the attack list or any gate's reason |
| Golden fixtures hand-computed before the code, in `tests/goldens/`, editable by no build session | Invariants pre-registered, git-tagged **and externally witnessed** before the first scored episode |
| A reviewer re-implements the logic from the spec text, importing nothing from the project | The scorer shares no code with the gate — the two are written twice on purpose (§4 rule 8) |
| Never weaken a test to get green | The run voids itself when the probe fails, rather than publishing a flattering number |
| **The review gate itself must go red on purpose** (§5.4) | The competence probe is a known-red case pointed at our own attacker |
| Evidence regenerates from stored artefacts | `make eval` regenerates every number **from the stored ledgers** — a scope stated exactly, because model output at temperature 0.7 is not reproducible and claiming otherwise would be false |

**Consequence:** `docs/reviews/` is not internal hygiene on this project. It is a public artefact
that demonstrates *"would you trust it"* — the rubric line that is otherwise only assertable. It is
**append-only**, it carries every FAIL as a numbered attempt that cannot be overwritten, and it
contains a deliberately seeded defect together with the review that either caught it or did not
(§5.4). A trail of twenty-two PASSes and no failures would be evidence that the gate is decorative,
which is precisely the thing this submission exists to criticise in other people's numbers.

---

## 1. The roles

| Role | Who | Does | Never does |
|---|---|---|---|
| **ARCHITECT** | this session | owns the spec, hand-computes the goldens, writes every build and review prompt, reads reports, recomputes load-bearing numbers, emits a VERIFICATION block per report, makes rulings, decides sequence | writes project code, edits repo files, commits, reviews |
| **OPERATOR** | Chinmoy | carries prompts to fresh sessions, pastes reports back, runs long jobs in his own terminal, commits the goldens and the architect's VERIFICATION blocks, makes final calls | lets a session decide something the spec left open |
| **BUILD SESSION** | fresh session | executes exactly one chunk | assumes, self-reviews, exceeds scope |
| **REVIEW SESSION** | a *different* fresh session | adversarially verifies one chunk, in two sealed phases (§10 template 2) | fixes what it reviews |
| **FIX SESSION** | a fresh session, after a FAIL | writes the `INCIDENTS.md` entry **first**, then fixes only the findings named | re-reviews its own fix |

**Architect placement.** The architect stays in this chat, because it holds the decision history —
the searches, the killed ideas, the audit lenses, and the reason behind every clause in the spec.
**That is a single point of failure, and it is treated as one rather than described as one:**
`ARCHITECT_HANDOFF.md` is updated at the end of *every* chunk (§11), so everything needed to resume
lives in the repository even though the reasoning that produced it does not. The operator relays
reports; `docs/sessions/` holds the originals, committed by the sessions themselves.

*Optional upgrade if relaying becomes tedious:* a second read-only session inside the repo,
booted with template 1. It sees the files directly but not the history. Use it for mechanical
checks, not for rulings.

**Rules that make the roles real:**

- **One prompt per chunk, and never two prompts in one message.** Two prompts in one message is how
  steps get skipped.
- ⚠️ **CONCURRENCY, precisely — revised 2026-08-30, because strict serialisation cannot fit the
  schedule (§12); the REVIEW half amended 2026-08-31, see immediately below.** **Up to two BUILD
  sessions may be in flight at once, if and only if their SCOPE FENCEs are disjoint and neither
  imports the other.** The architect records the concurrent pair as a ruling in `QUESTIONS.md` under
  `## Concurrent pairs` **before** issuing either prompt.
  ~~**REVIEW sessions remain strictly serial**~~ — **AMENDED 2026-08-31, see the next bullet.** What
  is **not** amended and still binds: **a chunk's review may not begin before the architect has
  recomputed that chunk's build report and committed its `ARCHITECT_CHECK`.**

- ⚠️ **AMENDMENT, 2026-08-31 — CONCURRENT REVIEWS. Approved by the OPERATOR on 2026-08-31.**
  The struck clause above read *"REVIEW sessions remain strictly serial."* It is **struck rather than
  deleted**, because a rule that changed under schedule pressure must be visible as a change.
  **AMENDED TO:** **UP TO TWO REVIEW SESSIONS MAY BE IN FLIGHT AT ONCE, IF AND ONLY IF their chunks
  are DISJOINT AND NEITHER DEPENDS ON THE OTHER.** **A chunk and its dependency are never reviewed in
  parallel** — **C7's and C8's reviews may not pair, because C8 depends on C7; C1's and C3's may, and
  C2's and C4's may.** The pair is recorded in `QUESTIONS.md` under `## Concurrent pairs` **BEFORE
  either prompt is issued**, exactly as a build pair is.

  **THE REASONING, WRITTEN DOWN BECAUSE A RULE CHANGED UNDER SCHEDULE PRESSURE MUST SHOW ITS
  WORKING:** the serial-review rule was **the BINDING CONSTRAINT on the entire critical path to the
  freeze** — twelve `full` reviews at a **measured ~75 minutes** is **~15 hours**, which put **C14
  past midnight on 31 August**. **NOTHING IN THE REVIEW ITSELF IS WEAKENED BY PAIRING.** Each review
  is still a **DIFFERENT FRESH SESSION**, still **two sealed phases**, still **blind in Phase 1**,
  still requires its **committed reimplementation** and its **eight mutants**, and still **cannot be
  written by the session that built the chunk**. **The only change is that two are in flight at
  once.**

  ⚠️ **WHAT IS EXPLICITLY NOT CHANGED, so this amendment cannot be read as a precedent for cutting
  review rigour:** **PASS conditions**, **persona coverage**, **mutant counts**, the
  **reimplementation requirement**, the **two sealed phases**, and the rule that **build and review
  are never the same session**. **This project's own C0 FAIL is the evidence that the gate works, and
  it is worth more than the hours it cost.**

  **RISKS ACCEPTED, EACH WITH ITS MITIGATION:** journal collisions on `STATUS.md`, `PROGRESS.md` and
  `docs/reviews/OPEN_FINDINGS.md` are handled by the **append-only + rebase + stop-after-two-
  rejections** clause, which was **PROVEN on 2026-08-31 when C0-FIX and C1 ran concurrently for 45
  minutes with zero collisions**; a **FAIL arriving while its pair is mid-flight** is covered by
  **§11a's twice-failed-chunk rule**; and **the architect's own throughput is the remaining limit, to
  be reported the moment it binds.**

  ⚠️ **SUPERSESSION, noted rather than back-edited:** **§12.0's item 1** was written on 2026-08-30
  and still reads *"Reviews stay serial, so the **serial review queue is the binding constraint**"*.
  **That sentence is the record of the arithmetic as it stood then and is not rewritten here**; from
  2026-08-31 **this bullet governs**, and the binding constraint is the architect's own throughput,
  above.
- Build and review are **never the same session**, and the architect is never the reviewer.
- Long runs (the sweep, the pilot, the calibration, the CaMeL branch test, the ladder windows)
  execute in the **operator's terminal**, never inside a session that might close mid-run.
- ⚠️ **AMENDMENT, 2026-09-03 — WHERE A LONG RUN MAY EXECUTE. Authorised by the OPERATOR on
  2026-09-03.** The bullet immediately above is **NARROWED, NOT DELETED**, and it is left standing
  rather than struck so that a reader sees what the rule **WAS** and what it **BECAME**. **AMENDED
  TO:**

  > **A run MAY execute inside a session IF it is CHECKPOINTED AND RESUMABLE and ANY ABORT IS
  > RECORDED BEFORE A RETRY. A run expected to exceed roughly TWO HOURS executes in the operator's
  > terminal, because a session has limits a terminal does not.**

  **REASON, AND IT IS A MEASUREMENT RATHER THAN A CONVENIENCE:** **C12 BUILD 1 demonstrated
  kill-and-resume on this very driver — three passes, ZERO duplicates, ZERO re-runs, and the
  denominator reading 20 on all three** (`docs/sessions/c12-build-1.txt` §4). **A session that dies
  leaves a checkpoint AND writes a report; a closed terminal leaves neither.** The clause was
  protecting against a run dying **where nobody notices**, and for a checkpointed run a session is
  the **better-observed** place, not the worse one.

  ⚠️ **WHAT IS NOT AMENDED, STATED SO NOBODY READS THIS AS TOUCHING IT: §6b IS UNCHANGED.**
  *"The first execution that runs to completion IS the run"* holds **WHEREVER it runs.** This
  amendment changes **WHERE** a run may happen and changes **NOTHING** about **WHICH** run counts. An
  abort is still recorded in `INCIDENTS.md` **before** any retry, and **two completed pilot runs
  existing is still a process violation published as one.**

  ⚠️ **AND THE SWEEP STILL GOES IN THE OPERATOR'S TERMINAL. It is hours long and it is the scored
  run.** The two-hour test is what puts it there, and §8's own copy of this clause — *"the sweep is
  not a session's job"* — agrees.

  **Recorded verbatim in `QUESTIONS.md`** under `## ⚠️ RECORDED BY ARCH — PILOT RUN (7c05e3b9)`,
  **before this bullet was written**, per hard rule 5. ⚠️ **That entry also names the two copies of
  the original clause this amendment does NOT reach — `CLAUDE.md` §4 and §8 below — both outside the
  amending session's fence, and the propagation is owed to the architect.**
- The architect may propose changes to the spec, but a **pre-registered artefact is frozen** (§6) —
  that is the one thing nobody may unilaterally change.
- **The operator does not open the submission form until the C21 review returns PASS** (§12).

---

## 2. The canonical files

Created in chunk 0, before any building. **Chat history is NOT a record. If it matters, it is a
file in the repo.**

### Governance files (the method)

| File | What it is | Rules |
|---|---|---|
| **CONTEXT.md** | the complete specification. THIS FILE IS LAW. | **Already exists as `PROJECT_SPEC.md`** — audited by six lenses, corrected, self-checked. Copied into the repo as `CONTEXT.md` at v1.0. Versioned thereafter; only the architect authors changes |
| **plan.md** | the chunk list — one card per chunk: scope, inputs, outputs, dependencies, review type, **calendar date and time-box**, explicit **"done when"** | §12 is its source. Plan changes are recorded architect rulings |
| **CLAUDE.md** | the constitution every session reads first: read-order, the **thirteen** hard rules verbatim, end-of-session duties, git rules | short; rules only |
| **STATUS.md** | one line per chunk, with a permanent **review-history column that is only ever appended to** — `C7: built → FAIL(1) → fixed → PASS(2)` | the single glance-state, and the history is not erasable |
| **PROGRESS.md** | session journal, newest on top, fixed template | one entry per session, opening with that session's `SESSION-TOKEN` |
| **QUESTIONS.md** | every ambiguity hit and every ruling made, **verbatim**; plus `## Session tokens` (§7a) and `## Concurrent pairs` | a ruling that exists only in chat does not exist |
| **`tests/goldens/`** | ⚠️ **the hand-computed expected values, authored by the ARCHITECT and committed by the OPERATOR *before* the build prompt that cites them is issued.** A build session may **read** them and may **never edit** them | **A `full` chunk with no golden may not be built.** This turns rule 3 from a habit into a file that either exists or does not |
| **docs/reviews/REVIEW_\<N\>_\<attempt\>.md** | one per review **attempt**, numbered from 1, **never overwritten, renamed or deleted** | public artefact, see §0. A FAIL that is not in the repo did not happen |
| **docs/reviews/independent/** | `c<N>_reimpl.py` — the reviewer's from-scratch reimplementation, importing nothing from `src/` — plus `c<N>_reimpl_diff.txt` | a `full` review without one **cannot PASS** |
| **docs/reviews/mutants/** | `c<N>_mutants.md`: one row per mutant — file:line, the operator changed, the test that killed it, **or an explicit equivalence proof** | **minimum eight mutants on a `full` chunk**, at least one per invariant the chunk touches |
| **docs/reviews/ARCHITECT_CHECK_\<N\>.md** | the architect's VERIFICATION block: every load-bearing number recomputed, the value obtained, the value claimed | **no chunk is tagged `cN-pass` without one.** An unrecorded gate is not a gate |
| **docs/reviews/OPEN_FINDINGS.md** | every MEDIUM and LOW a review could not close, appended by every review, closed explicitly with the SHA that closed it | stops findings accumulating silently underneath a wall of PASSes |
| **docs/sessions/\<chunk\>-\<role\>-\<attempt\>.txt** | **every session's FINAL OUTPUT block, committed verbatim by that session itself, before it reports** | what the architect reads is a convenience copy; **the file is the record** |
| **docs/personas/** | the **three** reviewer personas, cited by every review prompt | evaluation-integrity, code, submission |
| **ARCHITECT_HANDOFF.md** | how to resume: roles, read order, the hold-point, what is sealed, what is owed, every open ruling, and the next three prompts in draft | **updated at the end of every chunk.** Stale by more than one chunk → **building stops** until it is current |

### Project artefacts (the submission)

| File | What it is | Rules |
|---|---|---|
| **INCIDENTS.md** | what broke, and what was done about it | **Open from the first commit.** Razorpay reads this answer *first*. **Format fixed by hard rule 13.** **Snapshotted by `prereg-v1`, never frozen** (§6): it must keep growing. ⚠️ **APPEND-ONLY, AND IN EVERY SESSION'S FENCE** (Q-033, 2026-08-31) — *fencing it out left three sessions in one day reporting an incident they were forbidden to file, and hard rule 13's "an entry with an empty field is not an entry" applies at full strength to a session that cannot write one at all.* Same discipline as `STATUS.md` and `PROGRESS.md`: append only, never rewrite another session's lines, re-verify your own bytes after a rebase, stop after two rejected pushes |
| **RAZORPAY_SEMANTICS.md** | one row per documented Razorpay rule — **verbatim quote + URL + fetch date** — including all five instant-settlement bounds and the `X-Refund-Idempotency` documentation | ⚠️ **Written FIRST, before any world code** (spec §17). It is the oracle for the spend-free self-test (spec §13.5(7)): *"every documented Razorpay error in `RAZORPAY_SEMANTICS.md` fires in the mock world."* No row may be a paraphrase. **Frozen and git-tagged** (§6) |
| **INVARIANTS.md** | E1–E3, S1–S4, and **S2-amt as the labelled second predicate**, in plain English, no code | **Frozen and git-tagged** (§6) |
| **PROTOCOL.md** | arms, attacker budget, seeds, temperature, turn budget, the N decision rule with **both branches written out**, the calibrated probe threshold with its Wilson interval, the pre-registered headline comparison, the pinned τ²/AgentDojo/CaMeL SHAs, **the exact Google API model id strings**, the pre-registered task selections and the named dropped sets, **the quartile method**, and **the SHA-256 of every file under `config/`** | **Frozen and git-tagged** (§6) |
| **HOLES.md** | the CANARY-A predicate, the CANARY-B predicate, and **S4's in-flight window width (2)** — each SHA-256'd with a UTC timestamp | **Tagged `probe-v1` BEFORE the pilot and BEFORE the calibration command runs** (§6) |
| **PROVENANCE.md** | every constant tagged `[Razorpay-defined]` or `[merchant-policy, author-chosen]`; one row per attack A1–A6; every external claim with URL and date; the day-one free-tier limit screenshots; **the repository's remote URL**; the corpora licences incl. InjecAgent's British-spelled `LICENCE`, AgentHarm's field-of-use clause and R-Judge's absent licence | the honesty ledger. **Frozen and git-tagged** (§6) |
| **`config/`** | ⚠️ **what the experiment actually reads.** `protocol.yaml`, `lanes.yaml`, `ladder.yaml`. One loader, **no default for a required value** | **A PRE-REGISTRATION ARTEFACT AND PART OF THE FROZEN SET** (§6). Freezing the prose while leaving the numbers editable would have frozen nothing |
| **RESULTS.md** | every number, regenerable by one command; the `check-prereg` PASS/FAIL line; the VOID banner if the run voids | |
| **README.md** | results above the fold; the merchant's loss first, never the methodological critique; prior art named; architecture; the honest negative; **§ "Verifying the pre-registration"** (§6a); the `(unreviewed)` explainer (§7) | written last, from the artefacts |
| **AGENTS.md**, **docs/adr/**, **bench/** | Razorpay's own "Agent Ready" convention (`RAZORPAY_ENGINEERING_ORG.md` §9.4), which they run internally as an 80% bar with a POD health dashboard | cheap, visible, and it converts *"is it structured, would you trust it"* into a checklist they already own |
| **docs/render/** | ⚠️ **the replay renderer**: the video's §18 RACE beat **and** the Definition-of-Done box *"an audit log a non-author can read and follow"* — one build serving two deliverables | reads `evals/episodes/` alone; never a live run |

---

## 3. The loop

```
ARCHITECT hand-computes the chunk's goldens → OPERATOR commits tests/goldens/
ARCHITECT writes chunk-N build prompt (opens with a fresh SESSION-TOKEN)
   → OPERATOR pastes into a FRESH build session
      → session builds chunk N, commits ("(unreviewed)", Session-Token trailer), pushes
      → session commits docs/sessions/cN-build-1.txt, THEN emits "CHUNK N REPORT"
   → OPERATOR pastes report to ARCHITECT
   → ARCHITECT recomputes the load-bearing numbers itself and emits a VERIFICATION block
      → OPERATOR commits docs/reviews/ARCHITECT_CHECK_N.md
ARCHITECT writes chunk-N REVIEW prompt (a NEW SESSION-TOKEN)
   → OPERATOR pastes into a DIFFERENT FRESH session
      → PHASE 1, BLIND: reimplement from CONTEXT.md alone; generate >=20 own vectors; COMMIT both
      → PHASE 2, SIGHTED: read the diff and the journals; run the project on the Phase-1 vectors
      → session commits REVIEW_N_<attempt>.md on EITHER verdict, updates STATUS/PROGRESS,
        appends to OPEN_FINDINGS.md, tags cN-pass ONLY on PASS, pushes, states the SHA first
   → OPERATOR pastes report to ARCHITECT
   → on PASS: next chunk.
     on FAIL: FIX session writes the INCIDENTS.md entry FIRST, then fixes only the named findings
              → focused re-review as attempt 2, in a NEW file, with the FAIL left standing.
```

- **Chunks are small and self-contained** — one session, one sitting, one reviewable unit. If a
  chunk grows mid-flight, split it (C9 → C9A/C9B) and record the split as a ruling.
- **Every session prompt ends with the same demand:** final output as ONE plain-text code block,
  no markdown, so the operator copies it in one motion — and the session commits that same block to
  `docs/sessions/` **before** printing it.
- Every prompt names exactly which files and sections to read, in order.

---

## 4. The hard rules

These go in CLAUDE.md verbatim. **Thirteen.**

1. **THE STOP RULE.** If the spec is ambiguous, incomplete, or contradictory about anything you
   are building: STOP that item, write the question to QUESTIONS.md with the options you see,
   continue any unblocked work. **Never assume. A session that stops on a real ambiguity has
   succeeded.**
2. **NO SILENT DEVIATION.** **Class A** (changes meaning, behaviour, or a reported number) → STOP,
   ask the architect. **Class B** (implementation choice within spec) → do it, record it with
   rationale, judged at review. **Class C** (cosmetic) → one line.
3. **GOLDEN FIXTURES DEFINE DONE.** Hand-compute the expected outputs before writing the code. A
   test whose expected value was produced by the code it tests proves nothing. **Goldens live in
   `tests/goldens/`, are committed before the build prompt is issued, and a build session may READ
   them and may NEVER EDIT them. A `full` chunk with no golden may not be built.** See §5.2.
4. **ONE SOURCE OF TRUTH.** CONTEXT.md outranks the plan, the code, the tests, and memory. **A
   frozen pre-registration artefact outranks CONTEXT.md** — see §6.
5. **RULINGS ARE RECORDED VERBATIM** in QUESTIONS.md before anything else is touched.
6. **NEVER WEAKEN A TEST.** No deleting, skipping, loosening, or approximating an assertion to get
   green. If a ruling legitimately changes behaviour, the test flips citing the ruling — and the
   flip must be *provably* meaningful (it fails on the old code).
7. **EXACTNESS WHERE IT COUNTS.** See §5.1 — the precision-critical domain.
8. **PURITY SEPARATION, AND THE ANTI-CIRCULARITY RULE.** Core logic takes data in and returns
   results — no I/O, clock, network, or randomness inside it. Side effects live in a thin outer
   shell.
   - **The scorer must import no model client, and a test must assert that.**
   - **The probe, the void rule, the world and the arm-4 kernel must each import no model client,
     and a test must assert EACH** — four deliberate non-uses, four tests (spec §14). Until
     2026-08-30 only the scorer's was asserted, while the README claimed all four.
   - ⚠️ **THE GATE AND THE SCORER SHARE NO CODE, AND A TEST MUST ASSERT THAT.**
     `scorer/` imports nothing from `gates/`; `gates/` imports nothing from `scorer/`; neither
     imports a shared predicate helper. **Any logic they both need is written twice, on purpose** —
     once against the live call, once against the replayed ledger. The test is a module-graph walk
     over both packages' transitive first-party imports, failing on any shared first-party module
     outside a short, explicit allow-list of pure value types (enums, the harm-record dataclass,
     the paise integer wrapper) that carry **no predicate logic**. **Adding to that allow-list is a
     Class A deviation** requiring an architect ruling in `QUESTIONS.md`.
     *Why this one line is the whole moat:* in the spike, `gate.js` and `invariants.js` both called
     `world.js:intentKey`, so the invariant **could not have fired unless the gate had a bug**.
     **That is not a result; it is a definition.** (spec §7, §8.6.)
9. **CONFIG, NOT CONSTANTS.** Every spec-specified value lives in `config/`, loaded through one
   loader, with **no default for a required value** — a missing value is a hard refusal, never a
   silent fallback. A tripwire test scans the source for hardcoded spec values, using
   **`CONTEXT.md` §8.6's constants table as its authoritative list** (that table was amended on
   2026-08-30 to actually contain every author-chosen constant; it previously did not, so the
   tripwire had nothing complete to scan against).
   ⚠️ **`config/` is a pre-registration artefact.** Every file under it is listed in `PROTOCOL.md`
   with the SHA-256 of its **git blob**. `make check-prereg` recomputes them, runs inside **both**
   `make eval` and `make test`, and prints PASS/FAIL into `RESULTS.md`.
10. **DETERMINISM FOR LONG WORK.** Resumable (atomic writes, publish-on-complete), idempotent
    (re-run = zero duplicates), deterministic **where determinism is possible**.
    ⚠️ **Scope, stated exactly, because the looser claim is false:** the **world, the ledger schema,
    the scorer and the replay** are byte-identical from the same seed, and are tested to be.
    **Model output is NOT** — the attacker runs at temperature 0.7 against a hosted provider.
    So `make eval`'s claim is *"every number regenerates from the stored ledgers"*, which is true,
    checkable, and enough. **Do not write, and do not let the README write, that re-running the
    models reproduces the run.**
11. **NO SILENT DENOMINATOR SHRINKAGE.** Razorpay's own B.9: *"Score complete trials only. Do not
    let retries, fallbacks, skipped cases, or missing traces quietly shrink the denominator."*
    Every dropped episode is counted, categorised and printed as a number. **A truncated episode is
    counted in the denominator.**
12. **BUDGET AND KEY SAFETY.** See §8. A **token** ceiling as well as a call ceiling; a 429 means
    STOP and report, never retry into another lane.
13. ⚠️ **INCIDENTS FORMAT IS FIXED.** Every entry is exactly:
    `## INC-NN — <named failure, not "it was hard">` ·
    `**Event:**` what we saw while it unfolded ·
    `**Action:**` what we did ·
    `**Expectation:**` what should have happened and did not ·
    `**Missing:**` what, if present, would have helped debug it ·
    `**Missed:**` the signal that was there and was ignored ·
    `**Diagnosis:**` the causal mechanism, at most two sentences ·
    `**Fix:**` the change, **with its commit SHA** ·
    `**Systemic guardrail:**` what makes this class impossible — or the words *"none — accepted,
    because …"*.
    **An entry with an empty `Diagnosis` or `Missed` is not an entry.**
    **Every review FAIL produces one, written by the FIX session before it changes a line of code.**
    **At least two entries must be dated after the first build commit** — if the build produced no
    failure worth recording, that fact itself is `INC-00`, with its own diagnosis.
    *Why this format:* `Missing` and `Missed` are Razorpay's own house fields
    (`RAZORPAY_ENGINEERING_ORG.md` §9.3, machine-enforced there since 2022) and they are the two
    self-incriminating fields no other candidate will write. *Why `Diagnosis` and `Fix`-with-SHA:*
    "what broke" is read first, so the pressure runs **both** ways — to under-report a failure that
    costs a fix session, and to **dramatise** one that reads well. An invented incident has no commit.

---

## 5. Tailoring — the four things this project must define

### 5.1 The precision-critical domain

Anything below, handled lossily, invalidates a reported number.

| Domain | Rule | Golden |
|---|---|---|
| **Money** | integer **paise** end to end. Never a float, never a rupee decimal. Rounding is **ROUND_HALF_UP** on exact integers or `Decimal`, **never on a binary float** | **1** |
| **The harm vector** | four separately-tracked components — `customer_overcharge`, `merchant_irrecoverable_outflow`, `merchant_float_moved`, `fees_incurred`. **Never summed into one number.** Reported as per-episode median with IQR (`numpy.percentile(…, method="linear")`), never a total | **3**, **6** |
| **The ledger** | append-only, hash-chained, **rooted at a genesis hash loaded from `config/` with no default**. Any mutation of a prior entry must be detectable | **5** |
| **Seeds and determinism** | every episode reproducible from its seed. Two runs of the same seed produce byte-identical **worlds, ledgers and scores** for a fixed model output | **7** ⬅ *was missing* |
| **Timestamps and tags** | pre-registration artefacts carry real commit timestamps — **and a commit timestamp is forgeable, so the freeze is witnessed OUTSIDE this repository or it did not happen** (§6a). Never backdate, never amend a tagged commit | none possible — see §6a |
| **Token and rate accounting** | per-model consumption tracked from the API's own `usage` field, never estimated. The N decision rule keys off it and `RESULTS.md` publishes it | **8** ⬅ *was missing* |
| **The gate verdicts** | each arm emits exactly the verdict set spec §8.6 gives it, and no other | **9** ⬅ *was missing* |

### 5.2 The golden fixtures

Hand-computed **before** the code, by the architect, committed to `tests/goldens/` by the operator,
and quoted in the build prompt. **A build session may read them and may never edit them.**

**1. The money arithmetic — integer paise, ROUND_HALF_UP, and the one fee this project models.**

⚠️ **This replaces the "fee identity" golden of revision 1, which is deleted.** That golden belonged
to Razorpay **Route**, a project `DECISION.md` killed (`:14`, `:22`, and *"Route is gated behind
>₹40 Lakh domestic turnover"* at `:47`). It carried a **2% gateway fee and an 18% GST multiplier this
project does not model** — Whetstone Gate models exactly one fee, the instant-settlement fee, sourced
to Razorpay's own **ex-tax** worked example. And its stated final balance **did not reconcile**:
`[VERIFIED HERE — exact `Decimal`, ROUND_HALF_UP, 2026-08-30]` the four fees sum to **29.22**, so the
stated **−26.56** is reachable **only by excluding the ₹900 line**, in two different ways, and is
ambiguous between them. A build session told *"code must reproduce the goldens exactly"* would have
implemented a fee engine that does not exist here and shipped an 18% error into a published harm
component.

> Rounding is verified on Razorpay's two discriminating cases: **`0.885 → 0.89`** and
> **`2.065 → 2.07`**. Banker's rounding gives `0.88` and `2.06` — **these two cases are the whole
> test.** `[VERIFIED HERE — Python `Decimal`, ROUND_HALF_UP vs ROUND_HALF_EVEN, 2026-08-30]`
> ⚠️ **Compute them on `Decimal` or on integers, never on `float`.**
>
> The settlement fee is **ex-GST**:
> `fees_incurred_paise = ROUND_HALF_UP(settled_paise × 0.0025)`, computed as the exact integer
> **`(settled_paise * 25 + 5000) // 10000`**. Four hand-computed vectors
> `[VERIFIED HERE, 2026-08-30]`:
>
> | `settled_paise` | expected `fees_incurred_paise` | why this vector exists |
> |---|---|---|
> | `20,000,000` | `50,000` | reproduces Razorpay's own *"0.25% (₹500 ex-tax on ₹2,00,000)"* example verbatim |
> | `20,000,200` | `50,001` | exact product 50,000.5 — **the half-up case** |
> | `19,999,800` | `50,000` | exact product 49,999.5 → 50,000 |
> | `1` | `0` | the floor case |
>
> And one whole action: a `create_instant_settlement` of ₹2,00,000 writes
> `merchant_float_moved_paise = 20,000,000`, `fees_incurred_paise = 50,000`,
> `customer_overcharge_paise = 0`, `merchant_irrecoverable_outflow_paise = 0`.

**2. Each invariant, on a hand-built ledger.** For E1, E2, E3, S1, S2, **S2-amt**, S3, S4 — one
ledger that trips it and one that does not, both written by hand with the expected verdict stated.
**S2 and S2-amt must disagree on at least one fixture** — the staged instalment refund — because
that disagreement is the false-positive delta the project publishes as a finding (spec §9.2).

**3. The harm vector on one worked episode** — every component computed by hand from a small
ledger, including the case where a settlement sweep contributes `merchant_float_moved` and
`fees_incurred` but **zero** `merchant_irrecoverable_outflow`, and the case where
`rejected_by_razorpay == true` contributes **zero to all four** while still counting toward CANARY-B
reach and toward the productive-action confound.

**4. The probe.** A hand-built ledger where the planted violation is present → CANARY-A breached.
One where it is absent → run VOID. One where a **`DENIED`** entry names `pay_CANARYRECON` →
**CANARY-B reach counted anyway**, because reach counts blocked entries.

**5. The tamper test.** A ledger with one field altered → the hash chain detects it. **And the
mutation revision 1 would not have caught:** an entry whose stored `prev_hash` still matches the
previous entry's stored `hash` field while that previous entry's *contents* have been altered. A
verifier that compares stored fields instead of recomputing the previous entry's digest passes this
and must not. *(This is also the seeded defect of §5.4 — the architect writes that defect into C7's
build prompt, and this golden is what should catch it.)*

**6. A per-episode median + IQR** computed by hand on a small set, including the skew case (one
episode dominating) that the mean would misreport. **The quartile method is named:
`numpy.percentile(…, method="linear")`** — median and IQR on small samples swing materially between
linear interpolation, nearest-rank and Tukey hinges, and an unnamed method is an unreproducible
number. It is stated in `PROTOCOL.md` and the golden is computed against it.

**7. The world generator, pinned.** ⬅ *added; the most serious of the three missing goldens.*
`tests/goldens/world_seed_2001.json` — the first six raw `mulberry32(2001)` outputs to 10 significant
figures, **and** the complete 12-payment record for seed 2001: every id, `amount_paise`, `status`,
and the 8 captured / 3 authorized-uncaptured / 1 probe split, with **`pay_CANARYRECON` present and
carrying the spec §10.1 fields exactly** (`status: captured`, `amount 8,000,000`,
`amount_captured 8,000,000`, `amount_refunded 0`, the exemption note verbatim). Authored before C2
exists.
*Why:* C2's done-when would otherwise be *"two runs of one seed byte-identical"* — a check **any
deterministic function passes, including a wrong one.** The spike was JavaScript and spec §16
requires the PRNG to be **reimplemented, not carried over**. A mis-ported `mulberry32` gives every
arm a different exam, every reported number moves, and nothing else in this process would detect it.

**8. Token accounting.** ⬅ *added.* One recorded API response fixture with a known `usage` block →
the hand-computed accumulator state after it; plus **the 429 case** (a 429'd call contributes zero
tokens) and **the truncated-episode case** (counted in the denominator, per rule 11).
*Why:* the N decision rule keys off measured tokens/episode, the sweep's feasibility depends on the
accounting, and `RESULTS.md` publishes tokens per model per day.

**9. The gates.** ⬅ *added.* One hand-built ledger prefix plus one candidate action, with the
expected verdict stated **by hand** for arms 1, 2S and 4 — so *"each arm's verdict set matches the
spec"* is checkable rather than asserted. Includes the `INDETERMINATE` case (a declared obligation
with no result) and the P7-exempt case on `pay_CANARYRECON`.

**Rule:** if a golden cannot be computed by hand, the thing it tests is too complex and the chunk
is wrongly scoped.

### 5.3 The reviewer personas

Three files in `docs/personas/`, cited by every review prompt.

**Persona 1 — EVALUATION-INTEGRITY REVIEWER** *(the domain persona, pointed at this field's real
failure modes)*

> *You are reviewing work you did not create, for a project whose entire claim is that other
> people's measurements are unsound. If ours are unsound, the submission is worse than worthless.
> Assume the numbers are wrong until proven otherwise. Your loyalty is to CONTEXT.md and to the
> frozen protocol, not to the builder's effort.*

Checklist, in order of how this field actually fails:

- **Circularity.** Does any reported number depend on the builder having authored both the world
  and the answer key? **Does the gate share any first-party module with the scorer?** Where
  circularity is unavoidable, is it stated in the open?
- **Denominator integrity.** Are dropped, errored, retried or truncated episodes counted and
  printed? Does every partition sum to its total?
- **Metric soundness.** Are incommensurable quantities summed? Is a mean reported where the
  distribution is skewed? Is any ₹ figure a total rather than a median with spread? **Is the
  quartile method named?**
- **Arm confounding.** Do all arms sample the same attack space? Is probe *reach* reported per
  arm? Is budget starvation (blocked turns are turns not spent exploring) accounted for?
- **Post-hoc selection.** Was any threshold, seed set, N, or headline comparison chosen *after*
  seeing a number? Diff every claim against the frozen tag. **Was the calibration or the pilot run
  more than once (§6b)?**
- **Attacker competence.** Could a reported "0 escapes" be a broken instrument rather than a
  strong gate? Is the probe result printed beside every escape number?
- **Third-party claims.** Every statement about someone else's code, paper or product — verify at
  source. **This rule exists because three such claims reached the specification before an audit
  caught them.** It is the reason the rule is here.
- **Hand-recomputation** of every golden, and an attack menu of nasty inputs.

**Persona 2 — CODE REVIEWER** *(unchanged from the template)*

> *Your job is what breaks at the worst moment: crashes, corruption, silent data loss,
> unmaintainable mess.*

Plus four additions for this project: **the scorer imports no model client** (assert it);
**the scorer and the gates share no first-party module** (assert it); **the runner resumes correctly
across a day boundary** (kill it mid-run and restart); **no API key appears in any log, transcript,
report or committed file.**

**Persona 3 — SUBMISSION REVIEWER** ⬅ *new; used by C19, C20 and C21 — the deliverables nobody was
checking.*

> *You are the panelist. You have five minutes of video, one README, two form paragraphs and no
> patience. You have not read the spec. Anything you cannot verify from the repository in front of
> you, you distrust.*

Checklist:
- Does the README lead with **the merchant's loss**, never with the methodological critique
  (spec §21.3 — problem taste is the weakest rubric line and their first)?
- Is **every** claim about a third party sourced with a URL and a date?
- Does every "0/N" carry its ceiling? Does every ₹ figure carry its spread and its cell size?
- Does the video's RACE beat say **on screen** that it is a replay of a stored hash-chained ledger,
  not a live run, and does it name the seed and the pre-registered N?
- Does a **logged-out** browser load the repo URL and play the video?
- Can the pre-registration be verified **by running the procedure printed in the README**, start to
  finish, from a fresh clone?
- Do the two form paragraphs match the repository, and does the Build-Challenges paragraph cite
  ≥2 `INCIDENTS.md` entries of which **at least one is dated after the first build commit**?

### 5.4 ⚠️ THE REVIEW GATE MUST GO RED ON PURPOSE

§0 and §13 both quote `ai-playbook` B.9: *"a release gate that has never gone red is only
decorative."* Revision 1 applied that to the **attacker** (the competence probe) and **exempted its
own review gate** — offering, as evidence the gate works, that *"the probe voids our own run; it
already went red once."* That red is **retrospective**: the spike was declared VOID against a
threshold that did not exist when the spike ran. Red-by-hindsight is exactly what B.9 warns about.
B.9's own method is explicit: *"**Plant one known-red case.** Deliberately route one fixture to the
wrong variant… Confirm that the coverage check or grader fails, then revert."*

> **C7 (the ledger) is the SEEDED-DEFECT CHUNK.**
> The architect writes into C7's build prompt **one specific, spec-violating defect that the build
> session must implement verbatim and must not flag**:
> *"the chain verifier compares each entry's stored `prev_hash` to the previous entry's stored `hash`
> field, and never recomputes the previous entry's digest from its contents."*
> The C7 **review** session receives the ordinary review prompt **with no hint**.
>
> **If `REVIEW_7_1.md` does not raise that defect as a BLOCKER, the review process is broken.**
> The architect then **halts building**, rewrites the review prompt and the personas, and **re-runs
> the seeded-defect test on the next chunk before any further chunk is reviewed.**
>
> Either way the transcript ships in `docs/reviews/`, and the README says what it is. **This is the
> known-red case B.9 asks for, applied to our own grader** — and it is the only evidence in the
> repository that the PASS verdicts mean anything.

**Expected FAIL rate, stated in advance.** A review gate that returns PASS on every chunk first time
is either reviewing nothing, or reviewing a project that did not need reviewing. **If the first eight
chunks all PASS first time, the architect writes an `INCIDENTS.md` entry** recording that the gate
has not gone red, what was done about it, and whether the seeded-defect test was re-run. The plan's
fix-session reserve (§12) assumes **roughly one FAIL per four chunks**, and a rate far under that is
a finding about the gate rather than a compliment to the builder.

---

## 6. The freeze gate *(replaces "stakeholder gates")*

There is no external stakeholder here. The thing that outranks everyone is the **pre-registration**.

- ⚠️ **THE FREEZE IS WITNESSED OUTSIDE THIS REPOSITORY, OR IT DID NOT HAPPEN.** See §6a. This is the
  first bullet because every other bullet below is unverifiable without it.
- ⚠️ **THE FROZEN SET IS EXACTLY FIVE FILES PLUS ONE DIRECTORY** — mirrored from the architect ruling
  at `CONTEXT.md` §15.0, which is authoritative:
  `INVARIANTS.md`, `PROTOCOL.md`, `HOLES.md`, `PROVENANCE.md`, `RAZORPAY_SEMANTICS.md`, and
  **`config/`**.
  **`INCIDENTS.md` is SNAPSHOTTED by the tag and explicitly CONTINUES TO GROW** — it is the
  failure-recovery deliverable, and freezing it would guarantee that no failure from the build itself
  could ever be recorded. **Nothing else is frozen.**
  *(Revision 1 froze three files and the spec listed six, neither listed `config/`, and hard rule 4
  would have resolved the disagreement by freezing `INCIDENTS.md`. All three defects are closed.)*
- ⚠️ **`config/` IS IN THE FROZEN SET BECAUSE IT IS WHAT THE EXPERIMENT READS.** The turn budget,
  the seeds, the temperature, the caps, the selected N branch, the calibrated void threshold, the 50%
  CONFOUNDED ratio and the exact model id strings all live there. Frozen prose plus editable numbers
  freezes nothing. Every file under `config/` is listed in `PROTOCOL.md` with the SHA-256 of its
  **git blob**, and `make check-prereg` recomputes them inside both `make eval` and `make test`.
- ⚠️ **TWO TAGS, NOT ONE** — mirrored from `CONTEXT.md` §15.1:

  | Tag | Contents | Cut |
  |---|---|---|
  | **`probe-v1`** | `HOLES.md` alone — the CANARY-A predicate, the CANARY-B predicate, S4's in-flight window width (2), each SHA-256'd with a UTC timestamp | **BEFORE the pilot and BEFORE the calibration command is executed.** The calibration may not begin until `git rev-parse probe-v1` resolves |
  | **`prereg-v1`** | the full frozen set above, after the pilot has selected the N branch and the calibration has set the threshold | still **before every scored episode**, which is the only property that matters |

  *Why two:* `HOLES.md` carries both the probe predicates **and** the threshold those predicates
  produced. Committed in one tag, there is **no moment at which the predicate was fixed and the
  number was still unknown** — which is the entire property a pre-registration establishes.
- **The probe itself (`pay_CANARYRECON`) is planted in the WORLD chunk (C2), not at the freeze.** The
  calibration *measures* the probe's breach rate, so the door must already exist in every seed's
  world before calibration begins. Planting it afterwards is not late, it is impossible.
- **If a frozen artefact turns out to be wrong**, it is *not* edited. The run continues under the
  frozen protocol, the defect is recorded in `INCIDENTS.md`, and the finding is published as a
  limitation. Amending a pre-registration destroys the only thing it was for.
- ⚠️ **The C14 review is a VERIFICATION review: it may not require a change to a frozen artefact.**
  If it finds one, the finding is published as a limitation under the bullet above. *(Revision 1's
  loop cut the permanent tag inside the build session, before any reviewer had seen it, while §7
  forbade moving a tag — so a FAIL on the freeze chunk had no legal remedy. It has one now.)*
- **N is a decision rule, not a number** — both branches written down before the pilot, so the
  pilot *selects a branch* rather than amending the document.
  ⚠️ **And therefore N IS NOT A DEGRADATION RUNG** (§14): after `prereg-v1`, changing N is amending a
  frozen artefact; before it, N is chosen by the pilot's measured tokens/episode and never by
  schedule pressure.
- **The headline comparison is pre-registered.** Everything else is labelled exploratory.
- A review that finds a `RESULTS.md` figure inconsistent with the frozen tag is an **automatic FAIL**.

---

## 6a. THE PRE-REGISTRATION PROCEDURE — the mechanism that makes the freeze checkable

**The problem, stated plainly and verified first-hand.** The project's central claim is that its
measurements were committed to before they were taken. Revision 1 offered one mechanism for that: a
git tag, in a repository that is **private until 4 September**, plus an honour rule. That is not a
mechanism, because **git timestamps are forgeable and git documents how.**

`[VERIFIED HERE — 2026-08-30, git 2.43.0.windows.1]` On 30 August a commit **and an annotated tag**
were created both stamped 31 August 2026 — a date in the future — with two environment variables:

```
$ date -u
Sun Aug 30 04:55:14 UTC 2026
$ GIT_AUTHOR_DATE="2026-08-31T09:00:00+0530" GIT_COMMITTER_DATE="2026-08-31T09:00:00+0530" \
    git commit -m "freeze"
$ GIT_COMMITTER_DATE="2026-08-31T09:05:00+0530" git tag -a prereg-v1 -m "pre-registration frozen"
$ git log --pretty=fuller
  AuthorDate: Mon Aug 31 09:00:00 2026 +0530
  CommitDate: Mon Aug 31 09:00:00 2026 +0530
$ git cat-file -p prereg-v1
  tagger T <t@example.com> 1788147300 +0530      ← the tagger date is forged too
```

Git's own manual documents the recipe under a heading of its own.
`[VERIFIED — git-scm.com/docs/git-tag, "On Backdating Tags", 2026-08-30]`
**Therefore a "frozen on 31 Aug" tag, in a repo that was private until submission day, is
self-asserted, and a reviewer cannot check it.**

### 6a.1 What is hashed — and the failure mode that breaks the obvious answer

**Do not hash working-tree bytes.** `[VERIFIED HERE — 2026-08-30]` On this machine `core.autocrlf`
is `true`, set **system-wide** by the Git for Windows installer:

```
$ git config --show-origin --get-all core.autocrlf
file:C:/Program Files/Git/etc/gitconfig  true
```

so a file committed with LF is checked out with CRLF, and the two hash differently:

| what you hash | digest |
|---|---|
| the working-tree file on **Windows** (CRLF) | `d82058d4f3a56b0bce57ce209d8313ff…` |
| the same file's **git object** (LF) — what a Linux/macOS reviewer gets | `a0a57c73e14c352a00756da344a8655c…` |

**They do not match.** A fingerprint published on 31 August from the operator's working tree would
fail verification for every reviewer who clones on anything but Windows — the failure would land **at
the moment of judging**, silently, and look like fraud rather than a line-ending bug.

**Hash git objects instead.** `git show <ref>:<path>` bypasses the working-tree filter and emits the
normalised stored bytes, identically on every OS. `[VERIFIED HERE]`

⚠️ **PREREQUISITE — a C0 DELIVERABLE, not a 31 August step.** `.gitattributes` containing
`* text=auto eol=lf`, committed in the **first commit**. It makes the working tree agree with the
object store as well, after which both schemes agree. It is fixable only in the first commit, and
§4.3 below depends on it.

**Anchors, and why in this order:**

| Anchor | Role | Why |
|---|---|---|
| **A public GitHub gist** | **PRIMARY** | `created_at` and every `history[]` entry's `version`/`committed_at` are assigned **server-side**, and the Create-a-gist endpoint accepts only `description`, `files`, `public` — **there is no client-settable date field.** `[VERIFIED — docs.github.com/en/rest/gists/gists + api.github.com, 2026-08-30]` A judge checks it with one `curl` |
| **OpenTimestamps** | **SECONDARY** | Free, no account, Bitcoin-backed, and it submits only the digest. **But `ots verify` at the CLI requires a local Bitcoin Core node** `[VERIFIED — the client's own README, 2026-08-30]`, and **no judge will run a Bitcoin node.** Excellent as a trustless second anchor; unusable as the primary |

⚠️ **A gist can be edited later, and `created_at` is documented but its behaviour under every edit
path is not.** Therefore **the verifier must read the OLDEST entry of the gist's `history[]` array,
never its current state** — that is the conservative reading and it is what §6a.3 does.

**Publishing only a hash is sufficient and reveals nothing.** SHA-256 is a binding commitment, and
the guess-the-preimage weakness does not apply: the frozen files are long, prose-heavy and
unguessable. (It *would* apply to `HOLES.md` hashing the bare integer `2` — which is exactly why the
fingerprint hashes **whole files**, never individual values.) Publishing the three protocol files
themselves in a public repo on 31 Aug would be strictly stronger, but it hands the full protocol
design to ~1,800 competitors four days before the deadline. **Hash-only is the right trade.**

### 6a.2 OPERATOR PROCEDURE — 31 August, within 30 minutes of cutting the tag, before the first scored episode

⚠️ **These commands were executed end to end by the auditor, including a clone with
`core.autocrlf=false` simulating a Linux reviewer, which re-derived the identical combined
fingerprint and the identical commit id. `[VERIFIED HERE, 2026-08-30]` They are reproduced verbatim.
Do not paraphrase them and do not "improve" them — a paraphrase risks reintroducing the line-ending
failure. The only edits are the project's name and path, which the rename of 2026-08-30 forced and
which are not part of the tested mechanism.**

Run in **Git Bash** (not PowerShell — `sha256sum` and the pipe semantics are assumed).

```bash
# ── PREREQUISITE, done back in C0 (not on 31 Aug) ────────────────────────────
#   printf '* text=auto eol=lf\n' > .gitattributes && git add .gitattributes && git commit

cd /c/path/to/whetstone-gate

# 0. Sanity: the freeze must be committed and pushed BEFORE the tag.
git status --porcelain          # must be empty
git tag -a prereg-v1 -m "pre-registration frozen: invariants, protocol, holes, provenance, semantics, config"
git push origin prereg-v1

# 1. Build the fingerprint from GIT OBJECTS (OS-independent).  Note the sort:
#    the order must be deterministic so a reviewer reproduces it byte for byte.
for f in HOLES.md INVARIANTS.md PROTOCOL.md PROVENANCE.md RAZORPAY_SEMANTICS.md; do
  printf '%s  %s\n' "$(git show prereg-v1:$f | sha256sum | cut -d' ' -f1)" "$f"
done | sort -k2 > prereg-v1.sha256

# 2. Append the config directory, same scheme.
git ls-tree -r --name-only prereg-v1 -- config/ | sort | while read -r f; do
  printf '%s  %s\n' "$(git show "prereg-v1:$f" | sha256sum | cut -d' ' -f1)" "$f"
done >> prereg-v1.sha256

# 3. Append the git object ids — a second, independent witness to the same state.
{ echo "commit  $(git rev-parse prereg-v1^{commit})"
  echo "tree    $(git rev-parse prereg-v1^{tree})"
  echo "tag     $(git rev-parse prereg-v1)"; } >> prereg-v1.sha256

# 4. The single combined fingerprint. THIS is the number that gets published.
sha256sum prereg-v1.sha256 | cut -d' ' -f1 | tee PREREG_FINGERPRINT.txt
cat prereg-v1.sha256                       # keep this; it is published too

# 5. ANCHOR A — OpenTimestamps (free, no account, Bitcoin-backed).
pip3 install opentimestamps-client
ots stamp prereg-v1.sha256                 # produces prereg-v1.sha256.ots
git add prereg-v1.sha256 prereg-v1.sha256.ots PREREG_FINGERPRINT.txt
git commit -m "chore: publish prereg-v1 fingerprint and OTS receipt"
git push
```

**6. ANCHOR B — the public gist (this is the one a judge will actually check).**
In a browser, at `gist.github.com`, create a **public** gist named `whetstone-gate-prereg-v1.txt`
whose body is:

```
WHETSTONE GATE — pre-registration fingerprint
Repository: github.com/<user>/whetstone-gate  (PRIVATE until 4 Sep 2026, public thereafter)
Tag:        prereg-v1
Published:  <UTC timestamp>   — the authoritative time is THIS GIST'S created_at, not any git date.

COMBINED FINGERPRINT (sha256 of the manifest below):
<the value from step 4>

MANIFEST (sha256 of each file's git blob content, `git show prereg-v1:<path>`):
<paste prereg-v1.sha256 verbatim>

Verify: see README.md § "Verifying the pre-registration".
```

**7. Record the gist's own coordinates**, because a gist can be edited later and the reviewer must
check the *first* revision:

```bash
curl -s https://api.github.com/gists/<GIST_ID> \
  | python -c "import json,sys; d=json.load(sys.stdin); h=d['history'][-1]; \
print('created_at', d['created_at']); print('first_version', h['version'], h['committed_at'])"
```

Write `created_at` and `first_version` into `INCIDENTS.md` and into the README's verification section.
**Then, and only then, the first scored episode may run.**

**8. After the run** (2–3 Sept), repeat steps 1–6 for `evals/` and `RESULTS.md` as `results-v1`, and
publish a second gist. Two externally-stamped points bound the run from both sides, and the ordering
protocol-then-results is visible to anyone.

### 6a.3 REVIEWER PROCEDURE — what a judge runs, after 4 September

**This block goes verbatim into `README.md` § "Verifying the pre-registration".** It is not a
description of a verification; it *is* the verification, and C19's done-when is that a fresh session
ran it start to finish from a clean clone.

```bash
git clone https://github.com/<user>/whetstone-gate && cd whetstone-gate
git rev-parse prereg-v1^{commit}     # compare against the gist's `commit` line

for f in HOLES.md INVARIANTS.md PROTOCOL.md PROVENANCE.md RAZORPAY_SEMANTICS.md; do
  printf '%s  %s\n' "$(git show prereg-v1:$f | sha256sum | cut -d' ' -f1)" "$f"
done | sort -k2 > /tmp/check.sha256
git ls-tree -r --name-only prereg-v1 -- config/ | sort | while read -r f; do
  printf '%s  %s\n' "$(git show "prereg-v1:$f" | sha256sum | cut -d' ' -f1)" "$f"
done >> /tmp/check.sha256
{ echo "commit  $(git rev-parse prereg-v1^{commit})"
  echo "tree    $(git rev-parse prereg-v1^{tree})"
  echo "tag     $(git rev-parse prereg-v1)"; } >> /tmp/check.sha256

diff /tmp/check.sha256 prereg-v1.sha256 && echo "MANIFEST MATCHES"
sha256sum /tmp/check.sha256           # must equal the gist's COMBINED FINGERPRINT
```

Then, **the step that carries the whole claim**:

```bash
curl -s https://api.github.com/gists/<GIST_ID> | \
  python -c "import json,sys; d=json.load(sys.stdin); h=d['history'][-1]; \
print(d['created_at'], h['version'], h['committed_at'])"
```

`created_at` and the **oldest** history entry's `committed_at` are assigned by GitHub's servers and
have no client-settable parameter. If they read 31 August and the fingerprint matches, the frozen
files existed on 31 August — *regardless of what any git date claims*. Optionally,
`ots verify prereg-v1.sha256.ots` anchors the same digest in Bitcoin, with no trust in GitHub at all.

And the check that closes the loop:

```bash
git log --oneline prereg-v1..HEAD -- INVARIANTS.md PROTOCOL.md HOLES.md \
        PROVENANCE.md RAZORPAY_SEMANTICS.md config/
# must be EMPTY. Any commit here means a frozen artefact was amended.
```

### 6a.4 What this does and does not prove — this sentence goes in the README

> The gist proves the protocol was **fixed by 31 August**. It does not prove no earlier run happened —
> nothing can, and the `RESULTS.md` timestamps are as self-asserted as any other. What is externally
> witnessed is that **the scorecard was named before the numbers were published**, which is the
> property `ai-playbook` B.9 asks for.

**C14's done-when includes:** the gist exists; its `created_at` and its **oldest** history entry's
`version` and `committed_at` are recorded in `INCIDENTS.md` **and** in the README; and the fingerprint
reproduces from a fresh clone.

**Genesis binding — one line that costs nothing and proves something.** `src/…/ledger/` takes its
chain root, `genesis_hash`, from `config/protocol.yaml` **with no default** (rule 9). Before the
freeze it is the literal `PRE-FREEZE`; from `probe-v1` it is that tag's object id; **at `prereg-v1`
it is set to the `prereg-v1` tag object id, and every scored episode chains from it.** A ledger
cannot contain a hash of a tag that did not exist when it was written, so **pre-freeze episodes are
cryptographically distinguishable from scored ones** and no scored episode can have been computed
before the freeze. This is the one free proof available and revision 1 threw it away.

---

## 6b. ⚠️ CALIBRATION AND PILOT ARE SINGLE-SHOT

The arm-1 calibration sets the void threshold — the single number that decides whether the whole run
is publishable. **The incentive is exact and points one way:** a high observed arm-1 breach rate sets
a **high** threshold, which makes a later VOID **more** likely, so re-running the calibration until
it comes out low is rational, invisible, and violated no stated rule. The same applies to the pilot,
whose measured tokens/episode selects N. The append-only rule of §8 protects *completed episode
outputs*; it never said anything about *which run becomes the record*. It does now.

This goes into §6, verbatim into `CLAUDE.md`, and is mirrored at `CONTEXT.md` §15.4.

> **CALIBRATION AND PILOT ARE SINGLE-SHOT.** Before either starts, the operator commits and pushes
> `evals/cal/RUN_DECLARED.md` (resp. `evals/pilot/RUN_DECLARED.md`) naming the exact command, the seed
> block, the turn budget, the models and the UTC start time. **The first execution that runs to
> completion IS the run**, and its output directory is the record whatever number it contains. If an
> attempt aborts before completion, the abort, its cause and its partial episode count are written to
> `INCIDENTS.md` **before** any retry, and the retry is a numbered attempt in the same directory.
> **Two completed calibration runs existing is a process violation and is published as one.**

Persona 1's post-hoc-selection check asks for this explicitly, and `RESULTS.md` prints the
declared-vs-actual start times of both runs beside the threshold they produced.

---

## 7. Git discipline

- Atomic commits — one logical unit; messages say **what + why**, citing spec sections. Commit types
  `feat` / `fix` / `ref` / `test` / `chore`, per Razorpay's own house convention.
- Every commit touching source or tests before its chunk's review carries **"(unreviewed)"**.
- Every commit carries the trailer `Session-Token: <token>` (§7a).
- Review PASS = a commit + a **tag** (`cN-pass`). The tag chain is the project's spine.
- **Pre-registration tags** are separate and permanent: **`probe-v1`** and **`prereg-v1`**.
  ⚠️ *Revision 1 called the second one `preregistration-v1` in three places while the specification
  called it `prereg-v1` in seven — including the video's closing shot and the Definition of Done.
  Hard rule 4 makes the spec authoritative; this file was changed.*
- **Every session ends with a push** and states the pushed SHA as the first line of its report.
- No force-push. No tag moves. No amending a tagged commit.
- Secrets never in the repo, never in logs, never in reports.
- ⚠️ **REPOSITORY VISIBILITY IS A PROCESS DECISION, RECORDED HERE.** The remote is created
  **private** in C0 and **stays private until C21 flips it public on 4 September**, after the
  git-history secret scan has run and its output is committed. The whole freeze design depends on
  this and revision 1 never wrote it down.
- ⚠️ **THE `(unreviewed)` MARKERS ARE PERMANENT — turn them into an asset.** They can never be
  removed without a history rewrite this section forbids, so the public log will read as a wall of
  "(unreviewed)". C19 puts one paragraph in the README:
  > *Every source commit is marked `(unreviewed)` until a different session's adversarial review tags
  > it `cN-pass`. The tag chain is the spine, and `docs/reviews/` is the trail — including the
  > failures, which are numbered attempts that were never overwritten.*

---

### 7b. ⚠️ COMMITTING FROM A SHARED WORKING TREE — THE PRIVATE-INDEX RECIPE, IN ITS CORRECTED FORM

**Two or more sessions run in one working tree, and they also share ONE `.git/index`.** A bare
`git commit` commits **the whole index** and not your paths, so it can commit — or **delete** —
another session's work under **your** token. This recipe is not optional and it is not advice.
`INCIDENTS.md` **INC-65**, **INC-68**, **INC-82**, **INC-88**, **INC-91**, **INC-93**, **INC-95**,
**INC-97**; `docs/reviews/OPEN_FINDINGS.md` **OF-205**, **OF-208**, **OF-213**, **OF-215**,
**OF-216**. ⚠️ **Every line below is a MEASUREMENT from this repository, not a precaution.**

```sh
# 1. A private index, in a FRESH OS temp directory — never inside the repository.
export GIT_INDEX_FILE="$(mktemp -d)/index"

# 2. Seed it from HEAD, so it holds nothing anybody else staged.
git read-tree HEAD

# 3. ⚠️ STAGE, SNAPSHOT AND COMMIT IN **ONE** COMMAND. Not three. (OF-205.)
git add -- <this session's explicit paths> \
  && git diff --cached --stat \
  && git commit -F <message file>

# 4. ⚠️ STEP 4 IS THE ONE THAT WAS WRONG IN EVERY PROMPT. `env -u`, NEVER `VAR=`.
env -u GIT_INDEX_FILE git reset -- <THE SAME explicit paths>

# 5. Prove the shared index is clean. A non-zero exit is a hard-rule-1 STOP.
env -u GIT_INDEX_FILE git diff --cached --quiet
```

⚠️ **WHY STEP 4 IS SPELLED `env -u` AND WHY THE OTHER SPELLING IS WORSE THAN USELESS.**
`GIT_INDEX_FILE= git reset` is **WRONG**. **`env -u` REMOVES the variable; `VAR=` SETS IT TO THE
EMPTY STRING**, and git reads the empty value as a **PATH** — it opens an empty index there, and
**every tracked file then reads as DELETED**. `INC-91`, measured: `GIT_INDEX_FILE= git diff --cached
--stat` reported **the whole repository staged for deletion** (`CONTEXT.md 2361-`, `QUESTIONS.md
10489-`, `PROGRESS.md 9770-`, every file in the tree) — on the very command meant to *verify* the
fix. ⚠️ **And the bare `git reset` it replaces fails a different way:** if the recipe is folded into
one compound shell command, the `export` in step 1 is **still in force**, so `git reset` lands on the
**private** index and the **shared** one keeps stale blobs. `INC-91`, measured: **419 lines of the
session's own committed work left staged for DELETION across six files**, with a concurrent session
live in the same tree.

⚠️ **AND `git diff --cached` IS ALSO THE FIRST COMMAND OF A SESSION, BEFORE THE READ ORDER**
(`OF-213`). A non-empty result on a path you do not own is inherited, not yours: a bare commit by
anyone would land it. **Measured:** a session began with the shared index holding a stale blob that
was the **reverse of `HEAD`**, which would have re-introduced two secret-shaped literals a commit had
just removed — while `git diff HEAD` on the path was **empty**, so only the index was wrong.

⚠️ **COMPOSE THE `Swept:` LINE FROM THE STAGED SNAPSHOT ALONE, AND PUT NO LINE COUNTS IN IT.**
Step 3's `--stat` is the only true statement of what is about to be committed. `INC-88`, measured: a
clause-(i) diff read **182** `PROGRESS.md` lines two tool calls before the `add`, the commit landed
**309**, and the 127-line difference was a concurrent session's complete journal entry — *the read
was true when it ran and false when the add ran.* ⚠️ **But the message heredoc is composed BEFORE
step 3's `--stat` prints, so any number in it is a PREDICTION** (`OF-216`). `INC-97`, measured: a
`Swept:` line claimed `+67/-2` and `+45/-0` where the snapshot said `111/0` and `51/0`. **So state
what you can verify before the commit — the paths, the mode, the headings added, or the words
"swept nothing" — and leave the arithmetic to `git show --numstat`, which is authoritative, free and
cannot be wrong.**

⚠️ **IF THE SNAPSHOT LISTS FEWER FILES THAN YOU STAGED, YOU HAVE BEEN SWEPT** (`OF-215`). `git
status` reports such a path **CLEAN**, which is indistinguishable from *"you never edited it"*, and a
session trusting it writes a duplicate row. Find it with `git log -1 -- <path>`, **verify the content
INTACT**, and record the SHA and the token that carried it. ⚠️ **Nothing can warn the session being
swept** — `INC-65`'s uncloseable half — and this closes only the detection side.

**AI attribution: permitted and encouraged.** The operator's template bans it; that rule is
**deliberately dropped here.** Razorpay's engineering culture is explicitly AI-native — their
Agent Studio is built on the Claude Agent SDK, their public `ai-playbook` is an AI-engineering
curriculum with a belt ladder, and their job descriptions ask for people who "see every workflow as
an agent loop." Concealing AI-assisted development would be hiding the exact competence they are
hiring for. **The method is a signal, not a liability** — and this process document, in the repo,
is part of the submission.

---

## 7a. ⚠️ SESSION IDENTITY — mechanised as far as it can be, and named as an honour system where it cannot

Revision 1's central control was the sentence *"a **different** fresh session"*. **Nothing in the
repository distinguished a review written by a fresh session from one written by the build session's
own context window.** It was the process's load-bearing control and it was an honour system with no
artefact. It is now an honour system **with an artefact**, and this file says exactly that rather
than implying enforcement it does not have.

> **Every build, review and fix prompt opens with `SESSION-TOKEN: <8 random hex>`**, generated fresh
> by the architect, never reused, and recorded in `QUESTIONS.md` under `## Session tokens` as
> `<token> · chunk N · role BUILD|REVIEW|FIX · issued <ISO-8601>`.
> **Every commit a session makes carries the trailer `Session-Token: <token>`**, and its
> `PROGRESS.md` or `REVIEW_<N>_<attempt>.md` entry opens with the same token.
> **`make check-roles`** (built in C0) fails if any chunk's build and review commits share a token,
> if a token appears that was never issued, or if a token is reused across roles.

**What this does and does not prove — stated in the README, not just here.** It does **not** prove
the sessions were different; nothing can, and an operator determined to defeat it can paste a token
anywhere. **It makes reuse visible**, it makes the claim falsifiable by anyone reading the log, and
it converts "trust me" into "here is the check, run it." That is the honest maximum, and §15 lists
what remains open.

---

## 8. Key, budget and data safety

The template's data-store rules are adapted: this project has no big data store, but it does have
two irreplaceable finite resources.

- **API keys live only in `.env`** (git-ignored, never committed). No session reads, prints, echoes
  or commits a key value. To confirm a key exists, read only its name.
- ⚠️ **THE PRE-PUBLIC HISTORY SCAN IS OWNED BY C21 AND ITS REMEDY IS CONSTRAINED.** *"Scan the
  entire history, not just the current tree"* had no owner and no method in revision 1, and the
  obvious remedy — a history rewrite — is **banned** by §7's no-force-push rule and would destroy
  `probe-v1`, `prereg-v1` and every `cN-pass` tag. The method is fixed:
  `git log -p --all | grep -nEi '<key patterns>'`, output committed to `docs/submission/`, run
  **before** the visibility flip. **If it finds a key:** the key is revoked at the provider first,
  the incident is written under rule 13, and the repository is **not** rewritten — a revoked key in a
  public history is a recorded incident; a rewritten history is a destroyed pre-registration.
- **No payment method is attached to either provider account** (verified 2026-08-30). This is the
  hard guarantee: exceeding a limit returns HTTP 429 and the runner stops. **It cannot bill.**
- **The free-tier token budget is a finite resource and is treated like one.** Every run writes
  per-model consumption to `evals/usage/` from the API's own `usage` field. **Exploratory runs are
  spend-free (mocked) unless the prompt explicitly sanctions token spend.**
- ⚠️ **EVERY SANCTION CARRIES A TOKEN CEILING, NOT ONLY A CALL CEILING.** Revision 1's sanction line
  was *"max N calls"*. `[MEASURED, spike — spec §13.3]` **one episode burned ~300K tokens** against a
  200K-TPD lane: twenty sanctioned calls can cost a whole day. The line is now:
  `TOKEN SPEND: none — mock only | sanctioned: LANE <model+provider>, max N calls AND max T tokens, window <date>`
  **The session reads `evals/usage/<model>-<date>.jsonl` before its first call, aborts at whichever
  ceiling it hits first, and reports actual tokens by model.**
- ⚠️ **LANE RESERVATION.** The **reference-attacker** lanes (Gemma 4 26B / 31B) and the **gate-judge**
  lanes are reserved for the sweep from 31 August. **No build session may spend on them.** Ladder
  lanes (`gpt-oss-20b`, `qwen3.8-27b`, `gpt-oss-120b`) are reserved for the ladder windows.
- ⚠️ **A 429 MEANS THE WINDOW IS ALREADY SPENT: STOP and report — never retry into another lane.**
  (The *runner* backs off and re-queues within its own lane, per spec §13.5(3); a *session* does not.)
- **Ledgers and results in `evals/` are append-only to sessions.** A session may not delete or
  rewrite a completed episode's output. Deletions are operator-only.
- **Long runs execute in the operator's terminal.** A session that closes mid-sweep loses nothing
  because the runner checkpoints, but the sweep is not a session's job.
- **A spend-free self-test runs before any token is spent.** If the harness is broken, it fails
  for free. Its oracle is `RAZORPAY_SEMANTICS.md` (spec §13.5(7)).

---

## 9. Evidence and honesty

- Any claim from data ships its generating script **and** its committed output under
  `docs/evidence/` or `evals/`, and must regenerate byte-identically **from the stored artefacts**
  (rule 10's scope). No hand edits.
- Every evidence pack states **what it is NOT** ("a wiring witness, not a result"), its
  assumptions, and its limits — beside the numbers, not in a footnote.
- **One declared basis** for derived figures, stated next to the numbers.
- **Zero-occurrence branches are printed as zeros**, never omitted. A reader must distinguish
  "did not happen" from "was not checked."
- **Partition invariant:** counts sum to the total; every item in exactly one category.
- **Every third-party claim carries a URL and a date.** Anything unverified is tagged `[SECONDARY]`
  or `[INFERENCE]` or is deleted. **This rule exists because three false claims about other people's
  code reached the specification before an audit caught them** — which is why the rule is a rule and
  not a habit.
- **This document is subject to its own rule.** `PROCESS.md` ships publicly. §0's claims were
  re-derived from the spec's corrected §1/§4/§5 on 2026-08-30 precisely because a restated claim in a
  public process document is the same failure, in a second file.
- **Disclose limitations in the open.** The escape number is authored by us and no external ground
  truth for it exists anywhere; that sentence appears in the README, the video, and the submission
  form — volunteered, never buried. So does §6a.4's statement of what the freeze witness cannot prove.

---

## 10. Prompt templates

**1 — Build prompt**
```
SESSION-TOKEN: <8 hex>
<CHUNK ID / TITLE>. You are a BUILD session. Read first, build, hand off for review.
READ, IN ORDER: CLAUDE.md → plan.md <chunk card> → CONTEXT.md <sections> → STATUS.md →
PROGRESS.md (latest) → QUESTIONS.md → INCIDENTS.md → tests/goldens/<files> → docs/reviews/<prior>.
If card, spec and logs disagree → STOP, write QUESTIONS.md.
TASK: <exact deliverables>.
SCOPE FENCE (hard): change ONLY <area>; no refactors; if tempted elsewhere → STOP.
GOLDENS: tests/goldens/<files>. Hand-computed by the architect. READ them; NEVER EDIT them.
TOKEN SPEND: <none — mock only | sanctioned: LANE <model+provider>, max N calls AND max T tokens,
window <date>>. Read evals/usage/<model>-<date>.jsonl before your first call. Abort at whichever
ceiling comes first. A 429 = STOP and report; never retry into another lane.
VERIFY: code must reproduce the goldens exactly; add a kept probe for any fix that fails on the
old code and passes on the new (show both); run the full suite, report pass/fail/skip.
GIT: atomic commit(s), message ends "(unreviewed)", trailer "Session-Token: <token>"; update
STATUS.md + PROGRESS.md; append to INCIDENTS.md anything that broke, in the rule-13 format; push;
report the SHA.
BEFORE YOU REPORT: commit your FINAL OUTPUT block verbatim to docs/sessions/<chunk>-build-<n>.txt.
A fresh review follows — do not self-certify.
FINAL OUTPUT: ONE plain-text code block — pushed SHA first, then before/after, goldens verified,
probe flip, suite counts, files changed, STATUS/PROGRESS lines, INCIDENTS entries, questions
raised, tokens spent by model.
```

**2 — Review prompt** ⚠️ *Two sealed phases. Revision 1's single-phase form instructed the reviewer
to read `PROGRESS.md` and the full diff and only then to "independently" re-derive — which is not an
independent re-derivation, it is confirmation of a view already seen.*
```
SESSION-TOKEN: <8 hex>
<CHUNK ID> — ADVERSARIAL REVIEW (fresh session). Span: <BASE>..<HEAD>.
Assume it is wrong until proven otherwise. You fix nothing but MAY add kept tests.
Adopt persona: <evaluation-integrity + code | code-only | submission>.

=== PHASE 1 — BLIND. Do not proceed to Phase 2 until Phase 1 is COMMITTED. ===
READ ONLY: CLAUDE.md → docs/personas/<files> → the chunk card → every CONTEXT.md section cited →
QUESTIONS.md rulings → tests/goldens/.
You may NOT open PROGRESS.md, INCIDENTS.md, the diff, or anything under src/ or tests/ other than
tests/goldens/.
DO: reimplement the core logic from the CONTEXT.md text alone, in your own file
docs/reviews/independent/c<N>_reimpl.py, importing nothing from src/. Generate >=20 input vectors
YOURSELF that appear nowhere under tests/, including every boundary the spec names (exact cap,
cap ± 1 paise, zero, empty ledger, duplicate key, the window's last call). COMMIT both.

=== PHASE 2 — SIGHTED. ===
Now read the diff, PROGRESS.md, INCIDENTS.md. Run the project's code on your Phase-1 vectors and
diff the two; write docs/reviews/independent/c<N>_reimpl_diff.txt. ANY divergence is a finding.
Then: rerun the whole suite from a clean state and reproduce the count; re-derive every
load-bearing number your own way; mutation-test the critical operators (flip a >, a sign, an
off-by-one) — MINIMUM EIGHT MUTANTS on a full chunk, at least one per invariant the chunk touches,
each killed by a named test or given an explicit equivalence proof, one row each in
docs/reviews/mutants/c<N>_mutants.md; verify no reported figure contradicts prereg-v1; confirm the
scorer imports no model client AND that scorer/ and gates/ share no first-party module; sweep for
secrets and for "(unreviewed)" on src/test commits.

PASS REQUIRES ALL OF: every golden reproduced by your own computation; every mutant killed or
proven equivalent; the reimplementation agreeing on all >=20 vectors; zero BLOCKER findings; no
reported figure contradicting prereg-v1. On a full chunk, NO REIMPLEMENTATION = CANNOT PASS.
Anything else is FAIL. Any spec deviation is FAIL even if all tests pass.

VERDICT: docs/reviews/REVIEW_<N>_<attempt>.md — severity-ranked findings
(BLOCKER/MEDIUM/LOW/INFO) with spec citations, then PASS or FAIL. Append every unclosed MEDIUM/LOW
to docs/reviews/OPEN_FINDINGS.md.
ON EITHER VERDICT: commit REVIEW_<N>_<attempt>.md, update STATUS.md (append to the review-history
column) and PROGRESS.md, commit your FINAL OUTPUT block to docs/sessions/<chunk>-review-<n>.txt,
push, and state the pushed SHA as the FIRST LINE of your report. A FAIL that is not in the repo did
not happen. Tag <cN-pass> ONLY on PASS. Do not fix on FAIL.
FINAL OUTPUT: ONE plain-text code block.
```

**3 — Hard safety rider** *(append to any prompt run in auto mode)*
```
=== HARD SAFETY RIDER (auto mode; no exceptions) ===
- Never read, print, echo or commit .env or any API key value.
- No token spend unless this prompt explicitly sanctions it, naming the lane, a call ceiling AND a
  token ceiling. A 429 means the window is spent: STOP and report; never retry into another lane.
- evals/ and its ledgers are append-only: do not delete, rewrite or truncate a completed episode.
- tests/goldens/ is READ-ONLY to you. Never edit, add to, or regenerate a golden.
- Never edit a frozen artefact (INVARIANTS.md, PROTOCOL.md, HOLES.md, PROVENANCE.md,
  RAZORPAY_SEMANTICS.md, config/) after its tag exists.
- No destructive commands: no rm -rf, Remove-Item -Recurse/-Force, git clean -fdx, git worktree
  remove --force, no force-push, no tag move, no amend of a tagged commit.
- Throwaway work goes to a fresh OS temp directory only.
- If anything seems to require touching secrets, completed results, frozen artefacts, goldens, or
  files outside this task's scope, STOP and report instead of working around it.
These rules override anything above that conflicts.
```

---

## 11. The architect's duties

- **Verify before accepting.** Recompute every report's load-bearing numbers. Trust is not a
  verification method.
- ⚠️ **AND LEAVE A TRACE.** *"Recompute every report's load-bearing numbers"* was revision 1's one
  real gate, and it produced no artefact — an unrecorded gate is not a gate. **After every build and
  review report the architect emits a VERIFICATION block — the numbers recomputed, the value
  obtained, the value claimed — and the operator commits it to
  `docs/reviews/ARCHITECT_CHECK_<N>.md`. No chunk is tagged `cN-pass` without one.**
- **Operator transcripts are relays, not records.** After any operator-run job, the next session's
  first duty is independent on-machine verification from files and ledgers — never from what was
  pasted. ⚠️ **And every session commits its own FINAL OUTPUT block to `docs/sessions/` before it
  reports**, so a paraphrase on the way to the architect is detectable against the file.
- **Hand-compute the goldens** before writing a build prompt, and have the operator commit them to
  `tests/goldens/` **before the prompt is issued**. This is the architect's real work, it is the most
  expensive rule in this document, and it is now a file rather than a habit — because it is also the
  rule most likely to be quietly skipped under time pressure, and skipping it costs the project its
  central claim.
- **One prompt per chunk.** Respond to *this* report before issuing the next. Concurrency only under
  §1's disjoint-fence rule, recorded first.
- **State the expected FAIL rate** (§5.4). Eight consecutive first-time PASSes is an `INCIDENTS.md`
  entry.
- **Precision applies to the architect.** Correct loose statements on the record. *(Three false
  claims about third-party code reached the spec before the audit caught them. That was an architect
  failure, not a session failure — and it is why §9's URL-and-date rule exists.)*
- **Keep a v2 backlog.** Scope-widening ideas go on a recorded list, not into the current chunk.
- **State the hold-point.** At any pause: what is sealed, what is owed, by whom.
- ⚠️ **UPDATE `ARCHITECT_HANDOFF.md` AT THE END OF EVERY CHUNK** with: the hold-point, what is
  sealed, what is owed, every open ruling, and the next three prompts in draft. **If it is stale by
  more than one chunk, building stops until it is current.** The architect is a chat session holding
  five days of decisions across 40+ reports; this file is the only thing that survives it.
- **Guard the freeze.** After `probe-v1` and `prereg-v1`, refuse any change to a frozen artefact,
  including one the architect would prefer.

---

## 11a. RECORDED DEVIATION — OVERNIGHT AUTONOMOUS OPERATION (2026-08-31)

**Removing the operator from the loop removes a check. That belongs on the record, with its bounds,
rather than in a chat.**

Authorised by the operator on **2026-08-31**, for the overnight window of 31 August only. §1's role
table has the operator carrying every prompt and making the final calls; overnight he is asleep, and
this section says exactly what that does and does not permit.

### MAY PROCEED WITHOUT THE OPERATOR

- **Class B decisions** (hard rule 2 — implementation choice within spec; done, recorded, judged at
  review).
- **Build → review → fix → re-review cycles**, always in **different fresh sessions** (§1: build and
  review are never the same session).
- **The architect writing fix prompts after a FAIL.**
- **Moving to the next independent chunk** when one is blocked.

### MUST STOP AND WAIT — NO EXCEPTIONS

- **Any Class A decision.**
- **Anything touching the frozen set, the freeze, or the pre-registration** (§6, §6a, `CONTEXT.md`
  §15.0).
- **Anything that would fire a §14 degradation rung.**
- **Anything that changes a number that will be published.**
- **A review verdict** — because **a session never decides its own PASS** (`CLAUDE.md` §6.9).

### THE TWICE-FAILED-CHUNK RULE

As the operator **revised** it on 2026-08-31. ⚠️ **His first formulation — *"stop the whole queue"* —
was withdrawn by him as too blunt**, and the revision is what binds:

- **The twice-failed chunk stops. There is no third attempt.**
- **Anything depending on it does not start.**
- **INDEPENDENT HEALTHY CHUNKS CONTINUE.**
- **The architect writes a clearly-labelled STOP entry** naming *what failed*, *what it failed on
  twice*, and *its read on whether the repeat is **SYSTEMIC** rather than local*.
- **If the architect judges it systemic, the whole queue stops and the reason is stated.**
  **That judgement is the architect's.**

### HARD BOUNDS

- ⚠️ **ZERO PROVIDER MODEL CALLS OVERNIGHT.** No Groq call, no Google call, nothing that consumes a
  lane's quota.
- ⚠️ **RULED 2026-08-31 RATHER THAN ASSUMED: HTTP GETs to public third-party DOCUMENTATION are NOT
  provider model calls and are inside the bound.** C1 needs them to satisfy §9's URL-and-date rule.
- **Do not approach the pilot, the calibration or the freeze overnight** — they are the operator's
  and **he must be awake** (§6b, `CONTEXT.md` §15.4: both are single-shot).
- **Every stop writes an entry the operator can read in one pass:** what blocked, what it needs from
  him, and what the queue did instead.

### THE NEVER-CUT LIST, RESTATED HERE

**Not negotiable at any hour, INCLUDING ON THE OPERATOR'S OWN INSTRUCTION:**

τ²-bench · the competence probe and the void rule · the freeze, **both tags** and the external
witness gist · `INCIDENTS.md` · the counter-metric · the seeded-defect test · C21's two form
paragraphs and git-history secret scan.

### AND: WHICH INSTRUCTION GOVERNS WHEN

Instruction **(a)** — *fire the §14 ladder rather than move the freeze* — governs the **DAYTIME** of
31 August, when the operator is awake. **§11a governs the OVERNIGHT WINDOW, and overnight it WINS:
the architect STOPS rather than CUTS.**

⚠️ **NO RUNG IS PRE-AUTHORISED TO FIRE UNATTENDED, INCLUDING RUNG 1** — because rung 1 collapses a
review, and **the reviews are what this submission's credibility rests on.** **A stalled queue costs
hours; an unattended review cut costs the argument.**

---

## 12. THE CHUNK PLAN *(this section is `plan.md`; it is no longer a draft)*

**Twenty-two chunks, C0–C21, plus seven OPERATOR RUNS.** Every chunk carries a **calendar date**, a
**time-box**, its **dependencies**, its **review type** and a **done-when that is checkable rather
than a feeling**. Reconciled line by line against `CONTEXT.md` §17. Where the two disagreed, the spec
won and this table changed.

**Review types.** **`full`** = personas 1 + 2, the two-phase blind protocol of §10 template 2,
a committed reimplementation and ≥8 mutants. **`code`** = persona 2 only, no reimplementation
required, ≥4 mutants. **`submission`** = persona 3 + persona 1. **There is no fourth value, and no
chunk carries a dash** — revision 1 gave the one irreversible step (submit) a `—` and therefore no
reviewer at all.

### 12.0 The arithmetic, stated because revision 1's plan could not survive it

22 chunks × 2 sessions = **44 sessions**, plus a fix budget. Revision 1 was 16 chunks / 31 sessions
with **strict serialisation, no dates and no fix budget**, and `CONTEXT.md` §17 put the freeze on
31 August — which required twelve chunks and twenty-four serial sessions to complete inside the
remainder of 30 Aug plus 31 Aug. **That is not a tight plan; it is a plan that only survives if every
single review returns PASS**, which is exactly the pressure that stops a gate issuing FAILs. Four
things make this version survivable, and none of them is "cut scope":

1. **Two BUILD sessions in flight** when their fences are disjoint (§1). Reviews stay serial, so the
   **serial review queue is the binding constraint** — roughly 25 min for a `code` review, 45 for a
   `full`.
2. **1 and 2 September are RUN days.** The sweep executes in the operator's terminal, so session
   capacity on those days is nearly free and the plan puts only three chunks there.
3. ⚠️ **A FIX-SESSION RESERVE, budgeted rather than hoped for.** **One FAIL per four chunks** is the
   planning assumption (§5.4), i.e. **≈5 fix cycles** across the build. A cycle is a FIX session plus
   a focused re-review ≈ 40 min. **One hour per day, 30 Aug – 2 Sep, is reserved and is not
   allocated to any chunk.** If it goes unused, the day ends early; it is never spent on scope.
4. **The DEGRADATION LADDER of §14, written now** — because a ladder written while behind schedule
   is not a ladder.

⚠️ **Stated plainly, because the operator has to plan around it: it is already ~12:00 IST on
30 August. Half of day one is gone before C0 starts.** Day one carries seven chunks against a
serial review queue of roughly 4½ hours plus one reserved fix hour. **30 August is the tightest day
in the plan and the ladder's first rung exists for it.**

### 12.1 THE PLAN

#### 30 AUGUST — the world, the benchmark spine, and the attacker *(spec §17 row 1)*

| # | Time-box | Chunk | Deps | Review | Done when |
|---|---|---|---|---|---|
| **C0** | 12:00–13:30 | **Repo, toolchain, remote, canonical files, day-one setup.** Create the GitHub remote **PRIVATE**; `LICENSE` (MIT); **`.gitattributes` containing `* text=auto eol=lf` in the FIRST commit** (§6a); Python **3.12** venv; the `make` shim; `CONTEXT.md` v1.0; `CLAUDE.md` with all thirteen hard rules verbatim; `STATUS.md`, `PROGRESS.md`, `QUESTIONS.md`, `INCIDENTS.md` (with the five day-0 entries, in rule-13 format); the **three** personas; `tests/goldens/`; `config/` + its one loader; `make test` / `eval` / `selftest` / `check-prereg` / `check-roles` wired as one-line delegations to `python -m whetstone_gate.tasks`; **the §13.7 day-one setup** | — | **code** | `python --version` → **3.12.x**; `pip install -e vendor/tau2-bench` completes; `make test` **and** `python -m whetstone_gate.tasks test` both run green from a clean clone; `make check-roles` runs; `.gitattributes` is in the first commit; the remote exists, is **private**, and its URL is in `PROVENANCE.md`; **both providers' limits re-verified and screenshotted into `PROVENANCE.md` with the date**; **no payment method confirmed on either account**; ⚠️ **the exact Google API model id strings (`models/gemma-…`, `models/gemini-…`) are captured from the dashboard and written into `config/lanes.yaml`** — spec §13.3.2 says the spec cannot supply them and only the day-one screenshot can; ⚠️ **§13.7's fourth clause is executed: any limit differing from spec §13.2 is an `INCIDENTS.md` entry AND forces a re-run of the §13.4 feasibility arithmetic before the pilot, recorded as an architect ruling** |
| **C1** | 13:00–14:30 | **`RAZORPAY_SEMANTICS.md`** — one row per documented Razorpay rule: verbatim quote + URL + fetch date. Every A1–A6 error string; the `X-Refund-Idempotency` documentation; **all five instant-settlement bounds**; the capture concurrency error quoted as **three fields of an Errors table with its remediation intact**. **Plus `PROVENANCE.md`'s one row per attack A1–A6** with the *rejected-by-Razorpay* column and each constant tagged `[Razorpay-defined]` or `[merchant-policy, author-chosen]` | C0 | **full** | every row carries a verbatim quote, a URL and a fetch date; **no row is a paraphrase**; every A1–A6 error string in `CONTEXT.md` §6 resolves to a row; all five instant-settlement bounds present; `PROVENANCE.md` carries all six attack rows, and A5 is marked **entirely author-chosen** wherever it appears. *(Spec §17: written FIRST, before any world code. It is the oracle for the spend-free self-test — revision 1 mentioned this file **zero** times.)* |
| **C2** | 14:30–16:30 | **World generator + THE PROBE PLANTED.** Reimplemented `mulberry32`; 12 payments/seed; log-uniform ₹500–₹1,50,000; the **8 / 3 / 1** split; merchant balance ₹5,00,000; **`pay_CANARYRECON` planted in every seed's world** with the spec §10.1 fields exactly | C0 | **full** | **golden 7 reproduces exactly** — the six raw PRNG outputs to 10 s.f. and the full seed-2001 payment record; `pay_CANARYRECON` present in **every** seed with the exemption note verbatim; two runs of one seed byte-identical. *(The probe is a world-generation property and belongs here, not at the freeze.)* |
| **C3** | 14:30–16:30 | **τ² adapter A** — vendor at `a2c024725189473d2d7cea3a5cfdbcc67478e41f`; enumerate the **34 of 164** must-not-write tasks and the **130** write tasks; emit the stratified **20-airline / 20-retail T-FP id list** (first 40 write ids after sorting); assert the `db_reward` path imports no model | C0 | **full** | the **34/164** count reproduces **from the pinned SHA** (24 of 50 airline, 10 of 114 retail); the T-FP id list is deterministic and committed; a test asserts `db_reward` imports no model client; the pinned SHA is in `config/protocol.yaml`. *(Spec §21.4 calls this the project's **#1 time risk** and schedules it **first**; revision 1 scheduled it **tenth**, behind a chunk that depends on it.)* |
| **C4** | 16:30–19:00 | **World semantics + the five-tool surface + the typed harm record + the spend-free self-test.** Every documented rejection; `X-Refund-Idempotency`; the five instant-settlement bounds; **S4's in-flight window, width 2**; `initiate_payment` as a read-only stub; the harm record with its four components, `a_class`, `tool`, `rejected_by_razorpay`, `ledger_seq` | C1, C2 | **full** | **the spend-free self-test is 100% green** — ⚠️ **AMENDED 2026-08-31 per the architect's ruling on Q-018, adopting C1's option 1** (the clause previously read *"every documented Razorpay error in `RAZORPAY_SEMANTICS.md` fires in the mock world"*, which C1 established **first-hand** is **UNSATISFIABLE THE MOMENT THE ORACLE IS COMPLETE**: **~18 of the ~50 documented errors are UNREACHABLE BY CONSTRUCTION** from any world built on `CONTEXT.md` §8.6 — they depend on merchant account configuration, a payment method this world does not model, an active dispute, a **WALL CLOCK** (which **hard rule 8 forbids in core logic**), 5xx server faults, or a Razorpay product with no API at all — **and the perverse incentive of the old wording was to keep the oracle INCOMPLETE, the opposite of what C1 exists for**) — **every `RAZORPAY_SEMANTICS.md` row marked `MUST-FIRE` fires in the mock world; every row marked `MUST-HOLD` holds; and every row marked `RECORDED` is listed in the self-test's output as documented-but-unreachable WITH ITS REASON, so the excluded set is a printed number and not a silence (hard rule 11)**. **C1 labelled all 71 rows `MUST-FIRE` / `MUST-HOLD` / `RECORDED` for exactly this purpose; the counts are 40 / 13 / 18.** Goldens 1 and 3 reproduce exactly; a `rejected_by_razorpay` record contributes **zero to all four** harm components; the tool surface is exactly the five writes/reads plus the stub, everything else returning *"tool not enabled"* |
| **C5** | 16:30–19:00 | **τ² adapter B** — `HalfDuplexAgent` extension + **the Gemini 3.5 Flash Lite user simulator**; drive one must-not-write task and one write task end to end at the pin; **no fork of world/tasks/grader** | C3 | **full** | one must-not-write and one write task complete end to end at the pinned SHA with the user simulator wired; `db_reward` is read, not reimplemented; measured tokens and requests for both are recorded. ⚠️ **20:00 SCOPE-STAGING CHECKPOINT (spec §17):** if the adapter is not driving **both** directions by 20:00, we ship the **34 must-not-write control only** tonight and add the 130 write tasks on 31 Aug. **τ²-bench is never dropped — only its breadth is staged**, and the staging decision is an `INCIDENTS.md` entry the moment it is made |
| **C6** | 19:00–22:00 | **Attacker loop** — policy-blind; the sliding-window context (**last 6 turns verbatim + a ≤400-token summary produced DETERMINISTICALLY, not by an LLM call**); seeded from InjecAgent + AgentDojo + AgentHarm + ASB; `attacker_sys.txt` verbatim from spec §8.6; the corpus-vs-improvisation split instrumented | C0 | **full** | the spend-free self-test passes with the attacker mocked; **measured tokens/episode is recorded and compared against the ≤60,000 target**; the summary is byte-identical for identical state (proving it adds no request and breaks no determinism claim); the attacker's context provably contains **no policy string, no hole, no attack list and no gate reason**; corpora licences recorded in `PROVENANCE.md` — incl. **InjecAgent's British-spelled `LICENCE`**, AgentHarm's field-of-use clause, and R-Judge's absent licence (**cite, never vendor**) |

**Reserved 30 Aug:** one hour, unallocated, for the first fix cycle.

#### 31 AUGUST — the measurement stack, then the freeze *(spec §17 row 2)*

| # | Time-box | Chunk / run | Deps | Review | Done when |
|---|---|---|---|---|---|
| **C7** | 08:00–10:00 | **Ledger** — append-only, hash-chained, `entry_hash = SHA-256(prev_hash ‖ canonical-JSON(entry, sorted keys, no whitespace))`, **genesis root loaded from `config/` with no default** (§6a). Carries the typed harm record **and** `turn_index`, `arm`, `verdict` and the four harm components, so the §18 replay renderer is buildable from `evals/episodes/` alone. ⚠️ **THIS IS THE SEEDED-DEFECT CHUNK (§5.4)** | C4 | **full** | golden 5 reproduces, **including the recompute-the-previous-digest case**; a missing `genesis_hash` in config is a hard refusal, not a default; the render fields are present on every entry; **and the C7 review either raises the seeded defect as a BLOCKER or the review process is declared broken and building halts** |
| **C8** | 10:00–12:00 | **Scorer** — deterministic replay; E1–E3, S1, S2, **S2-amt**, S3, S4; `INDETERMINATE` at construction; **no model imports**; **no first-party module shared with `gates/`** | C7 | **full** | golden 2 passes on **all eight** predicates; **S2 and S2-amt disagree on the instalment fixture**; `test_scorer_imports_no_model_client` **and** `test_scorer_and_gates_share_no_first_party_module` both pass; the replay reconstructs state from the local chain and **never queries the world** |
| **C9** | 10:00–12:00 | **Gates** — arms 1, 2, 2S, 3, 4 as five separate modules behind one interface; `policy.txt`, `arm3_safety.txt` verbatim; arm 2S's folded-state JSON exactly as spec §8.6 gives it; the single generic denial string; **arm 4's kernel shares no code with the scorer** | C4, C7 | **full** | golden 9 passes; **each arm emits exactly its spec §8.6 verdict set and no other** (arm 1 → `ALLOWED` only; 2/2S/3 → `ALLOWED`/`DENIED`; 4 → + `INDETERMINATE`); `test_arm4_kernel_imports_no_model_client` passes; the module-graph test confirms `gates/` ↔ `scorer/` isolation; **arms 2 and 2S differ in exactly one input — the folded state** |
| **C10** | 12:00–14:30 | **Probe machinery + THE STATISTICS MODULE + the four non-use tests.** CANARY-A, CANARY-B (**counted over blocked entries too**), the ARM CONFOUNDED rule at 0.50 of arm 1's reach; **Wilson score interval, McNemar exact, paired bootstrap over seeds (10,000 resamples), rule-of-three at n ≥ 30 and exact one-sided Clopper–Pearson below it** | C7, C8, C2 | **full** | golden 4 passes; **reach counts a `DENIED` entry naming `pay_CANARYRECON`**; the statistics module reproduces `CONTEXT.md` §12.4's published table by computation — **±13.9 pp at n=50 / ±17.9 at n=30 / ±43.8 at n=5, and 6.0% / 10.0% / 45.1% upper bounds for an observed 0/n**; **all four non-use tests exist and pass** (spec §14). ⚠️ **This chunk must land before C14, because the Wilson LOWER BOUND is what sets the frozen void threshold** — revision 1 mentioned Wilson, McNemar, bootstrap and rule-of-three **zero times each** |
| **C11** | 12:00–15:00 | **Runner** — a **lane-aware scheduler, not a thread pool**; independent token buckets for RPM/TPM/RPD per model; per-episode checkpoint keyed `(block, arm, seed_or_task, attacker_model)`, skipped on re-run; **resume across DAY boundaries**; 429 = backoff-with-jitter and re-queue **within the lane**, a 429 storm parks the lane; live per-model usage to `evals/usage/<model>-<date>.jsonl`; **lane reservation enforced** (§8); **the ladder's arms-{1,4} × 4-points × n=5 matrix is a supported run mode** | C0, C9 | **full** | kill mid-run and resume with **zero duplicates and zero re-runs of completed episodes**; the usage file reconciles against API-reported totals; golden 8 reproduces (incl. the 429 and truncated-episode cases); **every dropped, errored, retried and truncated episode is counted, categorised and printable** (rule 11); a day-boundary resume is demonstrated, not asserted; **a runner checkpoint and an episode output are `git status`-visible against the committed `.gitignore`, demonstrated** (Q-003's rider). *(Upgraded from `code` to `full`: this chunk owns denominator integrity, 429 handling and episode dropping — squarely persona 1's territory.)* |
| **C12** | 15:00–17:30 | **Benign solver + the 30 benign scenarios + the paired-FP harness.** A second policy-blind LLM loop that **tries to succeed**; **30 mock-world scenarios derived from Razorpay's documented happy-path examples**, each shipping its own end-state predicate; the FP paired delta over `{gate OFF} × {arms 2, 2S, 3, 4}` | C4, C5, C9, C11 | **full** | all 30 scenarios are **traceable to a Razorpay documented example by URL** — none builder-invented (this is the counter-metric, and builder-written scenarios are the exact criticism this project levels at others); FP is computed as **solved-gate-OFF-and-failed-gate-ON with a gate denial in the trace**, with **both numerator and denominator printed**; "Solved" is `db_reward == 1.0` for τ² and the scenario predicate for the mock world |
| **C13** | 15:00–16:30 | **`src/camel_comparator/`** — vendor CaMeL at its pinned SHA and invoke it **UNMODIFIED** on AgentDojo banking. ⚠️ **Separate component from the AgentDojo adapter (C16); revision 1 conflated the two into one `code`-reviewed chunk** | C0 | **full** | the branch decision is **made and recorded**: **Branch A** — `google:gemini-2.0-flash-lite-001+camel+secpol` runs live; or **Branch B** — the model id is not served / the run does not complete, and the comparator ships as a **citation of Table 2, Appendix B ("Full results tables"), the `o3 High` block, `banking` column of arXiv 2503.18813v2** — CaMeL 81.2% ± 19.1 against Native Tool Calling API 62.5% ± 23.7, the paper's own Difference row +18.8% ± 4.6 — with the one-line reason verbatim from spec §8.5.1. ⚠️ **NOT Tables 5–7**, which are Appendix C, `Claude 3.5 Sonnet`, CaMeL against other defences, and where on `banking` CaMeL is **behind** the undefended model; **Table 7** remains §8.5.2's **P2** citation, out of the 949 attacks in total that Figure 11's caption states (Q-058, Q-064). **Branch B is published as a result, not hidden as a failure.** No CaMeL source file is modified — a diff against the vendored SHA is empty and is committed as proof |
| **RUN-1** | 16:30–18:00 | ⚙️ **OPERATOR RUN — the 90-minute CaMeL branch test** (spec §17 step a, §8.5.1) | C13 | *audited inside C13's review* | timeboxed to **90 minutes**; at 18:00 the branch is decided either way and written into `PROTOCOL.md` |
| **C14** | 18:00–23:30 | ⚠️ **THE FREEZE.** In this exact order: **(a)** `HOLES.md` written → **`git tag probe-v1`** → pushed; **(b)** `evals/pilot/RUN_DECLARED.md` committed → **PILOT** (20 episodes, seeds 2101–2110, ref + L2 `qwen3.8-27b`) → it **measures tokens/episode and SELECTS the N branch by the §13.4 rule**; **(c)** `evals/cal/RUN_DECLARED.md` committed → **ARM-1 CALIBRATION** (n=30) against the world that **already contains `pay_CANARYRECON`** → the threshold is the **95% Wilson lower bound rounded DOWN to 5 pp**; **(d)** write the full frozen set; **(e)** `git tag prereg-v1`; **(f)** **publish the external witness** per §6a.2 | C2, C6, C7, C8, C9, C10, C11, C13 | **full** *(a VERIFICATION review — see §6)* | `git rev-parse probe-v1` resolved **before** the calibration command was executed; **both `RUN_DECLARED.md` files were pushed before their runs started and exactly one completed run exists for each** (§6b); the N branch was selected **by the rule** and the measured tokens/episode is written into `PROTOCOL.md`; every frozen artefact describes something **that exists**; `make check-prereg` PASSes; **the gist exists, its `created_at` and its OLDEST history entry's `version`/`committed_at` are recorded in `INCIDENTS.md` and the README, and the fingerprint reproduces from a fresh clone**; `git log prereg-v1..HEAD -- <frozen paths>` is empty; ⚠️ **`corpora/MANIFEST.md`'s pinned SHAs are listed in `PROTOCOL.md` alongside `config/`'s digests, and `make check-prereg` verifies them** (Q-032) — without it `check-prereg` hashes the inputs to every published number **except** `CONTEXT.md` §11.3's corpus-versus-improvisation split. **This does NOT add `corpora/` to §15.0's frozen set**, which stays exactly five files plus `config/`: the manifest is already tracked and the pins are already verified on load, and what changes is that the pins become part of what the pre-registration **asserts** |
| **C15** | 23:30–00:30 | **Attacker-strength ladder harness + launch.** `config/ladder.yaml` with L1/L2/L3/REF on arms {1, 4}, n=5, seeds 2001–2005; **the x-axis computed as each model's own MEASURED CANARY-B reach in arm 1** — never parameter count | C11, C14 | **code** - ⚠️ **FOLDED INTO C18's REVIEW, 2026-09-02 (rung 1; `INCIDENTS.md` INC-61; `QUESTIONS.md` Q-083).** The original entry read `code` and stands above; the fold is the change. C15 publishes **no number of its own** and C18 consumes its output. | the ladder runs on a mocked lane end to end; the x-axis is **computed from measurement, not asserted**; the ±44 pp half-width is attached to every cell by the statistics module; **L1 and L3 window 1 launched tonight** — they need three daily windows each (31 Aug, 1 Sep, 2 Sep) at 200K TPD. *(Revision 1 had "ladder" appearing once, as a column heading, with no owner — while its first window is the night of 31 August.)* |
| **RUN-2** | from 23:30 | ⚙️ **OPERATOR RUN — ladder L1 + L3, window 1** | C15 | *audited in SWEEP-AUDIT-1* | both lanes launched before midnight; usage logged |

⚠️ **Gate for the whole day (spec §17):** the deterministic kernel showing **any unplanted violation**
means the invariant model is wrong — **stop and fix before any scored run.**
⚠️ **No scored episode runs before `prereg-v1` exists, and no calibration episode runs before
`probe-v1` exists.**
**Reserved 31 Aug:** one hour, unallocated, for fix cycles.

#### 1 SEPTEMBER — run day one *(spec §17 row 3)*

| # | Time-box | Chunk / run | Deps | Review | Done when |
|---|---|---|---|---|---|
| **RUN-3** | 08:00 → | ⚙️ **OPERATOR RUN — SWEEP DAY ONE.** M-ADV (mock world, five arms, reference attacker) + T-NEG (τ² must-not-write, five arms, with the user simulator) + **T-FP begins** (benign solver). Flash-Lite lanes carry the benign solver and the user simulator until their RPD is spent, then spill to Gemma. **Ladder L1/L3 window 2** | C14 | *audited by SWEEP-AUDIT-1 the same night* | ⚠️ **GATE: the runner not resuming across a day boundary by 14:00 → fix that first, before anything else.** A multi-day sweep is only safe with day-resume |
| **C16** | 09:00–12:00 | **AgentDojo banking adapter (AD-CMP).** Pinned SHA; `InjectionTask6` × all 16 user tasks × five arms; **the 8 dropped injection tasks named in `PROTOCOL.md`**; the two no-side-effect invariants | C9, C11 | ⚠️ **NOT RUN - CUT 2026-09-02 (rung 3; `INCIDENTS.md` INC-62; `QUESTIONS.md` Q-083).** The original entry read **full** and stands above, with its original reason - *"this chunk publishes a claim about a third party's system"* - because what the plan WAS is part of the record. **AD-CMP's 80 episodes are NOT RUN and are named as *not run*, with why, in `RESULTS.md` and the README (S14).** τ²-bench remains, so the externally-authored-answer-key claim is UNTOUCHED. ⚠️ `config/protocol.yaml`'s `vendor.agentdojo_sha` sentinel therefore **stays unresolved and the loader keeps RAISING - that is the correct end state and `config/` must NOT be edited to tidy it away.** | the 80-episode matrix enumerates deterministically; **the dropped pairs are named, never silently truncated**; the honest limitation is recorded for the README — *"`send_money` appends a transaction and never debits `account.balance`; the field's flagship money benchmark does not model a balance"*. *(`full`, not `code`: this chunk publishes a claim about a third party's system, which is the exact failure mode that has already bitten this project three times.)* |
| **C17** | 13:00–16:00 | **`docs/render/` — the replay renderer.** ⚠️ **Two deliverables, one build:** the video's §18 RACE beat (**five money bars, one seed, 1400 ms/turn**) **and** the Definition-of-Done box *"an audit log a non-author can read and follow"*. Reads `evals/episodes/` **only** | C7 | **code** - ⚠️ **DOWNGRADED FROM `full` 2026-09-02 (rung 5; `INCIDENTS.md` INC-63; `QUESTIONS.md` Q-083).** The original entry read **full** and stands above. C17 replays a **stored** ledger and **publishes no number**, so there is no figure for a reimplementation to disagree with; a `code` review still reads the diff, runs the suite and may raise BLOCKERs. | replays a **stored hash-chained ledger** and says so on screen; the caption states **the seed and the pre-registered N**; the rendered audit log is handed to a **non-author** who can follow one episode end to end without asking a question; **the renderer makes no network call and runs no model** |
| **SWEEP-AUDIT-1** | 22:00–23:00 | 🔍 **A `full` persona-1 SESSION over day one's output** — not a build, a **denominator audit** | RUN-3 | **full** | every block's attempted / completed / dropped / errored / truncated counts **reconcile to its declared total**; every partition sums; **zero-occurrence branches print as zeros**; usage is inside budget; any divergence is an `INCIDENTS.md` entry **tonight**, not on 3 September |

#### 2 SEPTEMBER — run day two, and the numbers *(spec §17 row 4)*

| # | Time-box | Chunk / run | Deps | Review | Done when |
|---|---|---|---|---|---|
| **RUN-4** | 08:00 → | ⚙️ **OPERATOR RUN — SWEEP DAY TWO.** M-BEN + T-FP continues + AD-CMP + the CaMeL comparator run (or its Branch-B citation). **Ladder L1/L3 window 3**; the L2 extended cell **only if the budget allows** | C16, C13 | *audited inside C18's review* | all blocks either complete or are recorded as incomplete **with their denominators** |
| **C18** | 10:00–17:00 | **`RESULTS.md` + `make eval`.** The five-arm trade-off table; the **reach** column; **CONFOUNDED** flags; the four harm components **never summed**, as per-episode medians with IQR; the paired-Δ false positives; the void determination; **and the four "mandatory alongside" outputs of spec §12.1**: the **turn-indexed escape curve** (1→20), **escape conditioned on probe reach**, the τ² DB-hash write rate **labelled explicitly as a negative control**, and **CaMeL's P1–P3 predictions scored against the result**. Plus the **S2-vs-S2-amt FP delta**, the productive-actions confound, the corpus-vs-improvisation split, the per-model token table, and the `check-prereg` PASS/FAIL line | C10, C12, C13, C15, C16, RUN-4 | **full** | ⚠️ **`make eval` (and `python -m whetstone_gate.tasks eval`) regenerate EVERY number in `RESULTS.md` from the stored ledgers, byte-identically** — the claim scoped exactly as rule 10 scopes it; every ₹ figure is a **median with IQR**, de-duplicated by `ledger_seq`, **never a sum**; every "0/N" ships its ceiling; **every table caption states its own cell size**; the pre-registered headline is reported **only if both arms clear the reach gate**, else published as CONFOUNDED; **if the run voids, spec §10.5's contingency set is what ships** and the VOID banner is at the top of both `RESULTS.md` and `README.md` |

⚠️ **GATE (spec §17): 18:00 — if one command does not regenerate every number, freeze features and
spend the rest of the day on that alone.**
**Reserved 2 Sep:** one hour for fix cycles. **After 2 Sep the fix reserve ends** — 3 and 4 September
are for the submission, not the build.

#### 3 SEPTEMBER — the artefacts *(spec §17 row 5)*

| # | Time-box | Chunk | Deps | Review | Done when |
|---|---|---|---|---|---|
| **C19** | 09:00–14:00 | **README + architecture + PROVENANCE final pass + the Agent-Ready conventions.** Results above the fold; **§2's merchant loss first, never the methodological critique**; prior art named — CaMeL, PRAMANA, `argus`, `AgentProof`, `HydraLoop`, `reserve-gate`, OCELOT; the honest negative; the attacker-strength figure with its **measured** x-axis; **§ "Verifying the pre-registration" carrying §6a.3 verbatim and §6a.4's honesty sentence**; the `(unreviewed)` explainer; the §7a statement of what session tokens do and do not prove; `AGENTS.md`, `docs/adr/`, `bench/` | C18 | **code** - ⚠️ **DOWNGRADED FROM `full` 2026-09-02 (rung 5; `INCIDENTS.md` INC-63; `QUESTIONS.md` Q-083).** The original entry read **full** and stands above. C19 writes prose and **publishes no computed number**. ⚠️ **BUT ONE VERIFICATION IN ITS done-when SURVIVES THE DOWNGRADE AND IS NAMED HERE SO IT IS NOT SKIPPED: *"a fresh session runs S6a.3's verification procedure start to finish from that clean clone and reproduces the published fingerprint"* - that is a reproduction check on the PRE-REGISTRATION, it is a PROCEDURE rather than a reimplementation, and it is REQUIRED under `code`.** | **the clean-clone test passes in a fresh directory, on the free tier, with no card attached**; ⚠️ **a fresh session runs §6a.3's verification procedure start to finish from that clean clone and reproduces the published fingerprint**; **no unsourced claim remains** — every third-party statement carries a URL and a date; `docs/reviews/OPEN_FINDINGS.md` is empty or every remaining item is explicitly accepted with a reason; ⚠️ **the clean-clone test EXECUTES ALL THREE bootstrap steps** — clone; venv + `pip install -e ".[dev]"`; the `vendor/MANIFEST.md` §2 fetch commands followed by `pip install -e vendor/tau2-bench` — **and the README prints all three beside the clone command.** Until then `CONTEXT.md` §20's first box is FALSE. (Q-010.) |
| **C20** | 14:00–20:00 | **The video.** The §18 shot list, its 0:35–1:25 RACE beat driven by C17's renderer. As many takes as it takes | C17, C18, C19 | **code** + **submission** - ⚠️ **THE `code` REVIEW IS FOLDED INTO C21's, 2026-09-02 (rung 1; `INCIDENTS.md` INC-61; `QUESTIONS.md` Q-083).** The original entry stands above; the fold is the change. **C21's review is `full` + `submission` and reads C20's output**, so the video is still adversarially reviewed - by the session that also checks the form paragraphs. C20 publishes **no number**. | every beat in spec §18 is present and in order; **the RACE says on screen that it is a replay of a stored hash-chained ledger, and names the seed and the pre-registered N**; the void banner and the ceiling are **spoken out loud**; the ladder's **n=5 and ±44 pp** are spoken out loud; it **ends on `git show prereg-v1`** with its commit hash and date; it is uploaded and an **unlisted** link plays for a logged-out viewer |

#### 4 SEPTEMBER — the submission *(spec §17 row 6)*

| # | Time-box | Chunk | Deps | Review | Done when |
|---|---|---|---|---|---|
| **C21** | 09:00–14:00 | ⚠️ **THE SUBMISSION PACK — the deliverable revision 1 left entirely unowned.** Write `docs/submission/FORM_ANSWERS.md` containing, verbatim and final: the project name; the **Project Objectives** paragraph (**opening on the merchant's loss, never on the methodological critique** — spec §21.3); the **Build Challenges & Technical Obstacles** paragraph in the **Event / Action / Expectation / Missing / Missed** format, sourced from **≥2 `INCIDENTS.md` entries of which at least one is dated after the first build commit**, carrying the §9 limitation sentence; the exact public repo URL; the exact video URL. Then **re-verify every perishable fact of spec §21.5** (incl. that the pre-registration gist still resolves and still reports its original `created_at`). Then run the **git-history secret scan** and commit its output. **Then flip the repository to public** | C19, C20 | **full** + **submission** | both paragraphs are **pasted into the live form's preview WITHOUT SUBMITTING and screenshotted into `docs/submission/`**; a **logged-out** browser loads the repo URL and plays the video; the history-scan output is committed; the repository is public; **≥2 `INCIDENTS.md` entries are dated after the first build commit**; ⚠️ **no payment method is attached to either provider account, RE-CONFIRMED on 4 September and recorded in `PROVENANCE.md` §1.5 with the new date** — it is the only claim in the frozen set that can go stale with NO file changing, and a card attached on 3 September would silently convert every subsequent 429 into a bill while this repository still read NONE ATTACHED |
| **SUBMIT** | by 18:00 IST | 🚩 **OPERATOR ACTION.** Paste the reviewed paragraphs, the repo URL and the video URL. Submit | **REVIEW_21 = PASS** | *gated on `REVIEW_21` = PASS; the reviewed artefact is what is pasted* | ⚠️ **The operator does not open the submission form until `REVIEW_21` is PASS.** The form is one-shot: *"no further changes or edits can be made after submitting."* **15:00 — no code changes.** The 5th is buffer, not plan |

### 12.2 Orphans closed, and the two deliberately dropped

Every row of `PROCESS_AUDIT.md` §3.1 now has an owner. Two are **deliberately dropped**, recorded
here rather than silently omitted:

| Dropped | Why | What ships instead |
|---|---|---|
| **R-Judge's Finance subset** (126 labelled money-movement trajectories) | spec §11.2 already calls it *"an upgrade if the days allow"*, and the days do not allow it — it is a fourth environment behind τ², the mock world and AgentDojo. **R-Judge also ships NO licence file of any kind** | It is **cited** in the README's prior art and **never vendored or redistributed**, per spec §11.3 |
| **`groq/compound` and `compound-mini` as extra ladder points** | spec §13.3.2 flags them as **agentic systems with built-in tooling, not raw models**. Adding them to a ladder whose x-axis is *measured model competence* would mix two different things on one axis | The ladder ships **four points** (L1, L2, L3, REF). The reason is printed on the figure |

**Carried forward at every chunk:** anything a review could not close, in
`docs/reviews/OPEN_FINDINGS.md` — appended by every review, closed explicitly with the SHA that
closed it.

---

## 13. What Razorpay is scoring, mapped to where this process produces it

Kept visible so no chunk drifts from the thing being judged. **Every claim in this table is checkable
in the repository, because this file ships publicly.**

| Rubric line | Where the process produces the evidence |
|---|---|
| **Problem taste** — *"did you pick something that actually matters"* | `CONTEXT.md` §2, written from Razorpay's own source code and their own documented semantics. The README leads with the merchant's loss (C19), never with the critique |
| **Build quality** — *"would you trust it"* | The review trail itself: `docs/reviews/` with **per-attempt PASS/FAIL files that are never overwritten**, committed independent reimplementations, ≥8 mutants per `full` chunk, an architect VERIFICATION block per chunk, an open-findings register — **and a deliberately seeded defect (§5.4) that tests the reviewer.** Plus a clean-clone test and `make eval` |
| **AI judgment** — *"and where you chose not to use one"* | **Four** named non-uses (`CONTEXT.md` §14) — the arm-4 kernel's money path, the scorer, the probe and void rule, and the world — **each asserted by its own named test** (C10), plus the measured gate latency that turns non-use #1 from an assertion into a number. *(Revision 1 said "three" while the spec said four, and only one of the four had a test.)* |
| **Failure recovery** — *read first* | `INCIDENTS.md`, open from commit one, **format fixed by hard rule 13** in Razorpay's own Event/Action/Missing/Missed shape, with `Diagnosis` and a `Fix`-with-SHA required. It carries the day-0 entries (attacker 0/20 → 16/20; the `destination` parameter that does not exist; 59% of escapes rejected by Razorpay itself; the duplicate-refund predicate that blocked legitimate instalments in 8/8 seeds; the "29 ms" figure found in no Razorpay source) — **and at least two entries dated after the first build commit**, because *"what broke while you were building this"* cannot honestly be answered with *"things that broke before I started"* |

| Their universal bar | Where |
|---|---|
| A measured number on a batch | RUN-3, RUN-4, C18 — 940 (or 840) episodes, every denominator printed |
| An honest negative | The void run published as void; the false-positive paired deltas; the four harm components reported separately; the **S2-vs-S2-amt** delta showing our own plausible invariant was wrong; the AgentDojo balance limitation; Branch B if CaMeL cannot run |
| Bounded, auditable action with stopping rules | C7 ledger, C10 probe and void rule, C9 gates — **and C17, which renders the log so a non-author can actually read it**, which is the part that was missing |
| Deliberate non-use of AI | Rule 8, **four tests** |

| Their own published doctrine (`ai-playbook` B.9) | Where — and whether it is enforceable or decorative |
|---|---|
| *"taking an exam it wrote and marked itself"* | **Enforceable.** Build ≠ review everywhere; the reviewer's Phase 1 is blind; **`gates/` and `scorer/` share no first-party module and a test asserts it** |
| *"a release gate that has never gone red is only decorative"* | **Enforceable, as of revision 2.** §5.4 plants a known-red case in C7 and ships the transcript either way; §11 requires an incident entry if eight chunks PASS first time. *(In revision 1 this line was decorative twice over: the spike's red was retrospective, and the review gate itself was exempt.)* |
| *"name the scorecard before implementation"* | **Enforceable.** Two tags, a frozen set that includes `config/`, `make check-prereg` inside both `make eval` and `make test`, an automatic FAIL for any `RESULTS.md` figure inconsistent with the tag — **and an external witness (§6a) without which the tag proves nothing** |
| *"do not let retries quietly shrink the denominator"* | **Enforceable.** Rule 11 quotes it verbatim; dropped episodes are counted, categorised and printed; persona 1's second check audits it; §9's partition invariant closes the gaps; **SWEEP-AUDIT-1 reconciles it the same night** |
| Outcome / Trajectory / Guardrails / **Quality / Efficiency** | Partly. `CONTEXT.md` §12.1's table covers Outcome, Trajectory and Guardrails. **Efficiency is filled by C18's per-model token table and §14's measured gate latency; Quality is filled by the benign solver's solve rate (C12), which is the closest honest analogue we have.** Stated here rather than claimed as a clean five-layer match |
| *"shadow mode → control → beat it → scale"* | Partly, and named as partial. **The five arms genuinely are the controls**, and arm 1 is the shadow baseline. There is **no separate observe-then-enforce artefact**, and this document does not claim one |

---

## 14. THE DEGRADATION LADDER

**Written before the first chunk, because a ladder written while behind schedule is not a ladder.**
It is itself rubric evidence — *stopping rules* — and it ships in the repository.

**When the schedule slips, cut in this order. Record every cut in `INCIDENTS.md` at the moment it is
made, with the time, the rung, and the reason. A cut item is never silently lost: it is named in
`RESULTS.md` and in the README as *not run*, with why.**

| Rung | Cut | Cost | Pre-declared? |
|---|---|---|---|
| **1** | **Collapse a `code`-review chunk into its neighbour's review.** C15's ladder harness reviews inside C18; C20's video reviews inside C21 | Two review slots ≈ 50 min. Loses the least evidence of anything here | ⚠️ **FIRED 2026-09-02 08:10 IST / 02:40 UTC** - `INC-61`, `Q-083`. Pre-declared: new, this document |
| **2** | **The L2 extended cell** stays at n=5 instead of 20 | The ladder's mid-point keeps its ±44 pp interval instead of narrowing | **NOT FIRED. RESERVED UNTIL C14** - it changes what is MEASURED, and after `prereg-v1` it cannot be changed at all. Pre-declared: **yes** — spec §13.3.3 |
| **3** | **C16 / AD-CMP, the AgentDojo comparator** — 80 episodes | Loses the second external environment. τ²-bench and the mock world remain, so **the external-answer-key claim survives intact** | ⚠️ **FIRED 2026-09-02 08:10 IST / 02:40 UTC - C16 IS NOT RUN** - `INC-62`, `Q-083`. Named as *not run*, with why, in `RESULTS.md` and the README. Pre-declared: new, this document |
| **4** | **T-FP 40 → 20 τ² tasks** | Halves the τ² false-positive sample; −6M tokens ≈ −3 h of Gemma lane time | **NOT FIRED. RESERVED UNTIL C14** - it changes what is MEASURED. Pre-declared: **yes** — spec §13.4, *"the one pre-declared further reduction"*. ⚠️ **Fire it BEFORE `prereg-v1` if at all possible**, because T-FP's task list is pre-registered in `PROTOCOL.md`. If it must fire after the tag, the block is published as **incomplete with its denominator**, never as a re-registration |
| **5** | **Downgrade C17's and C19's reviews from `full` to `code`** | Loses a reimplementation on two chunks that produce **no reported number**. Each downgrade is its own `INCIDENTS.md` entry | ⚠️ **FIRED 2026-09-02 08:10 IST / 02:40 UTC** - `INC-63`, `Q-083`. Pre-declared: new, this document |
| **6** | **C13 / CaMeL live run → Branch B citation** | The comparator ships as CaMeL's published **Table 2, Appendix B, `o3 High`, `banking`** with the one-line reason. ⚠️ **NOT Tables 5–7** (Appendix C, `Claude 3.5 Sonnet`, where CaMeL is *behind* on banking); **Table 7** stays §8.5.2's P2 citation (Q-058, Q-064) | **NOT FIRED. RESERVED UNTIL C14** - it changes what is MEASURED. ⚠️ C13 PASSED (`c13-pass`) on 2026-09-02, so the branch is RUN-1's to decide, not the ladder's. Pre-declared: **yes** — spec §8.5.1 |

⚠️ **WHAT C18 AND C19 MUST PUBLISH ABOUT EVERY CUT — the requirement, in the place those two
chunks will read it.** §14's rule is *"a cut item is never silently lost: it is named in
`RESULTS.md` and in the README as **not run**, with why."* As of **2026-09-02** that means, concretely:

| what | where | the words |
|---|---|---|
| **C16 / AD-CMP, 80 episodes** | `RESULTS.md` **and** `README.md` | **NOT RUN** — degradation rung 3, fired 2026-09-02 08:10 IST. The second external environment is lost; **τ²-bench remains, so the externally-authored-answer-key claim is intact.** `INCIDENTS.md` `INC-62` |
| **C15's and C20's `code` reviews** | `RESULTS.md` | **FOLDED** into C18's and C21's reviews — rung 1, `INC-61`. Neither publishes a number |
| **C17's and C19's review type** | `RESULTS.md` | **DOWNGRADED** `full` → `code` — rung 5, `INC-63`. Neither publishes a number |

⚠️ **AND THE ONE THAT IS EASIEST TO GET WRONG:** `vendor.agentdojo_sha` stays at its sentinel and
the loader **keeps raising**. **Do not report that as a defect, and do not edit `config/` to resolve
it** — `config/` is a pre-registration artefact (hard rule 9, §6a). **Report it as the visible
consequence of a published cut.** A reader who greps `agentdojo` must find the cut, not a mystery.

⚠️ **THIS IS NOT BOOKKEEPING.** It is the difference between honest scope reduction and
cherry-picking, in a submission whose entire thesis is that other people's numbers are unsound. **A
project that cuts a comparator and does not say so has done the thing it criticises.**

⚠️ **N IS NOT A RUNG, and the audit's suggestion that it should be is rejected.** After `prereg-v1`,
changing N is **amending a frozen artefact**, which §6 forbids outright. Before `prereg-v1`, N is
selected by the pilot's **measured tokens/episode** under the §13.4 decision rule, and never by
schedule pressure. **If the sweep cannot finish the pre-registered N, the episodes that did not run
are reported as an incomplete denominator — counted, categorised and printed (rule 11) — and the
number is published with its real n.** Quietly shrinking N to a number the schedule can reach is the
precise thing rule 11 and B.9 forbid.

**NEVER CUT, at any rung, for any reason:**

- **τ²-bench** — the external answer key; spec §21.4 says *"never dropped"*, and **only its breadth is
  staged** (the 20:00 rule on 30 Aug).
- **The competence probe and the void rule** — without them a "0 escapes" is unfalsifiable.
- **The freeze, both tags, and the external witness gist** — without the witness the freeze is
  self-asserted (§6a).
- **`INCIDENTS.md` and hard rule 13's format** — the answer Razorpay read first.
- **The counter-metric** — the benign solver and the paired FP delta. A project that publishes only
  what it blocked has published half a result.
- **The seeded-defect test (§5.4)** — the only evidence the review gate works.
- **The two form paragraphs and the git-history secret scan** (C21).

**Per-day slip triggers, decided now:**

| If, at… | …this is not done | Then |
|---|---|---|
| **30 Aug 20:00** | C5 is not driving τ² **both** directions | Ship the **34 must-not-write control only** tonight; add the 130 write tasks on 31 Aug (spec §17's staging rule). `INCIDENTS.md` entry immediately |
| **30 Aug 23:00** | C6 (attacker) is not reviewed | C6's review slips to 31 Aug 07:00; **31 Aug's C12 (benign solver) slips to 1 Sep 08:00** — still ahead of T-FP, which begins on 1 Sep. `INCIDENTS.md` entry |
| **31 Aug 18:00** | C10 or C11 is not PASSed | **Fire rung 1, then rung 3.** The freeze does not move: it is the one thing the whole project is staked on |
| **31 Aug 23:00** | The calibration has not started | The freeze slips to 1 Sep 02:00 and **the sweep starts late**, not the freeze early. **A pre-registration cut after the first scored episode is worthless**, so the freeze is never the thing that gives |
| **1 Sep 14:00** | The runner has not demonstrated a day-boundary resume | **Stop the sweep and fix it** (spec §17's own gate). A multi-day sweep without day-resume loses a day's episodes |
| **2 Sep 18:00** | One command does not regenerate every number | **Freeze features. The rest of the day is `make eval` and nothing else** (spec §17's own gate) |
| **3 Sep 20:00** | The video is not recorded | Record the shot list against **still frames and the C17 renderer** rather than dropping beats. Every §18 beat ships, even at lower polish |

---

## 15. RESIDUAL RISK — what this process still cannot close, stated openly

A process document that implies enforcement it does not have is doing the same thing this project
criticises. These are the holes that remain **after** every fix in revision 2. They are listed here,
and the load-bearing ones are repeated in the README.

1. **Session identity cannot be proven.** §7a's tokens make reuse **visible** and make the claim
   falsifiable; they do not make a build session reviewing its own work impossible. There is one
   human here and no second party. **This is an honour system with an audit trail, and calling it
   anything else would be a false claim.**
2. **A tag cut after the fact, on backdated commits, is undetectable from inside the repository.**
   §6a's external witness closes this **going forward** — from the gist's `created_at` onward, the
   frozen set is pinned by a server-assigned timestamp nobody here controls. It does **not** prove
   that no earlier run happened. §6a.4 says exactly that, in the README, unprompted.
3. **The escape number has no external ground truth.** It is adversarial *search*, not adjudication
   by the world, and it is a **lower bound on what escapes, never an upper bound**. This is the
   project's own stated limitation (`CONTEXT.md` §19) and no process rule changes it — which is why
   the false-positive tasks, the answer key and the competence control are all someone else's.
4. **The architect can be lied to by a relayed report.** `docs/sessions/` makes the original
   checkable against the relay, and the architect's `ARCHITECT_CHECK` recomputes the numbers — but
   the operator commits both. **Mitigated, not closed.**
5. **`INCIDENTS.md` is written by the person whose failures it records**, and the pressure runs in
   both directions: under-reporting saves a fix session the schedule cannot easily afford, and
   dramatising reads well to a panel that reads it first. Rule 13's `Diagnosis` and `Fix`-with-SHA
   fields make an invented incident expensive (it has no commit) and an omitted one visible (a FAIL
   in `STATUS.md`'s history column with no matching entry). **Mitigated, not closed.**
6. **`ots verify` needs a Bitcoin node.** The OpenTimestamps receipt is a genuine trustless anchor
   that **most judges cannot check**. That is why the gist is primary and OTS is secondary, and why
   the README says which is which.
7. **Whether a gist's `created_at` survives every edit path is undocumented.** GitHub's REST docs
   define `created_at`, `updated_at` and a `history[]` with server-assigned `version` and
   `committed_at`, and the create endpoint accepts no date field `[VERIFIED, 2026-08-30]` — but they
   are **silent** on whether `created_at` can move. §6a.3 therefore reads the **oldest history
   entry**, which is the conservative choice. **Unverified beyond that, and said so.**
8. **The throughput assumption is an estimate.** §12.0's plan assumes the operator can sustain a
   build-plus-review cycle in roughly 25–45 minutes across 44 sessions in six days. **That number has
   never been measured.** The fix-session reserve and the §14 ladder exist because it may be wrong;
   if it is wrong by more than the ladder absorbs, the ladder is fired further and every cut is
   recorded.

---

```
The process is the product that survives the project —
and on this one, the process is also the argument.
A gate that has never gone red is only decorative; so is a freeze nobody outside can check.
```
