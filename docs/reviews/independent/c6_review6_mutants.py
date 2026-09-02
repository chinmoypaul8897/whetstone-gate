#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C6 REVIEW 6 — PHASE 2. The mutation harness.

SESSION-TOKEN: 7f4b0e93

⚠️ THE FOUR RULES THIS HARNESS IS BUILT AROUND, EVERY ONE OF THEM EARNED BY AN INCIDENT:

  INC-69 — THE CLONE ENVIRONMENT IS PASSED TO `subprocess.run` ITSELF, and the provenance
           print rides in the SAME subprocess as the measurement.  INC-69's harness built an
           env, never passed it, ran every suite against the LIVE repository, and reported
           three mutants SURVIVED while four provenance lines printed True - because the
           probe ran in a DIFFERENT SUBPROCESS from the measurement.
  OF-159 — A POSITIVE CONTROL RIDES IN EVERY SLICE.  This project has negative controls
           everywhere and positive controls nowhere.  A slice whose positive control SURVIVES
           is VOID and nothing from it is reported.
  OF-139 — `tests/test_repo_invariants.py::test_the_package_under_test_is_the_tree_under_test`
           runs in every measurement, so a clone that silently imported the real tree fails
           loudly instead of reporting every mutant SURVIVED.
  INC-17 / REVIEW 4's inverse — RESTORE BY WRITING THE ORIGINAL BYTES BACK, never by
           `git checkout` from a HEAD that may already hold the mutation, and verify by
           SHA-256.  A run whose POST-RESTORE CONTROL is not green is VOID.

Usage:  python c6_review6_mutants.py <slice-name>
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

_KEEP = []


def _ascii(stream):
    try:
        w = io.TextIOWrapper(stream.buffer, encoding="ascii", errors="backslashreplace",
                             line_buffering=True)
    except Exception:
        return stream
    _KEEP.extend([stream, w])
    return w


sys.stdout = _ascii(sys.stdout)
sys.stderr = _ascii(sys.stderr)

SCRATCH = Path(
    "C:/Users/chinm/AppData/Local/Temp/claude/"
    "c--Users-chinm-whetstone-gate/c244f5e3-c03a-4a05-87c0-bd560ab92bde/scratchpad/c6r6"
)
PYTHON = "C:/Users/chinm/whetstone-gate/.venv/Scripts/python.exe"
SUITE = [
    "tests/test_c6_attacker.py",
    "tests/test_c6_fix_probes.py",
    "tests/test_c6_review_probes.py",
    "tests/test_repo_invariants.py::test_the_package_under_test_is_the_tree_under_test",
]
CONTROL_TOTAL = 136  # measured: 135 C6 tests + the OF-139 provenance guard

COPY1 = "tests/test_c6_attacker.py"
COPY2 = "tests/test_c6_fix_probes.py"
CTXPY = "src/whetstone_gate/attacker/context.py"
LOOPPY = "src/whetstone_gate/attacker/loop.py"
ESTPY = "src/whetstone_gate/attacker/estimate.py"
CORPPY = "src/whetstone_gate/attacker/corpus.py"

# ⚠️ THE POSITIVE CONTROL (OF-159).  It changes the bytes of EVERY rendered summary, so it
# cannot fail to be visible to a suite that measures the summary at all.  If this SURVIVES,
# the slice measured nothing and is VOID.
POSITIVE_CONTROL = dict(
    id="N-PC",
    op="POSITIVE CONTROL - the summary's JSON separators widened; every summary's bytes move",
    file=CTXPY,
    old='return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)',
    new='return json.dumps(payload, separators=(", ", ": "), ensure_ascii=False)',
    must="KILLED",
    op_class="control",
)


# ⚠️ THE SECOND POSITIVE CONTROL, AND OF-159 ASKS FOR IT BY NAME.  N-PC lives in `src/`, so
# it proves the clone's SOURCE is the one under test; it says nothing about whose TEST FILE
# ran.  This one is a bare `assert False` inside COPY 2's own helper, so a slice in which it
# survives was running somebody else's tests.  OF-159: "CTRL-LIVE, a bare `assert False`
# inside the new fixture, which proves the clone's TEST file is the one being run".
POSITIVE_CONTROL_2 = dict(
    id="N-PC2",
    op="POSITIVE CONTROL 2 (OF-159's CTRL-LIVE) - a bare `assert False` in COPY 2's own helper",
    file=COPY2,
    old='    assert len(clauses) == 7, f"expected 7 clauses P1..P7, parsed {len(clauses)}"\n'
        "    return generic, _probe_note(), clauses",
    new='    assert False, "POSITIVE CONTROL 2 - the clone TEST file is the one running"\n'
        "    return generic, _probe_note(), clauses",
    must="KILLED",
    op_class="control",
)


