#!/bin/bash
# Move all .err files and their corresponding audio files to tmp/audio/

set -e

TARGET_DIR="tmp/audio"

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

echo "Moving bad audio files to $TARGET_DIR..."
echo ""

moved_count=0

# Find all .err files
while IFS= read -r err_file; do
    if [ -f "$err_file" ]; then
        # Get the base name without .err extension
        base="${err_file%.err}"

        # Find corresponding audio file (.m4a or .mp4)
        if [ -f "${base}.m4a" ]; then
            audio_file="${base}.m4a"
        elif [ -f "${base}.mp4" ]; then
            audio_file="${base}.mp4"
        else
            echo "Warning: No audio file found for $err_file"
            continue
        fi

        # Move both files
        echo "Moving: $(basename "$audio_file")"
        mv "$err_file" "$TARGET_DIR/"
        mv "$audio_file" "$TARGET_DIR/"

        moved_count=$((moved_count + 1))
    fi
done < <(find books/*/audio/ -name "*.err" -type f)

echo ""
echo "========================================="
echo "Moved $moved_count audio files with errors to $TARGET_DIR/"
echo "========================================="
