#!/bin/bash

# Read JSON from stdin
json_input=$(cat)

# Debug: save raw input to see what we're getting
echo "$json_input" > /tmp/37d-hook-debug.json

# Extract fields using jq
tool_name=$(echo "$json_input" | jq -r '.tool_name // empty')
tool_input=$(echo "$json_input" | jq -r '.tool_input // empty')
tool_response=$(echo "$json_input" | jq -r '.tool_response // empty')

# Only process web searches for now
if [[ "$tool_name" != "WebSearch" && "$tool_name" != "WebFetch" ]]; then
    echo '{}'
    exit 0
fi

# Find book folder by looking for TODO_master.md
book_folder=$(find . -name "TODO_master.md" -path "*/books/*" | head -1 | xargs dirname 2>/dev/null)

if [ -z "$book_folder" ]; then
    exit 0
fi

# Create findings file path
findings_file="$book_folder/docs/web_searches_raw.md"
mkdir -p "$book_folder/docs"

# Append search results
{
    echo ""
    echo "## $(date '+%Y-%m-%d %H:%M:%S') - $tool_name"
    echo "### Query/URL:"
    if [ "$tool_name" = "web_search" ]; then
        echo "$tool_input" | jq -r '.query // "Unknown"'
    else
        echo "$tool_input" | jq -r '.url // "Unknown"'
    fi
    echo "### Raw Output:"
    echo '```'
    echo "$tool_response" | head -50
    echo '```'
    echo "---"
} >> "$findings_file"

# Return empty JSON object to satisfy Claude Code
echo '{}'