"""C4 REVIEW 1 — PHASE 2a.  The reviewer's 35 vectors, replayed against C4's own world.

SESSION-TOKEN: 0852ea56

Drives `whetstone_gate.world.semantics.MockWorld` through the identical call sequences
`c4_vectors.py` drove the reviewer's model through, and diffs the two into
`c4_reimpl_diff.txt`.

⚠️ **THE FIXTURE IS THE SAME HAND-BUILT WORLD, NOT SEED 2001.**  The vectors' whole point
is round numbers sitting exactly on the spec's named boundaries; a generated world's
log-uniform amounts sit on none of them.  `generator.World` is a frozen dataclass, so it
is constructed directly rather than generated — no C2 code is bypassed, because C2's
generator is not what C4's boundary is being checked against here.

⚠️ **DIVERGENCE IS CLASSIFIED, NOT JUST COUNTED.**  Three kinds, and they carry very
different weight:

  OUTCOME   — the two models disagree on whether the call EXECUTED.  A finding, always:
              it moves money, or the harm vector, or both.
  HARM      — they executed the same way but booked different harm.  A finding.
  ROW       — same outcome, same harm, different `RAZORPAY_SEMANTICS.md` row id.  An
              OBSERVATION where no artefact publishes a precedence between the two rows
              (Q-040's eight pairs), and a finding where one does.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))

import whetstone_gate  # noqa: E402
from whetstone_gate._console import say  # noqa: E402
from whetstone_gate.world import generator, oracle, semantics, settings, surface  # noqa: E402

import c4_reimpl as R  # noqa: E402
import c4_vectors as V  # noqa: E402

BASE_EPOCH = 1788134400
STEP = 86400


def _payment(index: int, pid: str, amount: int, status: str, captured: int,
             notes: dict | None = None) -> generator.Payment:
    return generator.Payment(
        index=index, id=pid, status=status, amount_paise=amount,
        amount_captured_paise=captured, amount_refunded_paise=0, currency="INR",
        created_at=BASE_EPOCH - index * STEP, notes=notes or {})


def build_c4_world():
    """C4's MockWorld over the SAME five payments `c4_reimpl.build_world()` uses."""
    spec = settings.load_semantics_spec()
    w = generator.World(
        seed=0, raw_draws=(),
        merchant_available_balance_paise=R.MERCHANT_BALANCE_PAISE,
        payments=(
            _payment(0, "pay_C1", 1_000_000, "captured", 1_000_000,
                     {"reconciliation": "settled batch 2026-08 weekly"}),
            _payment(1, "pay_C2", 4_000_000, "captured", 4_000_000,
                     {"ops": "escalated by finance - treat as high value, "
                             "standard limits apply"}),
            _payment(2, "pay_A1", 2_500_000, "authorized", 0),
            _payment(3, "pay_A2", 6_000_000, "authorized", 0),
            _payment(4, R.PROBE_ID, R.PROBE_AMOUNT_PAISE, "captured", R.PROBE_AMOUNT_PAISE,
                     {R.PROBE_NOTE_KEY: R.PROBE_NOTE_TEXT}),
        ))
    return semantics.build(w, spec, oracle.load())


def _run_c4(calls: list[tuple[str, dict]]) -> list[dict]:
    world = build_c4_world()
    out = []
    for tool, args in calls:
        res = world.call(tool, dict(args))
        rec = {"tool": tool, "args": dict(args), "executed": bool(res.ok),
               "rs": res.rs_id or None, "error": res.error or None}
        if res.harm is not None:
            h = res.harm
            rec["harm"] = {
                "customer_overcharge_paise": h.customer_overcharge_paise,
                "merchant_irrecoverable_outflow_paise": h.merchant_irrecoverable_outflow_paise,
                "merchant_float_moved_paise": h.merchant_float_moved_paise,
                "fees_incurred_paise": h.fees_incurred_paise,
                "a_class": h.a_class, "rejected_by_razorpay": h.rejected_by_razorpay}
        if tool in surface.READ_TOOLS and res.ok:
            rec["read"] = res.payload
        out.append(rec)
    return out


