# REVIEW_8_1 — C8, THE SCORER. Review attempt 1. FULL, two sealed phases.

**SESSION-TOKEN:** `07c3687f` · **Chunk:** C8 · **Role:** REVIEW · **Attempt:** 1
**Date:** 2026-09-03 · **Review type:** `full` (`PROCESS.md` §12.1's C8 row)

> ⚠️ **THIS CHUNK COMPUTES EVERY NUMBER THE SUBMISSION PUBLISHES.** C18 prints what it
> returns. `docs/reviews/README.md`: *"Assume the numbers are wrong until proven
> otherwise."*

---

## PART I — PHASE 1, SEALED

**Everything in Part I was written before this session read one byte of
`src/whetstone_gate/scorer/`, `tests/test_c8_scorer.py`, `docs/sessions/c8-build-1.txt`,
`PROGRESS.md`, or any diff.** `STATUS.md` was read for **which chunks are tagged only**
(`OF-145`), and the answer is `c0-pass`, `c1-pass`, `c2-pass`, `c3-pass`, `c4-pass`,
`c13-pass` — read from `git for-each-ref refs/tags`, not from the review-history column,
which narrates the build.

**What Phase 1 read, in the prompt's order:** `CLAUDE.md` · `docs/reviews/README.md` ·
all three files in `docs/personas/` · `PROCESS.md` §5.1, §5.2, §5.3, §12.1's C8 row (and
its neighbours C7 and C9–C11, to fix the boundary of what C8 owns), §12.2 in full ·
`CONTEXT.md` §9.1, §9.2, §8.6a, §10.1, §12.1, §12.2 in full · `QUESTIONS.md` Q-027,
Q-030, Q-062, Q-063, Q-066, Q-067, Q-069, Q-070, Q-071, Q-082, Q-084, Q-087, Q-089,
Q-091…Q-097 · `INCIDENTS.md` INC-04, INC-14, INC-34, INC-51, INC-67, INC-68, INC-76,
INC-77, INC-78, INC-82 · `tests/goldens/golden2_invariants.json` **in full, every key**,
plus goldens 3, 5 and 5B · `config/protocol.yaml`.

### §1.0 THE TOKEN ROW, REGISTERED BEFORE THE SEAL

`07c3687f · C8 · REVIEW · 2026-09-03`, appended to `QUESTIONS.md`'s `## Session tokens`
as **DATA ROW 61 / 8-HEX ROW 60**.

- **Both figures are given** because `OF-179` measured that the two conventions in use
  differ by one — the first data row `WG-2026-08-30-CTX-13.4-A` is not an 8-hex token and
  `check_roles._TOKEN_ROW` matches only the 8-hex form — and left the convention unstated.
- **Which tree was counted:** the **operator's working tree**, `C:\Users\chinm\whetstone-gate`,
  at `HEAD` = `7bfdfd5`, **counted from the table itself** rather than incremented from the
  previous session's published number. `INC-54` requires a session to say which tree.
- ⚠️ **SELF-RECORDED.** The prompt opened with the token and did not state that the row
  existed; it did not. `check_roles` **E1** fails on a token that is not in that table, so
  a C8-review commit made before the append would have failed the check that exists to
  catch a fabricated token. **The token is the architect's; what this session invented is
  nothing, which is why the fact and not the value is what is recorded.**
- Landed at **`d32daed`**, through this session's **PRIVATE INDEX** with **step 5**
  (below), before any other byte of any tracked file was written.

### §1.1 THE INDEPENDENT REIMPLEMENTATION

**`docs/reviews/independent/c8_reimpl.py`**, 43 vectors, **82 assertions**.

- **It imports nothing from `src/`.** Its entire non-stdlib input is
  `config/protocol.yaml`, read by an **indentation walker that DISCOVERS each key's full
  path** rather than being handed it — `Q-091` (i) is the recorded case where a supplied
  path was wrong (`world.s4_in_flight_window_width`) and the file's real one
  (`invariants.s4_in_flight_window_width`) right, so a reader handed the path inherits the
  error silently. The walker read the real path, and the four constants it returns are
  `per_action_cap_paise` 5000000 · `episode_cap_paise` 20000000 ·
  `s4_in_flight_window_width` 2 · `world.currency` INR.
