"""AI image generation functionality for 37degrees"""

from pathlib import Path
import yaml
import os
from rich.console import Console
from src.config import get_config
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm
from src.generators import GeneratorRegistry
from src.generators.invokeai import InvokeAIGenerator
from src.generators.comfyui import ComfyUIGenerator
from src.generators.mock import MockGenerator
from src.simple_invokeai_generator import build_prompt_from_scene, build_negative_prompt
from src.style_preset_loader import load_invokeai_style_presets
from src.cli.utils import resolve_target, get_book_path


def convert_scene_format(scene_data: dict) -> dict:
    """Convert new scene YAML format to expected slide format"""
    scene_desc = scene_data.get('sceneDescription', {})
    scene_info = scene_desc.get('scene', {})
    setting = scene_desc.get('setting', {})
    characters = scene_desc.get('characters', [])
    visual_elements = scene_data.get('visualElements', {})
    
    # Build elements list from various parts
    elements = []
    
    # Add main elements
    if 'mainElements' in scene_info:
        if isinstance(scene_info['mainElements'], list):
            elements.extend(scene_info['mainElements'])
        else:
            elements.append(scene_info['mainElements'])
    
    # Add character descriptions
    for char in characters:
        if isinstance(char, dict):
            if 'appearance' in char:
                elements.append(char['appearance'])
            if 'clothing' in char:
                elements.append(char['clothing'])
            if 'action' in char:
                elements.append(char['action'])
        elif isinstance(char, str):
            elements.append(char)
    
    # Add setting details
    if 'location' in setting:
        elements.append(setting['location'])
    if 'weather' in setting:
        elements.append(setting['weather'])
    
    # Convert to expected format
    converted = {
        'scene': {
            'elements': elements,
            'composition': scene_desc.get('composition', {}),
            'atmosphere': scene_info.get('atmosphere', ''),
            'background': scene_info.get('background', ''),
            'details': scene_info.get('details', ''),
        },
        'visual_style': visual_elements.get('colorPalette', {}),
        'mood': visual_elements.get('mood', {}),
        'technical_specs': scene_data.get('technicalSpecifications', {})
    }
    
    return converted

console = Console()

# Get config
config = get_config()

# Initialize generator registry
from src.generators import registry

# Register available generators
registry.register('invokeai', InvokeAIGenerator)
registry.register('comfyui', ComfyUIGenerator)
registry.register('mock', MockGenerator)

# Load generator config
generator_config_path = Path(config.get('services.generators.config_file', 'config/generators.yaml'))
if generator_config_path.exists():
    registry.load_config(generator_config_path)


def generate_images(target: str, book_id: str = None, generator_name: str = None):
    """Generate AI images for a book or collection
    
    Args:
        target: Book ID, book name, or collection name
        book_id: Specific book ID when target is a collection
        generator_name: Override generator (default from config)
    """
    
    # Resolve target
    target_type, target_value = resolve_target(target)
    
    if target_type == "collection":
        # Generate for entire collection
        if book_id:
            # Generate for specific book in collection
            generate_single_book_images_from_collection(target_value, book_id, generator_name)
        else:
            # Generate for all books in collection
            generate_collection_images(target_value, generator_name)
    else:
        # Generate for single book
        book_path = get_book_path(target_value)
        if book_path:
            generate_single_book_images(book_path, generator_name)
        else:
            console.print(f"[red]Book '{target}' not found![/red]")


