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

⚠️ **Note on OF-01's provenance.** This file's header says *"Appended by every review."* OF-01 was
raised by a **BUILD** session (C0-COMPLETION), from an adversarial re-check of its own change, before
any review has run. It is recorded here rather than held back because the alternative is a known gap
living only in a session report. **`Raised by` says so plainly instead of borrowing a review's name.**

| ID | Chunk | Severity | Finding | Spec citation | Raised by | Status | Closed by (SHA) |
|---|---|---|---|---|---|---|---|
| **OF-01** | C0 | **MEDIUM** | **A lone CR is invisible to both `check-roles` A3 and A4.** A single stray CR (not followed by LF) makes git classify an otherwise-textual file `-text`, so it lands in the binary bucket: A3 does not scan it, and A4 cannot fail on it because git converts nothing on `-text` content. **Reproduced:** a markdown file whose only defect is one lone CR eating a sentence reports `i/-text w/-text`, contains no CRLF pair, and **passes both checks.** ⚠️ **Not a regression** — the pre-`1be73e4` A3 searched for CRLF *pairs* and missed a lone CR too — **but it is INC-06's and INC-10's exact defect class, and INC-10 was caught only because that CR happened to be followed by LF.** Under a lone CR the repository would have gone green over corrupted prose. **Proposed fix, not applied:** a new check asserting *"no tracked file is classified `-text` while containing no NUL byte"* — a narrow discriminator that flags a file made binary by CR statistics alone, and that passes both dashboard PNGs (they carry NULs in `IHDR`). Needs a new check and a mutation test, i.e. new scope. | `PROCESS.md` §6a; `CLAUDE.md` hard rule 6; INC-06, INC-09, INC-10 | **C0-COMPLETION BUILD** (not a review — see the note above) | **OPEN** | — |
