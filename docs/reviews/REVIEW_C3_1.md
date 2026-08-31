# REVIEW_C3_1 — C3, τ² adapter A: the enumeration, the control and T-FP

**SESSION-TOKEN:** `a66c389d` · **Role:** REVIEW (attempt 1) · **Chunk:** C3
**Review type:** `full` — personas 1 **and** 2 · **Date:** 2026-08-31
**Built by:** `da356dbb` (C3 BUILD). **This session did not build any part of it and fixed nothing.**
**Concurrency:** may have overlapped C2's review as pair **P-03**. Disjoint fence; nothing of that
session's was read or written, and this session's mutation run is pinned in a clone for that reason.

## VERDICT — **PASS**

**Zero BLOCKER findings.** One MEDIUM, five LOW, three INFO. `c3-pass` cut.

The chunk's whole job is to reproduce, from a third-party checkout, a set of numbers the
specification asserts — and **every one of them reproduces, independently, by a different method,
with zero divergence in either direction**: all six sub-counts of `CONTEXT.md` §11.1, both
partitions id by id, the `reward_basis` census for all three domains, and the forty pre-registered
T-FP ids **in order**. The two things a reviewer can most easily be fooled by here — a scan that
passes over nothing, and an import walk that proves a claim about code we never call — were both
fired red by hand. Eleven mutants ran; ten died; the semantics-preserving control lived.

---

## 0. The evidence this verdict rests on, stated first

**The vendored tree, at BOTH ends of the session — the external-answer-key claim rests entirely
on it:**

```
START  git -C vendor/tau2-bench rev-parse HEAD  -> a2c024725189473d2d7cea3a5cfdbcc67478e41f
       git -C vendor/tau2-bench status --porcelain -> (empty)
END    git -C vendor/tau2-bench rev-parse HEAD  -> a2c024725189473d2d7cea3a5cfdbcc67478e41f
       git -C vendor/tau2-bench status --porcelain -> (empty)
```

The mutation run never wrote to it: it copied `src/`, `data/tau2/domains/` and `.git/HEAD` into a
throwaway clone and SHA-256-verified each copied file byte-identical first.

**Which tree every measurement loaded (INC-17):** `whetstone_gate.__file__` was printed on every run
in this session — the live repository for the suite runs, and
`…\scratchpad\mut\tree\src\whetstone_gate\__init__.py` under `PYTHONPATH` for all thirteen mutation
runs. No number below comes from a run that did not say.

**Suite counts, live tree, at the end of this session:**

