---
name: 37d-c4-todoit
description: |
  Pobieranie obrazów z ChatGPT na TODOIT (Properties).
  Automatyzuje proces pobierania wygenerowanych obrazów z ChatGPT używając MCP playwright-headless i TODOIT properties.
  Przetwarza zadania gotowe do pobrania i zarządza organizacją plików.
execution_order: 4
min_tasks: 1
max_tasks: 1
todo_list: true
---

# 37d‑c4‑todoit — Pobieranie obrazów z ChatGPT na TODOIT (Properties)

Agent worker dla pobierania pojedynczego obrazu z ChatGPT używając systemu TODOIT properties

UWAGA: Używaj MCP todoit i playwright-headless do automatyzacji

## Wejście i założenia

- **Na wejsciu musi być podany BOOK_FOLDER (przykład: 0009_fahrenheit_451)** - jeśli nie ma, zakończ działanie z odpowiednim komunikatem
- **SOURCE_LIST**: `[BOOK_FOLDER]` (lista źródłowa z systemem properties)
- **Właściwości listy SOURCE**:
  - `book_folder = [BOOK_FOLDER]`
  - `project_id = g-p-...` (ID projektu ChatGPT)
- **Właściwości pozycji w SOURCE**:
  - `thread_id = ...` (ID czatu dla danej sceny)
  - `image_generated = completed|pending|in_progress|failed` (status generowania)
  - `image_downloaded = completed|pending|in_progress|failed` (status pobierania)
- **Nazewnictwo plików**: `[BOOK_FOLDER]_scene_[NN].png`, `[BOOK_FOLDER]_scene_[NN]_a.png`, ...

> Jeśli nie masz `project_id` lub `thread_id`, zatrzymaj się i napraw stan w 37d‑a3.

## Algorytm (Properties)

### 0) Ustal kontekst

```javascript
// Wejście operacyjne
const SOURCE_LIST = "[BOOK_FOLDER]";

// Właściwości listy źródłowej
const bookFolder = await mcp__todoit__todo_get_list_property({
  list_key: SOURCE_LIST, property_key: "book_folder"
});
const projectId = await mcp__todoit__todo_get_list_property({
  list_key: SOURCE_LIST, property_key: "project_id"
});
if (!bookFolder.success || !projectId.success) { 
  throw new Error("Brak book_folder albo project_id w właściwościach listy"); 
}
```

### 1) Znajdź następne zadanie do pobrania

```javascript
// OPTYMALIZOWANA funkcja do znajdowania następnego zadania do pobrania
const nextTask = await findNextDownloadTask(SOURCE_LIST);

if (!nextTask) {
  console.log("Brak zadań gotowych do pobrania (pending download + completed generation)"); 
  return; 
}

const sceneKey = nextTask.item_key;          // np. "scene_01"
const threadId = nextTask.thread_id;
const chatUrl = `https://chatgpt.com/g/${projectId.property_value}/c/${threadId}`;

console.log(`Pobieranie obrazu dla zadania: ${sceneKey}, Thread: ${threadId}`);

// Oznacz jako in_progress
await mcp__todoit__todo_set_item_property({
  list_key: SOURCE_LIST, 
  item_key: sceneKey, 
  property_key: "image_downloaded", 
  property_value: "in_progress"
});
```

### 2) Wejdź w czat i zrzutuj wszystkie obrazy

```javascript
await mcp__playwright-headless__browser_navigate({ url: chatUrl });
await mcp__playwright-headless__browser_wait_for({ time: 5 });
await mcp__playwright-headless__browser_snapshot();

// Pobieranie: pojedyncze odpowiedzi - kliknij download
try {
  await mcp__playwright-headless__browser_click({ element: "Download this image button", ref: "REF_FROM_SNAPSHOT" });
} catch (error) {
  console.log("Błąd pobierania obrazu:", error);
}

