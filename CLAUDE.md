# CLAUDE.md — the constitution

**Every session reads this file first, before anything else, without exception.**
It is short on purpose. It is rules, not explanation. The explanation is in `PROCESS.md`; the
specification is `CONTEXT.md`.

**Who you are.** You are exactly one of: a **BUILD** session (executes one chunk), a **REVIEW**
session (adversarially verifies one chunk, in two sealed phases), or a **FIX** session (after a
FAIL, writes the `INCIDENTS.md` entry *first*, then fixes only the findings named). Your prompt
says which. **Build and review are never the same session.** You never review your own work.

---

## 1. THE READ ORDER

Read these in this order. Every prompt names which sections; if it does not, read the whole file.

| # | File | What you are getting |
|---|---|---|
| 1 | **`CLAUDE.md`** (this file) | the rules you are bound by |
| 2 | **`plan.md`** → your chunk's card | scope, inputs, outputs, deps, review type, done-when |
| 3 | **`CONTEXT.md`**, the sections your prompt names | **the law** |
| 4 | **`STATUS.md`** | where the project is |
| 5 | **`PROGRESS.md`** (latest entries) | what the last sessions did |
| 6 | **`QUESTIONS.md`** | every ruling already made — a ruling binds you |
| 7 | **`INCIDENTS.md`** | what has already broken |
| 8 | **`tests/goldens/`**, the files your prompt names | the expected values. **Read-only to you** |
| 9 | **`docs/reviews/`**, any prior review of your chunk | the findings you must not reintroduce |

`plan.md` is `PROCESS.md` §12. `ARCHITECT_HANDOFF.md` tells a fresh session how to resume.

**If the card, the spec and the logs disagree → STOP and write `QUESTIONS.md`.** (Rule 1.)
**If `PROCESS.md` and `CONTEXT.md` disagree → `CONTEXT.md` wins, and you STOP and record it.**
**If a frozen artefact and `CONTEXT.md` disagree → the frozen artefact wins.** (Rule 4.)

---

## 2. THE THIRTEEN HARD RULES

**Verbatim from `PROCESS.md` §4. Not paraphrased, not summarised, not reordered.**

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

## 3. CALIBRATION AND PILOT ARE SINGLE-SHOT

**Verbatim from `PROCESS.md` §6b, which requires it to appear here. Mirrored at `CONTEXT.md` §15.4.**

> **CALIBRATION AND PILOT ARE SINGLE-SHOT.** Before either starts, the operator commits and pushes
> `evals/cal/RUN_DECLARED.md` (resp. `evals/pilot/RUN_DECLARED.md`) naming the exact command, the seed
> block, the turn budget, the models and the UTC start time. **The first execution that runs to
> completion IS the run**, and its output directory is the record whatever number it contains. If an
> attempt aborts before completion, the abort, its cause and its partial episode count are written to
> `INCIDENTS.md` **before** any retry, and the retry is a numbered attempt in the same directory.
> **Two completed calibration runs existing is a process violation and is published as one.**


---

## 4. TOKEN, KEY AND SAFETY RULES

These bind every session in every mode. (`PROCESS.md` §8, §10 template 3.)

- **Never read, print, echo or commit `.env` or any API key value.** To confirm a key exists, read
  only its **name**. Keys live in `.env`, which is git-ignored. `.env.example` carries names and
  **no** values.
- **No token spend unless your prompt explicitly sanctions it**, naming the lane, a **call ceiling
  AND a token ceiling**, and a window. A sanction of "max N calls" alone is not a sanction: one
  spike episode burned ~300K tokens against a 200K-TPD lane.
- **Before your first sanctioned call, read `evals/usage/<model>-<date>.jsonl`.** Abort at whichever
  ceiling comes first. Report actual tokens **by model**.
- **A 429 means the window is already spent: STOP and report. Never retry into another lane.**
  (The *runner* backs off and re-queues within its own lane; a *session* does not.)
- **LANE RESERVATION.** The reference-attacker lanes (Gemma 4 26B / 31B) and the gate-judge lanes
  are reserved for the sweep from 31 August. The ladder lanes (`gpt-oss-20b`, `qwen3.8-27b`,
  `gpt-oss-120b`) are reserved for the ladder windows. **No build session may spend on them.**
- **`evals/` is append-only to you.** Never delete, rewrite or truncate a completed episode's
  output. Deletions are operator-only.
- **`tests/goldens/` is read-only to you.** Never edit, add to, or regenerate a golden.
- **Never edit a frozen artefact after its tag exists** — `INVARIANTS.md`, `PROTOCOL.md`,
  `HOLES.md`, `PROVENANCE.md`, `RAZORPAY_SEMANTICS.md`, `config/`. If one is wrong, it is **not**
  edited: the run continues under the frozen protocol, the defect goes in `INCIDENTS.md`, and the
  finding is published as a limitation.
