"""THE DEGRADATION RECORD — PUBLISHED, NOT OMITTED, AND **PARSED RATHER THAN ASSUMED**.

`PROCESS.md` §14's rule, which `PROTOCOL.md` §5 then applies to the pre-registration itself:

    *"A cut item is never silently lost: it is named in `RESULTS.md` and in the README as
    **not run**, with why."*

⚠️ **THIS MODULE READS `PROTOCOL.md` §5.1's TABLE. IT DOES NOT TRANSCRIBE IT.** `PROTOCOL.md`
is a **frozen** artefact and outranks `CONTEXT.md` (hard rule 4), and a transcription is a
second copy that can drift from the thing it copies — silently, in the one place where
silence is the failure. Parsing also means a **missing** table is a refusal rather than a
default: :func:`parse_rungs` refuses on anything but the six rows §14 declares.

⚠️ **RUNGS 2, 4 AND 6 ARE *NOT* FIRED AND THE TABLE SAYS SO — READ IT, DO NOT ASSUME IT.**
`PROTOCOL.md` §5.1 records that a session's own prompt asserted rungs 4 and 6 had been fired,
that this was **false against measurement**, and that the session **STOPPED rather than
writing it into a frozen artefact** (`QUESTIONS.md` **Q-099**). *"Firing a rung is an act
with a time, a reason and an `INCIDENTS.md` entry written at the moment of the cut — it is not
something a build session performs by transcription."* The same applies to **reporting** one.

⚠️ **AND THE ONE THAT IS EASIEST TO GET WRONG:** ``vendor.agentdojo_sha`` stays at its
sentinel and the loader **keeps raising**. That is **not** a defect and `config/` is **not**
edited to resolve it — it is *"the visible consequence of a published cut"*. A reader who
greps ``agentdojo`` must find the cut, not a mystery. So it is printed here, in the
degradation record, where that reader will land.

**PURE.** Markdown text in, rows out. The caller read the file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

#: §14's ladder has exactly six rungs. A table with any other count is a changed ladder, and
#: a changed ladder is a changed protocol.
RUNG_COUNT = 6

#: The heading `PROTOCOL.md` §5.1 carries. Located by prefix so its measured-at-HEAD suffix
#: may change without breaking the parse.
_RUNG_SECTION = "### 5.1 The rung table"

#: The heading `PROTOCOL.md` §5.2 carries — the words each cut is published in.
_MEANING_SECTION = "### 5.2 What the cuts mean"

#: ⚠️ Printed in the degradation record itself, so the sentinel is found as a **consequence**
#: rather than as an unexplained refusal. `PROTOCOL.md` §5.2's own row.
AGENTDOJO_SENTINEL_NOTE = (
    "vendor.agentdojo_sha stays at its sentinel and the config loader KEEPS RAISING on it. "
    "That is NOT a defect and config/ is NOT edited to resolve it (config/ is a "
    "pre-registration artefact, hard rule 9). It is the VISIBLE CONSEQUENCE OF A PUBLISHED "
    "CUT - rung 3, C16 / AD-CMP NOT RUN. A reader who greps `agentdojo` must find the cut, "
    "not a mystery."
)


class DegradationParseError(RuntimeError):
    """`PROTOCOL.md`'s degradation record could not be read, so it cannot be published.

    A refusal rather than an empty record: a `RESULTS.md` that printed *"no cuts"* because it
    failed to find the table would be the silent loss §14 forbids, produced by the code
    written to prevent it.
    """


@dataclass(frozen=True, slots=True)
class Rung:
    """One rung of §14's ladder, as `PROTOCOL.md` §5.1 records it."""

    number: int
    cut: str
    status: str
    recorded_at: str

    @property
    def fired(self) -> bool:
        """FIRED iff the status cell says so. ⚠️ Read from the cell, never inferred."""
        return "FIRED" in self.status and "NOT FIRED" not in self.status

    def render(self) -> str:
        return (
            f"| **{self.number}** | {self.cut} | "
            f"{'**FIRED**' if self.fired else 'NOT FIRED'} | {self.status} | "
            f"{self.recorded_at} |"
        )


@dataclass(frozen=True, slots=True)
class CutMeaning:
    """One row of `PROTOCOL.md` §5.2 — what a cut means, in the words it is published in."""

    what: str
    words: str


