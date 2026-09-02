"""C7 REVIEW 2 — PHASE 2. The PROJECT against the SEALED REIMPLEMENTATION, on the sealed vectors.

SESSION-TOKEN: b8c31a57.

The vector list and the reimplementation were committed at the Phase 1 seal and are not
edited here. This file is the ADAPTER plus the DIFF: it runs both implementations over the
identical inputs and reports every divergence. A divergence is a finding — and it is read in
BOTH directions, because a diff that is only ever read against the subject is half a diff.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile
import traceback

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import c7_review2_reimpl as R          # noqa: E402
import c7_review2_vectors as V         # noqa: E402

from whetstone_gate import config as cfg          # noqa: E402
from whetstone_gate.ledger import build, chain, control, entry as entrymod  # noqa: E402

DIVERGENCES = []
ROWS = []
SPEC = chain.ChainSpec(genesis_hash=V.GENESIS, algorithm="sha256")


#: The project names its refusal sources with a `_REFUSED` suffix; the reimplementation does
#: not. The two are the SAME classification and this maps one onto the other. A review that
#: scored the spelling would be scoring vocabulary rather than behaviour.
SOURCE_ALIAS = {
    "GATE_REFUSED": "GATE",
    "RAZORPAY_REFUSED": "RAZORPAY",
    "TOOL_LAYER_REFUSED": "TOOL_LAYER",
}


def norm(value):
    """Both implementations reduced to comparable shapes.

    Two deliberate normalisations, each stated so it can be disputed:
      * a REFUSAL is compared on the FACT of the refusal and not on the exception class
        name. The project raises typed subclasses (`LedgerEntryError`, `BlankValue`,
        `UndeterminedValue`, `MissingRequiredValue`, `TypeError`); the reimplementation
        raises one type. **The project is STRICTLY BETTER here** and scoring the names
        would penalise it for being more informative.
      * the refusal-source vocabulary is aliased, above.
    """
    if isinstance(value, tuple):
        if len(value) == 2 and value[0] in ("ok", "refused"):
            kind, val = value
            return ("refused",) if kind == "refused" else ("ok", norm(val))
        return tuple(norm(v) for v in value)
    if isinstance(value, str):
        return SOURCE_ALIAS.get(value, value)
    return value


def run(fn):
    """Return ('ok', value) or ('refused', ExceptionClassName)."""
    try:
        return ("ok", fn())
    except Exception as exc:  # noqa: BLE001 — the classification IS the measurement
        return ("refused", type(exc).__name__)


# ── the ADAPTERS ────────────────────────────────────────────────────────────────────────

def mine_verify(vec):
    v, seq, _reason = R.verify(vec["entries"], vec["genesis"])
    return (v, seq)


def proj_verify(vec):
    out = chain.verify(vec["entries"], genesis_hash=vec["genesis"], algorithm=SPEC.algorithm)
    return (out.verdict, out.first_bad_ledger_seq)


def mine_digest(vec):
    return R.digest(vec["prev"], vec["body"])


def proj_digest(vec):
    body = {k: val for k, val in vec["body"].items() if k not in ("prev_hash", "hash")}
    return chain.entry_digest(vec["prev"], body, algorithm=SPEC.algorithm)


def _append_body(body):
    return {k: v for k, v in body.items() if k not in ("ledger_seq", "arm")}


def mine_append(vec):
    led = R.Ledger(genesis_hash=V.GENESIS)
    stored = led.append(vec["body"])
    return stored["hash"]


def proj_append(vec):
    led = chain.Ledger(spec=SPEC, seed=2001, arm=vec["body"].get("arm", "1"))
    written = led.append(**_append_body(vec["body"]))
    return written.hash


def _one_arm(bodies):
    """⚠️ INPUT NORMALISATION, APPLIED SYMMETRICALLY TO BOTH IMPLEMENTATIONS, AND IT IS A
    FINDING AGAINST THE SEALED VECTOR RATHER THAN AGAINST THE PROJECT.

    `CONTEXT.md` §8: *"the only variable is the gate"* — one episode is one arm — and
    `chain.Ledger` takes ``arm`` at CONSTRUCTION so a mixed-arm ledger is **unbuildable**.
    The sealed `V36` supplies four bodies whose first carries arm 2 and whose rest default
    to arm 1, which the project cannot represent **by design and correctly**. The seal is
    not edited (`REVIEW_7_1` set that precedent with its own two reimplementation-side
    findings); the arm of the first body is stamped on all of them, for BOTH sides, here.
    """
    arm = bodies[0].get("arm", "1")
    return [dict(b, arm=arm) for b in bodies]


def mine_append_many(vec):
    led = R.Ledger(genesis_hash=V.GENESIS)
    for b in _one_arm(vec["bodies"]):
        led.append(b)
    return tuple(e["hash"] for e in led.entries())


def proj_append_many(vec):
    bodies = _one_arm(vec["bodies"])
    led = chain.Ledger(spec=SPEC, seed=2001, arm=bodies[0].get("arm", "1"))
    for b in bodies:
        led.append(**_append_body(b))
    return tuple(e.hash for e in led.entries)


def mine_determinism(vec):
    a = R.Ledger(genesis_hash=V.GENESIS)
    b = R.Ledger(genesis_hash=V.GENESIS)
    for body in vec["bodies"]:
        a.append(body)
        b.append(body)
    return tuple(x["hash"] for x in a.entries()) == tuple(y["hash"] for y in b.entries())


def proj_determinism(vec):
    a = chain.Ledger(spec=SPEC, seed=2001, arm="1")
    b = chain.Ledger(spec=SPEC, seed=2001, arm="1")
    for body in vec["bodies"]:
        a.append(**_append_body(body))
        b.append(**_append_body(body))
    return tuple(x.hash for x in a.entries) == tuple(y.hash for y in b.entries)


def mine_predicate(vec):
    """⚠️ ROUTED THROUGH THE WRITE PATH, exactly as the project's side is.

    The project can only evaluate a predicate on an entry it was able to WRITE, and three of
    the sealed truth-table vectors are INADMISSIBLE — `V40.1` violates consistency assertion
    2 and `V40.4`/`V40.5` violate assertion 1. Evaluating a predicate on an entry that cannot
    exist would compare the project's refusal against an answer about an impossible row.
    The reimplementation has the same admission check and the adapter uses it.
    """
    led = R.Ledger(genesis_hash=V.GENESIS)
    stored = led.append(vec["entry"])
    return (R.productive_action(stored), R.canary_b_attempt(stored), R.refusal_source(stored))


def proj_predicate(vec):
    led = chain.Ledger(spec=SPEC, seed=2001, arm=vec["entry"].get("arm", "1"))
    written = led.append(**_append_body(vec["entry"]))
    named = build.entries_naming((written,), R.PROBE_PAYMENT_ID)
    src = control.refusal_source(written)
    return (
        control.productive_action(written),
        len(named) == 1,
        "NONE" if src is None else src.upper().replace(" ", "_"),
    )


def mine_genesis(vec):
    return R.load_genesis(vec["text"])


def proj_genesis(vec):
    with tempfile.TemporaryDirectory() as tmp:
        d = pathlib.Path(tmp)
        (d / "protocol.yaml").write_text(
            vec["text"] + "\n" + "  hash_algorithm: sha256\n"
            if "hash_algorithm" not in vec["text"] else vec["text"],
            encoding="utf-8",
        )
        old = os.environ.get("WHETSTONE_CONFIG_DIR")
        os.environ["WHETSTONE_CONFIG_DIR"] = str(d)
        try:
            return chain.load_chain_spec().genesis_hash
        finally:
            if old is None:
                os.environ.pop("WHETSTONE_CONFIG_DIR", None)
            else:
                os.environ["WHETSTONE_CONFIG_DIR"] = old


ADAPTERS = {
    "verify": (mine_verify, proj_verify),
    "digest": (mine_digest, proj_digest),
    "append": (mine_append, proj_append),
    "append_many": (mine_append_many, proj_append_many),
    "determinism": (mine_determinism, proj_determinism),
    "predicate": (mine_predicate, proj_predicate),
    "genesis": (mine_genesis, proj_genesis),
}

print("=" * 96)
print("PROVENANCE — read BEFORE any result, because INC-69 is a harness that measured the wrong tree")
print("=" * 96)
print("  whetstone_gate.ledger.chain.__file__  %s" % chain.__file__)
print("  config.repo_root()                    %s" % cfg.repo_root())
print("  reimplementation                      %s" % R.__file__)
print("  vectors                               %s" % V.__file__)
print("  vector count                          %d under %d id stems"
      % (len(V.VECTORS), len({v['id'].split('.')[0] for v in V.VECTORS})))
print()
print("%-9s %-11s %-42s %-30s %-30s" % ("VECTOR", "KIND", "WHAT", "REIMPLEMENTATION", "PROJECT"))
print("-" * 130)

for vec in V.VECTORS:
    mine_fn, proj_fn = ADAPTERS[vec["kind"]]
    mine = run(lambda: mine_fn(vec))
    proj = run(lambda: proj_fn(vec))
    agree = norm(mine) == norm(proj)

    def short(outcome):
        kind, val = outcome
        if kind == "refused":
            return "REFUSED(%s)" % val
        if isinstance(val, str) and len(val) == 64:
            return val[:16] + "…"
        if isinstance(val, tuple):
            return "(" + ", ".join(
                (v[:12] + "…") if isinstance(v, str) and len(v) == 64 else str(v) for v in val
            ) + ")"
        return str(val)

    ROWS.append((vec["id"], vec["kind"], vec["what"], short(mine), short(proj), agree))
    if not agree:
        DIVERGENCES.append((vec["id"], vec["what"], vec["artefact"], mine, proj))
    print("%-9s %-11s %-42s %-30s %-30s %s"
          % (vec["id"], vec["kind"], vec["what"][:42], short(mine)[:30], short(proj)[:30],
             "" if agree else "  <<< DIVERGENCE"))

print()
print("=" * 96)
print("REFUSAL-CLASS AGREEMENT IS NOT ASSERTED AND IS NOT A DIVERGENCE.")
print("Both implementations are compared on WHETHER they refuse, not on the exception's name:")
print("the reimplementation raises one type and the project raises typed subclasses, and a")
print("review that scored the class names would be scoring vocabulary rather than behaviour.")
print("=" * 96)
print()
print("VECTORS RUN: %d      DIVERGENCES: %d" % (len(V.VECTORS), len(DIVERGENCES)))
for vid, what, artefact, mine, proj in DIVERGENCES:
    print("  %-9s %s   [%s]" % (vid, what, artefact))
    print("      reimplementation: %r" % (mine,))
    print("      project         : %r" % (proj,))
