#!/usr/bin/env python3
"""
Mock generator for testing and development
"""

import time
import random
from pathlib import Path
from typing import Dict, Optional, Any
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console

from .base import BaseImageGenerator, GeneratorError

console = Console()


class MockGenerator(BaseImageGenerator):
    """Mock generator that creates placeholder images"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize mock generator
        
        Args:
            config: Configuration dict with:
                - delay: Simulated generation delay in seconds (default: 2)
                - fail_rate: Probability of simulated failure (0.0-1.0, default: 0)
                - placeholder_style: Style of placeholder (simple, detailed, debug)
        """
        super().__init__(config)
        self.delay = config.get('delay', 2)
        self.fail_rate = config.get('fail_rate', 0.0)
        self.placeholder_style = config.get('placeholder_style', 'simple')
        self._generated_images = {}
    
    def test_connection(self) -> bool:
        """Always returns True for mock generator"""
        console.print("[green]Mock generator connection test successful[/green]")
        return True
    
    def generate_image(self,
                      prompt: str,
                      negative_prompt: str = "",
                      width: int = 1080,
                      height: int = 1920,
                      seed: int = -1,
                      **kwargs) -> Optional[str]:
        """Generate a mock placeholder image
        
        Args:
            prompt: Positive prompt (shown on placeholder)
            negative_prompt: Negative prompt (ignored)
            width: Image width
            height: Image height
            seed: Random seed (used for ID)
            **kwargs: Additional parameters
            
        Returns:
            Mock image ID if successful, None otherwise
        """
        # Simulate failure
        if random.random() < self.fail_rate:
            raise GeneratorError("Simulated generation failure")
        
        # Simulate generation delay
        console.print(f"[yellow]Mock generation starting (delay: {self.delay}s)...[/yellow]")
        time.sleep(self.delay)
        
        # Generate mock image ID
        if seed == -1:
            seed = random.randint(0, 2**32-1)
        image_id = f"mock_{seed}_{int(time.time())}"
        
        # Store generation info
        self._generated_images[image_id] = {
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'width': width,
            'height': height,
            'seed': seed,
            'kwargs': kwargs
        }
        
        console.print(f"[green]✓ Mock image generated: {image_id}[/green]")
        return image_id
    
    def download_image(self, image_id: str, output_path: Path) -> bool:
        """Create and save a placeholder image
        
        Args:
            image_id: Mock image ID
            output_path: Where to save the placeholder
            
        Returns:
            True if successful, False otherwise
        """
        if image_id not in self._generated_images:
            console.print(f"[red]Image ID not found: {image_id}[/red]")
            return False
        
        try:
            # Get generation info
            info = self._generated_images[image_id]
            
            # Create placeholder image
            img = self._create_placeholder(
                width=info['width'],
                height=info['height'],
                prompt=info['prompt'],
                image_id=image_id
            )
            
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save image
            img.save(output_path, 'PNG')
            console.print(f"[green]✓ Placeholder saved to: {output_path}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error saving placeholder: {e}[/red]")
            return False
    
    def _create_placeholder(self, width: int, height: int, prompt: str, image_id: str) -> Image.Image:
        """Create a placeholder image with text
        
        Args:
            width: Image width
            height: Image height  
            prompt: Prompt text to display
            image_id: Image ID to display
            
        Returns:
            PIL Image object
        """
        # Create base image with gradient background
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Create gradient background
        for y in range(height):
            r = int(100 + (155 * y / height))
            g = int(50 + (100 * y / height))
            b = int(150 + (105 * y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add content based on style
        if self.placeholder_style == 'simple':
            self._add_simple_content(draw, width, height, prompt, image_id)
        elif self.placeholder_style == 'detailed':
            self._add_detailed_content(draw, width, height, prompt, image_id)
        elif self.placeholder_style == 'debug':
            self._add_debug_content(draw, width, height, prompt, image_id)
        
        return img
    
    def _add_simple_content(self, draw: ImageDraw.Draw, width: int, height: int, 
                           prompt: str, image_id: str) -> None:
        """Add simple placeholder content"""
        # Draw border
        draw.rectangle([(10, 10), (width-10, height-10)], outline=(255, 255, 255), width=3)
        
        # Add title
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw "MOCK" text
        text = "MOCK PLACEHOLDER"
        bbox = draw.textbbox((0, 0), text, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = height // 3
        draw.text((x, y), text, fill=(255, 255, 255), font=font_large)
        
        # Draw dimensions
        dim_text = f"{width} x {height}"
        bbox = draw.textbbox((0, 0), dim_text, font=font_small)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = height // 2
        draw.text((x, y), dim_text, fill=(255, 255, 255), font=font_small)
        
        # Add prompt preview (truncated)
        prompt_preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
        bbox = draw.textbbox((0, 0), prompt_preview, font=font_small)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = height * 2 // 3
        draw.text((x, y), prompt_preview, fill=(200, 200, 200), font=font_small)
    
    def _add_detailed_content(self, draw: ImageDraw.Draw, width: int, height: int,
                             prompt: str, image_id: str) -> None:
        """Add detailed placeholder content with scene elements"""
        # Draw frame
        draw.rectangle([(20, 20), (width-20, height-20)], outline=(255, 255, 255), width=5)
        
        # Upper third for text overlay area (as per requirements)
        text_area_height = height // 3
        draw.rectangle([(50, 50), (width-50, text_area_height)], 
                      fill=(255, 255, 255, 50), outline=(255, 255, 255))
        
        # Add some mock scene elements
        # Sun/moon
        draw.ellipse([(width-200, 100), (width-100, 200)], 
                    fill=(255, 255, 100), outline=(255, 200, 0))
        
        # Ground/horizon
        draw.line([(0, height*2//3), (width, height*2//3)], 
                 fill=(100, 150, 100), width=3)
        
        # Mock character
        char_x = width // 2
        char_y = height * 2 // 3
        # Head
        draw.ellipse([(char_x-30, char_y-80), (char_x+30, char_y-20)],
                    fill=(255, 200, 150), outline=(200, 150, 100))
        # Body
        draw.rectangle([(char_x-40, char_y-20), (char_x+40, char_y+60)],
                      fill=(100, 100, 200), outline=(80, 80, 160))
        
        # Add labels
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((60, 60), "TEXT OVERLAY AREA", fill=(0, 0, 0), font=font)
        draw.text((50, height-100), f"Scene: {prompt[:30]}...", fill=(255, 255, 255), font=font)
    
    def _add_debug_content(self, draw: ImageDraw.Draw, width: int, height: int,
                          prompt: str, image_id: str) -> None:
        """Add debug information to placeholder"""
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Mono.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Debug info
        debug_info = [
            f"Generator: MockGenerator",
            f"Image ID: {image_id}",
            f"Dimensions: {width}x{height}",
            f"Style: {self.placeholder_style}",
            "",
            "PROMPT:",
            *[prompt[i:i+60] for i in range(0, len(prompt), 60)],
            "",
            f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        
        y = 30
        for line in debug_info:
            draw.text((30, y), line, fill=(255, 255, 255), font=font)
            y += 25
    
    def get_info(self) -> Dict[str, Any]:
        """Get generator information"""
        info = super().get_info()
        info.update({
            'delay': self.delay,
            'fail_rate': self.fail_rate,
            'placeholder_style': self.placeholder_style,
            'images_generated': len(self._generated_images)
        })
        return info