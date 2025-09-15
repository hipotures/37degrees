#!/usr/bin/env python3
"""
Test script for new AFA balancing algorithm
Tests on existing 36 books to compare old vs new selections
"""

import sys
import json
import yaml
import glob
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

sys.path.append('./scripts/lib')
from afa_calculations import calculate_depth_heat_composites

# Extended CANDIDATES matrix with underused formats in more cells
CANDIDATES_NEW = {
    ("low", "low"): [
        {"name": "exploratory_dialogue", "duration": 8},
        {"name": "emotional_perspective", "duration": 11},  # Added alternative
    ],
    ("low", "medium"): [
        {"name": "narrative_reconstruction", "duration": 10},
        {"name": "exploratory_dialogue", "duration": 8},  # Added as option
    ],
    ("low", "high"): [
        {"name": "critical_debate", "duration": 12},
        {"name": "narrative_reconstruction", "duration": 10},  # Added alternative
    ],
    ("medium", "low"): [
        {"name": "emotional_perspective", "duration": 11},
        {"name": "narrative_reconstruction", "duration": 10},  # Added alternative
    ],
    ("medium", "medium"): [
        {"name": "temporal_context", "duration": 13},
        {"name": "exploratory_dialogue", "duration": 8},  # Added for variety
    ],
    ("medium", "high"): [
        {"name": "social_perspective", "duration": 14},
        {"name": "critical_debate", "duration": 12},
        {"name": "narrative_reconstruction", "duration": 10},  # NEW
    ],
    ("high", "low"): [
        {"name": "academic_analysis", "duration": 15},
        {"name": "temporal_context", "duration": 13},
        {"name": "emotional_perspective", "duration": 11},  # Added
    ],
    ("high", "medium"): [
        {"name": "cultural_dimension", "duration": 16},
        {"name": "academic_analysis", "duration": 15},
        {"name": "exploratory_dialogue", "duration": 8},  # NEW for accessible scholarship
    ],
    ("high", "high"): [
        {"name": "academic_analysis", "duration": 18},
        {"name": "cultural_dimension", "duration": 16},
        {"name": "social_perspective", "duration": 14},
        {"name": "critical_debate", "duration": 12},
        {"name": "exploratory_dialogue", "duration": 8},  # Added even here
    ],
}

def calculate_frequency_penalty(format_name: str, counters: Dict, total_books: int = 36) -> float:
    """
    Penalizuje nadużywane formaty używając krzywej logarytmicznej
    """
    count = counters.get(format_name, 0)
    if total_books == 0:
        return 0.0
    usage_rate = count / total_books

    if usage_rate == 0:
        return -2.0  # Maksymalny bonus dla nieużywanych
    elif usage_rate < 0.05:  # < 5%
        return -1.0  # Duży bonus dla bardzo rzadko używanych
    elif usage_rate < 0.1:  # 5-10%
        return -0.5  # Bonus dla rzadko używanych
    elif usage_rate < 0.2:  # 10-20%
        return 0.0   # Neutralny
    else:  # > 20%
        # Progresywna kara dla nadużywanych
        return math.log(usage_rate * 5) * 2.0

def calculate_staleness_bonus(format_name: str, books_since_last: Dict) -> float:
    """
    Bonus za formaty długo nieużywane
    """
    books_since = books_since_last.get(format_name, 36)

    if books_since >= 15:
        return 1.5  # Bardzo duży bonus
    elif books_since >= 10:
        return 1.0  # Duży bonus
    elif books_since >= 5:
        return 0.5
    else:
        return 0.0

