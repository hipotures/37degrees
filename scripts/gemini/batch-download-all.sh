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

  # Step 1.2: Collect audio from mcptools browser snapshot
  echo "[1.2] Collecting audio from browser snapshot (mcptools)..."

  # Browser endpoint (default: localhost:8931)
  BROWSER_ENDPOINT="${BROWSER_ENDPOINT:-http://127.0.0.1:8931/sse}"
  echo "  → Browser endpoint: $BROWSER_ENDPOINT"

  ALL_AUDIO_JSON="$WORK_DIR/all_audio.json"
  echo "  → Initializing all_audio.json..."
  echo "[]" > "$ALL_AUDIO_JSON"

  # Run with timeout (max 30s)
  set +e
  AUDIO_RESULT_OUTPUT=$(timeout 30 npx ts-node "$SCRIPT_DIR/collect-audio-snapshot.ts" "$WORK_DIR" "$BROWSER_ENDPOINT" 2>&1)
  EXIT_CODE=$?
  set -e

  if [ $EXIT_CODE -eq 124 ]; then
    echo "  ⚠ Timeout (30s) - browser snapshot collection failed"
    exit 1
  fi

  if [ $EXIT_CODE -eq 0 ]; then
    # The result is now a path to a JSON file
    AUDIO_JSON_PATH=$(echo "$AUDIO_RESULT_OUTPUT" | tail -n 1)

    if [ ! -f "$AUDIO_JSON_PATH" ]; then
      echo "  ⚠ Script succeeded but output file path was not found: $AUDIO_JSON_PATH"
      echo "  → Full output: $AUDIO_RESULT_OUTPUT"
      exit 1
    fi

    AUDIO_COUNT=$(jq '.audio | length' "$AUDIO_JSON_PATH" 2>/dev/null || echo "0")
    echo "  ✓ Found $AUDIO_COUNT audio items from snapshot"

    # Use the snapshot directly as all_audio
    cp "$AUDIO_JSON_PATH" "$ALL_AUDIO_JSON"
    echo ""
  else
    echo "  ✗ Failed to collect audio from browser snapshot"
    echo "  Error: $(echo "$AUDIO_RESULT_OUTPUT" | grep -E "(Error|✗)" | head -3)"
    exit 1
  fi

  TOTAL_AUDIO=$(jq '.audio | length' "$ALL_AUDIO_JSON" 2>/dev/null || echo "0")
  echo "  ✓ Total audio collected: $TOTAL_AUDIO"
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

  TOTAL_MATCH_COUNT=$(jq '.matches | length' "$MATCHING_JSON" 2>/dev/null || echo "0")
  MATCH_COUNT=$TOTAL_MATCH_COUNT
  MATCH_QUERY=".matches[]"

  if [ -n "$MAX_DOWNLOADS" ] && [ "$MAX_DOWNLOADS" -lt "$MATCH_COUNT" ]; then
    MATCH_COUNT="$MAX_DOWNLOADS"
    MATCH_QUERY=".matches[:$MAX_DOWNLOADS][]"
    echo "  ℹ Limited to $MATCH_COUNT downloads (MAX_DOWNLOADS=$MAX_DOWNLOADS)"
    echo ""
  fi

  echo "  → Total downloads: $MATCH_COUNT"
  echo ""

  if [ "$MATCH_COUNT" -gt 0 ]; then
    DOWNLOAD_INDEX=0

    while IFS= read -r match; do
      DOWNLOAD_INDEX=$((DOWNLOAD_INDEX + 1))
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
        ERROR=$(echo "$DOWNLOAD_JSON" | jq -r '.error // "Unknown error"' | head -c 100)
        echo "  ✗ Failed: $ERROR"

        if [ "$DRY_RUN" != "true" ]; then
          SUBITEM="audio_dwn_$LANG"
          echo "  → Marking TODOIT as failed..."

          set +e
          TODOIT_OUTPUT=$("$SCRIPT_DIR/todoit-write-download-result.sh" \
            "$BOOK_KEY" "$SUBITEM" "failed" "" "$ERROR" 2>&1)
          TODOIT_EXIT=$?
          set -e

          if [ $TODOIT_EXIT -ne 0 ]; then
            echo "    Debug: $TODOIT_OUTPUT"
          fi

          if [ $TODOIT_EXIT -eq 0 ]; then
            echo "  ✓ TODOIT updated (failed)"
          else
            echo "  ⚠ TODOIT update failed (download failure logged locally)"
          fi
        fi
      fi

      # Rate limiting
      if [ $DOWNLOAD_INDEX -lt $MATCH_COUNT ]; then
        echo "  → Sleeping ${DOWNLOAD_SLEEP}s..."
        sleep $DOWNLOAD_SLEEP
      fi

      echo ""
      set -e
    done < <(jq -c "$MATCH_QUERY" "$MATCHING_JSON")
  fi

  SUCCESSFUL_COUNT=$(jq '[.[] | select(.success == true)] | length' "$DOWNLOADS_JSON")
  echo "  ✓ Phase 2 completed: $SUCCESSFUL_COUNT successful downloads"
  echo ""
