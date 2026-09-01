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


def __getattr__(name: str) -> int:
    """PEP 562: resolve :data:`CHARS_PER_TOKEN` from `config/` on access. No default."""
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
    if not text:
        return 0
    return math.ceil(len(text) / (chars_per_token() if divisor is None else divisor))


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


#: ⚠️ **What C14's pilot actually has to decide, carried in the estimate's own output.**
#:
#: `OPEN_FINDINGS.md` **OF-48** / `REVIEW_C6_1` **F-8**. C6 published *"~25,200 realistic
#: (WITHIN, with room)"* against *"~126,600 worst case"*. The review re-derived the whole
#: curve against **two** independent BPE vocabularies over ``run_episode``'s own contexts and
#: found the number that matters: **the crossover past the 60,000 target is at SEVEN
#: full-listing reads out of twenty turns** — six by this estimator, which errs high.
#:
#: ⚠️ **It is carried here rather than left in a review file because a reader of the estimate
#: is the person who needs it.** The estimate's "realistic" regime assumes two list reads; the
#: review measured three forces pushing well above that — Q-037 makes pagination mandatory
#: (``fetch_payments`` returns Razorpay's documented first **10** of 12 and the probe is index
#: **11**, so an argument-free call never shows the door), the six-turn window **evicts the
#: payment list** so a listing read at turn *t* is gone by *t+7*, and the tradecraft paragraph
#: says *"read every payment's notes"*. Measured: window-forced re-reads ≈ **33,665**;
#: tradecraft-faithful ≈ **42,860**; re-list every second turn ≈ **71,107, OVER**.
#:
#: ⚠️ **NO BRANCH IS SELECTED HERE AND NONE MAY BE.** `CONTEXT.md` §13.4's rule is that the
#: pilot's **measured** figure selects N, never an estimate and never a preference. This
#: string is the crossover and the forces, so C14 reads them beside the number rather than
#: having to rediscover them.
CROSSOVER_NOTE = (
    "CROSSOVER (OF-48, measured by REVIEW_C6_1 against cl100k_base and o200k over this "
    "loop's own contexts): 7 full-listing reads of 20 turns crosses 60,000 true tokens "
    "(6 by this estimator). 0 reads = 12,393; 2 = 24,036 (this estimator's 'realistic'); "
    "3 window-forced re-reads = 33,665; tradecraft-faithful = 42,860; every 2nd turn = "
    "71,107 OVER. Q-037 makes pagination MANDATORY (count:10 of 12, probe at index 11) and "
    "the 6-turn window EVICTS the payment list, so re-reads are structural, not chattiness. "
    "NO BRANCH IS SELECTED HERE: CONTEXT.md 13.4 gives that to C14's MEASURED figure."
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
            f"  {CROSSOVER_NOTE}"
        )
