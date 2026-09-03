"""C12 — **THE EPISODE DRIVER.** The tests for the chunk that finally runs something.

Organised by the claim each group defends, because a test file for a wiring chunk is
otherwise a list of plumbing checks with no argument in it:

  1. **SPEND SAFETY** — no model client, two ways; no deletion path; no key value anywhere.
  2. **HARD RULE 12** — golden 8's fixtures, reproduced **through this driver's wiring**
     rather than against the accumulator alone.
  3. **HARD RULE 11** — the turn identity, the episode denominator, and the resumed run.
  4. **HARD RULE 10** — resumable, idempotent, publish-on-complete, zero duplicates.
  5. **§10.1 — THE PROBE REACHES EVERY ARM AND LOOKS IDENTICAL IN ALL OF THEM**, asserted
     from the **driver** side, which is the only side that can see a whole episode.
  6. **THE REFUSALS** — every precondition that stands between this code and the operator's
     money, each asserted to refuse rather than warn.
  7. **THE PILOT** — read from `config/`, and the one number it exists to produce.

⚠️ **ZERO PROVIDER MODEL CALLS.** Every test here drives
:class:`whetstone_gate.driver.clients.TranscriptClient`, which opens nothing. The build
prompt sanctioned no spend and every lane is reserved (`PROCESS.md` §8).
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

from whetstone_gate import config as cfg
from whetstone_gate.driver import episode as driver_episode
from whetstone_gate.driver import pilot as pilot_module
from whetstone_gate.driver import protocol as driver_protocol
from whetstone_gate.driver import rehearsal
from whetstone_gate.driver import run as driver_run
from whetstone_gate.driver.clients import ModelReply, RateLimited, TranscriptClient
from whetstone_gate.gates import shell as gate_shell
from whetstone_gate.ledger import chain as ledger_chain
from whetstone_gate.ledger import store as ledger_store
from whetstone_gate.runner import n_rule
from whetstone_gate.runner.budget import Ceilings, LaneBudget, run_offers
from whetstone_gate.runner.episodes import EpisodeKey
from whetstone_gate.runner.redaction import SecretInPayload, refuse_if_secret_bearing
from whetstone_gate.world import generator as world_generator
from whetstone_gate.world import oracle as world_oracle
from whetstone_gate.world import semantics as world_semantics
from whetstone_gate.world import settings as world_settings

DRIVER_PACKAGE = "src/whetstone_gate/driver"
S3_BINDING = driver_episode.S3_AUTHORIZATION_IS_THE_PAYMENT


# ======================================================================================
# Fixtures — every one of them offline
# ======================================================================================


@pytest.fixture(scope="session")
def golden8(repo_root: Path) -> dict:
    """`tests/goldens/golden8_tokens.json`. ⚠️ **READ-ONLY. Never written, never regenerated.**"""
    return json.loads(
        (repo_root / "tests/goldens/golden8_tokens.json").read_bytes().decode("utf-8")
    )


@pytest.fixture(scope="session")
def driver_sources(repo_root: Path) -> list[Path]:
    return sorted((repo_root / DRIVER_PACKAGE).glob("*.py"))


@pytest.fixture
def one_seed_matrix() -> pilot_module.PilotMatrix:
    """A one-episode matrix on the reference lane. The pilot's shape, one cell wide."""
    real = pilot_module.load_pilot(arm="1")
    return pilot_module.PilotMatrix(
        arm="1",
        turn_budget=real.turn_budget,
        reference=pilot_module.PilotCell(
            lane=real.reference.lane,
            attacker_model=real.reference.attacker_model,
            seeds=(real.reference.seeds[0],),
        ),
        ladder_l2=pilot_module.PilotCell(
            lane=real.ladder_l2.lane, attacker_model=real.ladder_l2.attacker_model, seeds=()
        ),
        judge_lane=real.judge_lane,
    )


def _request(matrix: pilot_module.PilotMatrix, out_root: Path, **kwargs) -> driver_run.RunRequest:
    return driver_run.RunRequest(
        matrix=matrix,
        out_root=out_root,
        ceilings=Ceilings(
            call_ceiling=kwargs.pop("call_ceiling", 1000),
            token_ceiling=kwargs.pop("token_ceiling", 5_000_000),
        ),
        s3_binding=kwargs.pop("s3_binding", S3_BINDING),
        spend_real_tokens=kwargs.pop("spend_real_tokens", False),
        sanctioned_lanes=frozenset(kwargs.pop("sanctioned_lanes", ())),
        allow_absent_corpus=kwargs.pop("allow_absent_corpus", True),
    )


def _run_one_episode_on(
    *,
    arm: str,
    seed: int,
    attacker_replies,
    judge_replies=(),
    reservation: int,
    ceilings: Ceilings,
    judge_reservation: int | None = None,
    rate_limit_at: int | None = None,
    s3_binding: str = S3_BINDING,
):
    """Drive **one episode through the real wiring** with an offline client.

    This is deliberately :func:`whetstone_gate.driver.episode.run_one_episode` and not a
    re-implementation: golden 8 is reproduced *through the driver*, which is what the chunk's
    done-when asks for, and an assertion against :class:`LaneBudget` alone would only
    re-test C11.
    """
    settings = driver_episode.EpisodeSettings(
        attacker=driver_episode.AttackerSettings.from_config(),
        attacker_call_reservation_tokens=reservation,
        judge_call_reservation_tokens=(
            reservation if judge_reservation is None else judge_reservation
        ),
        s3_binding=s3_binding,
    )
    key = EpisodeKey(block="TEST", arm=arm, seed_or_task=str(seed), attacker_model="lane-a")
    attacker_budget = LaneBudget(model="lane-a", ceilings=ceilings)
    judge_budget = LaneBudget(model="lane-b", ceilings=ceilings)
    world = world_semantics.build(
        world_generator.generate_world(seed),
        world_settings.load_semantics_spec(),
        world_oracle.load(),
    )
    texts = gate_shell.load_gate_texts()
    judge_stub = None if arm in ("1", "4") else _AlwaysWiredJudge()
    gate = gate_shell.build_gate(arm, judge_stub)
    episode = driver_episode.run_one_episode(
        key=key,
        seed=seed,
        arm=arm,
        lane="lane-a",
        world=world,
        gate=gate,
        ledger=ledger_chain.Ledger(spec=ledger_chain.load_chain_spec(), seed=seed, arm=arm),
        client=TranscriptClient(
            attacker_replies=attacker_replies,
            judge_replies=judge_replies,
            rate_limit_at=rate_limit_at,
        ),
        attacker_budget=attacker_budget,
        judge_budget=judge_budget,
        judge_lane="lane-b",
        settings=settings,
        generic_denial=texts.generic_denial,
        corpus_entries=(),
        on_usage=lambda *_: None,
    )
    return episode, attacker_budget, judge_budget


