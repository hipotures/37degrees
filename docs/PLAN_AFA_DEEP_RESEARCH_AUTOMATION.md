# Plan: Automatyczny proces Deep Research dla AFA (Audio Format Analyzer)

## Cel
Utworzenie systemu automatycznego generowania Deep Research dla AFA, który:
1. Pobiera zadanie z nowej listy TODOIT `gemini-afa-research`
2. Składa prompt z 17 plików agentów (8 specjalistycznych + 9 językowych)
3. Zapisuje prompt do `books/{book}/prompts/afa-deep-research-prompt.md`
4. Uruchamia Deep Research w Gemini
5. Zapisuje URL jako `GEMINI_AFA_URL` w TODOIT

## Odpowiedzi użytkownika
✅ **Lista TODOIT**: Nowa osobna lista `gemini-afa-research`
✅ **Prompt storage**: Zapisz do pliku w `books/*/prompts/` lub `media/*/prompts/`
✅ **Format**: Zachować Markdown (##, -, listy)
✅ **Assembler**: Osobny moduł TypeScript
✅ **Property name**: `GEMINI_AFA_URL`

## Struktura plików do utworzenia

```
scripts/
├── internal/
│   └── find_next_research_afa_task.py       # Nowy - szuka pending w gemini-afa-research
├── gemini/
│   ├── assemble-afa-prompt.ts               # Nowy - składa prompt z 17 agentów
│   ├── todoit-read-research-afa-task.sh     # Nowy - wrapper dla find_next
│   ├── todoit-write-research-afa-result.sh  # Nowy - zapisuje GEMINI_AFA_URL
│   ├── execute-deep-research-afa.ts         # Nowy - Playwright automation
│   └── process-deep-research-afa-task.sh    # Nowy - główny orchestrator
```

## Komponenty do implementacji

### 1. `assemble-afa-prompt.ts` - Prompt Assembler

**Zadanie**: Złożyć prompt z 17 plików markdown agentów

**Źródła promptów**:
- **8 specjalistycznych**:
  - `37d-au-culture-impact-researcher.md`
  - `37d-au-youth-digital-connector.md`
  - `37d-au-symbols-meaning-analyst.md`
  - `37d-au-facts-history-specialist.md`
  - `37d-au-reality-wisdom-checker.md`
  - `37d-au-dark-drama-investigator.md`
  - `37d-au-writing-innovation-expert.md`
  - `37d-au-content-warning-assessor.md`

- **9 językowych**:
  - `37d-au-local-pl-context-specialist.md`
  - `37d-au-local-en-context-specialist.md`
  - `37d-au-local-de-context-specialist.md`
  - `37d-au-local-fr-context-specialist.md`
  - `37d-au-local-es-context-specialist.md`
  - `37d-au-local-pt-context-specialist.md`
  - `37d-au-local-ja-context-specialist.md`
  - `37d-au-local-ko-context-specialist.md`
  - `37d-au-local-hi-context-specialist.md`

**Ekstrakcja z każdego agenta**:
```typescript
interface AgentSection {
  name: string;
  primaryTasks: string[];      // z sekcji "## Primary Tasks"
  searchFocus: string[];        // z sekcji "## Search Focus Areas"
  outputRequirements: string[]; // z sekcji "## Output Requirements"
  notes: string[];              // z sekcji "## Notes"
}
```

**Format wyjściowy** (`books/{book}/prompts/afa-deep-research-prompt.md`):
```markdown
# Deep Research - AFA Analysis for {book_title}

## Book Information
title: {title}
author: {author}
year: {year}

## Research Agents - Specialized Topics

### Culture Impact Research
**Primary Tasks:**
- Research key film, theater adaptations
- Find influence on creators
...

**Search Focus Areas:**
1. Media Adaptations: Movies, series...
2. Creative Influence: Artists inspired...

**Output Requirements:**
- 50-60 specific examples
- Concrete names, titles, dates

**Notes:**
- Shows why book matters
- Collect from different periods

### Youth Digital Connection
[...]

### Symbols & Meaning Analysis
[...]

### Facts & History
[...]

### Reality & Wisdom
[...]

### Dark Drama Investigation
[...]

### Writing Innovation
[...]

### Content Warning Assessment
[...]

## Research Agents - Language Contexts

### Polish Context (pl)
**Primary Tasks:**
- Research publication history in Poland
...

**Search Focus Areas:**
1. Publication History: How book reached Poland
2. Translation Challenges: Translator problems
...

**Output Requirements:**
- 20-30 facts about local reception
- Specific Polish translators, actors
...

**Notes:**
- Creates local connection
- Priority: things Polish listeners remember
...

### English Context (en)
[...]

### German Context (de)
[...]

### French Context (fr)
[...]

### Spanish Context (es)
[...]

### Portuguese Context (pt)
[...]

### Japanese Context (ja)
[...]

### Korean Context (ko)
[...]

### Hindi Context (hi)
[...]

## Final Instructions
Generate comprehensive research covering all above areas.
Focus on factual, specific, verifiable information.
Each language context should have unique insights for that culture.
```

**API**:
```typescript
// Usage
const prompt = await assembleAFAPrompt(bookFolder);
// Returns: string (full markdown prompt)
```

**Implementacja**:
```typescript
import * as fs from 'fs';
import * as path from 'path';

interface AgentSection {
  name: string;
  primaryTasks: string[];
  searchFocus: string[];
  outputRequirements: string[];
  notes: string[];
}

async function assembleAFAPrompt(bookFolder: string): Promise<string> {
  const projectRoot = '/home/xai/DEV/37degrees';

  // 1. Read book.yaml
  const bookYaml = readBookInfo(bookFolder);

  // 2. Parse specialized agents
  const specializedAgents = [
    'culture-impact-researcher',
    'youth-digital-connector',
    'symbols-meaning-analyst',
    'facts-history-specialist',
    'reality-wisdom-checker',
    'dark-drama-investigator',
    'writing-innovation-expert',
    'content-warning-assessor'
  ];

  const specializedSections = specializedAgents.map(agent => {
    const agentPath = path.join(projectRoot, '.claude/agents', `37d-au-${agent}.md`);
    return parseAgentFile(agentPath);
  });

  // 3. Parse language agents
  const languages = ['pl', 'en', 'de', 'fr', 'es', 'pt', 'ja', 'ko', 'hi'];
  const languageSections = languages.map(lang => {
    const agentPath = path.join(projectRoot, '.claude/agents', `37d-au-local-${lang}-context-specialist.md`);
    return parseAgentFile(agentPath);
  });

  // 4. Assemble final prompt
  return buildPrompt(bookYaml, specializedSections, languageSections);
}

function parseAgentFile(filePath: string): AgentSection {
  const content = fs.readFileSync(filePath, 'utf-8');

  // Extract sections using regex
  const primaryTasks = extractSection(content, '## Primary Tasks');
  const searchFocus = extractSection(content, '## Search Focus Areas');
  const outputRequirements = extractSection(content, '## Output Requirements');
  const notes = extractSection(content, '## Notes');

  // Extract name from frontmatter or filename
  const nameMatch = content.match(/name: (.+)/);
  const name = nameMatch ? nameMatch[1] : path.basename(filePath);

  return {
    name,
    primaryTasks,
    searchFocus,
    outputRequirements,
    notes
  };
}

function extractSection(content: string, header: string): string[] {
  const headerRegex = new RegExp(`${header}\\s*\\n([\\s\\S]*?)(?=\\n## |$)`);
  const match = content.match(headerRegex);

  if (!match) return [];

  // Split by newlines and filter out empty lines
  return match[1]
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);
}

