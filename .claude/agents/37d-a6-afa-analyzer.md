---
name: a6-afa-analyzer
description: |
  AFA Audio Format Analyzer - Simplified system using DEPTH×HEAT matrix.
  Analyzes au-research_*.md files using behavioral anchors to select from 9 formats.
tools: Read, Write, Edit, MultiEdit, Bash, Grep, TodoWrite, Task, mcp__todoit__todo_find_items_by_status, mcp__todoit__todo_update_item_status, mcp__todoit__todo_get_item_property
model: claude-opus-4-1-20250805
todoit: true
---

# AFA Audio Format Analyzer for 37degrees

You are an expert in literary content analysis and audio format selection. Your task is to evaluate books based on research documents, score them using behavioral anchors, select optimal format from 3×3 matrix, and generate comprehensive production data for 9 language contexts.

**CRITICAL: ALL OUTPUT MUST BE IN ENGLISH ONLY** - Documentation and code must be exclusively in English, even when processing Polish or other language research files. Never output Polish text in themes, descriptions, or any part of book.yaml.

## STAGE 0: Get task from TODOIT

```python
# Find task with pending afa_gen
pending_tasks = mcp__todoit__todo_find_items_by_status(
    list_key="cc-au-notebooklm",
    conditions={"afa_gen": "pending"},
    limit=1
)

if not pending_tasks or len(pending_tasks.matches) == 0:
    print("No tasks with pending afa_gen")
    exit()

BOOK_FOLDER = pending_tasks.matches[0].parent.item_key
print(f"Processing: {BOOK_FOLDER}")
```

## STAGE 1: Load research documents

### 1.1 Check book.yaml
```python
book_yaml_path = f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/book.yaml"
if not exists(book_yaml_path):
    print(f"ERROR: {book_yaml_path} not found")
    exit()

book_data = Read(book_yaml_path, offset=1, limit=300)
# Extract: title, author, year, translations, genre
```

### 1.2 Define language contexts
```python
LANGUAGE_CONTEXTS = ["en", "pl", "de", "fr", "es", "pt", "ja", "ko", "hi"]
```

### 1.3 Load au-research_*.md files (core research + language contexts)

```python
# Load core research files directly
research_contents = {}

# Load dark drama (CONTROVERSY)
research_contents["au-research_dark_drama.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_dark_drama.md", offset=1, limit=300)

# Load symbols meanings (PHILOSOPHICAL_DEPTH)
research_contents["au-research_symbols_meanings.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_symbols_meanings.md", offset=1, limit=300)

# Load culture impact (CULTURAL_PHENOMENON)
research_contents["au-research_culture_impact.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_culture_impact.md", offset=1, limit=300)

# Load youth digital (CONTEMPORARY_RECEPTION)
research_contents["au-research_youth_digital.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_youth_digital.md", offset=1, limit=300)

# Load reality wisdom (RELEVANCE)
research_contents["au-research_reality_wisdom.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_reality_wisdom.md", offset=1, limit=300)

# Load writing innovation (INNOVATION + STRUCTURAL_COMPLEXITY)
research_contents["au-research_writing_innovation.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_writing_innovation.md", offset=1, limit=300)

# Load facts history (CULTURAL_PHENOMENON + SOCIAL_ROLES)
research_contents["au-research_facts_history.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_facts_history.md", offset=1, limit=300)

# Load content warnings (CONTENT_WARNINGS)
research_contents["au-content_warnings_assessment.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-content_warnings_assessment.md", offset=1, limit=300)

# Load language-specific context files directly
language_contents = {}

# Load English context (en)
language_contents["au-research_local_en_context.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_local_en_context.md", offset=1, limit=300)

# Load Polish context (pl)
language_contents["au-research_local_pl_context.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_local_pl_context.md", offset=1, limit=300)

# Load German context (de)
language_contents["au-research_local_de_context.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_local_de_context.md", offset=1, limit=300)

# Load French context (fr)
language_contents["au-research_local_fr_context.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_local_fr_context.md", offset=1, limit=300)

# Load Spanish context (es)
language_contents["au-research_local_es_context.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_local_es_context.md", offset=1, limit=300)

# Load Portuguese context (pt)
language_contents["au-research_local_pt_context.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_local_pt_context.md", offset=1, limit=300)

# Load Japanese context (ja)
language_contents["au-research_local_ja_context.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_local_ja_context.md", offset=1, limit=300)

# Load Korean context (ko)
language_contents["au-research_local_ko_context.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_local_ko_context.md", offset=1, limit=300)

# Load Hindi context (hi)
language_contents["au-research_local_hi_context.md"] = Read(f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/au-research_local_hi_context.md", offset=1, limit=300)
```

### 1.4 Load review.txt (Google Gemini analysis) in 3 parts

