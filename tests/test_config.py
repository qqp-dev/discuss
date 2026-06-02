from discuss.config import Config


def test_confirm_defaults_on():
    # FR-005: the wrong-target safety gate is on unless explicitly disabled.
    assert Config.load({}).confirm is True


def test_editor_default_is_wait_capable():
    # FR-009: save+close must block, so the default editor carries --wait.
    assert Config.load({}).editor_cmd == ["code", "--wait"]


def test_overrides_win():
    # operator config overrides defaults.
    c = Config.load({"confirm": False, "editor_cmd": ["gedit"]})
    assert c.confirm is False and c.editor_cmd == ["gedit"]


def test_empty_overrides_all_defaults():
    # edge: empty overrides → every field is its documented default (would catch a
    # field silently losing its default or a merge that mutates on the empty path).
    c = Config.load({})
    assert c.confirm is True
    assert c.editor_cmd == ["code", "--wait"]
    assert c.target_classes == []


def test_no_args_uses_defaults():
    # edge: load() with no argument (None) must behave like empty overrides, not crash
    # — exercises the None→{} normalization branch.
    c = Config.load()
    assert c.confirm is True


def test_unknown_keys_ignored():
    # edge: a stray/unknown config key must be ignored, not crash load() (would catch a
    # naive cls(**overrides) that forwards unknown kwargs into the dataclass).
    c = Config.load({"bogus_key": 123, "confirm": False})
    assert c.confirm is False
    assert not hasattr(c, "bogus_key")
