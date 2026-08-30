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

⚠️ **`REVIEW_C0_1` returned FAIL.** Its four BLOCKERs (B-01 … B-04) are **deliberately not in this
table** — the header above says a review may not PASS with an open BLOCKER and that a BLOCKER
therefore never appears here as "open". They live in `docs/reviews/REVIEW_C0.md` §4 and are closed by
a FIX session, not carried. The MEDIUMs and LOWs below are the carried remainder.

| ID | Chunk | Severity | Finding | Spec citation | Raised by | Status | Closed by (SHA) |
|---|---|---|---|---|---|---|---|
| **OF-02** | C0 | **MEDIUM** | **12 of 19 mutants survive both `make test` and `make check-roles`.** Applied per-mutant to a clean clone and **committed** (so the dirty-tree test was satisfied — the state a real defect lives in), with a semantics-preserving control that correctly survived. Survivors include **B1 no longer detecting a tracked `.env` at all** and **the secret scanner reduced to 1 of its 8 patterns**. Cause: `tests/test_repo_invariants.py` asserts `result.ok is True` against a repository in which every check passes trivially, and only three tests in the suite build a fixture that should make a check FAIL. **Partially closed here:** `tests/test_c0_review_probes.py` (20 kept probes) takes the kill rate from **6/19 to 17/19**. The two remaining are **M15 (D3)**, deliberately left because a probe there would leave a green test standing over B-02, and **M20**, an equivalent mutant (`git rev-list --max-parents=0 HEAD` cannot return empty while HEAD resolves). Full table in `REVIEW_C0.md` F-05. | `PROCESS.md` §5.4, §12.1 (`code` = ≥4 mutants) | **REVIEW_C0_1** | **OPEN** | — |
| **OF-03** | C0 | **MEDIUM** | **`check_gitattributes`'s early return removes A2/A3/A4 from the report with no `n/a`** — a check's *absence* and a check's *pass* are again indistinguishable to a caller. Reproduced: with `.gitattributes` deleted the function returns **one** result and the summary silently prints three fewer checks. Never a false PASS (A1 fails in that branch), so it is information loss, not verdict loss. `INCIDENTS.md` **INC-07** diagnosed exactly this, fixed it in `check_secrets`, named this function as the surviving instance, and accepted it with *"none — accepted"*. **The review does not accept it**: emitting the three as `Result(…, None, "not evaluated")` costs four lines and needs no second list. | `INCIDENTS.md` INC-07; `check_roles.py`'s own docstring (*"`n/a` is never silently a pass"*) | **REVIEW_C0_1** | **OPEN** | — |
| **OF-04** | C0 | **MEDIUM** | **Q-014's remaining half: a `Session-Token` trailer that is PRESENT but MALFORMED is treated as ABSENT, and E4 then prints a false statement.** E4 names `9663247`, `6d08cf3`, `d67550e`, `ec3064d` among *"commit(s) carry no trailer"* when all four carry one, and attributes them to Q-001 — a different session's different cause. **Reviewer's ruling (`REVIEW_C0.md` F4): it must FAIL, not be silent.** The architect's 8-hex ruling is what makes failing safe; the fix is a second permissive pattern feeding a new `E5`, leaving `_TOKEN_TRAILER` strict as ruled. **Due before C1 is reviewed** — from the first chunk with separate build and review sessions, E1's silence is all that stands between the log and an invented credential. | `PROCESS.md` §7a; `CONTEXT.md` §14 (*"rules fail closed"*); Q-014 | **REVIEW_C0_1** | **OPEN** | — |
| **OF-05** | C0 | **MEDIUM** | **`check-roles` B1 inspects only the repository root.** A tracked `config/secrets/.env` reports `PASS B1 no .env tracked — none tracked` (reproduced). Bounded by `.gitignore` (path-agnostic, so `git add -f` is needed) and by C1, which does catch it **if** the value matches one of the eight enumerated shapes (verified). The finding is that B1's printed claim is broader than its check. | `CLAUDE.md` §4; `PROCESS.md` §8 | **REVIEW_C0_1** | **OPEN** | — |
| **OF-06** | C0 | **MEDIUM** | **The loader returns YAML null, empty and whitespace-only values silently.** `require()` returns `None` for `key:` / `null` / `~` and `''` for a blank string; `outstanding_sentinels()` counts none of them. Found by an independent re-implementation written from the spec text (`docs/reviews/independent/c0_config_loader.py`) — 6 of 12 cases agree, 4 classes diverge, all of the form *"written down but never supplied"*. **Scenario:** a hand-edit leaves `probe.void_threshold_breach_rate:` blank; every sentinel report says clean and the void threshold is `None`. That is the scenario `config.py`'s own docstring says the mechanism exists to prevent, arriving through the input it cannot see. `lanes.yaml`'s `tpd: null` is explicitly **not** part of this — it is a documented, tested "no such limit exists". **Partially closed here** by `test_protocol_yaml_holds_no_null_and_no_empty_string`. | `CLAUDE.md` hard rule 9 | **REVIEW_C0_1** | **OPEN** | — |
| **OF-07** | C0 | **MEDIUM** | **`make test` is red for any uncommitted edit to any tracked file.** `test_the_object_store_and_the_working_tree_agree` compares the working tree against `git show HEAD:`. The suite is therefore unusable while writing code, creates standing pressure to **commit in order to go green** in a project whose commits are its audit trail, and is useless as a mutation oracle — the reviewer's first mutation run scored 18/18 "killed" on tree-dirtiness alone, control mutant included, and had to be discarded. `check-roles` A4 already asks §6a's property in the form answerable on a dirty tree, and `test_a4_does_not_fire_merely_because_the_tree_is_dirty` exists to keep it that way. | `PROCESS.md` §6a; `CLAUDE.md` hard rule 6 (pressure toward, not a breach of) | **REVIEW_C0_1** | **OPEN** | — |
| **OF-08** | C0 | **MEDIUM** | **Q-010's Class A default was not merely recorded but IMPLEMENTED before a ruling.** `.gitignore` gained `vendor/*/` in `ee098a4`, so a Class A deviation that *"changes what a reviewer receives"* is in force, unruled. The measurement behind it is sound and the reviewer agrees with the conclusion; the objection is procedural. Q-001's and Q-003's defaults are by contrast **accepted** — both reversible, both conservative. **Needs a ruling before C19's clean-clone test.** | `CLAUDE.md` hard rule 2 (Class A → STOP and ask); Q-010 | **REVIEW_C0_1** | **OPEN** | — |
| **OF-09** | C0 | **MEDIUM** | **`repo_root()` silently reports on the wrong directory and no target names the one it used.** `Path(__file__).resolve().parents[2]` is correct only for an editable src-layout install. Under `pip install .` it resolves to `…/.venv/Lib`, and `check-roles` then prints **`PASS F1 config/ loads — protocol.yaml and lanes.yaml parse`** over **zero** config files while `check-prereg` prints `config/ holds 0 file(s):` and **exits 0**. With one venv and two checkouts it reports on the venv's checkout: it printed a full green report while the reviewer stood in a clone with a deliberately corrupted `.gitattributes`. **It fooled the reviewer for one experiment.** | `CLAUDE.md` hard rule 9 (`config/` is a pre-registration artefact) | **REVIEW_C0_1** | **OPEN** | — |
| **OF-10** | C0 | **MEDIUM** | **Any exception in any check destroys the entire `check-roles` report.** `run()` builds all four groups eagerly and `check_gitattributes(root) + check_secrets(root)` is one element, so a `.gitattributes` problem **silences the secret scan** along with D, E and F. Reproduced: a non-UTF-8 byte in `.gitattributes` makes `read_text` raise and `make check-roles` emits a bare traceback with no check output at all. Fail-closed on the exit code; zero information in the report. `_git()`'s `RuntimeError` has the same blast radius. | `check_roles.py` docstring; `INCIDENTS.md` INC-07 (same family) | **REVIEW_C0_1** | **OPEN** | — |
| **OF-11** | C0 | **LOW** | **`_first_party_imports` misses `import a, b` (one capture group, records only `a`) and `importlib.import_module(...)`.** Two more holes in B-02's net; the textual approach itself is well-argued and correct. | `CLAUDE.md` hard rule 8 | **REVIEW_C0_1** | **OPEN** | — |
| **OF-12** | C0 | **LOW** | **The tripwire is evaded by arithmetic decomposition (`500 * 10000`) and Indian digit grouping (`50_00_000`).** Inherent to a textual scan and probably not worth closing — but it is stated nowhere, and `CONTEXT.md` §8.6 calls an out-of-table constant *"a review BLOCKER"*. Record it as a known limit. | `CLAUDE.md` hard rule 9; `CONTEXT.md` §8.6 | **REVIEW_C0_1** | **OPEN** | — |
| **OF-13** | C0 | **LOW** | **`pyproject.toml` declares `readme = "README.md"` against a file that does not exist.** Tolerated silently by both `pip install -e .` and `pip install .`. C19 creates the README; recorded so it is not discovered on 3 September. | `CONTEXT.md` §16, §20 | **REVIEW_C0_1** | **OPEN** | — |
| **OF-14** | C0 | **MEDIUM** | **`pip install -e .` — the obvious command — leaves `make test` broken, and nothing in the repository says `[dev]` is required.** Reproduced from a bare clone: `python -m whetstone_gate.tasks test` → `No module named pytest`, exit 1. There is no README, and `tasks.py` does not diagnose it. `CONTEXT.md` §20's first box splits ownership — C19 owns the clean-clone test, **C0 owns "the command exists"** — and the command as it stands does not run after the natural install. | `CONTEXT.md` §20 box 1; `PROCESS.md` §12.1 C0 done-when | **REVIEW_C0_1** | **OPEN** | — |
| **OF-01** | C0 | **MEDIUM** | **A lone CR is invisible to both `check-roles` A3 and A4.** A single stray CR (not followed by LF) makes git classify an otherwise-textual file `-text`, so it lands in the binary bucket: A3 does not scan it, and A4 cannot fail on it because git converts nothing on `-text` content. **Reproduced:** a markdown file whose only defect is one lone CR eating a sentence reports `i/-text w/-text`, contains no CRLF pair, and **passes both checks.** ⚠️ **Not a regression** — the pre-`1be73e4` A3 searched for CRLF *pairs* and missed a lone CR too — **but it is INC-06's and INC-10's exact defect class, and INC-10 was caught only because that CR happened to be followed by LF.** Under a lone CR the repository would have gone green over corrupted prose. **Proposed fix, not applied:** a new check asserting *"no tracked file is classified `-text` while containing no NUL byte"* — a narrow discriminator that flags a file made binary by CR statistics alone, and that passes both dashboard PNGs (they carry NULs in `IHDR`). Needs a new check and a mutation test, i.e. new scope. | `PROCESS.md` §6a; `CLAUDE.md` hard rule 6; INC-06, INC-09, INC-10 | **C0-COMPLETION BUILD** (not a review — see the note above) | **OPEN** | — |

