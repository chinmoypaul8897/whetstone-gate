"""The τ²-bench enumeration: the must-not-write control, the write tasks, and T-FP.

WHAT THIS MODULE IS, AND WHAT IT IS CAREFUL NOT TO BE
=====================================================
It **reads** the vendored τ²-bench checkout at the pinned commit and reports what is in
it. It authors nothing. Every count it prints is a property of *Sierra's* files; the only
thing this project contributes is the arithmetic that partitions them.

`CONTEXT.md` §11.1 states what the counts should be. This module **reproduces** them and
never assumes them. `tests/test_c3_tau2_enumeration.py` parses those figures back out of
`CONTEXT.md` itself and diffs them against what this module derives from the checkout —
so the specification and the third-party tree have to agree **without either being
transcribed into this file**. A disagreement is a finding on one of them, and finding out
which is worth more than finishing the chunk.

WRITE TOOLS ARE READ FROM THE DECORATOR, NEVER HAND-LISTED
===========================================================
A task is **must-not-write** when its ``evaluation_criteria.actions`` reference trajectory
contains **no write tool** (`CONTEXT.md` §11.1). Write tools are identified by τ²-bench's
own ``@is_tool(ToolType.WRITE)`` decorator, parsed out of τ²-bench's own source with
:mod:`ast`.

⚠️ **A hand-list of tool names would be an answer key we authored**, which is the single
thing this project exists not to do. It would also rot silently: the set would keep
looking right long after the benchmark had moved, and nothing here would notice.

*Verified for this build, 2026-08-31, at the pinned SHA:* the decorator set this parser
returns is **identical** to the set τ²-bench's own metaclass builds at import time — the
``__tool_type__`` attribute :func:`tau2.environment.toolkit.is_tool` sets — for all 14
airline and all 16 retail decorated tools, with **zero** ``mutates_state`` overrides in
either domain. The parser is used rather than the import because importing **any**
``tau2.*`` module executes ``vendor/tau2-bench/src/tau2/__init__.py``, which pulls in the
whole framework, ``litellm`` included, at a measured ~22 s. See :mod:`whetstone_gate.tau2`
and the db_reward note below.

THE SORT RULE — RULED, AND WRITTEN DOWN SO IT IS CHECKABLE RATHER THAN IMPLICIT
===============================================================================
`CONTEXT.md` §13.4 pre-registers T-FP as *"the first 40 write-task ids after sorting,
stratified 20 airline / 20 retail."* **"After sorting" does not say which sort**, and the
answer changes which tasks get run. Ruled by the architect on 2026-08-31:

    SORT THE WRITE-TASK IDS AS STRINGS, BYTEWISE ASCENDING — Python's default ``sorted()``
    over ``str`` — WITHIN EACH DOMAIN SEPARATELY, and take the FIRST 20 of each.
    Not numerically. Not by file order. Not by any τ²-internal ordering.

⚠️ **This is load-bearing, not a formality.** τ²'s task ids are *decimal strings*, so the
two orders genuinely disagree: bytewise, airline's first twenty run ``11 … 37`` and leave
``7`` and ``8`` out entirely, while a numeric sort would start at ``7``. Retail is worse —
bytewise puts ``100 … 109`` ahead of ``11``. Left to *"whatever sort the language
defaults to"*, the pre-registered sample would have been decided by an implementation
detail, after the fact, which is the opposite of pre-registration.

WHY telecom IS EXCLUDED — THE REASON, NOT THE CONCLUSION
========================================================
`CONTEXT.md` §11.1 **withdrew** an earlier unsourced claim that telecom is *"unsound"* and
replaced it with a structural one this module verifies at the pin: telecom's
``reward_basis`` carries **no DB component at all**, on any of its tasks. There is
therefore no DB-hash write signal to score, and telecom **cannot host the must-not-write
control** — not because it is bad, but because the measurement does not exist there.
:func:`telecom_reward_basis_census` re-derives that, so the reason is checked rather than
repeated.

WE SCORE ON ``db_reward`` ALONE, AND THE IMPRECISE VERSION OF THAT SENTENCE IS FALSE
====================================================================================
`CONTEXT.md` §11.1, verbatim, and this project uses it everywhere:

    "We score on ``db_reward`` alone — a hash comparison, no model. τ²-bench's full retail
    reward multiplies in an LLM-judged natural-language assertion, and we do not use it."

*"No LLM anywhere in the grader"* is **false** and was withdrawn:
``src/tau2/evaluator/evaluator_nl_assertions.py:121`` calls ``generate(...)`` with
``model=DEFAULT_LLM_NL_ASSERTIONS`` (``src/tau2/config.py:24``), and ``NL_ASSERTION``
gates the reward on 112 of 114 retail tasks. Both line numbers are re-verified at the
pinned SHA by ``tests/test_c3_tau2_enumeration.py``, which also walks ``db_reward``'s own
transitive imports and asserts that **path** reaches no model client. A walk over τ²-bench
as a whole would fail correctly and prove nothing about what we call.

⚠️ ``db_reward`` IS CALLED, NEVER REIMPLEMENTED. A reimplemented grader is an answer key we
authored. Nothing in this package computes a DB hash or compares one, and a test asserts it.
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from whetstone_gate import config as cfg
from whetstone_gate._console import say

# --------------------------------------------------------------------------------------
# Where the third party lives. `vendor/` is READ-ONLY to every session: the
# external-answer-key claim rests entirely on this checkout being unmodified.
# --------------------------------------------------------------------------------------

#: The vendored checkout's directory name under ``vendor/``.
VENDOR_DIRNAME = "tau2-bench"

#: The two domains this project uses. `CONTEXT.md` §11.1: airline and retail only.
DOMAINS: tuple[str, ...] = ("airline", "retail")

#: Excluded, for the structural reason :func:`telecom_reward_basis_census` re-derives.
EXCLUDED_DOMAIN = "telecom"

#: τ²-bench's own ``ToolType`` member name for a write tool.
WRITE_TOOL_TYPE = "WRITE"

#: τ²-bench's own tool decorators. Both set ``__tool_type__``; the second additionally
#: marks a tool the agent must discover before calling. Neither airline nor retail uses
#: the second at this SHA, and it is accepted here anyway so that a benchmark bump cannot
#: silently drop a write tool out of the classification.
TOOL_DECORATORS: tuple[str, ...] = ("is_tool", "is_discoverable_tool")

#: τ²-bench's own default when a task states no ``reward_basis``
#: (``EvaluationCriteria.reward_basis``'s ``default_factory``). Not our choice, and not
#: reached at this SHA: every airline and retail task states one explicitly.
TAU2_DEFAULT_REWARD_BASIS: tuple[str, ...] = ("DB", "COMMUNICATE")


class VendorError(RuntimeError):
    """The vendored checkout is missing, unreadable, or not at the pinned commit."""


class EnumerationError(RuntimeError):
    """The checkout parsed, but says something this enumeration cannot honestly reduce."""


class TaskClass(str, Enum):
    """How one τ² task's reference trajectory classifies.

    ``EMPTY_ACTIONS`` and ``READ_ONLY`` together are the **must-not-write** set. They are
    kept apart because `CONTEXT.md` §11.1 states them apart (7 + 17 airline, 2 + 8 retail)
    and because they are different things: one task has no reference trajectory at all,
    the other has one that only reads.
    """

    EMPTY_ACTIONS = "empty_actions"
    READ_ONLY = "read_only"
    WRITE = "write"


MUST_NOT_WRITE_CLASSES: tuple[TaskClass, ...] = (
    TaskClass.EMPTY_ACTIONS,
    TaskClass.READ_ONLY,
)


# ======================================================================================
# THE SHELL — everything that touches the filesystem lives here and nowhere else.
# Hard rule 8: core logic takes data in and returns results; side effects live in a thin
# outer shell. Every function below this line is pure and takes its bytes as arguments.
# ======================================================================================


def vendor_root() -> Path:
    """Return ``vendor/tau2-bench``, or refuse."""
    root = cfg.repo_root() / "vendor" / VENDOR_DIRNAME
    if not root.is_dir():
        raise VendorError(
            f"{root} does not exist. The vendored checkout is not committed "
            f"(QUESTIONS.md Q-010); vendor/MANIFEST.md carries the exact clone commands. "
            f"This chunk cannot be built or reviewed without it."
        )
    return root


def vendored_head_sha() -> str:
    """Return the commit the vendored checkout is on, read from its own ``.git``.

    Deliberately **not** a ``git`` subprocess: this module stays importable and
    deterministic with no process spawn, and a detached checkout writes the commit id
    into ``.git/HEAD`` directly. A symbolic HEAD is resolved through its ref file. Any
    other shape is a refusal rather than a guess.
    """
    head_file = vendor_root() / ".git" / "HEAD"
    if not head_file.is_file():
        raise VendorError(f"{head_file} does not exist, so the checkout cannot be pinned.")
    head = head_file.read_text(encoding="utf-8").strip()
    if head.startswith("ref: "):
        ref = vendor_root() / ".git" / head[len("ref: ") :].strip()
        if not ref.is_file():
            raise VendorError(f"{head_file} points at {ref}, which does not exist.")
        head = ref.read_text(encoding="utf-8").strip()
    if len(head) != len(head.strip()) or not _is_hex_commit(head):
        raise VendorError(f"{head_file} does not hold a commit id (got {head!r}).")
    return head


def _is_hex_commit(text: str) -> bool:
    """True for a full-length lowercase hex object id."""
    return len(text) == 40 and all(char in "0123456789abcdef" for char in text)


def pinned_sha() -> str:
    """The τ²-bench commit `PROTOCOL.md` pre-registers, read from ``config/``.

    Hard rule 9: it is a spec value, so it is read, never written into source.
    """
    return cfg.load("protocol").require("vendor.tau2_bench_sha")


def assert_vendor_at_pin() -> str:
    """Refuse unless the checkout is at the pinned commit. Returns that commit.

    ⚠️ **Every number this module reports is meaningless if this fails**, so it fails loudly
    rather than reporting numbers from a tree nobody pinned.
    """
    head, pin = vendored_head_sha(), pinned_sha()
    if head != pin:
        raise VendorError(
            f"vendor/{VENDOR_DIRNAME} is at {head}, but config/protocol.yaml pins "
            f"{pin}. Every count derived from this tree would be from a different "
            f"benchmark than the one PROTOCOL.md pre-registers. This is a refusal, not a "
            f"warning: re-checkout the pin, or raise it in QUESTIONS.md if the pin is wrong."
        )
    return head


def domain_data_dir(domain: str) -> Path:
    """τ²-bench's own data directory for ``domain``."""
    return vendor_root() / "data" / "tau2" / "domains" / domain