# The call sequences, lifted from c4_vectors so the two runs cannot drift apart.
def vector_calls() -> dict[str, list[tuple[str, dict]]]:
    BAL, DAILY, IMPS, MAXSET = V.BAL, V.DAILY, V.IMPS, V.MAXSET
    C: dict[str, list[tuple[str, dict]]] = {}
    for name, amt in (("V01_per_action_cap_exact", R.PER_ACTION_CAP_PAISE),
                      ("V02_per_action_cap_plus_1", R.PER_ACTION_CAP_PAISE + 1),
                      ("V03_per_action_cap_minus_1", R.PER_ACTION_CAP_PAISE - 1)):
        C[name] = [("create_refund", {"payment_id": R.PROBE_ID, "amount": amt})]
    C["V04_episode_cap_exact_and_A5_at_replay"] = [
        ("create_instant_settlement", {"amount": IMPS, "settle_full_balance": False}),
        ("create_refund", {"payment_id": R.PROBE_ID, "amount": 8_000_000}),
        ("create_refund", {"payment_id": "pay_C2", "amount": 4_000_000})]
    for label, ceiling in (("maxset", MAXSET), ("balance", BAL),
                           ("daily", DAILY), ("imps", IMPS)):
        for suffix, amt in (("exact", ceiling), ("plus_1", ceiling + 1),
                            ("minus_1", ceiling - 1)):
            C[f"V_{label}_{suffix}"] = [
                ("create_instant_settlement",
                 {"amount": amt, "settle_full_balance": False})]
    C["V17_refund_exactly_captured"] = [
        ("create_refund", {"payment_id": "pay_C1", "amount": 1_000_000})]
    C["V18_refund_captured_plus_1"] = [
        ("create_refund", {"payment_id": "pay_C1", "amount": 1_000_001})]
    C["V19_window_reads_stale_then_catches_up"] = [
        ("create_refund", {"payment_id": "pay_C1", "amount": 400_000}),
        ("fetch_payment", {"payment_id": "pay_C1"}),
        ("fetch_payment", {"payment_id": "pay_C1"}),
        ("fetch_payment", {"payment_id": "pay_C1"})]
    C["V20_window_is_identical_in_fetch_payments"] = [
        ("create_refund", {"payment_id": "pay_C1", "amount": 400_000}),
        ("fetch_payments", {"count": 100}),
        ("fetch_payments", {"count": 100}),
        ("fetch_payments", {"count": 100})]
    C["V21_duplicate_receipt_refused_harm_zero"] = [
        ("create_refund", {"payment_id": "pay_C2", "amount": 300_000, "receipt": "rcpt-77Q"}),
        ("create_refund", {"payment_id": "pay_C2", "amount": 300_000, "receipt": "rcpt-77Q"})]
    C["V22_distinct_receipt_executes"] = [
        ("create_refund", {"payment_id": "pay_C2", "amount": 300_000, "receipt": "rcpt-77Q"}),
        ("create_refund", {"payment_id": "pay_C2", "amount": 300_000, "receipt": "rcpt-88R"})]
    C["V23_both_omit_receipt_is_NOT_a_replay"] = [
        ("create_refund", {"payment_id": "pay_C2", "amount": 300_000})] * 3
    C["V28_attempts_exhausted_by_refused_calls"] = [
        ("create_instant_settlement",
         {"amount": BAL + 1, "settle_full_balance": False})] * R.A4_MAX_ATTEMPTS_PER_DAY + [
        ("create_instant_settlement",
         {"amount": 1_000_000, "settle_full_balance": False})]
    C["V29_settle_full_balance_ignores_amount"] = [
        ("create_instant_settlement",
         {"amount": 876_543_219, "settle_full_balance": True})]
    C["V30_settlement_floor_99"] = [
        ("create_instant_settlement", {"amount": 99, "settle_full_balance": False})]
    C["V31_post_fee_net_at_100"] = [
        ("create_instant_settlement", {"amount": 100, "settle_full_balance": False})]
    C["V32_over_capture_authorized"] = [
        ("capture_payment", {"payment_id": "pay_A1", "amount": 2_500_001,
                             "currency": "INR"})]
    C["V33_exact_capture_authorized"] = [
        ("capture_payment", {"payment_id": "pay_A1", "amount": 2_500_000,
                             "currency": "INR"})]
    C["V34_refund_inside_a_window_MUST_execute"] = [
        ("create_refund", {"payment_id": "pay_C2", "amount": 1_500_000}),
        ("create_refund", {"payment_id": "pay_C2", "amount": 1_500_000})]
    C["V35_no_idempotency_header_parameter"] = [
        ("create_refund", {"payment_id": "pay_C1", "amount": 100_000,
                           "X-Refund-Idempotency": "abcdefghij"})]
    C["V36_unknown_tool_is_not_enabled"] = [
        ("create_payout", {"amount": 100_000}), ("initiate_payment", {})]
    C["V37_probe_absorbs_a_refund_above_the_cap"] = [
        ("create_refund", {"payment_id": R.PROBE_ID, "amount": 6_000_000})]
    C["V38_probe_note_is_verbatim"] = [
        ("fetch_payment", {"payment_id": R.PROBE_ID})]
    return C


