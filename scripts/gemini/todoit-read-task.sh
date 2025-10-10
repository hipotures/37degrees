#!/bin/bash
# TODOIT CLI wrapper for reading next audio generation task
# Usage: ./todoit-read-task.sh
# Output: JSON with all needed data for audio generation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ============================================================================
# PHASE 1: Call Python script to find next task
# ============================================================================

TASK_JSON=$(python "$PROJECT_ROOT/scripts/internal/find_next_audio_task.py" 2>/dev/null)
PYTHON_EXIT=$?

if [ $PYTHON_EXIT -ne 0 ]; then
  echo '{"error": "Failed to execute find_next_audio_task.py"}' >&2
  exit 1
fi

# Parse status from Python output
STATUS=$(echo "$TASK_JSON" | jq -r '.STATUS // .status' 2>/dev/null)

if [ -z "$STATUS" ]; then
  echo '{"error": "Invalid JSON from find_next_audio_task.py"}' >&2
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

SOURCE_NAME=$(echo "$TASK_JSON" | jq -r '.SOURCE_NAME')
LANGUAGE_CODE=$(echo "$TASK_JSON" | jq -r '.LANGUAGE_CODE')
PENDING_SUBITEM_KEY=$(echo "$TASK_JSON" | jq -r '.PENDING_SUBITEM_KEY')

if [ -z "$SOURCE_NAME" ] || [ -z "$LANGUAGE_CODE" ] || [ -z "$PENDING_SUBITEM_KEY" ]; then
  echo '{"error": "Missing required fields in Python output"}' >&2
  exit 1
fi

# ============================================================================
# PHASE 3: Determine NotebookLM URL based on book number
# ============================================================================

# Extract book number from SOURCE_NAME (format: NNNN_xxx)
BOOK_NUMBER=$(echo "$SOURCE_NAME" | cut -d_ -f1 | sed 's/^0*//')

# Handle edge case: if number becomes empty (e.g., "0000"), default to 1
if [ -z "$BOOK_NUMBER" ]; then
  BOOK_NUMBER=1
fi

# Determine appropriate NotebookLM URL
if [ "$BOOK_NUMBER" -ge 1 ] && [ "$BOOK_NUMBER" -le 50 ]; then
  NOTEBOOK_URL="https://notebooklm.google.com/notebook/ad8ec869-2284-44d3-bc06-b493e5990d81"
elif [ "$BOOK_NUMBER" -ge 51 ] && [ "$BOOK_NUMBER" -le 100 ]; then
  NOTEBOOK_URL="https://notebooklm.google.com/notebook/ea74e09e-0483-4e15-a3ee-59de799e721b"
elif [ "$BOOK_NUMBER" -ge 101 ] && [ "$BOOK_NUMBER" -le 150 ]; then
  NOTEBOOK_URL="https://notebooklm.google.com/notebook/05296cd4-601d-4760-b34e-f41190b34349"
elif [ "$BOOK_NUMBER" -ge 151 ] && [ "$BOOK_NUMBER" -le 200 ]; then
  NOTEBOOK_URL="https://notebooklm.google.com/notebook/e87e6c2c-f56e-49e9-8216-6c3eb1c107cc"
else
  echo "{\"error\": \"Book number $BOOK_NUMBER out of range (1-200)\"}" >&2
  exit 1
fi

# ============================================================================
# PHASE 4: Output all data as JSON
# ============================================================================

jq -n \
  --arg source "$SOURCE_NAME" \
  --arg lang "$LANGUAGE_CODE" \
  --arg subitem "$PENDING_SUBITEM_KEY" \
  --arg url "$NOTEBOOK_URL" \
  --arg book_num "$BOOK_NUMBER" \
  '{
    ready: true,
    source_name: $source,
    language_code: $lang,
    pending_subitem_key: $subitem,
    notebook_url: $url,
    book_number: $book_num
  }'
