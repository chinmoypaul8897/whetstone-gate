"""N — A DECISION RULE, NOT A NUMBER. **BOTH ARITHMETICS, WHICH ONE BOUND, AND THE PILOT'S FIGURE.**

⚠️ **NO SESSION MAY SAY N IS DECIDED BEFORE THE PILOT.** `QUESTIONS.md` **Q-107**'s
*"regardless"* clause is **WITHDRAWN**, and `Q-121` is the measurement that withdrew it: the
rule's second conjunct can be read two ways and **they disagree below 31,909 measured
tokens/episode**. So this module prints what the rule *yields* under **both** readings and
**never** prints a selected branch that `config/` has not recorded.

`CONTEXT.md` §13.4, `PROTOCOL.md` §3 and `config/protocol.yaml`'s
``n_decision.branch_a_condition``, all verbatim on the same sentence:

    **N = 50 per arm per configuration IF the 31 Aug pilot's measured attacker tokens/episode
    is ≤ 60,000 AND the projected total Gemma lane-time is ≤ 32 h. Otherwise N = 30.**

`Q-107`, RULED, recorded verbatim in `QUESTIONS.md` before `runner/n_rule.py` was written:

    ⚠️ Q-107 IS RULED AND IT CHANGES A PUBLISHED NUMBER: §13.4's N rule has TWO conjuncts —
    tokens per episode ≤ 60,000 AND projected Gemma lane-time ≤ 32 h. … Implement BOTH
    conjuncts, record which one bound, and pin the boundary as INCLUSIVE at 60,000. **That
    limitation is published, not buried.**

⚠️ **THE ARITHMETIC IS NOT REIMPLEMENTED HERE.** It is C11's
:func:`whetstone_gate.runner.n_rule.select_n`, which carries both readings on one object
because *"record which one bound"* is a requirement rather than a courtesy. This module's whole
job is to **publish** it — including publishing the fact that, today, there is nothing to
publish because the pilot has not run.

**PURE.** A measured figure (or ``None``) in, lines out.
"""

from __future__ import annotations

from decimal import Decimal

from ..runner.n_rule import NDecision, limitation, select_n

#: ⚠️ `Q-121`'s **measured** break-even, printed whether or not the pilot has run. Below this
#: the two readings of the second conjunct select different N, and above it they agree.
#: Carried here as a published figure rather than as a comment, because `Q-107`'s ruling says
#: the limitation is *"published, not buried"* and a break-even nobody prints is buried.
BREAK_EVEN_TOKENS_PER_EPISODE = 31_908

#: What is printed while ``n_decision.measured_tokens_per_episode`` is ``TODO_C14_PILOT``.
PILOT_HAS_NOT_RUN = (
    "THE PILOT HAS NOT RUN, SO N IS NOT DECIDED AND THIS FILE DOES NOT DECIDE IT. "
    "`config/protocol.yaml`'s n_decision.measured_tokens_per_episode is the sentinel "
    "TODO_C14_PILOT and hard rule 9's loader RAISES on it, so there is no measured figure to "
    "evaluate the rule at. The calibration and the pilot are SINGLE-SHOT (CLAUDE.md S3): the "
    "first execution that runs to completion IS the run."
)


def lines(measured_tokens_per_episode: int | None) -> tuple[str, ...]:
    """§13.4's rule, published. **Both readings, which one bound, and the pilot's figure.**

    ``None`` is today's answer and is not an error: it means the pilot has not run, and every
    line below then says so rather than evaluating the rule at a number nobody measured.
    """
    rows: list[str] = [
        "N IS A DECISION RULE, NOT A NUMBER (CONTEXT.md S13.4; QUESTIONS.md Q-107 RULED, "
        "Q-121 MEASURED)",
        "",
        "  THE RULE: N = 50 per arm per configuration IF the pilot's MEASURED attacker "
        "tokens/episode is <= 60,000 AND the projected total Gemma lane-time is <= 32 h. "
        "Otherwise N = 30.",
        "",
        f"  PILOT'S MEASURED TOKENS/EPISODE : "
        f"{measured_tokens_per_episode if measured_tokens_per_episode is not None else 'NOT MEASURED'}",
        "",
    ]
    if measured_tokens_per_episode is None:
        rows.append(f"  !! {PILOT_HAS_NOT_RUN}")
        rows.append("")
        rows.append(
            "  BOTH ARITHMETICS ARE STILL NAMED, BECAUSE WHICH ONE BINDS IS A PUBLISHED "
            "QUESTION AND NOT A DETAIL:"
        )
        rows.append(
            "    RECOMPUTED (Q-107 option 2)          - the projection re-evaluated with the "
            "attacker's per-episode figure replaced by the MEASURED one. This is what Q-107's "
            "own published table does."
        )
        rows.append(
            "    AT THE REGISTERED TARGET (option 3)  - S13.4's own published table for the "
            "N=50 branch, computed at the pre-registered 60,000-token target: 40.05 h "
            "WHATEVER the pilot measures, so branch A is unreachable under this reading."
        )
        rows.append("")
        rows.append(
            f"  !! Q-121, MEASURED: the two readings DISAGREE. Under RECOMPUTED the second "
            f"conjunct HOLDS at any measured figure up to {BREAK_EVEN_TOKENS_PER_EPISODE:,} "
            f"tokens/episode (32.00 h) and FAILS from {BREAK_EVEN_TOKENS_PER_EPISODE + 1:,} "
            f"(32.01 h). Under AT-THE-REGISTERED-TARGET it fails at EVERY measurement. Golden "
            f"8 fixture F's own first vector is 24,310, which is BELOW the break-even - so at "
            f"that vector the two readings select DIFFERENT N."
        )
        rows.append("")
        rows.append(
            "  !! THE ARCHITECT'S 'REGARDLESS' CLAUSE IS WITHDRAWN. Q-107 read 'fails the "
            "second regardless of what the pilot measures'; Q-121 measured that this is TRUE "
            "under one arithmetic and FALSE under the other. NEITHER SIDE IS ADJUSTED TOWARD "
            "THE OTHER, and no session may say N is decided before the pilot."
        )
        rows.append("")
        rows.append(f"  THE LIMITATION, PUBLISHED AND NOT BURIED: {limitation()}")
        return tuple(rows)

    decision: NDecision = select_n(measured_tokens_per_episode)
    rows.extend(f"  {line}" for line in decision.lines())
    rows.append("")
    rows.append(
        f"  !! Q-121's BREAK-EVEN: {BREAK_EVEN_TOKENS_PER_EPISODE:,} tokens/episode. The "
        f"measured figure is "
        f"{'BELOW' if measured_tokens_per_episode <= BREAK_EVEN_TOKENS_PER_EPISODE else 'ABOVE'}"
        f" it, so the two readings of the second conjunct "
        f"{'DISAGREE' if not decision.readings_agree else 'AGREE'}."
    )
    if not decision.readings_agree:
        rows.append(
            "  !! THEY DISAGREE, AND NEITHER SIDE IS ADJUSTED TOWARD THE OTHER (Q-121). BOTH "
            "ARE PUBLISHED ABOVE: NDecision.n is the RECOMPUTED reading, because that is the "
            "one reproducing the architect's own Q-107 table on 4 of 4 vectors, and "
            "n_at_registered_target is the other, beside it."
        )
    rows.append("")
    rows.append(f"  THE LIMITATION, PUBLISHED AND NOT BURIED: {limitation()}")
    return tuple(rows)


def break_even() -> Decimal:
    """`Q-121`'s measured break-even, as a value a caller can compare against."""
    return Decimal(BREAK_EVEN_TOKENS_PER_EPISODE)
