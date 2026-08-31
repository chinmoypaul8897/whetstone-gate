# REVIEW_C1 — adversarial review of chunk C1, attempt 1

**SESSION-TOKEN:** `a0cc0212` · **Role:** REVIEW · **Chunk:** C1 · **Date:** 2026-08-31
**Review type:** `full` — personas 1 (evaluation integrity) **and** 2 (code), per `PROCESS.md`
§12.1's C1 row.
**Artefacts reviewed:** `RAZORPAY_SEMANTICS.md` (`55f1f2c`, its only commit) and `PROVENANCE.md`
§2.4 (`7a101a6`).
**Concurrent pair:** P-02 (C0 re-review, token `f57e216b`) was in flight. Its chunk is disjoint.
**Token spend: ZERO provider model calls.** 40 HTTP GETs to public documentation and to
`raw.githubusercontent.com` / `codeload.github.com`, permitted and required by `PROCESS.md` §11a.

---

# VERDICT: **FAIL**

**One BLOCKER.** It is not a defect in a quote, a digest or a count — **every one of those
verifies, and most of them verify perfectly.** It is that C1 established, correctly and
first-hand, that **two of A4's five bounds are documented by Razorpay without a figure**, wrote
three times that their author-chosen values *"live in `config/`"*, and **they do not live there,
or in `CONTEXT.md` §8.6's constants table, or anywhere else in this repository.**
`CONTEXT.md` §8.6 and `config/protocol.yaml`'s own header each say, verbatim:

> Any constant that is not in this table and not in `config/` is a defect, and finding one is a
> review BLOCKER.

**This is the fourth occurrence of that pattern**, in a section whose own text says *"THE THIRD
OCCURRENCE IS WHERE A PATTERN STOPS BEING BAD LUCK."* And it bites through a ruling **C1 itself
obtained**: Q-018 makes the `MUST-FIRE` set C4's done-when, RS-18 and RS-19 are both `MUST-FIRE`,
and **C4 cannot make them fire without inventing two constants the pre-registration does not
carry** — which is Q-018's own problem, reappearing one level down.

## ⚠️ What this verdict is NOT, stated first, because the evidence runs overwhelmingly the other way

This is the strongest artefact this project has produced, and the FAIL should not be read as
doubt about its content. Measured, not asserted:

| What was checked | Result |
|---|---|
| **All 10 quoted pages re-fetched, digests recompared** | ⚠️ **10 of 10 byte-identical.** Nine SHA-256s match to the character; S10's 109,181-byte count matches | 
| **Both pinned source trees re-fetched** | `refunds.go` SHA-256 identical raw and from the archive; the archive holds **exactly 94 files**, as claimed |
| **Both claimed-404 URLs, and all 6 discovery URLs** | 404 / 404 with the 135,098-byte shell; 200 on all six |
| **Every `Errors` entry on S1–S4 (79 of them) present verbatim in the file** | **79 of 79. Zero missing.** |
| **Partition recount, from the document** | **40 MUST-FIRE + 13 MUST-HOLD + 18 RECORDED = 71.** Exact. Every row in **exactly one** bucket; none unlabelled; RS-01…RS-71 contiguous |
| **§0's blockquote-is-verbatim check, re-implemented and re-run against all 12 sources** | **301 of 301 matched. Unmatched: 0** — the verdict reproduces exactly |
| **Every A1–A6 error string in `CONTEXT.md` §6** | resolves to a row, verbatim, **found independently in Phase 1 before C1's file was opened** |
| **All five instant-settlement bounds** | present; **three carry a published figure, two do not, and no figure was invented for either** |
| **A5 marked entirely author-chosen** | in `CONTEXT.md` §6, RS-20, `PROVENANCE.md` §2.4 and its own headed subsection |
| **Every `grep` claim in RS-12(iv) and `CONTEXT.md` §2** | `idempot` → 0, `X-Refund` → 0, `audit` → 0, `mcpgo.Max(` → 9, `mcpgo.Max(100)` → 6, `mcpgo.Min(` → 35, `Middleware` → 0. **All seven exact.** |
| **Razorpay pages changed since 2026-08-30** | **0.** No drift to record, in either direction |
| **Paraphrases found** | **0.** Razorpay's own typos survive intact — `10 character long`, `2 Lacs`, `authorised amount .` with its space before the full stop |

**C1 also found the fourth false third-party claim to reach this specification, in `CONTEXT.md`
§2, and it found it by reading the source it was already citing.** That is the chunk working
exactly as designed.

**The FAIL is about what the artefact caused and did not escalate, and about the fact that
nothing in this repository can detect it if a row goes wrong tomorrow.**

---

# 0. Method — and the substitution Q-016 ruled

`PROCESS.md` §10 template 2 makes a committed reimplementation a PASS condition for a `full`
review. **Q-016 (RULED, architect, 2026-08-31) substitutes a different obligation for C1**,
because C1 computes nothing. In its place this session **independently rebuilt the oracle from
Razorpay's documentation and source, blind**, and committed it **before** opening
`RAZORPAY_SEMANTICS.md`.

- **Phase 1 (blind):** `docs/reviews/independent/c1_oracle.md`, committed at **`f069486`**.
  26 rows (`IO-01`…`IO-26`). Read only `CLAUDE.md`, the two personas, `PROCESS.md` §12.1's C1
  row, and `CONTEXT.md` §2/§6/§9.2/§11.3/§15.2.
