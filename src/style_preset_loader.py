#!/usr/bin/env python3
"""
InvokeAI Style Preset Loader
Loads and displays available style presets from InvokeAI
"""

import json
from pathlib import Path
from typing import Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def load_invokeai_style_presets(invokeai_path: Optional[str] = None) -> Dict[str, Dict]:
    """Load InvokeAI style presets from the default presets file
    
    Args:
        invokeai_path: Optional path to InvokeAI installation. If not provided,
                      will try to find it in common locations.
    
    Returns:
        Dictionary mapping style names to their preset data
    """
    preset_paths = []
    
    if invokeai_path:
        preset_paths.append(Path(invokeai_path) / ".venv/lib/python3.12/site-packages/invokeai/app/services/style_preset_records/default_style_presets.json")
    
    # Common paths to check
    preset_paths.extend([
        Path.home() / "DEV/invokeai/.venv/lib/python3.12/site-packages/invokeai/app/services/style_preset_records/default_style_presets.json",
        Path("/home/xai/DEV/invokeai/.venv/lib/python3.12/site-packages/invokeai/app/services/style_preset_records/default_style_presets.json"),
        Path.home() / ".invokeai/.venv/lib/python3.12/site-packages/invokeai/app/services/style_preset_records/default_style_presets.json",
    ])
    
    for preset_path in preset_paths:
        if preset_path.exists():
            try:
                with open(preset_path, 'r', encoding='utf-8') as f:
                    presets_data = json.load(f)
                    
                # Convert to dictionary for easy lookup
                presets = {}
                for preset in presets_data:
                    name = preset.get('name')
                    if name:
                        presets[name] = preset.get('preset_data', {})
                
                console.print(f"[green]✓ Loaded {len(presets)} style presets from:[/green]")
                console.print(f"  {preset_path}")
                return presets
                
            except Exception as e:
                console.print(f"[red]Error loading presets from {preset_path}: {e}[/red]")
                continue
    
    console.print("[yellow]Warning: Could not find InvokeAI style presets file[/yellow]")
    return {}


def display_style_presets(presets: Dict[str, Dict]):
    """Display style presets in a formatted table"""
    if not presets:
        console.print("[red]No presets to display[/red]")
        return
    
    table = Table(title="InvokeAI Style Presets", show_header=True, header_style="bold magenta")
    table.add_column("Style Name", style="cyan", width=30)
    table.add_column("Positive Prompt", style="green", width=50)
    table.add_column("Negative Prompt", style="red", width=40)
    
    for name, data in sorted(presets.items()):
        positive = data.get('positive_prompt', '').replace('{prompt}', '[YOUR PROMPT]')
        negative = data.get('negative_prompt', '')
        
        # Truncate long prompts for display
        if len(positive) > 47:
            positive = positive[:44] + "..."
        if len(negative) > 37:
            negative = negative[:34] + "..."
            
        table.add_row(name, positive, negative)
    
    console.print(table)


def get_style_preset_details(presets: Dict[str, Dict], style_name: str) -> Optional[Dict]:
    """Get detailed information about a specific style preset"""
    if style_name in presets:
        preset = presets[style_name]
        console.print(Panel(f"[bold cyan]{style_name}[/bold cyan] Style Preset", expand=False))
        
        console.print("\n[bold green]Positive Prompt:[/bold green]")
        console.print(preset.get('positive_prompt', '').replace('{prompt}', '[YOUR PROMPT]'))
        
        console.print("\n[bold red]Negative Prompt:[/bold red]")
        console.print(preset.get('negative_prompt', 'None'))
        
        return preset
    else:
        console.print(f"[red]Style preset '{style_name}' not found[/red]")
        return None


def main():
    """Main function to demonstrate style preset loading"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load and display InvokeAI style presets")
    parser.add_argument('--path', help="Path to InvokeAI installation")
    parser.add_argument('--style', help="Show details for specific style")
    parser.add_argument('--json', action='store_true', help="Output as JSON")
    
    args = parser.parse_args()
    
    # Load presets
    presets = load_invokeai_style_presets(args.path)
    
    if args.json:
        # Output as JSON
        print(json.dumps(presets, indent=2))
    elif args.style:
        # Show specific style details
        get_style_preset_details(presets, args.style)
    else:
        # Display all presets in table
        display_style_presets(presets)
        
        # Show example usage
        console.print("\n[bold]Example Usage:[/bold]")
        console.print("To use the 'Illustration' style in your book.yaml:")
        console.print('[yellow]template_art_style: "Illustration"[/yellow]')
        
        if "Illustration" in presets:
            console.print("\nThis will apply:")
            illustration = presets["Illustration"]
            console.print(f"[green]Positive:[/green] {illustration.get('positive_prompt', '')}")
            console.print(f"[red]Negative:[/red] {illustration.get('negative_prompt', '')}")


if __name__ == "__main__":
    main()