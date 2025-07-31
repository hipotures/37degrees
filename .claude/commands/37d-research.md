---
name: 37d-research
description: |
  Launches comprehensive book research using 37d agent system.
  Usage: /37d-research "Book Title"
  USES SEQUENTIAL EXECUTION for reliable research.
  Dynamically discovers and executes all 37d agents.
enabled: true
---

<objective>
Execute comprehensive book research workflow using all available 37d agents in sequential order.
Generate complete research documentation for the specified book.
</objective>

<prerequisites>
VARIABLES used in this workflow:
- ${book_folder_path} = books/NNNN_book_name (e.g., books/0004_brave_new_world)
- ${book_folder_name} = NNNN_book_name (e.g., 0004_brave_new_world)  
- ${agent_name} = 37d-agent-type (e.g., 37d-facts-hunter, 37d-symbol-analyst)
- ${book_title} = extracted from book.yaml
- ${author} = extracted from book.yaml
- ${year} = extracted from book.yaml

JSON_PROMPT:
{
  "agent_name": "${agent_name}",
  "book_title": "${book_title}", 
  "author": "${author}",
  "year": "${year}",
  "todo_file": "docs/todo/TODO_${agent_name}.md",
  "project_root": "$CLAUDE_PROJECT_DIR",
  "book_folder_path": "$CLAUDE_PROJECT_DIR/${book_folder_path}"
}
</prerequisites>

<workflow>

## STEP 1: Discover Available Agents

<instructions>
1.1. EXECUTE exactly this Bash command: python scripts/list-agents.yaml.py
</instructions>

<agent-discovery>
The system will automatically discover all agents and params agents
Script outputs YAML with agents, agent_list, grouped_agents structures ready to use.
Groups execute sequentially by execution_order value in ascending order - any numeric values sorted ascending, agents within each group execute in parallel.
</agent-discovery>

## STEP 2: Initialize Research Environment

<instructions>
2.1. PARSE book title from user input and MAP VARIABLES:
     - Extract book title from input
     - FIND matching book folder in books/ directory  
     - SET ${book_folder_path} = books/NNNN_book_name
     - SET ${book_folder_name} = NNNN_book_name
2.2. EXECUTE exactly this Bash command: cd ${book_folder_path}
2.3. EXECUTE exactly this Bash command: pwd && tree -d
2.4. EXECUTE exactly this Bash command: cat book.yaml
2.5. SET remaining VARIABLES from book.yaml output:
     - SET ${book_title} = from book.yaml
     - SET ${author} = from book.yaml  
     - SET ${year} = from book.yaml

IMPORTANT: After step 2.2, DO NOT change working directory. All subsequent operations must remain in ${book_folder_path}.
</instructions>

<note>
IMPORTANT: After step 2.2, all subsequent file operations use paths RELATIVE to book directory.
Working directory is now: /path/to/37degrees/books/NNNN_book_name/
</note>

<error-handling>
IF book folder not found:
  REPORT: "ERROR: Book folder not found. Please create book entry first."
  EXIT workflow
</error-handling>

## STEP 4: Execute Agent Sequence

<agent-execution-pattern>
FOR EACH execution_order_group in grouped_agents:

### Phase 1: Pre-execution Setup
<instructions>
FOR EACH agent in current execution_order_group:
1. UPDATE TODO_master.md to mark agent as running:
   - CHANGE: "- [ ] ${agent_name}"
   - TO: "- [R] ${agent_name} (started YYYY-MM-DD HH:MM)"
2. USE AGENT JSON CONTEXT from prerequisites
   - For agents with todo_list: False, set "todo_file": null in JSON
</instructions>

### Phase 2: Agent Execution (Parallel)
<instructions>
IF execution_order_group has single agent:
   1. PREPARE Task call with JSON_PROMPT as prompt from prerequisites
   2. EXECUTE single Task call

IF execution_order_group has multiple agents:
   Execute ALL agents in group PARALLEL using multiple Task calls in single response:
   
   FOR EACH agent in current execution_order_group:
   1. PREPARE Task call with JSON_PROMPTas prompt from prerequisites

   EXECUTE all prepared Task calls simultaneously in single response
   CAPTURE all agent outputs for analysis
</instructions>

### Phase 3: Error Detection and Recovery
<error-handling>
IF agent output contains "ERROR: FILE TODO missing":
  1. REGENERATE TODO file for that agent
  2. RE-EXECUTE agent with same prompt
  
IF agent output contains other errors:
  1. LOG error message
  2. ATTEMPT recovery based on error type
  3. RE-EXECUTE if recovery successful
  4. SKIP agent if unrecoverable (mark in master TODO)
</error-handling>

### Phase 4: Finalization
<instructions>
FOR EACH agent in current execution_order_group:
1. UPDATE TODO_master.md:
   - CHANGE: "- [R] ${agent_name} (started YYYY-MM-DD HH:MM)"
   - TO: "- [x] ${agent_name} ✓ (completed YYYY-MM-DD HH:MM)"

PROCEED to next execution_order_group
</instructions>
</agent-execution-pattern>

</workflow>

<context>

## Dynamic Agent System
- Agents are discovered at runtime from config/prompt/37d-agents/37d-*.md
- Agents are grouped by execution_order field, then executed in parallel within groups
- Groups are processed sequentially in execution_order ascending order
- Agent TODO generation controlled by todo_list field (default: True)


## Agent TODO Control
Agents can control TODO generation via YAML frontmatter:
- `todo_list: True` (default): Generate book-specific TODO file
- `todo_list: False`: Agent creates tasks dynamically, no predefined TODO

Agents with todo_list: False typically:
- Analyze outputs from other agents (source-validator, bibliography-manager)
- Perform gap analysis and deep research (37d-deep-research)
- Have workflows independent of specific book content

</context>

<examples>

## Example 1: Agent Discovery
```
System: Discovering available agents...
System: Created symlink docs/agents → ../../../config/prompt/agents (documentation)
System: Found 8 agents in config/prompt/37d-agents/:
  - 37d-bibliography-manager
  - 37d-culture-impact
  - 37d-facts-hunter
  - 37d-myth-buster
  - 37d-polish-specialist
  ...
System: Creating directories for all agents...
System: Generating TODO files for all agents...
```

## Example 2: Dynamic TODO Generation
```
System: Executing 37d-todo-generator for 37d-facts-hunter...
System: Reading agent profile from config/prompt/37d-agents/37d-facts-hunter.md
System: Reading book context from docs/review.md
System: Agent focuses on "fascinating facts" with WebSearch capability
System: Book: "1984" (dystopian, 1949, political themes)
System: Generated 12 contextual tasks for facts-hunter:
  - Research Orwell's experiences in Spanish Civil War
  - Find connections to Polish communist censorship
  - Investigate real surveillance tech inspired by the book
  [Saved to docs/todo/TODO_37d-facts-hunter.md]
```

## Example 3: Agent Execution
```
System: Executing agent 37d-facts-hunter with generated TODO...
System: Agent working on 12 tasks from docs/todo/TODO_37d-facts-hunter.md
System: Searching for Orwell's Spanish Civil War experiences... ✓
System: Finding Polish censorship connections... ✓
System: Generated comprehensive findings file: docs/findings/37d-facts-hunter_findings.md
System: Agent completed successfully!
```

</examples>