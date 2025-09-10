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
- Tekst instrukcji TikTok-style (stały dla wszystkich generacji)

Kroki orchestratora:

0. Pobranie zadania i określenie odpowiedniego NotebookLM

// Znajdź zadania gdzie audio_gen jest pending (używamy find_subitems_by_status)
pending_audio_tasks = mcp__todoit__todo_find_subitems_by_status(
  list_key: "cc-au-notebooklm",
  conditions: {
    "afa_gen": "completed",
    "audio_gen": "pending"
  },
  limit: 1
)

if (pending_audio_tasks exists && pending_audio_tasks.matches.length > 0):
  // Pobierz pierwszy matching parent item
  SOURCE_NAME = pending_audio_tasks.matches[0].parent.item_key
  
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

5. Wybór formatu i wpisanie instrukcji - integracja z AFA

// ETAP 5A: Odczyt analizy AFA dla książki
afa_document_path = "books/" + SOURCE_NAME + "/docs/" + SOURCE_NAME + "-afa.md"

if (file_exists(afa_document_path)):
  // Odczytaj dokument AFA aby wydobyć format i prompty
  afa_content = Read(afa_document_path)
  
  // Wyodrębnij z AFA:
  // 1. chosen_format (np. "Mistrz i Uczeń")
  // 2. duration_min (np. 14)
  // 3. Sekcja "## PROMPTY A/B DLA FORMATU"
  // 4. Sekcja "## KLUCZOWE WĄTKI Z WIARYGODNOŚCIĄ"
  
  chosen_format = extract_chosen_format(afa_content)  // np. "Mistrz i Uczeń"
  duration_min = extract_duration(afa_content)        // np. 14
  prompt_A = extract_prompt_A(afa_content)            // prompt dla prowadzącego A
  prompt_B = extract_prompt_B(afa_content)            // prompt dla prowadzącego B
  key_threads = extract_key_threads(afa_content)      // 5 głównych wątków
  
  // Zbuduj instrukcje na podstawie AFA
  TIKTOK_INSTRUCTIONS_FROM_AFA = build_afa_instructions(chosen_format, duration_min, prompt_A, prompt_B, key_threads)
  
  selected_instructions = TIKTOK_INSTRUCTIONS_FROM_AFA

else:
  // FALLBACK: Jeśli brak AFA, użyj uproszczonej logiki
  
  book_findings_path = "books/" + SOURCE_NAME + "/docs/findings/"
  has_controversy = check_file_exists(book_findings_path + "au-research_dark_drama.md")
  has_philosophy = check_file_exists(book_findings_path + "au-research_symbols_meanings.md") 
  has_youth_content = check_file_exists(book_findings_path + "au-research_youth_digital.md")

  // FALLBACK FORMAT: PRZYJACIELSKA WYMIANA (format 1)
  FALLBACK_FORMAT = """
CEL: """ + duration_estimate + """ min dynamicznej rozmowy dwójki przyjaciół o książce. Naturalny flow, organiczne przejścia, energia typowa dla TikToka.

PROWADZĄCY: Dwoje przyjaciół - naturalna chemia, czasem się nie zgadzają, używają prostego języka młodzieżowego (ale nie przesadzają).

STRUKTURA ELASTYCZNA:
• HAK (0:00-0:15): Mocne otwarcie - kontrowersyjne stwierdzenie lub zaskakujące pytanie
• ESENCJA (0:15-1:30): O czym książka + dlaczego wciąż aktualna w 2025
• PING-PONG (1:30-5:00): Naturalna wymiana zdań, anegdoty, spory, przykłady z życia
• FAKTY: Wplatane ORGANICZNIE co 60-90s - tylko gdy pasują do rozmowy
• POLSKI KONTEKST: Odniesienia do polskiej popkultury, memy, sytuacje z polskiego życia
• ZAMKNIĘCIE: Mocny punchline + pytanie do widzów

TON: Lekki, energiczny, autentyczny. Jak rozmowa na korytarzu w szkole.
"""
  
  duration_estimate = "6-8"  // domyślny czas
  selected_instructions = FALLBACK_FORMAT

