# Claude Code Subagent System Discovery Report

**Date**: 2025-07-29  
**Investigation**: Understanding how Claude Code Task tool and subagents work

## Executive Summary

Through extensive testing with the `test-hello` agent, we discovered fundamental characteristics of Claude Code's subagent system that significantly impact the 37d agent research framework. Key findings include context inheritance, token costs, and prompt delivery mechanisms.

## Key Discoveries

### 1. Subagent Context Inheritance

**Finding**: Subagents receive the **complete context** of the main agent, not an isolated environment.

**Evidence**:
- Subagent receives: Main system prompt + Custom agent .md file + User message from Task
- Context includes: CLAUDE.md instructions, git status, environment info, system reminders
- Token usage: 21.9k-24k tokens per subagent invocation

**Implications**:
- Subagents are "aware" of the entire project
- High token costs due to full context inheritance
- Subagents can work with project knowledge even when ignoring specific instructions

### 2. Task Prompt Delivery Mechanism

**Finding**: Task `prompt` parameter is successfully delivered to subagents as "User message".

**Evidence Testing**:
```json
Task(prompt="Agent context: {\"agent_name\": \"test-hello\", \"book_title\": \"Dune\"}", subagent_type="test-hello")
```

**Result**: Agent correctly received and parsed JSON from prompt parameter.

**Architecture**:
- Main agent calls: `Task(prompt="...", subagent_type="agent-name")`
- Subagent receives: System prompt + Agent .md content + User message (prompt content)
- STEP 1.0 in WORKFLOW.md is valid - agents can parse JSON from User message

### 3. CLAUDE.md File Reading Behavior

**Finding**: CLAUDE.md is **read from file** during subagent execution, not passed as static context.

**Test Method**:
1. Renamed CLAUDE.md to CLAUDE.md-1
2. Invoked subagent
3. Observed 2k token reduction (21.9k vs 24k tokens)

**Implications**:
- CLAUDE.md content can be controlled per execution
- Possible optimization: create lightweight CLAUDE.md versions for different agent types
- Context is dynamically loaded, not cached

### 4. Token Cost Analysis

| Configuration | Token Count | Delta | Notes |
|---------------|-------------|--------|-------|
| Full context (with CLAUDE.md) | 24k tokens | baseline | Complete project context |
| Without CLAUDE.md | 21.9k tokens | -2.1k | Missing project instructions |
| System minimum | ~19k tokens | estimated | Core Claude Code context only |

**Cost Projection for 37d System**:
- 8 agents × 24k tokens = **192k tokens** startup cost
- Plus actual research work = **300-500k tokens** per book
- High operational costs for comprehensive research

### 5. Agent Behavior Patterns

**"Working While Not Working" Phenomenon Explained**:

Previous observation: Agents seemed to ignore TODO instructions but still performed relevant work.

**Root Cause**: Full context inheritance means agents have complete project knowledge:
- Agent ignores specific JSON instructions
- But "knows" from CLAUDE.md what the project does
- Performs work based on general project understanding
- Creates confusion about instruction following

**Example**:
- Agent receives TODO: "Research Polish translations"
- Ignores specific instruction
- But knows from context this is a book research project
- Performs general book research instead
- Appears to "work" but not follow specific guidance

## Technical Implementation Details

### Subagent Execution Flow

```
1. Main Agent calls Task(prompt="JSON context", subagent_type="agent-name")
2. Claude Code loads agent-name.md file
3. Subagent starts with:
   - Standard Claude Code system prompt
   - Content from agent-name.md file  
   - Full main agent context (CLAUDE.md, git, environment)
   - User message = prompt parameter from Task
4. Subagent executes with complete project awareness
```

### Context Composition

**Subagent receives**:
1. **Core System Prompt**: "You are Claude Code, Anthropic's official CLI for Claude."
2. **Agent Instructions**: Complete content from `.claude/agents/agent-name.md`
3. **Project Context**: CLAUDE.md file contents (global + project-specific instructions)
4. **Environment Data**: Git status, working directory, system info, recent commits
5. **User Message**: Prompt parameter from Task call
6. **System Reminders**: Various operational guidelines and warnings

**Total Context Size**: 21.9k-24k tokens per invocation

### Agent Instruction Priority

Testing revealed instruction priority order:
1. **Agent .md file instructions** (highest priority)
2. **CLAUDE.md project context** (medium priority) 
3. **Task prompt parameter** (user message - can be ignored if agent has other priorities)

## Optimization Strategies

### 1. Context Minimization (Limited Impact)

**Approach**: Create lightweight CLAUDE.md versions
**Savings**: ~2k tokens (8% reduction)
**Trade-off**: Loss of project context and guidelines

### 2. Agent Count Reduction (High Impact)

**Approach**: Use 3-4 specialized agents instead of 8
**Savings**: ~100k tokens startup cost
**Trade-off**: Less comprehensive research coverage

### 3. Selective Agent Usage (High Impact)

**Approach**: Use full 37d system only for priority books
**Savings**: Major cost reduction through usage frequency
**Trade-off**: Inconsistent research depth across books

### 4. Task Simplification (Medium Impact)

**Approach**: Smaller TODO lists, focused research scope
**Savings**: Reduced execution time and follow-up research
**Trade-off**: Less thorough research per book

## Recommendations

### For 37d System Operation

1. **Accept High Token Costs**: System provides comprehensive, intelligent research but at premium cost
2. **Use Strategically**: Deploy full system for high-priority books, simplified versions for others
3. **Monitor Token Usage**: Track costs per book to optimize budget allocation
4. **Agent Instruction Clarity**: Ensure .md files have clear, specific instructions since they take priority

### For Future Development

1. **Cost Tracking**: Implement token usage monitoring for 37d system
2. **Agent Tiers**: Create "light" and "full" versions of agent configurations
3. **Conditional Context**: Research ways to provide selective context to different agent types
4. **Batch Processing**: Group similar research tasks to minimize repeated context loading

## Technical Validation

### Test Environment
- **System**: Claude Code on Linux (Manjaro)
- **Test Agent**: test-hello.md modified for context debugging
- **Test Method**: Multiple invocations with different context configurations
- **Measurement**: Token counts from Claude Code output

### Test Cases Executed
1. ✅ Full context subagent invocation (24k tokens)
2. ✅ No CLAUDE.md invocation (21.9k tokens)  
3. ✅ JSON parsing from Task prompt (successful)
4. ✅ Context inheritance verification (complete inheritance confirmed)
5. ✅ Agent instruction priority testing (confirmed hierarchy)

## Conclusion

The Claude Code subagent system provides powerful capabilities for complex research tasks but comes with significant token costs due to complete context inheritance. The 37d system works as designed but requires careful cost management. 

**Key Insight**: Subagents are not isolated workers but context-aware collaborators with complete project knowledge. This explains both their intelligence and their operational costs.

**Strategic Decision Required**: Balance research comprehensiveness against operational costs based on project priorities and budget constraints.

---

*This report documents findings from investigation session 2025-07-29. Technical details may evolve as Claude Code system updates are released.*