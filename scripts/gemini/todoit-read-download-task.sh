#!/bin/bash
# TODOIT CLI wrapper for reading next audio download task
# Usage: ./todoit-read-download-task.sh
# Output: JSON with all needed data for audio download

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ============================================================================
# PHASE 1: Call Python script to find next download task
# ============================================================================

TASK_JSON=$(python "$PROJECT_ROOT/scripts/internal/find_next_download_task.py" 2>/dev/null)
PYTHON_EXIT=$?

if [ $PYTHON_EXIT -ne 0 ]; then
  echo '{"error": "Failed to execute find_next_download_task.py"}' >&2
  exit 1
fi

# Parse status from Python output
STATUS=$(echo "$TASK_JSON" | jq -r '.status' 2>/dev/null)

if [ -z "$STATUS" ]; then
  echo '{"error": "Invalid JSON from find_next_download_task.py"}' >&2
  exit 1
fi

# If no tasks found, return the original message
if [ "$STATUS" != "found" ]; then
  # Return Python's original response (no_tasks_found, error, etc.)
  echo "$TASK_JSON"
  exit 0
fi

# ============================================================================
# PHASE 2: Extract data from Python result
# ============================================================================

BOOK_KEY=$(echo "$TASK_JSON" | jq -r '.book_key')
LANGUAGE_CODE=$(echo "$TASK_JSON" | jq -r '.language_code')
SUBITEM_KEY=$(echo "$TASK_JSON" | jq -r '.subitem_key')
NOTEBOOK_URL=$(echo "$TASK_JSON" | jq -r '.notebook_url')
AUDIO_TITLE=$(echo "$TASK_JSON" | jq -r '.audio_title // empty')

if [ -z "$BOOK_KEY" ] || [ -z "$LANGUAGE_CODE" ] || [ -z "$SUBITEM_KEY" ]; then
  echo '{"error": "Missing required fields in Python output"}' >&2
  exit 1
fi

# ============================================================================
# PHASE 3: Output all data as JSON (pass through Python data + add ready flag)
# ============================================================================

jq -n \
  --arg book_key "$BOOK_KEY" \
  --arg lang "$LANGUAGE_CODE" \
  --arg subitem "$SUBITEM_KEY" \
  --arg url "$NOTEBOOK_URL" \
  --arg title "$AUDIO_TITLE" \
  '{
    ready: true,
    book_key: $book_key,
    language_code: $lang,
    subitem_key: $subitem,
    notebook_url: $url,
    audio_title: ($title | if . == "" then null else . end)
  }'
