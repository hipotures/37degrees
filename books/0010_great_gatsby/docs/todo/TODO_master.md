# TODO Master - The Great Gatsby Research Workflow

**Book**: The Great Gatsby (Wielki Gatsby)  
**Author**: F. Scott Fitzgerald  
**Year**: 1925  
**Book Folder**: books/0010_great_gatsby/  
**Started**: 2025-07-28 08:01:28

## Overall Research Status

- [ ] 37d-facts-hunter - Historical facts and context expert
- [ ] 37d-symbol-analyst - Literary symbolism and cross-cultural interpretations  
- [ ] 37d-culture-impact - Cultural adaptations from films to TikTok
- [ ] 37d-polish-specialist - Polish reception and education focus (CRITICAL)
- [ ] 37d-youth-connector - Gen Z culture bridge
- [ ] 37d-bibliography-manager - Master of citations and references
- [ ] 37d-source-validator - Guardian of research integrity

## Workflow Notes

Sequential execution for reliable results. Each agent follows common workflow from docs/agents/WORKFLOW.md:

1. Read agent-specific TODO from docs/todo/TODO_37d-[agent].md
2. Execute imperative research commands from agent file
3. Save findings to docs/findings/37d-[agent]_findings.md
4. JSON search results auto-saved to docs/37d-[agent]/ folder
5. Search index auto-maintained in docs/37d-[agent]/37d-[agent]_searches_index.txt
6. Mark tasks complete with timestamp

## Lock File Management

- Lock format: tmp/0010_great_gatsby-37d-[agent].lock
- Created before each agent execution
- Removed after completion (even if agent fails)
- Used by 37d-save-search.py hook for JSON data routing

## Completion Status

Start time: 2025-07-28 08:01:28  
End time: _pending_  
Duration: _pending_