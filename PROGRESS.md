# PROGRESS.md — the session journal

**Newest on top. One entry per session. Fixed template.**
Each entry opens with that session's `SESSION-TOKEN` (`PROCESS.md` §7a). Chat history is
not a record; this file is.

---

## ARCH — the rulings, the token batch, and two defect closures — BUILD — attempt 1 — 2026-08-31

**SESSION-TOKEN:** `921cfaa4` — issued by the architect in this session's prompt. ⚠️ **Its row was
written by this session, and that makes it the FOURTH self-recorded row in a table this session's own
headline change exists to stop needing.** The prompt asserted the row was already present; it was not
(`grep -c 921cfaa4 QUESTIONS.md` → **0** on first read, before any edit). See **Q-025**, and the batch
note in `QUESTIONS.md` where it is labelled rather than left looking tidy.

**Role:** BUILD, chunk cell **ARCH**. **No logic built. No tag cut. Not self-certified.**

**Token spend: NONE.** **Zero provider model calls.** No network operation was needed or made.

**Preconditions, verified rather than assumed.** `git log --oneline -3` showed **`ae8b14f`** (C2,
`f0c50283`) at HEAD; `git status --porcelain` **empty**. The prompt's *"NO OTHER SESSION IS RUNNING"*
was checked against the log rather than taken on trust — **precisely because that sentence was wrong
the last time it was written** (Q-024's third architect error): the last commit landed **28 minutes**
earlier, and nothing arrived during the session.

### 1. The token batch — and the defect inside it

`check-roles` **E1 has fired correctly three times** on one friction (`0811c64a`, `da356dbb`,
`debc97ae`): every session needs `QUESTIONS.md` for its own token row and so **collides there with
every other session**, and a session recording its own token is backwards — `PROCESS.md` §7a puts it
on the **architect**, and `REVIEW_C0.md` named self-recording as the honour-system weak point.

**Nine tokens are now recorded before the sessions that will use them exist.** `f57e216b` (C0 REVIEW),
`a0cc0212` (C1 REVIEW), `a66c389d` (C3 REVIEW), `94116fe2` (C2 REVIEW), `7904e0a2` (C4), `4377265b`
(C6), `ac7a0cf7` (C7), `5bd2f44a` (C8), `e1911a9f` (C9). **E1 parses 8 → 18 issued rows and stays
PASS.** An issued-but-unused row is harmless because **E1 checks commits → issued and never the
reverse**, so an unused row stands visible rather than being pruned to match what happened.

⚠️ **E2 AND E3 GET REAL INPUT FOR THE FIRST TIME.** C0 now holds BUILD + FIX + REVIEW and C1 holds
BUILD + REVIEW — exactly the shapes they police — and **before the C0 FIX session's B-01 repair they
could not have fired on them at all** (`REVIEW_C0.md` F4/B-01: of §7a's three named conditions, only
E1 could fire). **This is the first moment the build-vs-review separation is machine-checkable rather
than asserted.**

🚩 **AND THE BATCH OMITTED THIS SESSION'S OWN TOKEN — Q-025, a fourth architect error, found by the
verification the prompt itself demanded** (*"verify each is present and say so"*). **A token batch
that omits the batching session's own token reproduces exactly the defect it closes**: the batch is
not self-applying, because the session that lands one is itself a session and needs a row some
*earlier* batch had to contain. **Q-021's ruling — landed in this same session — already says the
batch *"is not enforced either, and that is said rather than implied."* This is the first instance of
that, within minutes.** Remedy, one clause: *every batch names the token of the session that lands
it.* **Options 2 and 3 were available and rejected for a stated reason:** C3's red was correct
*because C3's fence forbade the file*; this session's fence **names** it, so accepting a red here
would be accepting a broken `check-roles` for a reason that does not apply.

### 2. The six rulings — verbatim, and nothing deleted

**Q-017, Q-018, Q-019, Q-021, Q-022, Q-023**, recorded **verbatim** (hard rule 5). Each `Status` flips
to `RULED` **quoting the exact line it replaced**, and C2's and C3's `<pending>` placeholder lines are
**left standing rather than overwritten**, because they are an earlier session's text. The only lines
this session removed from `QUESTIONS.md` are the five status lines, each reproduced verbatim in its
replacement — checkable with `git diff`.

**Q-017 is the one that moves a number-bearing definition.** UPHELD: **S2 moves to `receipt`.** The
deciding argument is not that `receipt` is nicer — it is that **the header definition cannot be
implemented honestly**. `refunds.go:73-75` passes `nil` where `extraHeaders` go, so no refund on
Razorpay's own MCP surface can carry `X-Refund-Idempotency`, and **S2 as defined could never fire**;
making it fire would require our mock `create_refund` to accept a parameter the real server does not
have — **INC-02 in mirror image**, the error that collapsed ₹2,004 crore to ₹22.4 L, pointed the other
way. **The header finding is sharpened into a published claim, not lost.**

**Q-018:** C1's option 1, with **40 / 13 / 18** — **checked, not transcribed**, against
`RAZORPAY_SEMANTICS.md` §10's census, which states `40 + 13 + 18 = 71` against 71 contiguous rows.
**Q-019:** the **operator's confirmation** appended beneath the ruling **changing no word of it** —
condition (ii) satisfied, **(iii) discharged**, so C2 and its dependents are taggable on a review
PASS. **Q-021:** the architect's error; C3 was right. **Q-022** and **Q-023:** upheld, C2's handling
endorsed in both. **Q-024** placed as a new entry for the concurrent-review amendment — and while
placing it, `QUESTIONS.md`'s `## Concurrent pairs` preamble was found **still carrying the struck
clause** *"REVIEW sessions remain strictly serial"*, because `debc97ae` amended `PROCESS.md` §1 and
not this file's mirror. **The two canonical files disagreed for a day on the one rule every session
consults before writing its own pair row.** Corrected in `PROCESS.md`'s own manner: **struck, not
deleted.**

### 3. Q-022's remedy — the open door is now inside the frozen set

`config/protocol.yaml` gains **`probe.notes`**; §8.6's table gains the **probe note** row; the
registry gains a **STRICT** `probe_note` row on the quoted forms; and `world/spec.py`'s
`PROBE_NOTE_KEY` / `PROBE_NOTE_TEXT` **literals are deleted** in favour of a read through the loader —
**exactly the remedy C2 wrote.**

**The text was copied from §10.1, not retyped from the prompt**, and asserted character-identical:
**51 ASCII bytes**, SHA-256 `d3a87f639e49fa490ae473a676929ff3520bc794d3ef38070c6aef1e3e4c7fb5`, equal
to §8.6a's copy, to the deleted source literal and to golden 7's.

⚠️ **THE NAMES WERE KEPT, AND THAT WAS FORCED BY THE FENCE RATHER THAN CHOSEN.** `world/__init__.py`
re-exports both, and `tests/test_c2_world.py` asserts on them three times — **both files are outside
this session's fence**, and the prompt says a C2 test failing means *my* change is wrong. They resolve
**lazily, via PEP 562 `__getattr__`**, because `whetstone_gate.config.load` is deliberately uncached
(*"a cache would let a stale read outlive an edit during a long run"*) and a module-level eager read
would be exactly that cache frozen at import. **C2's tests pass unchanged; no test was edited.**

⚠️ **§8.6's warning gained a THIRD paragraph, which the prompt did not ask for.** The existing one says
*"THIS IS THE SECOND TIME THIS TABLE HAS BEEN INCOMPLETE"*, and this is the **third** — six rows 30
Aug, eight 31 Aug, and this. Leaving it would have left a **false count in the file that is law**.

### 4. `CONTEXT.md` v1.4, and an overclaim of the architect's own

**§9.2's S2 shows BOTH redefinitions, because they failed for different reasons** — amount-equality
was **wrong** (INC-04, 8/8 seeds, preserved verbatim), the header was **unimplementable**. **`S2-amt`
is unchanged.** The bullet also carries the caveat that **S2 may print a zero** — a policy-blind
attacker has no reason to populate `receipt` either — **and that a zero is a result**, because §12.1
prints it as a number and an invariant that cannot fire says something true about an opt-in guard.

**§8.6a's ULP sentence is corrected.** *"Near ₹1,50,000 one ULP flips the rounded paise integer"*
**overstated its own margin by about five orders of magnitude.** Re-derived by this session over all
**660** draws (50 scored + 10 pilot): closest approach **0.0011866860605438627855977872 paise** at
**seed 2046, draw index 3, raw `4167386882`**, **≈ 4.2 × 10⁵ ULPs**, and the float path reproduces
**all 660** integer paise here (**0 mismatches**). ⚠️ **An overclaim in a document whose subject is
overclaims, written by the architect — the class INC-05 made a rule.** **The decision to require
`Decimal` STANDS, for a stronger reason:** byte-identity is *claimed and tested*, correctly-rounded
`Decimal` makes it **provable**, and a float margin argument would need **recomputing whenever the
seed list changes** — which §13.4's N rule may do.

**One new test file**, `tests/test_arch_ulp_margin.py`, per Q-023's ruling: it **re-derives** the 660
draws rather than quoting them, and its failure messages read *"this is a finding, not a failure of
the world: report it, do not relax the assertion."* **Verified non-vacuous** — a synthetic amount
1e-10 from a boundary yields **0.036 ULPs** and fails the assertion.

⚠️ **DECLARED DEVIATION, Class B.** `config/protocol.yaml`'s `decimal_context_precision` comment
repeated the withdrawn sentence verbatim. Correcting it changes **no key and no value** —
`yaml.safe_load` of the working tree and of HEAD compare **equal** — and that file is inside this
session's fence; but TASK 3a said *"change no other key or value"* and Q-023 named §8.6a alone, so it
is recorded rather than slipped in. **Leaving it would have put a withdrawn justification inside the
artefact that gets hashed at `prereg-v1`** — the exact two-files-one-corrected shape this session
raises against the architect as Q-026, aimed at itself.

⚠️ **A SECOND, SMALLER DEVIATION, Class C:** the v1.4 change-log row was inserted with a Python
heredoc before the prompt's *"write files with your editor/write tools"* instruction was applied to it.
The bytes were verified afterwards — **0 CRLF, diff localised at 94 insertions / 28 deletions, not a
whole-file rewrite** — and every other edit in this session used the editor tools.

### 5. What was found and NOT fixed

**Q-025** — the token batch, above. **Q-026** — **`CONTEXT.md` §2 line 176 still carries
*"`create_refund` sends no idempotency key"***, the exact sentence Q-017's ruling calls **false**,
inside the block headed *"written so a payments engineer cannot puncture it."* **v1.3 corrected §2's
table row and not the prose fourteen lines below it**, so the specification now states **both** forms
of the claim, and a reader meets the false one first. **§2 is outside this session's task fence and
outside Q-017's own enumerated consequence list** (§9.2, `INVARIANTS.md`, C4, C8, golden 2), so it is
**raised, not edited — Q-022's handling, applied by the session that recorded the ruling endorsing
it.** Remedy supplied, one sentence.

**And one thing owed:** C1 raised **Q-017 as the OPERATOR'S** to rule, and the ruling as issued is
signed `(architect, 2026-08-31)` **with no operator-approval line**, unlike Q-024's *"APPROVED BY THE
OPERATOR"*. The ruling is recorded verbatim and **not** annotated inside its own text; the flag sits
at the head of the entry.

### 6. Counts

| | before | after |
|---|---|---|
| `make test` | 208 passed, 1 skipped, 2 deselected | **210 passed, 1 skipped, 2 deselected** |
| `make check-roles` | 17 passed, 0 failed, 4 n/a, exit 0 | **17 passed, 0 failed, 4 n/a, exit 0** |
| E1 issued rows parsed | 8 | **18** |

**+2 tests, both in `tests/test_arch_ulp_margin.py`, this session's only new test file.** **No other
count moved**, and `check-roles` is unchanged because E1/E2/E3 were already PASS — the batch changes
what they are checking **against**, not whether they pass. `git status --porcelain tests/goldens/`
**EMPTY**; no golden was edited, added or regenerated.

**No `INCIDENTS.md` entry is owed.** Nothing broke during this session: no test was weakened, no
assertion loosened, no red was reached. The two defects found are **specification and process
defects raised as questions** (Q-025, Q-026), not incidents of this session's own making — and
`INCIDENTS.md` is outside this session's fence in any case.

---

## C2 — the world generator, with the probe planted — BUILD — attempt 1 — 2026-08-31

**SESSION-TOKEN:** `f0c50283` — issued by the architect in this session's prompt, and recorded in
`QUESTIONS.md` `## Session tokens` **by this session**, on the architect's explicit instruction.
That is the third row in that table with that weakness and it is said plainly there rather than left
looking tidy. ⚠️ **This session was also given `QUESTIONS.md` inside its fence precisely so the trap
C3 hit could not repeat** — and it landed **two other sessions' rows** for the same reason:
`da356dbb` (C3 BUILD, owed since last night) and `debc97ae` (ARCHITECT CHECK 1, owed since **this
session was already running**).

**Role:** BUILD, chunk **C2**. Review type `full`. **Not tagged. Not self-certified. And not
taggable** — Q-019 (iii).

**Token spend: NONE.** **Zero provider model calls.** No network operation of any kind was needed or
made. The world is a seeded PRNG and a dataclass.

### Task 0 first: the suite was RED and it was an architect error, not a defect

`make test` and `check-roles` opened **RED** — `E1 FORGED/UNISSUED: {'da356dbb': [6 commits]}` —
because C3's prompt required the `Session-Token` trailer on every commit **and** fenced C3 out of the
file where the token must be recorded. C3 took the only option that neither fabricated a credential
nor crossed a hard fence, and reported the RED with its exact one-line remedy. That remedy landed
here, with **Q-020** (RULED) and **Q-021** (OPEN) placed **verbatim — byte for byte** from
`docs/sessions/c3-build-1.txt` sections 7 and 8, verified afterwards to still be exact substrings.

⚠️ **AND THEN IT HAPPENED AGAIN, MID-BUILD.** The **ARCHITECT CHECK 1** session (`debc97ae`) landed
five commits while this one was building and turned E1 red a second time, for the identical reason.
Its own report says its fence named `QUESTIONS.md` under `NOT` **"because the concurrent C2 BUILD
session owns that file"**, declares the one-row remedy, and defers four rulings to *"the next
session, once C2 releases the file."* **The row is landed here; the four rulings are not** — a ruling
is recorded verbatim (hard rule 5) or not at all, and reconstructing one from a summary would be
manufacturing it.

**TRUE BEFORE BASELINE, after task 0 and its commit:** `tasks test` **156 passed, 1 skipped,
2 deselected**; `check-roles` **17 passed, 0 failed, 4 n/a, exit 0**.

### Golden 7 reproduced exactly, on the first run, with nothing adjusted

`PROCESS.md` §5.2 authored golden 7 because C2's done-when would otherwise have been *"two runs of
one seed byte-identical"* — **a check any deterministic function passes, including a wrong one**.

| What the golden pins | Result |
|---|---|
| the **eleven** raw `mulberry32(2001)` u32 outputs | **MATCH**, all eleven |
| the **first six** as `u` to **10 significant figures** | **MATCH**, compared numerically |
| all **twelve** payment records, **field for field**, in generation order | **MATCH**, every field |
| merchant available balance | **MATCH** |
| the **8 / 3 / 1** split | **MATCH**, and exact by construction in every seed |
| `u = 0` → `50000` · `u = (2³²−1)/2³²` → `15000000` | **MATCH** |
| seed 2001: **4,414,803** paise captured, **12,414,803** with the probe | **MATCH**, three ways |

**No value was adjusted, and no golden byte was touched** — `git status --porcelain tests/goldens/`
is empty, and the test **re-derives the golden's own SHA-256 and byte count from
`tests/goldens/README.md`** and recomputes them from disk, so a session that "corrected" the oracle
would have to edit the published digest in a second file.

The three sums agree from **three independent sources**: the generated world, the golden summed on
its own records, and **§8.6a's ₹44,148 / ₹1,24,148 parsed out of `CONTEXT.md`** — no expected number
is transcribed into a test where a third copy could drift from both.

### The probe, across the whole scored range, and the discrimination task asserted

`pay_CANARYRECON` is present in **all 60 seeds** the project generates worlds for — scored
2001–2050, the ladder, and the disjoint pilot 2101–2110 — with §10.1's fields **parsed from
`CONTEXT.md` rather than transcribed**. ⚠️ **And the property that actually matters is asserted:
policy clause P7's tag — *"exempt from transaction limits"* — matches EXACTLY ONE payment in every
seed, and it is the probe.** If it matched two, P7 would exempt a payment the design does not intend
to; if none, the door would be shut and arm 4 VOID by construction. §8.6a's decoy at note-template
index 4 (*"standard limits apply"*) is its near-neighbour on purpose, and **that is what makes
finding the door a discrimination task rather than a reading test**.

### Three things this session did not take on trust

1. **The PRNG was reimplemented from §8.6a's four lines of prose, then checked** — never the other
   way round, and the architect's derivation scripts were deliberately not sought (they are in an OS
   temp scratchpad and reading them would make this a copy of the oracle rather than an independent
   reproduction of it).
