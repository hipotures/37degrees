#!/usr/bin/env python3
"""
Test accessing style presets through invokeai-python library
Using the internal API methods we discovered
"""

import asyncio
from invoke import Invoke
import json


async def main():
    print("=== Testing Style Presets Access ===\n")
    
    invoke = Invoke()
    
    try:
        # Connect
        print("Connecting to InvokeAI...")
        version = await invoke.wait_invoke()
        print(f"✓ Connected! Version: {version}\n")
        
        # We found that the library has get_async method on various API objects
        # Let's try to use it to access the style_presets endpoint
        
        print("1. Trying to access style_presets endpoint:")
        try:
            # The app object has get_async method
            result = await invoke.app.get_async("/style_presets/", version=1)
            print(f"   ✓ Success! Got {len(result)} style presets")
            
            # Show first few presets
            print("\n   Available style presets:")
            for preset in result[:5]:
                print(f"   - {preset['name']}")
                if 'preset_data' in preset:
                    data = preset['preset_data']
                    if 'positive_prompt' in data:
                        print(f"     Positive: {data['positive_prompt'][:100]}...")
                    if 'negative_prompt' in data:
                        print(f"     Negative: {data['negative_prompt'][:80]}...")
                print()
                
        except Exception as e:
            print(f"   Error: {e}")
            
        # 2. Try to get a specific style preset
        print("\n2. Looking for 'Illustration' style preset:")
        try:
            result = await invoke.app.get_async("/style_presets/", version=1)
            
            # Find Illustration preset
            illustration_preset = None
            for preset in result:
                if preset['name'] == 'Illustration':
                    illustration_preset = preset
                    break
                    
            if illustration_preset:
                print("   ✓ Found 'Illustration' preset!")
                data = illustration_preset.get('preset_data', {})
                print(f"   ID: {illustration_preset.get('id')}")
                print(f"   Positive prompt: {data.get('positive_prompt', 'N/A')}")
                print(f"   Negative prompt: {data.get('negative_prompt', 'N/A')}")
            else:
                print("   ✗ 'Illustration' preset not found")
                
        except Exception as e:
            print(f"   Error: {e}")
            
        # 3. Test creating a workflow with style preset
        print("\n3. Testing workflow generation with the library:")
        
        # Check if there's a workflow or generation functionality
        if hasattr(invoke, 'queue'):
            print("   Found queue interface")
            
            # The queue API should have enqueue_batch like our HTTP implementation
            try:
                # First, let's see what methods are available
                queue_methods = [m for m in dir(invoke.queue) if not m.startswith('_') and callable(getattr(invoke.queue, m))]
                print(f"   Available queue methods: {', '.join(queue_methods[:5])}...")
                
                # Check if we can enqueue a batch
                if hasattr(invoke.queue, 'enqueue_batch'):
                    print("   ✓ Found enqueue_batch method!")
                    
                    # Try to inspect the method signature
                    import inspect
                    sig = inspect.signature(invoke.queue.enqueue_batch)
                    print(f"   Method signature: enqueue_batch{sig}")
                    
            except Exception as e:
                print(f"   Error exploring queue: {e}")
                
        # 4. Alternative: Use the models API to generate
        print("\n4. Checking for generation through models API:")
        if hasattr(invoke, 'models'):
            print("   Models API is available")
            models = await invoke.models.list()
            if models:
                print(f"   Found {len(models)} models")
                
        # Close connection
        await invoke.close()
        print("\n✓ Test complete")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())