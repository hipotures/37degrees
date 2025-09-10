#!/bin/bash

# Migrate existing TODOIT structure to multilingual
# This script:
# 1. Removes old audio_gen and audio_dwn subitems
# 2. Adds new language-specific subitems (audio_gen_XX and audio_dwn_XX)
# 3. Preserves afa_gen as is

set -e

TARGET_LIST="cc-au-notebooklm"

# Language configuration
LANGUAGES=("pl" "en" "es" "pt" "hi" "ja" "ko" "de" "fr")
declare -A LANGUAGE_NAMES=(
    ["pl"]="Polish"
    ["en"]="English"
    ["es"]="Spanish"
    ["pt"]="Portuguese"
    ["hi"]="Hindi"
    ["ja"]="Japanese"
    ["ko"]="Korean"
    ["de"]="German"
    ["fr"]="French"
)

echo "========================================="
echo "TODOIT Multilingual Migration Script"
echo "========================================="
echo ""
echo "Target list: $TARGET_LIST"
echo "Languages to add: ${LANGUAGES[@]}"
echo ""

# Check if list exists
if ! todoit list show --list "$TARGET_LIST" > /dev/null 2>&1; then
    echo "❌ Error: List '$TARGET_LIST' not found!"
    echo "Please ensure the list exists before running migration."
    exit 1
fi

echo "📋 Fetching all items from the list..."
echo ""

# Counter for statistics
total_items=0
migrated_items=0
skipped_items=0
error_items=0

# Get all items in the list - extract main item keys only (not subitems)
# Look for items that start with book format (NNNN_bookname)
items_output=$(todoit item list --list "$TARGET_LIST" 2>/dev/null | awk -F'│' '/^│/ {gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3}' | awk '{print $1}' | grep "^[0-9][0-9][0-9][0-9]_")

if [ -z "$items_output" ]; then
    echo "⚠️  No items found in list $TARGET_LIST"
    exit 0
fi

# Process each book
while IFS= read -r book_key; do
    if [ -z "$book_key" ]; then
        continue
    fi
    
    ((total_items++))
    echo "📚 Processing book: $book_key"
    
    # Check if item has old structure
    has_old_structure=false
    
    # Check for old audio_gen
    if todoit item show --list "$TARGET_LIST" --item "$book_key" | grep -q "audio_gen[^_]"; then
        has_old_structure=true
        echo "  ⚠️  Found old audio_gen subitem"
    fi
    
    # Check for old audio_dwn
    if todoit item show --list "$TARGET_LIST" --item "$book_key" | grep -q "audio_dwn[^_]"; then
        has_old_structure=true
        echo "  ⚠️  Found old audio_dwn subitem"
    fi
    
    # Check if already migrated (has new structure)
    if todoit item show --list "$TARGET_LIST" --item "$book_key" | grep -q "audio_gen_pl"; then
        echo "  ✅ Already migrated - skipping"
        ((skipped_items++))
        echo ""
        continue
    fi
    
    if [ "$has_old_structure" = true ]; then
        echo "  🔄 Migrating to multilingual structure..."
        
        # Remove old audio_gen if exists
        echo "  🗑️  Removing old audio_gen..."
        todoit item delete --list "$TARGET_LIST" --item "$book_key" --subitem "audio_gen" --force 2>/dev/null || true
        
        # Remove old audio_dwn if exists
        echo "  🗑️  Removing old audio_dwn..."
        todoit item delete --list "$TARGET_LIST" --item "$book_key" --subitem "audio_dwn" --force 2>/dev/null || true
        
        # Add new multilingual subitems
        echo "  ➕ Adding multilingual subitems..."
        
        for lang in "${LANGUAGES[@]}"; do
            lang_name="${LANGUAGE_NAMES[$lang]}"
            
            # Add audio_gen_XX
            echo "    • Adding audio_gen_${lang} (${lang_name} generation)..."
            if todoit item add --list "$TARGET_LIST" --item "$book_key" \
                --subitem "audio_gen_${lang}" \
                --title "Audio generation - ${lang_name}" 2>/dev/null; then
                echo "      ✓ Added audio_gen_${lang}"
            else
                echo "      ⏭️  audio_gen_${lang} already exists or error"
            fi
            
            # Add audio_dwn_XX
            echo "    • Adding audio_dwn_${lang} (${lang_name} download)..."
            if todoit item add --list "$TARGET_LIST" --item "$book_key" \
                --subitem "audio_dwn_${lang}" \
                --title "Audio download - ${lang_name}" 2>/dev/null; then
                echo "      ✓ Added audio_dwn_${lang}"
            else
                echo "      ⏭️  audio_dwn_${lang} already exists or error"
            fi
        done
        
        echo "  ✅ Migration completed for $book_key"
        ((migrated_items++))
    else
        echo "  ℹ️  No old structure found - adding multilingual subitems..."
        
        # Add new multilingual subitems
        for lang in "${LANGUAGES[@]}"; do
            lang_name="${LANGUAGE_NAMES[$lang]}"
            
            # Add audio_gen_XX
            todoit item add --list "$TARGET_LIST" --item "$book_key" \
                --subitem "audio_gen_${lang}" \
                --title "Audio generation - ${lang_name}" 2>/dev/null || true
            
            # Add audio_dwn_XX
            todoit item add --list "$TARGET_LIST" --item "$book_key" \
                --subitem "audio_dwn_${lang}" \
                --title "Audio download - ${lang_name}" 2>/dev/null || true
        done
        
        echo "  ✅ Added multilingual structure for $book_key"
        ((migrated_items++))
    fi
    
    echo ""
done <<< "$items_output"

echo "========================================="
echo "📊 Migration Summary"
echo "========================================="
echo "Total items processed: $total_items"
echo "Successfully migrated: $migrated_items"
echo "Already migrated (skipped): $skipped_items"
echo "Errors: $error_items"
echo ""
echo "✅ Migration completed!"
echo ""
echo "💡 Next steps:"
echo "1. Verify the structure: todoit list show --list $TARGET_LIST"
echo "2. Update the AFA agent to use the new structure"
echo "3. Update the notebook-audio agent for language selection"
echo ""