#!/bin/bash

# Read JSON from stdin
json_input=$(cat)

# Extract fields using jq
agent_name=$(echo "$json_input" | jq -r '.agent_name // empty')
tool_name=$(echo "$json_input" | jq -r '.tool_name // empty')
tool_input=$(echo "$json_input" | jq -r '.tool_input // empty')
tool_response=$(echo "$json_input" | jq -r '.tool_response // empty')

# Only process 37d-* agents
if [[ ! "$agent_name" =~ ^37d- ]]; then
    exit 0
fi

# Find book folder by looking for TODO_master.md
book_folder=$(find . -name "TODO_master.md" -path "*/books/*" | head -1 | xargs dirname 2>/dev/null)

if [ -z "$book_folder" ]; then
    exit 0
fi

# Create findings file path
findings_file="$book_folder/docs/${agent_name}_raw_searches.md"
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

exit 0