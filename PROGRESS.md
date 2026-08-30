# PROGRESS.md — the session journal

**Newest on top. One entry per session. Fixed template.**
Each entry opens with that session's `SESSION-TOKEN` (`PROCESS.md` §7a). Chat history is
not a record; this file is.

---

## C0-COMPLETION — BUILD — attempt 1 — 2026-08-30

**SESSION-TOKEN:** ⚠️ **none issued.** This prompt, like C0's, carried no `SESSION-TOKEN`
line, and this session **did not fabricate one** — the prompt said so explicitly and
`QUESTIONS.md` **Q-001** already records the gap and the reasoning. Every commit here is
permanently untrailered, and `check-roles` E4 reports that as `n/a` naming Q-001, never as
a pass.

**Scope:** the **three operator-owed items** that C0 reported as FAIL-pending-operator,
now supplied. Nothing else. **No project logic** — no world, ledger, scorer, gates,
attacker or adapters.

**Token spend: NONE.** Zero calls to any Groq or Google model. Writing a model id into a
config file is not a call, and validating an id against the live endpoint is a later
chunk's job that needs the operator's key.

### What landed

1. **The four Google API model ids** (closes **Q-006**), captured by the operator from the
   live models endpoint on 2026-08-30 — `models/gemma-4-26b-a4b-it`,
   `models/gemma-4-31b-it`, `models/gemini-3.1-flash-lite`,
   `models/gemini-3.5-flash-lite` — with each lane's `inputTokenLimit`,
   `outputTokenLimit` and `supportedGenerationMethods`, and the **preview-vs-stable
   ruling** written down so nobody re-derives it under time pressure.
2. **Both dashboard screenshots** (closes half of **Q-008**), with byte sizes, SHA-256
   digests, and a structural PNG validation.
3. **The no-payment-method attestation** (closes the other half of **Q-008**), labelled
   **OPERATOR-ATTESTED**, with what the property actually buys written out beside it.

### The three things worth reading the diff for

1. **`make selftest` is still red, and the report says so in the first paragraph.** The
   placeholder gate is now green; the remaining failure is
   `test_the_camel_branch_is_decided_before_any_camel_run` — `TODO_C13_RUN1`, owned by
   RUN-1 on 31 August. A different reason, reported as a different reason. `STATUS.md`
   now carries a *"what `make selftest` is still waiting on"* table so a red gate is never
   mistaken for missing ids again.
2. **The caching finding was verified, not accepted.** The prompt said the architect had
   already checked that §13.4 is unaffected. It is — `grep -ic cach CONTEXT.md` returns
   **0**, and §13.4's figures re-derive exactly from raw throughput (32,000 × 60 =
   1.92M/h; 76.9M ÷ 1.92M = 40.05 h against its stated ≈40 h; ~37 h and ~34 h likewise).
   **Q-011** records the fact, the verification, and the forward consequence: caching is
   **not** an available lever for the §13.4 lane-hour gap, and it would not help on the
   Flash Lite lanes either, because those are **request**-bound and caching reduces
   *tokens*. The **rule-13 judgement is stated from rule 13's own text** — no `Event`, no
   violated `Expectation`, no causal mechanism for `Diagnosis`, no ignored signal for
   `Missed`; writing it as an incident would mean inventing two mandatory fields, which is
   the dramatisation rule 13's closing note warns against. **QUESTIONS entry, not an
   incident.**
