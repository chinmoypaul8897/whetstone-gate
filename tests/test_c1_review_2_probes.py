"""C1 ADVERSARIAL RE-REVIEW, attempt 2 — kept probes. `SESSION-TOKEN: df238be6`.

**Every probe here is GREEN, and every one of them closes a gap this review DEMONSTRATED
with a mutant** — not a gap it reasoned about. The mutation table is
`docs/reviews/mutants/c1_mutants.md`; the review is `docs/reviews/REVIEW_C1_2.md`.

⚠️ **Why green and not red.** `REVIEW_C1_1.md` shipped one deliberately-red probe, which was
right for a **FAIL**. This review **PASSES**, and a chunk cannot be done while a test in its
own area is red, so the defects that would need a red probe go to `OPEN_FINDINGS.md` for a
FIX session instead — with the mutant that proves each one committed beside them. Nothing is
weakened: a mutant is executable evidence too, and it is in the repository.

**What each probe is worth, stated as the mutant it kills:**

===========  =====================================================================  ==========
Probe        The mutant it kills, from `c1_mutants.md`                              was
===========  =====================================================================  ==========
``P1``       ``M-19``-class, generalised: ANY edit to ANY verbatim quote in §1       —
             onward. Nothing in this repository pinned the quote sequence; §0's
             own check cannot compare bytes offline for 297 of the 301 lines.
``P2``       ``M-15`` — a §8.6 row's PRINTED value diverging from ``config/``.       SURVIVED
``P3``       ``M-16`` and ``M-24`` — a TAG flipped in §8.6, and the SIXTH key's      SURVIVED
             tag, which `A4_KEYS` excludes so no assertion ever saw it.
``P4``       pins the TRUE offline-verifiable count (297), which §0 prints as 300.   —
``P5``       documents and guards the ``> **code:** 400`` blind spot that let        SURVIVED
             ``M-26`` through while its control ``M-27`` was killed.
``P6``       ``M-17``-class, generalised to EVERY money key rather than one.         —
===========  =====================================================================  ==========

⚠️ **`P1` is the one that would have mattered most on 31 August** and is this review's main
contribution to the file's future: `RAZORPAY_SEMANTICS.md` is the oracle C4 builds the world
from, its value is that its `>` blocks are Razorpay's bytes, and **until now the only thing
standing behind that was a human re-fetch.** This review re-fetched all twelve sources and
matched **301 of 301 quoted lines against the source each row cites**; `P1` freezes that
result so no later edit can move a quote silently.
"""

from __future__ import annotations

import hashlib
import re
import subprocess

import pytest

from whetstone_gate import config as cfg
from whetstone_gate.spec_constants import BY_KEY

# ── §0's own reduction rules, reproduced so the probes speak §0's language ────────────

ADDED_FIELD_LABELS = ("**error:**", "**code:**", "**description:**", "**solution:**")
_LABEL_RE = re.compile("|".join(re.escape(x) for x in ADDED_FIELD_LABELS))
SCOPE_HEADING = "## 1. Sources"

#: The SHA-256 of the newline-joined sequence of every line beginning with ``>`` from §1
#: onward, as committed at ``55f1f2c`` — `RAZORPAY_SEMANTICS.md`'s FIRST and only content
#: commit — and re-measured at every commit since. ⚠️ **Computed at `55f1f2c`, not at HEAD**,
#: so it is a pin against the file's origin rather than against whatever it happens to say
#: today; that is the whole point.
QUOTE_SEQUENCE_SHA256 = "04b453c9123ff002e1350b7dffa71a780efa41086ebb16ad013de51444108f5c"

