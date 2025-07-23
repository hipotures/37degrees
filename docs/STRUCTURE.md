# 37 Degrees - Project Structure

## Overview

The project has been reorganized to better support multimedia content for each book. Each book now has its own directory containing all related assets.

## Directory Structure

```
37degrees/
├── books/                      # All book content
│   └── [book_name]/           # Individual book directory
│       ├── book.yaml          # Book metadata and slides
│       ├── cover.jpg/png      # Book cover image
│       ├── background.jpg/png # Custom background (optional)
│       ├── audio/             # Book-specific audio
│       │   ├── theme.mp3      # Main theme music
│       │   └── narration.mp3  # Voice narration (future)
│       └── assets/            # Additional assets
│           ├── quotes/        # Quote images
│           └── characters/    # Character art
│
├── shared_assets/             # Shared resources
│   ├── fonts/                 # Common fonts
│   ├── music/                 # Shared background music
│   ├── templates/             # Video generation templates
│   └── backgrounds/           # Shared AI-generated backgrounds
│
├── content/                   # Series definitions
│   └── classics.yaml          # Classic books series
│
├── output/                    # Generated videos
└── src/                       # Source code
```

## Benefits of New Structure

1. **Self-contained books**: Each book has all its assets in one place
2. **Easy asset management**: Add cover, background, music directly to book folder
3. **Series flexibility**: Same book can appear in multiple series
4. **Better scalability**: Adding new books is straightforward
5. **Asset discovery**: Code automatically finds book-specific assets

## Adding a New Book

1. Create a new directory in `books/`:
   ```bash
   mkdir books/my_new_book
   mkdir books/my_new_book/audio
   mkdir books/my_new_book/assets
   ```

2. Add the book YAML file as `book.yaml`

3. Add optional assets:
   - `cover.jpg` or `cover.png` - Book cover
   - `background.jpg` or `background.png` - Custom background
   - `audio/theme.mp3` - Book-specific music
   - Any other assets in the `assets/` folder

4. Add the book to a series (e.g., in `content/classics.yaml`)

## Asset Priority

The system looks for assets in this order:

1. **Book-specific** (in book folder)
2. **Shared assets** (in shared_assets/)
3. **Generated/default** (created on demand)

For example, backgrounds:
- First checks: `books/[book_name]/background.jpg`
- Then checks: `shared_assets/backgrounds/[prompt_hash].png`
- Finally: Generates new background based on prompt

## Migration from Old Structure

A migration script `migrate_structure.py` was used to convert from the old structure:
- Old: `books/[a-z]/[a-z]/book_name.yaml`
- New: `books/book_name/book.yaml`

The old structure is backed up in `books_backup/` and can be removed once everything is verified to work correctly.