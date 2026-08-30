# ARCHITECT_HANDOFF.md — how a fresh session becomes the architect, from this repository alone

**Updated at the end of every chunk. If it is stale by more than one chunk, BUILDING STOPS
until it is current.** (`PROCESS.md` §11.)

**Why this file exists, stated plainly.** The architect is a chat session holding five days
of decisions across forty-plus reports — the searches, the killed ideas, the audit lenses,
and the reason behind every clause in the spec. **That is a single point of failure, and it
is treated as one rather than described as one.** This file is what survives it. The
reasoning that produced the decisions does not live here; the decisions, the state and the
next moves do.

*Current as of: **end of C0 build, 2026-08-30**. Chunk state: C0 built, unreviewed.*

---

## 1. The roles — read this before doing anything

| Role | Who | Does | **Never** does |
|---|---|---|---|
| **ARCHITECT** | one session, held open | owns the spec; **hand-computes the goldens**; writes every build and review prompt; recomputes load-bearing numbers and emits a VERIFICATION block per report; makes rulings; decides sequence | **writes project code, edits repo files, commits, or reviews** |
| **OPERATOR** | Chinmoy | carries prompts to fresh sessions, pastes reports back, runs long jobs in his own terminal, commits the goldens and the `ARCHITECT_CHECK` blocks, makes final calls | lets a session decide something the spec left open |
| **BUILD** | a fresh session | executes exactly one chunk | assumes · self-reviews · exceeds scope |
| **REVIEW** | a **different** fresh session | adversarially verifies one chunk, in two sealed phases | fixes what it reviews |
| **FIX** | a fresh session, after a FAIL | writes the `INCIDENTS.md` entry **first**, then fixes **only** the findings named | re-reviews its own fix |

**The three rules that make the roles real:**

1. **One prompt per chunk**, and never two prompts in one message.
2. **Up to two BUILD sessions may be in flight**, only if their scope fences are disjoint
   and neither imports the other, and only after the pair is recorded in `QUESTIONS.md`
   under `## Concurrent pairs` **before** either prompt is issued. **REVIEW sessions are
   strictly serial**, and a chunk's review may not begin before the architect has
   recomputed its build report and committed `ARCHITECT_CHECK_<N>.md`.
3. **Build and review are never the same session, and the architect is never the reviewer.**

---

## 2. The read order, for a session becoming the architect

1. **`CLAUDE.md`** — the thirteen hard rules. They bind you too.
2. **`CONTEXT.md`** — **the specification, and it is LAW.** Read §13 (cost, models,
   capacity) and §16 (repo structure) in full; §8.6 (every authored constant), §9 (the
   invariants), §10 (the probe), §12 (what we report) and §15 (pre-registration) closely.
3. **`PROCESS.md`** — the method. §4 (the rules), §5 (goldens and personas), §5.4 (**the
   seeded defect**), §6 and §6a (the freeze and its external witness), §11 (your duties),
   **§12 (the chunk plan — this is `plan.md`)**, §14 (the degradation ladder).
4. **`STATUS.md`** — where the project is, and the append-only review history.
5. **`PROGRESS.md`** — newest first. What the last sessions actually did.
6. **`QUESTIONS.md`** — **every open question is a decision waiting for you.** A ruling
   that exists only in a chat does not exist.
7. **`INCIDENTS.md`** — what has already broken.
8. **`docs/reviews/`** — `OPEN_FINDINGS.md` first, then any review of the chunk in hand.
9. **`PROVENANCE.md`** — what is owed, and by whom.

**Where the chunk plan lives:** `PROCESS.md` **§12.1**. It *is* `plan.md` — twenty-two
chunks C0–C21 plus seven operator runs, each with a calendar date, a time-box,
dependencies, a review type and a checkable done-when. **§12.0** carries the arithmetic
that plan has to survive; read it before you agree to a schedule.

---

## 3. Resume checklist — run this, in order, before issuing anything

```bash
git log --oneline -12                 # where are we
git tag                               # probe-v1? prereg-v1? which cN-pass?
git status --porcelain                # must be clean

python -m whetstone_gate.tasks test         # or: make test
python -m whetstone_gate.tasks check-roles  # or: make check-roles
```

Then, on paper:

- [ ] **Is `STATUS.md` consistent with the tags?** A chunk marked `PASS` with no `cN-pass`
      tag, or a tag with no `ARCHITECT_CHECK_<N>.md`, is a broken gate. **No chunk is
      tagged without an `ARCHITECT_CHECK`.**
- [ ] **Is every `QUESTIONS.md` item either RULED or explicitly still open?** Q-004 and
      Q-003 block later chunks — see §5.
- [ ] **Does the next chunk need a golden?** If it is a `full` chunk and
      `tests/goldens/` has no file for it, **you may not issue its build prompt.** Hand-compute
      the golden first and have the operator commit it. This is the most expensive rule in
      the process and the one most likely to be quietly skipped under time pressure.
