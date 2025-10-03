#!/usr/bin/env python3
"""
Language-first download task finder - CORRECTED VERSION
Prioritizes language over book position, with proper audio_gen verification
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
    # Strategy: For each language in priority order, find books with:
    # - completed audio_gen_{lang}
    # - pending audio_dwn_{lang}
    # Then verify in detail and return first match

    for lang in SUPPORTED_LANGUAGES:
        gen_key = f"audio_gen_{lang}"
        dwn_key = f"audio_dwn_{lang}"

        # Find books with completed audio_gen AND pending audio_dwn for this language
        output1, returncode1 = run_todoit_cmd([
            "item", "find-status", "--list", TARGET_LIST,
            "--status", "pending",
            "--complex", f'{{"{gen_key}": "completed", "{dwn_key}": "pending"}}',
            "--limit", "10"  # Get multiple to find first by position
        ])

        if returncode1 != 0:
            continue

        try:
            result1 = json.loads(output1)
            if not result1.get("data"):
                continue

            # Sort by parent key (position) to get first book
            books = sorted(result1["data"], key=lambda x: x.get("Parent Key", ""))

            for book_data in books:
                book_key = book_data.get("Parent Key")
                if not book_key:
                    continue

                # Double-check by getting subitems (to be absolutely sure)
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

                    # Verify gen is completed and dwn is pending
                    gen_completed = False
                    dwn_pending = False

                    for subitem in result2["data"]:
                        if subitem.get("Key") == gen_key and subitem.get("Status") == "completed":
                            gen_completed = True
                        if subitem.get("Key") == dwn_key and subitem.get("Status") == "pending":
                            dwn_pending = True

                    if gen_completed and dwn_pending:
                        # Found it!
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
                    continue

        except (json.JSONDecodeError, KeyError):
            continue

    # No tasks found
    print(json.dumps({"status": "no_tasks_found", "message": "No pending audio_dwn tasks with completed audio_gen"}))
    sys.exit(1)

if __name__ == "__main__":
    main()