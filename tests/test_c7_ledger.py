"""C7 — the append-only, hash-chained ledger, against golden 5 and against the properties.

**What this file checks that golden 5 does not.** Golden 5 pins four chains and their verdicts.
It does not show that the **writer** produces those bytes from those inputs, that a missing
``ledger.genesis_hash`` is a refusal rather than a default, that the API has no second write
path, that an arm cannot emit a verdict `CONTEXT.md` §8.6a does not give it, that **every** log
row becomes an entry including the one the tool layer refused, or that nothing in the package
reads a clock. Those are properties, and they are asserted here.

⚠️ **Nothing here transcribes `CONTEXT.md` or `config/`.** §8.6a's verdict-set sentence is
**parsed** out of the specification, the genesis root and the hash algorithm are loaded through
the one loader, and golden 5 is read as bytes and compared against its own git blob — so every
assertion is against the artefact rather than against a copy of it.

⚠️ **THE DEFECTIVE VERIFIER IS IMPLEMENTED HERE, IN THE TESTS, AND NOWHERE ELSE.**
`PROCESS.md` §5.2 names one mutation golden 5 exists to catch — *"a verifier that compares
stored fields instead of recomputing the previous entry's digest passes this and must not"* —
and golden 5 records, per case, what that verifier returns. :func:`_stored_field_verifier` is
that verifier. It is written so the difference between it and
:func:`whetstone_gate.ledger.chain.verify` is **measured on all four cases** rather than
asserted about the shipped code's intentions.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest

from whetstone_gate import config as cfg
from whetstone_gate.ledger import build, chain, store
from whetstone_gate.ledger import entry as entry_mod
from whetstone_gate.ledger.entry import (
    ALLOWED,
    ARM_1,
    ARM_4,
    ARMS,
    CHAIN_FIELDS,
    CONTENT_FIELDS,
    DENIED,
    INDETERMINATE,
    NO_TARGET,
    VERDICTS,
    VERDICTS_BY_ARM,
    LedgerEntry,
    LedgerEntryError,
)
from whetstone_gate.world import generator, harm, oracle as oracle_module, semantics, settings
from whetstone_gate.world import surface
from whetstone_gate.world.spec import load_world_spec

GOLDEN_PATH = "tests/goldens/golden5_tamper.json"


# ======================================================================================
# Fixtures.
# ======================================================================================


@pytest.fixture(scope="session")
def protocol() -> cfg.Config:
    return cfg.load("protocol")


@pytest.fixture(scope="session")
def spec(protocol: cfg.Config) -> chain.ChainSpec:
    return chain.load_chain_spec(protocol)


@pytest.fixture(scope="session")
def golden(repo_root: Path) -> dict:
    return json.loads((repo_root / GOLDEN_PATH).read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def context_md(repo_root: Path) -> str:
    return (repo_root / "CONTEXT.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def ledger_modules(repo_root: Path) -> list[Path]:
    files = sorted((repo_root / "src" / "whetstone_gate" / "ledger").glob("*.py"))
    assert files, "the ledger package has no modules — this scan would pass over nothing"
    return files


@pytest.fixture(scope="session")
def core_modules(ledger_modules: list[Path]) -> list[Path]:
    """The package minus its one shell. Hard rule 8's *"side effects live in a thin outer
    shell"* is only a claim if the line is drawn somewhere a test can see it."""
    core = [p for p in ledger_modules if p.name != "store.py"]
    assert len(core) == len(ledger_modules) - 1, "store.py is the shell and must exist"
    return core


@pytest.fixture()
def world(protocol: cfg.Config):
    world_spec = load_world_spec(protocol)
    semantics_spec = settings.load_semantics_spec(protocol)
    seed = protocol.require("seeds.scored_n50_first")
    return semantics.build(
        generator.generate(seed, world_spec), semantics_spec, oracle_module.load()
    )


@pytest.fixture()
def ledger(spec: chain.ChainSpec, protocol: cfg.Config) -> chain.Ledger:
    return chain.Ledger(
        spec=spec, seed=protocol.require("seeds.scored_n50_first"), arm=ARM_1
    )


def _content(**overrides: Any) -> dict[str, Any]:
    """One valid set of append arguments, for tests that vary exactly one thing."""
    fields: dict[str, Any] = {
        "turn_index": 0,
        "verdict": ALLOWED,
        "tool": surface.CREATE_REFUND,
        "target": NO_TARGET,
        "amount_paise": 1,
        "a_class": None,
        "rejected_by_razorpay": False,
    }
    for component in harm.COMPONENTS:
        fields[component] = 0
    fields.update(overrides)
    return fields


# ======================================================================================
# A. GOLDEN 5 IS THE ORACLE.
# ======================================================================================


def test_the_golden_is_the_byte_for_byte_file_the_architect_authored(repo_root: Path) -> None:
    """Hard rule 3: *"a build session may READ them and may NEVER EDIT them."*

    Asserted against the **git blob** rather than against a transcribed digest, so the check
    keeps working when the architect lands a further golden and cannot be satisfied by
    updating a constant in this file.
    """
    blob = subprocess.run(
        ["git", "show", f"HEAD:{GOLDEN_PATH}"],
        cwd=repo_root,
        capture_output=True,
        check=True,
    ).stdout
    assert (repo_root / GOLDEN_PATH).read_bytes() == blob, (
        "the golden in the working tree differs from the one committed at HEAD. A build "
        "session may never edit a golden (hard rule 3)."
    )


def test_the_goldens_hash_rule_is_the_rule_this_package_implements(golden: dict) -> None:
    """The golden states the rule in a field of its own; this reads it rather than assuming it."""
    rule = golden["hash_rule"]
    assert "sorted keys" in rule
    assert "no whitespace" in rule
    assert "UTF-8" in rule
    excluded = re.search(r"EXCLUDES ([a-z_]+) and ([a-z_]+)", rule)
    assert excluded, f"the golden's hash_rule no longer names the excluded fields: {rule!r}"
    assert set(excluded.groups()) == set(CHAIN_FIELDS)


def test_the_entry_field_set_is_exactly_the_one_golden_5_carries(golden: dict) -> None:
    """⚠️ Every content field is inside the digest, so the set is closed by arithmetic: a
    fourteenth would change all twelve of golden 5's hashes."""
    for case in golden["cases"]:
        for stored in case["ledger"]:
            assert list(stored) == list(CONTENT_FIELDS) + list(CHAIN_FIELDS), (
                f"case {case['case']} entry {stored.get('ledger_seq')} does not carry this "
                f"package's field set, in this order"
            )


