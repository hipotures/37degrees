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

# Copy specific 37d agent (example)
echo "Copying example 37d agent..."
if [ -f "/home/xai/DEV/37degrees/config/prompt/agents/37d-facts-hunter.md" ]; then
    cp "/home/xai/DEV/37degrees/config/prompt/agents/37d-facts-hunter.md" "$EXPORT_DIR/"
else
    echo "⚠️  37d-facts-hunter.md not found"
fi

# Copy 37d commands
echo "Copying 37d commands..."
cp /home/xai/DEV/37degrees/.claude/commands/37d-research.md "$EXPORT_DIR/37d-research.md"

if [ -f "/home/xai/DEV/37degrees/.claude/commands/37d-s1-gen-scenes.md" ]; then
    cp "/home/xai/DEV/37degrees/.claude/commands/37d-s1-gen-scenes.md" "$EXPORT_DIR/"
else
    echo "⚠️  37d-s1-gen-scenes.md not found"
fi

if [ -f "/home/xai/DEV/37degrees/.claude/commands/37d-s2-apply-style.md" ]; then
    cp "/home/xai/DEV/37degrees/.claude/commands/37d-s2-apply-style.md" "$EXPORT_DIR/"
else
    echo "⚠️  37d-s2-apply-style.md not found"
fi

# Copy hooks
echo "Copying hooks..."
if [ -f "/home/xai/DEV/37degrees/.claude/hooks/37d-save-search.py" ]; then
    cp /home/xai/DEV/37degrees/.claude/hooks/37d-save-search.py "$EXPORT_DIR/"
else
    echo "⚠️  37d-save-search.py not found"
fi
if [ -f "/home/xai/DEV/37degrees/.claude/hooks/37d-save-search.sh" ]; then
    cp /home/xai/DEV/37degrees/.claude/hooks/37d-save-search.sh "$EXPORT_DIR/"
else
    echo "⚠️  37d-save-search.sh not found"
fi

# Copy agent documentation from config/prompt/agents/
echo "Copying agent documentation..."
for doc in "STRUCTURE-BOOK.md" "research-report-prompt.md"; do
    if [ -f "/home/xai/DEV/37degrees/config/prompt/agents/$doc" ]; then
        cp "/home/xai/DEV/37degrees/config/prompt/agents/$doc" "$EXPORT_DIR/"
    else
        echo "⚠️  config/prompt/agents/$doc not found"
    fi
done

# Copy relevant docs from main docs directory  
echo "Copying relevant documentation from docs/..."
for doc in "SUBAGENT-DISCOVERY-REPORT.md" "ai-agent-instruction-guide.md" "PROMPT_GENERATION_GUIDE.md"; do
    if [ -f "/home/xai/DEV/37degrees/docs/$doc" ]; then
        cp "/home/xai/DEV/37degrees/docs/$doc" "$EXPORT_DIR/"
    fi
done

# Copy example graphics style
echo "Copying example graphics style..."
if [ -f "/home/xai/DEV/37degrees/config/prompt/graphics-styles/watercolor-style.yaml" ]; then
    cp "/home/xai/DEV/37degrees/config/prompt/graphics-styles/watercolor-style.yaml" "$EXPORT_DIR/"
else
    echo "⚠️  watercolor-style.yaml not found"
fi

# Copy example scene generator
echo "Copying example scene generator..."
if [ -f "/home/xai/DEV/37degrees/config/prompt/scene-generator/narrative-prompt-generator.md" ]; then
    cp "/home/xai/DEV/37degrees/config/prompt/scene-generator/narrative-prompt-generator.md" "$EXPORT_DIR/"
else
    echo "⚠️  narrative-prompt-generator.md not found"
fi

# Copy prompt templates
echo "Copying prompt templates..."
if [ -f "/home/xai/DEV/37degrees/config/prompt/scene-description-template.yaml" ]; then
    cp "/home/xai/DEV/37degrees/config/prompt/scene-description-template.yaml" "$EXPORT_DIR/"
