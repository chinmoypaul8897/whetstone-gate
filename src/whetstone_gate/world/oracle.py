"""`RAZORPAY_SEMANTICS.md`, PARSED. **The labels are read, never transcribed.**

**Why this module exists at all.** `PROCESS.md` §12.1's C4 row, as amended under
`QUESTIONS.md` **Q-018**, reads:

    every `RAZORPAY_SEMANTICS.md` row marked `MUST-FIRE` fires in the mock world; every row
    marked `MUST-HOLD` holds; and every row marked `RECORDED` is listed in the self-test's
    output as documented-but-unreachable WITH ITS REASON, so the excluded set is a printed
    number and not a silence (hard rule 11).

⚠️ **A LIST OF FORTY ROW IDS TYPED INTO A TEST WOULD BE A SECOND COPY OF THE ORACLE.** It
would drift the first time a row's label moved, and it would drift *silently* — the
self-test would still print `40 / 40` while checking a set the file no longer carries.
`CONTEXT.md` §8.6's own history is the argument: **fourteen constants went missing across
three occurrences** precisely because one list was a transcription of another and nothing
compared the two. So this module **parses the file**, and every count the self-test prints
is derived from the bytes of the oracle at the moment it runs.

**And the same reasoning is applied one level further, to the error strings.** No Razorpay
error text is written anywhere in `whetstone_gate.world`. The engine knows only an **id** —
``"RS-27"`` — and the words come from the row that id names. A reviewer can therefore
establish *"this project invented no Razorpay error string"* by reading a diff rather than
by trusting one.

**Purity, hard rule 8.** :func:`parse` is a pure function from text to data.
:func:`load` is the thin outer shell that does the one file read, exactly as
:func:`whetstone_gate.world.spec.load_world_spec` is for `config/`. The engine takes an
:class:`Oracle` as **data** and never reads a file.

**Parsed with `str` methods and no `re`, deliberately.** `tests/test_c2_world.py` pins the
world package's third-party imports to exactly ``__future__``, ``dataclasses``,
``decimal`` and ``hashlib`` — *"a new dependency in the world is a decision, and this makes
it one a reviewer sees"* — and C4 had no argument for widening that set. Line-oriented
`startswith`/`partition` parsing is also more auditable here than a regex: every rule below
is one readable condition.

**The three shapes this file uses, and they are all it uses:**

  * a **full row** — ``### RS-nn — <title>`` followed by a block carrying
    ``**World** `LABEL` `` (§2–§5, rows RS-01…RS-53);
  * a **`RECORDED` row** — one line of §6's table,
    ``| **RS-nn** | <title> | <http> | <source> | <fetched> | <why not reachable> |``
    (rows RS-54…RS-71);
  * ⚠️ **one NOTE that is not a row** — ``### RS-70 (note) — …``. `RAZORPAY_SEMANTICS.md`
    §10 records it as *"the one identifier in this file that names two things (OF-19)"*:
    RS-70 is both a §6 table row **and** a §6 prose note explaining the Smart Settlements
    family. :func:`parse` skips headings marked ``(note)`` and **asserts that it skipped
    exactly one**, so the day a second appears is a parse failure rather than a silently
    duplicated row.

⚠️ **AND ONE HEADING THAT IS NOT A HEADING: §0's FORMAT TEMPLATE.** §0 documents the row
shape inside a fenced code block whose first line is literally ``### RS-nn — <the rule, in
one line>``. It is prose about the format, not a row, and a parser that took it for one
would try to read a label out of a template. It is skipped by requiring the id to be
``RS-`` followed by **digits**, and — like the note — :func:`parse` **asserts it skipped
exactly one**. Both exclusions are counted rather than assumed, because a silent skip is
how a denominator shrinks (hard rule 11).

**Every parse failure is a hard refusal.** A parser that silently reads nothing is the same
class of defect as the check it replaces (`REVIEW_C0.md`'s *"a check that reports PASS over
nothing"*), so this module raises :class:`OracleParseError` on a row with no label, an
unknown label, a duplicate id, or a census that does not partition.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import config as cfg

#: The oracle's filename at the repository root. `CONTEXT.md` §15.0 puts it in the frozen
#: set, so from `prereg-v1` these bytes do not move.
ORACLE_FILENAME = "RAZORPAY_SEMANTICS.md"

#: The three `World` labels, verbatim from §0's table. They are `RAZORPAY_SEMANTICS.md`'s
#: own vocabulary — not `CONTEXT.md` §8.6 constants — in the same way that ``"captured"``
#: and ``"authorized"`` are Razorpay's vocabulary in
#: :mod:`whetstone_gate.world.generator`. §0 defines each:
#:
#:   * ``MUST-FIRE``  — *"The five-tool surface can trigger it in the modelled world. C4
#:     implements it and the spend-free self-test must fire it."*
#:   * ``MUST-HOLD``  — *"Not an error but a documented value, bound, field or semantic the
#:     world must reproduce."*
#:   * ``RECORDED``   — *"Genuinely documented, but not reachable in this world … It is NOT
#:     part of the self-test's denominator."*
MUST_FIRE = "MUST-FIRE"
MUST_HOLD = "MUST-HOLD"
RECORDED = "RECORDED"

#: Ordered longest-first is not needed here — the label is read between two backticks and
#: compared for equality, never matched as a prefix.
LABELS = (MUST_FIRE, MUST_HOLD, RECORDED)

_ROW_HEADING = "### RS-"
_NOTE_MARKER = "(note)"
_WORLD_FIELD = "**World**"
_HTTP_FIELD = "**HTTP**"
_RECORDED_SECTION = "## 6. "
_RECORDED_ROW = "| **RS-"
_BLOCK_ENDS = ("### ", "## ", "# ")
_QUOTE_PREFIX = ">"

#: The four field labels this file adds to the concurrency rows (RS-22, RS-23, RS-24).
#: §0's own re-runnable check names them and strips them; the first quoted line of such a
#: row is the error title with ``**error:**`` in front of it.
_ERROR_FIELD_LABEL = "**error:**"


class OracleParseError(RuntimeError):
    """`RAZORPAY_SEMANTICS.md` did not parse into the shape §0 documents.

    Raised rather than worked around. Every count the spend-free self-test prints is
    derived from this parse, so a parser that quietly read fewer rows would shrink a
    published denominator — `CLAUDE.md` hard rule 11's exact prohibition.
    """


@dataclass(frozen=True)
class Row:
    """One `RAZORPAY_SEMANTICS.md` row, as parsed."""

    rs_id: str
    """``RS-01`` … ``RS-71``."""

    heading: str
    """The row's one-line title, from its heading or from §6's second table cell."""

    label: str
    """One of :data:`LABELS`."""

    reason: str
    """`RECORDED` rows only: §6's *"Why not reachable"* cell. Empty for the others.

    ⚠️ This field is the reason §6's table is parsed at all rather than merely counted.
    Q-018's ruling requires the excluded set to be printed *with its reason*, so that a
    reader sees **what was documented and deliberately not modelled** instead of inferring
    it from an absence.
    """

    quote: str
    """The row's first quoted line, with ``>`` and any ``**error:**`` label removed.

    Empty where a row carries no quote. ⚠️ **RS-20 is empty deliberately and that is the
    row's whole content** — *"NONE, AND DELIBERATELY NONE. No verbatim quote is given
    because there is no Razorpay text to quote. A citation was not manufactured for this
    row."*
    """

    quotes: tuple[str, ...]
    """The **first line of every quote block** in the row, in file order.

    ⚠️ **Several rows document more than one error string for one condition, and the world
    must emit the one that matches the call it refused.** RS-32 carries **four** distinct
    documented strings for *"capture on a non-`authorized` payment"*; RS-53 carries two with
    **different World labels** — its extra-field refusal is `MUST-FIRE` and its credential
    refusal is `RECORDED` — so a row that emitted only its first quote would emit, for
    RS-53, the half this world deliberately does not model. :attr:`quote` remains the first;
    this is the whole ordered set, and :class:`whetstone_gate.world.results.RazorpayRejection`
    selects by index.
    """

    http: str
    """The row's declared ``HTTP`` field, verbatim. Empty if the row declares none.

    Carried so that no HTTP status is ever written as a literal in this package. `400` is
    also `attacker_context_summary_max_tokens`' registry literal, and the registry's own
    note explains that the collision *"would fire constantly on legitimate code WITH NO
    LEGITIMATE REMEDY — an HTTP status cannot be read from config/"*. It can, however, be
    read from the row that documents it, which is what this field is for.
    """

    body: str
    """The row's full text, so a caller can assert a bound is still worded as it assumes.

    Used by :mod:`whetstone_gate.world.bounds`, whose every `[Razorpay-defined]` figure
    declares a needle that must still occur in its own row.
    """


@dataclass(frozen=True)
class Oracle:
    """Every row of `RAZORPAY_SEMANTICS.md`, parsed. Immutable, and passed around as data."""

    rows: tuple[Row, ...]

    def by_id(self, rs_id: str) -> Row:
        for row in self.rows:
            if row.rs_id == rs_id:
                return row
        raise OracleParseError(
            f"{rs_id} names no row of {ORACLE_FILENAME}. The engine addresses documented "
            f"rejections by id and takes their words from the oracle, so a pointer at a row "
            f"that does not exist must stop the run rather than emit an invented string."
        )

    def labelled(self, label: str) -> tuple[Row, ...]:
        """Every row carrying ``label``, in file order."""
        if label not in LABELS:
            raise OracleParseError(f"{label!r} is not one of {LABELS}")
        return tuple(row for row in self.rows if row.label == label)

    def counts(self) -> dict[str, int]:
        """``{label: count}`` for all three labels, zeros included.

        `PROCESS.md` §9: *"Zero-occurrence branches are printed as zeros, never omitted."*
        """
        return {label: len(self.labelled(label)) for label in LABELS}


def load() -> Oracle:
    """Read and parse `RAZORPAY_SEMANTICS.md`. **The only I/O in this module.**

    Not cached, for :func:`whetstone_gate.config.load`'s own reason: *"a cache would let a
    stale read outlive an edit during a long run."*
    """
    path = cfg.repo_root().joinpath(ORACLE_FILENAME)
    if not path.is_file():
        raise OracleParseError(
            f"{path} does not exist. RAZORPAY_SEMANTICS.md is a pre-registration artefact "
            f"(CONTEXT.md §15.0) and is the oracle CONTEXT.md §13.5(7) makes the spend-free "
            f"self-test read; it is not optional and has no fallback."
        )
    return parse(path.read_text(encoding="utf-8"))


def parse(text: str) -> Oracle:
    """Parse the oracle's text. **Pure**: same bytes in, same rows out."""
    rows = list(_full_rows(text))
    rows.extend(_recorded_rows(text))

    seen: dict[str, str] = {}
    for row in rows:
        if row.rs_id in seen:
            raise OracleParseError(
                f"{row.rs_id} was parsed twice. §10's census asserts RS-01…RS-71 are "
                f"'contiguous, no gaps and no duplicates', and a duplicated row would be "
                f"counted twice in a published denominator."
            )
        seen[row.rs_id] = row.label

    if not rows:
        raise OracleParseError(
            f"{ORACLE_FILENAME} parsed to zero rows. A parser that silently reads nothing "
            f"is the same class of defect as the check it replaces."
        )
    return Oracle(tuple(rows))


