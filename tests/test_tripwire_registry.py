"""The hard-rule-9 tripwire: no spec value is hardcoded in implementation source.

    **CONFIG, NOT CONSTANTS.** Every spec-specified value lives in `config/` … A tripwire
    test scans the source for hardcoded spec values, using **`CONTEXT.md` §8.6's constants
    table as its authoritative list** (that table was amended on 2026-08-30 to actually
    contain every author-chosen constant; it previously did not, so the tripwire had
    nothing complete to scan against).

Two tests do two different jobs, and the second is the one that keeps the first honest:

  * :func:`test_no_spec_value_is_hardcoded_in_implementation_source` — the scan itself.
  * :func:`test_registry_covers_every_config_constant` — the **coverage** check. Without
    it, a constant could be dropped from the registry and the scan would still be green
    while no longer scanning for it. That is a tripwire in name only.

**C0 has no project logic, so the scan passes trivially today.** That is expected and is
not a weakness: the tripwire exists from the first commit so that the first chunk which
*could* violate it is already being watched, rather than the check arriving after the
code it was meant to constrain.
"""

from __future__ import annotations

import re

import pytest

from whetstone_gate import config as cfg
from whetstone_gate.spec_constants import (
    SPEC_CONSTANTS,
    TRIPWIRE_SELF_EXCLUSION,
    ScanMode,
    SpecConstant,
)


def _strip_comments_and_docstrings(source: str) -> str:
    """Remove ``#`` comments and triple-quoted blocks.

    Prose *about* a constant is not a hardcoded constant. A docstring that says
    "the ₹50,000 per-action cap" documents the code; a literal ``5000000`` in an
    expression is the defect. Conflating them would make the tripwire fire on its own
    explanations, and the first response to that is always to weaken it.
    """
    without_docstrings = re.sub(r'("""|\'\'\')(?:.|\n)*?\1', '""', source)
    return re.sub(r"#[^\n]*", "", without_docstrings)


def _strict_hits(constant: SpecConstant, code: str) -> list[str]:
    hits = []
    for literal in constant.literals:
        for match in re.finditer(rf"(?<![\w.]){re.escape(literal)}(?![\w.])", code):
            line = code.count("\n", 0, match.start()) + 1
            hits.append(f"line {line}: literal {literal!r}")
    return hits


def _contextual_hits(constant: SpecConstant, code: str) -> list[str]:
    """Fire only when the literal is *bound to a name that means this constant*.

    ``range(20)`` is fine; ``turn_budget = 20`` is not. Small integers recur innocently
    everywhere, and a strict scan for them would be so noisy that the only sustainable
    response would be to disable it.
    """
    if not constant.name_patterns:
        return []
    names = "|".join(re.escape(p) for p in constant.name_patterns)
    values = "|".join(re.escape(v) for v in constant.literals)
    pattern = rf"\w*(?:{names})\w*\s*(?:=|:|==|,)\s*(?:{values})(?![\w.])"
    hits = []
    for match in re.finditer(pattern, code, re.IGNORECASE):
        line = code.count("\n", 0, match.start()) + 1
        hits.append(f"line {line}: {match.group(0).strip()!r}")
    return hits


def test_no_spec_value_is_hardcoded_in_implementation_source(implementation_sources, repo_root):
    findings: list[str] = []
    for path in implementation_sources:
        code = _strip_comments_and_docstrings(path.read_text(encoding="utf-8"))
        rel = path.relative_to(repo_root).as_posix()
        for constant in SPEC_CONSTANTS:
            hits = (
                _strict_hits(constant, code)
                if constant.mode is ScanMode.STRICT
                else _contextual_hits(constant, code)
            )
            for hit in hits:
                findings.append(
                    f"  {rel} {hit}\n"
                    f"      constant : {constant.key}  {constant.tag}\n"
                    f"      read from: {constant.config_path}"
                )

    assert not findings, (
        "hard rule 9 violation — a CONTEXT.md §8.6 constant is hardcoded in implementation "
        "source instead of being read from config/:\n\n"
        + "\n".join(findings)
        + "\n\n  The remedy is to load it through whetstone_gate.config. It is NOT to add an "
        "exemption: config/ is a frozen pre-registration artefact, and a value that lives in "
        "source instead of config/ is a value the freeze does not cover."
    )


