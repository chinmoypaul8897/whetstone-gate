"""The vendored CaMeL and AgentDojo checkouts, and the empty diff that is C13's deliverable.

⚠️ **THE EMPTY DIFF IS THE DELIVERABLE, AND A COMMITTED DIFF THAT NOTHING RE-DERIVES IS A
SCREENSHOT.** `PROCESS.md` §12.1's C13 done-when: *"No CaMeL source file is modified — a
diff against the vendored SHA is empty and is committed as proof."* So the proof file next
door is **regenerated** by :func:`render_unmodified_proof` and diffed byte for byte by
``tests/test_c13_camel_comparator.py``. A tree edited after the proof was written makes the
test fail; a proof edited after the tree makes it fail the other way.

WHY GIT IS SHELLED OUT TO HERE AND NOWHERE ELSE
================================================
Hard rule 8: core logic takes data in and returns results; side effects live in a thin
outer shell. Everything below :data:`_SHELL_BOUNDARY` runs a subprocess or touches the
filesystem; everything above it is a pure function over bytes and is the part the tests
exercise directly.

⚠️ **THE DIGESTS AND SIZES COME FROM THE GIT OBJECT, NEVER THE WORKING TREE, AND THAT IS
NOT FUSSINESS.** ``core.autocrlf`` is ``true`` system-wide on the operator's machine, and
CaMeL ships no ``.gitattributes``, so ``interpreter.py`` checks out with one CR per line.
Measured here, at the pin: the **git blob** is **100,476** bytes over **2,716** lines and
the **working tree** is **103,192** bytes — and ``100,476 + 2,716 == 103,192`` exactly. A
reviewer who runs ``stat`` on Windows gets a number `CONTEXT.md` §8.5 does not state, is
right to be suspicious, and is looking at line endings rather than a modified file. That
arithmetic is *reported*, not hidden, by :func:`interpreter_measurement`.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .. import config as cfg

CAMEL_DIRNAME = "camel-prompt-injection"
"""``vendor/`` subdirectory holding the CaMeL checkout."""

AGENTDOJO_DIRNAME = "agentdojo"
"""``vendor/`` subdirectory holding the AgentDojo checkout.

⚠️ **Its SHA is NOT pinned in `config/` by this chunk.** ``vendor.agentdojo_sha`` is
**C16's** sentinel and resolving another chunk's sentinel is exactly the silent scope creep
the fences exist to stop. See `QUESTIONS.md` **Q-059** for the pin C13 measured and the
reason it is recorded in `vendor/MANIFEST.md` rather than in `config/`.
"""

INTERPRETER_PATH = "src/camel/interpreter/interpreter.py"
SECURITY_POLICY_PATH = "src/camel/security_policy.py"
MODELS_PATH = "src/camel/models.py"
BANKING_POLICY_PATH = "src/camel/pipeline_elements/security_policies/banking.py"

PROOF_FILENAME = "camel_unmodified.txt"
"""The committed empty-diff proof, beside this module.

`vendor/MANIFEST.md` §3 names this file ``docs/evidence/camel_unmodified.txt``; this
chunk's scope fence names only ``src/whetstone_gate/camel_comparator/``. The divergence is
recorded in `QUESTIONS.md` **Q-060** rather than resolved by crossing a fence.
"""


class VendorError(RuntimeError):
    """The vendored tree is absent, at the wrong commit, or modified.

    ⚠️ Always a refusal, never a warning. Every claim this package reports is a property of
    a tree at a named SHA; reporting one from a tree nobody pinned would be a measurement
    of nothing.
    """


# ======================================================================================
# THE PURE CORE. Nothing below takes a path; everything takes bytes or text.
# ======================================================================================


def is_hex_commit(text: str) -> bool:
    """True for a full-length lowercase hex object id."""
    return len(text) == 40 and all(char in "0123456789abcdef" for char in text)


def parse_head_file(head_text: str, resolve_ref: object = None) -> str:
    """Return the commit id a ``.git/HEAD`` body names, or raise.

    A detached checkout writes the commit id directly. A symbolic HEAD is *not* resolved
    here — that needs a second file, so it is the shell's job — and is reported as such.
    """
    head = head_text.strip()
    if head.startswith("ref: "):
        raise VendorError(
            f"HEAD is symbolic ({head!r}); the manifest's fetch commands produce a "
            f"DETACHED checkout so that the commit cannot move under the pin."
        )
    if not is_hex_commit(head):
        raise VendorError(f".git/HEAD does not hold a commit id (got {head!r}).")
    return head


@dataclass(frozen=True)
class Measurement:
    """A file's size, measured both canonically and as this machine sees it."""

    path: str
    blob_bytes: int
    """Bytes of the **git blob** — the canonical, OS-independent figure."""

    lines: int
    """Newline count of the blob."""

    worktree_bytes: int
    """Bytes on disk. Larger by one per line wherever ``core.autocrlf`` expanded LF."""

    cr_bytes: int
    """CR bytes on disk. Zero on a POSIX checkout."""

    @property
    def crlf_accounts_for_the_difference(self) -> bool:
        """⚠️ The whole point of carrying four numbers instead of one.

        If this is true, a working-tree size that disagrees with `CONTEXT.md` §8.5 is a
        line-ending artefact and **not** a modified file. If it is false, the difference is
        something else and wants explaining.
        """
        return self.blob_bytes + self.cr_bytes == self.worktree_bytes