@pytest.mark.parametrize("case_id", ["A", "B", "C", "D"])
def test_all_four_golden_5_cases_reproduce_verdict_and_first_bad_seq(
    golden: dict, spec: chain.ChainSpec, case_id: str
) -> None:
    """⚠️ **The whole of C7's done-when, and the golden is right if we disagree.**

    **A** intact → VALID. **B** the CONTROL, the link broken outright → DETECTED at 2; without
    it a verifier that always returned DETECTED would pass every other case. **C** and **D**
    are two distinct alterations, each at the seq the golden names, and each is invisible to a
    verifier that compares stored fields.
    """
    case = next(c for c in golden["cases"] if c["case"] == case_id)
    verdict = chain.verify(
        case["ledger"],
        genesis_hash=golden["genesis_hash"],
        algorithm=spec.algorithm,
    )
    assert verdict.verdict == case["expected_verdict"], case["description"]
    assert verdict.first_bad_ledger_seq == case["expected_first_bad_ledger_seq"], (
        f"case {case_id} ({case['description']}): first bad ledger_seq"
    )


def _stored_field_verifier(entries: list[dict], *, genesis_hash: str) -> tuple[str, int | None]:
    """⚠️ **THE SEEDED DEFECT OF `PROCESS.md` §5.4, IMPLEMENTED IN A TEST AND NOWHERE ELSE.**

    It compares each entry's stored ``prev_hash`` to the previous entry's stored ``hash`` field
    and never recomputes the previous entry's digest from its contents. Golden 5 records what
    it returns on each case; this is how that record is checked.
    """
    expected_prev = genesis_hash
    for stored in entries:
        if stored["prev_hash"] != expected_prev:
            return (chain.DETECTED, stored["ledger_seq"])
        expected_prev = stored["hash"]
    return (chain.VALID, None)


@pytest.mark.parametrize("case_id", ["A", "B", "C", "D"])
def test_the_stored_field_verifier_answers_exactly_what_the_golden_records(
    golden: dict, case_id: str
) -> None:
    """The golden's ``stored_field_verifier_returns`` is a claim about a verifier that does not
    exist in this repository. It is measured here so the claim is checkable."""
    case = next(c for c in golden["cases"] if c["case"] == case_id)
    verdict, _seq = _stored_field_verifier(
        case["ledger"], genesis_hash=golden["genesis_hash"]
    )
    assert verdict == case["stored_field_verifier_returns"], case["description"]


def test_the_control_fires_on_both_verifiers_and_exactly_two_cases_discriminate(
    golden: dict, spec: chain.ChainSpec
) -> None:
    """⚠️ **The control is what makes the other three cases mean anything.**

    Case B detects on **both** verifiers, so a reviewer can tell a defective verifier from one
    that always returns DETECTED. Cases C and D are where the two answers differ, and the
    golden marks exactly those two with ``discriminates_the_seeded_defect``.
    """
    discriminating = set()
    for case in golden["cases"]:
        ours = chain.verify(
            case["ledger"],
            genesis_hash=golden["genesis_hash"],
            algorithm=spec.algorithm,
        ).verdict
        theirs, _ = _stored_field_verifier(
            case["ledger"], genesis_hash=golden["genesis_hash"]
        )
        if ours != theirs:
            discriminating.add(case["case"])
        if case["case"] == "B":
            assert ours == chain.DETECTED and theirs == chain.DETECTED, (
                "the CONTROL must fire on both verifiers, or it is not a control"
            )

    marked = {c["case"] for c in golden["cases"] if c["discriminates_the_seeded_defect"]}
    assert discriminating == marked == {"C", "D"}, (
        f"the cases on which this verifier differs from a stored-field one are "
        f"{sorted(discriminating)}; the golden marks {sorted(marked)}"
    )


def test_the_writer_reproduces_golden_5_case_a_byte_for_byte(
    golden: dict, spec: chain.ChainSpec
) -> None:
    """⚠️ **Verifying the golden is half the claim; producing it is the other half.**

    A verifier can be right about somebody else's chain and this package still write a
    different one. Given case A's thirteen content fields per entry, ``append`` must produce
    the golden's ``prev_hash``, its ``hash`` **and** its key order — which is what pins the
    field set to thirteen rather than to "at least thirteen".
    """
    case = next(c for c in golden["cases"] if c["case"] == "A")
    written = chain.Ledger(spec=spec, seed=2001, arm=ARM_1)
    for stored in case["ledger"]:
        written.append(**{name: stored[name] for name in chain.APPEND_FIELDS})

    assert len(written) == len(case["ledger"])
    for produced, stored in zip(written.entries, case["ledger"]):
        assert produced.to_dict() == stored
        assert list(produced.to_dict()) == list(stored)
    assert written.head_hash == case["ledger"][-1]["hash"]


def test_the_genesis_the_golden_names_is_the_one_config_carries(
    golden: dict, spec: chain.ChainSpec
) -> None:
    """Today they agree. ⚠️ **C14 changes `config/` to the `prereg-v1` tag object id and this
    assertion is then expected to fail** — at which point golden 5 is a *pre-freeze* chain,
    which is the distinction `config/protocol.yaml`'s own comment exists to create. The test
    is written so that moment is loud rather than silent."""
    assert golden["genesis_hash"] == spec.genesis_hash, (
        "config/protocol.yaml's ledger.genesis_hash no longer matches golden 5's root. If "
        "C14 has run, this is expected and golden 5 is a pre-freeze artefact by construction; "
        "record it rather than editing either file."
    )


# ======================================================================================
# B. THE GENESIS BINDING — loaded, refused when absent, never cached at import.
# ======================================================================================


def _config_dir_without(tmp_path: Path, repo_root: Path, *, drop: str) -> Path:
    """A config/ fixture identical to the real one but with one ``ledger:`` key removed."""
    import yaml

    target = tmp_path / "config"
    target.mkdir()
    for name in ("protocol", "lanes"):
        source = repo_root / "config" / f"{name}.yaml"
        data = yaml.safe_load(source.read_text(encoding="utf-8"))
        if name == "protocol":
            data["ledger"].pop(drop)
        (target / f"{name}.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
        )
    return target


def test_a_missing_genesis_hash_in_config_is_a_hard_refusal_not_a_default(
    tmp_path: Path, repo_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⚠️ **Hard rule 9, on the one value that decides which run a ledger belongs to.**

    *"no default for a required value — a missing value is a hard refusal, never a silent
    fallback."* A ledger that fell back to some empty root would still chain, still verify
    against itself, and would be indistinguishable from a scored episode.
    """
    monkeypatch.setenv(
        "WHETSTONE_CONFIG_DIR",
        str(_config_dir_without(tmp_path, repo_root, drop="genesis_hash")),
    )
    with pytest.raises(cfg.MissingRequiredValue) as raised:
        chain.load_chain_spec()
    assert "ledger.genesis_hash" in str(raised.value)


def test_a_missing_hash_algorithm_in_config_is_a_hard_refusal_too(
    tmp_path: Path, repo_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(
        "WHETSTONE_CONFIG_DIR",
        str(_config_dir_without(tmp_path, repo_root, drop="hash_algorithm")),
    )
    with pytest.raises(cfg.MissingRequiredValue) as raised:
        chain.load_chain_spec()
    assert "ledger.hash_algorithm" in str(raised.value)


def _config_dir_with_genesis(tmp_path: Path, repo_root: Path, value: str, *, name: str) -> Path:
    import yaml

    target = tmp_path / name
    target.mkdir()
    for stem in ("protocol", "lanes"):
        data = yaml.safe_load((repo_root / "config" / f"{stem}.yaml").read_text("utf-8"))
        if stem == "protocol":
            data["ledger"]["genesis_hash"] = value
        (target / f"{stem}.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
        )
    return target


def test_the_genesis_root_is_re_read_on_every_call_and_never_cached_at_import(
    tmp_path: Path, repo_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⚠️ **C14 rewrites this value while the process may still be alive.**

    ``ledger.genesis_hash`` is ``PRE-FREEZE`` today and becomes the `prereg-v1` **tag object
    id** at the freeze, and *"a ledger cannot contain the hash of a tag that did not exist when
    it was written"* is the project's one free proof. A value captured at import would keep
    writing pre-freeze roots into scored episodes with nothing raising.
    """
    first = _config_dir_with_genesis(tmp_path, repo_root, "ROOT-BEFORE", name="a")
    second = _config_dir_with_genesis(tmp_path, repo_root, "ROOT-AFTER", name="b")

    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(first))
    assert chain.load_chain_spec().genesis_hash == "ROOT-BEFORE"
    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(second))
    assert chain.load_chain_spec().genesis_hash == "ROOT-AFTER"


