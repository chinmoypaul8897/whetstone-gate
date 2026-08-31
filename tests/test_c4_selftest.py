"""The spend-free self-test — that it is green, what it prints, and **that it can go red**.

`CONTEXT.md` §13.5(7) requires the self-test; `PROCESS.md` §12.1's C4 row, as amended under
`QUESTIONS.md` **Q-018**, gives it a denominator; and `PROCESS.md` §5.4 gives the reason this
file's second half exists:

    ⚠️ **THE REVIEW GATE MUST GO RED ON PURPOSE.**

⚠️ **A SELF-TEST THAT HAS ONLY EVER PASSED IS INDISTINGUISHABLE FROM ONE WHOSE PROBES SILENTLY
DO NOTHING.** `ai-playbook` B.9, quoted in `tests/test_tripwire_registry.py`: *"a release gate
that has never gone red is only decorative."* So five documented rejections are disabled here,
one at a time, across four different check ladders, and each mutation must make the self-test
**fail, naming exactly the rows that stopped firing and no others**.

**Why the mutations are applied in-process rather than to a copy of the tree.** Three reasons,
all of them recorded failures of this project:

  * **INC-17** — running against another tree. An in-process patch cannot reach a different
    `whetstone_gate`, and :func:`test_the_tree_under_test_is_this_repository` pins
    ``whetstone_gate.__file__`` before anything else runs.
  * **INC-06 / INC-22** — throwaway work landing in the repository. Nothing is written to disk
    here at all, so there is no `s4.md` to leave behind (`REVIEW_C1_2.md` INFO-3 is the most
    recent instance of that class).
  * It is **stronger**, not weaker: patching the engine method removes the rejection for every
    caller, which is what editing the source would do, and the restore is guaranteed by
    ``monkeypatch`` rather than by remembering.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import whetstone_gate
from whetstone_gate.world import bounds, oracle as oracle_module, selftest, semantics


@pytest.fixture(scope="session")
def report() -> selftest.SelfTestReport:
    return selftest.run()


@pytest.fixture(scope="session")
def oracle():
    return oracle_module.load()


# ======================================================================================
# A. INC-17 — WHICH TREE IS UNDER TEST.
# ======================================================================================


def test_the_tree_under_test_is_this_repository(repo_root: Path) -> None:
    """⚠️ **INC-17, enforced rather than remembered.** Everything below patches
    `whetstone_gate.world`; if that resolved to another checkout, every mutation would be
    applied somewhere the assertions do not read."""
    package = Path(whetstone_gate.__file__).resolve()
    assert package == (repo_root / "src" / "whetstone_gate" / "__init__.py").resolve(), (
        f"whetstone_gate resolves to {package}, not to this repository's src/ tree"
    )
    assert Path(semantics.__file__).resolve().is_relative_to(package.parent)


# ======================================================================================
# B. GREEN, AND WHAT IT PRINTS.
# ======================================================================================


def test_the_self_test_passes(report: selftest.SelfTestReport) -> None:
    """⚠️ **The bar is the spike's: 26 PASS / 0 FAIL at zero cost.** This is 40 + 13."""
    assert report.ok, (
        "MUST-FIRE not fired: "
        + "; ".join(f"{rs}: {why}" for rs, why in report.not_fired)
        + " | MUST-HOLD not held: "
        + "; ".join(f"{rs}: {why}" for rs, why in report.not_held)
    )
    assert not report.not_fired
    assert not report.not_held


def test_the_three_printed_numbers_are_the_oracles_own(
    report: selftest.SelfTestReport, oracle
) -> None:
    """⚠️ **The denominators are PARSED, never transcribed.** A list of forty ids typed into a
    test would drift the first time a label moved and would still print `40 / 40`."""
    counts = oracle.counts()
    assert (report.must_fire_total, len(report.fired)) == (
        counts[oracle_module.MUST_FIRE],
        counts[oracle_module.MUST_FIRE],
    )
    assert (report.must_hold_total, len(report.held)) == (
        counts[oracle_module.MUST_HOLD],
        counts[oracle_module.MUST_HOLD],
    )
    assert (report.recorded_total, len(report.recorded)) == (
        counts[oracle_module.RECORDED],
        counts[oracle_module.RECORDED],
    )
    assert sum(counts.values()) == len(oracle.rows)


