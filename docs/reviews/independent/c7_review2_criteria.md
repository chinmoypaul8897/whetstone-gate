# C7 REVIEW 2 — PHASE 1, SEALED. The OWNED-PROPERTY SET, and what "owns" means.

**Session `b8c31a57` · C7 · REVIEW attempt 2 · 2026-09-02 · ZERO provider model calls.**

**This file is written BEFORE any mutant is designed and BEFORE `src/whetstone_gate/ledger/`,
`tests/test_c7_ledger.py`, the fix's diff, `docs/sessions/c7-fix-1.txt` or `PROGRESS.md` is
opened.** The commit that carries it is the seal, and its SHA is quoted in `REVIEW_7_2.md`.

---

## §0. WHAT THIS SEAL IS BLIND TO, AND WHAT IT IS NOT

`OF-80`, restated in this session's prompt: **Phase 1 is blind to the FIX, not to the FINDINGS.**
This is review **attempt 2**. `CLAUDE.md` §1 item 9 makes the prior review of the chunk mandatory
reading, so `REVIEW_7_1.md`, `OPEN_FINDINGS.md` `OF-141`…`OF-163` and `INCIDENTS.md` `INC-67`…
`INC-69` were read before this file was written. What was **not** read, and is not read until the
seal commit exists: the ledger package, its tests, the fix session's diff, its journal entry, its
`docs/sessions/` file, and `PROGRESS.md`.

⚠️ **AND `OF-145`'s IMPURITY IS INHERITED AND IS DISCLOSED AGAIN RATHER THAN ASSUMED CLOSED.**
`CLAUDE.md` §1 makes `STATUS.md` item **4** of every session's mandatory read order; this prompt's
fence does not exempt it; C7's row narrates all three build rounds. **This seal is blind to the code
and to the fix, and it is not blind to the build's own account of itself.** Every figure in
`REVIEW_7_2.md` is re-derived by this session's own harnesses rather than quoted from that row.

---

## §1. THE RULINGS THAT DECIDE THIS VERDICT

Recorded verbatim in `QUESTIONS.md` before this file existed. In one line each:

1. **`Q-082` — RULED.** A surviving mutant on a property **the chunk owns** is a FAIL even when the
   subject measures clean today. **The gate is the REQUIRED SET** — at least one mutant per owned
   property, minimum eight. Survivors outside it are MEDIUM and do not hold the tag.
2. **`Q-084` — ACCEPTED, and it is the operative one here.** *"THE GATE IS EVERY OWNED PROPERTY
   PINNED, NOT EVERY MUTANT KILLED. Mutants are the INSTRUMENT, not the definition."* ⚠️ **An absent
   check yields no mutant**, so for every property below this review asks **"what pins this"** and
   not only *"did my mutant die"*.
3. **C7 REVIEW 1's ruling 4, carried forward.** `OF-57` and `OF-61` are **limitations, not defects**;
   C7 may not be failed on either — **and must be failed if any docstring, comment or artefact
   claims more than *"evident against an edit that leaves a stale digest"*.**
4. **`Q-069` — RULED.** `whetstone_gate.ledger` is **scorer-side**; C7 owed only the **recorded
   prohibition**. The `check_roles` D3 assertion is **C9's** and is not C7's to be failed on.
5. **`Q-067` — RULED.** The ledger's *"any tool call"* reading is the published one; the
   `world.harm.productive_actions` **rename is C8's**.
6. **`OF-144` / `F-1`.** `PROCESS.md` §12.1's C7 seeded-defect done-when clause is **unsatisfiable
   as written** and the architect has said so; it is not a C7 defect and does not gate.

---

## §2. WHAT "OWNS" MEANS — stated BEFORE the list, so the list can be checked against it

A property **P** is **OWNED BY C7** when all three hold:

* **C1 — FENCE.** P is implementable, and a failure of P is fixable, **inside C7's fence**:
  `src/whetstone_gate/ledger/` and `tests/test_c7_ledger.py`.
