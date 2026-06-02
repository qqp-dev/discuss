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
# SELECTORS — FILL THESE FROM A LIVE CAPTURE (docs/SELECTOR-CAPTURE.md, task T002).
#
# Each value is a CSS/text selector captured against the REAL logged-in UOPX portal. They
# are intentionally empty ("") placeholders until the operator records them. This dict is
# the single source of portal selectors in the whole codebase (FR-013 / SC-002): a portal
# change is fixed by editing ONLY this file.
# ---------------------------------------------------------------------------------------
# Recorded from the live capture (docs/SELECTOR-CAPTURE.md). The portal is Blackboard
# Ultra (vle.phoenix.edu). Its CSS classes are Material-UI/JSS — `makeStyles<rule>-0-2-NNN`
# — where only the trailing index churns between builds, so we match the stable `<rule>`
# prefix via [class*="makeStyles<rule>"] rather than the full class. Confidence is noted
# per selector; anything marked VERIFY LIVE must be confirmed against the live DOM in the
# step-3 checklist before the live tasks (T012/T015) rely on it.
SELECTORS = {
    # Click-path: the control that opens a class's discussions area.
    # NOT present in the captured fixtures — it lives on the course landing page, which
    # was not captured. The pipeline can instead navigate directly to the engagement URL
    # (…/ultra/courses/<id>/engagement). Capture the course page if a click-path selector
    # is actually required. VERIFY LIVE.
    "class_link": "",
    # Discussions list: one row per discussion. The row is the container that holds a
    # discussion link. "container" is generic, so this may over-match nested wrappers —
    # VERIFY LIVE (tighten the ancestor combinator if more than one node matches per row).
    "discussion_rows": "div[class*='makeStylescontainer']:has(> h3 a[href*='/engagement/discussion/_'])",
    # Due-date cell within a row, text "Due date: 6/2/26, 1:59 AM (CDT)". Matched 10× vs
    # 8 rows, so the grade-detail class is also used for non-due fields — the caller must
    # keep only cells whose text starts with "Due date:" (portal_parse does this). VERIFY LIVE.
    "due_date_cell": "[class*='makeStylesgradeDetail']",
    # The link/title that opens a discussion (href is the stable hook; also carries
    # aria-label="Discussion, <title>"). Matched 7 of the 8 list rows — confirm the 8th is
    # a non-discussion engagement item (journal/assignment), not a missed discussion. HIGH.
    "discussion_link": "a[href*='/engagement/discussion/_']",
    # On a discussion page: the instructor prompt, rendered read-only in Quill. NOTE the id
    # is reused 12× (prompt + every read-only post), so the prompt is the FIRST match —
    # the adapter must take `.first`. VERIFY LIVE that the first is the prompt, not a reply.
    "prompt_container": "#bb-editor-textbox",
    # The reply field: the single editable Quill editor (placeholder "Type a Post").
    # Exactly one match on the page. fill_reply (T015) still detects textarea-vs-richtext
    # at runtime per FR-011 — do NOT hard-code the type. HIGH.
    "reply_field": ".ql-editor[contenteditable='true']",
}

# Due-date strptime pattern for the text remaining AFTER the caller strips the "Due date: "
# label and the trailing " (TZ)" suffix — e.g. "6/2/26, 1:59 AM". Single-digit month/day
# parse fine under %m/%d. The "(CDT)" timezone label is dropped before parsing (Python's
# %Z cannot reliably parse it); soonest-due only needs the local date/time. Consumed by
# portal_parse.parse_discussions().
DUE_DATE_FORMAT = "%m/%d/%y, %I:%M %p"

# Login-page marker for portal_parse.is_login_page (T006, FR-003). The logged-out page is
# on www.phoenix.edu and carries this exact <title>; the logged-in portal is on
# vle.phoenix.edu (and shows no password field). VERIFY LIVE.
LOGIN_PAGE_MARKER = "University of Phoenix Login"