@dataclass(frozen=True)
class UnmodifiedProof:
    """The verification triple `vendor/MANIFEST.md` §3 specifies, as data."""

    package: str
    pinned_sha: str
    head_sha: str
    status_porcelain: str
    diff_against_pin: str
    tracked_files: int
    tracked_blob_bytes: int

    @property
    def head_matches_pin(self) -> bool:
        return self.head_sha == self.pinned_sha

    @property
    def is_clean(self) -> bool:
        return self.status_porcelain == ""

    @property
    def diff_is_empty(self) -> bool:
        return self.diff_against_pin == ""

    @property
    def holds(self) -> bool:
        """All three legs of the triple. **This is C13's done-when, as a boolean.**"""
        return self.head_matches_pin and self.is_clean and self.diff_is_empty

    def failures(self) -> list[str]:
        """Every leg that did not hold, named. Empty when :attr:`holds`."""
        problems: list[str] = []
        if not self.head_matches_pin:
            problems.append(
                f"HEAD is {self.head_sha}, but config/protocol.yaml pins {self.pinned_sha}"
            )
        if not self.is_clean:
            problems.append(
                f"`git status --porcelain` is NOT empty:\n{self.status_porcelain}"
            )
        if not self.diff_is_empty:
            problems.append(
                f"`git diff {self.pinned_sha}` is NOT empty. The comparator is no longer a "
                f"comparison against CaMeL:\n{self.diff_against_pin}"
            )
        return problems


