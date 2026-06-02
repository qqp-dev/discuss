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
SELECTORS = {
    # Click-path: the control that opens a class's discussions area.
    "class_link": "",
    # The discussions list: a selector matching each discussion row/card.
    "discussion_rows": "",
    # Within a discussion row: the due-date cell, and the link/title that opens it.
    "due_date_cell": "",
    "discussion_link": "",
    # On a discussion page: the container holding the prompt's plaintext.
    "prompt_container": "",
    # The reply field (plain textarea OR rich-text/contenteditable — type detected at
    # runtime in T015's fill_reply; do NOT hard-code the type here, FR-011).
    "reply_field": "",
}

# The due-date string format on the discussions list (a strptime pattern, e.g.
# "%b %d, %Y"), recorded during capture and consumed by portal_parse.parse_discussions().
# Placeholder until T002.
DUE_DATE_FORMAT = ""
