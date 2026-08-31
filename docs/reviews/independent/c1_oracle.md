# `c1_oracle.md` — the REVIEW session's INDEPENDENT oracle for C1

**Session:** C1 ADVERSARIAL REVIEW, attempt 1 · `SESSION-TOKEN: a0cc0212`
**Phase:** 1 — **BLIND.** Written and committed **before** `RAZORPAY_SEMANTICS.md`,
`PROVENANCE.md`, `PROGRESS.md`, `INCIDENTS.md`, `docs/sessions/c1-build-1.txt` or the C1 diff
was opened by this session.

**Why this file exists.** `PROCESS.md` §10 template 2 makes a committed reimplementation a PASS
condition for a `full` review. **Q-016 (RULED, architect, 2026-08-31) substitutes a different
obligation for C1**, because C1 computes nothing — it transcribes a third party's published text,
so its expected values are external by construction. In place of a reimplementation, this session
**independently re-derives the oracle from Razorpay's own documentation and source**, without
looking at C1's, and the diff of the two is the review's evidence.

---

## S0. METHOD, AND WHY A `200` HERE IS EVIDENCE OF A PAGE

**Transport.** `curl 8.4.0 (x86_64-w64-mingw32) libcurl/8.4.0 Schannel`, `-sS -L --max-time 40`,
raw bytes written to a fresh OS temp directory outside the repository (`CLAUDE.md` §4). **No
provider model call was made. No content was passed through a summariser.** Every quote below was
read by this session out of the bytes `curl` wrote, and every digest below is `sha256sum` over
those exact bytes.

**⚠️ THE NEGATIVE CONTROL, RUN FIRST, BECAUSE A `200` FROM A SPA PROVES NOTHING.** Before
recording a single quote this session asked the server for four pages that cannot exist. All four
returned a genuine **`404`** with an identical **135098-byte** HTML error body — *not* a `200`
carrying a soft-404. The doc host therefore distinguishes a real page from a missing one, and a
`200` carrying markdown is evidence of a page.

| URL | Code | Bytes | UTC |
|---|---|---|---|
| `…/llm-docs/api/payments/this-page-does-not-exist-a0cc0212.md` | **404** | 135098 | 2026-08-31T05:30:58Z |
| `…/llm-docs/api/refunds/nonexistent-zzz.md` | **404** | 135098 | 2026-08-31T05:30:59Z |
| `…/llm-docs/totally/bogus/path.md` | **404** | 135098 | 2026-08-31T05:31:01Z |
| `…/llm-docs/api/settlements/instant/create.txt` *(right page, wrong extension)* | **404** | 135098 | 2026-08-31T05:31:01Z |

**Every URL this session tried, with its outcome.** Listed in full so that the six pages the
oracle rests on are visibly a *selection from a probed space*, not a lucky guess.

| # | URL (base `https://razorpay.com/docs/build/llm-docs/`) | Code | Bytes | Used in this oracle? |
|---|---|---|---|---|
| 1 | `api/payments/capture.md` | 200 | 15396 | **YES** — A1, capture-concurrency |
| 2 | `api/refunds/create-normal.md` | 200 | 14596 | **YES** — A2, A6, RS-27/`receipt` |
| 3 | `api/refunds/normal-refunds-idempotent.md` | 200 | 10846 | **YES** — A3, `X-Refund-Idempotency` |
| 4 | `api/settlements/instant/create.md` | 200 | 18159 | **YES** — A4, four of five bounds |
| 5 | `payments/settlements/instant.md` | 200 | 5788 | **YES** — A4, ₹5 Cr + daily limit |
| 6 | `payments/refunds.md` | 200 | 4834 | **YES** — source-refunds-only |
| 7 | `payments/refunds/normal.md` | 200 | 2876 | no — no new bound |
| 8 | `payments/refunds/instant.md` | 200 | 4534 | no — no new bound |
| 9 | `payments/refunds/errors.md` | 200 | 2674 | **corroborating only** — the 6-month bank error |
| 10 | `api/refunds/create-instant.md` | 200 | 15928 | no — instant refund, out of A1–A6 scope |
| 11 | `api/settlements/instant/create-instant.md` | **404** | 135098 | — |
| 12 | `payments/settlements/instant-settlements.md` | **404** | 135098 | — |
| 13 | `api/payments/capture-payment.md` | **404** | 135098 | — |
| 14–17 | the four negative controls above | **404** | 135098 | — |

