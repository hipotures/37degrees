# 37degrees Agent Workflow

This document defines the imperative workflow for individual 37d research agents working on book research tasks.

<objective>
Execute research tasks from assigned TODO file systematically.
Generate comprehensive findings with proper citations and task tracking.
</objective>

<prerequisites>
VERIFY these conditions before starting:
1. Agent CWD is in book folder (books/NNNN_book_name/)
2. FILE TODO exists at docs/todo/TODO_37d-[agent-name].md
3. Agent has read access to book.yaml
</prerequisites>

<workflow>

## STEP 1: Initialize Agent Session

<instructions>
1.1. READ docs/agents/STRUCTURE-BOOK.md to understand folder structure
1.2. PARSE agent identity from execution context (37d-facts-hunter, 37d-symbol-analyst, etc.)
1.3. READ book.yaml to extract:
     - Book title
     - Author name
     - Publication year
1.4. CONFIRM FILE TODO exists at docs/todo/TODO_37d-[agent-name].md
</instructions>

<error-handling>
IF FILE TODO missing:
  REPORT: "ERROR: FILE TODO missing at docs/todo/TODO_37d-[agent-name].md - cannot proceed without task list"
  EXIT workflow

IF book.yaml missing:
  REPORT: "ERROR: book.yaml missing - cannot determine book metadata" 
  EXIT workflow
</error-handling>

## STEP 2: Assess Current State

<instructions>
2.1. READ FILE TODO at docs/todo/TODO_37d-[agent-name].md
2.2. COUNT tasks by status:
     - [ ] = Not started
     - [R] = Running (in progress)  
     - [x] = Completed with results
     - [0] = Completed with no results
2.3. CHECK if findings file exists at docs/findings/37d-[agent-name]_findings.md
2.4. DETERMINE work mode based on assessment
</instructions>

## STEP 3: Execute Tasks Systematically

<instructions>
FOR EACH task marked [ ] or [R] in FILE TODO:

3.1. MARK task as running:
     CHANGE: "- [ ] Task description"
     TO: "- [R] Task description (started YYYY-MM-DD HH:MM)"

3.2. EXECUTE research specific to task:
     - USE WebSearch for online research
     - USE WebFetch for specific page analysis  
     - GATHER information relevant to task objective
     - REPEAT searches if initial results insufficient

3.3. DOCUMENT findings:
     - APPEND results to docs/findings/37d-[agent-name]_findings.md
     - INCLUDE proper citations for all sources
     - MAINTAIN consistent formatting
     - USE quality rating scale (⭐⭐⭐⭐⭐ to ⭐)

3.4. UPDATE task completion:
     IF results found:
       CHANGE: "- [R] Task description (started YYYY-MM-DD HH:MM)"
       TO: "- [x] Task description ✓ (YYYY-MM-DD HH:MM)"
     
     IF no results found:
       CHANGE: "- [R] Task description (started YYYY-MM-DD HH:MM)"  
       TO: "- [0] Task description ✓ (YYYY-MM-DD HH:MM)"

3.5. CONTINUE to next uncompleted task
</instructions>

<task-execution-guidelines>
RESEARCH APPROACH:
- START with specific queries including book title + author
- BROADEN search terms if no results found
- EXECUTE multiple searches per task if needed
- CROSS-REFERENCE information from multiple sources
- PRIORITIZE academic and primary sources

SEARCH QUERY EXAMPLES:
- ✅ GOOD: "Don Quixote" Cervantes 1605 first edition publication
- ✅ GOOD: Aldous Huxley "Brave New World" 1932 historical context
- ❌ BAD: don quixote facts
- ❌ BAD: brave new world information

CITATION REQUIREMENTS:
- Books: Author Last, First. *Title*. Publisher, Year.
- Articles: Author. "Title." *Journal*, Year.
- Websites: "Page Title." *Site Name*. URL. Accessed: DD Month YYYY.
- ALL major claims must have citations
</task-execution-guidelines>

## STEP 4: Final Verification

<instructions>
4.1. READ FILE TODO to verify completion status
4.2. COUNT remaining [ ] or [R] tasks
4.3. IF incomplete tasks remain:
     CONTINUE to STEP 3 for remaining tasks
