#!/usr/bin/env python3
"""
Script to copy all items from gemini-deep-research to cc-au-research
Changes "Deep Research for..." to "Research for..." in titles
"""

import subprocess
import json
import sys

def run_todoit_command(command):
    """Run todoit CLI command and return result"""
    try:
        result = subprocess.run(
            f"TODOIT_OUTPUT_FORMAT=json {command}",
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output: {e}")
        return None

def safe_add_item(list_key, item_key, content):
    """Safely add item using subprocess with proper argument handling"""
    cmd = [
        "todoit", "item", "add",
        "--list", list_key,
        "--item", item_key,
        "--title", content
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, ""
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def main():
    print("Fetching items from gemini-deep-research list...")
    
    # Get all items from source list using todoit CLI
    result = run_todoit_command("todoit list show --list gemini-deep-research")
    
    if not result or not result.get("success", True):
        print(f"Error fetching source list: {result}")
        return
    
    # Extract items from the result
    items_data = result.get("items", {}).get("data", [])
    print(f"Found {len(items_data)} items in source list")
    
    if not items_data:
        print("No items found to copy")
        return
    
    # Copy each item to target list with modified title
    success_count = 0
    error_count = 0
    
    for item in items_data:
        item_key = item.get("Key", "")
        content = item.get("Task", "")
        
        if not item_key or not content:
            print(f"Skipping item with missing data: {item}")
            error_count += 1
            continue
        
        # Change "Deep Research for..." to "Research for..."
        modified_content = content.replace("Deep Research for", "Research for")
        
        # Use safe subprocess call with proper argument handling
        success, error = safe_add_item("cc-au-research", item_key, modified_content)
        
        if success:
            success_count += 1
            print(f"✓ Added: {item_key}")
        else:
            error_count += 1
            print(f"✗ Failed: {item_key} - {error}")
    
    print(f"\nSummary:")
    print(f"Successfully added: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Total processed: {len(items_data)}")

if __name__ == "__main__":
    main()