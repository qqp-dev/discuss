"""T017 — orchestrator pipeline (FR-001/005/006/010/012/014/015).

The pipeline is exercised entirely with the injected fakes from ``fake_ctx`` (conftest):
no browser, no claude subprocess, no live portal. Each test asserts one ordering or safety
guarantee of ``cli.run``.
"""

import datetime as dt

import pytest

from discuss import cli, handoff
from discuss.errors import FillVerifyFailed, NoUpcomingDiscussion, NotAuthenticated, SelectorMiss


def test_confirm_decline_aborts(fake_ctx):
    # FR-005: declining the gate extracts nothing and fills nothing.
    fake_ctx.confirm_answer = False
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.adapter.extracted is False
    assert fake_ctx.adapter.filled is False


def test_confirm_gate_names_discussion(fake_ctx):
    # FR-005: the confirmation gate names the selected discussion and its due date.
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.selected.title in fake_ctx.gate_prompt
    assert str(fake_ctx.selected.due_date) in fake_ctx.gate_prompt


def test_confirm_disabled_skips_gate(fake_ctx):
    # WHERE the operator disabled it (config.confirm=False), no gate is shown and the run
    # proceeds straight through to a fill.
    fake_ctx.config.confirm = False
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.gate_prompt is None  # confirm() never called
    assert fake_ctx.adapter.filled is True


def test_no_upcoming_due_stops(fake_ctx):
    # FR-014: nothing upcoming → stop, no fill.
    fake_ctx.adapter.discussions = []  # select_soonest_due → None
    with pytest.raises(NoUpcomingDiscussion):
        cli.run(**fake_ctx.kwargs)
    assert fake_ctx.adapter.filled is False


def test_not_authenticated_surfaces(fake_ctx):
    # edge (post-Esc#2 re-sequencing): a persistent login landing — the adapter raises
    # NotAuthenticated even after the post-navigation pause + single retry — surfaces; the run
    # aborts, nothing filled. (Auth is no longer checked on the fresh page before navigation.)
    def boom(page, cid):
        raise NotAuthenticated("login persisted across the retry")

    kwargs = fake_ctx.kwargs
    kwargs["adapter"].go_to_discussions = boom  # instance attr shadows the method (unbound)
    with pytest.raises(NotAuthenticated):
        cli.run(**kwargs)
    assert fake_ctx.adapter.filled is False


def test_extracted_prompt_written(fake_ctx):
    # FR-006: confirmed run writes prompt.md before the session.
    cli.run(**fake_ctx.kwargs)
    assert (fake_ctx.run_dir / handoff.PROMPT_FILE).exists()


def test_response_persisted_before_fill(fake_ctx):
    # FR-015: response.md exists on disk before fill is attempted.
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.adapter.response_existed_at_fill is True


def test_fill_does_not_submit(fake_ctx):
    # FR-010: the happy path fills but never submits.
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.adapter.filled is True
    assert fake_ctx.adapter.submitted is False


def test_fill_verify_mismatch_aborts(fake_ctx):
    # FR-012: a failed read-back aborts write-back, preserves the response, AND tells the
    # operator to paste manually — assert all three limbs of the criterion.
    fake_ctx.adapter.fill_raises = FillVerifyFailed("read-back mismatch")
    cli.run(**fake_ctx.kwargs)
    assert (fake_ctx.run_dir / handoff.RESPONSE_FILE).exists()  # preserved
    assert fake_ctx.adapter.submitted is False  # aborted: never submitted
    assert "paste" in fake_ctx.last_message.lower()  # manual-paste instruction


def test_fill_selector_miss_aborts(fake_ctx):
    # edge: a SelectorMiss at fill takes the same preserve-and-manual-paste path as a
    # verify mismatch (the reply field vanished/changed) rather than crashing the run.
    fake_ctx.adapter.fill_raises = SelectorMiss("reply field not found")
    cli.run(**fake_ctx.kwargs)
    assert (fake_ctx.run_dir / handoff.RESPONSE_FILE).exists()
    assert fake_ctx.adapter.submitted is False
    assert "paste" in fake_ctx.last_message.lower()


def test_happy_path_reports_discussion_title(fake_ctx):
    # FR-001: a clean run ends by reporting the discussion it drafted a reply for.
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.selected.title in fake_ctx.last_message


