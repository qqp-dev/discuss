"""[COVERAGE-EXEMPT] Live portal adapter — the ONLY home for UOPX selectors + click-path.

Every portal-specific selector and all live Playwright navigate/extract/fill I/O live
here and nowhere else (FR-013, Constitution P-III): a portal markup change is a one-file
fix. This module is coverage-exempt because it is honestly exercisable only against the
live, login-gated portal — which the Respectful-guest principle (P-I) forbids us from
automating in CI. It is verified by the operator checklist in `docs/SELECTOR-CAPTURE.md`,
not by unit tests. All PURE parsing/selection logic lives in `portal_parse.py` (which is
NOT exempt and is covered by saved-HTML fixtures).

Build status: SELECTORS + DUE_DATE_FORMAT are filled from the live capture (T002,
docs/SELECTOR-CAPTURE.md) and validated against the saved fixtures via the real selector
engine. The live navigate/extract methods (T012) and the runtime-typed `fill_reply`
(T015) are implemented here; their live behaviour is verified by the operator checklist
(T013/T016/T019), not by unit tests.
"""

from __future__ import annotations

from discuss.errors import FillVerifyFailed, NotAuthenticated, SelectorMiss

# ---------------------------------------------------------------------------------------
# SELECTORS — captured from a LIVE portal session (docs/SELECTOR-CAPTURE.md, task T002).
#
# Each value is a CSS/text selector recorded against the REAL logged-in UOPX portal and
# then validated by running the actual Playwright/Chromium selector engine against the
# captured fixtures (match counts noted per selector). This module is the single source of
# every portal selector in the codebase (FR-013 / SC-002): a portal markup change is fixed
# by editing ONLY this file.
#
# The selector STRINGS are authored here as named `*_SEL` constants so pure consumers
# (`portal_parse`) can import the VALUES without re-declaring them — the strings still live
# only here. `SELECTORS` (the dict) is assembled from the same constants for the live
# adapter's own use, so there is exactly one authoring site per selector.
#
# The portal is Blackboard Ultra (vle.phoenix.edu). Its CSS classes are Material-UI/JSS —
# `makeStyles<rule>-0-2-NNN` — where only the trailing index churns between builds, so we
# match the stable `<rule>` prefix via [class*="makeStyles<rule>"] rather than the full
# class. These resolve correctly against today's markup; a live re-verify is only needed if
# Ultra's markup changes (then this file is the one-file fix).
# ---------------------------------------------------------------------------------------

# Click-path: the control that opens a class's discussions area. NOT in the captured
# fixtures (it's on the course landing page). The pipeline navigates directly to the
# engagement URL instead (…/ultra/courses/<id>/engagement), so this is left empty unless a
# start-from-homepage click-path is later required.
CLASS_LINK_SEL = ""

# Discussions list: one row per discussion. Validated: 7/7 discussion rows, and — unlike
# the narrower `makeStylescontainer` card — each `contentListItem` row also NESTS that
# discussion's due-date cell, so a row + a within-row due lookup pair up correctly (T010
# soonest-due). A row container that excludes the due cell would make every discussion look
# undated.
DISCUSSION_ROWS_SEL = "div[class*='makeStylescontentListItem']"

# Due-date cell within a row, text "Due date: 6/2/26, 1:59 AM (CDT)". Validated: 5 cells,
# all genuine due dates. NOTE only graded discussions have one — 2 of the 7 (e.g. the
# ungraded intro) have NO due date, so soonest-due selection (T010) must skip rows without
# a parseable "Due date:" rather than treat them as due now/never.
DUE_DATE_CELL_SEL = "[class*='makeStylesgradeDetail']"

# The link/title that opens a discussion (stable href hook; also carries
# aria-label="Discussion, <title>"). Validated: 7 anchors -> 7 distinct discussions.
DISCUSSION_LINK_SEL = "a[href*='/engagement/discussion/_']"

# On a discussion page: the instructor prompt, read-only Quill. The id is reused 12×
# (prompt + every read-only post), so the prompt is the FIRST match — the adapter/extractor
# takes the first. Validated: first is the prompt ("Hello! Please take a moment…").
PROMPT_CONTAINER_SEL = "#bb-editor-textbox"

