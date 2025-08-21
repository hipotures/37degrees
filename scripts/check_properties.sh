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

echo "Sprawdzanie properties dla wszystkich list książek..."
echo "=================================================="

for book in "${books[@]}"; do
    echo ""
    echo "Lista: $book"
    echo "------------------------"
    
    # Sprawdź czy lista istnieje
    if todoit item property list --list "$book" >/dev/null 2>&1; then
        # Sprawdź properties scene_style_pathfile
        scene_issues=$(todoit item property list --list "$book" | grep scene_style_pathfile | grep -v "scene_[0-9][0-9][0-9][0-9]\.yaml" | wc -l)
        
        # Sprawdź properties dwn_pathfile dla image_dwn
        dwn_issues=$(todoit item property list --list "$book" | grep "image_dwn.*dwn_pathfile" | grep -v "scene_[0-9][0-9][0-9][0-9]\.png" | wc -l)
        
        if [ "$scene_issues" -gt 0 ] || [ "$dwn_issues" -gt 0 ]; then
            echo "❌ BŁĘDY ZNALEZIONE:"
            if [ "$scene_issues" -gt 0 ]; then
                echo "  - scene_style_pathfile: $scene_issues błędnych właściwości"
                echo "  Przykłady błędów:"
                todoit item property list --list "$book" | grep scene_style_pathfile | grep -v "scene_[0-9][0-9][0-9][0-9]\.yaml" | head -3
            fi
            if [ "$dwn_issues" -gt 0 ]; then
                echo "  - dwn_pathfile (image_dwn): $dwn_issues błędnych właściwości"
                echo "  Przykłady błędów:"
                todoit item property list --list "$book" | grep "image_dwn.*dwn_pathfile" | grep -v "scene_[0-9][0-9][0-9][0-9]\.png" | head -3
            fi
        else
            echo "✅ Properties OK"
        fi
    else
        echo "⚠️  Lista nie istnieje"
    fi
done

echo ""
echo "=================================================="
echo "Sprawdzanie zakończone."