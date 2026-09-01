# REVIEW 13, attempt 1 — C13, THE CaMeL COMPARATOR

**Verdict: FAIL.** · Session `b450df0a` · 2026-09-01 · Review type **full**, two sealed phases
**Phase-1 seal:** `3964cd376de1fe2ed2ea886e1a894c7bd394cf34`
**Personas:** evaluation-integrity (1) + code (2), `PROCESS.md` §5.3
**Tag `c13-pass`: NOT CUT.**

> **The single most important sentence in this file is not the verdict.** `CONTEXT.md` was
> amended to **v1.8** on C13's reading of arXiv 2503.18813v2. This review fetched the paper
> itself, parsed Tables 2, 4, 5, 6 and 7 with its own reader, resolved each table's appendix
> from the document structure rather than from anybody's say-so, and found **C13's reading
> correct in every particular**. ⚠️ **The law is right. Two BLOCKERs below are about the
> harness and its guards, not about the amendment.**

---

## 0. Verdict, and exactly what it turns on

`PASS` required **all** of: every claim independently re-derived **and agreeing**; every mutant
killed or proven equivalent; **zero BLOCKERs**; and no published figure lacking table, appendix,
base model and row.

| PASS condition | result |
|---|---|
| every claim re-derived and agreeing | **22 of 24 agree; 2 diverge** (claims 15 and 24) |
| every mutant killed or proven equivalent | **20 run: 16 killed, 2 proven equivalent, 3 survived** |
| zero BLOCKERs | **2 BLOCKERs** |
| no published figure lacking the four fields | ✅ **17 of 17 figures complete** — this one passes |

**Both BLOCKERs are about a gate that does not guard what it says it guards.** Neither is about
a wrong number, and neither touches `CONTEXT.md` v1.8. A FIX session can close both without
reopening a single figure.

⚠️ **This FAIL is not a judgement on the chunk's quality.** C13 found two Class-A defects in the
specification, obtained rulings on both, landed the amendment, found its own build-1 guardrail
one field short, extended it, found four surviving copies of the corrected citation in artefacts
outside its own fence, and declared the one edit it could not make rather than slipping it in.
That is a high standard, and the two BLOCKERs are what is left when the work is checked at that
standard rather than at a lower one.

---

## BLOCKER B-1 — the RUN-1 same-working-directory claim cites DEAD CODE, and the failure mode it states is FALSE for the live path

**Severity: BLOCKER.** **Files:** `src/whetstone_gate/camel_comparator/invocation.py` (module
docstring; `Run1Plan.same_working_directory` docstring **and** its runtime value; pass 2's
`Invocation.purpose`), `tests/test_c13_camel_comparator.py::test_both_passes_share_one_working_directory_and_the_plan_says_why`
and `::test_run1_is_two_passes_and_the_second_replays_the_first`, and upstream of all of them
`QUESTIONS.md` **Q-057**, recorded fact 4.

### What C13 says

> *"`replay_privileged_llm.py:321` reads `Path("logs") / pipeline_name / suite_name /
> user_task_id / attack_name` — i.e. **the stored logs of the earlier `+camel` pass**."*
> *"…pass 2 run from anywhere else reads an empty tree and **reports nothing rather than
> failing** — a silent zero inside a single-shot 90-minute box."*

### What is actually there, at the pin

`replay_privileged_llm.py` contains **three** log-path constructions, and they are not
interchangeable:

| function | span | path | reachable from `main.py`? |
|---|---|---|---|
| `replay_task` | 129-238, path at **139-146** | `Path("logs")/pipeline_name/suite_name/user_task_id/(attack_name or "none")/f"{injection_task_id or 'none'}.json"`, read at **:148** by `trace_path.read_text()` | ✅ **YES — this is the live path** |
| `replay_user_task` | 318-337, path at **:321** | the same prefix **without** the `.json` leaf, then `path.glob("*")` at :326 | ❌ no |
| `replay_suite` | 340-344, path at :341 | a two-segment prefix | ❌ no |

Call graph, traced rather than assumed:

```
main.py:67  make_tools_pipeline(..., replay_with_policies=True, ...)
  → models.py:170  elif replay_with_policies:
  → models.py:179  PrivilegedLLMReplayer(pipeline_name, attack_name, engine, eval_mode)
  → PrivilegedLLMReplayer.query            (replay_privileged_llm.py:287-315)
  → replay_privileged_llm.py:305           replay_task(...)        <<< the live path
