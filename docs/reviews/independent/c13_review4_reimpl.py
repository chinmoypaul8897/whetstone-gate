"""C13 REVIEW 4 - the SCOPED reimplementation, written in PHASE 1 and sealed with the criteria.

OF-80's second ruling: on a re-review the reimplementation is OF THE CHANGED SURFACE, independently
derived.  The changed surface here is

    (a) the four BRANCH_B_REQUIREMENTS phrases, and
    (b) the sentinel refusal path.

So this file re-derives, from `CONTEXT.md` S8.5.1 and `config/lanes.yaml` ALONE:

  * what the four requirements ARE (parsed out of the law at run time, never transcribed);
  * a predicate that says which of them a candidate `branch_b_condition` fails;
  * the sentinel refusal path, implemented TWICE - a `require`-shaped read that RAISES on a
    TODO_ sentinel, and a `get`-shaped read that hands the sentinel back AS A VALUE.  That pair is
    the exhibit REVIEW 3's mutant N-I2 rested on, and it is reproduced here without the project's
    loader so Phase 2 can check the project against it rather than against its own description.

IT IMPORTS NOTHING FROM `src/`.  It asserts that at run time.  It parses `config/lanes.yaml` with
its own minimal reader because the project's loader lives in `src/`.

Stdlib only.  ASCII only.  Run:  python docs/reviews/independent/c13_review4_reimpl.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------------------------
# 0.  THE FENCE, ASSERTED RATHER THAN PROMISED
# ---------------------------------------------------------------------------------------------

_LEAKED = sorted(m for m in sys.modules if m == "whetstone_gate" or m.startswith("whetstone_gate."))
assert not _LEAKED, "this file must import nothing from src/: leaked %r" % (_LEAKED,)

REPO = Path(__file__).resolve().parents[3]
CONTEXT = REPO / "CONTEXT.md"
LANES = REPO / "config" / "lanes.yaml"


# ---------------------------------------------------------------------------------------------
# 1.  A MINIMAL YAML READER - enough for one flat block, and no more
# ---------------------------------------------------------------------------------------------

def read_block(path: Path, top_key: str) -> dict:
    """Return the flat `key: value` mapping under one top-level key.

    Deliberately tiny.  It does NOT implement YAML; it implements the one shape this block has,
    and it raises if the block turns out to hold anything else, rather than guessing.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out: dict = {}
    inside = False
    for line in lines:
        if not inside:
            if line.rstrip() == top_key + ":":
                inside = True
            continue
        if line.strip() == "" or line.lstrip().startswith("#"):
            continue
        if not line.startswith(("  ", "\t")):
            break  # dedent: the block ended
        stripped = line.strip()
        if ":" not in stripped:
            raise ValueError("unexpected line in %s block: %r" % (top_key, line))
        key, _, raw = stripped.partition(":")
        value = raw.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        out[key.strip()] = value
    if not inside:
        raise KeyError("no top-level key %r in %s" % (top_key, path))
    return out


# ---------------------------------------------------------------------------------------------
# 2.  THE LAW - S8.5.1, and the four requirements DERIVED from it
# ---------------------------------------------------------------------------------------------

def normalise(s: str) -> str:
    """Lower-case, strip every quote character, collapse whitespace.

    Quote-stripping matters: the LAW writes `"It errored" is not a cause` with double quotes and
    `config/` writes 'It errored' with single ones.  A comparison that keeps them would find a
    difference that is not there.
    """
    s = s.lower()
    s = s.replace("“", "").replace("”", "").replace("‘", "").replace("’", "")
    s = s.replace('"', "").replace("'", "").replace("`", "").replace("*", "")
    s = s.replace("—", " ").replace("–", " ")
    return re.sub(r"\s+", " ", s).strip()


def law_section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i:j]


#: The four requirements, expressed as (label, the phrase that must appear in a condition).
#: The PHRASES ARE NOT TRANSCRIBED CONSTANTS - each is confirmed to occur in the law before it is
#: used, and the file refuses to run if the law no longer carries it.  That is the difference
#: between deriving from the law and making a third copy of it.
_CANDIDATE_REQUIREMENTS = [
    ("the diagnosed-cause requirement", "on a cause that has been diagnosed"),
    ("the it-errored-is-not-a-cause clause", "it errored is not a cause"),
    ("the harness-defect-is-never-branch-b clause", "a harness defect is never branch b"),
    ("the PROTOCOL.md-before-the-branch requirement", "protocol.md"),
]


