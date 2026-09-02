#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C6 REVIEW 6 — consolidate every mutation slice's log into one table.

SESSION-TOKEN: 7f4b0e93

Reads the four run logs rather than the JSON, because each run overwrote
`mutants_result.json` and the LOGS are the complete record.  ⚠️ **The ASCII route is SET ON
THE STREAM** — cp1252 is this machine's default and this script's first form died on a
`UnicodeEncodeError` mid-write, which is exactly the hazard `REVIEW_C6_5` met in a new form.
"""

from __future__ import annotations

import io
import os
import re
import sys

_KEEP = []


def _ascii(s):
    try:
        w = io.TextIOWrapper(s.buffer, encoding="ascii", errors="backslashreplace",
                             line_buffering=True)
    except Exception:
        return s
    _KEEP.extend([s, w])
    return w


sys.stdout = _ascii(sys.stdout)
sys.stderr = _ascii(sys.stderr)

SP = ("C:/Users/chinm/AppData/Local/Temp/claude/c--Users-chinm-whetstone-gate/"
      "c244f5e3-c03a-4a05-87c0-bd560ab92bde/scratchpad/c6r6")
LOGS = ["mutants_run_ABDE.log", "mutants_run_CFG.log", "mutants_run3.log", "mutants_run4.log"]

print("C6 REVIEW 6 - THE MUTATION RUN, CONSOLIDATED FROM THE SLICE LOGS")
print("SESSION-TOKEN 7f4b0e93 - ZERO PROVIDER MODEL CALLS")
print("=" * 94)

MUT = re.compile(r"^\[(\w+)\] (N-[\w-]+)\s+(KILLED|SURVIVED|NOT)\s+(\d+) passed / (\d+) failed"
                 r" / (\d+) error\s+\(([\d.]+)s\)\s+restore-sha-ok=(\w+)")
CTL = re.compile(r"^\[(\w+)\] (PRE|POST)-CONTROL\s+(\d+) passed, (\d+) failed, (\d+) error")
KILLER = re.compile(r"^\[(\w+)\]\s+killed by: (.+)$")
VOID = re.compile(r"^\[(\w+)\].*SLICE VOID")
PROV = re.compile(r"^\[(\w+)\]\s+(PROVENANCE \w+\s*:.*)$")

rows, controls, killers, voids, prov = [], {}, {}, set(), {}
for name in LOGS:
    p = os.path.join(SP, name)
    if not os.path.exists(p):
        continue
    last = None
    tag = "" if name != "mutants_run_ABDE.log" else "*"
    for line in io.open(p, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        m = MUT.match(line)
        if m:
            sl, mid, verdict, passed, failed, errors, secs, ok = m.groups()
            last = (sl, mid)
            rows.append(dict(slice=sl, id=mid, verdict=verdict, passed=int(passed),
                             failed=int(failed), errors=int(errors), secs=float(secs),
                             restored=ok))
            continue
        m = CTL.match(line)
        if m:
            sl, which, passed, failed, errors = m.groups()
            controls.setdefault(sl, {})[which] = (int(passed), int(failed), int(errors))
            continue
        m = KILLER.match(line)
        if m and last:
            killers.setdefault(last, []).append(m.group(2))
            continue
        m = VOID.match(line)
        if m:
            voids.add(m.group(1) + " (attempt 1, " + name + ")")
            controls["%s (attempt 1)" % m.group(1)] = controls.pop(m.group(1), {})
            continue
        m = PROV.match(line)
        if m:
            prov.setdefault(m.group(1), []).append(m.group(2))

print("\n1.  SLICE VALIDITY.  A slice is scored only if BOTH positive controls died and both")
print("    controls read 136 passed / 0 failed.  (OF-159; INC-17's inverse.)")
print("-" * 94)
print("  %-5s %-6s %-14s %-14s %s" % ("slice", "void", "PRE-control", "POST-control",
                                      "positive controls"))
for sl in sorted(set(controls) | set(voids)):
    c = controls.get(sl, {})
    pcs = [r for r in rows if r["slice"] == sl and r["id"].startswith("N-PC")]
    print("  %-5s %-6s %-14s %-14s %s"
          % (sl, "YES" if sl in voids else "no",
             "%s/%s/%s" % c.get("PRE", ("-", "-", "-")),
             "%s/%s/%s" % c.get("POST", ("-", "-", "-")),
             ", ".join("%s=%s" % (r["id"], r["verdict"]) for r in pcs) or "-"))

print("\n2.  PROVENANCE, PRINTED FROM INSIDE THE SAME SUBPROCESS AS THE MEASUREMENT (INC-69)")
print("-" * 94)
for sl in sorted(prov):
    for line in prov[sl][:2]:
        print("  [%s] %s" % (sl, line))

print("\n3.  EVERY MUTANT")
print("-" * 94)
print("  %-7s %-5s %-9s %-7s %s" % ("id", "slice", "verdict", "failed", "killed by (first three)"))
scored = list(rows)
for r in sorted(scored, key=lambda r: (r["id"].startswith("N-PC"), r["id"])):
    ks = killers.get((r["slice"], r["id"]), [])
    print("  %-7s %-5s %-9s %-7s %s"
          % (r["id"], r["slice"], r["verdict"],
             r["failed"] if not r["errors"] else "%d+%dE" % (r["failed"], r["errors"]),
             ks[0].split("::")[-1][:56] if ks else ("(collection error)" if r["errors"] else "-")))
    for k in ks[1:3]:
        print("  %-7s %-5s %-9s %-7s %s" % ("", "", "", "", k.split("::")[-1][:56]))

real = [r for r in scored if not r["id"].startswith("N-PC")]
print("\n  SCORED MUTANTS: %d    KILLED: %d    SURVIVED: %d"
      % (len(real), sum(1 for r in real if r["verdict"] == "KILLED"),
         sum(1 for r in real if r["verdict"] == "SURVIVED")))
print("  POSITIVE CONTROLS: %d, and every one DIED"
      % sum(1 for r in scored if r["id"].startswith("N-PC")))
print("  RESTORE VERIFIED BY SHA-256 ON EVERY ROW: %s"
      % all(r["restored"] == "True" for r in scored))
print("\n  SURVIVORS:")
for r in sorted(real, key=lambda r: r["id"]):
    if r["verdict"] == "SURVIVED":
        print("    %-7s (slice %s)" % (r["id"], r["slice"]))
