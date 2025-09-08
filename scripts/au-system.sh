#!/bin/bash

# Script to create cc-au-notebooklm list structure from books/ directory
# Creates "Audio for" items with audio_gen/audio_dwn/afa_gen subitems

# set -e removed to allow continuing on errors

TARGET_LIST="cc-au-notebooklm"

echo "Creating list structure in $TARGET_LIST from books/ directory..."

# Counter for statistics
count=0

# Process each directory in books/ (excluding symlinks)
for book_dir in books/*/; do
    # Skip if not a directory or if it's a symlink
    if [[ ! -d "$book_dir" ]] || [[ -L "${book_dir%/}" ]]; then
        continue
    fi
    
    # Extract book key from directory name (e.g., 0001_alice_in_wonderland)
    book_key=$(basename "$book_dir")
    
    # Skip if doesn't match expected pattern (NNNN_name)
    if [[ ! "$book_key" =~ ^[0-9]{4}_ ]]; then
        echo "Skipping invalid directory: $book_key"
        continue
    fi
    
    # Check if book.yaml exists
    book_yaml="${book_dir}book.yaml"
    if [[ ! -f "$book_yaml" ]]; then
        echo "Warning: No book.yaml found for $book_key, skipping..."
        continue
    fi
    
    # Extract title and author from book.yaml
    title=$(grep -A1 "title:" "$book_yaml" | grep -v "title_pl:" | head -1 | sed 's/.*title: *"\?\([^"]*\)"\?.*/\1/')
    author=$(grep "author:" "$book_yaml" | head -1 | sed 's/.*author: *"\?\([^"]*\)"\?.*/\1/')
    
    # Create item title
    item_title="Audio for $title by $author"
    
    echo "Adding item: $book_key - $item_title"
    
    # Add main item with pending status
    todoit item add --list "$TARGET_LIST" --item "$book_key" --title "$item_title" > /dev/null 2>&1 || {
        echo "  Item $book_key already exists, skipping..."
        continue
    }
    
    # Add audio_gen subitem
    echo "  Adding audio_gen subitem..."
    todoit item add --list "$TARGET_LIST" --item "$book_key" --subitem "audio_gen" --title "Audio generation" > /dev/null 2>&1 || true
    
    # Add audio_dwn subitem  
    echo "  Adding audio_dwn subitem..."
    todoit item add --list "$TARGET_LIST" --item "$book_key" --subitem "audio_dwn" --title "Audio download" > /dev/null 2>&1 || true
    
    # Add afa_gen subitem
    echo "  Adding afa_gen subitem..."
    todoit item add --list "$TARGET_LIST" --item "$book_key" --subitem "afa_gen" --title "Audio format analysis generation" > /dev/null 2>&1 || true
    
    echo "  Completed: $book_key"
    ((count++))
done

echo "List structure created successfully!"
echo "Total items processed: $count"