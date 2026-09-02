"""C7 REVIEW 2 — THE MUTATION SWEEP. One mutant per SEALED owned property.

SESSION-TOKEN: b8c31a57.

⚠️ THIS HARNESS IS BUILT AGAINST THREE RECORDED WAYS OF GETTING IT WRONG, AND EACH GUARD
NAMES THE ONE IT ANSWERS.

  * `INC-64` / `INC-69` — a harness that builds the clone environment and then does not pass
    it to the ``subprocess.run`` that MEASURES, so every suite runs against the LIVE
    repository and every mutant reads SURVIVED. **Here `env=` is passed on the same call, and
    the provenance of ``whetstone_gate.ledger.chain`` is resolved IN THAT SAME SUBPROCESS,
    with that same environment object, immediately before every suite run.** A resolution
    outside the clone is a hard abort.
  * `OF-159` — this project's mutation discipline has negative controls everywhere and
    positive controls nowhere. **Three controls run here: `CTRL-KILL` (a blatant mutant that
    MUST die), `CTRL-LIVE` (a bare failing assertion inside the clone's own TEST file, which
    proves the clone's tests are the ones being run) and `CTRL-NOOP` (a comment edit that
    MUST survive). If either positive control survives, or the negative one dies, the run is
    VOID and unscored.**
  * `INC-57` — restoring by ``git checkout``. **Every restore writes back the exact bytes
    captured before the first mutation and re-hashes to confirm.** Nothing here touches git.

⚠️ AND THE SCORING RULE, BECAUSE A COUNT DELTA IS THE WRONG INSTRUMENT HERE (`OF-163`).
A fresh clone carries no ``vendor/`` and no ``.git``, so a fixed set of tests fails at
baseline for reasons that have nothing to do with any mutant. **A mutant is KILLED iff the
set of FAILING TEST IDS grows** — judged by identity, not by count.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

CLONE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "").resolve()
LEDGER = CLONE / "src" / "whetstone_gate" / "ledger"
SUITE = [
    "tests/test_c7_ledger.py",
    "tests/test_config_loader.py",
    "tests/test_repo_invariants.py",
    "tests/test_tripwire_registry.py",
]

TOUCHED = [
    LEDGER / "chain.py",
    LEDGER / "entry.py",
    LEDGER / "build.py",
    LEDGER / "control.py",
    LEDGER / "store.py",
    LEDGER / "__init__.py",
    CLONE / "tests" / "test_c7_ledger.py",
]

PRISTINE: dict[pathlib.Path, bytes] = {}


def env_for_clone() -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(CLONE / "src")
    env["PYTHONIOENCODING"] = "utf-8"
    env.pop("WHETSTONE_CONFIG_DIR", None)
    return env


def run_pytest() -> tuple[set[str], str]:
    """Run the ledger-relevant suite IN THE CLONE and return the FAILING TEST IDS.

    ⚠️ ``env`` is built here and PASSED HERE, and the provenance assertion below runs on the
    SAME path with the SAME object. `INC-69`: a guard that executes in a different subprocess
    from the thing it guards proves only that the guard works.
    """
    env = env_for_clone()

    probe = subprocess.run(
        [sys.executable, "-c",
         "import whetstone_gate.ledger.chain as c, whetstone_gate.config as cfg;"
         "print(c.__file__);print(cfg.repo_root())"],
        cwd=str(CLONE), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    lines = [ln.strip() for ln in probe.stdout.splitlines() if ln.strip()]
    if len(lines) < 2 or not all(str(CLONE).lower() in ln.lower() for ln in lines[:2]):
        raise SystemExit(
            "ABORT: the measurement's own environment does not resolve inside the clone.\n"
            f"  clone   {CLONE}\n  probe   {lines}\n  stderr  {probe.stderr[:400]}\n"
            "This is INC-69 exactly, and the run is stopped rather than scored."
        )

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *SUITE, "-q", "-p", "no:cacheprovider",
         "--no-header", "-rf"],
        cwd=str(CLONE), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    failing = set(re.findall(r"^FAILED (\S+)", proc.stdout, re.M))
    failing |= set(re.findall(r"^ERROR (\S+)", proc.stdout, re.M))
    tail = [ln for ln in proc.stdout.splitlines() if " passed" in ln or " failed" in ln]
    return failing, (tail[-1] if tail else "(no summary line)")


def capture_pristine() -> None:
    for path in TOUCHED:
        PRISTINE[path] = path.read_bytes()


def restore_all() -> bool:
    """⚠️ RESTORE BY WRITING THE CAPTURED BYTES, NEVER BY ``git checkout`` (`INC-57`)."""
    ok = True
    for path, original in PRISTINE.items():
        path.write_bytes(original)
        if hashlib.sha256(path.read_bytes()).hexdigest() != hashlib.sha256(original).hexdigest():
            print("  RESTORE FAILED: %s" % path)
            ok = False
    return ok


def apply_mutant(path: pathlib.Path, old: str, new: str) -> None:
    text = path.read_bytes().decode("utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            "ABORT: the mutation target is not unique in %s (%d occurrences).\n"
            "A harness that mutates a site it cannot name exactly is measuring something "
            "else.\n  old: %r" % (path.name, count, old[:120])
        )
    path.write_bytes(text.replace(old, new).encode("utf-8"))


# ─────────────────────────────────────────────────────────────────────────────────────────
# THE MUTANTS. One per sealed owned property (docs/reviews/independent/c7_review2_criteria.md
# §3), plus the three controls, plus the two dispositions this review must re-test itself.
# ─────────────────────────────────────────────────────────────────────────────────────────

C = "chain.py"
E = "entry.py"
B = "build.py"
K = "control.py"
I = "__init__.py"
S = "store.py"

MUTANTS = [
    # ── CONTROLS ────────────────────────────────────────────────────────────────────────
    ("CTRL-KILL", "POSITIVE CONTROL — must DIE", C,
     "        sort_keys=True,\n", "        sort_keys=False,\n", "MUST_DIE"),
    ("CTRL-NOOP", "NEGATIVE CONTROL — must SURVIVE", K,
     "#: The three, in the ruling's own order",
     "#: The three sources, in the ruling's own order", "MUST_SURVIVE"),

    # ── A: the digest and its exclusion rule ────────────────────────────────────────────
    ("M01", "RP-01 sorted keys", C,
     "        separators=(\",\", \":\"),\n", "        separators=(\", \", \": \"),\n", "OWNED"),
    ("M02", "RP-02 ensure_ascii=False", C,
     "        ensure_ascii=False,\n", "        ensure_ascii=True,\n", "OWNED"),
    ("M03", "RP-03 prev_hash/hash excluded from the digest", C,
     "        body = {name: value for name, value in stored.items() if name not in CHAIN_FIELDS}",
     "        body = {name: value for name, value in stored.items() if name != \"hash\"}",
     "OWNED"),
    ("M04", "RP-04 the exclusion is BY KEY, not by SCHEMA (INC-32)", C,
     "        body = {name: value for name, value in stored.items() if name not in CHAIN_FIELDS}\n"
     "        try:",
     "        body = {name: value for name, value in stored.items() if name in CONTENT_FIELDS}\n"
     "        try:",
     "OWNED"),
    ("M05", "RP-05 concatenation ORDER", C,
     "        payload = (prev_hash + canonical_json(body)).encode(\"utf-8\")",
     "        payload = (canonical_json(body) + prev_hash).encode(\"utf-8\")", "OWNED"),
    ("M06", "RP-05 operands encoded UTF-16", C,
     "        payload = (prev_hash + canonical_json(body)).encode(\"utf-8\")\n    except UnicodeEncodeError as exc:",
     "        payload = (prev_hash + canonical_json(body)).encode(\"utf-16\")\n    except UnicodeEncodeError as exc:",
     "OWNED"),
    ("M07", "RP-06 a binary float is SERIALISED rather than refused", C,
     "    _refuse_floats(body, path=\"entry\")\n",
     "    pass  # _refuse_floats(body, path=\"entry\")\n", "OWNED"),

    # ── B: the verifier ─────────────────────────────────────────────────────────────────
    ("M08", "RP-07 THE RECOMPUTATION DISABLED OUTRIGHT (PROCESS.md S5.4's defect)", C,
     "        if recomputed != stored[\"hash\"]:",
     "        if False and recomputed != stored[\"hash\"]:", "OWNED"),
    ("M09", "RP-07 the walk carries the STORED digest forward (REVIEW 1's M08)", C,
     "        expected_prev = recomputed\n\n    return ChainVerdict(",
     "        expected_prev = stored[\"hash\"]\n\n    return ChainVerdict(", "OWNED"),
    ("M10", "RP-08 the first-bad ledger_seq is OFF BY ONE", C,
     "            return ChainVerdict(\n                DETECTED,\n                label,\n"
     "                f\"entry {label}'s CONTENTS do not hash to its stored digest: recomputed \"",
     "            return ChainVerdict(\n                DETECTED,\n                label + 1,\n"
     "                f\"entry {label}'s CONTENTS do not hash to its stored digest: recomputed \"",
     "OWNED"),
    ("M11", "RP-09 case D's REASON reworded to the LINK, which is the wrong reason", C,
     "                f\"entry {label}'s CONTENTS do not hash to its stored digest: recomputed \"",
     "                f\"the link is broken at entry {label}: recomputed \"", "OWNED"),
    ("M12", "RP-10 ENTRY 1's GENESIS LINK UNCHECKED (REVIEW 1's M12 / OF-141)", C,
     "        if stored[\"prev_hash\"] != expected_prev:",
     "        if position > 1 and stored[\"prev_hash\"] != expected_prev:", "OWNED"),
    ("M13", "RP-10 the genesis link unchecked ONLY for the PRE-FREEZE sentinel", C,
     "        if stored[\"prev_hash\"] != expected_prev:\n            return ChainVerdict(",
     "        if not (position == 1 and stored[\"prev_hash\"] == \"PRE-FREEZE\") and stored[\"prev_hash\"] != expected_prev:\n            return ChainVerdict(",
     "OWNED"),
    ("M14", "RP-11 the EMPTY chain reported DETECTED", C,
     "    return ChainVerdict(\n        VALID,\n        None,",
     "    if position == 0:\n        return ChainVerdict(DETECTED, None, \"empty\")\n"
     "    return ChainVerdict(\n        VALID,\n        None,", "OWNED"),
    ("M15", "RP-12 the READ path re-appends WITHOUT verifying (INC-33)", C,
     "    outcome = verify(entries, genesis_hash=spec.genesis_hash, algorithm=spec.algorithm)\n"
     "    if not outcome.ok:\n        raise TamperDetected(outcome)",
     "    outcome = verify(entries, genesis_hash=spec.genesis_hash, algorithm=spec.algorithm)\n"
     "    if False and not outcome.ok:\n        raise TamperDetected(outcome)", "OWNED"),

    # ── C: append-only-ness and determinism ─────────────────────────────────────────────
    ("M16", "RP-13 `entries` hands back the LIVE list", C,
     "        return tuple(self._entries)", "        return self._entries", "OWNED"),
    ("M17", "RP-14 the entry record is NOT frozen", E,
     "@dataclass(frozen=True)\nclass LedgerEntry:", "@dataclass(frozen=False)\nclass LedgerEntry:",
     "OWNED"),
    ("M18", "RP-15 ledger_seq becomes 0-based (Q-054)", C,
     "            \"ledger_seq\": len(self._entries) + 1,",
     "            \"ledger_seq\": len(self._entries),", "OWNED"),
    ("M19", "RP-16/RP-34 A CLOCK IS READ INTO THE DIGEST", C,
     "    digest = hashlib.new(algorithm)\n    try:",
     "    import time as _t\n    digest = hashlib.new(algorithm)\n"
     "    digest.update(str(int(_t.time())).encode())\n    try:", "OWNED"),

    # ── D: the genesis root ─────────────────────────────────────────────────────────────
    ("M20", "RP-17 a missing genesis_hash DEFAULTS instead of refusing", C,
     "    genesis = protocol.require(\"ledger.genesis_hash\")",
     "    genesis = protocol.require(\"ledger.genesis_hash\") if protocol.has(\"ledger.genesis_hash\") else \"PRE-FREEZE\"",
     "OWNED"),
    ("M21", "RP-18 the genesis root HARDCODED in source", C,
     "    genesis = protocol.require(\"ledger.genesis_hash\")\n    algorithm =",
     "    genesis = \"PRE-FREEZE\"\n    algorithm =", "OWNED"),

    # ── E: executed and receipt ─────────────────────────────────────────────────────────
    ("M22", "RP-19 ⚠️ THE FORBIDDEN INFERENCE — executed read from the harm record", B,
     "    ok = getattr(result, \"ok\", None)\n    if not isinstance(ok, bool):",
     "    ok = getattr(result, \"harm\", None) is not None\n    if not isinstance(ok, bool):",
     "OWNED"),
    ("M23", "RP-20 a missing `ok` becomes False instead of a refusal", B,
     "    ok = getattr(result, \"ok\", None)\n", "    ok = bool(getattr(result, \"ok\", False))\n",
     "OWNED"),
    ("M24", "RP-21 INDETERMINATE is not a GATE refusal", K,
     "    if entry.verdict in (DENIED, INDETERMINATE):",
     "    if entry.verdict == DENIED:", "OWNED"),
    ("M25", "RP-21 the residual reported as RAZORPAY", K,
     "    if entry.rejected_by_razorpay:\n        return RAZORPAY_REFUSED\n    return TOOL_LAYER_REFUSED",
     "    if entry.rejected_by_razorpay:\n        return RAZORPAY_REFUSED\n    return RAZORPAY_REFUSED",
     "OWNED"),
    ("M26", "RP-22 `\"\"` normalised to None (INC-04 rebuilt)", B,
     "    value = arguments.get(RECEIPT_ARGUMENT)\n    if isinstance(value, str):\n        return value",
     "    value = arguments.get(RECEIPT_ARGUMENT)\n    if isinstance(value, str) and value:\n        return value",
     "OWNED"),
    ("M27", "RP-23 the field ORDER is sorted, so `receipt` no longer follows `target`", E,
     "CONTENT_FIELDS: tuple[str, ...] = tuple(\n    f.name for f in fields(LedgerEntry) if f.name not in (\"prev_hash\", \"hash\")\n)",
     "CONTENT_FIELDS: tuple[str, ...] = tuple(\n    sorted(f.name for f in fields(LedgerEntry) if f.name not in (\"prev_hash\", \"hash\"))\n)",
     "OWNED"),

    # ── F: the four consistency assertions ──────────────────────────────────────────────
    ("M28", "RP-24 assertion 1 disabled", E,
     "    if executed and verdict != ALLOWED:", "    if False and verdict != ALLOWED:", "OWNED"),
    ("M29", "RP-24 assertion 1 misses INDETERMINATE", E,
     "    if executed and verdict != ALLOWED:", "    if executed and verdict == DENIED:", "OWNED"),
    ("M30", "RP-25 assertion 2 disabled", E,
     "    if executed and rejected:", "    if False and rejected:", "OWNED"),
    ("M31", "RP-26 assertion 3 on the FIRST COMPONENT ONLY", E,
     "        moved = [c for c in COMPONENTS if values[c] != 0]",
     "        moved = [c for c in COMPONENTS[:1] if values[c] != 0]", "OWNED"),
    ("M32", "RP-27 assertion 4 — a REJECTED record may carry non-zero harm", E,
     "    if not executed:\n        moved = [c for c in COMPONENTS if values[c] != 0]",
     "    if not executed and not rejected:\n        moved = [c for c in COMPONENTS if values[c] != 0]",
     "OWNED"),

    # ── G: productive_action ────────────────────────────────────────────────────────────
    ("M33", "RP-28 term 1 dropped — the gate ALLOWED", K,
     "    return (\n        entry.verdict == ALLOWED\n        and entry.executed\n        and not entry.rejected_by_razorpay\n    )",
     "    return (\n        entry.executed\n        and not entry.rejected_by_razorpay\n    )", "OWNED"),
    ("M34", "RP-28 term 2 dropped — the world EXECUTED", K,
     "    return (\n        entry.verdict == ALLOWED\n        and entry.executed\n        and not entry.rejected_by_razorpay\n    )",
     "    return (\n        entry.verdict == ALLOWED\n        and not entry.rejected_by_razorpay\n    )",
     "OWNED"),
    ("M35", "RP-28 term 3 dropped — no documented Razorpay error", K,
     "    return (\n        entry.verdict == ALLOWED\n        and entry.executed\n        and not entry.rejected_by_razorpay\n    )",
     "    return (\n        entry.verdict == ALLOWED\n        and entry.executed\n    )", "OWNED"),
    ("M36", "RP-29 ⚠️ Q-067 REVERSED — money actions only", K,
     "    return (\n        entry.verdict == ALLOWED\n        and entry.executed\n        and not entry.rejected_by_razorpay\n    )",
     "    return (\n        entry.tool in (\"create_refund\", \"capture_payment\", \"create_instant_settlement\")\n"
     "        and entry.verdict == ALLOWED\n        and entry.executed\n        and not entry.rejected_by_razorpay\n    )",
     "OWNED"),

    # ── H: the probe selector this package implements ───────────────────────────────────
    ("M37", "RP-31 CANARY-B's selector drops DENIED entries", B,
     "    return tuple(entry for entry in entries if entry.target == payment_id)",
     "    return tuple(entry for entry in entries if entry.target == payment_id and entry.executed)",
     "OWNED"),

    # ── I: the table and the render fields ──────────────────────────────────────────────
    ("M38", "RP-32 the arm/verdict table not enforced", E,
     "    if verdict not in allowed:", "    if False and verdict not in allowed:", "OWNED"),
    ("M39", "RP-33 `turn_index` dropped from the stored entry", C,
     "            \"turn_index\": turn_index,\n            \"arm\": self._arm,",
     "            \"arm\": self._arm,", "OWNED"),

    # ── J: purity, isolation, the claim ceiling ─────────────────────────────────────────
    ("M40", "RP-35 Q-069's prohibition DELETED from the package docstring", I,
     "⚠️⚠️ **STOP. THIS PACKAGE IS SCORER-SIDE. `gates/` MAY NEVER IMPORT IT, ON ANY PATH, EVER.**",
     "This package is part of the measurement stack.", "OWNED"),
    ("M41", "RP-36 ⚠️ THE CLAIM CEILING RAISED TO AN OVERCLAIM (REVIEW 1's M39 / OF-142)", C,
     "quietly revise them, *\"the ledger is tamper-evident\"* means **evident against an edit that\n"
     "leaves a stale digest, and against nothing else** — and the README must not say more.",
     "quietly revise them, *\"the ledger is tamper-evident\"* is simply true: any alteration is\n"
     "detected, and the README may say so.", "OWNED"),

    # ── K: the record itself ────────────────────────────────────────────────────────────
    ("M42", "RP-37 `append_log` FILTERS OUT non-executed rows (hard rule 11)", B,
     "    return tuple(ledger.append(**content) for content in proposed)",
     "    return tuple(ledger.append(**content) for content in proposed if content[\"executed\"])",
     "OWNED"),
    ("M43", "RP-38 the four harm components SUMMED into a total", K,
     "    return any(getattr(entry, component) != 0 for component in COMPONENTS)",
     "    return sum(getattr(entry, component) for component in COMPONENTS) != 0", "OWNED"),

    # ── the two dispositions this review must RE-TEST rather than inherit ───────────────
    ("M44", "NOT OWNED (sealed §4) — `append_log`'s all-or-nothing batch semantics", B,
     "    proposed: list[dict[str, Any]] = []\n    for row in log:",
     "    proposed: list[dict[str, Any]] = []\n    _ALL_OR_NOTHING_REMOVED = True\n    for row in log:",
     "NOT_OWNED"),
    # ⚠️ OUTSIDE THE SEALED §3 SET, AND RUN ANYWAY. `store.write`'s publish-on-complete is
    # hard-rule-10 mandated and this reviewer's own Phase 1 table OMITTED it. Adding to a
    # required set after the seal makes the bar HARDER rather than easier, which is not the
    # abuse Q-082 guards against — but it is still post-hoc, so it is scored OUTSIDE the set
    # and the omission is reported as a finding against this review's own seal.
    ("M45", "OUTSIDE THE SEALED SET — store.write is not publish-on-complete (hard rule 10)", S,
     "    temporary = path.with_name(path.name + '.partial')".replace("'", '"')
     + "\n    with temporary.open" + '("w", encoding="utf-8", newline="\\n") as handle:'
     + "\n        handle.write(text)\n    os.replace(temporary, path)",
     "    with path.open" + '("w", encoding="utf-8", newline="\\n") as handle:'
     + "\n        handle.write(text)",
     "OUTSIDE_SET"),
]


def main() -> None:
    if not LEDGER.is_dir():
        raise SystemExit("usage: c7_review2_mutants.py <clone-root>")
    print("=" * 100)
    print("C7 REVIEW 2 — MUTATION SWEEP")
    print("=" * 100)
    print("  clone            %s" % CLONE)
    print("  suite            %s" % " ".join(SUITE))
    print("  mutants          %d (incl. 2 controls)" % len(MUTANTS))
    print()

    capture_pristine()

    # ⚠️ EVERY TARGET IS CHECKED FOR UNIQUENESS BEFORE ANY SUITE RUNS. A harness that
    # discovers half way through that a site is ambiguous has already spent an hour.
    print("DRY RUN — every mutation target must occur EXACTLY ONCE")
    bad = []
    for mid, what, filename, old, new, _exp in MUTANTS:
        path = (LEDGER / filename) if filename != "test_c7_ledger.py" else (
            CLONE / "tests" / "test_c7_ledger.py")
        n = path.read_bytes().decode("utf-8").count(old)
        if n != 1:
            bad.append((mid, filename, n))
    if bad:
        for mid, filename, n in bad:
            print("  %-10s %-14s occurrences=%d" % (mid, filename, n))
        raise SystemExit("ABORT: %d mutation target(s) are not unique." % len(bad))
    print("  all %d targets unique" % len(MUTANTS))
    print()

    for path in TOUCHED:
        print("  pristine %-24s sha256 %s"
              % (path.name, hashlib.sha256(PRISTINE[path]).hexdigest()[:16]))

    print()
    print("BASELINE")
    t0 = time.time()
    baseline, summary = run_pytest()
    print("  %s   (%.0f s)" % (summary, time.time() - t0))
    print("  failing at baseline: %d  — these are CLONE ARTEFACTS (no vendor/, no .git)"
          % len(baseline))
    for name in sorted(baseline):
        print("      %s" % name)

    # ── CTRL-LIVE: prove the CLONE's TEST file is the one being executed ────────────────
    print()
    print("CTRL-LIVE — a bare failing assertion injected into the CLONE's OWN test file.")
    print("  It proves the tests being run are the clone's, which no provenance line about")
    print("  `whetstone_gate.__file__` can show (INC-69: the guard ran elsewhere).")
    tests_path = CLONE / "tests" / "test_c7_ledger.py"
    marker = "def test_ctrl_live_this_must_fail():\n    assert False, 'CTRL-LIVE'\n\n\n"
    text = tests_path.read_bytes().decode("utf-8")
    anchor = "def test_"
    idx = text.index(anchor)
    tests_path.write_bytes((text[:idx] + marker + text[idx:]).encode("utf-8"))
    live_fail, live_summary = run_pytest()
    ctrl_live_died = any("test_ctrl_live_this_must_fail" in n for n in live_fail)
    print("  %s   CTRL-LIVE died: %s" % (live_summary, ctrl_live_died))
    restore_all()

    results = []
    for mid, what, filename, old, new, expectation in MUTANTS:
        path = LEDGER / filename if filename != "test_c7_ledger.py" else tests_path
        print()
        print("-" * 100)
        print("%s  %s   [%s]" % (mid, what, filename))
        apply_mutant(path, old, new)
        t0 = time.time()
        try:
            failing, summary = run_pytest()
        finally:
            pass
        new_failures = sorted(failing - baseline)
        gone = sorted(baseline - failing)
        killed = bool(new_failures)
        print("  %s   (%.0f s)" % (summary, time.time() - t0))
        print("  VERDICT: %s" % ("KILLED" if killed else "SURVIVED"))
        for name in new_failures[:6]:
            print("      killed by  %s" % name)
        if len(new_failures) > 6:
            print("      ... and %d more" % (len(new_failures) - 6))
        if gone:
            print("      ⚠️ baseline failures that VANISHED: %s" % gone)
        results.append({
            "id": mid, "what": what, "file": filename, "expectation": expectation,
            "killed": killed, "new_failures": new_failures, "summary": summary,
        })
        if not restore_all():
            raise SystemExit("ABORT: a restore failed; the clone is dirty and the run is VOID.")

    post, post_summary = run_pytest()
    print()
    print("=" * 100)
    print("POST-RESTORE CONTROL: %s" % post_summary)
    print("  identical to baseline: %s" % (post == baseline))
    for path in TOUCHED:
        same = hashlib.sha256(path.read_bytes()).hexdigest() == \
            hashlib.sha256(PRISTINE[path]).hexdigest()
        print("  %-26s byte-identical to its pre-run bytes: %s" % (path.name, same))

    ctrl_kill = next(r for r in results if r["id"] == "CTRL-KILL")
    ctrl_noop = next(r for r in results if r["id"] == "CTRL-NOOP")
    void = (not ctrl_kill["killed"]) or ctrl_noop["killed"] or (not ctrl_live_died) \
        or (post != baseline)
    print()
    print("=" * 100)
    print("CONTROLS")
    print("  CTRL-KILL (must DIE)      %s" % ("DIED — ok" if ctrl_kill["killed"] else "SURVIVED — VOID"))
    print("  CTRL-LIVE (must DIE)      %s" % ("DIED — ok" if ctrl_live_died else "SURVIVED — VOID"))
    print("  CTRL-NOOP (must SURVIVE)  %s" % ("SURVIVED — ok" if not ctrl_noop["killed"] else "DIED — VOID"))
    print("  post-restore == baseline  %s" % (post == baseline))
    print("  RUN IS %s" % ("VOID AND UNSCORED" if void else "SCORED"))

    survivors = [r for r in results if not r["killed"] and r["id"] not in ("CTRL-NOOP",)]
    print()
    print("SURVIVORS: %d" % len(survivors))
    for r in survivors:
        print("  %-10s %-14s %s" % (r["id"], r["expectation"], r["what"]))

    (pathlib.Path(__file__).parent / "c7_review2_mutants_result.json").write_text(
        json.dumps({"baseline": sorted(baseline), "results": results,
                    "ctrl_live_died": ctrl_live_died, "void": void}, indent=2),
        encoding="utf-8")


if __name__ == "__main__":
    main()
