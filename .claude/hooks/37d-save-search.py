#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime
from pathlib import Path
import glob

# Debug mode
DEBUG = True

def debug_log(msg):
    if DEBUG:
        with open('/tmp/debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

debug_log("=== 37d-save-search.py STARTED ===")
debug_log(f"sys.argv: {sys.argv}")

# Read JSON from stdin
try:
    data = json.load(sys.stdin)
    debug_log(f"Successfully read JSON data")
except Exception as e:
    debug_log(f"ERROR reading JSON: {e}")
    print(f"[37d-hook] Error reading JSON: {e}", file=sys.stderr)
    sys.exit(0)

# Extract relevant fields
tool_name = data.get('tool_name', '')
session_id = data.get('session_id', '')
cwd = data.get('cwd', '')
tool_input = data.get('tool_input', {})
search_query = tool_input.get('query', '') or tool_input.get('prompt', '')

# Get agent context from JSON (provided by 37d-research.md)
agent_context = data.get('agent_context', {})
agent_name = agent_context.get('agent_name', '')
book_title = agent_context.get('book_title', '')
author = agent_context.get('author', '')
year = agent_context.get('year', '')

debug_log(f"tool_name: {tool_name}")
debug_log(f"cwd: {cwd}")
debug_log(f"search_query: {search_query[:100] if search_query else 'None'}")

# Only process search tools (WebSearch, WebFetch - capitalized)
if tool_name not in ['WebSearch', 'WebFetch']:
    debug_log(f"Skipping - tool_name '{tool_name}' not in ['WebSearch', 'WebFetch']")
    sys.exit(0)

debug_log(f"Processing {tool_name}")

# Get agent name from JSON context
if not agent_name:
    debug_log("ERROR: No agent_name in JSON context")
    print(f"[37d-hook] ERROR: No agent_name provided in context", file=sys.stderr)
    sys.exit(0)

debug_log(f"Using agent from JSON context: {agent_name}")

# DEBUG: Save complete data with agent name
debug_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
debug_filename = f'/tmp/agent-{agent_name}-{debug_timestamp}.json'
with open(debug_filename, 'w', encoding='utf-8') as debug_f:
    json.dump(data, debug_f, indent=2)
debug_log(f"Saved debug data to {debug_filename}")

# Find the docs folder
docs_folder = Path(cwd) / 'docs'

debug_log(f"docs_folder: {docs_folder}")

if not docs_folder.exists():
    debug_log(f"ERROR: Docs folder not found: {docs_folder}")
    print(f"[37d-hook] ERROR: Docs folder not found: {docs_folder}", file=sys.stderr)
    sys.exit(0)

debug_log(f"Docs folder exists: {docs_folder}")

# Generate filename with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
json_filename = f'{agent_name}_raw_{tool_name}_{timestamp}.json'

# Use agent-specific subdirectory (should exist from prepare-book-folders.sh)
agent_dir = docs_folder / agent_name
debug_log(f"Agent folder: {agent_dir}")

if not agent_dir.exists():
    debug_log(f"ERROR: Agent folder not found: {agent_dir}")
    print(f"[37d-hook] ERROR: Agent folder not found: {agent_dir} - run prepare-book-folders.sh first", file=sys.stderr)
    sys.exit(0)

# Save complete raw JSON to agent-specific folder
json_filepath = agent_dir / json_filename
with open(json_filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

# Update index file in agent-specific folder
index_file = agent_dir / f'{agent_name}_searches_index.txt'
with open(index_file, 'a', encoding='utf-8') as f:
    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {tool_name} | {session_id} | {json_filename} | {search_query[:100]}\n")

# Log success
print(f"[37d-hook] Saved {agent_name} search to: {json_filepath}")
debug_log(f"SUCCESS: Saved to {json_filepath}")
debug_log("=== 37d-save-search.py FINISHED ===")

sys.exit(0)