3. ⚠️ **The screenshots broke the build, and the break was real — INC-09.** They are the
   repository's first binary files. `check-roles` **A3** scanned every tracked file's raw
   bytes for `
`, and a PNG's deflate stream carries those bytes as data, so `make
   check-roles` and `make test` went red on a sound repository. **`.gitattributes` was
   innocent** and is unchanged — `git ls-files --eol` says `i/-text w/-text` and
   `git hash-object` with and without `--no-filters` agree, so `* text=auto` already
   detects them as binary. The prompt's conditional *"if they are being treated as text"*
   **did not fire**, and adding an image rule would have broken A1 anyway. What was fixed
   is A3 itself, **without weakening it**: A3 keeps its assertion over every file **git**
   calls text, and a new **A4** asserts the underlying property — would git's filter chain
   rewrite these bytes? — over **every** tracked file. Proven meaningful against the
   pre-fix module loaded out of the object store. **Q-012** records it as a Class B
   deviation with the reasoning exposed, because a session that changes a structural
   invariant should not be the only one who thinks the change was sound.

### Corrections made rather than carried forward

- **"six Google API model ids" → FOUR.** `config/lanes.yaml`'s header and `PROVENANCE.md`
  §2.3 both said six; there are four Google lanes and the gate reported four placeholders.
- **Q-006 names the gate file as `tests/test_lanes_no_placeholders.py`.** The file is
  `tests/test_lanes_operator_placeholders.py` and never had the other name. Both
  corrections are recorded **in Q-006's closure**, with the original text left standing —
  a question log that edits its own history is worth less than one that shows the fix.

### What was deliberately NOT touched

The `check_gitattributes` **early-return shape** that C0's own report names as a candidate
defect. The scope fence reserved it for C0's review and pre-empting it would remove the
reviewer's finding. It is still there.

---

## C0 — BUILD — attempt 1 — 2026-08-30

**SESSION-TOKEN:** ⚠️ **none issued.** The C0 build prompt carried no `SESSION-TOKEN` line,
and this session **did not fabricate one** — a fabricated token would be exactly the
*"token that was never issued"* that `make check-roles` exists to catch, and it would put a
forged credential in the audit trail of a project whose thesis is that self-certified
evidence is worthless. Recorded as **`QUESTIONS.md` Q-001**; C0's commits are permanently
untrailered and that gap is visible rather than papered over.

**Scope:** the repository, the toolchain, the private remote, the canonical files, and
`CONTEXT.md` §13.7's day-one provider setup. **No project logic** — no world, no ledger,
no scorer, no gates, no attacker, no adapters.

**Token spend: NONE.** No call to any Groq or Google model, not one. The chunk needed
none, and the two things that *do* need a provider — the exact Google API model ids and
the dashboard screenshots — are reachable only by the operator, not by any session.

### What was built

- **Repository** at `github.com/chinmoypaul8897/whetstone-gate`, **PRIVATE**, branch
  `main`. It stays private until C21 flips it on 4 September, after the git-history secret
  scan.
- **`.gitattributes` (`* text=auto eol=lf`) in the FIRST commit**, `ee3cf93`, with
  `.gitignore`, `LICENSE` and `INCIDENTS.md`. This is `PROCESS.md` §6a's prerequisite and
  it is fixable only in the first commit.
- **`CONTEXT.md` v1.0** — a byte-identical copy of the audited `PROJECT_SPEC.md` under a
  version header and an empty change-log, with the identity claim made checkable:
  `tail -n +35 CONTEXT.md | sha256sum` reproduces the source digest.
- **`PROCESS.md`**, unchanged and verified identical by SHA-256.
- **`CLAUDE.md`** — the constitution. All **thirteen** hard rules extracted **verbatim**
  (`diff` against `PROCESS.md` §4 is empty), plus §6b's single-shot rule verbatim, the read
  order, the token/key rules, the git rules and the end-of-session duties.
- **`STATUS.md`**, **`PROGRESS.md`**, **`QUESTIONS.md`**, **`PROVENANCE.md`**,
  **`ARCHITECT_HANDOFF.md`**; `docs/personas/` (three files, verbatim from §5.3),
  `docs/reviews/` + `OPEN_FINDINGS.md`, `tests/goldens/` (**empty — C0 authors no
  golden**).
- **Toolchain.** Python **3.12.2** venv; the `make` shim installed to `~/bin/make.exe`
  (GNU Make 3.82.90, verified to execute a recipe); τ²-bench installed editable at the
  pinned SHA; a **logic-free** `Makefile` whose every recipe is a one-line delegation.
- **`config/` + one loader** with **no defaulting accessor at all**, plus the hard-rule-9
  tripwire and its coverage test.

### The four things worth reading the diff for

1. **`.gitattributes` was verified, not assumed.** A clone with `core.autocrlf=false`
   (simulating a Linux reviewer) reproduces **byte-identical** SHA-256 digests to this
   Windows working tree, on every tracked file. That is the property `PROCESS.md` §6a's
   fingerprint depends on, and it now has evidence rather than an intention.
2. **The config loader has no `get(key, default=...)`, and a test asserts it does not.**
   Hard rule 9 is a hard refusal, so the API has nowhere to put a fallback. Values that are
   *not yet decided* — the void threshold, the N branch, the Google ids, the AgentDojo/CaMeL
   SHAs — are explicit `TODO_` sentinels that **raise on read, naming who owes them**. If a
   missing void threshold silently read as `0.0`, every run would clear the void check, the
   project's central control would be inert, and nothing would have raised.
3. **The tripwire has two modes and a coverage test, and it is proven to fire.** STRICT for
   distinctive literals; CONTEXTUAL for small integers that recur innocently (`range(20)`
   is fine, `turn_budget = 20` is not). A separate test asserts the registry covers every
   `CONTEXT.md` §8.6 row — without it a constant could be dropped from the registry and the
   scan would stay green while no longer scanning for it.
4. **`make selftest` is RED on purpose and `make test` is green.** Two of C0's own
   done-when boxes contradict each other (`QUESTIONS.md` Q-009); the resolution is two
   tiers, both real. `make test` prints how many operator-gate tests it deselected and why.

### Verification

| | |
|---|---|
| `make test` | **38 passed, 1 skipped, 2 deselected — exit 0** |
| `python -m whetstone_gate.tasks test` | identical result, **exit 0** |
| `make check-roles` | **12 passed, 0 failed, 4 n/a — exit 0** |
| `make selftest` | **2 failed — exit 2. Correct.** No token may be spent against a guessed model id |
| `make check-prereg` / `make eval` | run; report NOT-YET-FROZEN, which is *"not yet"*, not a pass |
| clean clone | verified in a fresh directory — see the C0 report |

The 1 skip is `gates/`↔`scorer/` isolation: **neither directory exists yet** (C8, C9), and
`n/a` is asserted as `n/a` rather than counted as a pass.

### Questions raised

**Ten**, Q-001 … Q-010. The three that block later chunks:

- **Q-004** — `CONTEXT.md` §16's repo tree is self-inconsistent about whether `gates/`,
  `scorer/` and the rest live **inside** `src/whetstone_gate/` or **beside** it. The two
  readings differ in every import path in the project. **Must be ruled before C2.** C0
  created neither, and `check-roles` checks both layouts so it needs no edit when the
  ruling lands.
- **Q-003** — the C0 prompt asks for `evals/` outputs to be git-ignored; `CONTEXT.md` §16,
  `PROCESS.md` §9 and `PROCESS.md` §6b all require them **committed**. Ignoring them would
  make `make eval` unable to regenerate anything from a clean clone and would leave §6b's
  single-shot control unenforceable.
- **Q-010** — τ²-bench at the pin is **793 MB**, most of it other people's published model
  transcripts. Pinned rather than committed. **C19's clean-clone test must include the
  fetch step**, or §20's first box is false.

### Incidents

**Three written — INC-06, INC-07, INC-08 — all dated AFTER the first build commit**, which
is what hard rule 13 requires and what C21 must cite. All eight entries in the file carry
all eight mandated fields.

- **INC-06** is the one to read: a build script wrote **CRLF into four tracked files**, and
  `.gitattributes` caught it. That is *exactly* the failure `PROCESS.md` §6a exists to
  prevent — a fingerprint from a CRLF working tree would not match what any Linux or macOS
  reviewer computes from the same git objects, and it would have failed **at the moment of
  judging**, silently, looking like fraud rather than a line-ending bug. It arrived on day
  one instead. Two checks now assert the property on every run.
- **INC-07** — a checker emitted a different result key on pass than on fail, so its test
  **crashed instead of failing**. The test was not relaxed to accommodate it (hard rule 6);
  the checker was corrected. Its `Systemic guardrail` is honestly *"none — accepted"*, and
  it **names the same smell still present in `check_gitattributes`** as a live candidate
  finding for C0's review rather than leaving it to be discovered.
- **INC-08** — operator-facing output was unreadable on the operator's own terminal. The
  slightest of the three, and labelled as such.

### Owed to the operator

The **exact Google API model id strings** (`models/gemma-…`, `models/gemini-…`), the two
dashboard **screenshots**, and the **no-payment-method** confirmation. Only the operator
can supply any of them. `make selftest` fails until the ids land.

### Hold-point

C0 is **built, unreviewed**. It has not been self-certified and must not be.
**Next:** the architect's `ARCHITECT_CHECK_0.md`, then a C0 **`code`** review in a
different fresh session. C1 (`RAZORPAY_SEMANTICS.md`) and C2 (the world + the planted
probe) are the next builds, and **C2 needs golden 7 committed before its prompt is
issued.**
