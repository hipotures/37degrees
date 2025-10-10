#!/bin/bash
# TODOIT CLI wrapper for writing audio download results
# Usage: ./todoit-write-download-result.sh <book_key> <subitem_key> <status> <file_path> [error_message]
# Output: JSON with success status

set -e

BOOK_KEY="$1"
SUBITEM_KEY="$2"
STATUS="$3"
FILE_PATH="$4"
ERROR_MSG="${5:-}"

TARGET_LIST="cc-au-notebooklm"

# ============================================================================
# Validation
# ============================================================================

if [ -z "$BOOK_KEY" ] || [ -z "$SUBITEM_KEY" ] || [ -z "$STATUS" ]; then
  echo '{"success": false, "error": "Missing required parameters: book_key, subitem_key, status"}' >&2
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

OUTPUT=$(echo "y" | todoit item status --list "$TARGET_LIST" --item "$BOOK_KEY" --subitem "$SUBITEM_KEY" --status "$STATUS" 2>&1)
if echo "$OUTPUT" | grep -q "❌"; then
  ERRORS+=("Failed to update status to $STATUS: $OUTPUT")
fi

# ============================================================================
# PHASE 2: Save file path if provided
# ============================================================================

if [ -n "$FILE_PATH" ]; then
  OUTPUT=$(echo "y" | todoit item property set --list "$TARGET_LIST" --item "$SUBITEM_KEY" --parent "$BOOK_KEY" --key file_path --value "$FILE_PATH" 2>&1)
  if echo "$OUTPUT" | grep -q "❌"; then
    ERRORS+=("Failed to set file_path property: $OUTPUT")
  fi
fi

# ============================================================================
# PHASE 3: Save error message if provided
# ============================================================================

if [ -n "$ERROR_MSG" ]; then
  # Truncate to 500 chars
  ERROR_TRUNCATED="${ERROR_MSG:0:500}"
  OUTPUT=$(echo "y" | todoit item property set --list "$TARGET_LIST" --item "$SUBITEM_KEY" --parent "$BOOK_KEY" --key ERROR --value "$ERROR_TRUNCATED" 2>&1)
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
    --arg book "$BOOK_KEY" \
    --arg subitem "$SUBITEM_KEY" \
    --arg file "$FILE_PATH" \
    '{
      success: true,
      status: $status,
      book_key: $book,
      subitem_key: $subitem,
      file_path: ($file | if . == "" then null else . end),
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
