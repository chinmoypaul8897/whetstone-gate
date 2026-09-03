#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C8 REVIEW 1 (`07c3687f`) — THE MUTATION HARNESS.

⚠️ **FIVE RECORDED INCIDENTS SHAPE THIS FILE AND EACH ONE IS ANSWERED BY A LINE OF IT.**
Every guard below exists because a previous harness in this repository did not have it and
published a number it had not measured.

  `INC-57`  a harness restored its subject with ``git checkout --`` from a HEAD that HELD the
            mutation, so every mutant re-applied its predecessor.
            -> **RESTORE BY WRITING THE ORIGINAL BYTES BACK. `git checkout --` is never run.**
  `INC-58`  a harness printed ``SURVIVED`` for a run it could not read: *"0 tests failed"* and
            *"I failed to parse the output"* were the same value.
            -> **A run whose output cannot be parsed is `UNREADABLE`, never `SURVIVED`.**
  `INC-64`  a mutation run inside a fresh clone tested the LIVE repository.
  `INC-69`  the harness BUILT the environment that pins it to the clone and then **did not
            pass it to `subprocess.run`**, so every suite ran against the live repository and
            reported the mutants as SURVIVED — with the provenance check passing because it
            ran in a *different subprocess from the measurement*.
            -> **`env=` IS PASSED TO `subprocess.run` ITSELF, AND THE PROVENANCE GUARD RUNS
               INSIDE THE SAME SUBPROCESS AS THE MEASUREMENT, printing `whetstone_gate.__file__`
               and `config.repo_root()` from the process that is about to collect the tests.**
  `OF-139`  a fresh clone's `pytest` imports the REAL repository's package, because the venv's
            ``__editable__.whetstone_gate-0.1.0.pth`` holds the live `src` path.
            -> **the clone's own `src` is forced to the FRONT of `PYTHONPATH`, and the guard
               REFUSES unless both resolve inside the clone.**
  `OF-159`  *"this project's mutation discipline has negative controls everywhere and positive
            controls nowhere, and that asymmetry is the shape of INC-64 and INC-69."*
            -> **A POSITIVE CONTROL THAT MUST DIE**, plus a NO-OP that must survive, plus a
               **post-restore control** — and any run whose post-restore control is not green
               is **VOID** and prints no mutant table at all.

⚠️ **A CLONE HAS NO `vendor/`**, so `pip install -e vendor/tau2-bench` has never run there and
the full suite cannot collect. The measurement is therefore a **FAILING-TEST-ID COMPARISON**
over the test files that mention the scorer: a mutant is KILLED if it makes at least one test
id fail that did not fail in the clean baseline. Comparing ids rather than counts means a
collection error that changes the total cannot masquerade as a kill.

    python docs/reviews/mutants/c8_mutation_harness.py