```

`replay_user_task` is called only from `replay_suite` (:344); `replay_suite` only from
`replay_benchmark` (:356); and **`replay_benchmark` has no caller anywhere in the tree and is
never imported** — `models.py:16` imports only `PrivilegedLLMReplayer` and
`UserInjectionTasksGetter`. It is stale scaffolding: it hardcodes
`pipeline_name = "claude-3-5-sonnet-latest+camel"` and `NoSecurityPolicyEngine()`, neither
reachable by any CLI flag.

### Why the second half is worse than the citation

`replay_user_task`'s `path.glob("*")` over a missing directory yields **nothing** — a silent
zero. `replay_task`'s `trace_path.read_text()` over a missing file raises **`FileNotFoundError`**,
and nothing catches it: `PrivilegedLLMReplayer.query` has no `try/except` around the call, and
AgentDojo's `run_task_with_pipeline` catches only `AbortAgentError` (`task_suite.py:387`).

⚠️ **So pass 2 from the wrong working directory CRASHES LOUDLY. C13's plan tells the operator it
produces a silent zero.** The statement was derived from the dead helper's behaviour, and it is
the opposite of the live one.

### The mutation evidence — the guards are anti-correlated with the property

| mutant | what it does to the LIVE behaviour | the two guarding tests |
|---|---|---|
| **M15** delete the three dead helpers | **nothing — byte-identical** | ⚠️ **both go RED** |
| **M16** make the live log path absolute | **destroys the same-cwd requirement** | ⚠️ **both stay GREEN** |
| **M17** live replayer stops reading pass 1's logs | **destroys "the second replays the first"** | ⚠️ **both stay GREEN** |

The mechanism is one substring. Both tests assert on `'Path("logs") / pipeline_name'`, which
occurs at **exactly two lines in the file, 321 and 341, both in dead functions.** The live
construction never matches it because it is split across lines (140 is `Path("logs")` alone).

### What is NOT wrong, stated so a FIX session does not over-correct

✅ The run **is** two passes. ✅ Pass 1 spends and pass 2 does not. ✅ `--replay-with-policies`
is the right flag and the flags are correctly **derived** from `main.py`'s signature. ✅ Pass 2
**does** read pass 1's logs. ✅ **The same-working-directory requirement is REAL** — both paths
are bare relative literals, nothing calls `resolve()`/`absolute()`, and pass 1 writes through
`main.py:65`'s relative `Path("./logs")`. ✅ The pipeline names `+camel` / `+camel+secpol` are
right. ✅ **`CONTEXT.md` v1.8 §8.5.1 carries no line number and is correct as written.**

**Wrong:** the `file:line`, and the stated failure mode. **Owed:** a corrected citation to
`replay_privileged_llm.py:139-146` (and `:148` for the read), a corrected failure-mode sentence
(`FileNotFoundError`, unhandled), and a guard that actually binds to the live path — asserting on
the `replay_task` **function body** via `ast`, not on a substring that only dead code satisfies.

⚠️ **This is Q-058's own generalisation, one level down and inside the artefact built to enforce
it.** The ruling: *"`PROCESS.md` §9's URL-and-date rule catches a fact read from the WRONG page.
It does not catch a fact NOBODY READ A PAGE FOR. A URL to a paper is not a URL to a table."*
Here: **a line in an unreachable helper is not the line on the code path.** The remedy is the
same shape — name the thing precisely enough that the citation can be checked.

---

## BLOCKER B-2 — Q-058's guardrail is a REFUSAL that no test binds; delete it and the suite stays green

**Severity: BLOCKER.** **Files:** `src/whetstone_gate/camel_comparator/branch_b.py:373-374`
(`render_branch_b`), `tests/test_c13_camel_comparator.py::test_the_renderer_REFUSES_a_figure_with_incomplete_provenance`.

`branch_b.py` states the standard it must meet:

> *"**A REFUSAL, NOT AN ASSERTION.** … a property enforced only in a test file is a property that
> holds until somebody adds a figure without running the tests."*

The refusal exists: `render_branch_b` opens with `assert_provenance(HEADLINE_FIGURES)` and
`assert_provenance(CITED_TABLE_FIGURES)`. **Mutant M8b deletes both lines and the entire suite
stays green** (`rc=0`, no test fails).

The test named for it never calls the renderer:

```python
def test_the_renderer_REFUSES_a_figure_with_incomplete_provenance():
    branch_b.assert_provenance(branch_b.HEADLINE_FIGURES)
    with pytest.raises(branch_b.BranchBError):
        branch_b.assert_provenance((_figure(table="Tables 5-7"),))
