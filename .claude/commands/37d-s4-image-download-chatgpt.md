Proces automatycznego pobierania obrazów z ChatGPT

UWAGA: Używaj MCP playwright-headless do automatyzacji

  Dane wejściowe:

  - Projekt: "[BOOK_FOLDER]" (np. "0031_solaris")
  - TODO-GENERATE file: /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md
  - TODO-DOWNLOAD file: /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md

  Kroki automatyzacji:

  0. Odczytaj Project ID i Thread ID z TODO

  // Odczytaj Project ID z TODO-GENERATE.md
  PROJECT_ID=$(grep "^# PROJECT_ID = " /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md | cut -d' ' -f4)
  if [ -z "$PROJECT_ID" ]; then
    echo "ERROR: Project ID nie znaleziony w TODO-GENERATE.md"
    exit 1
  fi
  echo "Project ID: $PROJECT_ID"

  // Znajdź pierwsze zadanie do pobrania [x] [ ] (thread created, image not downloaded)
  TASK_TO_DOWNLOAD=$(grep -n "^\[x\] \[ \] Created thread" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md | head -1)
  if [ -z "$TASK_TO_DOWNLOAD" ]; then
    echo "INFO: Brak zadań do pobrania - wszystkie obrazy już pobrane lub nie ma wygenerowanych threadów"
    exit 0
  fi
  
  // Wyciągnij Thread ID z zadania
  THREAD_ID=$(echo "$TASK_TO_DOWNLOAD" | sed 's/.*Created thread \([a-f0-9-]*\).*/\1/')
  echo "Thread ID: $THREAD_ID"
  
  // Zbuduj bezpośredni URL do chatu
  CHAT_URL="https://chatgpt.com/g/${PROJECT_ID}/c/${THREAD_ID}"
  echo "Chat URL: $CHAT_URL"

  1. Bezpośrednia nawigacja do chatu

  // CRITICAL: Nawiguj bezpośrednio do URL chatu złożonego z Project ID i Thread ID
  mcp__playwright-headless__browser_navigate(url: "${CHAT_URL}");
  
  // Format URL: https://chatgpt.com/g/[PROJECT_ID]/c/[THREAD_ID]
  // Przykład: https://chatgpt.com/g/g-p-688bf83687388191bf1edc733262fb53/c/688bf864-7c6c-8326-a983-b868f438bbc7
  
  // Poczekaj na załadowanie chatu
  mcp__playwright-headless__browser_wait_for(time: 3);

  2. Pobierz wszystkie obrazy z chatu

  // Zrób snapshot aby zobaczyć strukturę chatu
  mcp__playwright-headless__browser_snapshot();

  // CRITICAL: Chat może mieć 3 typy sytuacji:
  // 1. Single obraz - jeden prompt, jedna odpowiedź, jeden "Download this image"
  // 2. Multiple odpowiedzi - jeden prompt, X/Y responses, "Previous/Next response" buttons
  // 3. Multiple prompty - kilka promptów użytkownika w jednym chacie
  // 4. KOMBINACJA - kilka promptów, niektóre z multiple odpowiedziami

  // ALGORYTM: Przewiń przez CAŁY chat i pobierz wszystkie obrazy
  
  // Dla każdej sekcji "ChatGPT said:":
  // 1. Sprawdź czy są przyciski "Previous response" / "Next response"
  if (widzisz Previous/Next response buttons) {
    // Multiple odpowiedzi na ten sam prompt - SEPARATE CLICKS APPROACH
    // CRITICAL: ChatGPT domyślnie pokazuje ostatnią odpowiedź (2/2, 3/3, etc.)
    
    // KROK 1: Pobierz obraz z AKTUALNEJ odpowiedzi (ostatniej: 2/2)
    mcp__playwright-headless__browser_click(element: "Download this image button");
    
    // KROK 2: Przejdź do PIERWSZEJ odpowiedzi i pobierz z niej
    mcp__playwright-headless__browser_evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const prevButton = buttons.find(btn => {
        const label = btn.getAttribute('aria-label') || '';
        return label.includes('Previous response');
      });
      if (prevButton && !prevButton.disabled) {
        prevButton.click();
        return 'Moved to previous response';
      }
      return 'Already at first response';
    });
    
    // KROK 3: Pobierz obraz z pierwszej odpowiedzi (1/2)
    mcp__playwright-headless__browser_click(element: "Download this image button");
    
    // UWAGA: Ten algorytm działa dla 2 odpowiedzi (1/2, 2/2)
    // Dla więcej odpowiedzi trzeba rozszerzyć logikę
    
  } else {
    // Single odpowiedź - pobierz wszystkie obrazy z tej sekcji
    mcp__playwright-headless__browser_click(element: "Download this image button");
  }
  
  // POWTARZAJ dla każdej sekcji "ChatGPT said:" w chacie
  // WSZYSTKIE obrazy z chatu dotyczą tej samej sceny (numer z pierwszego JSON)
  
  // Poczekaj na pobranie
  mcp__playwright-headless__browser_wait_for(time: 5);

  3. Przenieś i nazwij pliki

  // Znajdź pobrane pliki
  ls -la -t /tmp/playwright-mcp-files/ChatGPT-Image*.png

  // Wyciągnij numer sceny z Thread ID (z TODO-GENERATE.md)
  // Format TODO: "[x] Created thread [THREAD_ID] for image scene_NN.json"
  SCENE_FILE=$(echo "$TASK_TO_DOWNLOAD" | sed 's/.*for image \(scene_[0-9][0-9]\.json\).*/\1/')
  SCENE_NUMBER=$(echo "$SCENE_FILE" | sed 's/scene_\([0-9][0-9]\)\.json/\1/')
  echo "Scene number: $SCENE_NUMBER"
  
  // Użyj nazwy: [BOOK_FOLDER]_scene_[NN].png, [BOOK_FOLDER]_scene_[NN]_a.png, etc.
  // Przykład: 0031_solaris_scene_01.png, 0031_solaris_scene_01_a.png

  // CRITICAL: Sprawdź czy plik już istnieje!
  ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[PLANNED_NAME].png
  
  // Jeśli istnieje → użyj następnego sufixu (_a, _b, _c...)
  // NIGDY nie nadpisuj istniejących plików!

  // Przenieś plik
  mv /tmp/playwright-mcp-files/ChatGPT-Image*.png /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[FINAL_NAME].png

  // Zaktualizuj status w TODO-GENERATE.md - zmień [x] [ ] na [x] [x]
  sed -i "s/^\[x\] \[ \] Created thread ${THREAD_ID}/[x] [x] Created thread ${THREAD_ID}/" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md

  4. Zamknij przeglądarkę

  // CRITICAL: Zawsze zamknij browser aby uniknąć konfliktów
  mcp__playwright-headless__browser_close();

  UWAGA: Nowa wersja s4 nie wymaga tworzenia TODO-DOWNLOAD.md!
  
  System automatycznie:
  1. Odczytuje Project ID z TODO-GENERATE.md
  2. Odczytuje Thread ID z ukończonych zadań w TODO-GENERATE.md
  3. Składa bezpośredni URL i nawiguje do chatu
  4. Pobiera obrazy bez przechodzenia przez sidebar
  
  Format URL: https://chatgpt.com/g/[PROJECT_ID]/c/[THREAD_ID]
  
  Stara wersja wymagała:
  - Tworzenia TODO-DOWNLOAD.md przez ręczne przewijanie sidebar
  - Klikania w konwersacje przez pozycję
  - żmudnej nawigacji przez projekty
  
  Nowa wersja:
  - Wszystkie dane bierze z TODO-GENERATE.md
  - Bezpośrednia nawigacja do konkretnego chatu
  - Szybsze i bardziej niezawodne

  Weryfikacja sukcesu:

  - Plik obrazu został zapisany w /books/[BOOK_FOLDER]/generated/
  - Nazwa pliku: [BOOK_FOLDER]_scene_[NN].png (np. 0031_solaris_scene_01.png)
  - Nie nadpisano istniejących plików
  - Status w TODO-GENERATE.md zaktualizowany z [x] [ ] na [x] [x]
  - Dla chatów z multiple odpowiedziami: 2 różne pliki PNG pobrane (różne rozmiary)
  - Bezpośrednia nawigacja do chatu bez przechodzenia przez sidebar

  System statusów:
  - [x] [x] - thread created ✅ + image downloaded ✅ (COMPLETED)
  - [x] [ ] - thread created ✅ + image pending ⏳ (READY TO DOWNLOAD)  
  - [ ] [ ] - thread pending ⏳ + image pending ⏳ (NOT STARTED)

  Uwagi techniczne:

  - **NOWA ARCHITEKTURA:** Bezpośrednie składanie URL z Project ID + Thread ID
  - **Brak nawigacji:** Nie trzeba klikać przez sidebar, projekty, konwersacje
  - **Źródło danych:** Wszystko z TODO-GENERATE.md (Project ID i Thread ID)
  - **Format URL:** https://chatgpt.com/g/[PROJECT_ID]/c/[THREAD_ID]
  - **Kompatybilność:** Działa z URL z "-[BOOK_FOLDER]" i bez (ChatGPT ignoruje suffix)
  - ZAWSZE używaj browser_snapshot() przed klikaniem
  - NIGDY nie używaj hardcoded refs - tylko rzeczywiste z snapshot
  - Zamknij browser na końcu (zapobiega konfliktom)
  - Multiple odpowiedzi: używaj SEPARATE CLICKS zamiast atomic evaluate
  - Przyciski wykrywaj przez aria-label, nie textContent