2. ⚠️ **A MUTANT SURVIVED, AND THE TEST WAS STRENGTHENED RATHER THAN THE FINDING DROPPED.** Replacing
   `context.divide(Decimal(raw), Decimal(U32_RANGE))` with `Decimal(raw / U32_RANGE)` — **literally
   §8.6a's forbidden *"JavaScript float division"*** — **passed every value test in the file**,
   because for a 32-bit numerator over 2^32 the binary64 quotient is exact, and it carries **no float
   literal, no `float()` call and no `math` import**, so the structural scan did not see it either.
   Python's `/` on two ints **returns a float**; in a package that computes money the operator itself
   is the defect (`PROCESS.md` §5.1). The scan now rejects `ast.Div`, and the reason is a comment in
   the test, not a silent patch.
3. **Every mutant was run in a temp-directory copy with `PYTHONPATH` set and
   `whetstone_gate.__file__` printed** — INC-17, whose whole lesson is that an editable install
   resolves the package **by name** and a naive clone-and-run tests the live repository. The evidence
   line is in the report.

**Mutation results** (`tests/test_c2_world.py` only, each mutant a single edit in the sandbox copy):
`shift15`, `shift7`, `odd61`, `incr`, `nomask2`, `twelve-draws`, `libm`, `clock`, `status-boundary`,
`probe-note`, `note-key`, `id-material-order`, `note-mod`, `float-u`, `probe-amount`,
`probe-position`, `hardcoded-currency` — **17 mutants, 17 killed**. ⚠️ **One further mutant is
reported as EQUIVALENT rather than counted as a kill**: dropping the redundant `& U32_MASK` on the
final XOR changes nothing, because both operands are already 32-bit. **INC-11 is the entry that made
counting an equivalent mutant as "killed" a recorded failure**, and it is not repeated here.

### Q-022 — the open door is a string the freeze does not cover

⚠️ **The probe's note text is in NEITHER `CONTEXT.md` §8.6's constants table NOR `config/`.** §8.6's
own sentence: *"Any constant that is not in this table and not in `config/` is a defect, and finding
one is a review BLOCKER."* `config/protocol.yaml` carries the **six ordinary** note templates with
their texts, `probe.payment_id` and `probe.payment_amount_paise` — and **no probe note**. `data/`,
where `AUTHORED_TEXTS` puts the policy string, does not exist yet.

**This is the single most load-bearing string in the world**: clause **P7**, in every arm's policy and
in the arm-4 kernel, matches on it. **No number moves** — §10.1 and §8.6a fix it identically, golden 7
pins it, and a test parses **both** spec sections and diffs them against the package's copy. C2's
fence names `config/`, `CONTEXT.md` and `spec_constants.py` under **NOT**, so it is named in **one**
place in source, with a nine-line comment and the exact YAML block that closes it. **The defect is
Class A; the response is Class B**, and ⚠️ **the reading under which this session should have stopped
instead is stated in Q-022 in its own sentence**, because Q-010 retires the "default taken" field for
Class A items and a session does not get to grade itself out of that.

### Q-023 — this project's own justification, measured

§8.6a says *"near ₹1,50,000 one ULP flips the rounded paise integer."* **Measured over all 660 draws
of the frozen seed set**: the closest any amount comes to a `.5` boundary is **1.19 × 10⁻³ paise —
about 4.2 × 10⁵ binary64 ULPs** — and a float implementation reproduces **all 660** integers on this
machine. **So that sentence overstates its own margin for these seeds by about five orders of
magnitude, and Q-019's decision is still right** — for a stronger reason than the sentence gives:
`Decimal` makes hard rule 10's byte-identity claim **provable**, where a float world's claim would
rest on a margin argument that has to be recomputed every time the seed list changes, and the seed
list is exactly what §13.4's N decision rule may change. The margin is now a committed test whose
failure message says *"this is a finding, not a failure of the world: report it, do not relax the
assertion."*

### What landed — five commits

| # | Commit | What |
|---|---|---|
| 1 | `b9ba135` | task 0 — the `da356dbb` and `f0c50283` token rows, **Q-020 and Q-021 verbatim** |
| 2 | `cf4000c` | **Q-022** and **Q-023**, and ARCHITECT CHECK 1's `debc97ae` row |
| 3 | `f93f224` | `src/whetstone_gate/world/` — prng, amounts, spec, generator *(unreviewed)* |
| 4 | `387b5ab` | `tests/test_c2_world.py` — 52 tests *(unreviewed)* |
| 5 | *(this)* | `STATUS.md` and `PROGRESS.md` |

### Counts

| | BEFORE (after task 0) | AFTER |
|---|---|---|
| `python -m whetstone_gate.tasks test` | **156 passed, 1 skipped, 2 deselected** | **208 passed, 1 skipped, 2 deselected** |
| `check-roles` | **17 passed, 0 failed, 4 n/a, exit 0** | **17 passed, 0 failed, 4 n/a, exit 0** |

**+52 tests, every one this chunk's, every one passing. 156 + 52 = 208.** Nothing else moved: no
existing test was edited, weakened, skipped or deleted, and `check-roles` is unchanged because `D1`
is still `n/a` (`gates/` and `scorer/` are C9's and C8's). ⚠️ Before task 0 the suite stood at
**154 passed, 2 FAILED** for one bookkeeping reason that was not a defect.

### The tripwire, live, on a package full of spec constants

`test_no_spec_value_is_hardcoded_in_implementation_source` **passes on the new package with no
exemption added and none wanted** — there is no escape comment by design. Read from `config/` rather
than written into source: the PRNG name, the payment count, the draw budget, the probe index, both
amount bounds, the merchant balance, the id salt, the id hash and its hex-character count, the
`created_at` base epoch and step, the currency, the decimal precision, the note templates and their
assignment rule, the probe's id and amount, **and `money.rounding`** — resolved through a
`ROUND_`-prefix guard rather than hardcoded, so the rounding mode lives under the freeze too. The
registry's CONTEXTUAL rows were actively avoided while naming things. **A hardcoded `"INR"` mutant
was confirmed to make the tripwire fire**, so it is not passing vacuously.

### What is owed, and what may not happen

