#!/usr/bin/env python3
"""
Analyze AFA format distribution across all book.yaml files
Shows statistics for audio format selection
"""

import yaml
from pathlib import Path
from collections import defaultdict
import json

def analyze_books():
    """Analyze all book.yaml files for AFA format distribution"""

    books_dir = Path('/home/xai/DEV/37degrees/books')
    format_counts = defaultdict(int)
    books_with_afa = []
    books_without_afa = []
    total_books = 0

    # Define all possible formats
    all_formats = [
        "academic_analysis",
        "critical_debate",
        "temporal_context",
        "cultural_dimension",
        "social_perspective",
        "emotional_perspective",
        "exploratory_dialogue",
        "narrative_reconstruction"
    ]

    # Initialize counts
    for fmt in all_formats:
        format_counts[fmt] = 0

    # Scan all book directories
    for book_dir in sorted(books_dir.glob('[0-9]*')):
        if not book_dir.is_dir():
            continue

        book_yaml = book_dir / 'book.yaml'
        if not book_yaml.exists():
            continue

        total_books += 1
        book_id = book_dir.name

        try:
            with open(book_yaml, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if 'afa_analysis' in data and 'formats' in data['afa_analysis']:
                formats = data['afa_analysis']['formats']
                if formats:
                    format_name = list(formats.keys())[0]
                    format_counts[format_name] += 1
                    books_with_afa.append((book_id, format_name))
                else:
                    books_without_afa.append(book_id)
            else:
                books_without_afa.append(book_id)

        except Exception as e:
            print(f"Error reading {book_yaml}: {e}")
            books_without_afa.append(book_id)

    # Print results
    print("=" * 80)
    print("AFA FORMAT DISTRIBUTION ANALYSIS")
    print("=" * 80)

    print(f"\n📊 OVERALL STATISTICS:")
    print(f"Total books scanned: {total_books}")
    print(f"Books with AFA analysis: {len(books_with_afa)}")
    print(f"Books without AFA analysis: {len(books_without_afa)}")

    print(f"\n📋 FORMAT DISTRIBUTION:")
    print(f"{'Format':<30} {'Count':<10} {'Percentage':<10} {'Usage'}")
    print("-" * 70)

    for fmt in all_formats:
        count = format_counts[fmt]
        if len(books_with_afa) > 0:
            percentage = (count / len(books_with_afa)) * 100
        else:
            percentage = 0

        # Visual bar
        bar_length = int(count * 2)
        bar = "█" * bar_length

        print(f"{fmt:<30} {count:<10} {percentage:>6.1f}%     {bar}")

    print(f"\n📚 BOOKS WITH AFA ANALYSIS ({len(books_with_afa)}):")
    for book_id, format_name in sorted(books_with_afa):
        title = book_id.split('_', 1)[1] if '_' in book_id else book_id
        print(f"  {book_id:<30} → {format_name}")

    # if books_without_afa:
    #     print(f"\n❌ BOOKS WITHOUT AFA ANALYSIS ({len(books_without_afa)}):")
    #     for book_id in sorted(books_without_afa):
    #         print(f"  - {book_id}")

    # Save to JSON
    output = {
        "total_books": total_books,
        "books_with_afa": len(books_with_afa),
        "format_counts": dict(format_counts),
        "books_list": [{"book": b, "format": f} for b, f in books_with_afa]
    }

    output_path = Path('/home/xai/DEV/37degrees/output/afa_distribution_report.json')
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Report saved to: {output_path}")

    # Update the main counts file
    counts_data = {
        "counts": dict(format_counts),
        "books_since_last": {}  # Would need more logic to track this
    }

    counts_path = Path('/home/xai/DEV/37degrees/output/afa_format_counts.json')
    with open(counts_path, 'w') as f:
        json.dump(counts_data, f, indent=2)

    print(f"💾 Counts updated in: {counts_path}")

if __name__ == "__main__":
    analyze_books()