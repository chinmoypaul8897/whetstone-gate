"""The ONE interface all five arms sit behind.

`PROCESS.md` §12.1's C9 card: *"arms 1, 2, 2S, 3, 4 as **five separate modules behind one
interface**"*. This is the interface. It is deliberately one method wide:

    ``decide(action, state) -> Verdict``

so that the runner's call site is **identical for every arm** and no arm can be handed a
different question from the others. §10.1's requirement is *"no DIFFERENTIAL information
across arms"*, and a per-arm signature would be a differential in the shape of an API.

⚠️ **THE ARM IS A FIELD OF THE GATE AND OF THE VERDICT, AND IT IS NOT DECORATION.**
:class:`whetstone_gate.gates.verdict.Verdict` refuses at construction any outcome outside
its arm's `CONTEXT.md` §8.6a set, so a gate that carries ``arm = "1"`` is a gate whose type
cannot produce a ``DENIED`` — not a gate whose ``if`` happened not to fire.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from whetstone_gate.gates.action import CandidateAction
from whetstone_gate.gates.state import FoldedState
from whetstone_gate.gates.verdict import ARM_VERDICT_SETS, UnknownArm, Verdict


class Gate(ABC):
    """One arm's gate. Subclasses set :attr:`arm` and implement :meth:`decide`."""

    #: The `CONTEXT.md` §8.6a arm identifier this gate speaks for.
    arm: str = ""

    def __init__(self) -> None:
        if self.arm not in ARM_VERDICT_SETS:
            raise UnknownArm(
                f"{type(self).__name__}.arm is {self.arm!r}, which is not one of "
                f"CONTEXT.md S8.6a's five arms. Every gate declares its arm, because the "
                f"arm is what fixes the verdict set the type will permit."
            )

    @abstractmethod
    def decide(self, action: CandidateAction, state: FoldedState) -> Verdict:
        """Return the verdict for ``action`` given ``state``. Never raises on a normal path."""
