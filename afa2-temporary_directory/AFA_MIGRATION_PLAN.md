# Audio Format Analyzer (AFA) System Migration Plan

## Executive Summary
Complete redesign of the Audio Format Analysis system for the 37degrees project, transitioning from a complex manual scoring system to an AI-driven automated analyzer that processes research findings to generate audio format selections and podcast scripts.

## System Comparison

### Current System (Legacy AFA)
- **Complexity**: 9 scoring dimensions (A-I)
- **Formats**: 12+ audio formats with complex rotation
- **Data Storage**: CSV files (audio_format_scores.csv, audio_format_output.csv)
- **Processing**: Multiple specialized agents
- **Output**: Separate PL/EN markdown files per book
- **Manual Work**: Extensive manual scoring required

### New System (Streamlined AFA)
- **Complexity**: 8 scoring dimensions aggregated to DEPTH×HEAT composites
- **Formats**: 9 formats from 3×3 matrix (Low/Medium/High for each axis)
- **Data Storage**: JSON/YAML with automatic generation
- **Processing**: AI-driven scoring using behavioral anchors (0-2-5-7-9-10)
- **Output**: Unified bilingual documents
- **Automation**: AI analyzes au-research_*.md files using ai-scoring-prompt.md

## Architecture Overview

```
37degrees/
├── src/
│   └── afa/                        # New AFA module
│       ├── __init__.py
│       ├── analyzer.py              # Core AFAAnalyzer with DEPTH×HEAT
│       ├── research_processor.py    # Process au-research_*.md
│       ├── ai_scorer.py            # AI-based scoring engine
│       ├── prompt_generator.py     # NotebookLM prompts
│       └── book_updater.py         # Updates book.yaml with afa_analysis
├── config/
│   ├── afa_formats.yaml           # 9 format definitions (3×3 matrix)
│   └── afa_settings.yaml          # System configuration
└── books/
    └── NNNN_book/
        ├── book.yaml               # UPDATED with afa_analysis: section (output)
        └── docs/
            └── findings/           # au-research_*.md files (input)
```

## Component Breakdown

### 1. Core Analyzer (`src/afa/analyzer.py`)
**Status**: Needs adaptation - minimal-afa-system.py uses different model

**Responsibilities**:
- Receive scores from AI Scorer (8 dimensions)
- Calculate DEPTH and HEAT composites
- Map to 3×3 format matrix
- Generate NotebookLM prompts

**Key Classes**:
```python
class AFAAnalyzer:
    def calculate_composites(raw_scores: Dict) -> Tuple[float, float]  # DEPTH, HEAT
    def select_format(depth: float, heat: float) -> FormatChoice  # From 3×3 matrix
    def process_book(book_data: Dict, ai_scores: Dict) -> AFADocument
```

### 2. Research Processor (`src/afa/research_processor.py`)
**Status**: Needs creation

**Responsibilities**:
- Parse au-research_*.md files
- Extract structured findings
- Aggregate research data
- Prepare for AI scoring

**Input Files**:
- `au-research_facts_history.md` - Historical facts
- `au-research_culture_impact.md` - Cultural influence
- `au-research_symbols_meanings.md` - Symbolic analysis
- `au-research_dark_drama.md` - Controversies
- `au-research_youth_digital.md` - Modern relevance
- `au-research_writing_innovation.md` - Literary innovation
- `au-research_local_context.md` - Polish context
- `au-research_reality_wisdom.md` - Life lessons

### 3. AI Scorer (`src/afa/ai_scorer.py`)
**Status**: Instructions ready in `ai-scoring-prompt.md`

**Responsibilities**:
- Load and concatenate au-research_*.md files
- Apply behavioral anchors from ai-scoring-prompt.md
- Generate 8 dimension scores using LLM
- Return structured scoring with confidence levels

**Scoring Mappings (8 dimensions)**:
```python
RESEARCH_TO_DIMENSIONS = {
    'CONTROVERSY': ['au-research_dark_drama.md'],
    'PHILOSOPHICAL_DEPTH': ['au-research_symbols_meanings.md'],
    'CULTURAL_PHENOMENON': ['au-research_culture_impact.md'],
    'CONTEMPORARY_RECEPTION': ['au-research_youth_digital.md'],
    'RELEVANCE': ['au-research_reality_wisdom.md', 'au-research_local_context.md'],
    'INNOVATION': ['au-research_writing_innovation.md'],
    'STRUCTURAL_COMPLEXITY': ['au-research_writing_innovation.md'],
    'SOCIAL_ROLES': ['au-research_local_context.md', 'au-research_facts_history.md']
}

# Aggregation to composites:
# DEPTH = avg(philosophical_depth, innovation, structural_complexity, relevance)
# HEAT = avg(controversy, social_roles, contemporary_reception, cultural_phenomenon)
```

