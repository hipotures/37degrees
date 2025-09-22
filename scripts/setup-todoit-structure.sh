#!/bin/bash

# Script to create complete TODOIT structure for books and media
# Usage: ./scripts/setup-todoit-structure.sh 0038_iliad [SCENE_COUNT]
# Usage: ./scripts/setup-todoit-structure.sh m00001_atomic_bomb [SCENE_COUNT]
# Creates list with audio + scenes + video, each with proper subtasks
# SCENE_COUNT defaults to 25 if not provided

set -e

# Show help function
show_help() {
    echo "📚 TODOIT Structure Setup Script"
    echo ""
    echo "Tworzy strukturę TODOIT dla książek i mediów z zadaniami audio, scen i video."
    echo ""
    echo "UŻYCIE:"
    echo "  $0 FOLDER [SCENE_COUNT]"
    echo "  $0 --help | -h"
    echo ""
    echo "ARGUMENTY:"
    echo "  FOLDER       - Nazwa folderu książki lub media"
    echo "                 Books: NNNN_title (np. 0038_iliad)"
    echo "                 Media: mNNNN_title (np. m00001_atomic_bomb)"
    echo "  SCENE_COUNT  - Opcjonalna liczba scen (domyślnie: 25 dla books, z YAML dla media)"
    echo ""
    echo "PRZYKŁADY:"
    echo "  Books (domyślnie 25 scen):"
    echo "    $0 0038_iliad"
    echo ""
    echo "  Books z niestandardową liczbą scen:"
    echo "    $0 0038_iliad 30"
    echo ""
    echo "  Media (liczba scen z media.yaml lub 25):"
    echo "    $0 m00001_atomic_bomb"
    echo ""
    echo "  Media z nadpisaniem liczby scen:"
    echo "    $0 m00001_atomic_bomb 15"
    echo ""
    echo "STRUKTURA TWORZONA:"
    echo "  ✓ 1x Audio task (18 subtasks - 9 języków × 2 operacje)"
    echo "  ✓ Nx Scene tasks (N × 4 subtasks)"
    echo "  ✓ 1x Video task"
    echo ""
    echo "WYMAGANIA:"
    echo "  - Folder musi istnieć w books/ lub media/"
    echo "  - Plik book.yaml lub media.yaml musi istnieć"
    echo "  - yq musi być zainstalowane (do parsowania YAML)"
    echo "  - todoit CLI musi być zainstalowane"
}

# Check for help flag
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

# Check if folder argument provided
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "❌ Błąd: Musisz podać folder jako argument"
    echo "Użycie: $0 FOLDER [SCENE_COUNT]"
    echo "Przykłady:"
    echo "  Books:  $0 0038_iliad"
    echo "  Books:  $0 0038_iliad 30"
    echo "  Media:  $0 m00001_atomic_bomb"
    echo "  Media:  $0 m00001_atomic_bomb 15"
    echo "SCENE_COUNT domyślnie wynosi 25"
    echo ""
    echo "Użyj '$0 --help' dla pełnej dokumentacji"
    exit 1
fi

PROJECT_FOLDER="$1"
SCENE_COUNT_PARAM="${2:-}"

# Detect project type and set paths
if [[ "$PROJECT_FOLDER" =~ ^m[0-9] ]]; then
    # Media project
    PROJECT_TYPE="media"
    PROJECT_PATH="/home/xai/DEV/37degrees/media/$PROJECT_FOLDER"
    CONFIG_YAML="$PROJECT_PATH/media.yaml"
    CONFIG_TYPE="media"
else
    # Book project
    PROJECT_TYPE="books"
    PROJECT_PATH="/home/xai/DEV/37degrees/books/$PROJECT_FOLDER"
    CONFIG_YAML="$PROJECT_PATH/book.yaml"
    CONFIG_TYPE="book"
fi

# Validate project folder exists
if [ ! -d "$PROJECT_PATH" ]; then
    echo "❌ Błąd: Folder projektu nie istnieje: $PROJECT_PATH"
    exit 1
fi

# Validate config YAML exists
if [ ! -f "$CONFIG_YAML" ]; then
    echo "❌ Błąd: Plik $CONFIG_TYPE.yaml nie istnieje: $CONFIG_YAML"
    exit 1
fi