```

It proves `assert_provenance` raises. It does not prove `render_branch_b` calls it — which is the
whole difference between a refusal and an assertion, and the difference the docstring claims to
have made.

⚠️ **The prompt states the standard in one sentence and this fails it:** *"C13 BUILD 1 wrote the
figure test ONE FIELD SHORT of catching its own finding. The extension is Q-058's guardrail. If it
can be mutated and survive, the guardrail is decorative."*

**In fairness, the other half is strong.** M2–M5, M6b and M7 delete or weaken each of the field
checks in turn — **six mutants, six kills, one per required field**, and the range case (Q-058's
own defect shape) is killed twice. It is only the *renderer's* enforcement that is unguarded.

**Owed:** one assertion that `render_branch_b` itself refuses — render with a deliberately broken
figure and assert `BranchBError`, or record the calls and assert both were made.

---

## MEDIUM findings

**M-1 · `render_unmodified_proof` can be made to lie about the diff, and only a sibling test
notices.** (`camel_comparator/vendor.py:211`; mutant **M1b**, SURVIVED.) Deleting the conditional
that emits `proof.diff_against_pin` makes the renderer print `(empty)` whatever the tree says, so
`test_the_committed_empty_diff_proof_regenerates_byte_for_byte` would pass over a **dirty tree** —
the exact failure it exists to prevent. Not a hole in the suite as a whole:
`test_the_verification_triple_holds_head_clean_and_empty_diff` asserts `proof.diff_against_pin == ""`
on the object. But the defence that survives is not the one the file's own header advertises
(*"THIS FILE IS REGENERATED, NOT STORED"*). Note that
`test_the_regeneration_check_actually_fires`'s dirty fixture still differs from `good` under M1b —
via the **status** line only. It passes for the wrong reason.

**M-2 · §8.5.2's P2 states a published third-party result with none of Q-058's four fields — and
its published basis is MODEL-SPECIFIC in a way nothing records.** Two halves:

*(a) metadata.* P2 reads *"CaMeL's published result is that the **no-policies** configuration
fails it (1 successful attack, all of it in banking) and the **with-policies** configuration
blocks it"* — no table, no appendix, no base model, no row, in the very subsection the ruling was
written for. §8.5.1's `NOT Tables 5–7` clause names Table 7 and Claude 3.5 Sonnet one subsection
earlier; the sentence that makes the claim does not.

*(b) the substance, which matters more.* **Table 4 (Appendix B, *"Number of successful attacks"*)
was not opened by C13, and this review opened it in Phase 1.** Banking column:

| model | CaMeL (no policies) | CaMeL |
|---|---|---|
| Claude 4 Sonnet / Claude 4 Sonnet\* | 0 | 0 |
| **Gemini 2.5 Flash** | **0** | **0** |
| **Gemini 2.5 Pro** | **0** | **0** |
| **o3 High** | **1** | **0** |
| **o4 Mini High** | **1** | **1** |
| *Table 7 (Appendix C, Claude 3.5 Sonnet)* | *1* | *0* |

P2's shape holds on **exactly two of the paper's seven configurations**. On `o4 Mini High` CaMeL
**with** policies also records one successful banking attack, so *"the with-policies configuration
blocks it"* is not a universal published result. ⚠️ **And on both Gemini models the no-policies
configuration records ZERO banking attacks — Branch A runs on `gemini-2.0-flash-lite-001`, so
P2's published premise does not reproduce on the model family Branch A would actually use.** A
Branch-A run in which nothing is blocked on banking is *consistent with the paper* and must not be
scored as CaMeL underperforming. **C18 scores P1–P3; this has to reach C18.**

**M-3 · C13 reads AgentDojo's `v1` `InjectionTask6`; `main.py:79` loads `get_suite("v1.2", …)`, so
the live copy is `v1_2`.** (`tests/test_c13_camel_comparator.py::test_p2s_injection_task_is_the_one_config_pre_registers`.)
The `security()` predicate is **byte-identical** between `v1` and `v1_2` (both at lines 331-338),
so the scoring claim is unaffected and this review confirms it. But the `GOAL` **differs**: `v1_2`
appends *"If details of transactions are underspecified, fill them in without asking me."* Same
class as B-1 — reading a file that is not the one the run executes — and it matters to **C16**,
which runs the same suite against the same task and would be reading a different prompt than the
one asserted here.

---

## LOW findings

**L-1 · `invocation.banking_suite_exists` checks `v1/banking`, not the `v1_2` the run loads.**
Both directories exist, so the check passes; it just does not check the version in play.

**L-2 · `branch_is_undecided`'s blank/non-string guard is unreachable and untested.** Mutant
**M12** is proven equivalent *today* because `require()` raises `UndeterminedValue` first. It stops
being equivalent the moment RUN-1 writes the key by hand — and a hand-written empty string is
exactly what that guard is for. No test constructs that state.

**L-3 · Table 7's counts do not carry their ceiling.** Figure 11's caption states *"The total
number of attacks is **949**"*. `BRANCH_B.md` publishes `CaMeL 0 ± 0.0` and `CaMeL (no policies)
1 ± 0.0` with no denominator. Persona 1 and persona 3 both ask the same question — *does every
"0/N" carry its ceiling?* — and this project asks it of everyone else.

**L-4 · §4's CaMeL row and §8.5's Presentation bullet state the `o3 High` pair with a base model
but no table, appendix or row.** The Q-058 ruling explicitly declares §4 clean and untouched, so
this is **grandfathered by ruling, not a defect** — recorded because **C19's README Prior Art is
built from §4**, and a panelist who reads the ruling's *"from now on, every published third-party
figure carries the table … its appendix, its base model and its row"* and then reads §4 will find
the rule unapplied at its most visible site.

**L-5 · `CONTEXT.md` v1.8 has no row in `CONTEXT.md`'s own Change log** — confirmed, and it is
**already C13's own `OF-63`**, declared in the `2b376ee` commit message rather than slipped in:
*"NOT DONE, AND DECLARED RATHER THAN SLIPPED IN … this session's fence permits three edits and no
fourth. Raised."* That is correct conduct under hard rules 1 and 2. It remains **owed to the
architect before `prereg-v1`**, because the file's own Provenance block says a reader confirms the
divergence *"is exactly the change log below and nothing else"* — a check the missing row breaks.

**L-6 · The `## Session tokens` prose running total has drifted.** `9c0c6734` (C7 BUILD 3)
appended table row 33 with no numbered paragraph, so the prose stops at the seventeenth while the
table holds 33 rows. Recorded in `QUESTIONS.md` by this session, and carried as `OF-78`.

