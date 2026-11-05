"""T017 — orchestrator pipeline (FR-001/005/006/010/012/014/015).

The pipeline is exercised entirely with the injected fakes from ``fake_ctx`` (conftest):
no browser, no claude subprocess, no live portal. Each test asserts one ordering or safety
guarantee of ``cli.run``.
"""

import datetime as dt

import pytest

from discuss import cli, handoff
from discuss.errors import (
    DiscussError,
    EmptyResponse,
    FillVerifyFailed,
    NoUpcomingDiscussion,
    NotAuthenticated,
    SelectorMiss,
)
from discuss.portal_parse import Discussion


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
    assert "main post" in fake_ctx.gate_prompt


def test_mode_menu_is_used_when_no_mode_configured(fake_ctx):
    # The operator sees an explicit work-mode menu unless DISCUSS_MODE pins the mode.
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.mode_prompted is True


def test_confirm_disabled_skips_gate(fake_ctx):
    # WHERE the operator disabled it (config.confirm=False), no gate is shown and the run
    # proceeds straight through to the selected mode.
    fake_ctx.config.confirm = False
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.gate_prompt is None  # confirm() never called
    assert fake_ctx.adapter.filled is True


def test_no_upcoming_due_stops(fake_ctx):
    # FR-014: nothing upcoming → stop, no fill, with an explicit no-parseable-dates state.
    fake_ctx.adapter.discussions = []  # select_soonest_due → None
    with pytest.raises(NoUpcomingDiscussion) as caught:
        cli.run(**fake_ctx.kwargs)
    assert str(caught.value) == (
        "No upcoming discussion for class _577963_1. Discussions found: 0. "
        "Discussions with parseable due dates: 0. Parseable due-date range: none "
        "(no parseable due dates). Today: 2026-06-01. Saved the list page markup to "
        f"{fake_ctx.config.run_root / cli.LIST_SNAPSHOT_FILE}."
    )
    assert fake_ctx.adapter.list_calls == 1
    assert fake_ctx.adapter.filled is False


def test_no_upcoming_message_reports_list_and_date_range(fake_ctx):
    fake_ctx.adapter.discussions = [
        Discussion("Undated", None, "u0"),
        Discussion("Past one", dt.date(2026, 5, 1), "u1"),
        Discussion("Past two", dt.date(2026, 5, 20), "u2"),
    ]
    with pytest.raises(NoUpcomingDiscussion) as caught:
        cli.run(**fake_ctx.kwargs)
    assert str(caught.value) == (
        "No upcoming discussion for class _577963_1. Discussions found: 3. "
        "Discussions with parseable due dates: 2. Parseable due-date range: "
        "2026-05-01 to 2026-05-20. Today: 2026-06-01. Saved the list page markup to "
        f"{fake_ctx.config.run_root / cli.LIST_SNAPSHOT_FILE}."
    )
    assert fake_ctx.adapter.list_calls == 1


def test_no_upcoming_snapshots_the_list_page(fake_ctx):
    # The evidence behind a no-upcoming result is captured by the tool itself: the exact
    # list markup the selection was made from lands in the run root.
    fake_ctx.adapter.discussions = []
    with pytest.raises(NoUpcomingDiscussion):
        cli.run(**fake_ctx.kwargs)
    snapshot = fake_ctx.config.run_root / cli.LIST_SNAPSHOT_FILE
    assert snapshot.read_text(encoding="utf-8") == "<html><body>captured list markup</body></html>"


def test_no_upcoming_snapshot_failure_still_reports(fake_ctx, tmp_path):
    # A failed snapshot write is reported in the message, never raised over the result.
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("x", encoding="utf-8")
    fake_ctx.config.run_root = blocker
    fake_ctx.adapter.discussions = []
    with pytest.raises(NoUpcomingDiscussion) as caught:
        cli.run(**fake_ctx.kwargs)
    assert "Could not save the list page markup" in str(caught.value)


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


def test_peer_posts_written(fake_ctx):
    # Peer-response drafting carries visible classmate posts into the session as a durable
    # input file, so choosing two replies is based on the opened discussion page.
    fake_ctx.mode = cli.MODE_PEER
    cli.run(**fake_ctx.kwargs)
    text = (fake_ctx.run_dir / handoff.PEER_POSTS_FILE).read_text()
    assert "Student A" in text
    assert "A thoughtful classmate post." in text


