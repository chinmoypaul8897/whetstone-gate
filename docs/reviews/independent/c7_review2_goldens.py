"""C7 REVIEW 2 - the three goldens, each by THIS REVIEWER'S OWN COMPUTATION.

SESSION-TOKEN: b8c31a57. Imports the sealed reimplementation and NOTHING from ``src/``.

Order is not decorative and is the architect's own (``golden5b`` ``derivation.control``):

  1. THE CONTROL, FIRST.  Reproduce golden 5 case A's THIRTEEN-field digests from a rule
     this session wrote itself.  A rule that cannot reproduce the fixture it is derived
     from is a wrong rule and every value it then produces is worthless.  A failing
     control is a STOP.
  2. GOLDEN 5 - all four cases, VERDICT, FIRST-BAD SEQ and REASON, plus the
     discrimination set computed rather than asserted.
  3. GOLDEN 3's ``executed`` DERIVED BY SEARCH, NOT BY CONFIRMATION - the 32-way and the
     1024-way enumerations reproduced independently, plus the SECOND ROUTE that never
     reads ``productive_actions``.
  4. GOLDEN 5B - the three FIFTEEN-field digests, recomputed and compared.
  5. GOLDEN 3's ``productive_actions``, term by term, from S8.6a PARSED OUT OF CONTEXT.md.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))

import c7_review2_reimpl as R  # noqa: E402

GOLDENS = REPO / "tests" / "goldens"
FAILURES = []


def check(label, obtained, expected):
    ok = obtained == expected
    print("  %-58s %s" % (label, "OK" if ok else "MISMATCH"))
    if not ok:
        print("      obtained: %r" % (obtained,))
        print("      expected: %r" % (expected,))
        FAILURES.append(label)
    return ok


def load(name):
    return json.loads((GOLDENS / name).read_text(encoding="utf-8"))


g5 = load("golden5_tamper.json")
g5b = load("golden5b_ledger_writer.json")
g3 = load("golden3_harm_vector.json")

print("=" * 78)
print("PROVENANCE")
print("=" * 78)
print("  reimplementation  %s" % (R.__file__,))
print("  goldens directory %s" % (GOLDENS,))
print("  project modules imported: NONE (asserted by ast in the reimplementation)")
print("  'whetstone_gate' in sys.modules: %s"
      % any(m.split(".")[0] == "whetstone_gate" for m in sys.modules))

# ---------------------------------------------------------------------------
# 1. THE CONTROL - golden 5 case A's THIRTEEN-field digests
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("1. THE CONTROL, RUN FIRST - golden 5 case A at THIRTEEN fields")
print("=" * 78)

case_a = [c for c in g5["cases"] if c["case"] == "A"][0]
prev = g5["genesis_hash"]
control_digests = []
for row in case_a["ledger"]:
    body = {k: v for k, v in row.items() if k not in ("prev_hash", "hash")}
    assert tuple(sorted(body)) == tuple(sorted(R.SCHEMA_13)), sorted(body)
    d = R.digest(prev, body)
    control_digests.append(d)
    print("  seq %d  link stored=%s  recomputed_from_contents=%s"
          % (row["ledger_seq"], row["prev_hash"] == prev, d == row["hash"]))
    check("seq %d digest" % row["ledger_seq"], d, row["hash"])
    prev = d

print()
print("  THE EXACT BYTES HASHED AFTER THE 'PRE-FREEZE' PREFIX, ENTRY 1:")
print("  " + R.canonical_json(
    {k: v for k, v in case_a["ledger"][0].items() if k not in ("prev_hash", "hash")}))
CONTROL_PASSED = not FAILURES
print()
print("  CONTROL: %s" % ("PASS" if CONTROL_PASSED else "FAIL - STOP"))
if not CONTROL_PASSED:
    raise SystemExit("CONTROL FAILED - the rule is wrong and every value below is worthless")

# ---------------------------------------------------------------------------
# 2. GOLDEN 5 - four cases, verdict, first-bad seq AND reason
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("2. GOLDEN 5 - four cases: VERDICT, FIRST-BAD SEQ, REASON")
print("=" * 78)

disagree = []
marked = []
for case in g5["cases"]:
    verdict, seq, reason = R.verify(case["ledger"], g5["genesis_hash"])
    sverdict, sseq, sreason = R.verify_stored_field_only(case["ledger"], g5["genesis_hash"])
    print("  case %s  recomputing=%-9s seq=%-4s reason=%-45s stored-field=%s"
          % (case["case"], verdict, seq, reason, sverdict))
    check("case %s verdict" % case["case"], verdict, case["expected_verdict"])
    check("case %s first-bad seq" % case["case"], seq, case["expected_first_bad_ledger_seq"])
    check("case %s stored-field verifier" % case["case"],
          sverdict, case["stored_field_verifier_returns"])
    if verdict != sverdict:
        disagree.append(case["case"])
    if case["discriminates_the_seeded_defect"]:
        marked.append(case["case"])

print()
check("the DISCRIMINATION set, computed vs the golden's own marking", disagree, marked)

print()
print("  CASE D, THE LOAD-BEARING ONE - the REASON, not only the verdict:")
case_d = [c for c in g5["cases"] if c["case"] == "D"][0]
e1 = case_d["ledger"][0]
body1 = {k: v for k, v in e1.items() if k not in ("prev_hash", "hash")}
recomputed1 = R.digest(e1["prev_hash"], body1)
print("    entry 1 stored hash        %s" % e1["hash"])
print("    entry 1 RECOMPUTED digest  %s" % recomputed1)
print("    they differ                                              %s" % (recomputed1 != e1["hash"]))
print("    entry 1's link to genesis still holds                    %s"
      % (e1["prev_hash"] == g5["genesis_hash"]))
print("    entry 2's stored prev_hash == entry 1's STORED hash      %s"
      % (case_d["ledger"][1]["prev_hash"] == e1["hash"]))

# ---------------------------------------------------------------------------
# 3. GOLDEN 3's `executed`, DERIVED BY SEARCH
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("3. GOLDEN 3's `executed` - DERIVED BY SEARCH, NOT BY CONFIRMATION")
print("=" * 78)

rows3 = g3["ledger"]
PINNED_PRODUCTIVE = g3["productive_actions"]
PINNED_CANARY_A = g3["probe"]["canary_a_breach"]
PINNED_CANARY_B = g3["probe"]["canary_b_reach"]
print("  golden 3 pins: productive_actions=%d  canary_a_breach=%d  canary_b_reach=%d"
      % (PINNED_PRODUCTIVE, PINNED_CANARY_A, PINNED_CANARY_B))


def scored(assignment_exec, assignment_verdict):
    """Score one candidate assignment against BOTH pinned counts, using only
    S8.6a's and S10.1's own predicates out of the reimplementation."""
    prod = 0
    canary_a = 0
    for row, ex, vd in zip(rows3, assignment_exec, assignment_verdict):
        entry = {
            "verdict": vd,
            "executed": ex,
            "rejected_by_razorpay": row["rejected_by_razorpay"],
            "target": row["target"],
            "tool": row["tool"],
            "amount_paise": row["amount_paise"],
        }
        prod += 1 if R.productive_action(entry) else 0
        canary_a += 1 if R.canary_a_breach(entry) else 0
    return prod, canary_a


def forced(satisfying):
    """Which positions take the same value in EVERY satisfying assignment."""
    out = {}
    for i in range(5):
        vals = {a[i] for a in satisfying}
        out[i + 1] = next(iter(vals)) if len(vals) == 1 else "FREE"
    return out


# --- SEARCH A: all 32 assignments of `executed`, verdicts assumed ALLOWED ---
satisfying_a = []
for combo in itertools.product([False, True], repeat=5):
    p, c = scored(combo, ["ALLOWED"] * 5)
    if p == PINNED_PRODUCTIVE and c == PINNED_CANARY_A:
        satisfying_a.append(combo)
print()
print("  SEARCH A - all 2^5 = 32 assignments of `executed` (verdicts assumed ALLOWED)")
print("    satisfying assignments: %d of 32" % len(satisfying_a))
for a in satisfying_a:
    print("      %s" % (dict(zip([1, 2, 3, 4, 5], a)),))
fa = forced(satisfying_a)
print("    FORCED per seq: %s" % (fa,))

# --- SEARCH B: all 1024 assignments of `executed` AND verdict together ---
satisfying_b = []
for combo in itertools.product([False, True], repeat=5):
    for vds in itertools.product(["ALLOWED", "DENIED"], repeat=5):
        p, c = scored(combo, vds)
        if p == PINNED_PRODUCTIVE and c == PINNED_CANARY_A:
            satisfying_b.append((combo, vds))
print()
print("  SEARCH B - all 2^5 x 2^5 = 1024 assignments of `executed` AND the gate verdict")
print("    satisfying assignments: %d of 1024" % len(satisfying_b))
fb = forced([c for c, _ in satisfying_b])
print("    FORCED per seq (executed): %s" % (fb,))
vb = {}
for i in range(5):
    vals = {v[i] for _, v in satisfying_b}
    vb[i + 1] = next(iter(vals)) if len(vals) == 1 else "FREE"
print("    FORCED per seq (verdict):  %s" % (vb,))

check("SEARCH A forces seqs 1-4 and leaves seq 5 free",
      fa, {1: True, 2: False, 3: True, 4: True, 5: "FREE"})
check("SEARCH B forces the same four",
      fb, {1: True, 2: False, 3: True, 4: True, 5: "FREE"})

# --- THE SECOND ROUTE: CANARY-A alone, never reading productive_actions ---
print()
print("  THE SECOND ROUTE - S10.1's CANARY-A ONLY, `productive_actions` NEVER READ")
qualify = []
for row in rows3:
    on_probe = row["target"] == R.PROBE_PAYMENT_ID
    right_tool = row["tool"] in ("create_refund", "capture_payment")
    over_cap = isinstance(row["amount_paise"], int) and row["amount_paise"] > R.PER_ACTION_CAP_PAISE
    if on_probe and right_tool and over_cap:
        qualify.append(row["ledger_seq"])
    print("    seq %d  on-probe=%-5s tool-qualifies=%-5s amount=%-9s over-cap=%-5s razorpay-rejected=%s"
          % (row["ledger_seq"], on_probe, right_tool, row["amount_paise"], over_cap,
             row["rejected_by_razorpay"]))
print("    rows qualifying ON AMOUNT: %s" % (qualify,))
rejected_of = {r["ledger_seq"]: r["rejected_by_razorpay"] for r in rows3}
remaining = [s for s in qualify if not rejected_of[s]]
print("    of those, NOT Razorpay-rejected (so capable of being executed): %s" % (remaining,))
print("    canary_a_breach pinned at %d, so those %d row(s) are FORCED executed"
      % (PINNED_CANARY_A, PINNED_CANARY_A))
check("the second route forces exactly seq 3", remaining, [3])
check("golden 3's own canary_a_note names seq 3 as executed",
      "seq 3: executed on the probe" in g3["probe"]["canary_a_note"], True)

# --- seq 5, settled by C7's consistency assertion 2 ---
print()
print("  SEQ 5 - free under both searches, settled by C7's CONSISTENCY ASSERTION 2")
print("    seq 5 rejected_by_razorpay = %s  ->  a Razorpay-refused call is one the world"
      % (rows3[4]["rejected_by_razorpay"],))
print("    did not perform, so executed=False.  It is OUTSIDE golden 5B's three rows and")
print("    changes nothing there.")
check("seq 5 is Razorpay-rejected", rows3[4]["rejected_by_razorpay"], True)

EXECUTED_G3 = {1: True, 2: False, 3: True, 4: True, 5: False}
print("    THIS REVIEWER'S DERIVED VECTOR: %s" % (EXECUTED_G3,))

# --- corroboration that does not enter the derivation ---
print()
print("  CORROBORATION (not used in the derivation above):")
print("    seq 1 carries non-zero harm (float %d, fees %d), and C7's consistency"
      % (rows3[0]["harm"]["merchant_float_moved_paise"],
         rows3[0]["harm"]["fees_incurred_paise"]))
print("    assertion 3 makes a non-zero component impossible on a call that did not happen.")

# ---------------------------------------------------------------------------
# 4. GOLDEN 5B - the three FIFTEEN-field digests
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("4. GOLDEN 5B - the WRITER oracle at FIFTEEN fields")
print("=" * 78)

check("golden 5B's pinned field_order == this reviewer's sealed SCHEMA_15",
      tuple(g5b["field_order"]), R.SCHEMA_15)

prev = g5b["genesis_hash"]
mine = []
for row in g5b["entries"]:
    body = {k: v for k, v in row.items() if k not in ("prev_hash", "hash")}
    check("seq %d prev_hash linkage" % row["ledger_seq"], row["prev_hash"], prev)
    d = R.digest(prev, body)
    mine.append(d)
    print("  seq %d  reviewer=%s" % (row["ledger_seq"], d))
    print("         file    =%s" % row["hash"])
    check("seq %d FIFTEEN-field digest" % row["ledger_seq"], d, row["hash"])
    prev = row["hash"]

print()
print("  THE `executed` COLUMN THE FILE STORES vs THIS REVIEWER'S DERIVED VECTOR:")
for row in g5b["entries"]:
    s = row["ledger_seq"]
    print("    seq %d  file=%-5s  derived-by-search=%-5s  agree=%s"
          % (s, row["executed"], EXECUTED_G3[s], row["executed"] == EXECUTED_G3[s]))
    check("seq %d executed agrees with the search" % s, row["executed"], EXECUTED_G3[s])

print()
print("  THE SUPERSEDED VALUE, RECOMPUTED - what seq 3's digest WOULD be at executed=false:")
row3 = dict(g5b["entries"][2])
body3 = {k: v for k, v in row3.items() if k not in ("prev_hash", "hash")}
body3_false = dict(body3, executed=False)
d_false = R.digest(row3["prev_hash"], body3_false)
print("    executed=false -> %s" % d_false)
print("    the correction block names   6ae5bd20f67283c0ad70811be2a17cba1a87460f13f78046c4b6f2af946ff76f")
check("the superseded digest reproduces from executed=false",
      d_false, "6ae5bd20f67283c0ad70811be2a17cba1a87460f13f78046c4b6f2af946ff76f")
check("seqs 1 and 2 are unchanged from REVIEW 1's own reproduction",
      mine[:2], ["186a2118ba239d24936e48a485c33b099d97bb0daa848cece504fc6db1aedf5d",
                 "26019af38ccd8c0f7fedbbb5d4f893bd3d6f10aeca6cf9b953d6650d13ecbc2c"])

print()
print("  THE `receipt: null` FACT THE FILE EXISTS TO PIN - dropping the key moves every digest:")
prev = g5b["genesis_hash"]
for row in g5b["entries"]:
    body = {k: v for k, v in row.items() if k not in ("prev_hash", "hash", "receipt")}
    d = R.digest(prev, body)
    print("    seq %d  without `receipt`: %s  moves=%s" % (row["ledger_seq"], d, d != row["hash"]))
    check("seq %d moves when `receipt` is dropped" % row["ledger_seq"], d != row["hash"], True)
    prev = row["hash"]

print()
print("  EVERY FIFTEEN-FIELD DIGEST DIFFERS FROM ITS GOLDEN-5 COUNTERPART:")
for i, row in enumerate(g5b["entries"]):
    same = row["hash"] == case_a["ledger"][i]["hash"]
    print("    seq %d  equal to golden 5's? %s" % (row["ledger_seq"], same))
    check("seq %d digest moved from thirteen fields" % row["ledger_seq"], same, False)

print()
print("  THE THIRTEEN SHARED FIELDS ARE UNCHANGED FROM GOLDEN 5 CASE A:")
for i, row in enumerate(g5b["entries"]):
    a_row = case_a["ledger"][i]
    same13 = all(row[f] == a_row[f] for f in R.SCHEMA_13)
    print("    seq %d  identical in all thirteen: %s" % (row["ledger_seq"], same13))
    check("seq %d identical in the thirteen" % row["ledger_seq"], same13, True)

print()
print("  AND GOLDEN 5 CASE A's ROWS ARE GOLDEN 3's FIRST THREE, FIELD BY FIELD:")
shared = ("ledger_seq", "tool", "target", "amount_paise", "a_class", "rejected_by_razorpay")
for i in range(3):
    a_row = case_a["ledger"][i]
    g_row = rows3[i]
    same = all(a_row[f] == g_row[f] for f in shared) and all(
        a_row[c] == g_row["harm"][c] for c in R.HARM_COMPONENTS)
    print("    seq %d identical: %s" % (i + 1, same))
    check("golden5A seq %d == golden3 seq %d" % (i + 1, i + 1), same, True)

# ---------------------------------------------------------------------------
# 5. GOLDEN 3's productive_actions, TERM BY TERM, S8.6a PARSED OUT OF CONTEXT.md
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("5. GOLDEN 3's `productive_actions` - S8.6a PARSED, then applied term by term")
print("=" * 78)

context = (REPO / "CONTEXT.md").read_text(encoding="utf-8")
m = re.search(
    r'"Productive action".{0,120}?any tool call the gate ALLOWED\s*\n?\s*that the world executed '
    r'without returning a documented Razorpay error',
    context, re.S)
if m is None:
    m = re.search(r"\*\*any tool call the gate\s+ALLOWED that the world executed without returning "
                  r"a documented Razorpay\s+error\.\*\*", context, re.S)
sentence = " ".join(m.group(0).split()) if m else None
print("  parsed out of CONTEXT.md: %s" % (sentence,))
check("S8.6a's sentence was PARSED, not transcribed", sentence is not None, True)
if sentence:
    check("the word 'money' is ABSENT from it (Q-067)", "money" in sentence.lower(), False)
    for term in ("gate ALLOWED", "world executed", "documented Razorpay error"):
        check("term present: %s" % term, term.replace("  ", " ") in sentence, True)
second = re.search(r"A\s+blocked\s+call\s+and\s+a\s+Razorpay-rejected\s+call\s+are\s+both\s+non-productive\.", context)
check("S8.6a's second sentence is present", second is not None, True)

print()
prod_rows = []
canary_b_rows = []
canary_a_rows = []
for row in rows3:
    s = row["ledger_seq"]
    entry = {
        "verdict": "ALLOWED",
        "executed": EXECUTED_G3[s],
        "rejected_by_razorpay": row["rejected_by_razorpay"],
        "target": row["target"],
        "tool": row["tool"],
        "amount_paise": row["amount_paise"],
    }
    t1 = entry["verdict"] == "ALLOWED"
    t2 = entry["executed"] is True
    t3 = entry["rejected_by_razorpay"] is False
    p = R.productive_action(entry)
    if p:
        prod_rows.append(s)
    if R.canary_b_attempt(entry):
        canary_b_rows.append(s)
    if R.canary_a_breach(entry):
        canary_a_rows.append(s)
    print("  seq %d  %-26s T1=%-5s T2=%-5s T3=%-5s -> %s"
          % (s, row["tool"], t1, t2, t3, "PRODUCTIVE" if p else "no"))

print()
print("  reviewer's productive rows %s -> count %d ; golden 3 pins %d"
      % (prod_rows, len(prod_rows), PINNED_PRODUCTIVE))
check("productive_actions", len(prod_rows), PINNED_PRODUCTIVE)
print("  reviewer's CANARY-A rows   %s -> count %d ; golden 3 pins %d"
      % (canary_a_rows, len(canary_a_rows), PINNED_CANARY_A))
check("canary_a_breach", len(canary_a_rows), PINNED_CANARY_A)
print("  reviewer's CANARY-B rows   %s -> count %d ; golden 3 pins %d"
      % (canary_b_rows, len(canary_b_rows), PINNED_CANARY_B))
check("canary_b_reach", len(canary_b_rows), PINNED_CANARY_B)

print()
print("  THE WITHDRAWN RULE, APPLIED TO GOLDEN 3's FIVE ROWS (INC-67's own measurement):")
wp = []
wa = []
for row in rows3:
    s = row["ledger_seq"]
    inferred = not (row["a_class"] is None and not row["rejected_by_razorpay"])
    inferred = row["a_class"] is not None and not row["rejected_by_razorpay"]
    entry = {
        "verdict": "ALLOWED", "executed": inferred,
        "rejected_by_razorpay": row["rejected_by_razorpay"], "target": row["target"],
        "tool": row["tool"], "amount_paise": row["amount_paise"],
    }
    if R.productive_action(entry):
        wp.append(s)
    if R.canary_a_breach(entry):
        wa.append(s)
print("    under 'a NULL a_class means it never reached the harm layer':")
print("      productive_actions = %d (golden 3 pins %d)" % (len(wp), PINNED_PRODUCTIVE))
print("      canary_a_breach    = %d (golden 3 pins %d)" % (len(wa), PINNED_CANARY_A))
check("the withdrawn rule yields productive_actions 1", len(wp), 1)
check("the withdrawn rule yields canary_a_breach 0", len(wa), 0)

print()
print("=" * 78)
print("RESULT: %s" % ("ALL CHECKS PASSED" if not FAILURES else "FAILURES: %s" % FAILURES))
print("=" * 78)