def normalise_spec_row(label: str) -> str:
    """Reduce a §8.6 **Constant** cell (or a registry ``spec_row``) to a comparable key.

    The table is prose in markdown: some cells are bold, some carry backticks, some carry an
    ``[ADDED 30 Aug]`` / ``[ADDED 31 Aug]`` marker, and the 30-August rows use an em dash
    where the 31-August rows use a hyphen. None of that is the constant's identity.
    """
    text = re.sub(r"\[ADDED[^\]]*\]", " ", label)
    text = text.replace("*", " ").replace("`", " ")
    text = re.sub(r"[‐-―−]", "-", text)  # any dash variant → ASCII hyphen
    return re.sub(r"\s+", " ", text).strip().lower()


def parse_s86_rows(context_md: str) -> list[str]:
    """Return the **Constant** cell of every row of `CONTEXT.md` §8.6's constants table.

    ⚠️ Parsed rather than transcribed, deliberately. A transcription would be one more copy
    of the table that can drift from it — which is the entire defect this closes.
    """
    lines = context_md.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("## 8.6 "))
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("#")), len(lines)
    )
    section = lines[start:end]
    header = next(
        i for i, line in enumerate(section) if line.strip().startswith("| Constant ")
    )
    rows: list[str] = []
    for line in section[header + 2 :]:  # skip the header and the |---|---|---| separator
        if not line.strip().startswith("|"):
            break
        rows.append(line.strip().strip("|").split("|")[0].strip())
    return rows


def test_every_s86_row_reaches_the_registry(repo_root):
    """⚠️ **THE DIRECTION THAT WAS NEVER CHECKED, AND THE MECHANISM BY WHICH EIGHT ROWS WENT
    MISSING.**

    ``test_registry_covers_every_config_constant``'s docstring claimed *"Every §8.6 row is in
    the registry, **and** every registry row points at a real config key."* **Only the second
    half was implemented.** It iterated ``SPEC_CONSTANTS`` and never ``§8.6``, so it could
    only ever find a registry row pointing at a missing config key — never a spec row the
    registry had never heard of. **A constant added to the spec that the tripwire never
    learns about is exactly the constant it cannot catch: the gap is not in the scan, it is
    in what the scan is pointed at.**

    On 2026-08-31 the architect found **eight** such constants, and **two of them were in
    neither §8.6 nor `config/` at all** — which §8.6's own next sentence calls *a defect, and
    finding one is a review BLOCKER* — while being load-bearing in **every row of §13.4's
    arithmetic**. §8.6's amended warning is blunt about the record: *"THIS IS THE SECOND TIME
    THIS TABLE HAS BEEN INCOMPLETE."* `ARCHITECT_CHECK_0.md` §5.

    Both directions are asserted here, so neither list can grow a row the other has not seen.
    """
    rows = parse_s86_rows((repo_root / "CONTEXT.md").read_text(encoding="utf-8"))
    assert len(rows) >= 21, (
        f"§8.6's constants table parsed to {len(rows)} rows, which is fewer than the 21 it "
        f"held on 2026-08-31. Either the table shrank or this parser stopped seeing it — "
        f"and a parser that silently reads nothing is the same class of defect as the check "
        f"it replaces."
    )

    in_spec = {normalise_spec_row(r) for r in rows}
    in_registry = {normalise_spec_row(c.spec_row) for c in SPEC_CONSTANTS}

    missing = sorted(in_spec - in_registry)
    assert not missing, (
        "CONTEXT.md §8.6 carries constants the tripwire's registry has never heard of, so "
        f"the tripwire does not scan for them and reports green anyway: {missing}. §8.6: "
        "'Any constant that is not in this table and not in config/ is a defect, and "
        "finding one is a review BLOCKER.' Add a SpecConstant row naming this spec_row."
    )

    phantom = sorted(in_registry - in_spec)
    assert not phantom, (
        f"the registry names §8.6 rows that do not exist in CONTEXT.md: {phantom}. Either a "
        "row was renamed in the spec and not here, or this registry has invented a constant "
        "the specification does not carry — and the registry is a TRANSCRIPTION of that "
        "table, nothing else."
    )