| command | result |
|---|---|
| `pytest tests/test_c3_tau2_enumeration.py -q` | **39 passed** |
| `pytest -q -m "not operator_gate" --ignore=tests/test_c1_review_probes.py` | **219 passed, 1 skipped, 2 deselected** (215 before this review's 4 probes) |
| `pytest -q` (nothing excluded) | **2 failed, 227 passed, 1 skipped** |
| `python -m whetstone_gate.tasks test` (`make test`) | **1 failed, 226 passed, 1 skipped, 2 deselected** |
| `python -m whetstone_gate.tasks check-roles` | **17 passed, 0 failed, 4 n/a — OK** |

⚠️ **Both red tests are outside C3 and neither is this review's to close.**
`test_c1_review_probes.py::test_section_0_states_its_own_quoted_line_count_correctly` is C1's open
**FAIL** (F-R2), owned by C1's FIX session. `test_lanes_operator_placeholders.py::test_the_camel_branch_is_decided_before_any_camel_run`
is an `operator_gate` that fails until RUN-1 decides the CaMeL branch on 31 August; `make test`
deselects it by design. **C3's own module is green in every configuration.**

**No frozen artefact is contradicted, and the reason is that none exists yet.** `git tag -l` returns
**`c0-pass` only** — `probe-v1` and `prereg-v1` do **not** exist and `PROTOCOL.md` has not been
written. So `config/protocol.yaml` was still editable when C3 added to it, `make check-prereg`
correctly reports NOT-YET-FROZEN, and the sort ruling of 2026-08-31 is **pre-freeze disambiguation,
not post-hoc selection**. Stated rather than skipped, because "no frozen artefact is contradicted"
would otherwise be a sentence that costs nothing.

---

## 1. Q-020's substitute for a reimplementation — the independent derivation

C3 reimplements nothing of ours; its expected values are Sierra's files at a pinned SHA, external by
construction. Q-020 therefore substitutes an independent re-derivation of the same numbers by a
different method. **`docs/reviews/independent/c3_enumeration.md` was written and committed at
`e89f63c` before a single C3 file was opened**, and the diff is
`docs/reviews/independent/c3_enumeration_diff.txt`.

My method differed from C3's deliberately: an `ast` decorator scan **plus a runtime
`__tool_type__` / `__mutates_state__` cross-check** (the one C3 declined to commit), reading raw
JSON rather than Sierra's pydantic models, and taking the census over all three domains.

| | mine (blind) | C3 | |
|---|---|---|---|
| airline | 50 total · 7 empty · 17 read-only · **24** must-not-write · 26 write | identical | ✅ |
| retail | 114 total · 2 empty · 8 read-only · **10** must-not-write · 104 write | identical | ✅ |
| combined | **34 of 164**, 130 write, every partition sums | identical | ✅ |
| empty + read-only ids | listed in full, both domains | identical, id for id | ✅ |
| `reward_basis` airline | `[DB, COMMUNICATE]` × 50 | identical | ✅ |
| `reward_basis` retail | `[DB, NL_ASSERTION]` × 112, `[DB]` × 2 | identical | ✅ |
| `reward_basis` telecom | `[ENV_ASSERTION]` × 2253, `[ENV_ASSERTION, ACTION]` × 32, **DB in zero** | identical | ✅ |
| write tools | airline 6, retail 7, from the decorator | identical | ✅ |
| T-FP, 40 ids | listed in full | identical **in order**, and identical to `config/protocol.yaml` | ✅ |

**Divergences: none.** §11.1's *"The spec's 34/164 figure is exactly right"* is now derived four
times independently, and this is the fourth.

Two further §11.1 third-party claims re-verified at source at the pin, because *four* false ones
have already reached this specification: `docs/evaluation.md:122-126` carries the `db_reward = 1.0
iff …` sentence quoted **complete and unaltered**; and `EvaluationCriteria.reward_basis`'s
`default_factory` really is `[RewardType.DB, RewardType.COMMUNICATE]`, so C3's
`TAU2_DEFAULT_REWARD_BASIS` is τ²'s value and not ours. Both hold.

---

## 2. The sort rule — my choice, recorded blind, and whether the ruling was needed

**My rule, written down before I looked at C3's:** *ascending bytewise (code-point) order on the
task `id` as a string, within each domain, first 20 of each.* Reasons, in order: `Task.id` is `str`
and every id in `tasks.json` is a JSON string, so bytewise is the type's own order and needs no
coercion the spec never mentions; **`int(id)` raises on all 2,285 telecom ids**, so a numeric rule is
not even total over τ²'s id space; and a stranger regenerating the sample from the pin should have
the instruction with the fewest hidden premises.

**C3's committed rule is the same rule.** ✅

**Was the ruling needed? Yes, and here is what it is worth in ids** — measured from the blind side
before I knew the answer:

| domain | bytewise ∆ numeric | only bytewise | only numeric |
|---|---|---|---|
| airline | **4 of 20 differ** | `35, 37` | `7, 8` |
| retail | **28 ids differ — 14 of 20 replaced** | `100–109, 110–113` | `2–9, 16–21` |

Two competent readers of §13.4's unqualified *"after sorting"* would have shared **6 of 20** retail
tasks. §13.4 as originally worded was **under-specified**, and had this been settled after a number
was seen it would have been textbook post-hoc selection. It was not: `prereg-v1` does not exist.
**The finding here is on the specification, not on C3** — C3 found the ambiguity, raised it, and
implemented the ruling, which is the behaviour hard rule 1 asks for.

**One thing C3 got right that a reasonable build would have got wrong.** The two 20-id lists collide
on the bare strings `11`, `14` and `15`, so a **flat** 40-element list of unqualified ids would hold
only **37 distinct values** and `set()`-ing it would lose three tasks silently. C3 committed them
**keyed by domain** and recorded the shape as a Class B deviation. I flagged this risk blind, before
seeing the file; the file already handles it.

---

## 3. Persona 1 — the denominator, and the competence control (prompt §2e)

The 34 must-not-write tasks **are** the externally-authored attacker-competence control
(`CONTEXT.md` §11.1(b)), so the asymmetry that matters is: **an unclassifiable action must not
default its task INTO the 34.**

**It does not. The refusal is real and it fires.** `enumerate_domain` raises `EnumerationError`
before any classification if any action names a tool the domain's toolkit does not define, and
**mutant M7** — which disables exactly that refusal — was **killed**. Verified, not read.

**Every partition sums, in the code and in the tests**, and both are checked against a number parsed
back out of `CONTEXT.md` rather than transcribed. **Mutant M2 is the proof that the sub-counts are
really checked**: it collapses empty into read-only, leaves the headline **34 unchanged**, and is
still killed by `test_the_must_not_write_split_reproduces_from_the_pinned_sha`.

**Two smaller things, both checked.** All nine "empty" tasks carry a literal `[]` — none is `null`
and none is missing — so the empty branch is exercised by real data. And `get_tasks()`'s default
`"base"` split **is** the whole file (`split_tasks.json`: 50 and 114), so the 164 denominator is the
same however the tasks are loaded.

**The `requestor` half of C3's claim is where the record overreaches — see F-5.**

---

## 4. The db_reward non-use (prompt §2c) — fired red by hand

**Does the walk walk `db_reward`'s own closure, or all of τ²?** Its own: it starts at
`tau2.evaluator.evaluator_env`, which I confirmed at source is where `db_reward` is computed
(`evaluator_env.py:125-131`, `:332-338`). It reaches **24** τ² modules and **zero** text-generation
clients.

**Can it go red? Yes — I fired it myself, twice over.**

* Pointed at `tau2.evaluator.evaluator_nl_assertions` by my own independent walk: **`litellm` on the
  path**, plus `tau2.utils.llm_utils`.
* **Mutant M8** repoints `DB_REWARD_MODULE` at that module inside the harness:
  `test_the_db_reward_path_reaches_no_text_generation_client` **FAILS**. Killed.

**Two ways the walk could have lied, both checked and both clean.**
`_closure` silently `continue`s on a `tau2.*` name that resolves to no file. I re-ran the walk
recording those: **126 unresolved names on the db_reward path, 126 of them `from <real module>
import <symbol>`, and ZERO real modules dropped.** And `_imports` uses `ast.walk`, so a **deferred**
`import litellm` inside a function body would still be seen — verified on a control fixture. Both
are now kept probes (`tests/test_c3_review_probes.py`).

**The two cited source lines, re-verified at the pin** (persona 1's third-party rule, and this
project has withdrawn four such claims): `evaluator_nl_assertions.py:121` is exactly
`assistant_message = generate(` with `model=DEFAULT_LLM_NL_ASSERTIONS,` on 122; `config.py:24` is
`DEFAULT_LLM_NL_ASSERTIONS = "gpt-4.1-2025-04-14"`. **Both correct.** §11.1's sentence stands.

**And the honest half is asserted rather than glossed**: `test_importing_any_tau2_module_loads_a_model_client_through_the_package_init`
states in the repository that importing *any* `tau2.*` module pulls `litellm` in through
`tau2/__init__.py`, so *"no model client is ever loaded in our process"* would be false and is not
what the project claims. That test is the reason this section can be believed.

---

## 5. The no-reimplementation scan (prompt §2d) — non-vacuous three ways

1. **It fires on a planted reimplementation** — `test_the_grader_scan_fires_on_a_planted_reimplementation`, a synthetic fixture. ✅
2. **The stripper did not eat the file** — `test_the_docstring_stripper_did_not_eat_the_adapter` asserts the stripped source still contains `def enumerate_domain` and `def classify_task` and no longer contains the prose word `Sierra`. So the scan is not reporting PASS over an empty string. ✅
3. **And, added by this review because a synthetic fixture is not the real package: mutant M9** plants a genuine `scored_reward()` doing `hashlib.sha256(...).hexdigest()` **inside `enumerate.py` itself**. `test_the_adapter_does_not_reimplement_the_hash_comparison` **FAILS**. Killed. ✅

---

## 6. The ids-are-strings guard (prompt §2b) — can it fail? Yes

`config/protocol.yaml` carries all 40 T-FP ids and all 34 control ids **quoted**, and they match my
blind derivation in order. **Mutant M6** unquotes one (`["11",` → `[11,`) — the exact YAML slip the
file's own comment warns about. Three tests go red, including
**`test_every_committed_id_is_a_string`**. The guard is real.

*(Mechanically the failure arrives as the `EnumerationError` `_committed_ids` raises rather than
through that test's own `assert`, which by then cannot be false. The protection is genuine and the
test does go red; the assertion itself is decorative. Recorded as INFO-2, not a finding.)*

---

## 7. The declined ast-vs-runtime cross-check (prompt §2f) — judged

**Is the fast path sound without it?** At the pin, yes, and I did not take C3's word for it: my blind
Phase-1 pass **ran the runtime cross-check itself** and it agrees exactly — `ast == runtime` on the
full tool set and on the WRITE subset, in both domains, with `mutates_state=True` exactly equal to
the WRITE set and zero overrides. So classifying by `tool_type` rather than `mutates_state` changes
nothing at this SHA either.

**Is the reason recorded where a reader finds it?** Yes, in three places: `enumerate.py`'s module
docstring, `test_the_adapter_imports_no_tau2_module_and_therefore_no_model_client`'s docstring, and
`docs/sessions/c3-build-1.txt` §12(d) with the measured ~22 s and the `litellm` cost. That is
adequate.

**But the trade has a cost, and it is F-3.** The runtime check is precisely what would catch the one
decorator spelling the `ast` parser misreads. The decision is defensible; the residue is a LOW
finding and this review has guarded it from the other side rather than leaving it implicit.

---

# FINDINGS, severity-ranked

## F-1 · **MEDIUM** · a guard on the competence control that no test can distinguish from an unrelated one
`src/whetstone_gate/tau2/enumerate.py:281-287` · `tests/test_c3_tau2_enumeration.py:243-254`

**Mutant M11 SURVIVED the entire suite.** Replacing `tool_types`'s *"this parser cannot read this
decorator"* `raise` with a silent skip leaves **215 passed, 1 skipped, 2 deselected — byte-for-byte
the baseline.** The branch's own message says a misread write tool *"silently moves a task into the
must-not-write control, and that control is a published number"*, and yet nothing detects its
removal.

**Why.** Its only test feeds a fixture whose **sole** decorated `def` is the unreadable one, so under
the mutation `found` is `{}` and the *other* refusal — `"no decorated tools were found at all"` —
raises instead. `pytest.raises(EnumerationError)` carries no `match=`, so the two are
indistinguishable.

**Why MEDIUM and not BLOCKER.** The production guard is intact; the mutant is genuinely
**equivalent at the pinned SHA** (all 30 airline+retail decorators are plain
`@is_tool(ToolType.MEMBER)`); the pin is separately enforced by a test that **can** go red; and the
vendored tree is verified unmodified at both ends. **No number C3 publishes is wrong.** What is
wrong is that a one-token regression on the guard protecting the externally-authored control
survives the whole suite, which is exactly what `PROCESS.md` §5.4 forbids.
**Remedy (one line, for whoever next touches C3):** `match="cannot read"`, or add a readable
`@is_tool(ToolType.READ)` def to the fixture so `found` is non-empty under the mutation.
→ **OF-26**

*Closing note, same family:* under **M1**, `test_write_tools_are_read_from_tau2s_own_decorator` did
not fail, because its own re-derivation keys off `tau2_enum.WRITE_TOOL_TYPE` — the constant M1
mutates — so both sides moved together. Seven other tests killed M1, so nothing is unguarded, but a
test that imports the constant it checks is nearer hard rule 3's line than it reads.

## F-2 · **LOW** · `report()` prints `DIFFERS` on a drifted pre-registration and still exits 0
`src/whetstone_gate/tau2/enumerate.py:625, 686-690`

`report()`'s final block compares the committed ids against the checkout and prints `MATCH` or
`DIFFERS` per domain — then `return 0` unconditionally. An operator running the module and checking
its exit status would see success over a drifted pre-registration.
**Mitigated, which is why it is LOW:** `report()` is not wired into `tasks.py` or the `Makefile`,
so it gates nothing, and `test_the_committed_selections_still_match_the_pinned_checkout` enforces
the equality inside `make test` (proven by M4, M5, M6, M10).
→ **OF-27**

## F-3 · **LOW** · the decorator parser silently reads the keyword form as `READ`
`src/whetstone_gate/tau2/enumerate.py:275-287`

`tool_types` reads the type from `decorator.args[0]` and treats *no positional argument* as
`ToolType.READ`. So `@is_tool(tool_type=ToolType.WRITE)` — legal, identical in effect, and a form
`toolkit.py`'s own signature invites — is recorded **READ**, and its tasks would land **inside the
34**. The same line's `getattr(decorator.func, "id", None)` also skips an attribute-qualified callee
(`@toolkit.is_tool(...)`) entirely. Both contradict the docstring's *"a decorator whose argument is
not a plain `ToolType.MEMBER` attribute is a refusal, not a silently-dropped tool."*
**LOW, not MEDIUM:** the shape does not occur at the pin, the pin is asserted, and the tree is
verified unmodified — so it is latent, not live. It could not be shown by a mutant because
demonstrating it means editing `vendor/`, which is read-only to every session.
**Guarded by this review from the other side:** `tests/test_c3_review_probes.py::test_no_pinned_domain_toolkit_uses_the_keyword_form_of_the_tool_decorator`
now asserts neither shape occurs, so a benchmark bump cannot introduce one silently. The parser
itself is C3's to widen.
→ **OF-28**

## F-4 · **LOW** · the "PURE" banner is false for eight functions below it
`src/whetstone_gate/tau2/enumerate.py:152, 251-253`

Line 152 says *"THE SHELL — everything that touches the filesystem lives here and nowhere else"* and
line 252 says *"PURE — from here down, every function takes its data as an argument."* Below it,
`enumerate_tau2`, `telecom_reward_basis_census`, `telecom_reward_basis_includes_db`, `tfp_quota`,
`committed_must_not_write_ids`, `committed_tfp_ids`, `_committed_ids` and `report` all read the
filesystem — `cfg.load` is explicitly uncached, so `tfp_quota()` and `_committed_ids()` open
`config/protocol.yaml` on **every** call.
**Hard rule 8's substance is honoured** — every real computation (`tool_types`, `classify_task`,
`enumerate_domain`, `sort_task_ids`, `tfp_selection`, `reward_basis`, `action_names`) does take its
data as arguments, and these eight are thin wrappers on the wrong side of a self-imposed comment.
Hence LOW. But C5 depends on C3, and a C5 session trusting that banner could call `tfp_quota()`
from inside episode logic believing it pure.
→ **OF-29**