def test_every_recorded_row_is_listed_by_id_WITH_ITS_REASON(
    report: selftest.SelfTestReport, oracle
) -> None:
    """⚠️ **Q-018's ruling, verbatim: the excluded set is *"a PRINTED NUMBER — hard rule 11's
    shape applied to a denominator of documented rules"*.** *"Listing them is the point: a
    reader can see exactly what was documented and deliberately not modelled, instead of
    inferring it from an absence."*"""
    printed = selftest.render(report)
    for row in oracle.labelled(oracle_module.RECORDED):
        assert row.rs_id in printed, f"{row.rs_id} is not listed in the output"
        assert row.reason.strip(), f"{row.rs_id} carries no reason in the oracle"
        head = " ".join(row.reason.split())[:40]
        assert head in printed, f"{row.rs_id}'s reason is not printed"


def test_the_render_prints_the_three_numbers_and_the_verdict(
    report: selftest.SelfTestReport
) -> None:
    printed = selftest.render(report)
    assert f"MUST-FIRE fired : {len(report.fired)} / {report.must_fire_total}" in printed
    assert f"MUST-HOLD held  : {len(report.held)} / {report.must_hold_total}" in printed
    assert f"RECORDED listed : {len(report.recorded)} / {report.recorded_total}" in printed
    assert printed.rstrip().endswith("RESULT: PASS")


def test_the_boundary_only_rows_are_printed_as_a_counted_set_with_their_reasons(
    report: selftest.SelfTestReport
) -> None:
    """⚠️ **THE SIX MUST-FIRE ROWS NO TOOL CAN REACH, PRINTED RATHER THAN LEFT SILENT.**

    §0's `MUST-FIRE` definition says *"the five-tool surface can trigger it"*; `PROCESS.md`'s
    done-when says *"fires in the mock world"*. For RS-07, RS-08, RS-09, RS-10, RS-31 and
    RS-40 those two sentences disagree, because **RS-12 requires both that the world model
    `X-Refund-Idempotency` and that `create_refund` expose no way to set it**, and RS-69
    records that `settlements.go` declares no `currency`. The world satisfies the done-when and
    **prints the disagreement**. `QUESTIONS.md` Q-041.
    """
    printed = selftest.render(report)
    assert set(dict(report.boundary_only)) == set(semantics.BOUNDARY_ONLY_ROWS)
    assert len(report.boundary_only) == 6
    for rs_id, why in report.boundary_only:
        assert rs_id in printed and why[:30] in printed
        assert rs_id in dict(report.fired), (
            f"{rs_id} is declared boundary-only but did not fire — the set is a claim about "
            f"reachability, not an excuse for a row that does not work"
        )


def test_the_self_test_spends_nothing_and_records_that_it_did(
    report: selftest.SelfTestReport
) -> None:
    """`PROCESS.md` §8: *"if the harness is broken, it fails for free."* The world imports no
    model client — `tests/test_c2_world.py` asserts that over the transitive closure — and this
    check makes the *"zero tokens"* claim part of the printed output."""
    printed = selftest.render(report)
    assert "ZERO provider calls" in printed and "ZERO tokens" in printed
    assert any("no token was spent" in note for note in report.notes)


def test_the_entry_point_returns_zero_when_green(capsys) -> None:
    """``python -m whetstone_gate.world.selftest`` — the named target, exit 0 on PASS."""
    assert selftest.main() == 0
    assert "RESULT: PASS" in capsys.readouterr().out


def test_the_bounds_are_re_verified_against_the_oracle_on_every_run(
    report: selftest.SelfTestReport
) -> None:
    assert len(report.bounds_checked) == len(bounds.BOUNDS) + len(bounds.VOCABULARY)


def test_the_seed_it_used_for_rs26_is_not_the_default_one_and_that_is_expected(
    report: selftest.SelfTestReport
) -> None:
    """⚠️ **RS-26 is UNREACHABLE on seed 2001, and `CONTEXT.md` §8.6a says why in its own words.**

    *"Across seeds 2001–2050 this design admits an E2 breach (the ₹2,00,000 episode cap) by
    refunds alone in 46 of 50 seeds … SEED 2001 IS ONE OF THE FOUR THAT CANNOT."* The self-test
    therefore searches the configured seed list for the first seed on which a payment's
    refundable amount can outrun the merchant balance, and it **prints which seeds it used** so
    the choice is visible rather than buried.
    """
    assert len(report.seeds_used) >= 2, (
        "the self-test used a single seed, which means the RS-26 probe found seed 2001 "
        "sufficient — check the arithmetic in `_Harness.seed_where_refunds_outrun_the_balance`"
    )
    assert "Seeds used:" in selftest.render(report)


# ======================================================================================
# C. ⚠️ IT MUST BE ABLE TO GO RED. FIVE MUTATIONS, FOUR LADDERS.
# ======================================================================================


