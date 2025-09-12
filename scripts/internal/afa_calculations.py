#!/usr/bin/env python3
"""
AFA Calculations Module
Handles DEPTH×HEAT composite calculations and format selection
"""

import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

def calculate_depth_heat_composites(ai_response: Dict) -> Tuple[float, str, float, str]:
    """
    Calculate DEPTH and HEAT composite scores from AI analysis
    
    Args:
        ai_response: Dictionary containing raw scores from AI analysis
        
    Returns:
        Tuple of (DEPTH, depth_category, HEAT, heat_category)
    """
    # DEPTH = avg(philosophical_depth, innovation, structural_complexity, relevance)
    depth_components = []
    for dim in ["philosophical_depth", "innovation", "structural_complexity", "relevance"]:
        if ai_response["raw_scores"][dim]["value"] is not None:
            depth_components.append(ai_response["raw_scores"][dim]["value"])

    if len(depth_components) >= 2:
        DEPTH = sum(depth_components) / len(depth_components)
        
        # Categorize
        if DEPTH < 4.0:
            depth_category = "low"
        elif DEPTH < 6.0:
            depth_category = "medium"
        else:
            depth_category = "high"
    else:
        raise ValueError("ERROR: Insufficient data for DEPTH")

    # HEAT = avg(controversy, social_roles, contemporary_reception, cultural_phenomenon)
    heat_components = []
    for dim in ["controversy", "social_roles", "contemporary_reception", "cultural_phenomenon"]:
        if ai_response["raw_scores"][dim]["value"] is not None:
            heat_components.append(ai_response["raw_scores"][dim]["value"])

    if len(heat_components) >= 2:
        HEAT = sum(heat_components) / len(heat_components)
        
        # Categorize
        if HEAT < 4.0:
            heat_category = "low"
        elif HEAT < 6.0:
            heat_category = "medium"
        else:
            heat_category = "high"
    else:
        raise ValueError("ERROR: Insufficient data for HEAT")

    return DEPTH, depth_category, HEAT, heat_category


def select_format_from_matrix(depth_category: str, heat_category: str) -> Dict[str, Any]:
    """
    Select format from DEPTH×HEAT matrix
    
    Args:
        depth_category: "low", "medium", or "high"
        heat_category: "low", "medium", or "high"
        
    Returns:
        Dictionary with format details
    """
    # 8 real dialogue formats mapped to DEPTH×HEAT positions
    FORMAT_MATRIX = {
        # Low DEPTH (simple, accessible)
        ("low", "low"): {"name": "exploratory_dialogue", "code": "exploratory_dialogue", "duration": 8},
        ("low", "medium"): {"name": "narrative_reconstruction", "code": "narrative_reconstruction", "duration": 10},
        ("low", "high"): {"name": "critical_debate", "code": "critical_debate", "duration": 12},
        
        # Medium DEPTH (balanced complexity)
        ("medium", "low"): {"name": "emotional_perspective", "code": "emotional_perspective", "duration": 11},
        ("medium", "medium"): {"name": "temporal_context", "code": "temporal_context", "duration": 13},
        ("medium", "high"): {"name": "social_perspective", "code": "social_perspective", "duration": 14},
        
        # High DEPTH (complex, scholarly)
        ("high", "low"): {"name": "academic_analysis", "code": "academic_analysis", "duration": 15},
        ("high", "medium"): {"name": "cultural_dimension", "code": "cultural_dimension", "duration": 16},
        ("high", "high"): {"name": "academic_analysis", "code": "academic_analysis", "duration": 18}
    }

    return FORMAT_MATRIX[(depth_category, heat_category)]


def extract_themes_with_credibility(research_contents: Dict[str, str]) -> Dict[str, List]:
    """
    Extract themes from research with credibility scoring
    
    Args:
        research_contents: Dictionary of research file contents
        
    Returns:
        Dictionary with universal themes
    """
    themes = {
        "universal": []
    }

    # Extract universal themes
    for filename, content in research_contents.items():
        pattern = r'\[(FACT|DISPUTE|ANALYSIS|BOMBSHELL|HYPOTHESIS)\]([^[]+)'
        matches = re.findall(pattern, content)
        
        for tag, text in matches[:3]:  # Max 3 per file
            # Calculate credibility based on tag type
            credibility = {
                "FACT": 0.95,
                "ANALYSIS": 0.85,
                "HYPOTHESIS": 0.75,
                "DISPUTE": 0.70,
                "BOMBSHELL": 0.90
            }.get(tag, 0.80)
            
            theme_id = f"{filename.split('_')[2]}_{len(themes['universal'])}"
            
            themes["universal"].append({
                "id": theme_id,
                "type": tag,
                "credibility": credibility,
                "content": text.strip()[:300],
                "source": filename.replace("au-research_", "").replace(".md", "")
            })

    # Keep top 8 universal themes
    themes["universal"] = sorted(themes["universal"], 
                                key=lambda x: x["credibility"], 
                                reverse=True)[:8]
    
    return themes