4.4. IF all tasks completed ([x] or [0]):
     PROCEED to completion
4.5. VERIFY findings file completeness:
     - Each [x] task has corresponding findings section
     - Each [0] task may have empty section with explanation
     - All findings include proper citations
     - Quality ratings assigned to sources
</instructions>

## STEP 5: Complete Session

<instructions>
5.1. CONFIRM FILE TODO shows all tasks as [x] or [0] with timestamps  
5.2. VERIFY findings file exists and contains research results
5.3. REPORT completion status:
     "Research completed successfully. All FILE TODO tasks marked complete."
5.4. SUMMARIZE key findings discovered during research
</instructions>

</workflow>

<context>

## Agent Types and Specializations

**37d-facts-hunter**: Historical facts, publication context, author background
**37d-symbol-analyst**: Literary symbols, cultural interpretations, cross-cultural analysis  
**37d-culture-impact**: Adaptations, modern influence, cultural presence
**37d-polish-specialist**: Polish translations, education system, local reception
**37d-youth-connector**: Gen Z connections, modern parallels, social media presence
**37d-bibliography-manager**: Source compilation, citation management
**37d-source-validator**: Quality assessment, verification, gap identification

## TODO File Format

Tasks in FILE TODO follow this progression:
```markdown
- [ ] Task description                           # Not started
- [R] Task description (started YYYY-MM-DD HH:MM)   # In progress  
- [x] Task description ✓ (YYYY-MM-DD HH:MM)        # Completed with results
- [0] Task description ✓ (YYYY-MM-DD HH:MM)        # Completed with no results
```

## Findings File Structure

```markdown
# 37d-[agent-name] Research Findings
## "[Book Title]" by [Author] ([Year])

### Research completed: YYYY-MM-DD HH:MM

---

## Task: [Task Name from TODO]
Date: YYYY-MM-DD HH:MM

### Finding 1: [Descriptive Title]
- **Fact**: [Specific information found]
- **Context**: [Why this is significant]
- **Source**: [Citation]
- **Quality**: ⭐⭐⭐⭐⭐
- **Verification**: [How this was confirmed]

### Citations:
[1] Author, "Title", Publisher, Year
[2] "Article Title", Website, URL, Accessed: YYYY-MM-DD
```

## Hook Integration

The 37d-save-search.py hook automatically saves raw search data to:
`docs/37d-[agent-name]/37d-[agent]_raw_WebSearch_[timestamp].json`

Agents focus on formatted findings - raw data is preserved automatically.

</context>

<examples>

## Example 1: Successful Task Execution
```
Agent: 37d-facts-hunter executing task research historical context
System: Reading FILE TODO...
System: Task marked as [R] running...
System: Executing WebSearch for "Brave New World" Huxley 1932 historical context...
System: Found 5 relevant sources...
System: Documenting findings with citations...
System: Task marked as [x] completed with timestamp...
System: Proceeding to next task...
```

## Example 2: No Results Found
```
Agent: 37d-symbol-analyst executing task analyze obscure symbols
System: Task marked as [R] running...
System: Executing multiple searches with various approaches...
System: No relevant results found after comprehensive search...
System: Task marked as [0] completed with timestamp...
System: Adding note about search attempts to findings...
```

## Example 3: Error Condition
```
Agent: 37d-polish-specialist starting session
System: Checking FILE TODO at docs/todo/TODO_37d-polish-specialist.md...
System: ERROR: FILE TODO missing - cannot proceed without task list
System: Exiting workflow
```

</examples>

<important-notes>

1. **Single Task Focus**: Execute ONE task at a time, update immediately
2. **Complete All Tasks**: NO minimum completion requirements - ALL tasks must be attempted
3. **Immediate Updates**: Update FILE TODO status during and after each task
4. **Quality Over Quantity**: Focus on finding accurate, well-cited information
5. **No Structure Management**: Agent does NOT create/verify folder structure
6. **Relative Paths**: All file paths relative to book directory CWD
7. **Task Extension**: Can ADD tasks to TODO if research reveals new areas, NEVER remove tasks

</important-notes>