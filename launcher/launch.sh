#!/usr/bin/env bash
# Discuss launcher: open a terminal emulator running the `discuss` pipeline.
#
# The `discuss` console-script must be on PATH — install the project into a venv
# (`pip install -e .[dev]`) and ensure that venv's bin is on PATH for your desktop
# session (see README). This shim only finds a terminal and runs `discuss` in it; the
# interactive Claude Code session and the human-paced portal steps happen inside.
set -euo pipefail

CMD="discuss"

# Prefer the Debian/Ubuntu alternatives wrapper, then common emulators. Each launches
# the terminal with `discuss` as its program. If none is found we fail loud with the
# documented fallback (run `discuss` directly).
if command -v x-terminal-emulator >/dev/null 2>&1; then
    exec x-terminal-emulator -e "$CMD"
elif command -v gnome-terminal >/dev/null 2>&1; then
    exec gnome-terminal -- bash -lc "$CMD"
elif command -v konsole >/dev/null 2>&1; then
    exec konsole -e "$CMD"
elif command -v xfce4-terminal >/dev/null 2>&1; then
    exec xfce4-terminal -e "$CMD"
elif command -v xterm >/dev/null 2>&1; then
    exec xterm -e "$CMD"
else
    echo "discuss: no supported terminal emulator found" >&2
    echo "  (tried x-terminal-emulator, gnome-terminal, konsole, xfce4-terminal, xterm)" >&2
    echo "  Fallback: open a terminal yourself and run: discuss" >&2
    exit 1
fi
