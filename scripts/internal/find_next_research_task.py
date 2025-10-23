#!/usr/bin/env python3
"""
Find next pending Deep Research task from gemini-au-deep-research list.
Simpler than audio version - no languages, no subitems, just item-level tasks.

Usage:
    python find_next_research_task.py

Output JSON:
    {"SOURCE_NAME": "0055_of_mice_and_men", "STATUS": "found"}
    {"status": "no_tasks_found", "message": "..."}
    {"status": "error", "message": "..."}
"""

import subprocess
import sys
import json
import os

TARGET_LIST = "gemini-au-deep-research"

def run_todoit_cmd(args):
    """Run todoit command with JSON output"""
    cmd = ["todoit"] + args
    env = os.environ.copy()
    env["TODOIT_OUTPUT_FORMAT"] = "json"

    result = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    return result.stdout, result.returncode

def main():
    """Find first pending research task"""

    # Get first pending item from list using find-status
    output, returncode = run_todoit_cmd([
        "item", "find-status",
        "--list", TARGET_LIST,
        "--status", "pending",
        "--limit", "1"
    ])

    if returncode != 0:
        print(json.dumps({"status": "error", "message": "Failed to query TODOIT"}))
        sys.exit(1)

    try:
        # Parse JSON output (find-status returns clean JSON)
        result = json.loads(output)

        if not result.get("data") or len(result["data"]) == 0:
            print(json.dumps({"status": "no_tasks_found", "message": "No pending research tasks"}))
            sys.exit(0)

        # Get first pending item (find-status uses "Item Key" field)
        first_item = result["data"][0]
        book_key = first_item.get("Item Key")

        if not book_key:
            print(json.dumps({"status": "error", "message": "Missing 'Item Key' in TODOIT response"}))
            sys.exit(1)

        # Success - return book folder
        print(json.dumps({
            "SOURCE_NAME": book_key,
            "STATUS": "found"
        }))
        sys.exit(0)

    except (json.JSONDecodeError, KeyError) as e:
        print(json.dumps({"status": "error", "message": f"JSON parsing error: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
