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

# Discover all 37d agents
AGENTS_DIR=".claude/agents"
if [ ! -d "$AGENTS_DIR" ]; then
    echo "Error: Agents directory '$AGENTS_DIR' not found"
    exit 1
fi

# Create agent-specific folders
echo "Creating agent-specific folders..."
for agent_file in "$AGENTS_DIR"/37d-*.md; do
    if [ -f "$agent_file" ]; then
        # Extract agent name from filename (remove path and .md extension)
        agent_name=$(basename "$agent_file" .md)
        agent_folder="$BOOK_PATH/docs/$agent_name"
        
        if [ ! -d "$agent_folder" ]; then
            mkdir -p "$agent_folder"
            echo "  Created: $agent_folder"
        else
            echo "  Exists: $agent_folder"
        fi
    fi
done

# Create symlink to agents documentation if it doesn't exist
AGENTS_SYMLINK="$BOOK_PATH/docs/agents"
if [ ! -L "$AGENTS_SYMLINK" ]; then
    ln -sf ../../../docs/agents "$AGENTS_SYMLINK"
    echo "Created symlink: $AGENTS_SYMLINK -> ../../../docs/agents"
else
    echo "Symlink exists: $AGENTS_SYMLINK"
fi

# Create other necessary directories
mkdir -p "$BOOK_PATH/assets"
mkdir -p "$BOOK_PATH/audio"
mkdir -p "$BOOK_PATH/generated"
mkdir -p "$BOOK_PATH/prompts"

echo "✅ All folders prepared for $BOOK_FOLDER"
echo ""
echo "Created structure:"
echo "  $BOOK_PATH/docs/"
echo "  $BOOK_PATH/docs/findings/"
echo "  $BOOK_PATH/docs/todo/"
echo "  $BOOK_PATH/docs/agents -> ../../../docs/agents"
for agent_file in "$AGENTS_DIR"/37d-*.md; do
    if [ -f "$agent_file" ]; then
        agent_name=$(basename "$agent_file" .md)
        echo "  $BOOK_PATH/docs/$agent_name/"
    fi
done
echo "  $BOOK_PATH/assets/"
echo "  $BOOK_PATH/audio/"
echo "  $BOOK_PATH/generated/"
echo "  $BOOK_PATH/prompts/"