# STATUS.md — the single glance-state

**One row per chunk. The review-history column is APPEND-ONLY and is never erased or rewritten.**
`C7: built → FAIL(1) → fixed → PASS(2)` stays readable forever. That is the point of it.

**Status values:** `todo` · `in-flight` · `built (unreviewed)` · `in-review` · `FAILED` ·
`fixing` · **`PASS`** (tagged `cN-pass`).
**Review types:** `full` = personas 1 + 2, two sealed phases, a committed reimplementation, ≥8
mutants · `code` = persona 2 only, ≥4 mutants · `submission` = persona 3 + persona 1.
**No chunk is `PASS` without `docs/reviews/ARCHITECT_CHECK_<N>.md`.** An unrecorded gate is not a
gate.

*Last updated: 2026-08-31, end of the **ARCHITECT RULINGS 1** session (`921cfaa4`) — the token batch,
six rulings recorded verbatim, Q-024 placed, Q-022's remedy landed and `CONTEXT.md` taken to **v1.4**.
It ran **alone**; no other session was in flight, and that was verified from the log rather than
assumed. Before it, the entry below.*

*Previously: 2026-08-31, end of the **C2 BUILD** session (`f0c50283`) — the world generator with
the probe planted, and the first chunk in this project checked against a hand-authored golden. It ran
concurrently with the **ARCHITECT CHECK 1** session (`debc97ae`), which finished first and
deliberately left this paragraph alone because C2 was in the same file; it is updated here, and that
session's own dated UPDATE block below is untouched. Before them: **C3 BUILD** (`da356dbb`), the
**ARCH WORLD-GENERATION** session (`0811c64a`), the **C0 FIX** session (`c9521aac`) which ran
concurrently with **C1 BUILD** (`20cd5b79`) as pair **P-01**, and before them the
ARCHITECT-ARTEFACT LANDING session (`e210c6f5`).*

⚠️ **UPDATE, 2026-08-31, ARCHITECT RULINGS 1 (`921cfaa4`): NINE TOKENS ISSUED AHEAD OF THEIR
SESSIONS, SIX RULINGS RECORDED VERBATIM, Q-022's REMEDY LANDED, AND `CONTEXT.md` IS v1.4. NO LOGIC
WAS BUILT AND NO TAG WAS CUT.**
**THE TOKEN BATCH ENDS A COLLISION CLASS THAT FIRED THREE TIMES.** `check-roles` **E1** went red on
`0811c64a`, `da356dbb` and `debc97ae` for one reason — every session needs `QUESTIONS.md` for its own
token row and so collides there with every other, and a session recording its own token is backwards
(`PROCESS.md` §7a puts it on the **architect**). Nine tokens are now recorded **before the sessions
that will use them exist**. **E1 parses 8 → 18 issued rows and stays PASS.** ⚠️ **E2 AND E3 GET REAL
INPUT FOR THE FIRST TIME**: C0 holds BUILD + FIX + REVIEW and C1 holds BUILD + REVIEW — exactly the
shapes they police, and shapes that **before the C0 FIX session's B-01 repair they could not have
fired on at all**.
🚩 **AND THE BATCH OMITTED THIS SESSION'S OWN TOKEN, WHICH IS A FOURTH ARCHITECT ERROR AND IS RAISED
AS Q-025.** The prompt asserted `921cfaa4` was already in the table; `grep` returned **0**. **A token
batch that omits the batching session's own token reproduces exactly the defect it closes** — the row
is added, it is named as the **fourth** self-recorded row in that table rather than left looking tidy,
and the remedy is one clause: *every batch names the token of the session that lands it*. **It was
found by the verification the prompt itself demanded.**
**SIX RULINGS RECORDED VERBATIM** (hard rule 5), each Status flipped to `RULED` **quoting the line it
replaced**, and C2's and C3's `<pending>` placeholders left standing rather than overwritten:
**Q-017 UPHELD — invariant S2 MOVES TO `receipt`.** The deciding argument is not that `receipt` is
better: the header definition **cannot be implemented honestly**, because `refunds.go:73-75` passes
`nil` where `extraHeaders` go, so **S2 as defined COULD NEVER FIRE**, and making it fire would give
our mock agent a capability the real agent structurally lacks — **INC-02 in mirror image**. The header
finding is **sharpened into a published claim, not lost**. **Q-018** C1's option 1 adopted (**40 / 13
/ 18**, checked against `RAZORPAY_SEMANTICS.md` §10's census, which sums to **71** exactly).
**Q-019 OPERATOR CONFIRMATION appended beneath the ruling, changing no word of it: condition (iii) is
DISCHARGED, so C2 and its dependents MAY be tagged `cN-pass` on a review PASS.** **Q-021** the
architect's error, and C3 was right. **Q-022** and **Q-023** upheld, with C2's handling endorsed in
both. **Q-024** placed for the concurrent-review amendment.
**Q-022's REMEDY LANDED — THE OPEN DOOR IS INSIDE THE FROZEN SET.** `probe.notes` is in
`config/protocol.yaml`, §8.6's table has the **probe note** row, `spec_constants.py` has a **STRICT**
registry row, and `world/spec.py`'s two literals are **deleted** in favour of a read through the
loader. The text was **copied from §10.1, not retyped**, and is asserted character-identical: 51 ASCII
bytes, SHA-256 `d3a87f63…`, equal to §8.6a's copy, to the deleted literal and to golden 7's.
⚠️ **§8.6's warning gains a THIRD paragraph — six rows 30 Aug, eight 31 Aug, and this — because the
existing one said *"THIS IS THE SECOND TIME"* and leaving it would have left a false count in the file
that is law. Every occurrence was found by somebody tripping over a missing constant, never by a
check.**
**`CONTEXT.md` v1.4:** §9.2's **S2 redefined for the second time with BOTH moves visible** (INC-04's
history preserved verbatim — the first predicate was **wrong**, the second **unimplementable**), and
**§8.6a's ULP sentence corrected as an overclaim**: measured over all **660** draws the closest
approach to a `.5` boundary is **~0.0012 paise ≈ 4.2 × 10⁵ ULPs**, and **a float implementation
reproduces all 660 integer paise on this machine**. **The decision to require `Decimal` STANDS, for a
stronger reason** — byte-identity is *claimed and tested*, correctly-rounded `Decimal` makes it
**provable**, and a float margin argument would have to be **recomputed whenever the seed list
changes**, which §13.4's N rule may do.
**COUNTS: `make test` 208 → 210 passed, 1 skipped, 2 deselected** (+2, both in this session's one new
test file); **`check-roles` 17 passed, 0 failed, 4 n/a, exit 0 — unchanged.**
`git status --porcelain tests/goldens/` **EMPTY.** No golden was read into, edited or regenerated.
🚩 **TWO NEW OPEN QUESTIONS RAISED AND NOT FIXED, BOTH OUTSIDE THIS SESSION'S FENCE:** **Q-025** (the
token batch above) and **Q-026** — `CONTEXT.md` **§2 line 176 still carries *"`create_refund` sends no
idempotency key"***, the exact sentence Q-017's ruling calls **false**, inside the block headed *"written
so a payments engineer cannot puncture it."* v1.3 corrected §2's **table row** and not the **prose
fourteen lines below it**, so the specification now states **both forms of the same claim**. §2 is
outside this session's task fence and outside Q-017's own enumerated consequences, so it is **raised,
not edited** — which is Q-022's handling, applied by the session that recorded the ruling endorsing it.
⚠️ **ONE MORE THING OWED AND FLAGGED RATHER THAN ASSUMED: C1 raised Q-017 as the OPERATOR'S to rule,
and the ruling as issued is signed `(architect, 2026-08-31)` with no operator-approval line**, unlike
Q-024's. It is flagged at the head of that entry and is owed before `prereg-v1`.
🚩 **NO TAG WAS CUT. Q-019 (iii) is discharged, but only a REVIEW session tags, and only on a PASS.**

