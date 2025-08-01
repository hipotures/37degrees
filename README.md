# 37degrees - TikTok Video Generator for Book Reviews

**🎬 Professional TikTok video generator transforming classic literature into engaging short-form content for Polish youth**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Wersja](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/user/37degrees/releases)
[![Licencja](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 Cel Projektu

37degrees (@37stopni - "gorączka czytania") to zaawansowany system generowania pionowych filmów TikTok (1080x1920) promujących klasyczną literaturę wśród polskiej młodzieży w wieku 12-25 lat. System generuje 25 scenicznych ilustracji AI dla każdej książki, które można wykorzystać do tworzenia angażujących materiałów wizualnych przedstawiających klasyczne dzieła dla pokolenia Z.

## ✨ Kluczowe Funkcjonalności

### 🎨 Generowanie Treści
- **Kompleksowy pipeline video**: Od konfiguracji książki → AI scene → AI images → montaż wideo
- **25 scenicznych ilustracji**: Różne struktury w zależności od typu generatora (narrative, flexible, podcast, atmospheric, emotional)
- **Niefotorealistyczny styl**: Dziecięce ilustracje zoptymalizowane pod kąt TikToka

### 🤖 Inteligentny System Agentów (37d)
- **8 wyspecjalizowanych agentów badawczych** działających w skoordynowanej sekwencji
- **Dynamiczne odkrywanie agentów** - rozszerzalna architektura poprzez konfigurację plikową
- **Kontrola liczby zadań** - konfigurowalne min/max zadań na typ agenta
- **System analizy luk** - agent deep-research wypełnia braki informacyjne

### 🎬 Zaawansowana Produkcja Video
- **GPU-accelerated rendering** z NVENC FFmpeg
- **Ken Burns effects** i płynne przejścia
- **Animacje tekstowe** z różnymi metodami nakładania
- **Safe zone compliance** dla elementów UI TikToka

### 🔍 System Badawczy
- **Integracja z Perplexity AI** i Google Search
- **Automatyczne generowanie recenzji** w języku polskim
- **Cache'owanie odpowiedzi** dla minimalizacji kosztów API
- **System walidacji źródeł** i kompilacji bibliografii

## 🚀 Szybki Start

### Wymagania Systemowe
- **Python 3.12+**
- **uv** package manager (zamiast pip)
- **FFmpeg** z obsługą NVENC (opcjonalnie, dla GPU acceleration)
- **InvokeAI** lub **ComfyUI** (do generowania AI)

### Instalacja

```bash
# Sklonuj repozytorium
git clone git@github.com:user/37degrees.git
cd 37degrees

# Skopiuj i skonfiguruj środowisko
cp .env.example .env
# Edytuj .env z właściwymi kluczami API

# Zainstaluj zależności przez uv
uv pip install -r requirements.txt

# Aktywuj wirtualne środowisko (jeśli potrzebne)
source .venv/bin/activate
```

### Pierwsze Uruchomienie

```bash
# Wyświetl wszystkie dostępne kolekcje
python main.py collections

# Wyświetl książki w kolekcji klasyki
python main.py list classics

# Testuj generowanie bez GPU (mock generator)
python main.py ai 17 --generator mock

# Wygeneruj kompletny film dla Małego Księcia
python main.py generate 17
```

## 📚 Główne Polecenia CLI

### Zarządzanie Kolekcjami i Książkami
```bash
python main.py collections              # Lista wszystkich kolekcji
python main.py list classics            # Książki w kolekcji "classics"
python main.py list                     # Wszystkie książki w projekcie
```

### Generowanie Treści
```bash
# Generowanie filmów
python main.py video 17                 # Film dla książki #17
python main.py video little_prince      # Film według nazwy książki
python main.py video classics           # Filmy dla całej kolekcji

# Generowanie obrazów AI
python main.py ai 17                    # Obrazy AI dla książki #17
python main.py ai 17 --generator comfyui # Wybór generatora
python main.py ai classics              # Obrazy dla całej kolekcji

# Kompleksowe generowanie (AI + video)
python main.py generate 17              # Wszystko dla książki #17
python main.py generate classics        # Wszystko dla kolekcji
```

### System Badawczy
```bash
# Generowanie treści badawczych AI
python main.py research 17 --provider perplexity  # Perplexity AI
python main.py research 17 --provider google      # Google Search
python main.py research classics --provider mock  # Testowanie

# Regenerowanie promptów (po edycji book.yaml)
python main.py prompts 17
python main.py prompts little_prince
```

### Generowanie Strony Statycznej
```bash
python main.py site              # Kompletna strona
python main.py site 17           # Strona pojedynczej książki
python main.py site classics     # Strony kolekcji
```

## 🧠 System Inteligentnych Agentów 37d

### Przepływ Badawczy
```bash
# Główny przepływ badawczy używający 8 wyspecjalizowanych agentów
/37d-research "Tytuł Książki"

# Eksport kompletnego systemu agentów
./scripts/export-37d-system.sh
```

### Specjalizacje Agentów
- **37d-facts-hunter**: Fakty historyczne, szczegóły biograficzne (8-14 zadań)
- **37d-culture-impact**: Adaptacje kulturowe, filmy, trendy TikTok (6-10 zadań)
- **37d-symbol-analyst**: Analiza symboliki literackiej (4-8 zadań)
- **37d-polish-specialist**: Polskie tłumaczenia, kontekst edukacyjny (7-12 zadań)
- **37d-youth-connector**: Relevantność dla Gen Z, hacki nauki (4-8 zadań)
- **37d-source-validator**: Weryfikacja integralności badań (0-0 zadań)
- **37d-bibliography-manager**: Kompilacja cytowań (0-0 zadań)
- **37d-deep-research**: Analiza luk, rozwiązywanie sprzeczności (0-5 zadań)

### Konfiguracja Agentów
- **Auto-odkrywanie**: Nowi agenci automatycznie wykrywani z `.claude/agents/37d-*.md`
- **YAML frontmatter**: `todo_list`, `min_tasks`, `max_tasks`, `execution_order`
- **Równoległa egzekucja**: Agenci grupowani wg `execution_order`, grupy wykonywane sekwencyjnie, agenci w grupach równolegle
- **Wyjście badań**: Wszystkie ustalenia zapisywane do `books/NNNN_book/docs/findings/`

## 🔧 Zaawansowane Konfiguracje

### Nadpisywanie Ustawień
```bash
# Nadpisanie pojedynczych parametrów
python main.py --set video.fps=60 video 17
python main.py --set development.debug=true --no-banner ai 17

# Użycie niestandardowego pliku konfiguracji
python main.py --config production.yaml video 17
```

### Generowanie Scen (37degrees Commands)
```bash
# Generowanie nowych opisów scen
/37d-s1-gen-scenes "Mały Książę" "Saint-Exupéry" narrative
/37d-s1-gen-scenes "Wyspa Skarbów" "Stevenson" flexible
/37d-s1-gen-scenes "Wichrowe Wzgórza" "Emily Brontë" emotional

# Aplikowanie stylów wizualnych do scen
/37d-s2-apply-style "Tytuł Książki" "Autor" [nazwa_stylu]

# Wybór konkretnego stylu
/37d-s2-apply-style "Mały Książę" "Saint-Exupéry" watercolor
/37d-s2-apply-style "1984" "Orwell" constructivist-propaganda
```

## 🏗️ Architektura Systemu

### Przepływ Danych
```
book.yaml → Generator Scen → Sceny JSON → Aplikacja Stylu → Prompty AI
                                                                    ↓
Strona HTML ← Plik Video ← Renderowanie Klatek ← Obrazy AI ← Generator AI

# Przepływ Badań Agentów 37d (Opcjonalny):
/37d-research → Odkrywanie Agentów → Generowanie TODO → Sekwencyjna Egzekucja
                                                                    ↓
books/docs/findings/ ← Kontrola Jakości ← Bibliografia ← Wyniki Badań
```

### Kluczowe Komponenty

#### 1. Architektura Plugin-ów (`src/generators/`)
- **BaseImageGenerator** - abstrakcyjna klasa definiująca interfejs
- **Wzorzec Registry** - dynamiczne odkrywanie generatorów
- **Generatory**: InvokeAI (główny), ComfyUI, Mock (testowanie)

#### 2. System Generowania Scen (v2.0+)
- **Proces dwustopniowy**: Opisy scen → Aplikacja stylu  
- **5 typów generatorów** z różnymi strukturami narracyjnymi:
  - `narrative`: 3 akty (ekspozycja 1-8, rozwój 9-18, finał 19-25)
  - `flexible`: 5 sekcji (opening 1-3, wprowadzenie 4-8, rozwój 9-15, kulminacja 16-20, zakończenie 21-25)
  - `podcast`: podział funkcjonalny (20% atmosfera, 32% postacie, 28% fabuła, 20% symbolika)
  - `atmospheric`: fokus na nastroju i klimacie
  - `emotional`: podróż emocjonalna bohaterów
- **Pliki scen**: `books/*/prompts/scenes/[type]/scene_XX.json`
- **Biblioteka stylów**: 34 profesjonalne style graficzne w `config/prompt/graphics-styles/`

#### 3. Bogata Biblioteka Stylów Wizualnych (34 style)
**Style klasyczne:**
- `children-book-illustration` - ciepłe ilustracje książkowe, styl Quentin Blake
- `watercolor` - akwarele z przezroczystymi plamami i miękkie krawędzie
- `oil-painting` - klasyczne malarstwo olejne z bogatymi teksturami
- `pencil-sketch` - szkice ołówkowe z organicznymi liniami

**Style nowoczesne:**
- `flat-design` - minimalistyczny design z geometrycznymi kształtami
- `3d-clay-render` - plastyczne renderowanie z miękkimi formami
- `glitch-art` - cyfrowe zniekształcenia i artefakty
- `isometric-blue-line-urban` - izometryczne miasta w stylu blueprint

**Style artystyczne:**
- `art-nouveau` - secesyjne ozdoby i organiczne formy
- `expressionist` - intensywne kolory i emocjonalne przedstawienia  
- `surrealist-dreamlike` - surrealistyczne kompozycje i oniryczne sceny
- `constructivist-propaganda` - geometryczne plakaty w stylu konstruktywizmu

**Style specjalistyczne:**
- `anime-style` - japońska animacja z charakterystycznymi cechami
- `comic-book` - komiksowy styl z dynamicznymi kadrami
- `noir-pulp-fiction` - czarno-biały klimat noir z kontrastami
- `vintage-travel-poster` - retro plakaty podróżnicze

**Każdy styl zawiera:**
- Szczegółowe prompty AI i słowa kluczowe
- Paletę kolorów z instrukcjami nasycenia
- Specyfikacje oświetlenia i renderowania
- Wzorce artystyczne i referencje

#### 4. System Konfiguracji (`src/config.py`)
- **Scentralizowane ustawienia** z `config/settings.yaml`
- **Nadpisywanie zmiennymi środowiskowymi** via `.env`
- **Nadpisywanie runtime** z flagą `--set`

#### 5. Pipeline Generowania Video
- **OptimizedVideoGenerator** - równoległe renderowanie klatek
- **SlideRenderer** - efekty Ken Burns i przejścia
- **TextAnimator** - animacje wejścia/wyjścia tekstu
- **Akceleracja GPU FFmpeg** z NVENC

#### 6. Integracja Badawcza (`src/research/`)
- **Wzorzec Provider** dla rozszerzalności
- **Implementacje**: Perplexity AI, Google Search
- **Automatyczne generowanie review.md** w języku polskim

#### 7. Generowanie Strony Statycznej (`src/site_generator/`)
- **Interaktywny HTML** dla eksploracji książek
- **Wizualizacje timeline** i organizacja kolekcji
- **Szablony** w `shared_assets/templates/`

## 📁 Struktura Projektu

```
37degrees/
├── books/                      # Katalog książek (NNNN_nazwa/ format)
│   └── 0017_little_prince/
│       ├── book.yaml          # Konfiguracja książki
│       ├── docs/              # Dokumentacja i badania
│       ├── generated/         # Wygenerowane obrazy AI (25 scen)
│       └── prompts/           # Prompty dla scen
├── collections/               # System kolekcji książek
│   └── classics.yaml         # Kolekcja "Klasyka Światowa" (37 książek)
├── config/                    # Główna konfiguracja systemu
│   ├── settings.yaml         # Centralne ustawienia
│   └── prompt/               # Szablony promptów i stylów
├── src/                      # Kod źródłowy
│   ├── cli/                 # Moduły CLI
│   ├── generators/          # Generatory obrazów AI
│   ├── research/            # System badawczy
│   └── site_generator/      # Generator strony statycznej
├── output/                  # Wygenerowane filmy
├── site/                    # Wygenerowana strona HTML
└── main.py                  # Główny punkt wejścia
```

## 📚 System Kolekcji

**Kolekcje** to tematyczne grupowania książek z metadanymi i konfiguracją serii.

### Struktura Kolekcji (`collections/classics.yaml`)

```yaml
books:
- order: 1                                    # Kolejność w serii
  path: books/0017_little_prince/book.yaml   # Ścieżka do konfiguracji książki
  tags:                                      # Tagi tematyczne
  - filozofia
  - baśń 
  - klasyka XX wieku

series:                                      # Metadane serii
  name: "Klasyka Światowa"                   # Nazwa kolekcji
  description: "Najważniejsze dzieła literatury światowej w formie angażujących TikToków"
  target_audience: "10-20 lat"              # Grupa docelowa
  language: "pl"                             # Język
  hashtags:                                  # Hashtagi TikTok
  - '#37stopni'
  - '#klasyka' 
  - '#booktok'
```

### Główna Kolekcja: "Klasyka Światowa"

**37 najważniejszych dzieł literatury światowej** pogrupowanych tematycznie:

**Fantasy i Baśnie:**
- Mały Książę, Władca Pierścieni, Harry Potter, Hobbit, Alicja w Krainie Czarów, Narnia

**Dystopie i Science Fiction:**  
- 1984, Brave New World, Fahrenheit 451, Duna, Solaris

**Klasyka Polska:**
- Lalka, Pan Tadeusz, Quo Vadis, Chłopi, Solaris

**Literatura Młodzieżowa:**
- Harry Potter, Hobbit, Tom Sawyer, Wyspa Skarbów

**Każda książka zawiera:**
- **Tagi tematyczne** - dla łatwego filtrowania i grupowania
- **Kolejność serii** - dla systematycznego publikowania
- **Ścieżka do konfiguracji** - łączenie z systemem książek

### Operacje na Kolekcjach

```bash
# Przeglądanie kolekcji
python main.py collections                  # Lista wszystkich kolekcji
python main.py list classics               # Książki w kolekcji "classics"

# Przetwarzanie całej kolekcji
python main.py ai classics                 # Generuj AI dla wszystkich książek
python main.py video classics              # Twórz filmy dla całej kolekcji
python main.py research classics           # Badania dla całej serii
```

## 🎨 Wzorce Projektowe

- **Registry Pattern**: Dynamiczne odkrywanie generatorów
- **Abstract Factory**: Tworzenie generatorów obrazów
- **Template Method**: Proces generowania scen
- **Strategy Pattern**: Metody nakładania tekstu
- **Provider Pattern**: Abstrakcja API badawczego

## 🎯 Kontekst Projektu

### Główny Kontekst
- **Grupa docelowa**: Polska młodzież na TikToku (12-25 lat)
- **Nazwa konta**: @37stopni (37 stopni - "gorączka czytania")
- **Focus serii**: Klasyka światowa adaptowana dla młodych czytelników
- **Format video**: Format pionowy 1080x1920, 25 scen na książkę
- **Styl artystyczny**: Niefotorealistyczne, dziecięce ilustracje
- **Rozdzielczość finalna**: 1080x1920 przy 30fps

### Kontekst Systemu Agentów 37d
- **Rozszerzalna architektura**: Nowi agenci auto-wykrywani z `.claude/agents/37d-*.md`
- **Konfiguracja YAML frontmatter**: `todo_list`, `min_tasks`, `max_tasks`, `execution_order`
- **Równoległa egzekucja**: Agenci grupowani wg `execution_order`, grupy wykonywane sekwencyjnie, agenci w grupach równolegle
- **Kontrola jakości**: Walidacja źródeł i kompilacja bibliografii wbudowane
- **Integracja hook-ów**: Wyniki wyszukiwań automatycznie zapisywane via Claude Code hooks

## 🔨 Development Guidelines

### Zasady Tworzenia Kodu
- **Minimalizm**: Rób tylko to, o co proszono; nic więcej, nic mniej
- **Edycja przed tworzeniem**: ZAWSZE preferuj edycję istniejących plików nad tworzeniem nowych
- **Brak proaktywnej dokumentacji**: NIGDY nie twórz plików dokumentacji (*.md) lub README chyba, że wyraźnie o to poproszono

### Specyfika Polskiego Projektu
- **Język polski**: Zawsze używaj polskiego dla treści specyficznych dla Polski
- **Format 24-godzinny**: Dla wszystkich timestamp-ów
- **Bezpieczeństwo danych**: Nigdy nie commituj prawdziwych loginów, URL-i, danych osobowych
- **Zarządzanie czasem**: Przy pracy z datami/SQL zawsze uwzględniaj UTC vs. czas lokalny
- **GitHub SSH**: Przy dodawaniu integracji z GitHub używaj SSH zamiast HTTPS

## 📊 Testowanie i Development

### Testowanie bez GPU
```bash
# Testuj z mock generatorem (bez AI)
python main.py ai 17 --generator mock

# Testuj generowanie video bez AI (wymaga istniejących obrazów)
python main.py video 17

# Debug mode
python main.py --set development.debug=true ai 17
```

### Batch Operations
```bash
# Skrypt batch dla badań
./scripts/export-37d-system.sh

# Utilities
python src/prompt_builder.py books/0017_little_prince/book.yaml
```

## 🤝 Rozszerzanie Systemu

### Dodawanie Nowego Generatora AI
1. Stwórz klasę dziedziczącą z `BaseImageGenerator`
2. Zaimplementuj wymagane metody
3. Generator zostanie automatycznie wykryty przez Registry

### Dodawanie Nowego Agenta 37d
1. Stwórz plik `.claude/agents/37d-nazwa-agenta.md`
2. Dodaj YAML frontmatter z konfiguracją
3. Agent zostanie automatycznie odkryty i włączony

### Dodawanie Nowego Providera Badań
1. Dziedzicz z `BaseResearchProvider`
2. Zaimplementuj wymagane metody API
3. Dodaj konfigurację do `settings.yaml`

## 📄 Licencja

Ten projekt jest licencjonowany na warunkach licencji MIT - szczegóły w pliku [LICENSE](LICENSE).

## 🆘 Wsparcie

- **Dokumentacja**: Pełna dokumentacja w katalogu `/docs`
- **Issues**: Zgłoś problemy przez GitHub Issues
- **Development**: Sprawdź `/docs/STRUCTURE.md` dla szczegółów architektury

---

**🎬 Stwórz angażujące TikToki z klasycznej literatury i zaraź młodzież gorączką czytania! 📚**