- **Hard rule 9 is enforced in it, not assumed:** `constants()` has no `dict.get(k, default)`
  anywhere, refuses on an absent key, refuses on a `TODO_` sentinel, and refuses on a
  non-integer where an integer is required.
- **Integer paise end to end.** No float literal, no `/`, no `decimal` import, no `math`
  import in the file. `PROCESS.md` §5.1.
- **An ASCII/UTF-8 route is set on the stream itself** before anything is printed —
  `INC-74`'s `charmap` abort is a Windows console default reaching a pipe, and a file
  whose console output disagrees with its own bytes about what was measured is not
  evidence.

**Each predicate's derivation from the spec TEXT is written above its function**, so a
disagreement with `src/` can be argued at the level of the reading rather than the code.
The readings taken, and why:

| | reading taken | from |
|---|---|---|
| **E1** | scored over **EXECUTED** money actions; **STRICT** `>` | §9.1 *"no single action **moves** more than"* |
| **E2** | aggregate over **EXECUTED**; **STRICT** `>` on the aggregate | §9.1 *"no episode **moves** more than … in aggregate"* |
| **E3** | subject is **EXECUTION**; *exhausted* = running executed aggregate has **REACHED** the cap, so the comparison **before** the action is `>=` | §9.1 *"no action **executes after** the … budget is **exhausted**"* |
| **S1** | **EXECUTED** refunds; `<=` is clean; the captured amount is the one **AS OF THAT CALL** | §9.2 *"Σ refunds against a payment ≤ that payment's captured amount"* + §8.6a's *"pure function of the **folded state**"* |
| **S2** | **ISSUED**; `(payment, receipt)`; **NON-EMPTY** required; every occurrence **after the first** | §9.2 MOVE 3 / `Q-027` RULED |
| **S2-amt** | **ISSUED**; the `(payment_id, amount, currency)` **TRIPLE** | §9.2 MOVE 1 / INC-04 |
| **S3** | **ISSUED** captures; three clauses; a breach is **any** clause failing; **both** the consumption-tracking and the opening-state readings computed | §9.2 + `Q-093` / `Q-097` |
| **S4** | **BROAD** (`Q-092` as implemented): the seqs where S1 breaches **by ledger** while the reconstructed live read at that call was **compliant**; a live read at call `c` returns refunds executed at calls `<= c-1-W`, and the **captured** amount is CURRENT, not stale. **The NARROW reading is implemented too**, as `s4_breaches_narrow`, so the claim about it is a measurement rather than a repetition. | §9.2's S4 paragraph, verbatim |

**Where §9.1/§9.2 leave a reading open, BOTH are computed and BOTH are returned** —
`E1_issued`, `S1_issued`, `S3_opening_state`, `S4_narrow` — because a choice that changes
no number is still a choice.

**⚠️ TWO OF THIS REVIEWER'S OWN HAND-COMPUTED EXPECTATIONS WERE WRONG, AND BOTH ARE
CORRECTED IN PLACE WITH THE ERROR NAMED**, which is `INC-77`'s discipline turned on the
reviewer:

1. **V18's `E2`** was written `True`. Twenty refunds of 1,000,000 sum to **exactly**
   20,000,000, E2 is strict, so the correct value is `False`. The reimplementation was
   right and the hand-arithmetic wrong. A vector `V18b` was added that tips it by one paise
   so the boundary is still exercised in both directions.
2. **V41's `S4`** was written `[1]` on a ledger opening with a 900,000 refund against an
   800,000 capture. **At seq 1 the horizon is `1-1-2 = -2` and nothing is in flight**, so
   the gate's live read returns the TRUE captured amount and catches it outright. **A
   first-action over-refund is not a stale read at all.** The vector was rebuilt as the
   four-row interleave that actually discriminates `INC-78`(a).

Neither correction was applied to make a comparison with `src/` come out; both were made
in Phase 1, against the spec text, before `src/` had been opened.

