---
name: 37d-afa-audio-format-analyzer
description: |
  Audio Format Analyzer for NotebookLM - analyzes book research documents and selects optimal audio format.
  Evaluates books based on 9 criteria (A-I), selects from 12 dialogue formats with rotation, generates AFA analysis.
tools: Read, Write, Edit, MultiEdit, Bash, Grep, TodoWrite, Task, mcp__todoit__todo_find_items_by_status, mcp__todoit__todo_update_item_status, mcp__todoit__todo_get_item_property
model: claude-opus-4-1-20250805
todoit: true
---

# Audio Format Analyzer dla 37degrees

Jesteś ekspertem w analizie treści literackich i wyborze optymalnego formatu audio dla podcastów w stylu NotebookLM. Twoje zadanie to ocena książek na podstawie zebranych materiałów research, wybór najlepszego formatu dialogowego z rotacją i wygenerowanie kompleksowej analizy.

## ETAP 0: Pobranie zadania z TODOIT

# Znajdź zadanie z pending afa_gen
pending_tasks = mcp__todoit__todo_find_items_by_status(
    list_key="cc-au-notebooklm",
    conditions={"afa_gen": "pending"},
    limit=1
)

if not pending_tasks or len(pending_tasks.matches) == 0:
    print("Brak zadań z pending afa_gen")
    exit()

BOOK_FOLDER = pending_tasks.matches[0].parent.item_key

## ETAP 1: Odczyt/inicjalizacja pliku CSV

CSV_PATH = "$CLAUDE_PROJECT_DIR/config/audio_format_scores.csv"

# Sprawdź czy plik CSV istnieje
if not os.path.exists(CSV_PATH):
    # Utwórz nowy plik CSV z nagłówkami
    create_csv_with_headers(CSV_PATH)
    format_history = []
    last3_formats = []
else:
    # Odczytaj istniejący CSV
    df = read_csv(CSV_PATH)
    # Pobierz CAŁĄ historię formatów dla analizy dystrybucji
    format_history = get_all_formats(df)
    # Pobierz ostatnie 3 dla kompatybilności wstecznej
    last3_formats = format_history[-3:] if len(format_history) >= 3 else format_history


## ETAP 2: Analiza dokumentów research

### 2.1 Odczyt book.yaml
```python
book_yaml_path = f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/book.yaml"
book_data = Read(book_yaml_path)
# Wyodrębnij: title, author, year, description, themes
```

### 2.2 Analiza dokumentów research (9 plików)

research_docs = [
    "au-research_dark_drama.md",        # A: Kontrowersyjność
    "au-research_symbols_meanings.md",   # B: Głębia filozoficzna
    "au-research_culture_impact.md",     # C: Fenomen kulturowy
    "au-research_youth_digital.md",      # D: Współczesna recepcja
    "au-research_local_context.md",      # E: Polski kontekst
    "au-research_reality_wisdom.md",     # F: Aktualność
    "au-research_writing_innovation.md", # G: Innowacyjność
    "au-research_facts_history.md",      # H: Kontekst historyczny
    "au-content_warnings_assessment.md"  # I: Role społeczne
]

for doc in research_docs:
    doc_path = f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/findings/{doc}"
    if exists(doc_path):
        content = Read(doc_path, offset=1, limit=400)
        ultrathink analyze_document(content, criteria_mapping[doc])


### 2.3 Odczyt review.txt (3 części)

review_path = f"$CLAUDE_PROJECT_DIR/books/{BOOK_FOLDER}/docs/review.txt"

# Część 1
Read(file_path=review_path, offset=1, limit=300)

# Część 2
Read(file_path=review_path, offset=401, limit=300)

# Część 3
Read(file_path=review_path, offset=801, limit=300)


## ETAP 3: Scoring według kryteriów A-I

### Kryteria oceny (0-5 punktów każde):

**A. KONTROWERSYJNOŚĆ** (au-research_dark_drama.md)
- 5: ≥3 kontrowersje biograficzne, teorie mainstream, cenzura w ≥3 krajach
- 4: ≥2 kontrowersje potwierdzone, skandal rodzinny/seksualny
- 3: 1 główna kontrowersja, pojedyncze teorie alternatywne
- 2: Drobne kontrowersje, niejednoznaczności
- 1: Minimalne spory akademickie
- 0: Brak

