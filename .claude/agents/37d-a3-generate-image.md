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
Zrealizuj wszystkie popniższe 10 faz jedna po drugiej, starannie, nie pomijając żadnej z nich.

### Faza 1. Odczyt konfiguracji z TODOIT
Wykonaj:

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
Wykonaj:

```javascript
// Używa zoptymalizowanego todo_find_items_by_status do znajdowania image_gen subtasków
// gotowych do generowania (scene_style completed, image_gen pending)
const readyImageTasks = await mcp__todoit__todo_find_items_by_status({
  list_key: "[TODOIT_LIST]",
  conditions: {
    "scene_style": "completed",
    "image_gen": "pending"
  },
  limit: 1  // Przetwarzaj tylko jedno zadanie na raz
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

### Faza 3. Rozpocznij przetwarzanie
Wykonaj:

```javascript
// Subtask pozostaje pending podczas przetwarzania - nie ma potrzeby ustawiania in_progress
// dla krótkich zadań. Po udanym zakończeniu będzie completed, po nieudanym failed.
console.log(`Starting image generation for ${sceneKey}`);
```

### Faza 4. Odczytaj ścieżkę pliku YAML
Wykonaj:

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

const yamlPath = `/home/xai/DEV/37degrees/${stylePathProperty.property_value}`;
const yamlFilename = stylePathProperty.property_value.split('/').pop(); // np. "scene_01.yaml"

console.log(`Using YAML file: ${yamlFilename}`);
```

### Faza 5. Nawigacja do projektu ChatGPT
Uzywany model, to o4-mini - TYLKO TEN MODEL MA BYC UZYWANY! Nie testuj innych modeli, nie sprawdzaj, nie szukaj!
Uwaga: projectId.property_value może byc zapisany jako (przykład): 
  68b7e9551f8081919511b1ce73c242ca
albo
  g-p-68b7e9551f8081919511b1ce73c242ca
Więc jeśli masz taki string 68b7e9551f8081919511b1ce73c242ca musisz do niego dokleić przedrostek "g-p-"

Pełna poprawna ścieżka wygląda wtedy tak:
  https://chatgpt.com/g/g-p-68b7e9551f8081919511b1ce73c242ca/project
  albo tak
  https://chatgpt.com/g/g-p-68b7e9551f8081919511b1ce73c242ca-0098-the-man-in-the-high-castle/project
Obydwie prowadzą na tą samą stronę!


```javascript
// Sprawdź czy PROJECT_ID istnieje w właściwościach listy
const projectId = await mcp__todoit__todo_get_list_property({
  list_key: "[TODOIT_LIST]",
  property_key: "project_id"
});

if (projectId.success && projectId.property_value) {
  // Użyj bezpośredniej nawigacji do istniejącego projektu z modelem o4-mini
  await mcp__playwright-headless__browser_navigate({
    url: `https://chatgpt.com/g/g-p-${projectId.property_value}/project?model=o4-mini`
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

### Faza 6. Oczyszczenie widoku projektu
Wykonaj:

```javascript
// Ukryj mylące elementy projektowe przed analizą
await mcp__playwright-headless__browser_evaluate({
  function: `() => {
    const buttons = document.querySelectorAll('button');
    let addFilesSection = null;
    
    for (let button of buttons) {
      if (button.textContent?.includes('Add files')) {
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

### Faza 7. Załączenie pliku YAML
Sprawdz, czy wybrany model to o4-mini, jesli nie, ustaw ten model.

W snapshocie znajdziesz taki kawałek tekstu (przykład, refy będą miały inne id):
  - button "Add files" [ref=e43] [cursor=pointer]:
    - generic [ref=e44] [cursor=pointer]: Add files
    On nas NIE interesuje, to dodaje pliki do projektu a tego NIE chcemy!

    Interesuje nas ten przycisk pomiędzy "New chat in.." a kolejnym generickiem, w tym przykładzie to jest ref=e55:
    - generic [ref=e48]:
      - paragraph [ref=e52]: New chat in 0098_the_man_in_the_high_castle
      - button [ref=e55] [cursor=pointer]:
        - img
      - generic [ref=e59]

Klikasz w to 2 razy, po kolei:
 - za pierwszym wybierasz "Create image"
 - za drugim "Add files" (tylko w tym miejscu!) i załaczasz plik yaml

```javascript
// Załącz plik YAML z zadania
await mcp__playwright-headless__browser_file_upload({
  paths: [yamlPath]
});

// Poczekaj aż plik się załączy i zweryfikuj jego poprawne załączenie
await mcp__playwright-headless__browser_wait_for({ time: 3 });
```

### Faza 8. Wpisanie promptu
Wykonaj:

```javascript
// CRITICAL: ChatGPT używa contenteditable div, NIE textarea!
const promptText = `[TODOIT_LIST]:${sceneKey} - create an image based on the scene, style, and visual specifications described in the attached YAML. Think carefully: the YAML is a blueprint, not the content!`;

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

### Faza 9. Uruchomienie generacji
Wykonaj:

```javascript
// Kliknij przycisk "Send prompt" (czarne koło ze strzałką)
await mcp__playwright-headless__browser_click({
  element: "Send prompt button",
  ref: "REF_FROM_SNAPSHOT"
});
```
Czekaj na jakąkolwiek odpowiedź ChatGPT
CRITICAL: Może być "Getting started" LUB komunikat błędu
"Getting started" oznacza poprawne rozpoczęcie generacji obrazu!!! Nie oznaczaj tego jako błąd!

Wykonaj dokładnie to polecenie, nie zmieniaj go na inne:
```
Bash(sleep 30)
```

### Faza 10. Sprawdzenie rezultatu i finalizacja
Wykonaj:

```javascript
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
    item_key: "image_gen",
    parent_item_key: sceneKey,
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
    item_key: "image_gen",
    parent_item_key: sceneKey,
    property_key: "thread_id",
    property_value: threadId
  });
  
  // Sprawdź czy to komunikaty związane z limitem ChatGPT Plus - nie zmieniaj statusu
  if (errorMessage.includes('limit') && (errorMessage.includes('plus plan') || errorMessage.includes('usage limit') || errorMessage.includes('available again'))) {
    console.log(`BŁĄD: ${sceneKey} image_gen - ChatGPT Plus limit detected. Thread ID: ${threadId}`);
    console.log(`Limit details: ${errorMessage}`);
    
    // UWAGA: NIE ustawiaj statusu failed dla limitu ChatGPT Plus!
    // Subtask pozostaje pending do ponownej próby
    return;
  }
  
  // Ustaw subtask jako failed tylko dla innych błędów (nie limitu ChatGPT Plus)
  await mcp__todoit__todo_update_item_status({
    list_key: "[TODOIT_LIST]",
    item_key: sceneKey,
    subitem_key: "image_gen",
    status: "failed"
  });
  
  // Raportuj błąd i zrób screenshot
  await mcp__playwright-headless__browser_take_screenshot({fullPage: true});
  console.log(`BŁĄD: ${sceneKey} image_gen - ChatGPT generation error. Thread ID: ${threadId}`);
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
  item_key: "image_gen",
  parent_item_key: sceneKey,
  property_key: "thread_id",
  property_value: threadId
});

// Ustaw subtask jako completed
await mcp__todoit__todo_update_item_status({
  list_key: "[TODOIT_LIST]",
  item_key: sceneKey,
  subitem_key: "image_gen",
  status: "completed"
});


// Raportuj sukces i zrob zapis udanej generacji robiąc screenshot
await mcp__playwright-headless__browser_take_screenshot({fullPage: true});
console.log(`Zadanie ${sceneKey} image_gen ukończone. Thread ID: ${threadId}`);
```

## Uwagi techniczne:

- **System subtasks:** image_gen subtask status (pending → completed/failed, ale przy limitach ChatGPT Plus pozostaje pending)
- **Brak in_progress:** Subtaski pozostają pending podczas przetwarzania, przechodzą bezpośrednio do completed/failed
- **ChatGPT Plus limit:** Gdy wystąpi limit, subtask pozostaje pending do ponownej próby
- **BOOK_FOLDER** jest odczytywany z właściwości listy TODOIT
- **PROJECT_ID** jest zapisywany w liście przy pierwszym utworzeniu projektu
- **Thread ID** jest zapisywany w właściwościach image_gen subtaska
- **Nazwa projektu** ChatGPT = BOOK_FOLDER (np. "0011_gullivers_travels")
- **CRITICAL:** Używaj contenteditable div, NIE textarea dla promptu
- **Element refs** są dynamiczne - zawsze rób snapshot przed interakcją
- NIE oznaczaj zadanie jako błędne, jeśli nie ma wyraźnego komunikatu o błędzie, możesz przeładować stronę, jeśli nie masz pewności co się dzieje
- Jeśli napotkasz jakiś problem z generacją obrazu, zrób screenshot:
  await mcp__playwright-headless__browser_take_screenshot({fullPage: true});
  a potem kontynuuj zgodnie z planem, możesz przeładować stronę

## Stan końcowy zadania:

- Jedno image_gen subtask przetworzone z ustawionym statusem:
  - **completed** - obraz wygenerowany pomyślnie
  - **failed** - błąd treści/polityki/inne (nie limit ChatGPT Plus)
  - **pending** - limit ChatGPT Plus (do ponownej próby)
- Thread ID zapisany w właściwościach image_gen subtaska
- PROJECT_ID zapisany w właściwościach listy (jeśli projekt był tworzony)
- Obraz rozpoczął generowanie w ChatGPT z pełną specyfikacją YAML (sukces) lub wykryto limit