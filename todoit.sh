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
declare -a book_directories=("0012_harry_potter")

# Plik z komendą/promptem dla modelu Claude.
COMMAND_FILE="/home/xai/DEV/37degrees/.claude/commands/37d-c3.md"

# Plik konfiguracyjny MCP.
MCP_CONFIG="/home/xai/DEV/37degrees/.mcp.json-one_stop_workflow"

# Czas oczekiwania w sekundach między poszczególnymi wywołaniami.
SLEEP_DURATION=179

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

# Funkcja do pobrania następnego zadania z TODOIT
get_next_task() {
    local book_dir="$1"
    
    # Pobierz następne pending zadanie
    next_task=$(todoit item next "$book_dir" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$next_task" ]; then
        # Wyciągnij klucz zadania z odpowiedzi
        task_key=$(echo "$next_task" | grep "Key:" | cut -d':' -f2 | xargs)
        echo "$task_key"
        return 0
    else
        echo ""
        return 1
    fi
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
        
        # Wywołaj orchestrator 37d-c3 dla konkretnego zadania
        {
            # Wyświetlenie zawartości pliku z główną komendą (37d-c3).
            cat "$COMMAND_FILE"
            # Dodanie do promptu informacji o konkretnym katalogu książki.
            echo "Katalog książki: $book_dir"
        } | claude --dangerously-skip-permissions -p --mcp-config "$MCP_CONFIG" --allowedTools "*"

        # Sprawdzenie kodu wyjścia ostatniej komendy.
        exit_code=$?
        if [ $exit_code -ne 0 ]; then
            echo "⚠️ Błąd: Polecenie 'claude' zakończyło się błędem w iteracji $iteration dla $book_dir."
            echo "Przerywam przetwarzanie tej książki i przechodzę do następnej."
            break
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
    done
    
    echo "Zakończono przetwarzanie książki: $book_dir"
    echo ""
done

echo "🎉 Wszystkie zadania zostały zakończone."
