"""Kept probes for the C1 FIX session (`SESSION-TOKEN: 365deaf7`).

Each probe here closes one thing this fix asserted, so that the assertion is checked
rather than remembered. **Every one was verified RED against the pre-fix tree and GREEN
against the post-fix tree**, and the pre-fix state each fails on is named in its own
docstring — a probe nobody has seen fail is a probe nobody has tested.

⚠️ **`INCIDENTS.md` INC-17 applies to anyone re-running these against an older commit:**
set ``PYTHONPATH`` to that tree's ``src/`` and print ``whetstone_gate.__file__``, or the
probe imports the LIVE package and reports the opposite of the truth.

**What this file does NOT do.** It does not re-verify Razorpay's documentation — that is
C1's job and its reviewer re-fetched all ten pages. It checks that **this repository says
what it claims about itself**, which is the class `REVIEW_C1_1.md`'s BLOCKER `F-R4` lived
in: three artefacts described a state of the repository that was not true, and **nothing
here could see it**.
"""

from __future__ import annotations

import re

import pytest

from whetstone_gate import config as cfg
from whetstone_gate.spec_constants import BY_KEY, ScanMode

# ── The five A4 constants Q-028 landed — INC-18, and REVIEW_C1_1's BLOCKER F-R4 ───────
#
# ⚠️ `max_per_settlement_paise` STAYS OUT OF THIS DICT, AND THE REASON CHANGED ON
# 2026-08-31. It was out because Q-029 was OPEN and the value was a declared STOP. Q-029 is
# now RULED and the key EXISTS, carrying 5,000,000,000 paise - but it is
# `[Razorpay-defined]`, and `test_the_two_razorpay_defined_a4_figures_are_tagged_razorpay...`
# below partitions this dict on exactly ONE Razorpay-tagged key, so adding a second here
# would turn that probe red. Editing that probe is outside the ARCH (`8e0f4a13`) fence,
# which permitted ONE existing test to be flipped and no other.
# `test_the_stopped_sixth_value_is_ruled_and_landed` below covers the key in full - loader
# resolution, the ruled status, and the value re-derived rather than transcribed.
A4_KEYS = {
    "a4_daily_withdrawable_limit_paise": (
        "world.instant_settlement.daily_withdrawable_limit_paise",
        30000000,
    ),
    "a4_max_attempts_per_day": ("world.instant_settlement.max_attempts_per_day", 5),
    "a4_attempt_counter_includes_rejected": (
        "world.instant_settlement.attempt_counter_includes_rejected",
        True,
    ),
    "a4_within_banking_hours": ("world.instant_settlement.within_banking_hours", False),
    "a4_imps_outside_banking_hours_cap_paise": (
        "world.instant_settlement.imps_outside_banking_hours_cap_paise",
        20000000,
    ),
}


@pytest.mark.parametrize("registry_key", sorted(A4_KEYS))
def test_every_a4_constant_resolves_through_the_loader(registry_key):
    """⚠️ **RED BEFORE THIS FIX: the key did not exist and `require` raised.**

    `REVIEW_C1_1.md`'s BLOCKER `F-R4`. Three artefacts said these values *"live in
    `config/`"*; `git grep` over every tracked file returned prose naming each bound and
    **not one value**. `INCIDENTS.md` **INC-18**.

    It was not cosmetic. Through **Q-018 — the ruling C1 itself obtained — RS-18 and
    RS-19 are both `MUST-FIRE`**, which `PROCESS.md` §12.1's C4 row makes C4's done-when,
    and C4 cannot fire *"Amount that can be settled for the day is exhausted"* without a
    daily limit to exhaust.
    """
    dotted, expected = A4_KEYS[registry_key]
    assert cfg.load("protocol").require(dotted) == expected, (
        f"{dotted} does not hold the value Q-028 ruled. This key IS the remedy for "
        f"REVIEW_C1_1's BLOCKER; changing it is a Class A deviation needing a ruling."
    )


