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
⚠️ Q-058, RULED 2026-09-01 — THE *"TABLES 5–7"* CITATION NAMED THE WRONG TABLE
═══════════════════════════════════════════════════════════════════════════════════════
Branch B ships **as a citation**, so the citation *is* the artefact, and the one §8.5.1
carried did not survive being opened. **`CONTEXT.md` is amended to v1.8 and now names
Table 2, Appendix B, `o3 High` for the headline pair**, so what follows is no longer a
divergence between this module and the law — it is what the law says, with the record of
the correction kept because *the project publishes the number that goes the wrong way.*
Verified first-hand against the paper on 2026-09-01, and **re-verified independently at
build 2** from a second fetch of the same URL that reproduced the same 2,554,718 bytes and
the same SHA-256:

  * `CONTEXT.md` §4 and §8.5 state **CaMeL banking 81.2 % ± 19.1 vs native 62.5 % ± 23.7**
    and an all-suites Overall of **77 vs 84**. ✅ **Every one of those numbers is correct**,
    and correct for the model §4 names, ``o3 High``. They are in **Table 2 —
    "Utility results on the AgentDojo benchmark, covering different suites" — Appendix B,
    "Full results tables"**, whose own ``Difference`` row reads **+18.8 % ± 4.6** on
    banking, confirming the direction §4 describes.
  * **Tables 5–7 are Appendix C, "Baseline results"**, a comparison of CaMeL against *other
    defenses* using **Claude 3.5 Sonnet**. In their banking column CaMeL is **behind** the
    undefended model — 75.00 vs 81.25 without attack (Table 5) and 70.83 vs 84.03 under
    attack (Table 6).

So a Branch-B artefact that says *"cite Tables 5–7, banking column"* would point a panelist
at a table showing **the opposite of the claim it is offered to support** — in a submission
whose entire thesis is that other people's numbers are unsound.

⚠️ **ONE HALF OF THE CITATION IS RIGHT AND IS KEPT.** P2's factual basis — *"the
no-policies configuration fails it (1 successful attack, all of it in banking) and the
with-policies configuration blocks it"* — **is Table 7**, exactly as cited, and reproduces
exactly. The range 5–7 is right for P2 and wrong for the headline pair.

═══════════════════════════════════════════════════════════════════════════════════════
⚠️ THE GUARDRAIL Q-058's RULING INSTALLS, AND WHY IT IS A REFUSAL AND NOT A TEST
═══════════════════════════════════════════════════════════════════════════════════════
The ruling's generalisable half: *"`PROCESS.md` §9's URL-and-date rule catches a fact read
from the WRONG page. It does not catch a fact NOBODY READ A PAGE FOR. A URL to a paper is
not a URL to a table. FROM NOW ON, EVERY PUBLISHED THIRD-PARTY FIGURE CARRIES THE TABLE OR
FIGURE NUMBER, ITS APPENDIX, ITS BASE MODEL AND ITS ROW — not merely the paper's URL."*

:meth:`PublishedFigure.provenance_failures` is that rule, **format-checked rather than
merely non-empty**, and :func:`render_branch_b` **refuses to render** a figure that fails
it. Build 1 asserted the same four fields were truthy and never fired the assertion at a
figure missing one; **truthiness cannot tell `Table 2` from `Tables 5-7`**, and the whole
defect Q-058 records is a range where a single table belonged.

