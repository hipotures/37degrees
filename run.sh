#!/bin/bash

# ---
# Skrypt do generowania obrazów dla serii książek przy użyciu narzędzia Claude.
#
# Ten skrypt automatyzuje proces generowania obrazów dla zdefiniowanej listy książek.
# Dla każdej książki na liście, skrypt wykonuje pętlę 26 razy, za każdym razem
# wywołując narzędzie wiersza poleceń 'claude' z odpowiednimi parametrami.
# ---

# Tablica zawierająca nazwy katalogów z książkami, które mają być przetworzone.
# Możesz łatwo dodać więcej książek, dodając kolejne elementy do tej tablicy.
declare -a book_directories=("0009_fahrenheit_451" "0010_great_gatsby" "0011_gullivers_travels")

# Plik z komendą/promptem dla modelu Claude.
COMMAND_FILE="/home/xai/DEV/37degrees/.claude/commands/37d-s3-image-generation-chatgpt.md"
#COMMAND_FILE="/home/xai/DEV/37degrees/.claude/commands/37d-s4-image-download-chatgpt.md"

# Plik konfiguracyjny MCP.
MCP_CONFIG="/home/xai/DEV/37degrees/.mcp.json-one_stop_workflow"

# Czas oczekiwania w sekundach między poszczególnymi wywołaniami.
SLEEP_DURATION=230

# Sprawdzenie, czy plik z komendą istnieje, aby uniknąć błędów.
if [ ! -f "$COMMAND_FILE" ]; then
    echo "Błąd: Plik z komendą nie został znaleziony pod ścieżką: $COMMAND_FILE"
    exit 1
fi

# Główna pętla iterująca po każdym katalogu zdefiniowanym w tablicy 'book_directories'.
for book_dir in "${book_directories[@]}"; do
    echo "=================================================="
    echo "Rozpoczynam przetwarzanie dla książki: $book_dir"
    echo "=================================================="

    # Wewnętrzna pętla wykonująca się 26 razy dla każdej książki.
    for i in {1..25}; do
        echo "-> Przebieg $i dla książki: $book_dir"

        # Użycie nawiasów klamrowych do grupowania komend, których wyjście
        # jest wspólnie przekierowywane do polecenia 'claude'.
        {
            # Wyświetlenie zawartości pliku z główną komendą.
            cat "$COMMAND_FILE"
            # Dodanie do promptu informacji o konkretnym katalogu książki.
            echo "Katalog książki: $book_dir"
        } | claude --dangerously-skip-permissions -p --mcp-config "$MCP_CONFIG" --allowedTools "*"

        # Sprawdzenie kodu wyjścia ostatniej komendy.
        # Jeśli polecenie 'claude' zakończyło się błędem, skrypt wyświetli komunikat.
        if [ $? -ne 0 ]; then
            echo "Ostrzeżenie: Polecenie 'claude' zakończyło się błędem w przebiegu $i dla $book_dir."
        fi

        echo "Oczekiwanie przez $SLEEP_DURATION sekund przed następnym przebiegiem..."
        sleep "$SLEEP_DURATION"
        echo "--------------------------------------------------"
    done
done

echo "Wszystkie zadania zostały zakończone."

