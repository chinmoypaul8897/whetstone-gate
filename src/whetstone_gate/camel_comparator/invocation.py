"""The RUN-1 invocation — built here, executed in the operator's terminal, decided by neither.

⚠️ **THIS MODULE STOPS AT THE POINT OF INVOCATION AND THAT IS THE WHOLE DESIGN.**
`PROCESS.md` §1: *long runs execute in the operator's terminal, never inside a session that
might close.* RUN-1 is an **operator run**, timeboxed, on 31 August. So this module produces
an argv, a working directory and the **name** of an environment variable, and returns. It
runs no subprocess, opens no socket, and imports no model client.

⚠️ **AND IT DOES NOT DECIDE THE BRANCH.** ``config/lanes.yaml``'s
``camel_comparator.branch`` is ``TODO_C13_RUN1``; ``make selftest`` is **RED on it and must
stay red** until RUN-1 writes it. :func:`branch_is_undecided` *reports* that state — it is
the only branch-shaped function here, it returns a string or ``None``, and it writes
nothing.

═══════════════════════════════════════════════════════════════════════════════════════
⚠️ Q-057, CLASS A — `+camel+secpol` IS A TWO-PASS PROTOCOL, NOT ONE INVOCATION
═══════════════════════════════════════════════════════════════════════════════════════
`CONTEXT.md` §8.5.1 Branch A reads *"Invoke as
`google:gemini-2.0-flash-lite-001+camel+secpol`"*. **That string cannot be passed as
``--model``.** Re-derived first-hand at the pin, 2026-09-01:

  * ``models.py:53`` builds ``CAMEL_MODEL_NAMES`` as ``{model}{suffix}`` over
    ``suffixes = ["", "+camel", "+camel+secpol", "+camel+secpol+strict"]`` and
    ``models.py:67`` merges them into **AgentDojo's** ``MODEL_NAMES``. Those suffixed
    strings are **pipeline names**, so AgentDojo's *"what model are you?"* injection tasks
    can resolve the pipeline — they are not ``--model`` inputs.
  * The pipeline name ``...+camel+secpol`` is **emitted by CaMeL** at ``models.py:188``,
    and it is produced only when ``replay_with_policies`` is true.
  * ``main.py``'s own docstring for that flag: *"replay the run with the given model
    enforcing security policies. **Note that the equivalent run (with same model and attack
    config) should have already been run.**"*
  * ``replay_task`` builds ``Path("logs") / pipeline_name / suite_name / user_task_id /
    (attack_name or "none") / f"{injection_task_id or 'none'}.json"`` and **reads it with
    ``read_text()``** — i.e. **the stored logs of the earlier ``+camel`` pass.** The span,
    the read and the call site are **derived by** :func:`live_log_path`, never written
    down here; see the correction below.

So Branch A is **two passes**: pass 1 produces ``+camel`` and is the pass that spends
tokens; pass 2 adds ``--replay-with-policies``, replays pass 1's logs through
``BankingSecurityPolicyEngine``, and produces ``+camel+secpol``.

═══════════════════════════════════════════════════════════════════════════════════════
⚠️ INC-39 — THE CITATION THAT WAS HERE NAMED A LINE IN A FUNCTION WITH NO CALLER
═══════════════════════════════════════════════════════════════════════════════════════
Builds 1 and 2 cited ``replay_privileged_llm.py:321`` and said that a pass 2 started from
the wrong directory *"reads an empty tree and reports nothing rather than failing — a
silent zero"*. **Both halves were wrong**, and C13 REVIEW 1 found it by tracing the call
graph instead of the line:

  * ``:321`` is inside ``replay_user_task``, called only by ``replay_suite`` (``:344``),
    called only by ``replay_benchmark`` (``:356``) — and **``replay_benchmark`` has no
    caller anywhere in the tree.** ``models.py:16`` imports only ``PrivilegedLLMReplayer``
    and ``UserInjectionTasksGetter``. It is stale scaffolding.
  * ⚠️ **The live path therefore FAILS LOUDLY, not silently.** ``replay_user_task`` uses
    ``path.glob("*")``, which over a missing directory yields nothing — a silent zero.
    ``replay_task`` uses ``trace_path.read_text()``, which over a missing file raises
    **``FileNotFoundError``**, and nothing catches it: ``PrivilegedLLMReplayer.query`` has
    no ``try``/``except``, and AgentDojo's ``run_task_with_pipeline`` catches only
    ``AbortAgentError``. **RUN-1 needs to know which it is: a loud crash inside a
    90-minute box is diagnosable and a silent zero is not.**

⚠️ **This is `Q-058`'s own generalisation one level in, inside the artefact built to
enforce it** — *"a URL to a paper is not a URL to a table"*. Build 1 opened the page. It
did not open the **call graph**. So the remedy is the same shape as everywhere else here:
the line is **derived**, and its enclosing function is **proved reachable**, by
:func:`live_log_path_from_source`.

⚠️ **AND THE FAILURE MODE IS WORSE THAN A CRASH, WHICH IS WHY THE RULING NARROWED BRANCH
B.** ``models.py:100`` is ``if "google" in model`` — **substring containment**, not a
prefix parse — so it is **TRUE** for the suffixed string. Dispatch therefore **succeeds**:
``models.py:104`` builds the client, ``models.py:109`` hands
``model.split(":")[1]`` — the whole ``gemini-2.0-flash-lite-001+camel+secpol`` — to
``GoogleLLM`` **as a model id**, and the provider-side error that follows is
indistinguishable from *"the model id is no longer served"*, which was §8.5.1's own Branch
B trigger. **A pre-registration whose negative branch can be reached by our own bug
measures nothing.** (A second, quieter consequence, recorded because it is measurable:
``models.py:105`` tests ``model == "google:gemini-2.0-flash-lite-001"`` by **equality**, so
the suffixed string also silently takes the ``max_tokens = 65535`` branch.)

**`CONTEXT.md` is amended to v1.8** (Q-057, ruled 2026-09-01): §8.5.1's Branch A now states
the two passes and this hazard, and **Branch B is taken only on a cause that has been
DIAGNOSED and recorded in `PROTOCOL.md`** — *"it errored" is not a cause, and a harness
defect is never Branch B.* This module built the two passes correctly before the ruling
existed; what changed is that the law now says what the harness does.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath, PureWindowsPath

from .. import config as cfg
from . import claims, vendor

SUITE = "banking"
"""AgentDojo's banking suite — *"what CaMeL's banking policies are written against and what
its published numbers were measured on"* (`CONTEXT.md` §8.5). Not a spec constant with a
`config/` home: it is the name of a third party's directory, re-derivable from the checkout
and asserted against it by ``test_the_banking_suite_named_here_exists_at_the_pin``."""

ENTRY_POINT = "main.py"
"""CaMeL's own CLI (``cyclopts.run(main)`` at ``main.py:114``)."""

