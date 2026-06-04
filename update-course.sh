#!/usr/bin/env bash
# Update the saved course ID and close.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.env"

echo ""
echo "========================================"
echo "   Discuss — update course ID"
echo "========================================"
echo ""
echo "Find your course ID in the UOPX portal URL:"
echo "  https://vle.phoenix.edu/ultra/courses/_XXXXXXX_1/outline"
echo ""

if [ -f "$CONFIG_FILE" ]; then
    current="$(grep DISCUSS_TARGET_CLASSES "$CONFIG_FILE" | cut -d= -f2)"
    echo "Current course ID: $current"
    echo ""
fi

while true; do
    read -rp "New course ID: " course_id
    if [ -n "$course_id" ]; then
        break
    fi
    echo "  Cannot be empty. Try again."
done

printf 'DISCUSS_TARGET_CLASSES=%s\n' "$course_id" > "$CONFIG_FILE"

echo ""
echo "  Saved! You're ready to run Discuss."
echo ""
read -rp "Press Enter to close..."
