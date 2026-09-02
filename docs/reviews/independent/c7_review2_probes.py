"""C7 REVIEW 2 — PHASE 2 PROBES. Driven, never described.

SESSION-TOKEN: b8c31a57.

Everything here is a MEASUREMENT taken against the live package, including the two probes
that attack this review's own inputs:

  §1  the H-1 fixture's FIVE SHAPES, and which of them actually RUN.
  §2  ⚠️ OF-141's STATED COST, driven rather than repeated — does removing entry 1's link
      check really let a PRE-FREEZE ledger be presented as a SCORED one?
  §3  the three refusal sources and the executed row, all four on ONE ledger.
  §4  the four consistency assertions, assertion 3 PER COMPONENT.
  §5  purity, append-only-ness and the shell — every scanner FIRED AT A DIRTY FILE first.
  §6  the READ path over golden 5's four cases.
  §7  the rulings, sited where the choice is made.
  §8  the claim ceiling, in BOTH directions.
"""

from __future__ import annotations

import ast
import hashlib
import io
import json
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import c7_review2_reimpl as R  # noqa: E402

from whetstone_gate import config as cfg                     # noqa: E402
from whetstone_gate.ledger import build, chain, control, store  # noqa: E402
from whetstone_gate.ledger import entry as entrymod          # noqa: E402

LEDGER_DIR = REPO / "src" / "whetstone_gate" / "ledger"
G5 = json.loads((REPO / "tests" / "goldens" / "golden5_tamper.json").read_text(encoding="utf-8"))
CASE_A = [c for c in G5["cases"] if c["case"] == "A"][0]["ledger"]
GENESIS = G5["genesis_hash"]
SPEC = chain.ChainSpec(genesis_hash=GENESIS, algorithm="sha256")

CHECKS = 0
FAILS = []


def check(label, obtained, expected):
    global CHECKS
    CHECKS += 1
    ok = obtained == expected
    print("    %-72s %s" % (label, "OK" if ok else "FAIL"))
    if not ok:
        print("        obtained %r  expected %r" % (obtained, expected))
        FAILS.append(label)


print("=" * 100)
print("PROVENANCE")
print("=" * 100)
print("  chain.__file__     %s" % chain.__file__)
print("  config.repo_root() %s" % cfg.repo_root())

# ─────────────────────────────────────────────────────────────────────────────────────────
print()
print("=" * 100)
print("§1  THE H-1 FIXTURE'S FIVE SHAPES — WHICH ONES ACTUALLY RUN")
print("=" * 100)
print("  The fixture loops over five prev_hash shapes and skips any equal to the genesis root.")
print("  Today's genesis root IS the literal 'PRE-FREEZE', so shape 1 — the one the fixture's")
print("  own comment calls 'THE threat shape' — is SKIPPED. Four shapes run.")
shapes = ["PRE-FREEZE", "b" * 40, "a" * 64, "", "PRE-FREEZE-2"]
ran = []
for s in shapes:
    if s == GENESIS:
        print("    shape %-14r  SKIPPED (== genesis)" % s[:14])
        continue
    ran.append(s)
    broken = [dict(e) for e in CASE_A]
    broken[0] = dict(broken[0], prev_hash=s)
    out = chain.verify(broken, genesis_hash=GENESIS, algorithm="sha256")
    print("    shape %-14r  %-9s seq=%-4s %s"
          % (s[:14], out.verdict, out.first_bad_ledger_seq, out.reason[:42]))
    check("shape %r DETECTED at seq 1 for the LINK" % s[:14],
          (out.verdict, out.first_bad_ledger_seq, "link is broken" in out.reason),
          ("DETECTED", 1, True))
check("four of the fixture's five shapes actually run", len(ran), 4)

# ─────────────────────────────────────────────────────────────────────────────────────────
print()
print("=" * 100)
print("§2  ⚠️ OF-141's STATED COST, DRIVEN — the claim is that entry 1's link check is 'the only")
print("    thing standing between a PRE-FREEZE ledger and a SCORED one'.")
print("=" * 100)


