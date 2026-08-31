"""C3 — the τ²-bench enumeration, re-derived and diffed against the specification.

⚠️ **WHERE THE EXPECTED VALUES COME FROM, BECAUSE THAT IS THE WHOLE QUESTION.**

C3 is a `full` chunk with **no golden**, and `QUESTIONS.md` **Q-020** rules why that is not
a hard-rule-3 violation: *C3's golden is τ²-bench itself at the pinned SHA.* Rule 3 exists
because *"a test whose expected value was produced by the code it tests proves nothing."*
C3's expected values are **Sierra's task files, read from an unmodified third-party
checkout** — external by construction, which is the strongest form of what rule 3 protects.
This is `QUESTIONS.md` **Q-016**'s reasoning (C1's golden is Razorpay's own documentation)
applied to C3.

So these tests take their two sides from two places, and **neither side is transcribed
into this file**:

  * one side is **parsed out of `CONTEXT.md` §11.1 and §13.4** — the law, written by the
    architect before this chunk existed;
  * the other is **derived from the vendored checkout** by
    :mod:`whetstone_gate.tau2.enumerate`.

A number written into this file by hand would be a third copy that can drift from both,
which is exactly the defect `test_every_s86_row_reaches_the_registry` was added to close.
The parsers therefore assert that they matched, because *a parser that silently reads
nothing is the same class of defect as the check it replaces.*
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from whetstone_gate import config as cfg
from whetstone_gate.tau2 import enumerate as tau2_enum

# ======================================================================================
# Parsing the law. Nothing below transcribes a number.
# ======================================================================================


def _section(markdown: str, heading: str) -> str:
    """Return one section of a markdown document, whitespace-normalised.

    Normalised because `CONTEXT.md` wraps its prose, and §11.1's counts straddle line
    breaks mid-phrase — *"and **10 of 114\\n  retail**"*. A regex written against the raw
    text would match on the author's line width.
    """
    lines = markdown.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(heading))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("#")), len(lines))
    return re.sub(r"\s+", " ", " ".join(lines[start:end]))


def _one(pattern: str, text: str, what: str) -> tuple[str, ...]:
    """Return the single match's groups, or fail loudly rather than reading nothing."""
    matches = re.findall(pattern, text)
    assert len(matches) == 1, (
        f"the {what} parser matched {len(matches)} times in CONTEXT.md, not once. Either "
        f"the specification was reworded or this parser stopped seeing it — and a parser "
        f"that silently reads nothing reports green over an unchecked claim."
    )
    return matches[0] if isinstance(matches[0], tuple) else (matches[0],)


def _int(text: str) -> int:
    return int(text.replace(",", ""))


@pytest.fixture(scope="module")
def spec_11_1(repo_root: Path) -> str:
    return _section((repo_root / "CONTEXT.md").read_text(encoding="utf-8"), "## 11.1 ")


@pytest.fixture(scope="module")
def spec_13_4(repo_root: Path) -> str:
    return _section((repo_root / "CONTEXT.md").read_text(encoding="utf-8"), "## 13.4 ")


@pytest.fixture(scope="module")
def enumeration() -> tau2_enum.Enumeration:
    return tau2_enum.enumerate_tau2()


# ======================================================================================
# TASK 1 — the enumeration.
# ======================================================================================


def test_the_vendored_checkout_is_at_the_commit_config_pins(enumeration):
    """Everything else in this file is meaningless if this is not true.

    The external-answer-key claim rests entirely on this checkout being the one
    `PROTOCOL.md` pre-registers.
    """
    assert enumeration.vendor_sha == tau2_enum.pinned_sha()
    assert tau2_enum.vendored_head_sha() == tau2_enum.pinned_sha()


