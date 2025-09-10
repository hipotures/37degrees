# Custom Command: 37d-c6-notebook-audio - NotebookLM Audio Generation Orchestrator

Orchestrator dla automatycznego generowania audio w NotebookLM z użyciem MCP playwright-cdp

UWAGA: Używaj MCP playwright-cdp do automatyzacji interfejsu NotebookLM

Dane wejściowe:

- Lista TODOIT: "notebooklm-audio" (automatyczne pobieranie kolejnego zadania)
- URL NotebookLM: https://notebooklm.google.com/notebook/700b4b7c-976f-4026-96f0-f1240bd69530?authuser=2
- Tekst instrukcji TikTok-style (stały dla wszystkich generacji)

Kroki orchestratora:

0. Inicjalizacja MCP playwright-cdp i otwarcie NotebookLM

// Uruchom MCP playwright-cdp i otwórz stronę NotebookLM
mcp__playwright-cdp__browser_navigate(url: "https://notebooklm.google.com/notebook/700b4b7c-976f-4026-96f0-f1240bd69530")
mcp__playwright-cdp__browser_snapshot()

1. Pobranie zadania i określenie języka

// Określ język docelowy (parametr lub znajdź pending audio_gen_XX)
TARGET_LANG = get_parameter("lang", default="pl")

// Znajdź zadanie z pending audio_gen_{TARGET_LANG}
pending_tasks = mcp__todoit__todo_find_subitems_by_status(
    list_key="cc-au-notebooklm",
    conditions={f"audio_gen_{TARGET_LANG}": "pending"},
    limit=1
)

if (pending_tasks exists):
  SOURCE_NAME = pending_tasks.matches[0].parent.item_key
  echo "📋 Pobrano zadanie: " + SOURCE_NAME + " dla języka: " + TARGET_LANG
else:
  echo "ℹ️ Brak pending zadań audio_gen_" + TARGET_LANG
  return

// Określ plik AFA i imiona hostów na podstawie języka
if (TARGET_LANG == "pl"):
  AFA_FILE = SOURCE_NAME + "-afa-pl.md"
  HOST_A_NAME = "Andrzej"
  HOST_B_NAME = "Beata"
else:
  AFA_FILE = SOURCE_NAME + "-afa-en.md"
  // Załaduj imiona z konfiguracji dla wybranego języka
  // config/audio_languages.yaml
  if (TARGET_LANG == "en"):
    HOST_A_NAME = "Andrew"
    HOST_B_NAME = "Beth"
  elif (TARGET_LANG == "es"):
    HOST_A_NAME = "Andrés"
    HOST_B_NAME = "Beatriz"
  elif (TARGET_LANG == "pt"):
    HOST_A_NAME = "André"
    HOST_B_NAME = "Beatriz"
  elif (TARGET_LANG == "hi"):
    HOST_A_NAME = "Arjun"
    HOST_B_NAME = "Bhavna"
  elif (TARGET_LANG == "ja"):
    HOST_A_NAME = "Akira"
    HOST_B_NAME = "Beniko"
  elif (TARGET_LANG == "ko"):
    HOST_A_NAME = "Ahn"
    HOST_B_NAME = "Bora"
  elif (TARGET_LANG == "de"):
    HOST_A_NAME = "Andreas"
    HOST_B_NAME = "Brigitte"
  elif (TARGET_LANG == "fr"):
    HOST_A_NAME = "Antoine"
    HOST_B_NAME = "Béatrice"

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
  echo "✅ Źródło " + SOURCE_NAME + " zaznaczone"
else:
  echo "❌ BŁĄD: Nie znaleziono źródła " + SOURCE_NAME
  return

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

// KROK 1: Znajdź przycisk trzech kropek (⋮ more_vert) OBOK "Podsumowanie audio"
// Ten przycisk jest po prawej stronie głównego przycisku "Podsumowanie audio"
mcp__playwright-cdp__browser_click(element: "Przycisk trzech kropek (more_vert) obok Podsumowanie audio", ref: "audio_more_vert_ref")

// KROK 2: Po kliknięciu trzech kropek pojawi się menu - kliknij "Dostosuj" w tym menu: menuitem "Dostosuj"
mcp__playwright-cdp__browser_click(element: "Dostosuj w rozwiniętym menu", ref: "dostosuj_ref")

// KROK 3: Pojawi się formularz customizacji - poczekaj na jego załadowanie
mcp__playwright-cdp__browser_snapshot()

5. Wpisanie instrukcji i generacja

