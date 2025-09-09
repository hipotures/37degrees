#!/usr/bin/env python3
import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_afa_file(filepath):
    """Analyze a single AFA file for completeness and format."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {
        'file': filepath.name,
        'book_id': filepath.name.split('_')[0],
        'format': None,
        'duration': None,
        'has_prompts': False,
        'has_key_threads': False,
        'has_metadata': False,
        'has_scoring': False,
        'is_complete': False,
        'issues': []
    }
    
    # Extract format
    format_match = re.search(r'\*\*Główny\*\*:\s*([^—]+)\s*—', content)
    if format_match:
        result['format'] = format_match.group(1).strip()
    else:
        result['issues'].append('Missing format')
    
    # Extract duration
    duration_match = re.search(r'\*\*Długość\*\*:\s*(\d+)\s*min', content)
    if duration_match:
        result['duration'] = int(duration_match.group(1))
    else:
        result['issues'].append('Missing duration')
    
    # Check for prompts A/B
    if '### Prowadzący A' in content and '### Prowadzący B' in content:
        result['has_prompts'] = True
    else:
        result['issues'].append('Missing prompts A/B')
    
    # Check for key threads
    if '## KLUCZOWE WĄTKI Z WIARYGODNOŚCIĄ' in content:
        result['has_key_threads'] = True
    else:
        result['issues'].append('Missing key threads')
    
    # Check for metadata
    if '## METRYKA DZIEŁA' in content:
        result['has_metadata'] = True
    else:
        result['issues'].append('Missing metadata')
    
    # Check for scoring
    if 'SUMA:' in content and 'Percentyl:' in content:
        result['has_scoring'] = True
    else:
        result['issues'].append('Missing scoring')
    
    # Check completeness
    result['is_complete'] = (
        result['format'] and 
        result['duration'] and 
        result['has_prompts'] and 
        result['has_key_threads'] and 
        result['has_metadata'] and 
        result['has_scoring']
    )
    
    return result

def main():
    # Find all AFA files for books 0001-0036
    afa_files = []
    books_dir = Path('/home/xai/DEV/37degrees/books')
    
    for i in range(1, 37):
        book_pattern = f"{i:04d}_*"
        for book_dir in books_dir.glob(book_pattern):
            afa_path = book_dir / 'docs' / f"{book_dir.name}-afa.md"
            if afa_path.exists():
                afa_files.append(afa_path)
    
    # Analyze all files
    results = []
    format_counts = defaultdict(int)
    missing_books = []
    
    # Check for missing books
    found_books = set()
    for f in afa_files:
        book_id = f.parent.parent.name.split('_')[0]
        found_books.add(int(book_id))
    
    for i in range(1, 37):
        if i not in found_books:
            missing_books.append(f"{i:04d}")
    
    # Analyze each file
    for filepath in sorted(afa_files):
        result = analyze_afa_file(filepath)
        results.append(result)
        if result['format']:
            format_counts[result['format']] += 1
    
    # Print results
    print("=" * 80)
    print("AFA FILES ANALYSIS REPORT (Books 0001-0036)")
    print("=" * 80)
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"Total books expected: 36")
    print(f"AFA files found: {len(results)}")
    print(f"Missing AFA files: {len(missing_books)}")
    
    if missing_books:
        print(f"\n❌ MISSING FILES:")
        for book_id in missing_books:
            print(f"  - Book {book_id}")
    
    print(f"\n📋 FORMAT DISTRIBUTION:")
    for format_name, count in sorted(format_counts.items(), key=lambda x: -x[1]):
        percentage = (count / len(results)) * 100
        print(f"  {format_name}: {count} ({percentage:.1f}%)")
    
    # Check for incomplete files
    incomplete = [r for r in results if not r['is_complete']]
    if incomplete:
        print(f"\n⚠️  INCOMPLETE FILES ({len(incomplete)}):")
        for r in incomplete:
            print(f"\n  {r['file']}:")
            for issue in r['issues']:
                print(f"    - {issue}")
    else:
        print(f"\n✅ ALL FILES COMPLETE!")
    
    # Duration statistics
    durations = [r['duration'] for r in results if r['duration']]
    if durations:
        print(f"\n⏱️  DURATION STATISTICS:")
        print(f"  Average: {sum(durations)/len(durations):.1f} min")
        print(f"  Min: {min(durations)} min")
        print(f"  Max: {max(durations)} min")
    
    # Detailed table
    print(f"\n📊 DETAILED TABLE:")
    print(f"{'Book ID':<8} {'Format':<30} {'Duration':<10} {'Complete':<10}")
    print("-" * 60)
    for r in sorted(results, key=lambda x: x['book_id']):
        format_str = r['format'][:28] + ".." if r['format'] and len(r['format']) > 30 else (r['format'] or 'N/A')
        duration_str = f"{r['duration']} min" if r['duration'] else 'N/A'
        complete_str = '✅' if r['is_complete'] else '❌'
        print(f"{r['book_id']:<8} {format_str:<30} {duration_str:<10} {complete_str:<10}")

if __name__ == '__main__':
    main()