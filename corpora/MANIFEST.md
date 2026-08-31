# `corpora/` — the attacker's seeded inputs, pinned

**`CONTEXT.md` §11.3: the attacker's inputs are not ours either.** *"The attacker composes
and adapts from published corpora; it does not invent from a blank page and it never sees
our policy."*

⚠️ **The corpus payloads are NOT committed to this repository.** The pins, the fetch
commands, the verification and the SHA-256 of every pinned file are. This follows
`QUESTIONS.md` **Q-010**, ruled — *pin, do not commit* — and `vendor/MANIFEST.md`'s shape.

⚠️ **R-Judge is CITED, NEVER VENDORED.** It ships **no licence file of any kind**, verified
first-hand here (§4). It appears in no row of this file and in no row of
`corpora/seed_index.json`, and nothing in `src/whetstone_gate/attacker/` fetches it.

---

## 1. The pins

Every SHA below was resolved **first-hand on 2026-08-31** by the C6 build session
(`SESSION-TOKEN: 4377265b`), and every byte count and hash was computed from the bytes the
pin actually returned. Licences are in `PROVENANCE.md` §3.3, each verified at source.

| Corpus | Repository | Pinned revision | Licence |
|---|---|---|---|
| **InjecAgent** | `github.com/uiuc-kang-lab/InjecAgent` | `f19c9f2c79a41046eb13c03c51a24c567a8ffa07` | **MIT** © 2023 Qiusi Zhan ⚠️ file spelled **`LICENCE`** |
| **AgentDojo** (injection corpus) | `github.com/ethz-spylab/agentdojo` | `089ed468cf3ed0322acc66b0211f26d9d90dbf60` | **MIT** © 2024 Debenedetti, Zhang, Balunović, Beurer-Kellner, Fischer, Tramèr |
| **AgentHarm** | `huggingface.co/datasets/ai-safety-institute/AgentHarm` | `e23b3fe60a0da9037314b88e5ee3a0c054970dad` | **MIT + an additional clause** © 2024 Gray Swan AI and UK AI Safety Institute ⚠️ **field-of-use clause** |
| **Agent Security Bench** | `github.com/agiresearch/ASB` | `1f561dccf92d55302368fa67679b4ba9d9c8fdc4` | **MIT** © 2024 AGI Research |
| **R-Judge** | `github.com/Lordog/R-Judge` | ⚠️ **not pinned — not fetched** | ⚠️ **NONE** — cited, never vendored |

## 2. The pinned files, and their hashes

`corpora/seed_index.json` is the machine-readable form of this table and is what
`src/whetstone_gate/attacker/corpus.py` reads. **The loader verifies each hash before it
parses**, because once the payload is not committed the pin is the entire integrity story.

| Corpus | Path within the pinned tree | Bytes | SHA-256 |
|---|---|---|---|
| InjecAgent | `data/attacker_cases_dh.jsonl` | 10,937 | `999d52e15af3c80a3303a09430af0f3878d1f91e4c573ca7b477a91cdfa6b991` |
| InjecAgent | `data/attacker_cases_ds.jsonl` | 13,209 | `87952398c989d8ca841724e38ecdbb789676d3841e19dfc44aac7b710df9cb1f` |
| AgentDojo | `src/agentdojo/data/suites/banking/injection_vectors.yaml` | 657 | `4eb98a601c108d9b4d88f5d3f2dbf455f775a718975a0ae2624b4cf0d0f6f819` |
| AgentHarm | `benchmark/harmful_behaviors_validation.json` | 22,584 | `40cd099915258b41142acfc88a9f2b4e15cd631c5490ad02a0dce0cf2b9c175e` |
| ASB | `data/all_attack_tools.jsonl` | 209,436 | `c960ab1e60dee2038d51bc64e8f119e565c037c95a8565f176899de8d819a4b2` |

**Cross-check performed here:** for the four GitHub files, the byte counts above were
obtained **twice by independent routes** — from the GitHub trees API at the pinned SHA, and
from `wc -c` over the downloaded bytes — and they agree exactly.

