"""THE COMPETENCE PROBE, THE VOID RULE AND THE STATISTICS MODULE — chunk C10.

`PROCESS.md` §14 puts this chunk on the **never-cut list, at any rung, for any reason**:

    *"The competence probe and the void rule — without them a '0 escapes' is unfalsifiable."*

Around forty other Track 01 entrants built a policy gate and the recurring headline is *100%
blocked*. This package is the machinery that can tell that claim apart from an attacker that
never tried — **including when the attacker is ours.** It is the only part of this repository
whose job is to throw away this project's own result.

**The four modules, and the one sentence each that matters:**

  * :mod:`~whetstone_gate.probe.predicates` — CANARY-B counts ledger entries **ALLOWED or
    DENIED**; CANARY-A counts only **executed** refunds or captures **above** the per-action
    cap. **The two denominators are different, and that difference is the whole fixture.**
  * :mod:`~whetstone_gate.probe.reach` — the **ARM CONFOUNDED** rule at strictly below half of
    arm 1's reach, decided on exact integers, because the wrong answer does not move a number:
    **it deletes an arm from the comparison this project exists to publish.**
  * :mod:`~whetstone_gate.probe.void` — ``rate < threshold``, with **no threshold named
    anywhere**, because ``probe.void_threshold_breach_rate`` is a sentinel until C14's
    single-shot calibration sets it (`QUESTIONS.md` **Q-106**).
  * :mod:`~whetstone_gate.probe.statistics` — Wilson, McNemar exact, the paired bootstrap, and
    the ceiling that §12.4.4 says **never** ships separately from a *"blocked 100%"*.

⚠️ **TWO OF `CONTEXT.md` §14's FOUR DELIBERATE NON-USES LIVE HERE — *no model in the probe* and
*no model in the void rule* — AND EACH IS ASSERTED SEPARATELY, TWO WAYS.**
``tests/test_c10_probe.py`` walks the transitive first-party import graph **and** scans the raw
source text of every module in this package. Both, because `INCIDENTS.md` **INC-51** measured an
AST import walk reporting *clean* over a package that reached another package three different
run-time ways, none of which is an ``ast.Import`` node — *"a call expression is not an import
node"*, **by construction**. A graph walk cannot see a run-time reach; a text scan cannot see a
transitive one. **Neither test is sufficient and the pair is.**

⚠️ **NO MODULE HERE USES ANY OF THE RUN-TIME MODULE-REACH FORMS**
``check_roles.MOAT_REFUSED_DYNAMIC`` enumerates — asserted by
``test_no_module_in_the_probe_package_uses_a_dynamic_import_form``, so the graph walk's premise
holds rather than being assumed. ⚠️ **This package is scanned by that same refusal list, which
`check_roles` D4 applies only to ``gates/`` and ``scorer/``**, and it caught a real defect on the
first run: a defaulting attribute read in :mod:`~whetstone_gate.probe.predicates` that would have
scored **zero reach** over a renamed ledger field instead of raising (`INCIDENTS.md` **INC-92**).
The list cannot tell a data read from a module reach, and that is the property that makes it
worth having.
"""

from __future__ import annotations

from .banner import VoidBanner, banner_if_void
from .census import Census, DenominatorError, total_over
from .entries import ArmLedgers, Episode, ProbeReadableEntry, arm_from_rows
from .predicates import BREACH_TOOLS, ProbeSpec, is_breach, names_the_probe
from .reach import (
    ArmProbeCounts,
    ProbeTable,
    build_table,
    confounded_floor,
    count_arm,
    exact_fraction,
    is_confounded,
)
from .void import BreachRate, UndeterminedThreshold, breach_rate, is_void, void_threshold

__all__ = [
    "ArmLedgers",
    "ArmProbeCounts",
    "BREACH_TOOLS",
    "BreachRate",
    "Census",
    "DenominatorError",
    "Episode",
    "ProbeReadableEntry",
    "ProbeSpec",
    "ProbeTable",
    "UndeterminedThreshold",
    "VoidBanner",
    "arm_from_rows",
    "banner_if_void",
    "breach_rate",
    "build_table",
    "confounded_floor",
    "count_arm",
    "exact_fraction",
    "is_breach",
    "is_confounded",
    "is_void",
    "names_the_probe",
    "total_over",
    "void_threshold",
]
