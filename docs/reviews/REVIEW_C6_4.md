# REVIEW_C6_4 — C6, THE ATTACKER LOOP. Adversarial review, attempt 4, after FIX 3.

**SESSION-TOKEN: `ca0dd160`** · **Date:** 2026-09-02 · **Personas:** evaluation-integrity + code
**Token row:** `daefb31` (row 45) · **Phase-1 seal:** `11193bd` · **Reviewed at:** `bd2107f`
**I did not build this chunk, I did not fix it, and I did not review it before.**

---

## VERDICT — **FAIL**

### ⚠️ **ZERO BLOCKERS. ALL SIX OF `REVIEW_C6_3`'s SURVIVORS ARE KILLED, BY THE RIGHT TESTS.**
### **What fails it is SEVEN NON-EQUIVALENT MUTANT SURVIVORS on C6's own surface — and THREE of them carry the FAIL: two are `REVIEW_C6_3`'s OWN `N15` and `N13` classes, unclosed in COPY 2 of the guard, and the third is `OF-108`'s class at the other end of the same loop.**

`docs/reviews/README.md`: *"PASS requires ALL of: … **every mutant killed or proven equivalent** …
zero BLOCKER findings."* This session's prompt states the bar again and states it **both ways**:
*"if FIX 3's new surface holds under your own mutants, that is a PASS and you should cut the tag."*

**It did not hold. 28 mutants ran; 16 died; 5 are equivalent with the boundary named; 7 survive and
are not equivalent.** That, and only that, is the FAIL.

⚠️ **THE BEHAVIOUR IS RIGHT, AND THAT IS SAID FIRST BECAUSE IT IS TRUE.** The four blindness claims
hold over the package's **actual assembled bytes** at five turns, measured by this session's own
**118-needle, ten-family** corpus with a **clean-surface control at 0 of 118**. The door is open —
the probe note reaches the attacker on the WORLD surface and never on the authored one, in every
turn. All six of REVIEW 3's survivors die to tests that name the property they attack, not to a
byte-count fixture. `_sole_killer` is real and has a self-test that fires it **in both directions**.
`OF-110`'s C6 half fires on all five dynamic forms **and on a sixth this review invented**. Copy 2
of the guard is now fired at leaks, and deleting its scan goes red.

| | |
|---|---|
| **BLOCKERS** | **0** |
| **MEDIUM** | 5 |
| **LOW** | 7 |
| **Mutants** | **28 run · 16 KILLED · 5 EQUIVALENT · 7 NON-EQUIVALENT SURVIVORS** |
| **The six survivors N4/N9/N12/N13/N14/N15** | **all six KILLED** |
| **Pre-committed polarities (Phase 1)** | **55 probes · 39 held exactly · 11 partial · 3 MISSES in the fix's favour · 1 held AGAINST the fix · 1 miss of my own** |
| **The four blindness claims, my method, my shapes** | **0 AUTHORED hits of 118 needles** at turns 1, 6, 7, 12, 20 |
| **Clean-surface control** | **0 of 118** — the needles are about leaks, not about the spec |
| **`make test`, measured twice by me** | **774 passed, 1 skipped, 2 deselected — 0 FAILED, both times** |
| **`make selftest`** | RED on `camel_comparator.branch` — **not C6's** |
| **`make check-roles`** | **17 passed, 0 failed, 5 n/a, exit 0** |
| **SPEND** | **ZERO PROVIDER MODEL CALLS. `evals/` does not exist.** |
| **Tag `c6-pass`** | **NOT CUT** |

⚠️ **THIS REVIEW IS NOT MANUFACTURING A FOURTH FAIL, AND IT SAYS SO WITH NUMBERS RATHER THAN WITH A
SENTENCE.** Of 55 polarities sealed at `11193bd` before any fix commit was opened, **three of the six
rows that predicted failure were wrong, and all three were wrong in the fix's favour** — `_sole_killer`
survives neither of the two weakenings I predicted it would survive, and `OF-110`'s scan catches a
dynamic form I predicted would escape it. **Four of the seven survivors are named here as NOT carrying
the FAIL**, with the reason, rather than counted to make seven look worse than three. And §14 states
plainly what the architect would need to decide to overrule this verdict.

---

## 0. THE EVIDENCE, AND WHICH TREE EVERY NUMBER CAME FROM

`whetstone_gate.__file__` printed for every run (INC-17):

* the working tree — `C:\Users\chinm\whetstone-gate\src\whetstone_gate\__init__.py`
* the mutation clone — `C:\Users\chinm\AppData\Local\Temp\claude\…\scratchpad\c6r4\tree\src\whetstone_gate\__init__.py`

**Every mutation ran in that fresh OS temp clone. This repository was never mutated.**

**SPEND: ZERO. NO PROVIDER MODEL CALL WAS MADE BY THIS SESSION.** `evals/` **does not exist** in this
repository — stated as the precise fact rather than as *"`evals/usage/` is empty"*, which would be
true of a directory that existed and was empty. **No C6 commit touches an `evals/` path**: measured
across all six of FIX 3's / Night Run A's commits (`51f0624`, `df741d4`, `f03d359`, `6bcc15a`,
`ee01e0c`, `0fcfab2`) — zero. Every model here is a mock.

| path | what |
|---|---|
| `independent/c6_review4_criteria.md` | **Phase 1, sealed at `11193bd`** — 55 probes, each with its polarity pre-committed |
| `independent/c6_review4_reimpl.py` | **Phase 1, sealed** — the scoped reimplementation; imports nothing from `src/` |
| `independent/c6_review4_reimpl_output.txt` | its output |
| `independent/c6_review4_probes.py` | Phase 2 — the sighted probes, importing the sealed shapes **from** the Phase-1 file |
| `independent/c6_review4_probes_output.txt` | its output |
| `mutants/c6_mutants_4.md` | 28 mutants, five equivalence proofs with their boundaries, **and C6 FIX 3's own owed fourteen** |

### 0.1 THE SEAL, AND MY LEAKS, DECLARED

`OF-80`'s ruling: *"on a RE-review, PHASE 1 IS BLIND TO THE FIX, NOT TO THE FINDINGS."* Sealed at
`11193bd`, before any of `51f0624 df741d4 f03d359 6bcc15a ee01e0c`, before
`docs/sessions/nightrun-a-1.txt`, and before the current `src/whetstone_gate/attacker/` or any
`tests/test_c6_*.py` was opened.

**`OF-104`…`OF-114` and `STATUS.md`'s C6 row were read at `2be75b1`** — `REVIEW_C6_3`'s own commit,
**the finding without the disposition** — because `6bcc15a` filled the dispositions and reading them
is reading the fix through a different file. `INC-53` and the `PROGRESS.md` entry were deferred to
Phase 2. ⚠️ **`INC-54` WAS read, and that is the one place this boundary was drawn looser than
REVIEW 3 drew its own**: it was written by the fix session, but this prompt directs Phase 1 to it
**for the token-row count**, and it is about the token table rather than about the fix's code. It is
named in the criteria file rather than left to be inferred.

⚠️ **AND THE LEAK `OF-80` NAMES IS REAL.** This prompt itself told Phase 1 that the scan has **three
layers**, that a **`_sole_killer`** helper exists, that **copy 2 had never been fired at a leak**,
that two mutants were declared **EQUIVALENT** and named which two, and that `OF-110`'s half landed as
a **source-text scan** over five dynamic forms. **Phase 1 knew the SHAPE and not the CONTENT.** What
that permits is exactly what the criteria file does — and **six of its rows predicted failure or
escape**, so it could not be a wish list.

