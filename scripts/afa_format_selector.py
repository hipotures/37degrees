#!/usr/bin/env python3
"""
AFA Format Selector - Simple Python implementation
Selects dialogue format based on book.yaml data and genre rules
Generates full format structure with hosts, segments, and prompts
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Format templates for all 8 dialogue types
FORMAT_TEMPLATES = {
    "academic_analysis": {
        "duration": 15,
        "hosts": {
            "host_a": "Professor analyzing structure, symbolism, and literary techniques with scholarly depth",
            "host_b": "Graduate student asking for clarification, connecting to theories, ensuring accessibility"
        },
        "structure": [
            {"segment": 1, "time_range": "00:00-03:00", "topic": "thesis", "lead": "host_a",
             "description": "Core thesis and revolutionary aspects of the work"},
            {"segment": 2, "time_range": "03:00-06:00", "topic": "analysis", "lead": "host_b",
             "description": "Deep dive into symbolism and literary techniques"},
            {"segment": 3, "time_range": "06:00-09:00", "topic": "examples", "lead": "host_a",
             "description": "Specific textual examples and close reading"},
            {"segment": 4, "time_range": "09:00-12:00", "topic": "synthesis", "lead": "host_b",
             "description": "Theoretical frameworks and scholarly interpretations"},
            {"segment": 5, "time_range": "12:00-15:00", "topic": "contemporary_relevance", "lead": "host_a",
             "description": "Impact on modern literature and academic discourse"}
        ],
        "prompts": {
            "host_a": "You are Professor {male_name}, analyzing '{book_title}' with scholarly depth. Discuss structure, symbolism, literary techniques. Academic but accessible.",
            "host_b": "You are {female_name}, a graduate student. Ask for clarification, request examples, connect to literary theories. Ensure accessibility while maintaining scholarly rigor."
        }
    },

    "critical_debate": {
        "duration": 18,
        "hosts": {
            "host_a": "Literary critic defending traditional interpretation and artistic merit",
            "host_b": "Contemporary critic challenging with modern perspectives and critiques"
        },
        "structure": [
            {"segment": 1, "time_range": "00:00-03:00", "topic": "opening_positions", "lead": "host_a",
             "description": "Traditional interpretation and canonical value"},
            {"segment": 2, "time_range": "03:00-06:00", "topic": "counter_argument", "lead": "host_b",
             "description": "Contemporary challenges and problematic aspects"},
            {"segment": 3, "time_range": "06:00-09:00", "topic": "evidence_exchange", "lead": "host_a",
             "description": "Textual evidence supporting both positions"},
            {"segment": 4, "time_range": "09:00-12:00", "topic": "critical_frameworks", "lead": "host_b",
             "description": "Different critical lenses and interpretations"},
            {"segment": 5, "time_range": "12:00-15:00", "topic": "synthesis_debate", "lead": "host_a",
             "description": "Finding common ground while maintaining differences"},
            {"segment": 6, "time_range": "15:00-18:00", "topic": "audience_implications", "lead": "host_b",
             "description": "What different readings mean for modern audiences"}
        ],
        "prompts": {
            "host_a": "You are {male_name}, defending '{book_title}' traditional interpretation. Argue for canonical value while acknowledging some critiques.",
            "host_b": "You are {female_name}, challenging with contemporary perspectives. Question problematic elements while respecting literary merit."
        }
    },

    "temporal_context": {
        "duration": 15,
        "hosts": {
            "host_a": "Historical expert explaining original context and period details",
            "host_b": "Contemporary observer connecting to modern relevance and parallels"
        },
        "structure": [
            {"segment": 1, "time_range": "00:00-03:00", "topic": "historical_setting", "lead": "host_a",
             "description": "Original historical context and period atmosphere"},
            {"segment": 2, "time_range": "03:00-06:00", "topic": "contemporary_parallels", "lead": "host_b",
             "description": "Modern situations that mirror historical themes"},
            {"segment": 3, "time_range": "06:00-09:00", "topic": "evolution", "lead": "host_a",
             "description": "How interpretations changed across time periods"},
            {"segment": 4, "time_range": "09:00-12:00", "topic": "timeless_elements", "lead": "host_b",
             "description": "Universal themes that transcend historical periods"},
            {"segment": 5, "time_range": "12:00-15:00", "topic": "future_relevance", "lead": "host_a",
             "description": "Why this historical perspective matters for the future"}
        ],
        "prompts": {
            "host_a": "You are {male_name}, a historian explaining '{book_title}' in its original context. Make history vivid and relevant.",
            "host_b": "You are {female_name}, connecting historical themes to 2025. Show how past illuminates present."
        }
    },

    "cultural_dimension": {
        "duration": 18,
        "hosts": {
            "host_a": "Cultural anthropologist analyzing cross-cultural themes and impacts",
            "host_b": "Local perspective sharing specific cultural reception and meaning"
        },
        "structure": [
            {"segment": 1, "time_range": "00:00-03:00", "topic": "original_culture", "lead": "host_a",
             "description": "Cultural context of origin and initial meaning"},
            {"segment": 2, "time_range": "03:00-06:00", "topic": "local_reception", "lead": "host_b",
             "description": "How different cultures received and interpreted"},
            {"segment": 3, "time_range": "06:00-09:00", "topic": "translation_challenges", "lead": "host_a",
             "description": "What gets lost and gained in cultural translation"},
            {"segment": 4, "time_range": "09:00-12:00", "topic": "cultural_adaptations", "lead": "host_b",
             "description": "Local adaptations and cultural reinterpretations"},
            {"segment": 5, "time_range": "12:00-15:00", "topic": "universal_vs_specific", "lead": "host_a",
             "description": "Tension between universal and culturally specific"},
            {"segment": 6, "time_range": "15:00-18:00", "topic": "cultural_bridge", "lead": "host_b",
             "description": "How literature builds cultural understanding"}
        ],
        "prompts": {
            "host_a": "You are {male_name}, analyzing '{book_title}' across cultures. Explain cultural universals and differences.",
            "host_b": "You are {female_name}, sharing local cultural perspective. Show unique cultural interpretations and values."
        }
    },

    "social_perspective": {
        "duration": 18,
        "hosts": {
            "host_a": "Sociologist analyzing systemic issues and social structures",
            "host_b": "Activist connecting to contemporary movements and change"
        },
        "structure": [
            {"segment": 1, "time_range": "00:00-03:00", "topic": "social_systems", "lead": "host_a",
             "description": "Social structures and power dynamics in the work"},
            {"segment": 2, "time_range": "03:00-06:00", "topic": "contemporary_movements", "lead": "host_b",
             "description": "Connection to current social justice movements"},
            {"segment": 3, "time_range": "06:00-09:00", "topic": "class_analysis", "lead": "host_a",
             "description": "Economic and class dimensions explored"},
            {"segment": 4, "time_range": "09:00-12:00", "topic": "marginalized_voices", "lead": "host_b",
             "description": "Perspectives of oppressed and marginalized groups"},
            {"segment": 5, "time_range": "12:00-15:00", "topic": "systemic_change", "lead": "host_a",
             "description": "How literature reflects and influences social change"},
            {"segment": 6, "time_range": "15:00-18:00", "topic": "action_implications", "lead": "host_b",
             "description": "From literary analysis to social action"}
        ],
        "prompts": {
            "host_a": "You are {male_name}, sociologist analyzing '{book_title}' social systems. Explain power structures and inequalities.",
            "host_b": "You are {female_name}, activist connecting to modern movements. Show how literature inspires social change."
        }
    },

    "emotional_perspective": {
        "duration": 18,
        "hosts": {
            "host_a": "Therapist/psychologist exploring emotional and psychological themes",
            "host_b": "Personal experiencer sharing emotional connection and impact"
        },
        "structure": [
            {"segment": 1, "time_range": "00:00-03:00", "topic": "emotional_landscape", "lead": "host_a",
             "description": "Psychological dynamics and emotional patterns"},
            {"segment": 2, "time_range": "03:00-06:00", "topic": "personal_impact", "lead": "host_b",
             "description": "How readers emotionally connect and relate"},
            {"segment": 3, "time_range": "06:00-09:00", "topic": "trauma_patterns", "lead": "host_a",
             "description": "Understanding trauma and healing in the narrative"},
            {"segment": 4, "time_range": "09:00-12:00", "topic": "relationship_dynamics", "lead": "host_b",
             "description": "Exploring relationships and attachment patterns"},
            {"segment": 5, "time_range": "12:00-15:00", "topic": "growth_journey", "lead": "host_a",
             "description": "Character development as psychological journey"},
            {"segment": 6, "time_range": "15:00-18:00", "topic": "healing_insights", "lead": "host_b",
             "description": "What we learn about resilience and healing"}
        ],
        "prompts": {
            "host_a": "You are {male_name}, therapist exploring '{book_title}' psychological depths. Analyze emotional patterns with compassion.",
            "host_b": "You are {female_name}, sharing personal emotional connection. Express how the story touches and transforms readers."
        }
    },

    "exploratory_dialogue": {
        "duration": 15,
        "hosts": {
            "host_a": "Curious explorer discovering the book with fresh eyes",
            "host_b": "Knowledgeable guide revealing hidden depths and connections"
        },
        "structure": [
            {"segment": 1, "time_range": "00:00-03:00", "topic": "first_impressions", "lead": "host_a",
             "description": "Initial reactions and surprising discoveries"},
            {"segment": 2, "time_range": "03:00-06:00", "topic": "hidden_layers", "lead": "host_b",
             "description": "Revealing deeper meanings and easter eggs"},
            {"segment": 3, "time_range": "06:00-09:00", "topic": "world_building", "lead": "host_a",
             "description": "Exploring the created world and its rules"},
            {"segment": 4, "time_range": "09:00-12:00", "topic": "connections", "lead": "host_b",
             "description": "Links to other works and cultural references"},
            {"segment": 5, "time_range": "12:00-15:00", "topic": "wonder_moments", "lead": "host_a",
             "description": "Celebrating moments of beauty and surprise"}
        ],
        "prompts": {
            "host_a": "You are {male_name}, discovering '{book_title}' with curiosity and wonder. Ask questions, express surprise, share excitement.",
            "host_b": "You are {female_name}, guiding the exploration. Reveal hidden depths while maintaining sense of discovery."
        }
    },

    "narrative_reconstruction": {
        "duration": 18,
        "hosts": {
            "host_a": "Detective/investigator piecing together narrative puzzles",
            "host_b": "Witness/informant providing crucial story details and clues"
        },
        "structure": [
            {"segment": 1, "time_range": "00:00-03:00", "topic": "mystery_setup", "lead": "host_a",
             "description": "Identifying narrative puzzles and mysteries"},
            {"segment": 2, "time_range": "03:00-06:00", "topic": "evidence_gathering", "lead": "host_b",
             "description": "Presenting key clues and story evidence"},
            {"segment": 3, "time_range": "06:00-09:00", "topic": "timeline_reconstruction", "lead": "host_a",
             "description": "Piecing together chronology and causality"},
            {"segment": 4, "time_range": "09:00-12:00", "topic": "unreliable_elements", "lead": "host_b",
             "description": "Identifying what can and cannot be trusted"},
            {"segment": 5, "time_range": "12:00-15:00", "topic": "hidden_truth", "lead": "host_a",
             "description": "Revealing the true story beneath the surface"},
            {"segment": 6, "time_range": "15:00-18:00", "topic": "final_reconstruction", "lead": "host_b",
             "description": "Complete narrative understanding achieved"}
        ],
        "prompts": {
            "host_a": "You are {male_name}, investigating '{book_title}' narrative mysteries. Piece together clues like a detective.",
            "host_b": "You are {female_name}, witness to the story. Provide evidence while maintaining narrative tension."
        }
    }
}

def load_book_yaml(book_path: str) -> Dict:
    """Load book.yaml file"""
    yaml_path = Path(book_path) / "book.yaml"
    if not yaml_path.exists():
        raise FileNotFoundError(f"No book.yaml found at {yaml_path}")

    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_format_stats() -> Dict:
    """Load format usage statistics"""
    stats_path = Path("output/afa_format_counts.json")
    if not stats_path.exists():
        # Return empty stats if file doesn't exist
        formats = list(FORMAT_TEMPLATES.keys())
        return {"counts": {f: 0 for f in formats}}

    with open(stats_path, 'r') as f:
        return json.load(f)

def count_research_files(book_path: str) -> int:
    """Count research files in docs/findings/"""
    findings_dir = Path(book_path) / "docs" / "findings"
    if not findings_dir.exists():
        return 0
    return len(list(findings_dir.glob("*.md")))

def get_genre_preferences(genre: str) -> Dict[str, float]:
    """Get format preferences based on genre"""
    genre_lower = genre.lower() if genre else ""

    # Initialize all formats with neutral score
    prefs = {fmt: 0.5 for fmt in FORMAT_TEMPLATES.keys()}

    # Apply genre-specific preferences
    if any(x in genre_lower for x in ["children", "fable", "fairy", "adventure"]):
        prefs["exploratory_dialogue"] = 0.9
        prefs["narrative_reconstruction"] = 0.85
        prefs["academic_analysis"] = 0.2  # Discourage but not forbid

    if any(x in genre_lower for x in ["gothic", "romance"]):
        prefs["emotional_perspective"] = 0.95
        prefs["academic_analysis"] = 0.3

    if any(x in genre_lower for x in ["philosophy", "philosophical"]):
        prefs["academic_analysis"] = 0.8
        prefs["critical_debate"] = 0.75

    if any(x in genre_lower for x in ["dystop", "political", "social"]):
        prefs["social_perspective"] = 0.85
        prefs["critical_debate"] = 0.8

    if any(x in genre_lower for x in ["historical", "history"]):
        prefs["temporal_context"] = 0.9
        prefs["cultural_dimension"] = 0.7

    if any(x in genre_lower for x in ["fantasy", "sci-fi", "science fiction"]):
        prefs["exploratory_dialogue"] = 0.85
        prefs["narrative_reconstruction"] = 0.8
        prefs["cultural_dimension"] = 0.65

    return prefs

def apply_score_modifiers(prefs: Dict[str, float], scores: Dict) -> Dict[str, float]:
    """Modify preferences based on AFA scores"""
    # Get key scores
    structural_complexity = scores.get('structural_complexity', 5)
    philosophical_depth = scores.get('philosophical_depth', 5)
    controversy = scores.get('controversy', 5)
    cultural_phenomenon = scores.get('cultural_phenomenon', 5)
    social_roles = scores.get('social_roles', 5)

    # Apply score-based modifiers
    if structural_complexity < 4:
        prefs["academic_analysis"] *= 0.5  # Reduce for simple books
        prefs["narrative_reconstruction"] *= 0.7
    elif structural_complexity >= 7:
        prefs["narrative_reconstruction"] *= 1.3

    if philosophical_depth >= 8:
        prefs["academic_analysis"] *= 1.2
        prefs["critical_debate"] *= 1.15

    if controversy >= 7:
        prefs["critical_debate"] *= 1.3

    if cultural_phenomenon >= 8:
        prefs["cultural_dimension"] *= 1.25

    if social_roles >= 7:
        prefs["social_perspective"] *= 1.2

    return prefs

def apply_distribution_balancing(prefs: Dict[str, float], stats: Dict) -> Dict[str, float]:
    """Apply gentle balancing based on usage statistics"""
    counts = stats.get('counts', {})
    total = sum(counts.values())

    if total == 0:
        return prefs

    for format_name, count in counts.items():
        if format_name not in prefs:
            continue

        usage_rate = count / total

        # Apply gentle penalties/bonuses
        if usage_rate > 0.25:  # Overused (>25%)
            prefs[format_name] *= 0.8
        elif usage_rate == 0:  # Never used
            prefs[format_name] *= 1.3
        elif usage_rate < 0.05:  # Rarely used (<5%)
            prefs[format_name] *= 1.15

    return prefs

def generate_format_structure(format_name: str, book_title: str) -> Dict:
    """Generate complete format structure with hosts, segments, and prompts"""
    if format_name not in FORMAT_TEMPLATES:
        raise ValueError(f"Unknown format: {format_name}")

    template = FORMAT_TEMPLATES[format_name]

    # Deep copy to avoid modifying template
    import copy
    structure = copy.deepcopy(template)

    # Customize prompts with book title
    for host_key in structure["prompts"]:
        structure["prompts"][host_key] = structure["prompts"][host_key].replace("{book_title}", book_title)

    # Add format name at the structure level
    full_structure = {
        format_name: {
            "name": format_name,
            "duration": structure["duration"],
            "hosts": structure["hosts"],
            "structure": structure["structure"],
            "prompts": structure["prompts"]
        }
    }

    return full_structure

def select_format(book_path: str) -> Dict:
    """Main selection logic"""
    # Load data
    try:
        book_data = load_book_yaml(book_path)
    except FileNotFoundError as e:
        return {"error": "BOOK_NOT_FOUND", "message": str(e)}

    # Extract book info
    book_info = book_data.get('book_info', {})
    title = book_info.get('title', 'Unknown')
    genre = book_info.get('genre', '')

    # Check research files
    research_count = count_research_files(book_path)
    if research_count < 3:
        return {
            "error": "INSUFFICIENT_RESEARCH",
            "book": title,
            "findings_count": research_count,
            "message": f"Cannot select format without proper research foundation. Need minimum 3 research files, found {research_count}."
        }

    # Get AFA scores if available
    afa_analysis = book_data.get('afa_analysis', {})
    scores = afa_analysis.get('scores', {})

    # Get format statistics
    stats = load_format_stats()

    # Calculate preferences
    prefs = get_genre_preferences(genre)
    prefs = apply_score_modifiers(prefs, scores)
    prefs = apply_distribution_balancing(prefs, stats)

    # Select format with highest preference
    selected_format = max(prefs.items(), key=lambda x: x[1])

    # Calculate confidence based on preference strength
    confidence = min(selected_format[1] / sum(prefs.values()) * 2, 1.0)

    # Prepare reasoning
    reasoning = generate_reasoning(title, genre, selected_format[0], scores, stats)

    return {
        "selected_format": selected_format[0],
        "confidence": round(confidence, 2),
        "book_title": title,
        "genre": genre,
        "reasoning": reasoning,
        "research_files_count": research_count,
        "scores_used": {
            "philosophical_depth": scores.get('philosophical_depth'),
            "structural_complexity": scores.get('structural_complexity'),
            "controversy": scores.get('controversy')
        }
    }

def generate_reasoning(title: str, genre: str, format: str, scores: Dict, stats: Dict) -> str:
    """Generate reasoning for format selection"""
    reasons = []

    # Genre-based reasoning
    if "children" in genre.lower() or "fable" in genre.lower():
        if format in ["exploratory_dialogue", "narrative_reconstruction"]:
            reasons.append(f"Children's/fable genre naturally suits {format}")
        elif format == "academic_analysis":
            reasons.append("Despite children's genre, exceptional depth justifies academic treatment")

    if "gothic" in genre.lower() and format == "emotional_perspective":
        reasons.append("Gothic genre demands emotional exploration")

    # Score-based reasoning
    if scores.get('philosophical_depth', 0) >= 8 and format == "academic_analysis":
        reasons.append(f"High philosophical depth ({scores['philosophical_depth']}) supports academic analysis")

    if scores.get('controversy', 0) >= 7 and format == "critical_debate":
        reasons.append(f"High controversy score ({scores['controversy']}) ideal for debate format")

    # Distribution reasoning
    counts = stats.get('counts', {})
    total = sum(counts.values())
    if total > 0:
        usage = counts.get(format, 0) / total * 100
        if usage == 0:
            reasons.append(f"Format never used before, increasing diversity")
        elif usage < 5:
            reasons.append(f"Rarely used format ({usage:.1f}%), improving balance")

    return "; ".join(reasons) if reasons else "Selected based on genre and score analysis"

def update_book_yaml(book_path: str, result: Dict) -> bool:
    """Update book.yaml with format selection and full structure"""
    if 'error' in result:
        return False

    yaml_path = Path(book_path) / "book.yaml"

    # Load existing YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        book_data = yaml.safe_load(f)

    # Ensure afa_analysis section exists
    if 'afa_analysis' not in book_data:
        book_data['afa_analysis'] = {}

    # Get current format if exists
    current_formats = book_data['afa_analysis'].get('formats', {})

    # Check if format is changing
    format_name = result['selected_format']

    # If we have the old complex structure with nested format
    if isinstance(current_formats, dict) and len(current_formats) == 1:
        # Old structure has format name as key
        current_format_name = list(current_formats.keys())[0] if current_formats else None
    else:
        # New simple structure
        current_format_name = current_formats.get('name') if isinstance(current_formats, dict) else None

    # Generate full structure for the new format
    if current_format_name != format_name or not isinstance(current_formats, dict) or 'hosts' not in current_formats.get(format_name, {}):
        # Format is changing or structure is missing - generate new
        full_structure = generate_format_structure(format_name, result['book_title'])
        book_data['afa_analysis']['formats'] = full_structure
        print(f"Generated new structure for format: {format_name}")
    else:
        # Format unchanged and has structure - preserve existing
        print(f"Preserving existing structure for format: {format_name}")

    # Write back to YAML
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(book_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)

    return True

def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python afa_format_selector.py <book_path> [--update]")
        print("Example: python afa_format_selector.py books/0037_wuthering_heights")
        print("         python afa_format_selector.py books/0037_wuthering_heights --update")
        sys.exit(1)

    book_path = sys.argv[1]
    update_yaml = '--update' in sys.argv

    result = select_format(book_path)

    # Output as JSON
    print(json.dumps(result, indent=2))

    # Update YAML if requested
    if update_yaml and 'error' not in result:
        if update_book_yaml(book_path, result):
            print(f"\n✓ Updated {book_path}/book.yaml with format: {result['selected_format']}")
        else:
            print(f"\n✗ Failed to update {book_path}/book.yaml")

if __name__ == "__main__":
    main()