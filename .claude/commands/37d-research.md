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
</prerequisites>

<workflow>

## STEP 1: Initialize Research Environment

<instructions>
1.1. PARSE book title from user input
1.2. FIND book folder matching the title in books/ directory
1.3. EXECUTE exactly this Bash command: ln -sf ../../../docs/agents books/${book_folder_path}/docs/agents
1.4. EXECUTE exactly this Bash command: cd ${book_folder_path}
1.5. EXECUTE exactly this Bash command: pwd (verify you are in book directory)
1.6. READ book.yaml to confirm book metadata
1.7. EXECUTE exactly this Bash command: mkdir -p docs/ docs/findings/ docs/todo/
</instructions>

<note>
IMPORTANT: After step 1.4, all subsequent file operations use paths RELATIVE to book directory.
Working directory is now: /path/to/37degrees/books/NNNN_book_name/

The symlink in step 1.3 creates link to documentation (docs/agents → ../../../docs/agents).
Agent profiles are accessed directly from ../../.claude/agents/ directory.
</note>

<error-handling>
IF book folder not found:
  REPORT: "ERROR: Book folder not found. Please create book entry first."
  EXIT workflow
</error-handling>

## STEP 2: Discover Available Agents

<instructions>
2.1. EXECUTE exactly this Bash command: ls ../../.claude/agents/37d-*.md
2.2. PARSE list to extract agent names (remove path and .md extension)
2.3. CREATE agent_list array with discovered agents in alphabetical order
2.4. SORT agents by execution_order field from agent profile headers
2.5. FOR EACH agent in agent_list:
     - EXECUTE exactly this Bash command: mkdir -p docs/${agent_name}
2.6. EXECUTE exactly this Bash command: find . -maxdepth 1 -name "*-37d-*.lock" -type f -delete
</instructions>

<agent-discovery>
The system will automatically discover all agents matching pattern: 37d-*.md
No hardcoded agent list is maintained - new agents are automatically included.
</agent-discovery>

## STEP 3: Generate TODO Files

<instructions>
3.1. FOR EACH discovered agent:
     a. READ agent profile from ../../.claude/agents/${agent_name}.md
     b. CHECK if agent has "todo_list: False" in YAML frontmatter
     c. IF todo_list is False:
        - SKIP TODO generation for this agent
        - AGENT will create tasks dynamically during execution
     d. IF todo_list is not False (default True):
        - EXTRACT key information:
          - Agent description and role
          - Tools available to agent
          - Task limits: min_tasks and max_tasks values
          - Specific instructions section
          - Output format requirements
          - Special focus areas
          - Any example tasks or priorities
        - GENERATE contextual TODO file based on:
          - Agent's expertise and role
          - Agent's task limits (min_tasks to max_tasks range)
          - Book metadata (title, author, year, genre)
          - Polish educational context
          - Youth engagement requirements (12-25 age group)
        - SAVE TODO to: docs/todo/TODO_${agent_name}.md

3.2. CREATE docs/todo/TODO_master.md listing all discovered agents as [ ] uncompleted
</instructions>

<todo-generation-rules>

### TODO File Structure
Each TODO file MUST follow this exact format:

```markdown
# TODO: [agent-name]
Book: [Book Title] ([Original Title if different])
Author: [Author Name]
Year: [Publication Year]
Location: books/[book_folder_name]/

## Primary Tasks
[Generate {min_tasks} to {max_tasks} tasks based on agent profile]
- [ ] [Task 1 - Core responsibility extracted from agent profile]
- [ ] [Task 2 - Specific to book context and genre]
- [ ] [Task 3 - Addressing Polish/youth angle]
- [ ] [Continue generating tasks up to agent's max_tasks limit]

## Search Focus Areas
[Generated based on agent's specific instructions and book context]
1. **[Category 1]**: [Specific aspects to investigate]
2. **[Category 2]**: [What to look for]
3. **[Category 3]**: [Polish/youth specific focus]

## Output Requirements
- Search results are automatically saved by 37d-save-search.py hook
- Generate comprehensive findings file: docs/findings/[agent-name]_findings.md
- Follow format specified in agent profile
- [Additional requirements from agent documentation]

## Notes
- Agent profile location: ../../.claude/agents/[agent-name].md (relative from book directory)
- The 37d-save-search.py hook will automatically save search results
- Check agent profile for specific workflow instructions
```

### Dynamic Task Generation Algorithm

1. **DEEPLY UNDERSTAND Agent Profile**:
   - READ entire agent profile comprehensively
   - EXTRACT agent's core mission and expertise from description
   - ANALYZE "SPECIFIC INSTRUCTIONS" section for research priorities
   - STUDY example tasks or search patterns provided
   - UNDERSTAND output format requirements and quality standards
   - IDENTIFY any specialized focus areas mentioned

2. **SYNTHESIZE with Book Context**:
   - COMBINE agent's expertise with book's specific characteristics
   - CONSIDER how agent's role applies to this particular work
   - ADAPT agent's capabilities to book's genre, era, and themes
   - INTEGRATE Polish educational context where relevant
   - ENSURE youth engagement angle (12-25) is addressed

3. **GENERATE Contextual Tasks**:
   - CREATE tasks that naturally emerge from agent profile + book combination
   - RESPECT agent's task limits: generate min_tasks to max_tasks tasks
   - USE language and priorities directly from agent's instructions
   - MIRROR the style and depth shown in agent's examples
   - ENSURE each task leverages agent's unique perspective
   - AVOID generic tasks - each must be specific to agent AND book

4. **Task Quantity and Scope**:
   - Minimum: Use agent's min_tasks field from YAML frontmatter
   - Maximum: Use agent's max_tasks field from YAML frontmatter  
   - Target: Aim for middle range between min and max for balanced coverage
   - BALANCE breadth of coverage with depth of investigation

