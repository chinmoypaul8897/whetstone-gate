# C3 — INDEPENDENT (BLIND) ENUMERATION

**Session:** `a66c389d` — REVIEW C3, attempt 1, **Phase 1 (blind)**.
**Committed before Phase 2 began.** Nothing under `src/whetstone_gate/tau2/`,
`tests/test_c3_tau2_enumeration.py`, `PROGRESS.md`, `INCIDENTS.md`,
`docs/sessions/c3-build-1.txt`, `config/protocol.yaml`'s `selections:` block, or the C3 diff had
been opened when this file was written.

This is Q-020's substitute for a reimplementation. C3 reimplements nothing of ours — its expected
values are Sierra's task files at a pinned SHA, external by construction — so what is independent
here is the **method**, not the data.

**Vendored tree at the time of derivation:**

```
git -C vendor/tau2-bench rev-parse HEAD  -> a2c024725189473d2d7cea3a5cfdbcc67478e41f
git -C vendor/tau2-bench status --porcelain -> (empty)
```

**Repo tags existing at the time of derivation:** `c0-pass` **only**. `probe-v1` and `prereg-v1` do
**not** exist. This matters and is used in §7.

---

## 1. My method, stated before the numbers

Inputs: **the vendored Sierra checkout only.** Harness:
`docs/reviews/independent/c3_enumeration.py` (committed beside this file).

1. **WRITE tools come from the decorator, never from a hand-list.** A hand-list would be an answer
   key we authored, which is the exact failure this project exists to criticise. I identify them
   **two independent ways and diff the two**:
   - **(A) `ast` parse** of `src/tau2/domains/<domain>/tools.py` — walk every `ClassDef`, every
     `FunctionDef`, every entry in `decorator_list`; accept a decorator whose callee is `is_tool`
     **or `is_discoverable_tool`** (both exist in `toolkit.py` and both set `__tool_type__`);
     resolve the type from positional `args[0]` **or** the `tool_type=` keyword **or** the
     signature default (`ToolType.READ`) when the decorator is called bare. No import, no
     `litellm`, ~40 ms.
   - **(B) runtime import** of `AirlineTools` / `RetailTools`, reading `__tool_type__` and
     `__mutates_state__` off each entry of the metaclass-built `_func_tools`.
2. **Tasks come from the raw `tasks.json`**, parsed with `json`, not through Sierra's pydantic
   models — a deliberately different path from any that loads `Task.model_validate`.
3. A task is **empty** if `evaluation_criteria.actions` is absent, `null` or `[]`; **write** if any
   action's `name` is in the domain's WRITE set; **read-only** otherwise.
   **must-not-write = empty + read-only.**
4. Every partition is asserted to sum to its domain total, and the two domain totals to 164.
5. I also census, per domain: every action `name` **not** found in that domain's decorated toolkit,
   and every distinct `requestor` value.

---

## 2. THE SORT RULE — recorded before I looked at C3's

> **My rule: ascending bytewise (codepoint) order on the task `id` AS A STRING, applied within
> each domain independently; take the first 20 of that domain's write-task ids.**

`CONTEXT.md` §13.4 says only *"the first 40 write-task ids after sorting, stratified 20 airline /
20 retail."* It does not name a sort. I chose bytewise for three reasons, in this order:

1. **It is the type's own order.** `Task.id` is `str` in
   `vendor/tau2-bench/src/tau2/data_model/tasks.py`, and every id in `tasks.json` is a JSON string
   (`{'str'}` for all 164). Sorting a `list[str]` with no key is bytewise in Python and in every
   other language's default string comparator. A numeric sort requires **coercing the field to a
   type it is not**, which is an assumption the spec never states.
2. **Numeric sort is not total over τ²'s id space.** Telecom ids look like
   `[mobile_data_issue]user_abroad_roaming_enabled_off[PERSONA:None]` — **all 2,285 are
   non-numeric**, and `int(id)` raises on every one. A selection rule that only works on two of the
   three domains is a weaker rule than one that works on all three, and §11.1 excludes telecom on a
   *structural* ground that could in principle be revisited.
3. **Reproducibility by a stranger.** The pre-registration's whole claim is that a third party can
   regenerate the selection from the pinned SHA. "Sort the ids" with no coercion step is the
   instruction with the fewest hidden premises.

**The counter-argument, stated honestly:** a reader of *"the first 40 write-task ids"* will very
plausibly picture `0, 1, 2, …`. The phrase as written in §13.4 **is ambiguous**, and §7 below
records what that ambiguity is worth in ids.