def read_tools_source(domain: str) -> str:
    """Return the text of τ²-bench's own toolkit module for ``domain``."""
    path = vendor_root() / "src" / "tau2" / "domains" / domain / "tools.py"
    if not path.is_file():
        raise VendorError(f"{path} does not exist; the checkout is not what it claims.")
    return path.read_text(encoding="utf-8")


def read_tasks(domain: str) -> tuple[dict, ...]:
    """Return every task τ²-bench ships for ``domain``, in file order.

    Reads ``tasks.json`` whole. That file **is** τ²'s ``base`` task split for airline and
    retail — verified at the pin: ``split_tasks.json`` lists all 50 airline and all 114
    retail ids under ``base`` — so no split filter is applied and none is needed.
    """
    path = domain_data_dir(domain) / "tasks.json"
    if not path.is_file():
        raise VendorError(f"{path} does not exist; the checkout is not what it claims.")
    tasks = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(tasks, list):
        raise EnumerationError(f"{path} did not parse to a list of tasks.")
    return tuple(tasks)


# ======================================================================================
# PURE — from here down, every function takes its data as an argument.
# ======================================================================================


def tool_types(tools_source: str) -> dict[str, str]:
    """Map every decorated tool in ``tools_source`` to its ``ToolType`` member name.

    Reads τ²-bench's **own decorator**. ``@is_tool()`` with no argument carries
    ``ToolType.READ`` — that is the decorator's own signature default — and a decorator
    whose argument is not a plain ``ToolType.MEMBER`` attribute is a refusal, not a
    silently-dropped tool: a write tool this parser could not read would move a task from
    the write set into the must-not-write control, which is a reported number.
    """
    tree = ast.parse(tools_source)
    found: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            if getattr(decorator.func, "id", None) not in TOOL_DECORATORS:
                continue
            if not decorator.args:
                found[node.name] = "READ"
                continue
            first = decorator.args[0]
            if isinstance(first, ast.Attribute) and getattr(first.value, "id", None) == "ToolType":
                found[node.name] = first.attr
            else:
                raise EnumerationError(
                    f"tool {node.name!r} carries a decorator this parser cannot read "
                    f"({ast.dump(first)}). Refusing rather than guessing its type: a "
                    f"misread write tool silently moves a task into the must-not-write "
                    f"control, and that control is a published number."
                )
    if not found:
        raise EnumerationError(
            "no decorated tools were found at all. A parser that silently reads nothing "
            "is the same class of defect as the check it replaces."
        )
    return found


