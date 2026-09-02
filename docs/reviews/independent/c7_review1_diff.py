"""C7 REVIEW 1 (`472cdc4b`) — PHASE 2. THE DIFF: the project's ledger against the reviewer's.

Run:  `PYTHONPATH=src python docs/reviews/independent/c7_review1_diff.py`

`docs/reviews/README.md`: *"`independent/c<N>_reimpl_diff.txt` — Phase 2's diff of the project's
output against the reimplementation, over the reviewer's own ≥20 vectors. **Any divergence is a
finding.**"* **Forty-five** vectors under forty-two id numbers (`V01`…`V42`, with `V36` split
into `V36a`…`V36d`, one per harm component), sealed at `f1ccde1` before
`src/whetstone_gate/ledger/` was opened. ⚠️ **The sealed `c7_vectors.py` header says *FORTY-TWO*,
which counts id numbers and not entries; it is NOT edited, and the count is corrected here and in
`REVIEW_7_1.md` §4 instead.**

⚠️ **THE IMPORT PROVENANCE IS PRINTED AT THE HEAD OF EVERY RUN** — `whetstone_gate.__file__` and
`config.repo_root()` — because `INCIDENTS.md` INC-64 / OF-139 records a harness that imported the
LIVE package while it believed it was importing a clone, and every mutant then reported SURVIVED.
"""

from __future__ import annotations

import json
import os
import sys
import traceback

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
sys.path.insert(0, os.path.join(ROOT, "src"))

import c7_reimpl as R  # noqa: E402
import c7_vectors as V  # noqa: E402

import whetstone_gate  # noqa: E402
from whetstone_gate import config as cfg  # noqa: E402
from whetstone_gate.ledger import chain as P_chain  # noqa: E402
from whetstone_gate.ledger import control as P_control  # noqa: E402
from whetstone_gate.ledger import entry as P_entry  # noqa: E402

GENESIS = "PRE-FREEZE"
ALGO = "sha256"

divergences: list[str] = []
lines: list[str] = []


def say(text: str = "") -> None:
    lines.append(text)
    print(text)


def banner() -> None:
    say("=" * 100)
    say("IMPORT PROVENANCE  (INC-64 / OF-139: print it or the run is worthless)")
    say("=" * 100)
    say(f"  whetstone_gate.__file__ : {whetstone_gate.__file__}")
    say(f"  config.repo_root()      : {cfg.repo_root()}")
    say(f"  reviewer reimpl         : {R.__file__}")
    say(f"  sys.executable          : {sys.executable}")
    say("")


def project_chain(blocks: list[dict], arm: str = "1") -> list[dict]:
    """Build the chain with the PROJECT's writer and return the stored dicts."""
    spec = P_chain.ChainSpec(genesis_hash=GENESIS, algorithm=ALGO)
    ledger = P_chain.Ledger(spec=spec, seed=2001, arm=arm)
    for b in blocks:
        kwargs = {k: v for k, v in b.items() if k != "arm"}
        ledger.append(**kwargs)
    return [e.to_dict() for e in ledger.entries]


def mine_chain(blocks: list[dict], arm: str = "1") -> list[dict]:
    """Build the chain with the REVIEWER's writer and return the stored dicts."""
    led = R.Ledger(genesis_hash_reader=lambda: GENESIS)
    for b in blocks:
        led.append({**b, "arm": arm})
    return list(led.entries)


def apply_mutation(entries: list[dict], mutate: dict | None, arm: str) -> list[dict]:
    if mutate is None:
        return entries
    out = [dict(e) for e in entries]
    op = mutate["op"]
    if op == "set":
        out[mutate["index"]][mutate["key"]] = mutate["value"]
    elif op == "add":
        out[mutate["index"]][mutate["key"]] = mutate["value"]
    elif op == "del":
        out[mutate["index"]].pop(mutate["key"], None)
    elif op == "truncate":
        out = out[: mutate["keep"]]
    elif op == "rederive_suffix":
        out = out[: mutate["keep"]]
        # re-chain a fresh entry onto the truncated tail, both ways, from the kept head
        prev = out[-1]["hash"] if out else GENESIS
        fresh = {"ledger_seq": len(out) + 1, "arm": arm, **{k: v for k, v in mutate["block"].items() if k != "arm"}}
        ordered = {k: fresh[k] for k in R.SCHEMA_15}
        ordered["prev_hash"] = prev
        ordered["hash"] = R.entry_hash(prev, ordered)
        out.append(ordered)
    else:
        raise AssertionError(op)
    return out