def _rows_that_stopped_firing(report: selftest.SelfTestReport) -> set[str]:
    return {rs_id for rs_id, _ in report.not_fired}


def test_disabling_the_extra_field_refusal_makes_the_self_test_name_rs53(monkeypatch) -> None:
    """⚠️ **INC-02's `destination`, silently accepted.** The single most consequential mutation
    in this file: with RS-53 disabled, a policy-blind attacker inventing a parameter Razorpay
    does not have is **ignored rather than refused**, which is the ₹2,004-crore fiction's exact
    shape. The self-test must say so, by name."""
    monkeypatch.setattr(
        semantics.MockWorld, "_reject_extra", lambda self, tool, arguments: None
    )
    report = selftest.run()
    assert not report.ok
    assert _rows_that_stopped_firing(report) == {"RS-53"}
    assert "RESULT: FAIL" in selftest.render(report)
    assert "FAIL RS-53" in selftest.render(report)


def test_disabling_the_notes_validation_makes_the_self_test_name_rs43(monkeypatch) -> None:
    """The refund ladder."""
    monkeypatch.setattr(semantics, "_notes_are_invalid", lambda notes: False)
    report = selftest.run()
    assert not report.ok
    assert _rows_that_stopped_firing(report) == {"RS-43"}


def test_disabling_the_idempotency_layer_makes_the_self_test_name_all_five_rows(
    monkeypatch
) -> None:
    """⚠️ **Five rows at once, which is the proof that the boundary-only set is really
    exercised** rather than declared and skipped. RS-07, RS-08, RS-09, RS-10 and RS-31 all key
    off `X-Refund-Idempotency`, which RS-12 requires the world to model and the tool never to
    send."""
    monkeypatch.setattr(
        semantics.MockWorld, "_check_idempotency", lambda self, key, body: None
    )
    report = selftest.run()
    assert not report.ok
    assert _rows_that_stopped_firing(report) == {"RS-07", "RS-08", "RS-09", "RS-10", "RS-31"}
    assert "RS-40" not in _rows_that_stopped_firing(report), (
        "RS-40 is boundary-only for a DIFFERENT reason — settlements.go declares no currency — "
        "and must not move with the idempotency layer"
    )


def test_relaxing_the_documented_key_length_makes_the_self_test_name_rs07(
    monkeypatch
) -> None:
    """A **bound** mutation rather than a method one: RS-05's documented minimum is what RS-07
    refuses against, and a world that stopped enforcing it would still look correct."""
    monkeypatch.setattr(bounds, "IDEMPOTENCY_KEY_MINIMUM_CHARS", 1)
    report = selftest.run()
    assert not report.ok
    assert _rows_that_stopped_firing(report) == {"RS-07"}


def test_relaxing_the_post_fee_net_floor_makes_the_self_test_name_rs39(monkeypatch) -> None:
    """The settlement ladder, and the one row that couples the fee arithmetic to a rejection —
    *"so the world's fee computation is observable at the boundary rather than only in the harm
    vector"* (RS-39's own Notes)."""
    monkeypatch.setattr(bounds, "SETTLEMENT_NET_MINIMUM_PAISE", 0)
    report = selftest.run()
    assert not report.ok
    assert _rows_that_stopped_firing(report) == {"RS-39"}


def test_the_self_test_is_green_again_after_every_mutation_is_undone() -> None:
    """``monkeypatch`` restores on teardown; this is the check that it did.

    ⚠️ A mutation harness that leaks its mutation turns every later test in the session into a
    test of the mutant. `REVIEW_C1_2.md` records that C1's harness *"restores after every
    mutant"* and prints an empty `git status`; this is the in-process equivalent.
    """
    report = selftest.run()
    assert report.ok
    assert len(report.fired) == report.must_fire_total
    assert len(report.held) == report.must_hold_total


def test_a_missing_probe_is_reported_as_a_failure_not_as_a_pass(monkeypatch) -> None:
    """⚠️ **The failure mode a self-test is most likely to have.** If a `MUST-FIRE` row had no
    probe, a naive implementation would iterate its probes and print `39 / 39`. This one
    iterates **the oracle** and reports the row as not fired, so the denominator cannot shrink
    to match the check (hard rule 11)."""
    probes = dict(selftest._FIRE_PROBES)
    removed = probes.pop("RS-27")
    monkeypatch.setattr(selftest, "_FIRE_PROBES", probes)
    report = selftest.run()
    assert not report.ok
    assert _rows_that_stopped_firing(report) == {"RS-27"}
    assert report.must_fire_total == 40, "the denominator moved with the check"
    assert "NO PROBE EXISTS" in dict(report.not_fired)["RS-27"]
    assert removed is not None
