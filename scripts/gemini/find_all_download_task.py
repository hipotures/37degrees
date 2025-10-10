#!/usr/bin/env python3
"""
Find all download tasks across all books
Returns JSON array of all pending audio_dwn tasks where audio_gen is completed
"""

import subprocess
import sys
import json
import os

TARGET_LIST = "cc-au-notebooklm"
SUPPORTED_LANGUAGES = ["pl", "en", "es", "pt", "hi", "ja", "ko", "de", "fr"]
MAX_BOOKS_TO_CHECK = 20  # Limit how many books to process

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

def get_books_with_pending_downloads():
    """Get books that have at least one pending audio_dwn (quick filter)"""
    books = set()

    # Check all languages for pending audio_dwn
    for lang in SUPPORTED_LANGUAGES:
        dwn_key = f"audio_dwn_{lang}"
        output, returncode = run_todoit_cmd([
            "item", "find-status", "--list", TARGET_LIST,
            "--status", "pending",
            "--complex", f'{{"{dwn_key}": "pending"}}',
            "--limit", "30"
        ])

        if returncode == 0:
            try:
                result = json.loads(output)
                if result.get("data"):
                    for book_data in result["data"]:
                        book_key = book_data.get("Parent Key")
                        if book_key:
                            books.add(book_key)
            except (json.JSONDecodeError, KeyError):
                pass

    return sorted(list(books))

def find_all_downloads_in_book(book_key):
    """Find ALL pending audio_dwn tasks in a specific book where audio_gen is completed"""
    # Get all subitems for this book
    output, returncode = run_todoit_cmd([
        "item", "list", "--list", TARGET_LIST,
        "--item", book_key
    ])

    if returncode != 0:
        return []

    try:
        json_start = output.find('{')
        if json_start == -1:
            return []

        progress_pos = output.find('\nProgress:')
        if progress_pos != -1:
            json_part = output[json_start:progress_pos]
        else:
            json_part = output[json_start:]

        result = json.loads(json_part)

        if not result.get("data"):
            return []

        # Build status map for all subitems
        subitem_status = {}
        for subitem in result["data"]:
            key = subitem.get("Key")
            status = subitem.get("Status")
            if key:
                subitem_status[key] = status

        # Find ALL pending audio_dwn where corresponding audio_gen is completed
        downloads = []
        book_number = int(book_key[:4])
        notebook_url = get_notebook_url(book_number)

        for lang in SUPPORTED_LANGUAGES:
            gen_key = f"audio_gen_{lang}"
            dwn_key = f"audio_dwn_{lang}"

            gen_status = subitem_status.get(gen_key)
            dwn_status = subitem_status.get(dwn_key)

            # Both must exist, gen must be completed, dwn must be pending
            if gen_status == "completed" and dwn_status == "pending":
                downloads.append({
                    "book_key": book_key,
                    "language_code": lang,
                    "subitem_key": dwn_key,
                    "notebook_url": notebook_url,
                    "status": "found"
                })

        return downloads

    except (json.JSONDecodeError, KeyError):
        return []

def main():
    # Get books that have pending audio_dwn (quick pre-filter)
    books = get_books_with_pending_downloads()

    # Limit number of books to process
    books = books[:MAX_BOOKS_TO_CHECK]

    if not books:
        print(json.dumps({
            "status": "no_tasks_found",
            "message": "No books with pending audio_dwn",
            "data": []
        }))
        sys.exit(0)

    # Collect ALL download tasks from ALL books
    all_downloads = []
    for book_key in books:
        downloads = find_all_downloads_in_book(book_key)
        all_downloads.extend(downloads)

    if all_downloads:
        print(json.dumps({
            "status": "success",
            "count": len(all_downloads),
            "data": all_downloads
        }, ensure_ascii=False))
        sys.exit(0)
    else:
        print(json.dumps({
            "status": "no_tasks_found",
            "message": "No pending audio_dwn tasks with completed audio_gen",
            "data": []
        }))
        sys.exit(0)

if __name__ == "__main__":
    main()
