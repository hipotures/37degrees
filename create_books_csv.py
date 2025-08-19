#!/usr/bin/env python3
"""
Script to create CSV file with book information from book.yaml files
"""

import os
import csv
import yaml
from pathlib import Path

def main():
    books_dir = Path("books")
    csv_file = "books.csv"
    
    # Check if books directory exists
    if not books_dir.exists():
        print(f"Directory {books_dir} not found")
        return
    
    books_data = []
    
    # Iterate through all book folders
    for book_folder in sorted(books_dir.iterdir()):
        if book_folder.is_dir() and book_folder.name.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
            book_yaml_path = book_folder / "book.yaml"
            
            if book_yaml_path.exists():
                try:
                    with open(book_yaml_path, 'r', encoding='utf-8') as f:
                        book_data = yaml.safe_load(f)
                    
                    # Extract book_info data
                    book_info = book_data.get('book_info', {})
                    title = book_info.get('title', 'N/A')
                    author = book_info.get('author', 'N/A')
                    
                    books_data.append({
                        'folder': book_folder.name,
                        'title': title,
                        'author': author
                    })
                    
                    print(f"Processed: {book_folder.name} - {title} by {author}")
                    
                except Exception as e:
                    print(f"Error processing {book_folder.name}: {e}")
            else:
                print(f"No book.yaml found in {book_folder.name}")
    
    # Write to CSV
    if books_data:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['folder', 'title', 'author'])
            writer.writeheader()
            writer.writerows(books_data)
        
        print(f"\nCSV file '{csv_file}' created with {len(books_data)} books")
    else:
        print("No books data found")

if __name__ == "__main__":
    main()