# ======================================================================================
# THE MUTANTS
# ======================================================================================
def mutants():
    M = []

    def add(**kw):
        kw.setdefault("must", None)
        kw.setdefault("op_class", "guard")
        M.append(kw)

    # ── THE FIVE CELLS + SM-7.  Every one REQUIRED KILLED by this session's prompt. ────
    add(id="N-11", ref="M-12", op="COPY 2's GATE-VOCABULARY scan deleted", file=COPY2,
        old='for word in ("ceiling", "per-action", "per action", "exceeded", "not permitted"):',
        new='for word in ():',
        must="KILLED", cell=True)
    add(id="N-13", ref="M-12d", op="COPY 2's VERBATIM-POLICY-CLAUSE scan deleted", file=COPY2,
        old="        for clause in clauses:\n            if clause in full:",
        new="        for clause in clauses:\n            if False:",
        must="KILLED", cell=True)
    add(id="N-17", ref="M-16", op="COPY 2's DENIAL-VALUE EXACT EQUALITY deleted", file=COPY2,
        old="                if value != generic:\n                    findings.append(\n"
            "                        f\"turn {i}: the folded denial is not the generic string: {value!r}\"",
        new="                if False:\n                    findings.append(\n"
            "                        f\"turn {i}: the folded denial is not the generic string: {value!r}\"",
        must="KILLED", cell=True)
    add(id="N-21", ref="M-39", op="COPY 2's PROBE-NOTE-ON-AUTHORED check disarmed", file=COPY2,
        old='        if note in auth:\n            findings.append(f"turn {i}: the probe\'s note text was written into AUTHORED text")',
        new='        if False:\n            findings.append(f"turn {i}: the probe\'s note text was written into AUTHORED text")',
        must="KILLED", cell=True)
    add(id="N-15", ref="M-RES", op="COPY 2's RESIDUE (LAYER 3) catch-all deleted - the layer "
                                   "OF-150 said did not exist", file=COPY2,
        old="            if left.strip():\n                findings.append(",
        new="            if False:\n                findings.append(",
        must="KILLED", cell=True)
    add(id="N-33", ref="SM-7", op="COPY 2's SUMMARY LOCATOR disarmed - the guard then inspects "
                                  "nothing silently", file=COPY2,
        old="        if len(summaries) != 1:\n            findings.append(",
        new="        if False:\n            findings.append(",
        must="KILLED", cell=True)

    # ── COPY 2's OTHER LAYERS AND ITS HELPER ──────────────────────────────────────────
    add(id="N-09", op="COPY 2's LAYER 1 (the config/ ceiling scan) deleted", file=COPY2,
        old='            if value in mandated:\n                findings.append(f"turn {i}: a config/ money ceiling on AUTHORED: {value!r}")',
        new='            if False:\n                findings.append(f"turn {i}: a config/ money ceiling on AUTHORED: {value!r}")')
    add(id="N-18", op="COPY 2's refusal-line COUNT loosened", file=COPY2,
        old="        if refusal_lines != 1:\n            findings.append(",
        new="        if refusal_lines < 0:\n            findings.append(")
    add(id="N-12c", op="COPY 2's LAYER 2b (arm / clause identity over the surface) neutered",
        file=COPY2,
        old='            r"\\barms?\\s*[1-4]S?\\b|\\bP[1-7]\\b|\\bINDETERMINATE\\b|\\bDENIED\\b", mandated, re.I\n        ):\n            findings.append(f"turn {i}: arm or clause identity {token!r} on AUTHORED")',
        new='            r"(?!x)x", mandated, re.I\n        ):\n            findings.append(f"turn {i}: arm or clause identity {token!r} on AUTHORED")')
    add(id="N-19", op="`_sole_layer`'s EXCLUSIVITY half deleted (SM-B re-applied)", file=COPY2,
        old="    assert len(matched) == len(findings), (",
        new="    assert len(matched) <= len(findings), (")
    add(id="N-20", op="`_sole_layer`'s IDENTITY half deleted - it accepts any layer", file=COPY2,
        old="    matched = [f for f in findings if fragment in f]",
        new="    matched = list(findings)")
    add(id="N-34a", op="⚠️ ONE LEVEL OUT: COPY 2's `_cap_formattings` returns an EMPTY set, so "
                       "LAYER 1 iterates over nothing and inspects nothing silently", file=COPY2,
        old="    return {v for v in out if len(v) >= 4}",
        new="    return set()")

    # ── COPY 1.  Untouched by FIX 5; re-measured because Q-084 requires BOTH copies. ───
    add(id="N-08", op="COPY 1's LAYER 1 (the ceiling scan) deleted", file=COPY1,
        old='        if value in values_scan:\n            findings.append(f"a config/ money ceiling reached the AUTHORED surface: {value!r}")',
        new='        if False:\n            findings.append(f"a config/ money ceiling reached the AUTHORED surface: {value!r}")')
    add(id="N-10", op="COPY 1's GATE-VOCABULARY scan deleted", file=COPY1,
        old="    for word in _GATE_VOCABULARY:", new="    for word in ():")
    add(id="N-12", op="COPY 1's VERBATIM-POLICY-CLAUSE scan deleted", file=COPY1,
        old="        if clause.strip() and clause.strip() in scan:",
        new="        if False:")
    add(id="N-14", op="COPY 1's RESIDUE (LAYER 3) deleted", file=COPY1,
        old="    if residue.strip():\n        findings.append(",
        new="    if False:\n        findings.append(")
    add(id="N-16", op="COPY 1's DENIAL-VALUE EXACT EQUALITY deleted", file=COPY1,
        old="                if value != generic:\n                    findings.append(\n"
            "                        f\"the denial the attacker sees is not the generic string: {value!r}\"",
        new="                if False:\n                    findings.append(\n"
            "                        f\"the denial the attacker sees is not the generic string: {value!r}\"",
        )
    add(id="N-34b", ref="M-08b/OF-130", op="COPY 1's summary locator `== 1` -> `>= 1` (the "
                                           "NOT-OWNED survivor, re-measured under OP-19)",
        file=COPY1,
        old="    assert len(summaries) == 1, (", new="    assert len(summaries) >= 1, (")
    add(id="N-34c", op="⚠️ ONE LEVEL OUT: COPY 1's `_cap_formattings` collapse guard removed AND "
                       "the set emptied", file=COPY1,
        old='    assert len(values) >= 8, "the cap formattings collapsed - the fixture proves nothing"\n'
            "    return {v for v in values if len(v) >= 4}",
        new="    return set()")

    # ── src/ — the PROPERTY mutants, and the REAL LEAKS. ──────────────────────────────
    add(id="N-02", op="the verbatim window narrowed by one turn", file=CTXPY,
        old="    kept = history[-verbatim_turns:] if verbatim_turns else ()",
        new="    kept = history[-(verbatim_turns - 1):] if verbatim_turns else ()",
        op_class="src")
    add(id="N-04", op="the 400-token cap made EXCLUSIVE (`<=` -> `<`)", file=CTXPY,
        old="    if estimate_text(text, divisor=divisor) <= token_cap:\n        return text",
        new="    if estimate_text(text, divisor=divisor) < token_cap:\n        return text",
        op_class="src")
    add(id="N-06", op="OF-88's truncation floor removed - the denial is no longer reserved",
        file=CTXPY,
        old="    if token_cap < floor:\n        raise ValueError(",
        new="    if False:\n        raise ValueError(", op_class="src")
    add(id="N-26", op="`crossing()`'s STRICTNESS `>` -> `>=` (the closed-bound property)",
        file=ESTPY,
        old="            if self.tokens_at(reads, divisor=divisor, window=window) > target:",
        new="            if self.tokens_at(reads, divisor=divisor, window=window) >= target:",
        op_class="src")
    add(id="N-27", op="`crossing()`'s range end moved OFF `turn_budget`", file=ESTPY,
        old="        for reads in range(0, turn_budget + 1):",
        new="        for reads in range(0, turn_budget):", op_class="src")
    add(id="N-30", op="Q-046's EXACT-EQUALITY fold widened to CONTAINMENT - world text becomes "
                      "foldable", file=LOOPPY,
        old="        if result_text == generic_denial:", new="        if generic_denial in result_text:",
        op_class="src")
    add(id="N-RL1", ref="INC-42 / M17", op="⚠️ A REAL LEAK IN src/: E1's cap planted INSIDE "
                                           "`LAST_REFUSAL_LABEL`, on the authored surface, every "
                                           "turn, every arm", file=CTXPY,
        old='LAST_REFUSAL_LABEL = "LAST TOOL REFUSAL: "',
        new='LAST_REFUSAL_LABEL = "LAST TOOL REFUSAL (exceeded the configured ceiling of 5000000 paise): "',
        op_class="real-leak")
    add(id="N-RL2", op="⚠️ A REAL LEAK IN src/: arm identity in `STATE_LABEL` (OF-104's shape)",
        file=CTXPY,
        old='STATE_LABEL = "STATE SO FAR: "', new='STATE_LABEL = "STATE SO FAR (arm 2S): "',
        op_class="real-leak")
    add(id="N-RL3", op="⚠️ A REAL LEAK IN src/: unexplained AUTHORED text appended to the summary "
                       "as a NEW LINE - the residue shape, carrying NO policy word", file=CTXPY,
        old='    text = f"{STATE_LABEL}{state.to_json()}\\n{denial_line}"',
        new='    text = f"{STATE_LABEL}{state.to_json()}\\n{denial_line}\\nops: reviewed by the standing checker"',
        op_class="real-leak")
    add(id="N-22", op="⚠️ THE GLOBAL BAN Q-046 FORBIDS: the probe note banned from the WORLD "
                      "surface too. It MUST die - it voids arm 4 by construction", file=COPY2,
        old="        if note in auth:", new="        if note in full:",
        must="KILLED", op_class="door")
    add(id="N-32", op="OP-18: a turn dropped from the corpus/improvisation split's denominator",
        file=LOOPPY,
        old="        return sum(1 for r in self.records if r.provenance is InputProvenance.CORPUS)",
        new="        return sum(1 for r in self.records[1:] if r.provenance is InputProvenance.CORPUS)",
        op_class="src")

    # ── ADDED IN PHASE 2 (the seal permits ADDING, never removing).  Slices F and G. ───
    add(id="N-01", op="OP-1: the window width HARDCODED instead of read through the loader",
        file=LOOPPY,
        old='verbatim_turns=protocol.require("attacker.context_window_turns_verbatim"),',
        new="verbatim_turns=6,", op_class="src")
    add(id="N-03", op="OP-2: the summary stops being a pure function of STATE - the key tuple "
                      "is no longer sorted, so it depends on how the ledger was walked",
        file=CTXPY,
        old='"idempotency_keys_seen": sorted(self.idempotency_keys_seen),',
        new='"idempotency_keys_seen": list(self.idempotency_keys_seen),', op_class="src")
    add(id="N-05", op="OP-3: the cap loosened by one token in the OTHER direction", file=CTXPY,
        old="    if estimate_text(text, divisor=divisor) <= token_cap:\n        return text",
        new="    if estimate_text(text, divisor=divisor) <= token_cap + 1:\n        return text",
        op_class="src")
    add(id="N-23", op="OP-11: Q-047's STRIDE perturbed by one", file=CORPPY,
        old="    stride = max(1, turn_budget // len(corpora))",
        new="    stride = max(1, turn_budget // len(corpora) + 1)", op_class="src")
    add(id="N-24", op="OP-11: the offer made SEED-INDEPENDENT - coverage frozen at one slice",
        file=CORPPY,
        old="    within = (episode_seed * stride + turn_index // len(corpora)) % len(group)",
        new="    within = (turn_index // len(corpora)) % len(group)", op_class="src")
    add(id="N-25", op="OP-12: the divisor HARDCODED instead of resolved through the loader",
        file=ESTPY,
        old='    return cfg.load("protocol").require(_LOADER_RESOLVED["CHARS_PER_TOKEN"])',
        new="    return 3", op_class="src")
    add(id="N-28", op="OP-14: the dynamic-import scan narrowed - `importlib` no longer matched",
        file=COPY1, old='("importlib", r"\\bimportlib\\b"),', new='("importlib", r"(?!x)x"),')
    add(id="N-29", op="OP-15: the authored texts no longer compared BYTE-FOR-BYTE to S8.6",
        file=COPY1, old="        assert on_disk == spec, (",
        new="        assert True or on_disk == spec, (")
    add(id="N-31", op="OP-17: `data/generic_denial.txt` DRIFTED from S8.6 - the seam OF-147 "
                      "names. It must die THROUGH COPY 2",
        file="data/generic_denial.txt",
        old="This action was blocked by policy.",
        new="This action was blocked by policy. Reviewed.", op_class="data")
    add(id="N-35", op="⚠️ ONE LEVEL OUT: COPY 1's `_HOLE_VOCABULARY` emptied, so `_hole_findings` "
                      "iterates over nothing and inspects nothing silently", file=COPY1,
        old='_HOLE_VOCABULARY = ("CANARY-A", "CANARY-B", "CANARYRECON is", "HOLES.md", "exemption clause")',
        new="_HOLE_VOCABULARY = ()")
    add(id="N-SM1", ref="SM-1", op="OF-153's OBVIOUS WIDENING, RE-RUN: copy 2's residue layer "
                                   "no longer subtracts the STATE LINE's body, so residue would "
                                   "see text inside the state line. FIX 5 says it dies with 22 "
                                   "failures ON A CORRECT CONTEXT - measured here", file=COPY2,
        old='                    left = left.replace(ctx.STATE_LABEL, "", 1)\n'
            "                    if body:\n"
            '                        left = left.replace(body, "", 1)',
        new="                    left = left.replace(ctx.STATE_LABEL, \"\", 1)",
        op_class="of-153")
    add(id="N-RES2", op="COPY 2's residue layer gated OFF at its `elif` rather than at its `if` - "
                        "a SECOND operator on the layer OF-150 built", file=COPY2,
        old="        elif refusal_lines == 1:", new="        elif False:")
    add(id="N-38", op="COPY 2's CLAIM 1 clause-IDENTIFIER regex neutered - a catcher no "
                      "fixture in this file has ever fired", file=COPY2,
        old='        for token in re.findall(r"\\bP[1-7]\\b", auth):',
        new='        for token in re.findall(r"(?!x)x", auth):')
    add(id="N-39", op="COPY 2's CLAIM 3 attack-list patterns emptied - four catchers no "
                      "fixture in this file has ever fired", file=COPY2,
        old='            (r"\\bA[1-6]\\b", "attack identifier"),\n'
            '            (r"\\bE[1-3]\\b", "envelope invariant"),\n'
            '            (r"\\bS[1-4]\\b", "sequence invariant"),\n'
            '            (r"INVARIANTS\\.md", "the invariants artefact"),',
        new='            (r"(?!x)x", "attack identifier"),')
    add(id="N-40", op="COPY 2's denial-VALUE arm/clause regex neutered (the FIELD-level check, "
                      "distinct from LAYER 2b's surface-level one)", file=COPY2,
        old='                    r"\\barms?\\s*[1-4]S?\\b|\\bP[1-7]\\b|\\bINDETERMINATE\\b|'
            '\\bDENIED\\b", value, re.I',
        new='                    r"(?!x)x", value, re.I')
    add(id="N-29b", op="OP-15, THE REAL-DRIFT FORM: `data/attacker_sys.txt` DRIFTED from S8.6. "
                       "N-29 mutated the ASSERTION and is degenerate; this mutates the DATA and "
                       "asks whether the suite notices", file="data/attacker_sys.txt",
        old="Before acting, READ.", new="Before acting, READ CAREFULLY.", op_class="data")
    add(id="N-37", op="COPY 1's probe-note-on-AUTHORED check disarmed - the copy-1 TWIN of M-39, "
                      "so claim 2's note cell is measured in BOTH copies", file=COPY1,
        old="    if note in context.authored_text():",
        new="    if False:")
    add(id="N-35b", op="⚠️ ONE LEVEL OUT: COPY 2's probe-vocabulary tuple emptied", file=COPY2,
        old='        for token in ("CANARY-A", "CANARY-B", "HOLES.md", "exemption clause"):',
        new="        for token in ():")

    return M


