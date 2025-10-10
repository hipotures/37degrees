#!/bin/bash
# Orchestrator script for Gemini NotebookLM audio generation workflow
# Usage: ./process-audio-task.sh [--headless]
# Example: ./process-audio-task.sh
# Example: ./process-audio-task.sh --headless=false

set -e

HEADLESS="true"

# Parse optional flags
if [ "$1" == "--headless=false" ]; then
  HEADLESS="false"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================" >&2
echo "NotebookLM Audio Generation Workflow" >&2
echo "Headless: $HEADLESS" >&2
echo "========================================" >&2
echo "" >&2

# ============================================================================
# PHASE 1: Read task from TODOIT
# ============================================================================

echo "[1/3] Reading task from TODOIT..." >&2

set +e
READ_RESULT=$("$SCRIPT_DIR/todoit-read-task.sh")
READ_EXIT=$?
set -e

if [ $READ_EXIT -ne 0 ]; then
  echo "✗ Failed to read task from TODOIT" >&2
  echo "$READ_RESULT" >&2
  exit 1
fi

# Check if ready
READY=$(echo "$READ_RESULT" | jq -r '.ready')

if [ "$READY" != "true" ]; then
  MESSAGE=$(echo "$READ_RESULT" | jq -r '.message // "No tasks ready"')
  echo "ℹ $MESSAGE" >&2
  echo "$READ_RESULT"
  exit 0
fi

# Extract data
SOURCE_NAME=$(echo "$READ_RESULT" | jq -r '.source_name')
LANGUAGE_CODE=$(echo "$READ_RESULT" | jq -r '.language_code')
PENDING_SUBITEM_KEY=$(echo "$READ_RESULT" | jq -r '.pending_subitem_key')
NOTEBOOK_URL=$(echo "$READ_RESULT" | jq -r '.notebook_url')
BOOK_NUMBER=$(echo "$READ_RESULT" | jq -r '.book_number')

echo "  ✓ Source: $SOURCE_NAME" >&2
echo "  ✓ Language: $LANGUAGE_CODE" >&2
echo "  ✓ Subitem: $PENDING_SUBITEM_KEY" >&2
echo "  ✓ Notebook: ...${NOTEBOOK_URL: -20}" >&2
echo "" >&2

# ============================================================================
# PHASE 2: Run Playwright audio generation script
# ============================================================================

echo "[2/3] Running Playwright audio generation..." >&2

# Construct command with all parameters
AUDIO_CMD="npx ts-node $SCRIPT_DIR/generate-audio.ts \"$SOURCE_NAME\" \"$LANGUAGE_CODE\" \"$NOTEBOOK_URL\" \"$HEADLESS\""

echo "  → Command: npx ts-node generate-audio.ts ..." >&2

# Run audio generation
# Playwright outputs JSON to stdout (last line), logs to stderr
# Temporarily disable exit-on-error to capture exit code
set +e
AUDIO_JSON=$(eval "$AUDIO_CMD" 2>&2)
AUDIO_EXIT=$?
set -e

# Validate JSON
if [ -z "$AUDIO_JSON" ] || ! echo "$AUDIO_JSON" | jq empty 2>/dev/null; then
  echo "✗ Failed to get valid JSON from Playwright" >&2
  echo "Output: $AUDIO_JSON" >&2
  exit 1
fi

# Parse result
SUCCESS=$(echo "$AUDIO_JSON" | jq -r '.success')
AUDIO_ID=$(echo "$AUDIO_JSON" | jq -r '.audioId // empty')
ERROR_MSG=$(echo "$AUDIO_JSON" | jq -r '.error // empty')
ERROR_TYPE=$(echo "$AUDIO_JSON" | jq -r '.errorType // empty')

echo "  ✓ Generation completed" >&2
echo "  → Success: $SUCCESS" >&2
if [ -n "$AUDIO_ID" ]; then
  echo "  → Audio ID: $AUDIO_ID" >&2
fi
echo "" >&2

# ============================================================================
# PHASE 3: Save results to TODOIT
# ============================================================================

echo "[3/3] Saving results to TODOIT..." >&2

# Determine status
if [ "$SUCCESS" == "true" ]; then
  STATUS="completed"
elif [ "$ERROR_TYPE" == "daily_limit" ]; then
  # CRITICAL: For daily limit, keep as pending for retry
  STATUS="pending"
  echo "  ⚠ Daily limit detected. Keeping task as pending for retry." >&2
elif [ "$ERROR_TYPE" == "network" ]; then
  # CRITICAL: For network/timeout errors, keep as pending for retry
  STATUS="pending"
  echo "  ⚠ Network/timeout error detected. Keeping task as pending for retry." >&2
else
  STATUS="failed"
fi

echo "  → Status: $STATUS" >&2

# Construct write command
WRITE_CMD="$SCRIPT_DIR/todoit-write-result.sh \"$SOURCE_NAME\" \"$PENDING_SUBITEM_KEY\" \"$STATUS\""

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

# Generate timestamp with second precision
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Construct screenshot path based on success/failure
if [ "$SUCCESS" == "true" ]; then
  SCREENSHOT="/tmp/gemini-success-${SOURCE_NAME}-${LANGUAGE_CODE}.png"
else
  SCREENSHOT="/tmp/gemini-error-${SOURCE_NAME}.png"
fi

# Output final JSON result
jq -n \
  --arg source "$SOURCE_NAME" \
  --arg lang "$LANGUAGE_CODE" \
  --arg subitem "$PENDING_SUBITEM_KEY" \
  --arg audio_id "$AUDIO_ID" \
  --arg status "$STATUS" \
  --arg timestamp "$TIMESTAMP" \
  --arg screenshot "$SCREENSHOT" \
  --argjson success "$SUCCESS" \
  --arg error_msg "$ERROR_MSG" \
  '{
    success: $success,
    source_name: $source,
    language_code: $lang,
    subitem_key: $subitem,
    audio_id: ($audio_id | if . == "" then null else . end),
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