- [ ] **Is `docs/reviews/OPEN_FINDINGS.md` growing?** Findings accumulating under a wall of
      PASSes is the failure mode it exists to prevent.
- [ ] **Have eight chunks passed first time?** If so, **write an `INCIDENTS.md` entry.**
      The expected rate is roughly **one FAIL per four chunks**; far under that is a finding
      about the gate, not a compliment to the builder.
- [ ] **Is a freeze tag involved?** After `probe-v1` and `prereg-v1`, **refuse any change to
      a frozen artefact, including one you would prefer.**

---

## 4. State — where the project actually is

### Built

| | |
|---|---|
| **C0** | **built, UNREVIEWED.** Repository, toolchain, private remote, canonical files, `config/` + loader, the day-one provider record |
| Everything else | `todo` |

**Nothing is tagged.** No `cN-pass`, no `probe-v1`, no `prereg-v1`.

### The environment, measured

| | |
|---|---|
| Python | **3.12.2** (`>=3.12,<3.14` required — τ²-bench at the pin makes 3.11 uninstallable) |
| `make` | shim at `~/bin/make.exe`, **GNU Make 3.82.90**, verified to run a recipe |
| τ²-bench | installed editable at `a2c024725189473d2d7cea3a5cfdbcc67478e41f`; `tau2-1.0.1` |
| `core.autocrlf` | `true`, **system-wide** — which is why `.gitattributes` is in commit one |
| Remote | `github.com/chinmoypaul8897/whetstone-gate`, **PRIVATE** |

### Bootstrapping a clean clone

⚠️ **The vendored trees are pinned, not committed** (`QUESTIONS.md` Q-010). A fresh clone
therefore runs three steps, not one, and **C19's clean-clone test must include all three**
or `CONTEXT.md` §20's first box is false:

```bash
git clone https://github.com/chinmoypaul8897/whetstone-gate && cd whetstone-gate
python -m venv .venv && source .venv/Scripts/activate   # 3.12.x REQUIRED
pip install -e .
#  ... then, for anything that touches tau2: the fetch commands in vendor/MANIFEST.md §2,
#      followed by `pip install -e vendor/tau2-bench`
make test          # or: python -m whetstone_gate.tasks test
```

---

## 5. What is sealed, what is owed, and every open ruling

### Sealed — do not reopen

These were ruled before the repository existed and are binding. Full list in
`QUESTIONS.md` § *Rulings carried in*.

- **The frozen set is exactly five files plus `config/`.** `INCIDENTS.md` is
  **snapshotted, not frozen** — it must keep growing.
- **Two tags, not one.** `probe-v1` (`HOLES.md` alone) is cut **before the pilot and before
  the calibration command runs**; `prereg-v1` after both, **before every scored episode**.
- **Calibration and pilot are single-shot.** `RUN_DECLARED.md` pushed first; the first run
  to completion **is** the run. Two completed calibration runs existing is a process
  violation **and is published as one**.
- **N is not a degradation rung.**
- **Python is 3.12.**
- **The probe is planted in C2**, not at the freeze. The calibration *measures* its breach
  rate, so the door must already exist in every seed's world.

### Owed — and by whom

| Owed | Owner | Blocks | Where |
|---|---|---|---|
| **The exact Google API model ids** (`models/gemma-…`, `models/gemini-…`) | **OPERATOR** | `make selftest`; every run | Q-006 |
| Dashboard **screenshots**, dated | **OPERATOR** | a C0 done-when box | Q-008 |
| **No-payment-method** confirmation | **OPERATOR** | a C0 done-when box; it is the ₹0 cost guarantee | Q-008 |
| **C0's `SESSION-TOKEN`**, retroactively | **ARCHITECT** | §7a's audit trail for C0 | Q-001 |
| **`ARCHITECT_CHECK_0.md`** | **ARCHITECT** | C0's review may not begin without it | `PROCESS.md` §11 |
| **Golden 7** (`world_seed_2001.json`) | **ARCHITECT** | **C2 may not be built without it** | `PROCESS.md` §5.2 |
| Goldens 1 and 3 | **ARCHITECT** | C4 | §5.2 |

### Open rulings the architect must make — in priority order