REPLAY_PATH = "src/camel/pipeline_elements/replay_privileged_llm.py"
"""CaMeL's replayer. ⚠️ **The FILE, never a line** — the line is derived. INC-39."""

REPLAY_CALLER_CLASS = "PrivilegedLLMReplayer"
REPLAY_CALLER_METHOD = "query"
"""The **live** entry point, from ``models.py:179``. Everything else in that module that
opens a ``logs/`` path is reachable only from ``replay_benchmark``, which has no caller."""

LOG_ROOT = "logs"
"""The directory name pass 1 writes and pass 2 reads. Both are **relative**, which is the
whole of the same-working-directory requirement."""

_ABSOLUTISERS = frozenset(
    {"resolve", "absolute", "cwd", "abspath", "realpath", "expanduser"}
)
"""Any of these on the log path would make the requirement go away — and M16 is exactly
that mutation, so :attr:`LogPathClaim.is_relative` is what has to notice it."""

_READ_CALLS = frozenset({"read_text", "read_bytes", "open", "glob", "iterdir", "rglob"})
"""⚠️ **Which one it is decides the failure mode, so it is REPORTED, not assumed.**
``read_text`` over a missing file raises ``FileNotFoundError``; ``glob`` over a missing
directory yields nothing. INC-39 is that distinction getting inverted."""


class InvocationError(RuntimeError):
    """The invocation cannot be built from what `config/` and the checkout actually say."""


@dataclass(frozen=True)
class Invocation:
    """One executable pass. ⚠️ Built, never run."""

    label: str
    purpose: str
    argv: list[str]
    cwd: str
    produces_pipeline_name: str
    spends_tokens: bool
    env_var_names: list[str] = field(default_factory=list)
    """⚠️ **NAMES ONLY.** `CLAUDE.md` §4: never read, print, echo or commit a key value.
    To confirm a key exists, read only its name."""

    def command(self) -> str:
        """The command as the operator would type it. Still not executed."""
        return " ".join(self.argv)


@dataclass(frozen=True)
class Run1Plan:
    """Everything RUN-1 needs, and nothing it must decide."""

    model_string: str
    suite: str
    timebox_minutes: int
    preflight: Invocation
    """⚠️ **RUN-1's FIRST ACTION**, and it spends nothing. See :data:`HELP_FLAG`."""
    passes: list[Invocation]
    injection_task: str
    user_task_count: int
    branch_undecided_because: str | None
    log_root: str
    log_path: LogPathClaim
    """⚠️ **The derivation** :attr:`same_working_directory` **is generated from** — the
    live path, its read, its call site and whether it is relative, all located by
    :mod:`ast`. Carried as data so RUN-1 can read the facts and not only the sentence."""

    same_working_directory: str
    """Why both passes MUST run from one directory, **generated from** :attr:`log_path`.

    ⚠️ **INC-39: this field used to carry a hand-written citation to
    ``replay_privileged_llm.py:321`` — a line inside a function with no caller — and to
    promise a *silent zero*. The live read is ``read_text()``, so it raises an unhandled
    ``FileNotFoundError`` instead.** It now says whichever of the two the derivation
    actually finds, and the `file:line` in it is the one :func:`live_log_path` produced."""

    @property
    def branch_is_decided(self) -> bool:
        return self.branch_undecided_because is None


