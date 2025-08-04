#!/bin/bash

# Skrypt do uruchomienia research dla książek 0001-0037
# Używa komendy 37d-research dla każdej książki z przerwą 5 minut

echo "=== Rozpoczynam batch research dla książek 0001-0037 ==="
echo "Start: $(date)"

# Lista folderów książek
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

# Licznik przebiegu
counter=1

# Pętla przez wszystkie książki
for book in "${books[@]}"; do
    echo ""
    echo "==============================================="
    echo "Przebieg $counter z ${#books[@]}: $book"
    echo "Czas: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "==============================================="
    
    # Uruchomienie komendy 37d-research
    (cat /home/xai/DEV/37degrees/.claude/commands/37d-research.md; echo ""; echo "Ścieżka do książki: books/$book") | claude --dangerously-skip-permissions -p --model sonnet
    
    # Sprawdzenie statusu wykonania
    if [ $? -eq 0 ]; then
        echo "✓ Research dla $book zakończony pomyślnie"
    else
        echo "✗ Błąd podczas research dla $book"
    fi
    
    # Przerwa między książkami (5 minut = 300 sekund)
    if [ $counter -lt ${#books[@]} ]; then
        echo "Czekam 5 minut przed następną książką..."
        sleep 300
    fi
    
    ((counter++))
done

echo ""
echo "=== Batch research zakończony ==="
echo "Koniec: $(date)"
echo "Przetworzone książki: ${#books[@]}"