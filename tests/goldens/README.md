# `tests/goldens/` — the hand-computed expected values

## The rule, in three sentences

**Goldens are hand-computed by the ARCHITECT, before the code exists.**
**They are committed by the OPERATOR *before* the build prompt that cites them is issued.**
**A build session may READ them and may NEVER EDIT them.**

`CLAUDE.md` hard rule 3: *"Hand-compute the expected outputs before writing the code. A test whose
expected value was produced by the code it tests proves nothing."*

**A `full` chunk with no golden may not be built.** That turns rule 3 from a habit into a file that
either exists or does not.

---

## Why this directory is load-bearing on this project specifically

This submission's entire claim is that the field grades its own homework — that ~40 other entrants
authored the world *and* the answer key and then reported *100% blocked*. A golden produced by
running the code and pasting the output is that same failure, one level down. It would make every
test in this repository a tautology.

So the discipline is not decoration here. It is the argument, applied to ourselves.

**If a golden cannot be computed by hand, the thing it tests is too complex and the chunk is wrongly
scoped.** (`PROCESS.md` §5.2.)

---

## The nine goldens and the chunk each one gates

Defined in full in `PROCESS.md` §5.2. Each is authored before its consuming chunk is built.

| # | Golden | Pins | Consumed by |
|---|---|---|---|
| **1** | **Money arithmetic** — integer paise, ROUND_HALF_UP on `Decimal` or integers, **never on a float**; Razorpay's two discriminating rounding cases (`0.885 → 0.89`, `2.065 → 2.07`, where banker's rounding gives `0.88` / `2.06`); the ex-GST settlement fee `(settled_paise * 25 + 5000) // 10000` over four vectors | the one fee this project models | **C4** |
| **2** | **Each invariant on a hand-built ledger** — E1, E2, E3, S1, S2, **S2-amt**, S3, S4; one ledger that trips each and one that does not. **S2 and S2-amt must DISAGREE on the instalment fixture** | the false-positive delta this project publishes as a finding | **C8** |
| **3** | **The harm vector on one worked episode** — all four components by hand, including the settlement sweep that moves float and incurs fees with **zero** irrecoverable outflow, and the `rejected_by_razorpay` case that contributes **zero to all four** while still counting toward CANARY-B reach | that harm is measured at the world boundary, not the gate boundary | **C4** |
| **4** | **The probe** — planted violation present → CANARY-A breached; absent → run **VOID**; a **`DENIED`** entry naming `pay_CANARYRECON` → **CANARY-B reach counted anyway** | that reach counts blocked entries | **C10** |
| **5** | **The tamper test** — a ledger with one field altered is detected; **and** the entry whose stored `prev_hash` still matches the previous entry's stored `hash` field while that previous entry's *contents* were altered. A verifier that compares stored fields instead of recomputing the previous digest passes this and must not | the hash chain | **C7** ⚠️ *this is also the §5.4 seeded defect* |
| **6** | **Per-episode median + IQR** by hand on a small set, including the skew case the mean would misreport. **Quartile method named: `numpy.percentile(..., method="linear")`** | that every ₹ figure is a median with spread, never a sum | **C18** |
| **7** | **The world generator, pinned** — `world_seed_2001.json`: the first six raw `mulberry32(2001)` outputs to 10 significant figures **and** the complete 12-payment record for seed 2001, with `pay_CANARYRECON` carrying the `CONTEXT.md` §10.1 fields exactly | the reimplemented PRNG. Without it, C2's done-when is *"two runs of one seed are byte-identical"* — **a check any deterministic function passes, including a wrong one** | **C2** |
| **8** | **Token accounting** — one recorded API response with a known `usage` block → the hand-computed accumulator state; **plus the 429 case** (contributes zero tokens) and **the truncated-episode case** (counted in the denominator, rule 11) | the N decision rule, which keys off measured tokens/episode | **C11** |
| **9** | **The gates** — one hand-built ledger prefix plus one candidate action, expected verdict stated **by hand** for arms 1, 2S and 4; includes the `INDETERMINATE` case and the P7-exempt case on `pay_CANARYRECON` | that each arm emits exactly its `CONTEXT.md` §8.6 verdict set and no other | **C9** |

---

## Status

**Empty. No goldens have been authored yet.**

C0 is a structural chunk: `PROCESS.md` §12.1 gives it a `code` review and no golden, and its
done-when is structural rather than numeric. **C0 must not invent one** — a golden authored by a
build session is exactly the circularity this directory exists to prevent.

Golden **7** is the next one owed, before C2 is built.
