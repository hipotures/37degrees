#!/bin/bash

# ---
# Skrypt do pobierania obrazów dla serii mediów przy użyciu TODOIT i narzędzia Claude.
#
# Ten skrypt automatyzuje proces pobierania obrazów dla zdefiniowanej listy mediów,
# używając systemu zarządzania zadaniami TODOIT. Dla każdego medium na liście,
# skrypt pobiera pending zadania z TODOIT i wykonuje je jedno po drugim.
# ---

# =============================================================================
# KONFIGURACJA ZAKRESU MEDIÓW
# =============================================================================
# Ustaw zakres mediów do przetworzenia:
# - Pozostaw puste aby przetworzyć wszystkie media
# - Ustaw liczby aby ograniczyć zakres (np. od 1 do 7)

MEDIA_START_RANGE="1"      # Początek zakresu (np. 1 dla m00001_xxx)
MEDIA_END_RANGE="7"        # Koniec zakresu (np. 7 dla m00007_xxx)

# =============================================================================
# ŁADOWANIE BIBLIOTEKI I INICJALIZACJA
# =============================================================================

# Ładuj bibliotekę funkcji do obsługi mediów
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/media_utils.sh"

# Walidacja parametrów zakresu
if ! validate_media_range "$MEDIA_START_RANGE" "$MEDIA_END_RANGE"; then
    show_media_range_help
    exit 1
fi

# Zainicjalizuj tablicę media_directories z dynamicznie pobranymi katalogami
declare -a media_directories
mapfile -t media_directories < <(populate_media_directories "$MEDIA_START_RANGE" "$MEDIA_END_RANGE")

# Sprawdź czy znaleziono media do przetworzenia
if [[ ${#media_directories[@]} -eq 0 ]]; then
    echo "❌ Error: No media found in specified range"
    exit 1
fi

# Pokaż informacje o znalezionych mediach
show_media_directories_info

# Plik z komendą/promptem dla modelu Claude.
COMMAND_FILE="/home/xai/DEV/37degrees/.claude/commands/37d-m4-download-image.md"

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
    local media_dir="$1"
    echo "📊 Sprawdzam postęp dla $media_dir..."
    todoit list show --list "$media_dir"
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
  local list_key="$1"

  # Znajdź zadania gdzie image_gen=completed i image_dwn=pending
  TODOIT_OUTPUT_FORMAT=json \
  todoit item find-subitems \
    --list "$list_key" \
    --conditions '{"image_gen":"completed","image_dwn":"pending"}' \
    --limit 1 2>/dev/null \
  | jq -r '.data[0].Parent // empty' 2>/dev/null \
  || return 1
}

# Funkcja do wykonania komendy claude z retry logic
execute_claude_with_retry() {
    local media_dir="$1"
    local task_key="$2"
    local max_attempts=3
    local sleep_between_retries=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        echo "🔄 Próba $attempt/$max_attempts dla $media_dir"

        # Wykonaj komendę claude
        local claude_output
        claude_output=$(
            {
                cat "$COMMAND_FILE"
                echo "Katalog medium: $media_dir, Task key: $task_key"
            } | claude --dangerously-skip-permissions -p --model sonnet --mcp-config "$MCP_CONFIG" --allowedTools "*" 2>&1
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

# Sprawdź czy podano parametr z nazwą konkretnego medium
if [ -n "$1" ]; then
    echo "🎯 Przetwarzam tylko: $1"
    media_directories=("$1")
fi

# Główna pętla iterująca po każdym katalogu zdefiniowanym w tablicy 'media_directories'.
for media_dir in "${media_directories[@]}"; do
    echo "=================================================="
    echo "Rozpoczynam przetwarzanie dla medium: $media_dir"
    echo "=================================================="

    # Wywołaj funkcję sprawdzania postępu
    check_progress "$media_dir"

    # Pętla wykonująca się dopóki są zadania do zrobienia w TODOIT
    iteration=1

    while true; do
        echo "-> Iteracja $iteration dla medium: $media_dir"

        # Pobierz następne zadanie z TODOIT CLI
        task_key=$(get_next_task "$media_dir")

        if [ -z "$task_key" ]; then
            echo "✅ Brak pending zadań dla $media_dir - wszystko ukończone!"
            break
        fi
        date
        echo "🎯 Następne zadanie: $task_key"

        # Wywołaj orchestrator 37d-m4 dla konkretnego zadania z retry logic
        claude_output=$(execute_claude_with_retry "$media_dir" "$task_key")

        # Sprawdzenie kodu wyjścia ostatniej komendy.
        exit_code=$?
        if [ $exit_code -ne 0 ]; then
            echo "⚠️ Błąd: Polecenie 'claude' zakończyło się błędem w iteracji $iteration dla $media_dir."

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
                    echo "❌ Inny błąd - przerywam przetwarzanie tego medium i przechodzę do następnego."
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
            echo "⚠️ Osiągnięto maksymalną liczbę iteracji (30) dla $media_dir. Przerywam."
            break
        fi
        check_progress "$media_dir"
    done

    echo "Zakończono przetwarzanie medium: $media_dir"
    echo ""
done

echo "🎉 Wszystkie zadania zostały zakończone."