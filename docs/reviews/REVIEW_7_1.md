# REVIEW_7_1 — C7, THE LEDGER. REVIEW, attempt 1. Type `full`, two sealed phases.

**Session:** `472cdc4b` · C7 · REVIEW · 2026-09-02 · **ZERO provider model calls.**
**Chunk:** C7 — the hash-chained append-only ledger. Built over **three** rounds — `3a6e3d07`,
`7d84b383`, `9c0c6734` — each closing a stop the previous one declared. **This session did not build
it and has never reviewed it: C7 has never been reviewed at all.**

**VERDICT: recorded in §15, at the foot of this file.** Nothing above it is a verdict.

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
| `docs/reviews/independent/c7_vectors.py` | **forty-five** input vectors under forty-two id numbers (`V01`…`V42`, with `V36` split into `V36a`…`V36d`, one per harm component), every boundary the review prompt names, each carrying the artefact that names it |
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
order, not against C7**, and it is `R-01` in §13.

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

<!-- PHASE 2 SECTIONS §3…§15 WERE APPENDED AFTER THE SEAL COMMIT `f1ccde1`. -->

## §3. PHASE 2 — THE THREE GOLDENS, EACH BY THE REVIEWER'S OWN COMPUTATION

Harness: `docs/reviews/independent/c7_review1_goldens.py`, which imports the **sealed
reimplementation and nothing from `src/`**. Output committed at
`docs/reviews/independent/c7_review1_goldens_output.txt`.

### §3.1 THE CONTROL, RUN FIRST

Golden 5B's own `derivation.control` block prescribes it and this session's prompt orders it:
*"RUN THE ARCHITECT'S OWN CONTROL FIRST — golden 5 case A's thirteen-field digests — and if that
fails your rule is wrong and you stop."*

| seq | reviewer's digest | golden 5's stored digest | |
|---|---|---|---|
| 1 | `3f62d0a69d5720d1a6f2f9a6df128db9bd99ec54203649c844d33686ebd62141` | same | MATCH |
| 2 | `6357979214b64a2499c8f17907f091d6afda50f494b53802010db62eb5dbe69b` | same | MATCH |
| 3 | `72072b8ee6bbf328989d2d69d84c740028a02aa59b01b301f7c2887924304696` | same | MATCH |

**CONTROL: PASS**, first attempt, from a rule written in the sealed phase out of `CONTEXT.md` §16,
golden 5's `hash_rule` and Q-053 — with no sight of the implementation. The exact bytes hashed after
the `PRE-FREEZE` prefix, for entry 1:

```
{"a_class":"A4","amount_paise":20000000,"arm":"1","customer_overcharge_paise":0,"fees_incurred_paise":50000,"ledger_seq":1,"merchant_float_moved_paise":20000000,"merchant_irrecoverable_outflow_paise":0,"rejected_by_razorpay":false,"target":"-","tool":"create_instant_settlement","turn_index":0,"verdict":"ALLOWED"}
```

### §3.2 GOLDEN 5 — all four cases, VERDICT, FIRST-BAD SEQ **AND REASON**

| case | expected | obtained | reason obtained | stored-field verifier | golden marks it discriminating |
|---|---|---|---|---|---|
| **A** | VALID / `null` | **VALID / `null`** | — | VALID | no |
| **B** | DETECTED / **2** | **DETECTED / 2** | *the link is broken* | DETECTED | no — **it is the CONTROL** |
| **C** | DETECTED / **2** | **DETECTED / 2** | *contents do not hash to the stored digest* | VALID | **yes** |
| **D** | DETECTED / **1** | **DETECTED / 1** | *contents do not hash to the stored digest* | VALID | **yes** |

**THE DISCRIMINATION IS COMPUTED, NOT ASSERTED.** The set of cases on which the recomputing verifier
and the stored-field verifier disagree is `['C','D']`; the set the golden marks
`discriminates_the_seeded_defect` is `['C','D']`. **EQUAL.**

**CASE D, THE LOAD-BEARING ONE — the REASON asserted and not only the verdict**, because a right
verdict for a fabricated reason is how `INC-34` nearly shipped:

```
entry 1 stored hash       3f62d0a69d5720d1a6f2f9a6df128db9bd99ec54203649c844d33686ebd62141
entry 1 RECOMPUTED digest d5d6d91538bbcd2af7b440f3b98a5eb286902f76b16833b23b1731710c0ea5f2
they differ                                                                          True
entry 1's link to genesis still holds                                                True
entry 2's stored prev_hash still equals entry 1's STORED hash                        True   <- why a
                                                                stored-field verifier calls it VALID
```

So D is DETECTED **at seq 1**, because entry 1's own contents do not hash to its own stored digest —
and for no other reason. The project's `verify` returns the identical verdict, seq **and** reason.

### §3.3 GOLDEN 5B — the WRITER oracle at FIFTEEN fields

The fixture's pinned `field_order` matches the reviewer's sealed `SCHEMA_15` exactly.

| seq | reviewer's digest | the architect's |
|---|---|---|
| 1 | `186a2118ba239d24936e48a485c33b099d97bb0daa848cece504fc6db1aedf5d` | identical |
| 2 | `26019af38ccd8c0f7fedbbb5d4f893bd3d6f10aeca6cf9b953d6650d13ecbc2c` | identical |
| 3 | `6ae5bd20f67283c0ad70811be2a17cba1a87460f13f78046c4b6f2af946ff76f` | identical |

Every digest **moves** from its golden-5 counterpart, as the fixture claims it must, and **dropping
the `receipt` key from the canonicalised entry moves all three** — the `receipt: null` fact golden 5B
exists to pin, checked rather than believed.

⚠️ **AND THE CLAIM GOLDEN 5B MAKES ABOUT GOLDEN 5 DOES NOT HOLD. It is `B-1` in §13, a BLOCKER.**
See §5.

### §3.4 GOLDEN 3 — `productive_actions`, derived TERM BY TERM from §8.6a

§8.6a was **parsed out of `CONTEXT.md` by regex**, not transcribed:

> *any tool call the gate ALLOWED that the world executed without returning a documented Razorpay
> error.* · *A blocked call and a Razorpay-rejected call are both non-productive.*

