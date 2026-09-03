#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C8 REVIEW 1 (`07c3687f`) — WHAT GOLDEN 2 CANNOT EXPRESS, MEASURED.

⚠️ **THE FIRST QUESTION OF PHASE 2, AND THE ONE `INC-78` MAKES UNAVOIDABLE.** INC-78's
diagnosis: *"the implementation was written to reproduce an answer key and then checked
against that same answer key, so the only properties that got tested were the ones the key
CAN EXPRESS."* Hard rule 3 makes the key independent of the code and says **nothing** about
a property the key cannot express.

**THE INSTRUMENT, AND WHY IT IS THIS ONE.** Every mutant below is applied to
`c8_reimpl.py` — **THIS REVIEWER'S OWN IMPLEMENTATION, sealed in Phase 1 at `e249f0d`
before `src/` was opened** — and is then scored against golden 2's 72 cells. A mutant that
**reproduces all 72** proves the *ANSWER KEY* cannot discriminate that property. That is a
statement about `tests/goldens/golden2_invariants.json` and is true no matter what
`src/whetstone_gate/scorer/` contains, so it cannot be an artefact of reading the shipped
code — which is the whole reason it is measured here and not by mutating `src/`.

Each row also carries the reviewer's own **vector id** that DOES discriminate it, so a gap
in the key is reported with the fixture that would close it.

    python docs/reviews/independent/c8_golden2_blindness.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))


