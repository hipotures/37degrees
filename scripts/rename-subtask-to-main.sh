#!/bin/bash

# Skrypt do zmiany nazw list z _subtask na oryginalne nazwy
# Zamienia 0001_alice_in_wonderland_subtask -> 0001_alice_in_wonderland

echo "==================================================="
echo "Rozpoczynam zmianę nazw list z _subtask na główne"
echo "==================================================="

# Wszystkie katalogi książek z books/ (na podstawie conv-list-all.sh)
declare -a book_lists=(
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

# Licznik
total=${#book_lists[@]}
current=0

# Zmiana nazwy każdej listy
for book_list in "${book_lists[@]}"; do
    ((current++))
    subtask_list_name="${book_list}_subtask"
    echo ""
    echo "[$current/$total] Zmieniam nazwę listy: $subtask_list_name -> $book_list"
    echo "---------------------------------------------------"
    
    # Sprawdź czy lista _subtask istnieje przed zmianą nazwy
    if todoit list show --list "$subtask_list_name" >/dev/null 2>&1; then
        # Zmień nazwę listy z _subtask na oryginalną
        todoit list rename --list "$subtask_list_name" --key "$book_list" --yes
        
        exit_code=$?
        if [ $exit_code -eq 0 ]; then
            echo "✅ Zmiana nazwy $subtask_list_name zakończona sukcesem"
        else
            echo "❌ Błąd zmiany nazwy $subtask_list_name (kod: $exit_code)"
        fi
    else
        echo "⚠️ Lista $subtask_list_name nie istnieje - pomijam"
    fi
    
    # Krótka pauza między operacjami
    sleep 0.5
done

echo ""
echo "==================================================="
echo "Zmiana nazw wszystkich list _subtask zakończona!"
echo "Przetworzono $total list"
echo "==================================================="