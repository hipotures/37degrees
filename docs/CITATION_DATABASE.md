# Citation Database System

## Overview

The 37degrees project now includes a SQLite citation database system for managing research references. Each book has its own `book.db` file that stores all citations, tracks their usage, and enables clean reference formatting using `[url=ID]` syntax.

## Database Structure

### Location
- **File**: `books/NNNN_book_name/book.db`
- Created automatically when generating research content

### Tables

#### 1. `citations`
Stores all citation references:

```sql
CREATE TABLE citations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    title TEXT,
    date TEXT,              -- Publication date
    last_updated TEXT,      -- Last update from source
    provider TEXT NOT NULL, -- 'perplexity', 'google', etc.
    topic TEXT,            -- Research topic category
    relevance_score REAL,
    added_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    accessed_at TEXT,
    domain TEXT,           -- Extracted domain
    language TEXT DEFAULT 'pl',
    is_active INTEGER DEFAULT 1,
    UNIQUE(provider, url)
);
```

#### 2. `research_sessions`
Tracks research generation sessions:

```sql
CREATE TABLE research_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    book_title TEXT,
    author TEXT,
    topics_researched TEXT,  -- JSON array
    total_citations INTEGER DEFAULT 0,
    metadata TEXT           -- JSON metadata
);
```

#### 3. `citation_usage`
Tracks where citations are used:

```sql
CREATE TABLE citation_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    citation_id INTEGER NOT NULL,
    session_id INTEGER,
    context TEXT,
    position INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (citation_id) REFERENCES citations(id),
    FOREIGN KEY (session_id) REFERENCES research_sessions(id)
);
```

## Citation Format

### In review.md

Instead of inline URLs:
```markdown
Książka została przetłumaczona [Źródło](https://example.com)
```

Use citation IDs:
```markdown
Książka została przetłumaczona [url=4]
```

### Inline citations
```markdown
Najnowsza adaptacja z 2025 roku [url=45] zdobyła wiele nagród.
```

### Bibliography Section

At the end of review.md:
```markdown
### 📚 Bibliografia

[1] https://example.com - "Title of page" (2024-01-15)
[2] https://example2.com - "Another title"
[45] https://example3.com - "Film adaptation info" (2025-07-01)
```

## Usage Examples

### Query Citations

```python
from src.research.citation_db import CitationDatabase
from pathlib import Path

# Initialize database
book_path = Path("books/0001_alice_in_wonderland/book.yaml")
db = CitationDatabase(book_path)

# Get all citations
citations = db.get_all_citations()

# Get citations by topic
symbolism_citations = db.get_citations_by_topic("symbolika")

# Get specific citation
citation = db.get_citation_by_id(45)
```

### Export Citations

```python
# Export as Markdown bibliography
markdown_bib = db.export_citations(format="markdown")

# Export as BibTeX
bibtex = db.export_citations(format="bibtex")

# Export as JSON
json_data = db.export_citations(format="json")
```

### Citation Statistics

```python
stats = db.get_citation_stats()
print(f"Total citations: {stats['total']}")
print(f"By provider: {stats['by_provider']}")
print(f"By topic: {stats['by_topic']}")
print(f"Top domains: {stats['top_domains']}")
```

## Command Line Usage

### View Citations
```bash
# Count citations
sqlite3 books/0001_alice_in_wonderland/book.db "SELECT COUNT(*) FROM citations;"

# List citations by topic
sqlite3 books/0001_alice_in_wonderland/book.db \
  "SELECT id, url, title FROM citations WHERE topic='adaptacje';"

# View research sessions
sqlite3 books/0001_alice_in_wonderland/book.db \
  "SELECT * FROM research_sessions;"
```

### Export Bibliography
```bash
# Export to file
sqlite3 books/0001_alice_in_wonderland/book.db \
  "SELECT '[' || id || '] ' || url || ' - \"' || 
   COALESCE(title, domain) || '\"' || 
   CASE WHEN date IS NOT NULL THEN ' (' || date || ')' ELSE '' END
   FROM citations ORDER BY id;" > bibliography.txt
```

## Benefits

1. **Clean Markdown**: Review files are more readable without long URLs
2. **Deduplication**: Same URL won't be stored multiple times per provider
3. **Analytics**: Track most cited sources, domains, topics
4. **Persistence**: Citations preserved even if external URLs change
5. **Export Options**: Generate bibliographies in various formats
6. **Version Control**: Smaller review.md files, better diffs

## Migration

For existing review.md files with inline URLs:

```python
# Future feature: Migration script
python scripts/migrate_citations.py books/0001_alice_in_wonderland
```

This will:
1. Parse existing review.md
2. Extract all URLs
3. Create citation database
4. Replace URLs with [url=ID]
5. Add bibliography section

## Technical Details

### Unique Constraint
- Citations are unique per (provider, url) combination
- Same URL can exist for different providers
- Prevents duplicate entries within same provider

### Local Time
- All timestamps use local time via `datetime('now', 'localtime')`
- Ensures correct timezone handling

### Domain Extraction
- Automatically extracts domain from URL
- Used for grouping and analytics
- Helps identify most cited sources

## Future Enhancements

1. **URL Validation**: Periodic checking of citation validity
2. **Alternative Sources**: Find replacements for dead links
3. **Cross-Book Analysis**: Compare citations across books
4. **Citation Networks**: Visualize citation relationships
5. **Auto-Migration**: Automatic migration of existing reviews
6. **Web Interface**: Browse citations through static site