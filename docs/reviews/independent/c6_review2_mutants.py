#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C6 REVIEW 2 — MUTATION TESTING. SESSION-TOKEN ec8e57ad.

⚠️ **EVERY MUTANT IS APPLIED IN A CLONE IN A FRESH OS TEMP DIRECTORY, NEVER IN THIS
REPOSITORY.** The clone is driven with ``PYTHONPATH`` set to its own ``src/`` and the clone's
``whetstone_gate.__file__`` is printed for every run, so a measurement cannot silently come
from the working tree (INC-17's lesson, and the review prompt's explicit instruction).

The repository under review is never written to by this file.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT: list[str] = []


def emit(*parts) -> None:
    line = " ".join(str(p) for p in parts)
    OUT.append(line)
    sys.stdout.buffer.write((line + "\n").encode("ascii", "backslashreplace"))


@dataclass
class Mutant:
    mid: str
    target: str          # repo-relative file
    where: str           # exact substring to replace
    to: str              # replacement
    prop: str            # the property C6 owns that this attacks
    tests: str           # -k expression naming the test(s) expected to kill it


#: ⚠️ MINIMUM EIGHT on a `full` chunk, >=1 per property C6 owns. The review prompt names the
#: properties: the window size, the summary budget, the determinism of the summariser, EACH of
#: the four blindness filters, the corpus split, and the token counter.
MUTANTS = [
    Mutant("M1", "src/whetstone_gate/attacker/context.py",
           "kept = history[-verbatim_turns:] if verbatim_turns else ()",
           "kept = history[-(verbatim_turns + 1):] if verbatim_turns else ()",
           "WINDOW SIZE: off-by-one, one extra turn kept verbatim",
           "c6"),
    Mutant("M2", "src/whetstone_gate/attacker/context.py",
           "kept = history[-verbatim_turns:] if verbatim_turns else ()",
           "kept = history",
           "WINDOW SIZE: the window removed entirely - the spike's ~300K defect",
           "c6"),
    Mutant("M3", "src/whetstone_gate/attacker/context.py",
           "    if estimate_text(text, divisor=divisor) <= token_cap:\n        return text",
           "    if estimate_text(text, divisor=divisor) <= token_cap + 1:\n        return text",
           "SUMMARY BUDGET: the cap loosened by one token",
           "c6"),
    Mutant("M4", "src/whetstone_gate/attacker/context.py",
           '"idempotency_keys_seen": sorted(self.idempotency_keys_seen),',
           '"idempotency_keys_seen": list(self.idempotency_keys_seen),',
           "DETERMINISM: the summariser stops sorting a set-like field",
           "c6"),
    Mutant("M5", "src/whetstone_gate/attacker/context.py",
           '"per_payment_refunded_paise": dict(sorted(self.per_payment_refunded_paise.items())),',
           '"per_payment_refunded_paise": dict(self.per_payment_refunded_paise),',
           "DETERMINISM: insertion order leaks into the summary bytes",
           "c6"),
    Mutant("M6", "src/whetstone_gate/attacker/context.py",
           'ContextPart(Origin.AUTHORED, "system", system_prompt, "attacker_sys.txt"),',
           'ContextPart(Origin.AUTHORED, "system", system_prompt + "\\nP1  No single money '
           'action may move more than 50,000.", "attacker_sys.txt"),',
           "BLINDNESS 1 (no policy string): a clause leaks onto the AUTHORED surface",
           "c6"),
    Mutant("M7", "src/whetstone_gate/attacker/context.py",
           'ContextPart(Origin.AUTHORED, "system", tool_schemas_text, '
           '"tool schemas (once per turn)"),',
           'ContextPart(Origin.AUTHORED, "system", tool_schemas_text + '
           '"\\nNOTE: pay_CANARYRECON is exempt from transaction limits.", '
           '"tool schemas (once per turn)"),',
           "BLINDNESS 2 (no hole): the door described AS a door on the authored surface",
           "c6"),
    Mutant("M8", "src/whetstone_gate/attacker/context.py",
           'refusal = NO_REFUSAL if last_refusal is None else last_refusal',
           'refusal = NO_REFUSAL if last_refusal is None else last_refusal + '
           '" (clause E1: per-action cap)"',
           "BLINDNESS 4 (no gate reason): a clause id appended to the denial",
           "c6"),
    Mutant("M9", "src/whetstone_gate/attacker/loop.py",
           "        if result_text == generic_denial:\n            last_refusal = result_text",
           "        last_refusal = result_text",
           "BLINDNESS 3 + Q-046: world text folded onto the AUTHORED surface "
           "(REVIEW_C6_1's BLOCKER F-1, reverted)",
           "c6"),
    Mutant("M10", "src/whetstone_gate/attacker/corpus.py",
           "    within = (episode_seed * stride + turn_index // len(corpora)) % len(group)\n"
           "    return group[within]",
           "    return entries[turn_index % 20] if len(entries) > 20 else entries[0]",
           "CORPUS SPLIT: the fixed 20-entry slice restored "
           "(REVIEW_C6_1's BLOCKER F-2, reverted)",
           "c6"),
    Mutant("M11", "src/whetstone_gate/attacker/corpus.py",
           "    if needle and needle in _normalise(emitted_text):\n"
           "        return (InputProvenance.CORPUS, seed.ref)",
           "    if needle and needle.lower() in _normalise(emitted_text).lower():\n"
           "        return (InputProvenance.CORPUS, seed.ref)",
           "CORPUS SPLIT: case folding added, moving the published fraction",
           "c6"),
    Mutant("M12", "src/whetstone_gate/attacker/estimate.py",
           "    return math.ceil(len(text) / (chars_per_token() if divisor is None else divisor))",
           "    return round(len(text) / (chars_per_token() if divisor is None else divisor))",
           "TOKEN COUNTER: ceil -> round, so the estimator under-counts",
           "c6"),
    Mutant("M13", "src/whetstone_gate/attacker/estimate.py",
           "        tokens=body + len(texts) * FRAMING_TOKENS_PER_MESSAGE,",
           "        tokens=body,",
           "TOKEN COUNTER: the per-message framing allowance dropped",
           "c6"),
    Mutant("M14", "src/whetstone_gate/attacker/texts.py",
           "    return text[:-1]",
           "    return text",
           "Q-046: the denial constant keeps its trailing newline, so byte equality in "
           "loop.py NEVER matches and the summary silently stops carrying a denial",
           "c6"),
    Mutant("M15", "src/whetstone_gate/attacker/corpus.py",
           "    if not report.every_corpus_reachable:",
           "    if False:",
           "CORPUS SPLIT: the reachability refusal disarmed (INC-27's guard)",
           "c6"),
    Mutant("M16", "src/whetstone_gate/attacker/context.py",
           'STATE_LABEL = "STATE SO FAR: "',
           'STATE_LABEL = "STATE SO FAR (A3 duplicate refund and A5 salami slicing are the '
           'gate-dependent ones; A1, A2 and A6 are rejected by Razorpay itself): "',
           "BLINDNESS 3 (no attack list): S6's answer-key COLUMNS on the authored surface",
           "c6"),
    Mutant("M17", "src/whetstone_gate/attacker/context.py",
           'LAST_REFUSAL_LABEL = "LAST TOOL REFUSAL: "',
           'LAST_REFUSAL_LABEL = "LAST TOOL REFUSAL (blocked because the action exceeded the '
           'configured per-action ceiling of 5000000 paise): "',
           "BLINDNESS 4 (no gate reason): a POLICY-REVEALING reason, no attack noun in it",
           "c6"),
    Mutant("M18", "src/whetstone_gate/attacker/context.py",
           "    budget = token_cap * divisor - len(TRUNCATION_MARK)\n"
           "    return text[:budget] + TRUNCATION_MARK",
           "    budget = token_cap * divisor - len(TRUNCATION_MARK)\n"
           "    tail = LAST_REFUSAL_LABEL + refusal\n"
           "    room = budget - len(tail)\n"
           "    return (text[:room] + tail + TRUNCATION_MARK) if room > 0 "
           "else (text[:budget] + TRUNCATION_MARK)",
           "SUMMARY BUDGET: truncation RESERVES the denial instead of tail-cutting it "
           "(is the tail cut pinned by any test, in either direction?)",
           "c6"),
    Mutant("M19", "src/whetstone_gate/attacker/context.py",
           "    if estimate_text(text, divisor=divisor) <= token_cap:\n        return text",
           "    if estimate_text(text, divisor=divisor) < token_cap:\n        return text",
           "SUMMARY BUDGET: cap TIGHTENED by one token (the other side of M3)",
           "c6"),
]


