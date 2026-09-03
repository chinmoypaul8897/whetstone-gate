"""ARM 2 — the policy text in the prompt, and **no ledger state**.

`CONTEXT.md` §8.6a: the policy string is *"given verbatim to arms 2 and 2S"*, and
*"Arm 2 receives the policy but **not** this object"* — the folded ledger state — and
*"that single difference is the pre-registered headline comparison (§12.4)."*

⚠️ **THE POLICY IS READ FROM `data/policy.txt`, NEVER TRANSCRIBED.** This module holds no
clause text at all; the bytes arrive from :mod:`whetstone_gate.gates.shell`. A copy in
source is the same defect as a hardcoded number, and a drifted copy would silently change
what this arm was shown while every test still passed — and clause **P7** is in that
string, so a drifted copy closes the probe's door.
"""

from __future__ import annotations

from whetstone_gate.gates.judge import ModelGate
from whetstone_gate.gates.verdict import ARM_2


class PolicyGate(ModelGate):
    """Arm 2. Policy in, one bit out, no episode state."""

    arm = ARM_2
