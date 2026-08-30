# REVIEW_C0 — adversarial review of chunk C0, attempt 1

**SESSION-TOKEN:** `52f5307b` · **Role:** REVIEW · **Chunk:** C0 · **Date:** 2026-08-30
**Review type:** `code` (persona 2 — CODE REVIEWER), per `PROCESS.md` §12.1's C0 row.
**Range reviewed:** root commit `ee3cf93` → `9663247` (the whole repository; no prior reviewed tag).

---

# VERDICT: **FAIL**

**Four BLOCKERs, all of the same shape and all in this chunk's own product.** C0's deliverable is
*a set of checks*, and `PROCESS.md` §5.4 says a review gate that cannot go red is not a gate. Four
of C0's checks report **PASS over nothing**:

| | The check | What it reports PASS over |
|---|---|---|
| **B-01** | `check-roles` **E2** and **E3** | a token issued as both `C0 BUILD` and `C0 REVIEW`, and a token reused across two roles — **the two conditions `PROCESS.md` §7a says `make check-roles` fails on** |
| **B-02** | `check-roles` **D3**, "the whole moat" | `gates/` and `scorer/` both importing one shared predicate helper — hard rule 8's **verbatim named spike defect**, in Python |
| **B-03** | `check-roles` **F1/F2/F3** | a `config/` that has lost `protocol.yaml` — a **pre-registration artefact** — while printing *"protocol.yaml and lanes.yaml parse"* |
| **B-04** | `make selftest`, the **pre-spend gate** | a `config/lanes.yaml` from which the key it guards has been deleted: it flips **RED → GREEN** |

None of these is a style issue and none is a matter of taste. Each was reproduced from a fresh clone
of the remote, and each reproduction is printed below with the commands that produce it.

**What this verdict is not.** The three baselines reproduce exactly, the line-ending property
re-derives independently, the provenance chain verifies at source, the secret and leak discipline is
clean, and §13.4's corrected arithmetic is internally consistent to the last decimal. The two build
sessions' self-reporting was, as far as I can check it, honest — including against themselves. That
is not what is being failed here. What is being failed is that **the checks were written against a
repository in which they all pass, and almost none was ever fired at input that should break it.**
Twelve of nineteen mutants survive on that account.

---

# 1. Clean-clone reproduction — the three baselines

Cloned from the **remote**, `core.autocrlf=false`, fresh Python 3.12.2 venv, `pip install -e ".[dev]"`.
Nothing of mine was added before these ran.

| Command | Reported by C0-COMPLETION | Reproduced here | |
|---|---|---|---|
| `python -m whetstone_gate.tasks test` | 41 passed · 1 skipped · 2 deselected | **41 passed · 1 skipped · 2 deselected**, exit 0 | ✅ |
| `python -m whetstone_gate.tasks check-roles` | 14 passed · 0 failed · 3 n/a | **14 passed · 0 failed · 3 n/a**, exit 0 | ✅ |
| `python -m whetstone_gate.tasks selftest` | 1 failed · 1 passed · 42 deselected | **1 failed · 1 passed · 42 deselected**, exit 1 | ✅ |

```bash
git -c core.autocrlf=false clone https://github.com/chinmoypaul8897/whetstone-gate cleanclone
cd cleanclone && py -3.12 -m venv .venv && ./.venv/Scripts/python -m pip install -e ".[dev]"
./.venv/Scripts/python -m whetstone_gate.tasks test        # 41 / 1 / 2, exit 0
./.venv/Scripts/python -m whetstone_gate.tasks check-roles  # 14 / 0 / 3, exit 0
./.venv/Scripts/python -m whetstone_gate.tasks selftest     # 1 failed 1 passed 42 deselected, exit 1
```

**`make test` does not depend on the ambient `tau2-bench`.** The prompt's specific suspicion is
disproved: `tau2-bench` is **not installed** in the clean venv and the suite is green anyway. It is
installed in the operator's tree (`vendor/tau2-bench` at `a2c0247…`, `git status --porcelain` empty,
`requires-python = ">=3.12,<3.14"` at line 10 — all verified here), but nothing in `tests/` imports it.

**Also verified, first-hand:** `python --version` → 3.12.2 · `make` shim present at `~/bin/make.exe`,
GNU Make 3.82.90, runs a recipe · remote returns **HTTP 404 to an anonymous client**, i.e. private ·
`PROVENANCE.md` §1 carries the URL and the `PRIVATE` row · the two dashboard PNGs are committed with
sizes and digests recorded · `evals/` does not exist and nothing under it is tracked.

---

# 2. The clean-clone-from-bare claim — is `CONTEXT.md` §20's first box true today?

**§20 box 1: `git clone` → one command → it runs. Owner split: C19 (the test), C0 (the command).**

**Exactly what a stranger must run, in order, from a bare clone:**

```bash
git clone https://github.com/chinmoypaul8897/whetstone-gate && cd whetstone-gate
py -3.12 -m venv .venv && . .venv/Scripts/activate     # 3.12 REQUIRED, not preferred
pip install -e ".[dev]"                                 # the ".[dev]" is load-bearing — see below
python -m whetstone_gate.tasks test                     # or `make test`
# and, only if tau2-bench is wanted (nothing in tests/ needs it today):
mkdir -p vendor/tau2-bench && cd vendor/tau2-bench
git init -q && git remote add origin https://github.com/sierra-research/tau2-bench.git
git fetch -q --depth 1 origin a2c024725189473d2d7cea3a5cfdbcc67478e41f
git checkout -q --detach FETCH_HEAD && cd ../.. && pip install -e vendor/tau2-bench
```

**The box is NOT true today, for three reasons, one of which is C0's.**

1. ⚠️ **`pip install -e .` — the obvious command — produces a broken `make test`, and nothing says so.**
   `pytest` lives in the `dev` extra. **Reproduced from a bare clone:**
   ```
   $ pip install -e .
   $ python -m whetstone_gate.tasks test
   ...\python.exe: No module named pytest        # exit 1
   ```
   There is **no README.md in this repository**, so the `[dev]` requirement is written nowhere at all.
   `tasks.py` also does not diagnose it — `_pytest` returns pytest's raw exit code, so the user gets a
   one-line `ModuleNotFoundError` from a target whose whole purpose is to be the one command.
2. **`pip install -e vendor/tau2-bench` — a literal C0 done-when box — cannot be run from a bare clone.**
   `vendor/*/` is git-ignored under Q-010. The fetch commands are in `vendor/MANIFEST.md` §2 and they
   work, so this is *documented*, not missing — but Q-010 is an **unruled Class A** item (§8, F-11), and
   the done-when box as written is satisfiable only after a step the box does not mention.
