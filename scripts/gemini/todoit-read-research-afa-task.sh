#!/bin/bash
# TODOIT CLI wrapper for reading next AFA Deep Research task
# Usage: ./todoit-read-research-afa-task.sh
# Output: JSON with all needed data for AFA Deep Research generation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ============================================================================
# PHASE 1: Call Python script to find next task
# ============================================================================

TASK_JSON=$(python "$PROJECT_ROOT/scripts/internal/find_next_research_afa_task.py" 2>/dev/null)
PYTHON_EXIT=$?

if [ $PYTHON_EXIT -ne 0 ]; then
  echo '{"error": "Failed to execute find_next_research_afa_task.py"}' >&2
  exit 1
fi

# Parse status from Python output
STATUS=$(echo "$TASK_JSON" | jq -r '.STATUS // .status' 2>/dev/null)

if [ -z "$STATUS" ]; then
  echo '{"error": "Invalid JSON from find_next_research_afa_task.py"}' >&2
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

if [ -z "$SOURCE_NAME" ]; then
  echo '{"error": "Missing SOURCE_NAME in Python output"}' >&2
  exit 1
fi

# ============================================================================
# PHASE 3: Extract book number for informational purposes
# ============================================================================

# Extract book number from SOURCE_NAME (format: NNNN_xxx)
BOOK_NUMBER=$(echo "$SOURCE_NAME" | cut -d_ -f1 | sed 's/^0*//')

# Handle edge case: if number becomes empty (e.g., "0000"), default to 1
if [ -z "$BOOK_NUMBER" ]; then
  BOOK_NUMBER=1
fi

# ============================================================================
# PHASE 4: Output all data as JSON
# ============================================================================

jq -n \
  --arg source "$SOURCE_NAME" \
  --arg book_num "$BOOK_NUMBER" \
  '{
    ready: true,
    source_name: $source,
    book_number: $book_num
  }'
