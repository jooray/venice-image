#!/usr/bin/env python3
"""
Venice AI Image Generation CLI Tool

A command-line utility to generate images using the Venice AI API.
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests


class VeniceImageGenerator:
    """Venice AI Image Generation client."""

    BASE_URL = "https://api.venice.ai/api/v1"

    # Aspect ratio presets
    ASPECT_RATIOS = {
        "square": (1024, 1024),
        "1:1": (1024, 1024),
        "landscape": (1264, 848),
        "3:2": (1264, 848),
        "cinema": (1280, 720),
        "16:9": (1280, 720),
        "tall": (720, 1280),
        "9:16": (720, 1280),
        "portrait": (848, 1264),
        "2:3": (848, 1264),
        "instagram": (1011, 1264),
        "4:5": (1011, 1264),
    }

    def __init__(self, api_key: str):
        """Initialize the Venice Image Generator with API key."""
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def list_models(self, verbose: bool = False) -> None:
        """List available image generation models."""
        url = f"{self.BASE_URL}/models"
        params = {"type": "image"}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()

            if verbose:
                print(json.dumps(data, indent=2))
            else:
                print("Available models:")
                for model in data.get("data", []):
                    model_id = model.get("id", "unknown")
                    traits = model.get("model_spec", {}).get("traits", [])
                    traits_str = f" ({', '.join(traits)})" if traits else ""
                    print(f"  - {model_id}{traits_str}")

        except requests.RequestException as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            sys.exit(1)

    def generate_image(self, prompt: str, model: str = "venice-sd35", **kwargs) -> Dict:
        """Generate an image using the Venice AI API."""
        url = f"{self.BASE_URL}/image/generate"

        # Build payload with defaults
        payload = {
            "model": model,
            "prompt": prompt,
            "format": kwargs.get("format", "jpeg"),
            "hide_watermark": True,
            "safe_mode": kwargs.get("safe_mode", False),
            "return_binary": False,
        }

        # Add optional parameters if provided
        optional_params = [
            "negative_prompt", "width", "height", "steps", "cfg_scale",
            "seed", "style_preset"
        ]

        for param in optional_params:
            if param in kwargs and kwargs[param] is not None:
                payload[param] = kwargs[param]

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Error generating image: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response:
                try:
                    error_data = e.response.json()
                    print(f"API Error: {error_data}", file=sys.stderr)
                except:
                    print(f"Response: {e.response.text}", file=sys.stderr)
            sys.exit(1)

    def save_image(self, base64_data: str, output_path: Optional[str],
                   image_id: str, format_ext: str) -> str:
        """Save base64 image data to file."""
        # Determine output filename
        if output_path:
            filename = output_path
        else:
            filename = f"{image_id}.{format_ext}"

        # Handle file conflicts by adding suffix
        original_filename = filename
        counter = 1
        while Path(filename).exists():
            name_part = Path(original_filename).stem
            ext_part = Path(original_filename).suffix
            filename = f"{name_part}_{counter}{ext_part}"
            counter += 1

        # Decode and save image
        try:
            image_data = base64.b64decode(base64_data)
            with open(filename, 'wb') as f:
                f.write(image_data)
            return filename
        except Exception as e:
            print(f"Error saving image: {e}", file=sys.stderr)
            sys.exit(1)


def parse_aspect_ratio(ar_string: str) -> Tuple[int, int]:
    """Parse aspect ratio string and return width, height."""
    ar_lower = ar_string.lower()
    if ar_lower in VeniceImageGenerator.ASPECT_RATIOS:
        return VeniceImageGenerator.ASPECT_RATIOS[ar_lower]

    # Try to parse custom ratio like "4:3"
    if ":" in ar_string:
        try:
            w_ratio, h_ratio = map(float, ar_string.split(":"))
            # Calculate dimensions maintaining the ratio, targeting around 1024 pixels
            base_size = 1024
            if w_ratio >= h_ratio:
                width = base_size
                height = int(base_size * h_ratio / w_ratio)
            else:
                height = base_size
                width = int(base_size * w_ratio / h_ratio)

            # Round to nearest multiple of 8 (common requirement for AI models)
            width = ((width + 7) // 8) * 8
            height = ((height + 7) // 8) * 8

            return width, height
        except ValueError:
            pass

    raise ValueError(f"Invalid aspect ratio: {ar_string}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate images using Venice AI API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list-models
  %(prog)s "A beautiful sunset" --model flux-dev
  %(prog)s "A cat in space" --ar square --output cat.png --format png
  %(prog)s "Mountain landscape" --negative-prompt "people, cars" --steps 30
        """
    )

    # API key from environment
    api_key = os.getenv("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)

    # Command options
    parser.add_argument("--list-models", action="store_true",
                       help="List available image generation models")
    parser.add_argument("--verbose", action="store_true",
                       help="Show detailed output (for --list-models)")

    # Image generation options
    parser.add_argument("prompt", nargs="?", help="Text prompt for image generation")
    parser.add_argument("--model", default="venice-sd35",
                       help="Model to use for generation (default: venice-sd35)")
    parser.add_argument("--negative-prompt", help="Negative prompt to avoid certain elements")

    # Dimensions
    parser.add_argument("--width", type=int, help="Image width in pixels")
    parser.add_argument("--height", type=int, help="Image height in pixels")
    parser.add_argument("--ar", "--aspect-ratio", dest="aspect_ratio",
                       help="Aspect ratio (square, landscape, cinema, tall, portrait, instagram, or custom like 4:3)")

    # Generation parameters
    parser.add_argument("--steps", type=int, help="Number of inference steps")
    parser.add_argument("--cfg-scale", type=float, help="CFG scale for prompt adherence")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible results")
    parser.add_argument("--style-preset", help="Style preset to apply")

    # Output options
    parser.add_argument("--format", choices=["jpeg", "png", "webp"], default="jpeg",
                       help="Output image format (default: jpeg)")
    parser.add_argument("--output", help="Output filename")
    parser.add_argument("--safe-mode", action="store_true",
                       help="Enable safe mode content filtering")

    args = parser.parse_args()

    # Initialize client
    client = VeniceImageGenerator(api_key)

    # Handle list models command
    if args.list_models:
        client.list_models(verbose=args.verbose)
        return

    # Require prompt for image generation
    if not args.prompt:
        parser.error("Prompt is required for image generation. Use --list-models to see available models.")

    # Handle dimensions
    width = args.width
    height = args.height

    if args.aspect_ratio:
        if width or height:
            parser.error("Cannot specify both --ar and --width/--height")
        try:
            width, height = parse_aspect_ratio(args.aspect_ratio)
        except ValueError as e:
            parser.error(str(e))

    # Prepare generation parameters
    gen_params = {
        "format": args.format,
        "safe_mode": args.safe_mode,
    }

    if args.negative_prompt:
        gen_params["negative_prompt"] = args.negative_prompt
    if width:
        gen_params["width"] = width
    if height:
        gen_params["height"] = height
    if args.steps:
        gen_params["steps"] = args.steps
    if args.cfg_scale:
        gen_params["cfg_scale"] = args.cfg_scale
    if args.seed:
        gen_params["seed"] = args.seed
    if args.style_preset:
        gen_params["style_preset"] = args.style_preset

    # Generate image
    print(f"Generating image with model '{args.model}'...")
    result = client.generate_image(args.prompt, args.model, **gen_params)

    # Extract and save images
    images = result.get("images", [])
    if not images:
        print("No images returned from API", file=sys.stderr)
        sys.exit(1)

    image_id = result.get("id", "generated_image")

    # Save first image (Venice API typically returns one image)
    base64_data = images[0]
    filename = client.save_image(base64_data, args.output, image_id, args.format)

    print(f"Image saved as: {filename}")

    # Show timing info if available
    timing = result.get("timing", {})
    if timing:
        total_time = timing.get("total", 0) / 1000  # Convert to seconds
        print(f"Generation completed in {total_time:.2f} seconds")


if __name__ == "__main__":
    main()
