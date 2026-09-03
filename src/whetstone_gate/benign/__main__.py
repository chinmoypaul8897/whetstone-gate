"""**THE COMMAND LINE — and every flag that has to be typed rather than assumed.**

    python -m whetstone_gate.benign --dry-run \\
      --seed 2001 \\
      --s3-binding authorization-is-the-payment \\
      --turn-budget 20 \\
      --temperature 0.7

⚠️ **NEITHER MODE IS THE DEFAULT.** ``--dry-run`` and ``--spend-real-tokens`` are one
required, mutually exclusive group, so *"no argument spends money by default"* is a property
of the parser rather than a rule somebody has to remember. This is
``driver/__main__.py``'s shape, deliberately.

--------------------------------------------------------------------------------------
⚠️ WHAT A REAL RUN REFUSES, AND WHY EACH REFUSAL IS THE OUTCOME
--------------------------------------------------------------------------------------

**1. A PROVIDER CLIENT, WHICH THIS PACKAGE DELIBERATELY DOES NOT SHIP.** The client is an
injected two-method parameter — :class:`whetstone_gate.driver.clients.MeteredModelClient` —
and this package imports none. C12-DRIVER established the reason and it is unchanged here:
*"Writing an untested provider client into this chunk would put an unexercised code path
between the operator and a SINGLE-SHOT run."* T-FP is part of the scored sweep the operator
starts, so the same argument applies with the same force.

**2. THE RESERVED LANE.** ``config/lanes.yaml`` gives the benign solver ``flash-lite-3.1``
(``reserved_from: null``) with a declared spill to ``gemma-31b``, which is **reserved from
2026-08-31**. `PROCESS.md` §8: *"No build session may spend on them."* And the spill is not
optional — ``flash-lite-3.1`` carries **500 RPD** against T-FP's 4,000 agent calls — so a
real benign run needs a sanction for a reserved lane before it starts, not when it spills.

**3. `probe-v1`.** `CONTEXT.md` §15.1 cuts that tag before the pilot and before the arm-1
calibration, and `PROTOCOL.md` §6 calls the order *"not negotiable"*. This target checks it
through the driver's own :func:`whetstone_gate.driver.run.probe_tag_resolves` rather than
asking git again — one reader, one answer.

--------------------------------------------------------------------------------------
⚠️ AND A DRY RUN REFUSES TO PUBLISH A FIGURE
--------------------------------------------------------------------------------------

:func:`whetstone_gate.benign.report.false_positive_rate` raises on a dry run, and
:func:`~whetstone_gate.benign.report.rate_lines` prints the refusal **in place of the
rate**. Every count still prints, so the refusal costs no evidence — it costs exactly the
one thing a rehearsal is not entitled to produce.
"""

from __future__ import annotations

import argparse

from whetstone_gate._console import say
from whetstone_gate.benign import report as report_module
from whetstone_gate.benign import shell as benign_shell
from whetstone_gate.benign.blindness import BlindnessError
from whetstone_gate.benign.constants import BenignConstantError
from whetstone_gate.benign.evidence import EvidenceError
from whetstone_gate.benign.executor import BenignExecutorError
from whetstone_gate.benign.manifest import SOLVER_LANE, USER_SIMULATOR_LANE, BlockRefused
from whetstone_gate.benign.paired import PairingError
from whetstone_gate.benign.rehearsal import RehearsalError
from whetstone_gate.benign.report import ReportRefused
from whetstone_gate.benign.solve import BenignSolverError
from whetstone_gate.config import repo_root
from whetstone_gate.driver.episode import S3_BINDINGS
from whetstone_gate.driver.run import PROBE_TAG, probe_tag_resolves

#: The reserved lane ``config/lanes.yaml`` names as the benign solver's spill.
#: `PROCESS.md` §8 — **no build session may spend on it.**
SPILL_LANE = "gemma-31b"


class CommandRefused(RuntimeError):
    """A precondition typed on the command line. Printed as the outcome, exit code 2."""


#: ⚠️ **EVERY NAMED REFUSAL THIS PACKAGE CAN RAISE ON A COMMAND-LINE PATH.**
#:
#: The first version caught two of them. Measured by this chunk's own adversarial pass,
#: before its first commit: ``--turn-budget 3`` (a plan longer than the budget) and
#: ``--temperature -0.5`` both produced a **Python traceback and exit 1** instead of the
#: ``REFUSED - and the refusal is the outcome`` block and exit 2. **Both are designed
#: refusals arriving as crashes**, and it is precisely the defect commit ``5b88a5e``
#: recorded against the driver one commit before this chunk began — *"the refusal printed a
#: TRACEBACK instead of a named refusal"*. A refusal a reader mistakes for a bug is a
#: refusal that gets worked around.
REFUSALS: tuple[type[Exception], ...] = (
    CommandRefused,
    benign_shell.BenignRunRefused,
    BenignConstantError,
    BenignExecutorError,
    BenignSolverError,
    BlindnessError,
    BlockRefused,
    EvidenceError,
    PairingError,
    RehearsalError,
    ReportRefused,
)