def calculate_compatibility_score(format_name: str, ai_scores: Dict) -> float:
    """
    Ocenia jak dobrze format pasuje do charakterystyki książki
    """
    # Get scores safely
    def get_score(key):
        val = ai_scores.get(key, {}).get("value", 0)
        return float(val) if val is not None else 0.0

    controversy = get_score("controversy")
    philosophical = get_score("philosophical_depth")
    cultural = get_score("cultural_phenomenon")
    contemporary = get_score("contemporary_reception")
    relevance = get_score("relevance")
    innovation = get_score("innovation")
    structural = get_score("structural_complexity")
    social = get_score("social_roles")

    score = 0.0

    if format_name == "exploratory_dialogue":
        # Prefers accessible, less complex books
        if structural < 5:
            score += 1.0
        if philosophical < 6:
            score += 0.5
        if controversy < 5:
            score += 0.5
        if philosophical > 8:
            score -= 1.0  # Too complex

    elif format_name == "academic_analysis":
        # Prefers complex, philosophical books
        if philosophical > 7:
            score += 1.5
        if structural > 7:
            score += 1.0
        if innovation > 7:
            score += 0.5
        if philosophical < 5:
            score -= 1.0  # Too simple

    elif format_name == "narrative_reconstruction":
        # Prefers story-driven, culturally significant books
        if cultural > 7:
            score += 1.0
        if structural > 5:
            score += 0.5
        if contemporary > 5:
            score += 0.5
        if structural < 3:
            score -= 1.0  # Too simple narrative

    elif format_name == "emotional_perspective":
        # Prefers emotionally resonant books
        if relevance > 7:
            score += 1.0
        if social > 5:
            score += 0.5
        if controversy < 8:
            score += 0.5  # Not too controversial

    elif format_name == "critical_debate":
        # Prefers controversial books
        if controversy > 7:
            score += 1.5
        if social > 6:
            score += 0.5
        if controversy < 4:
            score -= 1.0  # Not controversial enough

    elif format_name == "cultural_dimension":
        # Prefers culturally significant books
        if cultural > 7:
            score += 1.5
        if contemporary > 6:
            score += 0.5
        if cultural < 5:
            score -= 1.0

    elif format_name == "social_perspective":
        # Prefers socially relevant books
        if social > 6:
            score += 1.0
        if controversy > 5:
            score += 0.5
        if relevance > 6:
            score += 0.5

    elif format_name == "temporal_context":
        # Works well for classics with modern relevance
        if relevance > 6:
            score += 1.0
        if cultural > 6:
            score += 0.5

    return score

def select_format_with_smart_balancing(
    depth_cat: str,
    heat_cat: str,
    ai_scores: Dict,
    counters: Dict,
    books_since_last: Dict,
    book_num: int
) -> Tuple[str, Dict[str, float]]:
    """
    New smart balancing algorithm
    Returns: (selected_format_name, scores_breakdown)
    """
    candidates = CANDIDATES_NEW.get((depth_cat, heat_cat), [])

    if not candidates:
        return "academic_analysis", {}

    scores = {}
    breakdowns = {}

    for format in candidates:
        format_name = format["name"]
        base_score = 10.0

        # 1. Compatibility Score (weight: 40%)
        cs = calculate_compatibility_score(format_name, ai_scores) * 4.0

        # 2. Frequency Penalty (weight: 50% → stronger balancing)
        fps = calculate_frequency_penalty(format_name, counters, book_num) * 5.0

        # 3. Staleness Bonus (weight: 25% → slightly stronger)
        sb = calculate_staleness_bonus(format_name, books_since_last) * 2.5

        # Total score
        total = base_score + cs - fps + sb

        # Threshold check - don't force completely incompatible
        if cs < -3.0:  # Very poor match
            total = total * 0.5  # Significant reduction, but not elimination

        scores[format_name] = total
        breakdowns[format_name] = {
            "base": base_score,
            "compatibility": cs,
            "frequency_penalty": fps,
            "staleness_bonus": sb,
            "total": total
        }

    # Select format with highest score
    best_format = max(scores.items(), key=lambda x: x[1])[0]

    return best_format, breakdowns

