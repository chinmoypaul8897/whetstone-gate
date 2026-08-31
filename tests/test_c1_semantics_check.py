"""⚠️ `RAZORPAY_SEMANTICS.md` §0's *"re-runnable check"* — **implemented**.

`docs/reviews/OPEN_FINDINGS.md` **OF-15** and **OF-16**; C1 REVIEW findings **F-R5** and
**F-R6**. Committed by C1 FIX (`SESSION-TOKEN: 365deaf7`), 2026-08-31.

**Until this file existed, §0 published a check with NO IMPLEMENTATION ANYWHERE** — not in
``tests/``, not in ``src/``, not a ``Makefile`` target. ⚠️ **That is `INCIDENTS.md`
INC-13's own lesson landing on the document that cites it**: §0 invokes INC-13 — *"a `0x08`
backspace that sat in `CONTEXT.md` for two days … because nothing checked a tracked
document's content"* — as the reason the convention *"mattered enough to fix rather than to
note"*, **and then the fix was performed and not kept.** `make test` could not detect a
paraphrase in the project's oracle.

**Three defects in the check AS SPECIFIED are fixed here, not carried** (F-R6):

  (i)   It matched each quoted line against **ANY** source in §1, never against **the source
        the row itself cites**. A documented ``409`` rewritten to ``400`` leaves the payload
        ``* code: 400``, which occurs **8×** in one source alone; and RS-22 given RS-23's
        ``solution`` is **still a verbatim Razorpay quote, from the wrong page**.
  (ii)  It passed **vacuously over an empty payload**: three ``>`` lines reduce to ``""`` and
        ``"" in s`` is ``True`` for every source, so emptying a row's quote is the cheapest
        way to destroy it while keeping the check green.
  (iii) Its stripping rule said *"the **three**-field labels"* while listing **four**. Read
        as *unwrap the bold* the check reports **3 unmatched**; read as *remove the label*
        it reports **0**, and only the second reproduces §0's published result.

⚠️ **WHAT THIS FILE HONESTLY CANNOT DO, SAID FIRST AND COUNTED (hard rule 11).** The
verbatim half needs the **ten fetched pages and two pinned source trees**, and this
repository **does not vendor them**; re-fetching inside ``make test`` would make the suite
depend on razorpay.com being reachable, which is a worse property than the one it buys. So
**300 of the 301 non-empty quoted lines cannot have their bytes checked here** — that number
is asserted below rather than left as a silence, and **`OF-15` stays OPEN on that half**.
The remaining choice — vendor ~112 KB under ``tests/fixtures/`` or accept the gap in writing
— **is the architect's**, and §0 now carries the "in writing" version.

**What IS closed offline, and one of them the review expected only a re-fetch could catch:**

  * **no empty payload** — kills mutant **M-10** by a second, independent route;
  * **every quoted line belongs to a row, and that row cites a source that exists** — the
    structural half of source-binding;
  * ⚠️ **every row's declared ``HTTP`` code equals the ``code:`` line inside its own quote** —
    this **kills mutant M-03 offline**, which `REVIEW_C1_1.md` records as caught by
    **NOTHING**;
  * **§8's quote of `CONTEXT.md` matched byte-for-byte against `CONTEXT.md`**, source-bound —
    the one source this repository holds, and the end-to-end proof that the matcher works;
  * **§0's own published counts regenerate.**

**Still caught by nothing, and named rather than omitted:** **M-06** (a wrong ``file:line``)
and **M-12** (a remediation lifted from the wrong page). M-12 is the worst of the set exactly
because it remains a **verbatim Razorpay quote** — only bytes from the cited page can catch
it.
"""

from __future__ import annotations

import re

import pytest

# §0's four added field labels. ⚠️ FOUR, not three: §0 said "three" and listed four, and the
# published result only reproduces under "remove the label entirely" (F-R6 iii).
ADDED_FIELD_LABELS = ("**error:**", "**code:**", "**description:**", "**solution:**")
_LABEL_RE = re.compile("|".join(re.escape(x) for x in ADDED_FIELD_LABELS))

#: §0's declared scope: "Counted over §1 onward".
SCOPE_HEADING = "## 1. Sources"


@pytest.fixture(scope="module")
def oracle(repo_root):
    return (repo_root / "RAZORPAY_SEMANTICS.md").read_text(encoding="utf-8").split("\n")


def _scope(lines: list[str]) -> list[tuple[int, str]]:
    """(index, line) for every line from §1 onward — §0's own scope, reproduced exactly."""
    start = next(i for i, ln in enumerate(lines) if ln.startswith(SCOPE_HEADING))
    return list(enumerate(lines))[start:]


