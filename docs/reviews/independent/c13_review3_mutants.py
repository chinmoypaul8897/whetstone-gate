#!/usr/bin/env python3
"""C13 REVIEW 3 — the mutation driver.  Session ``c09c385b``.

Every mutation is applied in a **fresh OS temp clone**, **committed inside that clone**
(REVIEW 1 records that editing without committing produced three false SURVIVORS, because the
harness reads ``git cat-file blob``), and ``whetstone_gate.__file__`` is printed so the run is
provably against the mutated copy.

The clone's ``vendor/`` holds NTFS junctions to the real trees.  Nothing in the suite writes
there — ``test_a_real_edit_to_the_vendored_tree_breaks_the_triple`` copies to ``tmp_path`` first,
verified before the junctions were made.

Usage::

    python docs/reviews/independent/c13_review3_mutants.py --clone <path> [--only ID,ID]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SRC = "src/whetstone_gate/camel_comparator"
TESTS = "tests/test_c13_camel_comparator.py"
CFG = "config/lanes.yaml"
LAW = "CONTEXT.md"

# (id, file, old, new, note).  ``old`` must occur EXACTLY ONCE or the mutant is reported
# INAPPLICABLE rather than silently applied somewhere else.
MUTANTS: list[tuple[str, str, str, str, str]] = [
    # ---------------------------------------------------------------- REVIEW 2's six survivors
    (
        "R2-OF96-N11", f"{SRC}/invocation.py",
        "PurePosixPath(root).is_absolute() or PureWindowsPath(root).is_absolute()",
        "PurePosixPath(root).is_absolute()",
        "OF-96: delete the Windows disjunct of _is_relative_literal",
    ),
    (
        "R2-OF97-N13", f"{SRC}/invocation.py",
        '{"read_text", "read_bytes", "open"}',
        '{"read_text", "read_bytes", "open", "glob"}',
        "OF-97: add glob to crashes_loudly's loud set",
    ),
    (
        "R2-OF98-N8", f"{SRC}/invocation.py",
        "len(live) != 1",
        "len(live) < 1",
        "OF-98: weaken 'exactly one reachable' to 'at least one'",
    ),
    (
        "R2-OF100-setdefault", f"{SRC}/invocation.py",
        "            found[node.name] = node",
        "            found.setdefault(node.name, node)",
        "OF-100: HEAD keeps the LAST module-level def (what Python binds). This mutation "
        "restores the setdefault REVIEW 2 found, i.e. keeping the FIRST — the defect direction.",
    ),
    (
        "R2-OF101-N14", f"{SRC}/branch_b.py",
        "TABLE_NUMBER.fullmatch",
        "TABLE_NUMBER.match",
        "OF-101: fullmatch -> match",
    ),
    (
        "R2-OF102-N6", f"{SRC}/branch_b.py",
        "if figure.table == table\n        and figure.base_model == base_model",
        "if figure.base_model == base_model",
        "OF-102: drop the table key from banking_rows",
    ),
    # ---------------------------------------------------------------- the fix's OWN new surface
    (
        "N-A-superseded", f"{SRC}/invocation.py",
        'SUPERSEDED_BRANCH_TRIGGER = "model id is still served"',
        'SUPERSEDED_BRANCH_TRIGGER = "zzz never occurs zzz"',
        "new: the superseded trigger the predicate refuses becomes unreachable",
    ),
    (
        "N-B-req-diagnosed", f"{SRC}/invocation.py",
        '"on a cause that has been diagnosed",',
        '"cause",',
        "new: weaken the diagnosis requirement to a prefix substring (criteria N-2)",
    ),
    (
        "N-C-req-harness", f"{SRC}/invocation.py",
        '"a harness defect is never branch b",',
        '"harness",',
        "new: weaken the harness-defect exclusion to a substring (criteria N-2)",
    ),
    (
        "N-D-req-protocol", f"{SRC}/invocation.py",
        '"protocol.md",',
        '"md",',
        "new: weaken the PROTOCOL.md requirement to a substring (criteria N-2)",
    ),
    (
        "N-E-drop-one-req", f"{SRC}/invocation.py",
        '    (\n        "the harness-defect exclusion",\n'
        '        "a harness defect is never branch b",\n    ),\n',
        "",
        "new: delete one whole BRANCH_B_REQUIREMENT entry",
    ),
    (
        "N-F-no-refusal", f"{SRC}/invocation.py",
        "        if SUPERSEDED_BRANCH_TRIGGER in value.lower():",
        "        if False and SUPERSEDED_BRANCH_TRIGGER in value.lower():",
        "new: the predicate stops refusing the superseded trigger (criteria J-4/N-4)",
    ),
    (
        "N-G-empty-is-pass", f"{SRC}/invocation.py",
        "        if not isinstance(value, str) or not value.strip():",
        "        if False:",
        "new: an absent/blank branch condition reads as a PASS — Q-079's actual HEAD state",
    ),
    (
        "N-H-skip-b-half", f"{SRC}/invocation.py",
        "    if not isinstance(branch_b_condition, str):\n        return problems",
        "    if True:\n        return problems",
        "new: the branch_b half of the predicate never runs (criteria N-6)",
    ),
    (
        "N-I-loader-bypass", f"{SRC}/invocation.py",
        'lanes.require("camel_comparator.branch_b_condition"),',
        'lanes.get("camel_comparator.branch_b_condition", "") if hasattr(lanes, "get") '
        'else lanes.require("camel_comparator.branch_b_condition"),',
        "new: soften the loader read away from require() (criteria N-8, hard rule 9)",
    ),
    # ---------------------------------------------------------------- the ORDERING probe (B3-i)
    (
        "P-B3-7-law", LAW,
        "**Branch B — the run does not complete, ON A CAUSE THAT HAS BEEN DIAGNOSED.**",
        "**Branch B — the run does not complete.**",
        "⚠️ THE ORDERING PROBE: amend the LAW only, leave config/ alone. Must go RED AT THE LAW.",
    ),
    # ---------------------------------------------------------------- the config reverts (B-3)
    (
        "P-B3-4-revert-a", CFG,
        'branch_a_condition: "IT RUNS:',
        'branch_a_condition: "the model id is still served AND the run completes inside the '
        '90-minute box" #',
        "revert branch_a_condition to REVIEW 2's measured string",
    ),
    (
        "P-B3-5-delete-b", CFG,
        "  branch_b_condition:",
        "  branch_b_condition_DELETED:",
        "delete the branch_b_condition key entirely (rename it out of reach)",
    ),
]

# Phrase-by-phrase deletions from config's branch_b_condition (criteria P-B3-6).
CFG_PHRASE_DELETIONS: list[tuple[str, str, str]] = [
    ("P-B3-6a", "ON A CAUSE THAT HAS BEEN DIAGNOSED AND ", "the diagnosis requirement"),
    ("P-B3-6b", "'It errored' is not a cause, and ", "'it errored' is not a cause"),
    ("P-B3-6c", "a harness defect is NEVER Branch B - ", "the harness-defect exclusion"),
    ("P-B3-6d", "RECORDED IN PROTOCOL.md BEFORE A BRANCH IS SELECTED. ", "PROTOCOL.md ordering"),
]


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def reset(clone: Path) -> None:
    # ⚠️ `git reset --hard` on a TEMP CLONE only, never on the repository, and no `git clean`
    # anywhere — CLAUDE.md §4's no-destructive-commands rule. Only tracked files are mutated,
    # so a hard reset to the ORIG tag restores the clone completely.
    run(["git", "reset", "--hard", "ORIG"], clone)


def pytest_c13(clone: Path, src: Path) -> tuple[int, int, list[str]]:
    env_prefix = [sys.executable, "-m", "pytest", TESTS, "-q", "--no-header", "-p", "no:cacheprovider"]
    proc = subprocess.run(env_prefix, cwd=clone, capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          env={**__import__("os").environ, "PYTHONPATH": str(src)})
    out = proc.stdout + proc.stderr
    m = re.search(r"(\d+) failed", out)
    failed = int(m.group(1)) if m else 0
    m = re.search(r"(\d+) passed", out)
    passed = int(m.group(1)) if m else 0
    errors = re.findall(r"(\d+) error", out)
    if errors:
        failed += int(errors[0])
    died = sorted({ln.split("::")[1].split("[")[0]
                   for ln in out.splitlines()
                   if ln.startswith(("FAILED ", "ERROR ")) and "::" in ln})
    return passed, failed, died


def apply_and_run(clone: Path, src: Path, mid: str, rel: str,
                  old: str, new: str, note: str) -> dict[str, object]:
    reset(clone)
    path = clone / rel
    text = path.read_text(encoding="utf-8")
    n = text.count(old)
    if n != 1:
        return {"id": mid, "file": rel, "note": note, "status": "INAPPLICABLE",
                "occurrences": n, "died": []}
    path.write_bytes(text.replace(old, new, 1).encode("utf-8"))
    run(["git", "add", "-A"], clone)
    run(["git", "-c", "user.email=r@x", "-c", "user.name=r", "commit", "-q", "-m",
         f"mutant {mid}"], clone)
    passed, failed, died = pytest_c13(clone, src)
    return {"id": mid, "file": rel, "note": note,
            "status": "KILLED" if failed else "SURVIVED",
            "passed": passed, "failed": failed, "died": died}


def main() -> int:
    import os

    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    clone = Path(args.clone).resolve()
    src = clone / "src"
    wanted = {s.strip() for s in args.only.split(",") if s.strip()}

    run(["git", "tag", "-f", "ORIG"], clone)

    probe = subprocess.run(
        [sys.executable, "-c", "import whetstone_gate;print(whetstone_gate.__file__)"],
        cwd=clone, capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(src)},
    ).stdout.strip()
    print(f"whetstone_gate.__file__ = {probe}")
    assert str(clone) in probe, "the run is NOT against the mutated clone — abort"

    reset(clone)
    c_pass, c_fail, c_died = pytest_c13(clone, src)
    print(f"CONTROL (unmutated, same clone): {c_pass} passed, {c_fail} failed")
    assert c_fail == 0, "a mutation run whose control is RED measures nothing"

    plan = list(MUTANTS)
    cfg_text = (clone / CFG).read_text(encoding="utf-8")
    for mid, phrase, what in CFG_PHRASE_DELETIONS:
        plan.append((mid, CFG, phrase, "", f"delete {what} from branch_b_condition"))
    del cfg_text

    results: list[dict[str, object]] = []
    for mid, rel, old, new, note in plan:
        if wanted and mid not in wanted:
            continue
        r = apply_and_run(clone, src, mid, rel, old, new, note)
        results.append(r)
        died = ", ".join(r.get("died") or []) or "-"
        print(f"{mid:22s} {str(r['status']):13s} "
              f"failed={r.get('failed', '?')!s:>3s} passed={r.get('passed', '?')!s:>3s}  {died}")
    reset(clone)

    if args.out:
        Path(args.out).write_bytes(
            json.dumps({"control": {"passed": c_pass, "failed": c_fail, "died": c_died},
                        "results": results}, indent=2).encode("utf-8"))
        print(f"[json written to {args.out}]")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
