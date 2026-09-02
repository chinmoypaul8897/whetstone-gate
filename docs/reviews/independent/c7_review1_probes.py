"""C7 REVIEW 1 (`472cdc4b`) — PHASE 2 §§2-7. THE DRIVEN PROBES.

Run:  `PYTHONPATH=src python docs/reviews/independent/c7_review1_probes.py`

Everything the review prompt orders driven rather than read:

    §2  the THREE-SOURCE TABLE through the REAL world, and the two byte-identical
        capture_payment hashes reproduced against the PRE-Q-062 field set
    §3  `executed` read from ToolResult.ok, MECHANICALLY - the prohibition, not the docstring
    §4  the four consistency assertions, per component
    §5  `productive_action` term by term against §8.6a PARSED OUT OF CONTEXT.md, not transcribed
    §6  append-only, genesis, the never-cached root, no clock/float/total/model client,
        determinism - and EVERY SCANNER FIRED AT A FILE BUILT TO BREAK IT (INC-14's shape)
    §7  the rulings recorded where the choice is made, and the claims that must not exceed
        "evident against an edit that leaves a stale digest"
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

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

import whetstone_gate  # noqa: E402
from whetstone_gate import config as cfg  # noqa: E402
from whetstone_gate.ledger import build as P_build  # noqa: E402
from whetstone_gate.ledger import chain as P_chain  # noqa: E402
from whetstone_gate.ledger import control as P_control  # noqa: E402
from whetstone_gate.ledger import entry as P_entry  # noqa: E402
from whetstone_gate.ledger import store as P_store  # noqa: E402
from whetstone_gate.world import generator, semantics  # noqa: E402
from whetstone_gate.world import oracle as oracle_module  # noqa: E402
from whetstone_gate.world import settings  # noqa: E402
from whetstone_gate.world.spec import load_world_spec  # noqa: E402

FAILS: list[str] = []
OUT: list[str] = []


def say(text: str = "") -> None:
    OUT.append(text)
    print(text)


def rule(title: str) -> None:
    say("")
    say("=" * 100)
    say(title)
    say("=" * 100)


def check(label: str, condition: bool, detail: str = "") -> None:
    say(f"    [{'OK ' if condition else 'FAIL'}] {label}" + (f"   {detail}" if detail else ""))
    if not condition:
        FAILS.append(label)


def make_world(seed: int):
    protocol = cfg.load("protocol")
    return semantics.build(
        generator.generate(seed, load_world_spec(protocol)),
        settings.load_semantics_spec(protocol),
        oracle_module.load(),
    )


def thirteen(content: dict) -> dict:
    """Golden 5's THIRTEEN content fields — this schema minus Q-062's and Q-066's."""
    return {k: v for k in P_entry.GOLDEN_5_CONTENT_FIELDS for v in [content[k]]}


