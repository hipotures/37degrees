---
name: 37d-a5-gemini-deep-research
description: |
    Ten agent automatyzuje proces Deep Research w Google Gemini dla książek z projektu 37degrees.
    Proces obejmuje:
     - otwarcie przeglądarki,
     - aktywację Deep Research,
     - wklejenie instrukcji z pliku prompt,
     - zmianę nazwy czatu
     - oczekiwanie na rozpoczęcie procesu badawczego
---

# Gemini Deep Research - Instrukcja automatyzacji

## Parametry wejściowe
- `book_folder` - nazwa folderu książki (np. `0026_pride_and_prejudice`)


## Wymagania wstępne
- Powinieneś być zalogowant do Google Gemini w przeglądarce. Jeśli wykryjesz brak zalogowania się do Google, przerywasz działanei z odpowiednim komunikatem.
- Folder książki z plikiem `books/[book_folder]/docs/book-ds-prompt.md`
- MCP playwright-headless (domyślnie) lub playwright-show-browser (jeśli użytkownik wyraźnie o to poprosi)

## KRYTYCZNE ZASADY OSZCZĘDZANIA TOKENÓW
- **NIE UŻYWAJ Read tool** - nie czytaj pliku `book-ds-prompt.md` (555 linii = tysiące tokenów)
- **NIE UŻYWAJ TodoWrite** - ten agent nie potrzebuje systemu zadań
- **UŻYWAJ TYLKO xsel + Control+V** - zero tokenów


## Proces automatyzacji

### 1. Sprawdź istnienie pliku (BEZ CZYTANIA)
```bash
# Sprawdź czy plik istnieje (nie czytaj zawartości!)
test -f books/${book_folder}/docs/book-ds-prompt.md && echo "Plik istnieje" || echo "Brak pliku"
```

### 2. Otwórz Google Gemini
```javascript
// Nawiguj do Google Gemini
// Domyślnie używaj playwright-headless, chyba że użytkownik wyraźnie prosi o playwright-show-browser
await mcp__playwright-headless__browser_navigate("https://gemini.google.com/")
```

### 3. Aktywuj Deep Research
```javascript
// Znajdź i kliknij przycisk Deep Research
const deepResearchButton = page.locator('button:has-text("Deep Research")');
await deepResearchButton.click();
```

### 4. Wklej instrukcje (OPTYMALNA METODA - ZERO TOKENÓW)

**WAŻNE: NIE CZYTAJ PLIKU - wklej go bezpośrednio używając xsel**

```bash
# Wczytaj plik do schowka systemowego (bez czytania zawartości w Claude Code)
cat books/${book_folder}/docs/book-ds-prompt.md | xsel --clipboard

# Skupienie na polu tekstowym i wklejenie
await page.getByRole('textbox', { name: 'Tu wpisz prompt' }).click();
await page.keyboard.press('Control+v');
```

### 5. Wyślij instrukcje
```javascript
// Wyślij wiadomość
await page.keyboard.press('Enter');
// LUB kliknij przycisk send
const sendButton = page.locator('button[data-testid="send-button"]');
await sendButton.click();
```

### 6. Czekaj na przygotowanie planu
```javascript
// Czekaj aż Gemini przygotuje plan badawczy
await page.waitForSelector('button:has-text("Zacznij wyszukiwanie")', { timeout: 60000 });
```

### 7. Rozpocznij wyszukiwanie
```javascript
// Kliknij "Zacznij wyszukiwanie"
const startButton = page.locator('button:has-text("Zacznij wyszukiwanie")');
await startButton.click();
```

### 8. Zmień nazwę czatu (po rozpoczęciu wyszukiwania)
```javascript
// Wróć do czatu
const backButton = page.locator('button:has(img[title="chevron_left"])');
await backButton.click();

// Otwórz menu opcji
const moreButton = page.locator('button:has(img[title="more_vert"])');
await moreButton.click();

// Kliknij "Zmień nazwę"
const renameButton = page.locator('button:has-text("Zmień nazwę")');
await renameButton.click();

// Wprowadź nową nazwę
const nameInput = page.locator('input[type="text"]');
await nameInput.fill(book_folder);

// Potwierdź zmianę
const confirmButton = page.locator('button:has-text("Zmień nazwę")');
await confirmButton.click();
```

### 9. Monitoruj postęp
```javascript
// Monitoruj status Deep Research
const statusSelector = 'div:has-text("Analizuję treść")';
await page.waitForSelector(statusSelector, { timeout: 5000 });

// Opcjonalnie: czekaj na ukończenie (może trwać kilka minut)
const completionSelector = 'div:has-text("Gotowe")';
await page.waitForSelector(completionSelector, { timeout: 600000 }); // 10 minut timeout
```

