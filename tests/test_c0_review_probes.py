"""KEPT PROBES added by the C0 ADVERSARIAL REVIEW (SESSION-TOKEN ``52f5307b``).

**These are probes, not fixes.** A review session fixes nothing (`CLAUDE.md` §1); it may add
kept tests, and `PROCESS.md` §12.1's `code` review asks for mutants, with a surviving mutant
closed by a **kept probe that stays in the repository.**

Nineteen mutants were applied to `check_roles.py`, `config.py` and `spec_constants.py`, each
one committed so that ``test_the_object_store_and_the_working_tree_agree`` was satisfied —
the state a real defect actually lives in. **Twelve survived**, every one of them leaving
``make test`` at exactly *41 passed, 1 skipped, 2 deselected* and ``make check-roles`` at
exit 0. The reason is uniform: the suite asserts that each check **passes on this
repository** — a state in which every check passes trivially — and almost never that a check
**fires on input that should break it**.

Each probe below names the mutant it kills. Every one PASSES against the reviewed code, so
a later session can re-apply the mutation and watch the probe do its job.

⚠️ **The BLOCKERs this review found are NOT closed here.** A probe detects; only a fix
closes. See `docs/reviews/REVIEW_C0.md`.

Idiom follows `tests/test_repo_invariants.py`: a throwaway git repository under ``tmp_path``,
never the repository under review.
"""

from __future__ import annotations

import subprocess as sp

import pytest
import yaml

from whetstone_gate import check_roles
from whetstone_gate import config as cfg


def _results(group):
    return {r.check: r for r in group}


def _init(path, gitattributes: bytes | None = b"* text=auto eol=lf\n"):
    path.mkdir(parents=True, exist_ok=True)
    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "fixture@example.invalid"],
        ["git", "config", "user.name", "fixture"],
        ["git", "config", "core.autocrlf", "false"],
    ):
        sp.run(cmd, cwd=path, check=True, capture_output=True)
    if gitattributes is not None:
        (path / ".gitattributes").write_bytes(gitattributes)
    return path


def _commit(path, message="fixture"):
    sp.run(["git", "add", "-A"], cwd=path, check=True, capture_output=True)
    sp.run(["git", "commit", "-qm", message], cwd=path, check=True, capture_output=True)


# =======================================================================================
# check_roles — every check fired against input that SHOULD break it
# =======================================================================================


def test_b1_fires_on_a_tracked_env_file(tmp_path):
    """B1 must FAIL when a ``.env`` is tracked. Kills the mutant that stops detecting one.

    `CLAUDE.md` §4: *"Never read, print, echo or commit `.env`."* The suite only ever
    asserted ``B1 … .ok is True`` against a repository that has no tracked ``.env``, so
    replacing the predicate with ``f == ".environment"`` left `make test` and
    `make check-roles` both green (mutant M13).
    """
    repo = _init(tmp_path / "r")
    (repo / ".env.example").write_bytes(b"GROQ_API_KEY=\n")
    (repo / ".env").write_bytes(b"GROQ_API_KEY=placeholder-not-a-real-key\n")
    _commit(repo)

    b1 = _results(check_roles.check_secrets(repo))["B1 no .env tracked"]
    assert b1.ok is False, f"B1 did not fire on a tracked .env: {b1.detail}"
    assert ".env" in b1.detail


@pytest.mark.parametrize(
    "label, payload",
    [
        ("Groq API key", "gsk_" + "a" * 40),
        ("Google API key", "AIza" + "B" * 35),
        ("Razorpay LIVE key", "rzp_live_" + "c" * 14),
        ("Razorpay test key", "rzp_test_" + "d" * 14),
        ("OpenAI key", "sk-" + "e" * 40),
        ("GitHub token", "ghp_" + "f" * 36),
        ("AWS access key id", "AKIA" + "G" * 16),
        # Assembled from two halves so this file does not trip C1 on itself.
        ("private key block", "-----BEGIN " + "RSA PRIVATE KEY-----"),
    ],
)
def test_c1_fires_through_check_secrets_for_every_pattern(tmp_path, label, payload):
    """Every pattern must be caught **through `check_secrets`**, not merely by its regex.

    ``test_the_secret_scanner_actually_fires`` exercises five of the eight regexes directly
    via ``re.search``. It therefore stays green when the *scanner* stops using them:
    truncating the loop to ``SECRET_PATTERNS[:1]`` — Google, Razorpay, OpenAI, GitHub, AWS
    and private-key blocks all unscanned — survived the whole suite (mutant M17).

    These payloads are synthetic filler. None is, or resembles, a real credential.
    """
    repo = _init(tmp_path / "r")
    (repo / ".env.example").write_bytes(b"GROQ_API_KEY=\n")
    (repo / "leak.txt").write_text(f"token = {payload}\n", encoding="utf-8")
    _commit(repo)

    c1 = _results(check_roles.check_secrets(repo))[
        "C1 no secret-shaped string in any tracked file"
    ]
    assert c1.ok is False, f"C1 did not fire on a {label}: {c1.detail}"
    assert label in c1.detail


