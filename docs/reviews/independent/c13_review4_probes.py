"""C13 REVIEW 4 - PHASE 2 probes.

Everything this review measures that is not a mutant.  Written AFTER the seal, and it says so.

Two things it does that matter:

  * it DIFFS the project's `branch_condition_problems` against the Phase-1 scoped
    reimplementation's law-derived predicate, over the sealed 24 vectors PLUS the vectors
    that discriminate the two derivations.  A divergence is a finding, whichever side is
    right;
  * it scans the C13 test file for the INC-50/INC-55 SHAPE - an assertion whose expected
    value is read out of the same module-level object that produced the actual value - and
    prints every hit, because criterion S-5 pre-committed the polarity NO.

It imports the project on purpose (this is Phase 2) and it imports the Phase-1
reimplementation as a module, so the two predicates are compared rather than described.
"""

from __future__ import annotations

import ast
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "src"))

from whetstone_gate import config as cfg  # noqa: E402
from whetstone_gate.camel_comparator import invocation  # noqa: E402

_spec = importlib.util.spec_from_file_location("c13r4reimpl", HERE / "c13_review4_reimpl.py")
_mod = importlib.util.module_from_spec(_spec)
sys.modules.pop("whetstone_gate", None)  # the reimpl asserts it is not imported...
_saved = {k: v for k, v in sys.modules.items() if k.startswith("whetstone_gate")}
for k in list(_saved):
    del sys.modules[k]
_spec.loader.exec_module(_mod)
sys.modules.update(_saved)

OUT: list[str] = []


def say(line: str = "") -> None:
    OUT.append(line)


def rule(title: str) -> None:
    say("")
    say("-- %s %s" % (title, "-" * max(0, 74 - len(title))))


# ==============================================================================================
def probe_reimpl_diff() -> None:
    rule("A. THE PROJECT'S PREDICATE vs THE PHASE-1 LAW-DERIVED ONE")
    context_md = (REPO / "CONTEXT.md").read_text(encoding="utf-8")
    derived, section, _ = _mod.derive_requirements(context_md)
    lanes = cfg.load("lanes")
    cond_a = lanes.require("camel_comparator.branch_a_condition")
    cond_b = lanes.require("camel_comparator.branch_b_condition")

    say("   law-derived requirements (Phase 1): %d" % len(derived))
    for label, phrase in derived:
        say("     %-46s %r" % (label, phrase))
    say("   project's BRANCH_B_REQUIREMENTS   : %d" % len(invocation.BRANCH_B_REQUIREMENTS))
    for label, phrase in invocation.BRANCH_B_REQUIREMENTS:
        say("     %-46s %r" % (label, phrase))
    say("")

    vectors = _mod.build_vectors(derived)
    agree = disagree = 0
    for vid, desc, cond, _expected in vectors:
        mine = len(_mod.branch_b_problems(cond, derived))
        theirs = len(invocation.branch_condition_problems(cond_a, cond))
        if mine == theirs:
            agree += 1
        else:
            disagree += 1
            say("   XX %-4s mine=%d theirs=%d  %s" % (vid, mine, theirs, desc))
    say("   sealed vectors: %d agree, %d disagree (of %d)" % (agree, disagree, len(vectors)))
    say("")

    say("   -- the DISCRIMINATING vectors, added in Phase 2 to separate the two derivations --")
    strong = cond_b
    discriminators = [
        ("D1", "the law's clause replaced by a DIFFERENT 'is not a cause' sentence",
         strong.replace("'It errored' is not a cause", "A provider timeout is not a cause")),
        ("D2", "the law's clause replaced by 'a slow network is not a cause'",
         strong.replace("'It errored' is not a cause", "a slow network is not a cause")),
        ("D3", "'it errored' deleted, the rest of the sentence kept",
         strong.replace("'It errored' is not a cause", "that is not a cause")),
    ]
    for did, desc, cond in discriminators:
        mine = _mod.branch_b_problems(cond, derived)
        theirs = invocation.branch_condition_problems(cond_a, cond)
        verdict = "AGREE" if len(mine) == len(theirs) else "DIVERGE"
        say("   %-3s %-7s mine=%d theirs=%d  %s" % (did, verdict, len(mine), len(theirs), desc))
        if len(mine) != len(theirs):
            say("        mine  : %s" % (mine[0][:110] if mine else "(accepted)"))
            say("        theirs: %s" % (theirs[0][:110] if theirs else "(accepted)"))


