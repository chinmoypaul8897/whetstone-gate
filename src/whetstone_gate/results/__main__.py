"""``python -m whetstone_gate.results <run-dir>`` — regenerate `RESULTS.md` from stored ledgers.

⚠️ **THIS COMMAND ASKS NO MODEL ANYTHING AND RUNS NO EPISODE.** It reads a directory of
committed JSON and replays it. That is the whole of `make eval`'s claim — *"every number
regenerates from the stored ledgers"* — and it is why the claim is checkable.

⚠️ **IT WRITES TO STDOUT BY DEFAULT, NOT TO `RESULTS.md`.** `RESULTS.md` **is written by the
run**, and a build session that created one would be publishing numbers no sweep produced.
The run passes ``--output RESULTS.md``; every other caller gets the bytes on the stream and
decides for itself.

**THE RUN DIRECTORY**::

    <run-dir>/
      run.json          the blocks no ledger can carry - see below. REQUIRED.
      <arm>/<episode>.json   {"episode","arm","seed","truncated","chain_status","rows"}

``run.json`` is **required and has no defaults**, because every block it carries is mandatory
under §12.1 and a default would be a number this assembler invented. It holds:
``utc_date``, ``pre_registered_n`` (per arm), ``turn_budget``, ``false_positives`` (per arm,
``[numerator, denominator]``), ``tau2`` (``write_attempts`` and ``db_writes`` per arm, and
``tasks``), ``agentdojo_registered_episodes``, ``corpus_split``
(``corpus_derived_turns``, ``improvised_turns``, ``corpora``), ``camel`` (a
:class:`~whetstone_gate.results.camel.CamelObservation`'s fields), ``p2_shape_holds_on``,
``p2_configurations``, ``token_lines``, ``headline_result`` and ``limitations``.

⚠️ **THE N DECISION IS NOT IN ``run.json`` AND MUST NOT BE.** It is COMPUTED here from
``config/``'s own ``n_decision.measured_tokens_per_episode`` through C11's
:func:`whetstone_gate.runner.n_rule.select_n` — both arithmetics, which one bound, and the
pilot's figure — so a run manifest cannot assert a branch the pilot has not selected.

⚠️ **A MISSING KEY IS A REFUSAL WITH ITS OWNER NAMED.** A `RESULTS.md` assembled over a
silently absent block is the most expensive failure this project could ship, because it would
look complete.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

from .. import config as _config
from ..camel_comparator.claims import spec_deny_by_default_string
from ..camel_comparator.predictions import parse_predictions

from .blocks import AgentDojoBlock, CorpusSplit, Tau2NegativeControl
from .camel import CamelObservation, score_predictions
from .degradation import degradation_record
from .document import ResultsInput, render_results
from .figures import UNDECIDED, both_branch_ceilings
from .nrule import lines as n_decision_lines_for
from .loader import (
    LoadError,
    Repository,
    calibrated_void_threshold,
    genesis_hash,
    git_tags,
    head_sha,
    load_episodes,
    measured_tokens_per_episode,
    n_branches,
    open_findings_counts,
    prereg_line,
    read_review_files,
    scoring_constants,
    read_text,
    selected_branch,
    statistics_settings,
    tree_description,
)
from .pipeline import (
    LoadedEpisode,
    build_arm_rows,
    confounded_fraction,
    delta_reports,
    denominator_report,
    determination,
    escape_by_reach_for,
    money_reports,
    probe_counts,
    score_run,
    turn_curve_for,
)


def _require(manifest: Mapping[str, Any], key: str, owner: str) -> Any:
    if key not in manifest:
        raise LoadError(
            f"run.json is missing {key!r}. It is owned by {owner}, it is mandatory under "
            f"CONTEXT.md S12.1, and there is no default: a block this assembler filled in for "
            f"itself would be a number no sweep produced"
        )
    return manifest[key]


def build_input(run_dir: Path, root: Path) -> ResultsInput:
    """Read a run directory and a repository, and produce the pure assembler's whole input."""
    repository = Repository(root=root)
    manifest_path = run_dir / "run.json"
    if not manifest_path.is_file():
        raise LoadError(
            f"{manifest_path} does not exist. Every block it carries is mandatory under "
            f"CONTEXT.md S12.1 and none of them has a default"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    stored = load_episodes(run_dir)
    episodes = tuple(
        LoadedEpisode(
            episode=e.episode,
            arm=e.arm,
            seed=e.seed,
            truncated=e.truncated,
            chain_status=e.chain_status,
            rows=e.rows,
        )
        for e in stored
    )

    level, min_n, quartile_method = statistics_settings()
    protocol = _config.load("protocol")
    constants = scoring_constants()
    fraction = confounded_fraction(protocol.require("probe.arm_confounded_reach_fraction"))
    turn_budget = int(_require(manifest, "turn_budget", "the runner (attacker.turn_budget)"))

    scored = score_run(episodes, constants)
    counts = probe_counts(episodes, _probe_spec())
    table = build_arm_rows(
        scored,
        counts,
        level=level,
        rule_of_three_min_n=min_n,
        fraction=fraction,
        false_positives={
            arm: (int(pair[0]), int(pair[1]))
            for arm, pair in _require(manifest, "false_positives", "C12's paired-delta harness").items()
        },
    )

    by_arm: dict[str, list[LoadedEpisode]] = {}
    for episode in episodes:
        by_arm.setdefault(episode.arm, []).append(episode)

    curves = tuple(
        turn_curve_for(arm, by_arm[arm], scored.scores.get(arm, ()), turn_budget)
        for arm in sorted(by_arm)
    )
    reach_rows = tuple(
        escape_by_reach_for(
            arm,
            by_arm[arm],
            scored.scores.get(arm, ()),
            _probe_spec(),
            confounded=next(
                (row.confounded for row in table.rows if row.arm == arm), False
            ),
            level=level,
            rule_of_three_min_n=min_n,
        )
        for arm in sorted(by_arm)
    )

    arm1 = table.row("1")
    threshold, reason = calibrated_void_threshold()
    void = determination(
        counts,
        threshold,
        utc_date=str(_require(manifest, "utc_date", "the operator")),
        escape_numerator=arm1.escape.numerator if arm1 else 0,
        escape_denominator=arm1.escape.denominator if arm1 else 1,
        undetermined_reason=reason,
    )

    context_md = read_text(repository.context_md)
    camel_fields = dict(_require(manifest, "camel", "RUN-1 / C13's comparator"))
    predictions = score_predictions(
        parse_predictions(context_md),
        CamelObservation(**camel_fields),
        deny_by_default_string=spec_deny_by_default_string(context_md),
        p2_shape_holds_on=tuple(_require(manifest, "p2_shape_holds_on", "C13's branch_b")),
        p2_configurations=int(_require(manifest, "p2_configurations", "C13's branch_b")),
    )

    open_total, open_by_severity = open_findings_counts(
        read_text(repository.reviews_dir / "OPEN_FINDINGS.md")
    )
    from .trail import build_trail  # local: keeps this module's import list to the shell's

    trail = build_trail(
        read_text(repository.status_md),
        read_review_files(repository.reviews_dir),
        git_tags(root),
        open_findings_total=open_total,
        open_findings_by_severity=open_by_severity,
    )

    branch_a_n, branch_b_n = n_branches()
    tau2_manifest = dict(_require(manifest, "tau2", "C3's tau2 adapter"))
    corpus = dict(_require(manifest, "corpus_split", "C6's attacker corpus"))

    return ResultsInput(
        utc_date=str(manifest["utc_date"]),
        head_sha=head_sha(root),
        tree_description=tree_description(root),
        genesis_hash=genesis_hash(),
        void=void,
        table=table,
        denominator=denominator_report(
            scored,
            {
                arm: int(value)
                for arm, value in _require(
                    manifest, "pre_registered_n", "PROTOCOL.md S3"
                ).items()
            },
        ),
        money=money_reports(scored, quartile_method=quartile_method),
        deltas=delta_reports(scored),
        predictions=predictions,
        degradation=degradation_record(read_text(repository.protocol_md)),
        trail=trail,
        zero_ceilings=both_branch_ceilings(
            branch_a_n=branch_a_n,
            branch_b_n=branch_b_n,
            level=level,
            rule_of_three_min_n=min_n,
            taken=selected_branch() or UNDECIDED,
        ),
        turn_curves=curves,
        escape_by_reach=reach_rows,
        tau2=Tau2NegativeControl(
            per_arm_write_attempts={
                arm: int(v) for arm, v in tau2_manifest["write_attempts"].items()
            },
            per_arm_db_writes={arm: int(v) for arm, v in tau2_manifest["db_writes"].items()},
            tasks=int(tau2_manifest["tasks"]),
        ),
        agentdojo=AgentDojoBlock(
            registered_episodes=int(
                _require(manifest, "agentdojo_registered_episodes", "PROTOCOL.md S3")
            )
        ),
        corpus_split=CorpusSplit(
            corpus_derived_turns=int(corpus["corpus_derived_turns"]),
            improvised_turns=int(corpus["improvised_turns"]),
            corpora={str(k): str(v) for k, v in corpus["corpora"].items()},
        ),
        n_decision_lines=n_decision_lines_for(measured_tokens_per_episode()),
        token_lines=tuple(_require(manifest, "token_lines", "C11's runner report")),
        prereg_line=prereg_line(root),
        headline_result=str(_require(manifest, "headline_result", "the sweep")),
        limitations=tuple(_require(manifest, "limitations", "every session that raised one")),
    )


def _probe_spec():
    from ..probe.predicates import ProbeSpec

    return ProbeSpec.from_config()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m whetstone_gate.results",
        description=(
            "Regenerate RESULTS.md from stored ledgers. Asks no model anything and runs no "
            "episode: every number comes out of committed JSON."
        ),
    )
    parser.add_argument("run_dir", type=Path, help="the run directory of stored ledgers")
    parser.add_argument(
        "--root", type=Path, default=None, help="repository root (default: the config's)"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="-",
        help=(
            "where to write. Default '-' is STDOUT. RESULTS.md is written BY THE RUN, and a "
            "session that created one would publish numbers no sweep produced."
        ),
    )
    args = parser.parse_args(argv)
    root = args.root if args.root is not None else _config.repo_root()
    try:
        text = render_results(build_input(args.run_dir, root))
    except LoadError as exc:
        sys.stderr.write(f"REFUSED: {exc}\n")
        return 2
    if args.output == "-":
        sys.stdout.write(text)
    else:
        Path(args.output).write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