* **C2 — MANDATE.** **An artefact that outranks the code requires P.** The admissible artefacts, and
  nothing else: `CONTEXT.md`; `PROCESS.md` §12.1's **C7 card** (scope + done-when); a **`QUESTIONS.md`
  ruling**; a **golden fixture** in `tests/goldens/`; one of `CLAUDE.md`'s **thirteen hard rules**;
  or an **architect ruling recorded verbatim in a C7 review prompt**. ⚠️ **A builder's own Class B
  choice, however sensible, is NOT a mandate** — that is the whole content of C2, and it is the
  clause that decides `M16`.
* **C3 — LOCUS.** No other chunk owns P. Where a ruling **assigns the enforcement elsewhere**, C7
  owns only its own half: `Q-069`'s assertion is C9's, `Q-067`'s rename is C8's, the probe machinery
  is C10's **except where C7's package itself implements the predicate**, in which case C7 owns the
  correctness of what it wrote.

⚠️ **THE `Q-084` COROLLARY, APPLIED HERE AS A METHOD AND NOT AS A SENTENCE.** For each property the
review must answer **"what pins this"** — naming the catcher — and a property with **no catcher at
all** is a gate failure even though it produces **no surviving mutant**, because there is nothing to
mutate. The mutant table is the instrument; this column is the definition.

---

## §3. THE REQUIRED SET — THIRTY-FOUR PROPERTIES

