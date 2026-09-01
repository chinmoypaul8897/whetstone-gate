#!/usr/bin/env python3
"""C13 REVIEW 3 — the SCOPED reimplementation of the CHANGED SURFACE.

Session ``c09c385b``.  Written and committed in PHASE 1, before any fix artefact was opened
(see ``c13_review3_criteria.md`` §0 for the blindness boundary this file was written under).

THE RULING THIS FILE EXISTS UNDER
---------------------------------
``docs/reviews/README.md``: *"a ``full`` review with no reimplementation CANNOT PASS."*
``QUESTIONS.md``, the C6 REVIEW 3 ruling block: *"ON A RE-REVIEW THE REIMPLEMENTATION IS OF THE
CHANGED SURFACE, INDEPENDENTLY DERIVED … written from CONTEXT.md and config/ alone, importing
nothing from ``src/``."*

This session's prompt scopes it to exactly two things:

  1. **the branch-condition predicate**  — what ``camel_comparator.branch_a_condition`` and
     ``branch_b_condition`` must say, derived from ``CONTEXT.md`` v1.9 §8.5.1;
  2. **the two provenance regexes** — the table/figure number and the appendix, derived from
     ``Q-058``'s ruling as recorded in ``CONTEXT.md`` v1.9 §8.5.1 / §8.5.2.

WHAT THIS FILE IMPORTS
----------------------
stdlib only.  ``sys.path`` is never touched, ``whetstone_gate`` is never imported, nothing under
``src/`` is read.  ``config/lanes.yaml`` is parsed by the minimal reader below rather than by the
project's loader, for the same reason: the loader is ``src/``.

⚠️ WHAT IS DERIVED HERE AND WHAT IS READ
----------------------------------------
The **requirements** are derived from ``CONTEXT.md``'s own text at run time — never transcribed
into this file as a literal list.  That is deliberate and it is the property this file exists to
have: if ``CONTEXT.md`` §8.5.1 is amended, this file's expectations move with the law, and a
config that no longer matches goes red **at the law**.  A reimplementation carrying its own copy
of the phrase list would be a third copy that can drift, which is the defect ``Q-064`` is about.

The **vectors** for the two regexes are authored here, before the project's regexes were seen.

Usage::

    python docs/reviews/independent/c13_review3_reimpl.py [--repo <path>]

Exit code 0 always; the report is the output.  Phase 2 diffs the project's answers against it.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------------------------
# 0. A minimal YAML scalar reader — enough for config/lanes.yaml's camel_comparator block.
#    Written rather than imported so that nothing about how the project reads its own config
#    can influence what this file believes the config says.
# --------------------------------------------------------------------------------------------


def _dedent_block(lines: list[str], indent: int, fold: bool) -> str:
    body = [ln[indent:] if len(ln) >= indent else ln.strip() for ln in lines]
    if fold:
        # YAML folded scalars join on single spaces, blank lines becoming newlines.
        out: list[str] = []
        run: list[str] = []
        for ln in body:
            if ln.strip() == "":
                if run:
                    out.append(" ".join(run))
                    run = []
                out.append("")
            else:
                run.append(ln.strip())
        if run:
            out.append(" ".join(run))
        return "\n".join(out).strip("\n")
    return "\n".join(body).rstrip("\n")


def read_block(path: Path, block: str) -> dict[str, str]:
    """Return the scalar keys of one top-level mapping ``block`` in a YAML file.

    Handles plain, single-quoted, double-quoted and block (``|`` / ``>``, with the ``-``/``+``
    chomping indicators) scalars, and skips comments and nested mappings.  It is deliberately
    small: anything it cannot parse is reported rather than guessed at.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out: dict[str, str] = {}

    start = None
    for i, ln in enumerate(lines):
        if re.match(rf"^{re.escape(block)}\s*:\s*(#.*)?$", ln):
            start = i + 1
            break
    if start is None:
        return out

    # The block's own indentation is set by its first non-blank, non-comment child.
    child_indent = None
    i = start
    while i < len(lines):
        ln = lines[i]
        stripped = ln.strip()
        if stripped == "" or stripped.startswith("#"):
            i += 1
            continue
        indent = len(ln) - len(ln.lstrip(" "))
        if child_indent is None:
            if indent == 0:
                break  # the block was empty
            child_indent = indent
        if indent < child_indent:
            break  # dedented out of the block
        if indent > child_indent:
            i += 1
            continue

        m = re.match(r"^\s*([A-Za-z0-9_.\-]+)\s*:\s*(.*?)\s*$", ln)
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2)

        if rest.startswith("|") or rest.startswith(">"):
            fold = rest.startswith(">")
            body: list[str] = []
            j = i + 1
            block_indent = None
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() == "":
                    body.append("")
                    j += 1
                    continue
                nindent = len(nxt) - len(nxt.lstrip(" "))
                if nindent <= child_indent:
                    break
                if block_indent is None:
                    block_indent = nindent
                body.append(nxt)
                j += 1
            out[key] = _dedent_block(body, block_indent or 0, fold)
            i = j
            continue

        # strip a trailing comment from a plain scalar only (never from a quoted one)
        if rest.startswith('"') and rest.endswith('"') and len(rest) >= 2:
            val = rest[1:-1].replace('\\"', '"')
        elif rest.startswith("'") and rest.endswith("'") and len(rest) >= 2:
            val = rest[1:-1].replace("''", "'")
        else:
            val = re.sub(r"\s+#.*$", "", rest).strip()
        out[key] = val
        i += 1

    return out