#: All six of A4's configured values: registry key → (§8.6 constant cell, expected tag).
A4_ALL_SIX = {
    "a4_daily_withdrawable_limit_paise": (
        "A4 daily withdrawable limit",
        "[merchant-policy, author-chosen]",
    ),
    "a4_max_attempts_per_day": ("A4 max attempts per day", "[merchant-policy, author-chosen]"),
    "a4_attempt_counter_includes_rejected": (
        "A4 attempt counter includes rejected",
        "[merchant-policy, author-chosen]",
    ),
    "a4_within_banking_hours": ("A4 banking-hours setting", "[merchant-policy, author-chosen]"),
    "a4_imps_outside_banking_hours_cap_paise": (
        "A4 IMPS outside-banking-hours cap",
        "[Razorpay-defined]",
    ),
    # ⚠️ THE SIXTH. `test_c1_fix_probes.A4_KEYS` deliberately excludes it — that dict is
    # partitioned on exactly ONE Razorpay-tagged key — so before this file NOTHING asserted
    # its tag. Mutant M-24 flipped it and the suite stayed green; M-25, the identical flip on
    # the IMPS cap, was killed instantly. The difference was membership of a dict.
    "a4_max_per_settlement_paise": ("A4 max per settlement", "[Razorpay-defined]"),
}


@pytest.fixture(scope="module")
def oracle_lines(repo_root):
    return (repo_root / "RAZORPAY_SEMANTICS.md").read_text(encoding="utf-8").split("\n")


def _payload(line: str) -> str:
    text = _LABEL_RE.sub("", line[1:]).strip()
    if len(text) >= 2 and text.startswith("`") and text.endswith("`"):
        text = text[1:-1]
    return text


def _scoped_quote_lines(lines: list[str]) -> list[str]:
    start = next(i for i, ln in enumerate(lines) if ln.startswith(SCOPE_HEADING))
    return [ln for ln in lines[start:] if ln.startswith(">")]


def _row_at(lines: list[str], index: int) -> str | None:
    current = None
    for i, line in enumerate(lines):
        if i > index:
            break
        m = re.match(r"^### (RS-\d+)", line)
        if m:
            current = m.group(1)
        elif line.startswith("## "):
            current = None
    return current


# ── P1 ────────────────────────────────────────────────────────────────────────────────


def test_p1_every_verbatim_quote_is_byte_identical_to_the_oracles_first_commit(oracle_lines):
    """⚠️ **THE QUOTE SEQUENCE IS PINNED. NOTHING PINNED IT BEFORE.**

    `RAZORPAY_SEMANTICS.md` exists to be Razorpay's bytes. §0 says so and describes a check
    that would prove it — but **297 of its 301 quoted lines cannot have their bytes checked
    offline**, because the ten pages and two pinned trees are not vendored (`OF-15`, open).
    So between re-fetches there was nothing at all: `M-19`, `M-22` and `M-02` are three
    different ways of editing this file's content, and only one of them was caught.

    This probe closes the general case without vendoring anything and without a network
    call: it pins the **sequence of every `>` line from §1 onward** to its SHA-256 at
    ``55f1f2c``, the file's first and only content commit. Any edit to any verbatim quote —
    a digit, a negation, a swapped remediation, a deleted line, a reordering — moves the
    hash.

    ⚠️ **It deliberately does NOT cover §0's own check block**, which is exactly the carve-out
    §0's scope sentence already makes (*"Counted over §1 onward"*). That is why the whole-file
    `>` count could legitimately move 313 → 316 when the C1 FIX session rewrote §0, while
    **this** sequence did not move at all — measured at `55f1f2c`, `62c4f89`, `3b35e85`,
    `32dfb7f` and HEAD, identical at every one.

    ⚠️ **A ruling may legitimately change a quote** — if Razorpay's page changes, the drift is
    recorded with both dates (`PROCESS.md` §9). This assertion then flips **citing that
    ruling**, and the flip is provable because the old hash is in git. It is never edited to
    match whatever the file now says; that is hard rule 6's forbidden move.
    """
    quoted = _scoped_quote_lines(oracle_lines)
    digest = hashlib.sha256("\n".join(quoted).encode("utf-8")).hexdigest()
    assert digest == QUOTE_SEQUENCE_SHA256, (
        "THE SEQUENCE OF VERBATIM QUOTES IN RAZORPAY_SEMANTICS.md HAS CHANGED.\n"
        f"  expected {QUOTE_SEQUENCE_SHA256}  (as committed at 55f1f2c)\n"
        f"  got      {digest}  ({len(quoted)} lines beginning with '>' from §1 onward)\n\n"
        "This file is the oracle C4 builds the world from, and its whole value is that its "
        "'>' blocks are Razorpay's bytes and not the author's. If a page genuinely changed, "
        "record the drift with BOTH dates and flip this constant citing the ruling — the old "
        "hash is in git, so the flip is provable. If it did not, a quote has been edited."
    )


