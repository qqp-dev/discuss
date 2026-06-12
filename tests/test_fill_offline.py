"""T022 — `file://` fill oracle against the captured Quill reply form (FR-011, FR-012).

Drives the **real** ``portal_adapter.fill_reply`` against the captured ``reply_form.html``
loaded over ``file://`` in a headless Chromium — the controlled real boundary blessed by
intent.md's saved-real-HTML coverage statement. This exercises the *actual* fill surface the criterion names (runtime
field-type detection picking the contenteditable Quill branch, the editor rendering the
injected text, read-back passing, and nothing being submitted) instead of a fake. If the
captured selector or the runtime branch is wrong, it surfaces HERE — offline, with zero
submit risk — rather than live.

No silent skips: when ``playwright install chromium`` is absent the test LOUDLY skips with a
printed reason (no-silent-caps); it never passes silently.
"""

import pathlib

import pytest

from discuss import portal_adapter

playwright = pytest.importorskip(
    "playwright.sync_api",
    reason="LOUD SKIP: `playwright install chromium` not present — file:// fill oracle not run",
)


def test_fill_against_captured_reply_form():
    # FR-011/FR-012: the REAL fill_reply, against the REAL captured Quill DOM, must detect
    # the field type at runtime, render the text, pass read-back, and submit nothing.
    from playwright.sync_api import sync_playwright

    fixture = pathlib.Path("fixtures/reply_form.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        page.goto(fixture)
        start_url = page.url
        portal_adapter.fill_reply(page, "My drafted reply.")        # real adapter, real DOM
        field = page.query_selector(portal_adapter.REPLY_FIELD_SEL)
        assert "My drafted reply." in field.inner_text()            # rendered effect
        assert field.evaluate("el => document.activeElement === el || el.contains(document.activeElement)")
        assert page.url == start_url                                # nothing navigated/submitted
        b.close()
