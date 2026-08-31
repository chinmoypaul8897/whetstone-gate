"""C6 — the attacker loop. Policy-blind, sliding-window, corpus-seeded.

`CONTEXT.md` §8.6, §11.3, §13.3; `PROCESS.md` §12.1's C6 row.

⚠️ **This package imports no model client.** The client is injected and mocked for every
test, and ``tests/test_c6_attacker.py`` asserts the absence over this package's own
sources and its transitive first-party imports. `PROCESS.md` §8 reserves the attacker
lanes for the sweep, and no build session may spend on them.
"""

from __future__ import annotations

from whetstone_gate.attacker.context import (
    AssembledContext,
    ContextPart,
    FoldedState,
    Origin,
    Turn,
    assemble,
    render_summary,
)
from whetstone_gate.attacker.corpus import (
    CorpusEntry,
    CorpusSource,
    CorpusUnavailable,
    InputProvenance,
    classify_provenance,
    load_entries,
    load_sources,
    seed_for_turn,
)
from whetstone_gate.attacker.estimate import (
    BudgetComparison,
    TokenEstimate,
    estimate_messages,
    estimate_text,
)
from whetstone_gate.attacker.loop import (
    AttackerSettings,
    EpisodeResult,
    ModelClient,
    StateFolder,
    ToolExecutor,
    TurnRecord,
    run_episode,
)
from whetstone_gate.attacker.texts import attacker_system_prompt

__all__ = [
    "AssembledContext",
    "AttackerSettings",
    "BudgetComparison",
    "ContextPart",
    "CorpusEntry",
    "CorpusSource",
    "CorpusUnavailable",
    "EpisodeResult",
    "FoldedState",
    "InputProvenance",
    "ModelClient",
    "Origin",
    "StateFolder",
    "TokenEstimate",
    "ToolExecutor",
    "Turn",
    "TurnRecord",
    "assemble",
    "attacker_system_prompt",
    "classify_provenance",
    "estimate_messages",
    "estimate_text",
    "load_entries",
    "load_sources",
    "render_summary",
    "run_episode",
    "seed_for_turn",
]
