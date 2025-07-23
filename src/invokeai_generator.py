#!/usr/bin/env python3
"""
InvokeAI Image Generator for 37degrees project
Generates images using InvokeAI API based on scene prompts
"""

import os
import json
import time
import requests
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import uuid
from datetime import datetime


class InvokeAIGenerator:
    def __init__(self, base_url: str = "http://localhost:9090"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()
        
    def test_connection(self) -> bool:
        """Test if InvokeAI is accessible"""
        try:
            response = self.session.get(f"{self.api_url}/app/version")
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def generate_image(self, 
                      prompt: str,
                      negative_prompt: str = "",
                      model_key: str = None,
                      width: int = 1080,
                      height: int = 1920,
                      steps: int = 30,
                      cfg_scale: float = 7.5,
                      sampler: str = "euler_a",
                      seed: int = -1) -> Optional[Dict]:
        """Generate a single image using InvokeAI API v1"""
        
        # Create a workflow for text2img
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
        
        # Debug: print the request
        request_data = {
            "prepend": False,
            "batch": {
                "graph": workflow,
                "runs": 1,
                "data": []
            }
        }
        
        print("\n=== REQUEST DATA ===")
        print(json.dumps(request_data, indent=2)[:2000] + "...")
        print("===================\n")
        
        try:
            # Queue the workflow using batch endpoint
            response = self.session.post(
                f"{self.api_url}/queue/default/enqueue_batch",
                json=request_data
            )
            
            if response.status_code != 200:
                print(f"Failed to enqueue workflow: {response.text}")
                return None
                
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)[:500]}...")
            
            # Extract session ID from batch response
            if "batch" in result:
                batch_id = result["batch"]["batch_id"]
                print(f"Batch enqueued: {batch_id}")
                # For batch, we need to wait for the batch to process
                return self._wait_for_batch(batch_id)
            else:
                print(f"Unexpected response format: {result.keys()}")
                return None
                
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    def _create_text2img_workflow(self, **params) -> Dict:
        """Create a text2img workflow for InvokeAI v6"""
        # Generate unique IDs for nodes
        model_id = str(uuid.uuid4())
        compel_pos_id = str(uuid.uuid4())
        compel_neg_id = str(uuid.uuid4())
        noise_id = str(uuid.uuid4())
        denoise_id = str(uuid.uuid4())
        l2i_id = str(uuid.uuid4())
        image_id = str(uuid.uuid4())
        
        workflow = {
            "name": "text2img",
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
                        "key": params.get("model_key", "c81f2f9b-cabd-40ec-b6f4-d3172c10bafc"),
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
                    "seed": params.get("seed", -1),
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
                },
                image_id: {
                    "id": image_id,
                    "type": "image",
                    "position": {"x": 1500, "y": 100},
                    "is_intermediate": False,
                    "use_cache": False
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
                {
                    "id": str(uuid.uuid4()),
                    "source": {"node_id": l2i_id, "field": "image"},
                    "destination": {"node_id": image_id, "field": "image"}
                }
            ]
        }
        
        return workflow
    
    def _wait_for_batch(self, batch_id: str, timeout: int = 300) -> Optional[Dict]:
        """Wait for batch to complete and return the result"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check batch status - get newest items first, sorted by created_at desc
                response = self.session.get(
                    f"{self.api_url}/queue/default/list?limit=50&order_by=created_at&order_dir=desc"
                )
                
                if response.status_code == 200:
                    queue_data = response.json()
                    items = queue_data.get("items", [])
                    
                    # Find items for our batch
                    batch_items = [item for item in items if item.get("batch_id") == batch_id]
                    
                    if batch_items:
                        item = batch_items[0]
                        status = item.get("status")
                        print(f"Status: {status}")
                        
                        if status == "completed":
                            session_id = item.get("session_id")
                            print(f"Session completed: {session_id}")
                            return self._get_session_output(session_id)
                        elif status in ["failed", "canceled"]:
                            print(f"Batch item {status}: {item.get('error_message')}")
                            print(f"Error type: {item.get('error_type')}")
                            print(f"Traceback: {item.get('error_traceback')[:500]}")
                            return None
                    else:
                        print(f"Waiting for batch {batch_id}...")
                
            except Exception as e:
                print(f"Error checking batch status: {e}")
            
            time.sleep(2)
        
        print(f"Timeout waiting for batch {batch_id}")
        return None
    
    def get_style_presets(self) -> Dict[str, Dict]:
        """Get available style presets from InvokeAI"""
        try:
            response = self.session.get(f"{self.api_url}/style_presets/")
            if response.status_code == 200:
                presets = {}
                for preset in response.json():
                    presets[preset['name']] = preset['preset_data']
                return presets
            else:
                print(f"Failed to get style presets: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Error getting style presets: {e}")
            return {}
    
    def _get_session_output(self, session_id: str) -> Optional[Dict]:
        """Get output from completed session"""
        try:
            # Get the queue item details which contains the results
            response = self.session.get(
                f"{self.api_url}/queue/default/list?session_id={session_id}&limit=1"
            )
            
            if response.status_code == 200:
                queue_data = response.json()
                items = queue_data.get("items", [])
                print(f"DEBUG: Got {len(items)} items for session {session_id}")
                
                if items:
                    item = items[0]
                    # Check in session.results
                    session = item.get("session", {})
                    results = session.get("results", {})
                    
                    # Debug - print session info
                    print(f"Session ID from queue: {session_id}")
                    print(f"Session data keys: {list(session.keys())[:10]}")
                    
                    # Find image output in results
                    image_found = None
                    for node_id, result in results.items():
                        if isinstance(result, dict) and result.get("type") == "image_output":
                            image_data = result.get("image", {})
                            image_name = image_data.get("image_name")
                            if image_name:
                                print(f"Found image in node {node_id}: {image_name}")
                                image_found = image_name
                                # Don't return immediately - check all nodes
                    
                    if image_found:
                        # Try to get the actual latest image from the session
                        # Since API returns old images, we'll generate a unique name
                        import uuid
                        unique_suffix = str(uuid.uuid4())[:8]
                        print(f"Warning: API returning cached image. Session: {session_id}")
                        return {"image_name": image_found, "session_id": session_id}
                
                print("No image output found in session results")
            else:
                print(f"Failed to get session data: {response.status_code}")
            
            return None
            
        except Exception as e:
            print(f"Error getting session output: {e}")
            return None
    
    def _wait_for_completion(self, session_id: str, timeout: int = 300) -> Optional[Dict]:
        """Wait for session to complete and return the result"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check session status
                response = self.session.get(
                    f"{self.api_url}/sessions/{session_id}"
                )
                
                if response.status_code == 200:
                    session_data = response.json()
                    status = session_data.get("status")
                    
                    if status == "completed":
                        # Get the output image
                        outputs = session_data.get("outputs", {})
                        for node_id, output in outputs.items():
                            if output.get("type") == "image_output":
                                image_name = output.get("image", {}).get("image_name")
                                if image_name:
                                    return {"image_name": image_name, "session_id": session_id}
                        
                    elif status in ["failed", "canceled"]:
                        print(f"Session {status}: {session_data.get('error')}")
                        return None
                
            except Exception as e:
                print(f"Error checking session status: {e}")
            
            time.sleep(2)
        
        print(f"Timeout waiting for session {session_id}")
        return None
    
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
                print(f"Failed to download image: {response.status_code}")
                return False
            
        except Exception as e:
            print(f"Error downloading image: {e}")
            return False


