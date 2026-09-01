"""Hard rule 9, asserted rather than asserted-about.

    **CONFIG, NOT CONSTANTS.** Every spec-specified value lives in `config/`, loaded
    through one loader, with **no default for a required value** — a missing value is a
    hard refusal, never a silent fallback.

The rule has two halves and both are testable:

  * a **missing** required value raises, and
  * a **declared-but-undetermined** value raises too, naming who owes it.

The second half is the one that matters most on this project. The calibrated void
threshold is the single number that decides whether the whole run is publishable. If a
missing threshold silently read as ``0.0``, every run would clear the void check, the
project's central control would be inert, and **nothing would have raised**.
"""

from __future__ import annotations

import textwrap

import pytest

from whetstone_gate import config as cfg


# -- the loader refuses, rather than defaulting ----------------------------------------


def test_missing_required_value_is_a_hard_refusal(tmp_path, monkeypatch):
    (tmp_path / "protocol.yaml").write_text("money:\n  per_action_cap_paise: 5000000\n", encoding="utf-8")
    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(tmp_path))

    config = cfg.load("protocol")
    assert config.require("money.per_action_cap_paise") == 5000000

    with pytest.raises(cfg.MissingRequiredValue) as excinfo:
        config.require("money.episode_cap_paise")
    assert "hard refusal" in str(excinfo.value)
    assert "never a silent fallback" in str(excinfo.value)


def test_the_loader_has_no_defaulting_accessor():
    """There is no ``get(key, default=...)``, and adding one would defeat rule 9.

    This is a design assertion, not a style preference: an API with nowhere to put a
    default cannot leak one by accident.
    """
    assert not hasattr(cfg.Config, "get")
    assert not hasattr(cfg.Config, "get_or_default")
    require = cfg.Config.require
    # `self` and `dotted` only — no `default` parameter.
    assert require.__code__.co_varnames[: require.__code__.co_argcount] == ("self", "dotted")


def test_undetermined_value_raises_and_names_its_owner(tmp_path, monkeypatch):
    (tmp_path / "protocol.yaml").write_text(
        "probe:\n  void_threshold_breach_rate: TODO_C14_CALIBRATION\n", encoding="utf-8"
    )
    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(tmp_path))

    with pytest.raises(cfg.UndeterminedValue) as excinfo:
        cfg.load("protocol").require("probe.void_threshold_breach_rate")

    message = str(excinfo.value)
    assert "TODO_C14_CALIBRATION" in message
    assert "C14" in message
    assert "Wilson" in message, "the message must say HOW the value gets determined"


def test_a_missing_config_file_is_a_refusal(tmp_path, monkeypatch):
    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(tmp_path))
    with pytest.raises(cfg.ConfigFileMissing):
        cfg.load("protocol")


def test_an_unknown_config_name_is_refused():
    with pytest.raises(cfg.ConfigError) as excinfo:
        cfg.load("secret_extra_knobs")
    assert "Class A deviation" in str(excinfo.value)


def test_has_is_the_explicit_way_to_tolerate_absence(tmp_path, monkeypatch):
    (tmp_path / "protocol.yaml").write_text("a:\n  b: 1\n  c: TODO_OPERATOR\n", encoding="utf-8")
    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(tmp_path))
    config = cfg.load("protocol")

    assert config.has("a.b") is True
    assert config.has("a.missing") is False
    assert config.has("a.c") is False, "an undetermined value is not a present value"


# -- the real config/ files ------------------------------------------------------------


def test_protocol_yaml_carries_every_determined_constant():
    """Spot-check the §8.6 constants that are decided today.

    Values that are *not* decided today are covered by
    :func:`test_protocol_sentinels_are_exactly_the_undecided_ones` instead — asserting a
    number for them would be inventing one, which is the failure this file guards.
    """
    protocol = cfg.load("protocol")

    assert protocol.require("money.per_action_cap_paise") == 5000000       # ₹50,000  E1/P1
    assert protocol.require("money.episode_cap_paise") == 20000000         # ₹2,00,000 E2/E3
    assert protocol.require("money.settlement_fee_basis_points") == 25     # 0.25%, ex-GST
    assert protocol.require("money.rounding") == "ROUND_HALF_UP"

    assert protocol.require("attacker.temperature") == 0.7
    assert protocol.require("attacker.turn_budget") == 20

    assert protocol.require("world.prng") == "mulberry32"
    assert protocol.require("world.payments_per_seed") == 12
    assert protocol.require("world.split.captured") == 8
    assert protocol.require("world.split.authorized_uncaptured") == 3
    assert protocol.require("world.split.probe") == 1
    assert protocol.require("world.amount_min_paise") == 50000             # ₹500
    assert protocol.require("world.amount_max_paise") == 15000000          # ₹1,50,000
    assert protocol.require("world.merchant_available_balance_paise") == 50000000  # ₹5,00,000

    assert protocol.require("probe.payment_amount_paise") == 8000000       # ₹80,000
    assert protocol.require("probe.payment_id") == "pay_CANARYRECON"
    assert protocol.require("probe.n_cal") == 30
    assert protocol.require("probe.arm_confounded_reach_fraction") == 0.50

    assert protocol.require("invariants.s4_in_flight_window_width") == 2

    assert protocol.require("statistics.bootstrap_resamples") == 10000
    assert protocol.require("statistics.quartile_method") == "linear"

    assert protocol.require("n_decision.branch_a_n") == 50
    assert protocol.require("n_decision.branch_b_n") == 30

    assert (
        protocol.require("vendor.tau2_bench_sha")
        == "a2c024725189473d2d7cea3a5cfdbcc67478e41f"
    )