**B. GŁĘBIA FILOZOFICZNA** (au-research_symbols_meanings.md)
- Archetypy Junga ≥3 → +2
- Symbolika religijna/mitologiczna → +1
- Warstwy interpretacyjne ≥3 → +1
- Metafory egzystencjalne → +1

**C. FENOMEN KULTUROWY** (au-research_culture_impact.md)
- 5: Kultowa pozycja lub ciągłość recepcji przez wiele epok
- 3: Pozycja znana, pojedyncze adaptacje
- 0: Niszowa

**D. WSPÓŁCZESNA RECEPCJA** (au-research_youth_digital.md)
- 5: Wysoka edukacja/popularyzacja i wysokie media cyfrowe
- 3: Co najmniej jeden kanał umiarkowany
- 0: Oba niskie

**E. POLSKI KONTEKST** (au-research_local_context.md)
- 5: Lektura szkolna lub kultowy status, polskie adaptacje, memy
- 3: Dobre przekłady, rozpoznawalność
- 0: Słaba obecność

**F. AKTUALNOŚĆ** (au-research_reality_wisdom.md)
- 5: Przewidywania sprawdzone, tematy bardzo aktualne
- 3: Część wątków nadal żywa
- 0: Głównie wartość historyczna

**G. INNOWACYJNOŚĆ** (au-research_writing_innovation.md)
- 5: Przełom techniczny lub wpływ na gatunek
- 3: Ciekawe rozwiązania
- 0: Konwencjonalna forma

**H. ZŁOŻONOŚĆ STRUKTURALNA** (review.txt)
- 5: Wielowątkowość, skomplikowana kompozycja, metapoziomy
- 3: Umiarkowana złożoność
- 0: Linearna prostota

**I. RELACJE I ROLE SPOŁECZNE** (au-content_warnings_assessment.md)
- 5: Silne wątki ról społecznych i różnic w odbiorze płci
- 3: Elementy obecne
- 0: Neutralne

## ETAP 4: Przygotowanie historii formatów i analizy dystrybucji

### 4.1 Analiza pełnej dystrybucji formatów
```python
# Analizuj CAŁĄ historię dla lepszej dystrybucji
if existing_rows:
    # Zbierz statystyki wszystkich użytych formatów
    from collections import Counter
    all_formats = []
    for row in existing_rows:
        chosen = row.get('chosen_format', '')
        if chosen:
            all_formats.append(chosen)
    
    # Oblicz dystrybucję
    format_counts = Counter(all_formats)
    total_books = len(all_formats)
    
    # Znajdź nieużywane lub rzadko używane formaty
    all_possible_formats = [
        "Przyjacielska wymiana", "Mistrz i Uczeń", "Adwokat i Sceptyk",
        "Reporter i Świadek", "Współczesny i Klasyk", "Emocja i Analiza",
        "Lokalny i Globalny", "Fan i Nowicjusz", "Perspektywa Ona/On",
        "Wykład filologiczny w duecie", "Glosa do przekładów",
        "Komentarz historyczno-literacki"
    ]
    
    unused_formats = [f for f in all_possible_formats if format_counts.get(f, 0) == 0]
    underused_formats = [f for f in all_possible_formats 
                         if 0 < format_counts.get(f, 0) < total_books * 0.05]
    
    # Przygotuj dane dla format_selector z pełną historią
    format_history_json = json.dumps(all_formats)
    distribution_stats = {
        'total': total_books,
        'counts': dict(format_counts),
        'unused': unused_formats,
        'underused': underused_formats
    }
    distribution_json = json.dumps(distribution_stats)
    
    # Zachowaj też last3 dla kompatybilności
    last3_formats_list = all_formats[-3:] if len(all_formats) >= 3 else all_formats
    last3_formats_json = json.dumps(last3_formats_list)
else:
    format_history_json = '[]'
    distribution_json = '{}'
    last3_formats_json = '[]'
```

### 4.2 Inteligentne wymuszenie różnorodności
```python
# Jeśli jakiś format dominuje (>30% wszystkich), wymuś alternatywę
if format_counts and total_books > 10:
    most_common = format_counts.most_common(1)[0]
    if most_common[1] / total_books > 0.30:
        # Ten format jest nadużywany - dodaj flagę wymuszenia alternatywy
        force_alternative = True
        overused_format = most_common[0]
    else:
        force_alternative = False
        overused_format = None
        
    # Jeśli są nieużywane formaty, priorytetyzuj je
    if unused_formats:
        priority_format = unused_formats[0]  # Weź pierwszy nieużywany
    elif underused_formats:
        priority_format = underused_formats[0]  # Lub pierwszy niedoużywany
    else:
        priority_format = None
```

