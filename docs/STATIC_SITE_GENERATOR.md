# Static Site Generator Guide

## Overview

The 37degrees project now includes a static HTML site generator that creates an interactive web experience for browsing the book collection. The generator transforms book YAML files into beautiful, responsive HTML pages organized by collections.

## Architecture

### Components

1. **Base Classes** (`src/site_generator/base.py`)
   - `BaseHtmlGenerator`: Abstract base for all HTML generators
   - Template rendering with variable substitution
   - Asset management (CSS, JS, fonts)
   - Path utilities

2. **Generators**
   - `BookPageGenerator`: Creates individual book pages from book.yaml
   - `IndexPageGenerator`: Creates main index.html with all collections
   - `CollectionPageGenerator`: Creates pages for each collection

3. **Site Builder** (`src/site_generator/site_builder.py`)
   - Orchestrates the generation process
   - Progress tracking and reporting
   - Batch processing support

## Usage

### Command Line

```bash
# Generate complete site
python main.py site

# Generate single book page
python main.py site 17
python main.py site little_prince

# Generate all books in a collection
python main.py site classics

# Generate specific book from collection
python main.py site classics 17
```

### Configuration

Configure output directory in `config/settings.yaml`:

```yaml
paths:
  site_output: ${SITE_OUTPUT:-site}
```

Or override via environment:
```bash
SITE_OUTPUT=public python main.py site
```

## Generated Structure

```
site/
├── index.html              # Main page with all collections
├── books/                  # Individual book pages
│   ├── 0017_little_prince.html
│   ├── 0019_master_and_margarita.html
│   └── ...
├── collections/            # Collection overview pages
│   ├── classics.html
│   └── ...
└── assets/                 # Static resources
    ├── css/
    ├── js/
    └── fonts/
```

## Features

### Book Pages

Each book page includes:
- **Interactive Timeline**: Author's life events
- **Symbol Explorer**: Key themes and symbols with modal details
- **Visual Statistics**: Charts showing translations, popularity
- **Adaptations Gallery**: Movies, theater, other media
- **Smooth Animations**: Scroll-triggered reveals
- **Responsive Design**: Mobile-friendly layout

### Index Page

The main index.html features:
- **Hero Section**: Project introduction
- **Collection Grid**: Books organized by series
- **Book Cards**: Visual preview with emoji, title, author
- **Filter/Search**: (Future enhancement)
- **Statistics**: Total books, collections, countries

### Collection Pages

Collection-specific pages show:
- **Progress Tracking**: Digitalization status
- **Book List**: Detailed view of all books
- **Availability Status**: Shows which books have pages
- **Collection Stats**: Authors, years, genres

## Customization

### Templates

The system uses HTML templates from `shared_assets/templates/`:
- `book_page_template.html`: Base template for book pages
- Custom templates can be created and specified

### Styling

- **Tailwind CSS**: Utility-first styling via CDN
- **Custom Styles**: Inline styles for specific effects
- **Color Scheme**: Solarized-inspired palette
- **Typography**: Inter for body, Lora for headings

### Data Sources

Book pages pull data from:
1. `book.yaml`: Basic metadata, slides, configuration
2. `docs/review.md`: Research content, facts, quotes
3. `docs/README.md`: Additional documentation
4. Generated content: Prompts, images

## Best Practices

1. **Run Research First**
   ```bash
   python main.py research 17
   python main.py site 17
   ```
   Pages are richer with review.md content

2. **Batch Generation**
   ```bash
   python main.py site  # Generate everything
   ```

3. **Preview Locally**
   ```bash
   cd site
   python -m http.server 8000
   # Open http://localhost:8000
   ```

4. **Deploy to GitHub Pages**
   ```bash
   # Copy site/ contents to gh-pages branch
   # Or use GitHub Actions for automation
   ```

## Template Variables

Book page template supports these placeholders:

- `[BOOK_TITLE]` - Book title
- `[BOOK_TITLE_GENITIVE]` - Genitive form (Polish grammar)
- `[BOOK_EMOJI]` - Book's emoji icon
- `[AUTHOR_NAME]` - Author name
- `[AUTHOR_EMOJI]` - Author emoji
- `[HERO_DESCRIPTION]` - Hero section text
- `[AUTHOR_DESCRIPTION]` - Author section text
- `[SYMBOLS_DESCRIPTION]` - Symbols section text

JavaScript data objects:
- `timelineData` - Array of {year, event}
- `characterData` - Array of {id, name, emoji, color, description}

## Future Enhancements

- Search functionality across all books
- Tag-based filtering
- Reading progress tracking
- User annotations
- Social sharing
- PWA support for offline reading
- Multi-language support
- Integration with video content
- Analytics dashboard

## Troubleshooting

### "Template not found"
- Check `shared_assets/templates/` exists
- Verify template filename matches

### "Book not found"
- Ensure book.yaml exists in book directory
- Check book ID format (e.g., 0017_little_prince)

### Broken links
- Run full site generation to ensure all pages exist
- Check relative paths in templates

### Missing styles
- Ensure internet connection for Tailwind CDN
- Check browser console for CSS errors

## Development

To add a new generator:

```python
# src/site_generator/my_generator.py
from src.site_generator.base import BaseHtmlGenerator

class MyGenerator(BaseHtmlGenerator):
    def generate(self, **kwargs) -> Path:
        # Your implementation
        html = self.render_template('my_template.html', context)
        output_path = self.output_dir / 'my_page.html'
        # Save and return path
```

Register in site_builder.py and add CLI support.