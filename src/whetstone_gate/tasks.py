"""``python -m whetstone_gate.tasks <target>`` — the make-free entry point.

`CONTEXT.md` §16 settles the entry-point question in two halves, and neither is optional:

  1. **Every `make` target is one line that delegates here.** The Makefile contains no
     build logic, so a reviewer with no ``make`` — on any OS — runs
     ``python -m whetstone_gate.tasks eval`` and gets a byte-identical result. §20's
     *"one command"* box is satisfied by **either** form.
  2. **C0 installs a `make` shim** on the operator's machine, so ``make eval`` works here
     too.

Targets: ``test`` · ``eval`` · ``selftest`` · ``check-prereg`` · ``check-roles``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from . import check_roles as _check_roles
from . import config as cfg
from ._console import say

TARGETS = ("test", "eval", "selftest", "check-prereg", "check-roles")

#: ⚠️ **THE RUN DIRECTORY `make eval` READS, AND WHY IT IS A LITERAL, NOT A CONFIG KEY.**
#: `CONTEXT.md` §16 names ``evals/results/`` as the raw per-episode JSON, and the
#: assembler's own contract is ``<run-dir>/run.json`` plus ``<arm>/<episode>.json``.
#: This is a repository PATH, not one of §8.6's spec-specified values, so hard rule 9's
#: *"every spec-specified value lives in `config/`"* does not reach it — and `config/`
#: is a FROZEN pre-registration artefact that may not gain a key. `QUESTIONS.md` Q-131.
EVAL_RUN_DIR = "evals/results"


def _pytest(*args: str) -> int:
    """Run pytest in-process-adjacent, from the repository root."""
    return subprocess.run(
        [sys.executable, "-m", "pytest", *args], cwd=cfg.repo_root()
    ).returncode


# --------------------------------------------------------------------------------------


def task_test() -> int:
    """The unit suite.

    ⚠️ ``check-prereg`` runs **inside** this target, per hard rule 9 — the pre-registration
    check belongs to both ``make test`` and ``make eval``, not to a ceremony nobody runs.

    ``operator_gate`` tests are **deselected here and run by `make selftest`**, and the
    count is printed rather than hidden. They are pre-spend readiness gates that are
    *supposed* to be red until an operator action lands; failing the unit suite on them
    would mean the suite could never be green before 31 August, and a suite nobody can
    make green is a suite nobody reads. See QUESTIONS.md Q-009.
    """
    say("── check-prereg (hard rule 9: runs inside both `test` and `eval`) ─────────────")
    prereg = task_check_prereg()
    say()

    outstanding = cfg.outstanding_sentinels()
    operator_owed = [s for s in outstanding if s[2] == "TODO_OPERATOR"]
    if operator_owed:
        say("── DESELECTED FROM THIS TARGET, NOT HIDDEN ───────────────────────────────────")
        say(f"  {len(operator_owed)} value(s) in config/ still await the OPERATOR:")
        for name, dotted, _ in operator_owed:
            say(f"    · {name}.yaml : {dotted}")
        say("  `make selftest` runs the gate that FAILS on these. No token may be spent")
        say("  until they are resolved. See QUESTIONS.md Q-006.")
        say()

    say("── unit suite ────────────────────────────────────────────────────────────────")
    rc = _pytest("-q", "-m", "not operator_gate")
    return rc or prereg


def task_selftest() -> int:
    """The spend-free self-test — everything that must be true **before a token is spent**.

    `CONTEXT.md` §13.5(7): *"Before any token is spent, a deterministic self-test asserts
    that every documented Razorpay error in `RAZORPAY_SEMANTICS.md` fires in the mock
    world."* That oracle arrives with C1/C4. **Today this target is the operator-gate
    tier**, and it is RED by design while the Google API model ids are placeholders — which
    is correct, because no token may be spent against a guessed model id.
    """
    say("── selftest — the pre-spend gate ─────────────────────────────────────────────")
    say("  Scope today: the operator-readiness gates.")
    say("  C1/C4 add the RAZORPAY_SEMANTICS.md oracle — every documented Razorpay error")
    say("  must fire in the mock world before a single token is spent.")
    say()
    return _pytest("-q", "-m", "operator_gate")


def task_check_prereg() -> int:
    """Recompute the SHA-256 of every ``config/`` file's **git blob** against `PROTOCOL.md`.

    ⚠️ The digest is taken from the **git object** (``git show <ref>:<path>``), never from
    working-tree bytes. On this machine ``core.autocrlf`` is ``true`` system-wide, so a
    file committed with LF checks out as CRLF and hashes differently; a fingerprint
    published from a working tree would fail verification for every reviewer on Linux or
    macOS — silently, at the moment of judging. (`PROCESS.md` §6a.)

    Before `prereg-v1` there is nothing to check against, and this reports NOT-YET-FROZEN
    and succeeds. **That is not a pass**: it is the honest statement that the freeze has
    not happened. C18 wires the PASS/FAIL line into `RESULTS.md`.
    """
    root = cfg.repo_root()
    protocol = root / "PROTOCOL.md"
    config_files = sorted(p.name for p in (root / "config").glob("*.yaml"))

    say(f"  config/ holds {len(config_files)} file(s): {', '.join(config_files)}")

    if not protocol.is_file():
        say("  STATUS: NOT-YET-FROZEN — PROTOCOL.md does not exist.")
        say("          It is written by C14, which lists every config/ file with the")
        say("          SHA-256 of its GIT BLOB. Until then there is no manifest to")
        say("          recompute against. This is not a PASS; it is 'not yet'.")
        return 0

    try:
        tag = subprocess.run(
            ["git", "rev-parse", "--verify", "-q", "prereg-v1^{commit}"],
            cwd=root, capture_output=True, text=True,
        )
    except OSError as exc:  # pragma: no cover - git is a hard prerequisite
        say(f"  ERROR: could not run git: {exc}")
        return 1

    if tag.returncode != 0:
        say("  STATUS: NOT-YET-FROZEN — the `prereg-v1` tag does not resolve.")
        say("          PROTOCOL.md exists but the freeze has not been cut.")
        return 0

    say(f"  prereg-v1 resolves to {tag.stdout.strip()[:12]}")
    say("  STATUS: the manifest comparison lands with C14, which authors PROTOCOL.md's")
    say("          SHA-256 table. C0 wires the target; C14 gives it something to check.")
    return 0


def task_check_roles() -> int:
    """The repository's structural invariants. See :mod:`whetstone_gate.check_roles`."""
    return _check_roles.run()