# ── P2 ────────────────────────────────────────────────────────────────────────────────


def test_p2_every_a4_value_printed_in_context_8_6_equals_the_value_in_config(repo_root):
    """⚠️ **MUTANT M-15 SURVIVED THE ENTIRE SUITE, AND THIS IS WHY.**

    §8.6's constants table is the tripwire's *authoritative list* (hard rule 9), and the
    "three-way check" is asserted in both directions — but **both directions match on the ROW
    NAME**. ``parse_s86_rows`` returns a ``list[str]`` of *Constant* cells;
    ``test_every_s86_row_reaches_the_registry`` compares those names to
    ``SpecConstant.spec_row``, and ``test_registry_covers_every_config_constant`` resolves
    ``config_path``. **No step anywhere compares the VALUE printed in §8.6 to the value in
    ``config/``.**

    So §8.6 could print *30,000,000 paise* beside a `config/` holding `3000000` and the suite
    stays green — demonstrated, not argued: mutant **M-15** did exactly that and survived.
    §8.6 is what a reader is pointed at; `config/` is what the world reads; a divergence
    publishes one number and runs another.
    """
    context = (repo_root / "CONTEXT.md").read_text(encoding="utf-8")
    protocol = cfg.load("protocol")

    checked = 0
    for key, (spec_row, _tag) in A4_ALL_SIX.items():
        row = next(
            (ln for ln in context.split("\n") if ln.startswith(f"| **{spec_row}**")), None
        )
        assert row is not None, (
            f"CONTEXT.md §8.6 has no row whose Constant cell is {spec_row!r}. Either the row "
            f"was renamed and this probe not updated, or a constant left the table — and "
            f"§8.6: 'Any constant that is not in this table and not in config/ is a defect, "
            f"and finding one is a review BLOCKER.'"
        )
        dotted = BY_KEY[key].config_path.split(":", 1)[1]
        value = protocol.require(dotted)
        if isinstance(value, bool):
            # Booleans are printed as literals, not digits — sometimes bare inside backticks
            # (`` `true` ``) and sometimes as the whole assignment
            # (`` `within_banking_hours: false` ``), so match the word rather than a wrapping.
            printed = re.findall(r"\b(true|false)\b", row)
            assert printed, f"{spec_row}: §8.6 prints no `true`/`false` literal"
            assert printed[0] == str(value).lower(), (
                f"{spec_row}: config/ holds {value!r}; §8.6 prints `{printed[0]}`"
            )
        else:
            # Accept 30000000 or the Indian-grouped 3,00,00,000 / 30,000,000 forms.
            found = {int(m.replace(",", "")) for m in re.findall(r"\b[\d,]*\d\b", row)}
            assert value in found, (
                f"{spec_row}: config/ holds {value:,} at {dotted}, and CONTEXT.md §8.6's row "
                f"prints no such number. §8.6 is the list a reader is pointed at and config/ "
                f"is what the world reads; publishing one and running the other is the defect "
                f"this probe exists for.\n  row: {row[:220]}"
            )
        checked += 1

    assert checked == 6, f"checked {checked} A4 rows, not the 6 that must exist"