// Odczytaj plik AFA i pobierz instrukcje
AFA_PATH = "books/" + SOURCE_NAME + "/docs/" + AFA_FILE
afa_content = Read(AFA_PATH)

// Wydobądź całą zawartość AFA
// AFA zawiera format, długość, prompty i strukturę - wszystko czego potrzebujemy

// Podstaw imiona hostów w miejsca {imię_A} i {imię_B} w całym dokumencie AFA
afa_content = afa_content.replace("{imię_A}", HOST_A_NAME)
afa_content = afa_content.replace("{imię_B}", HOST_B_NAME)

// Dla języków innych niż polski, możemy dodać nagłówek
if (TARGET_LANG != "pl"):
  language_note = "Language: " + TARGET_LANG.toUpperCase() + "\n"
  language_note += "Hosts: " + HOST_A_NAME + " & " + HOST_B_NAME + "\n\n"
  afa_content = language_note + afa_content

mcp__playwright-cdp__browser_type(
  element: "text area for audio customization",
  ref: "textarea_ref", 
  text: afa_content,
  slowly: false
)

// Kliknij "Wygeneruj"
mcp__playwright-cdp__browser_click(element: "Wygeneruj button", ref: "wygeneruj_ref")

6. Weryfikacja rozpoczęcia generacji

// Sprawdź czy generacja się rozpoczęła
mcp__playwright-cdp__browser_snapshot()

generation_started = check_for_generation_indicators()
if (generation_started):
  echo "✅ Generacja audio dla źródła " + SOURCE_NAME + " rozpoczęta pomyślnie"
  echo "Status: Nowe audio w trakcie generowania..."
  
  // Oznacz zadanie audio_gen_{TARGET_LANG} jako completed w TODOIT
  mcp__todoit__todo_update_item_status(
    list_key: "cc-au-notebooklm",
    item_key: SOURCE_NAME,
    subitem_key: "audio_gen_" + TARGET_LANG,
    status: "completed"
  )
  echo "✅ Zadanie " + SOURCE_NAME + "/audio_gen_" + TARGET_LANG + " oznaczone jako completed"
else:
  echo "❌ BŁĄD: Nie udało się rozpocząć generacji dla " + SOURCE_NAME
  return

7. Status końcowy

// Sprawdź aktualny stan generacji w Studio
audio_count = count_generated_audio()
generating_count = count_generating_audio()

echo "Status NotebookLM:"
echo "- Wygenerowane audio: " + audio_count  
echo "- W trakcie generowania: " + generating_count
echo "- Ostatnie źródło: " + SOURCE_NAME

Uwagi techniczne:

- CRITICAL: URL NotebookLM musi być aktywny i dostępny
- CRITICAL: Lista notebooklm-audio musi istnieć z pending zadaniami
- CRITICAL: Źródło pobrane z TODOIT musi istnieć w liście źródeł NotebookLM
- CRITICAL: NotebookLM domyślnie ma wszystkie źródła zaznaczone - użyj głównego checkboxa "Wybierz wszystkie źródła" do odznaczenia
- CRITICAL: Nazwa źródła w NotebookLM musi pasować 1:1 z item_key z TODOIT (np. 0007_dune)
- WARNING: Główny przycisk "Podsumowanie audio" od razu rozpoczyna generację - NIE KLIKAJ GO!
- WARNING: Używaj tylko przycisku trzech kropek (⋮) obok "Podsumowanie audio" do customizacji
- Tekst instrukcji TikTok-style jest stały dla wszystkich generacji
- Orchestrator wykonuje JEDEN pełny cykl generacji
- NotebookLM pozwala na równoległe generowanie wielu audio
- Weryfikacja opiera się na obecności wskaźników generacji w interfejsie
- System nie czeka na ukończenie generacji - tylko na jej rozpoczęcie

Obsługa błędów:

- Brak źródła [SOURCE_NAME] → komunikat błędu i zakończenie
- Problemy z nawigacją → retry z browser_snapshot
- Błędy kliknięcia → sprawdzenie overlay i retry z Escape
- Brak wskaźników generacji → komunikat o niepowodzeniu
- Przypadkowe kliknięcie głównego przycisku → generacja z domyślnymi ustawieniami (błąd operatora)

Stan końcowy:

- Źródło [SOURCE_NAME] zaznaczone w zakładce Źródła
- Nowa generacja audio rozpoczęta z instrukcjami TikTok-style  
- Zadanie [SOURCE_NAME] oznaczone jako completed w liście notebooklm-audio
- Interfejs NotebookLM gotowy do kolejnych operacji
- Raport o statusie generacji i aktualnym stanie systemu
