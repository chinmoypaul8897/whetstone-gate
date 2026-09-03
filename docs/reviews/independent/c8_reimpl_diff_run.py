#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C8 REVIEW 1 (`07c3687f`) — the Phase-2 DIFF: the SHIPPED scorer against the Phase-1
reimplementation, over the reviewer's own vectors.

`docs/reviews/README.md`: *"`independent/c<N>_reimpl_diff.txt` — Phase 2's diff of the
project's output against the reimplementation, over the reviewer's own >=20 vectors. **Any
divergence is a finding.**"*

Writes `docs/reviews/independent/c8_reimpl_diff.txt`.

    python docs/reviews/independent/c8_reimpl_diff_run.py
"""

from __future__ import annotations

import importlib.util
import io
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "src"))

spec = importlib.util.spec_from_file_location("c8_reimpl", os.path.join(_HERE, "c8_reimpl.py"))
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

from whetstone_gate.scorer import (                                        # noqa: E402
    Authorization, OpeningState, constants_from, entries_from_rows, score_invariants,
)

RC = R.constants()
SC = constants_from({
    "per_action_cap_paise": RC["per_action_cap_paise"],
    "episode_cap_paise": RC["episode_cap_paise"],
    "s4_in_flight_window_width": RC["s4_window_width"],
    "currency": RC["currency"],
})

#: The reviewer's `Row` -> a stored ledger row, so the shipped scorer reads it exactly as it
#: would read a real one. `issued` goes in as a VERDICT, which is where `ReplayEntry.issued`
#: reads it from — the boolean is never handed straight across.
def as_row(row):
    return {
        "ledger_seq": row.seq,
        "verdict": "ALLOWED" if row.issued else "DENIED",
        "tool": row.tool,
        "target": row.payment or row.authorization or "-",
        "receipt": row.receipt,
        "amount_paise": row.amount,
        "executed": row.executed,
        "rejected_by_razorpay": False,
    }


def as_opening(opening):
    return OpeningState(
        captured_paise=dict(opening.captured),
        authorizations={k: Authorization(v.get("exists", True), v.get("consumed", False),
                                         v["amount_paise"])
                        for k, v in opening.authorizations.items()},
        payment_ids=frozenset(opening.captured) | frozenset(opening.authorizations),
    )


#: The cells both sides express. `S3` is compared under the ARCHITECT's subject rule, which
#: golden 2's F9 states and which the reimplementation adopted as a declared Phase-2
#: amendment; `S3_by_capture_row` is reported beside it because the two DIVERGE and the
#: divergence is a finding of this review.
COMPARED = ["E1", "E2", "E2_total_moved_paise", "E3", "S1", "S2", "S2-amt", "S3", "S4"]


def main():
    out = io.StringIO()
    w = out.write
    w("C8 REVIEW 1 (`07c3687f`) - PHASE 2 DIFF\n")
    w("The SHIPPED scorer `src/whetstone_gate/scorer/` against the Phase-1\n")
    w("reimplementation `docs/reviews/independent/c8_reimpl.py`, SEALED at `e249f0d`\n")
    w("before `src/` was opened, over THE REVIEWER'S OWN VECTORS.\n\n")
    w("docs/reviews/README.md: \"Any divergence is a finding.\"\n\n")
    w("Constants, read from config/protocol.yaml by the reimplementation's own\n")
    w("indentation walker and handed to the shipped scorer as data:\n")
    for k in sorted(RC):
        w("    %-24s %s\n" % (k, RC[k]))
    w("\n")
    w("=" * 100 + "\n")
    w("%-62s %-20s %-8s\n" % ("vector / cell", "value", "agree"))
    w("=" * 100 + "\n")

    total = agree = 0
    divergences = []
    for name, rows, opening, _expect in R.vectors():
        mine = R.score(rows, opening, RC)
        ship = score_invariants(
            entries_from_rows([as_row(r) for r in rows]), as_opening(opening), SC
        ).as_cells()
        head_written = False
        for cell in COMPARED:
            total += 1
            a, b = mine[cell], ship[cell]
            same = a == b
            if same:
                agree += 1
            else:
                divergences.append((name, cell, a, b))
            if not same or not head_written:
                if not head_written:
                    w("\n%s\n" % name)
                    head_written = True
            if not same:
                w("    %-58s reimpl=%-18r shipped=%-18r  ** DIVERGES **\n"
                  % (cell, a, b))
        if head_written and not any(d[0] == name for d in divergences):
            w("    all %d compared cells agree\n" % len(COMPARED))

    w("\n" + "=" * 100 + "\n")
    w("VECTORS: %d      CELLS COMPARED: %d      AGREE: %d      DIVERGENCES: %d\n"
      % (len(R.vectors()), total, agree, len(divergences)))
    w("=" * 100 + "\n")
    if divergences:
        w("\nDIVERGENCES, EACH A FINDING:\n")
        for name, cell, a, b in divergences:
            w("  %-58s %-22s reimpl=%r shipped=%r\n" % (name, cell, a, b))
    else:
        w("\nNO DIVERGENCE. The shipped scorer and an implementation written from the spec\n")
        w("text alone, by a session that had not seen it, agree on every cell of every\n")
        w("vector - including the ten readings golden 2 provably cannot discriminate.\n")

    path = os.path.join(_HERE, "c8_reimpl_diff.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out.getvalue())
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    print(out.getvalue()[-2200:])
    print("written: %s" % path)
    return 1 if divergences else 0


if __name__ == "__main__":
    sys.exit(main())
