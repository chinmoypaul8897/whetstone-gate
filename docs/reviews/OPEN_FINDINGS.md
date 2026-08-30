# OPEN_FINDINGS.md — findings a review could not close

**Appended by every review. Closed only explicitly, with the SHA that closed it.**

This file exists so that MEDIUM and LOW findings cannot accumulate silently underneath a wall of
PASS verdicts (`PROCESS.md` §2, §12.2). A review may PASS a chunk with open MEDIUMs and LOWs; it may
**not** PASS with an open BLOCKER, and a BLOCKER therefore never appears here as "open".

**C19's done-when:** this file is **empty, or every remaining item is explicitly accepted with a
reason.** An item that is neither closed nor accepted blocks the README chunk.

---

## Format

One row per finding. Never delete a row — closing a finding means filling in its last two columns.

| ID | Chunk | Severity | Finding | Spec citation | Raised by | Status | Closed by (SHA) |
|---|---|---|---|---|---|---|---|

- **ID** — `OF-NN`, allocated in order, never reused.
- **Severity** — `MEDIUM` or `LOW` only. (`INFO` is recorded in the review file, not here.)
- **Raised by** — `REVIEW_<N>_<attempt>.md`.
- **Status** — `OPEN` · `CLOSED` · `ACCEPTED` (accepted requires a stated reason in the row).

---

## Findings

*(No entries. Nothing has been reviewed yet: C0 is the first chunk and its review has not run.)*