def write_tool_names(tools_source: str) -> frozenset[str]:
    """The names of every ``@is_tool(ToolType.WRITE)`` tool in ``tools_source``."""
    return frozenset(
        name for name, kind in tool_types(tools_source).items() if kind == WRITE_TOOL_TYPE
    )


def evaluation_criteria(task: Mapping) -> Mapping:
    """``task['evaluation_criteria']``, or an empty mapping when it carries none."""
    criteria = task.get("evaluation_criteria")
    return criteria if isinstance(criteria, Mapping) else {}


def action_names(task: Mapping) -> tuple[str, ...]:
    """The tool names in this task's reference trajectory, in order.

    An absent ``evaluation_criteria``, an absent ``actions`` key, a ``null`` and an empty
    list all reduce to the empty tuple — they are the same fact for this classification,
    and :func:`enumerate_domain` counts each shape separately so none of them hides.
    """
    actions = evaluation_criteria(task).get("actions") or []
    return tuple(action["name"] for action in actions)


def reward_basis(task: Mapping) -> tuple[str, ...]:
    """This task's ``reward_basis``, falling back to τ²'s **own** documented default.

    The fallback is τ²-bench's, not ours (``EvaluationCriteria.reward_basis``'s
    ``default_factory``), and it is not reached at the pinned SHA: every airline and
    retail task states its basis explicitly. Sorted so the census keys are stable.
    """
    basis = evaluation_criteria(task).get("reward_basis")
    if not basis:
        return TAU2_DEFAULT_REWARD_BASIS
    return tuple(sorted(str(component) for component in basis))


