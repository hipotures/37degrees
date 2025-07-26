#!/bin/bash

# ensure_prompts_dirs.sh - Bezpiecznie tworzy katalogi prompts dla wszystkich książek
# Nie usuwa ani nie nadpisuje istniejących plików czy katalogów

echo "=== Ensuring prompts directories for all books ==="
echo

# Liczniki
created=0
existed=0
errors=0

# Przejdź przez wszystkie katalogi książek
for book_dir in books/[0-9]*; do
    if [ -d "$book_dir" ]; then
        prompts_dir="$book_dir/prompts"
        book_name=$(basename "$book_dir")
        
        # Sprawdź czy katalog prompts istnieje
        if [ -d "$prompts_dir" ]; then
            echo "✓ EXISTS: $prompts_dir"
            ((existed++))
        elif [ -e "$prompts_dir" ]; then
            # Jeśli istnieje ale nie jest katalogiem (np. plik)
            echo "⚠️  ERROR: $prompts_dir exists but is not a directory!"
            ((errors++))
        else
            # Utwórz katalog
            if mkdir -p "$prompts_dir"; then
                echo "✅ CREATED: $prompts_dir"
                ((created++))
            else
                echo "❌ FAILED: Could not create $prompts_dir"
                ((errors++))
            fi
        fi
    fi
done

echo
echo "=== Summary ==="
echo "📁 Already existed: $existed"
echo "✨ Newly created: $created"
echo "⚠️  Errors: $errors"
echo "📚 Total books: $((existed + created + errors))"

# Opcjonalnie: utwórz .gitkeep w nowych katalogach
if [ "$created" -gt 0 ]; then
    echo
    read -p "Do you want to add .gitkeep files to new directories? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for book_dir in books/[0-9]*; do
            prompts_dir="$book_dir/prompts"
            gitkeep="$prompts_dir/.gitkeep"
            
            # Tylko dla nowo utworzonych katalogów
            if [ -d "$prompts_dir" ] && [ ! -f "$gitkeep" ] && [ -z "$(ls -A "$prompts_dir" 2>/dev/null)" ]; then
                touch "$gitkeep"
                echo "📝 Added .gitkeep to $prompts_dir"
            fi
        done
    fi
fi

echo
echo "✅ Done!"