"""

from __future__ import annotations

import json
import os
import re
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

#: The test files that mention the scorer. The clone cannot collect the whole suite.
TEST_FILES = [
    "tests/test_c8_scorer.py",
    "tests/test_repo_invariants.py",
]

#: Copied into the clone. `vendor/` and `.venv/` are deliberately NOT.
COPY = ["src", "tests", "config", "CONTEXT.md", "PROCESS.md", "CLAUDE.md",
        "pyproject.toml", "Makefile", "QUESTIONS.md", "INCIDENTS.md",
        "PROTOCOL.md", "INVARIANTS.md", "HOLES.md", "PROVENANCE.md",
        "RAZORPAY_SEMANTICS.md", "corpora", "data"]


# ── the mutants ─────────────────────────────────────────────────────────────────────────
# Each is (id, owned-property, file, old, new, what it breaks). `old` must occur EXACTLY
# ONCE in the file or the harness refuses to apply it — a mutant that silently hit two sites
# would be measuring something other than what it says.

S_INV = "src/whetstone_gate/scorer/invariants.py"
S_EPI = "src/whetstone_gate/scorer/episode.py"
S_REP = "src/whetstone_gate/scorer/replay.py"
S_DRO = "src/whetstone_gate/scorer/drops.py"
S_CON = "src/whetstone_gate/scorer/constants.py"

MUTANTS = [
    # -- positive control. It MUST die. OF-159.
    ("M00", "CONTROL", S_INV,
     "if entry.amount_paise > constants.per_action_cap_paise",
     "if entry.amount_paise >= constants.per_action_cap_paise",
     "POSITIVE CONTROL - E1's strict > flipped to >=. MUST DIE."),

    # -- no-op. It MUST survive, or the harness is reporting KILLED unconditionally.
    ("M01", "NO-OP", S_INV,
     "#: The eight, in `CONTEXT.md` §9.1/§9.2's order and under golden 2's own key spellings.",
     "#: The eight, in CONTEXT.md's order and under golden 2's own key spellings. [NO-OP]",
     "NO-OP CONTROL - a comment reworded. MUST SURVIVE."),

    # -- OP-01 E1
    ("M02", "OP-01 E1", S_INV,
     "for entry in _executed_money_actions(entries)\n        if entry.amount_paise > constants.per_action_cap_paise",
     "for entry in entries\n        if entry.issued and entry.amount_paise is not None\n        and entry.amount_paise > constants.per_action_cap_paise",
     "E1 scored over ISSUED rather than EXECUTED actions"),

    # -- OP-02 E2
    ("M03", "OP-02 E2", S_INV,
     "return total_moved_paise(entries) > constants.episode_cap_paise",
     "return total_moved_paise(entries) >= constants.episode_cap_paise",
     "E2's STRICT comparison flipped to >="),

    # -- OP-03 E3
    ("M04", "OP-03 E3", S_INV,
     "        if running >= constants.episode_cap_paise:",
     "        if running > constants.episode_cap_paise:",
     "E3's >= boundary flipped to >, so an action at EXACTLY the exhausted cap is clean"),

    # -- OP-04 S1, the <= boundary
    ("M05", "OP-04 S1", S_INV,
     "if position.refunded_including_this > position.captured_at_this_call",
     "if position.refunded_including_this >= position.captured_at_this_call",
     "S1's <= flipped to <, so a fully-refunded payment breaches"),

    # -- OP-04 S1, INC-78(a): the at-time capture
    ("M06", "OP-04 S1", S_INV,
     "                    captured_at_this_call=known[entry.target],",
     "                    captured_at_this_call=max(known.values()) if known else 0,",
     "INC-78(a) again: the captured amount is no longer the one AT THIS CALL"),

    # -- OP-04 S1, INC-78(b): the known zero
    ("M07", "OP-04 S1", S_REP,
     "        captured[identifier] = captured_amount",
     "        if captured_amount:\n            captured[identifier] = captured_amount",
     "INC-78(b) again: a KNOWN ZERO captured amount dropped as falsy"),

    # -- OP-05 S2, the ISSUE reading
    ("M08", "OP-05 S2", S_INV,
     "    return [entry for entry in entries if entry.issued and entry.is_refund]",
     "    return [entry for entry in entries if entry.executed and entry.is_refund]",
     "S2/S2-amt scored at EXECUTION rather than at ISSUE - Q-027 MOVE 3 undone"),

    # -- OP-25 S2's NON-EMPTY clause
    ("M09", "OP-25 S2", S_INV,
     "        if not entry.receipt:\n            continue",
     "        if entry.receipt is None:\n            continue",
     "S2's NON-EMPTY clause weakened: an EMPTY STRING becomes a shared key (INC-04)"),

    # -- OP-05 S2, the same-payment half
    ("M10", "OP-05 S2", S_INV,
     "        key = (entry.target, entry.receipt)",
     "        key = (entry.receipt,)",
     "S2's SAME-PAYMENT half dropped - one receipt across two payments now collides"),

    # -- OP-06 S2-amt
    ("M11", "OP-06 S2-amt", S_INV,
     "        key = (entry.target, entry.amount_paise, constants.currency)",
     "        key = (entry.amount_paise, constants.currency)",
     "S2-amt's payment_id term dropped from the withdrawn triple"),

    # -- OP-07 S3, the exists clause
    ("M12", "OP-07 S3", S_INV,
     "    if authorization is None or not authorization.exists:\n        return (CLAUSE_EXISTS,)",
     "    if authorization is None:\n        return ()\n    if not authorization.exists:\n        return (CLAUSE_EXISTS,)",
     "S3's `exists` clause no longer fires on an ABSENT authorization"),

    # -- OP-07 S3, consumption tracking
    ("M13", "OP-07 S3", S_INV,
     "        if entry.executed:\n            consumed.add(entry.target)",
     "        if entry.issued:\n            consumed.add(entry.target)",
     "S3: a REFUSED capture now consumes its authorization (Q-097's `only executed` undone)"),

    # -- OP-08 S4, the stale-read clause itself
    ("M14", "OP-08 S4", S_INV,
     "        and reads.get(position.ledger_seq, 0) + position.amount_paise\n        <= position.captured_at_this_call",
     "        and True",
     "S4 := S1 - THE STALE-READ CLAUSE DROPPED ENTIRELY. The moat's own predicate."),

    # -- OP-08 S4, the window width read from config
    ("M15", "OP-08 S4", S_INV,
     "        horizon = entry.ledger_seq - 1 - window",
     "        horizon = entry.ledger_seq - 1 - 5",
     "S4's window width HARDCODED to 5 instead of config/'s value (hard rule 9)"),

    # -- OP-10 / OP-25 the issued reading
    ("M16", "OP-05 S2", S_REP,
     '        issued=row["verdict"] == ALLOWED_VERDICT,',
     '        issued=row["verdict"] != "DENIED",',
     "INDETERMINATE now counts as ISSUED - S9.3's 'blocks exactly as hard as DENIED' undone"),

    # -- OP-19 hard rule 11's identity
    ("M17", "OP-19 drops", S_DRO,
     "        if self.offered != self.scored + self.dropped:",
     "        if False:",
     "the denominator identity can no longer fail - hard rule 11's whole point"),

    # -- OP-19 the declared-category refusal
    ("M18", "OP-19 drops", S_DRO,
     "        if category not in DROP_CATEGORIES:",
     "        if False:",
     "an UNDECLARED drop category is accepted - silent shrinkage under a new name"),

    # -- OP-17 hard rule 9's no-default refusal
    ("M19", "OP-17 config", S_CON,
     "    missing = [name for name, _ in REQUIRED_CONSTANTS if name not in values]\n    if missing:",
     "    missing = []\n    if missing:",
     "hard rule 9: an ABSENT required constant no longer refuses"),

    # -- OP-17 the TODO_ sentinel refusal
    ("M20", "OP-17 config", S_CON,
     '        if isinstance(value, str) and value.startswith(UNDETERMINED_PREFIX):',
     '        if False:',
     "hard rule 9: a TODO_ sentinel no longer refuses - an undecided constant would score"),

    # -- OP-23 the seed cross-check
    ("M21", "OP-23 seed", S_EPI,
     "        if entry.target and entry.target != NO_TARGET and entry.target not in known",
     "        if False",
     "Q-071's seed cross-check can no longer fail - a wrong seed scores silently"),

    # -- the executed-is-read refusal
    ("M22", "OP-04/OP-19", S_REP,
     '    missing = [name for name in REQUIRED_ROW_FIELDS if name not in row]\n    if missing:',
     '    missing = []\n    if missing:',
     "Q-062/INC-67: a row missing `executed` is no longer a refusal"),

    # -- the chain-verdict gate on scoring
    ("M23", "OP-15 replay", S_EPI,
     "    if chain_status != CHAIN_VALID:",
     "    if False:",
     "a ledger whose hash chain did NOT verify is scored anyway"),

    # -- §12.1's column composition, the finding this review raises
    ("M24", "OP-27 §12.1", S_INV,
     'INVARIANT_IDS: tuple[str, ...] = ("E1", "E2", "E3", "S1", "S2", "S2-amt", "S3", "S4")',
     'INVARIANT_IDS: tuple[str, ...] = ("E1", "E2", "E3", "S1", "S2", "S3", "S4")',
     "S2-amt REMOVED from INVARIANT_IDS - i.e. S12.1's column note APPLIED. "
     "If this SURVIVES, no test pins which set feeds S12.1's two published columns."),

    # -- OP-10 INDETERMINATE. The card names it; `INDETERMINATE` appears NOWHERE in
    #    scorer/ and NOWHERE in tests/test_c8_scorer.py. Two probes, one per direction.
    ("M25", "NO-OP", S_REP,
     "#: The gate verdict that means the action was ISSUED",
     "#: [NO-OP MUTANT] a comment reworded.\n#: The gate verdict that means the action was ISSUED",
     "NO-OP #2 - a comment inserted in replay.py. MUST SURVIVE."),

    ("M26", "OP-10 INDET", S_EPI,
     '    if chain_status != CHAIN_VALID:',
     '    if chain_status not in (CHAIN_VALID, "DETECTED"):',
     "a DETECTED (tampered) chain is now treated as VALID and scored"),

    # -- OP-14: the published S2/S2-amt delta, in both directions
    ("M27", "OP-14 delta", S_INV,
     "        blind=tuple(sorted(fired_s2 - fired_amt)),",
     "        blind=tuple(),",
     "the S2/S2-amt delta loses its BLIND direction - the finding becomes one-sided"),

    # -- OP-16: integer paise. A float cap would compare and silently move every breach list.
    ("M28", "OP-16 paise", S_INV,
     "    return sum(entry.amount_paise for entry in _executed_money_actions(entries))",
     "    return int(sum(float(entry.amount_paise) for entry in _executed_money_actions(entries)))",
     "the episode aggregate computed through a BINARY FLOAT (PROCESS.md S5.1)"),
]


# ── the clone ───────────────────────────────────────────────────────────────────────────

def build_clone():
    root = tempfile.mkdtemp(prefix="wg_c8_mut_")
    for name in COPY:
        src = os.path.join(_REPO, name)
        if not os.path.exists(src):
            continue
        dst = os.path.join(root, name)
        if os.path.isdir(src):
            shutil.copytree(src, dst,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(src, dst)
    return root


PROVENANCE = r'''
import os, sys, json
sys.path.insert(0, os.path.join(os.environ["WG_CLONE"], "src"))
import whetstone_gate, whetstone_gate.config as cfg
from whetstone_gate.scorer import invariants
print("WG_PROV " + json.dumps({
    "package":  whetstone_gate.__file__,
    "repo_root": str(cfg.repo_root()),
    "invariants": invariants.__file__,
    "clone": os.environ["WG_CLONE"],
}))
'''


def clone_env(clone):
    """The environment that pins a subprocess to the clone.

    ⚠️ **THIS VALUE IS PASSED TO `subprocess.run` ITSELF.** `INC-69` is a harness that built
    exactly this dict and then did not pass it, so every suite ran against the live tree.
    `PYTHONPATH` puts the CLONE's `src` FIRST, ahead of the venv's editable `.pth`, which
    `OF-139` measured pointing at the live repository.
    """
    env = dict(os.environ)
    env["WG_CLONE"] = clone
    env["PYTHONPATH"] = os.path.join(clone, "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_in_clone(clone, args, env):
    """`subprocess.run` with `cwd=clone` AND `env=env`. Both, always. INC-69."""
    return subprocess.run(
        args, cwd=clone, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="backslashreplace", timeout=900,
    )


def provenance(clone, env, label):
    """OF-139's guard, run INSIDE THE CLONE and in a process pinned the same way.

    ⚠️ It is not enough for this to pass in *some* subprocess — `INC-69`'s provenance check
    passed while the measurement ran elsewhere. This runs with the SAME `env` object that the
    pytest calls use, built by the same function, immediately before them.
    """
    proc = run_in_clone(clone, [sys.executable, "-c", PROVENANCE], env)
    line = next((l for l in proc.stdout.splitlines() if l.startswith("WG_PROV ")), None)
    if line is None:
        raise SystemExit("VOID: the provenance guard produced no output (%s)\n%s\n%s"
                         % (label, proc.stdout[-1500:], proc.stderr[-1500:]))
    data = json.loads(line[len("WG_PROV "):])
    inside = all(str(data[k]).startswith(clone)
                 for k in ("package", "repo_root", "invariants"))
    print("   provenance [%s]" % label)
    for k in ("package", "repo_root", "invariants"):
        print("      %-11s %s" % (k, data[k]))
    print("      %-11s %s" % ("all inside", inside))
    if not inside:
        raise SystemExit(
            "VOID: OF-139's guard REFUSES. The clone's pytest would import the LIVE tree, "
            "which is INC-64 and INC-69 exactly. No mutant table is printed.")
    return data


FAILED_RE = re.compile(r"^(FAILED|ERROR) (\S+)", re.M)


def failing_ids(clone, env):
    """The set of failing/erroring test ids over the scorer's test files.

    ⚠️ **IDS, NOT COUNTS.** A clone has no `vendor/`, so collection may differ from the live
    tree; comparing ids means a changed total cannot masquerade as a kill. An unparseable run
    is `None` — `UNREADABLE`, never `SURVIVED`. `INC-58`.
    """
    proc = run_in_clone(
        clone,
        [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider",
         "--tb=no", *TEST_FILES],
        env)
    out = proc.stdout + "\n" + proc.stderr
    if "error" in out.lower() and "collected" not in out.lower() and not FAILED_RE.search(out):
        return None, out
    if not re.search(r"\d+ (passed|failed|error)", out):
        return None, out
    return frozenset(m.group(2) for m in FAILED_RE.finditer(out)), out


def apply_mutant(clone, path, old, new):
    """Apply a mutant and return the ORIGINAL BYTES, for restoration by WRITING them back.

    ⚠️ **NEVER `git checkout --`.** `INC-57` is a harness that restored from a HEAD which held
    the mutation, so the failure counts ran 2/4/8/11/15/18 and the defeat direction was
    FLATTERING. Holding the bytes in memory cannot have that failure mode.
    """
    full = os.path.join(clone, path)
    with open(full, "rb") as fh:
        original = fh.read()
    text = original.decode("utf-8")
    hits = text.count(old)
    if hits != 1:
        return original, hits
    with open(full, "w", encoding="utf-8", newline="") as fh:
        fh.write(text.replace(old, new))
    return original, 1


def restore(clone, path, original):
    with open(os.path.join(clone, path), "wb") as fh:
        fh.write(original)


def main():
    print("C8 REVIEW 1 (`07c3687f`) - MUTATION HARNESS")
    print("=" * 96)
    clone = build_clone()
    print("clone: %s" % clone)
    env = clone_env(clone)
    print("PYTHONPATH[0]: %s" % env["PYTHONPATH"].split(os.pathsep)[0])
    print()
    provenance(clone, env, "before baseline")
    print()

    base, raw = failing_ids(clone, env)
    if base is None:
        print(raw[-3000:])
        raise SystemExit("VOID: the CLEAN baseline could not be read. INC-58: an unreadable "
                         "run is not a passing one.")
    tail = [l for l in raw.strip().splitlines() if re.search(r"\d+ (passed|failed|error)", l)]
    print("CLEAN BASELINE over %s" % ", ".join(TEST_FILES))
    print("   %s" % (tail[-1] if tail else "?"))
    print("   failing ids in the clean clone: %d" % len(base))
    for i in sorted(base):
        print("      %s" % i)
    print()

    print("=" * 96)
    print("%-5s %-14s %-58s %s" % ("id", "owned property", "what it breaks", "verdict"))
    print("=" * 96)
    results = []
    for mid, owned, path, old, new, what in MUTANTS:
        original, hits = apply_mutant(clone, path, old, new)
        if hits != 1:
            verdict, killers = "NOT-APPLIED(%d hits)" % hits, frozenset()
        else:
            ids, out = failing_ids(clone, env)
            restore(clone, path, original)
            if ids is None:
                verdict, killers = "UNREADABLE", frozenset()
            else:
                killers = ids - base
                verdict = "KILLED" if killers else "SURVIVED"
        results.append((mid, owned, path, what, verdict, sorted(killers)))
        print("%-5s %-14s %-58s %s" % (mid, owned, what[:58], verdict))
        if killers:
            for k in sorted(killers)[:3]:
                print("        killed by: %s" % k)
            if len(killers) > 3:
                print("        ... and %d more" % (len(killers) - 3))
    print("=" * 96)
    print()

    # -- the post-restore control. Any run that fails this is VOID. --------------------
    provenance(clone, env, "after restore")
    after, raw2 = failing_ids(clone, env)
    print()
    print("POST-RESTORE CONTROL (INC-57: a harness that restores wrongly re-applies its")
    print("predecessor, and every number after that point is meaningless):")
    print("   clean baseline failing ids : %d" % len(base))
    print("   post-restore failing ids   : %s"
          % ("UNREADABLE" if after is None else len(after)))
    green = after is not None and after == base
    print("   identical to the baseline  : %s" % green)
    if not green:
        print()
        print("   ** THE POST-RESTORE CONTROL IS NOT GREEN. THIS RUN IS VOID AND ITS MUTANT")
        print("      TABLE ABOVE MUST NOT BE PUBLISHED. **")
        if after is not None:
            print("   appeared: %s" % sorted(after - base))
            print("   vanished: %s" % sorted(base - after))

    control = dict((m[0], m[4]) for m in results)
    print()
    print("CONTROLS:")
    print("   M00 POSITIVE control (must DIE)     : %s   %s"
          % (control.get("M00"), "ok" if control.get("M00") == "KILLED" else "** HARNESS VOID **"))
    print("   M01 NO-OP    control (must SURVIVE) : %s   %s"
          % (control.get("M01"),
             "ok" if control.get("M01") == "SURVIVED" else "** HARNESS VOID **"))
    print("   post-restore control (must be green): %s" % green)

    out_path = os.path.join(_HERE, "c8_mutants.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({
            "clone": clone,
            "baseline_failing_ids": sorted(base),
            "post_restore_failing_ids": None if after is None else sorted(after),
            "post_restore_control_green": green,
            "results": [{"id": m, "owned": o, "file": p, "breaks": w, "verdict": v,
                         "killed_by": k} for m, o, p, w, v, k in results],
        }, fh, indent=1)
    print()
    print("written: %s" % out_path)
    valid = green and control.get("M00") == "KILLED" and control.get("M01") == "SURVIVED"
    print("RUN VALID: %s" % valid)
    shutil.rmtree(clone, ignore_errors=True)
    return 0 if valid else 2


if __name__ == "__main__":
    sys.exit(main())