3. `pyproject.toml` declares `readme = "README.md"` against a file that does not exist. Both `pip
   install -e .` and `pip install .` tolerate it silently, so this is LOW — but it is one more thing
   that will be discovered at C19 rather than now.

**What is C0's to fix and what is C19's:** the README is C19's. **The `[dev]` trap is C0's**, because
C0 owns "the command exists" and the command as it stands does not run after the natural install.

---

# 3. The line-ending property, re-derived independently

Run in the Linux-simulating clean clone (`core.autocrlf=false`), not taken from any report.

```python
for every path in `git ls-files -z`:
    sha256(open(path,'rb').read())  ==  sha256(git show HEAD:<path>)
```

| | |
|---|---|
| **Denominator** | **40 tracked files** — every tracked path, none skipped |
| Non-regular paths skipped | **0** |
| Mismatches | **0** |
| Files containing any CR byte | 2 — both PNGs, `401` and `350` CRs, all inside deflate data |

The two PNGs specifically: `git ls-files --eol` → `i/-text w/-text attr/text=auto eol=lf`;
`git check-attr -a` → `text: auto`, `eol: lf`; `git hash-object` and `git hash-object --no-filters`
return **the same blob id** for both. So the attributes *are* applied and the filter chain is a
provable no-op on them. **`.gitattributes` needed no image rule and correctly has none** — adding one
would break A1, which requires that file to contain exactly `* text=auto eol=lf`.

**A2 verified independently:** `.gitattributes` was added in `ee3cf93`, which `git rev-list
--max-parents=0 HEAD` confirms is the root commit.

**The property holds. This part of the freeze prerequisite is sound.**

---

# 4. Findings

Severity key: **BLOCKER** — cannot PASS with it open. **MEDIUM** / **LOW** — goes to
`OPEN_FINDINGS.md`. **INFO** — recorded here only.

---

## B-01 · BLOCKER · `check-roles` E2 and E3 are structurally unable to fail

**Citation.** `PROCESS.md` §7a and `CLAUDE.md` §5, identically:
> **`make check-roles`** fails if any chunk's build and review commits share a token, **if a token
> appears that was never issued**, or if a token is reused across roles.

**Two of those three clauses cannot fire.** `check_session_tokens` builds

```python
issued: dict[str, tuple[str, str]] = {}
for token, chunk, role in _TOKEN_ROW.findall(...):
    issued[token.lower()] = (chunk, role.upper())     # ← keyed by TOKEN
```

A token that appears in **two** rows keeps only the **last**. By the time `by_chunk_role` is built,
every token belongs to exactly one `(chunk, role)` bucket, so:

* `shared_build_review` intersects `by_chunk_role[(chunk,"BUILD")]` with
  `by_chunk_role[(chunk,"REVIEW")]` — for a duplicated token one of those is always empty. **E2 can
  never fire.**
* `reused_across_roles` counts the buckets containing each token — always exactly `1`, so `> 1` is
  never true. **E3 can never fire.**

**Evidence — re-runnable by a third party.** In the clean clone, insert into `QUESTIONS.md`
`## Session tokens` the two violations the rule names:

```
| `deadbeef` | C0 | BUILD  | 2026-08-30 |
| `deadbeef` | C0 | REVIEW | 2026-08-30 |     ← E2's exact condition
| `cafebabe` | C1 | BUILD  | 2026-08-30 |
| `cafebabe` | C2 | FIX    | 2026-08-30 |     ← E3's exact condition
```
then run `check_roles.check_session_tokens(Path('.'))`:

```
rows parsed by _TOKEN_ROW: [('deadbeef','C0','BUILD'), ('deadbeef','C0','REVIEW'),
                            ('cafebabe','C1','BUILD'), ('cafebabe','C2','FIX')]

  PASS E2 no token shared by a chunk's BUILD and REVIEW | clean
  PASS E3 no token reused across roles                  | clean
```

The rows parse. The violations are present. **Both checks say clean.**

**Why this is a BLOCKER and not a MEDIUM.** §7a is candid that session identity is *"an honour system
**with an artefact**"*, and its whole claim is *"here is the check, run it."* The check is the artefact.
Two thirds of it is inert, and the README is scheduled (C19) to tell a panelist that this check exists.
Publishing that sentence over these two checks would be exactly the class of unsound self-certification
this project exists to expose. `PROCESS.md` §5.4 is the governing line: a gate that cannot go red is not
a gate.

**Not caught by anything.** `test_no_commit_carries_a_forged_or_reused_session_token` asserts
`results["E2 …"].ok is True` against the current repository, where the condition is absent. Mutating
E1's predicate to its logical inverse also survives (mutant M11), for the same reason.

---

## B-02 · BLOCKER · the gate/scorer moat check is defeated by hard rule 8's own named defect

**Citation.** `CLAUDE.md` hard rule 8, the ⚠️ clause, verbatim:
> `scorer/` imports nothing from `gates/`; `gates/` imports nothing from `scorer/`; **neither imports a
> shared predicate helper.** … **The test is a module-graph walk over both packages' transitive
> first-party imports**, failing on any shared first-party module outside a short, explicit
> **allow-list of pure value types** … *Why this one line is the whole moat:* in the spike, `gate.js`
> and `invariants.js` both called `world.js:intentKey`, so the invariant **could not have fired unless
> the gate had a bug.**

**Evidence.** Four attack forms, built under `src/whetstone_gate/{gates,scorer}/` in a throwaway tree
and run through `check_roles.check_gate_scorer_isolation`:

| # | What `gates/` and `scorer/` do | D-group verdict |
|---|---|---|
| 1 | both `from whetstone_gate.shared_predicate import intent_key` | **FAIL D3** ✅ correct |
| 2 | both `from whetstone_gate import shared_predicate`, both call `shared_predicate.intent_key` | **PASS** ❌ |
| 3 | `gates/` does `from .. import scorer` | **PASS** ❌ (D1 blind too) |
| 4 | each imports its own helper; both helpers import the shared predicate (**one hop**) | **PASS** ❌ |

Form 2 is the spike defect transliterated into Python, and it is the most natural way to write it in a
`src/whetstone_gate/` layout.

**Three distinct causes:**

1. `shared = (gate_imports & scorer_imports) - {"whetstone_gate"}`. For `from whetstone_gate import X`
   the regex captures the **module** (`whetstone_gate`), not the imported name — so both sides record
   the string `"whetstone_gate"`, and the subtraction then discards it. **The one implicit allow-list
   entry excuses the commonest import form in the project's own layout.** Hard rule 8 permits an
   allow-list only of *"pure value types (enums, the harm-record dataclass, the paise integer wrapper)
   that carry **no predicate logic**"*, and says **adding to it is a Class A deviation requiring an
   architect ruling**. `whetstone_gate` is a package, not a pure value type, and no ruling exists.
