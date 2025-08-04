# TODO - 37degrees Project

## Usprawnienie procesu generowania obrazów

### Problem
Obecnie przy generowaniu obrazów w ChatGPT tworzymy listy z nazwami czatów, co jest nieefektywne.

### Rozwiązanie
Zamiast list z nazwami czasów, przy generowaniu scen zapisywać **ID wątka** z sesji ChatGPT.

### Przykład z sesji:
```
Przebieg 1
## ✅ ChatGPT Image Generation Automation Complete!

The automation process for generating images from the 0031_solaris scene_23.json file has been **successfully completed**. Here's a summary of what was accomplished:

### ✅ **Success Indicators:**
- **File uploaded**: scene_23.json from `/home/xai/DEV/37degrees/books/0031_solaris/prompts/genimage/scene_23.json`
- **Tool selected**: "Create image" tool activated
- **Prompt entered**: "Wygeneruj obraz opisany załączonym jsonem"
- **Generation started**: Status progressed through: "Thinking" → "Reading documents" → "Getting started"
- **New conversation created**: URL changed to unique thread `c/688be883-c554-8332-9e61-e5e57577d91e`
- **Page title updated**: Now shows "Generowanie obrazu z JSON"
```

### Implementacja
- ID wątka: `c/688be883-c554-8332-9e61-e5e57577d91e`
- Zamiast list nazw czatów tworzyć mapowanie: `scene_XX.json` → `thread_id`
- Łatwiejsze śledzenie i pobieranie wygenerowanych obrazów
- Możliwość bezpośredniego dostępu do konwersacji

### Korzyści
1. Precyzyjne śledzenie każdej sceny
2. Łatwiejszy dostęp do wygenerowanych obrazów
3. Możliwość ponownego wygenerowania konkretnej sceny
4. Eliminacja błędów związanych z nazwami chatów i szukania chatów


#### Programowa obsługa TODO
0. Primery key Project_id
1. Podaj pierwszy TODO do zrobienia
2. Podaj zrobione
3. Podaj niezrobione
4. Update pozycji TODO
5. Append to TODO
6. Clear all states for TODO