"""WHETSTONE GATE.

A policy gate for agentic payments, attacked by an adversary that has never seen the
policy, on an externally-authored answer key, under a protocol that was frozen,
git-tagged and externally witnessed before the first scored episode ran.

The specification is `CONTEXT.md` and it is LAW. The method is `PROCESS.md`. The rules
every session is bound by are `CLAUDE.md`.

⚠️ Two structural rules govern what may import what, and each is asserted by a test:

  * ``scorer`` imports no model client, and shares NO first-party module with ``gates``.
    Anything both need is written TWICE, on purpose — once against the live call, once
    against the replayed ledger. In the spike, the gate and the invariant checker both
    called the same ``intentKey`` helper, so the invariant could not have fired unless
    the gate had a bug. That is not a result; it is a definition.

  * Core logic takes data in and returns results — no I/O, clock, network or randomness
    inside it. Side effects live in a thin outer shell.
"""

__version__ = "0.1.0"
