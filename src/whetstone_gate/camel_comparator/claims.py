"""The claims `CONTEXT.md` §8.5/§8.5.1 makes about CaMeL, each re-derived at the pin.

⚠️ **NOTHING IN THIS MODULE TRANSCRIBES A LINE NUMBER, A BYTE COUNT OR A STRING FROM THE
SPECIFICATION.** Every expected value is **parsed out of `CONTEXT.md`**; every observed
value is **derived from the vendored checkout with** :mod:`ast`. The two sides come from
two places and the test diffs them, so a divergence is a finding on one of them rather
than a green test over a copy that agrees with itself.

That shape is `QUESTIONS.md` **Q-016**/**Q-020**/**Q-031**'s enforcement made executable,
and it is the reason a `full` chunk with no golden is still checkable.

WHY :mod:`ast` AND NOT :func:`re`
=================================
Three of the four claims are about a **signature's arity** — *"the ENGINE's method is
``check_policy(tool_name, kwargs, dependencies)``; the TWO-argument shape is the per-tool
policy callback"*. §8.5 records that **the previous draft got this exactly backwards.** A
regex over source text can confirm that a string appears; it cannot confirm that a call
passes three arguments, that a dispatch chain's final ``else`` raises, or that a denial is
the **last** statement of a method. :mod:`ast` can, and does, below.

⚠️ **CaMeL IS PARSED, NEVER IMPORTED.** Importing it would pull ``google.genai``,
``openai`` and ``anthropic`` into this package's import graph — three model clients, in the
one package whose job is to *not* call a model.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from . import vendor

CLAIM_IDS = (
    "3a_interpreter_is_a_hand_written_ast_interpreter",
    "3b_engine_method_takes_three_arguments",
    "3b_interpreter_passes_all_three",
    "3b_per_tool_callback_takes_two_arguments",
    "3c_deny_by_default_is_the_last_branch",
    "3d_provider_dispatch_is_the_real_gate",
    "3d_gemini_lite_is_in_the_name_list",
    "3d_gemini_lite_has_its_own_max_tokens_branch",
)
"""Every claim this module re-derives, in the order the C13 prompt states them."""


class ClaimError(RuntimeError):
    """A claim could not be re-derived because the construct it names is not there."""


@dataclass(frozen=True)
class ClaimVerdict:
    """One re-verified third-party claim.

    ⚠️ ``holds`` false is **not** an error to swallow. `PROCESS.md` §9: every third-party
    claim carries a URL and a date, and anything unverified is tagged or deleted. A verdict
    that does not hold is a **finding**, and it outranks finishing the chunk.
    """

    claim_id: str
    what_the_spec_says: str
    where: str
    expected: object
    observed: object
    holds: bool
    note: str = ""


# ======================================================================================
# THE SPEC SIDE — parsed out of CONTEXT.md. Nothing here is written by hand.
# ======================================================================================


def _section(markdown: str, heading: str) -> str:
    """Return one section of `CONTEXT.md`, raw (line structure preserved).

    Ends at the next heading of the **same or shallower** depth, so §8.5 does not swallow
    §8.5.1 and §8.5.1 does not swallow §8.6.
    """
    lines = markdown.splitlines()
    depth = len(heading) - len(heading.lstrip("#"))
    starts = [i for i, line in enumerate(lines) if line.startswith(heading)]
    if len(starts) != 1:
        raise ClaimError(
            f"{heading!r} matched {len(starts)} times in CONTEXT.md, not once. Either the "
            f"specification was reworded or this parser stopped seeing it - and a parser "
            f"that silently reads nothing reports green over an unchecked claim."
        )
    start = starts[0]
    end = len(lines)
    for i in range(start + 1, len(lines)):
        stripped = lines[i].lstrip("#")
        this_depth = len(lines[i]) - len(stripped)
        if lines[i].startswith("#") and this_depth <= depth:
            end = i
            break
    return "\n".join(lines[start:end])


def _spec_text(context_md: str) -> str:
    """§8.5 **including** its subsections, whitespace-normalised into one string.

    Normalised because `CONTEXT.md` wraps its prose and several references straddle a line
    break mid-phrase — *"is in `_supported_model_names`\\n(`models.py:40`)"*. A parser
    written against the raw text would match on the author's line width.

    ⚠️ **§8.5's slice already contains §8.5.1 and §8.5.2**, because :func:`_section` ends at
    the next heading of the same or shallower depth and those are deeper. Concatenating
    §8.5.1 on top would double every anchor in it and turn each *"occurs once"* check into a
    false alarm — which is exactly what it did on first run, and is why the check is written
    as *"exactly once"* rather than *"at least once"*.
    """
    return re.sub(r"\s+", " ", _section(context_md, "## 8.5 "))


#: Each claim's reference is found by the prose that INTRODUCES it, never by its position
#: in a list. ⚠️ This is not decoration. §8.5 states four distinct `security_policy.py`
#: references and §8.5.1 four `models.py` ones, and **two pairs of them span the same
#: number of lines** — ``77-82`` and ``44-49`` are both six, ``:40`` and ``:67`` are both
#: one. Anything that picked "the first" or "the six-line one" would compare a claim
#: against a *different* claim's expected value and still print green.
_ANCHORS: dict[str, tuple[str, str]] = {
    "engine_signature": ("check_policy(tool_name, kwargs, dependencies)", "security_policy.py"),
    "interpreter_call": ("passes all three at", "interpreter.py"),
    "per_tool_callback": ("two-argument", "security_policy.py"),
    "deny_by_default": ("ends at", "security_policy.py"),
    "provider_dispatch": ("provider-prefix dispatch", "models.py"),
    "name_list_span": ("That set", "models.py"),
    "gemini_id_line": ("is in `_supported_model_names`", "models.py"),
    "max_tokens_branch": ("with a dedicated", "models.py"),
}

_REF = r"`?{name}:(\d+)(?:-(\d+))?"


def spec_line_references(context_md: str) -> dict[str, tuple[int, int]]:
    """Each claim's ``(start, end)`` line range, taken from the prose that introduces it.

    A bare ``:<n>`` becomes ``(n, n)`` — a single line is a range of one, and
    special-casing it here would mean special-casing it in every caller.

    ⚠️ No line number is written into this module, not even as an example. The
    hardcoded-value tripwire caught one in this very docstring: CaMeL's
    ``interpreter.py`` call site collides with a seed in `CONTEXT.md` §8.6's seed list.
    The collision was a false positive; **writing the number at all was not**, and the
    remedy was to derive it, exactly as hard rule 9 says.
    """
    text = _spec_text(context_md)
    found: dict[str, tuple[int, int]] = {}
    for claim, (anchor, filename) in _ANCHORS.items():
        occurrences = [m.end() for m in re.finditer(re.escape(anchor), text)]
        if len(occurrences) != 1:
            raise ClaimError(
                f"the anchor {anchor!r} occurs {len(occurrences)} times in CONTEXT.md "
                f"S8.5/S8.5.1, not once. Either the specification was reworded or this "
                f"parser stopped seeing it - and a parser that silently reads nothing "
                f"reports green over an unchecked claim."
            )
        match = re.search(_REF.format(name=re.escape(filename)), text[occurrences[0] :])
        if match is None:
            raise ClaimError(
                f"CONTEXT.md states no `{filename}:<line>` reference after {anchor!r}. "
                f"That reference IS claim {claim!r}; reading none of it would make the "
                f"line-number check vacuously true."
            )
        start = int(match.group(1))
        found[claim] = (start, int(match.group(2)) if match.group(2) else start)
    return found


def spec_interpreter_size(context_md: str) -> tuple[int, int]:
    """§8.5's *"100,476 bytes, 2,716 lines"*, parsed rather than copied."""
    text = _spec_text(context_md)
    matches = re.findall(r"\*\*([\d,]+) bytes, ([\d,]+) lines\*\*", text)
    if len(matches) != 1:
        raise ClaimError(
            f"the interpreter-size parser matched {len(matches)} times in CONTEXT.md "
            f"S8.5, not once."
        )
    return int(matches[0][0].replace(",", "")), int(matches[0][1].replace(",", ""))


