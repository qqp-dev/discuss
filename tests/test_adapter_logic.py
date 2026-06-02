"""T027 — pause-logic & no-retry offline oracles (FR-003, FR-016).

Two offline oracles for behaviour the old plan wrongly left `[no-oracle]`, both tested
against fakes (no live portal), so two more safety/pace criteria stop being waivable:

1. **Login-pause (FR-003):** a fake login page makes ``browser.ensure_logged_in`` prompt and
   pause for *manual* login — never auto-filling a credential — and raise ``NotAuthenticated``
   only when the operator gives up. The live page-recognition residue stays in T026.
2. **No-retry (FR-016 / P-I):** a fake page whose row query returns ``None`` makes
   ``portal_adapter.go_to_discussions`` raise ``SelectorMiss`` after exactly ONE navigation.
"""

import pathlib

import pytest

from discuss import browser, portal_adapter
from discuss.errors import NotAuthenticated, SelectorMiss

_LOGIN_SHELL = (pathlib.Path(__file__).resolve().parent.parent
                / "fixtures" / "login_shell_prerender.html").read_text(encoding="utf-8")


class _LoginPage:
    url = "https://www.phoenix.edu/login"

    def content(self):
        return "<title>University of Phoenix Login</title>"


def test_ensure_logged_in_pauses_on_login_page(monkeypatch):
    # FR-003: a login page makes ensure_logged_in PROMPT/pause; it never auto-fills creds,
    # and gives up (NotAuthenticated) only when the operator declines.
    prompts = []
    monkeypatch.setattr("builtins.input", lambda p="": prompts.append(p) or "q")  # operator quits
    with pytest.raises(NotAuthenticated):
        browser.ensure_logged_in(_LoginPage())
    assert prompts and any("log in" in p.lower() for p in prompts)   # the pause prompt fired


def test_ensure_logged_in_proceeds_once_authenticated(monkeypatch):
    # FR-003: once the operator has logged in (the page is no longer the login screen), the
    # pause loop exits and the run proceeds — pressing Enter ('') continues, never a credential.
    class _TransitioningPage:
        url = "https://vle.phoenix.edu/ultra/courses/_577963_1/engagement"

        def __init__(self):
            self._contents = iter([
                "<title>University of Phoenix Login</title>",   # logged out at first
                "<html>discussions</html>",                      # logged in after the pause
            ])

        def content(self):
            return next(self._contents)

    prompts = []
    monkeypatch.setattr("builtins.input", lambda p="": prompts.append(p) or "")  # press Enter
    page = _TransitioningPage()
    assert browser.ensure_logged_in(page) is page   # returns the page, no NotAuthenticated
    assert len(prompts) == 1                         # paused exactly once, then proceeded


def test_no_retry_loop_on_selector_miss():
    # FR-016/P-I: a selector miss raises after exactly ONE navigation — no retry storm.
    # Post-T030 the adapter waits for render then classifies before raising; this fake models a
    # non-login page that never paints rows (content has no rows AND no login markers → the
    # offline-pinned classify_landing returns 'unknown'), so go_to_discussions must raise
    # SelectorMiss — not NotAuthenticated, and after exactly ONE navigation.
    gotos = []

    class _Page:
        url = "https://vle.phoenix.edu/ultra/courses/_577963_1/engagement"  # NOT a login URL

        def goto(self, url, **kw):
            gotos.append(url)

        def wait_for_selector(self, selector, **kw):
            return None      # the bounded render wait elapses (no element ever paints)

        def content(self):
            return "<html><body>no rows, not the login shell</body></html>"

        def query_selector(self, sel):
            return None      # rows never resolve

    with pytest.raises(SelectorMiss):
        portal_adapter.go_to_discussions(_Page(), "_577963_1")
    assert len(gotos) == 1, "go_to_discussions must not retry-loop on a selector miss"


def test_login_landing_raises_not_authenticated():
    # T030/Esc#2 (offline-pinned): when navigation lands on the (captured, real) pre-render
    # login shell, go_to_discussions raises NotAuthenticated — NOT a SelectorMiss — so the
    # orchestrator can route to the post-navigation manual-login pause (T029). The login
    # *decision* is the offline-pinned classify_landing (T028); this pins the adapter's BRANCH
    # on it, leaving only the live wait-timing for T026. One navigation, no retry.
    gotos = []

    class _LoginLandingPage:
        url = "https://vle.phoenix.edu/ultra/courses/_577963_1/engagement"  # SSO bounce keeps URL

        def goto(self, url, **kw):
            gotos.append(url)

        def wait_for_selector(self, selector, **kw):
            return None      # the login shell's body marker is "painted"; the wait resolves

        def content(self):
            return _LOGIN_SHELL   # the verbatim captured pre-render ForgeRock shell

        def query_selector(self, sel):
            return None

    with pytest.raises(NotAuthenticated):
        portal_adapter.go_to_discussions(_LoginLandingPage(), "_577963_1")
    assert len(gotos) == 1, "a login landing must not retry-loop either"
