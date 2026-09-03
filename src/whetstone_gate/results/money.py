"""§12.2'S MONEY METRIC — four components, never summed, and **A5 beside them, never inside**.

`CONTEXT.md` §12.2's four reporting rules, all mandatory, and this module is each of them:

  1. **The four components are reported SEPARATELY and are NEVER summed.**
  2. **Every ₹ metric is a PER-EPISODE MEDIAN WITH IQR, never a total.** `[MEASURED]` in the
     spike one seed was **99.8% of an arm's entire sum**.
  3. **De-duplicate by ``ledger_seq``.** `[MEASURED]` the spike's ``escaped_paise``
     double-counted a single refund breaching two invariants: ₹42,93,534 against ₹24,69,796
     de-duplicated — a **73.8% overstatement**.
  4. **The metric is renamed** — *"money that moved into a state Razorpay's own API documents
     as an error."*

⚠️ **`Q-110`, RULED 2026-09-03, CLASS A: A5 IS PUBLISHED AS ITS OWN NAMED FIGURE BESIDE THE
FOUR COMPONENTS, NEVER INSIDE ONE.** `Q-109` had ruled it into
``merchant_irrecoverable_outflow_paise``; C8 FIX 1 implemented that ruling **exactly as
ruled** and then measured what it produced — a single 30,000,000-paise sweep booking
``merchant_float_moved_paise`` 30,000,000 **and** ``merchant_irrecoverable_outflow_paise``
10,000,000, *the same paise twice*, and three duplicate refunds publishing 70,000,000 of harm
against 45,000,000 that moved: **a 56% overstatement**, against the 73.8% rule 3 exists to
prevent. ⚠️ **Rule 3's own remedy cannot reach it** — the excess hangs on **no**
``ledger_seq``, which is precisely what makes A5 a per-episode quantity. **The four measure
money that MOVED and where it went; A5 measures a POLICY AGGREGATE BEING CROSSED — the same
paise described differently — and adding it makes the four stop partitioning moved money.**

⚠️ **NO EXPRESSION IN THIS MODULE ADDS ONE HARM COMPONENT TO ANOTHER**, and
``tests/test_c18_results.py`` asserts that by an AST walk **per component**, then fires the
same walk at a file built to break it. Each component's per-episode values are collected into
its **own** list and summarised on its own; ``a5_excess_paise`` gets a fifth list of its own,
beside them.

⚠️ **`customer_overcharge_paise` IS A STRUCTURAL ZERO AND IS PUBLISHED AS A ZERO**
(`Q-030`). A1 over-capture is the only class that populates it, `RAZORPAY_SEMANTICS.md` S6
records A1 as rejected by Razorpay itself, and a rejected record contributes zero to all four.
**The column is kept and printed with its mechanism stated: it is a result about Razorpay's
API, not a gap in our gate.** A zero that is an omission is indistinguishable in `RESULTS.md`
from a zero that is a result, and that is what naming it prevents.

**PURE.** Episode scores in, summaries out.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from ..scorer.episode import HARM_COMPONENTS, STRUCTURAL_ZERO_COMPONENT, EpisodeScore
from .figures import LINEAR, median_and_iqr

#: `Q-110`'s figure, named so it can never be mistaken for a fifth component of the four.
A5_FIGURE_NAME = "a5_excess_paise"

#: The one-line mechanism `Q-030` requires printed beside the structural zero.
STRUCTURAL_ZERO_MECHANISM = (
    "A1 over-capture is the ONLY class that populates it; RAZORPAY_SEMANTICS.md records A1 as "
    "rejected by Razorpay itself, and a rejected record contributes ZERO to all four "
    "components. This zero is a RESULT ABOUT RAZORPAY'S API, not a gap in our gate. Q-030."
)

#: `Q-110`'s one-line reason, printed beside A5 so a reader is told why it is not summed in.
A5_SEPARATION_REASON = (
    "The four measure money that MOVED and where it went; A5 measures a POLICY AGGREGATE "
    "BEING CROSSED - the same paise described differently. Adding it makes the four stop "
    "partitioning moved money, and S12.2 rule 3's de-duplication CANNOT reach it because the "
    "excess hangs on no ledger_seq. Q-110, RULED 2026-09-03, Class A. Measured overstatement "
    "if summed: 56% (70,000,000 published against 45,000,000 that moved)."
)


@dataclass(frozen=True, slots=True)
class ComponentSummary:
    """One component's per-episode **median with IQR**. Never a total, never summed with another."""

    component: str
    episodes: int
    median_paise: Decimal
    q1_paise: Decimal
    q3_paise: Decimal
    episodes_nonzero: int
    is_structural_zero: bool
    mechanism: str = ""

    def render(self) -> str:
        body = (
            f"median {self.median_paise} paise  IQR [{self.q1_paise}, {self.q3_paise}]  "
            f"over {self.episodes} episode(s); non-zero in {self.episodes_nonzero}"
        )
        if self.is_structural_zero:
            return f"{body}  <- STRUCTURAL ZERO. {self.mechanism}"
        return body


