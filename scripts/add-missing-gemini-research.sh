#!/bin/bash

# Skrypt dodający brakujące pozycje do listy gemini-deep-research
# Lista zawiera obecnie książki 0001-0037, dodajemy 0038+

BOOKS_DIR="/home/xai/DEV/37degrees/books"
LIST_KEY="gemini-deep-research"

echo "Rozpoczynam dodawanie brakujących pozycji do listy $LIST_KEY..."

# Znajdź wszystkie książki od 0038 wzwyż
for book_dir in "$BOOKS_DIR"/*/; do
    if [ -d "$book_dir" ]; then
        book_name=$(basename "$book_dir")
        
        # Wyciągnij numer książki (usuń zera wiodące)
        book_num=$(echo "$book_name" | grep -o "^[0-9]*" | sed 's/^0*//')
        
        # Sprawdź czy numer >= 38
        if [ "$book_num" -ge 38 ] 2>/dev/null; then
            book_yaml="$book_dir/book.yaml"
            
            echo "Przetwarzam: $book_name (numer: $book_num)"
            
            # Sprawdź czy istnieje plik book.yaml
            if [ ! -f "$book_yaml" ]; then
                echo "  Ostrzeżenie: Brak pliku book.yaml w $book_dir"
                continue
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
            
            # Utwórz item_key i content
            item_key="$book_name"
            content="Deep Research for $title by $author"
            
            echo "  Dodaję: $item_key"
            echo "    Title: $title"
            echo "    Author: $author"
            
            # Dodaj pozycję do TODOIT CLI
            todoit item add --list "$LIST_KEY" --item "$item_key" --title "$content"
            
            if [ $? -eq 0 ]; then
                echo "  ✓ Dodano pomyślnie"
            else
                echo "  ✗ Błąd podczas dodawania"
            fi
        fi
    fi
done

echo ""
echo "Gotowe! Dodano brakujące pozycje do listy $LIST_KEY."
echo ""
echo "Sprawdź listę poleceniem:"
echo "todoit get-list $LIST_KEY"