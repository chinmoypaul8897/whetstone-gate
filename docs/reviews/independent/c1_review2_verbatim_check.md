# `c1_review2_verbatim_check.md` — the check §0 says cannot be run offline, run

**`SESSION-TOKEN: df238be6`** · C1 ADVERSARIAL RE-REVIEW, attempt 2 · 2026-08-31
**Token spend: ZERO provider model calls.** 22 HTTP GETs to public documentation and to
`raw.githubusercontent.com`, permitted and required by `PROCESS.md` §11a.

---

## Why this file exists

`RAZORPAY_SEMANTICS.md` §0 publishes a re-runnable check and then, honestly, records that most of
it cannot run: *"the ten fetched pages and two pinned source trees … this repository does not vendor
them"*, so **297 of the 301 non-empty quoted lines cannot have their bytes checked offline**
(`OF-15`, open).

**A review is not offline.** This session fetched all twelve sources and ran the check §0 describes,
in full and **source-bound** — every quoted line required to occur as a contiguous substring of *the
source the row carrying it names in its own `Source` field*, and of no other.

---

## 1. Result

```
SOURCE-BOUND VERBATIM CHECK   (bodies re-fetched 2026-08-31T15:22Z)
  '>' lines in scope (§1 onward)            : 304
  quote-internal blanks                     : 3
  non-empty payload lines                   : 301
  MATCHED against the source the row cites  : 301 / 301
  UNMATCHED                                 : 0
  per source: S1 69 · S2 63 · S3 25 · S4 84 · S5 7 · S6 1 · S7 19 · S8 18 ·
              S11 9 · S12 2 · CONTEXT.md 4
```

⚠️ **301 of 301, source-bound. §0's published verdict reproduces exactly, and it reproduces under
the STRONGER reading** — attempt 1 ran the substring half globally (any source); this run binds each
line to the one source its row cites, which is the change `F-R6(i)` demanded and which §0's
implementation can only do structurally offline.

**Reduction rules are §0's own**, reproduced rather than reinvented: strip the leading `>`, strip the
**four** added field labels `**error:** / **code:** / **description:** / **solution:**`, strip one
layer of wrapping backticks, drop empty remainders and count them separately. Comparison is
whitespace-normalised on both sides (`re.sub(r"\s+", " ", …)`), because the file wraps at 100 columns
and the sources do not.

⚠️ **One parser detail, recorded because it is a real limit of the SHIPPED check and not only of
this one.** A first pass resolved each row's `Source` from the **first** `**Source**` field in the
row body — which is what `tests/test_c1_semantics_check.py::_declared_sources` does — and reported
**3 unmatched**, all in **RS-12**. RS-12 carries **two** `Source` fields (S12 for part (i), S11 for
part (ii)), and the three lines are part (ii)'s Go snippet, which is in `refunds.go` (S11) and not in
`payment.go` (S12). Resolving per **quote block** instead of per **row** matched all three. **No
defect in RS-12** — both of its `Source` fields are correct and correctly placed. The finding is that
offline source-binding is **per-row**, and RS-12 is the row where per-row and per-block differ.

## 2. The re-fetch — every URL, digest then and now