---

## OF-01 — status update from `REVIEW_C0_1` (`52f5307b`), 2026-08-30

**Confirmed. Independently reproduced. Stays OPEN. Partially mitigated, and re-scoped.**

The reviewer reproduced OF-01 exactly as written and then established **one fact the original row
does not state, which changes how it must be fixed**:

> **`PROCESS.md` §6a's fingerprint property is NOT violated by a lone CR.** For the reproduction
> file, the working-tree bytes and the committed blob are byte-identical
> (`b'line one\rline two\nline three\n'` on both sides) — git applies no conversion to `-text`
> content, so a fresh clone reproduces the bytes on every OS.

**A3 and A4 are therefore not failing at their own job.** The gap is in a **different** property,
and `INCIDENTS.md` INC-10's `Missing` field already names it: *"nothing checks a tracked document's
CONTENT, only its line endings … neither can say 'and it has eaten a sentence.'"* That is the
property a lone CR breaks, and it is the property INC-06 and INC-10 are both about.

**What this review did, and did not do.**

- **Verified the proposed discriminator is sound and false-positive-free here.** Both dashboard PNGs
  carry NUL bytes in their first 8000 (IHDR); the lone-CR file carries none.
- **Answered the anti-circularity objection that kept it out of `check_roles`.** The discriminator
  is **not** a second copy of git's text/binary heuristic. It compares git's verdict against an
  independent signal — which is the *opposite* of hard rule 8's circularity, not an instance of it.
  The reason recorded for not applying it therefore does not survive.
- **Added it as a KEPT PROBE**: `tests/test_c0_review_probes.py::test_no_tracked_file_is_binary_without_a_nul_byte`.
  `make test` now detects the condition on every run.
- **Did not fix it.** A review session fixes nothing (`CLAUDE.md` §1), and `make check-roles` — not
  `make test` — is what C0's done-when names.

**Revised status:** *reproduced, detected by `make test`, still invisible to `make check-roles`.*
**Severity unchanged at MEDIUM.** The fix session adds it as `A5` in `check_gitattributes`, with the
mutation test that the original row correctly says it needs.