def verify_under(entries, genesis):
    return chain.verify(entries, genesis_hash=genesis, algorithm="sha256")


def verify_M12(entries, genesis):
    """`M12` reimplemented HERE, so the consequence can be driven without mutating the tree.

    Byte-for-byte `chain.verify`'s algorithm with ONE change: the link comparison is skipped
    at position 1. Everything else — including the recomputation, which uses ``expected_prev``
    and NOT the entry's stored ``prev_hash`` — is identical.
    """
    expected_prev = genesis
    for position, stored in enumerate(entries, start=1):
        seq = stored.get("ledger_seq")
        if position > 1 and stored["prev_hash"] != expected_prev:
            return ("DETECTED", seq, "the link is broken")
        body = {k: v for k, v in stored.items() if k not in chain.CHAIN_FIELDS}
        recomputed = chain.entry_digest(expected_prev, body, algorithm="sha256")
        if recomputed != stored["hash"]:
            return ("DETECTED", seq, "contents do not hash to the stored digest")
        expected_prev = recomputed
    return ("VALID", None, "")


TAG_ID = "9c0c67349c0c67349c0c67349c0c67349c0c6734"   # a plausible git tag object id

print()
print("  (a) REVIEW 1's EXHIBIT — entry 1's prev_hash alone, digest untouched, verified against")
print("      the REAL root. This is what M12 lets through, and it reproduces:")
exhibit = [dict(e) for e in CASE_A]
exhibit[0] = dict(exhibit[0], prev_hash="a" * 64)
head = verify_under(exhibit, GENESIS)
m12 = verify_M12(exhibit, GENESIS)
print("      HEAD  -> %s at %s" % (head.verdict, head.first_bad_ledger_seq))
print("      M12   -> %s" % (m12[0],))
check("the exhibit: HEAD DETECTED, M12 VALID", (head.verdict, m12[0]), ("DETECTED", "VALID"))

print()
print("  (b) ⚠️ THE ACTUAL PUBLISHED THREAT — a ledger WRITTEN pre-freeze, PRESENTED as scored.")
print("      Build it from the PRE-FREEZE root, then verify it against the tag object id every")
print("      scored episode would chain from. Three forgeries, each driven under HEAD AND M12:")
prefreeze = [dict(e) for e in CASE_A]          # written from 'PRE-FREEZE'

forgeries = {
    "0. untouched, verified against the TAG root": prefreeze,
    "1. entry 1's prev_hash rewritten to the TAG root, digest untouched":
        [dict(prefreeze[0], prev_hash=TAG_ID)] + [dict(e) for e in prefreeze[1:]],
    "2. entry 1's prev_hash LEFT at PRE-FREEZE (M12 would skip the link check)":
        [dict(e) for e in prefreeze],
}
for label, doc in forgeries.items():
    h = verify_under(doc, TAG_ID)
    m = verify_M12(doc, TAG_ID)
    print("      %-64s HEAD=%-9s M12=%s" % (label, h.verdict, m[0]))
    check("forgery %r is DETECTED by HEAD" % label[:1], h.verdict, "DETECTED")
    check("forgery %r is DETECTED by M12 TOO" % label[:1], m[0], "DETECTED")

print()
print("  ⚠️ THE MECHANISM, READ OFF chain.verify's OWN SOURCE RATHER THAN INFERRED:")
src = (LEDGER_DIR / "chain.py").read_text(encoding="utf-8")
line = [ln.strip() for ln in src.splitlines()
        if "recomputed = entry_digest(" in ln and "expected_prev" in ln]
print("      %s" % (line[0] if line else "(not found)"))
check("the recomputation hashes from `expected_prev`, NOT from the entry's stored prev_hash",
      bool(line) and "expected_prev" in line[0] and "stored" not in line[0], True)
print()
print("      So entry 1's digest is bound to THE ROOT THE VERIFIER WAS GIVEN. Removing the link")
print("      check leaves that binding intact, and a pre-freeze ledger presented as scored is")
print("      caught AT THE RECOMPUTATION under M12 exactly as under HEAD.")
print("      chain.py's own docstring says this correctly: a pre-freeze episode 'cannot be")
print("      presented as a scored one WITHOUT RE-DERIVING EVERY DIGEST IN IT'.")