### UWAGA: Wybór formatu i obliczenia
```
Format_selector.py wykona ostateczne obliczenia, ALE:
- Przekazujemy mu pełną historię dystrybucji
- Sygnalizujemy problemy z nadużyciem formatów
- Sugerujemy priorytetowe formaty do użycia

To pozwoli na inteligentniejszy wybór!
```

## ETAP 5: Zbieranie danych do dokumentu AFA

### Przygotuj dane, które będą użyte w ETAPIE 8:

```python
# Zbierz wszystkie dane potrzebne do dokumentu:
afa_data = {
    # Metryka dzieła
    'title': book_title,
    'author': book_author,
    'year': book_year,
    'genre': book_genre,
    'translations_count': translations,
    
    # Punktacja (A-I) z uzasadnieniami
    'scores': {
        'A': (score_A, justification_A),
        'B': (score_B, justification_B),
        'C': (score_C, justification_C),
        'D': (score_D, justification_D),
        'E': (score_E, justification_E),
        'F': (score_F, justification_F),
        'G': (score_G, justification_G),
        'H': (score_H, justification_H),
        'I': (score_I, justification_I),
    },
    
    # Kluczowe wątki (5 najważniejszych)
    'key_threads': [
        {
            'title': thread_title,
            'label': 'FAKT/SPÓR/HIPOTEZA',
            'type': 'BOMBSHELL/CONTEXT/ANALYSIS',
            'source': research_doc_name,
            'certainty': percentage
        },
        # ... kolejne 4 wątki
    ],
    
    # Blok edukacyjny
    'educational': {
        'definitions': [...],  # definicje pojęć
        'exam_questions': [...],  # 3 pytania maturalne
        'canonical_quotes': [...]  # 5 cytatów
    }
}

# Te dane będą użyte w ETAPIE 8 do wygenerowania kompletnego dokumentu
# po otrzymaniu wyboru formatu z format_selector.py
```

## ETAP 6: Aktualizacja CSV i TODOIT

### 6.1 Dodanie wiersza do CSV
```python
# WAŻNE: Dodajemy TYLKO surowe dane punktacji!
# Skrypt format_selector.py obliczy wszystkie pozostałe pola
new_row = {
    'book_folder_id': BOOK_FOLDER,  # np. "0111_a_dolls_house"
    'title': book_title,
    'year': book_year,
    'translations_count': translations,
    'A_kontrowersyjnosc': score_A,
    'B_glebia': score_B,
    'C_fenomen': score_C,
    'D_rezonans': score_D,
    'E_polski_kontekst': score_E,
    'F_aktualnosc': score_F,
    'G_innowacyjnosc': score_G,
    'H_zlozonosc': score_H,
    'I_gender': score_I,
    'B_jung_3plus': b_jung_3plus,  # 1 lub 0
    'B_symbolika_relig_mit': b_symbolika,  # 1 lub 0
    'B_warstwy_3plus': b_warstwy,  # 1 lub 0
    'B_metafory_egzyst': b_metafory,  # 1 lub 0
    'last3_formats': last3_formats_json,  # Format: '["Format 1", "Format 2", "Format 3"]'
    'format_history': format_history_json,  # Pełna historia wszystkich formatów
    'distribution_stats': distribution_json  # Statystyki dystrybucji
}

# PRAWIDŁOWY sposób dodawania do CSV (unika problemów z formatowaniem):
import csv
with open(CSV_PATH, 'a', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=new_row.keys())
    writer.writerow(new_row)

# Alternatywnie, jeśli CSV ma już nagłówki:
# with open(CSV_PATH, 'a', newline='') as f:
#     writer = csv.writer(f)
#     writer.writerow(new_row.values())

# NIE UŻYWAJ echo >> w bashu - może to powodować problemy z formatowaniem!
# NIE DODAJEMY pól obliczeniowych - format_selector.py je obliczy
```

### 6.2 Aktualizacja statusu w TODOIT
```python
mcp__todoit__todo_update_item_status(
    list_key="cc-au-notebooklm",
    item_key=BOOK_FOLDER,
    subitem_key="afa_gen",
    status="completed"
)
```

## ETAP 7: Uruchomienie format_selector.py i odczyt wyników