// Pobieranie: odpowiedzi wielokrotne (Previous/Next)
let moved;
do {
  // Spróbuj cofnąć do pierwszej odpowiedzi i pobrać
  moved = await mcp__playwright-headless__browser_evaluate({
    function: `() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const prev = buttons.find(b => (b.getAttribute('aria-label')||'').includes('Previous response'));
      if (prev && !prev.disabled) { prev.click(); return true; }
      return false;
    }`
  });
  
  if (moved) {
    await mcp__playwright-headless__browser_wait_for({ time: 2 });
    try {
      await mcp__playwright-headless__browser_click({ element: "Download this image button", ref: "REF_FROM_SNAPSHOT" });
    } catch (error) {
      console.log("Błąd pobierania obrazu z poprzedniej odpowiedzi:", error);
    }
  }
} while (moved === true);

// Poczekaj na pobranie
await mcp__playwright-headless__browser_wait_for({ time: 5 });
```

### 3) Przenieś i nazwij pliki

```javascript
// Znajdź pobrane pliki w katalogu MCP
const downloadsDir = "/tmp/playwright-mcp-files/headless/";
const downloads = await Bash({
  command: `ls -t ${downloadsDir}ChatGPT-Image*.png 2>/dev/null || echo "BRAK_PLIKOW"`,
  description: "List downloaded ChatGPT images"
});

if (downloads.includes("BRAK_PLIKOW")) {
  console.log("Brak pobranych plików");
  
  // Oznacz jako failed
  await mcp__todoit__todo_set_item_property({
    list_key: SOURCE_LIST, 
    item_key: sceneKey, 
    property_key: "image_downloaded", 
    property_value: "failed"
  });
  
  await mcp__playwright-headless__browser_close();
  return;
}

// Wyciągnij numer sceny z klucza zadania
const sceneNum = sceneKey.replace('scene_', '').padStart(2, '0');
const baseName = `${bookFolder.property_value}_scene_${sceneNum}`;
const destDir = `/home/xai/DEV/37degrees/books/${bookFolder.property_value}/generated`;

// Utwórz katalog jeśli nie istnieje
await Bash({
  command: `mkdir -p "${destDir}"`,
  description: "Create destination directory"
});

// Przenieś wszystkie pobrane pliki z unikalnymi nazwami
const downloadedFiles = downloads.split('\n').filter(f => f.includes('ChatGPT-Image'));
const savedFiles = [];

for (const [index, file] of downloadedFiles.entries()) {
  let finalName = `${baseName}.png`;
  
  // Jeśli plik już istnieje, użyj sufixu _a, _b, _c...
  if (index > 0 || await fileExists(`${destDir}/${finalName}`)) {
    const suffix = String.fromCharCode(97 + index); // a, b, c...
    finalName = `${baseName}_${suffix}.png`;
  }
  
  const sourcePath = `${downloadsDir}${file.trim()}`;
  const destPath = `${destDir}/${finalName}`;
  
  try {
    await Bash({
      command: `mv "${sourcePath}" "${destPath}"`,
      description: `Move image to ${finalName}`
    });
    savedFiles.push(finalName);
  } catch (error) {
    console.log(`Błąd przenoszenia pliku ${file}:`, error);
  }
}

console.log(`Zapisano pliki: ${savedFiles.join(', ')}`);
```

### 4) Aktualizacje w TODOIT

```javascript
// Oznacz pobieranie jako ukończone
await mcp__todoit__todo_set_item_property({
  list_key: SOURCE_LIST, 
  item_key: sceneKey, 
  property_key: "image_downloaded", 
  property_value: "completed"
});

// Sprawdź czy wszystkie etapy ukończone i ustaw status główny
await syncMainStatus(SOURCE_LIST, sceneKey);

