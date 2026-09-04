"""**DELIVERABLE A — THE §18 RACE BEAT.** Five arms, one seed, one turn per frame.

`CONTEXT.md` §18, the 0:35–1:25 row, verbatim:

    **THE RACE.** Five arms, one seed, same attacker, side by side, five money bars
    filling at different speeds, 1400 ms/turn. **On-screen caption states the seed and
    the pre-registered N** — *"seed 2005 · N per `PROTOCOL.md`"* — so it is not
    cherry-picking, and **it says on screen that this is a replay of a stored
    hash-chained ledger, not a live run.**

Run it::

    python docs/render/race.py                    # the default seed, animated
    python docs/render/race.py --seed 2101
    python docs/render/race.py --no-animate       # every frame at once, for capture
    python docs/render/race.py --list             # what is actually on disk

---

## ⚠️ FIVE BARS PER COMPONENT, AND THE FOUR COMPONENTS ARE NEVER ADDED

§18 says *"five money bars"*. `CONTEXT.md` §12.2 says the four harm components are
**never summed** — over-capture takes money **from the customer**, over-refund is an
irrecoverable **merchant** outflow, a sweep moves the merchant's **own** float, and fees
are a fifth kind of thing again. *"The old metric added together three different losses
to three different parties."*

**A stacked bar would put that forbidden sum back on screen as a length**, which is the
same claim in a costume, in the one artefact a judge watches. So this renderer draws
**four tracks, five bars each** — five money bars racing, four times over, nothing added
to anything. ⚠️ **This reading is a build-session choice between two spec sentences that
pull apart, and it is raised in `docs/sessions/c17-build-1.txt` under QUESTIONS OWED
rather than settled here.**

---

## ⚠️ A NOT-RUN ARM IS NOT A ZERO BAR

Four of the five arms have never run. An empty bar and an absent bar look identical on
screen and mean opposite things, and *"0% escaped"* is precisely the claim this project
exists to distrust. A not-run arm therefore has **no bar track drawn at all** — see
:data:`NOT_RUN_MARK` — and the frame footer counts the arms it is missing.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import replay as rp  # noqa: E402  (path-relative sibling; see the note above)
from whetstone_gate._console import say  # noqa: E402

# --------------------------------------------------------------------------------------
# Presentation constants. ⚠️ NONE OF THESE ENTERS A REPORTED NUMBER.
# --------------------------------------------------------------------------------------

#: §18's frame duration, in milliseconds. ⚠️ **A PRESENTATION VALUE, NOT A MEASUREMENT.**
#: It is named here rather than read from ``config/`` because ``config/`` is a frozen
#: pre-registration artefact (`CLAUDE.md` §4) and this build session may not add a key to
#: it. It is overridable with ``--ms-per-turn`` and it enters no figure this project
#: publishes. Raised under QUESTIONS OWED in `docs/sessions/c17-build-1.txt`.
MS_PER_TURN = 1400

#: How wide a bar track is drawn, in characters. Pure typography.
BAR_CELLS = 28

FILLED = "#"
EMPTY_CELL = "."
NOT_RUN_MARK = "  -- NOT RUN --  no episode file for this arm at this seed"

#: ⚠️ **N DOES NOT EXIST.** The pilot completed 0 of 20 episodes, ``select_n`` returned
#: ``USABLE TO SELECT N: False``, and ``config/protocol.yaml``'s
#: ``n_decision.selected_branch`` is still ``TODO_C14_PILOT``. `RESULTS.md` §3.2,
#: `INCIDENTS.md` `INC-142`. README.md:28's convention is that a placeholder is spelled
#: ``<<PENDING-RUN: name>>`` and **a placeholder is never a result**. Nothing in this
#: module invents, guesses or defaults an N.
N_PLACEHOLDER = "<<PENDING-RUN: N>>"

#: The one sentence §18 requires on screen.
REPLAY_BANNER = (
    "REPLAY OF A STORED, HASH-CHAINED LEDGER -- NOT A LIVE RUN. "
    "No model is called and no network is touched by this renderer."
)

#: Short, plain-English names for §12.2's four harm components, in `COMPONENTS` order.
COMPONENT_LABELS = {
    "customer_overcharge_paise": "A1 over-capture      money taken FROM A CUSTOMER",
    "merchant_irrecoverable_outflow_paise": "A2/A3 over-refund    MERCHANT outflow, unrecoverable",
    "merchant_float_moved_paise": "A4 balance sweep     merchant's OWN float moved",
    "fees_incurred_paise": "fees incurred        the charge the action caused",
}


def paise(value: int) -> str:
    """Integer paise, grouped. ⚠️ Never a float — `PROCESS.md` §5.1 on the money path."""
    return f"{value:,} paise"


def bar(value: int, scale: int) -> str:
    """One money bar. ``scale`` is the largest value in this track across the arms."""
    if scale <= 0:
        return EMPTY_CELL * BAR_CELLS
    filled = min(BAR_CELLS, (value * BAR_CELLS) // scale)
    return FILLED * filled + EMPTY_CELL * (BAR_CELLS - filled)


def chain_note(episode: rp.EpisodeReplay) -> str:
    """What to print about this episode's chain. ⚠️ **Vacuous is not VALID.**"""
    if not episode.present:
        return "not run"
    if not episode.chain_ok:
        return f"!! CHAIN {episode.chain_verdict} at ledger_seq {episode.chain_first_bad_seq}"
    if episode.chain_is_vacuous:
        return "chain VALID but VACUOUS (0 entries -- a chain over nothing proves nothing)"
    return f"chain VALID, {episode.turns_seen} entries recomputed"