def derive_requirements(context_text: str):
    """Confirm each candidate phrase against S8.5.1, and return the ones the law actually carries.

    If the law stops carrying one, this function returns fewer than four and every caller notices,
    which is the property a transcribed constant would not have.
    """
    section = law_section(context_text, "### 8.5.1", "### 8.5.2")
    flat = normalise(section)
    derived = []
    for label, phrase in _CANDIDATE_REQUIREMENTS:
        if phrase in flat:
            derived.append((label, phrase))
    return derived, section, flat


# ---------------------------------------------------------------------------------------------
# 3.  THE PREDICATE - one problem per FAILED requirement, naming THAT requirement and no other
# ---------------------------------------------------------------------------------------------

SUPERSEDED_TRIGGER = "the model id is still served"


def branch_b_problems(condition_b: str, requirements) -> list:
    """Which of the derived requirements this candidate `branch_b_condition` fails.

    R-5, pre-committed in the criteria: a condition that weakens EXACTLY ONE requirement yields
    EXACTLY ONE problem, and that problem names the requirement that failed - not all four.
    """
    flat = normalise(condition_b)
    problems = []
    for label, phrase in requirements:
        if phrase not in flat:
            problems.append(
                "branch_b_condition does not carry %s (expected the phrase %r)" % (label, phrase)
            )
    return problems


def branch_a_problems(condition_a: str) -> list:
    flat = normalise(condition_a)
    problems = []
    if SUPERSEDED_TRIGGER in flat:
        problems.append(
            "branch_a_condition still carries the SUPERSEDED trigger %r (Q-057, Q-079)"
            % SUPERSEDED_TRIGGER
        )
    return problems


def requirement_count_problem(requirements, expected: int = 4) -> list:
    """The size check, pinned against a LITERAL - which is the half REVIEW 3 found missing.

    An assertion of the form `len(REQUIREMENTS) == len(REQUIREMENTS)` cannot fail.  This one can.
    """
    if len(requirements) != expected:
        return [
            "expected exactly %d requirements derived from CONTEXT.md S8.5.1, derived %d: %r"
            % (expected, len(requirements), [label for label, _ in requirements])
        ]
    return []


# ---------------------------------------------------------------------------------------------
# 4.  THE SENTINEL REFUSAL PATH, IMPLEMENTED TWICE
# ---------------------------------------------------------------------------------------------

class UndeterminedValueShaped(Exception):
    """The refusal CLAUDE.md hard rule 9 requires: 'a missing value is a hard refusal, never a
    silent fallback'.  Named ...Shaped because this file cannot import the project's class."""


SENTINEL = re.compile(r"^TODO_[A-Z0-9_]+$")


def require_shaped(block: dict, key: str, where: str = "lanes.yaml"):
    """The REFUSING read.  A missing key and a sentinel value are the SAME answer."""
    if key not in block:
        raise UndeterminedValueShaped("%s: %r is not set" % (where, key))
    value = block[key]
    if SENTINEL.match(value.strip()):
        raise UndeterminedValueShaped(
            "%s: 'camel_comparator.%s' is not yet determined (sentinel %r)"
            % (where, key, value.strip())
        )
    return value


def get_shaped(block: dict, key: str) -> str:
    """The NON-refusing read - the mutant N-I2 installed.  A sentinel flows through AS A VALUE."""
    return block.get(key, "")


# ---------------------------------------------------------------------------------------------
# 5.  THE VECTORS
# ---------------------------------------------------------------------------------------------

STRONG = (
    "THE RUN DOES NOT COMPLETE, ON A CAUSE THAT HAS BEEN DIAGNOSED AND RECORDED IN PROTOCOL.md "
    "BEFORE A BRANCH IS SELECTED. 'It errored' is not a cause, and a harness defect is NEVER "
    "Branch B."
)


def weaken(text: str, strong: str, weak: str) -> str:
    """Replace a strong phrase with a weaker one, case-insensitively, once."""
    return re.sub(re.escape(strong), weak, text, count=1, flags=re.IGNORECASE)


