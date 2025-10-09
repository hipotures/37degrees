#!/bin/bash
# TODOIT CLI wrapper for writing image generation results
# Usage: ./todoit-write-result.sh <list_key> <scene_key> <thread_id> <status> [project_id] [error_message]
# Output: JSON with success status

set -e

LIST_KEY="$1"
SCENE_KEY="$2"
THREAD_ID="$3"
STATUS="$4"
PROJECT_ID="${5:-}"
ERROR_MSG="${6:-}"

if [ -z "$LIST_KEY" ] || [ -z "$SCENE_KEY" ] || [ -z "$THREAD_ID" ] || [ -z "$STATUS" ]; then
  echo '{"success": false, "error": "Missing required parameters: list_key, scene_key, thread_id, status"}' >&2
  exit 1
fi

# Validate status
if [[ ! "$STATUS" =~ ^(completed|failed|pending)$ ]]; then
  echo '{"success": false, "error": "Invalid status. Must be: completed, failed, or pending"}' >&2
  exit 1
fi

# CRITICAL: Don't save anything if thread_id is a placeholder or invalid
if [[ "$THREAD_ID" =~ ^FAILED.*$ ]] || [[ "$THREAD_ID" == "null" ]] || [[ "$THREAD_ID" == "undefined" ]]; then
  echo '{"success": false, "error": "Cannot save with placeholder thread_id. Playwright script must provide real thread ID."}' >&2
  exit 1
fi

ERRORS=()

# 1. Save thread_id to image_gen subtask (always, even on error)
OUTPUT=$(echo "y" | todoit item property set --list "$LIST_KEY" --item "$SCENE_KEY" --subitem image_gen --key thread_id --value "$THREAD_ID" 2>&1)
if echo "$OUTPUT" | grep -q "❌"; then
  ERRORS+=("Failed to set thread_id: $OUTPUT")
fi

# 2. Save project_id to list if provided (only when new project created)
if [ -n "$PROJECT_ID" ]; then
  # Check if project_id already exists
  EXISTING_PROJECT=$(TODOIT_OUTPUT_FORMAT=json todoit list property get --list "$LIST_KEY" --key project_id 2>/dev/null | jq -r '.data[0].project_id // empty' || echo "")

  if [ -z "$EXISTING_PROJECT" ]; then
    OUTPUT=$(echo "y" | todoit list property set --list "$LIST_KEY" --key project_id --value "$PROJECT_ID" 2>&1)
    if echo "$OUTPUT" | grep -q "❌"; then
      ERRORS+=("Failed to set project_id: $OUTPUT")
    fi
  fi
fi

# 3. Save error message if provided
if [ -n "$ERROR_MSG" ]; then
  # Truncate to 500 chars
  ERROR_TRUNCATED="${ERROR_MSG:0:500}"
  OUTPUT=$(echo "y" | todoit item property set --list "$LIST_KEY" --item "$SCENE_KEY" --subitem image_gen --key ERROR --value "$ERROR_TRUNCATED" 2>&1)
  if echo "$OUTPUT" | grep -q "❌"; then
    ERRORS+=("Failed to set error property: $OUTPUT")
  fi
fi

# 4. Update status based on result
# NOTE: If status is "pending" (ChatGPT limit), we don't change it - it stays pending for retry
if [ "$STATUS" != "pending" ]; then
  OUTPUT=$(echo "y" | todoit item status --list "$LIST_KEY" --item "$SCENE_KEY" --subitem image_gen --status "$STATUS" 2>&1)
  if echo "$OUTPUT" | grep -q "❌"; then
    ERRORS+=("Failed to update status to $STATUS: $OUTPUT")
  fi
fi

# Return result
if [ ${#ERRORS[@]} -eq 0 ]; then
  jq -n \
    --arg status "$STATUS" \
    --arg scene_key "$SCENE_KEY" \
    --arg thread_id "$THREAD_ID" \
    '{
      success: true,
      status: $status,
      scene_key: $scene_key,
      thread_id: $thread_id,
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
