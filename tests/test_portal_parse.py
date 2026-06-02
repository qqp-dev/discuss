from discuss.portal_parse import verify_fill_readback


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