---

## 3. WRITE TOOLS, FROM THE DECORATOR

Both toolkits derive **directly** from `ToolKitBase` (no intermediate class contributing tools),
both import only `is_tool` (neither uses `is_discoverable_tool`), and neither domain's
`environment.py` adds a tool. Airline and retail have **no user-side toolkit** — only `telecom` and
`mock` ship a `user_tools.py` — so their reference trajectories are single-control.

| Domain | decorated tools | WRITE | names |
|---|---|---|---|
| **airline** | 14 | **6** | `book_reservation`, `cancel_reservation`, `send_certificate`, `update_reservation_baggages`, `update_reservation_flights`, `update_reservation_passengers` |
| **retail** | 16 | **7** | `cancel_pending_order`, `exchange_delivered_order_items`, `modify_pending_order_address`, `modify_pending_order_items`, `modify_pending_order_payment`, `modify_user_address`, `return_delivered_order_items` |

**Method (A) `ast` and method (B) runtime agree exactly**, on both the full tool set and the WRITE
subset, in both domains:

```
[airline] ast==runtime tool set : True    ast==runtime WRITE set : True
[retail ] ast==runtime tool set : True    ast==runtime WRITE set : True
```

`transfer_to_human_agents` is `ToolType.GENERIC` at this SHA — **not** WRITE — in both domains, and
`calculate` is GENERIC. Neither counts as a write. `send_certificate` is WRITE but appears in **zero**
reference trajectories.

**`mutates_state` is not a second answer.** No decorator in either domain overrides it, so the
inferred `mutates_state == (tool_type is WRITE)` and the runtime `__mutates_state__ == True` set is
**identical** to the WRITE set (6 airline, 7 retail). Classifying by `mutates_state` instead of by
`tool_type` would change nothing at this SHA. That is a fact about this SHA, not a licence to use it.

---

## 4. THE MUST-NOT-WRITE ENUMERATION

| Domain | total | empty | read-only | **must-not-write** | write | sums? |
|---|---|---|---|---|---|---|
| **airline** | 50 | **7** | **17** | **24** | 26 | ✅ 7+17+26 = 50 |
| **retail** | 114 | **2** | **8** | **10** | 104 | ✅ 2+8+104 = 114 |
| **COMBINED** | **164** | 9 | 25 | **34** | **130** | ✅ 34+130 = 164 |

**Ids, in full:**

- airline **empty (7)**: `0, 10, 26, 28, 31, 34, 46`
- airline **read-only (17)**: `1, 2, 3, 4, 5, 6, 9, 13, 27, 36, 38, 41, 43, 45, 47, 48, 49`
- retail **empty (2)**: `24, 57`
- retail **read-only (8)**: `10, 12, 25, 50, 62, 65, 67, 68`

All nine "empty" tasks carry a literal `[]`. **None** is `null` and **none** is missing, in either
domain — so the empty branch is exercised by real data and is not a defensive no-op.

`get_tasks()`'s default split is `"base"`, and `split_tasks.json` gives `base = 50` (airline) and
`base = 114` (retail) — i.e. the default split **is** the whole file. The 164 denominator is
therefore the same whether one reads `tasks.json` directly or calls `get_tasks()`.

---

## 5. THE DENOMINATOR CONTROL — requestor and unknown-tool census

The 34 are the externally-authored attacker-competence control (§11.1(b)), so anything that could
silently *add* a task to the 34 inflates the control.

| Domain | actions | distinct `requestor` values seen | action names not in the decorated toolkit |
|---|---|---|---|
| airline | 142 | **`requestor` key absent from all 142** | **none** |
| retail | 550 | **`requestor` key absent from all 550** | **none** |

⚠️ **Read this carefully.** The union of keys present on airline/retail reference actions is
`{action_id, arguments, compare_args, info, name}`. **`requestor` never appears in the raw JSON at
all.** Sierra's `Action.requestor` carries `default="assistant"`, so a *model-validated* action is
`"assistant"`, but a *raw-JSON* action has no such field. A test phrased as *"no action has
`requestor == 'user'`"* over raw JSON is therefore **true for a reason that has nothing to do with
user-requested writes** — it passes over data where the field cannot exist. Whether C3's check is
of that shape is a Phase 2 question; the datum is recorded here, blind.

**Zero unknown tool names** is confirmed: every one of the 692 reference action names resolves to a
decorated tool in its own domain. So the *behaviour* of an unknown name is untested by the data —
it is reachable only by a deliberate defect. That, too, is a Phase 2 question, recorded blind:
**if an unrecognised name defaults to "not a write", the task defaults INTO the 34.**

