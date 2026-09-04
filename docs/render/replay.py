"""**THE REPLAY CORE — loads a STORED episode, VERIFIES its chain, and reports FACTS.**

`PROCESS.md` §12's C17 card: *"`docs/render/` — the replay renderer. Reads
`evals/episodes/` **only**."* This module is the half both deliverables share: the §18
RACE beat (:mod:`race`) and the audit log (:mod:`audit`).

---

## ⚠️ IT VERIFIES THE CHAIN RATHER THAN TRUSTING IT

A renderer that would happily animate a tampered ledger is a prop, not evidence. Every
episode loaded here goes through :func:`whetstone_gate.ledger.chain.verify`, which
**recomputes** each entry's digest from that entry's own contents and walks on from the
recomputed value — never from the stored one. `tests/goldens/golden5_tamper.json`'s cases
C and D are the mutations that separate a recomputing verifier from a stored-field one,
and `tests/test_c17_render.py` fires both shapes at this module.

⚠️ **A VALID VERDICT OVER AN EMPTY LEDGER IS VACUOUS, AND THIS MODULE SAYS SO.** Ten of
the eleven stored episodes are literally ``"ledger": []``. A chain over nothing verifies
trivially, and printing a bare ``VALID`` over one would be the most flattering true
sentence available. :attr:`EpisodeReplay.chain_is_vacuous` exists so the renderers can
refuse to print it that way.

---

## ⚠️ THIS MODULE MAKES NO NETWORK CALL AND RUNS NO MODEL

`CONTEXT.md` §14 names four deliberate non-uses, each with its own test. The renderer is
the same species: it reads stored JSON and does arithmetic. `INCIDENTS.md` **INC-51** is
the entry about an import walk reporting clean while a live reach existed — so
`tests/test_c17_render.py` asserts it **two ways**, an AST walk over the transitive
first-party closure *and* a raw source-text scan, and fires each at a planted leak.

---

## ⚠️ NOTHING HERE ADJUDICATES. IT DISPLAYS WHAT THE LEDGER ALREADY STORES

C17 publishes **no number** (`PROCESS.md` §12, rung 5's downgrade note). The harm figures
below are **read out of the stored entries**, never recomputed from world state — that is
`scorer/`'s job, and `CLAUDE.md` hard rule 8 keeps the two apart on purpose.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from whetstone_gate import config as cfg
from whetstone_gate.ledger.chain import load_chain_spec, verify
from whetstone_gate.ledger.entry import ARMS
from whetstone_gate.world.harm import COMPONENTS

#: ``pilot__<arm>__<seed>__<model>.json`` — the stored filename convention.
_NAME_PARTS = 4


class EpisodeLoadError(RuntimeError):
    """A stored episode could not be read as one. Refused, never guessed at."""


def repo_root() -> Path:
    """The repository root, from this file's own location. No environment lookup."""
    return Path(__file__).resolve().parent.parent.parent


def episodes_dir(root: Path | None = None) -> Path:
    """⚠️ **The only directory this package reads.** The C17 card says so in terms."""
    return (repo_root() if root is None else root) / "evals" / "episodes"


def turn_budget() -> int:
    """``attacker.turn_budget``, from ``config/`` through the one loader.

    Hard rule 9: **no default for a required value.** A missing budget is a hard refusal
    here, not a silent fallback to a number this file invented — and the literal is not
    written in this file at all, which `tests/conftest.py`'s tripwire scan enforces over
    ``docs/render/`` exactly as it does over ``src/``.
    """
    return int(cfg.load("protocol").require("attacker.turn_budget"))


# --------------------------------------------------------------------------------------
# Completeness. ⚠️ FOUR STATES, BECAUSE THE STORED DATA HAS FOUR.
# --------------------------------------------------------------------------------------

COMPLETE = "COMPLETE"
TRUNCATED = "TRUNCATED"
EMPTY = "EMPTY"
ABSENT = "ABSENT"


