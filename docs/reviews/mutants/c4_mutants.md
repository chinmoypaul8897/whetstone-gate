# C4 mutation run — review 1

**SESSION-TOKEN:** `0852ea56` · **Role:** REVIEW · **Chunk:** C4 · **Date:** 2026-09-01
**Review type:** `full`, `PROCESS.md` §12.1 — **minimum eight mutants plus a control.**

**SIXTEEN MUTANTS AND TWO CONTROLS RAN. FIFTEEN KILLED, ONE PROVEN EQUIVALENT AND REPLACED,
ZERO SURVIVORS. BOTH CONTROLS SURVIVED, SO BOTH RUNS ARE VALID.**

Two campaigns, because four of this review's probes were written *after* the first clone was
taken and it would have been dishonest to claim a score for them:

| | mutants | control | scope | result |
|---|---|---|---|---|
| **Campaign 1** — the main run | M-01 … M-12 | `CONTROL` | the **whole suite**, clone at `6d124f8` | 11 killed, **M-12 EQUIVALENT**, control survived |
| **Campaign 2** — targeted | M-12b, M-13 … M-15 | `CONTROL-2` | C4's four test files, clone at `fe71ca3` | **4 killed**, control survived |

⚠️ **M-12 SURVIVED AND WAS THEN PROVEN EQUIVALENT RATHER THAN REPORTED AS A SURVIVOR OR
QUIETLY DROPPED.** It patched the `RECORDED` parser to drop the last **line** of §6's slice —
and that line is **blank**, so the census still parsed 18 rows and no behaviour changed. That
is a defect in the mutant, not a gap in the suite, and the discipline that caught it is the
one INC-11 exists for: *a mutant must be shown to change behaviour before its verdict means
anything.* **M-12b** does the genuine thing — drops the last matching **row**, 18 → 17 — and
is **KILLED**.

⚠️ **M-15 IS THE ONE THAT FOUND A REAL GAP IN THE SHIPPED SUITE.** Exactly one test catches
it, and it is one this review added:
`test_must_hold_rs11_idempotency_covers_BOTH_refund_speeds`. Before it, a change making the
idempotency key stop covering both refund speeds — **RS-11's own stated property** — would
have passed every test in the repository.

---

## Method, and the three traps it is built to avoid

Every mutant aims at an **operator that moves a published number**: the fee's integer form and
its rounding, each A4 threshold and the ladder's order, the window width and which fields it
staleness, the duplicate-`receipt` predicate and its non-empty clause, the
`rejected_by_razorpay` zeroing, an A-class trigger, and the census parser.

### INC-11 — a mutant that scores a "kill" merely by existing on disk

`tests/test_repo_invariants.py::test_the_object_store_and_the_working_tree_agree` compares
every tracked file's working-tree bytes against the object store, so **any** uncommitted edit
fails it and would kill **every** mutant including the control. INC-11 records that happening:
*"18 of 18 killed"*, control included, and the run correctly discarded.

**Every mutant below was COMMITTED before it ran**, inside the clone, and
`git status --porcelain` is captured as `TREE: clean` on all fourteen runs. Each mutant is
then reverted by a second commit, so the next one starts from the baseline rather than from
its predecessor.

⚠️ **AND THIS REVIEW TRIPPED THE SAME TRAP ITSELF, AT THE BASELINE, BEFORE ANY MUTANT RAN.**
The Phase-1 commit produced `docs/reviews/independent/c4_reimpl_expected.json` through
`Path.write_text()`, which on Windows translates `\n` to `\r\n`. `.gitattributes` is
`* text=auto eol=lf`, so the object store held LF and the working tree held CRLF —
**1,221 CR bytes** — and that invariant went **RED**. A mutation baseline taken from that tree
would have been **VOID for a reason having nothing to do with C4**. It is **C2 REVIEW's own
recorded defect one tool along** (that session produced its `c2_reimpl_expected.json` through
a Windows shell redirect and tripped the identical trap) and it is INC-24's class. Caught at
the baseline, fixed in `51404cc` by taking the translating layer out of the path
(`open(..., newline="\n")`), with the reason written beside the call. **OWED to
`INCIDENTS.md`, which a review session may not write.**

### INC-17 — an editable install that resolves `whetstone_gate` by name

`src/` is on `sys.path` through a `.pth`, so a bare `pytest` inside a clone still imports the
**live repository**. `PYTHONPATH` is therefore set to the tree under test and
**`whetstone_gate.__file__` is printed and recorded on every single run**:

```
whetstone_gate.__file__ = C:\Users\chinm\AppData\Local\Temp\claude\
                          c--Users-chinm-whetstone-gate\4099700c-447c-4b22-aa22-1f6e38356463\
                          scratchpad\mut\tree\src\whetstone_gate\__init__.py
```

**Never the live tree, on any of the fourteen runs.** A run that does not state which tree it
loaded is not evidence.

### `REVIEW_C0_2` — a concurrent session moving the baseline under the run

