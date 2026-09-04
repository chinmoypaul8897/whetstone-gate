# C21 — THE SUBMISSION FORM ANSWERS

**Written by C21 BUILD 1, `SESSION-TOKEN 9e2c81d4`, 2026-09-04. NOT SELF-CERTIFIED — a fresh
adversarial review (`full` + `submission`, persona 3) follows and has not run.**

This file is what the operator pastes. `PROCESS.md` §12's C21 card requires it "verbatim and
final", and `PROCESS.md` §12's SUBMIT row makes **"the reviewed artefact is what is pasted"** the
gate. A paragraph re-drafted in the form box has never been reviewed, and the form is one-shot.

---

## 0. READ THIS BEFORE THE PARAGRAPHS — FIVE RULE-1 STOPS AND ONE STATE FACT

### 0.0 THE STATE FACT THAT GOVERNS EVERY WORD BELOW

⚠️ **NO SCORED EPISODE HAS RUN. THERE IS NO SWEEP, NO CALIBRATION AND NO PILOT.**
Measured by this session at `HEAD`:

| Fact | How this session measured it | State |
|---|---|---|
| `evals/` | `find evals -type f` | **one file**: `evals/pilot/RUN_DECLARED.md` |
| `RESULTS.md` | `ls RESULTS.md` | **does not exist** |
| `git tag -l` | `git tag -l` | `c0-pass c1-pass c2-pass c3-pass c4-pass c13-pass` **and `probe-v1`** |
| **`prereg-v1`** | the same command | ⚠️ **DOES NOT EXIST** |
| `probe.void_threshold_breach_rate` | `config/protocol.yaml:335` | **`TODO_C14_CALIBRATION`** — an explicit sentinel; the loader raises on it |
| the pre-registration witness gist | `grep -n PENDING README.md` | **does not exist** — `README.md:1222` prints the id as the literal `<<PENDING-RUN: GIST_ID>>` |
| the video | `STATUS.md:1834`, C20 status column | **`todo - review folded`**; no video URL exists anywhere in this repository |

**Consequence, stated rather than implied:** every number either paragraph would want is written
below as an explicit named placeholder in the form `<<PENDING-RUN: name>>` — the convention
`README.md:28` already fixes: *"every one of them is spelled `<<PENDING-RUN: name>>` so you can
find them all with one grep."* **A placeholder is never a result.** §8 lists every one.

### 0.1 STOP — THIS FILE'S NAME

