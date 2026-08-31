"""`whetstone_gate.world` — the seeded mock world, with the competence probe planted.

**What this package is.** A pure, seeded generator: given an integer seed and the constants
`config/protocol.yaml` carries, it returns twelve payments — eight `captured`, three
`authorized`-uncaptured, and `pay_CANARYRECON`, the planted door — plus the merchant's
available balance. `CONTEXT.md` **§8.6a** is the specification and states it exactly;
`tests/goldens/world_seed_2001.json` (**golden 7**, architect-derived independently of any
project code) is the oracle.

**Why the probe lives here rather than at the freeze.** It is a **world-generation
property** (`CONTEXT.md` §10.1, `PROCESS.md` §12.1's C2 row): every seed's world contains
it, every arm sees the identical id and the identical exemption note, and §10.1's actual
requirement is *"no DIFFERENTIAL information across arms"* — which is a property of how the
world is built, not of what is hashed into `HOLES.md`.

**The layout is ruled.** `QUESTIONS.md` **Q-004** ruled OPTION 1 on 2026-08-31: the
subpackages are children of `whetstone_gate/`, so this is `whetstone_gate.world` and never
a top-level `world`. The deciding fact was verified at source — tau2-bench installs a
top-level package named `tau2`, and a sibling layout would collide with the benchmark the
project's external-answer-key claim rests on.

⚠️ **BUILT AND REVIEWABLE, NOT TAGGABLE.** `QUESTIONS.md` **Q-019 (iii)**: *"NO CHUNK WHOSE
NUMBERS DERIVE FROM THIS ALGORITHM MAY BE TAGGED `cN-pass` UNTIL THE OPERATOR HAS CONFIRMED
IT. Build on it and review against it; do not tag."* §8.6a is a Class A architect ruling
made overnight and is explicitly re-opened for the operator before `prereg-v1`.

⚠️ **`QUESTIONS.md` Q-022 is OPEN against this package**: the probe's note text — the string
that *is* the open door — is in neither `CONTEXT.md` §8.6's constants table nor `config/`,
which §8.6's own sentence calls a defect and a review BLOCKER. It is named in one place,
:data:`whetstone_gate.world.spec.PROBE_NOTE_TEXT`, with the one-line remedy.

**Scope.** Generation only. The tool surface, the documented Razorpay rejections, the
idempotency key, the instant-settlement bounds and the S4 in-flight window are **C4's**.
"""

from __future__ import annotations

from .amounts import exact_u, log_uniform_paise, rounding_mode
from .generator import (
    ID_PREFIX,
    STATUS_AUTHORIZED,
    STATUS_CAPTURED,
    Payment,
    World,
    created_at,
    generate,
    generate_world,
    payment_id,
)
from .prng import ALGORITHM, U32_MASK, U32_RANGE, Mulberry32, UnknownGenerator, for_seed
from .spec import (
    PROBE_NOTE_KEY,
    PROBE_NOTE_TEXT,
    WorldConfigError,
    WorldSpec,
    load_world_spec,
)

__all__ = [
    "ALGORITHM",
    "ID_PREFIX",
    "Mulberry32",
    "PROBE_NOTE_KEY",
    "PROBE_NOTE_TEXT",
    "Payment",
    "STATUS_AUTHORIZED",
    "STATUS_CAPTURED",
    "U32_MASK",
    "U32_RANGE",
    "UnknownGenerator",
    "World",
    "WorldConfigError",
    "WorldSpec",
    "created_at",
    "exact_u",
    "for_seed",
    "generate",
    "generate_world",
    "load_world_spec",
    "log_uniform_paise",
    "payment_id",
    "rounding_mode",
]
