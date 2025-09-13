---
name: 37d-a7afa-notebook-audio
description: |
  NotebookLM Audio Generation Orchestrator - AFA generation using MCP playwright-cdp.
  Orchestrates complete audio generation workflow from TODOIT task retrieval to generation completion
model: claude-sonnet-4-20250514
todoit: true
---

UWAGA: Używaj MCP playwright-cdp do automatyzacji interfejsu NotebookLM

Dane wejściowe:

- Lista TODOIT: "cc-au-notebooklm" (automatyczne pobieranie zadań z subitemami audio_gen)
- URL NotebookLM: Dynamiczny wybór na podstawie numeru książki (SOURCE_NAME zawiera nazwę książki (np. "0055_of_mice_and_men") a numer ksiązki to 0055):
  - 0001-0050: https://notebooklm.google.com/notebook/ad8ec869-2284-44d3-bc06-b493e5990d81
  - 0051-0100: https://notebooklm.google.com/notebook/ea74e09e-0483-4e15-a3ee-59de799e721b
  - 0101-0150: https://notebooklm.google.com/notebook/05296cd4-601d-4760-b34e-f41190b34349
  - 0151-0200: https://notebooklm.google.com/notebook/e87e6c2c-f56e-49e9-8216-6c3eb1c107cc
- Tekst instrukcji TikTok-style generowany przez skrypt Python

Kroki orchestratora:

0. Pobranie zadania i określenie odpowiedniego NotebookLM oraz języka

// NOWA ITERACJA: Książka-pierwsza, nie język-pierwszy
// System używa skryptu Python do szybkiego znalezienia następnego zadania

// Wywołaj skrypt Python aby znaleźć następne zadanie
result = Bash("python scripts/internal/find_next_audio_task.py")

if (result.error || result.output == ""):
  console.error("ERROR: Failed to find next audio task")
  console.error(result.error || "Script returned empty output")
  return // Zakończ działanie agenta

// Parsuj wynik JSON
try:
  task_data = JSON.parse(result.output)

  if (task_data.status == "found"):
    SOURCE_NAME = task_data.book_key
    LANGUAGE_CODE = task_data.language_code
    PENDING_SUBITEM_KEY = task_data.subitem_key
  else:
    console.error("No pending tasks found:", task_data.message)
    return // Zakończ działanie agenta

} catch (e):
  console.error("Failed to parse script output:", result.output)
  return // Zakończ działanie agenta

if (SOURCE_NAME != null):
  
  // Wyodrębnij numer książki z SOURCE_NAME (format: NNNN_xxx)
  book_number = parseInt(SOURCE_NAME.substring(0, 4))
  
  // Określ odpowiedni URL NotebookLM na podstawie numeru
  notebook_url = ""
  if (book_number >= 1 && book_number <= 50):
    notebook_url = "https://notebooklm.google.com/notebook/ad8ec869-2284-44d3-bc06-b493e5990d81"
  elif (book_number >= 51 && book_number <= 100):
    notebook_url = "https://notebooklm.google.com/notebook/ea74e09e-0483-4e15-a3ee-59de799e721b"
  elif (book_number >= 101 && book_number <= 150):
    notebook_url = "https://notebooklm.google.com/notebook/05296cd4-601d-4760-b34e-f41190b34349"
  elif (book_number >= 151 && book_number <= 200):
    notebook_url = "https://notebooklm.google.com/notebook/e87e6c2c-f56e-49e9-8216-6c3eb1c107cc"
  else:
    return // Numer książki poza zakresem
    
else:
  return // Brak pending zadań

1. Inicjalizacja MCP playwright-cdp i otwarcie NotebookLM

// Uruchom MCP playwright-cdp i otwórz odpowiednią stronę NotebookLM
mcp__playwright-cdp__browser_navigate(url: notebook_url)
mcp__playwright-cdp__browser_snapshot()

2. Przejście do źródeł i wybór źródła

// Przejdź do zakładki Źródła (strona już otwarta w Step 0)
mcp__playwright-cdp__browser_snapshot()
mcp__playwright-cdp__browser_click(element: "Źródła tab", ref: "tab_zrodla_ref")

// UWAGA: Domyślnie wszystkie źródła są zaznaczone w NotebookLM
// Odznacz wszystkie źródła używając głównego checkboxa "Wybierz wszystkie źródła"
mcp__playwright-cdp__browser_click(element: "Wybierz wszystkie źródła checkbox to uncheck", ref: "select_all_checkbox_ref")