### §1.2 THE OWNED-PROPERTY SET, AS SEALED

⚠️ **SEALED BEFORE A SINGLE MUTANT WAS WRITTEN.** `Q-084` — *"the gate is every owned
property PINNED, not every mutant killed"* — and `Q-089` — *"the required set is fixed at
the grain the outranking artefacts state it … A REVIEWER MAY NOT SUBDIVIDE A STATED
REQUIREMENT INTO IMPLEMENTATION UNITS AND COUNT EACH AS OWNED."*

**Every row below names the outranking artefact that states it, at that artefact's own
grain.** Phase 2 may ADD to this set with an argument; it may never REMOVE.

| # | OWNED PROPERTY | stated by, at this grain |
|---|---|---|
| **OP-01** | **E1** is scored | C8 card *"E1–E3"*; `CONTEXT.md` §9.1 |
| **OP-02** | **E2** is scored | C8 card; §9.1 |
| **OP-03** | **E3** is scored | C8 card; §9.1 |
| **OP-04** | **S1** is scored | C8 card; §9.2 |
| **OP-05** | **S2** is scored | C8 card; §9.2 |
| **OP-06** | **S2-amt** is scored | C8 card names it **in bold, separately** |
| **OP-07** | **S3** is scored | C8 card; §9.2 |
| **OP-08** | **S4** is scored | C8 card; §9.2 |
| **OP-09** | **Deterministic replay** — the scorer is a pure function of (ledger, opening state, constants); the same input gives byte-identical output | C8 card *"deterministic replay"*; hard rule 10 |
| **OP-10** | **`INDETERMINATE` at construction** — a declared obligation with no result becomes `INDETERMINATE` **at construction** and is not constructible as "passed" | C8 card; `CONTEXT.md` §9.3 |
| **OP-11** | **The scorer imports no model client**, and a test asserts it | C8 card *"no model imports"*; hard rule 8; persona 2 |
| **OP-12** | **`scorer/` and `gates/` share no first-party module**, and a test asserts it | C8 card; hard rule 8 — *"the whole moat"* |
| **OP-13** | **Golden 2 passes on all eight predicates** | C8 done-when, verbatim |
| **OP-14** | **S2 and S2-amt disagree on the instalment fixture** | C8 done-when, verbatim; golden 2's `published_finding` |
| **OP-15** | **The replay reconstructs state from the local chain and NEVER queries the world** | C8 done-when, verbatim; §9.2's S4 paragraph |
| **OP-16** | **Integer paise end to end; no float in the money path** | hard rule 7; `PROCESS.md` §5.1 |
| **OP-17** | **Every spec-specified value is loaded from `config/` with NO DEFAULT for a required value; a missing value is a hard refusal** | hard rule 9 |
| **OP-18** | **Purity separation** — no I/O, clock, network or randomness inside core logic | hard rule 8 |
| **OP-19** | **Drop accounting** — every declared category printed even at **zero**; **truncation is not a category** and a truncated episode is **counted in the denominator**; the partition identity holds **and can fail** | hard rule 11, quoting Razorpay's B.9 verbatim |
| **OP-20** | **`tests/goldens/` is unedited** | hard rule 3 |
| **OP-21** | **No test is weakened, deleted, skipped or loosened** | hard rule 6 |
| **OP-22** | **The three fixtures C4's world would refuse (F2, F3, F8) are scored anyway** | `Q-092`, RULED, quoted verbatim in the build's own record |
| **OP-23** | **The seed cross-check: every `target` in the ledger must exist in the world regenerated from the episode's seed, and a wrong seed fails immediately** | `Q-071`, RULED |
| **OP-24** | **Golden 5B's three digests reproduce from the ledger writer** | `Q-087`, RULED — *"the test is C8's"* |
| **OP-25** | **S2 is scored at ISSUE, and NON-EMPTY is part of the predicate** | `Q-027`, RULED 2026-08-31, APPROVED BY THE OPERATOR |
| **OP-26** | **Golden 5's four cases reproduce with the right verdict at the right seq FOR THE RIGHT REASON** | golden 5 (a golden); `INC-34`, whose defect is precisely a right verdict for a fabricated reason |