⚠️ **This is not a hypothetical here: a C6 FIX session (`7b99a85a`) ran concurrently with this
review for its entire length and committed four times while it was in progress** —
`2911ad0`, `17585ab`, `1ad8946`, `6d124f8`. The whole campaign therefore ran **in a clone, in
an OS temp directory** (`CLAUDE.md` §4: *"throwaway work goes to a fresh OS temp directory,
never into the repository"*), on a **frozen snapshot**. No concurrent commit could move a
single one of the fourteen runs, and the live tree was never touched.

⚠️ **`git reset --hard` WAS DELIBERATELY NOT USED**, even though INC-11's own remedy names it.
The live tree held another session's uncommitted work for most of this review, and a stray
hard reset would have destroyed it. Reverts inside the clone are ordinary commits.

---

## Scoring, and why it is set-based rather than count-based

**The oracle is the FAILURE SET, not a count.** A mutant is **KILLED** when its failure set
differs from the baseline's; it **SURVIVED** when the two are identical.

The clone's baseline is redder than the live tree, and **every extra red is attributed rather
than waved through**:

| Baseline at `6d124f8`, tree clean, **2026-09-01T04:33:28Z** | |
|---|---|
| **420 passed, 13 failed, 1 skipped, 12 errors** | |
| 11 failures + **all 12 errors** | the absent `vendor/tau2-bench` checkout — **793 MB, pinned not committed** under `Q-010`, `.gitignore` carries `vendor/*/`, so a clone cannot have it. All in `tests/test_c3_*`: **C3's territory, not C4's** |
| 1 failure | `test_the_camel_branch_is_decided_before_any_camel_run` — an **operator placeholder**, resolved by C13/RUN-1 |
| 1 failure | `test_the_windowed_context_stops_growing_which_is_what_the_window_is_FOR` — the concurrent C6 FIX session's **declared STOP**, `Q-050` / `INC-29`, red in the live tree too by that session's own decision |

Set-based scoring is insensitive to a stable, attributed red — and **that is exactly what
makes a control meaningful**, because a control that changes no behaviour must reproduce the
baseline set exactly.

For comparison, the **live** tree at this review's own baseline
(`3510428`, clean, **2026-09-01T03:48:57Z**) was **397 passed, 1 failed, 1 skipped** — the
CaMeL placeholder alone.

---

## The table

### Campaign 1 — the whole suite, clone at `6d124f8`, baseline **2026-09-01T04:33:28Z**

Every run: `TREE: clean`, and `whetstone_gate.__file__` resolving **inside the clone**.

| # | Mutant — the operator moved | File | Verdict | New | First tests that caught it |
|---|---|---|---|---|---|
| **M-01** | the fee's `+ half` term removed — **ROUND_HALF_UP becomes truncation** | `money.py` | **KILLED** | 2 | `test_every_golden_1_fee_vector_reproduces_in_the_exact_integer_form`; `test_the_decimal_form_and_the_integer_form_agree_on_every_vector` |
| **M-02** | the basis-point denominator becomes **1000**, not 10000 — a **10× fee** | `money.py` | **KILLED** | 14 | every golden-1 vector, golden 3's five entries, its episode totals, and the live-world whole action |
| **M-03** | the A4 ladder checked **BALANCE FIRST**, so RS-16 is unfireable | `semantics.py` | **KILLED** | 16 | `test_a_balance_first_order_would_make_RS16_UNFIREABLE`; `test_each_a4_ceiling_owns_a_non_empty_band_at_its_exact_boundary`; the self-test on RS-16 |
| **M-04** | the IMPS ceiling fires **at** the cap, not above it — OF-44 / Q-042's boundary | `semantics.py` | **KILLED** | 8 | golden 3's ledger, its episode totals and `productive_actions`; `test_each_a4_ceiling_owns_a_non_empty_band_at_its_exact_boundary` |
| **M-05** | the S4 window is **one tool call short** | `semantics.py` | **KILLED** | 10 | `test_all_four_redundant_fields_go_stale_together_in_BOTH_readers`; the self-test |
| **M-06** | the window staleness `amount_refunded` but leaves **`status` CURRENT** — RS-46's own build hazard | `semantics.py` | **KILLED** | 9 | `test_all_four_redundant_fields_go_stale_together_in_BOTH_readers`; the self-test's RS-46 hold |
| **M-07** | the duplicate-`receipt` predicate loses its **NON-EMPTY** clause — **INC-04 rebuilt** | `semantics.py` | **KILLED** | 20 | `test_two_refunds_that_both_OMIT_receipt_are_NOT_treated_as_a_replay`; `test_a_refund_behind_another_REFUND_executes…`; `test_the_BOUNDARY_is_never_stale_only_reads_are` |
| **M-08** | a **Razorpay-rejected record keeps its harm** instead of four zeros | `harm.py` | **KILLED** | 5 | `test_golden_3s_two_rejected_entries_contribute_zero_to_all_four`; `test_a_rejected_record_is_zero_on_all_four_however_it_is_constructed`; `test_a_duplicate_receipt_is_refused_with_harm_zero…` |
| **M-09** | A4 books the settlement **principal as irrecoverable outflow**, not float | `harm.py` | **KILLED** | 4 | golden 1's whole action **through both paths**, and golden 3's ledger + episode totals |
| **M-10** | ⚠️ **RS-23 refuses a refund behind another REFUND — invariant S4 DELETED** | `semantics.py` | **KILLED** | 23 | `test_a_refund_behind_another_REFUND_executes_or_invariant_S4_can_never_fire`; golden 3's ledger; the self-test |
| **M-11** | the A4 attempt counter **ignores REFUSED attempts** — Q-028's reading reversed | `semantics.py` | **KILLED** | 14 | `test_rs19_fires_by_exhausting_the_counter_with_REFUSED_attempts`; the self-test on RS-19 |
| **M-12** | the census parser drops the last **line** of §6's slice | `oracle.py` | ⚠️ **EQUIVALENT** | 0 | the dropped line is **blank**; 18 rows still parse. Replaced by **M-12b** |
| **CONTROL** | a local renamed and a comment added in `_daily_remaining` | `semantics.py` | ✅ **SURVIVED** | 0 | **the run is VALID** |

### Campaign 2 — C4's four test files, clone at `fe71ca3`, baseline **2026-09-01T05:15:51Z**

Baseline: **112 passed, 0 failed.** Every run: `TREE: clean`, `__file__` inside `tree2`.

| # | Mutant | File | Verdict | Caught by |
|---|---|---|---|---|
| **M-12b** | the census parser drops the last **RECORDED ROW** — 18 → 17 | `oracle.py` | **KILLED** (1) | `test_the_oracle_partitions_all_seventy_one_rows_and_the_counts_are_the_files_own` — **C4's own test** |
| **M-13** | **RS-21 removed**, so an A6 refund on an `authorized` payment EXECUTES | `semantics.py` | **KILLED** (14) | `test_a6s_else_branch_is_unreachable_over_every_authorized_payment_of_twenty_seeds` (this review's, closing **OF-54**); `test_split_rs04_rs21_an_AUTHORIZED_payment_fires_RS21_not_RS04`; the self-test |
| **M-14** | the idempotency key's **CHARSET** clause (RS-08) dropped, length kept | `semantics.py` | **KILLED** (13) | `test_must_hold_rs05_enforces_BOTH_halves_of_the_documented_key_shape` (this review's); the self-test's boundary-only set |
| **M-15** | ⚠️ the idempotency body **ignores `speed`**, so RS-11 stops covering both speeds | `semantics.py` | **KILLED** (1) | **`test_must_hold_rs11_idempotency_covers_BOTH_refund_speeds` — THIS REVIEW'S PROBE, AND THE ONLY TEST IN THE REPOSITORY THAT CATCHES IT** |
| **CONTROL-2** | a local introduced in the refund ladder | `semantics.py` | ✅ **SURVIVED** | **the run is VALID** |

---

## What survived, and what that means

**Nothing survived that should not have.** One mutant survived and was then **proven
equivalent by hand** rather than reported as a finding — the check INC-11 exists to force —
and its genuine replacement was killed.

**What the run establishes, stated at its true weight:**

* **The published numbers are defended.** M-01, M-02, M-04, M-08 and M-09 each move a figure
  that reaches `RESULTS.md`, and each is killed by a **golden** — which is what a golden is
  for, and is the thing a review can most easily take on trust and must not.
* **The order is defended, not merely documented.** M-03 reproduces in source exactly the
  claim C4 makes in prose — a balance-first ladder leaves RS-16 with an empty firing band —
  and the suite catches it.
* ⚠️ **THE MOAT IS DEFENDED.** M-10 takes RS-23's own reading and refuses a refund behind
  another refund. That deletes invariant **S4**, *"the genuinely un-representable one"*, and
  it is killed by **23 tests**, the first being the probe written for exactly that property.
* **INC-04 is defended.** M-07 removes §9.2's non-empty clause and rebuilds the predicate that
  blocked legitimate instalment refunds in 8 of 8 seeds. Killed by **20** tests.
* ⚠️ **AND ONE REAL GAP WAS FOUND AND CLOSED.** M-15 is caught by exactly one test, added by
  this review. Without it, RS-11's stated property — that idempotency covers **both** refund
  speeds — had no defender anywhere in the repository.

**What this run does NOT establish**, stated rather than left to inference: campaign 2 ran
only C4's four test files, not the whole suite, so its four verdicts answer *"does the probe
detect the defect it was written for"* — hard rule 6's *"provably meaningful"* bar — and
**not** *"does the whole suite detect it"*. Campaign 1 is what carries the suite-wide score.

**And what neither campaign can establish:** a mutation score measures the suite's sensitivity
to the defects **someone thought to write**. Sixteen operators is not the space of defects.
The reimplementation diff (§2a of `REVIEW_C4_1.md`) is the half of this review that does not
depend on the reviewer having guessed the right mutation.
