#!/usr/bin/env python3
import os
import re
from pathlib import Path
from collections import defaultdict

def normalize_format(format_name):
    """Normalize format name to handle inconsistent capitalization."""
    if not format_name:
        return None
    
    # Remove asterisks and extra whitespace
    clean = format_name.strip().replace('**', '').strip()
    
    # Normalize to title case for consistency
    format_map = {
        'przyjacielska wymiana': 'Przyjacielska wymiana',
        'wykład filologiczny': 'Wykład filologiczny',
        'wykład filologiczny w duecie': 'Wykład filologiczny w duecie',
        'mistrz i uczeń': 'Mistrz i Uczeń',
    }
    
    lower = clean.lower()
    return format_map.get(lower, clean)

def main():
    # Find all AFA files
    afa_files = []
    books_dir = Path('/home/xai/DEV/37degrees/books')
    
    for i in range(1, 37):
        book_pattern = f"{i:04d}_*"
        for book_dir in books_dir.glob(book_pattern):
            afa_path = book_dir / 'docs' / f"{book_dir.name}-afa.md"
            if afa_path.exists():
                afa_files.append(afa_path)
    
    # Analyze formats
    format_counts = defaultdict(int)
    format_details = defaultdict(list)
    missing_books = []
    
    # Check for missing books
    found_books = set()
    for f in afa_files:
        book_id = f.parent.parent.name.split('_')[0]
        found_books.add(int(book_id))
    
    for i in range(1, 37):
        if i not in found_books:
            missing_books.append(f"{i:04d}")
    
    # Extract formats
    for filepath in sorted(afa_files):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        book_name = filepath.parent.parent.name
        book_id = book_name.split('_')[0]
        
        # Try multiple patterns to find format
        format_match = None
        patterns = [
            r'\*\*Główny\*\*:\s*([^—]+)\s*—',
            r'- \*\*Główny\*\*:\s*([^—]+)\s*—',
            r'Główny:\s*([^—]+)\s*—',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                format_match = match
                break
        
        if format_match:
            raw_format = format_match.group(1).strip()
            normalized = normalize_format(raw_format)
            if normalized:
                format_counts[normalized] += 1
                format_details[normalized].append(book_name)
        else:
            # Special case for Little Prince
            if 'MISTRZ I UCZEŃ' in content:
                format_counts['Mistrz i Uczeń'] += 1
                format_details['Mistrz i Uczeń'].append(book_name)
    
    # Print results
    print("=" * 80)
    print("AFA FORMAT DISTRIBUTION ANALYSIS (Books 0001-0036)")
    print("=" * 80)
    
    print(f"\n📊 SUMMARY:")
    print(f"Total books analyzed: {sum(format_counts.values())}")
    print(f"Missing AFA files: {len(missing_books)} (Book {', '.join(missing_books)})")
    
    print(f"\n📚 FORMAT DISTRIBUTION (NORMALIZED):")
    print("-" * 60)
    
    total = sum(format_counts.values())
    for format_name, count in sorted(format_counts.items(), key=lambda x: -x[1]):
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"\n📖 {format_name}: {count} książek ({percentage:.1f}%)")
        print("   Książki:")
        for book in sorted(format_details[format_name])[:5]:  # Show first 5
            title = book.split('_', 1)[1] if '_' in book else book
            print(f"   • {title}")
        if len(format_details[format_name]) > 5:
            print(f"   ... i {len(format_details[format_name]) - 5} więcej")
    
    print("\n" + "=" * 80)
    print("🎯 PODSUMOWANIE:")
    print(f"• Dominujący format: Przyjacielska wymiana ({format_counts.get('Przyjacielska wymiana', 0)} książek)")
    print(f"• Format akademicki: Wykład filologiczny ({format_counts.get('Wykład filologiczny', 0) + format_counts.get('Wykład filologiczny w duecie', 0)} książek)")
    print(f"• Format edukacyjny: Mistrz i Uczeń ({format_counts.get('Mistrz i Uczeń', 0)} książek)")
    print(f"• Brakujący plik: Don Quixote (0006)")

if __name__ == '__main__':
    main()