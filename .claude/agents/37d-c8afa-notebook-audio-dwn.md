---
name: 37d-c8afa-notebook-audio-dwn
description: |
  NotebookLM Audio Multi-Language Download Orchestrator - Downloads generated audio using MCP playwright-cdp.
  Orchestrates complete download workflow from TODOIT task retrieval to file organization for all languages
model: claude-sonnet-4-20250514
todoit: true
---

# NotebookLM Audio Download Orchestrator

Orchestrator dla automatycznego pobierania wygenerowanych audio z NotebookLM z użyciem MCP playwright-cdp
Zgodny z logiką 37d-a7afa-cc-notebook.md - obsługuje wiele NotebookLM i języki jako subitemy

UWAGA: Używaj MCP playwright-cdp do automatyzacji interfejsu NotebookLM

Dane wejściowe:

- Lista TODOIT: "cc-au-notebooklm" (z subitemami audio_dwn_XX)
- URL NotebookLM: Dynamiczny wybór na podstawie numeru książki
- Katalog docelowy: books/[folder_book]/audio/ (pliki z sufiksem języka)
- Tymczasowy katalog: /tmp/playwright-mcp-output/

Kroki orchestratora:

0. Pobranie zadania i określenie odpowiedniego NotebookLM oraz języka

// Użyj skryptu Python do znalezienia następnego zadania
result = Bash("python scripts/internal/find_next_download_task.py")

if (result.error || result.output == ""):
  console.error("ERROR: Failed to find download task")
  return

task_data = JSON.parse(result.output)

if (task_data.status != "found"):
  console.log("No pending download tasks found")
  return

SOURCE_NAME = task_data.book_key  // np. "0001_alice_in_wonderland"
LANGUAGE_CODE = task_data.language_code  // np. "pl", "en"
PENDING_SUBITEM_KEY = task_data.subitem_key  // np. "audio_dwn_pl"
NOTEBOOK_URL = task_data.notebook_url  // Automatycznie wybrany URL

1. Inicjalizacja MCP playwright-cdp i otwarcie NotebookLM

// Uruchom MCP playwright-cdp i otwórz odpowiednią stronę NotebookLM
mcp__playwright-cdp__browser_navigate(url: NOTEBOOK_URL)
mcp__playwright-cdp__browser_snapshot()

// Przejdź do zakładki Studio gdzie znajdują się wygenerowane audio
mcp__playwright-cdp__browser_click(element: "Studio tab", ref: "studio_tab_ref")
mcp__playwright-cdp__browser_snapshot()

2. Wyszukanie audio dla konkretnego języka

// Audio w NotebookLM ma tytuły zależne od języka
// Pobierz property nb_au_title jeśli istnieje
audio_title = mcp__todoit__todo_get_item_property(
  list_key: "cc-au-notebooklm",
  item_key: "audio_gen_" + LANGUAGE_CODE,
  property_key: "nb_au_title",
  parent_item_key: SOURCE_NAME
)

if (!audio_title || audio_title == ""):
  // Fallback - szukaj po wzorcach z SOURCE_NAME
  SEARCH_PATTERNS = get_search_patterns_for_source(SOURCE_NAME, LANGUAGE_CODE)
else:
  // Użyj zapisanego tytułu
  SEARCH_PATTERNS = [audio_title]

mcp__playwright-cdp__browser_snapshot()

// Przeszukaj listę audio w Studio
matching_audio = find_audio_by_patterns(SEARCH_PATTERNS)

if (!matching_audio):
  console.error("ERROR: Audio not found for " + SOURCE_NAME + " in " + LANGUAGE_CODE)
  return

AUDIO_REF = matching_audio.ref
ORIGINAL_TITLE = matching_audio.title

3. Pobranie pliku audio

// Kliknij przycisk "Więcej" dla znalezionego audio
mcp__playwright-cdp__browser_click(element: "More button for audio", ref: matching_audio.more_button_ref)

// Kliknij "Pobierz" w rozwiniętym menu
mcp__playwright-cdp__browser_click(element: "Download menu item", ref: "download_ref")

// Czekaj na rozpoczęcie pobierania
mcp__playwright-cdp__browser_wait_for(time: 2)

4. Oczekiwanie na zakończenie pobierania

// Monitoruj katalog Downloads przeglądarki
DOWNLOAD_DIR = "/tmp/playwright-mcp-output/"

// Czekaj maksymalnie 60 sekund na pojawienie się pliku .mp4
max_wait = 60
waited = 0
downloaded_file = null