### 0.2 ⚠️ THE VERDICT RULE WAS WRITTEN BEFORE ANY MEASUREMENT

`independent/c6_review4_criteria.md` §0.2, sealed: a **mutant survivor on the fix's own new code,
non-equivalent and exhibited → FAIL**; a **needle escaping the guard while the four claims still hold
over the real bytes → MEDIUM, not FAIL** (which is how `REVIEW_C6_3` graded the identical shape as its
`M-1`); an escape **inside the folded-state JSON → not a C6 finding**, because §8.6 puts that object
on the authored surface and **C7's ledger fills it**; a repository-wide limit → **routed, not
charged**; **zero survivors → PASS and cut the tag.** Every grade below is that rule applied.

---

## 1. THE PRE-COMMITTED POLARITIES — 55 PROBES

Sealed at `11193bd`. Full table in `independent/c6_review4_criteria.md`; measurements in
`independent/c6_review4_probes_output.txt` and `mutants/c6_mutants_4.md`.

| # | subject | expected | measured |
|---|---|---|---|
| **P-01…P-12** | the six survivors, and each fixture's exhibit | KILLED / HOLD | ✅ **all twelve held** — §2 |
| **P-13** | `_sole_killer` carries both halves | HOLD | ✅ `assert matched` **and** `len(matched) == len(findings)` |
| **P-14** | `_sole_killer` with the exclusivity half deleted | ⚠️ predicted **SURVIVOR** | ⚠️ **KILLED — I was wrong, §3.1** |
| **P-15** | `_sole_killer` inverted | KILLED | ✅ **KILLED**, 18 failures |
| **P-16** | `_sole_killer` accepting any layer | ⚠️ predicted **SURVIVOR** | ⚠️ **KILLED — I was wrong, §3.1** |
| **P-17** | one layer per fixture, measured | HOLD | ✅ enforced by the helper, and `R-01` proves the enforcement load-bearing |
| **P-18** | **the clean-surface control**, 118 needles | 0 hits | ✅ **0 of 118** on the package's own unleaked surface, at five turns |
| **P-19…P-27** | nine families planted on the authored surface | each CAUGHT | 🟡 **PARTIAL: 118/118 in the refusal VALUE, 118/118 as a new-line RESIDUE, 72/118 in the LABEL** — §4.2 |
| **P-28** | a gate reason in a LABEL matching no ceiling, no id, no arm digit | ⚠️ predicted **ESCAPE** | ⚠️ **ESCAPES, both copies — the prediction held, §4.3** |
| **P-29** | a ceiling / a paraphrase inside a folded-state VALUE | ⚠️ predicted **ESCAPE, not a finding** | ⚠️ **ESCAPES, and it is correct behaviour — §4.4** |
| **P-30** | **`OF-104`'s own two shapes, caught in both copies** | HOLD | 🔴 **DID NOT HOLD.** `arm 2S` is caught in both; `"STATE SO FAR (this arm runs a live judge): "` — `OF-104`'s own third exhibit — **escapes both. §5** |
| **P-31** | the two copies share no import edge, by AST | HOLD | ✅ neither imports the other; the 5 textual occurrences are prose |
| **P-32** | copy 2 fired independently at my shapes | HOLD | ✅ copy 2 fires on 6 of the 9 shapes tested; the 3 it misses are the 3 copy 1 misses (§5) |
| **P-33** | `OF-104`'s scan deleted from **COPY 2** | KILLED | ✅ **KILLED**, 3 failures |
| **P-34** | `OF-104`'s scan deleted from **COPY 1** | KILLED | ✅ **KILLED**, 5 failures |
| **P-35** | the two copies' vocabularies differ | HOLD | ✅ 31 words vs 5; different subtraction routes |
| **P-36** | `SM-1`'s equivalence proof | ⚠️ predicted **UNSOUND** | 🟡 **PARTIAL — I found the separating input I predicted, and the conclusion I drew from it does not follow. §7** |
| **P-37** | `SM-5`'s equivalence proof | SOUND | ✅ **SOUND**, and it matches `REVIEW_C6_3`'s own `N10` precedent |
| **P-38 / P-39** | five dynamic forms: AST silent, text scan fires | HOLD | ✅ **all five, both halves** |
| **P-40** | a split target name `"open" + "ai"` | ⚠️ predicted **ESCAPE** | ⚠️ **it FIRES — I was wrong, §6** |
| **P-41** | the text scan can go red | HOLD | ✅ `R-16` kills it, 5 failures |
| **P-42** | the four claims over the real assembled bytes | 0 AUTHORED hits | ✅ **0** at turns 1, 6, 7, 12, 20 |
| **P-43** | the must-reach control | T/T/F/F | 🟡 **the probe NOTE is T/F at every turn ✅; `pay_CANARYRECON` is T/T at turn 20 — and the cause is MY fixture, §8.2** |
| **P-44** | ≥1 explained FULL-surface hit | HOLD | 🔴 **0 FULL hits, and that is a defect of MY needle design, not of the package. §8.3** |
| **P-45 / P-46 / P-47** | `OF-112` / `OF-113` / `OF-114` judged | OPEN / OPEN / CLOSABLE | ✅ **all three held** — §9 |
| **P-48** | my prior: ≥1 new-surface survivor | ≥1 | ⚠️ **7, of which 3 carry the FAIL** — §3 |
| **P-49…P-55** | regressions and standing properties | HOLD | ✅ **all seven** — §11 |

**Three of the six rows that predicted failure were wrong, and all three were wrong in the fix's
favour.** One row that predicted success — **P-30** — failed against the fix, and it is §5.

---

## 2. 🟢 THE SIX SURVIVORS — **ALL KILLED, AND BY THE RIGHT TESTS**

Re-run by this session, control first, in a fresh clone at baseline **111 passed**.

| survivor | operator | verdict | killed by |
|---|---|---|---|
| **N4** | `crossing()`'s `> target` → `>= target` | ✅ **KILLED**, 2 failed | `test_the_crossing_is_STRICTLY_over_the_target_and_is_pinned_at_the_boundary_BOTH_WAYS` |
| **N9** | the relative-import resolution deleted | ✅ **KILLED**, 2 failed | `test_the_import_scan_fires_on_a_RELATIVE_import_too[×2]` |
| **N12** | LAYER 3, the residue catch-all, deleted | ✅ **KILLED**, 4 failed | `test_LAYER_3_is_the_SOLE_killer_of_authored_text_carrying_no_policy_word[×4]` |
| **N13** | `refusal_lines != 1` → `< 1` | ✅ **KILLED**, 3 failed | `test_the_denial_line_COUNT_is_the_SOLE_killer_of_a_summary_with_more_than_one[2, 3, 5]` |
| **N14** | the `value != generic` block deleted | ✅ **KILLED**, 4 failed | `test_the_denial_equality_is_the_SOLE_killer_of_a_value_that_leaks_nothing_else[×3]` |
| **N15** | LAYER 1's exemption widened to the state LINE | ✅ **KILLED**, 3 failed | `test_LAYER_1_scans_the_state_LABEL_and_exempts_only_the_state_JSON[×3]` |

