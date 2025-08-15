#!/bin/bash
# 37d-c4 Image Download Script

# Validate input
if [ -z "$1" ]; then
    echo "Usage: $0 <SOURCE_LIST> <TASK_KEY>"
    exit 1
fi

SOURCE_LIST="${1:-0013_hobbit}"
TASK_KEY="${2:-item_0004}"

# Execute 37d-c4 download with specified parameters
exec node /home/xai/DEV/37degrees/.claude/commands/37d-c4.js \
    "Task key: ${TASK_KEY}"