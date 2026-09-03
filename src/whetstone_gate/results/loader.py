"""THE THIN OUTER SHELL — the only place in this package that touches a file or a subprocess.

Hard rule 8's purity separation: *"Core logic takes data in and returns results — no I/O,
clock, network, or randomness inside it. Side effects live in a thin outer shell."* Every
other module here is that core. This one reads.

⚠️ **IT READS STORED LEDGERS. IT ASKS NO MODEL ANYTHING, AND IT RUNS NO EPISODE.** `make
eval`'s claim is *"every number regenerates from the stored ledgers"* — so the input is a run
directory of committed JSON, and there is no code path from here to a provider. That is
asserted two ways in ``tests/test_c18_results.py``, over this package's whole transitive
first-party closure **and** over its raw source text.

⚠️ **IT IMPORTS NO LEDGER MODULE.** A stored ledger row reaches this package as a plain
mapping, exactly as it reaches the scorer, so ``results/`` stays off `OPEN_FINDINGS.md`
**OF-183**'s already-red *"nothing in this repository imports the ledger yet"* walk. The price
is that the row's field names are read structurally; the test that pays it asserts every name
this package reads against ``ledger/entry.py``'s own dataclass, parsed from source.

⚠️ **A MISSING INPUT IS A REFUSAL, NEVER A DEFAULT.** An absent arm directory, an absent
`PROTOCOL.md`, an unresolvable threshold — each raises with its owner named. A `RESULTS.md`
assembled over a silently empty input would be the most expensive failure this project could
ship, because it would look complete.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

from .. import config as _config
from ..probe.void import UndeterminedThreshold, void_threshold


class LoadError(RuntimeError):
    """An input `RESULTS.md` needs could not be read. **Always a stop.**"""


@dataclass(frozen=True, slots=True)
class StoredEpisode:
    """One stored episode as it sits on disk: its identity, its rows, and its chain verdict."""

    episode: str
    arm: str
    seed: int
    truncated: bool
    chain_status: str
    rows: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True, slots=True)
class Repository:
    """The paths this shell reads. Named so a caller can point it at a fixture directory."""

    root: Path

    @property
    def protocol_md(self) -> Path:
        return self.root / "PROTOCOL.md"

    @property
    def status_md(self) -> Path:
        return self.root / "STATUS.md"

    @property
    def context_md(self) -> Path:
        return self.root / "CONTEXT.md"

    @property
    def holes_md(self) -> Path:
        return self.root / "HOLES.md"

    @property
    def reviews_dir(self) -> Path:
        return self.root / "docs" / "reviews"


def read_text(path: Path) -> str:
    """UTF-8, always, and a refusal with the file's name when it is not there."""
    if not path.is_file():
        raise LoadError(
            f"{path} does not exist. RESULTS.md cannot be assembled without it, and "
            f"assembling one that silently omitted this section would look complete"
        )
    return path.read_text(encoding="utf-8")


def read_review_files(reviews_dir: Path) -> dict[str, str]:
    """Every ``*.md`` in `docs/reviews/`, by filename. The verdicts are parsed from the text."""
    if not reviews_dir.is_dir():
        raise LoadError(
            f"{reviews_dir} is not a directory. The review trail is a PUBLISHED RESULT "
            f"(PROCESS.md S12.1's C18 row) and an empty one would misreport eleven-plus real "
            f"FAILs as no reviews at all"
        )
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(reviews_dir.glob("*.md"))
    }


def git_tags(root: Path) -> tuple[str, ...]:
    """``git for-each-ref refs/tags``. ⚠️ **The tag is the authority on a PASS**, not a column."""
    result = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/tags"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise LoadError(
            f"git for-each-ref failed in {root}: {result.stderr.strip()!r}. The tag chain is "
            f"this project's spine and the review trail cannot be published without it"
        )
    return tuple(sorted(line.strip() for line in result.stdout.splitlines() if line.strip()))


