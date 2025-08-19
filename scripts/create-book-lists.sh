#!/bin/bash

# Script to create TODOIT lists for books starting from 0038
# Creates lists with keys matching book folder names, proper titles, and 37d tag
# Usage: ./scripts/create-book-lists.sh [--dry-run] [--start=NNNN]

# set -e  # Temporarily disabled for debugging

BOOKS_DIR="/home/xai/DEV/37degrees/books"
DEFAULT_START=41
DRY_RUN=false
START_NUM=$DEFAULT_START

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            echo "🔍 DRY RUN MODE - No lists will be created"
            ;;
        --start=*)
            START_NUM="${arg#*=}"
            echo "📊 Starting from book number: $START_NUM"
            ;;
        *)
            echo "Unknown argument: $arg"
            echo "Usage: $0 [--dry-run] [--start=NNNN]"
            echo "Examples:"
            echo "  $0 --dry-run --start=38"
            echo "  $0 --start=40"
            exit 1
            ;;
    esac
done

echo "🚀 Creating TODOIT lists for books starting from $(printf '%04d' $START_NUM)"
echo ""

# Find all book directories starting from START_NUM
BOOK_DIRS=$(find "$BOOKS_DIR" -maxdepth 1 -type d -name "????_*" | sort)

if [ -z "$BOOK_DIRS" ]; then
    echo "❌ No book directories found in $BOOKS_DIR"
    exit 1
fi

PROCESSED=0
CREATED=0
SKIPPED=0

for book_dir in $BOOK_DIRS; do
    # Extract book folder name (e.g., "0038_iliad")
    BOOK_FOLDER=$(basename "$book_dir")
    
    # Extract book number
    BOOK_NUM=$(echo "$BOOK_FOLDER" | grep -o '^[0-9]\{4\}' || echo "0000")
    
    # Skip if book number is less than START_NUM
    if [ "$BOOK_NUM" -lt "$(printf '%04d' $START_NUM)" ]; then
        continue
    fi
    
    # Check if book.yaml exists
    BOOK_YAML="$book_dir/book.yaml"
    if [ ! -f "$BOOK_YAML" ]; then
        echo "⚠️  Skipping $BOOK_FOLDER - no book.yaml found"
        ((SKIPPED++))
        continue
    fi
    
    # Extract book title from YAML
    BOOK_TITLE=$(yq '.book_info.title' "$BOOK_YAML" 2>/dev/null | sed 's/"//g')
    if [ -z "$BOOK_TITLE" ] || [ "$BOOK_TITLE" = "null" ]; then
        echo "⚠️  Skipping $BOOK_FOLDER - cannot read title from book.yaml"
        ((SKIPPED++))
        continue
    fi
    
    echo "📚 Processing: $BOOK_FOLDER"
    echo "   Title: $BOOK_TITLE"
    
    # Check if list already exists
    LIST_CHECK_OUTPUT=$(todoit list show --list "$BOOK_FOLDER" 2>&1)
    if echo "$LIST_CHECK_OUTPUT" | grep -q "📋\|Progress:\|ID:"; then
        echo "   ⏭️  List already exists - skipping"
        ((SKIPPED++))
        echo ""
        continue
    fi
    
    # Create list title
    LIST_TITLE="AI Image Generation for $BOOK_TITLE"
    
    if [ "$DRY_RUN" = true ]; then
        echo "   📝 Would create list:"
        echo "      Key: $BOOK_FOLDER"
        echo "      Title: $LIST_TITLE"
        echo "      Tag: 37d"
    else
        # Create the list with 37d tag
        echo "   ➕ Creating list: $BOOK_FOLDER"
        CREATE_OUTPUT=$(todoit list create --list "$BOOK_FOLDER" --title "$LIST_TITLE" --tag "37d" 2>&1)
        CREATE_EXIT_CODE=$?
        
        echo "   📝 DEBUG: CREATE_OUTPUT: $CREATE_OUTPUT"
        echo "   📝 DEBUG: EXIT_CODE: $CREATE_EXIT_CODE"
        
        if echo "$CREATE_OUTPUT" | grep -q "error\|Error"; then
            echo "   ❌ Error creating list: $CREATE_OUTPUT"
            continue
        fi
        
        echo "   ✅ Created list with 37d tag"
        ((CREATED++))
    fi
    
    ((PROCESSED++))
    echo ""
done

echo "========================================="
if [ "$DRY_RUN" = true ]; then
    echo "🔍 DRY RUN COMPLETE!"
    echo "📚 Books that would be processed: $PROCESSED"
else
    echo "✅ LIST CREATION COMPLETE!"
    echo "📚 Books processed: $PROCESSED"
    echo "➕ Lists created: $CREATED"
    echo "⏭️  Lists skipped: $SKIPPED"
fi
echo ""

if [ "$CREATED" -gt 0 ] && [ "$DRY_RUN" = false ]; then
    echo "💡 Next steps:"
    echo "   1. Run setup-todoit-structure.sh for each created list"
    echo "   2. Run migrate-gemini-research.sh to add deep research tasks"
    echo ""
    echo "🔍 Verify created lists:"
    echo "   todoit list all"
fi