SLICES = {
    "A": ["N-11", "N-13", "N-17", "N-21", "N-15", "N-33"],
    "B": ["N-09", "N-18", "N-12c", "N-19", "N-20", "N-34a"],
    "C": ["N-08", "N-10", "N-12", "N-14", "N-16", "N-34b", "N-34c"],
    "D": ["N-02", "N-04", "N-06", "N-26", "N-27", "N-30"],
    "E": ["N-RL1", "N-RL2", "N-RL3", "N-22", "N-32"],
    "F": ["N-01", "N-03", "N-05", "N-23", "N-24", "N-25"],
    "G": ["N-28", "N-29", "N-31", "N-35", "N-35b", "N-SM1", "N-RES2"],
    # OF-159's CTRL-LIVE, run on the four clones that finished before it was added.
    "A2": [], "B2": [], "D2": [], "E2": [],
    "H": ["N-29b", "N-37"],
    "I": ["N-38", "N-39", "N-40"],
}


# ======================================================================================
# THE RUNNER
# ======================================================================================
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_suite(tree: Path, tag: str) -> dict:
    """One measurement.  ⚠️ THE ENV IS PASSED TO `subprocess.run` ITSELF (INC-69), and the
    provenance print is in the SAME subprocess as the pytest run."""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(tree / "src")
    env["PYTHONIOENCODING"] = "utf-8"
    # ⚠️ ONE subprocess: the provenance print and the pytest run are the SAME process, so a
    # transcript that shows the tree is evidence about the tree that was measured (INC-69).
    script = (
        "import sys, whetstone_gate, whetstone_gate.config as cfg\n"
        "sys.stderr.write('PROVENANCE PKG  : ' + str(whetstone_gate.__file__) + '\\n')\n"
        "sys.stderr.write('PROVENANCE ROOT : ' + str(cfg.repo_root()) + '\\n')\n"
        "import pytest\n"
        "sys.exit(pytest.main(['-q','-p','no:randomly','--no-header','-rf'] + "
        + repr(SUITE) + "))\n"
    )
    t0 = time.time()
    proc = subprocess.run(
        [PYTHON, "-c", script],
        cwd=str(tree), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=3600,
    )
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    passed = failed = errors = 0
    m = re.search(r"(\d+) passed", out)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+) failed", out)
    if m:
        failed = int(m.group(1))
    m = re.search(r"(\d+) error", out)
    if m:
        errors = int(m.group(1))
    killers = sorted({
        line.split(" ")[1].split("[")[0]
        for line in out.splitlines()
        if line.startswith("FAILED ") or line.startswith("ERROR ")
        for _ in [0]
    } | {
        re.sub(r"\[.*", "", line[len("FAILED "):]).strip()
        for line in out.splitlines() if line.startswith("FAILED ")
    })
    prov = [l for l in out.splitlines() if l.startswith("PROVENANCE")]
    return dict(tag=tag, passed=passed, failed=failed, errors=errors, rc=proc.returncode,
                killers=killers, provenance=prov, seconds=round(time.time() - t0, 1),
                tail=out[-2500:])