- **Phase 2 (sighted):** the diff, the re-fetch, the partition recount, the mutation run.
- **Diff:** `docs/reviews/independent/c1_oracle_diff.txt`.

⚠️ **Four deliberate 404s were run BEFORE any quote was recorded**, because a `200` from a
single-page app proves nothing. All four returned a genuine 404 with an identical 135,098-byte
body, so a `200` carrying markdown on this host **is** evidence of a page. C1 ran the same
control, on two different URLs, and reached the same conclusion independently.

---

# 1. Findings

Severity key follows `REVIEW_C0.md`: **BLOCKER** — cannot PASS with it open. **MEDIUM** / **LOW**
— goes to `OPEN_FINDINGS.md`. **INFO** — recorded here only.

| ID | Severity | Finding | Owner |
|---|---|---|---|
| **F-R4** | ⚠️ **BLOCKER** | Two author-chosen A4 constants — and a third, the banking-hours window — exist in **neither `CONTEXT.md` §8.6 nor `config/`**, while three project artefacts state that they *"live in `config/`"* | architect (both files are outside C1's fence) |
| **F-R5** | **HIGH** | §0's *"re-runnable check"* has **no committed implementation anywhere in the repository**. 4 of 12 corruptions are caught by **nothing**; 3 more only by that uncommitted check | C1 FIX + architect |
| **F-R6** | **HIGH** | The §0 check, **as specified**, matches each quoted line against **any** source rather than against **the source the row cites** — so a wrong HTTP code and a remediation lifted from the wrong page both pass it | C1 FIX |
| **F-R2** | **MEDIUM** | §0 publishes **299 of 299**. The file as committed carries **301** non-empty quoted lines. The *verdict* reproduces; the *denominator* does not | C1 FIX |
| **F-R1** | **MEDIUM** | RS-12's Notes says *"⚠️ **See RS-31.**"*. RS-31 is a different rule that explicitly disclaims being a duplicate-refund guard. The intended row is **RS-27** | C1 FIX |
| **F-R3** | **LOW** | `RS-70` is **two identifiers**: a RECORDED table row (the three `500`s) and a `### RS-70 (note)` heading. RS-16 and RS-65–RS-68 all say *"see RS-70"* | C1 FIX |
| **F-R7** | **LOW** | §10's opening sentence says *"Total: **14** items … All **14** resolve"* directly above a table of **18** and a counts row of **18** | C1 FIX |
| **F-R8** | **LOW** | `PROVENANCE.md` §2.4's A4 cell says *"only three carry a published figure (**balance**; ₹5 Cr; ₹2 L)"*. Razorpay publishes **no** figure for the balance — it is live merchant state | C1 FIX |
| **F-R9** | **INFO** | RS-17 is `MUST-FIRE` but its predicate is *"outside banking hours"*. C4 must model that as **seeded world state**, never `now()` — hard rule 8 | C4 |
| **F-R10** | **INFO** | Q-026 (`CONTEXT.md` line 178 still carries the sentence Q-017's ruling calls false) **independently confirmed**. Already OPEN; **not** a C1 defect | architect |

---

## F-R4 · ⚠️ BLOCKER · two A4 constants live in `config/` according to three files, and in no file according to `git grep`

### What C1 established, and established correctly

RS-18 and RS-19 are among the strongest rows in the artefact. Both say, in bold:

> ⚠️ **NO FIGURE IS PUBLISHED, AND THIS FILE DOES NOT SUPPLY ONE.**

**This session reached the identical conclusion blind** (`c1_oracle.md` IO-17, IO-18), from the
same two pages plus a check C1 also made — Razorpay's own closing sentence,
*"You can check the Dashboard for latest updates on the limits"*. **C1 invented no number.
Check 2f passes without qualification.**

### What follows from it, and what nobody carried

Two bounds documented without figures mean **this project must choose two values**. A third
follows from F-02: *"banking hours"* is defined on no page, so the window is ours too. Three
new `[merchant-policy, author-chosen]` constants. Where they are said to be:

| Where | What it says |
|---|---|
| `RAZORPAY_SEMANTICS.md` **RS-18** | *"The world therefore reads this ceiling **from `config/`**, tagged `[merchant-policy, author-chosen]`"* |
| `RAZORPAY_SEMANTICS.md` **RS-19** | *"the bound is `[Razorpay-defined]`, its value is `[merchant-policy, author-chosen]` and **lives in `config/`**"* |
| `PROVENANCE.md` **§2.4**, A4 | *"*its value* is `[merchant-policy, author-chosen]` and **lives in `config/`**"* |

Where they actually are — the search, run over every tracked file:

```
git grep -in "daily_withdraw\|withdrawable\|attempts_per_day\|max_attempts\|banking_hours"
```

Every hit is **prose naming the bound**. **Not one is a value.** `config/protocol.yaml` has no
such key. `CONTEXT.md` §8.6's constants table has no such row. `src/whetstone_gate/spec_constants.py`
— the tripwire registry, which that module's docstring says *"is a transcription of that table,
and nothing else"* — has no such entry.

### Why it is a BLOCKER and not a MEDIUM

**Three independent reasons, each sufficient on its own.**

1. **The rule is unconditional and it is stated twice.** `CONTEXT.md` §8.6 and
   `config/protocol.yaml`'s header both carry the same sentence: *"Any constant that is not in
   this table and not in `config/` is a defect, and finding one is a review BLOCKER."* It does
   not say "unless another chunk will add it later."
2. **It makes C4's done-when unsatisfiable — through the ruling C1 obtained.** Q-018's ruling,
   now in `PROCESS.md` §12.1's C4 row, reads: *"every `RAZORPAY_SEMANTICS.md` row marked
   `MUST-FIRE` fires in the mock world."* **RS-18 and RS-19 are both `MUST-FIRE`.** To fire
   *"Amount that can be settled for the day is exhausted"* the world needs a daily limit; to fire
   *"No more attempts left for today"* it needs an attempt count. C4's only routes are to invent
   two constants outside the frozen set — which is what §8.6 forbids — or to fail its done-when.
   **Q-018 was raised to give C4 a satisfiable denominator. This is that same problem one level
   down, and C1 is the chunk that would have seen it.**
3. **It is the fourth occurrence, and §8.6 has already declared the third to be the pattern.**
   Six rows added 30 Aug; eight added 31 Aug; the probe note (Q-022) added 31 Aug. §8.6's own
   text: *"EACH TIME IT WAS FOUND BY SOMEBODY TRIPPING OVER A MISSING CONSTANT, NEVER BY A
   CHECK."* This one was found the same way, by a fourth session, tripping over the same thing.

### What is C1's, stated precisely and no more broadly

C1 **could not** write to `config/` or `CONTEXT.md` — both are outside its fence, and refusing
to write into a pre-registration artefact from outside is the *correct* behaviour, endorsed by
Q-022's ruling. **C1 is not faulted for not fixing this.** What is C1's:

- **The route was open and C1 used it three times.** Q-016, Q-017 and Q-018 were declared OWED
  in `docs/sessions/c1-build-1.txt` §11, in `QUESTIONS.md` format, for the architect to place.
  **A fourth entry was not.** C2 BUILD did exactly this for the probe note and it became Q-022.
- **Three artefacts assert a location that is empty.** *"lives in `config/`"* describes the
  remedy as though it were in place. In `PROVENANCE.md` §2.4 — a table under the column heading
  *"Every constant, tagged"*, in a file whose §2.4 preamble promises *"This table asserts nothing
  that file does not source"* — that is a claim about this repository's state, and it is false.
- **F-02 named the banking-hours window and assigned it to *"C4 + `PROVENANCE.md`"***, not to
  §8.6 or `config/`. Half-right, and the half it misses is the half §8.6 calls a BLOCKER.

### Remedy — the architect's, one amendment, before `prereg-v1`

Three rows into `CONTEXT.md` §8.6, three keys into `config/protocol.yaml`, three rows into
`spec_constants.py`. **All three are legal only while `prereg-v1` does not exist** — the same
window, and the same argument, as Q-022's. ⚠️ **The values themselves are a Class A choice: they
set how hard A4's ceiling binds, and A4 is one of the three attacks that survive contact with the
real API.** They are not this review's to pick, and this review picks none.

---

## F-R5 · HIGH · §0's "re-runnable check" is re-runnable by nobody — 4 of 12 corruptions are caught by nothing

§0 does the right thing and says so well:

> **Re-runnable check.** Take every line of this file beginning with `>` … require the remainder
> to occur as a contiguous substring of one of the sources in §1 …
> **Result at the time of writing: 299 of 299 quoted lines matched. Unmatched: 0.**

and it invokes the right precedent — `INCIDENTS.md` **INC-13**, *"a `0x08` backspace that sat in
`CONTEXT.md` for two days … because nothing checked a tracked document's content."* §0 says this
*"mattered enough to fix rather than to note."*

⚠️ **There is no implementation.** Not in `tests/`, not in `src/`, not a `Makefile` target, not a
script. `make test` cannot detect a paraphrase in this file. **The fix was performed and not
kept**, which is INC-13's own lesson landing on the document that cites it.

### The mutation run — architect-ruled analogue, 12 mutants, throwaway copies only

⚠️ **ARCHITECT RULING, 2026-08-31:** for an oracle document the mutation analogue is *corrupt a
row and see whether anything catches it.* Twelve mutants, each applied to a copy in an OS temp
directory. **The artefact under review was never mutated in place**; the harness restores and
then re-reads to prove the restore, and `git diff HEAD -- RAZORPAY_SEMANTICS.md` was empty before
and after.

Detectors: **D1** = `tests/test_c1_review_probes.py`, committed by this review. **D2** = §0's own
check, implemented here per its stated algorithm — **not committed anywhere**. **D3** = the
re-fetch and digest comparison — **a review act, not a repeatable check**.

| # | Mutation | Where | D1 | D2 | D3 | **Caught by** |
|---|---|---|---|---|---|---|
| **M-01** | a changed digit in a figure — `₹ 5 Cr` → `₹ 6 Cr` | RS-16, inside the quote | miss | **CAUGHT** | miss | D2 *(uncommitted)* |
| **M-02** | **a dropped negation** — *"NO FIGURE IS PUBLISHED"* → *"A FIGURE IS PUBLISHED"* | RS-18 prose | miss | miss | miss | ⚠️ **NOTHING** |
| **M-03** | **a wrong HTTP code** — the in-flight `409` → `400` | RS-09, inside the quote | miss | miss | miss | ⚠️ **NOTHING** |
| **M-04** | a wrong URL — S3 → a path that 404s | §1 evidence table | miss | miss | **CAUGHT** | D3 *(review only)* |
| **M-05** | **a paraphrase replacing a quote** — `greater than amount captured` → `greater than the amount captured` | RS-03 | miss | **CAUGHT** | miss | D2 *(uncommitted)* |
| **M-06** | **a wrong `file:line`** — `refunds.go:73-75` → `:71-73` | RS-12(ii) | miss | miss | miss | ⚠️ **NOTHING** |
| **M-07** | **a row moved `MUST-FIRE` → `RECORDED`** | RS-21 (A6) | **CAUGHT** | miss | miss | D1 |
| **M-08** | ⚠️ **CONTROL — one added comma, no semantic change** | RS-23 prose | miss | miss | miss | ✅ **SURVIVED, as required** |
| **M-09** | a changed digit in a recorded digest | S1 SHA-256 | miss | miss | **CAUGHT** | D3 *(review only)* |
| **M-10** | a quote emptied to `>` alone | RS-21 | **CAUGHT** | miss | miss | D1 |
| **M-11** | a RECORDED row deleted — 18 → 17 | RS-71 | **CAUGHT** | miss | miss | D1 |
| **M-12** | **a remediation swapped between the two near-identical concurrency rows** | RS-22 gets RS-23's `solution` | miss | miss | miss | ⚠️ **NOTHING** |

**The control survived.** Four mutants are caught by nothing; two more only by a manual re-fetch;
two only by a check no future session can run. **Before this review, 11 of 12 were invisible to
`make test`.**

⚠️ **"NOTHING" is the interesting answer, and here is what each one buys an adversary.**
**M-02** flips the one sentence check 2f exists to protect, and would license C4 to hard-code an
invented daily limit. **M-06** breaks the citation Q-017 turns on. **M-03** changes a documented
409 into a 400, and the world would then fire the wrong code in the self-test that is supposed to
prove it matches Razorpay. **M-12** is the worst: it is *still a verbatim Razorpay quote*, just
from the wrong page.

**Partially closed here.** `tests/test_c1_review_probes.py` adds 8 probes and takes the kill rate
from **1/12 to 4/12** (M-07, M-10, M-11, plus the F-R2 assertion). It does **not** close F-R5:
the verbatim half needs the ten sources, which this repository does not vendor, and re-fetching
inside `make test` would make the suite depend on razorpay.com being up. **A probe detects; only
a fix closes.** The remedy is the architect's call between vendoring the ten fetched bodies under
`tests/fixtures/` (~112 KB, and it would make the oracle checkable from a clean clone forever) or
accepting the gap in writing.

---

## F-R6 · HIGH · the §0 check is weaker than its own sentence, in three specific ways

The review prompt asked whether the check *covers what it claims*, and whether it *can be made to
pass over an empty string, or over prose it silently strips.* Re-implemented and probed:

**(i) It matches against ANY source, never against the source the row cites.** This is the
structural flaw, and M-03 and M-12 are both instances.
- **M-03:** the payload after stripping is `* code: 400`, which occurs **8 times** in
  `normal-refunds-idempotent.md` alone. A documented `409` rewritten to `400` matches trivially.
  **Every `code:` and every `description:` line in the file is checked this weakly.**
- **M-12:** RS-22 cites **S1** (`capture.md`). Give it RS-23's `solution` and the string is
  **verbatim in `create-normal.md` (S2)** and **absent from `capture.md`** — measured, 1 hit and
  0 hits. A source-bound check catches it instantly; the global one cannot.
  ⚠️ **This session flagged that near-duplicate blind, in Phase 1 (`c1_oracle.md` IO-21), as
  *"the single most likely place for a `file:line`-class defect in the whole artefact."***

**(ii) It passes vacuously over an empty payload.** Three `>` lines reduce to `""`, and `"" in s`
is `True` for every source. Emptying a row's quote is the cheapest way to destroy it while
keeping the check green. **M-10 confirms it; D2 missed it and D1 catches it.**

**(iii) Its stripping rule is ambiguous in a way that changes the answer.** §0 says to strip
*"the three-field labels `**error:**` / …"* — but names **four**. Read as *unwrap the bold*,
`**error:** Request failed…` becomes `error: Request failed…`, which is in no source, and the
check reports **3 unmatched**. Read as *remove the label entirely*, it reports **0**. Only the
second reading reproduces §0's result. **A check whose published result depends on which of two
readings you take is not yet a check** — and it is one sentence from being one.

**None of (i)–(iii) means a row is currently wrong.** This session ran the substring half against
all twelve sources and **301 of 301 matched**. The finding is that the check would not tell us if
one were.

---

## F-R2 · MEDIUM · §0 publishes 299; the file carries 301

§0: *"**Result at the time of writing: 299 of 299 quoted lines matched. Unmatched: 0.**"*

Recomputed under §0's own scope (*"Counted over §1 onward"*): **304** lines begin with `>`,
**3** are quote-internal blanks, **301** are non-empty. All 301 match. **The verdict reproduces
exactly and the denominator does not.**

⚠️ **It was never reproducible.** `RAZORPAY_SEMANTICS.md` has exactly one commit, `55f1f2c`, and
the count at that commit is already 301. This is not a figure made stale by a later edit.

The most likely mechanism, offered as the diagnosis a FIX session can test rather than as a
claim: **§6 contains exactly 2 quoted lines** (the RS-70 note's *"**API support** | **Yes** |
**No** |"* and *"- Smart Settlements can be used via Dashboard only."*), and **301 − 2 = 299**. If
the check was run over §2–§5 and §8, it produced 299 and **did not cover §6** — which is F-R6's
*"does it cover what it claims"* in a second form. Both lines match, so nothing is wrong; the
scope statement is.

A published number that does not regenerate is what hard rule 10 exists to forbid, and persona
1's *"does every partition sum to its total?"* asks the same question of the same file.
**`test_section_0_states_its_own_quoted_line_count_correctly` is red on purpose and is this
finding's executable half.**

---

## F-R1 · MEDIUM · RS-12's cross-reference aims at the wrong row, on the project's headline finding

RS-12's Notes, verbatim:

> **Notes.** ⚠️ **See RS-31.** Razorpay documents a *second*, weaker idempotency mechanism on the
> `receipt` field — and `receipt` **is** one of `create_refund`'s five parameters.

**RS-31 is *"a refund that has already been processed cannot be re-initiated"***, and its own
Notes say *"⚠️ Do **not** read this as a duplicate-refund guard."* **The row meant is RS-27**,
whose heading is *"`receipt` IS TREATED AS AN IDEMPOTENCY KEY"*.

Every other citation in the project gets it right — §7's A1–A6 table, §9's F-06 row,
`PROVENANCE.md` §2.4, `CONTEXT.md` §2 and §9.2 all say **RS-27**. **The one wrong pointer is in
RS-12**, the row Q-017's Class A ruling turns on, and it is the pointer a reader follows to find
the qualification. The prose beside it is correct, so a careful reader recovers; the address does
not.

⚠️ **No mechanical check can catch this**, and this review's probe says so in its own docstring:
`test_every_cross_reference_points_at_a_row_that_exists` is **green**, because RS-31 exists. A
pointer can be well-formed and wrong. **That is why F-R1 is reported and not merely probed.**

---

## F-R3 · LOW · `RS-70` names two different things

`RS-70` is a row of §6's RECORDED table (the three `500`s from S3) **and** the heading
`### RS-70 (note) — why the whole Smart Settlements family is RECORDED`. Four rows (RS-65–RS-68)
and RS-16 all say *"see RS-70"*, and land ambiguously — on a 5xx row or on a note about API
availability.

**The count is not affected**, and this review confirms it: the note carries no `**World**` label
and does not inflate the partition, which recomputes to 71. The `(note)` suffix shows C1 knew.
**In an artefact whose identifiers are its addressing scheme, one address should name one thing.**
`RS-70n`, or a plain `§6 note`, costs nothing.

---

## F-R7 · LOW · §10 states its own denominator twice, as 14 and as 18

> *"`CONTEXT.md` §6 names 7 error strings and 5 bounds across A1–A6; §9.2 names 2 more … **Total:
> 14 items.** **All 14 resolve to a first-hand row.**"*

The table immediately beneath is **numbered 1 to 18**, and §10's counts table says *"Items named
… requiring a first-hand row: **18**"*. The 18 is right — it picks up §2's source-refunds quote
and A5's absence, which the 7+5+2 arithmetic omits. **Persona 1's second check is denominator
integrity, and this file is where that check is supposed to be exemplary.**

---

## F-R8 · LOW · the balance is counted among the bounds "carrying a published figure", and it carries none

`PROVENANCE.md` §2.4, A4: *"⚠️ **only three carry a published figure** (balance; ₹5 Cr; ₹2 L)."*

Razorpay publishes **₹5 Cr** (on two pages) and **₹2,00,000**. It publishes **no figure for the
settlement balance** — that bound is live merchant state, and this session recorded it blind as
*"NO PUBLISHED FIGURE — and none is possible"* (`c1_oracle.md` IO-14).

**The operative half is correct and is what check 2e asked for:** exactly two bounds need an
author-chosen value, and the cell names exactly those two. The imprecision is in the parenthetical
only. Recorded because this file's value is that its parentheticals are exact.

---

## F-R9 · INFO · RS-17 is `MUST-FIRE` and its predicate needs a clock — for C4, not against C1

RS-17 fires *"outside banking hours"*. **Hard rule 8 forbids a clock in core logic**, and Q-018's
own reasoning lists *"a WALL CLOCK"* among the grounds for `RECORDED` (it is why RS-59, the
6-month refund limit, is `RECORDED`). RS-17 is nonetheless correctly `MUST-FIRE`, **provided C4
models banking-hours as seeded world state** — deterministic, replayable, never `now()`. RS-17's
own Notes point that way. Flagged so C4 cannot reach for `datetime.now()` and still believe it is
inside the rule. **Not a C1 defect.**

---

## F-R10 · INFO · Q-026 independently confirmed — already open, and not C1's

Check 2g asked whether an older sentence survives anywhere. **It does.** `CONTEXT.md` line 178,
inside the block headed *"And the sharper one, written so a payments engineer cannot puncture
it"*:

> nothing caps the **total across payments**, and `create_refund` sends no idempotency key — so a
> retry is a second refund.

`CONTEXT.md` §9.2 line 966 calls that exact form *"false"*; `PROVENANCE.md` line 384 says
*"❌ **do not write**"* it. **This is already `QUESTIONS.md` Q-026, OPEN**, raised by ARCH BUILD
`921cfaa4` with a one-sentence remedy drafted. **Confirmed independently here; recorded as open,
not re-raised, and not counted against C1.**

⚠️ **Two further occurrences that Q-026 does not name, and which this review judges DEFENSIBLE:**
`CONTEXT.md` §6's A3 *Mechanism* cell and `PROVENANCE.md` §2.4's A3 *Mechanism* cell both read
*"no idempotency key is sent."* Those describe **what the attacker does in this attack** — a
policy-blind attacker sends none — not what the tool **can** do, and `PROVENANCE.md`'s cell
carries the ⚠️ pointing at `receipt` in the same row. **Named here so a later session does not
"fix" them into inaccuracy.**

---

# 2. Both halves of F-06, re-verified at source by this session

Check 2g required independent verification of both halves of the finding that changed a project
invariant. **Both hold.** Full transcription at `c1_oracle.md` IO-23–IO-26.

**Half one — the header is structurally unsendable.**
`razorpay-mcp-server@7950d51d…849f : pkg/razorpay/refunds.go`, lines 73–75:

```go
73		refund, err := client.Payment.Refund(
74			payload["payment_id"].(string),
75			int(payload["amount"].(float64)), data, nil)
```

`razorpay-go@v1.4.0 : resources/payment.go:44` —
`func (p *Payment) Refund(paymentID string, amount int, data map[string]interface{}, extraHeaders map[string]string)`
— and `:53` spends it: `return p.Request.Post(url, data, extraHeaders)`. The 4th positional
argument **is** `extraHeaders`; `refunds.go:75` passes the literal `nil`; **no tool parameter can
reach it.** `go.mod` pins `razorpay-go v1.4.0`, as cited.

**Half two — `receipt` is documented as an idempotency key.**
`api/refunds/create-normal.md`, Errors, L338–341:
*"Duplicate receipt found for this refund request."* (400) · *"The value passed in the `receipt`
parameter has already been used for an earlier refund on the same payment. **`receipt` is treated
as an idempotency key.**"* And `refunds.go:66` is
`ValidateAndAddOptionalString(data, "receipt")` — into `data`, the **request body**, not the
headers. `create_refund`'s five parameters are exactly `payment_id, amount, speed, notes,
receipt`; **`destination` does not exist**, confirming INC-02's correction at source. Every
`file:line` in `CONTEXT.md` §2 and §9.2 — `:73-75`, `:66`, `:42-46`, `payment.go:44` — **resolves
exactly.**

⚠️ **One counterweight this review records because it cuts against the project's convenience.**
On the **same page**, `receipt`'s *request Parameters* entry (L182–183) says only *"A unique
identifier provided by you for your internal reference."* Razorpay documents `receipt` as an
idempotency key in **one Errors-table `description`**, and as internal reference in the
Parameters block, with no cross-reference. **Both are true.** RS-27 and `PROVENANCE.md` reach the
right conclusion — *"an attacker simply omits it, or varies it"* — and the second half is why.

---

# 3. The partition recount, both ways (check 2d)

Recomputed from the document, not from its counts table:

| | Published | Recomputed | |
|---|---|---|---|
| `MUST-FIRE` | 40 | **40** | ✅ |
| `MUST-HOLD` | 13 | **13** | ✅ |
| `RECORDED` | 18 | **18** | ✅ |
| **Total** | 71 | **71** | ✅ |
| Rows in **two** buckets | 0 | **0** | ✅ |
| Rows in **no** bucket | 0 | **0** | ✅ |
| Row numbers `RS-01`…`RS-71` contiguous, no gaps, no duplicates | claimed | **confirmed** | ✅ |

**RS-70 (note) carries no `World` label and is correctly not counted.** RS-53's declared
split-scope (extra-field half `MUST-FIRE`, credential half `RECORDED`, counted once) is stated in
§10 rather than rounded away — **the right handling.**

**Are the 18 `RECORDED` genuinely unreachable, or is one merely inconvenient?** Each was
examined. Seventeen are unarguable: account-level disablement (RS-54, RS-55, RS-62), a payment
method the world does not model (RS-56), an active dispute (RS-58), a wall clock (RS-59, and hard
rule 8 forbids one), routing/enablement (RS-60), separate products (RS-61, RS-63, RS-64, RS-71),
5xx faults (RS-70), and parameters the MCP tool does not expose (RS-69 — **verified first-hand**:
`settlements.go:221-247` declares only `amount`, `settle_full_balance`, `description`, `notes`).
**RS-65–RS-68 are the strongest of all**, resting on Razorpay's own table cell *"**API support** |
**Yes** | **No** |"*.

**The one worth pressing is RS-57**, *"Partial refund is currently not supported for this payment
method"* — and **C1 flags its own exposure**, in its own row: *"⚠️ Would otherwise be
attack-relevant — it forces full refunds."* This review agrees it is correctly `RECORDED` (it is
gateway-specific and the world models no gateway variation) and records that **C1 marked the one
inconvenient exclusion as inconvenient rather than quietly filing it.** That is the behaviour the
`RECORDED` bucket could most easily have been abused to avoid.

---

# 4. Every URL re-fetched — digest then and now (check 2b)

⚠️ **Zero drift, in either direction. Nothing to record as a change to the world.**

| # | URL | Bytes then/now | SHA-256 then | now | |
|---|---|---|---|---|---|
| S1 | `…/api/payments/capture.md` | 15,396 / **15396** | `ddbca672…ed1d9` | **identical** | ✅ |
| S2 | `…/api/refunds/create-normal.md` | 14,596 / **14596** | `517e32ac…56569` | **identical** | ✅ |
| S3 | `…/api/refunds/normal-refunds-idempotent.md` | 10,846 / **10846** | `95fa561c…070a9b` | **identical** | ✅ |
| S4 | `…/api/settlements/instant/create.md` | 18,159 / **18159** | `95776ebd…8cccd` | **identical** | ✅ |
| S5 | `…/payments/settlements/instant.md` | 5,788 / **5788** | `4d2a0558…d4d08` | **identical** | ✅ |
| S6 | `…/payments/refunds.md` | 4,834 / **4834** | `65f32df2…8c19e` | **identical** | ✅ |
| S7 | `…/api/payments/fetch-all-payments.md` | 10,123 / **10123** | `9e7f6d97…72bf93` | **identical** | ✅ |
| S8 | `…/api/payments/fetch-with-id.md` | 12,613 / **12613** | `38f97247…5790c` | **identical** | ✅ |
| S9 | `…/payments/settlements/faqs.md` | 20,378 / **20378** | `4ccfaa94…b80de5` | **identical** | ✅ |
| S10 | `razorpay.com/capital/instant-settlements/` | 109,181 / **109181** | *(none recorded)* | byte count matches; digest now `e3c4ef75…d77f481` | ✅ |
| S11 | `razorpay-mcp-server@7950d51d…849f` | 94 files | `refunds.go` = `d483495c…3f26f` | **identical**, raw **and** from the archive | ✅ |
| S12 | `razorpay-go@v1.4.0 : resources/payment.go` | 7,793 / **7793** | — | fetched, `0279e086…89b58` | ✅ |

**Both claimed-404 URLs** (`…/llm-docs/llms.txt`, `…/api/payments/fetch-all.md`) → **404**, each
with the 135,098-byte shell. **All six discovery URLs** → **200**.
⚠️ **C1's claim that each page was fetched twice, six minutes apart, byte-identical, is
corroborated**: this session fetched the six core pages twice, 3 minutes apart, and got identical
digests, then matched C1's recorded digests 24 hours later. **The digests are real.**

---

# 5. The Phase 1 → Phase 2 diff, row by row

Full text at `docs/reviews/independent/c1_oracle_diff.txt`. Summary of all 26 independent rows:

| Independent | C1's row | Agreement |
|---|---|---|
| IO-01 A1 amount-equality | RS-01 | ✅ character-identical, including `authorised amount .` |
| IO-02 A1 `amount_due` | RS-02 | ✅ identical |
| IO-03 A2 over-refund | RS-03 | ✅ identical, `greater than amount captured` (no article) |
| IO-04 A2 fully refunded | RS-04 | ✅ identical |
| IO-05 A6 not captured | RS-21 | ✅ identical |
| IO-06 `settle_full_balance`, doc wording | RS-13 | ✅ identical, double space preserved |
| IO-07 `settle_full_balance`, MCP wording | RS-14 | ✅ identical; **both independently place it at `settlements.go:231-232`, not on any doc page** |
| IO-08 header + 10-char minimum (prose) | RS-05 | ✅ identical, `10 character long` singular preserved |
| IO-09 409 (prose) | RS-06 | ✅ identical |
| IO-10 10-char minimum (error) | RS-07 | ✅ identical |
| IO-11 409 same-key-in-flight | RS-09 | ✅ identical |
| IO-12 the **second** 409 | RS-10 | ✅ identical — **both kept the two 409s distinct** |
| IO-13 `receipt` as idempotency key | RS-27 | ✅ identical |
| IO-14 bound 1, balance | RS-15 | ✅ identical · ⚠️ **F-R8**: independent says *no published figure*; `PROVENANCE.md` counts it among the three that carry one |
| IO-15 bound 2, ₹5 Cr | RS-16 | ✅ identical; both corroborate on S5 |
| IO-16 bound 3, ₹2 L | RS-17 | ✅ identical, `2 Lacs` preserved · **F-R9** raised by both (C1 as F-02) |
| IO-17 bound 4, daily limit | RS-18 | ✅ identical — **both: NO FIGURE, none invented** · **F-R4** |
| IO-18 bound 5, attempts/day | RS-19 | ✅ identical — **both: NO FIGURE, none invented** · **F-R4** |
| IO-19 the three-way minimum disagreement | RS-36 / F-03 | ✅ **both found it independently**, including the MCP's fourth value `Min(200)` |
| IO-20 capture concurrency, three fields | RS-22 | ✅ identical, remediation intact |
| IO-21 the refund-page near-duplicate | RS-23 | ✅ **both kept them separate and credited each correctly** |
| IO-22 source refunds only | RS-25 | ✅ identical, bold preserved |
| IO-23 `nil` into `extraHeaders` | RS-12(i)(ii) | ✅ identical |
| IO-24 five parameters, no `destination` | RS-12(iii) | ✅ identical · see the note below |
| IO-25 `refunds.go:66` forwards `receipt` | RS-27 | ✅ identical |
| IO-26 `go.mod` pins | (`CONTEXT.md` §2) | ✅ identical |

**Divergences: 3.** One is **F-R8** (a parenthetical). One is **F-R9** (a `MUST-FIRE` label this
review accepts with a rider). **The third is not a divergence of fact but is worth its own line:**

⚠️ **RS-12(iii)'s heading still reads *"`create_refund` has five parameters and none of them is a
key."*** — the exact form `CONTEXT.md` v1.3 declared **FALSE** as the fourth false third-party
claim. **This review does not raise it as a finding**, because RS-12's own Notes immediately
qualifies it (*"Razorpay documents a second, weaker idempotency mechanism on the `receipt`
field"*), RS-27 states the correction in full three sections later, and within RS-12's frame —
which is about the **header** — the sentence is defensible. **It is named here rather than filed
because it is one clause away from being the fifth**, and because **F-R1's misaimed pointer is
what a reader must follow to find its qualification.** Fixing F-R1 fixes most of this.

**Not covered by the independent oracle** (stated so the agreement is not read as broader than
it is): S7–S10 were not mined blind, so RS-44–RS-49 rest on C1's transcription plus this
review's digest match, not on an independent second reading. **Rows this review did not rebuild
are `NOT-COVERED`, never `verified`.**

---

# 6. Persona 1 — the evaluation-integrity checklist

| Check | Result |
|---|---|
| **Circularity** | ✅ **The strongest result in this review.** C1's expected values are a third party's published text, external by construction. This review's oracle was built **blind and committed first** (`f069486`), so the agreement is between two independent readings of the same external source, not between a file and itself. ⚠️ The **one** circularity risk is the `MUST-FIRE`/`RECORDED` split, which is **ours** — and §0 and §11(2) both say so. This session deliberately did **not** invent its own labels blind, because a label is a decision about our world, not a fact about Razorpay's docs. |
| **Denominator integrity** | ✅ partition sums exactly (40+13+18=71), every row in one bucket. ⚠️ **F-R2** (299 vs 301) and **F-R7** (14 vs 18) are two published denominators that do not regenerate |
| **Metric soundness** | n/a — this chunk reports no metric |
| **Arm confounding** | n/a |
| **Post-hoc selection** | ✅ no threshold, seed or comparison is chosen here. ⚠️ **F-R4** is the live risk: two values still **unchosen** for a `MUST-FIRE` bound, and choosing them after C4 sees how hard A4's ceiling binds would be exactly post-hoc selection. **That is the strongest reason F-R4 must close before `prereg-v1`, not after** |
| **Attacker competence** | n/a |
| **Third-party claims** | ✅ **every statement verified at source.** 10 pages re-fetched with matching digests, 2 pinned trees re-read, all 7 `grep` claims reproduced, 79 of 79 Errors entries present, 0 paraphrases. **C1 itself found the fourth false claim in this specification.** ⚠️ **F-R5**: nothing keeps it verified tomorrow |
| **Hand-recomputation** | ✅ substituted by Q-016's re-fetch obligation, discharged in full |

# 7. Persona 2 — code reviewer

C1 ships no first-party source. `git show --stat 55f1f2c 7a101a6` touches only the two documents.

| Check | Result |
|---|---|
| **No API key in any log, transcript, report or committed file** | ✅ scanned the two artefacts, `c1-build-1.txt` and this review's own outputs — clean. C1's fetches are unauthenticated public GETs |
| **Scorer imports no model client / gate and scorer share no module** | n/a — no source in this chunk |
| **Silent data loss** | ⚠️ **F-R5** is this persona's finding as much as persona 1's: an oracle nothing checks is a corruption channel with no alarm, and **M-11 (a deleted row) was invisible to `make test`** until this review's probe |
| **Crashes / corruption** | ✅ none. ⚠️ Noted for the FIX session: the mutation harness that swapped the artefact in place is **this review's throwaway tool in an OS temp directory**, restores and re-reads to prove the restore, and `git diff HEAD` was empty before and after |

---

# 8. What this review did NOT establish

1. **S7–S10 were not independently mined.** Their digests match; their *content* was read once, by C1.
2. **No Razorpay API call was made** by either session. This is a review of documentation against
   documentation. Where Razorpay's docs are wrong, both files are wrong together.
3. **The `MUST-FIRE`/`RECORDED` labels were assessed for internal consistency and for whether each
   `RECORDED` exclusion is honest — not re-derived from scratch.**
4. **F-R4's two values are not proposed here.** They are a Class A choice and belong to the
   architect.
5. **The mutation set is 12, not exhaustive.** A thirteenth mutation nobody thought of is the
   argument for closing F-R5 rather than for adding a thirteenth probe.

---

# 9. What must happen before a re-review

1. **F-R4** — architect: three rows into `CONTEXT.md` §8.6, three keys into
   `config/protocol.yaml`, three rows into `spec_constants.py`. **Before `prereg-v1`.**
   A `QUESTIONS.md` entry is **OWED** and is written out in full in this session's FINAL OUTPUT.
2. **F-R5 / F-R6** — C1 FIX: commit the §0 check, **bound to each row's cited source**, with the
   empty-payload case rejected and the four-vs-three label ambiguity resolved in one sentence.
   Vendoring the ten bodies is the architect's call.
3. **F-R2, F-R1, F-R3, F-R7, F-R8** — C1 FIX, and `INCIDENTS.md` **first**, per hard rule 13.
4. `tests/test_c1_review_probes.py::test_section_0_states_its_own_quoted_line_count_correctly`
   goes green when F-R2 closes. ⚠️ **It is red on purpose and it is C1's, not C0's.**

**No tag is cut. `c1-pass` is not applied.** This review fixed nothing.

---

**Reviewed by:** C1 ADVERSARIAL REVIEW attempt 1 · `SESSION-TOKEN: a0cc0212` · 2026-08-31
**Phase 1 sealed at:** `f069486`, before any sighted file was opened.
