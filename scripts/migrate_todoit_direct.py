#!/usr/bin/env python3
"""
Direct migration script for TODOIT multilingual structure
Migrates from 3 subitems (afa_gen, audio_gen, audio_dwn) 
to 19 subitems (1 afa_gen + 9 audio_gen_XX + 9 audio_dwn_XX)
"""

import subprocess
import json
import sys

TARGET_LIST = "cc-au-notebooklm"

# Language configuration
LANGUAGES = ["pl", "en", "es", "pt", "hi", "ja", "ko", "de", "fr"]
LANGUAGE_NAMES = {
    "pl": "Polish",
    "en": "English", 
    "es": "Spanish",
    "pt": "Portuguese",
    "hi": "Hindi",
    "ja": "Japanese",
    "ko": "Korean",
    "de": "German",
    "fr": "French"
}

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
    """Get all main items from the list"""
    output, _ = run_todoit_cmd(["item", "list", "--list", TARGET_LIST])
    
    items = []
    for line in output.split('\n'):
        if '│' in line:
            parts = line.split('│')
            if len(parts) >= 3:
                item_key = parts[2].strip().split()[0] if parts[2].strip() else ""
                # Only get main items (NNNN_bookname format)
                if item_key and item_key[:4].isdigit() and '_' in item_key:
                    items.append(item_key)
    
    return list(set(items))  # Remove duplicates

def check_item_structure(book_key):
    """Check current structure of an item"""
    output, _ = run_todoit_cmd(["item", "show", "--list", TARGET_LIST, "--item", book_key])
    
    has_old_audio_gen = "audio_gen" in output and "audio_gen_" not in output
    has_old_audio_dwn = "audio_dwn" in output and "audio_dwn_" not in output
    has_new_structure = "audio_gen_pl" in output
    
    return has_old_audio_gen, has_old_audio_dwn, has_new_structure

def delete_old_subitem(book_key, subitem_key):
    """Delete old subitem"""
    print(f"  🗑️  Removing old {subitem_key}...")
    run_todoit_cmd(["item", "delete", "--list", TARGET_LIST, 
                    "--item", book_key, "--subitem", subitem_key, "--force"])

def add_language_subitem(book_key, lang, task_type):
    """Add language-specific subitem"""
    lang_name = LANGUAGE_NAMES[lang]
    subitem_key = f"{task_type}_{lang}"
    
    if task_type == "audio_gen":
        title = f"Audio generation - {lang_name}"
    else:  # audio_dwn
        title = f"Audio download - {lang_name}"
    
    output, returncode = run_todoit_cmd([
        "item", "add", "--list", TARGET_LIST,
        "--item", book_key, "--subitem", subitem_key,
        "--title", title
    ])
    
    if returncode == 0:
        print(f"      ✓ Added {subitem_key}")
    else:
        if "already exists" in output.lower():
            print(f"      ⏭️  {subitem_key} already exists")
        else:
            print(f"      ❌ Error adding {subitem_key}")

def migrate_book(book_key):
    """Migrate a single book to multilingual structure"""
    print(f"\n📚 Processing book: {book_key}")
    
    # Check current structure
    has_old_gen, has_old_dwn, has_new = check_item_structure(book_key)
    
    if has_new:
        print(f"  ✅ Already migrated - skipping")
        return "skipped"
    
    if has_old_gen or has_old_dwn:
        print(f"  🔄 Migrating to multilingual structure...")
        
        # Remove old subitems
        if has_old_gen:
            delete_old_subitem(book_key, "audio_gen")
        if has_old_dwn:
            delete_old_subitem(book_key, "audio_dwn")
        
        # Add new multilingual subitems
        print(f"  ➕ Adding multilingual subitems...")
        
        for lang in LANGUAGES:
            # Add audio_gen_XX
            print(f"    • Adding audio_gen_{lang} ({LANGUAGE_NAMES[lang]} generation)...")
            add_language_subitem(book_key, lang, "audio_gen")
            
            # Add audio_dwn_XX  
            print(f"    • Adding audio_dwn_{lang} ({LANGUAGE_NAMES[lang]} download)...")
            add_language_subitem(book_key, lang, "audio_dwn")
        
        print(f"  ✅ Migration completed for {book_key}")
        return "migrated"
    else:
        print(f"  ℹ️  No old structure found - adding multilingual subitems...")
        
        for lang in LANGUAGES:
            add_language_subitem(book_key, lang, "audio_gen")
            add_language_subitem(book_key, lang, "audio_dwn")
        
        print(f"  ✅ Added multilingual structure for {book_key}")
        return "migrated"

def main():
    print("=========================================")
    print("TODOIT Multilingual Migration Script")
    print("=========================================")
    print("")
    print(f"Target list: {TARGET_LIST}")
    print(f"Languages to add: {' '.join(LANGUAGES)}")
    print("")
    
    # Check if list exists
    output, returncode = run_todoit_cmd(["list", "show", "--list", TARGET_LIST])
    if returncode != 0 or "not found" in output.lower():
        print(f"❌ Error: List '{TARGET_LIST}' not found!")
        print("Please ensure the list exists before running migration.")
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
    migrated = 0
    skipped = 0
    errors = 0
    
    # Process each book
    for book_key in items:
        try:
            result = migrate_book(book_key)
            if result == "migrated":
                migrated += 1
            elif result == "skipped":
                skipped += 1
        except Exception as e:
            print(f"  ❌ Error processing {book_key}: {e}")
            errors += 1
    
    print("")
    print("=========================================")
    print("📊 Migration Summary")
    print("=========================================")
    print(f"Total items processed: {total}")
    print(f"Successfully migrated: {migrated}")
    print(f"Already migrated (skipped): {skipped}")
    print(f"Errors: {errors}")
    print("")
    print("✅ Migration completed!")
    print("")
    print("💡 Next steps:")
    print(f"1. Verify the structure: todoit list show --list {TARGET_LIST}")
    print("2. Test the AFA agent with new structure")
    print("3. Test the notebook-audio agent for language selection")
    print("")

if __name__ == "__main__":
    main()