def define_host_roles(format_name: str) -> Dict[str, str]:
    """Define host roles based on 8 consolidated dialogue formats"""
    roles_map = {
        "exploratory_dialogue": {
            "host_a": "enthusiastic book lover sharing passion",
            "host_b": "curious newcomer asking basic questions"
        },
        "academic_analysis": {
            "host_a": "professor/expert presenting complex concepts",
            "host_b": "student/assistant simplifying and clarifying"
        },
        "cultural_dimension": {
            "host_a": "local culture specialist",
            "host_b": "global literature observer"
        },
        "social_perspective": {
            "host_a": "social historian analyzing context",
            "host_b": "contemporary critic examining power dynamics"
        },
        "critical_debate": {
            "host_a": "passionate advocate defending the work",
            "host_b": "critical skeptic questioning value"
        },
        "narrative_reconstruction": {
            "host_a": "investigative reporter asking questions",
            "host_b": "eyewitness describing events and emotions"
        },
        "temporal_context": {
            "host_a": "classical literature expert explaining origins",
            "host_b": "contemporary reader finding modern relevance"
        },
        "emotional_perspective": {
            "host_a": "emotional reader sharing feelings",
            "host_b": "analytical critic explaining techniques"
        }
    }
    return roles_map.get(format_name, {"host_a": "primary voice", "host_b": "supporting voice"})


def generate_segment_structure(format_dict: Dict, themes: Dict, depth_score: float, heat_score: float) -> List[Dict]:
    """Generate time-mapped segments for 2-host dialogue formats"""
    
    duration = format_dict["duration"]
    format_name = format_dict["name"]
    segments = []
    
    # Segment count based on duration
    if duration <= 10:
        segment_count = 3
    elif duration <= 14:
        segment_count = 4
    else:
        segment_count = 5
    
    segment_duration = duration / segment_count
    
    # Define segment patterns for each format
    segment_patterns = {
        "exploratory_dialogue": ["introduction", "exploration", "discovery", "reflection"],
        "academic_analysis": ["thesis", "analysis", "examples", "synthesis"],
        "cultural_dimension": ["local_context", "global_impact", "translations", "legacy"],
        "social_perspective": ["historical_context", "power_dynamics", "contemporary_relevance", "future"],
        "critical_debate": ["opening_positions", "main_arguments", "counterarguments", "resolution"],
        "narrative_reconstruction": ["setup", "key_events", "revelations", "impact"],
        "temporal_context": ["original_era", "evolution", "modern_parallels", "timelessness"],
        "emotional_perspective": ["first_impressions", "deep_emotions", "technique_analysis", "lasting_impact"]
    }
    
    pattern = segment_patterns.get(format_name, ["opening", "development", "climax", "conclusion"])
    
    # Generate segments with alternating lead between host_a and host_b
    for i in range(segment_count):
        start_time = i * segment_duration
        end_time = (i + 1) * segment_duration
        
        # Alternate lead between hosts
        lead = "host_a" if i % 2 == 0 else "host_b"
        
        # Select theme and description
        if i < len(themes["universal"]):
            theme = themes["universal"][i]
            topic = pattern[i] if i < len(pattern) else theme["id"]
            description = theme["content"][:100]
        else:
            topic = pattern[i] if i < len(pattern) else "synthesis"
            description = "Bringing themes together"
        
        segments.append({
            "segment": i + 1,
            "time_range": f"{int(start_time):02d}:{int((start_time % 1) * 60):02d}-{int(end_time):02d}:{int((end_time % 1) * 60):02d}",
            "topic": topic,
            "lead": lead,
            "description": description
        })
    
    return segments


