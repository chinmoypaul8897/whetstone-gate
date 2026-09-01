"""C13 REVIEW 2, session 8c49c4d3 — the CONTEXT.md v1.9 audit.

A FIX session amended the law. This audits the amendment from the git BLOBS,
never the working tree: control bytes counted as BYTES before and after, the LF
arithmetic against numstat, P1/P3 byte-identity, and section movement.
"""
import subprocess
import re
import hashlib

REPO = r"c:/Users/chinm/whetstone-gate"
BEFORE = "041abe4^:CONTEXT.md"   # v1.8
AFTER = "041abe4:CONTEXT.md"     # v1.9
HEAD = "HEAD:CONTEXT.md"


def blob(ref):
    return subprocess.run(["git", "show", ref], cwd=REPO, capture_output=True).stdout


def control_scan(b, label):
    counts = {}
    for byte in b:
        if byte < 0x20 or byte == 0x7F:
            counts[byte] = counts.get(byte, 0) + 1
    lf = counts.pop(0x0A, 0)
    print(f"  {label}: {len(b):,} bytes | LF {lf:,} | CR {counts.get(0x0D,0)} | "
          f"TAB {counts.get(0x09,0)} | 0x08 {counts.get(0x08,0)}")
    others = {hex(k): v for k, v in sorted(counts.items())}
    print(f"     every OTHER control byte (<0x20 or 0x7f), LF excluded: "
          f"{others if others else 'NONE — clean'}")
    return lf, counts


print("=" * 92)
print("1. CONTROL-BYTE SCAN, COUNTED AS BYTES, over the whole file (INC-13 put a raw 0x08 here)")
print("=" * 92)
b_before, b_after, b_head = blob(BEFORE), blob(AFTER), blob(HEAD)
lf_b, ctl_b = control_scan(b_before, "v1.8 (041abe4^)")
lf_a, ctl_a = control_scan(b_after, "v1.9 (041abe4) ")
lf_h, ctl_h = control_scan(b_head, "HEAD           ")
print(f"  v1.9 blob == HEAD blob ? {b_after == b_head}   "
      f"(sha256 head={hashlib.sha256(b_head).hexdigest()[:16]}…)")

print()
print("=" * 92)
print("2. LF ARITHMETIC vs git diff --numstat")
print("=" * 92)
ns = subprocess.run(["git", "show", "--numstat", "--format=", "041abe4", "--", "CONTEXT.md"],
                    cwd=REPO, capture_output=True, text=True).stdout.split()
ins, dele = int(ns[0]), int(ns[1])
print(f"  numstat: +{ins} / -{dele}  -> insertions - deletions = {ins - dele}")
print(f"  LF delta measured from the blobs: {lf_a} - {lf_b} = {lf_a - lf_b}")
print(f"  MATCH: {ins - dele == lf_a - lf_b}")

print()
print("=" * 92)
print("3. P1 AND P3 BYTE-IDENTICAL, AND NO SECTION MOVED")
print("=" * 92)
t_before = b_before.decode("utf-8")
t_after = b_after.decode("utf-8")


def grab(text, start_marker, end_marker):
    i = text.index(start_marker)
    j = text.index(end_marker, i)
    return text[i:j]


for name, s, e in [("P1", "> **P1.**", "> **P2.**"), ("P3", "> **P3.**", "\n\n**If P1–P3 hold")]:
    a = grab(t_before, s, e)
    b = grab(t_after, s, e)
    same = a.encode("utf-8") == b.encode("utf-8")
    print(f"  {name}: byte-identical v1.8 -> v1.9 ? {same}   ({len(a.encode())} bytes)")
    if not same:
        print("     !!! DIFFERS")

hb = re.findall(r"^(#{2,4} .*)$", t_before, re.M)
ha = re.findall(r"^(#{2,4} .*)$", t_after, re.M)
print(f"  headings: v1.8={len(hb)}  v1.9={len(ha)}")
print(f"  heading SEQUENCE identical (no section moved, none added/removed): {hb == ha}")
if hb != ha:
    only_b = [h for h in hb if h not in ha]
    only_a = [h for h in ha if h not in hb]
    print(f"     only in v1.8: {only_b}")
    print(f"     only in v1.9: {only_a}")

print()
print("=" * 92)
print("4. WHAT ACTUALLY CHANGED — the hunks, by section")
print("=" * 92)
d = subprocess.run(["git", "show", "--format=", "-U0", "041abe4", "--", "CONTEXT.md"],
                   cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                   errors="replace").stdout
for h in re.findall(r"^@@[^@]*@@.*$", d, re.M):
    print("  " + h.strip()[:120])
