import subprocess

import pytest

from discuss import handoff
from discuss.errors import DiscussError, EmptyResponse


def test_write_prompt_creates_prompt_md(tmp_path):
    # FR-006: extracted prompt lands in the run dir as prompt.md.
    rd = handoff.make_run_dir(tmp_path)
    p = handoff.write_prompt(rd, "Discuss X.", {"title": "Wk1", "due": "2026-06-08"})
    assert p.name == "prompt.md" and "Discuss X." in p.read_text()


def test_write_prompt_includes_meta(tmp_path):
    # FR-006: the run carries the discussion's title + due date; write_prompt must persist
    # the meta alongside the prompt (would catch meta being silently dropped).
    rd = handoff.make_run_dir(tmp_path)
    p = handoff.write_prompt(rd, "Discuss X.", {"title": "Wk1", "due": "2026-06-08"})
    text = p.read_text()
    assert "Wk1" in text and "2026-06-08" in text


def test_read_response_returns_saved_text(tmp_path):
    # FR-009: the saved response.md is the final response, returned stripped of edges.
    rd = handoff.make_run_dir(tmp_path)
    (rd / "response.md").write_text("My edited answer.\n")
    assert handoff.read_response(rd) == "My edited answer."


def test_read_response_empty_raises(tmp_path):
    # FR-012/FR-014: a whitespace-only draft must not be treated as a valid response.
    rd = handoff.make_run_dir(tmp_path)
    (rd / "response.md").write_text("   \n")
    with pytest.raises(EmptyResponse):
        handoff.read_response(rd)


def test_read_response_missing_raises(tmp_path):
    # edge: no response.md at all (session never wrote one) → EmptyResponse, not a
    # FileNotFoundError leaking out of the handoff layer.
    rd = handoff.make_run_dir(tmp_path)
    with pytest.raises(EmptyResponse):
        handoff.read_response(rd)


def test_run_dirs_unique(tmp_path):
    # edge: each run gets its own dir so back-to-back runs never overwrite each other.
    a = handoff.make_run_dir(tmp_path)
    b = handoff.make_run_dir(tmp_path)
    assert a != b and a.is_dir() and b.is_dir()


def test_render_workflow_copies_template_to_claude_md(tmp_path):
    # FR-007: the primed workflow is placed at run_dir/CLAUDE.md so `claude` auto-reads
    # it from cwd (would catch a wrong destination filename breaking the priming contract).
    template = tmp_path / "tpl.md"
    template.write_text("# primed workflow\nread prompt.md\n")
    rd = handoff.make_run_dir(tmp_path)
    dest = handoff.render_workflow(rd, template)
    assert dest.name == "CLAUDE.md"
    assert dest.read_text() == "# primed workflow\nread prompt.md\n"


def test_run_session_invokes_claude_in_run_dir(tmp_path, monkeypatch):
    # FR-007: the session runs `claude` in the run dir (so it auto-reads CLAUDE.md) with
    # the editor exposed via env, then returns the saved response.
    rd = handoff.make_run_dir(tmp_path)
    (rd / "response.md").write_text("final text")
    calls = {}

    def fake_run(cmd, cwd=None, env=None, **kw):
        calls.update(cmd=cmd, cwd=cwd, env=env)

        class R:
            returncode = 0

        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    out = handoff.run_session(rd, ["code", "--wait"])
    assert calls["cwd"] == rd
    assert calls["cmd"][0] == "claude"
    assert calls["env"]["DISCUSS_EDITOR"] == "code --wait"
    assert out == "final text"


def test_run_session_nonzero_exit_raises(tmp_path, monkeypatch):
    # edge: a failed/aborted claude session (non-zero exit) must raise, not silently
    # proceed with a possibly-stale response.
    rd = handoff.make_run_dir(tmp_path)
    (rd / "response.md").write_text("stale text")

    def fake_run(cmd, cwd=None, env=None, **kw):
        class R:
            returncode = 1

        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(DiscussError):
        handoff.run_session(rd, ["code", "--wait"])


def test_run_session_empty_response_raises(tmp_path, monkeypatch):
    # edge: session exits cleanly but wrote no/blank response.md → EmptyResponse, so the
    # pipeline never proceeds to fill an empty draft.
    rd = handoff.make_run_dir(tmp_path)

    def fake_run(cmd, cwd=None, env=None, **kw):
        class R:
            returncode = 0

        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(EmptyResponse):
        handoff.run_session(rd, ["code", "--wait"])
