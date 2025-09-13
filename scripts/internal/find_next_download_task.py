#!/usr/bin/env python3
"""
Find next audio download task using book-first iteration logic
Similar to find_next_audio_task.py but for audio_dwn_XX subitems
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
    # COMMAND 1: Get ALL books with completed afa_gen and at least one completed audio_gen
    # We need books that have generated audio ready to download
    output1, returncode1 = run_todoit_cmd([
        "item", "find-status", "--list", TARGET_LIST,
        "--status", "in_progress",
        "--complex", '{"afa_gen": "completed"}',
        "--limit", "50"
    ])

    if returncode1 != 0:
        print(json.dumps({"status": "error", "message": "Command 1 failed"}))
        sys.exit(1)

    try:
        result1 = json.loads(output1)
        if not result1.get("data"):
            print(json.dumps({"status": "no_tasks_found", "message": "No books with completed afa_gen"}))
            sys.exit(1)

        # ITERATE through all books until we find one with pending audio_dwn tasks
        for book_data in result1["data"]:
            book_key = book_data["Parent Key"]

            # COMMAND 2: Get all subitems for this book
            output2, returncode2 = run_todoit_cmd([
                "item", "list", "--list", TARGET_LIST,
                "--item", book_key
            ])

            if returncode2 != 0:
                continue  # Skip this book and try next one

            try:
                # Find JSON part in output
                json_start = output2.find('{')
                if json_start == -1:
                    continue  # Skip this book

                # Find end of JSON (before Progress line)
                progress_pos = output2.find('\nProgress:')
                if progress_pos != -1:
                    json_part = output2[json_start:progress_pos]
                else:
                    json_part = output2[json_start:]

                result2 = json.loads(json_part)

                if not result2.get("data"):
                    continue  # Skip this book

                # Check if this book has any completed audio_gen tasks
                has_completed_audio = False
                for subitem in result2["data"]:
                    if (subitem.get("Key", "").startswith("audio_gen_") and
                        subitem.get("Status") == "completed"):
                        has_completed_audio = True
                        break

                if not has_completed_audio:
                    continue  # Skip books without any completed audio

                # Find first pending audio_dwn_XX in language order
                for lang in SUPPORTED_LANGUAGES:
                    gen_key = f"audio_gen_{lang}"
                    dwn_key = f"audio_dwn_{lang}"

                    # Check if audio_gen is completed but audio_dwn is pending
                    gen_completed = False
                    dwn_pending = False

                    for subitem in result2["data"]:
                        if subitem.get("Key") == gen_key and subitem.get("Status") == "completed":
                            gen_completed = True
                        if subitem.get("Key") == dwn_key and subitem.get("Status") == "pending":
                            dwn_pending = True

                    if gen_completed and dwn_pending:
                        # Found a language ready to download!
                        # Extract book number from book_key (format: NNNN_xxx)
                        book_number = int(book_key[:4])
                        notebook_url = get_notebook_url(book_number)

                        # Get the audio title from property if it exists
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
                                # Parse JSON output
                                title_data = json.loads(output3)
                                if title_data.get("data") and len(title_data["data"]) > 0:
                                    audio_title = title_data["data"][0].get("nb_au_title")
                            except json.JSONDecodeError:
                                # Fallback to text parsing if not JSON
                                if "nb_au_title:" in output3:
                                    audio_title = output3.split("nb_au_title:", 1)[1].strip()

                        result = {
                            "book_key": book_key,
                            "language_code": lang,
                            "subitem_key": dwn_key,
                            "notebook_url": notebook_url,
                            "audio_title": audio_title,  # Can be None if not found
                            "status": "found"
                        }
                        print(json.dumps(result, ensure_ascii=False))
                        sys.exit(0)

            except (json.JSONDecodeError, KeyError):
                continue  # Skip this book and try next one

        # No pending audio_dwn found in any book
        print(json.dumps({"status": "no_tasks_found", "message": "No pending audio_dwn tasks found (or no completed audio_gen)"}))
        sys.exit(1)

    except (json.JSONDecodeError, KeyError, IndexError):
        print(json.dumps({"status": "error", "message": "Failed to parse command 1 result"}))
        sys.exit(1)

if __name__ == "__main__":
    main()