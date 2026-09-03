"""THE REVIEW TRAIL IS ITSELF A PUBLISHED RESULT.

`PROCESS.md` §12.1's C18 row consumes every other chunk's output, and the honest thing to
publish beside those numbers is **how each one was checked**. For every chunk: whether it was
adversarially reviewed, **how many times**, whether it PASSED, and **what residue is open**.

⚠️ **THE UNREVIEWED CHUNKS ARE NAMED IN THE TABLE, PLAINLY, NOT FOOTNOTED.** C8, C9, C10, C11
and C14 may ship unreviewed and the table says so in its own status column. C6 was reviewed
**six** times and C7 **twice**, and both ship **WITH RESIDUE and no tag** (`QUESTIONS.md`
**Q-089**, ARCH DISPOSITION 1).

⚠️ **A WALL OF PASSES WOULD BE WEAKER EVIDENCE THAN THIS TRAIL.** `ai-playbook` B.9: *"A
release gate that has never gone red is only decorative."* The FAIL verdicts in
`docs/reviews/` are the evidence that the review gate works, and they are **counted from the
files** rather than asserted — :func:`count_verdicts` reads each review's own verdict line,
so the number in `RESULTS.md` is whatever the repository actually contains on the day it is
assembled and cannot be a remembered figure.

⚠️ **THE TAG IS THE AUTHORITY ON A PASS, NOT THE STATUS COLUMN.** `REVIEW_8_1.md` §1 makes
the point in terms: the answer to *"which chunks are tagged"* is read from
``git for-each-ref refs/tags``, **not from the review-history column**. So :class:`ChunkTrail`
carries both and prints them side by side; where they disagree, the disagreement is the
finding.

**PURE.** Parsed text and a tag set in, rows out. The caller ran git and read the files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping, Sequence

#: `STATUS.md`'s chunk table heading. Located by its own first column.
_CHUNK_TABLE_HEADER = "| # | Date | Chunk | Review | Status | Review history"

#: ⚠️ **THE VERDICT SHAPES WERE MEASURED ACROSS `docs/reviews/`, NOT ASSUMED, AND THERE ARE
#: TWO.** The first pass of this parser knew only the inline form and reported **three**
#: reviews as ``UNRECORDED`` — ``REVIEW_7_1``, ``REVIEW_7_2`` and ``REVIEW_8_1``, every one of
#: them a **FAIL**. Those three record the verdict as a *heading* (``# ⚠️ FAIL.`` at the foot
#: of the file, and ``> # ⚠️ **FAIL** — FOUR BLOCKERS …`` inside a blockquote), because their
#: own opening line says *"VERDICT: recorded in §15, at the foot of this file. Nothing above
#: it is a verdict."* A parser that saw only the inline form would have published *"FAIL 10"*
#: where the repository holds **14**, and would have printed C7 and C8 with no verdict at all.
#:
#:   * **inline** — ``VERDICT: **FAIL``, ``VERDICT — **PASS``, ``Verdict: FAIL``. Same line
#:     only, so ``VERDICT: recorded in §15`` correctly matches nothing. ⚠️ **Nothing but
#:     punctuation and whitespace may sit between the word and the verdict**, measured: a
#:     32-character window matched ``verdict: **P-48 predicted PASS.**`` in ``REVIEW_C6_6``
#:     — a sentence about a *prediction* — and reported that FAIL as ``AMBIGUOUS``.
#:   * **heading** — a heading line, optionally quoted, whose PASS/FAIL is the **first word**
#:     of the heading, reachable across nothing but punctuation, whitespace and the warning
#:     glyph.
#:
#: ⚠️ **THE HEADING PATTERN ALLOWS NO WORD CHARACTER BEFORE THE VERDICT, AND THAT BOUND WAS
#: MEASURED RATHER THAN CHOSEN.** A looser *"within the first twelve characters"* version
#: matched ``## 8. WHAT A PASS REQUIRED, ITEM BY ITEM`` in all six `REVIEW_C6_*` files —
#: a prose heading **about** the bar, in six reviews whose verdict is **FAIL** — and reported
#: every one of them ``AMBIGUOUS``. Restricting the run-up to ``[^\w\n]`` leaves ``# ⚠️
#: FAIL.`` and ``> # ⚠️ **FAIL** —`` matching and drops the prose heading, because ``8. WHAT
#: A `` contains word characters.
#: ⚠️ **THE PATTERNS ARE PLAIN STRINGS AND ARE NOT PRE-COMPILED, DELIBERATELY.**
#: ``check_roles.MOAT_REFUSED_DYNAMIC`` refuses the code-compilation builtin outright, over
#: **raw source text**, because `INCIDENTS.md` **INC-51** measured the whole vocabulary of
#: run-time reach walking straight past D1, D2 and D3 — *"a call expression is not an import
#: node"*. **That scan cannot tell a regex pre-compilation from a code one, and cannot tell
#: a comment from a call either — which is exactly the property that makes it worth
#: having**; the refusal list's own rationale says *"the cost of a false positive is a
#: rewording, and the cost of a false negative is the submission's central argument."*
#: **This paragraph is that rewording, twice over.** ``re.search`` and ``re.finditer`` take
#: the flags as arguments and cache the prepared form internally, so nothing is lost but a
#: line.
_VERDICT_INLINE = r"verdict[^\w\n]{0,8}(PASS|FAIL)\b"
_VERDICT_HEADING = r"^>?[^\S\n]*#{1,3}[^\w\n]{0,10}(PASS|FAIL)\b"
_VERDICT_FLAGS = re.IGNORECASE
_HEADING_FLAGS = re.IGNORECASE | re.MULTILINE

#: A review artefact's own name. ⚠️ **The attempt suffix is OPTIONAL**: the first review this
#: project ever wrote is ``REVIEW_C0.md`` with no ``_1``, and a parser requiring the suffix
#: silently dropped it — losing a **FAIL** and reporting C0 as reviewed once, passing.
_REVIEW_FILE = r"^REVIEW_(C?)(\d+)(?:_(\d+))?\.md$"

#: `docs/reviews/ARCHITECT_CHECK_<N>.md`. Not reviews, and counted separately rather than
#: folded in: an architect check verifies a chunk on the machine and is a different artefact
#: from an adversarial review by a fresh session.
_ARCHITECT_CHECK_FILE = r"^ARCHITECT_CHECK_(\d+)\.md$"


@dataclass(frozen=True, slots=True)
class ReviewArtefact:
    """One file in `docs/reviews/`, its chunk, its attempt, and the verdict it records."""

    filename: str
    chunk: str
    attempt: int
    verdict: str

    @property
    def failed(self) -> bool:
        return self.verdict == "FAIL"

    @property
    def passed(self) -> bool:
        return self.verdict == "PASS"


def parse_verdict(review_text: str) -> str:
    """The verdict a review file records: ``PASS``, ``FAIL``, ``AMBIGUOUS`` or ``UNRECORDED``.

    ⚠️ **``UNRECORDED`` IS A DISTINCT ANSWER FROM ``PASS``, AND SO IS ``AMBIGUOUS``.** A review
    whose verdict this parser cannot find is not a pass, and defaulting it to one would be
    exactly the shape of reporting this project exists to criticise. A file whose two verdict
    shapes **disagree** is reported as ``AMBIGUOUS`` rather than resolved by preferring one —
    the disagreement is the finding, and a parser that silently picked would hide it.

    Both shapes are tried because both exist in `docs/reviews/`; see :data:`_VERDICT_INLINE`
    for what the single-shape version of this function got wrong, measured.
    """
    found = {
        match.group(1).upper()
        for match in re.finditer(_VERDICT_INLINE, review_text, _VERDICT_FLAGS)
    }
    found.update(
        match.group(1).upper()
        for match in re.finditer(_VERDICT_HEADING, review_text, _HEADING_FLAGS)
    )
    if not found:
        return "UNRECORDED"
    if len(found) > 1:
        return "AMBIGUOUS"
    return found.pop()


def review_artefacts(files: Mapping[str, str]) -> tuple[ReviewArtefact, ...]:
    """Every ``REVIEW_<chunk>[_<attempt>].md`` in ``files``, verdict read from its own text."""
    found: list[ReviewArtefact] = []
    for filename in sorted(files):
        match = re.match(_REVIEW_FILE, filename)
        if not match:
            continue
        found.append(
            ReviewArtefact(
                filename=filename,
                chunk=f"C{match.group(2)}",
                attempt=int(match.group(3)) if match.group(3) else 1,
                verdict=parse_verdict(files[filename]),
            )
        )
    return tuple(found)


def architect_checks(files: Mapping[str, str]) -> tuple[str, ...]:
    """`docs/reviews/ARCHITECT_CHECK_<N>.md`, counted **separately** from adversarial reviews.

    An architect check verifies a chunk **on the machine**; an adversarial review is a fresh
    session re-deriving it. Folding the two together would inflate the review count with a
    different kind of evidence, which is the direction that flatters.
    """
    return tuple(sorted(name for name in files if re.match(_ARCHITECT_CHECK_FILE, name)))


def count_verdicts(artefacts: Sequence[ReviewArtefact]) -> dict[str, int]:
    """FAIL / PASS / AMBIGUOUS / UNRECORDED, **counted from the files**, never asserted."""
    counts = {"FAIL": 0, "PASS": 0, "AMBIGUOUS": 0, "UNRECORDED": 0}
    for artefact in artefacts:
        counts[artefact.verdict] = counts.get(artefact.verdict, 0) + 1
    return counts


@dataclass(frozen=True, slots=True)
class ChunkTrail:
    """One chunk's row of the published review trail."""

    chunk: str
    title: str
    review_type: str
    status: str
    reviews: int
    fails: int
    passes: int
    unrecorded: int
    tagged: bool
    tag: str

    @property
    def adversarially_reviewed(self) -> bool:
        return self.reviews > 0

    @property
    def ships_unreviewed(self) -> bool:
        return self.reviews == 0

    @property
    def ships_with_residue(self) -> bool:
        """Reviewed, never passed, no tag — C6 and C7's disposition (`Q-089`)."""
        return self.reviews > 0 and not self.tagged

    def verdict_summary(self) -> str:
        if self.ships_unreviewed:
            return "**UNREVIEWED - NO TAG**"
        if self.tagged:
            return f"**PASSED** (tagged `{self.tag}`)"
        return "**SHIPS WITH RESIDUE - reviewed, never passed, NO TAG**"


