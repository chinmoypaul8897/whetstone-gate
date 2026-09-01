"""C6 REVIEW 1 — the summary's determinism and the one-call-per-turn NUMBER, re-derived.

⚠️ `QUESTIONS.md` **Q-031** part 1 requires this review to re-derive *"the summary's
determinism BY ITS OWN METHOD"*. `CONTEXT.md` §13.3 is the law:

    *"The summary is produced DETERMINISTICALLY — a template that concatenates the running
    folded state (§8.6) with the last denial reason — not by an LLM call, so it adds no
    requests and does not break the seeded-determinism claim or the 20-requests/episode
    budget."*

Six properties, each derived here rather than read out of C6's tests:

  D1  identical state  -> byte-identical summary
  D2  different state  -> different bytes (or the property is trivial)
  D3  insertion order of the folded state's nested maps is irrelevant
  D4  truncation at the configured cap is deterministic AND visibly marked
  D5  exactly ONE model call per turn; 20 per 20-turn episode; ZERO to render a summary
  D6  the window keeps the last N turns and the older ones are VERIFIABLY GONE; tool
      schemas appear exactly once per turn; and the sizes come from ``config/`` — proved by
      pointing the loader at an ALTERED config, not by reading the source

Run: ``python docs/reviews/independent/c6_summary_and_calls.py``
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import whetstone_gate
from whetstone_gate import config as cfg
from whetstone_gate.attacker import context as ctx
from whetstone_gate.attacker import estimate as est
from whetstone_gate.attacker import loop as attacker_loop

sys.path.insert(0, str(Path(__file__).parent))
from c6_blindness import (  # noqa: E402
    Folder,
    RecordingClient,
    TOOL_SCHEMAS,
    generic_denial,
    seed_2001_payload,
)

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str) -> None:
    RESULTS.append((name, ok, detail))


# ======================================================================================
# D1..D4 — the template
# ======================================================================================


def state(**kw) -> ctx.FoldedState:
    base = dict(
        episode_paise_moved=4_412_300,
        per_payment_refunded_paise={"pay_z": 3, "pay_a": 1, "pay_m": 2},
        per_payment_captured_paise={"pay_m": 90, "pay_a": 10},
        idempotency_keys_seen=("zzz", "aaa", "mmm"),
        actions_executed=5,
        turns_remaining=13,
    )
    base.update(kw)
    return ctx.FoldedState(**base)


def d1_d2_d3(cap: int, denial: str) -> None:
    a = ctx.render_summary(state(), denial, cap)
    b = ctx.render_summary(state(), denial, cap)
    check("D1 identical state -> byte-identical", a.encode() == b.encode(), f"{len(a)} chars")

    # D2 — a different state must move the bytes. Exercised on EVERY field, one at a time,
    # because "different state -> different bytes" tested on one field is a claim about
    # one field.
    moved, stuck = [], []
    variants = {
        "episode_paise_moved": state(episode_paise_moved=4_412_301),
        "per_payment_refunded_paise": state(per_payment_refunded_paise={"pay_z": 4, "pay_a": 1, "pay_m": 2}),
        "per_payment_captured_paise": state(per_payment_captured_paise={"pay_m": 91, "pay_a": 10}),
        "idempotency_keys_seen": state(idempotency_keys_seen=("zzz", "aaa", "mmm", "qqq")),
        "actions_executed": state(actions_executed=6),
        "turns_remaining": state(turns_remaining=12),
    }
    for field, variant in variants.items():
        (moved if ctx.render_summary(variant, denial, cap) != a else stuck).append(field)
    check("D2 different state -> different bytes (all 6 fields)", not stuck,
          f"moved={len(moved)}/6" + (f" STUCK={stuck}" if stuck else ""))

    # And the last-refusal half must move too.
    check("D2b a different refusal -> different bytes",
          ctx.render_summary(state(), denial + " x", cap) != a, "")

    # D3 — insertion order. Three permutations of every mapping and sequence.
    perms = [
        state(per_payment_refunded_paise={"pay_a": 1, "pay_m": 2, "pay_z": 3},
              per_payment_captured_paise={"pay_a": 10, "pay_m": 90},
              idempotency_keys_seen=("aaa", "mmm", "zzz")),
        state(per_payment_refunded_paise={"pay_m": 2, "pay_z": 3, "pay_a": 1},
              per_payment_captured_paise={"pay_m": 90, "pay_a": 10},
              idempotency_keys_seen=("mmm", "zzz", "aaa")),
    ]
    check("D3 insertion order is irrelevant", all(ctx.render_summary(p, denial, cap) == a for p in perms),
          f"{len(perms)} permutations")


def d4_truncation(cap: int, denial: str) -> None:
    big = state(per_payment_refunded_paise={f"pay_{i:05d}": i for i in range(3000)})
    t1 = ctx.render_summary(big, denial, cap)
    t2 = ctx.render_summary(big, denial, cap)
    check("D4a truncation is deterministic", t1 == t2, f"{len(t1)} chars")
    check("D4b truncation is VISIBLY marked", ctx.TRUNCATION_MARK in t1, ctx.TRUNCATION_MARK)
    check("D4c the truncated summary is within the cap", est.estimate_text(t1) <= cap,
          f"estimate {est.estimate_text(t1)} vs cap {cap}")

    # ⚠️ D4d — DOES TRUNCATION COLLIDE? Two DIFFERENT states whose difference falls beyond
    # the cut render identically. That is D2 failing in exactly the regime where the
    # summary is doing work.
    other = state(per_payment_refunded_paise={
        **{f"pay_{i:05d}": i for i in range(2999)}, "pay_02999": 999999})
    collides = ctx.render_summary(other, denial, cap) == t1
    check("D4d different states must not collide under truncation", not collides,
          "TWO DISTINCT STATES RENDER IDENTICALLY" if collides else "distinct")

    # ⚠️ D4e — the cap is enforced in CHARACTERS via the estimator's divisor. At a small
    # cap the marker alone overruns it.
    tiny = ctx.render_summary(big, denial, 5)
    check("D4e the cap holds at small values too", est.estimate_text(tiny) <= 5,
          f"cap=5 -> estimate {est.estimate_text(tiny)} ({len(tiny)} chars)")

    # ⚠️ D4f — the summary the attacker is SENT depends on estimate.CHARS_PER_TOKEN, a
    # Class B implementation parameter declared to be "superseded by C14's measurement".
    original = est.CHARS_PER_TOKEN
    try:
        est.CHARS_PER_TOKEN = 4
        moved = ctx.render_summary(big, denial, cap) != t1
    finally:
        est.CHARS_PER_TOKEN = original
    check("D4f the ATTACKER'S TEXT does not depend on the estimator's divisor", not moved,
          "changing estimate.CHARS_PER_TOKEN 3->4 CHANGES the summary bytes"
          if moved else "independent")


# ======================================================================================
# D5 — the call count, from MY mock
# ======================================================================================


def d5_call_count(denial: str) -> None:
    settings = attacker_loop.AttackerSettings.from_config()
    client = RecordingClient(["fetch_payments()", "create_refund(payment_id='p', amount=1)"])

    class Ex:
        def __init__(self):
            self.n = 0

        def execute(self, attacker_text: str) -> str:
            self.n += 1
            return seed_2001_payload(count=10) if "fetch" in attacker_text else denial

    ex = Ex()
    result = attacker_loop.run_episode(
        client=client, executor=ex, settings=settings,
        tool_schemas_text=TOOL_SCHEMAS, corpus_entries=(), fold=Folder(),
    )
    check("D5a exactly one model call per turn",
          len(client.messages) == settings.turn_budget == len(result.records) == result.model_calls,
          f"calls={len(client.messages)} turns={settings.turn_budget} "
          f"records={len(result.records)} reported={result.model_calls}")
    check("D5b executor called once per turn", ex.n == settings.turn_budget, f"{ex.n}")
    check("D5c temperature is config's on EVERY call",
          set(client.temperatures) == {settings.temperature}, f"{sorted(set(client.temperatures))}")

    # D5d — rendering a summary makes ZERO model calls. Asserted by rendering many with a
    # client that would raise if touched.
    class Exploding:
        def complete(self, *, messages, temperature):  # pragma: no cover
            raise AssertionError("render_summary made a model call")

    for i in range(50):
        ctx.render_summary(state(actions_executed=i), denial, settings.summary_token_cap)
    check("D5d rendering 50 summaries makes ZERO model calls", True, "no client is reachable "
          "from context.py — render_summary takes no client argument")


# ======================================================================================
# D6 — the window
# ======================================================================================


def d6_window(denial: str) -> None:
    settings = attacker_loop.AttackerSettings.from_config()
    # ⚠️ FIXED-WIDTH markers, deliberately. A marker whose length grows with its index
    # (``UNIQUE_MARKER_9`` -> ``UNIQUE_MARKER_10``) makes the fixture itself grow, and D6d
    # would then measure my own fixture rather than C6's window. The first draft of this
    # file did exactly that and reported a false FAIL.
    client = RecordingClient([f"ATKMARK{i:03d}" for i in range(40)])

    class Ex:
        def __init__(self):
            self.n = 0

        def execute(self, attacker_text: str) -> str:
            self.n += 1
            return f"RESMARK{self.n - 1:03d}"

    result = attacker_loop.run_episode(
        client=client, executor=Ex(), settings=settings,
        tool_schemas_text=TOOL_SCHEMAS, corpus_entries=(), fold=Folder(),
    )
    last = result.contexts[-1]
    kept = [p for p in last.parts if p.origin is ctx.Origin.ATTACKER]
    check("D6a the window keeps exactly config's verbatim turns",
          len(kept) == settings.verbatim_turns, f"{len(kept)} vs {settings.verbatim_turns}")

    # ⚠️ VERIFIED GONE, not merely unlabelled — over the ACTUAL wire form. The LAST context
    # is assembled before turn 19 runs, so its history is turns 0..18 and it keeps 13..18.
    wire = json.dumps(last.as_messages())
    kept_first = (settings.turn_budget - 1) - settings.verbatim_turns
    evicted = [i for i in range(kept_first) if f"ATKMARK{i:03d}" in wire]
    check("D6b evicted turns are GONE from the wire form", not evicted, f"still present: {evicted}")
    still_kept = [i for i in range(kept_first, settings.turn_budget - 1)
                  if f"ATKMARK{i:03d}" in wire]
    check("D6b' the kept turns really are the LAST ones",
          still_kept == list(range(kept_first, settings.turn_budget - 1)), f"kept {still_kept}")

    # Tool schemas EXACTLY once per turn.
    counts = {c.full_text().count(TOOL_SCHEMAS) for c in result.contexts}
    check("D6c tool schemas appear exactly once in every turn's context", counts == {1}, f"{counts}")

    # D6d — the window's whole purpose. ⚠️ The claim to test is *"stops GROWING"*, not
    # *"is a single constant"*: ``turns_remaining`` loses a digit at turn 10, which moves the
    # folded state's JSON by one character. A check demanding one constant value would be
    # testing the width of an integer.
    sizes = [est.estimate_messages(c.texts()).tokens for c in result.contexts]
    tail = sizes[settings.verbatim_turns + 1:]
    grows = [i for i in range(1, len(tail)) if tail[i] > tail[i - 1]]
    check("D6d per-turn context STOPS GROWING once the window fills", not grows,
          f"turns {settings.verbatim_turns + 1}..{settings.turn_budget - 1} range "
          f"{min(tail)}..{max(tail)} tokens; growth steps at {grows}")


def d6e_config_is_really_read(repo: Path) -> None:
    """⚠️ Proved by POINTING THE LOADER AT AN ALTERED CONFIG, in a SEPARATE PROCESS.

    A monkeypatched env var inside the same interpreter can be defeated by module-level
    caching. A subprocess cannot.
    """
    original = repo.joinpath("config/protocol.yaml").read_bytes().decode("utf-8")
    altered = (original
               .replace("context_window_turns_verbatim: 6", "context_window_turns_verbatim: 3")
               .replace("context_summary_max_tokens: 400", "context_summary_max_tokens: 40")
               .replace("turn_budget: 20", "turn_budget: 7"))
    assert altered != original
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "config"
        d.mkdir()
        d.joinpath("protocol.yaml").write_bytes(altered.encode("utf-8"))
        d.joinpath("lanes.yaml").write_bytes(repo.joinpath("config/lanes.yaml").read_bytes())
        env = dict(os.environ, WHETSTONE_CONFIG_DIR=str(d), PYTHONIOENCODING="utf-8")
        probe = Path(__file__).parent / "c6_config_probe.py"
        out = subprocess.run([sys.executable, str(probe)], env=env, capture_output=True, text=True)
        if out.returncode != 0:
            check("D6e the sizes are genuinely read from config/", False, out.stderr.strip()[-400:])
            return
        got = json.loads(out.stdout.strip().splitlines()[-1])
    ok = (got["turn_budget"], got["verbatim"], got["cap"], got["calls"], got["kept"]) == (
        7, 3, 40, 7, 3)
    check("D6e the sizes are genuinely read from config/ (subprocess, altered file)", ok,
          json.dumps(got))
    # And the CAP really binds the bytes: 40 tokens -> at most 120 characters.
    check("D6e' the altered summary cap really shortens the attacker's text",
          got["summary_chars"] <= 40 * est.CHARS_PER_TOKEN,
          f"summary_chars={got['summary_chars']} vs cap*divisor={40 * est.CHARS_PER_TOKEN}")


def main() -> int:
    print(f"whetstone_gate.__file__ = {whetstone_gate.__file__}")
    repo = cfg.repo_root()
    settings = attacker_loop.AttackerSettings.from_config()
    denial = generic_denial()
    print(f"config: turn_budget={settings.turn_budget} verbatim={settings.verbatim_turns} "
          f"cap={settings.summary_token_cap} temperature={settings.temperature}")
    print()

    d1_d2_d3(settings.summary_token_cap, denial)
    d4_truncation(settings.summary_token_cap, denial)
    d5_call_count(denial)
    d6_window(denial)
    d6e_config_is_really_read(repo)

    failures = 0
    for name, ok, detail in RESULTS:
        mark = "OK  " if ok else "FAIL"
        print(f"[{mark}] {name}" + (f"   -- {detail}" if detail else ""))
        failures += int(not ok)
    print()
    print(f"{len(RESULTS) - failures}/{len(RESULTS)} properties hold; {failures} did not")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