@dataclass(frozen=True, slots=True)
class DegradationRecord:
    """The whole record: six rungs, what each fired cut means, and the sentinel note."""

    rungs: tuple[Rung, ...]
    meanings: tuple[CutMeaning, ...]
    source: str

    @property
    def fired(self) -> tuple[Rung, ...]:
        return tuple(r for r in self.rungs if r.fired)

    @property
    def not_fired(self) -> tuple[Rung, ...]:
        return tuple(r for r in self.rungs if not r.fired)

    def names_c16_as_not_run(self) -> bool:
        """§14's concrete requirement: **C16 / AD-CMP is named NOT RUN, with why.**"""
        haystack = " ".join(m.what + " " + m.words for m in self.meanings).upper()
        return "AD-CMP" in haystack and "NOT RUN" in haystack

    def refuse(self) -> None:
        if len(self.rungs) != RUNG_COUNT:
            raise DegradationParseError(
                f"the degradation ladder has {len(self.rungs)} rungs, not {RUNG_COUNT}. "
                f"PROCESS.md S14 declares six; a different count is a changed ladder, and a "
                f"changed ladder is a changed protocol"
            )
        if not self.names_c16_as_not_run():
            raise DegradationParseError(
                "the degradation record does not name C16 / AD-CMP as NOT RUN. PROCESS.md "
                "S14: 'a cut item is never silently lost: it is named in RESULTS.md and in "
                "the README as not run, with why.' A project that cuts a comparator and does "
                "not say so has done the thing it criticises"
            )

    def lines(self) -> tuple[str, ...]:
        self.refuse()
        rows: list[str] = [
            f"THE DEGRADATION RECORD - what this run ACTUALLY IS. Read from {self.source} "
            f"S5.1, not transcribed.",
            "",
            "| Rung | Cut | Fired? | Status as recorded | Recorded at |",
            "|---|---|---|---|---|",
        ]
        rows.extend(rung.render() for rung in self.rungs)
        rows.append("")
        rows.append(
            f"  FIRED     : {', '.join(str(r.number) for r in self.fired) or 'none'}"
        )
        rows.append(
            f"  NOT FIRED : {', '.join(str(r.number) for r in self.not_fired) or 'none'}"
            f"   (read from the table, NOT assumed - PROTOCOL.md S5.1, Q-099)"
        )
        rows.append("")
        rows.append("WHAT EACH CUT MEANS, IN THE WORDS IT IS PUBLISHED IN (S5.2)")
        rows.append("")
        rows.append("| What | The words |")
        rows.append("|---|---|")
        rows.extend(f"| {m.what} | {m.words} |" for m in self.meanings)
        rows.append("")
        rows.append(f"  !! {AGENTDOJO_SENTINEL_NOTE}")
        rows.append("")
        rows.append(
            "  N IS NOT A RUNG. After `prereg-v1`, changing N amends a frozen artefact, which "
            "S6 forbids outright. If the sweep cannot finish the pre-registered N, the "
            "episodes that did not run are reported as an INCOMPLETE DENOMINATOR - counted, "
            "categorised and printed - and the number is published with its real n. See the "
            "denominator section above."
        )
        return tuple(rows)


def _table_rows(body: str) -> list[list[str]]:
    """Every data row of the first markdown table in ``body``, cell by cell."""
    rows: list[list[str]] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or all(set(cell) <= set("-: ") for cell in cells):
            continue
        rows.append(cells)
    return rows


def _section(text: str, heading: str) -> str:
    starts = [i for i, line in enumerate(text.splitlines()) if line.startswith(heading)]
    if len(starts) != 1:
        raise DegradationParseError(
            f"{heading!r} matched {len(starts)} times in the protocol, not once. The "
            f"degradation record is PROTOCOL.md's own; if this parser cannot find it, "
            f"RESULTS.md would publish no cuts at all, which is PROCESS.md S14's silent loss "
            f"produced by the code written to prevent it"
        )
    lines = text.splitlines()
    start = starts[0]
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith(("## ", "### "))),
        len(lines),
    )
    return "\n".join(lines[start:end])


def parse_rungs(protocol_md: str) -> tuple[Rung, ...]:
    """§5.1's rung table, read. ⚠️ **Refuses on anything but six numbered rungs.**"""
    rows = _table_rows(_section(protocol_md, _RUNG_SECTION))
    rungs: list[Rung] = []
    for cells in rows:
        if len(cells) < 4:
            continue
        match = re.match(r"\*\*(\d+)\*\*", cells[0])
        if not match:
            continue
        rungs.append(
            Rung(
                number=int(match.group(1)),
                cut=cells[1],
                status=cells[2],
                recorded_at=cells[3],
            )
        )
    if len(rungs) != RUNG_COUNT:
        raise DegradationParseError(
            f"PROTOCOL.md S5.1 yielded {len(rungs)} rungs, not {RUNG_COUNT}. PROCESS.md S14 "
            f"declares six and every one of them is published whether it fired or not"
        )
    return tuple(sorted(rungs, key=lambda r: r.number))


def parse_meanings(protocol_md: str) -> tuple[CutMeaning, ...]:
    """§5.2's *"what the cuts mean, concretely, for what is published"* table, read."""
    rows = _table_rows(_section(protocol_md, _MEANING_SECTION))
    meanings = [
        CutMeaning(what=cells[0], words=cells[1])
        for cells in rows
        if len(cells) >= 2 and cells[0].lower() not in {"what", ""}
    ]
    if not meanings:
        raise DegradationParseError(
            "PROTOCOL.md S5.2 yielded no rows. Every cut's published WORDS live there, and "
            "publishing a cut without them is naming it without saying why"
        )
    return tuple(meanings)


def degradation_record(protocol_md: str, *, source: str = "PROTOCOL.md") -> DegradationRecord:
    """The whole record, parsed from `PROTOCOL.md`'s own text and refused if it is not there."""
    record = DegradationRecord(
        rungs=parse_rungs(protocol_md),
        meanings=parse_meanings(protocol_md),
        source=source,
    )
    record.refuse()
    return record


def fired_numbers(rungs: Sequence[Rung]) -> tuple[int, ...]:
    return tuple(r.number for r in rungs if r.fired)