def test_the_must_not_write_split_reproduces_from_the_pinned_sha(enumeration, spec_11_1):
    """⚠️ **The single most checkable claim in the specification, re-derived.**

    `CONTEXT.md` §11.1 says *"The spec's 34/164 figure is exactly right"* and states six
    sub-counts. All six are parsed back out of §11.1 and diffed against the checkout. A
    divergence means either the spec is wrong or the enumeration is, and both outrank
    finishing the chunk.
    """
    total_mnw, total_tasks = (int(x) for x in _one(r"\*\*(\d+) of (\d+) tasks\*\*", spec_11_1, "34/164"))
    air_mnw, air_total, air_empty, air_read = (
        int(x)
        for x in _one(
            r"\*\*(\d+) of (\d+) airline\*\* \((\d+) with an empty action list, (\d+) read-only\)",
            spec_11_1,
            "airline",
        )
    )
    ret_mnw, ret_total, ret_empty, ret_read = (
        int(x)
        for x in _one(
            r"\*\*(\d+) of (\d+) retail\*\* \((\d+) empty, (\d+) read-only\)",
            spec_11_1,
            "retail",
        )
    )

    airline = enumeration.by_domain("airline")
    retail = enumeration.by_domain("retail")

    assert (enumeration.must_not_write_count, enumeration.total) == (total_mnw, total_tasks)
    assert (airline.must_not_write_count, airline.total) == (air_mnw, air_total)
    assert (len(airline.empty_action_ids), len(airline.read_only_ids)) == (air_empty, air_read)
    assert (retail.must_not_write_count, retail.total) == (ret_mnw, ret_total)
    assert (len(retail.empty_action_ids), len(retail.read_only_ids)) == (ret_empty, ret_read)


def test_the_write_task_count_reproduces_as_the_complement(enumeration, spec_11_1):
    """§11.1's *"130 write tasks"*, and that they really are the complement."""
    (declared,) = _one(r"\*\*(\d+) write tasks\*\*", spec_11_1, "130 write tasks")
    assert enumeration.write_count == int(declared)
    assert enumeration.must_not_write_count + enumeration.write_count == enumeration.total


def test_every_partition_sums_to_its_total(enumeration):
    """`PROCESS.md` §9: counts sum to the total; every item in exactly one category."""
    for domain in enumeration.domains:
        buckets = (domain.empty_action_ids, domain.read_only_ids, domain.write_ids)
        assert sum(len(bucket) for bucket in buckets) == domain.total
        assert domain.must_not_write_count + domain.write_count == domain.total
        seen: set[str] = set()
        for bucket in buckets:
            assert not seen & set(bucket), f"{domain.domain}: an id is in two buckets"
            seen |= set(bucket)
        assert len(seen) == domain.total

    assert enumeration.total == sum(domain.total for domain in enumeration.domains)


def test_the_config_counts_agree_with_the_checkout():
    """`config/` pre-registers 34 and 130. They are read, never assumed to be right."""
    protocol = cfg.load("protocol")
    enumeration = tau2_enum.enumerate_tau2()
    assert enumeration.must_not_write_count == protocol.require(
        "selections.tau2_must_not_write_task_count"
    )
    assert enumeration.write_count == protocol.require("selections.tau2_write_task_count")


def test_the_reward_basis_census_reproduces(enumeration, spec_11_1):
    """§11.1's census: 50 airline `[DB, COMMUNICATE]`; 112 + 2 retail."""
    (air_total,) = _one(
        r"all \*\*(\d+)\*\* airline tasks are `\[DB, COMMUNICATE\]`", spec_11_1, "airline basis"
    )
    ret_total, ret_nl, ret_db = _one(
        r"of the \*\*(\d+)\*\* retail tasks, \*\*(\d+)\*\* are `\[DB, NL_ASSERTION\]` and "
        r"\*\*(\d+)\*\* are `\[DB\]`",
        spec_11_1,
        "retail basis",
    )

    assert dict(enumeration.by_domain("airline").reward_basis_census) == {
        ("COMMUNICATE", "DB"): int(air_total)
    }
    assert dict(enumeration.by_domain("retail").reward_basis_census) == {
        ("DB", "NL_ASSERTION"): int(ret_nl),
        ("DB",): int(ret_db),
    }
    assert enumeration.by_domain("retail").total == int(ret_total)


