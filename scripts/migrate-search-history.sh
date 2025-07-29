#!/bin/bash

# One-time script to migrate search history from agent folders to search_history/
# Usage: ./scripts/migrate-search-history.sh

set -e

echo "Migrating search history for all books..."

for book_dir in books/0*; do
    if [ -d "$book_dir" ]; then
        book_name=$(basename "$book_dir")
        echo "Processing $book_name..."
        
        search_history_dir="$book_dir/search_history"
        docs_dir="$book_dir/docs"
        
        # Skip if search_history doesn't exist
        if [ ! -d "$search_history_dir" ]; then
            echo "  Skipping - no search_history folder"
            continue
        fi
        
        
        # Initialize combined index file
        combined_index="$search_history_dir/searches_index.txt"
        > "$combined_index"  # Start fresh
        
        # Process each agent folder
        for agent_folder in "$docs_dir"/37d-*; do
            if [ -d "$agent_folder" ]; then
                agent_name=$(basename "$agent_folder")
                echo "  Processing $agent_name..."
                
                # Move all JSON files
                json_count=0
                for json_file in "$agent_folder"/*.json; do
                    if [ -f "$json_file" ]; then
                        echo "    DEBUG: Copying $json_file to $search_history_dir/"
                        cp "$json_file" "$search_history_dir/" || echo "    ERROR: Failed to copy $json_file"
                        json_count=$((json_count + 1))
                    fi
                done
                
                # Append index file content if it exists
                index_file="$agent_folder/${agent_name}_searches_index.txt"
                if [ -f "$index_file" ]; then
                    cat "$index_file" >> "$combined_index"
                fi
                
                echo "    Moved $json_count JSON files"
                
                # Remove empty agent folder
                if [ -d "$agent_folder" ] && [ -z "$(ls -A "$agent_folder")" ]; then
                    rmdir "$agent_folder"
                    echo "    Removed empty folder $agent_name"
                fi
            fi
        done
        
        # Count total files in search_history
        json_total=$(find "$search_history_dir" -name "*.json" | wc -l)
        echo "  ✅ Total: $json_total JSON files in search_history/"
    fi
done

echo ""
echo "✅ Migration completed for all books"
echo "All JSON files moved to search_history/ folders"
echo "All index files combined into searches_index.txt"