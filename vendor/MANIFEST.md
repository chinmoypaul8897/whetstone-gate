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
| AgentDojo | ✅ **LICENCE RECORDED by C6, 2026-08-31** — **MIT** © 2024 Edoardo Debenedetti, Jie Zhang, Mislav Balunović, Luca Beurer-Kellner, Marc Fischer, and Florian Tramèr (⚠️ §11.3 named no holder; MIT requires the notice). `PROVENANCE.md` §3.3. ⚠️ **The PIN is still C13 / C16's** — C6 pinned only the banking **injection corpus** file, in `corpora/MANIFEST.md`; `config/protocol.yaml:vendor.agentdojo_sha` remains `TODO_C13_C16` and C6 did not resolve another chunk's sentinel |
| CaMeL | licence to be recorded at its pin |
| InjecAgent | ✅ **RECORDED by C6, 2026-08-31** — **MIT** © 2023 Qiusi Zhan. ⚠️ its licence file is spelled **`LICENCE`**, British-style; **both spellings were fetched to prove the miss**: `LICENCE` → HTTP 200, `LICENSE` → **HTTP 404**. `PROVENANCE.md` §3.3 |
| AgentHarm | ✅ **RECORDED by C6, 2026-08-31** — **"MIT License with an additional clause"** © 2024 **Gray Swan AI and UK AI Safety Institute** (⚠️ §11.3 named only the second of the two holders). ⚠️ **field-of-use clause binds even though the dataset is NOT gated** (`"gated": false`, verified) — **our use qualifies and `PROVENANCE.md` §3.3 says so** |
| ASB | ✅ **RECORDED by C6, 2026-08-31** — **MIT** © 2024 AGI Research. `PROVENANCE.md` §3.3 |
| **R-Judge** | ✅ **VERIFIED FIRST-HAND by C6, 2026-08-31 — it ships NO licence file of any kind.** GitHub's repository API reports `"license": null` and the repository root holds no licence-shaped file. Therefore **cited, never vendored, never redistributed** (`CONTEXT.md` §11.3, `PROCESS.md` §12.2). Its Finance subset is a deliberate drop, recorded rather than silently omitted. ⚠️ **Verified from repository METADATA only — not one byte of the corpus was fetched**, which is the whole point of the rule. `PROVENANCE.md` §3.3 |

---

## 6. ⚠️ APPENDED BY C13 (`c2b7f419`), 2026-09-01 — CaMeL and AgentDojo, vendored and measured

**APPEND-ONLY. Nothing above this line is altered.** §1's `TODO_C13_C16` rows are left exactly
as they stand: **only `config/protocol.yaml:vendor.camel_sha` was resolved**, and §6.5 below
records why the AgentDojo row was not.

### 6.1 The pins

| Package | Pinned commit | Why this pin |
|---|---|---|
| **`CaMeL`** (`google-research/camel-prompt-injection`) | `f083b6b396399d3b3c7f2ddaf613a5945eaf32d8` | **`refs/heads/main` = `HEAD`**, resolved by `git ls-remote` on 2026-09-01; the commit is dated **2025-06-20T15:59:27+02:00**. ⚠️ **It predates `CONTEXT.md` §8.5's 2026-08-30 reading by fourteen months**, so the tree those claims were read from has not moved under them — which is *why* all eight line references reproduce exactly. Pinned in `config/protocol.yaml:vendor.camel_sha` |
| **`AgentDojo`** (`ethz-spylab/agentdojo`) | `928bbae820a89556b03de5cf818eb350cd6082d1` (`refs/tags/v0.1.34`) | ⚠️ **NOT `main`, and the reason is first-hand rather than a preference.** CaMeL's own `pyproject.toml` declares `agentdojo>=0.1.34` and its `uv.lock` **resolves that to exactly `0.1.34` from PyPI** (`uv.lock:13-15`). `refs/tags/v0.1.34` is this SHA, and the checked-out tree's own `pyproject.toml:12` reads `version = "0.1.34"` — so the pin is **derived from the third party's own lockfile**, not chosen by a session. `main` today is `089ed468cf3ed0322acc66b0211f26d9d90dbf60`, a much later tree; vendoring that and calling it *"what CaMeL runs on"* would have been a sixth false third-party claim. ⚠️ **Recorded here only — `config/protocol.yaml:vendor.agentdojo_sha` is still `TODO_C13_C16`. See §6.5** |