def generate_detailed_prompts(format_dict: Dict, title: str, themes: Dict, book_year: int, language: str = "en") -> Dict[str, str]:
    """Generate detailed host prompts for 8 dialogue formats with placeholders"""
    
    format_name = format_dict["name"]
    
    # Prompts for each of the 8 consolidated formats
    # Using {male_name} and {female_name} placeholders
    prompts_map = {
        "exploratory_dialogue": {
            "host_a": f"You are {{male_name}}, an enthusiastic book lover discussing '{title}'. Share your passion and knowledge in an accessible way. Focus on: {themes['universal'][0]['content'][:100] if themes['universal'] else 'key themes'}",
            "host_b": f"You are {{female_name}}, curious about '{title}' for the first time. Ask basic questions, express first impressions, help make the book accessible to newcomers."
        },
        "academic_analysis": {
            "host_a": f"You are Professor {{male_name}}, analyzing '{title}' with scholarly depth. Discuss structure, symbolism, literary techniques. Academic but accessible.",
            "host_b": f"You are {{female_name}}, a graduate student. Ask for clarification, request examples, connect to literary theories, ensure accessibility."
        },
        "cultural_dimension": {
            "host_a": f"You are {{male_name}}, examining '{title}' from local cultural perspective. Discuss Polish reception, translations, local significance.",
            "host_b": f"You are {{female_name}}, providing global context for '{title}'. Compare international adaptations, discuss universal themes."
        },
        "social_perspective": {
            "host_a": f"You are {{male_name}}, a social historian. Analyze '{title}' through lens of power, gender, class. Historical context: {book_year}.",
            "host_b": f"You are {{female_name}}, examining contemporary relevance. Connect to current social debates, modern interpretations."
        },
        "critical_debate": {
            "host_a": f"You are {{male_name}}, passionately defending '{title}'. Address controversies: {themes['universal'][3]['content'][:80] if len(themes['universal']) > 3 else 'various controversies'}.",
            "host_b": f"You are {{female_name}}, critically questioning '{title}'. Point out problems, challenge assumptions, maintain respectful skepticism."
        },
        "narrative_reconstruction": {
            "host_a": f"You are {{male_name}}, an investigative reporter. Ask about key events in '{title}', seek details, uncover hidden meanings.",
            "host_b": f"You are {{female_name}}, an eyewitness to the story. Describe scenes vividly, share emotional impact, bring narrative to life."
        },
        "temporal_context": {
            "host_a": f"You are {{male_name}}, a classical literature expert. Explain '{title}' in its original {book_year} context, conventions, intentions.",
            "host_b": f"You are {{female_name}} from 2025. Find modern parallels in '{title}', connect to current technology, contemporary sensibilities."
        },
        "emotional_perspective": {
            "host_a": f"You are {{male_name}}, sharing emotional response to '{title}'. Discuss personal impact, moments that moved you, feelings evoked.",
            "host_b": f"You are {{female_name}}, an analytical critic. Explain how '{title}' creates emotions through technique, structure, language."
        }
    }
    
    return prompts_map.get(format_name, {
        "host_a": f"You are {{male_name}} discussing '{title}'. Focus on depth.",
        "host_b": f"You are {{female_name}} engaging with '{title}'. Explore themes."
    })


def calculate_percentile(total_score: float) -> int:
    """Calculate percentile based on total score (0-80 scale)"""
    # Rough percentile mapping
    if total_score >= 70:
        return 95
    elif total_score >= 60:
        return 85
    elif total_score >= 50:
        return 75
    elif total_score >= 40:
        return 60
    elif total_score >= 30:
        return 45
    else:
        return 30


def determine_target_audience(themes: Dict, heat_score: float) -> str:
    """Determine appropriate audience based on content"""
    if heat_score >= 7:
        return "16+"  # Controversial content
    elif heat_score >= 5:
        return "14+"  # Some mature themes
    else:
        return "12+"  # General audience


def extract_content_warnings(themes: Dict, research_contents: Dict) -> List[str]:
    """Identify content that needs warnings"""
    warnings = []
    
    # Check for controversial content
    for theme in themes["universal"]:
        if theme["type"] in ["BOMBSHELL", "DISPUTE"]:
            if "violence" in theme["content"].lower():
                warnings.append("historical violence")
            if "sexual" in theme["content"].lower():
                warnings.append("sexual content references")
            if "racist" in theme["content"].lower() or "colonial" in theme["content"].lower():
                warnings.append("colonial/racist content discussion")
    
    return warnings if warnings else ["none"]


def extract_educational_elements(themes: Dict, book_data: Dict) -> List[str]:
    """Identify educational value points"""
    elements = []
    
    # Add literary techniques
    if "genre" in book_data:
        elements.append(f"{book_data['genre']} genre characteristics")
    
    # Add historical context
    if "year" in book_data:
        elements.append(f"Historical context of {book_data['year']}")
    
    # Add thematic elements
    for theme in themes["universal"][:3]:
        if theme["type"] == "ANALYSIS":
            elements.append(theme["content"][:50])
    
    return elements