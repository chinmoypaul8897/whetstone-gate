"""The τ²-bench adapter.

⚠️ **This package is `whetstone_gate.tau2`, NOT a top-level `tau2`.** `QUESTIONS.md`
**Q-004** (architect, 2026-08-31) ruled OPTION 1 on exactly this point, and the deciding
fact was this package: `vendor/tau2-bench/pyproject.toml` declares ``name = "tau2"`` and
installs a **top-level package called `tau2`**. A sibling layout — `src/tau2/`, as
`CONTEXT.md` §16 originally drew it — would publish a second top-level `tau2` into every
reviewer's environment, **in direct collision with the benchmark this project's entire
external-answer-key claim rests on**. Import paths are `whetstone_gate.tau2.…`.

**What lives here, and what does not.** C3 builds the *enumeration and the selections*:
which of Sierra's 164 airline+retail tasks are must-not-write, which are write, and which
40 are pre-registered for the T-FP block. **Driving a task end to end with the user
simulator is C5's**, and the fence between them is deliberate — `PROCESS.md` §12.1 splits
adapter A from adapter B precisely so the risk `CONTEXT.md` §21.4 calls *the project's #1
time risk* is retired before anything depends on it.

**Nothing in this package authors a task, a gold behaviour or a grader.** That is the
point of the whole chunk: τ²-bench is *"the ONLY source of tasks, gold behaviour and a
grader that this project did not author"*, and the moment we write one of our own we are
grading our own homework, which is the failure this submission exists to name.
"""

from __future__ import annotations