# ==============================================================================================
def probe_shape_scan() -> None:
    rule("B. S-5 - THE INC-50/INC-55 SHAPE, SCANNED RATHER THAN EYEBALLED")
    say("   Looking for: an assertion in tests/test_c13_camel_comparator.py whose EXPECTED")
    say("   side reads a module-level object of `invocation`/`branch_b` that also produced")
    say("   the ACTUAL side - so both move together and the assertion cannot fail.")
    path = REPO / "tests" / "test_c13_camel_comparator.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def module_attrs(node) -> set[str]:
        found = set()
        for n in ast.walk(node):
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name):
                if n.value.id in {"invocation", "branch_b", "vendor", "claims", "predictions"}:
                    found.add(f"{n.value.id}.{n.attr}")
        return found

    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assert):
            continue
        test = node.test
        # only comparisons and `any(... in ...)` shapes carry an expected/actual split
        left_attrs = module_attrs(test)
        if len(left_attrs) < 1:
            continue
        # the shape: the SAME module-level NAME appears more than once in one assertion,
        # or a call to a module predicate is compared against a module-level constant.
        names = [
            f"{n.value.id}.{n.attr}"
            for n in ast.walk(test)
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
            and n.value.id in {"invocation", "branch_b"}
        ]
        calls = {
            f"{n.func.value.id}.{n.func.attr}"
            for n in ast.walk(test)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and isinstance(n.func.value, ast.Name) and n.func.value.id in {"invocation", "branch_b"}
        }
        constants = {n for n in names if n.split(".")[1].isupper()} | {
            n for n in names if n.split(".")[1].isupper() or n.split(".")[1][0].isupper()
        }
        if calls and constants:
            hits.append((node.lineno, sorted(calls), sorted(constants)))
        elif len(set(names)) == 1 and len(names) > 1:
            hits.append((node.lineno, [], sorted(set(names))))

    if not hits:
        say("   RESULT: 0 hits. S-5's pre-committed polarity (NO occurrence) HOLDS.")
    else:
        say("   RESULT: %d candidate hit(s) from a DELIBERATELY OVER-BROAD scanner." % len(hits))
        say("   Each is judged individually below; a candidate is not a finding.")
        for lineno, calls, consts in hits:
            src = path.read_text(encoding="utf-8").splitlines()[lineno - 1].strip()
            say("     line %-5d call(s)=%s const(s)=%s" % (lineno, calls, consts))
            say("        %s" % src[:110])
    say("")
    say("   And the two assertions INC-55 is about, searched for by their own text:")
    text = path.read_text(encoding="utf-8")
    for needle in (
        "len(undiagnosed) == len(invocation.BRANCH_B_REQUIREMENTS)",
        "for what, _ in invocation.BRANCH_B_REQUIREMENTS:",
    ):
        live = [
            i + 1
            for i, ln in enumerate(text.splitlines())
            if needle in ln and not ln.strip().startswith("#")
        ]
        commented = [
            i + 1
            for i, ln in enumerate(text.splitlines())
            if needle in ln and ln.strip().startswith("#")
        ]
        say("     %-58s live=%s quoted-in-a-comment=%s" % (needle[:56], live, commented))


# ==============================================================================================
def probe_of_items() -> None:
    rule("C. OF-115, OF-117, OF-118, OF-119")
    test_src = (REPO / "tests" / "test_c13_camel_comparator.py").read_text(encoding="utf-8")
    context_md = (REPO / "CONTEXT.md").read_text(encoding="utf-8")

    say("   OF-115  'OF-104' occurrences in the C13 test file : %d  (F-115a expected 0)"
        % test_src.count("OF-104"))
    say("   OF-115  'OF-62' occurrences                        : %d" % test_src.count("OF-62"))
    say("   OF-115  'Q-079' occurrences                        : %d" % test_src.count("Q-079"))

    # F-119b - the window width, MEASURED. The prediction sealed in Phase 1 was ~3,592 chars.
    lines = context_md.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("### 8.5.1 "))
    end_new = next(i for i in range(start + 1, len(lines))
                   if lines[i].startswith("### 8.5.2 ") or lines[i].startswith("## "))
    end_old = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
    win_new = "\n".join(lines[start:end_new])
    win_old = "\n".join(lines[start:end_old])
    say("")
    say("   OF-119  window NOW  ('### 8.5.2 ' or '## ')  : %5d chars, ends at line %d (%r)"
        % (len(win_new), end_new + 1, lines[end_new][:34]))
    say("   OF-119  window BEFORE ('## ' only)           : %5d chars, ends at line %d (%r)"
        % (len(win_old), end_old + 1, lines[end_old][:34]))
    say("   OF-119  narrowing                            : %5d chars removed (%.0f%% of the old)"
        % (len(win_old) - len(win_new), 100.0 * (len(win_old) - len(win_new)) / len(win_old)))
    say("   F-119b  SEALED PREDICTION was ~3,592 chars, 'within 10%% of 3,592'  ->  measured "
        "%d, delta %+.1f%%" % (len(win_new), 100.0 * (len(win_new) - 3592) / 3592))
    flat = re.sub(r"\s+", " ", win_new).lower()
    say("   F-119c  all four phrases inside the narrowed window: %s"
        % all(p in flat for _, p in invocation.BRANCH_B_REQUIREMENTS))
    say("   OF-119  'policy coverage' (S8.5.2's P3) in the narrowed window: %s  (must be False)"
        % ("policy coverage" in flat))

    # OF-118, against the RULE OF DECISION pre-committed in the seal S4.
    say("")
    say("   OF-118  the pre-committed rule of decision, part by part:")
    from whetstone_gate import camel_comparator as package
    say("     (a) exported            : %s"
        % ("branch_conditions_are_stale" in package.__all__))
    say("     (a) export IS the thing : %s"
        % (package.branch_conditions_are_stale is invocation.branch_conditions_are_stale))
    main_src = (REPO / "src" / "whetstone_gate" / "camel_comparator" / "__main__.py").read_text(
        encoding="utf-8")
    tree = ast.parse(main_src)
    bound, said = set(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
            f = n.value.func
            nm = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if nm == "branch_conditions_are_stale":
                bound |= {t.id for t in n.targets if isinstance(t, ast.Name)}
        if isinstance(n, ast.Call):
            f = n.func
            if (f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)) == "say":
                said |= {i.id for i in ast.walk(n)
                         if isinstance(i, ast.Name) and isinstance(i.ctx, ast.Load)}
    say("     (b) result BOUND        : %s" % sorted(bound))
    say("     (b) reaches say()       : %s" % sorted(bound & said))
    say("     (c) an input on which the printed line CHANGES:")
    good = invocation.branch_condition_problems(
        cfg.load("lanes").require("camel_comparator.branch_a_condition"),
        cfg.load("lanes").require("camel_comparator.branch_b_condition"))
    bad = invocation.branch_condition_problems("the model id is still served", "no condition")
    say("         real config -> %d problem(s) -> prints 'OK - both keys agree with the law'"
        % len(good))
    say("         a broken pair -> %d problem(s) -> prints '%d PROBLEM(S)' and then each one"
        % (len(bad), len(bad)))
    say("     ⚠ RESIDUAL, stated rather than glossed: main()'s RETURN CODE is unchanged by")
    say("       `stale`. `python -m whetstone_gate.camel_comparator` exits 0 with a stale")
    say("       condition; only the printed line moves. FIX 3 names that omission in terms.")