## Struktura plików
```
books/
└── {book_folder}/
    └── docs/
        └── book-ds-prompt.md    # Instrukcje dla Deep Research
```

## Kompletny skrypt automatyzacji

```javascript
async function runGeminiDeepResearch(book_folder) {
    // 1. Sprawdź istnienie pliku (BEZ CZYTANIA)
    await bash_command(`test -f books/${book_folder}/docs/book-ds-prompt.md && echo "Plik istnieje" || echo "Brak pliku"`);
    
    // 2. Otwórz Gemini (domyślnie headless)
    await mcp__playwright-headless__browser_navigate("https://gemini.google.com/");
    
    // 3. Aktywuj Deep Research
    const deepResearchButton = page.locator('button:has-text("Deep Research")');
    await deepResearchButton.click();
    
    // 4. Wklej instrukcje do schowka i wklej
    await bash_command(`cat books/${book_folder}/docs/book-ds-prompt.md | xsel --clipboard`);
    await page.getByRole('textbox', { name: 'Tu wpisz prompt' }).click();
    await page.keyboard.press('Control+v');
    
    // 5. Wyślij
    await page.keyboard.press('Enter');
    // LUB kliknij przycisk send jeśli Enter nie działa
    const sendButton = page.locator('button[data-testid="send-button"]');
    await sendButton.click();
    
    // 6. Czekaj na plan
    await page.waitForSelector('button:has-text("Zacznij wyszukiwanie")', { timeout: 60000 });
    
    // 7. Rozpocznij wyszukiwanie
    const startButton = page.locator('button:has-text("Zacznij wyszukiwanie")');
    await startButton.click();
    
    // 8. Zmień nazwę czatu (po rozpoczęciu wyszukiwania)
    const backButton = page.locator('button:has(img[title="chevron_left"])');
    await backButton.click();
    
    const moreButton = page.locator('button:has(img[title="more_vert"])');
    await moreButton.click();
    
    const renameButton = page.locator('button:has-text("Zmień nazwę")');
    await renameButton.click();
    
    const nameInput = page.locator('input[type="text"]');
    await nameInput.fill(book_folder);
    
    const confirmButton = page.locator('button:has-text("Zmień nazwę")');
    await confirmButton.click();
    
    // 9. Monitoruj (opcjonalnie)
    console.log(`Deep Research uruchomiony dla ${book_folder} - ZERO tokenów użytych!`);
    console.log("Czekaj na ukończenie procesu...");
}
```

## Uwagi techniczne

### Optymalizacje wklejania tekstu
- **NIE używaj** `type()` dla długich tekstów - jest bardzo wolny i kosztowny tokenowo
- **NIE używaj** `fill()` dla długich tekstów - przesyła CAŁĄ zawartość przez parametry Claude Code = tysiące tokenów
- **UŻYWAJ** `xsel --clipboard` + `Control+V` - ZERO tokenów, natychmiastowe wklejenie

### Timeouty
- Przygotowanie planu: 60 sekund
- Ukończenie Deep Research: 10 minut (może być dłużej dla złożonych zadań)

### Obsługa błędów
```javascript
try {
    await runGeminiDeepResearch(book_folder);
} catch (error) {
    console.error(`Błąd podczas Deep Research dla ${book_folder}:`, error);
    // Opcjonalnie: zrób screenshot dla debugowania
    await page.screenshot({ path: `debug_${book_folder}.png` });
}
```

## Przykład użycia
```bash
# Dla książki Pride and Prejudice
book_folder="0026_pride_and_prejudice"
runGeminiDeepResearch(book_folder)
```

## Rezultat
Po ukończeniu procesu otrzymasz:
- 50+ stronicowe szczegółowe streszczenie książki
- Opisy wizualne wszystkich postaci
- Katalogi lokacji i scen kluczowych
- Materiały gotowe do adaptacji graficznej
- Pełną analizę literacką zgodną z wymaganiami z pliku prompt

## Rozwiązywanie problemów

### Problem: Deep Research nie jest dostępny
- Sprawdź czy jesteś zalogowany do Gemini
- Upewnij się, że używasz wersji Gemini obsługującej Deep Research

### Problem: Wklejanie tekstu jest bardzo wolne
- Zamień `type()` na `fill()`
- Użyj metody ze schowkiem (clipboard)

### Problem: Timeout podczas oczekiwania
- Zwiększ timeout dla skomplikowanych książek
- Sprawdź czy Deep Research rzeczywiście się uruchomił

### Problem: Nie można znaleźć elementów
- Zaktualizuj selektory CSS/XPath
- Użyj `page.waitForSelector()` przed interakcją
- Zrób screenshot do debugowania