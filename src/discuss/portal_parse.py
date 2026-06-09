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
    LOGIN_SHELL_BODY_MARKER,
    LOGIN_SHELL_TITLE_MARKER,
    PEER_POST_AUTHOR_SEL,
    PEER_POST_BODY_SEL,
    PEER_POST_SEL,
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


@dataclass(frozen=True)
class PeerPost:
    """One visible classmate post: stable ordinal, display author, and plaintext body."""

    index: int
    author: str
    text: str


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


def extract_peer_posts(
    html: str,
    *,
    message_selector: str = PEER_POST_SEL,
    author_selector: str = PEER_POST_AUTHOR_SEL,
    body_selector: str = PEER_POST_BODY_SEL,
) -> list[PeerPost]:
    """Return visible classmate posts as plaintext, excluding the topic prompt/new editor.

    Pure over the captured discussion HTML. The live portal marks the instructor prompt as an
    ``is-topic`` message outside ``div.comment-wrapper`` and classmate responses as comment
    wrappers; the default selector follows that distinction so prompt text and the operator's
    new-post editor never become peer candidates.
    """
    tree = HTMLParser(html or "")
    posts: list[PeerPost] = []
    for message in tree.css(message_selector):
        body = message.css_first(body_selector)
        text = collapse_whitespace(body.text(separator=" ")) if body is not None else ""
        if not text:
            continue
        author = ""
        author_node = message.css_first(author_selector)
        if author_node is not None:
            author = collapse_whitespace(author_node.text(separator=" "))
        posts.append(PeerPost(index=len(posts) + 1, author=author or "Classmate", text=text))
    return posts


def is_login_page(url: str, html: str) -> bool:
    """True iff the page is the login screen — post-render OR pre-render shell (FR-003, Esc#2).

    Pure decision so it is unit-testable off saved HTML. Recognises three signals, any one
    sufficient: (1) the POST-render ``LOGIN_PAGE_MARKER``; (2) the PRE-render ForgeRock SSO
    shell, keyed on its title AND body markers TOGETHER (the live adapter reads the DOM
    before the SPA paints, so the post-render marker is absent — Esc#2's exact failure); (3)
    a ``/login`` URL fallback. ``browser.ensure_logged_in`` uses this to pause and prompt for
    *manual* login — the tool never automates credentials.
    """
    h = html or ""
    if LOGIN_PAGE_MARKER and LOGIN_PAGE_MARKER in h:
        return True
    if LOGIN_SHELL_TITLE_MARKER in h and LOGIN_SHELL_BODY_MARKER in h:
        return True
    return "/login" in (url or "").lower()


def classify_landing(url: str, html: str) -> str:
    """Classify a post-navigation landing as ``"discussions"`` | ``"login"`` | ``"unknown"``.

    Esc#2 corrective (FR-003/FR-018): after the live adapter waits for render, the caller
    must branch on what it actually landed on — a rendered discussions list (proceed), a
    login redirect (pause for manual login, FR-003), or genuinely unrecognised markup (a real
    selector miss, distinct from a login bounce so the FR-018 diagnostic stays honest).

    Pure over the (url, html) pair. Checks for rendered discussion rows FIRST so a real list
    is never misread as login/unknown; falls to the login predicate; else ``"unknown"``.
    """
    if HTMLParser(html or "").css_first(DISCUSSION_ROWS_SEL) is not None:
        return "discussions"
    if is_login_page(url, html):
        return "login"
    return "unknown"