### 6.2 Reproducing the checkouts

Run from the repository root. A **shallow fetch of the exact SHA**, exactly as §2 does for
τ²-bench: far faster, and it cannot silently land on a different commit.

```bash
# -- CaMeL -------------------------------------------------------------------
mkdir -p vendor/camel-prompt-injection && cd vendor/camel-prompt-injection
git init -q
git remote add origin https://github.com/google-research/camel-prompt-injection.git
git fetch -q --depth 1 origin f083b6b396399d3b3c7f2ddaf613a5945eaf32d8
git checkout -q --detach FETCH_HEAD
git rev-parse HEAD    # must print f083b6b396399d3b3c7f2ddaf613a5945eaf32d8
cd ../..

# -- AgentDojo (v0.1.34 -- the version CaMeL's own uv.lock resolves) ----------
mkdir -p vendor/agentdojo && cd vendor/agentdojo
git init -q
git remote add origin https://github.com/ethz-spylab/agentdojo.git
git fetch -q --depth 1 origin 928bbae820a89556b03de5cf818eb350cd6082d1
git checkout -q --detach FETCH_HEAD
git rev-parse HEAD    # must print 928bbae820a89556b03de5cf818eb350cd6082d1
cd ../..
```

⚠️ **Neither is `pip install`-ed by C13, and that is deliberate.** C13 **parses** these trees
with `ast`; it never imports them. Importing CaMeL executes `models.py`, which imports
`google.genai`, `openai` and `anthropic` — three model clients, in the one package whose whole
job is to *not* call a model. RUN-1's operator installs CaMeL in the operator's own environment,
in the operator's own terminal.

### 6.3 ⚠️ THE MEASURED SIZES — and Q-010's ruling reproducing on a second, independent tree

`[MEASURED HERE, 2026-09-01, FROM GIT BLOBS — never from working-tree bytes]`

| | CaMeL @ `f083b6b3…` | AgentDojo @ `928bbae8…` |
|---|---|---|
| tracked files | **63** | **25,082** |
| total tracked bytes | **2,174,188** (2.17 MB) | **249,841,677** (249.8 MB) |
| largest file | `analysis.ipynb` — 1,031,576 B | `notebooks/analysis.ipynb` — 593,419 B |
| next two | `uv.lock` — 687,349 B; `src/camel/interpreter/interpreter.py` — 100,476 B | `uv.lock` — 554,220 B; `runs/…/injection_task_4.json` — 493,642 B |

⚠️ **99.2 % of AgentDojo — 24,914 files and 247,748,881 bytes — is `runs/`: other people's
published model transcripts** (`claude-3-opus-20240229`, `claude-3-haiku-20240307`, …), which
this project never reads. **That is τ²-bench's `data/tau2/results/` pattern reproducing on an
independent tree**, and it is a second, independent measurement supporting `QUESTIONS.md`
**Q-010**'s ruling that the vendored trees are **pinned, not committed**. AgentDojo `main` is
larger still: 36,860 files and 428,502,698 bytes, **99.5 %** of it `runs/`.

**Combined with τ²-bench's 793.2 MB, committing all three would put ~1.05 GB in front of every
judge**, against `CONTEXT.md` §1's zero-cost-clone claim. ⚠️ **And the cost Q-010 names is now
larger, not smaller: C19's clean-clone test must fetch THREE trees, not one**, or `CONTEXT.md`
§20's first box stays false.

### 6.4 The verification triple — run, and clean on both

```
$ cd vendor/camel-prompt-injection
$ git rev-parse HEAD          -> f083b6b396399d3b3c7f2ddaf613a5945eaf32d8   (== the pin)
$ git status --porcelain      -> (empty)
$ git diff f083b6b39639...    -> (empty)

$ cd vendor/agentdojo
$ git rev-parse HEAD          -> 928bbae820a89556b03de5cf818eb350cd6082d1
$ git status --porcelain      -> (empty)
$ git diff 928bbae820a8...    -> (empty)
```

