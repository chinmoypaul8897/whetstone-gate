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

⚠️ **REVIEW_C0_1 B-04, and why this file now looks the way it does.** Both gates below
used to read `config/` **around** the loader:

    branch = cfg.load("lanes").data.get("camel_comparator", {}).get("branch")
    assert not cfg.is_sentinel(branch)

`.data.get(..., {})` is the defaulting accessor `config.py`'s own docstring says *"does not
exist and must not be added"*, and `is_sentinel(None)` is `False` - **so ABSENCE READ AS
DECIDED.** Deleting the `camel_comparator:` block flipped `make selftest` from correctly
RED to **GREEN**, and deleting `config/lanes.yaml` entirely left the other gate passing
too. The gate standing between this project and spending its finite free tier against a
guessed model id **passed vacuously whenever the file it guards was absent.** See
`INCIDENTS.md` **INC-15**.

Both predicates now go **through** `require()`, so a missing file, a missing key and an
undetermined value are each a hard refusal. Each is a helper returning either ``None`` or
the operator-facing message, so that `tests/test_c0_fix_probes.py` can fire the gate at a
broken fixture and assert it goes red - `PROCESS.md` S5.4: *a release gate that has never
gone red is only decorative.*
"""

from __future__ import annotations

import pytest

from whetstone_gate import config as cfg

pytestmark = pytest.mark.operator_gate


_WHAT_TO_DO = (
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


def operator_placeholder_problem() -> str | None:
    """Return the operator-facing message, or ``None`` if nothing is owed.

    ⚠️ Goes through :func:`config.outstanding_sentinels`, which now **raises** when a
    REQUIRED config file is absent (B-03). Before that, deleting `config/lanes.yaml`
    entirely left this gate passing over a file that was not there.
    """
    try:
        outstanding = [s for s in cfg.outstanding_sentinels() if s[2] == "TODO_OPERATOR"]
    except cfg.ConfigError as exc:
        return (
            "CONFIG REFUSAL - the pre-spend gate cannot even READ config/, so it certainly\n"
            "cannot certify that no placeholder remains. A gate that passes when the file\n"
            "it guards is absent is worse than no gate (INCIDENTS.md INC-15).\n\n"
            f"    {exc}"
        )
    if not outstanding:
        return None
    return (
        "OPERATOR ACTION REQUIRED - "
        f"{len(outstanding)} value(s) can only come from the operator's provider "
        "dashboard:\n\n"
        + "\n".join(f"    - config/{name}.yaml : {dotted}" for name, dotted, _ in outstanding)
        + "\n\n"
        + _WHAT_TO_DO
    )


def camel_branch_problem() -> str | None:
    """Return why the CaMeL branch is not yet decided, or ``None`` if it is.

    ⚠️ `require()` is the ONLY read path. It raises :class:`config.ConfigFileMissing` if
    `lanes.yaml` is gone, :class:`config.MissingRequiredValue` if the key is gone, and
    :class:`config.UndeterminedValue` while the value is a ``TODO_`` sentinel. All three
    are the same answer to this gate - *"nobody has decided"* - and all three used to be
    invisible to it.
    """
    try:
        branch = cfg.load("lanes").require("camel_comparator.branch")
    except cfg.ConfigError as exc:
        return (
            "the CaMeL branch is still undecided. It is decided by RUN-1 on 31 August, "
            "inside a 90-minute box, and written into PROTOCOL.md. Branch B - shipping the "
            "comparator as a citation - is a RESULT, and publishing it as one is the "
            "point.\n\n"
            f"    {type(exc).__name__}: {exc}"
        )
    if not isinstance(branch, str) or not branch.strip():
        return (
            f"config/lanes.yaml states camel_comparator.branch = {branch!r}, which names no "
            "branch. RUN-1 records Branch A or Branch B; anything else is a value nobody "
            "chose."
        )
    return None


def test_no_operator_placeholder_remains_in_config():
    problem = operator_placeholder_problem()
    assert problem is None, problem


def test_the_camel_branch_is_decided_before_any_camel_run():
    """RUN-1 (31 Aug, 90 minutes, timeboxed) decides Branch A or Branch B.

    ! **Branch B is published as a result, not hidden as a failure** - the comparator
    ships as a citation of **Table 2, Appendix B ("Full results tables"), the `o3 High`
    block, `banking` column** of arXiv 2503.18813v2 - CaMeL 81.2% +/- 19.1 against
    `Native Tool Calling API` 62.5% +/- 23.7, the paper's own Difference row +18.8% +/- 4.6
    - with the `CONTEXT.md` S8.5.1 reason verbatim. Either way the answer is recorded in
    `PROTOCOL.md` before the tag.

    ! **NOT Tables 5-7.** Those are Appendix C ("Baseline results"), base model
    `Claude 3.5 Sonnet`, CaMeL against OTHER DEFENCES, and on `banking` they show CaMeL
    BEHIND the undefended model. **Table 7 is RETAINED as S8.5.2's P2 citation**, where it
    is right and where C13 verified it exactly. (Q-058 RULED 2026-09-01; Q-064; Q-074.)

    ! This docstring is the FIFTH site of Q-064's citation and the one a human actually
    reads: this test is deliberately red in `make selftest`, so the text above is printed
    IN FULL every time any session runs the pre-spend gate. It survived four fences that
    each named this file under NOT (Q-074). `tests/test_repo_invariants.py`'s
    superseded-string tripwire now scans for it, and was fired at this docstring's previous
    text to prove it would have caught it.
    """
    problem = camel_branch_problem()
    assert problem is None, problem