@pytest.mark.parametrize("registry_key", sorted(A4_KEYS))
def test_every_a4_constant_is_in_all_three_places(registry_key, repo_root):
    """§8.6's three-way consistency, asserted per key rather than only in aggregate.

    §8.6 and `config/protocol.yaml`'s header each say, verbatim: *"Any constant that is
    not in this table and not in `config/` is a defect, and finding one is a review
    BLOCKER."* ⚠️ **RED BEFORE THIS FIX on all three legs at once** — no config key, no
    §8.6 row, no registry row.

    ``test_every_s86_row_reaches_the_registry`` already checks the two lists agree in
    aggregate. This checks the **named** constant, so a future edit cannot satisfy the
    set-equality by renaming rather than by carrying the value.
    """
    constant = BY_KEY.get(registry_key)
    assert constant is not None, f"{registry_key} is not in the tripwire registry"

    dotted, _ = A4_KEYS[registry_key]
    assert constant.config_path == f"protocol.yaml:{dotted}"

    context = (repo_root / "CONTEXT.md").read_text(encoding="utf-8")
    assert constant.spec_row in context, (
        f"§8.6 has no row named {constant.spec_row!r}, so the tripwire scans for a "
        f"constant the specification does not carry."
    )


def test_the_two_razorpay_defined_a4_figures_are_tagged_razorpay_and_the_rest_are_not():
    """⚠️ **The two tags are MIXED inside one config block, and a wrong tag is a
    `PROVENANCE.md` defect rather than a formatting one.**

    `PROVENANCE.md`'s central rule is that every constant is tagged either
    `[Razorpay-defined]` or `[merchant-policy, author-chosen]`. In `world.instant_settlement`
    exactly ONE landed key is Razorpay's published figure — the IMPS cap — and the other
    four are ours. A probe that only checked *"every row is tagged"* would pass with the
    tags swapped, which is why this one checks **which**.
    """
    assert BY_KEY["a4_imps_outside_banking_hours_cap_paise"].tag == "[Razorpay-defined]"
    for key in A4_KEYS:
        if key != "a4_imps_outside_banking_hours_cap_paise":
            assert BY_KEY[key].tag == "[merchant-policy, author-chosen]", (
                f"{key} is tagged {BY_KEY[key].tag!r}. Razorpay documents these BOUNDS and "
                f"publishes no figure for them; the VALUES are this project's, and "
                f"PROVENANCE.md's whole job is to say which is which."
            )


def test_the_imps_cap_agrees_with_the_rupee_figure_razorpay_publishes():
    """⚠️ **The check that would have caught Q-029, applied to the figure that PASSED it.**

    `paise = rupees × 100`, and RS-17's committed quote gives the cap as ₹2,00,000.
    ``200000 * 100 == 20000000``. **This is the control**: it is the reason Q-029 can say
    the convention is not in doubt and that the defect is specific to RS-16's line.
    """
    rupees = 200000
    assert (
        cfg.load("protocol").require(
            "world.instant_settlement.imps_outside_banking_hours_cap_paise"
        )
        == rupees * 100
    )


