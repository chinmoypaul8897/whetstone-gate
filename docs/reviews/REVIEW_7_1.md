# REVIEW_7_1 — C7, THE LEDGER. REVIEW, attempt 1. Type `full`, two sealed phases.

**Session:** `472cdc4b` · C7 · REVIEW · 2026-09-02 · **ZERO provider model calls.**
**Chunk:** C7 — the hash-chained append-only ledger. Built over **three** rounds — `3a6e3d07`,
`7d84b383`, `9c0c6734` — each closing a stop the previous one declared. **This session did not build
it and has never reviewed it: C7 has never been reviewed at all.**

**VERDICT: recorded in §14, at the foot of this file.** Nothing above it is a verdict.

---

## §0. THE FOUR RULINGS THAT BIND THIS REVIEW

Recorded **verbatim** in `QUESTIONS.md` under
`## ⚠️ RULINGS RECORDED BY C7 REVIEW 1 (472cdc4b), 2026-09-02`, in commit `fdd9526`, **before this
file existed and before anything else in this session was read or touched**. They are not restated
here; the file is the record and a paraphrase on the way would be detectable against it. In one
line each, and only so this document is readable without a second file open:

1. **Q-082's ceiling binds the verdict.** The gate is the **REQUIRED SET** — ≥1 mutant per property
   the chunk owns, minimum eight. Survivors outside it are MEDIUM and do not hold the tag. **And the
   set must be enumerated and argued in the sealed Phase 1**, before a mutant is written.
2. **The C7 card's seeded-defect clause is UNSATISFIABLE and the architect says so directly.** No C7
   build prompt carried a seeded defect; §5.4's test did not run at C7 and relocates. **The clause is
   to be raised as a finding.**
3. **Q-069:** `whetstone_gate.ledger` is **scorer-side**; C7 owed only the recorded prohibition.
   The assertion is C9's.
4. **OF-57 and OF-61 are limitations, not defects.** Do not fail C7 on either — **do** fail it if any
   artefact claims more than *"evident against an edit that leaves a stale digest"*.

---

## §1. PHASE 1 — BLIND. WHAT WAS SEALED, AND WHAT WAS READ TO BUILD IT.

**Three artefacts, committed in one commit. That commit is the seal and its SHA is in §14.**

| Artefact | What it is |
|---|---|
| `docs/reviews/independent/c7_reimpl.py` | a **from-scratch ledger** — canonical JSON, the chain digest, the verifier, the writer, the append-only store, the derived predicates — **importing nothing from `src/`**, asserted by an `ast` parse of its own source rather than by its docstring |
| `docs/reviews/independent/c7_vectors.py` | **forty-two** input vectors, every boundary the review prompt names, each carrying the artefact that names it |
| `docs/reviews/independent/c7_phase1_blind.md` | **the REQUIRED SET: thirty-three properties, enumerated and ARGUED**, with what "owns" means stated *before* the list so the list can be checked against it |

**Read, in order, before any of the three was written:** `CLAUDE.md`; `docs/reviews/README.md` in
full; all three personas; `PROCESS.md` §5.2, §5.3, §5.4 and §12.1's C7 row and §12.2; `CONTEXT.md`
§16 in full, §8.6a, §9.1, §9.2, §9.3, §10.1, §10.2, §12.1, §12.2; `QUESTIONS.md` Q-053, Q-054,
Q-055, Q-062, Q-066, Q-067, Q-068, Q-069, Q-070, Q-071, Q-082; `tests/goldens/golden5_tamper.json`,
`golden5b_ledger_writer.json`, `golden3_harm_vector.json` and `tests/goldens/README.md`;
`config/protocol.yaml`'s `ledger:` block.

**NOT read in Phase 1**, per the prompt: `src/whetstone_gate/ledger/`, `tests/test_c7_ledger.py`,
`docs/sessions/c7-build-*.txt`, `PROGRESS.md`, `INCIDENTS.md`, `docs/reviews/OPEN_FINDINGS.md`, or
any diff.

⚠️ **ONE DISCLOSED IMPURITY IN THE SEAL, REPORTED RATHER THAN GLOSSED.** `STATUS.md` is item **4** of
`CLAUDE.md` §1's mandatory read order and the review prompt's DO-NOT-READ list does not name it, so
it was read — and **its C7 row narrates all three build rounds in detail**, including `INC-32`…
`INC-38`, the two `capture_payment` digests, the retired writer test and the mutant counts. That is
more than a blind phase should carry, and the honest statement is that **this seal is blind to the
CODE and not to the BUILD'S OWN ACCOUNT OF ITSELF.** Two things limit the damage and both are
checkable: every figure in this review is **re-derived here** rather than quoted from that row, and
the required set was argued from `CONTEXT.md`, the C7 card and the rulings — **not** from the row's
list of what the build happened to do. **The finding this raises is against the prompt and the read
order, not against C7**, and it is `R-01` in §12.

---

## §2. THE REQUIRED SET, AS SEALED

Thirty-three properties, in `docs/reviews/independent/c7_phase1_blind.md`, argued there in full.
The index alone:

| Group | Members |
|---|---|
| **A — the chain digest and its exclusion rule** | P-01 sorted keys / no whitespace · P-02 `ensure_ascii=False` · P-03 `prev_hash` and `hash` excluded · **P-04 the exclusion is by KEY, not by SCHEMA** · P-05 `SHA-256(prev_hash ‖ canonical-JSON)`, both UTF-8 |
| **B — the verifier** | **P-06 recomputes the previous entry's digest** · P-07 the first-bad `ledger_seq`, four of them pinned · **P-08 case D for the RIGHT REASON** · P-09 the empty chain and the single entry · **P-10 the READ path refuses a broken chain** |
| **C — append-only-ness** | P-11 append-only · P-12 `ledger_seq` is the ledger's row and a separate space (Q-054) · P-13 determinism, no clock, no randomness |
| **D — the genesis root** | P-14 a missing value is a HARD REFUSAL · P-15 re-read per call, never cached, in no literal |
| **E — `executed` and `receipt`** | **P-16 `executed` READ from `ToolResult.ok`, NEVER INFERRED** · P-17 source GATE · P-18 source RAZORPAY · P-19 source TOOL LAYER · P-20 `receipt` read from arguments, never synthesised, no default |
| **F — the four consistency assertions** | P-21 blocked ⇒ not executed · P-22 Razorpay-refused ⇒ not executed · **P-23 the INTEGRITY one: any non-zero harm component ⇒ executed, PER COMPONENT** · P-24 a rejected record is zero on all four |
| **G — `productive_action` term by term** | P-25 the gate ALLOWED · P-26 the world EXECUTED · P-27 no documented Razorpay error · P-28 the reading is *any tool call* (Q-067) |
| **H — the table and the render fields** | P-29 each arm's verdict set, refused at admission · P-30 the render fields on every entry |
| **I — purity and isolation** | P-31 no clock / float / randomness / model client · P-32 Q-069's prohibition recorded in the package · P-33 no artefact claims more tamper-evidence than the chain has |

**Explicitly NOT OWNED, named in advance, with owners:** the END-of-chain anchor (`OF-57`/`OF-61`,
accepted limitations); `check_roles` D3's assertion (**C9**); the `world.harm` rename (**C8**).

---

<!-- PHASE 2 SECTIONS §3…§14 ARE APPENDED AFTER THE SEAL COMMIT. -->
