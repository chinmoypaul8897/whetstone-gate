#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C8 REVIEW 1 (`07c3687f`) — THE MOAT, RE-DRIVEN BY THE REVIEWER.

`CLAUDE.md` hard rule 8: *"⚠️ **THE GATE AND THE SCORER SHARE NO CODE, AND A TEST MUST ASSERT
THAT.** … **Any logic they both need is written twice, on purpose.** … *Why this one line is
the whole moat:* in the spike, `gate.js` and `invariants.js` both called `world.js:intentKey`,
so the invariant **could not have fired unless the gate had a bug**. **That is not a result; it
is a definition.**"*

⚠️ **`gates/` DOES NOT EXIST YET — C9 writes it — so `check_roles` D1..D4 report `n/a` against
this repository (`OF-64`, `Q-094`, `INC-76`).** This file does what an `n/a` cannot: it copies
`src/` into a FRESH OS TEMP TREE, plants the `gates/` package C9 will write, and runs
`check_roles`'s **REAL** `check_gate_scorer_isolation` against the **REAL** scorer — then
drives it RED three ways.

**THE THREE REDS, and why these three:**

  1. **a gate importing the scorer** — the plain form.
  2. **a shared predicate helper both sides import** — ⚠️ **hard rule 8's OWN NAMED SPIKE
     DEFECT**, transliterated into Python. `REVIEW_C0.md` **B-02** records that D3 once passed
     on exactly this shape and that it is *"the most natural way to write it in this layout"*.
  3. **`INC-51`'s dynamic reach** — `importlib.import_module`, which **D1, D2 and D3 all PASS**
     and only **D4**, the source-text scan, catches.

⚠️ **EVERY WALK RUNS IN A SUBPROCESS WHOSE `PYTHONPATH` PUTS THE TREE UNDER TEST FIRST, THE
`env` IS PASSED TO `subprocess.run` ITSELF (`INC-69`), AND THE CHILD PRINTS THE RESOLVED
`check_roles.__file__` FROM THE PROCESS THAT DOES THE WALK (`OF-139`).** A walk that resolved
to the live repository would report a perfect moat for the wrong reason, which is `INC-64`.

    python docs/reviews/independent/c8_moat_check.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

CHILD = r'''
import json, os, sys
sys.path.insert(0, os.path.join(os.environ["WG_TREE"], "src"))
from pathlib import Path
import whetstone_gate
from whetstone_gate import check_roles as cr
out = []
for r in cr.check_gate_scorer_isolation(Path(os.environ["WG_TREE"])):
    out.append({"name": r.check, "ok": r.ok, "detail": (r.detail or "")})
print("WG_MOAT " + json.dumps({
    "package": whetstone_gate.__file__,
    "checkroles": cr.__file__,
    "results": out,
}))
'''