⚠️ **THE COUNT IS NOT THE POINT; THE KILLERS ARE.** `REVIEW_C6_3`'s complaint about the label class
was that *"they die on one test … because a longer label changes the summary's CHARACTER COUNT.
Nothing in that kill is about the label's content."* **Not one of these six kills is of that shape.**
Every killer names the property its mutant attacks.

**And the fixtures are derived, not written.** `N4`'s boundary base is `target − 8 × per_read`,
computed from `config/` — **17,616**, which this review recomputed independently
(`6 × (⌈2887/3⌉ − ⌈240/3⌉) = 5,298`; `60,000 − 8 × 5,298 = 17,616`) and which agrees with `OF-108`'s
exhibit exactly. `N15`'s three cap shapes are read from `config/` in three formattings — bare paise,
Indian-grouped rupees, comma-grouped paise — **so neither the number nor the rendering is what is
pinned.** `N15` additionally has **the other side**: a cap value that is *legitimately* inside the
state JSON must **not** fire, so a session that repaired the red by deleting the exemption meets a
named assertion. That is `INC-50`'s *"fire it at BOTH"* applied without being asked.

⚠️ **THE HARNESS'S OWN FIRST RUN WAS INVALID AND IS RECORDED RATHER THAN QUIETLY REPLACED.** Its
restore step ended with `git checkout -- <path>`, which restores from **HEAD** — and HEAD held the
mutation, because the harness commits it. Every mutant re-applied its predecessor and the failure
counts ran **2, 4, 8, 11, 15, 18** instead of **2, 2, 4, 3, 4, 3**. Caught by the monotone count,
fixed, the clone reset to the sealed content and re-baselined at 111 before anything was re-measured.
**A mutation harness whose restore is defeated by its own commit reports every mutant as KILLED, which
is the flattering direction** — and this review would have published six kills it had not measured.

---

## 3. 🔴 THE SEVEN NON-EQUIVALENT SURVIVORS

Full table, every exhibit and every equivalence boundary: `mutants/c6_mutants_4.md`.
**22 new-surface mutants ran. 10 killed, 5 equivalent with the boundary named, 7 survive.**

### 3.1 First, what did NOT survive — because it is the fix's strongest work

⚠️ **`_sole_killer` SURVIVES NOTHING.** Phase 1 predicted (P-14, P-16) that weakening it would
survive, on the reasoning that *a suite whose fixtures are all single-layer cannot notice the
exclusivity clause going away — unless a self-test exists.* **The self-test exists**, and it is
better than the one I would have asked for:
`test_the_sole_killer_helper_REJECTS_a_shape_that_two_layers_catch` fires the helper at
`"STATE SO FAR [DENIED once]: "` — a shape caught **twice**, by LAYER 2's `denied` and by the new
surface scan's `DENIED` — asserts `pytest.raises(AssertionError, match="caught by more than one
layer")`, **and then fires it in the other direction** so it cannot be satisfied by a helper that
always raises (`INC-50`). Three separate mutations of the helper — dropping the exclusivity clause,
dropping the identity clause, and making it a no-op — **all die on that one test**; a fourth,
inverting it, dies with 18 failures.

**C6 FIX 3 found this itself, as its own survivor `SM-2`, by mutating its own new surface.** That is
the 2c ruling earning its keep, and it is the single strongest thing in this fix.

### 3.2 ⚠️ THE THREE THAT CARRY THE FAIL

| id | severity | the exhibit on which HEAD and the mutant differ |
|---|---|---|
| **R-14** | **MEDIUM** | **`N15` / `OF-107`'s CLASS, IN COPY 2.** Widen copy 2's exemption from the state **JSON** to the whole state **LINE**: with `STATE_LABEL = "STATE SO FAR (5000000): "` over a real 20-turn episode, **HEAD returns 40 findings and the mutant returns 0**, and **all 111 tests stay green**. Copy 1 got `test_LAYER_1_scans_the_state_LABEL_and_exempts_only_the_state_JSON` with three cap formattings *and* the other-side test; **copy 2 got neither** — measured over the file, `exempts_only_the_state_JSON` is absent and no copy-2 test plants a cap in `STATE_LABEL`. **Remedy: one parametrised case, in copy 2, mirroring copy 1's.** |
| **R-15** | **MEDIUM** | **`N13` / `OF-111`'s CLASS, IN COPY 2.** Copy 2's `refusal_lines != 1` → `< 1`: a summary carrying **two** recognisable last-denial lines gives **HEAD 20 findings and the mutant 0**, suite green. Copy 1 got a three-count fixture (2, 3, 5); copy 2 got none. **Remedy: one two-denial-line episode through copy 2.** |
| **R-20** | **MEDIUM** | **`OF-108`'s CLASS AT THE OTHER END OF THE SAME LOOP.** `crossing()`'s `range(0, turn_budget + 1)` → `range(0, turn_budget)`. Exhibit, **all values positive and realistic**: a series with `full_listing_chars = 1600` (a *paginated* read, not the 12-payment listing), `displaced = 240`, `base_tokens = 5,521` → `tokens_at(19) = 57,277 ≤ 60,000 < tokens_at(20) = 60,001`. **HEAD returns `20`. The mutant returns `None`.** `None` makes `crossover_note()` print *"NO number of full-listing reads inside 20 turns crosses 60,000"* — **a sentence instead of a number**, which the method's own docstring calls *a different finding for C14*. `OF-108` pinned the **target** boundary in both directions and `R-19` shows the **k = 0** end is pinned; **the `turn_budget` end is pinned by nothing.** **Remedy: one fixture at that base.** |

⚠️ **WHY THESE THREE AND NOT A JUDGEMENT CALL.** Two of them are the **same two classes REVIEW 3
failed C6 on**, reappearing in the copy of the guard that FIX 3 itself identified as under-fired.
`N-M1b` / `OF-123` is precisely the finding that *copy 2 had never been fired at a leak at all*; FIX 3
closed that for `OF-104`'s shape and **did not extend `N13`'s or `N15`'s fixtures to copy 2**, so the
same defect it named survives, one class over, in the same function. That is a defect with a
one-fixture remedy each, not a preference.

### 3.3 THE FOUR THAT DO NOT — named, so the count is not padded

| id | severity | why it does not carry the FAIL |
|---|---|---|
| **R-18** | LOW | `_dynamic_reach_findings`'s `rglob` → `glob`. Exhibit: a dynamic import in `attacker/sub/reach.py` — HEAD 2 findings, mutant 0. **Latent**: `attacker/` is flat today and every positive-control package is flat. |
| **R-08** | LOW | `assert len(summaries) == 1` → `>= 1`. Exhibit: a **second** AUTHORED part carrying `STATE_LABEL` — HEAD's parser assertion fires loudly, the mutant proceeds silently. **No code path builds two.** |
| **R-12** | LOW | LAYER 2b over `values_scan` instead of `scan`. Exhibit: `idempotency_keys_seen = ("arm 2S",)` — HEAD `["2b 'arm 2S'"]`, mutant `[]`. **HEAD is the stricter one, and the surface is the folded state, which C7's ledger fills.** This review pre-committed at `11193bd` (P-29) that an escape there is not a C6 defect. |
| **R-05** | LOW | LAYER 2's system-prompt subtraction, all occurrences → one. Exhibit: the §8.6 prompt present **twice** — HEAD `[]`, mutant `["vocab 'limits'"]`. ⚠️ **The mutant is STRICTER and WRONG**: it reports the prompt's own tradecraft words as a leak. **HEAD is correct.** |

