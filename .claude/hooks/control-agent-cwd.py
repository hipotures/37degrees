#!/usr/bin/env python3
"""
Hook to force 37d agents to work in correct book directories.
This hook detects Task calls with 37d subagents and changes working directory.
"""

import os
import sys
import json
import re

# Get the project directory from environment variable
PROJECT_DIR = os.environ.get('CLAUDE_PROJECT_DIR')

def extract_book_path_from_prompt(prompt):
    """Extract book folder path from JSON context in prompt."""
    try:
        # Parse JSON and look for book_folder_path
        prompt_data = json.loads(prompt)
        book_folder_path = prompt_data.get('book_folder_path', '')
        
        # Extract relative path from full path
        if book_folder_path and 'books/' in book_folder_path:
            # Extract books/NNNN_name part
            start = book_folder_path.find('books/')
            return book_folder_path[start:]
            
    except (json.JSONDecodeError, Exception):
        pass
    
    return None

def main():
    """Main hook function."""
    try:
        # Check if PROJECT_DIR is available
        if not PROJECT_DIR:
            return
            
        # Read the hook data from stdin
        input_data = sys.stdin.read().strip()
        if not input_data:
            return
            
        hook_data = json.loads(input_data)
        
        # Check if this is a Task call with 37d subagent
        if (hook_data.get('tool_name') == 'Task' and 
            'subagent_type' in hook_data.get('tool_input', {}) and
            hook_data['tool_input']['subagent_type'].startswith('37d-')):
            
            # Extract book path from prompt
            prompt = hook_data['tool_input'].get('prompt', '')
            book_path = extract_book_path_from_prompt(prompt)
            
            if book_path:
                # Construct full path and change directory
                full_book_path = os.path.join(PROJECT_DIR, book_path)
                if os.path.exists(full_book_path):
                    os.chdir(full_book_path)
                    # Log for debugging
                    with open('/tmp/hook-debug.log', 'a') as f:
                        f.write(f"Changed directory to: {full_book_path}\n")
    
    except Exception as e:
        # Log errors for debugging
        with open('/tmp/hook-debug.log', 'a') as f:
            f.write(f"Hook error: {str(e)}\n")
        pass

if __name__ == "__main__":
    main()
    sys.exit(0)