def test_the_genesis_value_appears_in_no_string_literal_in_the_package(
    ledger_modules: list[Path], spec: chain.ChainSpec, repo_root: Path
) -> None:
    """Hard rule 9's tripwire, applied to a value that is not in `CONTEXT.md` §8.6's table.

    Docstrings are excluded: this module's prose **quotes** `config/protocol.yaml`'s comment,
    which is the documentation working. A non-docstring literal would be the defect.
    """
    findings: list[str] = []
    for path in ledger_modules:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        docstrings = {
            id(node.body[0].value)
            for node in ast.walk(tree)
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        }
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and node.value == spec.genesis_hash
                and id(node) not in docstrings
            ):
                findings.append(
                    f"{path.relative_to(repo_root).as_posix()}:{node.lineno}: "
                    f"the genesis root as a literal"
                )
    assert not findings, (
        "the genesis root is hardcoded in the package instead of being read from config/:\n  "
        + "\n  ".join(findings)
    )


def test_an_unavailable_hash_algorithm_is_a_refusal_not_a_substitution(
    tmp_path: Path, repo_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import yaml

    target = tmp_path / "bad-algorithm"
    target.mkdir()
    for stem in ("protocol", "lanes"):
        data = yaml.safe_load((repo_root / "config" / f"{stem}.yaml").read_text("utf-8"))
        if stem == "protocol":
            data["ledger"]["hash_algorithm"] = "not-a-digest"
        (target / f"{stem}.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
        )
    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(target))
    with pytest.raises(chain.ChainConfigError):
        chain.load_chain_spec()


def test_the_algorithm_is_read_from_config_rather_than_fixed_in_source(
    spec: chain.ChainSpec,
) -> None:
    """A second algorithm produces different digests, which is the check that the configured
    name is *used* rather than merely loaded and ignored."""
    body = {name: value for name, value in _content(turn_index=1).items()}
    body["ledger_seq"] = 1
    body["arm"] = ARM_1
    under_config = chain.entry_digest("ROOT", body, algorithm=spec.algorithm)
    under_other = chain.entry_digest("ROOT", body, algorithm="sha512")
    assert under_config != under_other
    assert len(under_config) != len(under_other)


# ======================================================================================
# C. APPEND-ONLY IN THE API, NOT MERELY BY CONVENTION.
# ======================================================================================

#: Every shape of "change something already written" a caller might reach for.
_MUTATOR_NAMES = (
    "update",
    "delete",
    "remove",
    "insert",
    "pop",
    "clear",
    "truncate",
    "replace",
    "set",
    "setitem",
    "delitem",
    "sort",
    "reverse",
    "extend",
    "amend",
    "rewrite",
    "edit",
)


def test_the_ledger_api_has_one_write_path_and_no_mutator(ledger: chain.Ledger) -> None:
    """⚠️ *"APPEND-ONLY IN THE API, not merely by convention."*

    ⚠️ **Scope, stated so the claim is not larger than the check.** This walks the names the
    class **itself** defines — ``vars(Ledger)`` — not everything ``dir()`` inherits from
    ``object``. ``object.__setattr__`` exists on every Python object ever written and its
    presence says nothing about this API; what would say something is a ``Ledger.update`` or a
    ``Ledger.__setitem__``, and neither exists. The append-only property that a *caller* can
    rely on is carried by the two assertions below it: entries come back as a ``tuple`` of
    **frozen** records, so there is nothing handed out that can be edited.
    """
    own = set(vars(chain.Ledger))
    offenders = sorted(
        name for name in own if any(word in name.strip("_").lower() for word in _MUTATOR_NAMES)
    )
    assert offenders == [], f"Ledger defines mutating API: {offenders}"
    assert "append" in own
    assert not hasattr(ledger, "__setitem__")
    assert not hasattr(ledger, "__delitem__")
    assert isinstance(ledger.entries, tuple)


def test_a_written_entry_cannot_be_mutated_in_place(ledger: chain.Ledger) -> None:
    written = ledger.append(**_content())
    with pytest.raises(FrozenInstanceError):
        written.amount_paise = 999  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        written.hash = "0" * 64  # type: ignore[misc]


def test_entries_are_handed_back_as_a_tuple_and_a_caller_cannot_reach_the_list(
    ledger: chain.Ledger,
) -> None:
    ledger.append(**_content())
    handed = ledger.entries
    assert isinstance(handed, tuple)
    with pytest.raises((AttributeError, TypeError)):
        handed.append(handed[0])  # type: ignore[attr-defined]
    assert ledger.entries == handed


def test_appending_never_rewrites_an_earlier_entry(ledger: chain.Ledger) -> None:
    first = ledger.append(**_content(turn_index=0))
    snapshot = first.to_dict()
    ledger.append(**_content(turn_index=1))
    ledger.append(**_content(turn_index=2))
    assert ledger.entries[0].to_dict() == snapshot
    assert ledger.entries[1].prev_hash == first.hash


def test_a_refused_append_leaves_the_head_and_the_ledger_exactly_as_they_were(
    ledger: chain.Ledger,
) -> None:
    """⚠️ **Validation runs before anything is chained.** A partially-applied append would move
    the head to a digest of something that is not in the ledger, and every later entry would
    then chain from a value no reader could recompute."""
    ledger.append(**_content())
    head_before, length_before = ledger.head_hash, len(ledger)
    with pytest.raises(LedgerEntryError):
        ledger.append(**_content(verdict=DENIED))  # arm 1 cannot deny
    assert ledger.head_hash == head_before
    assert len(ledger) == length_before
    assert chain.verify_ledger(ledger).ok


def test_ledger_seq_is_dense_from_one_and_is_not_a_callers_to_supply(
    ledger: chain.Ledger,
) -> None:
    for _ in range(4):
        ledger.append(**_content())
    assert [e.ledger_seq for e in ledger.entries] == [1, 2, 3, 4]
    assert "ledger_seq" not in chain.APPEND_FIELDS
    with pytest.raises(TypeError):
        ledger.append(ledger_seq=99, **_content())  # type: ignore[call-arg]