def generate_single_book_images(book_yaml_path: Path, generator_name: str = None):
    """Generate AI images for a single book"""
    
    # Load book info
    with open(book_yaml_path, 'r', encoding='utf-8') as f:
        book_data = yaml.safe_load(f)
    book_info = book_data.get('book_info', {})
    
    # Load scenes from individual YAML files in prompts/genimage/
    book_dir = book_yaml_path.parent
    prompts_dir = book_dir / "prompts" / "genimage"
    slides = []
    
    if prompts_dir.exists():
        scene_files = sorted(prompts_dir.glob("scene_*.yaml"))
        for scene_file in scene_files:
            try:
                with open(scene_file, 'r', encoding='utf-8') as f:
                    raw_scene_data = yaml.safe_load(f)
                    # Convert to expected format
                    scene_data = convert_scene_format(raw_scene_data)
                    # Add scene number from filename
                    scene_num = scene_file.stem.split('_')[1]
                    scene_data['scene_id'] = int(scene_num)
                    scene_data['type'] = f"scene_{scene_num}"
                    slides.append(scene_data)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load {scene_file}: {e}[/yellow]")
                continue
    
    console.print(f"\n[bold cyan]Generating AI images for: {book_info.get('title', 'Unknown')}[/bold cyan]")
    console.print(f"[dim]Total scenes: {len(slides)}[/dim]\n")
    
    # Get generator
    if not generator_name:
        # Check environment or use default from config
        if os.getenv('TESTING') == 'true':
            generator_name = 'mock'
        else:
            generator_name = config.get('services.generators.default', 'invokeai')
    
    console.print(f"[yellow]Using generator: {generator_name}[/yellow]")
    
    try:
        generator = registry.get_generator(generator_name)
    except Exception as e:
        console.print(f"[red]Failed to initialize generator '{generator_name}': {e}[/red]")
        return
    
    # Test connection
    if not generator.test_connection():
        console.print(f"[red]Failed to connect to {generator_name}[/red]")
        return
    
    # Check if images already exist
    book_dir = book_yaml_path.parent
    generated_dir = book_dir / "generated"
    if generated_dir.exists():
        existing_images = list(generated_dir.glob("*.png"))
        if existing_images:
            console.print(f"[yellow]Found {len(existing_images)} existing images - regenerating...[/yellow]")
    
    # Get configuration
    custom_art_style = book_data.get('custom_art_style', {})
    template_art_style = book_data.get('template_art_style', '')
    ai_generation = book_data.get('ai_generation', {})
    tech_specs = book_data.get('technical_specs', {})
    
    # Load style presets if using template
    template_style = None
    if template_art_style:
        style_presets = load_invokeai_style_presets()
        if template_art_style in style_presets:
            template_style = style_presets[template_art_style]
            console.print(f"[green]Using style template: {template_art_style}[/green]")
    
    # Parse resolution
    resolution = tech_specs.get('resolution', '1080x1920').split('x')
    width, height = int(resolution[0]), int(resolution[1])
    
    # Validate dimensions for the generator
    width, height = generator.validate_dimensions(width, height)
    
    # Create output directory
    generated_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate images with progress
    successful = 0
    failed = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        main_task = progress.add_task("Generating AI images...", total=len(slides))
        
        for idx, slide in enumerate(slides):
            scene_type = slide.get('type', 'unknown')
            progress.update(main_task, description=f"Generating scene {idx + 1}/{len(slides)}: {scene_type}")
            
            # Build prompts
            prompt = build_prompt_from_scene(slide, custom_art_style, template_style)
            negative_prompt = build_negative_prompt(custom_art_style, template_style)
            
            console.print(f"\n[cyan]Scene {idx + 1}: {scene_type}[/cyan]")
            console.print(f"[dim]Prompt: {prompt[:100]}...[/dim]")
            
            try:
                # Generate image
                image_id = generator.generate_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    seed=ai_generation.get('seed', -1),
                    model_key=ai_generation.get('model_key'),
                    steps=ai_generation.get('steps', 30),
                    cfg_scale=ai_generation.get('cfg_scale', 7.5),
                    sampler=ai_generation.get('sampler', 'euler_a')
                )
                
                if image_id:
                    # Download image
                    output_path = generated_dir / f"scene_{idx:02d}_{scene_type}.png"
                    if generator.download_image(image_id, output_path):
                        console.print(f"[green]✓ Saved to: {output_path}[/green]")
                        successful += 1
                    else:
                        console.print(f"[red]✗ Failed to save image[/red]")
                        failed += 1
                else:
                    console.print(f"[red]✗ Failed to generate image[/red]")
                    failed += 1
                    
            except Exception as e:
                console.print(f"[red]✗ Error: {e}[/red]")
                failed += 1
            
            progress.update(main_task, advance=1)
    
    # Summary
    console.print(f"\n[bold]Generation Summary:[/bold]")
    console.print(f"  [green]✅ Successful: {successful}[/green]")
    if failed > 0:
        console.print(f"  [red]❌ Failed: {failed}[/red]")
    console.print(f"  [dim]Total: {len(slides)}[/dim]")
    console.print(f"\n[dim]Images saved to: {generated_dir}/[/dim]")