Fetched with `curl -s -L`, 2026-08-31T15:22Z. **C1's original fetch was 2026-08-30T20:42–20:49Z**,
so this is **~18h40m later**, and it is the **third** independent fetch of these pages (C1 BUILD,
attempt 1's reviewer, this session).

| # | URL | HTTP | Bytes then / now | SHA-256 recorded in §1 | now | |
|---|---|---|---|---|---|---|
| **S1** | `…/api/payments/capture.md` | 200 | 15,396 / **15396** | `ddbca672…6ed1d9` | **identical** | ✅ |
| **S2** | `…/api/refunds/create-normal.md` | 200 | 14,596 / **14596** | `517e32ac…b356569` | **identical** | ✅ |
| **S3** | `…/api/refunds/normal-refunds-idempotent.md` | 200 | 10,846 / **10846** | `95fa561c…c2070a9b` | **identical** | ✅ |
| **S4** | `…/api/settlements/instant/create.md` | 200 | 18,159 / **18159** | `95776ebd…dd98cccd` | **identical** | ✅ |
| **S5** | `…/payments/settlements/instant.md` | 200 | 5,788 / **5788** | `4d2a0558…5d9d4d08` | **identical** | ✅ |
| **S6** | `…/payments/refunds.md` | 200 | 4,834 / **4834** | `65f32df2…2478c19e` | **identical** | ✅ |
| **S7** | `…/api/payments/fetch-all-payments.md` | 200 | 10,123 / **10123** | `9e7f6d97…02772bf93` | **identical** | ✅ |
| **S8** | `…/api/payments/fetch-with-id.md` | 200 | 12,613 / **12613** | `38f97247…d205790c` | **identical** | ✅ |
| **S9** | `…/payments/settlements/faqs.md` | 200 | 20,378 / **20378** | `4ccfaa94…923b80de5` | **identical** | ✅ |
| **S10** | `razorpay.com/capital/instant-settlements/` | 200 | 109,181 / **109181** | *(none recorded)* | `e3c4ef75…fd77f481` — **identical to attempt 1's** | ✅ |
| **S11** | `razorpay-mcp-server@7950d51d…849f : pkg/razorpay/refunds.go` | 200 | — / **10875** | `d483495c…56d3f26f` | **identical** | ✅ |
| **S12** | `razorpay-go@v1.4.0 : resources/payment.go` | 200 | 7,793 / **7793** | *(attempt 1: `0279e086…89b58`)* | **identical** | ✅ |

**Also fetched at the pinned SHA:** `pkg/razorpay/settlements.go` (12,136 bytes,
`d6a5579b…e18b06f3`) and `go.mod` (1,583 bytes, `fcfff81f…4033cf7d`).

**Both claimed-404 URLs** → **404**, each with a **135,098-byte** SPA shell, digest
`73e38354…9e0923bc` — the 404-shape control reproduces exactly, so a `200` on this host remains
evidence of a page. **All six discovery URLs** → **200**.

⚠️ **ZERO DRIFT, on the third consecutive independent fetch.** Nothing to record as a change to the
world, in either direction.

## 3. The two figures that had to be checked at source, not in the repository

### 3.1 ₹5 Cr — the column, which could have made the value wrong by 10×

RS-16 quotes S5's comparison table as `Maximum amount per settlement | ₹5 Crores | ₹50 Crores |` and
then asserts, **in author prose rather than in the quote**, that *"the `₹5 Crores` cell is Instant
Settlement and the `₹50 Crores` cell is Smart Settlements."* The quote does **not** carry the header
row, so the column attribution is not itself quoted. **If it were reversed the configured value would
be wrong by 10× and every downstream artefact would carry it.** Checked at source:

```
S5, lines 45-55:
    Feature| Instant Settlement | Smart Settlements |
     ---
    Minimum amount per settlement | ₹100 | ₹5 Lakhs |
     ---
    Maximum amount per settlement | ₹5 Crores | ₹50 Crores |
```

✅ **RS-16's attribution is CORRECT.** ₹5 Crores is the Instant Settlement column. Corroborated twice
more on the same page: *"Settle amounts **up to ₹5 Crores** through **Instant Settlement**"*, and
*"Benefits of Smart Settlements … between ₹5 Lakhs to up to ₹50 Crores"*. It also confirms the C1 FIX
session's diagnosis of the 10× annotation defect — the ₹50 Crores cell is one column to the right —
at the weight the ruling left it: *"a diagnosis to test, not a finding."*

### 3.2 ₹2,00,000 — Razorpay's own figure, and the boundary its two halves disagree on

✅ Razorpay **publishes the figure itself**; it is not an author conversion from *"2 Lacs"*. RS-17's
own `solution` line reads *"Either lower the `amount` to **₹ 2,00,000 or below**"*. `[Razorpay-defined]`
is right.

⚠️ **And the two halves of that same verbatim quote disagree about the boundary** — see `OF-44`. The
error string says *"an amount **less than** 2 Lacs"* (₹2,00,000 exactly is **refused**); the solution
says *"₹ 2,00,000 **or below**"* (₹2,00,000 exactly is **accepted**). Both are Razorpay's, both
re-fetched today, both byte-identical.

### 3.3 Inline third-party quotes — the ones §0's `>` check does not cover

§0's convention governs `>` blocks. These rows also quote sources **inline, in prose**, where no
check reaches. All verified at source by this session:

| Quote | Cited | At source | |
|---|---|---|---|
| *"We have introduced the limits on Instant Settlements to make the settlement process more predictable for your daily needs"* | S9 | 1 hit | ✅ |
| *"IMPS channel has an upper limit of ₹5 Lakhs per transaction"* | S5 | 1 hit | ✅ |
| *"`24*7`"* / *"`Holidays: None`"* | S5 | 1 hit each | ✅ |
| *"You can check the Dashboard for latest updates on the limits"* | S5 | 1 hit | ✅ |

## 4. The `>`-sequence, across the whole span

Computed at every commit that has ever touched `RAZORPAY_SEMANTICS.md`:

| Commit | total lines | `>` whole file | `>` §1 onward | non-empty | SHA-256 of the §1-onward sequence |
|---|---|---|---|---|---|
| `55f1f2c` *(the oracle's only content commit)* | 1403 | 313 | **304** | **301** | `04b453c9…44108f5c` |
| `62c4f89` | 1507 | 313 | **304** | **301** | `04b453c9…44108f5c` |
| `3b35e85` | 1594 | **316** | **304** | **301** | `04b453c9…44108f5c` |
| `32dfb7f` | 1620 | 316 | **304** | **301** | `04b453c9…44108f5c` |
| **HEAD** | 1620 | 316 | **304** | **301** | `04b453c9…44108f5c` |

⚠️ **IDENTICAL AT EVERY COMMIT, from the file's origin to HEAD.** The claim both the fix session and
the Q-029 session made is **true, and true more broadly than either checked** — each verified only
its own commit pair.

**The whole-file count moved 313 → 316 at `3b35e85`**, which is the C1 FIX session rewriting §0's own
check block — and §0's scope sentence excludes exactly that (*"Counted over §1 onward — this check's
own description block above is excluded, since it quotes nothing"*). ⚠️ **So the two published counts
are both right and they are counting different things:** the fix session's *"313 … identical"* and
the arch session's *"316 … identical"* are consistent with each other and with this table. **Not one
character of any verbatim Razorpay quote has been altered at any point in this chunk's history.**

This hash is now pinned in `tests/test_c1_review_2_probes.py::test_p1_…`, so it is checked on every
`make test` rather than at the whim of a reviewer with a network connection.

## 5. What this file does NOT establish

1. **It is documentation against documentation.** No Razorpay API call was made. Where Razorpay's
   docs are wrong, the oracle is wrong with them — unchanged from attempt 1 §8(2).
2. **It checks bytes, not labels.** The `MUST-FIRE` / `MUST-HOLD` / `RECORDED` split is **ours**, §0
   says so, and this run does not re-derive it. Attempt 1 assessed it for internal consistency and
   for whether each `RECORDED` exclusion is honest; that assessment is not repeated here.
3. **It checks `>` blocks and the four inline quotes in §3.3.** Prose is not covered by any check —
   which is exactly what three surviving mutants demonstrate (`c1_mutants.md` §4).
4. **`S9` and `S10` contribute no `>` lines** under this parse, and that is correct rather than a
   miss: RS-49's S10 quote is a **table of five individually-verbatim text nodes**, one of §0's three
   declared exceptions, and S9 is cited only inline (§3.3 above).
