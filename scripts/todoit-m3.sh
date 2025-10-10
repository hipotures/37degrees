#!/bin/bash

# ---
# Skrypt do generowania obrazów dla serii mediów przy użyciu TODOIT i narzędzia Claude.
#
# Ten skrypt automatyzuje proces generowania obrazów dla zdefiniowanej listy mediów,
# używając systemu zarządzania zadaniami TODOIT. Dla każdego medium na liście,
# skrypt pobiera pending zadania z TODOIT i wykonuje je jedno po drugim.
# ---

# =============================================================================
# KONFIGURACJA ZAKRESU MEDIÓW
# =============================================================================
# Ustaw zakres mediów do przetworzenia:
# - Pozostaw puste aby przetworzyć wszystkie media
# - Ustaw liczby aby ograniczyć zakres (np. od 1 do 7)

MEDIA_START_RANGE="71"      # Początek zakresu (np. 1 dla m00001_xxx)
MEDIA_END_RANGE="73"        # Koniec zakresu (np. 7 dla m00007_xxx)

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

# Czas oczekiwania w sekundach między poszczególnymi wywołaniami.
SLEEP_DURATION=79

# Funkcja do sprawdzenia postępu zadań w TODOIT
check_progress() {
    local media_dir="$1"
    echo "📊 Sprawdzam postęp dla $media_dir..."
    todoit list show --list "$media_dir"
}

# Funkcja do parsowania czasu z error_messages
# Wejście: JSON string z error_messages
# Wyjście: liczba sekund do czekania (z +1 minuta buforem) lub 0 jeśli nie znaleziono
parse_reset_time_from_messages() {
    local json_output="$1"

    # Wyciągnij error_messages array
    local error_messages=$(echo "$json_output" | jq -r '.error_messages[]? // empty' 2>/dev/null)

    if [ -z "$error_messages" ]; then
        echo "0"
        return
    fi

    # Szukaj wzorca "X hours and Y minutes" lub "X minutes"
    local hours=0
    local minutes=0

    # Próba 1: "X hours and Y minutes"
    if echo "$error_messages" | grep -qE "[0-9]+ hours? and [0-9]+ minutes?"; then
        hours=$(echo "$error_messages" | grep -oE "[0-9]+ hours? and [0-9]+ minutes?" | grep -oE "^[0-9]+" | head -1)
        minutes=$(echo "$error_messages" | grep -oE "[0-9]+ hours? and [0-9]+ minutes?" | grep -oE "[0-9]+ minutes?" | grep -oE "[0-9]+" | head -1)
    # Próba 2: tylko "X minutes"
    elif echo "$error_messages" | grep -qE "[0-9]+ minutes?"; then
        minutes=$(echo "$error_messages" | grep -oE "[0-9]+ minutes?" | grep -oE "[0-9]+" | head -1)
    # Próba 3: tylko "X hours"
    elif echo "$error_messages" | grep -qE "[0-9]+ hours?"; then
        hours=$(echo "$error_messages" | grep -oE "[0-9]+ hours?" | grep -oE "[0-9]+" | head -1)
    fi

    # Ustaw domyślne wartości jeśli puste
    hours=${hours:-0}
    minutes=${minutes:-0}

    # Jeśli nie znaleziono czasu, zwróć 0
    if [ "$hours" -eq 0 ] && [ "$minutes" -eq 0 ]; then
        echo "0"
        return
    fi

    # Konwertuj na sekundy i dodaj 1 minutę (60s) buforu
    local total_seconds=$((hours * 3600 + minutes * 60 + 60))
    echo "$total_seconds"
}

# Funkcja do pobrania następnego zadania z TODOIT
get_next_task() {
  local list_key="$1"

  # Znajdź zadania gdzie scene_style=completed i image_gen=pending
  TODOIT_OUTPUT_FORMAT=json \
  todoit item find-subitems \
    --list "$list_key" \
    --conditions '{"scene_style":"completed","image_gen":"pending"}' \
    --limit 1 2>/dev/null \
  | jq -r '.data[0].Parent // empty' 2>/dev/null \
  || return 1
}

