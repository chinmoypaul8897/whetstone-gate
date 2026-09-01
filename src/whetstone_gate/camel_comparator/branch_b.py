"""The Branch-B artefact — built NOW, complete, so taking it is a selection not an authoring job.

`CONTEXT.md` §8.5.1 pre-declares two branches, and `PROCESS.md` §12.1 makes both a
precondition of RUN-1 rather than an outcome of it:

  * **Branch A** — the model id is still served and the run completes. The live table ships.
  * **Branch B** — the id is not served, or the run does not complete. The comparator ships
    as a **citation** of CaMeL's published numbers with a one-line reason **verbatim** from
    §8.5.1.

⚠️ **BRANCH B IS PUBLISHED AS A RESULT, NOT HIDDEN AS A FAILURE**, and `CONTEXT.md` §14's
degradation ladder pre-declares it at rung 6. **Both arms must exist before the run or the
choice is post-hoc**, which is why this module renders a finished artefact today, at zero
token cost, while nobody is under time pressure.

═══════════════════════════════════════════════════════════════════════════════════════
⚠️ Q-058, CLASS A — THE *"TABLES 5–7"* CITATION NAMES THE WRONG TABLE
═══════════════════════════════════════════════════════════════════════════════════════
Branch B ships **as a citation**, so the citation *is* the artefact, and this one does not
survive being opened. Verified first-hand against the paper on 2026-09-01:

  * `CONTEXT.md` §4 and §8.5 state **CaMeL banking 81.2 % ± 19.1 vs native 62.5 % ± 23.7**
    and an all-suites Overall of **77 vs 84**. ✅ **Every one of those numbers is correct**,
    and correct for the model §4 names, ``o3 High``. They are in **Table 2 —
    "Utility results on the AgentDojo benchmark, covering different suites" — Appendix B,
    "Full results tables"**, whose own ``Difference`` row reads **+18.8 % ± 4.6** on
    banking, confirming the direction §4 describes.
  * **Tables 5–7 are Appendix C, "Baseline results"**, a comparison of CaMeL against *other
    defenses* using **Claude 3.5 Sonnet** (stated in Figure 11's caption). In their banking
    column CaMeL is **behind** the undefended model — 75.00 vs 81.25 without attack
    (Table 5) and 70.83 vs 84.03 under attack (Table 6).

So a Branch-B artefact that says *"cite Tables 5–7, banking column"* would point a panelist
at a table showing **the opposite of the claim it is offered to support** — in a submission
whose entire thesis is that other people's numbers are unsound.

⚠️ **ONE HALF OF THE CITATION IS RIGHT AND IS KEPT.** P2's factual basis — *"the
no-policies configuration fails it (1 successful attack, all of it in banking) and the
with-policies configuration blocks it"* — **is Table 7**, exactly as cited, and reproduces
exactly. The range 5–7 is right for P2 and wrong for the headline pair.

`CONTEXT.md` is outside C13's fence and hard rule 2 makes a Class A change the architect's,
so **nothing is corrected there**. The artefact below carries §8.5.1's reason **verbatim**
and cites **both** tables with what each actually says, and `QUESTIONS.md` **Q-058** asks
for the ruling.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .predictions import Prediction

ARXIV_ID = "2503.18813v2"
PAPER_TITLE = "Defeating Prompt Injections by Design"
PAPER_URL = "https://arxiv.org/abs/2503.18813v2"
PAPER_HTML_URL = "https://arxiv.org/html/2503.18813v2"
FETCHED = "2026-09-01"
FETCH_STATUS = "HTTP 200, 2,554,718 bytes"
FETCH_SHA256 = "b5cd7970e905f1504439c3eddb3855ab18d951d10bf806ec2f5f3baa02ca8a51"
"""SHA-256 of the exact HTML rendering these figures were read out of.