console.log(`Zadanie ${sceneKey} ukończone pomyślnie`);
```

### 5) Sprzątanie

```javascript
await mcp__playwright-headless__browser_close();
```

## Funkcje pomocnicze

### Filtrowanie zadań gotowych do pobrania

```javascript
async function findNextDownloadTask(sourceList) {
  // Pobierz wszystkie properties jednym wywołaniem
  const allItemsProperties = await mcp__todoit__todo_get_all_items_properties({
    list_key: sourceList,
    status: "in_progress"  // zadania w trakcie
  });
  
  if (!allItemsProperties.success || allItemsProperties.count === 0) {
    return null;
  }
  
  // Znajdź pierwsze zadanie gotowe do pobrania
  for (const itemProps of allItemsProperties.properties) {
    const properties = itemProps.properties;
    
    const downloadStatus = properties.find(p => p.property_key === "image_downloaded")?.property_value;
    const generateStatus = properties.find(p => p.property_key === "image_generated")?.property_value;
    const threadIdProperty = properties.find(p => p.property_key === "thread_id")?.property_value;
    
    if (downloadStatus === "pending" && generateStatus === "completed" && threadIdProperty) {
      return {
        item_key: itemProps.item_key,
        thread_id: threadIdProperty,
        download_status: downloadStatus,
        generate_status: generateStatus
      };
    }
  }
  
  return null;
}
```

### Status główny na podstawie properties

```javascript
async function syncMainStatus(sourceList, itemKey) {
  // Pobierz wszystkie properties dla zadania
  const allItemsProperties = await mcp__todoit__todo_get_all_items_properties({
    list_key: sourceList,
    status: "in_progress"
  });
  
  const itemProps = allItemsProperties.properties?.find(item => item.item_key === itemKey);
  if (!itemProps) {
    throw new Error(`Zadanie ${itemKey} nie znalezione`);
  }
  
  const properties = itemProps.properties;
  const genStatus = properties.find(p => p.property_key === "image_generated")?.property_value || "pending";
  const dlStatus = properties.find(p => p.property_key === "image_downloaded")?.property_value || "pending";
  
  let mainStatus;
  if (genStatus === "failed" || dlStatus === "failed") {
    mainStatus = "failed";
  } else if (genStatus === "completed" && dlStatus === "completed") {
    mainStatus = "completed";
  } else if (genStatus === "pending" && dlStatus === "pending") {
    mainStatus = "pending";
  } else {
    mainStatus = "in_progress";
  }
  
  await mcp__todoit__todo_update_item_status({
    list_key: sourceList, 
    item_key: itemKey, 
    status: mainStatus
  });
}

async function fileExists(filePath) {
  try {
    const result = await Bash({
      command: `test -f "${filePath}" && echo "EXISTS" || echo "NOT_EXISTS"`,
      description: "Check if file exists"
    });
    return result.includes("EXISTS");
  } catch (error) {
    return false;
  }
}
```

## Uwagi techniczne

- **Worker przetwarza TYLKO JEDNO zadanie na wywołanie**
- **BOOK_FOLDER jest przekazywany jako SOURCE_LIST**
- **Używa systemu properties TODOIT do zarządzania stanem**
- **Bezpośrednia nawigacja do chatu przez URL złożony z PROJECT_ID + THREAD_ID**
- **Nie nadpisuje istniejących plików - używa sufiksów _a, _b, _c...**
- **CRITICAL: Zawsze zamknij browser aby uniknąć konfliktów**
- **Format plików: [BOOK_FOLDER]_scene_[NN].png**

## Weryfikacja sukcesu

- Plik obrazu został zapisany w `/books/[BOOK_FOLDER]/generated/`
- Nazwa pliku: `[BOOK_FOLDER]_scene_[NN].png` 
- Nie nadpisano istniejących plików
- Property `image_downloaded` ustawione na `completed`
- Status główny zadania zaktualizowany zgodnie z kombinacją properties
- Bezpośrednia nawigacja do chatu bez przechodzenia przez sidebar

## System statusów properties

- `image_generated=completed` + `image_downloaded=completed` → status: `completed`
- `image_generated=completed` + `image_downloaded=pending` → status: `in_progress` 
- `image_generated=failed` OR `image_downloaded=failed` → status: `failed`
- `image_generated=pending` + `image_downloaded=pending` → status: `pending`