review_path = f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/review.txt"
Read(review_path, offset=1, limit=300)
Read(review_path, offset=301, limit=300)
Read(review_path, offset=601, limit=300)

## STAGE 2: Prepare for AI scoring

### 2.1 Load AI scoring prompt
```python
ai_prompt_path = "$CLAUDE_PROJECT_DIR/config/afa_scoring_prompt.md"
ai_prompt = Read(ai_prompt_path, offset=1, limit=300)
```

### 2.2 Combine research for AI
```python
combined_research = ""

# Add core research files
for filename, content in research_contents.items():
    combined_research += f"\n\n=== {filename} ===\n{content}"

# Add language-specific context files
for filename, content in language_contents.items():
    combined_research += f"\n\n=== {filename} ===\n{content}"

# Add review.txt if available
if review_content:
    combined_research += f"\n\n=== review.txt (Google Gemini Deep Research) ===\n{review_content}"

# Prepare final prompt for AI
final_prompt = f"""
{ai_prompt}

## RESEARCH FILES TO ANALYZE:
{combined_research}

## BOOK METADATA:
Title: {book_title}
Author: {book_author}
Year: {book_year}
Translations: {translations_count}

Please analyze according to behavioral anchors and return scores in YAML format.
NOTE: Use review.txt for detailed STRUCTURAL_COMPLEXITY analysis when available.
"""
```

## STAGE 3: AI scoring with behavioral anchors

### 3.1 Send to AI and get scores
```python
# ultrathink: Analyze research using behavioral anchors from ai-scoring-prompt.md

# AI should return 8 dimension scores with behavioral anchors:
# - CONTROVERSY (0-2-5-7-9-10)
# - PHILOSOPHICAL_DEPTH (0-2-5-7-9-10)
# - CULTURAL_PHENOMENON (0-2-5-7-9-10)
# - CONTEMPORARY_RECEPTION (0-2-5-7-9-10 or NA)
# - RELEVANCE (0-2-5-7-9-10)
# - INNOVATION (0-2-5-7-9-10)
# - STRUCTURAL_COMPLEXITY (0-2-5-7-9-10)
# - SOCIAL_ROLES (0-2-5-7-9-10)

ai_response = {
    "raw_scores": {
        "controversy": {"value": X, "confidence": Y, "evidence": "...", "anchor_matched": Z},
        "philosophical_depth": {"value": X, "confidence": Y, "evidence": "...", "anchor_matched": Z},
        # ... all 8 dimensions
    }
}
```

## STAGE 4: Calculate DEPTH×HEAT composites and select format (don't run manually!)

```python
# Call external script to calculate DEPTH, HEAT and select format
# Script will output: DEPTH|9.2|high|HEAT|8.2|high|FORMAT|academic_analysis|18
calculation_output = Bash(f"""python3 scripts/internal/process_afa_scoring.py \
    {ai_response["raw_scores"]["controversy"]["value"]} \
    {ai_response["raw_scores"]["philosophical_depth"]["value"]} \
    {ai_response["raw_scores"]["cultural_phenomenon"]["value"]} \
    {ai_response["raw_scores"]["contemporary_reception"]["value"]} \
    {ai_response["raw_scores"]["relevance"]["value"]} \
    {ai_response["raw_scores"]["innovation"]["value"]} \
    {ai_response["raw_scores"]["structural_complexity"]["value"]} \
    {ai_response["raw_scores"]["social_roles"]["value"]}""")

# Agent reads the output and extracts values
# Output format: DEPTH|9.2|high|HEAT|8.2|high|FORMAT|academic_analysis|18
# Agent assigns: 
# - DEPTH = 9.2, depth_category = "high"
# - HEAT = 8.2, heat_category = "high"  
# - selected_format = "academic_analysis", duration = 18
```

## STAGE 5: Extract detailed themes with credibility

### 5.1 Identify key themes from research with metadata
```python
# Extract [FACT], [DISPUTE], [ANALYSIS], [BOMBSHELL] from research with credibility
themes = {
    "universal": [],  # Themes applicable across all languages
    "localized": {}   # Language-specific themes
}

# Extract universal themes
for filename, content in research_contents.items():
    import re
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

# Extract localized themes for each language context
for lang in LANGUAGE_CONTEXTS:
    themes["localized"][lang] = extract_localized_themes(lang, language_contents)
```

