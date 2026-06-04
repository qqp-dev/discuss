#!/usr/bin/env bash
# One-time setup for discuss. Run this once; after that use the desktop launcher.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.env"
UV="$HOME/.local/bin/uv"

echo ""
echo "========================================"
echo "   discuss — first-time setup"
echo "========================================"
echo ""

# ── 1. uv ────────────────────────────────────────────────────────────────────
if ! command -v uv >/dev/null 2>&1 && ! [ -f "$UV" ]; then
    echo "Installing package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo ""
fi
command -v uv >/dev/null 2>&1 && UV="$(command -v uv)"

# ── 2. Python environment ─────────────────────────────────────────────────────
echo "Setting up Python environment..."
"$UV" venv --python 3.12 "$SCRIPT_DIR/.venv" --quiet 2>/dev/null || \
    "$UV" venv --python 3.11 "$SCRIPT_DIR/.venv" --quiet 2>/dev/null || true
"$UV" pip install -e "$SCRIPT_DIR/.[dev]" --quiet
echo "  done."
echo ""

# ── 3. Browser ────────────────────────────────────────────────────────────────
echo "Installing browser (one-time download, ~175 MB)..."
"$SCRIPT_DIR/.venv/bin/python" -m playwright install chromium --quiet 2>/dev/null || \
    "$SCRIPT_DIR/.venv/bin/python" -m playwright install chromium
echo "  done."
echo ""

# ── 4. Course ID ──────────────────────────────────────────────────────────────
if [ -f "$CONFIG_FILE" ]; then
    current="$(grep DISCUSS_TARGET_CLASSES "$CONFIG_FILE" | cut -d= -f2)"
    echo "Current course ID: $current"
    read -rp "Press Enter to keep it, or type a new one: " new_id
    if [ -n "$new_id" ]; then
        printf 'DISCUSS_TARGET_CLASSES=%s\n' "$new_id" > "$CONFIG_FILE"
        echo "  saved."
    else
        echo "  keeping $current."
    fi
else
    echo "Find your course ID in the UOPX portal URL:"
    echo "  https://vle.phoenix.edu/ultra/courses/_XXXXXXX_1/outline"
    echo ""
    while true; do
        read -rp "Enter your course ID (e.g. _577963_1): " course_id
        if [ -n "$course_id" ]; then
            break
        fi
        echo "  Course ID cannot be empty. Try again."
    done
    printf 'DISCUSS_TARGET_CLASSES=%s\n' "$course_id" > "$CONFIG_FILE"
    echo "  saved."
fi
echo ""

# ── 5. Desktop launchers ─────────────────────────────────────────────────────
echo "Installing desktop launchers..."
chmod +x "$SCRIPT_DIR/launcher/launch.sh"
chmod +x "$SCRIPT_DIR/update-course.sh"
mkdir -p "$HOME/.local/share/applications"

cat > "$HOME/.local/share/applications/discuss.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Discuss
Comment=Draft this week's UOPX discussion post with assistance (fills the reply, never submits)
Exec=$SCRIPT_DIR/launcher/launch.sh
Terminal=false
Categories=Education;
EOF

cat > "$HOME/.local/share/applications/discuss-update-course.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Discuss — Update Course ID
Comment=Update the saved UOPX course ID (do this when your class changes)
Exec=gnome-terminal --title="Update Course ID" -- bash -c "$SCRIPT_DIR/update-course.sh"
Terminal=false
Categories=Education;
EOF

update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

if [ -d "$HOME/Desktop" ]; then
    cp "$HOME/.local/share/applications/discuss.desktop" "$HOME/Desktop/discuss.desktop"
    cp "$HOME/.local/share/applications/discuss-update-course.desktop" \
       "$HOME/Desktop/discuss-update-course.desktop"
    chmod +x "$HOME/Desktop/discuss.desktop" "$HOME/Desktop/discuss-update-course.desktop"
    echo "  two shortcuts added to your Desktop."
else
    echo "  added to applications menu."
fi
echo ""

# ── Done ──────────────────────────────────────────────────────────────────────
echo "========================================"
echo "   Setup complete!"
echo ""
echo "   To use: open 'Discuss' from your"
echo "   applications menu (or Desktop)."
echo "========================================"
echo ""