⚠️ `PROCESS.md` §9: *every third-party claim carries a URL and a date.* A digest as well,
because a URL and a date identify a **request**, and what a later reviewer needs to check is
the **response**. `INCIDENTS.md` **INC-05** exists because a precise-sounding third-party
number was carried forward with neither.
"""


@dataclass(frozen=True)
class PublishedFigure:
    """One number read out of the paper, with the provenance that makes it checkable.

    ⚠️ Every field below is **required**, and
    ``test_every_published_figure_carries_url_date_and_digest`` asserts it. A figure
    without provenance is exactly `INCIDENTS.md` **INC-05**'s *"29 ms"*.
    """

    table: str
    appendix: str
    caption: str
    base_model: str
    row: str
    suite: str
    value: str
    url: str = PAPER_HTML_URL
    fetched: str = FETCHED
    digest: str = FETCH_SHA256


_T2 = dict(
    table="Table 2",
    appendix="Appendix B, Full results tables",
    caption="Utility results on the AgentDojo benchmark, covering different suites.",
    base_model="o3 High",
)
_T5 = dict(
    table="Table 5",
    appendix="Appendix C, Baseline results",
    caption="Defenses utility.",
    base_model="Claude 3.5 Sonnet",
)
_T6 = dict(
    table="Table 6",
    appendix="Appendix C, Baseline results",
    caption="Defenses utility under attack.",
    base_model="Claude 3.5 Sonnet",
)
_T7 = dict(
    table="Table 7",
    appendix="Appendix C, Baseline results",
    caption="Defenses: number of successful attacks.",
    base_model="Claude 3.5 Sonnet",
)

#: ⚠️ THE FIGURES CONTEXT.md ACTUALLY QUOTES — and the table they are actually in.
HEADLINE_FIGURES: tuple[PublishedFigure, ...] = (
    PublishedFigure(**_T2, row="CaMeL", suite="Overall", value="77.3% +/- 8.3"),
    PublishedFigure(**_T2, row="Native Tool Calling API", suite="Overall", value="84.5% +/- 7.2"),
    PublishedFigure(**_T2, row="CaMeL", suite="banking", value="81.2% +/- 19.1"),
    PublishedFigure(**_T2, row="Native Tool Calling API", suite="banking", value="62.5% +/- 23.7"),
    PublishedFigure(**_T2, row="Difference", suite="banking", value="+18.8% +/- 4.6"),
    PublishedFigure(**_T2, row="Difference", suite="Overall", value="-7.2% +/- 1.1"),
)

#: ⚠️ WHAT TABLES 5-7 ACTUALLY SAY - carried so the correction is checkable, not asserted.
CITED_TABLE_FIGURES: tuple[PublishedFigure, ...] = (
    PublishedFigure(**_T5, row="CaMeL", suite="Banking", value="75.00% +/- 21.22"),
    PublishedFigure(**_T5, row="Undefended model", suite="Banking", value="81.25% +/- 19.12"),
    PublishedFigure(**_T6, row="CaMeL", suite="Banking", value="70.83% +/- 7.42"),
    PublishedFigure(**_T6, row="Undefended model", suite="Banking", value="84.03% +/- 5.98"),
    PublishedFigure(**_T7, row="CaMeL", suite="Overall", value="0 +/- 0.0"),
    PublishedFigure(**_T7, row="CaMeL", suite="Banking", value="0 +/- 0.0"),
    PublishedFigure(**_T7, row="CaMeL (no policies)", suite="Overall", value="1 +/- 0.0"),
    PublishedFigure(**_T7, row="CaMeL (no policies)", suite="Banking", value="1 +/- 0.0"),
    PublishedFigure(**_T7, row="CaMeL (no policies)", suite="Slack", value="0 +/- 0.0"),
    PublishedFigure(**_T7, row="CaMeL (no policies)", suite="Travel", value="0 +/- 0.0"),
    PublishedFigure(**_T7, row="CaMeL (no policies)", suite="Workspace", value="0 +/- 0.0"),
)


class BranchBError(RuntimeError):
    """§8.5.1's Branch-B reason could not be read, so it cannot be carried verbatim."""