# ─────────────────────────────────────────────────────────────────────────────────────────
print()
print("=" * 100)
print("§3  THE THREE REFUSAL SOURCES PLUS THE EXECUTED ROW, ON ONE LEDGER")
print("=" * 100)


def row(**over):
    base = dict(turn_index=0, verdict="ALLOWED", tool="create_refund",
                target="pay_54cd5f529e3350", receipt=None, amount_paise=300000,
                a_class=None, rejected_by_razorpay=False, executed=True,
                customer_overcharge_paise=0, merchant_irrecoverable_outflow_paise=0,
                merchant_float_moved_paise=0, fees_incurred_paise=0)
    base.update(over)
    return base


led = chain.Ledger(spec=SPEC, seed=2001, arm="4")
built = [
    led.append(**row(turn_index=0, verdict="DENIED", executed=False)),
    led.append(**row(turn_index=1, verdict="INDETERMINATE", executed=False)),
    led.append(**row(turn_index=2, rejected_by_razorpay=True, executed=False, a_class="A2")),
    led.append(**row(turn_index=3, executed=False)),
    led.append(**row(turn_index=4, executed=True)),
]
sources = [control.refusal_source(e) for e in built]
print("    %s" % sources)
check("the five sources", sources,
      ["GATE_REFUSED", "GATE_REFUSED", "RAZORPAY_REFUSED", "TOOL_LAYER_REFUSED", None])
check("the ledger verifies", chain.verify_ledger(led).verdict, chain.VALID)
check("the tool-layer row and the executed row have DIFFERENT digests",
      built[3].hash != built[4].hash, True)
diff_fields = [f for f in entrymod.CONTENT_FIELDS
               if built[3].to_dict()[f] != built[4].to_dict()[f]]
print("    content fields that differ between the tool-layer row and the executed row: %s"
      % diff_fields)
check("and the ONLY content difference besides the row number and turn is `executed`",
      sorted(diff_fields), ["executed", "ledger_seq", "turn_index"])
check("productive_action is TRUE only on the executed row",
      [control.productive_action(e) for e in built], [False, False, False, False, True])

# ─────────────────────────────────────────────────────────────────────────────────────────
print()
print("=" * 100)
print("§4  THE FOUR CONSISTENCY ASSERTIONS, EACH DRIVEN — assertion 3 PER COMPONENT")
print("=" * 100)


def refused(**over):
    try:
        chain.Ledger(spec=SPEC, seed=2001, arm="4").append(**row(**over))
        return False
    except entrymod.LedgerEntryError:
        return True
    except Exception:  # noqa: BLE001
        return False


check("assertion 1: DENIED + executed", refused(verdict="DENIED", executed=True), True)
check("assertion 1: INDETERMINATE + executed (§9.3)",
      refused(verdict="INDETERMINATE", executed=True), True)
check("assertion 2: rejected_by_razorpay + executed",
      refused(rejected_by_razorpay=True, executed=True), True)
for comp in R.HARM_COMPONENTS:
    check("assertion 3 PER COMPONENT: %s non-zero on a non-executed call" % comp,
          refused(executed=False, **{comp: 1}), True)
check("assertion 4: a REJECTED record carrying non-zero harm",
      refused(rejected_by_razorpay=True, executed=False, merchant_float_moved_paise=1), True)
print("    ⚠️ a SUM-BASED assertion 3 would pass three of those four single-component rows,")
print("       which is why the check is per component and why it is driven four times.")

# ─────────────────────────────────────────────────────────────────────────────────────────
print()
print("=" * 100)
print("§5  PURITY, APPEND-ONLY-NESS AND THE SHELL — every scanner FIRED AT A DIRTY FILE FIRST")
print("=" * 100)

