#\!/bin/bash
# Hook to change directory for 37d agents

# Extract book folder path using jq
BOOK_PATH=$(jq -r 'if (.tool_name == "Task" and (.tool_input.subagent_type )) then (.tool_input.prompt | fromjson | .book_folder_path) else "skip" end')

if [ "$BOOK_PATH" \!= "skip" ] && [ -n "$BOOK_PATH" ]; then
    # Extract relative path (books/NNNN_name part)
    RELATIVE_PATH=$(echo "$BOOK_PATH" | sed 's|.*/\(books/[^/]*\).*|\1|')
    
    # Build full path with project directory
    FULL_PATH="${CLAUDE_PROJECT_DIR}/${RELATIVE_PATH}"
    
    # Change to that directory if it exists
    if [ -d "$FULL_PATH" ]; then
        cd "$FULL_PATH"
        echo "Changed directory to: $FULL_PATH" >> /tmp/hook-cd.log
    fi
fi

exit 0
EOF < /dev/null