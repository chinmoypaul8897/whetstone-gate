"""Shared fixtures.

Deliberately thin: C0 builds a skeleton, and a fat conftest is where scope creep hides.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from whetstone_gate import config as cfg
from whetstone_gate.spec_constants import TRIPWIRE_SELF_EXCLUSION


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return cfg.repo_root()


@pytest.fixture(scope="session")
def implementation_sources(repo_root: Path) -> list[Path]:
    """Every first-party **implementation** ``.py`` file the tripwire scans.

    Scope, and why it is drawn here:

      * ``src/`` and ``docs/render/`` are in. They are the code that *runs the
        experiment*, and hard rule 9's risk is precisely that one of them reads a spec
        value from a literal instead of from ``config/``.
      * ``tests/`` is **out**. A test that asserts ``per_action_cap_paise == 5000000`` is
        not a hardcoding defect — it is the check that ``config/`` still says what the
        spec says, which is the thing rule 9 wants. Scanning tests would make the only
        possible remedy "delete the assertion", i.e. hard rule 6's forbidden move.
      * ``vendor/`` and ``.venv/`` are out. Somebody else's code at a pinned SHA, which
        C13's done-when requires to diff **empty** against that SHA.
      * ``spec_constants.py`` is out — it *is* the registry, so it necessarily contains
        every literal the tripwire hunts. ``test_tripwire_registry`` asserts that this
        exclusion list has exactly one entry, so it cannot grow into an amnesty.
    """
    roots = [repo_root / "src", repo_root / "docs" / "render"]
    files: list[Path] = []
    for root in roots:
        if root.is_dir():
            files.extend(
                p
                for p in root.rglob("*.py")
                if ".venv" not in p.parts and "vendor" not in p.parts
            )
    excluded = repo_root / TRIPWIRE_SELF_EXCLUSION
    return sorted(p for p in files if p.resolve() != excluded.resolve())
