#!/bin/bash

# Lista wszystkich książek do sprawdzenia (tylko aktualne, bez _old)
books=(
    "0001_alice_in_wonderland"
    "0002_animal_farm"
    "0003_anna_karenina"
    "0004_brave_new_world"
    "0005_chlopi"
    "0006_don_quixote"
    "0007_dune"
    "0008_emma"
    "0009_fahrenheit_451"
    "0010_great_gatsby"
    "0011_gullivers_travels"
    "0012_harry_potter"
    "0013_hobbit"
    "0014_jane_eyre"
    "0015_lady_of_the_camellias"
    "0016_lalka"
    "0017_little_prince"
    "0018_lord_of_the_rings"
    "0019_master_and_margarita"
    "0020_narnia"
    "0021_nineteen_eighty_four"
    "0022_old_man_and_the_sea"
    "0023_one_hundred_years_of_solitude"
    "0024_pan_tadeusz"
    "0025_portrait_of_dorian_gray"
    "0026_pride_and_prejudice"
    "0027_quo_vadis"
    "0028_red_and_black"
    "0029_robinson_crusoe"
    "0030_romeo_and_juliet"
    "0031_solaris"
    "0032_sorrows_of_young_werther"
    "0033_the_trial"
    "0034_to_kill_a_mockingbird"
    "0035_tom_sawyer"
    "0036_treasure_island"
    "0037_wuthering_heights"
)

echo "Sprawdzanie alignment properties dla wszystkich list książek..."
echo "=============================================================="

for book in "${books[@]}"; do
    echo ""
    echo "Lista: $book"
    echo "------------------------"
    
    # Sprawdź czy lista istnieje
    if todoit item property list --list "$book" >/dev/null 2>&1; then
        
        # Sprawdź scene_style_pathfile - czy numery scen w properties zgadzają się z parent item
        style_misaligned=$(todoit item property list --list "$book" | grep "scene_style.*scene_style_pathfile" | while IFS='│' read -r key subitem prop_key prop_value; do
            key=$(echo "$key" | xargs)
            prop_value=$(echo "$prop_value" | xargs)
            
            # Wyciągnij numer sceny z parent item (np. scene_0001 -> 0001)
            if [[ "$key" =~ scene_([0-9]{4}) ]]; then
                expected_num="${BASH_REMATCH[1]}"
                
                # Sprawdź czy property zawiera ten sam numer sceny
                if [[ "$prop_value" =~ scene_([0-9]{4})\.yaml ]]; then
                    actual_num="${BASH_REMATCH[1]}"
                    if [[ "$expected_num" != "$actual_num" ]]; then
                        echo "MISMATCH"
                    fi
                else
                    echo "MISMATCH"
                fi
            fi
        done | wc -l)
        
        # Sprawdź dwn_pathfile - czy numery scen w properties zgadzają się z parent item
        dwn_misaligned=$(todoit item property list --list "$book" | grep "image_dwn.*dwn_pathfile" | while IFS='│' read -r key subitem prop_key prop_value; do
            key=$(echo "$key" | xargs)
            prop_value=$(echo "$prop_value" | xargs)
            
            # Wyciągnij numer sceny z parent item (np. scene_0001 -> 0001)
            if [[ "$key" =~ scene_([0-9]{4}) ]]; then
                expected_num="${BASH_REMATCH[1]}"
                
                # Sprawdź czy property zawiera ten sam numer sceny
                if [[ "$prop_value" =~ scene_([0-9]{4})\.png ]]; then
                    actual_num="${BASH_REMATCH[1]}"
                    if [[ "$expected_num" != "$actual_num" ]]; then
                        echo "MISMATCH"
                    fi
                else
                    echo "MISMATCH"
                fi
            fi
        done | wc -l)
        
        if [ "$style_misaligned" -gt 0 ] || [ "$dwn_misaligned" -gt 0 ]; then
            echo "❌ BŁĘDY ALIGNMENT:"
            if [ "$style_misaligned" -gt 0 ]; then
                echo "  - scene_style_pathfile: $style_misaligned błędnych alignment"
            fi
            if [ "$dwn_misaligned" -gt 0 ]; then
                echo "  - dwn_pathfile: $dwn_misaligned błędnych alignment"
            fi
        else
            echo "✅ Alignment OK"
        fi
    else
        echo "⚠️  Lista nie istnieje"
    fi
done

echo ""
echo "=============================================================="
echo "Sprawdzanie zakończone."