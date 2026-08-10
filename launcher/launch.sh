#!/usr/bin/env bash
# Discuss launcher. Double-click or pin to taskbar — no terminal needed.
set -euo pipefail

LAUNCHER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$LAUNCHER_DIR")"
CONFIG_FILE="$PROJECT_DIR/.env"
DISCUSS_BIN="$PROJECT_DIR/.venv/bin/discuss"

# ── Preflight ─────────────────────────────────────────────────────────────────
_die() {
    local msg="$1"
    if command -v zenity >/dev/null 2>&1; then
        zenity --error --title="Discuss" --text="$msg" 2>/dev/null || true
    elif command -v notify-send >/dev/null 2>&1; then
        notify-send "Discuss — error" "$msg"
    fi
    echo "discuss: $msg" >&2
    exit 1
}

if [ ! -f "$DISCUSS_BIN" ]; then
    _die "Setup hasn't been run yet.\n\nOpen a terminal and run:\n  $PROJECT_DIR/setup.sh"
fi

if [ ! -f "$CONFIG_FILE" ]; then
    _die "No course ID configured.\n\nOpen a terminal and run:\n  $PROJECT_DIR/setup.sh"
fi

# The CLI reads CONFIG_FILE itself, so direct and launcher runs share one parser and any
# process-environment override remains authoritative.

# ── Build the command the terminal will run ───────────────────────────────────
# Keep the window open after discuss exits so the user can read any output.
INNER="$DISCUSS_BIN; echo ''; echo 'Done — close this window when ready.'; exec bash"

# ── Launch in whatever terminal is available ──────────────────────────────────
if command -v gnome-terminal >/dev/null 2>&1; then
    exec gnome-terminal --title="Discuss" -- bash -c "$INNER"
elif command -v x-terminal-emulator >/dev/null 2>&1; then
    exec x-terminal-emulator -T "Discuss" -e bash -c "$INNER"
elif command -v xfce4-terminal >/dev/null 2>&1; then
    exec xfce4-terminal --title="Discuss" -e "bash -c '$INNER'"
elif command -v konsole >/dev/null 2>&1; then
    exec konsole --title "Discuss" -e bash -c "$INNER"
elif command -v xterm >/dev/null 2>&1; then
    exec xterm -T "Discuss" -e bash -c "$INNER"
else
    _die "No terminal emulator found.\n\nInstall gnome-terminal or xterm, then try again."
fi
