#!/usr/bin/env python3
"""Update collection file paths to match new numbered directory structure"""

import yaml
from pathlib import Path

def update_collection_paths(collection_file: str):
    """Update paths in collection file to match new directory structure"""
    
    # Load collection
    with open(collection_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Update book paths
    books = data.get('books', [])
    updated = 0
    
    for book in books:
        old_path = book['path']
        
        # Extract book name from old path
        # Example: books/little_prince/book.yaml -> little_prince
        parts = old_path.split('/')
        if len(parts) >= 3:
            book_name = parts[1]
            
            # Find matching numbered directory
            books_dir = Path('books')
            for dir_path in books_dir.iterdir():
                if dir_path.is_dir() and book_name in dir_path.name.lower():
                    new_path = f"books/{dir_path.name}/book.yaml"
                    if Path(new_path).exists():
                        book['path'] = new_path
                        updated += 1
                        print(f"Updated: {old_path} -> {new_path}")
                        break
    
    # Save updated collection
    with open(collection_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    
    print(f"\nTotal paths updated: {updated}")

if __name__ == "__main__":
    update_collection_paths("collections/classics.yaml")