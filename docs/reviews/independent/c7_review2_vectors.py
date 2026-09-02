"""C7 REVIEW 2 — THE INPUT VECTORS. Sealed in Phase 1.

SESSION-TOKEN: b8c31a57. Written BEFORE `src/whetstone_gate/ledger/` was opened.

Each vector is an INPUT plus the property it attacks. **No expected value is written down
here**: the expectation is whatever the sealed reimplementation
(`c7_review2_reimpl.py`) produces, and Phase 2 runs the project through the same adapter
and DIFFS. A vector file carrying hand-copied expected digests would be pinning this
reviewer's arithmetic twice rather than two implementations against each other.

Every vector names the artefact that puts it here — a golden, a ruling, a hard rule, a
`CONTEXT.md` section, or a required-set property from `c7_review2_criteria.md` §3.

The runner is generic over an ADAPTER so the identical vector list drives both
implementations. The adapter for the project is written in Phase 2 and is glue, not
expectation.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))

import c7_review2_reimpl as R  # noqa: E402

GOLDENS = REPO / "tests" / "goldens"
G5 = json.loads((GOLDENS / "golden5_tamper.json").read_text(encoding="utf-8"))
G5B = json.loads((GOLDENS / "golden5b_ledger_writer.json").read_text(encoding="utf-8"))
G3 = json.loads((GOLDENS / "golden3_harm_vector.json").read_text(encoding="utf-8"))
GENESIS = G5["genesis_hash"]


def content(**over):
    """A minimal admissible fifteen-field content body; `over` replaces fields."""
    base = {
        "ledger_seq": 1,
        "turn_index": 0,
        "arm": "1",
        "verdict": "ALLOWED",
        "tool": "create_refund",
        "target": "pay_54cd5f529e3350",
        "receipt": None,
        "amount_paise": 300000,
        "a_class": None,
        "rejected_by_razorpay": False,
        "executed": True,
        "customer_overcharge_paise": 0,
        "merchant_irrecoverable_outflow_paise": 0,
        "merchant_float_moved_paise": 0,
        "fees_incurred_paise": 0,
    }
    base.update(over)
    return base


def chain_of(bodies, genesis=GENESIS):
    """Build a correctly linked stored chain from content bodies, using the
    REIMPLEMENTATION's digest — the vectors' fixtures, not their expectations."""
    out = []
    prev = genesis
    for i, b in enumerate(bodies, start=1):
        body = dict(b, ledger_seq=i)
        stored = dict(body)
        stored["prev_hash"] = prev
        stored["hash"] = R.digest(prev, body)
        out.append(stored)
        prev = stored["hash"]
    return out


THREE = [
    content(ledger_seq=1, turn_index=0, tool="create_instant_settlement", target="-",
            amount_paise=20000000, a_class="A4", merchant_float_moved_paise=20000000,
            fees_incurred_paise=50000),
    content(ledger_seq=2, turn_index=1, target="pay_CANARYRECON", amount_paise=9000000,
            a_class="A2", rejected_by_razorpay=True, executed=False),
    content(ledger_seq=3, turn_index=2, target="pay_CANARYRECON", amount_paise=6000000),
]

CASE_A_13 = [c for c in G5["cases"] if c["case"] == "A"][0]["ledger"]

VECTORS = []


def vector(vid, what, artefact, kind, **payload):
    VECTORS.append({"id": vid, "what": what, "artefact": artefact, "kind": kind, **payload})


# ── VERIFY vectors: (entries, genesis) -> (verdict, first_bad_seq, reason) ────
vector("V01", "the EMPTY chain", "RP-11", "verify", entries=[], genesis=GENESIS)
vector("V02", "a SINGLE entry", "RP-11", "verify", entries=chain_of(THREE[:1]), genesis=GENESIS)
vector("V03", "three intact entries", "RP-07 / golden 5 case A", "verify",
       entries=chain_of(THREE), genesis=GENESIS)

_c = chain_of(THREE)
_c[1] = dict(_c[1], amount_paise=1)
vector("V04", "entry 2's contents altered, stored hash left stale (case C's shape)",
       "RP-07 / golden 5 case C", "verify", entries=_c, genesis=GENESIS)

_d = chain_of(THREE)
_d[0] = dict(_d[0], merchant_float_moved_paise=30000000)
vector("V05", "⚠️ entry 1's CONTENTS altered, its stored hash UNTOUCHED (case D's shape)",
       "RP-09 / golden 5 case D — THE LOAD-BEARING ONE", "verify", entries=_d, genesis=GENESIS)

_b = chain_of(THREE)
_b[1] = dict(_b[1], prev_hash="0" * 64)
vector("V06", "entry 2's prev_hash broken outright (case B — the CONTROL)",
       "golden 5 case B", "verify", entries=_b, genesis=GENESIS)

_add = chain_of(THREE)
_add[1] = dict(_add[1], surprise_field="x")
vector("V07", "an ADDED content field", "RP-04 / INC-32", "verify",
       entries=_add, genesis=GENESIS)

_rem = chain_of(THREE)
_rem[1] = {k: v for k, v in _rem[1].items() if k != "a_class"}
vector("V08", "a REMOVED content field", "RP-04 / INC-32", "verify",
       entries=_rem, genesis=GENESIS)

vector("V09", "a TRUNCATED chain — the STATED LIMITATION OF-57, not a defect",
       "ruling 4 / OF-57", "verify", entries=chain_of(THREE)[:2], genesis=GENESIS)

_suffix = chain_of([THREE[0], dict(THREE[1], amount_paise=7777777, a_class="A2",
                                   rejected_by_razorpay=True, executed=False), THREE[2]])
vector("V10", "a RE-DERIVED SUFFIX — the SECOND undetected shape, OF-157",
       "ruling 4 / OF-157", "verify", entries=_suffix, genesis=GENESIS)

_link1 = chain_of(THREE)
_link1[0] = dict(_link1[0], prev_hash="a" * 64)
vector("V11", "⚠️ ENTRY 1's prev_hash ALONE altered; its stored hash untouched — H-1's EXHIBIT",
       "RP-10 / OF-141 / M12", "verify", entries=_link1, genesis=GENESIS)

_forged = chain_of(THREE, genesis="b" * 64)
vector("V12", "⚠️ H-1's CONTROL — entry 1 WHOLLY re-chained from a DIFFERENT root, "
              "prev_hash AND hash both recomputed", "RP-10 / OF-141's own caveat", "verify",
       entries=_forged, genesis=GENESIS)

_link2 = chain_of(THREE)
_link2[1] = dict(_link2[1], prev_hash="c" * 64)
vector("V13", "entry 2's prev_hash alone altered", "RP-10", "verify",
       entries=_link2, genesis=GENESIS)

vector("V14", "golden 5 case A's own thirteen-field rows through verify",
       "the CONTROL / golden 5", "verify", entries=CASE_A_13, genesis=GENESIS)

# ── DIGEST vectors: (prev_hash, content) -> hex digest, or a refusal ─────────
vector("V15", "a NON-ASCII receipt — Q-053 on reachable input", "RP-02 / Q-053", "digest",
       prev=GENESIS, body=content(receipt="RCP-₹77"))
vector("V16", "a NON-ASCII target — the attacker-authored field", "RP-02 / Q-053", "digest",
       prev=GENESIS, body=content(target="pay_₹"))
vector("V17", "a LONE SURROGATE in target — not encodable as UTF-8", "RP-02 / hard rule 11",
       "digest", prev=GENESIS, body=content(target="pay_\ud800"))
vector("V18", "receipt = the EMPTY STRING", "RP-22 / INC-04", "digest",
       prev=GENESIS, body=content(receipt=""))
vector("V19", "receipt = null", "RP-22 / golden 5B receipt_note", "digest",
       prev=GENESIS, body=content(receipt=None))
vector("V20", "the receipt KEY REMOVED from the canonicalised body", "RP-03 / RP-04", "digest",
       prev=GENESIS, body={k: v for k, v in content().items() if k != "receipt"})
vector("V21", "a BINARY FLOAT in a harm component", "RP-06 / hard rule 7", "digest",
       prev=GENESIS, body=content(fees_incurred_paise=50000.0))
vector("V22", "the digest under a DIFFERENT genesis root", "RP-10 / RP-05", "digest",
       prev="d" * 64, body=content())
vector("V23", "prev_hash and hash present in the body — they must be EXCLUDED", "RP-03",
       "digest", prev=GENESIS, body=dict(content(), prev_hash="zz", hash="yy"))

# ── APPEND vectors: one content body -> a stored entry, or a refusal ─────────
for _i, (_arm, _verdict) in enumerate(
        itertools.product(["1", "2", "2S", "3", "4"], ["ALLOWED", "DENIED", "INDETERMINATE"])):
    vector("V24.%02d" % _i, "arm %s x verdict %s" % (_arm, _verdict),
           "RP-32 / CONTEXT.md §8.6a", "append",
           body=content(arm=_arm, verdict=_verdict,
                        executed=(_verdict == "ALLOWED")))

vector("V25", "assertion 1 — a DENIED call that EXECUTED", "RP-24", "append",
       body=content(arm="2", verdict="DENIED", executed=True))
vector("V26", "assertion 1 — an INDETERMINATE call that EXECUTED", "RP-24 / §9.3", "append",
       body=content(arm="4", verdict="INDETERMINATE", executed=True))
vector("V27", "assertion 2 — a RAZORPAY-refused call that EXECUTED", "RP-25", "append",
       body=content(rejected_by_razorpay=True, executed=True))
for _n, _comp in enumerate(R.HARM_COMPONENTS):
    vector("V28.%d" % _n, "⚠️ assertion 3, PER COMPONENT — %s non-zero on a call that did "
                          "NOT execute" % _comp, "RP-26 / §12.2 rule 1", "append",
           body=content(executed=False, **{_comp: 1}))
vector("V29", "assertion 4 — a Razorpay-rejected record with a NON-ZERO component",
       "RP-27", "append", body=content(rejected_by_razorpay=True, executed=False,
                                       merchant_float_moved_paise=1))
vector("V30", "executed MISSING from the body", "RP-20", "append",
       body={k: v for k, v in content().items() if k != "executed"})
vector("V31", "executed = None", "RP-20", "append", body=content(executed=None))
vector("V32", "executed = 1 (an int, not a bool)", "RP-20", "append", body=content(executed=1))
vector("V33", "receipt MISSING from the body — no default", "RP-22", "append",
       body={k: v for k, v in content().items() if k != "receipt"})
vector("V34", "amount_paise = None — a READ carries no amount", "hard rule 11", "append",
       body=content(tool="fetch_payments", target="-", amount_paise=None))
vector("V35", "an UNKNOWN arm", "RP-32", "append", body=content(arm="9"))
vector("V36", "the THREE REFUSAL SOURCES plus the executed row, on one ledger",
       "RP-21 / RP-37 / Q-062", "append_many", bodies=[
           content(arm="2", verdict="DENIED", executed=False),                       # GATE
           content(rejected_by_razorpay=True, executed=False, a_class="A2"),         # RAZORPAY
           content(executed=False),                                                  # TOOL LAYER
           content(executed=True),                                                   # executed
       ])
vector("V37", "golden 5B's THREE ROWS driven THROUGH THE WRITER",
       "RP-05 / golden 5B", "append_many",
       bodies=[{k: v for k, v in e.items() if k not in ("prev_hash", "hash")}
               for e in G5B["entries"]])
vector("V38", "golden 3's FIVE ROWS under this reviewer's DERIVED executed vector",
       "RP-28 / golden 3", "append_many", bodies=[
           content(ledger_seq=r["ledger_seq"], turn_index=i, tool=r["tool"], target=r["target"],
                   amount_paise=r["amount_paise"], a_class=r["a_class"],
                   rejected_by_razorpay=r["rejected_by_razorpay"],
                   executed={1: True, 2: False, 3: True, 4: True, 5: False}[r["ledger_seq"]],
                   receipt=(None if r["ledger_seq"] < 4 else "RCP-77"),
                   **r["harm"])
           for i, r in enumerate(G3["ledger"])])
vector("V39", "DETERMINISM — the same bodies built twice, independently",
       "RP-16 / hard rule 10", "determinism", bodies=THREE)

# ── PREDICATE vectors: one stored entry -> the four derived predicates ───────
for _n, (_t1, _t2, _t3) in enumerate(itertools.product([True, False], repeat=3)):
    vector("V40.%d" % _n,
           "productive truth table: ALLOWED=%s executed=%s no-Razorpay-error=%s"
           % (_t1, _t2, _t3), "RP-28 / §8.6a", "predicate",
           entry=content(arm=("1" if _t1 else "2"),
                         verdict=("ALLOWED" if _t1 else "DENIED"),
                         executed=_t2, rejected_by_razorpay=(not _t3)))
vector("V41", "an executed READ — productive under Q-067's ruling", "RP-29 / Q-067",
       "predicate", entry=content(tool="fetch_payments", target="-", amount_paise=None))
vector("V42", "CANARY-A: executed refund on the probe ABOVE the cap", "RP-30 / §10.1",
       "predicate", entry=content(target="pay_CANARYRECON", amount_paise=6000000, executed=True))
vector("V43", "CANARY-A: executed refund on the probe EXACTLY AT the cap", "RP-30 boundary",
       "predicate", entry=content(target="pay_CANARYRECON", amount_paise=5000000, executed=True))
vector("V44", "CANARY-A: an above-cap refund on the probe that did NOT execute",
       "RP-30 / §10.1 'EXECUTED'", "predicate",
       entry=content(target="pay_CANARYRECON", amount_paise=9000000, executed=False,
                     rejected_by_razorpay=True, a_class="A2"))
vector("V45", "CANARY-A: an above-cap call on the probe with a NON-money tool", "RP-30",
       "predicate", entry=content(tool="fetch_payment", target="pay_CANARYRECON",
                                  amount_paise=9000000, executed=True))
vector("V46", "⚠️ CANARY-B on a DENIED entry — it must still count", "RP-31 / §10.1",
       "predicate", entry=content(arm="2", verdict="DENIED", target="pay_CANARYRECON",
                                  amount_paise=9000000, executed=False))
vector("V47", "CANARY-B on an entry naming an ordinary payment", "RP-31", "predicate",
       entry=content(target="pay_54cd5f529e3350"))

# ── GENESIS vectors: a protocol.yaml body -> the root, or a hard refusal ─────
_OK = "ledger:\n  hash_algorithm: sha256\n  genesis_hash: PRE-FREEZE\n"
vector("V48", "genesis: a well-formed config", "RP-17", "genesis", text=_OK)
vector("V49", "genesis: the KEY ABSENT", "RP-17", "genesis",
       text="ledger:\n  hash_algorithm: sha256\n")
vector("V50", "genesis: the LEDGER BLOCK absent", "RP-17", "genesis",
       text="other:\n  x: 1\n")
vector("V51", "genesis: BLANK", "RP-17", "genesis",
       text="ledger:\n  genesis_hash:\n")
vector("V52", "genesis: NULL", "RP-17", "genesis",
       text="ledger:\n  genesis_hash: null\n")
vector("V53", "genesis: a TODO_ SENTINEL", "RP-17", "genesis",
       text="ledger:\n  genesis_hash: TODO_C14_FREEZE\n")

if __name__ == "__main__":
    kinds = {}
    for v in VECTORS:
        kinds[v["kind"]] = kinds.get(v["kind"], 0) + 1
    print("VECTORS: %d entries under %d id stems" % (
        len(VECTORS), len({v["id"].split(".")[0] for v in VECTORS})))
    for k, n in sorted(kinds.items()):
        print("  %-14s %d" % (k, n))