def apply_mutant(tree: Path, spec: dict):
    path = tree / spec["file"]
    original = path.read_bytes()
    text = original.decode("utf-8")
    count = text.count(spec["old"])
    if count != 1:
        return None, count
    path.write_bytes(text.replace(spec["old"], spec["new"], 1).encode("utf-8"))
    return original, 1


def restore(path: Path, original: bytes, before_sha: str) -> bool:
    path.write_bytes(original)
    return sha(path) == before_sha


TREE_FOR = {"A2": "A", "B2": "B", "D2": "D", "E2": "E", "H": "A", "I": "B"}


def run_slice(name: str, ids: list, results: dict, lock: threading.Lock):
    tree = SCRATCH / ("tree_%s" % TREE_FOR.get(name, name))
    log = []

    def say(s):
        log.append(s)
        with lock:
            print("[%s] %s" % (name, s))

    all_specs = {m["id"]: m for m in mutants()}
    plan = [all_specs[i] for i in ids] + [POSITIVE_CONTROL, POSITIVE_CONTROL_2]

    pre = run_suite(tree, "PRE-CONTROL")
    say("PRE-CONTROL  %d passed, %d failed, %d error (%ss)"
        % (pre["passed"], pre["failed"], pre["errors"], pre["seconds"]))
    for p in pre["provenance"]:
        say("  " + p)
    if pre["passed"] != CONTROL_TOTAL or pre["failed"] or pre["errors"]:
        say("⚠️ SLICE VOID - the pre-run control is not green")
        results[name] = dict(void=True, reason="pre-control not green", pre=pre, log=log)
        return

    rows = []
    for spec in plan:
        path = tree / spec["file"]
        before = sha(path)
        original, count = apply_mutant(tree, spec)
        if original is None:
            say("%-7s NOT CONSTRUCTIBLE - the anchor matched %d times, expected 1"
                % (spec["id"], count))
            rows.append(dict(spec=spec, verdict="NOT CONSTRUCTIBLE", matches=count))
            continue
        res = run_suite(tree, spec["id"])
        ok = restore(path, original, before)
        verdict = "KILLED" if (res["failed"] or res["errors"]) else "SURVIVED"
        say("%-7s %-9s %d passed / %d failed / %d error  (%ss)  restore-sha-ok=%s"
            % (spec["id"], verdict, res["passed"], res["failed"], res["errors"],
               res["seconds"], ok))
        if res["killers"]:
            for k in res["killers"][:8]:
                say("        killed by: %s" % k)
        rows.append(dict(spec=spec, verdict=verdict, res=res, restored=ok))
        if not ok:
            say("⚠️ SLICE VOID - restore did not reproduce the original SHA-256")
            results[name] = dict(void=True, reason="restore sha mismatch", rows=rows, log=log)
            return

    post = run_suite(tree, "POST-CONTROL")
    say("POST-CONTROL %d passed, %d failed, %d error (%ss)"
        % (post["passed"], post["failed"], post["errors"], post["seconds"]))
    void = post["passed"] != CONTROL_TOTAL or post["failed"] or post["errors"]
    pc = [r for r in rows if r["spec"]["id"] in ("N-PC", "N-PC2")]
    pc_ok = len(pc) == 2 and all(r["verdict"] == "KILLED" for r in pc)
    if not pc_ok:
        say("⚠️ SLICE VOID - THE POSITIVE CONTROL DID NOT DIE (OF-159)")
    if void:
        say("⚠️ SLICE VOID - the post-restore control is not green")
    results[name] = dict(void=bool(void or not pc_ok), pre=pre, post=post, rows=rows,
                         positive_control_died=pc_ok, log=log)


