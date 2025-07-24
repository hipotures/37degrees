# Configuration System Documentation

## Overview

The 37degrees project uses a centralized configuration system that supports:
- YAML-based configuration files
- Environment variable substitution
- Runtime overrides
- CLI parameter overrides
- Validation and defaults

## Main Configuration File

The primary configuration file is located at `config/settings.yaml`. This file contains all project-wide settings organized by sections.

### Configuration Structure

```yaml
project:
  name: 37degrees
  version: 2.0.0
  
services:
  generators:
    default: invokeai
    config_file: config/generators.yaml
    
video:
  resolution: 1080x1920
  fps: 30
  duration_per_slide: 3.5
  
# ... more sections
```

## Environment Variables

### Loading from .env Files

The configuration system automatically loads environment variables from `.env` files. The system searches for `.env` in:
1. Project root directory
2. Parent directories (if not found in root)

Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
# Edit .env with your values
```

### Variable Substitution

The configuration system supports environment variable substitution with two formats:

### Required Variables
```yaml
api_key: ${API_KEY}  # Fails if API_KEY is not set
```

### Variables with Defaults
```yaml
model: ${MODEL_NAME:-gpt-4}  # Uses 'gpt-4' if MODEL_NAME is not set
```

### Common Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_GENERATOR` | Default image generator | invokeai |
| `VIDEO_RESOLUTION` | Video resolution | 1080x1920 |
| `VIDEO_FPS` | Video frame rate | 30 |
| `OUTPUT_DIR` | Output directory | output |
| `DEBUG` | Enable debug mode | false |
| `LOG_LEVEL` | Logging level | INFO |
| `PERPLEXITY_API_KEY` | Perplexity API key | (none) |
| `GOOGLE_API_KEY` | Google API key | (none) |
| `OPENAI_API_KEY` | OpenAI API key | (none) |

## Using Configuration in Code

### Basic Usage

```python
from src.config import get_config

# Get config instance
config = get_config()

# Get values with dot notation
fps = config.get('video.fps', 30)
output_dir = config.get('paths.output_dir', 'output')

# Get entire section
video_settings = config.get_section('video')
```

### Convenience Functions

```python
from src.config import get, set_override

# Quick access
fps = get('video.fps', 30)

# Runtime override
set_override('video.fps', 60)
```

## CLI Configuration Overrides

The system supports configuration overrides from the command line:

### Custom Config File
```bash
python main.py --config my_config.yaml ai 17
```

### Set Individual Values
```bash
# Set single value
python main.py --set video.fps=60 video 17

# Set multiple values
python main.py --set video.fps=60 --set video.crf=18 video 17

# Set boolean values
python main.py --set development.debug=true ai 17
```

### Disable Banner
```bash
python main.py --no-banner list
```

## Configuration Sections

### Project Section
Basic project metadata:
```yaml
project:
  name: 37degrees
  version: 2.0.0
  description: TikTok video generator
```

### Services Section
External service configurations:
```yaml
services:
  generators:
    default: invokeai
    config_file: config/generators.yaml
  research:  # Future implementation
    default: perplexity
    providers:
      perplexity:
        api_key: ${PERPLEXITY_API_KEY}
```

### Video Section
Video generation settings:
```yaml
video:
  resolution: 1080x1920
  fps: 30
  duration_per_slide: 3.5
  codec: libx264
  gpu_encoding: true
```

### Audio Section
Audio processing settings:
```yaml
audio:
  default_volume: 0.7
  fade_in_duration: 1.0
  normalize: true
```

### Text Overlay Section
Text rendering configuration:
```yaml
text_overlay:
  default_method: outline
  outline_width: 3
  enable_color_emojis: true
```

### Paths Section
Directory configuration:
```yaml
paths:
  books_dir: books
  collections_dir: collections
  output_dir: output
  temp_dir: /tmp/37degrees
```

### Development Section
Development and debugging options:
```yaml
development:
  debug: false
  verbose: false
  parallel_processing: true
  max_workers: 4
```

### Feature Flags
Enable/disable features:
```yaml
features:
  web_generators: false
  research_api: false
  static_site: false
  batch_operations: true
```

## Configuration Precedence

Configuration values are resolved in this order (highest to lowest priority):

1. CLI `--set` overrides
2. Environment variables
3. Configuration file values
4. Default values in code

## Validation

The configuration system includes basic validation:

```python
config = get_config()
errors = config.validate()
if errors:
    for error in errors:
        print(f"Config error: {error}")
```

## Custom Configuration Files

You can create custom configuration files for different environments:

### Production Config
`config/production.yaml`:
```yaml
development:
  debug: false
  verbose: false
  
video:
  crf: 18  # Higher quality
  preset: slow  # Better compression
```

### Development Config
`config/development.yaml`:
```yaml
development:
  debug: true
  verbose: true
  
services:
  generators:
    default: mock  # Use mock generator
```

Use custom configs:
```bash
# Production
python main.py --config config/production.yaml video 17

# Development
python main.py --config config/development.yaml ai 17
```

## Best Practices

1. **Use environment variables for secrets**
   ```yaml
   api_key: ${SECRET_API_KEY}  # Never hardcode
   ```

2. **Provide sensible defaults**
   ```yaml
   timeout: ${API_TIMEOUT:-30}
   ```

3. **Group related settings**
   ```yaml
   video:
     resolution: 1080x1920
     fps: 30
     # Related settings together
   ```

4. **Document non-obvious settings**
   ```yaml
   crf: 23  # 0-51, lower = better quality
   ```

5. **Use feature flags for experimental features**
   ```yaml
   features:
     experimental_ai: ${ENABLE_EXPERIMENTAL:-false}
   ```

## Extending Configuration

To add new configuration options:

1. Add to `config/settings.yaml`
2. Use in code with `config.get()`
3. Document in this file
4. Consider adding validation

Example:
```yaml
# In settings.yaml
my_feature:
  enabled: ${MY_FEATURE_ENABLED:-false}
  timeout: ${MY_FEATURE_TIMEOUT:-60}
```

```python
# In code
from src.config import get_config

config = get_config()
if config.get('my_feature.enabled', False):
    timeout = config.get('my_feature.timeout', 60)
    # Use feature...
```