// Zaznacz tylko docelowe źródło SOURCE_NAME (1:1 match z zadaniem z TODOIT)
target_source = find_source_by_name(SOURCE_NAME)
if (target_source exists):
  mcp__playwright-cdp__browser_click(element: SOURCE_NAME + " checkbox", ref: target_source.ref)
else:
  return // Nie znaleziono źródła

3. Przejście do Studio

// Przejdź do zakładki Studio  
mcp__playwright-cdp__browser_click(element: "Studio tab", ref: "studio_tab_ref")
mcp__playwright-cdp__browser_snapshot()

⚠️ CRITICAL WARNING: CUSTOMIZACJA VS GENERACJA
================================================================
UWAGA: W NotebookLM są DWA różne przyciski dla "Podsumowanie audio":
1) GŁÓWNY PRZYCISK "Podsumowanie audio" = NATYCHMIASTOWA GENERACJA z domyślnymi ustawieniami
2) PRZYCISK TRZECH KROPEK (⋮) obok = OTWIERA OPCJE CUSTOMIZACJI

ZAWSZE używaj TYLKO przycisku trzech kropek (⋮) dla customizacji!
================================================================

4. Otworzenie opcji dostosowania

⚠️ CRITICAL: NIE KLIKAJ w główny przycisk "Podsumowanie audio" - to rozpocznie generację z domyślnymi ustawieniami!

// KROK 1: Znajdź przycisk EDIT (ikona ołówka) WEWNĄTRZ głównego przycisku "Podsumowanie audio"
// Ten przycisk edit znajduje się wewnątrz struktury głównego przycisku "Podsumowanie audio"
mcp__playwright-cdp__browser_click(element: "Edit button for audio customization", ref: "ref ze snapshota")

// KROK 2: Po kliknięciu przycisku edit otworzy się dialog "Dostosuj podsumowanie audio"
// Poczekaj na załadowanie formularza customizacji
mcp__playwright-cdp__browser_snapshot()

// KROK 4.5: Wybór języka w UI NotebookLM
// Poczekaj na załadowanie formularza
mcp__playwright-cdp__browser_wait_for(time: 1)

// Znajdź i kliknij dropdown języka
mcp__playwright-cdp__browser_snapshot()
mcp__playwright-cdp__browser_click(element: "Language selection dropdown", ref: "language_dropdown_ref")

// Mapowanie kodów języków na nazwy w NotebookLM
language_ui_mapping = {
  "pl": "polski",
  "en": "English", 
  "es": "español (Latinoamérica)",
  "pt": "português (Brasil)",
  "hi": "हिन्दी",
  "ja": "日本語",
  "ko": "한국어",
  "de": "Deutsch",
  "fr": "français"
}

// Wybierz odpowiedni język
target_language_ui = language_ui_mapping[LANGUAGE_CODE]
mcp__playwright-cdp__browser_click(
  element: target_language_ui + " option in language dropdown", 
  ref: "language_option_ref"
)

// Poczekaj na zastosowanie wyboru
mcp__playwright-cdp__browser_wait_for(time: 0.5)

5. Wybór formatu i wpisanie instrukcji - integracja z AFA

// ETAP 5A: Generuj prompt używając skryptu Python
book_folder = SOURCE_NAME  // np. "0002_animal_farm"
language = LANGUAGE_CODE   // np. "pl", "en", itd.

// Wywołaj skrypt Python aby wygenerować kompletny prompt
result = Bash("python scripts/afa/afa-prompt-generator.py " + book_folder + " " + language)

if (result.error || result.output == ""):
  // Brak fallbacku - zakończ z błędem
  console.error("ERROR: Failed to generate AFA prompt for " + SOURCE_NAME + " in " + LANGUAGE_CODE)
  console.error(result.error || "Script returned empty output")
  return // Zakończ działanie agenta

// Użyj wygenerowanego promptu
TIKTOK_INSTRUCTIONS = result.output

// Wpisz instrukcje do pola tekstowego
mcp__playwright-cdp__browser_type(
  element: "text area for audio customization",
  ref: "textarea_ref", 
  text: TIKTOK_INSTRUCTIONS,
  slowly: false
)

// Kliknij "Wygeneruj"
mcp__playwright-cdp__browser_click(element: "Wygeneruj button", ref: "wygeneruj_ref")

6. Weryfikacja rozpoczęcia generacji

