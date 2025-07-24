#!/usr/bin/env python3
"""
ComfyUI generator plugin - refactored from ComfyUIGenerator
"""

import json
import time
import requests
import websocket
import uuid
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


class ComfyUIGenerator(BaseImageGenerator):
    """ComfyUI generator implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize ComfyUI generator
        
        Args:
            config: Configuration dict with:
                - server_address: ComfyUI server address (default: 127.0.0.1:8188)
                - workflow_template: Path to workflow JSON template
                - timeout: Generation timeout in seconds (default: 120)
        """
        super().__init__(config)
        self.server_address = config.get('server_address', '127.0.0.1:8188')
        self.client_id = str(uuid.uuid4())
        self.workflow_template = config.get('workflow_template')
        self.timeout = config.get('timeout', 120)
        
        # Load workflow template if provided
        self._workflow = None
        if self.workflow_template:
            self._load_workflow_template()
    
    def test_connection(self) -> bool:
        """Test if ComfyUI server is accessible"""
        try:
            response = requests.get(f"http://{self.server_address}/system_stats")
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
        """Generate image using ComfyUI
        
        Args:
            prompt: Positive prompt
            negative_prompt: Negative prompt
            width: Image width
            height: Image height
            seed: Random seed (-1 for random)
            **kwargs: Additional parameters (workflow_override, etc.)
            
        Returns:
            Prompt ID if successful, None otherwise
        """
        # Use provided workflow or default template
        workflow = kwargs.get('workflow_override') or self._workflow
        if not workflow:
            raise GeneratorError("No workflow template provided")
        
        # Update workflow with prompts and settings
        workflow = self._update_workflow(
            workflow,
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            seed=seed,
            **kwargs
        )
        
        # Queue the prompt
        try:
            prompt_id = self._queue_prompt(workflow)
            console.print(f"[yellow]Queued generation: {prompt_id}[/yellow]")
            
            # Wait for completion
            result = self._wait_for_completion(prompt_id)
            
            if result:
                console.print(f"[green]✓ Generation complete: {prompt_id}[/green]")
                return prompt_id
            else:
                raise GeneratorTimeoutError(f"Generation timed out after {self.timeout}s")
                
        except requests.exceptions.ConnectionError:
            raise GeneratorConnectionError("Failed to connect to ComfyUI server")
        except Exception as e:
            if isinstance(e, (GeneratorError, GeneratorTimeoutError, GeneratorConnectionError)):
                raise
            raise GeneratorError(f"Error generating image: {e}")
    
    def download_image(self, image_id: str, output_path: Path) -> bool:
        """Download generated image from ComfyUI
        
        Args:
            image_id: Prompt ID from generation
            output_path: Where to save the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get generation history
            response = requests.get(f"http://{self.server_address}/history/{image_id}")
            if response.status_code != 200:
                console.print(f"[red]Failed to get history for {image_id}[/red]")
                return False
            
            history = response.json()
            
            # Find output images
            if image_id in history:
                outputs = history[image_id]['outputs']
                for node_id, node_output in outputs.items():
                    if 'images' in node_output:
                        # Get first image
                        image = node_output['images'][0]
                        image_data = self._get_image(
                            image['filename'],
                            image['subfolder'],
                            image['type']
                        )
                        
                        # Ensure parent directory exists
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Save image
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        
                        console.print(f"[green]✓ Saved to: {output_path}[/green]")
                        return True
            
            console.print(f"[red]No images found for prompt {image_id}[/red]")
            return False
            
        except Exception as e:
            console.print(f"[red]Error downloading image: {e}[/red]")
            return False
    
    def _load_workflow_template(self) -> None:
        """Load workflow template from file"""
        try:
            template_path = Path(self.workflow_template)
            if template_path.exists():
                with open(template_path, 'r') as f:
                    self._workflow = json.load(f)
                console.print(f"[green]Loaded workflow template: {template_path}[/green]")
            else:
                console.print(f"[yellow]Workflow template not found: {template_path}[/yellow]")
        except Exception as e:
            console.print(f"[red]Error loading workflow template: {e}[/red]")
    
    def _update_workflow(self, workflow: Dict, **params) -> Dict:
        """Update workflow with generation parameters
        
        This method needs to be customized based on your workflow structure
        """
        # Deep copy workflow to avoid modifying original
        import copy
        workflow = copy.deepcopy(workflow)
        
        # Common node IDs (adjust based on your workflow)
        # "6" = CLIP Text Encode (Positive)
        # "7" = CLIP Text Encode (Negative)  
        # "5" = Empty Latent Image
        # "3" = KSampler
        
        # Update positive prompt
        if "6" in workflow:
            workflow["6"]["inputs"]["text"] = params.get('prompt', '')
        
        # Update negative prompt
        if "7" in workflow:
            workflow["7"]["inputs"]["text"] = params.get('negative_prompt', '')
        
        # Update resolution
        if "5" in workflow:
            workflow["5"]["inputs"]["width"] = params.get('width', 1080)
            workflow["5"]["inputs"]["height"] = params.get('height', 1920)
        
        # Update seed if specified
        if "3" in workflow and params.get('seed', -1) != -1:
            workflow["3"]["inputs"]["seed"] = params['seed']
        
        # Additional parameters
        if "3" in workflow:
            if 'steps' in params:
                workflow["3"]["inputs"]["steps"] = params['steps']
            if 'cfg_scale' in params:
                workflow["3"]["inputs"]["cfg"] = params['cfg_scale']
            if 'sampler' in params:
                workflow["3"]["inputs"]["sampler_name"] = params['sampler']
        
        return workflow
    
    def _queue_prompt(self, workflow: Dict) -> str:
        """Queue prompt and return prompt_id"""
        p = {"prompt": workflow, "client_id": self.client_id}
        response = requests.post(f"http://{self.server_address}/prompt", json=p)
        
        if response.status_code != 200:
            raise GeneratorError(f"Failed to queue prompt: {response.text}")
        
        return response.json()['prompt_id']
    
    def _wait_for_completion(self, prompt_id: str) -> bool:
        """Wait for image generation to complete using WebSocket"""
        ws = websocket.WebSocket()
        try:
            ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")
            
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                out = ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    if message['type'] == 'executed':
                        if message['data']['node'] is None and message['data']['prompt_id'] == prompt_id:
                            # Generation complete
                            return True
                    elif message['type'] == 'execution_error':
                        if message['data']['prompt_id'] == prompt_id:
                            error_msg = message['data'].get('exception_message', 'Unknown error')
                            raise GeneratorError(f"Execution error: {error_msg}")
            
            return False
            
        finally:
            ws.close()
    
    def _get_image(self, filename: str, subfolder: str, folder_type: str) -> bytes:
        """Retrieve generated image data"""
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url = f"http://{self.server_address}/view"
        response = requests.get(url, params=data)
        
        if response.status_code != 200:
            raise GeneratorError(f"Failed to get image: {response.status_code}")
        
        return response.content
    
    def get_info(self) -> Dict[str, Any]:
        """Get generator information"""
        info = super().get_info()
        info.update({
            'server_address': self.server_address,
            'workflow_template': self.workflow_template,
            'has_workflow': self._workflow is not None
        })
        return info