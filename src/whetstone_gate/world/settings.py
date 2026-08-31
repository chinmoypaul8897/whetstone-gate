"""C4's constants, resolved from `config/`. **Beside `spec.py`, never inside it.**

**Why a second spec object rather than more fields on :class:`~whetstone_gate.world.spec.WorldSpec`.**
`spec.py` and the generator are **C2's**, and C2 is tagged `c2-pass`. This session's fence
says *"EXTEND the existing package — C2 built the generator and it is TAGGED `c2-pass`; you
add semantics beside it and you do not rewrite it"*, and `tests/test_c2_world.py` drives
`WorldSpec` directly, including with deliberately altered specs. Widening that dataclass
would put C4's constants inside C2's reviewed surface for no benefit — the two objects are
loaded from the same `config/protocol.yaml` through the same one loader, and
:func:`load_semantics_spec` accepts an already-loaded :class:`~whetstone_gate.config.Config`
so the file is still read once.

**Every value below is a row of `CONTEXT.md` §8.6's constants table and a key of
`config/protocol.yaml`.** Nothing here carries a default: the loader raises on a missing,
blank or `TODO_` value, which is hard rule 9's *"a missing value is a hard refusal, never a
silent fallback"*.

⚠️ **THE SIX A4 VALUES ARE THE ONES C1'S REVIEW FAILED ON**, and they are read here rather
than known. `QUESTIONS.md` **Q-028** (RULED, APPROVED BY THE OPERATOR) and **Q-029** (RULED,
Class A) placed them; `INCIDENTS.md` **INC-18** records their absence. `config/protocol.yaml`'s
own header states the rule this module obeys: *"C4 must read every ceiling it enforces, and a
`[Razorpay-defined]` figure hardcoded in source is the SAME hard-rule-9 defect as an
author-chosen one."*

⚠️ **`within_banking_hours` IS A CONSTANT AND NEVER A CLOCK READ**, and this module is where
that would go wrong if it were going to. Hard rule 8 forbids a clock in core logic, C1's
reviewer raised exactly this against RS-17 (`F-R9`), and
`tests/test_c2_world.py::test_the_world_reads_no_clock_and_draws_no_ambient_randomness`
scans **every** module of this package — including this one — for `time`, `datetime`,
`calendar` and `zoneinfo`. `false` means every episode sits **outside** banking hours, which
makes RS-17's ₹2,00,000 IMPS cap **operative in every episode** — the tighter reading, so a
wrong choice here can only make this project's escape numbers smaller.

⚠️ **THE IN-FLIGHT WINDOW IS COUNTED IN TOOL CALLS, NEVER IN TIME**, which is why its field
is named :attr:`SemanticsSpec.in_flight_window_calls` rather than anything ending in
`seconds`. `CONTEXT.md` §9.2 fixes the unit — *"a window of **2 subsequent tool calls**"* —
and §8.6 hashes the width into `HOLES.md` at `probe-v1`.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import config as cfg


class SemanticsConfigError(RuntimeError):
    """`config/`'s C4 block is internally inconsistent.

    Raised rather than repaired, for :class:`~whetstone_gate.world.spec.WorldConfigError`'s
    reason: every check below compares two values `config/` already carries, and a
    disagreement between them means the pre-registration says two different things about
    the same world.
    """


@dataclass(frozen=True)
class SemanticsSpec:
    """Every constant the world's Razorpay boundary needs, already resolved. Immutable."""

    # -- money (§8.6, `money.*`) --------------------------------------------------------
    settlement_fee_basis_points: int
    rounding: str
    per_action_cap_paise: int

    # -- the S4 in-flight window (§8.6, §9.2, `invariants.*`) ---------------------------
    in_flight_window_calls: int

    # -- A4's six configured values (§8.6, Q-028, Q-029, `world.instant_settlement.*`) ---
    daily_withdrawable_limit_paise: int
    max_attempts_per_day: int
    attempt_counter_includes_rejected: bool
    within_banking_hours: bool
    imps_cap_paise: int
    max_per_settlement_paise: int

    # -- the world the boundary operates on (§8.6a, `world.*`, `probe.*`) ---------------
    currency: str
    opening_balance_paise: int
    probe_payment_id: str

    def __post_init__(self) -> None:
        self._check_consistent()

    def _check_consistent(self) -> None:
        """Each check compares two values `config/` already holds."""
        if self.in_flight_window_calls < 1:
            raise SemanticsConfigError(
                f"invariants.s4_in_flight_window_width is {self.in_flight_window_calls}; a "
                f"window of zero subsequent tool calls is no window, and invariant S4 — the "
                f"one CONTEXT.md §9.2 calls 'the genuinely un-representable one' — would be "
                f"UNFIRABLE while every test still passed."
            )

        if self.max_attempts_per_day < 1:
            raise SemanticsConfigError(
                f"world.instant_settlement.max_attempts_per_day is "
                f"{self.max_attempts_per_day}; no instant settlement could ever execute, and "
                f"RS-19 would fire on the first attempt rather than on the exhausting one."
            )

        ceilings = (
            self.imps_cap_paise,
            self.daily_withdrawable_limit_paise,
            self.opening_balance_paise,
            self.max_per_settlement_paise,
        )
        if list(ceilings) != sorted(ceilings) or len(set(ceilings)) != len(ceilings):
            raise SemanticsConfigError(
                f"A4's four amount ceilings are {ceilings}, which is not a strictly "
                f"ascending sequence. `docs/reviews/REVIEW_C1_2.md` §2.3 establishes that "
                f"they are STRICTLY NESTED, and `semantics.py`'s descending check order "
                f"depends on it: with two ceilings equal or out of order, one of RS-15, "
                f"RS-16, RS-17 or RS-18 has an EMPTY firing band and can never fire, which "
                f"makes C4's done-when unsatisfiable for that row while the self-test still "
                f"reports a number. This is the assumption stated as a refusal rather than "
                f"as a comment."
            )


def load_semantics_spec(protocol: cfg.Config | None = None) -> SemanticsSpec:
    """Read C4's constants from `config/protocol.yaml`. **The only I/O in this module.**

    ``protocol`` may be supplied so a caller that has already loaded the file does not read
    it twice. It is not a defaulting hook: every read goes through
    :meth:`whetstone_gate.config.Config.require`, which has no ``default=`` parameter to
    abuse.
    """
    protocol = protocol if protocol is not None else cfg.load("protocol")
    settlement = "world.instant_settlement."

    return SemanticsSpec(
        settlement_fee_basis_points=protocol.require("money.settlement_fee_basis_points"),
        rounding=protocol.require("money.rounding"),
        per_action_cap_paise=protocol.require("money.per_action_cap_paise"),
        in_flight_window_calls=protocol.require("invariants.s4_in_flight_window_width"),
        daily_withdrawable_limit_paise=protocol.require(
            settlement + "daily_withdrawable_limit_paise"
        ),
        max_attempts_per_day=protocol.require(settlement + "max_attempts_per_day"),
        attempt_counter_includes_rejected=protocol.require(
            settlement + "attempt_counter_includes_rejected"
        ),
        within_banking_hours=protocol.require(settlement + "within_banking_hours"),
        imps_cap_paise=protocol.require(
            settlement + "imps_outside_banking_hours_cap_paise"
        ),
        max_per_settlement_paise=protocol.require(settlement + "max_per_settlement_paise"),
        currency=protocol.require("world.currency"),
        opening_balance_paise=protocol.require("world.merchant_available_balance_paise"),
        probe_payment_id=protocol.require("probe.payment_id"),
    )