@dataclass(frozen=True)
class EpisodeReplay:
    """One stored episode, verified, with the facts a renderer needs. **Frozen.**"""

    path: Path | None
    arm: str
    seed: int | None
    model: str | None
    genesis_hash: str | None
    algorithm: str | None
    entries: tuple[Mapping[str, Any], ...]
    chain_verdict: str
    chain_first_bad_seq: int | None
    chain_reason: str
    budget: int
    completeness: str

    @property
    def present(self) -> bool:
        """False when no episode file exists for this arm. ⚠️ **NOT the same as zero.**"""
        return self.completeness != ABSENT

    @property
    def chain_ok(self) -> bool:
        return self.chain_verdict == "VALID"

    @property
    def chain_is_vacuous(self) -> bool:
        """⚠️ ``VALID`` over **zero entries** proves nothing and must not be printed bare."""
        return self.chain_ok and not self.entries

    @property
    def turns_seen(self) -> int:
        return len(self.entries)

    @property
    def last_turn_index(self) -> int | None:
        if not self.entries:
            return None
        return max(int(e["turn_index"]) for e in self.entries)

    def component_total(self, component: str) -> int:
        """One harm component, summed **within itself** across the episode's entries.

        ⚠️ **The four components are NEVER added to each other.** `CONTEXT.md` §12.2:
        the old metric *"added together three different losses to three different
        parties"* — an over-capture takes money from a **customer**, an over-refund is a
        **merchant** outflow, a sweep moves the merchant's **own** float. There is
        deliberately no method on this class that returns a single money total.
        """
        return sum(int(e.get(component, 0) or 0) for e in self.entries)

    def component_total_through(self, component: str, turn_index: int) -> int:
        """The same, restricted to entries at or before ``turn_index`` — the RACE beat."""
        return sum(
            int(e.get(component, 0) or 0)
            for e in self.entries
            if int(e["turn_index"]) <= turn_index
        )

    def entries_at(self, turn_index: int) -> tuple[Mapping[str, Any], ...]:
        return tuple(e for e in self.entries if int(e["turn_index"]) == turn_index)

    # -- the three outcomes the fifteen-field schema can tell apart --------------------

    @property
    def executed(self) -> int:
        return sum(1 for e in self.entries if e.get("executed"))

    @property
    def razorpay_refused(self) -> int:
        return sum(1 for e in self.entries if e.get("rejected_by_razorpay"))

    @property
    def tool_layer_refused(self) -> int:
        """⚠️ Neither executed nor refused by Razorpay — `Q-062`'s third outcome.

        `tests/goldens/golden5b_ledger_writer.json` states plainly that its own three
        rows contain **no** row of this shape (*"no_tool_layer_row_here"*). The real
        stored pilot ledger does, at ``ledger_seq`` 6.
        """
        return sum(
            1
            for e in self.entries
            if not e.get("executed") and not e.get("rejected_by_razorpay")
        )


def absent_replay(arm: str, budget: int) -> EpisodeReplay:
    """The arm that has **not run**.

    ⚠️ **This is not a zero and no renderer may draw it as one.** A zero bar and a
    not-run bar look identical on screen and mean opposite things, and *"0% escaped"* is
    precisely the claim this project exists to distrust (`CONTEXT.md` §19).
    """
    return EpisodeReplay(
        path=None,
        arm=arm,
        seed=None,
        model=None,
        genesis_hash=None,
        algorithm=None,
        entries=(),
        chain_verdict="NOT-RUN",
        chain_first_bad_seq=None,
        chain_reason="no episode file exists for this arm",
        budget=budget,
        completeness=ABSENT,
    )


def parse_episode_name(path: Path) -> tuple[str, int, str] | None:
    """``pilot__1__2101__gemma-26b.json`` -> ``("1", 2101, "gemma-26b")``.

    Returns ``None`` rather than raising: an unrecognised filename in the directory is
    something to *report*, not something to crash the render on.
    """
    parts = path.stem.split("__")
    if len(parts) != _NAME_PARTS:
        return None
    _, arm, seed, model = parts
    if not seed.isdigit():
        return None
    return arm, int(seed), model


