#!/bin/bash

# Script to migrate gemini-deep-research items to individual book lists
# Usage: ./scripts/migrate-gemini-research.sh [--dry-run] [--book=BOOK_ID] [--start=BOOK_ID]

set -e

SOURCE_LIST="gemini-deep-research"
TARGET_ITEM_KEY="gemini-ds"
DRY_RUN=false
SINGLE_BOOK=""
START_FROM=""

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            echo "🔍 DRY RUN MODE - No changes will be made"
            ;;
        --book=*)
            SINGLE_BOOK="${arg#*=}"
            echo "📚 SINGLE BOOK MODE - Processing only: $SINGLE_BOOK"
            ;;
        --start=*)
            START_FROM="${arg#*=}"
            echo "🚀 START FROM MODE - Processing from: $START_FROM onwards"
            ;;
        *)
            echo "Unknown argument: $arg"
            echo "Usage: $0 [--dry-run] [--book=BOOK_ID] [--start=BOOK_ID]"
            echo "Examples:"
            echo "  $0 --dry-run --book=0001_alice_in_wonderland"
            echo "  $0 --book=0001_alice_in_wonderland"
            echo "  $0 --start=0040_hamlet"
            echo "  $0 --dry-run --start=0040_hamlet"
            echo "  $0 --dry-run"
            exit 1
            ;;
    esac
done

echo "🚀 Starting migration from $SOURCE_LIST to individual book lists"
echo ""

