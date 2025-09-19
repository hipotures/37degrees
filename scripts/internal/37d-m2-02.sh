#!/bin/bash

set -e  # Exit on error

MEDIA_FOLDER="${1:-}"

# Validation
if [[ -z "$MEDIA_FOLDER" ]]; then
    echo "Usage: $0 <media_folder>"
    echo "Example: $0 m00008_roswell_incident_1947"
    echo "All other parameters are read from media/[MEDIA_FOLDER]/media.yaml"
    exit 1
fi

# Read parameters from media.yaml
MEDIA_YAML="media/${MEDIA_FOLDER}/media.yaml"
if [[ ! -f "$MEDIA_YAML" ]]; then
    echo "Error: Media configuration not found: $MEDIA_YAML"
    exit 1
fi

# Extract parameters from YAML
SCENE_GENERATOR=$(grep "scene_generator:" "$MEDIA_YAML" | awk '{print $2}')
STYLE_NAME=$(grep "graphics_style:" "$MEDIA_YAML" | awk '{print $2}')

if [[ -z "$SCENE_GENERATOR" ]]; then
    echo "Error: Cannot find scene_generator in $MEDIA_YAML"
    exit 1
fi

if [[ -z "$STYLE_NAME" ]]; then
    echo "Error: Cannot find graphics_style in $MEDIA_YAML"
    exit 1
fi

# Check if directories exist
SCENES_DIR="media/${MEDIA_FOLDER}/prompts/scenes/${SCENE_GENERATOR}/"
OUTPUT_DIR="media/${MEDIA_FOLDER}/prompts/genimage/"

if [[ ! -d "$SCENES_DIR" ]]; then
    echo "Error: Scenes directory not found: $SCENES_DIR"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "Merging scenes with style..."
echo "Media: $MEDIA_FOLDER"
echo "Scene generator: $SCENE_GENERATOR"
echo "Style: $STYLE_NAME"

# Execute merge script for all scenes
python3 scripts/merge-scenes-with-style.py \
    "$SCENES_DIR" \
    "$OUTPUT_DIR" \
    "$STYLE_NAME" \
    "technical-specifications"

echo "✅ Merge completed successfully"