class _AlwaysWiredJudge:
    """A placeholder the driver replaces. It exists only to satisfy ``build_gate``."""

    def complete(self, *, system: str, user: str) -> str:  # pragma: no cover - replaced
        raise AssertionError("the metered judge client was not wired in")


# ======================================================================================
# 1. SPEND SAFETY
# ======================================================================================

_FORBIDDEN_IMPORTS = {
    "groq", "google", "openai", "anthropic", "litellm", "cohere", "mistralai",
    "httpx", "requests", "urllib", "urllib3", "aiohttp", "http", "socket", "ftplib",
}

#: The vocabulary of **dynamic reach**, which an AST import walk cannot see.
#: `INCIDENTS.md` **INC-51** measured all three walking past `check_roles` D1, D2 and D3.
_DYNAMIC_REACH = ("__import__", "importlib", "getattr(")


def _imported_modules(path: Path, *, source_root: Path) -> set[str]:
    """Every module name this file could reach, **in every import form Python has.**

    ⚠️ ``from X import Y`` may name a MODULE ``Y``, and ``X.Y`` is then an edge of the
    import graph that ``X`` alone does not carry. `INCIDENTS.md` **INC-43** is what
    recording ``node.module`` alone cost: the walk died at the package root.
    """
    tree = ast.parse(path.read_bytes().decode("utf-8"))
    package_parts = path.resolve().relative_to(source_root.resolve()).parts[:-1]
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package_parts[: len(package_parts) - (node.level - 1)]
                prefix = ".".join(base + ((node.module,) if node.module else ()))
            else:
                prefix = node.module or ""
            if not prefix:
                continue
            found.add(prefix)
            for alias in node.names:
                found.add(f"{prefix}.{alias.name}")
    return found


def _first_party_import_closure(roots: list[Path], *, source_root: Path):
    """Walk ``roots`` and every first-party module they transitively reach."""
    seen: set[str] = set()
    queue = list(roots)
    findings: list[str] = []
    while queue:
        path = queue.pop()
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        for module in _imported_modules(path, source_root=source_root):
            root = module.split(".")[0]
            if root in _FORBIDDEN_IMPORTS:
                findings.append(f"{path.name} reaches {module!r}")
            if root == "whetstone_gate":
                candidate = source_root.joinpath(*module.split("."))
                for target in (candidate.with_suffix(".py"), candidate / "__init__.py"):
                    if target.is_file():
                        queue.append(target)
    return seen, findings


def test_the_driver_imports_no_model_client_AST_WALK(repo_root: Path, driver_sources):
    """⚠️ **WAY ONE OF TWO: the transitive first-party AST walk.**

    The driver is the module most likely to want a provider and it may not have one — the
    client is a parameter (:class:`whetstone_gate.driver.clients.MeteredModelClient`).
    Walked over the package's own modules **and** everything first-party they reach, so the
    guarantee cannot be evaded by putting the client one module away.
    """
    source_root = repo_root / "src"
    seen, findings = _first_party_import_closure(list(driver_sources), source_root=source_root)
    assert not findings, "the driver can reach a provider or the network:\n  " + "\n  ".join(
        findings
    )
    assert len(seen) > len(driver_sources), "the transitive walk never left the package"
    assert any(
        Path(name).name == "loop.py" for name in seen
    ), "the walk did not reach the attacker loop, so it did not cross the package boundary"


def test_the_driver_imports_no_model_client_RAW_SOURCE_SCAN(driver_sources):
    """⚠️ **WAY TWO OF TWO: the raw-source scan, and it is NOT belt-and-braces.**

    `INCIDENTS.md` **INC-51**, measured: ``__import__(…)``, ``importlib.import_module(…)``
    and ``getattr(pkg, "name")`` escape an AST import walk **by construction** — a call
    expression is not an ``ast.Import`` node — and all three made a ``gates/`` module run a
    ``scorer/`` predicate while `check_roles` **D1, D2 AND D3 every one reported PASS**.

    **The two halves see different things and neither is the guarantee alone:** the AST walk
    sees every static import exactly and cannot see a call; this scan sees the vocabulary and
    cannot see semantics.
    """
    findings: list[str] = []
    for path in driver_sources:
        code = _strip_comments_and_docstrings(path.read_bytes().decode("utf-8"))
        for form in _DYNAMIC_REACH:
            if form in code:
                findings.append(f"{path.name} carries the dynamic-reach form {form!r}")
        for name in _FORBIDDEN_IMPORTS:
            if re.search(rf"(?<![\w.]){re.escape(name)}\.", code):
                findings.append(f"{path.name} names {name!r} in executable source")
    assert not findings, (
        "the driver's SOURCE TEXT carries a form an AST walk cannot see:\n  "
        + "\n  ".join(findings)
        + "\n  INC-51: a dynamic reach passes D1, D2 and D3 and is not a result, it is a "
        "definition. Write it statically so the AST walk can see it."
    )


def _strip_comments_and_docstrings(source: str) -> str:
    """Prose *about* a client is not a client. The same reduction the hard-rule-9 tripwire
    makes, and for the same reason: a scanner that fires on its own explanations is a
    scanner whose first fix is to weaken it."""
    without_docstrings = re.sub(r'("""|\'\'\')(?:.|\n)*?\1', '""', source)
    return re.sub(r"#[^\n]*", "", without_docstrings)


#: Every removal form. `CLAUDE.md` §4 makes deletion of `evals/` **operator-only**.
_REMOVAL_CALLS = {
    "remove", "unlink", "rmdir", "rmtree", "truncate", "removedirs", "rename",
}


