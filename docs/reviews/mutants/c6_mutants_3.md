# `c6_mutants_3.md` — C6 REVIEW 3 (`3605d31c`), 2026-09-02

**26 mutants run. 18 KILLED, 8 SURVIVED — of which 2 are proved EQUIVALENT and 6 are proved
NON-EQUIVALENT BY EXHIBIT.**

**Every mutation ran in a FRESH OS TEMP CLONE**, `C:\Users\chinm\AppData\Local\Temp\c6r3-Q54R\tree`,
whose `whetstone_gate.__file__` printed as
`C:\Users\chinm\AppData\Local\Temp\c6r3-Q54R\tree\src\whetstone_gate\__init__.py` (INC-17).
**This repository was never mutated**; each mutant was applied, the file's SHA-256 compared before
and after, the suite run, and `git checkout -- .` verified to restore the original digest.

**Baseline on the unmutated clone: `77 passed`** (`tests/test_c6_attacker.py`,
`tests/test_c6_fix_probes.py`, `tests/test_c6_review_probes.py`).
**SPEND: ZERO. No provider model call was made by this session.**

⚠️ **AN EQUIVALENCE CLAIM HERE IS AN EXHIBIT, NEVER AN ARGUMENT** — `docs/reviews/README.md`, and
this session's prompt in terms. Both equivalence rows below carry a value, not a paragraph.

---

## 1. THE FOUR OLD SURVIVORS — RE-RUN VERBATIM, ALL FOUR NOW KILLED

| id | file | operator | verdict | killed by |
|---|---|---|---|---|
| **M3** | `attacker/context.py:render_summary` | `estimate_text(...) <= token_cap` → `<= token_cap + 1` | ✅ **KILLED** | `test_c6_fix_probes.py::test_the_cap_is_INCLUSIVE_and_pinned_in_BOTH_directions` |
| **M19** | `attacker/context.py:render_summary` | `<= token_cap` → `< token_cap` | ✅ **KILLED** | same test |
| **M17** | `attacker/context.py:LAST_REFUSAL_LABEL` | the label carries E1's cap as a bare integer (REVIEW 2's exact text) | ✅ **KILLED**, 3 failures | `test_c6_attacker.py::test_the_attackers_context_contains_no_gate_denial_reason` **+2** |
| **M18** | `attacker/context.py:render_summary` | ⚠️ **INVERTED** — the pre-`OF-88` **tail cut** restored, because HEAD now *is* the reserve-the-denial cut M18 was | ✅ **KILLED**, 4 failures | `test_the_truncation_mark_says_the_cut_is_lossy` **+3** |

⚠️ **M18's POLARITY FLIPPED AND THE FLIP IS RECORDED RATHER THAN GLOSSED.** `OF-88`'s ruling made
the mutant's behaviour the *correct* one, so re-running M18 verbatim would have re-applied what HEAD
already does and measured nothing. The mutant that carries M18's meaning against this HEAD is the
**tail cut**, and it dies on four tests.

---

## 2. B-1 — THE CROSSOVER, PROVED BY MUTATION AND NOT BY READING