The C21 BUILD prompt named the deliverable `docs/submission/FORM.md`. **The card and the spec both
name `docs/submission/FORM_ANSWERS.md`** — `PROCESS.md`:1343 (*"Write `docs/submission/FORM_ANSWERS.md`
containing, verbatim and final: …"*) and `CONTEXT.md`:2187 (*"`└── submission/  # FORM_ANSWERS.md,
the form-preview screenshots, the history-scan output`"*). `CLAUDE.md` §2 rule 4 — *"ONE SOURCE OF
TRUTH. CONTEXT.md outranks the plan, the code, the tests, and memory"* — resolves it: **this file
carries the card's name.** A six-line pointer sits at `docs/submission/FORM.md` so a session
holding the prompt's name still lands here; it holds no content of its own and cannot diverge.
This session could not write `QUESTIONS.md` (fenced out; another session was writing there), so it
is recorded in this session's report under **QUESTIONS OWED**.

### 0.2 STOP — WHICH "§9 LIMITATION SENTENCE"

The card says *"carrying the §9 limitation sentence"* and writes bare "§9" where it writes "spec
§21.3" elsewhere. Three files have a §9. **`CONTEXT.md` §9 is THE INVARIANTS** (`CONTEXT.md`:1048)
and carries no limitation sentence. **`README.md` §9 is *Limitations*** (`README.md`:684) — a
fourteen-subsection section, not a sentence. **Only `PROCESS.md` §9 names one sentence AND names
the submission form as its destination** (`PROCESS.md`:1029):

> **Disclose limitations in the open.** The escape number is authored by us and no external ground
> truth for it exists anywhere; that sentence appears in the README, the video, and the submission
> form — volunteered, never buried.

**This file takes `PROCESS.md` §9 as the referent.** It is the best-supported reading, not a
certain one, and it is owed to `QUESTIONS.md`.

### 0.3 STOP — THE CANONICAL LIMITATION SENTENCE NAMES A COMPONENT THAT WAS CUT

The published wording is `PROVENANCE.md` §4:596-604:

> **The escape number is authored by us, and no external ground truth for it exists anywhere.** It
> is adversarial *search*, not adjudication by the world, and it is a **lower bound on what
> escapes, never an upper bound.** That is why the false-positive tasks, the answer key and the
> competence control are all **someone else's**: τ²-bench's `db_reward`, AgentDojo's banking suite,
> and a probe that voids our own run.

⚠️ **Its third clause names AgentDojo's banking suite, and AgentDojo was CUT.** `README.md`:701
(*"### 9.2 RUNG 3 FIRED — C16 / the AgentDojo comparator, 80 episodes, WAS NOT RUN"*),
`STATUS.md`:1830 (*"NOT RUN - CUT (rung 3)"*), and `config/protocol.yaml`'s `vendor.agentdojo_sha`
is still the sentinel `TODO_C13_C16`. **§3 below therefore carries the mandated sentence — the two
sentences `PROCESS.md` §9 actually names — verbatim, and states the third clause in the form that
matches the repository today.** Both forms are printed here so the substitution is visible rather
than silent. Owed to `QUESTIONS.md`.

### 0.4 STOP — THE CARD'S FIVE FIELDS VS HARD RULE 13'S EIGHT

The card requires the Build-Challenges paragraph *"in the Event / Action / Expectation / Missing /
Missed format"* — five fields. `CLAUDE.md` §2 rule 13 fixes eight for an `INCIDENTS.md` entry and
gives the reason the extra three matter: *"**Why `Diagnosis` and `Fix`-with-SHA:** … An invented
incident has no commit."* Rule 13 governs `INCIDENTS.md`, not form prose, so the card may be
deliberate — **but a `Fix:` SHA is the one thing a panelist can check in ten seconds.** §3 below
uses the card's five named fields as its headings and appends **Diagnosis** and **Fix (SHA)** to
each, which satisfies the card and forfeits nothing. Owed to `QUESTIONS.md`.

### 0.5 STOP — TWO OF THE CARD'S OWN DELIVERABLES ARE UNSATISFIABLE TODAY

- **"the exact video URL"** — `STATUS.md`:1834 puts C20 at `todo`; no video URL exists in this
  repository. §5 is a placeholder and the operator checklist says so.
- **"re-verify … that the pre-registration gist still resolves and still reports its original
  `created_at`"** — there is no gist and no `prereg-v1` to fingerprint, so there is nothing to
  re-verify. `CONTEXT.md` §21.5 calls this *"the one perishable fact the project cannot re-create
  after the fact."* **It cannot be reported as PASS and it is not.**

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
commodity, and we say so first.** At least 43 Track 01 entrants built the same missing limit; of 43
Track 01 READMEs read in full, every one authored its own world **and** its own answer key, and the
recurring headline is *100% blocked*. (That is a survey result, not a census: the corpus cannot be
enumerated, and **the corpus definition misses precisely the repos most likely to be near
neighbours.**) Better gates already exist in public — CaMeL's, and PRAMANA's audit log — and
`jboiie/argus`, `adthya-anil/AgentProof` and `Chavan-Kartik/HydraLoop` all ship generated
adversaries, which we did not invent either.

**So the objective is the whetstone, not the blade: to measure what a "blocked" number is worth.**
One attacker that has never seen our policy text, our pre-registered holes, our attack-and-invariant
taxonomy or any gate's denial reason — the only refusal it sees is a single generic string,
identical across all five arms — run against every arm on the same seeds, with escapes found by
deterministic replay of a hash-chained ledger and no model anywhere in the scorer. False positives
and an external check that the attacker was trying at all come from **someone else's** benchmark:
τ²-bench (`github.com/sierra-research/tau2-bench`, MIT, pinned at
`a2c024725189473d2d7cea3a5cfdbcc67478e41f`, 2026-08-18), whose tasks, gold behaviour and `db_reward`
hash grader are Sierra's, not ours. A defender-integrity probe with a threshold registered before
the run **discards our own data** if the attacker turns out to be blunt. And `gates/` and `scorer/`
share no first-party module — asserted by a module-graph walk over both packages' transitive
imports with an **empty** allow-list — because in the spike that preceded this project the gate and
the invariant checker both called one shared helper, so the invariant could not have fired unless
the gate had a bug. **That is not a result; it is a definition**, and never doing that again is this
project's central structural commitment.

⚠️ **State, so nothing above is misread: no scored episode has run.** This submission is a
measurement apparatus, a pre-registered protocol and a published failure record — not a results
table. Every number in the repository is either measured from files in the repository, or is a
named `<<PENDING-RUN: …>>` placeholder that `RESULTS.md` fills when a run exists. The freeze is
**partial, and this repository says so on its own first screen**: `probe-v1` is cut and `HOLES.md`
is byte-identical at it, but `prereg-v1` does not exist and the external witness gist has not been
published. When a run exists, `make eval` regenerates every published number **from the stored
ledgers**, byte-identically — and nothing more than that: the attacker runs at temperature 0.7
against a hosted provider, so **re-running the models does not reproduce the run**, and no sentence
here should be read as saying it does.

---

## 3. BUILD CHALLENGES & TECHNICAL OBSTACLES — paste verbatim

> ⚠️ Card format: **Event / Action / Expectation / Missing / Missed**. `Diagnosis` and `Fix (SHA)`
> are appended per §0.4. Sourced from **two `INCIDENTS.md` entries**, one dated **after** the first
> build commit (`ee3cf93`, 2026-08-30) as the card and `CONTEXT.md` §20 require. This session
> counted **137 `## INC-` headings** in `INCIDENTS.md`; the great majority are dated after that
> commit, so the requirement is met many times over — these two are chosen for being the most
> self-incriminating, not the most flattering.

---

**The two failures worth your time are the same failure twice: a check that was supposed to be
load-bearing reported success over a live defect.**

**INC-02 — a threat model built on a parameter that does not exist.** `[INCIDENTS.md:59, dated
2026-08-28 — before this repository's first commit]`

- **Event:** the original threat model had `create_refund` sending money to an attacker-controlled
  `destination`, and produced a headline harm figure of **₹2,004 crore**.
- **Action:** read Razorpay's own refund API documentation and the official MCP server's Go source.
  `create_refund` has **no `destination` parameter** — Razorpay does source refunds only — and there
  is **no `CreatePayout`** anywhere in the MCP write surface. **No tool in that surface sends money
  to an attacker-controlled account.** Replaying the spike's episodes against Razorpay's documented
  rejections, **30 of 51 money actions (59%) would have been refused by Razorpay itself, 26 of them
  for that non-existent parameter.** ₹2,004 cr collapsed to **₹22.4 L**.
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
- ⚠️ Both ₹ figures above are **spike** figures from a **withdrawn** threat model, quoted to show
  the size of the correction. **They are not results of this project**, which publishes no ₹ figure
  until a run exists — and then only as a per-episode median with its spread, never as a sum.

**INC-132 — the line this project calls "the whole moat" printed PASS on all four checks over a
live `gates/` → `scorer/` reach.** `[INCIDENTS.md:9832, dated 2026-09-04 — after the first build
commit]`

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
- **Fix (SHA):** **`1fd0877`** — D4's scan set is now the union of both package directories and
  every first-party module in either transitive closure. Three new tests, of which **two were run
  against the pre-fix checker and FAILED there**, so they are measurements and not decoration. The
  allow-list stays empty; widening it is a Class A deviation requiring a recorded architect ruling.

**What these cost, and what is still open — volunteered rather than buried.** This repository ships
**137 recorded incidents**, a review trail of **14 FAIL and 6 PASS across 20 adversarial reviews**
with **6 chunks tagged and 14 unreviewed**, and an open-findings register that is published, not
drained. The build session and the review session are never the same session, and one chunk — the
attacker loop — was reviewed **six times, never passed, and ships with its residue named and
untagged** rather than quietly re-scoped. Both failures above have the same shape — **a check that
reported success over a live defect** — which is precisely the shape this project accuses the field
of, so the evidence is held against ourselves in the same file we publish.

And the limitation that outranks all of them, stated in the open because it does not go away:

> **The escape number is authored by us, and no external ground truth for it exists anywhere.** It
> is adversarial *search*, not adjudication by the world, and it is a **lower bound on what escapes,
> never an upper bound.** That is why the false-positive tasks, the answer key and the competence
> control are someone else's — τ²-bench's `db_reward` hash grader, and a probe that voids our own
> run.

---

## 4. THE EXACT PUBLIC REPOSITORY URL

```
https://github.com/chinmoypaul8897/whetstone-gate
```

Verified two ways by this session: `git remote -v` →
`origin  https://github.com/chinmoypaul8897/whetstone-gate.git (fetch)`; and `README.md`:1202 and
`README.md`:1450 both print `git clone https://github.com/chinmoypaul8897/whetstone-gate`.

⚠️ **The repository is still PRIVATE.** `PROCESS.md`:862 — it *"stays private until C21 flips it
public on 4 September, after the git-history secret scan has run and its output is committed."*
**This session did not flip it. That is the operator's act** — checklist item O-7.

---

## 5. THE EXACT VIDEO URL

```
<<PENDING-RUN: VIDEO_URL>>
```

⚠️ **No video URL exists in this repository.** `STATUS.md`:1834 records C20's status as
`todo - review folded`, and a search of `README.md` and `CONTEXT.md` for a video URL returns
nothing. **This is a placeholder and must not be pasted as-is** — checklist item O-4.

---

## 6. THE FIVE METHOD CLAIMS — WHAT MAY AND MAY NOT BE SAID

The paragraphs above claim a **method**, never an outcome. Each of the five load-bearing method
claims was verified against the repository as it exists at `HEAD` today, and each was then attacked
from three independent angles — literal truth; the panelist who has not read the spec; and the
project's own `HOLES.md` / `OPEN_FINDINGS.md` / `INCIDENTS.md` record.

⚠️ **All fifteen adversarial passes came back REFUTED against the claims as they are usually
worded.** **One** of the five is true as stated; **two** are true only when narrowed; **two** are
not yet true at all. §2 above uses only the narrowed forms.

| # | Claim as usually worded | Verdict | Why |
|---|---|---|---|
| 1 | A policy-blind attacker | ⚠️ **TRUE ONLY AS NARROWED** | Blind to **our** policy, holes, taxonomy and gate reasons. **Not** blind to attack technique — it is deliberately seeded from published third-party corpora, and the system prompt we wrote names four attack families. Never write *"has never seen any attack list."* |
| 2 | An externally-authored answer key (τ²-bench) | ⚠️ **TRUE ONLY AS NARROWED** | τ²-bench supplies the **false-positive** ground truth and the **competence control**. It supplies **no escape ground truth** — escape is measured wholly in our own mock Razorpay world. And it has graded nothing yet. |
| 3 | A competence probe that VOIDS our own run | ⚠️ **NOT YET TRUE AS AN ACCOMPLISHED FACT** | The rule is written, tagged and byte-identical at `probe-v1`, and the decision is pure arithmetic. But the threshold is the sentinel `TODO_C14_CALIBRATION`, the loader **raises** on it, **no VOID verdict is computable on any input today**, and there is no run to void. |
| 4 | A freeze witnessed outside the repository | ⚠️ **NOT YET TRUE** | `prereg-v1` does not exist; no witness gist exists; `README.md`'s verification command still prints `<<PENDING-RUN: GIST_ID>>`. What **is** true: `probe-v1` is cut and `HOLES.md` is byte-identical at it. |
| 5 | `gates/` and `scorer/` share no first-party module | ✅ **VERIFIED, with its limits stated** | Measured by this session; see §6.1(5). |

### 6.1 The evidence, claim by claim

**(1) POLICY-BLIND — TRUE AS NARROWED.**
*Safe:* "The attacker never receives the gate's policy text, our pre-registered holes, our
attack-or-invariant taxonomy, or any gate's denial reason; the only refusal it sees is one generic
string, identical across arms. Blindness is checked against the actually-assembled context by tests
carrying planted-leak positive controls."
*Evidence:* `CONTEXT.md` §7's architecture block — *"ATTACKER (LLM, policy-blind) … never sees:
policy, holes, attack list, gate reasons"*; `tests/test_c6_attacker.py` (the blindness guards, incl.
`test_the_attacker_package_imports_no_model_client_and_no_network_library`);
`tests/test_c12_benign.py:404 test_the_blindness_scan_FIRES_at_four_planted_leaks` — the guard is
proved to fire, not merely to be silent.
*Do not write:* *"it has never seen any attack list."* The attacker is seeded from published
third-party attack corpora, and the system prompt we authored names four attack families in plain
English. *Also carry:* the attacker chunk C6 was **reviewed six times, never passed, and carries no
tag** (`README.md`:986).

