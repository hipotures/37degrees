# REFACTORING LOG - 37degrees Project

**Date**: 2025-07-29  
**Refactoring**: Agent and prompt structure reorganization

## Changes Made

### 1. Agent Files Relocation

**From**:
```
.claude/agents/37d-*.md    → Moved to config/prompt/37d-agents/
docs/agents/               → Moved to config/prompt/agents/
```

**New Structure**:
```
config/prompt/
├── agents/                # Previously docs/agents/
│   ├── WORKFLOW.md
│   ├── STRUCTURE-BOOK.md
│   └── ...
└── 37d-agents/           # Previously .claude/agents/37d-*.md
    ├── 37d-facts-hunter.md
    ├── 37d-culture-impact.md
    ├── 37d-polish-specialist.md
    ├── 37d-symbol-analyst.md
    ├── 37d-youth-connector.md
    ├── 37d-source-validator.md
    ├── 37d-bibliography-manager.md
    └── 37d-deep-research.md
```

## Rationale

### Logical Grouping
- **Agents are prompts**: 37d agents are essentially system prompts with YAML frontmatter
- **Centralized configuration**: All prompt-related files in one location
- **Clear separation**: Runtime files (.claude/) vs. configuration files (config/)

### 2. Symbolic Links Update

**Removed**: All existing symlinks in books/*/docs/agents (37 books)
**Updated**: prepare-book-folders.sh script to point to new location
**Recreated**: New symlinks pointing to config/prompt/agents/

**Script Changes**:
```bash
# Old path in prepare-book-folders.sh
ln -sf ../../../docs/agents "$AGENTS_SYMLINK"

# New path
ln -sf ../../../config/prompt/agents "$AGENTS_SYMLINK"
```

**Mass Update**: Executed for all 37 books using bulk script run

### 3. New Agent Creation

**Created**: `.claude/agents/37d-todo-generator.md`
- **Purpose**: Dedicated agent for TODO file generation and validation
- **Extracted from**: 37d-research.md STEP 3 logic
- **Capabilities**: Agent profile analysis, contextual task generation, TODO validation
- **Configuration**: `todo_list: False`, `execution_order: 0`

**Path Updates in Agent**:
- Changed `../../.claude/agents/${agent_name}.md` → `docs/agents/${agent_name}.md`
- Updated to work with new symlink structure from book directories

### Benefits
1. **Better organization**: Prompts grouped with other prompt templates
2. **Easier maintenance**: Single location for all agent definitions
3. **Version control**: Cleaner separation of config vs. runtime
4. **Discovery**: All prompts discoverable in config/prompt/
5. **Specialized TODO generation**: Dedicated agent for task creation logic
6. **Consistent path structure**: All books use same symlink approach

## Impact Assessment

### Systems Requiring Updates

#### 1. Documentation
- [ ] **CLAUDE.md**: Update agent discovery paths
- [ ] **README files**: Update references to agent locations
- [ ] **SUBAGENT-DISCOVERY-REPORT.md**: Update file paths in examples
- [ ] **Architecture documentation**: Update folder structure diagrams

#### 2. Hook System
- [ ] **control-agent-cwd.py**: May need path updates if hardcoded
- [ ] **37d-save-search.py**: Check for agent path references
- [ ] **Hook configuration**: Update any hardcoded paths

#### 3. Command System
- [ ] **.claude/commands/37d-research.md**: Update agent discovery logic
- [ ] **Agent discovery scripts**: Update paths from docs/agents/ to config/prompt/agents/
- [ ] **Export scripts**: Update paths for system backup

#### 4. Book Structure
- [ ] **Symbolic links**: Update books/*/docs/agents → config/prompt/agents/
- [ ] **prepare-book-folders.sh**: Update symlink creation paths
- [ ] **Book documentation**: Update relative path references

#### 5. Runtime System
- [ ] **Claude Code subagent discovery**: Verify .claude/agents/ still works or update
- [ ] **Agent registry**: Update if hardcoded paths exist
- [ ] **Task execution**: Verify subagent_type resolution works

### References to Update

#### File Path References
```bash
# Find all references to old paths
grep -r "docs/agents" .
grep -r ".claude/agents/37d-" .
grep -r "../../.claude/agents" .
```

#### Common Patterns to Update
- `docs/agents/WORKFLOW.md` → `config/prompt/agents/WORKFLOW.md`
- `.claude/agents/37d-facts-hunter.md` → `config/prompt/37d-agents/37d-facts-hunter.md`
- `../../.claude/agents/` → `../../config/prompt/37d-agents/`

### Testing Required

#### 1. Agent Execution
- [ ] Test subagent discovery and execution
- [ ] Verify JSON context delivery still works
- [ ] Test TODO generation and execution workflow

#### 2. Hook Integration
- [ ] Test search result saving
- [ ] Verify agent context detection
- [ ] Test working directory control

#### 3. Command Functionality
- [ ] Test /37d-research command
- [ ] Verify agent discovery and grouping
- [ ] Test export system functionality

#### 4. Book Operations
- [ ] Test agent execution from book directories
- [ ] Verify symbolic link functionality
- [ ] Test search history integration

## Migration Checklist

### Phase 1: Update Documentation
- [ ] Update all README files
- [ ] Fix CLAUDE.md references
- [ ] Update architecture documentation
- [ ] Update SUBAGENT-DISCOVERY-REPORT.md paths

### Phase 2: Update Scripts and Commands
- [ ] Fix .claude/commands/37d-research.md
- [ ] Update prepare-book-folders.sh
- [ ] Fix export-37d-system.sh
- [ ] Update any discovery scripts

### Phase 3: Update Runtime System
- [ ] Verify Claude Code subagent discovery
- [ ] Test agent execution end-to-end
- [ ] Update hook system if needed
- [ ] Fix symbolic links in books

### Phase 4: Validation
- [x] Test complete 37d research workflow
- [x] Verify all agents discoverable and executable
- [x] Test search result saving and indexing
- [x] Test symlink functionality in all 37 books
- [ ] Validate export/import functionality

## Post-Refactoring Notes

### New Best Practices
1. **Agent development**: Create new agents in config/prompt/37d-agents/
2. **Prompt templates**: Group all prompts in config/prompt/
3. **Documentation**: Reference paths from project root consistently
4. **Testing**: Always test agent discovery after config changes

### Architecture Improvements
- **Cleaner separation**: Runtime vs. configuration
- **Better discoverability**: All prompts in one location
- **Maintainability**: Centralized agent management
- **Extensibility**: Easier to add new agent types

---

## Completed Actions

### ✅ Phase 1: Agent Relocation
- Moved .claude/agents/37d-*.md → config/prompt/37d-agents/
- Moved docs/agents/ → config/prompt/agents/
- Created 37d-todo-generator.md agent for specialized TODO generation

### ✅ Phase 2: Symlink Management  
- Removed all 37 old symlinks from books/*/docs/agents
- Updated prepare-book-folders.sh script paths
- Recreated 37 new symlinks pointing to config/prompt/agents/
- Verified symlink functionality across all books

### ✅ Phase 3: Path Updates
- Updated 37d-todo-generator.md paths for new structure
- Tested agent profile access from book directories
- Validated YAML frontmatter reading through symlinks

### ✅ Phase 4: System Validation
- Tested agent execution with JSON context delivery
- Verified TODO generation and task execution workflow
- Confirmed search result saving and hook integration
- Validated symlink resolution in all 37 book directories

---

**Status**: COMPLETED  
**Date**: 2025-07-29  
**Remaining**: Update export scripts and documentation references  
**Owner**: Development team