# ── P3 ────────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("key", sorted(A4_ALL_SIX))
def test_p3_every_a4_tag_is_asserted_including_the_sixth_key(key, repo_root):
    """⚠️ **THE SIXTH KEY'S TAG WAS ASSERTED BY NOTHING, AND A TAG IS A PROVENANCE DEFECT.**

    ``test_c1_fix_probes.A4_KEYS`` holds **five** keys and partitions them on *exactly one*
    Razorpay-tagged entry, so ``a4_max_per_settlement_paise`` — the **second**
    `[Razorpay-defined]` key — could not be added without turning that probe red. ARCH BUILD
    (`8e0f4a13`) recorded the omission in its report and argued the key is *"covered in full
    by the flipped probe instead — loader resolution, ruled status, and the value
    re-derived."* **The tag is not in that list**, and the same session's own registry note
    says *"getting one wrong is a PROVENANCE.md defect, not a formatting one."*

    Measured rather than argued, with its own control:

      * **M-24** — flip ``a4_max_per_settlement_paise``'s tag → **SURVIVED**, suite green.
      * **M-25** — the identical flip on ``a4_imps_outside_banking_hours_cap_paise`` →
        **KILLED** at once.

    The tag machinery works; the sixth key was simply outside it, because a dict has five
    entries. This probe is over **all six**, so membership of a dict is no longer what decides
    whether a provenance tag is checked.

    ⚠️ **The tags are judged on the merits, not on the three places agreeing with each other**
    — `REVIEW_C1_2.md` §2 records the source check for each, including the one that could have
    been wrong by 10×: S5's comparison table is headed ``Feature| Instant Settlement | Smart
    Settlements |`` and reads ``Maximum amount per settlement | ₹5 Crores | ₹50 Crores |``, so
    **₹5 Crores is the Instant Settlement column** and `[Razorpay-defined]` is right.
    """
    spec_row, expected = A4_ALL_SIX[key]
    constant = BY_KEY[key]
    assert constant.tag == expected, (
        f"{key} is tagged {constant.tag!r}; on the merits it is {expected!r}.\n"
        f"PROVENANCE.md's whole job is to say which figures are Razorpay's and which are "
        f"ours. Razorpay publishes ₹5 Cr (S5's table, Instant Settlement column) and ₹2,00,000 "
        f"(RS-17's own solution line) and NO figure for the daily limit, the attempt count, "
        f"the banking-hours window or the counter's reading."
    )
    assert constant.spec_row == spec_row, (
        f"{key}'s spec_row is {constant.spec_row!r}, not {spec_row!r} — the §8.6 → registry "
        f"direction matches on this string, so a drift here silently unlinks the two lists."
    )

    # ⚠️ AND THE SAME TAG IN §8.6, WHICH IS THE THIRD PLACE AND WAS THE UNGUARDED ONE.
    # Mutant M-16 flipped the tag in CONTEXT.md's own §8.6 cell — leaving the registry and
    # config/ untouched — and SURVIVED, because the registry is what every existing tag
    # assertion reads. §8.6 is the table PROVENANCE.md and the tripwire are both pointed at,
    # so a reader is told one provenance while the registry carries another.
    context = (repo_root / "CONTEXT.md").read_text(encoding="utf-8")
    row = next(ln for ln in context.split("\n") if ln.startswith(f"| **{spec_row}**"))
    other = (
        "[Razorpay-defined]"
        if expected != "[Razorpay-defined]"
        else "[merchant-policy, author-chosen]"
    )
    assert expected in row, (
        f"CONTEXT.md §8.6's row for {spec_row!r} does not carry the tag {expected!r} that "
        f"the registry carries.\n  row: {row[:240]}"
    )
    if expected == "[Razorpay-defined]":
        # The author-chosen phrase legitimately appears in the two mixed BOUND/VALUE rows,
        # so only the purely-Razorpay rows can assert the other tag's absence.
        assert other not in row, (
            f"CONTEXT.md §8.6's row for {spec_row!r} carries BOTH tags. This value is "
            f"Razorpay's published figure; tagging it as ours would move it out of the set "
            f"PROVENANCE.md says we chose.\n  row: {row[:240]}"
        )


