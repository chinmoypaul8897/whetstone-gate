"""C13 — the CaMeL comparator: vendor it, prove it unmodified, wire it, decide nothing.

WHAT THIS PACKAGE IS, AND THE ONE SENTENCE THAT BOUNDS IT
=========================================================
`CONTEXT.md` §8.5 demotes CaMeL from *"arm 5"* to a **scoped comparator**, and the whole
resolution is four words: **run CaMeL unmodified, on its home turf.** So this package

  * **reads** the vendored CaMeL checkout at the pinned commit and reports what is in it;
  * **proves** that checkout is unmodified, by regenerating the empty diff rather than
    storing a screenshot of one;
  * **builds** the RUN-1 invocation and **stops at the point of invocation**;
  * **decides nothing.**

⚠️ **IT MAKES NO PROVIDER CALL, AND IT NEVER WILL.** `PROCESS.md` §1: long runs execute in
the operator's terminal, never inside a session that might close. RUN-1 is an **operator
run**, timeboxed to 90 minutes. This package hands the operator an argv and gets out of the
way. It does not import CaMeL, it does not import a model client, and
``test_the_comparator_imports_no_model_client`` asserts it.

⚠️ **IT DOES NOT DECIDE THE BRANCH.** `config/lanes.yaml`'s ``camel_comparator.branch`` is
``TODO_C13_RUN1`` and ``make selftest`` is **RED on it, correctly**. A build session that
turned that green would have decided, from a chair, a question the spec reserves for a
timeboxed run. :func:`branch_is_undecided` reports the state; nothing here writes it.

WHY EVERY CLAIM IS RE-DERIVED AND NOTHING IS TRANSCRIBED
=========================================================
Almost every sentence C13 ships is a statement about somebody else's code, and **five false
claims about third-party behaviour have already reached this specification** — the
``create_refund`` ``destination`` parameter (`INCIDENTS.md` **INC-02**), the 59% figure, the
*"29 ms"* Vulcan number (**INC-05**, the entry that made URL-and-date a rule), ``receipt``
*"is not a key"*, and AgentHarm's single copyright holder.

So this package takes its two sides from two places and **transcribes neither**:

  * one side is **parsed out of `CONTEXT.md` §8.5, §8.5.1 and §8.5.2** — the law, written
    before this chunk existed;
  * the other is **derived from the vendored checkout** with :mod:`ast`, at the pin.

A line number written into this source by hand would be a third copy that can drift from
both. Every parser asserts it matched, because *a parser that silently reads nothing is the
same class of defect as the check it replaces* — `QUESTIONS.md` **Q-020**'s build note.

THE GOLDEN, AND WHY THERE ISN'T ONE
====================================
C13 is a `full` chunk with **no golden**, and that is a ruling, not an omission:
`PROCESS.md` §5.2's enumerated nine assign none to C13, whose done-when is **a decision and
a proof** rather than a computed value. This is `QUESTIONS.md` **Q-016**'s reasoning (C1's
golden is Razorpay's own documentation), **Q-020**'s (C3's golden is τ²-bench at the pinned
SHA) and **Q-031**'s (C6's done-when is structural) applied to C13. Recorded as **Q-056**.

**ENFORCEMENT in place of a golden:** C13's REVIEW re-verifies every third-party claim
below **independently, at the pin, first-hand**. The tests here make that re-verification
cheap rather than replacing it.

WHAT THIS PACKAGE FOUND, STATED HERE BECAUSE IT OUTRANKS FINISHING THE CHUNK
=============================================================================
Two divergences between `CONTEXT.md` and the sources, both raised in `QUESTIONS.md`:

  * **Q-057 (Class A) — the `+camel+secpol` run is a TWO-PASS protocol.** §8.5.1 says
    *"Invoke as `google:gemini-2.0-flash-lite-001+camel+secpol`"*. That string is a
    **pipeline name CaMeL emits** (``models.py:188``), not a ``--model`` argument; the real
    invocation is two passes, the second carrying ``--replay-with-policies``, which replays
    the first's stored logs through the policy engine. See :mod:`.invocation`.
  * **Q-058 (Class A) — the *"Tables 5–7"* citation names the wrong table.** The
    ``81.2 ± 19.1`` / ``62.5 ± 23.7`` banking pair and the 77-vs-84 Overall are **Table 2,
    Appendix B, `o3 High`**. Tables 5–7 are Appendix C, **Claude 3.5 Sonnet**, where
    CaMeL's banking is *behind* the undefended model. Branch B ships as a citation, so the
    citation is the artefact. See :mod:`.branch_b`.

Neither is corrected here — `CONTEXT.md` is outside this chunk's fence and hard rule 2
makes a Class A change the architect's. Both are **recorded, and the artefacts are built so
the correction is one edit rather than a rewrite.**
"""

from __future__ import annotations

from .branch_b import BranchBArtefact, render_branch_b
from .claims import (
    CLAIM_IDS,
    ClaimVerdict,
    spec_line_references,
    verify_all_claims,
)
from .invocation import (
    Invocation,
    Run1Plan,
    branch_conditions_are_stale,
    branch_is_undecided,
    run1_plan,
)
from .predictions import Prediction, parse_predictions
from .vendor import (
    UnmodifiedProof,
    agentdojo_root,
    assert_vendor_at_pin,
    pinned_sha,
    render_unmodified_proof,
    unmodified_proof,
    vendor_root,
)

__all__ = [
    "BranchBArtefact",
    "CLAIM_IDS",
    "ClaimVerdict",
    "Invocation",
    "Prediction",
    "Run1Plan",
    "UnmodifiedProof",
    "agentdojo_root",
    "assert_vendor_at_pin",
    "branch_conditions_are_stale",
    "branch_is_undecided",
    "parse_predictions",
    "pinned_sha",
    "render_branch_b",
    "render_unmodified_proof",
    "run1_plan",
    "spec_line_references",
    "unmodified_proof",
    "vendor_root",
    "verify_all_claims",
]
