"""**PER-EPISODE CHECKPOINTS. Hard rule 10, and `evals/` is append-only.**

`CONTEXT.md` §13.5(2) and `PROTOCOL.md` §8:

    **Checkpoint per episode.** Each `(block, arm, seed_or_task, attacker_model)` writes its
    own JSON and is **skipped on re-run**, so a crash costs one episode rather than the run,
    and re-running the same command resumes — **across DAY boundaries**, which this sweep
    spans by design.

    **`evals/` is append-only.** No session deletes, rewrites or truncates a completed
    episode's output.

**This is a thin outer shell** (hard rule 8). It is one of only three modules in this package
that touch a filesystem, and it holds no predicate logic beyond *"does this file exist and
does it say what we are about to say"*.

--------------------------------------------------------------------------------------
⚠️ THE THREE PROPERTIES, AND HOW EACH IS OBTAINED RATHER THAN CLAIMED
--------------------------------------------------------------------------------------

**ATOMIC / PUBLISH-ON-COMPLETE.** The document is written to a sibling ``.partial`` file and
moved into place with :func:`os.replace`, which is atomic on both POSIX and Windows, so a
reader never observes a half-written checkpoint. ``.partial`` is in the committed `.gitignore`
(`Q-003`'s ruling names it by extension), so an in-flight write is invisible to `git status`
and a **published** one is not — which is the rider `Q-003` attached to C11's done-when.

**IDEMPOTENT.** :func:`publish` on an existing file with **identical bytes** is a no-op that
returns ``False``. Re-running the same command therefore re-runs zero completed episodes and
writes zero duplicates, and :func:`is_complete` is what the scheduler asks before dispatching.

**APPEND-ONLY.** :func:`publish` on an existing file with **different** bytes is a
:class:`CheckpointRefusal`, never an overwrite. ⚠️ **There is no delete, no truncate and no
force flag in this module**, and no argument that produces one: `CLAUDE.md` §4 makes deletion
operator-only, and a ``force=True`` parameter is how that rule would be got round by a session
in a hurry. ``tests/test_c11_runner.py`` asserts the absence by parsing this module's AST for
every removal call, so the claim is checked rather than promised.

--------------------------------------------------------------------------------------
⚠️ DETERMINISM, AT ITS EXACT SCOPE
--------------------------------------------------------------------------------------

**The checkpoint BYTES are deterministic given the same content**: canonical JSON, keys
sorted, LF newlines, no trailing whitespace, UTF-8. Two runs that produce the same episode
content produce byte-identical checkpoints, and that is testable and tested.

⚠️ **THE CONTENT IS NOT.** The attacker runs at `attacker.temperature` against a hosted
provider, so **re-running the models does not reproduce the run** — hard rule 10 says so in
capitals and this docstring is one of the places it would be easy to overclaim. What
regenerates byte-identically is every number, **from the stored ledgers**, which is a
different and true claim.

**LF, EXPLICITLY.** ``newline="\\n"``. The default on Windows translates ``\\n`` to ``\\r\\n``,
and `PROCESS.md` §6a records what that costs: the working tree and the git object store then
disagree, and a fingerprint recomputed on Linux stops matching the one this machine published.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .episodes import EpisodeKey
from .redaction import refuse_if_secret_bearing

#: Where checkpoints live, relative to the repository root. `CONTEXT.md` §16's tree.
CHECKPOINT_DIR = ("evals", "checkpoints")

#: The in-flight suffix. ⚠️ It is in the committed `.gitignore` (`evals/**/*.partial`), which
#: is `Q-003`'s ruling: *"Ignore only genuinely transient in-flight files."*
PARTIAL_SUFFIX = ".partial"

#: The keys a checkpoint document carries, in this order. Declared, so a reader knows the
#: shape without opening one and a missing field is a refusal rather than a ``None``.
DOCUMENT_KEYS: tuple[str, ...] = (
    "key",
    "block",
    "arm",
    "seed_or_task",
    "attacker_model",
    "lane",
    "utc_started",
    "utc_finished",
    "turns_run",
    "turn_budget",
    "tokens_spent",
    "calls_used",
    "truncated",
    "cause",
    "ledger_path",
)


class CheckpointRefusal(RuntimeError):
    """The write is refused. `evals/` is append-only and deletion is operator-only."""


@dataclass(frozen=True)
class CheckpointStore:
    """The checkpoint directory. **Holds a path and nothing else.**"""

    root: Path

    @classmethod
    def under(cls, repo_root: Path) -> "CheckpointStore":
        return cls(root=repo_root.joinpath(*CHECKPOINT_DIR))

    def path_for(self, key: EpisodeKey) -> Path:
        """Where ``key``'s checkpoint lives. **Injective** — see :attr:`EpisodeKey.slug`."""
        return self.root / f"{key.slug}.json"

    def is_complete(self, key: EpisodeKey) -> bool:
        """Has this episode already been published? **The resume check.**

        An in-flight ``.partial`` is deliberately **not** complete: it is a write that did not
        finish, and treating it as done is how a crash would silently remove an episode from
        the denominator.
        """
        return self.path_for(key).is_file()

    def completed(self) -> set[str]:
        """Every published checkpoint's slug. What a resume reads before dispatching."""
        if not self.root.is_dir():
            return set()
        return {p.stem for p in self.root.glob("*.json")}

    # -- the write path ----------------------------------------------------------------

    def publish(self, key: EpisodeKey, document: Mapping[str, Any]) -> bool:
        """Publish ``document`` for ``key``. Returns ``True`` if bytes were written.

        **Idempotent**: an existing file with identical bytes is left alone and ``False`` is
        returned. **Append-only**: an existing file with different bytes is a refusal.
        """
        refuse_if_secret_bearing(dict(document), where=f"checkpoint[{key.slug}]")
        missing = [name for name in DOCUMENT_KEYS if name not in document]
        if missing:
            raise CheckpointRefusal(
                f"{key.slug}: checkpoint is missing {missing}. Hard rule 9's shape applied to "
                f"an episode record: a missing required field is a refusal, never a None that "
                f"propagates into a published number"
            )
        unknown = [name for name in document if name not in DOCUMENT_KEYS]
        if unknown:
            raise CheckpointRefusal(
                f"{key.slug}: checkpoint carries undeclared field(s) {unknown}. The shape is "
                f"declared at DOCUMENT_KEYS so a reader knows it without opening a file; a "
                f"field nobody declared is a field no report prints"
            )

        text = render(document)
        path = self.path_for(key)
        if path.exists():
            if path.read_bytes() == text.encode("utf-8"):
                return False
            raise CheckpointRefusal(
                f"{path} already exists with DIFFERENT contents. `evals/` is append-only "
                f"(CLAUDE.md S4): a completed episode's output is never rewritten or "
                f"truncated, and deletion is operator-only. If this episode genuinely needs "
                f"to run again, that is the operator's call and it is made outside this code"
            )

        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + PARTIAL_SUFFIX)
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
        return True

    def read(self, key: EpisodeKey) -> dict[str, Any]:
        """Read a published checkpoint back."""
        path = self.path_for(key)
        with path.open("r", encoding="utf-8") as handle:
            document = json.load(handle)
        if not isinstance(document, dict):
            raise CheckpointRefusal(f"{path} did not parse to a mapping")
        return document