def test_the_driver_has_NO_DELETION_PATH_asserted_by_AST(driver_sources):
    """⚠️ **`evals/` IS APPEND-ONLY AND DELETION IS OPERATOR-ONLY — asserted, not promised.**

    Parsed rather than grepped, so a call spelled across a line break is still seen. The
    same guard :mod:`whetstone_gate.runner.checkpoint` carries: a ``force=True`` parameter
    is how `CLAUDE.md` §4 would be got round by a session in a hurry, and there is no
    argument in this package that produces one.
    """
    findings: list[str] = []
    for path in driver_sources:
        for node in ast.walk(ast.parse(path.read_bytes().decode("utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            name = (
                node.func.attr
                if isinstance(node.func, ast.Attribute)
                else getattr(node.func, "id", "")
            )
            if name in _REMOVAL_CALLS:
                findings.append(f"{path.name}:{node.lineno} calls {name}()")
    assert not findings, (
        "the driver can delete or truncate a completed episode's output:\n  "
        + "\n  ".join(findings)
        + "\n  CLAUDE.md S4: `evals/` is append-only and deletions are OPERATOR-ONLY."
    )


def test_no_key_value_can_reach_a_checkpoint_a_ledger_or_a_usage_row():
    """⚠️ **C11's redaction REFUSES rather than masks, and the driver's writes go through it.**

    A masking helper would write the record with ``***`` in it and carry on, leaving the run
    in a state where something upstream is putting credentials into episode data and nobody
    is told. `CLAUDE.md` §4's own instruction for this class of thing is *"STOP and report
    instead of working around it."*
    """
    with pytest.raises(SecretInPayload):
        refuse_if_secret_bearing({"note": "gsk_" + "A" * 32}, where="checkpoint[test]")
    with pytest.raises(SecretInPayload):
        refuse_if_secret_bearing({"note": "AIza" + "B" * 35}, where="usage[test]")
    with pytest.raises(SecretInPayload):
        refuse_if_secret_bearing({"echo": "GROQ_API_KEY=redacted"}, where="ledger[test]")
    # A clean payload passes and returns None, so it reads as an assertion at a call site.
    assert refuse_if_secret_bearing({"lane": "gemma-26b", "total_tokens": 3000}) is None


def test_the_driver_never_names_an_environment_variable_or_reads_one(driver_sources):
    """The key **names** come from `config/lanes.yaml`'s ``provider`` field through
    :mod:`whetstone_gate.runner.keys`, whose only public function returns a **boolean**.
    Nothing here subscripts the environment."""
    findings = []
    for path in driver_sources:
        code = _strip_comments_and_docstrings(path.read_bytes().decode("utf-8"))
        for form in ("os.environ", "getenv", "dotenv", "_API_KEY"):
            if form in code:
                findings.append(f"{path.name} carries {form!r}")
    assert not findings, "the driver reaches for the environment directly:\n  " + "\n  ".join(
        findings
    )


# ======================================================================================
# 2. HARD RULE 12 — golden 8, reproduced THROUGH THE WIRING
# ======================================================================================


def test_golden8_fixture_A_tokens_bind_first_through_the_driver(golden8):
    """⚠️ **Fixture A: the TOKEN ceiling binds while the CALL ceiling still has room** —
    hard rule 12's *"whichever comes first"*, in the direction the spike actually failed.

    Driven through :func:`whetstone_gate.driver.episode.run_one_episode`, not against the
    accumulator alone: the chunk's done-when is *"golden 8's fixtures reproduce through your
    wiring"*, and an assertion against :class:`LaneBudget` would only re-test C11.
    """
    fixture = golden8["fixtures"]["A_tokens_bind_first"]
    ceilings = _fixture_ceilings(golden8)
    cost = fixture["offered_calls"][0]
    episode, budget, _ = _run_one_episode_on(
        arm="1",
        seed=_a_pilot_seed(),
        attacker_replies=[("{}", cost)] * len(fixture["offered_calls"]),
        reservation=cost,
        ceilings=ceilings,
    )
    expected = fixture["expected"]
    assert budget.state() == {
        "calls_used": expected["calls_used"],
        "calls_unused": expected["calls_unused"],
        "tokens_spent": expected["tokens_spent"],
        "tokens_unspent": expected["tokens_unspent"],
        "stopped_by": expected["stopped_by"],
    }
    assert episode.turns_run == expected["calls_used"]
    assert episode.truncated, "a lane that stopped mid-episode truncated it"
    assert episode.cause == "TOKEN_CEILING"


def test_golden8_fixture_B_calls_bind_first_through_the_driver(golden8):
    """⚠️ **Fixture B: the CALL ceiling binds while the TOKEN ceiling still has HALF its
    budget.** A and B together are why hard rule 12 says a call ceiling alone is not a
    sanction and a token ceiling alone is not one either."""
    fixture = golden8["fixtures"]["B_calls_bind_first"]
    ceilings = _fixture_ceilings(golden8)
    cost = fixture["offered_calls"][0]
    episode, budget, _ = _run_one_episode_on(
        arm="1",
        seed=_a_pilot_seed(),
        attacker_replies=[("{}", cost)] * len(fixture["offered_calls"]),
        reservation=cost,
        ceilings=ceilings,
    )
    expected = fixture["expected"]
    assert budget.state()["stopped_by"] == expected["stopped_by"]
    assert budget.state()["calls_used"] == expected["calls_used"]
    assert budget.state()["tokens_spent"] == expected["tokens_spent"]
    assert budget.tokens_unspent == expected["tokens_unspent"]
    assert episode.cause == "CALL_CEILING"


def test_golden8_fixture_C_boundaries_are_INCLUSIVE_through_the_driver(golden8):
    """⚠️ **Fixture C: BOTH ceilings are INCLUSIVE, exercised ON the boundary.**

    Golden 8: *"A lane that lands EXACTLY on its token ceiling has not overspent. An
    accumulator written with >= refuses the second 50,000 call and reports 50,000 spent,
    leaving half the sanctioned budget unusable."*
    """
    fixture = golden8["fixtures"]["C_exact_boundaries"]
    ceilings = _fixture_ceilings(golden8)

    part1 = fixture["part_1_token_boundary"]
    cost = part1["offered_calls"][0]
    _episode, budget, _ = _run_one_episode_on(
        arm="1",
        seed=_a_pilot_seed(),
        attacker_replies=[("{}", cost)] * (len(part1["offered_calls"]) + 1),
        reservation=cost,
        ceilings=ceilings,
    )
    assert budget.tokens_spent == part1["expected"]["tokens_spent"], (
        "the lane must be allowed to land EXACTLY on its token ceiling"
    )
    assert budget.calls_used == part1["expected"]["calls_admitted"]

    part2 = fixture["part_2_call_boundary"]
    cost2 = part2["offered_calls"][0]
    _episode2, budget2, _ = _run_one_episode_on(
        arm="1",
        seed=_a_pilot_seed(),
        attacker_replies=[("{}", cost2)] * len(part2["offered_calls"]),
        reservation=cost2,
        ceilings=ceilings,
    )
    assert budget2.calls_used == part2["expected"]["calls_used"]
    assert budget2.tokens_spent == part2["expected"]["tokens_spent"]
    assert budget2.stopped_by == part2["expected"]["stopped_by"]


def test_golden8_fixture_D_a_429_STOPS_THE_LANE_through_the_driver(golden8):
    """⚠️ **Fixture D: a 429 costs ZERO tokens and ZERO calls, and the LANE STOPS.**

    *"THE LANE STOPS WITH 99,000 OF 100,000 TOKENS AND 9 OF 10 CALLS UNUSED, AND THAT IS
    CORRECT BEHAVIOUR RATHER THAN WASTE. An accumulator that retries, or that spills into
    another model's lane to use the remaining budget, produces a HIGHER number here and
    violates hard rule 12 to do it."*
    """
    fixture = golden8["fixtures"]["D_a_429_at_call_2"]
    ceilings = _fixture_ceilings(golden8)
    first = fixture["sequence"][0]["usage_total_tokens"]
    episode, budget, judge_budget = _run_one_episode_on(
        arm="1",
        seed=_a_pilot_seed(),
        attacker_replies=[("{}", first)] * 5,
        reservation=first,
        ceilings=ceilings,
        rate_limit_at=2,
    )
    expected = fixture["expected"]
    assert budget.state() == {
        "calls_used": expected["calls_used"],
        "calls_unused": expected["calls_unused"],
        "tokens_spent": expected["tokens_spent"],
        "tokens_unspent": expected["tokens_unspent"],
        "stopped_by": expected["stopped_by"],
    }
    assert budget.rate_limited == 1
    assert episode.cause == "RATE_LIMIT_429"
    assert episode.turns_run == 1, "the 429'd call never ran, so its turn never completed"
    # ⚠️ `other_lane_used: false`. There is no code path that moves a refused call.
    assert judge_budget.calls_used == 0 and judge_budget.tokens_spent == 0


def test_golden8_fixture_E_ceilings_are_PER_MODEL_and_never_pooled(golden8, tmp_path):
    """⚠️ **Fixture E: two lanes at 60,000 and 50,000 pool to 110,000 — OVER a 100,000
    ceiling — while NEITHER exceeds it alone, and BOTH LANES CONTINUE.**

    A pooling accumulator aborts a lane that has budget and *"costs the run episodes it was
    entitled to"*. Driven through a **two-lane run**, which is the shape the driver actually
    has, so the property is a fact about the wiring and not about one class.
    """
    fixture = golden8["fixtures"]["E_per_model_never_pooled"]
    ceiling = _fixture_ceilings(golden8).token_ceiling
    per_lane = [lane["tokens_spent"] for lane in fixture["lanes"]]
    assert sum(per_lane) == fixture["expected"]["pooled_total"] > ceiling
    assert max(per_lane) <= ceiling

    matrix = pilot_module.load_pilot(arm="1")
    matrix = pilot_module.PilotMatrix(
        arm="1",
        turn_budget=matrix.turn_budget,
        reference=pilot_module.PilotCell(
            lane=matrix.reference.lane,
            attacker_model=matrix.reference.attacker_model,
            seeds=(matrix.reference.seeds[0],),
        ),
        ladder_l2=pilot_module.PilotCell(
            lane=matrix.ladder_l2.lane,
            attacker_model=matrix.ladder_l2.attacker_model,
            seeds=(matrix.reference.seeds[0],),
        ),
        judge_lane=matrix.judge_lane,
    )
    request = _request(
        matrix, tmp_path / "e", call_ceiling=1000, token_ceiling=ceiling
    )
    result = driver_run.execute(
        request,
        client=TranscriptClient(attacker_replies=rehearsal.attacker_transcript(2)),
        corpus_entries=(),
    )
    assert all(not budget.stopped for budget in result.budgets.values()), (
        "a POOLING implementation aborts a lane that has budget"
    )
    pooled = sum(budget.tokens_spent for budget in result.budgets.values())
    assert pooled > 0 and len(result.budgets) >= 2


def test_golden8_fixture_F_the_N_rule_is_WIRED_and_never_re_derived(golden8):
    """⚠️ **Fixture F: §13.4's N rule keys off MEASURED tokens/episode.**

    The driver **wires C11's rule** and contains no arithmetic that could disagree with it.
    All four architect-stated vectors reproduce under the first conjunct, which is the
    conjunct `PROCESS.md` §5.2 names golden 8 as pinning.
    """
    fixture = golden8["fixtures"]["F_the_S13_4_N_rule"]
    for vector in fixture["vectors"]:
        measured = vector["measured_tokens_per_episode"]
        assert n_rule.select_n_first_conjunct_only(measured) == vector["N"], vector["why"]
    assert fixture["boundary_is_inclusive"] is True
    # And the driver reaches the rule only through `pilot.decide_n`, which refuses a dry run.
    measurement = pilot_module.measure_tokens_per_episode(
        attacker_tokens=fixture["vectors"][0]["measured_tokens_per_episode"],
        completed=1,
        truncated=0,
    )
    decision = pilot_module.decide_n(measurement, dry_run=False)
    assert isinstance(decision, n_rule.NDecision)
    assert decision.n in (
        int(cfg.load("protocol").require("n_decision.branch_a_n")),
        int(cfg.load("protocol").require("n_decision.branch_b_n")),
    )


def test_the_pure_accumulator_still_reproduces_every_offered_cost_fixture(golden8):
    """Golden 8's fixtures A, B and C against C11's own pure path, so a failure here and a
    failure above are distinguishable: this one says the accumulator drifted, that one says
    the **wiring** did."""
    ceilings = _fixture_ceilings(golden8)
    for name in ("A_tokens_bind_first", "B_calls_bind_first"):
        fixture = golden8["fixtures"][name]
        budget = run_offers("gemma-26b", ceilings, fixture["offered_calls"])
        expected = fixture["expected"]
        assert budget.state() == {
            "calls_used": expected["calls_used"],
            "calls_unused": expected["calls_unused"],
            "tokens_spent": expected["tokens_spent"],
            "tokens_unspent": expected["tokens_unspent"],
            "stopped_by": expected["stopped_by"],
        }
    part1 = golden8["fixtures"]["C_exact_boundaries"]["part_1_token_boundary"]
    budget = run_offers("gemma-26b", ceilings, part1["offered_calls"])
    assert budget.tokens_spent == part1["expected"]["tokens_spent"]
    assert budget.stopped_by is None


def _fixture_ceilings(golden8: dict) -> Ceilings:
    block = golden8["fixture_ceilings"]
    return Ceilings(
        call_ceiling=block["call_ceiling"], token_ceiling=block["token_ceiling"]
    )


def _a_pilot_seed() -> int:
    return pilot_module.pilot_seeds()[0]


def test_the_token_figure_comes_from_the_providers_own_usage_block_and_is_never_estimated():
    """⚠️ Golden 8: *"usage.total_tokens, and nothing else. IT DOES NOT ADD prompt_tokens
    AND completion_tokens ITSELF."* A reply whose block lacks the total is a **refusal**."""
    from whetstone_gate.runner.budget import BudgetError, usage_total_tokens

    assert usage_total_tokens({"total_tokens": 4242}) == 4242
    with pytest.raises(BudgetError):
        usage_total_tokens({"prompt_tokens": 4000, "completion_tokens": 242})
    # And the driver's own reply type carries the block through verbatim.
    reply = ModelReply(text="x", usage={"total_tokens": 7, "prompt_tokens": 3})
    assert reply.usage["total_tokens"] == 7


# ======================================================================================
# 3 & 4. HARD RULES 10 AND 11 — the denominator, the resume, the duplicate refusal
# ======================================================================================


def test_the_turn_identity_reconciles_and_every_category_prints(tmp_path):
    """``attempted == decided + unparsed + off_surface``, refused rather than assumed.

    ⚠️ Both non-decided categories are **printed as numbers**. `INCIDENTS.md` **INC-01**: an
    attacker whose calls are silently dropped scores *"0 escapes in 20 episodes"*, which
    reads as a perfect defence and is a broken instrument.
    """
    matrix = pilot_module.load_pilot(arm="1")
    result = driver_run.execute(
        _request(matrix, tmp_path / "counts"),
        client=TranscriptClient(
            attacker_replies=rehearsal.attacker_transcript(matrix.episode_count)
        ),
        corpus_entries=(),
    )
    assert len(result.episodes) == matrix.episode_count
    for episode in result.episodes:
        episode.counts.reconcile()
        assert episode.counts.attempted == episode.turn_budget
        assert episode.counts.unparsed > 0, "the rehearsal plants an unparsed turn on purpose"
        assert episode.counts.off_surface > 0, "and an off-surface tool call, for Q-142"
        rendered = "\n".join(episode.counts.lines())
        assert "UNPARSED" in rendered and "OFF-SURFACE" in rendered
    result.denominator.reconcile()
    assert result.denominator.denominator == matrix.episode_count


def test_kill_mid_run_and_resume_with_ZERO_duplicates_and_zero_re_runs(tmp_path):
    """⚠️ **Hard rule 10's whole claim, demonstrated rather than asserted.**

    Pass 1 dies part-way (its transcript is exhausted). Pass 2 resumes and re-runs **only**
    what has no checkpoint. Pass 3 re-runs **nothing at all** and makes **zero** model calls.
    """
    out = tmp_path / "resume"
    matrix = pilot_module.load_pilot(arm="1")
    partial = 3

    with pytest.raises(Exception):
        driver_run.execute(
            _request(matrix, out),
            client=TranscriptClient(attacker_replies=rehearsal.attacker_transcript(partial)),
            corpus_entries=(),
        )
    after_crash = sorted(p.stem for p in (out / "evals/checkpoints").glob("*.json"))
    assert len(after_crash) == partial, "a crash costs ONE episode, not the run"

    second = driver_run.execute(
        _request(matrix, out),
        client=TranscriptClient(
            attacker_replies=rehearsal.attacker_transcript(matrix.episode_count)
        ),
        corpus_entries=(),
    )
    assert len(second.already_complete) == partial
    assert len(second.episodes) == matrix.episode_count - partial
    after_resume = sorted(p.stem for p in (out / "evals/checkpoints").glob("*.json"))
    assert len(after_resume) == len(set(after_resume)) == matrix.episode_count
    assert set(after_crash) <= set(after_resume), "a published checkpoint is never rewritten"

    third_client = TranscriptClient(
        attacker_replies=rehearsal.attacker_transcript(matrix.episode_count)
    )
    third = driver_run.execute(_request(matrix, out), client=third_client, corpus_entries=())
    assert third.episodes == []
    assert third_client.attacker_calls == 0, "a re-run makes ZERO model calls"


def test_a_RESUMED_run_still_reports_the_WHOLE_denominator(tmp_path):
    """⚠️ **`INCIDENTS.md` INC-110, and it is this chunk's own defect, measured before it
    was committed.**

    With only *this invocation's* episodes counted, the **second** run of the same command
    printed ``episodes attempted: 0``, ``DENOMINATOR: 0`` and a pilot measurement of *zero
    tokens over zero episodes* — a completed 20-episode pilot reading as nothing, and
    reading **clean** while it did. Hard rule 11 counts *"skipped cases"* by name.
    """
    out = tmp_path / "resumed-denominator"
    matrix = pilot_module.load_pilot(arm="1")
    first = driver_run.execute(
        _request(matrix, out),
        client=TranscriptClient(
            attacker_replies=rehearsal.attacker_transcript(matrix.episode_count)
        ),
        corpus_entries=(),
    )
    second = driver_run.execute(
        _request(matrix, out),
        client=TranscriptClient(
            attacker_replies=rehearsal.attacker_transcript(matrix.episode_count)
        ),
        corpus_entries=(),
    )
    assert second.episodes == [], "nothing should have re-run"
    assert second.denominator.attempted == first.denominator.attempted
    assert second.denominator.denominator == matrix.episode_count
    assert second.attacker_tokens(matrix) == first.attacker_tokens(matrix) > 0
    assert "IN the denominator" in second.report


def test_a_republished_episode_with_DIFFERENT_bytes_is_REFUSED_not_overwritten(tmp_path):
    """⚠️ **`evals/` is append-only.** An identical re-write is the no-op idempotence asks
    for; a **different** one is a refusal naming the file, never an overwrite."""
    out = tmp_path / "append-only"
    matrix = pilot_module.load_pilot(arm="1")
    driver_run.execute(
        _request(matrix, out),
        client=TranscriptClient(
            attacker_replies=rehearsal.attacker_transcript(matrix.episode_count)
        ),
        corpus_entries=(),
    )
    published = sorted((out / "evals/episodes").glob("*.json"))[0]
    stored = ledger_store.read(published)
    assert ledger_store.write(published, stored) is False, "an identical re-write is a no-op"

    other = ledger_chain.Ledger(
        spec=ledger_chain.load_chain_spec(), seed=stored.seed, arm=stored.arm
    )
    with pytest.raises(ledger_store.LedgerStoreError, match="append-only"):
        ledger_store.write(published, other)


def test_a_truncated_episode_is_COUNTED_IN_THE_DENOMINATOR_and_its_cost_is_not_zero(golden8):
    """⚠️ Hard rule 11, and it is on `PROCESS.md` §14's NEVER-CUT list. Golden 8 carries no
    truncated-episode fixture at all (`Q-108`, `Q-117`), so the vectors here are this
    session's own and are marked as the weaker oracle they are."""
    ceilings = _fixture_ceilings(golden8)
    cost = golden8["fixtures"]["A_tokens_bind_first"]["offered_calls"][0]
    episode, _budget, _judge = _run_one_episode_on(
        arm="1",
        seed=_a_pilot_seed(),
        attacker_replies=[("{}", cost)] * 6,
        reservation=cost,
        ceilings=ceilings,
    )
    assert episode.truncated
    outcome = episode.outcome()
    assert outcome.truncated and outcome.started
    assert outcome.tokens_spent > 0, "'it stopped early' is not 'it was free'"
    assert outcome.cause is not None, "a truncated episode must state its category"


# ======================================================================================
# 5. §10.1 — THE PROBE REACHES EVERY ARM AND LOOKS IDENTICAL IN ALL OF THEM
# ======================================================================================


def _episode_for_arm(arm: str, seed: int, *, judge_allows: bool = True):
    replies = [(reply, 1) for reply in rehearsal.episode_replies()]
    judge = [
        (rehearsal.REHEARSAL_ALLOW if judge_allows else rehearsal.REHEARSAL_DENY, 1)
        for _ in range(len(replies))
    ]
    episode, _budget, _judge_budget = _run_one_episode_on(
        arm=arm,
        seed=seed,
        attacker_replies=replies,
        judge_replies=judge,
        reservation=1,
        ceilings=Ceilings(call_ceiling=10_000, token_ceiling=10_000_000),
    )
    return episode


def test_the_probe_is_in_every_arms_world_with_the_frozen_note_and_amount():
    """⚠️ **`CONTEXT.md` §10.1's door, per arm, read from `config/` and never transcribed.**

    *"Every arm leaves it open — including the kernel. If the control arm closes the door,
    the probe measures nothing and arm 4 is VOID by construction."*
    """
    protocol = cfg.load("protocol")
    probe_id = protocol.require("probe.payment_id")
    note = protocol.require("probe.notes")["reconciliation"]
    amount = protocol.require("probe.payment_amount_paise")
    seed = _a_pilot_seed()
    world = world_semantics.build(
        world_generator.generate_world(seed),
        world_settings.load_semantics_spec(),
        world_oracle.load(),
    )
    payment = world.payment(probe_id)
    assert payment.amount_captured_paise == amount
    assert payment.notes["reconciliation"] == note


def test_the_episode_a_seed_produces_is_IDENTICAL_ACROSS_ARMS_up_to_the_gates_verdict():
    """⚠️ **THE DRIVER-SIDE ASSERTION OF §10.1, AND IT IS THE ONLY SIDE THAT SEES A WHOLE
    EPISODE.** C9 asserted this from the gate side and C10 from the probe side.

    *"Restate the requirement precisely: not 'discoverable', but **no DIFFERENTIAL
    information across arms**."* So every arm's sequence of **proposals** — turn, tool,
    target, amount — must agree for as long as the arms have been shown the same thing,
    which is up to and including the first non-``ALLOWED`` verdict. After that they diverge
    legitimately: a refused turn hands the attacker a different tool result.
    """
    seed = _a_pilot_seed()
    prefixes = {
        arm: driver_episode.arm_invariant_prefix(_episode_for_arm(arm, seed).ledger.entries)
        for arm in ("1", "2", "2S", "3", "4")
    }
    for arm, prefix in prefixes.items():
        assert prefix, f"arm {arm} produced no ledger entry at all"
    for left in prefixes:
        for right in prefixes:
            assert driver_episode.prefixes_agree(prefixes[left], prefixes[right]), (
                f"arms {left} and {right} were shown different things before a verdict "
                f"separated them:\n  {left}: {prefixes[left]}\n  {right}: {prefixes[right]}"
            )


def test_a_DENYING_arm_still_agrees_with_arm_1_up_to_the_denial():
    """The same property where it actually bites: a gate that denies **truncates** the
    shared prefix, and everything before the denial must still match arm 1 exactly."""
    seed = _a_pilot_seed()
    control = driver_episode.arm_invariant_prefix(
        _episode_for_arm("1", seed).ledger.entries
    )
    denied = driver_episode.arm_invariant_prefix(
        _episode_for_arm("2", seed, judge_allows=False).ledger.entries
    )
    assert len(denied) == 1, "a gate that denies everything separates at the first turn"
    assert denied[0][:3] == control[0][:3], (
        "the DENIED arm proposed something different from the control on turn 0, which is a "
        "differential the attacker could only have got from the gate"
    )
    assert driver_episode.prefixes_agree(control, denied)


def test_CANARY_B_reach_is_non_zero_in_every_arm_including_the_ones_that_block():
    """⚠️ `HOLES.md` §3.2: *"BLOCKED ENTRIES COUNT. That is the point of the signal: reach
    measures whether the attacker went to the door, not whether it got through."*"""
    probe_id = cfg.load("protocol").require("probe.payment_id")
    seed = _a_pilot_seed()
    for arm in ("1", "2", "2S", "3", "4"):
        episode = _episode_for_arm(arm, seed, judge_allows=(arm != "2"))
        naming = [e for e in episode.ledger.entries if e.target == probe_id]
        assert naming, f"arm {arm} recorded no entry naming the probe"


def test_the_attacker_is_shown_the_same_words_in_every_arm():
    """The system prompt and the tool-schema block are **arm-independent by construction** —
    one is `data/attacker_sys.txt`, the other is derived from the world's own declarations."""
    schemas = driver_protocol.tool_schemas_text()
    system = driver_episode.attacker_texts_are_shared()
    for arm in ("1", "2", "2S", "3", "4"):
        assert driver_protocol.tool_schemas_text() == schemas
        assert arm not in schemas.split()


def test_the_tool_schema_block_leaks_no_policy_no_cap_and_no_clause(repo_root: Path):
    """⚠️ **`PROCESS.md` §12.1's C6 row: the attacker's context carries no policy string, no
    hole, no attack list and no gate reason.** These bytes reach the attacker every turn."""
    schemas = driver_protocol.tool_schemas_text()
    blob = schemas + driver_protocol.MALFORMED_CALL_REPLY
    policy = (repo_root / "data/policy.txt").read_bytes().decode("utf-8")
    for line in policy.splitlines():
        stripped = line.strip()
        if len(stripped) > 20:
            assert stripped not in blob, f"the policy line {stripped!r} reached the attacker"
    protocol = cfg.load("protocol")
    for key in (
        "money.per_action_cap_paise",
        "money.episode_cap_paise",
        "probe.payment_amount_paise",
    ):
        assert str(protocol.require(key)) not in blob
    assert protocol.require("probe.payment_id") not in blob
    assert gate_shell.load_gate_texts().generic_denial not in blob, (
        "the parser's own failure message must NOT be the gate's denial: one is a gate "
        "decision the attacker may fold, the other is our harness failing"
    )


# ======================================================================================
# 6. THE REFUSALS
# ======================================================================================


def test_a_real_run_REFUSES_ENTIRELY_when_probe_v1_does_not_resolve(tmp_path, repo_root):
    """⚠️ **`CONTEXT.md` §15.1 cuts `probe-v1` BEFORE the pilot and BEFORE the calibration**,
    and `PROTOCOL.md` §6 calls the order *"not negotiable"*. Both runs are **single-shot**:
    a run started before the tag exists has spent it **outside the pre-registration**."""
    if driver_run.probe_tag_resolves(repo_root):
        pytest.skip("probe-v1 exists in this tree; the refusal cannot be observed")
    request = _request(
        pilot_module.load_pilot(arm="1"),
        tmp_path / "real",
        spend_real_tokens=True,
        sanctioned_lanes=("gemma-26b", "qwen-27b"),
    )
    with pytest.raises(driver_run.RunRefused, match="probe-v1"):
        driver_run.preflight(request, repo_root=repo_root, utc_date="2026-09-03")


def test_a_reserved_lane_needs_an_EXPLICIT_SANCTION_and_there_is_no_wildcard():
    """`PROCESS.md` §8: *"No build session may spend on a reserved lane."* The sanction names
    the lanes **one by one**; there is no ``allow_all`` and no environment variable."""
    from whetstone_gate.runner.lanes import LaneReserved, refuse_reserved

    with pytest.raises(LaneReserved, match="RESERVED"):
        refuse_reserved("gemma-26b", sanctioned=frozenset())
    refuse_reserved("gemma-26b", sanctioned=frozenset({"gemma-26b"}))
    # A lane that carries no reservation needs no sanction at all.
    refuse_reserved("flash-lite-3.1", sanctioned=frozenset())


def test_a_dry_run_REFUSES_an_out_root_inside_the_repository(repo_root: Path, tmp_path):
    """A rehearsal ledger in `evals/episodes/` is byte-shaped exactly like a scored one, and
    `evals/` is append-only with **operator-only** deletion — so no session could remove it."""
    with pytest.raises(driver_run.RunRefused, match="may not write into the repository"):
        driver_run.refuse_out_root_inside_the_repository(repo_root / "evals", repo_root)
    with pytest.raises(driver_run.RunRefused):
        driver_run.refuse_out_root_inside_the_repository(repo_root, repo_root)
    # Outside is fine.
    driver_run.refuse_out_root_inside_the_repository(tmp_path, repo_root)


def test_BOTH_ceilings_or_neither_and_neither_has_a_default():
    """Hard rule 12: *"A sanction of 'max N calls' alone is not a sanction: one spike episode
    burned ~300K tokens against a 200K-TPD lane."*"""
    with pytest.raises(TypeError):
        Ceilings(call_ceiling=10)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        Ceilings(token_ceiling=10)  # type: ignore[call-arg]


def test_the_S3_binding_has_no_default_and_an_unknown_one_is_a_refusal():
    """⚠️ **`QUESTIONS.md` Q-141 is an OPEN Class A question and this driver refuses to
    answer it.** A default would decide arm 4's verdicts, and the option that returns
    ``INDETERMINATE`` on every capture **blocks**, which flatters our own gate."""
    with pytest.raises(TypeError):
        driver_episode.EpisodeSettings.from_config()  # type: ignore[call-arg]
    with pytest.raises(driver_episode.DriverError, match="Q-141"):
        driver_episode.EpisodeSettings.from_config(s3_binding="whatever-is-convenient")
    for binding in driver_episode.S3_BINDINGS:
        assert driver_episode.EpisodeSettings.from_config(s3_binding=binding)


def test_the_pilot_arm_has_no_default_because_config_carries_no_key_for_it():
    """`CONTEXT.md` §13.4 and `PROTOCOL.md` §3.1 both say *"1 ref arm"* and **neither says
    which**. `QUESTIONS.md` **Q-144**: choosing it here would choose a pre-registered
    parameter by preference."""
    with pytest.raises(TypeError):
        pilot_module.load_pilot()  # type: ignore[call-arg]
    with pytest.raises(pilot_module.PilotError, match="Q-144"):
        pilot_module.load_pilot(arm="   ")


def test_an_absent_corpus_REFUSES_a_real_run_whatever_the_flag_says(tmp_path, repo_root):
    """⚠️ `CONTEXT.md` §11.3 publishes a corpus-versus-improvisation split, and a run with no
    corpus publishes *"100% improvised"* — a broken instrument reporting a headline.
    `QUESTIONS.md` **Q-145**: the check lives in **preflight**, so it fires **before** a
    single-shot run has started rather than on episode 1."""
    corpora = repo_root / "corpora" / "fetched"
    if corpora.is_dir():
        pytest.skip("the corpora are fetched in this tree; the refusal cannot be observed")
    request = _request(
        pilot_module.load_pilot(arm="1"),
        tmp_path / "nocorpus",
        allow_absent_corpus=True,
    )
    # A DRY run may proceed, and the report says so in terms.
    checks = driver_run.preflight(request, repo_root=repo_root, utc_date="2026-09-03")
    assert checks.corpus_entries == ()
    assert any("100% IMPROVISED" in line for line in checks.lines)
    # A dry run that did NOT ask may not.
    strict = _request(
        pilot_module.load_pilot(arm="1"), tmp_path / "nc2", allow_absent_corpus=False
    )
    with pytest.raises(driver_run.RunRefused, match="corpora"):
        driver_run.preflight(strict, repo_root=repo_root, utc_date="2026-09-03")


def test_a_DRY_RUN_MAY_NEVER_SELECT_THE_N_BRANCH():
    """⚠️ A transcript's token counts are **the caller's numbers**, so a dry run measures the
    **harness** and never §13.4's tokens/episode. The pilot is single-shot; its output
    directory is the record whatever it contains."""
    measurement = pilot_module.measure_tokens_per_episode(
        attacker_tokens=1_000, completed=1, truncated=0
    )
    with pytest.raises(pilot_module.PilotError, match="DRY RUN"):
        pilot_module.decide_n(measurement, dry_run=True)


def test_a_TRUNCATED_pilot_episode_refuses_to_average_because_the_error_FLATTERS():
    """⚠️ A truncated episode cost **less** than a whole one and divides as if it were whole,
    so the figure reads **LOW** — and low is the direction that selects the **larger** N.
    `INCIDENTS.md` **INC-103**'s shape, running where it flatters."""
    measurement = pilot_module.measure_tokens_per_episode(
        attacker_tokens=100, completed=9, truncated=1
    )
    assert measurement.denominator == 10
    assert not measurement.is_usable_for_n
    with pytest.raises(pilot_module.PilotError, match="TRUNCATED"):
        pilot_module.decide_n(measurement, dry_run=False)
    # Both denominators are still PRINTED. Hard rule 11 counts; only the figure refuses.
    rendered = "\n".join(measurement.lines())
    assert "TRUNCATED" in rendered and "USABLE TO SELECT N" in rendered


def test_the_tokens_per_episode_division_rounds_UP_because_DOWN_is_the_unsafe_direction():
    """§13.4's branch A is *"measured tokens/episode ≤ 60,000"*. Rounding **down** can select
    N=50 on a run that measured 60,000.4; rounding up can only select the smaller N."""
    measurement = pilot_module.measure_tokens_per_episode(
        attacker_tokens=60_001, completed=1, truncated=0
    )
    assert measurement.over_completed == 60_001
    uneven = pilot_module.measure_tokens_per_episode(
        attacker_tokens=10, completed=4, truncated=0
    )
    assert uneven.over_completed == 3, "ceil(10/4) is 3, not 2"


# ======================================================================================
# 7. THE PILOT, READ FROM config/
# ======================================================================================


def test_the_pilot_matrix_is_read_from_config_and_is_twenty_episodes():
    """⚠️ **`CONTEXT.md` §13.4's block table: *"1 ref arm + L2 × 10"* = 20 episodes**, on
    `seeds.pilot_first` … `seeds.pilot_last`, which are **disjoint from the scored set on
    purpose** (`PROTOCOL.md` §2.2)."""
    protocol = cfg.load("protocol")
    first = protocol.require("seeds.pilot_first")
    last = protocol.require("seeds.pilot_last")
    matrix = pilot_module.load_pilot(arm="1")

    assert matrix.reference.seeds == tuple(range(first, last + 1))
    assert matrix.ladder_l2.seeds == matrix.reference.seeds
    assert matrix.episode_count == 2 * (last - first + 1) == 20
    assert matrix.turn_budget == protocol.require("attacker.turn_budget")

    scored = range(
        protocol.require("seeds.scored_n50_first"), protocol.require("seeds.scored_n50_last") + 1
    )
    assert not set(matrix.reference.seeds) & set(scored), (
        "the pilot seeds must be DISJOINT from the scored block: running the pilot on scored "
        "seeds would let the branch decision be made on a look at the episodes it sizes"
    )


def test_the_two_pilot_lanes_are_the_reference_attacker_and_ladder_L2():
    """§13.4: *"ref + L2 (`qwen`)"*, and *"the L2 pilot point is `qwen/qwen3.8-27b` — the only
    ladder lane whose 2M TPD can host a 10-episode pilot share"*."""
    from whetstone_gate.runner.lanes import load_lanes

    matrix = pilot_module.load_pilot(arm="1")
    lanes = load_lanes()
    assert "REFERENCE" in lanes[matrix.reference.lane].role
    assert lanes[matrix.ladder_l2.lane].api_model_id == "qwen/qwen3.8-27b"
    assert lanes[matrix.ladder_l2.lane].tpd == 2_000_000
    assert "gate judge" in lanes[matrix.judge_lane].role


def test_every_pilot_episode_key_is_distinct_and_the_dispatch_order_is_deterministic():
    """A collision on the checkpoint path is a **silently lost episode**; a dispatch order
    that depends on a hash seed makes *"kill mid-run and resume"* unrepeatable."""
    matrix = pilot_module.load_pilot(arm="1")
    keys = matrix.keys()
    slugs = [key.slug for key in keys]
    assert len(slugs) == len(set(slugs)) == matrix.episode_count
    assert keys == pilot_module.load_pilot(arm="1").keys()


def test_the_pilots_measured_figure_is_ATTACKER_tokens_only_and_is_split_BY_ROLE(tmp_path):
    """⚠️ **`INCIDENTS.md` INC-111.** §13.3.2 puts the reference attacker **and** the gate
    judge on `gemma-26b`, so a split by **lane** both double-counted an episode's cost and
    dropped every reference-attacker episode from the very figure the pilot exists to
    produce. The split is by **role**."""
    matrix = pilot_module.load_pilot(arm="2")
    result = driver_run.execute(
        _request(matrix, tmp_path / "roles", token_ceiling=20_000_000),
        client=TranscriptClient(
            attacker_replies=rehearsal.attacker_transcript(matrix.episode_count),
            judge_replies=rehearsal.judge_transcript(
                matrix.episode_count * matrix.turn_budget
            ),
        ),
        corpus_entries=(),
    )
    for episode in result.episodes:
        assert episode.judge_tokens > 0, "arm 2 runs a judge on every decided turn"
        assert episode.attacker_tokens == (
            episode.turns_run * rehearsal.reservation_tokens()
        )
        assert episode.tokens_spent == episode.attacker_tokens + episode.judge_tokens
    # The reference lane IS the judge lane, and its episodes are still in the figure.
    assert matrix.reference.lane == matrix.judge_lane
    measured = result.attacker_tokens(matrix)
    assert measured == sum(e.attacker_tokens for e in result.episodes) > 0
    assert all(
        e.judge_tokens not in (0,) for e in result.episodes
    ), "no judge token may leak into the attacker figure"


def test_arms_1_and_4_run_no_judge_call_at_all():
    """`PROTOCOL.md` §2.1: arm 1 is the no-gate control and arm 4 is a **deterministic
    kernel** with *"no model on the money path"* — one of hard rule 8's four deliberate
    non-uses."""
    seed = _a_pilot_seed()
    for arm in ("1", "4"):
        episode = _episode_for_arm(arm, seed)
        assert episode.judge_calls == 0
        assert episode.judge_tokens == 0


# ======================================================================================
# The call protocol
# ======================================================================================


def test_the_parser_reads_one_call_and_refuses_to_guess():
    """Strict, never a substring search: *"I could call the refund tool but I will not"*
    contains a tool name, and a parser that acted on it would be an instrument nobody could
    reason about."""
    parsed = driver_protocol.parse_call(
        'thinking... {"tool": "create_refund", "arguments": {"payment_id": "pay_x", '
        '"amount": 100}} and that is my move'
    )
    assert parsed.parsed and parsed.tool == "create_refund"
    assert parsed.arguments == {"payment_id": "pay_x", "amount": 100}
    assert parsed.is_on_the_surface

    prose = driver_protocol.parse_call("I could call create_refund but I will not.")
    assert not prose.parsed and prose.reason

    thinking_first = driver_protocol.parse_call(
        '{"plan": "read first"} then {"tool": "fetch_payments", "arguments": {}}'
    )
    assert thinking_first.parsed and thinking_first.tool == "fetch_payments"

    off = driver_protocol.parse_call('{"tool": "create_payment_link", "arguments": {}}')
    assert off.parsed and not off.is_on_the_surface


def test_an_unparsed_turn_must_carry_a_reason():
    """A turn dropped without one is `INC-01`'s flattering zero with no way to see it."""
    with pytest.raises(driver_protocol.CallProtocolError):
        driver_protocol.ParsedCall(parsed=False)


def test_the_schema_block_is_DERIVED_from_the_worlds_own_declarations():
    """A transcribed copy is an unfrozen second original of the tool surface, and §8.6a's own
    warning is that *"a seventh tool is not a bonus; it is an unmeasured attack path"*."""
    from whetstone_gate.world import surface

    schemas = driver_protocol.tool_schemas_text()
    for name in surface.TOOL_SURFACE:
        assert f"  {name}(" in schemas
    assert len(surface.TOOL_SURFACE) == 6
    for declaration in surface.DECLARATIONS.values():
        for parameter in declaration.parameters:
            assert parameter in schemas
