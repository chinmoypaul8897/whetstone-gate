"""C13 REVIEW 2, session 8c49c4d3 — FIRST-PARTY mutation driver.

Mutates src/whetstone_gate/camel_comparator/* inside the temp clone only, runs the
C13 suite, records which tests die, and restores. Nothing in the real repo is touched.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

MUT = Path(__file__).resolve().parent / "mut"
PY = r"c:/Users/chinm/whetstone-gate/.venv/Scripts/python.exe"
BB = MUT / "src" / "whetstone_gate" / "camel_comparator" / "branch_b.py"
VEND = MUT / "src" / "whetstone_gate" / "camel_comparator" / "vendor.py"
INV = MUT / "src" / "whetstone_gate" / "camel_comparator" / "invocation.py"


def restore():
    subprocess.run(["git", "checkout", "--", "src", "config", "tests"], cwd=MUT,
                   capture_output=True, text=True, encoding="utf-8", errors="replace")


def run_tests():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(MUT / "src")
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([PY, "-m", "pytest", "tests/test_c13_camel_comparator.py",
                        "-q", "--no-header", "-p", "no:cacheprovider"],
                       cwd=MUT, capture_output=True, text=True, env=env,
                       encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    names = sorted(set(re.findall(r"^(?:FAILED|ERROR) \S+::([\w\[\]\-.]+)", out, re.M)))
    base = sorted({n.split("[")[0] for n in names})
    m = re.search(r"(\d+) failed", out)
    nf = int(m.group(1)) if m else 0
    m = re.search(r"(\d+) passed", out)
    npass = int(m.group(1)) if m else 0
    return {"failed": nf, "passed": npass, "distinct_test_functions": base,
            "tail": out.strip().splitlines()[-1] if out.strip() else ""}


def edit(path, old, new, count=1):
    b = path.read_bytes().decode("utf-8")
    if old not in b:
        raise SystemExit(f"PATTERN NOT FOUND in {path.name}: {old[:70]!r}")
    nb = b.replace(old, new, count)
    if nb == b:
        raise SystemExit("no-op mutation")
    path.write_bytes(nb.encode("utf-8"))


MUTANTS = {}


def m(name, desc):
    def deco(f):
        MUTANTS[name] = (f, desc)
        return f
    return deco


@m("D1", "delete assert_provenance(HEADLINE_FIGURES) from render_branch_b")
def _d1():
    edit(BB, "    assert_provenance(HEADLINE_FIGURES)\n", "")


@m("D2", "delete assert_provenance(CITED_TABLE_FIGURES) from render_branch_b")
def _d2():
    edit(BB, "    assert_provenance(CITED_TABLE_FIGURES)\n", "")


@m("D3", "delete assert_provenance(TABLE_4_BANKING_FIGURES) from render_branch_b")
def _d3():
    edit(BB, "    assert_provenance(TABLE_4_BANKING_FIGURES)\n", "")


@m("D-all", "delete ALL THREE assert_provenance calls from render_branch_b")
def _dall():
    for t in ("HEADLINE_FIGURES", "CITED_TABLE_FIGURES", "TABLE_4_BANKING_FIGURES"):
        edit(BB, f"    assert_provenance({t})\n", "")


# ---------------------------------------------------------------- NEW SURFACE
@m("N1", "ceiling gate: is_a_count figure with NO ceiling is accepted")
def _n1():
    edit(BB, "        if self.is_a_count and not self.ceiling.strip():",
             "        if False and self.is_a_count and not self.ceiling.strip():")


@m("N2", "ceiling gate: is_a_count figure with a ceiling but NO SOURCE is accepted")
def _n2():
    edit(BB, "        if self.is_a_count and not self.ceiling_source.strip():",
             "        if False and self.is_a_count and not self.ceiling_source.strip():")


@m("N3", "per-table attribution SWAPPED: Table 4's ceiling sourced to Figure 11")
def _n3():
    edit(BB, "        ceiling_source=CEILING_SOURCE_F9,", "        ceiling_source=CEILING_SOURCE_F11,")


@m("N4", "per-table attribution SWAPPED the other way: Table 7's ceiling sourced to Figure 9")
def _n4():
    edit(BB, "    ceiling_source=CEILING_SOURCE_F11,\n)", "    ceiling_source=CEILING_SOURCE_F9,\n)")


@m("N5", "banking_rows loses the SUITE filter - the quiet-collapse class the fix reports")
def _n5():
    edit(BB, "        and figure.suite.lower() == \"banking\"", "        and True")


@m("N6", "banking_rows loses the TABLE key - five suites collapse across tables")
def _n6():
    edit(BB, "        if figure.table == table\n", "        if True\n")


@m("N7", "p2_holds_for: 'CaMeL with policies blocks it' weakened to 'no-policies is non-zero'")
def _n7():
    edit(BB, 'return not rows["CaMeL (no policies)"].startswith("0") and rows["CaMeL"].startswith("0")',
             'return not rows["CaMeL (no policies)"].startswith("0")')


@m("N8", "reachability refusal deleted: 'exactly one reachable' becomes 'at least one'")
def _n8():
    edit(INV, "    if len(live) != 1:", "    if len(live) < 1:")


@m("N9", "reachability walk neutered: every function counts as reachable")
def _n9():
    edit(INV, "    reachable = _reachable_from(functions, caller)",
              "    reachable = set(functions)")


@m("N10", "_is_relative_literal drops the POSIX rule (Windows-only check)")
def _n10():
    edit(INV, "        PurePosixPath(root).is_absolute() or PureWindowsPath(root).is_absolute()",
              "        PureWindowsPath(root).is_absolute()")


@m("N11", "_is_relative_literal drops the WINDOWS rule (POSIX-only check)")
def _n11():
    edit(INV, "        PurePosixPath(root).is_absolute() or PureWindowsPath(root).is_absolute()",
              "        PurePosixPath(root).is_absolute()")


@m("N12", "_absolutises always False - the .resolve() form stops being noticed")
def _n12():
    edit(INV, "def _absolutises(func: ast.FunctionDef, name: str) -> bool:",
              "def _absolutises(func: ast.FunctionDef, name: str) -> bool:\n    return False")


@m("N13", "crashes_loudly: glob counted as a loud read, so the failure mode inverts")
def _n13():
    edit(INV, 'return self.read_call in {"read_text", "read_bytes", "open"}',
              'return self.read_call in {"read_text", "read_bytes", "open", "glob"}')


@m("N14", "TABLE_NUMBER fullmatch -> match, so 'Table 5-7' style ranges pass again")
def _n14():
    edit(BB, "if not TABLE_NUMBER.fullmatch(self.table):", "if not TABLE_NUMBER.match(self.table):")


def main():
    which = sys.argv[1]
    restore()
    fn, desc = MUTANTS[which]
    fn()
    res = run_tests()
    res["mutant"] = which
    res["description"] = desc
    print(json.dumps(res, indent=2))
    restore()


if __name__ == "__main__":
    main()