---

## 4. THE FOUR BLINDNESS CLAIMS — RE-DERIVED BY MY METHOD, MY SHAPES, WITH A CONTROL

`Q-031`'s enforcement clause is the substitute for the golden C6 does not have: *"C6's REVIEW must
INDEPENDENTLY RE-DERIVE the four 'never sees' assertions and the summary's determinism **BY ITS OWN
METHOD**. A divergence is a finding."*

### 4.1 The corpus, derived from the spec and not from the fix's list

**Ten families, 118 needles**, built in `independent/c6_review4_reimpl.py` from *"what does a GATE
know that §10.1 forbids the attacker to learn?"* and from `CONTEXT.md` §8.6/§8.6a/§10.1 and
`config/protocol.yaml` alone:

| family | n | spanning |
|---|---|---|
| F1 cap values in unusual renderings | 27 | bare paise, western grouping, **Indian lakh grouping** (`2,00,000` — the form §8.6 itself prints), rupees, `Rs`/`INR`/`₹`, `.00`, **`2 lakh`, `half a lakh`, `0.5 lakh`, `2L`** |
| F2 clause ids | 14 | `P1`…`P7`, `clause P4`, `P1-P6`, **`P1–P6` with `policy.txt`'s own EN DASH**, lowercase `p7`, `P2/P3` |
| F3 policy **paraphrases** | 7 | an LLM judge asked for *"a reason"* writes a paraphrase, never a quote — **none carries a digit or an id** |
| F4 arm identity | 12 | `arm 1`…`arm 4`, `arm 2S`, **`Arm Four`**, `the no-gate control`, **`the kernel`**, **`the gate judge`** |
| F5 hole descriptors | 14 | `CANARY-A`, `CANARY-B`, `HOLES.md`, `EXEMPTION:`, `in-flight window`, `window width 2`, `void threshold`, the two `config/` key names |
| F6 verdict vocabulary | 8 | `DENIED`, `ALLOWED`, `INDETERMINATE`, `declared obligation with no result` |
| F7 answer-key vocabulary | 15 | `A1`/`A3`/`A5`/`A6`, `E1`–`E3`, `S2-amt`, `S3`, `S4`, **`Rejected by Razorpay itself`**, **`Gate-dependent?`** — §6's two answer-key columns |
| F8 extra folded-state fields | 8 | §8.6 fixes the folded state's **six** fields exactly; a seventh is defender state |
| F9 config key names | 6 | a reason that names the key it read |
| F10 the seven clause **bodies**, read at run time from `data/policy.txt` | 7 | so a leak that **renumbered** the clauses could not evade an id-only scan, and so a drifted transcription in **my** file cannot weaken the scan |

⚠️ **F7 DELIBERATELY EXCLUDES the four harm words §8.6's GOAL string carries** — *over-captures,
excess refunds, early settlements, duplicated refunds* — and F5 excludes the bare words *exception*,
*limits*, *special* and *refuses*, every one of which is in the TRADECRAFT paragraph.
**`REVIEW_C6_2` had to re-derive its list after firing on the zero-turn context.** This is that lesson
applied before the fact, and the control below is what makes it checkable rather than a promise.

### 4.2 The measurement, over the package's ACTUAL assembled bytes

Over `run_episode`'s real 20-turn output, with the real seed-2001 world payloads from
`whetstone_gate.world`, a corpus part offered every turn, and a **growing** folded state (`OF-82`'s
lesson: a constant fold makes a boundedness assertion green by accident):

```
turn   FULL chars  FULL hits   AUTH chars  AUTH hits   pay_CANARYRECON F/A   probe note F/A
   1         1214          0         1123          0        False/False          False/False
   6        10590          0         1476          0         True/False           True/False
   7        10719          0         1529          0         True/False           True/False
  12        10987          0         1796          0         True/False           True/False
  20        11035          0         1844          0         True/True            True/False

CLEAN-SURFACE CONTROL: 0 of 118 needles fire on the unleaked AUTHORED surface, at all five turns.
```

**All four claims hold.** ⚠️ **And the control matters in the opposite direction from the usual one**:
a needle that fires on a clean surface is a needle about the **spec**. Mine do not fire.

**Planted on the authored surface, by carrier:**

| carrier | caught |
|---|---|
| inside the refusal **VALUE** | **118 / 118** |
| as a **new-line RESIDUE** in the summary | **118 / 118** |
| inside `LAST_REFUSAL_LABEL` | 🟡 **72 / 118** |

The 46 that escape in the label are: **F8 config-shaped state field names (8 of 8), F9 config key
names (6 of 6), F5 hole descriptors (7 of 14), F4 arm identity without a digit (6 of 12), F7
answer-key vocabulary (5 of 15), F6 verdict vocabulary (5 of 8), F3 paraphrases (5 of 7), and F1's
four word-rendered ceilings — `2 lakh`, `half a lakh`, `0.5 lakh`, `2L`.**

### 4.3 P-28 held: the label is the weak surface, and the mechanism was derivable from the DESIGN

Phase 1 predicted this **before any code was opened**, from the design alone: *subtraction by identity
subtracts the label's CURRENT bytes, so a leak inside a label subtracts itself and leaves no residue;
only a content-matching layer can see it.* Measured:

```
LAST TOOL REFUSAL (the reviewer declined it):                       copy1 0   copy2 0
LAST TOOL REFUSAL (declined on review of the running total):        copy1 0   copy2 0
STATE SO FAR (a live judge reviewed this):                          copy1 0   copy2 0
```

### 4.4 P-29 held, and it is **not** a finding

A ceiling rendering and a paraphrase carried inside a **folded-state value** both escape. **That is
correct.** §8.6 puts the folded state on the authored surface and **C7's ledger fills it**; a C6
guard exempting it is exempting somebody else's data, not laundering a gate reason. Pre-committed as
not-a-finding at `11193bd`, and it stays that way now that it is measured.

---

## 5. 🟡 **P-30 DID NOT HOLD — two of `OF-104`'s OWN THREE MEASURED EXHIBITS STILL ESCAPE BOTH COPIES**

This is the sharpest result in the review, and it is a pre-committed polarity that failed **against**
the fix rather than for it.

`OF-104`'s measurement table lists **three** shapes, each producing *"0 findings from all four
guards"*:

```
1  LAST_REFUSAL_LABEL = "LAST TOOL REFUSAL (arm 2S): "
2  LAST_REFUSAL_LABEL = "... the gate judge rejected ...; arm one ..."
3  STATE_LABEL        = "STATE SO FAR (this arm runs a live judge): "
```

Its **remedy** — *"run that same regex over `scan` rather than over `value`, in BOTH copies"* — was
verified in `OF-104` against **two digit-bearing shapes**: *"`arm 2S` in the refusal label →
`['arm 2S']`; **`arm 4`** in the state label → `['arm 4']`."*

**C6 FIX 3 implemented that remedy exactly, in both copies, independently, with a clean-tree control.
This review confirms it: `R-11` (copy 1) dies with 5 failures and `R-13` (copy 2) with 3.** And then:

