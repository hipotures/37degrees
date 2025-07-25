#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Read JSON from stdin
try:
    data = json.load(sys.stdin)
    # DEBUG: Save to /tmp/agent.json
    with open('/tmp/agent.json', 'w', encoding='utf-8') as debug_f:
        json.dump(data, debug_f, indent=2)
except Exception as e:
    print(f"[37d-hook] Error reading JSON: {e}", file=sys.stderr)
    sys.exit(0)

# Extract relevant fields
tool_name = data.get('tool_name', '')
session_id = data.get('session_id', '')
cwd = data.get('cwd', '')
tool_input = data.get('tool_input', {})
search_query = tool_input.get('query', '') or tool_input.get('prompt', '')

# Only process search tools (WebSearch, WebFetch - capitalized)
if tool_name not in ['WebSearch', 'WebFetch']:
    sys.exit(0)

# Determine book folder from cwd
book_folder = None
agent_name = None

# Check if we're in a book's docs directory
cwd_path = Path(cwd)
if cwd_path.name == 'docs' and 'books' in str(cwd_path):
    # We're in books/XXXX/docs/ - get the book folder
    book_folder = cwd_path.parent
    # Look for 37d TODO files in this directory
    for todo_file in cwd_path.glob('TODO_37d-*.md'):
        agent_name = todo_file.stem.replace('TODO_', '')
        break
elif 'books' in str(cwd_path):
    # We're somewhere in books/ - find the book folder
    parts = cwd_path.parts
    try:
        books_index = parts.index('books')
        if books_index + 1 < len(parts):
            book_name = parts[books_index + 1]
            book_folder = Path(cwd).parent / 'books' / book_name
            if not book_folder.exists():
                book_folder = cwd_path / 'books' / book_name
            # Check for TODO files in docs
            docs_dir = book_folder / 'docs'
            if docs_dir.exists():
                for todo_file in docs_dir.glob('TODO_37d-*.md'):
                    agent_name = todo_file.stem.replace('TODO_', '')
                    break
    except ValueError:
        pass

# If we couldn't determine the book folder from cwd, fall back to old method
if not book_folder or not agent_name:
    # Get project directory from environment
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', '.')
    books_dir = Path(project_dir) / 'books'
    
    # Look for recently modified 37d TODO files (last 2 hours)
    import time
    current_time = time.time()
    
    for book_dir in books_dir.iterdir():
        if book_dir.is_dir():
            docs_dir = book_dir / 'docs'
            if docs_dir.exists():
                for todo_file in docs_dir.glob('TODO_37d-*.md'):
                    # Check if file was modified recently (2 hours)
                    if (current_time - todo_file.stat().st_mtime) < 7200:
                        book_folder = book_dir
                        # Extract agent name from filename
                        agent_name = todo_file.stem.replace('TODO_', '')
                        break
        if book_folder:
            break

# If we still couldn't find active 37d research, exit
if not book_folder or not agent_name:
    sys.exit(0)

# Generate filename with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
json_filename = f'{agent_name}_raw_{tool_name}_{timestamp}.json'
json_filepath = book_folder / 'docs' / json_filename

# Save complete raw JSON
json_filepath.parent.mkdir(parents=True, exist_ok=True)
with open(json_filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

# Update index file
index_file = book_folder / 'docs' / f'{agent_name}_searches_index.txt'
with open(index_file, 'a', encoding='utf-8') as f:
    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {tool_name} | {session_id} | {json_filename}\n")

# Log success
print(f"[37d-hook] Saved raw JSON to: {json_filepath}")

sys.exit(0)