fi

# =============================================================================
# PHASE 3: Build File Mapping (direct from directory naming - no AI needed)
# =============================================================================

if [ -z "$RESUME_FROM" ] || [ "$RESUME_FROM" = "phase2" ] || [ "$RESUME_FROM" = "phase3" ]; then
  echo "=== PHASE 3: Build File Mapping (from directory structure) ==="
  echo ""

  DOWNLOADS_JSON="$WORK_DIR/downloads.json"
  FILE_MAPPING_JSON="$WORK_DIR/file-mapping.json"

  if [ ! -f "$DOWNLOADS_JSON" ]; then
    echo "✗ Missing downloads.json - run Phase 2 first"
    exit 1
  fi

  echo "[3.1] Building file mapping from directory structure..."

  # Build mappings directly from downloads.json
  # Directory structure is: /tmp/playwright-mcp-output/[book_key]_[lang]/filename
  # So we can extract book_key and lang from the directory name

  MAPPINGS_ARRAY="[]"

  while IFS= read -r line; do
    SUCCESS=$(echo "$line" | jq -r '.success')
    FILE_PATH=$(echo "$line" | jq -r '.file_path')

    if [ "$SUCCESS" = "true" ] && [ -n "$FILE_PATH" ] && [ "$FILE_PATH" != "null" ]; then
      # Extract book_key and language_code from path
      # Path format: /tmp/playwright-mcp-output/[book_key]_[lang]/filename
      DIR_NAME=$(basename "$(dirname "$FILE_PATH")")

      # Split dir name by last underscore to get book_key and lang
      LANG="${DIR_NAME##*_}"
      BOOK_KEY="${DIR_NAME%_*}"

      # Build target path
      EXT="${FILE_PATH##*.}"
      TARGET_PATH="books/$BOOK_KEY/audio/${BOOK_KEY}_${LANG}.${EXT}"

      # Build mapping object
      MAPPING="{\"source_file\": \"$FILE_PATH\", \"book_key\": \"$BOOK_KEY\", \"language_code\": \"$LANG\", \"target_path\": \"$TARGET_PATH\"}"

      # Append to array
      MAPPINGS_ARRAY=$(echo "$MAPPINGS_ARRAY" | jq --argjson new "$MAPPING" '. += [$new]')
    fi
  done < <(jq -c '.[]' "$DOWNLOADS_JSON")

  # Save mappings to file
  echo "{\"success\": true, \"mappings\": $MAPPINGS_ARRAY}" > "$FILE_MAPPING_JSON"

  MAPPING_COUNT=$(jq '.mappings | length' "$FILE_MAPPING_JSON" 2>/dev/null || echo "0")
  echo "  ✓ Built $MAPPING_COUNT file mappings (direct from directory structure)"
  echo ""
fi

# =============================================================================
# PHASE 4: Execute Moves + Update TODOIT
# =============================================================================

if [ -z "$RESUME_FROM" ] || [ "$RESUME_FROM" = "phase3" ] || [ "$RESUME_FROM" = "phase4" ]; then
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

MAPPING_COUNT=$(jq '.mappings | length' "$FILE_MAPPING_JSON" 2>/dev/null || echo "0")

echo "[4.1] Generating move script..."
echo "  → Mappings: $MAPPING_COUNT"

if [ "$MAPPING_COUNT" -gt 0 ]; then
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
  done < <(jq -c '.mappings[]' "$FILE_MAPPING_JSON")
fi

chmod +x "$MOVES_SCRIPT"

echo "  ✓ Move script generated: $MOVES_SCRIPT"
echo ""

echo "[4.2] Executing moves..."

MOVE_INDEX=0
if [ "$MAPPING_COUNT" -gt 0 ]; then
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

        set +e  # Don't exit if TODOIT update fails
        TODOIT_OUTPUT=$("$SCRIPT_DIR/todoit-write-download-result.sh" \
          "$BOOK_KEY" "$SUBITEM" "completed" "$DEST" 2>&1)
        TODOIT_EXIT=$?
        set -e  # Re-enable error exit

        if [ $TODOIT_EXIT -ne 0 ]; then
          echo "    Debug: $TODOIT_OUTPUT"
        fi

        if [ $TODOIT_EXIT -eq 0 ]; then
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
  done < <(jq -c '.mappings[]' "$FILE_MAPPING_JSON")
fi

fi