def task_eval() -> int:
    """Regenerate every number in `RESULTS.md` **from the stored ledgers**.

    ⚠️ The scope of "regenerates" is exact, because the looser claim is false (hard rule
    10). The **world, the ledger schema, the scorer and the replay** are byte-identical
    from the same seed and are tested to be. **Model output is not** — the attacker runs
    at temperature 0.7 against a hosted provider. So the claim is *"every number
    regenerates from the stored ledgers"*, which is true, checkable, and enough. Do not
    let this command, or the README, imply that re-running the models reproduces the run.

    ⚠️ **IT SPENDS NO TOKEN AND ASKS NO MODEL ANYTHING.** It replays committed JSON.

    ⚠️ **WITH NO RUN DIRECTORY IT REFUSES AND EXITS NON-ZERO** — never 0. See the body.
    """
    say("── check-prereg (hard rule 9: runs inside both `test` and `eval`) ─────────────")
    prereg = task_check_prereg()
    say()

    root = cfg.repo_root()
    run_dir = root / EVAL_RUN_DIR
    manifest = run_dir / "run.json"

    say("── eval ──────────────────────────────────────────────────────────────────────")
    if not manifest.is_file():
        why = "the directory does not exist" if not run_dir.is_dir() else "it holds no run.json"
        say(f"  NO SCORED RUN EXISTS YET — {EVAL_RUN_DIR}/: {why}.")
        say("  There is nothing to regenerate FROM. The run directory is the sweep's own")
        say("  output; until it exists this command has no stored ledgers to replay, and")
        say("  CONTEXT.md §20's one-command claim is PENDING THE RUN, not satisfied.")
        say()
        say("  ⚠️ THIS IS A REFUSAL AND IT EXITS NON-ZERO ON PURPOSE. A green `make eval`")
        say("  with no run behind it is precisely the overclaim this project fails other")
        say("  entrants for. `check-prereg` FAILS OPEN today (OF-185 / Q-100); that defect")
        say("  is deliberately NOT copied into the target CONTEXT.md §20 names.")
        return 2

    say(f"  run directory : {EVAL_RUN_DIR}/")
    say("  Replaying the STORED LEDGERS. No model is called and no token is spent:")
    say("  tests/test_c18_results.py asserts the assembler's import closure holds no")
    say("  model client two independent ways, with a planted leaky module firing both.")
    say()

    # Local import, the convention `results/__main__.py` already uses for `trail`: it keeps
    # this module's module-level import list free of the assembler's whole dependency graph.
    from .results.__main__ import main as _assemble

    rc = _assemble(
        [str(run_dir), "--root", str(root), "--output", str(root / "RESULTS.md")]
    )

    say()
    if rc == 0:
        say("  RESULTS.md written. Every number in it came out of committed JSON, and the")
        say("  pre-registration check's PASS/FAIL line is carried INTO that file by the")
        say("  assembler itself, as hard rule 9 requires.")
    else:
        say("  ⚠️ THE ASSEMBLER REFUSED and nothing was written — see the REFUSED line")
        say("  above. A missing block is a refusal naming its owner, never a filled-in")
        say("  default: a RESULTS.md assembled over an absent block would look complete.")
    return max(rc, prereg)


# --------------------------------------------------------------------------------------

_DISPATCH = {
    "test": task_test,
    "eval": task_eval,
    "selftest": task_selftest,
    "check-prereg": task_check_prereg,
    "check-roles": task_check_roles,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m whetstone_gate.tasks",
        description=(
            "The make-free entry point. Every `make` target is a one-line delegation "
            "here, so a reviewer with no `make`, on any OS, gets an identical result."
        ),
    )
    parser.add_argument("target", choices=TARGETS, help="the target to run")
    args = parser.parse_args(argv)
    return _DISPATCH[args.target]()


if __name__ == "__main__":
    raise SystemExit(main())