```
"LAST TOOL REFUSAL (arm 2S): "                                       copy1  1   copy2 20
"LAST TOOL REFUSAL (the gate judge rejected it; arm one would ...): " copy1  0   copy2  0   ESCAPES
"STATE SO FAR (this arm runs a live judge): "                         copy1  0   copy2  0   ESCAPES
CONTROL, clean tree                                                   copy1  0   copy2  0
```

**The regex is `\barms?\s*[1-4]S?\b|\bP[1-7]\b|\bINDETERMINATE\b|\bDENIED\b`. It requires a DIGIT
after `arm`.** *"this arm runs a live judge"* and *"arm one"* carry none, and neither copy's gate
vocabulary carries *judge*, *gate*, *rejected* or *reviewed*. So **the remedy as ruled, faithfully
implemented, does not reach two of the three shapes the finding measured.**

⚠️ **AND ONE MORE THING, WHICH IS WHY THIS IS NOT MERELY UNTIDY.** The parametrize list that closes
`OF-104` is introduced by the comment *"`REVIEW_C6_3`'s own two exhibits, verbatim"*, and its
state-label case reads **`"STATE SO FAR (arm 4 runs a judge): "`** — not `OF-104`'s
`"STATE SO FAR (this arm runs a live judge): "`. The substituted words are `arm 4` for `this arm`,
**and that substitution is exactly the discriminator the regex needs.** The shape is defensible — it
appears verbatim in `OF-104`'s *remedy* line — but the word *"verbatim"* is not, and this is
`INC-47`/`OF-113`'s own diagnosis one level down: ***`Fix:` is bound to a commit and cannot be
invented; a COMMENT is bound to nothing.***

**Severity: MEDIUM, not a BLOCKER**, under the rule sealed at `11193bd` and for the reason
`REVIEW_C6_3` gave when it graded a strictly worse state (coverage **zero**) as its own `M-1`: the
labels are module constants, the real ones leak nothing, and the four claims hold today over the real
bytes. It is a **tripwire coverage** finding. **Grading it a BLOCKER now, when total absence of the
same coverage was a MEDIUM then, would be manufacturing a fourth FAIL.**

**Remedy, and it is one line plus two fixtures:** add a **word-form arm alternative** and a
**judge/gate-reason vocabulary** to the surface scan in both copies — e.g.
`\barms?\s+(?:one|two|three|four)\b` and `judge|gate reason|reviewed by` — and carry
`OF-104`'s **actual third exhibit** in the parametrize list.

---

## 6. 🟢 `OF-110`'s C6 HALF — **GENUINELY CLOSED**, and stronger than `OF-110` asked

`INC-51` is the context that makes this load-bearing: this exact class **defeated hard rule 8's moat
test** — `gates/` reached `scorer/` live via `importlib` while D3 printed *"share no first-party
module on any path"*.

Fired at seven forms in synthetic packages, **outside this repository**:

| form | AST walk | source-text scan |
|---|---|---|
| `importlib.import_module("openai")` | silent | ✅ **FIRES** |
| `__import__("openai")` | silent | ✅ **FIRES** |
| `getattr(whetstone_gate, "c")` | silent | ✅ **FIRES** |
| `sys.modules[...]` — **not named by `OF-110`** | silent | ✅ **FIRES** |
| `exec("import openai", ns)` — **not named by `OF-110`** | silent | ✅ **FIRES** |
| ⚠️ `importlib.import_module("open" + "ai")` — **my P-40** | silent | ✅ **FIRES** |
| `builtins.__dict__["__imp" + "ort__"]("openai")` — my seventh | silent | ❌ silent |

**The real package: ZERO HITS.**

⚠️ **P-40 was my miss, and the design is better than my prediction.** I predicted a split target name
would escape, reasoning about the *target*; the scan refuses **the mechanism vocabulary**, not the
target — so `importlib` is caught however the string is spelled. The seventh form escapes both halves
and **is not a finding**: it uses no refused name at all, and the docstring is scoped honestly —
*"the walk sees the graph and cannot see a call; this sees the vocabulary and cannot see semantics …
neither is the guarantee alone."* **A claim scoped to what it delivers is not a defect.** And the
refusal list is itself pinned: `R-17` (dropping `getattr`) dies on
`test_the_dynamic_reach_refusal_list_is_pinned`, which names each required entry individually rather
than counting them.

**It is written separately from `check_roles.py`'s D4 and deliberately not imported from it** — *a
probe that borrows the predicate it is checking cannot find a defect in the predicate*, which is hard
rule 8's anti-circularity shape applied one level down, correctly.

---

## 7. THE TWO EQUIVALENCE PROOFS — AUDITED

**The standard is `REVIEW_C6_3`'s own `N6`:** enumerate the reachable inputs, show agreement on all of
them, **and name the input that WOULD separate them.**

### 7.1 `SM-5` (`assert replaced == 1` disarmed) — **SOUND**

*"Disarming an assertion that is true on every input any test supplies cannot fail for any suite."*
That is exactly `REVIEW_C6_3`'s own `N10` reasoning and it is correct. The separating input is
namable and is named here for completeness: **a context with zero parts carrying `STATE_LABEL`** —
measured, HEAD's assertion fires and the mutant returns the context unchanged. No code path builds
one. **SOUND.**

### 7.2 `SM-1` (the `Origin.AUTHORED` filter dropped) — 🟡 **the VERDICT is right; the PROOF is not**

Its stated proof: *"Enumerated across four history depths (3, 5, 15, 15 parts): the number of parts
containing `STATE_LABEL` is 1 WITH the origin filter and 1 WITHOUT it, EVERY TIME, **so the helper
returns a byte-identical context either way**."*

**That last clause is false in general, and this review built the separating input P-36 predicted:**

```
an ATTACKER part echoing "STATE SO FAR: "  ->  HEAD replaced=1   MUTANT replaced=2   bytes DIFFER
a WORLD tool result carrying it            ->  HEAD replaced=1   MUTANT replaced=2   bytes DIFFER
```

⚠️ **AND THE CONCLUSION I PRE-COMMITTED FROM THAT DOES NOT FOLLOW, WHICH IS REPORTED AS A MISS
AGAINST THIS FILE.** P-36 said *"if I can build a separating input, the survivor stands and it is a
FAIL trigger."* It is not, and the reason is measurable: **on every separating input the mutant's own
`assert replaced == 1` RAISES.** So the mutant is **identical or louder — never silently different** —
and the AUTHORED surface, which is the only thing the guard reads, is **byte-identical even in the
separating case**. That is the sound proof, and it is stronger than the one FIX 3 gave. It is supplied
in `mutants/c6_mutants_4.md` §3.2.

**Graded LOW**, as a defect in the **wording of a proof** rather than in the analysis behind it, and
recorded because FIX 3's own precedent (`REVIEW_C6_3`'s `N6`) states its boundary and this one does
not. **It does not carry the FAIL**, and §14 says so explicitly.

---

## 8. DETERMINISM, THE MUST-REACH CONTROL, AND TWO PLACES MY OWN METHOD DIFFERED

### 8.1 One call per turn, and the door

`run_episode` against my own mock: **20 turns, 20 model calls, 20 contexts.** The probe note reaches
the attacker on the **WORLD** surface at every turn from 6 onward and **never** on the authored one.
**The door is open and the authored surface is clean.**

### 8.2 🟡 P-43 — `pay_CANARYRECON` on the AUTHORED surface at turn 20, and the cause is MY fixture