# --------------------------------------------------------------------------------------------
# 1. THE BRANCH-CONDITION PREDICATE, derived from CONTEXT.md v1.9 §8.5.1.
# --------------------------------------------------------------------------------------------

# The section of the law that governs.  Located by heading, never by line number.
_S851_START = re.compile(r"^###\s*8\.5\.1\b", re.M)
_NEXT_HEADING = re.compile(r"^#{2,3}\s+\d", re.M)


def spec_section_851(context_md: Path) -> str:
    text = context_md.read_text(encoding="utf-8")
    m = _S851_START.search(text)
    if not m:
        raise SystemExit("FATAL: CONTEXT.md has no §8.5.1 heading — the law moved.")
    tail = text[m.end():]
    n = _NEXT_HEADING.search(tail)
    return tail[: n.start()] if n else tail


def derive_requirements(section: str) -> dict[str, list[str]]:
    """Derive, FROM THE LAW'S OWN TEXT, what each branch's condition must carry.

    Nothing here is a transcription of ``config/``.  Each requirement is a phrase this
    reviewer located in §8.5.1 by pattern, and the pattern is what is written down — so an
    amendment to §8.5.1 that removes the phrase makes the requirement disappear from this
    file too, and a config still carrying it becomes visible as an over-specification rather
    than silently correct.
    """
    flat = re.sub(r"\s+", " ", section)

    reqs: dict[str, list[str]] = {"branch_a": [], "branch_b": [], "forbidden_a": []}

    # --- Branch A.  §8.5.1's Branch A heading is literally "Branch A — it runs."
    if re.search(r"Branch A\s*[—-]+\s*\*{0,2}it runs", flat):
        reqs["branch_a"].append("run-completes")

    # --- The phrasing Q-057's ruling identifies as indistinguishable from a harness defect.
    # It is FORBIDDEN in branch_a_condition.  Derived from the ⚠️ hazard paragraph, which says
    # dispatch SUCCEEDS on the suffixed string, so a provider error cannot be read as "not served".
    if re.search(r"indistinguishable from Branch B", flat):
        reqs["forbidden_a"].append("the model id is still served")

    # --- Branch B.  Every clause below is present in §8.5.1 v1.9 and is located, not assumed.
    b: list[str] = []
    if re.search(r"ON A CAUSE THAT HAS BEEN DIAGNOSED", flat):
        b.append("diagnosed-cause")
    if re.search(r'"?It errored"? is not a cause', flat, re.I):
        b.append("it-errored-is-not-a-cause")
    if re.search(r"a harness defect is never Branch B", flat, re.I):
        b.append("harness-defect-is-never-branch-b")
    if re.search(r"RUN-1 records the diagnosed cause in .?PROTOCOL\.md.? before it selects a branch",
                 flat, re.I):
        b.append("protocol-md-before-the-branch")
    reqs["branch_b"] = b
    return reqs


