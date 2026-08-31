"""The world's constants, resolved from `config/`. **Every one of them, as of 2026-08-31.**

**Purity separation, hard rule 8.** Everything in `whetstone_gate.world` that computes is a
pure function of data handed to it. This module is the **thin outer shell** that does the
one piece of I/O the package needs: it reads `config/protocol.yaml` through the project's
single loader and returns a frozen :class:`WorldSpec`. :func:`~whetstone_gate.world.generate.generate`
then takes that spec as data and touches no file, no clock, no network and no ambient
randomness.

**Every value below is a row of `CONTEXT.md` §8.6's constants table and a key of
`config/protocol.yaml`** — §8.6a states the algorithm, §8.6 tabulates its constants, and
`config/` is what the experiment actually reads. Nothing here carries a default: the
loader raises on a missing, blank or `TODO_` value, which is hard rule 9's *"a missing
value is a hard refusal, never a silent fallback."*

⚠️ **THERE USED TO BE ONE EXCEPTION, AND ITS HISTORY IS KEPT HERE RATHER THAN TIDIED AWAY.**
When C2 BUILD (`f0c50283`) wrote this module on 2026-08-31, **the probe's note text was in
neither §8.6's constants table nor `config/`** — which §8.6's own sentence calls *"a defect,
and finding one is a review BLOCKER"* — so the value could not be read like the others. C2's
fence named `config/`, `CONTEXT.md` and `spec_constants.py` under **NOT**, so rather than
write into a frozen artefact from outside its fence, it **named the string here**, in one
place, in a nine-line comment carrying the exact remedy, as module constants
``PROBE_NOTE_KEY`` and ``PROBE_NOTE_TEXT``.

**It was raised as `QUESTIONS.md` Q-022, UPHELD by the architect, and the remedy landed on
2026-08-31 in session `921cfaa4`** — before `prereg-v1`, after which `config/` is frozen even
when wrong. `config/protocol.yaml` now carries `probe.notes`, §8.6 carries the **probe note**
row, and `spec_constants.py` carries a STRICT registry row on the quoted forms. **The two
module constants are therefore GONE and both values are read below through
:meth:`~whetstone_gate.config.Config.require`, like every other value** — which is exactly
what C2's remedy block said would happen on that landing.

⚠️ **THE READS BELOW ARE NEW, AND THIS PARAGRAPH IS WHY THAT IS SAID OUT LOUD.** A reader who
meets `probe_note_key=protocol.require("probe.notes")` with no history would reasonably assume
the value was always in `config/` and that the freeze always covered it. **It was not, and it
did not.** This is the single most load-bearing string in the world — policy clause **P7**
matches on it, so the gate's exemption, the arm-4 kernel's, **CANARY-A**'s breach predicate and
the attacker's whole discrimination task all key off these words, and its near-neighbour is the
deliberate decoy at note-template index 4 (*"standard limits apply"*, which grants nothing).
**It sat outside the frozen set for the length of one chunk, and that is a fact about this
project's record, not a footnote.**
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import config as cfg


def read_probe_note(protocol: cfg.Config) -> tuple[str, str]:
    """The probe's ``(key, text)``, read from ``probe.notes`` in `config/protocol.yaml`.

    **The one place in this package that knows `probe.notes`' shape**, so the module
    attributes and :func:`load_world_spec` cannot drift apart.

    `config/` writes it as a one-entry mapping, matching the form `CONTEXT.md` §10.1 and
    §8.6a both use — ``notes: {reconciliation: "..."}``. It is **unpacked rather than
    indexed by a literal key**: a literal ``"reconciliation"`` here would be a second copy
    of a `config/` value living in source, which is precisely what **Q-022** was about.

    A mapping of any other size is a `config/` defect and is **refused, not repaired**.
    §10.1 fixes the probe's note as exactly one annotation, and clause **P7** matches on
    its text — so an extra or a missing annotation changes whether the door is open.
    """
    notes = protocol.require("probe.notes")
    if not isinstance(notes, dict) or len(notes) != 1:
        raise WorldConfigError(
            f"probe.notes must be a mapping of exactly one annotation; `config/` gives "
            f"{notes!r}. CONTEXT.md §10.1 fixes the probe's note as exactly one entry, and "
            f"policy clause P7 matches on its TEXT — so an extra or a missing annotation "
            f"changes whether the open door is open, and arm 4 would be VOID BY "
            f"CONSTRUCTION with every test still passing."
        )
    (key, text), = notes.items()
    return key, text


#: ⚠️ **THESE TWO NAMES ARE RESOLVED THROUGH THE LOADER, NOT WRITTEN HERE.** They were
#: module-level string literals when C2 BUILD wrote this file, because the value was in
#: neither `CONTEXT.md` §8.6's constants table nor `config/` — see the module docstring and
#: `QUESTIONS.md` **Q-022**. Since the Q-022 remedy landed (session `921cfaa4`, 2026-08-31)
#: they read `probe.notes` from `config/protocol.yaml` like every other value in this
#: module, and **`git log -p` on this file shows the literals being deleted rather than
#: their ever having been read from `config/`.**
#:
#: **Resolved lazily, and the reason is `whetstone_gate.config.load`'s own:** *"Not cached:
#: these files are tiny, and a cache would let a stale read outlive an edit during a long
#: run."* A module-level eager read would be exactly that stale cache, frozen at import.
#: PEP 562 keeps the attribute names that `whetstone_gate.world.__init__` re-exports and
#: that `tests/test_c2_world.py` asserts against, while making each access a fresh read.
_LOADER_RESOLVED = {
    "PROBE_NOTE_KEY": 0,
    "PROBE_NOTE_TEXT": 1,
}


def __getattr__(name: str) -> str:
    """PEP 562: resolve ``PROBE_NOTE_KEY`` / ``PROBE_NOTE_TEXT`` from `config/` on access."""
    try:
        index = _LOADER_RESOLVED[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
    return read_probe_note(cfg.load("protocol"))[index]


class WorldConfigError(RuntimeError):
    """`config/`'s world block is internally inconsistent.

    Raised rather than repaired. Every check below compares two values `config/` already
    carries; a disagreement between them means the pre-registration says two different
    things about the same world, and generating *something* from it would publish a number
    nobody registered.
    """


@dataclass(frozen=True)
class WorldSpec:
    """Every constant `whetstone_gate.world` needs, already resolved. Immutable.

    Built only by :func:`load_world_spec`. Passing it around rather than re-reading
    `config/` is what lets the generator be a pure function — and what lets a test drive
    the generator with a deliberately altered spec without touching a frozen artefact.
    """

    prng: str
    payments_per_seed: int
    draws_per_seed: int
    probe_index: int
    captured_count: int
    authorized_count: int
    probe_count: int
    amount_min_paise: int
    amount_max_paise: int
    merchant_available_balance_paise: int
    payment_id_salt: str
    payment_id_hash_algorithm: str
    payment_id_hex_chars: int
    created_at_base_epoch: int
    created_at_step_seconds: int
    currency: str
    decimal_context_precision: int
    note_template_assignment: str
    note_templates: tuple[tuple[str, str], ...]
    rounding: str
    probe_payment_id: str
    probe_payment_amount_paise: int
    probe_note_key: str
    probe_note_text: str

    def __post_init__(self) -> None:
        self._check_consistent()

    # -- the checks, each comparing two values `config/` already holds --------------------

    def _check_consistent(self) -> None:
        parts = self.captured_count + self.authorized_count + self.probe_count
        if parts != self.payments_per_seed:
            raise WorldConfigError(
                f"world.split sums to {parts} but world.payments_per_seed is "
                f"{self.payments_per_seed}. CONTEXT.md §8.6a makes the split EXACT BY "
                f"CONSTRUCTION; a mismatch here would make it exact by accident."
            )

        expected_draws = self.payments_per_seed - self.probe_count
        if self.draws_per_seed != expected_draws:
            raise WorldConfigError(
                f"world.prng_draws_per_seed is {self.draws_per_seed}, but one draw per "
                f"ORDINARY payment is {expected_draws}. §8.6a: 'THE PROBE CONSUMES NO "
                f"DRAW … a twelfth draw would make the probe's presence perturb the "
                f"ordinary payments.'"
            )

        ordinary = self.captured_count + self.authorized_count
        if self.probe_index != ordinary:
            raise WorldConfigError(
                f"world.probe_index is {self.probe_index}, but the ordinary payments "
                f"occupy indices 0..{ordinary - 1}. §8.6a assigns status POSITIONALLY, so "
                f"the probe is the index immediately after the last ordinary payment."
            )

        assignment = f"index_mod_{len(self.note_templates)}"
        if self.note_template_assignment != assignment:
            raise WorldConfigError(
                f"world.note_template_assignment is "
                f"{self.note_template_assignment!r} but the pool holds "
                f"{len(self.note_templates)} templates, which is {assignment!r}. §8.6a "
                f"assigns by `index mod <pool size>`; the two must agree or some template "
                f"is unreachable — and template index 4 is the DELIBERATE DECOY without "
                f"which CANARY-A measures reading rather than competence."
            )

        if not 0 < self.payment_id_hex_chars:
            raise WorldConfigError(
                f"world.payment_id_hash.hex_chars is {self.payment_id_hex_chars}; an id "
                f"truncated to nothing is not an id."
            )


def load_world_spec(protocol: cfg.Config | None = None) -> WorldSpec:
    """Read the world's constants from `config/protocol.yaml`. **The only I/O in the package.**

    ``protocol`` may be supplied so a caller that has already loaded the file does not read
    it twice. It is not a defaulting hook: the values still come from `config/`, and every
    read goes through :meth:`whetstone_gate.config.Config.require`, which has no
    ``default=`` parameter to abuse.
    """
    protocol = protocol if protocol is not None else cfg.load("protocol")

    templates = tuple(
        (entry["key"], entry["text"]) for entry in protocol.require("world.note_templates")
    )

    probe_note_key, probe_note_text = read_probe_note(protocol)

    return WorldSpec(
        prng=protocol.require("world.prng"),
        payments_per_seed=protocol.require("world.payments_per_seed"),
        draws_per_seed=protocol.require("world.prng_draws_per_seed"),
        probe_index=protocol.require("world.probe_index"),
        captured_count=protocol.require("world.split.captured"),
        authorized_count=protocol.require("world.split.authorized_uncaptured"),
        probe_count=protocol.require("world.split.probe"),
        amount_min_paise=protocol.require("world.amount_min_paise"),
        amount_max_paise=protocol.require("world.amount_max_paise"),
        merchant_available_balance_paise=protocol.require(
            "world.merchant_available_balance_paise"
        ),
        payment_id_salt=protocol.require("world.payment_id_salt"),
        payment_id_hash_algorithm=protocol.require("world.payment_id_hash.algorithm"),
        payment_id_hex_chars=protocol.require("world.payment_id_hash.hex_chars"),
        created_at_base_epoch=protocol.require("world.created_at_base_epoch"),
        created_at_step_seconds=protocol.require("world.created_at_step_seconds"),
        currency=protocol.require("world.currency"),
        decimal_context_precision=protocol.require("world.decimal_context_precision"),
        note_template_assignment=protocol.require("world.note_template_assignment"),
        note_templates=templates,
        rounding=protocol.require("money.rounding"),
        probe_payment_id=protocol.require("probe.payment_id"),
        probe_payment_amount_paise=protocol.require("probe.payment_amount_paise"),
        probe_note_key=probe_note_key,
        probe_note_text=probe_note_text,
    )
