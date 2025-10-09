---
name: 37d-a3-playwright-upload
description: |
  Subagent worker for AI image generation in ChatGPT using STANDALONE Playwright script and TODOIT subtasks.
  Processes image_gen subtasks by finding scenes where scene_style is completed but image_gen is pending.
  Uses standalone TypeScript script (0 tokens!) instead of MCP playwright-headless.
execution_order: 3
min_tasks: 1
max_tasks: 1
todo_list: true
---

# Subagent: 37d-a3 - AI Image Generation Worker (Playwright Standalone)

Worker subagent dla pojedynczego zadania generowania obrazu w ChatGPT.
Używa systemu subtasks do śledzenia stanu generowania obrazów.

**KLUCZOWA RÓŻNICA:** Używa standalone Playwright script (npx ts-node) zamiast MCP!
**KORZYŚCI:** 0 tokenów na automatyzację, szybsze, deterministyczne, łatwe do debugowania.

## Dane wejściowe z promptu wywołania:

- TODOIT_LIST: "[BOOK_FOLDER]" (np. "0011_gullivers_travels")

## Kroki worker subagenta:
Zrealizuj wszystkie poniższe 7 faz jedna po drugiej, starannie, nie pomijając żadnej z nich.

### Faza 1. Odczyt konfiguracji z TODOIT

```javascript
// Odczytaj BOOK_FOLDER z właściwości listy TODOIT
const bookFolder = await mcp__todoit__todo_get_list_property({
  list_key: "[TODOIT_LIST]",
  property_key: "book_folder"
});

if (!bookFolder.success) {
  console.log("ERROR: book_folder property not found in TODOIT list [TODOIT_LIST]");
  return;
}

console.log(`Processing book: ${bookFolder.property_value}`);
```

### Faza 2. Znajdź następne zadanie do generowania

```javascript
// Używa zoptymalizowanego todo_find_items_by_status do znajdowania image_gen subtasków
// gotowych do generowania (scene_style completed, image_gen pending)
const readyImageTasks = await mcp__todoit__todo_find_items_by_status({
  list_key: "[TODOIT_LIST]",
  conditions: {
    "scene_style": "completed",
    "image_gen": "pending"
  },
  limit: 1  // CRITICAL: Only 1 to minimize token usage
});

if (!readyImageTasks.success || readyImageTasks.matches.length === 0) {
  console.log("No image_gen subtasks ready for processing");
  return;
}

const nextTask = readyImageTasks.matches[0];
const parentItem = nextTask.parent;
const sceneKey = parentItem.item_key;          // np. "scene_0001"
const imageGenSubtask = nextTask.matching_subitems.find(s => s.item_key === "image_gen");

console.log(`Processing ${sceneKey} for image generation`);
console.log(`Found ${readyImageTasks.matches_count} total image_gen tasks ready`);
```

### Faza 3. Odczytaj ścieżkę pliku YAML i project ID

```javascript
// Znajdź odpowiedni scene_style subtask aby odczytać ścieżkę pliku
const styleSubtask = nextTask.matching_subitems.find(s => s.item_key === "scene_style");

const stylePathProperty = await mcp__todoit__todo_get_item_property({
  list_key: "[TODOIT_LIST]",
  item_key: styleSubtask.item_key,
  parent_item_key: sceneKey,
  property_key: "scene_style_pathfile"
});

if (!stylePathProperty.success) {
  throw new Error(`Style file path not found for ${sceneKey}`);
}

const yamlFilename = stylePathProperty.property_value.split('/').pop(); // np. "scene_01.yaml"

console.log(`Using YAML file: ${yamlFilename}`);

// Sprawdź czy PROJECT_ID istnieje w właściwościach listy
const projectId = await mcp__todoit__todo_get_list_property({
  list_key: "[TODOIT_LIST]",
  property_key: "project_id"
});

let projectIdArg = '';
if (projectId.success && projectId.property_value) {
  projectIdArg = projectId.property_value;
  console.log(`Using existing project ID: ${projectIdArg}`);
}
```

### Faza 4. Uruchom standalone Playwright script

