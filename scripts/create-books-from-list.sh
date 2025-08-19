#!/bin/bash

# Script to create book structure from /tmp/books-2.txt starting from 0038
# Usage: ./scripts/create-books-from-list.sh [--dry-run] [--limit=N]

set -e

BOOKS_FILE="/tmp/books-2.txt"
STARTING_NUM=38
DRY_RUN=false
LIMIT=0

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            echo "🔍 DRY RUN MODE - No files will be created"
            ;;
        --limit=*)
            LIMIT="${arg#*=}"
            echo "📊 LIMIT MODE - Processing only $LIMIT book(s)"
            ;;
        *)
            echo "Unknown argument: $arg"
            echo "Usage: $0 [--dry-run] [--limit=N]"
            exit 1
            ;;
    esac
done

if [ "$DRY_RUN" = true ] || [ "$LIMIT" -gt 0 ]; then
    echo ""
fi

if [ ! -f "$BOOKS_FILE" ]; then
    echo "Error: Books file '$BOOKS_FILE' does not exist"
    exit 1
fi

echo "Creating book structures from $BOOKS_FILE starting from number $(printf '%04d' $STARTING_NUM)..."
echo ""

# Function to normalize book name for directory
normalize_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | \
    sed 's/[^a-z0-9 ]//g' | \
    sed 's/ \+/ /g' | \
    sed 's/^ *//; s/ *$//' | \
    tr ' ' '_'
}

# Function to create book.yaml
create_book_yaml() {
    local title="$1"
    local author="$2"
    local book_dir="$3"
    
    if [ "$DRY_RUN" = true ]; then
        echo "    Would create: $book_dir/book.yaml"
        return
    fi
    
    cat > "$book_dir/book.yaml" << EOF
book_info:
  title: "$title"
  title_pl: ""
  author: "$author"
  year: 
  genre: ""
EOF
}

# Count already processed books to adjust starting number
done_count=$(grep -c "^✅ DONE:" "$BOOKS_FILE" || echo "0")
echo "📋 Found $done_count already processed book(s)"

# Process books
current_num=$((STARTING_NUM + done_count))
processed=0
echo "🔢 Starting from number: $(printf '%04d' $current_num)"
echo ""

while IFS= read -r line; do
    # Skip empty lines
    if [ -z "$line" ]; then
        continue
    fi
    
    # Skip lines already marked as done
    if [[ "$line" =~ ^✅ ]]; then
        continue
    fi
    
    # Parse "Title - Author" format
    if [[ "$line" =~ ^(.*)\ -\ (.*)$ ]]; then
        title="${BASH_REMATCH[1]}"
        author="${BASH_REMATCH[2]}"
        
        # Normalize title for directory name
        normalized_title=$(normalize_name "$title")
        book_num=$(printf '%04d' $current_num)
        book_dir="books/${book_num}_${normalized_title}"
        
        echo "Processing: $title by $author"
        echo "  Directory: $book_dir"
        
        # Check if already exists
        if [ -d "$book_dir" ]; then
            echo "  ⚠️  SKIPPED: Directory already exists"
            if [ "$DRY_RUN" = false ]; then
                sed -i "s/^$line$/✅ DONE: $line/" "$BOOKS_FILE"
            fi
        else
            if [ "$DRY_RUN" = true ]; then
                echo "  📁 Would create: $book_dir/"
                echo "    Would run: ./scripts/prepare-book-folders.sh ${book_num}_${normalized_title}"
                echo "    Would mark as done in $BOOKS_FILE"
            else
                # Create book structure
                mkdir -p "$book_dir"
                
                # Create book.yaml
                create_book_yaml "$title" "$author" "$book_dir"
                
                # Run prepare-book-folders.sh
                ./scripts/prepare-book-folders.sh "${book_num}_${normalized_title}"
                
                echo "  ✅ CREATED: Structure created successfully"
                
                # Mark as done in the file
                sed -i "s/^$line$/✅ DONE: $line/" "$BOOKS_FILE"
            fi
        fi
        
        # Count all processed books (both new and skipped) for limit check
        ((processed++))
        
        ((current_num++))
        echo ""
        
        # Debug: show current progress
        if [ "$LIMIT" -gt 0 ]; then
            echo "DEBUG: processed=$processed, limit=$LIMIT"
        fi
        
        # Check limit
        if [ "$LIMIT" -gt 0 ] && [ "$processed" -ge "$LIMIT" ]; then
            echo "📊 Reached limit of $LIMIT book(s)"
            break
        fi
        
    else
        echo "⚠️  SKIPPED: Cannot parse line: $line"
    fi
    
done < <(cat "$BOOKS_FILE")

echo "========================================="
if [ "$DRY_RUN" = true ]; then
    echo "🔍 DRY RUN COMPLETE!"
    echo "📚 Books that would be processed: $processed"
else
    echo "✅ Processing complete!"
    echo "📚 Books processed: $processed"
fi
echo "🔢 Next available number: $(printf '%04d' $current_num)"
echo ""
if [ "$DRY_RUN" = false ]; then
    echo "Updated file: $BOOKS_FILE (marked with ✅ DONE:)"
fi