# Extract project info from YAML
if [ "$CONFIG_TYPE" = "book" ]; then
    PROJECT_TITLE=$(yq '.book_info.title' "$CONFIG_YAML" 2>/dev/null | sed 's/"//g')
    PROJECT_AUTHOR=$(yq '.book_info.author' "$CONFIG_YAML" 2>/dev/null | sed 's/"//g')
    YAML_SCENE_COUNT=""  # Books don't have scene_count in YAML
else
    PROJECT_TITLE=$(yq '.media_info.title' "$CONFIG_YAML" 2>/dev/null | sed 's/"//g')
    PROJECT_AUTHOR=""
    YAML_SCENE_COUNT=$(yq '.media_info.scene_count' "$CONFIG_YAML" 2>/dev/null | sed 's/"//g')
fi

if [ -z "$PROJECT_TITLE" ] || [ "$PROJECT_TITLE" = "null" ]; then
    echo "❌ Błąd: Nie można odczytać tytułu z $CONFIG_YAML"
    exit 1
fi

# Determine final scene count: parameter > YAML > default 25
if [ -n "$SCENE_COUNT_PARAM" ]; then
    SCENE_COUNT="$SCENE_COUNT_PARAM"
elif [ -n "$YAML_SCENE_COUNT" ] && [ "$YAML_SCENE_COUNT" != "null" ]; then
    SCENE_COUNT="$YAML_SCENE_COUNT"
else
    SCENE_COUNT=25
fi

# Validate scene count is a positive integer
if ! [[ "$SCENE_COUNT" =~ ^[1-9][0-9]*$ ]]; then
    echo "❌ Błąd: SCENE_COUNT musi być liczbą całkowitą większą niż 0"
    echo "Podano: $SCENE_COUNT"
    exit 1
fi

# Determine scene count source for display
if [ -n "$SCENE_COUNT_PARAM" ]; then
    SCENE_SOURCE="parameter"
elif [ -n "$YAML_SCENE_COUNT" ] && [ "$YAML_SCENE_COUNT" != "null" ]; then
    SCENE_SOURCE="YAML"
else
    SCENE_SOURCE="default"
fi

echo "📚 Tworzenie struktury TODOIT dla projektu:"
echo "   Typ: $PROJECT_TYPE"
echo "   Folder: $PROJECT_FOLDER"
echo "   Tytuł: $PROJECT_TITLE"
echo "   Autor: $PROJECT_AUTHOR"
echo "   Liczba scen: $SCENE_COUNT (źródło: $SCENE_SOURCE)"
echo ""

# Check if list already exists by parsing output
LIST_CHECK_OUTPUT=$(todoit list show --list "$PROJECT_FOLDER" 2>&1)
if echo "$LIST_CHECK_OUTPUT" | grep -q "not found\|not accessible\|List.*not found"; then
    LIST_EXISTS=false
else
    echo "⚠️  Lista $PROJECT_FOLDER już istnieje - kontynuuję i aktualizuję strukturę"
    LIST_EXISTS=true
fi

echo "🚀 Rozpoczynam tworzenie struktury TODOIT..."

# Function to safely add item (always try to add, skip if already exists)
safe_add_item() {
    local item_key="$1"
    local title="$2"
    
    echo "   ➕ Dodaję item: $item_key"
    local output
    output=$(todoit item add --list "$PROJECT_FOLDER" --item "$item_key" --title "$title" 2>&1)
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
    output=$(todoit item add --list "$PROJECT_FOLDER" --item "$parent_key" --subitem "$subitem_key" --title "$title" 2>&1)
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
        todoit item property set --list "$PROJECT_FOLDER" --item "$item_key" --subitem "$subitem_key" --key "$property" --value "$value"
    else
        echo "   🏷️  Ustawiam właściwość: $item_key -> $property = $value"
        todoit item property set --list "$PROJECT_FOLDER" --item "$item_key" --key "$property" --value "$value"
    fi
}

