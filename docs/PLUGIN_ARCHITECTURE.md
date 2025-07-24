# Image Generator Plugin Architecture

## Overview

The 37degrees project now supports a plugin-based architecture for image generators, allowing easy integration of different AI image generation services. This document describes how to use and develop generator plugins.

## Architecture Components

### 1. Base Class (`src/generators/base.py`)

All generators must inherit from `BaseImageGenerator`:

```python
class BaseImageGenerator(ABC):
    def __init__(self, config: Dict[str, Any])
    
    @abstractmethod
    def test_connection(self) -> bool
    
    @abstractmethod
    def generate_image(self, prompt: str, negative_prompt: str = "", 
                      width: int = 1080, height: int = 1920, 
                      seed: int = -1, **kwargs) -> Optional[str]
    
    @abstractmethod
    def download_image(self, image_id: str, output_path: Path) -> bool
```

### 2. Generator Registry (`src/generators/registry.py`)

The registry manages all available generators:

```python
from src.generators import GeneratorRegistry

registry = GeneratorRegistry()
registry.register('my_generator', MyGeneratorClass)
generator = registry.get_generator('my_generator', config)
```

### 3. Configuration (`config/generators.yaml`)

Generators are configured in YAML:

```yaml
generators:
  my_generator:
    class: MyGeneratorClass
    api_key: ${MY_API_KEY}  # Environment variable
    base_url: https://api.example.com
    custom_param: value

default_generator: my_generator
```

## Available Generators

### 1. InvokeAI Generator

Primary production generator using InvokeAI local server.

**Configuration:**
```yaml
invokeai:
  class: InvokeAIGenerator
  base_url: http://localhost:9090
  default_model: model-uuid
  board_name: "37degrees - Generated Images"
  max_wait: 30
```

**Features:**
- Board organization
- SDXL resolution optimization
- Style preset support
- Retry mechanism

### 2. ComfyUI Generator

Alternative generator with workflow support.

**Configuration:**
```yaml
comfyui:
  class: ComfyUIGenerator
  server_address: 127.0.0.1:8188
  workflow_template: workflows/default_workflow.json
  timeout: 120
```

**Features:**
- Custom workflow support
- WebSocket monitoring
- Flexible node configuration

### 3. Mock Generator

Testing generator that creates placeholder images.

**Configuration:**
```yaml
mock:
  class: MockGenerator
  delay: 2
  fail_rate: 0.0
  placeholder_style: detailed  # simple, detailed, debug
```

**Features:**
- No external dependencies
- Configurable failure simulation
- Visual placeholder styles

## Using Generators

### Command Line

```bash
# Use default generator
python main.py ai 17

# Use specific generator
python main.py ai 17 --generator mock

# Use mock for testing
TESTING=true python main.py ai 17
```

### In Code

```python
from src.generators import GeneratorRegistry
from pathlib import Path

# Initialize registry
registry = GeneratorRegistry()
registry.load_config(Path('config/generators.yaml'))

# Get generator
generator = registry.get_generator('invokeai')

# Test connection
if generator.test_connection():
    # Generate image
    image_id = generator.generate_image(
        prompt="A beautiful sunset",
        negative_prompt="text, watermark",
        width=1080,
        height=1920
    )
    
    # Download result
    if image_id:
        generator.download_image(image_id, Path('output.png'))
```

## Creating a New Generator

### Step 1: Create Generator Class

Create a new file `src/generators/my_generator.py`:

```python
from typing import Dict, Optional, Any
from pathlib import Path
from .base import BaseImageGenerator, GeneratorError

class MyGenerator(BaseImageGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url')
    
    def test_connection(self) -> bool:
        # Test API connection
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def generate_image(self, prompt: str, negative_prompt: str = "",
                      width: int = 1080, height: int = 1920,
                      seed: int = -1, **kwargs) -> Optional[str]:
        # Call API to generate image
        response = requests.post(
            f"{self.base_url}/generate",
            json={
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "seed": seed
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        if response.status_code == 200:
            return response.json()['image_id']
        else:
            raise GeneratorError(f"Generation failed: {response.text}")
    
    def download_image(self, image_id: str, output_path: Path) -> bool:
        # Download generated image
        response = requests.get(
            f"{self.base_url}/images/{image_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        if response.status_code == 200:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        return False
```

### Step 2: Register Generator

In your main code or `src/cli/ai.py`:

```python
from src.generators import GeneratorRegistry
from src.generators.my_generator import MyGenerator

registry = GeneratorRegistry()
registry.register('my_generator', MyGenerator)
```

### Step 3: Add Configuration

Add to `config/generators.yaml`:

```yaml
generators:
  my_generator:
    class: MyGenerator
    api_key: ${MY_GENERATOR_API_KEY}
    base_url: https://api.mygenerator.com
    # Add any custom parameters
```

### Step 4: Use Generator

```bash
python main.py ai 17 --generator my_generator
```

## Error Handling

The plugin system includes several error types:

- `GeneratorError`: Base exception for all generator errors
- `GeneratorConnectionError`: Connection failures
- `GeneratorTimeoutError`: Generation timeouts
- `GeneratorLimitError`: API rate limits

Use the `@retry_with_backoff` decorator for automatic retries:

```python
@retry_with_backoff(max_retries=3)
def generate_image(self, prompt: str, **kwargs):
    # Implementation with automatic retry
```

## Best Practices

1. **Always implement `test_connection()`** to verify service availability
2. **Use environment variables** for sensitive data (API keys)
3. **Implement proper error handling** with meaningful messages
4. **Support dimension validation** via `validate_dimensions()`
5. **Add retry logic** for transient failures
6. **Log operations** using Rich console
7. **Create mock generators** for testing workflows

## Testing

Test your generator implementation:

```python
# Test connection
assert generator.test_connection()

# Test with mock generator
mock_gen = registry.get_generator('mock', {'delay': 0})
image_id = mock_gen.generate_image("test prompt")
assert mock_gen.download_image(image_id, Path("test.png"))
```

## Environment Variables

Generators can use environment variables in config:

```yaml
my_generator:
  api_key: ${MY_API_KEY}
  endpoint: ${MY_ENDPOINT:-https://default.com}
```

Set environment variables:

```bash
export MY_API_KEY=your-key-here
export MY_ENDPOINT=https://api.example.com
```