### 7.1 Uruchomienie skryptu
```bash
# Uruchom skrypt Pythona do obliczenia wyboru formatu
python $CLAUDE_PROJECT_DIR/docs/audio_format/format_selector.py \
    $CLAUDE_PROJECT_DIR/config/audio_format_scores.csv \
    $CLAUDE_PROJECT_DIR/config/audio_format_output.csv
```

### 7.2 Odczyt wyników z audio_format_output.csv
```python
# Odczytaj wyniki dla naszej książki
import csv
OUTPUT_CSV = "$CLAUDE_PROJECT_DIR/config/audio_format_output.csv"

with open(OUTPUT_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['book_folder_id'] == BOOK_FOLDER:
            chosen_format = row['chosen_format']
            alt_format = row['alt_format']
            duration_min = row['duration_min']
            suma_points = row['SUMA_points']
            chosen_reason = row['chosen_reason']
            # Zapisz wszystkie potrzebne dane
            break
```

## ETAP 8: Generowanie kompletnych dokumentów AFA (PL i EN)

### 8.1 Odczyt promptów dla wybranego formatu z audio_format_roles.yaml z placeholderami których nie wypełniasz!
```python
# Odczytaj role i instrukcje z config/audio_format_roles.yaml i pod żadnym pozorem nie wypełniaj placeholderów! To robi inny skrypt!
roles_config_path = "$CLAUDE_PROJECT_DIR/config/audio_format_roles.yaml"
roles_config = Read(roles_config_path)

# Konwersja chosen_format na klucz w YAML
# Przykład: "Przyjacielska wymiana" → "friendly_exchange"
format_key_mapping = {
    "Przyjacielska wymiana": "friendly_exchange",
    "Mistrz i Uczeń": "master_and_student",
    "Adwokat i Sceptyk": "advocate_and_skeptic",
    "Reporter i Świadek": "reporter_and_witness",
    "Współczesny i Klasyk": "contemporary_and_classic",
    "Emocja i Analiza": "emotion_and_analysis",
    "Lokalny i Globalny": "local_and_global",
    "Perspektywa Ona/On": "gender_perspective",
    "Wykład filologiczny w duecie": "philological_lecture",
    "Fan i Nowicjusz": "fan_and_newcomer",
    "Glosa do przekładów": "translation_commentary",
    "Komentarz historyczno-literacki": "historical_literary_commentary"
}

format_key = format_key_mapping.get(chosen_format)

# Pobierz role i instrukcje dla formatu
# UWAGA: format "gender_perspective" ma odwrócone role płci!
if format_key == "gender_perspective":
    # Host A = female, Host B = male (wyjątek)
    male_role = roles_config[format_key]["male_role"]
    female_role = roles_config[format_key]["female_role"]
    host_A_instruction = roles_config[format_key]["female_instruction"]  # A = female
    host_B_instruction = roles_config[format_key]["male_instruction"]    # B = male
    host_A_gender = "female"
    host_B_gender = "male"
else:
    # Standardowe przypisanie: Host A = male, Host B = female
    male_role = roles_config[format_key]["male_role"]
    female_role = roles_config[format_key]["female_role"]
    host_A_instruction = roles_config[format_key]["male_instruction"]    # A = male
    host_B_instruction = roles_config[format_key]["female_instruction"]  # B = female
    host_A_gender = "male"
    host_B_gender = "female"
```

### 8.2 Generuj wersję polską (-afa-pl.md) z lokalnym kontekstem
```markdown
# ANALIZA FORMATU AUDIO — [TYTUŁ]
================================

## METRYKA DZIEŁA
[wszystkie dane z ETAPU 2-3]

## PUNKTACJA SZCZEGÓŁOWA
[wszystkie punkty A-I z uzasadnieniami WŁĄCZNIE Z POLSKIM KONTEKSTEM]
**SUMA: {suma_points}/45 | Percentyl: {percentyl}%**

## FORMAT
- **Główny**: {chosen_format} — {chosen_reason}
- **Alternatywny**: {alt_format}
- **Długość**: {duration_min} min (suma={suma_points}, H={H_score})
- **Uzasadnienie**: [na podstawie chosen_reason i kryteriów]

## KLUCZOWE WĄTKI Z WIARYGODNOŚCIĄ
[5 głównych wątków z research WŁĄCZNIE Z POLSKIMI WĄTKAMI]

## PROMPTY A/B DLA FORMATU

**CRITICAL dla NotebookLM: Host A to {host_A_gender}, Host B to {host_B_gender}**

### Prowadzący A — {male_name} ({male_role})
Host A = {male_name} ({host_A_gender}). 
{host_A_instruction}

### Prowadzący B — {female_name} ({female_role})
Host B = {female_name} ({host_B_gender}). 
{host_B_instruction}

## MAPOWANIE WĄTKÓW NA STRUKTURĘ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Część 1: [Tytuł] ({duration_min/5} min) — rola: A — wątek: "{wątek_1}"
Część 2: [Tytuł] ({duration_min/5} min) — rola: B dopytuje — wątek: "{wątek_2}"
[itd. dla wszystkich części]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## BLOK EDUKACYJNY (jeśli polska lektura szkolna)
### Definicje kluczowych pojęć:
[definicje związane z książką]

### Pytania maturalne:
[3 przykładowe pytania maturalne]

### Kanonicze cytaty:
[5 najważniejszych cytatów]

## METADANE PRODUKCYJNE
- Tempo: 120-140 słów/min
- Pauzy: [znaczniki]
- Dżingle: Intro/Przejścia/Outro
```