def build_parser() -> argparse.ArgumentParser:
    """The parser. ⚠️ **Every measurement-bearing value is ``required=True`` with no default.**"""
    parser = argparse.ArgumentParser(
        prog="python -m whetstone_gate.benign",
        description=(
            "C12 - THE BENIGN SOLVER. Runs legitimate merchant work through the same "
            "six-name tool surface and the same world the attacker uses, policy-blind, and "
            "reports CONTEXT.md S12.3's PAIRED false-positive delta."
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="no network call of any kind; the solver is a scripted transcript and NO "
        "FIGURE IS PUBLISHED",
    )
    mode.add_argument(
        "--spend-real-tokens",
        action="store_true",
        help="spend a lane's quota. Refuses without a provider client, which this package "
        "deliberately does not ship",
    )
    parser.add_argument(
        "--seed",
        type=int,
        action="append",
        required=True,
        metavar="SEED",
        help="a world seed. REPEATABLE. S12.4 pairs BY SEED and every arm of a pair uses "
        "the same one. Repeat it to run the paired matrix at the T-FP block's scale",
    )
    parser.add_argument(
        "--s3-binding",
        choices=S3_BINDINGS,
        required=True,
        help="Q-141, RULED 'authorization-is-the-payment'. Still required with no default, "
        "per the ruling's own operational note",
    )
    parser.add_argument(
        "--turn-budget",
        type=int,
        required=True,
        help="turns per benign episode. ⚠️ Q-156: config/ carries NO "
        "benign_solver.turn_budget, and the attacker's is not this solver's to borrow",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        required=True,
        help="⚠️ Q-156: config/ carries NO benign_solver.temperature, and S12.3's paired "
        "definition is 'same task, same seed, same solver, SAME TEMPERATURE' — so it is "
        "part of the measurement and is typed, not defaulted",
    )
    parser.add_argument(
        "--sanction-lane",
        action="append",
        default=[],
        metavar="LANE",
        help="sanction one reserved lane for a real run. No wildcard. Repeatable",
    )
    return parser


def refuse_a_real_run(sanctioned: frozenset[str]) -> None:
    """Everything a real run needs and this build cannot supply. **Refusals, in order.**"""
    if not probe_tag_resolves(repo_root()):
        raise CommandRefused(
            f"{PROBE_TAG} does not resolve. CONTEXT.md S15.1 cuts it BEFORE the pilot and "
            f"BEFORE the arm-1 calibration, and PROTOCOL.md S6 calls that order 'not "
            f"negotiable'. T-FP is part of the scored sweep, so a benign episode that "
            f"spent before the tag existed would have spent inside a run the "
            f"pre-registration does not cover.\n"
            f"To rehearse before the tag exists, use --dry-run."
        )
    if SPILL_LANE not in sanctioned:
        raise CommandRefused(
            f"lane {SPILL_LANE!r} is RESERVED from 2026-08-31 (config/lanes.yaml) and is "
            f"the benign solver's DECLARED SPILL: {SOLVER_LANE!r} carries 500 RPD against "
            f"T-FP's 4,000 agent calls, so the spill is not optional and cannot be "
            f"discovered halfway through. PROCESS.md S8: no build session may spend on it. "
            f"This run's sanctioned set is {sorted(sanctioned)}.\n"
            f"The tau2 user simulator would need {USER_SIMULATOR_LANE!r} as well, and "
            f"nothing in src/ drives one - see Q-154."
        )
    raise CommandRefused(
        "--spend-real-tokens needs a provider client and this package deliberately ships "
        "none: it imports no model client and makes no provider call, asserted two ways in "
        "tests/test_c12_benign.py.\n"
        "Supply one at the call site - anything satisfying "
        "whetstone_gate.driver.clients.MeteredModelClient, whose two methods return a "
        "ModelReply carrying the provider's OWN usage block - and call "
        "whetstone_gate.benign.shell.execute(settings, client_for_task=lambda task: yours).\n"
        "Writing an untested provider client into this chunk would put an unexercised code "
        "path between the operator and a SINGLE-SHOT scored block (PROCESS.md S6b)."
    )


def main(argv: list[str] | None = None) -> int:
    """Parse, refuse or run, print. ⚠️ **A refusal exits 2 and is printed as the outcome.**"""
    args = build_parser().parse_args(argv)
    say("-- benign - the counter-metric ---------------------------------------------")
    try:
        if args.spend_real_tokens:
            refuse_a_real_run(frozenset(args.sanction_lane))
        settings = benign_shell.load_settings(
            seeds=tuple(args.seed),
            s3_binding=args.s3_binding,
            turn_budget=args.turn_budget,
            temperature=args.temperature,
            spend_real_tokens=bool(args.spend_real_tokens),
        )
        result = benign_shell.execute(
            settings,
            client_for_task=lambda task: benign_shell.transcript_client_for(
                task, turn_budget=settings.constants.turn_budget
            ),
        )
    except REFUSALS as refusal:
        say(
            f"  REFUSED ({type(refusal).__name__}) - and the refusal is the outcome, not "
            f"an error to work around:"
        )
        for line in str(refusal).split("\n"):
            say(f"    {line}")
        return 2
    report_module.print_report(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
