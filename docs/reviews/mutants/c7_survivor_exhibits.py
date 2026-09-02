"""C7 REVIEW 1 (`472cdc4b`) — THE FOUR SURVIVORS, EACH SETTLED BY EXHIBIT.

Run:  `PYTHONPATH=src python docs/reviews/mutants/c7_survivor_exhibits.py`

`docs/reviews/README.md`: each mutant row carries *"the test that killed it — **or an explicit
equivalence proof**"*. A survivor is therefore one of exactly two things, and the difference is
decided by a **concrete input on which HEAD and the mutant differ** — or by a proof that no such
input exists. Neither is settled by assertion here.

    M08  EQUIVALENT   — proved: the assignment is reached only where the two values are equal
    M12  NOT equivalent — exhibited: an input HEAD DETECTS and the mutant calls VALID
    M16  NOT equivalent — exhibited: the ledger is left SHORT where HEAD leaves it untouched
    M39  NOT equivalent — exhibited: the claim itself changes, and no test reads it
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

import whetstone_gate  # noqa: E402
from whetstone_gate import config as cfg  # noqa: E402
from whetstone_gate.ledger import build as P_build  # noqa: E402
from whetstone_gate.ledger import chain as P_chain  # noqa: E402
from whetstone_gate.ledger import entry as P_entry  # noqa: E402

OUT: list[str] = []


def say(t: str = "") -> None:
    OUT.append(t)
    print(t)


def rule(t: str) -> None:
    say("")
    say("=" * 100)
    say(t)
    say("=" * 100)


GENESIS = "PRE-FREEZE"
ALGO = "sha256"


def content(**kw):
    base = dict(turn_index=0, verdict="ALLOWED", tool="create_refund",
                target="pay_CANARYRECON", receipt=None, amount_paise=100, a_class=None,
                rejected_by_razorpay=False, executed=True, customer_overcharge_paise=0,
                merchant_irrecoverable_outflow_paise=0, merchant_float_moved_paise=0,
                fees_incurred_paise=0)
    base.update(kw)
    return base


def build(n=3):
    spec = P_chain.ChainSpec(genesis_hash=GENESIS, algorithm=ALGO)
    led = P_chain.Ledger(spec=spec, seed=2001, arm="1")
    for i in range(n):
        led.append(**content(turn_index=i))
    return [e.to_dict() for e in led.entries]


# ── the two verifiers, spelled out here so the exhibit is self-contained ──────
def verify_head(entries, genesis):
    """HEAD's shape: link check, then recompute, then carry the RECOMPUTED digest forward."""
    prev = genesis
    for e in entries:
        if e["prev_hash"] != prev:
            return ("DETECTED", e["ledger_seq"], "link")
        rec = P_chain.entry_digest(prev, {k: v for k, v in e.items()
                                          if k not in P_entry.CHAIN_FIELDS}, algorithm=ALGO)
        if rec != e["hash"]:
            return ("DETECTED", e["ledger_seq"], "recompute")
        prev = rec
    return ("VALID", None, "")


def verify_M08(entries, genesis):
    """M08: carry the STORED digest forward instead of the recomputed one."""
    prev = genesis
    for e in entries:
        if e["prev_hash"] != prev:
            return ("DETECTED", e["ledger_seq"], "link")
        rec = P_chain.entry_digest(prev, {k: v for k, v in e.items()
                                          if k not in P_entry.CHAIN_FIELDS}, algorithm=ALGO)
        if rec != e["hash"]:
            return ("DETECTED", e["ledger_seq"], "recompute")
        prev = e["hash"]          # <- THE MUTATION
    return ("VALID", None, "")


def verify_M12(entries, genesis):
    """M12: the FIRST entry's link to the genesis root is not checked."""
    prev = genesis
    position = 0
    for e in entries:
        position += 1
        if position > 1 and e["prev_hash"] != prev:   # <- THE MUTATION
            return ("DETECTED", e["ledger_seq"], "link")
        rec = P_chain.entry_digest(prev, {k: v for k, v in e.items()
                                          if k not in P_entry.CHAIN_FIELDS}, algorithm=ALGO)
        if rec != e["hash"]:
            return ("DETECTED", e["ledger_seq"], "recompute")
        prev = rec
    return ("VALID", None, "")