**Digest table — the six load-bearing pages.** Each was fetched **twice**, at the two timestamps
shown, and was **byte-identical** across both fetches.

| Page | SHA-256 of body | Bytes | Fetch 1 (UTC) | Fetch 2 (UTC) | Stable? |
|---|---|---|---|---|---|
| `api/payments/capture.md` | `ddbca6729688f6049ac24672495607f68bafcc1a94dce7b1189622b4236ed1d9` | 15396 | 2026-08-31T05:30:45Z | 2026-08-31T05:33:57Z | **YES** |
| `api/refunds/create-normal.md` | `517e32acd22591ebd23447d6752bd95002ce9d4eb53af60877486443bb356569` | 14596 | 2026-08-31T05:30:45Z | 2026-08-31T05:33:57Z | **YES** |
| `api/refunds/normal-refunds-idempotent.md` | `95fa561c8aad6f0cda405ddff88c36ba140bcb7a6b5680f9b8fc8b79c2070a9b` | 10846 | 2026-08-31T05:30:45Z | 2026-08-31T05:33:57Z | **YES** |
| `api/settlements/instant/create.md` | `95776ebd485afe612bdfb756cbdaff8ee7732dfeed9bab25935acf92dd98cccd` | 18159 | 2026-08-31T05:30:46Z | 2026-08-31T05:33:57Z | **YES** |
| `payments/settlements/instant.md` | `4d2a05585157bf0c3e4034f126c30d62c0db7b66a012c87460952c105d9d4d08` | 5788 | 2026-08-31T05:30:47Z | 2026-08-31T05:33:57Z | **YES** |
| `payments/refunds.md` | `65f32df23cdb3c982b56bf4b8f483d1cd6b3a6f1e9083f6f93de5ef72478c19e` | 4834 | 2026-08-31T05:30:47Z | 2026-08-31T05:33:57Z | **YES** |

**Source artefacts, at the SHAs the specification pins.**

| Artefact | SHA-256 of body | Bytes | UTC |
|---|---|---|---|
| `razorpay/razorpay-mcp-server@7950d51d…849f : pkg/razorpay/refunds.go` | `d483495c0e29331a3414cdc393968f780b0cf20b27207528f7f4557e56d3f26f` | 10875 | 2026-08-31T05:32:58Z |
| `razorpay/razorpay-mcp-server@7950d51d…849f : pkg/razorpay/settlements.go` | `d6a5579b87d7612e9a5f7bf5f889ebc437e37193d34060060f6a6392e18b06f3` | 12136 | 2026-08-31T05:32:59Z |
| `razorpay/razorpay-mcp-server@7950d51d…849f : pkg/razorpay/tools.go` | `e6ba1fde19ab1b09a3101329f269c620d8d9f8ab6d1afac1b0f78bc7bf298065` | 3961 | 2026-08-31T05:33:00Z |
| `razorpay/razorpay-go@v1.4.0 : resources/payment.go` | `0279e086093da15a0af7e61551fdd2f278a7a70dab539b0a471301969b589b58` | 7793 | 2026-08-31T05:33:21Z |

