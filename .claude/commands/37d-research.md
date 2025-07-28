---
name: 37d-research
description: |
  Launches comprehensive book research using 37d agent system.
  Usage: /37d-research "Book Title"
  USES SEQUENTIAL EXECUTION for reliable research.
enabled: true
---

Execute comprehensive book research workflow for the specified book.

WORKFLOW:
1. Parse book title from input
2. Find matching folder in books/ directory
3. Read book.yaml to get full metadata
4. Create tmp/ directory and clean old lock files
5. Generate TODO files for each agent in book docs/todo/ folder
6. Execute agents SEQUENTIALLY for reliable results

IMPORTANT: All agents should refer to docs/agents/WORKFLOW.md for standard workflow steps.

LOCK FILE MANAGEMENT:
- CRITICAL: Only create/remove locks when in project root directory
- First verify we're in correct location: [[ -d "books" ]] || exit 1
- Verify tmp directory exists: [[ -d "tmp" ]] || { echo "ERROR: tmp/ directory must exist"; exit 1; }
- Clean ALL 37d locks: find tmp -maxdepth 1 -name "*-37d-*.lock" -type f -delete
- Before each agent: touch tmp/NNNN_book_name-37d-agent-name.lock
- After each agent: rm -f tmp/NNNN_book_name-37d-agent-name.lock
- Lock format example: tmp/0001_alice_in_wonderland-37d-facts-hunter.lock

SEQUENTIAL EXECUTION ORDER:

1. 37d-facts-hunter - Historical facts and context expert
2. 37d-symbol-analyst - Literary symbolism and cross-cultural interpretations
3. 37d-culture-impact - Cultural adaptations from films to TikTok
4. 37d-polish-specialist - Polish reception and education focus (CRITICAL)
5. 37d-youth-connector - Gen Z culture bridge
6. 37d-bibliography-manager - Master of citations and references
7. 37d-source-validator - Guardian of research integrity

EXECUTION PATTERN FOR EACH AGENT:
```bash
# Create lock file
touch tmp/${book_folder_name}-${agent_name}.lock

# Execute agent
Task "Use ${agent_name} to research..."

# Remove lock file (ALWAYS, even if agent fails)
rm -f tmp/${book_folder_name}-${agent_name}.lock
```


PROVIDING CONTEXT TO EACH AGENT:
When invoking agents, ALWAYS include:
- Full book title and author
- Year of publication
- Book folder path

Example for each agent:
"Task 1: Use 37d-facts-hunter to research 'Don Quixote' by Cervantes (1605) 
located in books/0006_don_quixote/. Focus on fascinating facts and creation story."

FINDING THE BOOK FOLDER:
See docs/STRUCTURE.md for detailed project structure and folder organization.

BOOK FOLDER MATCHING:
- User provides: "Mały Książę" or "Little Prince" or "The Little Prince"
- Search books/ for matching folder names
- Use fuzzy matching if exact match not found
- Read book.yaml for confirmation

DIRECTORY CREATION:
If book folder exists, may create missing subfolders safely (mkdir -p):
- tmp/ (project root level for lock files)
- books/NNNN_book_name/docs/ (if missing)
- books/NNNN_book_name/docs/findings/ (if missing) - shared folder for all agent findings
- books/NNNN_book_name/docs/todo/ (if missing) - centralized TODO files
- books/NNNN_book_name/docs/37d-[agent]/ (agent-specific subfolders for JSON search data and indexes)
- NEVER delete or overwrite existing files/folders
- NEVER create new book folders

Note: The 37d-save-search.py hook uses lock files to determine where to save JSON search data.

ERROR HANDLING:
If book folder doesn't exist (books/NNNN_book_name/), STOP workflow with error:
- Inform user that book needs to be created first

TODO GENERATION:
For each agent, create in docs/todo/:
- TODO_37d-facts-hunter.md
- TODO_37d-symbol-analyst.md
- TODO_37d-culture-impact.md
- TODO_37d-polish-specialist.md
- TODO_37d-source-validator.md
- TODO_37d-youth-connector.md
- TODO_37d-bibliography-manager.md

Also create docs/todo/TODO_master.md for overall workflow tracking.

Each agent will:
- Read their TODO from docs/todo/TODO_37d-[agent].md
- Follow common workflow from docs/agents/WORKFLOW.md
- Perform research using imperative commands from their agent file
- Save findings to docs/findings/37d-[agent]_findings.md
- JSON search results are auto-saved by hook to docs/37d-[agent]/ folder
- Search index is auto-maintained in docs/37d-[agent]/37d-[agent]_searches_index.txt
- Mark tasks complete with timestamp