## F-5 · **LOW** · the build record calls 692 actions "assistant actions"; the field is absent
`docs/sessions/c3-build-1.txt:97-98`

The record states *"zero name a `user` requestor (142 airline and 550 assistant actions, 0 user)"*.
The counts are right and the conclusion is right — but **no airline or retail reference action
carries a `requestor` key at all**. The union of their keys is
`{action_id, arguments, compare_args, info, name}`. They are `"assistant"` only through
`Action.requestor`'s pydantic `default="assistant"`, and this project reads raw JSON and never loads
that model. **No code and no test computes the census the sentence reports**; `action_names()` never
looks at `requestor`. So *"0 user"* is true because the field is absent, not because it was
surveyed — a distinction this project holds other people to.
**Not a wrong number, and not a wrong conclusion**, hence LOW rather than MEDIUM.
**Made checkable by this review:** `tests/test_c3_review_probes.py::test_no_reference_action_carries_a_requestor_field_at_all`
pins the real key set and the 142/550 counts, and goes red if a bump ever ships a user-requested
action — which in a dual-control benchmark would put a **user-side write inside the 34**.
→ **OF-30**

## F-6 · **LOW** · a cited constant's name is pinned, its quoted value is not
`tests/test_c3_tau2_enumeration.py:562`

`test_the_two_source_lines_the_specification_cites_are_still_there` asserts
`config_lines[23].startswith("DEFAULT_LLM_NL_ASSERTIONS = ")`. §11.1 quotes the **value**
(`"gpt-4.1-2025-04-14"`), and that half is unpinned: τ² could bump the judge model and the test
would stay green while the specification's quotation went stale. One `== ` away from closed.
→ **OF-31**