**CRITICAL:** Używamy Bash + npx ts-node zamiast MCP playwright-headless!

```bash
# Uruchom standalone script z parametrami
npx ts-node scripts/chatgpt/upload-scene.ts [book_folder] [yaml_filename] [project_id]
```

**Przykład:**
```bash
npx ts-node scripts/chatgpt/upload-scene.ts 0011_gullivers_travels scene_0001.yaml g-p-68b7e9551f8081919511b1ce73c242ca
```

**Wykonaj:**
```javascript
// Konstruuj komendę
const bookFolderValue = bookFolder.property_value;
const cmd = projectIdArg
  ? `npx ts-node scripts/chatgpt/upload-scene.ts ${bookFolderValue} ${yamlFilename} ${projectIdArg}`
  : `npx ts-node scripts/chatgpt/upload-scene.ts ${bookFolderValue} ${yamlFilename}`;

console.log(`Running command: ${cmd}`);

// Uruchom komendę przez Bash (timeout 3 minuty)
Bash({
  command: cmd,
  timeout: 180000
});
```

### Faza 5. Parsuj JSON output

Script zwraca JSON na stdout. Przykłady:

**Sukces:**
```json
{
  "success": true,
  "threadId": "abc123-def456-ghi789",
  "projectId": "g-p-68b7e9551f8081919511b1ce73c242ca",
  "sceneKey": "scene_0001"
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

**Wykonaj:**
```javascript
// Parsuj JSON output z Bash result
const output = [BASH_OUTPUT];  // Output z poprzedniej komendy Bash

// Znajdź JSON w output (może być stderr + stdout)
const jsonMatch = output.match(/\{[\s\S]*"success"[\s\S]*\}/);
if (!jsonMatch) {
  console.log("ERROR: Could not parse JSON output from script");
  console.log("Output:", output);
  return;
}

const result = JSON.parse(jsonMatch[0]);

console.log(`Script result: ${result.success ? 'SUCCESS' : 'FAILED'}`);
if (result.threadId) {
  console.log(`Thread ID: ${result.threadId}`);
}
if (result.projectId) {
  console.log(`Project ID: ${result.projectId}`);
}
if (result.error) {
  console.log(`Error: ${result.error.substring(0, 200)}...`);
  console.log(`Error type: ${result.errorType}`);
}
```

### Faza 6. Zapisz dane w TODOIT

```javascript
// Zapisz thread ID w właściwościach image_gen subtaska (zawsze, nawet przy błędzie)
if (result.threadId) {
  await mcp__todoit__todo_set_item_property({
    list_key: "[TODOIT_LIST]",
    item_key: "image_gen",
    parent_item_key: sceneKey,
    property_key: "thread_id",
    property_value: result.threadId
  });
}

// Zapisz Project ID w liście (jeśli otrzymaliśmy nowy)
if (result.projectId && !projectIdArg) {
  await mcp__todoit__todo_set_list_property({
    list_key: "[TODOIT_LIST]",
    property_key: "project_id",
    property_value: result.projectId
  });
  console.log(`Saved new project ID: ${result.projectId}`);
}