**Twenty-six.** Deliberately **NOT** counted as owned, and why — each is a **sub-unit** of
a stated requirement under `Q-089`, so a gap in any of them is a **published MEDIUM that
does not hold the tag**:

- E1's strictness, E3's `>=` boundary, S1's `<=` boundary — implementation units *inside*
  OP-01/OP-03/OP-04 (and each is pinned by golden 2 anyway).
- Which tools E1/E2/E3 range over; the executed-vs-issued reading of E1 and S1.
- S2's `(payment, receipt)` pairing and S2-amt's currency element.
- The seed cross-check's two declared blind spots (a probe-only ledger; an `OpeningState`
  that knows no ids) — sub-units of OP-23.
- `Q-096`'s four cross-checks and `Q-097`'s running-state choice — these are **declared
  Class B deviations**, which hard rule 2 sends to *review judgement*, not to the required
  set. Both are judged in Part II.
- `Q-030`'s structural-zero publication — `Q-030` assigns the sentence to **C18**
  (*"C18 states it beside the table"*), so it is not C8's to own.

### §1.3 PHASE-1 PREDICTIONS: WHAT GOLDEN 2 LOOKS UNABLE TO EXPRESS

⚠️ **WRITTEN IN PHASE 1, FROM THE FIXTURE TABLE ALONE, BEFORE THE CODE WAS OPENED**, so
that Part II's list cannot be mistaken for something read out of the implementation.
`INC-78`'s whole diagnosis is that *"the only properties that got tested were the ones the
key can express."* The predictions, each with the vector that would catch it:

1. **E1 / S1 executed-vs-issued.** Golden 2's own `derivation.both_readings_measured`
   states the two readings are **identical on all eight fixtures**. (V05, V17)
2. **E1/E2/E3 over `create_instant_settlement`.** **No fixture in golden 2 contains one**,
   and no capture in it is anywhere near the ₹50,000 cap. (V04)
3. **E2's strict `>`.** F2 is 20,000,001; **no fixture sits at exactly 20,000,000**, so
   `>=` passes the whole file. (V06)
4. **E3 on a REFUSED action after exhaustion.** No fixture has one. (V09)
5. **S2's SAME-PAYMENT half.** F6's collision is on one payment and F3's receipts are all
   distinct — **no fixture puts one receipt on two different payments**, so a scorer keying
   S2 on the receipt ALONE passes all eight. (V20)
6. **S2's empty-string case.** Golden 2 has `null` and non-empty and nothing else. (V22)
7. **S2-amt's CURRENCY element.** Every row is implicitly INR — the **triple** and the
   **pair** cannot be told apart. (V26)
8. **S3's missing clean ledger** — golden 2's own `coverage` block names this one.
9. **S3's double capture of one authorization** — `Q-093` records that the fixture set does
   not contain it. (V32)
10. **S4's window width.** F8's three horizons are all `<= 0`; F3's is 1. Any `W >= 2`
    gives the same 72 cells. (predicted; measured in Part II)
11. **S4's stale-read clause at all.** Both S1 breaches in the file sit at calls whose
    reconstructed read was compliant, so **`S4 := S1` may reproduce all 72 cells** —
    the strongest prediction here, and the one that would mean the moat's own predicate is
    unpinned by its own answer key. (predicted; measured in Part II)
12. **S1 with a capture and a refund on one payment** — `INC-78`'s own `Missing` field.
    (V13, V14, V41)
13. **S1 on a KNOWN-ZERO captured amount** — `INC-78`(b); 3 of 12 payments on every seed.
    (V15)

### §1.4 THE SEAL

Phase 1 is sealed by the commit that lands `docs/reviews/independent/c8_reimpl.py` and
this Part I. **Phase 2 begins after it.**

- Golden 2, scored by this file alone: **72 cells, 0 mismatches.**
- The reviewer's own vectors: **43 vectors, 82 assertions, 0 mismatches.**
