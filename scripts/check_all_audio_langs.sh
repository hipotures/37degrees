#!/bin/bash
# Batch audio language verification for all books
# Checks that audio files contain the language indicated by filename

set -e

echo "Starting audio language verification for all books..."
echo ""

checked_books=0
books_with_errors=0

for book_dir in books/*/; do
    # Skip if it's a symlink
    if [ -L "$book_dir" ]; then
        continue
    fi

    # Check if audio directory exists
    audio_dir="${book_dir}audio"
    if [ -d "$audio_dir" ]; then
        echo "Checking: $book_dir"
        checked_books=$((checked_books + 1))

        # Run check_lang.py and capture output
        output=$(python scripts/check_lang.py --folder "$audio_dir" --model turbo 2>&1)

        # If output is not empty, there are errors
        if [ -n "$output" ]; then
            echo "$output"
            books_with_errors=$((books_with_errors + 1))
            echo ""
        fi
    fi
done

echo "========================================="
echo "Summary:"
echo "  Books checked: $checked_books"
echo "  Books with errors: $books_with_errors"
echo "========================================="
