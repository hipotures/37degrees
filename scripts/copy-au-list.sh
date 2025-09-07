#!/bin/bash

# Script to copy cc-au-research list structure to cc-au-notebooklm
# Changes "Research for" to "Audio for" and adds audio_gen/audio_dwn subitems

set -e

SOURCE_LIST="cc-au-research"
TARGET_LIST="cc-au-notebooklm"

echo "Copying list structure from $SOURCE_LIST to $TARGET_LIST..."

# Get source list items with JSON output format
echo "Reading source list items..."
export TODOIT_OUTPUT_FORMAT=json
source_json=$(todoit item list --list "$SOURCE_LIST")

# Parse JSON and extract items
echo "$source_json" | jq -r '.data[] | @base64' | while IFS= read -r item; do
    # Decode and extract item data
    item_data=$(echo "$item" | base64 -d)
    item_key=$(echo "$item_data" | jq -r '.Key')
    original_title=$(echo "$item_data" | jq -r '.Title')
    
    # Skip if no valid data
    if [[ -z "$item_key" || -z "$original_title" ]]; then
        echo "Skipping invalid item data"
        continue
    fi
    
    # Replace "Research for" with "Audio for"
    new_title=$(echo "$original_title" | sed 's/Research for/Audio for/')
    
    echo "Adding item: $item_key - $new_title"
    
    # Add main item with pending status (no JSON output for add operations)
    unset TODOIT_OUTPUT_FORMAT
    todoit item add --list "$TARGET_LIST" --item "$item_key" --title "$new_title" > /dev/null
    
    # Add audio_gen subitem
    echo "  Adding audio_gen subitem..."
    todoit item add --list "$TARGET_LIST" --item "$item_key" --subitem "audio_gen" --title "Audio generation" > /dev/null
    
    # Add audio_dwn subitem  
    echo "  Adding audio_dwn subitem..."
    todoit item add --list "$TARGET_LIST" --item "$item_key" --subitem "audio_dwn" --title "Audio download" > /dev/null
    
    echo "  Completed: $item_key"
done

echo "List structure copied successfully!"
echo "Total items copied with subitems added."