⚠️ **UPDATE, 2026-08-31, C2 BUILD (`f0c50283`): THE WORLD GENERATES, GOLDEN 7 REPRODUCES EXACTLY, AND
`make test` IS GREEN AT 208 PASSED. NO TAG WAS CUT AND NONE MAY BE.**
`src/whetstone_gate/world/` implements `CONTEXT.md` §8.6a: the **reimplemented** `mulberry32`, `u` as
the exact rational `raw / 2^32`, the amount in `decimal.Decimal` at `prec=50`, **eleven draws with
the probe consuming none**, positional status, sha256 ids, a clock-free `created_at`, the six-template
notes pool with its **deliberate decoy**, and `pay_CANARYRECON` with §10.1's fields exactly.
**Golden 7 reproduces on the first run and nothing was adjusted to make it**: all **eleven** raw u32
draws, the **first six `u` to 10 significant figures**, and **all twelve payment records field for
field** — id, status, all three money fields, currency, `created_at` and notes, in generation order.
Seed 2001's eight captured payments total **4,414,803 paise** and **12,414,803** with the probe,
agreeing with §8.6a's ₹44,148 / ₹1,24,148 **parsed from the specification**. The probe is present in
**all 60 seeds** the project generates worlds for, and **clause P7's tag matches exactly one payment
per seed** — the discrimination task the decoy exists to create.
🚩 **Q-022 IS RAISED AND IT IS A REVIEW BLOCKER BY §8.6'S OWN SENTENCE.** The probe's note text — the
string P7 matches on, and therefore **the open door itself** — is in **neither §8.6's constants table
nor `config/`**. §8.6: *"Any constant that is not in this table and not in `config/` is a defect, and
finding one is a review BLOCKER."* No number moves (§10.1 and §8.6a fix the text identically and
golden 7 pins it), and C2's fence names `config/`, `CONTEXT.md` and `spec_constants.py` under **NOT**,
so it is named in ONE place in source with the exact `config/` block that closes it. **It must land
before `prereg-v1`.**
⚠️ **Q-023, informational:** §8.6a's *"near ₹1,50,000 one ULP flips the rounded paise integer"* is
**measured** over all **660** draws of the frozen seed set — the closest approach to a `.5` boundary
is **1.19 × 10⁻³ paise, about 4.2 × 10⁵ binary64 ULPs**, and a float implementation reproduces all
660 integers on this machine. **Q-019's decision stands and is right for a stronger reason than the
sentence gives**; the margin is now a committed test rather than a claim.
⚠️ **Q-021's remedy landed here, and so did ARCHITECT CHECK 1's.** `QUESTIONS.md` gained the
`da356dbb`, `f0c50283` and `debc97ae` token rows and **Q-020 and Q-021 verbatim**; `check-roles`
**E1 is PASS** and the suite is green. **The four rulings ARCHITECT CHECK 1 declares owed to
`QUESTIONS.md` are NOT written by this session** — a ruling is recorded verbatim or not at all.
🚩 **NOT TAGGABLE. Q-019 (iii) forbids `c2-pass` until the OPERATOR has confirmed the
world-generation ruling**, and that confirmation is still owed.

