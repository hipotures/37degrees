#!/usr/bin/env python3
"""
Book-first version of find_next_download_task.py
Downloads all languages for one book before moving to the next book
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

def find_books_with_completed_audio():
    """Find books that have at least one completed audio_gen (ready for download)"""
    output, returncode = run_todoit_cmd([
        "item", "find-status", "--list", TARGET_LIST,
        "--status", "completed",
        "--complex", '{"item": {"status": "in_progress"}, "subitem": {"audio_gen_pl": "completed"}}',
        "--limit", "50"
    ])

    if returncode != 0:
        return []

    books = []
    try:
        result = json.loads(output)
        if result.get("data"):
            for book_data in result["data"]:
                book_key = book_data["Parent Key"]
                if book_key not in books:
                    books.append(book_key)
    except (json.JSONDecodeError, KeyError):
        pass

    return books

def find_next_download_in_book(book_key):
    """Find next pending audio_dwn task in a specific book"""
    # Get all subitems for this book
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

        # Find first pending audio_dwn in language priority order
        # But only if corresponding audio_gen is completed
        for lang in SUPPORTED_LANGUAGES:
            gen_key = f"audio_gen_{lang}"
            dwn_key = f"audio_dwn_{lang}"

            gen_completed = False
            dwn_pending = False

            for subitem in result["data"]:
                if subitem.get("Key") == gen_key and subitem.get("Status") == "completed":
                    gen_completed = True
                if subitem.get("Key") == dwn_key and subitem.get("Status") == "pending":
                    dwn_pending = True

            if gen_completed and dwn_pending:
                # Found a language ready to download!
                book_number = int(book_key[:4])
                notebook_url = get_notebook_url(book_number)

                # Try to get audio title
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

                return {
                    "book_key": book_key,
                    "language_code": lang,
                    "subitem_key": dwn_key,
                    "notebook_url": notebook_url,
                    "audio_title": audio_title,
                    "status": "found"
                }

        return None

    except (json.JSONDecodeError, KeyError):
        return None

def main():
    # Find books that have completed audio_gen (ready for download)
    books = find_books_with_completed_audio()

    if not books:
        print(json.dumps({"status": "no_tasks_found", "message": "No books with completed audio_gen"}))
        sys.exit(1)

    # Sort books by key (position order) to maintain consistency
    books.sort()

    # Iterate through books in position order
    for book_key in books:
        result = find_next_download_in_book(book_key)
        if result:
            print(json.dumps(result, ensure_ascii=False))
            sys.exit(0)

    # No pending download tasks found
    print(json.dumps({"status": "no_tasks_found", "message": "No pending audio_dwn tasks found"}))
    sys.exit(1)

if __name__ == "__main__":
    main()