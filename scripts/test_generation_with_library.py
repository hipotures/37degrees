#!/usr/bin/env python3
"""
Test image generation using invokeai-python library
Mimicking our HTTP workflow approach
"""

import asyncio
from invoke import Invoke
from invoke.api import BaseModels, ModelType
import json
import uuid


async def create_text2img_workflow(**params):
    """Create a text2img workflow structure"""
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
                "style": "",  # Empty - we know style presets are text templates
                "original_width": params.get("width", 1080),
                "original_height": params.get("height", 1920),
                "crop_top": 0,
                "crop_left": 0,
                "target_width": params.get("width", 1080),
                "target_height": params.get("height", 1920)
            },
            compel_neg_id: {
                "id": compel_neg_id,
                "type": "sdxl_compel_prompt",
                "position": {"x": 300, "y": 200},
                "prompt": params.get("negative_prompt", ""),
                "style": "",
                "original_width": params.get("width", 1080),
                "original_height": params.get("height", 1920),
                "crop_top": 0,
                "crop_left": 0,
                "target_width": params.get("width", 1080),
                "target_height": params.get("height", 1920)
            },
            noise_id: {
                "id": noise_id,
                "type": "noise",
                "position": {"x": 600, "y": 0},
                "seed": params.get("seed", -1),
                "width": params.get("width", 1080),
                "height": params.get("height", 1920),
                "use_cpu": False
            },
            denoise_id: {
                "id": denoise_id,
                "type": "denoise_latents",
                "position": {"x": 900, "y": 100},
                "steps": params.get("steps", 30),
                "cfg_scale": params.get("cfg_scale", 7.5),
                "denoising_start": 0,
                "denoising_end": 1,
                "scheduler": params.get("sampler", "euler_a"),
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


async def main():
    print("=== Testing Image Generation with Library ===\n")
    
    invoke = Invoke()
    
    try:
        # Connect
        print("Connecting to InvokeAI...")
        version = await invoke.wait_invoke()
        print(f"✓ Connected! Version: {version}\n")
        
        # Test 1: Generate with custom style (no template)
        print("1. Generating image with custom style:")
        
        # Create workflow
        workflow = await create_text2img_workflow(
            prompt="minimalist children's book illustration with naive art approach, style of simple artwork, single red rose, small planet surface, starry background, composition: rose centered on tiny planet, warm, precious mood, vertical composition, clear space in upper third for text overlay, clean lines, flat colors, whimsical",
            negative_prompt="text, letters, words, typography, writing, watermark, signature, logo, photorealistic, 3d render, complex textures, detailed shading, realistic lighting",
            width=1080,
            height=1920,
            steps=30,
            cfg_scale=7.5
        )
        
        # Create batch request
        batch_request = {
            "prepend": False,
            "batch": {
                "graph": workflow,
                "runs": 1,
                "data": []
            }
        }
        
        print("   Enqueueing batch...")
        try:
            result = await invoke.queue.enqueue_batch(batch_request)
            print(f"   ✓ Batch enqueued!")
            print(f"   Batch ID: {result.batch.batch_id}")
            print(f"   Queue ID: {result.batch.queue_id}")
            
            # Wait for completion
            print("\n   Waiting for generation to complete...")
            # Note: The library might have a wait method, but we'll check manually
            
        except Exception as e:
            print(f"   Error: {e}")
            
        # Test 2: Try with a style template (Illustration)
        print("\n2. Testing with Illustration template:")
        
        # With template, we apply it to the prompt ourselves
        template = "Illustration of {prompt}"
        base_prompt = "single red rose on tiny planet with stars"
        full_prompt = template.replace("{prompt}", base_prompt)
        
        print(f"   Template: {template}")
        print(f"   Base prompt: {base_prompt}")
        print(f"   Full prompt: {full_prompt}")
        
        workflow2 = await create_text2img_workflow(
            prompt=full_prompt,
            negative_prompt="text, watermark",
            width=1080,
            height=1920
        )
        
        batch_request2 = {
            "prepend": False,
            "batch": {
                "graph": workflow2,
                "runs": 1,
                "data": []
            }
        }
        
        try:
            result2 = await invoke.queue.enqueue_batch(batch_request2)
            print(f"\n   ✓ Second batch enqueued!")
            print(f"   Batch ID: {result2.batch.batch_id}")
            
        except Exception as e:
            print(f"   Error: {e}")
            
        # Test 3: Check queue status
        print("\n3. Checking queue status:")
        try:
            # List queue items
            queue_items = await invoke.queue.list(limit=5)
            print(f"   Found {len(queue_items.items)} items in queue")
            
            for item in queue_items.items[:2]:
                print(f"   - Status: {item.status}, Created: {item.created_at}")
                
        except Exception as e:
            print(f"   Error checking queue: {e}")
            
        # Close connection
        await invoke.close()
        print("\n✓ Test complete")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())