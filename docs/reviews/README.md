# `docs/reviews/` — the review trail

**This directory is a public artefact of the submission, not internal hygiene.**

Razorpay's build-quality rubric line is *"would you trust it"*, and that is otherwise only
assertable. This directory is what makes it checkable: it is the evidence that the work was
adversarially reviewed by sessions that did not write it.

**It is APPEND-ONLY. Nothing here is ever overwritten, renamed or deleted.**
A FAIL that is not in the repository did not happen.

---

## What lives here

| Path | What it is | Rule |
|---|---|---|
| `REVIEW_<N>_<attempt>.md` | one file per review **attempt** of chunk N, numbered from 1 | committed on **either** verdict. Never overwritten. `C7: built → FAIL(1) → fixed → PASS(2)` means two files exist, and the FAIL is still readable |
| `independent/c<N>_reimpl.py` | the reviewer's **from-scratch reimplementation**, written in Phase 1 from `CONTEXT.md` text alone, importing nothing from `src/` | **a `full` review with no reimplementation CANNOT PASS** |
| `independent/c<N>_reimpl_diff.txt` | Phase 2's diff of the project's output against the reimplementation, over the reviewer's own ≥20 vectors | any divergence is a finding |
| `mutants/c<N>_mutants.md` | one row per mutant: `file:line`, the operator changed, the test that killed it — **or an explicit equivalence proof** | **minimum 8 mutants on a `full` chunk**, ≥1 per invariant the chunk touches. `code` chunks: ≥4 |
| `ARCHITECT_CHECK_<N>.md` | the architect's VERIFICATION block — every load-bearing number recomputed, the value obtained beside the value claimed | **no chunk is tagged `cN-pass` without one.** An unrecorded gate is not a gate |
| `OPEN_FINDINGS.md` | every MEDIUM and LOW a review could not close | appended by every review; closed explicitly, with the SHA that closed it |

The three reviewer personas that every review prompt cites are one directory up, in
[`docs/personas/`](../personas/).

---

## The two sealed phases

A review is not one pass. (`PROCESS.md` §10, template 2.)

- **PHASE 1 — BLIND.** The reviewer reads `CLAUDE.md`, the personas, the chunk card, the cited
  `CONTEXT.md` sections, the `QUESTIONS.md` rulings and `tests/goldens/` — **and nothing else.** It
  may not open `PROGRESS.md`, `INCIDENTS.md`, the diff, or anything under `src/` or `tests/` other
  than the goldens. It reimplements the logic from the specification text and generates ≥20 of its
  own input vectors, including every boundary the spec names. **Both are committed before Phase 2
  begins.**
- **PHASE 2 — SIGHTED.** Only now does it read the diff and the journals, run the project's code on
  its Phase-1 vectors, mutation-test the critical operators, and re-derive every load-bearing number
  its own way.

Phase 1 is sealed first because a reviewer who has read the builder's code and the builder's story
is no longer re-deriving anything — it is confirming a view it has already seen.

**PASS requires ALL of:** every golden reproduced by the reviewer's own computation; every mutant
killed or proven equivalent; the reimplementation agreeing on all ≥20 vectors; **zero BLOCKER
findings**; and no reported figure contradicting `prereg-v1`. Anything else is FAIL. **A spec
deviation is FAIL even if every test passes.**

---

## Why a wall of PASSes would be bad news

`razorpay/ai-playbook` B.9: *"a release gate that has never gone red is only decorative."*
This project applies that to **its own review gate**, not just to its attacker.

- **C7, the ledger, is the SEEDED-DEFECT CHUNK** (`PROCESS.md` §5.4). The architect writes one
  specific, spec-violating defect into C7's build prompt, which the build session implements
  verbatim and does not flag. The C7 review session gets the ordinary review prompt with **no
  hint**. **If `REVIEW_7_1.md` does not raise that defect as a BLOCKER, the review process is
  declared broken**, building halts, and the review prompt and personas are rewritten before any
  further chunk is reviewed. Either way the transcript ships here and the README says what it is.
  **It is the only evidence in this repository that the PASS verdicts mean anything.**
- **The expected FAIL rate is stated in advance:** roughly **one FAIL per four chunks**. **If the
  first eight chunks all PASS first time, that is an `INCIDENTS.md` entry** — a finding about the
  gate, not a compliment to the builder.

A trail of twenty-two PASSes and no failures would be evidence that the gate is decorative, which is
precisely the thing this submission exists to criticise in other people's numbers.