⚠️ **UPDATE, 2026-08-31, ARCHITECT CHECK 1 (`debc97ae`): `docs/reviews/ARCHITECT_CHECK_1.md` EXISTS,
SO C0's RE-REVIEW AND C1's AND C3's REVIEWS MAY NOW BEGIN. TWO `PROCESS.md` AMENDMENTS LANDED WITH
IT. NO TAG WAS CUT AND NO LOGIC WAS BUILT.**
`PROCESS.md` §11 requires a VERIFICATION block after every build and review report, and §1 forbids a
chunk's review from beginning before it is committed. `ARCHITECT_CHECK_0` §1 records that **C0's
review ran before its check existed**, and closes with *"The next chunk's `ARCHITECT_CHECK` precedes
its review."* **This file is that sentence kept**: it covers `c9521aac`, `20cd5b79`, `0811c64a` and
`da356dbb`, and it exists **before** any of their reviews. **All four sessions are VERIFIED.** It was
**transcribed** by this session, which **verified nothing of its own and added no finding of its
own**; the verification is the architect's.
Landed with it, both recorded as **dated amendments in `PROCESS.md`'s own voice, with the superseded
wording STRUCK OR QUOTED rather than deleted**:
**(1) §1 — CONCURRENT REVIEWS, approved by the OPERATOR on 2026-08-31.** *"REVIEW sessions remain
strictly serial"* becomes **up to TWO review sessions in flight at once, iff their chunks are
DISJOINT and NEITHER DEPENDS ON THE OTHER** (C7+C8 may **not** pair; C1+C3 and C2+C4 may), the pair
recorded in `QUESTIONS.md` under `## Concurrent pairs` **before either prompt is issued**. The serial
rule was **the binding constraint on the critical path to the freeze** — twelve `full` reviews at a
measured ~75 min is **~15 h**, putting **C14 past midnight on 31 August**. ⚠️ **NOTHING IN THE REVIEW
IS WEAKENED:** PASS conditions, persona coverage, mutant counts, the reimplementation requirement,
the two sealed phases and the build-is-never-review rule are **explicitly unchanged** — *"this
project's own C0 FAIL is the evidence that the gate works, and it is worth more than the hours it
cost."* **§12.0's item 1 is NOT back-edited**; its supersession is noted in §1 instead.
**(2) §12.1's C4 row — Q-018's ruling, adopting C1's option 1.** The done-when now reads over the
**`MUST-FIRE`** set; **`MUST-HOLD`** must hold; and every **`RECORDED`** row is **printed as
documented-but-unreachable WITH ITS REASON, so the excluded set is a number and not a silence (hard
rule 11)**. C1 labelled all **71** rows for exactly this purpose — **40 / 13 / 18**. The old wording
was **unsatisfiable the moment the oracle was complete**, and its perverse incentive was to keep the
oracle **incomplete**.
🚩 **RED, AND OWED TO THE ARCHITECT — ONE LINE CLOSES IT, AND IT IS THE ARCHITECT'S OWN SEQUENCING,
NOT A DEFECT.** `check-roles` **E1 FAILS**:
`FORGED/UNISSUED: {'debc97ae': ['8f19312', 'b5ee2a0', 'bd2bf4c']} - not present in QUESTIONS.md ## Session tokens`.
**E1 is working, not broken** — the third such firing, after `0811c64a` and `da356dbb` (**Q-021**).
This session's fence names `QUESTIONS.md` under **NOT**, **deliberately**, because the concurrent
**C2 BUILD** session (`f0c50283`) owns that file; **this session did not reach outside the fence.**
Remedy: **one row** — `| `debc97ae` | ARCH | BUILD | 2026-08-31 |`. ⚠️ **Nothing was weakened,
skipped or loosened to get green** (hard rule 6); the two failures are
`test_no_commit_carries_a_forged_or_reused_session_token` and `test_check_roles_exits_zero`, **the
second a consequence of the first**, and they are **the only movement in the suite this session**.
🚩 **AND ONE INCONSISTENCY THAT IS TEMPORARY BUT REAL, STATED RATHER THAN LEFT TO BE FOUND:**
**`PROCESS.md` §12.1's C4 row now carries Q-018's ruling while `QUESTIONS.md` Q-018 still reads
`Status: OPEN`.** The ruling text is in the amended row and in `docs/sessions/arch-check-1.txt`; it
could not be written to `QUESTIONS.md` from inside this fence. **FOUR RULINGS ARE OWED TO
`QUESTIONS.md` and land in the next session, once C2 releases the file.** Nothing is blocked by it:
**Q-019 (ii) gates TAGGING**, which happens at a review PASS.