def head_sha(root: Path) -> str:
    """The commit these numbers were assembled at. Printed at the top of `RESULTS.md`."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise LoadError(f"git rev-parse HEAD failed in {root}: {result.stderr.strip()!r}")
    return result.stdout.strip()


def tree_description(root: Path) -> str:
    """Whether the working tree was clean when these numbers were taken. ⚠️ **Stated, not assumed.**

    A `RESULTS.md` assembled over a dirty tree is a `RESULTS.md` whose inputs are not the ones
    at its own HEAD, and a reader is entitled to be told which tree produced the numbers
    rather than to infer it from a SHA that does not describe the bytes.
    """
    result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True
    )
    if result.returncode != 0:
        return "UNKNOWN - git status failed"
    dirty = [line for line in result.stdout.splitlines() if line.strip()]
    if not dirty:
        return "CLEAN at HEAD"
    return f"DIRTY - {len(dirty)} path(s) differ from HEAD; these numbers are NOT HEAD's"


def load_episodes(run_dir: Path) -> tuple[StoredEpisode, ...]:
    """Every stored episode under ``run_dir``, sorted by ``(arm, episode)``.

    Layout: ``<run_dir>/<arm>/<episode>.json``, each holding ``{"episode", "arm", "seed",
    "truncated", "chain_status", "rows"}``. Sorted so the same directory renders
    byte-identically — a filesystem's own order is not a contract.
    """
    if not run_dir.is_dir():
        raise LoadError(
            f"{run_dir} is not a directory. `make eval` regenerates every number FROM THE "
            f"STORED LEDGERS (Q-003), and with no ledgers there is nothing to regenerate - "
            f"which is a refusal, not an empty result"
        )
    episodes: list[StoredEpisode] = []
    for arm_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        for path in sorted(arm_dir.glob("*.json")):
            document = json.loads(path.read_text(encoding="utf-8"))
            missing = [
                key
                for key in ("episode", "arm", "seed", "truncated", "chain_status", "rows")
                if key not in document
            ]
            if missing:
                raise LoadError(
                    f"{path} is missing {missing}. A stored episode the assembler would have "
                    f"to guess at is a refusal, not a guess (QUESTIONS.md Q-062)"
                )
            episodes.append(
                StoredEpisode(
                    episode=str(document["episode"]),
                    arm=str(document["arm"]),
                    seed=int(document["seed"]),
                    truncated=bool(document["truncated"]),
                    chain_status=str(document["chain_status"]),
                    rows=sorted_rows(document["rows"]),
                )
            )
    if not episodes:
        raise LoadError(
            f"{run_dir} holds no stored episodes. Publishing a RESULTS.md over zero episodes "
            f"would print every ceiling over an empty denominator, which is exactly the shape "
            f"hard rule 11 forbids"
        )
    return tuple(sorted(episodes, key=lambda e: (e.arm, e.episode)))


def statistics_settings() -> tuple[float, int, str]:
    """``(confidence_level, rule_of_three_min_n, quartile_method)`` from `config/`, no defaults."""
    protocol = _config.load("protocol")
    return (
        float(protocol.require("statistics.confidence_level")),
        int(protocol.require("statistics.rule_of_three_min_n")),
        str(protocol.require("statistics.quartile_method")),
    )


def scoring_constants():
    """C8's :class:`~whetstone_gate.scorer.constants.ScoringConstants`, read through `config/`.

    ⚠️ **THE KEY PATHS ARE `REQUIRED_CONSTANTS`' OWN**, split here rather than retyped, so a
    value quoted under the wrong path — *"hard rule 9's defect one level down"*, in that
    module's words — cannot be introduced by this shell. ``scorer/`` imports no config loader
    at all, which is why the reading is the caller's job in the first place.
    """
    from ..scorer.constants import REQUIRED_CONSTANTS, constants_from

    protocol = _config.load("protocol")
    values = {}
    for attribute, path in REQUIRED_CONSTANTS:
        _file, _, dotted = path.partition(":")
        values[attribute] = protocol.require(dotted)
    return constants_from(values)


def attacker_temperature() -> str:
    """``attacker.temperature`` from `config/`, as its rendered string.

    ⚠️ **READ HERE, NEVER WRITTEN INTO THE PURE CORE.** It is a `CONTEXT.md` §8.6 constant,
    and the tripwire caught it as a literal in `document.py` before this function existed.
    """
    return str(_config.load("protocol").require("attacker.temperature"))


def n_branches() -> tuple[int, int]:
    """``(branch_a_n, branch_b_n)`` from `config/`. Both printed; the pilot selects."""
    protocol = _config.load("protocol")
    return (
        int(protocol.require("n_decision.branch_a_n")),
        int(protocol.require("n_decision.branch_b_n")),
    )


def selected_branch() -> str | None:
    """The pilot's selected branch, or ``None`` while it is still ``TODO_C14_PILOT``.

    ⚠️ **``None`` IS THE ANSWER TODAY AND IS NOT ROUNDED UP.** `Q-107`'s *"regardless"* clause
    is WITHDRAWN and `Q-121` measured the break-even at **31,908** tokens/episode: **no
    session may say N is decided before the pilot.**
    """
    try:
        return str(_config.load("protocol").require("n_decision.selected_branch"))
    except _config.ConfigError:
        return None


def measured_tokens_per_episode() -> int | None:
    """The pilot's measured figure, or ``None`` while the pilot has not run."""
    try:
        return int(_config.load("protocol").require("n_decision.measured_tokens_per_episode"))
    except (_config.ConfigError, ValueError, TypeError):
        return None