⚠️ **THE CaMeL PROOF IS COMMITTED AND, MORE IMPORTANTLY, IT IS REGENERATED.**
`src/whetstone_gate/camel_comparator/camel_unmodified.txt` carries the triple above, and
`tests/test_c13_camel_comparator.py::test_the_committed_empty_diff_proof_regenerates_byte_for_byte`
re-runs all three commands against the live checkout and diffs the result **byte for byte**. A
committed diff that nothing re-derives is a screenshot. A second test copies the checkout to a
temp directory, edits one file, and asserts that `status` and `diff` both stop being empty — so
the proof is shown able to go red rather than assumed able.

§3 above names that file `docs/evidence/camel_unmodified.txt`. C13's scope fence permitted only
`src/whetstone_gate/camel_comparator/`, so the file lives there and the divergence is recorded as
`QUESTIONS.md` **Q-060** rather than settled by crossing a fence.

⚠️ **A CRLF TRAP THAT WILL CATCH THE NEXT READER, RECORDED SO THAT IT DOES NOT.**
`core.autocrlf` is `true` on this machine and **CaMeL ships no `.gitattributes`**, so
`interpreter.py` checks out with one CR per line. `CONTEXT.md` §8.5's **100,476 bytes** is the
**git blob**; `stat` on Windows reports **103,192**. `100,476 + 2,716 CR = 103,192` exactly, and
the harness prints all four numbers rather than only the one that looks wrong. **Every size and
line number in this section is taken from `git ls-tree -l` / `git cat-file -s`, never from the
working tree** — the same rule `PROCESS.md` §6a already imposes on the pre-registration
fingerprint, applied here for the same reason.

### 6.5 ⚠️ WHAT C13 DELIBERATELY DID **NOT** DO

* **`config/protocol.yaml:vendor.agentdojo_sha` is still `TODO_C13_C16`.** That key is **C16's**.
  C13 vendored and measured AgentDojo because CaMeL's banking policies are typed on
  `BankingEnvironment` (`banking.py:17`) and the comparator cannot be read without it — but
  resolving another chunk's sentinel is exactly the silent scope creep the fences exist to stop.
  **C16 adopts `928bbae8…` or records why it differs.** `QUESTIONS.md` **Q-059**.
* **C13 did not decide the branch.** `config/lanes.yaml:camel_comparator.branch` is
  `TODO_C13_RUN1` and `make selftest` is **RED on it, correctly**. RUN-1 decides it, inside its
  90-minute box, in the operator's terminal.
* **C13 did not run CaMeL, and did not check whether the model id is still served.** Zero
  provider calls, zero tokens. `PROCESS.md` §8's lane reservation is absolute.

### 6.6 Licences — recorded first-hand at the pins, closing §5's two open rows

| Source | Recorded |
|---|---|
| **CaMeL** | ✅ **Apache-2.0**, verified 2026-09-01 at `f083b6b3…`. ⚠️ **The `LICENSE` file is the UNMODIFIED Apache template — line 190 still reads `Copyright [yyyy] [name of copyright owner]`, so the file itself names no holder.** The holder is in the **per-file headers**: `# Copyright 2025 Google LLC`, carried by **50 of the 54** tracked `.py` files. The correct attribution is therefore *"Apache-2.0, © 2025 Google LLC per the per-file headers"* — **not** a named holder read off `LICENSE`, and **not** "no holder either", which is what `CONTEXT.md` §11.3's PRAMANA/DoomArena note (*"do not attribute a named holder"*) would produce if applied here mechanically. **The two cases differ and the difference is recorded rather than flattened.** |
| **AgentDojo** | ✅ **MIT** © 2024 **Edoardo Debenedetti, Jie Zhang, Mislav Balunovic, Luca Beurer-Kellner, Marc Fischer, and Florian Tramèr** — re-verified first-hand at `928bbae8…`, 2026-09-01, confirming C6's §5 record and Q-034's six names. ⚠️ **The shipped file spells it `Balunovic`, without the diacritic `CONTEXT.md` §11.3 uses (`Balunović`).** MIT requires the notice be reproduced, so **the repository's own spelling is the one to reproduce**; recorded rather than silently normalised. |
