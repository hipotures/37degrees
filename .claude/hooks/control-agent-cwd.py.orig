#!/usr/bin/env python3
"""
PreToolUse hook to control agent working directory.
Ensures agents stay within their assigned book directory.
"""
import json
import sys
import os
from datetime import datetime

def main():
    # Read input from stdin
    data = json.load(sys.stdin)
    
    # Save complete raw JSON to /tmp (like 37d-save-search.py)
    debug_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pid = os.getpid()
    debug_filename = f'/tmp/control-agent-cwd_{debug_timestamp}_{pid}.json'
    with open(debug_filename, 'w', encoding='utf-8') as debug_f:
        json.dump(data, debug_f, indent=2)
    
    # Only process Task tool calls
    if data.get('tool_name') != 'Task':
        # Pass through other tools unchanged
        print(json.dumps({}))
        return
    
    # Log the call
    debug_log = {
        'timestamp': datetime.now().isoformat(),
        'tool': data.get('tool_name'),
        'agent': data.get('tool_input', {}).get('subagent_type'),
        'prompt': data.get('tool_input', {}).get('prompt', '')[:200] + '...',
        'cwd': os.getcwd(),
        'debug_file': debug_filename
    }
    
    with open('/tmp/agent-cwd-control.log', 'a') as f:
        f.write(json.dumps(debug_log) + '\n')
    
    # Extract book path from prompt if present
    prompt = data.get('tool_input', {}).get('prompt', '')
    if 'located in books/' in prompt:
        # Extract book path
        start = prompt.find('located in books/')
        if start != -1:
            path_part = prompt[start + len('located in '):]
            book_path = path_part.split('.')[0].split()[0].rstrip('/')
            
            # Modify prompt to include explicit CWD instruction
            modified_prompt = prompt + f"\n\nCRITICAL: You MUST stay within {book_path}/ directory. Do NOT access other book directories."
            
            # Return modified tool input
            return_data = {
                'tool_input': {
                    **data.get('tool_input', {}),
                    'prompt': modified_prompt
                }
            }
            
            with open('/tmp/agent-cwd-control.log', 'a') as f:
                f.write(f"Modified prompt for {book_path}\n")
            
            print(json.dumps(return_data))
            return
    
    # Pass through unchanged if no book path found
    print(json.dumps({}))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # Log error and pass through
        with open('/tmp/agent-cwd-control-error.log', 'a') as f:
            f.write(f"{datetime.now().isoformat()} ERROR: {str(e)}\n")
        print(json.dumps({}))