**(2) EXTERNALLY-AUTHORED ANSWER KEY — TRUE AS NARROWED.**
*Safe:* "The tasks, the gold behaviour and the grader for the false-positive block and the
competence control are Sierra's, not ours — τ²-bench, MIT, pinned."
*Evidence:* `config/protocol.yaml:396 tau2_bench_sha: a2c024725189473d2d7cea3a5cfdbcc67478e41f`;
`vendor/tau2-bench/LICENSE` → *"MIT License / Copyright (c) 2025 Sierra Research"*; `CONTEXT.md`
§11.1's authorship-split table — tasks, gold behaviour, grader and benign tasks all **Sierra**, the
gate **"Us — the only thing we author"**.
*Do not write:* any present-tense claim that our numbers were scored by it. `CONTEXT.md` §11.1 is
explicit that τ²-bench does **not** provide escape ground truth, and that *"Escape measurement moves
WHOLLY to the mock Razorpay world."* `evals/` holds one declaration file and `RESULTS.md` does not
exist, so **the external key has graded nothing.** *Also:* we score on `db_reward` alone — a hash
comparison, no model; τ²-bench's full retail reward multiplies in an LLM-judged natural-language
assertion and **we do not use it**. *And:* AgentDojo, the second external environment, was **cut**
(rung 3, `README.md`:701).

