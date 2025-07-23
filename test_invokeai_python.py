#!/usr/bin/env python3
"""
Test script to explore invokeai-python library
and check how it handles style templates
"""

import asyncio
from invoke import Invoke
from invoke.api import BaseModels, ModelType
import json


async def main():
    print("=== Testing invokeai-python library ===\n")
    
    # Initialize the client
    invoke = Invoke()
    
    try:
        # Wait for connection
        print("Waiting for InvokeAI connection...")
        version = await invoke.wait_invoke()
        print(f"✓ Connected! Version: {version}\n")
        
        # 1. List available models
        print("1. Checking available models:")
        models = await invoke.models.list(base_models=[BaseModels.SDXL], model_type=[ModelType.Main])
        for model in models[:3]:  # Show first 3
            print(f"   - {model.name} (key: {model.key})")
        print()
        
        # 2. Check if there's a way to get style presets
        print("2. Looking for style preset methods:")
        
        # Check available attributes on invoke object
        invoke_attrs = [attr for attr in dir(invoke) if not attr.startswith('_')]
        print(f"   Available invoke attributes: {', '.join(invoke_attrs[:10])}...")
        
        # Check if there's a styles attribute
        if hasattr(invoke, 'styles'):
            print("   ✓ Found 'styles' attribute!")
            styles_methods = [m for m in dir(invoke.styles) if not m.startswith('_')]
            print(f"   Available methods: {', '.join(styles_methods)}")
            
            # Try to list styles
            try:
                styles = await invoke.styles.list()
                print(f"\n   Available style presets:")
                for style in styles[:5]:
                    print(f"   - {style}")
            except Exception as e:
                print(f"   Could not list styles: {e}")
        else:
            print("   ✗ No 'styles' attribute found")
        
        # 3. Check for presets or templates
        if hasattr(invoke, 'presets'):
            print("\n   ✓ Found 'presets' attribute!")
            try:
                presets = await invoke.presets.list()
                print(f"   Available presets: {presets}")
            except Exception as e:
                print(f"   Could not list presets: {e}")
                
        # 4. Try to generate an image with the library
        print("\n3. Attempting to generate an image:")
        
        # Check if there's a generation method
        if hasattr(invoke, 'generate') or hasattr(invoke, 'images'):
            print("   Found generation methods!")
            
            # Try different approaches
            if hasattr(invoke, 'images') and hasattr(invoke.images, 'generate'):
                print("   Trying invoke.images.generate()...")
                # This is hypothetical - we don't know the exact API yet
                try:
                    result = await invoke.images.generate(
                        prompt="A simple red rose, illustration style",
                        model_key="c81f2f9b-cabd-40ec-b6f4-d3172c10bafc",
                        width=1080,
                        height=1920
                    )
                    print(f"   Result: {result}")
                except Exception as e:
                    print(f"   Error: {e}")
                    
        # 5. Explore the API structure
        print("\n4. Exploring API structure:")
        
        # Check what's available in invoke.api
        if hasattr(invoke, 'api'):
            api_attrs = [attr for attr in dir(invoke.api) if not attr.startswith('_')]
            print(f"   API attributes: {', '.join(api_attrs[:10])}...")
            
        # Look for workflow or graph functionality
        if hasattr(invoke, 'graph') or hasattr(invoke, 'workflow'):
            print("   ✓ Found graph/workflow functionality")
            
        # 6. Try to inspect the actual HTTP client
        if hasattr(invoke, 'session') or hasattr(invoke, '_session'):
            print("\n5. Found HTTP session - could make direct API calls")
            
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n=== Test complete ===")


if __name__ == "__main__":
    asyncio.run(main())