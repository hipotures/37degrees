#!/bin/bash

# Script to add multilingual audio items to all books
# Adds 9 audio_gen_XX and 9 audio_dwn_XX for each book

echo "Adding multilingual items to cc-au-notebooklm..."
echo ""

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

count=0
for book in books/[0-9][0-9][0-9][0-9]_*/; do
    # Skip symlinks
    if [[ -L "${book%/}" ]]; then
        continue
    fi
    
    book_key=$(basename "$book")
    echo "Processing: $book_key"
    
    # Add language-specific items
    for lang in "${LANGUAGES[@]}"; do
        lang_name="${LANGUAGE_NAMES[$lang]}"
        
        # Add audio_gen_XX
        todoit item add --list cc-au-notebooklm --item "$book_key" \
            --subitem "audio_gen_${lang}" \
            --title "Audio generation - ${lang_name}" 2>/dev/null
        
        # Add audio_dwn_XX  
        todoit item add --list cc-au-notebooklm --item "$book_key" \
            --subitem "audio_dwn_${lang}" \
            --title "Audio download - ${lang_name}" 2>/dev/null
    done
    
    ((count++))
    echo "  ✓ Added multilingual items for $book_key"
done

echo ""
echo "✅ Processed $count books"
echo "Each book now has 18 language items (9 audio_gen_XX + 9 audio_dwn_XX)"
echo ""
echo "Next: Run cleanup_todoit_audio.py to remove old audio_gen and audio_dwn"