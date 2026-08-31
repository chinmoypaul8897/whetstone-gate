"""KEPT PROBES added by the C1 ADVERSARIAL REVIEW (SESSION-TOKEN ``a0cc0212``).

**These are probes, not fixes.** A review session fixes nothing (`CLAUDE.md` §1); it may add
kept tests. `PROCESS.md` §10 template 2 asks a `full` review for mutants; ⚠️ **for an ORACLE
DOCUMENT the architect ruled (2026-08-31) that the mutation analogue is CORRUPT A ROW AND SEE
WHETHER ANYTHING CATCHES IT.** Twelve mutants were applied to throwaway copies of
``RAZORPAY_SEMANTICS.md``. **Before this file existed, the answer for eleven of the twelve was
NOTHING** — `RAZORPAY_SEMANTICS.md` §0 publishes a *"re-runnable check"* of its own
blockquote-is-verbatim rule and reports **299 of 299**, but **no implementation of that check
is committed anywhere in this repository**, so `make test` could not detect a paraphrase, a
changed digit, a wrong HTTP code or a row moved between `MUST-FIRE` and `RECORDED`.

That gap is the finding. These probes are its executable half. See `docs/reviews/REVIEW_C1_1.md`.

⚠️ **THE PROBES BELOW ARE ALL OFFLINE AND DETERMINISTIC.** The verbatim-substring half of §0's
check needs the ten fetched sources, which this repository does not vendor; re-fetching inside
``make test`` would make the suite depend on razorpay.com being up, which is worse than not
testing. So these probes assert the parts that ARE checkable offline — the census, the
partition, and the internal reference graph — and the review document records, per mutant,
exactly which mutants that leaves uncovered.

⚠️ **ONE PROBE IS RED ON PURPOSE.** ``test_section_0_states_its_own_quoted_line_count_correctly``
fails against the reviewed artefact: §0 publishes **299 of 299** and the file as committed
carries **301** non-empty quoted lines. **That is C1 finding F-R2 and it belongs to C1's FIX
session — it is NOT a defect in C0 or in any other chunk**, and a concurrent reviewer seeing
`make test` red should read this docstring before attributing it.

⚠️ **NO PROBE HERE ASSERTS A RAZORPAY FIGURE.** A probe that hardcoded ₹5 Cr or the ten-character
idempotency minimum would be this project's own hard rule 9 violation and would make the oracle
circular — the artefact would be checked against a copy of itself. Every probe is a *structural*
property of the document.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
ORACLE = REPO / "RAZORPAY_SEMANTICS.md"

#: The three ``World`` labels `RAZORPAY_SEMANTICS.md` §0 defines. Any other value is a defect.
LABELS = ("MUST-FIRE", "MUST-HOLD", "RECORDED")

#: §0 adds these four field labels to the concurrency rows (RS-22, RS-23, RS-24) and its own
#: check declares them stripped before matching. They are this file's, not Razorpay's.
_ADDED_FIELD_LABEL = re.compile(r"^\s*\*\*(error|code|description|solution):\*\*\s*")


def _lines():
    return ORACLE.read_text(encoding="utf-8").split("\n")


def _from_section_1(lines):
    """§0's check is scoped *"Counted over §1 onward"*. Reproduce that scope exactly."""
    start = next(i for i, ln in enumerate(lines) if ln.startswith("## 1. Sources"))
    return lines[start:]


def _quoted_payloads(lines):
    """Every ``>`` line from §1 onward, reduced exactly as §0's check specifies.

    Strip the leading ``>``, the four added field labels, and one layer of wrapping backticks.
    Blank continuation lines (a bare ``>`` inside a multi-line quote) reduce to ``""`` and are
    returned so a caller can count them separately rather than silently dropping them.
    """
    out = []
    for ln in _from_section_1(lines):
        if not ln.startswith(">"):
            continue
        t = _ADDED_FIELD_LABEL.sub("", ln[1:]).strip()
        if len(t) >= 2 and t.startswith("`") and t.endswith("`"):
            t = t[1:-1]
        out.append(t)
    return out


def _row_labels():
    """Map every ``### RS-nn`` row to the ``World`` labels its body carries."""
    lines = _lines()
    rows, cur, buf = {}, None, []
    for ln in lines:
        m = re.match(r"^### (RS-\d+)", ln)
        if m:
            if cur:
                rows[cur] = buf
            cur, buf = m.group(1), []
            continue
        if ln.startswith("## ") and cur:
            rows[cur], cur, buf = buf, None, []
            continue
        if cur is not None:
            buf.append(ln)
    if cur:
        rows[cur] = buf
    out = {}
    for name, body in rows.items():
        found = re.findall(r"\*\*World\*\*\s*`?([A-Z][A-Z-]+)`?", " ".join(body))
        out[name] = [f for f in found if f in LABELS]
    return out