# Get all items from source list
echo "📋 Getting items from $SOURCE_LIST..."
SOURCE_ITEMS_JSON=$(TODOIT_OUTPUT_FORMAT=json todoit item list --list "$SOURCE_LIST" 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$SOURCE_ITEMS_JSON" ]; then
    echo "❌ Error: Could not get items from $SOURCE_LIST"
    exit 1
fi

# Parse items count
ITEMS_COUNT=$(echo "$SOURCE_ITEMS_JSON" | jq -r '.count // 0' 2>/dev/null)
if [ "$ITEMS_COUNT" -eq 0 ]; then
    echo "⚠️  No items found in $SOURCE_LIST"
    exit 0
fi

echo "📊 Found $ITEMS_COUNT items in source list"
echo ""

# Get all item properties
echo "🏷️ Getting item properties from $SOURCE_LIST..."
PROPERTIES_JSON=$(TODOIT_OUTPUT_FORMAT=json todoit item property list --list "$SOURCE_LIST" 2>/dev/null)

# Process each item
echo "$SOURCE_ITEMS_JSON" | jq -r '.data[]? | "\(.Key)|\(.Title)|\(.Status)"' | while IFS='|' read -r item_key content status; do
    
    # Skip if item_key doesn't look like a book folder (should start with 4 digits)
    if ! echo "$item_key" | grep -q '^[0-9]\{4\}_'; then
        echo "⏭️  Skipping non-book item: $item_key"
        continue
    fi
    
    # Skip if single book mode and this isn't the target book
    if [ -n "$SINGLE_BOOK" ] && [ "$item_key" != "$SINGLE_BOOK" ]; then
        continue
    fi
    
    # Skip if start from mode and this book is before the start point
    if [ -n "$START_FROM" ] && [[ "$item_key" < "$START_FROM" ]]; then
        continue
    fi
    
    echo "📚 Processing book: $item_key"
    echo "   Content: $content"
    echo "   Status: $status"
    
    # Check if target list exists
    if ! todoit list show --list "$item_key" >/dev/null 2>&1; then
        echo "   ⚠️  Target list '$item_key' does not exist - skipping"
        continue
    fi
    
    # Get SEARCH_URL property if exists
    SEARCH_URL=""
    if [ -n "$PROPERTIES_JSON" ]; then
        SEARCH_URL=$(echo "$PROPERTIES_JSON" | jq -r --arg key "$item_key" '.[$key].SEARCH_URL // ""' 2>/dev/null)
    fi
    
    if [ -n "$SEARCH_URL" ] && [ "$SEARCH_URL" != "null" ]; then
        echo "   🔗 Found SEARCH_URL: $SEARCH_URL"
    fi
    
    # Determine ds_gen status based on SEARCH_URL existence
    DS_GEN_STATUS="pending"
    if [ -n "$SEARCH_URL" ] && [ "$SEARCH_URL" != "null" ]; then
        DS_GEN_STATUS="completed"
    fi
    
    if [ "$DRY_RUN" = true ]; then
        echo "   📝 Would add item '$TARGET_ITEM_KEY' to list '$item_key'"
        echo "      - Title: $content"
        echo "      - Subitems:"
        echo "        • ds_gen: Generate gemini deep research... (status: $DS_GEN_STATUS)"
        if [ -n "$SEARCH_URL" ] && [ "$SEARCH_URL" != "null" ]; then
            echo "          - Property SEARCH_URL: $SEARCH_URL"
        fi
        echo "        • ds_dwn: Download gemini deep research... (status: pending)"
        echo "        • ds_exp: Export to gdrive gemini deep research... (status: pending)"
    else
        # Add main item to target list
        echo "   ➕ Adding item '$TARGET_ITEM_KEY' to list '$item_key'..."
        ADD_OUTPUT=$(todoit item add --list "$item_key" --item "$TARGET_ITEM_KEY" --title "$content" 2>&1)
        
        if echo "$ADD_OUTPUT" | grep -q "already exists"; then
            echo "   ⏭️  Item '$TARGET_ITEM_KEY' already exists in '$item_key' - updating subitems..."
        elif echo "$ADD_OUTPUT" | grep -q "error\|Error"; then
            echo "   ❌ Error adding item: $ADD_OUTPUT"
            continue
        else
            echo "   ✅ Added item '$TARGET_ITEM_KEY'"
        fi
        
        # Add ds_gen subitem
        echo "   ➕ Adding subitem 'ds_gen'..."
        DS_GEN_TITLE="Generate gemini deep research for $(echo "$content" | sed 's/Deep Research for //')"
        todoit item add --list "$item_key" --item "$TARGET_ITEM_KEY" --subitem "ds_gen" --title "$DS_GEN_TITLE" 2>/dev/null
        
        # Set ds_gen status
        echo "   🔄 Setting ds_gen status to '$DS_GEN_STATUS'..."
        todoit item status --list "$item_key" --item "$TARGET_ITEM_KEY" --subitem "ds_gen" --status "$DS_GEN_STATUS" 2>/dev/null
        
        # Set SEARCH_URL property on ds_gen if exists
        if [ -n "$SEARCH_URL" ] && [ "$SEARCH_URL" != "null" ]; then
            echo "   🏷️ Setting SEARCH_URL property on ds_gen..."
            todoit item property set --list "$item_key" --item "$TARGET_ITEM_KEY" --subitem "ds_gen" --key "SEARCH_URL" --value "$SEARCH_URL" 2>/dev/null
            echo "   ✅ Set SEARCH_URL property"
        fi
        
        # Add ds_dwn subitem
        echo "   ➕ Adding subitem 'ds_dwn'..."
        DS_DWN_TITLE="Download gemini deep research for $(echo "$content" | sed 's/Deep Research for //')"
        todoit item add --list "$item_key" --item "$TARGET_ITEM_KEY" --subitem "ds_dwn" --title "$DS_DWN_TITLE" 2>/dev/null
        todoit item status --list "$item_key" --item "$TARGET_ITEM_KEY" --subitem "ds_dwn" --status "pending" 2>/dev/null
        
        # Add ds_exp subitem
        echo "   ➕ Adding subitem 'ds_exp'..."
        DS_EXP_TITLE="Export to gdrive gemini deep research for $(echo "$content" | sed 's/Deep Research for //')"
        todoit item add --list "$item_key" --item "$TARGET_ITEM_KEY" --subitem "ds_exp" --title "$DS_EXP_TITLE" 2>/dev/null
        todoit item status --list "$item_key" --item "$TARGET_ITEM_KEY" --subitem "ds_exp" --status "pending" 2>/dev/null
        
        echo "   ✅ Added all subitems (ds_gen: $DS_GEN_STATUS, ds_dwn: pending, ds_exp: pending)"
    fi
    
    echo ""
done

if [ "$DRY_RUN" = true ]; then
    echo "🔍 DRY RUN COMPLETE!"
    echo "💡 Run without --dry-run to perform actual migration"
else
    echo "✅ MIGRATION COMPLETE!"
    echo ""
    echo "💡 To verify migration, check a few target lists:"
    echo "   todoit list show --list 0001_alice_in_wonderland"
    echo "   todoit item property list --list 0001_alice_in_wonderland --item gemini-ds"
fi