def spec_deny_by_default_string(context_md: str) -> str:
    """§8.5's deny-by-default reason, taken from the spec's own quotation of it."""
    text = _spec_text(context_md)
    matches = sorted(set(re.findall(r"Denied\(\"([^\"]+Defaulting to denial\.)\"\)", text)))
    if not matches:
        raise ClaimError(
            "CONTEXT.md S8.5 no longer quotes the deny-by-default string, which IS claim 3c."
        )
    return matches[0]


def spec_model_id(context_md: str) -> str:
    """The Gemini id §8.5.1 says CaMeL allowlists."""
    text = re.sub(r"\s+", " ", _section(context_md, "### 8.5.1 "))
    matches = sorted(set(re.findall(r"`(gemini-[\w.\-]+)`", text)))
    if len(matches) != 1:
        raise ClaimError(
            f"CONTEXT.md S8.5.1 names {len(matches)} distinct gemini ids ({matches}), not "
            f"one. Claim 3d is about exactly one id."
        )
    return matches[0]


def spec_max_tokens(context_md: str) -> int:
    """§8.5.1's *"dedicated `max_tokens=<n>` branch"*, parsed rather than copied.

    ⚠️ The value is deliberately not written here — see :func:`spec_line_references`'s note
    on why no spec-stated number appears anywhere in this module, not even in prose.
    """
    text = re.sub(r"\s+", " ", _section(context_md, "### 8.5.1 "))
    matches = sorted(set(re.findall(r"max_tokens=(\d+)", text)))
    if len(matches) != 1:
        raise ClaimError(
            f"CONTEXT.md S8.5.1 names {len(matches)} max_tokens values, not one."
        )
    return int(matches[0])