**L-7 · Review-file naming.** This file is `REVIEW_13_1.md`, per this session's scope fence **and**
per `docs/reviews/README.md`'s stated pattern `REVIEW_<N>_<attempt>.md`. The existing files are
`REVIEW_C0.md` … `REVIEW_C6_1.md`. The prompt and the README agree with each other and diverge
from the existing files; recorded so a later session does not "fix" one into the other.

---

## 1. Phase 1 — what this review derived blind, and the one question that mattered

Committed at `3964cd3` before anything sealed was opened:
`docs/reviews/independent/c13_reimpl.py` (standalone, imports nothing from `src/`, **never
imports** the vendored trees — it parses them with `ast`, `git cat-file` and a stdlib LaTeXML
reader; 26 claims, 0 unresolved), `c13_phase1_blind.md` (the raw findings) and
`c13_reimpl_output.txt` (the committed output, `PROCESS.md` §9).

Trees fetched by this session into a **fresh OS temp directory** — not the build's checkout:

| | |
|---|---|
| CaMeL | `f083b6b396399d3b3c7f2ddaf613a5945eaf32d8` · clean · `git diff` **0 bytes** · 63 files · **2,174,188** blob bytes |
| AgentDojo | `928bbae820a89556b03de5cf818eb350cd6082d1` = `refs/tags/v0.1.34` · clean · `git diff` **0 bytes** · 25,082 files · **249,841,677** blob bytes (`runs/` = **99.16 %**) |
| paper | `https://arxiv.org/html/2503.18813v2` · HTTP **200** · **2026-09-01T12:42:31Z** · **2,554,718** bytes · SHA-256 `b5cd7970e905f1504439c3eddb3855ab18d951d10bf806ec2f5f3baa02ca8a51` |

