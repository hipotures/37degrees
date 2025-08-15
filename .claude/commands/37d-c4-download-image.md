---
name: 37d-c4-download-image
description: |
  Automates image download process from ChatGPT using MCP playwright-headless and TODOIT subtasks.
  Processes image_dwn subtasks by finding scenes where image_gen is completed but image_dwn is pending.
  Downloads generated images, saves file paths, and updates subtask status.
execution_order: 4
min_tasks: 1
max_tasks: 1
todo_list: true
---

**UWAGA:** `todo_list: true` oznacza że system ma używać **MCP TODOIT** do zarządzania zadaniami i subtaskami.

# Custom Instruction: AI Image Download from ChatGPT (Subtasks Version)

Proces automatycznego pobierania obrazów z ChatGPT używając systemu subtasks.

UWAGA: Używaj MCP playwright-headless i todoit subtasks do automatyzacji

## Dane wejściowe:

- Projekt: "[BOOK_FOLDER]" (np. "0031_solaris")

Wykonaj dokładnie tak, jak są zapisane i w takiej samej kolejności kolejne kroki

### 0. Odczytaj konfigurację i znajdź zadanie

```javascript
// Odczytaj Project ID z właściwości listy
const projectId = await mcp__todoit__todo_get_list_property({
  list_key: "[BOOK_FOLDER]",
  property_key: "project_id"
});

if (!projectId.success) {
  console.log("ERROR: Project ID not found in list properties");
  return;
}

console.log(`Project ID: ${projectId.property_value}`);
```

###  Step 1. Znajdź następne zadanie do pobrania

```javascript

const readyDownloadTasks = await mcp__todoit__todo_find_subitems_by_status({
  list_key: "[BOOK_FOLDER]",
  conditions: {
    "image_gen": "completed",
    "image_dwn": "pending"
  },
  limit: 1
});

if (!readyDownloadTasks.success || readyDownloadTasks.items.length === 0) {
  console.log("No image_dwn subtasks ready for processing");
  return;
}

const nextTask = readyDownloadTasks.items[0];
const sceneKey = nextTask.parent_key;          // np. "scene_0001"
const imageDwnSubtaskKey = nextTask.item_key;  // np. "scene_0001_image_dwn"

console.log(`Processing ${sceneKey} for image download`);
```

###  Step 2. Odczytaj Thread ID z właściwości

```javascript
// Znajdź odpowiedni image_gen subtask aby odczytać thread_id
const imageGenSubtaskKey = imageDwnSubtaskKey.replace('_image_dwn', '_image_gen');

const threadIdProperty = await mcp__todoit__todo_get_item_property({
  list_key: "[BOOK_FOLDER]",
  item_key: imageGenSubtaskKey,
  property_key: "thread_id"
});

if (!threadIdProperty.success) {
  throw new Error(`Thread ID not found for ${sceneKey}`);
}

const threadId = threadIdProperty.property_value;
console.log(`Thread ID: ${threadId}`);

// Zbuduj bezpośredni URL do chatu
const chatUrl = `https://chatgpt.com/g/${projectId.property_value}/c/${threadId}`;
console.log(`Chat URL: ${chatUrl}`);
```

###  Step 3. Bezpośrednia nawigacja do chatu

```javascript
// CRITICAL: Nawiguj bezpośrednio do URL chatu złożonego z Project ID i Thread ID
await mcp__playwright-headless__browser_navigate({ url: chatUrl });

// Poczekaj na załadowanie chatu
await mcp__playwright-headless__browser_wait_for({ time: 3 });
```

###  Step 4. Pobierz wszystkie obrazy z chatu

```javascript
// Zrób snapshot aby zobaczyć strukturę chatu
await mcp__playwright-headless__browser_snapshot();

// CRITICAL: Chat może mieć 3 typy sytuacji:
// 1. Single obraz - jeden prompt, jedna odpowiedź, jeden "Download this image"
// 2. Multiple odpowiedzi - jeden prompt, X/Y responses, "Previous/Next response" buttons
// 3. Multiple prompty - kilka promptów użytkownika w jednym chacie
// 4. KOMBINACJA - kilka promptów, niektóre z multiple odpowiedziami