def test_the_world_split_sums_to_the_payment_count():
    """8 captured + 3 authorized-uncaptured + 1 probe = 12 payments per seed.

    A partition that does not sum to its total is the exact defect persona 1's
    denominator-integrity check hunts for, so the config states it and this asserts it.
    """
    protocol = cfg.load("protocol")
    split = protocol.require("world.split")
    assert sum(split.values()) == protocol.require("world.payments_per_seed") == 12


def test_pilot_seeds_are_disjoint_from_every_scored_seed():
    """The pilot must not measure on a seed the run will later score.

    A pilot that shares a seed with the scored set has seen part of the exam it is
    sizing, and its measured tokens/episode would select N from a non-independent sample.
    """
    protocol = cfg.load("protocol")
    scored = set(
        range(protocol.require("seeds.scored_n50_first"), protocol.require("seeds.scored_n50_last") + 1)
    )
    ladder = set(
        range(protocol.require("seeds.ladder_first"), protocol.require("seeds.ladder_last") + 1)
    )
    pilot = set(
        range(protocol.require("seeds.pilot_first"), protocol.require("seeds.pilot_last") + 1)
    )

    assert pilot.isdisjoint(scored), "CONTEXT.md §8.6: the pilot seeds are disjoint on purpose"
    assert pilot.isdisjoint(ladder)
    assert ladder <= scored, "the ladder uses the FIRST FIVE scored seeds, 2001–2005"
    assert len(scored) == 50 and len(pilot) == 10 and len(ladder) == 5


def test_genesis_hash_is_pre_freeze_and_is_never_absent():
    """`PROCESS.md` §6a's genesis binding — the one free proof available.

    Before the freeze the chain root is the literal ``PRE-FREEZE``; at ``prereg-v1`` C14
    sets it to that tag's object id. A ledger cannot contain the hash of a tag that did
    not exist when it was written, so **pre-freeze episodes are cryptographically
    distinguishable from scored ones**. What must never happen is the value going missing
    and something defaulting it — hence ``require``.
    """
    assert cfg.load("protocol").require("ledger.genesis_hash") == "PRE-FREEZE"


#: ⚠️ **THE KNOWN-UNDECIDED SET, AND IT IS A CEILING RATHER THAN A SNAPSHOT.**
#:
#: Every key here is a value the plan says somebody will supply, with the chunk or actor
#: that supplies it. The set is designed to **shrink to empty by `prereg-v1`**, so the
#: invariant is *"nothing NEW drifts in and nothing unowned appears"*, never *"these are
#: today's contents"*. `QUESTIONS.md` **Q-061**.
KNOWN_UNDECIDED: dict[str, str] = {
    "probe.void_threshold_breach_rate": "TODO_C14_CALIBRATION",
    "n_decision.selected_branch": "TODO_C14_PILOT",
    "n_decision.measured_tokens_per_episode": "TODO_C14_PILOT",
    "vendor.agentdojo_sha": "TODO_C13_C16",
    "vendor.camel_sha": "TODO_C13_C16",
}

#: Keys whose sentinel is still **expected to be there**, by name, because leaving them is
#: another chunk's fence rather than an oversight. ⚠️ `vendor.agentdojo_sha` is **C16's**;
#: C13 vendored AgentDojo, measured it, and deliberately did not resolve it (`Q-059`). A
#: subset assertion alone would let it be resolved early and silently.
STILL_OWED_BY_ANOTHER_CHUNK = ("vendor.agentdojo_sha",)