def branch_value_problem(branch: object) -> str | None:
    """What is wrong with a branch **value**, or ``None``. ⚠️ Pure, so it can be fired.

    ⚠️ **OF-75 IS WHY THIS IS A SEPARATE FUNCTION AND NOT AN `if` INSIDE THE CALLER.**
    Mutant **M12** deleted that `if` and was **proven equivalent** — because
    ``require()`` raises ``UndeterminedValue`` on the ``TODO_`` sentinel first, so today
    nothing can reach the guard. *Today* is the load-bearing word: it stops being
    equivalent the moment RUN-1 writes the key **by hand**, inside a 90-minute box, and a
    hand-written empty string is exactly what this guard is for.

    An unreachable guard that looks like a check is worse than no guard, so it is not left
    unreachable and it is not deleted: it is **lifted out to where a test can construct the
    state that reaches it**, without `config/` ever having to hold a blank.
    """
    if not isinstance(branch, str) or not branch.strip():
        return f"camel_comparator.branch is {branch!r}, which names no branch."
    return None


#: ⚠️ **THE SUPERSEDED BRANCH-B TRIGGER, CARRIED AS THE SHAPE THIS MODULE REFUSES.**
#: `CONTEXT.md` v1.7 §8.5.1 made Branch B's condition *"the model id is no longer served"*, so
#: `config/`'s Branch-A key read *"the model id is still served AND …"*. `Q-057`'s ruling narrowed
#: it, because ``"google" in model`` is **substring containment**: dispatch SUCCEEDS on the suffixed
#: pipeline name, the whole string reaches ``genai.Client`` as a model id, and the provider error
#: that follows is **indistinguishable from Branch B's own trigger**. This is the phrasing that
#: makes a harness defect look like the pre-registered negative result.
SUPERSEDED_BRANCH_TRIGGER = "model id is still served"

#: §8.5.1's Branch-B requirements, as the **spec's own** phrases. ⚠️ Each is asserted to occur in
#: `CONTEXT.md` §8.5.1 before it is required of `config/`, so this tuple cannot quietly become a
#: third copy that drifts from the law — which is the failure `Q-058` and `Q-064` are both about.
BRANCH_B_REQUIREMENTS: tuple[tuple[str, str], ...] = (
    (
        "the diagnosis requirement",
        "on a cause that has been diagnosed",
    ),
    (
        "the words that make 'it errored' insufficient",
        "is not a cause",
    ),
    (
        "the harness-defect exclusion",
        "a harness defect is never branch b",
    ),
    (
        "where the diagnosed cause is recorded before a branch is selected",
        "protocol.md",
    ),
)


def branch_condition_problems(
    branch_a_condition: object, branch_b_condition: object
) -> list[str]:
    """Every way `config/`'s two branch conditions fall short of §8.5.1 v1.9. Empty is a pass.

    ⚠️ **`Q-079` IS WHY THIS EXISTS, AND THE REASON IS ONE SENTENCE: NOTHING READ THAT KEY.**
    `Q-064` named `branch_a_condition` as carrying the **un-narrowed** Branch-B trigger and
    printed the cause as a number — *"`grep -rn` returns one hit, the definition itself"*.
    A fix session with the file open corrected the sibling key and not this one, and no
    test could have noticed, because **a pre-registered condition that nothing asserts is a
    comment**. `config/` is a pre-registration artefact and hard rule 4 makes a **frozen**
    one outrank `CONTEXT.md`, so after `prereg-v1` this string would have been the higher
    authority on which branch RUN-1 takes.

    ⚠️ **A LIST, NOT A BOOL, AND PURE** — the same two choices as
    :func:`branch_value_problem` and :func:`branch_b.assert_provenance`, for the same two
    reasons. A failure must **name the field**, because a gate whose only output is *"no"*
    is a gate somebody edits out under time pressure; and the predicate must be firable at
    a constructed value, so the guard can be proved to go red **without `config/` ever
    having to hold the defective string**.

    ⚠️ **Branch B is the NEGATION of Branch A**, which is exactly how the defect survived:
    `Q-079` records that with no `branch_b_condition` key, `config/` bound the project to
    taking its pre-registered negative branch whenever *"the run does not complete"*, with
    **no diagnosis requirement** — the thing `Q-057`'s ruling forbade in terms: *"a
    pre-registration whose negative branch can be reached by our own bug measures
    nothing."* So Branch B's trigger is required to be **stated**, never inferred.
    """
    problems: list[str] = []
    for label, value in (
        ("branch_a_condition", branch_a_condition),
        ("branch_b_condition", branch_b_condition),
    ):
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{label} is {value!r}, which states no condition.")
            continue
        if SUPERSEDED_BRANCH_TRIGGER in value.lower():
            problems.append(
                f"{label} still carries {SUPERSEDED_BRANCH_TRIGGER!r}, the pre-Q-057 "
                f"trigger. That phrasing is indistinguishable from a harness defect: "
                f"dispatch succeeds on substring containment, so a provider error on the "
                f"suffixed string would present as the pre-registered negative result."
            )

    if not isinstance(branch_b_condition, str):
        return problems
    lowered = branch_b_condition.lower()
    for what, phrase in BRANCH_B_REQUIREMENTS:
        if phrase not in lowered:
            problems.append(
                f"branch_b_condition does not carry {what} ({phrase!r}). CONTEXT.md v1.9 "
                f"§8.5.1: Branch B is taken only on a cause that has been DIAGNOSED and "
                f"recorded in PROTOCOL.md before a branch is selected; 'it errored' is not "
                f"a cause, and a harness defect is never Branch B."
            )
    return problems