# ======================================================================================
# THE OBSERVED SIDE — derived from the checkout with `ast`. Pure over source text.
# ======================================================================================


def _parse(source: str, path: str) -> ast.Module:
    try:
        return ast.parse(source)
    except SyntaxError as exc:  # pragma: no cover - a syntax error at the pin is a finding
        raise ClaimError(f"{path} does not parse at the pin: {exc}") from exc


def _find_class(tree: ast.Module, name: str, path: str) -> ast.ClassDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise ClaimError(f"{path} defines no class {name!r} at the pin.")


def _find_method(klass: ast.ClassDef, name: str, path: str) -> ast.FunctionDef:
    for node in klass.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise ClaimError(f"{path}:{klass.name} defines no method {name!r} at the pin.")


def _signature_span(func: ast.FunctionDef) -> tuple[int, int]:
    """``(first line of ``def``, last line of the signature)``.

    The signature ends on the line before the body starts — which is how a reader counts
    it, and how `CONTEXT.md` §8.5 counts ``security_policy.py:77-82``.
    """
    return func.lineno, func.body[0].lineno - 1


def engine_check_policy(source: str, path: str) -> tuple[tuple[int, int], list[str]]:
    """``SecurityPolicyEngine.check_policy``'s signature span and argument names."""
    tree = _parse(source, path)
    func = _find_method(_find_class(tree, "SecurityPolicyEngine", path), "check_policy", path)
    args = [a.arg for a in func.args.args if a.arg != "self"]
    return _signature_span(func), args


def per_tool_callback(source: str, path: str) -> tuple[tuple[int, int], list[str]]:
    """The ``SecurityPolicy`` Protocol's ``__call__`` — the TWO-argument shape.

    ⚠️ The span runs from the **class** statement, not the ``def``, because that is what
    `CONTEXT.md` §8.5's ``security_policy.py:44-49`` names: the callback's whole
    declaration, which is what distinguishes it from the engine's method.
    """
    tree = _parse(source, path)
    klass = _find_class(tree, "SecurityPolicy", path)
    func = _find_method(klass, "__call__", path)
    args = [a.arg for a in func.args.args if a.arg != "self"]
    end = func.body[-1].end_lineno or func.body[-1].lineno
    return (klass.lineno, end), args


def deny_by_default(source: str, path: str) -> tuple[int, str, bool]:
    """The final ``return Denied(...)`` of the engine's ``check_policy``.

    Returns its line, its reason string, and **whether it is the last statement** — the
    part that makes it *deny-by-default* rather than merely present. §8.5's second reason
    for demoting CaMeL is that this branch *"denies 100% of calls"* against un-ported
    tools, so *"last"* is the load-bearing word.
    """
    tree = _parse(source, path)
    func = _find_method(_find_class(tree, "SecurityPolicyEngine", path), "check_policy", path)
    last = func.body[-1]
    if not (
        isinstance(last, ast.Return)
        and isinstance(last.value, ast.Call)
        and isinstance(last.value.func, ast.Name)
        and last.value.func.id == "Denied"
        and last.value.args
        and isinstance(last.value.args[0], ast.Constant)
    ):
        raise ClaimError(
            f"{path}: SecurityPolicyEngine.check_policy no longer ENDS in "
            f"`return Denied(<str>)`. Claim 3c is about the last branch."
        )
    return last.lineno, str(last.value.args[0].value), True


