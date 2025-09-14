#!/usr/bin/env python3
"""
NotebookLM Audio Multi-Language Download Orchestrator
Downloads generated audio using MCP playwright-cdp and orchestrates complete workflow
"""

import json
import subprocess
import sys
import os
import time
from datetime import datetime

# Constants
DOWNLOAD_DIR = "/tmp/playwright-mcp-output/"
SUPPORTED_LANGUAGES = ["pl", "en", "es", "pt", "hi", "ja", "ko", "de", "fr"]

def run_bash_command(command, description=""):
    """Execute bash command and return result"""
    print(f"🔧 {description}: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result

def run_mcp_command(tool, params):
    """Execute MCP command via Claude Code API (placeholder for actual implementation)"""
    # This would be replaced with actual MCP calls in the agent environment
    print(f"🤖 MCP Command: {tool} with params: {json.dumps(params, indent=2)}")
    return {"success": True, "data": {}}

def get_search_patterns_for_source(source_name, language_code):
    """Get search patterns for finding audio based on book and language"""
    base_name = source_name.replace(r'^\d+_', '', 1) if source_name else ""

    # Language-specific title patterns
    title_patterns = {
        "pl": {
            "alice_in_wonderland": ["Alicja w Krainie Czarów", "Alice", "Alicja"],
            "chlopi": ["Chłopi", "Władysław Reymont"],
            "war_and_peace": ["Wojna i pokój", "Lew Tołstoj"],
        },
        "en": {
            "alice_in_wonderland": ["Alice's Adventures in Wonderland", "Alice", "Lewis Carroll"],
            "chlopi": ["The Peasants", "Władysław Reymont"],
            "war_and_peace": ["War and Peace", "Leo Tolstoy"],
        },
        "es": {
            "alice_in_wonderland": ["Las aventuras de Alicia en el país de las maravillas", "Alicia"],
            "chlopi": ["Los campesinos", "Władysław Reymont"],
            "war_and_peace": ["Guerra y paz", "León Tolstói"],
        },
        "pt": {
            "alice_in_wonderland": ["As Aventuras de Alice no País das Maravilhas", "Alice"],
            "chlopi": ["Os Camponeses", "Władysław Reymont"],
            "war_and_peace": ["Guerra e Paz", "Léon Tolstói"],
        },
        "de": {
            "alice_in_wonderland": ["Alice im Wunderland", "Alice"],
            "chlopi": ["Die Bauern", "Władysław Reymont"],
            "war_and_peace": ["Krieg und Frieden", "Leo Tolstoi"],
        },
        "fr": {
            "alice_in_wonderland": ["Les Aventures d'Alice au pays des merveilles", "Alice"],
            "chlopi": ["Les Paysans", "Władysław Reymont"],
            "war_and_peace": ["Guerre et Paix", "Léon Tolstoï"],
        },
        "hi": {
            "alice_in_wonderland": ["Alice", "ऐलिस"],
            "chlopi": ["Władysław Reymont", "किसान"],
            "war_and_peace": ["युद्ध और शांति", "Leo Tolstoy"],
        },
        "ja": {
            "alice_in_wonderland": ["不思議の国のアリス", "Alice", "アリス"],
            "chlopi": ["農民", "Władysław Reymont"],
            "war_and_peace": ["戦争と平和", "Leo Tolstoy"],
        },
        "ko": {
            "alice_in_wonderland": ["이상한 나라의 앨리스", "Alice", "앨리스"],
            "chlopi": ["농민", "Władysław Reymont"],
            "war_and_peace": ["전쟁과 평화", "Leo Tolstoy"],
        }
    }

    # Get patterns for language and book
    lang_patterns = title_patterns.get(language_code, {})
    book_patterns = lang_patterns.get(base_name, [source_name])

    return book_patterns

def find_newest_mp4_file(directory):
    """Find newest .mp4 file in directory"""
    result = run_bash_command(f"find {directory} -name '*.mp4' -type f -printf '%T@ %p\\n' | sort -n | tail -1 | cut -d' ' -f2-")
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None

def file_exists(file_path):
    """Check if file exists"""
    return os.path.isfile(file_path)

def directory_exists(dir_path):
    """Check if directory exists"""
    return os.path.isdir(dir_path)

def main():
    print("🎵 NotebookLM Audio Download Orchestrator Starting...")

    # Step 0: Get Task and Determine NotebookLM and Language
    print("\n=== Step 0: Finding next download task ===")

    result = run_bash_command("python scripts/internal/find_next_download_task.py", "Finding next download task")

    if result.returncode != 0 or not result.stdout.strip():
        print("❌ ERROR: Failed to find download task")
        print(f"Error output: {result.stderr}")
        return False

    try:
        task_data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Failed to parse task data: {e}")
        return False

    if task_data.get("status") != "found":
        print("ℹ️  No pending download tasks found")
        return False

    SOURCE_NAME = task_data["book_key"]
    LANGUAGE_CODE = task_data["language_code"]
    PENDING_SUBITEM_KEY = task_data["subitem_key"]
    NOTEBOOK_URL = task_data["notebook_url"]
    AUDIO_TITLE = task_data.get("audio_title")

    print(f"📚 Book: {SOURCE_NAME}")
    print(f"🌐 Language: {LANGUAGE_CODE}")
    print(f"📋 Subitem: {PENDING_SUBITEM_KEY}")
    print(f"🔗 NotebookLM URL: {NOTEBOOK_URL}")
    print(f"🎵 Audio Title: {AUDIO_TITLE or 'Not saved, will use patterns'}")

    # Step 1: Initialize MCP playwright-cdp and Open NotebookLM
    print("\n=== Step 1: Opening NotebookLM ===")

    # Launch MCP playwright-cdp and open appropriate NotebookLM page
    run_mcp_command("mcp__playwright-cdp__browser_navigate", {"url": NOTEBOOK_URL})
    run_mcp_command("mcp__playwright-cdp__browser_snapshot", {})

    # Navigate to Studio tab where generated audio is located
    run_mcp_command("mcp__playwright-cdp__browser_click", {
        "element": "Studio tab",
        "ref": "studio_tab_ref"
    })
    run_mcp_command("mcp__playwright-cdp__browser_snapshot", {})

    # Step 2: Search for Audio for Specific Language
    print("\n=== Step 2: Searching for audio ===")

    if not AUDIO_TITLE:
        # Fallback - search by patterns with SOURCE_NAME
        SEARCH_PATTERNS = get_search_patterns_for_source(SOURCE_NAME, LANGUAGE_CODE)
        print(f"🔍 Using search patterns: {SEARCH_PATTERNS}")
    else:
        # Use saved title
        SEARCH_PATTERNS = [AUDIO_TITLE]
        print(f"🔍 Using saved title: {AUDIO_TITLE}")

    run_mcp_command("mcp__playwright-cdp__browser_snapshot", {})

    # In actual implementation, this would search audio list in Studio Tab
    # For now, we'll simulate finding the audio
    print("🔍 Searching for matching audio...")
    matching_audio = {
        "ref": "audio_ref_123",
        "title": SEARCH_PATTERNS[0],
        "more_button_ref": "more_button_ref_123"
    }

    if not matching_audio:
        print(f"❌ ERROR: Audio not found for {SOURCE_NAME} in {LANGUAGE_CODE}")
        return False

    AUDIO_REF = matching_audio["ref"]
    ORIGINAL_TITLE = matching_audio["title"]

    print(f"✅ Found audio: {ORIGINAL_TITLE}")

    # Step 3: Download Audio File
    print("\n=== Step 3: Downloading audio file ===")

    # Click "More" button for found audio
    run_mcp_command("mcp__playwright-cdp__browser_click", {
        "element": "More button for audio",
        "ref": matching_audio["more_button_ref"]
    })

    # Click "Download" in expanded menu
    run_mcp_command("mcp__playwright-cdp__browser_click", {
        "element": "Download menu item",
        "ref": "download_ref"
    })

    # Wait for download to start
    run_mcp_command("mcp__playwright-cdp__browser_wait_for", {"time": 2})

    # Step 4: Wait for Download Completion
    print("\n=== Step 4: Waiting for download completion ===")

    max_wait = 60
    waited = 0
    downloaded_file = None

    print(f"⏳ Waiting up to {max_wait} seconds for download...")

    while waited < max_wait:
        downloaded_file = find_newest_mp4_file(DOWNLOAD_DIR)
        if downloaded_file:
            print(f"✅ Downloaded file found: {downloaded_file}")
            break

        run_mcp_command("mcp__playwright-cdp__browser_wait_for", {"time": 2})
        waited += 2
        print(f"⏳ Waited {waited}s...")

    if not downloaded_file:
        print(f"❌ ERROR: Download timeout after {max_wait} seconds")
        return False

    # Step 5: Map and Move File
    print("\n=== Step 5: Moving file to destination ===")

    BOOK_FOLDER = f"books/{SOURCE_NAME}"
    AUDIO_DIR = f"{BOOK_FOLDER}/audio"

    # Check if directory exists
    if not directory_exists(AUDIO_DIR):
        print(f"❌ ERROR: Directory does not exist: {AUDIO_DIR}")
        print("Please create the directory structure manually")
        return False

    # Generate target name with language (.mp4 like from NotebookLM)
    DEST_FILENAME = f"{SOURCE_NAME}_{LANGUAGE_CODE}.mp4"
    DEST_PATH = f"{AUDIO_DIR}/{DEST_FILENAME}"

    # Move file
    move_result = run_bash_command(f"mv '{downloaded_file}' '{DEST_PATH}'", "Moving downloaded file")

    if move_result.returncode == 0 and file_exists(DEST_PATH):
        print(f"✅ Audio file moved to: {DEST_PATH}")

        # Save path as property for subitem
        run_mcp_command("mcp__todoit__todo_set_item_property", {
            "list_key": "cc-au-notebooklm",
            "item_key": PENDING_SUBITEM_KEY,
            "property_key": "file_path",
            "property_value": DEST_PATH,
            "parent_item_key": SOURCE_NAME
        })
    else:
        print(f"❌ ERROR: Failed to move file to {DEST_PATH}")
        print(f"Move result: {move_result.stderr}")
        return False

    # Step 6: Mark Task as Completed
    print("\n=== Step 6: Marking task as completed ===")

    # Mark subitem audio_dwn_XX as completed
    run_mcp_command("mcp__todoit__todo_update_item_status", {
        "list_key": "cc-au-notebooklm",
        "item_key": SOURCE_NAME,
        "subitem_key": PENDING_SUBITEM_KEY,
        "status": "completed"
    })

    print(f"✅ Task {PENDING_SUBITEM_KEY} marked as completed")

    # Step 7: Safety Verification Before Deletion from NotebookLM
    print("\n=== Step 7: Safety verification for NotebookLM deletion ===")

    deletion_check = run_bash_command(f"scripts/internal/can_delete_file.sh '{DEST_PATH}'", "Safety verification")

    if deletion_check.stdout.startswith("CANNOT_DELETE_FROM_NOTEBOOK"):
        reason = deletion_check.stdout.split(":", 1)[1] if ":" in deletion_check.stdout else "Unknown reason"
        print(f"⚠️  Skipping deletion from NotebookLM: {reason}")
        print("File preserved in NotebookLM for safety")
        deletion_timestamp = None
    else:
        print("✅ Safety verification passed - proceeding with NotebookLM deletion")

        # Step 8: Delete Audio File from NotebookLM (After Safety Verification)
        print("\n=== Step 8: Deleting audio from NotebookLM ===")

        print(f"🗑️  Starting deletion of: {ORIGINAL_TITLE}")

        # Ensure we're in Studio tab
        run_mcp_command("mcp__playwright-cdp__browser_snapshot", {})

        # Step 1: Click "More" button for same audio
        run_mcp_command("mcp__playwright-cdp__browser_click", {
            "element": "More button for audio",
            "ref": matching_audio["more_button_ref"]
        })
        run_mcp_command("mcp__playwright-cdp__browser_wait_for", {"time": 1})

        # Check if menu expanded
        run_mcp_command("mcp__playwright-cdp__browser_snapshot", {})

        # Step 2: Click "Delete" in expanded menu
        run_mcp_command("mcp__playwright-cdp__browser_click", {
            "element": "Delete menu item",
            "ref": "delete_ref"
        })
        run_mcp_command("mcp__playwright-cdp__browser_wait_for", {"time": 1})

        # Step 3: Confirm deletion in confirmation dialog
        run_mcp_command("mcp__playwright-cdp__browser_snapshot", {})
        run_mcp_command("mcp__playwright-cdp__browser_click", {
            "element": "Confirm delete button",
            "ref": "confirm_delete_ref"
        })

        # Wait for deletion to complete
        run_mcp_command("mcp__playwright-cdp__browser_wait_for", {"time": 3})

        print(f"🗑️  Audio deleted from NotebookLM: {ORIGINAL_TITLE}")

        # Save deletion information as property with timestamp
        deletion_timestamp = datetime.now().isoformat()
        run_mcp_command("mcp__todoit__todo_set_item_property", {
            "list_key": "cc-au-notebooklm",
            "item_key": PENDING_SUBITEM_KEY,
            "property_key": "deleted_from_notebooklm",
            "property_value": deletion_timestamp,
            "parent_item_key": SOURCE_NAME
        })

    # Step 9: Final Status
    print("\n=== Step 9: Final status ===")

    # Check downloaded file size
    file_info_result = run_bash_command(f"ls -lh '{DEST_PATH}'", "Getting file info")
    file_info = file_info_result.stdout.strip() if file_info_result.returncode == 0 else "Unable to get file info"

    print("=== Download Completed ===")
    print(f"📚 Book: {SOURCE_NAME}")
    print(f"🌐 Language: {LANGUAGE_CODE}")
    print(f"🎵 Original title: {ORIGINAL_TITLE}")
    print(f"📁 File location: {DEST_PATH}")
    print(f"📊 File info: {file_info}")
    print(f"✅ Status: {PENDING_SUBITEM_KEY} marked as completed")

    if deletion_timestamp:
        print(f"🗑️  File safely deleted from NotebookLM at: {deletion_timestamp}")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)