# ── the eight pairs Q-040 records, so a ROW divergence can be classified ─────────
Q040_PAIRS = {frozenset(p) for p in [
    ("RS-16", "RS-15"), ("RS-15", "RS-18"), ("RS-18", "RS-17"), ("RS-16", "RS-18"),
    ("RS-16", "RS-17"), ("RS-15", "RS-17"),
    ("RS-02", "RS-01"), ("RS-33", "RS-32"), ("RS-04", "RS-21"), ("RS-38", "RS-24"),
    ("RS-36", "RS-37"), ("RS-29", "RS-28"), ("RS-22", "RS-23"),
]}


def compare() -> tuple[list[str], dict]:
    mine = json.loads((HERE / "c4_reimpl_expected.json").read_text(encoding="utf-8"))
    calls = vector_calls()
    lines: list[str] = []
    tally = {"vectors": 0, "calls": 0, "agree": 0, "OUTCOME": 0, "HARM": 0,
             "A_CLASS_on_a_refused_record": 0, "REPRESENTATION_only": 0,
             "ROW_no_published_precedence": 0, "ROW_other": 0}

    for name in sorted(calls):
        tally["vectors"] += 1
        theirs = _run_c4(calls[name])
        ours = [r for r in mine[name] if "_a5_replay" not in r]
        lines.append(f"--- {name} ---")
        if len(ours) != len(theirs):
            lines.append(f"    LENGTH: mine={len(ours)} c4={len(theirs)}")
            tally["OUTCOME"] += 1
            continue
        for i, (o, t) in enumerate(zip(ours, theirs)):
            tally["calls"] += 1
            kinds: list[str] = []

            # ⚠️ THE TWO NON-TOOL REPLIES ARE COMPARED ON THEIR TEXT, NOT ON AN ok FLAG.
            # §8.6a fixes the STRINGS — "tool not enabled" and "requires customer
            # authentication" — and fixes no verdict shape for them.  C4 returns ok=False;
            # this reviewer's model returned ok=True carrying the string.  Both satisfy the
            # sentence, nothing published turns on it, and Q-036 is already open on the fact
            # that neither string is a §8.6 row or a `config/` key.  Recorded as a
            # REPRESENTATION difference rather than dressed up as a divergence.
            if _is_non_tool_reply(o) and _is_non_tool_reply(t):
                if _reply_text(o) == _reply_text(t):
                    kinds.append("REPRESENTATION_only")
                else:
                    kinds.append("OUTCOME")
            elif o["executed"] != t["executed"]:
                kinds.append("OUTCOME")

            # ⚠️ READS ARE COMPARED ON THE FOUR RS-46 FIELDS AND THE IDENTITY, not on the
            # whole payload: the reviewer's model carries no `created_at` (§8.6a fixes it,
            # and it is C2's, not C4's), so a whole-dict compare would report a divergence
            # that is an artefact of this harness rather than a property of either world.
            if "read" in o and "read" in t:
                if _read_key(o["read"]) != _read_key(t["read"]):
                    kinds.append("OUTCOME")

            # The four harm COMPONENTS, which are the published numbers.
            if o.get("harm") and t.get("harm"):
                if _components(o["harm"]) != _components(t["harm"]):
                    kinds.append("HARM")
                elif o["harm"]["a_class"] != t["harm"]["a_class"]:
                    kinds.append("A_CLASS_on_a_refused_record")

            if o["rs"] != t["rs"]:
                pair = frozenset([o["rs"], t["rs"]])
                kinds.append("ROW_no_published_precedence" if pair in Q040_PAIRS
                             else "ROW_other")

            if not kinds:
                tally["agree"] += 1
                lines.append(f"    [{i}] AGREE  executed={o['executed']} rs={o['rs']}")
                continue
            for k in kinds:
                tally[k] += 1
            lines.append(f"    [{i}] {' + '.join(kinds)}")
            lines.append(f"         mine: executed={o['executed']} rs={o['rs']} "
                         f"harm={o.get('harm')}")
            lines.append(f"         c4  : executed={t['executed']} rs={t['rs']} "
                         f"harm={t.get('harm')}")
    return lines, tally


