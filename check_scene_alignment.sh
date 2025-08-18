#!/bin/bash

# Sprawdza czy properties subitemów zgadzają się z nazwą parent itemu w którym są
# Usage: ./check_scene_alignment.sh [book_name]

# Jeśli nie podano argumentu, użyj pierwszej dostępnej listy z "scene_"
if [[ -z "$1" ]]; then
    BOOK=$(todoit list all | grep -o "│ [0-9]* │ [^│]*" | grep "scene" | head -1 | sed 's/│ [0-9]* │ //' | xargs)
    if [[ -z "$BOOK" ]]; then
        echo "❌ Nie znaleziono żadnej listy ze scenami"
        exit 1
    fi
else
    BOOK="$1"
fi

echo "Sprawdzanie alignment properties dla listy: $BOOK"
echo "=============================================="

if ! todoit list get --key "$BOOK" >/dev/null 2>&1; then
    echo "❌ Lista $BOOK nie istnieje"
    exit 1
fi

echo ""
echo "Pobieranie listy scen..."

# Pobierz wszystkie itemy z listy i znajdź sceny
SCENES=$(todoit item list --list "$BOOK" | grep "^scene_[0-9][0-9][0-9][0-9]" | cut -d' ' -f1)

if [[ -z "$SCENES" ]]; then
    echo "❌ Nie znaleziono scen w liście $BOOK"
    exit 1
fi

SCENE_COUNT=$(echo "$SCENES" | wc -l)
echo "Znaleziono $SCENE_COUNT scen"

echo ""
echo "🔍 Sprawdzanie scene_style_pathfile properties:"
echo "-----------------------------------------------"

STYLE_ERRORS=0
for scene in $SCENES; do
    expected_num=$(echo "$scene" | sed 's/scene_//')
    
    # Sprawdź czy subitem scene_style istnieje
    if todoit item get --list "$BOOK" --item "$scene" --subitem "scene_style" >/dev/null 2>&1; then
        # Pobierz property scene_style_pathfile
        property_output=$(todoit item property get --list "$BOOK" --item "$scene" --subitem "scene_style" --key "scene_style_pathfile" 2>/dev/null)
        
        if [[ $? -eq 0 && -n "$property_output" ]]; then
            property_value=$(echo "$property_output" | tail -1 | xargs)
            
            if [[ "$property_value" =~ scene_([0-9]{4})\.yaml ]]; then
                actual_num="${BASH_REMATCH[1]}"
                
                if [[ "$expected_num" == "$actual_num" ]]; then
                    echo "  ✅ $scene -> scene_${actual_num}.yaml"
                else
                    echo "  ❌ $scene -> scene_${actual_num}.yaml (powinno być scene_${expected_num}.yaml)"
                    ((STYLE_ERRORS++))
                fi
            else
                echo "  ❌ $scene -> $property_value (nieprawidłowy format)"
                ((STYLE_ERRORS++))
            fi
        else
            echo "  ⚠️  $scene -> brak property scene_style_pathfile"
        fi
    else
        echo "  ⚠️  $scene -> brak subitem scene_style"
    fi
done

echo ""
echo "🔍 Sprawdzanie dwn_pathfile properties:"
echo "---------------------------------------"

DWN_ERRORS=0
for scene in $SCENES; do
    expected_num=$(echo "$scene" | sed 's/scene_//')
    
    # Sprawdź czy subitem image_dwn istnieje
    if todoit item get --list "$BOOK" --item "$scene" --subitem "image_dwn" >/dev/null 2>&1; then
        # Pobierz property dwn_pathfile
        property_output=$(todoit item property get --list "$BOOK" --item "$scene" --subitem "image_dwn" --key "dwn_pathfile" 2>/dev/null)
        
        if [[ $? -eq 0 && -n "$property_output" ]]; then
            property_value=$(echo "$property_output" | tail -1 | xargs)
            
            if [[ "$property_value" =~ scene_([0-9]{4})\.png ]]; then
                actual_num="${BASH_REMATCH[1]}"
                
                if [[ "$expected_num" == "$actual_num" ]]; then
                    echo "  ✅ $scene -> scene_${actual_num}.png"
                else
                    echo "  ❌ $scene -> scene_${actual_num}.png (powinno być scene_${expected_num}.png)"
                    ((DWN_ERRORS++))
                fi
            else
                echo "  ❌ $scene -> $property_value (nieprawidłowy format)"
                ((DWN_ERRORS++))
            fi
        else
            echo "  ⚠️  $scene -> brak property dwn_pathfile"
        fi
    else
        echo "  ⚠️  $scene -> brak subitem image_dwn"
    fi
done

TOTAL_ERRORS=$((STYLE_ERRORS + DWN_ERRORS))

echo ""
echo "=============================================="
if [[ $TOTAL_ERRORS -eq 0 ]]; then
    echo "🎉 Wszystkie properties są poprawnie wyrównane!"
else
    echo "❌ Znaleziono $TOTAL_ERRORS błędów wyrównania properties"
    echo "   - scene_style_pathfile: $STYLE_ERRORS błędów"
    echo "   - dwn_pathfile: $DWN_ERRORS błędów"
fi
echo "=============================================="

exit $TOTAL_ERRORS