def test_telecom_is_excluded_for_the_structural_reason_and_the_counts_reproduce(spec_11_1):
    """⚠️ **The REASON is asserted, not the conclusion.**

    §11.1 withdrew an unsourced *"unsound"* claim about telecom and replaced it with a
    structural fact. This re-derives the fact: no telecom task's ``reward_basis`` carries
    ``DB``, so there is no DB-hash write signal and telecom cannot host the control.
    """
    env_only, telecom_total, env_and_action = _one(
        r"reward basis is `\[ENV_ASSERTION\]` on ([\d,]+) of its ([\d,]+) tasks and "
        r"`\[ENV_ASSERTION, ACTION\]` on the other (\d+)",
        spec_11_1,
        "telecom",
    )

    census = dict(tau2_enum.telecom_reward_basis_census())
    assert census == {
        ("ENV_ASSERTION",): _int(env_only),
        ("ACTION", "ENV_ASSERTION"): _int(env_and_action),
    }
    assert sum(census.values()) == _int(telecom_total)
    assert tau2_enum.telecom_reward_basis_includes_db() is False


# ======================================================================================
# The write-tool set comes from the decorator.
# ======================================================================================


def test_write_tools_are_read_from_tau2s_own_decorator(enumeration):
    """No hand-list. A hand-list is an answer key we authored.

    Asserted structurally: every name the enumeration calls a write tool carries
    ``@is_tool(ToolType.WRITE)`` on its ``def`` in τ²-bench's own source, and every such
    ``def`` is in the set. The expected values are the decorators; there is no third list.
    """
    for domain in enumeration.domains:
        source = tau2_enum.read_tools_source(domain.domain)
        from_decorator = {
            node.name
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.FunctionDef)
            for decorator in node.decorator_list
            if isinstance(decorator, ast.Call)
            and getattr(decorator.func, "id", None) in tau2_enum.TOOL_DECORATORS
            and decorator.args
            and isinstance(decorator.args[0], ast.Attribute)
            and decorator.args[0].attr == tau2_enum.WRITE_TOOL_TYPE
        }
        assert from_decorator, f"{domain.domain}: no write decorators found at all"
        assert set(domain.write_tools) == from_decorator


def test_a_tool_whose_decorator_cannot_be_read_is_a_refusal_not_a_silent_read_tool():
    """The failure is not symmetric, so it must not default.

    An unreadable write tool would move its task **into** the must-not-write control,
    inflating the one number §11.1 calls the externally-authored competence check.
    """
    with pytest.raises(tau2_enum.EnumerationError):
        tau2_enum.tool_types(
            "def f():\n    pass\n"
            "@is_tool(SOMETHING_ELSE)\n"
            "def g(self):\n    pass\n"
        )


def test_a_source_with_no_decorated_tools_is_a_refusal():
    """A parser that reads nothing must not report an empty write set as a clean one."""
    with pytest.raises(tau2_enum.EnumerationError):
        tau2_enum.tool_types("def not_a_tool(self):\n    pass\n")


# ======================================================================================
# TASK 2 — T-FP and the ruled sort.
# ======================================================================================


def test_the_spec_still_says_first_40_stratified_20_and_20(spec_13_4):
    """The pre-registration in `config/` is checked against §13.4's own sentence."""
    count, airline, retail = _one(
        r"takes the \*\*first (\d+) write-task ids after sorting, stratified (\d+) airline / "
        r"(\d+) retail\.\*\*",
        spec_13_4,
        "T-FP rule",
    )
    protocol = cfg.load("protocol")
    assert protocol.require("selections.tfp_task_count") == int(count)
    assert protocol.require("selections.tfp_stratification.airline") == int(airline)
    assert protocol.require("selections.tfp_stratification.retail") == int(retail)