---

## INFO — recorded here, not in `OPEN_FINDINGS.md`

**INFO-1 · the bytewise retail sample is the tail of the file, and `RESULTS.md` should say so.**
Bytewise order puts **14 of retail's 20 T-FP tasks in ids `100–113`**, plus `0, 1, 11, 13, 14, 15`.
That is a legitimate consequence of a pre-registered rule and **not a defect** — but the T-FP number
is a false-positive rate, and a reader deserves one sentence saying the sample is the first 20 of a
bytewise sort, not a random draw. Airline also contributes **20 of its 26** write tasks (77%) against
retail's **20 of 104** (19%). For C18.

**INFO-2 · `test_every_committed_id_is_a_string`'s own assertion cannot be false**, because
`_committed_ids()` raises on a non-string before returning. The behaviour is protected and the test
does go red (M6) — via the exception, not the assert. Cosmetic. *(The same test takes the
`enumeration` fixture and never uses it.)*

**INFO-3 · `reward_basis()`'s fallback returns an UNSORTED tuple** while the live path returns
`tuple(sorted(...))`. This looks like an inconsistency and is in fact what makes
`test_reward_basis_falls_back_to_tau2s_own_default_and_never_reaches_it_here` able to detect the
fallback being reached — the two normal forms cannot collide. Correct as written; worth a comment
saying so, since the next reader will "fix" it.

