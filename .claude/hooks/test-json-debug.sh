#!/bin/bash

# Test hook that logs all JSON input for debugging
# Usage: Add to hooks config to see what data is available

# Read JSON from stdin
json_input=$(cat)

# Create debug log directory
debug_dir="$CLAUDE_PROJECT_DIR/.claude/hooks/debug"
mkdir -p "$debug_dir"

# Generate timestamp for unique filename
timestamp=$(date '+%Y%m%d_%H%M%S')

# Save raw JSON to debug file
echo "$json_input" > "${debug_dir}/hook_debug_${timestamp}.json"

# Pretty print JSON to separate file
echo "$json_input" | jq '.' > "${debug_dir}/hook_debug_${timestamp}_pretty.json" 2>/dev/null

# Also log to console (will appear in Claude's output)
echo "=== HOOK DEBUG: PostToolUse ==="
echo "Timestamp: $(date)"
echo "Raw JSON saved to: ${debug_dir}/hook_debug_${timestamp}.json"
echo ""
echo "=== Extracted Fields ==="
echo "session_id: $(echo "$json_input" | jq -r '.session_id // "N/A"')"
echo "hook_event_name: $(echo "$json_input" | jq -r '.hook_event_name // "N/A"')"
echo "tool_name: $(echo "$json_input" | jq -r '.tool_name // "N/A"')"
echo "cwd: $(echo "$json_input" | jq -r '.cwd // "N/A"')"
echo "transcript_path: $(echo "$json_input" | jq -r '.transcript_path // "N/A"')"
echo ""
echo "=== Tool Input ==="
echo "$json_input" | jq '.tool_input // {}' 2>/dev/null
echo ""
echo "=== Tool Response ==="
echo "$json_input" | jq '.tool_response // {}' 2>/dev/null
echo "=== END HOOK DEBUG ==="

# For 37d agents specifically
agent_name=$(echo "$json_input" | jq -r '.agent_name // "unknown"')
if [[ "$agent_name" =~ ^37d- ]]; then
    echo ""
    echo "=== 37D AGENT DETECTED: $agent_name ==="
fi

# Always exit successfully so we don't block Claude
exit 0
