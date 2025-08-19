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

1. Pobranie następnego zadania z listy TODOIT

// Pobierz następne pending zadanie z listy notebooklm-audio
next_task = mcp__todoit__todo_get_next_pending(list_key: "notebooklm-audio")

if (next_task exists):
  SOURCE_NAME = next_task.item_key
  echo "📋 Pobrano zadanie: " + SOURCE_NAME + " - " + next_task.content
else:
  echo "ℹ️ Brak pending zadań w liście notebooklm-audio"
  return

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

4. Otworzenie opcji dostosowania

// Kliknij przycisk customization dla Podsumowanie audio
mcp__playwright-cdp__browser_click(element: "Podsumowanie audio customization button", ref: "audio_custom_ref")

// Kliknij "Dostosuj" w rozwiniętym menu
mcp__playwright-cdp__browser_click(element: "Dostosuj menu item", ref: "dostosuj_ref")

5. Wpisanie instrukcji i generacja

// Wklej tekst instrukcji TikTok-style
TIKTOK_INSTRUCTIONS = "Omówcie książkę. Zmieśćcie wszystko w maksymalnie 5-7 minutach - to ma być dynamiczne! Omówcie temat jak dwójka przyjaciół odkrywających szokujące fakty podczas nocnej rozmowy. Grupa docelowa: Polacy w wieku 14-25 lat na TikToku. Używajcie prostego języka, memów, odniesień do polskiej popkultury. Co 30 sekund rzućcie faktem, który zmusi do zatrzymania przewijania. Włączcie kontrowersyjne opinie, pytania do widzów typu \"a wy co byście zrobili?\". Mówcie po polsku, ale wplatajcie anglicyzmy jak \"vibe\", \"cringe\", \"slay\". Zacznijcie od haka w stylu \"Tego nie uczą w szkołach, bo...\". Twórzcie napięcie i cliffhangery. Bez długich wstępów - od razu do sedna! WAŻNE: W połowie dyskusji zapytajcie wprost \"A wy co o tym myślicie? Dajcie znać w komentarzach!\" i zakończcie mocnym wezwaniem \"Piszcie w komentarzach czy się zgadzacie czy jesteśmy totalnie w błędzie!\""

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
  echo "✅ Generacja audio dla źródła " + SOURCE_NAME + " rozpoczęta pomyślnie"
  echo "Status: Nowe audio w trakcie generowania..."
  
  // Oznacz zadanie jako completed w liście TODOIT
  mcp__todoit__todo_mark_completed(
    list_key: "notebooklm-audio",
    item_key: SOURCE_NAME
  )
  echo "✅ Zadanie " + SOURCE_NAME + " oznaczone jako completed w liście notebooklm-audio"
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

Stan końcowy:

- Źródło [SOURCE_NAME] zaznaczone w zakładce Źródła
- Nowa generacja audio rozpoczęta z instrukcjami TikTok-style  
- Zadanie [SOURCE_NAME] oznaczone jako completed w liście notebooklm-audio
- Interfejs NotebookLM gotowy do kolejnych operacji
- Raport o statusie generacji i aktualnym stanie systemu