# The reply field: the single editable Quill editor (placeholder "Type a Post"). Validated:
# exactly 1 match. fill_reply (T015) still detects textarea-vs-richtext at runtime per
# FR-011 — do NOT hard-code the type.
REPLY_FIELD_SEL = ".ql-editor[contenteditable='true']"

# Classmate top-level posts shown in the opened discussion. These are read-only comment
# messages under ``div.comment-wrapper``; keeping the scope there excludes the instructor
# prompt/topic message and the new top-level reply editor.
PEER_POST_SEL = "div.comment-wrapper bb-message[message-mode='view']"
PEER_POST_AUTHOR_SEL = "bb-linked-username[analytics-id='discussion.message.user']"
PEER_POST_BODY_SEL = ".ql-editor[contenteditable='false']"

# The single dict view the live adapter uses; assembled from the constants above so each
# selector is authored exactly once (FR-013 / SC-002).
SELECTORS = {
    "class_link": CLASS_LINK_SEL,
    "discussion_rows": DISCUSSION_ROWS_SEL,
    "due_date_cell": DUE_DATE_CELL_SEL,
    "discussion_link": DISCUSSION_LINK_SEL,
    "prompt_container": PROMPT_CONTAINER_SEL,
    "reply_field": REPLY_FIELD_SEL,
    "peer_post": PEER_POST_SEL,
    "peer_post_author": PEER_POST_AUTHOR_SEL,
    "peer_post_body": PEER_POST_BODY_SEL,
}

# Due-date strptime pattern for the text remaining AFTER the caller strips the "Due date: "
# label and the trailing " (TZ)" suffix — e.g. "6/2/26, 1:59 AM". Single-digit month/day
# parse fine under %m/%d. The "(CDT)" tz label is dropped before parsing (Python's %Z can't
# reliably parse it); soonest-due only needs the local date/time. Consumed by
# portal_parse.parse_discussions().
DUE_DATE_FORMAT = "%m/%d/%y, %I:%M %p"

# Login-page marker for portal_parse.is_login_page (T006, FR-003). The logged-out page is
# on www.phoenix.edu and carries this exact <title>; the logged-in portal is on
# vle.phoenix.edu (no password field). Confirmed against login_page.html. This marker is
# only present POST-render, so it alone misses the pre-render shell below (Esc#2).
LOGIN_PAGE_MARKER = "University of Phoenix Login"

# Pre-render login-shell markers (Esc#2). The live IdP is a client-rendered ForgeRock/Vue
# SPA; navigated to pre-render it is a 1.6 KB shell carrying NONE of LOGIN_PAGE_MARKER
# (which only appears once the SPA paints) but two stable shell markers: the `<title>Login</title>`
# and ForgeRock's `data-testid="fr-body-image"` on <body>. Keyed TOGETHER (both required) so a
# page that merely has a "Login" title cannot false-positive. Captured verbatim in
# fixtures/login_shell_prerender.html (the FR-018 self-snapshot from the first live run).
LOGIN_SHELL_TITLE_MARKER = "<title>Login</title>"
LOGIN_SHELL_BODY_MARKER = 'data-testid="fr-body-image"'

# CSS form of the ForgeRock login-shell body marker, for the render wait below (Esc#2). Same
# marker as LOGIN_SHELL_BODY_MARKER, expressed as a selector so wait_for_selector can wake on
# EITHER the expected content OR the login shell appearing.
LOGIN_SHELL_BODY_SEL = "[data-testid='fr-body-image']"

# Bounded, human-paced render wait (Esc#2). The live portal + its IdP are client-rendered SPAs,
# so the DOM is empty at `domcontentloaded`; we must wait for the content (or the login shell) to
# PAINT before reading it. `wait_for_selector` is mutation-observer-based — it resolves the
# instant the element appears and otherwise blocks up to the timeout; it is NOT a tight poll, so
# it stays within the Respectful-guest pace (P-I). ~20s tolerates a slow paint without hanging a
# human-in-the-loop run.
LANDING_WAIT_MS = 20_000

