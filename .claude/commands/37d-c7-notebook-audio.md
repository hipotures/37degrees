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

// Wklej tekst instrukcji TikTok-style

TIKTOK_INSTRUCTIONS = """
CEL
Stwórzcie 5–7-minutowy, dynamiczny odcinek audio-wideo na TikToka, w którym dwoje przyjaciół rozbiera na czynniki pierwsze wybraną książkę. Zero długich wstępów. Natychmiastowy hak, napięcie, cliffhangery, fakty „stop-scroll” co ~30 s, proste słowa i odniesienia do polskiej popkultury.

ROLA PROWADZĄCYCH
Dwie osoby: „Prowadzący_A” i „Prowadzący_B”. Brzmią jak dobrzy znajomi przy nocnej rozmowie. Czasem się nie zgadzają. Spierają się rzeczowo, bez obrażania. Używają prostego języka i młodzieżowego slangu 15–25, ale oszczędnie i naturalnie.

TON I STYL
• Mówcie po polsku. Zdania krótkie. Zero akademickiego tonu. 
• Wplatacie memy i referencje do PL popkultury. Unikajcie hermetycznych żartów.
• Co ~30 s dorzucacie „fakt-przerywnik” (zaskakujący, liczbowy, kontrowersyjny albo ciekawostka).
• Tworzycie napięcie i mini-cliffhangery między segmentami.
• Opinie mogą być ostre, ale zawsze oznaczajcie je jako opinie.

STRUKTURA (5–7 min, 12–14 beatów po 20–30 s)
1) HAK 0:00–0:15 — odważne zdanie otwarcia. Przykład formy: 
   „Tego nie uczą w szkołach, bo…”, „Możecie pożałować, jeśli przeczytacie, ale…”, 
   „Nie odzobaczę tego, co znalazłem w…”. Wymyślcie własną wersję.
2) O CO CHODZI 0:15–0:40 — 1-zdaniowe streszczenie książki, dlaczego ma znaczenie dziś.
3) FAKT #1 0:40–1:00 — „stop-scroll” (liczba, cytat tezy, kontekst historyczny bez spojlera).
4) KONFLIKT TEZ 1:00–1:30 — A vs B, krótka różnica zdań.
5) FAKT #2 1:30–2:00 — ciekawostka, porównanie do współczesności.
6) SCENA/OBRAZ 2:00–2:30 — obrazowe porównanie, mem, analogia z życia w PL.
7) FAKT #3 2:30–3:00 — kontrowersyjny wniosek lub liczba.
8) „CO BYŚ ZROBIŁ?” 3:00–3:15 — pytanie do widzów (moralny dylemat, wybór).
9) MID-CTA 3:15–3:25 — dosłownie: „A wy co o tym myślicie? Dajcie znać w komentarzach!”
10) ROZWINIĘCIE SPORU 3:25–4:15 — krótkie argumenty A i B, przykład z życia.
11) FAKT #4 4:15–4:45 — zaskakujący kontrprzykład lub błąd myślenia.
12) PRAKTYCZNY TAKEAWAY 4:45–5:30 — jak wykorzystać myśl książki jutro w Polsce.
13) FAKT #5 5:30–6:00 — najmocniejsza ciekawostka lub odczarowanie mitu.
14) ZAMKNIĘCIE 6:00–6:30 — jedno zdanie „po tym nie spojrzycie tak samo na…”. 
    Finałowe wezwanie: „Piszcie w komentarzach czy się zgadzacie czy jesteśmy totalnie w błędzie!”

"""

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
