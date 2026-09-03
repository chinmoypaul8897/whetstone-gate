"""THE THIN OUTER SHELL — **the only I/O in this package.**

`CLAUDE.md` hard rule 8: *"Core logic takes data in and returns results — no I/O, clock,
network, or randomness inside it. **Side effects live in a thin outer shell.**"* This module
is that shell, and it is the only file under `gates/` that opens anything. Every other
module in the package is a pure function of its arguments, which is what lets
:mod:`whetstone_gate.gates.arm4_kernel` be *"a pure function of the folded state"* rather
than a function that mostly is.

**What it reads, and why each is read rather than written down:**

* ``config/protocol.yaml``, through :mod:`whetstone_gate.config` — **the one loader**
  (hard rule 9). Not a second parser: a second loader is a second place a required value
  could acquire a default.
* ``data/policy.txt`` — §8.6a's policy string, *"given verbatim to arms 2 and 2S"*, and the
  source of clause **P7**'s exemption tag. A copy in source would be an unfrozen second
  original deciding whether the probe's door is open (§10.1).
* ``data/arm3_safety.txt`` — §8.6a's safety prompt, verbatim.
* ``data/generic_denial.txt`` — §8.6's one denial message, *"identical across arms, leaking
  no policy"*, which an ``INDETERMINATE`` returns too. `QUESTIONS.md` **Q-046** ruled that
  a denial is identified *"by exact string equality against that one authored constant,
  read from `data/` and never inlined"*, and this is the gate side of the same constant.

⚠️ **`whetstone_gate.attacker.texts` LOADS THREE OF THESE ALREADY AND THIS MODULE DOES NOT
IMPORT IT.** Not an oversight: the attacker package loads the policy *in order to prove the
attacker never sees it*, and a gate that imported the attacker's loader would put the
attacker's module in the gate's import closure — the wrong direction for the one boundary
C6's blindness guard exists to protect. The read is four lines and it is written twice.

⚠️ **NOTHING UNDER `gates/` READS THE FILESYSTEM EXCEPT THIS MODULE, AND NOTHING HERE
DECIDES ANYTHING.** A test asserts both halves.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from whetstone_gate.config import load, repo_root
from whetstone_gate.gates.arm1 import NoGate
from whetstone_gate.gates.arm2 import PolicyGate
from whetstone_gate.gates.arm2s import PolicyAndStateGate
from whetstone_gate.gates.arm3 import SafetyPromptGate
from whetstone_gate.gates.arm4_kernel import Arm4Kernel
from whetstone_gate.gates.base import Gate
from whetstone_gate.gates.constants import REQUIRED_CONSTANTS, GateConstants, constants_from
from whetstone_gate.gates.judge import GateJudgeClient
from whetstone_gate.gates.policy import exemption_tag
from whetstone_gate.gates.verdict import ARM_1, ARM_2, ARM_2S, ARM_3, ARM_4

#: The three `CONTEXT.md` §8.6 / §8.6a texts this package sends or matches on, by their
#: repository-relative paths.
POLICY_PATH = "data/policy.txt"
ARM3_SAFETY_PATH = "data/arm3_safety.txt"
GENERIC_DENIAL_PATH = "data/generic_denial.txt"


class AuthoredTextMissing(RuntimeError):
    """An authored text file is absent. A hard refusal, with no fallback and no default.

    Hard rule 9's shape applied to a **text**. A gate that silently ran with an empty policy
    would be arm 3 wearing arm 2's label, and every escape number in the headline comparison
    would be against the wrong arm.
    """


def _read(rel_path: str) -> str:
    """Read one repository-relative text file as UTF-8. **Bytes, then an explicit decode.**

    Never ``Path.read_text``: universal-newline translation rewrites every line ending on
    this machine, which is `INCIDENTS.md` **INC-16** and **INC-74** exactly. Reading bytes
    means a file that has drifted to CRLF **shows** as CRLF instead of being silently
    normalised into a comparison that then passes.
    """
    # ⚠️ `joinpath`, not the `/` operator: hard rule 7's integer-paise scanner refuses
    # `ast.Div` anywhere under this package, and a path join written with `/` is
    # indistinguishable from a true division to an AST walk. Spelling the join out costs
    # nothing and keeps the scanner strict over every module instead of exempting this one.
    path: Path = repo_root().joinpath(rel_path)
    if not path.is_file():
        raise AuthoredTextMissing(
            f"{path} does not exist. It is a CONTEXT.md S8.6 authored text and it has no "
            f"fallback: a gate cannot enforce a policy it was never given, and S10.1 makes "
            f"a closed probe door arm 4 VOID BY CONSTRUCTION."
        )
    return path.read_bytes().decode("utf-8")


@dataclass(frozen=True)
class GateTexts:
    """The authored texts the five arms need, with the P7 tag already parsed out."""

    policy: str
    arm3_safety: str
    generic_denial: str
    exemption_tag: str


def load_gate_texts() -> GateTexts:
    """Read the three §8.6 texts and parse clause P7's exemption tag out of the policy."""
    policy = _read(POLICY_PATH)
    return GateTexts(
        policy=policy,
        arm3_safety=_read(ARM3_SAFETY_PATH),
        generic_denial=_read(GENERIC_DENIAL_PATH),
        exemption_tag=exemption_tag(policy),
    )


def load_gate_constants() -> GateConstants:
    """Read the two gate constants from `config/` **through the one loader**.

    Each key path comes from :data:`whetstone_gate.gates.constants.REQUIRED_CONSTANTS`, so
    the paths are written down once and the loader's own refusals — missing, blank,
    ``TODO_`` sentinel — are what raise.
    """
    protocol = load("protocol")
    values = {}
    for name, key_path in REQUIRED_CONSTANTS:
        _file, _, dotted = key_path.partition(":")
        values[name] = protocol.require(dotted)
    return constants_from(values)


def build_gate(arm: str, client: GateJudgeClient | None = None) -> Gate:
    """Build the gate for ``arm``, reading everything it needs from `config/` and `data/`.

    ``client`` is required for arms 2, 2S and 3 and **must not** be supplied for arms 1 and
    4 — a control arm or a deterministic kernel handed a model client is an arm whose
    behaviour could depend on one, and hard rule 8 names the arm-4 kernel as one of the four
    deliberate non-uses.
    """
    needs_client = arm in (ARM_2, ARM_2S, ARM_3)
    if needs_client and client is None:
        raise ValueError(f"arm {arm} is a model-backed gate and needs a judge client")
    if not needs_client and client is not None:
        raise ValueError(
            f"arm {arm} takes no model client. CLAUDE.md hard rule 8 names the arm-4 "
            f"kernel as a deliberate non-use, and arm 1 is the no-gate control."
        )
    if arm == ARM_1:
        return NoGate()
    if arm == ARM_4:
        texts = load_gate_texts()
        return Arm4Kernel(load_gate_constants(), texts.exemption_tag)
    texts = load_gate_texts()
    if arm == ARM_2:
        return PolicyGate(client, texts.policy)  # type: ignore[arg-type]
    if arm == ARM_2S:
        return PolicyAndStateGate(client, texts.policy)  # type: ignore[arg-type]
    if arm == ARM_3:
        return SafetyPromptGate(client, texts.arm3_safety)  # type: ignore[arg-type]
    raise ValueError(f"arm {arm!r} is not one of CONTEXT.md S8.6a's five arms")