def test_e1_fires_on_a_commit_carrying_an_unissued_token(tmp_path):
    """E1 must FAIL on a well-formed token that `QUESTIONS.md` never issued.

    `PROCESS.md` §7a makes E1 the clause that catches a forged credential in the audit
    trail. On this repository **no commit carries a trailer `_TOKEN_TRAILER` can parse**,
    so ``used`` is empty and E1's verdict is identical however its predicate is written:
    inverting it to ``if t in issued`` survived (M11), and so did widening the regex to any
    hex length (M12). This probe gives E1 real input.
    """
    repo = _init(tmp_path / "r")
    (repo / ".env.example").write_bytes(b"GROQ_API_KEY=\n")
    (repo / "QUESTIONS.md").write_text(
        "## Session tokens\n\n| Token | Chunk | Role | Issued |\n|---|---|---|---|\n"
        "| `aaaaaaaa` | C0 | BUILD | 2026-08-30 |\n",
        encoding="utf-8",
    )
    _commit(repo)
    (repo / "note.md").write_text("second\n", encoding="utf-8")
    sp.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    sp.run(
        ["git", "commit", "-qm", "forged\n\nSession-Token: bbbbbbbb"],
        cwd=repo, check=True, capture_output=True,
    )

    e1 = _results(check_roles.check_session_tokens(repo))[
        "E1 no commit carries an UNISSUED token"
    ]
    assert e1.ok is False, (
        f"E1 passed over a Session-Token that appears in no QUESTIONS.md row: {e1.detail}"
    )
    assert "bbbbbbbb" in e1.detail


def test_a2_fires_when_gitattributes_is_not_in_the_first_commit(tmp_path):
    """A2 must FAIL when ``.gitattributes`` arrives late.

    `PROCESS.md` §6a: it is fixable **only** in the first commit, and after that the
    fingerprint property is unrecoverable without a history rewrite §7 forbids. The suite
    asserted only that A2 passes on this repository, so ``added[-1] -> added[0]`` (M7) and
    substituting a fake root commit (M20) both survived.
    """
    repo = _init(tmp_path / "r", gitattributes=None)
    (repo / "a.txt").write_bytes(b"hello\n")
    _commit(repo, "root without .gitattributes")
    (repo / ".gitattributes").write_bytes(b"* text=auto eol=lf\n")
    _commit(repo, "late .gitattributes")

    a2 = _results(check_roles.check_gitattributes(repo))[
        "A2 .gitattributes in the FIRST commit"
    ]
    assert a2.ok is False, f"A2 passed on a late .gitattributes: {a2.detail}"


def test_a2_reads_the_EARLIEST_add_not_the_latest(tmp_path):
    """A2 must ask *"was it in the first commit"*, which is the OLDEST adding commit.

    ``git log --diff-filter=A`` lists adding commits newest-first, so the root-commit test is
    ``added[-1]``. A file that WAS in the root commit, was later deleted and re-added, still
    satisfies `PROCESS.md` §6a — the property held when it mattered. Reading ``added[0]``
    instead would call that repository broken (mutant M7), and the previous probe could not
    tell the two apart because its fixture had only one adding commit.
    """
    repo = _init(tmp_path / "r")
    (repo / "a.txt").write_bytes(b"hello\n")
    _commit(repo, "root WITH .gitattributes")
    (repo / ".gitattributes").unlink()
    _commit(repo, "delete it")
    (repo / ".gitattributes").write_bytes(b"* text=auto eol=lf\n")
    _commit(repo, "re-add it")

    adds = sp.run(
        ["git", "log", "--diff-filter=A", "--format=%H", "--", ".gitattributes"],
        cwd=repo, check=True, capture_output=True, text=True,
    ).stdout.split()
    assert len(adds) == 2, f"the fixture has {len(adds)} adding commit(s), so it proves nothing"

    a2 = _results(check_roles.check_gitattributes(repo))[
        "A2 .gitattributes in the FIRST commit"
    ]
    assert a2.ok is True, (
        "A2 read the LATEST adding commit rather than the earliest. The file WAS in the root "
        f"commit, which is the property §6a asks about. detail: {a2.detail}"
    )


