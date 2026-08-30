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


def test_registry_covers_every_config_constant():
    """Every §8.6 row is in the registry, and every registry row points at a real config key.

    This is the check that stops the tripwire silently losing coverage. `CONTEXT.md` §8.6:
    *"Any constant that is not in this table and not in `config/` is a defect, and finding
    one is a review BLOCKER."*
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