class SceneImageGenerator:
    def __init__(self, book_path: str):
        self.book_path = Path(book_path)
        self.book_dir = self.book_path.parent
        self.generator = InvokeAIGenerator()
        
        # Load book configuration
        with open(self.book_path, 'r', encoding='utf-8') as f:
            self.book_data = yaml.safe_load(f)
        
        # Create output directories
        self.generated_dir = self.book_dir / "generated"
        self.generated_dir.mkdir(exist_ok=True)
        
    def generate_all_scenes(self):
        """Generate images for all scenes in the book"""
        if not self.generator.test_connection():
            print("Failed to connect to InvokeAI. Make sure it's running on http://localhost:9090")
            return
        
        custom_art_style = self.book_data.get('custom_art_style', {})
        template_art_style = self.book_data.get('template_art_style', '')
        ai_generation = self.book_data.get('ai_generation', {})
        tech_specs = self.book_data.get('technical_specs', {})
        slides = self.book_data.get('slides', [])
        
        # Get model configuration from ai_generation section
        model_key = ai_generation.get('model_key')
        if not model_key:
            print("No model_key specified in ai_generation. Using default model.")
            model_key = "c81f2f9b-cabd-40ec-b6f4-d3172c10bafc"  # Dreamshaper XL
        
        # Check if we should use a template style
        template_style = None
        if template_art_style and template_art_style not in ['', '-']:
            # Get available style presets
            style_presets = self.generator.get_style_presets()
            if template_art_style in style_presets:
                template_style = style_presets[template_art_style]
                print(f"Using style template: {template_art_style}")
            else:
                print(f"Warning: Template '{template_art_style}' not found. Available templates:")
                print(", ".join(sorted(style_presets.keys())))
                print("Using custom_art_style instead.")
        else:
            print("Using custom art style")
            
        print(f"Using model: {ai_generation.get('model_name', 'default')}")
        print(f"Generating {len(slides)} scenes...\n")
        
        for idx, slide in enumerate(slides):
            print(f"\n[Scene {idx + 1}/{len(slides)}]")
            print(f"Type: {slide.get('type')}")
            
            # Build the prompt from scene description
            prompt = self._build_prompt_from_scene(slide, custom_art_style, template_style)
            negative_prompt = self._build_negative_prompt(custom_art_style, template_style)
            
            print(f"Prompt preview: {prompt[:150]}...")
            
            # Generate the image
            result = self.generator.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                model_key=model_key,
                width=int(tech_specs.get('resolution', '1080x1920').split('x')[0]),
                height=int(tech_specs.get('resolution', '1080x1920').split('x')[1]),
                steps=ai_generation.get('steps', 30),
                cfg_scale=ai_generation.get('cfg_scale', 7.5),
                sampler=ai_generation.get('sampler', 'euler_a')
            )
            
            if result:
                # Download the generated image
                image_name = result.get('image_name')
                output_path = self.generated_dir / f"scene_{idx:02d}_{slide.get('type')}.png"
                
                if self.generator.download_image(image_name, str(output_path)):
                    print(f"✓ Saved to: {output_path}")
                else:
                    print(f"✗ Failed to download image")
            else:
                print(f"✗ Failed to generate image")
            
            # Small delay between generations
            time.sleep(2)
        
        print(f"\n✅ Generation complete! Images saved to: {self.generated_dir}")
    
    def generate_single_scene(self, scene_index: int):
        """Generate a single scene by index"""
        if not self.generator.test_connection():
            print("Failed to connect to InvokeAI.")
            return
        
        custom_art_style = self.book_data.get('custom_art_style', {})
        template_art_style = self.book_data.get('template_art_style', '')
        slides = self.book_data.get('slides', [])
        
        if scene_index < 0 or scene_index >= len(slides):
            print(f"Invalid scene index. Must be between 0 and {len(slides)-1}")
            return
        
        slide = slides[scene_index]
        ai_generation = self.book_data.get('ai_generation', {})
        model_key = ai_generation.get('model_key', "c81f2f9b-cabd-40ec-b6f4-d3172c10bafc")
        
        print(f"Generating scene {scene_index + 1}: {slide.get('type')}")
        
        # Get resolution
        tech_specs = self.book_data.get('technical_specs', {})
        resolution = tech_specs.get('resolution', '1080x1920')
        width = int(resolution.split('x')[0])
        height = int(resolution.split('x')[1])
        
        print(f"Resolution: {width}x{height}")
        print(f"Model: {ai_generation.get('model_name', 'Dreamshaper XL')}")
        
        # Check if we should use a template style
        template_style = None
        if template_art_style and template_art_style not in ['', '-']:
            style_presets = self.generator.get_style_presets()
            if template_art_style in style_presets:
                template_style = style_presets[template_art_style]
                print(f"Using style template: {template_art_style}")
            else:
                print(f"Warning: Template '{template_art_style}' not found.")
                print("Using custom_art_style instead.")
        
        prompt = self._build_prompt_from_scene(slide, custom_art_style, template_style)
        negative_prompt = self._build_negative_prompt(custom_art_style, template_style)
        
        print(f"Full prompt: {prompt}")
        print(f"Negative: {negative_prompt}")
        
        result = self.generator.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            model_key=model_key,
            width=int(art_style.get('resolution', '1080x1920').split('x')[0]),
            height=int(art_style.get('resolution', '1080x1920').split('x')[1]),
            steps=ai_generation.get('steps', 30),
            cfg_scale=ai_generation.get('cfg_scale', 7.5),
            sampler=ai_generation.get('sampler', 'euler_a')
        )
        
        if result:
            image_name = result.get('image_name')
            output_path = self.generated_dir / f"scene_{scene_index:02d}_{slide.get('type')}.png"
            
            if self.generator.download_image(image_name, str(output_path)):
                print(f"✓ Image saved to: {output_path}")
                return str(output_path)
            else:
                print(f"✗ Failed to download image")
        else:
            print(f"✗ Failed to generate image")
        
        return None
    
    def _build_prompt_from_scene(self, slide: Dict, custom_art_style: Dict, template_style: Optional[Dict] = None) -> str:
        """Build a complete prompt from scene and style information"""
        scene = slide.get('scene', {})
        
        # Start with the style directive
        if template_style:
            # Use template style - {prompt} will be replaced with our scene
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
        
        # Add color information
        color_palette = art_style.get('color_palette', {})
        if color_palette.get('base'):
            colors = ", ".join(color_palette['base'][:3])
            scene_prompt.append(f"color palette: {colors}")
        
        # Add background
        if scene.get('background'):
            scene_prompt.append(f"background: {scene['background']}")
        
        # Add technical specs
        # Only add custom style specs if not using template
        if not template_style:
            scene_prompt.extend([
                "vertical composition",
                "clear space in upper third for text overlay",
                custom_art_style.get('line_work', 'clean lines'),
                custom_art_style.get('color_technique', 'flat colors'),
                custom_art_style.get('overall_feeling', 'whimsical')
            ])
        
        # Build final prompt
        if template_style:
            # Replace {prompt} placeholder with our scene
            final_prompt = base_prompt.replace('{prompt}', ", ".join(scene_prompt))
        else:
            final_prompt = ", ".join(scene_prompt)
            
        return final_prompt
    
    def _build_negative_prompt(self, custom_art_style: Dict, template_style: Optional[Dict] = None) -> str:
        """Build negative prompt from style configuration"""
        if template_style:
            # Use template negative prompt if available
            return template_style.get('negative_prompt', 'text, watermark')
        else:
            # Use custom negative prompt
            negative_parts = [
                "text", "letters", "words", "typography", "writing",
                "watermark", "signature", "logo"
            ]
            
            # Add style-specific negatives
            avoid = custom_art_style.get('avoid', '')
            if avoid:
                negative_parts.append(avoid)
            
            # Add default negatives for our use case
            negative_parts.extend([
                "photorealistic", "3d render", "complex textures",
                "detailed shading", "realistic lighting",
                "ugly", "deformed", "noisy", "blurry"
            ])
            
            return ", ".join(negative_parts)


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate images for 37degrees book scenes")
    parser.add_argument('book_yaml', nargs='?', help="Path to book YAML file")
    parser.add_argument('--test', action='store_true', help="Test connection only")
    parser.add_argument('--scene', type=int, help="Generate only specific scene (0-based index)")
    
    args = parser.parse_args()
    
    if args.test:
        generator = InvokeAIGenerator()
        if generator.test_connection():
            print("✓ Successfully connected to InvokeAI")
        else:
            print("✗ Failed to connect to InvokeAI")
        return
    
    if not args.book_yaml:
        parser.error("book_yaml is required unless --test is specified")
    
    # Generate images for the book
    scene_generator = SceneImageGenerator(args.book_yaml)
    
    if args.scene is not None:
        scene_generator.generate_single_scene(args.scene)
    else:
        scene_generator.generate_all_scenes()


if __name__ == "__main__":
    main()