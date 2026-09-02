"""C7 REVIEW 1 (`472cdc4b`) — THE MUTATION HARNESS.

Run from the CLONE, with PYTHONPATH pointed at the CLONE's `src`:

    CLONE=/tmp/c7rev1.XXXX
    PYTHONPATH="$CLONE/src" python docs/reviews/mutants/c7_mutants.py --clone "$CLONE"

⚠️ **BOTH KNOWN FAILURE DIRECTIONS ARE GUARDED, AND BOTH ARE FLATTERING.**

  * `INCIDENTS.md` **INC-64 / OF-139** — a harness that imports the LIVE package while it
    believes it is importing a clone: every mutation is invisible and **every mutant reports
    SURVIVED**. Guarded by printing `whetstone_gate.__file__` and `config.repo_root()` at the
    head of the run, asserting both resolve inside the clone, and by running the repository's
    own `test_the_package_under_test_is_the_tree_under_test` in the clone first.
  * `INCIDENTS.md` **INC-57** — restoring with `git checkout --` from a HEAD that already holds
    the mutation: every restore re-applies its predecessor and **every mutant reports KILLED**.
    Guarded by capturing the original bytes before the first mutation and **writing them back**,
    re-hashing to confirm, and never invoking git.

⚠️ **A RUN WHOSE POST-RESTORE CONTROL IS NOT GREEN IS VOID AND IS NOT SCORED.**

⚠️ **THREE NO-OP CONTROL MUTANTS ARE RUN AND MUST SURVIVE.** A sweep in which everything dies
cannot distinguish a suite that kills mutants from a harness that reports KILLED unconditionally.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

CHAIN = "src/whetstone_gate/ledger/chain.py"
ENTRY = "src/whetstone_gate/ledger/entry.py"
BUILD = "src/whetstone_gate/ledger/build.py"
CONTROL = "src/whetstone_gate/ledger/control.py"
INIT = "src/whetstone_gate/ledger/__init__.py"

# ──────────────────────────────────────────────────────────────────────────────
# THE REQUIRED SET, one mutant per property, sealed at `f1ccde1` in
# docs/reviews/independent/c7_phase1_blind.md BEFORE any of these were written.
# ──────────────────────────────────────────────────────────────────────────────
MUTANTS: list[dict] = [
    # ── Group A — the chain digest and its exclusion rule ─────────────────────
    dict(id="M01", prop="P-01", file=CHAIN, op="sort_keys=True -> False",
         old="        sort_keys=True,", new="        sort_keys=False,"),
    dict(id="M02", prop="P-01", file=CHAIN, op='separators no-whitespace -> spaced',
         old='        separators=(",", ":"),', new='        separators=(", ", ": "),'),
    dict(id="M03", prop="P-02", file=CHAIN, op="ensure_ascii=False -> True (Q-053 option 2)",
         old="        ensure_ascii=False,\n        allow_nan=False,",
         new="        ensure_ascii=True,\n        allow_nan=False,"),
    dict(id="M04", prop="P-03", file=CHAIN, op="prev_hash NOT excluded from the digest",
         old='        body = {name: value for name, value in stored.items() if name not in CHAIN_FIELDS}',
         new='        body = {name: value for name, value in stored.items() if name != "hash"}'),
    dict(id="M05", prop="P-04", file=CHAIN,
         op="the digest body is selected by SCHEMA, not by key (INC-32's defect)",
         old='        body = {name: value for name, value in stored.items() if name not in CHAIN_FIELDS}',
         new='        body = {name: stored[name] for name in CONTENT_FIELDS if name in stored}'),
    dict(id="M06", prop="P-05", file=CHAIN, op="the concatenation order is reversed",
         old='        payload = (prev_hash + canonical_json(body)).encode("utf-8")',
         new='        payload = (canonical_json(body) + prev_hash).encode("utf-8")'),
    dict(id="M07", prop="P-05", file=CHAIN, op='the operands are encoded UTF-16, not UTF-8',
         old='        payload = (prev_hash + canonical_json(body)).encode("utf-8")',
         new='        payload = (prev_hash + canonical_json(body)).encode("utf-16")'),
    # ── Group B — the verifier ────────────────────────────────────────────────
    dict(id="M08", prop="P-06", file=CHAIN,
         op="⚠️ THE §5.4 DEFECT: carry the STORED digest forward, never the recomputed one",
         old="        expected_prev = recomputed", new='        expected_prev = stored["hash"]'),
    dict(id="M09", prop="P-06", file=CHAIN, op="the recomputation check is disabled outright",
         old='        if recomputed != stored["hash"]:', new='        if False:'),
    dict(id="M10", prop="P-07", file=CHAIN, op="the first-bad ledger_seq is off by one",
         old="""        if recomputed != stored["hash"]:
            return ChainVerdict(
                DETECTED,
                label,""",
         new="""        if recomputed != stored["hash"]:
            return ChainVerdict(
                DETECTED,
                label + 1,"""),
    dict(id="M11", prop="P-08", file=CHAIN,
         op="⚠️ INC-34: the verifier requires THIS package's content schema",
         old="        missing = [name for name in (LEDGER_SEQ, *CHAIN_FIELDS) if name not in stored]",
         new="        missing = [name for name in (*CONTENT_FIELDS, *CHAIN_FIELDS) if name not in stored]"),
    dict(id="M12", prop="P-09", file=CHAIN,
         op="the FIRST entry's link to the genesis root is not checked",
         old='        if stored["prev_hash"] != expected_prev:',
         new='        if position > 1 and stored["prev_hash"] != expected_prev:'),
    dict(id="M13", prop="P-10", file=CHAIN,
         op="⚠️ INC-33: the READ path re-appends without verifying the stored bytes",
         old="""    outcome = verify(entries, genesis_hash=spec.genesis_hash, algorithm=spec.algorithm)
    if not outcome.ok:
        raise TamperDetected(outcome)""",
         new="""    outcome = verify(entries, genesis_hash=spec.genesis_hash, algorithm=spec.algorithm)
    if False:
        raise TamperDetected(outcome)"""),
    # ── Group C — append-only-ness and the sequence ───────────────────────────
    dict(id="M14", prop="P-11", file=CHAIN, op="`entries` hands back the LIVE list",
         old="        return tuple(self._entries)", new="        return self._entries"),
    dict(id="M15", prop="P-12", file=CHAIN, op="ledger_seq is 0-based, not the dense 1-based row",
         old='            "ledger_seq": len(self._entries) + 1,',
         new='            "ledger_seq": len(self._entries),'),
    dict(id="M16", prop="P-13", file=BUILD,
         op="append_log validates as it goes, so a bad row leaves a SHORT ledger",
         old="        validate_content(dict(content, ledger_seq=1, arm=ledger.arm))\n        proposed.append(content)",
         new="        proposed.append(content)"),
    # ── Group D — the genesis root ────────────────────────────────────────────
    dict(id="M17", prop="P-14", file=CHAIN,
         op="a missing ledger.genesis_hash DEFAULTS instead of refusing",
         old='    genesis = protocol.require("ledger.genesis_hash")',
         new='    genesis = protocol.data.get("ledger", {}).get("genesis_hash") or "PRE-FREEZE"'),
    dict(id="M18", prop="P-15", file=CHAIN, op="the genesis root is a HARDCODED literal in source",
         old='    genesis = protocol.require("ledger.genesis_hash")',
         new='    genesis = "PRE-FREEZE"'),
    # ── Group E — `executed`, its three sources, and `receipt` ────────────────
    dict(id="M19", prop="P-16", file=BUILD,
         op="a result with no `ok` silently becomes False instead of refusing",
         old='    ok = getattr(result, "ok", None)', new='    ok = getattr(result, "ok", False)'),
    dict(id="M20", prop="P-16", file=BUILD,
         op="⚠️ THE FORBIDDEN INFERENCE: `executed` derived from verdict + harm, not read",
         old="    content[EXECUTED] = executed",
         new="    content[EXECUTED] = bool(verdict == 'ALLOWED' and harm is not None "
             "and not harm.rejected_by_razorpay)"),
    dict(id="M21", prop="P-17", file=CONTROL, op="INDETERMINATE no longer counts as a gate refusal",
         old="    if entry.verdict in (DENIED, INDETERMINATE):",
         new="    if entry.verdict == DENIED:"),
    dict(id="M22", prop="P-18", file=CONTROL, op="a RAZORPAY refusal is reported as the tool layer's",
         old="""    if entry.rejected_by_razorpay:
        return RAZORPAY_REFUSED
    return TOOL_LAYER_REFUSED""",
         new="""    if entry.rejected_by_razorpay:
        return TOOL_LAYER_REFUSED
    return TOOL_LAYER_REFUSED"""),
    dict(id="M23", prop="P-19", file=CONTROL, op="the residual bucket is reported as RAZORPAY's",
         old="""    if entry.rejected_by_razorpay:
        return RAZORPAY_REFUSED
    return TOOL_LAYER_REFUSED""",
         new="""    if entry.rejected_by_razorpay:
        return RAZORPAY_REFUSED
    return RAZORPAY_REFUSED"""),
    dict(id="M24", prop="P-20", file=BUILD,
         op='an empty-string `receipt` is normalised to None (INC-04 rebuilt)',
         old="""    value = arguments.get(RECEIPT_ARGUMENT)
    if isinstance(value, str):
        return value
    return None""",
         new="""    value = arguments.get(RECEIPT_ARGUMENT)
    if isinstance(value, str) and value:
        return value
    return None"""),
    dict(id="M25", prop="P-20", file=CHAIN, op="`receipt` gains a default of None on the write path",
         old="        receipt: str | None,", new="        receipt: str | None = None,"),
    # ── Group F — the four consistency assertions ─────────────────────────────
    dict(id="M26", prop="P-21", file=ENTRY, op="assertion 1 disabled: a BLOCKED call may claim executed",
         old="    if executed and verdict != ALLOWED:", new="    if False and verdict != ALLOWED:"),
    dict(id="M27", prop="P-22", file=ENTRY,
         op="assertion 2 disabled: a RAZORPAY-refused call may claim executed",
         old="    if executed and rejected:", new="    if False and rejected:"),
    dict(id="M28", prop="P-23", file=ENTRY,
         op="⚠️ assertion 3 checks only the FIRST component, not all four",
         old="        moved = [c for c in COMPONENTS if values[c] != 0]",
         new="        moved = [c for c in COMPONENTS[:1] if values[c] != 0]"),
    dict(id="M29", prop="P-23", file=ENTRY,
         op="assertion 3 fires only for gate-blocked calls, so a tool-layer refusal may carry harm",
         old="    if not executed:\n        moved =",
         new="    if not executed and verdict != ALLOWED:\n        moved ="),
    dict(id="M30", prop="P-24", file=BUILD,
         op="the absence case claims Razorpay refused it, so a rejected record is fabricated",
         old='        fields: dict[str, Any] = {"a_class": None, "rejected_by_razorpay": False}',
         new='        fields: dict[str, Any] = {"a_class": None, "rejected_by_razorpay": True}'),
    # ── Group G — `productive_action`, term by term ───────────────────────────
    dict(id="M31", prop="P-25", file=CONTROL, op="term 1 dropped (the gate ALLOWED)",
         old="""    return (
        entry.verdict == ALLOWED
        and entry.executed
        and not entry.rejected_by_razorpay
    )""",
         new="""    return (
        entry.executed
        and not entry.rejected_by_razorpay
    )"""),
    dict(id="M32", prop="P-26", file=CONTROL, op="term 2 dropped (the world EXECUTED it)",
         old="""    return (
        entry.verdict == ALLOWED
        and entry.executed
        and not entry.rejected_by_razorpay
    )""",
         new="""    return (
        entry.verdict == ALLOWED
        and not entry.rejected_by_razorpay
    )"""),
    dict(id="M33", prop="P-27", file=CONTROL, op="term 3 dropped (no documented Razorpay error)",
         old="""    return (
        entry.verdict == ALLOWED
        and entry.executed
        and not entry.rejected_by_razorpay
    )""",
         new="""    return (
        entry.verdict == ALLOWED
        and entry.executed
    )"""),
    dict(id="M34", prop="P-28", file=CONTROL,
         op="⚠️ Q-067 REVERSED: the NARROW reading — money actions only, reads not counted",
         old="""    return (
        entry.verdict == ALLOWED
        and entry.executed
        and not entry.rejected_by_razorpay
    )""",
         new="""    return (
        entry.verdict == ALLOWED
        and entry.executed
        and not entry.rejected_by_razorpay
        and entry.tool in ("create_refund", "capture_payment", "create_instant_settlement")
    )"""),
    # ── Group H — the table and the render fields ─────────────────────────────
    dict(id="M35", prop="P-29", file=ENTRY, op="the arm/verdict table is not enforced",
         old="    if verdict not in allowed:", new="    if verdict not in VERDICTS:"),
    dict(id="M36", prop="P-30", file=ENTRY, op="`turn_index` is dropped from the stored entry",
         old='        return {name: getattr(self, name) for name in (*CONTENT_FIELDS, *CHAIN_FIELDS)}',
         new='        return {name: getattr(self, name) for name in (*CONTENT_FIELDS, *CHAIN_FIELDS)\n'
             '                if name != "turn_index"}'),
    # ── Group I — purity, isolation and the claim ceiling ─────────────────────
    dict(id="M37", prop="P-31", file=CHAIN, op="a binary float is serialised instead of refused",
         old='    _refuse_floats(body, path="entry")', new='    pass'),
    dict(id="M38", prop="P-32", file=INIT,
         op="Q-069's prohibition is deleted from the package docstring",
         old="⚠️⚠️ **STOP. THIS PACKAGE IS SCORER-SIDE. `gates/` MAY NEVER IMPORT IT, ON ANY PATH, EVER.**",
         new="This package is used by the scorer."),
    dict(id="M39", prop="P-33", file=CHAIN,
         op="the tamper-evidence claim is raised above the ceiling ruling 4 fixes",
         old="quietly revise them, *\"the ledger is tamper-evident\"* means **evident against an edit that\nleaves a stale digest, and against nothing else** — and the README must not say more.",
         new="quietly revise them, the ledger is tamper-evident: any alteration is detected."),
    # ── THE CONTROLS — no-op mutations that MUST SURVIVE ──────────────────────
    dict(id="C-1", prop="CONTROL", file=CONTROL, control=True,
         op="a local name is renamed in productive_actions (no behaviour change)",
         old="    return sum(1 for entry in entries if productive_action(entry))",
         new="    return sum(1 for _e in entries if productive_action(_e))"),
    dict(id="C-2", prop="CONTROL", file=CHAIN, control=True,
         op="one word of a prose sentence in a docstring is changed",
         old="Two independent things are checked at every entry, in this order:",
         new="Two separate things are checked at every entry, in this order:"),
    dict(id="C-3", prop="CONTROL", file=ENTRY, control=True,
         op="an f-string message is reworded without changing any behaviour",
         old='raise LedgerEntryError(f"ledger_seq must be an integer >= 1, got {seq!r}")',
         new='raise LedgerEntryError(f"ledger_seq has to be an integer >= 1, got {seq!r}")'),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_suite(clone: Path, env: dict) -> tuple[bool, str, str]:
    """One pytest run per mutant. Returns (green, tail, the names of the killing tests).

    ⚠️ **ONE RUN AND NOT TWO.** The first version ran the suite twice for a killed mutant —
    once with ``-x`` for the verdict and again without it for the killer names — and the sweep
    then exceeded the session's command timeout and was **cut off mid-mutant, leaving a
    mutation applied in the clone**. That is `INCIDENTS.md` INC-57's hazard arriving through a
    timeout rather than through git: the next run's baseline read RED and the run VOIDED
    itself, which is the harness behaving correctly. The clone was restored by **copying the
    pristine bytes from the repository**, verified by SHA-256 on all six files, and this
    function now makes one pass and parses both facts out of it.
    """
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_c7_ledger.py", "-q", "-p", "no:cacheprovider",
         "--no-header", "--tb=no"],
        cwd=str(clone), env=env, capture_output=True, text=True,
    )
    tail = [ln for ln in proc.stdout.splitlines() if ln.strip()][-1:]
    failed = [ln.split("::")[-1].split()[0] for ln in proc.stdout.splitlines()
              if ln.startswith("FAILED")]
    killers = ", ".join(failed[:3]) + (f" (+{len(failed)-3} more)" if len(failed) > 3 else "")
    return proc.returncode == 0, " | ".join(tail)[-200:], killers


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", required=True)
    args = ap.parse_args()
    clone = Path(args.clone).resolve()

    env = dict(os.environ)
    env["PYTHONPATH"] = str(clone / "src")

    print("=" * 100)
    print("IMPORT PROVENANCE — printed BEFORE any mutant (INC-64 / OF-139)")
    print("=" * 100)
    probe = subprocess.run(
        [sys.executable, "-c",
         "import whetstone_gate;from whetstone_gate import config as cfg;"
         "print(whetstone_gate.__file__);print(cfg.repo_root())"],
        cwd=str(clone), env=env, capture_output=True, text=True)
    pkg, root = probe.stdout.strip().splitlines()[:2]
    print(f"  CLONE                   : {clone}")
    print(f"  whetstone_gate.__file__ : {pkg}")
    print(f"  config.repo_root()      : {root}")
    inside = Path(pkg).resolve().is_relative_to(clone) and Path(root).resolve() == clone
    print(f"  both resolve INSIDE the clone: {inside}")
    if not inside:
        print("  VOID: the harness would be mutating a tree the interpreter does not import.")
        return 2
    guard = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/test_repo_invariants.py::test_the_package_under_test_is_the_tree_under_test",
         "-q", "-p", "no:cacheprovider", "--no-header"],
        cwd=str(clone), env=env, capture_output=True, text=True)
    print(f"  the repository's OWN OF-139 guard, run in the clone: "
          f"{'PASS' if guard.returncode == 0 else 'FAIL'}")
    if guard.returncode != 0:
        print("  VOID.")
        return 2

    print()
    print("=" * 100)
    print("BASELINE CONTROL (must be green before a single mutant)")
    print("=" * 100)
    ok, tail, _ = run_suite(clone, env)
    print(f"  {tail}")
    if not ok:
        print("  VOID: the baseline is not green.")
        return 2

    originals = {f: (clone / f).read_bytes() for f in {m["file"] for m in MUTANTS}}
    original_shas = {f: hashlib.sha256(b).hexdigest() for f, b in originals.items()}
    print()
    for f, s in sorted(original_shas.items()):
        print(f"  original {f:<44} sha256 {s[:16]}…")

    print()
    print("=" * 100)
    print("THE MUTANTS")
    print("=" * 100)
    results = []
    for m in MUTANTS:
        path = clone / m["file"]
        text = originals[m["file"]].decode("utf-8")
        if m["old"] not in text:
            results.append((m, "NOT-APPLIED", "the anchor text was not found"))
            print(f"  {m['id']}  {m['prop']:<9} NOT-APPLIED  (anchor not found)  {m['op']}")
            continue
        count = text.count(m["old"])
        mutated = text.replace(m["old"], m["new"], 1)
        line = text[: text.index(m["old"])].count("\n") + 1
        path.write_bytes(mutated.encode("utf-8"))
        ok, tail, killers = run_suite(clone, env)
        # ⚠️ RESTORE BY WRITING THE ORIGINAL BYTES. Never `git checkout` (INC-57).
        path.write_bytes(originals[m["file"]])
        assert sha(path) == original_shas[m["file"]], f"restore failed for {m['file']}"
        verdict = "SURVIVED" if ok else "KILLED"
        results.append((m, verdict, killers or tail))
        flag = ""
        if m.get("control") and verdict == "KILLED":
            flag = "   <- a CONTROL died: the harness is over-killing"
        if not m.get("control") and verdict == "SURVIVED":
            flag = "   <- SURVIVOR"
        print(f"  {m['id']}  {m['prop']:<9} {verdict:<9} {m['file'].split('/')[-1]}:{line}"
              f" (x{count})  {m['op']}{flag}")
        if verdict == "KILLED":
            print(f"          killed by: {killers}")

    print()
    print("=" * 100)
    print("POST-RESTORE CONTROL (a run whose post-restore control is not green is VOID)")
    print("=" * 100)
    for f, b in originals.items():
        assert (clone / f).read_bytes() == b, f"{f} was not restored"
    ok, tail, _ = run_suite(clone, env)
    print("  every file byte-identical to its pre-run bytes: True")
    print(f"  {tail}")
    if not ok:
        print("  VOID: the post-restore control is not green. THIS RUN IS NOT SCORED.")
        return 2

    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    required = [(m, v, k) for m, v, k in results if not m.get("control")]
    controls = [(m, v, k) for m, v, k in results if m.get("control")]
    killed = [r for r in required if r[1] == "KILLED"]
    survived = [r for r in required if r[1] == "SURVIVED"]
    notapplied = [r for r in required if r[1] == "NOT-APPLIED"]
    print(f"  REQUIRED-SET mutants : {len(required)}")
    print(f"    KILLED             : {len(killed)}")
    print(f"    SURVIVED           : {len(survived)}   {[m['id'] for m, _, _ in survived]}")
    print(f"    NOT APPLIED        : {len(notapplied)} {[m['id'] for m, _, _ in notapplied]}")
    print(f"  CONTROL mutants      : {len(controls)}   "
          f"SURVIVED {sum(1 for _, v, _ in controls if v == 'SURVIVED')} of {len(controls)}")
    for m, v, _ in controls:
        print(f"    {m['id']}  {v}   {m['op']}")
    props = sorted({m["prop"] for m, _, _ in required})
    print(f"  distinct REQUIRED-SET properties covered: {len(props)}  {props}")
    return 0 if not survived and not notapplied else 1


if __name__ == "__main__":
    raise SystemExit(main())
