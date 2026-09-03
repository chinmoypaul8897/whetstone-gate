"""ARM 3 — a safety system prompt, and **no policy at all**.

`CONTEXT.md` §8.6a gives the text verbatim in `data/arm3_safety.txt` and describes it as
the prompt *"which names no cap, no clause and no attack"*. §8.6a's policy paragraph says
the same thing from the other side: the policy string is given to arms 2 and 2S, and
*"arm 1 and arm 3 never see it."*

⚠️ **THAT IS THE ARM'S WHOLE CONTENT AND IT IS TESTED, NOT ASSERTED.**
`tests/test_c9_gates.py` parses `data/policy.txt`'s seven clauses and asserts that **not
one** of them appears anywhere in this arm's assembled messages — including **P7**. Arm 3
still leaves the probe's door open, and it does so the only way an arm with no policy can:
**nothing in it closes the door**, because nothing in it knows there is one.
"""

from __future__ import annotations

from whetstone_gate.gates.judge import ModelGate
from whetstone_gate.gates.verdict import ARM_3


class SafetyPromptGate(ModelGate):
    """Arm 3. The §8.6a safety prompt, the shared action rendering, no policy, no state."""

    arm = ARM_3
