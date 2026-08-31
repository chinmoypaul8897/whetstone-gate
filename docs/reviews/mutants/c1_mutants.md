# `c1_mutants.md` — the mutation run for C1, adversarial re-review **attempt 2**

**`SESSION-TOKEN: df238be6`** · **Role:** REVIEW · **Chunk:** C1 · 2026-08-31
Companion to `docs/reviews/REVIEW_C1_2.md`. `REVIEW_C1_1.md`'s own 12-mutant table is **not
superseded and not edited** — it is the baseline this run is measured against.

---

## 0. The adaptation, and why the interesting question changed

**ARCHITECT RULING, 2026-08-31** (carried forward from attempt 1): for an oracle document the
mutation analogue is *corrupt a row and see whether anything catches it.*

⚠️ **At attempt 1 there was almost nothing to catch anything** — `RAZORPAY_SEMANTICS.md` §0
published a *"re-runnable check"* with **no implementation anywhere in the repository**, and 11 of
12 mutants were invisible to `make test`. **There is now an implementation**
(`tests/test_c1_semantics_check.py`) and six configured A4 constants, so this run asks two
different questions:

1. **Do attempt 1's four *"caught by NOTHING"* mutants die now?**
2. **Do the NEW artefacts defend themselves?** — the six A4 keys in their three places, and the
   five properties §0 now publishes.

---

## 1. Method, and the two ways this run could have been void

**Throwaway tree only.** Every mutant is applied to a fresh `git checkout -- .` of a **clone** in
an OS temp directory. The artefacts under review were **never mutated in place**;
`git status --porcelain` on the mutation tree is printed after the last mutant and is **empty**,
and `git status` on the live repository shows only this session's own intended commits.

⚠️ **INC-17, enforced rather than remembered.** Before **every** pytest run the harness executes a
separate interpreter with the same environment and asserts the mutant tree's name appears in
`whetstone_gate.__file__`; it raises `SystemExit` otherwise. INC-17 is the entry about a mutation
subprocess that had lost `PYTHONPATH`, tested the **live** repository, and reported every mutant
passing — *"nothing in the output looked wrong."* It fooled attempt 1's harness once and the C1 FIX
session's once.

⚠️ **INC-11, and the baseline this run refused to take.** `make test` at the base SHA `af76310` was
**RED**, and the red belonged to the **concurrent architect goldens session**, not to C1:
`tests/test_c2_world.py::test_the_golden_is_the_byte_for_byte_file_the_architect_authored` parses
`tests/goldens/README.md` for `` SHA-256 `<64 hex>` `` and demands **exactly one**; that README
carried **three**, because goldens 1 and 3 were placed in `5559b72`. INC-11 is precisely the entry
about a baseline taken from an already-red tree — *"every mutant scoring 'killed' by a red that was
already red."* So this run scores against a **selection that is green at the base SHA** and says so:

*(⚠️ **That red is now CLOSED, and not by this review** — the concurrent session found it in its own
baseline, fixed it in `165f1e6` and raised `Q-035`. `make test` at the SHA C1 passes on is **306
passed, 1 skipped, 2 deselected**. The scoping decision below is left exactly as it was taken,
because it was right when it was taken and a run's method is not rewritten by later news.)*

```
tests/test_c1_semantics_check.py   tests/test_c1_fix_probes.py
tests/test_c1_review_probes.py     tests/test_c1_review_2_probes.py
tests/test_tripwire_registry.py    tests/test_config_loader.py
```

**Baseline at each base SHA: green.** (`65 passed` before this review's probes; `77 passed` after.)
The harness **aborts and prints the failures** rather than scoring, if the baseline is ever red —
it did abort, twice, during construction, and both aborts were this session's own fault.

**Detectors.** **D1** = the C1 test files as the fix session left them (`test_c1_semantics_check.py`
+ `test_c1_fix_probes.py`) plus attempt 1's `test_c1_review_probes.py`. **D2** = the six probes this
review adds, `tests/test_c1_review_2_probes.py`.

---

## 2. The table — 18 mutants and one control

Base SHA for the **before** column: `af76310`. For the **after** column: `086e469`/`2ac35a5`
(this review's probes committed).

| # | Mutation | Where | before D2 | after D2 | Killed by |
|---|---|---|---|---|---|
| **M-02** | **a dropped negation** — RS-18's *"NO FIGURE IS PUBLISHED, AND THIS FILE DOES NOT SUPPLY ONE"* → *"A FIGURE IS PUBLISHED…"* | RS-18 **prose** | ⚠️ nothing | ⚠️ **nothing** | — |
| **M-03** | a documented `409` rewritten to `400` | RS-09, **inside the quote** | **KILLED** | **KILLED** | `…http_code_agrees…`, P1 |
| **M-06** | **a wrong `file:line`** — `refunds.go:73-75` → `:71-73` | RS-12(ii) **prose** | ⚠️ nothing | ⚠️ **nothing** | — |
| **M-12** | **a remediation lifted from the wrong page** — RS-22 given RS-23's `solution`, *still a verbatim Razorpay quote* | RS-22, inside the quote | ⚠️ nothing | ✅ **KILLED** | **P1** |
| **M-14** | a configured A4 value wrong by 10× — `daily_withdrawable_limit_paise` `30000000` → `3000000` | `config/protocol.yaml` | **KILLED** | **KILLED** | loader probe, P2, P6 |
| **M-15** | **§8.6's PRINTED value diverges from `config/`** — `30,000,000` → `300,000,000`, `config/` untouched | `CONTEXT.md` §8.6 | ⚠️ nothing | ✅ **KILLED** | **P2** |
| **M-16** | **a TAG flipped in §8.6** — `[Razorpay-defined]` → `[merchant-policy, author-chosen]` on *A4 max per settlement* | `CONTEXT.md` §8.6 | ⚠️ nothing | ✅ **KILLED** | **P3** |
| **M-17** | `max_per_settlement_paise` → `50000000000` — **the 10× figure Q-029 rejected** | `config/protocol.yaml` | **KILLED** | **KILLED** | Q-029 probe, P6 |
| **M-18** | an A4 **registry row deleted** (`a4_max_attempts_per_day`) | `spec_constants.py` | **KILLED** | **KILLED** | 4 tests incl. P2, P3 |
| **M-19** | **§8's quote of `CONTEXT.md` corrupted** — the one line checked verbatim offline | RS §8 | **KILLED** | **KILLED** | §8 verbatim test, P1 |
| **M-20** | a cited `Source` changed to `S13`, which §1 does not list | RS-15 | **KILLED** | **KILLED** | 2 source tests |
| **M-21** | **a quote emptied** to a bare `>` | RS-19 | **KILLED** | **KILLED** | 3 tests, + P1 |
| **M-22** | a changed digit **inside a quote** on a row whose `HTTP` is `n/a` — `maximum` → `minimum` | RS-13 | ⚠️ nothing | ✅ **KILLED** | **P1** |
| **M-23** | **RS-16's DERIVATION corrupted to the 10× reading** — `10⁷`/`50,000,000 rupees` → `10⁸`/`500,000,000` | RS-16 **prose** | ⚠️ nothing | ⚠️ **nothing** | — |
| **M-24** | **the SIXTH key's TAG flipped** in the registry — `a4_max_per_settlement_paise` | `spec_constants.py` | ⚠️ nothing | ✅ **KILLED** | **P3** |
| **M-25** | ⚠️ **TAG CONTROL** — the identical flip on `a4_imps_outside_banking_hours_cap_paise`, which **is** in `A4_KEYS` | `spec_constants.py` | **KILLED** | **KILLED** | existing tag probe, P3 |
| **M-26** | **RS-22's own quoted `400` → `409`, in the `> **code:** 400` bold form** | RS-22, inside the quote | ⚠️ nothing | ✅ **KILLED** | **P1** |
| **M-27** | ⚠️ **CODE CONTROL** — the identical corruption on RS-01, whose code line is plain | RS-01, inside the quote | **KILLED** | **KILLED** | `…http_code_agrees…`, P1 |
| **CTRL** | ⚠️ **CONTROL — one added comma in RS-20's prose, no semantic change** | RS-20 prose | ✅ **SURVIVED** | ✅ **SURVIVED** | — *(required)* |

**Kill rate: 11 / 18 → 16 / 18. THE CONTROL SURVIVED BOTH RUNS, so both runs are valid.**

---

## 3. What the two paired mutants prove, which a single mutant cannot

Two mutants in this set exist **only** to make a survival mean something. Each is a
corruption paired with the *identical* corruption applied one row over, where the only difference
is which side of a boundary the row happens to sit on.

| Pair | The corruption | Difference between the two | Result |
|---|---|---|---|
| **M-24 / M-25** | flip a `[Razorpay-defined]` tag to `[merchant-policy, author-chosen]` in the registry | **membership of a five-entry dict.** `test_c1_fix_probes.A4_KEYS` holds five keys and partitions them on *exactly one* Razorpay-tagged entry, so the sixth key could not be added without turning that probe red | **M-24 SURVIVED, M-25 KILLED.** The tag machinery works; the sixth key was outside it |
| **M-26 / M-27** | rewrite a documented `400` to `409` **inside the row's own verbatim quote** | **the written form of the code line.** `> **code:** 400` (RS-22/23/24) versus `> * code: 400` (everywhere else). §0 property 3's regex is `` code:\s*`?([1-5]\d{2})`?`` run on the **raw** line, and cannot cross the `**` | **M-26 SURVIVED, M-27 KILLED.** §0's property-3 kill is real for 37 rows and absent on 3 |

⚠️ **M-26's three rows are the ones `REVIEW_C1_1.md` named as the most dangerous in the file.**
RS-22 and RS-23 are the near-identical concurrency rows, and **M-12 — which attempt 1 called *"the
worst"*** — is the swap between them. The module already knows the bold form: `**code:**` is in its
own `ADDED_FIELD_LABELS` and `_payload()` strips it. Property 3 simply does not route through
`_payload()`. **`OF-40`.**

---

## 4. The three survivors, and what they have in common

**M-02, M-06 and M-23 all survive, and all three are PROSE** — not a verbatim `>` quote, not a
`config/` value, not a registry or §8.6 tag. That is the whole of the residual gap, and it is worth
stating as a property rather than as three anecdotes:

> **After this review, `RAZORPAY_SEMANTICS.md`'s verbatim quotes, `config/`'s values, and every A4
> tag in all three of its places are guarded by an executable check. Its PROSE is not.**

And the prose is where the rest of this review's findings live: the misaimed cross-references
(`OF-42`), §0's `300` (`OF-39`), §10's derivation (`OF-43`), *"three orders of magnitude"*
(`OF-45`). **M-23 is the sharpest of the three** — it rewrites RS-16's derivation to *exactly* the
10× reading that Q-029 was raised about, cost a declared STOP and a Class A ruling, and `config/`
would still hold the right number while the artefact explained the wrong one.

⚠️ **§0 declares only M-06 and M-12 as *"caught by nothing"*.** M-12 now dies to P1; **M-02 and
M-23 survive and are named in no artefact.** `OF-46`.

---

## 5. What P1 bought, stated precisely so it is not read as more than it is

`P1` pins the SHA-256 of the newline-joined sequence of every line beginning with `>` from §1
onward to **`04b453c9123ff002e1350b7dffa71a780efa41086ebb16ad013de51444108f5c`**, its value at
`55f1f2c` — the oracle's first and only content commit.

**It kills four mutants that nothing killed before** (M-12, M-22, M-26, and it doubles up on M-19
and M-21) because all four edit bytes inside a `>` block. **It kills none of the three survivors**,
because none of them touches a `>` block. That is the correct boundary and it is why the probe is
worth having *and* why it does not close `OF-15`:

- **What P1 proves:** the quotes are the same bytes they were at `55f1f2c`.
- **What P1 does NOT prove:** that those bytes are Razorpay's. **Only a fetch proves that**, and
  this review performed one — see `docs/reviews/independent/c1_review2_verbatim_check.md`, where
  **301 of 301** quoted lines matched, **source-bound**, against pages re-fetched 2026-08-31T15:22Z
  whose digests are identical to C1's. **P1 freezes that result; it does not re-derive it.**

`OF-15`'s open remainder is unchanged in kind — the ten bodies are still not vendored — but its
practical severity drops sharply, because the corruption channel it worried about now has an alarm.

---

## 6. Reproduction

Harness: `mutate.py`, written to the session scratchpad and **deliberately not committed** — it is
throwaway tooling under `CLAUDE.md` §4 (*"Throwaway work goes to a fresh OS temp directory, never
into the repository"*). Every mutation is a single anchored string replacement whose anchor is
asserted to occur **exactly once** in the target file, or in exactly one row block where the line
itself is not file-unique (M-26, M-27); the harness `SKIP`s rather than guessing, and it did skip
twice during construction, which is how two bad anchors were found.

```
python mutate.py <clone> <base-sha>
```
