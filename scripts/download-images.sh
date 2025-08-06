#!/bin/bash
# ChatGPT Image Download Automation Script
# Usage: ./scripts/download-images.sh 0005_chlopi

set -e

BOOK_FOLDER="$1"

if [ -z "$BOOK_FOLDER" ]; then
    echo "Usage: ./scripts/download-images.sh BOOK_FOLDER"
    echo "Example: ./scripts/download-images.sh 0005_chlopi"
    exit 1
fi

echo "=== ChatGPT Image Download Automation ==="
echo "Book folder: $BOOK_FOLDER"
echo "Date: $(date)"
echo

# Check if book folder exists
if [ ! -d "books/$BOOK_FOLDER" ]; then
    echo "ERROR: Book folder books/$BOOK_FOLDER does not exist"
    exit 1
fi

# Check if TODO-GENERATE.md exists
if [ ! -f "books/$BOOK_FOLDER/prompts/genimage/TODO-GENERATE.md" ]; then
    echo "ERROR: TODO-GENERATE.md not found for $BOOK_FOLDER"
    exit 1
fi

# Extract and display Project ID
PROJECT_ID=$(grep "^# PROJECT_ID = " "books/$BOOK_FOLDER/prompts/genimage/TODO-GENERATE.md" | cut -d' ' -f4)
if [ -z "$PROJECT_ID" ]; then
    echo "ERROR: Project ID not found in TODO-GENERATE.md"
    exit 1
fi
echo "Project ID: $PROJECT_ID"

# Count pending tasks
PENDING_COUNT=$(grep -c "^\[x\] \[ \] Created thread" "books/$BOOK_FOLDER/prompts/genimage/TODO-GENERATE.md" 2>/dev/null || echo "0")
echo "Pending downloads: $PENDING_COUNT"

if [ "$PENDING_COUNT" -eq 0 ] 2>/dev/null; then
    echo "✓ All images already downloaded!"
    exit 0
fi

echo
echo "Starting download process..."
echo

# Run Python automation script
python3 scripts/auto-download-chatgpt.py "$BOOK_FOLDER"

echo
echo "Download process completed!"