def build_vectors(requirements):
    """>= 20 vectors.  Each is (id, description, condition, expected_problem_labels)."""
    v = []
    labels = [label for label, _ in requirements]

    v.append(("V01", "HEAD's own strong condition", STRONG, []))
    v.append(("V02", "the strong condition, lower-cased", STRONG.lower(), []))
    v.append(("V03", "the strong condition, upper-cased", STRONG.upper(), []))
    v.append(("V04", "the strong condition with collapsed whitespace",
              re.sub(r"\s+", " ", STRONG), []))
    v.append(("V05", "the strong condition with double quotes for single",
              STRONG.replace("'", '"'), []))

    # --- the four WEAK forms, one per requirement.  Each must flag EXACTLY its own. ------------
    v.append(("V06", "diagnosed-cause weakened to bare 'cause' (REVIEW 3's N-B)",
              weaken(STRONG, "ON A CAUSE THAT HAS BEEN DIAGNOSED", "FOR SOME CAUSE"),
              [labels[0]]))
    v.append(("V07", "it-errored clause deleted",
              weaken(STRONG, "'It errored' is not a cause, and ", ""),
              [labels[1]]))
    v.append(("V08", "harness clause INVERTED to SOMETIMES (REVIEW 3's N-C exhibit)",
              weaken(STRONG, "a harness defect is NEVER Branch B",
                     "a harness defect is SOMETIMES Branch B"),
              [labels[2]]))
    v.append(("V09", "PROTOCOL.md replaced by CONTEXT.md (REVIEW 3's N-D)",
              weaken(STRONG, "PROTOCOL.md", "CONTEXT.md"),
              [labels[3]]))

    # --- pairs and the empty case -------------------------------------------------------------
    two = weaken(weaken(STRONG, "ON A CAUSE THAT HAS BEEN DIAGNOSED", "FOR SOME CAUSE"),
                 "a harness defect is NEVER Branch B", "a harness defect is SOMETIMES Branch B")
    v.append(("V10", "two requirements weakened at once", two, [labels[0], labels[2]]))
    v.append(("V11", "REVIEW 3's single fixture - the run does not complete",
              "the run does not complete", labels[:]))
    v.append(("V12", "the empty condition", "", labels[:]))
    v.append(("V13", "whitespace only", "   \n  ", labels[:]))
    v.append(("V14", "an unrelated sentence", "Branch B is taken when we feel like it.", labels[:]))

    # --- near-misses that must still PASS, so the predicate is not merely strict ---------------
    v.append(("V15", "extra prose appended", STRONG + " See Q-057 and Q-079.", []))
    v.append(("V16", "extra prose prepended", "Pre-registered. " + STRONG, []))
    v.append(("V17", "the phrase order permuted",
              "'It errored' is not a cause, and a harness defect is NEVER Branch B. THE RUN DOES "
              "NOT COMPLETE, ON A CAUSE THAT HAS BEEN DIAGNOSED AND RECORDED IN PROTOCOL.md "
              "BEFORE A BRANCH IS SELECTED.", []))
    v.append(("V18", "protocol.md in lower case", STRONG.replace("PROTOCOL.md", "protocol.md"), []))
    v.append(("V19", "backticks around PROTOCOL.md",
              STRONG.replace("PROTOCOL.md", "`PROTOCOL.md`"), []))
    v.append(("V20", "smart quotes around It errored",
              STRONG.replace("'It errored'", "‘It errored’"), []))

    # --- the near-miss that must FAIL: a substring that reads as the phrase but is not ---------
    v.append(("V21", "'diagnosed' present but not 'on a cause that has been diagnosed'",
              weaken(STRONG, "ON A CAUSE THAT HAS BEEN DIAGNOSED",
                     "WITH A DIAGNOSED SOMETHING-OR-OTHER"),
              [labels[0]]))
    v.append(("V22", "'harness' present, the clause absent",
              weaken(STRONG, "a harness defect is NEVER Branch B",
                     "harness questions are out of scope"),
              [labels[2]]))
    v.append(("V23", "'md' present, PROTOCOL.md absent",
              weaken(STRONG, "PROTOCOL.md", "some.md"), [labels[3]]))
    v.append(("V24", "'cause' present three times, the requirement absent",
              "THE RUN DOES NOT COMPLETE. A cause, a cause, a cause. 'It errored' is not a cause, "
              "and a harness defect is NEVER Branch B, recorded in PROTOCOL.md before a branch is "
              "selected.", [labels[0]]))
    return v


# ---------------------------------------------------------------------------------------------
# 6.  RUN
# ---------------------------------------------------------------------------------------------