# How each derived requirement is recognised in a config string.  These are the reviewer's own
# recognisers; they are intentionally phrase-level and case-insensitive on the connective words
# only, because the law's own emphasis markers (**, ⚠️) must not be required in a YAML scalar.
_RECOGNISERS: dict[str, re.Pattern[str]] = {
    "run-completes": re.compile(r"\brun\b[^.]{0,60}\bcomplet", re.I),
    "diagnosed-cause": re.compile(r"\bcause\b[^.]{0,40}\bdiagnos", re.I),
    "it-errored-is-not-a-cause": re.compile(r"it errored[^.]{0,20}is not a cause", re.I),
    "harness-defect-is-never-branch-b": re.compile(r"harness defect is never branch\s*b", re.I),
    "protocol-md-before-the-branch": re.compile(
        r"PROTOCOL\.md\b(?:(?!\bbefore\b).){0,120}\bbefore\b", re.I | re.S),
}


def evaluate_branch_conditions(reqs: dict[str, list[str]],
                               cfg: dict[str, str]) -> list[tuple[str, str, bool, str]]:
    """Return (check-id, requirement, holds, evidence) for every derived requirement."""
    results: list[tuple[str, str, bool, str]] = []

    a = cfg.get("branch_a_condition")
    b = cfg.get("branch_b_condition")

    results.append(("A-present", "branch_a_condition exists and is non-empty",
                    bool(a and a.strip()), repr(a)[:200]))
    results.append(("B-present", "branch_b_condition exists and is non-empty",
                    bool(b and b.strip()), repr(b)[:200]))

    for bad in reqs["forbidden_a"]:
        holds = bool(a) and bad.lower() not in (a or "").lower()
        results.append((f"A-forbids::{bad}",
                        f"branch_a_condition does NOT contain {bad!r}", holds, ""))

    for name in reqs["branch_a"]:
        rx = _RECOGNISERS[name]
        m = rx.search(a or "")
        results.append((f"A-requires::{name}",
                        f"branch_a_condition carries {name}", bool(m),
                        m.group(0) if m else ""))

    for name in reqs["branch_b"]:
        rx = _RECOGNISERS[name]
        m = rx.search(b or "")
        results.append((f"B-requires::{name}",
                        f"branch_b_condition carries {name}", bool(m),
                        m.group(0) if m else ""))

    return results


# --------------------------------------------------------------------------------------------
# 2. THE TWO PROVENANCE REGEXES, derived from Q-058's ruling as it stands in CONTEXT.md v1.9.
# --------------------------------------------------------------------------------------------
#
# The ruling: "EVERY PUBLISHED THIRD-PARTY FIGURE CARRIES THE TABLE OR FIGURE NUMBER, ITS
# APPENDIX, ITS BASE MODEL AND ITS ROW."  Two of those four are shaped enough to regex, and the
# defect the ruling is about — "Tables 5–7" standing in for "Table 2" — is a RANGE where a single
# table belongs.  So the table recogniser must reject a range and must reject the plural, and the
# appendix recogniser must name exactly one appendix.
#
# ⚠️ Two readings of the appendix field are BOTH defensible and both are computed, because
# CONTEXT.md v1.9 writes the appendix WITH a parenthetical title — 'Appendix B ("Full results
# tables")' — while the field itself is 'Appendix B'.  A divergence between the project's regex
# and either of these is a datum for Phase 2 to classify, not automatically a defect.

