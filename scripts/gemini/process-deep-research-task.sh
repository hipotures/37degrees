#!/bin/bash
# Orchestrator script for Gemini Deep Research workflow
# Usage: ./process-deep-research-task.sh [--headless=false]
# Example: ./process-deep-research-task.sh
# Example: ./process-deep-research-task.sh --headless=false

set -e

HEADLESS="true"

# Parse optional flags
if [ "$1" == "--headless=false" ]; then
  HEADLESS="false"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================" >&2
echo "Gemini Deep Research Workflow" >&2
echo "Headless: $HEADLESS" >&2
echo "========================================" >&2
echo "" >&2

# ============================================================================
# PHASE 1: Read task from TODOIT
# ============================================================================

echo "[1/3] Reading task from TODOIT..." >&2

set +e
READ_RESULT=$("$SCRIPT_DIR/todoit-read-research-task.sh")
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
BOOK_NUMBER=$(echo "$READ_RESULT" | jq -r '.book_number')

echo "  ✓ Source: $SOURCE_NAME" >&2
echo "  ✓ Book number: $BOOK_NUMBER" >&2
echo "" >&2

# ============================================================================
# PHASE 2: Run Playwright Deep Research automation
# ============================================================================

echo "[2/3] Running Playwright Deep Research automation..." >&2

# Construct command with parameters
if [ "$HEADLESS" == "false" ]; then
  RESEARCH_CMD="npx ts-node $SCRIPT_DIR/execute-deep-research.ts \"$SOURCE_NAME\" false"
else
  RESEARCH_CMD="npx ts-node $SCRIPT_DIR/execute-deep-research.ts \"$SOURCE_NAME\""
fi

echo "  → Command: npx ts-node execute-deep-research.ts $SOURCE_NAME" >&2

# Run Deep Research automation
# Playwright outputs JSON to stdout (last line), logs to stderr
# Temporarily disable exit-on-error to capture exit code
set +e
RESEARCH_JSON=$(eval "$RESEARCH_CMD" 2>&2)
RESEARCH_EXIT=$?
set -e

# Validate JSON
if [ -z "$RESEARCH_JSON" ] || ! echo "$RESEARCH_JSON" | jq empty 2>/dev/null; then
  echo "✗ Failed to get valid JSON from Playwright" >&2
  echo "Output: $RESEARCH_JSON" >&2
  exit 1
fi

# Parse result
SUCCESS=$(echo "$RESEARCH_JSON" | jq -r '.success')
SEARCH_URL=$(echo "$RESEARCH_JSON" | jq -r '.searchUrl // empty')
ERROR_MSG=$(echo "$RESEARCH_JSON" | jq -r '.error // empty')
ERROR_TYPE=$(echo "$RESEARCH_JSON" | jq -r '.errorType // empty')

echo "  ✓ Deep Research automation completed" >&2
echo "  → Success: $SUCCESS" >&2
if [ -n "$SEARCH_URL" ]; then
  echo "  → Search URL: ${SEARCH_URL:0:80}..." >&2
fi
echo "" >&2

# ============================================================================
# PHASE 3: Save results to TODOIT
# ============================================================================

echo "[3/3] Saving results to TODOIT..." >&2

# Determine status
if [ "$SUCCESS" == "true" ]; then
  STATUS="in_progress"  # Deep Research is running in background
else
  STATUS="failed"
fi

echo "  → Status: $STATUS" >&2

# Construct write command
WRITE_CMD="$SCRIPT_DIR/todoit-write-research-result.sh \"$SOURCE_NAME\" \"$STATUS\""

# Add error message if present
if [ -n "$ERROR_MSG" ]; then
  # Escape quotes in error message
  ESCAPED_ERROR=$(echo "$ERROR_MSG" | sed 's/"/\\"/g')
  WRITE_CMD="$WRITE_CMD \"$ESCAPED_ERROR\""
else
  WRITE_CMD="$WRITE_CMD \"\""
fi

# Add search URL if present
if [ -n "$SEARCH_URL" ]; then
  WRITE_CMD="$WRITE_CMD \"$SEARCH_URL\""
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
  SCREENSHOT="/tmp/gemini-deep-research-final-success-*.png"
else
  SCREENSHOT="/tmp/gemini-deep-research-error-*.png"
fi

# Output final JSON result
jq -n \
  --arg source "$SOURCE_NAME" \
  --arg url "$SEARCH_URL" \
  --arg status "$STATUS" \
  --arg timestamp "$TIMESTAMP" \
  --arg screenshot "$SCREENSHOT" \
  --argjson success "$SUCCESS" \
  --arg error_msg "$ERROR_MSG" \
  '{
    success: $success,
    source_name: $source,
    search_url: ($url | if . == "" then null else . end),
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
