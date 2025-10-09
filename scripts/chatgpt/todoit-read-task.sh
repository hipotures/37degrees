#!/bin/bash
# TODOIT CLI wrapper for reading next image generation task
# Usage: ./todoit-read-task.sh <list_key>
# Output: JSON with all needed data for image generation

set -e

LIST_KEY="$1"

if [ -z "$LIST_KEY" ]; then
  echo '{"error": "list_key parameter required"}' >&2
  exit 1
fi

# 1. Get book/media folder property
FOLDER_JSON=$(TODOIT_OUTPUT_FORMAT=json todoit list property get --list "$LIST_KEY" --key media_folder 2>/dev/null || \
              TODOIT_OUTPUT_FORMAT=json todoit list property get --list "$LIST_KEY" --key book_folder 2>/dev/null)

if [ -z "$FOLDER_JSON" ] || echo "$FOLDER_JSON" | grep -q "not found"; then
  echo '{"error": "book_folder/media_folder property not found"}' >&2
  exit 1
fi

BOOK_FOLDER=$(echo "$FOLDER_JSON" | jq -r '.data[0] | to_entries[0].value')

# 2. Get project_id (optional)
PROJECT_ID_JSON=$(TODOIT_OUTPUT_FORMAT=json todoit list property get --list "$LIST_KEY" --key project_id 2>/dev/null || echo "")
PROJECT_ID=$(echo "$PROJECT_ID_JSON" | jq -r '.data[0].project_id // empty' 2>/dev/null || echo "")

# 3. Find next ready task
TASK_OUTPUT=$(TODOIT_OUTPUT_FORMAT=json todoit item find-status --complex '{"scene_style": "completed", "image_gen": "pending"}' --list "$LIST_KEY" --limit 1 2>&1)

# Check if output is valid JSON
if ! echo "$TASK_OUTPUT" | jq empty 2>/dev/null; then
  # Not JSON - probably "No items found" message
  echo '{"ready": false, "message": "No tasks ready for image generation"}'
  exit 0
fi

TASK_COUNT=$(echo "$TASK_OUTPUT" | jq -r '.count // 0')

if [ "$TASK_COUNT" -eq 0 ]; then
  echo '{"ready": false, "message": "No tasks ready for image generation"}'
  exit 0
fi

# Extract parent key
SCENE_KEY=$(echo "$TASK_OUTPUT" | jq -r '.data[0]."Parent Key"')

# 4. Get YAML file path from scene_style subtask
YAML_PATH_JSON=$(TODOIT_OUTPUT_FORMAT=json todoit item property get --list "$LIST_KEY" --item "$SCENE_KEY" --subitem scene_style --key scene_style_pathfile 2>/dev/null)

if [ -z "$YAML_PATH_JSON" ] || echo "$YAML_PATH_JSON" | grep -q "not found"; then
  echo "{\"error\": \"scene_style_pathfile not found for $SCENE_KEY\"}" >&2
  exit 1
fi

YAML_PATH=$(echo "$YAML_PATH_JSON" | jq -r '.data[0].scene_style_pathfile')
YAML_FILENAME=$(basename "$YAML_PATH")

# Output all data as JSON
jq -n \
  --arg book_folder "$BOOK_FOLDER" \
  --arg project_id "$PROJECT_ID" \
  --arg scene_key "$SCENE_KEY" \
  --arg yaml_path "$YAML_PATH" \
  --arg yaml_filename "$YAML_FILENAME" \
  '{
    ready: true,
    book_folder: $book_folder,
    project_id: ($project_id | if . == "" then null else . end),
    scene_key: $scene_key,
    yaml_path: $yaml_path,
    yaml_filename: $yaml_filename
  }'
