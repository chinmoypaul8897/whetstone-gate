"""THE OPERATOR GATE - this test is SUPPOSED to be red until the operator acts.

`CONTEXT.md` S13.3.2:

    **The Google model names above are the builder's dashboard labels, not API id
    strings.** ... The S13.7 day-one screenshot MUST capture the exact Google API id for
    each label (e.g. the `models/gemma-...` and `models/gemini-...` strings) ... Building
    against a dashboard label rather than an id would be a defect; **this is the one place
    the spec cannot supply the string first-hand.**

So the ids cannot be derived, guessed, or discovered by any session - only read off a
dashboard by the operator. Until they are, `config/lanes.yaml` carries explicit
``TODO_OPERATOR`` placeholders and this test fails.

**Why it is marked ``operator_gate`` rather than left in the unit suite** (QUESTIONS.md
Q-009): C0's done-when demands *both* that ``make test`` runs green from a clean clone
*and* that a test fails while placeholders remain. Those are only compatible if the two
live in different tiers, so:

  * ``make test``     - the unit suite. Deselects this, **and prints how many
                        operator-gate tests it deselected and why.** Nothing is hidden.
  * ``make selftest`` - the pre-spend gate. Runs this. **Red today, correctly**, because
                        no token may be spent against a guessed model id.

The alternative - dropping the placeholder check into the unit suite - would leave a
suite that cannot be green before 31 August, and a suite nobody can make green is a suite
nobody reads.
"""

from __future__ import annotations

import pytest

from whetstone_gate import config as cfg

pytestmark = pytest.mark.operator_gate


def test_no_operator_placeholder_remains_in_config():
    outstanding = [s for s in cfg.outstanding_sentinels() if s[2] == "TODO_OPERATOR"]

    assert not outstanding, (
        "OPERATOR ACTION REQUIRED - "
        f"{len(outstanding)} value(s) can only come from the operator's provider "
        "dashboard:\n\n"
        + "\n".join(f"    - config/{name}.yaml : {dotted}" for name, dotted, _ in outstanding)
        + "\n\n"
        "  WHAT TO DO: open Google AI Studio -> the model list, and copy the EXACT API id\n"
        "  string for each dashboard label (the `models/gemma-...` / `models/gemini-...`\n"
        "  form, not the display name). Write each into config/lanes.yaml in place of\n"
        "  TODO_OPERATOR:\n"
        "      gemma-26b       <- 'Gemma 4 26B'\n"
        "      gemma-31b       <- 'Gemma 4 31B'\n"
        "      flash-lite-3.1  <- 'Gemini 3.1 Flash Lite'\n"
        "      flash-lite-3.5  <- 'Gemini 3.5 Flash Lite'\n\n"
        "  WHY IT CANNOT BE GUESSED: CONTEXT.md S13.3.2 - 'Building against a dashboard\n"
        "  label rather than an id would be a defect; this is the one place the spec\n"
        "  cannot supply the string first-hand.' A wrong id fails at the first API call\n"
        "  of the sweep, after the freeze, on a day with no slack.\n\n"
        "  See QUESTIONS.md Q-006. The exact ids are written into PROTOCOL.md at prereg-v1."
    )


def test_the_camel_branch_is_decided_before_any_camel_run():
    """RUN-1 (31 Aug, 90 minutes, timeboxed) decides Branch A or Branch B.

    ! **Branch B is published as a result, not hidden as a failure** - the comparator
    ships as a citation of Tables 5-7 of arXiv 2503.18813v2 with the `CONTEXT.md` S8.5.1
    reason verbatim. Either way the answer is recorded in `PROTOCOL.md` before the tag.
    """
    branch = cfg.load("lanes").data.get("camel_comparator", {}).get("branch")
    assert not cfg.is_sentinel(branch), (
        "the CaMeL branch is still undecided. It is decided by RUN-1 on 31 August, inside "
        "a 90-minute box, and written into PROTOCOL.md. Branch B - shipping the comparator "
        "as a citation - is a RESULT, and publishing it as one is the point."
    )
