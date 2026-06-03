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
    for name in ("contract.md", "contract-impact.md"):
        p = ROOT / "method" / "schemas" / name
        assert p.is_file(), f"method/schemas/{name} must be vendored by copy (FR-003)"


def test_contract_exists_declares_source_of_truth():
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
    text = _read("constitution.md").lower()
    assert "contract loop" in text, "constitution must declare Contract Loop adoption"
    assert "contract-currency" in text, "must name the contract-currency G3 reviewer"
    assert "contract-impact.md" in text, "must require a per-change contract-impact.md"
    assert "g3" in text, "must name the G3 done-gate"


def test_changelog_has_001_and_002():
    text = _read("CHANGELOG.md")
    assert "001" in text and "discussion-draft-pipeline" in text, "CHANGELOG must record change 001"
    assert "002" in text and "contract-loop-conformance" in text, "CHANGELOG must record change 002"


@pytest.mark.skipif(LINT is None, reason="operator-home lint-contract-impact.sh not on PATH")
def test_001_contract_impact_wellformed():
    d = ROOT / "changes" / "001-discussion-draft-pipeline"
    r = subprocess.run([LINT, str(d)], capture_output=True, text=True)
    assert r.returncode == 0, (r.stderr or r.stdout)


def test_001_contract_impact_is_nonempty_list():
    text = _read("changes/001-discussion-draft-pipeline/contract-impact.md")
    assert "none (internal-only)" not in text, "001 changed behavior — must not declare none (B2 trap)"
    assert "section:" in text and "kind:" in text, "001 declaration must be a non-empty impact list"


@pytest.mark.skipif(LINT is None, reason="operator-home lint-contract-impact.sh not on PATH")
def test_002_contract_impact_wellformed():
    d = ROOT / "changes" / "002-contract-loop-conformance"
    r = subprocess.run([LINT, str(d)], capture_output=True, text=True)
    assert r.returncode == 0, (r.stderr or r.stdout)


def test_001_learnings_references_contract_impact():
    text = _read("changes/001-discussion-draft-pipeline/learnings.md")
    assert "contract-impact.md" in text, "001 learnings must reference the authored declaration"