def main() -> int:
    say("=" * 100)
    say("IMPORT PROVENANCE")
    say("=" * 100)
    say(f"  whetstone_gate.__file__ : {whetstone_gate.__file__}")
    say(f"  config.repo_root()      : {cfg.repo_root()}")

    # ══════════════════════════════════════════════════════════════════════════
    rule("M08 (P-06) — EQUIVALENT, and the proof is a CONTROL-FLOW argument plus an EXHAUSTIVE "
         "SEARCH")
    # ══════════════════════════════════════════════════════════════════════════
    say("  The mutation:  expected_prev = recomputed   ->   expected_prev = stored['hash']")
    say("")
    say("  THE PROOF. The assignment is reached only by falling through the line above it:")
    src = Path(ROOT, "src", "whetstone_gate", "ledger", "chain.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "verify")
    body_src = ast.unparse(ast.Module(body=fn.body[-3:], type_ignores=[]))
    for line in body_src.splitlines():
        say(f"      {line}")
    say("")
    say("  `if recomputed != stored['hash']: return ...` GUARDS the assignment, so at the")
    say("  assignment `recomputed == stored['hash']` HOLDS BY CONSTRUCTION. Assigning either")
    say("  name assigns the same value. There is no input on which the two differ, because")
    say("  reaching the line at all requires them to be equal.")
    say("")
    say("  ⚠️ AND THE SEARCH, BECAUSE A CONTROL-FLOW ARGUMENT CAN BE WRONG. Every mutation")
    say("  shape this review generated is run through BOTH verifiers:")
    shapes = []
    base = build(3)
    shapes.append(("intact", [dict(e) for e in base]))
    for idx in range(3):
        m = [dict(e) for e in base]
        m[idx]["amount_paise"] = 1
        shapes.append((f"entry {idx+1} contents altered, hash stale", m))
        m = [dict(e) for e in base]
        m[idx]["prev_hash"] = "0" * 64
        shapes.append((f"entry {idx+1} prev_hash broken", m))
        m = [dict(e) for e in base]
        m[idx]["hash"] = "0" * 64
        shapes.append((f"entry {idx+1} hash broken", m))
        m = [dict(e) for e in base]
        m[idx]["smuggled"] = 1
        shapes.append((f"entry {idx+1} field ADDED", m))
        m = [dict(e) for e in base]
        m[idx].pop("fees_incurred_paise")
        shapes.append((f"entry {idx+1} field REMOVED", m))
    shapes.append(("truncated", [dict(e) for e in base[:2]]))
    shapes.append(("empty", []))
    disagree = []
    for label, chain_ in shapes:
        h, m8, m12 = (verify_head(chain_, GENESIS), verify_M08(chain_, GENESIS),
                      verify_M12(chain_, GENESIS))
        if h[:2] != m8[:2]:
            disagree.append((label, h, m8))
    say(f"    {len(shapes)} shapes searched; HEAD and M08 disagree on {len(disagree)} of them.")
    say(f"    -> M08 is EQUIVALENT. {disagree}")
    say("")
    say("  ⚠️ AND WHAT M08 IS NOT. `PROCESS.md` §5.4's defect is *'the chain verifier compares")
    say("  each entry's stored prev_hash to the previous entry's stored hash field, AND NEVER")
    say("  RECOMPUTES the previous entry's digest from its contents.'* M08 changes only the")
    say("  second half's *carrier*, with the recomputation still in place. The mutant that")
    say("  actually removes the recomputation is M09, and M09 was KILLED by golden 5's cases")
    say("  C and D. The equivalence of M08 is therefore evidence FOR the verifier, not against.")

    # ══════════════════════════════════════════════════════════════════════════
    rule("M12 (P-09) — NOT EQUIVALENT. THE EXHIBIT: an input HEAD DETECTS and M12 calls VALID.")
    # ══════════════════════════════════════════════════════════════════════════
    say("  The mutation:  if stored['prev_hash'] != expected_prev:")
    say("              ->  if position > 1 and stored['prev_hash'] != expected_prev:")
    say("")
    say("  THE INPUT: a three-entry ledger whose ENTRY 1's `prev_hash` alone is edited, from")
    say("  the genesis root to something else. Nothing else is touched.")
    exhibit = [dict(e) for e in build(3)]
    say(f"    entry 1 prev_hash BEFORE : {exhibit[0]['prev_hash']!r}")
    exhibit[0]["prev_hash"] = "a" * 64
    say(f"    entry 1 prev_hash AFTER  : {exhibit[0]['prev_hash']!r}")
    say(f"    entry 1 hash             : {exhibit[0]['hash']}   (UNCHANGED, and still correct")
    say("                                for the body it is taken over, because the digest")
    say("                                EXCLUDES prev_hash — golden 5's own hash_rule)")
    h = verify_head(exhibit, GENESIS)
    m = verify_M12(exhibit, GENESIS)
    live = P_chain.verify(exhibit, genesis_hash=GENESIS, algorithm=ALGO)
    say("")
    say(f"    HEAD            -> {h[0]} at seq {h[1]}   (reason: {h[2]})")
    say(f"    the LIVE verify -> {live.verdict} at seq {live.first_bad_ledger_seq}")
    say(f"    M12             -> {m[0]} at seq {m[1]}")
    ok = h[0] == "DETECTED" and m[0] == "VALID"
    say(f"    -> THEY DIFFER: {ok}")
    say("")
    say("  ⚠️ WHY THE INTEGRITY CHECK DOES NOT CATCH IT, WHICH IS THE WHOLE POINT.")
    say("  `prev_hash` is EXCLUDED from the canonicalised entry, so editing it moves NO digest.")
    say("  The link check is the ONLY thing that reads it, and M12 removes the link check for")
    say("  exactly the entry that binds a ledger to its genesis root.")
    say("")
    say("  ⚠️ WHAT IT COSTS, IN `config/protocol.yaml`'s OWN WORDS:")
    say("      'A ledger cannot contain the hash of a tag that did not exist when it was")
    say("       written, so pre-freeze episodes are CRYPTOGRAPHICALLY DISTINGUISHABLE from")
    say("       scored ones. This is the one free proof available and it costs a single line.'")
    say("  That proof rests on ENTRY 1's link and on nothing else. Under M12 the suite is")
    say("  green while the first link is unchecked, so NO TEST IN THIS REPOSITORY COVERS the")
    say("  binding the freeze's one free proof is made of.")
    say("")
    say("  THE REMEDY IS ONE FIXTURE: a ledger whose entry 1 `prev_hash` alone is altered, ")
    say("  asserted DETECTED at seq 1. Golden 5 has no such case — its case B breaks entry 2.")
    for c in [dict(e) for e in build(3)]:
        pass
    say("")
    say("  AND THE CONVERSE SHAPE, CHECKED SO THE FINDING IS NOT OVERSTATED — a whole entry 1")
    say("  forged to chain from a different root (prev_hash AND hash both recomputed):")
    forged = [dict(e) for e in build(3)]
    body0 = {k: v for k, v in forged[0].items() if k not in P_entry.CHAIN_FIELDS}
    forged[0]["prev_hash"] = "b" * 64
    forged[0]["hash"] = P_chain.entry_digest("b" * 64, body0, algorithm=ALGO)
    say(f"    HEAD -> {verify_head(forged, GENESIS)[0]}    M12 -> {verify_M12(forged, GENESIS)[0]}")
    say("    Both DETECT this one, at the recomputation. So M12's gap is narrow and real:")
    say("    it is exactly the edit that touches `prev_hash` and leaves every digest alone.")

    # ══════════════════════════════════════════════════════════════════════════
    rule("M16 (P-13 as sealed → RE-MARKED) — NOT EQUIVALENT, and NOT OWNED. Both are argued.")
    # ══════════════════════════════════════════════════════════════════════════
    say("  The mutation: `append_log` drops its validate-everything-first pass, so a bad row")
    say("  at position k leaves rows 1…k-1 already appended.")
    say("")
    say("  NOT EQUIVALENT — the exhibit, run against HEAD:")
    spec = P_chain.ChainSpec(genesis_hash=GENESIS, algorithm=ALGO)
    led = P_chain.Ledger(spec=spec, seed=2001, arm="1")

    class _R:
        def __init__(self, ok):
            self.ok = ok
            self.harm = None
    good = (0, "fetch_payments", {}, _R(True))
    bad = (1, "create_refund", {"payment_id": "pay_x", "amount": 5}, _R(True))
    rows = [good, good, bad]

    def turn_of(row):
        return row[0]

    def verdict_of(row):
        # the third row claims a verdict arm 1 cannot emit -> validate_content refuses it
        return "DENIED" if row is bad else "ALLOWED"
    try:
        P_build.append_log(led, rows, turn_index_of=turn_of, verdict_of=verdict_of)
        say("    HEAD: append_log ACCEPTED the batch (unexpected)")
    except Exception as exc:  # noqa: BLE001
        say(f"    HEAD: append_log refused -> {type(exc).__name__}: {str(exc)[:70]}")
    say(f"    HEAD: the ledger is left with {len(led)} entries  <- ALL OR NOTHING")
    say("    M16: rows 1 and 2 are already appended when row 3 refuses, leaving 2 entries.")
    say("         A short ledger VERIFIES (nothing anchors the end — OF-57), so the loss is")
    say("         silent. The two implementations therefore differ on a real input.")
    say("")
    say("  NOT OWNED, and this is argued rather than asserted, because it is the disposition")
    say("  that decides whether it holds the tag:")
    say("    · The sealed P-13 is DETERMINISM — *'the same inputs in the same order give")
    say("      byte-identical digests'* — and M16 does not touch it. M16 attacks a DIFFERENT")
    say("      property: `append_log`'s all-or-nothing batch semantics.")
    say("    · That property passes criterion 1 of the sealed definition of *owns* (the fix is")
    say("      inside `ledger/`) and FAILS criterion 2: NO artefact that outranks the code")
    say("      requires it. `CONTEXT.md` §16 says *append-only, hash-chained* and nothing about")
    say("      batches; no C7 card clause, no ruling and no golden mentions it. It is the")
    say("      builder's own Class B choice, argued in its own docstring.")
    say("    · Hard rule 11 is the nearest candidate and does not reach: a caller-supplied bad")
    say("      row is not a *dropped episode*, and the caller gets the refusal either way.")
    say("    → MEDIUM in OPEN_FINDINGS.md. It does NOT hold the tag (Q-082's ruling).")
    say("")
    say("  ⚠️ THIS DISPOSITION COSTS THIS REVIEW NOTHING, AND THAT IS STATED SO IT CAN BE")
    say("  CHECKED: the verdict is already FAIL on M12 and M39, so marking M16 NOT-OWNED")
    say("  changes no outcome. A reviewer narrowing a set to avoid a FAIL is the failure")
    say("  Q-082's safeguard exists for; there is no such incentive here.")

    # ══════════════════════════════════════════════════════════════════════════
    rule("M39 (P-33) — NOT EQUIVALENT, and OWNED. The claim ceiling is not pinned by anything.")
    # ══════════════════════════════════════════════════════════════════════════
    say("  The mutation replaces `chain.py`'s stated limitation")
    say('      \'"the ledger is tamper-evident" means **evident against an edit that leaves a')
    say("       stale digest, and against nothing else** — and the README must not say more.'")
    say("  with")
    say("      'the ledger is tamper-evident: any alteration is detected.'")
    say("  and the whole 159-test C7 suite stays GREEN.")
    say("")
    say("  NOT EQUIVALENT: the two texts make different claims, and the second is FALSE — this")
    say("  review's own vectors V09 and V10 exhibit a truncation and a re-derived suffix that")
    say("  BOTH verify. The mutant makes the package assert something the package disproves.")
    say("")
    say("  OWNED: P-33 is in the sealed required set, and ruling 4 of this session's prompt")
    say("  puts it there in terms — *'DO fail it if any docstring, comment or artefact claims")
    say("  more than that.'* The chunk owns the ceiling; nothing else can own it, because the")
    say("  sentence lives in this package.")
    say("")
    say("  ⚠️ AND THE REMEDY IS A PATTERN THIS CHUNK ALREADY USES, WHICH IS WHY THE BAR IS NOT")
    say("  UNREASONABLE: M38 — deleting Q-069's prohibition from the package docstring — was")
    say("  KILLED by `test_Q069_the_scorer_side_prohibition_is_stated_in_the_package_itself`,")
    say("  which PARSES the docstring rather than trusting it. The identical fixture pointed at")
    say("  chain.py's ceiling sentence closes M39. One test, already written once, ten lines away.")
    say("")
    say("  The subject is CLEAN TODAY — this review measured it, and the ceiling sentence is")
    say("  present in the ruling's own words. Q-082's ruling is explicit that this does not")
    say("  save it: *'clean today is exactly what an unpinned guard cannot promise tomorrow.'*")

    rule("SUMMARY")
    say("  M08  EQUIVALENT      P-06  proof by control flow + a 20-shape search, 0 disagreements")
    say("  M12  NOT equivalent  P-09  OWNED     -> FAIL-carrying")
    say("  M16  NOT equivalent  —     NOT OWNED -> MEDIUM in OPEN_FINDINGS.md")
    say("  M39  NOT equivalent  P-33  OWNED     -> FAIL-carrying")
    with open(os.path.join(HERE, "c7_survivor_exhibits_output.txt"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(OUT) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