def test_the_tfp_selection_is_the_first_n_of_the_bytewise_string_sort(enumeration):
    quota = tau2_enum.tfp_quota()
    selection = tau2_enum.tfp_selection(enumeration, quota)
    for domain, ids in selection.items():
        write_ids = enumeration.by_domain(domain).write_ids
        assert list(ids) == sorted(write_ids)[: quota[domain]]
        assert len(ids) == quota[domain]
        assert set(ids) <= set(write_ids)
    assert sum(len(ids) for ids in selection.values()) == cfg.load("protocol").require(
        "selections.tfp_task_count"
    )


def test_the_ruled_sort_is_not_the_sort_a_numeric_reading_would_give(enumeration):
    """⚠️ **Why the ruling was needed at all — and why this assertion is not a tautology.**

    τ²'s ids are decimal strings, so bytewise and numeric order genuinely disagree and
    select **different tasks**. If this ever stopped being true the ruling would be
    decorative, and a reader should be told rather than left assuming it mattered.
    """
    differed = 0
    for domain in enumeration.domains:
        write_ids = list(domain.write_ids)
        bytewise = sorted(write_ids)
        numeric = sorted(write_ids, key=int)
        quota = tau2_enum.tfp_quota()[domain.domain]
        if bytewise[:quota] != numeric[:quota]:
            differed += 1
    assert differed == len(enumeration.domains), (
        "the bytewise and numeric sorts select the same sample in some domain, so the "
        "architect's sort ruling would not be load-bearing there. Say so rather than "
        "letting this assertion imply a difference that is not there."
    )


def test_a_domain_with_fewer_write_tasks_than_its_quota_is_a_refusal(enumeration):
    """Hard rule 11's shape, one step earlier: no silently short sample."""
    with pytest.raises(tau2_enum.EnumerationError):
        tau2_enum.tfp_selection(enumeration, {"airline": 10_000, "retail": 1})


def test_non_ascii_ids_are_a_refusal_because_the_ruled_sort_is_bytewise():
    with pytest.raises(tau2_enum.EnumerationError):
        tau2_enum.sort_task_ids(["1", "é"])


# ======================================================================================
# The committed pre-registration, diffed against the checkout.
# ======================================================================================


def test_the_committed_selections_still_match_the_pinned_checkout(enumeration):
    """⚠️ `config/` is a pre-registration artefact; this is what keeps it honest.

    The ids in `config/protocol.yaml` were derived from this checkout and hand-written into
    that file. This re-derives them and diffs. A mangled or drifted id is a test failure
    here, not a discovery made after the sweep — which matters because
    `INCIDENTS.md` INC-06, INC-10, INC-12, INC-13 and INC-16 are five occurrences in this
    project of literal text mangled between a tool call and a file.
    """
    assert tau2_enum.committed_must_not_write_ids() == enumeration.must_not_write_ids_by_domain
    assert tau2_enum.committed_tfp_ids() == tau2_enum.tfp_selection(
        enumeration, tau2_enum.tfp_quota()
    )


def test_every_committed_id_is_a_string(enumeration):
    """Unquoted, YAML turns ``"0"`` into ``0`` and the selection matches no task at all."""
    for committed in (tau2_enum.committed_must_not_write_ids(), tau2_enum.committed_tfp_ids()):
        for domain, ids in committed.items():
            assert all(isinstance(task_id, str) for task_id in ids), domain


def test_the_domains_config_pre_registers_are_the_domains_this_adapter_reads():
    committed = cfg.load("protocol").require("selections.tau2_must_not_write_task_ids")
    assert set(committed) == set(tau2_enum.DOMAINS)
    assert tau2_enum.EXCLUDED_DOMAIN not in committed


