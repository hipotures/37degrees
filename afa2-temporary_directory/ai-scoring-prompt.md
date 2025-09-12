# AI Book Scoring Prompt v2.1
## Standardized Behavioral Anchors with AFA Integration

## Task
Analyze the provided research files and score the book using behavioral anchors. Your scores will determine the audio format through a DEPTH×HEAT matrix for AFA (Audio Format Advisor) system.

## Critical Instructions

1. **Use behavioral anchors** - Compare evidence to specific anchor points (0, 2, 5, 7, 9, 10)
2. **Mark NA when appropriate** - If insufficient data, mark NA rather than guessing
3. **Cite specific evidence** - Each score needs 1-2 concrete citations from research
4. **Calculate confidence** - Rate your confidence in each score (0.0-1.0)
5. **No imputation** - Never fill in missing data with assumptions

## Operational Definitions

### Accepted Data Sources
- **Academic**: peer-reviewed journals, university databases, dissertations
- **Media**: major newspapers (>100k circulation), established magazines
- **Cultural**: IMDB, Goodreads, official publisher data, museum records
- **Social**: Twitter/X, TikTok, Instagram, Reddit (deduplicated by post, not likes)
- **Time window**: Last 5 years for "contemporary", lifetime cumulative for "phenomenon"

### Counting Rules
- **Adaptations**: Each distinct production counts once (TV series = 1, not per episode)
- **Mentions**: Deduplicate by author/poster within 30 days
- **Controversies**: Weight by impact (global ban = 2 points, single country = 1)
- **Translations**: Count unique languages, not editions

### Era-Specific Adjustments
- **Pre-1950**: No social media metrics (NA for contemporary_reception)
- **Pre-1900**: No film adaptations possible (adjust cultural_phenomenon anchors)
- **Pre-1800**: Focus on manuscript traditions, scholarly editions
- **All eras**: Scale innovation relative to contemporary norms

## Scoring Process

For each dimension:
1. Read the relevant research files
2. Compare findings to behavioral anchors
3. Select the anchor that best matches the evidence
4. If between anchors, interpolate (e.g., 6 if between 5 and 7)
5. If insufficient evidence, mark as NA
6. Record 1-2 specific supporting facts

## Behavioral Anchors Reference

### CONTROVERSY (weighted impact score)
Point calculation:
- Academic debate = 1 point
- Plagiarism scandal = 2 points  
- Single country ban = 2 points
- Author persecution = 3 points
- Multi-country ban (2-3) = 4 points
- Widespread ban (4+) = 6 points

Point-to-anchor function:
```python
def controversy_anchor(points):
    if points == 0: return 0
    elif points <= 2: return 2
    elif points <= 5: return 5
    elif points <= 8: return 7
    elif points <= 11: return 9
    else: return 10  # points >= 12
```

Anchors:
- **0**: No controversies (0 points)
- **2**: Minor debates (1-2 points)
- **5**: Moderate controversy (3-5 points)
- **7**: Significant controversy (6-8 points)
- **9**: Major controversies (9-11 points)
- **10**: Global scandal (12+ points)
- **NA**: No controversy data available

Example scoring:
```
If research shows: "Burton plagiarized from Payne (1885)" + "Banned in Saudi Arabia and Egypt"
Score: 5 (two significant controversies)
Evidence: "Burton plagiarism documented 1885, banned in 2 countries"
Confidence: 0.9
```

