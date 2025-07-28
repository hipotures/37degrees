# TODO Master Workflow: Jane Eyre Research

**Book**: Jane Eyre by Charlotte Brontë (1847)  
**Location**: books/0014_jane_eyre/  
**Start**: 2025-07-28 10:48:50  

## Sequential Agent Execution Plan

### Phase 1: Core Research
- [ ] **37d-facts-hunter** - Historical facts and creation story
- [ ] **37d-symbol-analyst** - Literary symbolism and interpretations  
- [ ] **37d-culture-impact** - Cultural adaptations and modern relevance

### Phase 2: Polish Context (CRITICAL)
- [ ] **37d-polish-specialist** - Polish reception and educational focus

### Phase 3: Modern Connections
- [ ] **37d-youth-connector** - Gen Z culture bridge

### Phase 4: Validation
- [ ] **37d-bibliography-manager** - Master of citations and references
- [ ] **37d-source-validator** - Guardian of research integrity

## Lock Management
All agents use lock files in tmp/ directory:
- Format: `0014_jane_eyre-37d-[agent-name].lock`
- Created before agent execution
- Removed after completion (even on failure)

## Output Structure
- Findings: `docs/findings/37d-[agent]_findings.md`
- JSON data: `docs/37d-[agent]/` (auto-saved by hook)
- Search index: `docs/37d-[agent]/37d-[agent]_searches_index.txt`

---
*Generated: 2025-07-28 10:48:50*