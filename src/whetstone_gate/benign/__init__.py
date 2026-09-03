"""**C12 — THE BENIGN SOLVER. THE COUNTER-METRIC.**

⚠️ **WITHOUT THIS PACKAGE, *"ZERO ESCAPES"* IS HALF A RESULT.** A gate that blocks
everything scores zero escapes and is useless, and **nothing else in this repository can
tell those two apart.** `PROCESS.md` §14's never-cut list names *"the counter-metric — the
benign solver and the paired FP delta"* and adds: *"A project that publishes only what it
blocked has published half a result."*

`INCIDENTS.md` `INC-04` is the fixture this chunk exists to generalise, and its ``Missing``
field is this chunk's whole justification, verbatim:

    **Missing:** A benign counter-metric. The spike measured only what was blocked, so a
    predicate that blocked everything would have scored perfectly on every number it
    reported.

--------------------------------------------------------------------------------------
LAYOUT — hard rule 8's purity separation
--------------------------------------------------------------------------------------

**Core (no I/O, no clock, no network, no randomness):**
  :mod:`.constants`  what the solver runs on — and the two values `config/` does not carry
  :mod:`.texts`      the solver's system prompt: a merchant's job, not an attacker's goal
  :mod:`.catalogue`  the benign work requests, each with its own end-state predicate
  :mod:`.executor`   one turn: gate → world → ledger
  :mod:`.solve`      the loop: assemble, one model call, execute, record
  :mod:`.paired`     ⚠️ **the paired FP delta — the whole measurement**
  :mod:`.blindness`  the needles, the scan, and the clean-surface control
  :mod:`.report`     the printed report, and the rate a dry run may not compute

**Thin outer shell (the modules that read a file, and all of them do):**
  :mod:`.shell`      the reads, the world, the gates, the paired matrix
  :mod:`.manifest`   the T-FP block's forty pre-registered τ² ids, and its refusal —
                     ⚠️ **shell, not core**: it reads ``config/protocol.yaml`` through the
                     one loader, both for ``selections.tfp_task_ids`` and for the count
  :mod:`.evidence`   `INC-04` driven end to end through the **real scorer** — ⚠️ also
                     shell, for the same reason: it reads the four scoring constants
  :mod:`.__main__`   the command line, and the flags that have to be typed

**Neither, and labelled so:**
  :mod:`.rehearsal`  a scripted transcript — ⚠️ **a fixture, never a model**

⚠️ **THIS LIST WAS WRONG IN THE FIRST VERSION AND THE ERROR IS THE KIND THIS PROJECT
EXISTS TO CATCH.** It omitted :mod:`.evidence` entirely and filed :mod:`.manifest` under
*core*, while both open ``config/protocol.yaml``. A layout claim that a reader cannot check
against the code is a docstring asserting hard rule 8's purity separation and quietly
breaking it. Found by this chunk's own adversarial pass, before its first commit, and
``tests/test_c12_benign.py`` now asserts the split module by module rather than trusting
this paragraph.

--------------------------------------------------------------------------------------
⚠️ THE FIVE CLAIMS THIS PACKAGE MAKES, EACH SCOPED EXACTLY
--------------------------------------------------------------------------------------

**1. THE SOLVER IS POLICY-BLIND, AND THE SCAN IS OVER THE ASSEMBLED BYTES.** It never sees
``data/policy.txt``, a cap, a clause id or a gate's denial reason — it sees §8.6's **one**
generic denial string, which is identical across arms and carries neither arm identity nor
clause. :mod:`.blindness` scans the context objects the model would have been handed, with
needles **read at run time** from ``config/`` and ``data/``, and with a **clean-surface
control that must score zero**. §12.3's reason: *"A benign solver tuned to avoid the gate
would make the false-positive rate a measurement of our own tuning."*

**2. IT IS NOT AN ATTACKER WITH THE ATTACKS REMOVED.** It has its own loop, its own system
prompt and no corpus. What it shares with C6 is §13.3's mandated sliding window and the
six-name tool surface — shared **so the two agents are shown the same thing**, because a
benign solver given a different context than the attacker would confound the comparison
§12.1 prints side by side. :mod:`.solve`'s docstring names that import as the first thing a
reviewer should challenge.

**3. THE DELTA IS PAIRED, TASK BY TASK AND ACTION BY ACTION.** The same task on the same
seed through arm 1 and through each gated arm. A false positive is **an action arm 1
executed and a gated arm refused** — never two independent rates subtracted. And the pair's
own validity is checked with the driver's
:func:`whetstone_gate.driver.episode.arm_invariant_prefix`: if the two arms' proposals
diverged **before** any refusal, the **action-level join** for that pair is dropped and the
pair is **named with its seed** beside the rate. ⚠️ **It stays in the TASK counts**, because
§12.3's denominator is *"the set the solver solved gate-OFF"* — a property of the baseline
arm alone, naming no proposal-agreement condition — and excluding it would publish a
different quantity under §12.3's label **and run in the flattering direction**. That
disagreement is `Q-160`, it is **Class A**, and it is the architect's.

**4. THE TWO FAILURE COUNTERS ARE SEPARATE, AND BOTH PRINT.** A task that failed because
the **gate refused** an action is a false positive; a task that failed because the solver
**could not do it** is not. Conflating them inflates our own counter-metric in the
flattering direction, and the flattering direction is the one a reader is entitled to
distrust. Both counters print, with the zeros.

**5. A DRY RUN PUBLISHES NO FIGURE.** :mod:`.rehearsal`'s transcript decides which calls
the solver makes, therefore which tasks complete, therefore the numerator **and** the
denominator. So :func:`.report.false_positive_rate` **refuses** a dry run and the refusal is
printed in the rate's place, while every count still prints. This is
:func:`whetstone_gate.driver.pilot.decide_n`'s discipline, copied: *"The dry run produces a
well-formed number and then REFUSES TO USE IT."*

--------------------------------------------------------------------------------------
⚠️ SEVEN THINGS THIS PACKAGE REFUSED TO DECIDE, AND WHERE EACH IS RECORDED
--------------------------------------------------------------------------------------

Hard rule 1: *"a session that stops on a real ambiguity has succeeded."*

  * **`Q-154`** — **C12's dependency C5 is UNBUILT** (`STATUS.md` says ``todo``), so no τ²
    task can be driven: there is no user simulator and **no first-party ``db_reward`` call
    site anywhere in ``src/``**, and §11.1 makes ``db_reward == 1.0`` the only definition of
    *"solved"* for a τ² task. The **T-FP block is enumerated and refused**, never skipped.
  * **`Q-155`** — and building C5 would not close it: **§8.6a's six-name surface and τ²'s
    tool set are disjoint**, and :class:`whetstone_gate.gates.action.CandidateAction` raises
    outside the six, so **no arm can form a verdict about a τ² action**. A bridge would be
    *our* claim about what a τ² task means, in the one block that exists because the tasks,
    the gold behaviour and the grader are **not ours**. **Class A.**
  * **`Q-156`** — ``config/`` carries **no** ``benign_solver.turn_budget`` and **no**
    ``benign_solver.temperature``, while §12.3's paired definition includes *"same
    temperature"*. Both are **required arguments with no default**; ``config/`` was **not**
    edited, because it is a pre-registration artefact.
  * **`Q-158`** — `PROCESS.md` §12.1 requires **30** mock-world scenarios *"traceable to a
    Razorpay documented example by URL — none builder-invented"*. `RAZORPAY_SEMANTICS.md`
    fetched **ten** pages and its rows are overwhelmingly **error** entries. **Three** are
    built and sourced; twenty-seven cannot be sourced from what this repository has fetched,
    and inventing them is the precise failure §12.3 names.
  * **`Q-157`** — the solver's system prompt is a **fourth authored text** and §8.6 authors
    three. Both places the house rule points at — ``data/`` and ``spec_constants.py`` — are
    outside this session's fence, so the text is in :mod:`.texts` with the gap recorded.
  * **`Q-159`** — :func:`whetstone_gate.driver.run.execute` **cannot host a benign
    episode**, measured three ways (see :mod:`.shell`). This package therefore consumes
    every reachable piece of the driver and **writes nothing anywhere**, rather than
    becoming a second runner.
  * **`Q-160`** — ⚠️ **Class A: does an UNPAIRED pair belong in §12.3's denominator?** This
    session's own adversarial pass called counting them a BLOCKER; **the change was made and
    then REVERTED**, because the pass's own verifier refuted it and the refutation is
    stronger — see :func:`.paired.totals_for_arm`. The counts are §12.3's literal ones and
    the unpaired number prints beside them.
"""