**AgentDojo's file is the BANKING suite's injection corpus**, which is `CONTEXT.md` §11.2's
suite. It is deliberately **not** taken from `runs/`, which is that project's archive of
other people's published model transcripts — the same distinction `vendor/MANIFEST.md` §4
draws for τ²-bench's `data/tau2/results/`.

## 3. Reproducing the checkouts

Run from the repository root. A **shallow fetch of the exact revision** is used rather than
a full clone: far faster, and it cannot silently land on a different commit.

```bash
# ── InjecAgent ──────────────────────────────────────────────────────────────
mkdir -p corpora/fetched/injecagent && cd corpora/fetched/injecagent
git init -q
git remote add origin https://github.com/uiuc-kang-lab/InjecAgent.git
git fetch -q --depth 1 origin f19c9f2c79a41046eb13c03c51a24c567a8ffa07
git checkout -q --detach FETCH_HEAD
git rev-parse HEAD          # must print f19c9f2c79a41046eb13c03c51a24c567a8ffa07
cd ../../..

# ── AgentDojo ───────────────────────────────────────────────────────────────
mkdir -p corpora/fetched/agentdojo && cd corpora/fetched/agentdojo
git init -q
git remote add origin https://github.com/ethz-spylab/agentdojo.git
git fetch -q --depth 1 origin 089ed468cf3ed0322acc66b0211f26d9d90dbf60
git checkout -q --detach FETCH_HEAD
git rev-parse HEAD          # must print 089ed468cf3ed0322acc66b0211f26d9d90dbf60
cd ../../..

# ── Agent Security Bench ────────────────────────────────────────────────────
mkdir -p corpora/fetched/asb && cd corpora/fetched/asb
git init -q
git remote add origin https://github.com/agiresearch/ASB.git
git fetch -q --depth 1 origin 1f561dccf92d55302368fa67679b4ba9d9c8fdc4
git checkout -q --detach FETCH_HEAD
git rev-parse HEAD          # must print 1f561dccf92d55302368fa67679b4ba9d9c8fdc4
cd ../../..

# ── AgentHarm (a HuggingFace dataset, so the revision is an HF commit) ───────
mkdir -p corpora/fetched/agentharm/benchmark
curl -fsSL -o corpora/fetched/agentharm/benchmark/harmful_behaviors_validation.json \
  https://huggingface.co/datasets/ai-safety-institute/AgentHarm/resolve/e23b3fe60a0da9037314b88e5ee3a0c054970dad/benchmark/harmful_behaviors_validation.json
```

## 4. Verifying a fetched tree has not been touched

```bash
cd corpora/fetched/injecagent
git rev-parse HEAD                     # the pinned SHA, exactly
git status --porcelain                 # MUST be empty
git diff f19c9f2c79a41046eb13c03c51a24c567a8ffa07   # MUST be empty
```

…and the same three commands in `corpora/fetched/agentdojo` and `corpora/fetched/asb`
against their own pins. **AgentHarm is fetched as a single file rather than a git tree, so
its integrity check is its SHA-256 alone** — which is the check
`src/whetstone_gate/attacker/corpus.py` applies to all five files on every load, before it
parses any of them.

## 5. Licences — verified first-hand, 2026-08-31

Recorded in full in `PROVENANCE.md` §3.3, with the URL fetched, the HTTP status and the
verbatim clause where one binds. The two facts that a build script gets wrong silently:

- ⚠️ **InjecAgent's licence file is spelled `LICENCE`** (British). Verified here by
  fetching **both** spellings: `LICENCE` → **HTTP 200**, `LICENSE` → **HTTP 404**. A build
  script globbing `LICENSE*` finds nothing and would wrongly report *"no licence"*.
- ⚠️ **AgentHarm's field-of-use clause binds even though the dataset is NOT gated**
  (`"gated": false`, verified against the HuggingFace API here), so there is no
  click-through to accept and nothing prompts a reader to look. **Our use qualifies** and
  `PROVENANCE.md` §3.3 says so explicitly.
- ⚠️ **R-Judge ships no licence file of any kind**, verified here against the GitHub API:
  `license` is `null` and the repository root holds no licence-shaped file. Therefore
  **cited, never vendored, never redistributed** — a deliberate drop, recorded rather than
  silently omitted (`PROCESS.md` §12.2).
