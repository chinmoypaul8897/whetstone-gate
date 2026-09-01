"""**THE THIN OUTER SHELL — the only module in this package that touches a filesystem.**

Hard rule 8: *"Core logic takes data in and returns results — no I/O, clock, network, or
randomness inside it. Side effects live in a thin outer shell."* This module is that shell for
**this package's own data** — the stored episode — and it does nothing else.

⚠️ **SCOPE, STATED SO THE CLAIM IS NOT LARGER THAN THE CHECK, which is the shape
`tests/test_c2_world.py` already uses for the world.** :mod:`~whetstone_gate.ledger.entry` and
:mod:`~whetstone_gate.ledger.build` open nothing at all. :mod:`~whetstone_gate.ledger.chain`
opens nothing **directly** and has exactly one indirect read:
:func:`~whetstone_gate.ledger.chain.load_chain_spec` calls
:func:`whetstone_gate.config.load`, which reads `config/protocol.yaml`. **That is the one
loader, it is the project's outer shell for configuration, and reading it is what a shell is
for** — hard rule 9 requires the genesis root to come from `config/` and nowhere else, so the
read is not incidental, it is the rule. What would be a defect is a *core* function taking a
path or writing a file, and none does. `tests/test_c7_ledger.py::test_only_the_shell_touches_a_filesystem`
scans for the direct form and says in its own docstring that the indirect one is out of scope,
rather than leaving a reader to infer a stronger claim than the scan supports.

**Why the package ships a document shape at all.** `PROCESS.md` §12.1's C17 row: the replay
renderer *"Reads `evals/episodes/` **only**"*, makes no network call and runs no model; hard
rule 10 requires *"atomic writes, publish-on-complete"* and *"idempotent (re-run = zero
duplicates)"*; and `CONTEXT.md` §20's `make eval` regenerates every published figure from the
stored ledgers. A hash chain nobody can store is a substrate for nothing, and if this chunk
does not define the document, three later chunks each define a different one.

**The shape is read off golden 5 rather than invented.** That file is itself a stored ledger:
``genesis_hash`` beside a ``ledger`` array of entries. This document is those two keys plus the
three facts a reader needs in order to verify and caption an episode without consulting
``config/`` — which matters because ``ledger.genesis_hash`` **changes at C14**, so a ledger that
did not record the root it actually chained from would stop verifying the moment the freeze
landed. That is the whole of `config/protocol.yaml`'s *"pre-freeze episodes are
CRYPTOGRAPHICALLY DISTINGUISHABLE from scored ones"*: distinguishable requires that each
episode state which root it used.

    {"genesis_hash": …, "hash_algorithm": …, "seed": …, "arm": …, "ledger": [ … ]}

``arm`` is at the document level **and** on every entry, and :func:`from_document` checks that
they agree. The redundancy is deliberate — it is the one place a mixed-arm file would be
detectable by a reader who is not recomputing anything.

⚠️ **`evals/` IS APPEND-ONLY (`CLAUDE.md` §4): "Never delete, rewrite or truncate a completed
episode's output."** :func:`write` therefore **refuses to overwrite** a file whose bytes differ
and treats an identical re-write as the no-op hard rule 10's idempotence asks for. Deletion is
operator-only and there is no code for it here.

⚠️ **NEWLINES ARE LF, EXPLICITLY.** ``open(..., newline="\\n")``. The default on Windows
translates ``\\n`` to ``\\r\\n``, and `PROCESS.md` §6a records what that costs: the working tree
and the git object store then disagree, and the pre-registration fingerprint a reviewer
recomputes on Linux stops matching the one this machine published.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from .chain import ChainSpec, Ledger, rebuild

#: The key golden 5 uses for the array of entries. Kept, rather than renamed to "entries",
#: so a stored document and the golden read the same way.
LEDGER_KEY = "ledger"

DOCUMENT_KEYS: tuple[str, ...] = (
    "genesis_hash",
    "hash_algorithm",
    "seed",
    "arm",
    LEDGER_KEY,
)


class LedgerStoreError(RuntimeError):
    """The document cannot be written or read as specified. Always a refusal."""


def to_document(ledger: Ledger) -> dict[str, Any]:
    """The ledger as the mapping that is written to ``evals/episodes/``. **Pure.**"""
    return {
        "genesis_hash": ledger.genesis_hash,
        "hash_algorithm": ledger.algorithm,
        "seed": ledger.seed,
        "arm": ledger.arm,
        LEDGER_KEY: [entry.to_dict() for entry in ledger.entries],
    }


def from_document(document: Mapping[str, Any]) -> Ledger:
    """Rebuild a :class:`~whetstone_gate.ledger.chain.Ledger` from a stored document. **Pure.**

    ⚠️ **THE STORED CHAIN IS VERIFIED FIRST AND A TAMPERED DOCUMENT IS A REFUSAL**
    (:class:`~whetstone_gate.ledger.chain.TamperDetected`), not a happy object. See
    :func:`whetstone_gate.ledger.chain.rebuild` and `INCIDENTS.md` **INC-33** for what this
    function used to do instead, which was to launder every mutation it was handed.

    ⚠️ **AND A DOCUMENT WHOSE CHAIN IS PERFECT BUT WHOSE ENTRIES PRE-DATE `QUESTIONS.md` Q-062
    AND Q-066 IS A DIFFERENT REFUSAL** — :class:`~whetstone_gate.ledger.entry.LedgerEntryError`,
    naming the schema and **both** fields it is missing. `tests/goldens/golden5_tamper.json` is
    exactly such a document: thirteen content fields — this schema minus
    :data:`~whetstone_gate.ledger.entry.WIDENED_FIELDS` — an intact chain, and
    :func:`whetstone_gate.ledger.chain.verify` still returns its four stored verdicts. **The two refusals are kept apart on purpose**: calling an untampered
    document tampered would put a false accusation in front of a reviewer verifying a published
    episode, which is the audience `PROCESS.md` §6a.3 exists for.

    ``genesis_hash`` and ``hash_algorithm`` come from the **document**, which is what lets a
    pre-freeze episode still verify after C14 moves `config/`'s root. They are not trusted
    blindly: entry 1's ``prev_hash`` must equal the stated root and every digest must recompute
    under the stated algorithm, so a document that names the wrong root or algorithm fails.
    """
    missing = [key for key in DOCUMENT_KEYS if key not in document]
    if missing:
        raise LedgerStoreError(f"stored ledger is missing {missing}")
    entries = document[LEDGER_KEY]
    if not isinstance(entries, list):
        raise LedgerStoreError(
            f"{LEDGER_KEY!r} must be a list of entries, got {type(entries).__name__}"
        )
    seed = document["seed"]
    if not isinstance(seed, int) or isinstance(seed, bool):
        # ⚠️ The seed is the input that REGENERATES the world the replay scores against, and it
        # is the one document key no digest covers (see this module's docstring). Its type is
        # checked here because "banana" would otherwise be written straight back out.
        raise LedgerStoreError(
            f"stored ledger carries seed={seed!r}, which is not a seed. It is the input that "
            f"regenerates the world every later number is scored against."
        )
    spec = ChainSpec(
        genesis_hash=document["genesis_hash"], algorithm=document["hash_algorithm"]
    )
    return rebuild(entries, spec=spec, seed=seed, arm=document["arm"])


def render(ledger: Ledger) -> str:
    """The document's exact bytes, as text: JSON, two-space indent, one trailing newline."""
    return json.dumps(to_document(ledger), indent=2, ensure_ascii=False) + "\n"


