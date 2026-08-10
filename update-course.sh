#!/usr/bin/env bash
# Update the saved course ID and close.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.env"
# shellcheck source=course-config.sh
source "$SCRIPT_DIR/course-config.sh"

echo ""
echo "========================================"
echo "   Discuss — update course ID"
echo "========================================"
echo ""
echo "Find your course ID in the UOPX portal URL:"
echo "  https://vle.phoenix.edu/ultra/courses/_XXXXXXX_1/outline"
echo ""

current="$(discuss_current_course_id "$CONFIG_FILE")"
if [ -n "$current" ]; then
    echo "Current course ID: $current"
    echo ""
fi

while true; do
    read -rp "New course ID: " course_id
    if discuss_validate_course_id "$course_id"; then
        break
    fi
done

discuss_save_course_id "$CONFIG_FILE" "$course_id"

echo ""
echo "  Saved course ID: $course_id"
echo "  File: $CONFIG_FILE"
echo "  You're ready to run Discuss."
echo ""
read -rp "Press Enter to close..."
