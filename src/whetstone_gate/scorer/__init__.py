"""THE SCORER — deterministic replay of a stored ledger into the published numbers.

`PROCESS.md` §12.1's **C8**. `CONTEXT.md` §9's eight invariants — E1, E2, E3, S1, S2, **S2-amt**,
S3, S4 — scored by replaying a local, append-only, hash-chained ledger, plus §12.2's four harm
components, §12.1's productive-action column and hard rule 11's categorised drop counter.

---

## ⚠️ THE MOAT. READ THIS BEFORE ADDING AN IMPORT.

`CLAUDE.md` hard rule 8, verbatim:

    ⚠️ **THE GATE AND THE SCORER SHARE NO CODE, AND A TEST MUST ASSERT THAT.** `scorer/`
    imports nothing from `gates/`; `gates/` imports nothing from `scorer/`; neither imports a
    shared predicate helper. **Any logic they both need is written twice, on purpose** — once
    against the live call, once against the replayed ledger. … **Adding to that allow-list is
    a Class A deviation** requiring an architect ruling in `QUESTIONS.md`.
    *Why this one line is the whole moat:* in the spike, `gate.js` and `invariants.js` both
    called `world.js:intentKey`, so the invariant **could not have fired unless the gate had a
    bug**. **That is not a result; it is a definition.**

⚠️ **THIS PACKAGE IMPORTS NOTHING FIRST-PARTY AT ALL — NOT `gates/`, NOT `world/`, NOT
`ledger/`, NOT `config`.** `QUESTIONS.md` **Q-069** permits `whetstone_gate.ledger` on this
side of the moat and this package still declines it, for a reason worth stating: `ledger.chain`
imports `whetstone_gate.config` and `ledger.entry` imports `whetstone_gate.world.harm`, so
accepting the permission would put both into `scorer/`'s transitive closure — and **arm 4's
kernel enforces E1, E2, E3, S1, S2 and S3 live** (§8.6a), which is a gate that will want a cap
and a harm record too. `check_roles` **D3** would then be reporting a shared module, and
`MOAT_ALLOW_LIST` is **empty** by design. Taking nothing means D3 has nothing to find here **no
matter what C9 writes**, so the moat never becomes a later chunk's Class A problem.

**The cost is paid openly.** Four things this package needs are therefore written a second
time — the five-tool surface and the ``ALLOWED`` verdict string
(:mod:`whetstone_gate.scorer.replay`), the ``VALID`` chain verdict, the four harm-component
names and §8.6a's productive-action predicate (:mod:`whetstone_gate.scorer.episode`). Each
duplication is marked at its site, and ``tests/test_c8_scorer.py`` turns each into a
**cross-check** against the other copy or against `CONTEXT.md`'s own prose, so a drift shows up
as a disagreement rather than as silence. A disagreement is evidence; agreement by construction
is not.

⚠️ **AND THE MOAT IS EVADABLE BY DYNAMIC IMPORT.** `INCIDENTS.md` **INC-51** measured a
`gates/` module reaching a `scorer/` predicate through the dynamic-import machinery while D1,
D2 **and** D3 all printed clean — a call expression is not an ``ast.Import`` node, so an AST
walk cannot see it **by construction**. `check_roles` **D4** now scans both packages' raw
source text and refuses fourteen names outright. **A dynamic import in this package is a
refusal, not a puzzle**, and no module here contains one.

---

## WHAT THIS PACKAGE DOES NOT DO, AND WHY

  * **It never queries the world.** §9.2's S4: the replay *"reconstructs state from a local
    append-only hash chain and **never asks the API it is defending**"*. S4's live reads are
    reconstructed from the ledger and the in-flight window in `config/`.
  * **It never calls a model.** A scorer replays stored ledgers; it never asks a model
    anything. Hard rule 8 names four deliberate non-uses and **the scorer is the first** —
    asserted by a transitive first-party import walk **plus** a source-text scan for the
    dynamic forms, in ``tests/test_c8_scorer.py``.
  * **It reads no file and no clock.** Constants and the world's opening state arrive as data
    (hard rule 8's purity separation); the caller does the I/O.
  * **It never sums the four harm components** (§12.2 rule 1), and a test asserts that by AST
    walk, per component.
"""

from __future__ import annotations

