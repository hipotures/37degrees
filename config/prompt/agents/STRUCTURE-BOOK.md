# Book Folder Structure Guide

This document describes the folder structure that agents work within when researching a single book.

## Working Directory Context

**Agent Working Directory**: `books/NNNN_book_name/`

When an agent is executed, they are positioned in the specific book folder (e.g., `books/0004_brave_new_world/`). From this working directory, all paths are relative.

## Folder Structure

```
. (Current Working Directory - book folder)
├── book.yaml                   # Book metadata and slide configuration
├── book.db                     # Internal database (DO NOT MODIFY)
├── assets/                     # Generated images and media
├── audio/                      # Generated audio files
├── prompts/                    # Generated AI prompts
└── docs/                       # Research documentation (MAIN WORK AREA)
    ├── book-research-prompt.md           # Initial research prompt
    ├── agents/                           # Agent workflow documentation
    │   ├── WORKFLOW.md                   # Agent execution workflow
    │   └── research-report-prompt.md     # Research report template
    ├── findings/                         # AGENT OUTPUT FILES
    │   ├── 37d-facts-hunter_findings.md
    │   ├── 37d-symbol-analyst_findings.md
    │   ├── 37d-culture-impact_findings.md
    │   ├── 37d-polish-specialist_findings.md
    │   ├── 37d-youth-connector_findings.md
    │   ├── 37d-bibliography-manager_findings.md
    │   └── 37d-source-validator_findings.md
    ├── todo/                             # AGENT INPUT FILES
    │   ├── TODO_37d-facts-hunter.md
    │   ├── TODO_37d-symbol-analyst.md
    │   ├── TODO_37d-culture-impact.md
    │   ├── TODO_37d-polish-specialist.md
    │   ├── TODO_37d-youth-connector.md
    │   ├── TODO_37d-bibliography-manager.md
    │   ├── TODO_37d-source-validator.md
    │   └── TODO_master.md              # Supervisor tracking
├── search_history/                   # RAW SEARCH DATA (auto-saved)
│   ├── search_WebSearch_YYYYMMDD_HHMMSS_PID.json
│   ├── search_WebFetch_YYYYMMDD_HHMMSS_PID.json
│   └── searches_index.txt
```

## File Access Patterns

### Input Files (READ-ONLY for agents)
- `book.yaml` - Book metadata, title, author, year
- `docs/todo/TODO_37d-[agent-name].md` - Agent's task list

### Output Files (WRITE/APPEND by agents)  
- `docs/findings/37d-[agent-name]_findings.md` - Research results
- `docs/todo/TODO_37d-[agent-name].md` - Task status updates

### Auto-Generated Files (DO NOT TOUCH)
- `search_history/` - Raw search data saved by hooks
- `book.db` - Internal database

## Key Principles

### 1. Relative Paths Only
Agents work with relative paths from book directory:
- ✅ CORRECT: `docs/todo/TODO_37d-facts-hunter.md`
- ❌ WRONG: `books/0004_brave_new_world/docs/todo/TODO_37d-facts-hunter.md`

### 2. Limited Scope
Agents only know about:
- This specific book's folder
- Files within this book's directory tree
- NO knowledge of project-wide structure
- NO access to other books' folders

### 3. File Creation Rules
Agents may:
- READ any file in the book folder
- UPDATE existing TODO files
- WRITE/APPEND to their findings file
- EXTEND TODO lists (add tasks, never remove)

Agents must NOT:
- Create new books or folders outside docs/
- Modify book.yaml or configuration files
- Access files outside this book's directory
- Remove or delete any existing files

## Error Conditions

### Missing Critical Files
If these files don't exist, agent must EXIT immediately:
- `docs/todo/TODO_37d-[agent-name].md` - Cannot work without task list
- `book.yaml` - Cannot determine book metadata

### Corrupted or Empty Files
If critical files exist but are empty/corrupted:
- REPORT the specific issue
- DO NOT attempt to recreate
- EXIT with error message

## Integration Points

### Search Data Hook
The `37d-save-search.py` hook automatically saves search results to:
- `search_history/search_WebSearch_[timestamp]_[pid].json`
- `search_history/search_WebFetch_[timestamp]_[pid].json`
- `search_history/searches_index.txt`

Agents don't need to manage this data - focus on findings.

## Example Agent Perspective

From 37d-facts-hunter agent viewpoint in `books/0004_brave_new_world/`:

```bash
# Agent's current working directory
pwd
# Output: /path/to/37degrees/books/0004_brave_new_world

# Agent reads their task list
cat docs/todo/TODO_37d-facts-hunter.md

# Agent writes findings
echo "## New Finding" >> docs/findings/37d-facts-hunter_findings.md

# Agent updates task status
# (Uses Edit tool on docs/todo/TODO_37d-facts-hunter.md)
```

This structure keeps agents focused and isolated within their specific book's research context.