2. `head = module.lstrip(".").split(".")[0]` yields `""` for `from .. import scorer`, and `""` is not in
   `package_roots`, so the import is not recorded at all.
3. **The walk is one level deep, not transitive.** `_first_party_imports` reads only the `.py` files
   directly under `gates/` and `scorer/` and collects their *direct* imports. Hard rule 8 says
   **transitive**.

**Mitigating, and stated for fairness:** D1/D2/D3 report `n/a` today (neither directory exists), so no
false claim has yet been published, and the binding tests are C8's and C9's done-when items. That is
precisely why it must be fixed **now**: `check_roles.py`'s own docstring calls D *"the whole moat"*,
`tests/test_repo_invariants.py::test_gates_and_scorer_share_no_first_party_module` delegates to it, and a
C8/C9 reviewer arriving in a fortnight will see a green D3 and conclude the moat holds.

---

## B-03 · BLOCKER · the F group reports `config/` complete over a `config/` missing `protocol.yaml`

**Citation.** `CLAUDE.md` hard rule 9 — *"Every spec-specified value lives in `config/` … a missing
value is a hard refusal, never a silent fallback"* — and its ⚠️ clause: **`config/` is a
pre-registration artefact.** Also hard rule 11: no silent denominator shrinkage.

**Evidence.** In the clean clone: `git rm config/protocol.yaml && git commit`, then
`python -m whetstone_gate.tasks check-roles`:

```
  F - config/ completeness (hard rule 9)
    [PASS] F1 config/ loads
           protocol.yaml and lanes.yaml parse                       ← protocol.yaml DOES NOT EXIST
    [PASS] F2 undetermined values are DECLARED, not defaulted
           1 explicit TODO_ sentinel(s); ...                        ← it was 6
    [PASS] F3 OPERATOR-owed values
           none outstanding

  14 passed, 0 failed, 3 n/a

  OK - no structural invariant is broken.                           ← exit 0
```

Five sentinels vanish from the count — among them
`protocol:probe.void_threshold_breach_rate = TODO_C14_CALIBRATION`, which `config.py`'s own module
docstring calls *"the single number that decides whether the whole run is publishable"*. That is hard
rule 11's shape applied to a check's own denominator, and F1's detail is a **hardcoded string** that
names a file it never opened.

**Two causes.** `outstanding_sentinels()` carries a blanket `if not path.is_file(): continue`, written
so that `ladder.yaml` (legitimately absent until C15) is not an error — and it silently excuses
`protocol.yaml` and `lanes.yaml` too. And `Result("F1 config/ loads", True, "protocol.yaml and
lanes.yaml parse")` states a conclusion rather than reporting what loaded.

**Reachable without any deletion.** Install non-editably — `pip install .`, which is what someone who
has not been told about `-e` will type — and `repo_root()` (`Path(__file__).resolve().parents[2]`)
resolves to `…/.venv/Lib`. Then:

```
    [PASS] F1 config/ loads          protocol.yaml and lanes.yaml parse
    [PASS] F2 undetermined values …  0 explicit TODO_ sentinel(s); no undetermined values remain
    [PASS] F3 OPERATOR-owed values   none outstanding
```
over a directory holding **zero** config files. And `check-prereg` — which hard rule 9 requires inside
**both** `make test` and `make eval` — prints `config/ holds 0 file(s):` and **exits 0**.
See also F-12.

---

## B-04 · BLOCKER · the pre-spend gate flips GREEN when the key it guards is deleted

**Citation.** `PROCESS.md` §8: *"A spend-free self-test runs before any token is spent. If the harness
is broken, it fails for free."* `CONTEXT.md` §13.5(7). And `config.py`'s own docstring: *"There is **no**
`get(key, default=...)`. It does not exist and must not be added."*

**Evidence.** Delete the `camel_comparator:` block from `config/lanes.yaml` and run `make selftest`:

| state | `make selftest` |
|---|---|
| as shipped | `1 failed, 1 passed, 42 deselected` — correctly **RED** |
| `camel_comparator:` block removed | **`2 passed, 42 deselected`** — **GREEN** |

The gate declares the CaMeL branch *decided* when the key does not exist. The mechanism is one line in
`tests/test_lanes_operator_placeholders.py`:

```python
branch = cfg.load("lanes").data.get("camel_comparator", {}).get("branch")
assert not cfg.is_sentinel(branch)
```

It reaches **around** the loader to `.data` and uses `dict.get` with a default — the exact accessor the
loader was built without, so that hard rule 9's refusal could not be got around by accident. It was got
around on purpose, in the test that guards spending. `is_sentinel(None)` is `False`, so absence reads as
determined.

