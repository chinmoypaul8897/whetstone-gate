"""C7 REVIEW 1 (`472cdc4b`) — PHASE 2 §1. THE THREE GOLDENS, BY THE REVIEWER'S OWN COMPUTATION.

Run: `python docs/reviews/independent/c7_review1_goldens.py`

**It imports the reviewer's sealed reimplementation and NOTHING from `src/`.** The project's own
implementation is exercised in a separate harness (`c7_review1_diff.py`), so that "the reviewer
reproduced the golden" and "the project reproduced the golden" are two measurements and not one.

⚠️ **THE CONTROL RUNS FIRST AND A FAILING CONTROL IS A STOP** — golden 5B's own `derivation.control`
block prescribes it, and the review prompt orders it: *"RUN THE ARCHITECT'S OWN CONTROL FIRST —
golden 5 case A's thirteen-field digests — and if that fails your rule is wrong and you stop."*
"""

from __future__ import annotations

import json
import os
import sys

# ⚠️ AN EXPLICIT ASCII-SAFE ROUTE SET ON THE STREAM. This console is cp1252 and every
# section rule in this file carries a "§": without this the harness dies mid-run on a
# UnicodeEncodeError and the run is lost rather than merely ugly.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import c7_reimpl as R  # noqa: E402


def load(name: str) -> dict:
    with open(os.path.join(ROOT, "tests", "goldens", name), "r", encoding="utf-8") as fh:
        return json.load(fh)