// ALGORYTM: Przewiń przez CAŁY chat i pobierz wszystkie obrazy

try {
  // Sprawdź czy są przyciski "Previous response" / "Next response"
  const hasMultipleResponses = await mcp__playwright-headless__browser_evaluate({
    function: `() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.some(btn => {
        const label = btn.getAttribute('aria-label') || '';
        return label.includes('Previous response') || label.includes('Next response');
      });
    }`
  });

  if (hasMultipleResponses) {
    // Multiple odpowiedzi na ten sam prompt - SEPARATE CLICKS APPROACH
    // CRITICAL: ChatGPT domyślnie pokazuje ostatnią odpowiedź (2/2, 3/3, etc.)
    
    // KROK 1: Pobierz obraz z AKTUALNEJ odpowiedzi (ostatniej: 2/2)
    try {
      await mcp__playwright-headless__browser_click({
        element: "Download this image button",
        ref: "REF_FROM_SNAPSHOT"
      });
    } catch (error) {
      console.log("Błąd pobierania obrazu z ostatniej odpowiedzi:", error);
    }
    
    // KROK 2: Przejdź do PIERWSZEJ odpowiedzi i pobierz z niej
    const movedToPrevious = await mcp__playwright-headless__browser_evaluate({
      function: `() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        const prevButton = buttons.find(btn => {
          const label = btn.getAttribute('aria-label') || '';
          return label.includes('Previous response');
        });
        if (prevButton && !prevButton.disabled) {
          prevButton.click();
          return true;
        }
        return false;
      }`
    });
    
    if (movedToPrevious) {
      await mcp__playwright-headless__browser_wait_for({ time: 2 });
      
      // KROK 3: Pobierz obraz z pierwszej odpowiedzi (1/2)
      try {
        await mcp__playwright-headless__browser_click({
          element: "Download this image button",
          ref: "REF_FROM_SNAPSHOT"
        });
      } catch (error) {
        console.log("Błąd pobierania obrazu z pierwszej odpowiedzi:", error);
      }
    }
    
    // UWAGA: Ten algorytm działa dla 2 odpowiedzi (1/2, 2/2)
    // Dla więcej odpowiedzi trzeba rozszerzyć logikę
    
  } else {
    // Single odpowiedź - pobierz wszystkie obrazy z tej sekcji
    try {
      await mcp__playwright-headless__browser_click({
        element: "Download this image button",
        ref: "REF_FROM_SNAPSHOT"
      });
    } catch (error) {
      console.log("Błąd pobierania obrazu:", error);
    }
  }
  
  // POWTARZAJ dla każdej sekcji "ChatGPT said:" w chacie
  // WSZYSTKIE obrazy z chatu dotyczą tej samej sceny (numer z YAML)
  
  // Poczekaj na pobranie
  await mcp__playwright-headless__browser_wait_for({ time: 5 });

} catch (error) {
  console.log(`Błąd podczas pobierania obrazów: ${error.message}`);
}
```

###  Step 5. Przenieś i nazwij pliki

```javascript
// Znajdź pobrane pliki
const downloadsDir = "/tmp/playwright-mcp-files/headless/";

const downloadCheck = await Bash({
  command: `ls -t ${downloadsDir}ChatGPT-Image*.png 2>/dev/null | head -5`,
  description: "List downloaded ChatGPT images"
});

if (!downloadCheck || downloadCheck.includes("No such file")) {
  console.log("Brak pobranych plików");
  
  // Oznacz jako failed
  await mcp__todoit__todo_update_item_status({
    list_key: "[BOOK_FOLDER]",
    item_key: imageDwnSubtaskKey,
    status: "failed"
  });
  
  await mcp__todoit__todo_set_item_property({
    list_key: "[BOOK_FOLDER]",
    item_key: imageDwnSubtaskKey,
    property_key: "ERROR",
    property_value: "No downloaded files found"
  });
  
  await mcp__playwright-headless__browser_close();
  return;
}