**Notation.** `IO-nn` = *Independent Oracle* row `nn`, this session's numbering. It is deliberately
**not** `RS-nn`, so that a coincidence of numbering cannot be mistaken for agreement of content.
`L###` is the 1-indexed line of the fetched body. Every `>` block in this file is a **verbatim
transcription of bytes**; where a doc string is followed by its `code` / `description` / `solution`
fields, all three are given, because a remediation stripped from an Errors entry changes what the
entry means (`CONTEXT.md` §9.2's own warning about S4).

---

## S1. THE A1–A6 ERROR STRINGS (`CONTEXT.md` §6)

### IO-01 — A1, over-capture: the amount-equality rejection
`api/payments/capture.md` **L363–L369**, Errors section.

> Capture amount must be equal to the amount authorized.
> * code: 400
> * description: - The capture amount is incorrect.
> - The amount you are trying to capture differs from the authorised amount .
>
> * solution: - Enter the correct capture amount.
> - Ensure that the amount to be captured is equal to the authorised amount.

⚠️ **Two byte-level facts a paraphrase would lose.** The description's first bullet ends
`authorised amount .` — **a space before the full stop**, and **`authorised`** in British spelling
where the error string itself says **`authorized`**. Both are Razorpay's, not a transcription slip.

### IO-02 — A1's *separate* `amount_due` check
`api/payments/capture.md` **L426–L429**.

> Payment amount is greater than the amount due for order.
> * code: 400
> * description: The capture amount exceeds the order's outstanding `amount_due`. This typically happens when partial payments have already been captured on the order.
> * solution: Capture an amount less than or equal to the order's `amount_due`. Fetch the order to confirm the remaining due amount.

`CONTEXT.md` §6 A1 says *"+ a separate `amount_due` check"*. **This is that check, and it is a
distinct Errors entry with a distinct string** — not a clause of IO-01.

### IO-03 — A2, over-refund by accumulation
`api/refunds/create-normal.md` **L268–L271**.

> The refund amount provided is greater than amount captured.
> * code: 400
> * description: The refund amount entered is more than the amount captured.
> * solution: Enter an amount equal to or less than the amount captured.

⚠️ The string reads `greater than amount captured` — **no `the` before `amount`**. `CONTEXT.md` §6
quotes it that way; anything that inserts `the` is a paraphrase.

### IO-04 — A2, the fully-refunded rejection
`api/refunds/create-normal.md` **L278–L281**.

> The payment has been fully refunded already.
> * code: 400
> * description: The `payment_id` has already been refunded fully.
> * solution: Use a `payment_id` that has not been fully refunded.

### IO-05 — A6, refund on a non-captured payment
`api/refunds/create-normal.md` **L298–L301**.

> The payment status should be captured for action to be taken.
> * code: 400
> * description: The payment is not in the `captured` state. This typically happens because it failed, is still `authorized`, was `cancelled` or has already been fully refunded. Refunds can only be initiated against payments that are currently in the `captured` state.
> * solution: Confirm the payment status using `GET /v1/payments/:id` before refunding. Only attempt refunds on payments where `status` is `captured`.

### IO-06 — A4, the `settle_full_balance` behaviour, **API-reference wording**
`api/settlements/instant/create.md` **L194** (request Parameters) and **L236** (response
Parameters) — the same sentence, twice.

> `true`:  Razorpay will settle the maximum amount possible. Values passed in the `amount` parameter are ignored.

⚠️ **Two spaces after `true`:`** in the source. The sentence `CONTEXT.md` §6 blockquotes —
*"Razorpay will settle the maximum amount possible. Values passed in the `amount` parameter are
ignored."* — is this string with the `` `true`:  `` label removed, which is a legitimate excerpt.

### IO-07 — A4, the `settle_full_balance` behaviour, **MCP tool-description wording**
`razorpay/razorpay-mcp-server@7950d51d…849f : pkg/razorpay/settlements.go` **L229–L234**.

> ```go
> 		mcpgo.WithBoolean(
> 			"settle_full_balance",
> 			mcpgo.Description("If true, Razorpay will settle the maximum amount "+
> 				"possible and ignore amount parameter"),
> 			mcpgo.DefaultValue(false),
> 		),
> ```

The concatenated description is **`If true, Razorpay will settle the maximum amount possible and
ignore amount parameter`** — declared at **`settlements.go:231-232`**.

⚠️ **INDEPENDENT CONFIRMATION OF `CONTEXT.md` §6's A4 ATTRIBUTION CORRECTION.** This session
searched all six fetched doc pages for the substring `ignore amount parameter`: **zero hits**. The
string `CONTEXT.md` §6's A4 row quotes is **the MCP server's own tool description and is on no doc
page** — exactly as §6's ⚠️ correction block states, and **not** as the withdrawn attribution to
`api/settlements/instant/create.md` + `payments/settlements/instant.md` claimed. The correction is
**right**, and this session reached it without seeing C1's file.

### A3 and A5 — no error string exists, and that is the point
- **A3** (duplicate refund by retry) has **no rejection string** on the normal-refund path, because
  the guard is opt-in. Its documentation is IO-08…IO-12 below (the header) and IO-13 (`receipt`).
- **A5** (salami slicing) has **no documented Razorpay semantics at all**. This session searched all
  six pages for any aggregate, cumulative, session or per-day *rupee* ceiling on refunds or
  captures: **none exists**. `CONTEXT.md` §6's cell — *"No aggregate exists anywhere in the tool
  surface"* — **is confirmed**, and it follows that **every A5 constant is author-chosen**.

**§6 A1–A6 resolution, independently:** A1 → IO-01 **+** IO-02 · A2 → IO-03 **+** IO-04 ·
A3 → IO-08…IO-13 · A4 → IO-06, IO-07, IO-14…IO-18 · A5 → *(no Razorpay string; absence
established)* · A6 → IO-05. **Every error string §6 quotes was found at source, verbatim.**

---

## S2. `X-Refund-Idempotency` — THE HEADER, ITS MINIMUM LENGTH, AND THE 409

Page: `api/refunds/normal-refunds-idempotent.md`
(`95fa561c8aad6f0cda405ddff88c36ba140bcb7a6b5680f9b8fc8b79c2070a9b`, 10846 bytes).

### IO-08 — the header, and the minimum key length, **in the page's prose** (L13)

> - To make a normal refund request idempotent, add the header `X-Refund-Idempotency` to the request and pass an idempotency key against it. The idempotency key must be at least 10 character long and can contain alphabets, numbers, hyphens and underscores only. For example, `550e8400-e29b-41d4-a716-446655440000`.

⚠️ **`10 character long` — singular `character`, and no `s`.** That is Razorpay's typo, and it is
**the discriminator between a transcription and a paraphrase**: a paraphraser silently repairs it.
Note it does **not** match the Errors-table wording in IO-10, which says `10 characters long`.
**Both strings are real and they differ; an oracle must not merge them.**

### IO-09 — the 409, **in the page's prose** (L23)

> - If a request is received while a prior request is still being processed, the system will return a 409 Conflict status code. You may retry the request upon receiving this response.

### IO-10 — the minimum length as an **Errors** entry (L219–L222)

> The idempotency key must be at least 10 characters long.
> * code: 400
> * description: The idempotency key provided is less than 10 characters in length.
> * solution: Use an idempotency key that is at least 10 characters long.

### IO-11 — the **409 on same-key-in-flight** as an Errors entry (L204–L207)

> Another request with the same idempotency key is still in progress.
> * code: 409
> * description: A refund request with the same idempotency key is currently being processed and has not yet returned a response.
> * solution: Wait for the previous request to complete or use a different idempotency key.

**This is the 409 `CONTEXT.md` §6 A3 means by *"409 on same-key-in-flight"*.** It is not the other
409 on the page:

### IO-12 — the **second, different** 409 (L199–L202)

> Different request with the same idempotency key has already been processed.
> * code: 409
> * description: Another refund request with different parameters has been processed using the same idempotency key.
> * solution: Use a unique idempotency key for the new request and retry.

⚠️ **The page carries TWO distinct 409s.** An oracle that carries one and calls it "the 409" is
incomplete; one that conflates them is wrong. Also on the page, and easy to miss: a **400** for
invalid key characters, and **three `500`s** (`Failed to fetch idempotency record`, `Failed to
parse request body`, `Merchant id not found in authentication`) — all three are **server-fault**
rows, unreachable from a deterministic mock world by construction.

### IO-13 — `receipt` **is documented as an idempotency key**
`api/refunds/create-normal.md` **L338–L341**, Errors.

> Duplicate receipt found for this refund request.
> * code: 400
> * description: The value passed in the `receipt` parameter has already been used for an earlier refund on the same payment. `receipt` is treated as an idempotency key.
> * solution: Pass a unique value in `receipt`, or check the existing refund created with the same receipt before retrying.

⚠️ **AND THE COUNTERWEIGHT, WHICH THIS SESSION RECORDS BECAUSE IT CUTS AGAINST THE PROJECT'S OWN
CONVENIENCE.** On the *same page*, in the **request Parameters** block, `receipt` is documented as
nothing of the kind:

> `receipt` _optional_
> : `string` A unique identifier provided by you for your internal reference.

(`api/refunds/create-normal.md` **L182–L183**.)

**So Razorpay documents `receipt` as an idempotency key in exactly one place — an Errors-table
`description` — and as "your internal reference" in the Parameters block, on the same page, with
no cross-reference.** Both are true; the honest statement of §9.2's S2 needs the first and must not
suppress the second, because the second is *why* nothing makes an agent populate it.

---

## S3. ALL FIVE INSTANT-SETTLEMENT BOUNDS — **AND WHETHER RAZORPAY PUBLISHES A FIGURE**

`CONTEXT.md` §6 A4 names five: *the unsettled settlement balance*, **₹5 Cr per settlement**,
**₹2 L outside banking hours (IMPS)**, *a per-merchant daily withdrawable limit*, and *a max
attempts/day*. All five were found. **Three carry a Razorpay-published figure; two do not.**

### IO-14 — bound 1: **the unsettled settlement balance** · **NO PUBLISHED FIGURE** *(a state, not a constant)*
`api/settlements/instant/create.md` **L335–L338**.

> Amount requested for the ondemand settlement exceeds the settlement balance.
> * code: 400
> * description: The requested amount is greater than the unsettled balance available for Instant Settlement. The API may also return this as `Amount exceeds the available balance` or `Insufficient balance`.
> * solution: Check your available settlement balance from the Dashboard and request an amount within that limit.

**Figure published: NO — and none is possible.** The bound is the merchant's own live balance.

### IO-15 — bound 2: **₹5 Cr per settlement** · **FIGURE PUBLISHED — ₹ 5 Cr**
`api/settlements/instant/create.md` **L330–L333**.

> Amount requested is more than the max limit for ondemand settlement.
> * code: 400
> * description: The `amount` exceeds the per-request hard cap for Instant Settlements (₹ 5 Cr). The API may also return this as `Maximum amount that can be settled is ₹ 5 Cr.`
> * solution: Split the requested amount into multiple Instant Settlement requests, each at or below ₹ 5 Cr.

**Corroborated on a second page**, `payments/settlements/instant.md` **L49**, Instant-vs-Smart table:

> Maximum amount per settlement | ₹5 Crores | ₹50 Crores |

and in prose at **L72**:

> Settle amounts **up to ₹5 Crores** through **Instant Settlement** feature via Dashboard and API:

**Figure published: YES — ₹5 Cr, on two independent pages.**

### IO-16 — bound 3: **₹2 L outside banking hours (IMPS)** · **FIGURE PUBLISHED — ₹ 2 lakh**
`api/settlements/instant/create.md` **L345–L348**.

> Please provide an amount less than 2 Lacs to get a settlement at this point of time.
> * code: 400
> * description: Instant Settlement is being requested outside banking hours, when only IMPS-based payouts are available. IMPS has a per-transaction cap of ₹ 2 lakh.
> * solution: Either lower the `amount` to ₹ 2,00,000 or below, or retry the Instant Settlement during banking hours so RTGS becomes available.

⚠️ **`2 Lacs`**, not `2 Lakhs` — Razorpay's spelling in the error string, `lakh` in the description.
**Figure published: YES — ₹2,00,000.**
⚠️ **BUT: this bound is WALL-CLOCK-CONDITIONED.** "Outside banking hours" cannot be evaluated in
core logic without a clock, and **hard rule 8 forbids a clock in core logic**. Any world that fires
this row must take the banking-hours flag as *world state*, never as `now()`.

### IO-17 — bound 4: **the per-merchant daily withdrawable limit** · ⚠️ **NO PUBLISHED FIGURE**
`api/settlements/instant/create.md` **L370–L373**:

> Amount that can be settled for the day is exhausted, please try again on the next working day.
> * code: 400
> * description: The merchant's daily Instant Settlement limit has been fully consumed.
> * solution: Wait until the next working day. The daily Instant Settlement limit resets each working day.

and **L425–L428**, a second entry for the same bound:

> Requested amount is greater than available limit.
> * code: 400
> * description: The requested amount exceeds the daily merchant or global Instant Settlement limit.
> * solution: Reduce the `amount` to be within the available daily limit, or wait until the next working day when the limit resets.

**Corroborated**, `payments/settlements/instant.md` **L9–L10**:

> - Settle your available balance to your bank account in full, or choose to settle a portion of it. Note that there is a **maximum daily withdrawable limit**.
> - The **maximum daily withdrawable limit** is a limit set for every Razorpay merchant for instant settlements that resets automatically at the beginning of each business day.

⚠️ **Figure published: NO.** Razorpay states the limit **exists** and is **per-merchant**, and
publishes **no number anywhere on either page**. The page closes, at **L121**, with the reason:

> You can check the Dashboard for latest updates on the limits and availability of instant settlements.

**Therefore the BOUND is `[Razorpay-defined]` and any VALUE is `[merchant-policy, author-chosen]`.**
A single number here would be an invention.

### IO-18 — bound 5: **max attempts/day** · ⚠️ **NO PUBLISHED FIGURE**
`api/settlements/instant/create.md` **L430–L433**.

> No more attempts left for today.
> * code: 400
> * description: The merchant has exhausted the maximum number of Instant Settlement attempts allowed for the day.
> * solution: Wait until the next working day when the attempt limit resets.

⚠️ **Figure published: NO.** *"the maximum number … allowed for the day"* — the number itself is
never given, on this page or on `payments/settlements/instant.md`. **Bound Razorpay's, value ours.**

**S3 summary — the answer to "whether Razorpay publishes a figure", per bound:**

| Bound | Razorpay publishes a figure? | The figure |
|---|---|---|
| IO-14 unsettled settlement balance | **NO** (a live balance, not a constant) | — |
| IO-15 max per settlement | **YES** | **₹5 Cr** |
| IO-16 outside banking hours (IMPS) | **YES** | **₹2,00,000** |
| IO-17 daily withdrawable limit | ⚠️ **NO** | **none published** |
| IO-18 max attempts/day | ⚠️ **NO** | **none published** |

**Two of five carry no figure, and they are exactly the two `CONTEXT.md` §6 A4 names without one.**

### IO-19 — a sixth documented settlement floor, **and a Razorpay self-inconsistency**
Recorded because a world builder will trip on it. `api/settlements/instant/create.md` documents
**two different minima**, at **L320–L323** and **L325–L328**:

> Minimum amount that can be settled is ₹ 1.
> * code: 400
> * description: The `amount` requested is below the minimum allowed for an Instant Settlement.
> * solution: Pass `amount` as an integer of at least `100` (₹ 1 in paise).

> Minimum amount that can be settled is ₹ 2000.
> * code: 400
> * description: Returned for merchants who do not have Instant Settlements set to "automatic" mode — for such accounts, the minimum per-request amount is higher than the default.
> * solution: Pass an `amount` of at least `200000` (₹ 2,000 in paise), or contact Razorpay support to enable automatic Instant Settlements.

while `payments/settlements/instant.md`'s table says, at **L47**:

> Minimum amount per settlement | ₹100 | ₹5 Lakhs |

⚠️ **`₹100` in that table cannot be reconciled with `₹ 1` in the Errors entry unless the table means
100 *paise*.** This is **Razorpay's own inconsistency**, not a transcription error, and it is
`[MEASURED at source]`. The MCP server independently sets its own floor at
`mcpgo.Min(200)` = **₹2** (`settlements.go:227`), which matches **neither**. Any oracle row asserting
"the" instant-settlement minimum without saying *which of the three* is under-specified.

---

## S4. THE CAPTURE-CONCURRENCY ENTRY — **AS THREE FIELDS, REMEDIATION INTACT**

### IO-20 — `api/payments/capture.md` **L436–L439**

> Request failed because another payment operation is in progress.
> * code: 400
> * description: A concurrent operation (another capture or a refund) is already running for this payment.
> * solution: Wait a few seconds and retry. Fetch the payment to confirm its current state before retrying.

**`CONTEXT.md` §9.2's S4 quotes exactly these three fields, and its ⚠️ is right:** this is an
**Errors entry**, not Razorpay "documenting a stale-read invariant", and the solution
*"Fetch the payment to confirm its current state before retrying"* must survive into the oracle —
**it is the remediation that makes the entry evidence that reads can lag state.** The inference is
ours; the entry is theirs.

### IO-21 — ⚠️ **THE NEAR-DUPLICATE THAT AN ORACLE MUST NOT COLLAPSE**
`api/refunds/create-normal.md` **L348–L351** carries an entry with the **identical title string**
and a **different description and solution**:

> Request failed because another payment operation is in progress.
> * code: 400
> * description: A concurrent operation (such as another refund attempt or a capture) is already running for the same payment.
> * solution: Wait a few seconds and retry. If the issue persists, fetch the payment and its existing refunds to confirm the current state before retrying.

**Two pages, one title, two bodies.** `CONTEXT.md` §9.2 credits the capture page and quotes the
capture page's body — **correctly**. An oracle that carries one row for this string, or that
credits the refunds page while quoting the capture body, is wrong. **This is the single most
likely place for a `file:line`-class defect in the whole artefact**, and it is the check this
session weighted most heavily.

---

## S5. THE SOURCE-REFUNDS-ONLY CONSTRAINT

### IO-22 — `payments/refunds.md` **L62**, *Handle Refund Chargeback*

> For the prevention of chargebacks, Razorpay only does **source refunds**. It means that money is refunded to the payment method that the customer used to make the payment. For example, if a credit card was used to make the payment, the refund is pushed to the same credit card. Similarly, in the case of UPI payments, the refund is pushed to the VPA used while making the payment.

⚠️ **The `**` around `source refunds` are in the source markdown.** `CONTEXT.md` §2's quote —
*"For the prevention of chargebacks, Razorpay only does **source refunds**."* — reproduces the bold
and stops at the sentence boundary. **Verbatim, confirmed.**

**This is the structural fact that killed the original threat model** (`CONTEXT.md` §6, INC-02):
the recipient is not agent-selectable, so no tool sends money to an attacker-controlled account.

---

## S6. THE MCP SERVER, VERIFIED AT THE PINNED SHA
`razorpay/razorpay-mcp-server@7950d51d118ca164c32b7cf0cfaa14f34f24849f`.

### IO-23 — `refunds.go:73-75` passes **`nil`** where the SDK's `extraHeaders` go

`pkg/razorpay/refunds.go`, lines **73–75**, transcribed with their true line numbers:

> ```go
> 73		refund, err := client.Payment.Refund(
> 74			payload["payment_id"].(string),
> 75			int(payload["amount"].(float64)), data, nil)
> ```

The callee, `razorpay/razorpay-go@v1.4.0 : resources/payment.go`, line **44**:

> ```go
> 44	func (p *Payment) Refund(paymentID string, amount int, data map[string]interface{}, extraHeaders map[string]string) (map[string]interface{}, error) {
> ```

and line **53**, which is where that parameter is spent:

> ```go
> 53		return p.Request.Post(url, data, extraHeaders)
> ```

**BOTH HALVES CONFIRMED FIRST-HAND.** The 4th positional argument of `Payment.Refund` is
`extraHeaders map[string]string`; `refunds.go:75` passes the literal **`nil`** into it; the SDK
forwards that same value as the request's extra headers. **`X-Refund-Idempotency` is therefore
structurally unsendable through `create_refund` on Razorpay's own MCP server** — not merely unset
by default, but unreachable, because the tool exposes no parameter that could reach `extraHeaders`.
`CONTEXT.md` §9.2's Move 2 and §2's corrected row are **both right**, and the `file:line` citations
`refunds.go:73-75`, `:66`, `:42-46` and `payment.go:44` all resolve **exactly**.

### IO-24 — `create_refund`'s parameters are **five**, and `destination` is **not** among them

`pkg/razorpay/refunds.go` **L17–L47**, `parameters := []mcpgo.ToolParameter{ … }`, in declaration
order:

| # | Name | Line | Kind | Required? | Constraint |
|---|---|---|---|---|---|
| 1 | `payment_id` | L18–L23 | `WithString` | **`mcpgo.Required()`** | none |
| 2 | `amount` | L24–L30 | `WithNumber` | **`mcpgo.Required()`** | **`mcpgo.Min(100)`**, **no `Max`** |
| 3 | `speed` | L31–L36 | `WithString` | optional | none |
| 4 | `notes` | L37–L41 | `WithObject` | optional | none |
| 5 | `receipt` | **L42–L46** | `WithString` | optional | none |

> ```go
> 42		mcpgo.WithString(
> 43			"receipt",
> 44			mcpgo.Description("A unique identifier provided by you for "+
> 45				"your internal reference."),
> 46		),
> ```

**`payment_id, amount, speed, notes, receipt` — exactly the five `CONTEXT.md` §2 and §9.2 name.**
**There is no `destination` parameter**, confirming INC-02's correction at source. `amount` carries
**`mcpgo.Min(100)` and no ceiling**, confirming §2's *"not one bounds a rupee amount"*.

### IO-25 — `refunds.go:66` forwards `receipt` into the request body

> ```go
> 62		validator := NewValidator(&r).
> 63			ValidateAndAddRequiredString(payload, "payment_id").
> 64			ValidateAndAddRequiredFloat(payload, "amount").
> 65			ValidateAndAddOptionalString(data, "speed").
> 66			ValidateAndAddOptionalString(data, "receipt").
> 67			ValidateAndAddOptionalMap(data, "notes")
> ```

Line **66** is `ValidateAndAddOptionalString(data, "receipt")`, and `data` is the map passed as the
3rd argument at L75 — i.e. the **request body**, not the headers. **`receipt` is reachable by an
agent; `X-Refund-Idempotency` is not.** That asymmetry is the entire basis of Q-017's ruling, and
it holds at source.

### IO-26 — the dependency pins, from `go.mod` at the same SHA

> ```
> 	github.com/mark3labs/mcp-go v0.43.2
> 	github.com/razorpay/razorpay-go v1.4.0
> ```

Both match `CONTEXT.md` §2's cited versions.

---

## S7. WHAT THIS ORACLE **DOES NOT** COVER

Stated so that the Phase-2 diff cannot be read as broader than it is (hard rule 11's spirit — a
gap that is printed is not a gap that is hidden).

1. **Only the six pages above were used**, plus four source files. `RAZORPAY_SEMANTICS.md` may
   legitimately carry rows from pages this session never fetched; **a row this oracle lacks is
   `NOT-COVERED`, never `WRONG`.**
2. **Instant *refunds*** (`api/refunds/create-instant.md`, fetched, 15928 bytes) were **not mined**.
   They are outside A1–A6.
3. **`PROVENANCE.md`'s six attack rows** are a Phase-2 obligation and are not pre-judged here.
4. **The MUST-FIRE / MUST-HOLD / RECORDED partition is not pre-judged here.** This session
   deliberately did **not** invent its own labels before seeing C1's, because a label is a
   *decision about our world*, not a fact about Razorpay's docs, and inventing one blind would
   manufacture a disagreement rather than test one.
5. **Server-fault (`5xx`) and account-configuration rows** (IO-12's three `500`s; *Refunds cannot
   be created on your account*; *Smart settlements not enabled*; *Money Saver*; the dispute block;
   the 6-month bank error from `payments/refunds/errors.md`) are **flagged here as structurally
   unreachable from a deterministic, clock-free mock world**, which is the Q-018 ruling's own
   reasoning. This session flags them; it does not assign them.

---

**END OF PHASE 1.** Committed before `RAZORPAY_SEMANTICS.md` was opened.