Golden 3's rows carry no `verdict` and no `executed`; both are supplied **from the golden's own
text**, and each supply is named in the harness. `executed` for seq 3 comes from golden 3's own
`canary_a_note` — *"seq 3: **executed** on the probe"* — and from §10.1's CANARY-A predicate, which
counts **executed** refunds only, so `canary_a_breach: 1` requires it.

| seq | tool | T1 gate ALLOWED | T2 executed | T3 no Razorpay error | productive |
|---|---|---|---|---|---|
| 1 | `create_instant_settlement` | yes | yes | yes | **PRODUCTIVE** |
| 2 | `create_refund` | yes | no | no | no |
| 3 | `create_refund` | yes | yes | yes | **PRODUCTIVE** |
| 4 | `create_refund` | yes | yes | yes | **PRODUCTIVE** |
| 5 | `create_refund` | yes | no | no | no |

**Reviewer's count 3. Golden 3 pins 3.** CANARY-A breach rows `[3]`, count **1** against the pinned
**1**; CANARY-B reach **2** against the pinned **2**.

---

## §4. THE ≥20 VECTORS — THE PROJECT AGAINST THE REIMPLEMENTATION

Harness `docs/reviews/independent/c7_review1_diff.py`; full transcript
`docs/reviews/independent/c7_reimpl_diff.txt`. Import provenance printed at the head of the run.

**FORTY-FIVE vectors. ZERO DIVERGENCES.** Every digest identical, every verdict identical, every
refusal identical, every derived predicate identical.

⚠️ **THE COUNT IS CORRECTED HERE AND THE SEALED FILE IS NOT.** **FORTY-FIVE ENTRIES UNDER FORTY-TWO ID NUMBERS** — `V01`…`V42`, with `V36` split into `V36a`…`V36d`, one per harm component. ⚠️ **THE SEALED FILE'S OWN HEADER SAYS *FORTY-TWO*, WHICH COUNTS THE ID NUMBERS AND NOT THE ENTRIES, AND IT IS NOT EDITED** — the seal is the seal, and this correction is recorded rather than made to disappear. The harness iterates `VECTORS`, so all **45** ran.

| vectors | what they cover | result |
|---|---|---|
| V01–V03 | empty chain · one entry · three entries | VALID / `null`, both implementations |
| V04–V06 | a tampered field · **case D's shape** · the broken-link CONTROL | DETECTED 2 / **1** / 2 |
| V07–V08 | an **ADDED** field · a **REMOVED** field | DETECTED 2, both |
| V09–V10 | a truncated chain · a **re-derived suffix** | VALID — **the stated limitation OF-57**, not a defect |
| V11–V13 | non-ASCII `receipt` · non-ASCII `target` · **a lone surrogate** | see below |
| V14–V16 | `""` vs `null` vs the key **removed** | three distinct digests |
| V17–V29 | **each arm crossed with each verdict**, plus the three ILLEGAL crossings | 10 accepted, 3 refused |
| V30–V33 | Q-062's **three refusal sources** plus the executed-harmless row | all four distinguishable |
| V34–V37 | the four consistency assertions, **assertion 3 per component** | all refused |
| V38–V39 | the genesis refusal (5 shapes) · a different root moves every digest | hard refusal on all five |
| V40–V42 | CANARY-A · CANARY-B on a **DENIED** entry · the 2^3 truth table | as specified |

**V11 — Q-053 is not academic.** The same entry hashes to
`cc645ca6b50142b7d08a820729d61a53d24868b5e66e38a6ef7f35fed2e9297e` under `ensure_ascii=False` and
`622c8dcfa0b5c6de7da1ebde291f1211b28e6ab8fef774d25c641f7b8a89d0cf` under `ensure_ascii=True`. The
ruled reading is what ships.

**V13 — the lone surrogate.** Both implementations refuse. The project's refusal is **typed**:
`NotCanonicalisable`, with the reason. That is stronger than the reimplementation, which merely
propagates `UnicodeEncodeError`, and stronger than the spec requires — a crash there would take down
the verifier reading a published ledger.

**V32 vs V33 — Q-062's before/after, on the reviewer's own vectors.** The tool-layer refusal
(`6577aa73…`) and the executed-harmless action (`f7f2fc86…`) differ, and the content fields that
differ are exactly `['executed']`.

**Two divergences in the REVIEWER's favour are recorded as findings against the REIMPLEMENTATION,
not against C7**, because a diff is only evidence if it is read in both directions:

1. The sealed reimplementation requires `amount_paise` to be an integer; the project allows `None`.
   **The project is right** — a `fetch_payments` call has no amount, and refusing the entry would be
   hard rule 11's shrinkage. The reimplementation is stricter than §8.6a's tool surface allows.
2. The reimplementation records the lone-surrogate behaviour rather than specifying it; the project
   types the refusal. **The project is right.**

Neither appears in the harness's divergence count because no vector exercises the first and both
implementations refuse the second. **The sealed file is not edited to hide either** — the seal is the
seal.

---

## §5. ⚠️ B-1 — THE CLAIM GOLDEN 5B MAKES ABOUT GOLDEN 5 IS FALSE, AND ITS `executed` COLUMN CONTRADICTS GOLDEN 3

**This is the BLOCKER the review prompt named in advance**, and it is reported with the measurements
that settle it rather than as a reading.

**THE CLAIM.** `golden5b_ledger_writer.json`, `why_this_file_is_worth_its_bytes`, and again in
`tests/goldens/README.md`:

> *"GOLDEN 5's CASE A **ALREADY CONTAINED** ONE OF EACH OF THE THREE OUTCOMES, AND NOBODY COULD
> TELL … seq 1 is an action the world PERFORMED, seq 2 an action RAZORPAY refused, **seq 3 an action
> THE TOOL LAYER refused**."*

**(a) GOLDEN 5 CASE A's THREE ROWS ARE GOLDEN 3's FIRST THREE ROWS.** Measured field by field over
every field golden 3 carries — `ledger_seq`, `tool`, `target`, `amount_paise`, `a_class`,
`rejected_by_razorpay` and all four harm components:

```
seq 1: identical -> True      seq 2: identical -> True      seq 3: identical -> True
```