def _payload(line: str) -> str:
    """Reduce one ``>`` line exactly as §0 specifies: strip ``>``, the four labels, one
    layer of wrapping backticks."""
    text = _LABEL_RE.sub("", line[1:]).strip()
    if len(text) >= 2 and text.startswith("`") and text.endswith("`"):
        text = text[1:-1]
    return text


def _quoted(lines: list[str]) -> list[tuple[int, str]]:
    return [(i, _payload(ln)) for i, ln in _scope(lines) if ln.startswith(">")]


def _row_at(lines: list[str], index: int) -> str | None:
    """The ``RS-nn`` whose body contains this line, or ``None`` if it is in no row.

    A ``## `` heading ends a row: §6's table rows and §8's block quote are deliberately
    outside every ``### RS-nn`` body, and the tests below treat them as named exceptions
    rather than pretending they belong to a row.
    """
    current = None
    for i, line in enumerate(lines):
        if i > index:
            break
        m = re.match(r"^### (RS-\d+)", line)
        if m:
            current = m.group(1)
        elif line.startswith("## "):
            current = None
    return current


def _declared_sources(lines: list[str], row: str) -> set[str]:
    """Every ``S<n>`` named in ``row``'s ``**Source**`` field."""
    start = next(i for i, ln in enumerate(lines) if ln.startswith(f"### {row} "))
    end = next(
        (
            i
            for i in range(start + 1, len(lines))
            if lines[i].startswith("### ") or lines[i].startswith("## ")
        ),
        len(lines),
    )
    body = "\n".join(lines[start:end])
    field = re.search(r"\*\*Source\*\*(.*?)(?:·|\n\*\*|\n\n)", body, re.S)
    return set(re.findall(r"\bS(\d{1,2})\b", field.group(1))) if field else set()


# ── (ii) the empty-payload hole — mutant M-10, by a second route ──────────────────────


def test_no_quoted_line_reduces_to_an_empty_payload_outside_a_multiline_quote(oracle):
    """⚠️ **F-R6(ii).** ``"" in s`` is ``True`` for every source on earth.

    Emptying a row's quote to a bare ``>`` is the cheapest way to destroy it while keeping a
    substring check green — **mutant M-10**, which `REVIEW_C1_1.md` records as caught only by
    that review's own probe. §0's sentence said *"take every line beginning with `>`"* with no
    blank-line exception, so as specified the check would have accepted the emptied row.

    A blank ``>`` is legitimate **only** as a separator inside a multi-line quote — it must
    have a non-empty quoted line both above and below it. A trailing or leading blank is a
    destroyed quote.
    """
    lines = [ln for _, ln in _scope(oracle)]
    offenders = []
    for pos, line in enumerate(lines):
        if not line.startswith(">") or _payload(line) != "":
            continue
        before = pos > 0 and lines[pos - 1].startswith(">") and _payload(lines[pos - 1])
        after = (
            pos + 1 < len(lines)
            and lines[pos + 1].startswith(">")
            and _payload(lines[pos + 1])
        )
        if not (before and after):
            offenders.append(line)
    assert not offenders, (
        f"{len(offenders)} quoted line(s) reduce to an EMPTY payload and are not interior "
        f"separators of a multi-line quote. An empty payload matches every source "
        f"vacuously, so this is a destroyed quote that a substring check reports as green."
    )


def test_the_declared_blank_count_is_exactly_what_section_0_publishes(oracle):
    """§0 now publishes 304 / 3 / 301. All three regenerate, or this fails.

    ⚠️ **OF-17.** The old figure was **299**, it never regenerated from the stated scope, and
    it embedded **two undeclared narrowings** — the 3 blanks, and §6's 2 quoted lines
    (`301 − 2 = 299`). Both are now declared. A published number that does not regenerate is
    what hard rule 10 exists to forbid.
    """
    payloads = [p for _, p in _quoted(oracle)]
    blanks = [p for p in payloads if p == ""]
    text = "\n".join(oracle)

    assert len(payloads) == 304, f"{len(payloads)} lines begin with '>' in scope, not 304"
    assert len(blanks) == 3, f"{len(blanks)} quote-internal blanks, not 3"
    assert len(payloads) - len(blanks) == 301

    stated = re.search(
        r"\*\*Result at the time of writing: (\d+) of (\d+) quoted lines matched", text
    )
    assert stated and int(stated.group(2)) == 301
    assert "**304** lines begin with `>` in that scope" in text
    assert "**3** are quote-internal blanks" in text


# ── (i) source-binding — the structural half, offline ─────────────────────────────────