def branch_conditions_are_stale() -> list[str]:
    """:func:`branch_condition_problems` over the two keys `config/` actually holds.

    ⚠️ ``require()`` is the only read path, so a missing file and a missing key are the
    same answer rather than two different silences — and a **missing** `branch_b_condition`
    is the exact state `Q-079` found, so it must be a refusal and never an empty pass.
    """
    try:
        lanes = cfg.load("lanes")
        return branch_condition_problems(
            lanes.require("camel_comparator.branch_a_condition"),
            lanes.require("camel_comparator.branch_b_condition"),
        )
    except cfg.ConfigError as exc:
        return [f"{type(exc).__name__}: {exc}"]


def branch_is_undecided() -> str | None:
    """Why the CaMeL branch is not yet decided, or ``None`` once RUN-1 has decided it.

    ⚠️ ``require()`` is the only read path, so a missing file, a missing key and a ``TODO_``
    sentinel are all the same answer — *"nobody has decided"* — rather than three different
    silences. Hard rule 9 forbids substituting a value here, and this function never does:
    it **reports**.
    """
    try:
        branch = cfg.load("lanes").require("camel_comparator.branch")
    except cfg.ConfigError as exc:
        return f"{type(exc).__name__}: {exc}"
    return branch_value_problem(branch)


def spec_timebox_minutes(context_md: str) -> int:
    """§8.5.1's *"timeboxed to 90 minutes"*, parsed rather than hardcoded.

    ⚠️ Parsed for two reasons, and the second is the real one. It keeps a spec-stated
    number out of first-party source (hard rule 9's spirit), **and** the alternative —
    adding a ``config/`` key — is outside this chunk's fence, which permits exactly one new
    key, ``vendor.camel_sha``. Inventing a second would be the silent scope creep the
    fences exist to stop.
    """
    text = claims._section(context_md, "### 8.5.1 ")
    matches = sorted({int(m) for m in re.findall(r"timeboxed to (\d+) minutes", text)})
    if len(matches) != 1:
        raise InvocationError(
            f"CONTEXT.md S8.5.1 states {len(matches)} distinct timebox value(s) "
            f"({matches}), not one. RUN-1's box is what makes Branch B reachable rather "
            f"than a run that never ends."
        )
    return matches[0]


def google_api_key_var(root: Path | None = None) -> str:
    """The environment variable CaMeL reads for Google, **derived from the checkout**.

    ⚠️ Derived, not written down, and the **name** only. `CLAUDE.md` §4 permits reading a
    key's name to confirm it exists and nothing more; this function never opens ``.env``.
    """
    root = root if root is not None else vendor.vendor_root()
    source = vendor.blob_text(root, vendor.MODELS_PATH)
    found = sorted(set(re.findall(r'os\.getenv\("([A-Z0-9_]*GOOGLE[A-Z0-9_]*)"\)', source)))
    if len(found) != 1:
        raise InvocationError(
            f"models.py names {len(found)} Google environment variable(s) ({found}) at the "
            f"pin, not one. The operator would not know which key to set."
        )
    return found[0]


HELP_FLAG = "--help"
"""``cyclopts`` supplies this one; it is not a parameter of ``main``, so it is not derived.

⚠️ It costs nothing and it is **RUN-1's first action**, because :func:`cli_flags` derives
the other spellings from a *signature* and **this argv has never been executed** — no
session on this project may spend a token here. `--help` converts a derivation into an
observation for the price of zero tokens, inside a 90-minute box where that matters."""


def _find_function(tree: ast.Module, name: str, path: str) -> ast.FunctionDef:
    found = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if len(found) != 1:
        raise InvocationError(
            f"{path} defines {len(found)} function(s) named {name!r} at the pin, not one. "
            f"The flag spellings are derived from its signature; deriving them from the "
            f"wrong function would hand RUN-1 an argv that silently does something else."
        )
    return found[0]


