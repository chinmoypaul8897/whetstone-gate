"""C14 — THE FREEZE, checked rather than asserted.

⚠️ **WHY THIS FILE EXISTS, IN ONE SENTENCE.** A pre-registration is a claim about *what was written
down before the numbers were taken*, and **a claim nothing checks is a comment** — which is the exact
diagnosis `QUESTIONS.md` `Q-079` records for a `config/` key that carried the superseded Branch-B
trigger through a fix session that had the file open, because *nothing read either key*.

So every load-bearing sentence in the four frozen artefacts this chunk writes is pinned here:

  * **(a)** every `config/` file has a row in `PROTOCOL.md`'s manifest and its **git-blob** SHA-256
    **recomputes**;
  * **(b)** ⚠️ that check is **FIRED AT A TAMPERED FIXTURE** and required to go **RED**. *A manifest
    that has never gone red is decoration* — `ai-playbook` B.9's rule about release gates, applied to
    the gate this project's central claim rests on;
  * **(c)** `INVARIANTS.md`'s eight predicates agree with **golden 2's own `predicates` block, term
    by term**, byte for byte. Two statements of one predicate is the shape that drifts, and the
    golden is the scorer's oracle while `INVARIANTS.md` is the published statement;
  * **(d)** `HOLES.md`'s probe fields agree with `config/protocol.yaml`'s `probe.*` **exactly**,
    read **through the loader**, and S4's window agrees with
    `invariants.s4_in_flight_window_width` — ⚠️ **not** `world.s4_in_flight_window_width` (`Q-091`);
  * **(e)** ⚠️ **no artefact claims more than the system delivers**, on the two ceilings this
    repository has already paid for: the ledger is evident **against an edit that leaves a stale
    digest and against nothing else**, and **model output is not reproducible**.

⚠️ **(e) IS THE `M39` PATTERN, APPLIED ONE LEVEL OUT.** Mutant `M39` replaced `chain.py`'s stated
limitation with *"the ledger is tamper-evident: any alteration is detected"* and the **whole suite
stayed GREEN**. The architect's C7 REVIEW 1 ruling 4 is explicit about the scope of the remedy:
*"DO fail it if any docstring, comment **or artefact** claims more than that."* `chain.py` is now
pinned; **the artefacts were not**, and a frozen artefact is the copy a judge actually reads.

**Nothing in this file transcribes an expected value that the artefacts also carry.** Both sides come
from somewhere else — `config/` through the loader, the golden through `json`, the git object store
through `git cat-file` — and the artefacts are **parsed**. A number written into this file by hand
would be a third copy that can drift from both.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest
import yaml

from whetstone_gate import config as cfg

# ======================================================================================
# The frozen set, and the two documents this chunk must keep in agreement.
# ======================================================================================

#: `CONTEXT.md` §15.0's frozen set: exactly five files plus `config/`. `INCIDENTS.md` is
#: SNAPSHOTTED by the tag and explicitly CONTINUES TO GROW, so it is not here.
FROZEN_FILES: tuple[str, ...] = (
    "HOLES.md",
    "INVARIANTS.md",
    "PROTOCOL.md",
    "PROVENANCE.md",
    "RAZORPAY_SEMANTICS.md",
)

GOLDEN_2 = "tests/goldens/golden2_invariants.json"

#: The eight, in golden 2's own key order. `S2-amt` is a KEY, not a variant spelling.
PREDICATE_KEYS: tuple[str, ...] = ("E1", "E2", "E3", "S1", "S2", "S2-amt", "S3", "S4")


# ======================================================================================
# git-object plumbing. `PROCESS.md` §6a.1: hash the OBJECT, never the working tree.
# ======================================================================================


def _git(repo_root: Path, *args: str) -> bytes:
    """Run git and return raw stdout **bytes** — never text, never a decoded pipe."""
    done = subprocess.run(
        ["git", *args], cwd=repo_root, capture_output=True, check=True
    )
    return done.stdout


def blob_bytes(repo_root: Path, path: str, ref: str = "HEAD") -> bytes:
    """The stored bytes of ``path`` at ``ref``.

    ⚠️ **NOT the working-tree bytes, and the distinction decides whether a reviewer on Linux
    can verify this project at all.** `core.autocrlf` is `true` system-wide on the machine
    this repository is built on, so a file committed with LF checks out as CRLF and hashes
    differently. A fingerprint published from a working tree fails for every non-Windows
    reviewer — **silently, at the moment of judging.** (`PROCESS.md` §6a.1, measured there.)
    """
    blob_id = _git(repo_root, "rev-parse", f"{ref}:{path}").decode().strip()
    return _git(repo_root, "cat-file", "blob", blob_id)


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


# ======================================================================================
# THE MANIFEST CHECK — a PURE function, so that (b) can fire it at a tampered fixture.
# ======================================================================================

_MANIFEST_ROW = re.compile(
    r"^\|\s*`(config/[^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|", re.MULTILINE
)


def manifest_rows(protocol_text: str) -> dict[str, str]:
    """Parse `PROTOCOL.md`'s `config/` manifest into ``{path: sha256}``.

    ⚠️ **A PARSER THAT SILENTLY READS NOTHING IS THE SAME CLASS OF DEFECT AS THE CHECK IT
    REPLACES**, so every caller asserts the row count it got.
    """
    return {path: digest for path, digest in _MANIFEST_ROW.findall(protocol_text)}


def manifest_problems(manifest: dict[str, str], blobs: dict[str, bytes]) -> list[str]:
    """**THE CHECK.** Every problem between a manifest and a set of file bytes.

    Empty list means PASS. It is deliberately a pure function of two dictionaries: the whole
    point of `(b)` is to hand it a **tampered** copy and require it to come back non-empty,
    and a check that can only be run against reality can never be shown to work.

    Three failure directions, because only one of them is the obvious one:

      1. a file whose bytes do not hash to its manifest row — **the tamper**;
      2. a file present in `config/` with **no row** — a value the freeze does not cover;
      3. a row naming a file that **does not exist** — a manifest that has drifted the other
         way.
    """
    problems: list[str] = []
    for path in sorted(set(manifest) | set(blobs)):
        if path not in blobs:
            problems.append(f"{path}: manifest row for a file that does not exist")
            continue
        if path not in manifest:
            problems.append(f"{path}: present in config/ with NO manifest row")
            continue
        actual = sha256_hex(blobs[path])
        if actual != manifest[path]:
            problems.append(
                f"{path}: MISMATCH — manifest says {manifest[path]}, bytes hash to {actual}"
            )
    return problems


# ======================================================================================
# (a) THE MANIFEST RECOMPUTES
# ======================================================================================


def test_every_config_file_is_in_PROTOCOL_mds_manifest_and_its_blob_sha_RECOMPUTES(
    repo_root: Path,
) -> None:
    """⚠️ **The pre-registration's own integrity check, run for real.**

    `CONTEXT.md` §15.0: *"Every file under `config/` is listed in `PROTOCOL.md` with its
    SHA-256 (of its git blob, not its working-tree bytes)."* This asserts it in **both
    directions at once** — no file without a row, no row without a file — because a freeze
    that covers *most* of what the experiment reads covers nothing.
    """
    protocol = (repo_root / "PROTOCOL.md")
    assert protocol.is_file(), "PROTOCOL.md does not exist; C14 writes it."

    manifest = manifest_rows(protocol.read_text(encoding="utf-8"))
    on_disk = sorted(p.name for p in (repo_root / "config").glob("*.yaml"))
    assert on_disk, "config/ holds no .yaml files; the parser or the tree is wrong."
    assert manifest, (
        "PROTOCOL.md's config manifest parsed to ZERO rows. A parser that silently reads "
        "nothing is the defect it replaces."
    )

    blobs = {f"config/{name}": blob_bytes(repo_root, f"config/{name}") for name in on_disk}
    problems = manifest_problems(manifest, blobs)
    assert not problems, "PROTOCOL.md's config/ manifest does not recompute:\n  " + "\n  ".join(
        problems
    )


def test_the_working_tree_agrees_with_the_object_store_for_config(
    repo_root: Path,
) -> None:
    """⚠️ **The manifest hashes the OBJECT; the experiment reads the WORKING TREE.**

    If those two ever disagree, the manifest can recompute perfectly while the file the run
    actually loads says something else — a freeze that verifies and means nothing. This is
    the one place that gap can open, so it is closed here rather than assumed shut.
    """
    dirty = _git(repo_root, "status", "--porcelain", "--", "config/").decode().strip()
    assert not dirty, (
        "config/ has uncommitted changes, so PROTOCOL.md's git-blob digests describe bytes "
        f"the experiment will not read:\n{dirty}"
    )


# ======================================================================================
# (b) ⚠️ FIRED AT A TAMPERED FIXTURE. A manifest that has never gone red is decoration.
# ======================================================================================


def test_the_manifest_check_GOES_RED_on_a_TAMPERED_config_VALUE(
    repo_root: Path, tmp_path: Path
) -> None:
    """⚠️ **The gate, fired.** A control that has never been observed failing is not a control.

    The tamper is **a real config value change, not a whitespace edit**, and this test proves
    that before it proves anything else: the tampered bytes still **parse as YAML** and
    `money.per_action_cap_paise` reads back **different**. Otherwise a green-then-red pair
    would only show that SHA-256 notices a byte, which nobody doubts.

    ⚠️ **AND THE CONTROL RUNS FIRST.** The untampered bytes must come back **clean** through
    the same function, or the red below proves nothing about tampering — it would only show
    that the check fails on everything.
    """
    protocol_text = (repo_root / "PROTOCOL.md").read_text(encoding="utf-8")
    manifest = manifest_rows(protocol_text)
    target = "config/protocol.yaml"
    assert target in manifest, f"{target} has no manifest row; (a) should have caught this."

    pristine = blob_bytes(repo_root, target)
    blobs = {path: blob_bytes(repo_root, path) for path in manifest}

    # ── CONTROL: the real bytes are CLEAN through the very same function ─────────────
    assert manifest_problems(manifest, blobs) == [], (
        "the untampered manifest check is already failing, so the RED below would prove "
        "nothing about tampering."
    )

    # ── THE TAMPER: one spec value, changed by one paise ─────────────────────────────
    before = yaml.safe_load(pristine.decode("utf-8"))["money"]["per_action_cap_paise"]
    tampered = pristine.replace(
        f"per_action_cap_paise: {before}".encode(),
        f"per_action_cap_paise: {before + 1}".encode(),
    )
    assert tampered != pristine, "the tamper did not apply; the fixture is not exercising anything."

    # It is a REAL value change: it still parses, and the value really moved.
    reparsed = yaml.safe_load(tampered.decode("utf-8"))
    assert reparsed["money"]["per_action_cap_paise"] == before + 1, (
        "the tampered copy does not parse to a changed value, so this is a whitespace edit "
        "dressed as a value edit."
    )
    # Write it out so the fixture is a file on disk, not only a bytes object.
    tampered_path = tmp_path / "protocol.yaml"
    tampered_path.write_bytes(tampered)

    # ── THE CHECK MUST GO RED ────────────────────────────────────────────────────────
    problems = manifest_problems(manifest, {**blobs, target: tampered_path.read_bytes()})
    assert problems, (
        "⚠️ THE MANIFEST DID NOT NOTICE A CHANGED SPEC VALUE. `make check-prereg` would pass "
        "over an edited pre-registration artefact, which is the single failure this whole "
        "chunk exists to make impossible."
    )
    assert any(target in p and "MISMATCH" in p for p in problems), (
        f"the check went red for the wrong reason: {problems}"
    )


def test_the_manifest_check_GOES_RED_on_a_MISSING_ROW_and_on_a_PHANTOM_ROW(
    repo_root: Path,
) -> None:
    """⚠️ **The other two directions, fired.**

    A manifest can fail by covering too little (a `config/` file nobody listed — the value
    the freeze does not reach) or by covering too much (a row for a file that is gone). Both
    are silent under a check that only compares the rows it happens to have.
    """
    manifest = manifest_rows((repo_root / "PROTOCOL.md").read_text(encoding="utf-8"))
    blobs = {path: blob_bytes(repo_root, path) for path in manifest}
    dropped = sorted(manifest)[0]

    missing_row = manifest_problems({k: v for k, v in manifest.items() if k != dropped}, blobs)
    assert any("NO manifest row" in p for p in missing_row), (
        f"a config/ file with no manifest row went unnoticed: {missing_row}"
    )

    phantom = manifest_problems(
        {**manifest, "config/never_existed.yaml": "0" * 64}, blobs
    )
    assert any("does not exist" in p for p in phantom), (
        f"a manifest row for a nonexistent file went unnoticed: {phantom}"
    )


# ======================================================================================
# (c) INVARIANTS.md AGREES WITH GOLDEN 2, TERM BY TERM
# ======================================================================================


def golden_predicates(repo_root: Path) -> dict[str, str]:
    block = json.loads((repo_root / GOLDEN_2).read_text(encoding="utf-8"))["predicates"]
    return {k: v for k, v in block.items() if not k.startswith("_")}


def invariants_quoted_predicates(invariants_text: str) -> dict[str, str]:
    """Pull each predicate's **verbatim golden quote** out of `INVARIANTS.md`.

    The file states each invariant twice on purpose: once as prose a stranger can apply, and
    once as the golden's own words in a blockquote directly under a marker line. **The prose
    is for the reader; the quoted line is the contract**, and it is the quoted line this
    compares.
    """
    found: dict[str, str] = {}
    lines = invariants_text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(
            r"^\*\*Golden-2 predicate\*\*.*`predicates\.([A-Za-z0-9-]+)`:\s*$", line
        )
        if not match:
            continue
        for candidate in lines[index + 1 : index + 4]:
            if candidate.startswith("> "):
                found[match.group(1)] = candidate[2:]
                break
    return found


def test_INVARIANTS_md_agrees_with_GOLDEN_2s_predicates_block_TERM_BY_TERM(
    repo_root: Path,
) -> None:
    """⚠️ **Two statements of one predicate is the shape that drifts.**

    `tests/goldens/golden2_invariants.json` is the **scorer's** oracle — hand-computed by the
    architect, read-only to every build session. `INVARIANTS.md` is the **published**
    statement, and it is what a judge reads. Nothing but this test connects them.

    The comparison is **byte for byte**, in both directions: every golden key must appear in
    the artefact, every artefact quote must name a golden key, and the strings must be equal.
    A paraphrase pins the paraphrase.
    """
    golden = golden_predicates(repo_root)
    assert set(golden) == set(PREDICATE_KEYS), (
        f"golden 2's predicate keys moved: {sorted(golden)} vs {sorted(PREDICATE_KEYS)}"
    )

    quoted = invariants_quoted_predicates(
        (repo_root / "INVARIANTS.md").read_text(encoding="utf-8")
    )
    assert set(quoted) == set(PREDICATE_KEYS), (
        "INVARIANTS.md does not carry exactly the eight golden-2 predicate quotes. "
        f"Found {sorted(quoted)}; expected {sorted(PREDICATE_KEYS)}."
    )

    divergences = [
        f"{key}:\n    golden:    {golden[key]!r}\n    artefact:  {quoted[key]!r}"
        for key in PREDICATE_KEYS
        if golden[key] != quoted[key]
    ]
    assert not divergences, (
        "⚠️ INVARIANTS.md and golden 2 state a predicate DIFFERENTLY. One of them is wrong, "
        "and which one is not a thing a test may decide — it is a STOP.\n"
        + "\n".join(divergences)
    )


def test_the_predicate_comparison_would_NOTICE_a_one_word_paraphrase() -> None:
    """⚠️ **Fired.** The comparison above is only worth its bytes if a near-miss fails it.

    The planted text is the real S2 predicate with **`ISSUED` softened to `EXECUTED`** —
    which is not a cosmetic edit anywhere in this project. It is `Q-027` MOVE 3 **run
    backwards**, and it names the exact predicate the architect withdrew because it *could
    not fire*.
    """
    golden = {"S2": "two refunds ISSUED ON THE SAME PAYMENT carrying the SAME NON-EMPTY receipt."}
    artefact = (
        "**Golden-2 predicate**, verbatim from x → `predicates.S2`:\n\n"
        "> two refunds EXECUTED ON THE SAME PAYMENT carrying the SAME NON-EMPTY receipt.\n"
    )
    quoted = invariants_quoted_predicates(artefact)
    assert quoted, "the parser found nothing in the planted fixture, so it proves nothing."
    assert quoted["S2"] != golden["S2"], (
        "the comparison does not distinguish ISSUED from EXECUTED, so it would not have "
        "caught Q-027's withdrawn predicate coming back."
    )


# ======================================================================================
# (d) HOLES.md AGREES WITH config/ EXACTLY
# ======================================================================================

_HOLES_ROW = re.compile(r"^\|\s*`([a-z0-9_.]+)`\s*\|\s*`([^`]*)`\s*\|\s*$", re.MULTILINE)


def holes_rows(holes_text: str) -> dict[str, str]:
    return dict(_HOLES_ROW.findall(holes_text))


def test_HOLES_md_probe_fields_agree_with_config_protocol_yaml_EXACTLY(
    repo_root: Path,
) -> None:
    """⚠️ **A drifted copy of the probe's note would close the door and make arm 4 VOID BY
    CONSTRUCTION while every test still passed.**

    That is `CONTEXT.md` §8.6's own sentence about this exact string, and it is why the note
    lives under the freeze rather than in source. Clause **P7** matches on it, **CANARY-A**'s
    breach predicate depends on it, and its near-neighbour — note template 4's *"standard
    limits apply"* — is a deliberate decoy that grants nothing.

    Every row is read **through the loader**, so a sentinel or a blank raises rather than
    comparing equal to something.
    """
    protocol_cfg = cfg.load("protocol")
    rows = holes_rows((repo_root / "HOLES.md").read_text(encoding="utf-8"))
    assert rows, "HOLES.md's config table parsed to ZERO rows."

    # Every DETERMINED probe.* key in config/ must be carried by the artefact.
    declared_sentinels = {dotted for dotted, _ in protocol_cfg.sentinels()}
    probe_keys = {
        f"probe.{leaf}"
        for leaf in protocol_cfg.data["probe"]
        if not isinstance(protocol_cfg.data["probe"][leaf], dict)
    }
    probe_keys |= {
        f"probe.notes.{leaf}" for leaf in protocol_cfg.data["probe"].get("notes", {})
    }
    uncovered = sorted((probe_keys - declared_sentinels) - set(rows))
    assert not uncovered, (
        f"HOLES.md omits determined probe values that config/ carries: {uncovered}. "
        "A probe field the frozen artefact does not state is a field nothing pins."
    )

    # And the sentinel itself must be NAMED, not quietly absent.
    holes_text = (repo_root / "HOLES.md").read_text(encoding="utf-8")
    assert "probe.void_threshold_breach_rate" in holes_text, (
        "HOLES.md does not name the void threshold's config key. An undetermined value that "
        "the artefact does not mention is indistinguishable from one nobody owes."
    )
    assert "TODO_C14_CALIBRATION" in holes_text, (
        "HOLES.md does not name the void threshold's SENTINEL, so a reader cannot tell that "
        "the number is owed rather than chosen."
    )

    # Every stated row must equal what the loader returns.
    mismatches: list[str] = []
    for dotted, stated in sorted(rows.items()):
        actual = protocol_cfg.require(dotted)
        if isinstance(actual, bool):
            agrees = stated.lower() == str(actual).lower()
        elif isinstance(actual, int):
            agrees = stated.replace(",", "").strip() == str(actual)
        elif isinstance(actual, float):
            agrees = float(stated) == actual
        else:
            agrees = stated == actual
        if not agrees:
            mismatches.append(f"{dotted}: HOLES.md says {stated!r}, config/ says {actual!r}")
    assert not mismatches, (
        "⚠️ HOLES.md and config/ disagree about the probe. The frozen artefact and the file "
        "the experiment reads must say the same thing:\n  " + "\n  ".join(mismatches)
    )


def test_HOLES_md_carries_S4s_WINDOW_WIDTH_AT_THE_KEY_PATH_IT_REALLY_LIVES_AT(
    repo_root: Path,
) -> None:
    """⚠️ **`Q-091`: the width is at `invariants.s4_in_flight_window_width`, NOT under `world.`.**

    The **value is 2 under either name**, so no number moves and this is not a money defect —
    which is exactly why it is worth a test. A wrong key path in a *frozen* artefact is
    inherited silently by everything downstream, and the golden's own `constants` block
    records the same correction for the same reason.
    """
    holes_text = (repo_root / "HOLES.md").read_text(encoding="utf-8")
    protocol_cfg = cfg.load("protocol")

    assert "invariants.s4_in_flight_window_width" in holes_text, (
        "HOLES.md does not name S4's window width at its real config key path."
    )
    assert "world.s4_in_flight_window_width" not in holes_text, (
        "HOLES.md names S4's window under `world.`, which is Q-091's wrong path."
    )

    stated = holes_rows(holes_text).get("invariants.s4_in_flight_window_width")
    assert stated is not None, "HOLES.md has no table row for S4's window width."
    assert int(stated) == protocol_cfg.require("invariants.s4_in_flight_window_width")

    # And the golden agrees, so all three copies are pinned to one another.
    golden_constants = json.loads((repo_root / GOLDEN_2).read_text(encoding="utf-8"))[
        "constants"
    ]["s4_in_flight_window_width"]
    assert golden_constants["config_key"] == "invariants.s4_in_flight_window_width"
    assert golden_constants["value"] == int(stated)


# ======================================================================================
# (e) ⚠️ NO ARTEFACT CLAIMS MORE THAN THE SYSTEM DELIVERS — BOTH CEILINGS, BY PARSING
# ======================================================================================

#: Sentences that are FALSE about this repository's ledger. `M39` is the first of them
#: verbatim, and it survived the entire suite once already.
_TAMPER_OVERCLAIMS: tuple[str, ...] = (
    "any alteration is detected",
    "every alteration is detected",
    "all alterations are detected",
    "any modification is detected",
    "tamper-proof",
    "tamperproof",
)

#: Sentences that are FALSE about this project's determinism. The attacker runs at
#: temperature 0.7 against a hosted provider; hard rule 10 states the scope exactly.
_DETERMINISM_OVERCLAIMS: tuple[str, ...] = (
    "re-running the models reproduces",
    "rerunning the models reproduces",
    "the run is fully reproducible",
    "fully reproducible run",
    "reproduces the run",
)

#: A window that CONTAINS one of these is REPORTING the false claim, not making it. This is
#: how an honest artefact quotes a sentence in order to reject it — and how a mutant that
#: quotes it in order to ASSERT it is still caught.
_DISCLAIMERS: tuple[str, ...] = (
    "false",
    "is not claimed",
    "never claimed",
    "does not claim",
    "do not claim",
    "not caught",
    "does not",
    "do not write",
    "must not",
    "would be",
)

_WINDOW = 220


def overclaim_hits(documents: dict[str, str], phrases: tuple[str, ...]) -> list[str]:
    """Every occurrence of ``phrases`` that is **not** inside a disclaimer.

    ⚠️ **PRESENCE IS NOT THE TEST; PROXIMITY TO A DISCLAIMER IS.** Requiring the ceiling's
    words alone would be defeated by a document that keeps them *and* adds an overclaim
    beside them, which is precisely what `M39` did to `chain.py`.
    """
    hits: list[str] = []
    for name, text in documents.items():
        flat = re.sub(r"\s+", " ", text.replace("**", "").replace("*", "")).lower()
        for phrase in phrases:
            start = 0
            while (found := flat.find(phrase, start)) != -1:
                window = flat[max(0, found - _WINDOW) : found + _WINDOW]
                if not any(d in window for d in _DISCLAIMERS):
                    hits.append(f"{name}: {phrase!r} with no disclaimer near: ...{window}...")
                start = found + 1
    return hits


def frozen_documents(repo_root: Path) -> dict[str, str]:
    return {
        name: (repo_root / name).read_text(encoding="utf-8")
        for name in FROZEN_FILES
        if (repo_root / name).is_file()
    }


def test_NO_ARTEFACT_CLAIMS_MORE_TAMPER_EVIDENCE_THAN_THE_LEDGER_DELIVERS(
    repo_root: Path,
) -> None:
    """⚠️ **Ruling 4, extended from `chain.py` to the artefacts, which is where it always pointed.**

    *"The ledger is tamper-evident"* means **evident against an edit that leaves a stale
    digest, and against nothing else.** What is **not** caught is any edit leaving **no**
    stale digest, and there are **exactly two** shapes of it — **truncation** and **a
    re-derived suffix** — both the same fact: *nothing commits to the END of the chain.*

    ⚠️ **`OF-57`'s published row said *"truncation is THE ONE mutation the chain cannot see"*
    and *"any alteration is DETECTED"*. Both were FALSE**, and `OF-157` is the correction.
    The row predated the second shape's identification, `chain.py` caught up and the
    published text did not — which is exactly what this test is for.

    **BOTH DIRECTIONS.** Direction 1: the ceiling is stated, and **both** undetected shapes
    are named. Direction 2: it is not exceeded anywhere in the frozen set.
    """
    documents = frozen_documents(repo_root)
    assert len(documents) >= 3, f"too few frozen artefacts found to check: {sorted(documents)}"

    # ── DIRECTION 1: the ceiling is STATED, and both shapes are ENUMERATED ───────────
    for name in ("PROTOCOL.md", "HOLES.md", "INVARIANTS.md"):
        flat = re.sub(r"\s+", " ", documents[name].replace("**", "").replace("*", "")).lower()
        required = {
            "evident against an edit that leaves a stale digest": "the ceiling itself",
            "against nothing else": "the half that makes it a ceiling and not a boast",
            "truncation": "undetected shape 1",
            "re-derived suffix": "undetected shape 2 — the one OF-57's row omitted",
        }
        missing = [f"{k!r} ({why})" for k, why in required.items() if k not in flat]
        assert not missing, (
            f"{name} no longer states the tamper-evidence ceiling. A claim nothing pins is a "
            "claim that drifts (OF-142, mutant M39). Missing: " + "; ".join(missing)
        )

    # ── DIRECTION 2: the ceiling is NOT EXCEEDED, anywhere in the frozen set ─────────
    hits = overclaim_hits(documents, _TAMPER_OVERCLAIMS)
    assert not hits, (
        "⚠️ A FROZEN ARTEFACT CLAIMS MORE TAMPER-EVIDENCE THAN THE LEDGER DELIVERS. Ruling 4: "
        "'DO fail it if any docstring, comment or artefact claims more than that.'\n  "
        + "\n  ".join(hits)
    )


def test_NO_ARTEFACT_CLAIMS_THE_MODELS_REPRODUCE_THE_RUN(repo_root: Path) -> None:
    """⚠️ **Hard rule 10's scope, stated exactly, because the looser claim is false.**

    The **world, the ledger schema, the scorer and the replay** are byte-identical from the
    same seed and are tested to be. **Model output is NOT** — the attacker runs at
    temperature 0.7 against a hosted provider. So `make eval`'s claim is *"every number
    regenerates from the stored ledgers"*, which is true, checkable and enough.

    `CLAUDE.md` hard rule 10 names the downstream risk in terms: *"Do not write, and do not
    let the README write, that re-running the models reproduces the run."* The README is
    C19's; **the frozen artefacts are this chunk's**, and they are pinned here.
    """
    documents = frozen_documents(repo_root)

    # ── DIRECTION 1: the scope is STATED where the run is described ──────────────────
    for name in ("PROTOCOL.md", "HOLES.md", "INVARIANTS.md"):
        flat = re.sub(r"\s+", " ", documents[name].replace("**", "").replace("*", "")).lower()
        required = {
            "model output is not": "the negative half, said outright",
            "temperature 0.7": "the reason, not an assertion",
            "byte-identical": "what IS determined",
            "scorer": "one of the four things that are",
            "replay": "another of the four",
        }
        missing = [f"{k!r} ({why})" for k, why in required.items() if k not in flat]
        assert not missing, (
            f"{name} no longer states the determinism ceiling. Missing: " + "; ".join(missing)
        )

    # ── DIRECTION 2: the looser claim is made nowhere ────────────────────────────────
    hits = overclaim_hits(documents, _DETERMINISM_OVERCLAIMS)
    assert not hits, (
        "⚠️ A FROZEN ARTEFACT CLAIMS THE MODELS REPRODUCE THE RUN. Hard rule 10 forbids it, "
        "and the attacker's temperature is 0.7.\n  " + "\n  ".join(hits)
    )


@pytest.mark.parametrize(
    "phrases,planted",
    [
        (
            _TAMPER_OVERCLAIMS,
            "The ledger is hash-chained, so any alteration is detected and the audit log "
            "can be trusted end to end by anyone who reads it.",
        ),
        (
            _DETERMINISM_OVERCLAIMS,
            "Every episode is seeded, so re-running the models reproduces the published "
            "run exactly, on any machine, at no cost.",
        ),
    ],
    ids=["tamper-evidence", "determinism"],
)
def test_the_OVERCLAIM_SCANNER_FIRES_at_a_planted_claim(
    phrases: tuple[str, ...], planted: str
) -> None:
    """⚠️ **Both scanners, fired.** *A release gate that has never gone red is only decorative.*

    The first planted sentence is **mutant `M39` in prose** — the claim that survived the
    whole 159-test suite once already. The second is the sentence hard rule 10 exists to keep
    out of the README.

    ⚠️ **AND THE NEGATIVE CONTROL RUNS BESIDE IT:** the same sentence, wrapped in a
    disclaimer, must come back **clean**. Without it this test would pass just as happily
    against a scanner that flags everything.
    """
    assert overclaim_hits({"planted.md": planted}, phrases), (
        "the scanner did not fire on a planted overclaim, so it is decoration."
    )
    disclaimed = f"This project does not claim the following, which is FALSE: {planted}"
    assert not overclaim_hits({"planted.md": disclaimed}, phrases), (
        "the scanner fires on a DISCLAIMED quotation, so an honest artefact could not quote "
        "a false sentence in order to reject it — which is what the honest ones do."
    )


# ======================================================================================
# The freeze's own preconditions — stated as tests so they cannot be forgotten at the tag.
# ======================================================================================


def test_NO_FROZEN_ARTEFACT_IS_MISSING_BEFORE_THE_TAG_IS_CUT(repo_root: Path) -> None:
    """`CONTEXT.md` §15.0's frozen set is **exactly five files plus `config/`**, and all five
    must exist before `prereg-v1` can mean anything.

    ⚠️ **`INCIDENTS.md` IS DELIBERATELY NOT IN THAT SET.** It is *snapshotted* by the tag and
    **explicitly continues to grow**: freezing the failure-recovery deliverable would
    guarantee that no failure from the build itself could ever be recorded.
    """
    missing = [name for name in FROZEN_FILES if not (repo_root / name).is_file()]
    assert not missing, f"frozen artefacts that do not exist: {missing}"
    assert (repo_root / "config").is_dir(), "config/ — the sixth member — does not exist."
    assert (repo_root / "INCIDENTS.md").is_file(), (
        "INCIDENTS.md must exist and must NOT be in FROZEN_FILES; it is snapshotted, not frozen."
    )
    assert "INCIDENTS.md" not in FROZEN_FILES


def test_the_undetermined_values_are_NAMED_in_PROTOCOL_md_rather_than_left_silent(
    repo_root: Path,
) -> None:
    """⚠️ **Hard rule 11's shape, applied to a set of VALUES instead of a set of episodes.**

    `prereg-v1` may not be cut while the pilot's N branch and the calibration's void
    threshold are sentinels — *"a pre-registration that describes things which do not yet
    exist is theatre"* (`CONTEXT.md` §15). The failure mode this closes is not that they are
    outstanding; it is that they could be outstanding **and unmentioned**, so a reader of the
    protocol could not tell the freeze was incomplete.

    So: **every declared sentinel in `config/` is named in `PROTOCOL.md`, by its key.**
    """
    protocol_text = (repo_root / "PROTOCOL.md").read_text(encoding="utf-8")
    outstanding = cfg.outstanding_sentinels()
    assert outstanding, (
        "no sentinels remain in config/. If the pilot and calibration have run, this test's "
        "premise is gone and it should be replaced by one asserting the VALUES, not the gap."
    )
    unnamed = [
        f"{name}.yaml:{dotted} ({sentinel})"
        for name, dotted, sentinel in outstanding
        if dotted not in protocol_text
    ]
    assert not unnamed, (
        "PROTOCOL.md does not name every undetermined config value, so a reader cannot tell "
        "which parts of the freeze are still owed:\n  " + "\n  ".join(unnamed)
    )


def test_PROTOCOL_md_carries_the_CORPUS_PINS_that_Q032_ruled_it_must(
    repo_root: Path,
) -> None:
    """⚠️ **`Q-032`, RULED: the corpus pins become part of what the pre-registration ASSERTS.**

    Before this, `make check-prereg` hashed the inputs to every published number **except**
    `CONTEXT.md` §11.3's corpus-versus-improvisation split — *"that asymmetry is not
    defensible in a project whose freeze is its central claim."*

    ⚠️ **The ruling does NOT add `corpora/` to §15.0's frozen set**, which stays exactly five
    files plus `config/`. Both halves are asserted: the pins are present, **and** the frozen
    set has not silently grown.
    """
    protocol_text = (repo_root / "PROTOCOL.md").read_text(encoding="utf-8")
    index = json.loads((repo_root / "corpora" / "seed_index.json").read_text(encoding="utf-8"))

    missing: list[str] = []
    for source in index["sources"]:
        for field in ("pin", "sha256"):
            if source[field] not in protocol_text:
                missing.append(f"{source['corpus']} {source['path']}: {field} {source[field]}")
    assert not missing, (
        "PROTOCOL.md is missing corpus pins that Q-032's ruling requires it to carry:\n  "
        + "\n  ".join(missing)
    )
    assert "corpora/" not in FROZEN_FILES, "the frozen set must stay five files plus config/."


def test_the_DEGRADATION_RECORD_in_PROTOCOL_md_matches_INCIDENTS_md(
    repo_root: Path,
) -> None:
    """⚠️ **A protocol that describes an unfired plan is not the protocol — and a protocol that
    describes a rung nobody fired is worse, because it is a cut this project never paid for.**

    `PROCESS.md` §14 requires every cut to be recorded in `INCIDENTS.md` **at the moment it is
    made**, with its time and reason. So the artefact's rung table is checked against
    `INCIDENTS.md` itself: a rung `PROTOCOL.md` calls FIRED must have an entry, and a rung it
    calls NOT FIRED must not.

    ⚠️ **This test is why `Q-099` exists.** The C14 build prompt asserted that rungs 4 and 6
    had been fired; `INCIDENTS.md` carries entries for rungs **1, 3 and 5 only**, and
    `PROCESS.md` §14 reads *"NOT FIRED"* for 2, 4 and 6. The session stopped rather than
    writing an unfired cut into a frozen artefact, and this is the check that would catch it
    being written later.
    """
    incidents = (repo_root / "INCIDENTS.md").read_text(encoding="utf-8")
    protocol_text = (repo_root / "PROTOCOL.md").read_text(encoding="utf-8")

    fired_in_incidents = {
        int(number)
        for number in re.findall(r"DEGRADATION RUNG (\d) FIRED", incidents)
    }
    # ⚠️⚠️ **FLIPPED {1,3,5} -> {1,3,4,5} BY ARCH LANES 1 (`6d1a94f3`), 2026-09-04, CITING THE
    # OPERATOR'S RULING OF THAT DATE: "RUNG 4 FIRES. RUNGS 2 AND 6 DO NOT."**
    #
    # ⚠️ **THIS TEST ASKED TO BE FLIPPED, IN ITS OWN WORDS**, and that is why the flip is not a
    # weakening (hard rule 6). Its message reads: *"the set of rungs INCIDENTS.md records as
    # fired has changed. That is legitimate — a rung may be fired — but PROTOCOL.md is a FROZEN
    # artefact and its table must be re-checked by a human, not by this assertion."* **The human
    # re-check happened**: the ruling is recorded verbatim in `QUESTIONS.md` BEFORE any file was
    # touched (hard rule 5), `INC-144` was written at the moment of the cut with the time and the
    # reason, and `PROTOCOL.md` §5.1, §5.2 and §3.2 were all updated in the same commit.
    #
    # ⚠️ **AND THE FLIP IS PROVABLY MEANINGFUL — it FAILS on the old artefacts.** `INCIDENTS.md`
    # at `b60e198` carries `DEGRADATION RUNG` entries for 1, 3 and 5 only; this assertion run
    # against that file yields `{1,3,5} != {1,3,4,5}` and goes RED. It is a real flip, not a
    # widened set that would accept anything.
    #
    # ⚠️ **AND `prereg-v1` DOES NOT RESOLVE**, verified as that session's first act, so
    # `PROTOCOL.md` was not yet frozen when it was amended — which `PROCESS.md` §14 rung 4 asks
    # for in terms: *"Fire it BEFORE `prereg-v1` if at all possible."*
    assert fired_in_incidents == {1, 3, 4, 5}, (
        "the set of rungs INCIDENTS.md records as fired has changed. That is legitimate — a "
        "rung may be fired — but PROTOCOL.md is a FROZEN artefact and its table must be "
        f"re-checked by a human, not by this assertion. Found: {sorted(fired_in_incidents)}"
    )

    # ⚠️ ANCHOR ON THE SECTION, NOT ON THE ROW SHAPE. `| **1** | ... |` also matches the ARMS
    # table, and a rung check that silently scored arm 1 as "rung 1" would be the exact class
    # of defect this file exists to catch. The first draft of this test did precisely that,
    # and the assertion below is what caught it.
    section = re.search(
        r"^## 5\. THE DEGRADATION RECORD.*?(?=^## )", protocol_text, re.MULTILINE | re.DOTALL
    )
    assert section, "PROTOCOL.md has no degradation-record section to check."
    rung_rows = re.findall(r"^\|\s*\*\*(\d)\*\*\s*\|(.+)$", section.group(0), re.MULTILINE)
    assert len(rung_rows) == 6, f"PROTOCOL.md's rung table has {len(rung_rows)} rows, not 6."
    assert [n for n, _ in rung_rows] == list("123456"), (
        f"PROTOCOL.md's rung table is not rungs 1-6 in order: {[n for n, _ in rung_rows]}"
    )
    for number, row in rung_rows:
        claims_fired = "FIRED" in row and "NOT FIRED" not in row
        really_fired = int(number) in fired_in_incidents
        assert claims_fired == really_fired, (
            f"PROTOCOL.md's rung {number} says "
            f"{'FIRED' if claims_fired else 'NOT FIRED'} and INCIDENTS.md says "
            f"{'FIRED' if really_fired else 'NOT FIRED'}. A cut is an act with a time, a "
            "reason and an entry written at the moment it was made — never a transcription."
        )
