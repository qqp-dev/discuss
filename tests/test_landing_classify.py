"""T028 — offline login-shell classification oracle (Esc#2, FR-003/FR-018).

The first live run bounced to a client-rendered ForgeRock SSO login shell and the adapter,
reading the DOM pre-render, saw `<title>Login</title>` + `data-testid="fr-body-image"` and
an empty `appRoot` — NOT the post-render `"University of Phoenix Login"` marker `is_login_page`
used to key on. FR-018's self-snapshot captured that exact shell, so the login-classification
fix is an OFFLINE oracle (the captured shell IS the fixture), not a live residue.
"""

from discuss.portal_parse import classify_landing, is_login_page

# Deliberately NOT a `/login` URL: detection must come from the pre-render BODY markers, since
# the live `page.url` after the SSO bounce was the engagement URL, not a tell-tale login path.
# Keying off the URL alone is exactly what failed to save the first live run.
_ENGAGEMENT_URL = "https://vle.phoenix.edu/ultra/courses/_577963_1/engagement"


def test_classify_prerender_login_shell(login_shell_prerender_html):
    # Esc#2/FR-003: the un-rendered ForgeRock shell classifies as a login page from its
    # pre-render markup — the bug the first live run hit (it read as a selector miss instead).
    assert classify_landing(_ENGAGEMENT_URL, login_shell_prerender_html) == "login"
    assert is_login_page(_ENGAGEMENT_URL, login_shell_prerender_html) is True


def test_classify_discussions_list(discussions_fixture_html, discussions_url):
    # FR-004: the rendered discussions list classifies as `discussions` (rows resolve), so the
    # pipeline proceeds rather than mistaking a real list for a login/unknown landing.
    assert classify_landing(discussions_url, discussions_fixture_html) == "discussions"


def test_classify_unknown_markup():
    # FR-018: arbitrary markup that is neither login nor a discussions list is `unknown`, so a
    # genuine selector miss stays distinguishable from a login redirect (the diagnostic stays
    # honest — a miss is a miss, a login bounce is a login bounce).
    assert classify_landing("https://example.com/x", "<html><body><p>hi</p></body></html>") == "unknown"
