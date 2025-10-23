#!/bin/bash
# TODOIT CLI wrapper for writing Deep Research results
# Usage: ./todoit-write-research-result.sh <source_name> <status> [error_message] [search_url]
# Output: JSON with success status

set -e

SOURCE_NAME="$1"
STATUS="$2"
ERROR_MSG="${3:-}"
SEARCH_URL="${4:-}"

TARGET_LIST="gemini-au-deep-research"

# ============================================================================
# Validation
# ============================================================================

if [ -z "$SOURCE_NAME" ] || [ -z "$STATUS" ]; then
  echo '{"success": false, "error": "Missing required parameters: source_name, status"}' >&2
  exit 1
fi

# Validate status (in_progress = success, failed = error)
if [[ ! "$STATUS" =~ ^(in_progress|failed|pending)$ ]]; then
  echo '{"success": false, "error": "Invalid status. Must be: in_progress, failed, or pending"}' >&2
  exit 1
fi

ERRORS=()

# ============================================================================
# PHASE 1: Update item status
# ============================================================================

# Update item status (not subitem - research tasks are item-level)
OUTPUT=$(echo "y" | todoit item status --list "$TARGET_LIST" --item "$SOURCE_NAME" --status "$STATUS" 2>&1)
if echo "$OUTPUT" | grep -q "❌"; then
  ERRORS+=("Failed to update status to $STATUS: $OUTPUT")
fi

# ============================================================================
# PHASE 2: Save SEARCH_URL if provided (success case)
# ============================================================================

if [ -n "$SEARCH_URL" ]; then
  OUTPUT=$(echo "y" | todoit item property set --list "$TARGET_LIST" --item "$SOURCE_NAME" --key SEARCH_URL --value "$SEARCH_URL" 2>&1)
  if echo "$OUTPUT" | grep -q "❌"; then
    ERRORS+=("Failed to set SEARCH_URL property: $OUTPUT")
  fi
fi

# ============================================================================
# PHASE 3: Save error message if provided (failure case)
# ============================================================================

if [ -n "$ERROR_MSG" ]; then
  # Truncate to 500 chars
  ERROR_TRUNCATED="${ERROR_MSG:0:500}"
  OUTPUT=$(echo "y" | todoit item property set --list "$TARGET_LIST" --item "$SOURCE_NAME" --key ERROR --value "$ERROR_TRUNCATED" 2>&1)
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
    --arg url "$SEARCH_URL" \
    '{
      success: true,
      status: $status,
      source_name: $source,
      search_url: ($url | if . == "" then null else . end),
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
