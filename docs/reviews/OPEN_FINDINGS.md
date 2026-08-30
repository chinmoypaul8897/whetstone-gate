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

⚠️ **UPDATED BY THE C0 FIX SESSION (`c9521aac`), 2026-08-31.** Six rows move: **OF-01, OF-03, OF-04,
OF-06 and OF-10 are CLOSED**; **OF-02, OF-09 and OF-11 are updated but STAY OPEN**, each with the
part that was *not* closed named rather than rounded up. **This session closed nothing by assertion:
every closure carries a probe that was run against the pre-fix source and observed to fail there.**
⚠️ **A fix session does not certify its own work.** These rows record what changed and with which
SHA; whether that is *enough* is the next review's to say, and no `c0-pass` tag is cut here.

| ID | Chunk | Severity | Finding | Spec citation | Raised by | Status | Closed by (SHA) |
|---|---|---|---|---|---|---|---|
| **OF-02** | C0 | **MEDIUM** | **12 of 19 mutants survive both `make test` and `make check-roles`.** Applied per-mutant to a clean clone and **committed** (so the dirty-tree test was satisfied — the state a real defect lives in), with a semantics-preserving control that correctly survived. Survivors include **B1 no longer detecting a tracked `.env` at all** and **the secret scanner reduced to 1 of its 8 patterns**. Cause: `tests/test_repo_invariants.py` asserts `result.ok is True` against a repository in which every check passes trivially, and only three tests in the suite build a fixture that should make a check FAIL. **Partially closed here:** `tests/test_c0_review_probes.py` (20 kept probes) takes the kill rate from **6/19 to 17/19**. The two remaining are **M15 (D3)**, deliberately left because a probe there would leave a green test standing over B-02, and **M20**, an equivalent mutant (`git rev-list --max-parents=0 HEAD` cannot return empty while HEAD resolves). Full table in `REVIEW_C0.md` F-05. | `PROCESS.md` §5.4, §12.1 (`code` = ≥4 mutants) | **REVIEW_C0_1** | ⚠️ **OPEN — M15 KILLED, MEASURED; THE OTHER 18 NOT RE-RUN** | **`947a995` kills M15**, which the review deliberately left alive because *"a probe there would leave a green test standing over B-02 — B-02 needs a fix, not a probe."* **Measured, not asserted:** M15 (`shared = set()` hard-wired in D3) was applied to a clean clone of `8ed108e`, **committed** — INC-11's corrected harness, so the oracle is the assertions and not the tree's cleanliness — and the suite reported **5 failed, 111 passed**, the five being all four B-02 attack forms plus the `import a, b` probe. ⚠️ **The remaining 18 mutants were NOT re-run and no new mutation score is claimed here.** A mutation run is a review activity and a fix session that scored its own work would be doing exactly what this project exists to reject. What can be said is narrower and checkable: this session added **52 probes**, of which **46 fail against `864c621`'s source** and the 6 that pass there are regression guards by design; the count of tests in this suite that fire a check at input built to break it goes from **3** (`REVIEW_C0.md` F-05's number) to well over forty. **The next review re-runs the mutants.** |
| **OF-03** | C0 | **MEDIUM** | **`check_gitattributes`'s early return removes A2/A3/A4 from the report with no `n/a`** — a check's *absence* and a check's *pass* are again indistinguishable to a caller. Reproduced: with `.gitattributes` deleted the function returns **one** result and the summary silently prints three fewer checks. Never a false PASS (A1 fails in that branch), so it is information loss, not verdict loss. `INCIDENTS.md` **INC-07** diagnosed exactly this, fixed it in `check_secrets`, named this function as the surviving instance, and accepted it with *"none — accepted"*. **The review does not accept it**: emitting the three as `Result(…, None, "not evaluated")` costs four lines and needs no second list. | `INCIDENTS.md` INC-07; `check_roles.py`'s own docstring (*"`n/a` is never silently a pass"*) | **REVIEW_C0_1** | **CLOSED** | **`4a34c04`** — A2, A3, A4 **and A5** are emitted as `Result(…, None, "not evaluated — .gitattributes is missing; see A1")`. ⚠️ **And INC-07's other half, which OF-03 does not state and which was still present:** A1 was emitted under a *different check name* on the failing branch (`A1 .gitattributes exists`) from the passing one (`A1 .gitattributes content`), so a caller's lookup raised `KeyError` instead of reporting a failure — INC-07's literal one-line diagnosis. A1 now keeps one name on both branches. Probe: `test_every_A_check_is_still_emitted_when_gitattributes_is_missing` |
| **OF-04** | C0 | **MEDIUM** | **Q-014's remaining half: a `Session-Token` trailer that is PRESENT but MALFORMED is treated as ABSENT, and E4 then prints a false statement.** E4 names `9663247`, `6d08cf3`, `d67550e`, `ec3064d` among *"commit(s) carry no trailer"* when all four carry one, and attributes them to Q-001 — a different session's different cause. **Reviewer's ruling (`REVIEW_C0.md` F4): it must FAIL, not be silent.** The architect's 8-hex ruling is what makes failing safe; the fix is a second permissive pattern feeding a new `E5`, leaving `_TOKEN_TRAILER` strict as ruled. **Due before C1 is reviewed** — from the first chunk with separate build and review sessions, E1's silence is all that stands between the log and an invented credential. | `PROCESS.md` §7a; `CONTEXT.md` §14 (*"rules fail closed"*); Q-014 | **REVIEW_C0_1** | **CLOSED** | **`0067b19`** — and the architect **raised it to BLOCKER for this fix cycle** in Q-014 (ii), on scheduling the reviewer could not see: C1's review is the next review this project runs. Implemented exactly as ruled: a second **permissive** pattern `^Session-Token:\s*(\S.*?)\s*$` applied only where the strict one did not match, feeding a new **`E5 malformed Session-Token trailer`** that FAILS and names the SHAs; `_TOKEN_TRAILER` **stays strict** and is still pinned by the review's own probe; `_TOKEN_ROW`'s chunk group widens to `(C\d+\|ARCH)` and **the token group is not touched**. E4's *"carry no trailer"* list drops from **20 to 16** and stops naming `9663247`, `6d08cf3`, `d67550e`, `ec3064d`. Those four ship as an **explicit, dated, named exception list of full SHAs, pinned at exactly four entries by a test** — Q-014 (iv) forbids reshaping that token, and a permanently red check is one people learn to ignore (Q-009's own argument). **E5 FAILS on any NEW malformed trailer.** Probes: `test_e5_fires_on_a_malformed_trailer_that_is_not_on_the_exception_list`, `test_e4_no_longer_counts_a_malformed_trailer_as_an_absent_one`, `test_the_e5_exception_list_is_exactly_the_four_ctx_13_4_commits`, `test_a_chunk_cell_of_ARCH_parses_and_leaves_E1_clean` |
| **OF-05** | C0 | **MEDIUM** | **`check-roles` B1 inspects only the repository root.** A tracked `config/secrets/.env` reports `PASS B1 no .env tracked — none tracked` (reproduced). Bounded by `.gitignore` (path-agnostic, so `git add -f` is needed) and by C1, which does catch it **if** the value matches one of the eight enumerated shapes (verified). The finding is that B1's printed claim is broader than its check. | `CLAUDE.md` §4; `PROCESS.md` §8 | **REVIEW_C0_1** | **OPEN** | — |
| **OF-06** | C0 | **MEDIUM** | **The loader returns YAML null, empty and whitespace-only values silently.** `require()` returns `None` for `key:` / `null` / `~` and `''` for a blank string; `outstanding_sentinels()` counts none of them. Found by an independent re-implementation written from the spec text (`docs/reviews/independent/c0_config_loader.py`) — 6 of 12 cases agree, 4 classes diverge, all of the form *"written down but never supplied"*. **Scenario:** a hand-edit leaves `probe.void_threshold_breach_rate:` blank; every sentinel report says clean and the void threshold is `None`. That is the scenario `config.py`'s own docstring says the mechanism exists to prevent, arriving through the input it cannot see. `lanes.yaml`'s `tpd: null` is explicitly **not** part of this — it is a documented, tested "no such limit exists". **Partially closed here** by `test_protocol_yaml_holds_no_null_and_no_empty_string`. | `CLAUDE.md` hard rule 9 | **REVIEW_C0_1** | **CLOSED** | **`02f3a2a`** — `require()` raises the new `BlankValue`; the sweep COUNTS blanks under a `BLANK_` marker kept deliberately distinct from `TODO_` (a sentinel is a declaration with an owner, a blank is an omission with nobody's name on it, and one heading for both would relabel a defect as a plan); `check-roles` **F2 now FAILS** on any blank. ⚠️ `0`, `False` and `[]` are SUPPLIED values and still pass — guarded by four probes, because a truthiness test would make `per_action_cap_paise: 0` a refusal. `lanes.yaml`'s `tpd: null` is exempt via `NULL_IS_A_VALUE`, **pinned at exactly two entries by a test** (the second is `reserved_from`, a **Class B** call recorded in the constant's own comment). Probes: `test_a_blank_value_is_a_refusal_and_is_counted` ×5, `test_zero_false_and_empty_list_are_SUPPLIED_values_and_must_pass` ×4, `test_the_null_is_a_value_exemption_is_exactly_two_entries_and_covers_tpd` |
| **OF-07** | C0 | **MEDIUM** | **`make test` is red for any uncommitted edit to any tracked file.** `test_the_object_store_and_the_working_tree_agree` compares the working tree against `git show HEAD:`. The suite is therefore unusable while writing code, creates standing pressure to **commit in order to go green** in a project whose commits are its audit trail, and is useless as a mutation oracle — the reviewer's first mutation run scored 18/18 "killed" on tree-dirtiness alone, control mutant included, and had to be discarded. `check-roles` A4 already asks §6a's property in the form answerable on a dirty tree, and `test_a4_does_not_fire_merely_because_the_tree_is_dirty` exists to keep it that way. | `PROCESS.md` §6a; `CLAUDE.md` hard rule 6 (pressure toward, not a breach of) | **REVIEW_C0_1** | **OPEN** | — |
| **OF-08** | C0 | **MEDIUM** | **Q-010's Class A default was not merely recorded but IMPLEMENTED before a ruling.** `.gitignore` gained `vendor/*/` in `ee098a4`, so a Class A deviation that *"changes what a reviewer receives"* is in force, unruled. The measurement behind it is sound and the reviewer agrees with the conclusion; the objection is procedural. Q-001's and Q-003's defaults are by contrast **accepted** — both reversible, both conservative. **Needs a ruling before C19's clean-clone test.** | `CLAUDE.md` hard rule 2 (Class A → STOP and ask); Q-010 | **REVIEW_C0_1** | **OPEN** | — |
| **OF-09** | C0 | **MEDIUM** | **`repo_root()` silently reports on the wrong directory and no target names the one it used.** `Path(__file__).resolve().parents[2]` is correct only for an editable src-layout install. Under `pip install .` it resolves to `…/.venv/Lib`, and `check-roles` then prints **`PASS F1 config/ loads — protocol.yaml and lanes.yaml parse`** over **zero** config files while `check-prereg` prints `config/ holds 0 file(s):` and **exits 0**. With one venv and two checkouts it reports on the venv's checkout: it printed a full green report while the reviewer stood in a clone with a deliberately corrupted `.gitattributes`. **It fooled the reviewer for one experiment.** | `CLAUDE.md` hard rule 9 (`config/` is a pre-registration artefact) | **REVIEW_C0_1** | ⚠️ **OPEN — PARTIALLY CLOSED** | **`02f3a2a` closes the `check-roles` half only.** `check-roles` now prints **`ROOT EXAMINED`** and **`CONFIG DIR`** at the top *and* at the bottom of its report, and a new **`R1 the examined root IS this repository`** FAILS — rather than reporting green over the wrong directory — when that root holds no `.git` or no `config/`. F1 additionally prints the config directory it opened and the files it actually parsed. ⚠️ **STAYS OPEN** because the finding says *"every target"*: `check-prereg`, `test` and `eval` live in `src/whetstone_gate/tasks.py`, which is **outside the C0-FIX session's scope fence**, so `check-prereg` still prints `config/ holds N file(s)` without naming the root it resolved. Probes: `test_check_roles_FAILS_rather_than_passing_vacuously_on_a_non_repository`, `test_every_target_prints_the_root_it_examined` |
| **OF-10** | C0 | **MEDIUM** | **Any exception in any check destroys the entire `check-roles` report.** `run()` builds all four groups eagerly and `check_gitattributes(root) + check_secrets(root)` is one element, so a `.gitattributes` problem **silences the secret scan** along with D, E and F. Reproduced: a non-UTF-8 byte in `.gitattributes` makes `read_text` raise and `make check-roles` emits a bare traceback with no check output at all. Fail-closed on the exit code; zero information in the report. `_git()`'s `RuntimeError` has the same blast radius. | `check_roles.py` docstring; `INCIDENTS.md` INC-07 (same family) | **REVIEW_C0_1** | **CLOSED** | **`02f3a2a`** — the groups are built **lazily**, one at a time, each inside its own `try`; a group that raises is reported **by name**, with the exception type, message and `file:line`, and **every other group still runs**. A and B/C are also split into separate groups, so a `.gitattributes` problem can no longer be in the same element as the secret scan at all. Probe: `test_one_raising_group_cannot_silence_the_secret_scan` — a non-UTF-8 byte in `.gitattributes`, asserting that `C1`, `B1`, `E1` and `F1` all still appear in the output |
| **OF-11** | C0 | **LOW** | **`_first_party_imports` misses `import a, b` (one capture group, records only `a`) and `importlib.import_module(...)`.** Two more holes in B-02's net; the textual approach itself is well-argued and correct. | `CLAUDE.md` hard rule 8 | **REVIEW_C0_1** | ⚠️ **OPEN — HALF CLOSED, and the half is named rather than rounded up** | **`947a995` closes the `import a, b` half only**, as a consequence of B-02's rewrite rather than as scope of its own: the walk moved from one regex to `ast.parse`, which sees every alias. Probe: `test_the_walk_sees_import_forms_a_single_capture_group_missed`. ⚠️ **`importlib.import_module(…)` STAYS OPEN and is not closeable this way** — it is a runtime call, not an import statement, and no parser of import statements can see it. The review's own argument against an import-driven walk (*"importing `gates` to learn what `gates` imports would execute it"*) still holds, so the remedy is not "parse harder"; it would be a separate check. **Recorded as half closed rather than closed.** |
| **OF-12** | C0 | **LOW** | **The tripwire is evaded by arithmetic decomposition (`500 * 10000`) and Indian digit grouping (`50_00_000`).** Inherent to a textual scan and probably not worth closing — but it is stated nowhere, and `CONTEXT.md` §8.6 calls an out-of-table constant *"a review BLOCKER"*. Record it as a known limit. | `CLAUDE.md` hard rule 9; `CONTEXT.md` §8.6 | **REVIEW_C0_1** | **OPEN** | — |
| **OF-13** | C0 | **LOW** | **`pyproject.toml` declares `readme = "README.md"` against a file that does not exist.** Tolerated silently by both `pip install -e .` and `pip install .`. C19 creates the README; recorded so it is not discovered on 3 September. | `CONTEXT.md` §16, §20 | **REVIEW_C0_1** | **OPEN** | — |
| **OF-14** | C0 | **MEDIUM** | **`pip install -e .` — the obvious command — leaves `make test` broken, and nothing in the repository says `[dev]` is required.** Reproduced from a bare clone: `python -m whetstone_gate.tasks test` → `No module named pytest`, exit 1. There is no README, and `tasks.py` does not diagnose it. `CONTEXT.md` §20's first box splits ownership — C19 owns the clean-clone test, **C0 owns "the command exists"** — and the command as it stands does not run after the natural install. | `CONTEXT.md` §20 box 1; `PROCESS.md` §12.1 C0 done-when | **REVIEW_C0_1** | **OPEN** | — |
| **OF-01** | C0 | **MEDIUM** | **A lone CR is invisible to both `check-roles` A3 and A4.** A single stray CR (not followed by LF) makes git classify an otherwise-textual file `-text`, so it lands in the binary bucket: A3 does not scan it, and A4 cannot fail on it because git converts nothing on `-text` content. **Reproduced:** a markdown file whose only defect is one lone CR eating a sentence reports `i/-text w/-text`, contains no CRLF pair, and **passes both checks.** ⚠️ **Not a regression** — the pre-`1be73e4` A3 searched for CRLF *pairs* and missed a lone CR too — **but it is INC-06's and INC-10's exact defect class, and INC-10 was caught only because that CR happened to be followed by LF.** Under a lone CR the repository would have gone green over corrupted prose. **Proposed fix, not applied:** a new check asserting *"no tracked file is classified `-text` while containing no NUL byte"* — a narrow discriminator that flags a file made binary by CR statistics alone, and that passes both dashboard PNGs (they carry NULs in `IHDR`). Needs a new check and a mutation test, i.e. new scope. | `PROCESS.md` §6a; `CLAUDE.md` hard rule 6; INC-06, INC-09, INC-10 | **C0-COMPLETION BUILD** (not a review — see the note above) | **CLOSED** | **`4a34c04`** — `check-roles` **A5, branch B**: every file git classifies as **binary** (`w/-text`) must carry at least one NUL in its first 8000 bytes. A binary-classified file with no NUL is textual content git classified binary on **CR statistics alone**, which is exactly this finding. The verdict is taken **from git** (`git ls-files --eol`, `w/` side), never from a reimplementation of its heuristic; the NUL test is **not** a second copy of that predicate — it compares git's verdict against an **independent** signal, which is the opposite of hard rule 8's circularity, and the review confirmed that reasoning at F3. Probes: `test_a5_branch_B_fires_on_the_OF01_reproduction` (the review's exact `printf 'line one\rline two\nline three\n'`, asserting first that git really says `w/-text` so the probe cannot pass on the wrong branch, then that A5 FAILS while A3 and A4 both still PASS — the blindness this finding is about) and `test_a5_branch_B_passes_the_two_dashboard_pngs` (the false-positive half: both carry NULs in their IHDR). ⚠️ **A5's stated limit, printed in its own output:** a NUL inside a prose document is invisible to **both** branches, because a NUL makes git classify a file binary at any size — MEASURED, not assumed — so branch T never sees it and branch B accepts it. That is `INC-10`'s `Missing` field, and it **stays open**; A5 narrows it and does not close it. Asserted as a known gap by `test_a5_states_the_NUL_in_prose_gap_it_cannot_close`. |

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

---

## OF-01 — CLOSED by the C0 FIX session (`c9521aac`), 2026-08-31, in `4a34c04`

**`A5` exists, in `check_gitattributes`, with TWO branches — and the second branch is the reason
the first is not enough.**

⚠️ **A claim that must not be rebuilt, because it is in the record and it is wrong.** It was
proposed that ONE branch would do — that a control-byte scan over TEXT-classified files is a
*"strict superset"* of OF-01's lone-CR discriminator. **It is not.** OF-01's whole point is that a
lone CR makes git classify the file **BINARY**, so a scan over text-classified files **skips exactly
the file OF-01 is about**. `INCIDENTS.md` **INC-13**'s byte, conversely, sits in a file git
correctly calls **TEXT**. **Two holes, on opposite sides of git's own verdict.** Building one branch
would have closed OF-01 on paper and left it open — which is, precisely, this chunk's own failure
mode repeated. Both branches are built, and each has its own probe fired at a fixture built to
violate it.

**What A5 does NOT close, printed in A5's own output and asserted by a test** so that a later reader
cannot take the check for more than it is:

> A NUL (`0x00`) inside a prose document is invisible to **both** branches. A NUL makes git classify
> a file binary at **any** size — measured on 2026-08-31, not assumed — so branch T never sees it and
> branch B *accepts* it as the very signal it looks for. Closing that needs a judgement about which
> tracked paths are prose, which is a second copy of a decision A5 deliberately takes from git.

So `INCIDENTS.md` **INC-10's `Missing` field** — *"nothing checks a tracked document's CONTENT, only
its line endings … neither can say 'and it has eaten a sentence'"* — **stays open**. A5 narrows it.
An escape sequence resolving to a printable character, or to a TAB, is still invisible.
