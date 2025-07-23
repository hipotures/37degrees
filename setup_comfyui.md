# ComfyUI Setup for 37degrees Project

## Installation

1. **Clone ComfyUI:**
```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run with RTX 4090 optimizations:**
```bash
python main.py --gpu-only --highvram --use-pytorch-cross-attention
```

## API Usage for Batch Processing

### 1. Enable API Mode
- In ComfyUI interface, click settings icon
- Enable "Dev mode Options"
- Use "Save (API format)" button to save workflow as JSON

### 2. Example API Script
```python
import json
import requests
import yaml
from pathlib import Path

def generate_image_from_prompt(prompt_yaml_path, output_path):
    """Generate image using ComfyUI API"""
    
    # Load our YAML prompt
    with open(prompt_yaml_path, 'r') as f:
        prompt_data = yaml.safe_load(f)
    
    # ComfyUI workflow template (save from UI first)
    with open('comfyui_workflow.json', 'r') as f:
        workflow = json.load(f)
    
    # Update prompt in workflow
    # (adjust based on your workflow structure)
    workflow["6"]["inputs"]["text"] = str(prompt_data)
    
    # Send to ComfyUI API
    response = requests.post(
        "http://127.0.0.1:8188/prompt",
        json={"prompt": workflow}
    )
    
    # Wait for completion and save result
    # (implementation depends on ComfyUI version)
```

### 3. Batch Processing Script
```bash
#!/bin/bash
# batch_generate.sh

for prompt in books/little_prince/prompts/scene_*.yaml; do
    scene_num=$(basename "$prompt" .yaml | sed 's/scene_//')
    output="books/little_prince/generated/scene_${scene_num}.png"
    
    python generate_with_comfyui.py "$prompt" "$output"
    echo "Generated: $output"
done
```

## Recommended Models for Children's Book Style

1. **Stable Diffusion XL** - Good for general illustration
2. **DreamShaper XL** - Artistic, dreamlike quality
3. **Juggernaut XL** - Versatile style control
4. **Custom LoRA** - Train on children's book illustrations

## RTX 4090 Performance

- First generation: ~40 seconds (includes model loading)
- Subsequent generations: ~15-20 seconds
- FLUX models at 1024x1024: 15-17 seconds

## Tips for Our Use Case

1. Use negative prompts:
   - "photorealistic, complex, detailed, realistic lighting"
   
2. Add style modifiers:
   - "children's book illustration"
   - "flat colors"
   - "simple shapes"
   
3. Samplers for consistency:
   - Euler a
   - DPM++ 2M Karras
   - 20-30 steps

## Alternative: InvokeAI CLI

If ComfyUI API is too complex, InvokeAI offers direct CLI:

```bash
invokeai-generate \
    --prompt "$(cat prompt.txt)" \
    --outdir ./output \
    --sampler k_euler_a \
    --steps 25 \
    --cfg-scale 7.5 \
    --width 1080 \
    --height 1920
```