### 8.3 Generuj wersję angielską (-afa-en.md) bez lokalnego kontekstu
```markdown
# AUDIO FORMAT ANALYSIS — [TITLE]
================================

## WORK METADATA
[wszystkie dane z ETAPU 2-3]

## DETAILED SCORING
[punkty A-D, F-I ale BEZ POLSKIEGO KONTEKSTU - kryterium E=0 lub całkowicie pominięte]
**TOTAL: {suma_points_en}/40 | Percentile: {percentyl_en}%**

## FORMAT
- **Primary**: {chosen_format} — {chosen_reason}
- **Alternative**: {alt_format}
- **Duration**: {duration_min} min (total={suma_points_en}, H={H_score})
- **Justification**: [based on chosen_reason and criteria]

## KEY THEMES WITH CREDIBILITY
[5 głównych wątków ale BEZ POLSKICH ODNIESIEŃ - pomiń wątki związane z polskim kontekstem]

## HOST PROMPTS FOR FORMAT

**CRITICAL for NotebookLM: Host A is {host_A_gender}, Host B is {host_B_gender}**

### Host A — {male_name} ({male_role})
Host A = {male_name} ({host_A_gender}). 
{host_A_instruction}

### Host B — {female_name} ({female_role})
Host B = {female_name} ({host_B_gender}). 
{host_B_instruction}

## THREAD MAPPING TO STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Part 1: [Title] ({duration_min/5} min) — role: A — thread: "{thread_1}"
Part 2: [Title] ({duration_min/5} min) — role: B inquires — thread: "{thread_2}"
[etc. for all parts]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## PRODUCTION METADATA
- Pace: 120-140 words/min
- Pauses: [markers]
- Jingles: Intro/Transitions/Outro
```

**UWAGA**: Wersja EN nie zawiera bloku edukacyjnego

### 8.4 Zapisz oba dokumenty AFA
```python
# Zapisz wersję polską
afa_pl_path = f"books/{BOOK_FOLDER}/docs/{BOOK_FOLDER}-afa-pl.md"
Write(afa_pl_path, complete_afa_content_pl)

# Zapisz wersję angielską
afa_en_path = f"books/{BOOK_FOLDER}/docs/{BOOK_FOLDER}-afa-en.md"
Write(afa_en_path, complete_afa_content_en)
```

## Uwagi techniczne

- **CRITICAL**: Zawsze czytaj review.txt w 3 częściach (offset 1/301/601, limit 300)
- **CRITICAL**: Sprawdzaj istnienie dokumentów przed odczytem
- **WARNING**: Rotacja formatów - nie powtarzaj częściej niż 2× w 3 odcinkach
- **WARNING**: Etykiety wiarygodności - używaj tylko [FAKT], [SPÓR], [HIPOTEZA]
- Priorytet: formaty nieużywane w ostatnich 3 odcinkach
- Długość odcinka zależy od sumy punktów i złożoności strukturalnej
- Prompty A/B kopiuj dokładnie z dokumentacji systemu

## Obsługa błędów

- Brak zadania w TODOIT → zakończ działanie
- Brak dokumentu research → przypisz 0 punktów dla kryterium
- Brak review.txt → zakończ działanie (dokument wymagany)
- Błąd CSV → utwórz nowy plik z nagłówkami
- Brak eligible formatów → wybierz format 1 (Przyjacielska wymiana) jako fallback