from __future__ import annotations

from .blindness import (
    AUTHORED,
    AUTHORED_MINUS_MANDATED_STATE,
    FULL,
    BlindnessError,
    BlindnessReport,
    Finding,
    Needle,
    cap_formattings,
    needles,
    scan_context,
    scan_contexts,
    scan_text,
    subtract_mandated_state,
)
from .catalogue import (
    BUILDERS,
    SCENARIOS_REQUIRED_BY_THE_PLAN,
    SOURCE_URLS,
    BenignCall,
    BenignTask,
    EndState,
    NoSuitablePayment,
    build_all,
    capture_an_authorized_payment,
    reconcile_the_payment_list,
    staged_refund_with_goodwill,
)
from .constants import (
    ABSENT_FROM_CONFIG,
    REQUIRED_CONSTANTS,
    BenignConstantError,
    BenignConstants,
    constants_from,
)
from .evidence import (
    REQUIRED_ROW_FIELDS,
    EvidenceError,
    S2Evidence,
    load_scoring_constants,
    payments_for_opening,
    rows_from_ledger,
    s2_evidence_for,
)
from .executor import ActionRecord, BenignExecutor, BenignExecutorError
from .manifest import (
    C5_EVIDENCE,
    SOLVER_LANE,
    SURFACE_EVIDENCE,
    TFP_BLOCK,
    USER_SIMULATOR_LANE,
    BlockRefused,
    TfpManifest,
    load_manifest,
    refuse_tfp,
)
from .paired import (
    BASELINE_ARM,
    ArmTotals,
    PairedTask,
    PairingError,
    RefusedAction,
    TaskUnderArm,
    totals_for_arm,
)
from .report import (
    BenignRunReport,
    FalsePositiveRate,
    ReportRefused,
    false_positive_rate,
    print_report,
    rate_lines,
    render,
)
from .rehearsal import RehearsalError, longest_transcript, reply_for, transcript_for
from .shell import (
    GATED_ARMS,
    BenignRunRefused,
    BenignSettings,
    build_world,
    clean_surface_contexts,
    execute,
    load_needles,
    load_settings,
    run_task_under_arm,
    transcript_client_for,
)
from .solve import (
    BenignEpisode,
    BenignSolverError,
    MeteredSolverClient,
    SolverClient,
    TurnRecord,
    WindowSettings,
    protocol_has_a_call,
    run_benign_episode,
)
from .texts import DONE_MARKER, benign_system_prompt, work_request