# The discussions area for a class. `class_link` is empty (the start-from-homepage click
# is not used); we navigate directly to the engagement area, the stem every discussion row
# in the captured list shares (…/courses/<id>/engagement). The exact landing URL is a live
# detail verified in T013.
DISCUSSIONS_URL_TEMPLATE = "https://vle.phoenix.edu/ultra/courses/{class_id}/engagement"


def _visible_field(page, selector: str):
    """Return a visible field handle or raise ``SelectorMiss`` with the selector named."""
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

    try:
        field = page.wait_for_selector(selector, state="visible", timeout=LANDING_WAIT_MS)
    except PlaywrightTimeoutError as exc:
        raise SelectorMiss(f"reply field not visible (selector {selector!r})") from exc
    if field is None:
        raise SelectorMiss(f"reply field not found (selector {selector!r})")
    return field


def _prepare_contenteditable(field) -> bool:
    """Focus the contenteditable and select all current rendered content."""
    return bool(
        field.evaluate(
            """el => {
                el.scrollIntoView({block: "center", inline: "nearest"});
                el.focus();
                const selection = window.getSelection();
                const range = document.createRange();
                range.selectNodeContents(el);
                selection.removeAllRanges();
                selection.addRange(range);
                return document.activeElement === el || el.contains(document.activeElement);
            }"""
        )
    )


def _dispatch_editor_input(field, text: str) -> None:
    field.evaluate(
        """(el, value) => {
            const eventInit = {bubbles: true, cancelable: true, data: value, inputType: "insertText"};
            const inputEvent = typeof InputEvent === "function"
                ? new InputEvent("input", eventInit)
                : new Event("input", {bubbles: true, cancelable: true});
            el.dispatchEvent(inputEvent);
            el.dispatchEvent(new Event("change", {bubbles: true, cancelable: true}));
        }""",
        text,
    )


# ---------------------------------------------------------------------------------------
# Live navigate/extract methods (T012). [COVERAGE-EXEMPT] — these drive a real Playwright
# ``page`` against the login-gated portal and are verified by the operator checklist (T013),
# not by unit tests. All PURE parsing they rely on is delegated to ``portal_parse`` (which
# IS unit-tested against the saved fixtures). Each method is human-paced and issues the
# minimum page loads (FR-016, P-I); any missing selector raises ``SelectorMiss`` naming the
# step, so a portal change fails loud and points here (the one-file fix).
#
# ``portal_parse`` is imported lazily inside the methods: it imports the selector constants
# from this module at import time, so a top-level import here would be circular.
# ---------------------------------------------------------------------------------------


def _await_landing(page, content_sel: str, *, step: str, miss: str) -> None:
    """Wait (bounded, ~20s) for the expected content OR the login shell to render, then branch
    on the landing (Esc#2). A login redirect → ``NotAuthenticated`` so the orchestrator pauses
    for manual login and retries (FR-003); the expected content present → proceed; neither
    (timeout / unknown markup) → ``SelectorMiss`` naming the step.

    The classification *decision* is the offline-pinned pure ``classify_landing`` (T028, unit-
    tested against the captured pre-render shell fixture); only the wait *timing* is live. Both
    imports are lazy so importing this module (and, transitively, ``portal_parse``) needs no
    Playwright install and no constants cycle.
    """
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

    from discuss.portal_parse import classify_landing

    try:
        page.wait_for_selector(f"{content_sel}, {LOGIN_SHELL_BODY_SEL}", timeout=LANDING_WAIT_MS)
    except PlaywrightTimeoutError:
        pass  # neither painted in time — fall through to classify/raise below (post-render)

    if classify_landing(page.url, page.content()) == "login":
        raise NotAuthenticated(f"the portal redirected to the login page at the {step!r} step")
    if page.query_selector(content_sel) is None:
        raise SelectorMiss(miss)


def go_to_discussions(page, class_id: str):
    """Navigate to the discussions list for ``class_id`` (FR-004). Waits for render, then:
    a login redirect → ``NotAuthenticated`` (the orchestrator pauses for manual login, Esc#2);
    no discussion rows after render → ``SelectorMiss``."""
    page.goto(DISCUSSIONS_URL_TEMPLATE.format(class_id=class_id), wait_until="domcontentloaded")
    _await_landing(
        page,
        DISCUSSION_ROWS_SEL,
        step="navigate",
        miss=(
            f"discussions list did not render for class {class_id} "
            f"(no rows matched {DISCUSSION_ROWS_SEL!r})"
        ),
    )
    return page