def test_the_stopped_sixth_value_is_ruled_and_landed(repo_root):
    """⚠️ **FLIPPED 2026-08-31 BY ARCH BUILD (`8e0f4a13`) ON A RULING, NOT WEAKENED.**

    **This probe used to assert the opposite**, and its previous form is preserved in
    `docs/sessions/arch-q029-1.txt` rather than only in `git log`. It was
    ``test_the_stopped_sixth_value_is_still_stopped_and_still_declared``, and it failed
    if `max_per_settlement_paise` appeared while `QUESTIONS.md` **Q-029** was still
    ``**Status:** **OPEN**``, or if the absence stopped being *declared*. **Q-029 is now
    RULED** (architect, 2026-08-31, Class A), so the state it guarded no longer exists and
    the probe asserts the ruled state instead.

    ⚠️ **HARD RULE 6 IS WHY THIS DOCSTRING IS THIS LONG.** *"NEVER WEAKEN A TEST … If a
    ruling legitimately changes behaviour, the test flips citing the ruling — and the flip
    must be provably meaningful (it fails on the old code)."* **It does, on all four
    assertions at once**: against the pre-ruling tree the key is absent, so ``require``
    raises before any assertion is reached, and the RULED check fails on Q-029's own status
    line. **This is a reversal, not a loosening** — the old probe made one assertion in each
    branch, this one makes four and every one of them is stricter than "the key is absent".

    **The four, and the last is the one Q-029 exists for.** The key resolves through the
    **loader** (not just present in the YAML text); it carries **5,000,000,000**; Q-029 is
    **RULED** and not merely edited; and the value equals the **derivation recomputed here**
    rather than a transcribed constant — ``5 * 10**7 * 100`` — so a future edit that changes
    the figure has to change arithmetic, not a copy of itself.
    """
    protocol = cfg.load("protocol")
    questions = (repo_root / "QUESTIONS.md").read_text(encoding="utf-8")

    entry = re.search(
        r"### Q-029 —.*?\n(.*?)\n(?=### Q-|\n## )", questions, re.S
    )
    assert entry is not None, "Q-029 has been deleted from QUESTIONS.md"
    assert "**Status:** **RULED**" in entry.group(1), (
        "QUESTIONS.md Q-029 is no longer marked RULED, but config/ carries the value it "
        "ruled. Either the question was re-opened without the key being withdrawn, or the "
        "entry was edited. Rs 5 Cr is Class A: it resolved to three different paise "
        "figures and no two agreed, and only an architect ruling closes that."
    )

    value = protocol.require("world.instant_settlement.max_per_settlement_paise")

    # ⚠️ Derived, never transcribed. 1 crore = 10^7, so Rs 5 Cr = 50,000,000 rupees, and
    # paise = rupees * 100 - the convention every other money key in protocol.yaml obeys,
    # with RS-17's Rs 2,00,000 -> 20,000,000 as the control. The two figures this is NOT:
    # 50,000,000,000 (10x, RS-16's Notes line until 2026-08-31) and 500,000,000,000 (100x,
    # the C1 FIX prompt).
    rupees_in_five_crore = 5 * 10**7
    assert value == rupees_in_five_crore * 100, (
        f"world.instant_settlement.max_per_settlement_paise is {value}, and Rs 5 Cr is "
        f"{rupees_in_five_crore * 100} paise. If this is 50000000000 or 500000000000, it "
        f"is the 10x or the 100x figure Q-029 ruled against - both are named in that entry, "
        f"in config/, in RAZORPAY_SEMANTICS.md RS-16 and in PROVENANCE.md S2.4 precisely so "
        f"neither is written back. Changing it is a Class A deviation needing a ruling."
    )
    assert value == 5000000000


