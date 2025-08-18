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

echo "Sprawdzanie nazw itemów dla wszystkich list książek..."
echo "Szukam itemów które NIE mają nazwy scene_NNNN..."
echo "============================================================"

for book in "${books[@]}"; do
    echo ""
    echo "Lista: $book"
    echo "------------------------"
    
    # Sprawdź czy lista istnieje
    if todoit item list --list "$book" >/dev/null 2>&1; then
        # Znajdź wszystkie PARENT itemy (nie subitemy) które zaczynają się od "scene_" ale nie mają formatu scene_NNNN
        # Wyciągnij kolumnę "Key" z tabeli tylko dla parent itemów (nie subitemy)
        # Subitemy to: scene_gen, scene_style, image_gen, image_dwn - pomijamy je
        irregular_items=$(todoit item list --list "$book" | grep -E "^│.*│.*scene_.*│.*│.*│$" | awk -F'│' '{print $3}' | sed 's/^ *//;s/ *$//' | grep -E "^scene_" | grep -v -E "^scene_(gen|style)$" | grep -v -E "^scene_[0-9][0-9][0-9][0-9]$" | wc -l)
        
        if [ "$irregular_items" -gt 0 ]; then
            echo "❌ ZNALEZIONO NIEPRAWIDŁOWE NAZWY PARENT ITEMÓW:"
            echo "  - Nieprawidłowe nazwy: $irregular_items"
            echo "  Przykłady nieprawidłowych nazw:"
            todoit item list --list "$book" | grep -E "^│.*│.*scene_.*│.*│.*│$" | awk -F'│' '{print $3}' | sed 's/^ *//;s/ *$//' | grep -E "^scene_" | grep -v -E "^scene_(gen|style)$" | grep -v -E "^scene_[0-9][0-9][0-9][0-9]$" | head -5
        else
            # Sprawdź czy są jakiekolwiek parent itemy zaczynające się od "scene_"
            scene_items=$(todoit item list --list "$book" | grep -E "^│.*│.*scene_.*│.*│.*│$" | awk -F'│' '{print $3}' | sed 's/^ *//;s/ *$//' | grep -E "^scene_[0-9]" | wc -l)
            if [ "$scene_items" -gt 0 ]; then
                echo "✅ Wszystkie nazwy parent itemów OK (znaleziono $scene_items itemów scene_NNNN)"
            else
                echo "⚠️  Brak parent itemów zaczynających się od 'scene_'"
            fi
        fi
    else
        echo "⚠️  Lista nie istnieje"
    fi
done

echo ""
echo "============================================================"
echo "Sprawdzanie zakończone."