def classify_task(task: Mapping, write_tools: frozenset[str]) -> TaskClass:
    """Classify one task against a domain's write-tool set.

    `CONTEXT.md` §11.1: a task is must-not-write when its reference trajectory contains no
    write tool. The empty trajectory is a distinct case and is kept distinct.
    """
    names = action_names(task)
    if not names:
        return TaskClass.EMPTY_ACTIONS
    if any(name in write_tools for name in names):
        return TaskClass.WRITE
    return TaskClass.READ_ONLY


def sort_task_ids(ids: Iterable[str]) -> tuple[str, ...]:
    """THE RULED SORT: task ids as strings, bytewise ascending.

    Python's default ``sorted()`` over ``str`` orders by Unicode code point, which for the
    ASCII decimal ids τ² ships **is** bytewise order. That equivalence is asserted rather
    than assumed — :func:`assert_ids_are_ascii` is called on every list this module sorts,
    so a non-ASCII id in some future task set is a refusal instead of a quiet re-ordering
    of a pre-registered sample.
    """
    ordered = tuple(sorted(ids))
    assert_ids_are_ascii(ordered)
    return ordered


def assert_ids_are_ascii(ids: Sequence[str]) -> None:
    """Refuse on any id whose code-point order is not its byte order."""
    offenders = [task_id for task_id in ids if not task_id.isascii()]
    if offenders:
        raise EnumerationError(
            f"the ruled sort is BYTEWISE ascending, and these ids are not ASCII, so "
            f"code-point order is not byte order for them: {offenders}. Refusing rather "
            f"than silently choosing one of the two orderings for a pre-registered sample."
        )


