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

from discuss.errors import FillVerifyFailed, SelectorMiss

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

# The single dict view the live adapter uses; assembled from the constants above so each
# selector is authored exactly once (FR-013 / SC-002).
SELECTORS = {
    "class_link": CLASS_LINK_SEL,
    "discussion_rows": DISCUSSION_ROWS_SEL,
    "due_date_cell": DUE_DATE_CELL_SEL,
    "discussion_link": DISCUSSION_LINK_SEL,
    "prompt_container": PROMPT_CONTAINER_SEL,
    "reply_field": REPLY_FIELD_SEL,
}

# Due-date strptime pattern for the text remaining AFTER the caller strips the "Due date: "
# label and the trailing " (TZ)" suffix — e.g. "6/2/26, 1:59 AM". Single-digit month/day
# parse fine under %m/%d. The "(CDT)" tz label is dropped before parsing (Python's %Z can't
# reliably parse it); soonest-due only needs the local date/time. Consumed by
# portal_parse.parse_discussions().
DUE_DATE_FORMAT = "%m/%d/%y, %I:%M %p"

# Login-page marker for portal_parse.is_login_page (T006, FR-003). The logged-out page is
# on www.phoenix.edu and carries this exact <title>; the logged-in portal is on
# vle.phoenix.edu (no password field). Confirmed against login_page.html.
LOGIN_PAGE_MARKER = "University of Phoenix Login"

# The discussions area for a class. `class_link` is empty (the start-from-homepage click
# is not used); we navigate directly to the engagement area, the stem every discussion row
# in the captured list shares (…/courses/<id>/engagement). The exact landing URL is a live
# detail verified in T013.
DISCUSSIONS_URL_TEMPLATE = "https://vle.phoenix.edu/ultra/courses/{class_id}/engagement"


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


def go_to_discussions(page, class_id: str):
    """Navigate to the discussions list for ``class_id`` (FR-004). Raises SelectorMiss if
    the list does not render (no discussion rows resolve)."""
    page.goto(DISCUSSIONS_URL_TEMPLATE.format(class_id=class_id), wait_until="domcontentloaded")
    if page.query_selector(DISCUSSION_ROWS_SEL) is None:
        raise SelectorMiss(
            f"discussions list did not render for class {class_id} "
            f"(no rows matched {DISCUSSION_ROWS_SEL!r})"
        )
    return page


def list_discussions(page):
    """Return the discussions on the current list page (FR-004), delegating the parse to
    the unit-tested ``portal_parse.parse_discussions``."""
    from discuss.portal_parse import parse_discussions

    return parse_discussions(page.content())


def open_discussion(page, discussion):
    """Open ``discussion`` (a parsed row) and confirm its prompt container is present
    (FR-006). Raises SelectorMiss if the prompt container is absent."""
    page.goto(discussion.url, wait_until="domcontentloaded")
    if page.query_selector(PROMPT_CONTAINER_SEL) is None:
        raise SelectorMiss(
            f"prompt container not found on discussion page (selector {PROMPT_CONTAINER_SEL!r})"
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

    field = page.query_selector(REPLY_FIELD_SEL)
    if field is None:
        raise SelectorMiss(f"reply field not found (selector {REPLY_FIELD_SEL!r})")

    tag = (field.evaluate("el => el.tagName") or "").lower()
    is_contenteditable = bool(field.evaluate("el => el.isContentEditable"))

    if tag in ("textarea", "input"):
        field.fill(text)  # fill() replaces existing content
        actual = field.input_value()
    elif is_contenteditable:
        field.click()  # focus the editable body
        page.keyboard.press("Control+A")  # clear any existing content before typing
        page.keyboard.press("Delete")
        page.keyboard.insert_text(text)
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
