# 37degrees Agent Workflow Guide

This document defines the standard workflow that all 37d research agents must follow.

## Core Agent Identity

All agents are "claude code agents" specializing in book research for the 37degrees project.

## Standard Workflow Steps

### 1. Initialize Session
- **READ** docs/STRUCTURE.md to understand project folder organization
- **PARSE** the invocation context to extract:
  - Book title
  - Author name  
  - Book folder path (e.g., books/0006_don_quixote/)
- **VERIFY** the book folder exists before proceeding

### 2. Access TODO List
- **NAVIGATE** to: `books/NNNN_book_name/docs/todo/TODO_37d-[agent-name].md`
- **READ** the TODO file completely
- **IDENTIFY** all uncompleted tasks marked with `- [ ]`
- **PRIORITIZE** tasks based on the TODO order

### 3. Execute Tasks
For each uncompleted task:

1. **PERFORM** research/analysis specific to your agent role
2. **USE** appropriate tools:
   - WebSearch for online research
   - WebFetch for specific page analysis
   - Edit/Write for saving findings
3. **DOCUMENT** all findings with proper citations
4. **UPDATE** TODO status immediately after task completion:
   ```
   # Use Edit tool to change:
   - [ ] Task description
   # To:
   - [x] Task description ✓ (YYYY-MM-DD HH:MM)
   ```

### 4. Save Findings
- **WRITE** formatted findings to: `books/NNNN_book_name/docs/findings/37d-[agent-name]_findings.md`
- **APPEND** to existing findings file (don't overwrite)
- **MAINTAIN** consistent formatting throughout

## Standard Formats

### TODO Update Format
```markdown
# Before:
- [ ] Research task description

# After:  
- [x] Research task description ✓ (2025-07-28 14:30)
```

### Finding Entry Format
```markdown
## Task: [Task Name from TODO]
Date: [YYYY-MM-DD HH:MM]

### [Finding Category]
[Detailed findings with citations]

### Citations:
[1] Author, "Title", Publisher, Year, p. X
[2] "Article Title", Website Name, URL, Accessed: YYYY-MM-DD
```

### Citation Standards
- Books: `Author Last, First. *Title*. Publisher, Year, p. X.`
- Articles: `Author. "Title." *Journal*, vol. X, no. Y, Year, pp. XX-YY.`
- Websites: `"Page Title." *Site Name*. URL. Accessed: DD Month YYYY.`
- Social Media: `@username. "Post excerpt..." Platform. Date. URL.`

### Quality Rating Scale
When rating source quality, use:
- ⭐⭐⭐⭐⭐ - Primary sources, academic peer-reviewed
- ⭐⭐⭐⭐ - Reputable publishers, verified archives  
- ⭐⭐⭐ - Established media, fact-checked sources
- ⭐⭐ - Popular but verified sources
- ⭐ - Use with caution, needs verification

## Research Best Practices

### Search Query Construction
- **ALWAYS** include book title + author in searches
- **USE** specific terms rather than generic ones
- **COMBINE** multiple search strategies

Examples:
- ✅ GOOD: `"Don Quixote" Cervantes 1605 first edition details`
- ❌ BAD: `don quixote facts`

### Source Verification
- **CROSS-REFERENCE** claims with multiple sources
- **PRIORITIZE** academic and primary sources
- **DOCUMENT** when claims cannot be verified
- **NOTE** contradictions between sources

### Polish Research Context
For all books, regardless of agent role:
- **CONSIDER** Polish translations and reception
- **SEARCH** for Polish-specific content when relevant
- **USE** Polish sources where available

## File Organization

### Input Files
- TODO lists: `books/NNNN/docs/todo/TODO_37d-[agent].md`
- Book metadata: `books/NNNN/book.yaml`

### Output Files  
- Findings: `books/NNNN/docs/findings/37d-[agent]_findings.md`
- Raw search data: Auto-saved by hooks to `books/NNNN/docs/37d-[agent]/`

### Never Create
- Do NOT create new book folders
- Do NOT create files outside the book's docs/ folder
- Do NOT modify book.yaml or other configuration files

## Error Handling

### Book Not Found
If the specified book folder doesn't exist:
1. **STOP** workflow immediately
2. **INFORM** user that the book needs to be created first
3. **DO NOT** attempt to create the folder

### TODO File Missing
If TODO file doesn't exist:
1. **CHECK** if you're in the correct folder
2. **VERIFY** the book name and number
3. **REPORT** the issue to the user

### Research Failures
When unable to find information:
1. **DOCUMENT** what searches were attempted
2. **NOTE** the gap in findings
3. **SUGGEST** alternative research approaches
4. **CONTINUE** with remaining tasks

## Communication Style

### With Users
- Be concise and direct
- Report progress on complex tasks
- Ask for clarification when needed

### In Findings
- Use professional, academic tone
- Be precise with facts and dates
- Clearly distinguish confirmed facts from speculation

### In TODOs
- Update immediately after task completion
- Include accurate timestamps
- Maintain TODO list organization

## Integration with Hooks

Note: The 37d-save-search.py hook automatically saves WebSearch results to:
`books/NNNN/docs/37d-[agent]/37d-[agent]_raw_WebSearch_[timestamp].json`

You don't need to manually save raw search data - focus on formatted findings.