import datetime as dt

from discuss.portal_parse import (
    extract_prompt_text,
    parse_discussions,
    select_soonest_due,
    verify_fill_readback,
)


def test_readback_match_ignores_trailing_ws():
    # FR-012: a trailing newline from the field read-back must not count as a mismatch.
    assert verify_fill_readback("My answer.", "My answer.\n") is True


def test_readback_mismatch_detected():
    # FR-012: a partial/garbled paste must fail verification.
    assert verify_fill_readback("My full answer.", "My full") is False


def test_readback_empty_intended_is_false():
    # edge: an empty/whitespace-only intended text is never a valid successful fill.
    assert verify_fill_readback("", "anything") is False


def test_readback_richtext_wrappers_compare_on_text():
    # edge: a rich-text field returns the text wrapped in <p>…</p>; verification must
    # compare on text content so the markup wrapper is not seen as a mismatch.
    assert verify_fill_readback("My answer.", "<p>My answer.</p>") is True


def test_readback_empty_actual_is_false():
    # FR-012: an empty read-back (nothing landed in the field, or it was cleared) must
    # fail verification against a non-empty intended response.
    assert verify_fill_readback("My answer.", "") is False


def test_readback_intended_angle_brackets_not_a_false_match():
    # FR-012 fail-safe: the operator's response may legitimately contain angle brackets
    # (code, generics, math like a<b). A read-back with DIFFERENT bracketed content must
    # NOT verify True — stripping markup from the *intended* side would fail OPEN on this
    # safety gate, letting a garbled paste pass. This guards that regression.
    assert verify_fill_readback("Use Vec<String>", "Use Vec<HashMap>") is False
    assert verify_fill_readback("x <1> y", "x <2> y") is False


# --- T010: due-date parsing & soonest-due selection (FR-004) ---


def test_parse_discussions_reads_rows_and_due_dates(discussions_fixture_html):
    # FR-004: each list row yields a title, its url, and a parsed due date (or None for the
    # ungraded rows that carry no "Due date:" cell). Catches a row selector that misses
    # rows or one that cannot reach the due-date cell nested inside the row.
    items = parse_discussions(discussions_fixture_html)
    assert len(items) == 7
    dated = [i for i in items if i.due_date is not None]
    assert len(dated) == 5  # 2 of the 7 (Course Questions, Meet Your Faculty) are ungraded
    assert min(i.due_date for i in dated) == dt.date(2026, 6, 2)
    assert all(i.url and i.url.startswith("http") for i in items)


def test_select_soonest_due_from_fixture(discussions_fixture_html):
    # FR-004: pick the nearest FUTURE due date.
    items = parse_discussions(discussions_fixture_html)
    chosen = select_soonest_due(items, today=dt.date(2026, 6, 1))
    assert chosen.due_date == min(
        i.due_date for i in items if i.due_date and i.due_date >= dt.date(2026, 6, 1)
    )


def test_no_upcoming_due_returns_none():
    # FR-014 edge: all past → no target.
    items = [type("D", (), {"title": "old", "due_date": dt.date(2020, 1, 1), "url": "u"})()]
    assert select_soonest_due(items, today=dt.date(2026, 6, 1)) is None


def test_unparseable_due_skipped():
    items = [
        type("D", (), {"title": "bad", "due_date": None, "url": "a"})(),
        type("D", (), {"title": "good", "due_date": dt.date(2026, 6, 8), "url": "b"})(),
    ]
    assert select_soonest_due(items, today=dt.date(2026, 6, 1)).title == "good"


def test_select_soonest_due_tie_breaks_on_list_order():
    # edge: a tie on due date resolves to the earliest in list order (deterministic).
    same = dt.date(2026, 6, 8)
    items = [
        type("D", (), {"title": "first", "due_date": same, "url": "a"})(),
        type("D", (), {"title": "second", "due_date": same, "url": "b"})(),
    ]
    assert select_soonest_due(items, today=dt.date(2026, 6, 1)).title == "first"


def test_select_soonest_due_empty_list_returns_none():
    # edge: nothing parsed at all → no target (caller raises NoUpcomingDiscussion).
    assert select_soonest_due([], today=dt.date(2026, 6, 1)) is None


def test_parse_discussions_robust_to_bad_and_linkless_rows():
    # FR-004/FR-014: a malformed or unparseable "Due date:" must yield due_date=None (not a
    # crash, not a bogus date), and a row with no discussion link must be skipped (not a
    # blank-title/empty-url phantom). Catches: strptime crashing the whole parse on one bad
    # cell, and link-less rows leaking into the result. Synthetic markup mirrors the live
    # Ultra class shape (makeStyles<rule>-0-2-NNN) the selectors key off.
    html = """
    <div class="makeStylescontentListItem-0-2-1">
      <a href="https://vle.phoenix.edu/engagement/discussion/_1_1"
         aria-label="Discussion, Empty Due">open</a>
      <div class="makeStylesgradeDetail-0-2-1">Due date:  (PST)</div>
    </div>
    <div class="makeStylescontentListItem-0-2-2">
      <a href="https://vle.phoenix.edu/engagement/discussion/_2_1"
         aria-label="Discussion, Bogus Due">open</a>
      <div class="makeStylesgradeDetail-0-2-2">Due date: someday next week</div>
    </div>
    <div class="makeStylescontentListItem-0-2-3">
      <div class="makeStylesgradeDetail-0-2-3">Due date: 6/9/26, 1:59 AM (CDT)</div>
    </div>
    """
    items = parse_discussions(html)
    assert [i.title for i in items] == ["Empty Due", "Bogus Due"]  # linkless row dropped
    assert all(i.due_date is None for i in items)  # empty + unparseable both → None


# --- T011: prompt extraction (FR-006) ---


def test_extract_prompt_text_from_fixture(discussion_page_fixture_html):
    # FR-006: the instructor prompt is returned as normalized plaintext from the FIRST
    # prompt container (the #bb-editor-textbox id is reused by every read-only post, so a
    # selector that grabbed the last/all matches would return the wrong text or a concat).
    text = extract_prompt_text(discussion_page_fixture_html)
    assert "Please take a moment and share a few facts about yourself" in text
    assert "<" not in text  # markup stripped


def test_extract_prompt_text_collapses_whitespace(discussion_page_fixture_html):
    # FR-006: plaintext is normalized — no doubled spaces or stray newlines leak through.
    text = extract_prompt_text(discussion_page_fixture_html)
    assert "  " not in text and "\n" not in text


def test_extract_prompt_text_missing_container_returns_empty():
    # edge: a page with no prompt container yields "" (caller treats empty as a failure),
    # rather than crashing on a None node.
    assert extract_prompt_text("<html><body><p>no prompt here</p></body></html>") == ""
