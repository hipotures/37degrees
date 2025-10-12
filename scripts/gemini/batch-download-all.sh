#!/bin/bash
# Complete batch audio download with AI matching
# Usage: ./batch-download-all.sh [--model gemini|claude] [--resume-from phase2|phase3] [--work-dir /tmp/xxx]
# Env vars: DRY_RUN=true, MAX_DOWNLOADS=N

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# =============================================================================
# CONFIGURATION
# =============================================================================

# Default model (can be overridden with --model)
PRIMARY_MODEL="${PRIMARY_MODEL:-gemini}"

# Gemini-specific model
GEMINI_MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"
GEMINI_EXTRA_ARGS="${GEMINI_EXTRA_ARGS:---yolo --allowed-tools playwright-cdp,todoit}"

# Dry run mode (only matching, no downloads)
DRY_RUN="${DRY_RUN:-false}"

# Max downloads for testing (empty = all)
MAX_DOWNLOADS="${MAX_DOWNLOADS:-}"

# Rate limiting between downloads
DOWNLOAD_SLEEP=2

# Work directory (can be overridden with --work-dir for resume)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
WORK_DIR="${WORK_DIR:-/tmp/audio-batch-$TIMESTAMP}"

# Resume from phase (empty = start from beginning)
RESUME_FROM=""

# =============================================================================
# PARSE ARGUMENTS
# =============================================================================

while [[ $# -gt 0 ]]; do
  case $1 in
    --model)
      PRIMARY_MODEL="$2"
      shift 2
      ;;
    --resume-from)
      RESUME_FROM="$2"
      shift 2
      ;;
    --work-dir)
      WORK_DIR="$2"
      shift 2
      ;;
    --gemini-model)
      GEMINI_MODEL="$2"
      shift 2
      ;;
    --gemini-extra-args)
      GEMINI_EXTRA_ARGS="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--model gemini|claude] [--gemini-model <model_name>] [--gemini-extra-args <args>] [--resume-from phase2|phase3] [--work-dir /tmp/xxx]"
      exit 1
      ;;
  esac
done

# =============================================================================
# SETUP
# =============================================================================

mkdir -p "$WORK_DIR"

echo "========================================="
echo "Batch Audio Download with AI Matching"
echo "========================================="
echo "Work directory: $WORK_DIR"
echo "Primary model: $PRIMARY_MODEL"
echo "Dry run: $DRY_RUN"
if [ -n "$MAX_DOWNLOADS" ]; then
  echo "Max downloads: $MAX_DOWNLOADS"
fi
if [ -n "$RESUME_FROM" ]; then
  echo "Resume from: $RESUME_FROM"
fi
echo ""

# =============================================================================
# PHASE 1: AI Matching (NotebookLM titles → tasks)
# =============================================================================