# --------------------------------------------------------------------------------------
# Aggregates.
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class DomainEnumeration:
    """One domain's partition of τ²'s tasks. Every id appears in exactly one bucket."""

    domain: str
    empty_action_ids: tuple[str, ...]
    read_only_ids: tuple[str, ...]
    write_ids: tuple[str, ...]
    reward_basis_census: tuple[tuple[tuple[str, ...], int], ...]
    write_tools: tuple[str, ...]
    tool_type_census: tuple[tuple[str, int], ...]

    @property
    def must_not_write_ids(self) -> tuple[str, ...]:
        """The must-not-write control for this domain, in the ruled order."""
        return sort_task_ids(self.empty_action_ids + self.read_only_ids)

    @property
    def total(self) -> int:
        return len(self.empty_action_ids) + len(self.read_only_ids) + len(self.write_ids)

    @property
    def must_not_write_count(self) -> int:
        return len(self.empty_action_ids) + len(self.read_only_ids)

    @property
    def write_count(self) -> int:
        return len(self.write_ids)


@dataclass(frozen=True)
class Enumeration:
    """Every domain's partition, plus the commit it was all read from."""

    vendor_sha: str
    domains: tuple[DomainEnumeration, ...]

    def by_domain(self, domain: str) -> DomainEnumeration:
        for enumerated in self.domains:
            if enumerated.domain == domain:
                return enumerated
        raise KeyError(domain)

    @property
    def total(self) -> int:
        return sum(domain.total for domain in self.domains)

    @property
    def must_not_write_count(self) -> int:
        return sum(domain.must_not_write_count for domain in self.domains)

    @property
    def write_count(self) -> int:
        return sum(domain.write_count for domain in self.domains)

    @property
    def must_not_write_ids_by_domain(self) -> dict[str, tuple[str, ...]]:
        return {domain.domain: domain.must_not_write_ids for domain in self.domains}


def enumerate_domain(
    domain: str, tasks: Sequence[Mapping], tools_source: str
) -> DomainEnumeration:
    """Partition one domain's tasks. Pure: the caller supplies the bytes.

    ⚠️ **An action naming a tool this domain's toolkit does not define is a refusal.** Such
    a name is unclassifiable, and the failure is not symmetric: an unrecognised write tool
    would move its task *into* the must-not-write control, inflating the one number
    `CONTEXT.md` §11.1 calls the externally-authored attacker-competence check. Zero occur
    at the pinned SHA, and this is what keeps that a checked fact rather than a habit.
    """
    known = set(tool_types(tools_source))
    write_tools = write_tool_names(tools_source)

    unknown = sorted(
        {name for task in tasks for name in action_names(task) if name not in known}
    )
    if unknown:
        raise EnumerationError(
            f"{domain}: reference trajectories name tools this domain's toolkit does not "
            f"define: {unknown}. Refusing: an unclassifiable action would default the "
            f"task into the must-not-write control, which is a published number."
        )

    ids_seen: set[str] = set()
    buckets: dict[TaskClass, list[str]] = {member: [] for member in TaskClass}
    census: dict[tuple[str, ...], int] = {}
    for task in tasks:
        task_id = task["id"]
        if not isinstance(task_id, str):
            raise EnumerationError(
                f"{domain}: task id {task_id!r} is {type(task_id).__name__}, not str. The "
                f"ruled sort is a STRING sort; a numeric id would silently re-order a "
                f"pre-registered sample."
            )
        if task_id in ids_seen:
            raise EnumerationError(
                f"{domain}: task id {task_id!r} occurs more than once, so the partition "
                f"cannot sum to the total (PROCESS.md §9)."
            )
        ids_seen.add(task_id)
        buckets[classify_task(task, write_tools)].append(task_id)
        basis = reward_basis(task)
        census[basis] = census.get(basis, 0) + 1

    return DomainEnumeration(
        domain=domain,
        empty_action_ids=sort_task_ids(buckets[TaskClass.EMPTY_ACTIONS]),
        read_only_ids=sort_task_ids(buckets[TaskClass.READ_ONLY]),
        write_ids=sort_task_ids(buckets[TaskClass.WRITE]),
        reward_basis_census=tuple(sorted(census.items())),
        write_tools=tuple(sorted(write_tools)),
        tool_type_census=tuple(sorted(_count_values(tool_types(tools_source)))),
    )


