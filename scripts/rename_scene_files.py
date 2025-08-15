#!/usr/bin/env python3
"""
Script to rename scene files from scene_NN.yaml to scene_NNNN.yaml format
across all books in the 37degrees project.

Usage: python scripts/rename_scene_files.py [--dry-run]
"""

import os
import re
import argparse
import glob
from pathlib import Path

def find_scene_files():
    """Find all scene YAML files that need renaming"""
    pattern = "books/*/prompts/**/*.yaml"
    all_files = glob.glob(pattern, recursive=True)
    
    # Filter for scene files with 2-digit numbers
    scene_files = []
    for file in all_files:
        filename = os.path.basename(file)
        if re.match(r'^scene_\d{2}\.yaml$', filename):
            scene_files.append(file)
    
    return sorted(scene_files)

def get_new_filename(old_path):
    """Generate new filename with 4-digit scene number"""
    directory = os.path.dirname(old_path)
    filename = os.path.basename(old_path)
    
    # Extract the 2-digit number
    match = re.match(r'^scene_(\d{2})\.yaml$', filename)
    if match:
        scene_num = match.group(1)
        # Convert to 4-digit format
        new_filename = f"scene_{scene_num.zfill(4)}.yaml"
        new_path = os.path.join(directory, new_filename)
        return new_path
    
    return None

def rename_files(dry_run=True):
    """Rename all scene files from NN to NNNN format"""
    scene_files = find_scene_files()
    
    print(f"Found {len(scene_files)} scene files to rename")
    print("=" * 60)
    
    renamed_count = 0
    errors = []
    
    for old_path in scene_files:
        new_path = get_new_filename(old_path)
        
        if new_path is None:
            errors.append(f"Could not generate new name for: {old_path}")
            continue
            
        if os.path.exists(new_path):
            errors.append(f"Target file already exists: {new_path}")
            continue
        
        if dry_run:
            print(f"WOULD RENAME: {old_path} -> {new_path}")
        else:
            try:
                os.rename(old_path, new_path)
                print(f"RENAMED: {old_path} -> {new_path}")
                renamed_count += 1
            except OSError as e:
                errors.append(f"Error renaming {old_path}: {e}")
    
    print("=" * 60)
    if dry_run:
        print(f"DRY RUN COMPLETE: {len(scene_files)} files would be renamed")
    else:
        print(f"RENAME COMPLETE: {renamed_count} files renamed successfully")
    
    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    
    return renamed_count, errors

def main():
    parser = argparse.ArgumentParser(description="Rename scene files from NN to NNNN format")
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
    
    renamed_count, errors = rename_files(dry_run)
    
    if not dry_run and renamed_count > 0:
        print("\nRemember to commit these changes to git if they look correct!")

if __name__ == "__main__":
    main()