def test_the_token_trailer_matches_exactly_eight_hex_and_nothing_else(tmp_path):
    """``_TOKEN_TRAILER`` must accept **exactly** 8 hex characters.

    The architect ruled on 2026-08-30 (QUESTIONS.md Q-014) that tokens are 8 random hex from
    now on and that **the regex is NOT widened**. Nothing pinned that: loosening it to
    ``{1,}`` survived the whole suite (mutant M12). This probe holds the ruling in place.

    ⚠️ It pins the STRICT matcher only. Q-014's open half — that a trailer which is *present
    but malformed* should be a FAILURE rather than an absence (`REVIEW_C0.md` F4) — is closed
    by a **separate, permissive** pattern feeding a new check, not by widening this one.
    """
    accept = ["deadbeef", "DEADBEEF", "00000000", "52f5307b"]
    reject = [
        "deadbee",                    # 7
        "deadbeef0",                  # 9
        "WG-2026-08-30-CTX-13.4-A",   # the shape that is actually in this repository's log
        "not-hex!",
        "",
    ]
    body = "some commit subject\n\nSession-Token: {}\n"
    for token in accept:
        assert check_roles._TOKEN_TRAILER.findall(body.format(token)) == [token]
    for token in reject:
        assert check_roles._TOKEN_TRAILER.findall(body.format(token)) == [], (
            f"the strict trailer matcher accepted {token!r}. PROCESS.md §7a specifies 8 hex "
            f"and the Q-014 ruling declined to widen it."
        )


def test_a4_fires_when_a_tracked_path_has_no_regular_file(tmp_path):
    """A4 must FAIL when it could not check every tracked path — hard rule 11's denominator.

    ``b0a4855`` added exactly this guarantee, after finding that the loop skipped such paths
    while printing *"all N tracked file(s)"*. Reverting it to ``not divergent`` survived the
    suite (M9), so the fix had nothing asserting it.
    """
    repo = _init(tmp_path / "r")
    (repo / "kept.md").write_bytes(b"kept\n")
    (repo / "vanished.md").write_bytes(b"gone\n")
    _commit(repo)
    (repo / "vanished.md").unlink()

    a4 = _results(check_roles.check_gitattributes(repo))[
        "A4 working tree and object store hold identical bytes"
    ]
    assert a4.ok is False, (
        f"A4 passed while one tracked path was checked by nothing: {a4.detail}"
    )
    assert "vanished.md" in a4.detail


def test_eol_classification_reports_the_working_tree_side(tmp_path):
    """``_eol_classification`` must report git's ``w/`` verdict, not its ``i/`` one.

    `PROCESS.md` §6a's property is about what git does to the bytes **on checkin**, so the
    working-tree classification is the one A3 must branch on — and the function's own
    docstring says it asks *"how it classifies each tracked path's working-tree content."*
    Switching the prefix to ``i/`` survived the suite (M10): the two agree on every file
    this repository currently holds.
    """
    repo = _init(tmp_path / "r")
    (repo / "note.txt").write_bytes(b"plain text\n")
    _commit(repo)
    # Same path, now binary in the WORKING TREE only. The index still says text.
    (repo / "note.txt").write_bytes(b"\x00binary\r\npayload\r\n")

    eol = sp.run(
        ["git", "ls-files", "--eol", "note.txt"],
        cwd=repo, check=True, capture_output=True, text=True,
    ).stdout
    assert "i/lf" in eol and "w/-text" in eol, (
        f"the fixture does not exercise the i/ vs w/ disagreement at all: {eol!r}"
    )

    classification = check_roles._eol_classification(repo)
    assert classification["note.txt"] == "-text", (
        "the check read git's INDEX-side classification. §6a asks what git will do to the "
        f"WORKING-TREE bytes, which is the `w/` field. git says: {eol!r}"
    )


# =======================================================================================
# OF-01 — the lone-CR gap, given a discriminator rather than left as prose
# =======================================================================================


def test_no_tracked_file_is_binary_without_a_nul_byte(repo_root):
    """⚠️ `docs/reviews/OPEN_FINDINGS.md` **OF-01**, made checkable.

    A single stray CR makes git classify an otherwise-textual file ``-text``. It then lands
    in the binary bucket: A3 does not scan it, and A4 cannot fail on it because git converts
    nothing on ``-text`` content. INC-06's and INC-10's defect class then goes green.
    **Reproduced by this reviewer**: a markdown file whose only defect is one lone CR reports
    ``i/-text w/-text``, holds no CRLF pair, and passes both checks.

    The discriminator OF-01 proposes — *"git calls this binary, yet it holds no NUL byte"* —
    is asserted here. It passes on the two dashboard PNGs (both carry NULs in their IHDR) and
    fires on a lone-CR text file. It is **not a second copy of git's heuristic**: it compares
    git's verdict against an independent signal, which is the opposite of hard rule 8's
    circularity.

    ⚠️ **This does not close OF-01.** It detects the condition inside `make test`; it does
    not make `make check-roles` report it, and `check-roles` is what the C0 done-when names.
    """
    tracked = sp.run(
        ["git", "ls-files", "-z"], cwd=repo_root, check=True, capture_output=True
    ).stdout.decode().split("\0")
    classification = check_roles._eol_classification(repo_root)

    suspects = []
    for rel in filter(None, tracked):
        path = repo_root / rel
        if not path.is_file() or classification.get(rel) != "-text":
            continue
        if b"\x00" not in path.read_bytes()[:8000]:
            suspects.append(rel)

    assert not suspects, (
        "git classifies these tracked files as binary although they hold no NUL byte in "
        f"their first 8000 bytes: {suspects}. That is the signature of a file made binary "
        "by stray CR statistics rather than by being binary — and in that state NEITHER "
        "check-roles A3 NOR A4 will look at it (OPEN_FINDINGS OF-01; INCIDENTS INC-06, "
        "INC-10)."
    )


