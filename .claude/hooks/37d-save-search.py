#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime
from pathlib import Path
import glob

# Debug mode
DEBUG = False

def debug_log(msg):
    if DEBUG:
        with open('/tmp/debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

debug_log("=== 37d-save-search.py STARTED ===")
debug_log(f"sys.argv: {sys.argv}")

# Read JSON from stdin
try:
    data = json.load(sys.stdin)
    # DEBUG: Save to /tmp/agent.json
    with open('/tmp/agent.json', 'w', encoding='utf-8') as debug_f:
        json.dump(data, debug_f, indent=2)
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

debug_log(f"tool_name: {tool_name}")
debug_log(f"cwd: {cwd}")
debug_log(f"search_query: {search_query[:100] if search_query else 'None'}")

# Only process search tools (WebSearch, WebFetch - capitalized)
if tool_name not in ['WebSearch', 'WebFetch']:
    debug_log(f"Skipping - tool_name '{tool_name}' not in ['WebSearch', 'WebFetch']")
    sys.exit(0)

debug_log(f"Processing {tool_name}")

# Look for lock file in tmp directory
tmp_dir = Path(cwd) / 'tmp'
debug_log(f"Looking for tmp_dir: {tmp_dir}")

if not tmp_dir.exists():
    debug_log(f"ERROR: No tmp directory found at {tmp_dir}")
    print(f"[37d-hook] No tmp directory found", file=sys.stderr)
    sys.exit(0)

debug_log(f"tmp_dir exists: {tmp_dir}")

# Find lock files (only 37d agent locks)
lock_files = list(tmp_dir.glob('*-37d-*.lock'))
debug_log(f"Found {len(lock_files)} lock files")

if len(lock_files) == 0:
    debug_log(f"ERROR: No lock file found in {tmp_dir}")
    print(f"[37d-hook] No lock file found - no active agent", file=sys.stderr)
    sys.exit(0)

if len(lock_files) > 1:
    debug_log(f"ERROR: Multiple lock files found: {[f.name for f in lock_files]}")
    print(f"[37d-hook] ERROR: Multiple lock files found: {[f.name for f in lock_files]}", file=sys.stderr)
    sys.exit(0)

debug_log(f"Using lock file: {lock_files[0].name}")

# Parse the single lock file
lock_file = lock_files[0]
lock_name = lock_file.stem  # e.g., "0001_alice_in_wonderland-37d-facts-hunter"

# Split to find the -37d- pattern
if '-37d-' not in lock_name:
    print(f"[37d-hook] ERROR: Invalid lock file format (missing -37d-): {lock_name}", file=sys.stderr)
    sys.exit(0)

# Split by -37d- to separate book and agent
book_part, agent_suffix = lock_name.split('-37d-', 1)
agent_part = f"37d-{agent_suffix}"  # "37d-facts-hunter"

# Find the book folder
books_dir = Path(cwd) / 'books'
book_folder = books_dir / book_part

debug_log(f"books_dir: {books_dir}")
debug_log(f"book_part: {book_part}")
debug_log(f"book_folder: {book_folder}")

if not book_folder.exists():
    debug_log(f"ERROR: Book folder not found: {book_folder}")
    print(f"[37d-hook] ERROR: Book folder not found: {book_folder}", file=sys.stderr)
    sys.exit(0)

debug_log(f"Book folder exists: {book_folder}")

# Generate filename with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
json_filename = f'{agent_part}_raw_{tool_name}_{timestamp}.json'

# Create agent-specific subdirectory according to new structure
agent_dir = book_folder / 'docs' / agent_part
agent_dir.mkdir(parents=True, exist_ok=True)

# Save complete raw JSON to agent-specific folder
json_filepath = agent_dir / json_filename
with open(json_filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

# Update index file in agent-specific folder
index_file = agent_dir / f'{agent_part}_searches_index.txt'
with open(index_file, 'a', encoding='utf-8') as f:
    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {tool_name} | {session_id} | {json_filename} | {search_query[:100]}\n")

# Log success
print(f"[37d-hook] Saved {agent_part} search to: {json_filepath}")
debug_log(f"SUCCESS: Saved to {json_filepath}")
debug_log("=== 37d-save-search.py FINISHED ===")

sys.exit(0)