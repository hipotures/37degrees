#!/bin/bash
# Simple test hook that logs to a file

echo "Hook executed at $(date)" >> /tmp/hook-test.log
echo "Input received:" >> /tmp/hook-test.log
cat >> /tmp/hook-test.log
echo "---" >> /tmp/hook-test.log

# Return empty JSON
echo '{}'