def render(document: Mapping[str, Any]) -> str:
    """The document as **canonical** JSON text: sorted keys, no whitespace padding, LF.

    Canonical because *"the checkpoint bytes are deterministic given the same content"* is a
    claim this project makes, and a claim about bytes needs a byte-level rule. ``sort_keys``
    is that rule; dictionary insertion order is not.
    """
    return json.dumps(dict(document), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def build_document(
    key: EpisodeKey,
    *,
    lane: str,
    utc_started: str,
    utc_finished: str,
    turns_run: int,
    turn_budget: int,
    tokens_spent: int,
    calls_used: int,
    cause: str | None,
    ledger_path: str | None,
) -> dict[str, Any]:
    """Assemble a checkpoint document. **Pure** — the timestamps arrive as arguments.

    ⚠️ Hard rule 8 forbids a clock inside core logic, and the two UTC strings are exactly the
    kind of thing that invites one. They are the **shell's** to read and this function's to
    record, so a test can drive a whole run at a fixed clock and get byte-identical output.

    ``truncated`` is **derived here from the turn counts**, never passed in: a flag a caller
    sets can disagree with the counts beside it, and rule 11's denominator is computed from
    that flag.
    """
    return {
        "key": key.slug,
        "block": key.block,
        "arm": key.arm,
        "seed_or_task": key.seed_or_task,
        "attacker_model": key.attacker_model,
        "lane": lane,
        "utc_started": utc_started,
        "utc_finished": utc_finished,
        "turns_run": turns_run,
        "turn_budget": turn_budget,
        "tokens_spent": tokens_spent,
        "calls_used": calls_used,
        "truncated": turns_run < turn_budget,
        "cause": cause,
        "ledger_path": ledger_path,
    }