def test_registry_covers_every_config_constant():
    """And the other direction: every registry row points at a real config key.

    This is the half that was implemented. It is what killed mutant M16 (renaming a row key).
    The §8.6 → registry half is :func:`test_every_s86_row_reaches_the_registry`, added by the
    C0 FIX session because it did not exist.
    """
    protocol = cfg.load("protocol")

    for constant in SPEC_CONSTANTS:
        file_part, _, dotted = constant.config_path.partition(":")
        assert file_part == "protocol.yaml", constant.key
        if dotted.endswith(".*"):
            # A whole subtree (seeds.*, world.*). Assert the subtree exists.
            assert protocol.has(dotted[:-2]) or isinstance(
                protocol.data.get(dotted.split(".")[0]), dict
            ), f"{constant.key}: {dotted} names no section of protocol.yaml"
        else:
            assert protocol.has(dotted), (
                f"{constant.key}: registry points at {dotted}, which protocol.yaml does not "
                f"define. Either the config lost a value or the registry drifted."
            )


def test_every_registry_row_is_tagged_razorpay_or_author_chosen():
    """`PROVENANCE.md`'s central rule: a constant carrying neither tag is a defect.

    ``[Razorpay-defined]`` means they documented it and we copied it.
    ``[merchant-policy, author-chosen]`` means **we invented it** and the result moves if
    it is wrong. A reader must be able to tell which, for every number in the run.
    """
    allowed = {"[Razorpay-defined]", "[merchant-policy, author-chosen]"}
    for constant in SPEC_CONSTANTS:
        assert constant.tag in allowed, f"{constant.key} carries {constant.tag!r}"


def test_contextual_constants_declare_name_patterns():
    """A CONTEXTUAL row with no name patterns would scan for nothing and always pass."""
    for constant in SPEC_CONSTANTS:
        if constant.mode is ScanMode.CONTEXTUAL:
            assert constant.name_patterns, (
                f"{constant.key} is CONTEXTUAL but declares no name_patterns, so it would "
                f"silently match nothing — a green check that checks nothing."
            )


def test_the_self_exclusion_is_exactly_one_file(repo_root):
    """The registry excludes itself, and nothing else, ever.

    An exclusion list is the natural place for a tripwire to die quietly. Pinning it to a
    single named file means widening it requires editing this assertion, which a review
    will see.
    """
    assert TRIPWIRE_SELF_EXCLUSION == "src/whetstone_gate/spec_constants.py"
    assert (repo_root / TRIPWIRE_SELF_EXCLUSION).is_file()


def test_the_tripwire_actually_fires(tmp_path):
    """The seeded-defect principle, applied to the tripwire itself.

    `ai-playbook` B.9: *"a release gate that has never gone red is only decorative."* A
    scan that has never fired is indistinguishable from a scan with a broken regex, so
    here it is pointed at a file that really does hardcode two §8.6 constants.
    """
    offender = tmp_path / "bad_gate.py"
    offender.write_text(
        "def check(amount):\n"
        "    return amount <= 5000000\n"       # per-action cap, STRICT
        "\n"
        "turn_budget = 20\n",                  # turn budget, CONTEXTUAL
        encoding="utf-8",
    )
    code = _strip_comments_and_docstrings(offender.read_text(encoding="utf-8"))

    strict = _strict_hits(next(c for c in SPEC_CONSTANTS if c.key == "per_action_cap_paise"), code)
    contextual = _contextual_hits(next(c for c in SPEC_CONSTANTS if c.key == "turn_budget"), code)

    assert strict, "the STRICT scan failed to catch a bare 5000000"
    assert contextual, "the CONTEXTUAL scan failed to catch `turn_budget = 20`"


@pytest.mark.parametrize(
    "innocent",
    [
        "for i in range(20):\n    pass\n",
        "HTTP_TOO_MANY_REQUESTS = 429\n",
        "parts = name.split('.')[2]\n",
    ],
)
def test_the_contextual_scan_does_not_fire_on_ordinary_code(innocent):
    """The other half of a usable tripwire: it must not cry wolf.

    A check that fires on ``range(20)`` gets switched off within a day, and then the real
    violation ships.
    """
    code = _strip_comments_and_docstrings(innocent)
    for constant in SPEC_CONSTANTS:
        if constant.mode is ScanMode.CONTEXTUAL:
            assert not _contextual_hits(constant, code), (
                f"{constant.key} fired on ordinary code: {innocent!r}"
            )
