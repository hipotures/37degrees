#!/bin/bash

# ---
# Zoptymalizowany skrypt do pobierania obrazów dla serii książek przy użyciu TODOIT.
# Używa atomic-image-download.py zamiast Claude dla każdego obrazka - 20-30x szybszy.
#
# Ten skrypt automatyzuje proces pobierania obrazów dla zdefiniowanej listy książek,
# używając systemu zarządzania zadaniami TODOIT. Dla każdej książki na liście,
# skrypt pobiera pending zadania z TODOIT i wykonuje je jedno po drugim.
# ---

# Tablica zawierająca nazwy katalogów z książkami, które mają być przetworzone.
# Każda nazwa katalogu odpowiada nazwie listy TODOIT.
declare -a book_directories=(
    "0034_to_kill_a_mockingbird"
    "0037_wuthering_heights"
)

# Ścieżka do zoptymalizowanego skryptu pobierania
ATOMIC_DOWNLOADER="/home/xai/DEV/37degrees/scripts/atomic-image-download.py"

# Czas oczekiwania w sekundach między poszczególnymi wywołaniami (znacznie skrócony)
SLEEP_DURATION=1

# Sprawdzenie, czy skrypt pobierania istnieje
if [ ! -f "$ATOMIC_DOWNLOADER" ]; then
    echo "Błąd: Skrypt pobierania nie został znaleziony pod ścieżką: $ATOMIC_DOWNLOADER"
    exit 1
fi

# Funkcja do sprawdzenia postępu zadań w TODOIT
check_progress() {
    local book_dir="$1"
    echo "📊 Sprawdzam postęp dla $book_dir..."
    todoit list show "$book_dir"
}

# Zoptymalizowana funkcja do pobrania następnego zadania z TODOIT  
get_next_task() {
    local book_dir="$1"
    
    # Użyj jq do znalezienia pierwszego zadania gotowego do pobrania
    # (image_downloaded=pending AND image_generated=completed)
    TODOIT_OUTPUT_FORMAT=json \
    todoit item property list "$book_dir" 2>/dev/null \
    | jq -r '
        to_entries[] | 
        select(.value.image_downloaded == "pending" and .value.image_generated == "completed") | 
        .key
    ' | head -1 || return 1
}

# Funkcja do wykonania atomic download z retry logic
execute_atomic_download_with_retry() {
    local book_dir="$1"
    local task_key="$2"
    local max_attempts=3
    local sleep_between_retries=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "🔄 Próba $attempt/$max_attempts dla $book_dir/$task_key"
        
        # Wykonaj atomic download
        local download_output
        download_output=$(python3 "$ATOMIC_DOWNLOADER" "$book_dir" "$task_key" 2>&1)
        local exit_code=$?
        
        # Jeśli sukces - zwróć wynik
        if [ $exit_code -eq 0 ]; then
            echo "$download_output"
            return 0
        fi
        
        # Sprawdź czy to błąd ChatGPT daily limit - przerwij cały skrypt
        if echo "$download_output" | grep -qE "(daily usage limit reached|Create image feature is disabled|more available on|plus plan limit|limit resets in|Przekroczony limit generowania obrazów|ChatGPT Plus osiągnął limit|CHATGPT_DAILY_LIMIT_REACHED|You've hit the plus plan limit)"; then
            echo "🚫 **KRYTYCZNY BŁĄD: ChatGPT daily image limit osiągnięty**"
            echo "Szczegóły błędu:"
            echo "$download_output"
            echo ""
            echo "💡 Pobieranie obrazów w ChatGPT zostało zablokowane na dziś."
            echo "🔄 Uruchom ponownie jutro lub gdy limit zostanie zresetowany."
            echo ""
            echo "🛑 **KOŃCZĘ CAŁY SKRYPT** - brak sensu kontynuowania bez możliwości pobierania obrazów."
            exit 1
        fi
        
        # Sprawdź czy to błąd sieciowy/tymczasowy - retry
        if echo "$download_output" | grep -qE "(connection error|timeout|network error|failed to connect|browser error|502|503|504)"; then
            echo "⚠️ Błąd sieciowy wykryty w próbie $attempt/$max_attempts"
            
            if [ $attempt -lt $max_attempts ]; then
                echo "⏳ Oczekiwanie ${sleep_between_retries}s przed kolejną próbą..."
                sleep $sleep_between_retries
                ((attempt++))
                continue
            else
                echo "❌ Osiągnięto maksymalną liczbę prób ($max_attempts)"
                echo "$download_output"
                return $exit_code
            fi
        else
            # Inny błąd - nie retry
            echo "❌ Błąd pobierania:"
            echo "$download_output"
            return $exit_code
        fi
    done
    
    return 1
}

# Główna pętla iterująca po każdym katalogu zdefiniowanym w tablicy 'book_directories'.
for book_dir in "${book_directories[@]}"; do
    echo "=================================================="
    echo "Rozpoczynam przetwarzanie dla książki: $book_dir"
    echo "=================================================="

    # Wywołaj funkcję sprawdzania postępu
    check_progress "$book_dir"

    # Pętla wykonująca się dopóki są zadania do zrobienia w TODOIT
    iteration=1
    
    while true; do
        echo "-> Iteracja $iteration dla książki: $book_dir"
        
        # Pobierz następne zadanie z TODOIT CLI
        task_key=$(get_next_task "$book_dir")
        
        if [ -z "$task_key" ]; then
            echo "✅ Brak pending zadań dla $book_dir - wszystko ukończone!"
            break
        fi
        
        echo "🎯 Następne zadanie: $task_key"
        
        # Wywołaj atomic downloader z retry logic
        download_output=$(execute_atomic_download_with_retry "$book_dir" "$task_key")
        exit_code=$?
        
        if [ $exit_code -ne 0 ]; then
            echo "⚠️ Błąd: Pobieranie zakończyło się błędem w iteracji $iteration dla $book_dir/$task_key."
            echo "❌ Przerywam przetwarzanie tej książki i przechodzę do następnej."
            break
        else
            # Wyświetl output z atomic downloader
            echo "$download_output"
        fi

        echo "✅ Iteracja $iteration ukończona"
        echo "Oczekiwanie przez $SLEEP_DURATION sekund przed następną iteracją..."
        sleep "$SLEEP_DURATION"
        echo "--------------------------------------------------"
        
        ((iteration++))
        
        # Zabezpieczenie przed nieskończoną pętlą - maksymalnie 50 iteracji
        if [ $iteration -gt 50 ]; then
            echo "⚠️ Osiągnięto maksymalną liczbę iteracji (50) dla $book_dir. Przerywam."
            break
        fi
        
        # Sprawdź postęp po każdej iteracji
        check_progress "$book_dir"
    done
    
    echo "Zakończono przetwarzanie książki: $book_dir"
    echo ""
done

echo "🎉 Wszystkie zadania zostały zakończone."