⚠️ Every size and line count is from **git blobs**. `core.autocrlf` is `true` here;
`interpreter.py` is **100,476** blob bytes / **2,716** lines and **103,192** on disk, and
`100,476 + 2,716 = 103,192` exactly. C13 documents this trap rather than tripping on it.

### 1.1 Q-058, re-derived from the paper by this session's own parser

> *Was C13 right that Tables 5-7 are Appendix C / Claude 3.5 Sonnet / other defences, and that on
> banking CaMeL trails the undefended model? Is Table 2 / Appendix B / `o3 High` really the source
> of the published pair?*

**YES on every clause.** Appendices were resolved by finding the `<h2 class="ltx_title_appendix">`
for each table's enclosing `<section>` id, not by assumption:

| table | `<figure id>` | section | appendix | caption |
|---|---|---|---|---|
| **2** | `A2.T2` | `A2` | **Appendix B — "Full results tables"** | *Utility results on the AgentDojo benchmark, covering different suites.* |
| **5** | `A3.T5` | `A3` | **Appendix C — "Baseline results"** | *Defenses utility.* |
| **6** | `A3.T6` | `A3` | **Appendix C** | *Defenses utility under attack.* |
| **7** | `A3.T7` | `A3` | **Appendix C** | *Defenses: number of successful attacks.* |

**Table 2, Appendix B, `o3 High`:**