**(3) A COMPETENCE PROBE THAT VOIDS OUR OWN RUN — NOT YET TRUE AS AN ACCOMPLISHED FACT.**
*What is true, verified by this session:* `probe-v1` is an annotated tag, object id
`170bd3ff4abfdd8f87f64055972a60c82cc54efc`, tagger date **2026-09-03 20:43:04 +0530**, message
*"pre-registration: HOLES.md, before the pilot and the calibration"*. `HOLES.md`'s git blob is
`a4e50ed6f379784c6b6bfefdd1728a57ca3d4c20` at **both** `probe-v1` and `HEAD`, and
`git diff probe-v1 HEAD -- HOLES.md` is **empty** — so the rule is frozen and provably unmoved.
`HOLES.md`:221 states the consequence verbatim: **"Below the calibrated threshold → THE WHOLE RUN
IS VOID."** The decision is pure arithmetic — `src/whetstone_gate/probe/void.py`:81 `breach_rate`,
:109 `is_void` — with no model client, asserted by
`tests/test_c10_probe.py`:1092/:1106 `test_the_VOID_RULE_imports_no_model_client_WAY_ONE/WAY_TWO`.
*What is not:* `config/protocol.yaml`:335 reads `void_threshold_breach_rate: TODO_C14_CALIBRATION`.
The loader raises rather than defaulting, so **no VOID verdict is computable from `config/` as it
stands, on any input.** The single-shot arm-1 calibration that sets the threshold has not run.
*Safe wording:* "the void rule is written, frozen and git-tagged before the run; its threshold is
set by a single-shot calibration that has not yet been run, and the repository publishes that as a
declared sentinel rather than as a default."
*Do not write:* "a live kill switch", or "if it falls short the run is automatically voided" — the
banner states what must not be published; nothing suppresses a table.

