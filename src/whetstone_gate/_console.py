"""ASCII-safe console output.

The operator runs these targets in Git Bash on Windows, where the console codepage
mangles the typography this project's prose uses (``—``, ``§``, ``⚠``, ``₹``). A report
the operator cannot read is a report that does not get read, and the `check-roles` output
is one of the few places where a *failure* is communicated.

So: **docstrings and Markdown keep their typography; printed output is transliterated to
ASCII at the moment of printing.** One helper, applied at the boundary, rather than
flattening the source.
"""

from __future__ import annotations

_TRANSLITERATIONS = {
    "—": "-",      # em dash
    "–": "-",      # en dash
    "…": "...",    # ellipsis
    "§": "S",      # section sign
    "·": "*",      # middle dot
    "⚠": "!",      # warning sign
    "️": "",       # variation selector-16 (the emoji tail on the warning sign)
    "→": "->",
    "≤": "<=",
    "≥": ">=",
    "₹": "Rs.",    # rupee
    "×": "x",
    "─": "-",      # box drawing light horizontal
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "±": "+/-",
    "≥": ">=",
    "τ": "tau",
    "²": "2",
    "✓": "y",
    "✗": "n",
}

_TABLE = str.maketrans(_TRANSLITERATIONS)


def ascii_safe(text: str) -> str:
    """Transliterate ``text`` to ASCII, replacing anything left over rather than failing."""
    return text.translate(_TABLE).encode("ascii", "replace").decode("ascii")


def say(text: str = "") -> None:
    """``print`` for anything a human will read off a terminal.

    Flushed, because these targets shell out to ``pytest`` and an unflushed buffer would
    print this narration *after* the subprocess output it is supposed to introduce.
    """
    print(ascii_safe(text), flush=True)