# =============================================================================
# PHASE 4.5: Verify Deletion Safety (run can_delete_file.sh immediately)
# =============================================================================

if [ -z "$RESUME_FROM" ] || [ "$RESUME_FROM" = "phase4" ] || [ "$RESUME_FROM" = "phase4.5" ]; then
  echo "=== PHASE 4.5: Verify Deletion Safety ==="
  if [ "$DRY_RUN" = "true" ]; then
    echo "ℹ DRY_RUN mode: Safety check skipped"
    echo ""
  else
    echo "[4.5.1] Checking deletion safety for each file..."
    echo ""

    FILE_MAPPING_JSON="$WORK_DIR/file-mapping.json"
    UPDATED_MAPPINGS="[]"

    VERIFICATION_INDEX=0
    while IFS= read -r mapping; do
      VERIFICATION_INDEX=$((VERIFICATION_INDEX + 1))

      BOOK_KEY=$(echo "$mapping" | jq -r '.book_key')
      LANG=$(echo "$mapping" | jq -r '.language_code')
      NOTEBOOK_DELETED=$(echo "$mapping" | jq -r '.notebook_deleted // false')

      if [ "$NOTEBOOK_DELETED" = "true" ]; then
        UPDATED_MAPPING="$mapping"
        UPDATED_MAPPINGS=$(echo "$UPDATED_MAPPINGS" | jq --argjson new "$UPDATED_MAPPING" '. += [$new]')
        echo "[$VERIFICATION_INDEX] ℹ $BOOK_KEY ($LANG) - Already deleted, skipping safety check"
        continue
      fi

      DEST=$(echo "$mapping" | jq -r '.target_path')

      # Run can_delete_file.sh immediately while file is fresh (< 5 min)
      DELETION_CHECK=$(bash "$SCRIPT_DIR/../internal/can_delete_file.sh" "$DEST" 2>&1)
      DELETION_CHECK_TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

      # Add deletion_check to mapping
      UPDATED_MAPPING=$(echo "$mapping" | jq \
        --arg check "$DELETION_CHECK" \
        --arg timestamp "$DELETION_CHECK_TIMESTAMP" \
        '. += {deletion_check: $check, deletion_check_time: $timestamp}')

      # Append to updated array
      UPDATED_MAPPINGS=$(echo "$UPDATED_MAPPINGS" | jq --argjson new "$UPDATED_MAPPING" '. += [$new]')

      # Show status
      if [ "$DELETION_CHECK" = "CAN_DELETE_FROM_NOTEBOOK" ]; then
        echo "[$VERIFICATION_INDEX] ✓ $BOOK_KEY ($LANG) - Can delete"
      else
        REASON=$(echo "$DELETION_CHECK" | cut -d':' -f2 | cut -c1-50)
        echo "[$VERIFICATION_INDEX] ⚠ $BOOK_KEY ($LANG) - Cannot delete: $REASON"
      fi
    done < <(jq -c '.mappings[]' "$FILE_MAPPING_JSON")

    # Save updated mappings back to file
    echo "{\"success\": true, \"mappings\": $UPDATED_MAPPINGS}" > "$FILE_MAPPING_JSON"

    echo ""
    echo "  ✓ Phase 4.5 completed: All files verified"
    echo ""
  fi
fi

# =============================================================================
# PHASE 5: Delete Audio from NotebookLM (Safe deletion after verification)
# =============================================================================

