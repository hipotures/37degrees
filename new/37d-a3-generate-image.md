---
name: 37d-a3-generate-image
description: |
  Subagent worker for AI image generation in ChatGPT using MCP playwright-headless and TODOIT subtasks.
  Processes image_gen subtasks by finding scenes where scene_style is completed but image_gen is pending.
  Generates images, saves thread IDs, and updates subtask status.
execution_order: 3
min_tasks: 1
max_tasks: 1
todo_list: true
---

# Subagent: 37d-a3 - AI Image Generation Worker (Subtasks Version)

Worker subagent dla pojedynczego zadania generowania obrazu w ChatGPT.
Używa systemu subtasks do śledzenia stanu generowania obrazów.

UWAGA: Używaj MCP todoit (subtasks system) i playwright-headless do automatyzacji

## Dane wejściowe z promptu wywołania:

- TODOIT_LIST: "[BOOK_FOLDER]" (np. "0011_gullivers_travels")

## Kroki worker subagenta:

### 1. Odczyt konfiguracji z TODOIT

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

### 2. Znajdź następne zadanie do generowania

```javascript
// Używa zoptymalizowanego todo_find_subitems_by_status do znajdowania image_gen subtasków
// gotowych do generowania (scene_style completed, image_gen pending)
const readyImageTasks = await mcp__todoit__todo_find_subitems_by_status({
  list_key: "[TODOIT_LIST]",
  conditions: {
    "scene_style": "completed",
    "image_gen": "pending"
  },
  limit: 1  // Przetwarzaj tylko jedno zadanie na raz
});

if (!readyImageTasks.success || readyImageTasks.items.length === 0) {
  console.log("No image_gen subtasks ready for processing");
  return;
}

const nextTask = readyImageTasks.items[0];
const imageGenSubtaskKey = nextTask.item_key;  // np. "scene_0001_image_gen"

// Wyciągnij scene key z subtask key 
const sceneKey = imageGenSubtaskKey.replace('_image_gen', ''); // np. "scene_0001"

console.log(`Processing ${sceneKey} for image generation`);
console.log(`Found ${readyImageTasks.count} total image_gen tasks ready`);
```

### 3. Rozpocznij przetwarzanie

```javascript
// Subtask pozostaje pending podczas przetwarzania - nie ma potrzeby ustawiania in_progress
// dla krótkich zadań. Po udanym zakończeniu będzie completed, po nieudanym failed.
console.log(`Starting image generation for ${imageGenSubtaskKey}`);
```

### 4. Odczytaj ścieżkę pliku YAML

```javascript
// Znajdź odpowiedni scene_style subtask aby odczytać ścieżkę pliku
const styleSubtaskKey = imageGenSubtaskKey.replace('_image_gen', '_scene_style');

const stylePathProperty = await mcp__todoit__todo_get_item_property({
  list_key: "[TODOIT_LIST]",
  item_key: styleSubtaskKey,
  property_key: "scene_style_pathfile"
});

if (!stylePathProperty.success) {
  throw new Error(`Style file path not found for ${sceneKey}`);
}

const yamlPath = `/home/xai/DEV/37degrees/${stylePathProperty.property_value}`;
const yamlFilename = stylePathProperty.property_value.split('/').pop(); // np. "scene_01.yaml"

console.log(`Using YAML file: ${yamlFilename}`);
```

### 5. Nawigacja do projektu ChatGPT