def load_episode(path: Path, budget: int | None = None) -> EpisodeReplay:
    """Read one stored episode and **verify its chain**.

    ⚠️ The chain is verified against the episode's **own declared** genesis and
    algorithm, and :func:`genesis_matches_config` reports separately whether that
    declaration agrees with ``config/``. Collapsing the two would answer a question
    nobody asked: an episode written before a genesis moved is *internally* sound and
    *externally* out of date, and a reader needs both facts, not their conjunction.
    """
    budget = turn_budget() if budget is None else budget
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise EpisodeLoadError(f"{path.name}: not readable as stored JSON ({exc})") from exc
    if not isinstance(raw, Mapping):
        raise EpisodeLoadError(f"{path.name}: top level is {type(raw).__name__}, not an object")

    ledger = raw.get("ledger")
    if not isinstance(ledger, list):
        raise EpisodeLoadError(
            f"{path.name}: no 'ledger' array. An episode with no ledger is refused rather "
            f"than rendered as an episode in which nothing happened."
        )
    entries = tuple(ledger)

    genesis = raw.get("genesis_hash")
    algorithm = raw.get("hash_algorithm")
    if not isinstance(genesis, str) or not isinstance(algorithm, str):
        raise EpisodeLoadError(
            f"{path.name}: genesis_hash/hash_algorithm missing. The chain cannot be "
            f"verified against a root the file does not declare, and it is refused rather "
            f"than verified against one this renderer chose for it."
        )

    verdict = verify(entries, genesis_hash=genesis, algorithm=algorithm)

    named = parse_episode_name(path)
    arm = str(raw.get("arm", named[0] if named else "?"))
    seed = raw.get("seed", named[1] if named else None)
    model = named[2] if named else None

    if not entries:
        completeness = EMPTY
    else:
        last = max(int(e["turn_index"]) for e in entries)
        completeness = COMPLETE if last >= budget - 1 else TRUNCATED

    return EpisodeReplay(
        path=path,
        arm=arm,
        seed=int(seed) if seed is not None else None,
        model=model,
        genesis_hash=genesis,
        algorithm=algorithm,
        entries=entries,
        chain_verdict=verdict.verdict,
        chain_first_bad_seq=verdict.first_bad_ledger_seq,
        chain_reason=verdict.reason,
        budget=budget,
        completeness=completeness,
    )


def genesis_matches_config(replay: EpisodeReplay) -> bool | None:
    """Does the episode's declared genesis agree with ``config/``? ``None`` if absent.

    ⚠️ `config/protocol.yaml`'s genesis binding is the project's one free proof: *"a
    ledger cannot contain the hash of a tag that did not exist when it was written, so
    pre-freeze episodes are CRYPTOGRAPHICALLY DISTINGUISHABLE from scored ones."* This
    reports the comparison; it does not editorialise about it.
    """
    if replay.genesis_hash is None:
        return None
    return replay.genesis_hash == load_chain_spec().genesis_hash


def discover(root: Path | None = None) -> list[Path]:
    """Every stored episode file, sorted. ⚠️ **Reads ``evals/episodes/`` and nothing else.**"""
    directory = episodes_dir(root)
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.json"))


def load_all(root: Path | None = None, budget: int | None = None) -> list[EpisodeReplay]:
    budget = turn_budget() if budget is None else budget
    return [load_episode(path, budget) for path in discover(root)]


def seeds_available(replays: Iterable[EpisodeReplay]) -> list[int]:
    return sorted({r.seed for r in replays if r.seed is not None})


def by_arm(
    replays: Iterable[EpisodeReplay], seed: int, budget: int
) -> dict[str, list[EpisodeReplay]]:
    """Group one seed's episodes under **all five arms**, absent ones included.

    ⚠️ **Every arm gets a key, whether or not it ran.** An arm dropped from the mapping
    because it has no file is an arm that silently disappears from the render, and the
    whole point of :func:`absent_replay` is that a missing arm stays *visible*.
    """
    grouped: dict[str, list[EpisodeReplay]] = {arm: [] for arm in ARMS}
    for replay in replays:
        if replay.seed == seed and replay.arm in grouped:
            grouped[replay.arm].append(replay)
    for arm, found in grouped.items():
        if not found:
            grouped[arm] = [absent_replay(arm, budget)]
    return grouped


__all__ = [
    "ABSENT",
    "ARMS",
    "COMPLETE",
    "COMPONENTS",
    "EMPTY",
    "TRUNCATED",
    "EpisodeLoadError",
    "EpisodeReplay",
    "absent_replay",
    "by_arm",
    "discover",
    "episodes_dir",
    "genesis_matches_config",
    "load_all",
    "load_episode",
    "parse_episode_name",
    "repo_root",
    "seeds_available",
    "turn_budget",
]
