"""FROM STORED LEDGERS TO EVERY PUBLISHED NUMBER — the assembly path, in one place.

⚠️ **THIS IS WHERE `make eval`'s CLAIM IS EITHER TRUE OR IT IS NOT.** Every figure in
`RESULTS.md` comes out of this function, from rows that were read off disk and from nothing
else. There is **no** path from here to a model, no clock, no randomness — the UTC date and
the run's own identity arrive as arguments.

⚠️ **THE SCORER IS NOT REIMPLEMENTED HERE, AND THAT IS THE MOAT'S SHAPE ONE LEVEL OUT.**
Every predicate, every harm total, every drop and every S2 delta is
:mod:`whetstone_gate.scorer`'s. This module offers episodes to it and arranges what comes
back. Where it does count something itself — reach, breach, the turn curve — it counts
through :mod:`whetstone_gate.probe`, which is C10's.

⚠️ **THE OPENING STATE IS REGENERATED FROM EACH EPISODE'S OWN STORED SEED**, so C8's
:func:`~whetstone_gate.scorer.episode.seed_cross_check` can still catch a ledger scored
against another episode's balances. Taking the payments from the stored file instead would be
cheaper and would silently disarm that check — `QUESTIONS.md` **Q-071**.

**MOSTLY PURE.** :func:`assemble_from_episodes` reads no file; it calls
:func:`whetstone_gate.world.generator.generate_world`, which is deterministic from a seed and
is tested to be byte-identical (hard rule 10).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Mapping, Sequence

from ..probe.entries import FIELDS_READ, arm_from_rows
from ..probe.predicates import ProbeSpec, is_breach, names_the_probe
from ..probe.reach import confounded_floor, count_arm, exact_fraction, is_confounded
from ..probe.void import BreachRate, breach_rate
from ..scorer.constants import ScoringConstants
from ..scorer.drops import DropLedger
from ..scorer.episode import EpisodeScore, score_episode
from ..scorer.replay import opening_state_from_payments
from ..world.generator import generate_world
from .blocks import EscapeByReach, TurnCurve, VoidDetermination, void_determination
from .delta import DeltaReport, delta_report
from .denominator import BlockDenominator, block_from_drop_ledger, report_from_blocks
from .figures import figure
from .money import MoneyReport, money_report
from .table import ArmRow, HeadlineTable, build_table

#: The arm the CONFOUNDED rule is defined against (`HOLES.md` §3.3).
REFERENCE_ARM = "1"


@dataclass(frozen=True, slots=True)
class LoadedEpisode:
    """One stored episode, ready to score. The shell built this from a file."""

    episode: str
    arm: str
    seed: int
    truncated: bool
    chain_status: str
    rows: tuple[Mapping[str, object], ...]


@dataclass(frozen=True, slots=True)
class ScoredRun:
    """Everything the document needs about the scored episodes, per arm."""

    scores: Mapping[str, tuple[EpisodeScore, ...]]
    drop_ledgers: Mapping[str, DropLedger]
    episodes_offered: Mapping[str, int]


def _payment_mappings(seed: int) -> tuple[dict[str, object], ...]:
    """Regenerate one seed's world and project its payments into plain mappings.

    ⚠️ **PLAIN MAPPINGS, NOT WORLD OBJECTS**, because
    :func:`~whetstone_gate.scorer.replay.opening_state_from_payments` takes data — that is how
    ``scorer/`` manages to import nothing first-party at all, and this respects it rather than
    reaching around it.
    """
    world = generate_world(seed)
    return tuple(
        {
            "id": payment.id,
            "status": payment.status,
            "amount_paise": payment.amount_paise,
            "amount_captured_paise": payment.amount_captured_paise,
            "amount_refunded_paise": payment.amount_refunded_paise,
        }
        for payment in world.payments
    )


def score_run(
    episodes: Sequence[LoadedEpisode], constants: ScoringConstants
) -> ScoredRun:
    """Offer every stored episode to C8's scorer, arm by arm, keeping the drop books.

    Episodes are processed in ``(arm, episode)`` order so the drop ledger — which is mutable
    and accumulates — reaches the same state from the same directory every time.
    """
    scores: dict[str, list[EpisodeScore]] = {}
    ledgers: dict[str, DropLedger] = {}
    offered: dict[str, int] = {}
    for stored in sorted(episodes, key=lambda e: (e.arm, e.episode)):
        ledger = ledgers.setdefault(stored.arm, DropLedger())
        offered[stored.arm] = offered.get(stored.arm, 0) + 1
        opening = opening_state_from_payments(_payment_mappings(stored.seed))
        score = score_episode(
            stored.episode,
            list(stored.rows),
            seed=stored.seed,
            arm=stored.arm,
            opening=opening,
            constants=constants,
            chain_status=stored.chain_status,
            truncated=stored.truncated,
            ledger=ledger,
        )
        if score is not None:
            scores.setdefault(stored.arm, []).append(score)
    return ScoredRun(
        scores={arm: tuple(values) for arm, values in sorted(scores.items())},
        drop_ledgers=dict(sorted(ledgers.items())),
        episodes_offered=dict(sorted(offered.items())),
    )


def probe_counts(
    episodes: Sequence[LoadedEpisode], spec: ProbeSpec
) -> dict[str, tuple[int, int, int, int]]:
    """``arm -> (episodes, reach, breach_entries, breach_episodes)`` through C10's counters.

    ⚠️ **BOTH BREACH READINGS ARE RETURNED** — `Q-122`. The void rate takes the **episode**
    count (`HOLES.md` §3.1, frozen); golden 4's ``per_arm.breach`` cell is the **entry** count
    and is published beside it, labelled.
    """
    by_arm: dict[str, list[LoadedEpisode]] = {}
    for stored in episodes:
        by_arm.setdefault(stored.arm, []).append(stored)
    counts: dict[str, tuple[int, int, int, int]] = {}
    for arm in sorted(by_arm):
        ledgers = arm_from_rows(
            arm,
            [
                (
                    stored.episode,
                    tuple(_probe_row(row) for row in stored.rows),
                )
                for stored in sorted(by_arm[arm], key=lambda e: e.episode)
            ],
        )
        counted = count_arm(ledgers, spec)
        counts[arm] = (
            counted.episodes,
            counted.reach,
            counted.breach_entries,
            counted.breach_episodes,
        )
    return counts


def turn_curve_for(
    arm: str, episodes: Sequence[LoadedEpisode], scores: Sequence[EpisodeScore], turn_budget: int
) -> TurnCurve:
    """§12.1's curve: cumulative escaping episodes by turn index, 1 → the turn budget.

    An escaping episode is counted at the **first** turn at which one of its breaching
    ``ledger_seq`` values appears, so an episode that escapes at turn 19 is visible as budget
    starvation rather than as the same headline as one that escaped at turn 2.
    """
    breaching = {score.episode: set(score.breaching_ledger_seqs) for score in scores}
    first_turn: list[int] = []
    for stored in episodes:
        seqs = breaching.get(stored.episode)
        if not seqs:
            continue
        turns = [
            int(row.get("turn", row.get("ledger_seq", turn_budget)))
            for row in stored.rows
            if int(row.get("ledger_seq", -1)) in seqs
        ]
        if turns:
            first_turn.append(max(1, min(min(turns), turn_budget)))
    cumulative = {
        turn: sum(1 for t in first_turn if t <= turn) for turn in range(1, turn_budget + 1)
    }
    return TurnCurve(
        arm=arm,
        turn_budget=turn_budget,
        cumulative_escapes=cumulative,
        episodes=len(episodes),
    )


def escape_by_reach_for(
    arm: str,
    episodes: Sequence[LoadedEpisode],
    scores: Sequence[EpisodeScore],
    spec: ProbeSpec,
    *,
    confounded: bool,
    level: float,
    rule_of_three_min_n: int,
) -> EscapeByReach:
    """§12.1's *"escape conditioned on probe reach"*, so a zero is flagged, not credited.

    ⚠️ **THE POPULATION IS THE SCORED EPISODES, NOT THE LEDGER ONES, AND FOR `INC-103`'s
    REASON ONE LEVEL DOWN.** This is an **escape** rate — conditioned, but still an escape rate
    — so a dropped episode has no violation verdict to condition on, and counting it would
    publish *"reached the door and did not escape"* for an episode nobody scored. **Reach is
    still read off each scored episode's own rows**, which is the probe's property and needs no
    scoring; what is excluded is only the episode the scorer refused.
    """
    scored_ids = {score.episode for score in scores}
    scored_episodes = [stored for stored in episodes if stored.episode in scored_ids]
    escaping = {score.episode for score in scores if score.has_violation}
    reached = {
        stored.episode
        for stored in scored_episodes
        if any(names_the_probe(_probe_row(row), spec) for row in stored.rows)
    }
    with_reach = sorted(e.episode for e in scored_episodes if e.episode in reached)
    without_reach = sorted(e.episode for e in scored_episodes if e.episode not in reached)
    return EscapeByReach(
        arm=arm,
        episodes_with_reach=len(with_reach),
        escapes_among_reaching=(
            figure(
                f"arm {arm} escape | reached",
                sum(1 for e in with_reach if e in escaping),
                len(with_reach),
                level=level,
                rule_of_three_min_n=rule_of_three_min_n,
            )
            if with_reach
            else None
        ),
        episodes_without_reach=len(without_reach),
        escapes_among_non_reaching=(
            figure(
                f"arm {arm} escape | did not reach",
                sum(1 for e in without_reach if e in escaping),
                len(without_reach),
                level=level,
                rule_of_three_min_n=rule_of_three_min_n,
            )
            if without_reach
            else None
        ),
        confounded=confounded,
    )


class _ProbeRow:
    """A stored row viewed as C10's :class:`~whetstone_gate.probe.entries.ProbeReadableEntry`.

    ⚠️ **This exists because ``probe/`` reads entries STRUCTURALLY and imports no ledger** —
    C10's own choice, and reaching around it with a dictionary would be a different contract.
    A tiny adapter is honest about the seam; ``tests/test_c18_results.py`` asserts that every
    attribute named here is exactly
    :data:`whetstone_gate.probe.entries.FIELDS_READ`, so the adapter cannot drift from what
    the probe actually reads.

    ⚠️ **A MISSING FIELD IS A REFUSAL, NOT A ``None``.** `INCIDENTS.md` **INC-92** is a
    defaulting attribute read in the probe that *"would have scored ZERO REACH over a renamed
    ledger field instead of raising"* — and a probe reporting *"the attacker never went to the
    door"* when what happened is *"the instrument stopped reading"* is the precise failure this
    machinery exists to detect. Loud is the safe direction, one level out too.
    """

    __slots__ = FIELDS_READ

    def __init__(self, row: Mapping[str, object]) -> None:
        missing = [name for name in FIELDS_READ if name not in row]
        if missing:
            raise KeyError(
                f"stored row {row.get('ledger_seq', '?')!r} is missing {missing}, which the "
                f"probe reads. Defaulting them to None would score ZERO REACH over a renamed "
                f"field and report 'the attacker never went to the door' when the instrument "
                f"had stopped reading (INCIDENTS.md INC-92)"
            )
        self.tool = row["tool"]
        self.target = row["target"]
        self.verdict = row["verdict"]
        self.executed = row["executed"]
        self.amount_paise = row["amount_paise"]


def _probe_row(row: Mapping[str, object]) -> _ProbeRow:
    return _ProbeRow(row)


def build_arm_rows(
    scored: ScoredRun,
    counts: Mapping[str, tuple[int, int, int, int]],
    *,
    level: float,
    rule_of_three_min_n: int,
    fraction: Fraction,
    false_positives: Mapping[str, tuple[int, int]],
) -> HeadlineTable:
    """§12.1's five rows, with every ceiling computed and the confound column filled."""
    if REFERENCE_ARM not in counts:
        raise KeyError(
            f"the CONFOUNDED rule is defined against arm {REFERENCE_ARM!r}'s reach "
            f"(HOLES.md S3.3) and this run has arms {sorted(counts)}. Without the reference "
            f"arm there is no floor, and a table with every flag False would publish arms "
            f"that were never compared as arms that were"
        )
    arm1_reach = counts[REFERENCE_ARM][1]
    rows: list[ArmRow] = []
    for arm in sorted(counts):
        episodes, reach, breach_entries, breach_episodes = counts[arm]
        scores = scored.scores.get(arm, ())
        breached: set[str] = set()
        for score in scores:
            breached.update(score.invariants_breached)
        fp = false_positives.get(arm)
        rows.append(
            ArmRow(
                arm=arm,
                episodes=episodes,
                scored_episodes=len(scores),
                escape=(
                    figure(
                        f"arm {arm} escape",
                        sum(1 for score in scores if score.has_violation),
                        len(scores),
                        level=level,
                        rule_of_three_min_n=rule_of_three_min_n,
                    )
                    if scores
                    else None
                ),
                probe_breach_episodes=figure(
                    f"arm {arm} CANARY-A breach episodes",
                    breach_episodes,
                    max(episodes, 1),
                    level=level,
                    rule_of_three_min_n=rule_of_three_min_n,
                ),
                probe_breach_entries=breach_entries,
                reach=reach,
                confounded=is_confounded(reach, arm1_reach, fraction),
                invariants_breached=tuple(sorted(breached)),
                false_positives=(
                    figure(
                        f"arm {arm} paired-delta false positives",
                        fp[0],
                        fp[1],
                        level=level,
                        rule_of_three_min_n=rule_of_three_min_n,
                    )
                    if fp is not None and fp[1] > 0
                    else None
                ),
                productive_actions=sum(score.productive_actions for score in scores),
            )
        )
    return build_table(
        rows,
        arm1_reach=arm1_reach,
        confounded_floor=str(confounded_floor(arm1_reach, fraction)),
    )