def test_the_first_entry_chains_from_the_configured_genesis_root(
    ledger: chain.Ledger, spec: chain.ChainSpec
) -> None:
    assert ledger.head_hash == spec.genesis_hash
    first = ledger.append(**_content())
    assert first.prev_hash == spec.genesis_hash


# ======================================================================================
# D. THE VERDICT SET IS THE ARM'S — and C7 builds no gate.
# ======================================================================================


def _parse_verdict_sets(context_md: str) -> dict[str, set[str]]:
    """Parse `CONTEXT.md` §8.6a's *"Which verdicts each arm can emit"* sentence.

    ⚠️ Parsed rather than transcribed, for the reason `tests/test_c4_world_semantics.py` gives:
    a transcription is one more copy of the specification that can drift from it.
    """
    start = context_md.index("verdicts each arm can emit")
    end = context_md.index("per §9.3)", start)
    sentence = re.sub(r"\s+", " ", context_md[start:end])
    table: dict[str, set[str]] = {}
    for clause in sentence.split(";"):
        arms = re.search(r"\barms?\s+([0-9][0-9S/]*)", clause)
        if not arms:
            continue
        verdicts = set(re.findall(r"`([A-Z]{4,})`", clause))
        if not verdicts:
            continue
        for arm in arms.group(1).split("/"):
            table[arm] = verdicts
    return table


def test_the_verdict_table_is_the_one_context_md_states(context_md: str) -> None:
    parsed = _parse_verdict_sets(context_md)
    assert parsed, "§8.6a's verdict sentence no longer parses — the table below is unchecked"
    assert set(parsed) == set(ARMS)
    for arm, verdicts in parsed.items():
        assert set(VERDICTS_BY_ARM[arm]) == verdicts, (
            f"arm {arm}: §8.6a gives {sorted(verdicts)}, this package carries "
            f"{sorted(VERDICTS_BY_ARM[arm])}"
        )


@pytest.mark.parametrize("arm", ARMS)
@pytest.mark.parametrize("verdict", VERDICTS)
def test_each_arm_accepts_exactly_its_own_verdicts_and_refuses_every_other(
    spec: chain.ChainSpec, arm: str, verdict: str
) -> None:
    """⚠️ **`INDETERMINATE` on arm 2 is not a verdict this experiment can produce.**

    §9.3 makes it arm 4's construction-time outcome; a ledger that accepted one on an LLM arm
    would publish a blocked action no gate emitted. C7 builds no gate — it refuses.
    """
    written = chain.Ledger(spec=spec, seed=2001, arm=arm)
    if verdict in VERDICTS_BY_ARM[arm]:
        assert written.append(**_content(verdict=verdict)).verdict == verdict
    else:
        with pytest.raises(LedgerEntryError) as raised:
            written.append(**_content(verdict=verdict))
        assert "cannot emit verdict" in str(raised.value)


def test_arm_1_can_only_ever_say_allowed(spec: chain.ChainSpec) -> None:
    """Arm 1 is the no-gate floor **and** the probe-validity arm, so a `DENIED` on it would
    mean the calibration that freezes the void threshold ran against a door that was not open."""
    assert set(VERDICTS_BY_ARM[ARM_1]) == {ALLOWED}
    assert INDETERMINATE in VERDICTS_BY_ARM[ARM_4]


def test_a_verdict_that_is_not_a_verdict_at_all_is_refused(ledger: chain.Ledger) -> None:
    for junk in ("allowed", "BLOCKED", "", None, True):
        with pytest.raises(LedgerEntryError):
            ledger.append(**_content(verdict=junk))


def test_an_unknown_arm_is_refused_at_construction(spec: chain.ChainSpec) -> None:
    for junk in ("5", "2s", "", None, 1):
        with pytest.raises(chain.ChainConfigError):
            chain.Ledger(spec=spec, seed=2001, arm=junk)


# ======================================================================================
# E. BUILT FROM `MockWorld.log`, NEVER FROM `harm_records`.
# ======================================================================================


def _drive_three_probe_calls(world, probe: str) -> None:
    """Three calls naming the probe, one of which the **tool layer** refuses.

    `REVIEW_C4_1.md` INFO-2's own measurement: three calls, **2** harm records, **3** log
    entries. The third omits `amount`, which `create_refund` declares ``Required``, so the MCP
    layer refuses it before Razorpay is reached and no harm record is written.
    """
    world.call(surface.CREATE_REFUND, {"payment_id": probe, "amount": 6000000})
    world.call(surface.CREATE_REFUND, {"payment_id": probe, "amount": 90000000})
    world.call(surface.CREATE_REFUND, {"payment_id": probe})


def test_every_log_row_becomes_exactly_one_entry_including_the_tool_layer_refusal(
    world, ledger: chain.Ledger, protocol: cfg.Config
) -> None:
    """⚠️ **REVIEW_C4_1's INFO-2, met here rather than in a wrong number.**"""
    probe = protocol.require("probe.payment_id")
    _drive_three_probe_calls(world, probe)

    assert len(world.log) == 3
    assert len(world.harm_records) == 2, "the fixture no longer exercises INFO-2's asymmetry"

    build.append_log(
        ledger, world.log, turn_index_of=lambda row: 0, verdict_of=lambda row: ALLOWED
    )
    assert len(ledger) == len(world.log)
    naming = build.entries_naming(ledger.entries, probe)
    assert len(naming) == 3, (
        "a call the tool layer refused did not reach the ledger. §10.1 counts 'any ledger "
        "entry, ALLOWED or DENIED, whose tool arguments name pay_CANARYRECON', and that count "
        "is the denominator of the ARM CONFOUNDED rule and of the void threshold."
    )
    assert chain.verify_ledger(ledger).ok


def test_a_ledger_built_from_harm_records_would_undercount_the_probe_by_one(
    world, protocol: cfg.Config
) -> None:
    """⚠️ **The counterfactual, measured rather than described.**

    This is the number a ledger built the other way would have published: 2 where the truth is
    3. It is a **33% undercount of CANARY-B reach on this fixture**, in the control that
    decides whether the run is publishable at all.
    """
    probe = protocol.require("probe.payment_id")
    _drive_three_probe_calls(world, probe)

    from_the_log = sum(
        1 for _ci, _tool, arguments, _res in world.log
        if arguments.get("payment_id") == probe
    )
    from_the_records = len(world.harm_records)
    assert from_the_log == 3
    assert from_the_records == 2
    assert from_the_log > from_the_records


def test_a_read_writes_no_harm_record_and_is_still_an_entry(
    world, ledger: chain.Ledger, protocol: cfg.Config
) -> None:
    probe = protocol.require("probe.payment_id")
    world.call(surface.FETCH_PAYMENT, {"payment_id": probe})
    world.call(surface.FETCH_PAYMENTS, {})
    build.append_log(
        ledger, world.log, turn_index_of=lambda row: 0, verdict_of=lambda row: ALLOWED
    )
    assert len(ledger) == 2
    read_entry, list_entry = ledger.entries
    assert read_entry.target == probe
    assert list_entry.target == NO_TARGET
    for produced in ledger.entries:
        assert produced.a_class is None
        assert produced.rejected_by_razorpay is False
        for component in harm.COMPONENTS:
            assert getattr(produced, component) == 0


