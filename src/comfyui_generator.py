#!/usr/bin/env python3
"""
ComfyUI integration for generating images from YAML prompts
"""

import json
import yaml
import requests
import time
import base64
from pathlib import Path
from typing import Dict, Any
import websocket
import uuid


class ComfyUIGenerator:
    """Generate images using ComfyUI API"""
    
    def __init__(self, server_address: str = "127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        
    def load_workflow_template(self, template_path: str) -> Dict:
        """Load ComfyUI workflow template"""
        with open(template_path, 'r') as f:
            return json.load(f)
    
    def build_prompt_text(self, prompt_data: Dict) -> str:
        """Convert our YAML prompt to text for ComfyUI"""
        art_style = prompt_data['scene_generation']['art_style']
        scene = prompt_data['scene_generation']['scene_details']
        instructions = prompt_data['scene_generation']['generation_instructions']
        
        # Build comprehensive prompt
        prompt_parts = [
            # Style directives
            art_style['primary_style'],
            art_style['complexity'],
            f"Style: {art_style['overall_feeling']}",
            f"Color technique: {art_style['color_technique']}",
            
            # Scene elements
            f"Scene contains: {', '.join(scene['elements'])}",
            f"Composition: {scene['composition']}",
            f"Atmosphere: {scene['atmosphere']}",
            f"Background: {scene['background']}",
            
            # Technical requirements
            f"Aspect ratio: {art_style['aspect_ratio']}",
            instructions['text_space'],
            instructions['style_emphasis'],
            
            # What to emphasize
            f"Emphasize: {art_style['emphasize']}"
        ]
        
        # Negative prompt
        negative_parts = [
            art_style['avoid'],
            instructions['no_text'],
            "photorealistic, complex textures, detailed shading",
            "text, letters, words, typography"
        ]
        
        return {
            "positive": ", ".join(prompt_parts),
            "negative": ", ".join(negative_parts)
        }
    
    def update_workflow(self, workflow: Dict, prompt_yaml_path: str) -> Dict:
        """Update workflow with our prompt"""
        # Load YAML prompt
        with open(prompt_yaml_path, 'r') as f:
            prompt_data = yaml.safe_load(f)
        
        # Build prompt text
        prompts = self.build_prompt_text(prompt_data)
        
        # Update workflow nodes (adjust based on your workflow)
        # Typical nodes:
        # "6" = CLIP Text Encode (Positive)
        # "7" = CLIP Text Encode (Negative)
        # "5" = Empty Latent Image
        
        if "6" in workflow:
            workflow["6"]["inputs"]["text"] = prompts["positive"]
            
        if "7" in workflow:
            workflow["7"]["inputs"]["text"] = prompts["negative"]
            
        # Set resolution
        if "5" in workflow:
            workflow["5"]["inputs"]["width"] = 1080
            workflow["5"]["inputs"]["height"] = 1920
            
        return workflow
    
    def queue_prompt(self, workflow: Dict) -> str:
        """Queue prompt and return prompt_id"""
        p = {"prompt": workflow, "client_id": self.client_id}
        response = requests.post(f"http://{self.server_address}/prompt", json=p)
        return response.json()['prompt_id']
    
    def get_image(self, filename: str, subfolder: str, folder_type: str) -> bytes:
        """Retrieve generated image"""
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url = f"http://{self.server_address}/view"
        response = requests.get(url, params=data)
        return response.content
    
    def wait_for_completion(self, prompt_id: str, timeout: int = 120) -> Dict:
        """Wait for image generation to complete"""
        ws = websocket.WebSocket()
        ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executed':
                    if message['data']['node'] is None and message['data']['prompt_id'] == prompt_id:
                        # Generation complete
                        break
        
        ws.close()
        
        # Get history to find output images
        response = requests.get(f"http://{self.server_address}/history/{prompt_id}")
        return response.json()
    
    def generate_image(self, prompt_yaml_path: str, workflow_path: str, output_path: str):
        """Generate image from YAML prompt"""
        print(f"Generating image from: {prompt_yaml_path}")
        
        # Load and update workflow
        workflow = self.load_workflow_template(workflow_path)
        workflow = self.update_workflow(workflow, prompt_yaml_path)
        
        # Queue generation
        prompt_id = self.queue_prompt(workflow)
        print(f"Queued with ID: {prompt_id}")
        
        # Wait for completion
        history = self.wait_for_completion(prompt_id)
        
        # Find and save output image
        if prompt_id in history:
            outputs = history[prompt_id]['outputs']
            for node_id, node_output in outputs.items():
                if 'images' in node_output:
                    for image in node_output['images']:
                        image_data = self.get_image(
                            image['filename'], 
                            image['subfolder'], 
                            image['type']
                        )
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        print(f"Saved to: {output_path}")
                        return
        
        print("No image found in output!")


def main():
    """Generate all scenes for any book"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python comfyui_generator.py <book_yaml_path>")
        sys.exit(1)
    
    book_yaml_path = Path(sys.argv[1])
    book_dir = book_yaml_path.parent
    
    generator = ComfyUIGenerator()
    
    # You need to save a workflow from ComfyUI first!
    workflow_path = "comfyui_workflow.json"
    
    prompts_dir = book_dir / "prompts"
    output_dir = book_dir / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for prompt_file in sorted(prompts_dir.glob("scene_*.yaml")):
        scene_num = prompt_file.stem.split('_')[1]
        output_path = output_dir / f"scene_{scene_num}.png"
        
        try:
            generator.generate_image(
                prompt_file,
                workflow_path,
                output_path
            )
            time.sleep(2)  # Be nice to the GPU
        except Exception as e:
            print(f"Error generating {prompt_file}: {e}")


if __name__ == "__main__":
    main()