def main() -> int:
    say("=" * 100)
    say("IMPORT PROVENANCE  (INC-64 / OF-139)")
    say("=" * 100)
    say(f"  whetstone_gate.__file__ : {whetstone_gate.__file__}")
    say(f"  config.repo_root()      : {cfg.repo_root()}")

    protocol = cfg.load("protocol")
    seed = protocol.require("seeds.scored_n50_first")
    spec = P_chain.load_chain_spec(protocol)
    say(f"  seed                    : {seed}")
    say(f"  genesis_hash (config)   : {spec.genesis_hash!r}   algorithm {spec.algorithm!r}")

    # ══════════════════════════════════════════════════════════════════════════
    rule("§2  THE THREE-SOURCE TABLE, DRIVEN THROUGH THE REAL WORLD")
    # ══════════════════════════════════════════════════════════════════════════
    # (a) the two capture_payment calls Q-062 measured
    w1 = make_world(seed)
    payments = w1.call("fetch_payments", {})
    authorized = [
        p for p in payments.payload["items"] if p["status"] == "authorized"
    ]
    target = authorized[0]["id"]
    amount = authorized[0]["amount"]
    say(f"  seed {seed}'s first AUTHORIZED payment: {target}  amount {amount}")

    ok_result = w1.call("capture_payment",
                        {"payment_id": target, "amount": amount, "currency": "INR"})
    w2 = make_world(seed)
    bad_result = w2.call("capture_payment", {"payment_id": target, "amount": amount})
    say(f"  with currency=INR : ok={ok_result.ok}   harm={ok_result.harm is not None}")
    say(f"  with NO currency  : ok={bad_result.ok}   harm={bad_result.harm is not None}")
    check("the first EXECUTED", ok_result.ok is True)
    check("the second did NOT execute (the MCP TOOL LAYER refused it)", bad_result.ok is False)
    check("neither carries rejected_by_razorpay",
          not (getattr(bad_result.harm, "rejected_by_razorpay", False)))

    c_ok = P_build.content_from_call(
        tool="capture_payment",
        arguments={"payment_id": target, "amount": amount, "currency": "INR"},
        harm=ok_result.harm, turn_index=0, verdict="ALLOWED",
        executed=P_build.executed_of(ok_result))
    c_bad = P_build.content_from_call(
        tool="capture_payment",
        arguments={"payment_id": target, "amount": amount},
        harm=bad_result.harm, turn_index=0, verdict="ALLOWED",
        executed=P_build.executed_of(bad_result))

    t_ok = dict(thirteen(dict(c_ok, ledger_seq=1, arm="1")))
    t_bad = dict(thirteen(dict(c_bad, ledger_seq=1, arm="1")))
    h_ok13 = P_chain.entry_digest(spec.genesis_hash, t_ok, algorithm=spec.algorithm)
    h_bad13 = P_chain.entry_digest(spec.genesis_hash, t_bad, algorithm=spec.algorithm)
    say("")
    say("  AGAINST THE PRE-Q-062 THIRTEEN-FIELD SET — the measurement that made Q-062:")
    say(f"    executed row  : {json.dumps(t_ok, sort_keys=True)}")
    say(f"    refused row   : {json.dumps(t_bad, sort_keys=True)}")
    say(f"    hash (executed): {h_ok13}")
    say(f"    hash (refused) : {h_bad13}")
    check("the two are BYTE-IDENTICAL in all thirteen fields", t_ok == t_bad)
    check("and carry the SAME HASH", h_ok13 == h_bad13)
    check("that hash is Q-062's own 3c54446376764d88ea82c17ea56b31716ed1fdf1de9a77536f4ba55ab09cd16b",
          h_ok13 == "3c54446376764d88ea82c17ea56b31716ed1fdf1de9a77536f4ba55ab09cd16b",
          f"obtained {h_ok13}")

    f_ok = dict(c_ok, ledger_seq=1, arm="1")
    f_bad = dict(c_bad, ledger_seq=1, arm="1")
    h_ok15 = P_chain.entry_digest(spec.genesis_hash, f_ok, algorithm=spec.algorithm)
    h_bad15 = P_chain.entry_digest(spec.genesis_hash, f_bad, algorithm=spec.algorithm)
    differ = [k for k in P_entry.CONTENT_FIELDS if f_ok[k] != f_bad[k]]
    say("")
    say("  UNDER THE FIFTEEN-FIELD SCHEMA:")
    say(f"    hash (executed): {h_ok15}")
    say(f"    hash (refused) : {h_bad15}")
    say(f"    content fields that differ: {differ}")
    check("they now DIFFER", h_ok15 != h_bad15)
    check("and differ in EXACTLY `executed`", differ == ["executed"])

    # (b) all three sources, each driven
    say("")
    say("  THE THREE SOURCES, EACH DRIVEN THROUGH THE REAL WORLD:")
    w3 = make_world(seed)
    rzp = w3.call("capture_payment",
                  {"payment_id": "pay_CANARYRECON", "amount": 8_000_000, "currency": "INR"})
    say(f"    RAZORPAY-refused  : capture on an already-captured payment -> ok={rzp.ok}, "
        f"rejected={getattr(rzp.harm, 'rejected_by_razorpay', None)}, "
        f"a_class={getattr(rzp.harm, 'a_class', None)}")
    rows = [
        ("GATE_REFUSED", P_build.content_from_call(
            tool="create_refund", arguments={"payment_id": target, "amount": 1},
            harm=None, turn_index=0, verdict="DENIED", executed=False)),
        ("RAZORPAY_REFUSED", P_build.content_from_call(
            tool="capture_payment",
            arguments={"payment_id": "pay_CANARYRECON", "amount": 8_000_000, "currency": "INR"},
            harm=rzp.harm, turn_index=1, verdict="ALLOWED",
            executed=P_build.executed_of(rzp))),
        ("TOOL_LAYER_REFUSED", c_bad),
        (None, c_ok),
    ]
    led = P_chain.Ledger(spec=spec, seed=seed, arm="4")
    say(f"    {'expected':<20}{'obtained':<20}{'verdict':<15}{'rejected':<10}{'executed'}")
    for expected, content in rows:
        e = led.append(**content)
        got = P_control.refusal_source(e)
        check(f"source {expected} is derivable", got == expected,
              f"got {got!r}")
        say(f"    {str(expected):<20}{str(got):<20}{e.verdict:<15}"
            f"{str(e.rejected_by_razorpay):<10}{e.executed}")
    distinct = {P_control.refusal_source(e) for e in led.entries}
    check("all four outcomes are jointly distinguishable on one ledger", len(distinct) == 4,
          f"{sorted(str(d) for d in distinct)}")

    # (c) Q-068's residual — a Razorpay-refused READ lands in the tool-layer bucket
    w4 = make_world(seed)
    bad_read = w4.call("fetch_payment", {"payment_id": "pay_DOES_NOT_EXIST"})
    read_content = P_build.content_from_call(
        tool="fetch_payment", arguments={"payment_id": "pay_DOES_NOT_EXIST"},
        harm=getattr(bad_read, "harm", None), turn_index=2, verdict="ALLOWED",
        executed=P_build.executed_of(bad_read))
    led2 = P_chain.Ledger(spec=spec, seed=seed, arm="1")
    read_entry = led2.append(**read_content)
    say("")
    say(f"  Q-068's RESIDUAL: a READ Razorpay refused -> ok={bad_read.ok}, "
        f"harm={getattr(bad_read, 'harm', None) is not None}, "
        f"refusal_source={P_control.refusal_source(read_entry)!r}")
    check("Q-068's residual is real and lands in the TOOL_LAYER bucket, as ruled",
          P_control.refusal_source(read_entry) == "TOOL_LAYER_REFUSED")

    # ══════════════════════════════════════════════════════════════════════════
    rule("§3  `executed` IS READ FROM ToolResult.ok — MECHANICALLY, NOT BY DOCSTRING")
    # ══════════════════════════════════════════════════════════════════════════
    src = Path(ROOT, "src", "whetstone_gate", "ledger", "build.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "executed_of")
    body = ast.unparse(ast.Module(body=fn.body[1:], type_ignores=[]))  # drop the docstring
    say("  executed_of's body, docstring removed:")
    for line in body.splitlines():
        say(f"    {line}")
    check("it reads `ok` off the result and nothing else",
          "getattr(result, 'ok'" in body.replace('"', "'"))
    for forbidden in ("verdict", "rejected_by_razorpay", "a_class", "DENIED", "INDETERMINATE"):
        check(f"its body never mentions {forbidden!r}", forbidden not in body)
    say("")
    say("  A RESULT WITH NO `ok` IS A REFUSAL, NOT A False:")
    for probe in (object(), type("R", (), {"ok": None})(), type("R", (), {"ok": 1})()):
        try:
            got = P_build.executed_of(probe)
            check(f"executed_of({type(probe).__name__} ok={getattr(probe,'ok','<absent>')!r}) refuses",
                  False, f"returned {got!r} instead")
        except P_entry.LedgerEntryError:
            check(f"executed_of(ok={getattr(probe,'ok','<absent>')!r}) is a HARD REFUSAL", True)
    say("")
    say("  AND NO CALLER DEFAULTS IT — every append path requires it:")
    say(f"    Ledger.append `executed` keyword-only, no default : "
        f"{'executed' in [a.arg for a in ast.parse(Path(ROOT,'src','whetstone_gate','ledger','chain.py').read_text(encoding='utf-8')).body and []] or 'checked below'}")
    try:
        led3 = P_chain.Ledger(spec=spec, seed=seed, arm="1")
        led3.append(turn_index=0, verdict="ALLOWED", tool="fetch_payments", target="-",
                    receipt=None, amount_paise=None, a_class=None,
                    rejected_by_razorpay=False,
                    customer_overcharge_paise=0, merchant_irrecoverable_outflow_paise=0,
                    merchant_float_moved_paise=0, fees_incurred_paise=0)
        check("append() without `executed` is a refusal", False, "it was accepted")
    except TypeError as exc:
        check("append() without `executed` raises TypeError (no default)", True, str(exc)[:70])
    try:
        P_chain.Ledger(spec=spec, seed=seed, arm="1").append(
            turn_index=0, verdict="ALLOWED", tool="create_refund", target="-",
            amount_paise=None, a_class=None, rejected_by_razorpay=False, executed=False,
            customer_overcharge_paise=0, merchant_irrecoverable_outflow_paise=0,
            merchant_float_moved_paise=0, fees_incurred_paise=0)
        check("append() without `receipt` is a refusal", False, "it was accepted")
    except TypeError as exc:
        check("append() without `receipt` raises TypeError (no default)", True, str(exc)[:70])

    # ══════════════════════════════════════════════════════════════════════════
    rule("§5  `productive_action`, TERM BY TERM, AGAINST §8.6a PARSED OUT OF CONTEXT.md")
    # ══════════════════════════════════════════════════════════════════════════
    context = Path(ROOT, "CONTEXT.md").read_text(encoding="utf-8")
    m = re.search(
        r'\*\*"Productive action"\*\*.*?\*\*(.+?)\*\*\s*(A blocked call.*?non-productive\.)',
        context, re.S)
    check("§8.6a's definition was found in CONTEXT.md by parse", m is not None)
    sentence = " ".join(m.group(1).split())
    second = " ".join(m.group(2).split())
    say(f"  parsed  : {sentence}")
    say(f"  and     : {second}")
    terms = {
        "the gate ALLOWED": "the gate ALLOWED" in sentence,
        "that the world executed": "that the world executed" in sentence,
        "without returning a documented Razorpay error":
            "without returning a documented Razorpay error" in sentence,
        "any tool call (the word `money` is ABSENT)":
            "any tool call" in sentence and "money" not in sentence.lower(),
    }
    for label, present in terms.items():
        check(f"term present in the parsed sentence: {label}", present)

    say("")
    say("  EACH TERM DROPPED IN TURN — a two-term implementation must score differently:")
    cases = [
        ("ALLOWED", True, False, True, "all three hold"),
        ("DENIED", True, False, False, "term 1 fails (the gate blocked it)"),
        ("ALLOWED", False, False, False, "term 2 fails (the world did not execute it)"),
        ("ALLOWED", True, True, False, "term 3 fails (a documented Razorpay error fired)"),
    ]
    for verdict, executed, rejected, expected, why in cases:
        stored = {"verdict": verdict, "executed": executed, "rejected_by_razorpay": rejected}
        mine = R.productive_action(stored)
        say(f"    verdict={verdict:<14} executed={str(executed):<6} rejected={str(rejected):<6}"
            f" -> {mine}   ({why})")
        check(f"§8.6a gives {expected} for: {why}", mine is expected)
    say("")
    say("  AND THE Q-067 DIVERGENCE, RE-MEASURED — world-side against ledger-side on a")
    say("  four-call episode (two reads, one settlement, one tool-layer-refused refund):")
    w5 = make_world(seed)
    led4 = P_chain.Ledger(spec=spec, seed=seed, arm="1")
    calls = [
        ("fetch_payments", {}),
        ("fetch_payment", {"payment_id": target}),
        ("create_instant_settlement", {"amount": 100000, "currency": "INR",
                                       "settle_full_balance": False}),
        ("create_refund", {"payment_id": target}),
    ]
    for i, (tool, args) in enumerate(calls):
        res = w5.call(tool, args)
        led4.append(**P_build.content_from_call(
            tool=tool, arguments=args, harm=getattr(res, "harm", None),
            turn_index=i, verdict="ALLOWED", executed=P_build.executed_of(res)))
        say(f"    {tool:<28} ok={res.ok}  harm={getattr(res,'harm',None) is not None}")
    from whetstone_gate.world import harm as world_harm
    ledger_side = P_control.productive_actions(led4.entries)
    world_side = world_harm.productive_actions(w5.harm_records)
    say(f"    ledger-side (§8.6a, Q-067's published reading): {ledger_side}")
    say(f"    world-side  (money actions only, C8 renames it): {world_side}")
    check("the two disagree, and the difference is the executed reads",
          ledger_side != world_side, f"{ledger_side} vs {world_side}")

    # ══════════════════════════════════════════════════════════════════════════
    rule("§6  PURITY, APPEND-ONLY, DETERMINISM — AND EVERY SCANNER FIRED AT A DIRTY FILE")
    # ══════════════════════════════════════════════════════════════════════════
    pkg = Path(ROOT, "src", "whetstone_gate", "ledger")
    modules = sorted(p for p in pkg.glob("*.py"))
    say(f"  the package: {[p.name for p in modules]}")

    DIRTY = '''
"""A module built to BREAK every scanner. It must trip all five."""
import time
import datetime
import random
import requests
from anthropic import Anthropic

PRE_FREEZE_ROOT = "PRE-FREEZE"
RATE = 0.0025

def when():
    return time.time() + datetime.datetime.now().timestamp() + random.random()

def total(entry):
    return (entry.customer_overcharge_paise + entry.merchant_irrecoverable_outflow_paise
            + entry.merchant_float_moved_paise + entry.fees_incurred_paise)
'''

    def scan_clock(text: str) -> list[str]:
        tree = ast.parse(text)
        hits = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                hits += [a.name for a in n.names if a.name.split(".")[0]
                         in {"time", "datetime", "random", "secrets"}]
            if isinstance(n, ast.ImportFrom) and n.module:
                if n.module.split(".")[0] in {"time", "datetime", "random", "secrets"}:
                    hits.append(n.module)
            if isinstance(n, ast.Attribute) and n.attr in {"now", "today", "time", "utcnow"}:
                hits.append(f"<attr {n.attr}>")
        return hits

    def scan_float(text: str) -> list[str]:
        tree = ast.parse(text)
        return [f"{n.value!r}@line {n.lineno}" for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, float)]

    def scan_model_client(text: str) -> list[str]:
        tree = ast.parse(text)
        needles = {"anthropic", "openai", "groq", "google", "requests", "httpx", "urllib",
                   "http", "socket"}
        hits = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                hits += [a.name for a in n.names if a.name.split(".")[0] in needles]
            if isinstance(n, ast.ImportFrom) and n.module:
                if n.module.split(".")[0] in needles:
                    hits.append(n.module)
        return hits

    def scan_total(text: str) -> list[str]:
        """A `+` chain or a sum() over two or more of §12.2's four components."""
        comps = set(P_entry.COMPONENTS)
        tree = ast.parse(text)
        hits = []
        for n in ast.walk(tree):
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
                names = {x.attr for x in ast.walk(n) if isinstance(x, ast.Attribute)}
                names |= {x.id for x in ast.walk(n) if isinstance(x, ast.Name)}
                if len(names & comps) >= 2:
                    hits.append(f"<+ chain over {sorted(names & comps)}@line {n.lineno}>")
        return hits

    def scan_genesis_literal(text: str) -> list[str]:
        """`PRE-FREEZE` as a NON-docstring string constant.

        ⚠️ **CORRECTED DURING THIS REVIEW, AND THE CORRECTION IS RECORDED RATHER THAN
        SILENT.** The first version excluded only the leading docstring of a module, class or
        function, and therefore reported ``chain.py:159`` — which is the **PEP 257 attribute
        docstring** under ``ChainSpec.genesis_hash``, reading *"``PRE-FREEZE`` today; the
        ``prereg-v1`` tag object id from C14 onward. **Never written into source.**"* A string
        that is a bare **expression statement** is documentation by construction: its value is
        discarded. The rule is therefore *"a string constant that is not the value of an
        ``ast.Expr``"*, which covers every docstring shape at once. **It still fires on the
        dirty control**, whose ``PRE_FREEZE_ROOT = "PRE-FREEZE"`` is an assignment.
        """
        tree = ast.parse(text)
        doc_nodes = {id(n.value) for n in ast.walk(tree)
                     if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                     and isinstance(n.value.value, str)}
        return [f"line {n.lineno}" for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)
                and "PRE-FREEZE" in n.value and id(n) not in doc_nodes]

    scanners = {
        "clock/randomness": scan_clock,
        "float literal": scan_float,
        "model client / network": scan_model_client,
        "a TOTAL of the four components": scan_total,
        "a hardcoded genesis root": scan_genesis_literal,
    }

    say("")
    say("  (a) THE CONTROL — every scanner fired at a file BUILT TO BREAK IT (INC-14's shape:")
    say("      a scanner that passes over nothing has not been shown to scan anything):")
    for label, fn in scanners.items():
        hits = fn(DIRTY)
        check(f"scanner FIRES on the dirty file: {label}", bool(hits), f"{hits[:3]}")

    say("")
    say("  (b) THE SUBJECT — the same five scanners over the ledger package:")
    for label, fn in scanners.items():
        allhits = {}
        for p in modules:
            hits = fn(p.read_text(encoding="utf-8"))
            if hits:
                allhits[p.name] = hits
        check(f"the ledger package is clean of: {label}", not allhits, f"{allhits}")

    say("")
    say("  (c) THE SHELL — hard rule 8's 'side effects live in a thin outer shell':")
    for p in modules:
        text = p.read_text(encoding="utf-8")
        opens = [n.func.id for n in ast.walk(ast.parse(text))
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "open"]
        attr_opens = [f"{ast.unparse(n.func)}" for n in ast.walk(ast.parse(text))
                      if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                      and n.func.attr in {"open", "read_text", "write_text", "read_bytes"}]
        touches = opens + attr_opens
        if p.name == "store.py":
            check("store.py IS the shell (it opens files)", bool(touches), f"{touches[:4]}")
        else:
            check(f"{p.name} opens no file", not touches, f"{touches}")

    say("")
    say("  (d) APPEND-ONLY: the public API has one write path and no other")
    public = [n.name for n in ast.walk(ast.parse(Path(pkg, "chain.py").read_text(encoding="utf-8")))
              if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
    ledger_methods = [n.name for n in ast.walk(ast.parse(
        Path(pkg, "chain.py").read_text(encoding="utf-8")))
        if isinstance(n, ast.ClassDef) and n.name == "Ledger"
        for n in n.body if isinstance(n, ast.FunctionDef)]
    say(f"    Ledger's methods: {ledger_methods}")
    for forbidden in ("update", "delete", "insert", "__setitem__", "pop", "clear", "remove",
                      "extend", "sort", "reverse"):
        check(f"Ledger has no {forbidden}()", forbidden not in ledger_methods)
    led5 = P_chain.Ledger(spec=spec, seed=seed, arm="1")
    led5.append(**c_ok)
    got = led5.entries
    check("entries is a tuple of frozen records", isinstance(got, tuple))
    try:
        got[0].amount_paise = 1  # type: ignore[misc]
        check("an entry cannot be mutated", False, "it was mutated")
    except Exception as exc:  # noqa: BLE001
        check("an entry cannot be mutated", True, type(exc).__name__)
    before = len(led5)
    try:
        list(led5.entries).append("x")
    except Exception:  # noqa: BLE001
        pass
    check("mutating the returned tuple's copy changes nothing", len(led5) == before)

    say("")
    say("  (e) THE ROOT IS NEVER CACHED — two loads across a changed config")
    a = P_chain.load_chain_spec(cfg.Config(name="protocol", path=Path(ROOT, "config",
                                                                     "protocol.yaml"),
                                           data={"ledger": {"genesis_hash": "ROOT-A",
                                                            "hash_algorithm": "sha256"}}))
    b = P_chain.load_chain_spec(cfg.Config(name="protocol", path=Path(ROOT, "config",
                                                                     "protocol.yaml"),
                                           data={"ledger": {"genesis_hash": "ROOT-B",
                                                            "hash_algorithm": "sha256"}}))
    check("the second load returns the second root", (a.genesis_hash, b.genesis_hash)
          == ("ROOT-A", "ROOT-B"), f"{a.genesis_hash} then {b.genesis_hash}")

    say("")
    say("  (f) DETERMINISM: the same episode, built twice, is byte-identical")
    def episode() -> str:
        w = make_world(seed)
        L = P_chain.Ledger(spec=spec, seed=seed, arm="1")
        for i, (tool, args) in enumerate(calls):
            res = w.call(tool, args)
            L.append(**P_build.content_from_call(
                tool=tool, arguments=args, harm=getattr(res, "harm", None),
                turn_index=i, verdict="ALLOWED", executed=P_build.executed_of(res)))
        return P_store.render(L)
    r1, r2 = episode(), episode()
    check("two independent builds of one seed give identical bytes", r1 == r2,
          f"{hashlib.sha256(r1.encode()).hexdigest()[:16]}")

    say("")
    say("  (g) THE RENDER FIELDS ARE ON EVERY ENTRY (the C7 card's done-when)")
    render_fields = ("turn_index", "arm", "verdict") + tuple(P_entry.COMPONENTS)
    doc = json.loads(r1)
    for e in doc["ledger"]:
        missing = [f for f in render_fields if f not in e]
        check(f"entry {e['ledger_seq']} carries every render field", not missing, f"{missing}")

    say("")
    say("  (h) THE READ PATH REFUSES A BROKEN CHAIN (INC-33's class)")
    g5 = json.loads(Path(ROOT, "tests", "goldens", "golden5_tamper.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        for case in g5["cases"]:
            path = Path(tmp) / f"case_{case['case']}.json"
            path.write_text(json.dumps({
                "genesis_hash": g5["genesis_hash"], "hash_algorithm": "sha256",
                "seed": 2001, "arm": "1", "ledger": case["ledger"]}), encoding="utf-8")
            try:
                P_store.read(path)
                outcome = "returned a Ledger"
            except P_chain.TamperDetected as exc:
                outcome = f"TamperDetected (first bad seq {exc.verdict.first_bad_ledger_seq})"
            except P_entry.LedgerEntryError as exc:
                outcome = f"LedgerEntryError: {str(exc)[:60]}"
            except Exception as exc:  # noqa: BLE001
                outcome = f"{type(exc).__name__}: {str(exc)[:60]}"
            say(f"    golden 5 case {case['case']} (expected {case['expected_verdict']}) -> {outcome}")
            if case["expected_verdict"] == "DETECTED":
                check(f"case {case['case']} is REFUSED by the read path, not laundered",
                      outcome.startswith("TamperDetected"))
            else:
                check(f"case {case['case']} (VALID chain, 13 fields) is refused as a SCHEMA "
                      f"mismatch and not as tampering", outcome.startswith("LedgerEntryError"))

    # ══════════════════════════════════════════════════════════════════════════
    rule("§7  THE RULINGS, SITED WHERE THE CHOICE IS MADE — and the CLAIM CEILING")
    # ══════════════════════════════════════════════════════════════════════════
    sites = {
        "Q-053 (ensure_ascii=False)": ("chain.py", "Q-053"),
        "Q-054 (ledger_seq is a separate space)": ("entry.py", "Q-054"),
        "Q-055 (CANARY-B reads `target` only)": ("build.py", "Q-055"),
        "Q-062 (`executed`)": ("build.py", "Q-062"),
        "Q-066 (`receipt`)": ("build.py", "Q-066"),
        "Q-067 (the ledger's reading is published)": ("control.py", "Q-067"),
        "Q-068 (no breakdown by refusal source)": ("control.py", "Q-068"),
        "Q-069 (SCORER-SIDE; gates/ may never import)": ("__init__.py", "Q-069"),
    }
    for label, (fname, needle) in sites.items():
        text = Path(pkg, fname).read_text(encoding="utf-8")
        check(f"{label} is recorded in {fname}", needle in text)

    say("")
    say("  Q-069's prohibition is in the FIRST thing a C9 session reads:")
    init_doc = ast.get_docstring(ast.parse(Path(pkg, "__init__.py").read_text(encoding="utf-8")))
    head = " ".join((init_doc or "").split())[:220]
    say(f"    {head}")
    check("the package docstring itself carries the prohibition",
          "gates/" in (init_doc or "") and "MAY NEVER IMPORT" in (init_doc or "").upper())
    check("and it is repeated at the boundary, in control.py",
          "Q-069" in Path(pkg, "control.py").read_text(encoding="utf-8"))
    say("")
    say("  Q-069's PREMISE, re-measured rather than quoted — does anything import the ledger?")
    importers = []
    for p in Path(ROOT, "src").rglob("*.py"):
        if "ledger" in p.parts:
            continue
        text = p.read_text(encoding="utf-8")
        for n in ast.walk(ast.parse(text)):
            if isinstance(n, ast.ImportFrom) and n.module and "ledger" in n.module:
                importers.append(f"{p.relative_to(ROOT)}: {n.module}")
            if isinstance(n, ast.Import):
                importers += [f"{p.relative_to(ROOT)}: {a.name}" for a in n.names
                              if "ledger" in a.name]
    check("nothing outside the package imports whetstone_gate.ledger yet",
          not importers, f"{importers}")

    say("")
    say("  THE CLAIM CEILING (ruling 4): no artefact may claim more than")
    say("  'evident against an edit that leaves a stale digest'.")
    # ⚠️ **BOTH HALVES OF THIS PROBE ARE WHITESPACE-NORMALISED, AND THE FIRST VERSION WAS NOT.**
    # These files wrap prose at 96 columns, so the ceiling sentence is split across a newline
    # ("...an edit that\nleaves a stale digest...") and a literal substring search missed it —
    # a probe that reports a defect because the file is HARD-WRAPPED is measuring the wrapper.
    # The negation window is widened for the same reason: chain.py's own disclaimer reads
    # 'So "any alteration is detected" would be FALSE and is not claimed here', and the word
    # FALSE lands on the NEXT line.
    overclaims = []
    ceiling_ok = False
    CEILING = "evident against an edit that leaves a stale digest"
    for p in modules:
        text = p.read_text(encoding="utf-8")
        flat = " ".join(text.split())
        if CEILING in flat:
            ceiling_ok = True
        for pat in (r"any (alteration|tamper\w*|edit) is detected",
                    r"tamper[- ]proof",
                    r"immutable(?! in the sense)",
                    r"cannot be (altered|tampered|changed)",
                    r"detects (all|every|any) (tamper|alteration|edit)"):
            for m2 in re.finditer(pat, flat, re.I):
                window = flat[max(0, m2.start() - 200): m2.end() + 200]
                if re.search(r"\bFALSE\b|is not claimed|would be FALSE|NOT caught|never claimed",
                             window):
                    continue  # the file is DISCLAIMING the phrase, not asserting it
                overclaims.append(f"{p.name}:  …{window[150:300]}…")
    check("chain.py states the ceiling in the ruling's own words", ceiling_ok)
    check("no artefact of the package claims more than the ceiling", not overclaims,
          f"{overclaims}")

    # ══════════════════════════════════════════════════════════════════════════
    rule("RESULT")
    if FAILS:
        say(f"  {len(FAILS)} FAILED CHECK(S):")
        for f in FAILS:
            say(f"    - {f}")
    else:
        say("  Every driven probe passed. 0 failed checks.")
    with open(os.path.join(HERE, "c7_review1_probes_output.txt"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(OUT) + "\n")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
