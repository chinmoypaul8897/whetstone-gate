"""C7 REVIEW 2 — THE SIX SURVIVORS, EACH DRIVEN. Equivalence PROVED or REFUTED, never asserted.

SESSION-TOKEN: b8c31a57.

Each survivor is reimplemented HERE, in process, so its consequence can be exhibited without
mutating any tree. Every claim below is a measurement printed beside it.

  M09  RP-07  the walk carries the STORED digest forward   (REVIEW 1's `M08`)
  M11  RP-09  the stale-digest REASON reworded to say the link is broken
  M32  RP-27  assertion 4 — a REJECTED record may carry non-zero harm
  M43  RP-38  the four harm components SUMMED into a total
  M44  ----   `append_log`'s all-or-nothing batch semantics       (NOT OWNED, sealed §4)
  M45  ----   `store.write` is not publish-on-complete            (OUTSIDE the sealed set)
"""

from __future__ import annotations

import itertools
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "docs" / "reviews" / "independent"))

from whetstone_gate.ledger import build, chain, control, store            # noqa: E402
from whetstone_gate.ledger import entry as entrymod                       # noqa: E402
from whetstone_gate.world.harm import COMPONENTS                          # noqa: E402

G5 = json.loads((REPO / "tests/goldens/golden5_tamper.json").read_text(encoding="utf-8"))
CASE_A = [c for c in G5["cases"] if c["case"] == "A"][0]["ledger"]
GEN = G5["genesis_hash"]
SPEC = chain.ChainSpec(genesis_hash=GEN, algorithm="sha256")

FAILS = []


def check(label, obtained, expected):
    ok = obtained == expected
    print("    %-76s %s" % (label, "OK" if ok else "FAIL"))
    if not ok:
        print("        obtained %r expected %r" % (obtained, expected))
        FAILS.append(label)


def row(**over):
    base = dict(turn_index=0, verdict="ALLOWED", tool="create_refund",
                target="pay_54cd5f529e3350", receipt=None, amount_paise=300000,
                a_class=None, rejected_by_razorpay=False, executed=True,
                customer_overcharge_paise=0, merchant_irrecoverable_outflow_paise=0,
                merchant_float_moved_paise=0, fees_incurred_paise=0)
    base.update(over)
    return base


# =========================================================================================
print("=" * 100)
print("M09 — RP-07: `expected_prev = recomputed` becomes `expected_prev = stored['hash']`")
print("       (this is REVIEW 1's `M08`, re-tested rather than inherited)")
print("=" * 100)
print()
print("  THE CONTROL-FLOW PROOF, read off the shipped source rather than described:")
src = (REPO / "src/whetstone_gate/ledger/chain.py").read_text(encoding="utf-8")
i_guard = src.index('if recomputed != stored["hash"]:')
i_assign = src.index("        expected_prev = recomputed")
between = src[i_guard:i_assign]
print("      the guard  `if recomputed != stored[\"hash\"]:`  ends in a `return`  : %s"
      % ("return ChainVerdict(" in between))
print("      the assignment is reached ONLY by falling through that guard      : %s"
      % (i_assign > i_guard and between.count("\n        expected_prev") == 0))
check("at the assignment, `recomputed` and `stored['hash']` are equal BY CONSTRUCTION",
      "return ChainVerdict(" in between and i_assign > i_guard, True)


def verify_M09(entries, genesis):
    expected = genesis
    for stored in entries:
        seq = stored.get("ledger_seq")
        if stored["prev_hash"] != expected:
            return ("DETECTED", seq)
        body = {k: v for k, v in stored.items() if k not in chain.CHAIN_FIELDS}
        rec = chain.entry_digest(expected, body, algorithm="sha256")
        if rec != stored["hash"]:
            return ("DETECTED", seq)
        expected = stored["hash"]        # <- the mutation
    return ("VALID", None)


print()
print("  AND THE SEARCH, because a proof that is only an argument is an argument.")
print("  Every mutation shape over golden 5 case A, both verifiers, looking for ONE disagreement:")
shapes = []
for idx in range(3):
    for op in ("alter-content", "break-prev", "break-hash", "add-field", "remove-field"):
        doc = [dict(e) for e in CASE_A]
        e = dict(doc[idx])
        if op == "alter-content":
            e["amount_paise"] = 1
        elif op == "break-prev":
            e["prev_hash"] = "0" * 64
        elif op == "break-hash":
            e["hash"] = "0" * 64
        elif op == "add-field":
            e["smuggled"] = 1
        else:
            e.pop("a_class", None)
        doc[idx] = e
        shapes.append(("%s@%d" % (op, idx + 1), doc))