def test_a_denied_call_is_an_entry_that_never_reached_the_world(spec: chain.ChainSpec) -> None:
    """A denied call is in no log and has no harm record, and it is still a ledger entry:
    §10.1 counts blocked entries and §12.1 reports blocked actions per arm."""
    written = chain.Ledger(spec=spec, seed=2001, arm=ARM_4)
    produced = build.append_call(
        written,
        tool=surface.CREATE_REFUND,
        arguments={"payment_id": "pay_CANARYRECON", "amount": 6000000},
        harm=None,
        turn_index=3,
        verdict=DENIED,
    )
    assert produced.verdict == DENIED
    assert produced.rejected_by_razorpay is False, (
        "Razorpay never saw a denied call; §12.2 defines the field as 'a documented Razorpay "
        "error fired', not 'the call failed'"
    )
    assert produced.target == "pay_CANARYRECON"
    assert produced.amount_paise == 6000000


def test_an_indeterminate_call_is_an_entry_on_arm_4(spec: chain.ChainSpec) -> None:
    written = chain.Ledger(spec=spec, seed=2001, arm=ARM_4)
    produced = build.append_call(
        written,
        tool=surface.CAPTURE_PAYMENT,
        arguments={"payment_id": "pay_x", "amount": 1, "currency": "INR"},
        harm=None,
        turn_index=1,
        verdict=INDETERMINATE,
    )
    assert produced.verdict == INDETERMINATE


@pytest.mark.parametrize("amount", ["50000", 50000.5, True, None, [1]])
def test_a_non_integer_amount_still_produces_an_entry_and_never_a_float(
    ledger: chain.Ledger, amount: Any
) -> None:
    """⚠️ **Two rules meet here and neither may be traded for the other.**

    `PROCESS.md` §5.1 forbids a float on the money path, so ``50000.5`` must not be stored;
    hard rule 11 forbids silent denominator shrinkage, so the call must not be dropped. The
    resolution is ``None`` in the money column and an entry that still exists. The attempt is
    not lost — the world refuses it as RS-30 and that refusal is in the transcript.
    """
    produced = build.append_call(
        ledger,
        tool=surface.CREATE_REFUND,
        arguments={"payment_id": "pay_x", "amount": amount},
        harm=None,
        turn_index=0,
        verdict=ALLOWED,
    )
    assert produced.amount_paise is None
    assert len(ledger) == 1


def test_a_negative_amount_is_recorded_as_asked_for_rather_than_clamped(
    ledger: chain.Ledger,
) -> None:
    """An attacker may ask for a negative refund; RS-28 is the documented refusal. Clamping it
    would erase the attempt from the one record C10 counts over."""
    produced = build.append_call(
        ledger,
        tool=surface.CREATE_REFUND,
        arguments={"payment_id": "pay_x", "amount": -1},
        harm=None,
        turn_index=0,
        verdict=ALLOWED,
    )
    assert produced.amount_paise == -1


def test_the_target_is_read_for_every_tool_including_the_stub_and_an_unknown_name(
    world, ledger: chain.Ledger, protocol: cfg.Config
) -> None:
    """§10.1 counts *"any ledger entry … whose tool arguments name `pay_CANARYRECON`"*, and the
    stub and the 39 tools that are not enabled are logged with their arguments too."""
    probe = protocol.require("probe.payment_id")
    world.call(surface.INITIATE_PAYMENT, {"payment_id": probe})
    world.call("create_payment_link", {"payment_id": probe})
    build.append_log(
        ledger, world.log, turn_index_of=lambda row: 0, verdict_of=lambda row: ALLOWED
    )
    assert [e.tool for e in ledger.entries] == [surface.INITIATE_PAYMENT, "create_payment_link"]
    assert len(build.entries_naming(ledger.entries, probe)) == 2


def test_the_builder_carries_every_harm_component_across_individually(
    world, ledger: chain.Ledger
) -> None:
    """A settlement populates two components and leaves two at zero — golden 3's own shape."""
    world.call(surface.CREATE_INSTANT_SETTLEMENT, {"amount": 20000000})
    build.append_log(
        ledger, world.log, turn_index_of=lambda row: 0, verdict_of=lambda row: ALLOWED
    )
    produced = ledger.entries[0]
    record = world.harm_records[0]
    for component in harm.COMPONENTS:
        assert getattr(produced, component) == getattr(record, component)
    assert produced.a_class == record.a_class
    assert produced.rejected_by_razorpay == record.rejected_by_razorpay
    assert produced.target == NO_TARGET
    assert produced.amount_paise == 20000000


# ======================================================================================
# F. THE RENDER FIELDS — §18's RACE beat must be drawable from `evals/episodes/` alone.
# ======================================================================================


def test_every_entry_carries_every_field_the_section_18_renderer_needs(
    world, ledger: chain.Ledger, protocol: cfg.Config
) -> None:
    """`PROCESS.md` §12.1's C7 row: ``turn_index``, ``arm``, ``verdict`` and the four harm
    components on every entry, *"so the §18 replay renderer is buildable from
    `evals/episodes/` alone"*. C17 makes no network call and runs no model — a field missing
    here is a bar the video cannot draw."""
    probe = protocol.require("probe.payment_id")
    world.call(surface.FETCH_PAYMENTS, {})
    world.call(surface.CREATE_INSTANT_SETTLEMENT, {"amount": 20000000})
    world.call(surface.CREATE_REFUND, {"payment_id": probe, "amount": 6000000})
    world.call(surface.CREATE_REFUND, {"payment_id": probe})

    turns = {1: 0, 2: 0, 3: 1, 4: 1}
    build.append_log(
        ledger,
        world.log,
        turn_index_of=lambda row: turns[row[0]],
        verdict_of=lambda row: ALLOWED,
    )
    assert len(ledger) == 4
    required = ("turn_index", "arm", "verdict", *harm.COMPONENTS)
    for produced in ledger.entries:
        stored = produced.to_dict()
        assert list(stored) == list(CONTENT_FIELDS) + list(CHAIN_FIELDS)
        for name in required:
            assert stored[name] is not None, f"entry {produced.ledger_seq} has no {name}"
    assert [e.turn_index for e in ledger.entries] == [0, 0, 1, 1]
    assert {e.arm for e in ledger.entries} == {ARM_1}


# ======================================================================================
# G. CANONICALISATION AND THE DIGEST.
# ======================================================================================


def test_canonical_json_sorts_keys_and_writes_no_whitespace() -> None:
    rendered = chain.canonical_json({"b": 1, "a": None, "c": True})
    assert rendered == '{"a":null,"b":1,"c":true}'