```javascript
// Sprawdź czy PROJECT_ID istnieje w właściwościach listy
const projectId = await mcp__todoit__todo_get_list_property({
  list_key: "[TODOIT_LIST]",
  property_key: "project_id"
});

if (projectId.success && projectId.property_value) {
  // Użyj bezpośredniej nawigacji do istniejącego projektu z modelem o4-mini
  await mcp__playwright-headless__browser_navigate({
    url: `https://chatgpt.com/g/${projectId.property_value}/project?model=o4-mini`
  });
} else {
  // Utwórz nowy projekt ChatGPT z modelem o4-mini
  await mcp__playwright-headless__browser_navigate({
    url: "https://chatgpt.com/?model=o4-mini"
  });
  
  // Otwórz sidebar
  await mcp__playwright-headless__browser_click({
    element: "Open sidebar button",
    ref: "REF_FROM_SNAPSHOT"
  });
  
  // Sprawdź czy projekt book_folder istnieje
  await mcp__playwright-headless__browser_snapshot();
  
  // Jeśli projekt istnieje - kliknij go
  // Jeśli nie istnieje - utwórz nowy:
  await mcp__playwright-headless__browser_click({
    element: "New project button",
    ref: "REF_FROM_SNAPSHOT"
  });
  
  await mcp__playwright-headless__browser_type({
    element: "project name input field",
    ref: "REF_FROM_SNAPSHOT",
    text: bookFolder.property_value,
    submit: true
  });
  
  // Wyciągnij Project ID z URL po utworzeniu
  const newProjectId = await mcp__playwright-headless__browser_evaluate({
    function: "() => { return window.location.pathname.split('/')[2]; }"
  });
  
  // Zapisz Project ID w właściwościach listy TODOIT
  await mcp__todoit__todo_set_list_property({
    list_key: "[TODOIT_LIST]",
    property_key: "project_id", 
    property_value: newProjectId
  });
  
  console.log(`Created new project with ID: ${newProjectId}`);
}
```

### 6. Oczyszczenie widoku projektu

```javascript
// Ukryj mylące elementy projektowe przed analizą
await mcp__playwright-headless__browser_evaluate({
  function: `() => {
    const buttons = document.querySelectorAll('button');
    let addFilesSection = null;
    
    for (let button of buttons) {
      if (button.textContent?.includes('Add files') && button.textContent?.includes('Chats in this project can access')) {
        addFilesSection = button.parentElement;
        break;
      }
    }
    
    if (addFilesSection) {
      addFilesSection.style.display = 'none';
      addFilesSection.setAttribute('data-hidden-by-claude', 'project-files');
    }
    
    return addFilesSection ? 'Project files section hidden' : 'Section not found';
  }`
});
```

### 7. Załączenie pliku YAML

```javascript
// Kliknij przycisk "Add photos & files"
await mcp__playwright-headless__browser_click({
  element: "Add photos & files button",
  ref: "REF_FROM_SNAPSHOT"
});

// Wybierz "Add files" z menu
await mcp__playwright-headless__browser_click({
  element: "Add files menu option",
  ref: "REF_FROM_SNAPSHOT"
});

// Załącz plik YAML z zadania
await mcp__playwright-headless__browser_file_upload({
  paths: [yamlPath]
});

// Poczekaj aż plik się załączy i zweryfikuj jego poprawne załączenie
await mcp__playwright-headless__browser_wait_for({ time: 3 });
```

### 8. Wybór narzędzia "Create image"

```javascript
// Kliknij przycisk "Choose tool"
await mcp__playwright-headless__browser_click({
  element: "Choose tool button",
  ref: "REF_FROM_SNAPSHOT"
});

// Wybierz "Create image" z menu dropdown
await mcp__playwright-headless__browser_click({
  element: "Create image option",
  ref: "REF_FROM_SNAPSHOT"
});
```

### 9. Wpisanie promptu

```javascript
// CRITICAL: ChatGPT używa contenteditable div, NIE textarea!
const sceneNumber = sceneKey.replace('scene_', '').replace(/^0+/, '') || '1';
const promptText = `scene_${sceneNumber} - create an image based on the scene, style, and visual specifications described in the attached YAML. The YAML is a blueprint, not the content.`;

await mcp__playwright-headless__browser_evaluate({
  function: `() => {
    const contentEditable = document.querySelector('[contenteditable="true"]');
    if (contentEditable) {
      contentEditable.textContent = '${promptText}';
      contentEditable.dispatchEvent(new Event('input', { bubbles: true }));
      contentEditable.focus();
      return 'Text entered successfully';
    }
    return 'Contenteditable field not found';
  }`
});
```

### 10. Uruchomienie generacji

```javascript
// Kliknij przycisk "Send prompt" (czarne koło ze strzałką)
await mcp__playwright-headless__browser_click({
  element: "Send prompt button",
  ref: "REF_FROM_SNAPSHOT"
});