def list_discussions(page):
    """Return the discussions on the current list page (FR-004), delegating the parse to
    the unit-tested ``portal_parse.parse_discussions``."""
    from discuss.portal_parse import parse_discussions

    return parse_discussions(page.content())


def open_discussion(page, discussion):
    """Open ``discussion`` (a parsed row) and wait for its prompt container to render (FR-006).
    A login redirect → ``NotAuthenticated`` (Esc#2); no prompt container after render →
    ``SelectorMiss``. This owns the render wait for the prompt page; ``extract_prompt`` then
    reads the painted content."""
    page.goto(discussion.url, wait_until="domcontentloaded")
    _await_landing(
        page,
        PROMPT_CONTAINER_SEL,
        step="open",
        miss=f"prompt container not found on discussion page (selector {PROMPT_CONTAINER_SEL!r})",
    )
    return page


def extract_prompt(page) -> str:
    """Return the discussion's prompt as normalized plaintext (FR-006), delegating to the
    unit-tested ``portal_parse.extract_prompt_text``. Raises SelectorMiss on empty text."""
    from discuss.portal_parse import extract_prompt_text

    text = extract_prompt_text(page.content())
    if not text:
        raise SelectorMiss(
            f"prompt text was empty (container {PROMPT_CONTAINER_SEL!r} missing or blank)"
        )
    return text


def extract_peer_posts(page):
    """Return visible classmate posts from the opened discussion page."""
    from discuss.portal_parse import extract_peer_posts as parse_peer_posts

    return parse_peer_posts(page.content())


def fill_reply(page, text: str) -> None:
    """Inject ``text`` into the reply field and verify the read-back — never submit (T015).

    [COVERAGE-EXEMPT] Live Playwright; the read-back *decision* is the unit-tested pure
    ``verify_fill_readback`` (T014), and the no-submit / rendered-equals-response guarantees
    are verified by the operator checklist (T016). Steps, per FR-010/FR-011/FR-012:

    1. Locate the reply field by the captured selector; absent → ``SelectorMiss`` (raise,
       never guess — FR-011).
    2. **Detect the field type at runtime** (do NOT hard-code it): a ``<textarea>``/``<input>``
       is filled with ``fill()``; a contenteditable rich-text body (the Quill editor) is
       focused, cleared, and typed into via the keyboard. A field that is neither aborts.
    3. Read the rendered content back and check it with ``verify_fill_readback``; a mismatch
       (partial/garbled paste) → ``FillVerifyFailed``.
    4. **Never** locate or click a submit/post control — there is deliberately no such
       lookup anywhere in this function. On any raise the caller preserves ``response.md``
       and tells the operator to paste manually (FR-012/FR-015).
    """
    from discuss.portal_parse import verify_fill_readback

    field = _visible_field(page, REPLY_FIELD_SEL)

    tag = (field.evaluate("el => el.tagName") or "").lower()
    is_contenteditable = bool(field.evaluate("el => el.isContentEditable"))

    if tag in ("textarea", "input"):
        field.scroll_into_view_if_needed()
        field.fill(text)  # fill() replaces existing content
        actual = field.input_value()
    elif is_contenteditable:
        field.scroll_into_view_if_needed()
        field.click()  # focus the editable body
        if not _prepare_contenteditable(field):
            raise FillVerifyFailed("reply field could not be focused; aborting write-back")
        page.keyboard.press("Backspace")
        page.keyboard.insert_text(text)
        _dispatch_editor_input(field, text)
        actual = field.inner_text()
    else:
        # Located, but neither a textarea nor contenteditable — we cannot type into it
        # safely, so abort (write-back is preserved by the caller) rather than guess.
        raise FillVerifyFailed(
            f"reply field type is undetectable (tag={tag!r}, contenteditable=False); "
            "aborting write-back"
        )

    if not verify_fill_readback(text, actual):
        raise FillVerifyFailed("reply field read-back did not match the intended response")
