"""**THE T-FP BLOCK — its TWENTY selected τ² tasks, and why it cannot run today.**

`CONTEXT.md` §13.4 pre-registers the block: **T-FP** is *"5 configs × 40 of 130
(pre-registered sample)"*, and the sample is *"the **first 40 write-task ids after sorting,
stratified 20 airline / 20 retail**"*. ``config/protocol.yaml`` carries the ids at
``selections.tfp_task_ids``, and this module **reads them** through
:func:`whetstone_gate.tau2.enumerate.committed_tfp_ids` rather than transcribing them.

⚠️ **TWENTY, NOT FORTY — RUNG 4 *WAS* FIRED, 2026-09-04 05:27 UTC, BY THE OPERATOR, ON
SCHEDULE.** `PROCESS.md` §14's rung 4 is *"T-FP 40 → 20 τ² tasks"*; `INCIDENTS.md` **INC-144**
records the cut at the moment it was made and `PROTOCOL.md` §3.2 names the twenty that run and
the twenty that do not. ``config/protocol.yaml``'s ``selections.tfp_task_count`` is now **20**
and its stratification ``{airline: 10, retail: 10}``. The surviving ids are the **same rule at
a smaller K** — the first ten per domain under the same bytewise-ascending string sort — so
each list is an **exact prefix** of its pre-registered twenty: **a reduction, not a
re-registration.**

⚠️ **THIS DOCSTRING PREVIOUSLY SAID, IN CAPITALS, "FORTY, NOT TWENTY. RUNG 4 WAS NOT FIRED."
It was true when written and the cut made it false**, which is why it is corrected here rather
than left to read as a fact about today. `INCIDENTS.md` **INC-146** is this repository's entry
about a false claim standing in an artefact, and the lesson it draws is the reason for this
paragraph: **a number that moves has prose attached to it, and the prose is part of the edit.**

⚠️ **τ²-BENCH ITSELF IS NOT CUT.** It is on `PROCESS.md` §14's never-cut list and
`CONTEXT.md` §21.4 says *"It is never dropped"* — **only the breadth of this one block is
staged**, which §21.4 permits in terms (*"its scope is staged"*). T-NEG keeps all 34
must-not-write tasks and the externally-authored-answer-key claim is **intact**.

:data:`whetstone_gate.runner.n_rule.TFP_REDUCED` is that same reduced figure. The count is read
and then **checked against the stratification**, which is what
:func:`whetstone_gate.tau2.enumerate.tfp_quota` already refuses on.

--------------------------------------------------------------------------------------
⚠️⚠️ THE BLOCK CANNOT RUN, AND THIS IS A HARD-RULE-1 STOP WITH A MEASURED CAUSE — `Q-154`
--------------------------------------------------------------------------------------

`PROCESS.md` §12.1 gives C12's dependencies as **C4, C5, C9, C11**. Three are built.
**C5 is not**, and `STATUS.md` says so in its own row:

    | **C5** | 30 Aug | τ² adapter B — ``HalfDuplexAgent`` + the Gemini 3.5 Flash Lite user
    simulator | `full` | **todo** | — |

C5 is the chunk whose done-when is *"one must-not-write and one write task complete end to
end at the pinned SHA with the user simulator wired; ``db_reward`` is read, not
reimplemented"*. **Measured in this tree, 2026-09-03:**

  * ``src/whetstone_gate/tau2/`` contains exactly two files — ``__init__.py`` and
    ``enumerate.py`` — and ``__init__.py`` says so itself: *"Driving a task end to end with
    the user simulator is **C5's**."*
  * ``grep -rnE "EnvironmentEvaluator|calculate_reward|RewardInfo|get_db_hash" src/``
    matches **nothing**. There is **no first-party call site for ``db_reward``**, and
    `CONTEXT.md` §11.1 makes ``db_reward == 1.0`` the *only* definition of *"solved"* for a
    τ² task.
  * There is no user simulator anywhere in ``src/``, and τ² is **dual-control**: §13.4
    budgets *"one agent call PLUS one user-simulator call"* per turn.

--------------------------------------------------------------------------------------
⚠️ AND A SECOND, DEEPER STOP THAT IS NOT FIXED BY BUILDING C5 — `Q-155`
--------------------------------------------------------------------------------------

The C12 prompt asks for a solver doing *"τ² tasks, through the same six-name tool surface
the attacker uses, against the same world."* **Measured: those two universes are disjoint,
and deliberately so.**

  * §8.6a's surface is six names — ``fetch_payments``, ``fetch_payment``,
    ``capture_payment``, ``create_refund``, ``create_instant_settlement``,
    ``initiate_payment``.
  * τ²'s write tools at the pinned SHA are ``book_reservation``, ``cancel_reservation``,
    ``send_certificate``, ``update_reservation_baggages``, ``update_reservation_flights``,
    ``update_reservation_passengers`` (airline, 6 of 14) and ``cancel_pending_order``,
    ``exchange_delivered_order_items``, ``modify_pending_order_address``,
    ``modify_pending_order_items``, ``modify_pending_order_payment``,
    ``modify_user_address``, ``return_delivered_order_items`` (retail, 7 of 16).
  * ``grep`` for any of the six names across ``src/whetstone_gate/tau2/`` returns **zero**.
  * :class:`whetstone_gate.gates.action.CandidateAction` **raises**
    :class:`~whetstone_gate.gates.action.UnknownTool` for anything outside the six, so
    :class:`~whetstone_gate.gates.base.Gate` — every arm of it, including arm 4's kernel —
    **cannot form a verdict about a τ² action at all**.

⚠️ **A BRIDGE BETWEEN THEM WOULD HAVE TO BE AUTHORED HERE, AND AUTHORING IT IS THE ONE
THING THIS CHUNK MAY NOT DO.** τ²'s value, in §11.1's own authorship table, is that *"the
tasks, the gold behaviour and the grader"* are **Sierra's** — *"the ONLY source of tasks,
gold behaviour and a grader that this project did not author"*. A mapping from
``cancel_pending_order`` onto ``create_refund`` would be **our** claim about what a τ² task
means, and ``db_reward`` — a hash of **τ²'s** database — would stop being a grader of it.
That is grading our own homework, in the block that exists precisely because we do not.

**So this module enumerates the block, refuses to run it, and names both questions.** Hard
rule 1: *"a session that stops on a real ambiguity has succeeded."* The refusal is the
outcome and it is printed as one, never as a skip and never as a zero.

**PURE, except the two readers that go through ``config/``'s one loader.**
"""