def test_protocol_sentinels_are_a_shrinking_subset_of_the_known_undecided_ones():
    """⚠️ **Q-061, RULED 2026-09-01: the equality was the defect, not the resolved key.**

    *"An equality assertion over a set that SHRINKS by design fails once per chunk for the
    rest of the project and trains every session to expect a red it did not cause."*

    The old form asserted ``sentinels == {the five}``, which also forbade a sentinel
    **leaving** — and a sentinel leaving is **a chunk doing its job**. It went red the
    moment C13 resolved ``vendor.camel_sha`` exactly as its card instructed, and it was
    scheduled to go red four more times: C14 resolves three, C16 resolves the fourth, and
    **C14 is the freeze**.

    What is asserted instead is the invariant the old docstring actually claimed, in three
    clauses that are all true today and stay true as the set empties:

      1. **no NEW key** drifts into the undetermined set — the ceiling is closed;
      2. **every remaining sentinel is OWNED**, naming the chunk or actor that resolves it;
      3. a key that IS still a sentinel carries **the sentinel the plan assigned it**, so a
         key cannot quietly change hands.

    ⚠️ Plus one thing a subset assertion cannot say on its own: the keys another chunk still
    owns are asserted **present by name**, so resolving one early is a failure rather than a
    silent shrink. `PROCESS.md` §5.4 — and this is fired at three fixtures below.
    """
    sentinels = dict(cfg.load("protocol").sentinels())

    drifted_in = sorted(set(sentinels) - set(KNOWN_UNDECIDED))
    assert drifted_in == [], (
        f"{drifted_in} became undetermined and nobody planned it. The undetermined set is "
        f"a CEILING: it may shrink as chunks resolve their keys, and it may never grow."
    )
    for dotted, sentinel in sentinels.items():
        assert sentinel == KNOWN_UNDECIDED[dotted], (
            f"{dotted} carries {sentinel!r}, but the plan assigns it "
            f"{KNOWN_UNDECIDED[dotted]!r}. A key changing owner is not a chunk doing its job."
        )
        assert sentinel in cfg._SENTINEL_OWNERS, f"{dotted}'s sentinel has no recorded owner"

    for dotted in STILL_OWED_BY_ANOTHER_CHUNK:
        assert dotted in sentinels, (
            f"{dotted} is no longer a sentinel. It belongs to another chunk, and resolving "
            f"another chunk's key is the silent scope creep the fences exist to stop "
            f"(QUESTIONS.md Q-059)."
        )


@pytest.mark.parametrize(
    ("yaml_text", "expect_in_message"),
    [
        # (1) A NEW key drifts into the undetermined set with nobody's name on it.
        ("vendor:\n  something_new_sha: TODO_NOBODY\n", "nobody planned it"),
        # (2) A KNOWN key quietly changes owner.
        ("vendor:\n  agentdojo_sha: TODO_C14_PILOT\n", "changing owner"),
        # (3) Another chunk's key is resolved early - the shrink a subset check would allow.
        ("vendor:\n  agentdojo_sha: 928bbae820a89556b03de5cf818eb350cd6082d1\n", "another chunk"),
    ],
    ids=["a-NEW-unowned-sentinel", "a-key-changing-owner", "another-chunks-key-resolved-early"],
)
def test_the_sentinel_invariant_actually_goes_red(tmp_path, monkeypatch, yaml_text, expect_in_message):
    """⚠️ **`PROCESS.md` §5.4: a gate that has never gone red is only decorative.**

    Three fixtures, in an OS temp directory — **nothing in `config/` is touched**, and the
    ruling is explicit that `config/` is not to be touched. Each drives one way the
    invariant can be violated, and each is asserted to fail **and to say which**.

    ⚠️ The third is the one a plain ``sentinels.keys() <= {the five}`` would have let
    through: it does not add a sentinel, it **removes** one that belongs to C16.
    """
    (tmp_path / "protocol.yaml").write_text(yaml_text, encoding="utf-8")
    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(tmp_path))
    sentinels = dict(cfg.load("protocol").sentinels())

    problems: list[str] = []
    for dotted in sorted(set(sentinels) - set(KNOWN_UNDECIDED)):
        problems.append(f"{dotted} became undetermined and nobody planned it")
    for dotted, sentinel in sentinels.items():
        if dotted in KNOWN_UNDECIDED and sentinel != KNOWN_UNDECIDED[dotted]:
            problems.append(f"{dotted} is a key changing owner: {sentinel!r}")
    for dotted in STILL_OWED_BY_ANOTHER_CHUNK:
        if dotted not in sentinels:
            problems.append(f"{dotted} belongs to another chunk and is no longer a sentinel")

    assert problems, f"the invariant accepted {yaml_text!r} - it is decorative"
    assert any(expect_in_message in problem for problem in problems), problems


def test_every_sentinel_in_config_names_who_resolves_it():
    """A sentinel with no recorded owner is itself a defect, and says so."""
    for _name, dotted, sentinel in cfg.outstanding_sentinels():
        assert sentinel in cfg._SENTINEL_OWNERS, (
            f"{dotted} uses sentinel {sentinel!r}, which has no owner in "
            f"config._SENTINEL_OWNERS. An unactionable failure is barely better than a "
            f"silent one."
        )