def _cell_text(cell: str) -> str:
    """A markdown cell reduced to its plain words, for a table that must stay readable."""
    plain = re.sub(r"\*\*(.+?)\*\*", r"\1", cell)
    plain = re.sub(r"`([^`]*)`", r"\1", plain)
    return re.sub(r"\s+", " ", plain).strip()


def parse_status_chunks(status_md: str) -> tuple[tuple[str, str, str, str], ...]:
    """`STATUS.md`'s chunk table, as ``(chunk, title, review type, status)`` per row.

    The review-history column is **not** parsed into the published table. It is append-only
    prose that no parser should reduce, and the trail's numbers come from the review files
    and the tags — the two things a reader can re-derive without trusting this parser.
    """
    lines = status_md.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith(_CHUNK_TABLE_HEADER)]
    if len(starts) != 1:
        raise RuntimeError(
            f"STATUS.md's chunk table header matched {len(starts)} times, not once. The "
            f"review trail is a PUBLISHED RESULT and a RESULTS.md that silently printed an "
            f"empty one would be the omission it exists to prevent"
        )
    rows: list[tuple[str, str, str, str]] = []
    for line in lines[starts[0] + 1 :]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            if rows:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 5 or all(set(cell) <= set("-: ") for cell in cells):
            continue
        chunk = _cell_text(cells[0])
        if not chunk:
            continue
        rows.append((chunk, _cell_text(cells[2]), _cell_text(cells[3]), _cell_text(cells[4])))
    if not rows:
        raise RuntimeError("STATUS.md's chunk table yielded no rows")
    return tuple(rows)