@dataclass(frozen=True)
class BranchBArtefact:
    """The finished Branch-B publication."""

    reason_verbatim: str
    base_url_hit_count: int
    predictions: list[Prediction]
    markdown: str


def branch_b_reason(context_md: str) -> str:
    """§8.5.1's one-line Branch-B reason, **verbatim**.

    ⚠️ Parsed, never transcribed. §8.5.1 requires it *"verbatim"*, and a copy in first-party
    source is a second version that can drift from the pre-registered one without anybody
    noticing — which is the failure this whole chunk is built against.
    """
    lines = context_md.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("### 8.5.1 ")]
    if len(starts) != 1:
        raise BranchBError("'### 8.5.1 ' does not occur exactly once in CONTEXT.md.")
    end = next(
        (i for i in range(starts[0] + 1, len(lines)) if lines[i].startswith("## ")), len(lines)
    )
    body = re.sub(r"\s+", " ", "\n".join(lines[starts[0] : end]))
    matches = re.findall(r'\*"(CaMeL dispatches only to[^"]+)"\*', body)
    if len(matches) != 1:
        raise BranchBError(
            f"CONTEXT.md S8.5.1 states {len(matches)} Branch-B reason(s), not one. Branch B "
            f"ships that sentence VERBATIM; carrying none of it, or the wrong one, would "
            f"publish a reason nobody pre-registered."
        )
    return matches[0]


def _figure_table(figures: tuple[PublishedFigure, ...]) -> list[str]:
    rows = ["| Table | Base model | Row | Suite | Value |", "|---|---|---|---|---|"]
    rows += [
        f"| {f.table} | {f.base_model} | {f.row} | {f.suite} | **{f.value}** |" for f in figures
    ]
    return rows