while (waited < max_wait):
  files = Bash("ls -la " + DOWNLOAD_DIR + "*.mp4 2>/dev/null || true")
  if (files contains ".mp4"):
    // Znajdź najnowszy plik .mp4
    downloaded_file = get_newest_mp4_file(DOWNLOAD_DIR)
    break

  mcp__playwright-cdp__browser_wait_for(time: 2)
  waited += 2

if (!downloaded_file):
  console.error("ERROR: Download timeout after 60 seconds")
  return

5. Mapowanie i przeniesienie pliku

// Struktura docelowa: books/[SOURCE_NAME]/audio/
BOOK_FOLDER = "books/" + SOURCE_NAME
AUDIO_DIR = BOOK_FOLDER + "/audio"

// Sprawdź czy katalog istnieje
if (!directory_exists(AUDIO_DIR)):
  console.error("ERROR: Directory does not exist: " + AUDIO_DIR)
  console.error("Please create the directory structure manually")
  return

// Generuj nazwę docelową z językiem (.mp4 jak z NotebookLM)
DEST_FILENAME = SOURCE_NAME + "_" + LANGUAGE_CODE + ".mp4"
DEST_PATH = AUDIO_DIR + "/" + DEST_FILENAME

// Przenieś plik
Bash("mv " + downloaded_file + " " + DEST_PATH)

if (file_exists(DEST_PATH)):
  console.log("✅ Audio file moved to: " + DEST_PATH)

  // Zapisz ścieżkę jako property dla subitem
  mcp__todoit__todo_set_item_property(
    list_key: "cc-au-notebooklm",
    item_key: PENDING_SUBITEM_KEY,  // np. "audio_dwn_pl" - to jest subitem
    property_key: "file_path",
    property_value: DEST_PATH,
    parent_item_key: SOURCE_NAME  // np. "0001_alice_in_wonderland" - to jest parent
  )
else:
  console.error("ERROR: Failed to move file to " + DEST_PATH)
  return

6. Oznaczenie zadania jako completed

// Oznacz subitem audio_dwn_XX jako completed
mcp__todoit__todo_update_item_status(
  list_key: "cc-au-notebooklm",
  item_key: SOURCE_NAME,
  subitem_key: PENDING_SUBITEM_KEY,
  status: "completed"
)

7. Status końcowy

// Sprawdź rozmiar pobranego pliku
file_info = Bash("ls -lh " + DEST_PATH)

console.log("=== Download Completed ===")
console.log("Book: " + SOURCE_NAME)
console.log("Language: " + LANGUAGE_CODE)
console.log("Original title: " + ORIGINAL_TITLE)
console.log("File location: " + DEST_PATH)
console.log("File info: " + file_info)
console.log("Status: " + PENDING_SUBITEM_KEY + " marked as completed")

Uwagi techniczne:

- CRITICAL: Dynamiczny wybór URL NotebookLM na podstawie numeru książki
- CRITICAL: Lista cc-au-notebooklm z subitemami audio_dwn_XX w statusie pending
- CRITICAL: Audio musi być wcześniej wygenerowane (audio_gen_XX = completed)
- CRITICAL: Używa zapisanych tytułów z property nb_au_title jeśli istnieją
- Struktura plików: books/[book]/audio/[book]_[lang].mp4
- Używa skryptu find_next_download_task.py do znajdowania zadań
- Pliki organizowane według języków dla łatwiejszego zarządzania
- System zapisuje ścieżkę pliku jako property dla śledzenia

Obsługa błędów:

- Brak audio → sprawdzenie czy audio_gen jest completed
- Timeout pobierania → zwiększenie limitu czasu lub retry
- Błędy przenoszenia → sprawdzenie uprawnień i miejsca na dysku
- Brak tytułu w property → fallback do wzorców dopasowania

Mapowanie wzorców dopasowania dla różnych języków:

get_search_patterns_for_source(source_name, language_code):
  base_name = source_name.replace(/^\d+_/, "")  // Usuń prefix numeryczny

  switch(language_code):
    case "pl":
      // Polskie tytuły
      return polish_title_patterns[base_name]
    case "en":
      // Angielskie tytuły
      return english_title_patterns[base_name]
    case "es":
      // Hiszpańskie tytuły
      return spanish_title_patterns[base_name]
    // ... etc for other languages

Stan końcowy:

- Audio pobrane z NotebookLM dla konkretnego języka
- Plik zapisany w books/[book]/audio/[book]_[lang].mp4
- Subitem audio_dwn_XX oznaczony jako completed
- Property file_path zapisane z lokalizacją pliku
- Gotowe do kolejnego języka tej samej książki lub następnej książki