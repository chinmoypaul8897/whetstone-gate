"""C2 REVIEW 1 — PHASE 2a. Diff C2's generator against the blind reimplementation.

Session `94116fe2`. Runs `whetstone_gate.world` (the LIVE editable-installed tree — INC-17)
against the thirty-one vectors this session committed in phase 1, and reports every
divergence field by field.

⚠️ INC-17: this prints `whetstone_gate.__file__` first. A run that does not state which
tree it loaded is not evidence.

⚠️ **The report is written HERE with `newline="\n"`, never redirected through the shell.**
The first run of this harness used `> c2_reimpl_diff.txt` on Windows and wrote CRLF into a
tracked file, turning `test_gitattributes_is_correct_and_in_the_first_commit` (check A3) and
`test_the_object_store_and_the_working_tree_agree` RED. That is the same class of mistake
this chunk's review prompt names — *"write files with your editor/write tools, not shell
heredocs"* — reached by a different route, and the fix is to take the shell out of the path.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import c2_reimpl as R
import c2_vectors as V

import whetstone_gate
from whetstone_gate.world import generate, load_world_spec
from whetstone_gate.world.amounts import exact_u, log_uniform_paise, rounding_mode
from whetstone_gate.world.prng import Mulberry32
from decimal import Context


def world_to_plain(world) -> dict:
    """C2's frozen dataclasses, rendered into the same plain shape the reimpl returns."""
    return {
        "seed": world.seed,
        "prng": {
            "algorithm": "mulberry32",
            "draws_consumed": len(world.raw_draws),
            "raw_u32": list(world.raw_draws),
        },
        "merchant_available_balance_paise": world.merchant_available_balance_paise,
        "payments": [
            {
                "index": p.index,
                "id": p.id,
                "status": p.status,
                "amount_paise": p.amount_paise,
                "amount_captured_paise": p.amount_captured_paise,
                "amount_refunded_paise": p.amount_refunded_paise,
                "currency": p.currency,
                "created_at": p.created_at,
                "notes": dict(p.notes),
            }
            for p in world.payments
        ],
    }