def run_chain_vector(v: dict) -> None:
    arm = v["blocks"][0]["arm"] if v["blocks"] else "1"
    tag = f"{v['id']} {v['name']}"

    try:
        p_entries = project_chain(v["blocks"], arm)
        p_err = None
    except Exception as exc:  # noqa: BLE001
        p_entries, p_err = [], f"{type(exc).__name__}: {exc}"
    try:
        m_entries = mine_chain(v["blocks"], arm)
        m_err = None
    except Exception as exc:  # noqa: BLE001
        m_entries, m_err = [], f"{type(exc).__name__}: {exc}"

    if (p_err is None) != (m_err is None):
        say(f"  {tag}")
        say(f"      WRITE: project={p_err or 'ok'}   reviewer={m_err or 'ok'}   <- DIVERGENCE")
        divergences.append(f"{v['id']} write: project={p_err or 'ok'} reviewer={m_err or 'ok'}")
        return
    if p_err is not None:
        say(f"  {tag}")
        say(f"      both refused the WRITE: {p_err[:90]}")
        return

    p_hashes = [e["hash"] for e in p_entries]
    m_hashes = [e["hash"] for e in m_entries]
    same_digests = p_hashes == m_hashes

    p_mut = apply_mutation(p_entries, v["mutate"], arm)
    m_mut = apply_mutation(m_entries, v["mutate"], arm)

    pv = P_chain.verify(p_mut, genesis_hash=GENESIS, algorithm=ALGO)
    mv = R.verify(m_mut, GENESIS)
    p_res = (pv.verdict, pv.first_bad_ledger_seq)
    m_res = mv.as_tuple()

    exp = v["expect_verify"]
    agree = p_res == m_res
    ok_exp = (exp == "RECORD_BEHAVIOUR") or (p_res == tuple(exp) if isinstance(exp, (list, tuple)) else False)

    say(f"  {tag}")
    say(f"      digests identical      : {same_digests}"
        + ("" if same_digests else f"   project={p_hashes}  reviewer={m_hashes}"))
    say(f"      verify project/reviewer: {p_res} / {m_res}   expected {exp}")
    if not same_digests:
        divergences.append(f"{v['id']} digests differ")
    if not agree:
        divergences.append(f"{v['id']} verdicts differ: project {p_res} reviewer {m_res}")
        say("      <- DIVERGENCE (the two implementations disagree)")
    if not ok_exp and exp != "RECORD_BEHAVIOUR":
        divergences.append(f"{v['id']} project {p_res} != sealed expectation {exp}")
        say("      <- MISSES THE SEALED EXPECTATION")
    if v.get("is_stated_limitation"):
        say(f"      (VALID here is the STATED LIMITATION {v['is_stated_limitation']}, not a defect)")

    if v["id"] == "V11":
        e = p_mut[0]
        body = {k: val for k, val in e.items() if k not in ("prev_hash", "hash")}
        strict = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        import hashlib
        alt = hashlib.sha256((GENESIS + strict).encode("utf-8")).hexdigest()
        say(f"      ensure_ascii=False digest (shipped): {e['hash']}")
        say(f"      ensure_ascii=True  digest (Q-053 option 2, REJECTED): {alt}")
        say(f"      they differ on REACHABLE input: {alt != e['hash']}")
        if alt == e["hash"]:
            divergences.append("V11: the two canonicalisations did not differ")
    if v["id"] in ("V14", "V15"):
        say(f"      digest: {p_hashes[0]}")


def run_append_vector(v: dict) -> None:
    block = v["block"]
    arm = block["arm"]
    tag = f"{v['id']} {v['name']}"

    def attempt(fn):
        try:
            fn()
            return "ACCEPT", None
        except Exception as exc:  # noqa: BLE001
            return "REFUSE", f"{type(exc).__name__}: {exc}"

    p_res, p_msg = attempt(lambda: project_chain([block], arm))
    m_res, m_msg = attempt(lambda: mine_chain([block], arm))

    say(f"  {tag}")
    say(f"      project={p_res}  reviewer={m_res}  expected={v['expect']}")
    if p_res != m_res:
        divergences.append(f"{v['id']} project {p_res} reviewer {m_res}")
        say(f"      <- DIVERGENCE   project: {(p_msg or '')[:80]}   reviewer: {(m_msg or '')[:80]}")
    if p_res != v["expect"]:
        divergences.append(f"{v['id']} project {p_res} != sealed expectation {v['expect']}")
        say("      <- MISSES THE SEALED EXPECTATION")
    if p_res == "REFUSE":
        say(f"      refusal: {(p_msg or '')[:150]}")


