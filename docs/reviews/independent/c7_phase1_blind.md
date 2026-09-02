# C7 REVIEW 1 (`472cdc4b`) — PHASE 1, BLIND. THE REQUIRED SET, ENUMERATED AND ARGUED.

**Sealed before a single mutant was written, and before anything under `src/whetstone_gate/ledger/`
or `tests/test_c7_ledger.py` was opened.** That ordering is the whole point of the file:

> `QUESTIONS.md` **Q-082**, as this session's prompt carries it: *"the required set is WORTHLESS IF
> CHOSEN AFTER SEEING THE RESULT — that is the same regress with an extra step. ENUMERATE AND ARGUE
> THE OWNED PROPERTIES IN THE SEALED PHASE 1, BEFORE WRITING A SINGLE MUTANT. Phase 2 may ADD a
> member with an argument; it may never REMOVE one."*

**THE GATE, from Q-082's ruling:** at least one mutant per property or invariant **the chunk owns**,
minimum eight (`PROCESS.md` §5.3). A survivor **inside** this set is a FAIL. A survivor **outside**
it is a MEDIUM finding in `OPEN_FINDINGS.md` and does not hold the tag.

---

## What "OWNS" means here, stated before the list so the list can be checked against it

A property is **OWNED BY C7** when all three hold:

1. **C7 is the chunk that implements it.** Not C4's world, not C8's scorer, not C10's probe
   machinery. The test is: if this behaviour is wrong, is the fix inside `src/whetstone_gate/ledger/`?
2. **An artefact that outranks the code fixes it** — `CONTEXT.md`, `PROCESS.md` §12.1's C7 card,
   a `QUESTIONS.md` ruling, or a golden. A property C7 invented for its own convenience is not owned;
   it is a Class B implementation choice.
3. **Getting it wrong changes a published number, a stored document, or a refusal** — rather than
   changing only a message.

Where a property fails (1) it is marked **NOT OWNED** below **with its owner named**, so a Phase-2
survivor on it can be dispositioned without re-arguing.

---

## THE REQUIRED SET — THIRTY-TWO PROPERTIES

`PROCESS.md` §5.3's floor is eight. This is four times it, and the reason is that C7 is the chunk
every published number is replayed from: C8, C9 and C10 all read this ledger, and a defect here is
not visible in any of them as a defect — it is visible as a number.

### Group A — the chain digest and its exclusion rule (`CONTEXT.md` §16, golden 5's `hash_rule`)

| # | Property | Why C7 OWNS it |
|---|---|---|
| **P-01** | The canonicalisation is **sorted keys, no whitespace** | `CONTEXT.md` §16 gives the rule in those words. Key order or a separator space changes every digest in the repository. |
| **P-02** | `ensure_ascii=False` | `QUESTIONS.md` **Q-053, RULED CONFIRMED**. Q-053's own argument is that the two readings differ on **reachable** input — `target` and `receipt` carry attacker-authored text at temperature 0.7 — so this is a value, not a style. |
| **P-03** | The canonicalised entry **EXCLUDES `prev_hash` and `hash`** | golden 5's `hash_rule` field, verbatim. Including either makes the digest self-referential and no chain can ever verify. |
| **P-04** | The exclusion is **by key, not by schema**: a smuggled extra key, or a deleted content key, **moves the digest** | This is what makes one verifier correct at golden 5's thirteen fields and at golden 5B's fifteen. A canonicaliser over a **fixed field list** returns VALID on a sixteenth key — and **golden 5 has no case that would catch it**, so the golden cannot be the reviewer's only instrument here. |
| **P-05** | `SHA-256( prev_hash ‖ canonical-JSON )`, **both operands as UTF-8 strings**, in that order | `CONTEXT.md` §16 and golden 5's `hash_rule`. Concatenating the other way round, or hashing bytes of the digest rather than of the hex string, produces a chain no external reviewer can reproduce — and §6a.3 exists for exactly that reader. |

### Group B — the verifier (`PROCESS.md` §5.2 golden 5, §5.4)

