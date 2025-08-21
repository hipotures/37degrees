#!/usr/bin/env python3
"""
Script to validate gemini_book_styles.csv against actual book folders and available styles
"""

import csv
import os
from pathlib import Path

def main():
    # Load the CSV file
    csv_file = "gemini_book_styles.csv"
    books_dir = Path("books")
    styles_dir = Path("config/prompt/graphics-styles")
    
    # Check if files exist
    if not Path(csv_file).exists():
        print(f"❌ {csv_file} not found")
        return
    
    if not books_dir.exists():
        print(f"❌ {books_dir} directory not found")
        return
        
    if not styles_dir.exists():
        print(f"❌ {styles_dir} directory not found")
        return
    
    # Get actual book folders
    actual_books = set()
    for folder in sorted(books_dir.iterdir()):
        if folder.is_dir() and folder.name.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
            actual_books.add(folder.name)
    
    # Get available styles
    available_styles = set()
    for style_file in styles_dir.glob("*.yaml"):
        available_styles.add(style_file.name)
    
    print(f"📊 Found {len(actual_books)} book folders")
    print(f"📊 Found {len(available_styles)} available styles")
    
    # Read CSV and validate
    csv_books = set()
    csv_styles = set()
    issues = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, 2):  # Start from 2 (header is row 1)
            folder = row.get('folder', '').strip()
            style = row.get('style', '').strip()
            
            if not folder or not style:
                issues.append(f"Row {row_num}: Empty folder or style")
                continue
                
            csv_books.add(folder)
            csv_styles.add(style)
            
            # Check if book folder exists
            if folder not in actual_books:
                issues.append(f"Row {row_num}: Book folder '{folder}' not found")
            
            # Check if style exists
            if style not in available_styles:
                issues.append(f"Row {row_num}: Style '{style}' not found")
    
    print(f"📊 CSV contains {len(csv_books)} book entries")
    print(f"📊 CSV references {len(csv_styles)} different styles")
    
    # Find missing books
    missing_books = actual_books - csv_books
    if missing_books:
        print(f"\n⚠️  Books missing from CSV ({len(missing_books)}):")
        for book in sorted(missing_books)[:10]:  # Show first 10
            print(f"   - {book}")
        if len(missing_books) > 10:
            print(f"   ... and {len(missing_books) - 10} more")
    
    # Find extra books in CSV
    extra_books = csv_books - actual_books
    if extra_books:
        print(f"\n⚠️  Books in CSV but not in folders ({len(extra_books)}):")
        for book in sorted(extra_books)[:10]:
            print(f"   - {book}")
        if len(extra_books) > 10:
            print(f"   ... and {len(extra_books) - 10} more")
    
    # Find missing styles
    missing_styles = csv_styles - available_styles
    if missing_styles:
        print(f"\n❌ Styles referenced but not found ({len(missing_styles)}):")
        for style in sorted(missing_styles):
            print(f"   - {style}")
    
    # Show validation issues
    if issues:
        print(f"\n❌ Validation issues ({len(issues)}):")
        for issue in issues[:10]:  # Show first 10
            print(f"   - {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more")
    
    # Summary
    if not issues and not missing_books and not extra_books and not missing_styles:
        print(f"\n✅ All validations passed!")
        print(f"   - All {len(csv_books)} books have corresponding folders")
        print(f"   - All {len(csv_styles)} styles exist")
        print(f"   - No missing or extra entries")
    else:
        print(f"\n📊 Validation Summary:")
        print(f"   - Missing books: {len(missing_books)}")
        print(f"   - Extra books: {len(extra_books)}")
        print(f"   - Missing styles: {len(missing_styles)}")
        print(f"   - Other issues: {len(issues)}")

if __name__ == "__main__":
    main()