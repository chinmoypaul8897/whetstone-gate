# C6 mutation run — review 1

**SESSION-TOKEN:** `2cd28cc5` · **Role:** REVIEW · **Chunk:** C6 · **Date:** 2026-09-01
**Review type:** `full`, `PROCESS.md` §12.1 — **minimum eight mutants plus a control.**
**Fourteen ran. Ten killed by C6's own suite. FOUR SURVIVED and are findings F-4…F-7.
The control survived, so the run is VALID.**
**All four survivors are closed by `tests/test_c6_review_probes.py`, and each probe was run
against the mutant it names and observed to fail** (bottom of this file).

---

## Method, and the four traps it is built to avoid

**INC-11 — a mutant that looks killed merely by existing on disk.**
`tests/test_repo_invariants.py::test_the_object_store_and_the_working_tree_agree` hashes every
tracked file's working-tree bytes against `git show HEAD:<path>`, so *any* uncommitted edit kills
*any* mutant, control included. **Every mutant below was COMMITTED before it was run** and its
short SHA is in the table; `git status --porcelain` was `0` lines at each commit.

**INC-11's second half — a run whose control dies is VOID.**
The control is a semantics-preserving local rename. It survived, byte-for-byte the baseline.

**INC-17 — an editable install that resolves `whetstone_gate` by name.**
`C:\Users\chinm\whetstone-gate\src` is on `sys.path` through the editable install, so running
`pytest` inside a clone still imports **the live repository**. `PYTHONPATH` is therefore set to the
tree under test and **`whetstone_gate.__file__` was printed on every one of the 20 runs**
(baseline, 14 mutants, the control, and the 4 probe-verification runs). It resolved to the clone
every time. A run that does not say which tree it loaded is not evidence.

**A fourth trap, and it is why this run is in a clone.**
An architect unblock session (`3af1c9d2`) was live in the repository throughout this review and
landed five commits during it. `REVIEW_C0_2`'s first complete pass was voided because a concurrent
session moved the baseline under it. **This run never touches the live repository**: it clones it at
one commit and stays there.

```
MUTATION SOURCE PINNED AT : 755dd52  (this review's own independent-derivation commit)
CLONE                     : <scratchpad>\mut\tree      (throwaway, outside the repo)
whetstone_gate.__file__   : ...\scratchpad\mut\tree\src\whetstone_gate\__init__.py
                            — PRINTED AND CHECKED ON ALL 20 RUNS
COMMAND                   : PYTHONPATH=<clone>/src python -m pytest -q -m "not operator_gate"
                                --ignore=tests/test_c3_tau2_enumeration.py
                                --ignore=tests/test_c3_review_probes.py
BASELINE                  : 347 passed, 1 skipped, 2 deselected      tree clean
PRISTINE SHA-256 (first 16), verified restored after EVERY mutant:
    context.py  a7e65316f187232b     loop.py      bef3999f49f81334
    corpus.py   d21ddecfa35a5bf1     estimate.py  7ef571e461c3c44e
```