| # | Question | Why it is urgent |
|---|---|---|
| **1** | **Q-004** — do `gates/`, `scorer/`, `world/` … live **inside** `src/whetstone_gate/` or **beside** it? | `CONTEXT.md` §16's tree is self-inconsistent (a `└──` followed by eleven `├──` siblings). **The two readings differ in every import path**, and hard rule 8's module-graph test walks those paths. **Must be ruled before C2.** |
| **2** | **Q-003** — is `evals/` committed or ignored? | If ignored, `make eval` regenerates nothing from a clean clone, `RUN_DECLARED.md` cannot be pushed before its run, and §6b's single-shot control is unenforceable. Blocks C14, C18, C19. |
| **3** | **Q-010** — vendored trees pinned, not committed (793 MB measured) | **C19's clean-clone test must include the fetch step**, or §20's first box is false. |
| **4** | **Q-001** — C0's missing session token | The commits are permanently untrailered; decide whether to issue C0's token retroactively for the record. |
| **5** | **Q-009** — the two-tier suite (`make test` green, `make selftest` red by design) | Confirm or overturn; two C0 done-when boxes contradict each other without it. |
| **6** | **Q-002** (the `Date:` field), **Q-005** (a path typo in §16), **Q-007** (six unlisted models on the dashboards) | Low. Q-007 is informational: **no limit differs from §13.2**, so no incident is forced and §13.4's arithmetic stands. |

---

## 6. The next three prompts, in draft

**Before any of them:** issue a fresh 8-hex `SESSION-TOKEN`, record it in `QUESTIONS.md`
under `## Session tokens`, and open the prompt with it. Every prompt ends with the demand
for **one plain-text code block**, and the session commits that block to `docs/sessions/`
**before** printing it.

### Draft 1 — C0 REVIEW (`code`, persona 2). **Issue this first.**
Span `ee3cf93..HEAD`. Persona 2 only; ≥4 mutants; no reimplementation required.
**Point it at, without hinting at the answers:** the config loader's refusal semantics
(does a missing *and* an undetermined value really raise, and is there truly no defaulting
path?); the tripwire's two scan modes (does CONTEXTUAL miss a real violation? does STRICT
fire on innocent code?); the `.gitattributes` cross-platform digest claim; whether
`make test` green + `make selftest` red is honest or a dodge (**Q-009**); and whether
anything from the parent research directory leaked into the repository.
⚠️ **Do not tell it about Q-009's reasoning.** Whether a reviewer independently spots the
two-tier suite as a possible weakening is itself information about the review gate.

### Draft 2 — C1 BUILD: `RAZORPAY_SEMANTICS.md` + `PROVENANCE.md`'s A1–A6 rows
`full` review. **Written FIRST, before any world code** — it is the oracle for the
spend-free self-test. Every row: **verbatim quote + URL + fetch date. No row may be a
paraphrase.** All five instant-settlement bounds. The capture-concurrency error as **three
fields of an Errors table with its remediation intact**. `X-Refund-Idempotency` (min 10
chars, 409 on same-key-in-flight) **and** the `refunds.go:73-75` finding that an agent on
Razorpay's official MCP server **structurally cannot send it**. **A5 marked entirely
author-chosen wherever it appears.**

### Draft 3 — C2 BUILD: the world generator + **the probe planted**
`full` review. ⚠️ **BLOCKED until golden 7 is hand-computed and committed** — the six raw
`mulberry32(2001)` outputs to 10 significant figures **and** the complete 12-payment record
for seed 2001. Without it, C2's done-when collapses to *"two runs of one seed are
byte-identical"*, **which any deterministic function passes, including a wrong one** — and
the PRNG is being **reimplemented** in Python from a JavaScript spike, which is exactly
where a silent mis-port lives. `pay_CANARYRECON` present in **every** seed with the §10.1
fields exactly, exemption note verbatim.
⚠️ **Q-004 must be ruled before this prompt is issued** — it decides where the module goes.

---

## 7. The three things not to lose

1. **The seeded defect (`PROCESS.md` §5.4).** **C7 is the seeded-defect chunk.** The
   architect writes one specific, spec-violating defect into C7's build prompt — *"the chain
   verifier compares each entry's stored `prev_hash` to the previous entry's stored `hash`
   field, and never recomputes the previous entry's digest from its contents"* — which the
   build session implements verbatim and does not flag. **The C7 review gets the ordinary
   prompt with no hint. If `REVIEW_7_1.md` does not raise it as a BLOCKER, building halts**
   and the review prompt and personas are rewritten. It is the only evidence in the
   repository that the PASS verdicts mean anything.
2. **The freeze, both tags, and the external witness.** A git tag proves nothing about when
   it was made — git documents backdating under its own heading. **The gist is the witness,
   and without it the freeze is self-asserted.** Follow `PROCESS.md` §6a.2 **verbatim**; do
   not paraphrase those commands, because a paraphrase risks reintroducing the line-ending
   failure that would make the fingerprint fail for every non-Windows reviewer.
3. **The counter-metric.** The benign solver and the paired false-positive delta. **A
   project that publishes only what it blocked has published half a result** — and the 30
   benign scenarios must be traceable to a Razorpay documented example **by URL**, never
   builder-invented, because builder-written benign scenarios are the exact criticism this
   project levels at everyone else.