- **No destructive commands.** No `rm -rf`, no `Remove-Item -Recurse/-Force`, no `git clean -fdx`,
  no `git worktree remove --force`, no force-push, no tag move, no amend of a tagged commit.
- **Throwaway work goes to a fresh OS temp directory**, never into the repository.
- **Long runs execute in the operator's terminal**, never inside a session that might close.
- **If anything seems to require touching secrets, completed results, frozen artefacts, goldens, or
  files outside your task's scope: STOP and report instead of working around it.**

---

## 5. GIT RULES

(`PROCESS.md` §7, §7a.)

- **Atomic commits.** One logical unit. The message says **what + why**, citing spec sections.
- **Commit types:** `feat` / `fix` / `ref` / `test` / `chore` — Razorpay's own house convention.
- **Every commit touching source or tests, before its chunk's review, ends with `(unreviewed)`.**
  These markers are **permanent** — history is never rewritten — and the README explains them.
- **Every commit carries the trailer `Session-Token: <token>`**, the 8-hex token your prompt opened
  with. It is recorded in `QUESTIONS.md` under `## Session tokens`. **Never invent one and never
  reuse one:** `make check-roles` fails if a chunk's build and review commits share a token, if a
  token appears that was never issued, or if a token is reused across roles. **If your prompt did
  not carry a token, do not fabricate one — write it to `QUESTIONS.md` and say so in your report.**
- **Review PASS = a commit + a tag `cN-pass`.** The tag chain is the project's spine.
- **Pre-registration tags are separate and permanent: `probe-v1` and `prereg-v1`.** Not
  `preregistration-v1`.
- **No force-push. No tag moves. No amending a tagged commit.** No history rewrite, ever — a
  rewrite would destroy `probe-v1`, `prereg-v1` and every `cN-pass` tag.
- **The repository is PRIVATE until C21 flips it public on 4 September**, after the git-history
  secret scan has run and its output is committed.
- **Secrets never in the repo, never in logs, never in reports.**
- **Every session ends with a push, and states the pushed SHA as the first line of its report.**
- **AI attribution is permitted and encouraged** on this project. The operator's usual template
  bans it; that rule is deliberately dropped here (`PROCESS.md` §7).

---

## 6. END-OF-SESSION DUTIES

**Do all of these. A session that skips one is not finished.** (`PROCESS.md` §3, §11.)

1. **Commit your FINAL OUTPUT block, verbatim, to `docs/sessions/<chunk>-<role>-<attempt>.txt`
   BEFORE you print it.** What the architect reads is a convenience copy; **the file is the
   record**, and a paraphrase on the way is then detectable against it.
2. **Update `STATUS.md`** — your chunk's row, and **append** to the review-history column. That
   column is never erased or overwritten.
3. **Update `PROGRESS.md`** — one entry, newest on top, opening with your `SESSION-TOKEN`.
4. **Append to `INCIDENTS.md` anything that broke**, in rule 13's format, with `Diagnosis` and
   `Missed` filled in. An entry with either empty is not an entry.
5. **Append every unclosed MEDIUM/LOW finding to `docs/reviews/OPEN_FINDINGS.md`** (review
   sessions).
6. **Write every ambiguity and every ruling to `QUESTIONS.md`, verbatim.** A ruling that exists only
   in a chat does not exist.
7. **Push.** State the pushed SHA as the first line of your report.
8. **Emit your FINAL OUTPUT as ONE plain-text code block, no markdown.** The operator copies it in
   one motion and does not read the transcript. Everything that matters is inside the block.
9. **Do not self-certify.** A fresh adversarial review follows. Tag `cN-pass` only on a review PASS,
   and only a review session tags it.

---

## 7. WHAT THIS PROJECT IS — the one paragraph that keeps you honest

Razorpay's official MCP server lets a model move a merchant's money with no spend ceiling. Around
forty other Track 01 entrants built the missing policy gate; each authored its own world **and** its
own answer key, and the recurring headline is *100% blocked*. **This project builds the same gate,
then attacks it with an adversary that has never seen the policy, on an externally-authored answer
key, and publishes what got through — including a competence probe that VOIDS our own run if the
attacker was not really trying.** The measurements are frozen, git-tagged and **witnessed outside
this repository** before any scored episode runs.

**So every rule above is the argument, applied to ourselves.** If our numbers are unsound, the
submission is worse than worthless. That is why the build session never reviews its own chunk, why
the goldens are hand-computed before the code, why `gates/` and `scorer/` share no first-party
module, and why a test is never weakened to get green.