# ── the census ────────────────────────────────────────────────────────────────────────────


def test_every_quoted_line_survives_section_0s_stripping_as_non_empty_text():
    """MUTANT M-05 (a paraphrase replacing a quote) and the empty-string attack on §0's check.

    ⚠️ The review prompt asked whether §0's check *"can be made to pass over an empty string"*.
    It can: a ``>`` line that reduces to ``""`` is a substring of every source, so a naive
    implementation counts it as MATCHED. This probe pins the number of such lines, so a row
    emptied out — the cheapest way to destroy a quote while keeping the check green — moves it.
    """
    payloads = _quoted_payloads(_lines())
    empties = [p for p in payloads if p == ""]
    assert len(payloads) == 304, (
        "the number of '>' lines from §1 onward changed; a quote was added, removed or emptied"
    )
    assert len(empties) == 3, (
        "the number of quote-internal blank lines changed. An empty payload is a substring of "
        "every source, so §0's check passes over it vacuously — this count is the guard."
    )


def test_section_0_states_its_own_quoted_line_count_correctly():
    """⚠️ RED ON PURPOSE — C1 review finding **F-R2**. Not a C0 defect. See this module's docstring.

    §0 publishes *"299 of 299 quoted lines matched"*. Recomputed from the file as committed, at
    its only commit ``55f1f2c``, the figure is **301**. The verdict (*Unmatched: 0*) reproduces
    exactly — this review re-ran the substring half against all ten sources and every one of the
    301 matched — but the **denominator does not regenerate**, and a published number that does
    not regenerate is what `CLAUDE.md` hard rule 10 exists to forbid.
    """
    stated = re.search(r"\*\*Result at the time of writing: (\d+) of (\d+) quoted lines matched",
                       ORACLE.read_text(encoding="utf-8"))
    assert stated, "§0's published result line is gone — the check's own claim must stay stated"
    payloads = _quoted_payloads(_lines())
    actual = len([p for p in payloads if p != ""])
    assert int(stated.group(2)) == actual, (
        f"§0 publishes a denominator of {stated.group(2)} non-empty quoted lines; the file as "
        f"committed carries {actual}. C1 finding F-R2 — owned by C1's FIX session."
    )


# ── the partition ─────────────────────────────────────────────────────────────────────────


def test_every_written_out_row_carries_exactly_one_world_label():
    """MUTANT M-07 (a row moved between MUST-FIRE and RECORDED), half one.

    ⚠️ Q-018's ruling makes the `MUST-FIRE` set **C4's done-when**, so a row that carries two
    labels, or none, silently adds or removes a rule from the spend-free self-test.
    """
    labels = _row_labels()
    written_out = {k: v for k, v in labels.items() if k != "RS-70"}
    unlabelled = sorted(k for k, v in written_out.items() if len(v) == 0)
    multiple = sorted(k for k, v in written_out.items() if len(set(v)) > 1)
    assert not unlabelled, f"rows in NO bucket: {unlabelled}"
    assert not multiple, f"rows in MORE THAN ONE bucket: {multiple}"


def test_the_partition_sums_and_matches_what_the_file_publishes():
    """MUTANT M-07, half two — and persona 1's *"does every partition sum to its total?"*

    §10's counts table publishes **40 / 13 / 18 = 71**. Recompute all four from the document
    rather than trusting the table, so that moving a row between buckets fails here.
    """
    labels = _row_labels()
    written_out = {k: v for k, v in labels.items() if k != "RS-70"}
    must_fire = sum(1 for v in written_out.values() if v and v[0] == "MUST-FIRE")
    must_hold = sum(1 for v in written_out.values() if v and v[0] == "MUST-HOLD")

    text = ORACLE.read_text(encoding="utf-8")
    recorded_start = text.index("## 6. Documented, but NOT reachable")
    recorded_end = text.index("### RS-70 (note)")
    recorded = re.findall(r"^\| \*\*(RS-\d+)\*\* \|", text[recorded_start:recorded_end], re.M)

    assert must_fire == 40, f"MUST-FIRE recomputes to {must_fire}, not the published 40"
    assert must_hold == 13, f"MUST-HOLD recomputes to {must_hold}, not the published 13"
    assert len(recorded) == 18, f"RECORDED recomputes to {len(recorded)}, not the published 18"
    assert must_fire + must_hold + len(recorded) == 71, "the partition does not sum to 71"
    assert len(set(recorded)) == len(recorded), "a RECORDED row number is duplicated"