function buildPrompt(
  bookYaml: any,
  specializedSections: AgentSection[],
  languageSections: AgentSection[]
): string {
  let prompt = `# Deep Research - AFA Analysis for ${bookYaml.title}\n\n`;

  prompt += `## Book Information\n`;
  prompt += `title: ${bookYaml.title}\n`;
  prompt += `author: ${bookYaml.author}\n`;
  prompt += `year: ${bookYaml.year || 'Unknown'}\n\n`;

  prompt += `## Research Agents - Specialized Topics\n\n`;

  for (const section of specializedSections) {
    prompt += formatSection(section);
  }

  prompt += `\n## Research Agents - Language Contexts\n\n`;

  for (const section of languageSections) {
    prompt += formatSection(section);
  }

  prompt += `\n## Final Instructions\n`;
  prompt += `Generate comprehensive research covering all above areas.\n`;
  prompt += `Focus on factual, specific, verifiable information.\n`;
  prompt += `Each language context should have unique insights for that culture.\n`;

  return prompt;
}

function formatSection(section: AgentSection): string {
  let output = `### ${section.name}\n\n`;

  if (section.primaryTasks.length > 0) {
    output += `**Primary Tasks:**\n`;
    output += section.primaryTasks.join('\n') + '\n\n';
  }

  if (section.searchFocus.length > 0) {
    output += `**Search Focus Areas:**\n`;
    output += section.searchFocus.join('\n') + '\n\n';
  }

  if (section.outputRequirements.length > 0) {
    output += `**Output Requirements:**\n`;
    output += section.outputRequirements.join('\n') + '\n\n';
  }

  if (section.notes.length > 0) {
    output += `**Notes:**\n`;
    output += section.notes.join('\n') + '\n\n';
  }

  return output;
}
```

### 2. `find_next_research_afa_task.py`

Analogiczny do `find_next_research_task.py` ale:
- Lista: `gemini-afa-research` (nie `gemini-au-deep-research`)
- Szuka: pierwszego zadania ze statusem `pending`

```python
#!/usr/bin/env python3
"""
Find next pending AFA Deep Research task from gemini-afa-research list.

Usage:
    python find_next_research_afa_task.py

Output JSON:
    {"SOURCE_NAME": "0055_of_mice_and_men", "STATUS": "found"}
    {"status": "no_tasks_found", "message": "..."}
    {"status": "error", "message": "..."}
"""

