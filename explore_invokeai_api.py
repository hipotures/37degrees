#!/usr/bin/env python3
"""
Deep exploration of invokeai-python library API
Looking for style presets and generation methods
"""

import asyncio
from invoke import Invoke
from invoke.api import BaseModels, ModelType
import json
import inspect


async def explore_object(obj, name="object", max_depth=2, current_depth=0):
    """Recursively explore an object's attributes and methods"""
    if current_depth >= max_depth:
        return
    
    print(f"\n{'  ' * current_depth}=== Exploring {name} ===")
    
    # Get all non-private attributes
    attrs = [attr for attr in dir(obj) if not attr.startswith('_')]
    
    for attr in attrs:
        try:
            value = getattr(obj, attr)
            attr_type = type(value).__name__
            
            # Skip certain types to avoid clutter
            if attr_type in ['method', 'function', 'coroutine']:
                # Show method signature if possible
                try:
                    sig = inspect.signature(value)
                    print(f"{'  ' * current_depth}- {attr}({sig}): {attr_type}")
                except:
                    print(f"{'  ' * current_depth}- {attr}(): {attr_type}")
            elif attr_type in ['str', 'int', 'float', 'bool', 'NoneType']:
                print(f"{'  ' * current_depth}- {attr}: {attr_type} = {value}")
            else:
                print(f"{'  ' * current_depth}- {attr}: {attr_type}")
                
                # Explore nested objects (but not too deep)
                if current_depth < max_depth - 1 and attr_type not in ['module', 'type']:
                    if hasattr(value, '__dict__') or hasattr(value, '__dir__'):
                        await explore_object(value, f"{name}.{attr}", max_depth, current_depth + 1)
                        
        except Exception as e:
            print(f"{'  ' * current_depth}- {attr}: <error accessing: {e}>")


async def test_generation_methods(invoke):
    """Test different ways to generate images"""
    print("\n=== Testing Generation Methods ===")
    
    # Method 1: Check if there's a direct generation interface
    if hasattr(invoke, 'images'):
        print("\n1. Exploring invoke.images:")
        images_attrs = [attr for attr in dir(invoke.images) if not attr.startswith('_')]
        for attr in images_attrs[:10]:
            print(f"   - {attr}")
            
    # Method 2: Check queue interface (similar to our HTTP approach)
    if hasattr(invoke, 'queue'):
        print("\n2. Exploring invoke.queue:")
        queue_attrs = [attr for attr in dir(invoke.queue) if not attr.startswith('_')]
        for attr in queue_attrs[:10]:
            print(f"   - {attr}")
            
        # Try to enqueue a batch (like our HTTP implementation)
        if hasattr(invoke.queue, 'enqueue_batch'):
            print("   ✓ Found enqueue_batch method!")
            
    # Method 3: Check for workflow/graph functionality
    if hasattr(invoke, 'graph'):
        print("\n3. Found graph functionality")
        
    # Method 4: Look for utilities that might have style presets
    if hasattr(invoke, 'utilities'):
        print("\n4. Exploring invoke.utilities:")
        util_attrs = [attr for attr in dir(invoke.utilities) if not attr.startswith('_')]
        for attr in util_attrs:
            print(f"   - {attr}")


async def test_style_presets_direct(invoke):
    """Try to access style presets through direct API calls"""
    print("\n=== Testing Style Presets Direct Access ===")
    
    # The library uses aiohttp internally, let's try to make a direct call
    if hasattr(invoke, '_session') or hasattr(invoke, 'session'):
        print("Found internal session, could make direct API calls")
        
        # Try to access the style presets endpoint we know exists
        try:
            # Get the base URL
            base_url = f"http://{invoke.host}/api/v1"
            print(f"Base URL: {base_url}")
            
            # We know the endpoint exists from our previous work
            endpoint = f"{base_url}/style_presets/"
            print(f"Trying endpoint: {endpoint}")
            
            # The library might have a method to make raw API calls
            # Let's check if there's a request method
            if hasattr(invoke, 'request') or hasattr(invoke, '_request'):
                print("Found request method!")
                
        except Exception as e:
            print(f"Error accessing internals: {e}")


async def main():
    print("=== Deep Exploration of invokeai-python ===\n")
    
    invoke = Invoke()
    
    try:
        # Connect
        print("Connecting to InvokeAI...")
        version = await invoke.wait_invoke()
        print(f"✓ Connected! Version: {version}\n")
        
        # 1. Explore the main invoke object
        await explore_object(invoke, "invoke", max_depth=2)
        
        # 2. Test generation methods
        await test_generation_methods(invoke)
        
        # 3. Test style presets
        await test_style_presets_direct(invoke)
        
        # 4. Check specific endpoints we're interested in
        print("\n=== Checking Specific Functionality ===")
        
        # Check if we can access app settings or configuration
        if hasattr(invoke, 'app'):
            print("\nExploring invoke.app:")
            app_attrs = [attr for attr in dir(invoke.app) if not attr.startswith('_')]
            for attr in app_attrs:
                try:
                    value = getattr(invoke.app, attr)
                    if callable(value):
                        print(f"   - {attr}() -> method")
                    else:
                        print(f"   - {attr}: {type(value).__name__}")
                except:
                    print(f"   - {attr}: <inaccessible>")
                    
        # Close connection
        await invoke.close()
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())