| # | Property | Why C7 OWNS it |
|---|---|---|
| **P-06** | The verifier **RECOMPUTES the previous entry's digest from its contents** and never compares stored field to stored field | `PROCESS.md` §5.2 golden 5 names this in terms as the mutation revision 1 would not have caught, and §5.4 names the same sentence as the seeded defect. It is the single most load-bearing line in the chunk. |
| **P-07** | The verifier returns the **first-bad `ledger_seq`**, and golden 5 pins four of them: A VALID/`null`, B DETECTED/**2**, C DETECTED/**2**, D DETECTED/**1** | The golden states them. **Case D at 1 rather than 2 is the whole discrimination** — a verifier that checked integrity only from entry 2 onward would return 2 and look right. |
| **P-08** | Case D is DETECTED **for the right reason** — entry 1's own recomputed digest disagrees with its stored `hash` — and not because of some other accident | A right verdict for a fabricated reason is a false pass on the one case that tests the review gate itself. This is asserted, not assumed. |
| **P-09** | An **empty chain** is VALID with first-bad `null`, and a **single entry** chains from the genesis root | The two degenerate shapes. A verifier that indexes `entries[i-1]` unguarded crashes on the first; one that skips entry 0 never checks the genesis link at all. |
| **P-10** | The **READ path refuses a broken chain** — loading a ledger does not re-hash whatever it is handed and hand back a valid object | A reader that recomputes and **overwrites** the stored digests launders golden 5's cases B, C and D into valid ledgers. The store is C7's; nothing downstream can detect this. |

### Group C — append-only-ness and the sequence (`CONTEXT.md` §16, Q-054)

| # | Property | Why C7 OWNS it |
|---|---|---|
| **P-11** | The log is **APPEND-ONLY**: no public update, delete, insert or reorder | `CONTEXT.md` §16 calls it a *"hash-chained append-only log"*, and `CLAUDE.md` §4 makes `evals/` append-only to every session. |
| **P-12** | `ledger_seq` is the **dense 1-based ledger row** and is a **separate space** from the world's write counter | `QUESTIONS.md` **Q-054, RULED**: *"NO CHUNK MAY JOIN THEM ON THAT KEY"*, with the divergence measured at harm records [1,2] against entries [1,2,3]. §12.2 uses `ledger_seq` as the de-duplication key, so a wrong assignment moves a **published** money figure by rule 3. |
| **P-13** | Appending is **idempotent in the sense hard rule 10 requires** — the same inputs in the same order give byte-identical digests, every time, with no clock and no randomness anywhere in the path | Hard rule 10 *claims and tests* that the ledger schema and the replay are byte-identical from the same seed. |

### Group D — the genesis root (`PROCESS.md` §12.1's C7 done-when, hard rule 9)

| # | Property | Why C7 OWNS it |
|---|---|---|
| **P-14** | A **missing `ledger.genesis_hash` is a HARD REFUSAL**, never a default and never a silent fallback | The C7 card's done-when says so in those words; hard rule 9 says *"no default for a required value"*. |
| **P-15** | The root is **RE-READ PER CALL and never cached**, and appears in **no non-docstring literal** in the package | `config/protocol.yaml`'s own comment: *"A ledger cannot contain the hash of a tag that did not exist when it was written, so pre-freeze episodes are CRYPTOGRAPHICALLY DISTINGUISHABLE from scored ones."* A cached or hardcoded root destroys exactly that proof, and it destroys it **silently**. |

### Group E — `executed`, its three sources, and `receipt` (Q-062, Q-066, Q-068)

| # | Property | Why C7 OWNS it |
|---|---|---|
| **P-16** | `executed` is **READ FROM THE WORLD'S OWN `ToolResult.ok`** and **NEVER INFERRED** from `verdict` and `rejected_by_razorpay` | Q-062's ruling: *"`executed` is TRUE if and only if the world ACTUALLY PERFORMED the action"*. The inference **cannot see the tool-layer refusal, which is the whole finding**, and a ledger that re-derived the world's admission rules would make the two agree by construction — hard rule 8, one package along. |
| **P-17** | Source **GATE** is derivable: `executed` false, `verdict` DENIED or INDETERMINATE | Q-062's table, row 1. |
| **P-18** | Source **RAZORPAY** is derivable: `executed` false, `rejected_by_razorpay` true | Q-062's table, row 2. |
| **P-19** | Source **TOOL LAYER** is derivable: `executed` false, `verdict` ALLOWED, `rejected_by_razorpay` false — **the row that was previously indistinguishable from success** | Q-062's table, row 3, and the measurement that produced the ruling: two `capture_payment` entries on seed 2001, one that moved ₹665.23 and one the MCP layer refused, **byte-identical with the same hash**. |
| **P-20** | `receipt` is **read from the call's own arguments**, **never synthesised**, and has **no default on any construction path** | Q-066, GRANTED. `None` is the claim that makes S2 unfireable, so a default of `None` would silently delete a scored invariant. |

### Group F — the four consistency assertions (`CONTEXT.md` §12.2)

| # | Property | Why C7 OWNS it |
|---|---|---|
| **P-21** | **Assertion 1** — a call the gate BLOCKED never executed. `INDETERMINATE` blocks exactly as hard as `DENIED` | `CONTEXT.md` §9.3. An entry with `verdict: DENIED, executed: true` is a contradiction the ledger must refuse to write, not record. |
| **P-22** | **Assertion 2** — a call Razorpay refused never executed | §12.2: the money never moved. |
| **P-23** | **Assertion 3, THE INTEGRITY ONE** — **any non-zero harm component implies `executed`**, checked **PER COMPONENT and never against a total** | *Money cannot move on a call that did not happen.* §12.2 reporting rule 1 forbids summing the four, and a sum-based check passes three of the four single-component violations. This is the assertion that is an integrity check rather than a restatement of 1 and 2. |
| **P-24** | **Assertion 4** — a record with `rejected_by_razorpay == true` contributes **ZERO to all four** harm components | §12.2, verbatim. It is also what keeps such a record counting toward CANARY-B reach and the productive-action confound without inflating a money figure. |

### Group G — `productive_action`, term by term (`CONTEXT.md` §8.6a, Q-067)

| # | Property | Why C7 OWNS it |
|---|---|---|
| **P-25** | **Term 1** — the gate **ALLOWED** it | §8.6a: *"A blocked call … is non-productive."* |
| **P-26** | **Term 2** — the world **EXECUTED** it | §8.6a: *"that the world executed"*. This term did not exist before Q-062 and is the reason the ruling was needed. |
| **P-27** | **Term 3** — **no documented Razorpay error** was returned | §8.6a: *"A … Razorpay-rejected call [is] non-productive."* |
| **P-28** | The reading is **`any tool call`** — the word *money* is absent, so an executed **read** counts | `QUESTIONS.md` **Q-067, RULED: the ledger's reading is the published one.** This is the term that makes `world.harm.productive_actions` (world-side **1**) disagree with the ledger (**3**) on a four-call episode; C8 renames the world's. |

*Why all four are separate members rather than one:* `INC-35` records a test named *term by term*
that could not discriminate two of the three terms, and two mutants survived it. A single
"productive_action is correct" member would rebuild that.

### Group H — the arm/verdict table and the render fields (`CONTEXT.md` §8.6a, the C7 card)

| # | Property | Why C7 OWNS it |
|---|---|---|
| **P-29** | Each arm emits **exactly** its §8.6a verdict set and the ledger **refuses** anything else — arm 1 → `ALLOWED` only; 2/2S/3 → `ALLOWED`/`DENIED`; 4 → **+** `INDETERMINATE` | §8.6a states the sets. C9 builds the gates, but **C7 is the substrate that records the verdict**, and its card puts `verdict` on every entry. ⚠️ **Shared with C9** — C9 owns *emission*, C7 owns *admission*. Marked owned for C7 on the admission half only. |
| **P-30** | The **render fields are present on every entry** — `turn_index`, `arm`, `verdict` and the four harm components | The C7 card's done-when, in terms, *"so the §18 replay renderer is buildable from `evals/episodes/` alone"*. C17 cannot add a field to a chain that is already hashed. |

### Group I — the purity and isolation properties (`CLAUDE.md` hard rules 8 and 10, Q-069)

| # | Property | Why C7 OWNS it |
|---|---|---|
| **P-31** | **No clock, no float, no randomness, no network, no model client** anywhere in the ledger; every money quantity an **integer paise** | `CLAUDE.md` hard rule 8 and `CONTEXT.md` §5.1. A float harm component is a wrong published number that no test of the chain would ever see. |
| **P-32** | **Q-069's prohibition is recorded in the package itself**, where a C9 session writing `from whetstone_gate.ledger import …` reaches it first | Ruling 3 of this session's prompt: *"C7 was required only to record the prohibition where a C9 session will hit it."* ⚠️ **The ENFORCEMENT is C9's** — `check_roles` D3 — and is explicitly **NOT OWNED** by C7. What C7 owns is that the sentence is **there**, asserted by parsing rather than by trusting. |

---

## The three properties this review will NOT hold C7 to, named in advance

| Not owned | Owner | Why |
|---|---|---|
| **The END of the chain is anchored** — truncation and a re-derived suffix both verify | **accepted and published as a limitation** | Ruling 4 of this session's prompt: `OF-57` and `OF-61` are **limitations, not defects**, and C7 must not be failed on either. What C7 **is** held to is that no docstring, comment or artefact claims more than *"evident against an edit that leaves a stale digest"* — and that claim-check is P-33 below. |
| **`check_roles` D3 asserts `gates/` never imports the ledger** | **C9** | Q-069's ruling assigns the assertion to C9. No gate exists; D3 reports `n/a`. |
| **`world.harm.productive_actions` is renamed** | **C8** | Q-067's ruling assigns the rename to C8 and says C7 does not touch `world/`. |

| # | Property | Why C7 OWNS it |
|---|---|---|
| **P-33** | **No artefact of C7 claims more about tamper-evidence than *"evident against an edit that leaves a stale digest"*** | Ruling 4, second half, in terms: *"DO fail it if any docstring, comment or artefact claims more than that."* An overclaim here is the exact failure mode `INCIDENTS.md` INC-05 made a rule about, in a document whose subject is overclaims. |

**THIRTY-THREE MEMBERS.** `PROCESS.md` §5.3's floor is eight.

---

## What Phase 2 is permitted to do to this list

**ADD** a member, with an argument written beside it. **NEVER REMOVE** one. If a member turns out to
be unownable — because the behaviour lives in another chunk — it is **re-marked NOT OWNED with its
owner named**, and that re-marking is itself argued in `REVIEW_7_1.md`, because "it turned out not to
be ours" is the sentence a reviewer reaches for on the day a mutant survives.