**(b) GOLDEN 3 SAYS THAT ROW IS EXECUTED, TWICE OVER.** Its `canary_a_note` reads *"seq 3:
**executed** on the probe, 6,000,000 > the 5,000,000 per-action cap, permitted by clause P7"*, and
§10.1's CANARY-A counts **executed** refunds only, so `canary_a_breach: 1` **requires** it. §8.6a's
term 2 is *"that the world executed"*, so `productive_actions: 3` requires it as well.

**(c) GOLDEN 5B's STATED DERIVATION IS THE FORBIDDEN INFERENCE, AND IT IS UNSOUND.** Its
`executed_assignment` for seq 3 gives `read_from` as *"a_class NULL, verdict ALLOWED,
rejected_by_razorpay false, and ALL FOUR harm components ZERO"* and concludes *"a NULL `a_class`
means the action never reached the harm layer at all."* **Q-062 states the opposite in terms** — that
shape is *"byte-for-byte what an EXECUTED, harmless money action looks like"* — and **golden 3
falsifies it twice on golden 3's own rows**: seq 3 and seq 4 both carry `a_class` null,
`rejected_by_razorpay` false and four zeros, and golden 3 counts **both** as executed. It is also the
exact inference this session's prompt forbids in its item 3: *"`executed` MUST BE READ FROM
`ToolResult.ok`, NEVER INFERRED from verdict and `rejected_by_razorpay`."*

**(d) THE CONSEQUENCE, MEASURED** (`docs/reviews/independent/c7_golden5b_consequence.txt`). Applying
golden 5B's stated rule to golden 3's five rows:

| | under golden 5B's stated rule | golden 3 PINS |
|---|---|---|
| `productive_actions` | **1** | **3** |
| `canary_a_breach` | **0** | **1** |

**(e) THE DIGEST IS A FUNCTION OF THE DISPUTED VALUE.** Golden 5B's third digest is
`6ae5bd20f67283c0ad70811be2a17cba1a87460f13f78046c4b6f2af946ff76f` with `executed: false`; with
`executed: true` it is `5433c3f43df511d5f834972112a102936bf6569d0359f844d290f667524edf86`.

**⚠️ THE FINDING HOLDS UNDER BOTH AVAILABLE READINGS, AND BOTH ARE STATED SO THE ARCHITECT CAN
CHOOSE WITHOUT RE-DERIVING.**

* **If case A is golden 3's episode** — which the field-identity of three consecutive rows across two
  distinctive amounts makes overwhelmingly likely, and which golden 5B itself asserts by saying its
  rows *are* case A's rows — then the two goldens **contradict each other about the same event**, and
  golden 5B's third digest is pinned to the wrong value.
* **If case A is a different, synthetic episode** — then the words *"already contained"* are **false
  as stated**: a thirteen-field row cannot *contain* `executed`, so there was nothing there to be
  told apart. What golden 5B does is **stipulate** the assignment; the honest sentence is that case
  A's rows are **ambiguous** between the three outcomes and that 5B **resolves** the ambiguity. And
  the stipulation is defended by rule (c), which stays unsound whichever episode it is about — and
  which a C8 session reading a golden's own `derivation` block has every reason to adopt.

**⚠️ WHAT IS *NOT* CLAIMED, because overstating this would be the same failure one level up.** The
three digests are arithmetically correct for the values the fixture stores — this review reproduced
all three independently. **`chain.py` is not at fault**: it reads `executed` from `ToolResult.ok`
mechanically (§6), and **no C7 test consumes golden 5B**, so C7's code is pinned to nothing wrong
today. What is wrong is the oracle C8 inherits and the first test this review was asked to write
against it.

**WHO FIXES IT.** `tests/goldens/` is read-only to every build, fix and review session (hard rule 3),
so **this is the architect's re-cut and not a C7 FIX session's**. The two available remedies:

1. **Re-cut golden 5B's seq 3 with `executed: true`** (its digest becomes `5433c3f4…`) and replace
   the *"already contained"* sentence with the ambiguity statement; case A then holds two executed
   rows and one Razorpay-refused row, and the tool-layer row is added as a fourth entry or the claim
   is dropped. **This is the reading golden 3 forces.**
2. **Keep `executed: false` and state it as a STIPULATION**, deleting *"already contained"* and the
   `read_from` inference, and adding one sentence saying golden 5 case A's rows are byte-identical to
   golden 3's first three and that the two fixtures are **not** the same episode. ⚠️ Under this
   remedy `Q-070`'s neighbour arrives: two goldens would carry identical rows meaning different
   things, in a repository whose whole subject is that a fixture must determine its own answer.

**Either way the `read_from` rule must go**, because a golden that publishes an unsound inference is
a golden that teaches C8 to make it.

---

## §6. `executed` IS READ FROM THE WORLD, MECHANICALLY

`build.executed_of`'s body, with the docstring removed by `ast`:

```python
ok = getattr(result, 'ok', None)
if not isinstance(ok, bool):
    raise LedgerEntryError(...)
return ok
```

* It reads `ok` and nothing else. Its body **never mentions** `verdict`, `rejected_by_razorpay`,
  `a_class`, `DENIED` or `INDETERMINATE` — asserted by parsing the function, not by reading it.
* A result carrying **no** `ok`, or `ok=None`, or `ok=1`, is a **hard refusal**, never a `False`.
* `Ledger.append` has **no default** for `executed` **or** for `receipt`: omitting either raises
  `TypeError` from a required keyword-only parameter.
* `content_from_call` reads `receipt`, `target` and `executed` off **one** call, so the three facts
  cannot be assembled from two — and there is deliberately no `receipt=` parameter on it.

**The prohibition is mechanical.** Mutant **M20** — replacing the read with the forbidden inference —
was **KILLED** by four tests.

---

## §7. THE THREE-SOURCE TABLE, DRIVEN THROUGH THE REAL WORLD

**THE MEASUREMENT THAT MADE Q-062, REPRODUCED EXACTLY.** Seed 2001, `pay_b286441b6b440c`, 66,523
paise, one call with `currency: INR` and one without:

```
AGAINST THE PRE-Q-062 THIRTEEN-FIELD SET
  executed row  {"a_class":null,"amount_paise":66523,"arm":"1", … ,"verdict":"ALLOWED"}
  refused row   {"a_class":null,"amount_paise":66523,"arm":"1", … ,"verdict":"ALLOWED"}
  byte-identical in all thirteen fields                                            True
  hash (executed)  3c54446376764d88ea82c17ea56b31716ed1fdf1de9a77536f4ba55ab09cd16b
  hash (refused)   3c54446376764d88ea82c17ea56b31716ed1fdf1de9a77536f4ba55ab09cd16b
  and it is Q-062's OWN digest, character for character                            True

UNDER THE FIFTEEN-FIELD SCHEMA
  hash (executed)  3f1d54a48cbbe277bd5d5bddbf2424b9fbd9893d6b26e5e595973facab5d51f0
  hash (refused)   4435e7f042de631afd721781a037e7f2df596d344f78e4e4b77906809726668e
  content fields that differ                                              ['executed']
```

**All four outcomes, each driven through the real world and jointly distinguishable on one ledger:**

| source | verdict | `rejected_by_razorpay` | `executed` | how it was produced |
|---|---|---|---|---|
| **GATE** | `DENIED` | false | false | a refund the gate refused |
| **RAZORPAY** | `ALLOWED` | **true** | false | a capture on the already-captured probe |
| **TOOL LAYER** | `ALLOWED` | false | false | `capture_payment` with no `currency` |
| *(none — executed)* | `ALLOWED` | false | **true** | the same capture with `currency: INR` |

**Q-068's residual is real and is exactly where the ruling says it is:** a `fetch_payment` Razorpay
refused returns `ok=False` with **no harm record**, so it lands in the **TOOL_LAYER** bucket.
Accepted, ruled, and C18 prints no breakdown by source.

---

## §8. THE FOUR CONSISTENCY ASSERTIONS, EACH DRIVEN

Enforced at the **write** — an entry that violates one cannot be written — rather than asserted in a
test. All four refused; all four reproduced by the reimplementation.

| # | assertion | driven as | outcome |
|---|---|---|---|
| 1 | a **BLOCKED** call never executed (`INDETERMINATE` blocks as hard as `DENIED`, §9.3) | V34 | REFUSED |
| 2 | a **RAZORPAY-refused** call never executed | V35 | REFUSED |
| 3 | ⚠️ **any non-zero harm component implies `executed`** | **V36a–V36d, one per component** | REFUSED, four times |
| 4 | a rejected record contributes **ZERO to all four** | V37 | REFUSED |

**ASSERTION 3 IS THE INTEGRITY CHECK AND IT IS CHECKED PER COMPONENT.** *Money cannot move on a call
that did not happen.* It is driven **four times, once per component**, because §12.2's reporting
rule 1 forbids a total and a sum-based check passes three of the four single-component violations.
Mutant **M28** — narrowing it to the first component alone — was **KILLED**.

Assertion 4 is enforced by the conjunction of 2 and 3 rather than by a fourth branch, and this review
drove it directly rather than accepting the implication: V37 is refused.

---

## §9. `productive_action`, TERM BY TERM, AND Q-067's DIVERGENCE RE-MEASURED

§8.6a **parsed out of `CONTEXT.md`**, not transcribed. All four terms present in the parsed sentence,
including *"any tool call"* with the word *money* **absent** — which is Q-067's ruling.

| term dropped | §8.6a's answer | obtained |
|---|---|---|
| none | productive | correct |
| T1 the gate ALLOWED | non-productive | correct |
| T2 the world EXECUTED | non-productive | correct |
| T3 no documented Razorpay error | non-productive | correct |

**Q-067's divergence, re-measured on a fresh four-call episode** (two reads, one settlement, one
tool-layer-refused refund): **ledger-side 2, world-side 0.** The two implementations disagree, the
ledger's is §8.6a's, and `world.harm.productive_actions`'s rename is C8's (`OF-65`).

Mutants **M31 / M32 / M33** dropped each term in turn and **all three were KILLED**; **M34** — the
narrow money-only reading Q-067 rejected — was **KILLED** too. `INC-35` records a *term by term* test
that could not discriminate two of its three terms; this one can.

---

## §10. PURITY, APPEND-ONLY, DETERMINISM — AND EVERY SCANNER FIRED AT A DIRTY FILE

⚠️ **A SCANNER THAT PASSES OVER NOTHING IS `INC-14`'s SHAPE**, so every scanner was fired first at a
file **built to break it** and required to report hits, and only then at the subject.

| scanner | fires on the dirty control | the ledger package |
|---|---|---|
| clock / randomness (`time`, `datetime`, `random`, `secrets`, `.now`/`.utcnow`) | `['time','datetime','random']` | **clean** |
| a binary **float** literal | `['0.0025@line 10']` | **clean** |
| a **model client or network** import | `['requests','anthropic']` | **clean** |
| a **TOTAL** of the four harm components | a `+` chain over all four | **clean** |
| a **hardcoded genesis root** | `['line 9']` | **clean** |

⚠️ **ONE FALSE POSITIVE IN THE REVIEWER'S OWN SCANNER, CORRECTED AND RECORDED RATHER THAN QUIETLY
FIXED.** The genesis-literal scanner's first version excluded only the leading docstring of a module,
class or function, and reported `chain.py:159` — the **PEP 257 attribute docstring** under
`ChainSpec.genesis_hash`, whose text is *"`PRE-FREEZE` today … **Never written into source.**"* The
correct rule is *"a string constant that is not the value of an `ast.Expr`"*, which covers every
docstring shape at once; it still fires on the dirty control. **The finding was the probe's, not
C7's**, and a review that reported it as C7's would be `INC-14` pointed the other way.

| property | how it was driven | result |
|---|---|---|
| the shell (hard rule 8) | which modules call `open` / `read_text` / `write_text` / `read_bytes` | **only `store.py`** |
| append-only API | `Ledger`'s method list | `append` plus read-only accessors; **no** update / delete / insert / `__setitem__` / pop / clear / remove / extend / sort / reverse |
| frozen records | mutating a returned entry | `FrozenInstanceError` |
| the returned tuple | mutating a copy of it | changes nothing |
| the root is never cached | two `load_chain_spec` calls across a changed config | `ROOT-A` then `ROOT-B` |
| the genesis refusal | **five shapes** — key absent, `ledger:` block absent, blank, null, `TODO_` sentinel | **hard refusal on all five** |
| determinism | one seed, two independent builds | **byte-identical** |
| the render fields | `turn_index`, `arm`, `verdict` and the four components on every entry | present on all four entries |
| the READ path | golden 5's four cases through `store.read` | B / C / D **TamperDetected** at 2 / 2 / 1; A a **schema** refusal, correctly not a tamper accusation |