# =======================================================================================
# config — the loader's refusals, fired rather than assumed
# =======================================================================================


def test_load_refuses_a_yaml_that_is_not_a_mapping(tmp_path, monkeypatch):
    """A config file parsing to a list or a scalar is a refusal, not a usable config.

    Replacing the guard with ``if False:`` survived the suite (M4).
    """
    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(tmp_path))
    (tmp_path / "protocol.yaml").write_text("- one\n- two\n", encoding="utf-8")
    with pytest.raises(cfg.ConfigError):
        cfg.load("protocol")


def test_require_refuses_when_the_path_traverses_a_non_mapping(tmp_path, monkeypatch):
    """``require("a.b")`` where ``a`` is a scalar is a MISSING value, never ``None``.

    Hard rule 9: *"a missing value is a hard refusal, never a silent fallback."* A mutant
    returning ``None`` here instead of raising survived the suite (M6).
    """
    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(tmp_path))
    (tmp_path / "protocol.yaml").write_text("a: 3\n", encoding="utf-8")
    with pytest.raises(cfg.MissingRequiredValue):
        cfg.load("protocol").require("a.b")


def test_sentinels_are_found_inside_lists(tmp_path, monkeypatch):
    """The sweep must recurse into LISTS, or `config/lanes.yaml` is invisible to it.

    Every lane lives in a YAML list, so the whole operator gate — the check that stopped a
    token being spent against a guessed model id — hangs on this one ``elif``. Replacing it
    with ``elif False:`` survived the suite (M5), because no sentinel currently sits in a
    list: the four ``TODO_OPERATOR`` placeholders it was written for were resolved in
    ``457c5d3``, and with them went the only input that exercised this branch.
    """
    monkeypatch.setenv("WHETSTONE_CONFIG_DIR", str(tmp_path))
    (tmp_path / "lanes.yaml").write_text(
        "lanes:\n  - name: probe-lane\n    api_model_id: TODO_OPERATOR\n", encoding="utf-8"
    )
    assert list(cfg.load("lanes").sentinels()) == [
        ("lanes[probe-lane].api_model_id", "TODO_OPERATOR")
    ]


def test_protocol_yaml_holds_no_null_and_no_empty_string(repo_root):
    """⚠️ A value left BLANK is invisible to the ``TODO_`` sentinel mechanism.

    `src/whetstone_gate/config.py`'s own docstring names the stake: *"if a missing threshold
    silently read as 0.0, every run would clear the void check … and nothing would have
    raised."* The sentinel mechanism catches ``void_threshold_breach_rate:
    TODO_C14_CALIBRATION``. It does **not** catch ``void_threshold_breach_rate:`` — a YAML
    null — which ``require`` returns as ``None``, ``outstanding_sentinels`` does not count,
    `check-roles` F2 reports as *"no undetermined values remain"*, and `make selftest` passes
    over. This probe closes the typo-shaped half of that gap for `protocol.yaml`, where a
    null is never a meaningful value.

    ⚠️ `lanes.yaml` is deliberately **excluded**: ``tpd: null`` there means *"no such limit
    exists"*, which is a documented and separately tested fact about Google's free tier, not
    an omission.
    """
    data = yaml.safe_load(
        (repo_root / "config" / "protocol.yaml").read_text(encoding="utf-8")
    )
    blanks: list[str] = []

    def walk(node, prefix):
        if isinstance(node, dict):
            for key, child in node.items():
                walk(child, f"{prefix}.{key}" if prefix else str(key))
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, f"{prefix}[{index}]")
        elif node is None or (isinstance(node, str) and not node.strip()):
            blanks.append(f"{prefix} = {node!r}")

    walk(data, "")
    assert not blanks, (
        "config/protocol.yaml carries values that are blank rather than determined or "
        f"explicitly undetermined: {blanks}. A blank is NOT a TODO_ sentinel — the loader "
        "returns it as None, outstanding_sentinels() does not count it, check-roles F2 "
        "reports 'no undetermined values remain', and make selftest goes green over it."
    )
