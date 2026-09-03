"""``python -m whetstone_gate.driver`` — the command line, and the flag that spends money.

⚠️⚠️ **NO ARGUMENT SPENDS MONEY BY DEFAULT, AND THE DEFAULT IS NOT "DRY RUN" EITHER.**
Exactly one of ``--dry-run`` / ``--spend-real-tokens`` must be typed. A parser whose
*absent* argument meant *"call the provider"* is one typo away from the pilot; a parser that
silently defaulted to a dry run would let an operator believe a real run had happened. Both
readings are refusals here, so the operator's intent is always **in the command they can
paste into `RUN_DECLARED.md`** (`PROCESS.md` §6b).

**Every other precondition is :mod:`whetstone_gate.driver.run`'s** — `probe-v1`, the lane
sanctions, the key **names**, the day's usage file — and this module only turns text into
the arguments those refusals read.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from whetstone_gate import config as cfg
from whetstone_gate._console import say
from whetstone_gate.driver import episode as driver_episode
from whetstone_gate.driver import pilot as pilot_module
from whetstone_gate.driver import rehearsal
from whetstone_gate.driver import run as driver_run
from whetstone_gate.driver.clients import MeteredProviderClient, TranscriptClient
from whetstone_gate.runner.budget import Ceilings

PROGRAM = "python -m whetstone_gate.driver"


def build_parser() -> argparse.ArgumentParser:
    """The whole surface. **Every money-relevant flag is `required=True`.**"""
    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=(
            "Run CONTEXT.md S13.4's pilot block, or rehearse it offline. "
            "The pilot is SINGLE-SHOT (PROCESS.md S6b): the first execution that runs to "
            "completion IS the run, whatever number it contains."
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="make NO network call at all; drive a deterministic transcript instead",
    )
    mode.add_argument(
        "--spend-real-tokens",
        action="store_true",
        help=(
            "call the provider. REFUSES unless probe-v1 resolves, both ceilings are given, "
            "every reserved lane is sanctioned by name, and every provider key NAME is set"
        ),
    )
    parser.add_argument(
        "--arm",
        required=True,
        help=(
            "the arm the pilot runs. NOT in config/ and NOT defaulted: CONTEXT.md S13.4 and "
            "PROTOCOL.md S3.1 both say '1 ref arm' and neither says which (QUESTIONS.md Q-144)"
        ),
    )
    parser.add_argument(
        "--s3-binding",
        required=True,
        choices=list(driver_episode.S3_BINDINGS),
        help=(
            "what a capture REFERENCES for CONTEXT.md S9.2's S3. An OPEN Class A question "
            "(QUESTIONS.md Q-141): it changes arm 4's verdicts, and one reading blocks every "
            "capture, which FLATTERS OUR OWN GATE"
        ),
    )
    parser.add_argument(
        "--call-ceiling",
        required=True,
        type=int,
        help="hard rule 12's call ceiling, PER LANE, never pooled (golden 8 fixture E)",
    )
    parser.add_argument(
        "--token-ceiling",
        required=True,
        type=int,
        help=(
            "hard rule 12's token ceiling, PER LANE. 'A sanction of max N calls alone is not "
            "a sanction': one spike episode burned ~300K tokens against a 200K-TPD lane"
        ),
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=None,
        help=(
            "where evals/ is written. REQUIRED for --dry-run and REFUSED if it is inside "
            "the repository; defaults to the repository root for a real run"
        ),
    )
    parser.add_argument(
        "--sanction-lane",
        action="append",
        default=[],
        metavar="LANE",
        help=(
            "name a RESERVED lane this run may spend on (PROCESS.md S8). Repeatable. There "
            "is no wildcard, deliberately"
        ),
    )
    parser.add_argument(
        "--allow-absent-corpus",
        action="store_true",
        help=(
            "--dry-run only: proceed with NO attacker corpus. CONTEXT.md S11.3's "
            "corpus-vs-improvisation split would then read 100%% IMPROVISED, so a REAL run "
            "refuses regardless of this flag (QUESTIONS.md Q-145)"
        ),
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        default=None,
        help=(
            "--dry-run only: a JSON file {'attacker': [[text, tokens], ...], 'judge': [...], "
            "'rate_limit_at': null}. Omit it to use the built-in rehearsal fixture"
        ),
    )
    return parser


def _transcript_client(
    arguments: argparse.Namespace, matrix: pilot_module.PilotMatrix
) -> TranscriptClient:
    """The offline client for a dry run. ⚠️ **A FIXTURE, and it says so in the report.**"""
    if arguments.transcript is not None:
        document = json.loads(arguments.transcript.read_bytes().decode("utf-8"))
        return TranscriptClient(
            attacker_replies=[tuple(row) for row in document["attacker"]],
            judge_replies=[tuple(row) for row in document.get("judge", [])],
            rate_limit_at=document.get("rate_limit_at"),
        )
    episodes = matrix.episode_count
    return TranscriptClient(
        attacker_replies=rehearsal.attacker_transcript(episodes),
        # An upper bound: at most one judge call per turn, and only decided turns make one.
        # TranscriptClient refuses on EXHAUSTION, never on leftovers.
        judge_replies=rehearsal.judge_transcript(episodes * matrix.turn_budget),
    )


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    matrix = pilot_module.load_pilot(arm=arguments.arm)

    out_root = arguments.out_root
    if out_root is None:
        if arguments.dry_run:
            say(
                "REFUSED: --dry-run needs --out-root, and it must be OUTSIDE this "
                "repository. A rehearsal ledger in evals/episodes/ is byte-shaped exactly "
                "like a scored one, and evals/ is append-only with operator-only deletion "
                "(CLAUDE.md S4), so no session could remove it afterwards."
            )
            return 2
        out_root = cfg.repo_root()

    request = driver_run.RunRequest(
        matrix=matrix,
        out_root=out_root,
        ceilings=Ceilings(
            call_ceiling=arguments.call_ceiling, token_ceiling=arguments.token_ceiling
        ),
        s3_binding=arguments.s3_binding,
        spend_real_tokens=bool(arguments.spend_real_tokens),
        sanctioned_lanes=frozenset(arguments.sanction_lane),
        allow_absent_corpus=bool(arguments.allow_absent_corpus),
    )

    # ⚠️ The client factory is built INSIDE the try, because refusing to invent a provider
    # client IS a RunRefused and must print like every other refusal — as a named outcome
    # and a non-zero exit, never as a traceback. Built outside, it escaped this handler.
    try:
        client = (
            _transcript_client(arguments, matrix)
            if request.dry_run
            else _provider_client(matrix)
        )
        result = driver_run.execute(request, client=client)
    except driver_run.RunRefused as refused:
        say("REFUSED - and the refusal is the outcome, not an error to work around:")
        for part in str(refused).split(". "):
            say(f"  {part}")
        return 2
    driver_run.print_report(result)
    return 0


def _provider_client(matrix: pilot_module.PilotMatrix) -> MeteredProviderClient:
    """⚠️ **CONSTRUCT THE REAL PROVIDER CLIENT — `Q-150`, RULED 2026-09-03, OPTION 1.**

    This function replaced ``_refuse_to_invent_a_provider_client``, which raised on every
    ``--spend-real-tokens`` invocation and made `evals/pilot/RUN_DECLARED.md` §1's declared
    command unrunnable. The ruling names the architect's own error — *"the C12 BUILD prompt
    said 'ship no provider client, supply one at the call site' AND the declared command
    goes through `tasks drive`, WHICH IS A CLI WITH NO INJECTION POINT"* — and takes option
    1 because it is the only one that keeps §1's command **true as written**.

    ⚠️⚠️ **AND IT STILL REFUSES ON THIS MATRIX, FOR A DIFFERENT AND UNRELATED REASON.**
    :class:`whetstone_gate.driver.clients.MeteredModelClient` has exactly two methods,
    ``complete_attacker`` and ``complete_judge``. They distinguish the **role**; nothing in
    either signature distinguishes a **lane**. :func:`whetstone_gate.driver.run.execute`
    takes **one** client for the whole matrix, and the pilot's matrix has **two attacker
    cells on two different providers** — ``gemma-26b`` on Google and ``qwen-27b`` on Groq.
    So a single client is asked to call two different models with no way to know which, and
    **there is no signal anywhere on the call path that would tell it**: ``lane`` is a live
    local in ``run.py``'s dispatch loop and in ``_MeteredCall``, and neither forwards it.

    ⚠️ **BOTH CELLS ALSO RUN THE SAME SEED BLOCK**, so turn 1 of ``gemma-26b``/seed *N* and
    turn 1 of ``qwen-27b``/seed *N* are **byte-identical**: the payload cannot distinguish
    the lanes even in principle. Inferring the lane from dispatch order, or reaching up the
    call stack for it, would be a guess about another module's internals — `INCIDENTS.md`
    **INC-51**'s exact species, which walked past `check_roles` D1, D2 **and** D3.

    **So this refuses, by name, and states the one-line fix** (`QUESTIONS.md` **Q-161**,
    Class A). A single-attacker-lane matrix constructs and runs normally, which is the
    path this code takes when the fix lands or when a matrix has one cell.
    """
    attacker_lanes = sorted({matrix.lane_for(key) for key in matrix.keys()})
    if len(attacker_lanes) != 1:
        raise driver_run.RunRefused(
            f"this matrix dispatches attacker episodes on {len(attacker_lanes)} lanes "
            f"({attacker_lanes}) and driver.run.execute takes ONE client for all of them. "
            f"MeteredModelClient's two methods distinguish the ROLE (attacker vs judge) and "
            f"carry NO lane, NO model id and NO episode key, so a single client cannot know "
            f"which provider a given complete_attacker call is for - and both cells run the "
            f"SAME seeds, so the messages are byte-identical and cannot be told apart "
            f"either. This REFUSES rather than guessing from dispatch order or reading the "
            f"caller's frame, which would be INCIDENTS.md INC-51's exact species. "
            f"THE FIX IS ONE FIELD AND ONE ARGUMENT, and it is OUTSIDE this session's "
            f"fence: _PacedClient already holds the lane (its attacker_buckets.lane) and "
            f"_MeteredCall already holds it too, so threading `lane` into "
            f"MeteredModelClient's two methods closes it. QUESTIONS.md Q-161, Class A. "
            f"NOTHING WAS SPENT and no episode was attempted"
        )
    return MeteredProviderClient.for_lanes(
        attacker_lane=attacker_lanes[0], judge_lane=matrix.judge_lane
    )


if __name__ == "__main__":
    raise SystemExit(main())