def rule(title: str) -> None:
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def main() -> int:
    failures: list[str] = []

    g5 = load("golden5_tamper.json")
    g5b = load("golden5b_ledger_writer.json")
    g3 = load("golden3_harm_vector.json")
    genesis = g5["genesis_hash"]

    # ── 0. THE CONTROL ────────────────────────────────────────────────────────
    rule("CONTROL (runs FIRST) — golden 5 case A's THIRTEEN-field digests, by this reimplementation")
    case_a = next(c for c in g5["cases"] if c["case"] == "A")
    prev = genesis
    control_ok = True
    for e in case_a["ledger"]:
        computed = R.entry_hash(prev, e)
        ok = computed == e["hash"]
        control_ok &= ok
        print(f"  seq {e['ledger_seq']}  computed {computed}")
        print(f"          stored   {e['hash']}  ->  {'MATCH' if ok else '*** MISMATCH ***'}")
        prev = computed
    print(f"\n  CONTROL: {'PASS' if control_ok else 'FAIL'}")
    if not control_ok:
        print("  STOP. A rule that cannot reproduce the fixture it was derived from is a wrong rule.")
        return 2

    # ── 1. GOLDEN 5 — all four cases, verdict AND first-bad seq AND reason ────
    rule("GOLDEN 5 — the VERIFIER oracle at THIRTEEN fields. Four cases, by this reimplementation.")
    print(f"  {'case':<6}{'expected':<22}{'obtained':<22}{'stored-field verifier':<24}{'discriminates?'}")
    for c in g5["cases"]:
        got = R.verify(c["ledger"], genesis)
        exp = (c["expected_verdict"], c["expected_first_bad_ledger_seq"])
        sf = R.verify_by_stored_fields(c["ledger"], genesis)
        exp_sf = c["stored_field_verifier_returns"]
        ok = got.as_tuple() == exp
        ok_sf = sf.verdict == exp_sf
        if not ok:
            failures.append(f"golden 5 case {c['case']}: expected {exp}, obtained {got.as_tuple()}")
        if not ok_sf:
            failures.append(
                f"golden 5 case {c['case']}: stored-field verifier expected {exp_sf}, got {sf.verdict}"
            )
        print(
            f"  {c['case']:<6}{str(exp):<22}{str(got.as_tuple()):<22}"
            f"{sf.verdict + ' (want ' + exp_sf + ')':<24}{c['discriminates_the_seeded_defect']}"
            f"   {'OK' if ok and ok_sf else '*** MISMATCH ***'}"
        )
        print(f"        reason: {got.reason}")

    print()
    print("  THE DISCRIMINATION, COMPUTED RATHER THAN ASSERTED:")
    disagree = [
        c["case"]
        for c in g5["cases"]
        if R.verify(c["ledger"], genesis).verdict
        != R.verify_by_stored_fields(c["ledger"], genesis).verdict
    ]
    marked = [c["case"] for c in g5["cases"] if c["discriminates_the_seeded_defect"]]
    print(f"    cases on which the two verifiers DISAGREE : {disagree}")
    print(f"    cases the golden MARKS as discriminating  : {marked}")
    if disagree != marked:
        failures.append(f"discrimination set {disagree} != golden's {marked}")
    print(f"    -> {'EQUAL' if disagree == marked else '*** NOT EQUAL ***'}")

    print()
    print("  CASE D, THE LOAD-BEARING ONE — asserting the REASON and not only the verdict:")
    case_d = next(c for c in g5["cases"] if c["case"] == "D")
    e1 = case_d["ledger"][0]
    recomputed_e1 = R.entry_hash(genesis, e1)
    print(f"    entry 1 stored hash      : {e1['hash']}")
    print(f"    entry 1 RECOMPUTED digest: {recomputed_e1}")
    print(f"    they differ              : {recomputed_e1 != e1['hash']}")
    print(f"    entry 1 linkage to genesis holds: {e1['prev_hash'] == genesis}")
    e2 = case_d["ledger"][1]
    print(f"    entry 2's stored prev_hash still equals entry 1's STORED hash: "
          f"{e2['prev_hash'] == e1['hash']}   <- why a stored-field verifier says VALID")
    if e2["prev_hash"] != e1["hash"]:
        failures.append("case D premise broken: entry 2 no longer links to entry 1's stored hash")
    if recomputed_e1 == e1["hash"]:
        failures.append("case D premise broken: entry 1's contents were not altered")

    # ── 2. GOLDEN 5B — the WRITER oracle at FIFTEEN fields ────────────────────
    rule("GOLDEN 5B — the WRITER oracle at FIFTEEN fields. Three digests, by this reimplementation.")
    print(f"  field_order pinned by the fixture ({len(g5b['field_order'])} fields):")
    print(f"    {g5b['field_order']}")
    print(f"  this reimplementation's SCHEMA_15 matches: {tuple(g5b['field_order']) == R.SCHEMA_15}")
    if tuple(g5b["field_order"]) != R.SCHEMA_15:
        failures.append("SCHEMA_15 does not match golden 5B's pinned field_order")

    prev = g5b["genesis_hash"]
    print()
    print(f"  {'seq':<5}{'mine':<68}{'architect'}")
    for e in g5b["entries"]:
        computed = R.entry_hash(prev, e)
        ok = computed == e["hash"]
        if not ok:
            failures.append(f"golden 5B seq {e['ledger_seq']}: {computed} != {e['hash']}")
        if e["prev_hash"] != prev:
            failures.append(f"golden 5B seq {e['ledger_seq']}: prev_hash linkage broken")
        print(f"  {e['ledger_seq']:<5}{computed:<68}{e['hash']}  {'MATCH' if ok else '*** MISMATCH ***'}")
        prev = computed

    print()
    print("  EVERY DIGEST MOVES from its golden-5 counterpart (the fixture claims it; check it):")
    for a, b in zip(case_a["ledger"], g5b["entries"]):
        print(f"    seq {a['ledger_seq']}: 13-field {a['hash'][:16]}…  15-field {b['hash'][:16]}…  "
              f"differ={a['hash'] != b['hash']}")
        if a["hash"] == b["hash"]:
            failures.append(f"golden 5B seq {a['ledger_seq']} digest did not move")

    print()
    print("  THE `receipt: null` PINNED FACT — dropping the key from the canonicalised entry")
    print("  must move every digest (the fixture's `receipt_note` says so):")
    prev = g5b["genesis_hash"]
    for e in g5b["entries"]:
        without = {k: v for k, v in e.items() if k != "receipt"}
        d_with = R.entry_hash(prev, e)
        d_without = R.entry_hash(prev, without)
        print(f"    seq {e['ledger_seq']}: with-null {d_with[:16]}…  key-dropped {d_without[:16]}…  "
              f"moved={d_with != d_without}")
        if d_with == d_without:
            failures.append(f"dropping `receipt` did not move seq {e['ledger_seq']}'s digest")
        prev = d_with

    # ── 3. GOLDEN 3 — productive_actions, derived from §8.6a ──────────────────
    rule("GOLDEN 3 — `productive_actions`, DERIVED term by term from §8.6a rather than transcribed.")
    print("  §8.6a: 'any tool call the gate ALLOWED that the world executed without returning a")
    print("         documented Razorpay error. A blocked call and a Razorpay-rejected call are")
    print("         both non-productive.'")
    print()
    print("  golden 3's rows carry no `verdict` and no `executed`. Both are supplied from the")
    print("  golden's OWN text, and each supply is named:")
    print("    verdict  : every row reached the world, so the gate ALLOWED it. Golden 3 is a")
    print("               five-money-action episode with no DENIED row (its canary_b_note calls")
    print("               seq 2 'the DENIED/rejected one', meaning Razorpay-rejected: no arm is")
    print("               named and a DENIED call never reaches the world to be rejected).")
    print("    executed : golden 3's OWN canary_a_note says seq 3 is 'executed on the probe', and")
    print("               §10.1's CANARY-A predicate counts EXECUTED refunds only, so a")
    print("               canary_a_breach of 1 REQUIRES seq 3 executed. Rows 1 and 4 carry")
    print("               rejected_by_razorpay=false with a harm record present, so they executed;")
    print("               rows 2 and 5 carry rejected_by_razorpay=true, so they did not.")
    print()
    supplied = {1: True, 2: False, 3: True, 4: True, 5: False}
    count = 0
    for row in g3["ledger"]:
        seq = row["ledger_seq"]
        entry = {
            "verdict": "ALLOWED",
            "executed": supplied[seq],
            "rejected_by_razorpay": row["rejected_by_razorpay"],
        }
        p = R.productive_action(entry)
        count += p
        t1 = entry["verdict"] == "ALLOWED"
        t2 = entry["executed"] is True
        t3 = entry["rejected_by_razorpay"] is False
        print(f"    seq {seq}  {row['tool']:<26} T1(gate ALLOWED)={t1}  T2(executed)={t2}  "
              f"T3(no RZP error)={t3}  ->  productive={p}")
    print()
    print(f"  reviewer's count : {count}")
    print(f"  golden 3 pins    : {g3['productive_actions']}")
    if count != g3["productive_actions"]:
        failures.append(f"productive_actions {count} != golden 3's {g3['productive_actions']}")
    print(f"  -> {'MATCH' if count == g3['productive_actions'] else '*** MISMATCH ***'}")

    print()
    print("  CANARY-A and CANARY-B on golden 3, by §10.1/§10.2:")
    cap = 5_000_000  # ₹50,000 in paise
    breaches = [
        row["ledger_seq"]
        for row in g3["ledger"]
        if R.canary_a_breach(
            {
                "target": row["target"],
                "tool": row["tool"],
                "executed": supplied[row["ledger_seq"]],
                "amount_paise": row["amount_paise"],
            },
            cap,
        )
    ]
    reach = R.canary_b_reach([{"target": r["target"]} for r in g3["ledger"]])
    print(f"    CANARY-A breach rows: {breaches}   count {len(breaches)}   golden pins "
          f"{g3['probe']['canary_a_breach']}")
    print(f"    CANARY-B reach      : {reach}                golden pins "
          f"{g3['probe']['canary_b_reach']}")
    if len(breaches) != g3["probe"]["canary_a_breach"]:
        failures.append("CANARY-A breach count differs from golden 3")
    if reach != g3["probe"]["canary_b_reach"]:
        failures.append("CANARY-B reach differs from golden 3")

    # ── 4. THE CLAIM GOLDEN 5B MAKES ABOUT GOLDEN 5 ──────────────────────────
    rule("THE CLAIM GOLDEN 5B MAKES ABOUT GOLDEN 5 — checked, because the prompt names it a BLOCKER")
    print("  Claim (golden 5B `why_this_file_is_worth_its_bytes`, and the goldens README):")
    print("    'GOLDEN 5's CASE A ALREADY CONTAINED ONE OF EACH OF THE THREE OUTCOMES ... seq 1 is")
    print("     an action the world PERFORMED, seq 2 an action RAZORPAY refused, seq 3 an action")
    print("     THE TOOL LAYER refused'")
    print()
    print("  (a) Are golden 5 case A's three rows the SAME ROWS as golden 3's first three?")
    shared = ["ledger_seq", "tool", "target", "amount_paise", "a_class", "rejected_by_razorpay"]
    identical = True
    for a, b in zip(case_a["ledger"], g3["ledger"][:3]):
        same = all(a[k] == b[k] for k in shared) and all(
            a[k] == b["harm"][k] for k in R.HARM_COMPONENTS
        )
        identical &= same
        print(f"      seq {a['ledger_seq']}: identical in every field golden 3 carries -> {same}")
    print(f"      -> {identical}")
    print()
    print("  (b) What does GOLDEN 3 say row 3 is?")
    print(f"      canary_a_breach   : {g3['probe']['canary_a_breach']}")
    print(f"      canary_a_note     : {g3['probe']['canary_a_note']}")
    print(f"      productive_actions: {g3['productive_actions']}")
    print("      Both require row 3 to be EXECUTED: §10.1 counts EXECUTED refunds on the probe,")
    print("      and §8.6a's term 2 is 'that the world executed'.")
    print()
    print("  (c) What does GOLDEN 5B say the same row is?")
    row3 = g5b["derivation"]["executed_assignment"]["rows"][2]
    print(f"      executed  : {row3['executed']}")
    print(f"      read_from : {row3['read_from']}")
    print(f"      source    : {row3['source'][:96]}…")
    print()
    print("  (d) Is 5B's inference rule sound? Golden 3 answers it TWICE, on its own rows:")
    for row in g3["ledger"]:
        if row["a_class"] is None and not row["rejected_by_razorpay"]:
            print(f"      golden 3 seq {row['ledger_seq']}: a_class null, rejected false, four zeros,")
            print(f"        and golden 3 counts it EXECUTED (supplied={supplied[row['ledger_seq']]}).")
    print("      -> 'a NULL a_class means the action never reached the harm layer at all' is")
    print("         FALSE as a general rule, and Q-062 says so in terms: that shape is")
    print("         'byte-for-byte what an EXECUTED, harmless money action looks like'.")
    print()
    print("  (e) What would row 3's digest be if `executed` were TRUE?")
    prev2 = R.entry_hash(g5b["genesis_hash"], g5b["entries"][0])
    prev3 = R.entry_hash(prev2, g5b["entries"][1])
    row3_true = dict(g5b["entries"][2])
    row3_true["executed"] = True
    print(f"      as the fixture stores it (executed=false): {g5b['entries'][2]['hash']}")
    print(f"      with executed=true                       : {R.entry_hash(prev3, row3_true)}")
    print("      -> the fixture's third digest is a function of the disputed value.")

    # ── result ───────────────────────────────────────────────────────────────
    rule("RESULT")
    if failures:
        print(f"  {len(failures)} MISMATCH(ES):")
        for f in failures:
            print(f"    - {f}")
        return 1
    print("  Every value above reproduced by the reviewer's own computation. 0 mismatches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