# Funkcja do wykonania process-image-task.sh z retry logic
execute_image_generation_with_retry() {
    local media_dir="$1"
    local max_attempts=3
    local sleep_between_retries=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        echo "🔄 Próba $attempt/$max_attempts dla $media_dir"

        # Wykonaj skrypt generowania obrazów
        local script_output
        script_output=$("$SCRIPT_DIR/chatgpt/process-image-task.sh" "$media_dir" 2>&1)

        local exit_code=$?

        # Jeśli sukces - zwróć wynik
        if [ $exit_code -eq 0 ]; then
            echo "$script_output"
            return 0
        fi

        # Sprawdź czy to błąd limitu ChatGPT - przekaż do istniejącej obsługi
        if echo "$script_output" | grep -qE "(plus plan limit|limit resets in|daily usage limit)"; then
            echo "$script_output"
            return $exit_code
        fi

        # Sprawdź czy to błąd network/timeout - retry
        if echo "$script_output" | grep -qE "(timeout|network|connection|ECONNREFUSED)"; then
            echo "⚠️ Błąd sieci wykryty w próbie $attempt/$max_attempts"

            if [ $attempt -lt $max_attempts ]; then
                echo "⏳ Oczekiwanie ${sleep_between_retries}s przed kolejną próbą..."
                sleep $sleep_between_retries
                ((attempt++))
                continue
            else
                echo "❌ Osiągnięto maksymalną liczbę prób ($max_attempts)"
                echo "$script_output"
                return $exit_code
            fi
        else
            # Inny błąd - nie retry
            echo "$script_output"
            return $exit_code
        fi
    done

    return 1
}

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

        echo "🎯 Następne zadanie: $task_key"

        # Wywołaj skrypt generowania obrazów dla konkretnego zadania z retry logic
        script_output=$(execute_image_generation_with_retry "$media_dir")

        # Sprawdzenie kodu wyjścia ostatniej komendy.
        exit_code=$?

        # Wyświetl output ze skryptu
        echo "$script_output"

        if [ $exit_code -ne 0 ]; then
            echo "⚠️ Błąd: Skrypt generowania obrazów zakończył się błędem w iteracji $iteration dla $media_dir."

            # Spróbuj sparsować JSON output
            local json_line=$(echo "$script_output" | grep -E '^\s*\{' | tail -1)

            if [ -n "$json_line" ]; then
                # Sprawdź czy jest error_messages
                local has_error_messages=$(echo "$json_line" | jq -r '.error_messages | length' 2>/dev/null)

                if [ -n "$has_error_messages" ] && [ "$has_error_messages" -gt 0 ]; then
                    # Wyświetl komunikaty błędów
                    echo ""
                    echo "🚫 **Wykryto limit ChatGPT Plus:**"
                    echo "$json_line" | jq -r '.error_messages[]' 2>/dev/null

                    # Parsuj czas do resetu
                    local sleep_seconds=$(parse_reset_time_from_messages "$json_line")

                    if [ "$sleep_seconds" -gt 0 ]; then
                        local sleep_minutes=$((sleep_seconds / 60))
                        local sleep_hours=$((sleep_minutes / 60))
                        local remaining_minutes=$((sleep_minutes % 60))

                        # Oblicz czas wznowienia
                        local wake_time=$(date -d "+${sleep_seconds} seconds" "+%Y-%m-%d %H:%M:%S %Z")

                        echo ""
                        echo "💤 Wykonuję sleep na ${sleep_hours}h ${remaining_minutes}min (+ 1min buforu)"
                        echo "⏰ Wznowienie przetwarzania o: $wake_time"
                        echo ""

                        sleep "$sleep_seconds"

                        echo "🚀 Kontynuowanie przetwarzania po sleep..."

                        # Nie zwiększaj licznika iteracji - powtórz tę samą iterację
                        continue
                    fi
                fi
            fi

            # Jeśli nie wykryto limitu z error_messages, sprawdź czy to daily limit (stary sposób)
            if echo "$script_output" | grep -qE "(daily usage limit reached|Create image feature is disabled|more available on|Przekroczony limit generowania obrazów|ChatGPT Plus osiągnął limit|CHATGPT_DAILY_LIMIT_REACHED|Orchestrator zatrzymany z powodu osiągnięcia dziennego limitu)"; then
                echo "🚫 **KRYTYCZNY BŁĄD: ChatGPT daily image limit osiągnięty**"
                echo ""
                echo "💡 Generowanie obrazów w ChatGPT zostało zablokowane na dziś."
                echo "🔄 Uruchom ponownie jutro lub gdy limit zostanie zresetowany."
                echo ""
                echo "🛑 **KOŃCZĘ CAŁY SKRYPT** - brak sensu kontynuowania bez możliwości generowania obrazów."
                exit 1
            else
                echo "❌ Inny błąd - przerywam przetwarzanie tego medium i przechodzę do następnego."
                break
            fi
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
