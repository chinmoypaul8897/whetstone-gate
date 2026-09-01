"""Token counting — ⚠️ **AN ESTIMATE, AND IT IS LABELLED ONE EVERYWHERE.**

⚠️ **ARCHITECT RULING, 2026-08-31, recorded in `QUESTIONS.md` Q-031.** C6's done-when
says *"measured tokens/episode is recorded and compared against the ≤ 60,000 target"*. **A
true measurement requires a provider call and C6 may not make one** — `PROCESS.md` §8's
lane reservation gives the Gemma lanes to the sweep from 31 August and no build session
may spend on them. So C6 produces an **ESTIMATE**, with its method declared in the code
and in the report, and **C14's pilot measures the real figure** (`CONTEXT.md` §13.3: *"The
pilot MUST measure the actual figure and it selects the N branch"*).

**Why the label matters more than the number.** The measured figure selects the **N
branch** (§13.4) — the size of the entire run. An estimate presented as a measurement is
`INCIDENTS.md` **INC-05**'s class: a precise-sounding figure with no source behind it. So
every value this module returns is carried in a type whose name says `Estimate`, and the
one function that compares against the §8.6 target returns a verdict that names itself an
estimate too.

---

**THE METHOD, STATED SO IT CAN BE CHECKED RATHER THAN TRUSTED.**

A **character-count approximation**: ``ceil(len(text) / CHARS_PER_TOKEN)`` over the UTF-8
text of the assembled context, summed across every part, plus a per-message framing
allowance.

*Why not a real tokenizer.* The attacker runs on **Gemma 4 26B/31B** (`CONTEXT.md`
§13.3.2). A tokenizer for that model is not in this project's dependencies — `pyproject.toml`
declares exactly ``pyyaml`` and ``numpy`` — and adding one would break `CONTEXT.md` §20's
clean-clone claim for a number that C14 replaces with a real measurement anyway. **Naming a
tokenizer from a different model family would be worse than approximating**: it would read
as a measurement while measuring a different vocabulary, which is precisely the
false-precision failure INC-05 records.

*The parameters were declared IMPLEMENTATION CHOICES, and* ⚠️ **ONE OF THE TWO WAS NOT —
`QUESTIONS.md` Q-048, RULED 2026-09-01, Class A, from `REVIEW_C6_1`'s finding F-3.** The
paragraph that stood here said both were Class B and that they *"must never be added to
`config/`"*, on the ground that C14's measurement supersedes them before any scored episode
runs. ⚠️ **That was true of the FIGURE and false of the EXPERIMENT.**
:func:`whetstone_gate.attacker.context.render_summary` enforces §8.6's **400-token** summary
cap as ``token_cap * CHARS_PER_TOKEN`` **characters**, so this divisor decides **the bytes
the attacker is sent**, in every arm, on every turn — measured by the review as its property
**D4f**: 3 → 4 renders a different summary. A §8.6 row hashed into `PROTOCOL.md` at
`prereg-v1` whose operational meaning is fixed by a number outside the freeze is not frozen.

So :data:`CHARS_PER_TOKEN` is now a §8.6 row, a `config/protocol.yaml` key and a tripwire
registry row, and it is **read through the one loader on every access**.

⚠️ **:data:`FRAMING_TOKENS_PER_MESSAGE` IS STILL CLASS B, AND THAT IS Q-048's OWN TEST
APPLIED RATHER THAN COPIED.** It is used only by :func:`estimate_messages` and **never by
the cap**, so it moves the figure this project *reports* and not one byte of what the
attacker is *sent*. Q-048's question — *"does this value change what the experiment
sees?"* — answers **no** for it, and the two parameters are therefore treated differently
on purpose rather than rounded to the same answer.

*Expected error, MEASURED rather than asserted, and the first measurement was WRONG.*
Calibrated by the C6 build session against a real BPE tokenizer (``cl100k_base``) over
this project's own assembled attacker context — the full numbers are in
``docs/sessions/c6-build-1.txt``.

⚠️ **The calibration was run twice and the first run gave the wrong answer, so the second
is the one recorded.** Against a *toy* fixture with short tool results, prose dominated,
the text ran **4.11 characters per token**, and a divisor of 4 over-estimated by +2.9% —
the safe direction. Against the **real seed-2001 world payload** the same estimator ran
**‑25.4%, LOW**: `fetch_payments` returns JSON, JSON tokenizes far denser than prose
(**2.97** chars/token), and a divisor of 4 therefore **under**-estimates every context a
real episode actually assembles. **That is the unsafe direction for this particular
number**, because Branch A of §13.4's N decision rule is *"measured tokens/episode ≤
60,000"* — an under-estimate is exactly the error that would make a run look like it fits.

So the divisor is **3**, chosen against the realistic fixture rather than the flattering
one. Measured error at that divisor: **‑0.9%** on the worst case (full payment list
returned every turn) and **+11.9%** on the realistic call mix. It never under-states by
more than one percent, and where it errs it errs high.

⚠️ **It is an estimate in TWO ways, and the second is not fixable here.** ``cl100k_base``
is not Gemma's tokenizer, and the attacker runs on Gemma 4 26B/31B. The calibration bounds
the *arithmetic*, not the *vocabulary*. **Only a provider call measures the real figure,
and that is C14's.**
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from whetstone_gate import config as cfg

#: ⚠️ **``CHARS_PER_TOKEN`` — a `CONTEXT.md` §8.6 row, read from `config/` on EVERY ACCESS.**
#:
#: ``protocol.yaml:attacker.chars_per_token``. It is **not** written here: `QUESTIONS.md`
#: **Q-048** made it a §8.6 constant because it decides the bytes the attacker is sent (see
#: this module's docstring), and hard rule 9 then puts it in `config/` with no default.
#:
#: **Resolved lazily through PEP 562, which is `whetstone_gate.world.spec`'s established
#: pattern here and is used for its stated reason:** *"a module-level eager read would be
#: exactly that stale cache, frozen at import"* — `whetstone_gate.config.load` is
#: deliberately uncached so a read cannot outlive an edit during a long run. PEP 562 keeps
#: the plain attribute name that ``context.render_summary`` imports and that
#: ``tests/test_c6_review_probes.py::test_the_estimator_uses_the_divisor_its_calibration_selected``
#: reads, while making each access a fresh load.
#:
#: ⚠️ **Three, not the conventional four.** The conventional four is calibrated on prose;
#: this project's contexts are dominated by the JSON `fetch_payments` returns, which
#: measured **2.97** characters per BPE token against the real seed-2001 world (C6's
#: calibration) and **2.99** on the review's independent re-derivation. At four the
#: estimator ran 25% **LOW**, and low is the unsafe direction for the one number that
#: selects §13.4's N branch.
_LOADER_RESOLVED = {"CHARS_PER_TOKEN": "attacker.chars_per_token"}


def __getattr__(name: str):
    """PEP 562: resolve :data:`CHARS_PER_TOKEN` and :data:`CROSSOVER_NOTE` on access.

    ⚠️ **:data:`CROSSOVER_NOTE` is here for the same reason the divisor is** — every number
    in it is read from `config/`, and `config.load` is deliberately uncached so that a read
    cannot outlive an edit during a long run. A module-level eager string would be exactly
    the stale cache, frozen at import, that this pattern exists to prevent; it would also be
    a **second** place the crossover figure could live, which is `INCIDENTS.md` **INC-41**.
    """
    if name == "CROSSOVER_NOTE":
        return crossover_note()
    try:
        dotted = _LOADER_RESOLVED[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
    return cfg.load("protocol").require(dotted)


def chars_per_token() -> int:
    """The §8.6 divisor, from `config/`. The explicit form of :data:`CHARS_PER_TOKEN`."""
    return cfg.load("protocol").require(_LOADER_RESOLVED["CHARS_PER_TOKEN"])


#: Per-message framing allowance — role markers and delimiters that every chat API adds
#: around a message and that the character count of the message body does not see.
#:
#: ⚠️ **Still a Class B implementation parameter, and deliberately NOT a §8.6 row** — it is
#: used only by :func:`estimate_messages` and never by ``render_summary``'s cap, so it moves
#: the figure this project **reports** and not one byte of what the attacker is **sent**.
#: That is `QUESTIONS.md` **Q-048**'s own test applied rather than copied; the divisor above
#: fails it and this does not. It is pinned as a behaviour by
#: ``tests/test_c6_review_probes.py::test_the_estimator_applies_its_per_message_framing_allowance``,
#: which killed mutant **M9**.
FRAMING_TOKENS_PER_MESSAGE = 4


@dataclass(frozen=True)
class TokenEstimate:
    """⚠️ An ESTIMATE. The name is the label and the label is load-bearing."""

    tokens: int
    """The estimated token count. **Not a measurement.**"""

    characters: int
    """The character count it was derived from — the one figure here that IS exact."""

    messages: int
    """How many messages the framing allowance was applied to."""

    method: str = (
        "ESTIMATE - character-count approximation, "
        "ceil(chars / CHARS_PER_TOKEN) + messages * FRAMING_TOKENS_PER_MESSAGE, "
        "over ASSEMBLED CONTEXTS (prompt side) ONLY. "
        "!! COMPLETION TOKENS ARE NOT COUNTED: a provider bills prompt + completion and "
        "evals/usage/ is written from the API's own usage field, which reports both. At "
        "40-400 output tokens/turn over 20 turns that is 800-8,000 tokens/episode "
        "UNCOUNTED, and the omission is ONE-DIRECTIONAL and LOW - CONTEXT.md 13.4's "
        "unsafe direction, since Branch A is 'measured tokens/episode <= 60,000'. "
        "(OPEN_FINDINGS.md OF-47, REVIEW_C6_1 F-7.) "
        "NOT a provider measurement. C14's pilot measures the real figure and it "
        "selects the N branch (CONTEXT.md 13.3, 13.4; QUESTIONS.md Q-031)."
    )

    def __str__(self) -> str:  # pragma: no cover - reporting convenience
        return f"~{self.tokens} tokens (ESTIMATE, {self.characters} chars)"


def estimate_text(text: str, *, divisor: int | None = None) -> int:
    """Estimated tokens for one string. Deterministic, and pure given the divisor.

    ⚠️ **The bare module global cannot be used here.** PEP 562's ``__getattr__`` fires on
    *attribute access on the module object*, never on a global-name lookup inside a function
    defined in that module — so ``CHARS_PER_TOKEN`` written here would be a ``NameError``,
    not a config read. :func:`chars_per_token` is the in-module form and is what this calls.

    ``divisor`` is an optimisation with no semantics of its own: `config/` is deliberately
    uncached (:func:`whetstone_gate.config.load`), so a caller summing over three hundred
    message texts passes the value it already read rather than re-parsing the YAML three
    hundred times. Omitted, it is read. There is **no default divisor** — hard rule 9 — only
    a choice between reading it here and being handed the value the caller just read.
    """
    return estimate_characters(
        len(text), divisor=chars_per_token() if divisor is None else divisor
    )


def estimate_characters(characters: int, *, divisor: int) -> int:
    """The estimator's arithmetic, over a character COUNT rather than over the text.

    ⚠️ **Extracted so :class:`CrossoverSeries` cannot grow a second copy of it.** The series
    reasons about the cost of a 2,887-character listing it does not hold, and the honest way
    to give it that number is to hand it the same function :func:`estimate_text` runs — not a
    reimplementation of ``ceil(chars / divisor)`` four lines away that is free to drift. That
    is `INCIDENTS.md` **INC-41**'s lesson applied one level down: a figure derived twice is a
    figure that can disagree with itself.
    """
    if characters <= 0:
        return 0
    return math.ceil(characters / divisor)


def estimate_messages(texts: tuple[str, ...]) -> TokenEstimate:
    """Estimated tokens for a whole assembled context.

    Pure: same input, same output, no clock and no I/O. That matters because the summary
    cap is enforced with this function, and a non-deterministic cap would make the
    deterministic-summary claim false.
    """
    divisor = chars_per_token()  # read ONCE, then handed down — see estimate_text
    characters = sum(len(t) for t in texts)
    body = sum(estimate_text(t, divisor=divisor) for t in texts)
    return TokenEstimate(
        tokens=body + len(texts) * FRAMING_TOKENS_PER_MESSAGE,
        characters=characters,
        messages=len(texts),
    )


#: ⚠️ **THE FIXTURE THE CROSSOVER SERIES WAS MEASURED ON, NAMED — `INCIDENTS.md` INC-41.**
#:
#: `REVIEW_C6_2` could not reproduce the previous note's series *"because the note does not
#: say what fixture produced it"*, so BLOCKER B-1 had to be stated as *"the note contradicts
#: its own printed numbers"* rather than as *"its measurement was performed wrongly"*. **A
#: number C14 reads beside the pilot's when it selects §13.4's N branch has to be
#: reproducible**, so the fixture is written down here and a test regenerates the series from
#: it against the real world.
#:
#: ⚠️ **The seed is READ FROM `config/`, not written here.** It is `CONTEXT.md` §8.6's
#: ``seed list`` row (``seeds.scored_n50_first``), so a literal copy would be a hard-rule-9
#: tripwire failure — and the tripwire caught exactly that while this fixture was being
#: written, which is the mechanism working rather than a near miss worth hiding.
def crossover_fixture() -> str:
    """The fixture :data:`CROSSOVER_SERIES` was measured on, named so it can be rebuilt."""
    protocol = cfg.load("protocol")
    seed = protocol.require("seeds.scored_n50_first")
    return (
        f"FIXTURE 'seed-{seed} front-loaded': run_episode over the REAL seed-{seed} mock "
        f"world (world.generator.generate + world.semantics.build, no stand-in), at the "
        f"configured turn_budget / context_window_turns_verbatim / "
        f"context_summary_max_tokens / chars_per_token; system prompt data/attacker_sys.txt "
        f"verbatim; tool schemas = world.surface.TOOL_SURFACE joined with ', '; the attacker "
        f"emits 'fetch_payments(count=12)' every turn; the folded state is the all-zero fold "
        f"with only turns_remaining varying; k of the "
        f"{protocol.require('attacker.turn_budget')} turns return the full fetch_payments "
        f"listing and the rest return fetch_payment(<probe id>). The k reads are placed on "
        f"turns 0..k-1 - FRONT-LOADED, which is the DEAREST arrangement, since a result "
        f"produced at turn i is carried by min(window, turn_budget-1-i) later contexts."
    )


@dataclass(frozen=True)
class CrossoverSeries:
    """⚠️ **The crossover, DERIVED from the series rather than written beside it — `INC-41`.**

    `OPEN_FINDINGS.md` **OF-48** / `REVIEW_C6_1` **F-8** asked for the crossover to reach C14.
    The string that answered it published **7 full-listing reads** while its own printed
    series crossed at **9**, and `REVIEW_C6_2` BLOCKER **B-1** proved the disagreement three
    independent ways. **The remedy is not a corrected literal: it is that there is no longer
    a literal to correct.** :meth:`crossing` computes the figure from :meth:`tokens_at`, which
    computes from :meth:`tokens_per_read`, which computes from `config/` and the two character
    counts below — so the headline and the series are one computation and **cannot disagree**.

    ⚠️ **The linear model is not a fit; it is arithmetic, and it reproduces the measurement
    exactly.** ``assemble()`` runs **before** each turn's call, so a tool result produced at
    turn *i* appears in the contexts of turns *i+1 … i+window* and in no other context.
    Swapping a cheap result for the full listing therefore costs exactly
    ``window x (est(full) - est(displaced))`` **for as long as every read is far enough from
    the end of the episode to be carried by a whole window** — which is
    :meth:`linear_reads_limit` = ``turn_budget - window``. Measured against
    :func:`crossover_fixture`, the model is exact at every ``k`` up to that limit and
    over-states beyond it (the safe direction), and the crossing lands inside it.
    """

    base_tokens: int
    """Estimated prompt-side tokens for the whole episode at **zero** full-listing reads."""

    full_listing_chars: int
    """Characters in one ``fetch_payments(count:12)`` result on that fixture's world."""

    displaced_result_chars: int
    """Characters in the cheap result a full-listing read REPLACES on that fixture.

    ⚠️ **A read does not ADD a message, it CHANGES one**, so the marginal cost is a
    difference and not a total. Treating it as a total is how a bound of 5,802 tokens/read
    gets published where the real figure is 5,298.
    """

    def tokens_per_read(self, *, divisor: int, window: int) -> int:
        """The marginal cost of one more full-listing read. **Derived, never recorded.**"""
        return window * (
            estimate_characters(self.full_listing_chars, divisor=divisor)
            - estimate_characters(self.displaced_result_chars, divisor=divisor)
        )

    def tokens_at(self, reads: int, *, divisor: int, window: int) -> int:
        """Estimated episode tokens at ``reads`` full-listing reads."""
        if reads < 0:
            raise ValueError("reads cannot be negative")
        return self.base_tokens + reads * self.tokens_per_read(divisor=divisor, window=window)

    def linear_reads_limit(self, *, turn_budget: int, window: int) -> int:
        """The largest ``k`` for which every read is still carried by a whole window."""
        return max(0, turn_budget - window)

    def crossing(self, target: int, *, divisor: int, window: int, turn_budget: int) -> int | None:
        """The smallest number of reads whose estimate **exceeds** ``target``.

        ``None`` when no number of reads inside ``turn_budget`` crosses it — which is a real
        answer and must not be rendered as a number, because *"the budget is never exceeded"*
        and *"the budget is exceeded at k"* are different findings for C14.
        """
        per_read = self.tokens_per_read(divisor=divisor, window=window)
        for reads in range(0, turn_budget + 1):
            if self.tokens_at(reads, divisor=divisor, window=window) > target:
                return reads
        return None