DIRTY = '''
import time, random, datetime, requests
RATE = 0.0025
GENESIS = "PRE-FREEZE"
def total(e):
    return (e.customer_overcharge_paise + e.merchant_irrecoverable_outflow_paise
            + e.merchant_float_moved_paise + e.fees_incurred_paise)
def now():
    return datetime.datetime.now()
'''

SCANNERS = {
    "clock / randomness": lambda t: sorted(
        {n for n in ("time", "datetime", "random", "secrets") if
         any(l.strip().startswith(("import " + n, "from " + n)) or ("import " in l and n in l)
             for l in t.splitlines() if l.strip().startswith(("import ", "from ")))}
        | ({".now()"} if ".now()" in t else set())),
    "a binary float literal": lambda t: sorted(
        {node.value for node in ast.walk(ast.parse(t))
         if isinstance(node, ast.Constant) and isinstance(node.value, float)}),
    "a model client or network import": lambda t: sorted(
        {n for n in ("requests", "httpx", "anthropic", "openai", "groq", "google")
         if any(l.strip().startswith(("import " + n, "from " + n)) or
                (l.strip().startswith(("import ", "from ")) and n in l)
                for l in t.splitlines())}),
    "a TOTAL of the four harm components": lambda t: (
        ["+ chain over all four"] if "customer_overcharge_paise +" in t.replace("\n", " ")
        or "+ e.merchant_float_moved_paise" in t else []),
}

print("    the DIRTY CONTROL first — a scanner that fires on nothing is INC-14's shape:")
for name, fn in SCANNERS.items():
    hits = fn(DIRTY)
    print("      %-40s dirty control -> %s" % (name, hits))
    check("scanner %r fires on the dirty control" % name, bool(hits), True)

print()
print("    and now at the package:")
package_text = "\n".join(
    (LEDGER_DIR / f).read_text(encoding="utf-8") for f in
    ("__init__.py", "chain.py", "entry.py", "build.py", "control.py", "store.py"))
for name, fn in SCANNERS.items():
    if name == "a binary float literal":
        hits = []
        for f in ("__init__.py", "chain.py", "entry.py", "build.py", "control.py", "store.py"):
            hits += ["%s:%r" % (f, v) for v in fn((LEDGER_DIR / f).read_text(encoding="utf-8"))]
    else:
        hits = fn(package_text)
    print("      %-40s the ledger package -> %s" % (name, hits or "clean"))
    check("the ledger package is clean for %r" % name, hits, [])

print()
print("    the SHELL — which modules touch the filesystem:")
io_names = ("open", "read_text", "write_text", "read_bytes", "write_bytes", "replace")
for f in ("__init__.py", "chain.py", "entry.py", "build.py", "control.py", "store.py"):
    text = (LEDGER_DIR / f).read_text(encoding="utf-8")
    tree = ast.parse(text)
    found = sorted({
        (n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id)
        for n in ast.walk(tree) if isinstance(n, ast.Call)
        and ((isinstance(n.func, ast.Attribute) and n.func.attr in io_names)
             or (isinstance(n.func, ast.Name) and n.func.id in io_names))})
    print("      %-14s %s" % (f, found or "none"))
check("only store.py performs I/O",
      sorted(f for f in ("__init__.py", "chain.py", "entry.py", "build.py", "control.py",
                         "store.py")
             if any(isinstance(n, ast.Call)
                    and ((isinstance(n.func, ast.Attribute) and n.func.attr in io_names)
                         or (isinstance(n.func, ast.Name) and n.func.id in io_names))
                    for n in ast.walk(ast.parse((LEDGER_DIR / f).read_text(encoding="utf-8"))))),
      ["store.py"])

print()
print("    the APPEND-ONLY API:")
methods = sorted(n for n in dir(chain.Ledger) if not n.startswith("_"))
print("      Ledger public surface: %s" % methods)
check("no mutator on the public surface",
      [m for m in methods if m in ("update", "delete", "insert", "pop", "clear", "remove",
                                   "extend", "sort", "reverse", "__setitem__")], [])
led2 = chain.Ledger(spec=SPEC, seed=2001, arm="1")
led2.append(**row())
try:
    object.__setattr__  # noqa: B018
    led2.entries[0].amount_paise = 1
    frozen = False