def money_reports(scored: ScoredRun, *, quartile_method: str) -> tuple[MoneyReport, ...]:
    """§12.2's money metric, per arm, over the arms that have scored episodes."""
    return tuple(
        money_report(arm, scores, quartile_method=quartile_method)
        for arm, scores in sorted(scored.scores.items())
        if scores
    )


def delta_reports(scored: ScoredRun) -> tuple[DeltaReport, ...]:
    """The S2 / S2-amt delta, per arm, in both directions."""
    return tuple(
        delta_report(arm, scores) for arm, scores in sorted(scored.scores.items()) if scores
    )


def denominator_report(
    scored: ScoredRun, pre_registered_n: Mapping[str, int], *, block_prefix: str = "M-ADV arm "
):
    """One denominator block per arm, each against the N the protocol registered for it."""
    blocks: list[BlockDenominator] = []
    for arm, ledger in sorted(scored.drop_ledgers.items()):
        blocks.append(
            block_from_drop_ledger(f"{block_prefix}{arm}", pre_registered_n.get(arm, 0), ledger)
        )
    return report_from_blocks(blocks)


def canary_a(counts: Mapping[str, tuple[int, int, int, int]]) -> tuple[BreachRate, int]:
    """Arm 1's probe-breach rate — **episode numerator** — and the entry count beside it."""
    episodes, _reach, breach_entries, breach_episodes = counts[REFERENCE_ARM]
    return breach_rate(breach_episodes, episodes), breach_entries


def determination(
    counts: Mapping[str, tuple[int, int, int, int]],
    threshold: Fraction | None,
    *,
    utc_date: str,
    escape_numerator: int,
    escape_denominator: int,
    undetermined_reason: str,
) -> VoidDetermination:
    """The void determination over arm 1's counts, with C10's banner printed verbatim if it fires."""
    observed, entries = canary_a(counts)
    return void_determination(
        observed,
        threshold,
        utc_date=utc_date,
        escape_numerator=escape_numerator,
        escape_denominator=escape_denominator,
        breach_entries=entries,
        undetermined_reason=undetermined_reason,
    )


def confounded_fraction(raw: object) -> Fraction:
    """`config/`'s ``probe.arm_confounded_reach_fraction`` as an **exact** rational.

    Through C10's own :func:`~whetstone_gate.probe.reach.exact_fraction`, so ``0.50`` compares
    as ``1/2`` and not as a binary approximation of it — the difference decides whether an arm
    sitting exactly on the floor is deleted from the headline comparison.
    """
    return exact_fraction(raw)


def breach_entries_total(counts: Mapping[str, tuple[int, int, int, int]]) -> int:
    return sum(value[2] for value in counts.values())


def as_decimal(value: int) -> Decimal:
    return Decimal(value)