@dataclass(frozen=True)
class LogPathClaim:
    """Where pass 2 reads pass 1's logs — **located by** :mod:`ast`, **proved reachable**.

    ⚠️ **INC-39 IS THE REASON EVERY FIELD HERE IS DERIVED RATHER THAN WRITTEN.** The
    previous version of this claim was a sentence carrying a line number, and the line
    number was inside a function nothing calls. A sentence cannot be wrong about a call
    graph it never consulted; this object can only be built by consulting one.
    """

    function: str
    """The function that actually builds the path — **derived**, not named in advance."""

    span: tuple[int, int]
    """First and last line of the path expression."""

    read_line: int
    read_call: str
    """⚠️ **The failure mode, as a fact.** ``read_text`` → unhandled ``FileNotFoundError``
    (loud). ``glob`` → an empty iterator (a silent zero). INC-39 is these two swapped."""

    called_at: int
    called_from: str
    """The live call site. Its existence is what makes :attr:`function` reachable at all."""

    root_literal: str
    is_relative: bool
    """⚠️ **The same-working-directory requirement, as a boolean.** False the moment the
    root is absolute or anything in the function resolves it."""

    unreachable_others: tuple[str, ...]
    """Every OTHER function in the module that opens a ``logs/`` path and **cannot be
    reached** from the live caller. Reported so the dead scaffolding is on the record —
    and asserted only as *"the others are all unreachable"*, never as *"they exist"*, so
    deleting them changes no verdict."""

    @property
    def crashes_loudly(self) -> bool:
        """⚠️ True when a missing log tree RAISES instead of reporting nothing.

        RUN-1 needs this: a loud crash inside the 90-minute box is diagnosable, and a
        silent zero is a number nobody can tell from a real one.
        """
        return self.read_call in {"read_text", "read_bytes", "open"}

    def citation(self) -> str:
        """``<file>:<start>-<end>`` — the citation, generated from the derivation."""
        return f"{REPLAY_PATH}:{self.span[0]}-{self.span[1]}"

    def read_citation(self) -> str:
        return f"{REPLAY_PATH}:{self.read_line}"


def _path_root_literal(node: ast.AST) -> str | None:
    """The string in ``Path("...")`` at the head of a ``/``-chain, or ``None``.

    Walks the **left spine** of the ``BinOp`` chain, because ``Path("logs") / a / b`` parses
    as ``((Path("logs") / a) / b)`` and the root is the deepest left operand.
    """
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        node = node.left
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Path"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    ):
        return node.args[0].value
    return None


def _is_relative_literal(root: str) -> bool:
    """Whether a ``Path(...)`` literal is relative — **on POSIX *and* Windows rules.**

    ⚠️ Both, deliberately. ``PureWindowsPath("/var/logs").is_absolute()`` is **False**
    (no drive), so a Windows-only check would call CaMeL's own POSIX-style absolute path
    relative and M16 would walk straight through the guard written to stop it.
    """
    return not (
        PurePosixPath(root).is_absolute() or PureWindowsPath(root).is_absolute()
    )


def _log_path_construction(func: ast.FunctionDef) -> tuple[str, tuple[int, int], str] | None:
    """``(assigned name, (start, end), root literal)`` for a ``Path(".../logs")/…`` in *func*.

    ⚠️ **Matched on the root's final COMPONENT, not on the whole literal.** ``Path("logs")``
    and ``Path("/var/logs")`` must both be found, because M16 — *make the live path
    absolute* — is exactly the second, and a matcher that stopped recognising the path once
    it was made absolute would report **"no live path"** instead of **"the requirement is
    gone"**. Those are different findings and only one of them is true.
    """
    for node in ast.walk(func):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        root = _path_root_literal(node.value)
        if root is None or PurePosixPath(root).name != LOG_ROOT:
            continue
        start = node.value.lineno
        end = node.value.end_lineno or start
        return target.id, (start, end), root
    return None


def _base_name(node: ast.AST) -> str | None:
    """The root ``Name`` of an attribute/call chain — ``a.b().c()`` → ``a``.

    ⚠️ Chains are unwrapped rather than matched one level deep so that
    ``trace_path.resolve().read_text()`` is still recognised as a **read of the log
    path**. A one-level matcher would miss it and report *"the path is never read"*, which
    is again the wrong finding for M16's second form.
    """
    while isinstance(node, (ast.Call, ast.Attribute)):
        node = node.func if isinstance(node, ast.Call) else node.value
    return node.id if isinstance(node, ast.Name) else None


def _read_site(func: ast.FunctionDef, name: str) -> tuple[int, str] | None:
    """The first ``<name>….<read call>()`` in *func*, as ``(line, attribute)``."""
    sites = [
        (node.lineno, node.func.attr)
        for node in ast.walk(func)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in _READ_CALLS
        and _base_name(node.func.value) == name
    ]
    return sorted(sites)[0] if sites else None


def _absolutises(func: ast.FunctionDef, name: str) -> bool:
    """Whether *func* turns *name* — or any path — into an absolute one."""
    for node in ast.walk(func):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in _ABSOLUTISERS:
                return True
    return False