def test_every_quoted_line_belongs_to_a_row_or_to_a_declared_exception(oracle):
    """⚠️ **F-R6(i), the half that CAN be checked without the source bodies.**

    A quote that belongs to no row cites nothing, so nothing can ever verify it. The two
    legitimate exceptions are **named here rather than skipped**: §6's `RECORDED` table (its
    rows are one-liners, not `### RS-nn` bodies) and §8's quote of `CONTEXT.md` (which §0's
    own sentence carves out explicitly). ⚠️ §6's two lines are exactly the ones the old
    denominator silently dropped to reach 299 — see OF-17.
    """
    section_6 = next(i for i, ln in enumerate(oracle) if ln.startswith("## 6. "))
    section_7 = next(i for i, ln in enumerate(oracle) if ln.startswith("## 7. "))
    section_8 = next(i for i, ln in enumerate(oracle) if ln.startswith("## 8. "))
    section_9 = next(i for i, ln in enumerate(oracle) if ln.startswith("## 9. "))

    orphans = []
    in_s6 = in_s8 = 0
    for index, payload in _quoted(oracle):
        if not payload:
            continue
        if section_6 <= index < section_7:
            in_s6 += 1
            continue
        if section_8 <= index < section_9:
            in_s8 += 1
            continue
        if _row_at(oracle, index) is None:
            orphans.append(f"line {index + 1}: {payload[:70]}")

    assert not orphans, (
        "quoted line(s) belong to no RS-nn row and to no declared exception, so no source "
        "can ever be bound to them:\n  " + "\n  ".join(orphans)
    )
    assert in_s6 == 2, f"§6 contributes {in_s6} quoted lines, not the 2 OF-17 accounts for"
    assert in_s8 == 4, f"§8 contributes {in_s8} quoted lines, not 4"


def test_every_row_that_carries_a_quote_declares_a_source_that_exists(oracle):
    """The other half of source-binding: a row's ``Source`` must name a real §1 source.

    §1's table lists **S1–S12**. A row citing ``S13`` — or citing nothing at all while
    carrying a quote — cannot be verified by anyone, ever, and the global check `F-R6(i)`
    describes would not notice.
    """
    text = "\n".join(oracle)
    known = set(re.findall(r"^\| \*\*S(\d{1,2})\*\* \|", text, re.M))
    assert len(known) == 12, f"§1's source table parsed to {len(known)} sources, not 12"

    rows_with_quotes = {
        _row_at(oracle, i) for i, p in _quoted(oracle) if p and _row_at(oracle, i)
    }
    assert len(rows_with_quotes) >= 45, (
        f"only {len(rows_with_quotes)} rows carry quotes, which is implausibly few — this "
        f"parser has probably stopped seeing them (INC-14's class)."
    )

    bad = []
    for row in sorted(rows_with_quotes):
        declared = _declared_sources(oracle, row)
        if not declared:
            bad.append(f"{row}: carries a quote and declares NO source")
        elif not declared <= known:
            bad.append(f"{row}: cites {sorted(declared - known)}, which §1 does not list")
    assert not bad, "\n  ".join([""] + bad)


# ── the HTTP cross-check — ⚠️ this kills M-03 offline ─────────────────────────────────


def test_every_rows_declared_http_code_agrees_with_the_code_line_inside_its_own_quote(
    oracle,
):
    """⚠️ **THIS KILLS MUTANT M-03, WHICH `REVIEW_C1_1.md` RECORDS AS CAUGHT BY NOTHING.**

    M-03 rewrites RS-09's documented ``409`` to ``400`` **inside the quote**. The review
    shows why the specified check cannot see it: the payload becomes ``* code: 400``, which
    occurs **8 times in `normal-refunds-idempotent.md` alone**, so a global substring match
    succeeds. And a *source-bound* match would also succeed, because that string really is on
    that page.

    **But the row's own `HTTP` field still says 409.** The corruption makes the row
    self-contradictory, and self-contradiction needs no external source to detect. ⚠️ **Why
    it matters beyond the mutant:** the review's own words — *"the world would then fire the
    wrong code in the self-test that is supposed to prove it matches Razorpay."*

    Rows whose ``HTTP`` field is ``n/a`` are excluded and **counted**, never silently skipped.
    **The partition, measured rather than guessed: 53 rows carry an `HTTP` field; 37 are
    checked; 16 are excluded — 12 whose code is `n/a` (a documented value, bound or semantic
    rather than an error) and 4 whose quote carries no `code:` line. 37 + 12 + 4 = 53.**
    """
    checked = skipped = not_applicable = no_code_line = 0
    mismatches = []
    for i, line in enumerate(oracle):
        m = re.match(r"^\*\*HTTP\*\* (.+?) ·", line)
        if not m:
            continue
        declared = re.findall(r"\b([1-5]\d{2})\b", m.group(1))
        if not declared:
            not_applicable += 1
            skipped += 1
            continue
        row = _row_at(oracle, i)
        start = next(j for j in range(i, -1, -1) if oracle[j].startswith(f"### {row} "))
        codes = {
            c
            for ln in oracle[start:i]
            if ln.startswith(">")
            for c in re.findall(r"code:\s*`?([1-5]\d{2})`?", ln)
        }
        if not codes:
            no_code_line += 1
            skipped += 1
            continue
        checked += 1
        if not codes <= set(declared):
            mismatches.append(
                f"{row}: HTTP field declares {declared}, its own quote says code: "
                f"{sorted(codes)}"
            )

    assert checked == 37, (
        f"{checked} row(s) had both an HTTP code and a code: line to compare, not the 37 "
        f"measured on 2026-08-31. A check that silently compares fewer rows than it did "
        f"yesterday reports PASS over nothing (INC-14)."
    )
    assert not mismatches, (
        "a row's declared HTTP code contradicts the code: line inside its own verbatim "
        "quote. One of the two was corrupted:\n  " + "\n  ".join(mismatches)
    )
    # ⚠️ HARD RULE 11: the excluded set is a PRINTED NUMBER with its categories, never a
    # silence, and the partition is asserted to SUM — which is persona 1's own check applied
    # to this check's own denominator.
    assert (not_applicable, no_code_line, skipped) == (12, 4, 16), (
        f"the HTTP cross-check's excluded set changed: {not_applicable} n/a code(s) + "
        f"{no_code_line} row(s) whose quote carries no 'code:' line = {skipped}, against the "
        f"12 + 4 = 16 measured on 2026-08-31."
    )
    assert checked + skipped == 53, "the partition does not sum to the 53 HTTP fields"


