"""ARM 2S — arm 2 **plus the folded ledger state**, and nothing else.

`CONTEXT.md` §8.6a: *"Arm 2S's 'folded ledger state' is this exact JSON, recomputed from the
ledger before every gate call and appended to arm 2S's prompt … Arm 2 receives the policy
but **not** this object — that single difference is the pre-registered headline comparison
(§12.4)."*

⚠️ **THE DIFFERENCE IS AN APPEND, SO IT IS EXACTLY MEASURABLE.** This class overrides one
method — :meth:`sends_folded_state` — and changes nothing else: same client protocol, same
preamble bytes, same renderer, same parser. `PROCESS.md` §12.1's C9 done-when reads *"arms
2 and 2S differ in exactly one input — the folded state"*, and `tests/test_c9_gates.py`
reconstructs arm 2's user message from arm 2S's by removing exactly
:data:`whetstone_gate.gates.judge.FOLDED_STATE_BLOCK_PREFIX` and the JSON after it,
asserting the remainder is byte-identical. **A claim about "one input" that is checked by
reading the code is not a measurement.**
"""

from __future__ import annotations

from whetstone_gate.gates.judge import ModelGate
from whetstone_gate.gates.verdict import ARM_2S


class PolicyAndStateGate(ModelGate):
    """Arm 2S. Arm 2's inputs, plus §8.6a's six-key folded-state object."""

    arm = ARM_2S

    def sends_folded_state(self) -> bool:
        return True