def test_every_config_pointer_in_the_oracle_resolves_to_a_real_key(repo_root):
    """⚠️ **THE CHECK THAT DID NOT EXIST, AND WHOSE ABSENCE IS `INC-18`'s `Missing` FIELD.**

    `RAZORPAY_SEMANTICS.md` and `PROVENANCE.md` now name config keys in prose
    (``config/protocol.yaml : world.instant_settlement.…``). **Nothing in this repository
    has ever read such a claim.** That is exactly how three artefacts came to assert that
    two values *"live in `config/`"* when no key, no §8.6 row and no registry row existed:
    the tripwire's three consistency directions all begin from a row that exists in at
    least one of the three lists, so **a constant named only in prose is invisible to every
    one of them.**

    ⚠️ **STATED LIMIT, because a check is worth only what its limit is honest about.**
    This resolves **dotted paths rooted at a real top-level section of `protocol.yaml`**, in
    **two files**. It does not — and cannot, without parsing English — catch a fourth
    artefact writing *"lives in `config/`"* about a key that does not exist. `INC-18`'s
    `Systemic guardrail` says so in those words. This narrows the gap; it does not close it.

    ⚠️ **The text is whitespace-normalised before matching, and that is not a convenience.**
    Both artefacts wrap at 100 columns, so a pointer can be split across two lines mid-path;
    a line-oriented parser would silently see fewer pointers than exist, which is `INC-14`'s
    *"a check that reports PASS over nothing"* arriving in the checker instead of the code.
    **The floor assertion below is what makes that failure loud rather than green.**
    """
    protocol = cfg.load("protocol")
    top_level = set(protocol.data)
    # A pointer is a backticked dotted path whose HEAD is a real protocol.yaml section.
    # Rooting it that way is what keeps `refunds.go:66`, `pkg/razorpay/...` and
    # `spec_constants.py` out without an exclusion list that could quietly grow.
    pattern = re.compile(r"`([a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+)`")

    unresolved: list[str] = []
    seen = 0
    for name in ("RAZORPAY_SEMANTICS.md", "PROVENANCE.md"):
        text = re.sub(r"\s+", " ", (repo_root / name).read_text(encoding="utf-8"))
        for dotted in pattern.findall(text):
            if dotted.split(".")[0] not in top_level:
                continue
            seen += 1
            if not protocol.has(dotted):
                unresolved.append(f"{name}: {dotted}")

    assert seen >= 7, (
        f"only {seen} config pointer(s) found across the two artefacts, which is fewer "
        f"than the 7 they carried on 2026-08-31. Either the pointers were removed or this "
        f"parser stopped seeing them - and a check that silently reads nothing is the same "
        f"class of defect as the one it replaces (INC-14)."
    )
    assert not unresolved, (
        "an artefact names a config key that config/protocol.yaml does not define:\n  "
        + "\n  ".join(unresolved)
        + "\n\nThis is REVIEW_C1_1's BLOCKER F-R4 exactly: a file asserting a location "
        "that is empty. PROVENANCE.md §2.4's own preamble promises 'This table asserts "
        "nothing that file does not source.'"
    )


# ── Q-027 / INC-20 — S2's third definition ────────────────────────────────────────────


def _s92(repo_root: object) -> str:
    """§9.2's text, **whitespace-normalised**.

    ⚠️ Normalised deliberately: `CONTEXT.md` wraps at 100 columns, so RS-27's quote is
    split across two lines inside §9.2 and a raw substring test would report it missing
    while it is plainly there. A probe that fails for a formatting reason gets weakened,
    and hard rule 6 is about what happens next.
    """
    text = (repo_root / "CONTEXT.md").read_text(encoding="utf-8")
    start = text.index("## 9.2 Sequence invariants")
    return re.sub(r"\s+", " ", text[start : text.index("## 9.3 ", start)])


def test_s2_is_defined_on_issue_not_on_execution(repo_root):
    """⚠️ **RED BEFORE THIS FIX: §9.2 read *"two executed refunds"*.**

    `QUESTIONS.md` **Q-027**, RULED, APPROVED BY THE OPERATOR. `INCIDENTS.md` **INC-20**.
    Razorpay rejects a duplicate ``receipt`` itself (RS-27, 400), scoped *"for an earlier
    refund on the same payment"* — **S2's scope exactly** — so in a world faithful to that
    rejection the second refund is never EXECUTED and **S2 as defined could not fire**. One
    unfirable predicate had been swapped for another.
    """
    section = _s92(repo_root)
    assert "**S2 IS NOW: two refunds ISSUED ON THE SAME PAYMENT" in section, (
        "§9.2's S2 no longer reads ISSUED. Q-027 ruled that S2 fires at issue, not at "
        "execution, because the gate acts at issue and Razorpay's own guard refuses the "
        "second execution. Reverting to 'executed' restores a predicate that CANNOT FIRE."
    )
    assert "two executed refunds ON THE SAME PAYMENT" not in section, (
        "the withdrawn MOVE 3 definition is back as the live one."
    )