// Czekaj na jakąkolwiek odpowiedź ChatGPT
// CRITICAL: Może być "Getting started" LUB komunikat błędu

let responseAppeared = false;

// Sprawdź czy pojawiła się odpowiedź w ciągu 60 sekund
for (let attempt = 1; attempt <= 6; attempt++) {  // 6 prób x 10s = 60s
  const snapshotCheck = await mcp__playwright-headless__browser_snapshot();
  
  const checkText = snapshotCheck.toString();
  if (checkText.includes("Getting started") ||
      checkText.includes("You've hit the plus plan limit") ||
      checkText.includes("can't create that image") ||
      checkText.includes("I'm unable to generate") ||
      checkText.includes("violates our content policies") ||
      checkText.includes("sorry") ||
      checkText.includes("unfortunately")) {
    responseAppeared = true;
    break;
  }
  
  await mcp__playwright-headless__browser_wait_for({ time: 10 });
}

// Jeśli nic się nie pojawiło - przeładuj stronę i sprawdź stan
if (!responseAppeared) {
  console.log("⚠️ Brak odpowiedzi ChatGPT - przeładowuję stronę");
  const currentUrl = await mcp__playwright-headless__browser_evaluate({
    function: "() => window.location.href"
  });
  await mcp__playwright-headless__browser_navigate({ url: currentUrl });
  await mcp__playwright-headless__browser_wait_for({ time: 3 });
}
```

### 11. Sprawdzenie rezultatu i finalizacja

```javascript
// CRITICAL: Sprawdź aktualny stan po ewentualnym przeładowaniu
const snapshotAfterSend = await mcp__playwright-headless__browser_snapshot();
const responseText = snapshotAfterSend.toString();

if (responseText.includes("can't create that image") || 
    responseText.includes("I'm unable to generate") ||
    responseText.includes("I cannot create") ||
    responseText.includes("violates our content policies") ||
    responseText.includes("request violates") ||
    responseText.includes("content policy") ||
    responseText.includes("You've hit the plus plan limit") ||
    responseText.includes("sorry") ||
    responseText.includes("unfortunately")) {
  
  // Wyciągnij pełny komunikat błędu z ChatGPT
  const errorMessage = await mcp__playwright-headless__browser_evaluate({
    function: `() => {
      const messageElements = document.querySelectorAll('[data-message-author-role="assistant"]');
      for (let elem of messageElements) {
        const text = elem.textContent;
        if (text.includes('can\\'t create') || 
            text.includes('unable to generate') ||
            text.includes('cannot create') ||
            text.includes('violates our content policies') ||
            text.includes('request violates') ||
            text.includes('content policy') ||
            text.includes('You\\'ve hit the plus plan limit') ||
            text.includes('sorry') ||
            text.includes('unfortunately')) {
          return text.trim();
        }
      }
      return 'ChatGPT image generation error detected';
    }`
  });
  
  // Zapisz komunikat błędu w właściwościach zadania
  await mcp__todoit__todo_set_item_property({
    list_key: "[TODOIT_LIST]",
    item_key: imageGenSubtaskKey,
    property_key: "ERROR",
    property_value: errorMessage
  });
  
  // Wyciągnij thread ID nawet w przypadku błędu
  const threadId = await mcp__playwright-headless__browser_evaluate({
    function: "() => { return window.location.pathname.split('/c/')[1]; }"
  });
  
  // Zapisz thread ID w właściwościach zadania
  await mcp__todoit__todo_set_item_property({
    list_key: "[TODOIT_LIST]",
    item_key: imageGenSubtaskKey,
    property_key: "thread_id",
    property_value: threadId
  });
  
  // Ustaw subtask jako failed
  await mcp__todoit__todo_update_item_status({
    list_key: "[TODOIT_LIST]",
    item_key: imageGenSubtaskKey,
    status: "failed"
  });
  
  // Raportuj błąd
  console.log(`BŁĄD: ${nextTask.content} - ChatGPT generation error. Thread ID: ${threadId}`);
  console.log(`Error details: ${errorMessage}`);
  return;
}

// Sukces - zapisz thread ID i finalizuj zadanie
const threadId = await mcp__playwright-headless__browser_evaluate({
  function: "() => { return window.location.pathname.split('/c/')[1]; }"
});