def test_a_checkout_that_is_not_at_the_pin_is_a_refusal(monkeypatch):
    """The pin check must be able to go red, or it is decorative."""
    monkeypatch.setattr(tau2_enum, "pinned_sha", lambda: "0" * 40)
    with pytest.raises(tau2_enum.VendorError):
        tau2_enum.assert_vendor_at_pin()


# ======================================================================================
# TASK 3 — the db_reward non-use, asserted over the db_reward PATH.
# ======================================================================================

#: Text-generation model clients. τ²-bench's own single model-client module is
#: ``tau2.utils.llm_utils`` (it defines ``generate``); the rest are the SDKs it and the
#: voice stack reach for.
TEXT_GENERATION_CLIENTS = frozenset(
    {
        "litellm",
        "openai",
        "anthropic",
        "cohere",
        "mistralai",
        "groq",
        "google",
        "boto3",
        "aws_sdk_bedrock_runtime",
        "transformers",
        "vllm",
        "huggingface_hub",
    }
)

#: The τ² modules that would put a model **on the reward path** if they were reachable.
MODEL_BEARING_TAU2_MODULES = frozenset(
    {"tau2.utils.llm_utils", "tau2.evaluator.evaluator_nl_assertions"}
)

#: Where ``db_reward`` is computed: ``EnvironmentEvaluator.calculate_reward``.
DB_REWARD_MODULE = "tau2.evaluator.evaluator_env"


def _vendor_src(repo_root: Path) -> Path:
    return repo_root / "vendor" / tau2_enum.VENDOR_DIRNAME / "src"


def _module_file(src: Path, module: str) -> Path | None:
    flat = src / (module.replace(".", "/") + ".py")
    if flat.is_file():
        return flat
    package = src / module.replace(".", "/") / "__init__.py"
    return package if package.is_file() else None


def _imports(path: Path, module: str) -> set[str]:
    """Every dotted name this module imports at module level, absolute and relative."""
    package = module if path.name == "__init__.py" else module.rpartition(".")[0]
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parts = package.split(".")
                root = ".".join(parts[: len(parts) - (node.level - 1)] if node.level > 1 else parts)
                base = f"{root}.{node.module}" if node.module else root
            else:
                base = node.module or ""
            found.add(base)
            found |= {f"{base}.{alias.name}" for alias in node.names}
    return found


def _closure(src: Path, start: str) -> tuple[set[str], set[str]]:
    """Walk ``start``'s transitive module-level imports inside the vendored tree.

    Returns ``(first_party_modules, third_party_roots)``. Package ``__init__`` side effects
    are deliberately **not** followed — see
    :func:`test_importing_any_tau2_module_loads_a_model_client_through_the_package_init`,
    which states that fact rather than letting this walk hide it.
    """
    first_party: set[str] = set()
    third_party: set[str] = set()
    stack = [start]
    while stack:
        module = stack.pop()
        if module in first_party:
            continue
        path = _module_file(src, module)
        if path is None:
            if not module.startswith("tau2"):
                third_party.add(module.split(".")[0])
            continue
        first_party.add(module)
        for imported in _imports(path, module):
            if imported.startswith("tau2"):
                stack.append(imported)
            elif imported:
                third_party.add(imported.split(".")[0])
    return first_party, third_party


def test_the_db_reward_path_reaches_no_text_generation_client(repo_root):
    """⚠️ **The claim this project publishes, tested over the PATH WE CALL.**

        "We score on `db_reward` alone — a hash comparison, no model. τ²-bench's full
        retail reward multiplies in an LLM-judged natural-language assertion, and we do
        not use it."

    A walk over τ²-bench **as a whole** would fail correctly and prove nothing: τ² does
    contain an LLM path, legitimately, on a code path we never call.
    """
    modules, third_party = _closure(_vendor_src(repo_root), DB_REWARD_MODULE)
    assert DB_REWARD_MODULE in modules
    assert not (third_party & TEXT_GENERATION_CLIENTS), sorted(third_party & TEXT_GENERATION_CLIENTS)
    assert not (modules & MODEL_BEARING_TAU2_MODULES), sorted(modules & MODEL_BEARING_TAU2_MODULES)


