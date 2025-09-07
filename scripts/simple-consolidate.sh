#!/bin/bash

# Prosty skrypt konsolidacji
mkdir -p /tmp/books

files="au-research_facts_history.md au-research_local_context.md au-research_culture_impact.md au-research_youth_digital.md au-research_dark_drama.md au-research_symbols_meanings.md au-research_reality_wisdom.md au-research_writing_innovation.md au-content_warnings_assessment.md"

for book_dir in books/????_*; do
    if [ ! -d "$book_dir" ] || [ -L "$book_dir" ]; then
        continue
    fi
    
    book_name=$(basename "$book_dir")
    findings_dir="$book_dir/docs/findings"
    
    if [ ! -d "$findings_dir" ]; then
        continue
    fi
    
    # Sprawdź czy są pliki au-*
    au_count=$(ls "$findings_dir"/au-*.md 2>/dev/null | wc -l)
    if [ $au_count -eq 0 ]; then
        continue
    fi
    
    echo "Processing: $book_name"
    output="/tmp/books/${book_name}.md"
    
    echo "# $book_name Research Findings" > "$output"
    echo "" >> "$output"
    
    for file in $files; do
        filepath="$findings_dir/$file"
        if [ -f "$filepath" ]; then
            echo "Adding: $file"
            echo "## $file" >> "$output"
            echo "" >> "$output"
            cat "$filepath" >> "$output"
            echo "" >> "$output"
            echo "---" >> "$output"
            echo "" >> "$output"
        fi
    done
    
    echo "Created: $output"
    echo ""
done

echo "Done. Files in /tmp/books/"
ls -la /tmp/books/