### 4. Prompt Generator (`src/afa/prompt_generator.py`)
**Status**: Ready to adapt from `afa-prompt-generator.py`

**Responsibilities**:
- Generate NotebookLM prompts
- Create host personas
- Structure dialogue segments
- Support bilingual output

### 5. Book Updater (`src/afa/book_updater.py`)
**Status**: Needs creation

**Responsibilities**:
- Load existing book.yaml
- Merge afa_analysis section
- Preserve existing data
- Save updated book.yaml

### 6. Format Configuration (`config/afa_formats.yaml`)
**Status**: Needs creation based on 3×3 matrix

**Format Matrix (9 formats)**:
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

**AFA Format Codes (1:1 mapping)**:
```yaml
format_mapping:
  casual_chat: "casual_conversation"     # Low DEPTH, Low HEAT
  dialogue: "natural_dialogue"           # Low DEPTH, Medium HEAT
  debate: "heated_debate"                # Low DEPTH, High HEAT
  essay: "essay_presentation"            # Medium DEPTH, Low HEAT
  exchange: "friendly_exchange"          # Medium DEPTH, Medium HEAT
  symposium: "panel_discussion"          # Medium DEPTH, High HEAT
  lecture: "academic_lecture"            # High DEPTH, Low HEAT
  seminar: "seminar_discussion"          # High DEPTH, Medium HEAT
  conference: "conference_symposium"     # High DEPTH, High HEAT
```

## Implementation Phases

### Phase 1: Foundation (Days 1-3)
1. **Create module structure**
   ```bash
   mkdir -p src/afa
   touch src/afa/__init__.py
   ```

2. **Create AFAAnalyzer**
   - Implement DEPTH×HEAT composite calculation
   - Map to 3×3 format matrix
   - Handle NA values per ai-scoring-prompt.md

3. **Create format configuration**
   - Define all 9 formats in YAML
   - Include bilingual support
   - Map to AFA codes (1:1 bijection)

### Phase 2: Research Integration (Days 4-6)
1. **Build research processor**
   ```python
   class ResearchProcessor:
       def load_research_files(book_folder: str) -> Dict[str, str]
       def extract_findings(content: str) -> List[Finding]
       def aggregate_research(findings: Dict) -> ResearchSummary
   ```

2. **Implement finding extractor**
   - Parse markdown structure
   - Extract [FACT], [DISPUTE], [ANALYSIS] tags
   - Capture certainty percentages

### Phase 3: AI Integration (Days 7-9)
1. **Create AI scorer**
   ```python
   class AIScorer:
       def load_scoring_prompt() -> str  # Load ai-scoring-prompt.md
       def analyze_research(research_files: Dict[str, str]) -> Dict
       def validate_anchors(scores: Dict) -> bool  # Check 0-2-5-7-9-10
   ```

2. **Use existing prompt from ai-scoring-prompt.md**
   - Load behavioral anchors definitions
   - Apply scoring rules
   - Calculate DEPTH and HEAT composites
   - Validate confidence levels

### Phase 4: Output Generation (Days 10-12)
1. **Implement book updater**
   - Load existing book.yaml
   - Add/update afa_analysis section
   - Preserve all other book data
   - Save updated book.yaml

2. **NotebookLM prompt generation**
   - Generate host prompts based on format
   - Create dialogue structure
   - Add timing segments
   - Export as text for copy-paste

### Phase 5: CLI Integration (Days 13-14)
1. **Add to main.py**
   ```python
   @cli.command()
   @click.argument('book_id')
   @click.option('--language', default='pl')
   def afa(book_id: str, language: str):
       """Generate AFA analysis for a book"""
       agent = MinimalAFAAgent()
       processor = ResearchProcessor()
       scorer = AIScorer()
       # ... implementation
   ```

2. **Batch processing**
   ```python
   @cli.command()
   @click.argument('collection')
   def afa_batch(collection: str):
       """Process entire collection"""
   ```

### Phase 6: Testing & Migration (Days 15-16)
1. **Create test suite**
   - Unit tests for each component
   - Integration tests
   - Sample book processing

2. **Migration scripts**
   - Convert CSV data to new format
   - Validate migrated data
   - Generate comparison reports

## File Templates

### `src/afa/__init__.py`
```python
"""Audio Format Analyzer - Streamlined AFA System"""

from .analyzer import MinimalAFAAgent
from .research_processor import ResearchProcessor
from .ai_scorer import AIScorer
from .prompt_generator import PromptGenerator

__version__ = '2.0.0'
__all__ = ['MinimalAFAAgent', 'ResearchProcessor', 'AIScorer', 'PromptGenerator']
```

