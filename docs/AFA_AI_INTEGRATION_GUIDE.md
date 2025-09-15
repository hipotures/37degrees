# AFA AI Format Selector - Integration Guide

## Overview
This guide documents how to integrate the AI-based format selector into the existing 37degrees AFA system, replacing the mathematical approach while maintaining fallback capabilities.

---

## Current System Architecture

### Before (Mathematical Selection)
```
1. Behavioral scoring (8 dimensions) →
2. Calculate DEPTH & HEAT composites →
3. Map to matrix cells (low/medium/high) →
4. Select format from candidates →
5. Apply frequency balancing
```

### After (AI-Based Selection)
```
1. Behavioral scoring (8 dimensions) →
2. Calculate DEPTH & HEAT (for context) →
3. Prepare AI context (book data + findings + stats) →
4. AI selects format with reasoning →
5. Validate and update statistics
```

---

## Integration Points

### 1. Primary Integration - AFA Analysis Pipeline

**File:** `scripts/afa/afa_analyzer.py` (or similar)

**Current flow:**
```python
# After getting scores from AI
depth, heat = calculate_depth_heat_composites(scores)
format = select_format_from_matrix(depth_category, heat_category)
```

**New flow:**
```python
# After getting scores from AI
from afa_ai_selector import select_format_with_ai

# Prepare book directory path
book_dir = Path(f"books/{book_id}")

# Use AI selector
ai_result = select_format_with_ai(book_dir, ai_function=your_ai_client)

# Extract format
format = ai_result['selected_format']
reasoning = ai_result['primary_reasoning']

# Log for audit
print(f"Selected {format}: {reasoning}")
```

### 2. Research Materials Check

Ensure sufficient research before format selection:

```python
def can_process_book(book_dir: Path) -> Tuple[bool, str]:
    """Check if book has sufficient research materials for processing"""

    findings_dir = book_dir / "docs" / "findings"

    if not findings_dir.exists():
        return False, "No findings directory exists"

    md_files = list(findings_dir.glob("*.md"))

    if len(md_files) < 3:
        return False, f"Insufficient research files: {len(md_files)} found, minimum 3 required"

    # Check if files have substantial content
    empty_files = []
    for file in md_files:
        content = file.read_text()
        if len(content.strip()) < 100:
            empty_files.append(file.name)

    if empty_files:
        return False, f"Research files lack content: {', '.join(empty_files)}"

    return True, "Sufficient research materials available"


def select_format_robust(book_dir: Path, ai_client=None):
    """Select format with AI only if sufficient research exists"""

    # First check if we can process this book
    can_process, reason = can_process_book(book_dir)

    if not can_process:
        raise ValueError(
            f"Cannot process {book_dir.name}: {reason}. "
            "Research materials must be generated first."
        )

    # Proceed with AI selection
    try:
        result = select_format_with_ai(book_dir, ai_client)
        return result
    except Exception as e:
        # No fallback - if AI fails, we stop
        raise ValueError(f"Format selection failed: {e}")
```

### 3. Statistics Update

After selection, update the counters:

```python
def update_format_statistics(selected_format: str):
    """Update format usage statistics after selection"""

    stats_path = Path("output/afa_format_counts.json")

    # Load current stats
    if stats_path.exists():
        with open(stats_path, 'r') as f:
            stats = json.load(f)
    else:
        stats = initialize_empty_stats()

    # Update counts
    stats['counts'][selected_format] += 1

    # Update books_since_last
    for fmt in stats['books_since_last']:
        if fmt == selected_format:
            stats['books_since_last'][fmt] = 0
        else:
            stats['books_since_last'][fmt] += 1

    # Save
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
```

---

## AI Client Integration

### Option 1: OpenAI API
```python
def create_openai_client():
    import openai

    client = openai.Client(api_key=os.getenv('OPENAI_API_KEY'))

    def ai_function(prompt):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a literary format selector."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content

    return ai_function
```

### Option 2: Anthropic Claude
```python
def create_claude_client():
    from anthropic import Anthropic

    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    def ai_function(prompt):
        response = client.messages.create(
            model="claude-3-opus-20240229",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.content[0].text

    return ai_function
```

