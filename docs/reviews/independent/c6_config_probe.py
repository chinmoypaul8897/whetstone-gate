"""A one-shot probe run in a SEPARATE INTERPRETER against an ALTERED ``config/``.

⚠️ Why a subprocess rather than ``monkeypatch.setenv``. C6's own
``test_the_window_sizes_are_read_from_config_and_not_from_source`` sets the env var inside
the *running* interpreter, where ``whetstone_gate.config`` may already have cached a load.
A fresh process cannot be fooled that way, so this is the stronger form of the same proof:
point the loader at a file whose numbers differ and watch the BEHAVIOUR change.

It prints one line of JSON and nothing else, so its caller can parse it.
Invoked by ``c6_summary_and_calls.py``; not useful on its own.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from whetstone_gate.attacker import context as ctx  # noqa: E402
from whetstone_gate.attacker.loop import AttackerSettings, run_episode  # noqa: E402

from c6_blindness import TOOL_SCHEMAS, Folder, RecordingClient  # noqa: E402


class _Executor:
    def execute(self, attacker_text: str) -> str:
        return "r"


def main() -> int:
    settings = AttackerSettings.from_config()
    client = RecordingClient([f"a{i:03d}" for i in range(40)])
    result = run_episode(
        client=client,
        executor=_Executor(),
        settings=settings,
        tool_schemas_text=TOOL_SCHEMAS,
        corpus_entries=(),
        fold=Folder(),
    )
    print(json.dumps({
        "turn_budget": settings.turn_budget,
        "verbatim": settings.verbatim_turns,
        "cap": settings.summary_token_cap,
        "temperature": settings.temperature,
        "calls": len(client.messages),
        "kept": len([p for p in result.contexts[-1].parts if p.origin is ctx.Origin.ATTACKER]),
        "summary_chars": max(
            len(p.text) for c in result.contexts for p in c.parts
            if p.label.startswith("deterministic summary")
        ),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