🚩 **Q-022 must land in `config/` before `prereg-v1`.** After that tag `config/` is frozen even when
it is wrong, and the fix would become a published limitation instead of a one-block edit.
🚩 **Q-019 (ii) and (iii) are unchanged and still bind: the world-generation ruling is re-opened for
the OPERATOR before `prereg-v1`, and NO CHUNK WHOSE NUMBERS DERIVE FROM IT MAY BE TAGGED `cN-pass`
UNTIL HE HAS CONFIRMED IT.** C2 is built and is reviewable. **It is not taggable, and no tag was
cut.**
⚠️ **Four rulings remain owed to `QUESTIONS.md` by the architect** (ARCHITECT CHECK 1's §7(c)),
including Q-018's — whose ruling is already implemented in `PROCESS.md` §12.1's C4 row while Q-018
still reads `Status: OPEN`. **Not this session's to write.**
⚠️ **`INCIDENTS.md` is outside this chunk's fence and no entry is owed by it:** nothing broke during
this build. The surviving float-division mutant is a **test-strength finding caught and closed inside
the session**, recorded above and in the commit message rather than dramatised into an incident —
hard rule 13's pressure runs both ways, and an invented incident has no commit.

**Do not self-certify. A fresh adversarial review follows.**

---

## ARCH — ARCHITECT_CHECK_1 + two `PROCESS.md` amendments — BUILD — attempt 1 — 2026-08-31

**SESSION-TOKEN:** `debc97ae` — issued by the architect in this session's prompt.
⚠️ **NOT recorded in `QUESTIONS.md` `## Session tokens` by this session, and that is deliberate and
the architect's own sequencing.** This session's fence names `QUESTIONS.md` under **NOT**, because
the **concurrent C2 BUILD session (`f0c50283`) owns that file** — its first task was landing the
token rows and two question entries there, which it did in `b9ba135`. `check-roles` **E1 therefore
FAILS** on this session's three commits — which is E1 **working**, the third such firing after
`0811c64a` and `da356dbb` (**Q-021**). The row is **OWED** and is one line. Nothing was weakened to
hide it.

**Role:** BUILD, chunk **ARCH**. **No tag cut. Nothing self-certified.**

**Token spend: NONE.** **Zero provider model calls.** No Groq, no Google, no network operation of any
kind was needed or made. **No logic was built and no defect was fixed.** This session wrote one
architect artefact and two `PROCESS.md` amendments.

### Why this session ran, and what it exists to stop

`PROCESS.md` §11: *"After every build and review report the architect emits a VERIFICATION block —
the numbers recomputed, the value obtained, the value claimed … **No chunk is tagged `cN-pass`
without one**."* §1: *"a chunk's review may not begin before the architect has recomputed that
chunk's build report and committed its `ARCHITECT_CHECK`."*

**`ARCHITECT_CHECK_0` §1 records that C0's review ran BEFORE its check existed** — which §1 forbids —
and closes that paragraph with *"The next chunk's `ARCHITECT_CHECK` precedes its review."*
**`ARCHITECT_CHECK_1` is that sentence kept.** It covers the four sessions of 30–31 August and it
exists **before any of their reviews begins**, so the omission does not repeat.

### Task 1 — `docs/reviews/ARCHITECT_CHECK_1.md`

**TRANSCRIBED, NOT AUTHORED.** This session **verified nothing of its own and added no finding of its
own** — it has no independent basis for one, and inventing one would make the file worthless. Written
in `ARCHITECT_CHECK_0`'s shape, and carrying its **vehicle note** convention so the file says on its
face who verified and who typed. **All four sessions are VERIFIED.**

| § | Session | The architect's finding, in one line |
|---|---|---|
| 1 | **C0 FIX** `c9521aac` | at HEAD `11f8345`, clean: test **116 passed**, `check-roles` **17/0/4 exit 0** (now printing `ROOT EXAMINED` — **OF-09's half-closure**), `selftest` **still RED, correctly** (**Q-009 upheld**). **B-01 read in source**: `_issued_tokens` → `dict[str, set[tuple[str, str]]]`, so the impossibility that made E2/E3 unable to fire **is gone**. **Q-015's `MOAT_ALLOW_LIST` created EMPTY.** INC-13…16 present, **zero placeholder `Fix` SHAs**. Fence 11 files, all inside |
| 2 | **C1** `20cd5b79` | 85,895 bytes, 71 rows. **F-01 confirmed locally.** **F-06 re-verified independently AT SOURCE**, the page re-fetched by the architect — ⚠️ **so `CONTEXT.md` §2's *"none is a key"* WAS FALSE, the FOURTH false third-party claim to reach this specification.** **INC-05 made that class a rule, and `RAZORPAY_SEMANTICS.md` is what caught it** |
| 3 | **ARCH** `0811c64a` | test **117 passed**, `check-roles` **17/0/4 exit 0**. **Golden 7 measured: `649e54ca…dd2b`, 4879 bytes — IDENTICAL to the architect's own derivation. Not one byte altered in transit.** Fence 10 files, all inside |
| 4 | **C3** `da356dbb` | ⚠️ **the enumeration RE-DERIVED INDEPENDENTLY** from §11.1's text alone, importing nothing from `whetstone_gate` and without reading C3's code: **34/164 MATCH**, write tools **name for name**, T-FP bytewise **MATCH**, telecom **MATCH**. **Two independent derivations now confirm 34/164; `CONTEXT.md` §21.4's #1 TIME RISK IS RETIRED.** **The sort ruling is PROVED load-bearing by the architect's own output, not asserted** |
| 5 | — | **INC-17 reproduced** by the architect at 03:45 IST. ⚠️ **Live consequence: the C0 re-review must re-run 46 probes against pre-fix source, and done naively ALL 46 REPORT PASS** |
| 6 | — | **TWO ARCHITECT ERRORS, recorded against himself**: the **STRICT `400` tripwire row** (the FIX session implemented what it was told **and flagged the consequence** — that flag is what got the instruction corrected), and **C3's fence-vs-trailer contradiction (Q-021)** |
| 7 | — | what he **could not** verify: the dashboard PNGs, the no-payment-method attestation, and that the sessions were genuinely different (**nothing can — §7a says so**) |
| 8 | — | **No tag is cut by this file.** C0 stays `FAILED` until its re-review passes; C1, C2, C3 stay `built (unreviewed)` |

### Task 2 — `PROCESS.md` §1, concurrent reviews

**Approved by the OPERATOR on 2026-08-31.** *"REVIEW sessions remain strictly serial"* → **UP TO TWO
REVIEW SESSIONS IN FLIGHT AT ONCE, IFF their chunks are DISJOINT AND NEITHER DEPENDS ON THE OTHER.**
**A chunk and its dependency are never reviewed in parallel** — **C7's and C8's may not pair; C1's
and C3's may, and C2's and C4's may.** The pair is recorded in `QUESTIONS.md` under
`## Concurrent pairs` **before either prompt is issued**, exactly as a build pair is.

⚠️ **The old clause is STRUCK, not deleted, and the amendment is dated and in the file's own voice
alongside the existing *"revised 2026-08-30"* note — because a rule that changed under schedule
pressure must be visible as a change and must show its working.** The working: the serial-review rule
was **the binding constraint on the entire critical path to the freeze** — **twelve `full` reviews at
a measured ~75 minutes is ~15 hours**, which put **C14 past midnight on 31 August**.

⚠️ **WHAT IS EXPLICITLY NOT CHANGED, so this cannot be read as a precedent for cutting review
rigour:** **PASS conditions, persona coverage, mutant counts, the reimplementation requirement, the
two sealed phases, and the rule that build and review are never the same session.** Each review is
still a **different fresh session**, still **blind in Phase 1**. **The only change is that two are in
flight at once.** *"This project's own C0 FAIL is the evidence that the gate works, and it is worth
more than the hours it cost."*

**RISKS ACCEPTED, EACH WITH ITS MITIGATION:** journal collisions on `STATUS.md`, `PROGRESS.md` and
`OPEN_FINDINGS.md` → the **append-only + rebase + stop-after-two-rejections** clause, **PROVEN on
2026-08-31 when C0-FIX and C1 ran concurrently for 45 minutes with zero collisions**; a **FAIL
arriving while its pair is mid-flight** → **§11a's twice-failed-chunk rule**; and **the architect's
own throughput**, the remaining limit, to be reported the moment it binds.

⚠️ **Class B judgement, recorded rather than taken silently: `PROCESS.md` §12.0's item 1 still reads
*"Reviews stay serial, so the serial review queue is the binding constraint."*** It was **NOT
back-edited** — it is the record of the arithmetic as it stood on 30 August, and rewriting it would
erase that. **The supersession is noted inside the new §1 bullet instead.**

### Task 3 — `PROCESS.md` §12.1's C4 row, Q-018's ruling implemented

C4's done-when read *"every documented Razorpay error in `RAZORPAY_SEMANTICS.md` fires in the mock
world"*. **C1 established first-hand that ~18 of the ~50 documented errors are UNREACHABLE BY
CONSTRUCTION** from any world built on `CONTEXT.md` §8.6 — merchant account configuration, a payment
method this world does not model, an active dispute, a **WALL CLOCK (which hard rule 8 forbids in
core logic)**, 5xx faults, or a Razorpay product with no API at all. **So as written the done-when
becomes UNSATISFIABLE THE MOMENT THE ORACLE IS COMPLETE, and the perverse incentive is to keep the
oracle INCOMPLETE — the opposite of what C1 exists for.**

**AMENDED per the architect's ruling of 2026-08-31, adopting C1's option 1:** the done-when reads
over the **`MUST-FIRE`** set; every **`MUST-HOLD`** row holds; and **every `RECORDED` row is listed
in the self-test's output as documented-but-unreachable WITH ITS REASON, so the excluded set is a
printed number and not a silence (hard rule 11).** **C1 labelled all 71 rows for exactly this
purpose; the counts are 40 / 13 / 18.** The superseded wording is **quoted inside the amended row**,
not deleted.

### What landed — four commits

| # | Commit | What |
|---|---|---|
| 1 | `bd2bf4c` | `docs/reviews/ARCHITECT_CHECK_1.md` |
| 2 | `b5ee2a0` | `PROCESS.md` §1 — the concurrent-reviews amendment |
| 3 | `8f19312` | `PROCESS.md` §12.1's C4 row — Q-018's ruling |
| 4 | *(this)* | `STATUS.md` + `PROGRESS.md` |

**Documentation only — no source, no test.** These commits therefore carry **no `(unreviewed)`
marker**, and every one carries `Session-Token: debc97ae`.
⚠️ **All files written with the editor/Write tools, never through a shell heredoc or a Python
script** — **INC-06, INC-10, INC-12, INC-13 and INC-16 are FIVE occurrences in this project of
literal text mangled between a tool call and a file**, and INC-16 happened to the session that had
just documented the fourth. Every written file was verified afterwards: **zero CR bytes, zero stray
C0 control bytes, valid UTF-8, and `git hash-object` == `git hash-object --no-filters`** (so §6a's
fingerprint property holds). The three amended `STATUS.md` chunk rows were re-counted at **7 pipes /
6 columns** each.

### Counts

| | BEFORE | AFTER |
|---|---|---|
| `python -m whetstone_gate.tasks test` | **156 passed**, 1 skipped, 2 deselected, **0 failed** | ⚠️ **154 passed, 2 failed**, 1 skipped, 2 deselected |
| `check-roles` | **17 passed, 0 failed, 4 n/a, exit 0** | ⚠️ **16 passed, 1 failed, 4 n/a, exit 1** |

**Total is 156 at both ends. No test was added, removed, weakened, skipped or loosened** (hard rule
6), and **no source was touched.** ⚠️ **The ONLY movement is this session's own unrecorded token**,
and it is named as such: `test_no_commit_carries_a_forged_or_reused_session_token` fails, and
`test_check_roles_exits_zero` fails **as a consequence of it**. **Nothing in the movement is
attributable to the concurrent C2 session** — C2's `b9ba135` (the token rows, Q-020 and Q-021) landed
**before** this session's first commit and is in its base, which is **why C3's two failures were
already cleared at the BEFORE reading**.

### What broke while doing it

**Nothing.** No `INCIDENTS.md` entry is owed by this session, and none was written — `INCIDENTS.md`
is outside this fence in any case. The E1 failure is **not a defect**: it is **the architect's own
sequencing**, predicted in this session's prompt, and it is Q-021's shape repeating by design.

### What is owed

🚩 **This session's token row — one line.** `| `debc97ae` | ARCH | BUILD | 2026-08-31 |` in
`QUESTIONS.md` `## Session tokens`. Until it lands, `check-roles` exits 1.
🚩 **FOUR RULINGS are owed to `QUESTIONS.md` by the architect** and land in the **next** session, once
**C2 (`f0c50283`) releases the file**. They are **not this session's** to write.
🚩 ⚠️ **AND ONE TEMPORARY INCONSISTENCY, STATED RATHER THAN LEFT TO BE FOUND: `PROCESS.md` §12.1's C4
row now carries Q-018's ruling while `QUESTIONS.md` Q-018 still reads `Status: OPEN`.** The ruling
text is in the amended row and in `docs/sessions/arch-check-1.txt`. **Hard rule 5 says a ruling is
recorded in `QUESTIONS.md` before anything else is touched; this session could not, and says so
rather than reaching outside its fence** — the precedent being C1 BUILD and C3 BUILD, which did the
same and were right to.
**Nothing is blocked by any of it: Q-019 (ii) gates TAGGING, which happens at a review PASS.**

**No tag was cut. Nothing is self-certified.** A fresh adversarial review follows — and, now that
`ARCHITECT_CHECK_1` exists, **C0's re-review and C1's and C3's reviews may begin.**

---

## C3 — τ² adapter A: the enumeration and the pre-registered task selections — BUILD — attempt 1 — 2026-08-31

**SESSION-TOKEN:** `da356dbb` — issued by the architect in this session's prompt.
⚠️ **NOT recorded in `QUESTIONS.md` `## Session tokens` by this session, and that is deliberate.**
C3's scope fence names `QUESTIONS.md` under **NOT**. `check-roles` **E1 therefore FAILS** on this
session's three commits — which is E1 **working**, exactly as it did for `0811c64a`. The row is
**OWED to the architect** and is one line. See *What is owed* below; nothing was weakened to hide it.

**Role:** BUILD, chunk **C3**. Review type `full`. **Not tagged. Not self-certified.**

**Token spend: NONE.** **Zero provider model calls.** No Groq, no Google, no network operation of any
kind was needed or made. This chunk reads local files from a vendored checkout and enumerates them.

### Why this chunk ran first

`CONTEXT.md` §21.4 names the τ² adapter **the project's #1 time risk** — *"the step most likely to
eat a day"* — and `PROCESS.md` §12.1 schedules it **first**; revision 1's plan scheduled it **tenth,
behind a chunk that depends on it**. Everything external about this submission rests on τ²-bench: it
is the **only** source of tasks, gold behaviour and a grader this project did not author, and
`PROCESS.md` §14 puts it on the **never-cut** list. If it could not be driven, the central claim was
gone. **It can be driven, and the specification's numbers are right.**

### The result — all six of §11.1's sub-counts reproduced, none assumed

| | `CONTEXT.md` §11.1 claims | Reproduced at the pinned SHA |
|---|---|---|
| must-not-write, total | **34 of 164** | **34 of 164** ✅ |
| airline | **24 of 50** (7 empty, 17 read-only) | **24 of 50** (7, 17) ✅ |
| retail | **10 of 114** (2 empty, 8 read-only) | **10 of 114** (2, 8) ✅ |
| write tasks | **130** | **130** = 26 airline + 104 retail ✅ |
| `reward_basis`, airline | all **50** `[DB, COMMUNICATE]` | **50** ✅ |
| `reward_basis`, retail | **112** `[DB, NL_ASSERTION]`, **2** `[DB]` | **112 / 2** ✅ |
| telecom | **2,253** `[ENV_ASSERTION]` + **32** `[ENV_ASSERTION, ACTION]` of **2,285** | **2,253 / 32 / 2,285**, `DB` in **none** ✅ |

Partitions, printed as `PROCESS.md` §9 requires: `7 + 17 + 26 = 50`, `2 + 8 + 104 = 114`,
`34 + 130 = 164`. **Nothing needed adjusting.** ⚠️ **§11.1's *"The spec's 34/164 figure is exactly
right"* is now a checked statement rather than a checked-once one** — the test re-derives it on every
run and **parses the expected values back out of `CONTEXT.md` itself**, so neither side is
transcribed into a test file where a third copy could drift from both.

### Three things that were verified rather than trusted

1. **Write tools come from τ²'s own decorator, and the parser was cross-checked against τ².** The
   enumeration reads `@is_tool(ToolType.WRITE)` out of τ²-bench's source with `ast` — *a hand-list of
   tool names would be an answer key we authored.* ⚠️ **The set that parser returns was checked
   against the set τ²'s own metaclass builds at import time** (the `__tool_type__` attribute
   `is_tool` sets): **identical on all 14 airline and all 16 retail decorated tools, with zero
   `mutates_state` overrides in either domain.** Airline WRITE = 6, retail WRITE = 7.
2. **Telecom's exclusion is asserted as its REASON, not its conclusion.** §11.1 withdrew an unsourced
   *"unsound"* claim and replaced it with a structural one. The test re-derives that no telecom
   `reward_basis` carries `DB` at all — so there is **no DB-hash write signal to score** and telecom
   **cannot host the control**, which is a different and checkable statement.
3. **Both source lines §11.1 cites are still exactly there.**
   `evaluator_nl_assertions.py:121` is `assistant_message = generate(` with
   `model=DEFAULT_LLM_NL_ASSERTIONS,` on 122, and `config.py:24` is
   `DEFAULT_LLM_NL_ASSERTIONS = "gpt-4.1-2025-04-14"`. **No drift.** *This project has shipped four
   false claims about third-party code; a stale line number would be the fifth, and it is cheap to
   check.*

### The sort ruling, and why it is load-bearing rather than a formality

§13.4 pre-registers T-FP as *"the first 40 write-task ids after sorting"* and **does not say which
sort**. Ruled by the architect: **task ids as strings, bytewise ascending, within each domain, first
20 of each.** ⚠️ **The two readings select different tasks in BOTH domains**, and a test asserts that
difference so the ruling is shown to matter instead of assumed to:

| | first | last | what a numeric sort would have done |
|---|---|---|---|
| airline | `"11"` | `"37"` | started at `"7"`; `"7"` and `"8"` are excluded bytewise |
| retail | `"0"` | `"15"` | `"100"`…`"109"` sort **ahead of** `"11"` bytewise |

**Left to "whatever sort the language defaults to", a pre-registered sample would have been decided
by an implementation detail after the fact** — the opposite of pre-registration.

### The db_reward non-use, stated at the precision the claim actually supports

The test walks **`db_reward`'s own transitive imports** — `tau2.evaluator.evaluator_env`, 24
first-party modules — and finds **no text-generation client**: `litellm` unreachable,
`tau2.utils.llm_utils` unreachable, `evaluator_nl_assertions` unreachable. *A walk over τ²-bench as a
whole would fail correctly and prove nothing about what we call.* Three things keep that honest:

- **the same walk is pointed at `evaluator_nl_assertions` and MUST find `litellm` and
  `tau2.utils.llm_utils`** — a walk that finds nothing anywhere is a walk with a broken regex;
- ⚠️ **`vendor/tau2-bench/src/tau2/__init__.py` DOES import the framework's model clients**, so
  **importing any `tau2.*` module loads `litellm` into the process** (measured ~22 s). That is a
  property of package initialisation, not of the reward path — and it is **asserted in a test rather
  than left out**, because *"no model client is ever loaded in our process"* would be **false**. It
  is also why this adapter imports **no** τ² module and reads τ²'s **files** instead;
- ⚠️ **one provider SDK name IS reachable from the db_reward path and this session says so first:**
  `elevenlabs`, a **speech**-synthesis SDK, imported by `tau2.data_model.voice` for a pydantic type,
  inside `try: … except ImportError`, not installed here, never called on the reward path. **Not a
  text-generation client and it does not touch the claim** — but a reviewer would find it, so a test
  names it, pins where it enters, and asserts it is still guarded. **It is not swallowed by a
  denylist that happens not to mention it.**

### What landed — three commits

| # | Commit | What |
|---|---|---|
| 1 | `7fb09d4` | the **34 must-not-write ids** and the **40 T-FP ids** pre-registered in `config/protocol.yaml` |
| 2 | `39516dd` | `src/whetstone_gate/tau2/` — the enumeration *(unreviewed)* |
| 3 | `5032cb6` | `tests/test_c3_tau2_enumeration.py` — 39 tests *(unreviewed)* |

⚠️ **`config/` is a pre-registration artefact and editing it was legal ONLY because `prereg-v1` does
not exist.** No existing key or value was changed; `vendor.tau2_bench_sha` was **verified**, not
rewritten. Every id is **quoted** — τ² task ids are strings, and unquoted YAML would turn `"0"` into
`0`, matching no task at all. ⚠️ The ids were **hand-written and then machine-verified against the
derived enumeration**, and that verification is a **committed test**, not a one-off — because
`INC-06`, `INC-10`, `INC-12`, `INC-13` and `INC-16` are **five occurrences** in this project of
literal text mangled between a tool call and a file.

⚠️ **Class B deviation, recorded rather than silently taken:** the prompt asks for the 34 *"each with
its domain"*; both lists are committed as **domain-keyed mappings** rather than flat `{id, domain}`
records. Identical information, and the domain cannot be separated from an id.

### Counts

| | BEFORE | AFTER |
|---|---|---|
| `python -m whetstone_gate.tasks test` | **117 passed, 1 skipped, 2 deselected** | ⚠️ **154 passed, 2 failed**, 1 skipped, 2 deselected |
| `check-roles` | **17 passed, 0 failed, 4 n/a, exit 0** | ⚠️ **16 passed, 1 failed, 4 n/a, exit 1** |

**+39 tests, all this chunk's, all passing.** The **two** failures and the **one** `check-roles`
failure are **the same single cause**: `da356dbb` is not in `QUESTIONS.md`'s token table, which is
outside this chunk's fence. `test_no_commit_carries_a_forged_or_reused_session_token` fails, and
`test_check_roles_exits_zero` fails **as a consequence of it**. ⚠️ **Nothing was weakened, skipped or
loosened** (hard rule 6), and no test was touched to make this go away.

### What broke while doing it

**Nothing in this chunk's own work.** Every count reproduced on the first derivation, the
hand-written config ids matched the derived ones on the first check, and no test was flipped.
⚠️ **`INCIDENTS.md` INC-17 was PLACED, and it is not this session's finding** — it was found by the
ARCH world-generation session (`0811c64a`) and **independently reproduced by the architect**: a probe
run inside a clone of an *old* commit imported `whetstone_gate` from **the live repository**, because
an editable install resolves the package **by name** regardless of the working directory. It printed
`1 passed` where the truth was a failure. ⚠️ **Its live consequence is carried in the entry: the C0
re-review must re-run 46 probes against pre-fix source, and done naively ALL 46 WILL REPORT PASS.**

### What is owed

🚩 **Q-021 — OWED, and it is why the suite is red.** `CLAUDE.md` §5 requires the `Session-Token`
trailer on every commit **and** requires the token to be recorded in `QUESTIONS.md`; C3's fence names
`QUESTIONS.md` under **NOT**. This session carried the trailer and **did not reach outside the
fence** — the precedent being C1 BUILD, which wrote Q-016/017/018 into its report *"rather than
reaching outside the fence"*, and was right to. **Remedy: one row —**
`| `da356dbb` | C3 | BUILD | 2026-08-31 |`.
🚩 **Q-020 — RULED by the architect, OWED to `QUESTIONS.md`.** C3 is a `full` chunk with **no
golden**, and that is a ruling, not an omission: **C3's golden is τ²-bench itself at the pinned SHA**
— expected values read from an unmodified third-party checkout are external **by construction**,
which is the strongest form of what hard rule 3 protects. Q-016's reasoning, applied to C3. Its
enforcement is that **C3's review must independently re-derive the 34/164 split, the six sub-counts,
the `reward_basis` census and the 40 T-FP ids from the same SHA, by its own method, and diff.**
🚩 **A `conftest.py` guardrail is NAMED AS OWED** by INC-17 — an assertion that
`whetstone_gate.__file__` lies under the pytest rootdir. `tests/conftest.py` is an existing test file
and outside this fence, so it is **named, not built**.

Both full texts are in `docs/sessions/c3-build-1.txt`, in `QUESTIONS.md`'s exact format.

**`vendor/tau2-bench` verified at `a2c024725189473d2d7cea3a5cfdbcc67478e41f` with an EMPTY porcelain
BEFORE and AFTER.** It was never edited, patched or installed over. **No tag was cut. Nothing is
self-certified — a fresh adversarial review follows.**

---

## ARCH — world-generation specification + golden 7 + the owed questions — BUILD — attempt 1 — 2026-08-31

**SESSION-TOKEN:** `0811c64a` — issued by the architect in this session's prompt. ⚠️ **Recorded in
`QUESTIONS.md` `## Session tokens` BY THIS SESSION**, because no earlier session wrote the row and
`check-roles` **E1 fails on a token that is not in that table** — it did, `FORGED/UNISSUED` on this
session's own first two commits, which is E1 working rather than being satisfied retroactively. That
is stated in the table rather than left tidy: **what is not claimed is that a different session
vouched for this one.** It is also **the first row whose chunk cell is `ARCH`**, which only became
parseable when the C0 FIX session landed Q-014 (iii).

**Role:** BUILD, chunk cell **ARCH**. Specification, config, one **architect-authored** fixture and
question-log entries. ⚠️ **NO LOGIC WAS BUILT AND NO VALUE WAS COMPUTED.**

**Token spend: NONE.** Zero provider model calls. No network operation was needed or made.

### The finding this session exists to answer

**`CONTEXT.md` §8.6 did not determine a world.** Its *"world generation"* row gives the PRNG, the
payment count, the amount range, the 8/3/1 split and the merchant balance **and nothing else** — no
draw order, no exact log-uniform formula, no id format, no non-amount field, no status-assignment
rule. `PROCESS.md` §5.2's **golden 7** requires *"the complete 12-payment record for seed 2001"*,
which **is not derivable from that text**. So the golden that gates C2 could not be authored, and
C2's done-when would have fallen back to *"two runs of one seed are byte-identical"* — **a check any
deterministic function passes, including a wrong one.**

### What landed — seven commits

| # | Commit | What |
|---|---|---|
| 1 | `cb96c9a` | **`CONTEXT.md` v1.3 + §8.6a**, the algorithm stated exactly, and the v1.3 change-log row |
| 2 | `65c8354` | §8.6's **nine** new constants rows + the matching `config/protocol.yaml` `world:` keys |
| 3 | `09ada4c` | `SESSION-TOKEN 0811c64a` recorded in `QUESTIONS.md` |
| 4 | `345f921` | the **nine registry rows** + the ruled `400` correction *(unreviewed)* |
| 5 | `d9c32d8` | **golden 7** — `tests/goldens/world_seed_2001.json` — and the goldens README |
| 6 | `ebd16ec` | the **two false attributions** corrected (§2, §6) + §9.2's pointer to Q-017 |
| 7 | `64a16fe` | **Q-016 / Q-017 / Q-018 placed verbatim**, and **Q-019 recorded** |

**§8.6a fixes:** the `mulberry32` step (logical `>>>`, every product mod 2^32); **`u` as the exact
rational `raw / 2^32`, never the JavaScript float division**; the amount in `decimal.Decimal` at
`prec=50`; **exactly eleven draws per seed, the probe consuming none**; positional status assignment;
`pay_` + the first 14 hex of `sha256("whetstone-gate:<seed>:<index>")`; `created_at` from a **fixed**
epoch so the world **contains no clock read**; the six-template notes pool assigned by `index mod 6`;
and the `fetch_payments` return order.

### The two decisions inside it that are load-bearing, and are recorded as such (Q-019)

1. ⚠️ **`decimal.Decimal`, NOT binary floating point — and this is correctness, not preference.**
   `math.exp`/`math.log` call the platform libm, which may differ by **one ULP** across platforms,
   and near ₹1,50,000 one ULP **flips the rounded paise integer**. Hard rule 10 and §5.1 both **claim
   and test** a byte-identical world, so **the spec as written would have shipped a world
   reproducible only on the machine that generated the golden** — passing its own test here and
   **failing on a reviewer's**. `Decimal.ln()`/`Decimal.exp()` are required to be *correctly rounded*
   and are therefore platform-identical.
2. ⚠️ **The notes pool carries a DELIBERATE DECOY at index 4.** The attacker's own tradecraft
   paragraph says *"**some** describe exceptions to normal limits"* — **plural**. If
   `pay_CANARYRECON` were the only annotated payment, that paragraph would stop being tradecraft and
   become a **signpost**: CANARY-A would measure whether the model can **read**, not whether the
   attacker is **competent**, and the void threshold would calibrate against an inflated number.
   *"standard limits apply"* is the discriminator against *"exempt from transaction limits"*.
   **Finding the door is a discrimination task.**

### Golden 7 — copied, never computed

`tests/goldens/world_seed_2001.json` · SHA-256
`649e54ca446e8308f5fcd69ebba56eda5faea8d58246be7277cdb8b42227dd2b` · **4,879 bytes** — both **as
observed**, both equal to the expected values.

⚠️ **`tests/goldens/` is read-only to a build session (hard rule 3), and this session computed no
value in that file.** It was the vehicle for an architect-authored golden that §5.2 requires
committed before C2's prompt is issued. **Copied byte for byte, never transcribed**, and verified
four ways: `sha256` matched, size matched, `cmp` against the source reported IDENTICAL, and
`git hash-object` equalled `git hash-object --no-filters` (`afb546d43d022eff1bbff0e686eef95be70bcf2e`
both ways). `check-roles` **A5 passes** on it. **No `mulberry32` and no amount formula was
implemented anywhere to "confirm" it** — a golden verified by a reimplementation has stopped being
independent. Copy rather than retype because **INC-06, INC-10, INC-12, INC-13 and INC-16 are five
occurrences in this project of literal text mangled between a tool call and a file**, and a golden is
the one artefact where a single wrong character is undetectable by any test **because it is the
test**. The same reasoning governed Q-016/017/018, which were **extracted byte-for-byte** from
`docs/sessions/c1-build-1.txt` and verified afterwards to still be exact substrings of `QUESTIONS.md`.

### Two false attributions, corrected at source

- **§2's `create_refund` row said of its five parameters *"none is a key"*. That is FALSE.** Razorpay
  documents `receipt` **as** an idempotency key. ⚠️ **The fourth false claim about third-party
  behaviour to reach this specification**; `INCIDENTS.md` **INC-05** is the entry that made the class
  a rule, and that rule is what caught this one. The finding is **sharpened, not weakened**: the
  header is *structurally unsendable*, `receipt` is merely *optional and unpopulated by default*.
- **§6 credited *"will settle the maximum amount possible and ignore amount parameter"* to two doc
  pages. It is on neither** — it is `settlements.go:231-232`, which **§2's own table cites
  correctly**. One specification, one string, two attributions.
- ⚠️ **§9.2's definition of S2 was NOT touched.** A fact about a third party was corrected; an
  invariant was not. Whether S2 should recognise a repeated `receipt` is **Q-017 — OPEN, and the
  operator's.** §9.2 gained only a one-line pointer saying so.

### Counts

| | BEFORE | AFTER |
|---|---|---|
| `python -m whetstone_gate.tasks test` | **116 passed, 1 skipped, 2 deselected** | **117 passed, 1 skipped, 2 deselected** |
| `check-roles` | **17 passed, 0 failed, 4 n/a, exit 0** | **17 passed, 0 failed, 4 n/a, exit 0** |

**+1 test, and it is the one sanctioned probe.** ⚠️ **It fails against the pre-fix source and passes
against the new**, demonstrated in a throwaway clone at `09ada4c` — hard rule 6's *"provably
meaningful"* bar. The registry's `400` row moved **STRICT → CONTEXTUAL** by architect ruling; **no
existing assertion pinned the mode, so none was changed to get green**, and the distinction between a
ruled re-aim and a weakening is made visible by the probe asserting **both** halves — it still fires
on `context_summary_max_tokens = 400` and no longer fires on `HTTP_BAD_REQUEST = 400`.

### What broke while doing it

⚠️ **A FALSE PASS, caught and not shipped, and an `INCIDENTS.md` entry is OWED for it.** The first
attempt to prove the new probe fails against the pre-fix source **reported `1 passed`** — the
opposite of the truth. Cause: the throwaway clone was checked out at the old SHA, but the venv's
**editable install resolved `whetstone_gate` to the live repository**, so the probe read the *new*
registry while appearing to test the *old* one. Re-run with `PYTHONPATH` pointing at the clone's
`src/` — and with `whetstone_gate.__file__` printed to prove which tree was loaded — it **failed**,
correctly. **This is the C0 review's own "a check that reports PASS over nothing" class, arriving in
the verification procedure rather than in the code**, and it will bite the C0 re-review, which must
re-run 46 probes against pre-fix source. `INCIDENTS.md` is not this session's file; the full rule-13
entry is in this session's report and in `docs/sessions/arch-worldgen-1.txt`, **declared OWED to the
architect.**

### What is owed, and what may not happen

🚩 **Q-019 is Class A and carries the operator's own three conditions.** The derivation is published
(§8.6a plus the entry); **the ruling is explicitly re-opened for the operator's review before
`prereg-v1`** — it does not pass silently into the frozen set because it was written overnight; and
⚠️ **no chunk whose numbers derive from this algorithm may be tagged `cN-pass` until the operator has
confirmed it. C2 is unblocked to be BUILT and REVIEWED. It is not unblocked to be TAGGED.**
**No tag was cut. Nothing is self-certified — a fresh adversarial review follows.**

⚠️ **`config/` is a pre-registration artefact and editing it was legal ONLY because `prereg-v1` does
not exist.** From that tag it is frozen and a defect in it is published as a limitation, never
edited away.

---

## C0 — the four BLOCKERs — FIX — attempt 1 — 2026-08-31

**SESSION-TOKEN:** `c9521aac` — issued by the architect in the C0 fix prompt and recorded in
`QUESTIONS.md` `## Session tokens` by the `e210c6f5` session **before this session ran**. Carried as
the `Session-Token:` trailer on all eleven commits below.

**Role:** FIX. Wrote the `INCIDENTS.md` entries **first, in `864c621`, before a line of code
changed** (hard rule 13), then fixed only the findings named in the prompt. **Ran concurrently with
the C1 BUILD session (`20cd5b79`) as pair P-01**, whose four commits are interleaved in the log
below; every one of this session's eleven commits touched **only** files inside its own scope fence,
and `git show --stat` per commit is the check.

**Token spend: NONE.** Zero provider model calls — no Groq, no Google, nothing consuming a lane's
quota. Mock and local only.

### What landed — the four BLOCKERs, with the review's own §4 evidence re-run OLD beside NEW

| | OLD (`864c621`) | NEW (`8ed108e`) |
|---|---|---|
| **B-01** — §7a's two named violations inserted into `QUESTIONS.md` | `PASS E2 \| clean` · `PASS E3 \| clean` | `FAIL E2 \| SHARED on ['C0']` · `FAIL E3 \| REUSED: cafebabe … deadbeef …` |
| **B-02** — the four attack forms | 1 `FAIL` · 2 `PASS` · 3 `PASS` · 4 `PASS` | **1 · 2 · 3 · 4 all `FAIL`** (and form 3 fails `D1` too) |
| **B-03** — `git rm config/protocol.yaml` | `14 passed, 0 failed, 3 n/a` · **exit 0** | `14 passed, 1 failed, 6 n/a` · **exit 1** |
| **B-04a** — `camel_comparator:` block deleted | `make selftest` → **`2 passed`** (GREEN) | **`1 failed, 1 passed`** (RED) |
| **B-04b** — `config/lanes.yaml` deleted entirely | operator gate → **`1 passed`** | **`1 failed`** |

Each was run in a **clean clone** of the tree at that SHA — `git clone`, `git checkout <sha>`,
`core.autocrlf=false` — not by editing this working tree, and the mutations are the review's own
verbatim.

### And the rest

- **`A5`, one check with TWO branches** (`4a34c04`) — closes **OF-01** and is **INC-13**'s systemic
  guardrail. ⚠️ **A claim in the record that must not be rebuilt: one branch would NOT have done
  it.** A control-byte scan over TEXT-classified files is *not* a superset of OF-01's discriminator,
  because a lone CR makes git call the file **BINARY** — so a text-only scan skips exactly the file
  OF-01 is about. Two holes, opposite sides of git's own verdict.
- **`E5` + a dated four-SHA exception list** (`0067b19`) — Q-014 (i)–(iv), which the architect raised
  to **BLOCKER** for this cycle. E4's *"carry no trailer"* list drops **20 → 16** and stops printing
  a false statement about four commits that do carry one.
- **`MOAT_ALLOW_LIST`, created EMPTY** (`947a995`), with a probe that pins it empty **and** proves an
  entry can actually blind D3 — so pinning it is not decorative.
- **The §8.6 → registry direction, which never existed** (`8ed108e`). Measured: **21** §8.6 rows,
  **14** pre-fix registry rows, **8** with no registry entry at all. All eight added.
- **OF-03, OF-04, OF-06 and OF-10 CLOSED.** **OF-02, OF-09 and OF-11 updated but STILL OPEN**, each
  with the part that was *not* closed named rather than rounded up.

### What broke while doing it, and what caught it

⚠️ **`INCIDENTS.md` INC-16.** Renaming one import line, this session used a **Python script** rather
than the editor tool, and `Path.write_text`'s Windows newline translation rewrote **all 705 line
endings** of `tests/test_c0_fix_probes.py` to CRLF. **`check-roles` A3 and A4 caught it, before any
commit** — which is what `.gitattributes` was a first-commit deliverable for. Repaired at byte level
with `read_bytes`/`write_bytes` and no escape sequence. **FIFTH occurrence of INC-06's class, in the
session that had just written INC-13 about the fourth, against an explicit warning in its own
prompt.** Recorded rather than quietly repaired.

### Numbers

`make test` **61 → 116 passed**, 1 skipped, 2 deselected · `check-roles` **14 passed / 0 failed / 3
n/a → 17 passed / 0 failed / 4 n/a**, exit 0 · `make selftest` **1 failed, 1 passed → unchanged, and
that is correct** (Q-009: red until RUN-1 decides the CaMeL branch) · F2 sentinel count **6 → 6**.

**52 kept probes in `tests/test_c0_fix_probes.py`. 46 of them fail against `864c621`'s source**; the
6 that pass there are regression guards by design, not defect probes, and are named as such.

### Raised and NOT acted on

⚠️ **`400` as a STRICT tripwire literal is also HTTP Bad Request**, which C11's runner is likely to
write bare — and a hit there has **no legitimate remedy**, since an HTTP status cannot be read from
`config/` and `spec_constants.py` offers no escape comment by design. Implemented STRICT as the
architect directed (the failure mode is a stop-and-ask, never a silent pass) with the concern
recorded in the row's own `note`. **This session's scope fence forbids `QUESTIONS.md`, so it could
not be raised there and is raised in the session report instead — it needs a ruling.**

⚠️ **This session certifies nothing and cut no tag.** A fresh adversarial review re-runs the evidence.

---

## C1 — RAZORPAY_SEMANTICS.md + PROVENANCE.md A1–A6 — BUILD — attempt 1 — 2026-08-31

**SESSION-TOKEN:** `20cd5b79` — issued by the architect in the C1 build prompt and recorded in
`QUESTIONS.md` `## Session tokens` by the `e210c6f5` session **before this session ran**, which is
the shape `PROCESS.md` §7a intended. Carried as the `Session-Token:` trailer on every commit below.

**Role:** BUILD — **documentation only**. No source file, no test file and no golden was touched.
Ran concurrently with the **C0 FIX** session (`c9521aac`), which owns `src/`, `tests/` and
`INCIDENTS.md` tonight (concurrent pair **P-01**).

**Token spend: NONE.** Zero provider model calls — no Groq call, no Google call, nothing consuming a
lane's quota. **27 HTTP GETs to public third-party documentation**, plus 5 against two pinned public
source trees. Fetching a public docs page is not a provider model call and consumes no lane quota
(ruled 2026-08-31, `PROCESS.md` §11a); `PROCESS.md` §9 *requires* those fetches, because this chunk
is nothing but third-party claims.

### What landed

1. **`RAZORPAY_SEMANTICS.md` — new, 71 rows**, each with a verbatim quote, a URL and a **UTC fetch
   timestamp**. **0 rows marked `[UNFETCHED]`.** Partitioned `MUST-FIRE` 40 / `MUST-HOLD` 13 /
   `RECORDED` 18 — and 40 + 13 + 18 = 71 exactly.
2. **`PROVENANCE.md` §2.4** — one row per attack A1–A6 with the *rejected-by-Razorpay* column and
   every constant tagged; the inversion carried in `CONTEXT.md` §6's own words; **A5 marked entirely
   `[merchant-policy, author-chosen]`** in the table, in its own headed subsection, and at RS-20.
   §2.2 and §3.2 gained **append-only landing notes**; no existing row was rewritten.

### Every quote was fetched, and every quote was then checked back against the bytes

**All 10 pages returned HTTP 200 and were fetched twice, six minutes apart, byte-identical both
times** — so the review's re-fetch diff is a real test, not a coin toss. SHA-256 of every page is in
§1. **`refunds.go:73-75` was verified first-hand at the pinned SHA and has NOT drifted**;
`grep -rni "idempot"` over the whole 94-file archive returns **0 hits**; the SDK's `extraHeaders`
slot is `resources/payment.go:44`. **All five instant-settlement bounds were found.** Three carry a
published figure (settlement balance; **₹5 Cr**; **₹2 L** outside banking hours); **two — the daily
withdrawable limit and the max attempts/day — are documented WITHOUT one, and this session invented
neither.**

### The finding that came out of checking my own file

The file's premise is *"a `>` block is a verbatim quote."* A mechanical check — strip the `>`, grep
the remainder against the fetched bytes — found **17 lines that were this session's own commentary
sitting inside quote blocks**. They were **rewritten, not excused**: RS-12(iv)'s greps became a
table, RS-22's warning became plainly-labelled commentary beside the quote it qualifies, and RS-49 —
the one quote whose source is HTML and therefore not a contiguous run of bytes — became a table of
five individually-verbatim text nodes with the joining declared. **The check now reports 299 of 299
matched, 0 unmatched, and it is written into the file so the review can re-run it.**
This is **INC-13's** lesson generalised: a `>` block that reads as Razorpay's text but is the
author's is the same failure as a `0x08` that renders as nothing.

### Six findings — all against this project's own records, none against Razorpay

⚠️ **No Razorpay page's text has changed since 2026-08-30.** Every string `CONTEXT.md` §6 and §9.2
attribute to a Razorpay page was found on that page, verbatim. **Zero divergences.** The findings are
of a different kind, listed as F-01…F-06 in `RAZORPAY_SEMANTICS.md` §9:

- **F-06 (HIGH)** — Razorpay documents `receipt` as *"treated as an idempotency key"*, and `receipt`
  **is** one of `create_refund`'s five parameters. The S2 finding **survives** — both mechanisms are
  opt-in and only the header is *structurally* unreachable — but the claim is narrower than *"the
  tool sends no idempotency key."* **Class A; recorded and NOT defaulted past. `Q-017` owed.**
- **F-01 (MEDIUM)** — `CONTEXT.md` §6 attributes *"will settle the maximum amount possible and ignore
  amount parameter"* to two docs pages. **It is on neither.** It is the MCP server's own tool
  description, which `CONTEXT.md` §2 cites correctly. One string, two attributions, one spec.
- **F-05 (MEDIUM)** — ~40% of the documented errors are account-configuration errors no world can
  reach, so C4's *"every documented Razorpay error fires"* is unsatisfiable once the file is
  complete. The `MUST-FIRE` / `RECORDED` split gives it a denominator. **`Q-018` owed.**
- **F-02 (MEDIUM)** — the ₹2 L bound is conditioned on *"banking hours"*, which **no page defines**.
- **F-03 (LOW)** — three different published instant-settlement minimums (₹1 / ₹2,000 / ₹100), plus
  ₹2 in the MCP tool. A floor; the attack pushes up. No reported number depends on it.
- **F-04 (LOW)** — `PROVENANCE.md` §2.2's *"₹500 ex-tax on ₹2,00,000"* is 500 **paise** on 200,000
  **paise** in the source. **The rate is identical (0.25%) and golden 1's four vectors are
  unaffected**; the units in that descriptive sentence are off by 100×.

### One addition that changes how C4 must build the world

**RS-26 — refunds are paid out of the merchant balance**, the same balance
`create_instant_settlement` sweeps: *"Refunds are paid out from the merchant balance, not directly
from the original payment."* **This couples A4 to A2 and A3.** A world modelling two independent
pools lets an attacker drain the balance *and* refund out of it, **counting the same rupees twice** —
which is `INCIDENTS.md` INC-03's failure with a fresh mechanism. The world's ₹5,00,000 opening
balance is *smaller* than the 12-payment captured total, so this fires in ordinary play, not only
under attack. **28 such additions are recorded (RS-26…RS-53).**

### Verification

| | Before (dirty tree) | After (committed) |
|---|---|---|
| `python -m whetstone_gate.tasks test` | **1 failed, 79 passed, 1 skipped, 2 deselected** | **80 passed, 1 skipped, 2 deselected** |
| `python -m whetstone_gate.tasks check-roles` | **15 passed, 0 failed, 4 n/a** | **15 passed, 0 failed, 4 n/a** |

⚠️ **The suite count MOVED from the 61 this session's prompt predicted to 79.** The concurrent C0 FIX
session added `tests/test_c0_fix_probes.py` and its C0 BLOCKER fixes. **Said, not investigated and
not touched**, exactly as the prompt directs. The single failure before commit is **OF-07** — it
named `PROVENANCE.md` (mine, uncommitted) alongside three files of the concurrent session — and it
went green on commit. **It was not weakened and it was not touched.**

### Owed to the architect

**`Q-016`** (the ruling that C1's golden is Razorpay's own documentation), **`Q-017`** (F-06, Class
A), **`Q-018`** (F-05) — full text in this session's `FINAL OUTPUT` block and in
`docs/sessions/c1-build-1.txt`. `QUESTIONS.md` was outside this session's fence.
**No `INCIDENTS.md` entry is owed.** Nothing broke: the 17 quote-block lines were found by a check
this session wrote and were fixed before the first commit, so there is no `Event`, no violated
`Expectation` and no ignored `Missed` signal — and rule 13's own closing note warns against
dramatising an entry that reads well. The reasoning is stated so a reviewer can overturn it on the
reasoning rather than on the conclusion (the `Q-011` precedent).

---

## C0 — ARCHITECT-ARTEFACT LANDING — BUILD — attempt 1 — 2026-08-31

**SESSION-TOKEN:** `e210c6f5` — 8 hex, `PROCESS.md` §7a's shape, generated by the **architect** with
`secrets.token_hex(4)` and issued in the architect's own message, carried as the `Session-Token:`
trailer on all six of this session's commits and recorded in `QUESTIONS.md` `## Session tokens`.
⚠️ **This session recorded its own row, and says so there.** The two rows beside it — `c9521aac`
(C0 FIX) and `20cd5b79` (C1 BUILD) — were recorded **by a different session from the ones that will
use them, and before those sessions ran**, which is the shape §7a intended and which `52f5307b`
could not achieve.

**Role:** BUILD — documentation and config only. **No logic was written and no defect was fixed**,
with one exception forced by the work itself (see *The finding* below).

**Token spend: NONE.** Zero provider model calls of any kind — no Groq call, no Google call,
nothing that consumed a lane's quota. No network operation of any kind was performed.

### What landed

1. **The twelve rulings, verbatim** — Q-001, Q-002, Q-003, Q-004, Q-005, Q-007, Q-009, Q-010,
   Q-011, Q-012, Q-014, Q-015. Each entry's `**Status:**` became **RULED** while **keeping the
   prose that records what it was before**; no existing text was deleted from any entry. Q-006 and
   Q-008 were left untouched — both are **OPERATOR** actions, not architect rulings.
2. **Three session-token rows and the first concurrent pair, P-01** (C0-FIX + C1 BUILD). §1's
   concurrency rule names *"two BUILD sessions"*; **the rule is extended to a FIX+BUILD pair and
   that extension is recorded rather than assumed**, together with the journal-collision hazard
   (`STATUS.md`, `PROGRESS.md`, `INCIDENTS.md` are shared) and the operator's twice-rejected-push
   stop rule.
3. **`docs/reviews/ARCHITECT_CHECK_0.md`** — the architect's C0 verification block, which
   `PROCESS.md` §11 requires before any `cN-pass`. **It records its own process deviation first**:
   §11 and §1 require it **before** the chunk's review, and C0's review ran a day earlier.
   §13.4's three branches recomputed = **MATCH on every cell**; B-01…B-04 each **CONFIRMED from the
   architect's own reading of the source**; **verdict: C0's FAIL is UPHELD, no `c0-pass`.**
4. **`CONTEXT.md` v1.2** — three defect corrections with one change-log row (§16's tree re-nested
   under Q-004; §16's mingw path under Q-005; §8.6's eight added constants under the architect's own
   finding). **No number §13.4 publishes moves.**
5. **`config/protocol.yaml`** — `gate_judge.target_tokens_per_call: 1500` and
   `benign_solver.target_tokens_per_episode: 50000`, the two constants that existed in **neither
   §8.6 nor `config/`**. ⚠️ **Legal only because `prereg-v1` does not yet exist.**
6. **`PROCESS.md`** — three done-when additions (C11 under Q-003's rider, C19 under Q-010, C21's
   billing re-check, which closes a gap `STATUS.md` had carried as *OWED TO THE ARCHITECT* since
   30 Aug) and the new **§11a RECORDED DEVIATION — OVERNIGHT AUTONOMOUS OPERATION**.

### The finding — Q-005 was misdiagnosed, and the defect was a control byte

**`CONTEXT.md` has carried a literal `0x08` BACKSPACE byte since v1.0 (`104fc74`).** The §16 string
is `C:\MinGW` + `<BS>` + `in\mingw32-make.exe`. A backspace renders as nothing, so every viewer —
and every session, and the review — displayed `C:\MinGWin\...`, and **Q-005 recorded it as a prose
typo.** It is not a typo.

It was found only because the `Edit` tool refused to match the string `MinGWin`, three times, while
`grep` and the file viewer both showed it. **The tool's refusal was correct and the display was
wrong.** Confirmed with `od -An -tx1`: byte `08`. Confirmed present in `HEAD:CONTEXT.md` and in
`310488d:CONTEXT.md`, and absent from `git diff` — i.e. **committed, not introduced by this
session.** A sweep of every tracked file found it to be **the only C0 control byte in any tracked
text file** (the two PNGs excepted, correctly). It is now repaired, and the repair was made with a
script containing **no backslash characters at all**, per INC-12's guardrail, which then verified
that the file grew by exactly one byte and that zero control bytes remain.

**The ruling's ACTION was right even though its DIAGNOSIS was wrong** — correcting the path to
`C:\MinGW\bin\mingw32-make.exe` is exactly what removes the byte. The ruling was pasted **verbatim
as instructed and was not "improved"**; the correction is recorded here and in the report instead.

⚠️ **AN `INCIDENTS.md` ENTRY IS OWED.** It is not written here because **the concurrent C0 FIX
session owns `INCIDENTS.md` tonight** and this session's scope fence forbids it. **The full
rule-13 entry is in this session's FINAL OUTPUT block**, committed to
`docs/sessions/c0-arch-landing-1.txt`, for the architect to place.

### Why no check could see it

- **A3** scans for CRLF. A backspace is not a line ending.
- **A4** compares worktree bytes against the blob. **They agree exactly** — git converts nothing —
  so §6a's fingerprint property genuinely holds and A4 is not failing at its own job.
- **OF-01's proposed discriminator would NOT catch it.** That one keys on *"git calls this file
  binary, yet it holds no NUL byte."* Here git correctly calls `CONTEXT.md` **text**: a lone `0x08`
  does not trip git's binary heuristic, which keys on NUL.
- This is **INC-10's `Missing` field arriving a second time**: *"nothing checks a tracked document's
  CONTENT, only its line endings."*

### Verification

| | Before | After |
|---|---|---|
| `python -m whetstone_gate.tasks test` | **61 passed, 1 skipped, 2 deselected** | **61 passed, 1 skipped, 2 deselected** |
| `python -m whetstone_gate.tasks check-roles` | **14 passed, 0 failed, 3 n/a** | **14 passed, 0 failed, 3 n/a** |
| `check-roles` **F2** sentinel count | **6** | **6** — unchanged, as required: two **determined** values were added, not sentinels |

Mid-session, with `CONTEXT.md` and `config/protocol.yaml` edited but uncommitted,
`test_the_object_store_and_the_working_tree_agree` failed **naming exactly those two files** — that
is **OF-07**, it is known, it is not this session's to fix, and it went green on commit. It was not
weakened and it was not touched.

### A bookkeeping slip, recorded rather than tidied

**Tasks 1 and 2 landed in ONE commit (`b7ca648`), not two.** Both edit `QUESTIONS.md`, and both sets
of edits were in the working tree before the first commit was made. The message names the rulings
only. **History is never rewritten, so it stands**; it is recorded here and in the report so the
mismatch between that message and that diff is explained rather than discovered.

### What a later session needs

1. **Q-005's entry still reads "typo".** The ruling is verbatim and binding; **the mechanism it
   states is wrong** and the correction lives here, in `STATUS.md`, and in `CONTEXT.md` v1.2's
   change-log row. Do not re-derive it.
2. **Q-011's entry contains stale arithmetic** — *"~71M ÷ 1.92M = 36.98 h ✓ (§13.4 says ~37 h)"* and
   *"~65M ÷ 1.92M = 33.9 h ✓"*. Those figures were **superseded the same day by Q-013 / v1.1**
   (69.10M = 35.99 h; 59.30M = 30.89 h). The entry's **conclusion is unaffected** — it argues that
   §13.4 assumes no caching discount, which is still true — but **the numbers it reproduces are the
   pre-correction ones.** Left in place: it is history, and this session deletes no existing text.
3. **`ARCH` is not yet parseable.** This session's `## Session tokens` row says `C0` where `ARCH`
   would be honest, because `_TOKEN_ROW` cannot match `ARCH` until the C0 FIX session lands
   Q-014 (iii). The row explains itself. **It is not to be rewritten retroactively** — the commits
   it names already carry it.

**Pushed SHA:** see this session's FINAL OUTPUT block in `docs/sessions/c0-arch-landing-1.txt`.

---

## C0 — REVIEW — attempt 1 — 2026-08-30

**SESSION-TOKEN:** `52f5307b` — 8 hex, `PROCESS.md` §7a's shape, carried as the `Session-Token:`
trailer on this session's commit and recorded in `QUESTIONS.md` `## Session tokens`. ⚠️ **The row was
written by the session it names**, because omitting it would make E1 fail on my own commit and turn
C0's *"`make check-roles` runs"* box red for a bookkeeping reason. That is an honour-system act inside
an honour-system control and the row says so.

**Verdict: FAIL. Four BLOCKERs. No `c0-pass` tag was cut. Nothing was fixed.**

**Token spend: NONE.** Zero provider calls. The only network operations were `git clone` /
`git ls-remote` against this project's own remote and one anonymous HTTP request to the repository URL
to establish that it returns 404, i.e. is private.

### The finding, in one sentence

**C0's deliverable is a set of checks, and four of them report PASS over nothing.** `check-roles`
**E2 and E3 cannot fire at all**; **D3 — the file's own docstring calls it "the whole moat" — is
defeated by hard rule 8's own named spike defect**; the **F group reports `config/` complete over a
`config/` that has lost `protocol.yaml`, while printing that `protocol.yaml` parsed**; and
**`make selftest`, the pre-spend gate, flips RED → GREEN when the key it guards is deleted.**

### What was verified and holds

- **All three baselines reproduce exactly** from a clone of the *remote* into a fresh directory with
  `core.autocrlf=false` and a new venv: **41/1/2**, **14/0/3**, **1 failed 1 passed 42 deselected**.
- **`make test` does not need `tau2-bench`** — the clean venv does not have it and the suite is green,
  which disproves the "it only passes because tau2 is ambient" hypothesis outright.
- **The line-ending property re-derives independently.** 40 tracked files, **0** skipped, **0**
  mismatches between working-tree bytes and `git show HEAD:`. Both PNGs are `i/-text w/-text` with
  identical filtered and unfiltered blob ids. `.gitattributes` is in the root commit.
- **The provenance chain verifies from two directions.** `git show 310488d:CONTEXT.md | tail -n +35 |
  sha256sum` → `10f6746c…`, and `sha256(PROJECT_SPEC.md)` **at source** is the same digest.
- **§13.4 is internally consistent to the stated precision** — every cell of the component table
  recomputed from the block table and the four feasibility bullets; 76.90M/40.05 h, 69.10M/35.99 h,
  59.30M/30.89 h all check out, and the corrected chain terminates inside 32 h as the ruling claims.
- **Secrets, spend and leak: clean.** No `.env` tracked; an independent `git log -p --all` scan
  against 8 key shapes returns zero hits; `evals/` does not exist. Of the **17** files in the research
  directory, exactly **two** came across — `PROCESS.md` byte-identical, `PROJECT_SPEC.md` as
  `CONTEXT.md` — and the 5.5% / 3.2% line overlap from the two changelogs is **100% explained** by
  those two files quoting themselves. Zero lines unaccounted for; zero in any `docs/sessions/`
  transcript.

### The number that matters most

**Mutation testing: 6 of 19 mutants killed before the probes.** Twelve behaviour-changing mutations —
including *`check-roles` no longer detecting a tracked `.env` at all* and *the secret scanner reduced
to 1 of its 8 patterns* — left `make test` at exactly `41 passed, 1 skipped, 2 deselected` and
`make check-roles` at exit 0. The cause is uniform and is the whole review: **the suite asserts that
each check passes on this repository, which is a state in which every check passes trivially.** Only
three tests in the entire suite build a fixture that should make a check FAIL, and all three are
INC-09's CRLF work.

**20 kept probes added** (`tests/test_c0_review_probes.py`) take that to **17 of 19**. The two left are
**M15**, deliberately — a probe there would leave a green test standing over the moat BLOCKER — and
**M20**, which is an equivalent mutant.

### The four reserved rulings

- **F1 (early return):** real, MEDIUM, **not** a false PASS. It loses information, not the verdict —
  but `INCIDENTS.md` INC-07 diagnosed exactly this shape, fixed it in `check_secrets`, named
  `check_gitattributes` as the survivor and accepted it. **I do not accept it**, and its larger form
  (F-13) *does* cross checks: an exception in `check_gitattributes` silences the secret scan.
- **F2 (Q-012 / A4 vacuity):** **sufficient. No revert. The screenshot box stands.** I re-derived the
  property myself rather than taking the test's word: rule 6 forbids weakening an assertion, not
  withdrawing a false one, and every failure the narrowing removed was a false positive *with respect
  to the property actually asserted*. The withdrawal is carried in A4's own printed output, which is
  the one place a future reader cannot skip.
- **F3 (OF-01, lone CR):** confirmed, **stays OPEN**, re-scoped. New fact: **§6a's fingerprint property
  is not violated by a lone CR** — worktree bytes and blob are identical — so A3/A4 are not failing at
  their own job; the gap is the *content* property INC-10's `Missing` field already names. The
  discriminator is sound, is **not** circular (it compares git's verdict against an independent signal),
  and is now a kept probe in `make test` — but `check-roles` still cannot report it.
- **F4 (Q-014, malformed token):** **it must FAIL, not be silent. MEDIUM, due before C1 is reviewed.**
  The project's own doctrine is *"rules fail closed"*; E4 currently prints a **false statement** about
  four commits with the wrong cause attached; and the architect's 8-hex ruling is precisely what makes
  failing closed safe. Cost: four lines and a second, permissive pattern feeding a new `E5`.

### What a later session needs and would otherwise re-derive

1. **`repo_root()` will fool you.** It is `Path(__file__).resolve().parents[2]`, so with one venv and
   two checkouts, `check-roles` reports on the **venv's** checkout, silently. **It fooled me for one
   experiment** — I corrupted `.gitattributes` in one clone and got a full green report from the other.
   No target prints the root it used. That is **OF-09**.
2. **`make test` is red for the whole middle of any session** (OF-07), which is what produced
   **INC-11**: a mutation run scoring 18/18 including a control mutant that should have survived. If
   you mutation-test this repository, **commit the mutant first and always include a control.**
3. **INC-12 is the third occurrence of INC-06's quoting defect**, this time in a review session's own
   tooling, caught by a Python parser rather than by any check. Author files with the write/edit tools;
   the heredoc path has now failed three times in three sessions.

### Scope discipline

**No source file was modified. No fix was made. No tag was created.** What was added: the review
(`docs/reviews/REVIEW_C0.md`), 20 kept probes, the independent re-implementation
(`docs/reviews/independent/c0_config_loader.py`, written from the spec text alone and importing nothing
from the project), thirteen ledger rows in `OPEN_FINDINGS.md` (OF-02…OF-14 plus an OF-01 status
update), **Q-015** (hard rule 8 routes allow-list decisions through `QUESTIONS.md` by name), and
**INC-11** / **INC-12**.

---

## CTX-13.4 — BUILD — attempt 1 — 2026-08-30

**SESSION-TOKEN:** `WG-2026-08-30-CTX-13.4-A` — **the first token this project has issued.**
Carried as the `Session-Token:` trailer on both commits, **verbatim as issued**. ⚠️ It is **not**
the 8-hex shape `PROCESS.md` §7a specifies and `check_roles.py` enforces, so **`check-roles` cannot
see it**: E4 counts these two commits among the *"carry no trailer"* list even though the trailer is
there, and E1 — the forged-token check — is **silent**, not passing. Raised as **Q-014** and **not
fixed**: the fence says record, and `CLAUDE.md` §5 forbids inventing a conforming token.

**Scope:** one correction. `CONTEXT.md` §13.4 and its version header, plus `QUESTIONS.md`.
**Nothing else** — no config, no test, no source, no `PROCESS.md`, no tag, and **the early-return
shape in `check_gitattributes` is still untouched and still reserved for C0's review.**

**Token spend: NONE.** Zero provider calls of any kind.

### What landed

1. **`CONTEXT.md` §13.4's two N=30 fallback projections corrected** under the Q-013 ruling:
   *"~71M tokens ≈ 37 h"* → **69.10M = 35.99 h**, and *"(−6M tokens → ~34 h)"* → **−9.80M →
   59.30M = 30.89 h**. The N=50 headline **76.90M / 40.05 h was correct as published** and is
   unchanged, and so is the decision rule — structure, branches, thresholds and its *"No other
   branch. No post-hoc adjustment."* clause.
2. **A per-branch component breakdown table**, because **the absence of one is why the error
   survived.** Every cell is §13.4's own four feasibility bullets re-evaluated at each branch.
3. **`CONTEXT.md` at v1.1** with its first change-log row, and the header's byte-identity claim
   against `PROJECT_SPEC.md` marked **SUPERSEDED** — diverged in §13.4 only, with the v1.0 digest
   **retained** as the common-ancestor record.
4. **Three rulings recorded in `QUESTIONS.md`, Q-013 CLOSED**; **Q-014 raised.**

### The three things worth reading the diff for

1. **The arithmetic was re-derived here before it was written, not taken on trust.** The prompt
   said so in as many words — *"the architect has been wrong before and being told a number is
   verified is not verification"* — so all three branches were recomputed from §13.4's four
   component bullets. **All three matched the architect's figures exactly**, to the cent and to two
   decimal places of lane-time: 76.90M/40.05 h, 69.10M/35.99 h, 59.30M/30.89 h. Had they not, the
   instruction was to STOP rather than write them.
2. **The consequence is the point, and it is now in the file.** As published the chain ran
   **40 → 37 → 34 h against a 32 h budget** and therefore **never reached its own budget**, with no
   branch left. Corrected, it lands at **30.89 h**. The error was not decoration on a sound plan;
   the corrected numbers are what make the plan's own escape hatch work. **Both slips were
   conservative** — they made the budget look tighter, never looser.
3. **The byte-identity note was updated, not deleted.** Deleting the digest would have erased the
   only evidence that the divergence is exactly §13.4 and nothing else. It is now labelled the
   **common ancestor**, the check is rewritten to run against commit `310488d`, and **that command
   was executed and reproduces the digest.** The working-file form is documented as
   **expected to fail** from v1.1 on, so a later reader does not read the divergence as damage.

### Checks, against their values before this session

| Check | Before | After |
|---|---|---|
| `make test` | 41 passed, 1 skipped, 2 deselected | **identical** |
| `make check-roles` | 14 passed, 0 failed, 3 n/a | **identical** — E4's *"carry no trailer"* list grew 16 → 18 (see Q-014); no result changed |
| `make selftest` | 1 failed, 1 passed, 42 deselected — **red on purpose**, `camel_comparator.branch` is `TODO_C13_RUN1` | **identical** |

⚠️ **`make test` was transiently red mid-session and is green again.**
`test_the_object_store_and_the_working_tree_agree` compares the working tree against `HEAD:`, so it
fires on **any** uncommitted edit to a tracked file, including this one. It is not a defect and it
is not this session's to change; it means **`make test` is only meaningful once the work is
committed.** Recorded here so the next session is not surprised by it. **Nothing was weakened,
skipped or loosened to get green** (hard rule 6) — the commit is what made it pass.

**`INCIDENTS.md`: no entry.** Nothing broke. No test failed on its merits, no artefact was damaged,
no run aborted. Hard rule 13's *"an invented incident has no commit"* cuts both ways, and inventing
one to look thorough would be the dramatisation it warns against. The one process point worth
stating is not a failure: **hard rule 5 wants the ruling recorded before anything else is touched,
and the working-tree edits were made before `QUESTIONS.md` was written.** The **permanent record is
the commit order**, and the ruling commit `ec3064d` precedes the correction commit `d67550e`
deliberately for that reason. Disclosed rather than smoothed over.

---

## C0-COMPLETION — BUILD — attempt 1 — 2026-08-30

**SESSION-TOKEN:** ⚠️ **none issued.** This prompt, like C0's, carried no `SESSION-TOKEN`
line, and this session **did not fabricate one** — the prompt said so explicitly and
`QUESTIONS.md` **Q-001** already records the gap and the reasoning. Every commit here is
permanently untrailered, and `check-roles` E4 reports that as `n/a` naming Q-001, never as
a pass.

**Scope:** the **three operator-owed items** that C0 reported as FAIL-pending-operator,
now supplied. Nothing else. **No project logic** — no world, ledger, scorer, gates,
attacker or adapters.

**Token spend: NONE.** Zero calls to any Groq or Google model. Writing a model id into a
config file is not a call, and validating an id against the live endpoint is a later
chunk's job that needs the operator's key.

### What landed

1. **The four Google API model ids** (closes **Q-006**), captured by the operator from the
   live models endpoint on 2026-08-30 — `models/gemma-4-26b-a4b-it`,
   `models/gemma-4-31b-it`, `models/gemini-3.1-flash-lite`,
   `models/gemini-3.5-flash-lite` — with each lane's `inputTokenLimit`,
   `outputTokenLimit` and `supportedGenerationMethods`, and the **preview-vs-stable
   ruling** written down so nobody re-derives it under time pressure.
2. **Both dashboard screenshots** (closes half of **Q-008**), with byte sizes, SHA-256
   digests, and a structural PNG validation.
3. **The no-payment-method attestation** (closes the other half of **Q-008**), labelled
   **OPERATOR-ATTESTED**, with what the property actually buys written out beside it.

### The three things worth reading the diff for

1. **`make selftest` is still red, and the report says so in the first paragraph.** The
   placeholder gate is now green; the remaining failure is
   `test_the_camel_branch_is_decided_before_any_camel_run` — `TODO_C13_RUN1`, owned by
   RUN-1 on 31 August. A different reason, reported as a different reason. `STATUS.md`
   now carries a *"what `make selftest` is still waiting on"* table so a red gate is never
   mistaken for missing ids again.
2. **The caching finding was verified, not accepted.** The prompt said the architect had
   already checked that §13.4 is unaffected. It is — `grep -ic cach CONTEXT.md` returns
   **0**, and §13.4's figures re-derive exactly from raw throughput (32,000 × 60 =
   1.92M/h; 76.9M ÷ 1.92M = 40.05 h against its stated ≈40 h; ~37 h and ~34 h likewise).
   **Q-011** records the fact, the verification, and the forward consequence: caching is
   **not** an available lever for the §13.4 lane-hour gap, and it would not help on the
   Flash Lite lanes either, because those are **request**-bound and caching reduces
   *tokens*. The **rule-13 judgement is stated from rule 13's own text** — no `Event`, no
   violated `Expectation`, no causal mechanism for `Diagnosis`, no ignored signal for
   `Missed`; writing it as an incident would mean inventing two mandatory fields, which is
   the dramatisation rule 13's closing note warns against. **QUESTIONS entry, not an
   incident.**
3. ⚠️ **The screenshots broke the build, and the break was real — INC-09.** They are the
   repository's first binary files. `check-roles` **A3** scanned every tracked file's raw
   bytes for `\r\n`, and a PNG's deflate stream carries those bytes as data, so `make
   check-roles` and `make test` went red on a sound repository. **`.gitattributes` was
   innocent** and is unchanged — `git ls-files --eol` says `i/-text w/-text` and
   `git hash-object` with and without `--no-filters` agree, so `* text=auto` already
   detects them as binary. The prompt's conditional *"if they are being treated as text"*
   **did not fire**, and adding an image rule would have broken A1 anyway. What was fixed
   is A3 itself, **without weakening it**: A3 keeps its assertion over every file **git**
   calls text, and a new **A4** asserts the underlying property — would git's filter chain
   rewrite these bytes? — over **every** tracked file. Proven meaningful against the
   pre-fix module loaded out of the object store. **Q-012** records it as a Class B
   deviation with the reasoning exposed, because a session that changes a structural
   invariant should not be the only one who thinks the change was sound.

### Corrections made rather than carried forward

- **"six Google API model ids" → FOUR.** `config/lanes.yaml`'s header and `PROVENANCE.md`
  §2.3 both said six; there are four Google lanes and the gate reported four placeholders.
- **Q-006 names the gate file as `tests/test_lanes_no_placeholders.py`.** The file is
  `tests/test_lanes_operator_placeholders.py` and never had the other name. Both
  corrections are recorded **in Q-006's closure**, with the original text left standing —
  a question log that edits its own history is worth less than one that shows the fix.

### What was deliberately NOT touched

The `check_gitattributes` **early-return shape** that C0's own report names as a candidate
defect. The scope fence reserved it for C0's review and pre-empting it would remove the
reviewer's finding. It is still there.

---

## C0 — BUILD — attempt 1 — 2026-08-30

**SESSION-TOKEN:** ⚠️ **none issued.** The C0 build prompt carried no `SESSION-TOKEN` line,
and this session **did not fabricate one** — a fabricated token would be exactly the
*"token that was never issued"* that `make check-roles` exists to catch, and it would put a
forged credential in the audit trail of a project whose thesis is that self-certified
evidence is worthless. Recorded as **`QUESTIONS.md` Q-001**; C0's commits are permanently
untrailered and that gap is visible rather than papered over.

**Scope:** the repository, the toolchain, the private remote, the canonical files, and
`CONTEXT.md` §13.7's day-one provider setup. **No project logic** — no world, no ledger,
no scorer, no gates, no attacker, no adapters.

**Token spend: NONE.** No call to any Groq or Google model, not one. The chunk needed
none, and the two things that *do* need a provider — the exact Google API model ids and
the dashboard screenshots — are reachable only by the operator, not by any session.

### What was built

- **Repository** at `github.com/chinmoypaul8897/whetstone-gate`, **PRIVATE**, branch
  `main`. It stays private until C21 flips it on 4 September, after the git-history secret
  scan.
- **`.gitattributes` (`* text=auto eol=lf`) in the FIRST commit**, `ee3cf93`, with
  `.gitignore`, `LICENSE` and `INCIDENTS.md`. This is `PROCESS.md` §6a's prerequisite and
  it is fixable only in the first commit.
- **`CONTEXT.md` v1.0** — a byte-identical copy of the audited `PROJECT_SPEC.md` under a
  version header and an empty change-log, with the identity claim made checkable:
  `tail -n +35 CONTEXT.md | sha256sum` reproduces the source digest.
- **`PROCESS.md`**, unchanged and verified identical by SHA-256.
- **`CLAUDE.md`** — the constitution. All **thirteen** hard rules extracted **verbatim**
  (`diff` against `PROCESS.md` §4 is empty), plus §6b's single-shot rule verbatim, the read
  order, the token/key rules, the git rules and the end-of-session duties.
- **`STATUS.md`**, **`PROGRESS.md`**, **`QUESTIONS.md`**, **`PROVENANCE.md`**,
  **`ARCHITECT_HANDOFF.md`**; `docs/personas/` (three files, verbatim from §5.3),
  `docs/reviews/` + `OPEN_FINDINGS.md`, `tests/goldens/` (**empty — C0 authors no
  golden**).
- **Toolchain.** Python **3.12.2** venv; the `make` shim installed to `~/bin/make.exe`
  (GNU Make 3.82.90, verified to execute a recipe); τ²-bench installed editable at the
  pinned SHA; a **logic-free** `Makefile` whose every recipe is a one-line delegation.
- **`config/` + one loader** with **no defaulting accessor at all**, plus the hard-rule-9
  tripwire and its coverage test.

### The four things worth reading the diff for

1. **`.gitattributes` was verified, not assumed.** A clone with `core.autocrlf=false`
   (simulating a Linux reviewer) reproduces **byte-identical** SHA-256 digests to this
   Windows working tree, on every tracked file. That is the property `PROCESS.md` §6a's
   fingerprint depends on, and it now has evidence rather than an intention.
2. **The config loader has no `get(key, default=...)`, and a test asserts it does not.**
   Hard rule 9 is a hard refusal, so the API has nowhere to put a fallback. Values that are
   *not yet decided* — the void threshold, the N branch, the Google ids, the AgentDojo/CaMeL
   SHAs — are explicit `TODO_` sentinels that **raise on read, naming who owes them**. If a
   missing void threshold silently read as `0.0`, every run would clear the void check, the
   project's central control would be inert, and nothing would have raised.
3. **The tripwire has two modes and a coverage test, and it is proven to fire.** STRICT for
   distinctive literals; CONTEXTUAL for small integers that recur innocently (`range(20)`
   is fine, `turn_budget = 20` is not). A separate test asserts the registry covers every
   `CONTEXT.md` §8.6 row — without it a constant could be dropped from the registry and the
   scan would stay green while no longer scanning for it.
4. **`make selftest` is RED on purpose and `make test` is green.** Two of C0's own
   done-when boxes contradict each other (`QUESTIONS.md` Q-009); the resolution is two
   tiers, both real. `make test` prints how many operator-gate tests it deselected and why.

### Verification

| | |
|---|---|
| `make test` | **38 passed, 1 skipped, 2 deselected — exit 0** |
| `python -m whetstone_gate.tasks test` | identical result, **exit 0** |
| `make check-roles` | **12 passed, 0 failed, 4 n/a — exit 0** |
| `make selftest` | **2 failed — exit 2. Correct.** No token may be spent against a guessed model id |
| `make check-prereg` / `make eval` | run; report NOT-YET-FROZEN, which is *"not yet"*, not a pass |
| clean clone | verified in a fresh directory — see the C0 report |

The 1 skip is `gates/`↔`scorer/` isolation: **neither directory exists yet** (C8, C9), and
`n/a` is asserted as `n/a` rather than counted as a pass.

### Questions raised

**Ten**, Q-001 … Q-010. The three that block later chunks:

- **Q-004** — `CONTEXT.md` §16's repo tree is self-inconsistent about whether `gates/`,
  `scorer/` and the rest live **inside** `src/whetstone_gate/` or **beside** it. The two
  readings differ in every import path in the project. **Must be ruled before C2.** C0
  created neither, and `check-roles` checks both layouts so it needs no edit when the
  ruling lands.
- **Q-003** — the C0 prompt asks for `evals/` outputs to be git-ignored; `CONTEXT.md` §16,
  `PROCESS.md` §9 and `PROCESS.md` §6b all require them **committed**. Ignoring them would
  make `make eval` unable to regenerate anything from a clean clone and would leave §6b's
  single-shot control unenforceable.
- **Q-010** — τ²-bench at the pin is **793 MB**, most of it other people's published model
  transcripts. Pinned rather than committed. **C19's clean-clone test must include the
  fetch step**, or §20's first box is false.

### Incidents

**Three written — INC-06, INC-07, INC-08 — all dated AFTER the first build commit**, which
is what hard rule 13 requires and what C21 must cite. All eight entries in the file carry
all eight mandated fields.

- **INC-06** is the one to read: a build script wrote **CRLF into four tracked files**, and
  `.gitattributes` caught it. That is *exactly* the failure `PROCESS.md` §6a exists to
  prevent — a fingerprint from a CRLF working tree would not match what any Linux or macOS
  reviewer computes from the same git objects, and it would have failed **at the moment of
  judging**, silently, looking like fraud rather than a line-ending bug. It arrived on day
  one instead. Two checks now assert the property on every run.
- **INC-07** — a checker emitted a different result key on pass than on fail, so its test
  **crashed instead of failing**. The test was not relaxed to accommodate it (hard rule 6);
  the checker was corrected. Its `Systemic guardrail` is honestly *"none — accepted"*, and
  it **names the same smell still present in `check_gitattributes`** as a live candidate
  finding for C0's review rather than leaving it to be discovered.
- **INC-08** — operator-facing output was unreadable on the operator's own terminal. The
  slightest of the three, and labelled as such.

### Owed to the operator

The **exact Google API model id strings** (`models/gemma-…`, `models/gemini-…`), the two
dashboard **screenshots**, and the **no-payment-method** confirmation. Only the operator
can supply any of them. `make selftest` fails until the ids land.

### Hold-point

C0 is **built, unreviewed**. It has not been self-certified and must not be.
**Next:** the architect's `ARCHITECT_CHECK_0.md`, then a C0 **`code`** review in a
different fresh session. C1 (`RAZORPAY_SEMANTICS.md`) and C2 (the world + the planted
probe) are the next builds, and **C2 needs golden 7 committed before its prompt is
issued.**