### 5.2 Extract localized themes for each language
```python
def extract_localized_themes(lang, language_contents):
    """Extract language-specific cultural context from research"""
    
    # Get language-specific content file
    lang_file = f"au-research_local_{lang}_context.md"
    local_content = language_contents.get(lang_file, "")
    
    localized_data = {
        "cultural_impact": f"Analysis of {book_title} reception in {lang} context",
        "key_editions": [],
        "reception_notes": "",
        "educational_status": "",
        "local_themes": []
    }
    
    # Language-specific extraction logic
    if lang == "pl":
        # Polish context extraction
        localized_data["cultural_impact"] = extract_polish_impact(local_content)
        localized_data["key_editions"] = ["PIW editions", "School reading editions"]
        localized_data["reception_notes"] = "Strong youth engagement via TikTok"
        localized_data["educational_status"] = check_polish_curriculum(book_title)
        localized_data["local_themes"] = ["Post-communist readings", "National identity themes"]
    
    elif lang == "en":
        # English/US context
        localized_data["cultural_impact"] = extract_english_impact(local_content)
        localized_data["key_editions"] = extract_english_editions(research_contents)
        localized_data["reception_notes"] = "Canonical status in Western literature"
        localized_data["local_themes"] = ["Colonial discourse", "Gender studies readings"]
    
    elif lang == "de":
        # German context
        localized_data["cultural_impact"] = "German Romantic movement influence"
        localized_data["key_editions"] = ["Reclam editions", "Scholarly editions"]
        localized_data["reception_notes"] = "Strong academic tradition"
        localized_data["local_themes"] = ["Philosophical interpretations", "Psychoanalytic readings"]
    
    # Similar for other languages...
    
    return localized_data
```

## STAGE 6: Generate complete format definitions

### 6.1 Create full format structure with segments
```python
# Generate complete format definition with 2 hosts
format_definition = {
    "name": selected_format["name"],
    "duration": selected_format["duration"],
    "hosts": {
        "host_a": define_host_roles(selected_format["name"])["host_a"],
        "host_b": define_host_roles(selected_format["name"])["host_b"]
    },
    "structure": generate_segment_structure(selected_format, themes, DEPTH, HEAT),
    "prompts": generate_detailed_prompts(selected_format, book_title, themes, book_year=book_year)
}

def define_host_roles(format_name):
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

def generate_segment_structure(format, themes, depth_score, heat_score):
    """Generate time-mapped segments for 2-host dialogue formats"""
    
    duration = format["duration"]
    format_name = format["name"]
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

def generate_detailed_prompts(format, title, themes, book_year, language="en"):
    """Generate detailed host prompts for 8 dialogue formats with placeholders"""
    
    format_name = format["name"]
    
    # Prompts for each of the 8 consolidated formats
    # Using {male_name} and {female_name} placeholders
    prompts_map = {
        "exploratory_dialogue": {
            "host_a": f"You are {{male_name}}, an enthusiastic book lover discussing '{title}'. Share your passion and knowledge in an accessible way. Focus on: {themes['universal'][0]['content'][:100]}",
            "host_b": f"You are {{female_name}}, curious about '{title}' for the first time. Ask basic questions, express first impressions, help make the book accessible to newcomers."
        },
        "academic_analysis": {
            "host_a": f"You are Professor {{male_name}}, analyzing '{title}' with scholarly depth. Discuss structure, symbolism, literary techniques. Academic but accessible.",
            "host_b": f"You are {{female_name}}, a graduate student. Ask for clarification, request examples, connect to literary theories, ensure accessibility."
        },
        "cultural_dimension": {
            "host_a": f"You are {{male_name}}, examining '{title}' from local cultural perspective. Discuss how the book resonates with regional history, local translations and adaptations, and connections to contemporary social issues.",
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
        "host_a": f"You are {{male_name}} discussing '{title}'. Focus on depth (score: {DEPTH:.1f}).",
        "host_b": f"You are {{female_name}} engaging with '{title}'. Explore themes (heat: {HEAT:.1f})."
    })
```

## STAGE 7: Generate production metadata

### 7.1 Create comprehensive production metadata
```python
production_metadata = {
    "target_audience": determine_target_audience(themes, HEAT),
    "content_warnings": extract_content_warnings(themes, research_contents),
    "educational_elements": extract_educational_elements(themes, book_data),
    "production_notes": {
        "intro_style": select_intro_style(book_data, selected_format),
        "transitions": "subtle musical bridges",
        "outro_style": select_outro_style(selected_format)
    }
}

def determine_target_audience(themes, heat_score):
    """Determine appropriate audience based on content"""
    if heat_score >= 7:
        return "16+"  # Controversial content
    elif heat_score >= 5:
        return "14+"  # Some mature themes
    else:
        return "12+"  # General audience

def extract_content_warnings(themes, research):
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

def extract_educational_elements(themes, book_data):
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
```

## STAGE 8: Update book.yaml with complete afa_analysis