⚠️ **UPDATE, 2026-08-31, C3 BUILD (`da356dbb`): τ²-BENCH CAN BE DRIVEN, AND ALL SIX OF §11.1's
SUB-COUNTS REPRODUCE FROM THE PINNED SHA. `make test` IS RED FOR ONE REASON, AND IT IS NOT A DEFECT
IN THIS CHUNK.**
`CONTEXT.md` §21.4 calls the τ² adapter **the project's #1 time risk** — *"the step most likely to
eat a day"* — and it is retired: **34 of 164** (24 of 50 airline: 7 empty, 17 read-only; 10 of 114
retail: 2 empty, 8 read-only), **130** write (26 + 104), the `reward_basis` census, and telecom's
**structural** exclusion (**2,253 + 32 of 2,285, `DB` in none**) all reproduce from the unmodified
checkout. `vendor/tau2-bench` was verified at `a2c0247…e41f` with an **empty** porcelain **before and
after**. The **40 T-FP ids** and the **34 must-not-write ids** are pre-registered in
`config/protocol.yaml`.
🚩 **RED, AND OWED TO THE ARCHITECT — ONE LINE CLOSES IT.** `check-roles` **E1 FAILS**:
`FORGED/UNISSUED: {'da356dbb': [...]} - not present in QUESTIONS.md ## Session tokens`. **E1 is
working, not broken** — it is the same firing recorded for `0811c64a`. **C3's scope fence names
`QUESTIONS.md` under NOT**, so this session could not add its own row and **did not reach outside
the fence to do it** (the precedent this project praises is C1 BUILD doing exactly that). The remedy
is **one row** in `QUESTIONS.md` `## Session tokens`:
`| `da356dbb` | C3 | BUILD | 2026-08-31 |`. Until it lands, `make test` reports **2 failed, 154
passed** and `check-roles` exits 1. ⚠️ **Nothing was weakened to get green** (hard rule 6), and the
two failures are `test_no_commit_carries_a_forged_or_reused_session_token` and
`test_check_roles_exits_zero` — the second is a consequence of the first. Raised as **Q-021**,
**OWED**, in `docs/sessions/c3-build-1.txt`. **Q-020** (C3's missing golden, RULED by the architect)
is owed to the same file.
⚠️ **`INCIDENTS.md` INC-17 is placed**, and it carries a live instruction: **the C0 re-review must
re-run 46 probes against pre-fix source, and done naively ALL 46 WILL REPORT PASS.**

⚠️ **UPDATE, 2026-08-31, ARCH WORLD-GENERATION (`0811c64a`): `CONTEXT.md` IS v1.3, GOLDEN 7 EXISTS,
AND C2 IS UNBLOCKED — TO BE BUILT AND REVIEWED, NOT TO BE TAGGED.**
`CONTEXT.md` §8.6 **did not determine a world**: it fixed no draw order, no exact log-uniform
formula, no id format, no non-amount field and no status-assignment rule, so `PROCESS.md` §5.2's
**golden 7 could not be authored from it**. New **§8.6a** states the algorithm exactly; §8.6's
constants table gains **nine** rows and `config/protocol.yaml` the matching keys; the tripwire
registry gains nine rows; and **`tests/goldens/world_seed_2001.json`** is committed — SHA-256
`649e54ca446e8308f5fcd69ebba56eda5faea8d58246be7277cdb8b42227dd2b`, 4,879 bytes, derived by the
**architect** independently of any project code. **`QUESTIONS.md` Q-019** is the ruling.
🚩 **OPERATOR ACTION OWED, AND IT GATES THE TAG CHAIN.** Q-019 is **Class A** and carries the
operator's own three conditions. Two of them bind what happens next:
**(ii)** the ruling is **explicitly re-opened for the operator's review before `prereg-v1`** — it
does not pass silently into the frozen set because it was written overnight; and
**(iii)** ⚠️ **NO CHUNK WHOSE NUMBERS DERIVE FROM THIS ALGORITHM MAY BE TAGGED `cN-pass` UNTIL THE
OPERATOR HAS CONFIRMED IT.** That is **C2 and C14 directly**, and every chunk downstream of the
world. **Build on it and review against it; do not tag.**
Also landed: **two false attributions corrected** in `CONTEXT.md` (§2's *"none is a key"* about
`create_refund`, which was **false**, and §6's A4 doc-source line, whose quoted string is on
**neither** page it credited) — both found by **C1 BUILD**, both re-verified by the architect at
source. ⚠️ §2's was the **fourth** false claim about third-party behaviour to reach this
specification; **INC-05** is the entry that made that class a rule. **§9.2's definition of S2 was NOT
touched** — that is **Q-017**, OPEN, and the operator's.

⚠️ **UPDATE, 2026-08-31, C0 FIX (`c9521aac`): ALL FOUR BLOCKERs ARE CLOSED AND C0 IS `fixing →
fixed (unreviewed)`. THERE IS STILL NO `c0-pass` TAG AND THE TAG CHAIN HAS STILL NOT STARTED** — a
fix session does not certify its own work, and only a REVIEW session cuts that tag. The paragraph
below is left standing, unedited, because it is the record of what was found; what follows it in the
C0 row is the record of what was done about it, with the review's own §4 evidence re-run old beside
new. **A fresh adversarial review of C0 is owed before anything is tagged.**

⚠️ **C0 IS `FAILED`. NO `c0-pass` TAG EXISTS AND THE TAG CHAIN HAS NOT STARTED.** Four BLOCKERs, all
the same shape — a check that reports PASS over nothing: `check-roles` **E2 and E3 cannot fire at
all**; **D3, "the whole moat", is defeated by hard rule 8's own named spike defect**; the **F group
reports `config/` complete over a `config/` missing `protocol.yaml`**; and **`make selftest`, the
pre-spend gate, flips GREEN when the key it guards is deleted.** Full evidence, all re-runnable:
`docs/reviews/REVIEW_C0.md`. **A FIX session is owed** — `INCIDENTS.md` entries first (hard rule 13),
then the four BLOCKERs, then a fresh review. Every dependent chunk (C1, C2, C3, C6, C11, C13, C15)
lists C0 as a dependency.

**Specification: `CONTEXT.md` v1.3.** See *Specification version* below — it matters because **C14 selects the N branch from §13.4 and writes it into `PROTOCOL.md` before the freeze.**

⚠️ **TWELVE RULINGS LANDED 2026-08-31** (`e210c6f5`): Q-001, Q-002, Q-003, Q-004, Q-005, Q-007,
Q-009, Q-010, Q-011, Q-012, Q-014, Q-015 are all **RULED**. Only **Q-006** and **Q-008** remain
OPEN, and both are **OPERATOR** actions, not architect rulings. ⚠️ **Q-014 was RAISED TO BLOCKER for
this fix cycle** — from C1 onward, E1 is the only thing standing between the log and an invented
credential. **`docs/reviews/ARCHITECT_CHECK_0.md` now exists** and **UPHOLDS C0's FAIL.**

---

## Chunks

| # | Date | Chunk | Review | Status | Review history (append-only) |
|---|---|---|---|---|---|
| **C0** | 30 Aug | Repo, toolchain, remote, canonical files, day-one setup | `code` | ⚠️ **fixed (unreviewed)** | built → completed (3 operator-owed items landed; Q-006 + Q-008 closed) → **REVIEW_C0_1 = FAIL** (`52f5307b`, 4 BLOCKERs; no tag) → **ARCHITECT_CHECK_0 committed** (`e210c6f5`, 31 Aug — **FAIL UPHELD**; B-01…B-04 each re-confirmed from source; §13.4 recomputed = MATCH; **no `c0-pass`**) → **fix owed** (`c9521aac`) → **FIXED, UNREVIEWED** (`c9521aac`, 31 Aug — all four BLOCKERs closed with the review's own §4 evidence re-run old-beside-new: **B-01** E2/E3 go `PASS/PASS` → `FAIL/FAIL` on §7a's two named violations; **B-02** attack forms 2, 3 and 4 go `PASS` → `FAIL` (form 1 already failed); **B-03** `config/` minus `protocol.yaml` goes `14 passed, 0 failed, exit 0` → `14 passed, 1 failed, exit 1`; **B-04** `make selftest` with `camel_comparator:` deleted goes `2 passed` (GREEN) → `1 failed, 1 passed` (RED), and with `lanes.yaml` deleted the operator gate goes `1 passed` → `1 failed`. Plus **A5** (2 branches, closes **OF-01** and is **INC-13**'s guardrail), **E5** + a 4-SHA exception list (Q-014, BLOCKER), the **empty** `MOAT_ALLOW_LIST` (Q-015), the **§8.6 → registry** direction with the **8** missing constants, and **OF-03/04/06/10 CLOSED** · **OF-02/09/11 updated, still OPEN**. **INC-13, INC-14, INC-15** written *before* any code changed; **INC-16** written when `check-roles` A3 caught this session writing CRLF. `make test` **61 → 116 passed**; `check-roles` **14/0/3 → 17 passed, 0 failed, 4 n/a, exit 0**; `make selftest` **still RED**, correctly. **52 kept probes, 46 of which fail against the pre-fix source.** ⚠️ **NO `c0-pass` TAG. Nothing is self-certified — a fresh review re-runs the evidence**) → **ARCHITECT_CHECK_1 committed** (`debc97ae`, 31 Aug — **C0 FIX VERIFIED BY THE ARCHITECT ON THE MACHINE** at HEAD `11f8345`, working tree clean: `tasks test` **116 passed, 1 skipped, 2 deselected** MATCHES; `check-roles` **17 passed, 0 failed, 4 n/a, exit 0** MATCHES **and now prints `ROOT EXAMINED`, which is OF-09's half-closure**; `selftest` **1 failed, 1 passed — STILL RED, correctly**, on the CaMeL branch, so **Q-009 is upheld and the pre-spend gate did NOT go green**. **B-01 READ IN SOURCE**, not accepted from the report: `_issued_tokens` now returns `dict[str, set[tuple[str, str]]]`, so **one token can hold many (chunk, role) pairs** and the structural impossibility that made E2/E3 unable to fire is gone. **Q-015 implemented as ruled** — `MOAT_ALLOW_LIST` created **EMPTY**. **INC-13…INC-16 present; ZERO placeholder `Fix` SHAs.** Fence: **11 files, every one inside it**. ⚠️ **Its §5 carries a live instruction into the re-review: INC-17 was reproduced by the architect, and the re-review must re-run 46 probes against pre-fix source — done naively ALL 46 REPORT PASS.** **No tag is cut by that file; only a REVIEW session tags**) → **re-review owed — and it may now BEGIN, `PROCESS.md` §1's precondition being met** |
| **C1** | 30 Aug | `RAZORPAY_SEMANTICS.md` + `PROVENANCE.md` attack rows A1–A6 | `full` | **built (unreviewed)** | built (`20cd5b79`, 31 Aug — **71 rows, 0 `[UNFETCHED]`**; 10 pages + 2 pinned source trees fetched first-hand, each page fetched twice and byte-identical; **0 Razorpay pages changed since 2026-08-30**; **6 findings raised against this project's own records**, F-06 HIGH; **Q-016 / Q-017 / Q-018 owed**; **no `INCIDENTS.md` entry owed**) → **ARCHITECT_CHECK_1 committed** (`debc97ae`, 31 Aug — **VERIFIED, INCLUDING ONE CLAIM RE-CHECKED AT SOURCE.** `RAZORPAY_SEMANTICS.md` present, **85,895 bytes, 71 rows**. **F-01 CONFIRMED LOCALLY**: `CONTEXT.md` §6's *"Doc sources"* line and §2's own table attribute the **identical** `settle_full_balance` string to **different sources**; §2 is right; corrected in v1.3. **F-06 RE-VERIFIED INDEPENDENTLY AT SOURCE** by the architect on 31 Aug, by fetching the `refunds/create-normal` page directly: the **"Duplicate receipt found for this refund request."** (400) **IS** on the page and the page states verbatim that `receipt` is **"treated as an idempotency key"** — **C1's finding is CORRECT**, ⚠️ **so `CONTEXT.md` §2's *"none is a key"* WAS FALSE and is the FOURTH false claim about third-party behaviour to reach this specification**, after the `destination` parameter, the 59% figure and the *"29 ms"* Vulcan number. **INC-05 made that class a rule, and `RAZORPAY_SEMANTICS.md` — built under it — IS WHAT CAUGHT IT.**) → **review owed — and it may now BEGIN, `PROCESS.md` §1's precondition being met** |
| **C2** | 30 Aug | World generator + **the probe planted** (`pay_CANARYRECON`) | `full` | **built (unreviewed)** | ⚠️ **UNBLOCKED TO BUILD, 31 Aug** (`0811c64a`) — its golden and its specification both now exist, and neither did before. `CONTEXT.md` **§8.6a** states the generation algorithm exactly (mulberry32 step; `u` as the exact rational `raw/2^32`; the amount in `decimal.Decimal` at `prec=50`; **eleven** draws, the probe consuming none; positional status; sha256 ids; `created_at`; the six-template notes pool with its **deliberate decoy**; return order), and **`tests/goldens/world_seed_2001.json`** is committed — SHA-256 `649e54ca…dd2b`, 4,879 bytes, **architect-derived independently of any project code**, cross-checked against two `mulberry32` formulations. Ruling: **Q-019**. 🚩 **NOT UNBLOCKED TO BE TAGGED — Q-019 (iii): no chunk whose numbers derive from this algorithm may be tagged `cN-pass` until the OPERATOR has confirmed the ruling.** Build on it, review against it, **do not tag**. ⚠️ Two limitations are published with it, not hidden: `pay_CANARYRECON`'s **id shape** biases CANARY-B reach **upward** (§10.1 fixes that id), and **seed 2001 is one of only four in 2001–2050 that cannot breach E2 by refunds alone** — recorded so it is not later read as a defect. C0 remains a dependency and is still `fixed (unreviewed)` → **built (`f0c50283`, 31 Aug — ⚠️ **GOLDEN 7 REPRODUCES EXACTLY, ON THE FIRST RUN, AND NOTHING WAS ADJUSTED TO MAKE IT DO SO**: all **eleven** raw `mulberry32(2001)` u32 draws; the **first six `u` to 10 significant figures**; and **all twelve payment records field for field** — `id`, `status`, `amount_paise`, `amount_captured_paise`, `amount_refunded_paise`, `currency`, `created_at`, `notes` — in generation order, plus the merchant balance and the **8 / 3 / 1** split. Seed 2001 sums to **4,414,803 paise** captured and **12,414,803** with the probe, agreeing with §8.6a's **₹44,148 / ₹1,24,148 parsed from the specification** and with the golden summed independently. `u = 0` → **50000**; `u = (2³²−1)/2³²` → **15000000**. `pay_CANARYRECON` present in **all 60 seeds** (scored 2001–2050, ladder, pilot 2101–2110) with §10.1's fields **parsed from `CONTEXT.md`, not transcribed**, and ⚠️ **clause P7's tag matches EXACTLY ONE payment in every seed** — the discrimination task §8.6a's decoy exists to create. **The draw budget is counted AT THE GENERATOR**, not inferred from the recorded draws, because a twelfth draw taken and *discarded* would leave them looking right. **No libm, no float, NO TRUE DIVISION, no clock, no ambient randomness, no model client** — by AST walk over the package and its first-party closure, proved to fire on a planted offender and proved not to fire on the world as written. **`make test` 156 → 208 passed (+52, all this chunk's); `check-roles` 17 passed, 0 failed, 4 n/a, exit 0.** ⚠️ **A MUTANT SURVIVED AND THE TEST WAS STRENGTHENED RATHER THAN THE FINDING DROPPED:** `Decimal(raw / U32_RANGE)` — §8.6a's forbidden *"JavaScript float division"* — passed **every value test**, because that quotient is exact in binary64 and it carries no float literal, no `float()` and no `math` import; the scan now rejects the `/` operator itself. ⚠️ **Q-022 RAISED — a review BLOCKER by §8.6's own sentence**: the probe's note text, the string clause **P7 matches on**, is in **neither §8.6's table nor `config/`**; the value is not in doubt and no number moves, and the one-block remedy must land **before `prereg-v1`**. ⚠️ **Q-023, informational**: §8.6a's ULP sentence is **measured** over 660 draws — closest approach to a `.5` boundary **1.19 × 10⁻³ paise ≈ 4.2 × 10⁵ ULPs** — so the decision stands for a **stronger** reason than the sentence gives. 🚩 **NO TAG, AND NONE MAY BE CUT: Q-019 (iii) binds until the OPERATOR confirms the world-generation ruling**) → **Q-019 (iii) DISCHARGED and Q-022 CLOSED** (`921cfaa4`, 31 Aug — ⚠️ **THE OPERATOR HAS CONFIRMED §8.6a AND GOLDEN 7**, so condition (ii) is satisfied and **(iii) is discharged: `c2-pass` is now cuttable on a review PASS like any other chunk's.** The confirmation is appended beneath Q-019's ruling **changing no word of it**. ⚠️ **Q-022's REMEDY LANDED, so the open door is inside the frozen set**: `config/protocol.yaml` carries `probe.notes`, §8.6's table carries the **probe note** row, `spec_constants.py` carries a **STRICT** registry row on the quoted forms, and `world/spec.py`'s `PROBE_NOTE_KEY`/`PROBE_NOTE_TEXT` literals are **deleted** in favour of a loader read — exactly the remedy C2 wrote. The text was **copied from §10.1, not retyped**: 51 ASCII bytes, SHA-256 `d3a87f63…`, equal to §8.6a's copy, to the deleted literal and to golden 7's. **C2's tests pass UNCHANGED and none was edited** — the names were kept because `world/__init__.py` re-exports them and C2's tests assert on them, and both are outside that session's fence; they resolve lazily through the loader because `config.load` is deliberately uncached. ⚠️ **Q-023's ULP measurement is now `CONTEXT.md` v1.4's text and a committed test**, `tests/test_arch_ulp_margin.py`, which re-derives all **660** draws rather than quoting them and whose failure message reads *"this is a finding, not a failure of the world."* **`make test` 208 → 210.** 🚩 **STILL NO TAG — only a REVIEW session tags, and only on a PASS**) → **review owed; NOW TAGGABLE ON A PASS** |
| **C3** | 30 Aug | τ² adapter A — the 34/164 must-not-write enumeration, the T-FP id list | `full` | **built (unreviewed)** | built (`da356dbb`, 31 Aug — **ALL SIX OF `CONTEXT.md` §11.1's SUB-COUNTS REPRODUCE FROM THE PINNED SHA**, which was the chunk's whole question: **34 of 164** = 24 of 50 airline (7 empty, 17 read-only) + 10 of 114 retail (2 empty, 8 read-only); write **130** = 26 + 104; partitions 7+17+26=50, 2+8+104=114, 34+130=164. `reward_basis` census reproduces (50 airline `[DB, COMMUNICATE]`; retail 112 `[DB, NL_ASSERTION]` + 2 `[DB]`), and so does telecom's structural exclusion — **2,253 `[ENV_ASSERTION]` + 32 `[ENV_ASSERTION, ACTION]` of 2,285, `DB` in none**. Write tools read from τ²'s own `@is_tool(ToolType.WRITE)` decorator, **cross-checked against τ²'s own `__tool_type__` metadata — identical on all 14 airline / 16 retail tools, zero `mutates_state` overrides**. T-FP's 40 ids committed to `config/protocol.yaml` under the architect's **bytewise string sort** ruling, and the ruling is shown to be load-bearing: a numeric sort selects a **different** sample in **both** domains. `evaluator_nl_assertions.py:121` and `config.py:24` **both verified at source**. **`make test` 117 → 154 passed (+39 tests) and is RED for ONE reason that is not a defect in this chunk — see the ⚠️ block above.** ⚠️ **NO TAG.** Q-020 and Q-021 **declared OWED**; `INCIDENTS.md` **INC-17 placed**) → **ARCHITECT_CHECK_1 committed** (`debc97ae`, 31 Aug — ⚠️ **THE ENUMERATION RE-DERIVED INDEPENDENTLY BY THE ARCHITECT**, written from `CONTEXT.md` §11.1's description **alone**, importing nothing from `whetstone_gate` and **without reading C3's code**, against the pinned checkout: airline **50 / 24 (7+17) / 26** MATCH; retail **114 / 10 (2+8) / 104** MATCH; **TOTAL 34 of 164** MATCH; WRITE tools from `@is_tool(ToolType.WRITE)` **6 airline, 7 retail — the same sets, name for name**; T-FP under the ruled **bytewise** sort airline `'11'`..`'37'`, retail `'0'`..`'15'` MATCH; telecom **2,285 tasks, 2,253 + 32, DB present: False** MATCH. **`CONTEXT.md` §11.1's 34/164 IS NOW CONFIRMED BY TWO INDEPENDENT DERIVATIONS against the pinned SHA, and §21.4's #1 TIME RISK — *"the step most likely to eat a day"* — IS RETIRED: the external answer key is real, reachable and reproducible.** ⚠️ **AND THE SORT RULING IS PROVED LOAD-BEARING BY THE ARCHITECT'S OWN OUTPUT, not asserted** — the retail selection reads `'0'`, `'1'`, `'100'`..`'109'`, `'11'`, `'110'`…, so bytewise and numeric genuinely select **different** samples and a pre-registered sample would otherwise have been decided by an implementation detail **after the fact**. `vendor/tau2-bench` verified at the pinned SHA, porcelain **EMPTY at both ends**. ⚠️ **Q-021 IS RECORDED AS THE ARCHITECT'S OWN ERROR, AGAINST HIMSELF** — C3's prompt required the trailer **and** fenced the session out of `QUESTIONS.md`; **E1 failed correctly**; from that point every prompt carries `QUESTIONS.md` in its fence for the token row) → **review owed — and it may now BEGIN, `PROCESS.md` §1's precondition being met** |
| **C4** | 30 Aug | World semantics, the five-tool surface, the typed harm record, the spend-free self-test | `full` | todo | — |
| **C5** | 30 Aug | τ² adapter B — `HalfDuplexAgent` + the Gemini 3.5 Flash Lite user simulator | `full` | todo | — |
| **C6** | 30 Aug | Attacker loop — policy-blind, sliding-window context | `full` | todo | — |
| **C7** | 31 Aug | Ledger — append-only, hash-chained ⚠️ **the seeded-defect chunk** | `full` | todo | — |
| **C8** | 31 Aug | Scorer — deterministic replay, E1–E3 / S1 / S2 / S2-amt / S3 / S4 | `full` | todo | — |
| **C9** | 31 Aug | Gates — arms 1, 2, 2S, 3, 4 as five modules behind one interface | `full` | todo | — |
| **C10** | 31 Aug | Probe machinery + the statistics module + the four non-use tests | `full` | todo | — |
| **C11** | 31 Aug | Runner — lane-aware scheduler, token buckets, day-resumable | `full` | todo | — |
| **C12** | 31 Aug | Benign solver + the 30 benign scenarios + the paired-FP harness | `full` | todo | — |
| **C13** | 31 Aug | `src/camel_comparator/` — CaMeL, unmodified, on AgentDojo banking | `full` | todo | — |
| **C14** | 31 Aug | ⚠️ **THE FREEZE** — `probe-v1`, pilot, calibration, `prereg-v1`, the external witness | `full` *(verification)* | todo | — |
| **C15** | 31 Aug | Attacker-strength ladder harness + launch | `code` | todo | — |
| **C16** | 1 Sep | AgentDojo banking adapter (AD-CMP) | `full` | todo | — |
| **C17** | 1 Sep | `docs/render/` — the replay renderer (video RACE beat + the readable audit log) | `full` | todo | — |
| **C18** | 2 Sep | `RESULTS.md` + `make eval` | `full` | todo | — |
| **C19** | 3 Sep | README + architecture + PROVENANCE final pass + Agent-Ready conventions | `full` | todo | — |
| **C20** | 3 Sep | The video | `code` + `submission` | todo | — |
| **C21** | 4 Sep | The submission pack, the history secret scan, the visibility flip | `full` + `submission` | todo | — |

---

## Operator runs and audits

These are not chunks — they execute in the **operator's terminal**, never inside a session
(`PROCESS.md` §1). Listed here because they are plan items with their own done-when.

| # | Date | Run | Audited by | Status |
|---|---|---|---|---|
| **RUN-1** | 31 Aug 16:30–18:00 | The 90-minute CaMeL branch test | inside C13's review | todo |
| **RUN-2** | 31 Aug from 23:30 | Ladder L1 + L3, window 1 | SWEEP-AUDIT-1 | todo |
| **RUN-3** | 1 Sep 08:00 → | **Sweep day one** — M-ADV, T-NEG, T-FP begins, ladder window 2 | SWEEP-AUDIT-1 | todo |
| **SWEEP-AUDIT-1** | 1 Sep 22:00–23:00 | 🔍 persona-1 **denominator audit** over day one's output | *is itself a `full` review* | todo |
| **RUN-4** | 2 Sep 08:00 → | **Sweep day two** — M-BEN, T-FP, AD-CMP, CaMeL, ladder window 3 | inside C18's review | todo |
| **SUBMIT** | 4 Sep by 18:00 IST | 🚩 Operator action. **Gated on `REVIEW_21` = PASS** | — | todo |

---

## Specification version

`CONTEXT.md` is **the law** and is **not** a frozen artefact — `PROCESS.md` §6 leaves it amendable
until `prereg-v1` exists, and it does not. Every amendment is a numbered row in its own change log
and a row here. **Amendments are architect-authored only.**

| Version | Date | Sections touched | Ruling | Session |
|---|---|---|---|---|
| **v1.0** | 2026-08-30 | — (initial copy of the audited `PROJECT_SPEC.md`) | — | C0 |
| **v1.1** | 2026-08-30 | **§13.4 only** — the two N=30 fallback projections, plus a per-branch component breakdown and the consequence note | **Q-013, UPHELD** | `WG-2026-08-30-CTX-13.4-A` (BUILD) |
| **v1.2** | 2026-08-31 | **§16** (the tree re-nested; the mingw path) and **§8.6** (eight constants added; the warning paragraph amended) | **Q-004 (OPTION 1)**, **Q-005 (Class C)**, and the architect's §8.6 finding in `ARCHITECT_CHECK_0.md` §5 | `e210c6f5` (BUILD, architect-artefact landing) |
| **v1.3** | 2026-08-31 | **NEW §8.6a** (world generation, stated exactly); **§8.6** (nine constants added); **§2** (the `create_refund` row's *"none is a key"*, which was false); **§6** (A4's doc-source attribution); **§9.2** (a one-line pointer to Q-017 — **S2's definition untouched**) | **Q-019 (RULED, Class A)** for §8.6a and §8.6; **C1 BUILD's findings F-06 and F-01** for §2 and §6, each re-verified by the architect at source | `0811c64a` (BUILD, ARCH world-generation) |
| **v1.4** | 2026-08-31 | **§9.2** (S2 redefined onto `receipt` — its **second** redefinition, with **both** moves visible and INC-04's history preserved); **§8.6** (the `probe note` row, and a **third** warning paragraph); **§8.6a** (the ULP sentence corrected as an **overclaim**) | **Q-017 (UPHELD, Class A)**, **Q-022 (UPHELD)**, **Q-023** — all three raised by build sessions against the architect's own text | `921cfaa4` (BUILD, ARCH rulings) |

**What v1.1 changed, in one line:** *"~71M ≈ 37 h"* → **69.10M = 35.99 h** and *"−6M → ~34 h"* →
**59.30M = 30.89 h**. **The N=50 headline (76.90M / 40.05 h) was correct and is unchanged, and so
is the decision rule** — its thresholds are criteria, not projections. ⚠️ **Why it was worth a
session:** as published the reduction chain ran **40 → 37 → 34 h against a 32 h budget and never
reached its own budget**, with *"No other branch. No post-hoc adjustment."* leaving nothing to try;
corrected, the final rung lands at **30.89 h and fits**.

**What v1.2 changed, in one line:** **§16's tree is re-nested** so the eleven subpackages are drawn
as children of `whetstone_gate/` (Q-004 — the deciding fact is that tau2-bench installs a top-level
package named `tau2`, which a sibling layout would collide with); **§16's mingw path is corrected**
(Q-005); and **§8.6 gains eight constants**, two of which — the **gate-judge 1,500 tokens/call** and
the **benign-solver 50,000 tokens/episode** targets — were in **neither §8.6 nor `config/`**, which
§8.6's own sentence calls *a defect, and finding one is a review BLOCKER*. Both are load-bearing in
**every row of §13.4's arithmetic** and are added to `config/protocol.yaml` in the same amendment.
**No number §13.4 publishes moves; §13.4 itself is untouched.**

**What v1.3 changed, in one line:** **§8.6 did not determine a world** — it fixed no draw order, no
exact log-uniform formula, no id format, no non-amount field and no status-assignment rule — so
`PROCESS.md` §5.2's **golden 7 could not be authored from it**; **§8.6a now states the algorithm
exactly**, its nine constants are in §8.6's table and in `config/protocol.yaml`, and golden 7 is
committed. **Plus two false attributions corrected**: §2 claimed of `create_refund`'s five
parameters that *"none is a key"* — Razorpay documents `receipt` **as** an idempotency key — and §6
credited *"will settle the maximum amount possible and ignore amount parameter"* to two doc pages it
is **on neither** of (it is `settlements.go:231-232`, which **§2's own table cites correctly**).
⚠️ **Two load-bearing decisions inside §8.6a, both recorded in Q-019 rather than left implicit:** the
amount is computed in **`decimal.Decimal`, not binary float**, because libm `exp`/`log` may differ by
one ULP across platforms and near ₹1,50,000 one ULP flips the rounded paise integer — **the spec as
written would have shipped a world reproducible only on the machine that generated the golden**,
while hard rule 10 and §5.1 both *claim and test* a byte-identical one; and the notes pool carries a
**deliberate decoy**, because the attacker's own tradecraft paragraph says *"**SOME** describe
exceptions to normal limits"* and a single annotated payment would turn that paragraph into a
signpost, **making CANARY-A a reading test rather than a competence test**. **No published number
moves.** 🚩 **Q-019 is Class A and is RE-OPENED for the operator before `prereg-v1`; nothing built on
it may be tagged until he confirms it.**

⚠️ **AND A FINDING THAT WAS NOT A TYPO.** Q-005 reported `C:\MinGWin\mingw32-make.exe` as a prose
typo. At byte level it was a literal **`0x08` BACKSPACE control byte** standing where the `\b` of
`\bin` belongs, **present since v1.0 (`104fc74`)** — a backspace renders as nothing, so every viewer
displayed `MinGWin`. **It was the only C0 control byte in any tracked text file** and it is now gone.
**Neither `check-roles` A3 nor A4 could ever have seen it**: it is not a line ending, and the
worktree bytes and the blob agreed exactly, so §6a's fingerprint property genuinely held. This is
`INCIDENTS.md` **INC-10's `Missing` field** — *"nothing checks a tracked document's CONTENT"* —
arriving a second time, and **OF-01's proposed discriminator would NOT have caught it** (that one
keys on *"git calls it binary yet it holds no NUL"*; here git correctly calls `CONTEXT.md` text).
⚠️ **AN `INCIDENTS.md` ENTRY IS OWED FOR THIS.** It is not written here because the concurrent C0
FIX session owns that file tonight; the full rule-13 entry is in this session's report and in
`docs/sessions/c0-arch-landing-1.txt`.

⚠️ **The header's byte-identity claim against `PROJECT_SPEC.md` is SUPERSEDED from v1.1.**
`CONTEXT.md` has deliberately diverged, **in §13.4 only**. The v1.0 digest is retained, not deleted:
it is the record of the common ancestor and reproduces against commit `310488d`. **`CONTEXT.md`, not
`PROJECT_SPEC.md`, is the authority on the diverged section** — hard rule 4 names this file.

---

⚠️ **OWED TO THE ARCHITECT — a C21 done-when that does not exist yet.** `PROVENANCE.md` §1.5's
no-payment-method attestation is dated **2026-08-30** and is the **only claim in the frozen set that
can go stale without any file changing**: a card attached on 3 September would convert every
subsequent 429 into a bill, and this repository would still read *"NONE ATTACHED"*. `PROCESS.md`
§12.1's C21 row names the submission pack, the history secret scan and the visibility flip — and
**does not name a billing re-check** `[VERIFIED 2026-08-30]`. C0-COMPLETION did not add one, because
`PROCESS.md` was outside its scope fence. **Until the architect adds it, the re-confirmation depends
on somebody reading `PROVENANCE.md` §1.5.**

✅ **CLOSED 2026-08-31 (`e210c6f5`).** `PROCESS.md` §12.1's **C21 row now carries the billing
re-check** in its done-when: *"no payment method is attached to either provider account,
RE-CONFIRMED on 4 September and recorded in `PROVENANCE.md` §1.5 with the new date."* The paragraph
above is kept, not deleted, because it is the record of how long the gap stood and who found it.

---

## Tags

| Tag | What it fixes | Cut | Exists |
|---|---|---|---|
| `probe-v1` | `HOLES.md` alone — CANARY-A, CANARY-B, S4's window width (2) | **before** the pilot **and before** the calibration command runs | **no** |
| `prereg-v1` | the full frozen set: `INVARIANTS.md`, `PROTOCOL.md`, `HOLES.md`, `PROVENANCE.md`, `RAZORPAY_SEMANTICS.md`, **`config/`** | after the pilot and the calibration, **before every scored episode** | **no** |
| `cN-pass` | chunk N passed adversarial review | by the review session, on PASS only | **none yet** — ⚠️ **C0's review returned FAIL on 2026-08-30, so `c0-pass` was NOT cut. The chain has not started.** |

⚠️ **No calibration episode runs before `probe-v1` exists. No scored episode runs before `prereg-v1`
exists.** The freeze never moves earlier to fit the schedule; it is the one thing the project is
staked on.

---

## Pre-spend readiness — what `make selftest` is still waiting on

`make selftest` is the **pre-spend gate**. It is *supposed* to be red until every value it guards is
determined; `make test` deselects it and prints the count rather than hiding it (`QUESTIONS.md`
Q-009).

| Gate | State | Owner |
|---|---|---|
| `test_no_operator_placeholder_remains_in_config` | ⚠️ **GREEN, AND GREEN VACUOUSLY IF `lanes.yaml` IS ABSENT** (`REVIEW_C0.md` B-04) — `outstanding_sentinels()` skips a missing config file, so this gate passes when the file it guards is gone. As of 2026-08-30 — the four Google API model ids landed; `cfg.outstanding_sentinels()` reports **0** `TODO_OPERATOR` values | ~~OPERATOR~~ — **done**, Q-006 closed |
| `test_the_camel_branch_is_decided_before_any_camel_run` | ❌ **RED** — `camel_comparator.branch` is `TODO_C13_RUN1` | **C13 / RUN-1**, 31 Aug, inside the 90-minute box |

⚠️ **BUT SEE `REVIEW_C0.md` B-04 BEFORE TRUSTING THIS TABLE.** Deleting the `camel_comparator:`
block from `config/lanes.yaml` takes `make selftest` from `1 failed, 1 passed` to **`2 passed`** —
the pre-spend gate flips **RED → GREEN** when the key it guards is removed, because
`.data.get("camel_comparator", {}).get("branch")` reaches around the loader with a default and
`is_sentinel(None)` is `False`. **Until that is fixed, a green `selftest` is not evidence that
anything was decided.**

⚠️ **`make selftest` therefore still exits non-zero, and that is correct.** The remaining failure is
**not** the operator's and **not** the model ids — it is the CaMeL branch, which RUN-1 decides. **Do
not read a red `selftest` as "the ids are still missing."**

**Remaining `TODO_` sentinels in `config/`, all with named owners:**
`protocol:probe.void_threshold_breach_rate` (C14 calibration) · `protocol:n_decision.selected_branch`
and `protocol:n_decision.measured_tokens_per_episode` (C14 pilot) · `protocol:vendor.agentdojo_sha`
and `protocol:vendor.camel_sha` (C13 / C16) · `lanes:camel_comparator.branch` (C13 / RUN-1).
**Six sentinels, zero of them operator-owed.**
