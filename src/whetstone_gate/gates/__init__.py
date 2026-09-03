"""`gates/` — the five arms of `CONTEXT.md` §8.6a, behind one interface.

## ⚠️ THE MOAT. READ THIS BEFORE ADDING AN IMPORT.

`CLAUDE.md` hard rule 8, verbatim:

    ⚠️ **THE GATE AND THE SCORER SHARE NO CODE, AND A TEST MUST ASSERT THAT.**
    `scorer/` imports nothing from `gates/`; `gates/` imports nothing from `scorer/`;
    neither imports a shared predicate helper. **Any logic they both need is written
    twice, on purpose** — once against the live call, once against the replayed ledger.
    … **Adding to that allow-list is a Class A deviation** requiring an architect ruling
    in `QUESTIONS.md`.
    *Why this one line is the whole moat:* in the spike, `gate.js` and `invariants.js`
    both called `world.js:intentKey`, so the invariant **could not have fired unless the
    gate had a bug**. **That is not a result; it is a definition.**

**Three prohibitions bind every file under this package:**

1. **Nothing here imports `whetstone_gate.scorer`, on any path, ever.** `check_roles`
   **D1**, **D2** and **D3** walk both packages' transitive first-party closures and fail
   on any shared module outside ``MOAT_ALLOW_LIST``, **which is empty and stays empty**.
2. **Nothing here imports `whetstone_gate.ledger` either.** `QUESTIONS.md` **Q-069**,
   RULED 2026-09-01: *"`whetstone_gate.ledger` IS SCORER-SIDE. `gates/` imports nothing
   from it, on any path, ever; `scorer/` may."* The runner may import both, because the
   runner is in neither closure.
3. **Nothing here reaches a module by name at run time.** `INCIDENTS.md` **INC-51**
   measured a `gates/` module executing a `scorer/` predicate while **D1, D2 and D3 all
   printed PASS** — an import expressed as a call produces no AST import node, so the walk
   was *complete over the wrong set*. `check_roles` **D4** now refuses the whole vocabulary
   of run-time module reach in this package's **raw source text**, and removing a name from
   ``MOAT_REFUSED_DYNAMIC`` is a Class A deviation. **Write every import statically.**

⚠️ **AND THE STRONGEST FORM IS THE ONE ACTUALLY TAKEN:** the only first-party module
outside this package that appears anywhere in its closure is `whetstone_gate.config`, the
one config loader, reached from :mod:`whetstone_gate.gates.shell` alone.
`whetstone_gate.scorer`'s closure is **exactly its own six modules** — it declined `Q-069`'s
permission — so **D3's intersection is empty by construction on both sides**, and neither
package can drag the other in by a later edit without a review seeing it.

## THE FIVE ARMS

| arm | module | what it gets | verdicts it may emit |
|---|---|---|---|
| **1** | :mod:`~whetstone_gate.gates.arm1` | nothing — no gate | ``ALLOWED`` |
| **2** | :mod:`~whetstone_gate.gates.arm2` | the policy text | ``ALLOWED`` / ``DENIED`` |
| **2S** | :mod:`~whetstone_gate.gates.arm2s` | the policy **and** the folded state | ``ALLOWED`` / ``DENIED`` |
| **3** | :mod:`~whetstone_gate.gates.arm3` | a safety prompt, no policy | ``ALLOWED`` / ``DENIED`` |
| **4** | :mod:`~whetstone_gate.gates.arm4_kernel` | the folded state, in code | ``ALLOWED`` / ``DENIED`` / ``INDETERMINATE`` |

Every verdict outside its arm's set is **refused at construction**
(:class:`~whetstone_gate.gates.verdict.Verdict`), and every ``DENIED`` and every
``INDETERMINATE`` returns §8.6's one generic denial string to the attacker, byte for byte.
"""

from __future__ import annotations

from whetstone_gate.gates.action import (
    CandidateAction,
    KNOWN_TOOLS,
    MONEY_TOOLS,
    READ_TOOLS,
    STUB_TOOLS,
    UnknownTool,
)
from whetstone_gate.gates.arm1 import NoGate
from whetstone_gate.gates.arm2 import PolicyGate
from whetstone_gate.gates.arm2s import PolicyAndStateGate
from whetstone_gate.gates.arm3 import SafetyPromptGate
from whetstone_gate.gates.arm4_kernel import (
    Arm4Kernel,
    CLAUSES,
    DEFAULT_CLAUSE_ORDER,
    first_finding,
    kernel_verdict,
)
from whetstone_gate.gates.base import Gate
from whetstone_gate.gates.constants import GateConfigError, GateConstants, constants_from
from whetstone_gate.gates.judge import (
    GateJudgeClient,
    JudgeMessages,
    ModelGate,
    parse_reply,
    render_action,
)
from whetstone_gate.gates.policy import PolicyTextMalformed, exemption_tag, is_exempt
from whetstone_gate.gates.shell import (
    GateTexts,
    build_gate,
    load_gate_constants,
    load_gate_texts,
)
from whetstone_gate.gates.state import Authorization, FoldedState, arm2s_state_object, fold
from whetstone_gate.gates.verdict import (
    ARM_1,
    ARM_2,
    ARM_2S,
    ARM_3,
    ARM_4,
    ARM_VERDICT_SETS,
    ARMS,
    MalformedVerdict,
    Outcome,
    UnknownArm,
    Verdict,
    VerdictOutsideArmSet,
    allowed,
    denied,
    indeterminate,
)

__all__ = [
    "ARM_1",
    "ARM_2",
    "ARM_2S",
    "ARM_3",
    "ARM_4",
    "ARMS",
    "ARM_VERDICT_SETS",
    "Arm4Kernel",
    "Authorization",
    "CLAUSES",
    "CandidateAction",
    "DEFAULT_CLAUSE_ORDER",
    "FoldedState",
    "Gate",
    "GateConfigError",
    "GateConstants",
    "GateJudgeClient",
    "GateTexts",
    "JudgeMessages",
    "KNOWN_TOOLS",
    "MONEY_TOOLS",
    "MalformedVerdict",
    "ModelGate",
    "NoGate",
    "Outcome",
    "PolicyAndStateGate",
    "PolicyGate",
    "PolicyTextMalformed",
    "READ_TOOLS",
    "STUB_TOOLS",
    "SafetyPromptGate",
    "UnknownArm",
    "UnknownTool",
    "Verdict",
    "VerdictOutsideArmSet",
    "allowed",
    "arm2s_state_object",
    "build_gate",
    "constants_from",
    "denied",
    "exemption_tag",
    "first_finding",
    "fold",
    "indeterminate",
    "is_exempt",
    "kernel_verdict",
    "load_gate_constants",
    "load_gate_texts",
    "parse_reply",
    "render_action",
]
