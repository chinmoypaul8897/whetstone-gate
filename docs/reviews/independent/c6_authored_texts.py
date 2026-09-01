"""C6 REVIEW 1 — the three `CONTEXT.md` §8.6 authored texts, verified BY MY OWN PARSE.

⚠️ **Why this needs its own parser rather than a re-run of C6's.** `INCIDENTS.md` **INC-13**
is a ``\\b`` that reached the specification as a real **0x08** byte and sat there for two
days, invisible. A single wrong character in ``data/policy.txt`` changes **what every arm
was shown** while every test still passes, because the test and the file would drift
together if the test merely re-read the file.

**MY METHOD DIFFERS FROM C6's ON THE ANCHOR, WHICH IS THE PART THAT CAN GO WRONG.**
C6 locates each fenced block by the prose sentence that introduces it and takes the *first*
fence after it. This file locates the block by the **file name in backticks** inside the
introducing line, and then requires that the fence it finds is the **nearest following**
one AND that no other fence lies between the marker and it. Two parsers that disagree about
which block they read is the failure mode worth catching; two that agree is evidence.

It also runs a **byte census** rather than a spot check: every code point in each file is
classified, and anything outside {printable ASCII, LF, an explicitly named non-ASCII
allow-set} is reported with its offset.

Run: ``python docs/reviews/independent/c6_authored_texts.py``
"""

from __future__ import annotations

import hashlib
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import whetstone_gate
from whetstone_gate import config as cfg

REPO = cfg.repo_root()

#: The three files, and the backticked name that identifies each block's introducing line.
TARGETS = {
    "data/policy.txt": "policy.txt",
    "data/arm3_safety.txt": "arm3_safety.txt",
    "data/attacker_sys.txt": "attacker_sys.txt",
}

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))


def context_lines() -> list[str]:
    return REPO.joinpath("CONTEXT.md").read_bytes().decode("utf-8").split("\n")


def block_for(lines: list[str], filename: str) -> str:
    """The fenced block introduced by the line that names ``filename`` in backticks.

    ⚠️ **A DIFFERENT ANCHOR FROM C6's, DELIBERATELY.** C6 matches a line *prefix*; this
    matches the backticked filename anywhere in a **bold** introducing line, then asserts
    the very next fence opens with nothing but prose between. If the two parsers ever
    disagree about which block belongs to which file, that disagreement is the finding.
    """
    marker = f"`{filename}`"
    intro = [i for i, line in enumerate(lines) if marker in line and line.startswith("**")]
    assert len(intro) == 1, f"{filename}: bold introducing line matched {len(intro)} times, want 1"
    start = intro[0]
    fences = [i for i, line in enumerate(lines) if line.strip() == "```" and i > start]
    assert len(fences) >= 2, f"{filename}: fewer than two fences follow its introducing line"
    open_f, close_f = fences[0], fences[1]
    # Nothing between the marker and the fence may itself be a fence.
    assert not any(lines[j].strip() == "```" for j in range(start + 1, open_f)), (
        f"{filename}: a fence lies between the introducing line and the block"
    )
    return "\n".join(lines[open_f + 1 : close_f]) + "\n"


def byte_census(rel: str, text: str) -> tuple[bool, str]:
    """Every code point classified. Anything unexpected is reported WITH ITS OFFSET."""
    allowed_non_ascii = {"₹", "–", "—"}  # rupee sign, en dash, em dash
    bad: list[str] = []
    non_ascii = Counter()
    for i, ch in enumerate(text):
        o = ord(ch)
        if ch == "\n":
            continue
        if 0x20 <= o <= 0x7E:
            continue
        if ch in allowed_non_ascii:
            non_ascii[ch] += 1
            continue
        bad.append(f"offset {i}: U+{o:04X} ({unicodedata.name(ch, 'unnamed')})")
    names = ", ".join(
        f"U+{ord(c):04X} {unicodedata.name(c)} x{n}" for c, n in sorted(non_ascii.items())
    )
    return (not bad, f"CR={text.count(chr(13))} non-ASCII: {names or 'none'}"
            + (f" ⚠️ UNEXPECTED: {bad}" if bad else ""))


def main() -> int:
    print(f"whetstone_gate.__file__ = {whetstone_gate.__file__}")
    lines = context_lines()
    print()

    for rel, filename in TARGETS.items():
        path = REPO / rel
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        spec_block = block_for(lines, filename)

        identical = text == spec_block
        check(f"{rel}: character-identical to CONTEXT.md §8.6 (my own anchor)", identical,
              f"sha256 {hashlib.sha256(raw).hexdigest()[:16]}"
              if identical
              else f"DIFFERS: file {len(text)} chars, spec block {len(spec_block)} chars")
        if not identical:
            for i, (a, b) in enumerate(zip(text, spec_block)):
                if a != b:
                    print(f"    first difference at offset {i}: file {a!r} vs spec {b!r}")
                    break

        ok, detail = byte_census(rel, text)
        check(f"{rel}: byte census clean (no control bytes, no stray non-ASCII)", ok, detail)

        # ⚠️ INC-13's exact shape: a backslash escape that reached disk as a control byte.
        check(f"{rel}: no 0x08 / 0x0C / 0x1B / 0x00 byte (INC-13's class)",
              not any(b in raw for b in (b"\x08", b"\x0c", b"\x1b", b"\x00")), "")
        # LF only, never CRLF.
        check(f"{rel}: LF line endings only", b"\r" not in raw, "")

    # The policy is SEVEN clauses, so "P7" has a referent (§8.6's own words).
    clauses = [ln for ln in (REPO / "data/policy.txt").read_text(encoding="utf-8").split("\n") if ln.strip()]
    check("policy.txt carries exactly seven clauses P1..P7",
          len(clauses) == 7 and [c.split()[0] for c in clauses] == [f"P{i}" for i in range(1, 8)],
          f"{len(clauses)} clauses: {[c.split()[0] for c in clauses]}")

    # ⚠️ P7 must match the probe note's discriminator, or the door does not open.
    note = cfg.load("protocol").require("probe.notes.reconciliation")
    p7 = clauses[6]
    tag = re.search(r'"([^"]+)"', p7)
    check("P7's quoted tag is a substring of the probe note (the door actually opens)",
          bool(tag) and tag.group(1) in note,
          f"P7 tag {tag.group(1)!r} vs note {note!r}" if tag else "P7 carries no quoted tag")

    # C6 built no gate: policy.txt and arm3_safety.txt are C9's TO USE.
    gates_dir = REPO / "src/whetstone_gate/gates"
    check("C6 built no gate (src/whetstone_gate/gates/ does not exist)", not gates_dir.exists(),
          str(gates_dir))

    print()
    failures = 0
    for name, ok, detail in RESULTS:
        mark = "OK  " if ok else "FAIL"
        print(f"[{mark}] {name}" + (f"   -- {detail}" if detail else ""))
        failures += int(not ok)
    print()
    print(f"{len(RESULTS) - failures}/{len(RESULTS)} properties hold; {failures} did not")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
