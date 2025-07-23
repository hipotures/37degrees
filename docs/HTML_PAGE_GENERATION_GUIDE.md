# Przewodnik tworzenia interaktywnych stron HTML dla książek

## Przegląd

Ten dokument opisuje proces tworzenia profesjonalnych, interaktywnych stron HTML prezentujących klasyczne książki, wzorowanych na stronie "Małego Księcia". Każda strona powinna być samowystarczalna, responsywna i angażująca wizualnie.

## Struktura projektu

```
books/NNNN_book_name/
├── docs/
│   ├── book_page.html      # Główna strona HTML
│   ├── review.md           # Ciekawostki i fakty o książce
│   └── assets/             # Obrazy, ikony (opcjonalnie)
```

## Wymagane elementy strony

### 1. Nagłówek z nawigacją
- Sticky navigation bar z nazwą książki i emoji
- Menu z linkami do sekcji (5-6 głównych sekcji)
- Responsywne menu mobilne (hamburger)

### 2. Sekcja Hero
- Tytuł: "Odkrywcza Podróż po Świecie [Tytuł Książki]"
- Krótki, angażujący opis zachęcający do eksploracji

### 3. Sekcja Autor
- Biografia autora z kluczowymi faktami
- **Interaktywna oś czasu** z najważniejszymi datami
- Fokus na wydarzeniach związanych z książką

### 4. Sekcja Geneza
- Okoliczności powstania dzieła
- Ciekawostki o procesie twórczym
- Format: 2x2 grid z kartami informacyjnymi

### 5. Sekcja Ciekawostki (opcjonalna)
- 4 fascynujące fakty z review.md
- Format: 2x2 grid
- Krótkie, zaskakujące informacje

### 6. Sekcja Symbole/Bohaterowie
- **Interaktywne karty postaci** z emoji
- Modal z opisem po kliknięciu
- 8-12 głównych elementów/postaci

### 7. Sekcja Wpływ
- **Wykresy Chart.js** pokazujące:
  - Porównanie z innymi książkami (tłumaczenia, sprzedaż)
  - Dane w kontekście (nie pojedyncze liczby)
- Wizualizacje muszą być informatywne

### 8. Sekcja Adaptacje
- **Karuzela** z filmami, teatrem, operą
- Przyciski nawigacji < >
- Placeholder images z opisami

## Technologie

```html
<!-- W <head> -->
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Lora:wght@400;600&display=swap" rel="stylesheet">
```

### Paleta kolorów (Cosmic Dream)
```css
--bg-primary: #FDF6E3;     /* Tło strony */
--text-primary: #073642;   /* Tekst główny */
--accent-primary: #268BD2; /* Niebieski akcent */
--accent-secondary: #B58900; /* Złoty akcent */
```

## Komponenty JavaScript

### 1. Timeline (Oś czasu)
```javascript
const timelineData = [
    { year: 'RRRR', event: 'Opis wydarzenia' },
    // ...
];
// Generowanie HTML z naprzemiennym układem
```

### 2. Character Grid (Siatka postaci)
```javascript
const characterData = [
    { 
        id: 'unique_id',
        name: 'Nazwa',
        emoji: '🎭',
        color: 'bg-color-200',
        description: 'Opis symboliki'
    },
    // ...
];
```

### 3. Wykresy Chart.js
- **Wykres słupkowy**: Porównania między książkami/krajami
- **Unikaj wykresów kołowych** dla pojedynczych wartości
- Dane muszą pokazywać kontekst i relacje

### 4. Karuzela
```javascript
const adaptationsData = [
    {
        type: 'Typ adaptacji',
        title: 'Tytuł/Reżyser',
        description: 'Krótki opis',
        image: 'https://placehold.co/600x400/COLOR/FFFFFF?text=Nazwa'
    },
    // ...
];
```

## Dane wymagane do zebrania

1. **O autorze**:
   - 5-7 kluczowych dat z życia
   - Związek z książką
   - Ciekawostki biograficzne

2. **Geneza dzieła**:
   - Okoliczności powstania
   - Proces twórczy
   - Pierwsze wydania

3. **Symbole/Bohaterowie**:
   - 8-12 głównych postaci/elementów
   - Krótkie opisy symboliki
   - Odpowiednie emoji

4. **Dane statystyczne**:
   - Liczba tłumaczeń
   - Sprzedaż (najlepiej w podziale na kraje)
   - Porównanie z innymi dziełami

5. **Adaptacje**:
   - Filmy, teatr, opera, gry
   - Daty i twórcy
   - Krótkie opisy

## Responsywność

- Mobile-first approach
- Breakpoints: md (768px), lg (1024px)
- Sticky navigation na wszystkich urządzeniach
- Dostosowanie wykresów do małych ekranów

## Generowanie grafik

Obecnie używane są placeholder images z placehold.co. Dla prawdziwych grafik:

1. **Sceny z książki**: Generowane przez AI (ComfyUI/InvokeAI)
2. **Ikony postaci**: Emoji lub proste ilustracje
3. **Tła sekcji**: Subtelne gradienty lub wzory

## Szablon startowy

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Tytuł Książki] - Interaktywna Odkrywcza Podróż</title>
    <!-- CDN imports -->
</head>
<body class="antialiased">
    <header><!-- Sticky nav --></header>
    <main>
        <section id="hero"><!-- Intro --></section>
        <section id="author"><!-- Timeline --></section>
        <section id="genesis"><!-- 2x2 grid --></section>
        <section id="curiosities"><!-- 2x2 grid --></section>
        <section id="symbols"><!-- Character grid --></section>
        <section id="impact"><!-- Charts --></section>
        <section id="adaptations"><!-- Carousel --></section>
    </main>
    <div id="character-modal"><!-- Modal --></div>
    <script>
        // JavaScript components
    </script>
</body>
</html>
```

## Wskazówki

1. **Treść przed formą**: Najpierw zbierz wszystkie ciekawostki z review.md
2. **Kontekst w danych**: Wykresy muszą pokazywać relacje, nie pojedyncze liczby
3. **Interaktywność**: Timeline, karty postaci i karuzela zwiększają zaangażowanie
4. **Spójność wizualna**: Używaj tej samej palety kolorów i fontów
5. **Optymalizacja**: Strona powinna ładować się szybko (CDN, lazy loading)

## Przykład: Mały Książę

Pełny przykład implementacji znajduje się w:
`books/0017_little_prince/docs/little_prince.html`

Zawiera wszystkie wymienione komponenty i może służyć jako wzór dla innych książek.