def past_end(episode: rp.EpisodeReplay, turn_index: int) -> str:
    """⚠️ **Why this bar has stopped moving — the difference the video must not blur.**

    A bar that stops growing at turn 8 of 20 looks exactly like an attacker that tried
    and achieved nothing. The stored gemma episode stopped *because the episode stopped*,
    and every frame after its last entry says so rather than letting a flat line imply a
    result. This is the *"handles a truncated ledger without pretending it is complete"*
    half of C17's done-when, applied per frame instead of once in a footer.
    """
    last = episode.last_turn_index
    if last is None:
        return "   [EMPTY LEDGER -- this episode recorded no turn at all]"
    if turn_index > last:
        return f"   [NO DATA -- ledger ended at turn {last + 1}; not a measured zero]"
    return ""


def completeness_note(episode: rp.EpisodeReplay) -> str:
    if episode.completeness == rp.ABSENT:
        return "NOT RUN"
    if episode.completeness == rp.EMPTY:
        return "EMPTY -- the episode produced no ledger entry at all"
    if episode.completeness == rp.TRUNCATED:
        last = episode.last_turn_index
        return (
            f"TRUNCATED -- stopped after turn {last + 1} of a {episode.budget}-turn budget; "
            f"the remaining {episode.budget - (last + 1)} turns were never attempted"
        )
    return "COMPLETE"


def caption(seed: int, budget: int) -> list[str]:
    """⚠️ **The caption §18 requires: the seed and the pre-registered N.**"""
    return [
        f"  seed {seed}  *  N = {N_PLACEHOLDER}  *  turn budget {budget}",
        f"  {REPLAY_BANNER}",
        "  N is a PLACEHOLDER, not a result: the pilot completed 0 of 20 episodes and",
        "  config/protocol.yaml n_decision.selected_branch is still TODO_C14_PILOT.",
    ]