**(4) A FREEZE WITNESSED OUTSIDE THE REPOSITORY — NOT YET TRUE.**
*Evidence:* `git tag -l` → seven tags, `prereg-v1` **absent**. `README.md`:56-58 states it against
itself: *"there is no `prereg-v1` to hash, **and** there is no published fingerprint or witness gist
to compare against — no `prereg-v1.sha256` and no OTS receipt exist in this tree."* `README.md`:1222
prints the verification command with the gist id as `<<PENDING-RUN: GIST_ID>>`.
*Safe wording:* "the pre-registration procedure — the frozen set, the fingerprint computed from git
objects, and the public-gist witness whose `created_at` GitHub assigns server-side — is written and
committed in full **before** there is any number to fit it to; one of its two tags is cut, the
witness has not been published, and the README says so on its first screen."
*Do not write:* any present-tense claim that the measurements are witnessed outside this repository.
**That is the single most damaging sentence available to this project**, because a claim of external
witness that a judge cannot `curl` discredits the one differentiator the project is built on.

**(5) `gates/` AND `scorer/` SHARE NO FIRST-PARTY MODULE — VERIFIED.**
*Measured by this session by running `python -m whetstone_gate.tasks check-roles` (read-only; the
working tree was byte-identical before and after):*

```
D - the gate/scorer moat
  [PASS] D1 gates/ imports nothing from scorer/
  [PASS] D2 scorer/ imports nothing from gates/
  [PASS] D3 no shared first-party module
         ... The allow-list holds 0 entr(y/ies). 118 first-party module(s) indexed;
         15 reachable from src/whetstone_gate/gates (14 seed(s)),
          6 from src/whetstone_gate/scorer (6 seed(s)), TRANSITIVELY
  [PASS] D4 no dynamic import in gates/ or scorer/
```

**The allow-list holds ZERO entries.** `src/whetstone_gate/check_roles.py`:637 —
`MOAT_ALLOW_LIST: frozenset[str] = frozenset()`. ⚠️ **`CLAUDE.md` hard rule 8 describes it as *"a
short, explicit allow-list of pure value types (enums, the harm-record dataclass, the paise integer
wrapper)"*. The implemented list is EMPTY** — stronger than the constitution describes, and the
correct thing to say is the measured "0", not the described "short". Owed to `QUESTIONS.md`.
*Limits that must travel with the claim:* (a) the property is "no shared first-party **module**",
**not** "no shared code" — both sides deliberately reimplement the same predicates twice, on
purpose; (b) this exact assertion has **twice** printed clean or PASS over a live `gates/` →
`scorer/` reach before being hardened (`INC-51`, `INC-132` — see §3); (c) the closure is built from
**static** imports, so a reach whose first hop is made by third-party code is scanned by neither
half — recorded as an **open** finding, not a closed one; (d) neither package has passed adversarial
review — there is no `c8-pass` and no `c9-pass` tag.