else
    echo "⚠️  scene-description-template.yaml not found"
fi

if [ -f "/home/xai/DEV/37degrees/config/prompt/style-description.yaml" ]; then
    cp "/home/xai/DEV/37degrees/config/prompt/style-description.yaml" "$EXPORT_DIR/"
else
    echo "⚠️  style-description.yaml not found"
fi

# Copy main project README
echo "Copying main project README..."
if [ -f "/home/xai/DEV/37degrees/README.md" ]; then
    cp "/home/xai/DEV/37degrees/README.md" "$EXPORT_DIR/PROJECT-README.md"
else
    echo "⚠️  README.md not found"
fi

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
# Agent Definitions (example)
37d-facts-hunter.md

# Main Commands
37d-research.md
37d-s1-gen-scenes.md
37d-s2-apply-style.md

# Hooks
37d-save-search.py

# Documentation
STRUCTURE-BOOK.md
research-report-prompt.md
SUBAGENT-DISCOVERY-REPORT.md
ai-agent-instruction-guide.md
PROMPT_GENERATION_GUIDE.md

# Examples
watercolor-style.yaml
narrative-prompt-generator.md
scene-description-template.yaml
style-description.yaml

# Project Overview
PROJECT-README.md

# System Overview
README.md
```

## Agent Configuration

All agents have YAML frontmatter with:
- `execution_order`: 1-10 (execution sequence)
- `todo_list`: True/False (whether to generate TODO files)
- `min_tasks`/`max_tasks`: Task quantity limits

### Research Agents (todo_list: True)
- **37d-facts-hunter**: 8-14 tasks - Biographical facts and trivia (example included)
- **37d-culture-impact**: 6-10 tasks - Cultural adaptations and modern impact  
- **37d-symbol-analyst**: 4-8 tasks - Literary symbolism analysis
- **37d-polish-specialist**: 7-12 tasks - Polish reception and translations
- **37d-youth-connector**: 4-8 tasks - Gen Z relevance and study hacks

### System Agents (todo_list: False) 
- **37d-source-validator**: 0-0 tasks - Verifies all citations and facts
- **37d-bibliography-manager**: 0-0 tasks - Compiles master bibliography
- **37d-deep-research**: 0-5 tasks - Gap analysis and deep investigations

Note: Only 37d-facts-hunter.md included as example. All 8 agents are described in SUBAGENT-DISCOVERY-REPORT.md

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

# Create single file with all content using files-to-prompt
echo "Creating single file with files-to-prompt..."
SINGLE_FILE="/tmp/$(basename "$EXPORT_DIR").txt"
if command -v files-to-prompt >/dev/null 2>&1; then
    files-to-prompt "$EXPORT_DIR" > "$SINGLE_FILE"
    echo "📄 Single file created: $SINGLE_FILE"
else
    echo "⚠️  files-to-prompt not found - skipping single file creation"
fi

# Show summary
echo ""
echo "✅ 37degrees agents exported to: $EXPORT_DIR"
echo ""
echo "📊 Export Summary:"
echo "   - 1 example agent file (37d-facts-hunter.md)"
echo "   - 3 command files (37d-research.md, 37d-s1-gen-scenes.md, 37d-s2-apply-style.md)"
echo "   - 1 hook file (37d-save-search.py)"
echo "   - $(ls -1 "$EXPORT_DIR"/*.md | grep -v 37d | grep -v README | wc -l) documentation files"
echo "   - $(ls -1 "$EXPORT_DIR"/*.yaml | wc -l) example YAML files"
echo "   - $(ls -1 "$EXPORT_DIR" | wc -l) total files"
echo ""
echo "📁 Directory: $EXPORT_DIR"
echo "📄 README: $EXPORT_DIR/README.md"
if [ -f "$SINGLE_FILE" ]; then
    echo "📄 Single file: $SINGLE_FILE"
fi
echo ""