def frame(
    grouped: dict[str, list[rp.EpisodeReplay]],
    turn_index: int,
    seed: int,
    budget: int,
) -> str:
    """One turn of the race, as text. **Pure** — takes data, returns a string."""
    lines: list[str] = []
    lines.append("=" * 78)
    lines.append(f"  THE RACE  --  turn {turn_index + 1} of {budget}")
    lines.extend(caption(seed, budget))
    lines.append("=" * 78)

    chosen = {arm: episodes[0] for arm, episodes in grouped.items()}

    for component in rp.COMPONENTS:
        scale = max(
            (
                episode.component_total_through(component, turn_index)
                for episode in chosen.values()
                if episode.present
            ),
            default=0,
        )
        lines.append("")
        lines.append(f"  {COMPONENT_LABELS[component]}")
        for arm in rp.ARMS:
            episode = chosen[arm]
            label = f"    arm {arm:<3}"
            if not episode.present:
                lines.append(f"{label}{NOT_RUN_MARK}")
                continue
            value = episode.component_total_through(component, turn_index)
            measured = "MEASURED ZERO" if value == 0 else paise(value)
            lines.append(f"{label}[{bar(value, scale)}]  {measured}{past_end(episode, turn_index)}")

    lines.append("")
    lines.append("-" * 78)
    for arm in rp.ARMS:
        episode = chosen[arm]
        model = episode.model or "-"
        lines.append(
            f"  arm {arm:<3} {model:<12} {completeness_note(episode)}"
        )
        lines.append(f"           {chain_note(episode)}")
    for arm in rp.ARMS:
        others = grouped[arm][1:]
        if others:
            names = ", ".join(sorted(e.model or "?" for e in others))
            lines.append(
                f"  ⚠️ arm {arm}: {len(grouped[arm])} stored episodes at this seed. "
                f"Shown: {chosen[arm].model}. ALSO ON DISK, NOT SHOWN: {names}."
            )
    not_run = [arm for arm in rp.ARMS if not chosen[arm].present]
    lines.append("")
    lines.append(
        f"  ARMS WITH NO DATA: {', '.join(not_run) if not_run else 'none'}"
        f"   ({len(not_run)} of {len(rp.ARMS)} arms have never run)"
    )
    lines.append(
        "  A NOT-RUN ARM IS DRAWN WITH NO BAR AT ALL, NEVER AS A ZERO BAR:"
    )
    lines.append(
        "  a zero bar and a not-run bar look identical and mean opposite things."
    )
    return "\n".join(lines)


def render(
    seed: int,
    *,
    animate: bool = True,
    ms_per_turn: int = MS_PER_TURN,
    root: Path | None = None,
) -> list[str]:
    """Every frame of the race for one seed. Returns them; prints them as it goes."""
    budget = rp.turn_budget()
    replays = rp.load_all(root, budget)
    grouped = rp.by_arm(replays, seed, budget)
    frames = [frame(grouped, turn, seed, budget) for turn in range(budget)]
    for index, text in enumerate(frames):
        say(text)
        if animate and index < len(frames) - 1:
            time.sleep(ms_per_turn / 1000)
    return frames


def list_episodes(root: Path | None = None) -> None:
    """⚠️ **What is ACTUALLY on disk**, so the caption can never outrun the data."""
    budget = rp.turn_budget()
    paths = rp.discover(root)
    say(f"  {len(paths)} stored episode(s) under evals/episodes/  (turn budget {budget})")
    say("")
    for path in paths:
        episode = rp.load_episode(path, budget)
        say(
            f"  {path.name:<34} arm {episode.arm:<3} seed {episode.seed}  "
            f"{episode.completeness:<10} {chain_note(episode)}"
        )
    if not paths:
        say("  ⚠️ NONE. evals/episodes/ is absent or empty; there is nothing to replay.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The §18 RACE beat: five arms, one seed.")
    parser.add_argument("--seed", type=int, default=None, help="which stored seed to race")
    parser.add_argument("--no-animate", action="store_true", help="print every frame at once")
    parser.add_argument("--ms-per-turn", type=int, default=MS_PER_TURN)
    parser.add_argument("--list", action="store_true", help="list the stored episodes and exit")
    args = parser.parse_args(argv)

    if args.list:
        list_episodes()
        return 0

    available = rp.seeds_available(rp.load_all())
    if not available:
        say("  ⚠️ NO STORED EPISODE EXISTS. There is nothing to replay, and this renderer")
        say("     will not invent one. Run the pilot or the calibration first.")
        return 1
    seed = args.seed if args.seed is not None else available[0]
    if seed not in available:
        say(f"  ⚠️ seed {seed} has no stored episode. Available: {available}")
        return 1

    render(seed, animate=not args.no_animate, ms_per_turn=args.ms_per_turn)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
