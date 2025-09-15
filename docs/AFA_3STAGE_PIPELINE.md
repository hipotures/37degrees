# AFA 3-Stage Pipeline Architecture

## Overview
The Audio Format Analysis (AFA) system now operates as a clean 3-stage pipeline, separating concerns and improving maintainability.

---

## Stage 1: Research Collection
**Purpose**: Gather comprehensive research materials about the book

### Input
- Book title and basic metadata

### Process
- Multiple specialized research agents run in parallel
- Each agent focuses on specific aspects (culture, history, youth relevance, etc.)

### Output
- Markdown files in `books/NNNN_bookname/docs/findings/`
- Typically 15-25 research files per book

### Tools
- Research agents: `au-culture-impact`, `au-dark-drama`, `au-facts-history`, etc.
- Orchestrated by: `37d-research` command

---

## Stage 2: Scoring & Analysis
**Purpose**: Analyze research materials and generate quantitative scores

### Input
- Research files from Stage 1 (`docs/findings/*.md`)

### Process
- AI analyzes all research materials
- Generates scores for 8 behavioral dimensions:
  - controversy (1-10)
  - philosophical_depth (1-10)
  - cultural_phenomenon (1-10)
  - contemporary_reception (1-10)
  - relevance (1-10)
  - innovation (1-10)
  - structural_complexity (1-10)
  - social_roles (1-10)

### Output
Updated `book.yaml` with:
```yaml
afa_analysis:
  version: "3.0"
  processed_at: "2025-09-15T08:42:00Z"
  scores:
    controversy: 7
    philosophical_depth: 9
    cultural_phenomenon: 8
    # ... all 8 dimensions
  # NO composite_scores - simplified system uses raw scores directly
```

### Tools
- Scoring agent: `37d-a6-afa-analyzer-v2`
- **NOTE**: DEPTH/HEAT composite scores removed - not needed

---

## Stage 3: Format Selection
**Purpose**: Select the most appropriate dialogue format based on scores and genre

### Input
- `afa_analysis.scores` from book.yaml
- `book_info.genre` from book.yaml
- Format usage statistics from `output/afa_format_counts.json`

### Process
Two options available:

#### Option A: Python Selector (Recommended)
- Fast, deterministic algorithm
- Genre-based preferences
- Score-based modifiers
- Distribution balancing
- No LLM required

#### Option B: AI Agent Selector
- More nuanced understanding
- Can read research content (if needed)
- Non-deterministic
- Requires LLM

### Output
Selected format added to book.yaml:
```yaml
afa_analysis:
  formats:
    name: "emotional_perspective"
    duration: 18
    confidence: 0.85
    reasoning: "Gothic genre demands emotional exploration"
```

### Tools
- Python selector: `scripts/afa_format_selector.py`
- AI agent: `37d-afa-format-selector`

---

## Pipeline Execution

### Full Pipeline
```bash
# Stage 1: Research
/37d-research "Wuthering Heights"

# Stage 2: Scoring (after research completes)
python scripts/afa/run_afa_analysis.py books/0037_wuthering_heights

# Stage 3: Format Selection
python scripts/afa_format_selector.py books/0037_wuthering_heights
```

### Stage 3 Only (when scores exist)
```bash
# Quick format selection
python scripts/afa_format_selector.py books/0037_wuthering_heights

# Or with AI agent for complex cases
/task "37d-afa-format-selector" "books/0037_wuthering_heights"
```

---

## Benefits of 3-Stage Architecture

1. **Separation of Concerns**
   - Research is independent of analysis
   - Scoring is independent of format selection
   - Each stage can be improved independently

2. **Flexibility**
   - Can re-run format selection without re-scoring
   - Can test different selection algorithms
   - Can manually override any stage

3. **Transparency**
   - Clear data flow between stages
   - Each stage produces inspectable output
   - Easy to debug and audit

4. **Performance**
   - Stage 3 is very fast (<100ms with Python)
   - Can batch process format selection
   - No need to re-run expensive stages

5. **Maintainability**
   - Simple to update selection logic
   - Easy to add new formats
   - Clear integration points

---

## Format Distribution Goals

Target distribution (balanced):
- Each format: 10-15% usage
- No format > 25% usage
- All 8 formats used across collection

Current distribution tracking:
- File: `output/afa_format_counts.json`
- Updated after each selection
- Used for balancing in Stage 3

---

## Migration Notes

### From Old System
1. Books with existing scores can skip Stage 1 & 2
2. Run Stage 3 to update format selection
3. Gradually reprocess books needing format updates

### Key Changes
- `process_afa_scoring.py` → `process_afa_scoring_v2.py` (no format selection)
- Mathematical format selection → Intelligent selection (genre + scores)
- Rigid rules → Soft preferences with balancing

---

## Next Steps

1. Update all books with Stage 3 format selection
2. Monitor format distribution improvement
3. Fine-tune selection weights based on results
4. Consider adding quality validation stage