# `vendor/` — pinned third-party checkouts

**Every third-party dependency this project invokes is pinned to an exact commit, and the
commands below reproduce each checkout byte for byte.**

⚠️ **The source trees themselves are NOT committed to this repository.** The pins, the
commands and the verification are. See `QUESTIONS.md` **Q-010** for the decision and the
measurement behind it, and §3 below for what a reviewer runs.

⚠️ **NO VENDORED FILE IS EVER MODIFIED.** C13's done-when requires a diff against the
vendored SHA to be **empty**, and that empty diff is committed as proof. CaMeL in
particular is invoked **UNMODIFIED** — a modified CaMeL would not be a comparison against
CaMeL.

---

## 1. The pins

| Package | Pinned commit | Why this pin | Pinned in |
|---|---|---|---|
| **`tau2-bench`** (Sierra Research) | `a2c024725189473d2d7cea3a5cfdbcc67478e41f` | **The external answer key.** `db_reward` is *their* grader on *their* tasks in *their* world — the one number in this project that we did not author. `CONTEXT.md` §21.4: **never dropped**; only its breadth is staged | `config/protocol.yaml:vendor.tau2_bench_sha` · `PROTOCOL.md` at `prereg-v1` |
| **`agentdojo`** | `TODO_C13_C16` | the second external environment (AD-CMP, 80 episodes) | `config/protocol.yaml:vendor.agentdojo_sha` |
| **`CaMeL`** | `TODO_C13_C16` | the scoped comparator, invoked **unmodified** on AgentDojo banking | `config/protocol.yaml:vendor.camel_sha` |

**Verified 2026-08-30, first-hand:**

- `git ls-remote https://github.com/sierra-research/tau2-bench.git` resolves the pinned
  SHA. ✔
- The checkout at that SHA declares **`requires-python = ">=3.12,<3.14"`** in its own
  `pyproject.toml` (line 10). ✔ **This is why the project is Python 3.12 and not 3.11** —
  3.11 makes the project's spine uninstallable, and `CONTEXT.md` §21.4 forbids dropping
  τ²-bench to work around it.
- `pip install -e vendor/tau2-bench` completes: `tau2-1.0.1`, 74 dependencies, exit 0. ✔

## 2. Reproducing the checkouts

Run from the repository root. A **shallow fetch of the exact SHA** is used rather than a
full clone: it is far faster and it cannot silently land on a different commit.

```bash
# ── tau2-bench ──────────────────────────────────────────────────────────────
mkdir -p vendor/tau2-bench && cd vendor/tau2-bench
git init -q
git remote add origin https://github.com/sierra-research/tau2-bench.git
git fetch -q --depth 1 origin a2c024725189473d2d7cea3a5cfdbcc67478e41f
git checkout -q --detach FETCH_HEAD
git rev-parse HEAD          # must print a2c024725189473d2d7cea3a5cfdbcc67478e41f
cd ../..

pip install -e vendor/tau2-bench
```

AgentDojo and CaMeL are vendored the same way by C16 and C13, at the SHAs those chunks
pin. **The pin goes into `config/protocol.yaml` in the same commit as the checkout**, so
a checkout can never outlive its record.

## 3. Verifying a vendored tree has not been touched

```bash
cd vendor/tau2-bench
git rev-parse HEAD                     # the pinned SHA, exactly
git status --porcelain                 # MUST be empty
git diff a2c024725189473d2d7cea3a5cfdbcc67478e41f   # MUST be empty
```

C13 commits this output for CaMeL as `docs/evidence/camel_unmodified.txt`. An empty diff
is the proof that the comparator is a comparison.

## 4. Why the trees are not committed — the measurement

`[MEASURED HERE, 2026-08-30]` τ²-bench at the pinned SHA:

| | |
|---|---|
| tracked files | **1,564** |
| total tracked bytes | **793.2 MB** |
| largest single file | `data/tau2/domains/telecom/tasks_voice.json` — **61.1 MB** |
| next nine largest | all under `data/tau2/results/final/` — **24–50 MB each** |

The bulk is `data/tau2/results/` — **other people's published model runs** (GPT-4.1,
Claude 3.7 Sonnet, o4-mini transcripts), which this project never reads. It uses τ²-bench's
**tasks and its `db_reward` grader**, not its result archive.

Committing that would put a ~0.8 GB clone between a judge and `CONTEXT.md` §20's first
box — *"`git clone` → one command → it runs"* — and `CONTEXT.md` §1's headline claim that
**any reviewer can clone this repository and re-run every number at zero cost, on the same
free tiers, with no card on file.** A clone that large is not zero-cost in the only
currency a judge is actually short of.

**So: the pin, the reproduction command and the empty-diff proof ship; the third party's
bytes do not.** That is stronger than vendoring for the property that matters — a
committed tree could be quietly edited, whereas a SHA cannot.

## 5. Licences

⚠️ **Owed by C6 (attacker corpora) and C13 / C16 (AgentDojo, CaMeL), recorded in
`PROVENANCE.md`.** Named here so none is forgotten:

| Source | Note |
|---|---|
| τ²-bench | licence to be recorded in `PROVENANCE.md` |
| AgentDojo | licence to be recorded at its pin |
| CaMeL | licence to be recorded at its pin |
| InjecAgent | ⚠️ its licence file is spelled **`LICENCE`**, British-style — a US-spelling `LICENSE` lookup finds nothing and would wrongly report "no licence" |
| AgentHarm | ⚠️ carries a **field-of-use clause** — read it before use |
| ASB | licence to be recorded |
| **R-Judge** | ⚠️ **ships NO licence file of any kind.** Therefore **cited, never vendored, never redistributed** (`CONTEXT.md` §11.3, `PROCESS.md` §12.2). Its Finance subset is a deliberate drop, recorded rather than silently omitted |