def check_policy_call_sites(source: str, path: str) -> list[tuple[int, int]]:
    """Every ``.check_policy(...)`` **call** in the interpreter, as ``(line, arity)``."""
    tree = _parse(source, path)
    sites: list[tuple[int, int]] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "check_policy"
        ):
            sites.append((node.lineno, len(node.args) + len(node.keywords)))
    return sorted(sites)


def _make_tools_pipeline(tree: ast.Module, path: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "make_tools_pipeline":
            return node
    raise ClaimError(f"{path} defines no `make_tools_pipeline` at the pin.")


def provider_dispatch(source: str, path: str) -> tuple[tuple[int, int], list[str], str, str]:
    """The provider dispatch chain: span, the provider tokens, the operator, the else.

    ⚠️ **The operator is returned rather than assumed.** §8.5.1 calls this
    *"provider-prefix dispatch"*; the code is ``if "google" in model`` — **substring
    containment over the whole model string**, not a prefix parse. The distinction does
    not change §8.5.1's conclusion (there is still no fourth provider and no ``base_url``),
    but `PROCESS.md` §9 makes third-party claims exact, so it is measured and reported.
    """
    tree = _parse(source, path)
    func = _make_tools_pipeline(tree, path)
    branch = next((n for n in func.body if isinstance(n, ast.If)), None)
    if branch is None:
        raise ClaimError(f"{path}: `make_tools_pipeline` opens with no `if` at the pin.")

    start = branch.lineno
    providers: list[str] = []
    operators: set[str] = set()
    node: ast.If | None = branch
    tail: list[ast.stmt] = []
    while node is not None:
        test = node.test
        if (
            isinstance(test, ast.Compare)
            and len(test.ops) == 1
            and isinstance(test.left, ast.Constant)
        ):
            providers.append(str(test.left.value))
            operators.add(type(test.ops[0]).__name__)
        tail = node.orelse
        node = tail[0] if len(tail) == 1 and isinstance(tail[0], ast.If) else None

    raises = [n for n in tail if isinstance(n, ast.Raise)]
    if not raises:
        raise ClaimError(
            f"{path}: the dispatch chain's final `else` does not raise. §8.5.1's claim is "
            f"that an unrecognised provider is REFUSED - if it is not, Groq's reachability "
            f"question has a different answer."
        )
    raised = raises[-1]
    end = raised.end_lineno or raised.lineno
    message = ""
    if isinstance(raised.exc, ast.Call) and raised.exc.args:
        first = raised.exc.args[0]
        if isinstance(first, ast.Constant):
            message = str(first.value)
    operator = operators.pop() if len(operators) == 1 else "|".join(sorted(operators))
    return (start, end), providers, operator, message


def supported_model_names(source: str, path: str) -> tuple[tuple[int, int], dict[str, int]]:
    """``_supported_model_names``'s span, and each base id mapped to its own line."""
    tree = _parse(source, path)
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "_supported_model_names"
        ):
            dict_node = node.value
            while isinstance(dict_node, ast.BinOp):
                dict_node = dict_node.left
            if not isinstance(dict_node, ast.Dict):
                raise ClaimError(f"{path}: `_supported_model_names` is not a dict literal.")
            ids = {
                str(k.value): k.lineno
                for k in dict_node.keys
                if isinstance(k, ast.Constant)
            }
            return (node.lineno, node.end_lineno or node.lineno), ids
    raise ClaimError(f"{path} defines no `_supported_model_names` at the pin.")


def max_tokens_branch(source: str, path: str, model_id: str) -> tuple[tuple[int, int], int]:
    """The ``if model == "google:<id>"`` branch's span and its ``max_tokens`` value."""
    tree = _parse(source, path)
    func = _make_tools_pipeline(tree, path)
    for node in ast.walk(func):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not (
            isinstance(test, ast.Compare)
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)
            and isinstance(test.comparators[0], ast.Constant)
            and model_id in str(test.comparators[0].value)
        ):
            continue
        assigns = [n for n in node.body if isinstance(n, ast.Assign)]
        if not assigns or not isinstance(assigns[0].value, ast.Constant):
            raise ClaimError(f"{path}: the {model_id} branch assigns no literal.")
        tail = node.orelse or node.body
        end = tail[-1].end_lineno or tail[-1].lineno
        return (node.lineno, end), int(assigns[0].value.value)
    raise ClaimError(
        f"{path}: no `model == \"google:{model_id}\"` branch at the pin. §8.5.1's claim "
        f"that this id has a DEDICATED max_tokens branch is what makes it the one reachable "
        f"free model."
    )