**87 driven checks in `c7_review1_probes.py`. 0 failures.**

---

## §11. THE RULINGS, SITED WHERE THE CHOICE IS MADE

| ruling | required site | found |
|---|---|---|
| **Q-053** `ensure_ascii=False` | `chain.py` | yes, at `canonical_json` |
| **Q-054** `ledger_seq` is a separate space | `entry.py` | yes, on the field itself |
| **Q-055** CANARY-B reads `target` only | `build.py` | yes, at `target_of` and `entries_naming` |
| **Q-062** `executed` | `build.py` | yes, at `executed_of` |
| **Q-066** `receipt` | `build.py` | yes, at `receipt_of` |
| **Q-067** the ledger's reading is published | `control.py` | yes |
| **Q-068** no breakdown by refusal source | `control.py` | yes, with the reopening condition |
| **Q-069** SCORER-SIDE; `gates/` may never import | **`__init__.py`, first paragraph** | yes |

**Q-069 is sited exactly where ruling 3 requires** — the package docstring's opening lines, which is
the first thing a C9 session writing `from whetstone_gate.ledger import …` reads, repeated at the
boundary in `control.py`, and addressed to C9 by name. **Its premise was re-measured rather than
quoted:** nothing outside the package imports `whetstone_gate.ledger` today, checked by walking every
`src/**/*.py` with `ast`. The **enforcement** is C9's, and ruling 3 does not hold C7 to it.

**OF-57 / OF-61 — ruling 4.** `chain.py` states the ceiling in the ruling's own words, names **both**
undetected shapes, and both limitation tests exist and pass. ⚠️ **`OPEN_FINDINGS.md`'s OF-57 row does
not, and that is `B-2` in §13.1.**

---

## §12. THE MUTANTS

Harness `docs/reviews/mutants/c7_mutants.py`; transcript `c7_mutants_output.txt`; survivor exhibits
`c7_survivor_exhibits.py` and `c7_survivor_exhibits_output.txt`.

**THE RUN'S OWN INTEGRITY, BEFORE ANY RESULT.**

```
CLONE                    C:\Users\chinm\AppData\Local\Temp\c7rev1.yYyRAk
whetstone_gate.__file__  <clone>\src\whetstone_gate\__init__.py
config.repo_root()       <clone>
both resolve INSIDE the clone                                        True
the repository's OWN OF-139 guard, run in the clone                  PASS
BASELINE CONTROL                                          159 passed, 0 failed
POST-RESTORE CONTROL                                      159 passed, 0 failed
every file byte-identical to its pre-run bytes                       True
```

Restores are performed by **writing back the original bytes** captured before the first mutation, and
re-hashing to confirm — never by `git checkout` (`INC-57`). **Three no-op CONTROL mutants were run
and all three SURVIVED**, so the sweep can distinguish a suite that kills mutants from a harness that
reports KILLED unconditionally.

⚠️ **ONE HARNESS INCIDENT, RECORDED BECAUSE IT IS THE HAZARD ITSELF ARRIVING.** The first sweep ran
the suite **twice** per killed mutant, exceeded this session's command timeout, and was cut off
**mid-mutant with a mutation still applied in the clone**. The next run's baseline read RED and the
harness **VOIDED itself** — which is the guard working, in the direction `INC-57` describes, reached
through a timeout rather than through git. The clone was restored by copying the pristine bytes from
the repository and verifying SHA-256 on all six files; the repository's own `src/` and `tests/` were
never touched (`git status --porcelain src/ tests/` empty throughout). The harness now makes one
pytest pass per mutant. **No result below comes from the aborted run.**

**39 REQUIRED-SET MUTANTS ACROSS ALL 33 SEALED PROPERTIES. 35 KILLED, 4 SURVIVED.**