@dataclass(frozen=True, slots=True)
class ReviewTrail:
    """Every chunk's row, plus the run-wide verdict counts. ⚠️ **Counted, never asserted.**"""

    rows: tuple[ChunkTrail, ...]
    verdict_counts: Mapping[str, int]
    open_findings_total: int
    open_findings_by_severity: Mapping[str, int]

    @property
    def unreviewed(self) -> tuple[str, ...]:
        return tuple(r.chunk for r in self.rows if r.ships_unreviewed)

    @property
    def with_residue(self) -> tuple[str, ...]:
        return tuple(r.chunk for r in self.rows if r.ships_with_residue)

    @property
    def tagged(self) -> tuple[str, ...]:
        return tuple(r.chunk for r in self.rows if r.tagged)

    def lines(self) -> tuple[str, ...]:
        rows: list[str] = [
            "THE REVIEW TRAIL - itself a published result. Every chunk: reviewed? how many "
            "times? passed? what residue?",
            "",
            "| chunk | what it is | review type | times adversarially reviewed | FAIL | PASS "
            "| unrecorded | verdict |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for row in self.rows:
            rows.append(
                f"| **{row.chunk}** | {row.title} | {row.review_type} | {row.reviews} | "
                f"{row.fails} | {row.passes} | {row.unrecorded} | {row.verdict_summary()} |"
            )
        rows.append("")
        rows.append(
            f"  REVIEW VERDICTS IN docs/reviews/, COUNTED FROM THE FILES: "
            f"FAIL {self.verdict_counts.get('FAIL', 0)} * "
            f"PASS {self.verdict_counts.get('PASS', 0)} * "
            f"UNRECORDED {self.verdict_counts.get('UNRECORDED', 0)}"
        )
        rows.append(
            f"  CHUNKS SHIPPING UNREVIEWED, NO TAG : "
            f"{', '.join(self.unreviewed) if self.unreviewed else 'none'}"
        )
        rows.append(
            f"  CHUNKS SHIPPING WITH RESIDUE, NO TAG : "
            f"{', '.join(self.with_residue) if self.with_residue else 'none'}"
        )
        rows.append(
            f"  CHUNKS TAGGED cN-pass              : "
            f"{', '.join(self.tagged) if self.tagged else 'none'}"
        )
        rows.append(
            f"  OPEN FINDINGS (docs/reviews/OPEN_FINDINGS.md): {self.open_findings_total}"
            + (
                "  ["
                + ", ".join(
                    f"{k} {v}" for k, v in sorted(self.open_findings_by_severity.items())
                )
                + "]"
                if self.open_findings_by_severity
                else ""
            )
        )
        rows.append("")
        rows.append(
            "  ! THE FAILS ARE THE EVIDENCE, NOT THE EMBARRASSMENT. ai-playbook B.9: 'A "
            "release gate that has never gone red is only decorative.' A wall of passes would "
            "be weaker evidence than this trail, and every FAIL above is a file in "
            "docs/reviews/ a reader can open."
        )
        rows.append(
            "  ! THE TAG IS THE AUTHORITY ON A PASS, NOT A STATUS COLUMN - read from "
            "`git for-each-ref refs/tags`, as REVIEW_8_1 S1 requires."
        )
        return tuple(rows)


def build_trail(
    status_md: str,
    review_files: Mapping[str, str],
    tags: Sequence[str],
    *,
    open_findings_total: int,
    open_findings_by_severity: Mapping[str, int],
) -> ReviewTrail:
    """Assemble the trail from `STATUS.md`, the review files' own verdicts, and the tag list."""
    artefacts = review_artefacts(review_files)
    tag_set = set(tags)
    rows: list[ChunkTrail] = []
    for chunk, title, review_type, status in parse_status_chunks(status_md):
        mine = [a for a in artefacts if a.chunk == chunk]
        tag = f"{chunk.lower()}-pass"
        rows.append(
            ChunkTrail(
                chunk=chunk,
                title=title,
                review_type=review_type,
                status=status,
                reviews=len(mine),
                fails=sum(1 for a in mine if a.failed),
                passes=sum(1 for a in mine if a.passed),
                unrecorded=sum(1 for a in mine if a.verdict == "UNRECORDED"),
                tagged=tag in tag_set,
                tag=tag,
            )
        )
    return ReviewTrail(
        rows=tuple(rows),
        verdict_counts=count_verdicts(artefacts),
        open_findings_total=open_findings_total,
        open_findings_by_severity=dict(open_findings_by_severity),
    )