| id | file | operator | verdict | killed by / exhibit |
|---|---|---|---|---|
| **N1** | `attacker/estimate.py:CROSSOVER_SERIES` | `base_tokens=16495` → `8247` (halved) | ✅ **KILLED**, 2 failures | `test_the_crossover_reaches_C14_through_the_estimates_own_comparison` + `..._reproduces_against_the_REAL_seed_2001_world` |
| **N2** | `attacker/estimate.py:crossover_note` | the headline's `{k}` replaced by the literal `9` | ✅ **KILLED** | `test_the_crossover_figure_is_GENERATED_from_its_own_series_and_not_written_beside_it` — **the assertion a literal cannot pass** |
| **N3** | `attacker/estimate.py:CrossoverSeries.tokens_per_read` | the `- estimate_characters(displaced…)` term dropped (a read treated as an ADDITION, not a REPLACEMENT — the error that produced REVIEW 2's 5,802) | ✅ **KILLED**, 2 failures | as N1 |
| **N5** | `attacker/estimate.py:estimate_characters` | `math.ceil` → `round` | ✅ **KILLED**, 3 failures | `..._reproduces_against_the_REAL_seed_2001_world` **+2** |
| **N7** | `attacker/estimate.py:linear_reads_limit` | `max(0, turn_budget - window)` → `max(0, turn_budget)` | ✅ **KILLED** | `..._reproduces_against_the_REAL_seed_2001_world` |
| **N4** | `attacker/estimate.py:CrossoverSeries.crossing` | `tokens_at(...) > target` → `>= target` | ⚠️ **SURVIVOR** | **§3.1** |
| **N6** | `attacker/estimate.py:estimate_characters` | `if characters <= 0` → `< 0` | ⚪ **SURVIVOR — EQUIVALENT** | **§4.1** |

**Beyond the suite, the generated-ness was measured directly** (`independent/c6_review3_probes.py`):
moving the series moves the printed figure — `base 16,495 → 9`, `8,247 → 10`, `32,990 → 6`, `0 → 12`;
`full_listing_chars 2,887 → 9`, `1,500 → 18`, and at `900` the headline changes **shape** to
*"NO number of full-listing reads inside 20 turns crosses 60,000 on this series"*, which is the
`None` branch the method's own docstring says must not be rendered as a number. Two accesses of
`CROSSOVER_NOTE` return **distinct objects** (PEP 562 regenerates; it is not a module-level cached
string), and a **fresh subprocess** with `WHETSTONE_CONFIG_DIR` pointing at `chars_per_token: 4`
prints **11**. **There is no literal to correct, and that is B-1's actual remedy.**

---

## 3. B-2 AND B-3 — THE GUARD AND THE WALKER

| id | file | operator | verdict | killed by / exhibit |
|---|---|---|---|---|
| **N8** | `tests/test_c6_attacker.py:_imported_modules` | B-3's own fix reverted — `for alias in node.names: found.add(f"{prefix}.{alias.name}")` removed | ✅ **KILLED** | `test_the_import_scan_ACTUALLY_FIRES_in_every_import_form` — **the positive control C6 never had** |
| **N11** | `tests/test_c6_attacker.py:_denial_findings` | LAYER 1 (money values) disarmed | ✅ **KILLED** | `test_the_attackers_context_contains_no_gate_denial_reason` |
| **N16** | `attacker/context.py:drop_earliest_rendered` | drops the **newest**-rendered instead of the oldest | ✅ **KILLED** | `test_the_truncation_mark_says_the_cut_is_lossy` |
| **N17** | `attacker/context.py:minimum_token_cap` | the mandated denial line removed from the floor | ✅ **KILLED**, 2 failures | `test_the_hard_refusal_covers_the_MANDATED_denial_line` **+1** |
| **N18** | `attacker/context.py:truncation_mark` | the count of dropped entries stops being **printed** (hard rule 11) | ✅ **KILLED**, 2 failures | `test_the_truncation_mark_says_the_cut_is_lossy` **+1** |
| **N19** | `attacker/corpus.py:seed_for_turn` | `stride = max(1, turn_budget // len(corpora))` → `… + 1` | ✅ **KILLED**, 2 failures | `test_the_selection_function_is_hand_recomputable_exactly_as_the_docstring_states` **+1** |
| **N20** | `attacker/corpus.py:corpora_in_order` | first-appearance order → `sorted` | ✅ **KILLED** | same test |
| **N9** | `tests/test_c6_attacker.py:_imported_modules` | the **relative**-import resolution dropped | ⚠️ **SURVIVOR** | **§3.2** |
| **N12** | `tests/test_c6_attacker.py:_denial_findings` | **LAYER 3** (the residue catch-all) disarmed | ⚠️ **SURVIVOR** | **§3.3** |
| **N13** | `tests/test_c6_attacker.py:_denial_findings` | `refusal_lines != 1` → `< 1` | ⚠️ **SURVIVOR** | **§3.4** |
| **N14** | `tests/test_c6_attacker.py:_denial_findings` | the `value != generic` equality disabled | ⚠️ **SURVIVOR** | **§3.5** |
| **N15** | `tests/test_c6_attacker.py:_denial_findings` | LAYER 1's exemption widened from the state **JSON** to the whole state **LINE** | ⚠️ **SURVIVOR** | **§3.6** |
| **N10** | `tests/test_c6_attacker.py` | `assert "config.py" in reached` → `… or True` | ⚪ **SURVIVOR — EQUIVALENT BY CONSTRUCTION** | **§4.2** |
| **N21** | `attacker/context.py:LAST_REFUSAL_LABEL` | the label carries **`(arm 2S)`** | ✅ **KILLED — but INCIDENTALLY** | **§3.7** |
| **N22** | `attacker/context.py:LAST_REFUSAL_LABEL` | *"(the gate judge rejected your last action; arm one would have executed it)"* | ✅ **KILLED — but INCIDENTALLY** | **§3.7** |
| **N23** | `attacker/context.py:STATE_LABEL` | *"STATE SO FAR (this arm runs a live judge)"* | ✅ **KILLED — but INCIDENTALLY** | **§3.7** |

---

## 3.1 N4 — `crossing()`'s `>` against §13.4's `≤`, unpinned. **NON-EQUIVALENT BY EXHIBIT.**

`per_read = 5,298`. A series whose `tokens_at(8)` is **exactly** the 60,000 target has
`base_tokens = 60,000 − 8 × 5,298 = 17,616`:

```
base_tokens = 17,616  ->  tokens_at(8) = 60,000 EXACTLY
   HEAD   (>)   crossing = 9
   MUTANT (>=)  crossing = 8
```

**HEAD is right and the mutant is wrong**, and the reason is §13.4's own wording: *"N = 50 … IF the
pilot's measured attacker tokens/episode is **≤ 60,000**"* — exactly 60,000 is **WITHIN** Branch A,
so the first read that breaks the budget is the first **strictly** over it. On the current series
the two agree, because `(60,000 − 16,495) / 5,298 = 8.2116` is not an integer, **which is exactly
why nothing sees it.** ⚠️ **This is `OF-87`'s class one level over, inside the code written to close
B-1**: the *cap* boundary was ruled inclusive and pinned in both directions; the *target* boundary
is the same shape and is pinned in neither. **Remedy: one fixture at `base_tokens = 17,616`.**

## 3.2 N9 — the relative-import resolution, unpinned. **NON-EQUIVALENT BY EXHIBIT.**

```
plant, in a synthetic tree, the ONLY route to a client being a relative import:
   from .. import provider_client        HEAD fires=True   MUTANT fires=False
   from ..provider_client import x       HEAD fires=True   MUTANT fires=False
```

**And the positive control's parameter list, read from the source, has FOUR rows and no relative
form:** `from <pkg> import <module>`, `from <pkg>.<module> import <name>`, `import <pkg>.<module>`,
`import <client>`. ⚠️ **`INCIDENTS.md` INC-43 calls the relative resolution *"a second form of the
same blindness, found while fixing the first"* — the capability was added and the control that
exists to pin exactly this was not extended to it.** **Remedy: one `parametrize` row.**

## 3.3 N12 — LAYER 3, the residue catch-all, is the sole killer of nothing. **NON-EQUIVALENT.**

```
an authored addition with NO policy word at all      LAYER3 fires=1   LAYERS 1-2 fire=0
   "unexplained AUTHORED text the spec does not mandate: 'NOTE: your last action was reviewed.'"
an addition naming the defender, no vocabulary       LAYER3 fires=1   LAYERS 1-2 fire=0
   "unexplained AUTHORED text the spec does not mandate: 'A reviewer looked at that one.'"
```

**LAYER 3 works** — it catches authored text carrying no recognised policy word, which is precisely
what `INC-42`'s `Action` field claims for it: *"A second, **independent** layer asserts the residue
is whitespace only, so unexplained authored text of **any** kind fails even when it carries no
recognised policy word."* ⚠️ **And it can be deleted with the whole 77-test suite green**, because
every leak the suite plants carries a cap value or a clause and dies to LAYERS 1–2 first.
**Remedy: one fixture that adds a policy-word-free line to the summary.**

## 3.4 N13 — `refusal_lines != 1` weakens to `< 1`. **NON-EQUIVALENT BY EXHIBIT.**

```
a summary carrying TWO recognisable denial lines ->
   HEAD:   "the summary carries 2 recognisable last-denial line(s), not 1; CONTEXT.md 13.3 …"
   MUTANT: silent (2 is not < 1)
```

The `< 1` half — *"a summary in which no line is recognisable as one is a finding in itself"* — is
exercised by the fix's own boundary-spanning shape. The `> 1` half is exercised by nothing. **LOW.**

## 3.5 N14 — the `value != generic` equality is never the SOLE killer. **NON-EQUIVALENT.**

The three value-leaks the fix's own test plants are each caught **twice**, so the equality check is
never the thing that fails:

| planted value | equality fires | token regex fires |
|---|---|---|
| `… (arm 2S)` | 1 | 1 |
| `… Clause P1 was violated.` | 1 | 1 |
| `… verdict=INDETERMINATE` | 1 | 1 |

**A value-leak only the equality can see:**
`"This action was blocked by policy. Try a smaller amount next time."` → HEAD fires on the equality
**alone**; the mutant is silent and no other layer sees it. ⚠️ **This is the assertion `Q-046`'s
ruling turns on** — *"THE LOOP THEREFORE IDENTIFIES A DENIAL BY EXACT STRING EQUALITY AGAINST THAT
ONE AUTHORED CONSTANT"* — and it is pinned by nothing. **Remedy: one planted value with no clause,
no arm and no verdict word.**

## 3.6 N15 — LAYER 1's exemption boundary, unpinned. **NON-EQUIVALENT BY EXHIBIT.**

`STATE_LABEL = "STATE SO FAR (actions over 5000000 paise are refused): "` → HEAD fires **twice** on
LAYER 1 (`'50000'`, `'5000000'`). Widen the exemption from the state **JSON** to the whole state
**LINE** and the same leak is invisible. **The fix's own `STATE_LABEL` case plants a policy
CLAUSE**, which LAYER 2 kills, **never a CAP VALUE** — so LAYER 1's exemption boundary is
unexercised. **Remedy: plant a cap value in `STATE_LABEL`, not only a clause.**

## 3.7 N21 / N22 / N23 — KILLED, BUT BY A BYTE-COUNT FIXTURE AND NOT BY ANY GUARD

**All three die**, each on exactly one test:
`test_c6_fix_probes.py::test_the_crossover_series_reproduces_against_the_REAL_seed_2001_world` —
because a longer label changes the summary's **character count**, which moves `base_tokens`.
**Nothing in the kill is about the label's content.**

**Measured, with that one fixture deselected:**

```
BASELINE minus the byte-count fixture : 76 passed, 1 deselected
N21  "LAST TOOL REFUSAL (arm 2S): "   : 76 passed, 1 deselected   <- ALL FOUR GUARDS SILENT
N22  the gate-judge prose             : 76 passed, 1 deselected   <- ALL FOUR GUARDS SILENT
```

And directly, against the four guards themselves:

```
LAST_REFUSAL_LABEL = "LAST TOOL REFUSAL (arm 2S): "                  four guards -> 0 findings
LAST_REFUSAL_LABEL = "... the gate judge rejected ...; arm one ..."   four guards -> 0 findings
STATE_LABEL        = "STATE SO FAR (this arm runs a live judge): "    four guards -> 0 findings
CONTROL: M17 verbatim                                                 four guards -> 6 findings
```

⚠️ **This is the finding, and it is carried as `OF-` rather than as a BLOCKER because the mutants
DIE.** The guard's own opening sentence is *"a denial leaks neither which arm is running nor which
clause fired"*, and its own regex `\barms?\s*[1-4]S?\b|\bP[1-7]\b|\bINDETERMINATE\b|\bDENIED\b`
encodes exactly that — **applied to the refusal VALUE and to nothing else**, while B-2 established
that the shape which actually occurs is a leak **in the label**. **Remedy, verified here to catch
both and to produce no false positive on the clean tree: run that same regex over `scan` (the
authored surface minus the §8.6 system prompt) in BOTH copies of the guard.**

---

## 4. THE TWO EQUIVALENCE PROOFS — BY EXHIBIT

### 4.1 N6 — `estimate_characters`' zero guard

```
CALL SITES, enumerated from the source (three, all in estimate.py):
   estimate.py:192   estimate_characters(len(text), divisor=...)
   estimate.py:301   estimate_characters(self.full_listing_chars, divisor=divisor)
   estimate.py:302   estimate_characters(self.displaced_result_chars, divisor=divisor)

EXHIBIT at the only reachable boundary:
   HEAD    estimate_characters(0, divisor=3)  = 0
   MUTANT  math.ceil(0 / 3)                   = 0     -> IDENTICAL
```

Every call site passes `len(str)` or a measured character count, so a negative argument is
unreachable. ⚠️ **The boundary of this proof is stated rather than hidden:** `CrossoverSeries` is a
frozen dataclass with no validation, so a *hand-constructed* series with a negative character count
would separate them. No code path constructs one.

### 4.2 N10 — an assertion mutated to `or True`

**EQUIVALENT BY CONSTRUCTION, and this mutant should not have been written.** `assert X or True`
cannot fail for any `X`, so a mutant that disarms a currently-true assertion is a survivor for every
passing assertion in any suite and measures nothing. It is recorded rather than deleted because a
mutant table that quietly drops its author's mistakes is not a record. **The meaningful compound —
revert the alias fix *and* disarm the named assertion — is unnecessary: N8 alone dies to the
positive control.**

---

## 5. WHAT THE COUNT MEANS

**18 killed. 2 equivalent. 6 non-equivalent survivors: N4, N9, N12, N13, N14, N15.**

⚠️ **ALL SIX ARE ON CODE NO REVIEW HAS SEEN — the fix's own new material — and four of the six are
in the blindness guard the submission rests on.** `docs/reviews/README.md`'s bar is *"every mutant
killed or **proven equivalent**"*, and this session's fence names `tests/` under **NOT**, so unlike
`REVIEW_C6_1` — which closed its four survivors with kept probes in its own commit — **this review
may not close them.**

⚠️ **AND THE SHAPE IS THE ONE THE PROMPT ASKED FOR.** `INC-42`'s own `Diagnosis` names the class —
*"a check written against the shape the author imagined, which is silent on the shape that actually
occurs"* — and counts **five instances in this repository in one day**. N9, N12, N14, N15 and §3.7
are instances **six through ten**, and every one of them is inside the code written to close
instances four and five. `INC-42`'s `Systemic guardrail` field predicted exactly this: *"NONE THAT
CLOSES THE CLASS — ACCEPTED, AND THE REASON IS THAT FOUR SESSIONS HAVE NOW TRIED."*
**That is an honest field, and it is also the reason this chunk cannot be tagged yet.**
