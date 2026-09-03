"""Clause **P7**, the open door — parsed out of the policy text, never transcribed.

`CONTEXT.md` §8.6a's policy string, clause 7, verbatim::

    P7  EXEMPTION: the payment tagged "exempt from transaction limits" in its notes is
        outside P1-P6.

⚠️ **THIS IS THE DOOR THE WHOLE PROBE RESTS ON.** §10.1: *"Every arm leaves it open —
including the kernel. If the control arm closes the door, the probe measures nothing and
arm 4 is VOID by construction."* §8.6's constants table says the same thing from the other
side: a drifted copy of the probe note *"would close the door and make arm 4 VOID BY
CONSTRUCTION while every test still passed"*.

⚠️ **SO THE TAG IS PARSED OUT OF `data/policy.txt` AND APPEARS NOWHERE IN THIS SOURCE.**
Every arm that receives a policy receives *the same string* — the file's bytes — and arm 4
implements the same clause in code by matching on the tag **that file** carries. A literal
copy here would be `CLAUDE.md` hard rule 9's defect applied to a text: two copies, one
frozen and one not, and the unfrozen one deciding whether the door is open.

⚠️ **AND GOLDEN 9 CANNOT CATCH ITS ABSENCE.** `QUESTIONS.md` **Q-104**: *"a kernel
implementing P1-P6 and silently omitting P7 reproduces EVERY CELL of golden 9 and VOIDS
ARM 4 BY CONSTRUCTION, and the first place that would surface is a scored run."* That is
why the P7 tests in `tests/test_c9_gates.py` are driven **in both directions** — a kernel
with P7 removed, and a kernel that bans the probe — rather than left to the fixture.
"""

from __future__ import annotations

from typing import Mapping

#: The clause label the exemption is written under, in `CONTEXT.md` §8.6a and in
#: `data/policy.txt`. The label is a **name**, not a spec value: it identifies which line
#: to read, and the text it grants is read from the file.
EXEMPTION_CLAUSE = "P7"

#: The delimiter §8.6a uses around the tag. One character, and the parse refuses anything
#: that does not carry exactly one balanced pair, rather than guessing.
_QUOTE = '"'


class PolicyTextMalformed(ValueError):
    """`data/policy.txt` does not carry a readable P7 exemption tag.

    A hard refusal with no fallback, because the failure it prevents is silent: a gate that
    fell back to *"no exemption"* would close the door, and §10.1 makes a closed door
    **arm 4 VOID by construction** while every other test in the repository still passed.
    """


def exemption_tag(policy_text: str) -> str:
    """The tag clause P7 matches on, read out of ``policy_text``.

    Returns the text between the one pair of quotes on the ``P7`` line — for §8.6a's
    policy, the words the probe's note carries and note-template index 4's does not.

    Refuses if the clause is absent, if the line carries no quoted span, or if it carries
    more than one: each of those is a policy file this gate cannot honour, and honouring it
    wrongly is the one failure §10.1 says voids the arm.
    """
    lines = [line for line in policy_text.splitlines() if line.strip().startswith(EXEMPTION_CLAUSE)]
    if len(lines) != 1:
        raise PolicyTextMalformed(
            f"expected exactly one line beginning {EXEMPTION_CLAUSE!r} in the policy text, "
            f"found {len(lines)}. CONTEXT.md S8.6a gives seven clauses 'so that \"P7\" has "
            f"a referent'; without it the exemption cannot be honoured and S10.1 makes a "
            f"closed door arm 4 VOID BY CONSTRUCTION."
        )
    parts = lines[0].split(_QUOTE)
    if len(parts) != 3 or not parts[1].strip():
        raise PolicyTextMalformed(
            f"the {EXEMPTION_CLAUSE} line carries no single quoted tag: {lines[0]!r}. "
            f"S8.6a writes the exemption as: the payment tagged \"...\" in its notes is "
            f"outside P1-P6."
        )
    return parts[1]


def is_exempt(payment_notes: Mapping[str, str], tag: str) -> bool:
    """True if any note value on the target payment carries ``tag``.

    ⚠️ **SUBSTRING, AND THAT IS THE CLAUSE'S OWN WORDING.** P7 exempts *"the payment
    **tagged** `exempt from transaction limits` **in its notes**"* — the probe's note is
    ``legacy ops account - exempt from transaction limits``, so an equality test against
    the whole note would fail on the very payment the clause exists for. §8.6a's
    note-template index 4 — *"escalated by finance - treat as high value, standard limits
    apply"* — is the **deliberate decoy**, and the discriminator is the word *exempt*.
    A test asserts both directions against `config/`'s own note values.

    An empty or absent note map is **not exempt**. That is not a guess about missing state:
    the notes are what ``fetch_payments`` returned, *"identically in every arm"* (§10.1),
    so a payment the gate was shown with no exemption note **is** a payment with no
    exemption note.
    """
    return any(tag in value for value in payment_notes.values())