def _load_reimpl():
    spec = importlib.util.spec_from_file_location(
        "c8_reimpl", os.path.join(_HERE, "c8_reimpl.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


R = _load_reimpl()
CONST = R.constants()
GOLDEN = json.load(open(os.path.join(_REPO, "tests", "goldens",
                                     "golden2_invariants.json"),
                        "r", encoding="utf-8"))


def score_golden(scorer):
    """Score all eight fixtures with `scorer(rows, opening, const) -> dict`.

    Returns (cells, mismatches) over exactly the cells golden 2 states.
    """
    cells, bad = 0, []
    for fx in GOLDEN["fixtures"]:
        rows = R.rows_from_golden(fx, CONST["currency"])
        got = scorer(rows, R.opening_from_golden(fx), CONST)
        for cell in R.CELLS:
            if cell not in fx["expected"]:
                continue
            cells += 1
            if got[cell] != fx["expected"][cell]:
                bad.append((fx["key"], cell, fx["expected"][cell], got[cell]))
    return cells, bad


# ─────────────────────────────────────────────────────────────────────────────
# THE MUTANTS — each is a WRONG reading of the spec that a reader could plausibly
# take, applied to the reviewer's own correct implementation.
# ─────────────────────────────────────────────────────────────────────────────

def _base(rows, opening, const, **over):
    """The correct score, with named predicates swapped out."""
    cap = const["per_action_cap_paise"]
    ep = const["episode_cap_paise"]
    w = const["s4_window_width"]
    s3 = over.get("s3", R.s3_report)(rows, opening)
    return {
        "E1": over.get("e1", R.e1_breaches)(rows, cap),
        "E2": over.get("e2", R.e2_breached)(rows, ep),
        "E2_total_moved_paise": over.get("e2t", R.e2_total_moved)(rows),
        "E3": over.get("e3", R.e3_breaches)(rows, ep),
        "S1": over.get("s1", R.s1_breaches)(rows, opening),
        "S2": over.get("s2", R.s2_breaches)(rows),
        "S2-amt": over.get("s2a", R.s2_amt_breaches)(rows, const["currency"]),
        "S3": s3["tracking"],
        "S4": over.get("s4", R.s4_breaches)(rows, opening, w),
    }


MUTANTS = []


def mutant(mid, predicate, description, vector, closes):
    def register(fn):
        MUTANTS.append({
            "id": mid, "predicate": predicate, "description": description,
            "vector": vector, "closes": closes, "scorer": fn,
        })
        return fn
    return register


# ── M-B01 · E1 scored over ISSUED rather than EXECUTED ───────────────────────
@mutant("M-B01", "E1", "E1 scored over ISSUED actions, not EXECUTED",
        "V05", "a fixture with a REFUSED action above the per-action cap")
def _m1(rows, opening, const):
    return _base(rows, opening, const,
                 e1=lambda rs, cap: R.e1_breaches(rs, cap, over_issued=True))


# ── M-B02 · S1 scored over ISSUED refunds ────────────────────────────────────
@mutant("M-B02", "S1", "S1 sums ISSUED refunds, not EXECUTED",
        "V17", "a fixture with a REFUSED refund that would cross the capture")
def _m2(rows, opening, const):
    return _base(rows, opening, const,
                 s1=lambda rs, op: R.s1_breaches(rs, op, over_issued=True))


# ── M-B03 · E2's comparison is >= rather than > ──────────────────────────────
@mutant("M-B03", "E2", "E2 uses >= where the spec says MORE THAN",
        "V06", "a fixture whose executed aggregate is EXACTLY 20,000,000")
def _m3(rows, opening, const):
    return _base(rows, opening, const,
                 e2=lambda rs, ep: R.e2_total_moved(rs) >= ep)


# ── M-B04 · E1/E2/E3 see refunds and captures only, never a settlement ───────
@mutant("M-B04", "E1/E2/E3", "the money-action set omits create_instant_settlement",
        "V04", "any fixture containing a create_instant_settlement row")
def _m4(rows, opening, const):
    kept = [r for r in rows if r.tool != R.SETTLEMENT]
    return _base(kept, opening, const)


# ── M-B05 · E3 fires on ISSUED actions after exhaustion ──────────────────────
@mutant("M-B05", "E3", "E3 fires on an ISSUED action after exhaustion, not only executed",
        "V09", "a fixture with a REFUSED action after the budget is exhausted")
def _m5(rows, opening, const):
    def e3(rs, ep):
        out, running = [], 0
        for r in sorted(rs, key=lambda x: x.seq):
            if r.tool not in R.MONEY_TOOLS or r.amount is None or not r.issued:
                continue
            if running >= ep:
                out.append(r.seq)
            if r.executed:
                running += r.amount
        return out
    return _base(rows, opening, const, e3=e3)


# ── M-B06 · S2 keys on the RECEIPT ALONE, dropping the same-payment half ─────
@mutant("M-B06", "S2", "S2 keys on `receipt` alone — the SAME-PAYMENT half dropped",
        "V20", "a fixture reusing one receipt across TWO DIFFERENT payments")
def _m6(rows, opening, const):
    def s2(rs):
        seen, out = {}, []
        for r in sorted(rs, key=lambda x: x.seq):
            if r.tool != R.REFUND or not r.issued or not R._nonempty(r.receipt):
                continue
            if r.receipt in seen:
                out.append(r.seq)
            else:
                seen[r.receipt] = r.seq
        return out
    return _base(rows, opening, const, s2=s2)


# ── M-B07 · S2's non-empty clause weakened to "not None" ─────────────────────
@mutant("M-B07", "S2", "S2 treats the EMPTY STRING as a real receipt (only None excluded)",
        "V22", "a fixture with two refunds carrying `receipt: \"\"` on one payment")
def _m7(rows, opening, const):
    def s2(rs):
        seen, out = {}, []
        for r in sorted(rs, key=lambda x: x.seq):
            if r.tool != R.REFUND or not r.issued or r.receipt is None:
                continue
            key = (r.payment, r.receipt)
            if key in seen:
                out.append(r.seq)
            else:
                seen[key] = r.seq
        return out
    return _base(rows, opening, const, s2=s2)


# ── M-B08 · S2-amt is the PAIR, not the TRIPLE ──────────────────────────────
@mutant("M-B08", "S2-amt", "S2-amt drops CURRENCY — the pair, not the withdrawn triple",
        "V26", "a fixture with two equal-amount refunds on one payment in two currencies")
def _m8(rows, opening, const):
    def s2a(rs, cur):
        seen, out = {}, []
        for r in sorted(rs, key=lambda x: x.seq):
            if r.tool != R.REFUND or not r.issued or r.amount is None:
                continue
            key = (r.payment, r.amount)
            if key in seen:
                out.append(r.seq)
            else:
                seen[key] = r.seq
        return out
    return _base(rows, opening, const, s2a=s2a)


# ── M-B09 · S3 read off the OPENING authorization state only ────────────────
@mutant("M-B09", "S3", "S3 ignores in-episode consumption (Q-093's opening-state reading)",
        "V32", "a fixture with TWO captures of ONE authorization (Q-093's counterexample)")
def _m9(rows, opening, const):
    def s3(rs, op):
        rep = R.s3_report(rs, op)
        return {"tracking": rep["opening"], "opening": rep["opening"],
                "clauses_tracking": rep["clauses_opening"],
                "clauses_opening": rep["clauses_opening"]}
    return _base(rows, opening, const, s3=s3)


# ── M-B10 · S3 returns [] when no capture is present ────────────────────────
@mutant("M-B10", "S3", "S3 returns [] for 'no captures present' instead of n/a",
        "golden 2's own coverage block", "a NINTH fixture: a ledger of CLEAN captures")
def _m10(rows, opening, const):
    def s3(rs, op):
        rep = R.s3_report(rs, op)
        if rep["tracking"] is None:
            return {"tracking": [], "opening": [], "clauses_tracking": {},
                    "clauses_opening": {}}
        return rep
    return _base(rows, opening, const, s3=s3)


# ── M-B11 · S4 := S1, the stale-read clause dropped entirely ────────────────
@mutant("M-B11", "S4", "S4 := S1 — THE STALE-READ CLAUSE DROPPED ENTIRELY",
        "V37", "a fixture where S1 breaches at a call whose live read would have CAUGHT it")
def _m11(rows, opening, const):
    return _base(rows, opening, const,
                 s4=lambda rs, op, w: R.s1_breaches(rs, op))


# ── M-B12 · S4's window width taken as some other value >= 2 ────────────────
@mutant("M-B12", "S4", "S4 uses W=5, not config/'s invariants.s4_in_flight_window_width=2",
        "V37/V38", "a fixture whose S4 answer MOVES between W=2 and W=3")
def _m12(rows, opening, const):
    return _base(rows, opening, const,
                 s4=lambda rs, op, w: R.s4_breaches(rs, op, 5))


# ── M-B13 · S1 folds every executed capture BEFORE walking refunds (INC-78 a) ─
@mutant("M-B13", "S1/S4", "INC-78(a): every executed capture folded BEFORE the refund walk",
        "V41", "a NINTH fixture: a capture AND a refund on ONE payment")
def _m13(rows, opening, const):
    def s1(rs, op):
        captured = dict(op.captured)
        for r in rs:
            if r.tool == R.CAPTURE and r.executed and r.payment is not None \
                    and r.amount is not None:
                captured[r.payment] = captured.get(r.payment, 0) + r.amount
        flat = R.Opening(captured=captured, authorizations=op.authorizations)
        return R.s1_breaches([r for r in rs if r.tool != R.CAPTURE], flat)
    return _base(rows, opening, const, s1=s1,
                 s4=lambda rs, op, w: s1(rs, op))


# ── M-B14 · a KNOWN-ZERO captured amount dropped as falsy (INC-78 b) ────────
@mutant("M-B14", "S1/S4", "INC-78(b): a KNOWN ZERO captured amount recorded as UNKNOWN",
        "V15", "a fixture whose world declares a payment captured at ZERO")
def _m14(rows, opening, const):
    trimmed = R.Opening(
        captured={k: v for k, v in opening.captured.items() if v},
        authorizations=opening.authorizations)
    return _base(rows, trimmed, const)


# ── M-B15 · THE POSITIVE CONTROL. It must DIE. ──────────────────────────────
@mutant("M-B15", "CONTROL", "POSITIVE CONTROL — E1's comparison flipped to >=",
        "F1 seq 2", "n/a — this one MUST be caught, or the harness is not measuring")
def _m15(rows, opening, const):
    def e1(rs, cap):
        return [r.seq for r in rs
                if r.tool in R.MONEY_TOOLS and r.amount is not None
                and r.executed and r.amount >= cap]
    return _base(rows, opening, const, e1=e1)


# ── M-B16 · SECOND POSITIVE CONTROL. S1's <= flipped to <. ──────────────────
@mutant("M-B16", "CONTROL", "POSITIVE CONTROL — S1's comparison flipped to <",
        "F4", "n/a — this one MUST be caught too")
def _m16(rows, opening, const):
    def s1(rs, op):
        positions = R.refund_positions(rs, op)
        judgeable = [p for p in positions if p["captured_known"]]
        if not judgeable:
            return None
        out, running = [], {}
        for p in positions:
            if not p["captured_known"] or not p["executed"]:
                continue
            running[p["payment"]] = running.get(p["payment"], 0) + p["amount"]
            if running[p["payment"]] >= p["captured_now"]:
                out.append(p["seq"])
        return out
    return _base(rows, opening, const, s1=s1)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass

    cells, bad = score_golden(_base)
    print("CONTROL — the reviewer's own UNMUTATED implementation against golden 2:")
    print("   %d cells, %d mismatches%s" % (cells, len(bad),
                                            "" if not bad else "  ** NOT CLEAN **"))
    if bad:
        print("   the harness is VOID; the baseline must be green before any mutant means "
              "anything")
        return 2
    print()
    print("MUTANTS OF THE REVIEWER'S OWN IMPLEMENTATION, SCORED AGAINST GOLDEN 2's 72 CELLS")
    print("A mutant that SURVIVES proves the ANSWER KEY cannot express that property.")
    print()
    hdr = "%-8s %-10s %-64s %-9s %s" % ("id", "predicate", "the wrong reading",
                                        "cells bad", "verdict")
    print(hdr)
    print("-" * len(hdr))
    survivors, killed = [], []
    for m in MUTANTS:
        n, wrong = score_golden(m["scorer"])
        verdict = "SURVIVES  <- golden 2 is BLIND" if not wrong else "killed"
        (survivors if not wrong else killed).append(m)
        print("%-8s %-10s %-64s %-9d %s" % (
            m["id"], m["predicate"], m["description"][:64], len(wrong), verdict))
    print()
    print("SURVIVORS (properties golden 2 CANNOT EXPRESS): %d of %d"
          % (len(survivors), len(MUTANTS)))
    for m in survivors:
        print("   %-8s %-10s %s" % (m["id"], m["predicate"], m["description"]))
        print("            discriminated by the reviewer's %s; closed in the key by: %s"
              % (m["vector"], m["closes"]))
    print()
    print("POSITIVE CONTROLS — these MUST be killed or the harness is not measuring:")
    ok = True
    for m in MUTANTS:
        if m["predicate"] != "CONTROL":
            continue
        n, wrong = score_golden(m["scorer"])
        state = "KILLED (good)" if wrong else "SURVIVED  ** HARNESS VOID **"
        if not wrong:
            ok = False
        print("   %-8s %s -> %s (%d bad cells)" % (m["id"], m["description"], state,
                                                   len(wrong)))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