if [ -z "$RESUME_FROM" ] || [ "$RESUME_FROM" = "phase4" ] || [ "$RESUME_FROM" = "phase4.5" ] || [ "$RESUME_FROM" = "phase5" ]; then
  echo "=== PHASE 5: Delete Audio from NotebookLM ==="
  if [ "$DRY_RUN" = "true" ]; then
    echo "ℹ DRY_RUN mode: Deletion skipped"
    echo ""
  else
    echo ""

    FILE_MAPPING_JSON="$WORK_DIR/file-mapping.json"
    MATCHING_JSON="$WORK_DIR/matching.json"
    DELETIONS_JSON="$WORK_DIR/deletions.json"

    if [ ! -f "$FILE_MAPPING_JSON" ] || [ ! -f "$MATCHING_JSON" ]; then
      echo "⚠ Skipping Phase 5: Missing mapping or matching data"
      echo ""
    else
      echo "[5.1] Deleting audio from NotebookLM..."

      # Initialize deletions log (preserve previous entries if present)
      if [ ! -f "$DELETIONS_JSON" ]; then
        echo "[]" > "$DELETIONS_JSON"
      fi

      DELETION_INDEX=0
      MAPPINGS=$(jq -c '.mappings[]' "$FILE_MAPPING_JSON" 2>/dev/null)
      MAPPING_COUNT=$(echo "$MAPPINGS" | wc -l)

      while IFS= read -r mapping; do
        DELETION_INDEX=$((DELETION_INDEX + 1))

        BOOK_KEY=$(echo "$mapping" | jq -r '.book_key')
        LANG=$(echo "$mapping" | jq -r '.language_code')

        # Find matching audio info (title, url) from matching.json
        MATCH_INFO=$(jq -c ".matches[] | select(.book_key == \"$BOOK_KEY\" and .language_code == \"$LANG\") | {audio_title, notebook_url}" "$MATCHING_JSON" 2>/dev/null | head -1)

        if [ -z "$MATCH_INFO" ] || [ "$MATCH_INFO" = "null" ]; then
          echo "[$DELETION_INDEX/$MAPPING_COUNT] Skipping: $BOOK_KEY ($LANG) - no match found"
          continue
        fi

        AUDIO_TITLE=$(echo "$MATCH_INFO" | jq -r '.audio_title')
        NOTEBOOK_URL=$(echo "$MATCH_INFO" | jq -r '.notebook_url')

        # Check deletion safety result from Phase 4.5
        DELETION_CHECK=$(echo "$mapping" | jq -r '.deletion_check // "NOT_CHECKED"')
        NOTEBOOK_DELETED=$(echo "$mapping" | jq -r '.notebook_deleted // false')

        if [ "$NOTEBOOK_DELETED" = "true" ]; then
          echo "[$DELETION_INDEX/$MAPPING_COUNT] Skipping: $BOOK_KEY ($LANG) - already deleted"
          continue
        fi

        if [ "$DELETION_CHECK" != "CAN_DELETE_FROM_NOTEBOOK" ]; then
          continue
        fi

        echo "[$DELETION_INDEX/$MAPPING_COUNT] Deleting: $BOOK_KEY ($LANG)"
        echo "  → Audio: ${AUDIO_TITLE:0:60}..."

        # Call delete script
        DELETE_PAYLOAD=$(jq -n --arg book "$BOOK_KEY" --arg lang "$LANG" --arg title "$AUDIO_TITLE" --arg url "$NOTEBOOK_URL" \
          '{book_key: $book, language_code: $lang, audio_title: $title, notebook_url: $url}')
        DELETE_RESULT=$(echo "$DELETE_PAYLOAD" | npx ts-node "$SCRIPT_DIR/delete-audio-from-notebooklm.ts" --stdin 2>&1)
        EXIT_CODE=$?

        # Extract JSON from output
        DELETE_JSON=$(echo "$DELETE_RESULT" | awk '/^{/,0')

        # Append to deletions.json
        jq -s '.[0] + [.[1]]' "$DELETIONS_JSON" <(echo "$DELETE_JSON") > "$DELETIONS_JSON.tmp"
        mv "$DELETIONS_JSON.tmp" "$DELETIONS_JSON"

        if [ $EXIT_CODE -eq 0 ]; then
          echo "  ✓ Deleted from NotebookLM"
          jq --arg book "$BOOK_KEY" --arg lang "$LANG" '
            .mappings = (.mappings | map(
              if .book_key == $book and .language_code == $lang
                then . + {notebook_deleted: true, deletion_check: "DELETED"}
                else .
              end
            ))
          ' "$FILE_MAPPING_JSON" > "$FILE_MAPPING_JSON.tmp"
          mv "$FILE_MAPPING_JSON.tmp" "$FILE_MAPPING_JSON"
        else
          ERROR=$(echo "$DELETE_JSON" | jq -r '.error' | head -c 100)
          if echo "$ERROR" | grep -qi "Audio not found"; then
            echo "  ✓ Already deleted in NotebookLM"
            jq --arg book "$BOOK_KEY" --arg lang "$LANG" '
              .mappings = (.mappings | map(
                if .book_key == $book and .language_code == $lang
                  then . + {notebook_deleted: true, deletion_check: "DELETED"}
                  else .
                end
              ))
            ' "$FILE_MAPPING_JSON" > "$FILE_MAPPING_JSON.tmp"
            mv "$FILE_MAPPING_JSON.tmp" "$FILE_MAPPING_JSON"
          else
            echo "  ⚠ Delete failed: $ERROR"
          fi
        fi

        echo ""
      done <<< "$MAPPINGS"

      SUCCESSFUL_DELETIONS=$(jq '[.[] | select(.success == true)] | length' "$DELETIONS_JSON")
      echo "  ✓ Phase 5 completed: $SUCCESSFUL_DELETIONS deletions"
      echo ""
    fi
  fi
fi

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

# =============================================================================
# CLEANUP: Remove empty download directories
# =============================================================================

echo "Cleaning up empty directories from /tmp/playwright-mcp-output/..."
rmdir /tmp/playwright-mcp-output/* 2>/dev/null || true
echo "✓ Cleanup completed"
echo ""