def test_the_row_number_space_is_contiguous_with_no_gaps_and_no_duplicates():
    """§10 publishes *"RS-01 … RS-71, contiguous, no gaps and no duplicates"*. Check it.

    A gap would mean a row was deleted; a duplicate would mean two rules share one address, and
    every cross-reference to that address becomes ambiguous.
    """
    text = ORACLE.read_text(encoding="utf-8")
    headings = re.findall(r"^### (RS-\d+)", text, re.M)
    table_rows = re.findall(r"^\| \*\*(RS-\d+)\*\* \|", text, re.M)
    # RS-70 is BOTH a RECORDED table row and a '(note)' heading — see finding F-R3.
    numbers = sorted({int(n.split("-")[1]) for n in headings + table_rows})
    assert numbers == list(range(1, 72)), (
        f"row numbers are not RS-01..RS-71 contiguous: got {numbers}"
    )


# ── the internal reference graph ──────────────────────────────────────────────────────────


def test_every_cross_reference_points_at_a_row_that_exists():
    """MUTANT M-06 (a wrong ``file:line``), applied to the document's own addressing scheme.

    Nothing in this repository checked that an ``RS-nn`` mentioned in a row's prose resolves to
    a real row — so a pointer could rot silently. This probe is green: every referenced number
    is in RS-01..RS-71. ⚠️ It deliberately does **not** assert that a pointer aims at the
    *right* row; finding **F-R1** records one that does not (RS-12's *"See RS-31"*, which means
    RS-27), and no mechanical check can catch that. That is itself the point of F-R1.
    """
    text = ORACLE.read_text(encoding="utf-8")
    referenced = {int(n) for n in re.findall(r"\bRS-(\d{2})\b", text)}
    dangling = sorted(n for n in referenced if not 1 <= n <= 71)
    assert not dangling, f"cross-references to rows that do not exist: {dangling}"


def test_every_source_the_rows_cite_is_declared_in_section_1():
    """MUTANT M-04 (a wrong URL) — the addressing half that IS checkable offline.

    Every row cites its page as ``**Source** S<n>``. §1 declares S1–S12. A row citing S13 would
    be pointing at a page the evidence table never lists, which is how an undeclared fetch — or
    an invented one — enters an oracle.
    """
    text = ORACLE.read_text(encoding="utf-8")
    cited = {int(n) for n in re.findall(r"\*\*Source\*\*\s+S(\d+)", text)}
    assert cited, "no row cites a source at all — the evidence trail is gone"
    undeclared = sorted(n for n in cited if not 1 <= n <= 12)
    assert not undeclared, f"rows cite sources §1 never declares: {['S%d' % n for n in undeclared]}"


def test_every_hash_in_section_1_is_a_well_formed_sha256_or_git_sha1():
    """MUTANT M-01 (a changed digit), applied to the digests rather than to a rupee figure.

    §1 is the evidence table the whole artefact rests on. It carries two kinds of hash: the
    **64-hex SHA-256** of each fetched body, and the **40-hex git SHA-1** pinning
    ``razorpay-mcp-server``. This probe cannot detect a *wrong* digest — only a re-fetch can,
    and this review did that for all ten pages and both source trees, with zero drift — but it
    does detect a **truncated or mangled** one, which is the failure mode a hand-edit produces
    and the one no re-fetch would flag as anything but a mismatch of unknown cause.
    """
    text = ORACLE.read_text(encoding="utf-8")
    start = text.index("## 1. Sources")
    end = text.index("## 2. The A1–A6 rows")
    hashes = re.findall(r"`([0-9a-f]{20,})`", text[start:end])
    sha256 = [h for h in hashes if len(h) == 64]
    sha1 = [h for h in hashes if len(h) == 40]
    malformed = [h for h in hashes if len(h) not in (40, 64)]
    assert not malformed, f"neither a SHA-256 nor a git SHA-1 in §1: {malformed}"
    assert len(sha256) == 10, (
        f"§1 declares 10 quoted pages, of which S10 is HTML and carries no digest, giving 9 "
        f"page digests — plus refunds.go's in S11's row, so 10. Found {len(sha256)}"
    )
    assert len(sha1) == 1, f"expected the 1 pinned git SHA-1 in §1, found {len(sha1)}"
