#!/usr/bin/env bash
# Shared helpers for the two operator-facing course-ID writers.

discuss_current_course_id() {
    local config_file="$1"
    local line
    if [[ -f "$config_file" ]]; then
        while IFS= read -r line || [[ -n "$line" ]]; do
            if [[ "$line" == DISCUSS_TARGET_CLASSES=* ]]; then
                printf '%s\n' "${line#*=}"
                return 0
            fi
        done < "$config_file"
    fi
}

discuss_validate_course_id() {
    local course_id="$1"
    if [[ -z "$course_id" ]]; then
        echo "  Course ID cannot be empty. Try again."
        return 1
    fi
    if [[ "$course_id" =~ [[:space:]] ]]; then
        echo "  Course ID cannot contain whitespace. Enter only the ID from the URL."
        return 1
    fi
    if [[ "$course_id" =~ ^[[:alpha:]][[:alnum:]+.-]*:// ]]; then
        echo "  Course ID cannot be a URL. Enter only the ID after /courses/."
        return 1
    fi
    return 0
}

discuss_save_course_id() {
    local config_file="$1"
    local course_id="$2"
    local temp_file line
    local found=false

    discuss_validate_course_id "$course_id" || return 1
    temp_file="$(mktemp "${config_file}.tmp.XXXXXX")"

    if ! {
        if [[ -f "$config_file" ]]; then
            while IFS= read -r line || [[ -n "$line" ]]; do
                if [[ "$line" == DISCUSS_TARGET_CLASSES=* ]]; then
                    if [[ "$found" == false ]]; then
                        printf 'DISCUSS_TARGET_CLASSES=%s\n' "$course_id"
                        found=true
                    fi
                else
                    printf '%s\n' "$line"
                fi
            done < "$config_file"
        fi
        if [[ "$found" == false ]]; then
            printf 'DISCUSS_TARGET_CLASSES=%s\n' "$course_id"
        fi
    } > "$temp_file"; then
        rm -f -- "$temp_file"
        return 1
    fi

    if ! mv -- "$temp_file" "$config_file"; then
        rm -f -- "$temp_file"
        return 1
    fi
}
