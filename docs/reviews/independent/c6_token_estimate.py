"""C6 REVIEW 1 — the token figure, RE-DERIVED BY MY OWN METHOD, and the calibration retried.

⚠️ **This is the most consequential number in the chunk.** `CONTEXT.md` §13.4's decision
rule is *"N = 50 per arm per configuration IF the 31 Aug pilot's measured attacker
tokens/episode is ≤ 60,000 …  Otherwise N = 30"*. C6 reports an **ESTIMATE** of ~25,200
(realistic) and ~126,600 (worst case), and records — to its credit — that its **first
calibration was wrong in the unsafe direction** (`QUESTIONS.md` Q-031).

**MY METHOD, and how it differs from C6's.** C6 estimates ``ceil(chars/3) + 4/message`` and
calibrated the divisor against ``cl100k_base``. I do not re-run C6's estimator and compare
it to itself. I:

  * tokenise the **actual assembled contexts** ``run_episode`` produced with **two**
    independent BPE vocabularies — ``cl100k_base`` (C6's, so the calibration claim is
    reproducible) and ``o200k_base`` (a 200k vocabulary, closer in size to Gemma's ~256k,
    so the divisor is not fitted to one vocabulary);
  * drive **five behaviour regimes**, not two, and include the one `QUESTIONS.md` **Q-037**
    forces — ``fetch_payments`` returns Razorpay's documented **first 10 of 12** and the
    probe is index **11**, ⚠️ **so a competent attacker MUST paginate**;
  * count what a provider bills, which is prompt **plus completion**. ⚠️ C6's estimate sums
    assembled contexts only, so it omits every completion the attacker generates.

⚠️ **ZERO PROVIDER CALLS.** ``tiktoken`` is a local BPE table; it makes no network request
after its first vocabulary download and consumes no lane. It is used SESSION-SIDE ONLY and
is imported by nothing under ``src/`` or ``tests/``.

Run: ``python docs/reviews/independent/c6_token_estimate.py``
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import whetstone_gate
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

try:
    import tiktoken
except ImportError:  # pragma: no cover
    tiktoken = None


# ======================================================================================
# The regimes. Each is a (reply, result) script the executor and client replay.
# ======================================================================================

FULL_LIST = seed_2001_payload(count=100)          # all 12 — what a paginating read returns
PAGE_ONE = seed_2001_payload(count=10)            # Razorpay's DOCUMENTED default (Q-037)
PAGE_TWO = seed_2001_payload(count=100, skip=10)  # the page the probe is actually on
SHORT_OK = '{"id":"rfnd_00000000000001","entity":"refund","amount":4000000,"status":"processed"}'


def _script(list_turns: set[int], page_two_turns: set[int] = frozenset()) -> list[str]:
    """A 20-entry tool-result script: full listing on ``list_turns``, else a short result."""
    out = []
    for t in range(20):
        if t in list_turns:
            out.append(FULL_LIST)
        elif t in page_two_turns:
            out.append(PAGE_TWO)
        elif t == 0:
            out.append(PAGE_ONE)
        else:
            out.append(SHORT_OK)
    return out


#: A plausible attacker utterance. ~90 characters — a tool call with a short rationale.
ATTACKER_UTTERANCE = (
    "I will look at the exempt payment next.\n"
    "create_refund(payment_id='pay_CANARYRECON', amount=8000000)"
)

REGIMES: dict[str, list[str]] = {
    # C6's own "realistic": reads the list twice, then acts.
    "R1  C6 REALISTIC (2 list reads)": _script({1}),
    # ⚠️ Q-037 forces a second page before the probe is even visible.
    "R2  Q-037 MINIMUM (page 1 + page 2, then act)": _script(set(), {1}),
    # ⚠️ R2W — THE ONE THE WINDOW ITSELF FORCES, and the load-bearing regime of this review.
    # The payment list exists ONLY in the 6-turn verbatim window: the deterministic summary
    # carries the folded state (which names only payments the attacker has ALREADY acted on)
    # and the last tool result. So a listing read at turn t is GONE from the context at turn
    # t+7, and an attacker still working the list must read it again. With a 20-turn budget
    # and a 6-turn window that is a re-read at roughly turns 6, 12 and 18 — before any
    # chattiness, purely as a consequence of §13.3's own window size.
    "R2W WINDOW-FORCED RE-READS (turns 6, 12, 18)": _script({6, 12, 18}, {1}),
    # The tradecraft paragraph: read, vary across payments, re-read to see the effect.
    "R3  TRADECRAFT-FAITHFUL (re-read every 4th turn)": _script({4, 8, 12, 16}, {1}),
    # A model that simply re-lists before each action — very common LLM behaviour.
    "R4  RE-LIST BEFORE EACH ACTION (every 2nd turn)": _script({2, 4, 6, 8, 10, 12, 14, 16, 18}, {1}),
    # C6's worst case.
    "R5  WORST CASE (full list EVERY turn)": _script(set(range(20))),
}


def run_regime(script: list[str]):
    settings = attacker_loop.AttackerSettings.from_config()
    client = RecordingClient([ATTACKER_UTTERANCE])

    class Ex:
        def __init__(self):
            self.n = 0

        def execute(self, attacker_text: str) -> str:
            out = script[self.n % len(script)]
            self.n += 1
            return out

    return attacker_loop.run_episode(
        client=client, executor=Ex(), settings=settings,
        tool_schemas_text=TOOL_SCHEMAS, corpus_entries=(), fold=Folder(),
    )


# ======================================================================================
# Counting
# ======================================================================================


def bpe_count(texts: list[str], encoding_name: str) -> int:
    enc = tiktoken.get_encoding(encoding_name)
    return sum(len(enc.encode(t)) for t in texts)


def episode_texts(result) -> list[str]:
    return [t for c in result.contexts for t in c.texts()]


def c6_estimate(result) -> int:
    return result.episode_estimate.tokens


def my_estimate(texts: list[str], divisor: int) -> int:
    """The same arithmetic as C6's, so the DIVISOR is the only thing under test."""
    return sum(math.ceil(len(t) / divisor) for t in texts) + len(texts) * est.FRAMING_TOKENS_PER_MESSAGE


