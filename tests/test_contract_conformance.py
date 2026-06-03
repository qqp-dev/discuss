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
