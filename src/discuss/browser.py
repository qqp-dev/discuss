"""[COVERAGE-EXEMPT] Persistent browser context + manual-login pause (FR-002, FR-003).

Wraps Playwright's ``launch_persistent_context`` so the tool reuses the operator's OWN
human-authenticated browser session — no credentials are ever stored, read, or typed
(FR-002, Constitution P-I). The login screen is recognised by the pure ``is_login_page``
predicate (in ``portal_parse``, unit-tested against the saved login fixture); on the login
page this module PAUSES and prompts the operator to log in by hand, and never automates the
login form (FR-003).

This module is coverage-exempt: it is honestly exercisable only against a live browser and
the login-gated portal, which the Respectful-guest principle forbids us from automating in
CI. Its behaviour is verified by the operator checklist in ``docs/SELECTOR-CAPTURE.md``
(the login-pause path in T019), not by unit tests. All PURE logic it relies on
(``is_login_page``) lives in ``portal_parse`` and IS unit-tested.
"""

from __future__ import annotations

from discuss.errors import NotAuthenticated
from discuss.portal_parse import is_login_page


def open_persistent_context(profile_dir):
    """Launch a persistent Chromium context bound to ``profile_dir``; return (context, page).

    The persistent profile holds whatever session the operator established by logging in
    once by hand — this function never reads or writes a credential (FR-002). Playwright is
    imported lazily so importing this module (and, transitively, ``portal_parse``) stays
    light and does not require a browser to be installed.
    """
    from playwright.sync_api import sync_playwright

    playwright = sync_playwright().start()
    context = playwright.chromium.launch_persistent_context(str(profile_dir), headless=False)
    page = context.pages[0] if context.pages else context.new_page()
    return context, page


def ensure_logged_in(page, announce=print, wait=input):
    """Pause for manual login while the current page is the login screen (FR-003).

    Human-paced (Constitution P-I): announce, wait for the operator to press Enter, then
    re-check the predicate — there is NO tight retry loop and NO attempt cap, because each
    iteration blocks on the operator. Raises ``NotAuthenticated`` only if the operator
    gives up (signals EOF / Ctrl-D at the prompt). Never reads or types a credential.

    ``announce``/``wait`` are injected so the pause UX is driven by the operator; the live
    behaviour is verified in T019.
    """
    while is_login_page(page.url, page.content()):
        announce(
            "Please log in to the portal in the opened browser window, then press Enter "
            "here to continue (or Ctrl-D to abort)."
        )
        try:
            wait("")
        except EOFError as exc:
            raise NotAuthenticated("operator aborted manual login") from exc
    return page
