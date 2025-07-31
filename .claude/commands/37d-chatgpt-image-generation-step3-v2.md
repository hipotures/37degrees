Proces automatycznego generowania obrazu w ChatGPT

UWAGA: Używaj MCP playwright-headless do automatyzacji

  Dane wejściowe:

  - Projekt: "0016_lalka"
  - Plik JSON: /home/xai/DEV/37degrees/books/0016_lalka/prompts/genimage/scene_23.json
  - Prompt: "Wygeneruj obraz opisany załączonym jsonem"

  Kroki automatyzacji:

  0. Otwórz stronę ChatGPT

  // Użyj MCP playwright-headless do nawigacji
  mcp__playwright-headless__browser_navigate('https://chatgpt.com/');

  1. Nawigacja do projektu

  // Otwórz sidebar
  mcp__playwright-headless__browser_click(element: "Open sidebar button");
  
  // Kliknij projekt 0016_lalka
  mcp__playwright-headless__browser_click(element: "0016_lalka project link");

  2. Załączenie pliku JSON

  // Kliknij przycisk "Add photos & files"
  mcp__playwright-headless__browser_click(element: "Add photos & files button");
  
  // Wybierz "Add files" z menu
  mcp__playwright-headless__browser_click(element: "Add files menu option");

  // Wybierz plik z systemu
  mcp__playwright-headless__browser_file_upload(paths: ["/home/xai/DEV/37degrees/books/0016_lalka/prompts/genimage/scene_23.json"]);

  3. Wybór narzędzia "Create image"

  // Kliknij przycisk "Choose tool"
  mcp__playwright-headless__browser_click(element: "Choose tool button");

  // Wybierz "Create image" z menu dropdown
  mcp__playwright-headless__browser_click(element: "Create image option");

  4. Wpisanie promptu

  // Najpierw zrób snapshot aby znaleźć aktualny ref
  mcp__playwright-headless__browser_snapshot();
  
  // Wpisz prompt w pole tekstowe (NIE używaj hardcoded ref!)
  mcp__playwright-headless__browser_type(
    element: "text input field for chat",
    ref: "UŻYJ_RZECZYWISTEGO_REF_Z_SNAPSHOT",
    text: "Wygeneruj obraz opisany załączonym jsonem"
  );

  5. Uruchomienie generacji

  // Kliknij przycisk "Send prompt" (czarne koło ze strzałką)
  mcp__playwright-headless__browser_click(element: "Send prompt button");

  Stan końcowy:

  - Plik JSON został załączony i jest widoczny w interfejsie
  - Narzędzie "Create image" jest wybrane (widoczne dodatkowe opcje Image/Styles)
  - Prompt jest wpisany w polu tekstowym
  - ChatGPT rozpoczyna generowanie obrazu (pojawia się status "Thinking" → "Reading documents" → "Getting started")

  Weryfikacja sukcesu:

  // Czekaj na pojawienie się statusu "Getting started" (generowanie się rozpoczęło)
  mcp__playwright-headless__browser_wait_for(text: "Getting started");

  - Sukcesem jest gdy obraz zaczyna się generować (pojawia się "Getting started")
  - URL zmienia się na nowy conversation thread (c/xxxxx)
  - Status przechodzi przez: "Thinking" → "Reading documents" → "Getting started"

  Uwagi techniczne:

  - ChatGPT używa React, więc potrzebne są właściwe eventy (focus, input, change)
  - Przycisk send pozostaje disabled dopóki nie ma tekstu w polu input
  - Używaj ZAWSZE MCP playwright-headless calls (nie raw Playwright API)
  - Element refs są dynamiczne - rób browser_snapshot() przed interakcją z elementami
  - NIGDY nie używaj hardcoded refs jak "#prompt-textarea" - zawsze używaj ref z aktualnego snapshot
  - Opisuj elementy naturalnie (np. "Open sidebar button") zamiast używać fake refs
  - Jeśli element nie zostanie znaleziony, zrób browser_snapshot() i spróbuj ponownie
  - Po browser_snapshot() znajdź właściwy ref dla pola tekstowego i użyj go w browser_type()