// ETAP 5B: Funkcje pomocnicze do parsowania AFA

function extract_chosen_format(afa_content):
  // Znajdź linię: "- **Główny**: [NAZWA FORMATU] — [uzasadnienie]"
  // Wyodrębnij nazwę formatu między "**: " a " —"
  pattern = /\*\*Główny\*\*:\s*(.+?)\s*—/
  match = afa_content.match(pattern)
  return match ? match[1] : "Przyjacielska wymiana"

function extract_duration(afa_content):
  // Znajdź linię: "- **Długość**: XX min"
  pattern = /\*\*Długość\*\*:\s*(\d+)\s*min/
  match = afa_content.match(pattern)
  return match ? parseInt(match[1]) : 8

function extract_prompt_A(afa_content):
  // Znajdź sekcję "### Prowadzący A — [rola]" i wyodrębnij prompt
  pattern = /### Prowadzący A[^`]*```([^`]+)```/s
  match = afa_content.match(pattern)
  return match ? match[1] : "Standardowy prompt A"

function extract_prompt_B(afa_content):
  // Znajdź sekcję "### Prowadzący B — [rola]" i wyodrębnij prompt
  pattern = /### Prowadzący B[^`]*```([^`]+)```/s
  match = afa_content.match(pattern)
  return match ? match[1] : "Standardowy prompt B"

function extract_key_threads(afa_content):
  // Znajdź sekcję "## KLUCZOWE WĄTKI Z WIARYGODNOŚCIĄ" i wyodrębnij 5 wątków
  threads_section = extract_section(afa_content, "KLUCZOWE WĄTKI Z WIARYGODNOŚCIĄ")
  // Parsuj wątki z format: "### N. Tytuł wątku"
  return parse_threads(threads_section)

function build_afa_instructions(format_name, duration, promptA, promptB, threads):
  return """
CEL: """ + duration + """ min rozmowy w formacie: """ + format_name + """

PROWADZĄCY A: """ + promptA + """

PROWADZĄCY B: """ + promptB + """

KLUCZOWE WĄTKI DO OMÓWIENIA:
""" + format_threads_for_notebooklm(threads) + """

STRUKTURA CZASOWA:
• Wprowadzenie (0:00-0:30): Przedstawienie tematu i formatu
• Rozwój wątków (0:30-""" + (duration-2) + """:00): Omówienie kluczowych wątków
• Zamknięcie (""" + (duration-2) + """:00-""" + duration + """:00): Podsumowanie i CTA

TON: Dopasowany do wybranego formatu, naturalny dialog bez długich monologów.
"""

// ETAP 5D: Funkcje pomocnicze - implementacja

function extract_section(content, section_name):
  // Znajdź sekcję po nazwie i zwróć jej zawartość do następnej sekcji ##
  start_pattern = "## " + section_name
  end_pattern = "## "
  
  start_index = content.indexOf(start_pattern)
  if (start_index == -1) return ""
  
  next_section = content.indexOf(end_pattern, start_index + start_pattern.length)
  if (next_section == -1) next_section = content.length
  
  return content.substring(start_index, next_section)

function parse_threads(threads_section):
  // Wyodrębnij wątki w formacie: "### 1. Tytuł wątku"
  pattern = /###\s*\d+\.\s*(.+)/g
  threads = []
  let match
  
  while ((match = pattern.exec(threads_section)) !== null) {
    threads.push(match[1])
  }
  
  return threads.slice(0, 5)  // maksymalnie 5 wątków

function format_threads_for_notebooklm(threads):
  if (!threads || threads.length == 0) {
    return "• Omówcie kluczowe aspekty książki zgodnie z waszą wiedzą"
  }
  
  formatted = ""
  for (i = 0; i < threads.length; i++) {
    formatted += "• " + threads[i] + "\n"
  }
  
  return formatted