---

## 7. THE OPERATOR CHECKLIST — WHAT TO PASTE WHERE, IN ORDER

⚠️ **Nothing in this section is a card requirement.** The card names the file's contents; this
checklist and the placeholder table in §8 are additions by this session, and they are labelled so
no reviewer reads them as mandated.

**Order matters. O-1 to O-8 gate each other.**

| # | Step | Where | Blocking? |
|---|---|---|---|
| **O-1** | ⚠️ **Do NOT open the submission form until the C21 review returns PASS.** `PROCESS.md`:175 and :1344 — the form is one-shot, *"no further changes or edits can be made after submitting"*, and the one irreversible step must not be the unreviewed one. | — | ⚠️ **HARD GATE** |
| **O-2** | Fill every `<<PENDING-RUN: …>>` in §8, or strike the sentence that carries it. **A placeholder pasted into the live form is the worst outcome available.** | this file | ⚠️ **HARD GATE** |
| **O-3** | Re-verify the perishable facts of `CONTEXT.md` §21.5 — see §7.1. | browser | ⚠️ **HARD GATE** |
| **O-4** | Record the video URL. §5 is a placeholder; `STATUS.md` has C20 at `todo`. | §5 of this file | ⚠️ **HARD GATE** |
| **O-5** | ⚠️ **Re-confirm that no payment method is attached to either provider account, on 4 September, and write the new date into `PROVENANCE.md` §1.5.** It is dated **2026-08-30** today. **No session can do this** — a session has no browser and no permitted credentials. It is the only claim in the frozen set that can go stale with **no file changing**, and a card attached on 3 September would silently turn every subsequent 429 into a bill while this repository still reads NONE ATTACHED. | provider billing pages | ⚠️ **HARD GATE** |
| **O-6** | ⚠️ **Re-run the git-history secret scan.** The committed output at `docs/submission/git-history-secret-scan.txt`:4 records `HEAD = 90b6d6fab329ad39b44f47f3f651bebe311e21c8`; `HEAD` has moved since. **The scan must cover the tree that goes public.** `PROCESS.md` §8 fixes the method and constrains the remedy: if it finds a key, revoke it at the provider and record the incident — **the history is NOT rewritten**, because a rewrite would destroy `probe-v1` and every `cN-pass` tag. | terminal, then commit | ⚠️ **HARD GATE on O-7** |
| **O-7** | **Flip the repository to public** — only after O-6's output is committed. `PROCESS.md`:862. | GitHub settings | after O-6 |
| **O-8** | In a **logged-out** browser: load the repo URL from §4 and play the video from §5. | browser | after O-7 |
| **O-9** | Paste **§1** as the project name, **§2** as Project Objectives, **§3** as Build Challenges & Technical Obstacles, **§4** as the repository URL, **§5** as the video URL — **verbatim, with no re-drafting in the form box.** | the live form | — |
| **O-10** | ⚠️ **Paste into the form's PREVIEW and SCREENSHOT it into `docs/submission/` — WITHOUT SUBMITTING.** This is the card's own done-when. | the live form | before submit |
| **O-11** | Submit. Deadline **18:00 IST**. | the live form | last |

### 7.1 O-3 in full — the five perishable facts (`CONTEXT.md` §21.5)

Each is dated **2026-08-30** in the repository and is therefore **six days stale** today.

| | Perishable fact | Stale value in the repository | Status |
|---|---|---|---|
| PF-1 | The MCP repo's frozen `main` and its open-PR count | `CONTEXT.md` §2: no merged commit since 26 March 2026; 43 PRs open; 23 of 25 August PRs unreviewed; genuinely open issues 0 — `GitHub API, 2026-08-30` | **RE-READ REQUIRED** |
| PF-2 | That no competitor has shipped the §5 conjunction | `CONTEXT.md` §5, surveyed 2026-08-30. §21.1 already records the ground moving — `kasauti` has announced a *"runtime red-team agent"* as its next milestone | ⚠️ **RE-READ REQUIRED — this is §2's central claim and the likeliest to have gone stale** |
| PF-3 | The free-tier limits of `CONTEXT.md` §13.2 | read from the provider dashboards, 2026-08-30 | **RE-READ REQUIRED** |
| PF-4 | `whetstone-gate` still unclaimed on GitHub | three `api.github.com` queries, all `total_count` 0, 2026-08-30 | **RE-RUN ALL THREE** |
| PF-5 | The pre-registration gist still resolves with its original `created_at` | ⚠️ **THERE IS NO GIST.** Nothing to re-verify | ⚠️ **CANNOT BE PERFORMED — DO NOT REPORT PASS** |