TABLE_NUMBER = re.compile(r"(?:Table|Figure) \d+")
APPENDIX_STRICT = re.compile(r"Appendix [A-Z]")
APPENDIX_WITH_TITLE = re.compile(r'Appendix [A-Z](?: \("[^"]+"\))?')

def table_ok(s: str) -> bool:
    """This reviewer's independent table/figure recogniser.

    fullmatch, deliberately: ``Q-058``'s defect is a citation that CONTAINS a plausible table
    reference inside something wider.  A search-based check accepts ``Table 5-7`` because
    ``Table 5`` is a prefix of it, which is the exact failure mode ``OF-101`` names.
    """
    return bool(TABLE_NUMBER.fullmatch(s or ""))


def appendix_ok(s: str, allow_title: bool = False) -> bool:
    rx = APPENDIX_WITH_TITLE if allow_title else APPENDIX_STRICT
    return bool(rx.fullmatch(s or ""))


# ---- the vectors.  Authored in Phase 1, before the project's regexes were seen. --------------

TABLE_VECTORS: list[tuple[str, bool, str]] = [
    ("Table 2", True, "the headline pair's own citation, CONTEXT.md v1.9 §8.5.1"),
    ("Table 4", True, "P2's premise, Appendix B"),
    ("Table 7", True, "P2's retained citation, Appendix C"),
    ("Figure 9", True, "Table 4's ceiling source"),
    ("Figure 11", True, "Table 7's ceiling source"),
    ("Table 10", True, "two digits must be accepted — nothing caps the number at one digit"),
    # --- the defect Q-058 is about, in every shape it has actually appeared in this repository
    ("Tables 5-7", False, "⚠️ THE DEFECT ITSELF — ASCII hyphen, plural"),
    ("Tables 5–7", False, "⚠️ THE DEFECT ITSELF — en dash, plural"),
    ("Tables 5—7", False, "⚠️ THE DEFECT ITSELF — em dash, plural"),
    ("Table 5-7", False, "⚠️ OF-101's EXACT CASE — singular range; a `match` accepts this"),
    ("Table 5–7", False, "singular range, en dash"),
    ("Tables 5, 6 and 7", False, "the prose form of the same range"),
    ("Tables 5 and 7", False, "two tables where one belongs"),
    # --- shapes that are simply not a citation
    ("Table", False, "the word alone"),
    ("Table ", False, "trailing space, no number"),
    ("Tables", False, "plural alone"),
    ("", False, "empty — the field is missing"),
    ("   ", False, "whitespace only"),
    ("table 2", False, "lower case — a label, not the paper's own"),
    ("TABLE 2", False, "upper case"),
    ("Table2", False, "no separator"),
    ("Table 2 ", False, "trailing space — fullmatch must reject; a strip() would accept"),
    (" Table 2", False, "leading space"),
    ("Table 2, Appendix B", False, "two fields in one — the appendix belongs in its own field"),
    ("Appendix B", False, "the wrong field's value"),
    ("Table 2 of arXiv 2503.18813v2", False,
     "⚠️ A URL TO A PAPER IS NOT A URL TO A TABLE — the ruling's own sentence, in field form"),
    ("Table -1", False, "negative"),
    ("Figure 11(b)", False, "a sub-figure is not the figure's own number"),
]