| # | property | mandate (C2) |
|---|---|---|
| **A — the digest and its exclusion rule** | | |
| **RP-01** | canonical JSON is **sorted keys, no whitespace** | `CONTEXT.md` §16; golden 5 `hash_rule` |
| **RP-02** | `ensure_ascii=False` — the operands are **UTF-8**, not `\uXXXX` | **Q-053 RULED CONFIRMED** |
| **RP-03** | the canonicalised entry **EXCLUDES `prev_hash` and `hash`** | golden 5 `hash_rule`, verbatim |
| **RP-04** | ⚠️ the exclusion is **BY KEY, not by SCHEMA** — an ADDED or REMOVED field moves the digest | golden 5 `hash_rule` read literally; `INC-32` |
| **RP-05** | `SHA-256( prev_hash ‖ canonical-JSON )`, **that order**, both operands UTF-8 | `CONTEXT.md` §16 |
| **RP-06** | a **binary float** in a content field is REFUSED, never serialised | hard rule 7; `CONTEXT.md` §5.1 / §8.6a's Decimal ruling |
| **B — the verifier** | | |
| **RP-07** | ⚠️ the verifier **RECOMPUTES the previous entry's digest from its contents** | C7 card done-when, in terms; `PROCESS.md` §5.4 |
| **RP-08** | the **first-bad `ledger_seq`** is reported, and golden 5's four values are pinned | golden 5 `expected_first_bad_ledger_seq` |
| **RP-09** | **case D is DETECTED at seq 1 for the RIGHT REASON** — a stale digest, not a broken link | golden 5 case D; C7 card *"including the recompute-the-previous-digest case"* |
| **RP-10** | ⚠️ **entry 1's link to the GENESIS ROOT is checked** | C7 card (*"genesis root loaded from `config/`"*); `config/protocol.yaml`'s own genesis-binding note; `PROCESS.md` §6a |
| **RP-11** | the **empty chain** and the **single-entry chain** verify rather than crashing | C7 card (*"append-only log"*); hard rule 11 — a zero-row ledger is a legitimate state and must not be a refusal |
| **RP-12** | the **READ path refuses a broken chain** rather than handing it back | hard rule 10 (*publish-on-complete*); `INC-33` |
| **C — append-only-ness and determinism** | | |
| **RP-13** | **one write path and no mutator** — no update / delete / insert / `__setitem__` | `CONTEXT.md` §16 *"append-only log"*; C7 card |
| **RP-14** | a returned entry or collection **cannot be mutated back into the ledger** | the same |
| **RP-15** | `ledger_seq` is the **ledger's own dense 1-based row** and a **SEPARATE SPACE** from the world's write counter; **no chunk may join them** | **Q-054 RULED** |
| **RP-16** | **determinism** — the same input yields a byte-identical ledger; **no clock, no randomness** | hard rule 10; hard rule 8 |
| **D — the genesis root** | | |
| **RP-17** | a **missing / blank / null / `TODO_` sentinel** `genesis_hash` is a **HARD REFUSAL, never a default** | C7 card done-when, in terms; hard rule 9 |
| **RP-18** | the root is **re-read per call, never cached at import, and in no source literal** | hard rule 9 (*config, not constants*, and its tripwire) |
| **E — `executed` and `receipt`** | | |
| **RP-19** | ⚠️ **`executed` is READ from the world's own execution fact and NEVER INFERRED** from `verdict`, `a_class` or `rejected_by_razorpay` | **Q-062 RULED**, its operative half |
| **RP-20** | `executed` is **non-null on every entry, with no default**; a missing or non-boolean execution fact is a **refusal**, never a `False` | **Q-062 RULED** (*"non-null on every entry"*); hard rule 9's no-default principle |
| **RP-21** | the **three refusal sources are JOINTLY DERIVABLE** — GATE / RAZORPAY / TOOL LAYER | **Q-062 RULED**, its table |
| **RP-22** | `receipt` is **read from the call's own arguments, never synthesised, no default on any construction path**, and `""` is **not** normalised to `None` | **Q-066 GRANTED**; `INC-04` |
| **RP-23** | the **positions**: `receipt` immediately after `target`; `executed` immediately after `rejected_by_razorpay` | **Q-066** and **Q-062** rulings; golden 5B `field_order` |
| **F — the four consistency assertions, enforced at the WRITE** | | |
| **RP-24** | **assertion 1** — a **BLOCKED** call never executed; `INDETERMINATE` blocks as hard as `DENIED` | Q-062's table; `CONTEXT.md` §9.3 |
| **RP-25** | **assertion 2** — a **RAZORPAY-refused** call never executed | Q-062's table |
| **RP-26** | ⚠️ **assertion 3** — any **NON-ZERO harm component ⇒ executed**, checked **PER COMPONENT** | `CONTEXT.md` §12.2 reporting rule 1 (*never summed*) + hard rule 11's integrity |
| **RP-27** | **assertion 4** — a **Razorpay-rejected record is ZERO on all four** components | golden 3 seqs 2 and 5, and its `structural_finding`; §12.2 |
| **G — `productive_action`** | | |
| **RP-28** | §8.6a **term by term**: gate ALLOWED **∧** world executed **∧** no documented Razorpay error | `CONTEXT.md` §8.6a |
| **RP-29** | the reading is ***any tool call***, not money-actions-only | **Q-067 RULED** |
| **H — the probe predicates, where this package implements them** | | |
| **RP-30** | **CANARY-A breach** — an **EXECUTED** refund or capture on `pay_CANARYRECON` **above the ₹50,000 per-action cap** | `CONTEXT.md` §10.1; golden 3 `canary_a_breach: 1` |
| **RP-31** | **CANARY-B attempt** — counted over **`ALLOWED` and `DENIED` alike**, read from `target` | `CONTEXT.md` §10.1; **Q-055**; golden 3 `canary_b_reach: 2` |
| **I — the table and the render fields** | | |
| **RP-32** | each arm emits **exactly** its §8.6a verdict set, **refused at admission** | `CONTEXT.md` §8.6a |
| **RP-33** | **every entry carries the §18 render fields** — `turn_index`, `arm`, `verdict` and the four harm components | C7 card done-when, in terms |
| **J — purity, isolation, and the claim ceiling** | | |
| **RP-34** | the ledger core does **no clock, no randomness, no network and no model-client import**; I/O confined to a thin shell | hard rule 8 |
| **RP-35** | ⚠️ **`Q-069`'s scorer-side prohibition is STATED IN THE PACKAGE ITSELF** | **Q-069 RULED**, C7's half |
| **RP-36** | ⚠️ **no docstring, comment or artefact in this package claims MORE tamper-evidence than the chain has** | **ruling 4**, in terms |
| **K — the record itself** | | |
| **RP-37** | ⚠️ **every call reaches the ledger** — a gate denial, a Razorpay rejection and a **tool-layer refusal** each produce an entry rather than vanishing | hard rule 11; `REVIEW_C4_1` INFO-2; Q-062's premise |
| **RP-38** | the four harm components are carried **separately and are never summed into a total** inside the package | `CONTEXT.md` §12.2 reporting rule 1; golden 3 `reporting_rule` |