5. **Task Quality Criteria**:
   - **Profile-Aligned**: Directly relates to agent's documented expertise
   - **Book-Specific**: References actual content, themes, or context
   - **Actionable**: Clear verb and measurable outcome
   - **Valuable**: Contributes to youth engagement goal
   - **Completable**: Achievable in a single research session

### Task Status Tracking
Tasks use this progression:
- `[ ]` - Not started
- `[x]` - Completed with results + timestamp
- `[0]` - Completed but no results found + timestamp

Example completion:
```
- [x] Research Polish translations and translators ✓ (2025-07-28 14:30)
- [0] Find unpublished dissertations (no results 2025-07-28 15:45)
```

</todo-generation-rules>

## STEP 4: Execute Agent Sequence

<agent-execution-pattern>
FOR EACH agent in discovered agent_list:

### Phase 1: Pre-execution Setup
<instructions>
1. UPDATE TODO_master.md to mark agent as running:
   - CHANGE: "- [ ] ${agent_name}"
   - TO: "- [R] ${agent_name} (started YYYY-MM-DD HH:MM)"
2. CREATE lock file: touch ${book_folder_name}-${agent_name}.lock
3. PREPARE agent context with book metadata and TODO location
</instructions>

### Phase 2: Agent Execution
<instructions>
1. CHECK if agent has todo_list: False in profile
2. IF agent has TODO file (todo_list is not False):
   EXECUTE agent using Task tool with prompt:
   "Use ${agent_name} to research '${book_title}' by ${author} (${year}) 
    YOUR TASKS ARE IN: docs/todo/TODO_${agent_name}.md
    Complete ALL tasks from this TODO file systematically.
    Mark each task as [x] with timestamp when done, [0] if no results found.
    After completing all tasks, generate comprehensive findings file."

3. IF agent has no TODO file (todo_list: False):
   EXECUTE agent using Task tool with prompt:
   "Use ${agent_name} to research '${book_title}' by ${author} (${year})
    Follow your agent profile instructions to complete your research.
    Generate comprehensive findings file when complete."
    
4. CAPTURE agent output for analysis
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

### Phase 4: TODO Verification Loop
<instructions>
1. IF agent has TODO file (todo_list is not False):
   a. READ docs/todo/TODO_${agent_name}.md
   b. COUNT tasks still marked as [ ]
   c. IF incomplete tasks remain:
      - RE-EXECUTE agent with reminder:
        "TODO incomplete - ${count} tasks remain. Complete all remaining [ ] tasks.
         Remember: [x] = completed with results, [0] = no results found.
         After all tasks done, generate comprehensive findings file."
      - RETURN to verification step

2. IF agent has no TODO file (todo_list: False):
   - SKIP TODO verification (agent manages own tasks)
   - VERIFY findings file was created
</instructions>

### Phase 5: Finalization
<instructions>
1. IF agent has TODO file: VERIFY all tasks marked [x] or [0]
2. IF agent has no TODO file: VERIFY findings file exists
3. UPDATE TODO_master.md:
   - CHANGE: "- [R] ${agent_name} (started YYYY-MM-DD HH:MM)"
   - TO: "- [x] ${agent_name} ✓ (completed YYYY-MM-DD HH:MM)"
4. REMOVE lock file: rm -f ${book_folder_name}-${agent_name}.lock
5. PROCEED to next agent
</instructions>
</agent-execution-pattern>

</workflow>

<context>

## Dynamic Agent System
- Agents are discovered at runtime from ../../.claude/agents/37d-*.md
- Agents are executed by execution_order field from agent profile headers (YAML frontmatter)
- Agent TODO generation controlled by todo_list field (default: True)
- Symlink created: books/NNNN/docs/agents → documentation only (not agent profiles)

## Lock File Management
Lock files prevent concurrent execution:
- Pattern: NNNN_book_name-37d-agent-name.lock
- Created before agent execution
- Removed after completion (success or failure)

## TODO Generation Intelligence
The system reads each agent's profile to understand:
- Core competencies and tools
- Expected output format
- Special focus areas
- Research priorities

This information drives dynamic TODO generation that matches:
- Agent capabilities with book requirements
- Polish context with youth engagement goals
- Academic rigor with accessibility needs

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
System: Created symlink docs/agents → ../../../docs/agents (documentation)
System: Found 8 agents in ../../.claude/agents/:
  - 37d-bibliography-manager
  - 37d-culture-impact
  - 37d-facts-hunter
  - 37d-myth-buster
  - 37d-polish-specialist
  - 37d-source-validator
  - 37d-symbol-analyst
  - 37d-youth-connector
System: Creating directories for all agents...
System: Generating TODO files for all agents...
```

## Example 2: Dynamic TODO Generation
```
System: Reading profile for 37d-facts-hunter...
System: Agent focuses on "fascinating facts" with WebSearch capability
System: Book: "1984" (dystopian, 1949, political themes)
System: Generating contextual tasks:
  - Research Orwell's experiences in Spanish Civil War
  - Find connections to Polish communist censorship
  - Investigate real surveillance tech inspired by the book
  [Generated 7 relevant tasks based on agent+book combination]
```

## Example 3: Flexible Execution
```
System: Executing newly added agent 37d-myth-buster...
System: No predefined template - reading agent profile...
System: Agent specializes in "debunking misconceptions"
System: Generated appropriate TODO based on capabilities
System: Agent completed successfully!
```

</examples>

<important-notes>

1. **Intelligent TODO**: Each TODO is generated based on agent profile + book context
2. **Profile-Driven**: All agent behavior derived from ../../.claude/agents/ profiles

</important-notes>