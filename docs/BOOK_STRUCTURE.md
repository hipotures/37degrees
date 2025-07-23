# Struktura katalogu książki

Każda książka w projekcie 37degrees ma następującą strukturę katalogów:

```
books/NNNN_book_name/
├── book.yaml           # Główna konfiguracja książki (wymagane)
├── docs/               # Dokumentacja i materiały badawcze
│   ├── README.md       # Opis zawartości katalogu docs
│   ├── review.md       # Fascynujące odkrycia o książce
│   ├── notes.md        # Notatki robocze
│   └── research.md     # Materiały badawcze
├── assets/             # Dodatkowe zasoby
│   ├── quotes/         # Cytaty z książki
│   └── characters/     # Opisy postaci
├── audio/              # Pliki audio
│   ├── theme.mp3       # Muzyka tematyczna
│   └── narration.mp3   # Narracja (przyszłość)
├── covers/             # Okładki książki
│   └── cover.jpg       # Główna okładka
├── generated/          # Wygenerowane obrazy AI
│   ├── scene_00_*.png  # Sceny do video
│   └── ...
├── prompts/            # Prompty dla AI
│   ├── scene_01_prompt.yaml
│   └── ...
└── frames/             # Klatki video (gitignore)
```

## Katalog docs/

Katalog `docs/` zawiera całą dokumentację związaną z książką:

### review.md
Zawiera fascynujące fakty, ciekawostki i mniej znane informacje o książce:
- Historia powstania
- Biograficzne ciekawostki o autorze
- Symbolika i ukryte znaczenia
- Recepcja kulturowa
- Adaptacje
- Rekordy i statystyki

### notes.md (opcjonalnie)
Notatki robocze podczas przygotowania:
- Pomysły na slajdy
- Cytaty do wykorzystania
- Koncepcje wizualne

### research.md (opcjonalnie)
Zebrany materiał badawczy:
- Linki do źródeł
- Cytaty z wywiadów
- Analizy krytyków

## Generowanie dokumentacji

1. **Automatyczne tworzenie struktury**:
   ```bash
   python scripts/create_docs_structure.py
   ```

2. **Generowanie review.md**:
   - Użyj promptu z instrukcjami wyszukiwania
   - Zapisz wyniki w `books/NNNN_book_name/docs/review.md`

## Wykorzystanie dokumentacji

Dokumentacja z katalogu `docs/` jest wykorzystywana do:
- Tworzenia angażujących tekstów na slajdy
- Znajdowania ciekawych faktów dla hooka
- Wyboru najlepszych cytatów
- Przygotowania CTA (call to action)