---

## Already-open findings deliberately NOT re-raised

**OF-08 / `REVIEW_C0_2` I-01 — `make test` does not run green from a clean clone, and the failures
are inside `tests/test_c3_tau2_enumeration.py`.** They are collection errors for a missing
`vendor/tau2-bench`, which `.gitignore` excludes (`vendor/*/`). This is real, it is already tracked,
and **it is not C3's to fix**: the cause is **Q-010**'s unruled Class A default putting the vendored
checkout outside the repository, and the remedy is an architect ruling plus `vendor/MANIFEST.md`'s
fetch commands in the README (C19's done-when already carries it). Re-raising it against C3 would
move a finding to the wrong owner. **Named here so it is visibly not overlooked.**

---

## What a PASS required, item by item

| Requirement | Result |
|---|---|
| independent derivation agrees on all six sub-counts | ✅ zero divergence |
| …on both partitions | ✅ id for id, both domains |
| …on the `reward_basis` census | ✅ all three domains, every census sums |
| …on the 40 T-FP ids | ✅ in order, and equal to `config/protocol.yaml` |
| vendored tree unmodified at both ends | ✅ SHA and empty porcelain printed at both |
| every mutant killed or proven equivalent | ✅ 10 killed; M11 survives, **equivalence proven at the pin** and raised as F-1 |
| the control survived | ✅ 215 passed — identical to baseline; the run is valid |
| zero BLOCKER findings | ✅ |
| no reported figure contradicts a frozen artefact | ✅ **none is frozen** — `git tag -l` is `c0-pass` only; `probe-v1`, `prereg-v1` and `PROTOCOL.md` do not exist |
| `docs/reviews/ARCHITECT_CHECK_1.md` exists (§11) | ✅ |

**PASS. `c3-pass` cut.**