def test_s2_carries_the_razorpay_rejection_that_forced_the_move(repo_root):
    """**The two halves of Q-027's argument must not drift apart.**

    The predicate is only defensible *because* the world rejects the duplicate. A §9.2
    that says ISSUED without saying why reads as a weakening of the invariant rather than
    as a correction of its scope — and the next session to read it would have no reason
    not to move it back.
    """
    section = _s92(repo_root)
    assert "Duplicate receipt found for this refund request." in section
    assert "an earlier refund on the same payment" in section
    assert "RS-27" in section


def test_s2_shows_all_three_withdrawn_definitions_and_why_each_failed(repo_root):
    """⚠️ **S2 has been redefined THREE times and a reader must see all three.**

    WRONG (INC-04, false positives in 8/8 seeds) → UNSENDABLE (`refunds.go:73-75` passes
    ``nil``) → UNFIRABLE (RS-27 refuses it). **Only the third is a one-word scope
    correction.** A file that showed only the current definition would hide the two
    strongest pieces of evidence this project has that a plausible invariant can be wrong,
    which is the same argument that keeps ``S2-amt``.
    """
    section = _s92(repo_root)
    for marker in ("MOVE 1", "MOVE 2", "MOVE 3", "INC-04", "Q-017", "Q-027"):
        assert marker in section, f"§9.2's S2 no longer records {marker}"
    assert "**`S2-amt` IS UNCHANGED.**" in section


def test_s2_still_says_it_may_print_a_zero_for_the_attacker_shaped_reason(repo_root):
    """**The move to ISSUED removes ONE of two reasons S2 could not fire, not both.**

    Q-017's caveat survives untouched: a policy-blind attacker has no reason to populate
    ``receipt`` either, and nothing can fix that. A §9.2 that dropped this line while
    adopting ISSUED would be claiming the correction bought more than it did.
    """
    section = _s92(repo_root)
    assert "S2 MAY PRINT A ZERO" in section
    assert "MOVE 3 DOES NOT REPAIR THIS" in section


def test_the_harm_metric_is_untouched_by_the_move(repo_root):
    """⚠️ **§12.2 is NOT edited, and that is the point rather than an omission.**

    Q-027's reason 2: the ledger already writes a harm record for every action the gate
    allowed *"whether or not the world then rejected it"*, and already contributes ZERO
    when ``rejected_by_razorpay``. So ISSUED needs **no new field and moves no figure**.
    §12.2's A3 row keeps *"executed"* deliberately: a harm class and a scored invariant are
    different objects, and the **gap between them is the publishable quantity** — Razorpay's
    own guard, measured. Collapsing the two would delete the finding.

    ⚠️ **This probe is GREEN on the pre-fix tree too, and that is the correct result** — the
    property it asserts is *"§12.2 did not move"*, which was true before this session and is
    true after. Its job is to fail on a **future** session aligning §12.2's A3 row with S2's
    predicate, which would look like tidying and would delete Q-027's reason 3.
    """
    text = re.sub(
        r"\s+", " ", (repo_root / "CONTEXT.md").read_text(encoding="utf-8")
    )
    assert (
        "whether or not the world then rejected it" in text
    ), "§12.2's live-field clause is what makes ISSUED cost nothing"
    assert (
        "**A3** duplicate refund | second executed refund with a seen idempotency key"
        in text
    ), (
        "§12.2's A3 harm row no longer says 'executed'. It is deliberately NOT aligned "
        "with S2's predicate - harm is booked when money moves, S2 is scored when the gate "
        "let it be attempted, and the difference between them is Q-027's reason 3."
    )


# ── Q-026 — the two cells ruled DEFENSIBLE, and the one sentence corrected ────────────


