#!/usr/bin/env python3
"""
Process AFA scoring - calculate DEPTH and HEAT from 8 scores
Usage: python scripts/internal/process_afa_scoring.py <8 scores>
Output: DEPTH|9.2|high|HEAT|8.2|high|FORMAT|academic_analysis|18
"""

import sys
sys.path.append('./scripts/lib')
from afa_calculations import calculate_depth_heat_composites, select_format_from_matrix

def main():
    if len(sys.argv) != 9:
        print("ERROR: Need exactly 8 scores")
        sys.exit(1)
    
    # Parse 8 scores from command line arguments
    scores = {
        'controversy': float(sys.argv[1]),
        'philosophical_depth': float(sys.argv[2]),
        'cultural_phenomenon': float(sys.argv[3]),
        'contemporary_reception': float(sys.argv[4]) if sys.argv[4] != 'NA' else None,
        'relevance': float(sys.argv[5]),
        'innovation': float(sys.argv[6]),
        'structural_complexity': float(sys.argv[7]),
        'social_roles': float(sys.argv[8])
    }
    
    # Create ai_response structure for the function
    ai_response = {
        'raw_scores': {
            key: {'value': value} for key, value in scores.items()
        }
    }
    
    # Calculate DEPTH and HEAT
    DEPTH, depth_category, HEAT, heat_category = calculate_depth_heat_composites(ai_response)
    
    # Select format from matrix
    selected_format = select_format_from_matrix(depth_category, heat_category)
    
    # Output in simple format for agent to parse
    print(f"DEPTH|{DEPTH:.1f}|{depth_category}|HEAT|{HEAT:.1f}|{heat_category}|FORMAT|{selected_format['name']}|{selected_format['duration']}")

if __name__ == "__main__":
    main()