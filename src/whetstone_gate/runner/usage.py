"""**LIVE PER-MODEL USAGE — `evals/usage/<model>-<date>.jsonl`. Hard rule 12.**

`CLAUDE.md` §4 and `CONTEXT.md` §13.5(4):

    **Before your first sanctioned call, read `evals/usage/<model>-<date>.jsonl`.** Abort at
    whichever ceiling comes first. Report actual tokens **by model**.

    **Per-model token accounting, logged live**, so the day's remaining allowance is
    observable **mid-run** rather than discovered at exhaustion.

**A thin outer shell** (hard rule 8). It appends lines and reads them back; every arithmetic
decision it feeds belongs to :mod:`.budget`.

--------------------------------------------------------------------------------------
⚠️ ONE FILE PER MODEL PER DAY, AND THAT IS THE DAY-BOUNDARY MECHANISM
--------------------------------------------------------------------------------------

The path carries the model **and the UTC date**. `CONTEXT.md` §13.5(5): *"Resume across DAYS.
The sweep spans more than one daily allowance window by design."* A daily allowance is a
property of a **day**, so the accounting is per day, and a run that crosses midnight UTC
starts a new file and a fresh window without anybody deciding to. :func:`spent_today` reads
only today's file, which is what a daily ceiling means.

⚠️ **PER MODEL. NEVER POOLED.** Golden 8 fixture E: two lanes at 60,000 and 50,000 pool to
110,000 — over a 100,000 ceiling — while **neither exceeds it alone**, and the correct outcome
is *"BOTH LANES CONTINUE"*. There is no function in this module that sums across models. A
pooled total is available only from :func:`.report.pooled_total_for_disclosure`, which exists
so a report can say *"and this is the figure a POOLING implementation would have aborted on"*
and is named so it cannot be mistaken for a ceiling input.

--------------------------------------------------------------------------------------
⚠️ JSONL, APPEND-ONLY, ONE ROW PER CALL
--------------------------------------------------------------------------------------

One line per call, appended, never rewritten. `PROCESS.md` §8: *"Ledgers and results in
`evals/` are append-only to sessions."* A JSON **array** would have to be re-serialised on
every call — read, mutate, rewrite — which is a rewrite of a completed record on every single
call, and one crash mid-rewrite loses the day's accounting. Lines cannot do that.

**Each row carries the API's own `usage` total and the fields needed to reconcile it**:
`PROCESS.md` §12.1's C11 done-when is *"the usage file reconciles against API-reported
totals"*, and :func:`reconcile` is that check — it re-adds the file's own rows and compares
the sum to the total the caller says the provider reported. ⚠️ **It compares; it does not
correct.** A mismatch is a returned discrepancy, because a reconciliation that silently
adopted one side would be a reconciliation that can never fail.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping

from .redaction import refuse_if_secret_bearing

#: Where usage rows live, relative to the repository root. `CONTEXT.md` §16's tree.
USAGE_DIR = ("evals", "usage")

#: The fields on one usage row, in order. Declared; an undeclared field is a refusal.
ROW_KEYS: tuple[str, ...] = (
    "utc",
    "model",
    "lane",
    "episode",
    "total_tokens",
    "outcome",
)

#: What one call's row says happened. ⚠️ ``RATE_LIMITED`` rows carry ``total_tokens: 0``,
#: because golden 8's fixture D is explicit: *"a 429'd call contributes ZERO tokens"*.
OUTCOME_OK = "OK"
OUTCOME_RATE_LIMITED = "RATE_LIMITED"
OUTCOME_ERROR = "ERROR"
OUTCOMES: tuple[str, ...] = (OUTCOME_OK, OUTCOME_RATE_LIMITED, OUTCOME_ERROR)


class UsageError(RuntimeError):
    """The usage file cannot be written or read as specified. Always a refusal."""


@dataclass(frozen=True)
class Discrepancy:
    """One model-day where the file's own rows and the provider's reported total disagree."""

    model: str
    date: str
    from_rows: int
    api_reported: int

    @property
    def delta(self) -> int:
        return self.from_rows - self.api_reported


@dataclass(frozen=True)
class UsageLog:
    """The usage directory. **Holds a path and nothing else.**"""

    root: Path

    @classmethod
    def under(cls, repo_root: Path) -> "UsageLog":
        return cls(root=repo_root.joinpath(*USAGE_DIR))

    def path_for(self, model: str, date: str) -> Path:
        """``evals/usage/<model>-<date>.jsonl``. ⚠️ ``date`` is a **UTC** ``YYYY-MM-DD``.

        The model string is slug-safe because a lane name is: `config/lanes.yaml`'s ``name``
        field is already a hyphenated identifier. The **api_model_id** — ``openai/gpt-oss-20b``
        — is not, and is deliberately not what this path is built from.
        """
        for component, value in (("model", model), ("date", date)):
            if "/" in value or "\\" in value or ".." in value:
                raise UsageError(
                    f"{component}={value!r} carries a path separator or '..'. Use the LANE "
                    f"name (config/lanes.yaml:name), not the api_model_id"
                )
        return self.root / f"{model}-{date}.jsonl"

    # -- write -------------------------------------------------------------------------

    def append(
        self,
        *,
        model: str,
        date: str,
        utc: str,
        lane: str,
        episode: str,
        total_tokens: int,
        outcome: str,
        status: int | None = None,
        error_type: str | None = None,
    ) -> None:
        """Append one call's row. **Append-only; nothing is ever rewritten.**

        ``total_tokens`` is the provider's own ``usage.total_tokens`` — see
        :func:`.budget.usage_total_tokens`. It is **never** an estimate and never a
        reconstruction from ``prompt_tokens + completion_tokens``.

        ⚠️⚠️ **``status`` AND ``error_type`` EXIST BECAUSE OF `INCIDENTS.md` INC-142**, whose
        `Missing` field is that the pilot's ten `PROVIDER_ERROR` rows could not tell the
        operator *"whether the qwen lane needs a credential, a corrected `api_model_id`, or a
        parser change."* They come from :class:`whetstone_gate.driver.clients.ProviderFailed`'s
        own fields — an integer status and a short enum-shaped type, **never a body, never a
        header** — and they pass through the same secret scan as the rest of the row, which
        **refuses rather than masks**.

        ⚠️ **THEY ARE OMITTED FROM THE ROW WHEN THEY ARE ``None``, AND THAT IS LOAD-BEARING.**
        `evals/` is append-only and the pilot's committed rows are the record `INC-143`'s eight
        numbers were measured from. A schema change that added keys to a **successful** row
        would silently re-shape that record; an `OK` row has nothing to report, so it is
        byte-identical to the ones the pilot wrote. `tests/test_arch_lanes.py` pins that
        exactly.
        """
        if outcome not in OUTCOMES:
            raise UsageError(f"{outcome!r} is not a declared outcome; declared: {list(OUTCOMES)}")
        if isinstance(total_tokens, bool) or not isinstance(total_tokens, int):
            raise UsageError(f"total_tokens must be an integer; got {total_tokens!r}")
        if total_tokens < 0:
            raise UsageError(f"total_tokens must not be negative; got {total_tokens}")
        if outcome == OUTCOME_RATE_LIMITED and total_tokens:
            raise UsageError(
                f"a 429'd call contributes ZERO tokens (golden 8 fixture D, verbatim), and "
                f"this row claims {total_tokens}. The request was refused by the rate limiter "
                f"and never ran"
            )

        if status is not None and (isinstance(status, bool) or not isinstance(status, int)):
            raise UsageError(f"status must be an integer HTTP status or None; got {status!r}")
        if error_type is not None and not isinstance(error_type, str):
            raise UsageError(f"error_type must be a string or None; got {error_type!r}")

        row = {
            "utc": utc,
            "model": model,
            "lane": lane,
            "episode": episode,
            "total_tokens": total_tokens,
            "outcome": outcome,
        }
        # ⚠️ ONLY WHEN THERE IS SOMETHING TO REPORT. See this method's docstring: an `OK` row
        # must stay byte-identical to the ones the pilot committed.
        if status is not None:
            row["status"] = status
        if error_type is not None:
            row["error_type"] = error_type
        refuse_if_secret_bearing(row, where=f"usage[{model}-{date}]")
        path = self.path_for(model, date)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")

    # -- read --------------------------------------------------------------------------

    def rows(self, model: str, date: str) -> Iterator[dict[str, Any]]:
        """Every row for one model-day. An absent file yields nothing — **and that is not
        the same as a zero**, which is why :meth:`spent_today` says which it got."""
        path = self.path_for(model, date)
        if not path.is_file():
            return
        with path.open("r", encoding="utf-8") as handle:
            for number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise UsageError(f"{path}:{number} is not JSON: {exc}") from exc
                if not isinstance(row, dict):
                    raise UsageError(f"{path}:{number} did not parse to a mapping")
                missing = [k for k in ROW_KEYS if k not in row]
                if missing:
                    raise UsageError(f"{path}:{number} is missing {missing}")
                yield row

    def spent_today(self, model: str, date: str) -> tuple[int, int, bool]:
        """``(tokens, calls, the_file_existed)`` for one model-day.

        ⚠️ **The third element is the point.** *"Nothing has been spent"* and *"there is no
        file, so nothing has been read"* are different statements, and a runner that treats
        the second as the first starts a lane against a budget it never checked. `OF-03`'s
        doctrine, applied to a precondition instead of to a report.
        """
        path = self.path_for(model, date)
        existed = path.is_file()
        tokens = 0
        calls = 0
        for row in self.rows(model, date):
            tokens += int(row["total_tokens"])
            if row["outcome"] == OUTCOME_OK:
                calls += 1
        return tokens, calls, existed

    def reconcile(
        self, model: str, date: str, api_reported_total: int
    ) -> Discrepancy | None:
        """`PROCESS.md` §12.1's *"the usage file reconciles against API-reported totals"*.

        Re-adds this model-day's own rows and compares the sum to the total the provider
        reports. Returns ``None`` when they agree and a :class:`Discrepancy` when they do not.

        ⚠️ **It never corrects either side.** Adopting one would make the check unable to
        fail, which is the shape golden 8's own fixture-E note calls out: *"a fixture that
        cannot fail is the defect this project keeps finding."*
        """
        from_rows, _, _ = self.spent_today(model, date)
        if from_rows == api_reported_total:
            return None
        return Discrepancy(
            model=model, date=date, from_rows=from_rows, api_reported=api_reported_total
        )


def per_model_totals(log: UsageLog, models: list[str], date: str) -> dict[str, int]:
    """Each model's own total for one day. ⚠️ **A mapping, never a sum.**

    Returning a dictionary rather than a number is deliberate: hard rule 12 says *"Report
    actual tokens BY MODEL"*, and there is no call site that can accidentally treat this
    return value as one lane's spend.
    """
    return {model: log.spent_today(model, date)[0] for model in models}


def preflight(
    log: UsageLog, model: str, date: str, ceilings: Mapping[str, int]
) -> tuple[int, int, bool]:
    """Read a lane's day before its first call. `CLAUDE.md` §4's *"Before your first
    sanctioned call, read `evals/usage/<model>-<date>.jsonl`"*, as a function.

    Returns ``(tokens_already_spent, calls_already_made, file_existed)`` so a
    :class:`.budget.LaneBudget` can be **seeded from the day's real state** rather than from
    zero. A lane resumed mid-window that started its accumulator at zero would run its whole
    ceiling a second time, which is the exact overspend hard rule 12 exists to prevent.

    ``ceilings`` is accepted and validated rather than ignored, so that a caller cannot call
    this with a call ceiling alone: hard rule 12, *"A sanction of 'max N calls' alone is not a
    sanction."*
    """
    for required in ("call_ceiling", "token_ceiling"):
        if required not in ceilings:
            raise UsageError(
                f"preflight needs BOTH ceilings and {required!r} is absent. Hard rule 12: "
                f"'A sanction of max N calls alone is not a sanction: one spike episode "
                f"burned ~300K tokens against a 200K-TPD lane.'"
            )
    return log.spent_today(model, date)