### Sample Output Structure (book.yaml with afa_analysis section)
```yaml
# books/0001_alice_in_wonderland/book.yaml
book_info:
  title: "Alice's Adventures in Wonderland"
  author: "Lewis Carroll"
  year: 1865
  translations: 174
  # ... existing book metadata ...

afa_analysis:  # NEW SECTION ADDED BY AFA SYSTEM
  version: "2.1"
  processed_at: "2024-09-11T18:00:00Z"
  
  raw_scores:
    controversy:
      value: 5.0
      confidence: 0.8
      evidence: "Banned in China 1931, pedophilia theories discredited"
      anchor_matched: 5
    philosophical_depth:
      value: 7.0
      confidence: 0.9
      evidence: "4+ interpretive layers, Jungian archetypes"
      anchor_matched: 7
    cultural_phenomenon:
      value: 9.0
      confidence: 1.0
      evidence: "60+ adaptations, defines genre"
      anchor_matched: 9
    contemporary_reception:
      value: 7.0
      confidence: 0.9
      evidence: "2B+ TikTok views, rabbit hole metaphor"
      anchor_matched: 7
    # ... other 4 dimensions ...

  composite_scores:
    depth:
      value: 7.5
      category: "high"
    heat:
      value: 6.2
      category: "high"

  format_recommendation:
    primary_format: "conference"
    afa_code: "conference_symposium"
    duration_minutes: 19
    
  themes:  # Key findings from research
    - id: "mathematical_satire"
      type: "FACT"
      content: "Carroll critiqued new mathematics through nonsense"
    - id: "portmanteau_invention"
      type: "FACT"
      content: "Invented portmanteau words technique"

  prompts:  # Generated for NotebookLM
    pl:
      host_a: "Jesteś ekspertem literackim..."
      host_b: "Jesteś krytykiem kulturowym..."
    en:
      host_a: "You are a literary expert..."
      host_b: "You are a cultural critic..."
```

## Components Status

### ✅ READY (in afa2-temporary_directory)
- `ai-scoring-prompt.md` - Complete AI scoring instructions with behavioral anchors
- `afa-prompt-generator.py` - Prompt generation framework (needs adaptation)
- `minimal-afa-system.py` - Reference implementation (different model than required)
- `AFA_MIGRATION_PLAN.md` - This migration plan document

### 🔧 NEEDS ADAPTATION
- `minimal-afa-system.py` → Must be rewritten for 8 dimensions and DEPTH×HEAT model
- `afa-prompt-generator.py` → Adapt for 9 formats from 3×3 matrix
- Integration with existing book.yaml structure
- Connection to au-research_*.md files

### ❌ NEEDS CREATION
- **AFAAnalyzer** - Core analyzer using DEPTH×HEAT composites
- **AI Scorer Implementation** - LLM integration using ai-scoring-prompt.md
- **Research Parser** - Extract and concatenate au-research files
- **Book Updater** - Add/update afa_analysis section in book.yaml
- **Format Configuration YAML** - 9 formats with bilingual definitions
- **CLI Commands** - Integration with main.py
- **Validation Script** - Check scores against behavioral anchors

## Success Metrics
1. **Automation**: 90% reduction in manual scoring effort
2. **Consistency**: Uniform scoring across all books using behavioral anchors
3. **Quality**: AI-generated scores validated against anchors (0-2-5-7-9-10)
4. **Speed**: Process 100 books in under 10 minutes
5. **Integration**: Seamless fit with existing 37degrees workflow

## Risk Mitigation
1. **AI Hallucination**: Validate scores against research content
2. **Format Bias**: Monitor distribution statistics
3. **Language Quality**: Review bilingual outputs
4. **Backward Compatibility**: Maintain adapter for old format

## Timeline
- **Week 1**: Foundation and core components
- **Week 2**: AI integration and research processing
- **Week 3**: Output generation and CLI
- **Week 4**: Testing, migration, and deployment

## Next Steps
1. ✅ Create this migration plan document (DONE)
2. ✅ Analyze ai-scoring-prompt.md structure (DONE)
3. ⏳ Create AFAAnalyzer for DEPTH×HEAT composites
4. ⏳ Implement Research Parser for au-research files
5. ⏳ Create AI Scorer using ai-scoring-prompt.md
6. ⏳ Build Format Configuration YAML (9 formats)
7. ⏳ Add CLI command: `python main.py afa <book_id>`
8. ⏳ Create validation script for behavioral anchors
9. ⏳ Test with sample books (0001-0010)
10. ⏳ Full migration of all books

## Notes
- All code and documentation in English
- Polish content only in user-facing outputs
- Maintain separation between analysis and generation
- Focus on maintainability and extensibility
- Document all AI prompts and scoring logic