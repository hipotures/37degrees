#!/bin/bash

set -e  # Exit on error

BOOK_FOLDER="${1:-}"
SCENE_SET="${2:-}"
STYLE_NAME="${3:-}"

# Validation
if [[ -z "$BOOK_FOLDER" || -z "$SCENE_SET" || -z "$STYLE_NAME" ]]; then
    echo "Usage: $0 <book_folder> <scene_set> <style_name>"
    echo "Example: $0 0039_odyssey world-building-focus-generator fresco-painting-style"
    exit 1
fi

# Check if directories exist
SCENES_DIR="books/${BOOK_FOLDER}/prompts/scenes/${SCENE_SET}/"
OUTPUT_DIR="books/${BOOK_FOLDER}/prompts/genimage/"

if [[ ! -d "$SCENES_DIR" ]]; then
    echo "Error: Scenes directory not found: $SCENES_DIR"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "Merging scenes with style..."
echo "Book: $BOOK_FOLDER"
echo "Scene set: $SCENE_SET"
echo "Style: $STYLE_NAME"

# Execute merge script for all scenes
python3 scripts/merge-scenes-with-style.py \
    "$SCENES_DIR" \
    "$OUTPUT_DIR" \
    "$STYLE_NAME" \
    "technical-specifications"

echo "✅ Merge completed successfully"