⚠️ **AND ONE HONESTY POINT THE RULE ITSELF FORCED INTO THE OPEN**, found at build 2 by
applying the new rule to this module's own figures: **Appendix C names no base model
anywhere.** Its entire prose is *"Appendix C Baseline results"*, Figure 18's caption, and
the three tables. `Claude 3.5 Sonnet` is attributed from **§6.3 "Baseline comparisons"** —
*"We compare CaMeL with other defenses implemented in AgentDojo … run with Claude 3.5
Sonnet"* — and from **Figure 11's caption**, whose sub-captions tie Table 5 and Table 7 to
that figure, with Figure 18's caption tying Table 6. So :attr:`PublishedFigure.
base_model_source` records **where the base model is asserted**, per figure, because a base
model taken from a different section of the paper than the table is *the same shape of
claim* Q-058 exists to stop — one level smaller, and in our own artefact.
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


#: A **single** numbered table or figure. ⚠️ A RANGE DOES NOT MATCH, and that is the point:
#: `Tables 5-7` is precisely the citation shape Q-058 records, and a check that accepted it
#: would be the check that failed to catch the defect it exists for.
TABLE_NUMBER = re.compile(r"(Table|Figure) \d+")

#: The appendix a table lives in, named as the paper names it: a letter, then its title.
APPENDIX = re.compile(r"Appendix [A-Z], .+")

#: How this figure's BASE MODEL is known. A table that states its own base model says so; a
#: table that does not must name the section or caption that does.
IN_TABLE = "stated in the table's own Model column"


@dataclass(frozen=True)
class PublishedFigure:
    """One number read out of the paper, with the provenance that makes it checkable.

    ⚠️ Every field below is **required**, and :meth:`provenance_failures` checks the four
    Q-058's ruling names — **table/figure number, appendix, base model, row** — by
    **format**, not by truthiness. A figure without provenance is `INCIDENTS.md`
    **INC-05**'s *"29 ms"*; a figure whose provenance is a *range* is Q-058 itself.
    """

    table: str
    appendix: str
    caption: str
    base_model: str
    base_model_source: str
    row: str
    suite: str
    value: str
    url: str = PAPER_HTML_URL
    fetched: str = FETCHED
    digest: str = FETCH_SHA256

    def provenance_failures(self) -> list[str]:
        """Every way this figure's provenance falls short of Q-058's rule. Empty is a pass.

        ⚠️ Returns a **list**, not a bool, so a failure names the field. A gate whose only
        output is *"no"* is a gate somebody edits out under time pressure.
        """
        problems: list[str] = []
        if not TABLE_NUMBER.fullmatch(self.table):
            problems.append(
                f"table={self.table!r} is not a single numbered table or figure. "
                f"Q-058: a RANGE - 'Tables 5-7' - is the exact citation shape that pointed "
                f"a reader at a table contradicting the claim it supported."
            )
        if not APPENDIX.fullmatch(self.appendix):
            problems.append(
                f"appendix={self.appendix!r} does not name an appendix and its title. "
                f"Table 2 and Table 5 are in DIFFERENT appendices measuring DIFFERENT "
                f"experiments, and that is the whole of Q-058."
            )
        if not self.base_model.strip():
            problems.append(
                "base_model is empty. Table 2's o3 High and Table 5's Claude 3.5 Sonnet "
                "disagree about which way CaMeL's banking column runs; a figure without a "
                "base model cannot be checked against either."
            )
        if not self.base_model_source.strip():
            problems.append(
                f"base_model_source is empty for base_model={self.base_model!r}. Appendix C "
                f"names no base model anywhere, so a Tables 5-7 figure must say WHERE its "
                f"base model is asserted or it is an unsourced claim in the artefact whose "
                f"whole subject is unsourced claims."
            )
        if not self.row.strip():
            problems.append(
                "row is empty. 'CaMeL' and 'Undefended model' are adjacent rows whose "
                "banking values are 75.00 and 81.25; Q-058's likely mechanism is exactly a "
                "row confusion."
            )
        if not self.suite.strip():
            problems.append("suite is empty; a value with no column is not a figure.")
        if not self.value.strip():
            problems.append("value is empty.")
        if not self.url.startswith("https://arxiv.org/"):
            problems.append(f"url={self.url!r} is not the arXiv source these were read from.")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", self.fetched):
            problems.append(f"fetched={self.fetched!r} is not an ISO-8601 date (PROCESS.md S9).")
        if not re.fullmatch(r"[0-9a-f]{64}", self.digest):
            problems.append(
                f"digest={self.digest!r} is not a SHA-256 of the bytes actually read. A URL "
                f"and a date identify a REQUEST; the digest identifies the RESPONSE."
            )
        return problems


_T2 = dict(
    table="Table 2",
    appendix="Appendix B, Full results tables",
    caption="Utility results on the AgentDojo benchmark, covering different suites.",
    base_model="o3 High",
    base_model_source=IN_TABLE,
)
#: ⚠️ Appendix C states NO base model. Tables 5 and 7 are tied to `Claude 3.5 Sonnet` by
#: Figure 11's caption and §6.3's *"run with Claude 3.5 Sonnet"*; Table 6 by Figure 18's
#: caption, which is Appendix C's only prose. Recorded per figure rather than assumed.
_C_MODEL_SOURCE_11 = (
    "NOT in Appendix C, which names no model: Figure 11's caption "
    '("...when using Claude 3.5 Sonnet") and S6.3 ("run with Claude 3.5 Sonnet")'
)
_C_MODEL_SOURCE_18 = (
    "NOT in Appendix C, which names no model: Figure 18's caption "
    '("...utility under attack for defenses. Full results in Table 6") over S6.3\'s '
    '"run with Claude 3.5 Sonnet"'
)
_T5 = dict(
    table="Table 5",
    appendix="Appendix C, Baseline results",
    caption="Defenses utility.",
    base_model="Claude 3.5 Sonnet",
    base_model_source=_C_MODEL_SOURCE_11,
)
_T6 = dict(
    table="Table 6",
    appendix="Appendix C, Baseline results",
    caption="Defenses utility under attack.",
    base_model="Claude 3.5 Sonnet",
    base_model_source=_C_MODEL_SOURCE_18,
)
_T7 = dict(
    table="Table 7",
    appendix="Appendix C, Baseline results",
    caption="Defenses: number of successful attacks.",
    base_model="Claude 3.5 Sonnet",
    base_model_source=_C_MODEL_SOURCE_11,
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


def assert_provenance(figures: tuple[PublishedFigure, ...]) -> None:
    """Refuse to publish a figure whose provenance falls short of Q-058's rule.

    ⚠️ **A REFUSAL, NOT AN ASSERTION.** Q-058's ruling makes the four fields a property of
    every published third-party figure; a property enforced only in a test file is a
    property that holds until somebody adds a figure without running the tests.
    """
    problems = [
        f"{figure.table} / {figure.row} / {figure.suite}: {problem}"
        for figure in figures
        for problem in figure.provenance_failures()
    ]
    if problems:
        raise BranchBError(
            "Branch B ships AS a citation, so a figure with incomplete provenance is a "
            "defect in the deliverable itself (Q-058):\n  " + "\n  ".join(problems)
        )


def _figure_table(figures: tuple[PublishedFigure, ...]) -> list[str]:
    """Render the four fields Q-058 requires, plus **where the base model is asserted**.

    ⚠️ The base-model source is a numbered legend rather than a repeated column. Repeating
    a 150-character provenance sentence on eleven rows makes the table unreadable, and an
    unreadable table is one nobody checks — which is how the citation this whole entry
    corrects survived in the first place.
    """
    sources: list[str] = []
    for figure in figures:
        if figure.base_model_source not in sources:
            sources.append(figure.base_model_source)

    rows = [
        "| Table | Appendix | Base model | Row | Suite | Value |",
        "|---|---|---|---|---|---|",
    ]
    rows += [
        f"| {f.table} | {f.appendix} | {f.base_model} [{sources.index(f.base_model_source) + 1}] "
        f"| {f.row} | {f.suite} | **{f.value}** |"
        for f in figures
    ]
    rows.append("")
    rows.append("**Where the base model is asserted** — ⚠️ *not always in the table:*")
    rows += [f"{index + 1}. {source}" for index, source in enumerate(sources)]
    return rows


def render_branch_b(context_md: str, base_url_hits: int, predictions: list[Prediction]) -> str:
    """Render the complete Branch-B artefact as markdown.

    Generated, not authored: the reason comes from `CONTEXT.md` §8.5.1 and the predictions
    from §8.5.2, so *"verbatim"* is a property of the pipeline rather than a claim.

    ⚠️ **It refuses before it renders.** Every published figure must carry Q-058's four
    fields in the right shape or nothing is produced at all.
    """
    assert_provenance(HEADLINE_FIGURES)
    assert_provenance(CITED_TABLE_FIGURES)
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
        "## 2. ⚠️ THE CITATION — **Table 2, Appendix B, `o3 High`** — with both table sets shown",
        "",
        "**This is what `CONTEXT.md` v1.8 §8.5.1 now specifies**, and §2b below is the",
        "citation it replaced. Both are printed because *the project publishes the number",
        "that goes the wrong way*: dropping the tables that embarrass the claim is the exact",
        "move this submission exists to criticise. See `QUESTIONS.md` **Q-058**.",
        "",
        f"Source: *{PAPER_TITLE}*, arXiv **{ARXIV_ID}** — {PAPER_URL}",
        f"Read from {PAPER_HTML_URL} on **{FETCHED}** ({FETCH_STATUS}), SHA-256 `{FETCH_SHA256}`.",
        "⚠️ **Fetched twice, by two sessions, and the byte count and digest reproduced",
        "exactly.** A URL and a date identify a *request*; the digest identifies the",
        "*response* (`PROCESS.md` §9, `INCIDENTS.md` **INC-05**).",
        "",
        "### 2a. ⚠️ THE HEADLINE PAIR — **Table 2, Appendix B (\"Full results tables\"), `o3 High`**",
        "",
        *_figure_table(HEADLINE_FIGURES),
        "",
        "✅ **Every number `CONTEXT.md` §4 and §8.5 state is correct, and correct for the",
        "model §4 names (`o3 High`).** On `banking` CaMeL is **ahead** by the paper's own",
        "`Difference` row, **+18.8 % ± 4.6** — which is what §4's *\"on banking alone it runs",
        "the other way\"* asserts. Only the **table attribution** was ever wrong, and it is",
        "corrected in the law rather than only here.",
        "",
        "### 2b. What **Tables 5–7** actually say — **Appendix C, Claude 3.5 Sonnet**",
        "",
        "⚠️ **These were §8.5.1's citation until v1.8 and they are NOT the headline pair.**",
        "They are a different experiment: CaMeL against *other defences*, on a different base",
        "model. They are shown in full, including the two rows that run against this",
        "project's own claim.",
        "",
        *_figure_table(CITED_TABLE_FIGURES),
        "",
        "⚠️ In Tables 5 and 6's banking column CaMeL is **behind** the undefended model —",
        "75.00 vs 81.25 and 70.83 vs 84.03. A Branch-B artefact citing *\"Tables 5–7, banking",
        "column\"* would point a panelist at a table showing the opposite of the claim it is",
        "offered to support.",
        "⚠️ **The likely mechanism, recorded as likely and not asserted as the cause:** Table",
        "5's **undefended** banking utility **81.25 % ± 19.12** sits one hundredth from",
        "CaMeL's Table 2 banking **81.2 % ± 19.1**.",
        "⚠️ **And Appendix C names no base model anywhere.** `Claude 3.5 Sonnet` comes from",
        "§6.3 and Figure 11's caption, which is why every row above is footnoted with **where",
        "its base model is asserted** rather than carrying an unsourced model name. A base",
        "model taken from a different section of the paper than the table is the same shape of",
        "claim Q-058 exists to stop — one level smaller, and in our own artefact.",
        "",
        "✅ **Table 7 IS correctly cited, and it is P2's basis, and it is RETAINED:** CaMeL",
        "blocks every attack in every suite (0), while **CaMeL (no policies) fails exactly",
        "one — and all of it is in banking.** That is `CONTEXT.md` §8.5.2's P2, reproduced",
        "exactly.",
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
