# `docs/render/` — the replay renderer (C17)

**Two deliverables, one build.** `PROCESS.md` §12's C17 card names both, and only one of them is
the obvious one.

| | what it is | run it |
|---|---|---|
| **A** | **the §18 RACE beat** — five arms, one seed, one frame per turn | `python docs/render/race.py` |
| **B** | **the audit log a non-author can read and follow** | `python docs/render/audit.py` |

**B is not a by-product of A.** The race answers *how fast*; the audit log answers *what happened, to
whose money, and how do I know this file was not edited*. A judge who cannot follow one episode end
to end without asking a question is the failure deliverable B exists to prevent.

```sh
python docs/render/race.py --list                      # what is actually on disk
python docs/render/race.py --seed 2101                 # the race, animated at 1400 ms/turn
python docs/render/race.py --seed 2101 --no-animate    # every frame at once, for capture
python docs/render/audit.py --episode pilot__1__2101__gemma-26b.json
python docs/render/audit.py --all
```

---

## What it reads, and what it will not do

- ⚠️ **It reads `evals/episodes/` and nothing else.** It reaches `config/` only through the one
  loader (hard rule 9) for the turn budget and the genesis root.
- ⚠️ **It makes no network call and runs no model.** `tests/test_c17_render.py` asserts this
  **four** ways — a transitive AST import walk, a raw source-text scan, a `sys.modules` check in a
  subprocess that actually renders, and a socket guard that proves the *capability* is absent — and
  each is fired at an input that makes it red. `INCIDENTS.md` **INC-51** is why one way is not
  enough: an AST walk cannot see `importlib.import_module("openai")` by construction.
- ⚠️ **It writes nothing.** `evals/` is append-only, and the renderer is a reader.

## What it says on screen, on purpose

- **That it is a replay of a stored, hash-chained ledger — not a live run.**
- **It verifies the chain rather than trusting it.** Every digest is recomputed from each entry's
  own contents and the walk continues from the *recomputed* value. A verifier that compared stored
  fields would pass a ledger whose contents were altered under consistent-looking links — golden 5's
  cases C and D — and the test suite fires exactly that mutation at this renderer.
- **The caption states the seed and N.** ⚠️ **N does not exist yet.** The pilot completed 0 of 20
  episodes, `select_n` returned `USABLE TO SELECT N: False`, and `config/protocol.yaml`'s
  `n_decision.selected_branch` is still `TODO_C14_PILOT` (`RESULTS.md` §3.2, `INC-142`). It is
  rendered as `<<PENDING-RUN: N>>`, README.md:28's convention. **Nothing here invents, guesses or
  defaults an N.**

## ⚠️ The three states the stored data actually has, and why each is labelled

Today's episodes are the pilot's, and they are not tidy. The renderer says what they are:

| state | what it looks like today | how it renders |
|---|---|---|
| **TRUNCATED** | the gemma episode stops after turn 8 of a 20-turn budget | named as truncated, with the unused turns counted; every frame past turn 8 says `NO DATA — ledger ended at turn 8`, never a flat bar |
| **EMPTY** | ten qwen episodes are literally `"ledger": []` | `VALID` **but VACUOUS** — a chain over nothing proves nothing, and it is never printed bare |
| **ABSENT** | arms 2, 2S, 3 and 4 have never run | `-- NOT RUN --`, with **no bar track drawn at all** |

⚠️ **A ZERO BAR AND A NOT-RUN BAR LOOK IDENTICAL ON SCREEN AND MEAN OPPOSITE THINGS.** Arm 1 ran and
moved no money — that is a **measured zero**. Arms 2, 2S, 3 and 4 produced no data at all. *"0%
escaped"* is precisely the claim this project exists to distrust, so the two are drawn differently
and a test asserts the difference survives into the rendered text.

## ⚠️ The four harm components are never summed

`CONTEXT.md` §12.2: the old metric *"added together three different losses to three different
parties"*. An over-capture takes money from a **customer**; an over-refund is an irrecoverable
**merchant** outflow; a sweep moves the merchant's **own** float, where the real loss is the fee, not
the principal — summing overstates it by roughly 330–670×.

§18 asks for *"five money bars"*. A **stacked** bar would put that forbidden sum back on screen as a
*length*, in the one artefact a judge watches. So the race draws **four component tracks with five
bars each** — five money bars racing, four times over, nothing added to anything. ⚠️ This reading
reconciles two spec sentences that pull apart, and it is raised under QUESTIONS OWED in
`docs/sessions/c17-build-1.txt` rather than settled here.

## Presentation values

`MS_PER_TURN = 1400` (§18's frame duration) and `BAR_CELLS` are **presentation** constants declared
in `race.py`. They enter no reported figure. ⚠️ §18's 1400 ms has **no home in `config/`**, and
`config/` is a frozen pre-registration artefact this session may not edit — so it is named, is
overridable with `--ms-per-turn`, and is raised under QUESTIONS OWED rather than written in silently.
