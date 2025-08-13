# Custom Command: 37d-c6-notebook-audio-download - NotebookLM Audio Download Orchestrator

Orchestrator dla automatycznego pobierania wygenerowanych audio z NotebookLM z użyciem MCP playwright-cdp

UWAGA: 
- Używaj MCP playwright-cdp do automatyzacji interfejsu NotebookLM i pobierania plików
- Każdy krok MUSI być wykonany

Dane wejściowe:

- Lista TODOIT: "notebooklm-audio-download" (automatyczne pobieranie kolejnego zadania)
- URL NotebookLM: https://notebooklm.google.com/notebook/700b4b7c-976f-4026-96f0-f1240bd69530?authuser=2
- Katalog docelowy: books/[folder_book]/audio (automatyczne mapowanie na podstawie item_key)
- Tymczasowy katalog: /tmp/playwright-mcp-output/[timestamp]/*.m4a

Kroki orchestratora:

0. Inicjalizacja MCP playwright-cdp i otwarcie NotebookLM

// Uruchom MCP playwright-cdp i otwórz stronę NotebookLM
mcp__playwright-cdp__browser_navigate(url: "https://notebooklm.google.com/notebook/700b4b7c-976f-4026-96f0-f1240bd69530")
mcp__playwright-cdp__browser_snapshot()

// Przejdź do zakładki Studio gdzie znajdują się wygenerowane audio
mcp__playwright-cdp__browser_click(element: "Studio", ref: "...")
mcp__playwright-cdp__browser_snapshot()

1. Pobranie następnego zadania z listy TODOIT

// Pobierz następne pending zadanie z listy notebooklm-audio-download
next_task = mcp__todoit__todo_get_next_pending(list_key: "notebooklm-audio-download")

if (next_task exists):
  SOURCE_NAME = next_task.item_key
  echo "📋 Pobrano zadanie: " + SOURCE_NAME + " - " + next_task.content
else:
  echo "ℹ️ Brak pending zadań w liście notebooklm-audio-download"
  return

2. Wyszukanie i dopasowanie audio do pobrania w Studio

// Studio już otwarte w Step 0

// UWAGA: Audio w NotebookLM ma tytuły jak "Jane Eyre: Feministyczna Ikona czy Problematic Fave..."
// ale item_key to "0014_jane_eyre" - trzeba dopasować wzorcem
SEARCH_PATTERNS = get_search_patterns_for_source(SOURCE_NAME)
// np. dla "0001_alice_in_wonderland" zwraca ["Alice", "Alicja", "Wonderland", "Krainie Czarów"]

mcp__playwright-cdp__browser_snapshot()

// Przeszukaj listę audio w Studio i dopasuj po wzorcach
matching_audios = []
for each audio_item in studio_audio_list:
  for each pattern in SEARCH_PATTERNS:
    if (audio_item.title contains pattern):
      matching_audios.add(audio_item)
      break  // Przejdź do następnego audio (jeden match wystarczy)

if (matching_audios.length == 0):
  echo "❌ BŁĄD: Nie znaleziono audio odpowiadającego " + SOURCE_NAME
  echo "Dostępne audio w Studio:"
  list_all_audio_titles_in_studio()
  echo "Sprawdź wzorce dopasowania lub czy audio zostało wygenerowane"
  return
elif (matching_audios.length == 1):
  found_audio = matching_audios[0]
  echo "✅ Znaleziono audio dla źródła " + SOURCE_NAME
  echo "Dopasowane audio: " + found_audio.title
else:
  // Więcej niż 1 dopasowanie - wybierz najnowsze (pierwsze na liście)
  found_audio = matching_audios[0]  // Lista jest sortowana chronologicznie (najnowsze pierwsze)
  echo "⚠️ Znaleziono " + matching_audios.length + " audio dla źródła " + SOURCE_NAME
  echo "Wybrano najnowsze: " + found_audio.title + " (" + found_audio.timestamp + ")"
  echo "Inne dopasowania:"
  for i=1 to matching_audios.length-1:
    echo "  - " + matching_audios[i].title + " (" + matching_audios[i].timestamp + ")"

AUDIO_REF = found_audio.more_button_ref

3. Zmiana nazwy audio na SOURCE_NAME (wykonać bezwzględnie!)

// Kliknij przycisk "Więcej" dla znalezionego audio
mcp__playwright-cdp__browser_click(element: "Więcej button for " + found_audio.title, ref: found_audio.more_button_ref)

// Kliknij "Zmień nazwę" w rozwiniętym menu
mcp__playwright-cdp__browser_click(element: "Zmień nazwę menu item", ref: "zmien_nazwe_ref")

// Wpisz SOURCE_NAME jako nową nazwę (np. "0003_anna_karenina")
mcp__playwright-cdp__browser_type(element: "Title textbox for audio rename", ref: "title_textbox_ref", text: SOURCE_NAME)

// Zatwierdź zmianę nazwy (Enter)
mcp__playwright-cdp__browser_press_key(key: "Enter")

echo "✅ Zmieniono nazwę audio z '" + found_audio.title + "' na '" + SOURCE_NAME + "'"

// Krótkie oczekiwanie na zaktualizowanie interfejsu
mcp__playwright-cdp__browser_wait_for(time: 2)

4. Pobranie pliku audio

// Kliknij przycisk "Więcej" dla audio o zmienionej nazwie (teraz SOURCE_NAME)
mcp__playwright-cdp__browser_click(element: "Więcej button for " + SOURCE_NAME, ref: audio_more_button_ref)

// Kliknij "Pobierz" w rozwiniętym menu
mcp__playwright-cdp__browser_click(element: "Pobierz menu item", ref: "pobierz_ref")

// Czekaj na rozpoczęcie pobierania (może być potrzebny krótki timeout)
mcp__playwright-cdp__browser_wait_for(time: 2)

echo "✅ Pobieranie pliku audio dla " + SOURCE_NAME + " rozpoczęte"

5. Oczekiwanie na zakończenie pobierania

// Sprawdź katalog tymczasowy w poszukiwaniu nowego pliku .m4a
TIMESTAMP = current_timestamp()
TEMP_DIR = "/tmp/playwright-mcp-output/" + TIMESTAMP

// Czekaj maksymalnie 30 sekund na pojawienie się pliku
wait_for_download_completion(TEMP_DIR, "*.m4a", max_wait_seconds: 30)

downloaded_files = list_files(TEMP_DIR, "*.m4a")

if (downloaded_files.length > 0):
  DOWNLOADED_FILE = downloaded_files[0]  // Pierwszy znaleziony plik .m4a
  echo "✅ Plik pobrany: " + DOWNLOADED_FILE
else:
  echo "❌ BŁĄD: Nie udało się pobrać pliku audio w ciągu 30 sekund"
  return

6. Mapowanie SOURCE_NAME na folder książki

// Mapowanie item_key na folder książki w strukturze books/
// Przykład: 0014_jane_eyre -> books/0014_jane_eyre
BOOK_FOLDER = "books/" + SOURCE_NAME

// Sprawdź czy folder książki istnieje
if (directory_exists(BOOK_FOLDER)):
  AUDIO_DIR = BOOK_FOLDER + "/audio"
  echo "✅ Znaleziono folder książki: " + BOOK_FOLDER
else:
  echo "❌ BŁĄD: Nie znaleziono folderu książki " + BOOK_FOLDER
  echo "Sprawdź strukturę katalogów projektu"
  return

7. Przeniesienie pliku

// Generuj nazwę docelową pliku na podstawie SOURCE_NAME
DEST_FILENAME = SOURCE_NAME + ".m4a"
DEST_PATH = AUDIO_DIR + "/" + DEST_FILENAME

// Przenieś plik z katalogu tymczasowego do docelowego
move_file(DOWNLOADED_FILE, DEST_PATH)

if (file_exists(DEST_PATH)):
  echo "✅ Plik audio przeniesiony do: " + DEST_PATH
else:
  echo "❌ BŁĄD: Nie udało się przenieść pliku do " + DEST_PATH
  return

8. Oznaczenie zadania jako completed

// Oznacz zadanie jako completed w liście TODOIT jesli udało się poprawnie przenieść do katalogu docelowego
mcp__todoit__todo_mark_completed(
  list_key: "notebooklm-audio-download",
  item_key: SOURCE_NAME
)
echo "✅ Zadanie " + SOURCE_NAME + " oznaczone jako completed w liście notebooklm-audio-download"

9. Status końcowy

// Sprawdź rozmiar pobranego pliku
file_size = get_file_size(DEST_PATH)
file_duration = get_audio_duration(DEST_PATH)  // jeśli dostępne

echo "Status pobierania:"
echo "- Źródło: " + SOURCE_NAME
echo "- Plik docelowy: " + DEST_PATH  
echo "- Rozmiar: " + file_size + " bytes"
if (file_duration):
  echo "- Czas trwania: " + file_duration
echo "- Status: Pobrane i przeniesione pomyślnie"

Uwagi techniczne:

- CRITICAL: URL NotebookLM musi być aktywny i dostępny
- CRITICAL: Lista notebooklm-audio-download musi istnieć z pending zadaniami
- CRITICAL: Audio dla SOURCE_NAME musi być już wygenerowane i dostępne w Studio
- CRITICAL: Folder books/[SOURCE_NAME] musi istnieć w strukturze projektu
- CRITICAL: Wyszukiwanie audio odbywa się po dopasowaniu SOURCE_NAME z tytułami audio
- CRITICAL: Jeśli istnieje więcej niż 1 audio dla tej samej książki, wybiera najnowsze (pierwsze na liście chronologicznej)
- Lista audio w NotebookLM Studio jest sortowana chronologicznie (najnowsze na górze)
- System loguje wszystkie znalezione dopasowania dla transparentności
- Pliki pobierają się do katalogu tymczasowego /tmp/playwright-mcp-output/[timestamp]/*.m4a
- System automatycznie tworzy katalog books/[SOURCE_NAME]/audio jeśli nie istnieje
- Nazwa docelowa pliku: [SOURCE_NAME].m4a (np. 0014_jane_eyre.m4a)
- Orchestrator wykonuje JEDEN pełny cykl pobierania dla jednego źródła
- Po pobraniu katalog tymczasowy jest czyszczony

Obsługa błędów:

- Brak audio dla [SOURCE_NAME] → komunikat błędu i zakończenie
- Problemy z pobieraniem → timeout i komunikat o niepowodzeniu
- Błędy przenoszenia pliku → sprawdzenie uprawnień i dostępności
- Brak folderu książki → komunikat o błędnej strukturze projektu

Mapowanie nazw plików:

- System zmienia nazwę audio w NotebookLM na SOURCE_NAME (np. "0003_anna_karenina")
- NotebookLM generuje plik: "0003-anna-karenina.m4a" (podkreślniki → myślniki)
- System mapuje item_key (np. "0014_jane_eyre") na folder "books/0014_jane_eyre"
- Docelowa nazwa: "0014_jane_eyre.m4a" w katalogu "books/0014_jane_eyre/audio/"

Stan końcowy:

- Nazwa audio w NotebookLM zmieniona na [SOURCE_NAME]
- Audio [SOURCE_NAME] pobrane z NotebookLM Studio jako [SOURCE_NAME-formatted].m4a
- Plik przeniesiony do books/[SOURCE_NAME]/audio/[SOURCE_NAME].m4a
- Zadanie [SOURCE_NAME] oznaczone jako completed w liście notebooklm-audio-download
- Katalog tymczasowy wyczyszczony
- Raport o statusie pobierania i lokalizacji pliku

## Mapowanie wzorców dopasowania item_key → audio tytuły

**UWAGA:** Po implementacji zmiany nazwy (Krok 3), to mapowanie jest używane tylko do **wyszukiwania i identyfikacji** audio w Studio, a nie do pobierania.

**Przykłady dopasowania dla identyfikacji:**
- `0001_alice_in_wonderland` → ["Alice", "Alicja", "Wonderland", "Krainie Czarów"]
- `0014_jane_eyre` → ["Jane Eyre", "Jane", "Eyre", "Feministyczna"]  
- `0007_dune` → ["Dune", "Diuna", "Wydm", "Arrakis"]
- `0012_harry_potter` → ["Harry Potter", "Harry", "Potter", "Fenomenu"]
- `0021_nineteen_eighty_four` → ["1984", "Nineteen Eighty", "Orwell", "Big Brother"]

**Strategia dopasowania (tylko identyfikacja):**
1. Usuń prefix numeryczny (0001_, 0014_ itp.)
2. Zamień podkreślniki na spacje
3. Dodaj popularne polskie tłumaczenia tytułów
4. Dodaj słowa kluczowe z tytułów audio
5. Szukaj pierwszego dopasowania w kolejności priorytetów

**Proces optymalizowany:**
1. **Identyfikacja** → Znajdź audio używając wzorców dopasowania
2. **Zmiana nazwy** → Zmień nazwę na SOURCE_NAME (np. "0003_anna_karenina")  
3. **Pobieranie** → Pobierz audio o zmienionej nazwie (przewidywalna nazwa pliku)

**CRITICAL:** System musi obsługiwać zarówno angielskie tytuły jak i polskie tłumaczenia 
przy **identyfikacji** audio, ale po zmianie nazwy proces pobierania jest zunifikowany.