#: The series, measured on :func:`crossover_fixture` with **this package's own estimator over
#: ``run_episode``'s own contexts**, and regenerated from the real seed-2001 world by
#: ``tests/test_c6_fix_probes.py::test_the_crossover_series_reproduces_against_the_REAL_seed_2001_world``.
CROSSOVER_SERIES = CrossoverSeries(
    base_tokens=16495,
    full_listing_chars=2887,
    displaced_result_chars=240,
)


def crossover_note() -> str:
    """⚠️ **What C14's pilot actually has to decide, carried in the estimate's own output.**

    ⚠️ **It is carried here rather than left in a review file because a reader of the estimate
    is the person who needs it.** The estimate's "realistic" regime assumes two list reads;
    three forces push above that, and all three are confirmed rather than asserted —
    `QUESTIONS.md` **Q-037** makes pagination **mandatory** (``fetch_payments`` returns
    Razorpay's documented first **10** of 12 and the probe is index **11**, so an
    argument-free call never shows the door), the six-turn window **EVICTS the payment list**
    so a listing read at turn *t* is gone by *t+7* (`REVIEW_C6_2` re-derived this as its
    vector V15), and §8.6's tradecraft paragraph says *"read every payment's notes"*.

    ⚠️ **NO BRANCH IS SELECTED HERE AND NONE MAY BE.** `CONTEXT.md` §13.4's rule is that the
    pilot's **measured** figure selects N, never an estimate and never a preference.

    ⚠️ **AND THE FIGURE IS COMPUTED, NOT WRITTEN — `INCIDENTS.md` INC-41.** Every number below
    falls out of :data:`CROSSOVER_SERIES` and `config/`. The previous form of this note
    published a crossover of **7** beside a series that crossed at **9**, and it was printed
    to an operator by :meth:`BudgetComparison.render` in that state.
    """
    protocol = cfg.load("protocol")
    divisor = chars_per_token()
    window = protocol.require("attacker.context_window_turns_verbatim")
    turn_budget = protocol.require("attacker.turn_budget")
    target = protocol.require("attacker.target_tokens_per_episode")
    series = CROSSOVER_SERIES
    per_read = series.tokens_per_read(divisor=divisor, window=window)
    limit = series.linear_reads_limit(turn_budget=turn_budget, window=window)
    k = series.crossing(target, divisor=divisor, window=window, turn_budget=turn_budget)
    if k is None:
        headline = (
            f"NO number of full-listing reads inside {turn_budget} turns crosses "
            f"{target:,} on this series"
        )
    else:
        headline = (
            f"{k} full-listing reads of {turn_budget} turns crosses {target:,} estimated "
            f"tokens ({series.tokens_at(k, divisor=divisor, window=window):,}); "
            f"{k - 1} reaches only "
            f"{series.tokens_at(max(k - 1, 0), divisor=divisor, window=window):,}"
        )
    points = "; ".join(
        f"{r} = {series.tokens_at(r, divisor=divisor, window=window):,}" for r in (0, 2, 3, 5)
    )
    return (
        f"CROSSOVER (OF-48; the figure is GENERATED from the series below, never written "
        f"beside it - INCIDENTS.md INC-41, REVIEW_C6_2 BLOCKER B-1): {headline}. "
        f"SERIES, reads = estimated tokens: {points}; marginal {per_read:,}/read = "
        f"window {window} x (ceil({series.full_listing_chars}/{divisor}) - "
        f"ceil({series.displaced_result_chars}/{divisor})), because assemble() runs BEFORE "
        f"each call so one result is carried by AT MOST {window} later contexts, and a read "
        f"REPLACES a cheap result rather than adding a message. The series is exact while "
        f"reads <= turn_budget - window = {limit} and over-states beyond it. "
        f"{crossover_fixture()} "
        f"Q-037 makes pagination MANDATORY (count:10 of 12, probe at index 11) and the "
        f"{window}-turn window EVICTS the payment list, so re-reads are structural, not "
        f"chattiness. NO BRANCH IS SELECTED HERE: CONTEXT.md 13.4 gives that to C14's "
        f"MEASURED figure."
    )


@dataclass(frozen=True)
class BudgetComparison:
    """An estimate set beside the §8.6 target — and it says which side is which."""

    estimated_tokens: int
    target_tokens: int
    """Read from ``config/protocol.yaml:attacker.target_tokens_per_episode``."""

    @property
    def within_target(self) -> bool:
        return self.estimated_tokens <= self.target_tokens

    def render(self) -> str:
        verdict = "WITHIN" if self.within_target else "OVER"
        return (
            f"ESTIMATED attacker tokens/episode: {self.estimated_tokens} "
            f"vs target {self.target_tokens} -> {verdict} "
            f"(ESTIMATE, not a measurement; C14's pilot measures the real figure and it "
            f"selects the N branch)\n"
            f"  !! PROMPT SIDE ONLY - completion tokens are NOT counted (OF-47): "
            f"800-8,000/episode uncounted, one-directional and LOW, which is CONTEXT.md "
            f"13.4's unsafe direction.\n"
            f"  {crossover_note()}"
        )