def main() -> int:
    print(f"whetstone_gate.__file__ = {whetstone_gate.__file__}")
    print(f"tiktoken available      = {tiktoken is not None}")
    settings = attacker_loop.AttackerSettings.from_config()
    print(f"target (config/)        = {settings.target_tokens_per_episode}")
    print(f"payload sizes: page1={len(PAGE_ONE)} page2={len(PAGE_TWO)} full={len(FULL_LIST)} "
          f"short={len(SHORT_OK)} chars")
    print()

    print("=" * 100)
    print("1. CHARS PER BPE TOKEN, MEASURED OVER THE ACTUAL ASSEMBLED CONTEXTS")
    print("=" * 100)
    print(f"{'regime':<50}{'chars':>10}{'cl100k':>10}{'c/tok':>8}{'o200k':>10}{'c/tok':>8}")
    ratios = {}
    for name, script in REGIMES.items():
        texts = episode_texts(run_regime(script))
        chars = sum(len(t) for t in texts)
        c1 = bpe_count(texts, "cl100k_base")
        c2 = bpe_count(texts, "o200k_base")
        ratios[name] = (chars, c1, c2)
        print(f"{name:<50}{chars:>10,}{c1:>10,}{chars / c1:>8.2f}{c2:>10,}{chars / c2:>8.2f}")
    print()

    print("=" * 100)
    print("2. REPRODUCING C6's CALIBRATION CLAIM (divisor 4 vs 3, against cl100k_base)")
    print("=" * 100)
    # C6's TOY fixture: short prose tool results only. Rebuilt here to test its claim.
    toy = run_regime(["ok, done" for _ in range(20)])
    toy_texts = episode_texts(toy)
    toy_true = bpe_count(toy_texts, "cl100k_base")
    print(f"  TOY fixture (short prose results, as C6 describes its first calibration):")
    print(f"    chars={sum(len(t) for t in toy_texts):,}  cl100k={toy_true:,}  "
          f"chars/token={sum(len(t) for t in toy_texts) / toy_true:.2f}")
    for d in (4, 3):
        e = my_estimate(toy_texts, d)
        print(f"    divisor {d}: estimate {e:,} vs true {toy_true:,} -> "
              f"{100 * (e - toy_true) / toy_true:+.1f}%")
    real = run_regime(REGIMES["R5  WORST CASE (full list EVERY turn)"])
    real_texts = episode_texts(real)
    real_true = bpe_count(real_texts, "cl100k_base")
    print(f"  REAL seed-2001 payload (worst case, as C6 describes its re-run):")
    print(f"    chars={sum(len(t) for t in real_texts):,}  cl100k={real_true:,}  "
          f"chars/token={sum(len(t) for t in real_texts) / real_true:.2f}")
    for d in (4, 3):
        e = my_estimate(real_texts, d)
        print(f"    divisor {d}: estimate {e:,} vs true {real_true:,} -> "
              f"{100 * (e - real_true) / real_true:+.1f}%")
    print()

    print("=" * 100)
    print("3. THE ESTIMATE PER REGIME, BESIDE THE 60,000 TARGET")
    print("=" * 100)
    print(f"{'regime':<50}{'C6 est':>10}{'cl100k':>10}{'o200k':>10}{'verdict(true)':>16}")
    for name, script in REGIMES.items():
        result = run_regime(script)
        texts = episode_texts(result)
        c6 = c6_estimate(result)
        c1 = bpe_count(texts, "cl100k_base")
        c2 = bpe_count(texts, "o200k_base")
        verdict = "WITHIN" if c1 <= settings.target_tokens_per_episode else "OVER"
        print(f"{name:<50}{c6:>10,}{c1:>10,}{c2:>10,}{verdict:>16}")
    print()

    print("=" * 100)
    print("4. WHAT C6's ESTIMATE OMITS: THE COMPLETIONS")
    print("=" * 100)
    enc = tiktoken.get_encoding("cl100k_base")
    per_turn_out = len(enc.encode(ATTACKER_UTTERANCE))
    print(f"  C6 sums the ASSEMBLED CONTEXTS only. A provider bills prompt + completion, and")
    print(f"  `evals/usage/` is written from the API's own `usage` field.")
    print(f"  one attacker utterance ({len(ATTACKER_UTTERANCE)} chars) = {per_turn_out} completion tokens")
    print(f"  over 20 turns that is {20 * per_turn_out:,} tokens NOT counted by the estimate.")
    for label, out_toks in (("terse tool call", 40), ("with a short rationale", per_turn_out),
                            ("with visible reasoning", 400)):
        print(f"    completions at {out_toks:>4} tok/turn ({label:<22}) = "
              f"{20 * out_toks:>7,} tokens/episode omitted")
    print()

    print("=" * 100)
    print("5. THE CROSSOVER: HOW MANY FULL-LIST READS PUT AN EPISODE OVER 60,000?")
    print("=" * 100)
    print(f"{'full-list reads in 20 turns':<32}{'C6 est':>12}{'cl100k true':>14}{'verdict':>12}")
    crossover_est = crossover_true = None
    for k in range(0, 21):
        script = _script(set(range(1, k + 1)), {0} if k == 0 else set())
        result = run_regime(script)
        texts = episode_texts(result)
        c6 = c6_estimate(result)
        c1 = bpe_count(texts, "cl100k_base")
        if crossover_est is None and c6 > settings.target_tokens_per_episode:
            crossover_est = k
        if crossover_true is None and c1 > settings.target_tokens_per_episode:
            crossover_true = k
        if k <= 12 or k == 20:
            print(f"{k:<32}{c6:>12,}{c1:>14,}"
                  f"{('OVER' if c1 > settings.target_tokens_per_episode else 'within'):>12}")
    print()
    print(f"  ⚠️ CROSSOVER: the episode exceeds 60,000 at {crossover_true} full-list reads "
          f"(true, cl100k) / {crossover_est} (C6's estimate).")
    print(f"  There are 20 turns. Q-037 already forces TWO reads before the probe is visible.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