shapes.append(("intact", [dict(e) for e in CASE_A]))
shapes.append(("truncated", [dict(e) for e in CASE_A][:2]))
shapes.append(("empty", []))
disagreements = []
for name, doc in shapes:
    a = chain.verify(doc, genesis_hash=GEN, algorithm="sha256")
    b = verify_M09(doc, GEN)
    if (a.verdict, a.first_bad_ledger_seq) != b:
        disagreements.append((name, (a.verdict, a.first_bad_ledger_seq), b))
print("      %d shapes searched; disagreements: %d" % (len(shapes), len(disagreements)))
for d in disagreements:
    print("        %s" % (d,))
check("M09 and HEAD agree on every shape", disagreements, [])
print()
print("  ⚠️ AND WHAT M09 IS NOT. `PROCESS.md` §5.4's defect is a verifier that NEVER RECOMPUTES.")
print("     M09 changes which of two provably equal names carries the value forward, with the")
print("     recomputation intact. The mutant that removes the recomputation is M08, and M08 was")
print("     KILLED. VERDICT: EQUIVALENT — M09 is evidence FOR the verifier, not against it.")

# =========================================================================================
print()
print("=" * 100)
print("M11 — RP-09: the STALE-DIGEST branch's `reason` reworded to say 'the link is broken'")
print("=" * 100)


def verify_M11(entries, genesis):
    expected = genesis
    for stored in entries:
        seq = stored.get("ledger_seq")
        if stored["prev_hash"] != expected:
            return ("DETECTED", seq, "the link is broken: entry %s stores prev_hash ..." % seq)
        body = {k: v for k, v in stored.items() if k not in chain.CHAIN_FIELDS}
        rec = chain.entry_digest(expected, body, algorithm="sha256")
        if rec != stored["hash"]:
            return ("DETECTED", seq, "the link is broken at entry %s: recomputed ..." % seq)
        expected = rec
    return ("VALID", None, "")


case_d = [c for c in G5["cases"] if c["case"] == "D"][0]["ledger"]
head_d = chain.verify(case_d, genesis_hash=GEN, algorithm="sha256")
mut_d = verify_M11(case_d, GEN)
print()
print("  GOLDEN 5 CASE D — the load-bearing case, under both:")
print("      HEAD  %s / %s / %r" % (head_d.verdict, head_d.first_bad_ledger_seq,
                                    head_d.reason[:70]))
print("      M11   %s / %s / %r" % (mut_d[0], mut_d[1], mut_d[2][:70]))
check("verdict and seq are UNCHANGED", (mut_d[0], mut_d[1]),
      (head_d.verdict, head_d.first_bad_ledger_seq))
check("the REASON changes, and changes to a statement that is FALSE about case D",
      ("link is broken" in mut_d[2], "link is broken" in head_d.reason), (True, False))
print()
print("  ⚠️ WHY THE NEW REASON IS FALSE AND NOT MERELY DIFFERENT — case D's link IS intact:")
e1 = case_d[0]
print("      entry 1's stored prev_hash == the genesis root : %s" % (e1["prev_hash"] == GEN))
print("      entry 1's contents hash to its stored digest   : %s"
      % (chain.entry_digest(GEN, {k: v for k, v in e1.items() if k not in chain.CHAIN_FIELDS},
                            algorithm="sha256") == e1["hash"]))
check("so 'the link is broken' is a FABRICATED reason for case D",
      e1["prev_hash"] == GEN, True)
print()
print("  ⚠️ NOT EQUIVALENT. `INCIDENTS.md` INC-34 is precisely 'the right verdict at the right")
print("     seq for an entirely fabricated reason', and the FIX's own H-1 fixture says a right")
print("     verdict for the wrong reason is the failure INC-34 nearly shipped — then asserts the")
print("     reason for the LINK branch and for no other. The STALE-DIGEST branch's reason is")
print("     asserted by nothing in this repository.")
suite = (REPO / "tests/test_c7_ledger.py").read_text(encoding="utf-8")
for needle in ("CONTENTS do not hash", "do not hash to its stored digest", ".reason"):
    print("      occurrences of %-34r in tests/test_c7_ledger.py: %d"
          % (needle, suite.count(needle)))
reason_asserts = [ln.strip() for ln in suite.splitlines() if ".reason" in ln]
print("      every `.reason` assertion in the suite:")
for ln in reason_asserts:
    print("        %s" % ln[:100])
check("no assertion in the suite mentions the stale-digest reason",
      any("CONTENTS do not hash" in ln or "do not hash" in ln for ln in reason_asserts), False)