// Dodaj uniwersalną stopkę do wybranego formatu
UNIVERSAL_FOOTER = """

UNIWERSALNE ZASADY (dla wszystkich formatów):
• BRANDING: "37stopni" to nazwa systemu medialnego podcastów o literaturze, filmie, muzyce i grach - wymowa: "trzydzieści siedem stopni"
• WPROWADZENIE: MUSI zawierać nazwę podcastu "trzydzieści siedem stopni" w pierwszych zdaniach. Przykłady:
  - "Dzisiaj w trzydziestu siedmiu stopniach omawiamy [tytuł] - kultową lekturę, która..."
  - "Trzydzieści siedem stopni! Dziś rozprawiamy o [tytuł]..."  
  - "Goorączki czytania! Dziś rozprawiamy o [tytuł]..."
  - "Witajcie w trzydziestu siedmiu stopniach - miejscu gdzie klasyka spotyka się z TikTokiem! Dziś na warsztat bierzemy [tytuł]..."
  - Możesz tworzyć własne warianty, ale ZAWSZE musisz wspomnieć "trzydzieści siedem stopni" na początku
• ZAKOŃCZENIE: "Jeśli podobał wam się ten odcinek trzydziestu siedmiu stopni, koniecznie zostawcie komentarz! Znajdziecie nas na wszystkich platformach jako "37stopni" - Facebook, Instagram, YouTube i oczywiście TikTok. Więcej materiałów czeka na was na www.37stopni.info. Do usłyszenia w kolejnym odcinku gorączki czytania!"
• Mówcie po polsku, naturalnie, bez tłumaczenia angielskich zwrotów na siłę
• Odniesienia do polskiej rzeczywistości 2025 - TikTok, szkoła, popkultura PL
• Fakty i liczby tylko gdy naprawdę coś wnoszą, nie na siłę
• Jeden CTA na końcu wystarczy - nie męczcie widzów ciągłym "dajcie znać"
• Humor mile widziany ale nie wymuszony - naturalne żarty gdy pasują
"""

// ETAP 5C: Finalizacja instrukcji z uniwersalną stopką
TIKTOK_INSTRUCTIONS = selected_instructions + UNIVERSAL_FOOTER

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
  // Oznacz subitem audio_gen jako completed
  mcp__todoit__todo_update_item_status(
    list_key: "cc-au-notebooklm",
    item_key: SOURCE_NAME,
    subitem_key: "audio_gen",
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
- NEW: Instrukcje są dynamiczne i bazują na analizie AFA lub fallback dla książek bez AFA
- NEW: Preferowany format i długość odcinka określane przez system AFA (12 formatów z rotacją)
- NEW: Prompty A/B dostosowane do specyfiki książki i wybranego formatu dialogowego
- Orchestrator wykonuje JEDEN pełny cykl generacji
- NotebookLM pozwala na równoległe generowanie wielu audio
- Weryfikacja opiera się na obecności wskaźników generacji w interfejsie
- System nie czeka na ukończenie generacji - tylko na jej rozpoczęcie

Obsługa błędów:

- Brak źródła [SOURCE_NAME] → komunikat błędu i zakończenie
- Brak dokumentu AFA → użycie fallback formatu "Przyjacielska wymiana"
- Błędny format AFA → użycie fallback z logowaniem ostrzeżenia
- Błąd parsowania promptów AFA → użycie standardowych promptów
- Problemy z nawigacją → retry z browser_snapshot
- Błędy kliknięcia → sprawdzenie overlay i retry z Escape
- Brak wskaźników generacji → komunikat o niepowodzeniu
- Przypadkowe kliknięcie głównego przycisku → generacja z domyślnymi ustawieniami (błąd operatora)

Stan końcowy:

- Źródło [SOURCE_NAME] zaznaczone w zakładce Źródła
- Nowa generacja audio rozpoczęta z instrukcjami opartymi na analizie AFA lub fallback
- Format audio dobrany zgodnie z systemem AFA (12 formatów) lub fallback "Przyjacielska wymiana"
- Prompty A/B dostosowane do specyfiki książki i wybranego formatu dialogowego
- Subitem audio_gen dla [SOURCE_NAME] oznaczony jako completed w liście cc-au-notebooklm
- Interfejs NotebookLM gotowy do kolejnych operacji
- Raport o statusie generacji, wybranym formacie i aktualnym stanie systemu
