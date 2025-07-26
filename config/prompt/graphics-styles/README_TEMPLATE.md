# Graphics Style Template Guide

## Użycie template'u

Plik `TEMPLATE_style.json` zawiera uniwersalny szablon do definiowania stylów graficznych. 

### Kluczowe zasady:

1. **Opisuj STYL, nie TREŚĆ** - wszystkie pola powinny opisywać JAK coś wygląda, nie CO przedstawia
2. **Nie wszystkie pola są wymagane** - wypełnij tylko te, które są istotne dla danego stylu
3. **Pole `technicalSpecifications` jest ZAWSZE wymagane**

### Struktura pól:

- **styleName**: Nazwa identyfikująca styl
- **description**: Zwięzły opis charakteru wizualnego
- **aiPrompts**: Słowa kluczowe dla generatorów AI (opcjonalne, ale przydatne)
- **colorPalette**: Wszystko o kolorach - paleta, kontrast, nasycenie
- **lineArt**: Charakterystyka linii - grubość, styl, tekstura
- **lighting**: Oświetlenie i cienie - kierunek, intensywność, typ
- **rendering**: Technika wykonania - od szkicu po fotorealizm
- **perspective**: Punkt widzenia - izometryczna, frontalna, etc.
- **mood**: Nastrój i emocje przekazywane przez styl
- **postProcessing**: Dodatkowe efekty jak bloom, grain, vignette
- **stylePrecedents**: Inspiracje stylem innych artystów (opcjonalne)
- **useCases**: Gdzie najlepiej stosować dany styl (opcjonalne)

### Przykłady wartości:

**colorPalette.saturation**: 
- "vibrant" - żywe, nasycone kolory
- "muted" - stonowane, przyćmione
- "monochromatic" - odcienie jednego koloru
- "desaturated" - prawie szarości

**lighting.type**:
- "flat" - brak gradientów świetlnych
- "dramatic" - silne kontrasty światła i cienia
- "soft diffused" - miękkie, rozproszone
- "studio" - profesjonalne oświetlenie studyjne

**rendering.detailLevel**:
- "minimal" - tylko niezbędne elementy
- "moderate" - umiarkowana ilość detali
- "highly detailed" - bogactwo szczegółów
- "hyperrealistic" - ekstremalne detale

### Tworzenie nowego stylu:

1. Skopiuj `TEMPLATE_style.json` do nowego pliku
2. Nazwij go opisowo, np. `vintage-poster-style.json`
3. Wypełnij odpowiednie pola
4. Usuń niewykorzystane sekcje (oprócz technicalSpecifications)
5. Zachowaj spójność w opisach - używaj podobnego języka