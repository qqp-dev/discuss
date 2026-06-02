"""Pure parsing / selection / comparison logic on HTML and text strings.

This module holds NO live Playwright I/O and NO portal selectors — those live in
`portal_adapter.py` (FR-013). Everything here is a pure function of its string inputs,
so it is honestly unit-testable against saved-HTML fixtures (Constitution §2).

T014 seeds the file with the read-back verifier and the shared text-normalization
helper; due-date parsing/selection (T010), prompt extraction (T011), and the login
predicate (T006) are added here once their portal fixtures exist (T002).
"""

from __future__ import annotations

import re

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


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
