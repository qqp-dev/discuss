"""Filesystem handoff between the orchestrator and the Claude Code session.

The orchestrator writes `prompt.md` + the workflow `CLAUDE.md` into a per-run dir,
launches the session there, and reads `response.md` back. Files are the entire handoff
contract — durable, so the final response is never lost if a downstream step fails
(FR-015). Launching `claude` itself is T008's `run_session`.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from shutil import which
from datetime import datetime
from pathlib import Path

from .errors import DiscussError, EmptyResponse

# Handoff filenames live here once (no duplicated string literals).
PROMPT_FILE = "prompt.md"
RESPONSE_FILE = "response.md"
WORKFLOW_FILE = "CLAUDE.md"

# The primed workflow template lives at the repo-root `templates/` dir (sibling of `src/`).
WORKFLOW_TEMPLATE = Path(__file__).resolve().parents[2] / "templates" / "workflow-CLAUDE.md"

# The interactive session command. `claude` auto-reads CLAUDE.md from its cwd.
# Resolve to absolute path so subprocess can find it regardless of venv PATH stripping.
_CLAUDE_BIN = which("claude") or str(Path.home() / ".local/bin/claude")
SESSION_CMD = [_CLAUDE_BIN]
# Env var the workflow uses to open the GUI editor (see templates/workflow-CLAUDE.md).
EDITOR_ENV_VAR = "DISCUSS_EDITOR"


def make_run_dir(run_root) -> Path:
    """Create and return a unique per-run working directory under `run_root`.

    Uses `mkdtemp` for collision-free uniqueness with a human-readable timestamp prefix.
    """
    root = Path(run_root)
    root.mkdir(parents=True, exist_ok=True)
    prefix = datetime.now().strftime("run-%Y%m%d-%H%M%S-")
    return Path(tempfile.mkdtemp(prefix=prefix, dir=root))


def write_prompt(run_dir, prompt_text, meta) -> Path:
    """Write the extracted prompt plus its metadata to `run_dir/prompt.md` (FR-006)."""
    path = Path(run_dir) / PROMPT_FILE
    header = "\n".join(f"{key}: {value}" for key, value in (meta or {}).items())
    body = prompt_text if prompt_text.endswith("\n") else prompt_text + "\n"
    content = (header + "\n\n" + body) if header else body
    path.write_text(content, encoding="utf-8")
    return path


def render_workflow(run_dir, template_path) -> Path:
    """Copy the primed workflow template into `run_dir/CLAUDE.md` (FR-007).

    `claude` auto-reads `CLAUDE.md` from its cwd, so placing it here is the priming
    contract — no fragile command-line flag.
    """
    dest = Path(run_dir) / WORKFLOW_FILE
    shutil.copyfile(Path(template_path), dest)
    return dest


def read_response(run_dir) -> str:
    """Read `run_dir/response.md` stripped; raise `EmptyResponse` if missing or blank.

    A missing or whitespace-only file must never be treated as a valid response
    (FR-012/FR-014) — the caller relies on this to refuse write-back.
    """
    path = Path(run_dir) / RESPONSE_FILE
    if not path.exists():
        raise EmptyResponse(f"no {RESPONSE_FILE} found in {run_dir}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise EmptyResponse(f"{RESPONSE_FILE} is empty or whitespace-only in {run_dir}")
    return text


def _session_command(editor_cmd) -> tuple[list[str], dict]:
    """Build the (command, env) for the interactive `claude` session.

    The editor command is exposed to the session via `DISCUSS_EDITOR` so the workflow
    can open the GUI editor with a blocking wait flag.
    """
    env = {**os.environ, EDITOR_ENV_VAR: " ".join(editor_cmd)}
    kickoff = (
        "Read prompt.md in this directory. "
        "Then follow the steps in CLAUDE.md exactly: surface the key angles and tensions in the prompt, "
        "ask me for my stance, main points, and any sources or evidence I want to use — "
        "and wait for my answer before drafting anything."
    )
    cmd = list(SESSION_CMD) + ["--model", "claude-opus-4-8", "--effort", "xhigh", kickoff]
    return cmd, env


def run_session(run_dir, editor_cmd, template_path=WORKFLOW_TEMPLATE) -> str:
    """Render the workflow, run the blocking `claude` session, return the response (FR-007).

    Renders the primed workflow into `run_dir/CLAUDE.md`, launches `claude` interactively
    with `cwd=run_dir` (blocking until the operator exits), then returns the saved
    response. A non-zero session exit aborts the run; a missing/blank response raises
    `EmptyResponse` (via `read_response`).
    """
    run_dir = Path(run_dir)
    render_workflow(run_dir, template_path)
    cmd, env = _session_command(editor_cmd)
    result = subprocess.run(cmd, cwd=run_dir, env=env)
    if result.returncode != 0:
        raise DiscussError(f"claude session exited with code {result.returncode}")
    return read_response(run_dir)
