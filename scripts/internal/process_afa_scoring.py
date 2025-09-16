#!/usr/bin/env python3
"""
Process AFA scoring - calculate DEPTH and HEAT from 8 dimension scores
Transforms raw scores into composite metrics and selects appropriate audio format
"""

import sys
import math
sys.path.append('./scripts/lib')
from afa_calculations import calculate_depth_heat_composites, select_format_from_matrix

def print_usage():
    """Print detailed usage information with examples"""
    print("""
AFA Scoring Processor - Calculate DEPTH×HEAT and Select Audio Format
====================================================================

USAGE:
    python process_afa_scoring.py <controversy> <philosophical_depth> <cultural_phenomenon>
                                  <contemporary_reception> <relevance> <innovation>
                                  <structural_complexity> <social_roles>

PARAMETERS (all required, in exact order):
    1. controversy              Score 0-10 or NA (scandals, bans, disputes)
    2. philosophical_depth      Score 0-10 or NA (interpretive layers, symbolism)
    3. cultural_phenomenon      Score 0-10 or NA (adaptations, cultural impact)
    4. contemporary_reception   Score 0-10 or NA (social media presence, virality)
    5. relevance               Score 0-10 or NA (contemporary significance)
    6. innovation              Score 0-10 or NA (literary breakthroughs)
    7. structural_complexity   Score 0-10 or NA (narrative architecture)
    8. social_roles            Score 0-10 or NA (social commentary, gender)

OUTPUT FORMAT:
    DEPTH|<value>|<category>|HEAT|<value>|<category>|FORMAT1|<name>|<duration>|<score>|FORMAT2|<name>|<duration>|<score>|FORMAT3|<name>|<duration>|<score>

EXAMPLE:
    python process_afa_scoring.py 8.0 9.0 5.0 2.0 8.0 9.0 7.0 7.0

    Output: DEPTH|8.4|high|HEAT|6.3|medium|FORMAT1|academic_analysis|17|9.21|FORMAT2|temporal_context|16|7.85|FORMAT3|social_perspective|14|6.12

SCORING NOTES:
    - Use 'NA' for dimensions that cannot be assessed (e.g., contemporary_reception for old books)
    - Scores should align with behavioral anchors (0, 2, 5, 7, 9, 10)
    - DEPTH formula: (philosophical_depth×1.5 + structural_complexity×1.2 + innovation×1.0) / 3.7
    - HEAT formula: (controversy×1.3 + cultural_phenomenon×1.0 + relevance×0.8 + contemporary_reception×0.5) / 3.6

FORMAT MATRIX:
    Low DEPTH + Low HEAT     → exploratory_dialogue (10 min)
    Low DEPTH + Medium HEAT  → cultural_dimension (11 min)
    Low DEPTH + High HEAT    → critical_debate (12 min)
    Medium DEPTH + Low HEAT  → emotional_perspective (13 min)
    Medium DEPTH + Medium HEAT → social_perspective (14 min)
    Medium DEPTH + High HEAT → narrative_reconstruction (15 min)
    High DEPTH + Low HEAT    → temporal_context (16 min)
    High DEPTH + Medium HEAT → academic_analysis (17 min)
    High DEPTH + High HEAT   → academic_analysis (18 min)
    """)

def main():
    # Check for help flag
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help', 'help']):
        print_usage()
        sys.exit(0)

    # Validate parameter count
    if len(sys.argv) != 9:
        print(f"\n❌ ERROR: Expected exactly 8 scores, but got {len(sys.argv) - 1} arguments\n")

        if len(sys.argv) > 1:
            print(f"Received: {' '.join(sys.argv[1:])}\n")

        print_usage()
        sys.exit(1)
    
    # Parse 8 scores from command line arguments with validation
    try:
        scores = {}
        score_names = [
            'controversy', 'philosophical_depth', 'cultural_phenomenon',
            'contemporary_reception', 'relevance', 'innovation',
            'structural_complexity', 'social_roles'
        ]

        for i, name in enumerate(score_names, 1):
            value = sys.argv[i]
            if value.upper() == 'NA':
                scores[name] = None
            else:
                try:
                    score = float(value)
                    if not (0 <= score <= 10):
                        print(f"\n❌ ERROR: Score for '{name}' must be between 0-10 (got {score})\n")
                        print_usage()
                        sys.exit(1)
                    scores[name] = score
                except ValueError:
                    print(f"\n❌ ERROR: Invalid value for '{name}': '{value}' (expected number 0-10 or 'NA')\n")
                    print_usage()
                    sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR: Failed to parse scores - {str(e)}\n")
        print_usage()
        sys.exit(1)
    
    # Create ai_response structure for the function
    ai_response = {
        'raw_scores': {
            key: {'value': value} for key, value in scores.items()
        }
    }
    
    # Calculate DEPTH and HEAT
    DEPTH, depth_category, HEAT, heat_category = calculate_depth_heat_composites(ai_response)

    # Get all possible formats and calculate their fitness scores
    all_formats = [
        "exploratory_dialogue", "academic_analysis", "cultural_dimension",
        "social_perspective", "critical_debate", "narrative_reconstruction",
        "temporal_context", "emotional_perspective"
    ]

    # Define format durations
    format_durations = {
        "exploratory_dialogue": 10,
        "cultural_dimension": 11,
        "critical_debate": 12,
        "emotional_perspective": 13,
        "social_perspective": 14,
        "narrative_reconstruction": 15,
        "temporal_context": 16,
        "academic_analysis": 17,
    }

    # Calculate distance from each format's ideal DEPTH/HEAT position
    format_ideal_positions = {
        "exploratory_dialogue": (2.5, 2.5),    # Low DEPTH, Low HEAT
        "cultural_dimension": (2.5, 5.5),      # Low DEPTH, Medium HEAT
        "critical_debate": (2.5, 8.5),         # Low DEPTH, High HEAT
        "emotional_perspective": (5.5, 2.5),   # Medium DEPTH, Low HEAT
        "social_perspective": (5.5, 5.5),      # Medium DEPTH, Medium HEAT
        "narrative_reconstruction": (5.5, 8.5), # Medium DEPTH, High HEAT
        "temporal_context": (8.5, 2.5),        # High DEPTH, Low HEAT
        "academic_analysis": (8.5, 5.5),       # High DEPTH, Medium HEAT
    }

    # Calculate fitness scores for all formats
    format_scores = []
    for format_name in all_formats:
        ideal_depth, ideal_heat = format_ideal_positions[format_name]
        # Euclidean distance
        distance = math.sqrt((DEPTH - ideal_depth)**2 + (HEAT - ideal_heat)**2)
        # Convert distance to score (lower distance = higher score)
        score = 10.0 / (1.0 + distance)
        format_scores.append({
            "name": format_name,
            "duration": format_durations[format_name],
            "score": score,
            "distance": distance
        })

    # Sort by score (descending) to get top 3
    format_scores.sort(key=lambda x: x["score"], reverse=True)
    top_3 = format_scores[:3]

    # Output top 3 formats
    print(f"DEPTH|{DEPTH:.1f}|{depth_category}|HEAT|{HEAT:.1f}|{heat_category}", end="")
    for i, fmt in enumerate(top_3, 1):
        print(f"|FORMAT{i}|{fmt['name']}|{fmt['duration']}|{fmt['score']:.2f}", end="")
    print()  # Final newline

if __name__ == "__main__":
    main()
