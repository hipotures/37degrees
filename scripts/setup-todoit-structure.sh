#!/bin/bash

# Script to create complete TODOIT structure for a new book
# Usage: ./scripts/setup-todoit-structure.sh 0038_iliad
# Creates list with audio + 25 scenes + video, each with proper subtasks

set -e

# Check if book folder argument provided
if [ $# -ne 1 ]; then
    echo "❌ Błąd: Musisz podać folder książki jako argument"
    echo "Użycie: $0 BOOK_FOLDER"
    echo "Przykład: $0 0038_iliad"
    exit 1
fi

BOOK_FOLDER="$1"
BOOK_PATH="/home/xai/DEV/37degrees/books/$BOOK_FOLDER"
BOOK_YAML="$BOOK_PATH/book.yaml"

# Validate book folder exists
if [ ! -d "$BOOK_PATH" ]; then
    echo "❌ Błąd: Folder książki nie istnieje: $BOOK_PATH"
    exit 1
fi

# Validate book.yaml exists
if [ ! -f "$BOOK_YAML" ]; then
    echo "❌ Błąd: Plik book.yaml nie istnieje: $BOOK_YAML"
    exit 1
fi

# Extract book info from YAML
BOOK_TITLE=$(yq '.book_info.title' "$BOOK_YAML" 2>/dev/null | sed 's/"//g')
BOOK_AUTHOR=$(yq '.book_info.author' "$BOOK_YAML" 2>/dev/null | sed 's/"//g')

if [ -z "$BOOK_TITLE" ] || [ "$BOOK_TITLE" = "null" ]; then
    echo "❌ Błąd: Nie można odczytać tytułu z $BOOK_YAML"
    exit 1
fi

if [ -z "$BOOK_AUTHOR" ] || [ "$BOOK_AUTHOR" = "null" ]; then
    echo "❌ Błąd: Nie można odczytać autora z $BOOK_YAML"
    exit 1
fi

echo "📚 Tworzenie struktury TODOIT dla książki:"
echo "   Folder: $BOOK_FOLDER"
echo "   Tytuł: $BOOK_TITLE"
echo "   Autor: $BOOK_AUTHOR"
echo ""

# Check if list already exists by parsing output
LIST_CHECK_OUTPUT=$(todoit list show --list "$BOOK_FOLDER" 2>&1)
if echo "$LIST_CHECK_OUTPUT" | grep -q "not found\|not accessible\|List.*not found"; then
    LIST_EXISTS=false
else
    echo "⚠️  Lista $BOOK_FOLDER już istnieje - kontynuuję i aktualizuję strukturę"
    LIST_EXISTS=true
fi

echo "🚀 Rozpoczynam tworzenie struktury TODOIT..."

# Function to safely add item (always try to add, skip if already exists)
safe_add_item() {
    local item_key="$1"
    local title="$2"
    
    echo "   ➕ Dodaję item: $item_key"
    local output
    output=$(todoit item add --list "$BOOK_FOLDER" --item "$item_key" --title "$title" 2>&1)
    if echo "$output" | grep -q "already exists\|duplicate"; then
        echo "   ⏭️  Item '$item_key' już istnieje - pomijam"
    elif echo "$output" | grep -q "error\|Error"; then
        echo "   ❌ Błąd dodawania item '$item_key': $output"
    else
        echo "   ✅ Dodano item: $item_key"
    fi
}

# Function to safely add subitem (always try to add, skip if already exists)
safe_add_subitem() {
    local parent_key="$1"
    local subitem_key="$2"
    local title="$3"
    
    echo "     ➕ Dodaję subitem: $parent_key.$subitem_key"
    local output
    output=$(todoit item add --list "$BOOK_FOLDER" --item "$parent_key" --subitem "$subitem_key" --title "$title" 2>&1)
    if echo "$output" | grep -q "already exists\|duplicate"; then
        echo "     ⏭️  Subitem '$parent_key.$subitem_key' już istnieje - pomijam"
    elif echo "$output" | grep -q "error\|Error"; then
        echo "     ❌ Błąd dodawania subitem '$parent_key.$subitem_key': $output"
    else
        echo "     ✅ Dodano subitem: $parent_key.$subitem_key"
    fi
}

# Function to safely set property (always update)
safe_set_property() {
    local item_key="$1"
    local subitem_key="$2"
    local property="$3"
    local value="$4"
    
    if [ -n "$subitem_key" ]; then
        echo "     🏷️  Ustawiam właściwość: $item_key.$subitem_key -> $property = $value"
        todoit item property set --list "$BOOK_FOLDER" --item "$item_key" --subitem "$subitem_key" --key "$property" --value "$value"
    else
        echo "   🏷️  Ustawiam właściwość: $item_key -> $property = $value"
        todoit item property set --list "$BOOK_FOLDER" --item "$item_key" --key "$property" --value "$value"
    fi
}

# Step 1: Create list if doesn't exist
if [ "$LIST_EXISTS" = false ]; then
    echo "1️⃣ Tworzę listę TODOIT: $BOOK_FOLDER"
    LIST_TITLE="AI Image Generation for $BOOK_FOLDER"
    todoit list create --list "$BOOK_FOLDER" --title "$LIST_TITLE" --tag "37d"
    
    # Tag 37d added directly in create command above
    
    # Set list properties
    echo "🏷️ Ustawiam właściwości listy:"
    todoit list property set --list "$BOOK_FOLDER" --key "book_folder" --value "$BOOK_FOLDER"
else
    echo "1️⃣ Lista już istnieje - aktualizuję strukturę"
fi

# Step 2: Create audio task
echo ""
echo "2️⃣ Tworzę zadanie audio..."
safe_add_item "audio" "Audio for video"

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

# Add multilingual audio subitems
for lang in "${LANGUAGES[@]}"; do
    lang_name="${LANGUAGE_NAMES[$lang]}"
    safe_add_subitem "audio" "audio_gen_${lang}" "Audio generation - ${lang_name}"
    safe_add_subitem "audio" "audio_dwn_${lang}" "Audio download - ${lang_name}"
    
    # Set audio download path for each language
    safe_set_property "audio" "audio_dwn_${lang}" "dwn_pathfile" "books/$BOOK_FOLDER/audio/${BOOK_FOLDER}_${lang}.m4a"
done

# Step 3: Create scene tasks (scene_0001 to scene_0025)
echo ""
echo "3️⃣ Tworzę zadania dla 25 scen..."
for i in {1..25}; do
    SCENE_NUM=$(printf "%04d" $i)
    SCENE_KEY="scene_$SCENE_NUM"
    
    echo "📸 Scena $i/25: $SCENE_KEY"
    
    # Main scene item
    safe_add_item "$SCENE_KEY" "Generate image using ${SCENE_KEY}.yaml"
    
    # Scene subitems
    safe_add_subitem "$SCENE_KEY" "image_dwn" "Image download for ${SCENE_KEY}.yaml"
    safe_add_subitem "$SCENE_KEY" "image_gen" "Image generation for ${SCENE_KEY}.yaml"
    safe_add_subitem "$SCENE_KEY" "scene_gen" "Scene generation for ${SCENE_KEY}.yaml"
    safe_add_subitem "$SCENE_KEY" "scene_style" "Scene styling for ${SCENE_KEY}.yaml"
    
    # Set scene properties
    safe_set_property "$SCENE_KEY" "scene_style" "scene_style_pathfile" "books/$BOOK_FOLDER/prompts/genimage/${SCENE_KEY}.yaml"
    safe_set_property "$SCENE_KEY" "image_dwn" "dwn_pathfile" "books/$BOOK_FOLDER/images/${BOOK_FOLDER}_${SCENE_KEY}.png"
done

# Step 4: Create video task
echo ""
echo "4️⃣ Tworzę zadanie video..."
safe_add_item "video" "Video from all scenes"
safe_set_property "video" "" "dwn_pathfile" "books/$BOOK_FOLDER/video/${BOOK_FOLDER}_final.mp4"

echo ""
echo "✅ Struktura TODOIT utworzona pomyślnie!"
echo ""
echo "📊 Podsumowanie utworzonej struktury:"
echo "   📋 Lista: $BOOK_FOLDER ($BOOK_TITLE - $BOOK_AUTHOR)"
echo "   📁 Właściwość book_folder: $BOOK_FOLDER"
echo "   🎵 1x Audio (18 subtasks - 9 languages × 2)"
echo "   🎬 25x Scenes (100 subtasks)"
echo "   📹 1x Video"
echo "   📝 Razem: 27 głównych zadań, 118 subtasks"
echo ""
echo "🔍 Sprawdź strukturę poleceniem:"
echo "   todoit list show --list $BOOK_FOLDER"
echo ""
echo "💡 Następne kroki:"
echo "   1. Uruchom 37d-a3 aby dodać project_id"
echo "   2. Uruchom proces generowania obrazów"