if [ -z "$RESUME_FROM" ] || [ "$RESUME_FROM" = "phase1" ]; then
  # Disable set -e for Phase 1 to prevent silent failures
  set +e

  echo "=== PHASE 1: AI Matching (NotebookLM titles → tasks) ==="
  echo ""

  # Step 1.1: Get all pending download tasks
  echo "[1.1] Reading pending download tasks from TODOIT..."

  TASKS_JSON="$WORK_DIR/tasks.json"
  python "$SCRIPT_DIR/find_all_download_task.py" > "$TASKS_JSON" 2>/dev/null

  if [ $? -ne 0 ]; then
    echo "✗ Failed to read tasks from TODOIT"
    exit 1
  fi

  TASK_COUNT=$(jq '.data | length' "$TASKS_JSON" 2>/dev/null || echo "0")
  echo "  ✓ Found $TASK_COUNT pending tasks"

  if [ "$TASK_COUNT" = "0" ]; then
    echo "ℹ No pending download tasks found"
    exit 0
  fi

  echo ""

  # Step 1.2: Collect audio from all notebooks
  echo "[1.2] Collecting audio from all NotebookLM notebooks..."

  # Get unique notebook URLs from tasks (into array)
  echo "  → Loading notebook URLs from tasks..."
  mapfile -t NOTEBOOK_URLS < <(jq -r '[.data[].notebook_url] | unique | .[]' "$TASKS_JSON" 2>/dev/null)

  echo "  → Found ${#NOTEBOOK_URLS[@]} unique notebook(s)"

  if [ ${#NOTEBOOK_URLS[@]} -eq 0 ]; then
    echo "  ⚠ No notebook URLs found in tasks"
    exit 1
  fi

  echo ""

  ALL_AUDIO_JSON="$WORK_DIR/all_audio.json"
  echo "  → Initializing all_audio.json..."
  echo "[]" > "$ALL_AUDIO_JSON"

  NOTEBOOK_COUNT=0

  echo "  → Starting iteration over ${#NOTEBOOK_URLS[@]} notebook(s)..."
  echo ""

  # Iterate through notebook URLs
  for NOTEBOOK_URL in "${NOTEBOOK_URLS[@]}"; do
    NOTEBOOK_COUNT=$((NOTEBOOK_COUNT + 1))
    echo "  → Notebook $NOTEBOOK_COUNT/${#NOTEBOOK_URLS[@]}"
    echo "    URL: $NOTEBOOK_URL"
    echo "    Collecting audio (this may take 10-60s)..."

    # Run with timeout (max 60s)
    set +e
    AUDIO_RESULT=$(timeout 60 npx ts-node "$SCRIPT_DIR/collect-audio-list.ts" "$NOTEBOOK_URL" 2>&1)
    EXIT_CODE=$?
    set -e

    if [ $EXIT_CODE -eq 124 ]; then
      echo "    ⚠ Timeout (60s) - skipping this notebook"
      continue
    fi

    if [ $EXIT_CODE -eq 0 ]; then
      # Extract JSON from output (find last complete JSON object)
      AUDIO_JSON=$(echo "$AUDIO_RESULT" | awk '/^{/,0')
      AUDIO_COUNT=$(echo "$AUDIO_JSON" | jq '.audio | length' 2>/dev/null || echo "0")
      echo "    ✓ Found $AUDIO_COUNT audio items"

      # Append to all_audio.json
      jq -s '.[0] + [.[1]]' "$ALL_AUDIO_JSON" <(echo "$AUDIO_JSON") > "$ALL_AUDIO_JSON.tmp"
      mv "$ALL_AUDIO_JSON.tmp" "$ALL_AUDIO_JSON"
    else
      echo "    ⚠ Failed to collect audio from this notebook"
      echo "    Error: $(echo "$AUDIO_RESULT" | grep -E "(Error|✗)" | head -3)"
    fi
  done

  TOTAL_AUDIO=$(jq '[.[].audio | length] | add' "$ALL_AUDIO_JSON" 2>/dev/null || echo "0")
  echo "  ✓ Total audio collected: $TOTAL_AUDIO (from $NOTEBOOK_COUNT notebooks)"
  echo ""

  # Step 1.3: AI matching
  echo "[1.3] Calling AI for matching..."

  MATCHING_JSON="$WORK_DIR/matching.json"
  npx ts-node "$SCRIPT_DIR/match-with-ai.ts" \
    "$TASKS_JSON" \
    "$ALL_AUDIO_JSON" \
    --model "$PRIMARY_MODEL" \
    --gemini-model "$GEMINI_MODEL" \
    --gemini-extra-args "$GEMINI_EXTRA_ARGS" \
    2>&1 | tee "$WORK_DIR/match-with-ai.log" | grep -E "^\[|  [→✓⚠✗]"

  EXIT_CODE=$?

  if [ $EXIT_CODE -ne 0 ]; then
    echo "✗ AI matching failed"
    echo "See log: $WORK_DIR/match-with-ai.log"
    exit 1
  fi

  # Extract JSON from output (find last complete JSON object)
  awk '/^{/,0' "$WORK_DIR/match-with-ai.log" > "$MATCHING_JSON"

  MATCH_COUNT=$(jq '.matches | length' "$MATCHING_JSON" 2>/dev/null || echo "0")
  UNMATCHED_COUNT=$(jq '.unmatched_tasks | length' "$MATCHING_JSON" 2>/dev/null || echo "0")
  MODEL_USED=$(jq -r '.model_used' "$MATCHING_JSON" 2>/dev/null || echo "unknown")

  echo "  ✓ Matched $MATCH_COUNT audio files (model: $MODEL_USED)"

  if [ "$UNMATCHED_COUNT" -gt 0 ]; then
    echo "  ⚠ Unmatched tasks: $UNMATCHED_COUNT"
  fi

  echo ""

  # Re-enable set -e for subsequent phases
  set -e
fi

# =============================================================================
# PHASE 2: Batch Download (with timestamp tracking)
# =============================================================================

if [ -z "$RESUME_FROM" ] || [ "$RESUME_FROM" = "phase2" ]; then
  echo "=== PHASE 2: Batch Download ==="
  if [ "$DRY_RUN" = "true" ]; then
    echo "ℹ DRY_RUN mode: Downloads will proceed, TODOIT updates skipped"
  fi
  echo ""

  MATCHING_JSON="$WORK_DIR/matching.json"
  DOWNLOADS_JSON="$WORK_DIR/downloads.json"

  if [ ! -f "$MATCHING_JSON" ]; then
    echo "✗ Missing matching.json - run Phase 1 first"
    exit 1
  fi

  # Initialize downloads log
  echo "[]" > "$DOWNLOADS_JSON"

  # Get matches
  MATCHES=$(jq -c '.matches[]' "$MATCHING_JSON" 2>/dev/null)
  MATCH_COUNT=$(echo "$MATCHES" | wc -l)

  # Apply MAX_DOWNLOADS limit if set
  if [ -n "$MAX_DOWNLOADS" ]; then
    MATCHES=$(echo "$MATCHES" | head -n "$MAX_DOWNLOADS")
    MATCH_COUNT=$(echo "$MATCHES" | wc -l)
    echo "  ℹ Limited to $MATCH_COUNT downloads (MAX_DOWNLOADS=$MAX_DOWNLOADS)"
    echo ""
  fi

  echo "  → Total downloads: $MATCH_COUNT"
  echo ""

  DOWNLOAD_INDEX=0

  echo "DEBUG: About to pipe matches to wc."
  echo "$MATCHES" | wc -l
  echo "DEBUG: Pipe to wc successful. Starting while loop."

  echo "$MATCHES" | while IFS= read -r match; do
    set +e

    BOOK_KEY=$(echo "$match" | jq -r '.book_key')
    LANG=$(echo "$match" | jq -r '.language_code')
    AUDIO_TITLE=$(echo "$match" | jq -r '.audio_title' | head -c 50)

    echo "[$DOWNLOAD_INDEX/$MATCH_COUNT] Downloading: $BOOK_KEY ($LANG)"
    echo "  → Audio: $AUDIO_TITLE..."

    # Download with timestamp tracking
    DOWNLOAD_RESULT=$(echo "$match" | npx ts-node "$SCRIPT_DIR/download-single-audio.ts" --stdin 2>&1)
    EXIT_CODE=$?

    # Extract JSON from output (find last complete JSON object)
    DOWNLOAD_JSON=$(echo "$DOWNLOAD_RESULT" | awk '/^{/,0')

    # Append to downloads.json
    jq -s '.[0] + [.[1]]' "$DOWNLOADS_JSON" <(echo "$DOWNLOAD_JSON") > "$DOWNLOADS_JSON.tmp"
    mv "$DOWNLOADS_JSON.tmp" "$DOWNLOADS_JSON"

    if [ $EXIT_CODE -eq 0 ]; then
      FILE_PATH=$(echo "$DOWNLOAD_JSON" | jq -r '.file_path')
      FILENAME=$(basename "$FILE_PATH")
      echo "  ✓ Downloaded: $FILENAME"
    else
      ERROR=$(echo "$DOWNLOAD_JSON" | jq -r '.error' | head -c 100)
      echo "  ✗ Failed: $ERROR"
    fi

    # Rate limiting
    if [ $DOWNLOAD_INDEX -lt $MATCH_COUNT ]; then
      echo "  → Sleeping ${DOWNLOAD_SLEEP}s..."
      sleep $DOWNLOAD_SLEEP
    fi

    echo ""
    set -e
  done

  SUCCESSFUL_COUNT=$(jq '[.[] | select(.success == true)] | length' "$DOWNLOADS_JSON")
  echo "  ✓ Phase 2 completed: $SUCCESSFUL_COUNT successful downloads"
  echo ""
fi

# =============================================================================
# PHASE 3: AI File Matching (files → tasks)
# =============================================================================

if [ -z "$RESUME_FROM" ] || [ "$RESUME_FROM" = "phase2" ] || [ "$RESUME_FROM" = "phase3" ]; then
  echo "=== PHASE 3: AI File Matching (files → tasks) ==="
  echo ""

  DOWNLOADS_JSON="$WORK_DIR/downloads.json"
  MATCHING_JSON="$WORK_DIR/matching.json"
  FILE_MAPPING_JSON="$WORK_DIR/file-mapping.json"

  if [ ! -f "$DOWNLOADS_JSON" ]; then
    echo "✗ Missing downloads.json - run Phase 2 first"
    exit 1
  fi

  if [ ! -f "$MATCHING_JSON" ]; then
    echo "✗ Missing matching.json - run Phase 1 first"
    exit 1
  fi

  echo "[3.1] Calling AI for file matching..."

  npx ts-node "$SCRIPT_DIR/match-files-ai.ts" \
    "$DOWNLOADS_JSON" \
    "$MATCHING_JSON" \
    --model "$PRIMARY_MODEL" \
    --gemini-model "$GEMINI_MODEL" \
    --gemini-extra-args "$GEMINI_EXTRA_ARGS" \
    2>&1 | tee "$WORK_DIR/match-files-ai.log" | grep -E "^\[|  [→✓⚠✗]"

  EXIT_CODE=$?

  if [ $EXIT_CODE -ne 0 ]; then
    echo "✗ AI file matching failed"
    echo "See log: $WORK_DIR/match-files-ai.log"
    exit 1
  fi

  # Extract JSON from output (find last complete JSON object)
  awk '/^{/,0' "$WORK_DIR/match-files-ai.log" > "$FILE_MAPPING_JSON"

  MAPPING_COUNT=$(jq '.mappings | length' "$FILE_MAPPING_JSON" 2>/dev/null || echo "0")
  MODEL_USED=$(jq -r '.model_used' "$FILE_MAPPING_JSON" 2>/dev/null || echo "unknown")

  echo "  ✓ Found $MAPPING_COUNT file mappings (model: $MODEL_USED)"
  echo ""
fi

# =============================================================================
# PHASE 4: Execute Moves + Update TODOIT
# =============================================================================

echo "=== PHASE 4: Execute Moves + Update TODOIT ==="
if [ "$DRY_RUN" = "true" ]; then
  echo "ℹ DRY_RUN mode: No overwrite if file exists, TODOIT updates skipped"
fi
echo ""

FILE_MAPPING_JSON="$WORK_DIR/file-mapping.json"
MOVES_SCRIPT="$WORK_DIR/moves.sh"

if [ ! -f "$FILE_MAPPING_JSON" ]; then
  echo "✗ Missing file-mapping.json - run Phase 3 first"
  exit 1
fi

# Generate moves.sh script
echo "#!/bin/bash" > "$MOVES_SCRIPT"
echo "# Auto-generated move commands" >> "$MOVES_SCRIPT"
if [ "$DRY_RUN" = "true" ]; then
  echo "# DRY_RUN mode: Using 'mv -n' (no overwrite)" >> "$MOVES_SCRIPT"
fi
echo "set -e" >> "$MOVES_SCRIPT"
echo "" >> "$MOVES_SCRIPT"

MAPPINGS=$(jq -c '.mappings[]' "$FILE_MAPPING_JSON" 2>/dev/null)
MAPPING_COUNT=$(echo "$MAPPINGS" | wc -l)

echo "[4.1] Generating move script..."
echo "  → Mappings: $MAPPING_COUNT"

while IFS= read -r mapping; do
  SRC=$(echo "$mapping" | jq -r '.source_file')
  DEST=$(echo "$mapping" | jq -r '.target_path')

  # Add move command to script
  if [ "$DRY_RUN" = "true" ]; then
    # DRY_RUN: Check if file exists before moving
    echo "if [ ! -f \"$DEST\" ]; then mv \"$SRC\" \"$DEST\"; else echo \"Skipped (exists): $DEST\"; fi" >> "$MOVES_SCRIPT"
  else
    # Normal mode: Always move (overwrite)
    echo "mv \"$SRC\" \"$DEST\"" >> "$MOVES_SCRIPT"
  fi
done <<< "$MAPPINGS"

chmod +x "$MOVES_SCRIPT"

echo "  ✓ Move script generated: $MOVES_SCRIPT"
echo ""

echo "[4.2] Executing moves..."

MOVE_INDEX=0
while IFS= read -r mapping; do
  MOVE_INDEX=$((MOVE_INDEX + 1))

  SRC=$(echo "$mapping" | jq -r '.source_file')
  DEST=$(echo "$mapping" | jq -r '.target_path')
  BOOK_KEY=$(echo "$mapping" | jq -r '.book_key')
  LANG=$(echo "$mapping" | jq -r '.language_code')

  DEST_DIR=$(dirname "$DEST")

  echo "[$MOVE_INDEX/$MAPPING_COUNT] Moving: $BOOK_KEY ($LANG)"
  echo "  → From: $(basename "$SRC")"
  echo "  → To: $DEST"

  # Create target directory if needed
  if [ ! -d "$DEST_DIR" ]; then
    echo "  ⚠ Creating directory: $DEST_DIR"
    mkdir -p "$DEST_DIR"
  fi

  # Move file
  if [ -f "$SRC" ]; then
    # Check if destination exists
    if [ -f "$DEST" ]; then
      if [ "$DRY_RUN" = "true" ]; then
        echo "  ⚠ Destination exists - skipping move (DRY_RUN)"
        echo "  ℹ File: $DEST"
      else
        echo "  ⚠ Destination exists - overwriting"
        mv "$SRC" "$DEST"

        if [ -f "$DEST" ]; then
          echo "  ✓ Moved successfully (overwritten)"
        else
          echo "  ✗ Move failed"
        fi
      fi
    else
      # Destination doesn't exist - safe to move
      mv "$SRC" "$DEST"

      if [ -f "$DEST" ]; then
        echo "  ✓ Moved successfully"
      else
        echo "  ✗ Move failed"
      fi
    fi

    # Update TODOIT only if NOT in dry run mode
    if [ "$DRY_RUN" != "true" ] && [ -f "$DEST" ]; then
      SUBITEM="audio_dwn_$LANG"
      echo "  → Updating TODOIT..."

      "$SCRIPT_DIR/todoit-write-download-result.sh" \
        "$BOOK_KEY" "$SUBITEM" "completed" "$DEST" \
        > /dev/null 2>&1

      if [ $? -eq 0 ]; then
        echo "  ✓ TODOIT updated"
      else
        echo "  ⚠ TODOIT update failed (file moved successfully)"
      fi
    elif [ "$DRY_RUN" = "true" ]; then
      echo "  ℹ TODOIT update skipped (DRY_RUN)"
    fi
  else
    echo "  ✗ Source file not found: $SRC"
  fi

  echo ""
done <<< "$MAPPINGS"

# =============================================================================
# SUMMARY
# =============================================================================

echo "========================================="
if [ "$DRY_RUN" = "true" ]; then
  echo "Batch Download Completed (DRY RUN)"
else
  echo "Batch Download Completed"
fi
echo "========================================="
echo ""
echo "Work directory: $WORK_DIR"
echo ""
echo "Files generated:"
echo "  - tasks.json: Pending download tasks"
echo "  - all_audio.json: Audio collected from NotebookLM"
echo "  - matching.json: AI matching (titles → tasks)"
echo "  - downloads.json: Download log with timestamps"
echo "  - file-mapping.json: AI matching (files → tasks)"
echo "  - moves.sh: Generated move commands"
echo "  - *.log: Execution logs"
echo ""

if [ -f "$FILE_MAPPING_JSON" ]; then
  MAPPED_COUNT=$(jq '.mappings | length' "$FILE_MAPPING_JSON")
  echo "Total audio processed: $MAPPED_COUNT"
fi

echo ""

if [ "$DRY_RUN" = "true" ]; then
  echo "ℹ DRY RUN mode:"
  echo "  ✓ Audio downloaded from NotebookLM"
  echo "  ✓ AI matching performed"
  echo "  ✓ Files moved (no overwrite if exists)"
  echo "  ✗ TODOIT status NOT updated"
  echo ""
fi

echo "ℹ Work directory NOT cleaned up (in /tmp, will auto-cleanup)"
echo ""
