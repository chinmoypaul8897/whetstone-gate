"""**THE REDACTION REFUSAL — no key value reaches a log or a checkpoint.**

`CLAUDE.md` §4: *"Never read, print, echo or commit `.env` or any API key value … Secrets
never in the repo, never in logs, never in reports."*

:mod:`.keys` makes it impossible for the runner to **obtain** a key value. This module is the
second half of the same guarantee, and it exists because the first half only covers the paths
this package controls: a caller can hand the runner a payload that already contains a key —
an echoed request header, a provider error message quoting the credential it rejected, a
config dictionary somebody widened. Every checkpoint and every usage row passes through
:func:`refuse_if_secret_bearing` **before** it is serialised.

⚠️ **IT REFUSES; IT DOES NOT MASK.** A masking helper would write the record with ``***`` in
it and carry on, which means the run continues in a state where something upstream is putting
credentials into episode data and nobody is told. A refusal stops the write and names the
field. `CLAUDE.md` §4's own instruction on this class of thing: *"STOP and report instead of
working around it."*

⚠️ **AND THE ERROR MESSAGE NAMES THE FIELD, NEVER THE VALUE.** A refusal that printed what it
found would put the secret in the traceback, in the pytest output, and in whatever CI log
caught it — which is the failure it exists to prevent, committed by the check itself.

**What it looks for**, and the honest limit of each:

  * **Provider key prefixes.** Groq issues ``gsk_``-prefixed keys and Google's AI Studio keys
    begin ``AIza``. Both are public, documented prefixes; neither is a secret, and neither is
    a key. ⚠️ **This is a prefix scan, not a validator** — it catches a real key of either
    shape and says nothing about a key whose shape changes.
  * **The environment-variable names themselves**, appearing as a *value* rather than a key
    name. ``{"note": "GROQ_API_KEY=..."}`` is somebody echoing a dotenv line.
  * **Any value that equals a set environment variable's value.** ⚠️ **This one is exact and
    it is the strongest of the three**, because it needs no knowledge of any provider's key
    format — but it can only compare, never read out: the comparison happens inside this
    module and neither operand leaves it.

⚠️ **WHAT THIS DOES NOT CLOSE, SAID PLAINLY:** a key that is not in this process's environment,
not of a known prefix shape, and not equal to anything set — a colleague's key pasted into a
prompt corpus, say — passes. The scan is a guard against the realistic accident, not a proof.
Saying so here is `PROCESS.md` §9's rule applied to a safety check: *"Every evidence pack
states what it is NOT."*
"""

from __future__ import annotations

import os
from typing import Any

#: Documented public prefixes of the two providers this project uses. Neither is a secret.
_KEY_PREFIXES: tuple[str, ...] = ("gsk_", "AIza")

#: The suffix every one of this project's key variables ends in. See :mod:`.keys`.
_KEY_NAME_SUFFIX = "_API_KEY"

#: Below this length a string cannot be a credential and comparing it to one would fire on
#: every empty or one-character field. A set-but-empty environment variable is the case that
#: made this necessary: ``"" == ""`` matches every blank string in the document.
_MIN_SECRET_LENGTH = 8


class SecretInPayload(RuntimeError):
    """A payload carried something that looks like a credential. **Always a refusal.**

    ⚠️ The message names the **field path** and the **reason**. It never carries the value.
    """


def _looks_like_a_key(value: str) -> str | None:
    """Return the REASON this string looks like a credential, or ``None``. Never the value."""
    if len(value) < _MIN_SECRET_LENGTH:
        return None
    for prefix in _KEY_PREFIXES:
        if value.startswith(prefix):
            return f"begins with the documented provider key prefix {prefix!r}"
    if _KEY_NAME_SUFFIX in value:
        return (
            f"contains {_KEY_NAME_SUFFIX!r} as part of a VALUE, which is what an echoed "
            f".env line looks like"
        )
    for name, env_value in os.environ.items():
        if not name.endswith(_KEY_NAME_SUFFIX):
            continue
        if len(env_value) >= _MIN_SECRET_LENGTH and value == env_value:
            return (
                f"is byte-identical to the value of the environment variable {name!r}. "
                f"⚠️ NEITHER VALUE IS REPRODUCED IN THIS MESSAGE"
            )
    return None


def refuse_if_secret_bearing(payload: Any, *, where: str = "$") -> None:
    """Walk ``payload`` and **raise** if any string in it looks like a credential.

    Recurses through mappings, sequences and their keys. ``where`` accumulates the field path
    so the refusal is actionable — *"the third checkpoint field"* is not a bug report.

    Returns ``None`` on a clean payload, so it reads as an assertion at a call site and cannot
    be mistaken for a sanitiser that returns a cleaned copy.
    """
    if isinstance(payload, str):
        reason = _looks_like_a_key(payload)
        if reason is not None:
            raise SecretInPayload(
                f"REFUSED: the value at {where} {reason}. CLAUDE.md S4: 'Never read, print, "
                f"echo or commit .env or any API key value … Secrets never in the repo, "
                f"never in logs, never in reports.' This is a REFUSAL, not a masking: the "
                f"write does not happen and the value is not reproduced here. Find what put "
                f"a credential into runner data and stop it there"
            )
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            refuse_if_secret_bearing(key, where=f"{where}.<key>")
            refuse_if_secret_bearing(value, where=f"{where}.{key}")
        return
    if isinstance(payload, (list, tuple, set, frozenset)):
        for index, value in enumerate(payload):
            refuse_if_secret_bearing(value, where=f"{where}[{index}]")
        return
    return