# ── (i) the verbatim half, on the ONE source this repository holds ────────────────────


def test_section_8s_quote_of_context_md_is_verbatim_and_source_bound(oracle, repo_root):
    """⚠️ **THE VERBATIM HALF, RUN END TO END — on the only source the repo carries.**

    §0's check carves out exactly one non-Razorpay source: *"or of `CONTEXT.md`, for the one
    quote of this project's own specification in §8."* `CONTEXT.md` **is** in this
    repository, so this is the one place the full check — reduce the payload, then require it
    as a contiguous substring **of the cited source and no other** — can actually run.

    **It is therefore the proof that the matcher works**, and not merely that it was
    described. If the reduction rule is wrong, or the wrapping-backtick strip is wrong, or
    the four labels are wrong, this test is where it shows.

    ⚠️ It also matters on its own: §8's quote is `CONTEXT.md` §6's inversion — the sentence
    the README leads with — and a drift between the two would publish two versions of this
    project's headline finding.
    """
    section_8 = next(i for i, ln in enumerate(oracle) if ln.startswith("## 8. "))
    section_9 = next(i for i, ln in enumerate(oracle) if ln.startswith("## 9. "))
    payloads = [
        p for i, p in _quoted(oracle) if section_8 <= i < section_9 and p
    ]
    assert len(payloads) == 4, f"§8 carries {len(payloads)} quoted lines, not 4"

    # The cited source, and ONLY the cited source.
    context = re.sub(r"\s+", " ", (repo_root / "CONTEXT.md").read_text(encoding="utf-8"))
    unmatched = [p for p in payloads if re.sub(r"\s+", " ", p) not in context]
    assert not unmatched, (
        "§8 quotes CONTEXT.md and the text is NOT in CONTEXT.md:\n  "
        + "\n  ".join(unmatched)
        + "\n\nThis is the one source this repository holds, so this is the one quote whose "
        "bytes can be checked offline. A drift here means §8 and CONTEXT.md §6 publish two "
        "different versions of this project's headline finding."
    )


def test_the_offline_gap_is_printed_as_a_number_and_not_as_a_silence(oracle):
    """⚠️ **HARD RULE 11 APPLIED TO THIS CHECK'S OWN DENOMINATOR.**

    301 non-empty quoted lines; **4** have their bytes verified here (§8's, against
    `CONTEXT.md`); **297 do not**, because the ten Razorpay pages and two pinned source trees
    are not vendored. `REVIEW_C1_1.md` F-R5 leaves that choice to the architect — vendor
    ~112 KB under ``tests/fixtures/``, or accept the gap in writing — and **`OF-15` stays
    OPEN on that half.**

    This test exists so the gap cannot be forgotten: it fails if the numbers move without
    somebody deciding they should. **A check that quietly covers less than it claims is the
    exact defect F-R6 found in the check this file implements.**
    """
    payloads = [p for _, p in _quoted(oracle) if p]
    verified_offline = 4
    assert len(payloads) == 301
    assert len(payloads) - verified_offline == 297, (
        "the count of quoted lines whose bytes CANNOT be checked offline has moved. If the "
        "ten source bodies were vendored, this number should drop and this assertion should "
        "be updated deliberately — never silently."
    )
