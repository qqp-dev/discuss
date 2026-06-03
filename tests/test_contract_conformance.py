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