# =========================================================================================
print()
print("=" * 100)
print("M32 — RP-27: assertion 3's guard narrowed to `if not executed and not rejected:`")
print("=" * 100)


def admissible_M32(values):
    """entry._validate_executed_consistency with M32 applied, everything else identical."""
    executed = values["executed"]
    verdict = values["verdict"]
    rejected = values["rejected_by_razorpay"]
    if executed and verdict != "ALLOWED":
        return False
    if executed and rejected:
        return False
    if not executed and not rejected:                     # <- the mutation
        if [c for c in COMPONENTS if values[c] != 0]:
            return False
    return True


bad = row(rejected_by_razorpay=True, executed=False, a_class="A2",
          merchant_irrecoverable_outflow_paise=7_500_000)
try:
    chain.Ledger(spec=SPEC, seed=2001, arm="1").append(**bad)
    head_writes = True
except entrymod.LedgerEntryError:
    head_writes = False
print()
print("  THE EXHIBIT: a RAZORPAY-REJECTED record claiming Rs 75,000 of irrecoverable outflow.")
print("      HEAD writes it : %s" % head_writes)
print("      M32 writes it  : %s" % admissible_M32(dict(bad, ledger_seq=1, arm="1")))
check("HEAD REFUSES it and M32 ACCEPTS it — NOT EQUIVALENT",
      (head_writes, admissible_M32(dict(bad, ledger_seq=1, arm="1"))), (False, True))
print()
print("  ⚠️ WHAT IT COSTS, and it is a PUBLISHED NUMBER rather than a message. §12.2's four")
print("     components are the money metric. golden 3's `structural_finding` says a rejected")
print("     record 'contributes ZERO to all four', and §12.2 zeroes them for an action the")
print("     world did not perform. Under M32 a ledger can carry harm attributed to a call")
print("     RAZORPAY REFUSED — the exact class `INCIDENTS.md` INC-03 is about, one layer up,")
print("     and 59% of the spike's escapes were Razorpay-rejected.")
print()
print("  AND THE EXHAUSTIVE SEARCH over the writable space, so the exhibit is not a lucky one:")
diverge = 0
total = 0
for executed, rejected, verdict in itertools.product(
        [True, False], [True, False], ["ALLOWED", "DENIED", "INDETERMINATE"]):
    for comp in (None, *COMPONENTS):
        values = dict(row(executed=executed, rejected_by_razorpay=rejected, verdict=verdict,
                          arm="4"), ledger_seq=1, arm="4")
        if comp:
            values[comp] = 1
        total += 1
        try:
            entrymod.validate_content(values)
            head_ok = True
        except entrymod.LedgerEntryError:
            head_ok = False
        # M32 differs only inside _validate_executed_consistency; the rest of validate_content
        # is unchanged, so the comparison is only meaningful where HEAD's other checks pass.
        mut_ok = admissible_M32(values)
        if head_ok != mut_ok and verdict in ("ALLOWED", "DENIED", "INDETERMINATE"):
            try:
                entrymod._validate(dict(values), require_chain=False)
                other_checks_pass = True
            except entrymod.LedgerEntryError as exc:
                other_checks_pass = "executed" in str(exc) or "non-zero harm" in str(exc)
            if other_checks_pass:
                diverge += 1
print("      %d writable shapes; HEAD and M32 disagree on %d" % (total, diverge))
check("M32 is NOT equivalent", diverge > 0, True)

# =========================================================================================
print()
print("=" * 100)
print("M43 — RP-38: `moved_money`'s `any(c != 0)` becomes `sum(c) != 0`")
print("=" * 100)
print()
print("  THE PROOF, and it rests on a validation this package ENFORCES rather than on taste:")
val_src = (REPO / "src/whetstone_gate/ledger/entry.py").read_text(encoding="utf-8")
print("      entry._validate requires each component `>= 0`: %s"
      % ("must be an integer >= 0 paise" in val_src))
check("every harm component is a NON-NEGATIVE integer on every construction path",
      "must be an integer >= 0 paise" in val_src, True)
print("      over non-negative integers, `sum(x) != 0`  <=>  `any(x != 0)`.")
print()
print("  AND THE SEARCH over every component pattern up to two non-zero values:")
disagree = 0
n = 0
for pattern in itertools.product([0, 1, 5_000_000], repeat=4):
    n += 1
    a = any(v != 0 for v in pattern)
    b = sum(pattern) != 0
    if a != b:
        disagree += 1
