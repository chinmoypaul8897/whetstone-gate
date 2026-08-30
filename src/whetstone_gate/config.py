"""THE ONE CONFIG LOADER.

`CLAUDE.md` hard rule 9, verbatim:

    **CONFIG, NOT CONSTANTS.** Every spec-specified value lives in `config/`, loaded
    through one loader, with **no default for a required value** — a missing value is a
    hard refusal, never a silent fallback.

This module is that one loader, and it is deliberately austere:

  * There is **no** ``get(key, default=...)``. It does not exist and must not be added.
    A caller that wants to tolerate absence must ask :meth:`Config.has` and say so out
    loud. You cannot get a silent fallback out of this API by accident, because the API
    has no place to put one.

  * A value that is **not yet determined** — the calibrated void threshold, the pilot's
    N branch, the Google API model ids, the AgentDojo/CaMeL SHAs — is written into the
    YAML as an explicit ``TODO_`` sentinel, and reading it raises
    :class:`UndeterminedValue`. "Not decided yet" is therefore a loud, typed failure at
    the point of use, not a zero that quietly propagates into a published number.

  * ``config/`` is a **pre-registration artefact** (`CONTEXT.md` §15.0). Every file under
    it is listed in `PROTOCOL.md` with the SHA-256 of its **git blob**, and
    ``make check-prereg`` recomputes them inside both ``make eval`` and ``make test``.

Why the sentinel mechanism earns its keep: the void threshold is the single number that
decides whether the whole run is publishable. If a missing threshold silently read as
``0.0``, every run would pass the void check and the project's central control would be
inert — and nothing would have raised.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import yaml

# --------------------------------------------------------------------------------------
# Errors. All of them are hard refusals; none of them has a "carry on with a default" path.
# --------------------------------------------------------------------------------------


class ConfigError(RuntimeError):
    """Base: something about `config/` is wrong and the caller must stop."""


class ConfigFileMissing(ConfigError):
    """A named config file does not exist."""


class MissingRequiredValue(ConfigError):
    """A required key is absent. Hard rule 9: this is a refusal, never a default."""


class UndeterminedValue(ConfigError):
    """A required key holds a ``TODO_`` sentinel: the value is not decided yet.

    The message names *who* decides it, so the failure is actionable rather than merely
    loud.
    """


# --------------------------------------------------------------------------------------

#: A value beginning with this prefix is declared-but-undetermined. Reading it raises.
SENTINEL_PREFIX = "TODO_"

#: Who resolves each sentinel. Keeps the failure message actionable.
_SENTINEL_OWNERS = {
    "TODO_OPERATOR": (
        "the OPERATOR — capture the exact Google API model id strings "
        "(models/gemma-…, models/gemini-…) from the dashboard. "
        "CONTEXT.md §13.3.2; QUESTIONS.md Q-006"
    ),
    "TODO_C14_CALIBRATION": (
        "C14 — the arm-1 calibration sets it to the 95% Wilson LOWER bound rounded DOWN "
        "to 5 pp, after `probe-v1` is cut, and it is SINGLE-SHOT (CLAUDE.md §3)"
    ),
    "TODO_C14_PILOT": (
        "C14 — the pilot's MEASURED tokens/episode selects the N branch by the "
        "CONTEXT.md §13.4 rule. Never by preference, never by schedule pressure"
    ),
    "TODO_C13_C16": "C13 / C16 — pin at the SHA actually vendored",
    "TODO_C13_RUN1": (
        "C13 / RUN-1 — the 90-minute timeboxed CaMeL branch test on 31 Aug decides "
        "Branch A (live) or Branch B (citation). Branch B is published as a result"
    ),
}

#: ⚠️ **REQUIRED, and the distinction is load-bearing rather than tidy.**
#:
#: These files are **pre-registration artefacts** (`CONTEXT.md` §15.0). A sweep that skips
#: one it cannot open reports a **smaller number than the truth**, which is `CLAUDE.md` hard
#: rule 11's shape applied to a check's own denominator. That is exactly what happened:
#: :func:`outstanding_sentinels` carried a blanket ``if not path.is_file(): continue``,
#: written so a legitimately-absent ``ladder.yaml`` was not an error — and it **silently
#: excused `protocol.yaml` too**, so with that file deleted `check-roles` printed
#: *"PASS F1 config/ loads — protocol.yaml and lanes.yaml parse"*, five sentinels vanished
#: from the count **including the void threshold**, and the process **exited 0**.
#: `REVIEW_C0.md` **B-03**; `ARCHITECT_CHECK_0.md` §3; `INCIDENTS.md` **INC-14**.
REQUIRED_CONFIGS: tuple[str, ...] = ("protocol", "lanes")

#: **NOT YET WRITTEN, by plan, with the chunk that writes it named.** An absent file here is
#: reported as *not yet* — never as *nothing*, and never as a pass. If one appears early it
#: is loaded and swept like any other.
NOT_YET_CONFIGS: dict[str, str] = {
    "ladder": (
        "C15 — the attacker-strength ladder harness. Absent until then, by plan, and its "
        "absence is REPORTED rather than skipped"
    ),
}

#: The config files this project reads. There are no others.
KNOWN_CONFIGS: tuple[str, ...] = REQUIRED_CONFIGS + tuple(NOT_YET_CONFIGS)


def config_dir() -> Path:
    """Return the repository's ``config/`` directory.

    Honours ``WHETSTONE_CONFIG_DIR`` so a test can point at a fixture directory without
    monkey-patching the loader. **It supplies no default value for anything** — it only
    says *where* to read, never *what* to read.
    """
    override = os.environ.get("WHETSTONE_CONFIG_DIR")
    if override:
        return Path(override)
    return repo_root() / "config"


def repo_root() -> Path:
    """Return the repository root, resolved from this file's location.

    ``src/whetstone_gate/config.py`` → up three parents. Deliberately not derived from
    the current working directory, so ``make`` and a bare ``python -m`` agree.
    """
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Config:
    """One parsed config file.

    Access is through :meth:`require` alone. There is no defaulting accessor by design.
    """

    name: str
    path: Path
    data: dict

    # -- the only read path ------------------------------------------------------------

    def require(self, dotted: str) -> Any:
        """Return the value at ``dotted`` (e.g. ``"money.per_action_cap_paise"``).

        Raises :class:`MissingRequiredValue` if any segment is absent, and
        :class:`UndeterminedValue` if the value is a ``TODO_`` sentinel. **It never
        returns a default, because it has none to return.**
        """
        node: Any = self.data
        walked: list[str] = []
        for segment in dotted.split("."):
            walked.append(segment)
            if not isinstance(node, dict) or segment not in node:
                raise MissingRequiredValue(
                    f"{self.path.name}: required value '{dotted}' is missing "
                    f"(stopped at '{'.'.join(walked)}'). "
                    f"Hard rule 9: a missing required value is a hard refusal, never a "
                    f"silent fallback. Add it to {self.path}, or — if it is not yet "
                    f"decided — write an explicit {SENTINEL_PREFIX}… sentinel."
                )
            node = node[segment]

        if is_sentinel(node):
            owner = _SENTINEL_OWNERS.get(node, "an unrecorded owner — this is itself a defect")
            raise UndeterminedValue(
                f"{self.path.name}: '{dotted}' is not determined yet (sentinel {node!r}). "
                f"Resolved by: {owner}. "
                f"Hard rule 9 forbids substituting a value here."
            )
        return node

    def has(self, dotted: str) -> bool:
        """True if ``dotted`` resolves to a real, determined value.

        The explicit way to tolerate absence. A caller that uses this is *saying so*,
        which is the whole point.
        """
        try:
            self.require(dotted)
        except ConfigError:
            return False
        return True

    def sentinels(self) -> Iterator[tuple[str, str]]:
        """Yield ``(dotted_path, sentinel)`` for every undetermined value in this file."""
        yield from _walk_sentinels(self.data, prefix="")


def is_sentinel(value: Any) -> bool:
    """True if ``value`` is a declared-but-undetermined ``TODO_`` marker."""
    return isinstance(value, str) and value.startswith(SENTINEL_PREFIX)


def _walk_sentinels(node: Any, prefix: str) -> Iterator[tuple[str, str]]:
    if is_sentinel(node):
        yield (prefix, node)
    elif isinstance(node, dict):
        for key, child in node.items():
            yield from _walk_sentinels(child, f"{prefix}.{key}" if prefix else str(key))
    elif isinstance(node, list):
        for index, child in enumerate(node):
            # Name the list item when it has a name, so an operator reading
            # "lanes[gemma-26b].api_model_id" knows which dashboard row to open.
            label = child["name"] if isinstance(child, dict) and "name" in child else index
            yield from _walk_sentinels(child, f"{prefix}[{label}]")


def load(name: str) -> Config:
    """Load ``config/<name>.yaml``.

    Not cached: these files are tiny, and a cache would let a stale read outlive an edit
    during a long run. Determinism matters more here than microseconds.
    """
    if name not in KNOWN_CONFIGS:
        raise ConfigError(
            f"unknown config {name!r}; this project reads exactly {KNOWN_CONFIGS}. "
            f"Adding one is a Class A deviation and needs an architect ruling."
        )
    path = config_dir() / f"{name}.yaml"
    if not path.is_file():
        raise ConfigFileMissing(
            f"{path} does not exist. config/ is a pre-registration artefact "
            f"(CONTEXT.md §15.0); it is not optional and has no fallback."
        )
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ConfigError(f"{path} did not parse to a mapping (got {type(data).__name__}).")
    return Config(name=name, path=path, data=data)


@dataclass(frozen=True)
class Sweep:
    """What a full pass over ``config/`` found — **including what it could not read**.

    The old sweep returned only the sentinel list, so *"no undetermined values remain"* and
    *"I did not open the file that holds them"* were the same answer. This type makes the
    denominator explicit, which is `CLAUDE.md` hard rule 11 applied to a check.
    """

    outstanding: tuple[tuple[str, str, str], ...]
    """``(config_name, dotted_path, sentinel)`` for every undetermined value found."""

    loaded: tuple[str, ...]
    """The config files actually opened and parsed. F1 reports **this**, not a fixed string."""

    not_yet: tuple[tuple[str, str], ...]
    """``(config_name, who writes it)`` for a NOT-YET file that is legitimately absent."""


def sweep_configs() -> Sweep:
    """Sweep every config file for undetermined values.

    ⚠️ **A missing REQUIRED config is a hard refusal, raised, not skipped.** ``load()``
    already raises :class:`ConfigFileMissing`; the old sweep **deliberately bypassed the
    loader's own refusal** with a blanket ``if not path.is_file(): continue``, so deleting
    a pre-registration artefact made the count go DOWN and the process still exit 0. A
    NOT-YET file is a different thing and is reported as one.
    """
    found: list[tuple[str, str, str]] = []
    loaded: list[str] = []
    not_yet: list[tuple[str, str]] = []
    for name in KNOWN_CONFIGS:
        path = config_dir() / f"{name}.yaml"
        if name in NOT_YET_CONFIGS and not path.is_file():
            not_yet.append((name, NOT_YET_CONFIGS[name]))
            continue
        cfg = load(name)  # RAISES ConfigFileMissing on a REQUIRED file that is not there
        loaded.append(name)
        for dotted, sentinel in cfg.sentinels():
            found.append((name, dotted, sentinel))
    return Sweep(tuple(found), tuple(loaded), tuple(not_yet))


def outstanding_sentinels() -> list[tuple[str, str, str]]:
    """Return ``(config_name, dotted_path, sentinel)`` for every undetermined value.

    Used by ``check-roles`` and by the operator-gate test, so that "somebody still owes
    this project a value" is a number the repository can print rather than a thing
    somebody has to remember. **Raises if a REQUIRED config file is absent** — see
    :func:`sweep_configs`.
    """
    return list(sweep_configs().outstanding)