def run_derive_vector(v: dict) -> None:
    block = v["block"]
    arm = block["arm"]
    tag = f"{v['id']} {v['name']}"
    p_entries = project_chain([block], arm)
    stored = p_entries[0]
    typed = P_entry.LedgerEntry.from_dict(stored)

    p_src = P_control.refusal_source(typed)
    m_src = R.refusal_source(stored)
    # the project spells the three sources with a _REFUSED suffix; map for comparison
    spelling = {"GATE_REFUSED": "GATE", "RAZORPAY_REFUSED": "RAZORPAY",
                "TOOL_LAYER_REFUSED": "TOOL_LAYER", None: None}
    p_prod = P_control.productive_action(typed)
    m_prod = R.productive_action(stored)

    say(f"  {tag}")
    say(f"      refusal_source project={p_src!r} -> {spelling[p_src]!r}   reviewer={m_src!r}")
    say(f"      productive     project={p_prod}   reviewer={m_prod}")
    if spelling[p_src] != m_src:
        divergences.append(f"{v['id']} refusal_source disagrees")
        say("      <- DIVERGENCE")
    if p_prod != m_prod:
        divergences.append(f"{v['id']} productive_action disagrees")
        say("      <- DIVERGENCE")
    if "expect_refusal_source" in v and spelling[p_src] != v["expect_refusal_source"]:
        divergences.append(f"{v['id']} refusal_source != sealed expectation")
        say("      <- MISSES THE SEALED EXPECTATION")
    if "expect_productive" in v and p_prod != v["expect_productive"]:
        divergences.append(f"{v['id']} productive != sealed expectation")
        say("      <- MISSES THE SEALED EXPECTATION")
    if "expect_canary_a" in v:
        mine_a = R.canary_a_breach(stored, V.PER_ACTION_CAP_PAISE)
        say(f"      CANARY-A (reviewer, §10.1) = {mine_a}   expected {v['expect_canary_a']}")
        if mine_a != v["expect_canary_a"]:
            divergences.append(f"{v['id']} CANARY-A != sealed expectation")
    if v.get("expect_canary_b_counted"):
        from whetstone_gate.ledger import build as P_build
        reached = P_build.entries_naming([typed], V.PROBE_ID)
        say(f"      CANARY-B: project entries_naming counts a {typed.verdict} entry -> "
            f"{len(reached)}   reviewer -> {R.canary_b_reach([stored])}")
        if len(reached) != 1 or R.canary_b_reach([stored]) != 1:
            divergences.append(f"{v['id']} CANARY-B did not count a blocked entry")
    say(f"      digest: {stored['hash']}")
    return stored