// WYMAGANE: Odczytaj docelową ścieżkę z properties subtaska
// Ścieżka musi być już ustawiona w formacie: books/xxx/images/xxxx_scene_0001.png
const existingPathProperty = await mcp__todoit__todo_get_item_property({
  list_key: "[BOOK_FOLDER]",
  item_key: imageDwnSubtaskKey,
  property_key: "dwn_pathfile"
});

if (!existingPathProperty.success || !existingPathProperty.property_value) {
  console.log(`ERROR: dwn_pathfile property not found for ${imageDwnSubtaskKey}`);
  console.log("This indicates the subtask was not properly initialized by previous agents");
  
  // Oznacz jako failed
  await mcp__todoit__todo_update_item_status({
    list_key: "[BOOK_FOLDER]",
    item_key: imageDwnSubtaskKey,
    status: "failed"
  });
  
  await mcp__todoit__todo_set_item_property({
    list_key: "[BOOK_FOLDER]",
    item_key: imageDwnSubtaskKey,
    property_key: "ERROR",
    property_value: "dwn_pathfile property missing - subtask not properly initialized"
  });
  
  await mcp__playwright-headless__browser_close();
  return;
}

const targetPath = `/home/xai/DEV/37degrees/${existingPathProperty.property_value}`;
console.log(`Using target path from properties: ${targetPath}`);

Wykonaj polecenie bash wstawiajac odpowiednie wartosci:
Bash({
  command: `
    i=0
    for sourceFile in $(ls -t ${downloadsDir}ChatGPT-Image*.png 2>/dev/null); do
      if [ $i -eq 0 ]; then
        finalTarget="${targetPath}"
      else
        finalTarget="${targetPath%.png}_${i}.png"
      fi
      
      if [[ -f "$finalTarget" ]]; then
        mv "$sourceFile" "\${finalTarget%.png}_$(uuidgen -r | cut -d- -f1).png"
      else
        mv "$sourceFile" "$finalTarget"
      fi
      
      echo "✅ Moved: $(basename "$sourceFile") -> $(basename "$finalTarget")"
      i=$((i+1))
    done
  `,
  description: "Move downloaded images with UUID on conflict"
});

console.log(`Image download process completed for ${sceneKey}`);

```

###  Step 6. Finalizacja zadania

```javascript
// Oznacz image_dwn subtask jako completed
await mcp__todoit__todo_update_item_status({
  list_key: "[BOOK_FOLDER]",
  item_key: imageDwnSubtaskKey,
  status: "completed"
});

console.log(`✅ ${sceneKey} image download completed`);

```

###  Step 7. Zamknij przeglądarkę

```javascript
// CRITICAL: Zawsze zamknij browser aby uniknąć konfliktów
await mcp__playwright-headless__browser_close();
```

## Weryfikacja sukcesu:

- Plik obrazu został zapisany w `/books/[BOOK_FOLDER]/images/`
- Nazwa pliku: `[BOOK_FOLDER]_scene_[NNNN].png` (np. `0031_solaris_scene_0001.png`)
- Nie nadpisano istniejących plików (używa UUID przy konflikcie nazw)
- image_dwn subtask ma status `completed`
- Dla chatów z multiple odpowiedziami: 2 różne pliki PNG pobrane (różne rozmiary)

## System statusów subtasks:

- **completed** - subtask ukończony pomyślnie ✅
- **failed** - subtask nieudany ❌

**Uwaga:** Subtaski NIE używają statusu `in_progress` dla krótkich operacji. 
Pozostają `pending` podczas przetwarzania, a następnie przechodzą bezpośrednio 
do `completed` lub `failed`. To zapewnia czysty restart po przerwaniu procesu.

## Uwagi techniczne:

- **Źródło danych:** Project ID z list properties, Thread ID z item properties
- **Format URL:** `https://chatgpt.com/g/[PROJECT_ID]/c/[THREAD_ID]`
- **ZAWSZE** używaj browser_snapshot() przed klikaniem
- **NIGDY** nie używaj hardcoded refs - tylko rzeczywiste z snapshot
- **Zamknij browser** na końcu (zapobiega konfliktom)
- **Multiple odpowiedzi:** używaj SEPARATE CLICKS zamiast atomic evaluate
- **Przyciski** wykrywaj przez aria-label, nie textContent