def _named_functions(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    """Every function in the module by **bare name**, methods included as ``Class.method``."""
    found: dict[str, ast.FunctionDef] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            found[node.name] = node
        elif isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    found[f"{node.name}.{child.name}"] = child
    return found


def _bare_calls(func: ast.FunctionDef) -> set[str]:
    """Every ``name(...)`` call in *func*. Attribute calls are not resolved — deliberately:
    an unresolved edge can only make the reachable set SMALLER, never larger, so a claim
    of *"reachable"* built on it is never an over-claim."""
    return {
        node.func.id
        for node in ast.walk(func)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }


def _reachable_from(functions: dict[str, ast.FunctionDef], root: str) -> set[str]:
    """Transitive closure of bare-name calls out of *root*."""
    seen: set[str] = set()
    queue = [root]
    while queue:
        current = queue.pop()
        if current in seen or current not in functions:
            continue
        seen.add(current)
        queue.extend(_bare_calls(functions[current]))
    return seen


def live_log_path_from_source(source: str) -> LogPathClaim:
    """Locate the log path pass 2 **actually** reads, over source **text** — pure.

    ⚠️ **Split out for the same reason** :func:`cli_flags_from_source` **is** (`PROCESS.md`
    §5.4): a gate that cannot be pointed at a mutated input is a gate nobody has seen go
    red. Every mutant behind INC-39 is fired at *this* function, so **not one byte of
    ``vendor/`` is touched to prove it fires.**

    The derivation, in order, so the refusals are legible:

      1. every function that builds a ``Path("logs")/...`` — there are three at the pin;
      2. the live caller, ``PrivilegedLLMReplayer.query``;
      3. what that caller can reach, transitively, through bare-name calls;
      4. **the intersection, which must be exactly one function.** That one is the live
         path; the rest are named as unreachable and nothing asserts they exist.
    """
    tree = ast.parse(source)
    functions = _named_functions(tree)

    constructions = {
        name: built
        for name, node in functions.items()
        if (built := _log_path_construction(node)) is not None
    }
    if not constructions:
        raise InvocationError(
            f"{REPLAY_PATH} builds no `Path({LOG_ROOT!r})` path at the pin. Pass 2 reads "
            f"pass 1's logs by that path; if it is gone, the two-pass protocol Q-057 "
            f"records is no longer what the code does."
        )

    caller = f"{REPLAY_CALLER_CLASS}.{REPLAY_CALLER_METHOD}"
    if caller not in functions:
        raise InvocationError(
            f"{REPLAY_PATH} defines no {caller} at the pin. That method IS the live entry "
            f"point (models.py:179 constructs it); without it there is no code path from "
            f"the CLI to the replay at all."
        )

    reachable = _reachable_from(functions, caller)
    live = sorted(set(constructions) & reachable)
    if len(live) != 1:
        raise InvocationError(
            f"{caller} reaches {len(live)} function(s) that open a `Path({LOG_ROOT!r})` "
            f"path ({live}), not exactly one. Candidates in the module: "
            f"{sorted(constructions)}. ⚠️ INC-39: citing a line inside a function nothing "
            f"calls is how this claim was wrong before, so 'exactly one REACHABLE one' is "
            f"the whole check and a bare 'the string is present' is not."
        )

    name = live[0]
    variable, span, root = constructions[name]
    read = _read_site(functions[name], variable)
    if read is None:
        raise InvocationError(
            f"{REPLAY_PATH}:{name} builds the log path and never reads it. The claim that "
            f"pass 2 replays pass 1's stored logs rests on that read."
        )
    call_lines = sorted(
        node.lineno
        for node in ast.walk(functions[caller])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == name
    )
    return LogPathClaim(
        function=name,
        span=span,
        read_line=read[0],
        read_call=read[1],
        called_at=call_lines[0],
        called_from=caller,
        root_literal=root,
        is_relative=(
            _is_relative_literal(root) and not _absolutises(functions[name], variable)
        ),
        unreachable_others=tuple(sorted(set(constructions) - reachable)),
    )


def live_log_path(root: Path | None = None) -> LogPathClaim:
    """:func:`live_log_path_from_source` over the **git blob** at the pin."""
    root = root if root is not None else vendor.vendor_root()
    return live_log_path_from_source(vendor.blob_text(root, REPLAY_PATH))


def same_working_directory_reason(cwd: str, claim: LogPathClaim) -> str:
    """RUN-1's same-working-directory warning, **generated from the derivation.**

    ⚠️ **The citation in this sentence is the one** :func:`live_log_path_from_source`
    **produced**, so the prose cannot drift from the code the way INC-39's did. The failure
    mode is likewise read off :attr:`LogPathClaim.crashes_loudly` rather than asserted.
    """
    if claim.crashes_loudly:
        consequence = (
            f"pass 2 started from any other directory raises an UNHANDLED "
            f"FileNotFoundError at {claim.read_citation()} ({claim.read_call}) - "
            f"{claim.called_from} has no try/except and AgentDojo catches only "
            f"AbortAgentError. IT CRASHES LOUDLY, which is the diagnosable failure and "
            f"NOT a silent zero"
        )
    else:  # pragma: no cover - the pin reads with read_text; kept so the claim stays honest
        consequence = (
            f"pass 2 started from any other directory reads an EMPTY tree via "
            f"{claim.read_call} at {claim.read_citation()} and reports nothing rather "
            f"than failing - a SILENT ZERO, which is the undiagnosable failure"
        )
    return (
        f"BOTH PASSES RUN FROM `{cwd}`. {claim.citation()} ({claim.function}, called at "
        f"{REPLAY_PATH}:{claim.called_at} from {claim.called_from}) opens a RELATIVE "
        f'Path("{claim.root_literal}") / <pass-1 pipeline name> / ... , so {consequence} '
        f"- inside a single-shot 90-minute box."
    )


def cli_flags_from_source(source: str) -> dict[str, str]:
    """:func:`cli_flags`, over source **text** — pure, so it can be fired at a fixture.

    ⚠️ Split out for exactly that reason. :func:`cli_flags` reads a git blob out of a real
    checkout, which a temp-directory fixture is not, and a gate that cannot be pointed at a
    mutated input is a gate nobody has seen go red (`PROCESS.md` §5.4).
    """
    if "cyclopts.run(" not in source:
        raise InvocationError(
            f"{ENTRY_POINT} no longer calls cyclopts.run at the pin. The kebab-casing rule "
            f"that turns a parameter name into a flag is cyclopts'; without it these "
            f"spellings are guesses."
        )
    main_fn = _find_function(ast.parse(source), "main", ENTRY_POINT)
    args = [*main_fn.args.posonlyargs, *main_fn.args.args, *main_fn.args.kwonlyargs]
    return {arg.arg: "--" + arg.arg.replace("_", "-") for arg in args}


def cli_flags(root: Path | None = None) -> dict[str, str]:
    """``main.py``'s parameter names, kebab-cased into flags — **DERIVED, NOT TRANSCRIBED.**

    ⚠️ This is the claim `QUESTIONS.md` **Q-057** turns on, so it is a derivation rather
    than a sentence. ``main.py`` ends in ``cyclopts.run(main)``, and **cyclopts kebab-cases
    a parameter name into its flag**, so ``replay_with_policies`` is
    ``--replay-with-policies``. Writing the four flags as string literals would be a second
    copy of a third party's CLI that can drift from it silently — the exact class
    `INCIDENTS.md` **INC-02** and **INC-05** record.

    ⚠️ **What this does NOT establish, stated so it is not mistaken for observed:** the
    argv has never been executed here and no token may be spent to execute it. This proves
    the *parameter names*, not cyclopts' rendering of them. :data:`HELP_FLAG` is RUN-1's
    first action for exactly that reason.
    """
    root = root if root is not None else vendor.vendor_root()
    return cli_flags_from_source(vendor.blob_text(root, ENTRY_POINT))


def require_flags(flags: dict[str, str], *names: str) -> list[str]:
    """Look up derived flags by PARAMETER name, refusing on any that is not there."""
    missing = [name for name in names if name not in flags]
    if missing:
        raise InvocationError(
            f"main.py's signature has no parameter(s) {missing} at the pin, so RUN-1's "
            f"command cannot be derived. Available: {sorted(flags)}. A hardcoded flag would "
            f"have been silently wrong instead."
        )
    return [flags[name] for name in names]


def base_pipeline_name(model_string: str) -> str:
    """The ``+camel`` pipeline name pass 1 writes and pass 2 reads.

    ``models.py:174`` builds it as ``f"{model.split(':')[1]}+camel"``. Reproduced here
    because **pass 2 finds pass 1's logs by this exact string**; get it wrong and the
    replay reads an empty directory and reports nothing rather than failing.
    """
    if ":" not in model_string:
        raise InvocationError(
            f"model string {model_string!r} has no `provider:id` colon. CaMeL splits on it "
            f"(models.py:109/129) and would index past the end of the list."
        )
    return f"{model_string.split(':', 1)[1]}+camel"


def secpol_pipeline_name(model_string: str) -> str:
    """The ``+camel+secpol`` name CaMeL **emits** at ``models.py:188``.

    ⚠️ This is the string `CONTEXT.md` §8.5.1 tells the operator to *invoke*. It is an
    output, not an input. See this module's header and `QUESTIONS.md` **Q-057**.
    """
    return base_pipeline_name(model_string) + "+secpol"


def run1_plan(context_md: str, root: Path | None = None) -> Run1Plan:
    """Build RUN-1's two passes. **Nothing here executes, and nothing here decides.**"""
    root = root if root is not None else vendor.vendor_root()
    lanes = cfg.load("lanes")
    protocol = cfg.load("protocol")
    # ⚠️ DERIVED, and its enclosing function PROVED REACHABLE, before any prose uses it.
    # INC-39: the citation this replaces was inside a function nothing calls.
    log_path = live_log_path(root)

    model_string = lanes.require("camel_comparator.model_string")
    injection_task = protocol.require("selections.agentdojo_injection_task")
    user_task_count = protocol.require("selections.agentdojo_user_task_count")
    key_var = google_api_key_var(root)
    cwd = f"vendor/{vendor.CAMEL_DIRNAME}"

    # ⚠️ DERIVED from main.py's signature at the pin, never written down here. Q-057.
    flags = cli_flags(root)
    model_flag, suites_flag, attack_flag, replay_flag = require_flags(
        flags, "model", "suites", "run_attack", "replay_with_policies"
    )

    common = [
        "python",
        ENTRY_POINT,
        model_flag,
        model_string,
        suites_flag,
        SUITE,
        attack_flag,
    ]

    preflight = Invocation(
        label="step 0 - preflight, and it is RUN-1's FIRST ACTION",
        purpose=(
            "Prints CaMeL's CLI and spends NOTHING. The flag spellings below are DERIVED "
            "from main.py's signature (cyclopts kebab-cases each parameter name), and "
            "THIS ARGV HAS NEVER BEEN EXECUTED - no session on this project may spend a "
            "token to try it. --help turns the derivation into an observation for free, "
            "before the 90-minute box starts running."
        ),
        argv=["python", ENTRY_POINT, HELP_FLAG],
        cwd=cwd,
        produces_pipeline_name="",
        spends_tokens=False,
        env_var_names=[],
    )

    passes = [
        Invocation(
            label="pass 1 of 2 - the CaMeL run",
            purpose=(
                "Produces the `+camel` pipeline: the privileged LLM emits a program and "
                "CaMeL's own AST interpreter executes it. THIS IS THE PASS THAT SPENDS "
                "TOKENS, and its logs are the input pass 2 replays."
            ),
            argv=list(common),
            cwd=cwd,
            produces_pipeline_name=base_pipeline_name(model_string),
            spends_tokens=True,
            env_var_names=[key_var],
        ),
        Invocation(
            label="pass 2 of 2 - the security-policy replay",
            purpose=(
                f"Adds --replay-with-policies. PrivilegedLLMReplayer re-executes pass 1's "
                f"STORED programs through BankingSecurityPolicyEngine and produces the "
                f"`+camel+secpol` pipeline. It reads logs/<pass-1 name>/... "
                f"({log_path.citation()} - {log_path.function}, read at "
                f"{log_path.read_citation()} by {log_path.read_call}, called at "
                f"{REPLAY_PATH}:{log_path.called_at} from {log_path.called_from}), so it "
                f"MUST run from the same working directory as pass 1, AFTER pass 1 has "
                f"completed."
            ),
            argv=[*common, replay_flag],
            cwd=cwd,
            produces_pipeline_name=secpol_pipeline_name(model_string),
            spends_tokens=False,
            env_var_names=[key_var],
        ),
    ]

    return Run1Plan(
        model_string=model_string,
        suite=SUITE,
        timebox_minutes=spec_timebox_minutes(context_md),
        preflight=preflight,
        passes=passes,
        injection_task=injection_task,
        user_task_count=user_task_count,
        branch_undecided_because=branch_is_undecided(),
        log_root=f"{cwd}/{log_path.root_literal}",
        log_path=log_path,
        same_working_directory=same_working_directory_reason(cwd, log_path),
    )


def suite_version_from_source(source: str) -> str:
    """The AgentDojo suite version ``main.py`` loads — **derived from its own call**.

    ⚠️ **OF-73/OF-74.** C13 read ``default_suites/v1/banking``; ``main.py:79`` is
    ``get_suite("v1.2", suite_name)``, so the copy the run executes is ``v1_2``. Writing
    ``"v1"`` here would be a second copy of a third party's choice — INC-02's class, and
    the same class as INC-39 one file over: **reading a file that is not the one the run
    executes.** So it is parsed, and a change to it is a loud refusal.
    """
    versions = sorted(
        {
            str(node.args[0].value)
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "get_suite"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        }
    )
    if len(versions) != 1:
        raise InvocationError(
            f"{ENTRY_POINT} calls get_suite with {len(versions)} distinct version(s) "
            f"({versions}) at the pin, not one. C16 runs this same suite and would be "
            f"scored against whichever copy a session happened to read."
        )
    return versions[0]


def suite_version(root: Path | None = None) -> str:
    """:func:`suite_version_from_source` over ``main.py``'s git blob."""
    root = root if root is not None else vendor.vendor_root()
    return suite_version_from_source(vendor.blob_text(root, ENTRY_POINT))


def suite_package(version: str) -> str:
    """AgentDojo's dotted suite version → its package directory. ``v1.2`` → ``v1_2``."""
    return "v" + version.lstrip("v").replace(".", "_")


def banking_suite_dir(dojo_root: Path, version: str) -> Path:
    """Where a given suite version's ``banking`` package lives in the AgentDojo checkout."""
    return dojo_root / "src" / "agentdojo" / "default_suites" / suite_package(version) / SUITE


def banking_suite_exists(root: Path | None = None, version: str = "v1") -> bool:
    """Whether AgentDojo's banking suite is present, **for the version asked about**.

    ⚠️ Asserted rather than assumed because :data:`SUITE` is a bare string in first-party
    source. If AgentDojo ever renames the directory, this goes false and a test says so —
    instead of RUN-1 discovering it inside the 90-minute box.

    ⚠️ **OF-74: the version is now a PARAMETER and it defaults to ``v1`` deliberately.**
    ``v1`` is where banking's ``task_suite.py`` and ``user_tasks.py`` live; ``v1_2``
    carries **only** ``injection_tasks.py`` and overrides into the same registry object.
    So *"does banking exist"* and *"which injection task will run"* are two questions, and
    conflating them is what OF-73 records. The caller says which it is asking.
    """
    root = root if root is not None else vendor.agentdojo_root()
    return banking_suite_dir(root, version).is_dir()
