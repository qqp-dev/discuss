"""Run configuration (FR-005, Q4).

`Config` resolves the operator-tunable knobs the pipeline needs. `Config.load(overrides)`
merges a dict of overrides over the documented defaults; unknown keys are ignored.

The orchestrator (`cli.py`) is responsible for gathering values from the project-root
`.env` and process environment into that overrides dict. This module stays a pure
dataclass + merge.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from pathlib import Path

# The package is installed editable from this repository, so resolving from this source
# file anchors every launch path to the project rather than the caller's working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Defaults live here once (no duplicated literals).
DEFAULT_EDITOR_CMD: list[str] = ["xed", "--wait"]
DEFAULT_PROFILE_DIR = PROJECT_ROOT / "profile"  # persistent browser profile (gitignored)
DEFAULT_RUN_ROOT = PROJECT_ROOT / "runs"  # where per-run dirs are created (gitignored)


@dataclass
class Config:
    """Resolved run configuration.

    - `profile_dir`: persistent Playwright profile reusing the operator's live session.
    - `target_classes`: class identifier(s) to search; the operator sets these.
    - `confirm`: the pre-extraction confirmation gate; defaults **on** (FR-005).
    - `editor_cmd`: the `--wait`-capable GUI editor command (FR-009).
    - `run_root`: parent directory for per-run working dirs.
    - `mode`: optional non-interactive work-mode shortcut; absent means show the menu.
    """

    profile_dir: Path = DEFAULT_PROFILE_DIR
    target_classes: list[str] = field(default_factory=list)
    confirm: bool = True
    editor_cmd: list[str] = field(default_factory=lambda: list(DEFAULT_EDITOR_CMD))
    run_root: Path = DEFAULT_RUN_ROOT
    mode: str | None = None

    @classmethod
    def load(cls, overrides: dict | None = None) -> "Config":
        """Build a Config from defaults with `overrides` merged over them.

        Unknown keys are ignored so a stale/typo'd config entry never crashes a run.
        """
        overrides = overrides or {}
        known = {f.name for f in fields(cls)}
        kwargs = {k: v for k, v in overrides.items() if k in known}
        return cls(**kwargs)
