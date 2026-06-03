import json
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LINT = shutil.which("lint-contract-impact.sh")


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_contract_schemas_vendored():
    # Catches: a regression where the schema is "adopted" by runtime reference to
    # portable-core instead of vendored by copy (FR-003) — deleting either copy reds this.
    for name in ("contract.md", "contract-impact.md"):
        p = ROOT / "method" / "schemas" / name
        assert p.is_file(), f"method/schemas/{name} must be vendored by copy (FR-003)"


def test_contract_exists_declares_source_of_truth():
    # Catches: a contract.md that exists but fails its load-bearing self-declaration —
    # missing the source-of-truth claim, missing the explicit non-subordination clause
    # (I3-), or stripped of a behavior-narrative section (I1–I3).
    contract = ROOT / "contract.md"
    assert contract.is_file(), "root contract.md must exist (I1)"
    text = contract.read_text(encoding="utf-8").lower()
    assert "source of truth" in text, "contract must name itself the source of truth (I3+)"
    # I3 negative limb (presence of the explicit non-subordination declaration):
    assert ("not subordinate to the archive" in text
            or "never subordinate to the archive" in text), \
        "contract must explicitly declare it is not subordinate to the archive (I3-)"
    # I2: reads as current truth — sanity-check the behavior-narrative sections are present.
    for marker in ("pipeline", "safety", "adapter"):
        assert marker in text, f"contract must describe the {marker} surface (I2)"


def test_constitution_declares_contract_loop():
    # Catches: a future change that drops the Contract Loop from project policy — losing
    # the adoption declaration, the contract-currency G3 gate, or the per-change
    # contract-impact.md requirement, which would let drift back in silently (FR-004).
    text = _read("constitution.md").lower()
    assert "contract loop" in text, "constitution must declare Contract Loop adoption"
    assert "contract-currency" in text, "must name the contract-currency G3 reviewer"
    assert "contract-impact.md" in text, "must require a per-change contract-impact.md"
    assert "g3" in text, "must name the G3 done-gate"


def test_changelog_has_001_and_002():
    # Catches: a CHANGELOG.md that loses (or never recorded) a shipped change's archive
    # entry — the human-readable archive half going stale against the git history (FR-005).
    text = _read("CHANGELOG.md")
    assert "001" in text and "discussion-draft-pipeline" in text, "CHANGELOG must record change 001"
    assert "002" in text and "contract-loop-conformance" in text, "CHANGELOG must record change 002"


@pytest.mark.skipif(LINT is None, reason="operator-home lint-contract-impact.sh not on PATH")
def test_001_contract_impact_wellformed():
    # Catches: a malformed 001 declaration (missing change/impact/rationale field, a bad
    # kind, an entry missing its note) — the D1 floor that must pass before any reviewer.
    d = ROOT / "changes" / "001-discussion-draft-pipeline"
    r = subprocess.run([LINT, str(d)], capture_output=True, text=True)
    assert r.returncode == 0, (r.stderr or r.stdout)


def test_001_contract_impact_is_nonempty_list():
    # Catches: the B2 mis-declaration trap — 001 declaring `none (internal-only)` (or an
    # empty list) despite having changed real acceptance-asserted behavior.
    text = _read("changes/001-discussion-draft-pipeline/contract-impact.md")
    assert "none (internal-only)" not in text, "001 changed behavior — must not declare none (B2 trap)"
    assert "section:" in text and "kind:" in text, "001 declaration must be a non-empty impact list"


@pytest.mark.skipif(LINT is None, reason="operator-home lint-contract-impact.sh not on PATH")
def test_002_contract_impact_wellformed():
    # Catches: a malformed 002 declaration — this change dogfooding the loop must itself
    # carry a well-formed contract-impact.md (D1), or the gate is hypocritical.
    d = ROOT / "changes" / "002-contract-loop-conformance"
    r = subprocess.run([LINT, str(d)], capture_output=True, text=True)
    assert r.returncode == 0, (r.stderr or r.stdout)


def test_001_learnings_references_contract_impact():
    # Catches: 001's learnings reverting to the recorded `N/A` contract-collapse note
    # without the forward reference to the now-authored declaration (FR-009).
    text = _read("changes/001-discussion-draft-pipeline/learnings.md")
    assert "contract-impact.md" in text, "001 learnings must reference the authored declaration"


def test_001_currency_verdict_recorded_pass():
    # Catches: the 001 collapse being marked done without the independent currency gate
    # having run-and-passed — a missing evidence file, or a recorded BLOCK/non-PASS (FR-008).
    p = ROOT / "changes" / "002-contract-loop-conformance" / "evidence-001-currency-verdict.json"
    assert p.is_file(), "currency verdict evidence must be recorded (FR-008)"
    verdict = json.loads(p.read_text(encoding="utf-8"))
    assert verdict.get("verdict") == "PASS", f"currency reviewer must PASS on the 001 collapse, got {verdict.get('verdict')}"


def test_no_src_modules_changed():
    # Catches: scope creep — a conformance change that strays into src/ production code,
    # breaking the docs/methodology-only blast-radius guarantee (FR-010). Green from the
    # start; reds only if a future edit on this branch touches src/.
    base = subprocess.run(["git", "merge-base", "HEAD", "main"],
                          cwd=ROOT, capture_output=True, text=True)
    if base.returncode != 0 or not base.stdout.strip():
        pytest.skip("no merge-base with main resolvable")
    diff = subprocess.run(["git", "diff", "--name-only", base.stdout.strip(), "HEAD"],
                          cwd=ROOT, capture_output=True, text=True)
    changed = [f for f in diff.stdout.splitlines() if f.startswith("src/")]
    assert changed == [], f"conformance change must touch no src/ module, found: {changed}"