def calibrated_void_threshold() -> tuple[Fraction | None, str]:
    """The frozen void threshold, or ``None`` **with the reason it does not exist yet**.

    ⚠️ **A ``None`` HERE IS NOT A FAILURE OF THIS CODE.** `Q-106`: no VOID verdict is
    computable from `config/` as it stands, on any input, *"and it must stay that way until
    C14"*. The reason string is carried so `RESULTS.md` says which, rather than printing a
    verdict computed from an absence.
    """
    try:
        return void_threshold(), "the threshold is calibrated and frozen"
    except UndeterminedThreshold as exc:
        return None, str(exc)


def prereg_line(root: Path) -> str:
    """The `check-prereg` PASS/FAIL line hard rule 9 requires printed into `RESULTS.md`.

    ⚠️ **THIS REPORTS WHAT THE TARGET ACTUALLY DOES, INCLUDING WHEN THAT IS *"NOT YET"*.**
    `PROTOCOL.md` does not exist until C14 and the `prereg-v1` tag does not resolve until the
    freeze; the target then reports ``NOT-YET-FROZEN`` and exits 0. **That is not a PASS**, and
    it is printed as its own word — `OPEN_FINDINGS.md` **OF-185** / `QUESTIONS.md` **Q-100**
    record that `check-prereg` currently *fails open*, which is a limitation owned by whoever
    owns ``src/whetstone_gate/tasks.py`` and is published here rather than papered over.
    """
    protocol = root / "PROTOCOL.md"
    if not protocol.is_file():
        return (
            "NOT-YET-FROZEN - PROTOCOL.md does not exist. This is NOT a PASS; it is 'not yet'."
        )
    tag = subprocess.run(
        ["git", "rev-parse", "--verify", "-q", "prereg-v1^{commit}"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if tag.returncode != 0:
        return (
            "NOT-YET-FROZEN - PROTOCOL.md exists but the `prereg-v1` tag does not resolve, so "
            "there is no freeze to check against. This is NOT a PASS; it is 'not yet'. "
            "(OF-185 / Q-100: `make check-prereg` currently FAILS OPEN and is owned by "
            "whoever owns src/whetstone_gate/tasks.py.)"
        )
    return (
        f"prereg-v1 resolves to {tag.stdout.strip()[:12]}; the manifest comparison is C14's "
        f"and is reported by `make check-prereg`"
    )


def genesis_hash() -> str:
    """`config/`'s ledger genesis binding, printed so pre-freeze episodes are distinguishable."""
    return str(_config.load("protocol").require("ledger.genesis_hash"))


def open_findings_counts(open_findings_md: str) -> tuple[int, dict[str, int]]:
    """Open findings and their severities, counted from `OPEN_FINDINGS.md`'s own rows.

    A row is open when its status cell says ``OPEN``. ``CLOSED`` and ``ACCEPTED`` are not, and
    a partially-closed row that still says OPEN is counted as open — which is the direction
    that does not flatter.
    """
    total = 0
    by_severity: dict[str, int] = {}
    for line in open_findings_md.splitlines():
        stripped = line.strip()
        if not stripped.startswith("| **OF-"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 7:
            continue
        status = cells[6].upper()
        if "OPEN" not in status:
            continue
        total += 1
        severity = "LOW"
        for candidate in ("HIGH", "MEDIUM", "LOW"):
            if candidate in cells[2].upper():
                severity = candidate
                break
        by_severity[severity] = by_severity.get(severity, 0) + 1
    return total, by_severity


def sorted_rows(rows: Sequence[Mapping[str, Any]]) -> tuple[Mapping[str, Any], ...]:
    """Ledger rows in ``ledger_seq`` order. **A stored file's array order is not a contract.**

    Applied by :func:`load_episodes` to every episode it reads. On a well-formed ledger this
    is a no-op — the writer emits rows in sequence — and on a malformed one it is the
    difference between a running aggregate (E2's and E3's) being computed over the episode's
    actual order and over whatever order a file happened to hold. `make eval`'s claim is
    *byte-identical* output from the same stored ledgers, and that is a claim about the rows,
    not about the JSON array they arrived in.
    """
    return tuple(sorted(rows, key=lambda row: int(row.get("ledger_seq", 0))))