# ── P4 ────────────────────────────────────────────────────────────────────────────────


def test_p4_the_offline_verifiable_count_regenerates_from_the_file(oracle_lines):
    """⚠️ **PINS THE TRUE QUANTITY. §0 PRINTS A DIFFERENT ONE — see `OF-22`.**

    §0's property 5 promises *"the number of lines the verbatim half CANNOT verify offline is
    printed as a number"*, and §0 prints **300**. The implementation asserts **297**
    (``test_the_offline_gap_is_printed_as_a_number_and_not_as_a_silence``), and 297 is right:
    §8 carries exactly **4** quoted lines and property 4 verbatim-matches all four against
    `CONTEXT.md`. ``301 − 4 = 297``.

    ⚠️ **This is `F-R2`'s class in the section that closed `F-R2`** — a published number that
    does not regenerate — and it is invisible because
    ``test_the_declared_blank_count_is_exactly_what_section_0_publishes`` string-binds only
    304, 3 and 301, and the offline-gap test asserts an identity between two literals it
    hardcodes itself. **Nothing reads §0's printed 300.**

    This probe pins the quantity that is true, computed from the file rather than transcribed,
    so a FIX correcting §0's sentence has something to correct it *to*.
    """
    lines = oracle_lines
    quoted = _scoped_quote_lines(lines)
    payloads = [_payload(ln) for ln in quoted]
    non_empty = [p for p in payloads if p]

    assert len(quoted) == 304
    assert len(payloads) - len(non_empty) == 3
    assert len(non_empty) == 301

    section_8 = next(i for i, ln in enumerate(lines) if ln.startswith("## 8. "))
    section_9 = next(i for i, ln in enumerate(lines) if ln.startswith("## 9. "))
    in_s8 = [
        ln
        for i, ln in enumerate(lines)
        if section_8 <= i < section_9 and ln.startswith(">") and _payload(ln)
    ]
    assert len(in_s8) == 4, f"§8 carries {len(in_s8)} quoted lines, not 4"

    verifiable_offline = len(in_s8)
    assert len(non_empty) - verifiable_offline == 297, (
        "the count of quoted lines whose bytes CANNOT be checked offline has moved. If the "
        "ten source bodies are ever vendored under tests/fixtures/, this number should drop "
        "and this assertion should be updated deliberately — never silently."
    )


# ── P5 ────────────────────────────────────────────────────────────────────────────────


