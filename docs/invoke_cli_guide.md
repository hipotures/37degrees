# InvokeAI CLI Guide

## Podstawowe komendy

### Uruchomienie InvokeAI CLI
```bash
# Opcja 1: Przez launcher
./invoke.sh  # lub invoke.bat na Windows
# Wybierz opcję (1)

# Opcja 2: Bezpośrednio
invokeai
```

### Lista dostępnych modeli
W InvokeAI CLI (po uruchomieniu):
```
invoke> !models
```

### Wybór modelu
```
invoke> !switch model_name
# np:
invoke> !switch dreamshaper-xl
```

### Generowanie obrazu z CLI
```
invoke> a children's book illustration of a boy with scarf on desert --width 1080 --height 1920 --steps 30 --cfg_scale 7.5
```

## Użycie invokeai-generate (jeśli dostępne)

### Podstawowa składnia
```bash
invokeai-generate \
  --prompt "your prompt here" \
  --model model_name \
  --width 1080 \
  --height 1920 \
  --steps 30 \
  --cfg_scale 7.5 \
  --sampler k_euler_a \
  --outdir ./output
```

### Lista modeli z poziomu systemu
```bash
# Sprawdź folder z modelami
ls ~/.invokeai/models/
# lub
ls ~/invokeai/models/

# Użyj model installer
invokeai-model-install --list
```

## Alternatywne podejście - Python API

```python
#!/usr/bin/env python3
from invokeai.app.api_app import ApiApp
from invokeai.app.services.config import InvokeAIAppConfig

# Inicjalizacja
config = InvokeAIAppConfig()
app = ApiApp(config)

# Lista modeli
models = app.model_manager.list_models()
for model_name, model_info in models.items():
    print(f"Model: {model_name}")
    
# Generowanie
result = app.generate(
    prompt="your prompt",
    model="dreamshaper-xl",
    width=1080,
    height=1920
)
```

## Import nowych modeli

### Z CLI
```
invoke> !import_model /path/to/model.safetensors
invoke> !import_model https://civitai.com/api/download/models/xxxxx
```

### Z linii poleceń
```bash
invokeai-model-install --add /path/to/model.safetensors
invokeai-model-install --add https://huggingface.co/model/path
```

## Batch processing dla naszego projektu

```bash
#!/bin/bash
# generate_scenes.sh

MODEL="dreamshaper-xl"  # lub inny model

for prompt_file in books/little_prince/prompts/scene_*.yaml; do
    scene_num=$(basename "$prompt_file" .yaml | sed 's/scene_//')
    
    # Konwertuj YAML na tekst
    prompt=$(python -c "
import yaml
with open('$prompt_file') as f:
    data = yaml.safe_load(f)
    # Tutaj logika konwersji YAML -> prompt text
    print(prompt_text)
    ")
    
    # Generuj przez InvokeAI
    invokeai-generate \
        --prompt "$prompt" \
        --model $MODEL \
        --width 1080 \
        --height 1920 \
        --steps 30 \
        --cfg_scale 7.5 \
        --outdir "books/little_prince/generated" \
        --output_prefix "scene_${scene_num}_"
done
```

## WebUI jako alternatywa

Jeśli CLI jest problematyczne, InvokeAI ma świetne WebUI:
```bash
# Uruchom WebUI
invokeai --web
# lub
./invoke.sh i wybierz opcję (2)
```

Następnie otwórz: http://localhost:9090

W WebUI możesz:
1. Zobaczyć wszystkie modele w dropdown menu
2. Importować nowe modele przez "Model Manager" (ikona kostki)
3. Użyć "Batch" dla wielu promptów
4. Zapisać workflow dla powtarzalności

## Tips

1. **Model naming**: Modele często mają nazwy jak:
   - `stable-diffusion-xl-base-1.0`
   - `dreamshaper-xl-v2-turbo`
   - `pony-diffusion-xl-v6`

2. **Sprawdź config**: 
   ```bash
   cat ~/.invokeai/invokeai.yaml
   # lub
   cat ~/invokeai/configs/models.yaml
   ```

3. **Logi**: Jeśli coś nie działa, sprawdź:
   ```bash
   tail -f ~/.invokeai/invokeai.log
   ```