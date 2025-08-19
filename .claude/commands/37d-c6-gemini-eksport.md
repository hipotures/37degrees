# Gemini Export - Automatyzacja Procesu

## 📋 Wymagane MCP (Message Control Protocols)

> **WAŻNE**: Używaj wyłącznie poniższych MCP w tym procesie
- `todoit` - zarządzanie listą zadań
- `playwright-cdp` - automatyzacja przeglądarki
- musi być podany katalog z książką, 
  jeśli go nie ma, zakończz pracę, 
  jeśli jest, jego wartość ustaw w zmiennej [BOOK_FOLDER]

> ⚠️ **UWAGA**: Błędy związane z dużymi odpowiedziami (>25000 tokens) należy ignorować
---

## 🚀 Proces Automatyzacji

### Krok 1: Pobranie pozycji do przetworzenia

Pobierz pierwszą pozycję ze statusem `in_progress` z listy zadań:

const readyDownloadTasks = await mcp__todoit__todo_find_subitems_by_status({
  list_key: "[BOOK_FOLDER]",
  conditions: {
    "ds_gen": "completed",
    "ds_exp": "pending"
  },
  limit: 1
});


**Przykładowy wynik:** `0002_animal_farm` - "Deep Research for Animal Farm by George Orwell"

---

### Krok 2: Połączenie z przeglądarką

1. **Połączenie z MCP playwright-cdp**
   - Połącz się z `playwright-cdp`
   - W przypadku braku połączenia → zgłoś błąd

---

### Krok 3: Wyszukanie chatu z książką
// mcp__todoit__todo_get_item_property
search_url = todo_get_item_property(
   list_key : '[BOOK_FOLDER]',
   item_key : 'ds_gen',
   property_key : 'SEARCH_URL'
)

Jeśli research_url nie zwróci wartosci lub zwróci błąd, wykonaj te cztery punkty:
1. **Nawigacja**
   - Przejdź do: `https://gemini.google.com/search`

2. **Wyszukiwanie**
   - W polu "Szukaj czatów" wpisz klucz książki (np. `0002_animal_farm`)

3. Z listy wyników wybierz chat o nazwie **dokładnie** pasującej do klucza (dopasowanie 1:1)
4. Kliknij na odpowiedni chat, aby go otworzyć

ELSE
  Jeśli research_url zawiera url (przykład, różnice bedą tylko w częsci za app/ : https://gemini.google.com/app/23500f4e7be0cdad)
Przejdź do strony $search_url

> ⚠️ **UWAGA**: Błędy związane z dużymi odpowiedziami (>25000 tokens) należy ignorować

---

### Krok 4: Eksport chatu do Google Docs

1. **W aplikacji Gemini masz wykonać dokładnie te czynnoścci, "na ślepo", bez sprawdzania stanu!**
   - Kliknij przycisk eksportu: `button[data-test-id="export-menu-button"]`
   - Wybierz opcję eksportu do Dokumentów: `button[data-test-id="export-to-docs-button"]`

Jeśli ta operacja się udała, zaktualizuj status eksportu dla tej książki:
  todo_update_item_status(
    list_key: "[BOOK_FOLDER]", 
    item_key: "gemini-ds",
    subitem_key: "ds_exp",
    status: "completed"
  )

---

### Krok 5: Pobranie dokumentu jako TXT

1. **Przełącz na nową kartę Google Docs**
   - Użyj: `browser_tab_select` z indeksem `1`
   - Jeśli nie ma tab z indeksem 1, wróc do kroku 3 i powtórz całą operację

2. **Pobierz dokument:**
   - Kliknij menu "Plik"
   - Kliknij "Pobierz"
   - Wybierz "Zwykły tekst (.txt)"

---

### Krok 6: Przeniesienie pliku do struktury projektu

1. **Weryfikacja zawartości**
   - Sprawdź tytuł i autora w pierwszych liniach pliku

2. **Identyfikacja katalogu docelowego**
   - Znajdź odpowiedni katalog: `books/NNNN_book_name/`

3. **Przeniesienie pliku**
   - Przenieś plik z `/tmp/playwright-mcp-output/[timestamp]/[nazwa-dokumentu].txt`
   - Do: `books/NNNN_book_name/docs/review.txt`
   Jeśli pliku nie ma, wróc do kroku 6, punktu 2, czyli ponownie pobierz plik w Docs
> ⚠️ **WAŻNE**: Używaj komendy `mv` zamiast `cp` aby uniknąć zapychania katalogu `/tmp/playwright-mcp-output/`

**Przykład przeniesienia:**
```bash
mv "/tmp/playwright-mcp-output/[timestamp]/nazwa-pliku.txt" \
   "/home/xai/DEV/37degrees/books/0001_alice_in_wonderland/docs/review.txt"
```


---

### Krok 7: Oznaczenie zadania jako ukończone

Po pomyślnym zakończeniu całego procesu, gdy jesteś pewien, że plik review.txt zawiera
odpowiednią treść (możesz odczytać pierwsze 10 linii, tam powinno być potwierdzenie poprawności,
że to właściwa książka) znajduje oznacz zadanie jako wykonane:
  todo_update_item_status(
    list_key: "[BOOK_FOLDER]", 
    item_key: "gemini-ds",
    subitem_key: "ds_dwn",
    status: "completed"
  )

---

### Krok 8: Czyszczenie środowiska
> ⚠️ **UWAGA**: Błędy związane z dużymi odpowiedziami (>25000 tokens) należy ignorować

1. Zamknij zakładkę Google Docs:
   mcp__playwright-cdp__browser_tab_close(log_limit=100)

2. Sprawdź, czy pozostała tylko jedna karta przeglądarki

---

## 🛠️ Szczegóły Techniczne

### Metoda JavaScript do eksportu

```javascript
() => document.querySelector('button[data-test-id="export-menu-button"]').click()
```

### Elementy interfejsu do interakcji

#### 1. Przycisk "Eksportuj" (menu dropdown)
```html
<button data-test-id="export-menu-button" 
        class="mdc-button mat-mdc-button-base...">
  <span>Eksportuj</span>
</button>
```

#### 2. Opcja "Eksportuj do Dokumentów"
```html
<button data-test-id="export-to-docs-button" 
        class="mat-mdc-menu-item...">
  <span>Eksportuj do Dokumentów</span>
</button>
```

### Narzędzia MCP używane w procesie:
- `mcp__playwright-cdp__browser_evaluate` - dla wykonania JavaScript
- `mcp__playwright-cdp__browser_click` - dla kliknięć w Google Docs
- `mcp__playwright-cdp__browser_tab_select` - dla przełączania kart
- `mcp__playwright-cdp__browser_tab_close` - dla zamykania kart

### Lokalizacja pobranego pliku

Plik TXT zostanie automatycznie zapisany w:
```
/tmp/playwright-mcp-output/[timestamp]/[nazwa-dokumentu].txt
```

---

## 📊 Podsumowanie

**Cel procesu:** Automatyczne eksportowanie chatów z Gemini do plików tekstowych i organizowanie ich w strukturze projektu książek.

**Kluczowe elementy:**
- ✅ Automatyczne wyszukiwanie chatów
- ✅ Eksport do Google Docs
- ✅ Konwersja do formatu TXT
- ✅ Organizacja w strukturze katalogów
- ✅ Zarządzanie statusem zadań

**Wymagania:**
- Aktywne połączenie z MCP
- Uprawnienia do Google Docs
- Dostęp do struktury katalogów projektu