def generate_single_book_images_from_collection(collection_name: str, book_id: str, generator_name: str = None):
    """Generate images for a specific book from a collection"""
    collection_file = Path(f"collections/{collection_name}.yaml")
    
    if not collection_file.exists():
        console.print(f"[red]Collection '{collection_name}' not found![/red]")
        return
    
    # Load collection
    with open(collection_file, 'r', encoding='utf-8') as f:
        collection_data = yaml.safe_load(f)
    
    books = collection_data.get('books', [])
    
    # Find book by order number
    book_ref = None
    for book in books:
        if str(book.get('order', '')) == book_id:
            book_ref = book
            break
    
    if not book_ref:
        console.print(f"[red]Book #{book_id} not found in collection '{collection_name}'[/red]")
        return
    
    book_path = Path(book_ref['path'])
    if book_path.exists():
        generate_single_book_images(book_path, generator_name)
    else:
        console.print(f"[red]Book file not found: {book_ref['path']}[/red]")


def generate_collection_images(collection_name: str, generator_name: str = None):
    """Generate images for all books in a collection"""
    collection_file = Path(f"collections/{collection_name}.yaml")
    
    if not collection_file.exists():
        console.print(f"[red]Collection '{collection_name}' not found![/red]")
        return
    
    # Load collection
    with open(collection_file, 'r', encoding='utf-8') as f:
        collection_data = yaml.safe_load(f)
    
    series_info = collection_data.get('series', {})
    books = collection_data.get('books', [])
    
    console.print(f"\n[bold cyan]Generating AI images for collection: {series_info.get('name', collection_name)}[/bold cyan]")
    console.print(f"[dim]Total books: {len(books)}[/dim]\n")
    
    # Calculate total scenes
    total_scenes = 0
    for book_ref in books:
        book_path = Path(book_ref['path'])
        if book_path.exists():
            with open(book_path, 'r', encoding='utf-8') as f:
                book_data = yaml.safe_load(f)
            total_scenes += len(book_data.get('slides', []))
    
    console.print(f"[yellow]This will generate approximately {total_scenes} images[/yellow]")
    
    # Confirm batch operation
    if not Confirm.ask(f"Generate AI images for [yellow]{len(books)}[/yellow] books?"):
        console.print("[yellow]Operation cancelled[/yellow]")
        return
    
    # Process each book
    successful = 0
    failed = 0
    
    for i, book_ref in enumerate(books, 1):
        book_path = Path(book_ref['path'])
        
        if book_path.exists():
            try:
                # Load book title
                with open(book_path, 'r', encoding='utf-8') as f:
                    book_data = yaml.safe_load(f)
                book_title = book_data.get('book_info', {}).get('title', 'Unknown')
                
                console.print(f"\n[bold blue]Book {i}/{len(books)}: {book_title}[/bold blue]")
                
                generate_single_book_images(book_path, generator_name)
                successful += 1
                
            except Exception as e:
                console.print(f"[red]Error with {book_path}: {e}[/red]")
                failed += 1
        else:
            console.print(f"[red]Book file not found: {book_ref['path']}[/red]")
            failed += 1
    
    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  [green]✅ Successful: {successful}[/green]")
    console.print(f"  [red]❌ Failed: {failed}[/red]")
    console.print(f"  [dim]Total: {len(books)}[/dim]")