# ==============================================================================================
def probe_standing() -> None:
    rule("D. STANDING PROPERTIES (T-1..T-10)")

    def sh(args, cwd=REPO):
        return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True,
                              encoding="utf-8", errors="replace")

    say("   T-3  git status --porcelain tests/goldens/  : %r"
        % sh(["git", "status", "--porcelain", "tests/goldens/"]).stdout.strip())
    blob = sh(["git", "rev-parse", "HEAD:CONTEXT.md"]).stdout.strip()
    data = (REPO / "CONTEXT.md").read_bytes()
    say("   T-4  CONTEXT.md blob  : %s" % blob)
    say("        REVIEW 3 measured: 8e820384afbb1de7de3892eb6b90a8e6dce1f378  -> %s"
        % ("IDENTICAL" if blob == "8e820384afbb1de7de3892eb6b90a8e6dce1f378" else "MOVED"))
    say("        bytes %d  LF %d  CR %d  TAB %d  (REVIEW 3: 224,645 / 2,361 / 0 / 0)"
        % (len(data), data.count(b"\n"), data.count(b"\r"), data.count(b"\t")))
    ver = re.search(r"v1\.\d+", (REPO / "CONTEXT.md").read_text(encoding="utf-8")[:4000])
    say("        version line says : %s" % (ver.group(0) if ver else "?"))
    say("   T-5  git tag -l       : %s" % " ".join(sh(["git", "tag", "-l"]).stdout.split()))
    say("        prereg-v1 resolves: %s"
        % (sh(["git", "rev-parse", "--verify", "prereg-v1"]).returncode == 0))
    evals = list((REPO / "evals").rglob("*")) if (REPO / "evals").exists() else []
    say("   T-6  files under evals/: %d" % len([p for p in evals if p.is_file()]))
    lanes_txt = (REPO / "config" / "lanes.yaml").read_text(encoding="utf-8")
    for key in ("branch_a_condition", "branch_b_condition"):
        line = next(ln for ln in lanes_txt.splitlines() if ln.strip().startswith(key + ":"))
        has = "diagnos" in line.lower()
        say("   T-7  %-19s carries a diagnosis word: %-5s" % (key, has))
    say("   T-9  Q-074's fifth site - 'Tables 5-7' in tests/test_lanes_operator_placeholders.py:")
    hits = sh(["git", "grep", "-n", "Tables 5", "--", "tests/", "src/", "config/", "PROCESS.md"])
    for ln in (hits.stdout or "").splitlines():
        say("        %s" % ln[:150])
    if not (hits.stdout or "").strip():
        say("        (no hits)")


def main() -> int:
    say("C13 REVIEW 4 - PHASE 2 PROBES  (written AFTER the seal 9e16d87)")
    say("repo: %s" % REPO)
    probe_reimpl_diff()
    probe_shape_scan()
    probe_of_items()
    probe_standing()
    text = "\n".join(OUT) + "\n"
    sys.stdout.write(text.encode("ascii", "replace").decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