**And the other half of the gate.** Remove `config/lanes.yaml` entirely and
`test_no_operator_placeholder_remains_in_config` **still passes** — `outstanding_sentinels()` skips
missing files (B-03's cause). The check that stood between this project and spending its finite free
tier against a guessed model id passes vacuously whenever the file it guards is absent.

---

## F-05 · MEDIUM · 12 of 19 mutants survive `make test` **and** `make check-roles`

**Method, stated so it can be re-run and so its own weakness is visible.** Each mutant was applied to a
clean clone, **committed** (so that `test_the_object_store_and_the_working_tree_agree` — which fires on
any uncommitted edit to a tracked file — was satisfied; that is the state a real defect lives in), then
`pytest -m "not operator_gate"` and `python -m whetstone_gate.tasks check-roles` were both run, then
`git reset --hard` back to the baseline with the source verified byte-identical. A deliberately
semantics-preserving **control mutant** was included and correctly survived, which is what makes the
harness trustworthy.

| id | verdict | mutation |
|---|---|---|
| M1 | KILLED | `is_sentinel`: `startswith` → equality |
| M2 | KILLED | `require`: drop the `TODO_` refusal |
| M3 | KILLED | `load`: accept any config name |
| **M4** | **SURVIVED** | `load`: accept a non-mapping YAML |
| **M5** | **SURVIVED** | `_walk_sentinels`: stop recursing into lists |
| **M6** | **SURVIVED** | `require`: non-dict traversal returns `None` instead of refusing |
| **M7** | **SURVIVED** | A2: `added[-1]` → `added[0]` |
| **M9** | **SURVIVED** | A4: drop `unverifiable`/`not_regular` from the verdict |
| **M10** | **SURVIVED** | `_eol_classification`: read git's `i/` side instead of `w/` |
| **M11** | **SURVIVED** | E1: invert the forged-token predicate |
| **M12** | **SURVIVED** | E: widen `_TOKEN_TRAILER` to any hex length |
| **M13** | **SURVIVED** | B1: stop detecting a tracked `.env` at all |
| M14 | KILLED | `_round_trips_unchanged`: always return `True` |
| **M15** | **SURVIVED** | D3: hard-wire `shared = set()` |
| M16 | KILLED | registry: rename a row key |
| **M17** | **SURVIVED** | C1: scan only the **first** of the 8 secret patterns |
| M19 | KILLED | B2/B3: point at a non-existent `.env.example` |
| **M20** | **SURVIVED** | A2: substitute a fake root commit |
| M18 | *survived* | **CONTROL** — semantically identical; survival is correct |

**Every survivor left `make test` at exactly `41 passed, 1 skipped, 2 deselected` and `make check-roles`
at exit 0.**

The two most alarming are **M13** (a tracked `.env` no longer detected) and **M17** (the secret scanner
reduced to one of eight patterns — Google, Razorpay, OpenAI, GitHub, AWS and private-key blocks all
unscanned). M17 survives because `test_the_secret_scanner_actually_fires` exercises the *regexes* via
`re.search` and never the *scanner*; the scanner can stop using them and the test cannot tell.

**Root cause, uniform across all twelve:** `tests/test_repo_invariants.py` asserts `result.ok is True`
against the repository under review — a state in which every check passes trivially. Only three tests in
the whole suite build a fixture that should make a check FAIL, and all three concern INC-09's CRLF work.

**Closed by kept probes.** See §6.

---

## F-06 · MEDIUM · `check_gitattributes`'s early return removes three checks from the report — the F1 ruling

Full ruling in §5. In short: reproduced, real, not a false PASS, but it puts a check's **absence** and a
check's **pass** back into the same bucket — the exact diagnosis `INCIDENTS.md` **INC-07** already wrote
for `check_secrets`, and INC-07 named this function as the surviving instance.

---

## F-07 · MEDIUM · E4 prints a false statement about four commits, with the wrong cause attached

The four CTX-13.4 commits **do** carry `Session-Token: WG-2026-08-30-CTX-13.4-A`. `_TOKEN_TRAILER`
cannot parse it, so they fall into `untrailered`, and E4 prints:

```
[ n/a] E4 every commit carries a Session-Token trailer
       20 commit(s) carry no trailer: ['9663247', '6d08cf3', 'd67550e', 'ec3064d', …].
       The C0 build prompt issued no SESSION-TOKEN and this session did not fabricate one …
```

The first four SHAs in that list are exactly the four commits that **do** carry a trailer, and the
explanation offered — Q-001 — is a different session's different cause. Full ruling in §5 (F4).

---

## F-08 · MEDIUM · B1 inspects only the repository root

`env_tracked` matches `f == ".env"` or `f.startswith(".env.")`. A tracked `config/secrets/.env` is
reported **`PASS B1 no .env tracked — none tracked`** (reproduced). `.gitignore`'s `.env` / `.env.*`
patterns are path-agnostic so `git add -f` is required to get there, and **C1 does catch it** if the
value matches one of the eight known shapes (verified: `config/secrets/.env:1 — Groq API key`). So the
exposure is bounded — but B1's printed claim is broader than its check, and the backstop only covers
shapes already enumerated.

---

## F-09 · MEDIUM · the loader returns YAML null, empty and whitespace-only values silently

From the independent re-implementation (§7). `require()` returns `None` for `key:`, `null` and `~`, and
returns `''` / `'   '` for a blank string. `outstanding_sentinels()` does not count any of them, so
`check-roles` F2 reports *"no undetermined values remain"* and `make selftest` passes.

**Concrete failure scenario.** A hand-edit leaves `probe.void_threshold_breach_rate:` with nothing after
the colon. Every sentinel report says clean; the void threshold is `None`; the run proceeds; the void
comparison either raises `TypeError` after the freeze on a run day, or — under an `if threshold:` form —
reads as absent and every run clears the void check. That is, word for word, the scenario `config.py`'s
docstring says the sentinel mechanism exists to prevent, arriving through the input the mechanism cannot
see.

`lanes.yaml`'s `tpd: null` is **not** part of this finding: it means *"no such limit exists"*, it is
documented in the file's header, and `test_every_lane_states_all_four_limits_explicitly` correctly tests
key **presence** rather than truthiness. The finding is that the loader cannot distinguish that from an
omission, and hard rule 9 covers both.

---

## F-10 · MEDIUM · `make test` is red for the whole middle of any session

`test_the_object_store_and_the_working_tree_agree` compares working-tree bytes against `git show HEAD:`,
so **any** uncommitted edit to **any** tracked file turns the suite red. The CTX-13.4 session recorded
hitting this. Consequences:

* the suite cannot be used while writing code, which is when a suite earns its keep;
* it creates standing pressure to **commit in order to go green**, which is the wrong direction of
  causation in a project whose commits are its audit trail;
* it makes the suite useless as a mutation oracle — my first mutation run scored 18/18 "killed" purely
  on tree-dirtiness, control mutant included, and had to be discarded.

`check-roles` A4 already asks §6a's property in the form that is answerable on a dirty tree, and
`test_a4_does_not_fire_merely_because_the_tree_is_dirty` exists precisely to keep it that way. This test
re-introduces what A4 was written to avoid.

---

## F-11 · MEDIUM · Q-010's Class A default was acted on before a ruling

`QUESTIONS.md` Q-010 is marked **Deviation class: A — "it changes what a reviewer receives."** Hard rule
2: *Class A → STOP, ask the architect.* The default was not merely recorded, it was **implemented**:
`.gitignore` gained `vendor/*/` in `ee098a4`, and the 793 MB tree is now outside the repository. The
measurement behind it is sound and I agree with the conclusion — but the mechanism ("Default taken
pending a ruling", a field C0 invented for a format `PROCESS.md` does not specify) converts rule 2's
"STOP and ask" into "proceed and flag" for the one class of deviation that may not be defaulted past.

Q-001 and Q-003's defaults are, by contrast, **acceptable**: Q-001's alternative was to fabricate a
credential or deliver nothing, and Q-003's default is the conservative direction (commit more, ignore
less) and is reversible. Q-010's is neither reversible-at-no-cost nor conservative: it moves a whole
dependency out of the artefact a judge clones. **It needs a ruling before C19's clean-clone test.**

---

## F-12 · MEDIUM · `repo_root()` silently reports on the wrong directory, and never names the one it used

`repo_root()` is `Path(__file__).resolve().parents[2]`, correct only for an editable src-layout install.
Two live consequences:

* **Non-editable install** (`pip install .`): resolves to `…/.venv/Lib`; see B-03's second half.
* **Two checkouts, one venv**: with the clean clone's venv active, `python -m whetstone_gate.tasks
  check-roles` run **from inside a different clone** reports on the *venv's* clone. It printed a
  full green report while the directory I was standing in had a deliberately corrupted
  `.gitattributes`. **It fooled me for one experiment**, which is the strongest evidence I can offer
  that it will fool someone else.

No target prints the root it examined. For a tool whose entire output is *"this repository is sound"*,
not naming the repository is a reporting defect on its own.

---

## F-13 · MEDIUM · any exception in any check destroys the whole `check-roles` report

`run()` builds all four groups in one eager list expression, and
`check_gitattributes(root) + check_secrets(root)` is a single element of it. So a failure in
`check_gitattributes` takes the **secret scan** down with it, along with D, E and F.

Reproduced: a `.gitattributes` containing a non-UTF-8 byte makes `path.read_text(encoding="utf-8")`
raise, and `make check-roles` emits a bare `UnicodeDecodeError` traceback with **no check output at all**
— including no secret scan — and exit 1. Fail-closed on the exit code, zero information in the report.
`_git()` raises `RuntimeError` on any non-zero git exit and has the same blast radius.

---

## F-14 · LOW · `_first_party_imports` misses two more import forms

`import a, b` records only `a` (the regex has one capture group), and `importlib.import_module(...)` is
invisible. The textual approach is deliberate and well-argued (importing `gates` to learn what `gates`
imports would execute it); these are simply two more holes in the same net as B-02.

## F-15 · LOW · the tripwire is evaded by arithmetic decomposition and Indian digit grouping

`5000000` and `5_000_000` are listed; `500 * 10000` and `50_00_000` are not matched. Inherent to a
textual scan and not worth closing, but it is not stated as a limitation anywhere and should be, since
`CONTEXT.md` §8.6 calls an out-of-table constant *"a review BLOCKER"*.

## F-16 · LOW · `pyproject.toml` names a `readme` that does not exist

`readme = "README.md"`; no such file. Tolerated silently by both `pip install -e .` and `pip install .`.
C19 will create it; recorded so it is not discovered on 3 September.

## F-17 · INFO · `STATUS.md` requires an artefact no session can produce

*"No chunk is `PASS` without `docs/reviews/ARCHITECT_CHECK_<N>.md`. An unrecorded gate is not a gate."*
That directory contains no such file and only the architect writes one. Worth confirming that a review
PASS is understood to be necessary-but-not-sufficient, or the rule will be quietly ignored the first
time a chunk passes.

## F-18 · INFO · the superseded byte-identity command now cuts inside the header

`tail -n +35 CONTEXT.md` was calibrated to v1.0's 34-line header. v1.1's header runs to line 61, so the
old command now truncates mid-header — it fails, as the note says it will, but for a second reason the
note does not give. The replacement command is the operative one and it verifies (§9).

---

# 5. F1 – F4: the four reserved rulings

## F1 — the early-return shape in `check_gitattributes`. **Ruling: real, MEDIUM, not a false PASS.**

**Reproduced.** With `.gitattributes` deleted, `check_gitattributes` returns **one** result:

```
FAIL A1 .gitattributes exists
CHECKS RETURNED: 1          ← A2, A3 and A4 do not run and are not reported
```

**Can A1, A3 or A4 be silently shadowed?** Taking each part of the question:

* **A1 cannot.** The early return *is* A1 failing.
* **A3 and A4 can be shadowed, but never into a green report.** The branch is entered only when A1
  fails, so `check-roles` always exits 1 in that state. The shadowing is of **information**, not of the
  verdict: `total` is computed from the results actually returned, so the summary silently prints three
  fewer checks — `11 passed, 1 failed, 3 n/a` — with nothing marking A2/A3/A4 as not-run. The module's
  own contract, in its docstring, is *"Checks that cannot yet apply report `n/a` with the reason, and
  `n/a` is never silently a pass."* Here they report nothing at all, which is weaker than `n/a`.
* **C0-COMPLETION grew the blast radius, as the prompt suspects — but only for A4, and only within the
  already-failing branch.** A4 joined A2 and A3 behind the same return. No new failure mode.
* **The larger version of the same shape is F-13**, and it *does* reach across checks: an exception in
  `check_gitattributes` suppresses `check_secrets` entirely, so a `.gitattributes` problem can silence
  the secret scan. That is the real cost of the shape and it is why this stays open rather than being
  waved through.

**`INCIDENTS.md` INC-07 diagnosed this exactly** — *"a check's absence and a check's pass became
indistinguishable to any caller"* — fixed it in `check_secrets`, and named `check_gitattributes` as the
surviving instance with `Systemic guardrail: none — accepted`. **I do not accept it.** The remedy INC-07
rejected as *"a second list to keep in sync"* is not the only one: emitting A2/A3/A4 as `Result(…, None,
"not evaluated — .gitattributes is missing")` costs four lines, needs no second list, and restores the
module's own stated contract. **MEDIUM. Open.**

## F2 — is Q-012's replacement justification sufficient? **Ruling: YES. No revert. The screenshot box stands.**

The claim under judgement: *"no true positive was lost,"* asserted by a test that clones the repository
and compares bytes.

**I judged it rather than accepting it, and I re-derived the underlying property myself** (§3): across
all 40 tracked files in a fresh clone with `core.autocrlf=false`, working-tree bytes equal
`git show HEAD:` bytes; the two PNGs are `i/-text w/-text` with identical filtered and unfiltered blob
ids. Git applies **no** conversion to `-text` content, so `PROCESS.md` §6a's property — *a reviewer who
clones this gets the committed bytes* — holds there unconditionally.

**Sufficient, for three reasons.**

1. **Hard rule 6 forbids weakening an assertion to get green. It does not require keeping a false one.**
   Old A3 asserted *"no `\r\n` bytes anywhere"*, which is not §6a's property and is not true of any
   binary file. Every failure the narrowing removed was a false positive **with respect to the property
   actually being asserted**, and that is the correct test for a rule-6 question.
2. **The evidence is of the strongest available kind.** `test_every_failure_the_narrowing_removed_was_a_false_positive`
   does not argue; it builds the adversarial file (plain ASCII, CRLF endings, one NUL byte — the case old
   A3 failed on), asserts git really classifies it `-text` so the test cannot pass on the wrong branch,
   **clones the repository**, and compares bytes. If it ever fails, the default is revertible and the test
   says so.
3. **The overclaim was withdrawn in the artefacts a reader actually reads.** `1be73e4`'s message cannot be
   corrected (no history rewrite), and the correction is instead carried in the source comment, in **A4's
   own printed output** — *"On the 2 binary file(s) this holds BY CONSTRUCTION and so asserts nothing"* —
   in INC-09 and in Q-012. Putting it in the runtime output is the right place; it is the only one a
   future reader cannot skip.

**One rider.** A4's honesty depends on that printed sentence. If a later chunk trims the detail strings,
A4 silently becomes an assertion over 38 files wearing a label that says 40. Worth a note in the fix
session.

## F3 — OF-01, the lone CR. **Ruling: CONFIRMED, stays OPEN, partially mitigated by a probe I added.**

**Reproduced.** A file whose only defect is one lone CR:

```
$ printf 'line one\rline two\nline three\n' > loneCR.md && git add . && git commit
$ git ls-files --eol loneCR.md
i/-text w/-text attr/text=auto eol=lf   loneCR.md
   PASS A3 no CRLF in any tracked file          (3 binary files "NOT scanned")
   PASS A4 working tree and object store hold identical bytes
```

**The finding I add, which OF-01 does not state and which changes how it should be fixed:** the working
tree bytes and the committed blob are **identical** (`b'line one\rline two\nline three\n'` both sides).
So **§6a's fingerprint property is not violated by a lone CR** — git converts nothing on `-text`
content, and a fresh clone reproduces the bytes. A3 and A4 are not failing at their own job.

The gap is in a **different** property, and `INCIDENTS.md` INC-10's `Missing` field already names it:
*"nothing checks a tracked document's CONTENT, only its line endings … neither can say 'and it has eaten
a sentence.'"* INC-10 was caught only because that CR happened to be followed by LF. Under a lone CR the
repository goes green over corrupted prose — which is what INC-06 and INC-10 are both about.

**`CONTEXT.md` §19's done-when requires OF-01 resolved** *(as the review prompt states)*. I cannot close
it, because closing it means adding a check and a review session fixes nothing. What I did instead:

* **Verified the proposed discriminator is sound and false-positive-free on this repository.** Both PNGs
  carry NUL bytes in their first 8000 (IHDR); the lone-CR file carries none. It is **not** a second copy
  of git's heuristic — it compares git's verdict against an independent signal, which is the opposite of
  hard rule 8's circularity, and the anti-circularity objection to a reimplementation does not apply.
* **Added it as a kept probe** — `test_no_tracked_file_is_binary_without_a_nul_byte` — so `make test`
  detects the condition from now on.

**It remains OPEN** because `make check-roles`, not `make test`, is what C0's done-when names, and
because the probe detects the condition without reporting it in the check. **Severity stays MEDIUM;
status changes from "reproduced, not fixed" to "reproduced, detected in `make test`, not reported by
`check-roles`."** The fix session adds it as `A5` in `check_gitattributes`.

## F4 — Q-014. **Ruling: a PRESENT but MALFORMED `Session-Token` trailer MUST be a FAILURE. Severity MEDIUM.**

The architect has ruled the format question (8 random hex; the regex is **not** widened) and that ruling
is not reopened here. What is mine is the remaining defect, and the answer is that it must fail closed.

**Four reasons.**

1. **The project's own doctrine.** `CONTEXT.md` §14 closes on Prabu Ram's formula, quoted with its
   source: *"judging fails open and rules fail closed."* This is a rule. It fails open.
2. **It does not merely stay silent — it prints something false.** E4's output names `9663247`,
   `6d08cf3`, `d67550e` and `ec3064d` among *"commit(s) carry no trailer"* when all four carry one, and
   offers Q-001's cause for them. A check that misreports is worse than one that says nothing, because
   its output is what a reader trusts. This is why I rank it above a cosmetic gap.
3. **The architect's ruling is what makes failing safe.** With 8-hex mandated from now on, a
   non-conforming trailer is a **strictly abnormal** condition: either a prompt issued a malformed token
   or somebody typed one by hand. Both should stop the build. Before the ruling, failing closed would
   have blocked legitimate work; after it, it cannot.
4. **The cost is four lines.** A second, permissive pattern — `^Session-Token:\s*(\S.*?)\s*$` — run when
   the strict one does not match, feeding a new `E5 malformed Session-Token trailer` that FAILS and names
   the SHAs. `untrailered` then means what it says.

**Why MEDIUM and not BLOCKER.** No forged token exists today; E1 does work on well-formed input (verified
— a commit carrying `Session-Token: deadbeef` with no matching row makes E1 FAIL and turns the suite
red); and the affected session's token is honestly recorded in `QUESTIONS.md` with the gap named. **But
it must be fixed before the first chunk whose build and review are separate sessions — i.e. before C1
is reviewed** — because from that point on E1's silence is the only thing standing between the log and
an invented credential. **It compounds B-01: E2 and E3 cannot fire, and E1 cannot see a malformed token.
Of §7a's three named conditions, exactly one works, on exactly one shape of input.**

---

# 6. Mutation testing — what I tried, what survived, what I added

**19 mutants + 1 control**, per-mutant, applied to a clean clone, committed, both entry points run,
`git reset --hard` between each with the source verified byte-identical. **Before the probes: 6 killed,
12 survived, control correctly survived.** Full table in F-05.

**Probes added — `tests/test_c0_review_probes.py`, 20 tests, all passing.** They are probes, not fixes:
each fires a check at input that should break it, and each names the mutant it kills.

| Probe | Kills | Closes |
|---|---|---|
| `test_b1_fires_on_a_tracked_env_file` | **M13** | B1 was never fired end to end |
| `test_c1_fires_through_check_secrets_for_every_pattern` (×8) | **M17** | all 8 patterns **through the scanner**, not via `re.search` |
| `test_e1_fires_on_a_commit_carrying_an_unissued_token` | **M11** | E1 had no input at all |
| `test_the_token_trailer_matches_exactly_eight_hex_and_nothing_else` | **M12** | pins the architect's Q-014 ruling *(regex NOT widened)*, which nothing held in place |
| `test_a2_fires_when_gitattributes_is_not_in_the_first_commit` | — | §6a's one-shot property, the late-add case |
| `test_a2_reads_the_EARLIEST_add_not_the_latest` | **M7** | added-deleted-re-added; the first probe could not tell `added[0]` from `added[-1]` with one adding commit |
| `test_a4_fires_when_a_tracked_path_has_no_regular_file` | **M9** | `b0a4855`'s rule-11 fix had no test behind it |
| `test_eol_classification_reports_the_working_tree_side` | **M10** | `w/` vs `i/`, which §6a distinguishes |
| `test_no_tracked_file_is_binary_without_a_nul_byte` | — | **OF-01**'s discriminator (F3) |
| `test_load_refuses_a_yaml_that_is_not_a_mapping` | **M4** | |
| `test_require_refuses_when_the_path_traverses_a_non_mapping` | **M6** | hard rule 9's refusal |
| `test_sentinels_are_found_inside_lists` | **M5** | the whole operator gate hangs on this one `elif` |
| `test_protocol_yaml_holds_no_null_and_no_empty_string` | — | F-09's typo-shaped half |

**After the probes: 17 of 19 killed.** The two that remain:

* **M15 (D3 hard-wired to `shared = set()`) — deliberately not closed.** A probe could only assert D3
  fires on the one form it already catches, which would leave a green test standing over B-02. **B-02
  needs a fix, not a probe.**
* **M20 (`roots = … or ["x"]`) — an equivalent mutant.** `git rev-list --max-parents=0 HEAD` cannot
  return empty while HEAD resolves, and if HEAD does not resolve `_git` raises first. The fallback is
  unreachable, so the mutation changes no behaviour and survival is correct.

**Suite after the probes: 61 passed, 1 skipped, 2 deselected.**

---

# 7. The independent re-implementation

Written from `CLAUDE.md` hard rule 9, `PROCESS.md` §4.9/§5.1 and `PROCESS.md` §12.1's C7 row alone,
importing nothing from the project. My six stated rules and the diff:

| input | mine | theirs | agree |
|---|---|---|---|
| determined int | `5000000` | `5000000` | ✅ |
| absent key | REFUSE | `MissingRequiredValue` | ✅ |
| `TODO_C14_CALIBRATION` | REFUSE | `UndeterminedValue` | ✅ |
| `0` | return `0` | return `0` | ✅ |
| `false` | return `False` | return `False` | ✅ |
| `[]` | return `[]` | return `[]` | ✅ |
| `key:` (YAML null) | REFUSE | **return `None`** | ❌ |
| `null` | REFUSE | **return `None`** | ❌ |
| `~` | REFUSE | **return `None`** | ❌ |
| `""` | REFUSE | **return `''`** | ❌ |
| `"   "` | REFUSE | **return `'   '`** | ❌ |
| `todo_C14_CALIBRATION` (lowercase) | REFUSE | **return the string** | ❌ |

**Where it agrees, and this is worth saying because it is the classic way rule 9 is got wrong:** both
implementations return `0`, `False` and `[]`. A truthiness test would treat all three as missing and a
`per_action_cap_paise: 0` would then silently become a refusal. Theirs walks the key path and tests
`is_sentinel`, never truthiness. **That is correct and I would not change it.**

**Where it diverges:** four classes, all of them *"the value was written down but never supplied"*.
Theirs returns it; mine refuses. See F-09 for the failure scenario. A seventh divergence sits in the
sweep rather than the accessor: my `outstanding()` **refuses** when a required config file is missing,
because a sweep that skips a file it cannot open reports a smaller number than the truth — theirs
`continue`s, which is B-03's cause.

**The lowercase-sentinel divergence is the weakest of mine** and I record it as a preference, not a
defect: a case-sensitive prefix is documented behaviour. It is worth a case-insensitive match only
because a config author who types `todo_operator` has declared it undetermined just as loudly.

Kept at `docs/reviews/independent/c0_config_loader.py`.

---

# 8. Class-B (and defaulted Class-A) decisions, judged

| Item | Class | Ruling |
|---|---|---|
| **Q-002** — a `**Date:**` line beyond hard rule 13's field list | B | **ACCEPT.** Rule 13 fixes the fields an entry must contain, not the fields it may not. The date is what makes *"at least two entries dated after the first build commit"* checkable at all, and it is checked. |
| **Q-009** — two tiers: `make test` deselects `operator_gate`, `make selftest` runs it | B | **ACCEPT.** The two done-when boxes genuinely contradict, the split is the only resolution that satisfies both, and it is not hidden: `task_test` **prints** what it deselected and why, `check-roles` F3 reports it, and `selftest` fails naming the lanes. This is the right shape. ⚠️ But see **B-04** — the gate the split created is itself vacuous, which is a defect in the gate, not in the split. |
| **Q-012** — A3 narrowed to git-classified text, A4 added | B | **ACCEPT.** Full reasoning at F2. The replacement justification holds, and I re-derived it rather than taking it. |
| Two-mode tripwire (STRICT / CONTEXTUAL) | B (unnumbered) | **ACCEPT.** A single strict mode over `2`, `20`, `25`, `30` would fire constantly and the first response would be to weaken it — which hard rule 6 forbids and which is how tripwires die. `test_registry_covers_every_config_constant` is what keeps it honest, and it killed a mutant (M16). |
| `TRIPWIRE_SELF_EXCLUSION` as a one-entry list with a test pinning it at one | B (unnumbered) | **ACCEPT.** The exclusion is unavoidable and the test is exactly the right guard against it growing into an amnesty. |
| **Q-001** — no trailer on C0's commits; nothing fabricated | A, **defaulted** | **ACCEPT.** The alternatives were to forge a credential in the audit trail of a project whose thesis is that self-certified evidence is worthless, or to deliver nothing. The chosen option is the reversible one and the gap is permanent and visible. Correct call. |
| **Q-003** — `evals/` outputs committed, only transient files ignored | A, **defaulted** | **ACCEPT.** `CONTEXT.md` §16 and `PROCESS.md` §9/§6b all require the outputs committed; the default is the conservative direction and is trivially reversible. |
| **Q-010** — vendored trees pinned, not committed | A, **defaulted and ACTED ON** | ⚠️ **F-11. Needs an architect ruling before C19.** The measurement is sound and I agree with the conclusion. The objection is procedural: `.gitignore` gained `vendor/*/` in `ee098a4`, so a Class A deviation is in force, unruled, and it changes what a judge receives. |
| **Q-004** — package layout ambiguity | A, **open, correctly not defaulted** | **CORRECT.** `check_roles` checks *both* candidate layouts and needs no edit when the ruling lands. This is how a Class A stop should look. |
| **Q-014** — malformed token recorded, not fixed | recorded | **CORRECT to record; the fix is now due.** See F4. |

---

# 9. Secret, spend and leak checks

**Secrets — clean.**
* No `.env` tracked (only `.env.example`, which carries `GROQ_API_KEY=` and `GOOGLE_API_KEY=` as bare
  names with no values). No `.env` file exists in the working tree at all.
* My own independent history scan — `git log -p --all` against eight key patterns plus
  `api_key = "…"` and `Authorization: Bearer …` shapes across all tracked files — returned **zero hits**.
  (C21 still owns the committed history scan; this is an early look, not a substitute.)
* No key value appears in any `docs/sessions/` transcript, any report, or any log.

**Spend — zero, and structurally so.**
* `evals/` **does not exist** and nothing under it is tracked, which is consistent with both build
  sessions' claim of zero provider calls and is the only checkable form that claim can take pre-C14.
* Nothing in `src/` or `tests/` imports an HTTP client, an SDK, or reads `GROQ_API_KEY`/`GOOGLE_API_KEY`.
* The four Google model ids in `config/lanes.yaml` were operator-captured; writing an id into a YAML file
  is not a call.
* **This review spent zero tokens and made zero provider calls.** The only network operations were
  `git clone`/`git ls-remote` against the project's own remote and one anonymous HTTP request to the
  repository URL to establish that it is private (404).

**Leak check — clean.** The research directory `C:\Users\chinm\razorpay buildathon` holds **17 files**. I
hashed every one against every tracked file and measured verbatim line overlap for each:

| | |
|---|---|
| Byte-identical to a tracked file | **`PROCESS.md` only** (`cc1587e7b4c4…`, matching its commit message exactly) |
| `PROJECT_SPEC.md` | sha256 **`10f6746c…`** — **exactly the common-ancestor digest `CONTEXT.md`'s header records**, verified at source |
| Long-line overlap, all 15 other files | `PROCESS_AUDIT.md` 5.5%, `SPEC_CHANGELOG.md` 3.2%, **every other file 0.0%** |
| Those overlapping lines | **100% explained** by `PROCESS.md`/`CONTEXT.md` themselves — the two changelogs quote the documents they describe. Zero lines unaccounted for. |
| `docs/sessions/*.txt` | **zero** lines from any unsanctioned research file |

**Exactly the two sanctioned files came across. Nothing else, under any name, in any form.**

---

# 10. The provenance chain

`CONTEXT.md` is v1.1 and its byte-identity note is marked SUPERSEDED. The replacement command, run
verbatim:

```
$ git show 310488d:CONTEXT.md | tail -n +35 | sha256sum
10f6746c46973112e4129cd9f44fa1bf6f8b146ee7927861ee26e7146f07ac1b     ← matches the recorded digest
$ tail -n +35 CONTEXT.md | sha256sum
892b033a…                                                            ← correctly does NOT reproduce
```

And, independently, `sha256(PROJECT_SPEC.md)` **at source** is `10f6746c…`. The common-ancestor claim is
therefore verified from two directions, not one.

**§13.4's three branch totals are internally consistent** — I recomputed every cell from the block table
and the four feasibility bullets:

| branch | attacker | benign | judge | user sim | total | ÷ 1.92M |
|---|---|---|---|---|---|---|
| N=50, T-FP 40 | 550 × 60K = 33.00M | 350 × 50K = 17.50M | 3 × 170 = 510 ep × 30K = 15.30M | 370 × 30K = 11.10M | **76.90M** | **40.05 h** ✅ |
| N=30, T-FP 40 | 450 × 60K = 27.00M | 350 × 50K = 17.50M | 3 × 150 = 450 ep × 30K = 13.50M | 370 × 30K = 11.10M | **69.10M** | **35.99 h** ✅ |
| N=30, T-FP 20 | 450 × 60K = 27.00M | 250 × 50K = 12.50M | 3 × 130 = 390 ep × 30K = 11.70M | 270 × 30K = 8.10M | **59.30M** | **30.89 h** ✅ |

Every episode count reconciles to the block table: attacker `30 CAL + 10 pilot + N×5 M-ADV + 170 T-NEG +
80 AD-CMP + 10 ladder`; judge per arm `N + 34 + 16 + 30 + T-FP`; user sim `170 + 5 × T-FP`. Requests
`11,000 + 7,000 + 10,200 + 7,400 = 35,600`. **All three totals, all three lane-hour figures and the
whole component table check out to the stated precision, and the corrected chain 40.05 → 35.99 → 30.89
terminates inside the 32 h budget as the ruling claims.**

---

# 11. What I could not verify

1. **What the two dashboard PNGs depict.** A session cannot read an image. `PROVENANCE.md` already labels
   the content OPERATOR-ATTESTED and does not claim otherwise; I verified them only as *files*.
2. **That no payment method is attached to either provider account.** Operator-attested. `PROVENANCE.md`
   §1.5 correctly records that no done-when re-checks it before the public flip, and `STATUS.md` carries
   the flag.
3. **That the sessions were actually different.** Nothing can prove this — §7a says so plainly. What I
   *can* say is that the mechanism §7a offers in its place is, today, two-thirds inert (B-01).
4. **Whether `pip install -e vendor/tau2-bench` completes from scratch.** I verified the checkout in the
   operator's tree is at the pinned SHA, clean, and declares `>=3.12,<3.14`. I did not re-run the install
   — it pulls 74 dependencies and is outside a review's remit.
5. **The remote's privacy setting as GitHub records it.** I established that an anonymous client gets 404,
   which is consistent with private (and with deleted, which `git ls-remote` rules out). I did not query
   the GitHub API.
6. **Anything about C1–C21.** Out of range.

---

# 12. What I would look at next with another hour

1. **Fire every remaining `check_roles` branch at a failing fixture and count the ones that have never
   been executed.** I fired seventeen; the pattern was so consistent that the right next step is a
   coverage run over `check_roles.py` restricted to the *failure* branches. My guess is that a third of
   the module has never executed.
2. **`_eol_classification`'s parser against hostile paths** — a path containing a literal tab, a
   quoted/escaped path (`core.quotepath`), a non-ASCII filename. It partitions on the first tab, which is
   right, but `git ls-files -z` still quotes some names and nothing tests it.
3. **`config/protocol.yaml` line by line against `CONTEXT.md` §8.6.** I checked the *registry* covers the
   table; I did not check every *value* in the YAML equals the spec's. That is the one place a wrong
   number would propagate silently into everything, and C14 freezes it.
4. **Whether `check-prereg` can ever fail.** Today it returns 0 on every path, including
   `config/ holds 0 file(s)`. Hard rule 9 puts it inside `make test` and `make eval`; C14 gives it a
   manifest. Someone should write down now what its FAIL looks like, because a check that has only ever
   returned 0 is the class of object this review has spent an hour on.
5. **The `.gitignore`'s `evals/` rules against Q-003's default**, before RUN-3 writes the first episode
   and discovers that something it needed was ignored.

---

# 13. Disposition

**FAIL.** No `c0-pass` tag is cut. Nothing was fixed.

**To clear this review, a FIX session must close B-01, B-02, B-03 and B-04**, writing its
`INCIDENTS.md` entries first (hard rule 13), and then a fresh review re-runs §4's evidence. The MEDIUMs
and LOWs go to `docs/reviews/OPEN_FINDINGS.md` as OF-02 … OF-12; **OF-01 stays open** with its status
updated per F3.

*This review changed no source file. It added `tests/test_c0_review_probes.py` (18 kept probes, all
passing) and `docs/reviews/independent/c0_config_loader.py` (the re-implementation), and recorded its
own SESSION-TOKEN in `QUESTIONS.md` under `## Session tokens` as `PROCESS.md` §7a requires — which is
itself an honour-system act, and is noted as one.*