`REVIEW_C6_3` measured `pay_CANARYRECON` **FULL=True, AUTHORED=False**. I measure **AUTHORED=True at
turn 20**, and the difference is my own driver: my `_Fold` is a **growing** fold (per `OF-82`'s
lesson), so by turn 20 the §8.6 folded state's `per_payment_refunded_paise` map carries every payment
id the attacker has acted on — **including the probe's**.

⚠️ **THAT IS CORRECT BEHAVIOUR AND NOT A LEAK, AND THE ARGUMENT IS SPECIFIC:** §13.3 mandates the
folded state in the summary; §8.6 fixes it as keyed by payment id; the id in question is one **the
attacker itself supplied** in its own tool call; and the map is built identically in every arm, so
there is **no differential**. `REVIEW_C6_3`'s cleaner reading is an artefact of its all-zero fold, not
a stronger property. **Recorded as a scope note, not a finding** — and recorded at all because a
silent difference between two reviews' must-reach tables is exactly the thing that should not sit
unexplained.

### 8.3 🔴 P-44 — 0 FULL-surface hits, and that is a defect of MY needle design

`REVIEW_C6_3` reported exactly **one** FULL-surface hit per turn — the probe's own note arriving as a
WORLD result. **Mine reports zero**, because my F5 family carries the **defender-side descriptions**
of the door (`CANARY-A`, `EXEMPTION:`, `void threshold`) and deliberately **not the note text
itself**, which §10.1 requires to reach the attacker. So my scan cannot produce that hit by
construction.

**The property is still measured** — the must-reach columns check the note and the id directly — but
**P-44 as sealed did not hold, and the reason is my file, not the package's.** Recorded as `OF-135`
rather than adjusted, on `OF-114`'s principle: *a tripwire that reports a defect that is not there is
the same class of error as one that misses a defect that is.*

---

## 9. `OF-112`, `OF-113`, `OF-114` — JUDGED

| id | FIX 3's stated reason | my judgement |
|---|---|---|
| **`OF-112`** — `test_c6_review_probes.py`'s all-zero `_Folder`, `OF-82`'s fourth instance | *"it is `REVIEW_C6_1`'s own probe file, and `INC-30`/`INC-31` are exactly a fix session committing to one"* | ✅ **STILL OPEN, and the reason is right.** The glob `tests/test_c6_*.py` did put the file inside FIX 3's fence, so it **could** have reached it — and `INC-30`/`INC-31` are a named hazard about a *fix* session editing a *reviewer's* evidence, which is the stronger consideration. ⚠️ **This review used a GROWING fold in its own driver precisely because of `OF-82`, and confirms the finding first-hand.** **Owner: a session that owns `tests/test_c6_review_probes.py`.** |
| **`OF-113`** — `INC-42`'s `Action` lists the tool schemas among what the guard **subtracts**; measured, they are **scanned** | *"`INCIDENTS.md` is append-only (`Q-033`), so another session's entry is NOT rewritten; the correction is in `INC-53` and in `OPEN_FINDINGS`"* | ✅ **STILL OPEN, CORRECTLY.** Verified first-hand: `_denial_findings` subtracts only `authored.attacker_system_prompt()`; the schema text stays in `scan` and is scanned by LAYERS 1–2, which is what the guard's own docstring says. **The direction is SAFE** — scanned is stronger than exempted. Rule 13 fixes the format and history is not rewritten. |
| **`OF-114`** — `REVIEW_C6_3`'s record of its own grep-vs-`ast` error | *"a fix session does not close a review's self-record"* | ✅ **THE REASON IS RIGHT AND IT DOES NOT BIND ME. CLOSED HERE.** A **review** session is the right author for a review's self-record. The corrected `ast`-based result is in `REVIEW_C6_3` §2.3 and in `independent/c6_review3_probes_output.txt`; nothing is owed and nothing is actionable. **Closed by this commit.** |

---

## 10. THE OWED `c6_mutants_4.md` — WRITTEN

C6 FIX 3 could not write it (`docs/reviews/mutants/` was outside its fence) and **named the debt
rather than skipping it**. It is written now, and it carries **both** tables: this session's 28 and
**C6 FIX 3's own fourteen, transcribed from `docs/sessions/nightrun-a-1.txt`.**

⚠️ **EVERY ONE OF ITS SIX CLAIMS THIS SESSION COULD INDEPENDENTLY RE-RUN REPRODUCES, INCLUDING THE
FAILURE COUNTS**: `N-M1a` 5 failed, `N-M1b` 3 failed, `SM-2` 1 failed, `SM-3` 3 failed, `SM-6` 1
failed, `SM-5` survives. The one claim that does not survive audit is **`SM-1`'s equivalence
argument** — not its verdict (§7.2).

⚠️ **AND ONE PROCESS NOTE: there is no `docs/sessions/c6-fix-3.txt`.** C6 FIX 3's FINAL OUTPUT is in
`docs/sessions/nightrun-a-1.txt` under token `363a2e9f`, because one operator "Night Run A" session
held two chunk tokens (`9c7c5973` for C0, `363a2e9f` for C6). `CLAUDE.md` §6.1 names the file
`docs/sessions/<chunk>-<role>-<attempt>.txt`. **The record exists and is complete; it is not where the
constitution says to look for it**, and a future reader grepping `c6-fix-3` finds nothing. `OF-134`.

---

## 11. REGRESSIONS AND STANDING PROPERTIES — MEASURED BY ME

| check | result |
|---|---|
| **`make test`, measurement 1** | **774 passed, 1 skipped, 2 deselected — 0 FAILED** (241.80 s) |
| **`make test`, measurement 2** | **774 passed, 1 skipped, 2 deselected — 0 FAILED** (220.59 s) |
| failures attributed by file | **there are none.** C6 FIX 3 measured 771 and C13 REVIEW 3 measured 721; the concurrent **C13 FIX 3 (`e9dd0346`)** has been landing tests throughout, which is where the +3 comes from |
| **`make check-roles`** | **17 passed, 0 failed, 5 n/a — exit 0**; E1 `44 issued row(s) covering 44 token(s)`, E2 and E3 clean |
| **`make selftest`** | **RED**, `1 failed, 1 passed, 775 deselected`, in `tests/test_lanes_operator_placeholders.py::test_the_camel_branch_is_decided_before_any_camel_run`, on `lanes: camel_comparator.branch = TODO_C13_RUN1`. **Not C6's, and it is supposed to be red until RUN-1 decides the branch.** |
| vendored pins | `tau2_bench_sha = a2c0247…`, `camel_sha = f083b6b…` both pinned and their verification tests green inside the 774; `agentdojo_sha = TODO_C13_C16` is **C16's sentinel, deliberately left by C13** and the loader **raises** on it rather than defaulting |
| `git status --porcelain tests/goldens/` | **EMPTY** |
| `evals/` | ⚠️ **does not exist.** No C6 commit touches an `evals/` path — measured across all six |
| `tests/goldens/` edited by C6 | **no** |
| `git tag -l` | `c0-pass c1-pass c2-pass c3-pass c4-pass` — **neither `probe-v1` nor `prereg-v1` is cut**, so no reported figure can contradict a frozen artefact |
| provider model calls by this session | **ZERO** |

---

## 12. FINDINGS

### 🔴 BLOCKER — **NONE**