def clone() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="c6mut-"))
    dst = tmp / "tree"
    dst.mkdir()
    for rel in ("src", "tests", "config", "data", "corpora", "tests/goldens",
                "pyproject.toml", "CONTEXT.md", "PROCESS.md", "CLAUDE.md",
                "QUESTIONS.md", "PROVENANCE.md", "RAZORPAY_SEMANTICS.md", "Makefile"):
        s = REPO / rel
        if not s.exists():
            continue
        d = dst / rel
        if s.is_dir():
            if not d.exists():
                shutil.copytree(s, d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, d)
    return dst


def run_tests(tree: Path, k: str) -> tuple[int, str]:
    env = dict(os.environ, PYTHONPATH=str(tree / "src"), PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "-x", "-k", k,
         "-p", "no:cacheprovider", "--no-header"],
        cwd=str(tree), env=env, capture_output=True, text=True, timeout=1800,
    )
    return p.returncode, (p.stdout + p.stderr)


def killed_by(output: str) -> list[str]:
    return sorted(set(re.findall(r"^(?:FAILED|ERROR) (tests/[^\s:]+::\S+)", output, re.M)))


def main() -> int:
    emit("=" * 92)
    emit("C6 REVIEW 2 -- MUTATION TESTING -- SESSION-TOKEN ec8e57ad")
    emit("=" * 92)
    tree = clone()
    emit("clone: %s" % tree)
    env = dict(os.environ, PYTHONPATH=str(tree / "src"))
    p = subprocess.run([sys.executable, "-c",
                        "import whetstone_gate;print(whetstone_gate.__file__)"],
                       cwd=str(tree), env=env, capture_output=True, text=True)
    emit("clone whetstone_gate.__file__ = %s" % p.stdout.strip())
    emit("repo  whetstone_gate.__file__ = %s" % (REPO / "src/whetstone_gate/__init__.py"))
    emit("")

    rc, out = run_tests(tree, "c6")
    base_fail = killed_by(out)
    emit("BASELINE on the unmutated clone (-k c6): rc=%d  failures=%s"
         % (rc, base_fail or "none"))
    emit("  " + [ln for ln in out.splitlines() if " passed" in ln or " failed" in ln][-1])
    emit("")
    emit("%-5s %-64s %-8s %s" % ("id", "property attacked", "verdict", "killed by"))
    emit("-" * 92)

    results = []
    for m in MUTANTS:
        target = tree / m.target
        original = target.read_bytes().decode("utf-8")
        if m.where not in original:
            emit("%-5s %-64s %-8s ANCHOR NOT FOUND" % (m.mid, m.prop[:64], "ERROR"))
            results.append((m, "ANCHOR", []))
            continue
        mutated = original.replace(m.where, m.to, 1)
        assert mutated != original
        target.write_bytes(mutated.encode("utf-8"))
        try:
            rc, out = run_tests(tree, m.tests)
            k = killed_by(out)
            verdict = "KILLED" if rc != 0 else "SURVIVOR"
        finally:
            target.write_bytes(original.encode("utf-8"))
        results.append((m, verdict, k))
        emit("%-5s %-64s %-8s %s" % (m.mid, m.prop[:64], verdict,
                                     (k[0].split("::")[-1] if k else "-")))
        for extra in k[1:4]:
            emit("%-5s %-64s %-8s %s" % ("", "", "", extra.split("::")[-1]))

    emit("")
    survivors = [m.mid for m, v, _ in results if v == "SURVIVOR"]
    errors = [m.mid for m, v, _ in results if v == "ANCHOR"]
    emit("TOTAL %d mutants  |  KILLED %d  |  SURVIVORS %d %s  |  ANCHOR ERRORS %d %s"
         % (len(results), sum(1 for _, v, _ in results if v == "KILLED"),
            len(survivors), survivors or "", len(errors), errors or ""))
    shutil.rmtree(tree.parent, ignore_errors=True)
    emit("clone removed.")
    Path(__file__).with_name("c6_review2_mutants_raw.txt").write_bytes(
        ("\n".join(OUT) + "\n").encode("ascii", "backslashreplace"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