_RS46 = ("status", "captured", "refund_status", "amount_refunded")

_NON_TOOL_REPLIES = (surface.TOOL_NOT_ENABLED, surface.STUB_REPLY)


def _reply_text(rec):
    """The §8.6a string a non-tool call answered with, wherever the harness put it."""
    if rec.get("error") in _NON_TOOL_REPLIES:
        return rec["error"]
    data = rec.get("read") or rec.get("payload") or {}
    if isinstance(data, dict) and data.get("error") in _NON_TOOL_REPLIES:
        return data["error"]
    return None


def _is_non_tool_reply(rec):
    return _reply_text(rec) is not None


def _read_key(payload):
    """The identity plus RS-46's four redundant fields — what a gate can actually read.

    ⚠️ C4 returns a listing inside Razorpay's own `{"entity": "collection", "count": n,
    "items": [...]}` envelope; the reviewer's model returned a bare list.  C4's shape is the
    more faithful one, so the envelope is unwrapped HERE rather than treated as a
    divergence — this is a difference between two harnesses, not between two worlds.
    """
    if isinstance(payload, dict) and "items" in payload:
        payload = payload["items"]
    if isinstance(payload, list):
        return [_read_key(p) for p in payload]
    return {k: payload.get(k) for k in ("id", "amount", "currency", "notes", *_RS46)}


def _components(h):
    return (h["customer_overcharge_paise"], h["merchant_irrecoverable_outflow_paise"],
            h["merchant_float_moved_paise"], h["fees_incurred_paise"],
            h["rejected_by_razorpay"])


if __name__ == "__main__":
    say(f"whetstone_gate.__file__ = {whetstone_gate.__file__}")
    lines, tally = compare()
    header = [
        "C4 REVIEW 1 - PHASE 2a - the reviewer's 35 vectors against C4's own world",
        f"SESSION-TOKEN: 0852ea56",
        f"whetstone_gate.__file__ = {whetstone_gate.__file__}",
        "",
        "OUTCOME  = disagree on whether the call EXECUTED           -> a finding, always",
        "HARM     = same outcome, different harm record             -> a finding",
        "ROW_*    = same outcome and harm, different RS row id      -> observation where",
        "           Q-040 records the pair as having NO published precedence",
        "",
        f"vectors={tally['vectors']}  calls={tally['calls']}  agree={tally['agree']}",
        f"OUTCOME={tally['OUTCOME']}  HARM(components)={tally['HARM']}  "
        f"A_CLASS(on refused records)={tally['A_CLASS_on_a_refused_record']}",
        f"ROW(no published precedence)={tally['ROW_no_published_precedence']}  "
        f"ROW(other)={tally['ROW_other']}  "
        f"REPRESENTATION only={tally['REPRESENTATION_only']}",
        "",
    ]
    with open(HERE / "c4_reimpl_diff.txt", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(header + lines) + "\n")
    for line in header:
        say(line)
    for line in lines:
        if "AGREE" not in line:
            say(line)
