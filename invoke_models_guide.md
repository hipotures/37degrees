# InvokeAI Model Guide for 37degrees Project

## Recommended Base Models for Non-Realistic Illustrations

### 1. **DreamShaper XL** ⭐ NAJLEPSZY WYBÓR
- **Styl**: Fantastyczny, ilustracyjny, łatwo kontrolowalny
- **Idealny dla**: Baśnie, fantasy (Hobbit, Władca Pierścieni, Harry Potter)
- **Link**: https://civitai.com/models/4384/dreamshaper-xl

### 2. **Pony Diffusion XL** ⭐ DLA MŁODSZYCH
- **Styl**: Kreskówkowy, anime, bardzo kreatywny
- **Idealny dla**: Książki dla dzieci (Mały Książę, Alicja w Krainie Czarów)
- **Link**: https://civitai.com/models/257749/pony-diffusion-v6-xl

### 3. **Playground v2.5** 
- **Styl**: Żywe kolory, silny kontrast, stylizowany
- **Idealny dla**: Książki przygodowe, sci-fi (Dune, Solaris)

### 4. **Deliberate v2**
- **Styl**: Realistyczne ilustracje z artystycznym twistem
- **Idealny dla**: Klasyka, dramaty (Anna Karenina, Romeo i Julia)

### 5. **Inkpunk Diffusion**
- **Styl**: Edgy, unikalny styl ilustracji
- **Idealny dla**: Dystopie (1984, Folwark Zwierzęcy)

## ControlNet dla Spójności

### Openpose ControlNet
- Kontroluje pozę postaci
- Przydatne dla scen z ludźmi
- Ustaw strength na 0.5-0.7

### Canny ControlNet  
- Zachowuje krawędzie i kompozycję
- Świetne do zachowania stylu między scenami

### Reference ControlNet
- Utrzymuje spójność stylu
- Idealne dla serii ilustracji

## LoRA dla Stylów Książkowych

### 1. **Children's Book Illustration LoRA**
```
Strength: 0.6-0.8
Trigger: "children book illustration"
```

### 2. **Watercolor Style LoRA**
```
Strength: 0.5-0.7
Trigger: "watercolor painting"
```

### 3. **Flat Design LoRA**
```
Strength: 0.7-0.9
Trigger: "flat design, minimal"
```

## Ustawienia dla Różnych Gatunków

### Baśnie (Mały Książę, Alicja)
```yaml
model: DreamShaper XL
lora: Children's Book Illustration (0.7)
negative_prompt: "photorealistic, complex, detailed shading, 3d render"
steps: 30
cfg_scale: 7
sampler: DPM++ 2M Karras
```

### Fantasy (Hobbit, Harry Potter)
```yaml
model: DreamShaper XL
controlnet: Openpose (0.6)
negative_prompt: "photorealistic, modern, technological"
steps: 35
cfg_scale: 8
sampler: Euler a
```

### Klasyka (Anna Karenina, Jane Eyre)
```yaml
model: Deliberate v2
lora: Vintage Illustration (0.5)
negative_prompt: "anime, cartoon, 3d, photorealistic"
steps: 30
cfg_scale: 7.5
sampler: DPM++ 2M Karras
```

### Dystopie (1984, Brave New World)
```yaml
model: Inkpunk Diffusion
controlnet: Canny (0.7)
negative_prompt: "colorful, cheerful, photorealistic"
steps: 35
cfg_scale: 8.5
sampler: DDIM
```

### Przygody (Tom Sawyer, Robinson Crusoe)
```yaml
model: Playground v2.5
lora: Adventure Style (0.6)
negative_prompt: "dark, gloomy, photorealistic, 3d"
steps: 30
cfg_scale: 7
sampler: UniPC
```

## Workflow dla Spójnej Serii

1. **Wybierz główny model** bazując na gatunku
2. **Dodaj LoRA** dla konkretnego stylu (opcjonalnie)
3. **Użyj ControlNet Reference** dla pierwszej sceny
4. **Generuj kolejne sceny** używając tej samej konfiguracji
5. **Zapisz seed** dla powtarzalności

## Przykładowy Prompt Template

```
[STYLE] illustration of [SCENE_DESCRIPTION], 
[MOOD] atmosphere, [COLOR_PALETTE] colors,
children's book style, simple shapes, 
clear space in upper third for text overlay,
vertical composition, 9:16 aspect ratio

Negative: photorealistic, complex textures, detailed shading, 
3d render, text, letters, words, typography
```

## VAE dla Lepszych Kolorów

- **vae-ft-mse-840000-ema**: Standardowy, dobry dla większości
- **kl-f8-anime2**: Lepszy dla stylów anime/cartoon
- **sdxl_vae**: Dla modeli SDXL

## IP Adapter (Opcjonalnie)

Użyj do transferu stylu z obrazu referencyjnego:
- **Strength**: 0.3-0.5
- **Mode**: "Style Transfer"

## Tips

1. **Consistency Token**: Dodaj unikalny token do każdej książki, np. `37deg_little_prince_style`
2. **Batch Generation**: Generuj 4-8 wariantów i wybierz najlepszy
3. **Seed Variation**: Użyj subseed strength 0.1-0.2 dla subtelnych wariacji
4. **Resolution**: Zawsze 1080x1920 dla TikTok

## Instalacja Modeli w InvokeAI

1. Otwórz Model Manager w UI
2. Kliknij "Add Model" → "Add Checkpoint"
3. Wklej link z Civitai lub HuggingFace
4. Poczekaj na pobranie
5. Model pojawi się w liście

Alternatywnie przez CLI:
```bash
invokeai-model-install --add https://civitai.com/api/download/models/[MODEL_ID]
```