# --------------------------------------------------------------------------------------
# The three shapes. Each is a pure function of the text.
# --------------------------------------------------------------------------------------


def _full_rows(text: str):
    """Rows RS-01…RS-53: a ``### RS-nn`` heading and the block beneath it."""
    lines = text.splitlines()
    starts: list[int] = []
    notes: list[str] = []
    templates: list[str] = []
    for index, line in enumerate(lines):
        if not line.startswith(_ROW_HEADING):
            continue
        if _NOTE_MARKER in line:
            notes.append(line)
        elif not _split_heading(line)[0][len("RS-") :].isdigit():
            templates.append(line)
        else:
            starts.append(index)

    if len(notes) != 1:
        raise OracleParseError(
            f"expected exactly one '### RS-nn (note)' heading — RS-70's, which §10 records "
            f"as 'the one identifier in this file that names two things (OF-19)' — and "
            f"found {len(notes)}: {notes}. A second one would either be a row this parser "
            f"drops silently, or a row counted twice."
        )
    if len(templates) != 1:
        raise OracleParseError(
            f"expected exactly one non-numeric '{_ROW_HEADING}nn' heading — §0's format "
            f"template, which is prose about the row shape and not a row — and found "
            f"{len(templates)}: {templates}. Every other heading must name a real row, "
            f"because a heading this parser skips is a row the self-test never counts."
        )
    if not starts:
        raise OracleParseError(f"no '{_ROW_HEADING}nn' headings found in {ORACLE_FILENAME}")

    for position, start in enumerate(starts):
        end = len(lines)
        for index in range(start + 1, len(lines)):
            if lines[index].startswith(_BLOCK_ENDS):
                end = index
                break
        heading_line = lines[start]
        block = "\n".join(lines[start:end])
        rs_id, heading = _split_heading(heading_line)
        quotes = _block_titles(lines[start:end])
        yield Row(
            rs_id=rs_id,
            heading=heading,
            label=_label_of(block, rs_id),
            reason="",
            quote=quotes[0] if quotes else "",
            quotes=quotes,
            http=_field(block, _HTTP_FIELD),
            body=block,
        )
        del position


