# C2 REVIEW 1 — PHASE 1 (BLIND)

**Session** `94116fe2` · **2026-08-31** · **REVIEW session, not the session that built C2.**

This file, `c2_reimpl.py`, `c2_vectors.py` and `c2_reimpl_expected.json` are committed **before
phase 2 opens anything under `src/whetstone_gate/world/`**, so nothing below can have been
back-fitted to the code it is about to be diffed against.

## 1. What was read, and what was not

**Read:** `CLAUDE.md`; `docs/personas/persona_1_evaluation_integrity.md`;
`docs/personas/persona_2_code.md`; `PROCESS.md` §5.1, §5.2 (golden 7), §12.1's C2 row;
`CONTEXT.md` §8.6 and §8.6a in full, §10.1; `QUESTIONS.md` Q-019 and Q-023;
`tests/goldens/world_seed_2001.json`.

**NOT opened, and `git log`/`git diff` not consulted for them:** `src/whetstone_gate/world/`,
`tests/test_c2_world.py`, `PROGRESS.md`, `INCIDENTS.md`, `docs/sessions/c2-build-1.txt`,
`docs/sessions/arch-worldgen-1.txt`, the C2 diff.

## 2. The reimplementation

`c2_reimpl.py` — **standard library only; it imports nothing from `src/`, nothing from `config/`
and nothing from `tests/`.** Every constant in it is transcribed from the specification with its
citation beside it. A reimplementation that read its constants from `config/` would be checking the
build against itself, which is the failure mode hard rule 3 exists to prevent.

The four PRNG lines are a direct transcription of §8.6a's block. Python's `>>` on a non-negative
`int` is a logical shift and every intermediate is masked to 32 bits, so `>>` is a faithful `>>>`;
every `*` is followed by `& 0xFFFFFFFF`, which is §8.6a's *"every product is mod 2^32 (JS
`Math.imul`)"*.

Two deliberate choices, recorded because they are judgement calls a different implementer could
have made differently:

1. **Every arithmetic step is issued against an explicit local `Context(prec=50)`** —
   `ctx.divide`, `ctx.ln`, `ctx.subtract`, `ctx.multiply`, `ctx.add`, `ctx.exp` — rather than with
   bare operators. §8.6a says *"all in `context`"*, and a bare operator silently uses the ambient
   thread context instead. This is checked against the build in phase 2f.
2. **`quantize` is written exactly as §8.6a's pseudo-code writes it** —
   `amount.quantize(Decimal(1), rounding=ROUND_HALF_UP)` — with no `context=` argument, because
   that is what the specification says. Its exposure to the ambient context is a phase-2f question,
   not something to silently "fix" in a reimplementation whose only job is to be faithful.

## 3. THE THREE-WAY `mulberry32` CHECK — the most valuable finding available here, and it is not one

This is the **third** independent implementation of `mulberry32` in this project: the architect's
(cross-checked two ways, per Q-019), C2 BUILD's, and this one. A divergence would have invalidated
every number the project publishes downstream.

**There is no divergence.** Against `tests/goldens/world_seed_2001.json`, computed by this session's
code alone:

| Checked | Result |
|---|---|
| the **eleven** raw `mulberry32(2001)` outputs | **identical, all 11** |
| `u_first_six_10sf`, rendered `%.10g` | **identical, all 6** |
| `merchant_available_balance_paise` | **identical** — 50,000,000 |
| the twelve payment records, **field for field, positionally** | **identical, all 12 × 9 fields** |
| golden 7 sha256, observed here | `649e54ca446e8308f5fcd69ebba56eda5faea8d58246be7277cdb8b42227dd2b` |
| golden 7 byte count, observed here | **4,879** |

Both match Q-019's recorded values exactly.

⚠️ **A note on `u_first_six_10sf`'s first entry.** The golden prints `"0.120760706"` — nine digits,
where the other five print ten. That is **not** an inconsistency: `%.10g` strips a trailing zero,
and `518663283 / 2^32 = 0.1207607060…`. The rendering is right and this session reproduces it
character for character.

## 4. AN ORACLE FOR THE AMOUNT FORMULA THAT USES NO TRANSCENDENTAL FUNCTION AT ALL

Reproducing golden 7 shows two implementations agree. It does **not** show the *formula* is right —
two faithful transcriptions of a wrong formula agree too. Two of this session's vectors have
closed forms, which gives an oracle built from integer root extraction and nothing else:

* `u = 1/2` (raw `2^31`) ⟹ `50000 · 300^(1/2) = √750000000000`.
  `math.isqrt(750000000000 · 10^60)` = `866025403784438646763723170752936183`.
  This session's `Decimal` `exp(ln(lo) + u·(ln(hi) − ln(lo)))` = `866025.403784438646763723170752936183471`.
  **Identical to all 36 significant figures the integer oracle carries.**