def render_unmodified_proof(
    proof: UnmodifiedProof, measurement: Measurement, fetched: str
) -> str:
    """Render the committed proof file. **Deterministic: same inputs, same bytes.**

    ⚠️ Every line ends ``\\n``. The file is compared byte for byte by the test that
    regenerates it, and a CRLF here would make that comparison a line-ending check.
    """
    lines = [
        "# CaMeL, UNMODIFIED - the empty-diff proof that IS C13's deliverable.",
        "#",
        "# PROCESS.md S12.1, C13 done-when:",
        '#   "No CaMeL source file is modified - a diff against the vendored SHA is empty',
        '#    and is committed as proof."',
        "#",
        "# CONTEXT.md S8.5's whole resolution is 'run CaMeL UNMODIFIED, on its home turf'.",
        "# A modified CaMeL would not be a comparison against CaMeL, so this file is the",
        "# evidence that the comparator is a comparison.",
        "#",
        "# THIS FILE IS REGENERATED, NOT STORED. tests/test_c13_camel_comparator.py re-runs",
        "# the three commands below against the live checkout and diffs the result against",
        "# these bytes. A committed diff that nothing re-derives is a screenshot.",
        "#",
        f"# Package : {proof.package}",
        f"# Pin     : {proof.pinned_sha}",
        f"# Fetched : {fetched}",
        "",
        "$ cd vendor/" + proof.package,
        "",
        "$ git rev-parse HEAD",
        proof.head_sha,
        "",
        # ⚠️ OF-71: `(empty)` is printed ONLY when the value is empty. It used to be
        # printed UNCONDITIONALLY, after the value, so a dirty tree rendered its own diff
        # and then the word "(empty)" underneath it — and mutant M1b, which deletes the
        # value and leaves the literal, SURVIVED the whole suite. A proof that can print
        # "(empty)" over a non-empty diff is the screenshot this file exists to not be.
        # Byte-identical for a clean tree, which is why the committed proof still
        # regenerates; it is the DIRTY rendering that was wrong.
        "$ git status --porcelain",
        proof.status_porcelain or "(empty)",
        "",
        f"$ git diff {proof.pinned_sha}",
        proof.diff_against_pin or "(empty)",
        "",
        "# ------------------------------------------------------------------------------",
        "# THE MEASUREMENT, AND WHY IT CARRIES FOUR NUMBERS INSTEAD OF ONE.",
        "#",
        "# CONTEXT.md S8.5 states the interpreter at 100,476 bytes and 2,716 lines. Both",
        "# reproduce - FROM THE GIT BLOB. core.autocrlf is true on the operator's machine",
        "# and CaMeL ships no .gitattributes, so the working tree carries one CR per line.",
        "# A reviewer running `stat` on Windows sees a number the spec does not state and",
        "# is right to be suspicious; the arithmetic below is what resolves it.",
        "#",
        f"#   file            : {measurement.path}",
        f"#   git blob bytes  : {measurement.blob_bytes}   <- CONTEXT.md S8.5's figure",
        f"#   lines           : {measurement.lines}   <- CONTEXT.md S8.5's figure",
        f"#   worktree bytes  : {measurement.worktree_bytes}",
        f"#   CR bytes        : {measurement.cr_bytes}",
        f"#   blob + CR == worktree : {measurement.crlf_accounts_for_the_difference}",
        "#",
        f"#   tracked files       : {proof.tracked_files}",
        f"#   tracked blob bytes  : {proof.tracked_blob_bytes}",
        "# ------------------------------------------------------------------------------",
        "# END",
    ]
    return "\n".join(lines) + "\n"


# ======================================================================================
# THE SHELL. Filesystem and subprocess live below this line and nowhere else.
# ======================================================================================

_SHELL_BOUNDARY = True


def _vendor_dir(dirname: str) -> Path:
    root = cfg.repo_root() / "vendor" / dirname
    if not root.is_dir():
        raise VendorError(
            f"{root} does not exist. The vendored checkouts are pinned, not committed "
            f"(QUESTIONS.md Q-010); vendor/MANIFEST.md carries the exact shallow-fetch "
            f"commands. C13 cannot be built or reviewed without it, and a SKIP here would "
            f"report green over a proof that was never checked."
        )
    return root


def vendor_root() -> Path:
    """``vendor/camel-prompt-injection``, or refuse."""
    return _vendor_dir(CAMEL_DIRNAME)


def agentdojo_root() -> Path:
    """``vendor/agentdojo``, or refuse.

    CaMeL's banking policies are typed on ``BankingEnvironment``
    (``banking.py:17``), so the comparator cannot be read - let alone run - without it.
    """
    return _vendor_dir(AGENTDOJO_DIRNAME)


def _git(root: Path, *args: str) -> str:
    """Run git in ``root`` and return stdout, or refuse. **The only subprocess here.**"""
    try:
        done = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, check=False
        )
    except OSError as exc:  # pragma: no cover - git is a hard prerequisite
        raise VendorError(f"could not run git in {root}: {exc}") from exc
    if done.returncode != 0:
        raise VendorError(
            f"`git {' '.join(args)}` failed in {root} (exit {done.returncode}): "
            f"{done.stderr.strip()}"
        )
    return done.stdout


def head_sha(root: Path) -> str:
    """The commit a checkout is on, read from its own ``.git/HEAD``.

    Deliberately **not** a subprocess: the manifest's commands produce a detached
    checkout, which writes the commit id into ``.git/HEAD`` directly, so this stays a
    file read. Any other shape is a refusal rather than a guess.
    """
    head_file = root / ".git" / "HEAD"
    if not head_file.is_file():
        raise VendorError(f"{head_file} does not exist, so the checkout cannot be pinned.")
    return parse_head_file(head_file.read_text(encoding="utf-8"))


def pinned_sha() -> str:
    """The CaMeL commit `PROTOCOL.md` pre-registers, read from ``config/``.

    Hard rule 9: it is a spec value, so it is read, never written into source.
    """
    return cfg.load("protocol").require("vendor.camel_sha")


