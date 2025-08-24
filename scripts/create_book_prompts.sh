#!/bin/bash

# Skrypt do tworzenia plików book-ds-prompt.md dla wszystkich książek
# na podstawie template Research-prompt.md
# 
# Użycie:
#   ./create_book_prompts.sh        # Tworzy pliki tylko jeśli nie istnieją
#   ./create_book_prompts.sh --force # Nadpisuje istniejące pliki

TEMPLATE_FILE="/home/xai/DEV/37degrees/docs/Research-prompt.md"
BOOKS_DIR="/home/xai/DEV/37degrees/books"
FORCE_OVERWRITE=false

# Sprawdź czy podano opcję --force
if [ "$1" = "--force" ] || [ "$1" = "-f" ]; then
    FORCE_OVERWRITE=true
    echo "Tryb FORCE: będą nadpisywane istniejące pliki"
fi

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Błąd: Nie znaleziono pliku template: $TEMPLATE_FILE"
    exit 1
fi

if [ "$FORCE_OVERWRITE" = true ]; then
    echo "Rozpoczynam tworzenie plików book-ds-prompt.md dla wszystkich książek (z nadpisywaniem)..."
else
    echo "Rozpoczynam tworzenie plików book-ds-prompt.md dla wszystkich książek..."
fi

# Iteruj przez wszystkie katalogi książek
for book_dir in "$BOOKS_DIR"/*/; do
    if [ -d "$book_dir" ]; then
        book_name=$(basename "$book_dir")
        book_yaml="$book_dir/book.yaml"
        docs_dir="$book_dir/docs"
        output_file="$docs_dir/book-ds-prompt.md"
        
        echo "Przetwarzam: $book_name"
        
        # Sprawdź czy istnieje plik book.yaml
        if [ ! -f "$book_yaml" ]; then
            echo "  Ostrzeżenie: Brak pliku book.yaml w $book_dir"
            continue
        fi
        
        # Utwórz katalog docs jeśli nie istnieje
        if [ ! -d "$docs_dir" ]; then
            mkdir -p "$docs_dir"
            echo "  Utworzono katalog: $docs_dir"
        fi
        
        # Sprawdź czy plik już istnieje (tylko jeśli nie ma --force)
        if [ -f "$output_file" ] && [ "$FORCE_OVERWRITE" = false ]; then
            echo "  Pominięto: plik już istnieje - $output_file"
            continue
        elif [ -f "$output_file" ] && [ "$FORCE_OVERWRITE" = true ]; then
            echo "  Nadpisywanie istniejącego pliku: $output_file"
        fi
        
        # Wyciągnij title i author z book.yaml
        title=$(grep "title:" "$book_yaml" | sed 's/.*title: *"\([^"]*\)".*/\1/' | head -1)
        author=$(grep "author:" "$book_yaml" | sed 's/.*author: *"\([^"]*\)".*/\1/' | head -1)
        
        # Sprawdź czy udało się wyciągnąć dane
        if [ -z "$title" ] || [ -z "$author" ]; then
            echo "  Błąd: Nie można wyciągnąć title lub author z $book_yaml"
            echo "    Title: '$title'"
            echo "    Author: '$author'"
            continue
        fi
        
        # Skopiuj template do docelowej lokalizacji
        cp "$TEMPLATE_FILE" "$output_file"
        
        # Podmień parametry [title] i [author]
        sed -i "s/\[title\]/$title/g" "$output_file"
        sed -i "s/\[author\]/$author/g" "$output_file"
        
        if [ "$FORCE_OVERWRITE" = true ] && [ -f "$output_file.bak" ]; then
            echo "  ✓ Nadpisano: $output_file"
        else
            echo "  ✓ Utworzono: $output_file"
        fi
        echo "    Title: $title"
        echo "    Author: $author"
    fi
done

echo ""
if [ "$FORCE_OVERWRITE" = true ]; then
    echo "Gotowe! Utworzono/nadpisano pliki book-ds-prompt.md dla wszystkich książek."
else
    echo "Gotowe! Utworzono pliki book-ds-prompt.md dla wszystkich książek."
fi