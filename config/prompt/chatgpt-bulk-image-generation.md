# ChatGPT Bulk Image Generation Process

Dla książki o tytule "[TYTUŁ]" autorstwa "[AUTOR]":

## 1. Lokalizacja plików

Znajdź folder książki w `/home/xai/DEV/37degrees/books/` (format: `NNNN_book_name`)

## 2. Przygotowanie

### a) Sprawdzenie/utworzenie projektu w ChatGPT
- Sprawdź czy istnieje projekt o nazwie takim jak folder książki (np. `0036_treasure_island`)
- Jeśli projekt nie istnieje:
  - Kliknij "New project" w lewym panelu
  - Nazwij projekt dokładnie tak jak folder książki
- Jeśli projekt istnieje, użyj go

### b) Dodanie plików kontekstowych (TYLKO przy tworzeniu nowego projektu)
**Ten krok wykonuj TYLKO jeśli właśnie utworzyłeś nowy projekt:**
- Kliknij "Add files" aby otworzyć okno dodawania plików
- W oknie dialogowym kliknij przycisk "Add files" w prawym górnym rogu (obok przycisku Close)
- Otworzy się systemowe okno wyboru plików
- Podaj pełną ścieżkę do folderu `docs/findings` danej książki, np.:
  `/home/xai/DEV/37degrees/books/0036_treasure_island/docs/findings`
- Zaznacz WSZYSTKIE pliki markdown (.md) które znajdują się w folderze `findings` (używając Ctrl+A lub zaznaczając ręcznie)
- Kliknij przycisk "Otwórz" lub "Open" w systemowym oknie
- **CZEKAJ** co najmniej 10 sekund aż wszystkie pliki się załadują
  - Podczas ładowania pliki mają ikonkę z kołem w środku (symbolizującym ładowanie)
  - Gdy pliki się załadują, ikona zmieni się na zwykłą ikonkę dokumentu
  - **WAŻNE**: Zamknij okno dopiero gdy wszystkie pliki mają ikonkę dokumentu (bez koła ładowania)
- Kliknij przycisk "Close" (krzyżyk) aby zamknąć okno dialogowe
- Po zamknięciu pod przyciskiem "Project files" powinna pokazać się liczba plików (np. "7 files")
- **ROZWIĄZYWANIE PROBLEMÓW**:
  - Jeśli któryś plik ładuje się bez końca (koło ładowania nie znika):
    - Przeładuj całą stronę (F5 lub Ctrl+R)
    - Powtórz operację załączania plików
  - **UWAGA**: Część plików może być już załączona - sprawdź które pliki są już dodane
  - Powinno być dokładnie **7 plików** z folderu findings:
    - 37d-bibliography-manager_findings.md
    - 37d-culture-impact_findings.md
    - 37d-facts-hunter_findings.md
    - 37d-polish-specialist_findings.md
    - 37d-source-validator_findings.md
    - 37d-symbol-analyst_findings.md
    - 37d-youth-connector_findings.md
- **DOPIERO TERAZ** kliknij w pole tekstowe chata (tam gdzie jest napis "New chat in [nazwa_projektu]")

### c) Przygotowanie plików JSON
Przejdź do katalogu `prompts/genimage/` dla tej książki

## 3. Proces generowania

Dla każdego pliku JSON w kolejności numerycznej (scene_01.json, scene_02.json, itd.):

### a) Przygotowanie pliku JSON
- Zlokalizuj odpowiedni plik JSON w folderze `prompts/genimage/` (np. `scene_01.json`)

### b) Konfiguracja ChatGPT - NOWA METODA Z ZAŁĄCZANIEM PLIKU
- Upewnij się że jesteś w projekcie dla tej książki (utworzonym w kroku 2a)
- **NOWA METODA (ZALECANA)**:
  - Kliknij przycisk "+" (plus) w dolnej części okna czatu
  - Wybierz "Add photos & files" z menu
  - W oknie dialogowym wyboru plików przejdź do folderu `prompts/genimage/` danej książki
  - Wybierz odpowiedni plik JSON (np. `scene_01.json`)
  - Po załączeniu pliku, w polu tekstowym wpisz dokładnie ten tekst: `Create an image based on the scene, style, and visual specifications described in the attached JSON. The JSON is a blueprint, not the content.`
  - Kliknij przycisk "Choose tool" (po lewej stronie pola tekstowego)
  - Z rozwiniętego menu wybierz "Create image"
  - Wyślij prompt klikając przycisk wysyłania (strzałka)
