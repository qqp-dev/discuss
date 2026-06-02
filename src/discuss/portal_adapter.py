"""[COVERAGE-EXEMPT] Live portal adapter — the ONLY home for UOPX selectors + click-path.

Every portal-specific selector and all live Playwright navigate/extract/fill I/O live
here and nowhere else (FR-013, Constitution P-III): a portal markup change is a one-file
fix. This module is coverage-exempt because it is honestly exercisable only against the
live, login-gated portal — which the Respectful-guest principle (P-I) forbids us from
automating in CI. It is verified by the operator checklist in `docs/SELECTOR-CAPTURE.md`,
not by unit tests. All PURE parsing/selection logic lives in `portal_parse.py` (which is
NOT exempt and is covered by saved-HTML fixtures).

Build status: T002 seeds the SELECTORS below from a *live capture* — the values are
placeholders until the operator records them (see docs/SELECTOR-CAPTURE.md). The live
navigate/extract methods are added in T012; the runtime-typed `fill_reply` in T015. None
of the live tasks can run until SELECTORS and DUE_DATE_FORMAT are filled.
"""

from __future__ import annotations

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
