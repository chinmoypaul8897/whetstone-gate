"""AN INDEPENDENT RE-IMPLEMENTATION of hard rule 9's required-value refusal.

Written by the C0 REVIEW session (SESSION-TOKEN 52f5307b) from the SPEC TEXT ONLY:

  CLAUDE.md hard rule 9 / PROCESS.md §4.9 —
    "Every spec-specified value lives in `config/`, loaded through one loader, with
     **no default for a required value** — a missing value is a hard refusal, never a
     silent fallback."

  PROCESS.md §12.1, C7 done-when —
    "a missing `genesis_hash` in config is a hard refusal, not a default"

  PROCESS.md §5.1 —
    "the ledger ... rooted at a genesis hash loaded from `config/` with no default"

It imports NOTHING from whetstone_gate. Its only job is to be diffed against theirs.

MY READING, stated before I looked at their behaviour:

  R1  An absent key is missing.                        -> refuse
  R2  A key written down with NO VALUE (`k:`, `null`,
      `~`) is a value nobody has supplied. That is
      the literal meaning of "a missing value".        -> refuse
  R3  A required STRING that is empty or whitespace-
      only is missing. `genesis_hash: ""` roots the
      chain at nothing, silently.                      -> refuse
  R4  `0`, `0.0`, `False`, `[]`, `{}` are DETERMINED
      values and must be returned. Truthiness is the
      classic way this rule is got wrong.              -> return
  R5  A declared-undetermined marker is missing, and
      the marker is matched CASE-INSENSITIVELY: a
      config author who types `todo_operator` has
      declared it undetermined just as loudly.         -> refuse
  R6  A missing config FILE is a refusal EVERYWHERE it
      is read, including in any "what is still
      outstanding" sweep. A sweep that skips a file it
      cannot open reports a smaller number than the
      truth, which is hard rule 11's shape.            -> refuse
"""

from __future__ import annotations
import re
from pathlib import Path
import yaml

_TODO = re.compile(r"^todo_", re.IGNORECASE)


class Refusal(RuntimeError):
    pass


def load(path: Path) -> dict:
    if not path.is_file():
        raise Refusal(f"R6: {path} does not exist; config/ has no fallback")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise Refusal(f"R6: {path} is not a mapping")
    return data


def require(data: dict, dotted: str):
    node = data
    for seg in dotted.split("."):
        if not isinstance(node, dict) or seg not in node:
            raise Refusal(f"R1: '{dotted}' is absent")
        node = node[seg]
    if node is None:
        raise Refusal(f"R2: '{dotted}' is written down with no value (YAML null)")
    if isinstance(node, str):
        if not node.strip():
            raise Refusal(f"R3: '{dotted}' is an empty/whitespace string")
        if _TODO.match(node):
            raise Refusal(f"R5: '{dotted}' is a declared-undetermined marker {node!r}")
    return node  # R4: 0, False, [], {} are determined and come back


def outstanding(paths: dict[str, Path], known: tuple[str, ...]) -> list[tuple[str, str, str]]:
    found = []
    for name in known:
        p = paths[name]
        if not p.is_file():
            raise Refusal(f"R6: cannot sweep {name}: {p} is missing — a sweep that "
                          f"skips a file it cannot open under-reports the truth")
        for dotted, value in _walk(load(p), ""):
            found.append((name, dotted, value))
    return found


def _walk(node, prefix):
    if isinstance(node, str) and _TODO.match(node):
        yield (prefix, node)
    elif node is None and prefix:
        yield (prefix, "<YAML NULL — undetermined>")
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from _walk(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            label = v["name"] if isinstance(v, dict) and "name" in v else i
            yield from _walk(v, f"{prefix}[{label}]")
