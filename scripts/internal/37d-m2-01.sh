#!/bin/bash

# Script: 37d-m2-01.sh
# Purpose: Mark all scene_style subtasks as completed in TODOIT system for MEDIA
# Usage: ./37d-m2-01.sh MEDIA_FOLDER
# Example: ./37d-m2-01.sh m00008_roswell_incident_1947

if [ $# -ne 1 ]; then
    echo "❌ Wywołanie niepoprawne - nie wykonano żadnej modyfikacji statusów"
    echo "Należy podać MEDIA_FOLDER"
    echo "Przykład: $0 m00008_roswell_incident_1947"
    exit 1
fi

MEDIA_FOLDER="$1"

# Get scene_count from media.yaml
SCENE_COUNT=$(grep "scene_count:" "media/$MEDIA_FOLDER/media.yaml" | awk '{print $2}')

if [ -z "$SCENE_COUNT" ]; then
    echo "❌ Cannot find scene_count in media/$MEDIA_FOLDER/media.yaml"
    exit 1
fi

echo "Marking scene_style subtasks as completed for media: $MEDIA_FOLDER (${SCENE_COUNT} scenes)"

for ((i=1; i<=SCENE_COUNT; i++)); do
    scene_key=$(printf "scene_%04d" $i)
    todoit item status --list "$MEDIA_FOLDER" --item "$scene_key" --subitem "scene_style" --status completed
done

echo "✅ All $SCENE_COUNT scene_style subtasks marked as completed for $MEDIA_FOLDER"