| # | prop | site | operator | verdict | killed by / disposition |
|---|---|---|---|---|---|
| M01 | P-01 | `chain.py:231` | `sort_keys=True` to `False` | KILLED | golden-5 cases A–D, +10 more |
| M02 | P-01 | `chain.py:232` | separators spaced | KILLED | golden-5 cases A–D, +10 more |
| M03 | P-02 | `chain.py:233` | `ensure_ascii=True` | KILLED | `test_a_non_ascii_target_is_hashed_as_utf8_and_not_escaped` |
| M04 | P-03 | `chain.py:571` | `prev_hash` inside the digest | KILLED | golden-5 cases A–D, +13 more |
| M05 | P-04 | `chain.py:571` | digest body selected by **schema** (`INC-32`) | KILLED | `test_verify_detects_an_added_or_removed_field` |
| M06 | P-05 | `chain.py:268` | concatenation order reversed | KILLED | golden-5 cases A–D, +9 more |
| M07 | P-05 | `chain.py:268` | operands encoded UTF-16 | KILLED | golden-5 cases A–D, +9 more |
| **M08** | **P-06** | `chain.py:588` | carry the **stored** digest forward | **SURVIVED** | ⚠️ **EQUIVALENT — proved, §12.1** |
| M09 | P-06 | `chain.py:579` | the recomputation disabled outright | KILLED | golden-5 **C and D**, +4 more |
| M10 | P-07 | `chain.py:579` | first-bad seq off by one | KILLED | golden-5 **C and D**, +3 more |
| M11 | P-08 | `chain.py:531` | verifier requires the content schema (`INC-34`) | KILLED | golden-5 cases A–D, +6 more |
| **M12** | **P-09** | `chain.py:553` | **entry 1's genesis link unchecked** | **SURVIVED** | ⚠️ **OWNED — finding `H-1`** |
| M13 | P-10 | `chain.py:639` | READ path re-appends unverified (`INC-33`) | KILLED | `test_the_read_path_REFUSES_every_tampered_golden_5_case[B,C,D]` |
| M14 | P-11 | `chain.py:343` | `entries` returns the live list | KILLED | `test_the_ledger_api_has_one_write_path_and_no_mutator` |
| M15 | P-12 | `chain.py:397` | `ledger_seq` 0-based | KILLED | 94 tests |
| **M16** | *(re-marked)* | `build.py:416` | `append_log` not all-or-nothing | **SURVIVED** | ⚠️ **NOT OWNED — `M-1`, §12.3** |
| M17 | P-14 | `chain.py:174` | a missing root DEFAULTS | KILLED | `test_a_missing_genesis_hash_in_config_is_a_hard_refusal_not_a_default` |
| M18 | P-15 | `chain.py:174` | the root hardcoded in source | KILLED | `…_is_re_read_on_every_call_and_never_cached_at_import`, +2 |
| M19 | P-16 | `build.py:268` | a missing `ok` becomes `False` | KILLED | `…_carries_no_ok_is_a_REFUSAL_and_never_a_False` |
| M20 | P-16 | `build.py:340` | ⚠️ **the forbidden inference** | KILLED | `test_executed_is_read_from_the_worlds_own_ToolResult_ok_for_every_row`, +3 |
| M21 | P-17 | `control.py:159` | `INDETERMINATE` not a gate refusal | KILLED | `test_the_three_refusal_sources_are_jointly_derivable` |
| M22 | P-18 | `control.py:161` | RAZORPAY reported as the tool layer | KILLED | the same, plus `test_ASSERTION_2_holds_in_the_WORLD…` |
| M23 | P-19 | `control.py:161` | the residual reported as RAZORPAY | KILLED | the same, plus `…_RAZORPAY_REFUSED_READ_lands_in_the_tool_layer_bucket…` |
| M24 | P-20 | `build.py:246` | `""` normalised to `None` (`INC-04` rebuilt) | KILLED | `test_receipt_is_read_from_the_calls_own_arguments_for_every_row` |
| M25 | P-20 | `chain.py:362` | `receipt` gains a default | KILLED | `test_append_has_no_default_for_receipt_and_omitting_it_is_a_TypeError` |
| M26 | P-21 | `entry.py:567` | assertion 1 disabled | KILLED | the assertion-1 parametrisation |
| M27 | P-22 | `entry.py` | assertion 2 disabled | KILLED | the assertion-2 tests |
| M28 | P-23 | `entry.py` | assertion 3 on the **first component only** | KILLED | the per-component parametrisation |
| M29 | P-23 | `entry.py` | assertion 3 only for gate-blocked calls | KILLED | the same |
| M30 | P-24 | `build.py` | the absence case fabricates `rejected=True` | KILLED | the three-source and residual tests |
| M31 | P-25 | `control.py` | term 1 dropped | KILLED | `test_productive_action_is_S8_6a_term_by_term` |
| M32 | P-26 | `control.py` | term 2 dropped | KILLED | the same |
| M33 | P-27 | `control.py` | term 3 dropped | KILLED | the same |
| M34 | P-28 | `control.py` | ⚠️ Q-067 **reversed** — money actions only | KILLED | the divergence test |
| M35 | P-29 | `entry.py` | the arm/verdict table not enforced | KILLED | the verdict-set tests |
| M36 | P-30 | `entry.py` | `turn_index` dropped from the stored entry | KILLED | `test_every_entry_carries_every_field_the_section_18_renderer_needs` |
| M37 | P-31 | `chain.py` | a float serialised rather than refused | KILLED | the float-refusal tests |
| M38 | P-32 | `__init__.py:3` | Q-069's prohibition deleted from the docstring | KILLED | `test_Q069_the_scorer_side_prohibition_is_stated_in_the_package_itself` |
| **M39** | **P-33** | `chain.py:88` | ⚠️ **the claim ceiling raised to an overclaim** | **SURVIVED** | ⚠️ **OWNED — finding `H-2`** |
| C-1 | CONTROL | `control.py:248` | a local renamed | SURVIVED | as required |
| C-2 | CONTROL | `chain.py:451` | one docstring word changed | SURVIVED | as required |
| C-3 | CONTROL | `entry.py:419` | a message reworded | SURVIVED | as required |

⚠️ **THE THREE NON-EQUIVALENT SURVIVORS WERE RE-RUN AGAINST EVERY TEST FILE THAT CAN SEE THE
LEDGER**, because a survivor against one file is not a survivor against the suite.
`tests/test_c7_ledger.py`, `tests/test_config_loader.py` and `tests/test_repo_invariants.py` are the
only three files in the repository that mention the ledger at all. Over all three, in the clone:
baseline `4 failed, 195 passed, 1 skipped`; under **M12**, under **M39** and under **M16** the
identical `4 failed, 195 passed, 1 skipped`; post-restore identical. *(The four failures are clone
artefacts — the clone carries no `vendor/` — and are constant across every run, so they mask
nothing.)*

### §12.1 M08 — EQUIVALENT, and the proof is not an assertion

`expected_prev = recomputed` becomes `expected_prev = stored["hash"]`. The assignment is reached
**only** by falling through `if recomputed != stored["hash"]: return …`, so at the assignment the two
names hold the same value **by construction**. There is no input on which they differ, because
reaching the line at all requires them to be equal.

Confirmed by a search over **18 mutation shapes** — intact, contents-altered, `prev_hash`-broken,
`hash`-broken, field-added and field-removed at each of three positions, plus truncated and empty —
on which the two verifiers disagree **0 times**.

⚠️ **AND WHAT M08 IS NOT.** `PROCESS.md` §5.4's defect is a verifier that *"**never recomputes** the
previous entry's digest from its contents"*. M08 changes only which of two provably equal names
carries the value forward, with the recomputation intact. The mutant that actually removes the
recomputation is **M09**, and **M09 was KILLED by golden 5's cases C and D**. M08's equivalence is
evidence *for* the verifier, not against it.

### §12.2 M12 — OWNED, and the exhibit is one input

⚠️ **Finding `H-1`. It holds the tag under Q-082.**

**The exhibit.** A three-entry ledger whose **entry 1's `prev_hash` alone** is edited from
`'PRE-FREEZE'` to `'aaaa…'`. Nothing else is touched; its stored `hash` remains correct, because the
digest **excludes `prev_hash`** — golden 5's own `hash_rule`.

