"""T024 — no-mock entry-point smoke gate (SC-006, FR-001).

The layer Escalation #1 lacked: drive the REAL entry-point wiring — ``Config.load(
_load_overrides()) → run(...)`` — to a *defined* state, stubbing ONLY ``browser_factory``
at the outermost (live-browser) boundary. No fake of any internal seam. The fatal
``IndexError`` that passed every other gate lived precisely in the ``Config.load → run``
seam the orchestrator fakes replaced; this test exercises that seam for real, so "the
program starts and reaches a defined state" is now gated — not just unit fakes.
"""

import datetime as dt

import pytest

from discuss import cli
from discuss.errors import NoUpcomingDiscussion


class _FakePage:  # an outermost-boundary stub: a logged-in portal with no discussions
    def content(self):
        return "<html></html>"


def _stub_browser_factory():
    return (object(), _FakePage())


def test_main_smoke_reaches_defined_state(monkeypatch, tmp_path):
    # SC-006: with a valid config + only the browser stubbed, the REAL Config.load→run
    # reaches a DEFINED state (NoUpcomingDiscussion), proving the seam is wired — not an
    # IndexError. This is the path that died on the first live invocation before the fix.
    monkeypatch.setenv("DISCUSS_TARGET_CLASSES", "_577963_1")
    monkeypatch.setenv("DISCUSS_RUN_ROOT", str(tmp_path))
    from discuss.config import Config

    cfg = Config.load(cli._load_overrides())                    # REAL config gathering

    class _A:                                                   # adapter at the live boundary
        def go_to_discussions(self, page, cid):
            pass

        def list_discussions(self, page):
            return []                                           # → select_soonest_due None

    with pytest.raises(NoUpcomingDiscussion):
        cli.run(config=cfg, browser_factory=_stub_browser_factory, adapter=_A(),
                today=dt.date(2026, 6, 1), ensure_logged_in=lambda p: None)


def test_main_no_class_exits_with_guidance(monkeypatch, capsys):
    # the guard that the original IndexError needed: real main(), no class → rc 2 + guidance.
    monkeypatch.delenv("DISCUSS_TARGET_CLASSES", raising=False)
    assert cli.main() == 2
    assert "DISCUSS_TARGET_CLASSES" in capsys.readouterr().out