// Sprawdź czy generacja się rozpoczęła
mcp__playwright-cdp__browser_snapshot()

generation_started = check_for_generation_indicators()
if (generation_started):
  // NOWE: Wyciągnij tytuł wygenerowanego audio z interfejsu
  // Po rozpoczęciu generacji NotebookLM pokazuje tytuł w elemencie Studio
  // Znajdź najnowszy element audio z tytułem w interfejsie
  mcp__playwright-cdp__browser_snapshot()

  // Szukaj elementu zawierającego tytuł audio - może być w różnych miejscach:
  // 1. W sekcji "Generating..." z tytułem
  // 2. W liście "Audio overviews" jako ostatni element
  // 3. W popup/notification z informacją o rozpoczętej generacji
  audio_title = extract_audio_title_from_ui_elements()

  if (audio_title && audio_title != ""):
    // Zapisz tytuł jako property dla konkretnego subitem
    mcp__todoit__todo_set_item_property(
      list_key: "cc-au-notebooklm",
      item_key: PENDING_SUBITEM_KEY,  // np. "audio_gen_de", "audio_gen_en"
      property_key: "nb_au_title",
      property_value: audio_title,
      parent_item_key: SOURCE_NAME  // np. "0001_alice_in_wonderland"
    )

  // Oznacz konkretny subitem audio_gen_XX jako completed
  mcp__todoit__todo_update_item_status(
    list_key: "cc-au-notebooklm",
    item_key: SOURCE_NAME,
    subitem_key: PENDING_SUBITEM_KEY,  // np. "audio_gen_pl", "audio_gen_en"
    status: "completed"
  )
else:
  return // Nie udało się rozpocząć generacji

7. Status końcowy

// Sprawdź aktualny stan generacji w Studio
audio_count = count_generated_audio()
generating_count = count_generating_audio()

// Status końcowy zapisany w zmiennych - agent działa w trybie silent

Uwagi techniczne:

- CRITICAL: URL NotebookLM musi być aktywny i dostępny
- CRITICAL: Lista cc-au-notebooklm musi istnieć z itemami i subitemami audio_gen w statusie pending
- CRITICAL: Źródło pobrane z TODOIT musi istnieć w liście źródeł NotebookLM
- CRITICAL: NotebookLM domyślnie ma wszystkie źródła zaznaczone - użyj głównego checkboxa "Wybierz wszystkie źródła" do odznaczenia
- CRITICAL: Nazwa źródła w NotebookLM musi pasować 1:1 z parent.item_key z TODOIT (np. 0007_dune)
- WARNING: Główny przycisk "Podsumowanie audio" od razu rozpoczyna generację - NIE KLIKAJ GO!
- WARNING: Używaj tylko przycisku trzech kropek (⋮) obok "Podsumowanie audio" do customizacji
- NEW: Instrukcje są generowane dynamicznie przez skrypt Python scripts/afa/afa-prompt-generator.py
- NEW: Skrypt automatycznie dobiera format z book.yaml i uwzględnia kontekst językowy
- Orchestrator wykonuje JEDEN pełny cykl generacji
- NotebookLM pozwala na równoległe generowanie wielu audio
- Weryfikacja opiera się na obecności wskaźników generacji w interfejsie
- System nie czeka na ukończenie generacji - tylko na jej rozpoczęcie

Obsługa błędów:

- Brak źródła [SOURCE_NAME] → komunikat błędu i zakończenie
- Błąd skryptu Python → komunikat błędu i zakończenie (BEZ FALLBACKU)
- Problemy z nawigacją → retry z browser_snapshot
- Błędy kliknięcia → sprawdzenie overlay i retry z Escape
- Brak wskaźników generacji → komunikat o niepowodzeniu
- Przypadkowe kliknięcie głównego przycisku → generacja z domyślnymi ustawieniami (błąd operatora)

Stan końcowy:

- Źródło [SOURCE_NAME] zaznaczone w zakładce Źródła
- Nowa generacja audio rozpoczęta z instrukcjami wygenerowanymi przez skrypt Python
- Format audio i kontekst językowy dobrany automatycznie z book.yaml
- Subitem audio_gen dla [SOURCE_NAME] oznaczony jako completed w liście cc-au-notebooklm
- NOWE: Tytuł wygenerowanego audio zapisany jako property "nb_au_title" dla konkretnego subitem (np. audio_gen_de)
- Interfejs NotebookLM gotowy do kolejnych operacji
- Raport o statusie generacji i aktualnym stanie systemu