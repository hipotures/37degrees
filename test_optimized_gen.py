#!/usr/bin/env python3
"""Test optimized video generator"""
import time
import sys
from pathlib import Path
from src.optimized_video_generator import OptimizedVideoGenerator
from src.video_generator import VideoGenerator
from rich.console import Console

console = Console()

def test_optimized(book_yaml: str):
    """Test optimized generator"""
    start_time = time.time()
    
    template_path = "shared_assets/templates/classics_template.yaml"
    generator = OptimizedVideoGenerator(template_path)
    
    try:
        output_path = generator.generate_video(book_yaml)
        elapsed = time.time() - start_time
        console.print(f"[green]Optimized generator: {elapsed:.2f} seconds[/green]")
        return output_path
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return None

def test_moviepy(book_yaml: str):
    """Test MoviePy generator"""
    start_time = time.time()
    
    template_path = "shared_assets/templates/classics_template.yaml"
    generator = VideoGenerator(template_path)
    
    try:
        output_path = generator.generate_video(book_yaml)
        elapsed = time.time() - start_time
        console.print(f"[yellow]MoviePy generator: {elapsed:.2f} seconds[/yellow]")
        return output_path
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        book_yaml = "books/little_prince/book.yaml"
    else:
        book_yaml = sys.argv[1]
    
    console.print(f"\n[bold cyan]Testing video generation for: {book_yaml}[/bold cyan]\n")
    
    # Test optimized version first
    console.print("[blue]Testing optimized generator...[/blue]")
    optimized_output = test_optimized(book_yaml)
    
    if optimized_output:
        console.print(f"\n[green]✓ Optimized video saved to: {optimized_output}[/green]\n")
    
    # Optional: test MoviePy for comparison
    # console.print("[blue]Testing MoviePy generator...[/blue]")
    # moviepy_output = test_moviepy(book_yaml)