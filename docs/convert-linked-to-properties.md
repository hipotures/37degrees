# Konwersja systemu Linked Lists → Properties

## Cel i zamysł

**Problem:** Obecny system używa par list (Sequential + Linked) do śledzenia statusów operacji:
- Lista Sequential (`[BOOK_FOLDER]`) - generowanie obrazów AI 
- Lista Linked (`[BOOK_FOLDER]-download`) - pobieranie wygenerowanych obrazów

**Rozwiązanie:** Konwersja na system properties w pojedynczych listach Sequential:
- `image_generated` - status generowania obrazu
- `image_downloaded` - status pobierania obrazu

**Korzyści:**
- Uproszczenie struktury (1 lista zamiast 2)
- Łatwość dodawania kolejnych operacji jako properties
- Lepsze śledzenie stanu każdego itemu w jednym miejscu
- Zachowanie wszystkich funkcjonalności

## Proces konwersji

### Etapy (skrypt `convert-linked-to-properties.sh`):

1. **analyze** - Analiza obecnego stanu par Sequential/Linked
2. **backup** - Backup wszystkich danych do JSON
3. **convert** - Mapowanie statusów na properties
4. **verify** - Weryfikacja konwersji
5. **test** - Test systemu properties
6. **cleanup** - Usunięcie wszystkich Linked lists
7. **sync** - Synchronizacja statusów głównych z properties

### Mapowanie statusów:

**Z Sequential list → property `image_generated`:**
- ⏳ (pending) → `"pending"`
- 🔄 (in_progress) → `"in_progress"`
- ✅ (completed) → `"completed"`
- ❌ (failed) → `"failed"`

**Z Linked list → property `image_downloaded`:**
- ⏳ (pending) → `"pending"`
- 🔄 (in_progress) → `"in_progress"`
- ✅ (completed) → `"completed"`
- ❌ (failed) → `"failed"`

**Status główny itemu (logika kombinacji):**
- `image_generated=completed` AND `image_downloaded=completed` → `completed`
- `image_generated=pending` AND `image_downloaded=pending` → `pending`
- `image_generated=failed` OR `image_downloaded=failed` → `failed`
- Pozostałe kombinacje → `in_progress`

## Zmiany dla skryptów/komend 37d

### 37d-c2.md (Style Applicator) - BEZ ZMIAN
- Pozostaje bez zmian
- Nadal tworzy listy Sequential z tagiem "37d"
- **Nie tworzy już Linked lists**

### 37d-c3.md (AI Image Generation Orchestrator) - ZMIANY

**PRZED konwersją:**
```javascript
// Sprawdź czy są pending zadania w Sequential list
next_task = mcp__todoit__todo_get_next_pending(list_key: "[BOOK_FOLDER]")
```

**PO konwersji:**
```javascript
// Sprawdź czy są zadania z image_generated != completed
// Filtruj po properties: image_generated = "pending" lub "in_progress"
next_task = mcp__todoit__todo_get_next_pending(list_key: "[BOOK_FOLDER]")

// Po ukończeniu generowania - ustaw property
mcp__todoit__todo_set_item_property(
  list_key: "[BOOK_FOLDER]",
  item_key: next_task.key,
  property_key: "image_generated",
  property_value: "completed"
)
```

### 37d-c4.md (Pobieranie obrazów) - ZNACZĄCE ZMIANY

**PRZED konwersją:**
```javascript
// Operacja na liście -download
const DOWNLOAD_LIST = "[BOOK_FOLDER]-download";
const next = await mcp__todoit__todo_get_next_pending({ list_key: DOWNLOAD_LIST });
```

**PO konwersji:**
```javascript
// Operacja na liście głównej - filtrowanie po properties
const SOURCE_LIST = "[BOOK_FOLDER]";

// Znajdź zadania gdzie image_generated=completed ale image_downloaded != completed
const allItems = await mcp__todoit__todo_get_list_items({ list_key: SOURCE_LIST });
const nextItem = allItems.items.find(item => {
  const imageGenerated = await mcp__todoit__todo_get_item_property({
    list_key: SOURCE_LIST, item_key: item.item_key, property_key: "image_generated"
  });
  const imageDownloaded = await mcp__todoit__todo_get_item_property({
    list_key: SOURCE_LIST, item_key: item.item_key, property_key: "image_downloaded"
  });
  
  return imageGenerated.property_value === "completed" && 
         imageDownloaded.property_value !== "completed";
});

// Po ukończeniu pobierania - ustaw property i status główny
await mcp__todoit__todo_set_item_property({
  list_key: SOURCE_LIST,
  item_key: nextItem.item_key,
  property_key: "image_downloaded", 
  property_value: "completed"
});

// Status główny zostanie automatycznie zsynchronizowany przez logikę kombinacji
// lub przez okresowe uruchomienie sync
```

### Nowe komendy pomocnicze - DODAJ

**Komenda do sprawdzania statusu properties:**
```javascript
// Pokaż status wszystkich properties dla książki
const items = await mcp__todoit__todo_get_list_items({ list_key: "[BOOK_FOLDER]" });
for (const item of items.items) {
  const imageGen = await mcp__todoit__todo_get_item_property({
    list_key: "[BOOK_FOLDER]", item_key: item.item_key, property_key: "image_generated"
  });
  const imageDl = await mcp__todoit__todo_get_item_property({
    list_key: "[BOOK_FOLDER]", item_key: item.item_key, property_key: "image_downloaded"  
  });
  
  console.log(`${item.item_key}: gen=${imageGen.property_value}, dl=${imageDl.property_value}`);
}
```

**Komenda do synchronizacji statusów (ręczna):**
```bash
# Uruchom synchronizację statusów głównych dla wszystkich list
./convert-linked-to-properties.sh sync
```

### Logika filtrowania zadań

**Zadania gotowe do generowania:**
```javascript
// image_generated = "pending" lub "in_progress"
const canGenerate = imageGenerated !== "completed";
```

**Zadania gotowe do pobierania:**
```javascript  
// image_generated = "completed" AND image_downloaded != "completed"
const canDownload = imageGenerated === "completed" && imageDownloaded !== "completed";
```

**Zadania całkowicie ukończone:**
```javascript
// image_generated = "completed" AND image_downloaded = "completed"
const fullyCompleted = imageGenerated === "completed" && imageDownloaded === "completed";
```

## Weryfikacja po konwersji

1. **Sprawdź properties na sample liście:**
```bash
todoit item property list [BOOK_FOLDER] --tree
```

2. **Sprawdź statusy główne:**
```bash
todoit list show [BOOK_FOLDER]
```

3. **Sprawdź czy nie ma już Linked lists:**
```bash
todoit list all | grep "L.*-download"  # Powinno być puste
```

4. **Test workflow:**
```javascript
// Test czy można znaleźć zadania do pobierania
const nextDownload = // logika filtrowania po properties
```

## Rollback (jeśli potrzebny)

Wszystkie dane są zbackupowane w `backup_YYYYMMDD_HHMMSS/`:
- Można przywrócić listy z JSON
- Można odtworzyć Linked lists z backup
- Properties można usunąć przed rollback

## Status po konwersji

✅ **Ukończone:**
- System properties zastępuje Linked lists
- Logika kombinacji properties → status główny
- Backup wszystkich danych
- Weryfikacja poprawności konwersji

⚠️ **Do aktualizacji:**
- Komendy 37d-c3, 37d-c4 - logika filtrowania
- Ewentualne custom skrypty używające Linked lists
- Dokumentacja systemu