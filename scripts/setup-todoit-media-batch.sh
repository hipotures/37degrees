#!/bin/bash

# Batch script to run setup-todoit-structure.sh for media m00017 to m00116
# Creates TODOIT structure for all media items with scene_count = 10

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETUP_SCRIPT="$SCRIPT_DIR/setup-todoit-structure.sh"
SCENE_COUNT=10

# Validate setup script exists
if [ ! -f "$SETUP_SCRIPT" ]; then
    echo "❌ Error: setup-todoit-structure.sh not found at: $SETUP_SCRIPT"
    exit 1
fi

# Make sure setup script is executable
chmod +x "$SETUP_SCRIPT"

echo "🚀 Starting batch TODOIT setup for media m00017 to m00116"
echo "   Scene count: $SCENE_COUNT"
echo "   Using script: $SETUP_SCRIPT"
echo ""

# Counter for progress tracking
TOTAL_ITEMS=70  # m00017 to m00116 = 100 items
CURRENT=0
SUCCESS_COUNT=0
ERROR_COUNT=0
SKIP_COUNT=0

# Process each media item from m00017 to m00116
for i in $(seq 47 116); do
    MEDIA_NUM=$(printf "%05d" $i)
    MEDIA_FOLDER="m${MEDIA_NUM}"
    CURRENT=$((CURRENT + 1))

    echo "[$CURRENT/$TOTAL_ITEMS] Processing: $MEDIA_FOLDER"

    # Find actual media folder (may have full name)
    MEDIA_PATH=$(find /home/xai/DEV/37degrees/media/ -maxdepth 1 -type d -name "${MEDIA_FOLDER}_*" | head -1)
    if [ -z "$MEDIA_PATH" ]; then
        echo "   ⏭️  Skipping $MEDIA_FOLDER - folder doesn't exist"
        SKIP_COUNT=$((SKIP_COUNT + 1))
        continue
    fi

    # Extract actual folder name for setup script
    ACTUAL_FOLDER=$(basename "$MEDIA_PATH")


    # Run setup script for this media item
    echo "   🔧 Running setup for $ACTUAL_FOLDER..."
    if "$SETUP_SCRIPT" "$ACTUAL_FOLDER" "$SCENE_COUNT"; then
        echo "   ✅ Success: $ACTUAL_FOLDER"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "   ❌ Error: $ACTUAL_FOLDER failed"
        ERROR_COUNT=$((ERROR_COUNT + 1))
    fi

    echo ""
done

echo "🏁 Batch setup completed!"
echo ""
echo "📊 Summary:"
echo "   Total processed: $CURRENT"
echo "   ✅ Successful: $SUCCESS_COUNT"
echo "   ❌ Errors: $ERROR_COUNT"
echo "   ⏭️  Skipped: $SKIP_COUNT"
echo ""

if [ $ERROR_COUNT -gt 0 ]; then
    echo "⚠️  Some items failed - check the output above for details"
    exit 1
else
    echo "🎉 All available media items processed successfully!"
fi
