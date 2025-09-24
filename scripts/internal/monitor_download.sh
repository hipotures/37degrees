#!/bin/bash

# Monitor download completion for NotebookLM audio files
# Usage: ./monitor_download.sh [timeout_seconds]

DOWNLOAD_DIR="/tmp/playwright-mcp-output"
TIMEOUT=${1:-300}  # Default 5 minutes
WAITED=0
CHECK_INTERVAL=2

echo "Monitoring $DOWNLOAD_DIR for new .mp4 files..."
echo "Timeout: $TIMEOUT seconds"
echo "Check interval: $CHECK_INTERVAL seconds"
echo ""

# Get initial state
INITIAL_FILES=$(find "$DOWNLOAD_DIR" -name "*.mp4" 2>/dev/null | wc -l)
echo "Initial .mp4 files count: $INITIAL_FILES"

while [ $WAITED -lt $TIMEOUT ]; do
    # Check for new .mp4 files
    CURRENT_FILES=$(find "$DOWNLOAD_DIR" -name "*.mp4" 2>/dev/null | wc -l)

    if [ $CURRENT_FILES -gt $INITIAL_FILES ]; then
        # New file detected
        NEWEST_FILE=$(find "$DOWNLOAD_DIR" -name "*.mp4" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
        if [ -n "$NEWEST_FILE" ]; then
            echo "SUCCESS: New audio file detected: $NEWEST_FILE"
            echo "File size: $(du -h "$NEWEST_FILE" | cut -f1)"
            echo "Download time: $(date)"
            exit 0
        fi
    fi

    # Show progress every 30 seconds
    if [ $((WAITED % 30)) -eq 0 ] && [ $WAITED -gt 0 ]; then
        echo "Still monitoring... ($WAITED/$TIMEOUT seconds elapsed)"
    fi

    sleep $CHECK_INTERVAL
    WAITED=$((WAITED + CHECK_INTERVAL))
done

echo "TIMEOUT: No new audio files detected after $TIMEOUT seconds"
exit 1