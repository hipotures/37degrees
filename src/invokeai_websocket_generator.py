#!/usr/bin/env python3
"""
InvokeAI WebSocket Generator - uses WebSocket to track generation progress
Just like the WebUI does
"""

import json
import time
import requests
import yaml
import asyncio
import socketio
from pathlib import Path
from typing import Dict, Optional
import uuid
import random
from rich.console import Console

console = Console()


class WebSocketInvokeAIGenerator:
    def __init__(self, base_url: str = "http://localhost:9090"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.sio = socketio.AsyncClient()
        self.current_session_id = None
        self.generation_complete = False
        self.generated_image = None
        
    def test_connection(self) -> bool:
        """Test if InvokeAI is accessible"""
        try:
            response = self.session.get(f"{self.api_url}/app/version")
            return response.status_code == 200
        except Exception as e:
            console.print(f"[red]Connection test failed: {e}[/red]")
            return False
    
    async def connect_websocket(self):
        """Connect to InvokeAI WebSocket"""
        @self.sio.on('connect')
        async def on_connect():
            console.print("[green]Connected to WebSocket[/green]")
        
        @self.sio.on('disconnect')
        async def on_disconnect():
            console.print("[yellow]Disconnected from WebSocket[/yellow]")
        
        @self.sio.on('invocation_complete')
        async def on_invocation_complete(data):
            """Handle invocation completion"""
            if data.get('invocation_source_id') == self.current_session_id:
                # Check if this is the final image output
                result = data.get('result', {})
                if result.get('type') == 'image_output':
                    image_data = result.get('image', {})
                    self.generated_image = image_data.get('image_name')
                    console.print(f"[green]✓ Image ready: {self.generated_image}[/green]")
                    self.generation_complete = True
        
        @self.sio.on('invocation_started')
        async def on_invocation_started(data):
            """Handle invocation start"""
            if data.get('invocation_source_id') == self.current_session_id:
                console.print(f"[cyan]Processing: {data.get('invocation', {}).get('type')}[/cyan]")
        
        # Connect to WebSocket
        await self.sio.connect(f"{self.base_url}/ws/socket.io/")
        
    async def generate_image_async(self, prompt: str, negative_prompt: str = "", 
                                  model_key: str = None, width: int = 1080, 
                                  height: int = 1920, steps: int = 30, 
                                  cfg_scale: float = 7.5, sampler: str = "euler_a", 
                                  seed: int = -1) -> Optional[str]:
        """Generate image using WebSocket for progress tracking"""
        
        # Reset state
        self.generation_complete = False
        self.generated_image = None
        
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
        
        # Get session ID from workflow
        self.current_session_id = workflow['id']
        
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
            console.print(f"[yellow]Batch submitted: {batch_id}[/yellow]")
            
            # Wait for completion via WebSocket
            timeout = 60
            start_time = time.time()
            
            while not self.generation_complete and time.time() - start_time < timeout:
                await asyncio.sleep(0.5)
            
            if self.generation_complete:
                return self.generated_image
            else:
                console.print("[red]✗ Timeout waiting for generation[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]Error generating image: {e}[/red]")
            return None
    
    def generate_image(self, **kwargs) -> Optional[str]:
        """Synchronous wrapper for async generation"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Connect and generate
            loop.run_until_complete(self.connect_websocket())
            result = loop.run_until_complete(self.generate_image_async(**kwargs))
            return result
        finally:
            loop.run_until_complete(self.sio.disconnect())
            loop.close()
    
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
            "name": "websocket_text2img",
            "author": "37degrees",
            "description": "Text to image with WebSocket tracking",
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


def main():
    """Test WebSocket generator"""
    generator = WebSocketInvokeAIGenerator()
    
    if not generator.test_connection():
        console.print("[red]Failed to connect to InvokeAI[/red]")
        return
    
    console.print("[cyan]Testing WebSocket image generation...[/cyan]")
    
    image_name = generator.generate_image(
        prompt="a beautiful sunset over mountains, digital art",
        negative_prompt="text, watermark",
        steps=20
    )
    
    if image_name:
        console.print(f"[green]✓ Generated image: {image_name}[/green]")
        
        # Download it
        if generator.download_image(image_name, "test_websocket.png"):
            console.print("[green]✓ Downloaded to test_websocket.png[/green]")
    else:
        console.print("[red]✗ Failed to generate image[/red]")


if __name__ == "__main__":
    main()