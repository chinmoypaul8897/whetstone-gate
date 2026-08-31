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

*The parameters are IMPLEMENTATION CHOICES, not spec constants.* `CONTEXT.md` §8.6 fixes
no estimation method, and the ruling above is what puts the choice here. They are recorded
as a **Class B** deviation (hard rule 2) in ``docs/sessions/c6-build-1.txt``: an
implementation choice within spec, done, recorded with its rationale, judged at review.
They are **not** §8.6 rows and must never be added to `config/` — a frozen
pre-registration artefact is for values that decide a published number, and this one is
superseded by C14's measurement before any scored episode runs.

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

#: Characters per token. An implementation parameter, NOT a `CONTEXT.md` §8.6 constant —
#: see this module's docstring.
#:
#: ⚠️ **Three, not the conventional four.** The conventional four is calibrated on prose;
#: this project's contexts are dominated by the JSON `fetch_payments` returns, which
#: measured **2.97** characters per BPE token against the real seed-2001 world. At four the
#: estimator ran 25% **LOW**, and low is the unsafe direction for the one number that
#: selects §13.4's N branch.
CHARS_PER_TOKEN = 3

#: Per-message framing allowance — role markers and delimiters that every chat API adds
#: around a message and that the character count of the message body does not see. An
#: implementation parameter, as above.
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
        "ceil(chars / CHARS_PER_TOKEN) + messages * FRAMING_TOKENS_PER_MESSAGE. "
        "NOT a provider measurement. C14's pilot measures the real figure and it "
        "selects the N branch (CONTEXT.md 13.3, 13.4; QUESTIONS.md Q-031)."
    )

    def __str__(self) -> str:  # pragma: no cover - reporting convenience
        return f"~{self.tokens} tokens (ESTIMATE, {self.characters} chars)"


def estimate_text(text: str) -> int:
    """Estimated tokens for one string. Deterministic and pure."""
    if not text:
        return 0
    return math.ceil(len(text) / CHARS_PER_TOKEN)


def estimate_messages(texts: tuple[str, ...]) -> TokenEstimate:
    """Estimated tokens for a whole assembled context.

    Pure: same input, same output, no clock and no I/O. That matters because the summary
    cap is enforced with this function, and a non-deterministic cap would make the
    deterministic-summary claim false.
    """
    characters = sum(len(t) for t in texts)
    body = sum(estimate_text(t) for t in texts)
    return TokenEstimate(
        tokens=body + len(texts) * FRAMING_TOKENS_PER_MESSAGE,
        characters=characters,
        messages=len(texts),
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
            f"selects the N branch)"
        )