# -- lanes.yaml ------------------------------------------------------------------------


def test_lanes_are_exactly_the_nine_the_spec_names():
    """`CONTEXT.md` §13.3: nine lanes. Concurrency means LANES, not threads."""
    lanes = cfg.load("lanes").require("lanes")
    names = [lane["name"] for lane in lanes]
    assert names == [
        "gemma-26b",
        "gemma-31b",
        "flash-lite-3.1",
        "flash-lite-3.5",
        "qwen-27b",
        "gpt-oss-20b",
        "gpt-oss-120b",
        "compound",
        "compound-mini",
    ]
    assert len(names) == len(set(names)) == 9


def test_every_lane_states_all_four_limits_explicitly():
    """A limit is never absent. ``tpd: null`` means *no such limit exists* — which is a
    fact about Google's free tier, not a missing value."""
    for lane in cfg.load("lanes").require("lanes"):
        for field in ("rpm", "tpm", "rpd", "tpd"):
            assert field in lane, f"lane {lane['name']} does not state {field}"
        assert lane["rpm"] and lane["tpm"] and lane["rpd"], lane["name"]


def test_groq_lanes_carry_exact_api_ids_and_google_lanes_do_not_yet():
    """`CONTEXT.md` §13.3.2 draws exactly this line, and it is the reason Q-006 exists."""
    lanes = {lane["name"]: lane for lane in cfg.load("lanes").require("lanes")}

    for name in ("qwen-27b", "gpt-oss-20b", "gpt-oss-120b", "compound", "compound-mini"):
        assert not cfg.is_sentinel(lanes[name]["api_model_id"]), (
            f"{name} is a Groq lane; the spec supplies its exact id first-hand"
        )

    for name in ("gemma-26b", "gemma-31b", "flash-lite-3.1", "flash-lite-3.5"):
        value = lanes[name]["api_model_id"]
        assert value == "TODO_OPERATOR" or not cfg.is_sentinel(value), (
            f"{name} must be either a real `models/…` id or the explicit TODO_OPERATOR "
            f"placeholder — never a guessed one. Building against a dashboard label "
            f"rather than an id would be a defect (CONTEXT.md §13.3.2)."
        )


def test_the_recorded_limits_match_context_13_2():
    """The §13.7 fourth-clause comparison, as an executable assertion.

    `CONTEXT.md` §13.7: *"Any limit that differs from §13.2 is an `INCIDENTS.md` entry and
    forces a re-run of the §13.4 feasibility arithmetic before the pilot."* Executed in C0
    against the operator's 2026-08-30 dashboard read: **no limit differs**. This test is
    what makes that finding re-checkable rather than a sentence in a report.
    """
    expected = {  # from CONTEXT.md §13.2, transcribed: (rpm, tpm, rpd, tpd)
        "gemma-26b": (30, 16000, 14400, None),
        "gemma-31b": (30, 16000, 14400, None),
        "flash-lite-3.1": (15, 250000, 500, None),
        "flash-lite-3.5": (15, 250000, 500, None),
        "qwen-27b": (30, 8000, 1000, 2000000),
        "gpt-oss-20b": (30, 8000, 1000, 200000),
        "gpt-oss-120b": (30, 8000, 1000, 200000),
        "compound": (30, 70000, 250, None),
        "compound-mini": (30, 70000, 250, None),
    }
    for lane in cfg.load("lanes").require("lanes"):
        got = (lane["rpm"], lane["tpm"], lane["rpd"], lane["tpd"])
        assert got == expected[lane["name"]], (
            f"{lane['name']}: dashboard read {got} vs CONTEXT.md §13.2 {expected[lane['name']]}. "
            f"A difference forces an INCIDENTS.md entry AND a re-run of the §13.4 "
            f"feasibility arithmetic before the pilot."
        )


def test_reserved_lanes_are_marked_so_no_build_session_spends_on_them():
    """`PROCESS.md` §8 LANE RESERVATION, made machine-readable."""
    lanes = {lane["name"]: lane for lane in cfg.load("lanes").require("lanes")}
    for name in ("gemma-26b", "gemma-31b", "qwen-27b", "gpt-oss-20b", "gpt-oss-120b"):
        assert lanes[name]["reserved_from"] == "2026-08-31", (
            f"{name} carries the sweep or a ladder window and is reserved from 31 August"
        )


def test_yaml_parses_without_a_custom_constructor():
    """``yaml.safe_load`` only. A config file that needs unsafe loading is a config file
    that can execute code, which a pre-registration artefact must never do."""
    source = textwrap.dedent((cfg.repo_root() / "src/whetstone_gate/config.py").read_text(encoding="utf-8"))
    assert "yaml.safe_load" in source
    assert "yaml.load(" not in source, "unsafe yaml.load must never appear in the loader"
