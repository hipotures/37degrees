---
name: 37d-research
description: |
  Launches comprehensive book research using 37d agent system.
  Usage: /37d-research "Book Title"
  USES SEQUENTIAL EXECUTION for reliable research.
enabled: true
---

<objective>
Execute comprehensive book research workflow using 7 specialized AI agents in sequential order.
Generate complete research documentation for the specified book.
</objective>

<prerequisites>
VERIFY these conditions before starting:
1. Working directory contains "books" folder
2. Directory "tmp" exists for lock files  
3. Book folder exists in books/NNNN_book_name format
4. User has permission to create/modify files
</prerequisites>

<workflow>

## STEP 1: Initialize Research Environment

<instructions>
1.1. PARSE book title from user input
1.2. SEARCH books/ directory for matching folder (use fuzzy matching if needed)
1.3. READ book.yaml to confirm book metadata
1.4. CREATE missing directories if needed:
     - books/NNNN_book_name/docs/
     - books/NNNN_book_name/docs/findings/
     - books/NNNN_book_name/docs/todo/
     - books/NNNN_book_name/docs/37d-[agent]/ (for each agent)
</instructions>

<error-handling>
IF book folder not found:
  REPORT: "ERROR: Book folder not found. Please create book entry first."
  EXIT workflow
</error-handling>

## STEP 2: Prepare Lock File System

<instructions>
2.1. VERIFY current directory: [[ -d "books" ]] || exit 1
2.2. VERIFY tmp directory exists: [[ -d "tmp" ]] || exit 1  
2.3. CLEAN all existing 37d lock files: find tmp -maxdepth 1 -name "*-37d-*.lock" -type f -delete
</instructions>

## STEP 3: Generate TODO Files

<instructions>
3.1. CHECK if TODO files already exist in docs/todo/
3.2. CREATE missing TODO files for each agent:
     - TODO_37d-facts-hunter.md
     - TODO_37d-symbol-analyst.md
     - TODO_37d-culture-impact.md
     - TODO_37d-polish-specialist.md
     - TODO_37d-youth-connector.md
     - TODO_37d-bibliography-manager.md
     - TODO_37d-source-validator.md
3.3. CREATE TODO_master.md with all agents listed as [ ] uncompleted
</instructions>

## STEP 4: Execute Agent Sequence

<agent-sequence>
1. 37d-facts-hunter - Historical facts and context expert
2. 37d-symbol-analyst - Literary symbolism and cross-cultural interpretations
3. 37d-culture-impact - Cultural adaptations from films to TikTok
4. 37d-polish-specialist - Polish reception and education focus (CRITICAL)
5. 37d-youth-connector - Gen Z culture bridge  
6. 37d-bibliography-manager - Master of citations and references
7. 37d-source-validator - Guardian of research integrity
</agent-sequence>

<agent-execution-pattern>
FOR EACH agent in sequence:

### Phase 1: Pre-execution Setup
<instructions>
1. EXECUTE Bash command: cd ${book_folder_path}
2. EXECUTE Bash command: pwd (verify you are in book directory)
3. UPDATE TODO_master.md to mark agent as running:
   - CHANGE: "- [ ] ${agent_name} - Description"
   - TO: "- [R] ${agent_name} - Description (started YYYY-MM-DD HH:MM)"
4. CREATE lock file: touch ../../tmp/${book_folder_name}-${agent_name}.lock
5. PREPARE agent context with:
   - Book title and author
   - Year of publication  
   - Book folder path: books/NNNN_book_name/
</instructions>

### Phase 2: Agent Execution
<instructions>
1. EXECUTE agent using Task tool with prompt:
   "Use ${agent_name} to research '${book_title}' by ${author} (${year}) 
    located in ${book_folder_path}.
    YOUR TASKS ARE IN: docs/todo/TODO_${agent_name}.md
    ONLY complete tasks from this FILE TODO. Do NOT create new tasks."
    