⚠️ **Said as a positive result.** All six of `REVIEW_C6_3`'s survivors are closed by changes that go
red when reverted, each proved by mutation in a temp clone rather than by reading a diff; the four
blindness claims hold over the real assembled bytes by an independent 118-needle method with a clean
control; the door is open; `OF-110`'s C6 half is genuinely closed on five forms plus a sixth I
invented; and `_sole_killer` survives none of four attacks.

### 🟡 MEDIUM

| id | finding |
|---|---|
| **M-1** (`OF-124`) | **`R-14` — `N15`/`OF-107`'s class is unclosed in COPY 2.** Widening copy 2's LAYER-1 exemption from the state JSON to the state LINE leaves all 111 tests green; exhibit `STATE_LABEL = "STATE SO FAR (5000000): "` → HEAD 40 findings, mutant 0. Copy 1 has the fixture **and** its other side; copy 2 has neither. |
| **M-2** (`OF-125`) | **`R-15` — `N13`/`OF-111`'s class is unclosed in COPY 2.** `refusal_lines != 1` → `< 1` leaves the suite green; exhibit: a summary with two recognisable denial lines → HEAD 20, mutant 0. |
| **M-3** (`OF-126`) | **`R-20` — `crossing()`'s `turn_budget` end is pinned by nothing**, while the `k = 0` end and the target boundary are both pinned. Exhibit at `full_listing_chars = 1600`, `base = 5,521`: HEAD `20`, mutant `None` — **a number versus a sentence, for the session that sizes the run.** |
| **M-4** (`OF-127`) | **Two of `OF-104`'s own three measured exhibits still escape BOTH copies** — `"…the gate judge rejected it; arm one…"` and `"STATE SO FAR (this arm runs a live judge): "`, each 0 findings from all four guards in both copies. The remedy `OF-104` ruled was implemented faithfully and does not reach a word-form arm or a judge-shaped reason. §5. |
| **M-5** (`OF-128`) | **Authored text appended to the STATE LINE escapes all three layers**, while the identical text added as a **new line** is caught. Mechanism, proved by construction: `state_json` **is** the whole body on an untruncated line, so the state line can never contribute residue, and `_with_extra_summary_line` only ever adds a new line. `OF-106`/`N12`'s class, one sub-case over. |

### 🔵 LOW

| id | finding |
|---|---|
| **L-1** (`OF-129`) | **`R-18` — `_dynamic_reach_findings` stops at the package root if `rglob` becomes `glob`**, and no control has a subpackage. Latent: `attacker/` is flat. |
| **L-2** (`OF-130`) | **Three unpinned strictness choices in claim 4's guard**, each exhibited: `R-08` (`len(summaries) == 1` → `>= 1`, a loud raise becomes silence), `R-12` (LAYER 2b's scope over the folded-state JSON — HEAD stricter, C7's data), `R-05` (the system-prompt subtraction count — the **mutant** is stricter and wrong). **None of the three loses protection under HEAD.** |
| **L-3** (`OF-131`) | **`SM-1`'s equivalence proof states a conclusion that is false in general.** The verdict is right and the sound proof — *identical or louder, never silently different* — is supplied in `c6_mutants_4.md` §3.2. |
| **L-4** (`OF-132`) | **A comment calls a substituted shape *"verbatim"*, and the substitution is the discriminator.** `"STATE SO FAR (arm 4 runs a judge): "` for `OF-104`'s `"STATE SO FAR (this arm runs a live judge): "`. `INC-47`'s diagnosis one level down: a **comment** is bound to nothing. |
| **L-5** (`OF-133`) | **46 of 118 needles escape when carried in `LAST_REFUSAL_LABEL`** — all 118 are caught in the refusal value and as a new-line residue. The escaping classes are config-shaped names, word-rendered ceilings (`2 lakh`, `half a lakh`), digit-free arm forms and paraphrases. |
| **L-6** (`OF-134`) | **There is no `docs/sessions/c6-fix-3.txt`.** C6 FIX 3's FINAL OUTPUT is inside `docs/sessions/nightrun-a-1.txt`. The record is complete; it is not where `CLAUDE.md` §6.1 says to look. |
| **L-7** (`OF-135`) | ⚠️ **THIS REVIEW'S OWN.** P-44 did not hold: my needle families carry the **defender-side descriptions** of the door and not the note text, so my FULL-surface hit count is **0** where `REVIEW_C6_3`'s was **1**. The property is measured separately by the must-reach columns; the sealed polarity was wrong about my own file. Recorded rather than adjusted. |

### ⚪ INFO

* ⚠️ **This session's own mutation harness was invalid on its first run** — `git checkout -- <path>`
  restored from a HEAD that held the mutation, so mutants stacked and the counts ran 2/4/8/11/15/18.
  Caught by the monotone count, fixed, and re-baselined before anything was published. **The failure
  direction was flattering** (everything reports KILLED), which is why it is recorded here and in
  `c6_mutants_4.md` rather than only fixed.
* **This session met the cp1252 hazard first-hand** (`INC-08`/`INC-25`/`OF-89`): a plain
  `print` of `OPEN_FINDINGS.md` cells died on `UnicodeEncodeError: 'charmap' codec`. Every byte both
  artefacts print now goes through one ASCII route with LF newlines, set on the stream rather than
  hoped for.
* **The concurrent C13 FIX 3 session (`e9dd0346`) had its token row and a staged `INCIDENTS.md`
  in flight when this session began reading.** Staging `QUESTIONS.md` then would have swept 31 lines
  of another session's row into a commit under this token — `INC-48`'s exact defect. Nothing was
  staged until that session had committed both at `bd2107f`. Named in `daefb31`'s message.

---

## 13. `REVIEW_C6_1`'s, `REVIEW_C6_2`'s AND `REVIEW_C6_3`'s FINDINGS — OPEN OR CLOSED, WITH A SHA

