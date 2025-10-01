#!/usr/bin/env python3
"""
Continue-first strategy: Prioritize continuing work on books that have already started audio generation
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

def find_books_with_any_completed_audio():
    """Find books that have at least one completed audio_gen (books in progress)"""
    books_in_progress = []

    for lang in SUPPORTED_LANGUAGES:
        gen_key = f"audio_gen_{lang}"

        output, returncode = run_todoit_cmd([
            "item", "find-status", "--list", TARGET_LIST,
            "--status", "completed",
            "--complex", f'{{"item": {{"status": "in_progress"}}, "subitem": {{"{gen_key}": "completed"}}}}',
            "--limit", "20"
        ])

        if returncode == 0:
            try:
                result = json.loads(output)
                if result.get("data"):
                    for book_data in result["data"]:
                        book_key = book_data["Parent Key"]
                        if book_key not in books_in_progress:
                            books_in_progress.append(book_key)
            except (json.JSONDecodeError, KeyError):
                continue

    return books_in_progress

def find_next_task_in_book(book_key):
    """Find next pending audio_gen task in a specific book"""
    output, returncode = run_todoit_cmd([
        "item", "list", "--list", TARGET_LIST,
        "--item", book_key
    ])

    if returncode != 0:
        return None

    try:
        json_start = output.find('{')
        if json_start == -1:
            return None

        progress_pos = output.find('\nProgress:')
        if progress_pos != -1:
            json_part = output[json_start:progress_pos]
        else:
            json_part = output[json_start:]

        result = json.loads(json_part)

        if not result.get("data"):
            return None

        # Find first pending audio_gen in language priority order
        for lang in SUPPORTED_LANGUAGES:
            subitem_key = f"audio_gen_{lang}"
            for subitem in result["data"]:
                if subitem.get("Key") == subitem_key and subitem.get("Status") == "pending":
                    return {
                        "book_key": book_key,
                        "language_code": lang,
                        "subitem_key": subitem_key,
                        "status": "found"
                    }

        return None

    except (json.JSONDecodeError, KeyError):
        return None

def find_new_book_task():
    """Find first task in books that haven't started audio generation yet"""
    for lang in SUPPORTED_LANGUAGES:
        gen_key = f"audio_gen_{lang}"

        output, returncode = run_todoit_cmd([
            "item", "find-status", "--list", TARGET_LIST,
            "--status", "pending",
            "--complex", f'{{"afa_gen": "completed", "{gen_key}": "pending"}}',
            "--limit", "1"
        ])

        if returncode == 0:
            try:
                result = json.loads(output)
                if result.get("data"):
                    book_key = result["data"][0]["Parent Key"]

                    # Check if this book has ANY completed audio_gen (if so, skip - it's handled in phase 1)
                    books_in_progress = find_books_with_any_completed_audio()
                    if book_key not in books_in_progress:
                        return {
                            "book_key": book_key,
                            "language_code": lang,
                            "subitem_key": gen_key,
                            "status": "found"
                        }
            except (json.JSONDecodeError, KeyError):
                continue

    return None

def main():
    # Phase 1: Continue work on books that have already started audio generation
    books_in_progress = find_books_with_any_completed_audio()

    # Sort books by key (position order) to maintain consistency
    books_in_progress.sort()

    for book_key in books_in_progress:
        result = find_next_task_in_book(book_key)
        if result:
            print(json.dumps(result))
            sys.exit(0)

    # Phase 2: Start new books (books with no completed audio_gen yet)
    result = find_new_book_task()
    if result:
        print(json.dumps(result))
        sys.exit(0)

    # No tasks found
    print(json.dumps({"status": "no_tasks_found", "message": "No pending audio_gen tasks found"}))
    sys.exit(1)

if __name__ == "__main__":
    main()