def _count_values(mapping: Mapping[str, str]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for value in mapping.values():
        counts[value] = counts.get(value, 0) + 1
    return list(counts.items())


def enumerate_tau2() -> Enumeration:
    """Read the pinned checkout and partition airline and retail. The shell's entry point."""
    sha = assert_vendor_at_pin()
    return Enumeration(
        vendor_sha=sha,
        domains=tuple(
            enumerate_domain(domain, read_tasks(domain), read_tools_source(domain))
            for domain in DOMAINS
        ),
    )


def telecom_reward_basis_census() -> tuple[tuple[tuple[str, ...], int], ...]:
    """Why telecom is excluded, re-derived rather than restated.

    `CONTEXT.md` §11.1 replaced an unsourced *"unsound"* claim with a structural one: no
    telecom task's ``reward_basis`` carries ``DB``, so there is no DB-hash write signal to
    score and telecom cannot host the must-not-write control at all.
    """
    assert_vendor_at_pin()
    tasks = read_tasks(EXCLUDED_DOMAIN)
    census: dict[tuple[str, ...], int] = {}
    for task in tasks:
        basis = reward_basis(task)
        census[basis] = census.get(basis, 0) + 1
    return tuple(sorted(census.items()))


def telecom_reward_basis_includes_db() -> bool:
    """True if ``DB`` appears in **any** telecom ``reward_basis``. It does not, at the pin.

    ⚠️ Named around ``reward_basis`` rather than around the grader's own symbol on purpose.
    ``tests/test_c3_tau2_enumeration.py`` scans this package for any sign of a
    reimplemented grader, and an identifier that merely *ends* with that symbol would pass
    that scan only by an accident of word-boundary matching. A near-miss that survives by
    luck is not a thing to leave in a file whose whole subject is not writing a grader.
    """
    return any("DB" in basis for basis, _ in telecom_reward_basis_census())


# --------------------------------------------------------------------------------------
# T-FP — the pre-registered write-task sample.
# --------------------------------------------------------------------------------------


def tfp_quota() -> dict[str, int]:
    """The per-domain T-FP quota, read from ``config/`` (hard rule 9).

    ``selections.tfp_stratification`` is the pre-registered stratification and
    ``selections.tfp_task_count`` its total. Both are checked against each other here
    rather than trusted, because a stratification that does not sum to its own total is a
    silently wrong sample, not a typo.
    """
    protocol = cfg.load("protocol")
    quota = {domain: int(protocol.require(f"selections.tfp_stratification.{domain}")) for domain in DOMAINS}
    declared = int(protocol.require("selections.tfp_task_count"))
    if sum(quota.values()) != declared:
        raise EnumerationError(
            f"config/protocol.yaml: selections.tfp_stratification sums to "
            f"{sum(quota.values())} but selections.tfp_task_count is {declared}. "
            f"PROCESS.md §9: every partition sums to its total."
        )
    return quota


def tfp_selection(enumeration: Enumeration, quota: Mapping[str, int]) -> dict[str, tuple[str, ...]]:
    """The pre-registered T-FP ids: the first ``quota[domain]`` write ids, per domain.

    The ordering is :func:`sort_task_ids` — the ruled bytewise string sort — and a domain
    with fewer write tasks than its quota is a refusal. Hard rule 11 forbids a quietly
    shrunken denominator, and a sample that silently returns short is the same defect one
    step earlier.
    """
    selected: dict[str, tuple[str, ...]] = {}
    for domain, wanted in quota.items():
        available = enumeration.by_domain(domain).write_ids
        if len(available) < wanted:
            raise EnumerationError(
                f"T-FP asks for {wanted} {domain} write tasks and the pinned checkout has "
                f"{len(available)}. Refusing to return a short sample: the shortfall would "
                f"reappear later as a denominator nobody declared."
            )
        selected[domain] = sort_task_ids(available)[:wanted]
    return selected


# --------------------------------------------------------------------------------------
# What is committed to config/, and the check that it still matches the checkout.
# --------------------------------------------------------------------------------------


def committed_must_not_write_ids() -> dict[str, tuple[str, ...]]:
    """The 34 must-not-write ids as ``config/protocol.yaml`` pre-registers them."""
    return _committed_ids("selections.tau2_must_not_write_task_ids")


def committed_tfp_ids() -> dict[str, tuple[str, ...]]:
    """The 40 T-FP ids as ``config/protocol.yaml`` pre-registers them."""
    return _committed_ids("selections.tfp_task_ids")


def _committed_ids(dotted: str) -> dict[str, tuple[str, ...]]:
    protocol = cfg.load("protocol")
    committed: dict[str, tuple[str, ...]] = {}
    for domain in DOMAINS:
        ids = protocol.require(f"{dotted}.{domain}")
        if not isinstance(ids, list) or not ids:
            raise EnumerationError(f"config/protocol.yaml: {dotted}.{domain} is not a list of ids.")
        for task_id in ids:
            if not isinstance(task_id, str):
                raise EnumerationError(
                    f"config/protocol.yaml: {dotted}.{domain} holds {task_id!r}, which YAML "
                    f"parsed as {type(task_id).__name__}. τ² task ids are STRINGS and an "
                    f"unquoted decimal id becomes an int that matches nothing."
                )
        committed[domain] = tuple(ids)
    return committed


# --------------------------------------------------------------------------------------
# The report. PROCESS.md §9: zero-occurrence branches print as zeros, never omitted, and
# every partition is shown summing to its total.
# --------------------------------------------------------------------------------------


def report() -> int:
    """Print the whole enumeration. Returns a process exit code."""
    try:
        enumeration = enumerate_tau2()
    except (VendorError, EnumerationError) as error:
        say(f"[FAIL] {error}")
        return 1

    say("-- tau2-bench enumeration ------------------------------------------------------")
    say(f"  vendored commit : {enumeration.vendor_sha}")
    say(f"  pinned by config: {pinned_sha()}   (equal, or this would not have printed)")
    say("")

    for domain in enumeration.domains:
        say(f"  {domain.domain}")
        say(f"    tasks                     : {domain.total}")
        say(f"    write tools (@is_tool WRITE): {len(domain.write_tools)}  {list(domain.write_tools)}")
        say(f"    tool types                : {dict(domain.tool_type_census)}")
        say(f"    must-not-write            : {domain.must_not_write_count}")
        say(f"      empty action list       : {len(domain.empty_action_ids)}")
        say(f"      read-only trajectory    : {len(domain.read_only_ids)}")
        say(f"    write                     : {domain.write_count}")
        say(
            f"    partition                 : {len(domain.empty_action_ids)} + "
            f"{len(domain.read_only_ids)} + {domain.write_count} = {domain.total}"
        )
        say(f"    reward_basis census       : {{" + ", ".join(f"{list(b)}: {n}" for b, n in domain.reward_basis_census) + "}")
        say("")

    say(
        f"  TOTAL: must-not-write {enumeration.must_not_write_count} + write "
        f"{enumeration.write_count} = {enumeration.total}"
    )
    say("")

    say(f"  {EXCLUDED_DOMAIN} (EXCLUDED - the reason, re-derived, not the conclusion)")
    census = telecom_reward_basis_census()
    for basis, count in census:
        say(f"    reward_basis {list(basis)}: {count}")
    say(f"    tasks                     : {sum(count for _, count in census)}")
    say(f"    any basis carrying DB     : {telecom_reward_basis_includes_db()}")
    say(
        "    -> no DB-hash write signal to score, so telecom cannot host the "
        "must-not-write control."
    )
    say("")

    quota = tfp_quota()
    selection = tfp_selection(enumeration, quota)
    say("  T-FP - the pre-registered write-task sample")
    say("    sort rule: task ids AS STRINGS, BYTEWISE ASCENDING, within each domain")
    for domain, ids in selection.items():
        say(f"    {domain}: {len(ids)} of {enumeration.by_domain(domain).write_count}  first={ids[0]!r} last={ids[-1]!r}")
        say(f"      {list(ids)}")
    say(f"    total selected: {sum(len(ids) for ids in selection.values())}")
    say("")

    say("  config/ agreement (the ids committed as a pre-registration artefact)")
    for label, committed, derived in (
        ("must-not-write", committed_must_not_write_ids(), enumeration.must_not_write_ids_by_domain),
        ("T-FP", committed_tfp_ids(), selection),
    ):
        for domain in DOMAINS:
            status = "MATCH" if committed[domain] == derived[domain] else "DIFFERS"
            say(f"    {label:<15} {domain:<8}: {status}  ({len(committed[domain])} committed)")
    return 0


if __name__ == "__main__":  # pragma: no cover - operator entry point
    raise SystemExit(report())
