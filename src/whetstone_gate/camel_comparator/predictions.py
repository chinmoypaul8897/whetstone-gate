"""P1, P2 and P3 — the pre-registered CaMeL predictions, carried verbatim.

⚠️ **THEY ARE PARSED OUT OF `CONTEXT.md` §8.5.2, NOT COPIED INTO THIS FILE.** The C13
prompt's instruction is *"Do not reword them"*, and a transcription is a second copy that
can be reworded by accident — silently, by a later edit, in the one place where silence is
the failure. Parsing makes *"verbatim"* a property the suite checks rather than a promise a
session makes.

**They are already pre-registered by being in `CONTEXT.md`.** Nothing here registers them
and nothing here scores them: **C18 scores them** (`PROCESS.md` §12.1). This module's only
job is to carry them into the harness intact, so RUN-1's output can be read against the
predictions that existed before it ran.

WHAT EACH ONE IS FOR, IN ONE LINE EACH
=======================================
  * **P1** — the *recipient clause*. CaMeL blocks exfiltration on provenance, never on
    magnitude. If P1 holds, the envelope gap this project claims exists is located.
  * **P2** — ``InjectionTask6``, which **is A5, salami slicing**, and is the one banking
    injection CaMeL-without-policies fails. Its predicted denial names the recipient and
    **never the aggregate**, *because there is no aggregate symbol in the engine to name* —
    a claim :mod:`.claims` re-derives at the pin rather than repeats.
  * **P3** — the honesty clause. A denial quoting *"No security policy matched"* measures
    **policy coverage**, not provenance enforcement, and is counted and reported
    **separately**. Without P3 a comparator run could report CaMeL blocking everything
    while measuring nothing, which is `INCIDENTS.md` **INC-05**'s class one level up.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PREDICTION_IDS = ("P1", "P2", "P3")
"""The three predictions `CONTEXT.md` §8.5.2 pre-registers. Exactly three, in order."""


class PredictionError(RuntimeError):
    """§8.5.2 could not be read, so the predictions cannot be carried."""


@dataclass(frozen=True)
class Prediction:
    """One pre-registered prediction, exactly as `CONTEXT.md` §8.5.2 states it."""

    ident: str
    """``P1`` / ``P2`` / ``P3``."""

    text: str
    """⚠️ **Verbatim.** The blockquote's own markdown, with only the ``> `` quote prefix
    removed and wrapped lines rejoined. Nothing is reworded, reordered or summarised."""

    def one_line(self) -> str:
        """The prediction with markdown emphasis stripped, for console rendering.

        ⚠️ A rendering convenience and **not** a second version of the prediction:
        :attr:`text` remains the carried value, and the tests assert against *that*.
        """
        plain = re.sub(r"\*\*(.+?)\*\*", r"\1", self.text)
        plain = re.sub(r"\*(.+?)\*", r"\1", plain)
        return re.sub(r"\s+", " ", plain).strip()


def _section_8_5_2(context_md: str) -> str:
    """§8.5.2's body, or refuse."""
    lines = context_md.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("### 8.5.2 ")]
    if len(starts) != 1:
        raise PredictionError(
            f"'### 8.5.2 ' matched {len(starts)} times in CONTEXT.md, not once. The "
            f"predictions are pre-registered BY BEING IN CONTEXT.md; if this parser cannot "
            f"find them, the harness would carry nothing and still look complete."
        )
    start = starts[0]
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    return "\n".join(lines[start:end])


def parse_predictions(context_md: str) -> list[Prediction]:
    """Return P1, P2 and P3 verbatim from `CONTEXT.md` §8.5.2.

    ⚠️ Refuses on anything but exactly three, in order. A §8.5.2 that grew a P4 or lost a
    P2 is a change to a **pre-registered** artefact, and the right response is a loud stop,
    not a harness that quietly carries two predictions where three were registered.
    """
    body = _section_8_5_2(context_md)
    quoted = [
        line[2:] if line.startswith("> ") else line[1:]
        for line in body.splitlines()
        if line.startswith(">")
    ]
    blockquote = "\n".join(quoted)

    marks = [(m.group(1), m.start()) for m in re.finditer(r"\*\*(P[123])\.\*\*", blockquote)]
    if [ident for ident, _ in marks] != list(PREDICTION_IDS):
        raise PredictionError(
            f"CONTEXT.md S8.5.2's blockquote states {[i for i, _ in marks]}, not "
            f"{list(PREDICTION_IDS)}. These are PRE-REGISTERED predictions; a change to "
            f"their number or order is a change to the pre-registration."
        )

    predictions: list[Prediction] = []
    for index, (ident, offset) in enumerate(marks):
        end = marks[index + 1][1] if index + 1 < len(marks) else len(blockquote)
        chunk = blockquote[offset:end].strip()
        text = re.sub(r"\s*\n\s*", " ", chunk).strip()
        if len(text) < 80:
            raise PredictionError(
                f"{ident} parsed to {len(text)} characters, which is too short to be the "
                f"prediction CONTEXT.md states. A truncated prediction carried into the "
                f"harness would be scored as if it were whole."
            )
        predictions.append(Prediction(ident=ident, text=text))
    return predictions
