#!/bin/bash

# Script to prepare all necessary folders for a book research session
# Usage: ./scripts/prepare-book-folders.sh 0003_anna_karenina

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <book_folder_name>"
    echo "Example: $0 0003_anna_karenina"
    exit 1
fi

BOOK_FOLDER="$1"
BOOK_PATH="books/$BOOK_FOLDER"

# Check if book folder exists
if [ ! -d "$BOOK_PATH" ]; then
    echo "Error: Book folder '$BOOK_PATH' does not exist"
    exit 1
fi

echo "Preparing folders for book: $BOOK_FOLDER"

# Create main research directories
mkdir -p "$BOOK_PATH/docs"
mkdir -p "$BOOK_PATH/docs/findings"
mkdir -p "$BOOK_PATH/docs/todo"
mkdir -p "$BOOK_PATH/search_history"

# Create symlink to agents documentation if it doesn't exist
AGENTS_SYMLINK="$BOOK_PATH/docs/agents"
if [ ! -L "$AGENTS_SYMLINK" ]; then
    ln -sf ../../../config/prompt/agents "$AGENTS_SYMLINK"
    echo "Created symlink: $AGENTS_SYMLINK -> ../../../config/prompt/agents"
else
    echo "Symlink exists: $AGENTS_SYMLINK"
fi

# Create other necessary directories
mkdir -p "$BOOK_PATH/assets"
mkdir -p "$BOOK_PATH/audio"
mkdir -p "$BOOK_PATH/images"
mkdir -p "$BOOK_PATH/prompts"
mkdir -p "$BOOK_PATH/prompts/genimage"
mkdir -p "$BOOK_PATH/prompts/scenes"

echo "✅ All folders prepared for $BOOK_FOLDER"
echo ""
echo "Created structure:"
echo "  $BOOK_PATH/docs/"
echo "  $BOOK_PATH/docs/findings/"
echo "  $BOOK_PATH/docs/todo/"
echo "  $BOOK_PATH/docs/agents -> ../../../config/prompt/agents"
echo "  $BOOK_PATH/search_history/"
echo "  $BOOK_PATH/assets/"
echo "  $BOOK_PATH/audio/"
echo "  $BOOK_PATH/images/"
echo "  $BOOK_PATH/prompts/"
echo "  $BOOK_PATH/prompts/genimage/"
echo "  $BOOK_PATH/prompts/scenes/"