def assert_vendor_at_pin() -> str:
    """Refuse unless the CaMeL checkout is at the pinned commit. Returns that commit."""
    head, pin = head_sha(vendor_root()), pinned_sha()
    if head != pin:
        raise VendorError(
            f"vendor/{CAMEL_DIRNAME} is at {head}, but config/protocol.yaml pins {pin}. "
            f"Every claim derived from this tree would be about a different CaMeL than the "
            f"one PROTOCOL.md pre-registers. This is a refusal, not a warning."
        )
    return head


def blob_text(root: Path, path: str) -> str:
    """Return a tracked file's **git blob** as text, never the working tree.

    ⚠️ This is the function that keeps every line number in this package OS-independent.
    ``git show HEAD:<path>`` returns the object bytes; ``open(path)`` returns whatever
    ``core.autocrlf`` produced on checkout.
    """
    return _git(root, "show", f"HEAD:{path}")


def blob_size(root: Path, path: str) -> int:
    """Byte length of a tracked file's git blob."""
    oid = _git(root, "rev-parse", f"HEAD:{path}").strip()
    return int(_git(root, "cat-file", "-s", oid).strip())


def interpreter_measurement(root: Path | None = None) -> Measurement:
    """Measure ``interpreter.py`` four ways. See :class:`Measurement`."""
    root = root if root is not None else vendor_root()
    on_disk = (root / INTERPRETER_PATH).read_bytes()
    blob = blob_text(root, INTERPRETER_PATH).encode("utf-8")
    return Measurement(
        path=INTERPRETER_PATH,
        blob_bytes=blob_size(root, INTERPRETER_PATH),
        lines=blob.count(b"\n"),
        worktree_bytes=len(on_disk),
        cr_bytes=on_disk.count(b"\r"),
    )


def tracked_totals(root: Path) -> tuple[int, int]:
    """``(tracked file count, total tracked blob bytes)`` — from git objects.

    `QUESTIONS.md` **Q-010**'s ruling turned on exactly this measurement for τ²-bench, and
    `PROCESS.md` §12.1's C19 clean-clone test must include the fetch step or `CONTEXT.md`
    §20's first box is false. So it is measured rather than asserted.
    """
    listing = _git(root, "ls-tree", "-r", "-l", "HEAD").splitlines()
    total = 0
    for line in listing:
        parts = line.split(None, 4)
        if len(parts) >= 4 and parts[3].isdigit():
            total += int(parts[3])
    return len(listing), total


def unmodified_proof(dirname: str = CAMEL_DIRNAME, pin: str | None = None) -> UnmodifiedProof:
    """Run `vendor/MANIFEST.md` §3's verification triple and return it as data."""
    root = _vendor_dir(dirname)
    resolved_pin = pin if pin is not None else pinned_sha()
    files, total_bytes = tracked_totals(root)
    return UnmodifiedProof(
        package=dirname,
        pinned_sha=resolved_pin,
        head_sha=head_sha(root),
        status_porcelain=_git(root, "status", "--porcelain").strip(),
        diff_against_pin=_git(root, "diff", resolved_pin).strip(),
        tracked_files=files,
        tracked_blob_bytes=total_bytes,
    )


def proof_path() -> Path:
    """The committed proof file, beside this module."""
    return Path(__file__).resolve().parent / PROOF_FILENAME


def fetched_from_proof(proof_text: str) -> str:
    """The vendoring date recorded in a committed proof file.

    ⚠️ **The one field the regeneration test takes FROM the file rather than recomputing.**
    A checkout's fetch date is not derivable from the checkout — a shallow fetch of the same
    SHA tomorrow produces the same tree — so it is data. Everything else in the proof is
    recomputed and must match byte for byte, which is what stops this one exception from
    becoming a hole: a stale date cannot hide a modified tree, because the tree is measured.
    """
    match = re.search(r"^# Fetched : (\S+)$", proof_text, re.MULTILINE)
    if match is None:
        raise VendorError(
            f"{PROOF_FILENAME} carries no `# Fetched :` line, so the proof cannot be "
            f"regenerated for comparison. PROCESS.md S9: every third-party claim carries a "
            f"URL and a date, and this file IS a third-party claim."
        )
    return match.group(1)
