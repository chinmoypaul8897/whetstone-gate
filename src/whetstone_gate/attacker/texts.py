"""The `CONTEXT.md` §8.6 authored texts, loaded from ``data/`` as FILES.

``spec_constants.AUTHORED_TEXTS`` already states why they are files and never string
literals in source, and the reason is worth repeating at the place that reads them:

    a copy in source is the same defect as a hardcoded number, and a drifted copy of the
    policy string would silently change what every arm was shown while every test still
    passed.

So this module holds **no text**. It holds three paths — and it takes even those from
``spec_constants.AUTHORED_TEXTS`` rather than restating them, because a second list of
the same filenames is a second thing that can drift.

⚠️ **Only one of the three is this package's to USE.** ``attacker_sys.txt`` is the
attacker's system prompt. ``policy.txt`` and ``arm3_safety.txt`` are **C9's**: they are
created here because they are §8.6 texts and C6 is the first chunk that needs the
file-loading mechanism at all, and they are loadable here so that the policy-blindness
tests can assert, against the real bytes, that **no clause of the real policy** reaches
the attacker's context. Loading the policy in order to prove the attacker never sees it
is the one legitimate use this package has for it, and
:func:`whetstone_gate.attacker.context.AssembledContext` is where that proof lives.

**No I/O beyond reading these three files, and no clock, network or randomness** — hard
rule 8. The read is a pure function of the repository contents.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from whetstone_gate.config import repo_root
from whetstone_gate.spec_constants import AUTHORED_TEXTS

#: The attacker's system prompt — the ONLY one of the three this package sends to a model.
ATTACKER_SYS = "data/attacker_sys.txt"

#: C9's, loaded here only so a test can prove the attacker never sees them.
POLICY = "data/policy.txt"
ARM3_SAFETY = "data/arm3_safety.txt"


class AuthoredTextMissing(RuntimeError):
    """An authored text file is absent.

    A hard refusal, deliberately: hard rule 9's shape applied to a TEXT rather than a
    number. An attacker that silently ran with an empty system prompt would reproduce
    `INCIDENTS.md` **INC-01** exactly — a competent-looking zero — because the tradecraft
    paragraph is the entire difference between 0/20 and 16/20.
    """


@dataclass(frozen=True)
class AuthoredText:
    """One §8.6 text, with the bytes that were actually read."""

    rel_path: str
    text: str

    @property
    def sha256(self) -> str:
        import hashlib

        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


@lru_cache(maxsize=None)
def load(rel_path: str) -> AuthoredText:
    """Load one authored text by its repository-relative path.

    Only the three paths in ``AUTHORED_TEXTS`` are loadable. Anything else raises, so a
    typo cannot quietly become a fourth authored text that no test compares to the spec.
    """
    if rel_path not in AUTHORED_TEXTS:
        raise AuthoredTextMissing(
            f"{rel_path!r} is not one of the CONTEXT.md §8.6 authored texts "
            f"{AUTHORED_TEXTS}. Adding a fourth is a Class A deviation: every one of "
            f"these is compared character-by-character against §8.6 by a test, and a "
            f"path no test knows about is a text nothing checks."
        )
    path = repo_root() / rel_path
    if not path.is_file():
        raise AuthoredTextMissing(
            f"{path} does not exist. It is a CONTEXT.md §8.6 authored text and it has no "
            f"fallback: running the attacker without its tradecraft paragraph is "
            f"INCIDENTS.md INC-01, which scored 0 escapes in 20 episodes and read as a "
            f"perfect defence."
        )
    # Bytes, then an explicit UTF-8 decode. Never Path.read_text() with platform newline
    # translation — INCIDENTS.md INC-16 is that exact API rewriting every line ending in
    # a tracked file on this machine.
    return AuthoredText(rel_path=rel_path, text=path.read_bytes().decode("utf-8"))


def attacker_system_prompt() -> str:
    """The attacker's system prompt, verbatim from ``data/attacker_sys.txt``."""
    return load(ATTACKER_SYS).text
