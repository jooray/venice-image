# Venice AI Image Generator

A command-line utility for generating images using the Venice AI API.

## Features

- Generate images from text prompts using various AI models
- List available models with their capabilities
- Support for multiple aspect ratios and custom dimensions
- Configurable generation parameters (steps, CFG scale, seed, etc.)
- Multiple output formats (JPEG, PNG, WebP)
- Automatic file naming with conflict resolution
- Safe mode and content filtering options

## Installation

1. Clone or download this project
2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
3. Set your Venice AI API key as an environment variable:
   ```bash
   export VENICE_API_KEY="your_api_key_here"
   ```

## Usage

### List Available Models

```bash
poetry run python venice_image_gen.py --list-models
```

For detailed model information:
```bash
poetry run python venice_image_gen.py --list-models --verbose
```

### Generate Images

Basic image generation:
```bash
poetry run python venice_image_gen.py "A beautiful sunset over mountains"
```

With specific model and parameters:
```bash
poetry run python venice_image_gen.py "A cat in space" --model flux-dev --steps 30 --format png
```

### Aspect Ratios

Use preset aspect ratios:
```bash
poetry run python venice_image_gen.py "Landscape photo" --ar landscape
poetry run python venice_image_gen.py "Portrait photo" --ar portrait
poetry run python venice_image_gen.py "Square image" --ar square
```

Available presets:
- `square` or `1:1` → 1024×1024
- `landscape` or `3:2` → 1264×848
- `cinema` or `16:9` → 1280×720
- `tall` or `9:16` → 720×1280
- `portrait` or `2:3` → 848×1264
- `instagram` or `4:5` → 1011×1264

Custom aspect ratios:
```bash
poetry run python venice_image_gen.py "Custom ratio" --ar 4:3
```

### Advanced Options

```bash
poetry run python venice_image_gen.py "Detailed prompt" \
  --model flux-dev \
  --negative-prompt "blurry, low quality" \
  --steps 25 \
  --cfg-scale 7.5 \
  --seed 123456 \
  --format png \
  --output my_image.png \
  --safe-mode
```

### Command Line Options

- `--list-models` - List available models
- `--verbose` - Show detailed output (with --list-models)
- `--model MODEL` - Specify model (default: venice-sd35)
- `--negative-prompt TEXT` - Negative prompt to avoid elements
- `--width WIDTH` - Image width in pixels
- `--height HEIGHT` - Image height in pixels
- `--ar RATIO` - Aspect ratio (preset or custom like 4:3)
- `--steps STEPS` - Number of inference steps
- `--cfg-scale SCALE` - CFG scale for prompt adherence
- `--seed SEED` - Random seed for reproducible results
- `--style-preset PRESET` - Style preset to apply
- `--format FORMAT` - Output format (jpeg, png, webp)
- `--output FILENAME` - Output filename
- `--safe-mode` - Enable content filtering

## Examples

```bash
# List models
poetry run python venice_image_gen.py --list-models

# Basic generation
poetry run python venice_image_gen.py "A serene lake at dawn"

# High-quality generation with specific settings
poetry run python venice_image_gen.py "Photorealistic portrait of a wise old wizard" \
  --model flux-dev \
  --steps 30 \
  --cfg-scale 8.0 \
  --format png \
  --ar portrait

# Generate with negative prompt
poetry run python venice_image_gen.py "Beautiful garden" \
  --negative-prompt "people, cars, buildings" \
  --ar landscape

# Reproducible generation with seed
poetry run python venice_image_gen.py "Abstract art" \
  --seed 42 \
  --steps 25
```

## Environment Variables

- `VENICE_API_KEY` - Your Venice AI API key (required)

## File Output

Generated images are saved with automatic naming:
- If `--output` is specified, uses that filename
- Otherwise, uses format: `{image_id}.{format}`
- If file exists, adds suffix: `{name}_1.{ext}`, `{name}_2.{ext}`, etc.

