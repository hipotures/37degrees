#!/bin/bash
# Orchestrator script for ChatGPT image generation workflow
# Usage: ./process-image-task.sh <TODOIT_LIST>
# Example: ./process-image-task.sh m00062_cointelpro_revelation_1971

set -e

TODOIT_LIST="$1"

if [ -z "$TODOIT_LIST" ]; then
  echo "Usage: $0 <TODOIT_LIST>" >&2
  echo "Example: $0 m00062_cointelpro_revelation_1971" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================" >&2
echo "ChatGPT Image Generation Workflow" >&2
echo "List: $TODOIT_LIST" >&2
echo "========================================" >&2
echo "" >&2

# ============================================================================
# PHASE 1: Read task from TODOIT
# ============================================================================

echo "[1/3] Reading task from TODOIT..." >&2

READ_RESULT=$("$SCRIPT_DIR/todoit-read-task.sh" "$TODOIT_LIST")
READ_EXIT=$?

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
BOOK_FOLDER=$(echo "$READ_RESULT" | jq -r '.book_folder')
PROJECT_ID=$(echo "$READ_RESULT" | jq -r '.project_id // empty')
SCENE_KEY=$(echo "$READ_RESULT" | jq -r '.scene_key')
YAML_FILENAME=$(echo "$READ_RESULT" | jq -r '.yaml_filename')

echo "  ✓ Scene: $SCENE_KEY" >&2
echo "  ✓ YAML: $YAML_FILENAME" >&2
if [ -n "$PROJECT_ID" ]; then
  echo "  ✓ Project ID: $PROJECT_ID" >&2
fi
echo "" >&2

# ============================================================================
# PHASE 2: Run Playwright upload script
# ============================================================================

echo "[2/3] Running Playwright upload..." >&2

# Construct command
UPLOAD_CMD="npx ts-node $SCRIPT_DIR/upload-scene.ts $BOOK_FOLDER $YAML_FILENAME"
if [ -n "$PROJECT_ID" ]; then
  UPLOAD_CMD="$UPLOAD_CMD $PROJECT_ID"
fi

echo "  → Command: $UPLOAD_CMD" >&2

# Run upload
# Playwright outputs JSON to stdout (last line), logs to stderr
# We need to capture stdout but show stderr to user
UPLOAD_JSON=$(eval "$UPLOAD_CMD" 2>&2)
UPLOAD_EXIT=$?

# Validate JSON
if [ -z "$UPLOAD_JSON" ] || ! echo "$UPLOAD_JSON" | jq empty 2>/dev/null; then
  echo "✗ Failed to get valid JSON from Playwright" >&2
  echo "Output: $UPLOAD_JSON" >&2
  exit 1
fi

# Parse result
SUCCESS=$(echo "$UPLOAD_JSON" | jq -r '.success')
THREAD_ID=$(echo "$UPLOAD_JSON" | jq -r '.threadId // empty')
NEW_PROJECT_ID=$(echo "$UPLOAD_JSON" | jq -r '.projectId // empty')
ERROR_MSG=$(echo "$UPLOAD_JSON" | jq -r '.error // empty')
ERROR_TYPE=$(echo "$UPLOAD_JSON" | jq -r '.errorType // empty')

echo "  ✓ Upload completed" >&2
echo "  → Success: $SUCCESS" >&2
echo "  → Thread ID: $THREAD_ID" >&2
echo "" >&2

# ============================================================================
# PHASE 3: Save results to TODOIT
# ============================================================================

echo "[3/3] Saving results to TODOIT..." >&2

# CRITICAL: Check if we have valid thread ID
if [ -z "$THREAD_ID" ] || [[ "$THREAD_ID" =~ ^FAILED.*$ ]] || [ "$THREAD_ID" == "null" ]; then
  echo "✗ CRITICAL: No valid thread ID from Playwright" >&2
  echo "✗ Not saving to TODOIT - scene remains unchanged for retry" >&2
  echo "$UPLOAD_JSON"
  exit 1
fi

# Determine status
if [ "$SUCCESS" == "true" ]; then
  STATUS="completed"
elif [ "$ERROR_TYPE" == "limit" ]; then
  STATUS="pending"
else
  STATUS="failed"
fi

echo "  → Status: $STATUS" >&2

# Construct write command
WRITE_CMD="$SCRIPT_DIR/todoit-write-result.sh \"$TODOIT_LIST\" \"$SCENE_KEY\" \"$THREAD_ID\" \"$STATUS\""

# Add project_id if new project was created
if [ -n "$NEW_PROJECT_ID" ] && [ -z "$PROJECT_ID" ]; then
  WRITE_CMD="$WRITE_CMD \"$NEW_PROJECT_ID\""
else
  WRITE_CMD="$WRITE_CMD \"\""
fi

# Add error message if present
if [ -n "$ERROR_MSG" ]; then
  # Escape quotes in error message
  ESCAPED_ERROR=$(echo "$ERROR_MSG" | sed 's/"/\\"/g')
  WRITE_CMD="$WRITE_CMD \"$ESCAPED_ERROR\""
fi

# Execute write
WRITE_RESULT=$(eval "$WRITE_CMD")
WRITE_EXIT=$?

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

# Determine final project ID (use new if created, else existing)
FINAL_PROJECT_ID="${NEW_PROJECT_ID:-$PROJECT_ID}"

# Generate timestamp with second precision
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Construct screenshot path based on success/failure
if [ "$SUCCESS" == "true" ]; then
  SCREENSHOT="/tmp/chatgpt-success-${BOOK_FOLDER}-${SCENE_KEY}.png"
else
  SCREENSHOT="/tmp/chatgpt-error-${BOOK_FOLDER}-${SCENE_KEY}.png"
fi

# Output final JSON result
jq -n \
  --arg list "$TODOIT_LIST" \
  --arg scene "$SCENE_KEY" \
  --arg thread_id "$THREAD_ID" \
  --arg status "$STATUS" \
  --arg project_id "$FINAL_PROJECT_ID" \
  --arg timestamp "$TIMESTAMP" \
  --arg screenshot "$SCREENSHOT" \
  --argjson success "$SUCCESS" \
  '{
    success: $success,
    list: $list,
    scene: $scene,
    thread_id: $thread_id,
    status: $status,
    project_id: $project_id,
    timestamp: $timestamp,
    screenshot: $screenshot
  }'