def main() -> int:
    banner()
    say("=" * 100)
    say(f"THE {len(V.VECTORS)} SEALED VECTOR ENTRIES (V01..V42, V36 split four ways), PROJECT versus REVIEWER")
    say("=" * 100)

    derived: dict[str, dict] = {}
    for v in V.VECTORS:
        kind = v["kind"]
        if kind == "chain":
            run_chain_vector(v)
        elif kind == "append":
            run_append_vector(v)
        elif kind == "derive":
            derived[v["id"]] = run_derive_vector(v)
        elif kind == "genesis":
            tag = f"  {v['id']} {v['name']}"
            say(tag)
            if v["genesis"] is None:
                try:
                    P_chain.ChainSpec(genesis_hash=None, algorithm=ALGO)
                    spec_made = True
                except Exception:  # noqa: BLE001
                    spec_made = False
                try:
                    R.verify([], None)
                    m_refused = False
                except R.LedgerRefusal:
                    m_refused = True
                # the real path: a Config whose ledger: block has no genesis_hash
                import whetstone_gate.config as C
                from pathlib import Path as _Path
                probes = {
                    "key absent": {"ledger": {"hash_algorithm": "sha256"}},
                    "ledger: block absent": {},
                    "blank value": {"ledger": {"genesis_hash": "", "hash_algorithm": "sha256"}},
                    "null value": {"ledger": {"genesis_hash": None, "hash_algorithm": "sha256"}},
                    "TODO_ sentinel": {"ledger": {"genesis_hash": "TODO_C14",
                                                  "hash_algorithm": "sha256"}},
                }
                all_refused = True
                for label, data in probes.items():
                    bad = C.Config(name="protocol",
                                   path=_Path(ROOT) / "config" / "protocol.yaml", data=data)
                    try:
                        spec = P_chain.load_chain_spec(bad)
                        all_refused = False
                        say(f"      {label:<22} -> *** DEFAULTED to {spec.genesis_hash!r} ***")
                    except Exception as exc:  # noqa: BLE001
                        say(f"      {label:<22} -> HARD REFUSAL  {type(exc).__name__}: "
                            f"{str(exc)[:90]}")
                p_refused = all_refused
                say(f"      reviewer verify with genesis None -> "
                    f"{'HARD REFUSAL' if m_refused else '*** DEFAULTED ***'}")
                if not p_refused:
                    divergences.append("V38 a missing genesis_hash did not refuse")
            else:
                a = project_chain([V.content()], "1")[0]["hash"]
                spec = P_chain.ChainSpec(genesis_hash=v["genesis"], algorithm=ALGO)
                led = P_chain.Ledger(spec=spec, seed=2001, arm="1")
                b = led.append(**{k: val for k, val in V.content().items() if k != "arm"}).hash
                say(f"      PRE-FREEZE root : {a}")
                say(f"      other root      : {b}")
                say(f"      every digest moves: {a != b}")
                if a == b:
                    divergences.append("V39 the genesis root did not enter the digest")
        elif kind == "truthtable":
            say(f"  {v['id']} {v['name']}")
            say("      allowed executed rejected | expected | reviewer | project(writable?)")
            for allowed, executed, rejected, expected in V.truth_table():
                stored = {
                    "verdict": "ALLOWED" if allowed else "DENIED",
                    "executed": executed,
                    "rejected_by_razorpay": rejected,
                }
                mine = R.productive_action(stored)
                writable = True
                try:
                    block = V.content(
                        arm="4",
                        verdict="ALLOWED" if allowed else "DENIED",
                        executed=executed,
                        rejected_by_razorpay=rejected,
                    )
                    project_chain([block], "4")
                except Exception:  # noqa: BLE001
                    writable = False
                proj = None
                if writable:
                    e = project_chain(
                        [V.content(arm="4", verdict="ALLOWED" if allowed else "DENIED",
                                   executed=executed, rejected_by_razorpay=rejected)], "4")[0]
                    proj = P_control.productive_action(P_entry.LedgerEntry.from_dict(e))
                say(f"      {str(allowed):<8}{str(executed):<9}{str(rejected):<9}| "
                    f"{str(expected):<9}| {str(mine):<9}| "
                    f"{'not writable' if not writable else proj}")
                if mine != expected:
                    divergences.append(f"truth table {(allowed, executed, rejected)} reviewer wrong")
                if writable and proj != expected:
                    divergences.append(f"truth table {(allowed, executed, rejected)} project wrong")
        say("")

    # V32 vs V33: the Q-062 before/after, on the reviewer's own vectors
    say("=" * 100)
    say("V32 versus V33 — the row that WAS byte-identical to success")
    say("=" * 100)
    a, b = derived["V32"], derived["V33"]
    diffs = [k for k in R.SCHEMA_15 if a.get(k) != b.get(k)]
    say(f"  TOOL-LAYER-REFUSED digest : {a['hash']}")
    say(f"  EXECUTED-HARMLESS  digest : {b['hash']}")
    say(f"  content fields that differ: {diffs}")
    if diffs != ["executed"] or a["hash"] == b["hash"]:
        divergences.append("V32/V33 do not differ in exactly `executed`")

    say("")
    say("=" * 100)
    say("RESULT")
    say("=" * 100)
    if divergences:
        say(f"  {len(divergences)} DIVERGENCE(S):")
        for d in divergences:
            say(f"    - {d}")
    else:
        say(f"  ZERO divergences across all {len(V.VECTORS)} vectors.")

    with open(os.path.join(HERE, "c7_reimpl_diff.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return 1 if divergences else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        raise SystemExit(3)
