#!/bin/bash

# Script: 37d-a2-01.sh
# Purpose: Mark all scene_style subtasks as completed in TODOIT system
# Usage: ./37d-a2-01.sh BOOK_FOLDER
# Example: ./37d-a2-01.sh 0038_iliad

if [ $# -ne 1 ]; then
    echo "❌ Wywołanie niepoprawne - nie wykonano żadnej modyfikacji statusów"
    echo "Należy podać BOOK_FOLDER"
    echo "Przykład: $0 0038_iliad"
    exit 1
fi

BOOK_FOLDER="$1"

echo "Marking scene_style subtasks as completed for book: $BOOK_FOLDER"

for i in $(printf "%04d " {1..25}); do
    scene_key="scene_$i"
    todoit item status --list "$BOOK_FOLDER" --item "$scene_key" --subitem "scene_style" --status completed
done

echo "✅ All 25 scene_style subtasks marked as completed for $BOOK_FOLDER"