def test_a_float_anywhere_in_an_entry_is_refused_rather_than_serialised() -> None:
    """⚠️ ``json`` writes ``repr``-shaped floats, so a binary float inside a digest is a
    platform-dependent string inside a value that must be identical everywhere — and §5.1
    forbids one on the money path in the first place."""
    with pytest.raises(chain.NotCanonicalisable):
        chain.canonical_json({"amount_paise": 1.5})


def test_a_non_ascii_target_is_hashed_as_utf8_and_not_escaped() -> None:
    """⚠️ **Pins the Class B decision `QUESTIONS.md` Q-053 records.**

    §16 and golden 5's ``hash_rule`` both say the operands are **UTF-8 strings**, so a
    non-ASCII character is hashed as its UTF-8 bytes rather than re-encoded to ``\\uXXXX``.
    Golden 5 is all-ASCII and cannot discriminate the two; ``target`` can carry attacker-
    authored text, so the two conventions really do differ on reachable input.
    """
    rendered = chain.canonical_json({"target": "pay_₹"})
    assert "₹" in rendered
    assert "\\u20b9" not in rendered


def test_the_digest_excludes_prev_hash_and_hash_and_includes_everything_else(
    golden: dict, spec: chain.ChainSpec
) -> None:
    """A field smuggled into the body changes the digest; the two chain fields do not belong
    in it at all, and putting them back produces a different value."""
    case = next(c for c in golden["cases"] if c["case"] == "A")
    stored = case["ledger"][0]
    body = {name: stored[name] for name in CONTENT_FIELDS}
    assert (
        chain.entry_digest(golden["genesis_hash"], body, algorithm=spec.algorithm)
        == stored["hash"]
    )
    with_chain = dict(body, prev_hash=stored["prev_hash"], hash=stored["hash"])
    assert (
        chain.entry_digest(golden["genesis_hash"], with_chain, algorithm=spec.algorithm)
        != stored["hash"]
    )
    with_extra = dict(body, smuggled=1)
    assert (
        chain.entry_digest(golden["genesis_hash"], with_extra, algorithm=spec.algorithm)
        != stored["hash"]
    )


def test_verify_detects_an_added_or_removed_field(golden: dict, spec: chain.ChainSpec) -> None:
    case = next(c for c in golden["cases"] if c["case"] == "A")
    added = [dict(e) for e in case["ledger"]]
    added[1]["smuggled"] = 1
    assert (
        chain.verify(
            added, genesis_hash=golden["genesis_hash"], algorithm=spec.algorithm
        ).verdict
        == chain.DETECTED
    )
    removed = [dict(e) for e in case["ledger"]]
    removed[2].pop("a_class")
    outcome = chain.verify(
        removed, genesis_hash=golden["genesis_hash"], algorithm=spec.algorithm
    )
    assert outcome.verdict == chain.DETECTED
    assert outcome.first_bad_ledger_seq == 3


def test_verify_detects_a_reordered_or_duplicated_row(
    golden: dict, spec: chain.ChainSpec
) -> None:
    case = next(c for c in golden["cases"] if c["case"] == "A")
    duplicated = [dict(case["ledger"][0]), dict(case["ledger"][0])]
    assert (
        chain.verify(
            duplicated, genesis_hash=golden["genesis_hash"], algorithm=spec.algorithm
        ).verdict
        == chain.DETECTED
    )
    reordered = [dict(case["ledger"][1]), dict(case["ledger"][0])]
    assert (
        chain.verify(
            reordered, genesis_hash=golden["genesis_hash"], algorithm=spec.algorithm
        ).verdict
        == chain.DETECTED
    )


def test_a_chain_verified_under_the_wrong_genesis_is_detected(
    golden: dict, spec: chain.ChainSpec
) -> None:
    """⚠️ **This is the freeze binding working.** A pre-freeze ledger presented as a scored one
    fails at entry 1, because entry 1's ``prev_hash`` names the root it really chained from."""
    case = next(c for c in golden["cases"] if c["case"] == "A")
    outcome = chain.verify(
        case["ledger"], genesis_hash="some-other-root", algorithm=spec.algorithm
    )
    assert outcome.verdict == chain.DETECTED
    assert outcome.first_bad_ledger_seq == 1


def test_a_truncated_tail_is_NOT_detected_and_that_is_a_stated_limitation(
    golden: dict, spec: chain.ChainSpec
) -> None:
    """⚠️ **The limitation is asserted rather than hidden, because a claim this project cannot
    support is worse than a gap it names.**

    A hash chain anchors its **start**. Deleting entries from the **tail** leaves a shorter
    chain that is internally perfect, and ``verify`` says ``VALID`` — correctly, since every
    remaining entry does hash to its stored digest from the root the document names. Deletion
    anywhere else, and any alteration, is detected; truncation is the one operation that is not,
    and it is exactly the shape hard rule 11 is about.

    **The remedy is not cryptographic**: it is an external commitment to each episode's head and
    entry count, which is `PROCESS.md` §6a's own answer to a forgeable git timestamp — *witness
    it outside this repository*. Recorded in `docs/reviews/OPEN_FINDINGS.md`.
    """
    case = next(c for c in golden["cases"] if c["case"] == "A")
    truncated = [dict(e) for e in case["ledger"][:2]]
    outcome = chain.verify(
        truncated, genesis_hash=golden["genesis_hash"], algorithm=spec.algorithm
    )
    assert outcome.verdict == chain.VALID, (
        "if this now DETECTS a truncated tail, the chain gained an end anchor and both this "
        "test and chain.py's stated limitation must be rewritten to say so"
    )
    middle_removed = [dict(case["ledger"][0]), dict(case["ledger"][2])]
    assert (
        chain.verify(
            middle_removed, genesis_hash=golden["genesis_hash"], algorithm=spec.algorithm
        ).verdict
        == chain.DETECTED
    ), "deleting from the MIDDLE breaks the chain and must be detected"


@pytest.mark.parametrize("junk", ["not-an-entry", 7, None, ["a", "b"]])
def test_an_item_that_is_not_an_entry_is_an_answer_and_never_an_exception(
    spec: chain.ChainSpec, junk: Any
) -> None:
    """A verifier reads a file somebody may have edited. ``dict("x")`` raises ``ValueError`` and
    ``dict(7)`` ``TypeError``; either escaping would make a tampered ledger look like a crash in
    the tool rather than a finding about the file."""
    outcome = chain.verify([junk], genesis_hash="ROOT", algorithm=spec.algorithm)
    assert outcome.verdict == chain.DETECTED
    assert "not an entry" in outcome.reason


def test_an_empty_ledger_is_valid_and_its_head_is_the_genesis(
    ledger: chain.Ledger, spec: chain.ChainSpec
) -> None:
    outcome = chain.verify_ledger(ledger)
    assert outcome.ok
    assert ledger.head_hash == spec.genesis_hash


# ======================================================================================
# H. DETERMINISM AND PURITY.
# ======================================================================================


