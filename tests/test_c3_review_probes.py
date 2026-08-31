"""C3 REVIEW 1 (`a66c389d`) — kept probes.

Four checks the review ran by hand and is leaving behind, because a fact established once
in a review document rots, and a fact established on every run does not. None of them
changes C3's behaviour; each pins something C3's own suite leaves unpinned.

`docs/reviews/REVIEW_C3_1.md` is the finding list. These probes close the two findings a
reviewer *can* close without touching C3's code (F-3, F-5) and turn two hand-run
verifications (§2c of the review) into standing assertions.
"""

from __future__ import annotations

import ast

from whetstone_gate.tau2 import enumerate as tau2_enum
from tests.test_c3_tau2_enumeration import (
    DB_REWARD_MODULE,
    _closure,
    _imports,
    _module_file,
    _vendor_src,
)


# ======================================================================================
# F-3 — the decorator parser's keyword blind spot, guarded at the pin.
# ======================================================================================


def test_no_pinned_domain_toolkit_uses_the_keyword_form_of_the_tool_decorator():
    """⚠️ **The parser's one blind spot, closed from the other side.**

    :func:`whetstone_gate.tau2.enumerate.tool_types` reads a tool's type from
    ``decorator.args[0]`` and treats a decorator with **no positional argument** as
    ``ToolType.READ``. So ``@is_tool(tool_type=ToolType.WRITE)`` — legal Python, and the
    same call — would be read as READ, and its tasks would land in the **must-not-write
    control**, which is a published number. The parser cannot be fixed by this session
    (a reviewer fixes nothing), so the risk is closed the only other way: by asserting
    that the shape which would trigger it **does not occur at the pinned SHA**.

    If a future benchmark bump introduces the keyword form, or an attribute-qualified
    decorator (``@toolkit.is_tool(...)``, which :func:`tool_types`'s
    ``getattr(decorator.func, "id", None)`` also skips), this goes red and forces the
    parser to be widened before the count moves.
    """
    offenders: list[str] = []
    for domain in tau2_enum.DOMAINS:
        tree = ast.parse(tau2_enum.read_tools_source(domain))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                name = getattr(decorator.func, "attr", None) or getattr(
                    decorator.func, "id", None
                )
                if name not in tau2_enum.TOOL_DECORATORS:
                    continue
                if getattr(decorator.func, "id", None) is None:
                    offenders.append(f"{domain}.{node.name}: attribute-qualified decorator")
                if any(keyword.arg == "tool_type" for keyword in decorator.keywords):
                    offenders.append(f"{domain}.{node.name}: tool_type= keyword form")

    assert not offenders, (
        "τ²-bench now spells a tool decorator in a form "
        "whetstone_gate.tau2.enumerate.tool_types() does not read, and it does NOT refuse "
        f"on this shape — it silently records READ: {offenders}. A write tool read as READ "
        "moves its tasks INTO the 34-task must-not-write control. Widen the parser "
        "(accept the `tool_type=` keyword and an attribute-qualified callee) before "
        "trusting any count derived from this checkout."
    )


# ======================================================================================
# §2c — the db_reward import walk, its two silent-failure modes pinned.
# ======================================================================================


def test_the_db_reward_import_walk_drops_no_real_tau2_module(repo_root):
    """⚠️ **The walk's one way of lying, checked rather than assumed.**

    ``_closure`` does ``if path is None: … continue`` — and for a name starting with
    ``tau2`` that resolves to no file, it is dropped **without even being recorded as
    third-party**. That is correct for ``from tau2.x import SomeClass`` (a symbol, not a
    module) and it is the overwhelming majority of them. It would be a *silent
    under-approximation* if any dropped name were a real module, because the walk would
    then be reporting "no model client" over a graph it had not finished walking.

    So: every unresolved ``tau2.*`` name on the db_reward path must be an attribute of a
    module that *did* resolve. Measured at the pin: 126 unresolved names, 126 of them
    symbols, **zero** real modules dropped.
    """
    src = _vendor_src(repo_root)
    modules, _ = _closure(src, DB_REWARD_MODULE)

    unresolved: set[str] = set()
    for module in modules:
        for imported in _imports(_module_file(src, module), module):
            if imported.startswith("tau2") and _module_file(src, imported) is None:
                unresolved.add(imported)

    assert unresolved, "no unresolved names at all — the walk shape has changed; re-check it"
    dropped_modules = sorted(name for name in unresolved if _module_file(src, name))
    assert not dropped_modules, (
        f"the db_reward import walk silently dropped real τ² modules: {dropped_modules}. "
        "Every count of 'no model client on the path' would then be over a partial graph."
    )
    orphans = sorted(
        name for name in unresolved if _module_file(src, name.rpartition(".")[0]) is None
    )
    assert not orphans, (
        f"these unresolved τ² names are neither a module nor an attribute of one: "
        f"{orphans}. The walk cannot say what it did with them."
    )


def test_the_import_walk_sees_a_function_level_import(repo_root):
    """A deferred ``import litellm`` inside a function must not evade the walk.

    ``_imports`` uses ``ast.walk``, which descends into function bodies, so it does not —
    but that is a property of one call and it is worth one assertion. Without it, moving
    a client import inside a function would be an undetectable way to make the db_reward
    claim false while the test stayed green.
    """
    deferred = ast.parse("def f():\n    import litellm\n")
    module_level = {
        alias.name
        for node in deferred.body
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert module_level == set(), "the fixture is not actually a deferred import"

    walked = {
        alias.name
        for node in ast.walk(deferred)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert "litellm" in walked, (
        "ast.walk no longer descends into function bodies, so _imports() would miss a "
        "deferred model-client import and the db_reward claim would rest on nothing."
    )


# ======================================================================================
# F-5 — what the reference actions actually carry, so the record can stop guessing.
# ======================================================================================


def test_no_reference_action_carries_a_requestor_field_at_all():
    """⚠️ **The datum behind C3's *"0 user requestors"*, stated as it really is.**

    ``docs/sessions/c3-build-1.txt`` records *"zero name a `user` requestor (142 airline
    and 550 assistant actions, 0 user)"*. The conclusion is right and the two counts are
    right, but **no airline or retail reference action carries a ``requestor`` key at
    all** — the union of their keys is ``{action_id, arguments, compare_args, info,
    name}``. They are *"assistant"* only through ``Action.requestor``'s pydantic
    ``default="assistant"``, and this project never loads that model; it reads the raw
    JSON. So *"0 user"* is true because the field is absent, not because it was surveyed.

    Pinning the real shape makes the claim checkable and makes it go red if a benchmark
    bump ever ships a user-requested action — which, in a dual-control benchmark, is a
    thing that can happen, and would put a *user-side write* inside the 34.
    """
    keys: set[str] = set()
    counts: dict[str, int] = {}
    for domain in tau2_enum.DOMAINS:
        actions = [
            action
            for task in tau2_enum.read_tasks(domain)
            for action in (tau2_enum.evaluation_criteria(task).get("actions") or [])
        ]
        counts[domain] = len(actions)
        for action in actions:
            keys |= set(action)

    assert counts == {"airline": 142, "retail": 550}, counts
    assert "requestor" not in keys, (
        f"a reference action now carries a `requestor` field ({sorted(keys)}). Re-derive "
        "the must-not-write control: a user-requested write would be a write inside the "
        "34, and whetstone_gate.tau2.enumerate.action_names() does not look at requestor."
    )
    assert keys == {"action_id", "arguments", "compare_args", "info", "name"}, sorted(keys)
