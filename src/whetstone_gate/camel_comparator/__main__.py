"""``python -m whetstone_gate.camel_comparator`` — the harness report, and nothing else.

⚠️ **THIS COMMAND SPENDS NOTHING AND DECIDES NOTHING.** It reads the vendored checkout,
re-derives every `CONTEXT.md` §8.5 claim, regenerates the empty-diff proof, prints RUN-1's
two-pass invocation, and stops. It makes no provider call and it does not write
``camel_comparator.branch``.

⚠️ **EVERY HUMAN-FACING LINE GOES THROUGH** :func:`whetstone_gate._console.say`.
`INCIDENTS.md` **INC-25**: the spend-free self-test died with ``UnicodeEncodeError`` on the
operator's own Git Bash console, before printing one line of its verdict, because a bare
``print()`` met this project's typography. That happened *inside* a session that had been
told to watch for it. There is no mechanism behind this rule, which is exactly why it is
restated here.
"""

from __future__ import annotations

import sys

from .. import config as cfg
from .._console import say
from . import branch_b as branch_b_mod
from . import claims, invocation, predictions, vendor


def _rule(title: str) -> None:
    say("")
    say(f"-- {title} " + "-" * max(0, 76 - len(title)))


def main() -> int:
    """Print the harness. Returns non-zero only if a re-verified claim does not hold."""
    context_md = (cfg.repo_root() / "CONTEXT.md").read_text(encoding="utf-8")

    _rule("C13 - THE CaMeL COMPARATOR (spend-free; decides nothing)")
    say("  CONTEXT.md S8.5: run CaMeL UNMODIFIED, on its home turf, in its own labelled")
    say("  table. This command builds the harness and STOPS AT THE POINT OF INVOCATION.")

    # ---- the pins and the empty diff -------------------------------------------------
    _rule("1. THE PINS, AND THE EMPTY DIFF THAT IS THE DELIVERABLE")
    camel = vendor.unmodified_proof(vendor.CAMEL_DIRNAME)
    say(f"  CaMeL     : {camel.head_sha}")
    say(f"              {camel.tracked_files} tracked files, {camel.tracked_blob_bytes} blob bytes")
    say(f"              HEAD==pin {camel.head_matches_pin} | status clean {camel.is_clean} "
        f"| diff empty {camel.diff_is_empty}")
    for problem in camel.failures():
        say(f"  ! {problem}")

    dojo = vendor.unmodified_proof(
        vendor.AGENTDOJO_DIRNAME, pin=vendor.head_sha(vendor.agentdojo_root())
    )
    say(f"  AgentDojo : {dojo.head_sha}")
    say(f"              {dojo.tracked_files} tracked files, {dojo.tracked_blob_bytes} blob bytes")
    say("              ! its SHA is C16's key; C13 left `vendor.agentdojo_sha` a sentinel")

    measurement = vendor.interpreter_measurement()
    say(f"  interpreter.py: blob {measurement.blob_bytes} B / {measurement.lines} lines; "
        f"worktree {measurement.worktree_bytes} B ({measurement.cr_bytes} CR bytes)")
    say(f"                  blob + CR == worktree: {measurement.crlf_accounts_for_the_difference}")

    # ---- the base_url grep -----------------------------------------------------------
    _rule("2. THE COROLLARY THAT DECIDES THE DESIGN")
    hits = claims.base_url_hits(vendor.vendor_root())
    say(f"  grep -rn \"base_url\" --include=*.py .  ->  "
        f"{branch_b_mod.base_url_hit_count_phrase(len(hits))}")
    for hit in hits:
        say(f"    {hit}")
    say("  No endpoint override means Groq is unreachable, and patching one in would mean")
    say("  this is no longer CaMeL. That is why the comparator runs on Google or not at all.")

    # ---- the re-verified claims ------------------------------------------------------
    _rule("3. EVERY S8.5 CLAIM, RE-DERIVED AT THE PIN")
    verdicts = claims.verify_all_claims(context_md)
    for verdict in verdicts:
        mark = "OK  " if verdict.holds else "FAIL"
        say(f"  [{mark}] {verdict.claim_id}")
        say(f"         where    : {verdict.where}")
        say(f"         expected : {verdict.expected}")
        say(f"         observed : {verdict.observed}")
        if verdict.note:
            say(f"         note     : {verdict.note}")
    failed = [v for v in verdicts if not v.holds]
    say(f"  {len(verdicts) - len(failed)} of {len(verdicts)} claims reproduce at the pin.")

    # ---- RUN-1 -----------------------------------------------------------------------
    _rule("4. RUN-1 - THE OPERATOR'S RUN. BUILT HERE, EXECUTED THERE.")
    plan = invocation.run1_plan(context_md)
    say(f"  model      : {plan.model_string}")
    say(f"  suite      : {plan.suite} ({plan.user_task_count} user tasks; "
        f"{plan.injection_task} is A5)")
    say(f"  timebox    : {plan.timebox_minutes} minutes")
    say(f"  logs       : {plan.log_root}")
    say("  ! `...+camel+secpol` is a PIPELINE NAME CaMeL emits, not a --model argument.")
    say("    The run is TWO PASSES. CONTEXT.md v1.8 S8.5.1 now says so; QUESTIONS.md Q-057.")
    say(f"  ! {plan.same_working_directory}")
    say("  ! FLAG SPELLINGS ARE DERIVED from main.py's signature (cyclopts kebab-cases each")
    say("    parameter name), NOT transcribed. The argv below has NEVER been executed, which")
    say("    is why step 0 is `--help` and why step 0 is RUN-1's first action.")
    for step in [plan.preflight, *plan.passes]:
        say("")
        say(f"    {step.label}   [spends tokens: {step.spends_tokens}]")
        say(f"      cd {step.cwd}")
        say(f"      {step.command()}")
        say(f"      purpose: {step.purpose}")
        if step.produces_pipeline_name:
            say(f"      -> logs/{step.produces_pipeline_name}/")
        # ! Printed as a NUMBER, never as silence: a step that needs no key says so.
        say(f"      env var NAME(S) required (never a value): "
            f"{', '.join(step.env_var_names) or 'NONE - 0 keys'}")

    _rule("5. THE BRANCH - NOT DECIDED HERE")
    if plan.branch_is_decided:
        say("  camel_comparator.branch is set. RUN-1 has decided; this session did not.")
    else:
        say("  UNDECIDED, correctly. `make selftest` is RED on it and MUST STAY RED until")
        say("  RUN-1 writes it. A build session that turned this green would have decided,")
        say("  from a chair, a question the specification reserves for a timeboxed run.")
        say(f"    {plan.branch_undecided_because}")
    # ! OF-118. The pre-registered CONDITIONS, read through the loader and checked against
    # CONTEXT.md v1.9 S8.5.1 - here, and not only in CI, because Q-079's defect was that
    # NOTHING READ THESE KEYS and a property enforced only in a test file holds only while
    # the tests run (REVIEW_13_1 B-2). This is the same shape as branch_is_undecided above.
    stale = invocation.branch_conditions_are_stale()
    say("  pre-registered branch conditions vs CONTEXT.md S8.5.1: "
        + ("OK - both keys agree with the law" if not stale else f"{len(stale)} PROBLEM(S)"))
    for problem in stale:
        say(f"    ! {problem}")
    say("  Branch B's artefact is ALREADY COMPLETE, beside this module, so taking it on the")
    say("  night is a selection and not an authoring job. Branch B is a RESULT.")

    _rule("6. THE PRE-REGISTERED PREDICTIONS (C18 SCORES THEM; NOTHING HERE DOES)")
    for prediction in predictions.parse_predictions(context_md):
        say(f"  {prediction.ident}: {prediction.one_line()}")

    _rule("RESULT")
    if failed:
        say(f"  FAIL - {len(failed)} third-party claim(s) did not reproduce at the pin.")
        say("  PROCESS.md S9: a claim that does not reproduce is a FINDING, and it outranks")
        say("  finishing the chunk.")
        return 1
    say("  PASS - every re-derived claim holds at the pin. ZERO provider calls, ZERO tokens.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
