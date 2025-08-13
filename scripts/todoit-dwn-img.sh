#!/bin/bash

# ---
# Skrypt do generowania obrazów dla serii książek przy użyciu TODOIT i narzędzia Claude.
#
# Ten skrypt automatyzuje proces generowania obrazów dla zdefiniowanej listy książek,
# używając systemu zarządzania zadaniami TODOIT. Dla każdej książki na liście,
# skrypt pobiera pending zadania z TODOIT i wykonuje je jedno po drugim.
# ---

# Tablica zawierająca nazwy katalogów z książkami, które mają być przetworzone.
# Każda nazwa katalogu odpowiada nazwie listy TODOIT.
declare -a book_directories=(
    "0030_romeo_and_juliet"
    "0023_one_hundred_years_of_solitude"
    "0026_pride_and_prejudice"
    "0028_red_and_black"
    "0029_robinson_crusoe"
    "0032_sorrows_of_young_werther"
    "0033_the_trial"
    "0034_to_kill_a_mockingbird"
    "0035_tom_sawyer"
    "0037_wuthering_heights"
)

# Plik z komendą/promptem dla modelu Claude.
COMMAND_FILE="/home/xai/DEV/37degrees/.claude/commands/37d-c4.md"

# Plik konfiguracyjny MCP.
MCP_CONFIG="/home/xai/DEV/37degrees/.mcp.json-one_stop_workflow"

# Czas oczekiwania w sekundach między poszczególnymi wywołaniami.
SLEEP_DURATION=3

# Sprawdzenie, czy plik z komendą istnieje, aby uniknąć błędów.
if [ ! -f "$COMMAND_FILE" ]; then
    echo "Błąd: Plik z komendą nie został znaleziony pod ścieżką: $COMMAND_FILE"
    exit 1
fi

# Funkcja do sprawdzenia postępu zadań w TODOIT
check_progress() {
    local book_dir="$1"
    echo "📊 Sprawdzam postęp dla $book_dir..."
    todoit list show "$book_dir"
}

# Funkcja do rozpoznawania błędów limitu Claude'a
parse_claude_error() {
    local error_output="$1"
    
    # Sprawdź czy błąd zawiera wzorzec "Claude AI usage limit reached|TIMESTAMP"
    if echo "$error_output" | grep -q "Claude AI usage limit reached|"; then
        # Wyciągnij timestamp UTC
        timestamp=$(echo "$error_output" | grep "Claude AI usage limit reached|" | sed 's/.*Claude AI usage limit reached|\([0-9]*\).*/\1/')
        echo "$timestamp"
        return 0
    else
        echo ""
        return 1
    fi
}

# Funkcja do obliczania czasu oczekiwania
calculate_sleep_time() {
    local reset_timestamp="$1"
    
    # Obecny czas w sekundach UTC
    current_time=$(date +%s)
    
    # Oblicz różnicę (dodaj margines bezpieczeństwa 60 sekund)
    sleep_time=$((reset_timestamp - current_time + 60))
    
    # Upewnij się, że czas oczekiwania nie jest ujemny
    if [ $sleep_time -lt 0 ]; then
        sleep_time=0
    fi
    
    echo "$sleep_time"
}

# Funkcja do pobrania następnego zadania z TODOIT
get_next_task() {
  TODOIT_OUTPUT_FORMAT=json \
  todoit item find "$1" --property image_downloaded --value pending --first 2>/dev/null \
  | jq -er 'if (.count // 0) > 0 then .data[0]["Item Key"] else halt_error(1) end' 2>/dev/null \
  || return 1
}