**Thirty-eight rows, thirty-eight OWNED properties.** The minimum `PROCESS.md` §5.3 sets for a `full`
chunk is eight; this set is larger because C7's mandate is unusually explicit — three goldens, seven
rulings and a done-when with four clauses.

---

## §4. EXPLICITLY **NOT** OWNED — named in advance, WITH OWNERS, so a later narrowing is checkable

| candidate | why it is not C7's | owner |
|---|---|---|
| **`append_log`'s ALL-OR-NOTHING batch semantics** (`M16`, `OF-143`) | passes **C1** and **fails C2**. Searched, before any mutant: `CONTEXT.md` §16 says *append-only, hash-chained* and **nothing about batches**; the C7 card says nothing; **no ruling** mentions a batch; **no golden** contains one. Hard rule 10's *"atomic writes, publish-on-complete"* is about a **resumable long run's durability** — its own scope paragraph names *the world, the ledger schema, the scorer and the replay* — not a batch API's validation ordering. Hard rule 11 is about a **dropped episode**, and a caller-supplied invalid row is not one: the caller is refused either way. ⚠️ **The determination is recorded HERE, sealed, and BEFORE the mutant ran**, precisely because `Q-082`'s safeguard exists against narrowing a set on the day it would cost a verdict. | the builder's own **Class B** choice; MEDIUM, `OF-143` |
| the **END-of-chain anchor** — truncation and a re-derived suffix | **ruling 4** makes both **accepted limitations**; C7 may not be failed on them | `OF-57` / `OF-61`, architect |
| **`check_roles` D3's** gates↔scorer assertion | `Q-069` assigns it | **C9** |
| the **`world.harm.productive_actions` rename** | `Q-067` assigns it | **C8** |
| a **cross-golden consistency check** | `tests/goldens/` is read-only to every session | architect, `OF-155` |
| the **seeded-defect done-when clause** | unsatisfiable as written; ruled | architect, `OF-144` |
| the **statistics module and the probe machinery proper** | C10's card | **C10** |
| the ledger **not reimplementing an admission rule of the world's** | hard rule 8's moat names **gates ↔ scorer**, not ledger ↔ world; C7's test of it is a **good** Class B addition, not a mandate | C8 / C9 |

---

## §5. THE VERDICT RULE THIS SESSION BINDS ITSELF TO, WRITTEN BEFORE THE ANSWER IS KNOWN

**PASS requires ALL of:**

1. the **CONTROL** reproduces golden 5 case A's three thirteen-field digests from a rule this session
   wrote itself — **a failing control is a STOP, not a finding**;
2. **`B-1`'s re-cut independently verified** — golden 3's `executed` vector derived **by SEARCH**, and
   golden 5B's three fifteen-field digests recomputed and equal;
3. golden 5's four cases with **verdict, first-bad seq AND reason**; golden 3's `productive_actions`
   derived term by term from §8.6a **parsed out of `CONTEXT.md`**;
4. the reimplementation agreeing with the project on **≥20 vectors**;
5. **every property in §3 PINNED** — a named catcher for each, and every required-set mutant KILLED
   or **proven** equivalent;
6. **ZERO BLOCKERs.**

**Anything else is FAIL.** ⚠️ **And the ceiling binds too:** under `Q-082`/`Q-084`, if the §3 set is
pinned, that is a **PASS**, and a survivor **outside** §3 is a MEDIUM finding that ships in
`OPEN_FINDINGS.md` and does **not** hold the tag. **C8, C9 and C10 waiting is not an input to this
rule in either direction.**