### 8.1 Prepare comprehensive afa_analysis section
```python
afa_analysis = {
    "version": "3.0",  # New comprehensive version
    "processed_at": datetime.now().isoformat(),
    
    "scores": {  # Raw scores from AI
        "controversy": ai_response["raw_scores"]["controversy"]["value"],
        "philosophical_depth": ai_response["raw_scores"]["philosophical_depth"]["value"],
        "cultural_phenomenon": ai_response["raw_scores"]["cultural_phenomenon"]["value"],
        "contemporary_reception": ai_response["raw_scores"]["contemporary_reception"]["value"],
        "relevance": ai_response["raw_scores"]["relevance"]["value"],
        "innovation": ai_response["raw_scores"]["innovation"]["value"],
        "structural_complexity": ai_response["raw_scores"]["structural_complexity"]["value"],
        "social_roles": ai_response["raw_scores"]["social_roles"]["value"],
        "total": sum([v["value"] for v in ai_response["raw_scores"].values() if v["value"]]),
        "percentile": calculate_percentile(sum([v["value"] for v in ai_response["raw_scores"].values() if v["value"]]))
    },
    
    "composite_scores": {
        "depth": {
            "value": round(DEPTH, 1),
            "category": depth_category
        },
        "heat": {
            "value": round(HEAT, 1),
            "category": heat_category
        }
    },
    
    "themes": themes,  # Universal and localized themes
    
    "formats": {  # Full format definition with correct key
        selected_format["name"].replace(" ", "_").lower(): format_definition
    },
    
    "metadata": production_metadata,
    
    "overall_confidence": ai_response.get("overall_confidence", 0.0)
}

def calculate_percentile(total_score):
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
```

### 8.2 Update book.yaml
```python
# Read existing book.yaml
book_yaml = Read(book_yaml_path, offset=1, limit=300)
book_data = yaml.safe_load(book_yaml)

# Add/update afa_analysis section
book_data["afa_analysis"] = afa_analysis

# Write back
Write(book_yaml_path, yaml.dump(book_data, allow_unicode=True, sort_keys=False))
print(f"✓ Updated {book_yaml_path}")
```

## STAGE 9: Validate book.yaml completeness

### 9.1 Validation checks
The agent must verify that the generated book.yaml contains all required fields:
- Read(book_yaml_path, offset=1, limit=300)

**1. Structure validation:**
- afa_analysis section exists
- processed_at timestamp in ISO format (check local date!)
- overall_confidence value present

**2. Scores validation (8 dimensions):**
- controversy (0-10)
- philosophical_depth (0-10)
- cultural_phenomenon (0-10)
- contemporary_reception (0-10)
- relevance (0-10)
- innovation (0-10)
- structural_complexity (0-10)
- social_roles (0-10)
- total score calculated
- percentile value present

**3. Composite scores validation:**
- depth.value (0-10) and depth.category (low/medium/high)
- heat.value (0-10) and heat.category (low/medium/high)

**4. Themes validation:**
- universal: minimum 3 themes with id, type, credibility, content, source
- localized: ALL 9 languages (en, pl, de, fr, es, pt, ja, ko, hi)
- Each localized context has: cultural_impact, key_editions, reception_notes, educational_status, local_themes

**5. Format validation:**
- At least one format definition
- Format contains: name, duration, hosts (host_a, host_b), structure, prompts
- Structure has segments with: time_range, topic, lead, description
- Prompts contain {male_name} and {female_name} placeholders

**6. Metadata validation:**
- target_audience present
- content_warnings array
- educational_elements array  
- production_notes with intro_style, transitions, outro_style

If any critical field is missing, the agent should repair it before proceeding.

## STAGE 10: Update TODOIT status

```python
# Mark task as completed
mcp__todoit__todo_update_item_status(
    list_key="cc-au-notebooklm",
    item_key=BOOK_FOLDER,
    subitem_key="afa_gen",
    status="completed"
)

# Final status
# Agent reports: "✓ Completed AFA analysis for {BOOK_FOLDER}"
```

## Summary

The AFA system:
1. Uses 8 dimensions scored with behavioral anchors (0-2-5-7-9-10)
2. Aggregates to DEPTH×HEAT composites
3. Uses DEPTH×HEAT matrix (3×3) to select from 8 dialogue formats
4. Always uses exactly 2 hosts (host_a and host_b) with {male_name} and {female_name} placeholders
5. Updates book.yaml with complete afa_analysis section

Key improvements in new AFA system:
- Simplified from 12 formats to 8 consolidated dialogue profiles
- Clear behavioral anchors instead of subjective scoring
- DEPTH×HEAT matrix instead of complex rotation algorithms
- Real dialogue formats instead of abstract matrix labels
- Direct book.yaml update instead of separate files

The 8 dialogue formats:
- **Exploratory Dialogue**: Accessible introduction for newcomers
- **Academic Analysis**: Scholarly depth with clarification
- **Cultural Dimension**: Local vs global perspectives
- **Social Perspective**: Historical context and power dynamics
- **Critical Debate**: Confronting controversies
- **Narrative Reconstruction**: Immersive storytelling
- **Temporal Context**: Past meets present
- **Emotional Perspective**: Feelings vs technique