---

## 6. `reward_basis` CENSUS — all three domains

| Domain | n | census | sums? | `DB` in basis |
|---|---|---|---|---|
| **airline** | 50 | `[DB, COMMUNICATE]` × **50** | ✅ | 50 |
| **retail** | 114 | `[DB, NL_ASSERTION]` × **112**; `[DB]` × **2** | ✅ | 114 |
| **telecom** | 2285 | `[ENV_ASSERTION]` × **2253**; `[ENV_ASSERTION, ACTION]` × **32** | ✅ | **0** |

Every domain's census sums to its own total, and **no telecom task has `DB` in its reward basis** —
which independently confirms §11.1's *structural* reason for excluding telecom (there is no DB-hash
write signal to score) rather than the withdrawn "unsound" claim.

**Sierra's own sentence, checked at source.** §11.1 quotes `docs/evaluation.md:122-126`. At the
pinned SHA those lines are exactly the `db_reward = 1.0 iff …` bullet, quoted complete and
unaltered. ✅

---

## 7. THE T-FP SELECTION, AND WHAT THE SORT IS WORTH

**Under my rule (bytewise on the string id, first 20 per domain):**

- **airline (20 of 26 write tasks):**
  `11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 29, 30, 32, 33, 35, 37`
- **retail (20 of 104 write tasks):**
  `0, 1, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 11, 110, 111, 112, 113, 13, 14, 15`

**Bytewise and numeric select different samples in BOTH domains** — so the ambiguity in §13.4 was
worth exactly this much:

| Domain | bytewise ∆ numeric | ids only-bytewise | ids only-numeric |
|---|---|---|---|
| airline | **4 ids differ** | `35, 37` | `7, 8` |
| retail | **28 ids differ** (14 of 20 replaced) | `100–109, 110–113` (14) | `2,3,4,5,6,7,8,9,16,17,18,19,20,21` |

**The ruling was NEEDED.** Left unruled, two competent readers of §13.4 pick samples that share only
6 of 20 retail tasks. This is a **pre-registered sample of a false-positive block**: had the sort
been settled *after* a number was seen, it would be textbook post-hoc selection. It was not —
`prereg-v1` does not exist and `PROTOCOL.md` is not yet frozen, so disambiguating now is
legitimate, and the only honest verdict is that §13.4 as originally worded was **under-specified**
and had to be closed before the freeze. That is a finding about the *spec*, not about C3.

⚠️ **One structural consequence of bytewise, recorded blind.** The two 20-id lists **collide on the
bare strings `11`, `14` and `15`**. A flat 40-element list of unqualified id strings therefore holds
only **37 distinct values**, and `set()`-ing it silently loses three tasks. The selection is only
well-formed if the ids are carried **domain-qualified** (two keyed lists, or `(domain, id)` pairs).
Phase 2 must check which shape was committed.

⚠️ **A second consequence, for persona 1.** Bytewise makes the retail sample **14/20 drawn from ids
100–113** — the tail of the file, not a spread of it. That is a legitimate consequence of a
pre-registered rule and is *not* a defect, but a reader of the T-FP number deserves to know the
sample is not a random draw. Worth one sentence in `RESULTS.md`.

Also noted: airline contributes **20 of its 26** write tasks (77%) while retail contributes **20 of
104** (19%). The 20/20 stratification is what §13.4 pre-registers; the asymmetry is a property of
the benchmark, not of the selection.

---

## 8. Every number this file asserts, in one block

```
airline: 50 total | 7 empty | 17 read-only | 24 must-not-write | 26 write | 6 WRITE tools
retail : 114 total | 2 empty | 8 read-only | 10 must-not-write | 104 write | 7 WRITE tools
TOTAL  : 164 total | 9 empty | 25 read-only | 34 must-not-write | 130 write
reward_basis airline : (DB, COMMUNICATE) x50
reward_basis retail  : (DB, NL_ASSERTION) x112 ; (DB,) x2
reward_basis telecom : (ENV_ASSERTION,) x2253 ; (ENV_ASSERTION, ACTION) x32 ; DB x0
unknown action names : 0    requestor key present on any action : NO (0 of 692)
T-FP airline (bytewise, 20): 11 12 14 15 16 17 18 19 20 21 22 23 24 25 29 30 32 33 35 37
T-FP retail  (bytewise, 20): 0 1 100 101 102 103 104 105 106 107 108 109 11 110 111 112 113 13 14 15
```