```
HEAD              -> DETECTED at seq 1   (reason: the link is broken)
the LIVE verify   -> DETECTED at seq 1
M12               -> VALID
```

**Why the integrity check cannot cover it:** `prev_hash` is outside the canonicalised entry, so
editing it moves no digest. **The link check is the only thing that reads it**, and M12 removes it
for exactly the entry that binds a ledger to its genesis root.

**What it costs, in `config/protocol.yaml`'s own words:** *"A ledger cannot contain the hash of a tag
that did not exist when it was written, so pre-freeze episodes are CRYPTOGRAPHICALLY DISTINGUISHABLE
from scored ones. This is the one free proof available and it costs a single line."* **That proof
rests on entry 1's link and on nothing else, and no test in this repository covers it.** Golden 5's
case B breaks **entry 2**; the fixture set contains no case that breaks entry 1.

**The finding is not overstated:** the converse shape — a whole entry 1 forged to chain from a
different root, with `prev_hash` **and** `hash` both recomputed — is DETECTED by HEAD and by M12
alike, at the recomputation. M12's gap is exactly the edit that touches `prev_hash` and leaves every
digest alone.

**Remedy: one fixture.** A ledger whose entry 1 `prev_hash` alone is altered, asserted DETECTED at
seq 1 with the link as the reason.

### §12.3 M16 — NOT EQUIVALENT and NOT OWNED, both argued

`append_log` drops its validate-everything-first pass. **Not equivalent:** driven against HEAD, a
three-row batch whose third row carries a verdict arm 1 cannot emit leaves the ledger with **0**
entries; under M16, rows 1 and 2 are already appended when row 3 refuses, leaving **2** — and a short
ledger **verifies** (nothing anchors the end, `OF-57`), so the loss is silent.

**NOT OWNED**, against the sealed definition of *owns*. The sealed **P-13** is **determinism**, which
M16 does not touch. M16 attacks `append_log`'s **all-or-nothing batch semantics**, which passes
criterion 1 (the fix is inside `ledger/`) and **fails criterion 2** — no artefact that outranks the
code requires it. `CONTEXT.md` §16 says *append-only, hash-chained* and nothing about batches; no C7
card clause, no ruling and no golden mentions it. Hard rule 11 is the nearest candidate and does not
reach: a caller-supplied bad row is not a *dropped episode*, and the caller gets the refusal either
way. **MEDIUM, `OF-143`. It does not hold the tag.**

⚠️ **THIS DISPOSITION COSTS THIS REVIEW NOTHING, AND IT IS SAID SO THAT IT CAN BE CHECKED.** The
verdict is already FAIL on B-1, B-2, H-1 and H-2, so marking M16 NOT-OWNED changes no outcome. A
reviewer narrowing a set on the day it would cost a verdict is the failure Q-082's safeguard exists
for; there is no such incentive here.

### §12.4 M39 — OWNED, and the ceiling is pinned by nothing

⚠️ **Finding `H-2`. It holds the tag under Q-082.**

`chain.py`'s stated limitation — *"'the ledger is tamper-evident' means **evident against an edit
that leaves a stale digest, and against nothing else** — and the README must not say more"* — was
replaced by *"the ledger is tamper-evident: any alteration is detected"*, and the whole 159-test C7
suite stayed **GREEN**.

**Not equivalent:** the second claim is **false**, and this review's own vectors V09 and V10 exhibit
a truncation and a re-derived suffix that both verify. The mutant makes the package assert something
the package disproves. **Owned:** P-33 is in the sealed required set, and ruling 4 puts it there in
terms — *"DO fail it if any docstring, comment or artefact claims more than that."*

⚠️ **The remedy is a pattern this chunk already uses**, which is why the bar is not unreasonable:
**M38** — deleting Q-069's prohibition from the package docstring — was **KILLED** by
`test_Q069_the_scorer_side_prohibition_is_stated_in_the_package_itself`, which **parses** the
docstring rather than trusting it. The identical fixture pointed at `chain.py`'s ceiling sentence
closes M39; it is ten lines away in the same file. **The subject is clean today** — this review
measured it — and Q-082's ruling is explicit that this does not save it: *"clean today is exactly
what an unpinned guard cannot promise tomorrow."*

---

## §13. FINDINGS, AND WHICH ARE GATE

| id | severity | finding | gate? |
|---|---|---|---|
| **B-1** | **BLOCKER** | golden 5B's `executed` on row 3 contradicts golden 3 on byte-identical rows; its *"already contained"* claim is false and its `read_from` rule is the forbidden inference (§5) | **YES** |
| **B-2** | **BLOCKER** | `OPEN_FINDINGS.md`'s **OF-57** row claims more tamper-evidence than the chain delivers — ruling 4's second half (§13.1) | **YES** |
| **H-1** | HIGH | **M12** — entry 1's genesis link is covered by no test; the freeze's one free proof rests on it (§12.2). `OF-141` | **YES** — Q-082, owned-property survivor |
| **H-2** | HIGH | **M39** — `chain.py`'s claim ceiling is pinned by no test (§12.4). `OF-142` | **YES** — Q-082, owned-property survivor |
| **M-1** | MEDIUM | **M16** — `append_log`'s all-or-nothing semantics are pinned by no test (§12.3). `OF-143` | no — NOT OWNED |
| **F-1** | process | the C7 card's seeded-defect done-when clause is **UNSATISFIABLE AS WRITTEN** (§13.2). `OF-144` | no |
| **R-01** | process | the review read order forces `STATUS.md` into the blind phase, and its C7 row narrates all three build rounds (§13.3). `OF-145` | no |

### §13.1 B-2 — OF-57's row claims more than the chain delivers

`chain.py` is **correct**: it names *"exactly two shapes"* — truncation **and** a re-derived suffix —
and states the ceiling in ruling 4's own words. **`OPEN_FINDINGS.md`'s OF-57 row does not**, and its
three claims are measurably false against this review's own vectors:

| OF-57 says | measured |
|---|---|
| *"truncation is the one mutation the chain cannot see"* | **false** — V10, a re-derived suffix, verifies |
| *"deletion from the MIDDLE and **any alteration** break it and are DETECTED"* | **false** — a re-derived suffix is an alteration and is not detected |
| *"'tamper-evident' means **against modification**, and against deletion anywhere but the end"* | **false, and it is the ceiling sentence** — a re-derived suffix is a modification |

