Proces automatycznego pobierania obrazów z ChatGPT

UWAGA: Używaj MCP playwright-headless do automatyzacji

  Dane wejściowe:

  - Projekt: "[BOOK_FOLDER]" (np. "0016_lalka")
  - TODO file: /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md

  Kroki automatyzacji:

  0. Sprawdź TODO list

  // Sprawdź czy istnieje TODO file
  ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md
  
  // Jeśli nie istnieje → utwórz TODO (patrz sekcja "Tworzenie TODO")
  // Jeśli istnieje → znajdź pierwsze nieukończone zadanie
  grep -n "^\[ \]" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md | head -1

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

  3. Pobierz obrazy

  // Zrób snapshot aby zobaczyć obrazy
  mcp__playwright-headless__browser_snapshot();

  // Dla każdego obrazu w konwersacji:
  mcp__playwright-headless__browser_click(element: "Download this image button");
  
  // Poczekaj na pobranie
  mcp__playwright-headless__browser_wait_for(time: 5);

  4. Przenieś i nazwij pliki

  // Znajdź pobrane pliki
  ls -la -t /tmp/playwright-mcp-files/ChatGPT-Image*.png

  // Sprawdź czy chat ma JSON ze sceną
  // Jeśli tak: użyj nazwy 0016_scene_12.png, 0016_scene_12_a.png
  // Jeśli nie: użyj nazwy 0016_generic_001.png, 0016_generic_002.png

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

  Uwagi techniczne:

  - ZAWSZE używaj browser_snapshot() przed klikaniem
  - NIGDY nie używaj hardcoded refs - tylko rzeczywiste z snapshot
  - Użyj POZYCJI w sidebar dla identycznych nazw chatów
  - Przewiń PRZED tworzeniem TODO (lazy loading)
  - Zamknij browser na końcu (zapobiega konfliktom)