#!/usr/bin/env python3
"""
Test AI Format Selector on problematic books
"""

import sys
from pathlib import Path
import json

sys.path.append('scripts/lib')
from afa_ai_selector import select_format_with_ai, prepare_ai_context

def test_book(book_id: str, book_name: str, expected_issues: str):
    """Test format selection for a specific book"""
    print(f"\n{'='*60}")
    print(f"Testing: {book_name} ({book_id})")
    print(f"Known issue: {expected_issues}")
    print("-"*60)

    book_dir = Path(f"books/{book_id}")
    if not book_dir.exists():
        print(f"ERROR: Book directory not found: {book_dir}")
        return None

    # Get context
    context = prepare_ai_context(book_dir)

    # Print key info
    print(f"Genre: {context['book']['genre']}")
    print(f"DEPTH: {context['scores']['depth'].get('value', 'N/A')} ({context['scores']['depth'].get('category', 'N/A')})")
    print(f"HEAT: {context['scores']['heat'].get('value', 'N/A')} ({context['scores']['heat'].get('category', 'N/A')})")
    print(f"Structural Complexity: {context['scores']['raw'].get('structural_complexity', 'N/A')}")

    # Get current format from book.yaml
    from afa_ai_selector import load_book_data
    book_data = load_book_data(book_dir)
    current_format = None
    if 'afa_analysis' in book_data and 'formats' in book_data['afa_analysis']:
        formats = book_data['afa_analysis']['formats']
        if isinstance(formats, dict):
            current_format = formats.get('name')
        elif isinstance(formats, list) and len(formats) > 0:
            current_format = formats[0].get('name')

    print(f"Current format: {current_format}")

    # Test AI selection (with mock for now)
    result = select_format_with_ai(book_dir)

    print(f"\nAI Selected: {result['selected_format']}")
    print(f"Confidence: {result.get('confidence', 'N/A')}")
    print(f"Reasoning: {result.get('primary_reasoning', 'N/A')}")

    # Evaluate if it's better
    is_better = False
    if book_id == "0037_wuthering_heights":
        # Should NOT be academic_analysis
        is_better = result['selected_format'] != 'academic_analysis'
    elif book_id in ["0001_alice_in_wonderland", "0017_little_prince", "0013_hobbit"]:
        # Children's books should NOT be academic_analysis
        is_better = result['selected_format'] in ['exploratory_dialogue', 'narrative_reconstruction', 'emotional_perspective']

    print(f"Improvement: {'✓ YES' if is_better else '✗ NO'}")

    return {
        'book': book_name,
        'current': current_format,
        'selected': result['selected_format'],
        'improved': is_better
    }

def main():
    """Test problematic books"""
    print("="*60)
    print("AI FORMAT SELECTOR TEST")
    print("Testing books with known inappropriate format assignments")
    print("="*60)

    test_cases = [
        ("0037_wuthering_heights", "Wuthering Heights", "Gothic romance assigned academic_analysis"),
        ("0001_alice_in_wonderland", "Alice in Wonderland", "Children's book assigned academic_analysis"),
        ("0017_little_prince", "Little Prince", "Children's fable assigned academic_analysis"),
        ("0013_hobbit", "The Hobbit", "Children's adventure assigned temporal_context (actually OK)"),
        ("0014_jane_eyre", "Jane Eyre", "Gothic romance assigned academic_analysis"),
    ]

    results = []
    for book_id, name, issue in test_cases:
        result = test_book(book_id, name, issue)
        if result:
            results.append(result)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    improvements = sum(1 for r in results if r['improved'])
    print(f"Improved selections: {improvements}/{len(results)}")

    print("\nFormat changes:")
    for r in results:
        status = "✓" if r['improved'] else "✗"
        print(f"{status} {r['book']}: {r['current']} → {r['selected']}")

    # Check diversity
    print("\nFormat diversity check:")
    selected_formats = [r['selected'] for r in results]
    unique_formats = set(selected_formats)
    print(f"Unique formats selected: {len(unique_formats)} ({', '.join(unique_formats)})")

    # Note about mock responses
    print("\n" + "="*60)
    print("NOTE: Currently using mock AI responses for testing.")
    print("Real implementation would use actual LLM with full context.")
    print("="*60)

if __name__ == "__main__":
    main()