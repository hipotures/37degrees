---
name: 37d-research
description: |
  Launches comprehensive book research using 37d agent system.
  Usage: /37d-research "Book Title"
  USES PARALLEL EXECUTION for faster research.
enabled: true
---

Execute comprehensive book research workflow for the specified book.

WORKFLOW:
1. Parse book title from input
2. Find matching folder in books/ directory (e.g., 0017_little_prince)
3. Read book.yaml to get full metadata
4. Generate TODO files for each agent in docs/ folder
5. Execute agents in PARALLEL GROUPS for efficiency
6. Monitor progress and compile final report

PARALLEL EXECUTION STRATEGY:

GROUP 1 - Data Gathering (all agents in parallel):
- 37d-facts-hunter - Fascinating facts and creation story
- 37d-symbol-analyst - Symbolism and meanings
- 37d-culture-impact - Cultural impact and adaptations
- 37d-polish-specialist - Polish perspective (CRITICAL)
- 37d-youth-connector - Youth perspectives
- 37d-bibliography-manager - Citation management

GROUP 2 - Validation (Sequential - waits for Group 1):
- 37d-source-validator - Verifies all facts from Group 1


PROVIDING CONTEXT TO EACH AGENT:
When invoking agents, ALWAYS include:
- Full book title and author
- Year of publication
- Book folder path

Example for each agent:
"Task 1: Use 37d-facts-hunter to research 'Don Quixote' by Cervantes (1605) 
located in books/0006_don_quixote/. Focus on fascinating facts and creation story."

FINDING THE BOOK FOLDER:
- User provides: "Mały Książę" or "Little Prince" or "The Little Prince"
- Search books/ for matching folder names
- Use fuzzy matching if exact match not found
- Read book.yaml for confirmation

EXISTING STRUCTURE:
```
books/
├── 0001_alice_in_wonderland/
├── 0002_animal_farm/
├── 0017_little_prince/
│   ├── assets/
│   ├── audio/
│   ├── book.yaml      # Contains title, author, metadata
│   └── docs/          # Where agent files will go
└── ...
```

TODO GENERATION:
For each agent, create in docs/:
- TODO_37d-facts-hunter.md
- TODO_37d-symbol-analyst.md
- TODO_37d-culture-impact.md
- TODO_37d-polish-specialist.md
- TODO_37d-source-validator.md
- TODO_37d-youth-connector.md
- TODO_37d-bibliography-manager.md

Also create TODO_master.md in the book folder root.

Each agent will:
- Read their TODO from docs/TODO_37d-[agent].md
- Perform research
- Save findings to docs/37d-[agent]_findings.md
- Mark tasks complete