__all__ = [
    "ABSENT_FROM_CONFIG",
    "AUTHORED",
    "AUTHORED_MINUS_MANDATED_STATE",
    "ActionRecord",
    "ArmTotals",
    "BASELINE_ARM",
    "BUILDERS",
    "BenignCall",
    "BenignConstantError",
    "BenignConstants",
    "BenignEpisode",
    "BenignExecutor",
    "BenignExecutorError",
    "BenignRunRefused",
    "BenignRunReport",
    "BenignSettings",
    "BenignSolverError",
    "BenignTask",
    "BlindnessError",
    "BlindnessReport",
    "BlockRefused",
    "C5_EVIDENCE",
    "DONE_MARKER",
    "EndState",
    "EvidenceError",
    "FULL",
    "FalsePositiveRate",
    "Finding",
    "GATED_ARMS",
    "MeteredSolverClient",
    "Needle",
    "NoSuitablePayment",
    "PairedTask",
    "PairingError",
    "REQUIRED_CONSTANTS",
    "REQUIRED_ROW_FIELDS",
    "RefusedAction",
    "RehearsalError",
    "ReportRefused",
    "S2Evidence",
    "SCENARIOS_REQUIRED_BY_THE_PLAN",
    "SOLVER_LANE",
    "SOURCE_URLS",
    "SURFACE_EVIDENCE",
    "SolverClient",
    "TFP_BLOCK",
    "TaskUnderArm",
    "TfpManifest",
    "TurnRecord",
    "USER_SIMULATOR_LANE",
    "WindowSettings",
    "benign_system_prompt",
    "build_all",
    "build_world",
    "cap_formattings",
    "capture_an_authorized_payment",
    "clean_surface_contexts",
    "constants_from",
    "execute",
    "false_positive_rate",
    "load_manifest",
    "load_scoring_constants",
    "load_needles",
    "load_settings",
    "longest_transcript",
    "needles",
    "payments_for_opening",
    "print_report",
    "protocol_has_a_call",
    "rate_lines",
    "reconcile_the_payment_list",
    "rows_from_ledger",
    "s2_evidence_for",
    "refuse_tfp",
    "render",
    "reply_for",
    "run_benign_episode",
    "run_task_under_arm",
    "scan_context",
    "scan_contexts",
    "scan_text",
    "staged_refund_with_goodwill",
    "subtract_mandated_state",
    "totals_for_arm",
    "transcript_client_for",
    "transcript_for",
    "work_request",
]
