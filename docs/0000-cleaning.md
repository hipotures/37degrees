# Procedura przenoszenia chatów ChatGPT do właściwych projektów

## Problem
W projekcie "0000" znajdują się chaty, które z jakiegoś powodu nie zostały przypisane do właściwych projektów książek. Chaty te powinny być przeniesione do odpowiednich projektów na podstawie ich zawartości.

## Procedura przenoszenia chatów

### 1. Pobranie Thread ID z ChatGPT

- Z interfejsu ChatGPT (projekt "0000") skopiuj Thread ID z URL chatu
- Format Thread ID: `68af27c0-2b0c-8328-aba2-12cd822c388f`
- Thread ID znajduje się w URL po `/c/`: `https://chatgpt.com/g/[PROJECT_ID]/c/[THREAD_ID]`

### 2. Identyfikacja właściwego projektu za pomocą TODOIT

```javascript
// Wyszukaj w TODOIT właściwą listę na podstawie Thread ID
const result = await mcp__todoit__todo_find_items_by_property(
  null,                                           // przeszukaj wszystkie listy
  "thread_id",                                   // klucz property
  "68af27c0-2b0c-8328-aba2-12cd822c388f",       // Thread ID z ChatGPT URL
  1                                              // limit wyników
);

// Wynik zawiera:
// - list_key: "0067_the_gulag_archipelago" (docelowy projekt ChatGPT)
// - parent_item_key: "scene_0020" (scena)
// - item_key: "image_gen" (subitem)
```

### 3. Mapowanie List Key na Projekt ChatGPT

**Reguła**: List Key z TODOIT = Nazwa Projektu ChatGPT

- `0067_the_gulag_archipelago` → Projekt ChatGPT: `0067_the_gulag_archipelago`
- `0053_the_scarlet_letter` → Projekt ChatGPT: `0053_the_scarlet_letter`
- itd.

### 4. Przeniesienie chatu w ChatGPT (ręcznie)

1. **Wejdź do chatu** w projekcie "0000"
2. **Kliknij "..." (menu opcji)** w prawym górnym rogu chatu
3. **Wybierz "Move to project"** z menu dropdown
4. **Znajdź i kliknij** właściwy projekt z listy rozwijanej:
   - Nazwa projektu = `list_key` z wyniku TODOIT
   - Np. `0067_the_gulag_archipelago`
5. **Potwierdź przeniesienie**

### 5. Weryfikacja

Po przeniesieniu sprawdź:
- Chat zniknął z projektu "0000"
- Chat pojawił się we właściwym projekcie książki
- Thread ID pozostał bez zmian
- URL zmienił się na: `https://chatgpt.com/g/[NEW_PROJECT_ID]/c/[THREAD_ID]`

## Przykład kompletny

**Thread ID z URL**: `68af27c0-2b0c-8328-aba2-12cd822c388f`

**Wyszukanie w TODOIT**:
```javascript
todo_find_items_by_property(null, "thread_id", "68af27c0-2b0c-8328-aba2-12cd822c388f", 1)
```

**Wynik**:
- `list_key`: `0067_the_gulag_archipelago`
- `parent_item_key`: `scene_0020`
- Chat dotyczy sceny 20 z książki "The Gulag Archipelago"

**Akcja**: Przenieś chat do projektu `0067_the_gulag_archipelago`

## Uwagi techniczne

- Thread ID nigdy się nie zmienia po przeniesieniu
- Project ID w URL zmieni się na nowy projekt
- Wszystkie załączniki (pliki YAML) pozostaną nienaruszone
- Historia chatu zostaje zachowana
- Properties w TODOIT nie wymagają aktualizacji (Thread ID pozostaje ten sam)

## Automatyzacja z CDP (Chrome DevTools Protocol)

### Alternatywa: Automatyczne przenoszenie z playwright-cdp

Zamiast ręcznego przenoszenia można użyć MCP playwright-cdp do automatyzacji:

#### 1. Połączenie z projektem 0000
```javascript
// Otwórz projekt 0000 w CDP
await mcp__playwright-cdp__browser_navigate({
  url: "https://chatgpt.com/g/g-p-68b0f4e5fdc881919dceaf90e75ab5c9-0000/project"
});
```

#### 2. Identyfikacja Thread ID z listy chatów
```javascript
// Pobierz snapshot strony z listą chatów
const snapshot = await mcp__playwright-cdp__browser_snapshot();

// Thread ID znajduje się w URL linków chatów w formacie:
// /g/g-p-[PROJECT_ID]/c/[THREAD_ID]
// Np: /g/g-p-68b0f4e5fdc881919dceaf90e75ab5c9-0000/c/68aa2a03-0d84-8331-8c33-71200500bb43

// Wyciągnij wszystkie Thread ID z widocznych linków chatów
```

#### 3. Wyszukanie docelowego projektu dla Thread ID
```javascript
// Dla każdego Thread ID wyszukaj w TODOIT właściwy projekt
const threadId = "68aa2a03-0d84-8331-8c33-71200500bb43"; // przykład

const result = await mcp__todoit__todo_find_items_by_property(
  null,                    // przeszukaj wszystkie listy
  "thread_id",            // klucz property
  threadId,               // Thread ID z URL chatu
  1                       // limit wyników
);

if (result.success && result.items.length > 0) {
  const targetProject = result.items[0].list_key;
  console.log(`Thread ${threadId} należy do projektu: ${targetProject}`);
}
```

#### 4. Automatyczne przeniesienie chatu
```javascript
// Jeśli znaleziono właściwy projekt - automatycznie przenieś
if (result.success && result.items.length > 0) {
  const targetProject = result.items[0].list_key;
  
  // Wejdź do chatu
  await mcp__playwright-cdp__browser_navigate({
    url: `https://chatgpt.com/g/g-p-68b0f4e5fdc881919dceaf90e75ab5c9-0000/c/${threadId}`
  });
  
  // Kliknij menu opcji chatu (3 kropki)
  await mcp__playwright-cdp__browser_click({
    element: "Open conversation options",
    ref: "REF_FROM_SNAPSHOT"
  });
  
  // Wybierz "Move to project"
  await mcp__playwright-cdp__browser_click({
    element: "Move to project option", 
    ref: "REF_FROM_SNAPSHOT"
  });
  
  // Znajdź i kliknij docelowy projekt na liście
  await mcp__playwright-cdp__browser_click({
    element: targetProject,
    ref: "REF_FROM_SNAPSHOT"
  });
  
  console.log(`✅ Moved chat ${threadId} to project ${targetProject}`);
}
```

#### 5. Pętla dla wszystkich chatów
```javascript
// Automatycznie przetworz wszystkie chaty z projektu 0000
const allThreadIds = []; // wyciągnięte z snapshot

for (const threadId of allThreadIds) {
  // Wyszukaj docelowy projekt
  const result = await mcp__todoit__todo_find_items_by_property(null, "thread_id", threadId, 1);
  
  if (result.success && result.items.length > 0) {
    // Przenieś chat automatycznie
    // ... kod przenoszenia z punktu 4
  } else {
    console.log(`⚠️  Thread ${threadId} not found in TODOIT - requires manual review`);
  }
}
```

## Lista chatów do sprawdzenia

Wszystkie chaty z projektu "0000" powinny zostać przeanalizowane i przeniesione do właściwych projektów na podstawie ich Thread ID i odpowiadających im wpisów w TODOIT.

**Metoda identyfikacji:**
1. Otwórz projekt 0000 przez CDP
2. Pobierz snapshot z listą chatów  
3. Wyciągnij Thread ID z URL linków (format: `/c/[THREAD_ID]`)
4. Dla każdego Thread ID użyj `todo_find_items_by_property` do znalezienia `list_key`
5. Automatycznie przenieś chat do znalezionego projektu lub oznacz do ręcznego sprawdzenia