APPENDIX_VECTORS: list[tuple[str, bool, bool, str]] = [
    # (value, strict_expected, with_title_expected, why)
    ("Appendix B", True, True, "Tables 2 and 4"),
    ("Appendix C", True, True, "Tables 5, 6 and 7"),
    ("Appendix A", True, True, "a valid appendix this project does not cite"),
    ('Appendix B ("Full results tables")', False, True,
     "⚠️ CONTEXT.md v1.9 writes it THIS way — the two readings differ here and only here"),
    ('Appendix C ("Baseline results")', False, True, "the same, for Appendix C"),
    ("Appendix", False, False, "the word alone"),
    ("", False, False, "empty — the field is missing"),
    ("appendix B", False, False, "lower case"),
    ("Appendix BB", False, False, "two letters"),
    ("Appendix 2", False, False, "a number where a letter belongs"),
    ("Appendices B-C", False, False, "⚠️ THE RANGE SHAPE, one field over"),
    ("Appendix B, Appendix C", False, False, "two appendices in one field"),
    ("Appendix B ", False, False, "trailing space"),
    (" Appendix B", False, False, "leading space"),
    ("B", False, False, "the letter alone"),
]


# --------------------------------------------------------------------------------------------
# 3. Report
# --------------------------------------------------------------------------------------------


