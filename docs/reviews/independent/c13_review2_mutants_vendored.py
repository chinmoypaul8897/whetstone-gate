"""C13 REVIEW 2, session 8c49c4d3 — mutation driver.

Applies one mutation to the COPY of the CaMeL tree in a fresh OS temp directory,
COMMITS it there (REVIEW 1 records that editing without committing produced three
false SURVIVORS, because the harness reads git blobs), runs the C13 suite, records
the failures, and resets the copy back to the pin.

Nothing in c:/Users/chinm/whetstone-gate is touched.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

MUT = Path(__file__).resolve().parent / "mut"
CAM = MUT / "vendor" / "camel-prompt-injection"
PIN = "f083b6b396399d3b3c7f2ddaf613a5945eaf32d8"
REPLAY = "src/camel/pipeline_elements/replay_privileged_llm.py"
PY = r"c:/Users/chinm/whetstone-gate/.venv/Scripts/python.exe"

PROPERTY_TESTS = {
    "test_run1_is_two_passes_and_the_second_replays_the_first",
    "test_both_passes_share_one_working_directory_and_the_plan_says_why",
    "test_the_live_log_path_is_located_by_ast_and_proved_reachable",
}


def git(*args, cwd=CAM):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed in {cwd}: {r.stderr}")
    return r.stdout


def reset_camel():
    git("reset", "--hard", "-q", PIN)
    git("clean", "-qfd")


def restore_first_party():
    subprocess.run(["git", "checkout", "--", "src", "config"], cwd=MUT,
                   capture_output=True, text=True, encoding="utf-8", errors="replace")


def run_tests(paths=("tests/test_c13_camel_comparator.py",)):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(MUT / "src")
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([PY, "-m", "pytest", *paths, "-q", "--no-header", "-p", "no:cacheprovider"],
                       cwd=MUT, capture_output=True, text=True, env=env,
                       encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    failed = sorted(set(re.findall(r"^(?:FAILED|ERROR) \S+::(\w+)", out, re.M)))
    m = re.search(r"(\d+) failed", out)
    nf = int(m.group(1)) if m else 0
    m = re.search(r"(\d+) passed", out)
    npass = int(m.group(1)) if m else 0
    ne = len(re.findall(r"^ERROR ", out, re.M))
    return {"rc": r.returncode, "failed": nf, "passed": npass, "errors": ne,
            "names": failed, "tail": out.strip().splitlines()[-1] if out.strip() else ""}


def mutate_replay(fn):
    """fn(text) -> text, applied to the vendored replay file, then committed."""
    p = CAM / REPLAY
    # The working tree is CRLF here (core.autocrlf=true) while the BLOB is LF.
    # Normalise to LF, mutate, write LF: git stores the identical blob either way,
    # so the only diff against the pin is the mutation itself.
    text = p.read_bytes().decode("utf-8").replace("\r\n", "\n")
    new = fn(text)
    if new == text:
        raise SystemExit("MUTATION WAS A NO-OP - the pattern did not match. Aborting.")
    p.write_bytes(new.encode("utf-8"))
    git("add", REPLAY)
    git("-c", "user.email=rev2@local", "-c", "user.name=rev2", "commit", "-q", "-m", "mutant")
    return git("rev-parse", "HEAD").strip()


def repin(sha):
    """Point config/protocol.yaml's camel_sha at the mutated HEAD, so the pin guard
    stops firing and the PROPERTY is what the run measures."""
    p = MUT / "config" / "protocol.yaml"
    b = p.read_bytes()
    b2 = b.replace(PIN.encode(), sha.encode())
    assert b2 != b
    p.write_bytes(b2)


MUTANTS = {}


def m(name):
    def deco(f):
        MUTANTS[name] = f
        return f
    return deco


@m("M15")
def _m15(t):
    """Delete the three DEAD helpers replay_user_task / replay_suite / replay_benchmark."""
    i = t.index("def replay_user_task(")
    # they run to the end of the file at the pin; verify nothing else follows
    return t[:i].rstrip() + "\n"


@m("M16-abs-posix")
def _m16a(t):
    return t.replace('        Path("logs")\n', '        Path("/var/logs")\n', 1)


@m("M16-abs-win")
def _m16b(t):
    return t.replace('        Path("logs")\n', '        Path("C:/logs")\n', 1)


@m("M16-resolve")
def _m16c(t):
    return t.replace('        Path("logs")\n', '        Path("logs").resolve()\n', 1)


@m("M16-dunder-file")
def _m16d(t):
    """REVIEW 1's own literal M16 form."""
    return t.replace('        Path("logs")\n',
                     '        Path(__file__).resolve().parent / "logs"\n', 1)


@m("M17")
def _m17(t):
    return t.replace("trace_path.read_text()", "'{}'", 1)


@m("M17-glob")
def _m17b(t):
    """The live read becomes a GLOB — a silent zero, which is the failure mode INC-39
    says is FALSE for the live path. crashes_loudly must go False."""
    return t.replace(
        "    execution_trace = TaskResults.model_validate_json(trace_path.read_text())",
        "    execution_trace = TaskResults.model_validate_json("
        "next(iter(trace_path.glob('*')), None) or '{}')", 1)


def main():
    which = sys.argv[1]
    also_repin = "--repin" in sys.argv
    reset_camel()
    restore_first_party()
    base = git("rev-parse", "HEAD").strip()
    assert base == PIN, base
    sha = mutate_replay(MUTANTS[which])
    if also_repin:
        repin(sha)
    res = run_tests()
    res["mutant"] = which
    res["repinned"] = also_repin
    res["camel_head"] = sha
    res["property_tests_failed"] = sorted(set(res["names"]) & PROPERTY_TESTS)
    res["other_failed"] = sorted(set(res["names"]) - PROPERTY_TESTS)
    print(json.dumps(res, indent=2))
    reset_camel()
    restore_first_party()


if __name__ == "__main__":
    main()