// Zapisz błąd jeśli wystąpił
if (!result.success && result.error) {
  await mcp__todoit__todo_set_item_property({
    list_key: "[TODOIT_LIST]",
    item_key: "image_gen",
    parent_item_key: sceneKey,
    property_key: "ERROR",
    property_value: result.error.substring(0, 500)  // Truncate to 500 chars
  });
}
```

### Faza 7. Ustaw status subtaska

```javascript
if (result.success) {
  // Sukces - ustaw completed
  await mcp__todoit__todo_update_item_status({
    list_key: "[TODOIT_LIST]",
    item_key: sceneKey,
    subitem_key: "image_gen",
    status: "completed"
  });

  console.log(`✓ ${sceneKey} image_gen completed. Thread ID: ${result.threadId}`);

} else {
  // Błąd - kategoryzuj

  if (result.errorType === 'limit') {
    // ChatGPT Plus limit - POZOSTAW jako pending (retry później)
    console.log(`⚠ ${sceneKey} image_gen - ChatGPT Plus limit detected. Keeping as pending for retry.`);
    console.log(`Limit details: ${result.error}`);

    // NIE zmieniaj statusu - subtask pozostaje pending

  } else {
    // Inne błędy (policy, unknown) - ustaw failed
    await mcp__todoit__todo_update_item_status({
      list_key: "[TODOIT_LIST]",
      item_key: sceneKey,
      subitem_key: "image_gen",
      status: "failed"
    });

    console.log(`✗ ${sceneKey} image_gen failed. Error type: ${result.errorType}`);
    console.log(`Error: ${result.error}`);
  }
}
```

## Uwagi techniczne:

### Standalone Playwright Script
- **Lokalizacja:** `scripts/chatgpt/upload-scene.ts`
- **Uruchomienie:** `npx ts-node scripts/chatgpt/upload-scene.ts <book> <scene> [projectId]`
- **Output:** JSON na stdout
- **Exit code:** 0 = success, 1 = failure
- **Screenshots:** `/tmp/chatgpt-success-*.png` lub `/tmp/chatgpt-error-*.png`

### Playwright Browser Profile
- **Lokalizacja:** `~/.cache/chatgpt-playwright-profile/`
- **Cel:** Persistent login (user musi raz zalogować się ręcznie)
- **Model:** o4-mini (hardcoded w scripcie)

### Różnice vs stary agent (37d-a3-generate-image)
- ❌ NIE używa MCP playwright-headless
- ✅ Używa Bash + standalone TypeScript script
- ✅ 0 tokenów na automatyzację (tylko parsing JSON)
- ✅ Deterministyczne selektory (nie dynamiczne refs)
- ✅ Łatwiejsze debugowanie (Playwright Inspector, screenshots)
- ✅ Szybsze (brak MCP overhead)

### Error Handling
- **ChatGPT Plus limit:** Subtask pozostaje `pending` → retry później
- **Content policy:** Subtask → `failed` (permanent)
- **Network errors:** Subtask → `failed` (można retry ręcznie)
- **Unknown errors:** Subtask → `failed`, zapisz error message

### BOOK_FOLDER i PROJECT_ID
- **BOOK_FOLDER** jest odczytywany z właściwości listy TODOIT
- **PROJECT_ID** jest zapisywany w liście przy pierwszym utworzeniu projektu
- **Thread ID** jest zapisywany w właściwościach image_gen subtaska
- **Nazwa projektu** ChatGPT = BOOK_FOLDER (np. "0011_gullivers_travels")

## Stan końcowy zadania:

- Jedno image_gen subtask przetworzone z ustawionym statusem:
  - **completed** - obraz wygenerowany pomyślnie
  - **failed** - błąd treści/polityki/network/inne (nie limit ChatGPT Plus)
  - **pending** - limit ChatGPT Plus (do ponownej próby)
- Thread ID zapisany w właściwościach image_gen subtaska
- PROJECT_ID zapisany w właściwościach listy (jeśli projekt był tworzony)
- Obraz rozpoczął generowanie w ChatGPT z pełną specyfikacją YAML (sukces) lub wykryto limit/błąd

## Debugowanie

### Jeśli script failuje:
1. Sprawdź screenshot w `/tmp/chatgpt-*.png`
2. Uruchom script ręcznie z headless=false:
   ```bash
   npx ts-node scripts/chatgpt/upload-scene.ts 0016_lalka scene_01.yaml
   ```
3. Użyj Playwright Inspector:
   ```bash
   PWDEBUG=1 npx ts-node scripts/chatgpt/upload-scene.ts 0016_lalka scene_01.yaml
   ```

### Jeśli selektory się zmieniły (ChatGPT UI update):
1. Zobacz `docs/playwright/chatgpt-upload-test-plan.md`
2. Zaktualizuj selektory w `scripts/chatgpt/upload-scene.ts`
3. Opcjonalnie: użyj Playwright Healer Agent (przyszłość)

## Następny krok po generacji obrazu:

Po successful completion image_gen, następny agent (37d-a4) pobierze gotowy obraz z ChatGPT.
