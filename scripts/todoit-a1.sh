#!/bin/bash

# ---
# Skrypt do generowania scen dla serii książek przy użyciu TODOIT i narzędzia Claude.
#
# Ten skrypt automatyzuje proces generowania scen dla zdefiniowanej listy książek,
# używając systemu zarządzania zadaniami TODOIT. Dla każdej książki na liście,
# skrypt pobiera pending zadania z TODOIT i wykonuje je jedno po drugim.
# ---

# Tablica zawierająca nazwy katalogów z książkami, które mają być przetworzone.
# Każda nazwa katalogu odpowiada nazwie listy TODOIT.
# Unikalna lista katalogów, posortowana rosnąco po numerze
declare -a book_directories=(
  "0069_lolita"
)

# Plik z komendą/promptem dla modelu Claude.
COMMAND_FILE="/home/xai/DEV/37degrees/.claude/agents/37d-a1-generate-scenes.md"

# Plik konfiguracyjny MCP.
MCP_CONFIG="/home/xai/DEV/37degrees/.mcp.json-one_stop_workflow"

# Czas oczekiwania w sekundach między poszczególnymi wywołaniami.
SLEEP_DURATION=11

# Sprawdzenie, czy plik z komendą istnieje, aby uniknąć błędów.
if [ ! -f "$COMMAND_FILE" ]; then
    echo "Błąd: Plik z komendą nie został znaleziony pod ścieżką: $COMMAND_FILE"
    exit 1
fi

# Funkcja do sprawdzenia postępu zadań w TODOIT
check_progress() {
    local book_dir="$1"
    echo "📊 Sprawdzam postęp dla $book_dir..."
    todoit list show --list "$book_dir"
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

# Funkcja sprawdzenia czy książka potrzebuje generowania scen
needs_scene_generation() {
  local list_key="$1"
  
  # Sprawdź czy istnieją jakieś scene_gen=pending
  local pending_count
  pending_count=$(TODOIT_OUTPUT_FORMAT=json \
    todoit item find-subitems \
      --list "$list_key" \
      --conditions '{"scene_gen":"pending"}' \
      2>/dev/null \
    | jq -r '.count // 0' 2>/dev/null | tr -d '\n' || echo "0")
  
  # Upewnij się że to jest liczba
  if ! [[ "$pending_count" =~ ^[0-9]+$ ]]; then
    pending_count=0
  fi
  
  # Zwróć 0 (sukces) jeśli są pending zadania, 1 (błąd) jeśli nie ma
  [ "$pending_count" -gt 0 ]
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

    # Sprawdź czy lista TODOIT istnieje
    if ! todoit list show --list "$book_dir" >/dev/null 2>&1; then
        echo "⏭️  Lista TODOIT '$book_dir' nie istnieje - pomijam"
        echo ""
        continue
    fi

    # Wywołaj funkcję sprawdzania postępu
    check_progress "$book_dir"

    # Sprawdź czy książka potrzebuje generowania scen
    if needs_scene_generation "$book_dir"; then
        echo "🎯 Książka $book_dir potrzebuje generowania scen"
        
        # Wywołaj agenta 37d-a1-generate-scenes dla całej książki z retry logic
        claude_output=$(execute_claude_with_retry "$book_dir")

        # Sprawdzenie kodu wyjścia ostatniej komendy.
        exit_code=$?
        if [ $exit_code -ne 0 ]; then
            echo "⚠️ Błąd: Polecenie 'claude' zakończyło się błędem dla $book_dir."
            
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
                    
                    # Spróbuj ponownie dla tej samej książki
                    echo "🔄 Ponowna próba dla $book_dir..."
                    claude_output=$(execute_claude_with_retry "$book_dir")
                    exit_code=$?
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
                fi
            fi
        fi
        
        # Wyświetl output z Claude tylko jeśli nie było błędu
        if [ $exit_code -eq 0 ]; then
            echo "$claude_output"
            echo "✅ Generowanie scen ukończone dla $book_dir"
        fi
    else
        echo "✅ Brak pending zadań dla $book_dir - wszystkie sceny już wygenerowane!"
    fi
    
    echo "Zakończono przetwarzanie książki: $book_dir"
    echo ""
done

echo "🎉 Wszystkie zadania zostały zakończone."