def test_p5_the_http_cross_checks_true_coverage_is_measured_and_its_blind_spot_named(
    oracle_lines,
):
    """⚠️ **THE `> **code:** 400` BLIND SPOT — mutant `M-26` survived, its control was killed.**

    §0's property 3 is published as a universal: *"Every row's declared `HTTP` code equals the
    `code:` line inside its own quote."* The implementation's regex is
    ``code:\\s*`?([1-5]\\d{2})`?`` run against the **raw** ``>`` line — so it cannot cross the
    ``**`` in the three concurrency rows that write ``> **code:** 400``. Those rows fall into
    the bucket the shipped test's own docstring and assertion call *"4 whose quote carries no
    `code:` line"*. **Only RS-06 truly has none; three of that four have one the regex cannot
    see**, and the assertion ``(12, 4, 16)`` pins the mis-categorisation in place.

    Measured, with its own control:

      * **M-26** — RS-22's own quoted ``400`` → ``409`` in the bold form → **SURVIVED**.
      * **M-27** — the identical corruption on RS-01, whose code line is plain → **KILLED**.

    ⚠️ **These are exactly the rows `REVIEW_C1_1.md` called the most dangerous in the file**:
    RS-22 and RS-23 are the near-identical concurrency rows, and `M-12` — *"the worst"*, a
    remediation lifted from the wrong page — is the swap between them. The module already
    knows the bold form: ``**code:**`` is in its own ``ADDED_FIELD_LABELS`` and ``_payload``
    strips it. Property 3 simply does not route through ``_payload``.

    This probe measures the true coverage form-agnostically and fails if it moves — including
    when somebody fixes it, which is the right moment to update the numbers deliberately.
    """
    both_forms = re.compile(r"(?:\*\*)?code:(?:\*\*)?\s*`?([1-5]\d{2})`?")
    shipped_form = re.compile(r"code:\s*`?([1-5]\d{2})`?")

    comparable, seen_by_shipped, blind = 0, 0, []
    for i, line in enumerate(oracle_lines):
        m = re.match(r"^\*\*HTTP\*\* (.+?) ·", line)
        if not m or not re.findall(r"\b[1-5]\d{2}\b", m.group(1)):
            continue
        row = _row_at(oracle_lines, i)
        start = next(
            j for j in range(i, -1, -1) if oracle_lines[j].startswith(f"### {row} ")
        )
        quote = [ln for ln in oracle_lines[start:i] if ln.startswith(">")]
        if any(both_forms.search(ln) for ln in quote):
            comparable += 1
            if any(shipped_form.search(ln) for ln in quote):
                seen_by_shipped += 1
            else:
                blind.append(row)

    assert comparable == 40, (
        f"{comparable} rows carry a declared HTTP code AND a code: line in one of the two "
        f"written forms, not the 40 measured on 2026-08-31."
    )
    assert seen_by_shipped == 37, (
        f"the shipped check compares {seen_by_shipped} rows, not the 37 it asserts."
    )
    assert blind == ["RS-22", "RS-23", "RS-24"], (
        f"the set of rows invisible to §0's property 3 has changed: {blind}. It was exactly "
        f"RS-22, RS-23 and RS-24 on 2026-08-31 — the three rows that write their code as "
        f"'> **code:** 400', which the shipped regex cannot cross. If this list is now EMPTY "
        f"the blind spot has been fixed and OF-23 closes: delete this assertion citing that. "
        f"If it has GROWN, a new row has quietly joined the unchecked set."
    )


# ── P6 ────────────────────────────────────────────────────────────────────────────────


def test_p6_every_money_key_obeys_paise_equals_rupees_times_one_hundred():
    """⚠️ **THE CONVENTION Q-029 TURNED ON, GENERALISED FROM ONE KEY TO ALL NINE.**

    Q-029 cost a declared STOP and a Class A ruling because ₹5 Cr resolved to **three**
    disagreeing paise figures and no two agreed: 5,000,000,000 (correct), 50,000,000,000
    (**10×**, what RS-16's own Notes carried until 31 Aug) and 500,000,000,000 (**100×**, what
    the C1 FIX prompt supplied). The ruling's guard is a single probe over a single key.

    **The derivation, recomputed here rather than transcribed** — so a future edit that
    changes the figure must change arithmetic, not a copy of itself:
    1 crore = 10⁷, so ₹5 Cr = 5 × 10⁷ = 50,000,000 rupees; × 100 = **5,000,000,000 paise**.

    ⚠️ **The convention is the control.** RS-17's parallel line (``₹2,00,000 = 20,000,000``)
    is what proved the RS-16 defect was one author-written annotation and not a reading error,
    and it did so because *every other money key obeys `paise = rupees × 100` without
    exception*. That property was asserted in prose, in three artefacts, and by no test. It is
    asserted here, over every money key in `config/protocol.yaml`.
    """
    protocol = cfg.load("protocol")
    crore = 10**7
    expected = {
        "money.per_action_cap_paise": 50_000,
        "money.episode_cap_paise": 200_000,
        "world.amount_min_paise": 500,
        "world.amount_max_paise": 150_000,
        "world.merchant_available_balance_paise": 500_000,
        "probe.payment_amount_paise": 80_000,
        "world.instant_settlement.daily_withdrawable_limit_paise": 300_000,
        "world.instant_settlement.imps_outside_banking_hours_cap_paise": 200_000,
        "world.instant_settlement.max_per_settlement_paise": 5 * crore,
    }
    for dotted, rupees in expected.items():
        value = protocol.require(dotted)
        assert value == rupees * 100, (
            f"{dotted} = {value:,} paise, but ₹{rupees:,} × 100 = {rupees * 100:,}. "
            f"config/protocol.yaml's own header: 'Integer paise end to end.'"
        )

    five_crore_paise = 5 * crore * 100
    assert five_crore_paise == 5_000_000_000
    assert protocol.require(
        "world.instant_settlement.max_per_settlement_paise"
    ) == five_crore_paise, (
        "₹5 Cr is 5,000,000,000 paise. 50,000,000,000 is ₹50 Cr (10×, RS-16's Notes line "
        "until 2026-08-31) and 500,000,000,000 is ₹500 Cr (100×, the C1 FIX prompt). "
        "QUESTIONS.md Q-029, RULED."
    )


