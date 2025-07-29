#!/bin/bash

# Export 37degrees agents to timestamped directory
# Usage: ./scripts/export-37d-system.sh

set -e

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
EXPORT_DIR="/tmp/37d-agents-$TIMESTAMP"

# Create export directory (flat structure)
echo "Creating export directory: $EXPORT_DIR"
mkdir -p "$EXPORT_DIR"

# Copy all 37d agents
echo "Copying 37d agents..."
cp /home/xai/DEV/37degrees/.claude/agents/37d-*.md "$EXPORT_DIR/"

# Copy 37d-research command (v4)
echo "Copying 37d-research command..."
cp /home/xai/DEV/37degrees/.claude/commands/37d-research.md "$EXPORT_DIR/37d-research.md"

# Copy hooks
echo "Copying hooks..."
cp /home/xai/DEV/37degrees/.claude/hooks/37d-save-search.py "$EXPORT_DIR/"
cp /home/xai/DEV/37degrees/.claude/hooks/37d-save-search.sh "$EXPORT_DIR/"

# Copy documentation
echo "Copying documentation..."
cp /home/xai/DEV/37degrees/docs/agents/STRUCTURE-BOOK.md "$EXPORT_DIR/"
cp /home/xai/DEV/37degrees/docs/agents/WORKFLOW.md "$EXPORT_DIR/"
cp /home/xai/DEV/37degrees/docs/agents/research-report-prompt.md "$EXPORT_DIR/"

# Create README with system overview
echo "Creating system overview..."
EXPORT_DATE=$(date)
{
echo "# 37degrees Agent System Export"
echo ""
echo "Exported on: $EXPORT_DATE"
cat << 'EOF'

## System Overview

This is the complete 37degrees book research agent system with 8 specialized agents (extensible) working in coordinated sequence.

**Requires Claude Code** - This system is designed to run in Claude Code (claude.ai/code), Anthropic's AI coding assistant. The agents are Claude Code subagents that work together through the Task tool.

## Documentation Links

- **Claude Code Overview**: https://docs.anthropic.com/en/docs/claude-code/overview
- **Subagents Guide**: https://docs.anthropic.com/en/docs/claude-code/sub-agents
- **Slash Commands**: https://docs.anthropic.com/en/docs/claude-code/slash-commands
- **Hooks Configuration**: https://docs.anthropic.com/en/docs/claude-code/hooks

## Files (Flat Structure)

```
# Agent Definitions
37d-facts-hunter.md
37d-culture-impact.md  
37d-symbol-analyst.md
37d-polish-specialist.md
37d-youth-connector.md
37d-source-validator.md
37d-bibliography-manager.md
37d-deep-research.md

# Main Workflow Command
37d-research.md

# Hooks
37d-save-search.py
37d-save-search.sh

# Documentation
STRUCTURE-BOOK.md
WORKFLOW.md
research-report-prompt.md

# System Overview
README.md
```

## Agent Configuration

All agents have YAML frontmatter with:
- `execution_order`: 1-10 (execution sequence)
- `todo_list`: True/False (whether to generate TODO files)
- `min_tasks`/`max_tasks`: Task quantity limits

### Research Agents (todo_list: True)
- **37d-facts-hunter**: 8-14 tasks - Biographical facts and trivia
- **37d-culture-impact**: 6-10 tasks - Cultural adaptations and modern impact  
- **37d-symbol-analyst**: 4-8 tasks - Literary symbolism analysis
- **37d-polish-specialist**: 7-12 tasks - Polish reception and translations
- **37d-youth-connector**: 4-8 tasks - Gen Z relevance and study hacks

### System Agents (todo_list: False) 
- **37d-source-validator**: 0-0 tasks - Verifies all citations and facts
- **37d-bibliography-manager**: 0-0 tasks - Compiles master bibliography
- **37d-deep-research**: 0-5 tasks - Gap analysis and deep investigations

## Usage

**Prerequisites:** Install Claude Code from https://claude.ai/code

1. Place 37d-*.md files in `.claude/agents/` directory
2. Place 37d-research.md in `.claude/commands/` directory
3. Place 37d-save-search.* files in `.claude/hooks/` directory
4. Configure hooks in Claude Code settings
5. Run in Claude Code: `/37d-research "Book Title"`

## Important Notes

- **Custom Instructions**: The 37d-research.md file contains the complete workflow logic and instructions for coordinating all agents. This is NOT a simple custom instruction - it's a sophisticated multi-step workflow that handles agent discovery, TODO generation, execution sequencing, and error recovery.

- **Version Information**: This export contains the v4 version of the research system with dynamic agent discovery, conditional TODO generation, and task quantity controls.

## Key Features

- **Dynamic agent discovery** - No hardcoded agent lists
- **Conditional TODO generation** - Based on agent configuration
- **Automatic search saving** - Via hooks integration
- **Task quantity control** - Min/max limits per agent
- **Parallel execution** - Groups by execution_order, parallel within groups
- **Gap analysis** - Deep research fills missing information
- **Quality control** - Source validation and bibliography management
EOF
} > "$EXPORT_DIR/README.md"

# Create file listing
echo "Creating file inventory..."
echo "## File Inventory" >> "$EXPORT_DIR/README.md"
echo "" >> "$EXPORT_DIR/README.md"
find "$EXPORT_DIR" -type f -name "*.md" -o -name "*.py" -o -name "*.sh" | \
  sort | \
  sed "s|$EXPORT_DIR/||" | \
  while read file; do
    echo "- $file" >> "$EXPORT_DIR/README.md"
  done

# Show summary
echo ""
echo "✅ 37degrees agents exported to: $EXPORT_DIR"
echo ""
echo "📊 Export Summary:"
echo "   - $(ls -1 "$EXPORT_DIR"/37d-*.md | wc -l) agent files"
echo "   - 1 workflow command file"
echo "   - $(ls -1 "$EXPORT_DIR"/37d-save-search.* | wc -l) hook files"
echo "   - $(ls -1 "$EXPORT_DIR"/*.md | grep -v 37d | grep -v README | wc -l) documentation files"
echo "   - $(ls -1 "$EXPORT_DIR" | wc -l) total files"
echo ""
echo "📁 Directory: $EXPORT_DIR"
echo "📄 README: $EXPORT_DIR/README.md"
echo ""