def test_the_import_walk_can_go_red_on_the_path_that_really_does_call_a_model(repo_root):
    """`ai-playbook` B.9: *a release gate that has never gone red is only decorative.*

    Pointed at ``evaluator_nl_assertions`` — the LLM-judged path we deliberately do not
    use — the same walk **must** find both the client SDK and τ²'s own ``generate``.
    """
    modules, third_party = _closure(
        _vendor_src(repo_root), "tau2.evaluator.evaluator_nl_assertions"
    )
    assert "litellm" in third_party
    assert "tau2.utils.llm_utils" in modules


def test_the_only_provider_sdk_on_the_db_reward_path_is_a_guarded_type_import(repo_root):
    """⚠️ **Stated rather than swallowed by a denylist that happens not to mention it.**

    One provider SDK name **is** reachable from the db_reward path: ``elevenlabs``, a
    speech-synthesis SDK, imported by ``tau2.data_model.voice`` for a pydantic type. It is
    wrapped in ``try: … except ImportError``, it is not installed here, and nothing on the
    reward path calls it. That is not a text-generation client and it does not touch the
    claim above — but it is a fact a reader would find on their own, so this test says it
    first and pins it, so it cannot quietly become something else.
    """
    src = _vendor_src(repo_root)
    modules, _ = _closure(src, DB_REWARD_MODULE)

    reachers = sorted(
        module
        for module in modules
        if any(
            name == "elevenlabs" or name.startswith("elevenlabs.")
            for name in _imports(_module_file(src, module), module)
        )
    )
    assert reachers == ["tau2.data_model.voice"]

    tree = ast.parse(_module_file(src, "tau2.data_model.voice").read_text(encoding="utf-8"))
    guarded = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Try)
        for child in ast.walk(node)
        if isinstance(child, ast.ImportFrom) and child.module == "elevenlabs"
    ]
    assert guarded, "the elevenlabs import is no longer inside a try/except ImportError"


def test_importing_any_tau2_module_loads_a_model_client_through_the_package_init(repo_root):
    """⚠️ **The fact a naive runtime check would hide, asserted so nobody claims otherwise.**

    ``vendor/tau2-bench/src/tau2/__init__.py`` imports the whole framework — agents, the
    user simulator, the runner — so **importing any `tau2.*` module executes it and loads
    `litellm` into the process**, at a measured ~22 s. That is a property of Python package
    initialisation, **not** of the db_reward path, and it is precisely why the test above
    is a static module-graph walk and why
    :mod:`whetstone_gate.tau2.enumerate` imports no τ² module at all.

    It is also why *"no model client is ever loaded in our process"* would be a **false**
    sentence, and this project has already had to withdraw four claims about third-party
    code. So the true, narrower sentence is the one it publishes.
    """
    init = _module_file(_vendor_src(repo_root), "tau2")
    assert init is not None and init.name == "__init__.py"
    imported = _imports(init, "tau2")
    assert "tau2.agent.llm_agent" in imported

    modules, third_party = _closure(_vendor_src(repo_root), "tau2.agent.llm_agent")
    assert "tau2.utils.llm_utils" in modules
    assert "litellm" in third_party


def test_the_two_source_lines_the_specification_cites_are_still_there(repo_root):
    """§11.1 cites two exact locations. Both are re-verified at the pinned SHA.

    This project has shipped four false claims about third-party code; a cited line number
    that has drifted is the fifth, and it is cheap to check.
    """
    src = _vendor_src(repo_root)
    nl_lines = (src / "tau2" / "evaluator" / "evaluator_nl_assertions.py").read_text(
        encoding="utf-8"
    ).splitlines()
    assert nl_lines[120].strip() == "assistant_message = generate("
    assert nl_lines[121].strip() == "model=DEFAULT_LLM_NL_ASSERTIONS,"

    config_lines = (src / "tau2" / "config.py").read_text(encoding="utf-8").splitlines()
    assert config_lines[23].startswith("DEFAULT_LLM_NL_ASSERTIONS = ")


