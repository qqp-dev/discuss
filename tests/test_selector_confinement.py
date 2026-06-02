"""FR-013 / SC-002: portal selectors must live in exactly one module — the adapter.

This is a structural invariant test, not a behavioural one: it falsifiably guards that no
module other than ``portal_adapter`` declares a ``SELECTORS`` table. Adding ``SELECTORS``
to any other ``src/discuss`` module turns this red. Runs without the live portal.
"""

import pathlib

_SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "discuss"


def test_selectors_confined_to_adapter():
    # FR-013/SC-002: a portal markup change must be a one-file fix, so the selector table
    # may exist only in portal_adapter.py. Pure consumers import the selector *values* by
    # their named constants; none re-declares the table.
    offenders = [
        p.name
        for p in _SRC.glob("*.py")
        if p.name != "portal_adapter.py" and "SELECTORS" in p.read_text(encoding="utf-8")
    ]
    assert offenders == []
