#!/usr/bin/env python3
"""
Test script for diagnosing intro/outro rendering issues.
Tests different DPR values and rendering flags to identify optimal settings.

Usage: python scripts/test_intro_rendering.py [book_dir]
"""

import sys
import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
import time
from datetime import datetime
import json

def test_single_configuration(page, html_path, output_dir, config_name, width=1080, height=1920, dpr=1):
    """Test a single rendering configuration and save screenshot."""
    print(f"  Testing {config_name} (DPR={dpr})...")
    
    # Convert Path to string for comparison
    html_path_str = str(html_path)
    
    # Navigate to HTML
    if html_path_str.startswith('http'):
        page.goto(html_path_str, wait_until="domcontentloaded", timeout=60000)
    else:
        page.goto(f"file://{os.path.abspath(html_path_str)}", wait_until="domcontentloaded")
    
    # Wait for animations to complete (max animation is 2.5s)
    page.wait_for_timeout(3000)
    
    # Take screenshot
    screenshot_path = output_dir / f"{config_name}_dpr{dpr}.png"
    page.screenshot(
        path=str(screenshot_path),
        clip={"x": 0, "y": 0, "width": width, "height": height},
        animations="disabled",  # Capture after animations complete
    )
    
    # Get file size for comparison
    file_size = screenshot_path.stat().st_size / 1024  # KB
    print(f"    Saved: {screenshot_path.name} ({file_size:.1f}KB)")
    
    return {
        "config": config_name,
        "dpr": dpr,
        "file": screenshot_path.name,
        "size_kb": file_size
    }

def run_rendering_tests(html_path, output_dir):
    """Run all rendering tests with different configurations."""
    results = []
    
    # Test configurations
    configs = [
        {
            "name": "basic",
            "args": [
                '--disable-blink-features=AutomationControlled',
            ]
        },
        {
            "name": "high_quality",
            "args": [
                '--force-color-profile=srgb',
                '--enable-gpu-rasterization',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-low-res-tiling',
                '--disable-blink-features=AutomationControlled',
            ]
        },
        {
            "name": "gpu_enhanced",
            "args": [
                '--force-color-profile=srgb',
                '--enable-gpu-rasterization',
                '--enable-accelerated-2d-canvas',
                '--enable-features=VaapiVideoDecoder',
                '--use-angle=gl',
                '--enable-unsafe-swiftshader',
                '--disable-web-security',
                '--disable-low-res-tiling',
                '--high-dpi-support=1',
            ]
        }
    ]
    
    dprs = [1, 2, 3]  # Test different device pixel ratios
    
    with sync_playwright() as p:
        for config in configs:
            for dpr in dprs:
                browser = p.chromium.launch(
                    headless=True,
                    args=config["args"]
                )
                
                context = browser.new_context(
                    viewport={"width": 1080, "height": 1920},
                    device_scale_factor=dpr,
                )
                
                page = context.new_page()
                
                try:
                    result = test_single_configuration(
                        page, html_path, output_dir, 
                        config["name"], dpr=dpr
                    )
                    results.append(result)
                except Exception as e:
                    print(f"    Error: {e}")
                finally:
                    context.close()
                    browser.close()
    
    return results

def generate_comparison_html(results, output_dir):
    """Generate HTML page for visual comparison."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Rendering Test Comparison</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #1a1a1a; 
            color: #fff;
            padding: 20px;
        }
        h1 { text-align: center; color: #d4af37; }
        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 20px 0;
        }
        .test-item {
            background: #2a2a2a;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .test-item img {
            width: 100%;
            height: auto;
            border: 1px solid #444;
            cursor: pointer;
        }
        .test-item h3 { 
            color: #d4af37; 
            margin: 10px 0;
        }
        .info {
            font-size: 14px;
            color: #aaa;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
        }
        .modal img {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            max-width: 90%;
            max-height: 90%;
        }
        .modal.active { display: block; }
    </style>
</head>
<body>
    <h1>Intro/Outro Rendering Test Results</h1>
    <div class="info" style="text-align: center; margin: 20px;">
        Click on any image to view full size | Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
    </div>
    
    <div class="grid">
"""
    
    for result in results:
        html_content += f"""
        <div class="test-item">
            <h3>{result['config'].upper()} - DPR {result['dpr']}</h3>
            <img src="{result['file']}" onclick="showModal(this.src)" alt="{result['config']} DPR={result['dpr']}">
            <div class="info">Size: {result['size_kb']:.1f}KB</div>
        </div>
"""
    
    html_content += """
    </div>
    
    <div id="modal" class="modal" onclick="hideModal()">
        <img id="modalImg" src="">
    </div>
    
    <script>
        function showModal(src) {
            document.getElementById('modalImg').src = src;
            document.getElementById('modal').classList.add('active');
        }
        function hideModal() {
            document.getElementById('modal').classList.remove('active');
        }
    </script>
</body>
</html>
"""
    
    comparison_path = output_dir / "comparison.html"
    with open(comparison_path, 'w') as f:
        f.write(html_content)
    
    print(f"\n✅ Comparison page generated: {comparison_path}")
    print(f"   Open in browser: file://{comparison_path.absolute()}")

def main():
    # Parse arguments
    if len(sys.argv) > 1:
        book_dir = sys.argv[1]
    else:
        # Find a book with intro HTML
        book_dirs = [d for d in Path("books").iterdir() if d.is_dir()]
        for d in book_dirs:
            if (d / "assets" / "podcast-intro-screen.html").exists():
                book_dir = d.name
                break
        else:
            print("❌ No book with intro HTML found. Please specify a book directory.")
            sys.exit(1)
    
    print(f"🎬 Testing rendering for book: {book_dir}")
    
    # Paths
    intro_html = Path(f"books/{book_dir}/assets/podcast-intro-screen.html")
    if not intro_html.exists():
        print(f"❌ Intro HTML not found: {intro_html}")
        print("   Run: python generate_full_video.py {book_dir} first")
        sys.exit(1)
    
    # Create test output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"tests/rendering_{book_dir}_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output directory: {output_dir}")
    
    # Run tests
    print("\n🧪 Running rendering tests...")
    results = run_rendering_tests(intro_html, output_dir)
    
    # Save results as JSON
    results_json = output_dir / "results.json"
    with open(results_json, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📊 Results saved to: {results_json}")
    
    # Generate comparison HTML
    generate_comparison_html(results, output_dir)
    
    # Summary
    print("\n📈 Summary:")
    print(f"   Configurations tested: {len(set(r['config'] for r in results))}")
    print(f"   DPR values tested: {sorted(set(r['dpr'] for r in results))}")
    print(f"   Total screenshots: {len(results)}")
    
    # Find best quality (largest file usually = best quality)
    if results:
        best = max(results, key=lambda x: x['size_kb'])
        print(f"\n🏆 Highest quality: {best['config']} with DPR={best['dpr']} ({best['size_kb']:.1f}KB)")
    else:
        print("\n⚠️ No successful tests completed")

if __name__ == "__main__":
    main()