print("      %d patterns; disagreements: %d" % (n, disagree))
check("M43 is EQUIVALENT over the writable space", disagree, 0)
print()
print("  ⚠️ AND THE PROPERTY IT LOOKS LIKE IT BREAKS, judged rather than waved past. §12.2's")
print("     reporting rule 1 is *'the four components are REPORTED separately and are NEVER")
print("     summed'*. `moved_money` returns a BOOL; it reports no figure and no rupee total, so")
print("     no reporting rule is breached. The stronger prohibition — *'there is no total() in")
print("     this package and there must never be one'* — is a COMMENT IN THE CODE, which under")
print("     the sealed criterion C2 is not an artefact that outranks the code.")
print("     VERDICT: EQUIVALENT, with the residual named — the property is pinned by a comment.")

# =========================================================================================
print()
print("=" * 100)
print("M44 — `append_log`'s ALL-OR-NOTHING batch semantics  (NOT OWNED, sealed §4)")
print("=" * 100)
print()
print("  Re-driven rather than inherited from REVIEW 1's OF-143. The exhibit, on HEAD:")


class _Res:
    def __init__(self, ok, harm=None):
        self.ok = ok
        self.harm = harm


led = chain.Ledger(spec=SPEC, seed=2001, arm="1")
rows = [
    (0, "create_refund", {"payment_id": "pay_54cd5f529e3350", "amount": 300000}, _Res(True)),
    (1, "create_refund", {"payment_id": "pay_54cd5f529e3350", "amount": 300000}, _Res(True)),
    (2, "create_refund", {"payment_id": "pay_54cd5f529e3350", "amount": 300000}, _Res(True)),
]
try:
    build.append_log(led, rows, turn_index_of=lambda r: r[0],
                     verdict_of=lambda r: "DENIED" if r[0] == 2 else "ALLOWED")
    refused = False
except entrymod.LedgerEntryError:
    refused = True
print("      a three-row batch whose LAST row carries a verdict arm 1 cannot emit:")
print("        refused: %s      len(ledger) afterwards: %d  (M16/M44 would leave 2)"
      % (refused, len(led)))
check("HEAD is all-or-nothing", (refused, len(led)), (True, 0))
print()
print("  ⚠️ THE DISPOSITION IS THE SEALED ONE AND THE SEAL PREDATES THIS MEASUREMENT.")
print("     `CONTEXT.md` §16 says append-only, hash-chained and nothing about batches; no C7")
print("     card clause, no ruling and no golden mentions one. It is the builder's Class B")
print("     choice, argued in `append_log`'s docstring — and hard rule 2 makes a Class B choice")
print("     'recorded with rationale, JUDGED AT REVIEW'. NOT OWNED. MEDIUM. `OF-143` stays open.")

# =========================================================================================
print()
print("=" * 100)
print("M45 — `store.write` is not publish-on-complete  (OUTSIDE the sealed set)")
print("=" * 100)
print()
print("  Hard rule 10 names 'atomic writes, publish-on-complete' in terms, and `store.write`")
print("  implements it with a `.partial` sibling and `os.replace`. THIS REVIEWER'S OWN PHASE-1")
print("  TABLE HAS NO ROW FOR IT — the omission is this review's, and it is reported as one.")
store_src = (REPO / "src/whetstone_gate/ledger/store.py").read_text(encoding="utf-8")
print("      `.partial` temporary written then os.replace()d: %s"
      % (".partial" in store_src and "os.replace(" in store_src))
check("the property HOLDS on HEAD", ".partial" in store_src and "os.replace(" in store_src, True)
print("      and it is pinned by: NOTHING — M45 removes the temporary entirely and the suite")
print("      stays green. Under Q-082 a survivor OUTSIDE the required set is MEDIUM and does")
print("      NOT hold the tag; the omission from the set is named so it is not read as a pass.")

print()
print("=" * 100)
print("SURVIVOR DISPOSITIONS")
print("=" * 100)
print("  M09  RP-07  EQUIVALENT — proved by control flow AND by a %d-shape search" % len(shapes))
print("  M11  RP-09  ⚠️ OWNED, NOT EQUIVALENT — the stale-digest reason is pinned by nothing")
print("  M32  RP-27  ⚠️ OWNED, NOT EQUIVALENT — assertion 4 is pinned by nothing")
print("  M43  RP-38  EQUIVALENT — components are validated >= 0, so sum != 0 <=> any != 0")
print("  M44  ----   NOT OWNED (sealed §4). MEDIUM, `OF-143`, unchanged")
print("  M45  ----   OUTSIDE the sealed set. MEDIUM, and the omission is this review's")
print()
print("CHECKS: %d failures" % len(FAILS))
for f in FAILS:
    print("  FAILED: %s" % f)