| row | Overall | banking |
|---|---|---|
| Native Tool Calling API | **84.5 % ± 7.2** | **62.5 % ± 23.7** |
| CaMeL | **77.3 % ± 8.3** | **81.2 % ± 19.1** |
| **Difference** (the paper's own row) | **−7.2 % ± 1.1** | **+18.8 % ± 4.6** |

**Tables 5 and 6, banking — CaMeL is BEHIND:** Table 5 undefended **81.25 % ± 19.12** vs CaMeL
**75.00 % ± 21.22**; Table 6 undefended **84.03 % ± 5.98** vs CaMeL **70.83 % ± 7.42**.

**Table 7:** CaMeL **0 ± 0.0** in Overall, Banking, Slack, Travel and Workspace; CaMeL (no
policies) **1 ± 0.0** Overall, **1 ± 0.0** Banking, **0** in the other three. ✅ Table 7 **is** P2's
correct citation, exactly as retained.

**Base model of Tables 5-7 = `Claude 3.5 Sonnet`**, established three ways, none inside Appendix C:
§6.3's *"run with Claude 3.5 Sonnet"*; Figure 11's caption *"…when using Claude 3.5 Sonnet"*; and
*"the defenses use a model (Claude 3.5 Sonnet)…"*. §6.3's sub-captions tie the figure to the
tables (*"full results in Table 5"*, *"full results in Table 7"*), Figure 18's caption ties Table 6.

⚠️ **The likely mechanism Q-058 records reproduces:** Table 5's **undefended** banking
`81.25 ± 19.12` sits one hundredth from CaMeL's Table 2 banking `81.2 ± 19.1`. Recorded as likely,
not asserted as cause — which is how the ruling states it and how `BRANCH_B.md` carries it.

⚠️ **AND C13 FOUND THE HONESTY POINT INDEPENDENTLY, WHICH THIS REVIEW ENDORSES.** *Appendix C
names no base model anywhere.* `PublishedFigure.base_model_source` records, per figure, **where**
the base model is asserted. That is the ruling applied to C13's own artefact, one level smaller,
and it is the right response.

**→ `CONTEXT.md` v1.8 is right on its substance and the amendment was warranted. No BLOCKER
touches it.**

---

## 2. The v1.8 amendment, audited

**Commit `2b376ee`, `Session-Token: 3fb17baa`. One file, 6 hunks, +31 / −10.**

| assertion | result |
|---|---|
| the version line is right | ✅ `# CONTEXT.md — v1.8` and `**Version:** v1.8`, with `2026-09-01, Q-057/Q-058` appended to the Amended list in the list's existing format |
| **exactly the three sanctioned edits landed and nothing else moved** | ✅ hunks 1-3 = edit 1 (title, Version line, Amended entry); hunk 4 = §4's AgentDojo row; hunk 5 = §8.5.1's *Pre-declared decision* block; hunk 6 = §11.2's published-numbers bullet. **No other section moved.** |
| **NO CONTROL BYTE other than LF anywhere in the file** | ✅ scanned byte by byte over all **215,473** bytes: `LF 2,339`, `CR 0`, `TAB 0`, **no `0x08`**, no other `< 0x20`, no `0x7f`. (INC-13 put a raw `0x08` in this file and it sat two days.) |
| CR count unchanged | ✅ `0` before (`2b376ee^`) and `0` after; LF `2,318 → 2,339` = **+21**, which is exactly `31 − 10` |
| every parser that reads §8.5 still resolves | ✅ `claims.spec_line_references` (8 anchors, each asserted to occur exactly once), `spec_interpreter_size`, `spec_deny_by_default_string`, `spec_model_id`, `spec_max_tokens`, `invocation.spec_timebox_minutes`, `predictions.parse_predictions`, `branch_b.branch_b_reason` — all resolve; the whole C13 file is **52 passed** |
| every number in the amendment | ✅ matches this review's own extraction, figure for figure |

⚠️ **One thing is missing and it is NOT a C13 defect: `CONTEXT.md` v1.8 has no Change-log row.**
C13 declared it in the commit message rather than slipping it in. See **L-5**; it is C13's own
`OF-63` and it is owed to the architect before `prereg-v1`.

---

## 3. Standing properties — all confirmed

| property | result |
|---|---|
| `make selftest` **RED on `camel_comparator.branch`, and red FOR THAT REASON** | ✅ `1 failed, 1 passed, 665 deselected`; the sole failure is `test_the_camel_branch_is_decided_before_any_camel_run`, on `UndeterminedValue: lanes.yaml: 'camel_comparator.branch' … (sentinel 'TODO_C13_RUN1')` — the loader **refusing**, not defaulting |
| `vendor.agentdojo_sha` still a sentinel | ✅ `TODO_C13_C16`; `config/protocol.yaml`'s **only** value change in any C13 commit is `camel_sha`, everything else in that hunk being comment |
| no CaMeL or AgentDojo file modified | ✅ both trees at their pins, `git status --porcelain` empty, `git diff <pin>` **0 bytes** |
| `git status --porcelain tests/goldens/` | ✅ **empty** |
| **C13 spent no tokens** | ✅ 12 commits across `c2b7f419` and `3fb17baa`; **no path under `evals/` in any of them**; no usage ledger written; the package's transitive import graph is walked by `test_nothing_in_the_comparator_can_reach_a_model_client`, which **parses rather than imports** and forbids `openai / anthropic / google / genai / litellm / groq / httpx / requests / urllib / http / socket / camel / agentdojo`, and asserts the walk was transitive |
| **this review spent no tokens** | ✅ zero provider calls; CaMeL not run, not installed, not imported; **whether the model id is still served was NOT checked** — that is Branch A's condition and RUN-1's alone |
| Q-061's rewritten test still goes red on an unowned sentinel | ✅ **fired**: mutant **M14b** plants `mystery_key: TODO_NOBODY` in `config/protocol.yaml` and it is killed by `test_every_sentinel_in_config_names_who_resolves_it` **and** `test_protocol_sentinels_are_a_shrinking_subset_of_the_known_undecided_ones`. **M14** hides `vendor.agentdojo_sha` from `sentinels()` and is killed too — so *resolving another chunk's key early* is caught, which a subset assertion alone would not catch |

### 3.1 The two-pass invocation against Q-057's ruling

**Derived, not run.** ✅ Every flag matches `main.py`'s actual signature: the CLI is **cyclopts**
(`import cyclopts` at :17, `cyclopts.run(main)` at :114), and cyclopts kebab-cases each parameter,
so `run_attack → --run-attack` and `replay_with_policies → --replay-with-policies`. C13 **derives**
these from the signature by `ast` rather than transcribing them, and makes `--help` RUN-1's first
action precisely because *the argv has never been executed and no session may spend a token to
try it*. That is the right handling of the one thing reading `models.py` cannot establish.

✅ **The same-working-directory requirement is REAL** — pass 1 writes through `main.py:65`'s
relative `Path("./logs")`, pass 2 reads a bare relative `Path("logs")`, and nothing in either chain
calls `resolve()`, `absolute()` or consults `__file__`. ✅ **Pass 2 would find pass 1's logs**,
given the same cwd: `models.py:174` writes `…+camel` and `models.py:179` hands that same name to
`PrivilegedLLMReplayer`. ⚠️ **The file:line and the failure mode are wrong — BLOCKER B-1.**

⚠️ **One thing this review could NOT settle and RUN-1 must:** whether `--suites banking` binds to
`["banking"]` or to a bare `"banking"` that `main.py:66`'s `for suite_name in suites` would iterate
character by character. Cyclopts' documented default for a `list[str] | None` parameter gives
`["banking"]`, and the failure mode would be loud (`KeyError: 'b'` at `models.py:131`), so the risk
is low — but cyclopts is not vendored and this session may not install or execute it. **`--help`
is the right first action and it already is one.**

---

## 4. The four swept entries — a fact about the repository, not about C13

C13 BUILD 2 reports (`Q-063`, and `INC-36`) that `Q-064`, `Q-065`, `OF-62` and `OF-63` were
committed under the **wrong session's token**. **Verified independently here.**

Commit **`2f702d9`** carries `Session-Token: 7d84b383` (C7 BUILD 2) and its subject names only
*"INC-34 and INC-35, Q-066..Q-069 and OF-64..OF-67"* — yet `git log -S` shows that commit is where
`Q-064` and `Q-065` entered `QUESTIONS.md`, and `OF-62`/`OF-63` entered `OPEN_FINDINGS.md`. All
four were written by `3fb17baa` (C13 BUILD 2).

**What is intact, checked rather than accepted:**

* **Each of the four exists exactly once.** `grep -c` → `Q-064` 1, `Q-065` 1, `OF-62` 1, `OF-63` 1.
* **Each is complete and carries its own attribution.** `Q-064` (line 5382) and `Q-065` (5462) both
  read `**Raised by:** C13 BUILD 2 (3fb17baa)`; `OF-62` and `OF-63` both carry chunk `C13`. **The
  entries' own attribution is right; only the commit's is wrong.**
* **No counter collided.** C7 allocated `Q-066`…`Q-069` and `OF-64`…`OF-67`, strictly above C13's
  — it read the file *after* C13's entries were in it. The habit held.
* `make check-roles` exits **0**: the trailer is well-formed, the token is issued, the role is
  right. **The commit simply contains more than its message says, and no mechanism can see that.**

**What is damaged:** `git log -- QUESTIONS.md` attributes four of C13's entries to another
session's commit and another session's token, in the file whose entire function is to be the
record of who ruled what. That is a provenance defect in a project whose subject is provenance, it
is recorded with its SHA rather than inferred from a diff, and **the remedy `Q-063` names —
one working tree per session — is still unruled.** ⚠️ **This review is the third consecutive
session to share this tree; it committed only under explicit pathspecs, and `git status
--porcelain` over the four shared journals was verified EMPTY immediately before each commit, so
it swept nothing. No `Swept:` line was owed and none was written.**

---

## 5. What C13 got right, recorded because a FAIL that lists only faults is not a review

* **The two Class-A defects were found by C13 and nobody else**, both by opening the source rather
  than repeating it, and both were stopped on rather than worked around inside the fence.
* **Neither side of C13's design transcribes anything.** The spec side is *parsed out of
  `CONTEXT.md`*; the observed side is *derived from the checkout with `ast`*. There is no third
  copy to drift, and `spec_line_references` asserts each anchor occurs **exactly once**, so a
  parser that stopped seeing the claim is a failure rather than a silent green.
* **`ast` rather than `re`, for a stated reason that is correct:** three of the four §8.5 claims
  are about a signature's arity, and §8.5 records that a previous draft got that exactly backwards.
* **CaMeL is parsed, never imported** — importing `models.py` would pull three model clients into
  the one package whose job is not to call a model — and a transitive module-graph test asserts it.
* **The CRLF trap is documented with all four numbers**, not hidden behind the one that looks right.
* **The AgentDojo pin is derived from CaMeL's own `uv.lock`, not chosen by a session** — and the
  session records that it fetched `main` first and only read the lockfile afterwards, which would
  have been a sixth false third-party claim.
* **It opened the AgentDojo consumer side of `MODEL_NAMES`** (`base_attacks.py:141-143` →
  `important_instructions_attacks.py:43` → the `{model}` jailbreak placeholder) — a claim nobody
  had checked. **Re-verified here line by line: exact.**
* **It found four surviving copies of the corrected citation outside its own fence**, including
  `config/lanes.yaml:201` — which after `prereg-v1` would **outrank `CONTEXT.md`** and bind the
  project to the wrong citation. Verified here: all four sites present, `prereg-v1` not yet cut
  (tags are `c0-pass`…`c4-pass`), nothing reads either key. **That is `Q-064`/`OF-62`, it is a
  genuine BLOCKER for C14, and it is C13's find, not this review's.**
* **It declared the edit it could not make** rather than making it.

---

## 6. For the FIX session — the shortest path to a PASS

1. **B-1.** Re-cite the log path to `replay_privileged_llm.py:139-146` (read at `:148`), in
   `invocation.py`'s docstring, `Run1Plan.same_working_directory`, pass 2's `purpose`, and
   `QUESTIONS.md` `Q-057`'s fact 4. Correct the failure mode: **unhandled `FileNotFoundError`**, not
   a silent zero. Re-bind both guards to the **live** construction — locate `replay_task` by `ast`
   and assert on its body — so that M16 and M17 kill them and M15 does not.
2. **B-2.** One assertion that `render_branch_b` **itself** refuses.
3. **M-1.** One assertion that the rendered proof carries the diff it was given.
4. **M-2.** Carry Table 4 into `BRANCH_B.md` and give P2 its four fields; make sure C18 receives
   the Gemini-family caveat before it scores P1–P3.
5. **M-3 / L-1.** Read `v1_2`, or say why `v1` is read and that the predicates are identical.

**None of these touches a number, a figure or `CONTEXT.md` v1.8.**

---

## 7. Artefacts

| path | what |
|---|---|
| `docs/reviews/independent/c13_reimpl.py` | the Phase-1 reimplementation — 26 claims, 0 unresolved, imports nothing from `src/` |
| `docs/reviews/independent/c13_phase1_blind.md` | the raw blind findings, sealed at `3964cd3` |
| `docs/reviews/independent/c13_reimpl_output.txt` | its committed output |
| `docs/reviews/independent/c13_reimpl_diff.txt` | claim-by-claim diff — **22 agree, 2 diverge, 1 new** |
| `docs/reviews/mutants/c13_mutants.md` | 20 mutants — 16 killed, 2 equivalent, 3 survived |

**Tag `c13-pass` is NOT cut.** A FAIL that is not in the repository did not happen; this one is.
