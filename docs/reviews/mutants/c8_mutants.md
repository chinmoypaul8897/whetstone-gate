# `c8_mutants.md` — C8 REVIEW 1 (`07c3687f`), the mutant table

**Harness:** `docs/reviews/mutants/c8_mutation_harness.py` · **Raw:** `docs/reviews/mutants/c8_mutants.json`

**RUN VALID: `True`** — all three controls green.


⚠️ **HOW A KILL IS MEASURED, AND WHY IT IS IDS AND NOT COUNTS.** A clone has no `vendor/`, so
`pip install -e vendor/tau2-bench` has never run there and the full suite cannot collect. A
mutant is **KILLED** if it makes at least one *test id* fail that did not fail in the clean
baseline. Comparing ids rather than counts means a collection error that changes the total
cannot masquerade as a kill (`INC-58`).

**The clean baseline in the clone held 10 failing ids** — 3 in `tests/test_c8_scorer.py`
(F9's S3 cell, and the two derived counts `Q-103`/`INC-83` names) and 7 in
`tests/test_repo_invariants.py`, which need a `.git` the clone does not have. Every verdict
below is *relative to that baseline*.

**The five guards, each answering a recorded incident:**

| guard | the incident it answers | result |
|---|---|---|
| restore by **writing the original bytes**, never `git checkout --` | `INC-57` | post-restore control **green** |
| an unreadable run is `UNREADABLE`, never `SURVIVED` | `INC-58` | 0 unreadable |
| `env=` passed to **`subprocess.run` itself**, provenance printed from the walking process | `INC-64`, `INC-69` | all paths inside the clone, before **and** after |
| the clone's `src` forced to the front of `PYTHONPATH` | `OF-139` | `whetstone_gate.__file__` and `config.repo_root()` both inside the clone |
| **a positive control that MUST die**, plus two no-ops that must survive | `OF-159` | `M00` KILLED, `M01`/`M25` SURVIVED |

---

## The table

| id | owned property | file | what it breaks | verdict | OWNED / NOT-OWNED |
|---|---|---|---|---|---|
| **M00** | CONTROL | `invariants.py` | POSITIVE CONTROL - E1's strict > flipped to >=. MUST DIE. | **KILLED** | killed — n/a |
| **M01** | NO-OP | `invariants.py` | NO-OP CONTROL - a comment reworded. MUST SURVIVE. | **SURVIVED** | control |
| **M02** | OP-01 E1 | `invariants.py` | E1 scored over ISSUED rather than EXECUTED actions | **SURVIVED** | NOT-OWNED (sub-unit of OP-01) |
| **M03** | OP-02 E2 | `invariants.py` | E2's STRICT comparison flipped to >= | **SURVIVED** | NOT-OWNED (sub-unit of OP-02) |
| **M04** | OP-03 E3 | `invariants.py` | E3's >= boundary flipped to >, so an action at EXACTLY the exhausted cap is clean | **KILLED** | killed — n/a |
| **M05** | OP-04 S1 | `invariants.py` | S1's <= flipped to <, so a fully-refunded payment breaches | **KILLED** | killed — n/a |
| **M06** | OP-04 S1 | `invariants.py` | INC-78(a) again: the captured amount is no longer the one AT THIS CALL | **KILLED** | killed — n/a |
| **M07** | OP-04 S1 | `replay.py` | INC-78(b) again: a KNOWN ZERO captured amount dropped as falsy | **KILLED** | killed — n/a |
| **M08** | OP-05 S2 | `invariants.py` | S2/S2-amt scored at EXECUTION rather than at ISSUE - Q-027 MOVE 3 undone | **KILLED** | killed — n/a |
| **M09** | OP-25 S2 | `invariants.py` | S2's NON-EMPTY clause weakened: an EMPTY STRING becomes a shared key (INC-04) | **SURVIVED** | NOT-OWNED (sub-unit of OP-25) |
| **M10** | OP-05 S2 | `invariants.py` | S2's SAME-PAYMENT half dropped - one receipt across two payments now collides | **SURVIVED** | NOT-OWNED (sub-unit of OP-05) |
| **M11** | OP-06 S2-amt | `invariants.py` | S2-amt's payment_id term dropped from the withdrawn triple | **KILLED** | killed — n/a |
| **M12** | OP-07 S3 | `invariants.py` | S3's `exists` clause no longer fires on an ABSENT authorization | **KILLED** | killed — n/a |
| **M13** | OP-07 S3 | `invariants.py` | S3: a REFUSED capture now consumes its authorization (Q-097's `only executed` undone) | **SURVIVED** | NOT-OWNED (sub-unit of OP-07) |
| **M14** | OP-08 S4 | `invariants.py` | S4 := S1 - THE STALE-READ CLAUSE DROPPED ENTIRELY. The moat's own predicate. | **KILLED** | killed — n/a |
| **M15** | OP-08 S4 | `invariants.py` | S4's window width HARDCODED to 5 instead of config/'s value (hard rule 9) | **KILLED** | killed — n/a |
| **M16** | OP-05 S2 | `replay.py` | INDETERMINATE now counts as ISSUED - S9.3's 'blocks exactly as hard as DENIED' undone | **SURVIVED** | **OWNED — OP-10** |
| **M17** | OP-19 drops | `drops.py` | the denominator identity can no longer fail - hard rule 11's whole point | **KILLED** | killed — n/a |
| **M18** | OP-19 drops | `drops.py` | an UNDECLARED drop category is accepted - silent shrinkage under a new name | **KILLED** | killed — n/a |
| **M19** | OP-17 config | `constants.py` | hard rule 9: an ABSENT required constant no longer refuses | **KILLED** | killed — n/a |
| **M20** | OP-17 config | `constants.py` | hard rule 9: a TODO_ sentinel no longer refuses - an undecided constant would score | **KILLED** | killed — n/a |
| **M21** | OP-23 seed | `episode.py` | Q-071's seed cross-check can no longer fail - a wrong seed scores silently | **KILLED** | killed — n/a |
| **M22** | OP-04/OP-19 | `replay.py` | Q-062/INC-67: a row missing `executed` is no longer a refusal | **KILLED** | killed — n/a |
| **M23** | OP-15 replay | `episode.py` | a ledger whose hash chain did NOT verify is scored anyway | **KILLED** | killed — n/a |
| **M24** | OP-27 §12.1 | `invariants.py` | S2-amt REMOVED from INVARIANT_IDS - i.e. S12.1's column note APPLIED. If this SURVIVES, no test pins which set feeds S12.1's two published columns. | **SURVIVED** | **OWNED — OP-27** |
| **M25** | NO-OP | `replay.py` | NO-OP #2 - a comment inserted in replay.py. MUST SURVIVE. | **SURVIVED** | control |
| **M26** | OP-10 INDET | `episode.py` | a DETECTED (tampered) chain is now treated as VALID and scored | **KILLED** | killed — n/a |
| **M27** | OP-14 delta | `invariants.py` | the S2/S2-amt delta loses its BLIND direction - the finding becomes one-sided | **KILLED** | killed — n/a |
| **M28** | OP-16 paise | `invariants.py` | the episode aggregate computed through a BINARY FLOAT (PROCESS.md S5.1) | **KILLED** | killed — n/a |

**29 mutants · 20 KILLED · 9 SURVIVED** (2 of the survivors are the required no-op controls, so **7 real survivors**).