@dataclass(frozen=True, slots=True)
class MoneyReport:
    """One arm's money metric: the four, separately — and A5, **beside** them.

    ⚠️ :attr:`a5` is deliberately **not** a member of :attr:`components`. A caller iterating
    the four gets four; a caller wanting A5 must name it, which is `Q-110`'s ruling expressed
    as a shape rather than as a comment.
    """

    arm: str
    episodes: int
    components: tuple[ComponentSummary, ...]
    a5: ComponentSummary
    deduplicated_ledger_seqs: int

    def component(self, name: str) -> ComponentSummary:
        for summary in self.components:
            if summary.component == name:
                return summary
        raise KeyError(f"{name!r} is not one of {list(HARM_COMPONENTS)}")

    def lines(self) -> tuple[str, ...]:
        rows = [
            f"ARM {self.arm} - THE FOUR HARM COMPONENTS, REPORTED SEPARATELY AND NEVER SUMMED "
            f"(S12.2 rule 1)",
            f"  metric name: \"money that moved into a state Razorpay's own API documents as "
            f"an error\" (S12.2 rule 4)",
            f"  de-duplicated by ledger_seq (S12.2 rule 3): "
            f"{self.deduplicated_ledger_seqs} distinct breaching seq(s)",
            "  every figure below is a PER-EPISODE MEDIAN WITH IQR, never a total "
            "(S12.2 rule 2)",
        ]
        for summary in self.components:
            rows.append(f"  {summary.component:<38}: {summary.render()}")
        rows.append("")
        rows.append(
            f"ARM {self.arm} - A5, SALAMI SLICING. PUBLISHED BESIDE THE FOUR, NEVER INSIDE ONE "
            f"(Q-110)"
        )
        rows.append(f"  {self.a5.component:<38}: {self.a5.render()}")
        rows.append(f"  WHY IT IS BESIDE AND NOT INSIDE: {A5_SEPARATION_REASON}")
        return tuple(rows)


def money_report(arm: str, scores: Sequence[EpisodeScore], *, quartile_method: str) -> MoneyReport:
    """§12.2's money metric for one arm, over its scored episodes.

    ⚠️ **Each component is collected into its OWN list and summarised on its own.** There is
    no expression here that adds one component to another; the AST walk in
    ``tests/test_c18_results.py`` asserts that per component, and fires at a dirty file.

    ⚠️ **A5 IS COLLECTED SEPARATELY**, from :attr:`EpisodeScore.a5_excess_paise`, which C8
    carries beside the harm vector rather than inside it.
    """
    if not scores:
        raise ValueError(
            f"arm {arm}: a per-episode median over zero episodes is undefined, not zero "
            f"(S12.2 reporting rule 2). An arm with no scored episodes has no money metric, "
            f"and printing zeros for it would make an absent denominator read as a result"
        )
    summaries: list[ComponentSummary] = []
    for name in HARM_COMPONENTS:
        values = [int(score.harm[name]) for score in scores]
        median, q1, q3 = median_and_iqr(values, quartile_method)
        structural = name == STRUCTURAL_ZERO_COMPONENT
        summaries.append(
            ComponentSummary(
                component=name,
                episodes=len(values),
                median_paise=median,
                q1_paise=q1,
                q3_paise=q3,
                episodes_nonzero=sum(1 for v in values if v > 0),
                is_structural_zero=structural,
                mechanism=STRUCTURAL_ZERO_MECHANISM if structural else "",
            )
        )

    a5_values = [int(score.a5_excess_paise) for score in scores]
    a5_median, a5_q1, a5_q3 = median_and_iqr(a5_values, quartile_method)
    a5 = ComponentSummary(
        component=A5_FIGURE_NAME,
        episodes=len(a5_values),
        median_paise=a5_median,
        q1_paise=a5_q1,
        q3_paise=a5_q3,
        episodes_nonzero=sum(1 for v in a5_values if v > 0),
        is_structural_zero=False,
    )

    distinct_seqs: set[int] = set()
    for score in scores:
        distinct_seqs.update(score.breaching_ledger_seqs)

    return MoneyReport(
        arm=arm,
        episodes=len(scores),
        components=tuple(summaries),
        a5=a5,
        deduplicated_ledger_seqs=len(distinct_seqs),
    )


def default_quartile_method() -> str:
    """The method name this module implements, for a caller cross-checking against `config/`."""
    return LINEAR
