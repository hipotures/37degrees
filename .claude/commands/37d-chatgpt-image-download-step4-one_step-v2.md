Proces automatycznego pobierania obrazów z ChatGPT

UWAGA: Używaj MCP playwright-headless do automatyzacji

  Dane wejściowe:

  - Projekt: "[BOOK_FOLDER]" (np. "0016_lalka")
  - TODO file: /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md

  Kroki automatyzacji:

  0. Sprawdź TODO list

  // Wykonaj to polecenie shell i postępuj zgodnie z ty, co wypisze na output:
  if [ -f "/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md" ]; then \
    TASK=$(grep -n "^\[ \]" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md | head -1); \
    if [ -n "$TASK" ]; then \
      echo "TODO-DOWNLOAD.md istnieje. Pierwsze zadanie: $TASK - pobierz obrazy z tego chata"; \
    else \
      echo "TODO-DOWNLOAD.md istnieje ale wszystkie zadania ukończone"; \
    fi; \
  else \
    echo "TODO-DOWNLOAD.md nie istnieje w /generated/, utwórz nowy (przejdź do sekcji Tworzenie TODO)"; \
  fi

  // CRITICAL: To polecenie sprawdza TYLKO folder "generated" i nic więcej!

  1. Nawigacja do ChatGPT

  // Otwórz stronę
  mcp__playwright-headless__browser_navigate('https://chatgpt.com/');

  // Otwórz sidebar
  mcp__playwright-headless__browser_click(element: "Open sidebar button");
  
  // Kliknij projekt
  mcp__playwright-headless__browser_click(element: "[BOOK_FOLDER] project link");

  2. Otwórz konkretną konwersację

  // CRITICAL: Użyj POZYCJI w sidebar (numer linii z TODO), nie nazwy!
  // Jeśli TODO line 3 = kliknij 3. konwersację w liście
  mcp__playwright-headless__browser_click(element: "Conversation at position [N] in sidebar");

  3. Pobierz wszystkie obrazy z chatu

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

  4. Przenieś i nazwij pliki

  // Znajdź pobrane pliki
  ls -la -t /tmp/playwright-mcp-files/ChatGPT-Image*.png

  // Sprawdź pierwszy prompt w chacie czy ma JSON ze sceną
  // Jeśli tak: użyj nazwy 0016_scene_12.png, 0016_scene_12_a.png, 0016_scene_12_b.png...
  // Jeśli nie: użyj nazwy 0016_generic_001.png, 0016_generic_002.png, 0016_generic_003.png...
  // WSZYSTKIE obrazy z jednego chatu mają ten sam numer sceny!

  // CRITICAL: Sprawdź czy plik już istnieje!
  ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[PLANNED_NAME].png
  
  // Jeśli istnieje → użyj następnego sufixu (_a, _b, _c...)
  // NIGDY nie nadpisuj istniejących plików!

  // Przenieś plik
  mv /tmp/playwright-mcp-files/ChatGPT-Image*.png /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[FINAL_NAME].png

  5. Zaktualizuj TODO

  // Oznacz zadanie jako ukończone (N = numer linii z kroku 0)
  sed -i 'Ns/^\[ \]/[x]/' /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md

  6. Zamknij przeglądarkę

  // CRITICAL: Zawsze zamknij browser aby uniknąć konfliktów
  mcp__playwright-headless__browser_close();

  Tworzenie TODO (jeśli nie istnieje):

  1. Przewiń do końca listy konwersacji

  // CRITICAL: ChatGPT używa lazy loading - musisz przewinąć!
  mcp__playwright-headless__browser_evaluate(() => {
    window.scrollTo(0, 5000);
    document.documentElement.scrollTop = 5000;
    document.body.scrollTop = 5000;
    const main = document.querySelector('main');
    if (main) main.scrollTop = 5000;
    return 'Scrolled';
  });

  // Powtarzaj aż zobaczysz scene_01

  2. Stwórz TODO file

  // CRITICAL: Zachowaj DOKŁADNĄ KOLEJNOŚĆ chatów!
  // Zapisz każdą konwersację jako osobną linię:
  [ ] Generowanie obrazu z jsona - Wygeneruj obraz opisany załączonym jsonem
  [ ] New chat
  [ ] Create image from JSON scene_25 - create an image based on...
  
  // NIE używaj generycznych opisów jak "Download from scene_25"

  Weryfikacja sukcesu:

  - Plik obrazu został zapisany w /books/[BOOK_FOLDER]/generated/
  - TODO pokazuje [x] przy ukończonym zadaniu
  - Nie nadpisano istniejących plików
  - Dla chatów z multiple odpowiedziami: 2 różne pliki PNG pobrane (różne rozmiary)

  Uwagi techniczne:

  - ZAWSZE używaj browser_snapshot() przed klikaniem
  - NIGDY nie używaj hardcoded refs - tylko rzeczywiste z snapshot
  - Użyj POZYCJI w sidebar dla identycznych nazw chatów
  - Przewiń PRZED tworzeniem TODO (lazy loading)
  - Zamknij browser na końcu (zapobiega konfliktom)
  - Multiple odpowiedzi: używaj SEPARATE CLICKS zamiast atomic evaluate
  - Przyciski wykrywaj przez aria-label, nie textContent
  - ChatGPT automatycznie wraca do ostatniej odpowiedzi - dlatego najpierw pobierz z niej