def run_group(tree, label):
    env = dict(os.environ)
    env["WG_TREE"] = tree
    env["PYTHONPATH"] = os.path.join(tree, "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run([sys.executable, "-c", CHILD], cwd=tree, env=env,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="backslashreplace", timeout=300)
    line = next((l for l in proc.stdout.splitlines() if l.startswith("WG_MOAT ")), None)
    if line is None:
        raise SystemExit("VOID: no output from the moat child\n%s\n%s"
                         % (proc.stdout[-1500:], proc.stderr[-1500:]))
    data = json.loads(line[len("WG_MOAT "):])
    if not (str(data["package"]).startswith(tree)
            and str(data["checkroles"]).startswith(tree)):
        raise SystemExit(
            "VOID: OF-139's guard REFUSES - the child imported the LIVE tree:\n"
            "   package    %s\n   checkroles %s" % (data["package"], data["checkroles"]))
    print("  %s" % label)
    print("     [provenance, from the walking process] %s"
          % data["checkroles"].replace(tree, "<TREE>"))
    verdicts = {}
    for r in data["results"]:
        state = "PASS" if r["ok"] is True else ("FAIL" if r["ok"] is False else "n/a")
        key = r["name"].split()[0]
        verdicts[key] = state
        detail = " ".join(r["detail"].split())
        print("     %-4s %-5s %s" % (key, state, detail[:92]))
    return verdicts


CLEAN_GATES = {
    "__init__.py": '"""arms 1, 2, 2S, 3, 4 behind one interface. C9 writes this."""\n',
    "arm1.py": ('"""arm 1 - no gate. ALLOWED only."""\n\n\n'
                'def decide(amount, cap):\n    return "ALLOWED"\n'),
    "arm4.py": ('"""arm 4 - the deterministic kernel, reimplementing its caps on purpose."""\n'
                '\n\ndef decide(amount, cap):\n'
                '    return "DENIED" if amount > cap else "ALLOWED"\n'),
}

RED_IMPORT = (
    '"""arm 4, reaching the scorer directly."""\n\n'
    'from whetstone_gate.scorer.invariants import e1_breaches\n\n\n'
    'def decide(entries, constants):\n'
    '    return "DENIED" if e1_breaches(entries, constants) else "ALLOWED"\n'
)

SHARED_HELPER = (
    '"""A predicate helper. BOTH sides import it - the spike\'s world.js:intentKey."""\n\n\n'
    'def over_cap(amount, cap):\n    return amount > cap\n'
)
RED_SHARED_GATE = (
    '"""arm 4, importing the shared predicate helper."""\n\n'
    'from whetstone_gate.shared_predicate import over_cap\n\n\n'
    'def decide(amount, cap):\n'
    '    return "DENIED" if over_cap(amount, cap) else "ALLOWED"\n'
)
RED_SHARED_SCORER = (
    '\n\n# [REVIEWER MUTANT] the other half of hard rule 8\'s own named spike defect\n'
    'from whetstone_gate.shared_predicate import over_cap  # noqa: E402,F401\n'
)

RED_DYNAMIC = (
    '"""arm 4, reaching the scorer through a CALL EXPRESSION (INC-51)."""\n\n'
    'import importlib\n\n\n'
    'def decide(entries, constants):\n'
    '    mod = importlib.import_module("whetstone_gate.scorer.invariants")\n'
    '    return "DENIED" if mod.e1_breaches(entries, constants) else "ALLOWED"\n'
)


def make_tree(label):
    root = tempfile.mkdtemp(prefix="wg_moat_%s_" % label)
    shutil.copytree(os.path.join(_REPO, "src"), os.path.join(root, "src"),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    gates = os.path.join(root, "src", "whetstone_gate", "gates")
    os.makedirs(gates, exist_ok=True)
    for name, body in CLEAN_GATES.items():
        with open(os.path.join(gates, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return root, gates


def write(path, body, mode="w"):
    with open(path, mode, encoding="utf-8", newline="\n") as fh:
        fh.write(body)


def main():
    print("C8 REVIEW 1 (`07c3687f`) - THE MOAT, RE-DRIVEN")
    print("=" * 96)
    trees = []

    root, _ = make_tree("clean")
    trees.append(root)
    print("BASELINE - a clean planted `gates/` against the REAL `scorer/`")
    base = run_group(root, "check_gate_scorer_isolation:")
    print()

    root1, g1 = make_tree("red1")
    trees.append(root1)
    write(os.path.join(g1, "arm4.py"), RED_IMPORT)
    print("RED 1 - a gate IMPORTING the scorer")
    r1 = run_group(root1, "check_gate_scorer_isolation:")
    print()

    root2, g2 = make_tree("red2")
    trees.append(root2)
    write(os.path.join(root2, "src", "whetstone_gate", "shared_predicate.py"), SHARED_HELPER)
    write(os.path.join(g2, "arm4.py"), RED_SHARED_GATE)
    write(os.path.join(root2, "src", "whetstone_gate", "scorer", "invariants.py"),
          RED_SHARED_SCORER, mode="a")
    print("RED 2 - a SHARED PREDICATE HELPER both sides import")
    print("        hard rule 8's OWN NAMED SPIKE DEFECT: `gate.js` and `invariants.js` both")
    print("        called `world.js:intentKey`, so the invariant could not have fired unless")
    print("        the gate had a bug - 'that is not a result; it is a definition'")
    r2 = run_group(root2, "check_gate_scorer_isolation:")
    print()

    root3, g3 = make_tree("red3")
    trees.append(root3)
    write(os.path.join(g3, "arm4.py"), RED_DYNAMIC)
    print("RED 3 - INC-51's DYNAMIC REACH (`importlib.import_module`)")
    print("        a call expression is not an `ast.Import` node, so D1, D2 and D3 cannot see")
    print("        the edge at all. Only D4, the source-text scan, catches it.")
    r3 = run_group(root3, "check_gate_scorer_isolation:")
    print()

    print("=" * 96)
    print("SUMMARY")
    print("=" * 96)
    keys = sorted(set(base) | set(r1) | set(r2) | set(r3))
    print("%-6s %-12s %-14s %-16s %-14s" % ("", "baseline", "RED 1 import",
                                            "RED 2 shared", "RED 3 dynamic"))
    for k in keys:
        print("%-6s %-12s %-14s %-16s %-14s" % (
            k, base.get(k, "-"), r1.get(k, "-"), r2.get(k, "-"), r3.get(k, "-")))
    print()
    ok_base = all(v == "PASS" for v in base.values())
    red1 = any(v == "FAIL" for v in r1.values())
    red2 = any(v == "FAIL" for v in r2.values())
    red3 = any(v == "FAIL" for v in r3.values())
    only_d4 = (r3.get("D4") == "FAIL"
               and all(r3.get(k) == "PASS" for k in ("D1", "D2", "D3") if k in r3))
    print("  baseline: all four PASS against the REAL scorer : %s" % ok_base)
    print("  RED 1 drives the group RED                      : %s" % red1)
    print("  RED 2 drives the group RED (the spike defect)   : %s" % red2)
    print("  RED 3 drives the group RED                      : %s" % red3)
    print("  RED 3 caught by D4 ALONE, D1-D3 green (INC-51)  : %s" % only_d4)
    for t in trees:
        shutil.rmtree(t, ignore_errors=True)
    return 0 if (ok_base and red1 and red2 and red3) else 1


if __name__ == "__main__":
    sys.exit(main())