* `u = 1/4` (raw `2^30`) ⟹ `(50000⁴ · 300)^(1/4)`. Integer 4th root =
  `208089572514390860666454254133578723`; this session's value =
  `208089.572514390860666454254133578723638`. **Identical to all 36 significant figures.**

So the log-uniform formula itself — not merely its transcription — is confirmed against arithmetic
that contains no `exp`, no `ln`, and no float.

## 5. The boundaries §8.6a names

| §8.6a's words | Vector | Computed here |
|---|---|---|
| *"`u = 0` gives exactly 50000"* | raw `0` | `50000.000000000000000000000000` → **50000** ✔ |
| *"`u → 1` gives exactly 15000000"* | raw `4294967295` | `14999999.980079769840689216264` → **15000000** ✔ |

Both hold. The second is worth stating precisely: the unrounded value is **0.0199 paise below**
15,000,000 and reaches it *by rounding*, not by arithmetic identity — so the claim is true as
written but is a rounding property, not an exactness property. Recorded, not raised: §8.6a says
*"Boundary behaviour, asserted by golden 7"*, and what golden 7 asserts is the rounded integer.

## 6. ⚠️ A CONSEQUENCE THAT DECIDES HOW TWO MUTANTS MUST BE JUDGED

**No reachable input can produce an exact `.5` tie, so `ROUND_HALF_UP` is unfalsifiable by value.**

The amount is `exp()` at `prec=50`; an amount with 6–8 integer digits therefore carries 42–44
fractional digits, and an exact tie needs every digit after the `5` to be zero. Across a search of
all integer amounts in `[50000, 15000000]` for the raw draw landing closest to a boundary, the
closest approach reachable is:

| raw | unrounded amount | distance from the boundary | HALF_UP gives |
|---|---|---|---|
| `2949329170` | `2511856.4999999998765810256667` | 1.23 × 10⁻¹⁰ paise **below** | 2511856 |
| `1894840345` | `619182.49999999987192885567587` | 1.28 × 10⁻¹⁰ paise **below** | 619182 |
| `3763271754` | `7403481.5000000016343574003343` | 1.63 × 10⁻⁹ paise **above** | 7403482 |

Therefore **`ROUND_HALF_UP → ROUND_HALF_EVEN` and `ROUND_HALF_UP → ROUND_HALF_DOWN` move no value
this world can ever produce.** They are value-invisible mutations of a §8.6-table constant
(*"money rounding mode … ROUND_HALF_UP"*), and **only a structural check can kill them** — exactly
the class C2 BUILD itself found with `ast.Div`, whose siblings this review was told to hunt. Both
are carried into phase 2's mutation set for that reason.

This is stated here, in the blind phase, so that if they survive it cannot be said the standard was
invented after seeing the result.

## 7. Q-023's measurement, re-derived blind

§8.6a and Q-023 state the closest approach to a rounding boundary over the 660 draws as
**0.0011866860605438627855977872 paise**, at **seed 2046, draw index 3**, raw `4167386882`, amount
`12662203.498813313939…`.

Computed here from raw `4167386882` alone: amount
`12662203.498813313939456137214402212766418196233083`, distance to the boundary
`0.0011866860605438627855977872` — **character-identical to the specification's figure.** The full
660-draw re-derivation, the ULP conversion and the float-reproduction claim are phase 2g.

## 8. The vectors

Thirty-one, in `c2_vectors.py`, with their expected values in `c2_reimpl_expected.json`: sixteen
raw-draw vectors and fifteen whole-seed vectors, plus two out-of-domain probes reported separately
because §8.6's seed list does not define them and inventing a requirement for them would be
manufacturing a finding.

Every boundary the prompt names is covered: `u = 0`; `u = 2^32 − 1`; the closest constructible
half-up straddle (both sides); seeds clustering at each end (16697 — 7 of 11 draws in the bottom
decile; 32423 — 7 of 11 in the top decile; 81859 — the widest span found, carrying both a
near-floor and a near-ceiling draw); and at least one seed from each of the **scored** (2001, 2002,
2005, 2046, 2050), **ladder** (2001, 2002, 2005) and **pilot** (2101, 2110) blocks.

The cluster seeds and the straddle raws were found by this session's own searches over seeds
0–199,999 and over all integer amounts in the interval — they are not in the specification, not in
the golden, and (verified in phase 2, since `tests/` is closed in phase 1) not in `tests/`.

## 9. Phase 1 verdict

**The blind derivation diverges from golden 7 on nothing.** The amount formula is independently
confirmed against an integer-root oracle. The remaining questions — whether *C2's code* agrees with
this, whether the probe's P7 tag matches exactly one payment in all sixty seeds, whether the four
non-uses are asserted at the scope C2 claims, and whether the structural scan kills the
value-invisible mutants — are phase 2's.
