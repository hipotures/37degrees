#!/bin/bash

# Fast cleanup script - copy audio_gen status to audio_gen_pl and delete audio_gen

echo "Starting fast cleanup for cc-au-notebooklm..."
echo ""

count=0
for book in $(todoit list show --list cc-au-notebooklm | grep -o "[0-9]\{4\}_[^[:space:]]*" | sort -u); do
    echo "Processing: $book"
    
    # Set audio_gen_pl to completed (same as audio_gen was)
    todoit item status --list cc-au-notebooklm --item "$book" --subitem audio_gen_pl --status completed 2>/dev/null
    
    # Delete old audio_gen
    todoit item delete --list cc-au-notebooklm --item "$book" --subitem audio_gen --force 2>/dev/null
    
    ((count++))
done

echo ""
echo "✅ Processed $count books"
echo "Done!"