import subprocess
import sys
import json
import os

TARGET_LIST = "gemini-afa-research"

def run_todoit_cmd(args):
    """Run todoit command with JSON output"""
    cmd = ["todoit"] + args
    env = os.environ.copy()
    env["TODOIT_OUTPUT_FORMAT"] = "json"

    result = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    return result.stdout, result.returncode

def main():
    """Find first pending AFA research task"""

    # Get first pending item from list using find-status
    output, returncode = run_todoit_cmd([
        "item", "find-status",
        "--list", TARGET_LIST,
        "--status", "pending",
        "--limit", "1"
    ])

    if returncode != 0:
        print(json.dumps({"status": "error", "message": "Failed to query TODOIT"}))
        sys.exit(1)

    try:
        # Parse JSON output (find-status returns clean JSON)
        result = json.loads(output)

        if not result.get("data") or len(result["data"]) == 0:
            print(json.dumps({"status": "no_tasks_found", "message": "No pending AFA research tasks"}))
            sys.exit(0)

        # Get first pending item (find-status uses "Item Key" field)
        first_item = result["data"][0]
        book_key = first_item.get("Item Key")

        if not book_key:
            print(json.dumps({"status": "error", "message": "Missing 'Item Key' in TODOIT response"}))
            sys.exit(1)

        # Success - return book folder
        print(json.dumps({
            "SOURCE_NAME": book_key,
            "STATUS": "found"
        }))
        sys.exit(0)

    except (json.JSONDecodeError, KeyError) as e:
        print(json.dumps({"status": "error", "message": f"JSON parsing error: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 3. `todoit-read-research-afa-task.sh`

Wrapper dla Python script, zwraca JSON:

```bash
#!/bin/bash
# TODOIT CLI wrapper for reading next AFA Deep Research task
# Usage: ./todoit-read-research-afa-task.sh
# Output: JSON with all needed data for AFA Deep Research generation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ============================================================================
# PHASE 1: Call Python script to find next task
# ============================================================================

TASK_JSON=$(python "$PROJECT_ROOT/scripts/internal/find_next_research_afa_task.py" 2>/dev/null)
PYTHON_EXIT=$?

if [ $PYTHON_EXIT -ne 0 ]; then
  echo '{"error": "Failed to execute find_next_research_afa_task.py"}' >&2
  exit 1
fi

# Parse status from Python output
STATUS=$(echo "$TASK_JSON" | jq -r '.STATUS // .status' 2>/dev/null)

if [ -z "$STATUS" ]; then
  echo '{"error": "Invalid JSON from find_next_research_afa_task.py"}' >&2
  exit 1
fi

# If no tasks found, return the original message
if [ "$STATUS" != "found" ]; then
  # Return Python's original response (no_tasks_found, error, etc.)
  echo "$TASK_JSON"
  exit 0
fi

# ============================================================================
# PHASE 2: Extract data from Python result
# ============================================================================

SOURCE_NAME=$(echo "$TASK_JSON" | jq -r '.SOURCE_NAME')

if [ -z "$SOURCE_NAME" ]; then
  echo '{"error": "Missing SOURCE_NAME in Python output"}' >&2
  exit 1
fi

# ============================================================================
# PHASE 3: Extract book number for informational purposes
# ============================================================================

# Extract book number from SOURCE_NAME (format: NNNN_xxx)
BOOK_NUMBER=$(echo "$SOURCE_NAME" | cut -d_ -f1 | sed 's/^0*//')

# Handle edge case: if number becomes empty (e.g., "0000"), default to 1
if [ -z "$BOOK_NUMBER" ]; then
  BOOK_NUMBER=1
fi

# ============================================================================
# PHASE 4: Output all data as JSON
# ============================================================================

jq -n \
  --arg source "$SOURCE_NAME" \
  --arg book_num "$BOOK_NUMBER" \
  '{
    ready: true,
    source_name: $source,
    book_number: $book_num
  }'
```

### 4. `todoit-write-research-afa-result.sh`

Zapisuje wyniki z użyciem `GEMINI_AFA_URL`:

```bash
#!/bin/bash
# TODOIT CLI wrapper for writing AFA Deep Research results
# Usage: ./todoit-write-research-afa-result.sh <source_name> <status> [error_message] [search_url]
# Output: JSON with success status

set -e

SOURCE_NAME="$1"
STATUS="$2"
ERROR_MSG="${3:-}"
SEARCH_URL="${4:-}"

TARGET_LIST="gemini-afa-research"

# ============================================================================
# Validation
# ============================================================================

if [ -z "$SOURCE_NAME" ] || [ -z "$STATUS" ]; then
  echo '{"success": false, "error": "Missing required parameters: source_name, status"}' >&2
  exit 1
fi

# Validate status (in_progress = success, failed = error)
if [[ ! "$STATUS" =~ ^(in_progress|failed|pending)$ ]]; then
  echo '{"success": false, "error": "Invalid status. Must be: in_progress, failed, or pending"}' >&2
  exit 1
fi

ERRORS=()

# ============================================================================
# PHASE 1: Update item status
# ============================================================================

# Update item status (not subitem - research tasks are item-level)
OUTPUT=$(echo "y" | todoit item status --list "$TARGET_LIST" --item "$SOURCE_NAME" --status "$STATUS" 2>&1)
if echo "$OUTPUT" | grep -q "❌"; then
  ERRORS+=("Failed to update status to $STATUS: $OUTPUT")
fi

# ============================================================================
# PHASE 2: Save GEMINI_AFA_URL if provided (success case)
# ============================================================================

if [ -n "$SEARCH_URL" ]; then
  OUTPUT=$(echo "y" | todoit item property set --list "$TARGET_LIST" --item "$SOURCE_NAME" --key GEMINI_AFA_URL --value "$SEARCH_URL" 2>&1)
  if echo "$OUTPUT" | grep -q "❌"; then
    ERRORS+=("Failed to set GEMINI_AFA_URL property: $OUTPUT")
  fi
fi

# ============================================================================
# PHASE 3: Save error message if provided (failure case)
# ============================================================================

if [ -n "$ERROR_MSG" ]; then
  # Truncate to 500 chars
  ERROR_TRUNCATED="${ERROR_MSG:0:500}"
  OUTPUT=$(echo "y" | todoit item property set --list "$TARGET_LIST" --item "$SOURCE_NAME" --key ERROR --value "$ERROR_TRUNCATED" 2>&1)
  if echo "$OUTPUT" | grep -q "❌"; then
    ERRORS+=("Failed to set error property: $OUTPUT")
  fi
fi

# ============================================================================
# Return result
# ============================================================================

if [ ${#ERRORS[@]} -eq 0 ]; then
  jq -n \
    --arg status "$STATUS" \
    --arg source "$SOURCE_NAME" \
    --arg url "$SEARCH_URL" \
    '{
      success: true,
      status: $status,
      source_name: $source,
      gemini_afa_url: ($url | if . == "" then null else . end),
      message: "All data saved successfully"
    }'
else
  ERROR_LIST=$(printf '%s\n' "${ERRORS[@]}" | jq -R . | jq -s .)
  jq -n \
    --argjson errors "$ERROR_LIST" \
    '{
      success: false,
      errors: $errors
    }'
  exit 1
fi
```

### 5. `execute-deep-research-afa.ts`

Główna automatyzacja - **kopia `execute-deep-research.ts` z dodatkową fazą assemblera**:

```typescript
// ... (wszystkie importy jak w execute-deep-research.ts)
import { assembleAFAPrompt } from './assemble-afa-prompt';

// CONFIG identyczny jak w execute-deep-research.ts

async function executeDeepResearchAFA(params: DeepResearchParams): Promise<DeepResearchResult> {
  // ... (PHASE 0-1 identyczne: Read book info, Browser Setup)

  // ========================================================================
  // PHASE 0.5: Assemble AFA prompt from 17 agents
  // ========================================================================

  console.error('[0.5/10] Assembling AFA research prompt...');

  try {
    const afaPrompt = await assembleAFAPrompt(params.sourceName, bookInfo);

    // Save to books/{book}/prompts/afa-deep-research-prompt.md
    const promptPath = path.join(
      CONFIG.projectRoot,
      'books',
      params.sourceName,
      'prompts',
      'afa-deep-research-prompt.md'
    );

    fs.mkdirSync(path.dirname(promptPath), { recursive: true });
    fs.writeFileSync(promptPath, afaPrompt, 'utf-8');

    console.error(`  ✓ Prompt saved: ${promptPath}`);
    console.error(`  → Total length: ${afaPrompt.length} characters`);
  } catch (error: any) {
    throw new Error(`Failed to assemble AFA prompt: ${error.message}`);
  }

  console.error('');

  // ... (PHASE 2-10 identyczne jak w execute-deep-research.ts)
  // Tylko różnica: w PHASE 5 ładujemy promptPath zamiast CONFIG.promptFile

  // PHASE 5: Load prompt to clipboard
  const promptPath = path.join(
    CONFIG.projectRoot,
    'books',
    params.sourceName,
    'prompts',
    'afa-deep-research-prompt.md'
  );
  loadPromptToClipboard(promptPath);

  // ... (reszta identyczna)
}
```

### 6. `process-deep-research-afa-task.sh`

Orchestrator 3-fazowy (analogiczny do `process-deep-research-task.sh`):

```bash
#!/bin/bash
# Orchestrator script for Gemini AFA Deep Research workflow
# Usage: ./process-deep-research-afa-task.sh [--headless=false]

set -e

HEADLESS="true"

# Parse optional flags
if [ "$1" == "--headless=false" ]; then
  HEADLESS="false"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================" >&2
echo "Gemini AFA Deep Research Workflow" >&2
echo "Headless: $HEADLESS" >&2
echo "========================================" >&2
echo "" >&2

# ============================================================================
# PHASE 1: Read task from TODOIT
# ============================================================================

echo "[1/3] Reading task from TODOIT..." >&2

set +e
READ_RESULT=$("$SCRIPT_DIR/todoit-read-research-afa-task.sh")
READ_EXIT=$?
set -e

if [ $READ_EXIT -ne 0 ]; then
  echo "✗ Failed to read task from TODOIT" >&2
  echo "$READ_RESULT" >&2
  exit 1
fi

# Check if ready
READY=$(echo "$READ_RESULT" | jq -r '.ready')

if [ "$READY" != "true" ]; then
  MESSAGE=$(echo "$READ_RESULT" | jq -r '.message // "No tasks ready"')
  echo "ℹ $MESSAGE" >&2
  echo "$READ_RESULT"
  exit 0
fi

# Extract data
SOURCE_NAME=$(echo "$READ_RESULT" | jq -r '.source_name')
BOOK_NUMBER=$(echo "$READ_RESULT" | jq -r '.book_number')

echo "  ✓ Source: $SOURCE_NAME" >&2
echo "  ✓ Book number: $BOOK_NUMBER" >&2
echo "" >&2

# ============================================================================
# PHASE 2: Run Playwright AFA Deep Research automation
# ============================================================================

echo "[2/3] Running Playwright AFA Deep Research automation..." >&2

# Construct command with parameters
if [ "$HEADLESS" == "false" ]; then
  RESEARCH_CMD="npx ts-node $SCRIPT_DIR/execute-deep-research-afa.ts \"$SOURCE_NAME\" false"
else
  RESEARCH_CMD="npx ts-node $SCRIPT_DIR/execute-deep-research-afa.ts \"$SOURCE_NAME\""
fi

echo "  → Command: npx ts-node execute-deep-research-afa.ts $SOURCE_NAME" >&2

# Run AFA Deep Research automation
set +e
RESEARCH_JSON=$(eval "$RESEARCH_CMD" 2>&2)
RESEARCH_EXIT=$?
set -e

# Validate JSON
if [ -z "$RESEARCH_JSON" ] || ! echo "$RESEARCH_JSON" | jq empty 2>/dev/null; then
  echo "✗ Failed to get valid JSON from Playwright" >&2
  echo "Output: $RESEARCH_JSON" >&2
  exit 1
fi

# Parse result
SUCCESS=$(echo "$RESEARCH_JSON" | jq -r '.success')
SEARCH_URL=$(echo "$RESEARCH_JSON" | jq -r '.searchUrl // empty')
ERROR_MSG=$(echo "$RESEARCH_JSON" | jq -r '.error // empty')

echo "  ✓ AFA Deep Research automation completed" >&2
echo "  → Success: $SUCCESS" >&2
if [ -n "$SEARCH_URL" ]; then
  echo "  → Search URL: ${SEARCH_URL:0:80}..." >&2
fi
echo "" >&2

# ============================================================================
# PHASE 3: Save results to TODOIT
# ============================================================================

echo "[3/3] Saving results to TODOIT..." >&2

# Determine status
if [ "$SUCCESS" == "true" ]; then
  STATUS="in_progress"  # AFA Deep Research is running in background
else
  STATUS="failed"
fi

echo "  → Status: $STATUS" >&2

# Construct write command
WRITE_CMD="$SCRIPT_DIR/todoit-write-research-afa-result.sh \"$SOURCE_NAME\" \"$STATUS\""

# Add error message if present
if [ -n "$ERROR_MSG" ]; then
  ESCAPED_ERROR=$(echo "$ERROR_MSG" | sed 's/"/\\"/g')
  WRITE_CMD="$WRITE_CMD \"$ESCAPED_ERROR\""
else
  WRITE_CMD="$WRITE_CMD \"\""
fi

# Add search URL if present
if [ -n "$SEARCH_URL" ]; then
  WRITE_CMD="$WRITE_CMD \"$SEARCH_URL\""
fi

# Execute write
set +e
WRITE_RESULT=$(eval "$WRITE_CMD")
WRITE_EXIT=$?
set -e

if [ $WRITE_EXIT -ne 0 ]; then
  echo "✗ Failed to save to TODOIT" >&2
  echo "$WRITE_RESULT" >&2
  exit 1
fi

echo "  ✓ Saved to TODOIT" >&2
echo "" >&2

# ============================================================================
# Final output
# ============================================================================

echo "========================================" >&2
echo "✓ Workflow completed successfully" >&2
echo "========================================" >&2

TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
SCREENSHOT="/tmp/gemini-deep-research-afa-*.png"

# Output final JSON result
jq -n \
  --arg source "$SOURCE_NAME" \
  --arg url "$SEARCH_URL" \
  --arg status "$STATUS" \
  --arg timestamp "$TIMESTAMP" \
  --arg screenshot "$SCREENSHOT" \
  --argjson success "$SUCCESS" \
  --arg error_msg "$ERROR_MSG" \
  '{
    success: $success,
    source_name: $source,
    gemini_afa_url: ($url | if . == "" then null else . end),
    status: $status,
    timestamp: $timestamp,
    screenshot: $screenshot,
    error: ($error_msg | if . == "" then null else . end)
  }'

# Exit with appropriate code
if [ "$SUCCESS" == "true" ]; then
  exit 0
else
  exit 1
fi
```

## Kluczowe różnice vs obecny Deep Research

| Aspekt | Obecny (audio) | Nowy (AFA) |
|--------|---------------|-----------|
| Lista TODOIT | `gemini-au-deep-research` | `gemini-afa-research` |
| Prompt source | Jeden plik `podcast_research_prompt.md` | 17 plików agentów składanych dynamicznie |
| Prompt location | `docs/audio-research/` (statyczny) | `books/{book}/prompts/` (generowany per książka) |
| Assembler | Brak | `assemble-afa-prompt.ts` |
| Property name | `SEARCH_URL` | `GEMINI_AFA_URL` |
| Header format | Title/Author | Title/Author/Year |
| Skrypty | `process-deep-research-task.sh` | `process-deep-research-afa-task.sh` |

## Kolejność implementacji

1. ✅ `find_next_research_afa_task.py` - prosta modyfikacja istniejącego (15 min)
2. ✅ `todoit-read-research-afa-task.sh` - wrapper (10 min)
3. ✅ `todoit-write-research-afa-result.sh` - modyfikacja z GEMINI_AFA_URL (15 min)
4. 🔧 `assemble-afa-prompt.ts` - **NAJWIĘKSZA PRACA** (2h)
   - Parser markdown agentów
   - Ekstrakcja sekcji (Primary Tasks, Search Focus, Output Requirements, Notes)
   - Formatowanie wyjściowe
5. ✅ `execute-deep-research-afa.ts` - kopia + integracja assemblera (1h)
6. ✅ `process-deep-research-afa-task.sh` - orchestrator (15 min)

**Całkowity czas: ~4 godziny**

## Testowanie

```bash
# 1. Utworzyć listę TODOIT
todoit list create --key gemini-afa-research --title "Gemini AFA Research Queue"

# 2. Dodać testowe zadanie
todoit item add --list gemini-afa-research --key 0055_of_mice_and_men --title "AFA Research: Of Mice and Men"

# 3. Uruchomić workflow
./scripts/gemini/process-deep-research-afa-task.sh

# 4. Sprawdzić wygenerowany prompt
cat books/0055_of_mice_and_men/prompts/afa-deep-research-prompt.md

# 5. Sprawdzić property w TODOIT
todoit item property get --list gemini-afa-research --item 0055_of_mice_and_men --key GEMINI_AFA_URL
```

## Potencjalne problemy i rozwiązania

### Problem 1: Różnice w strukturze agentów
**Rozwiązanie**: Assembler musi być odporny na brakujące sekcje, użyć try-catch i wartości domyślnych

### Problem 2: Za długi prompt (limit Gemini)
**Rozwiązanie**: Monitorować długość promptu, ewentualnie skrócić sekcje Notes lub użyć summarization

### Problem 3: Parsowanie markdown agentów
**Rozwiązanie**: Użyć prostych regex do ekstrakcji sekcji między `## Header` a następnym `##` lub końcem pliku

### Problem 4: Encoding issues (polskie znaki w agentach)
**Rozwiązanie**: Zawsze czytać pliki z `utf-8` encoding

## Metryki sukcesu

- ✅ Prompt jest generowany automatycznie z 17 agentów
- ✅ Prompt zachowuje markdown formatting
- ✅ Prompt jest zapisywany do `books/{book}/prompts/`
- ✅ Deep Research uruchamia się poprawnie
- ✅ URL jest zapisywany jako `GEMINI_AFA_URL` w TODOIT
- ✅ Proces działa end-to-end bez błędów
- ✅ Można uruchomić dla wielu książek sekwencyjnie

## Przykładowy output

```bash
$ ./scripts/gemini/process-deep-research-afa-task.sh

========================================
Gemini AFA Deep Research Workflow
Headless: true
========================================

[1/3] Reading task from TODOIT...
  ✓ Source: 0055_of_mice_and_men
  ✓ Book number: 55

[2/3] Running Playwright AFA Deep Research automation...
[0/10] Reading book information...
  ✓ Title: Of Mice and Men
  ✓ Author: John Steinbeck

[0.5/10] Assembling AFA research prompt...
  → Parsing 8 specialized agents...
  → Parsing 9 language agents...
  ✓ Prompt saved: books/0055_of_mice_and_men/prompts/afa-deep-research-prompt.md
  → Total length: 12453 characters

[1/10] Launching browser...
  → Connecting to existing browser on localhost:9222
  ✓ Connected to existing browser (1 pages)

[2/10] Navigating to Gemini...
  ✓ Navigation complete

[3/10] Verifying model...
  → Current model: Gemini 2.5 Pro
  ✓ Already using 2.5 Pro - skipping change

[4/10] Activating Deep Research...
  ✓ Deep Research activated

[5/10] Loading instructions to clipboard...
  ✓ Instructions loaded to clipboard

[6/10] Entering prompt...
  ✓ Header typed
  ✓ Instructions pasted
  ✓ Prompt submitted

[7/10] Waiting for plan generation...
  → Waiting for "Start search" button (max 180s)...
  ✓ Plan ready, start button appeared

[8/10] Starting search...
  ✓ Search started

[9/10] Getting chat URL...
  ✓ URL: https://gemini.google.com/app/abc123xyz

[10/10] Renaming chat...
  → Menu opened
  → Rename dialog opened
  → Entered new name: 0055_of_mice_and_men
  ✓ Chat renamed to: 0055_of_mice_and_men

  ✓ AFA Deep Research automation completed
  → Success: true
  → Search URL: https://gemini.google.com/app/abc123xyz...

[3/3] Saving results to TODOIT...
  → Status: in_progress
  ✓ Saved to TODOIT

========================================
✓ Workflow completed successfully
========================================
{
  "success": true,
  "source_name": "0055_of_mice_and_men",
  "gemini_afa_url": "https://gemini.google.com/app/abc123xyz",
  "status": "in_progress",
  "timestamp": "2025-10-23 12:34:56 UTC",
  "screenshot": "/tmp/gemini-deep-research-afa-*.png",
  "error": null
}
```