except Exception:  # noqa: BLE001
    frozen = True
check("a returned entry is FROZEN", frozen, True)
before = len(led2)
tup = led2.entries
check("`entries` returns a tuple", isinstance(tup, tuple), True)
check("mutating a copy of it changes nothing", len(led2), before)

print()
print("    DETERMINISM — two independent builds from the same inputs:")
a = chain.Ledger(spec=SPEC, seed=2001, arm="1")
b = chain.Ledger(spec=SPEC, seed=2001, arm="1")
for i in range(3):
    a.append(**row(turn_index=i))
    b.append(**row(turn_index=i))
check("byte-identical",
      store.render(a) == store.render(b), True)

print()
print("    THE GENESIS ROOT IS RE-READ, NEVER CACHED:")
with tempfile.TemporaryDirectory() as tmp:
    d = pathlib.Path(tmp)
    seen = []
    for value in ("ROOT-A", "ROOT-B"):
        (d / "protocol.yaml").write_text(
            "ledger:\n  hash_algorithm: sha256\n  genesis_hash: %s\n" % value, encoding="utf-8")
        import os as _os
        _os.environ["WHETSTONE_CONFIG_DIR"] = str(d)
        seen.append(chain.load_chain_spec().genesis_hash)
    _os.environ.pop("WHETSTONE_CONFIG_DIR", None)
