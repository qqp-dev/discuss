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
from discuss.config import Config
from discuss.errors import NoUpcomingDiscussion, NotAuthenticated


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
    # Isolate the no-config case even when the suite intentionally supplies a real root .env.
    monkeypatch.delenv("DISCUSS_TARGET_CLASSES", raising=False)
    monkeypatch.setattr(cli, "_load_overrides", lambda env=None: {})
    assert cli.main() == 2
    assert "DISCUSS_TARGET_CLASSES" in capsys.readouterr().out


# --- T029: auth re-sequenced AFTER navigation, with one in-context retry (Esc#2) ----------
#
# No-mock smoke EXTENSION (SC-006 discipline): only the outermost live boundary (the stub
# adapter standing in for the live portal) is faked — the REAL `cli.run` orchestration drives
# the new navigate → (login? pause + retry once) → proceed seam. The pre-navigation auth check
# (which a fresh about:blank page could never use to see a post-navigation SSO redirect) is
# gone; this gates the seam that replaces it.


def test_auth_pause_is_post_navigation_with_retry(tmp_path):
    # the manual-login pause fires AFTER the first navigation, the navigation is retried
    # EXACTLY once in-context, then the run proceeds to a defined state — and NO auth check
    # runs before the first navigation (the first recorded event is a navigate, not a pause).
    events = []

    class _A:
        def __init__(self):
            self.nav = 0

        def go_to_discussions(self, page, cid):
            self.nav += 1
            events.append("navigate")
            if self.nav == 1:
                raise NotAuthenticated("portal redirected to login")
            # second navigation (post-login) succeeds

        def list_discussions(self, page):
            return []  # → NoUpcomingDiscussion: a DEFINED downstream state

    def pause(page):
        events.append("pause")

    cfg = Config.load(
        {"target_classes": ["_x"], "run_root": tmp_path, "confirm": False, "editor_cmd": ["true"]}
    )
    a = _A()
    with pytest.raises(NoUpcomingDiscussion):
        cli.run(config=cfg, browser_factory=lambda: (object(), _FakePage()), adapter=a,
                today=dt.date(2026, 6, 1), ensure_logged_in=pause)
    assert events == ["navigate", "pause", "navigate"]  # pause AFTER nav; exactly one retry
    assert a.nav == 2


def test_login_landing_routes_to_pause_not_selector_miss(tmp_path):
    # a login landing routes to the manual-login PAUSE path (not surfaced as a SelectorMiss);
    # if the operator never authenticates, NotAuthenticated propagates after the single retry.
    events = []

    class _A:
        def go_to_discussions(self, page, cid):
            events.append("navigate")
            raise NotAuthenticated("still on login")  # login persists across the retry

    def pause(page):
        events.append("pause")

    cfg = Config.load(
        {"target_classes": ["_x"], "run_root": tmp_path, "confirm": False, "editor_cmd": ["true"]}
    )
    with pytest.raises(NotAuthenticated):
        cli.run(config=cfg, browser_factory=lambda: (object(), object()), adapter=_A(),
                today=dt.date(2026, 6, 1), ensure_logged_in=pause)
    # paused (not errored as a SelectorMiss) and retried exactly once before giving up
    assert events == ["navigate", "pause", "navigate"]