# ── the evidence this review's own claims rest on, kept executable ────────────────────


def test_no_reviewer_probe_file_has_ever_been_edited_by_a_later_session(repo_root):
    """⚠️ **HARD RULE 6, MADE MECHANICAL.**

    A fix session editing a reviewer's probe to get green is the precise move hard rule 6
    exists to catch. C1 FIX (`365deaf7`) claimed it did **not** do that — that it *"FITTED §0's
    SENTENCE TO THE REVIEWER'S ASSERTION rather than editing the reviewer's probe"* — and this
    review verified it: ``tests/test_c1_review_probes.py`` has exactly one commit, `4cfddc0`,
    and its blob is ``3a3af44d…`` at that commit **and** at HEAD.

    The claim was true. This probe makes it stay true, for every reviewer probe file in the
    project rather than for the one that happened to be checked.

    ⚠️ **THE INVARIANT IS ONE AUTHOR, NOT ONE COMMIT — and this probe was WRONG the first way
    round.** It first asserted *exactly one commit per file*, and it went red inside this very
    session, on this very file, the moment a second commit refined ``P3``. A review that
    amends its own probe before it is finished has done nothing wrong; a **later** session
    touching it is the whole offence. So the assertion is over the ``Session-Token`` trailer:
    every commit that touches a reviewer's probe file must carry the token of the session that
    authored it. That is the same identity `make check-roles` polices, applied to the one
    class of file hard rule 6 names.

    The mistake is left recorded here rather than tidied away, because a probe whose first
    form was wrong is exactly the kind of thing this project's reports are supposed to say out
    loud.

    ⚠️ **A legitimate reason for a later session to touch one exists** — `OF-19` records that
    renaming ``### RS-70 (note)`` would raise ``ValueError`` inside C1's reviewer's own
    partition probe. When that happens the edit is made by *a review session*, deliberately,
    and this assertion is updated citing it. What it forbids is a **fix** session doing it
    quietly to get green.
    """
    probes = sorted(repo_root.glob("tests/test_c*_review*_probes.py"))
    assert len(probes) >= 5, f"only {len(probes)} reviewer probe files found: {probes}"

    offenders = {}
    for path in probes:
        rel = path.relative_to(repo_root).as_posix()
        out = subprocess.run(
            ["git", "log", "--format=%h%x00%s%x00%b%x01", "--", rel],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        tokens = {}
        for entry in out.stdout.split("\x01"):
            if not entry.strip():
                continue
            sha, subject, body = (entry.strip().split("\x00") + ["", ""])[:3]
            found = re.search(r"^Session-Token:\s*([0-9a-f]{8})\s*$", body, re.M)
            tokens.setdefault(found.group(1) if found else "(none)", []).append(
                f"{sha} {subject[:60]}"
            )
        if len(tokens) > 1:
            offenders[rel] = tokens

    assert not offenders, (
        "a reviewer's probe file has been touched by MORE THAN ONE SESSION. A later session "
        "editing a reviewer's probe to get green is hard rule 6's central case, and the "
        "Session-Token trailer is what distinguishes it from the review refining its own "
        "work:\n  " + "\n  ".join(f"{k}: {v}" for k, v in offenders.items())
    )
