# AFA AI Format Selector - Flexible Prompt Design

## Philosophy: Guidance Without Rigidity

This document defines the flexible prompting approach for AI-based format selection that avoids both rigid rules and unconstrained chaos.

---

## Core Principles

### 1. Soft Preferences, Not Hard Rules
Instead of: "NEVER use academic_analysis for children's books"
We say: "Children's literature often resonates better with exploratory or narrative formats, though exceptions exist when philosophical depth warrants academic treatment"

### 2. Evidence-Based Justification
The AI must always cite specific content from research findings. This prevents hallucination and ensures grounded decisions.

### 3. Statistical Awareness Without Quotas
The AI knows current usage patterns but isn't forced to meet quotas. It considers diversity as one factor among many.

### 4. Genre Sensitivity With Flexibility
Different genres have natural affinities, but context can override default preferences.

---

## The Three-Layer Decision Framework

### Layer 1: Genre Affinity Signals
These are starting points, not destinations:

```
Children's/YA Literature:
  Strong affinity: exploratory_dialogue, narrative_reconstruction
  Moderate affinity: emotional_perspective (for coming-of-age)
  Weak affinity: academic_analysis (unless exceptional depth exists)

Gothic/Romance:
  Strong affinity: emotional_perspective
  Moderate affinity: cultural_dimension (for period romances)
  Weak affinity: academic_analysis (unless scholarly tradition exists)

Philosophy/Theory:
  Strong affinity: academic_analysis, critical_debate
  Moderate affinity: temporal_context (for historical philosophy)
  Weak affinity: narrative_reconstruction (unless structure demands it)

Social/Political:
  Strong affinity: social_perspective, critical_debate
  Moderate affinity: temporal_context, cultural_dimension
  Context-dependent: all others

Historical Fiction:
  Strong affinity: temporal_context
  Moderate affinity: cultural_dimension, social_perspective
  Context-dependent: all others

Fantasy/Sci-Fi:
  Strong affinity: exploratory_dialogue, narrative_reconstruction
  Moderate affinity: cultural_dimension (for world-building)
  Context-dependent: all others
```

### Layer 2: Evidence Requirements
Each format needs supporting evidence to be viable. **WITHOUT SUFFICIENT EVIDENCE, DO NOT PROCEED WITH FORMAT SELECTION.**

```
PREREQUISITE FOR ALL FORMATS:
  Minimum: At least 3 research files in docs/findings/
  Required: Clear thematic content to support dialogue

academic_analysis:
  Minimum: 2+ files with theoretical/symbolic content
  Ideal: Explicit academic frameworks mentioned

critical_debate:
  Minimum: Documented controversy or multiple interpretations
  Ideal: Opposing critical views clearly articulated

temporal_context:
  Minimum: Historical period data + modern relevance
  Ideal: Evolution of reception across eras

cultural_dimension:
  Minimum: 2+ distinct cultural contexts discussed
  Ideal: Translation/adaptation differences documented

social_perspective:
  Minimum: Social themes + systemic analysis present
  Ideal: Links to movements or current issues

emotional_perspective:
  Minimum: Psychological/emotional themes prominent
  Ideal: Trauma, relationships, or development focus

exploratory_dialogue:
  Minimum: Sufficient interesting facts/discoveries
  Ideal: World-building or mystery elements

narrative_reconstruction:
  Minimum: Complex structure or unreliable narration noted
  Ideal: Multiple perspectives or timeline complexity
```

**IMPORTANT:** If research materials are insufficient (< 3 files or lacking substance), the process should STOP. Do not attempt to select a format without proper research foundation.

### Layer 3: Balancing Factors
Applied only when multiple formats are viable:

```
Distribution Awareness:
- If format X is used >25% and format Y <5%, slight preference to Y
- Never force a bad fit for distribution's sake
- Weight: 15% of decision

Freshness Factor:
- If a format hasn't been used in 10+ books, slight boost
- If just used in last 2 books, slight penalty
- Weight: 10% of decision

Audience Resonance:
- Youth engagement potential matters
- Prefer accessible over academic when equal
- Weight: 20% of decision

Evidence Strength:
- More specific evidence > general claims
- Recent research > historical only
- Weight: 55% of decision (primary factor)
```

---

## Prompt Template Structure

```markdown
You are selecting a dialogue format for [BOOK TITLE] by [AUTHOR].

CONTEXT PROVIDED:
- Book metadata (genre, year, themes)
- Analytical scores (DEPTH, HEAT, etc.)
- Research findings summaries
- Current format distribution statistics

YOUR TASK:
Select the most appropriate format considering:
1. Natural fit with the book's character
2. Support from available research materials
3. Engagement potential for young audiences
4. Contribution to format diversity (when appropriate)

REMEMBER:
- Cite specific evidence from findings (required)
- Consider but don't obsess over statistics
- Stop process if research materials are insufficient
- Explain your reasoning transparently

GENRE HINTS (not rules):
[Insert relevant genre affinity signals]

CURRENT STATISTICS:
[Insert usage data with context]

OUTPUT:
Structured JSON with reasoning
```

---

## Example Decisions

### Example 1: Wuthering Heights
**Genre signals:** Gothic romance → emotional_perspective (strong), academic_analysis (weak)
**Evidence check:** Extensive material on toxic relationships, trauma cycles ✓
**Distribution:** emotional_perspective underused (1/39 books)
**Decision:** emotional_perspective
**Reasoning:** "Gothic intensity and psychological trauma themes in findings support emotional exploration over academic distance"

### Example 2: The Hobbit
**Genre signals:** Children's fantasy → exploratory_dialogue (strong), narrative_reconstruction (strong)
**Evidence check:** Adventure elements, world-building documented ✓
**Distribution:** Both formats unused (0/39 books)
**Decision:** narrative_reconstruction
**Reasoning:** "Quest structure with episodic adventures suits detective-style reconstruction, findings emphasize journey discoveries"

### Example 3: Crime and Punishment
**Genre signals:** Psychological philosophy → academic_analysis OR emotional_perspective
**Evidence check:** Both philosophical frameworks AND psychological depth present ✓
**Distribution:** academic_analysis overused (28%), emotional underused (2.5%)
**Decision:** emotional_perspective
**Reasoning:** "While philosophical, the psychological torment and guilt themes dominate findings, and emotional perspective offers fresh angle"

---

## Anti-Patterns to Avoid

### ❌ The Default Trap
"This is complex, so academic_analysis" - Complexity alone doesn't determine format

### ❌ The Distribution Override
"Exploratory is unused, so force it here" - Never sacrifice fit for statistics

### ❌ The Vague Justification
"This seems like it would work" - Always cite specific evidence

### ❌ The Genre Straightjacket
"Gothic must be emotional" - Genre guides but doesn't dictate

### ❌ The Hallucination Risk
"The findings probably discuss..." - Only cite what's actually there

---

## Success Metrics

A good format selection:
1. **Feels natural** - Format suits the book's essential character
2. **Has evidence** - Specific findings support the choice
3. **Engages audience** - Young people will connect with approach
4. **Adds variety** - Contributes to format diversity (when possible)
5. **Explains clearly** - Reasoning is transparent and logical

---

## Integration Notes

This flexible approach:
- Replaces rigid mathematical selection
- Maintains quality through evidence requirements
- Achieves diversity through gentle preferences
- Adapts to each book's unique character
- Provides clear audit trail through reasoning

The key insight: We don't need perfect rules or perfect freedom. We need intelligent guidance with accountability.