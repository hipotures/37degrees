#!/bin/bash

# Skrypt do zmiany tagów dla list z sufiksem _old
# 1. Dodaje tag 37d_old
# 2. Usuwa tag 37d

echo "==================================================="
echo "Rozpoczynam zmianę tagów dla list _old"
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

# Licznik
total=${#book_lists[@]}
current=0

# Zmiana tagów dla każdej listy
for book_list in "${book_lists[@]}"; do
    ((current++))
    old_list_name="${book_list}_old"
    echo ""
    echo "[$current/$total] Zmieniam tagi dla listy: $old_list_name"
    echo "---------------------------------------------------"
    
    # Sprawdź czy lista _old istnieje
    if todoit list show --list "$old_list_name" >/dev/null 2>&1; then
        echo "  🏷️ Dodaję tag 37d_old..."
        todoit list tag add --list "$old_list_name" --tag 37d_old
        
        if [ $? -eq 0 ]; then
            echo "  ✅ Tag 37d_old dodany"
        else
            echo "  ❌ Błąd dodawania tagu 37d_old"
        fi
        
        echo "  🏷️ Usuwam tag 37d..."
        todoit list tag remove --list "$old_list_name" --tag 37d
        
        if [ $? -eq 0 ]; then
            echo "  ✅ Tag 37d usunięty"
        else
            echo "  ⚠️ Tag 37d nie istniał lub błąd usuwania"
        fi
        
        echo "  ✅ Zmiana tagów dla $old_list_name zakończona"
    else
        echo "  ⚠️ Lista $old_list_name nie istnieje - pomijam"
    fi
    
    # Krótka pauza między operacjami
    sleep 0.5
done

echo ""
echo "==================================================="
echo "Zmiana tagów dla wszystkich list _old zakończona!"
echo "Przetworzono $total list"
echo "==================================================="