from __future__ import annotations

from dataclasses import dataclass

from whetstone_gate import config as cfg
from whetstone_gate.gates.verdict import ARMS
from whetstone_gate.runner.episodes import EpisodeKey
from whetstone_gate.tau2 import enumerate as tau2_enum

#: The pre-registered block name. `CONTEXT.md` §13.4's table and
#: ``whetstone_gate.results.denominator``'s own docstring both spell it this way.
TFP_BLOCK = "T-FP"

#: The lane `config/lanes.yaml` assigns the benign solver, by its ``role`` field:
#: *"benign solver (primary), spilling to Gemma when RPD is exhausted"*.
#:
#: ⚠️ **Named as a STRING here and resolved through :mod:`whetstone_gate.runner.lanes` at
#: use, never assumed reserved or unreserved.** ``flash-lite-3.1`` carries
#: ``reserved_from: null`` today and its declared spill, ``gemma-31b``, is **reserved from
#: 2026-08-31** — so a benign run that spills has to be sanctioned for the reserved lane,
#: and `PROCESS.md` §8 says **no build session may spend on it**.
SOLVER_LANE = "flash-lite-3.1"

#: The lane the τ² **user simulator** would run on, from the same file: *"τ² USER SIMULATOR —
#: τ² is dual-control; every turn is one agent call PLUS one user-simulator call, which
#: DOUBLES τ²'s request count"*. Carried so the refusal below can name what is missing.
USER_SIMULATOR_LANE = "flash-lite-3.5"


class BlockRefused(RuntimeError):
    """A pre-registered block cannot run, and the refusal is the outcome.

    ⚠️ **Not an error to work around.** The shape is
    :class:`whetstone_gate.driver.run.RunRefused`'s, deliberately: a block that quietly ran
    a reduced version of itself would publish a smaller denominator than the one
    ``PROTOCOL.md`` pre-registered, which is the single thing hard rule 11 and Razorpay's own
    B.9 both forbid.
    """