2. CAPTURE agent output for analysis
</instructions>

### Phase 3: Error Detection and Recovery
<error-handling>
IF agent output starts with "ERROR: FILE TODO missing":
  1. CREATE missing TODO file for that agent
  2. RE-EXECUTE agent with same prompt
  3. CONTINUE to verification

IF agent output starts with any other "ERROR:":
  1. LOG error message
  2. ATTEMPT recovery based on error type
  3. RE-EXECUTE agent if recovery successful
</error-handling>

### Phase 4: TODO Verification Loop
<instructions>
1. READ books/${book_folder_name}/docs/todo/TODO_${agent_name}.md
2. COUNT tasks marked as [ ] (incomplete) or [R] (running)
3. IF incomplete or running tasks found:
   - RE-EXECUTE agent with message:
     "FILE TODO incomplete - verify all completed tasks are marked [x] or [0] with timestamps.
      Tasks marked [ ] or [R] need to be completed. Use [R] when starting, [x] when done with results, [0] when done with no results."
   - RETURN to step 1 (maximum 3 attempts)
</instructions>

### Phase 5: Finalization
<instructions>
1. UPDATE TODO_master.md ONLY after TODO verification passes:
   - CHANGE: "- [R] ${agent_name} - Description (started YYYY-MM-DD HH:MM)"
   - TO: "- [x] ${agent_name} - Description ✓ (YYYY-MM-DD HH:MM)"
2. REMOVE lock file: rm -f ../../tmp/${book_folder_name}-${agent_name}.lock
3. PROCEED to next agent
</instructions>
</agent-execution-pattern>

</workflow>

<context>

## Lock File Format
Lock files follow pattern: tmp/NNNN_book_name-37d-agent-name.lock
Example: tmp/0001_alice_in_wonderland-37d-facts-hunter.lock

## Directory Structure
See docs/STRUCTURE.md for complete project directory structure and agent-specific folders.

## Agent Dependencies
Each agent builds upon previous agents' work:
- facts-hunter: Establishes historical foundation
- symbol-analyst: Analyzes literary elements
- culture-impact: Documents cultural influence
- polish-specialist: Localizes for Polish context
- youth-connector: Bridges to Gen Z audience
- bibliography-manager: Compiles all sources
- source-validator: Verifies research integrity

## Hook Integration
The 37d-save-search.py hook automatically:
- Detects active lock files
- Saves WebSearch/WebFetch results to appropriate agent folder
- Maintains search index for each agent

</context>

<examples>

## Example 1: Successful Execution
```
User: /37d-research "Mały Książę"
System: Found book folder: books/0017_little_prince/
System: Creating lock file for 37d-facts-hunter...
System: Executing agent...
System: Verifying TODO completion...
System: TODO verified, updating master...
[Process continues for all 7 agents]
System: Research workflow completed successfully!
```

## Example 2: TODO Verification Loop
```
System: Executing 37d-bibliography-manager...
Agent: [completes work but forgets to update TODO]
System: TODO incomplete - 7 tasks still marked [ ]
System: Re-executing agent with reminder...
Agent: [updates TODO properly]
System: TODO verified, proceeding...
```

## Example 3: Error Recovery
```
System: Executing 37d-symbol-analyst...
Agent: ERROR: FILE TODO missing at books/0017_little_prince/docs/todo/TODO_37d-symbol-analyst.md
System: Creating missing TODO file...
System: Re-executing agent...
Agent: [proceeds normally with TODO available]
```

</examples>

<important-notes>

1. **Sequential Execution**: Agents MUST run in order - each depends on previous agents' findings
2. **TODO Compliance**: NO agent is marked complete until their FILE TODO is fully updated  
3. **Lock File Discipline**: ALWAYS remove lock files, even on errors
4. **Error Recovery**: Attempt automatic recovery before failing
5. **User Visibility**: User sees final summary only - no intermediate error messages

</important-notes>