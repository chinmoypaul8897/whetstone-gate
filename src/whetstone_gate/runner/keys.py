"""**KEY PRESENCE, BY NAME. THERE IS NO PATH HERE THAT RETURNS A KEY VALUE.**

`CLAUDE.md` §4 and `PROCESS.md` §8, verbatim:

    **Never read, print, echo or commit `.env` or any API key value.** To confirm a key
    exists, read only its **name**. Keys live in `.env`, which is git-ignored.
    `.env.example` carries names and **no** values.

    **Secrets never in the repo, never in logs, never in reports.**

⚠️ **THE ONLY PUBLIC FUNCTION HERE RETURNS A BOOLEAN.** :func:`key_is_present` asks
``name in os.environ`` and returns that answer. It does **not** subscript the environment, it
does not call ``os.getenv``, and it does not open `.env`. A caller who wanted the value could
not obtain it from this module by any argument, because there is no code path that reads one.
``tests/test_c11_runner.py`` asserts that by parsing this module's AST rather than by reading
its prose.

⚠️ **AND THE MODULE DOES NOT NAME THE ENVIRONMENT VARIABLES EITHER.** The names come from
`config/lanes.yaml`'s ``provider`` field through :func:`env_var_for_provider`, so adding a
provider is a config edit rather than a source edit — and, more to the point, this file
contains no string that a grep for a key name would find in a suspicious place.

**Why a module at all, for one boolean.** Because the alternative is the boolean being
computed inline in the scheduler, next to the code that builds request payloads, where the
one-character difference between ``name in os.environ`` and ``os.environ[name]`` is invisible
in review. Here it is the whole file, and the file is scanned.
"""

from __future__ import annotations

import os

#: How a provider's key is named in the environment. Derived from the provider string, upper
#: cased, plus the project's one suffix. `.env.example` carries exactly ``GROQ_API_KEY`` and
#: ``GOOGLE_API_KEY``, both with **no value**, and this reproduces those two names from
#: `config/lanes.yaml`'s ``provider`` field rather than hardcoding a list that can drift.
_ENV_SUFFIX = "_API_KEY"


class KeyError_(RuntimeError):
    """A lane names a provider whose key name cannot be derived. A refusal, never a guess."""


def env_var_for_provider(provider: str) -> str:
    """The environment variable **NAME** for ``provider``. A name; never a value.

    ``"groq"`` -> ``"GROQ_API_KEY"``; ``"google"`` -> ``"GOOGLE_API_KEY"``.
    """
    if not isinstance(provider, str) or not provider.strip():
        raise KeyError_(f"a lane's provider must be a non-empty string; got {provider!r}")
    cleaned = provider.strip().upper().replace("-", "_").replace(" ", "_")
    if not cleaned.isidentifier():
        raise KeyError_(
            f"provider {provider!r} does not yield a usable environment variable name "
            f"({cleaned!r}). This is a refusal rather than a sanitised guess: a guessed name "
            f"reads as absent, and 'the key is missing' would then be indistinguishable from "
            f"'we looked in the wrong place'"
        )
    return cleaned + _ENV_SUFFIX


def key_is_present(env_var_name: str) -> bool:
    """``True`` if a variable of that **name** is set. ⚠️ **The value is never read.**

    ``in`` on the mapping, not a subscript and not ``getenv``. The distinction is the whole
    module: a subscript would put the secret on the stack, in a traceback frame, and one
    careless ``repr`` away from a log line.
    """
    return env_var_name in os.environ


def missing_keys(providers: list[str]) -> list[str]:
    """The **names** of the variables that are not set, for the providers given.

    Returned so a runner can refuse **before** dispatching an episode it cannot complete —
    which is hard rule 11's shape applied to a precondition: an episode that fails on a
    missing credential halfway through is an episode that has already spent tokens.
    """
    return [
        name
        for name in (env_var_for_provider(p) for p in providers)
        if not key_is_present(name)
    ]
