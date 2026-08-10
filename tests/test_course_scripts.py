"""The two operator-facing course-ID flows preserve the shared project .env."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _script_checkout(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    checkout = tmp_path / "discuss"
    checkout.mkdir()
    (checkout / "launcher").mkdir()
    for relative in ("setup.sh", "update-course.sh", "course-config.sh", "launcher/launch.sh"):
        source = ROOT / relative
        target = checkout / relative
        shutil.copyfile(source, target)

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    uv = fake_bin / "uv"
    uv.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "if [[ ${1:-} == venv ]]; then\n"
        "  for arg in \"$@\"; do\n"
        "    if [[ $arg == */.venv ]]; then venv=$arg; fi\n"
        "  done\n"
        "  mkdir -p \"$venv/bin\"\n"
        "  printf '#!/usr/bin/env bash\\nexit 0\\n' > \"$venv/bin/python\"\n"
        "  chmod +x \"$venv/bin/python\"\n"
        "fi\n",
        encoding="utf-8",
    )
    uv.chmod(0o755)

    home = tmp_path / "home"
    home.mkdir()
    env = os.environ.copy()
    env.update({"HOME": str(home), "PATH": f"{fake_bin}:{env['PATH']}"})
    return checkout, env


@pytest.mark.parametrize("script_name", ["update-course.sh", "setup.sh"])
def test_course_id_scripts_preserve_env_validate_and_deduplicate(tmp_path, script_name):
    checkout, env = _script_checkout(tmp_path)
    env_file = checkout / ".env"
    env_file.write_text(
        "OTHER_KEY=keep-me\n"
        "DISCUSS_TARGET_CLASSES=_old_1\n"
        "TAIL_KEY=also-keep\n"
        "DISCUSS_TARGET_CLASSES=_stale_duplicate_1\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["bash", str(checkout / script_name)],
        cwd=checkout,
        env=env,
        input=(
            "bad value\n"
            "https://vle.phoenix.edu/ultra/courses/_wrong_1/outline\n"
            "_new_1\n"
            "\n"
        ),
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    assert "whitespace" in output
    assert "URL" in output
    assert "_new_1" in output
    assert str(env_file) in output
    assert env_file.read_text(encoding="utf-8") == (
        "OTHER_KEY=keep-me\n"
        "DISCUSS_TARGET_CLASSES=_new_1\n"
        "TAIL_KEY=also-keep\n"
    )


@pytest.mark.parametrize("script_name", ["update-course.sh", "setup.sh"])
def test_course_id_scripts_append_target_key_when_absent(tmp_path, script_name):
    checkout, env = _script_checkout(tmp_path)
    env_file = checkout / ".env"
    env_file.write_text("OTHER_KEY=keep-me\nTAIL_KEY=also-keep\n", encoding="utf-8")

    result = subprocess.run(
        ["bash", str(checkout / script_name)],
        cwd=checkout,
        env=env,
        input="_new_1\n\n",
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    assert "_new_1" in output
    assert str(env_file) in output
    assert env_file.read_text(encoding="utf-8") == (
        "OTHER_KEY=keep-me\n"
        "TAIL_KEY=also-keep\n"
        "DISCUSS_TARGET_CLASSES=_new_1\n"
    )
