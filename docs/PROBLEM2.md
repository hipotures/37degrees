# PROBLEM2: Nieprawidłowa struktura JSON w generatorze scen

## Status: ZIDENTYFIKOWANY
**Data:** 2025-08-01  
**Priorytet:** MEDIUM  
**Dotyczy:** Generator scen (37d-s1-gen-scenes)

## Problem

Aktualnie generowane pliki YAML scen mają nieprawidłową **płaską strukturę** zamiast wymaganej **struktury 3-poziomowej**.

### Obecna (nieprawidłowa) struktura:
```json
{
  "sceneDescription": { ... },
  "colorPalette": { ... },
  "lighting": { ... },
  "rendering": { ... },
  "lineArt": { ... },
  "perspective": "...",
  "mood": { ... },
  "stylePrecedents": [...],
  "technicalSpecifications": { ... }
}
```

### Wymagana (prawidłowa) struktura:
```json
{
  "sceneDescription": {
    "setting": { ... },
    "characters": [ ... ],
    "scene": { ... },
    "composition": { ... }
  },
  "visualElements": {
    "colorPalette": { ... },
    "lighting": { ... },
    "rendering": { ... },
    "lineArt": { ... },
    "perspective": "...",
    "mood": { ... },
    "stylePrecedents": [ ... ]
  },
  "technicalSpecifications": {
    "resolution": { ... },
    "orientation": "..."
  }
}
```

## Źródło problemu

Zgodnie z dokumentacją `@.claude/commands/37d-s1-gen-scenes.md`, JSON powinien składać się z **3 logicznych sekcji**:

1. **`sceneDescription`** - opis sceny, postacie, setting, kompozycja
2. **`visualElements`** - wszystkie aspekty wizualne (kolory, oświetlenie, rendering, mood, style)
3. **`technicalSpecifications`** - specyfikacje techniczne (rozdzielczość, orientacja)

## Wpływ na funkcjonalność

### ✅ Co działa poprawnie:
- ChatGPT rozpoznaje i przetwarza obie struktury (płaską i hierarchiczną)
- Generowanie obrazów działa z obiema wersjami
- Konwersja JSON → YAML zachowuje strukturę

### ❌ Problemy strukturalne:
- **Brak logicznego grupowania:** Elementy wizualne są rozproszone na poziomie root
- **Trudność w utrzymaniu:** Brak jasnego podziału odpowiedzialności
- **Niezgodność z dokumentacją:** Struktura nie odpowiada opisowi w 37d-s1-gen-scenes.md
- **Potencjalne problemy przyszłościowe:** Nowe funkcje mogą wymagać prawidłowej hierarchii

## Testowanie

### Test przeprowadzony:
- **Plik:** `scene_04.yaml` (Solaris)
- **Konwersja:** JSON → YAML → YAML z poprawną strukturą
- **Wynik:** Wszystkie 3 warianty działają w ChatGPT

### Lokalizacja testów:
```
/tmp/scene_04_test.yaml          # Płaska struktura (kopia JSON)
/tmp/scene_04_corrected.yaml     # Poprawiona struktura 3-poziomowa
```

## Rozwiązanie

### 1. Zaktualizuj generator scen
Plik: `config/prompt/scene-description-template.yaml`

**PRZED:**
```json
{
  "sceneDescription": { ... },
  "colorPalette": { ... },
  "lighting": { ... }
}
```

**PO:**
```json
{
  "sceneDescription": {
    "setting": { ... },
    "characters": [ ... ],
    "scene": { ... },
    "composition": { ... }
  },
  "visualElements": {
    "colorPalette": { ... },
    "lighting": { ... },
    "rendering": { ... },
    "lineArt": { ... },
    "perspective": "...",
    "mood": { ... },
    "stylePrecedents": [ ... ]
  },
  "technicalSpecifications": {
    "resolution": { ... },
    "orientation": "..."
  }
}
```

### 2. Zaktualizuj istniejące pliki scen
- Wszystkie pliki `books/*/prompts/scenes/*/scene_*.yaml`
- Można użyć skryptu konwersji lub przeregenerować sceny

### 3. Zaktualizuj narzędzia przetwarzające
- Upewnij się, że wszystkie narzędzia obsługują nową strukturę
- Zachowaj backward compatibility z płaską strukturą

## Priorytety

### Wysokie:
- Aktualizacja template'u `scene-description-template.yaml`
- Testy z nową strukturą

### Średnie:
- Konwersja istniejących plików scen
- Dokumentacja zmian

### Niskie:
- Optymalizacja narzędzi pod nową strukturę

## Notatki implementacyjne

- **Kompatybilność wsteczna:** Zachowaj obsługę płaskiej struktury podczas migracji
- **Testowanie:** Sprawdź wszystkie typy generatorów (narrative, flexible, podcast, atmospheric, emotional)
- **Format YAML:** System teraz używa wyłącznie formatu YAML zamiast JSON

## Powiązane pliki

```
.claude/commands/37d-s1-gen-scenes.md          # Dokumentacja generatora
config/prompt/scene-description-template.json  # Template do naprawy
books/0031_solaris/prompts/genimage/scene_04.json  # Przykład problemu
```

---
**Status:** Problem zidentyfikowany, rozwiązanie zaplanowane  
**Następny krok:** Aktualizacja template'u JSON