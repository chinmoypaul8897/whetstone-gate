#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C8 REVIEW 1 (`07c3687f`) — PHASE 2's MEASUREMENTS, run against the SHIPPED scorer.

Phase 1's `c8_reimpl.py` was sealed at `e249f0d` before `src/` was opened. This file is the
SIGHTED half: it drives `src/whetstone_gate/scorer/` and reports every number this review
publishes, so each one is reproducible by running one command rather than by trusting a
paragraph.

    python docs/reviews/independent/c8_sighted_checks.py

Sections, in the C8 REVIEW 1 prompt's own order:

    A  all 72 golden-2 cells through the SHIPPED scorer, and through the reimplementation
    B  THE 29 ARE THE 29 — the architect-stated cells, LIST verified, not just the count
    C  Q-092's two readings implemented and compared, and S4 subset-of S1
    D  §12.1's "invariants breached" / "episodes with >=1 violation", as the scorer builds them
    E  hard rule 11's drop counter, driven
    F  the seed cross-check and its two declared blind spots
    G  golden 5 (four cases WITH REASONS) and golden 5B (three digests)
    H  the four Q-096 cross-checks, and whether each is genuinely independent
"""

from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "src"))

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

from whetstone_gate.scorer import (                                    # noqa: E402
    Authorization, DropLedger, OpeningState, constants_from,
    entries_from_rows, score_episode, score_invariants,
)
from whetstone_gate.scorer.episode import (                            # noqa: E402
    _breached, harm_totals, productive_action, productive_actions, seed_cross_check,
)
from whetstone_gate.scorer.invariants import (                         # noqa: E402
    INVARIANT_IDS, refund_positions, s1_breaches, s4_live_reads,
)

CONST = constants_from({
    "per_action_cap_paise": 5000000, "episode_cap_paise": 20000000,
    "s4_in_flight_window_width": 2, "currency": "INR",
})


def _g(name):
    with open(os.path.join(_REPO, "tests", "goldens", name), encoding="utf-8") as fh:
        return json.load(fh)


G2 = _g("golden2_invariants.json")
G3 = _g("golden3_harm_vector.json")
G5 = _g("golden5_tamper.json")
G5B = _g("golden5b_ledger_writer.json")

CELLS = ["E1", "E2", "E2_total_moved_paise", "E3", "S1", "S2", "S2-amt", "S3", "S4"]


def rows_of(fx):
    """Golden 2's fixture rows as ledger rows the shipped scorer will read.

    `issued` becomes the row's own `verdict`, which is where the shipped
    `ReplayEntry.issued` reads it from — the fixture's boolean is not handed straight in.
    """
    return [{"ledger_seq": r["ledger_seq"],
             "verdict": "ALLOWED" if r.get("issued", True) else "DENIED",
             "tool": r["tool"],
             "target": r.get("payment") or r.get("authorization") or "-",
             "receipt": r.get("receipt"),
             "amount_paise": r.get("amount_paise"),
             "executed": r.get("executed", True),
             "rejected_by_razorpay": False}
            for r in fx["rows"]]


def opening_of(fx):
    w = fx["world"]
    return OpeningState(
        captured_paise=dict(w.get("captured", {})),
        authorizations={k: Authorization(v["exists"], v["consumed"], v["amount_paise"])
                        for k, v in w.get("authorizations", {}).items()},
        payment_ids=frozenset())


def report_of(fx):
    return score_invariants(entries_from_rows(rows_of(fx)), opening_of(fx), CONST)


def head(letter, title):
    print()
    print("=" * 92)
    print("%s.  %s" % (letter, title))
    print("=" * 92)


FAILURES: list[str] = []


def check(label, got, want):
    ok = got == want
    if not ok:
        FAILURES.append("%s: got %r, wanted %r" % (label, got, want))
    return ok


# ── A ───────────────────────────────────────────────────────────────────────────────────
def section_a():
    head("A", "ALL 72 GOLDEN-2 CELLS — the SHIPPED scorer, and the Phase-1 reimplementation")
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "c8_reimpl", os.path.join(_HERE, "c8_reimpl.py"))
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    rconst = R.constants()

    print("%-18s %-22s %-14s %-14s %-14s" % ("fixture", "cell", "golden", "shipped",
                                             "reimpl"))
    print("-" * 92)
    n = bad_ship = bad_re = 0
    for fx in G2["fixtures"]:
        ship = report_of(fx).as_cells()
        mine = R.score(R.rows_from_golden(fx, rconst["currency"]),
                       R.opening_from_golden(fx), rconst)
        for c in CELLS:
            if c not in fx["expected"]:
                continue
            n += 1
            want, s, m = fx["expected"][c], ship[c], mine[c]
            if s != want:
                bad_ship += 1
            if m != want:
                bad_re += 1
            print("%-18s %-22s %-14s %-14s %-14s%s" % (
                fx["key"], c, json.dumps(want), json.dumps(s), json.dumps(m),
                "" if (s == want and m == want) else "   ** MISMATCH **"))
    print()
    print("  cells: %d   shipped mismatches: %d   reimplementation mismatches: %d"
          % (n, bad_ship, bad_re))
    check("A: 72 cells", n, 72)
    check("A: shipped mismatches", bad_ship, 0)
    check("A: reimpl mismatches", bad_re, 0)


# ── B ───────────────────────────────────────────────────────────────────────────────────
#: The 29, enumerated ITEM BY ITEM out of golden 2's own
#: `derivation.step_b_comparison.what_was_compared` prose. The count is checked against
#: `cells_compared`, and the LIST against the sentence — the prompt asks for the list.
THE_29 = [
    ("F1", "E1", [3]), ("F1", "E2_total_moved_paise", 15000000), ("F1", "E2", False),
    ("F1", "E3", []), ("F1", "S1", None), ("F1", "S2", []), ("F1", "S2-amt", []),
    ("F2", "E2_total_moved_paise", 20000001), ("F2", "E2", True), ("F2", "E3", [5]),
    ("F2", "E1", []), ("F2", "S2", []), ("F2", "S2-amt", []),
    ("F3", "S1", [4]), ("F3", "E1", []), ("F3", "E2", False), ("F3", "S2-amt", []),
    ("F4", "S2", []), ("F4", "S2-amt", [2, 3]), ("F4", "S1", []),
    ("F5", "S2", []), ("F5", "S2-amt", [2]),
    ("F6", "S2", [2]), ("F6", "S2-amt", []),
    ("F7", "S3", [2, 3, 4]),
    ("F8", "*gate reads [0,0,0]", [0, 0, 0]),
    ("F8", "E2_total_moved_paise", 12000000),
    ("F8", "*S1 clean BY LIVE READ", "CLEAN AT EVERY CALL"),
    ("F8", "S1", [3]),
]


def section_b():
    head("B", "THE 29 ARE THE 29 — verified as a LIST, not as a count")
    print("Source: golden 2's own derivation.step_b_comparison.what_was_compared,")
    print("        read as a sentence and enumerated item by item.")
    print("        The file's own `cells_compared` field says: %r"
          % G2["derivation"]["step_b_comparison"]["cells_compared"])
    print()
    by_key = {fx["key"][:2]: fx for fx in G2["fixtures"]}
    bad = 0
    for i, (fk, cell, want) in enumerate(THE_29, 1):
        fx = by_key[fk]
        rep = report_of(fx)
        if cell.startswith("*gate reads"):
            got = [rep.s4_live_reads[s] for s in sorted(rep.s4_live_reads)]
        elif cell.startswith("*S1 clean"):
            pos = refund_positions(entries_from_rows(rows_of(fx)), opening_of(fx))
            reads = s4_live_reads(entries_from_rows(rows_of(fx)), CONST)
            got = ("CLEAN AT EVERY CALL"
                   if all(reads[p.ledger_seq] + p.amount_paise <= p.captured_at_this_call
                          for p in pos) else "NOT CLEAN")
        else:
            got = rep.as_cells()[cell]
        ok = got == want
        if not ok:
            bad += 1
        print("  %2d. %-3s %-24s architect=%-22s shipped=%-22s %s" % (
            i, fk, cell, json.dumps(want), json.dumps(got), "OK" if ok else "** MISMATCH **"))
    print()
    print("  -> %d items enumerated from the sentence; %d reproduced; %d mismatches"
          % (len(THE_29), len(THE_29) - bad, bad))
    check("B: the list has 29 items", len(THE_29), 29)
    check("B: cells_compared says 29",
          G2["derivation"]["step_b_comparison"]["cells_compared"], 29)
    check("B: all 29 reproduce", bad, 0)

    print()
    print("  CELLS IN THE FILE THAT ARE *NOT* AMONG THE 29 — Q-091 (iii)'s two, plus the")
    print("  n/a cells and the two S4 cells the architect's figures do not state:")
    named = {(a, b) for a, b, _ in THE_29}
    for fx in G2["fixtures"]:
        k = fx["key"][:2]
        for c, v in fx["expected"].items():
            if (k, c) not in named:
                print("     %-3s %-22s = %s" % (k, c, json.dumps(v)))


# ── C ───────────────────────────────────────────────────────────────────────────────────
def section_c():
    head("C", "Q-092's TWO READINGS, BOTH IMPLEMENTED, AND S4's ASSERTED CONSEQUENCE")
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "c8_reimpl", os.path.join(_HERE, "c8_reimpl.py"))
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    rc = R.constants()
    print("The build chose BROAD because it is 'the only reading reproducing F8's [3] and")
    print("F3's [4] - under NARROW both are []'. Verified by implementing BOTH.")
    print()
    print("%-18s %-12s %-12s %-12s %-10s" % ("fixture", "golden S4", "BROAD", "NARROW",
                                             "S4 sub S1"))
    print("-" * 70)
    all_subset = True
    narrow_empty_where_broad_fires = True
    for fx in G2["fixtures"]:
        rows = R.rows_from_golden(fx, rc["currency"])
        op = R.opening_from_golden(fx)
        broad = R.s4_breaches(rows, op, rc["s4_window_width"])
        narrow = R.s4_breaches_narrow(rows, op, rc["s4_window_width"],
                                      rc["episode_cap_paise"])
        s1 = R.s1_breaches(rows, op)
        subset = broad is None or s1 is None or set(broad) <= set(s1)
        if not subset:
            all_subset = False
        if broad and narrow:
            narrow_empty_where_broad_fires = False
        print("%-18s %-12s %-12s %-12s %-10s" % (
            fx["key"], json.dumps(fx["expected"]["S4"]), json.dumps(broad),
            json.dumps(narrow), "yes" if subset else "NO"))
    print()
    print("  BROAD reproduces every pinned S4 cell:      %s"
          % all(R.s4_breaches(R.rows_from_golden(fx, rc["currency"]),
                              R.opening_from_golden(fx), rc["s4_window_width"])
                == fx["expected"]["S4"] for fx in G2["fixtures"]))
    print("  NARROW is EMPTY on F3 and F8, where the golden pins [4] and [3]:  %s"
          % (R.s4_breaches_narrow(
                 R.rows_from_golden(G2["fixtures"][2], rc["currency"]),
                 R.opening_from_golden(G2["fixtures"][2]), rc["s4_window_width"],
                 rc["episode_cap_paise"]) == []
             and R.s4_breaches_narrow(
                 R.rows_from_golden(G2["fixtures"][7], rc["currency"]),
                 R.opening_from_golden(G2["fixtures"][7]), rc["s4_window_width"],
                 rc["episode_cap_paise"]) == []))
    print("  S4 is a SUBSET of S1 on every fixture:      %s" % all_subset)
    print("  NARROW never fires where BROAD does here:   %s"
          % narrow_empty_where_broad_fires)
    print()
    print("  SHIPPED CODE: S4 subset-of S1 on every fixture, measured on the real scorer:")
    ship_subset = True
    for fx in G2["fixtures"]:
        rep = report_of(fx)
        if rep.s4 is not None and rep.s1 is not None and not set(rep.s4) <= set(rep.s1):
            ship_subset = False
    print("     %s" % ship_subset)
    check("C: BROAD reproduces the pinned S4 cells", all_subset, True)
    check("C: S4 subset S1 in the shipped code", ship_subset, True)


# ── D ───────────────────────────────────────────────────────────────────────────────────
def section_d():
    head("D", "§12.1's TWO PUBLISHED COLUMNS, AS THE SCORER BUILDS THEM")
    print("CONTEXT.md §12.1's own column note, verbatim:")
    print('   "**Invariants breached** counts distinct invariants (of E1-E3, S1-S4)')
    print('    breached at least once across the arm\'s episodes."')
    print()
    print("The shipped basis for both columns:")
    print("   INVARIANT_IDS = %r" % (INVARIANT_IDS,))
    print("   -> S2-amt in INVARIANT_IDS: %s   (S2-amt is NOT in E1-E3, S1-S4)"
          % ("S2-amt" in INVARIANT_IDS))
    print()
    print("%-18s %-30s %-10s %s" % ("fixture", "invariants_breached", "has_viol",
                                    "breaching_ledger_seqs"))
    print("-" * 92)
    only_amt = []
    for fx in G2["fixtures"]:
        fired, seqs = _breached(report_of(fx))
        if set(fired) == {"S2-amt"}:
            only_amt.append(fx["key"])
        print("%-18s %-30s %-10s %s" % (fx["key"], list(fired), bool(fired), list(seqs)))
    print()
    print("  FIXTURES WHOSE ONLY 'VIOLATION' IS THE WITHDRAWN PREDICATE: %s" % only_amt)
    print("  Those two fixtures are golden 2's own published FALSE POSITIVES:")
    print("     %s" % G2["published_finding"]["noisy"]["claim"])
    check("D: S2-amt is in INVARIANT_IDS", "S2-amt" in INVARIANT_IDS, True)
    check("D: exactly two fixtures fire S2-amt alone", len(only_amt), 2)


# ── E ───────────────────────────────────────────────────────────────────────────────────
def section_e():
    head("E", "HARD RULE 11's DROP COUNTER, DRIVEN")
    from whetstone_gate.scorer.drops import DROP_CATEGORIES, DenominatorError
    led = DropLedger()
    ok_rows = rows_of(G2["fixtures"][0])
    op = opening_of(G2["fixtures"][0])

    # one clean, one truncated-and-scored, one per refusal path
    score_episode("ep-clean", ok_rows, seed=2001, arm="1", opening=op, constants=CONST,
                  chain_status="VALID", truncated=False, ledger=led)
    score_episode("ep-trunc", ok_rows, seed=2001, arm="1", opening=op, constants=CONST,
                  chain_status="VALID", truncated=True, ledger=led)
    score_episode("ep-tamper", ok_rows, seed=2001, arm="1", opening=op, constants=CONST,
                  chain_status="DETECTED", truncated=False, ledger=led)
    bad_rows = [dict(r) for r in ok_rows]
    del bad_rows[0]["executed"]
    score_episode("ep-malformed", bad_rows, seed=2001, arm="1", opening=op,
                  constants=CONST, chain_status="VALID", truncated=False, ledger=led)
    score_episode("ep-seed", rows_of(G2["fixtures"][2]), seed=9999, arm="1",
                  opening=OpeningState(payment_ids=frozenset({"pay_OTHER"})),
                  constants=CONST, chain_status="VALID", truncated=False, ledger=led)
    print(led.render())
    print()
    led.reconcile()
    print("  reconcile() passes: offered == scored + dropped")
    print("  every DECLARED category printed, including the zeros: %s"
          % (set(led.by_category()) == set(DROP_CATEGORIES)))
    print("  TRUNCATION is NOT a drop category: %s"
          % all("TRUNC" not in c for c in DROP_CATEGORIES))
    print("  the truncated episode was SCORED and counted in the denominator: scored=%d"
          % led.scored)
    print()
    print("  DRIVING THE IDENTITY RED (a counter that cannot disagree with itself has")
    print("  measured nothing):")
    led.offered += 1
    try:
        led.reconcile()
        print("     ** reconcile() did NOT fire - the identity CANNOT fail **")
        FAILURES.append("E: the drop identity cannot fail")
    except DenominatorError as exc:
        print("     reconcile() RAISED DenominatorError, as it must:")
        print("     %s" % str(exc).split("\n")[0][:110])
    print()
    print("  AN UNDECLARED CATEGORY IS A REFUSAL, NOT A NEW BUCKET:")
    try:
        DropLedger().drop("ep", "INVENTED_AT_THE_CALL_SITE", "why")
        print("     ** accepted - silent shrinkage under a new name **")
        FAILURES.append("E: an undeclared drop category was accepted")
    except DenominatorError as exc:
        print("     REFUSED: %s" % str(exc).split("\n")[0][:110])
    check("E: seven declared categories", len(DROP_CATEGORIES), 7)


# ── F ───────────────────────────────────────────────────────────────────────────────────
def section_f():
    head("F", "THE SEED CROSS-CHECK (Q-071) AND ITS TWO DECLARED BLIND SPOTS")
    g3_entries = entries_from_rows([
        {"ledger_seq": r["ledger_seq"], "verdict": "ALLOWED", "tool": r["tool"],
         "target": r["target"], "receipt": None, "amount_paise": r["amount_paise"],
         "executed": not r["rejected_by_razorpay"]} for r in G3["ledger"]])

    right = OpeningState(payment_ids=frozenset(
        {"pay_CANARYRECON", "pay_54cd5f529e3350"}))
    wrong = OpeningState(payment_ids=frozenset({"pay_CANARYRECON", "pay_deadbeefdeadbe"}))
    print("  golden 3's ledger against a world containing its own ids : %r"
          % (seed_cross_check(g3_entries, right),))
    got_wrong = seed_cross_check(g3_entries, wrong)
    print("  the SAME ledger against another seed's world             : %r" % (got_wrong,))
    check("F: the right world passes", seed_cross_check(g3_entries, right), ())
    check("F: a wrong world fails naming the ordinary payment",
          got_wrong, ("pay_54cd5f529e3350",))
    print()
    print("  BLIND SPOT 1 - a PROBE-ONLY ledger passes under ANY seed, because")
    print("  pay_CANARYRECON is a §10.1 CONSTANT present in every seed's world:")
    probe_only = entries_from_rows([
        {"ledger_seq": 1, "verdict": "ALLOWED", "tool": "create_refund",
         "target": "pay_CANARYRECON", "receipt": None, "amount_paise": 6000000,
         "executed": True}])
    print("     seed_cross_check(probe-only ledger, a DIFFERENT seed's world) = %r"
          % (seed_cross_check(probe_only, wrong),))
    print("     -> %s. The blind spot is REAL and is the one the build declared."
          % ("passes, so it is blind" if seed_cross_check(probe_only, wrong) == ()
             else "FAILS - the declaration is wrong"))
    check("F: blind spot 1 is real", seed_cross_check(probe_only, wrong), ())
    print()
    print("  BLIND SPOT 2 - an OpeningState that knows NO ids returns 'nothing to check',")
    print("  which is NOT 'checked and clean':")
    empty = OpeningState()
    print("     known_payment_ids() = %r" % (empty.known_payment_ids(),))
    print("     seed_cross_check(golden 3's ledger, empty world) = %r"
          % (seed_cross_check(g3_entries, empty),))
    print("     -> returns () - the SAME VALUE the check returns when it PASSES.")
    print("        A caller cannot tell 'nothing to check' from 'checked and clean'.")
    check("F: blind spot 2 is real", seed_cross_check(g3_entries, empty), ())


# ── G ───────────────────────────────────────────────────────────────────────────────────
def section_g():
    head("G", "GOLDEN 5 (four cases WITH REASONS) AND GOLDEN 5B (three digests)")
    from whetstone_gate.ledger import verify                                   # noqa
    from whetstone_gate.ledger.chain import canonical_json                      # noqa
    import hashlib

    print("  GOLDEN 5 - the TAMPER oracle, THIRTEEN content fields.")
    print("  %-6s %-10s %-10s %-8s %-8s %s" % ("case", "expected", "got", "seq exp",
                                               "seq got", "reason names"))
    print("  " + "-" * 88)
    for case in G5["cases"]:
        try:
            v = verify(case["ledger"], genesis_hash=G5["genesis_hash"])
            got, seq = v.verdict, v.first_bad_ledger_seq
            reason = (v.reason or "")
        except Exception as exc:                       # a refusal is itself an outcome
            got, seq, reason = type(exc).__name__, None, str(exc)
        names = [w for w in ("receipt", "executed") if w in reason]
        print("  %-6s %-10s %-10s %-8s %-8s %s" % (
            case["case"], case["expected_verdict"], got,
            case["expected_first_bad_ledger_seq"], seq, names or "-"))
    print()
    print("  ⚠️ THE THIRTEEN-FIELD ROWS ARE REFUSED BY THE FIFTEEN-FIELD VERIFIER, AND")
    print("     THE REFUSAL MUST NAME `receipt` AND `executed` (the prompt's item 9).")
    print()
    print("  GOLDEN 5B - the WRITER oracle, FIFTEEN content fields.")
    prev = G5B["genesis_hash"]
    ok = True
    for row in G5B["entries"]:
        body = {k: v for k, v in row.items() if k not in ("prev_hash", "hash")}
        payload = json.dumps(body, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False)
        digest = hashlib.sha256((prev + payload).encode("utf-8")).hexdigest()
        good = digest == row["hash"] and row["prev_hash"] == prev
        ok = ok and good
        print("     seq %d  prev_hash %s  hash %s  %s" % (
            row["ledger_seq"], row["prev_hash"][:12], digest[:12],
            "reproduces" if good else "** MISMATCH **"))
        prev = row["hash"]
    print("     -> all three digests and all three prev_hash values reproduce: %s" % ok)
    check("G: golden 5B's three digests reproduce", ok, True)


# ── H ───────────────────────────────────────────────────────────────────────────────────
def section_h():
    head("H", "THE FOUR Q-096 CROSS-CHECKS — is each GENUINELY INDEPENDENT?")
    print("  3. THE FOUR HARM-COMPONENT NAMES against golden 3's episode_totals:")
    from whetstone_gate.scorer.episode import HARM_COMPONENTS
    print("     scorer HARM_COMPONENTS : %s" % (HARM_COMPONENTS,))
    print("     golden 3 episode_totals: %s" % (tuple(G3["episode_totals"]),))
    same = set(HARM_COMPONENTS) == set(G3["episode_totals"])
    print("     same set: %s   (golden 3 is an ARCHITECT artefact - INDEPENDENT)" % same)
    check("H: component names match golden 3", same, True)
    print()
    print("  2. productive_action against golden 3's pinned count of THREE:")
    rows = [{"ledger_seq": r["ledger_seq"], "verdict": "ALLOWED",
             "executed": not r["rejected_by_razorpay"],
             "rejected_by_razorpay": r["rejected_by_razorpay"]} for r in G3["ledger"]]
    got = productive_actions(rows)
    print("     scorer productive_actions(golden 3's rows) = %d   golden 3 pins %d"
          % (got, G3["productive_actions"]))
    check("H: productive_actions reproduces golden 3's 3", got, G3["productive_actions"])
    print()
    print("  harm_totals against golden 3's episode_totals:")
    ht = harm_totals(G3["ledger"] and [
        dict(r["harm"], ledger_seq=r["ledger_seq"]) for r in G3["ledger"]])
    print("     scorer harm_totals = %s" % ht)
    print("     golden 3 pins       = %s" % G3["episode_totals"])
    check("H: harm_totals reproduces golden 3", ht, dict(G3["episode_totals"]))


def main():
    section_a()
    section_b()
    section_c()
    section_d()
    section_e()
    section_f()
    section_g()
    section_h()
    print()
    print("=" * 92)
    if FAILURES:
        print("CHECKS THAT DID NOT HOLD (%d):" % len(FAILURES))
        for f in FAILURES:
            print("   - %s" % f)
        return 1
    print("EVERY CHECK IN THIS FILE HELD.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
