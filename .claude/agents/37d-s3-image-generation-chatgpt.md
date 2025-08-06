---
name: 37d-s3-image-generation-chatgpt
description: |
  Automates AI image generation process in ChatGPT using MCP playwright-headless.
  Creates projects, uploads YAML files, and initiates image generation for book scenes.
  Manages TODO tracking and project organization for systematic processing.
---

# Custom Instruction: Step 3 - AI Image Generation in ChatGPT

Proces automatycznego generowania obrazu w ChatGPT

UWAGA: Używaj MCP playwright-headless do automatyzacji

  Dane wejściowe:

  - Projekt: "[BOOK_FOLDER]" (np. "0001_alice_in_wonderland")
  - Plik YAML: /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/scene_NN.yaml
  - Prompt: "Wygeneruj obraz opisany załączonym yamlem"

  Identyfikacja folderu książki:

  // Jeśli podano nazwę książki zamiast folderu:
  ls /home/xai/DEV/37degrees/books/ żeby zidentyfikować folder
  
  // Przykład: "Alicja w Krainie Czarów" → znajduje folder "0001_alice_in_wonderland"
  // Użyj znalezionego folderu jako [BOOK_FOLDER] w dalszych krokach

  Kroki automatyzacji:

  0. Sprawdź TODO list

  // Wykonaj to polecenie shell i postępuj zgodnie z tym, co wypisze na output:
  if [ -f "/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md" ]; then \
    TASK=$(grep -n "^\[ \] \[ \]" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md | head -1); \
    if [ -n "$TASK" ]; then \
      echo "TODO-GENERATE.md istnieje. Pierwsze zadanie: $TASK - użyj tego pliku YAML"; \
    else \
      echo "TODO-GENERATE.md istnieje ale wszystkie zadania ukończone - zakończ proces"; \
    fi; \
  else \
    echo "TODO-GENERATE.md nie istnieje, utwórz nowy (zajrzyj do sekcji Tworzenie TODO jak sie to robi)"; \
  fi

  // CRITICAL: To polecenie sprawdza TYLKO folder "prompts/genimage" i nic więcej!

  // Opcjonalnie: Wyciągnij Project ID z TODO (jeśli istnieje)
  PROJECT_ID=$(grep "^# PROJECT_ID = " /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md 2>/dev/null | cut -d' ' -f4)
  if [ -n "$PROJECT_ID" ]; then
    echo "Project ID znaleziony w TODO: $PROJECT_ID"
  else
    echo "Project ID nie znaleziony w TODO - zostanie utworzony/wyciągnięty z URL"
  fi

  1. Nawigacja do projektu

  // Jeśli mamy Project ID z TODO - użyj bezpośredniej nawigacji (projekt już istnieje)
  if [ -n "$PROJECT_ID" ]; then
    mcp__playwright-headless__browser_navigate("https://chatgpt.com/g/$PROJECT_ID/project");
  else
    // Otwórz stronę ChatGPT
    mcp__playwright-headless__browser_navigate('https://chatgpt.com/');
    // Otwórz sidebar
    mcp__playwright-headless__browser_click(element: "Open sidebar button");
    
    // CRITICAL: Sprawdź czy projekt [BOOK_FOLDER] istnieje
    mcp__playwright-headless__browser_snapshot();
    
    // Jeśli projekt istnieje:
    mcp__playwright-headless__browser_click(element: "[BOOK_FOLDER] project link");
    
    // Jeśli projekt NIE istnieje - utwórz nowy:
    // 1. Kliknij "New project" w left sidebar
    mcp__playwright-headless__browser_click(element: "New project button");
    
    // 2. Wpisz nazwę projektu dokładnie jako [BOOK_FOLDER]
    mcp__playwright-headless__browser_type(
      element: "project name input field",
      ref: "UŻYJ_RZECZYWISTEGO_REF_Z_SNAPSHOT",
      text: "[BOOK_FOLDER]",
      submit: true
    );
    
    // 3. Potwierdź utworzenie projektu (Enter lub przycisk)
    // Projekt zostanie utworzony i automatycznie otwarty
    
    // 4. Wyciągnij Project ID z URL po utworzeniu/otwarciu projektu
    mcp__playwright-headless__browser_evaluate(function: "() => {
      const projectId = window.location.pathname.split('/')[2];
      console.log('Project ID:', projectId);
      return projectId;
    }");
    
    // CRITICAL: Zapisz PROJECT_ID dla późniejszego użycia w TODO
    // Project ID format: g-p-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  fi

  1.5. Oczyszczenie widoku (opcjonalne - dla lepszej analizy)

  // Ukryj mylące elementy projektowe przed snapshot
  mcp__playwright-headless__browser_evaluate(function: "() => {
    // Ukryj sekcję 'Add files' (pliki projektowe)
    const buttons = document.querySelectorAll('button');
    let addFilesSection = null;
    
    for (let button of buttons) {
      if (button.textContent?.includes('Add files') && button.textContent?.includes('Chats in this project can access')) {
        addFilesSection = button.parentElement;
        break;
      }
    }
    
    if (addFilesSection) {
      addFilesSection.style.display = 'none';
      addFilesSection.setAttribute('data-hidden-by-claude', 'project-files');
    }
    
    return addFilesSection ? 'Project files section hidden' : 'Section not found';
  }");

  2. Załączenie pliku YAML

  // CRITICAL: Użyj pliku YAML z TODO zadania (z kroku 0)
  // Wyciągnij nazwę pliku z pierwszego niezrealizowanego zadania
  // Format zadania: "[ ] Generate image using scene_NN.yaml"
  
  // Kliknij przycisk "Add photos & files"
  mcp__playwright-headless__browser_click(element: "Add photos & files button");
  
  // Wybierz "Add files" z menu
  mcp__playwright-headless__browser_click(element: "Add files menu option");

  // Wybierz plik z systemu (z TODO zadania)
  mcp__playwright-headless__browser_file_upload(paths: ["/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/[YAML_FROM_TODO]"]);

  3. Wybór narzędzia "Create image"

  // Kliknij przycisk "Choose tool"
  mcp__playwright-headless__browser_click(element: "Choose tool button");

  // Wybierz "Create image" z menu dropdown
  mcp__playwright-headless__browser_click(element: "Create image option");

  4. Wpisanie promptu

  // CRITICAL: ChatGPT używa contenteditable div, NIE textarea!
  // Najpierw znajdź i aktywuj pole tekstowe za pomocą JavaScript
  mcp__playwright-headless__browser_evaluate(function: "() => {
    const contentEditable = document.querySelector('[contenteditable=\"true\"]');
    if (contentEditable) {
      contentEditable.textContent = 'scene_01 - create an image based on the scene, style, and visual specifications described in the attached YAML. The YAML is a blueprint, not the content.';
      contentEditable.dispatchEvent(new Event('input', { bubbles: true }));
      contentEditable.focus();
      return 'Text entered successfully';
    }
    return 'Contenteditable field not found';
  }");

  // UWAGA: NIE używaj browser_type() - ChatGPT ma ukryte textarea i widoczne contenteditable div
  // Tylko contenteditable div pokazuje tekst w interfejsie użytkownika

  5. Uruchomienie generacji

  // Kliknij przycisk "Send prompt" (czarne koło ze strzałką)
  mcp__playwright-headless__browser_click(element: "Send prompt button");

  Stan końcowy:

  - Projekt [BOOK_FOLDER] istnieje i jest otwarty
  - Plik YAML został załączony i jest widoczny w interfejsie
  - Narzędzie "Create image" jest wybrane (widoczne dodatkowe opcje Image/Styles)
  - Prompt jest wpisany w polu tekstowym
  - ChatGPT rozpoczyna generowanie obrazu (pojawia się status "Thinking" → "Reading documents" → "Getting started")
  - Żaden plik nie jest załączony do projektu ("Pliki projektu") - jedyne załączone pliki znajdują się w chatach projektu.

  Weryfikacja sukcesu:

  // Czekaj na pojawienie się statusu "Getting started" (generowanie się rozpoczęło)
  mcp__playwright-headless__browser_wait_for(text: "Getting started");

  6. Aktualizuj TODO list

  // CRITICAL: Wyciągnij thread ID z URL po generowaniu
  // URL zmienia się na: https://chatgpt.com/c/688be9e1-219c-8331-8530-6cd9dd8a7fbc
  // Thread ID = "688be9e1-219c-8331-8530-6cd9dd8a7fbc"
  
  mcp__playwright-headless__browser_evaluate(function: "() => { return window.location.pathname.split('/c/')[1]; }");
  
  // Oznacz zadanie jako rozpoczęte z thread ID (N = numer linii z kroku 0)
  // Format: "[x] [ ] Created thread 688be9e1-219c-8331-8530-6cd9dd8a7fbc for image scene_01.yaml"
  sed -i 'Ns/\[ \] \[ \] Generate image using \(.*\)/[x] [ ] Created thread [THREAD_ID] for image \1/' /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md

  - Projekt [BOOK_FOLDER] został utworzony/otwarty poprawnie
  - Sukcesem jest gdy obraz zaczyna się generować (pojawia się "Getting started")
  - URL zmienia się na nowy conversation thread (c/xxxxx)
  - Status przechodzi przez: "Thinking" → "Reading documents" → "Getting started"
  - TODO zaktualizowane z thread ID i nazwą pliku YAML

  Uwagi techniczne:

  - CRITICAL: Nazwa projektu MUSI być dokładnie taka sama jak [BOOK_FOLDER]
  - Jeśli podano nazwę książki zamiast folderu, użyj find/grep do identyfikacji folderu
  - Zawsze sprawdź czy projekt istnieje PRZED próbą kliknięcia
  - Jeśli projekt nie istnieje - utwórz go zgodnie z procedurą
  - **CRITICAL dla Project ID:** Po utworzeniu/otwarciu projektu zawsze wyciągnij Project ID z URL
    - Project ID format: g-p-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (32 znaki hex)
    - URL format: /g/[PROJECT_ID]/project lub /g/[PROJECT_ID]-[BOOK_FOLDER]/project
    - Użyj prostego split: window.location.pathname.split('/')[2]
    - Zapisz Project ID w TODO-GENERATE.md na końcu pliku dla przyszłej automatyzacji
  - ChatGPT używa React, więc potrzebne są właściwe eventy (focus, input, change)
  - Przycisk send pozostaje disabled dopóki nie ma tekstu w polu input
  - Używaj ZAWSZE MCP playwright-headless calls (nie raw Playwright API)
  - Element refs są dynamiczne - rób browser_snapshot() przed interakcją z elementami
  - NIGDY nie używaj hardcoded refs jak "#prompt-textarea" - zawsze używaj ref z aktualnego snapshot
  - Opisuj elementy naturalnie (np. "Open sidebar button") zamiast używać fake refs
  - Jeśli element nie zostanie znaleziony, zrób browser_snapshot() i spróbuj ponownie
  - **CRITICAL dla pola tekstowego:** ChatGPT używa contenteditable div, NIE textarea!
    - textarea jest ukryte (visible: false) - tekst nie pojawi się w UI
    - contenteditable div jest widoczne (visible: true) - tekst widoczny dla użytkownika
    - ZAWSZE używaj browser_evaluate() z contenteditable, NIGDY browser_type()
  - Projekt zostanie automatycznie otwarty po utworzeniu - nie trzeba dodatkowo klikać

  System statusów TODO-GENERATE.md:
  - [ ] [ ] - thread pending ⏳ + image pending ⏳ (NOT STARTED)
  - [x] [ ] - thread created ✅ + image pending ⏳ (READY TO DOWNLOAD)  
  - [x] [x] - thread created ✅ + image downloaded ✅ (COMPLETED)

  Po rozpoczęciu generacji: [ ] [ ] → [x] [ ] (pierwszy checkbox = thread creation)
  Po pobraniu obrazu: [x] [ ] → [x] [x] (drugi checkbox = image download)

  Tworzenie TODO (jeśli nie istnieje):

  1. Znajdź wszystkie pliki YAML scen

  // CRITICAL: Sprawdź czy istnieją pliki YAML w folderze genimage
  find /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/ -name "scene_*.yaml" | sort

  2. Stwórz TODO file

  // CRITICAL: Zachowaj DOKŁADNĄ KOLEJNOŚĆ plików YAML!
  // Zapisz każdy plik YAML jako osobną linię z PODWÓJNYM STATUSEM:
  [ ] [ ] Generate image using scene_01.yaml
  [ ] [ ] Generate image using scene_02.yaml
  [ ] [ ] Generate image using scene_03.yaml
  
  // Format: "[ ] [ ] Generate image using [FILENAME]"
  // Pierwszy [ ] = thread creation status
  // Drugi [ ] = image download status
  // NIE używaj innych opisów

  3. Dodaj Project ID na końcu TODO file

  // CRITICAL: Zapisz Project ID otrzymany z kroku 2 na końcu TODO-GENERATE.md
  echo "" >> /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md
  echo "# PROJECT_ID = [PROJECT_ID_FROM_BROWSER]" >> /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/prompts/genimage/TODO-GENERATE.md
  
  // Przykład końcowego formatu TODO-GENERATE.md:
  // [ ] [ ] Generate image using scene_01.yaml
  // [ ] [ ] Generate image using scene_02.yaml
  // ...
  // [ ] [ ] Generate image using scene_25.yaml
  //
  // # PROJECT_ID = g-p-688bf3470db48191ae565a014f7e8429

  Weryfikacja sukcesu tworzenia TODO:

  - Plik TODO-GENERATE.md został utworzony w /books/[BOOK_FOLDER]/prompts/genimage/
  - Zawiera wszystkie pliki YAML jako osobne zadania z podwójnym statusem
  - Każda linia zaczyna się od "[ ] [ ] Generate image using" 
  - Pierwszy [ ] = thread creation status, drugi [ ] = image download status
  - Pliki są w kolejności numerycznej (scene_01, scene_02, etc.)
  - Project ID jest zapisany na końcu pliku jako "# PROJECT_ID = g-p-xxxx..."
  - W przypadku gdyby jakiś plik został załączony do projektu, należy go natychmiast usunąć. Nie może być żadnych plików projektów. Jedyne pliki załączone są dozwolone w chatach projektu.