def main() -> int:
    out = []
    say = out.append

    say("C13 REVIEW 4 - SCOPED REIMPLEMENTATION (Phase 1 seal)")
    say("repo: %s" % REPO)
    say("imports from src/: NONE (asserted at import time; sys.modules clean)")
    say("")

    context_text = CONTEXT.read_text(encoding="utf-8")
    requirements, section, flat = derive_requirements(context_text)

    say("-- R-1  requirements DERIVED from CONTEXT.md S8.5.1 (never transcribed) --")
    say("   S8.5.1 window: '### 8.5.1' .. '### 8.5.2'  ->  %d chars" % len(section))
    for label, phrase in requirements:
        say("   [derived] %-46s  phrase=%r" % (label, phrase))
    count_problem = requirement_count_problem(requirements, 4)
    say("   R-1 expected 4, derived %d  ->  %s"
        % (len(requirements), "PASS" if not count_problem else "FAIL " + count_problem[0]))
    say("")

    block = read_block(LANES, "camel_comparator")
    say("-- config/lanes.yaml camel_comparator, read by THIS FILE'S own parser --")
    for k in sorted(block):
        val = block[k]
        say("   %-20s = %s" % (k, (val[:96] + " ...") if len(val) > 96 else val))
    say("")

    fails = 0

    say("-- R-2  HEAD's branch_b_condition against the predicate --")
    p = branch_b_problems(block["branch_b_condition"], requirements)
    say("   expected 0 problems, got %d  ->  %s" % (len(p), "PASS" if not p else "FAIL"))
    for x in p:
        say("      %s" % x)
    fails += 0 if not p else 1
    say("")

    say("-- R-3  HEAD's branch_a_condition carries the SUPERSEDED trigger? --")
    pa = branch_a_problems(block["branch_a_condition"])
    say("   expected NO, got %s  ->  %s" % ("YES" if pa else "NO", "PASS" if not pa else "FAIL"))
    fails += 0 if not pa else 1
    say("")

    say("-- R-4/R-5/R-6  the vectors --")
    vectors = build_vectors(requirements)
    agree = 0
    for vid, desc, cond, expected_labels in vectors:
        got = branch_b_problems(cond, requirements)
        got_labels = [lab for lab, _ in requirements
                      if any(lab in g for g in got)]
        ok = sorted(got_labels) == sorted(expected_labels)
        agree += 1 if ok else 0
        if not ok:
            fails += 1
        say("   %s %-4s exp=%d got=%d  %s"
            % ("OK " if ok else "XX ", vid, len(expected_labels), len(got_labels), desc))
    say("   %d / %d vectors agree  (docs/reviews/README.md asks for >= 20)"
        % (agree, len(vectors)))
    say("")

    say("-- R-5 restated as the property it exists for --")
    singles = [v for v in vectors if len(v[3]) == 1]
    exact = [v for v in singles if len(branch_b_problems(v[2], requirements)) == 1]
    say("   vectors weakening EXACTLY ONE requirement: %d" % len(singles))
    say("   of those, vectors on which the predicate names EXACTLY ONE problem: %d" % len(exact))
    say("   -> %s" % ("PASS - one weakening, one problem"
                      if len(exact) == len(singles) else "FAIL - the predicate over-reports"))
    if len(exact) != len(singles):
        fails += 1
    say("")

    say("-- R-7/R-8  the sentinel refusal path, both readers --")
    sentinel_block = dict(block)
    sentinel_block["branch_b_condition"] = "TODO_C14_PENDING"
    try:
        require_shaped(sentinel_block, "branch_b_condition")
        say("   R-7 require-shaped read: RETURNED a value  ->  FAIL (hard rule 9)")
        fails += 1
    except UndeterminedValueShaped as exc:
        say("   R-7 require-shaped read RAISED: %s  ->  PASS" % exc)
    got = get_shaped(sentinel_block, "branch_b_condition")
    say("   R-8 get-shaped read RETURNED %r  ->  %s"
        % (got, "PASS - this is N-I2's exhibit" if got == "TODO_C14_PENDING" else "FAIL"))
    if got != "TODO_C14_PENDING":
        fails += 1
    sent_problems = branch_b_problems(got, requirements)
    say("   and under the get-shaped read the sentinel yields %d CONTENT complaints instead of a"
        % len(sent_problems))
    say("   refusal - which is exactly the difference REVIEW 3's N-I2 rested on.")
    say("")

    say("-- R-9  the branch VALUE itself is undecided, and the refusal is the answer --")
    try:
        require_shaped(block, "branch")
        say("   branch resolved to a value  ->  FAIL (RUN-1 has not happened)")
        fails += 1
    except UndeterminedValueShaped as exc:
        say("   branch: %s  ->  PASS" % exc)
    say("")

    say("RESULT: %s  (%d check(s) failed)" % ("ALL AGREE" if fails == 0 else "DIVERGENCE", fails))
    text = "\n".join(out) + "\n"
    sys.stdout.write(text.encode("ascii", "replace").decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