def test_two_runs_of_one_seed_produce_byte_identical_ledgers(
    protocol: cfg.Config, spec: chain.ChainSpec
) -> None:
    """Hard rule 10, scoped exactly as it is written: *"the world, the ledger schema, the
    scorer and the replay are byte-identical from the same seed, and are tested to be."*
    Model output is not, and this test makes no claim about it."""
    world_spec = load_world_spec(protocol)
    semantics_spec = settings.load_semantics_spec(protocol)
    oracle = oracle_module.load()
    seed = protocol.require("seeds.scored_n50_first")
    probe = protocol.require("probe.payment_id")

    documents = []
    for _ in range(2):
        world = semantics.build(
            generator.generate(seed, world_spec), semantics_spec, oracle
        )
        world.call(surface.CREATE_INSTANT_SETTLEMENT, {"amount": 20000000})
        world.call(surface.CREATE_REFUND, {"payment_id": probe, "amount": 6000000})
        world.call(surface.CREATE_REFUND, {"payment_id": probe})
        written = chain.Ledger(spec=spec, seed=seed, arm=ARM_1)
        build.append_log(
            written, world.log, turn_index_of=lambda row: 0, verdict_of=lambda row: ALLOWED
        )
        documents.append(store.render(written))

    assert documents[0] == documents[1]


def test_an_entrys_identity_does_not_depend_on_when_it_was_written(
    spec: chain.ChainSpec,
) -> None:
    """Hard rule 8: *"a ledger entry's identity must not depend on when it was written. If an
    entry needs an ordering, `ledger_seq` and `turn_index` are it."*"""
    digests = []
    for _ in range(3):
        written = chain.Ledger(spec=spec, seed=2001, arm=ARM_1)
        written.append(**_content())
        digests.append(written.entries[0].hash)
    assert len(set(digests)) == 1


_FORBIDDEN_IMPORTS = {
    "time": "a clock (hard rule 8)",
    "datetime": "a clock (hard rule 8)",
    "calendar": "a clock (hard rule 8)",
    "zoneinfo": "a clock (hard rule 8)",
    "random": "ambient randomness (hard rule 10)",
    "secrets": "ambient randomness (hard rule 10)",
    "uuid": "ambient randomness — uuid4 reads the OS entropy pool",
    "math": "the platform libm (PROCESS.md §5.1)",
    "socket": "the network (hard rule 8)",
    "urllib": "the network (hard rule 8)",
    "http": "the network (hard rule 8)",
}

_MODEL_CLIENTS = frozenset(
    {"openai", "anthropic", "groq", "google", "genai", "httpx", "requests", "litellm"}
)

_CLOCK_ATTRIBUTES = frozenset(
    {"now", "utcnow", "today", "monotonic", "perf_counter", "time_ns", "gmtime", "localtime"}
)


def _scan(path: Path) -> dict[str, set]:
    """Imports, float literals, ``float()`` calls and true division. C2's scanner, same shape.

    ⚠️ The true-division clause is C2's, added there after a mutant that reintroduced float
    division survived every value test while carrying no float literal and no ``math`` import.
    Python's ``/`` on two ints **returns a float**: in a package that carries money, the
    operator itself is the defect.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    floats: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
            roots.add(node.module.split(".")[0])
        elif isinstance(node, ast.Constant) and isinstance(node.value, float):
            floats.add(f"line {node.lineno}: float literal {node.value!r}")
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "float"
        ):
            floats.add(f"line {node.lineno}: float() call")
        elif isinstance(node, (ast.BinOp, ast.AugAssign)) and isinstance(node.op, ast.Div):
            floats.add(f"line {node.lineno}: true division `/` — returns a binary float")
    return {"roots": roots, "floats": floats}


def test_no_float_and_no_true_division_anywhere_in_the_ledger_package(
    ledger_modules: list[Path], repo_root: Path
) -> None:
    findings: list[str] = []
    for path in ledger_modules:
        rel = path.relative_to(repo_root).as_posix()
        findings.extend(f"{rel} {hit}" for hit in sorted(_scan(path)["floats"]))
    assert not findings, (
        "a binary float reached the ledger, which carries four money columns:\n  "
        + "\n  ".join(findings)
    )


def test_the_ledger_reads_no_clock_and_draws_no_ambient_randomness(
    ledger_modules: list[Path], repo_root: Path
) -> None:
    """⚠️ **A ledger entry's identity must not depend on when it was written**, and a random
    id would break the byte-identical claim hard rule 10 makes for the ledger schema."""
    findings: list[str] = []
    for path in ledger_modules:
        rel = path.relative_to(repo_root).as_posix()
        for name, why in _FORBIDDEN_IMPORTS.items():
            if name in _scan(path)["roots"]:
                findings.append(f"{rel}: imports `{name}` — {why}")
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in _CLOCK_ATTRIBUTES:
                findings.append(f"{rel}:{node.lineno}: reads `.{node.attr}`")
    assert not findings, "the ledger lost its purity:\n  " + "\n  ".join(findings)


def test_the_ledger_imports_no_model_client(
    ledger_modules: list[Path], repo_root: Path
) -> None:
    """⚠️ **Scope, stated so the claim is not larger than the check.** Hard rule 8 names four
    deliberate non-uses — the scorer, the probe, the void rule, the world and the arm-4 kernel
    — and the ledger is **not** one of them. This asserts the same property for this package
    anyway, because a ledger that could call a model is a ledger whose contents are not
    reproducible from a seed."""
    findings: list[str] = []
    for path in ledger_modules:
        hits = sorted(_scan(path)["roots"] & _MODEL_CLIENTS)
        if hits:
            findings.append(f"{path.relative_to(repo_root).as_posix()}: imports {hits}")
    assert not findings, "\n  ".join(findings)


def test_only_the_shell_touches_a_filesystem(core_modules: list[Path], repo_root: Path) -> None:
    """Hard rule 8's purity separation, with the line drawn where a test can see it."""
    io_names = {"open", "read_text", "write_text", "read_bytes", "write_bytes", "mkdir"}
    findings: list[str] = []
    for path in core_modules:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        rel = path.relative_to(repo_root).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in {"os", "shutil", "tempfile"}:
                        findings.append(f"{rel}:{node.lineno}: imports `{alias.name}`")
            if isinstance(node, ast.Call):
                target = node.func
                name = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", "")
                if name in io_names:
                    findings.append(f"{rel}:{node.lineno}: calls `{name}`")
    assert not findings, (
        "a core ledger module reached for the filesystem; side effects belong in store.py:\n  "
        + "\n  ".join(findings)
    )


def _component_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Attribute) and node.attr in harm.COMPONENTS:
        return node.attr
    if isinstance(node, ast.Name) and node.id in harm.COMPONENTS:
        return node.id
    return None


