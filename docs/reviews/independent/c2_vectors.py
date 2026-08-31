"""C2 REVIEW 1 — PHASE 1 (BLIND) INPUT VECTORS, chosen by this review session.

Session `94116fe2`. THIRTY-ONE vectors — sixteen raw-draw vectors on the amount path and
fifteen whole-seed vectors — none of them taken from `tests/`, from `tests/goldens/`, or
from any build artefact. They were chosen from `CONTEXT.md` §8.6a's own boundary language
plus two searches this session ran over seeds 0–199,999 with its own reimplementation.

⚠️ Committed BEFORE phase 2 opened `src/whetstone_gate/world/`, so the expected values in
`c2_reimpl_expected.json` cannot have been back-fitted to the code under review.

BOUNDARIES §8.6a NAMES, AND WHERE EACH IS COVERED
  `u = 0`                                    → RAW_VECTORS[0]  (must give exactly 50000)
  `u = 2**32 - 1`                            → RAW_VECTORS[6]  (must give exactly 15000000)
  the exact half-up rounding case            → RAW_VECTORS[8..12] — see HALF_UP_NOTE below
  a seed clustering at the LOW end           → SEED_VECTORS: 16697, 49041
  a seed clustering at the HIGH end          → SEED_VECTORS: 32423, 153502
  one seed from the SCORED block 2001–2050   → 2001, 2005, 2046, 2050
  one seed from the LADDER block 2001–2005   → 2001, 2005
  one seed from the PILOT  block 2101–2110   → 2101, 2110

HALF_UP_NOTE — WHY NO RAW DRAW CAN PRODUCE AN *EXACT* TIE, STATED RATHER THAN GLOSSED.
  The amount is `context.exp(...)` at `prec=50`. An amount with 6–8 integer digits therefore
  carries 42–44 fractional digits. An exact `.5` tie requires every one of those digits
  after the `5` to be zero, i.e. a ~1-in-10^42 coincidence in a transcendental function.
  It is not constructible, and claiming a constructed tie would be the overclaim this
  project exists to catch. What IS constructible, and is here, is the pair that STRADDLES a
  boundary as closely as a 32-bit draw allows:
      raw 1894840345 → 619182.49999999987…  → HALF_UP rounds DOWN to 619182
      raw 3763271754 → 7403481.50000000163… → HALF_UP rounds UP   to 7403482
      raw 2949329170 → 2511856.49999999988… → the closest approach this session found,
                                               1.23e-10 paise below the boundary
  ⚠️ A CONSEQUENCE WORTH STATING, because it decides how a mutant must be judged: since no
  reachable input is an exact tie, `ROUND_HALF_UP → ROUND_HALF_EVEN` and
  `ROUND_HALF_UP → ROUND_HALF_DOWN` move NO VALUE the world can ever produce. They are
  value-invisible mutants of a §8.6-table constant, and only a structural check can kill
  them. That is exactly the class C2 BUILD found with `ast.Div`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import c2_reimpl as R


# --- Sixteen raw-draw vectors on the amount path ---------------------------------------
# (raw, why this vector exists)
RAW_VECTORS: list[tuple[int, str]] = [
    (0, "u = 0 — §8.6a: 'u = 0 gives exactly 50000'. The closed interval's floor."),
    (1, "u = 2^-32 — one step off the floor; the smallest non-zero draw."),
    (677, "the LOWEST raw this session found over seeds 0-199999 (seed 49041, draw 1)."),
    (1073741824, "u = exactly 0.25 — an exact dyadic rational, no rounding in `u` itself."),
    (2147483648, "u = exactly 0.50 — the midpoint; geometric mean of the interval."),
    (3221225472, "u = exactly 0.75."),
    (4294967295, "u = 2^32 - 1 — §8.6a: 'u -> 1 gives exactly 15000000'. The ceiling."),
    (4294967294, "one step below the ceiling."),
    (4294954628, "the HIGHEST raw this session found over seeds 0-199999 (seed 153502)."),
    (1894840345, "straddle LOW: amount 619182.49999999987... -> HALF_UP rounds DOWN."),
    (3763271754, "straddle HIGH: amount 7403481.50000000163... -> HALF_UP rounds UP."),
    (2949329170, "CLOSEST approach found to a .5 boundary: 1.23e-10 paise below it."),
    (4174750378, "12786632.50000000661... -> rounds UP; the largest straddle found."),
    (4167386882, "Q-023's own witness draw (seed 2046, index 3) - re-derived here."),
    (2863311530, "0xAAAAAAAA - an alternating bit pattern belonging to no seed's draw."),
    (1431655765, "0x55555555 - its complement; exercises the shift/XOR path differently."),
]

# --- Fifteen whole-seed vectors ---------------------------------------------------------
SEED_VECTORS: list[tuple[int, str]] = [
    (2001, "SCORED + LADDER. The golden-7 seed; the only cross-check that already exists."),
    (2002, "LADDER. Adjacent to the golden - catches an off-by-one in seed handling."),
    (2005, "LADDER, last. The ladder block's upper edge."),
    (2046, "SCORED. Q-023's witness seed - the closest approach over the frozen 660."),
    (2050, "SCORED, last. The scored block's upper edge."),
    (2101, "PILOT, first. Disjoint from the scored set by construction."),
    (2110, "PILOT, last. The pilot block's upper edge."),
    (16697, "LOW-END CLUSTER: 7 of its 11 draws fall in the bottom decile of u."),
    (32423, "HIGH-END CLUSTER: 7 of its 11 draws fall in the top decile of u."),
    (81859, "WIDEST SPAN found: raw 880881 and raw 4293618963 in the same seed."),
    (49041, "carries the lowest raw found (677 -> the interval floor, 50000 paise)."),
    (153502, "carries the highest raw found (4294954628 -> 14999748 paise)."),
    (0, "seed 0 - the degenerate seed; `a` starts at the additive identity."),
    (1, "seed 1."),
    (4294967295, "seed 2^32 - 1 - the seed at the 32-bit mask boundary."),
]

# --- Out-of-domain robustness probes, reported SEPARATELY -------------------------------
# §8.6's seed list is 2001-2050 plus 2101-2110, so these are outside anything the project
# generates. A divergence here is REPORTED but is NOT a finding on its own: the spec does
# not define behaviour for them, and inventing a requirement would be manufacturing one.
OUT_OF_DOMAIN_SEEDS: list[tuple[int, str]] = [
    (4294967296, "seed 2^32 - probes whether the seed is masked into 32 bits before use."),
    (-1, "a negative seed - probes the sign handling of the initial state."),
]


def emit() -> dict:
    out = {
        "_comment": (
            "C2 REVIEW 1 (session 94116fe2) - expected values computed by "
            "docs/reviews/independent/c2_reimpl.py ALONE, which imports nothing from src/. "
            "Committed in PHASE 1, before any build source was opened."
        ),
        "raw_vectors": [],
        "seed_vectors": [],
        "out_of_domain_seeds": [],
    }
    for raw, why in RAW_VECTORS:
        out["raw_vectors"].append(
            {
                "raw": raw,
                "why": why,
                "u_10sf": R.u_to_10sf(raw),
                "u_exact_50": str(R.u_exact(raw)),
                "amount_unrounded_50": str(R.amount_exact_from_raw(raw)),
                "amount_paise": R.amount_paise_from_raw(raw),
            }
        )
    for seed, why in SEED_VECTORS:
        w = R.generate_world(seed)
        out["seed_vectors"].append({"seed": seed, "why": why, "world": w})
    for seed, why in OUT_OF_DOMAIN_SEEDS:
        try:
            w = R.generate_world(seed)
        except Exception as exc:  # pragma: no cover - documented, not asserted
            w = {"error": f"{type(exc).__name__}: {exc}"}
        out["out_of_domain_seeds"].append({"seed": seed, "why": why, "world": w})
    return out


if __name__ == "__main__":
    # ⚠️ WRITTEN HERE WITH `newline="\n"` RATHER THAN REDIRECTED THROUGH THE SHELL.
    # The first run of this file redirected stdout on Windows, which wrote CRLF into a
    # tracked file and turned `test_gitattributes_is_correct_and_in_the_first_commit`
    # (check A3) and `test_the_object_store_and_the_working_tree_agree` RED — the working
    # tree and the object store disagreed, which is exactly the condition `PROCESS.md` §6a
    # says would make the pre-registration fingerprint depend on which OS computed it.
    # Taking the shell out of the path is the fix; `newline="\n"` is what enforces it.
    target = Path(__file__).with_name("c2_reimpl_expected.json")
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(emit(), handle, indent=2, sort_keys=False)
        handle.write("\n")
    sys.stdout.write(f"wrote {target} with LF line endings\n")
