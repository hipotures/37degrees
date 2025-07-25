---
name: 37d-research
description: |
  Launches comprehensive book research using 37d agent system.
  Usage: /37d-research "Book Title" by Author Name
enabled: true
---

Execute comprehensive book research workflow for the specified book.

WORKFLOW:
1. Parse book title and author from input
2. Identify or create book folder structure
3. Create master TODO list for all 37d agents
4. Delegate research tasks to specialized agents
5. Monitor progress and compile results

BOOK FOLDER STRUCTURE:
books/
└── XXXX_book_name_slug/
    ├── docs/
    │   ├── 37d-facts-hunter_findings.md
    │   ├── 37d-symbol-analyst_findings.md
    │   ├── 37d-culture-impact_findings.md
    │   ├── 37d-polish-specialist_findings.md
    │   ├── 37d-source-validator_findings.md
    │   ├── 37d-youth-connector_findings.md
    │   └── 37d-bibliography_compiled.md
    ├── TODO_master.md
    └── FINAL_REPORT.md

PROCESS:
1. Generate book ID (e.g., 0017_little_prince)
2. Create folder structure if not exists
3. Generate TODO_master.md with tasks for each agent
4. Invoke each 37d agent with their specific tasks
5. Each agent works independently and saves to their file
6. Compile final report from all findings