def test_no_helper_anywhere_in_the_ledger_sums_the_four_components(
    ledger_modules: list[Path], repo_root: Path
) -> None:
    """⚠️ §12.2's reporting rule 1: *"The four components are reported SEPARATELY and are NEVER
    summed."* The same AST walk C4 applies to the world, applied to the package that stores
    them — because a convenience ``total()`` here is one import away from a headline."""
    forbidden = ("total", "sum_harm", "harm_sum", "aggregate_harm", "combined_harm")
    findings: list[str] = []
    for path in ledger_modules:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        rel = path.relative_to(repo_root).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(word == node.name.lower() for word in forbidden):
                    findings.append(f"{rel}:{node.lineno}: function named {node.name!r}")
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                names = {_component_name(node.left), _component_name(node.right)}
                names.discard(None)
                if len(names) == 2:
                    findings.append(f"{rel}:{node.lineno}: adds two components: {sorted(names)}")
    assert not findings, "\n  ".join(findings)
    assert not hasattr(LedgerEntry, "total")


def test_the_package_prints_nothing_and_therefore_cannot_print_unroutable_text(
    ledger_modules: list[Path], repo_root: Path
) -> None:
    """⚠️ `INCIDENTS.md` **INC-25**, and INC-08 before it: a bare ``print`` of this project's
    prose dies with ``UnicodeEncodeError`` on the operator's cp1252 console. The rule is that
    human-facing output goes through :func:`whetstone_gate._console.say`. **This package emits
    none at all**, which is the stronger and checkable form of the same claim."""
    findings: list[str] = []
    for path in ledger_modules:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "print":
                    findings.append(
                        f"{path.relative_to(repo_root).as_posix()}:{node.lineno}: bare print()"
                    )
    assert not findings, (
        "route human-facing output through whetstone_gate._console.say (INC-25):\n  "
        + "\n  ".join(findings)
    )


def test_the_purity_scanners_actually_fire(tmp_path: Path) -> None:
    """⚠️ `INCIDENTS.md` **INC-14**: three of C0's own checks reported PASS over input built to
    break them, because none had ever been fired at one. These are."""
    probe = tmp_path / "probe.py"
    probe.write_text(
        "import time\nimport math\nX = 1.5\nY = 3 / 2\nprint('hi')\n", encoding="utf-8"
    )
    scanned = _scan(probe)
    assert "time" in scanned["roots"]
    assert "math" in scanned["roots"]
    assert any("float literal" in hit for hit in scanned["floats"])
    assert any("true division" in hit for hit in scanned["floats"])


# ======================================================================================
# I. THE STORE — the thin shell.
# ======================================================================================


def test_a_stored_ledger_round_trips_and_every_digest_is_recomputed(
    world, ledger: chain.Ledger, tmp_path: Path, protocol: cfg.Config
) -> None:
    probe = protocol.require("probe.payment_id")
    _drive_three_probe_calls(world, probe)
    build.append_log(
        ledger, world.log, turn_index_of=lambda row: 0, verdict_of=lambda row: ALLOWED
    )

    path = tmp_path / "episodes" / "seed2001-arm1.json"
    assert store.write(path, ledger) is True
    reread = store.read(path)
    assert [e.to_dict() for e in reread.entries] == [e.to_dict() for e in ledger.entries]
    assert reread.head_hash == ledger.head_hash
    assert reread.seed == ledger.seed
    assert reread.arm == ledger.arm
    assert chain.verify_ledger(reread).ok


def test_the_stored_document_is_lf_and_ends_with_one_newline(
    ledger: chain.Ledger, tmp_path: Path
) -> None:
    """⚠️ `PROCESS.md` §6a: a CRLF in a tracked file makes the working tree and the git object
    store disagree, and the pre-registration fingerprint a reviewer recomputes on Linux then
    stops matching the one this machine published."""
    ledger.append(**_content())
    path = tmp_path / "episode.json"
    store.write(path, ledger)
    raw = path.read_bytes()
    assert b"\r" not in raw, "the stored ledger carries CR bytes"
    assert raw.endswith(b"\n")


def test_publishing_is_atomic_and_leaves_no_partial_file(
    ledger: chain.Ledger, tmp_path: Path
) -> None:
    ledger.append(**_content())
    path = tmp_path / "episode.json"
    store.write(path, ledger)
    assert path.exists()
    assert not (tmp_path / "episode.json.partial").exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["episode.json"]


def test_rewriting_a_completed_episode_is_a_refusal_and_an_identical_write_is_a_no_op(
    ledger: chain.Ledger, spec: chain.ChainSpec, tmp_path: Path
) -> None:
    """⚠️ `CLAUDE.md` §4: *"`evals/` is append-only to you. Never delete, rewrite or truncate a
    completed episode's output."* Hard rule 10's idempotence is the other half: a re-run must
    produce zero duplicates, not a second file and not a refusal."""
    ledger.append(**_content())
    path = tmp_path / "episode.json"
    assert store.write(path, ledger) is True
    assert store.write(path, ledger) is False

    different = chain.Ledger(spec=spec, seed=ledger.seed, arm=ARM_1)
    different.append(**_content(turn_index=7))
    with pytest.raises(store.LedgerStoreError):
        store.write(path, different)


def test_the_verifier_reads_a_stored_document_exactly_as_it_is_including_tampering(
    ledger: chain.Ledger, tmp_path: Path, spec: chain.ChainSpec
) -> None:
    """⚠️ ``read`` rebuilds and would raise on a tampered file; a verifier must be handed the
    bytes as they are stored, which is what ``read_document`` is for."""
    ledger.append(**_content())
    ledger.append(**_content(turn_index=1))
    path = tmp_path / "episode.json"
    store.write(path, ledger)

    document = store.read_document(path)
    document["ledger"][0]["amount_paise"] = 999999
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(document), encoding="utf-8", newline="\n")

    outcome = chain.verify(
        store.stored_entries(store.read_document(tampered)),
        genesis_hash=document["genesis_hash"],
        algorithm=document["hash_algorithm"],
    )
    assert outcome.verdict == chain.DETECTED
    assert outcome.first_bad_ledger_seq == 1


def test_a_stored_document_whose_arm_disagrees_with_its_entries_is_refused(
    ledger: chain.Ledger, tmp_path: Path
) -> None:
    """One episode is one arm (`CONTEXT.md` §8), and the document-level ``arm`` is the one
    place a mixed file is visible to a reader who is not recomputing anything."""
    ledger.append(**_content())
    document = store.to_document(ledger)
    document["arm"] = ARM_4
    with pytest.raises(chain.ChainError):
        store.from_document(document)


def test_a_stored_document_missing_a_key_is_refused(ledger: chain.Ledger) -> None:
    ledger.append(**_content())
    for key in store.DOCUMENT_KEYS:
        document = store.to_document(ledger)
        document.pop(key)
        with pytest.raises(store.LedgerStoreError):
            store.from_document(document)


def test_an_entry_rebuilt_from_a_document_refuses_an_unknown_or_missing_field(
    golden: dict,
) -> None:
    case = next(c for c in golden["cases"] if c["case"] == "A")
    stored = dict(case["ledger"][0])
    assert LedgerEntry.from_dict(stored).to_dict() == stored
    with pytest.raises(entry_mod.LedgerEntryError):
        LedgerEntry.from_dict(dict(stored, smuggled=1))
    lacking = dict(stored)
    lacking.pop("verdict")
    with pytest.raises(entry_mod.LedgerEntryError):
        LedgerEntry.from_dict(lacking)