def _rule(w: str = "=") -> str:
    return w * 94


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[3]))
    args = ap.parse_args(argv)
    repo = Path(args.repo)

    out = io.StringIO()
    p = lambda *a: print(*a, file=out)  # noqa: E731

    # This file must be provably independent of src/.  Assert it rather than claim it.
    leaked = sorted(m for m in sys.modules if m == "whetstone_gate"
                    or m.startswith("whetstone_gate."))
    p(_rule())
    p("C13 REVIEW 3 — SCOPED REIMPLEMENTATION OF THE CHANGED SURFACE")
    p("session c09c385b · imports nothing from src/ · stdlib only")
    p(_rule())
    p(f"repo                      : {repo}")
    p(f"whetstone_gate in modules : {leaked or 'NONE'}   <-- must be NONE")
    p(f"this file                 : {Path(__file__).resolve()}")
    p("")

    context_md = repo / "CONTEXT.md"
    lanes = repo / "config" / "lanes.yaml"
    version = ""
    m = re.search(r"^#\s*CONTEXT\.md\s*[—-]+\s*(v[\d.]+)", context_md.read_text(encoding="utf-8"),
                  re.M)
    if m:
        version = m.group(1)
    p(f"CONTEXT.md version read   : {version}")
    p(f"config read (raw, not via the project loader): {lanes}")
    p("")

    # ---- 1. the branch-condition predicate -------------------------------------------------
    p(_rule())
    p("1. THE BRANCH-CONDITION PREDICATE — requirements DERIVED FROM CONTEXT.md §8.5.1,")
    p("   then applied to config/lanes.yaml.  THE LAW IS ASSERTED FIRST; the config second.")
    p(_rule())
    section = spec_section_851(context_md)
    reqs = derive_requirements(section)
    p(f"§8.5.1 located: {len(section)} chars")
    p(f"  derived Branch A requirements : {reqs['branch_a'] or '(none derived)'}")
    p(f"  derived Branch A prohibitions : {reqs['forbidden_a'] or '(none derived)'}")
    p(f"  derived Branch B requirements : {reqs['branch_b'] or '(none derived)'}")
    p("")
    if not reqs["branch_b"]:
        p("  ⚠️ NO BRANCH-B REQUIREMENT COULD BE DERIVED FROM THE LAW.")
        p("     Either §8.5.1 no longer carries the diagnosis requirement, or this reader is")
        p("     wrong.  Either way the config cannot be judged and this is a finding.")
        p("")

    cfg = read_block(lanes, "camel_comparator")
    p(f"camel_comparator keys parsed  : {sorted(cfg)}")
    p("")
    for key in ("branch", "branch_a_condition", "branch_b_condition", "branch_b_action"):
        val = cfg.get(key)
        p(f"  {key}:")
        if val is None:
            p("      <ABSENT>")
        else:
            for ln in (val.splitlines() or [""]):
                p(f"      {ln}")
    p("")

    results = evaluate_branch_conditions(reqs, cfg)
    width = max(len(r[0]) for r in results)
    n_fail = 0
    for cid, desc, holds, ev in results:
        flag = "OK  " if holds else "FAIL"
        if not holds:
            n_fail += 1
        p(f"  [{flag}] {cid.ljust(width)}  {desc}")
        if ev:
            p(f"         evidence: {ev}")
    p("")
    p(f"  branch-condition predicate: {len(results) - n_fail}/{len(results)} hold, "
      f"{n_fail} fail")
    p("")

    # ---- 2. the two provenance regexes ------------------------------------------------------
    p(_rule())
    p("2. THE TWO PROVENANCE REGEXES — this reviewer's own, with ITS OWN vectors.")
    p(f"   TABLE_NUMBER        = {TABLE_NUMBER.pattern!r}   (fullmatch)")
    p(f"   APPENDIX_STRICT     = {APPENDIX_STRICT.pattern!r}   (fullmatch)")
    p(f"   APPENDIX_WITH_TITLE = {APPENDIX_WITH_TITLE.pattern!r}   (fullmatch)")
    p(_rule())
    p("")
    p(f"  TABLE / FIGURE — {len(TABLE_VECTORS)} vectors")
    bad = 0
    for value, expected, why in TABLE_VECTORS:
        got = table_ok(value)
        ok = got == expected
        if not ok:
            bad += 1
        p(f"    [{'OK ' if ok else 'XX '}] {'ACCEPT' if got else 'REJECT'}  "
          f"(expected {'ACCEPT' if expected else 'REJECT'})  {value!r}")
        p(f"           {why}")
    p(f"    -> {len(TABLE_VECTORS) - bad}/{len(TABLE_VECTORS)} agree with this reviewer's "
      f"own expectation")
    p("")
    p(f"  APPENDIX — {len(APPENDIX_VECTORS)} vectors, BOTH readings computed")
    bad_a = 0
    for value, exp_strict, exp_title, why in APPENDIX_VECTORS:
        g_s = appendix_ok(value, allow_title=False)
        g_t = appendix_ok(value, allow_title=True)
        ok = (g_s == exp_strict) and (g_t == exp_title)
        if not ok:
            bad_a += 1
        p(f"    [{'OK ' if ok else 'XX '}] strict={'Y' if g_s else 'N'} "
          f"withTitle={'Y' if g_t else 'N'}  "
          f"(expected {'Y' if exp_strict else 'N'}/{'Y' if exp_title else 'N'})  {value!r}")
        p(f"           {why}")
    p(f"    -> {len(APPENDIX_VECTORS) - bad_a}/{len(APPENDIX_VECTORS)} agree")
    p("")
    p(f"  TOTAL VECTORS: {len(TABLE_VECTORS) + len(APPENDIX_VECTORS)}  "
      f"(docs/reviews/README.md asks for >= 20)")
    p("")

    # ---- 3. the fullmatch-vs-match discrimination, isolated ---------------------------------
    p(_rule())
    p("3. OF-101 ISOLATED — which vectors DISCRIMINATE fullmatch from match?")
    p("   A vector on which both behave the same cannot pin `fullmatch`.")
    p(_rule())
    disc = [v for v, _e, _w in TABLE_VECTORS
            if bool(TABLE_NUMBER.fullmatch(v)) != bool(TABLE_NUMBER.match(v))]
    for v in disc:
        p(f"    DISCRIMINATES: {v!r}   fullmatch=REJECT  match=ACCEPT")
    if not disc:
        p("    NONE — which would mean the vector set cannot pin fullmatch at all.")
    p(f"    -> {len(disc)} of {len(TABLE_VECTORS)} table vectors discriminate.")
    p("")
    p("    ⚠️ `Tables 5-7` (plural) is NOT among them: `match` rejects it too, because the")
    p("       pattern requires the singular. That is exactly OF-101's point — the plural range")
    p("       is the only shape the project's parametrised fixture was reported to fire, so it")
    p("       cannot be the vector that pins `fullmatch`.")
    p("")

    p(_rule())
    p("END")
    p(_rule())

    text = out.getvalue()
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