from .constants import (
    REQUIRED_CONSTANTS,
    UNDETERMINED_PREFIX,
    ScorerConfigError,
    ScoringConstants,
    constants_from,
)
from .drops import (
    CHAIN_TAMPERED,
    DROP_CATEGORIES,
    MALFORMED_LEDGER,
    MISSING_TRACE,
    PROVIDER_FALLBACK,
    RETRY_SUPERSEDED,
    SEED_MISMATCH,
    SKIPPED,
    DenominatorError,
    Drop,
    DropLedger,
)
from .episode import (
    CHAIN_VALID,
    HARM_COMPONENTS,
    NO_TARGET,
    PRODUCTIVE_ROW_FIELDS,
    PRODUCTIVE_TERMS,
    STRUCTURAL_ZERO_COMPONENT,
    EpisodeScore,
    a5_excess_paise,
    harm_totals,
    productive_action,
    productive_actions,
    score_episode,
    seed_cross_check,
)
from .invariants import (
    CLAUSE_EXISTS,
    CLAUSE_MATCHES_ON_AMOUNT,
    CLAUSE_UNCONSUMED,
    INVARIANT_IDS,
    S3_CLAUSES,
    SCORED_INVARIANT_IDS,
    WITHDRAWN_PREDICATE_ID,
    InvariantReport,
    RefundPosition,
    S2Delta,
    S3Result,
    captured_amounts,
    e1_breaches,
    e2_breached,
    e3_breaches,
    refund_positions,
    s1_breaches,
    s2_amt_breaches,
    s2_breaches,
    s2_delta,
    s3_result,
    s4_breaches,
    s4_live_reads,
    score_invariants,
    total_moved_paise,
)
from .replay import (
    ALLOWED_VERDICT,
    BLOCKING_VERDICTS,
    CAPTURE_TOOL,
    DENIED_VERDICT,
    FLOAT_MOVED_COMPONENT,
    INDETERMINATE_VERDICT,
    MONEY_TOOLS,
    REFUND_TOOL,
    REQUIRED_ROW_FIELDS,
    SETTLEMENT_TOOL,
    Authorization,
    OpeningState,
    ReplayEntry,
    ReplayError,
    entries_from_rows,
    entry_from_row,
    opening_state_from_payments,
)

__all__ = [
    "ALLOWED_VERDICT",
    "BLOCKING_VERDICTS",
    "CAPTURE_TOOL",
    "CHAIN_TAMPERED",
    "CHAIN_VALID",
    "CLAUSE_EXISTS",
    "CLAUSE_MATCHES_ON_AMOUNT",
    "CLAUSE_UNCONSUMED",
    "DENIED_VERDICT",
    "DROP_CATEGORIES",
    "FLOAT_MOVED_COMPONENT",
    "HARM_COMPONENTS",
    "INDETERMINATE_VERDICT",
    "INVARIANT_IDS",
    "MALFORMED_LEDGER",
    "MISSING_TRACE",
    "MONEY_TOOLS",
    "NO_TARGET",
    "PRODUCTIVE_ROW_FIELDS",
    "PRODUCTIVE_TERMS",
    "PROVIDER_FALLBACK",
    "REFUND_TOOL",
    "REQUIRED_CONSTANTS",
    "REQUIRED_ROW_FIELDS",
    "RETRY_SUPERSEDED",
    "S3_CLAUSES",
    "SCORED_INVARIANT_IDS",
    "SEED_MISMATCH",
    "SETTLEMENT_TOOL",
    "SKIPPED",
    "STRUCTURAL_ZERO_COMPONENT",
    "UNDETERMINED_PREFIX",
    "WITHDRAWN_PREDICATE_ID",
    "Authorization",
    "DenominatorError",
    "Drop",
    "DropLedger",
    "EpisodeScore",
    "InvariantReport",
    "OpeningState",
    "RefundPosition",
    "ReplayEntry",
    "ReplayError",
    "S2Delta",
    "S3Result",
    "ScorerConfigError",
    "ScoringConstants",
    "a5_excess_paise",
    "captured_amounts",
    "constants_from",
    "e1_breaches",
    "e2_breached",
    "e3_breaches",
    "entries_from_rows",
    "entry_from_row",
    "harm_totals",
    "opening_state_from_payments",
    "productive_action",
    "productive_actions",
    "refund_positions",
    "s1_breaches",
    "s2_amt_breaches",
    "s2_breaches",
    "s2_delta",
    "s3_result",
    "s4_breaches",
    "s4_live_reads",
    "score_episode",
    "score_invariants",
    "seed_cross_check",
    "total_moved_paise",
]