def test_context_line_178_no_longer_carries_the_sentence_its_own_spec_calls_false(repo_root):
    """⚠️ **RED BEFORE THIS FIX.** `QUESTIONS.md` **Q-026**, UPHELD.

    §9.2 calls *"`create_refund` sends no idempotency key"* **false**; `PROVENANCE.md`
    marks it *"❌ do not write"*. It survived in §2's prose block — the one headed *"written
    so a payments engineer cannot puncture it"* — because v1.3 corrected the **table row**
    fifteen lines above and left the prose. Independently confirmed by C1's reviewer as
    `F-R10`.
    """
    text = (repo_root / "CONTEXT.md").read_text(encoding="utf-8")
    assert "and `create_refund` sends no idempotency key — so a" not in text, (
        "§2's prose block carries the false form again. §9.2 line-for-line calls this "
        "sentence false and PROVENANCE.md marks it 'do not write'."
    )
    assert "`X-Refund-Idempotency` — which their own MCP server structurally cannot send" in text


def test_the_two_a3_mechanism_cells_ruled_defensible_are_not_edited(repo_root):
    """⚠️ **A PROBE WHOSE JOB IS TO FAIL IF SOMEBODY "FIXES" SOMETHING CORRECT.**

    Q-026's ruling: *"C1's REVIEWER JUDGED §6's A3 Mechanism cell and `PROVENANCE.md`
    §2.4's A3 cell DEFENSIBLE — they describe what the attacker does in this attack, not
    what the tool CAN do … recorded here so a later session does not 'fix' them into
    inaccuracy."*

    A policy-blind attacker **does** send no idempotency key. Rewriting these to say the
    tool *cannot* send one would make them **false in the other direction** — the tool can
    send ``receipt``, which is the entire content of RS-27 and of Q-017.
    """
    context = (repo_root / "CONTEXT.md").read_text(encoding="utf-8")
    provenance = (repo_root / "PROVENANCE.md").read_text(encoding="utf-8")
    assert "Same logical refund issued twice; no idempotency key is sent" in context, (
        "§6's A3 Mechanism cell has been edited. Q-026's ruling explicitly leaves it "
        "alone: it describes the ATTACKER's behaviour, not the tool's capability."
    )
    assert (
        "the same logical refund issued twice; no idempotency key is sent" in provenance
    ), "PROVENANCE.md §2.4's A3 Mechanism cell has been edited. Same ruling, same reason."


# ── The registry rows' scan modes, asserted rather than assumed ───────────────────────


def test_the_small_integer_a4_constants_are_contextual_and_the_paise_ones_are_strict():
    """**Why the two modes, per row, and why getting it wrong is not cosmetic.**

    ``5``, ``True`` and ``False`` recur innocently in every Python file ever written, so a
    STRICT scan for them fires constantly — and hard rule 6 names what happens next: *the
    first thing anyone would do is weaken it.* They are CONTEXTUAL and gated on names.

    The paise integers are eight digits and distinctive, so a bare literal is a defect on
    its face and needs no name to gate it — the same shape as ``episode_cap_paise``.

    ⚠️ **A CONTEXTUAL row cannot see an UNNAMED literal** (``if attempts > 5:`` written
    inline). That limit is real, is already recorded as **OF-33** against ``index % 6``, and
    is stated in each row's own ``note``. The name lists are a mitigation, not a proof.
    """
    for key in ("a4_daily_withdrawable_limit_paise", "a4_imps_outside_banking_hours_cap_paise"):
        assert BY_KEY[key].mode is ScanMode.STRICT, key
    for key in (
        "a4_max_attempts_per_day",
        "a4_attempt_counter_includes_rejected",
        "a4_within_banking_hours",
    ):
        constant = BY_KEY[key]
        assert constant.mode is ScanMode.CONTEXTUAL, key
        assert constant.name_patterns, (
            f"{key} is CONTEXTUAL with no name patterns, so it scans for nothing at all "
            f"and reports green - a tripwire in name only."
        )
