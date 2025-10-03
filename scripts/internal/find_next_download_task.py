#!/usr/bin/env python3
"""
Fast book-first download task finder
Optimized to minimize queries - only checks books that have pending audio_dwn
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

def get_books_with_pending_downloads():
    """Get books that have at least one pending audio_dwn (quick filter)"""
    books = set()

    # Quick check: find any books with pending audio_dwn_pl (most books will have this)
    output, returncode = run_todoit_cmd([
        "item", "find-status", "--list", TARGET_LIST,
        "--status", "pending",
        "--complex", '{"audio_dwn_pl": "pending"}',
        "--limit", "50"
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

    # Also check other languages in case pl is completed
    for lang in ["en", "es", "pt"]:  # Just check a few high-priority languages
        dwn_key = f"audio_dwn_{lang}"
        output, returncode = run_todoit_cmd([
            "item", "find-status", "--list", TARGET_LIST,
            "--status", "pending",
            "--complex", f'{{"{dwn_key}": "pending"}}',
            "--limit", "20"
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

def find_next_download_in_book(book_key):
    """Find next pending audio_dwn task in a specific book where audio_gen is completed"""
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

        # Build status map for all subitems
        subitem_status = {}
        for subitem in result["data"]:
            key = subitem.get("Key")
            status = subitem.get("Status")
            if key:
                subitem_status[key] = status

        # Find first pending audio_dwn in language priority order
        # BUT ONLY if corresponding audio_gen is completed
        for lang in SUPPORTED_LANGUAGES:
            gen_key = f"audio_gen_{lang}"
            dwn_key = f"audio_dwn_{lang}"

            gen_status = subitem_status.get(gen_key)
            dwn_status = subitem_status.get(dwn_key)

            # Both must exist, gen must be completed, dwn must be pending
            if gen_status == "completed" and dwn_status == "pending":
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
    # Get books that have pending audio_dwn (quick pre-filter)
    books = get_books_with_pending_downloads()

    if not books:
        print(json.dumps({"status": "no_tasks_found", "message": "No books with pending audio_dwn"}))
        sys.exit(1)

    # Iterate through books in position order (book-first strategy)
    for book_key in books:
        result = find_next_download_in_book(book_key)
        if result:
            print(json.dumps(result, ensure_ascii=False))
            sys.exit(0)

    # No valid download tasks found (pending dwn but no completed gen)
    print(json.dumps({"status": "no_tasks_found", "message": "No pending audio_dwn tasks with completed audio_gen"}))
    sys.exit(1)

if __name__ == "__main__":
    main()