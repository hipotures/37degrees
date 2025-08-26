# Gemini Export - Automatyzacja Procesu

## 📋 Wymagane MCP (Message Control Protocols)

> **WAŻNE**: Używaj wyłącznie poniższych MCP w tym procesie
- `todoit` - zarządzanie listą zadań
- `playwright-cdp` - automatyzacja przeglądarki
- musi być podany katalog z książką, 
  jeśli go nie ma, zakończ pracę, 
  jeśli jest, jego wartość ustaw w zmiennej [BOOK_FOLDER]

> ⚠️ **UWAGA**: Błędy związane z dużymi odpowiedziami (>25000 tokens) należy ignorować
---

## 🚀 Proces Automatyzacji

### Krok 1: Pobranie pozycji do przetworzenia

Pobierz pierwszą pozycję ze statusem `in_progress` z listy zadań:

const result = await mcp__todoit__todo_get_list_items({
  list_key: "gemini-deep-research",
  status: "in_progress",
  limit: 1
});
const BOOK_FOLDER = result.items[0].item_key;

**Przykładowy wynik:** `0002_animal_farm` - "Deep Research for Animal Farm by George Orwell"

---

### Krok 2: Połączenie z przeglądarką

1. **Połączenie z MCP playwright-cdp**
   - Połącz się z `playwright-cdp`
   - W przypadku braku połączenia → zgłoś błąd

---

### Krok 3: Wyszukanie chatu z książką (3 opcje znalezienia)
Jeśli któraś opcja zwórci poprawny url, zignoruj pozostałe opcje.

Opcja 1.

search_url = todo_get_item_property(
   list_key : 'gemini-deep-research',
   item_key : '[BOOK_FOLDER]',
   property_key : 'SEARCH_URL'
)

Opcja 2.
// mcp__todoit__todo_get_item_property
search_url = todo_get_item_property(
   list_key : '[BOOK_FOLDER]',
   item_key : 'ds_gen',
   property_key : 'SEARCH_URL'
)

Opcja 3.
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

2. **Status**
Jesli ta operacja się udała, bedziesz mieć nową kartę Google Docs, wtedy oznacz
  todo_update_item_status(
    list_key: "[BOOK_FOLDER]", 
    item_key: "gemini-ds",
    subitem_key: "ds_exp",
    status: "completed"
  )
Jeśli operacja się nie udała, wróć do punktu 1 w tym kroku i ponów operację. Jeśli ponownie operacja się nie udała, przeładuj stronę i wróc do punktu 1.

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

### Krok 7: Zmień nazwę pliku
Nazwę pliku należy zmienić na [BOOK_FOLDER]  (Przykładowo 0001_alice_in_wonderland - rozszerzeniem pliku nie nalezy się przejmować, bedzie zachowane aktualne))

Są dwie możliwości zmiany nazwy pliku:
 - Poprzez klikniecie w aktualną nazwę (zwyle jest to nazwa zawierająca wyrazy "streszczenie" i/lub "wizualizacja".
   Po kliknieciu w nazwę należy ją zazanczyć Ctlr+a i wpisać nową
albo
 - Poprzez menu -> Plik (clik) -> Zmień nazwę (click). Stara nazwa będzie już zaznaczona, wystarczy wpisać nową.

### Krok 8: Oznaczenie zadania jako ukończone

Po pomyślnym zakończeniu całego procesu, gdy jesteś pewien, że plik review.txt zawiera
odpowiednią treść (możesz odczytać pierwsze 10 linii, tam powinno być potwierdzenie poprawności,
że to właściwa książka) znajduje oznacz zadanie jako wykonane wywołując 2 polecenia:

todo_update_item_status(
  list_key: "gemini-deep-research", 
  item_key: "[BOOK_FOLDER]",
  status: "completed"
)

todo_update_item_status(
  list_key: "[BOOK_FOLDER]", 
  item_key: "gemini-ds",
  subitem_key: "ds_dwn",
  status: "completed"
)

---

### Krok 8: Czyszczenie środowiska
> ⚠️ **UWAGA**: Błędy związane z dużymi odpowiedziami (>25000 tokens) należy ignorować. Nie zamykaj wszystkich tabów!


1. Sprawdź, czy pozostała tylko jedna karta przeglądarki
   mcp__playwright-cdp__browser_tab_list()
2. Zamknij zakładki Google Docs (ma zostać otwarty pierwszy tab o id 0):
   mcp__playwright-cdp__browser_tab_close(log_limit=100)

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
