#!/usr/bin/env python3
"""
Book-first version of find_next_audio_task.py
Uses exactly 2 commands like the original:
1. todoit item find-status (get first book with completed afa_gen and any completed audio_gen)
2. todoit item list (get all subitems for that book)
"""

import subprocess
import sys
import json
import os

TARGET_LIST = "cc-au-notebooklm"
SUPPORTED_LANGUAGES = ["pl", "en", "es", "pt", "hi", "ja", "ko", "de", "fr"]

def run_todoit_cmd(args):
    """Run todoit command with JSON output"""
    cmd = ["todoit"] + args
    env = os.environ.copy()
    env["TODOIT_OUTPUT_FORMAT"] = "json"

    result = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    return result.stdout, result.returncode

def main():
    # COMMAND 1: Get first book with completed afa_gen that has at least one audio_gen task
    # Strategy: Find books that have started audio generation (any completed audio_gen)
    # or books that are ready to start (completed afa_gen, all audio_gen pending)

    # First try: Find books with completed afa_gen and at least one completed audio_gen
    output1, returncode1 = run_todoit_cmd([
        "item", "find-status", "--list", TARGET_LIST,
        "--status", "in_progress",  # Required by todoit API
        "--complex", '{"item": {"status": "in_progress"}, "subitem": {"afa_gen": "completed"}}',
        "--limit", "20"  # Get multiple books to check their progress
    ])

    if returncode1 != 0:
        print(json.dumps({"status": "error", "message": "Command 1 failed"}))
        sys.exit(1)

    try:
        result1 = json.loads(output1)
        if not result1.get("data"):
            print(json.dumps({"status": "no_tasks_found", "message": "No books with completed afa_gen"}))
            sys.exit(1)

        # Iterate through books in position order (book-first strategy)
        for book_data in result1["data"]:
            book_key = book_data["Parent Key"]

            # COMMAND 2: Get all subitems for this book
            output2, returncode2 = run_todoit_cmd([
                "item", "list", "--list", TARGET_LIST,
                "--item", book_key
            ])

            if returncode2 != 0:
                continue  # Skip this book

            try:
                # Find JSON part in output (skip title lines and progress footer)
                json_start = output2.find('{')
                if json_start == -1:
                    continue

                # Find end of JSON (last '}' before Progress line)
                progress_pos = output2.find('\nProgress:')
                if progress_pos != -1:
                    json_part = output2[json_start:progress_pos]
                else:
                    json_part = output2[json_start:]

                result2 = json.loads(json_part)

                if not result2.get("data"):
                    continue

                # Find first pending audio_gen_XX in language priority order for THIS book
                for lang in SUPPORTED_LANGUAGES:
                    subitem_key = f"audio_gen_{lang}"
                    for subitem in result2["data"]:
                        if subitem.get("Key") == subitem_key and subitem.get("Status") == "pending":
                            # Found it!
                            result = {
                                "SOURCE_NAME": book_key,
                                "LANGUAGE_CODE": lang,
                                "PENDING_SUBITEM_KEY": subitem_key,
                                "STATUS": "found"
                            }
                            print(json.dumps(result))
                            sys.exit(0)

                # No pending audio_gen found in this book, try next book

            except (json.JSONDecodeError, KeyError):
                continue  # Skip this book and try next one

        # No pending audio_gen found in any book
        print(json.dumps({"status": "no_tasks_found", "message": "No pending audio_gen tasks found"}))
        sys.exit(1)

    except (json.JSONDecodeError, KeyError, IndexError):
        print(json.dumps({"status": "error", "message": "Failed to parse command 1 result"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
