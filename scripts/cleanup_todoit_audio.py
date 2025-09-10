#!/usr/bin/env python3
"""
Cleanup script for TODOIT audio structure
1. Copy status from audio_gen to audio_gen_pl
2. Delete old audio_gen (keep audio_dwn as it wasn't processed)
"""

import subprocess
import sys

TARGET_LIST = "cc-au-notebooklm"

def run_todoit_cmd(args):
    """Run todoit command and return output"""
    cmd = ["todoit"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.stdout, result.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return "", 1

def get_list_items():
    """Get all main items from books/ directory"""
    import os
    import glob
    
    items = []
    # Get all book directories, NO SYMLINKS
    for book_dir in glob.glob("books/[0-9][0-9][0-9][0-9]_*/"):
        if not os.path.islink(book_dir.rstrip('/')):  # Skip symlinks
            book_key = os.path.basename(book_dir.rstrip('/'))
            items.append(book_key)
    
    return sorted(items)  # Return sorted list

def get_subitem_status(book_key, subitem_key):
    """Get status of a specific subitem"""
    # Use list show which gives us the formatted output
    output, _ = run_todoit_cmd(["list", "show", "--list", TARGET_LIST])
    
    # Find the book section and then look for the subitem
    in_book = False
    for line in output.split('\n'):
        # Check if we're in the right book section
        if book_key in line:
            in_book = True
        elif in_book and '│' in line:
            # Look for exact subitem match (with spaces to avoid partial matches)
            if f"   {subitem_key} " in line or f"│ {subitem_key} " in line:
                if "✅" in line:
                    return "completed"
                elif "⏳" in line:
                    return "pending"
                elif "🔄" in line:
                    return "in_progress"
                elif "❌" in line:
                    return "failed"
            # Stop when we reach next book (new numbered item without dot)
            elif line.strip() and line.split()[0].replace('│', '').strip().isdigit():
                break
    
    return None

def update_subitem_status(book_key, subitem_key, status):
    """Update status of a subitem"""
    print(f"    Setting {subitem_key} to {status}")
    output, returncode = run_todoit_cmd([
        "item", "status", "--list", TARGET_LIST,
        "--item", book_key, "--subitem", subitem_key,
        "--status", status
    ])
    
    if returncode == 0:
        print(f"      ✓ Updated {subitem_key} status to {status}")
    else:
        print(f"      ❌ Error updating {subitem_key}")

def delete_subitem(book_key, subitem_key):
    """Delete a subitem"""
    print(f"    Deleting old {subitem_key}")
    output, returncode = run_todoit_cmd([
        "item", "delete", "--list", TARGET_LIST,
        "--item", book_key, "--subitem", subitem_key,
        "--force"
    ])
    
    if returncode == 0:
        print(f"      ✓ Deleted {subitem_key}")
    else:
        print(f"      ❌ Error deleting {subitem_key}")

def cleanup_book(book_key):
    """Cleanup audio structure for a single book - just delete old subitems"""
    print(f"\n📚 Processing: {book_key}")
    
    deleted_count = 0
    
    # Try to delete old audio_gen
    print(f"  🗑️  Attempting to delete audio_gen...")
    output, returncode = run_todoit_cmd([
        "item", "delete", "--list", TARGET_LIST,
        "--item", book_key, "--subitem", "audio_gen", "--force"
    ])
    if returncode == 0:
        print(f"      ✓ Deleted audio_gen")
        deleted_count += 1
    else:
        print(f"      - audio_gen not found or already deleted")
    
    # Try to delete old audio_dwn
    print(f"  🗑️  Attempting to delete audio_dwn...")
    output, returncode = run_todoit_cmd([
        "item", "delete", "--list", TARGET_LIST,
        "--item", book_key, "--subitem", "audio_dwn", "--force"
    ])
    if returncode == 0:
        print(f"      ✓ Deleted audio_dwn")
        deleted_count += 1
    else:
        print(f"      - audio_dwn not found or already deleted")
    
    if deleted_count > 0:
        print(f"  ✅ Cleanup completed - deleted {deleted_count} old subitems")
        return "cleaned"
    else:
        print(f"  ⏭️  Nothing to clean")
        return "skipped"

def main():
    print("=========================================")
    print("TODOIT Audio Structure Cleanup")
    print("=========================================")
    print("")
    print(f"Target list: {TARGET_LIST}")
    print("Action: Delete old audio_gen and audio_dwn subitems")
    print("Note: Keeping all language-specific subitems (audio_gen_XX, audio_dwn_XX)")
    print("")
    
    # Check if list exists
    output, returncode = run_todoit_cmd(["list", "show", "--list", TARGET_LIST])
    if returncode != 0 or "not found" in output.lower():
        print(f"❌ Error: List '{TARGET_LIST}' not found!")
        sys.exit(1)
    
    print("📋 Fetching all items from the list...")
    print("")
    
    items = get_list_items()
    
    if not items:
        print("⚠️  No items found in list")
        sys.exit(0)
    
    print(f"Found {len(items)} books to process")
    
    # Statistics
    total = len(items)
    cleaned = 0
    skipped = 0
    errors = 0
    
    # Process each book
    for book_key in items:
        try:
            result = cleanup_book(book_key)
            if result == "cleaned":
                cleaned += 1
            elif result == "skipped":
                skipped += 1
            elif result == "error":
                errors += 1
        except Exception as e:
            print(f"  ❌ Error processing {book_key}: {e}")
            errors += 1
    
    print("")
    print("=========================================")
    print("📊 Cleanup Summary")
    print("=========================================")
    print(f"Total items processed: {total}")
    print(f"Successfully cleaned: {cleaned}")
    print(f"Skipped (no old audio_gen): {skipped}")
    print(f"Errors: {errors}")
    print("")
    print("✅ Cleanup completed!")
    print("")
    print("💡 Next step:")
    print(f"Verify the structure: todoit list show --list {TARGET_LIST}")
    print("")

if __name__ == "__main__":
    main()