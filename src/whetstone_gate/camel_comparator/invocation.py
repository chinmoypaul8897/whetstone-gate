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
  * ``replay_privileged_llm.py:321`` reads
    ``Path("logs") / pipeline_name / suite_name / user_task_id / attack_name`` — i.e. **the
    stored logs of the earlier ``+camel`` pass.**

So Branch A is **two passes**: pass 1 produces ``+camel`` and is the pass that spends
tokens; pass 2 adds ``--replay-with-policies``, replays pass 1's logs through
``BankingSecurityPolicyEngine``, and produces ``+camel+secpol``.

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
from pathlib import Path

from .. import config as cfg
from . import claims, vendor

SUITE = "banking"
"""AgentDojo's banking suite — *"what CaMeL's banking policies are written against and what
its published numbers were measured on"* (`CONTEXT.md` §8.5). Not a spec constant with a
`config/` home: it is the name of a third party's directory, re-derivable from the checkout
and asserted against it by ``test_the_banking_suite_named_here_exists_at_the_pin``."""

ENTRY_POINT = "main.py"
"""CaMeL's own CLI (``cyclopts.run(main)`` at ``main.py:114``)."""


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
    same_working_directory: str
    """Why both passes MUST run from one directory, in the words of the code that requires
    it. ``replay_privileged_llm.py:321`` opens a **relative** ``Path("logs")``, so pass 2
    run from anywhere else reads an empty tree and **reports nothing rather than failing**
    — a silent zero inside a single-shot 90-minute box."""

    @property
    def branch_is_decided(self) -> bool:
        return self.branch_undecided_because is None


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
    if not isinstance(branch, str) or not branch.strip():
        return f"camel_comparator.branch is {branch!r}, which names no branch."
    return None


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
                "Adds --replay-with-policies. PrivilegedLLMReplayer re-executes pass 1's "
                "STORED programs through BankingSecurityPolicyEngine and produces the "
                "`+camel+secpol` pipeline. It reads logs/<pass-1 name>/... "
                "(replay_privileged_llm.py:321), so it MUST run from the same working "
                "directory as pass 1, AFTER pass 1 has completed."
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
        log_root=f"{cwd}/logs",
        same_working_directory=(
            f"BOTH PASSES RUN FROM `{cwd}`. replay_privileged_llm.py:321 opens a RELATIVE "
            f'Path("logs") / <pass-1 pipeline name> / ... , so pass 2 started from any '
            f"other directory reads an EMPTY tree and reports nothing rather than failing "
            f"- a silent zero inside a single-shot 90-minute box."
        ),
    )


def banking_suite_exists(root: Path | None = None) -> bool:
    """Whether AgentDojo's banking suite is present in the vendored checkout.

    ⚠️ Asserted rather than assumed because :data:`SUITE` is a bare string in first-party
    source. If AgentDojo ever renames the directory, this goes false and a test says so —
    instead of RUN-1 discovering it inside the 90-minute box.
    """
    root = root if root is not None else vendor.agentdojo_root()
    return (root / "src" / "agentdojo" / "default_suites" / "v1" / SUITE).is_dir()