# ======================================================================================
# TASK 4 — the adapter reads the grader, it does not reimplement it.
# ======================================================================================


def _adapter_code(repo_root: Path) -> dict[str, str]:
    """The adapter's source with comments and docstrings removed.

    Prose *about* the hash comparison is not a reimplementation of it — the same
    distinction ``tests/test_tripwire_registry.py`` draws, and for the same reason.
    """
    package = repo_root / "src" / "whetstone_gate" / "tau2"
    stripped = {}
    for path in sorted(package.rglob("*.py")):
        text = re.sub(r'("""|\'\'\')(?:.|\n)*?\1', '""', path.read_text(encoding="utf-8"))
        stripped[path.name] = re.sub(r"#[^\n]*", "", text)
    return stripped


#: The shapes a reimplemented DB-hash grader would take.
GRADER_TOKENS = (
    "hashlib",
    "sha256",
    "sha1",
    "md5",
    "hexdigest",
    "digest",
    "get_db_hash",
    "db_hash",
    "db_reward",
    "calculate_reward",
    "DBCheck",
)


def _grader_findings(sources: dict[str, str]) -> list[str]:
    return [
        f"{name}: {token}"
        for name, code in sources.items()
        for token in GRADER_TOKENS
        if re.search(rf"(?<![\w.]){re.escape(token)}(?![\w])", code)
    ]


def test_the_adapter_does_not_reimplement_the_hash_comparison(repo_root):
    """⚠️ **A reimplemented grader is an answer key we authored.**

    ``db_reward`` is τ²-bench's: *"`db_reward = 1.0` iff the predicted DB hash also equals
    the initial hash."* It is **called**, never rebuilt. Nothing in this package hashes a
    database or compares two hashes, and the whole point of the chunk collapses if it does.
    """
    findings = _grader_findings(_adapter_code(repo_root))
    assert not findings, (
        "the τ² adapter looks like it is reimplementing τ²-bench's grader: "
        f"{findings}. db_reward is CALLED, never reimplemented — a grader we wrote is an "
        "answer key we authored, which is the single thing this project exists to avoid."
    )


def test_the_grader_scan_fires_on_a_planted_reimplementation():
    """The seeded-defect principle: *a gate that has never gone red is only decorative.*

    A scan that has never fired is indistinguishable from a scan with a broken regex, so
    here it is pointed at a file that really does rebuild the hash comparison.
    """
    planted = {
        "bad_adapter.py": (
            "import hashlib\n"
            "def db_reward(predicted, target):\n"
            "    return 1.0 if hashlib.sha256(predicted).hexdigest() == target else 0.0\n"
        )
    }
    assert _grader_findings(planted)


def test_the_docstring_stripper_did_not_eat_the_adapter(repo_root):
    """The other half of a usable scan: it must still be looking at real code.

    If the strip swallowed the file, ``_grader_findings`` would return nothing and the test
    above would report green over an empty string — `REVIEW_C0.md`'s *"a check that reports
    PASS over nothing"* class, in a check written to avoid it.
    """
    stripped = _adapter_code(repo_root)
    assert set(stripped) == {"__init__.py", "enumerate.py"}
    assert "def enumerate_domain" in stripped["enumerate.py"]
    assert "def classify_task" in stripped["enumerate.py"]
    assert "Sierra" not in stripped["enumerate.py"], "prose survived the strip"