def test_on_existing_books():
    """Test new algorithm on all 36 existing books"""

    # Initialize counters
    old_selections = {}
    new_selections = {}
    new_counters = {
        "academic_analysis": 0,
        "critical_debate": 0,
        "temporal_context": 0,
        "cultural_dimension": 0,
        "social_perspective": 0,
        "emotional_perspective": 0,
        "exploratory_dialogue": 0,
        "narrative_reconstruction": 0
    }
    books_since_last = {fmt: 36 for fmt in new_counters.keys()}

    # Find all book.yaml files
    book_files = []
    for i in range(1, 37):
        pattern = f"/home/xai/DEV/37degrees/books/{i:04d}_*/book.yaml"
        files = glob.glob(pattern)
        book_files.extend(files)

    book_files.sort()

    print("=" * 80)
    print("TESTING NEW AFA BALANCING ALGORITHM ON 36 BOOKS")
    print("=" * 80)

    for idx, book_file in enumerate(book_files, 1):
        book_name = Path(book_file).parent.name

        try:
            with open(book_file, 'r') as f:
                data = yaml.safe_load(f)

            # Get old selection
            old_format = None
            if 'afa_analysis' in data and 'formats' in data['afa_analysis']:
                old_format = list(data['afa_analysis']['formats'].keys())[0]
                old_selections[book_name] = old_format

            # Get scores for new calculation
            if 'afa_analysis' in data and 'scores' in data['afa_analysis']:
                scores = data['afa_analysis']['scores']

                # Create ai_response structure
                ai_response = {
                    'raw_scores': {
                        key: {'value': value} for key, value in scores.items()
                        if key not in ['total', 'percentile']
                    }
                }

                # Calculate DEPTH and HEAT
                DEPTH, depth_cat, HEAT, heat_cat = calculate_depth_heat_composites(ai_response)

                # Test new algorithm
                new_format, breakdown = select_format_with_smart_balancing(
                    depth_cat, heat_cat,
                    ai_response['raw_scores'],
                    new_counters,
                    books_since_last,
                    idx
                )

                new_selections[book_name] = new_format

                # Update counters for next iteration
                new_counters[new_format] += 1
                for fmt in books_since_last:
                    if fmt == new_format:
                        books_since_last[fmt] = 0
                    else:
                        books_since_last[fmt] += 1

                # Print comparison
                if old_format != new_format:
                    print(f"\n{idx:2d}. {book_name[:30]:30s}")
                    print(f"    DEPTH: {DEPTH:.1f} ({depth_cat:6s}) | HEAT: {HEAT:.1f} ({heat_cat:6s})")
                    print(f"    OLD: {old_format:25s} NEW: {new_format:25s} ✨ CHANGED")
                    print(f"    Scores: ", end="")
                    for fmt, bd in sorted(breakdown.items(), key=lambda x: x[1]['total'], reverse=True)[:3]:
                        print(f"{fmt}={bd['total']:.1f} ", end="")

        except Exception as e:
            print(f"Error processing {book_name}: {e}")

    # Summary statistics
    print("\n" + "=" * 80)
    print("DISTRIBUTION COMPARISON")
    print("=" * 80)

    print("\nOLD DISTRIBUTION (Actual):")
    old_counts = {}
    for fmt in old_selections.values():
        old_counts[fmt] = old_counts.get(fmt, 0) + 1

    for fmt, count in sorted(old_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / 36) * 100
        bar = "█" * count + "░" * (10 - min(count, 10))
        print(f"  {fmt:28s} {count:2d} ({pct:5.1f}%) {bar}")

    print("\nNEW DISTRIBUTION (Simulated):")
    for fmt, count in sorted(new_counters.items(), key=lambda x: x[1], reverse=True):
        pct = (count / 36) * 100
        bar = "█" * count + "░" * (10 - min(count, 10))
        status = "✅" if count > 0 else "❌"
        print(f"  {fmt:28s} {count:2d} ({pct:5.1f}%) {bar} {status}")

    # Calculate improvement metrics
    old_zero_formats = sum(1 for fmt in ["exploratory_dialogue", "narrative_reconstruction",
                                          "emotional_perspective", "academic_analysis",
                                          "critical_debate", "temporal_context",
                                          "cultural_dimension", "social_perspective"]
                           if old_counts.get(fmt, 0) == 0)
    new_zero_formats = sum(1 for count in new_counters.values() if count == 0)

    old_max = max(old_counts.values()) if old_counts else 0
    old_min = min(old_counts.values()) if old_counts else 0
    new_max = max(new_counters.values())
    new_min = min(new_counters.values())

    print("\n" + "=" * 80)
    print("IMPROVEMENT METRICS")
    print("=" * 80)
    print(f"Unused formats:      OLD: {old_zero_formats} → NEW: {new_zero_formats}")
    print(f"Max usage:           OLD: {old_max} → NEW: {new_max}")
    print(f"Min usage:           OLD: {old_min} → NEW: {new_min}")
    print(f"Range (max-min):     OLD: {old_max-old_min} → NEW: {new_max-new_min}")
    print(f"Balance improved:    {'YES ✅' if (new_max-new_min) < (old_max-old_min) else 'NO ❌'}")

    # Which books would get the biggest changes?
    changes = 0
    for book in old_selections:
        if book in new_selections and old_selections[book] != new_selections[book]:
            changes += 1

    print(f"\nTotal changes:       {changes}/36 books ({(changes/36)*100:.1f}%)")

if __name__ == "__main__":
    test_on_existing_books()
