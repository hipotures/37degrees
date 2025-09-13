#!/bin/bash
# can_delete_file.sh - Safe file deletion verification script
# Usage: can_delete_file.sh <file_path>
# Returns: CAN_DELETE_FROM_NOTEBOOK or CANNOT_DELETE_FROM_NOTEBOOK:<reason>

file_path="$1"

# Check if file path provided
if [[ -z "$file_path" ]]; then
    echo "CANNOT_DELETE_FROM_NOTEBOOK:No file path provided"
    exit 1
fi

# Check if file exists
if [[ ! -f "$file_path" ]]; then
    echo "CANNOT_DELETE_FROM_NOTEBOOK:File does not exist"
    exit 1
fi

# Security: Only allow files in books/*/audio/ directories
if [[ ! "$file_path" =~ ^books/[^/]+/audio/.+ ]]; then
    echo "CANNOT_DELETE_FROM_NOTEBOOK:File path not in allowed books/*/audio/ directory"
    exit 1
fi

# Get current time and file modification time
current_time=$(date +%s)
file_mtime=$(stat -c %Y "$file_path" 2>/dev/null || echo 0)
file_size=$(stat -c %s "$file_path" 2>/dev/null || echo 0)

# Calculate time difference (in seconds)
time_diff=$((current_time - file_mtime))

# Safety checks
if [[ $file_size -le 1048576 ]]; then
    echo "CANNOT_DELETE_FROM_NOTEBOOK:File too small, must be >1MB (size=${file_size}bytes)"
    exit 1
fi

if [[ $time_diff -gt 300 ]]; then
    echo "CANNOT_DELETE_FROM_NOTEBOOK:File is older than 5 minutes (${time_diff}s)"
    exit 1
fi

# All checks passed - safe to delete from NotebookLM
echo "CAN_DELETE_FROM_NOTEBOOK"
exit 0