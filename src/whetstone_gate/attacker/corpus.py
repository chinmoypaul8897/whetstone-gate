"""The seeded attack corpora — pinned, verified by hash, and NEVER committed.

`CONTEXT.md` §11.3: *"The attacker composes and adapts from published corpora; it does not
invent from a blank page and it never sees our policy."* The four corpora are
**InjecAgent**, the **AgentDojo** injection corpus, **AgentHarm** and **Agent Security
Bench**. Their licences are recorded first-hand in `PROVENANCE.md` §3.3 and their pins,
fetch commands and verification in `corpora/MANIFEST.md`.

⚠️ **R-Judge is CITED, NEVER VENDORED — it ships no licence file of any kind**, verified
first-hand (`PROVENANCE.md` §3.3). Nothing in this module fetches it and nothing may.

---

## Why the payloads are not in this repository

`QUESTIONS.md` **Q-010**, ruled: **pin, do not commit.** The manifest carries every source,
its exact SHA, the fetch commands and the verification; the third party's bytes do not
ship. Three further reasons apply specifically here and are recorded in
``docs/sessions/c6-build-1.txt``:

  * **AgentHarm's licence carries a field-of-use clause** and its payload is a
    harmful-behaviour corpus. This repository **flips public on 4 September**
    (`CLAUDE.md` §5). Pinning rather than republishing is the conservative direction and
    costs nothing this project needs.
  * AgentHarm ships a ``canary_guid`` — a contamination canary. Republishing it would
    damage somebody else's benchmark.
  * A pin cannot drift; a committed copy can be edited quietly. That is Q-010's own
    reasoning and it is exactly why the corpus/improvisation fraction (§11.3) is
    checkable at all.

⚠️ **A MISSING CORPUS IS A LOUD FAILURE, NEVER AN EMPTY LIST.** If the fetched tree is
absent, :func:`load_entries` raises and names the fetch command. It must never return
zero entries, because zero entries would make §11.3's published split read *"100%
improvised"* — a headline number produced by a broken instrument, which is `INCIDENTS.md`
**INC-01** exactly, and `CLAUDE.md` hard rule 11's shape applied to a corpus rather than a
denominator.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from whetstone_gate.config import repo_root

#: Our selection record. Ours, so it is committed; the third party's bytes are not.
SEED_INDEX = "corpora/seed_index.json"

#: Where the fetched trees land. Git-ignored — see ``corpora/.gitignore``.
FETCHED_ROOT = "corpora/fetched"


class CorpusUnavailable(RuntimeError):
    """A pinned corpus file is absent or its bytes do not match the pinned hash.

    A hard refusal. See this module's docstring: an empty corpus is a broken instrument
    that publishes a flattering number.
    """


class InputProvenance(Enum):
    """⚠️ `CONTEXT.md` §11.3's instrumented split, as a type.

    *"Report the split — what fraction of successful attacks came from a seeded corpus
    versus the attacker's own improvisation. That number is itself interesting and nobody
    has published it."*

    **C18 publishes the fraction, so the field must exist in the record from the first
    episode** — a fraction cannot be recovered afterwards from transcripts that never
    carried it.
    """

    CORPUS = "corpus"
    IMPROVISED = "improvised"


@dataclass(frozen=True)
class CorpusSource:
    """One row of ``corpora/seed_index.json``: a pinned file inside a pinned tree."""

    corpus: str
    origin_url: str
    pin: str
    path: str
    sha256: str
    adapter: str
    licence: str


@dataclass(frozen=True)
class CorpusEntry:
    """One attack form drawn from a corpus, with the reference C18 reports."""

    corpus: str
    entry_id: str
    text: str

    @property
    def ref(self) -> str:
        """The stable reference written into the ledger, e.g. ``injecagent:dh:12``."""
        return f"{self.corpus}:{self.entry_id}"


def _normalise(text: str) -> str:
    """NFC, then collapse runs of whitespace, then strip.

    Declared here because :func:`classify_provenance` depends on it and a normalisation
    that is not written down is a threshold in disguise.
    """
    return " ".join(unicodedata.normalize("NFC", text).split())


def classify_provenance(
    emitted_text: str, seed: CorpusEntry | None
) -> tuple[InputProvenance, str | None]:
    """Decide whether this turn's input came from a corpus or was improvised.

    ⚠️ **THRESHOLD-FREE ON PURPOSE, AND THE BIAS DIRECTION IS STATED.** The rule is exact
    substring containment of the seed's normalised text in the attacker's normalised
    output. There is no similarity score and no cutoff, because a cutoff would be an
    author-chosen constant that decides a published number — and `CONTEXT.md` §8.6 fixes
    none, which by §8.6's own sentence would make inventing one a review BLOCKER.

    **The consequence, published rather than buried:** an attacker that *paraphrases* a
    corpus entry is recorded as ``IMPROVISED``. So the corpus fraction this yields is a
    **LOWER BOUND on corpus use and an UPPER BOUND on improvisation**, and C18 reports it
    as such. That direction is the honest one to be wrong in: it cannot inflate the
    "nobody has published this" number in our favour.
    """
    if seed is None:
        return (InputProvenance.IMPROVISED, None)
    needle = _normalise(seed.text)
    if needle and needle in _normalise(emitted_text):
        return (InputProvenance.CORPUS, seed.ref)
    return (InputProvenance.IMPROVISED, None)


# --------------------------------------------------------------------------------------
# Adapters. One per corpus, because the four ship four different shapes, and a single
# "clever" parser that guesses would be a silent failure the day a shape changes.
# --------------------------------------------------------------------------------------


def _adapter_injecagent(raw: bytes, corpus: str, key: str) -> list[CorpusEntry]:
    """JSONL; the attack form is the ``Attacker Instruction`` field."""
    entries = []
    for i, line in enumerate(raw.decode("utf-8").splitlines()):
        if not line.strip():
            continue
        row = json.loads(line)
        entries.append(CorpusEntry(corpus, f"{key}:{i}", row["Attacker Instruction"]))
    return entries


def _adapter_asb(raw: bytes, corpus: str, key: str) -> list[CorpusEntry]:
    """JSONL; ASB names the same field the same way InjecAgent does."""
    return _adapter_injecagent(raw, corpus, key)


def _adapter_agentdojo_injection_vectors(raw: bytes, corpus: str, key: str) -> list[CorpusEntry]:
    """AgentDojo's ``injection_vectors.yaml``: a mapping of vector name -> {description, default}.

    Parsed with the project's one YAML dependency. The ``default`` is the injected text.
    """
    import yaml

    doc = yaml.safe_load(raw.decode("utf-8")) or {}
    entries = []
    for name in sorted(doc):
        node = doc[name] or {}
        text = node.get("default") or node.get("description") or ""
        entries.append(CorpusEntry(corpus, f"{key}:{name}", text))
    return entries


def _adapter_agentharm(raw: bytes, corpus: str, key: str) -> list[CorpusEntry]:
    """AgentHarm: ``{"canary_guid": ..., "behaviors": [...]}``.

    ⚠️ The ``canary_guid`` is a contamination canary belonging to somebody else's
    benchmark. It is read past and never carried into a :class:`CorpusEntry`, so it can
    never reach a ledger, a report or this repository.
    """
    doc = json.loads(raw.decode("utf-8"))
    entries = []
    for row in doc["behaviors"]:
        entries.append(CorpusEntry(corpus, f"{key}:{row['id']}", row["prompt"]))
    return entries


ADAPTERS = {
    "injecagent_jsonl": _adapter_injecagent,
    "asb_jsonl": _adapter_asb,
    "agentdojo_injection_vectors_yaml": _adapter_agentdojo_injection_vectors,
    "agentharm_behaviors_json": _adapter_agentharm,
}


def load_sources(index_path: Path | None = None) -> tuple[CorpusSource, ...]:
    """Read ``corpora/seed_index.json`` — our selection record, committed."""
    path = index_path or (repo_root() / SEED_INDEX)
    if not path.is_file():
        raise CorpusUnavailable(
            f"{path} does not exist. It is this project's own record of WHICH corpus "
            f"entries seed the attacker, and it is committed. See corpora/MANIFEST.md."
        )
    doc = json.loads(path.read_bytes().decode("utf-8"))
    return tuple(
        CorpusSource(
            corpus=row["corpus"],
            origin_url=row["origin_url"],
            pin=row["pin"],
            path=row["path"],
            sha256=row["sha256"],
            adapter=row["adapter"],
            licence=row["licence"],
        )
        for row in doc["sources"]
    )


def load_entries(
    sources: tuple[CorpusSource, ...], fetched_root: Path | None = None
) -> tuple[CorpusEntry, ...]:
    """Load and hash-verify every pinned corpus file, then parse it.

    ⚠️ **The hash is checked before the parse, and a mismatch raises.** The pin is the
    whole integrity story once the payload is not committed (Q-010), so a corpus file
    whose bytes have drifted must stop the run rather than seed it.
    """
    root = fetched_root or (repo_root() / FETCHED_ROOT)
    entries: list[CorpusEntry] = []
    for source in sources:
        target = root / source.corpus / source.path
        if not target.is_file():
            raise CorpusUnavailable(
                f"{target} is not present. The corpora are PINNED, NOT COMMITTED "
                f"(QUESTIONS.md Q-010). Run the fetch commands in corpora/MANIFEST.md "
                f"section 2 before an episode. An absent corpus is never an empty corpus: "
                f"zero entries would make CONTEXT.md section 11.3's published split read "
                f"'100% improvised', which is a broken instrument reporting a headline."
            )
        raw = target.read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        if actual != source.sha256:
            raise CorpusUnavailable(
                f"{target} does not match its pinned hash.\n"
                f"  expected {source.sha256}\n  actual   {actual}\n"
                f"The pin is the integrity guarantee once the payload is not committed. "
                f"Re-fetch at the pin in corpora/MANIFEST.md, or stop."
            )
        adapter = ADAPTERS[source.adapter]
        key = Path(source.path).stem
        entries.extend(adapter(raw, source.corpus, key))
    if not entries:
        raise CorpusUnavailable(
            "every pinned corpus file parsed to zero entries. That is a parser failure, "
            "not an empty corpus, and it would publish a 100%-improvised split."
        )
    return tuple(entries)


def seed_for_turn(entries: tuple[CorpusEntry, ...], turn_index: int) -> CorpusEntry | None:
    """Pick the corpus entry offered to the attacker on a given turn.

    Deterministic rotation, not a random draw: hard rule 8 forbids randomness inside core
    logic, and hard rule 10's determinism claim covers everything this project can make
    deterministic. Given the same corpus and the same turn index, the same entry.
    """
    if not entries:
        return None
    return entries[turn_index % len(entries)]