def render_branch_b(context_md: str, base_url_hits: int, predictions: list[Prediction]) -> str:
    """Render the complete Branch-B artefact as markdown.

    Generated, not authored: the reason comes from `CONTEXT.md` §8.5.1 and the predictions
    from §8.5.2, so *"verbatim"* is a property of the pipeline rather than a claim.
    """
    reason = branch_b_reason(context_md)
    lines: list[str] = [
        "# Comparator: CaMeL on AgentDojo banking — BRANCH B (citation)",
        "",
        "> ⚠️ **This artefact is pre-built. Taking Branch B on the night is a SELECTION, not",
        "> an authoring job under time pressure.** `CONTEXT.md` §8.5.1 pre-declares both",
        "> branches and `PROCESS.md` §12.1 requires both to exist before RUN-1, or the choice",
        "> is post-hoc. `CONTEXT.md` §14 pre-declares it at rung 6 of the degradation ladder.",
        "",
        "> ⚠️ **BRANCH B IS PUBLISHED AS A RESULT, NOT HIDDEN AS A FAILURE.**",
        "",
        "## 1. The reason, verbatim from `CONTEXT.md` §8.5.1",
        "",
        f"> *\"{reason}\"*",
        "",
        "**Re-verified first-hand at the pin on 2026-09-01, not carried on trust:**",
        "",
        f"* `grep -rn \"base_url\" --include=*.py .` over the whole CaMeL repository returns",
        f"  **{base_url_hit_count_phrase(base_url_hits)}**. There is no OpenAI-compatible",
        "  endpoint override, so a free-tier Groq endpoint is unreachable — and patching one",
        "  in would mean this project is no longer running CaMeL **unmodified**, which",
        "  forfeits §8.5's entire resolution.",
        "* The dispatch at `models.py:100-127` admits `google` / `openai` / `anthropic` and",
        "  `raise ValueError(\"Invalid model\")` otherwise. It is the **real** gate;",
        "  `_supported_model_names` is a lookup table merged into AgentDojo's `MODEL_NAMES`",
        "  at `models.py:67` to answer injection tasks' *\"what model are you?\"*.",
        "",
        "## 2. ⚠️ THE CITATION — corrected, with both tables shown",
        "",
        "**`CONTEXT.md` §8.5.1 says to cite *Tables 5–7*. The headline banking pair is not in",
        "them.** Both halves are shown here so a reader can check the correction rather than",
        "take it. See `QUESTIONS.md` **Q-058**.",
        "",
        f"Source: *{PAPER_TITLE}*, arXiv **{ARXIV_ID}** — {PAPER_URL}",
        f"Read from {PAPER_HTML_URL} on **{FETCHED}** ({FETCH_STATUS}), SHA-256 `{FETCH_SHA256}`.",
        "",
        "### 2a. The figures `CONTEXT.md` §4 and §8.5 actually quote — **Table 2, Appendix B**",
        "",
        *_figure_table(HEADLINE_FIGURES),
        "",
        "✅ **Every number §4 states is correct, and correct for the model §4 names (`o3",
        "High`).** On banking CaMeL is **ahead** by the paper's own `Difference` row,",
        "**+18.8 % ± 4.6** — which is what §4's *\"on banking alone it runs the other way\"*",
        "asserts. Only the **table attribution** is wrong.",
        "",
        "### 2b. What **Tables 5–7** actually say — **Appendix C, Claude 3.5 Sonnet**",
        "",
        *_figure_table(CITED_TABLE_FIGURES),
        "",
        "⚠️ In Tables 5 and 6's banking column CaMeL is **behind** the undefended model. A",
        "Branch-B artefact citing *\"Tables 5–7, banking column\"* would point a panelist at a",
        "table showing the opposite of the claim it is offered to support.",
        "",
        "✅ **Table 7 IS correctly cited, and it is P2's basis:** CaMeL blocks every attack in",
        "every suite (0), while **CaMeL (no policies) fails exactly one — and all of it is in",
        "banking.** That is `CONTEXT.md` §8.5.2's P2, reproduced exactly.",
        "",
        "## 3. What this comparator does and does not claim",
        "",
        "* It is **CaMeL's own benchmark, CaMeL's own policies, unmodified** — the empty diff",
        "  in `camel_unmodified.txt` is the proof, and a test regenerates it.",
        "* It is **never merged into `CONTEXT.md` §12's five-arm table.** Different agent,",
        "  different world, different answer key.",
        "* CaMeL enforces **provenance, not magnitude**. Re-verified at the pin: every `>` in",
        "  `src/camel/pipeline_elements/security_policies/` is a `->` return annotation, and",
        "  the one relational operator in `security_policy.py` is `len(...) > 0` — a list",
        "  length, not an amount. `send_money_policy` *does* read `kwargs[\"amount\"]`",
        "  (`banking.py:73-74`), but only to ask **who may read it**.",
        "",
        "## 4. The pre-registered predictions, carried verbatim from `CONTEXT.md` §8.5.2",
        "",
        "⚠️ **Pre-registered by being in `CONTEXT.md`.** Nothing here registers them and",
        "nothing here scores them — **C18 scores them.**",
        "",
    ]
    for prediction in predictions:
        lines += [f"> {prediction.text}", ""]
    lines += [
        "⚠️ **Under Branch B, P1 and P2's *denial-string* halves are UNMEASURED and are",
        "reported as such** — no run means no denial strings. What Branch B can still report",
        "is P2's published half (Table 7, above) and P3's *structural* half: there is **no",
        "aggregate symbol in the engine to name**, re-derived at the pin rather than repeated.",
        "**A zero-occurrence branch is printed as a zero, never omitted** (`PROCESS.md` §9).",
        "",
    ]
    return "\n".join(lines) + "\n"


def base_url_hit_count_phrase(count: int) -> str:
    """Render the grep count so **zero is printed as a number**, never as silence."""
    return "ZERO hits" if count == 0 else f"{count} hit(s)"
