# TODO: 37d-bibliography-manager
Book: Chłopi (The Peasants)
Author: Władysław Reymont
Year: 1904-1909
Location: books/0005_chlopi/

## Primary Tasks
- [x] Scan all agent findings and extract every numbered citation (2025-07-29 20:15)
- [x] Standardize citation formats to consistent academic style (2025-07-29 20:15)
- [x] Detect and merge duplicate citations from different agents (2025-07-29 20:15)
- [x] Verify citation quality and assign 5-star ratings (2025-07-29 20:15)
- [x] Organize citations by category (primary, secondary, Polish, digital, etc.) (2025-07-29 20:15)
- [x] Compile missing citations where agents made unsourced claims (2025-07-29 20:15)
- [x] Generate final comprehensive bibliography with cross-references (2025-07-29 20:15)
- [x] Create citation statistics and quality distribution analysis (2025-07-29 20:15)

## Search Focus Areas
Generated based on agent's bibliography expertise and "Chłopi" research scope:

1. **Citation Harvesting**: Extract all [1], [2], [3] etc. citations from every agent's findings files in docs/findings/
2. **Format Standardization**: Apply consistent academic format for books, journals, websites, social media, and Polish sources
3. **Duplicate Detection**: Identify when multiple agents cited the same source with different formatting
4. **Quality Assessment**: Rate each source 1-5 stars based on academic authority, accessibility, and relevance
5. **Polish Source Handling**: Ensure proper formatting for Polish academic sources, maintaining original titles with translations
6. **Digital Source Verification**: Check that all URLs work and include proper access dates
7. **Gap Analysis**: Identify claims made without citations and suggest where sources could be found
8. **Cross-Reference Creation**: Map which agents used which sources to show research overlap

## Output Requirements
- Save findings to: docs/findings/37d-bibliography-manager_findings.md
- Follow exact agent profile format with complete citation statistics
- Create sections for: Primary Sources, Scholarly Sources, Polish Sources, Digital/Social Media, Fan/Popular Sources
- Include cross-reference index showing source usage by multiple agents
- Provide citation issues log documenting problems found

## Notes
- Agent profile location: ../../.claude/agents/37d-bibliography-manager.md (relative from book directory)
- This agent runs AFTER all other agents complete their research
- Focus on Polish sources and ensure Nobel Prize materials are properly documented
- Maintain academic rigor while respecting youth-relevant sources