# Funkcja do wykonania komendy claude z retry logic
execute_claude_with_retry() {
    local book_dir="$1"
    local max_attempts=3
    local sleep_between_retries=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "🔄 Próba $attempt/$max_attempts dla $book_dir"
        
        # Wykonaj komendę claude
        local claude_output
        claude_output=$(
            {
                cat "$COMMAND_FILE"
                echo "Katalog książki: $book_dir"
            } | claude --dangerously-skip-permissions -p --mcp-config "$MCP_CONFIG" --allowedTools "*" 2>&1
        )
        
        local exit_code=$?
        
        # Jeśli sukces - zwróć wynik
        if [ $exit_code -eq 0 ]; then
            echo "$claude_output"
            return 0
        fi
        
        # Sprawdź czy to błąd limitu Claude'a - przekaż do istniejącej obsługi
        if echo "$claude_output" | grep -q "Claude AI usage limit reached|"; then
            echo "$claude_output"
            return $exit_code
        fi
        
        # Sprawdź czy to błąd API (5xx) - retry
        if echo "$claude_output" | grep -qE "(API Error.*5[0-9]{2}|Internal server error|Server error|Service unavailable)"; then
            echo "⚠️ Błąd API wykryty w próbie $attempt/$max_attempts"
            
            if [ $attempt -lt $max_attempts ]; then
                echo "⏳ Oczekiwanie ${sleep_between_retries}s przed kolejną próbą..."
                sleep $sleep_between_retries
                ((attempt++))
                continue
            else
                echo "❌ Osiągnięto maksymalną liczbę prób ($max_attempts)"
                echo "$claude_output"
                return $exit_code
            fi
        else
            # Inny błąd - nie retry
            echo "$claude_output"
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
        
        # Wywołaj orchestrator 37d-c4 dla konkretnego zadania z retry logic
        claude_output=$(execute_claude_with_retry "$book_dir")

        # Sprawdzenie kodu wyjścia ostatniej komendy.
        exit_code=$?
        if [ $exit_code -ne 0 ]; then
            echo "⚠️ Błąd: Polecenie 'claude' zakończyło się błędem w iteracji $iteration dla $book_dir."
            
            # Sprawdź czy to błąd limitu Claude'a
            reset_timestamp=$(parse_claude_error "$claude_output")
            
            if [ -n "$reset_timestamp" ]; then
                echo "🔄 Wykryto limit Claude AI. Timestamp resetu: $reset_timestamp"
                
                # Oblicz czas oczekiwania
                sleep_time=$(calculate_sleep_time "$reset_timestamp")
                
                # Konwertuj timestamp na czytelną datę
                reset_date=$(date -d "@$reset_timestamp" "+%Y-%m-%d %H:%M:%S %Z")
                
                if [ $sleep_time -gt 0 ]; then
                    echo "⏰ Limit zostanie zresetowany o: $reset_date"
                    echo "⏳ Oczekiwanie $sleep_time sekund ($(($sleep_time/60)) minut)..."
                    sleep "$sleep_time"
                    echo "🚀 Kontynuowanie przetwarzania..."
                    
                    # Nie zwiększaj licznika iteracji - powtórz tę samą iterację
                    continue
                else
                    echo "✅ Limit już zresetowany, kontynuowanie..."
                fi
            else
                # Sprawdź czy to błąd daily limit ChatGPT - przerwij cały skrypt
                if echo "$claude_output" | grep -qE "(daily usage limit reached|Create image feature is disabled|more available on|plus plan limit|limit resets in|Przekroczony limit generowania obrazów|ChatGPT Plus osiągnął limit|CHATGPT_DAILY_LIMIT_REACHED|Orchestrator zatrzymany z powodu osiągnięcia dziennego limitu)"; then
                    echo "🚫 **KRYTYCZNY BŁĄD: ChatGPT daily image limit osiągnięty**"
                    echo "Szczegóły błędu:"
                    echo "$claude_output"
                    echo ""
                    echo "💡 Generowanie obrazów w ChatGPT zostało zablokowane na dziś."
                    echo "🔄 Uruchom ponownie jutro lub gdy limit zostanie zresetowany."
                    echo ""
                    echo "🛑 **KOŃCZĘ CAŁY SKRYPT** - brak sensu kontynuowania bez możliwości generowania obrazów."
                    exit 1
                else
                    echo "❌ Inny błąd - przerywam przetwarzanie tej książki i przechodzę do następnej."
                    echo "Szczegóły błędu:"
                    echo "$claude_output"
                    break
                fi
            fi
        else
            # Wyświetl output z Claude tylko jeśli nie było błędu
            echo "$claude_output"
        fi

        echo "✅ Iteracja $iteration ukończona"
        echo "Oczekiwanie przez $SLEEP_DURATION sekund przed następną iteracją..."
        sleep "$SLEEP_DURATION"
        echo "--------------------------------------------------"
        
        ((iteration++))
        
        # Zabezpieczenie przed nieskończoną pętlą - maksymalnie 30 iteracji
        if [ $iteration -gt 30 ]; then
            echo "⚠️ Osiągnięto maksymalną liczbę iteracji (30) dla $book_dir. Przerywam."
            break
        fi
        check_progress "$book_dir"
    done
    
    echo "Zakończono przetwarzanie książki: $book_dir"
    echo ""
done

echo "🎉 Wszystkie zadania zostały zakończone."
