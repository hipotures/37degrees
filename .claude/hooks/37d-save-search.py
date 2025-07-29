#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime
from pathlib import Path
import glob
import fcntl

# Debug mode
DEBUG = True

def debug_log(msg):
    if DEBUG:
        with open('/tmp/37d-web-hook-debug.log', 'a', encoding='utf-8') as f:
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

# Skip agent context - not available for Task-based agents

debug_log(f"tool_name: {tool_name}")
debug_log(f"cwd: {cwd}")
debug_log(f"search_query: {search_query[:100] if search_query else 'None'}")

# Only process search tools (WebSearch, WebFetch - capitalized)
if tool_name not in ['WebSearch', 'WebFetch']:
    debug_log(f"Skipping - tool_name '{tool_name}' not in ['WebSearch', 'WebFetch']")
    sys.exit(0)

debug_log(f"Processing {tool_name}")

# DEBUG: Save complete data
debug_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
debug_filename = f'/tmp/search-{debug_timestamp}.json'
with open(debug_filename, 'w', encoding='utf-8') as debug_f:
    json.dump(data, debug_f, indent=2)
debug_log(f"Saved debug data to {debug_filename}")

# Find the search_history folder
search_history_folder = Path(cwd) / 'search_history'

debug_log(f"search_history_folder: {search_history_folder}")

if not search_history_folder.exists():
    debug_log(f"ERROR: Search history folder not found: {search_history_folder}")
    print(f"[37d-hook] ERROR: Search history folder not found: {search_history_folder}", file=sys.stderr)
    sys.exit(0)

debug_log(f"Search history folder exists: {search_history_folder}")

# Generate filename with timestamp and PID (without agent name)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
pid = os.getpid()
json_filename = f'search_{tool_name}_{timestamp}_{pid}.json'

# Save complete raw JSON to search_history folder
json_filepath = search_history_folder / json_filename
with open(json_filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

# Update unified index file in search_history folder (with file locking)
index_file = search_history_folder / 'searches_index.txt'
with open(index_file, 'a', encoding='utf-8') as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {tool_name} | {session_id} | {json_filename} | {search_query[:100]}\n")
    # Lock automatically released when file closes

# Log success
print(f"[37d-hook] Saved search to: {json_filepath}")
debug_log(f"SUCCESS: Saved to {json_filepath}")
debug_log("=== 37d-save-search.py FINISHED ===")

sys.exit(0)