def test_main_post_mode_does_not_require_peer_replies(fake_ctx):
    # Main-post work is now a focused mode: response.md is sufficient and peer-reply files
    # are not required before filling the top-level reply field.
    def session_without_peer_replies(run_dir, editor_cmd, template_path=None, require_response=True):
        (run_dir / handoff.RESPONSE_FILE).write_text("My edited final answer.\n", encoding="utf-8")
        return "My edited final answer."

    kwargs = fake_ctx.kwargs
    kwargs["session"] = session_without_peer_replies
    cli.run(**kwargs)
    assert fake_ctx.adapter.filled is True


def test_missing_peer_reply_aborts_peer_mode(fake_ctx):
    # In peer mode, the two peer replies are required outputs; if the session omits them,
    # stop loud and never fill the top-level reply field.
    fake_ctx.mode = cli.MODE_PEER

    def session_without_peer_replies(run_dir, editor_cmd, template_path=None, require_response=True):
        return ""

    kwargs = fake_ctx.kwargs
    kwargs["session"] = session_without_peer_replies
    with pytest.raises(EmptyResponse):
        cli.run(**kwargs)
    assert fake_ctx.adapter.filled is False


def test_peer_mode_drafts_replies_without_fill(fake_ctx):
    # Peer-reply mode creates the two required reply drafts and never writes into the portal.
    fake_ctx.mode = cli.MODE_PEER
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.adapter.filled is False
    assert (fake_ctx.run_dir / handoff.PEER_REPLY_FILES[0]).exists()
    assert (fake_ctx.run_dir / handoff.PEER_REPLY_FILES[1]).exists()
    assert "paste" in fake_ctx.last_message.lower()


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


def test_load_overrides_parses_env(tmp_path):
    # FR-005/Q4: cli gathers config from env into the overrides dict (config.py delegates
    # this gathering to the orchestrator). Comma-split classes, space-split editor, and an
    # explicit confirm-off are all parsed; absent vars contribute no key (defaults win).
    from pathlib import Path

    env = {
        "DISCUSS_TARGET_CLASSES": " _577963_1 , _x_2 ",
        "DISCUSS_EDITOR": "xed --wait",
        "DISCUSS_CONFIRM": "false",
        "DISCUSS_PROFILE_DIR": "/tmp/p",
        "DISCUSS_RUN_ROOT": "/tmp/r",
        "DISCUSS_MODE": "peer",
    }
    missing_dotenv = tmp_path / "does-not-exist"
    ov = cli._load_overrides(env, dotenv_path=missing_dotenv)
    assert ov["target_classes"] == ["_577963_1", "_x_2"]
    assert ov["editor_cmd"] == ["xed", "--wait"]
    assert ov["confirm"] is False
    assert ov["profile_dir"] == Path("/tmp/p")
    assert ov["run_root"] == Path("/tmp/r")
    assert ov["mode"] == "peer"
    assert cli._load_overrides({}, dotenv_path=missing_dotenv) == {}


def test_project_dotenv_is_fallback_and_process_environment_wins(monkeypatch, tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    dotenv = project / ".env"
    dotenv.write_text(
        "# saved launcher config\n"
        "DISCUSS_TARGET_CLASSES=_from_file_1\n"
        "DISCUSS_CONFIRM=false\n"
        "OTHER_KEY=ignored\n",
        encoding="utf-8",
    )
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    monkeypatch.setattr(cli, "_DOTENV_FILE", dotenv)

    file_only = cli._load_overrides({})
    assert file_only["target_classes"] == ["_from_file_1"]
    assert file_only["confirm"] is False

    process_wins = cli._load_overrides(
        {"DISCUSS_TARGET_CLASSES": "_from_process_1", "DISCUSS_CONFIRM": "true"}
    )
    assert process_wins["target_classes"] == ["_from_process_1"]
    assert process_wins["confirm"] is True


def test_confirm_truthy_env_enables_gate(tmp_path):
    # DISCUSS_CONFIRM with a non-falsey value keeps the gate ON.
    assert cli._load_overrides(
        {"DISCUSS_CONFIRM": "1"}, dotenv_path=tmp_path / "missing"
    )["confirm"] is True


def test_discuss_mode_config_skips_menu(fake_ctx):
    # DISCUSS_MODE/main config pins the mode and avoids the interactive menu.
    fake_ctx.config.mode = "peer"
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.mode_prompted is False
    assert fake_ctx.adapter.filled is False


def test_invalid_discuss_mode_fails_loud(fake_ctx):
    fake_ctx.config.mode = "everything"
    with pytest.raises(DiscussError):
        cli.run(**fake_ctx.kwargs)


def test_choose_mode_input_accepts_menu_numbers(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "2")
    assert cli._choose_mode_via_input() == cli.MODE_PEER


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
