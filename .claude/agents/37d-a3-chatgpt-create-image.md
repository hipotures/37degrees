---
name: 37d-a3-chatgpt-create-image
description: |
  Subagent worker for AI image generation in ChatGPT using TODOIT CLI wrapper scripts.
  Processes image_gen subtasks by finding scenes where scene_style is completed but image_gen is pending.
  Uses simple bash wrapper scripts (todoit-read-task.sh, todoit-write-result.sh) for minimal token usage.
execution_order: 3
min_tasks: 1
max_tasks: 1
todo_list: true
---

# Subagent: 37d-a3 - AI Image Generation Worker (CLI Scripts + Playwright)

Worker subagent dla pojedynczego zadania generowania obrazu w ChatGPT.

**KLUCZOWA OPTYMALIZACJA:** Używa wrapper bash scripts zamiast bezpośrednich wywołań TODOIT CLI!
**KORZYŚCI:** Znacznie mniej tokenów (1-2 wywołania zamiast 7-9), prostszy kod, szybsze wykonanie.

## Dane wejściowe z promptu wywołania:

- TODOIT_LIST: "[LIST_KEY]" (np. "m00062_cointelpro_revelation_1971")

## Kroki worker subagenta:

Zrealizuj wszystkie poniższe 3 fazy jedna po drugiej, starannie.

### Faza 1. Odczyt zadania z TODOIT

**Wywołaj wrapper script który zwraca wszystkie potrzebne dane w jednym JSON:**

```bash
scripts/chatgpt/todoit-read-task.sh [TODOIT_LIST]
```

**Output JSON:**
```json
{
  "ready": true,
  "book_folder": "m00062_cointelpro_revelation_1971",
  "project_id": "g-p-68dd127ca5e88191ba5a5970c74b2e3e",
  "scene_key": "scene_0005",
  "yaml_path": "media/m00062_cointelpro_revelation_1971/prompts/genimage/scene_0005.yaml",
  "yaml_filename": "scene_0005.yaml"
}
```

**Lub gdy brak zadań:**
```json
{
  "ready": false,
  "message": "No tasks ready for image generation"
}
```

**Wykonaj:**
```javascript
const result = Bash({
  command: `scripts/chatgpt/todoit-read-task.sh [TODOIT_LIST]`,
  timeout: 30000
});

// Parse JSON
const taskData = JSON.parse(result.stdout);

if (!taskData.ready) {
  console.log("No image_gen tasks ready for processing");
  return;
}

console.log(`Processing ${taskData.scene_key} for image generation`);
console.log(`Book folder: ${taskData.book_folder}`);
console.log(`YAML file: ${taskData.yaml_filename}`);
if (taskData.project_id) {
  console.log(`Project ID: ${taskData.project_id}`);
}
```

### Faza 2. Uruchom standalone Playwright script

**Wywołaj standalone TypeScript script z parametrami:**

```bash
npx ts-node scripts/chatgpt/upload-scene.ts <book_folder> <yaml_filename> [project_id]
```

**Wykonaj:**
```javascript
// Construct command
let cmd = `npx ts-node scripts/chatgpt/upload-scene.ts ${taskData.book_folder} ${taskData.yaml_filename}`;

if (taskData.project_id) {
  cmd += ` ${taskData.project_id}`;
}

console.log(`Running: ${cmd}`);

// Execute Playwright script (timeout 3 minutes)
const uploadResult = Bash({
  command: cmd,
  timeout: 180000
});

// Parse JSON output from stdout
const jsonMatch = uploadResult.stdout.match(/\{[\s\S]*"success"[\s\S]*\}/);
if (!jsonMatch) {
  console.log("ERROR: Could not parse JSON output from Playwright script");
  console.log("Output:", uploadResult.stdout);
  return;
}

const scriptResult = JSON.parse(jsonMatch[0]);

console.log(`Script result: ${scriptResult.success ? 'SUCCESS' : 'FAILED'}`);
if (scriptResult.threadId) {
  console.log(`Thread ID: ${scriptResult.threadId}`);
}
if (scriptResult.projectId) {
  console.log(`Project ID: ${scriptResult.projectId}`);
}
if (scriptResult.error) {
  console.log(`Error: ${scriptResult.error.substring(0, 200)}...`);
  console.log(`Error type: ${scriptResult.errorType}`);
}
```

**Script zwraca JSON:**

**Sukces:**
```json
{
  "success": true,
  "threadId": "68e7cc28-4140-8329-af5c-2b67193e69ce",
  "projectId": "g-p-68dd127ca5e88191ba5a5970c74b2e3e-m00062-cointelpro-revelation-1971",
  "sceneKey": "scene_0005"
}
```

**Błąd (Content Policy):**
```json
{
  "success": false,
  "threadId": "abc123",
  "error": "I can't create that image as it violates our content policies...",
  "errorType": "policy"
}
```

**Błąd (ChatGPT Plus Limit):**
```json
{
  "success": false,
  "threadId": "abc123",
  "error": "You've hit the plus plan limit. Your limit will reset at 3:00 PM.",
  "errorType": "limit"
}
```

