#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C6 REVIEW 6 — `INC-47`'s TEST, APPLIED A FOURTH TIME, ACROSS `INC-70`, `INC-71` AND `INC-72`.

SESSION-TOKEN: 7f4b0e93

`INC-47`'s test: **does any field claim more than its commits demonstrate?**  It has fired once
already, on `INC-56`'s `Systemic guardrail` (found by `REVIEW_C6_5`, the third application).
Every numeric and structural claim in the three new entries is re-derived here, from the
repository, by this session.  Nothing is cited.
"""

from __future__ import annotations

import ast
import io
import re
import subprocess
import sys
from pathlib import Path

_KEEP = []


def _ascii(s):
    try:
        w = io.TextIOWrapper(s.buffer, encoding="ascii", errors="backslashreplace",
                             line_buffering=True)
    except Exception:
        return s
    _KEEP.extend([s, w])
    return w


sys.stdout = _ascii(sys.stdout)
sys.stderr = _ascii(sys.stderr)

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

OK, BAD = 0, 0


def claim(entry, text, got, want, note=""):
    global OK, BAD
    good = got == want
    if good:
        OK += 1
    else:
        BAD += 1
    print("  %-4s %-8s %-62s got=%r want=%r %s"
          % ("ok" if good else "OVER", entry, text, got, want, note))


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=str(REPO), capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


print("=" * 78)
print("INC-47's TEST, FOURTH APPLICATION - INC-70, INC-71, INC-72")
print("=" * 78)

# ======================================================================================
# INC-70
# ======================================================================================
print("\nINC-70 - the correcting entry for INC-56's overstated `Systemic guardrail`")

inc = (REPO / "INCIDENTS.md").read_bytes().decode("utf-8")
start = inc.index("## INC-70 ")
end = inc.index("## INC-71 ")
body70 = inc[start:end]

# 1. Does it QUOTE the false sentence?
false_sentence = ("the (class, copy) matrix for claim 4's three layers plus `crossing()`'s three "
                  "boundaries **is\n> complete and a deletion in either copy meets a red test**")
claim("INC-70", "quotes INC-56's false sentence verbatim",
      "is\n> complete and a deletion in either copy meets a red test" in body70, True)
claim("INC-70", "quotes it inside an `Expectation:` block-quote",
      body70.count("> *\"What is now closed **by construction**") >= 1, True)

# 2. Does it state the measured matrix WITH A MUTANT ID PER CELL?
rows = [l for l in body70.split("\n") if l.startswith("| LAYER") or l.startswith("| the ")]
with_ids = [l for l in rows if re.search(r"`M-\w+`", l)]
claim("INC-70", "matrix rows", len(rows), 8)
claim("INC-70", "matrix rows carrying at least one mutant id", len(with_ids), 8,
      "the prompt's own requirement")

# 3. `src/` untouched across FIX 5.
claim("INC-70", "`src/` untouched across FIX 5's commits",
      git("diff", "--name-only", "e8bf194^..ae5199a", "--", "src/").strip(), "")

# 4. The AST walk: copy 1's four guards, call sites, and whether any takes a run_episode result.
tree = ast.parse((REPO / "tests/test_c6_attacker.py").read_bytes().decode("utf-8"))
GUARDS = {"_denial_findings", "_policy_findings", "_hole_findings", "_attack_list_findings"}
calls = [n for n in ast.walk(tree)
         if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in GUARDS]
claim("INC-70", "call sites of copy 1's four guards (INC-70 says 20)", len(calls), 20,
      "REVIEW_C6_5 said 23; INC-70 corrected it to 20 and MEASURED it")
run_ep = [n for n in ast.walk(tree)
          if isinstance(n, ast.Call) and (
              (isinstance(n.func, ast.Attribute) and n.func.attr == "run_episode")
              or (isinstance(n.func, ast.Name) and n.func.id == "run_episode"))]
claim("INC-70", "run_episode calls in COPY 1", len(run_ep), 1)
# Is any guard call handed something derived from a run_episode result?
arg_srcs = []
src1 = (REPO / "tests/test_c6_attacker.py").read_bytes().decode("utf-8").split("\n")
for c in calls:
    arg_srcs.append(src1[c.lineno - 1].strip()[:100])
suspicious = [a for a in arg_srcs if "result" in a or "run_episode" in a or "episode" in a]
claim("INC-70", "guard call sites naming an episode result", len(suspicious), 0,
      "every one takes a hand-assembled context")

# 5. Five _sole_layer-routed fixtures landed in 000270e, and the residue layer with them.
added = git("show", "000270e", "--", "tests/test_c6_fix_probes.py")
claim("INC-70", "`_sole_layer` calls ADDED by 000270e", len(re.findall(r"^\+.*_sole_layer\(",
      added, re.M)), 5)
claim("INC-70", "the residue layer's finding string added by 000270e",
      "unexplained AUTHORED text the spec does not mandate" in
      "\n".join(l for l in added.split("\n") if l.startswith("+")), True)
claim("INC-70", "the rulings commit e8bf194 PRECEDES the fixtures commit 000270e",
      git("merge-base", "--is-ancestor", "e8bf194", "000270e") == "" and
      subprocess.run(["git", "merge-base", "--is-ancestor", "e8bf194", "000270e"],
                     cwd=str(REPO)).returncode == 0, True)

# 6. The `Fix:` SHA is real, and no promise is made.
fix70 = re.search(r"\*\*Fix:\*\*\s*\*\*`([0-9a-f]+)`\*\*", body70)
sha = fix70.group(1) if fix70 else ""
kind = subprocess.run(["git", "cat-file", "-t", sha], cwd=str(REPO), capture_output=True,
                      text=True).stdout.strip() if sha else ""
claim("INC-70", "its `Fix:` SHA resolves as a COMMIT (no promise)", kind, "commit",
      "= %s" % sha)
claim("INC-70", "it makes NO 'a later commit will write this' promise",
      "written into this line by the commit" in body70, False)

# 7. Does the Systemic guardrail claim MORE than it can prove?
guard70 = body70[body70.index("**Systemic guardrail:**"):]
claim("INC-70", "the guardrail says PARTIAL rather than complete",
      "PARTIAL" in guard70, True)
claim("INC-70", "it names what is NOT closed, in terms",
      "What is NOT closed, stated plainly" in guard70, True)
claim("INC-70", "it does NOT repeat INC-56's word 'complete' about the matrix",
      bool(re.search(r"matrix[^.]{0,60}\bis complete\b", guard70)), False)

# ======================================================================================
# INC-71 — the Fix:-field census, re-run from scratch
# ======================================================================================
print("\nINC-71 - the `Fix:` SHA census, RE-RUN BY ME rather than cited")
fields = re.findall(r"\*\*Fix:\*\*(.*?)(?=\n\*\*|\n## |\Z)", inc, re.S)
claim("INC-71", "`Fix:` fields in INCIDENTS.md", len(fields), 69)
hexes = []
for f in fields:
    hexes += re.findall(r"`([0-9a-f]{7,40})`", f)
claim("INC-71", "backticked hex-shaped strings inside them", len(hexes), 92)
commit = noncommit = 0
kinds = {}
for h in hexes:
    k = subprocess.run(["git", "cat-file", "-t", h], cwd=str(REPO), capture_output=True,
                       text=True).stdout.strip()
    kinds.setdefault(k or "unresolved", []).append(h)
    if k == "commit":
        commit += 1
    else:
        noncommit += 1
claim("INC-71", "resolve as a COMMIT", commit, 84)
claim("INC-71", "do NOT resolve as a commit", noncommit, 8)
claim("INC-71", "of those, git BLOBs (OF-152 called them 'vendored pins')",
      len(kinds.get("blob", [])), 2, "INC-71's correction of OF-152")
tokens = set(re.findall(r"^\| `([0-9a-f]{8})` \|",
                        (REPO / "QUESTIONS.md").read_bytes().decode("utf-8"), re.M))
unresolved = kinds.get("unresolved", [])
claim("INC-71", "of those, SESSION TOKENS from QUESTIONS.md's table",
      len([h for h in unresolved if h in tokens]), 5)
claim("INC-71", "unresolved strings that are NEITHER a token NOR a git object",
      len([h for h in unresolved if h not in tokens]), 0,
      "i.e. NO FABRICATED SHA reaches any committed `Fix:` field")
print("       kinds:", {k: len(v) for k, v in kinds.items()})

# INC-71's own Fix
start71, end71 = inc.index("## INC-71 "), inc.index("## INC-72 ")
body71 = inc[start71:end71]
f71 = re.search(r"\*\*Fix:\*\*\s*\*\*`([0-9a-f]+)`\*\*", body71)
k71 = subprocess.run(["git", "cat-file", "-t", f71.group(1)], cwd=str(REPO),
                     capture_output=True, text=True).stdout.strip() if f71 else ""
claim("INC-71", "its own `Fix:` SHA resolves as a COMMIT", k71, "commit")
claim("INC-71", "its Systemic guardrail says NONE rather than claiming one",
      "NONE FROM THIS SESSION" in body71, True)

# ======================================================================================
# INC-72
# ======================================================================================
print("\nINC-72 - C6 FIX 5's own harness")
body72 = inc[inc.index("## INC-72 "):]
body72 = body72[:body72.index("\n## ")] if "\n## " in body72[10:] else body72
for field in ("**Event:**", "**Action:**", "**Expectation:**", "**Missing:**", "**Missed:**",
              "**Diagnosis:**", "**Fix:**", "**Systemic guardrail:**"):
    claim("INC-72", "carries %s" % field, field in body72, True)
for entry, body in (("INC-70", body70), ("INC-71", body71), ("INC-72", body72)):
    diag = re.search(r"\*\*Diagnosis:\*\*(.*?)\n\*\*", body, re.S)
    missed = re.search(r"\*\*Missed:\*\*(.*?)\n\*\*", body, re.S)
    claim(entry, "Diagnosis is non-empty", bool(diag and diag.group(1).strip()), True)
    claim(entry, "Missed is non-empty", bool(missed and missed.group(1).strip()), True)

print("\n" + "=" * 78)
print("INC-47's TEST, FOURTH APPLICATION: %d claims verified, %d OVERSTATED" % (OK, BAD))
print("=" * 78)
sys.exit(1 if BAD else 0)