def write(path: Path, ledger: Ledger) -> bool:
    """Publish ``ledger`` to ``path`` atomically. Returns True if bytes were written.

    **Publish-on-complete**: the document is written to a sibling temporary file and moved into
    place with :func:`os.replace`, which is atomic on both POSIX and Windows, so a reader never
    observes a half-written episode.

    **Idempotent**: an existing file with identical bytes is left alone and ``False`` is
    returned. An existing file with *different* bytes is a refusal — see this module's
    docstring on `evals/` being append-only.
    """
    text = render(ledger)
    if path.exists():
        if path.read_bytes() == text.encode("utf-8"):
            return False
        raise LedgerStoreError(
            f"{path} already exists with different contents. `evals/` is append-only "
            f"(CLAUDE.md §4): a completed episode's output is never rewritten or truncated, "
            f"and deletion is operator-only."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    os.replace(temporary, path)
    return True


def read(path: Path) -> Ledger:
    """Read a stored ledger back. **Raises on a document whose chain does not verify.**

    Use :func:`read_document` + :func:`stored_entries` +
    :func:`whetstone_gate.ledger.chain.verify` when what is wanted is a *verdict* about a file
    rather than a ledger built from it.
    """
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise LedgerStoreError(f"{path} did not parse to a mapping")
    return from_document(document)


def read_document(path: Path) -> dict[str, Any]:
    """The raw document, **without** rebuilding anything.

    This is what a **reporting** verifier wants: it must be handed the bytes as they are
    stored, tampering included, so it can say *where* the chain broke.
    :func:`read` **raises** :class:`~whetstone_gate.ledger.chain.TamperDetected` on such a
    document, which is right for a caller that wants a ledger and wrong for one that wants a
    verdict — so both paths exist and each says which it is.
    """
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise LedgerStoreError(f"{path} did not parse to a mapping")
    return document


def stored_entries(document: Mapping[str, Any]) -> list[Any]:
    """The entry rows of a raw document, for :func:`whetstone_gate.ledger.chain.verify`.

    ⚠️ **The rows are handed over UNCOERCED.** ``dict(row)`` on a row that is a string or an
    integer raises, and this function sits on the exact path a verifier uses to report on a
    file somebody may have edited — so coercing here would turn *"that is not an entry"* from
    a verdict into a traceback, which is the thing
    :func:`whetstone_gate.ledger.chain.verify` was made total to avoid.
    """
    entries = document.get(LEDGER_KEY)
    if not isinstance(entries, list):
        raise LedgerStoreError(f"{LEDGER_KEY!r} is not a list of entries")
    return list(entries)
