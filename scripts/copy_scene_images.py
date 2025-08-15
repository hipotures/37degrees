#!/usr/bin/env python3
"""
Script to copy scene PNG files to books/*/images/ directories with renamed format.
Converts scene_NN.png to scene_00NN.png while preserving letter versions (a, b, c, etc.).

Examples:
- 0012_harry_potter_scene_15.png -> scene_0015.png
- 0012_harry_potter_scene_15_c.png -> scene_0015_c.png
- 0027_scene_01b.png -> scene_0001b.png

Usage: python scripts/copy_scene_images.py [--dry-run]
"""

import os
import re
import argparse
import glob
import shutil
from pathlib import Path

def find_scene_png_files():
    """Find all scene PNG files that need copying and renaming"""
    pattern = "books/*/generated/**/*.png"
    all_files = glob.glob(pattern, recursive=True)
    
    # Filter for scene files with 2-digit numbers
    scene_files = []
    for file in all_files:
        filename = os.path.basename(file)
        # Match various scene formats: scene_NN, scene_NN_x, scene_NNx
        if re.search(r'scene_\d{2}(?:[a-z]|_[a-z])?\.png$', filename):
            scene_files.append(file)
    
    return sorted(scene_files)

def get_book_folder(file_path):
    """Extract book folder from file path"""
    parts = file_path.split('/')
    for part in parts:
        if re.match(r'^\d{4}_', part):
            return part
    return None

def get_new_filename(old_path):
    """Generate new filename with 4-digit scene number"""
    filename = os.path.basename(old_path)
    
    # Extract scene number and optional version
    # Patterns: scene_15.png, scene_15_c.png, scene_15c.png
    match = re.search(r'scene_(\d{2})([a-z]|_[a-z])?\.png$', filename)
    if match:
        scene_num = match.group(1)
        version_suffix = match.group(2) or ""
        
        # Convert to 4-digit format
        new_filename = f"scene_{scene_num.zfill(4)}{version_suffix}.png"
        return new_filename
    
    return None

def copy_and_rename_files(dry_run=True):
    """Copy scene files to images/ folders with new naming"""
    scene_files = find_scene_png_files()
    
    print(f"Found {len(scene_files)} scene PNG files to process")
    print("=" * 80)
    
    copied_count = 0
    errors = []
    
    for old_path in scene_files:
        book_folder = get_book_folder(old_path)
        if not book_folder:
            errors.append(f"Could not determine book folder for: {old_path}")
            continue
            
        new_filename = get_new_filename(old_path)
        if not new_filename:
            errors.append(f"Could not generate new filename for: {old_path}")
            continue
        
        # Create target directory and file path
        target_dir = f"books/{book_folder}/images"
        target_path = os.path.join(target_dir, new_filename)
        
        if dry_run:
            print(f"WOULD COPY: {old_path}")
            print(f"        TO: {target_path}")
            print()
        else:
            try:
                # Create target directory if it doesn't exist
                os.makedirs(target_dir, exist_ok=True)
                
                # Copy file
                shutil.copy2(old_path, target_path)
                print(f"COPIED: {old_path}")
                print(f"    TO: {target_path}")
                print()
                copied_count += 1
                
            except (OSError, shutil.Error) as e:
                errors.append(f"Error copying {old_path}: {e}")
    
    print("=" * 80)
    if dry_run:
        print(f"DRY RUN COMPLETE: {len(scene_files)} files would be copied")
    else:
        print(f"COPY COMPLETE: {copied_count} files copied successfully")
    
    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    
    return copied_count, errors

def show_book_summary(dry_run=True):
    """Show summary of what images/ folders would be created/populated"""
    scene_files = find_scene_png_files()
    book_counts = {}
    
    for file_path in scene_files:
        book_folder = get_book_folder(file_path)
        if book_folder:
            book_counts[book_folder] = book_counts.get(book_folder, 0) + 1
    
    print(f"\nSUMMARY: {len(book_counts)} book folders will get images/ directories:")
    print("-" * 60)
    for book, count in sorted(book_counts.items()):
        status = "WOULD CREATE" if dry_run else "CREATED"
        print(f"{status}: books/{book}/images/ ({count} files)")

def main():
    parser = argparse.ArgumentParser(description="Copy scene PNG files to images/ folders with 4-digit naming")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Show what would be copied without actually copying (default)")
    parser.add_argument("--execute", action="store_true", 
                        help="Actually perform the copy operation")
    
    args = parser.parse_args()
    
    # Default to dry-run unless --execute is specified
    dry_run = not args.execute
    
    if dry_run:
        print("DRY RUN MODE - No files will be copied")
        print("Use --execute flag to actually copy files")
        print()
    else:
        print("EXECUTE MODE - Files will be copied")
        confirm = input("Are you sure you want to proceed? (y/N): ")
        if confirm.lower() != 'y':
            print("Operation cancelled")
            return
        print()
    
    copied_count, errors = copy_and_rename_files(dry_run)
    show_book_summary(dry_run)
    
    if not dry_run and copied_count > 0:
        print("\nImages copied to books/*/images/ folders with new naming!")
        print("Original files remain in generated/ folders unchanged.")

if __name__ == "__main__":
    main()