def test_load_overrides_parses_env():
    # FR-005/Q4: cli gathers config from env into the overrides dict (config.py delegates
    # this gathering to the orchestrator). Comma-split classes, space-split editor, and an
    # explicit confirm-off are all parsed; absent vars contribute no key (defaults win).
    from pathlib import Path

    env = {
        "DISCUSS_TARGET_CLASSES": " _577963_1 , _x_2 ",
        "DISCUSS_EDITOR": "nano",
        "DISCUSS_CONFIRM": "false",
        "DISCUSS_PROFILE_DIR": "/tmp/p",
        "DISCUSS_RUN_ROOT": "/tmp/r",
    }
    ov = cli._load_overrides(env)
    assert ov["target_classes"] == ["_577963_1", "_x_2"]
    assert ov["editor_cmd"] == ["nano"]
    assert ov["confirm"] is False
    assert ov["profile_dir"] == Path("/tmp/p")
    assert ov["run_root"] == Path("/tmp/r")
    assert cli._load_overrides({}) == {}  # nothing set → no overrides, all defaults win


def test_confirm_truthy_env_enables_gate():
    # DISCUSS_CONFIRM with a non-falsey value keeps the gate ON.
    assert cli._load_overrides({"DISCUSS_CONFIRM": "1"})["confirm"] is True


def test_main_without_target_class_fails_loud(monkeypatch, capsys):
    # FR-014: with no class configured, main must fail LOUD with guidance and a non-zero
    # exit — never crash with an IndexError, and never reach run().
    monkeypatch.delenv("DISCUSS_TARGET_CLASSES", raising=False)
    monkeypatch.setattr(cli, "_load_overrides", lambda env=None: {})

    def must_not_run(**kwargs):
        raise AssertionError("run() must not be called when no class is configured")

    monkeypatch.setattr(cli, "run", must_not_run)
    rc = cli.main()
    assert rc != 0
    out = capsys.readouterr().out.lower()
    assert "discuss_target_classes" in out  # the env var the operator must set


def test_main_wires_run_and_returns_zero(monkeypatch, tmp_path):
    # FR-001: the console entry builds real deps and delegates to run(), returning 0 on
    # success. run() itself is stubbed so no browser/portal is touched here.
    monkeypatch.setenv("DISCUSS_TARGET_CLASSES", "_x_1")
    calls = {}

    def fake_run(**kwargs):
        calls.update(kwargs)

    monkeypatch.setattr(cli, "run", fake_run)
    rc = cli.main()
    assert rc == 0
    assert calls["adapter"] is cli.portal_adapter
    assert callable(calls["browser_factory"])
    assert isinstance(calls["today"], dt.date)
    assert calls["config"].target_classes == ["_x_1"]  # env flowed into the config

    # the built browser_factory must open the PERSISTENT context (no creds) — exercise it
    # with the live call stubbed so it touches no real browser.
    seen = {}

    def fake_open(profile_dir):
        seen["profile_dir"] = profile_dir
        return ("ctx", "page")

    monkeypatch.setattr(cli.browser, "open_persistent_context", fake_open)
    assert calls["browser_factory"]() == ("ctx", "page")
    assert seen["profile_dir"] == cli.Config.load().profile_dir


def test_confirm_via_input_accepts_only_explicit_yes(monkeypatch):
    # FR-005: the default gate proceeds ONLY on an explicit yes; anything else declines.
    monkeypatch.setattr("builtins.input", lambda prompt: "y")
    assert cli._confirm_via_input("ok? ") is True
    monkeypatch.setattr("builtins.input", lambda prompt: "")
    assert cli._confirm_via_input("ok? ") is False
    monkeypatch.setattr("builtins.input", lambda prompt: "nope")
    assert cli._confirm_via_input("ok? ") is False


def test_main_reports_discuss_error_and_returns_one(monkeypatch):
    # FR-014: a fail-loud DiscussError from the pipeline is reported to the operator and
    # surfaces as a non-zero exit, not a traceback.
    monkeypatch.setenv("DISCUSS_TARGET_CLASSES", "_x_1")

    def fake_run(**kwargs):
        raise NoUpcomingDiscussion("no discussion has an upcoming due date")

    monkeypatch.setattr(cli, "run", fake_run)
    rc = cli.main()
    assert rc == 1
