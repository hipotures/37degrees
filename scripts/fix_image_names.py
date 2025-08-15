#!/usr/bin/env python3
"""
Script to fix image names in books/*/images/ folders to include book prefix.
Changes scene_NNNN.png to NNNN_bookname_scene_NNNN.png

Usage: python scripts/fix_image_names.py [--dry-run]
"""

import os
import re
import argparse
import glob
from pathlib import Path

def find_images_folders():
    """Find all books/*/images/ folders"""
    pattern = "books/*/images"
    return sorted(glob.glob(pattern))

def get_book_info(images_folder):
    """Extract book number and name from images folder path"""
    # books/0012_harry_potter/images -> 0012, harry_potter
    book_folder = os.path.dirname(images_folder)
    book_name = os.path.basename(book_folder)
    
    match = re.match(r'^(\d{4})_(.+)$', book_name)
    if match:
        book_num = match.group(1)
        book_name_part = match.group(2)
        return book_num, book_name_part, book_name
    return None, None, None

def get_new_filename(old_filename, book_num, book_name_part):
    """Generate new filename with book prefix"""
    # scene_0015.png -> 0012_harry_potter_scene_0015.png
    # scene_0015_c.png -> 0012_harry_potter_scene_0015_c.png
    
    if old_filename.startswith('scene_'):
        new_filename = f"{book_num}_{book_name_part}_{old_filename}"
        return new_filename
    
    return None

def fix_image_names(dry_run=True):
    """Rename image files to include book prefix"""
    images_folders = find_images_folders()
    
    print(f"Found {len(images_folders)} images folders to process")
    print("=" * 80)
    
    renamed_count = 0
    errors = []
    
    for images_folder in images_folders:
        book_num, book_name_part, full_book_name = get_book_info(images_folder)
        
        if not book_num:
            errors.append(f"Could not parse book info from: {images_folder}")
            continue
        
        # Get all PNG files in this images folder
        png_files = glob.glob(os.path.join(images_folder, "*.png"))
        
        print(f"\nProcessing: {full_book_name} ({len(png_files)} files)")
        print("-" * 60)
        
        for old_path in png_files:
            old_filename = os.path.basename(old_path)
            
            # Skip files that already have the book prefix
            if old_filename.startswith(f"{book_num}_{book_name_part}_"):
                continue
            
            new_filename = get_new_filename(old_filename, book_num, book_name_part)
            if not new_filename:
                errors.append(f"Could not generate new name for: {old_path}")
                continue
            
            new_path = os.path.join(images_folder, new_filename)
            
            if os.path.exists(new_path):
                errors.append(f"Target file already exists: {new_path}")
                continue
            
            if dry_run:
                print(f"WOULD RENAME: {old_filename}")
                print(f"          TO: {new_filename}")
            else:
                try:
                    os.rename(old_path, new_path)
                    print(f"RENAMED: {old_filename}")
                    print(f"     TO: {new_filename}")
                    renamed_count += 1
                except OSError as e:
                    errors.append(f"Error renaming {old_path}: {e}")
    
    print("=" * 80)
    if dry_run:
        print(f"DRY RUN COMPLETE: Files would be renamed in {len(images_folders)} folders")
    else:
        print(f"RENAME COMPLETE: {renamed_count} files renamed successfully")
    
    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    
    return renamed_count, errors

def main():
    parser = argparse.ArgumentParser(description="Fix image names to include book prefix")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Show what would be renamed without actually renaming (default)")
    parser.add_argument("--execute", action="store_true", 
                        help="Actually perform the rename operation")
    
    args = parser.parse_args()
    
    # Default to dry-run unless --execute is specified
    dry_run = not args.execute
    
    if dry_run:
        print("DRY RUN MODE - No files will be renamed")
        print("Use --execute flag to actually rename files")
        print()
    else:
        print("EXECUTE MODE - Files will be renamed")
        confirm = input("Are you sure you want to proceed? (y/N): ")
        if confirm.lower() != 'y':
            print("Operation cancelled")
            return
        print()
    
    renamed_count, errors = fix_image_names(dry_run)
    
    if not dry_run and renamed_count > 0:
        print("\nImage names fixed to include book prefixes!")

if __name__ == "__main__":
    main()