// Zapisz thread ID w właściwościach zadania
await mcp__todoit__todo_set_item_property({
  list_key: "[TODOIT_LIST]",
  item_key: imageGenSubtaskKey,
  property_key: "thread_id",
  property_value: threadId
});

// Ustaw subtask jako completed
await mcp__todoit__todo_update_item_status({
  list_key: "[TODOIT_LIST]",
  item_key: imageGenSubtaskKey,
  status: "completed"
});

// Raportuj sukces
console.log(`Zadanie ${nextTask.content} ukończone. Thread ID: ${threadId}`);
```

## Uwagi techniczne:

- **CRITICAL:** Worker przetwarza TYLKO JEDNO zadanie na wywołanie
- **System subtasks:** image_gen subtask status (pending → completed/failed)
- **Brak in_progress:** Subtaski pozostają pending podczas przetwarzania, przechodzą bezpośrednio do completed/failed
- **BOOK_FOLDER** jest odczytywany z właściwości listy TODOIT
- **PROJECT_ID** jest zapisywany w liście przy pierwszym utworzeniu projektu
- **Thread ID** jest zapisywany w właściwościach image_gen subtaska
- **Worker** kończy działanie po ukończeniu jednego zadania
- **Orchestrator** wywołuje worker w pętli dopóki są zadania do generowania
- **Nazwa projektu** ChatGPT = BOOK_FOLDER (np. "0011_gullivers_travels")
- **CRITICAL:** Używaj contenteditable div, NIE textarea dla promptu
- **Element refs** są dynamiczne - zawsze rób snapshot przed interakcją

## Stan końcowy zadania:

- Jedno image_gen subtask przetworzone z ustawionym statusem completed/failed
- Thread ID zapisany w właściwościach image_gen subtaska
- PROJECT_ID zapisany w właściwościach listy (przy pierwszym wywołaniu)
- Obraz rozpoczął generowanie w ChatGPT z pełną specyfikacją YAML
- Worker zakończył działanie - można wywołać następne zadanie
- Zadanie główne pozostaje in_progress do czasu ukończenia pobierania

## Optymalizacja z todo_find_subitems_by_status:

**Korzyści używania `todo_find_subitems_by_status`:**

1. **Jednozapytaniowe wyszukiwanie** - Zamiast iterować przez wszystkie subtaski i sprawdzać statusy rodzeństwa, jedna operacja znajduje gotowe zadania
2. **Filtrowanie na poziomie bazy** - Warunki aplikowane w SQL, nie w kodzie aplikacji  
3. **Limit na poziomie zapytania** - Pobiera tylko potrzebną liczbę wyników
4. **Automatyczna synchronizacja** - Zawsze aktualne statusy bez ręcznego odświeżania

**Przykład bez optymalizacji (powolny):**
```javascript
// ❌ Nieefektywne - wymaga wielu zapytań
const allItems = await todo_get_list_items(list_key);
const readyTasks = [];
for (const item of allItems.items) {
  const subtasks = await todo_get_subtasks(list_key, item.item_key);
  const styleTask = subtasks.find(s => s.item_key.includes('_scene_style'));
  const imageTask = subtasks.find(s => s.item_key.includes('_image_gen'));
  if (styleTask?.status === 'completed' && imageTask?.status === 'pending') {
    readyTasks.push(imageTask);
  }
}
```

**Z optymalizacją (szybki):**
```javascript
// ✅ Efektywne - jedno zapytanie  
const readyTasks = await todo_find_subitems_by_status({
  list_key: "[TODOIT_LIST]",
  conditions: {
    "scene_style": "completed", 
    "image_gen": "pending"
  },
  limit: 1
});
```

## Integracja z następnym etapem:

Po ukończeniu, system jest gotowy na 37d-a4-download-image:

```javascript
// Sprawdź gotowość na pobieranie
const readyDownloadTasks = await mcp__todoit__todo_find_subitems_by_status({
  list_key: "[TODOIT_LIST]",
  conditions: {
    "image_gen": "completed",
    "image_dwn": "pending"
  },
  limit: 25
});

console.log(`Ready for download: ${readyDownloadTasks.items.length} scenes`);
```