@dataclass(frozen=True)
class TfpManifest:
    """The T-FP block as ``config/`` pre-registers it. **Read, never transcribed.**"""

    task_ids_by_domain: dict[str, tuple[str, ...]]
    quota_by_domain: dict[str, int]
    declared_count: int

    @property
    def task_count(self) -> int:
        return sum(len(ids) for ids in self.task_ids_by_domain.values())

    @property
    def configurations(self) -> tuple[str, ...]:
        """§12.3's five configurations: gate OFF plus the four gated arms.

        Taken from :data:`whetstone_gate.gates.verdict.ARMS` so the matrix cannot drift
        from the arms that exist. §12.3: *"five configurations, one of which is the
        baseline. This is a second run mode, **not a sixth arm**; the arm count stays five."*
        """
        return ARMS

    @property
    def episode_count(self) -> int:
        """§13.4's figure for this block, **computed, never written down**: ``5 configs ×
        task_count``. At §13.4's pre-registered 40 that was **200**; after rung 4's cut to
        20 it is **100**. It moves with ``config/`` because it is derived from it."""
        return len(self.configurations) * self.task_count

    def keys(self) -> tuple[EpisodeKey, ...]:
        """Every episode of the block, as C11's ``(block, arm, seed_or_task, model)`` key.

        ⚠️ **THE TASK ID IS QUALIFIED BY ITS DOMAIN, AND IT HAS TO BE.** At §13.4's
        pre-registered **forty**, ``"11"``, ``"13"``, ``"14"`` and ``"15"`` each appeared in
        **both** the airline and the retail list, so a flat set of ids lost information and
        two different episodes collided on one checkpoint path — which
        :class:`~whetstone_gate.runner.episodes.EpisodeKey`'s own ``__post_init__`` calls
        *"a silently lost episode"*. The separator is ``-`` because the key refuses ``/``,
        ``\\`` and ``..``.

        ⚠️ **AFTER RUNG 4 THE SURVIVING TWENTY NO LONGER COLLIDE, AND THAT IS SAID HERE
        RATHER THAN LEFT TO IMPLY THE GUARD IS STILL EARNING ITS KEEP ON THIS SAMPLE.**
        The reduced lists are airline ``11..21`` and retail ``0``, ``1``, ``100..107``, which
        are **disjoint**, so on today's selection a flat id would happen not to collide. The
        qualification is kept because it is **correct**, because the forty remain
        pre-registered and the block may be restored, and because T-NEG's must-not-write
        lists **do** still overlap across domains (on id ``"10"``). **A guard that is right
        for a reason that has lapsed is still right; describing it as still demonstrated
        would not be.**
        """
        built: list[EpisodeKey] = []
        for arm in self.configurations:
            for domain in sorted(self.task_ids_by_domain):
                for task_id in self.task_ids_by_domain[domain]:
                    built.append(
                        EpisodeKey(
                            block=TFP_BLOCK,
                            arm=arm,
                            seed_or_task=f"{domain}-{task_id}",
                            attacker_model=SOLVER_LANE,
                        )
                    )
        return tuple(built)

    def lines(self) -> list[str]:
        out = [
            f"T-FP BLOCK — read from config/, not transcribed",
            f"  selections.tfp_task_count (config/)             : {self.declared_count}",
            f"  ids actually read                               : {self.task_count}",
        ]
        for domain in sorted(self.task_ids_by_domain):
            ids = self.task_ids_by_domain[domain]
            out.append(
                f"    {domain:<10} quota {self.quota_by_domain[domain]:>3}  read "
                f"{len(ids):>3}  first {ids[0]!r} last {ids[-1]!r}"
            )
        out.append(f"  configurations (S12.3's matrix)                 : "
                   f"{len(self.configurations)} — {', '.join(self.configurations)}")
        out.append(f"  episodes the block pre-registers               : {self.episode_count}")
        out.append(
            "  ⚠️ RUNG 4 (T-FP 40 -> 20) WAS FIRED 2026-09-04 05:27 UTC by the OPERATOR, on "
            "SCHEDULE — PROCESS.md S14; INCIDENTS.md INC-144; PROTOCOL.md S3.2 names the "
            "twenty that RUN and the twenty that DO NOT"
        )
        out.append(
            "     NOT fired by CONTEXT.md S13.4's decision rule — that rule reads the pilot's "
            "measured tokens/episode, and INC-142 records the pilot completed 0 of 20"
        )
        out.append(
            "     tau2-bench itself is NOT cut (never-cut list); only THIS BLOCK'S BREADTH is "
            "staged. T-NEG keeps all 34 must-not-write tasks"
        )
        return out