### PHILOSOPHICAL_DEPTH
- **0**: Pure entertainment, no deeper meaning
- **2**: Basic moral lesson or simple allegory
- **5**: 2-3 interpretive layers, some symbolism
- **7**: 4+ valid interpretations, rich symbolism, academic study
- **9**: Profound philosophical work, extensive scholarship
- **10**: Foundational philosophical text (e.g., Plato's Republic)
- **NA**: No philosophical analysis in research

### CULTURAL_PHENOMENON (lifetime cumulative)
- **0**: No adaptations or cultural references
- **2**: 1-2 adaptations (any medium)
- **5**: 3-10 distinct adaptations
- **7**: 11-30 adaptations across multiple media
- **9**: 50+ adaptations, major franchise
- **10**: 100+ adaptations, defines genre (e.g., Sherlock Holmes)
- **NA**: No cultural impact data available

Operational: Count each distinct work once (film=1, TV series=1 regardless of episodes, theatre production=1 per unique script)

### CONTEMPORARY_RECEPTION (last 5 years only)
- **0**: Zero social media presence
- **2**: <1000 social mentions/year (unique posts, not likes)
- **5**: 1K-100K mentions/year, 1-10 memes identified
- **7**: 100K-1M mentions/year, 11-50 memes, trending hashtags
- **9**: 1M+ posts/year, 51+ memes, BookTok phenomenon
- **10**: Viral phenomenon, defines online discourse
- **NA**: Pre-internet era book OR no social media data available

Operational: Count unique posts (not reposts/likes), 5-year window, deduplicate by author within 30 days

### RELEVANCE
- **0**: Purely historical interest
- **2**: Few themes still resonate
- **5**: Half of themes remain current
- **7**: Most themes highly relevant
- **9**: Eerily prophetic
- **10**: Defines current debates (e.g., 1984 on surveillance)
- **NA**: Cannot assess relevance

### INNOVATION
- **0**: Completely derivative
- **2**: Minor variations on established form
- **5**: Notable innovations within genre
- **7**: Created new subgenre or major technique
- **9**: Revolutionary, changed literature
- **10**: Created entirely new form (e.g., stream of consciousness)
- **NA**: Cannot assess innovation

### STRUCTURAL_COMPLEXITY
- **0**: Linear chronological narrative
- **2**: Minor flashbacks or subplot
- **5**: Multiple timelines OR narrators
- **7**: Complex structure with 3+ techniques
- **9**: Highly experimental form
- **10**: Defies conventional structure (e.g., Hopscotch by Cortázar)
- **NA**: Structure unclear from materials

### SOCIAL_ROLES
- **0**: No social commentary
- **2**: Minimal, stereotypical roles
- **5**: Some social awareness
- **7**: Strong social/gender analysis
- **9**: Defines social discourse
- **10**: Revolutionary social impact (e.g., Uncle Tom's Cabin)
- **NA**: No social commentary data

## Composite Score Calculation

### Mathematical Formulas

#### DEPTH (Intellectual and artistic sophistication)
```python
valid_scores = [s for s in [philosophical_depth, innovation, 
                structural_complexity, relevance] if s is not NA]
if len(valid_scores) >= 2:
    DEPTH = round(sum(valid_scores) / len(valid_scores), 1)  # half-up to 0.1
else:
    DEPTH = NA  # insufficient data
```

#### HEAT (Social engagement and cultural impact)
```python
valid_scores = [s for s in [controversy, social_roles, 
                contemporary_reception, cultural_phenomenon] if s is not NA]
if len(valid_scores) >= 2:
    HEAT = round(sum(valid_scores) / len(valid_scores), 1)  # half-up to 0.1
else:
    HEAT = NA  # insufficient data
```

#### Overall Confidence
```python
overall_confidence = count(scores != NA) / 8
# Accept if overall_confidence >= 0.5 (at least 4 valid dimensions)
```

### Binning Rules
- **Low**: < 4.0
- **Medium**: 4.0 - 5.9  
- **High**: ≥ 6.0
- **Boundary**: Values exactly on threshold (4.0, 6.0) round UP to higher category

### Overlap Prevention
To avoid double-counting between dimensions:
- **RELEVANCE**: Focus on contemporary applicability of themes
- **INNOVATION**: Focus on technical/formal breakthroughs at time of writing
- **STRUCTURAL_COMPLEXITY**: Focus on narrative architecture only
- Each dimension must cite different evidence

## Format Decision Matrix (DEPTH×HEAT → AFA)

### Primary Matrix
```
         HEAT →
DEPTH↓   Low              Medium           High
------------------------------------------------------
Low      casual_chat      dialogue         debate
         (6 min)          (9 min)          (11 min)

Medium   essay            exchange         symposium
         (11 min)         (13 min)         (15 min)

High     lecture          seminar          conference
         (15 min)         (17 min)         (19 min)
```

### Duration Rules
- Fixed duration per quadrant (no ranges)
- If distance to adjacent quadrant ≤ 0.2, add +1 minute
- Maximum duration: 20 minutes

### Alternative Format Selection
When distance to boundary ≤ 0.2:
1. **Priority**: HEAT boundary > DEPTH boundary
2. **Tie-break**: Choose longer format
3. **Example**: DEPTH=3.9, HEAT=3.9 → Check HEAT first → Alternative: dialogue

### AFA Format Mapping (1:1 Bijection)
```yaml
afa_format_codes:
  casual_chat: "casual_conversation"    # Low/Low
  dialogue: "natural_dialogue"          # Low/Medium
  debate: "heated_debate"               # Low/High
  essay: "essay_presentation"           # Medium/Low
  exchange: "friendly_exchange"         # Medium/Medium
  symposium: "panel_discussion"         # Medium/High
  lecture: "academic_lecture"           # High/Low
  seminar: "seminar_discussion"         # High/Medium
  conference: "conference_symposium"    # High/High
```

## Output Format

```yaml
book_id: "[folder_name]"
scoring_version: "2.1"
scorer: "AI"
date: "[ISO-8601 datetime]"
validation_status: "pending"

versioning:
  ruleset_version: "2.1.0"
  matrix_version: "1.0.0"
  data_sources_hash: "[SHA-256 of concatenated research files]"
  afa_mapping_version: "1.0.0"

metadata:
  era: "[pre_1800|1800_1900|1900_1950|1950_2000|post_2000]"
  genre: "[literary_fiction|genre_fiction|classics|philosophy|poetry|drama|non_fiction]"
  data_sources_used: ["research_file_1.md", "research_file_2.md"]

raw_scores:
  controversy:
    value: [0-10 or null]
    confidence: [0.0-1.0, precision 0.1]
    evidence: "[1-2 specific facts from research]"
    source_file: "[which research file provided evidence]"
    anchor_matched: [0|2|5|7|9|10|interpolated]
    
  philosophical_depth:
    value: [0-10 or null]
    confidence: [0.0-1.0]
    evidence: "[1-2 specific facts]"
    source_file: "[research file]"
    anchor_matched: [0|2|5|7|9|10|interpolated]
    
  cultural_phenomenon:
    value: [0-10 or null]
    confidence: [0.0-1.0]
    evidence: "[specific count of adaptations]"
    source_file: "[research file]"
    anchor_matched: [0|2|5|7|9|10|interpolated]
    
  contemporary_reception:
    value: [0-10 or null]
    confidence: [0.0-1.0]
    evidence: "[mention count, time window]"
    source_file: "[research file]"
    anchor_matched: [0|2|5|7|9|10|interpolated]
    
  relevance:
    value: [0-10 or null]
    confidence: [0.0-1.0]
    evidence: "[contemporary themes identified]"
    source_file: "[research file]"
    anchor_matched: [0|2|5|7|9|10|interpolated]
    
  innovation:
    value: [0-10 or null]
    confidence: [0.0-1.0]
    evidence: "[specific innovations noted]"
    source_file: "[research file]"
    anchor_matched: [0|2|5|7|9|10|interpolated]
    
  structural_complexity:
    value: [0-10 or null]
    confidence: [0.0-1.0]
    evidence: "[narrative techniques identified]"
    source_file: "[research file]"
    anchor_matched: [0|2|5|7|9|10|interpolated]
    
  social_roles:
    value: [0-10 or null]
    confidence: [0.0-1.0]
    evidence: "[social commentary aspects]"
    source_file: "[research file]"
    anchor_matched: [0|2|5|7|9|10|interpolated]

composite_scores:
  depth:
    value: [0.0-10.0, precision 0.1]
    calculation: "[show actual: (7+5+6+8)/4 = 6.5]"
    components_used: ["philosophical_depth", "innovation", etc.]
    components_missing: ["relevance"] 
    valid_component_count: 3
    category: "[low|medium|high]"
    
  heat:
    value: [0.0-10.0, precision 0.1]
    calculation: "[show actual: (3+4+NA+7)/3 = 4.7]"
    components_used: ["controversy", "social_roles", "cultural_phenomenon"]
    components_missing: ["contemporary_reception"]
    valid_component_count: 3
    category: "[low|medium|high]"

overall_confidence: 0.75  # 6 of 8 dimensions had data

format_recommendation:
  quadrant: "medium_heat_high_depth"
  matrix_position: "[row,col]"  # e.g., [3,2] for high depth, medium heat
  primary_format: "seminar"  # Must map 1:1 to afa_code
  afa_code: "seminar_discussion"  # Must be unique per format
  duration_minutes: 17
  alternative_format: "essay"  # if within 0.2 of boundary
  alternative_afa_code: "essay_presentation"
  distance_to_boundary: 0.2  # minimum distance to any quadrant boundary
  boundary_direction: "heat_low"  # which boundary is closest
  rationale: "High intellectual depth with moderate cultural heat suggests academic discussion format"

quality_assurance:
  anchors_used: true
  evidence_provided: true
  na_values_appropriate: true
  confidence_calibrated: true
  composites_valid: true
  minimum_data_met: true  # overall_confidence >= 0.5
  no_double_counting: true  # different evidence per dimension
```

## Example Scoring Process

Given research stating: "The book has been adapted into 3 films (1952, 1974, 2013), 2 TV series (BBC 1981 6 episodes, Netflix 2020 8 episodes), and one Broadway musical (1998). It sparked colonial debates in academic journals (1985-1990) with 47 scholarly articles. Banned in South Africa during apartheid. Current social media: 823 unique posts in 2024 on BookTok, 15 memes identified."

### Scoring:

1. **Cultural phenomenon**: 
   - Count: 3 films + 2 TV series + 1 musical = 6 distinct adaptations
   - Matches anchor 5: "3-10 distinct adaptations"
   - Score: 5.0, Confidence: 1.0
   - Evidence: "6 adaptations: 3 films, 2 TV series, 1 musical"

2. **Contemporary reception**:
   - Count: 823 posts/year, 15 memes
   - Between anchor 2 (<1000) and 5 (1K-100K)
   - Score: 2.5 (interpolated), Confidence: 0.9
   - Evidence: "823 BookTok posts 2024, 15 memes"

3. **Controversy**:
   - Points: Academic debates (1pt) + Country ban (2pts) = 3 total
   - Apply function: controversy_anchor(3) = 5
   - Score: 5.0, Confidence: 0.8
   - Evidence: "47 scholarly articles on colonialism, banned in South Africa"

### Composite Calculation:
```
DEPTH components: [philosophical_depth=6, innovation=4, structural_complexity=5, relevance=7]
DEPTH = (6 + 4 + 5 + 7) / 4 = 5.5 → Category: Medium

HEAT components: [controversy=5, social_roles=NA, contemporary_reception=2.5, cultural_phenomenon=5]
HEAT = (5 + 2.5 + 5) / 3 = 4.2 → Category: Medium

Overall confidence = 7/8 = 0.875 (only social_roles was NA)
```

### Format Decision:
- Quadrant: medium_heat_medium_depth → "exchange"
- Primary format: exchange
- AFA code: friendly_exchange
- Duration: 13 minutes (base)
- Distance to boundaries: 
  - HEAT to low boundary: |4.2 - 4.0| = 0.2
  - DEPTH to high boundary: |5.5 - 6.0| = 0.5
- Alternative check: HEAT distance ≤ 0.2, so check HEAT-adjacent quadrant
- Alternative format: essay (medium_depth_low_heat)

## CLI Validation

```bash
# Validation script checks before accepting output:
validate_scoring.py book_id-scoring.yaml

# Checks performed:
1. anchors_used: All scores map to defined anchors (0,2,5,7,9,10)
2. evidence_provided: Every non-NA score has evidence + source_file
3. composites_valid: DEPTH/HEAT calculated correctly with ≥2 components
4. confidence_calibrated: Confidence matches evidence quality
5. overall_confidence: ≥ 0.5 (minimum 4 valid dimensions)
6. format_mapping: Output format exists in afa_format_codes
7. schema_valid: Output matches JSON Schema

# Exit codes:
0 = valid, 1 = invalid structure, 2 = insufficient data, 3 = calculation error
```

### JSON Schema for Output Validation
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["book_id", "scoring_version", "versioning", "raw_scores", 
               "composite_scores", "overall_confidence", "format_recommendation"],
  "properties": {
    "book_id": {"type": "string"},
    "scoring_version": {"const": "2.1"},
    "versioning": {
      "type": "object",
      "required": ["ruleset_version", "matrix_version", "data_sources_hash"],
      "properties": {
        "ruleset_version": {"pattern": "^2\\.1\\.\\d+$"},
        "matrix_version": {"pattern": "^1\\.0\\.\\d+$"},
        "data_sources_hash": {"pattern": "^[a-f0-9]{64}$"}
      }
    },
    "raw_scores": {
      "type": "object",
      "patternProperties": {
        "^(controversy|philosophical_depth|cultural_phenomenon|contemporary_reception|relevance|innovation|structural_complexity|social_roles)$": {
          "type": "object",
          "required": ["value", "confidence"],
          "properties": {
            "value": {"oneOf": [{"type": "number", "minimum": 0, "maximum": 10}, {"type": "null"}]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "anchor_matched": {"enum": [0, 2, 5, 7, 9, 10, "interpolated", null]}
          }
        }
      }
    },
    "composite_scores": {
      "type": "object",
      "required": ["depth", "heat"],
      "properties": {
        "depth": {
          "properties": {
            "value": {"oneOf": [{"type": "number"}, {"type": "null"}]},
            "category": {"enum": ["low", "medium", "high", null]}
          }
        },
        "heat": {
          "properties": {
            "value": {"oneOf": [{"type": "number"}, {"type": "null"}]},
            "category": {"enum": ["low", "medium", "high", null]}
          }
        }
      }
    },
    "overall_confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "format_recommendation": {
      "type": "object",
      "required": ["primary_format", "afa_code", "duration_minutes"],
      "properties": {
        "primary_format": {"enum": ["casual_chat", "dialogue", "debate", "essay", "exchange", "symposium", "lecture", "seminar", "conference"]},
        "afa_code": {"enum": ["casual_conversation", "natural_dialogue", "heated_debate", "essay_presentation", "friendly_exchange", "panel_discussion", "academic_lecture", "seminar_discussion", "conference_symposium"]},
        "duration_minutes": {"type": "integer", "minimum": 6, "maximum": 20}
      }
    }
  }
}
```

## Quality Checks

Before submitting:
1. ✓ Used behavioral anchors, not arbitrary numbers?
2. ✓ Each score backed by specific evidence?
3. ✓ NA values used where data insufficient?
4. ✓ Confidence scores reflect data quality?
5. ✓ Composite scores calculated correctly?
6. ✓ Format follows DEPTH×HEAT matrix?

## Critical Reminders

- **Never guess** - Use NA when unsure
- **Interpolate carefully** - If between anchors, explain why
- **Era matters** - A 1700s book won't have TikTok presence (NA, not 0)
- **Confidence is key** - Low confidence flags human review need
- **Evidence is mandatory** - No score without citation
- **Minimum data** - Need at least 2 dimensions per composite for valid score

## Calibration Protocol

### Inter-rater reliability
- Test on 30-50 book sample
- Target Cohen's κ > 0.7
- Document disagreements for rubric refinement

### Validation markers
- Books with known high DEPTH: Ulysses, Being and Time, Gravity's Rainbow
- Books with known high HEAT: Harry Potter, Fifty Shades, Da Vinci Code
- Books with both: 1984, To Kill a Mockingbird, The Great Gatsby

### Common pitfalls to avoid
1. Conflating popularity with quality (separate HEAT from DEPTH)
2. Recency bias (adjust expectations by era)
3. Genre bias (innovation relative to genre norms)
4. Missing data imputation (use NA, don't guess)
5. Over-confidence (calibrate to actual evidence quality)

## Optional Advanced Features

### Confidence-Weighted Tie-Breaking
When two dimensions have identical scores but different confidence:
```python
# Only for tie-breaking, not main calculation
if score_a == score_b and confidence_a != confidence_b:
    use_higher_confidence_dimension()
```

### Era Normalization (Experimental)
For social metrics, calculate z-scores within era cohorts:
```python
def normalize_by_era(score, dimension, era):
    era_mean = ERA_MEANS[era][dimension]
    era_std = ERA_STDS[era][dimension]
    return (score - era_mean) / era_std

# Pre-computed from 50-book validation set:
ERA_MEANS = {
    "pre_1800": {"contemporary_reception": NA, "cultural_phenomenon": 3.2},
    "1800_1900": {"contemporary_reception": NA, "cultural_phenomenon": 4.5},
    # etc...
}
```
Note: Current NA rules and era adjustments are sufficient for v2.1.1

## Version History

### v2.1.1 (Current) - Final Standardization
- Enforced 1:1 bijection between formats and AFA codes
- Fixed duration to single minutes (removed range midpoint rule)
- Added hierarchy for alternative format selection (HEAT > DEPTH > duration)
- Formalized controversy point-to-anchor function
- Added versioning fields (ruleset, matrix, data_sources_hash)
- Implemented JSON Schema for output validation
- Clarified tie-breaking rules for boundary cases

### v2.1.0 - Full Standardization
- Added precise mathematical formulas for composites
- Operationalized all dimension definitions
- Implemented weighted controversy scoring
- Added AFA format code mapping
- Specified deduplication and counting rules
- Added CLI validation framework
- Defined 0.2 threshold for alternative formats
- Implemented half-up rounding to 0.1 precision
- Added minimum data requirements (≥0.5 overall confidence)

### v2.0 - Behavioral Anchors
- Introduced 0-2-5-7-9-10 anchor system
- Created DEPTH×HEAT composite metrics
- Added NA value handling
- Implemented confidence scoring

### v1.0 - Original
- Basic 8-dimension scoring
- Linear 0-10 scales without anchors

## Summary v2.1.1

**Core System**: Behavioral anchors (0,2,5,7,9,10) with NA handling → DEPTH×HEAT composites → 3×3 format matrix → AFA codes

**Key Rules**:
- Minimum 2 dimensions per composite, overall confidence ≥ 0.5
- 1:1 bijection format↔AFA code (9 unique pairs)
- Fixed durations 6-19 minutes
- Alternative format when distance ≤ 0.2 (HEAT priority > DEPTH)
- Controversy uses point-to-anchor function
- All calculations round half-up to 0.1

**Validation**: JSON Schema + CLI validator with 7 checks

This version (v2.1.1) is production-ready and fully standardized.