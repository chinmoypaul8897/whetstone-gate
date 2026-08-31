"""REVIEW C3 / attempt 1 — token a66c389d — INDEPENDENT (blind) derivation.

Method is deliberately NOT whetstone_gate's. Nothing under src/whetstone_gate/ is
imported or read. Inputs: the vendored Sierra checkout only, at the pinned SHA.

WRITE tools are identified from the DECORATOR, two independent ways:
  (A) ast parse of the domain tools.py  -- no import, no litellm
  (B) runtime import of the ToolKit class, reading __tool_type__ off _func_tools
and (A) vs (B) are diffed. A hand-list is never used.
"""

import ast
import json
import os
import sys

VENDOR = os.path.join("vendor", "tau2-bench")
SRC = os.path.join(VENDOR, "src")
DATA = os.path.join(VENDOR, "data", "tau2", "domains")

TOOL_DECORATORS = {"is_tool", "is_discoverable_tool"}


# ---------------------------------------------------------------- (A) ast pass
def _decorator_tool_type(dec):
    """Return (is_a_tool, tool_type_str_or_None, mutates_state_node) for a decorator node."""
    if not isinstance(dec, ast.Call):
        # bare @is_tool with no parens would be a Name/Attribute
        name = dec.attr if isinstance(dec, ast.Attribute) else getattr(dec, "id", None)
        if name in TOOL_DECORATORS:
            return True, "READ", None  # decorator default per toolkit.py signature
        return False, None, None
    fn = dec.func
    name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
    if name not in TOOL_DECORATORS:
        return False, None, None

    tt = None
    if dec.args:
        tt = dec.args[0]
    for kw in dec.keywords:
        if kw.arg == "tool_type":
            tt = kw.value
    mutates = None
    for kw in dec.keywords:
        if kw.arg == "mutates_state":
            mutates = ast.dump(kw.value)

    if tt is None:
        return True, "READ", mutates  # signature default
    if isinstance(tt, ast.Attribute) and getattr(tt.value, "id", None) == "ToolType":
        return True, tt.attr, mutates
    if isinstance(tt, ast.Constant):
        return True, str(tt.value).upper(), mutates
    return True, "UNRESOLVED:" + ast.dump(tt), mutates


def ast_tools(domain):
    """{tool_name: (tool_type, mutates_state_override)} for every @is_tool* in the domain."""
    path = os.path.join(SRC, "tau2", "domains", domain, "tools.py")
    tree = ast.parse(open(path, encoding="utf-8").read(), path)
    out = {}
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append((node.name, [ast.unparse(b) for b in node.bases]))
            for item in node.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for dec in item.decorator_list:
                    ok, tt, mut = _decorator_tool_type(dec)
                    if ok:
                        out[item.name] = (tt, mut)
    return out, classes


# ------------------------------------------------------------ (B) runtime pass
def runtime_tools(domain, klass):
    sys.path.insert(0, SRC)
    mod = __import__("tau2.domains.%s.tools" % domain, fromlist=["x"])
    cls = getattr(mod, klass)
    out = {}
    for name, fn in cls._func_tools.fget(cls.__new__(cls)).items():
        out[name] = (
            getattr(fn, "__tool_type__").value.upper(),
            getattr(fn, "__mutates_state__"),
        )
    return out


# ------------------------------------------------------------------- task load
def tasks(domain):
    return json.load(open(os.path.join(DATA, domain, "tasks.json"), encoding="utf-8"))


def actions_of(task):
    ec = task.get("evaluation_criteria") or {}
    return ec.get("actions") or []


