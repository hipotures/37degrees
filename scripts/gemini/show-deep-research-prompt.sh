#!/bin/bash
# Show Deep Research prompt without executing
# Usage: ./show-deep-research-prompt.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "========================================" >&2
echo "Deep Research Prompt Preview" >&2
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
  exit 0
fi

# Extract data
SOURCE_NAME=$(echo "$READ_RESULT" | jq -r '.source_name')
BOOK_NUMBER=$(echo "$READ_RESULT" | jq -r '.book_number')

echo "  ✓ Source: $SOURCE_NAME" >&2
echo "  ✓ Book number: $BOOK_NUMBER" >&2
echo "" >&2

# ============================================================================
# PHASE 2: Read book info
# ============================================================================

echo "[2/3] Reading book information..." >&2

BOOK_YAML="$PROJECT_ROOT/books/$SOURCE_NAME/book.yaml"

if [ ! -f "$BOOK_YAML" ]; then
  echo "✗ book.yaml not found: $BOOK_YAML" >&2
  exit 1
fi

# Extract title and author using Python
BOOK_INFO=$(python3 <<EOF
import yaml
import sys

try:
    with open('$BOOK_YAML', 'r') as f:
        data = yaml.safe_load(f)

    book_info = data.get('book_info', data)
    title = book_info.get('title', book_info.get('title_pl', 'Unknown'))
    author = book_info.get('author', 'Unknown')

    print(f"{title}|||{author}")
except Exception as e:
    print(f"Unknown|||Unknown", file=sys.stderr)
    sys.exit(1)
EOF
)

TITLE=$(echo "$BOOK_INFO" | cut -d'|' -f1)
AUTHOR=$(echo "$BOOK_INFO" | cut -d'|' -f4)

echo "  ✓ Title: $TITLE" >&2
echo "  ✓ Author: $AUTHOR" >&2
echo "" >&2

# ============================================================================
# PHASE 3: Generate and display prompt
# ============================================================================

echo "[3/3] Generating prompt..." >&2
echo "" >&2

PROMPT_FILE="$PROJECT_ROOT/docs/audio-research/podcast_research_prompt.md"

if [ ! -f "$PROMPT_FILE" ]; then
  echo "✗ Prompt file not found: $PROMPT_FILE" >&2
  exit 1
fi

# Generate header
HEADER="## BADANA KSIĄŻKA
title: $TITLE
author: $AUTHOR
"

# Read prompt content (skip first 3 lines - example header)
PROMPT_CONTENT=$(tail -n +4 "$PROMPT_FILE")

# Combine
FULL_PROMPT="${HEADER}${PROMPT_CONTENT}"

# Display
echo "================================================================================" >&2
echo "FULL PROMPT FOR: $SOURCE_NAME" >&2
echo "================================================================================" >&2
echo "" >&2

# Output to stdout (for piping/redirecting)
echo "$FULL_PROMPT"

echo "" >&2
echo "================================================================================" >&2
echo "Total length: ${#FULL_PROMPT} characters" >&2
echo "================================================================================" >&2