def main() -> int:
    print("C2 REVIEW 1 — PHASE 2a — REIMPLEMENTATION DIFF")
    print("session 94116fe2")
    print()
    print("INC-17 EVIDENCE — the tree actually loaded:")
    print(f"  whetstone_gate.__file__ = {whetstone_gate.__file__}")
    print(f"  sys.executable          = {sys.executable}")
    print(f"  reimplementation        = {R.__file__}")
    print()

    spec = load_world_spec()
    context = Context(prec=spec.decimal_context_precision)
    rounding = rounding_mode(spec.rounding)

    divergences = 0

    # ---- the sixteen raw-draw vectors, on the amount path ------------------------------
    print("=" * 78)
    print("A. SIXTEEN RAW-DRAW VECTORS — the amount path")
    print("=" * 78)
    print(f"{'raw':>12} {'reimpl':>10} {'C2':>10}  u agrees  verdict")
    for raw, why in V.RAW_VECTORS:
        mine = R.amount_paise_from_raw(raw)
        theirs = log_uniform_paise(
            exact_u(raw, context),
            minimum_paise=spec.amount_min_paise,
            maximum_paise=spec.amount_max_paise,
            context=context,
            rounding=rounding,
        )
        u_mine = R.u_exact(raw)
        u_theirs = exact_u(raw, context)
        u_ok = u_mine == u_theirs
        ok = mine == theirs and u_ok
        if not ok:
            divergences += 1
        print(
            f"{raw:>12} {mine:>10} {theirs:>10}  {str(u_ok):>8}  "
            f"{'AGREE' if ok else '*** DIVERGENCE ***'}"
        )
        print(f"{'':>12} why: {why}")

    # ---- the fifteen whole-seed vectors ------------------------------------------------
    print()
    print("=" * 78)
    print("B. FIFTEEN WHOLE-SEED VECTORS — all 12 payments, field for field, POSITIONALLY")
    print("=" * 78)
    for seed, why in V.SEED_VECTORS:
        mine = R.generate_world(seed)
        theirs = world_to_plain(generate(seed, spec))
        seed_diffs = []
        if mine["prng"]["raw_u32"] != theirs["prng"]["raw_u32"]:
            seed_diffs.append(
                f"raw_u32 reimpl={mine['prng']['raw_u32']} C2={theirs['prng']['raw_u32']}"
            )
        if (
            mine["merchant_available_balance_paise"]
            != theirs["merchant_available_balance_paise"]
        ):
            seed_diffs.append("merchant_available_balance_paise")
        if len(mine["payments"]) != len(theirs["payments"]):
            seed_diffs.append(
                f"payment count reimpl={len(mine['payments'])} C2={len(theirs['payments'])}"
            )
        else:
            # POSITIONAL, not set-wise: index i of one against index i of the other.
            for a, b in zip(mine["payments"], theirs["payments"]):
                for key in a:
                    if a[key] != b.get(key):
                        seed_diffs.append(
                            f"payment[{a['index']}].{key}: reimpl={a[key]!r} C2={b.get(key)!r}"
                        )
        if seed_diffs:
            divergences += len(seed_diffs)
            print(f"seed {seed:<12} *** {len(seed_diffs)} DIVERGENCE(S) ***")
            for d in seed_diffs:
                print(f"    {d}")
        else:
            print(f"seed {seed:<12} AGREE  — 11 raw draws, balance, 12 payments x 9 fields")
        print(f"{'':>17} why: {why}")

    # ---- out-of-domain probes, reported separately -------------------------------------
    print()
    print("=" * 78)
    print("C. OUT-OF-DOMAIN PROBES — reported, NOT counted as findings")
    print("=" * 78)
    print("§8.6's seed list is 2001-2050 plus 2101-2110. Behaviour outside it is undefined")
    print("by the specification, so a divergence here is recorded and is not a finding.")
    for seed, why in V.OUT_OF_DOMAIN_SEEDS:
        try:
            mine = R.generate_world(seed)["prng"]["raw_u32"]
        except Exception as exc:
            mine = f"{type(exc).__name__}: {exc}"
        try:
            theirs = list(generate(seed, spec).raw_draws)
        except Exception as exc:
            theirs = f"{type(exc).__name__}: {exc}"
        print(f"seed {seed}: {'AGREE' if mine == theirs else 'differ'}")
        print(f"    reimpl = {mine}")
        print(f"    C2     = {theirs}")
        print(f"    why: {why}")

    # ---- the raw stream itself, beyond the 11-draw budget -------------------------------
    print()
    print("=" * 78)
    print("D. THE RAW STREAM BEYOND THE ELEVEN-DRAW BUDGET")
    print("=" * 78)
    print("Golden 7 pins eleven draws. A generator that agreed on eleven and diverged on")
    print("the twelfth would still be wrong, and a later chunk taking more draws would")
    print("silently move every number. 200 draws are compared on each of six seeds.")
    for seed in (2001, 2005, 2046, 2050, 2101, 2110):
        mine = R.mulberry32_raw_sequence(seed, 200)
        gen = Mulberry32(seed)
        theirs = [gen.next_u32() for _ in range(200)]
        ok = mine == theirs
        if not ok:
            divergences += 1
            first = next(i for i, (x, y) in enumerate(zip(mine, theirs)) if x != y)
            print(f"seed {seed}: *** DIVERGENCE at draw {first} ***")
        else:
            print(f"seed {seed}: AGREE on all 200 draws")

    print()
    print("=" * 78)
    print(f"TOTAL DIVERGENCES: {divergences}")
    print("=" * 78)
    return 0 if divergences == 0 else 1


if __name__ == "__main__":
    buffer = io.StringIO()
    real_stdout, sys.stdout = sys.stdout, buffer
    try:
        code = main()
    finally:
        sys.stdout = real_stdout
    report = Path(__file__).with_name("c2_reimpl_diff.txt")
    with report.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(buffer.getvalue())
    print(buffer.getvalue())
    print(f"[written to {report} with LF line endings]")
    raise SystemExit(code)
