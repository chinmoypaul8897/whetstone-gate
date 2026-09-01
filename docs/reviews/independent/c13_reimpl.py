#!/usr/bin/env python3
# ruff: noqa: E501
"""C13 REVIEW 1 — PHASE 1 REIMPLEMENTATION. Written blind, before any C13 artefact was opened.

WHAT THIS IS
------------
`docs/reviews/README.md` requires a `full` review to ship a from-scratch reimplementation, written
from `CONTEXT.md`'s text alone, importing nothing from `src/`.  C13 ships almost no logic: nearly
every sentence it produces is **a claim about somebody else's code or a published table**.  So the
reimplementation is not a re-coded algorithm.  It is this: a standalone extractor that opens every
upstream source itself and prints what is actually there, as data, so that C13's claims can be
diffed against a second, independent reading.

It imports nothing from `src/` and nothing from the vendored trees.  It never imports CaMeL or
AgentDojo (importing CaMeL executes `models.py`, which imports three model clients).  It *parses*
them — with `ast`, with `git cat-file`, and with a small stdlib HTML reader.

⚠️ ALL SIZES AND LINE COUNTS COME FROM GIT BLOBS, never from the working tree.  `core.autocrlf` is
`true` on this machine and CaMeL ships no `.gitattributes`, so a text file's on-disk size exceeds
its blob size by exactly its LF count.  A reviewer who measures the working tree "finds" a modified
file that is not modified.

REPRODUCING THE INPUTS  (a fresh OS temp directory — never inside this repository)
---------------------------------------------------------------------------------
    R=/tmp/c13rev && mkdir -p "$R"

    mkdir -p "$R/camel" && cd "$R/camel" && git init -q \
      && git remote add origin https://github.com/google-research/camel-prompt-injection.git \
      && git fetch -q --depth 1 origin f083b6b396399d3b3c7f2ddaf613a5945eaf32d8 \
      && git checkout -q --detach FETCH_HEAD

    mkdir -p "$R/agentdojo" && cd "$R/agentdojo" && git init -q \
      && git remote add origin https://github.com/ethz-spylab/agentdojo.git \
      && git fetch -q --depth 1 origin 928bbae820a89556b03de5cf818eb350cd6082d1 \
      && git checkout -q --detach FETCH_HEAD

    curl -sSL -o "$R/camel_paper_v2.html" https://arxiv.org/html/2503.18813v2

RUNNING
-------
    python docs/reviews/independent/c13_reimpl.py --root /tmp/c13rev
    python docs/reviews/independent/c13_reimpl.py --root /tmp/c13rev --json

Exit status is 0 when every claim resolved and 1 when any claim could not be derived.  A claim that
could not be derived prints `UNRESOLVED` and is counted; nothing is silently dropped (hard rule 11
applied to this script's own denominator).
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

CAMEL_SHA = "f083b6b396399d3b3c7f2ddaf613a5945eaf32d8"
AGENTDOJO_SHA = "928bbae820a89556b03de5cf818eb350cd6082d1"
PAPER_URL = "https://arxiv.org/html/2503.18813v2"

# ---------------------------------------------------------------------------
# git plumbing — the only way sizes are ever measured here
# ---------------------------------------------------------------------------


def git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=False,
        check=True,
    )
    return out.stdout.decode("utf-8", errors="replace")


def blob(repo: Path, path: str) -> str:
    """File contents AS COMMITTED — LF-only, whatever the working tree looks like."""
    return git(repo, "cat-file", "blob", f"HEAD:{path}")


def blob_bytes(repo: Path, path: str) -> int:
    return int(
        subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-s", f"HEAD:{path}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )


def tree_measure(repo: Path, prefix: str | None = None) -> tuple[int, int, list[tuple[int, str]]]:
    args = ["ls-tree", "-l", "-r", "HEAD"]
    if prefix:
        args += ["--", prefix]
    files, total, sizes = 0, 0, []
    for line in git(repo, *args).splitlines():
        if not line.strip():
            continue
        meta, name = line.split("\t", 1)
        parts = meta.split()
        if parts[1] != "blob":
            continue
        n = int(parts[3])
        files += 1
        total += n
        sizes.append((n, name))
    sizes.sort(reverse=True)
    return files, total, sizes


def grep_count(repo: Path, pattern: str, include_py_only: bool = False) -> tuple[int, list[str]]:
    args = ["grep", "-rn", pattern, "."]
    if include_py_only:
        args = ["grep", "-rn", "--include=*.py", pattern, "."]
    p = subprocess.run(args + ["--exclude-dir=.git"], cwd=str(repo), capture_output=True, text=True)
    lines = [x for x in p.stdout.splitlines() if x.strip()]
    return len(lines), lines


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def parse(repo: Path, path: str) -> tuple[ast.Module, list[str]]:
    src = blob(repo, path)
    return ast.parse(src), src.split("\n")


def find_def(tree: ast.AST, name: str, cls: str | None = None) -> ast.FunctionDef | None:
    for node in ast.walk(tree):
        if cls is not None and isinstance(node, ast.ClassDef) and node.name == cls:
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef) and sub.name == name:
                    return sub
        if cls is None and isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def find_class(tree: ast.AST, name: str) -> ast.ClassDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def sig_span(fn: ast.FunctionDef, lines: list[str]) -> tuple[int, int]:
    """Line span of the `def` header: the `def` line through the line ending in `:` before the body."""
    start = fn.lineno
    end = fn.body[0].lineno - 1
    # walk back past a docstring-less blank / comment
    while end > start and not lines[end - 1].rstrip().endswith(":"):
        end -= 1
    return start, end


# ---------------------------------------------------------------------------
# arXiv LaTeXML HTML reader — no third-party parser
# ---------------------------------------------------------------------------


def _text(fragment: str) -> str:
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def _cell(fragment: str) -> str:
    """Numeric cells carry the authoritative value in the <math alttext="..."> attribute."""
    m = re.search(r'alttext="([^"]*)"', fragment)
    if m:
        return html.unescape(m.group(1))
    return _text(fragment)


class Paper:
    def __init__(self, path: Path):
        raw = path.read_bytes()
        self.sha256 = hashlib.sha256(raw).hexdigest()
        self.nbytes = len(raw)
        self.s = raw.decode("utf-8", errors="replace")
        self.appendices = self._appendices()

    def _appendices(self) -> dict[str, str]:
        out = {}
        for m in re.finditer(r'<h2 class="ltx_title ltx_title_appendix"[^>]*>(.*?)</h2>', self.s, re.S):
            j = self.s.rfind("<section", 0, m.start())
            sid = re.search(r'id="([^"]+)"', self.s[j : j + 200])
            if sid:
                out[sid.group(1)] = _text(m.group(1))
        return out

    def table(self, number: int) -> dict:
        """Return caption, enclosing figure id, appendix, and every row, for `Table <number>`."""
        for m in re.finditer(r'<figure id="([^"]+)"[^>]*>', self.s):
            fid = m.group(1)
            k = self.s.find("</figure>", m.end())
            seg = self.s[m.start() : k]
            cap_m = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", seg, re.S)
            if not cap_m:
                continue
            cap = _text(cap_m.group(1))
            if not re.match(rf"Table\s*{number}\b", cap):
                continue
            rows = []
            # LaTeXML emits tables either as <span class="ltx_tr">/<span class="ltx_td">
            # or as real <tr>/<td>. Handle both; the paper uses both forms.
            for tr in re.finditer(
                r'<span id="[^"]*" class="ltx_tr">(.*?)(?=<span id="[^"]*" class="ltx_tr">|$)', seg, re.S
            ):
                cells = re.findall(
                    r'<span id="[^"]*" class="ltx_td[^"]*">(.*?)</span>\s*'
                    r'(?=<span id="[^"]*" class="ltx_td|</span>|$)',
                    tr.group(1),
                    re.S,
                )
                rows.append([_cell(c) for c in cells])
            if not any(any(c for c in r) for r in rows):
                rows = [
                    [_cell(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
                    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", seg, re.S)
                ]
            appendix_id = fid.split(".")[0]
            return {
                "figure_id": fid,
                "caption": cap,
                "appendix_section_id": appendix_id,
                "appendix": self.appendices.get(appendix_id, "NOT-AN-APPENDIX (main body)"),
                "rows": rows,
            }
        return {}

    def sentences_naming(self, needle: str, window: int = 420) -> list[str]:
        flat = _text(self.s)
        return [flat[max(0, m.start() - window) : m.start() + window] for m in re.finditer(re.escape(needle), flat)]


def table2_block(tbl: dict, model_label: str) -> dict:
    """Table 2/3 group a model over three rows: Native / CaMeL / Difference. Return that block."""
    hdr = tbl["rows"][0]
    cols = [c for c in hdr if c]
    out: dict[str, dict[str, str]] = {}
    rows = tbl["rows"]
    for i, r in enumerate(rows):
        if r and r[0] == model_label:
            # the model row itself carries Method + values; the two following rows carry CaMeL, Difference
            out["Native Tool Calling API"] = dict(zip(cols, r[2:], strict=False))
            for label, j in (("CaMeL", i + 1), ("Difference", i + 2)):
                if j < len(rows) and rows[j] and rows[j][0] == label:
                    out[label] = dict(zip(cols, rows[j][1:], strict=False))
            break
    return out


def named_row(tbl: dict, label: str) -> dict[str, str]:
    hdr = [c for c in tbl["rows"][0] if c]
    for r in tbl["rows"]:
        if r and r[0] == label:
            return dict(zip(hdr, r[1:], strict=False))
    return {}


# ---------------------------------------------------------------------------
# the claims
# ---------------------------------------------------------------------------


class Claims:
    def __init__(self):
        self.rows: list[dict] = []

    def add(self, n: int, title: str, value, note: str = "") -> None:
        self.rows.append({"n": n, "title": title, "value": value, "note": note})

    @property
    def unresolved(self) -> list[dict]:
        return [r for r in self.rows if r["value"] in (None, {}, [], "UNRESOLVED")]


def derive(root: Path) -> Claims:
    camel = root / "camel"
    dojo = root / "agentdojo"
    paper = Paper(root / "camel_paper_v2.html")
    c = Claims()

    # -- 1 -----------------------------------------------------------------
    files, total, biggest = tree_measure(camel)
    c.add(
        1,
        "CaMeL: SHA resolves, tree clean, diff empty, blob-measured size",
        {
            "rev_parse_HEAD": git(camel, "rev-parse", "HEAD").strip(),
            "pin_expected": CAMEL_SHA,
            "matches_pin": git(camel, "rev-parse", "HEAD").strip() == CAMEL_SHA,
            "status_porcelain": git(camel, "status", "--porcelain").strip(),
            "status_empty": git(camel, "status", "--porcelain").strip() == "",
            "diff_vs_pin_bytes": len(git(camel, "diff", CAMEL_SHA)),
            "tracked_files": files,
            "tracked_bytes_from_blobs": total,
            "largest_three": biggest[:3],
            "commit_date": git(camel, "log", "-1", "--format=%cI", "HEAD").strip(),
            "ls_remote_HEAD": subprocess.run(
                ["git", "ls-remote", "https://github.com/google-research/camel-prompt-injection.git", "HEAD"],
                capture_output=True,
                text=True,
            ).stdout.split()[0],
        },
    )

    # -- 2 -----------------------------------------------------------------
    ad_files, ad_total, ad_biggest = tree_measure(dojo)
    runs_files, runs_total, _ = tree_measure(dojo, "runs")
    camel_pyproject = blob(camel, "pyproject.toml").split("\n")
    camel_lock = blob(camel, "uv.lock").split("\n")
    dep_line = next((i + 1, ln.strip()) for i, ln in enumerate(camel_pyproject) if "agentdojo" in ln)
    lock_i = next(i for i, ln in enumerate(camel_lock) if ln.strip() == 'name = "agentdojo"')
    ls_remote = subprocess.run(
        ["git", "ls-remote", "https://github.com/ethz-spylab/agentdojo.git", "refs/tags/v0.1.34", "refs/heads/main"],
        capture_output=True,
        text=True,
    ).stdout
    tag_sha = next((x.split()[0] for x in ls_remote.splitlines() if "refs/tags/v0.1.34" in x), None)
    main_sha = next((x.split()[0] for x in ls_remote.splitlines() if "refs/heads/main" in x), None)
    dojo_ver = [(i + 1, ln) for i, ln in enumerate(blob(dojo, "pyproject.toml").split("\n")) if ln.startswith("version")]
    c.add(
        2,
        "AgentDojo SHA — AND WHERE THE PIN COMES FROM (a pin chosen by a session is not a pin)",
        {
            "rev_parse_HEAD": git(dojo, "rev-parse", "HEAD").strip(),
            "pin_expected": AGENTDOJO_SHA,
            "matches_pin": git(dojo, "rev-parse", "HEAD").strip() == AGENTDOJO_SHA,
            "status_empty": git(dojo, "status", "--porcelain").strip() == "",
            "diff_vs_pin_bytes": len(git(dojo, "diff", AGENTDOJO_SHA)),
            "camel_pyproject_declares": {"line": dep_line[0], "text": dep_line[1]},
            "camel_uv_lock_resolves": {
                "lines": f"{lock_i + 1}-{lock_i + 3}",
                "text": [camel_lock[lock_i], camel_lock[lock_i + 1], camel_lock[lock_i + 2]],
            },
            "refs_tags_v0_1_34": tag_sha,
            "refs_heads_main": main_sha,
            "pin_is_the_tag": tag_sha == AGENTDOJO_SHA,
            "checked_out_tree_version_line": dojo_ver,
            "tracked_files": ad_files,
            "tracked_bytes_from_blobs": ad_total,
            "runs_files": runs_files,
            "runs_bytes": runs_total,
            "runs_share_pct": round(100.0 * runs_total / ad_total, 2),
            "largest_three": ad_biggest[:3],
        },
    )

    # -- 3 -----------------------------------------------------------------
    n_all, hits_all = grep_count(camel, "base_url")
    n_py, hits_py = grep_count(camel, "base_url", include_py_only=True)
    c.add(
        3,
        "grep -rn base_url over the WHOLE CaMeL tree — the COUNT, as a number",
        {"count_all_files": n_all, "count_py_only": n_py, "hits": hits_all + hits_py},
    )

    # -- 4 -----------------------------------------------------------------
    interp_src = blob(camel, "src/camel/interpreter/interpreter.py")
    c.add(
        4,
        "interpreter.py bytes AND lines, from the blob",
        {
            "blob_bytes": blob_bytes(camel, "src/camel/interpreter/interpreter.py"),
            "blob_lines_LF": interp_src.count("\n"),
            "worktree_bytes_on_this_machine": (camel / "src/camel/interpreter/interpreter.py").stat().st_size,
            "crlf_delta_explained": blob_bytes(camel, "src/camel/interpreter/interpreter.py")
            + interp_src.count("\n")
            == (camel / "src/camel/interpreter/interpreter.py").stat().st_size,
        },
    )

    # -- 5, 7, 8 -----------------------------------------------------------
    sp_tree, sp_lines = parse(camel, "src/camel/security_policy.py")
    engine_fn = find_def(sp_tree, "check_policy", cls="SecurityPolicyEngine")
    proto_cls = find_class(sp_tree, "SecurityPolicy")
    proto_call = find_def(sp_tree, "__call__", cls="SecurityPolicy")
    assert engine_fn and proto_cls and proto_call
    e_start, e_end = sig_span(engine_fn, sp_lines)
    p_start, p_end = proto_call.lineno, proto_call.body[0].lineno
    c.add(
        5,
        "SecurityPolicyEngine.check_policy signature, arg names, line span",
        {
            "arg_names": [a.arg for a in engine_fn.args.args],
            "arity_excluding_self": len(engine_fn.args.args) - 1,
            "def_header_span": f"{e_start}-{e_end}",
            "body_last_line": engine_fn.body[-1].end_lineno,
        },
    )
    c.add(
        7,
        "the per-tool SecurityPolicy callback signature, arg names, line span",
        {
            "class": proto_cls.name,
            "class_lineno": proto_cls.lineno,
            "method": "__call__",
            "arg_names": [a.arg for a in proto_call.args.args],
            "arity_excluding_self": len(proto_call.args.args) - 1,
            "span_class_through_body": f"{proto_cls.lineno}-{p_end}",
            "def_header_span": f"{p_start}-{p_end}",
        },
    )
    last = engine_fn.body[-1]
    deny_lines = [
        (n.lineno, ast.unparse(n))
        for n in ast.walk(engine_fn)
        if isinstance(n, ast.Return)
        and isinstance(n.value, ast.Call)
        and getattr(n.value.func, "id", "") == "Denied"
        and n.value.args
        and isinstance(n.value.args[0], ast.Constant)
    ]
    default_deny = [(ln, s) for ln, s in deny_lines if "No security policy matched" in s]
    c.add(
        8,
        "the deny-by-default return: line, exact string, AND WHETHER IT IS THE LAST STATEMENT",
        {
            "line": default_deny[0][0] if default_deny else None,
            "exact_string": "No security policy matched for tool. Defaulting to denial.",
            "source_line_verbatim": sp_lines[default_deny[0][0] - 1] if default_deny else None,
            "is_last_statement_of_method": bool(default_deny) and last.lineno == default_deny[0][0],
            "method_body_statement_count": len(engine_fn.body),
            "PRESENT_vs_TERMINATING": "both true — it is present AND it is body[-1]"
            if default_deny and last.lineno == default_deny[0][0]
            else "differs",
        },
    )

    # -- 6 -----------------------------------------------------------------
    interp_tree, _ = parse(camel, "src/camel/interpreter/interpreter.py")
    call_sites = [
        n
        for n in ast.walk(interp_tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "check_policy"
    ]
    tree_call_sites, tree_hits = grep_count(camel, "check_policy", include_py_only=True)
    c.add(
        6,
        "the interpreter's call site: line, ARITY FROM THE AST, and whether it is the only one",
        {
            "call_sites_in_interpreter": [
                {
                    "line": n.lineno,
                    "positional_arity": len(n.args),
                    "keyword_arity": len(n.keywords),
                    "receiver": ast.unparse(n.func.value),
                    "args_unparsed": [ast.unparse(a) for a in n.args],
                }
                for n in call_sites
            ],
            "is_only_call_site_in_interpreter": len(call_sites) == 1,
            "all_check_policy_grep_hits_tree_wide": tree_hits,
            "grep_hits_that_are_DEFINITIONS_not_calls": [h for h in tree_hits if "def check_policy" in h],
        },
    )

    # -- 9 -----------------------------------------------------------------
    models_tree, models_lines = parse(camel, "src/camel/models.py")
    mk = find_def(models_tree, "make_tools_pipeline")
    assert mk
    dispatch = mk.body[0]
    assert isinstance(dispatch, ast.If)
    conds, node = [], dispatch
    while isinstance(node, ast.If):
        conds.append({"line": node.test.lineno, "src": ast.unparse(node.test)})
        node = node.orelse[0] if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If) else None
    # the terminal else
    tail = dispatch
    while isinstance(tail.orelse[0] if tail.orelse else None, ast.If):
        tail = tail.orelse[0]
    raise_stmt = [n for n in ast.walk(dispatch) if isinstance(n, ast.Raise)]
    c.add(
        9,
        "provider dispatch: span, providers, error message, and THE OPERATOR — `in` or a prefix parse?",
        {
            "span": f"{dispatch.lineno}-{raise_stmt[0].end_lineno if raise_stmt else dispatch.end_lineno}",
            "conditions": conds,
            "operator": "SUBSTRING CONTAINMENT (`\"google\" in model`), NOT a prefix parse"
            if all(isinstance(ast.parse(x["src"], mode="eval").body, ast.Compare) for x in conds)
            and all("in " in x["src"] for x in conds)
            else "SEE conditions",
            "providers_in_order": [re.findall(r"'([^']+)'", x["src"]) for x in conds],
            "error_message": ast.unparse(raise_stmt[0]) if raise_stmt else None,
            "would_suffixed_string_dispatch": "google" in "google:gemini-2.0-flash-lite-001+camel+secpol",
            "model_id_handed_to_client": "google:gemini-2.0-flash-lite-001+camel+secpol".split(":")[1],
            "line_that_computes_it": next(
                (i + 1, models_lines[i])
                for i, ln in enumerate(models_lines)
                if "GoogleLLM(model.split" in ln and not ln.lstrip().startswith("#")
            ),
        },
    )

    # -- 10 ----------------------------------------------------------------
    supported = [(i + 1, ln) for i, ln in enumerate(models_lines) if "gemini-2.0-flash-lite-001" in ln]
    sup_assign = next(
        n
        for n in models_tree.body
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "_supported_model_names"
    )
    oai = next(
        n for n in models_tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "_oai_thinking_models"
    )
    efforts = next(
        n for n in models_tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "_thinking_efforts"
    )
    c.add(
        10,
        "gemini-2.0-flash-lite-001's line in _supported_model_names",
        {
            "lines_mentioning_it": supported,
            "_supported_model_names_span": f"{sup_assign.lineno}-{sup_assign.end_lineno}",
            "base_ids_literally_listed": len(sup_assign.value.left.keys)
            if isinstance(sup_assign.value, ast.BinOp)
            else len(sup_assign.value.keys),
            "o_series_models": len(oai.value.keys),
            "thinking_efforts": len(efforts.value.elts),
            "merged_total": (
                len(sup_assign.value.left.keys) if isinstance(sup_assign.value, ast.BinOp) else 0
            )
            + len(oai.value.keys) * len(efforts.value.elts),
        },
    )

    # -- 11 ----------------------------------------------------------------
    maxtok = [
        n
        for n in ast.walk(mk)
        if isinstance(n, ast.If)
        and isinstance(n.test, ast.Compare)
        and "gemini-2.0-flash-lite-001" in ast.unparse(n.test)
    ]
    c.add(
        11,
        "the max_tokens branch: span and value",
        {
            "span": f"{maxtok[0].lineno}-{maxtok[0].orelse[-1].end_lineno}" if maxtok else None,
            "test": ast.unparse(maxtok[0].test) if maxtok else None,
            "if_value": ast.unparse(maxtok[0].body[0]) if maxtok else None,
            "else_value": ast.unparse(maxtok[0].orelse[0]) if maxtok else None,
        },
    )

    # -- 12 ----------------------------------------------------------------
    emits = []
    for n in ast.walk(mk):
        if isinstance(n, ast.Assign) and "camel+secpol" in ast.unparse(n):
            emits.append({"line": n.lineno, "src": ast.unparse(n)})
    replay_branch = [
        n
        for n in ast.walk(mk)
        if isinstance(n, ast.If) and "replay_with_policies" in ast.unparse(n.test)
    ]
    rb = replay_branch[0] if replay_branch else None
    c.add(
        12,
        "models.py:188 — is `+camel+secpol` EMITTED there, and only on the replay branch?",
        {
            "emission_sites": emits,
            "emitted_at_188": any(e["line"] == 188 for e in emits),
            "replay_branch_span": f"{rb.lineno}-{rb.body[-1].end_lineno}" if rb else None,
            "all_emissions_inside_replay_branch": bool(rb)
            and all(rb.lineno <= e["line"] <= rb.body[-1].end_lineno for e in emits),
            "suffix_LIST_line_not_an_emission": [
                (i + 1, ln) for i, ln in enumerate(models_lines) if ln.startswith("suffixes")
            ],
        },
    )

    # -- 13 ----------------------------------------------------------------
    suff = next(n for n in models_tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "suffixes")
    camel_names = next(
        n for n in models_tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "CAMEL_MODEL_NAMES"
    )
    merge = [
        n
        for n in ast.walk(models_tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == "update"
        and "MODEL_NAMES" in ast.unparse(n.func.value)
    ]
    c.add(
        13,
        "the suffix list and the MODEL_NAMES merge: lines, and what merging implies",
        {
            "suffixes_line": suff.lineno,
            "suffixes": [ast.literal_eval(e) for e in suff.value.elts],
            "CAMEL_MODEL_NAMES_line": camel_names.lineno,
            "CAMEL_MODEL_NAMES_src": ast.unparse(camel_names),
            "merge_line": merge[0].lineno if merge else None,
            "merge_src": ast.unparse(merge[0]) if merge else None,
            "merge_target_is_agentdojo": "from agentdojo.models import MODEL_NAMES"
            in blob(camel, "src/camel/models.py"),
            "implication": (
                "the suffixed strings are keys in AgentDojo's model-NAME lookup, which feeds its "
                "'what model are you?' injection tasks — they are pipeline names, not --model inputs"
            ),
        },
    )

    # -- 14 ----------------------------------------------------------------
    main_tree, main_lines = parse(camel, "main.py")
    main_fn = find_def(main_tree, "main")
    doc_node = main_fn.body[0]
    doc_first = doc_node.lineno  # line of the opening """ of main()'s docstring
    doc_last = doc_node.end_lineno
    doc_lines = [
        (i + 1, ln)
        for i, ln in enumerate(main_lines)
        if "replay_with_policies:" in ln and doc_first <= i + 1 <= doc_last
    ]
    start = doc_lines[0][0] if doc_lines else None
    c.add(
        14,
        "main.py's --replay-with-policies docstring, verbatim",
        {
            "lines": f"{start}-{start + 1}" if start else None,
            "verbatim": "\n".join(main_lines[start - 1 : start + 1]) if start else None,
            "cli_library": [(i + 1, ln) for i, ln in enumerate(main_lines) if "cyclopts" in ln],
            "param_names": [a.arg for a in main_fn.args.args],
            "logdir_line": [(i + 1, ln) for i, ln in enumerate(main_lines) if "logdir" in ln and "=" in ln],
        },
    )

    # -- 15 ----------------------------------------------------------------
    rp_tree, rp_lines = parse(camel, "src/camel/pipeline_elements/replay_privileged_llm.py")
    path_sites = []
    for n in ast.walk(rp_tree):
        if isinstance(n, ast.Assign) and 'Path(' in ast.unparse(n) and "logs" in ast.unparse(n):
            owner = None
            for f in ast.walk(rp_tree):
                if isinstance(f, ast.FunctionDef) and f.lineno <= n.lineno <= f.end_lineno:
                    if owner is None or f.lineno > owner.lineno:
                        owner = f
            path_sites.append(
                {
                    "function": owner.name if owner else None,
                    "function_span": f"{owner.lineno}-{owner.end_lineno}" if owner else None,
                    "assign_span": f"{n.lineno}-{n.end_lineno}",
                    "expr": ast.unparse(n),
                }
            )
    # who calls whom, to decide which path the two-pass protocol actually walks
    callers: dict[str, list[int]] = {}
    for n in ast.walk(rp_tree):
        if isinstance(n, ast.Call) and getattr(n.func, "id", "") in {
            "replay_task",
            "replay_user_task",
            "replay_suite",
            "replay_benchmark",
        }:
            callers.setdefault(n.func.id, []).append(n.lineno)
    c.add(
        15,
        "the replayer's log path construction: file:line, and what it reads",
        {
            "log_path_constructions": path_sites,
            "internal_callers": callers,
            "reachable_from_main_py": (
                "main.py -> make_tools_pipeline -> PrivilegedLLMReplayer(models.py:179) -> "
                "PrivilegedLLMReplayer.query -> replay_task  => the LIVE path is the one inside replay_task"
            ),
            "dead_wrt_main_py": [
                p["function"] for p in path_sites if p["function"] in {"replay_user_task", "replay_suite"}
            ],
            "pipeline_name_handed_in": [
                (i + 1, ln) for i, ln in enumerate(models_lines) if "PrivilegedLLMReplayer(" in ln
            ],
            "relative_not_absolute": all("Path('logs')" in p["expr"] or 'Path("logs")' in p["expr"] for p in path_sites),
        },
    )

    # -- 16, 17, 18, 19, 20, 23 -------------------------------------------
    t2, t4, t5, t6, t7 = (paper.table(n) for n in (2, 4, 5, 6, 7))
    o3 = table2_block(t2, "o3 High")
    c.add(
        16,
        "Table 2, Appendix B, o3 High, banking AND Overall: all four numbers, both rows",
        {
            "figure_id": t2["figure_id"],
            "appendix": t2["appendix"],
            "caption": t2["caption"],
            "o3_High": o3,
            "url": PAPER_URL,
            "sha256": paper.sha256,
            "bytes": paper.nbytes,
        },
    )
    c.add(
        23,
        "the paper's own Difference row for o3 High banking",
        {"Difference": o3.get("Difference", {})},
    )
    c.add(
        17,
        "Table 5 banking: CaMeL and undefended",
        {
            "figure_id": t5["figure_id"],
            "appendix": t5["appendix"],
            "caption": t5["caption"],
            "CaMeL": named_row(t5, "CaMeL"),
            "Undefended model": named_row(t5, "Undefended model"),
        },
    )
    c.add(
        18,
        "Table 6 banking: CaMeL and undefended",
        {
            "figure_id": t6["figure_id"],
            "appendix": t6["appendix"],
            "caption": t6["caption"],
            "CaMeL": named_row(t6, "CaMeL"),
            "Undefended model": named_row(t6, "Undefended model"),
        },
    )
    c.add(
        19,
        "Table 7: CaMeL and CaMeL-no-policies, Overall and banking",
        {
            "figure_id": t7["figure_id"],
            "appendix": t7["appendix"],
            "caption": t7["caption"],
            "CaMeL": named_row(t7, "CaMeL"),
            "CaMeL (no policies)": named_row(t7, "CaMeL (no policies)"),
        },
    )
    base_model_sentences = [s for s in paper.sentences_naming("Claude 3.5 Sonnet") if "defen" in s.lower()]
    fig11 = [
        _text(m.group(1))
        for m in re.finditer(r"<figcaption[^>]*>(.*?)</figcaption>", paper.s, re.S)
        if _text(m.group(1)).startswith("Figure 11")
    ]
    c.add(
        20,
        "WHAT TABLES 5-7 ARE. Their appendix, their caption, THEIR BASE MODEL",
        {
            "appendix_section_ids": {5: t5["appendix_section_id"], 6: t6["appendix_section_id"], 7: t7["appendix_section_id"]},
            "appendix": {5: t5["appendix"], 6: t6["appendix"], 7: t7["appendix"]},
            "captions": {5: t5["caption"], 6: t6["caption"], 7: t7["caption"]},
            "figure_11_caption": fig11,
            "base_model_evidence": base_model_sentences[:3],
            "table_2_appendix_for_contrast": t2["appendix"],
        },
    )

    # -- extra: Table 4, because P2's shape is model-dependent --------------
    c.add(
        25,
        "EXTRA (not in the prompt's list, derived because P2 depends on it): Table 4, Appendix B",
        {
            "figure_id": t4["figure_id"],
            "appendix": t4["appendix"],
            "caption": t4["caption"],
            "rows": t4["rows"],
        },
    )

    # -- 21 ----------------------------------------------------------------
    it6 = {}
    for v in ("v1", "v1_2"):
        path = f"src/agentdojo/default_suites/{v}/banking/injection_tasks.py"
        tree, lines = parse(dojo, path)
        cls = find_class(tree, "InjectionTask6")
        sec = find_def(tree, "security", cls="InjectionTask6")
        goal = next(
            (n for n in cls.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "GOAL"), None
        )
        it6[v] = {
            "file": path,
            "class_lineno": cls.lineno,
            "security_span": f"{sec.lineno}-{sec.end_lineno}",
            "security_verbatim": "\n".join(lines[sec.lineno - 1 : sec.end_lineno]),
            "scoring_expression": ast.unparse(sec.body[-1]),
            "GOAL_src": ast.unparse(goal) if goal else None,
        }
    live = [(i + 1, ln) for i, ln in enumerate(main_lines) if "get_suite(" in ln]
    c.add(
        21,
        "InjectionTask6 in AgentDojo at the pinned version: file:line and the SCORING EXPRESSION",
        {
            "copies": it6,
            "v1_and_v1_2_security_identical": it6["v1"]["security_verbatim"] == it6["v1_2"]["security_verbatim"],
            "v1_and_v1_2_GOAL_identical": it6["v1"]["GOAL_src"] == it6["v1_2"]["GOAL_src"],
            "suite_version_camel_loads": live,
            "therefore_live_copy": "v1_2 (main.py calls get_suite(\"v1.2\", ...))",
        },
    )

    # -- extra: the no-conserved-resource claim ----------------------------
    bc_tree, bc_lines = parse(dojo, "src/agentdojo/default_suites/v1/tools/banking_client.py")
    send = find_def(bc_tree, "send_money")
    bal = [(i + 1, ln.strip()) for i, ln in enumerate(bc_lines) if "balance" in ln]
    c.add(
        26,
        "EXTRA: CONTEXT.md §11.2's claim that send_money never debits account.balance",
        {
            "send_money_span": f"{send.lineno}-{send.end_lineno}",
            "send_money_touches_balance": "balance" in "\n".join(bc_lines[send.lineno - 1 : send.end_lineno]),
            "every_balance_line": bal,
        },
    )

    # -- 22 ----------------------------------------------------------------
    c.add(
        22,
        "P1, P2, P3 as CONTEXT.md §8.5.2 states them, character for character",
        "DERIVED IN THE REVIEW PROSE — this script reads upstream sources, not the repository under review",
        note="see docs/reviews/REVIEW_13_1.md §Claim 22 for the character-for-character transcription",
    )

    # -- 24 ----------------------------------------------------------------
    c.add(
        24,
        "does ANY figure this project publishes lack table/appendix/base-model/row",
        "ASSESSED IN PHASE 2 against the shipped artefacts; the upstream ground truth for the four "
        "fields is claims 16-20 above",
    )

    return c


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, type=Path, help="fresh temp dir holding camel/, agentdojo/, camel_paper_v2.html")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    c = derive(a.root)
    if a.json:
        print(json.dumps(c.rows, indent=2, default=str))
    else:
        for r in sorted(c.rows, key=lambda x: x["n"]):
            print("=" * 100)
            print(f"CLAIM {r['n']:>2} — {r['title']}")
            if r["note"]:
                print(f"  note: {r['note']}")
            print(json.dumps(r["value"], indent=2, default=str))
    print("=" * 100)
    print(f"claims derived: {len(c.rows)}   unresolved: {len(c.unresolved)}")
    return 1 if c.unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