def test_the_adapter_imports_no_tau2_module_and_therefore_no_model_client(repo_root):
    """The adapter reads τ²'s **files**; it imports none of τ²'s **code**.

    Deliberate, and it is what keeps the unit suite free of a 22-second import that would
    also pull ``litellm`` into every test process. The cost is that the write-tool set is
    parsed rather than imported — cross-checked against τ²'s own ``__tool_type__``
    metadata for this build, and recorded in ``docs/sessions/c3-build-1.txt``.
    """
    for name, code in _adapter_code(repo_root).items():
        assert not re.search(r"(?m)^\s*(?:import|from)\s+tau2\b", code), name
        for client in TEXT_GENERATION_CLIENTS:
            assert not re.search(rf"(?m)^\s*(?:import|from)\s+{client}\b", code), f"{name}: {client}"


# ======================================================================================
# The pure classification, on hand-built tasks.
# ======================================================================================

_WRITE_TOOLS = frozenset({"book_reservation"})


@pytest.mark.parametrize(
    "criteria, expected",
    [
        ({"actions": []}, tau2_enum.TaskClass.EMPTY_ACTIONS),
        ({"actions": None}, tau2_enum.TaskClass.EMPTY_ACTIONS),
        ({}, tau2_enum.TaskClass.EMPTY_ACTIONS),
        ({"actions": [{"name": "get_user_details"}]}, tau2_enum.TaskClass.READ_ONLY),
        ({"actions": [{"name": "book_reservation"}]}, tau2_enum.TaskClass.WRITE),
        (
            {"actions": [{"name": "get_user_details"}, {"name": "book_reservation"}]},
            tau2_enum.TaskClass.WRITE,
        ),
    ],
)
def test_classify_task_on_hand_built_trajectories(criteria, expected):
    """One write tool anywhere in the trajectory makes the whole task a write task."""
    assert tau2_enum.classify_task({"evaluation_criteria": criteria}, _WRITE_TOOLS) == expected


def test_a_task_with_no_evaluation_criteria_at_all_is_empty_not_a_crash():
    assert tau2_enum.classify_task({"id": "x"}, _WRITE_TOOLS) is tau2_enum.TaskClass.EMPTY_ACTIONS


def test_reward_basis_falls_back_to_tau2s_own_default_and_never_reaches_it_here(enumeration):
    """The fallback is τ²'s ``default_factory``, not ours — and no task needs it at the pin."""
    assert tau2_enum.reward_basis({}) == tau2_enum.TAU2_DEFAULT_REWARD_BASIS
    for domain in enumeration.domains:
        for basis, _count in domain.reward_basis_census:
            assert basis != tau2_enum.TAU2_DEFAULT_REWARD_BASIS or basis == ("COMMUNICATE", "DB")


def test_an_action_naming_an_unknown_tool_is_a_refusal():
    """It would default the task into the must-not-write control, which is a reported number."""
    with pytest.raises(tau2_enum.EnumerationError):
        tau2_enum.enumerate_domain(
            "airline",
            [{"id": "1", "evaluation_criteria": {"actions": [{"name": "no_such_tool"}]}}],
            "@is_tool(ToolType.WRITE)\ndef book_reservation(self):\n    pass\n",
        )


def test_a_duplicate_task_id_is_a_refusal():
    """`PROCESS.md` §9's partition invariant cannot hold over a repeated id."""
    with pytest.raises(tau2_enum.EnumerationError):
        tau2_enum.enumerate_domain(
            "airline",
            [{"id": "1", "evaluation_criteria": {}}, {"id": "1", "evaluation_criteria": {}}],
            "@is_tool(ToolType.READ)\ndef get_user_details(self):\n    pass\n",
        )


def test_the_report_runs_and_exits_zero(capsys):
    """`PROCESS.md` §9: the numbers are printed, zeros included, not merely computed."""
    assert tau2_enum.report() == 0
    printed = capsys.readouterr().out
    assert "must-not-write" in printed
    assert "T-FP" in printed
    assert tau2_enum.pinned_sha() in printed