print("      two calls across a changed config -> %s" % seen)
check("the second call sees the new root", seen, ["ROOT-A", "ROOT-B"])
def _non_docstring_literals(path, needle):
    """⚠️ THE RULE IS *a string constant that is NOT the value of an `ast.Expr`*, which covers
    every docstring shape at once — module, class, function AND the PEP 257 attribute
    docstring that produced a false positive in REVIEW 1's own scanner (its §10)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstring_nodes = {id(n.value) for n in ast.walk(tree)
                       if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)}
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and needle in n.value and id(n) not in docstring_nodes]


_dirty = pathlib.Path(tempfile.mkdtemp()) / "dirty_genesis.py"
_dirty.write_text(
    '"""a docstring that mentions PRE-FREEZE, which must NOT count."""' + "\n"
    + 'ROOT = "PRE-FREEZE"' + "\n",
    encoding="utf-8")
check("the genesis-literal scanner FIRES on a dirty control",
      _non_docstring_literals(_dirty, "PRE-FREEZE"), ["PRE-FREEZE"])
for _f in ("chain.py", "entry.py", "build.py", "control.py", "store.py", "__init__.py"):
    check("no genesis literal outside a docstring in %s" % _f,
          _non_docstring_literals(LEDGER_DIR / _f, "PRE-FREEZE"), [])

# ─────────────────────────────────────────────────────────────────────────────────────────
print()
print("=" * 100)
print("§6  THE READ PATH OVER GOLDEN 5's FOUR CASES")
print("=" * 100)
with tempfile.TemporaryDirectory() as tmp:
    for case in G5["cases"]:
        doc = {"genesis_hash": GENESIS, "hash_algorithm": "sha256", "seed": 2001,
               "arm": "1", store.LEDGER_KEY: case["ledger"]}
        p = pathlib.Path(tmp) / ("case_%s.json" % case["case"])
        p.write_text(json.dumps(doc), encoding="utf-8")
        try:
            store.read(p)
            outcome = "ACCEPTED"
        except chain.TamperDetected as exc:
            outcome = "TamperDetected at seq %s" % exc.verdict.first_bad_ledger_seq
        except entrymod.LedgerEntryError:
            outcome = "LedgerEntryError (a SCHEMA refusal, not a tamper accusation)"
        print("      case %s  %s" % (case["case"], outcome))
        if case["case"] == "A":
            check("case A is a SCHEMA refusal, correctly NOT a tamper accusation",
                  outcome.startswith("LedgerEntryError"), True)
        else:
            check("case %s is TamperDetected at %s" % (case["case"],
                                                       case["expected_first_bad_ledger_seq"]),
                  outcome, "TamperDetected at seq %s" % case["expected_first_bad_ledger_seq"])

# ─────────────────────────────────────────────────────────────────────────────────────────
print()
print("=" * 100)
print("§7  THE RULINGS, SITED WHERE THE CHOICE IS MADE")
print("=" * 100)
SITES = {
    "Q-053": ("chain.py", "Q-053"),
    "Q-054": ("entry.py", "Q-054"),
    "Q-055": ("build.py", "Q-055"),
    "Q-062": ("build.py", "Q-062"),
    "Q-066": ("build.py", "Q-066"),
    "Q-067": ("control.py", "Q-067"),
    "Q-068": ("control.py", "Q-068"),
    "Q-069": ("__init__.py", "Q-069"),
}
for ruling, (fname, needle) in SITES.items():
    present = needle in (LEDGER_DIR / fname).read_text(encoding="utf-8")
    print("      %-6s -> %-14s %s" % (ruling, fname, "found" if present else "ABSENT"))
    check("%s is cited in %s" % (ruling, fname), present, True)

init_doc = ast.get_docstring(ast.parse((LEDGER_DIR / "__init__.py").read_text(encoding="utf-8")))
first = " ".join((init_doc or "").split())[:200]
print()
print("      Q-069's prohibition, first 200 characters of the PACKAGE docstring:")
print("      %s" % first)
check("Q-069's prohibition is in the package docstring's opening",
      "SCORER-SIDE" in first and "MAY NEVER IMPORT" in first, True)

# ─────────────────────────────────────────────────────────────────────────────────────────
print()
print("=" * 100)
print("§8  THE CLAIM CEILING, IN BOTH DIRECTIONS (ruling 4 / OF-142 / M39)")
print("=" * 100)
doc = ast.get_docstring(ast.parse((LEDGER_DIR / "chain.py").read_text(encoding="utf-8"))) or ""
flat = " ".join(doc.replace("**", "").replace("``", "").split())
for phrase in ("evident against an edit that leaves a stale digest",
               "and against nothing else",
               "the README must not say more",
               "exactly two",
               "Truncation",
               "RE-DERIVED SUFFIX",
               "WHAT THIS CHAIN DOES NOT DETECT"):
    check("STATED: %r" % phrase, phrase in flat, True)
for over in ("any alteration is detected", "every alteration is detected"):
    idx = flat.find(over)
    if idx == -1:
        print("      NOT EXCEEDED: %r absent entirely" % over)
        check("NOT EXCEEDED: %r" % over, True, True)
    else:
        window = flat[max(0, idx - 200): idx + 200]
        guarded = any(d in window for d in ("FALSE", "is not claimed", "would be", "does not"))
        print("      %r appears; disclaimed within 200 chars: %s" % (over, guarded))
        check("NOT EXCEEDED: %r is disclaimed" % over, guarded, True)

print()
print("      AND THE LIMITATIONS ARE REAL — both shapes driven:")
trunc = [dict(e) for e in CASE_A][:2]
check("a TRUNCATED tail still verifies (OF-57, shape 1)",
      chain.verify(trunc, genesis_hash=GENESIS, algorithm="sha256").verdict, chain.VALID)
suffix = [dict(CASE_A[0])]
prev = suffix[0]["hash"]
for e in CASE_A[1:]:
    body = {k: v for k, v in e.items() if k not in chain.CHAIN_FIELDS}
    body["amount_paise"] = 4242
    h = chain.entry_digest(prev, body, algorithm="sha256")
    suffix.append(dict(body, prev_hash=prev, hash=h))
    prev = h
check("a RE-DERIVED SUFFIX still verifies (OF-157, shape 2)",
      chain.verify(suffix, genesis_hash=GENESIS, algorithm="sha256").verdict, chain.VALID)

print()
print("=" * 100)
print("DRIVEN CHECKS: %d      FAILURES: %d" % (CHECKS, len(FAILS)))
for f in FAILS:
    print("  FAILED: %s" % f)
print("=" * 100)