### Faza 3. Zapisz wynik w TODOIT

**Wywołaj wrapper script który zapisze wszystkie dane w jednym wywołaniu:**

```bash
scripts/chatgpt/todoit-write-result.sh <list_key> <scene_key> <thread_id> <status> [project_id] [error_message]
```

**Parametry:**
- `list_key`: TODOIT list key (np. "m00062_cointelpro_revelation_1971")
- `scene_key`: Scene key (np. "scene_0005")
- `thread_id`: ChatGPT thread ID (zawsze wymagany)
- `status`: "completed", "failed", lub "pending" (dla ChatGPT limit)
- `project_id`: (optional) Nowy project ID jeśli został utworzony
- `error_message`: (optional) Error message jeśli wystąpił

**Wykonaj:**
```javascript
// Determine status based on result
let status;
let errorMessage = '';

if (scriptResult.success) {
  status = 'completed';
} else {
  if (scriptResult.errorType === 'limit') {
    // ChatGPT Plus limit - KEEP as pending for retry
    status = 'pending';
    errorMessage = scriptResult.error || '';
    console.log(`⚠ ChatGPT Plus limit detected. Keeping task as pending for retry.`);
  } else {
    // Other errors (policy, unknown) - mark as failed
    status = 'failed';
    errorMessage = scriptResult.error || '';
    console.log(`✗ Task failed. Error type: ${scriptResult.errorType}`);
  }
}

// Construct write command
let writeCmd = `scripts/chatgpt/todoit-write-result.sh "[TODOIT_LIST]" "${taskData.scene_key}" "${scriptResult.threadId}" "${status}"`;

// Add project_id if this was a new project
if (scriptResult.projectId && !taskData.project_id) {
  writeCmd += ` "${scriptResult.projectId}"`;
} else {
  writeCmd += ` ""`;  // Empty string for project_id
}

// Add error message if present
if (errorMessage) {
  // Escape quotes in error message
  const escapedError = errorMessage.replace(/"/g, '\\"');
  writeCmd += ` "${escapedError}"`;
}

console.log(`Saving results to TODOIT...`);

// Execute write script
const writeResult = Bash({
  command: writeCmd,
  timeout: 30000
});

// Parse result
const writeData = JSON.parse(writeResult.stdout);

if (writeData.success) {
  console.log(`✓ All data saved successfully`);
  console.log(`✓ ${taskData.scene_key} image_gen ${status}`);
} else {
  console.log(`✗ Failed to save some data:`, writeData.errors);
}
```

**Write script zwraca JSON:**

**Sukces:**
```json
{
  "success": true,
  "status": "completed",
  "scene_key": "scene_0005",
  "thread_id": "68e7cc28-4140-8329-af5c-2b67193e69ce",
  "message": "All data saved successfully"
}
```

**Błąd:**
```json
{
  "success": false,
  "errors": ["Failed to set thread_id: ...", "Failed to update status: ..."]
}
```

## Stan końcowy zadania:

- Jedno image_gen subtask przetworzone z ustawionym statusem:
  - **completed** - obraz wygenerowany pomyślnie
  - **failed** - błąd treści/polityki/network/inne
  - **pending** - limit ChatGPT Plus (pozostaje pending do ponownej próby)
- Thread ID zapisany w właściwościach image_gen subtaska
- PROJECT_ID zapisany w właściwościach listy (jeśli projekt był tworzony)
- Obraz rozpoczął generowanie w ChatGPT

## Uwagi techniczne:

### Wrapper Scripts
- **todoit-read-task.sh**: Agreguje 4 wywołania TODOIT CLI w 1 wywołanie (book_folder, project_id, next task, yaml path)
- **todoit-write-result.sh**: Agreguje 3-4 wywołania TODOIT CLI w 1 wywołanie (thread_id, project_id, error, status)
- **Korzyści**: 2 wywołania Bash zamiast 7-9, prostsze parsowanie JSON, mniej tokenów

### Playwright Script
- **Lokalizacja:** `scripts/chatgpt/upload-scene.ts`
- **Tryb:** headless (szybkie wykonanie)
- **Output:** JSON na stdout
- **Screenshots:** `/tmp/chatgpt-success-*.png` lub `/tmp/chatgpt-error-*.png`

### Error Handling
- **ChatGPT Plus limit:** Status pozostaje `pending` → auto-retry później
- **Content policy:** Status → `failed` (permanent)
- **Unknown errors:** Status → `failed`, zapisz error message

## Debugowanie

### Test wrapper scripts ręcznie:
```bash
# Test read
scripts/chatgpt/todoit-read-task.sh m00062_cointelpro_revelation_1971

# Test write
scripts/chatgpt/todoit-write-result.sh m00062_cointelpro_revelation_1971 scene_0005 "test-thread-123" completed "" ""
```

### Test Playwright script:
```bash
# With headless=false for debugging
npx ts-node scripts/chatgpt/upload-scene.ts m00062_cointelpro_revelation_1971 scene_0005.yaml g-p-xxx
```

## Następny krok:

Po successful completion image_gen, następny agent (37d-a4) pobierze gotowy obraz z ChatGPT.