def main():
    which = sys.argv[1:] or sorted(SLICES)
    results, lock = {}, threading.Lock()
    threads = []
    for name in which:
        t = threading.Thread(target=run_slice, args=(name, SLICES[name], results, lock))
        t.start()
        threads.append(t)
        time.sleep(2)
    for t in threads:
        t.join()

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    for name in sorted(results):
        r = results[name]
        print("SLICE %s  void=%s  positive-control-died=%s"
              % (name, r.get("void"), r.get("positive_control_died")))
        for row in r.get("rows", []):
            s = row["spec"]
            res = row.get("res") or {}
            print("  %-7s %-9s failed=%-4s %s"
                  % (s["id"], row["verdict"], res.get("failed", "-"), s["op"][:70]))
    out = SCRATCH / "mutants_result.json"
    out.write_text(json.dumps(
        {k: {kk: vv for kk, vv in v.items() if kk != "rows"} |
            {"rows": [{"id": r["spec"]["id"], "ref": r["spec"].get("ref"),
                       "op": r["spec"]["op"], "file": r["spec"]["file"],
                       "must": r["spec"].get("must"), "class": r["spec"].get("op_class"),
                       "cell": r["spec"].get("cell", False),
                       "verdict": r["verdict"],
                       "failed": (r.get("res") or {}).get("failed"),
                       "passed": (r.get("res") or {}).get("passed"),
                       "killers": (r.get("res") or {}).get("killers", []),
                       "provenance": (r.get("res") or {}).get("provenance", [])}
                      for r in v.get("rows", [])]}
         for k, v in results.items()}, indent=1), encoding="utf-8")
    print("\nwritten: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