# Step 1: Create list if doesn't exist
if [ "$LIST_EXISTS" = false ]; then
    echo "1️⃣ Tworzę listę TODOIT: $PROJECT_FOLDER"
    LIST_TITLE="AI Image Generation for $PROJECT_FOLDER"
    todoit list create --list "$PROJECT_FOLDER" --title "$LIST_TITLE" --tag "37d"

    # Tag 37d added directly in create command above

    # Set list properties
    echo "🏷️ Ustawiam właściwości listy:"
    if [ "$PROJECT_TYPE" = "books" ]; then
        todoit list property set --list "$PROJECT_FOLDER" --key "book_folder" --value "$PROJECT_FOLDER"
    else
        todoit list property set --list "$PROJECT_FOLDER" --key "media_folder" --value "$PROJECT_FOLDER"
    fi
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
    safe_set_property "audio" "audio_dwn_${lang}" "dwn_pathfile" "$PROJECT_TYPE/$PROJECT_FOLDER/audio/${PROJECT_FOLDER}_${lang}.mp4"
done

# Step 3: Create scene tasks (scene_0001 to scene_XXXX)
echo ""
echo "3️⃣ Tworzę zadania dla $SCENE_COUNT scen..."
for i in $(seq 1 $SCENE_COUNT); do
    SCENE_NUM=$(printf "%04d" $i)
    SCENE_KEY="scene_$SCENE_NUM"
    
    echo "📸 Scena $i/$SCENE_COUNT: $SCENE_KEY"
    
    # Main scene item
    safe_add_item "$SCENE_KEY" "Generate image using ${SCENE_KEY}.yaml"
    
    # Scene subitems
    safe_add_subitem "$SCENE_KEY" "image_dwn" "Image download for ${SCENE_KEY}.yaml"
    safe_add_subitem "$SCENE_KEY" "image_gen" "Image generation for ${SCENE_KEY}.yaml"
    safe_add_subitem "$SCENE_KEY" "scene_gen" "Scene generation for ${SCENE_KEY}.yaml"
    safe_add_subitem "$SCENE_KEY" "scene_style" "Scene styling for ${SCENE_KEY}.yaml"
    
    # Set scene properties
    safe_set_property "$SCENE_KEY" "scene_style" "scene_style_pathfile" "$PROJECT_TYPE/$PROJECT_FOLDER/prompts/genimage/${SCENE_KEY}.yaml"
    safe_set_property "$SCENE_KEY" "image_dwn" "dwn_pathfile" "$PROJECT_TYPE/$PROJECT_FOLDER/images/${PROJECT_FOLDER}_${SCENE_KEY}.png"
done

# Step 4: Create video task
echo ""
echo "4️⃣ Tworzę zadanie video..."
safe_add_item "video" "Video from all scenes"
safe_set_property "video" "" "dwn_pathfile" "$PROJECT_TYPE/$PROJECT_FOLDER/video/${PROJECT_FOLDER}_final.mp4"

echo ""
echo "✅ Struktura TODOIT utworzona pomyślnie!"
echo ""
AUDIO_SUBTASKS=$((9 * 2))  # 9 languages × 2 operations
SCENE_SUBTASKS=$((SCENE_COUNT * 4))  # Each scene has 4 subtasks
TOTAL_MAIN_TASKS=$((1 + SCENE_COUNT + 1))  # 1 audio + scenes + 1 video
TOTAL_SUBTASKS=$((AUDIO_SUBTASKS + SCENE_SUBTASKS))

echo "📊 Podsumowanie utworzonej struktury:"
echo "   📋 Lista: $PROJECT_FOLDER ($PROJECT_TITLE - $PROJECT_AUTHOR)"
if [ "$PROJECT_TYPE" = "books" ]; then
    echo "   📁 Właściwość book_folder: $PROJECT_FOLDER"
else
    echo "   📁 Właściwość media_folder: $PROJECT_FOLDER"
fi
echo "   🎵 1x Audio ($AUDIO_SUBTASKS subtasks - 9 languages × 2)"
echo "   🎬 ${SCENE_COUNT}x Scenes ($SCENE_SUBTASKS subtasks)"
echo "   📹 1x Video"
echo "   📝 Razem: $TOTAL_MAIN_TASKS głównych zadań, $TOTAL_SUBTASKS subtasks"
echo ""
echo "🔍 Sprawdź strukturę poleceniem:"
echo "   todoit list show --list $PROJECT_FOLDER"
echo ""
echo "💡 Następne kroki:"
echo "   1. Uruchom 37d-a3 aby dodać project_id"
echo "   2. Uruchom proces generowania obrazów"