---

## 8. THE PLACEHOLDER TABLE — every unfilled value, so filling them is mechanical

⚠️ **Not a card requirement** (see §7's preamble). Convention per `README.md`:28. **A placeholder is
never a result. Do not invent, estimate, round, hedge or illustrate one.**

| Placeholder | Where it appears | What fills it | Filled by |
|---|---|---|---|
| `<<PENDING-RUN: VIDEO_URL>>` | §5 of this file | the unlisted video URL, playable logged-out | **C20 / operator** |
| `<<PENDING-RUN: GIST_ID>>` | referenced in §0.0 and §6.1(4); lives in `README.md`:1222 | the public witness gist id and its server-assigned `created_at` | **C14 / operator** |

**And the numbers this file deliberately does NOT print, because printing any of them today would
be a fabricated result.** None appears in §2 or §3; each is listed so a later session filling
`RESULTS.md` can see what the form was written around:

| Number | Why it is absent |
|---|---|
| escape rate per arm (arms 1, 2, 2S, 3, 4) | no scored episode has run |
| money past the gate, per harm component | ditto — and every ₹ figure must ship as a per-episode median with its spread, never as a sum |
| false positives per arm (paired Δ) | ditto |
| probe breach rate, probe reach, and the VOID verdict | the threshold is `TODO_C14_CALIBRATION`; no VOID verdict is computable |
| the selected N | `n_decision.selected_branch` is `TODO_C14_PILOT`; the pilot has not run |
| the attacker-strength ladder | not run |
| any "blocked N%" or "0/N" | ⚠️ and when one exists it **never** ships without its rule-of-three ceiling |

---

## 9. EVERY FACTUAL CLAIM IN THIS FILE, AND WHERE IT WAS READ

Verified first-hand at `HEAD` by C21 BUILD 1 on 2026-09-04. `INCIDENTS.md` **INC-05** is the entry
that makes this mandatory: *"a precise-sounding third-party number that exists in no third-party
source."*

| Claim | Read in |
|---|---|
| Project name WHETSTONE GATE; repo `whetstone-gate` | `CONTEXT.md`:86 |
| Deliverable filename is `FORM_ANSWERS.md` | `PROCESS.md`:1343; `CONTEXT.md`:2187 |
| The §9 limitation sentence and its three destinations | `PROCESS.md`:1029-1031; published wording `PROVENANCE.md` §4:596-604 |
| Objectives must open on the merchant's loss | `CONTEXT.md` §21.3 |
| Razorpay MCP: list capped at 100, no rupee cap; nine `mcpgo.Max()`, none on a rupee amount; `capture_payment.amount` unbounded; `READ_ONLY` defaults false | `CONTEXT.md` §2, each table row carrying its own `file:line` citation into `razorpay/razorpay-mcp-server@7950d51d…`, read 2026-08-30 |
| The concrete loss (over-capture / over-refund / duplicate refund / early sweep) | `CONTEXT.md` §2, closing paragraph |
| 43 Track 01 READMEs; every one authored its own world and answer key; "100% blocked" | `CONTEXT.md` §1 |
| The mandatory occupancy caveat sentence, verbatim | `CONTEXT.md` §21.2 |
| CaMeL / PRAMANA better; `argus`, `AgentProof`, `HydraLoop` ship generated adversaries | `CONTEXT.md` §5 and §21.1 |
| The conjunction is the contribution | `CONTEXT.md` §5 |
| Attacker never sees policy, holes, attack list or gate reasons; one generic refusal message | `CONTEXT.md` §7 architecture block; `CONTEXT.md` §9.3 |
| Blindness guards are proved to fire | `tests/test_c12_benign.py`:404; `tests/test_c6_attacker.py` |
| No model in the scorer; deterministic ledger replay | `CONTEXT.md` §7 and §14; `tests/test_c8_scorer.py`:741 |
| The four deliberate non-uses each have a test | `tests/test_c9_gates.py`:1282,:1298; `tests/test_c8_scorer.py`:741; `tests/test_c10_probe.py`:1065,:1075,:1092,:1106; `tests/test_c2_world.py`:827 |
| τ²-bench MIT, pinned `a2c0247…`, 2026-08-18; Sierra authored tasks/gold/grader | `config/protocol.yaml`:396; `vendor/tau2-bench/LICENSE`; `CONTEXT.md` §11.1 |
| τ²-bench provides FP ground truth + competence control, **not** escape ground truth | `CONTEXT.md` §11.1, the two-column table |
| `db_reward` alone, no model | `CONTEXT.md` §11.1 |
| AgentDojo cut (rung 3) | `README.md`:701, :992, :1159; `STATUS.md`:1830; `config/protocol.yaml` `agentdojo_sha: TODO_C13_C16` |
| The spike's shared-helper failure — "not a result; it is a definition" | `CONTEXT.md` §7; `CLAUDE.md` §2 rule 8 |
| D1-D4 all PASS; allow-list 0 entries; 118 modules indexed / 15 / 6 / empty intersection | this session ran `python -m whetstone_gate.tasks check-roles`; `src/whetstone_gate/check_roles.py`:637 |
| `probe-v1` tag object `170bd3ff…`, 2026-09-03 20:43:04 +0530 | `git for-each-ref refs/tags/probe-v1` |
| `HOLES.md` byte-identical at `probe-v1` and `HEAD` (`a4e50ed6…`) | `git rev-parse probe-v1:HOLES.md` == `git rev-parse HEAD:HOLES.md`; `git diff` empty |
| "Below the calibrated threshold → THE WHOLE RUN IS VOID" | `HOLES.md`:221 |
| Void threshold is the sentinel `TODO_C14_CALIBRATION` | `config/protocol.yaml`:335 |
| Void rule is pure arithmetic | `src/whetstone_gate/probe/void.py`:81, :109 |
| `prereg-v1` does not exist; seven tags total | `git tag -l` |
| No witness gist; `<<PENDING-RUN: GIST_ID>>` | `README.md`:56-58, :1222 |
| `evals/` holds one file; `RESULTS.md` absent | `find evals -type f`; `ls RESULTS.md` |
| Review trail: 14 FAIL / 6 PASS over 20 files; 6 tagged; 14 unreviewed | counted by this session from `docs/reviews/REVIEW_*.md`, reading each file's own verdict line — three of the fourteen FAILs (`REVIEW_7_1`, `REVIEW_7_2`, `REVIEW_8_1`) record the verdict at the **foot** of the file, so a header-only scan undercounts by three. Agrees with `README.md`:955 |
| C6 reviewed six times, never passed, no tag | `README.md`:986; `docs/reviews/REVIEW_C6_1..6` |
| 137 `## INC-` headings | `grep -c "^## INC-" INCIDENTS.md` |
| INC-02 content and date (2026-08-28) | `INCIDENTS.md`:59-84 |
| INC-132 content, date (2026-09-04) and Fix SHA `1fd0877` | `INCIDENTS.md`:9832-9915 |
| First build commit `ee3cf93`, 2026-08-30 | `git log --reverse` |
| Repo URL | `git remote -v`; `README.md`:1202, :1450 |
| Repository still private until C21's flip | `PROCESS.md`:862 |
| Video URL absent; C20 `todo` | `STATUS.md`:1834; grep over `README.md` and `CONTEXT.md` |
| No payment method attached, attested 2026-08-30, operator-only | `PROVENANCE.md` §1.5 |
| Secret scan committed at `HEAD = 90b6d6fa…` | `docs/submission/git-history-secret-scan.txt`:4 |
| Determinism scope; model output is not reproducible | `CLAUDE.md` §2 rule 10; `README.md` §9.11; `CONTEXT.md` §20 |
| Placeholder convention `<<PENDING-RUN: name>>` | `README.md`:28 |
| Form is one-shot; no form until the review returns PASS | `PROCESS.md`:175, :1344 |

---

## 10. WHAT THIS SESSION DID NOT DO — so no reviewer has to infer it

- **Did not flip the repository public.** That is C21's other half and the operator's act.
- **Did not cut any tag**, including `prereg-v1`.
- **Did not touch `evals/`, `config/`, `src/`, `tests/`, `tests/goldens/`, `QUESTIONS.md`,
  `INCIDENTS.md`, `README.md`, `RESULTS.md`, `PROTOCOL.md`, `CONTEXT.md`, `PROCESS.md` or
  `corpora/`.** A concurrent session was live in this working tree throughout, spending the
  project's single-shot pilot window.
- **Did not re-run the git-history secret scan.** `docs/submission/` is inside this session's
  fence, but that scan's committed output is another session's completed artefact, and re-running
  it is checklist item **O-6** — an operator act ordered immediately before the visibility flip.
- **Spent zero provider tokens.** No sanction was held and none was taken. `.env` was never opened;
  no key name was paired with a value; no key value was read, printed or committed.
- **Did not run the pilot, the calibration or the sweep.**
- **Did not self-certify.** A fresh adversarial review follows.