- **STARA METODA (ALTERNATYWNA)**:
  - Otwórz plik JSON i skopiuj jego zawartość
  - Wklej **TYLKO** czystą zawartość JSON (bez żadnych dodatkowych instrukcji)
  - Ustaw narzędzie generowania obrazów (kliknij "Choose tool" → "Create image")
  - Wyślij prompt

### c) Oczekiwanie na generowanie
- **CZEKAJ** aż obraz się w pełni wygeneruje
- Status zmieni się z "Creating image" lub "Adding details" na "Image created"

### d) Zapisywanie obrazu
Po zakończeniu generowania:
- **METODA 1 (ZALECANA)**: Kliknij prawym przyciskiem myszy na wygenerowany obraz i wybierz "Zapisz obraz jako..."
- **METODA 2 (ALTERNATYWNA)**: Kliknij na przycisk "Download this image" pod obrazem (może nie działać zawsze)
- **UWAGA**: Jeśli przycisk download nie działa, ZAWSZE używaj prawego kliknięcia na obraz
- Plik zostanie pobrany z automatyczną nazwą w formacie: `ChatGPT-Image-[Miesiąc]-[Dzień]-[Rok]-[Godzina]-[Minuta]-[Sekunda]-[AM/PM].png`
- Przykład: `ChatGPT-Image-Jul-27-2025-03-17-41-AM.png`

### e) Przenoszenie do właściwej lokalizacji
Przenieś pobrany plik z folderu tymczasowego (zazwyczaj `/tmp/playwright-mcp-output/[timestamp]/`) do:
```
/home/xai/DEV/37degrees/books/[FOLDER_KSIĄŻKI]/generated/
```
zmieniając nazwę na: `[book_number]_scene_[NN].png`

### f) Przejście do następnego
**DOPIERO PO** zakończeniu całego procesu dla jednego obrazu przejdź do następnego JSON

## WAŻNE OGRANICZENIA

- **NIE** wysyłaj kolejnego JSONa dopóki poprzedni obraz się nie wygeneruje
- **NIE** dodawaj żadnego tekstu do JSONa - tylko czysta zawartość pliku (dotyczy starej metody)
- Przy nowej metodzie używaj DOKŁADNIE tekstu: `Create an image based on the scene, style, and visual specifications described in the attached JSON. The JSON is a blueprint, not the content.`
- Każdy obraz musi być w pełni wygenerowany i zapisany przed przejściem do następnego
- Jeśli generowanie się zawiesi, poczekaj lub odśwież stronę przed kontynuacją
- Używaj narzędzia "Create image" (DALL-E) dla każdego obrazu
- Pliki kontekstowe dodawaj TYLKO przy tworzeniu nowego projektu, nie przy każdym obrazie

## Przykład nazewnictwa

Dla książki "Treasure Island" (numer 0036):
- `scene_01.json` → `0036_scene_01.png`
- `scene_02.json` → `0036_scene_02.png`
- `scene_03.json` → `0036_scene_03.png`
- itd.

## Struktura katalogów

```
books/
  0036_treasure_island/
    prompts/
      genimage/         # Tu są pliki JSON źródłowe
        scene_01.json
        scene_02.json
        ...
    generated/          # Tu zapisuj wygenerowane obrazy
        0036_scene_01.png
        0036_scene_02.png
        ...
```

## Wskazówki

1. Proces jest czasochłonny - każdy obraz może generować się 1-2 minuty
2. Monitoruj status generowania przed przejściem do następnego
3. W przypadku błędów, zapisz które obrazy już zostały wygenerowane
4. Używaj dedykowanego projektu ChatGPT dla każdej książki (nazwa projektu = nazwa folderu książki)
5. Dzięki projektom możesz łatwo wrócić do generowania obrazów dla konkretnej książki
6. **NOWA METODA**: Załączanie plików JSON przez przycisk "+" jest bardziej niezawodne niż wklejanie zawartości
7. ChatGPT automatycznie rozpozna strukturę JSON z załączonego pliku