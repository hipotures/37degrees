#!/bin/bash
for book in books/[0-9][0-9][0-9][0-9]_*/; do
  book_key=$(basename "$book")
  todoit item status --list cc-au-notebooklm --item "$book_key" --subitem audio_gen_pl --status pending
done