Neither OF-57 nor OF-61 contains the words *re-derived* or *suffix*. The row predates the second
shape's identification; the code caught up and the published row did not. **Ruling 4 is explicit:
*"DO fail it if any docstring, comment or artefact claims more than that."*** `OPEN_FINDINGS.md` is a
published artefact of the submission — `docs/reviews/README.md` says so in its first line — and this
is the sentence a C19 or C20 session copies into the README.

**Remedy:** a FIX session **appends** a correction row naming both shapes and restating the ceiling
in ruling 4's words. ⚠️ **OF-57's original text is not rewritten**: this directory is append-only and
*"a FAIL that is not in the repository did not happen"* applies to a wrong sentence as much as to a
verdict.

### §13.2 F-1 — the C7 card's seeded-defect clause, raised as ruling 2 requires

`PROCESS.md` §12.1's C7 row ends: *"**and the C7 review either raises the seeded defect as a BLOCKER
or the review process is declared broken and building halts**"*, and §5.4 says the architect writes
one into C7's build prompt. **The architect states directly that no C7 build prompt carried one** —
all three instructed the correct behaviour, in capitals — and the trap was pre-announced in
`PROCESS.md` §12.1, in `tests/goldens/README.md` and in golden 5's own `seeded_defect_note`, so it
could not have worked here in any case.

**The clause is therefore unsatisfiable as written**, and no review can satisfy a done-when whose
premise is absent. It is raised here so the correction lands through the record: §5.4's test **did
not run at C7**, the clause is corrected, and the test relocates to a chunk that is not named.
*A review fixes nothing; it names what must be fixed.*

⚠️ **AND THIS REVIEW'S FAIL MUST NOT BE READ AS THE SEEDED-DEFECT TEST PASSING.** The verdict rests
on B-1, B-2, H-1 and H-2, none of which is a planted defect. **The gate has gone red on its own
findings, which is weaker evidence than a planted red, and this review does not claim otherwise.**

### §13.3 R-01 — the read order and the seal

`CLAUDE.md` §1 makes `STATUS.md` item **4** of every session's mandatory read order, and this review
prompt's DO-NOT-READ list does not name it. Its C7 row narrates all three build rounds in detail —
`INC-32` through `INC-38`, the two `capture_payment` digests, the retired writer test, the mutant
counts. **A blind phase should not carry that.** The seal is blind to the **code** and not to the
build's own account of itself. Two things limit the damage and both are checkable: every figure in
this review is **re-derived** rather than quoted from that row, and the required set was argued from
`CONTEXT.md`, the C7 card and the rulings rather than from the row's list of what the build did.
**The finding is against the prompt and the read order, not against C7.** Remedy: either add the
chunk's own `STATUS.md` row to the Phase-1 DO-NOT-READ list, or scope Phase 1's `STATUS.md` read to
the state column.

---

## §14. REGRESSIONS, MEASURED BY THIS SESSION

| check | result |
|---|---|
| **full suite**, real repository, `PYTHONPATH=src python -m pytest tests/` | **786 passed, 1 failed, 1 skipped** in 233 s |
| the one failure, **attributed by file** | `tests/test_lanes_operator_placeholders.py::test_the_camel_branch_is_decided_before_any_camel_run` — **1 file, 1 test** |
| its reason | `UndeterminedValue: lanes.yaml: 'camel_comparator.branch' … sentinel 'TODO_C13_RUN1'` — **the expected pre-existing red, and NOT C7's** |
| `make selftest` | **RED on exactly that test**: `1 failed, 1 passed, 786 deselected` |
| `make check-roles` | **17 passed, 0 failed, 5 n/a, exit 0** — E1 clean over **50 token rows** |
| `make check-prereg` | `NOT-YET-FROZEN` — `PROTOCOL.md` is C14's and does not exist. Not a PASS; *"not yet"* |
| `git status --porcelain tests/goldens/` | **EMPTY** |
| `git status --porcelain vendor/` | **EMPTY** — all vendored pins clean |
| `evals/` | **does not exist in the working tree** — nothing was written to it |
| `git status --porcelain src/ tests/` | **EMPTY** throughout, before and after the mutation sweep |

**C7 contributes zero failures to the suite.** The single red is `camel_comparator.branch`, which is
C13/RUN-1's and is the state the prompt names in advance.

---

## §15. VERDICT

# ⚠️ FAIL.

**NO TAG. `c7-pass` IS NOT CUT.**

| PASS requires | obtained |
|---|---|
| all four golden-5 cases with their reasons | **yes** — A VALID/`null`, B DETECTED/2, C DETECTED/2, D DETECTED/1, reasons asserted |
| golden 5B's three digests by the reviewer's own computation | **yes** — all three, control passed first |
| golden 3's three | **yes** — 3, derived term by term |
| the reimplementation agreeing on all ≥20 vectors | **yes** — **45 vectors, 0 divergences** |
| **every REQUIRED-SET mutant killed or proven equivalent** | **NO** — **M12 and M39 survive on owned properties** |
| **ZERO BLOCKERS** | **NO** — **two: B-1 and B-2** |

**The chunk's behaviour is, on every measurement this review could make, correct.** The chain, the
verifier, the writer, the three refusal sources, the four consistency assertions, `productive_action`
term by term, the genesis refusal, the purity claims and the READ path all reproduce independently
from a reimplementation written before the code was opened; 35 of 39 required-set mutants die; and
the one survivor on the verifier's central property is **provably equivalent**.

**Three of the four gate failures are about what is PINNED or PUBLISHED rather than about what the
code DOES, and one is about a fixture this chunk may not touch.** Under Q-082's ruling and ruling 4
those are exactly the failures that hold a tag: *"clean today is exactly what an unpinned guard
cannot promise tomorrow"*, and *"DO fail it if any docstring, comment or artefact claims more than
that."*

**WHAT A FIX SESSION MUST NOT DO.** It must not touch `tests/goldens/` — **B-1 is the architect's
re-cut**. It must not rewrite OF-57's original row — **B-2 is a correction APPENDED**.

**GATE: B-1, B-2, H-1, H-2. NOT GATE: M-1 (`OF-143`), F-1, R-01.**
