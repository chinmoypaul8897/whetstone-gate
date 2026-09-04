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

#: The warning glyph, named once so the lines carrying it stay inside 100 columns.
W = "⚠️"

#: ⚠️ **`H-1`. A CHAIN-FAILED ARM GETS NO BAR, FOR THE SAME REASON A NOT-RUN ONE
#: DOES NOT.** The race used to draw a full-length money bar from tampered content --
#: measured: ``arm 1  [############################]  88,888,888 paise`` from a ledger
#: whose chain had failed. §18 puts this frame in the video, **where the bar is the image
#: and the footer is small type**, so a footer note is not a cure. A bar is a claim about
#: money, and a file that fails its own digests supports no such claim.
CHAIN_FAILED_MARK = (
    "  !! CHAIN FAILED -- NO BAR DRAWN. This file does not match its own digests, "
    "so its contents are not a record of what happened"
)

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
    # ⚠️ `L-5` / `OF-266`: CLAMPED AT BOTH ENDS. ``min`` alone went NEGATIVE for a
    # negative value, so ``FILLED * filled`` was empty and ``EMPTY_CELL * (BAR_CELLS -
    # filled)`` OVERSHOT -- measured, ``bar(-5, 100)`` returned a 30-character track
    # against ``BAR_CELLS = 28``, breaking the frame's alignment. No stored component is
    # negative today; a track whose width depends on its value is a defect regardless.
    filled = max(0, min(BAR_CELLS, (value * BAR_CELLS) // scale))
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
    *,
    off_arm: "tuple[rp.EpisodeReplay, ...] | list[rp.EpisodeReplay]" = (),
    unreadable: "tuple[tuple[Path, str], ...] | list[tuple[Path, str]]" = (),
) -> str:
    """One turn of the race, as text. **Pure** — takes data, returns a string.

    ⚠️ ``off_arm`` and ``unreadable`` are keyword-only with empty defaults, so every
    existing caller is unchanged — but :func:`render` and :func:`list_episodes` now pass
    them, because hard rule 11 says *"every dropped episode is counted, categorised and
    printed as a number"* and a file on disk that reaches no track is dropped. `M-2` /
    `OF-258` is the episode whose arm is not one of the five; `M-4` / `OF-264` is the file
    that could not be read at all.
    """
    lines: list[str] = []
    lines.append("=" * 78)
    lines.append(f"  THE RACE  --  turn {turn_index + 1} of {budget}")
    lines.extend(caption(seed, budget))
    lines.append("=" * 78)

    chosen = {arm: episodes[0] for arm, episodes in grouped.items()}

    for component in rp.COMPONENTS:
        # ⚠️ `H-1`: A CHAIN-FAILED EPISODE SETS NO SCALE. If it did, fabricated
        # content would silently shrink every honest bar beside it to nothing -- the
        # tampered file would be deciding what the truthful arms look like.
        scale = max(
            (
                episode.component_total_through(component, turn_index)
                for episode in chosen.values()
                if episode.present and episode.chain_ok
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
            if not episode.chain_ok:
                # ⚠️ `H-1`. No bracket, no bar, no figure from a tampered file.
                lines.append(f"{label}{CHAIN_FAILED_MARK}")
                continue
            value = episode.component_total_through(component, turn_index)
            last = episode.last_turn_index
            # ⚠️ `B-2` / `O-7` IN THE ARTEFACT §18 PUTS ON SCREEN. "MEASURED ZERO"
            # used to be printed for ANY zero, including an EMPTY ledger -- so a bar
            # labelled MEASURED ZERO sat beside a bracket reading "[EMPTY LEDGER -- this
            # episode recorded no turn at all]", one line contradicting itself. It fires
            # on the real stored seeds 2102-2110, whose one arm-1 episode is EMPTY.
            if episode.completeness == rp.EMPTY:
                measured = "NO RECORD -- nothing was measured, and that is not a zero"
            elif value == 0 and last is not None and turn_index > last:
                measured = f"MEASURED ZERO THROUGH TURN {last + 1}"
            elif value == 0:
                measured = "MEASURED ZERO"
            else:
                measured = paise(value)
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
    # ⚠️ `H-4`. "NO DATA" USED TO MEAN "NO FILE". The footer computed
    # ``not_run = [arm for arm in ARMS if not chosen[arm].present]`` and printed it under
    # the heading ARMS WITH NO DATA -- but an EMPTY episode IS present, so on the real
    # stored seeds 2102-2110 it read "4 of 5 arms have never run" while **five of five had
    # no usable data**, crediting the one arm whose summary also said "nothing moved".
    # Three different facts, three lines: never ran / ran and recorded nothing / neither.
    not_run = [arm for arm in rp.ARMS if not chosen[arm].present]
    recorded_nothing = [
        arm for arm in rp.ARMS
        if chosen[arm].present and chosen[arm].completeness == rp.EMPTY
    ]
    unusable = len(not_run) + len(recorded_nothing)
    lines.append("")
    lines.append(
        f"  ARMS WITH NO DATA -- NEVER RAN (no episode file): "
        f"{', '.join(not_run) if not_run else 'none'}"
        f"   ({len(not_run)} of {len(rp.ARMS)} arms have never run)"
    )
    lines.append(
        f"  ARMS THAT RAN AND RECORDED NOTHING (EMPTY ledger): "
        f"{', '.join(recorded_nothing) if recorded_nothing else 'none'}"
        f"   ({len(recorded_nothing)} of {len(rp.ARMS)})"
    )
    lines.append(
        f"  {W} ARMS WITH NO USABLE DATA AT ALL: {unusable} of {len(rp.ARMS)}"
        f"   -- never ran, PLUS ran and recorded nothing. An EMPTY ledger is NOT data."
    )
    lines.append(
        "  A NOT-RUN ARM IS DRAWN WITH NO BAR AT ALL, NEVER AS A ZERO BAR:"
    )
    lines.append(
        "  a zero bar and a not-run bar look identical and mean opposite things."
    )

    # ⚠️ `H-3`. THE TWO DELIVERABLES MUST NOT DISAGREE ABOUT ONE EPISODE. This
    # renderer builds exactly ``budget`` frames, so an entry at a turn index at or beyond
    # the budget can appear in NONE of them -- while the audit log counts it. Measured: an
    # entry at turn index 25 booking 777,777 paise was in the audit summary and in none of
    # the twenty frames, with nothing anywhere saying a row had been dropped.
    # ⚠️ `chain_ok` IS PART OF THIS FILTER FOR `H-1`'s REASON, NOT `H-3`'s: the line
    # below prints PAISE FIGURES out of the entries, and a file that fails its own digests
    # supports no money claim anywhere in this frame. A chain-failed arm already carries
    # CHAIN_FAILED_MARK on every track and `!! CHAIN ... at ledger_seq N` in the footer,
    # so it is disclosed -- just never quantified.
    beyond = [
        (arm, entry)
        for arm in rp.ARMS
        if chosen[arm].chain_ok
        for entry in chosen[arm].entries_beyond_budget
    ]
    if beyond:
        lines.append("")
        lines.append(
            f"  {W} {len(beyond)} LEDGER ENTRY/ENTRIES LIE AT A TURN INDEX"
        )
        lines.append(
            f"  AT OR BEYOND THE TURN BUDGET (the budget is {budget})"
        )
        lines.append(
            "  AND ARE IN NO FRAME OF THIS RACE, WHICH DRAWS ONE FRAME PER BUDGETED TURN:"
        )
        for arm, entry in beyond:
            booked = ", ".join(
                f"{int(entry.get(component, 0) or 0):,} paise in {component}"
                for component in rp.COMPONENTS
                if int(entry.get(component, 0) or 0)
            )
            lines.append(
                f"       arm {arm:<3} turn index {int(entry['turn_index'])}   "
                f"{booked or 'no money booked'}"
            )
        lines.append(
            "  THE AUDIT LOG COUNTS THEM AND SO DOES THIS LINE. The race cannot DRAW them,"
        )
        lines.append(
            "  and says so rather than losing the money between two deliverables."
        )

    # ⚠️ `M-2` / `OF-258` and `M-4` / `OF-264`: hard rule 11 -- a file on disk that
    # reaches no track above is counted and categorised, never dropped in silence.
    if off_arm:
        lines.append("")
        lines.append(
            f"  {W} {len(off_arm)} STORED EPISODE(S) AT THIS SEED CARRY AN ARM THAT IS"
            " NOT ONE OF THE FIVE"
        )
        lines.append("  AND ARE IN NO TRACK ABOVE. Counted here rather than dropped:")
        for episode in off_arm:
            name = episode.path.name if episode.path else "(no file)"
            lines.append(f"       arm {episode.arm:<6} {name}")
    if unreadable:
        lines.append("")
        lines.append(
            f"  {W} {len(unreadable)} FILE(S) UNDER evals/episodes/ COULD NOT BE READ AS A"
            " STORED EPISODE"
        )
        lines.append("  AND ARE IN NO TRACK ABOVE. Counted here rather than dropped:")
        for path, reason in unreadable:
            lines.append(f"       {path.name}  -  {reason}")
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
    replays, unreadable = rp.load_all_reporting(root, budget)
    grouped = rp.by_arm(replays, seed, budget)
    stray = rp.off_arm(replays, seed)
    frames = [
        frame(grouped, turn, seed, budget, off_arm=stray, unreadable=unreadable)
        for turn in range(budget)
    ]
    for index, text in enumerate(frames):
        say(text)
        if animate and index < len(frames) - 1:
            time.sleep(ms_per_turn / 1000)
    return frames


def list_episodes(root: Path | None = None) -> None:
    """⚠️ **What is ACTUALLY on disk**, so the caption can never outrun the data."""
    budget = rp.turn_budget()
    paths = rp.discover(root)
    replays, unreadable = rp.load_all_reporting(root, budget)
    say(f"  {len(paths)} stored episode(s) under evals/episodes/  (turn budget {budget})")
    say("")
    for episode in replays:
        name = episode.path.name if episode.path else "(no file)"
        say(
            f"  {name:<34} arm {episode.arm:<3} seed {episode.seed}  "
            f"{episode.completeness:<10} {chain_note(episode)}"
        )
    if unreadable:
        # ⚠️ `M-4` / `OF-264`: counted and categorised, never a silence.
        say("")
        say(
            f"  {W} {len(unreadable)} FILE(S) COULD NOT BE READ AS A STORED EPISODE and are"
            " in nothing above:"
        )
        for path, reason in unreadable:
            say(f"       {path.name}  -  {reason}")
    if not paths:
        say(f"  {W} NONE. evals/episodes/ is absent or empty; there is nothing to replay.")


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
    # ⚠️ `M-4`: a stray unreadable file no longer takes this command down with it;
    # ``load_all`` collects the refusals and ``render`` prints them into every frame.
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
