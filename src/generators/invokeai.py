#!/usr/bin/env python3
"""
InvokeAI generator plugin - refactored from SimpleInvokeAIGenerator
"""

import json
import time
import requests
import uuid
import random
from pathlib import Path
from typing import Dict, Optional, Any
from rich.console import Console

from .base import (
    BaseImageGenerator, 
    GeneratorError,
    GeneratorConnectionError,
    GeneratorTimeoutError,
    retry_with_backoff
)

console = Console()


class InvokeAIGenerator(BaseImageGenerator):
    """InvokeAI generator implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize InvokeAI generator
        
        Args:
            config: Configuration dict with:
                - base_url: InvokeAI server URL (default: http://localhost:9090)
                - default_model: Model key to use
                - board_name: Optional board name for organization
                - max_wait: Maximum wait time in seconds (default: 30)
        """
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:9090')
        self.api_url = f"{self.base_url}/api/v1"
        self.session = requests.Session()
        self.board_id = None
        self.default_model = config.get('default_model')
        self.max_wait = config.get('max_wait', 30)
        
        # Initialize board if specified
        board_name = config.get('board_name')
        if board_name:
            self.board_id = self._get_or_create_board(board_name)
    
    def test_connection(self) -> bool:
        """Test if InvokeAI is accessible"""
        try:
            response = self.session.get(f"{self.api_url}/app/version")
            return response.status_code == 200
        except Exception as e:
            console.print(f"[red]Connection test failed: {e}[/red]")
            return False
    
    @retry_with_backoff(max_retries=3)
    def generate_image(self, 
                      prompt: str, 
                      negative_prompt: str = "",
                      width: int = 1080,
                      height: int = 1920,
                      seed: int = -1,
                      **kwargs) -> Optional[str]:
        """Generate image using InvokeAI
        
        Args:
            prompt: Positive prompt
            negative_prompt: Negative prompt  
            width: Image width
            height: Image height
            seed: Random seed (-1 for random)
            **kwargs: Additional parameters (model_key, steps, cfg_scale, sampler)
            
        Returns:
            Image name/ID if successful, None otherwise
        """
        # Create workflow
        workflow = self._create_text2img_workflow(
            prompt=prompt,
            negative_prompt=negative_prompt,
            model_key=kwargs.get('model_key', self.default_model),
            width=width,
            height=height,
            steps=kwargs.get('steps', 30),
            cfg_scale=kwargs.get('cfg_scale', 7.5),
            sampler=kwargs.get('sampler', 'euler_a'),
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
                raise GeneratorError(f"Failed to enqueue: {response.text}")
                
            result = response.json()
            batch_id = result.get("batch", {}).get("batch_id")
            console.print(f"[yellow]Generation started: {batch_id}[/yellow]")
            
            # Get current images before generation
            before_images = self._get_latest_images(limit=5)
            before_names = {img['image_name'] for img in before_images}
            
            # Wait and check for new image
            with console.status("[cyan]Generating image...[/cyan]") as status:
                for i in range(self.max_wait):
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
                                    if self._add_image_to_board(self.board_id, img['image_name']):
                                        console.print(f"[green]✓ Added to board[/green]")
                                    else:
                                        console.print(f"[yellow]⚠ Failed to add to board[/yellow]")
                                
                                return img['image_name']
                    
                    time.sleep(1)
            
            raise GeneratorTimeoutError(f"No new image found within {self.max_wait}s timeout")
                
        except requests.exceptions.ConnectionError:
            raise GeneratorConnectionError("Failed to connect to InvokeAI server")
        except Exception as e:
            if isinstance(e, (GeneratorError, GeneratorTimeoutError, GeneratorConnectionError)):
                raise
            raise GeneratorError(f"Error generating image: {e}")
    
    def download_image(self, image_id: str, output_path: Path) -> bool:
        """Download image from InvokeAI
        
        Args:
            image_id: InvokeAI image name
            output_path: Where to save the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.api_url}/images/i/{image_id}/full",
                stream=True
            )
            
            if response.status_code == 200:
                # Ensure parent directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
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
    
    def validate_dimensions(self, width: int, height: int) -> tuple[int, int]:
        """Validate dimensions for SDXL models
        
        SDXL works best with specific resolutions to avoid artifacts
        """
        # SDXL recommended resolutions
        sdxl_resolutions = [
            (832, 1248),   # Closest to our 1080x1920 maintaining aspect ratio
            (768, 1344),
            (896, 1152),
            (1024, 1024),
        ]
        
        # Find closest resolution
        target_ratio = height / width
        best_match = sdxl_resolutions[0]
        best_diff = float('inf')
        
        for res_w, res_h in sdxl_resolutions:
            ratio = res_h / res_w
            diff = abs(ratio - target_ratio)
            if diff < best_diff:
                best_diff = diff
                best_match = (res_w, res_h)
        
        if (width, height) != best_match:
            console.print(f"[yellow]Adjusting resolution from {width}x{height} to {best_match[0]}x{best_match[1]} for SDXL[/yellow]")
        
        return best_match
    
    def _get_latest_images(self, limit: int = 1) -> list:
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
    
    def _get_or_create_board(self, board_name: str) -> Optional[str]:
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
    
    def _add_image_to_board(self, board_id: str, image_name: str) -> bool:
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
            "name": "text2img_37degrees",
            "author": "37degrees",
            "description": "Text to image generation",
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