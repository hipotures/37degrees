#!/usr/bin/env python3
"""
Hybrid strategy for find_next_audio_task.py
Priority: High priority languages (pl, en, es) first, then book-first for remaining languages
"""

import subprocess
import sys
import json
import os

TARGET_LIST = "cc-au-notebooklm"
HIGH_PRIORITY_LANGUAGES = ["pl", "en", "es"]  # These get language-first priority
ALL_LANGUAGES = ["pl", "en", "es", "pt", "hi", "ja", "ko", "de", "fr"]

def run_todoit_cmd(args):
    """Run todoit command with JSON output"""
    cmd = ["todoit"] + args
    env = os.environ.copy()
    env["TODOIT_OUTPUT_FORMAT"] = "json"

    result = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    return result.stdout, result.returncode

def find_by_language_priority(languages):
    """Find tasks using language-first strategy for given languages"""
    for lang in languages:
        gen_key = f"audio_gen_{lang}"

        output1, returncode1 = run_todoit_cmd([
            "item", "find-status", "--list", TARGET_LIST,
            "--status", "pending",
            "--complex", f'{{"afa_gen": "completed", "{gen_key}": "pending"}}',
            "--limit", "1"
        ])

        if returncode1 != 0:
            continue

        try:
            result1 = json.loads(output1)
            if result1.get("data"):
                book_key = result1["data"][0]["Parent Key"]
                return {
                    "book_key": book_key,
                    "language_code": lang,
                    "subitem_key": gen_key,
                    "status": "found"
                }
        except (json.JSONDecodeError, KeyError, IndexError):
            continue

    return None

def find_by_book_priority():
    """Find tasks using book-first strategy"""
    # Get books with completed afa_gen
    output1, returncode1 = run_todoit_cmd([
        "item", "find-status", "--list", TARGET_LIST,
        "--status", "in_progress",
        "--complex", '{"item": {"status": "in_progress"}, "subitem": {"afa_gen": "completed"}}',
        "--limit", "10"
    ])

    if returncode1 != 0:
        return None

    try:
        result1 = json.loads(output1)
        if not result1.get("data"):
            return None

        # Iterate through books in position order
        for book_data in result1["data"]:
            book_key = book_data["Parent Key"]

            # Get all subitems for this book
            output2, returncode2 = run_todoit_cmd([
                "item", "list", "--list", TARGET_LIST,
                "--item", book_key
            ])

            if returncode2 != 0:
                continue

            try:
                json_start = output2.find('{')
                if json_start == -1:
                    continue

                progress_pos = output2.find('\nProgress:')
                if progress_pos != -1:
                    json_part = output2[json_start:progress_pos]
                else:
                    json_part = output2[json_start:]

                result2 = json.loads(json_part)

                if not result2.get("data"):
                    continue

                # Find first pending audio_gen in remaining languages (not high priority)
                remaining_languages = [l for l in ALL_LANGUAGES if l not in HIGH_PRIORITY_LANGUAGES]
                for lang in remaining_languages:
                    subitem_key = f"audio_gen_{lang}"
                    for subitem in result2["data"]:
                        if subitem.get("Key") == subitem_key and subitem.get("Status") == "pending":
                            return {
                                "book_key": book_key,
                                "language_code": lang,
                                "subitem_key": subitem_key,
                                "status": "found"
                            }

            except (json.JSONDecodeError, KeyError):
                continue

    except (json.JSONDecodeError, KeyError, IndexError):
        pass

    return None

def main():
    # Phase 1: Try high priority languages first (language-first strategy)
    result = find_by_language_priority(HIGH_PRIORITY_LANGUAGES)
    if result:
        print(json.dumps(result))
        sys.exit(0)

    # Phase 2: Try remaining languages with book-first strategy
    result = find_by_book_priority()
    if result:
        print(json.dumps(result))
        sys.exit(0)

    # No tasks found
    print(json.dumps({"status": "no_tasks_found", "message": "No pending audio_gen tasks found"}))
    sys.exit(1)

if __name__ == "__main__":
    main()