| id | severity | status at `bd2107f` |
|---|---|---|
| **R1 F-1 / F-2** | BLOCKER | ✅ CLOSED `17585ab` / `2911ad0` — revert-goes-red proved by `REVIEW_C6_2` §9 |
| **R1 F-3** / `Q-048` | HIGH | ✅ CLOSED `1ad8946` |
| **R1 F-4/F-5/F-6** | MEDIUM | ✅ CLOSED — probes present and green |
| **R1 F-7** / `OF-47` | MEDIUM | 🔶 **OPEN by design.** Verified: the estimate is prompt-side only and says so in `TokenEstimate.method` and `render()` |
| **R1 F-8** / `OF-48` | MEDIUM | ✅ CLOSED `fe3984f` |
| **R1 F-9** / `OF-49` | MEDIUM | 🔶 **OPEN**, widened and stated; five bias classes named |
| **R1 F-10** / `OF-50`, **F-11** / `OF-51` | LOW | ✅ CLOSED `fe3984f` / `17585ab` |
| **R1 F-12** / `OF-52` → `OF-90` | LOW | 🔶 **OPEN** — outside every C6 fence |
| **R2 B-1 / B-2 / B-3** | BLOCKER | ✅ **all three CLOSED** `fe3984f`, verified by `REVIEW_C6_3` §2–§4 and re-confirmed here (`R-11`, `R-13`, `R-16`) |
| **R2 M-1…M-8** (`OF-81`…`OF-88`) | MEDIUM | ✅ **all eight CLOSED** `fe3984f` |
| **R2 M-9** / `OF-89` | MEDIUM | ✅ CLOSED `9c809c2` |
| **R2 L-1**/`OF-90`, **L-4**/`OF-92`, **L-6**/`OF-94`, **L-7**/`OF-95` | LOW | 🔶 **OPEN** — outside the fence; `Q-076`, `Q-078` raised |
| **R2 L-2** / `OF-53` | MEDIUM | 🔶 **OPEN.** Verified again: `spec_constants.AUTHORED_TEXTS` still holds exactly three paths and `data/generic_denial.txt` is not among them |
| **R2 L-3** / `OF-91`, **L-5** / `OF-93` | LOW | ✅ CLOSED `fe3984f` |
| **R3 M-1** / `OF-104` | MEDIUM | 🟡 **CLOSED `f03d359` FOR THE SHAPE IT RULED, AND ITS RESIDUE IS RE-RAISED AS `OF-127`.** The remedy is implemented in both copies and goes red when reverted; two of the finding's own three exhibits still escape. §5 |
| **R3 M-2** / `OF-105` (`N14`) | MEDIUM | ✅ **CLOSED `f03d359`** — `N14` re-run here: KILLED, 4 failed |
| **R3 M-3** / `OF-106` (`N12`) | MEDIUM | ✅ **CLOSED `f03d359`** — KILLED, 4 failed. Residue sub-case re-raised as `OF-128` |
| **R3 M-4** / `OF-107` (`N15`) | MEDIUM | 🟡 **CLOSED `f03d359` for COPY 1** — KILLED, 3 failed — **and unclosed in COPY 2**, re-raised as `OF-124` |
| **R3 M-5** / `OF-108` (`N4`) | MEDIUM | 🟡 **CLOSED `f03d359`** — KILLED, 2 failed — **and the same class at the range's other end is re-raised as `OF-126`** |
| **R3 M-6** / `OF-109` (`N9`) | MEDIUM | ✅ **CLOSED `f03d359`** — KILLED, 2 failed; three relative forms in the control |
| **R3 M-7** / `OF-110` | MEDIUM | ✅ **C6's HALF CLOSED `f03d359`** — five forms plus a sixth verified here. **The C2 / C3 / C13 halves remain open and routed.** |
| **R3 M-8** / `OF-112` | MEDIUM | 🔶 **OPEN** — §9 |
| **R3 L-1** / `OF-111` (`N13`) | LOW | 🟡 **CLOSED `f03d359` for COPY 1** — KILLED, 3 failed — **and unclosed in COPY 2**, re-raised as `OF-125` |
| **R3 L-2** / `OF-113` | LOW | 🔶 **OPEN, correctly** — §9 |
| **R3 L-3** / `OF-53` | MEDIUM | 🔶 **OPEN** — verified |
| **R3 L-4** / `OF-114` | LOW | ✅ **CLOSED by this commit** — §9 |
| **`OF-123`** (C6 FIX 3's own) | MEDIUM | ✅ **CLOSED for the instance `f03d359`** — `R-13` kills it, 3 failed. **The CLASS stays open**, and this review is the seventh instance |

---

## 14. WHAT A PASS REQUIRED, ITEM BY ITEM

| requirement | met? |
|---|---|
| all six survivors killed by changes that go red when reverted | ✅ **all six**, by tests that name the property |
| both equivalence proofs sound | 🟡 **`SM-5` sound; `SM-1`'s verdict right and its stated proof false in general** — LOW, §7.2 |
| **every new-surface mutant killed or proven equivalent** | ❌ **7 NON-EQUIVALENT SURVIVORS; 3 carry the FAIL** |
| the four blindness claims by MY method with MY needle shapes | ✅ **0 AUTHORED hits of 118**, five turns, over the real assembled bytes |
| **a clean-surface control** | ✅ **0 of 118** |
| the must-reach control | ✅ the note **FULL=True / AUTHORED=False** at every turn; `pay_CANARYRECON`'s AUTHORED=True at turn 20 explained and correct (§8.2) |
| my scoped reimplementation agreeing | ✅ the three layers, the exclusivity semantics and the needle families all re-derived from `CONTEXT.md` + `config/` alone, and its `sole_catcher` agrees with the package's `_sole_killer` on four constructed exhibits |
| zero BLOCKERs | ✅ **zero** |
| no reported figure contradicting `prereg-v1` | n/a — neither `probe-v1` nor `prereg-v1` is cut |
| no spec deviation | ✅ |

### ⚠️ WHAT WOULD OVERRULE THIS VERDICT, STATED SO THE ARCHITECT DOES NOT HAVE TO GUESS

**The FAIL rests on `OF-124`, `OF-125` and `OF-126` — three mutant survivors, three one-fixture
remedies.** It does **not** rest on the four LOW survivors, on `OF-127`, or on `OF-128`; those are
findings, not the gate.

The one judgement in it is this: **is a surviving mutant on a TEST-side guard a FAIL when the guard's
subject is provably clean today?** This project has answered yes twice in the last two reviews, on
exactly this shape, and `docs/reviews/README.md`'s bar says *"every mutant killed or proven
equivalent"* without qualification. **If the architect rules that the bar is about the SUBJECT rather
than about the GUARD, this chunk passes on everything else** — and that ruling belongs in
`QUESTIONS.md`, not in a reviewer's discretion, which is why the verdict follows the written bar.

---

## 15. A NOTE ON PROPORTION

**C6 has now failed four times, and this one is different in kind from the last.** REVIEW 1 failed it
on a Class A deviation and a corpus reaching 4% of itself. REVIEW 2 failed it on a published figure
its own series refuted, a guard that read past its own leak, and a walk that did not walk. REVIEW 3
failed it on six assertions that could be deleted with the suite green. **All of those are closed, and
every closure was proved here by reverting it and watching a named test go red.**

**What fails it now is narrower than any of them, and it has a shape worth naming: FIX 3 fixed COPY 1
thoroughly and COPY 2 for one class only.** It found the copy-2 blindness itself — `N-M1b`, its own
self-directed mutant, the single best moment in the chunk's history — closed it for `OF-104`, and did
not carry `N13`'s and `N15`'s fixtures across. **The mechanism that found the defect was applied once
and not swept.**

⚠️ **AND THE CLASS NOW HAS A COUNT, WHICH IS THE ONLY THING WORTH MORE THAN THE INSTANCE.** `INC-42`'s
`Systemic guardrail` field reads *"NONE THAT CLOSES THE CLASS — ACCEPTED, AND THE REASON IS THAT FOUR
SESSIONS HAVE NOW TRIED."* `REVIEW_C6_3` made it five. `INC-53` made it six. **This is seven** — and
for the first time the instances are not new blind spots but **the same three classes not carried from
one copy of a guard to its twin.** The remedy that keeps being named is *a mechanism rather than
another careful pair of eyes*; the mechanism this fix demonstrated — **mutate your own new surface** —
works, and what is owed is applying it to **both copies** rather than to the one the finding named.

⚠️ **This review is not failing a chunk to look rigorous, and it is not passing one because the
project is behind schedule.** Thirty-nine of fifty-five polarities sealed before the fix was opened
held exactly; **three of the six rows that predicted failure were wrong, and all three were wrong in
the fix's favour**; one row that predicted success failed against the fix and is §5; and one miss is
recorded against this review's own needle design. **The gate went red on three specific, named,
reproducible mutants, each with a concrete input on which HEAD and the mutant differ, and on nothing
else.**

---

**PASS: NO. TAG `c6-pass`: NOT CUT.**