### Option 3: Local LLM
```python
def create_local_llm_client():
    # Using Ollama or similar
    import requests

    def ai_function(prompt):
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama2',
                'prompt': prompt,
                'format': 'json'
            }
        )
        return response.json()['response']

    return ai_function
```

---

## Migration Strategy

### Phase 1: Parallel Testing
1. Run both systems in parallel
2. Log both selections
3. Compare results
4. Measure improvement metrics

```python
def test_parallel_selection(book_dir: Path):
    # Get both selections
    ai_result = select_format_with_ai(book_dir)
    math_result = select_format_mathematical(book_dir)

    # Log comparison
    log_entry = {
        'book': book_dir.name,
        'ai_format': ai_result['selected_format'],
        'math_format': math_result['selected_format'],
        'match': ai_result['selected_format'] == math_result['selected_format'],
        'ai_confidence': ai_result['confidence']
    }

    # Append to comparison log
    with open('format_selection_comparison.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    return ai_result  # Use AI result
```

### Phase 2: Gradual Rollout
1. Start with new books only
2. Monitor for issues
3. Expand to re-processing existing books
4. Full deployment

### Phase 3: Optimization
1. Fine-tune prompts based on results
2. Adjust confidence thresholds
3. Optimize for cost/performance

---

## Configuration

Add to `config/settings.yaml`:

```yaml
afa:
  selector:
    mode: "ai"  # "ai", "mathematical", or "hybrid"
    ai:
      provider: "openai"  # "openai", "anthropic", "local"
      model: "gpt-4"
      temperature: 0.7
      max_retries: 3
    fallback:
      enabled: true
      trigger_on_low_confidence: 0.5
    validation:
      require_evidence: true
      min_evidence_length: 20
    statistics:
      track_usage: true
      balance_threshold: 0.25  # Warn if any format >25%
```

---

## Monitoring & Logging

### Selection Audit Log
```python
def log_selection(book_id: str, result: dict):
    """Create audit trail for format selections"""

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'book_id': book_id,
        'format': result['selected_format'],
        'confidence': result['confidence'],
        'reasoning': result['primary_reasoning'],
        'evidence': result.get('evidence_from_findings', ''),
        'method': result['validation_status']
    }

    log_path = Path('logs/format_selections.jsonl')
    log_path.parent.mkdir(exist_ok=True)

    with open(log_path, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

### Performance Metrics
Track:
- Format distribution over time
- AI confidence levels
- Fallback frequency
- Processing time
- Cost (if using paid APIs)

---

## Testing

### Unit Tests
```python
def test_ai_selector():
    # Test with known problematic books
    test_books = [
        "0037_wuthering_heights",  # Should NOT be academic
        "0013_hobbit",  # Should be exploratory/narrative
    ]

    for book_id in test_books:
        result = select_format_with_ai(Path(f"books/{book_id}"))
        assert result['validation_status'] == 'valid'
        assert result['selected_format'] != 'academic_analysis'
```

### Integration Tests
1. Process batch of books
2. Verify format diversity improves
3. Check no hallucinations in evidence
4. Validate reasoning quality

---

## Rollback Plan

If issues arise:

1. **Immediate:** Switch `mode` to "mathematical" in config
2. **Investigation:** Review audit logs for problematic selections
3. **Fix:** Adjust prompts or validation rules
4. **Re-test:** Run parallel testing again
5. **Re-deploy:** When confidence restored

---

## Success Metrics

### Short-term (1 month)
- All 8 formats used at least once
- Academic_analysis drops below 25%
- No inappropriate genre-format matches

### Long-term (3 months)
- Format distribution within 10-20% range for each
- High confidence scores (>0.8 average)
- Positive user feedback on format variety

---

## Next Steps

1. [ ] Choose AI provider
2. [ ] Set up API credentials
3. [ ] Run parallel testing on 10 books
4. [ ] Review results with team
5. [ ] Deploy to production
6. [ ] Monitor for 2 weeks
7. [ ] Full rollout if successful

---

This integration maintains system stability while introducing intelligence and flexibility into format selection.