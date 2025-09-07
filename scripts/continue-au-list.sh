#!/bin/bash

# Script to continue copying remaining items from cc-au-research to cc-au-notebooklm
# Continues from item 0101 onwards

set -e

SOURCE_LIST="cc-au-research"
TARGET_LIST="cc-au-notebooklm"
START_FROM="0101"

echo "Continuing list copy from item $START_FROM..."

# Get source list items with JSON output format, filter from 0101 onwards
export TODOIT_OUTPUT_FORMAT=json
source_json=$(todoit item list --list "$SOURCE_LIST")

# Parse JSON and extract items starting from 0101
echo "$source_json" | jq -r '.data[] | select(.Key >= "0101" and (.Key | startswith("0"))) | @base64' | while IFS= read -r item; do
    # Decode and extract item data
    item_data=$(echo "$item" | base64 -d)
    item_key=$(echo "$item_data" | jq -r '.Key')
    original_title=$(echo "$item_data" | jq -r '.Title')
    
    # Skip if no valid data
    if [[ -z "$item_key" || -z "$original_title" ]]; then
        continue
    fi
    
    # Replace "Research for" with "Audio for"
    new_title=$(echo "$original_title" | sed 's/Research for/Audio for/')
    
    echo "Adding item: $item_key - $new_title"
    
    # Add main item with pending status
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

echo "Continuation completed!"