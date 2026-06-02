"""Pure parsing / selection / comparison logic on HTML and text strings.

This module holds NO live Playwright I/O and NO portal selectors — those live in
`portal_adapter.py` (FR-013). Everything here is a pure function of its string inputs,
so it is honestly unit-testable against saved-HTML fixtures (Constitution §2).

T014 seeds the file with the read-back verifier and the shared text-normalization
helper; due-date parsing/selection (T010), prompt extraction (T011), and the login
predicate (T006) are added here once their portal fixtures exist (T002).
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass

from selectolax.parser import HTMLParser

from discuss.portal_adapter import (
    DISCUSSION_LINK_SEL,
    DISCUSSION_ROWS_SEL,
    DUE_DATE_CELL_SEL,
    DUE_DATE_FORMAT,
    LOGIN_PAGE_MARKER,
    PROMPT_CONTAINER_SEL,
)

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
# Trailing parenthetical timezone label, e.g. " (CDT)", dropped before strptime.
_TZ_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")
_DUE_LABEL_RE = re.compile(r"^\s*due\s+date\s*:\s*", re.IGNORECASE)
# Title prefix the portal puts on the discussion link's aria-label ("Discussion, <title>").
_TITLE_PREFIX_RE = re.compile(r"^\s*discussion\s*,\s*", re.IGNORECASE)


def collapse_whitespace(value: str) -> str:
    """Collapse all whitespace runs to single spaces and trim. No markup handling."""
    if not value:
        return ""
    return _WS_RE.sub(" ", value).strip()


def normalize_text(value: str) -> str:
    """Strip HTML tags, then collapse whitespace — yields the plaintext of an HTML source.

    Used for the *read-back* side of verification and for prompt extraction (T011): a
    rich-text field's read-back (e.g. ``<p>…</p>``) reduces to its visible text content.
    Do NOT apply this to known plaintext that may contain literal angle brackets — see
    ``verify_fill_readback``.
    """
    if not value:
        return ""
    return collapse_whitespace(_TAG_RE.sub("", value))


def verify_fill_readback(intended: str, actual: str) -> bool:
    """True iff the field read-back equals the intended text after normalization (FR-012).

    Asymmetric by design: the operator's ``intended`` text is known plaintext that may
    legitimately contain angle brackets (code, generics, ``a<b``), so we only collapse its
    whitespace — never strip "tags" from it (that would fail OPEN, letting a garbled paste
    pass this safety gate). The field ``actual`` read-back may carry rich-text structural
    markup (``<p>``/``<br>``), so we strip that to compare on text content. The residual
    ambiguity (a plain textarea echoing literal ``<…>`` content) resolves to a mismatch —
    fail-SAFE: write-back aborts and the operator is told to paste manually.

    An empty or whitespace-only ``intended`` is never a successful fill, so it returns
    False.
    """
    norm_intended = collapse_whitespace(intended)
    if not norm_intended:
        return False
    return norm_intended == normalize_text(actual)


@dataclass(frozen=True)
class Discussion:
    """One discussion list row: its title, parsed due date (None if ungraded), and url."""

    title: str
    due_date: dt.date | None
    url: str


def _parse_due_date(cell_text: str, date_format: str) -> dt.date | None:
    """Parse "Due date: 6/2/26, 1:59 AM (CDT)" → date, or None if absent/unparseable.

    Strips the "Due date:" label and the trailing " (TZ)" suffix, then applies the
    portal's recorded ``date_format``. An ungraded row (no due cell, empty text) or an
    unrecognised format yields None so soonest-due selection skips it (FR-004/FR-014)
    rather than treating it as due now or never.
    """
    if not cell_text:
        return None
    s = _DUE_LABEL_RE.sub("", cell_text)
    s = _TZ_SUFFIX_RE.sub("", s).strip()
    if not s:
        return None
    try:
        return dt.datetime.strptime(s, date_format).date()
    except ValueError:
        return None


def parse_discussions(
    html: str,
    *,
    row_selector: str = DISCUSSION_ROWS_SEL,
    link_selector: str = DISCUSSION_LINK_SEL,
    due_selector: str = DUE_DATE_CELL_SEL,
    date_format: str = DUE_DATE_FORMAT,
) -> list[Discussion]:
    """Parse a discussions-list page into ``Discussion`` rows (FR-004).

    Pure over the HTML string. Selectors default to the adapter's recorded values (the
    single authoring site, FR-013) but are injectable so the adapter can override and so
    the parsing logic is testable in isolation. A row whose due cell is missing or holds an
    unparseable date gets ``due_date=None``; a row with no discussion link is skipped.
    """
    tree = HTMLParser(html)
    items: list[Discussion] = []
    for row in tree.css(row_selector):
        link = row.css_first(link_selector)
        if link is None:
            continue
        label = link.attributes.get("aria-label") or link.text(strip=True) or ""
        title = _TITLE_PREFIX_RE.sub("", label).strip()
        url = link.attributes.get("href") or ""
        due_cell = row.css_first(due_selector)
        due_text = due_cell.text(strip=True) if due_cell is not None else ""
        items.append(Discussion(title=title, due_date=_parse_due_date(due_text, date_format), url=url))
    return items


def select_soonest_due(items, today: dt.date):
    """Return the row with the nearest *upcoming* due date, or None (FR-004).

    Skips past-due and undated rows. Ties on due date resolve to the earliest in list
    order (``min`` is stable), giving a deterministic pick. Returns None when nothing is
    upcoming so the caller can stop rather than select an arbitrary discussion (FR-014).
    """
    upcoming = [i for i in items if i.due_date is not None and i.due_date >= today]
    if not upcoming:
        return None
    return min(upcoming, key=lambda i: i.due_date)


def extract_prompt_text(html: str, *, container_selector: str = PROMPT_CONTAINER_SEL) -> str:
    """Return the discussion's instructor prompt as normalized plaintext (FR-006).

    Pure over the HTML string. Takes the FIRST matching container — the portal reuses the
    prompt container id on every read-only post, so first-match is the instructor prompt
    and anything later is a student reply. Returns "" when the container is absent so the
    caller can treat an empty extraction as a failure rather than crashing on a None node.
    """
    node = HTMLParser(html).css_first(container_selector)
    if node is None:
        return ""
    return collapse_whitespace(node.text(separator=" "))


def is_login_page(url: str, html: str) -> bool:
    """True iff the page is the logged-out login screen (FR-003).

    Pure decision so it is unit-testable off saved HTML. Keys off the recorded login-page
    marker in the page body, with a URL fallback so a login redirect that has not yet
    rendered its body is still recognised. ``browser.ensure_logged_in`` uses this to pause
    and prompt for *manual* login — the tool never automates credentials.
    """
    if LOGIN_PAGE_MARKER and LOGIN_PAGE_MARKER in (html or ""):
        return True
    return "/login" in (url or "").lower()