def main():
    report = {}
    print("=" * 72)
    print("PART A — WRITE TOOL IDENTIFICATION, FROM THE DECORATOR")
    print("=" * 72)

    write_tools = {}
    all_tools = {}
    for domain, klass in [("airline", "AirlineTools"), ("retail", "RetailTools")]:
        a, classes = ast_tools(domain)
        print("\n[%s] classes: %s" % (domain, classes))
        print("[%s] ast: %d decorated tools" % (domain, len(a)))
        for n in sorted(a):
            print("    %-34s %-8s mutates_state_override=%s" % (n, a[n][0], a[n][1]))
        w = sorted(n for n, (tt, _) in a.items() if tt == "WRITE")
        print("[%s] ast WRITE (%d): %s" % (domain, len(w), w))
        write_tools[domain] = set(w)
        all_tools[domain] = set(a)
        report[domain + "_write_tools"] = w

    print("\n" + "=" * 72)
    print("PART A2 — RUNTIME CROSS-CHECK (import, read __tool_type__)")
    print("=" * 72)
    for domain, klass in [("airline", "AirlineTools"), ("retail", "RetailTools")]:
        try:
            r = runtime_tools(domain, klass)
        except Exception as e:  # pragma: no cover
            print("[%s] RUNTIME FAILED: %r" % (domain, e))
            continue
        a, _ = ast_tools(domain)
        rw = set(n for n, (tt, _) in r.items() if tt == "WRITE")
        aw = set(n for n, (tt, _) in a.items() if tt == "WRITE")
        print("[%s] runtime tools=%d  WRITE=%d" % (domain, len(r), len(rw)))
        print("[%s] ast==runtime tool set   : %s" % (domain, set(a) == set(r)))
        print("[%s] ast==runtime WRITE set  : %s" % (domain, aw == rw))
        if aw != rw:
            print("    ONLY-AST: %s  ONLY-RUNTIME: %s" % (aw - rw, rw - aw))
        ms = sorted(n for n, (_, m) in r.items() if m)
        print("[%s] mutates_state=True (%d): %s" % (domain, len(ms), ms))

    print("\n" + "=" * 72)
    print("PART B — MUST-NOT-WRITE ENUMERATION")
    print("=" * 72)
    totals = {}
    partitions = {}
    for domain in ("airline", "retail"):
        ts = tasks(domain)
        empty, readonly, write = [], [], []
        unknown_names = {}
        requestors = {}
        for t in ts:
            acts = actions_of(t)
            for a in acts:
                requestors[a.get("requestor")] = requestors.get(a.get("requestor"), 0) + 1
                if a.get("name") not in all_tools[domain]:
                    unknown_names.setdefault(a.get("name"), []).append(t["id"])
            if not acts:
                empty.append(t["id"])
            elif any(a.get("name") in write_tools[domain] for a in acts):
                write.append(t["id"])
            else:
                readonly.append(t["id"])
        mnw = empty + readonly
        totals[domain] = len(ts)
        partitions[domain] = dict(empty=empty, readonly=readonly, write=write, mnw=mnw)
        print("\n[%s] total=%d  empty=%d  read-only=%d  must-not-write=%d  write=%d"
              % (domain, len(ts), len(empty), len(readonly), len(mnw), len(write)))
        print("[%s] partition sums to total: %s"
              % (domain, len(empty) + len(readonly) + len(write) == len(ts)))
        print("[%s] requestor census: %s" % (domain, requestors))
        print("[%s] action names NOT in the domain toolkit: %s"
              % (domain, unknown_names if unknown_names else "NONE"))
        print("[%s] empty ids   : %s" % (domain, sorted(empty, key=int)))
        print("[%s] readonly ids: %s" % (domain, sorted(readonly, key=int)))

    tot = totals["airline"] + totals["retail"]
    mnw = len(partitions["airline"]["mnw"]) + len(partitions["retail"]["mnw"])
    wr = len(partitions["airline"]["write"]) + len(partitions["retail"]["write"])
    print("\n>>> COMBINED: %d must-not-write of %d ; write tasks = %d" % (mnw, tot, wr))
    print(">>> mnw + write == total : %s" % (mnw + wr == tot))

    print("\n" + "=" * 72)
    print("PART C — reward_basis CENSUS (airline, retail, telecom)")
    print("=" * 72)
    for domain in ("airline", "retail", "telecom"):
        ts = tasks(domain)
        c = {}
        for t in ts:
            rb = (t.get("evaluation_criteria") or {}).get("reward_basis")
            k = tuple(rb) if rb else None
            c[k] = c.get(k, 0) + 1
        print("[%s] n=%d  %s" % (domain, len(ts), {str(k): v for k, v in sorted(c.items(), key=lambda x: -x[1])}))
        print("[%s] census sums to total: %s" % (domain, sum(c.values()) == len(ts)))
        print("[%s] 'DB' in basis: %d task(s)"
              % (domain, sum(v for k, v in c.items() if k and "DB" in k)))

    print("\n" + "=" * 72)
    print("PART D — T-FP SELECTION (write tasks, 20 airline + 20 retail)")
    print("=" * 72)
    for domain in ("airline", "retail"):
        w = partitions[domain]["write"]
        bytewise = sorted(w)[:20]
        numeric = sorted(w, key=lambda s: int(s))[:20]
        print("\n[%s] write-task count = %d" % (domain, len(w)))
        print("[%s] BYTEWISE (sorted on the str id, my rule) first 20:\n    %s" % (domain, bytewise))
        print("[%s] NUMERIC  (sorted on int(id))          first 20:\n    %s" % (domain, numeric))
        print("[%s] bytewise == numeric ? %s   (symmetric difference: %s)"
              % (domain, bytewise == numeric, sorted(set(bytewise) ^ set(numeric), key=int)))
    tfp = sorted(partitions["airline"]["write"])[:20] + sorted(partitions["retail"]["write"])[:20]
    print("\n>>> T-FP (bytewise, 20 airline then 20 retail), %d ids:" % len(tfp))
    print(json.dumps(tfp))
    print(">>> id python type in tasks.json: %s"
          % {type(t["id"]).__name__ for t in tasks("airline") + tasks("retail")})


main()