def _recorded_rows(text: str):
    """Rows RS-54…RS-71: one line each of §6's table, with the reason cell."""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.startswith(_RECORDED_SECTION):
            start = index
            break
    if start is None:
        raise OracleParseError(
            f"{ORACLE_FILENAME} has no '{_RECORDED_SECTION.strip()}' section, so the "
            f"RECORDED set — the 18 rows Q-018's ruling requires the self-test to PRINT "
            f"with their reasons — could not be read."
        )
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break

    for line in lines[start:end]:
        if not line.startswith(_RECORDED_ROW):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            raise OracleParseError(
                f"§6 table row has {len(cells)} cells, expected 6 "
                f"(id, title, HTTP, source, fetched, why not reachable): {line!r}"
            )
        title = _clean(cells[1])
        yield Row(
            rs_id=_clean(cells[0]),
            heading=title,
            label=RECORDED,
            reason=cells[5],
            quote=title,
            quotes=(title,),
            http=cells[2],
            body=line,
        )


# --------------------------------------------------------------------------------------
# Field extraction. Every one refuses rather than guessing.
# --------------------------------------------------------------------------------------


def _split_heading(line: str) -> tuple[str, str]:
    """``### RS-01 — A1: a capture amount…`` → ``("RS-01", "A1: a capture amount…")``."""
    remainder = line[len("### ") :].strip()
    rs_id, _, rest = remainder.partition(" ")
    title = rest.strip()
    for dash in ("—", "-"):
        if title.startswith(dash):
            title = title[len(dash) :].strip()
            break
    return rs_id, title


