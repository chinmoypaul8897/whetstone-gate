"""**THE RUN REPORT — per model, never pooled; every zero printed.**

`CLAUDE.md` hard rule 12: *"Report actual tokens **by model**."*
`CLAUDE.md` hard rule 11: *"Every dropped episode is counted, categorised and printed as a
number."*
`PROCESS.md` §9: *"Zero-occurrence branches are printed as zeros, never omitted. A reader must
distinguish 'did not happen' from 'was not checked.'"*

**PURE.** It formats values it is handed. It reads no file and no clock.

⚠️ **ASCII, AT THE BOUNDARY.** Everything here is plain ASCII and the caller prints it through
:func:`whetstone_gate._console.say`, which transliterates. The operator runs these targets in
Git Bash on Windows, where the console codepage mangles this project's typography — and *"a
report the operator cannot read is a report that does not get read"*.

--------------------------------------------------------------------------------------
⚠️ THE POOLED TOTAL IS PRINTED, AND IT IS PRINTED AS A DISCRIMINATOR
--------------------------------------------------------------------------------------

Golden 8 fixture E is the one that separates a correct implementation from a plausible one:
two lanes at 60,000 and 50,000 pool to **110,000** — over a 100,000 ceiling — while **neither
exceeds it alone**, and the correct outcome is *"BOTH LANES CONTINUE"*. The golden records
that the architect's **first** version of that fixture used 30,000 × 3, and that it
*"discriminates NOTHING"* because both readings return the same answer.

So :func:`pooled_total_for_disclosure` exists, and its name is the argument: a report that
printed only per-model figures could not show a reader that the pooled figure was **over** and
the lanes **continued anyway**, which is the evidence that the ceilings are per model. It is
a **disclosure**, never an input — nothing in this package compares it to a ceiling, and
:func:`per_model_lines` is what hard rule 12 asks for.
"""

from __future__ import annotations

from typing import Mapping

from .budget import STOP_REASONS, LaneBudget
from .episodes import RunDenominator


def per_model_lines(budgets: Mapping[str, LaneBudget]) -> list[str]:
    """Hard rule 12's *"Report actual tokens BY MODEL"*, as lines. **Sorted, every model.**"""
    lines = [
        "PER-MODEL TOKEN AND CALL ACCOUNTING  (hard rule 12: ceilings are PER MODEL)",
        f"  {'model':<18}{'calls':>7}/{'ceil':<7}{'tokens':>12}/{'ceiling':<12}  stopped by",
    ]
    for name in sorted(budgets):
        budget = budgets[name]
        lines.append(
            f"  {name:<18}{budget.calls_used:>7}/{budget.ceilings.call_ceiling:<7}"
            f"{budget.tokens_spent:>12,}/{budget.ceilings.token_ceiling:<12,}  "
            f"{budget.stopped_by or '-'}"
        )
        lines.append(
            f"  {'':<18}{'unused:':>7} {budget.calls_unused:<7}"
            f"{'unspent:':>12} {budget.tokens_unspent:<12,}  "
            f"429s: {budget.rate_limited}"
        )
    return lines


def pooled_total_for_disclosure(budgets: Mapping[str, LaneBudget]) -> int:
    """The sum across models. ⚠️ **A DISCLOSURE, NEVER A CEILING INPUT.**

    Named at length on purpose. Golden 8 fixture E: pooling aborts a lane that has budget, and
    *"that is the same class of error as fixture D's converse and it costs the run episodes it
    was entitled to."* Nothing in this package compares this number to a ceiling; it exists so
    a report can state it and show that no lane stopped because of it.
    """
    return sum(budget.tokens_spent for budget in budgets.values())


def pooling_discriminator_lines(
    budgets: Mapping[str, LaneBudget], token_ceiling: int
) -> list[str]:
    """State the pooled figure **against** the per-model outcome. Golden 8 fixture E's shape.

    Prints, in terms: what the pooled total is, whether it exceeds the ceiling, whether any
    single model does, and what actually happened. A reader can then tell a per-model
    implementation from a pooling one **from the report alone**, which is what the golden's
    own corrected fixture is for.
    """
    pooled = pooled_total_for_disclosure(budgets)
    largest = max((b.tokens_spent for b in budgets.values()), default=0)
    return [
        "POOLED-VS-PER-MODEL DISCRIMINATOR  (golden 8 fixture E)",
        f"  pooled total across {len(budgets)} model(s) : {pooled:,}",
        f"  pooled exceeds the ceiling          : {pooled > token_ceiling}",
        f"  any SINGLE model exceeds it         : {largest > token_ceiling}",
        f"  lanes stopped by a POOLED total     : 0   (this package has no such code path)",
        "  ! A POOLING implementation aborts a lane that has budget. The pooled figure is a "
        "DISCLOSURE, never a ceiling input.",
    ]


def stop_reason_lines(budgets: Mapping[str, LaneBudget]) -> list[str]:
    """Every declared stop reason and its count, **including the zeros**."""
    counts = {reason: 0 for reason in STOP_REASONS}
    for budget in budgets.values():
        if budget.stopped_by in counts:
            counts[budget.stopped_by] += 1
    lines = ["LANES STOPPED, BY REASON  (every declared reason, including the zeros)"]
    lines.extend(f"  {reason:<26}: {count}" for reason, count in counts.items())
    lines.append(f"  {'still running':<26}: {sum(1 for b in budgets.values() if not b.stopped)}")
    return lines


def denominator_lines(denominator: RunDenominator) -> list[str]:
    """Hard rule 11's counter. **A truncated episode is counted in the denominator.**"""
    return ["EPISODE DENOMINATOR  (hard rule 11 / Razorpay B.9)", *
            (f"  {line}" for line in denominator.lines())]


def render_run_report(
    *,
    budgets: Mapping[str, LaneBudget],
    denominator: RunDenominator,
    token_ceiling: int,
    limitations: list[str],
) -> str:
    """The whole report as one ASCII block.

    ``limitations`` is a **required** argument with no default. `Q-107`'s ruling ends *"That
    limitation is published, not buried"*, and a default of ``[]`` is precisely how a
    limitation gets buried — by a caller that forgets it and a signature that lets them.
    """
    lines: list[str] = ["=" * 78, "WHETSTONE GATE - RUN REPORT", "=" * 78, ""]
    lines.extend(per_model_lines(budgets))
    lines.append("")
    lines.extend(pooling_discriminator_lines(budgets, token_ceiling))
    lines.append("")
    lines.extend(stop_reason_lines(budgets))
    lines.append("")
    lines.extend(denominator_lines(denominator))
    lines.append("")
    lines.append("LIMITATIONS, PUBLISHED  (not buried)")
    if not limitations:
        lines.append("  (none stated by the caller)")
    for text in limitations:
        lines.append(f"  - {text}")
    lines.append("=" * 78)
    return "\n".join(lines)
