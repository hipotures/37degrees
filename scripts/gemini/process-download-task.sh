#!/bin/bash
# Orchestrator script for Gemini NotebookLM audio download workflow
# Usage: ./process-download-task.sh [--headless]
# Example: ./process-download-task.sh
# Example: ./process-download-task.sh --headless=false

set -e

HEADLESS="true"

# Parse optional flags
if [ "$1" == "--headless=false" ]; then
  HEADLESS="false"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================" >&2
echo "NotebookLM Audio Download Workflow" >&2
echo "Headless: $HEADLESS" >&2
echo "========================================" >&2
echo "" >&2

# ============================================================================
# PHASE 1: Read download task from TODOIT
# ============================================================================

echo "[1/3] Reading download task from TODOIT..." >&2

set +e
READ_RESULT=$("$SCRIPT_DIR/todoit-read-download-task.sh")
READ_EXIT=$?
set -e

if [ $READ_EXIT -ne 0 ]; then
  echo "✗ Failed to read download task from TODOIT" >&2
  echo "$READ_RESULT" >&2
  exit 1
fi

# Check if ready
READY=$(echo "$READ_RESULT" | jq -r '.ready')

if [ "$READY" != "true" ]; then
  MESSAGE=$(echo "$READ_RESULT" | jq -r '.message // "No download tasks ready"')
  echo "ℹ $MESSAGE" >&2
  echo "$READ_RESULT"
  exit 0
fi

# Extract data
BOOK_KEY=$(echo "$READ_RESULT" | jq -r '.book_key')
LANGUAGE_CODE=$(echo "$READ_RESULT" | jq -r '.language_code')
SUBITEM_KEY=$(echo "$READ_RESULT" | jq -r '.subitem_key')
NOTEBOOK_URL=$(echo "$READ_RESULT" | jq -r '.notebook_url')
AUDIO_TITLE=$(echo "$READ_RESULT" | jq -r '.audio_title // empty')

echo "  ✓ Book: $BOOK_KEY" >&2
echo "  ✓ Language: $LANGUAGE_CODE" >&2
echo "  ✓ Subitem: $SUBITEM_KEY" >&2
if [ -n "$AUDIO_TITLE" ]; then
  echo "  ✓ Audio title: $AUDIO_TITLE" >&2
fi
echo "" >&2

# ============================================================================
# PHASE 2: Run Playwright audio download script
# ============================================================================

echo "[2/3] Running Playwright audio download..." >&2

# Construct command with all parameters
if [ -n "$AUDIO_TITLE" ]; then
  DOWNLOAD_CMD="npx ts-node $SCRIPT_DIR/download-audio.ts \"$BOOK_KEY\" \"$LANGUAGE_CODE\" \"$NOTEBOOK_URL\" \"$AUDIO_TITLE\" \"$HEADLESS\""
else
  DOWNLOAD_CMD="npx ts-node $SCRIPT_DIR/download-audio.ts \"$BOOK_KEY\" \"$LANGUAGE_CODE\" \"$NOTEBOOK_URL\" \"\" \"$HEADLESS\""
fi

echo "  → Command: npx ts-node download-audio.ts ..." >&2

# Run download
set +e
DOWNLOAD_JSON=$(eval "$DOWNLOAD_CMD" 2>&2)
DOWNLOAD_EXIT=$?
set -e

# Validate JSON
if [ -z "$DOWNLOAD_JSON" ] || ! echo "$DOWNLOAD_JSON" | jq empty 2>/dev/null; then
  echo "✗ Failed to get valid JSON from Playwright" >&2
  echo "Output: $DOWNLOAD_JSON" >&2
  exit 1
fi

# Parse result
SUCCESS=$(echo "$DOWNLOAD_JSON" | jq -r '.success')
FILE_PATH=$(echo "$DOWNLOAD_JSON" | jq -r '.filePath // empty')
ERROR_MSG=$(echo "$DOWNLOAD_JSON" | jq -r '.error // empty')
ERROR_TYPE=$(echo "$DOWNLOAD_JSON" | jq -r '.errorType // empty')

echo "  ✓ Download completed" >&2
echo "  → Success: $SUCCESS" >&2
if [ -n "$FILE_PATH" ]; then
  echo "  → File: $FILE_PATH" >&2
fi
echo "" >&2

# ============================================================================
# PHASE 3: Save results to TODOIT
# ============================================================================

echo "[3/3] Saving results to TODOIT..." >&2

# Determine status
if [ "$SUCCESS" == "true" ]; then
  STATUS="completed"
elif [ "$ERROR_TYPE" == "not_found" ]; then
  # Audio not found - might not be generated yet
  STATUS="pending"
  echo "  ⚠ Audio not found. Keeping task as pending (might not be generated yet)." >&2
elif [ "$ERROR_TYPE" == "network" ] || [ "$ERROR_TYPE" == "download_timeout" ]; then
  # Network/timeout errors - retry
  STATUS="pending"
  echo "  ⚠ Network/timeout error detected. Keeping task as pending for retry." >&2
else
  STATUS="failed"
fi

echo "  → Status: $STATUS" >&2

# Construct write command
WRITE_CMD="$SCRIPT_DIR/todoit-write-download-result.sh \"$BOOK_KEY\" \"$SUBITEM_KEY\" \"$STATUS\" \"$FILE_PATH\""

# Add error message if present
if [ -n "$ERROR_MSG" ]; then
  # Escape quotes in error message
  ESCAPED_ERROR=$(echo "$ERROR_MSG" | sed 's/"/\\"/g')
  WRITE_CMD="$WRITE_CMD \"$ESCAPED_ERROR\""
fi

# Execute write
set +e
WRITE_RESULT=$(eval "$WRITE_CMD")
WRITE_EXIT=$?
set -e

if [ $WRITE_EXIT -ne 0 ]; then
  echo "✗ Failed to save to TODOIT" >&2
  echo "$WRITE_RESULT" >&2
  exit 1
fi

echo "  ✓ Saved to TODOIT" >&2
echo "" >&2

# ============================================================================
# Final output
# ============================================================================

echo "========================================" >&2
echo "✓ Workflow completed successfully" >&2
echo "========================================" >&2

# Generate timestamp
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Construct screenshot path based on success/failure
if [ "$SUCCESS" == "true" ]; then
  SCREENSHOT="/tmp/gemini-download-success-${BOOK_KEY}-${LANGUAGE_CODE}.png"
else
  SCREENSHOT="/tmp/gemini-download-error-${BOOK_KEY}.png"
fi

# Output final JSON result
jq -n \
  --arg book "$BOOK_KEY" \
  --arg lang "$LANGUAGE_CODE" \
  --arg subitem "$SUBITEM_KEY" \
  --arg file "$FILE_PATH" \
  --arg status "$STATUS" \
  --arg timestamp "$TIMESTAMP" \
  --arg screenshot "$SCREENSHOT" \
  --argjson success "$SUCCESS" \
  --arg error_msg "$ERROR_MSG" \
  '{
    success: $success,
    book_key: $book,
    language_code: $lang,
    subitem_key: $subitem,
    file_path: ($file | if . == "" then null else . end),
    status: $status,
    timestamp: $timestamp,
    screenshot: $screenshot,
    error: ($error_msg | if . == "" then null else . end)
  }'

# Exit with appropriate code based on success
if [ "$SUCCESS" == "true" ]; then
  exit 0
else
  exit 1
fi
