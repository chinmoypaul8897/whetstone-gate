"""**THE NINE LANES, THEIR LIMITS, AND THE RESERVATIONS. `PROCESS.md` §8.**

`CONTEXT.md` §13.3, verbatim, and it is the sentence that makes this a scheduler rather than a
thread pool:

    **Concurrency here means LANES, not threads.** One in-flight episode per model+provider
    lane. Available lanes: `gemma-26b`, `gemma-31b`, `flash-lite-3.1`, `flash-lite-3.5`,
    `qwen-27b`, `gpt-oss-20b`, `gpt-oss-120b`, `compound`, `compound-mini` = **9 lanes**. The
    runner schedules episodes onto lanes, never onto a thread pool.

**A thin outer shell** (hard rule 8): it reads `config/lanes.yaml` through the one loader and
returns values. It decides nothing that :mod:`.budget` or :mod:`.buckets` decides.

--------------------------------------------------------------------------------------
⚠️ LANE RESERVATION IS ENFORCED, NOT DOCUMENTED
--------------------------------------------------------------------------------------

`PROCESS.md` §8:

    **LANE RESERVATION.** The **reference-attacker** lanes (Gemma 4 26B / 31B) and the
    **gate-judge** lanes are reserved for the sweep from 31 August. **No build session may
    spend on them.** Ladder lanes (`gpt-oss-20b`, `qwen3.8-27b`, `gpt-oss-120b`) are reserved
    for the ladder windows.

`config/lanes.yaml` carries ``reserved_from`` on every lane — a date, or an explicit ``null``
meaning *"this lane carries no reservation"*, which `config.py`'s ``NULL_IS_A_VALUE`` records
as a **determined** value rather than a missing one. :func:`reserved_lanes` reads it and
:func:`refuse_reserved` is the refusal.

⚠️ **THE REFUSAL IS THE DEFAULT AND IT TAKES AN EXPLICIT SANCTION TO LIFT.** :func:`refuse_reserved`
requires the caller to name the lanes its prompt sanctioned, one by one. There is no
``allow_all`` and no environment variable: a session that has not been given a lane cannot
spend on it by forgetting to pass an argument, only by passing a wrong one — and a wrong one
is visible in a diff. ⚠️ **A REFUSED LANE IS COUNTED, NOT SWALLOWED**: the episodes that did
not run against it are recorded under :data:`.episodes.LANE_RESERVED` and printed, because
hard rule 11 counts *skipped cases* too.

⚠️ **THIS SESSION SPENT NOTHING.** C11's build prompt reads *"TOKEN SPEND: NONE. ZERO PROVIDER
MODEL CALLS. YOU BUILD THE RUNNER AND YOU DO NOT RUN IT."* Every lane is reserved; the pilot
and the calibration are single-shot and the operator's.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import config as cfg


class LaneError(RuntimeError):
    """A lane is missing, malformed, or reserved. Always a refusal, never a default."""


class LaneReserved(LaneError):
    """A run tried to dispatch onto a lane its prompt did not sanction. `PROCESS.md` §8."""


@dataclass(frozen=True)
class Lane:
    """One model+provider lane and its four limits.

    ⚠️ ``tpd`` is ``int | None`` and ``None`` means **"no such limit exists"**, not
    *"unknown"*. `config/lanes.yaml`'s own header: Google's free tier shows no daily token cap
    at all, only requests/day and tokens/minute. Treating that ``None`` as zero would park
    every Google lane forever; treating it as *unknown* would let a runner guess one.
    """

    name: str
    provider: str
    api_model_id: str
    rpm: int
    tpm: int
    rpd: int
    tpd: int | None
    reserved_from: str | None
    role: str

    @property
    def is_reserved(self) -> bool:
        return self.reserved_from is not None


def _require(record: dict, field: str, lane_name: str) -> object:
    if field not in record:
        raise LaneError(
            f"lane {lane_name!r} states no {field!r}. config/lanes.yaml is a pre-registration "
            f"artefact and hard rule 9 makes a missing required value a hard refusal, never a "
            f"silent fallback — a lane with a guessed limit is a lane that overspends"
        )
    return record[field]


def load_lanes() -> dict[str, Lane]:
    """Every lane in `config/lanes.yaml`, keyed by name. **Through the one loader.**"""
    records = cfg.load("lanes").require("lanes")
    lanes: dict[str, Lane] = {}
    for record in records:
        name = str(_require(record, "name", "<unnamed>"))
        if name in lanes:
            raise LaneError(f"config/lanes.yaml declares lane {name!r} twice")
        tpd = _require(record, "tpd", name)
        lanes[name] = Lane(
            name=name,
            provider=str(_require(record, "provider", name)),
            api_model_id=str(_require(record, "api_model_id", name)),
            rpm=int(_require(record, "rpm", name)),
            tpm=int(_require(record, "tpm", name)),
            rpd=int(_require(record, "rpd", name)),
            tpd=None if tpd is None else int(tpd),
            reserved_from=(
                None
                if _require(record, "reserved_from", name) is None
                else str(record["reserved_from"])
            ),
            role=str(_require(record, "role", name)),
        )
    return lanes


def reserved_lanes() -> dict[str, str]:
    """``{lane name: the date it is reserved from}`` for every reserved lane."""
    return {
        lane.name: lane.reserved_from
        for lane in load_lanes().values()
        if lane.reserved_from is not None
    }


def refuse_reserved(lane_name: str, *, sanctioned: frozenset[str]) -> None:
    """Refuse unless ``lane_name`` is reserved-free **or** explicitly sanctioned.

    ``sanctioned`` is the set of lane names this run's prompt named, verbatim. There is no
    default value for it and no wildcard: `PROCESS.md` §8 says *"No token spend unless your
    prompt explicitly sanctions it, naming the lane, a call ceiling AND a token ceiling, and a
    window"*, and a wildcard is how *"naming the lane"* stops being a constraint.
    """
    lanes = load_lanes()
    if lane_name not in lanes:
        raise LaneError(
            f"{lane_name!r} is not a lane. config/lanes.yaml declares {sorted(lanes)}; a lane "
            f"this project has not pre-registered is not one it may spend on"
        )
    lane = lanes[lane_name]
    if lane.is_reserved and lane_name not in sanctioned:
        raise LaneReserved(
            f"lane {lane_name!r} is RESERVED from {lane.reserved_from} (PROCESS.md S8) and "
            f"this run's sanctioned set is {sorted(sanctioned) or '[] - nothing sanctioned'}. "
            f"Its role: {lane.role}. No build session may spend on a reserved lane; the "
            f"reference-attacker and gate-judge lanes are held for the sweep and the ladder "
            f"lanes for the ladder windows. Episodes refused here are COUNTED under "
            f"LANE_RESERVED and printed (hard rule 11), never silently skipped"
        )


def providers_for(lane_names: list[str]) -> list[str]:
    """The distinct providers those lanes sit on, so a caller can check key **presence**."""
    lanes = load_lanes()
    seen: list[str] = []
    for name in lane_names:
        if name not in lanes:
            raise LaneError(f"{lane_name_error(name, lanes)}")
        provider = lanes[name].provider
        if provider not in seen:
            seen.append(provider)
    return seen


def lane_name_error(name: str, lanes: dict[str, Lane]) -> str:
    return f"{name!r} is not a lane; config/lanes.yaml declares {sorted(lanes)}"