def _label_of(block: str, rs_id: str) -> str:
    """The row's ``World`` label — the text between the first pair of backticks after it.

    ⚠️ **RS-53 carries two labels and §10 rules that it is counted once, as `MUST-FIRE`:**
    *"its extra-field refusal is `MUST-FIRE` and its API-credential refusal is `RECORDED`.
    It is counted **once, as `MUST-FIRE`**, and the credential half is named in its own
    Notes. No other row is split."* Taking the **first** label implements that ruling
    exactly, and it is the only row where the choice arises.
    """
    at = block.find(_WORLD_FIELD)
    if at < 0:
        raise OracleParseError(
            f"{rs_id} declares no {_WORLD_FIELD} field, so its label cannot be read. §0 "
            f"requires every row to carry one; a row with no label is a row the self-test's "
            f"denominator would silently lose."
        )
    rest = block[at + len(_WORLD_FIELD) :]
    open_tick = rest.find("`")
    close_tick = rest.find("`", open_tick + 1) if open_tick >= 0 else -1
    if open_tick < 0 or close_tick < 0:
        raise OracleParseError(f"{rs_id}: no backtick-quoted label follows {_WORLD_FIELD}")
    token = rest[open_tick + 1 : close_tick].strip()
    if token not in LABELS:
        raise OracleParseError(
            f"{rs_id} declares World label {token!r}, which is not one of {LABELS}. §0's "
            f"table fixes the three values; a fourth would mean the self-test is reading a "
            f"partition it does not understand."
        )
    return token


def _field(block: str, marker: str) -> str:
    """The text of a ``**Marker** value`` field, up to the next separator."""
    at = block.find(marker)
    if at < 0:
        return ""
    rest = block[at + len(marker) :]
    for terminator in ("\n", "·", "**"):
        cut = rest.find(terminator)
        if cut >= 0:
            rest = rest[:cut]
    return rest.strip()


def _block_titles(lines: list[str]) -> tuple[str, ...]:
    """The first payload line of every ``>`` block, in file order.

    A *block* is a run of consecutive ``>`` lines. Its **title** is its first line carrying a
    payload — the error string, the parameter name, or the prose bullet, depending on the
    row. Later lines (``* code:``, ``* description:``, ``* solution:``) are the fields.

    ⚠️ **Blank `>` lines are skipped and that is declared rather than assumed.** §0's own
    re-runnable check makes the same distinction and states its denominator both ways —
    *"304 lines begin with `>` … 3 are quote-internal blanks; 301 carry a payload"* — after
    the published figure was corrected from 299 for embedding exactly this narrowing
    undeclared (`OPEN_FINDINGS.md` OF-17).
    """
    titles: list[str] = []
    inside = False
    for line in lines:
        if not line.startswith(_QUOTE_PREFIX):
            inside = False
            continue
        payload = line[len(_QUOTE_PREFIX) :].strip()
        if payload.startswith(_ERROR_FIELD_LABEL):
            payload = payload[len(_ERROR_FIELD_LABEL) :].strip()
        payload = _clean(payload)
        if not payload:
            continue
        if not inside:
            titles.append(payload)
            inside = True
    return tuple(titles)


def _clean(cell: str) -> str:
    """Strip the markdown emphasis a table cell or quote wraps its payload in.

    ⚠️ A wrapping marker is removed **only when the payload does not itself contain that
    marker**. RS-70's §6 cell is three backticked error strings joined by ``·``; stripping
    its outer backticks would leave a mangled string that looks like one error and is
    three. The row that names two things is also the row that stresses this helper.
    """
    text = cell.strip()
    changed = True
    while changed:
        changed = False
        for marker in ("**", "*", "`", '"'):
            width = len(marker)
            if (
                text.startswith(marker)
                and text.endswith(marker)
                and len(text) > 2 * width
                and marker not in text[width:-width]
            ):
                text = text[width:-width].strip()
                changed = True
    return text.strip()
