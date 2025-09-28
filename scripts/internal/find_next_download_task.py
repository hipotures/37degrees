#!/usr/bin/env python3
"""
Optimized version of find_next_download_task.py
Uses more efficient todoit queries to minimize subprocess calls
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

def get_notebook_url(book_number):
    """Get the appropriate NotebookLM URL based on book number"""
    if 1 <= book_number <= 50:
        return "https://notebooklm.google.com/notebook/ad8ec869-2284-44d3-bc06-b493e5990d81"
    elif 51 <= book_number <= 100:
        return "https://notebooklm.google.com/notebook/ea74e09e-0483-4e15-a3ee-59de799e721b"
    elif 101 <= book_number <= 150:
        return "https://notebooklm.google.com/notebook/05296cd4-601d-4760-b34e-f41190b34349"
    elif 151 <= book_number <= 200:
        return "https://notebooklm.google.com/notebook/e87e6c2c-f56e-49e9-8216-6c3eb1c107cc"
    else:
        return None

def main():
    # Strategy: Use one command to find books with pending audio_dwn tasks
    # This is much more efficient than iterating through all books

    # Try each language in priority order
    for lang in SUPPORTED_LANGUAGES:
        dwn_key = f"audio_dwn_{lang}"

        # COMMAND 1: Find books with pending audio_dwn for this language
        output1, returncode1 = run_todoit_cmd([
            "item", "find-status", "--list", TARGET_LIST,
            "--status", "in_progress",
            "--complex", f'{{"item": {{"status": "in_progress"}}, "subitem": {{"{dwn_key}": "pending"}}}}',
            "--limit", "1"  # We only need the first one
        ])

        if returncode1 != 0:
            continue  # Try next language

        try:
            result1 = json.loads(output1)
            if not result1.get("data"):
                continue  # No books found for this language

            # Found a book! Get the parent key
            book_key = result1["data"][0]["Parent Key"]

            # COMMAND 2: Verify this book has completed audio_gen for this language
            gen_key = f"audio_gen_{lang}"
            output2, returncode2 = run_todoit_cmd([
                "item", "find-status", "--list", TARGET_LIST,
                "--status", "completed",
                "--complex", f'{{"item": {{"key": "{book_key}"}}, "subitem": {{"{gen_key}": "completed"}}}}',
                "--limit", "1"
            ])

            if returncode2 != 0:
                continue  # This book doesn't have completed audio_gen

            try:
                result2 = json.loads(output2)
                if not result2.get("data"):
                    continue  # No completed audio_gen found

                # Perfect! We found a book with completed audio_gen and pending audio_dwn
                book_number = int(book_key[:4])
                notebook_url = get_notebook_url(book_number)

                # COMMAND 3: Try to get audio title (but don't fail if it doesn't exist)
                output3, returncode3 = run_todoit_cmd([
                    "item", "property", "get",
                    "--list", TARGET_LIST,
                    "--item", book_key,
                    "--subitem", gen_key,
                    "--key", "nb_au_title"
                ])

                audio_title = None
                if returncode3 == 0 and output3:
                    try:
                        title_data = json.loads(output3)
                        if title_data.get("data") and len(title_data["data"]) > 0:
                            audio_title = title_data["data"][0].get("nb_au_title")
                    except json.JSONDecodeError:
                        if "nb_au_title:" in output3:
                            audio_title = output3.split("nb_au_title:", 1)[1].strip()

                result = {
                    "book_key": book_key,
                    "language_code": lang,
                    "subitem_key": dwn_key,
                    "notebook_url": notebook_url,
                    "audio_title": audio_title,
                    "status": "found"
                }
                print(json.dumps(result, ensure_ascii=False))
                sys.exit(0)

            except (json.JSONDecodeError, KeyError):
                continue  # Try next language

        except (json.JSONDecodeError, KeyError, IndexError):
            continue  # Try next language

    # No tasks found in any language
    print(json.dumps({"status": "no_tasks_found", "message": "No pending audio_dwn tasks found with completed audio_gen"}))
    sys.exit(1)

if __name__ == "__main__":
    main()