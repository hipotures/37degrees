---
name: 37d-a7-notebook-audio
description: |
  NotebookLM Audio Generation Orchestrator - automated audio generation using MCP playwright-cdp.
  Orchestrates complete audio generation workflow from TODOIT task retrieval to generation completion.
execution_order: 7
min_tasks: 1
max_tasks: 3
todo_list: false
---

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

5. Wybór formatu i wpisanie instrukcji

// Analiza źródła i wybór odpowiedniego formatu audio
// SOURCE_NAME zawiera nazwę książki (np. "0055_of_mice_and_men")

// Sprawdź czy istnieją findings dla tej książki
book_findings_path = SOURCE_NAME + "/docs/findings/"
has_controversy = check_file_exists(book_findings_path + "au-research_dark_drama.md")
has_philosophy = check_file_exists(book_findings_path + "au-research_symbols_meanings.md") 
has_youth_content = check_file_exists(book_findings_path + "au-research_youth_digital.md")

// FORMAT 1: DYNAMICZNA ROZMOWA (domyślny dla książek przygodowych/młodzieżowych)
TIKTOK_FORMAT_CONVERSATION = """
CEL: 5-7 min dynamicznej rozmowy dwójki przyjaciół o książce. Naturalny flow, organiczne przejścia, energia typowa dla TikToka.

PROWADZĄCY: Dwoje przyjaciół - naturalna chemii, czasem się nie zgadzają, używają prostego języka młodzieżowego (ale nie przesadzają).

STRUKTURA ELASTYCZNA:
• HAK (0:00-0:15): Mocne otwarcie - kontrowersyjne stwierdzenie lub zaskakujące pytanie
• ESENCJA (0:15-1:00): O czym książka + dlaczego wciąż aktualna w 2025
• PING-PONG (1:00-4:30): Naturalna wymiana zdań, anegdoty, spory, przykłady z życia
• FAKTY: Wplatane ORGANICZNIE co 60-90s (nie co 30s!) - tylko gdy pasują do rozmowy
• POLSKI KONTEKST: Odniesienia do polskiej popkultury, memy, sytuacje z polskiego życia
• ZAMKNIĘCIE (4:30-5:00): Mocny punchline + pytanie do widzów

TON: Lekki, energiczny, autentyczny. Jak rozmowa na korytarzu w szkole.
"""

// FORMAT 2: KRYTYCZNA ANALIZA (dla klasyków i książek kontrowersyjnych)
TIKTOK_FORMAT_CRITICAL = """
CEL: 6-8 min pogłębionej analizy z konstruktywną krytyką. Balans między dostępnością a głębią, bez akademickiego tonu.

PROWADZĄCY: Jeden analityk (rzeczowy, konkretny) + jeden sceptyk (zadaje trudne pytania, kwestionuje).

STRUKTURA:
• TEZA (0:00-0:30): Główna kontrowersja lub problem książki - od razu do rzeczy
• KONTEKST (0:30-1:30): Historyczny/społeczny background - dlaczego to było ważne wtedy
• ARGUMENTY ZA (1:30-3:00): Co działa, uniwersalne wartości, ponadczasowe tematy
• ARGUMENTY PRZECIW (3:00-4:30): Problematyczne aspekty, co się zestarzało, krytyka
• WSPÓŁCZESNOŚĆ (4:30-6:00): Jak to się ma do Polski 2025, paralele z Gen Z
• WERDYKT (6:00-6:30): Zbalansowana ocena - czy warto czytać + pytanie do widzów

TON: Rzeczowy ale przystępny. Jak dobry podcast ale skondensowany.
FAKTY: Konkretne dane, cytaty, liczby wspierające argumenty.
"""

// FORMAT 3: DEBATA PERSPEKTYW (dla książek z dylematami moralnymi)
TIKTOK_FORMAT_DEBATE = """
CEL: 5-6 min ostrej debaty z przeciwnych perspektyw. Edgy ale merytoryczne, emocjonujące starcie opinii.

PROWADZĄCY: "Adwokat" (broni książki/bohatera) vs "Prokurator" (atakuje/krytykuje). Ostre ale fair play.

STRUKTURA:
• STARCIE (0:00-0:20): Dwa przeciwne stanowiska wypowiedziane jednocześnie/na przemian
• RUNDA 1 (0:20-1:30): Pierwszy mocny argument każdej strony + przykład
• RUNDA 2 (1:30-3:00): Kontrargumenty - "ale przecież..." + nowe dowody
• TWIST (3:00-3:30): Nieoczekiwany fakt lub perspektywa zmieniająca wszystko
• RUNDA 3 (3:30-4:30): Ostatnie, najmocniejsze argumenty obu stron
• ROZSTRZYGNIĘCIE (4:30-5:00): "Sędzią jesteście wy" - oddanie głosu widzom + CTA

TON: Intensywny, pasjonujący. Jak prawdziwa kłótnia ale z szacunkiem.
DYNAMIKA: Szybkie przejścia, przerywanie sobie (ale nie chaotycznie), emocje.
"""

// Logika wyboru formatu na podstawie analizy źródła
selected_format = ""

if (has_controversy && has_philosophy):
  // Książki z kontrowersyjnymi tematami i głębią filozoficzną
  selected_format = TIKTOK_FORMAT_CRITICAL
  echo "📚 Wybrano format: KRYTYCZNA ANALIZA (kontrowersje + filozofia)"
  
elif (SOURCE_NAME contains ["crime", "murder", "death"] || has_controversy):
  // Książki z dylematami moralnymi, przemocą, trudnymi wyborami
  selected_format = TIKTOK_FORMAT_DEBATE
  echo "⚔️ Wybrano format: DEBATA PERSPEKTYW (dylematy moralne)"
  
elif (has_youth_content || SOURCE_NAME contains ["adventure", "fantasy", "young"]):
  // Książki młodzieżowe, przygodowe, fantasy
  selected_format = TIKTOK_FORMAT_CONVERSATION
  echo "💬 Wybrano format: DYNAMICZNA ROZMOWA (młodzieżowa/przygodowa)"
  
else:
  // Domyślny wybór dla pozostałych książek
  selected_format = TIKTOK_FORMAT_CONVERSATION
  echo "💬 Wybrano format domyślny: DYNAMICZNA ROZMOWA"

// Dodaj uniwersalną stopkę do wybranego formatu
UNIVERSAL_FOOTER = """

UNIWERSALNE ZASADY (dla wszystkich formatów):
• Mówcie po polsku, naturalnie, bez tłumaczenia angielskich zwrotów na siłę
• Odniesienia do polskiej rzeczywistości 2025 - TikTok, szkoła, popkultura PL
• Fakty i liczby tylko gdy naprawdę coś wnoszą, nie na siłę
• Jeden CTA na końcu wystarczy - nie męczcie widzów ciągłym "dajcie znać"
• Humor mile widziany ale nie wymuszony - naturalne żarty gdy pasują
"""

TIKTOK_INSTRUCTIONS = selected_format + UNIVERSAL_FOOTER

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
