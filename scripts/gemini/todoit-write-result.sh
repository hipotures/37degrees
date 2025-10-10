#!/bin/bash
# TODOIT CLI wrapper for writing audio generation results
# Usage: ./todoit-write-result.sh <source_name> <subitem_key> <status> [error_message]
# Output: JSON with success status

set -e

SOURCE_NAME="$1"
SUBITEM_KEY="$2"
STATUS="$3"
ERROR_MSG="${4:-}"

TARGET_LIST="cc-au-notebooklm"

# ============================================================================
# Validation
# ============================================================================

if [ -z "$SOURCE_NAME" ] || [ -z "$SUBITEM_KEY" ] || [ -z "$STATUS" ]; then
  echo '{"success": false, "error": "Missing required parameters: source_name, subitem_key, status"}' >&2
  exit 1
fi

# Validate status
if [[ ! "$STATUS" =~ ^(completed|failed|pending)$ ]]; then
  echo '{"success": false, "error": "Invalid status. Must be: completed, failed, or pending"}' >&2
  exit 1
fi

ERRORS=()

# ============================================================================
# PHASE 1: Update subitem status
# ============================================================================

# For audio, we always update status (unlike image_gen where pending means no change)
OUTPUT=$(echo "y" | todoit item status --list "$TARGET_LIST" --item "$SOURCE_NAME" --subitem "$SUBITEM_KEY" --status "$STATUS" 2>&1)
if echo "$OUTPUT" | grep -q "❌"; then
  ERRORS+=("Failed to update status to $STATUS: $OUTPUT")
fi

# ============================================================================
# PHASE 2: Save error message if provided
# ============================================================================

if [ -n "$ERROR_MSG" ]; then
  # Truncate to 500 chars
  ERROR_TRUNCATED="${ERROR_MSG:0:500}"
  OUTPUT=$(echo "y" | todoit item property set --list "$TARGET_LIST" --item "$SOURCE_NAME" --subitem "$SUBITEM_KEY" --key ERROR --value "$ERROR_TRUNCATED" 2>&1)
  if echo "$OUTPUT" | grep -q "❌"; then
    ERRORS+=("Failed to set error property: $OUTPUT")
  fi
fi

# ============================================================================
# Return result
# ============================================================================

if [ ${#ERRORS[@]} -eq 0 ]; then
  jq -n \
    --arg status "$STATUS" \
    --arg source "$SOURCE_NAME" \
    --arg subitem "$SUBITEM_KEY" \
    '{
      success: true,
      status: $status,
      source_name: $source,
      subitem_key: $subitem,
      message: "All data saved successfully"
    }'
else
  ERROR_LIST=$(printf '%s\n' "${ERRORS[@]}" | jq -R . | jq -s .)
  jq -n \
    --argjson errors "$ERROR_LIST" \
    '{
      success: false,
      errors: $errors
    }'
  exit 1
fi