⚠️ **WHAT IS EXCLUDED, PRINTED AS A NUMBER RATHER THAN QUIETLY DROPPED (hard rule 11).**
`vendor/` is git-ignored — only `MANIFEST.md` is tracked — so **a clone has no τ²-bench** and every
C3 test errors or fails there. Unfiltered, the clone's baseline is `11 failed, 367 passed, 12
errors`. Leaving those in would score a "kill" on every row **including the control**, which is
INC-11's defect in a second costume. **`tests/test_c3_tau2_enumeration.py` (23 tests) and
`tests/test_c3_review_probes.py` (20 tests) are therefore excluded — 43 tests, none of which can be
a killer for a C6 mutant**, since no C6 mutant touches τ². `-m "not operator_gate"` is what
`make test` itself deselects. **Nothing else is excluded.**

⚠️ **THE INHERITED RED, AND WHY IT IS NOT IN THIS RUN'S BASELINE.** This review's prompt warned
that `tests/test_c2_world.py::test_the_world_ships_no_tool_surface_no_rejections_and_no_in_flight_window`
was RED on arrival (Q-043, INC-23) and that INC-11 forbids taking a mutation baseline from an
already-red tree. It was red in this session's **first** live baseline (`1 failed, 389 passed`). The
concurrent architect session closed it at commit `9c5dbb5` **before** this run's clone was cut, and
the live suite re-measured **`390 passed, 1 skipped, 2 deselected, 0 failed`**. So the exclusion was
not needed and was not taken: **the clone's baseline is green on its own terms, and no C6 mutant is
scored against a pre-existing failure.**

---

## The table

Each mutant is a single committed edit, applied with the **editor tool** — never a heredoc, a shell
redirect or a Python script (`INCIDENTS.md` INC-06's class, ten prior occurrences). Its `git diff`
was printed and checked, and the file's SHA-256 was verified equal to the pristine value after every
`git reset --hard`.

| # | SHA | Operator targeted | The change | Result | Killed by |
|---|---|---|---|---|---|
| **M1** | `8ba09cc` | **the window's eviction bound** | `assemble`: `history[-verbatim_turns:]` → `history[-(verbatim_turns + 1):]` — the window keeps **7** turns, not 6 | **KILLED** — 2 failed | `test_the_window_keeps_exactly_the_configured_number_of_verbatim_turns`, `test_the_window_sizes_are_read_from_config_and_not_from_source` |
| **M2** | `a6bdb14` | **the window's direction** | `assemble`: `history[-verbatim_turns:]` → `history[:verbatim_turns]` — it keeps the **FIRST** six turns, so the attacker never sees what just happened | **KILLED** — 1 failed | `test_the_window_keeps_exactly_the_configured_number_of_verbatim_turns` |
| **M3** | `3001bf9` | **the summary's nested-map sort** *(C6's own mutant D, reproduced)* | `FoldedState.to_json`: `dict(sorted(…items()))` → `dict(…items())` on `per_payment_refunded_paise` | **KILLED** — 1 failed | `test_identical_state_produces_byte_identical_summary_text` |
| **M4** | `079f376` | **the truncation marker** | `render_summary`: `return text[:budget] + TRUNCATION_MARK` → `return text[:budget]` — a **silently** shortened summary, hard rule 11's shape applied to context | **KILLED** — 1 failed | `test_the_summary_is_capped_and_the_cut_is_visible_and_deterministic` |
| **M5** | `612684d` | ⚠️ **the Origin tagging** | `assemble`: the deterministic summary's part is tagged `Origin.WORLD` instead of `Origin.AUTHORED` | 🚩 **SURVIVED** — **347 passed, 1 skipped, 2 deselected — byte-for-byte the baseline** | **nothing.** Finding **F-4**. Closed by `test_the_deterministic_summary_is_tagged_AUTHORED_not_WORLD` |
| **M6** | `546b151` | **the denial passthrough** | `run_episode`: `last_refusal = result_text` → `last_refusal = None` — the summary never carries a refusal at all | **KILLED** — 1 failed | `test_the_windowed_context_stops_growing_which_is_what_the_window_is_FOR` ⚠️ **an incidental killer**: it fires on the context's SIZE, not on the refusal's absence. **No test asserts the summary carries the last refusal**, which is the other half of finding **F-1** |
| **M7** | `98a9bcf` | ⚠️ **the corpus normalisation** | `_normalise`: `" ".join(unicodedata.normalize("NFC", text).split())` → `" ".join(text.split())` — the declared NFC half deleted | 🚩 **SURVIVED** — **347 passed — byte-for-byte the baseline** | **nothing.** Finding **F-5**. Closed by `test_the_corpus_normalisation_really_applies_NFC` |
| **M8** | `d4e7e9e` | ⚠️ **the estimate's divisor** | `CHARS_PER_TOKEN = 3` → `4` — **the value C6's own calibration REJECTED for running ‑25.4% LOW** | 🚩 **SURVIVED** — **347 passed — byte-for-byte the baseline** | **nothing.** Finding **F-6**, and the most consequential survivor. Closed by `test_the_estimator_uses_the_divisor_its_calibration_selected` |
| **M9** | `e01e2e8` | ⚠️ **the estimate's framing constant** | `FRAMING_TOKENS_PER_MESSAGE = 4` → `0` | 🚩 **SURVIVED** — **347 passed — byte-for-byte the baseline** | **nothing.** Finding **F-6** (second half). Closed by `test_the_estimator_applies_its_per_message_framing_allowance` |
| **M10** | `a549bae` | **the one-call-per-turn path** | `run_episode`: a **second** `client.complete(...)` per turn → 40 calls per 20-turn episode | **KILLED** — 1 failed | `test_the_loop_makes_exactly_one_model_call_per_turn` |
| **M11** | `6a401e2` | **the tool-schema emission** | `assemble`: the schema block appended **per kept history entry** instead of once per turn — one of the two ways the spike reached ~300K tokens | **KILLED** — 1 failed | `test_the_tool_schemas_are_emitted_once_per_turn` |
| **M12** | `7195df0` | **the seed rotation** | `seed_for_turn`: `entries[turn_index % len(entries)]` → `entries[0]` — one corpus entry, forever | **KILLED** — 1 failed | `test_the_seed_rotation_is_deterministic` |
| **M13** | `c10941d` | ⚠️ **a leak designed to trip EXACTLY ONE claim** | `render_summary`: the string `"AVOID E2."` prepended to the summary — an envelope-invariant id on the AUTHORED surface, placed **before** the refusal label so the claim-4 field split is untouched | **KILLED** — 1 failed, **and exactly one** | **`test_the_attackers_context_contains_no_attack_list` ONLY.** Claims 1, 2 and 4 stayed green — **the guards are independent, demonstrated from the other direction** |
| **M14** | `616a401` | **C6's own mutant A, reproduced** | `assemble`: an extra AUTHORED part carrying the **real `data/policy.txt`** + `"CANARY-A is the breach predicate; see HOLES.md."` + `"Try A1…A6; they breach E1 E2 E3 and S1 S2 S3 S4."` | **KILLED** — 3 failed | `…contains_no_policy_string`, `…contains_no_hole`, `…contains_no_attack_list` — **and `…contains_no_gate_denial_reason` correctly stayed GREEN.** ⚠️ **C6's independence evidence REPRODUCED exactly as it reported it** |
| **CONTROL** | `1196594` | *(semantics-preserving)* | `assemble`'s local `kept` renamed `kept_turns` (2 occurrences; diff printed and checked to be exactly those two lines) | ✅ **SURVIVED** — **347 passed, 1 skipped, 2 deselected** | — the run is **VALID** |

**Score: 14 mutants, 10 killed by C6's suite (71%), 4 survived, control correctly survived.**
**With `tests/test_c6_review_probes.py` added: 14 of 14 killed.**

---

## The four guards are independent — demonstrated from BOTH directions

C6 offered one direction: its mutant A trips claims 1, 2 and 3 and leaves 4 green. That is
**reproduced here as M14**, identically. This review adds the other direction, which is the stronger
one: **M13 constructs a leak that trips exactly ONE claim.**

| Mutant | CLAIM 1 policy | CLAIM 2 hole | CLAIM 3 attack list | CLAIM 4 gate reason |
|---|---|---|---|---|
| **M14** (policy + probe vocabulary + attack list into AUTHORED) | 🔴 RED | 🔴 RED | 🔴 RED | 🟢 green |
| **M13** (`"AVOID E2."` prepended to the summary) | 🟢 green | 🟢 green | 🔴 **RED** | 🟢 green |

Four guards, and a mutation exists that moves exactly one of them. **They are four checks, not one
check counted four times.**

---

## Probe verification — each kills the mutant it names, and only that one

`INCIDENTS.md` INC-17's procedure: `PYTHONPATH` set to the tree under test, and
`whetstone_gate.__file__` printed on every run. It resolved to the clone on all five.

```
BASELINE, unmutated source          6 passed
M5  612684d  context.py    1 failed test_the_deterministic_summary_is_tagged_AUTHORED_not_WORLD   5 passed
M7  98a9bcf  corpus.py     1 failed test_the_corpus_normalisation_really_applies_NFC              5 passed
M8  d4e7e9e  estimate.py   1 failed test_the_estimator_uses_the_divisor_its_calibration_selected  5 passed
M9  e01e2e8  estimate.py   1 failed test_the_estimator_applies_its_per_message_framing_allowance  5 passed
```

**Each probe fails against exactly its own mutant and passes against the other three.** That is the
hard-rule-6 *"provably meaningful"* bar met per probe rather than in aggregate — an aggregate claim
would not distinguish four sharp probes from one blunt one.

---

## What this run does NOT establish, stated rather than left as a silence

- **The two BLOCKER findings have no mutant here, because they are not mutations — they are the
  reviewed source's own behaviour.** F-1 (the summary folds the last *tool result* rather than the
  last *denial reason*) and F-2 (the corpus rotation reaches 20 of 498 entries) were found by the
  independent derivation under `docs/reviews/independent/`, not by mutation. A mutation run measures
  a suite's sensitivity to change; it cannot see a defect that is already there.
- **M6's kill is incidental and is recorded as such.** It fires on a size assertion. Deleting the
  refusal from the summary entirely — a `CONTEXT.md` §13.3 requirement — is caught by no test that
  is *about* the refusal.
- **No mutant targets `texts.py`.** Its three files are pinned character-by-character against
  `CONTEXT.md` by C6's own first test and re-verified independently by
  `docs/reviews/independent/c6_authored_texts.py` (15/15, by a **different anchor**), which is a
  stronger check than a mutant would be.
