---
name: 37d-research
description: |
   This is agent workflow for individual 37d research.
---


<objective>
Execute ALL research tasks marked [ ] from FILE TODO
</objective>

<prerequisites>
VERIFY these conditions before starting:
1. EXECUTE Bash command: pwd (verify you are in books/NNNN_book_name directory)
2. VERIFY FILE TODO exists at docs/todo/TODO_37d-[agent-name].md
VARIABLES received via JSON in User message:
- ${agent_name} = target agent name (e.g., 37d-facts-hunter, 37d-symbol-analyst)
- ${book_title} = book title
- ${author} = author name
- ${year} = publication year
- ${todo_file} = path to TODO file (e.g., docs/todo/TODO_37d-facts-hunter.md)

</prerequisites>
<workflow>

## STEP 1: Initialize Agent Session

<instructions>
1.0. PARSE Agent context JSON from User message:
     - EXTRACT JSON block marked as "Agent context:" from the User message
     - PARSE JSON to get: agent_name, book_title, author, year, todo_file
     - SAVE complete Agent context JSON to /tmp/agent-context-[timestamp]-[pid].txt for debugging
     - USE parsed values for subsequent workflow steps

1.1. DETERMINE agent name from parsed agent_name field
1.2. READ book.yaml to extract book metadata (verify against parsed context):
     - title (should match book_title from context)
     - author (should match author from context) 
     - year (should match year from context)
1.3. VERIFY search_history/ directory exists
</instructions>

<error-handling>
IF FILE TODO missing:
  REPORT: "ERROR: FILE TODO missing at docs/todo/TODO_37d-[agent-name].md"
  EXIT workflow

IF book.yaml missing:
  REPORT: "ERROR: book.yaml missing - cannot determine book metadata"
  EXIT workflow

IF docs/agents/ not accessible:
  REPORT: "ERROR: Cannot access agent documentation at docs/agents/ - verify symbolic link exists"
  EXIT workflow
</error-handling>

## STEP 2: Task Execution

<instructions>
IF FILE TODO contains tasks marked [ ]:

2.1. READ FILE TODO and FIND first task marked [ ]
     
2.2. CONSTRUCT search query based on:
     - Task description
     - Book title and author
     - Specific aspect mentioned in task
     
2.3. EXECUTE WebSearch with constructed query
     Example: "Brave New World" Huxley 1932 "Polish translation" history

2.4. EVALUATE search results:
     IF results insufficient or too general:
       REFINE query with more specific terms
       EXECUTE additional WebSearch
       
2.5. UPDATE task status in FILE TODO:
     IF valuable results found:
       CHANGE: "- [ ] Task description"
       TO: "- [x] Task description (completed YYYY-MM-DD HH:MM)"
       
     IF no results after multiple attempts:
       CHANGE: "- [ ] Task description"  
       TO: "- [0] Task description (no results YYYY-MM-DD HH:MM)"

2.6. CHECK for more tasks:
     IF more tasks marked [ ] in FILE TODO:
       CONTINUE with next [ ] task (return to step 2.1)
     ELSE:
       END session - all tasks completed
</instructions>

<search-strategy>
SINGLE SEARCH APPROACH:
- Craft ONE well-constructed query per task
- Include: book title + author + specific aspect from task
- Use quotes for exact phrases
- Add year if historically relevant

WHEN TO DO SECOND SEARCH (exceptional cases):
Do second search ONLY when:
1. First search returned ≤2 sources total
   OR
2. Search results contain only generic/Wikipedia pages with no specific information

IF doing second search:
- Completely rephrase the query
- Try different keywords or approach
- Maximum 2 searches total per task

DEFAULT BEHAVIOR:
- If search returns 3+ relevant sources → mark [x] and move on
- If no useful results after max 2 attempts → mark [0]
</search-strategy>

NOTE: The 37d-save-search.py hook automatically saves all WebSearch/WebFetch 
results to search_history/ as timestamped JSON files.

</workflow>

<context>

## Task Status Progression
```
- [ ] Task description                    # Not started
- [x] Task description (completed DATE)   # Completed with results
- [0] Task description (no results DATE)  # Completed without results
```

Note: No [R] running status - tasks go directly from [ ] to [x] or [0]

## File Locations
- Input: docs/todo/TODO_37d-[agent-name].md

</context>

<examples>

## Example 1: Multiple Task Execution
```
Agent: Reading FILE TODO...
Agent: Found task "Research Polish translations and translators"
Agent: Searching: "Brave New World" "Nowy wspaniały świat" Polish translation history
Agent: Found relevant results about Huxley translations
Agent: Task marked [x] with timestamp
Agent: Checking for more [ ] tasks...
Agent: Found next task "Analyze translation challenges"
Agent: Continuing with next task...
```

## Example 2: Multiple Search Attempts
```
Agent: Found task "Analyze key concepts translation to Polish"
Agent: Searching: "Brave New World" Polish translation "soma" "feelies" terminology
Agent: Limited results, refining search...
Agent: Searching: "Nowy wspaniały świat" Huxley Polish "soma" translation choices
Agent: Found detailed analysis of translation decisions
Agent: Task marked [x] with timestamp
```

## Example 3: No Results
```
Agent: Found task "Find unpublished Polish dissertations"
Agent: Searching: "Brave New World" Polish unpublished dissertation manuscript
Agent: No results found, trying broader search...
Agent: Searching: Huxley Polish academic thesis unpublished  
Agent: Still no relevant results after 3 attempts
Agent: Task marked [0] with timestamp
```

</examples>

<important-notes>

1. **Simple Status**: Only [ ] → [x] or [ ] → [0], no intermediate states
2. **Multiple Searches**: Can search multiple times per task for better results

</important-notes>