def base_url_hits(root: Path) -> list[str]:
    """§8.5.1's grep, re-run at the pin: every ``base_url`` occurrence in CaMeL's Python.

    ⚠️ **This is the corollary that decides C13's design.** No ``base_url`` means no
    OpenAI-compatible endpoint override, so Groq is unreachable — and patching one in would
    mean the project is no longer running CaMeL unmodified, which forfeits §8.5's entire
    resolution. Returned as a list so the count is a number and an empty result is
    *reported as zero* rather than as silence (`PROCESS.md` §9).
    """
    hits: list[str] = []
    for path in sorted(root.rglob("*.py")):
        if ".git" in path.parts:
            continue
        for number, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            if "base_url" in line:
                hits.append(f"{path.relative_to(root).as_posix()}:{number}:{line.strip()}")
    return hits


# ======================================================================================
# THE DIFF — spec side against observed side, one verdict per claim.
# ======================================================================================


def verify_all_claims(context_md: str, root: Path | None = None) -> list[ClaimVerdict]:
    """Re-derive every §8.5/§8.5.1 claim at the pin and diff it against the spec."""
    root = root if root is not None else vendor.vendor_root()
    refs = spec_line_references(context_md)
    sp_source = vendor.blob_text(root, vendor.SECURITY_POLICY_PATH)
    int_source = vendor.blob_text(root, vendor.INTERPRETER_PATH)
    md_source = vendor.blob_text(root, vendor.MODELS_PATH)
    verdicts: list[ClaimVerdict] = []

    # -- 3a ---------------------------------------------------------------------------
    want_bytes, want_lines = spec_interpreter_size(context_md)
    measured = vendor.interpreter_measurement(root)
    verdicts.append(
        ClaimVerdict(
            claim_id=CLAIM_IDS[0],
            what_the_spec_says=(
                f"a hand-written AST interpreter, {want_bytes:,} bytes and {want_lines:,} "
                f"lines - which is why CaMeL is a whole agent architecture and not a gate "
                f"you can drop in"
            ),
            where=vendor.INTERPRETER_PATH,
            expected=(want_bytes, want_lines),
            observed=(measured.blob_bytes, measured.lines),
            holds=(measured.blob_bytes, measured.lines) == (want_bytes, want_lines),
            note=(
                f"measured from the GIT BLOB. The working tree is "
                f"{measured.worktree_bytes} bytes here because core.autocrlf added "
                f"{measured.cr_bytes} CR bytes; blob + CR == worktree is "
                f"{measured.crlf_accounts_for_the_difference}."
            ),
        )
    )

    # -- 3b, the ENGINE's three-argument method ---------------------------------------
    span, args = engine_check_policy(sp_source, vendor.SECURITY_POLICY_PATH)
    want = refs["engine_signature"]
    verdicts.append(
        ClaimVerdict(
            claim_id=CLAIM_IDS[1],
            what_the_spec_says=(
                "the ENGINE's method is check_policy(tool_name, kwargs, dependencies)"
            ),
            where=f"{vendor.SECURITY_POLICY_PATH}:{span[0]}-{span[1]}",
            expected=(want, ["tool_name", "kwargs", "dependencies"]),
            observed=(span, args),
            holds=span == want and args == ["tool_name", "kwargs", "dependencies"],
            note="three arguments, and the spec records that a previous draft said two",
        )
    )

    # -- 3b, the interpreter passing all three ----------------------------------------
    sites = check_policy_call_sites(int_source, vendor.INTERPRETER_PATH)
    want_line = refs["interpreter_call"]
    verdicts.append(
        ClaimVerdict(
            claim_id=CLAIM_IDS[2],
            what_the_spec_says=(
                f"the interpreter passes all three at "
                f"{vendor.INTERPRETER_PATH}:{want_line[0]}"
            ),
            where=vendor.INTERPRETER_PATH,
            expected=[(want_line[0], 3)],
            observed=sites,
            holds=sites == [(want_line[0], 3)],
            note="arity counted from the call node, not from the source text",
        )
    )

    # -- 3b, the TWO-argument per-tool callback ---------------------------------------
    cb_span, cb_args = per_tool_callback(sp_source, vendor.SECURITY_POLICY_PATH)
    cb_want = refs["per_tool_callback"]
    verdicts.append(
        ClaimVerdict(
            claim_id=CLAIM_IDS[3],
            what_the_spec_says=(
                "the TWO-argument (tool_name, kwargs) shape is the PER-TOOL POLICY CALLBACK"
            ),
            where=f"{vendor.SECURITY_POLICY_PATH}:{cb_span[0]}-{cb_span[1]}",
            expected=(cb_want, ["tool_name", "kwargs"]),
            observed=(cb_span, cb_args),
            holds=cb_span == cb_want and cb_args == ["tool_name", "kwargs"],
            note="SecurityPolicy Protocol.__call__, invoked by the engine at line 95",
        )
    )

    # -- 3c ---------------------------------------------------------------------------
    line, reason, is_last = deny_by_default(sp_source, vendor.SECURITY_POLICY_PATH)
    want_reason = spec_deny_by_default_string(context_md)
    want_line_3c = refs["deny_by_default"]
    verdicts.append(
        ClaimVerdict(
            claim_id=CLAIM_IDS[4],
            what_the_spec_says=(
                "check_policy ENDS with Denied(\"No security policy matched for tool. "
                "Defaulting to denial.\") - the branch that would make a Razorpay port "
                "measure our port rather than CaMeL"
            ),
            where=f"{vendor.SECURITY_POLICY_PATH}:{line}",
            expected=(want_line_3c[0], want_reason, True),
            observed=(line, reason, is_last),
            holds=(line, reason, is_last) == (want_line_3c[0], want_reason, True),
            note="'last statement' is the load-bearing word, so it is asserted, not assumed",
        )
    )

    # -- 3d, the dispatch -------------------------------------------------------------
    d_span, providers, operator, message = provider_dispatch(md_source, vendor.MODELS_PATH)
    d_want = refs["provider_dispatch"]
    verdicts.append(
        ClaimVerdict(
            claim_id=CLAIM_IDS[5],
            what_the_spec_says=(
                "the real hard gate is provider dispatch - google / openai / anthropic, "
                "else raise ValueError('Invalid model') - and NOT the name list"
            ),
            where=f"{vendor.MODELS_PATH}:{d_span[0]}-{d_span[1]}",
            expected=(d_want, ["google", "openai", "anthropic"], "Invalid model"),
            observed=(d_span, providers, message),
            holds=(
                d_span == d_want
                and providers == ["google", "openai", "anthropic"]
                and message == "Invalid model"
            ),
            note=(
                f"the comparison operator is `{operator}` - CONTEXT.md S8.5.1 calls this "
                f"'provider-prefix dispatch' and the code is substring containment over the "
                f"whole model string. The conclusion is unchanged; the wording is not exact."
            ),
        )
    )

    # -- 3d, the name list ------------------------------------------------------------
    list_span, ids = supported_model_names(md_source, vendor.MODELS_PATH)
    model_id = spec_model_id(context_md)
    id_want = refs["gemini_id_line"]
    verdicts.append(
        ClaimVerdict(
            claim_id=CLAIM_IDS[6],
            what_the_spec_says=f"{model_id} is in _supported_model_names at models.py:40",
            where=f"{vendor.MODELS_PATH}:{ids.get(model_id)}",
            expected=id_want[0],
            observed=ids.get(model_id),
            holds=ids.get(model_id) == id_want[0],
            note=(
                f"_supported_model_names spans {list_span[0]}-{list_span[1]} and holds "
                f"{len(ids)} base ids; it is merged into AgentDojo's MODEL_NAMES, so it "
                f"feeds the 'what model are you?' injection tasks, not admission control"
            ),
        )
    )

    # -- 3d, the max_tokens branch ----------------------------------------------------
    mt_span, mt_value = max_tokens_branch(md_source, vendor.MODELS_PATH, model_id)
    mt_want = refs["max_tokens_branch"]
    verdicts.append(
        ClaimVerdict(
            claim_id=CLAIM_IDS[7],
            what_the_spec_says=f"a dedicated max_tokens={spec_max_tokens(context_md)} branch",
            where=f"{vendor.MODELS_PATH}:{mt_span[0]}-{mt_span[1]}",
            expected=(mt_want, spec_max_tokens(context_md)),
            observed=(mt_span, mt_value),
            holds=mt_span == mt_want and mt_value == spec_max_tokens(context_md),
        )
    )

    return verdicts
