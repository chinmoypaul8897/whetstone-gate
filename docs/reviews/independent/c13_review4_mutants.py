"""C13 REVIEW 4 - the mutation driver.

Runs in a FRESH OS TEMP CLONE whose path is passed as argv[1].  For each mutant:

  1. capture the target file's ORIGINAL BYTES from the (restored) tree;
  2. apply the mutation and assert the bytes actually changed - a no-op mutation that
     "survives" is the single most flattering failure a harness can have;
  3. COMMIT the mutation inside the clone, so the tree under test is the tree that is
     committed and `test_the_object_store_and_the_working_tree_agree` cannot mask a result;
  4. run the named test command;
  5. RESTORE BY WRITING BACK THE ORIGINAL BYTES - never `git checkout --` from a HEAD that
     holds the mutation.  C6 REVIEW 4's harness was defeated exactly that way, and a
     defeated restore reports EVERY mutant as KILLED;
  6. commit the restore and RE-RUN THE CONTROL.  A run whose post-restore control is not
     green is VOID and is printed as VOID, never scored as a kill.

Stdlib only.  Imports nothing from `src/` - it drives pytest as a subprocess.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

CLONE = Path(sys.argv[1]).resolve()
ONLY = sys.argv[2:] or None

C13_TEST = "tests/test_c13_camel_comparator.py"
CONTROL = ["python", "-m", "pytest", C13_TEST, "-q", "--no-header"]
FAST = ["python", "-m", "pytest", C13_TEST, "-x", "-q", "--no-header"]


#: The clone is USELESS without this and the failure direction is the flattering one in
#: reverse.  `.venv/Lib/site-packages/__editable__.whetstone_gate-0.1.0.pth` puts the REAL
#: repository's `src` on `sys.path`, so a bare `python -m pytest` inside the clone imports
#: `C:\Users\chinm\whetstone-gate\src\whetstone_gate` and every `src/` mutation applied
#: here would have had NO EFFECT AT ALL - every mutant reported as SURVIVED.  Measured, not
#: assumed: the check is printed at the top of every run.  PYTHONPATH precedes site-packages
#: in `sys.path`, so this wins.
ENV = {**os.environ, "PYTHONPATH": str(CLONE / "src")}


def sh(args, cwd=CLONE):
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=ENV)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def commit(message: str) -> None:
    sh(["git", "add", "-A"])
    sh(["git", "-c", "user.name=mutant", "-c", "user.email=m@x", "commit", "-q",
        "--no-verify", "-m", message])


def summarise(proc) -> str:
    tail = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
    return tail[-1][:150] if tail else "(no output)"


# -------------------------------------------------------------------------------------------
# The mutants.  (id, OWN row, file, [(old, new), ...], description, command)
# -------------------------------------------------------------------------------------------

INV = "src/whetstone_gate/camel_comparator/invocation.py"
MAIN = "src/whetstone_gate/camel_comparator/__main__.py"
BB = "src/whetstone_gate/camel_comparator/branch_b.py"
LANES = "config/lanes.yaml"
CTX = "CONTEXT.md"

MUTANTS = [
    # ---- REVIEW 3's five survivors ---------------------------------------------------------
    ("N-B", "OWN-3", INV,
     [('        "on a cause that has been diagnosed",', '        "cause",')],
     "requirement 1 phrase weakened to the bare substring 'cause'"),
    ("N-C", "OWN-3", INV,
     [('        "a harness defect is never branch b",', '        "harness",')],
     "requirement 3 phrase weakened to 'harness' - the exhibit under which "
     "'a harness defect is SOMETIMES Branch B' passed the whole repository"),
    ("N-D", "OWN-3", INV,
     [('        "protocol.md",', '        "md",')],
     "requirement 4 phrase weakened to 'md' - CONTEXT.md then satisfies it"),
    ("N-E", "OWN-3", INV,
     [('''    (
        "where the diagnosed cause is recorded before a branch is selected",
        "protocol.md",
    ),
)''', ")")],
     "one whole BRANCH_B_REQUIREMENTS entry deleted"),
    ("N-I2", "OWN-6", INV,
     [('''        return branch_condition_problems(
            lanes.require("camel_comparator.branch_a_condition"),
            lanes.require("camel_comparator.branch_b_condition"),
        )''',
       '''        _blk = lanes.data.get("camel_comparator", {})
        return branch_condition_problems(
            _blk.get("branch_a_condition", ""),
            _blk.get("branch_b_condition", ""),
        )''')],
     "require() replaced by a defaulting read - a sentinel flows in AS A VALUE"),

    # ---- FIX 3's own self-directed mutants --------------------------------------------------
    ("SD-11", "OWN-3", INV,
     [("f\"branch_b_condition does not carry {what} ({phrase!r}). CONTEXT.md v1.9 \"",
       "f\"branch_b_condition does not carry {what} ({BRANCH_B_REQUIREMENTS!r}). CONTEXT.md v1.9 \"")],
     "the complaint quotes EVERY requirement instead of the one that failed"),
    ("SD-13", "OWN-6", MAIN,
     [('''    stale = invocation.branch_conditions_are_stale()
    say("  pre-registered branch conditions vs CONTEXT.md S8.5.1: "
        + ("OK - both keys agree with the law" if not stale else f"{len(stale)} PROBLEM(S)"))
    for problem in stale:
        say(f"    ! {problem}")''',
       '''    stale = invocation.branch_conditions_are_stale()
    del stale
    say("  pre-registered branch conditions vs CONTEXT.md S8.5.1: "
        "OK - both keys agree with the law")''')],
     "OF-118's call is KEPT and its result DISCARDED - a call is not a reader"),
    ("SD-14", "OWN-6", MAIN,
     [('''    say("  pre-registered branch conditions vs CONTEXT.md S8.5.1: "
        + ("OK - both keys agree with the law" if not stale else f"{len(stale)} PROBLEM(S)"))
    for problem in stale:
        say(f"    ! {problem}")''',
       '''    _n = len(stale)
    say("  pre-registered branch conditions vs CONTEXT.md S8.5.1: "
        "OK - both keys agree with the law")''')],
     "the result is READ but never reaches say() - the operator is still told nothing"),

    # ---- NEW-SURFACE, one per owned property ------------------------------------------------
    ("NS-1", "OWN-1", INV,
     [("        argv=[*common, replay_flag],", "        argv=[*common],")],
     "pass 2 drops --replay-with-policies, so the two passes become the same command"),
    ("NS-2", "OWN-2", LANES,
     [('  branch_a_condition: "IT RUNS: both passes',
       '  branch_a_condition: "the model id is still served AND both passes')],
     "Branch A's condition re-acquires the pre-Q-057 model-id clause"),
    ("NS-3", "OWN-3", INV,
     [('        "is not a cause",', '        "a cause",')],
     "requirement 2's phrase - the one REVIEW 3 never mutated - weakened further"),
    ("NS-4", "OWN-3", INV,
     [("f\"branch_b_condition does not carry {what} ({phrase!r}). CONTEXT.md v1.9 \"",
       "f\"branch_b_condition does not carry {what} ({what!r}). CONTEXT.md v1.9 \"")],
     "the complaint quotes the LABEL instead of the PHRASE"),
    ("NS-5", "OWN-3", INV,
     [("    lowered = branch_b_condition.lower()", "    lowered = branch_b_condition")],
     "the case fold is dropped, so the guard becomes case-sensitive against an "
     "upper-case config value"),
    ("NS-6", "OWN-4", CTX,
     [("**Branch B — the run does not complete, ON A CAUSE THAT HAS BEEN DIAGNOSED.**",
       "**Branch B — the run does not complete.**")],
     "the LAW alone is amended - config untouched. The failure must be AT THE LAW"),
    ("NS-7", "OWN-5", INV,
     [('SUPERSEDED_BRANCH_TRIGGER = "model id is still served"',
       'SUPERSEDED_BRANCH_TRIGGER = "model id is still served on tuesdays"')],
     "the superseded-trigger constant made unreachable"),
    ("NS-8", "OWN-6", INV,
     [('    except cfg.ConfigError as exc:\n        return [f"{type(exc).__name__}: {exc}"]',
       '    except cfg.ConfigError:\n        return []')],
     "the loader's refusal is SWALLOWED and reported as a clean pass"),
    ("NS-9", "OWN-7", LANES,
     [("  branch: TODO_C13_RUN1", '  branch: "A"')],
     "the branch is DECIDED from a chair - RUN-1's single-shot decision pre-empted"),
    ("NS-10", "OWN-8", BB,
     [('        if not APPENDIX.fullmatch(self.appendix):',
       '        if False and not APPENDIX.fullmatch(self.appendix):')],
     "the provenance gate stops requiring an appendix"),
    ("NS-11", "OWN-8", BB,
     [("TABLE_NUMBER = re.compile(r\"(Table|Figure) \\d+\")",
       "TABLE_NUMBER = re.compile(r\"(Tables?|Figures?) [\\d-]+\")")],
     "the table-number gate starts accepting the RANGE 'Tables 5-7' - Q-058's own shape"),
    ("NS-12", "OWN-9", BB,
     [('''_T2 = dict(
    table="Table 2",''', '''_T2 = dict(
    table="Table 5",''')],
     "the headline pair is re-attributed to Table 5 - the citation Q-058 ruled wrong"),
    # ⚠️ NO MUTANT WRITES INTO `vendor/`. The clone's vendored trees are NTFS JUNCTIONS to
    # the real ones (they are gitignored and therefore absent from any clone), so a write
    # there would land in the operator's repository. OWN-10 is attacked from the other side
    # instead - the PIN - which exercises the same guard and touches nothing outside the clone.
    ("NS-13", "OWN-10", "config/protocol.yaml",
     [("  camel_sha: f083b6b396399d3b3c7f2ddaf613a5945eaf32d8",
       "  camel_sha: 0000000000000000000000000000000000000000")],
     "the pinned CaMeL SHA no longer matches the checkout - the empty-diff proof is "
     "about a different CaMeL than PROTOCOL.md pre-registers"),

    # ---- ROUND 2 -----------------------------------------------------------------------------
    # NS-9b is the half of OWN-7 C13 ACTUALLY owns. NS-9 mutated `config/lanes.yaml`'s `branch`
    # key - the key RUN-1 is REQUIRED to write and C13 is FORBIDDEN to write - so it is
    # indistinguishable in the artefact from RUN-1 doing its job. This one mutates C13's OWN
    # code to write that key, which is the thing the chunk can and must prevent.
    ("NS-9b", "OWN-7", INV,
     [("def spec_timebox_minutes(context_md: str) -> int:",
       "def decide_the_branch_from_a_chair() -> None:\n"
       "    (cfg.repo_root() / \"config\" / \"lanes.yaml\").write_text(\n"
       "        \"branch: A\", encoding=\"utf-8\"\n"
       "    )\n"
       "\n"
       "\n"
       "def spec_timebox_minutes(context_md: str) -> int:")],
     "THIS PACKAGE writes config/ - the half of OWN-7 C13 actually owns"),

    # ⚠️ THE HARNESS'S OWN NEGATIVE CONTROL. A mutant that changes NO behaviour must SURVIVE.
    # If this one is reported KILLED, the harness is reporting kills that are not kills and
    # every other row in the table is void. It is included for the same reason a probe that
    # VOIDS the run is: a harness with no way to fail is not a measurement.
    ("NS-14", "CONTROL", INV,
     [("    passes = [", "    passes = [] or [")],
     "EXPECTED EQUIVALENT - a no-op restructure. It MUST survive or the harness is broken"),

    ("NS-15", "OWN-1", INV,
     [("        produces_pipeline_name=base_pipeline_name(model_string),",
       '        produces_pipeline_name="",')],
     "pass 1 stops declaring the pipeline name pass 2 replays - the log dependency "
     "Q-057 fact 4 is about"),
    ("NS-16", "OWN-9", BB,
     [('    appendix="Appendix B, Full results tables",\n'
       '    caption="Utility results',
       '    appendix="Appendix C, Baseline results",\n'
       '    caption="Utility results')],
     "the headline pair is moved to Appendix C - Q-058's exact defect, one field over"),
    ("NS-17", "OWN-8", BB,
     [("        if not self.base_model.strip():",
       "        if False and not self.base_model.strip():")],
     "the provenance gate stops requiring a base model"),
]


def apply_edits(path: Path, edits) -> bytes:
    original = path.read_bytes()
    text = original.decode("utf-8")
    for old, new in edits:
        if old not in text:
            raise LookupError("anchor not found in %s: %r" % (path.name, old[:70]))
        text = text.replace(old, new, 1)
    path.write_bytes(text.encode("utf-8"))
    return original


def main() -> int:
    print("C13 REVIEW 4 - MUTATION RUN")
    print("clone : %s" % CLONE)
    proc = sh(["python", "-c",
               "import whetstone_gate as w; from whetstone_gate import config as c; "
               "print(w.__file__); print(c.repo_root())"])
    seen = (proc.stdout or proc.stderr).strip().splitlines()
    print("whetstone_gate.__file__ = %s" % (seen[0] if seen else "?"))
    print("config.repo_root()      = %s" % (seen[1] if len(seen) > 1 else "?"))
    if seen and not seen[0].lower().startswith(str(CLONE).lower()):
        print("!! THE PACKAGE UNDER TEST IS NOT THE CLONE'S. Every result would be void.")
        return 3
    print("HEAD  : %s" % sh(["git", "rev-parse", "HEAD"]).stdout.strip())
    print("")

    t0 = time.time()
    control = sh(CONTROL)
    print("[CONTROL, before any mutation] rc=%d  %s  (%.0fs)"
          % (control.returncode, summarise(control), time.time() - t0))
    if control.returncode != 0:
        print("!! CONTROL IS NOT GREEN. The whole run would be uninterpretable. STOPPING.")
        return 2
    print("")

    rows = []
    for mid, own, relpath, edits, description in MUTANTS:
        if ONLY and mid not in ONLY:
            continue
        path = CLONE / relpath
        before = digest(path)
        try:
            original = apply_edits(path, edits)
        except LookupError as exc:
            print("[%-6s] %-7s ANCHOR MISSING -> %s" % (mid, own, exc))
            rows.append((mid, own, relpath, "ANCHOR-MISSING", "", description))
            continue
        after = digest(path)
        assert before != after, "%s: the mutation changed no bytes" % mid
        commit("mutant %s" % mid)

        t = time.time()
        run = sh(FAST)
        killed = run.returncode != 0
        line = summarise(run)

        # -- RESTORE BY WRITING THE ORIGINAL BYTES. Never `git checkout --`. ------------------
        path.write_bytes(original)
        restored = digest(path)
        commit("restore %s" % mid)
        ctl = sh(CONTROL)
        void = restored != before or ctl.returncode != 0

        verdict = "VOID" if void else ("KILLED" if killed else "SURVIVED")
        rows.append((mid, own, relpath, verdict, line, description))
        print("[%-6s] %-7s %-9s %-34s %s  (%.0fs)"
              % (mid, own, verdict, Path(relpath).name, line[:78], time.time() - t))
        if void:
            print("         !! restore digest %s vs original %s; post-restore control rc=%d"
                  % (restored, before, ctl.returncode))

    print("")
    print("SUMMARY")
    print("%-7s %-8s %-9s %s" % ("id", "own", "verdict", "file"))
    for mid, own, relpath, verdict, line, _ in rows:
        print("%-7s %-8s %-9s %s" % (mid, own, verdict, relpath))
    survivors = [r for r in rows if r[3] == "SURVIVED"]
    voids = [r for r in rows if r[3] == "VOID"]
    print("")
    print("%d mutant(s): %d KILLED, %d SURVIVED, %d VOID, %d ANCHOR-MISSING"
          % (len(rows), sum(1 for r in rows if r[3] == "KILLED"), len(survivors), len(voids),
             sum(1 for r in rows if r[3] == "ANCHOR-MISSING")))
    for r in survivors:
        print("  SURVIVOR %s (%s) %s - %s" % (r[0], r[1], r[2], r[5]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