def load_manifest() -> TfpManifest:
    """Read the block's pre-registered selection, and refuse a selection that disagrees.

    ⚠️ **THE CROSS-CHECK IS THIS FUNCTION'S AND NOT THE ENUMERATOR'S.**
    :func:`whetstone_gate.tau2.enumerate.report` prints ``MATCH`` or ``DIFFERS`` and
    **returns 0 either way** — drift is not a refusal there. `CONTEXT.md` §13.4 pins the
    count *and* the stratification, so a manifest whose two halves disagree would run a
    block that is not the one ``PROTOCOL.md`` registered, and that has to raise here.
    """
    ids = tau2_enum.committed_tfp_ids()
    # ⚠️ `tfp_quota` ALREADY refuses a stratification that does not sum to
    # `selections.tfp_task_count`, and that check is not repeated here. The count is read
    # again, separately and through the same one loader, for a different purpose: the report
    # prints **config/'s own number** beside the ids it actually read, so a reader sees the
    # count asserted and the same count read, rather than a count read that must be trusted
    # to have been the target.
    stratified = tau2_enum.tfp_quota()
    declared = int(cfg.load("protocol").require("selections.tfp_task_count"))

    if set(ids) != set(stratified):
        raise BlockRefused(
            f"config/ names T-FP domains {sorted(stratified)} in the stratification and "
            f"{sorted(ids)} in the id lists. A domain in one and not the other is a block "
            f"whose size depends on which key you read"
        )
    for domain, expected in stratified.items():
        if len(ids[domain]) != expected:
            raise BlockRefused(
                f"config/ says T-FP takes {expected} {domain} task(s) and "
                f"selections.tfp_task_ids.{domain} lists {len(ids[domain])}. CONTEXT.md "
                f"S13.4 pre-registers both; a mismatch means the block would run a sample "
                f"nobody registered. Hard rule 11: this is a refusal, not a truncation"
            )
    manifest = TfpManifest(
        task_ids_by_domain={domain: tuple(values) for domain, values in ids.items()},
        quota_by_domain=stratified,
        declared_count=declared,
    )
    if manifest.task_count != declared:
        raise BlockRefused(
            f"config/ declares selections.tfp_task_count = {declared} and the id lists "
            f"hold {manifest.task_count}"
        )
    return manifest


#: The evidence, as facts a reviewer can re-measure, for the refusal below. Each is a
#: command whose output was read in this tree on 2026-09-03.
C5_EVIDENCE: tuple[str, ...] = (
    "STATUS.md's C5 row reads `todo` — tau2 adapter B, the HalfDuplexAgent and the user "
    "simulator, is NOT BUILT",
    "src/whetstone_gate/tau2/ holds exactly __init__.py and enumerate.py, and __init__.py "
    "says 'Driving a task end to end with the user simulator is C5's'",
    "grep -rn 'calculate_reward|RewardInfo|get_db_hash|EnvironmentEvaluator' src/ matches "
    "NOTHING — there is no first-party db_reward call site, and CONTEXT.md S11.1 makes "
    "db_reward == 1.0 the only definition of 'solved' for a tau2 task",
    "tau2 is DUAL-CONTROL (S13.4: 'one agent call PLUS one user-simulator call'), and no "
    f"user simulator exists in src/; lane {USER_SIMULATOR_LANE!r} is assigned one and "
    "nothing drives it",
)

#: The evidence for the second, deeper stop — the one building C5 would not close.
SURFACE_EVIDENCE: tuple[str, ...] = (
    "S8.6a's surface is six names; tau2's write tools are book_reservation, "
    "cancel_pending_order, modify_pending_order_items and ten more. The two sets are "
    "DISJOINT and grep confirms zero overlap",
    "gates.action.CandidateAction raises UnknownTool outside the six names, so NO ARM — "
    "including arm 4's kernel — can form a verdict about a tau2 action",
    "S11.1's authorship table gives the tau2 tasks, the gold behaviour and the grader as "
    "SIERRA's. A tool mapping authored here would make db_reward a grader of OUR claim "
    "about what a tau2 task means, which is grading our own homework in the one block "
    "that exists because we do not",
)


def refuse_tfp(manifest: TfpManifest) -> BlockRefused:
    """Build the refusal, with the manifest it refuses to run **and both questions named**.

    Returned rather than raised so a caller can print it beside the manifest — the block's
    selected ids are a real, checkable deliverable, and the refusal is a fact about the *run*,
    not about the enumeration. `PROCESS.md` §9: *"zero-occurrence branches are printed as
    zeros, never omitted. A reader must distinguish 'did not happen' from 'was not
    checked.'"* This block **was checked** and **did not happen**.
    """
    lines = [
        f"the {TFP_BLOCK} block enumerates {manifest.episode_count} episodes over "
        f"{manifest.task_count} pre-registered tau2 tasks and NONE OF THEM CAN RUN",
        "",
        "Q-154 — C12's dependency C5 is UNBUILT, so no tau2 task can be driven at all:",
    ]
    lines.extend(f"  - {fact}" for fact in C5_EVIDENCE)
    lines.extend(
        [
            "",
            "Q-155 — and building C5 would NOT close it, because the two tool surfaces are "
            "disjoint:",
        ]
    )
    lines.extend(f"  - {fact}" for fact in SURFACE_EVIDENCE)
    lines.extend(
        [
            "",
            "This is a hard-rule-1 STOP and the refusal is the outcome. The SELECTED ids "
            "ARE read and printed above, so the block's denominator is visible and a later "
            "session does not have to re-derive it. The denominator printed is the "
            "POST-RUNG-4 one; PROTOCOL.md S3.2 carries the pre-registered forty and names "
            "the twenty that were cut, because a cut item is never silently lost.",
        ]
    )
    return BlockRefused("\n".join(lines))
