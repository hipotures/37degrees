#!/usr/bin/env python3
"""
Simple InvokeAI Generator - waits fixed time then takes the newest image
Bypasses all the batch/queue/websocket complexity
"""

import json
import time
import requests
import yaml
from pathlib import Path
from typing import Dict, Optional
import uuid
import random
from rich.console import Console
from rich.status import Status

console = Console()


class SimpleInvokeAIGenerator:
    def __init__(self, base_url: str = "http://localhost:9090"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.board_id = None
        
    def test_connection(self) -> bool:
        """Test if InvokeAI is accessible"""
        try:
            response = self.session.get(f"{self.api_url}/app/version")
            return response.status_code == 200
        except Exception as e:
            console.print(f"[red]Connection test failed: {e}[/red]")
            return False
    
    def generate_and_wait(self, prompt: str, negative_prompt: str = "", 
                         model_key: str = None, width: int = 1080, 
                         height: int = 1920, steps: int = 30, 
                         cfg_scale: float = 7.5, sampler: str = "euler_a", 
                         seed: int = -1, max_wait: int = 30) -> Optional[str]:
        """Generate image and wait for completion (checks every second)"""
        
        # Create workflow
        workflow = self._create_text2img_workflow(
            prompt=prompt,
            negative_prompt=negative_prompt,
            model_key=model_key,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            sampler=sampler,
            seed=seed
        )
        
        # Submit generation request
        request_data = {
            "prepend": False,
            "batch": {
                "graph": workflow,
                "runs": 1,
                "data": []
            }
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/queue/default/enqueue_batch",
                json=request_data
            )
            
            if response.status_code != 200:
                console.print(f"[red]Failed to enqueue: {response.text}[/red]")
                return None
                
            result = response.json()
            batch_id = result.get("batch", {}).get("batch_id")
            console.print(f"[yellow]Generation started: {batch_id}[/yellow]")
            
            # Get current images before generation
            before_images = self._get_latest_images(limit=5)
            before_names = {img['image_name'] for img in before_images}
            
            # Wait and check for new image
            with console.status("[cyan]Generating image...[/cyan]") as status:
                for i in range(max_wait):
                    elapsed = i + 1
                    status.update(f"[cyan]Generating image... {elapsed}s[/cyan]")
                    
                    # Check for new image every second after 5 seconds
                    if i >= 5:
                        current_images = self._get_latest_images(limit=5)
                        for img in current_images:
                            if img['image_name'] not in before_names:
                                status.stop()
                                console.print(f"[green]✓ New image ready: {img['image_name']} (after {elapsed}s)[/green]")
                                
                                # Add to board if we have one
                                if self.board_id:
                                    if self.add_image_to_board(self.board_id, img['image_name']):
                                        console.print(f"[green]✓ Added to board[/green]")
                                    else:
                                        console.print(f"[yellow]⚠ Failed to add to board[/yellow]")
                                
                                return img['image_name']
                    
                    time.sleep(1)
            
            console.print("[red]✗ No new image found within timeout[/red]")
            return None
                
        except Exception as e:
            console.print(f"[red]Error generating image: {e}[/red]")
            return None
    
    def _get_latest_images(self, limit: int = 1):
        """Get latest images from InvokeAI"""
        try:
            response = self.session.get(
                f"{self.api_url}/images/",
                params={"limit": limit, "order_by": "created_at", "order_dir": "DESC"}
            )
            
            if response.status_code == 200:
                return response.json().get("items", [])
            return []
            
        except Exception as e:
            console.print(f"[red]Error getting images: {e}[/red]")
            return []
    
    def _create_text2img_workflow(self, **params) -> Dict:
        """Create a text2img workflow"""
        # Generate unique IDs for nodes
        model_id = str(uuid.uuid4())
        compel_pos_id = str(uuid.uuid4())
        compel_neg_id = str(uuid.uuid4())
        noise_id = str(uuid.uuid4())
        denoise_id = str(uuid.uuid4())
        l2i_id = str(uuid.uuid4())
        
        workflow = {
            "name": "simple_text2img",
            "author": "37degrees",
            "description": "Simple text to image generation",
            "version": "1.0.0",
            "contact": "",
            "tags": "",
            "notes": "",
            "exposedFields": [],
            "meta": {
                "version": "3.0.0",
                "category": "default"
            },
            "id": str(uuid.uuid4()),
            "nodes": {
                model_id: {
                    "id": model_id,
                    "type": "sdxl_model_loader",
                    "position": {"x": 0, "y": 0},
                    "model": {
                        "key": params.get("model_key") or "c81f2f9b-cabd-40ec-b6f4-d3172c10bafc",
                        "hash": "blake3:d279309ea6e5ee6e8fd52504275865cc280dac71cbf528c5b07c98b888bddaba",
                        "name": "Dreamshaper XL v2 Turbo",
                        "base": "sdxl",
                        "type": "main"
                    }
                },
                compel_pos_id: {
                    "id": compel_pos_id,
                    "type": "sdxl_compel_prompt",
                    "position": {"x": 300, "y": 0},
                    "prompt": params["prompt"],
                    "style": "",
                    "original_width": params["width"],
                    "original_height": params["height"],
                    "crop_top": 0,
                    "crop_left": 0,
                    "target_width": params["width"],
                    "target_height": params["height"]
                },
                compel_neg_id: {
                    "id": compel_neg_id,
                    "type": "sdxl_compel_prompt",
                    "position": {"x": 300, "y": 200},
                    "prompt": params.get("negative_prompt", ""),
                    "style": "",
                    "original_width": params["width"],
                    "original_height": params["height"],
                    "crop_top": 0,
                    "crop_left": 0,
                    "target_width": params["width"],
                    "target_height": params["height"]
                },
                noise_id: {
                    "id": noise_id,
                    "type": "noise",
                    "position": {"x": 600, "y": 0},
                    "seed": params.get("seed", -1) if params.get("seed", -1) != -1 else random.randint(0, 2**32-1),
                    "width": params["width"],
                    "height": params["height"],
                    "use_cpu": False
                },
                denoise_id: {
                    "id": denoise_id,
                    "type": "denoise_latents",
                    "position": {"x": 900, "y": 100},
                    "steps": params["steps"],
                    "cfg_scale": params["cfg_scale"],
                    "denoising_start": 0,
                    "denoising_end": 1,
                    "scheduler": params["sampler"],
                    "cfg_rescale_multiplier": 0
                },
                l2i_id: {
                    "id": l2i_id,
                    "type": "l2i",
                    "position": {"x": 1200, "y": 100}
                }
            },
            "edges": [
                {
                    "id": str(uuid.uuid4()),
                    "source": {"node_id": model_id, "field": "unet"},
                    "destination": {"node_id": denoise_id, "field": "unet"}
                },
                {
                    "id": str(uuid.uuid4()),
                    "source": {"node_id": model_id, "field": "clip"},
                    "destination": {"node_id": compel_pos_id, "field": "clip"}
                },
                {
                    "id": str(uuid.uuid4()),
                    "source": {"node_id": model_id, "field": "clip2"},
                    "destination": {"node_id": compel_pos_id, "field": "clip2"}
                },
                {
                    "id": str(uuid.uuid4()),
                    "source": {"node_id": model_id, "field": "clip"},
                    "destination": {"node_id": compel_neg_id, "field": "clip"}
                },
                {
                    "id": str(uuid.uuid4()),
                    "source": {"node_id": model_id, "field": "clip2"},
                    "destination": {"node_id": compel_neg_id, "field": "clip2"}
                },
                {
                    "id": str(uuid.uuid4()),
                    "source": {"node_id": compel_pos_id, "field": "conditioning"},
                    "destination": {"node_id": denoise_id, "field": "positive_conditioning"}
                },
                {
                    "id": str(uuid.uuid4()),
                    "source": {"node_id": compel_neg_id, "field": "conditioning"},
                    "destination": {"node_id": denoise_id, "field": "negative_conditioning"}
                },
                {
                    "id": str(uuid.uuid4()),
                    "source": {"node_id": noise_id, "field": "noise"},
                    "destination": {"node_id": denoise_id, "field": "noise"}
                },
                {
                    "id": str(uuid.uuid4()),
                    "source": {"node_id": denoise_id, "field": "latents"},
                    "destination": {"node_id": l2i_id, "field": "latents"}
                },
                {
                    "id": str(uuid.uuid4()),
                    "source": {"node_id": model_id, "field": "vae"},
                    "destination": {"node_id": l2i_id, "field": "vae"}
                },
            ]
        }
        
        return workflow
    
    def get_or_create_board(self, board_name: str) -> Optional[str]:
        """Get or create a board by name"""
        try:
            # First check if board exists
            response = self.session.get(f"{self.api_url}/boards/?all=true")
            
            if response.status_code == 200:
                boards = response.json()
                for board in boards:
                    if board.get('board_name') == board_name:
                        console.print(f"[green]Using existing board: {board_name}[/green]")
                        return board['board_id']
            
            # Create new board
            from urllib.parse import quote
            response = self.session.post(
                f"{self.api_url}/boards/?board_name={quote(board_name)}"
            )
            
            if response.status_code == 201:
                board = response.json()
                console.print(f"[green]Created new board: {board_name}[/green]")
                return board['board_id']
            else:
                console.print(f"[red]Failed to create board: {response.text}[/red]")
                
        except Exception as e:
            console.print(f"[red]Error managing board: {e}[/red]")
        
        return None
    
    def add_image_to_board(self, board_id: str, image_name: str) -> bool:
        """Add an image to a board"""
        try:
            response = self.session.post(
                f"{self.api_url}/board_images/",
                json={"board_id": board_id, "image_name": image_name}
            )
            return response.status_code == 201
        except Exception as e:
            console.print(f"[red]Error adding image to board: {e}[/red]")
            return False
    
    def download_image(self, image_name: str, output_path: str) -> bool:
        """Download an image from InvokeAI"""
        try:
            response = self.session.get(
                f"{self.api_url}/images/i/{image_name}/full",
                stream=True
            )
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            else:
                console.print(f"[red]Failed to download image: {response.status_code}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error downloading image: {e}[/red]")
            return False


def load_invokeai_style_presets() -> Dict[str, Dict]:
    """Load InvokeAI style presets from file"""
    preset_path = Path("/home/xai/DEV/invokeai/.venv/lib/python3.12/site-packages/invokeai/app/services/style_preset_records/default_style_presets.json")
    
    if preset_path.exists():
        try:
            with open(preset_path, 'r', encoding='utf-8') as f:
                presets_data = json.load(f)
            
            presets = {}
            for preset in presets_data:
                name = preset.get('name')
                if name:
                    presets[name] = preset.get('preset_data', {})
            
            return presets
        except Exception as e:
            console.print(f"[red]Error loading presets: {e}[/red]")
    
    return {}


def build_prompt_from_scene(slide: Dict, custom_art_style: Dict, template_style: Optional[Dict] = None) -> str:
    """Build a complete prompt from scene and style information"""
    scene = slide.get('scene', {})
    
    # Add unique timestamp
    unique_id = f"unique_{int(time.time() * 1000)}"
    
    if template_style:
        # Use template style
        base_prompt = template_style.get('positive_prompt', '{prompt}')
        scene_prompt = []
    else:
        # Use custom art style
        base_prompt = None
        scene_prompt = [
            custom_art_style.get('primary_style', 'illustration'),
            f"style of {custom_art_style.get('complexity', 'simple artwork')}"
        ]
    
    # Add scene elements
    elements = scene.get('elements', [])
    if elements:
        scene_prompt.append(", ".join(elements))
    
    # Add composition
    if scene.get('composition'):
        scene_prompt.append(f"composition: {scene['composition']}")
    
    # Add atmosphere
    if scene.get('atmosphere'):
        scene_prompt.append(f"{scene['atmosphere']} mood")
    
    # Add background
    if scene.get('background'):
        scene_prompt.append(f"background: {scene['background']}")
    
    # Only add custom style specs if NOT using template
    if not template_style:
        # Add color information
        color_palette = custom_art_style.get('color_palette', {})
        if color_palette.get('base'):
            colors = ", ".join(color_palette['base'][:3])
            scene_prompt.append(f"color palette: {colors}")
            
        # Add technical specs
        scene_prompt.extend([
            "vertical composition",
            "clear space in upper third for text overlay",
            custom_art_style.get('line_work', 'clean lines'),
            custom_art_style.get('color_technique', 'flat colors'),
            custom_art_style.get('overall_feeling', 'whimsical')
        ])
    
    # Build final prompt
    if template_style:
        final_prompt = base_prompt.replace('{prompt}', ", ".join(scene_prompt))
    else:
        final_prompt = ", ".join(scene_prompt)
    
    # Add unique identifier
    final_prompt = f"{final_prompt}, {unique_id}"
        
    return final_prompt


def build_negative_prompt(custom_art_style: Dict, template_style: Optional[Dict] = None) -> str:
    """Build negative prompt from style configuration"""
    if template_style:
        return template_style.get('negative_prompt', 'text, watermark')
    else:
        negative_parts = [
            "text", "letters", "words", "typography", "writing",
            "watermark", "signature", "logo"
        ]
        
        avoid = custom_art_style.get('avoid', '')
        if avoid:
            negative_parts.append(avoid)
        
        negative_parts.extend([
            "photorealistic", "3d render", "complex textures",
            "detailed shading", "realistic lighting",
            "ugly", "deformed", "noisy", "blurry"
        ])
        
        return ", ".join(negative_parts)


def main():
    """Generate single scene or all scenes"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple InvokeAI generator - fixed wait time")
    parser.add_argument('book_yaml', help="Path to book YAML file")
    parser.add_argument('--scene', type=int, help="Generate only specific scene (0-based index)")
    parser.add_argument('--wait', type=int, default=30, help="Maximum wait time in seconds (default: 30)")
    
    args = parser.parse_args()
    
    # Load book data
    with open(args.book_yaml, 'r', encoding='utf-8') as f:
        book_data = yaml.safe_load(f)
    
    generator = SimpleInvokeAIGenerator()
    
    if not generator.test_connection():
        console.print("[red]Failed to connect to InvokeAI[/red]")
        return
    
    # Create or get board for this book
    book_title = book_data.get('book_info', {}).get('title', 'Unknown')
    board_name = f"37degrees - {book_title}"
    console.print(f"[blue]Looking for board: {board_name}[/blue]")
    generator.board_id = generator.get_or_create_board(board_name)
    
    # Get configuration
    custom_art_style = book_data.get('custom_art_style', {})
    template_art_style = book_data.get('template_art_style', '')
    ai_generation = book_data.get('ai_generation', {})
    tech_specs = book_data.get('technical_specs', {})
    slides = book_data.get('slides', [])
    
    # Load style presets
    style_presets = load_invokeai_style_presets()
    template_style = None
    if template_art_style and template_art_style in style_presets:
        template_style = style_presets[template_art_style]
        console.print(f"[green]Using style template: {template_art_style}[/green]")
    
    # Output directory
    book_path = Path(args.book_yaml)
    generated_dir = book_path.parent / "generated"
    generated_dir.mkdir(exist_ok=True)
    
    # Generate scene(s)
    if args.scene is not None:
        # Single scene
        if 0 <= args.scene < len(slides):
            slide = slides[args.scene]
            console.print(f"\n[bold cyan]Generating scene {args.scene + 1}: {slide.get('type')}[/bold cyan]")
            
            prompt = build_prompt_from_scene(slide, custom_art_style, template_style)
            negative_prompt = build_negative_prompt(custom_art_style, template_style)
            
            console.print(f"Prompt: {prompt[:100]}...")
            
            image_name = generator.generate_and_wait(
                prompt=prompt,
                negative_prompt=negative_prompt,
                model_key=ai_generation.get('model_key'),
                width=int(tech_specs.get('resolution', '1080x1920').split('x')[0]),
                height=int(tech_specs.get('resolution', '1080x1920').split('x')[1]),
                steps=ai_generation.get('steps', 30),
                cfg_scale=ai_generation.get('cfg_scale', 7.5),
                sampler=ai_generation.get('sampler', 'euler_a'),
                max_wait=args.wait
            )
            
            if image_name:
                output_path = generated_dir / f"scene_{args.scene:02d}_{slide.get('type')}.png"
                if generator.download_image(image_name, str(output_path)):
                    console.print(f"[green]✓ Saved to: {output_path}[/green]")
                else:
                    console.print(f"[red]✗ Failed to save image[/red]")
            else:
                console.print(f"[red]✗ Failed to generate image[/red]")
        else:
            console.print(f"[red]Invalid scene index. Must be between 0 and {len(slides)-1}[/red]")
    else:
        # All scenes
        console.print(f"[cyan]Generating {len(slides)} scenes...[/cyan]\n")
        
        for idx, slide in enumerate(slides):
            console.print(f"\n[bold cyan][Scene {idx + 1}/{len(slides)}][/bold cyan]")
            console.print(f"Type: {slide.get('type')}")
            
            prompt = build_prompt_from_scene(slide, custom_art_style, template_style)
            negative_prompt = build_negative_prompt(custom_art_style, template_style)
            
            console.print(f"Prompt preview: {prompt[:100]}...")
            
            image_name = generator.generate_and_wait(
                prompt=prompt,
                negative_prompt=negative_prompt,
                model_key=ai_generation.get('model_key'),
                width=int(tech_specs.get('resolution', '1080x1920').split('x')[0]),
                height=int(tech_specs.get('resolution', '1080x1920').split('x')[1]),
                steps=ai_generation.get('steps', 30),
                cfg_scale=ai_generation.get('cfg_scale', 7.5),
                sampler=ai_generation.get('sampler', 'euler_a'),
                max_wait=args.wait
            )
            
            if image_name:
                output_path = generated_dir / f"scene_{idx:02d}_{slide.get('type')}.png"
                
                if generator.download_image(image_name, str(output_path)):
                    console.print(f"[green]✓ Saved to: {output_path}[/green]")
                else:
                    console.print(f"[red]✗ Failed to save image[/red]")
            else:
                console.print(f"[red]✗ Failed to generate image[/red]")
            
            # Small delay between generations
            time.sleep(2)
        
        console.print(f"\n[bold green]✅ Generation complete! Images saved to: {generated_dir}[/bold green]")


if __name__ == "__main__":
    main()