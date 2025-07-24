#!/usr/bin/env python3
"""
Enhanced text overlay system with color emoji support using Pilmoji
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor
from pilmoji import Pilmoji
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import re


class EmojiTextOverlay:
    """Handles text overlay with emoji support and various visibility methods"""
    
    def __init__(self, config: Dict):
        """Initialize with text overlay configuration"""
        self.config = config
        self.method = config.get('method', 'outline')
        self.font_config = config.get('font', {})
        self.regular_font = None
        
    def get_font(self, scale: float = 1.0) -> ImageFont.FreeTypeFont:
        """Load font with specified settings"""
        font_family = self.font_config.get('family', 'Arial')
        font_size = int(self.font_config.get('size', 48) * scale)
        font_weight = self.font_config.get('weight', 'bold')
        
        # Load regular font for text
        if not self.regular_font or self.regular_font.size != font_size:
            regular_font_paths = [
                # Noto Sans has excellent Unicode coverage
                "/usr/share/fonts/noto/NotoSans-Bold.ttf",
                "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
                # DejaVu also has good Unicode support
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                f"/usr/share/fonts/truetype/liberation/Liberation{font_family}-{font_weight.capitalize()}.ttf",
                f"/usr/share/fonts/truetype/dejavu/DejaVu{font_family}-{font_weight.capitalize()}.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Fallback
            ]
            
            for font_path in regular_font_paths:
                try:
                    self.regular_font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue
                    
            if not self.regular_font:
                self.regular_font = ImageFont.load_default()
        
        return self.regular_font
    
    def apply_gradient_overlay(self, image: Image.Image) -> Image.Image:
        """Apply darkening gradient to top of image"""
        img_copy = image.copy()
        gradient_config = self.config.get('gradient', {})
        
        # Create gradient
        width, height = image.size
        gradient_height = int(height * gradient_config.get('height_percent', 40) / 100)
        
        gradient = Image.new('RGBA', (width, gradient_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        start_opacity = int(255 * gradient_config.get('start_opacity', 0.7))
        end_opacity = int(255 * gradient_config.get('end_opacity', 0.0))
        
        for y in range(gradient_height):
            opacity = int(start_opacity - (start_opacity - end_opacity) * (y / gradient_height))
            draw.rectangle([(0, y), (width, y + 1)], fill=(0, 0, 0, opacity))
        
        # Apply gradient
        img_copy.paste(gradient, (0, 0), gradient)
        return img_copy
    
    def get_text_position(self, text_bbox: Tuple[int, int, int, int], 
                         image_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate text position based on alignment"""
        width, height = image_size
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        alignment = self.font_config.get('alignment', 'center')
        
        # Horizontal position
        if alignment == 'left':
            x = 50  # Left margin
        elif alignment == 'right':
            x = width - text_width - 50  # Right margin
        else:  # center
            x = (width - text_width) // 2
        
        # Vertical position (upper third)
        y = height // 6  # Approximately 16% from top
        
        return x, y
    
    def wrap_text(self, text: str, max_width: int, font: ImageFont.FreeTypeFont) -> list:
        """Wrap text to fit within max width"""
        # For emoji-aware wrapping, we need to use Pilmoji's text measurement
        words = text.split()
        lines = []
        current_line = []
        
        # Create temporary image for text measurement
        temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            
            # Use Pilmoji for accurate text measurement with emojis
            with Pilmoji(temp_img) as pilmoji:
                bbox = pilmoji.getsize(test_line, font)
                line_width = bbox[0]
            
            if line_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def draw_text_with_outline(self, image: Image.Image, position: Tuple[int, int], 
                              text: str, font: ImageFont.FreeTypeFont) -> Image.Image:
        """Draw text with outline using Pilmoji"""
        outline_config = self.config.get('outline', {})
        outline_color = outline_config.get('color', 'black')
        outline_width = outline_config.get('width', 3)
        text_color = self.font_config.get('color', 'white')
        
        x, y = position
        
        # Draw outline
        with Pilmoji(image) as pilmoji:
            for adj_x in range(-outline_width, outline_width + 1):
                for adj_y in range(-outline_width, outline_width + 1):
                    if adj_x != 0 or adj_y != 0:
                        pilmoji.text((x + adj_x, y + adj_y), text, outline_color, font)
            
            # Draw main text
            pilmoji.text((x, y), text, text_color, font)
        
        return image
    
    def draw_text_with_shadow(self, image: Image.Image, position: Tuple[int, int], 
                             text: str, font: ImageFont.FreeTypeFont) -> Image.Image:
        """Draw text with drop shadow using Pilmoji"""
        shadow_config = self.config.get('shadow', {})
        shadow_color = shadow_config.get('color', 'rgba(0, 0, 0, 0.8)')
        offset_x = shadow_config.get('offset_x', 2)
        offset_y = shadow_config.get('offset_y', 2)
        text_color = self.font_config.get('color', 'white')
        
        x, y = position
        
        # Parse shadow color (simplified)
        if shadow_color.startswith('rgba'):
            shadow_color = (0, 0, 0, 200)  # Default semi-transparent black
        
        with Pilmoji(image) as pilmoji:
            # Draw shadow
            pilmoji.text((x + offset_x, y + offset_y), text, shadow_color, font)
            
            # Draw main text
            pilmoji.text((x, y), text, text_color, font)
        
        return image
    
    def draw_text_with_box(self, image: Image.Image, position: Tuple[int, int], 
                          text: str, font: ImageFont.FreeTypeFont, lines: list) -> Image.Image:
        """Draw text with semi-transparent box background using Pilmoji"""
        box_config = self.config.get('box', {})
        box_color = box_config.get('color', 'rgba(0, 0, 0, 0.5)')
        padding = box_config.get('padding', 20)
        border_radius = box_config.get('border_radius', 15)
        text_color = self.font_config.get('color', 'white')
        
        # Create overlay for box
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Calculate box dimensions for all lines
        max_width = 0
        total_height = 0
        line_height = self.font_config.get('line_height', 1.4)
        line_spacing = int(font.size * line_height)
        
        # Use Pilmoji to get accurate text dimensions
        temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        with Pilmoji(temp_img) as pilmoji:
            for line in lines:
                bbox = pilmoji.getsize(line, font)
                max_width = max(max_width, bbox[0])
                total_height += line_spacing
        
        x, y = position
        box_x1 = x - padding
        box_y1 = y - padding
        box_x2 = x + max_width + padding
        box_y2 = y + total_height + padding
        
        # Parse box color
        if box_color.startswith('rgba'):
            box_color = (0, 0, 0, 128)  # Default semi-transparent black
        
        # Draw rounded rectangle
        draw.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], 
                              radius=border_radius, fill=box_color)
        
        # Composite box onto image
        img_with_box = Image.alpha_composite(image.convert('RGBA'), overlay)
        
        # Draw text on top with Pilmoji
        with Pilmoji(img_with_box) as pilmoji:
            current_y = y
            for line in lines:
                pilmoji.text((x, current_y), line, text_color, font)
                current_y += line_spacing
        
        return img_with_box
    
    def draw_text_with_glow(self, image: Image.Image, position: Tuple[int, int], 
                           text: str, font: ImageFont.FreeTypeFont) -> Image.Image:
        """Draw text with glow effect using Pilmoji"""
        glow_config = self.config.get('glow', {})
        glow_color = glow_config.get('color', 'white')
        intensity = glow_config.get('intensity', 0.8)
        spread = glow_config.get('spread', 10)
        text_color = self.font_config.get('color', 'white')
        
        # Create glow layer
        glow_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        
        # Draw multiple layers for glow effect with Pilmoji
        with Pilmoji(glow_layer) as pilmoji:
            for i in range(spread, 0, -1):
                alpha = int(255 * intensity * (i / spread))
                glow_fill = (*ImageColor.getrgb(glow_color), alpha)
                
                for adj_x in range(-i, i + 1, max(1, i // 2)):
                    for adj_y in range(-i, i + 1, max(1, i // 2)):
                        x, y = position
                        pilmoji.text((x + adj_x, y + adj_y), text, glow_fill, font)
        
        # Apply blur for smoother glow
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=spread // 2))
        
        # Composite glow
        img_with_glow = Image.alpha_composite(image.convert('RGBA'), glow_layer)
        
        # Draw crisp text on top
        with Pilmoji(img_with_glow) as pilmoji:
            pilmoji.text(position, text, text_color, font)
        
        return img_with_glow
    
    def apply_text_overlay(self, image: Image.Image, text: str) -> Image.Image:
        """Apply text overlay using configured method with emoji support"""
        # Prepare image
        if self.method == 'gradient':
            image = self.apply_gradient_overlay(image)
        
        # Get font
        font = self.get_font()
        
        # Wrap text
        max_width = int(image.size[0] * 0.8)  # 80% of image width
        lines = self.wrap_text(text, max_width, font)
        
        # Calculate line height
        line_height = self.font_config.get('line_height', 1.4)
        font_size = self.font_config.get('size', 48)
        line_spacing = int(font_size * line_height)
        
        # Process based on method
        result_image = image.convert('RGBA')
        
        # For box method, handle all lines together
        if self.method == 'box':
            # Get position for first line
            temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
            with Pilmoji(temp_img) as pilmoji:
                bbox = pilmoji.getsize(lines[0], font)
            
            x, y = self.get_text_position((0, 0, bbox[0], bbox[1]), image.size)
            result_image = self.draw_text_with_box(result_image, (x, y), text, font, lines)
        else:
            # Handle other methods line by line
            for i, line in enumerate(lines):
                # Get position for this line
                temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
                with Pilmoji(temp_img) as pilmoji:
                    bbox = pilmoji.getsize(line, font)
                
                x, base_y = self.get_text_position((0, 0, bbox[0], bbox[1]), image.size)
                y = base_y + (i * line_spacing)
                
                if self.method == 'outline':
                    result_image = self.draw_text_with_outline(result_image, (x, y), line, font)
                    
                elif self.method == 'shadow':
                    result_image = self.draw_text_with_shadow(result_image, (x, y), line, font)
                    
                elif self.method == 'glow':
                    result_image = self.draw_text_with_glow(result_image, (x, y), line, font)
                    
                else:  # Default to simple text
                    with Pilmoji(result_image) as pilmoji:
                        pilmoji.text((x, y), line, self.font_config.get('color', 'white'), font)
        
        return result_image.convert('RGB')


def test_emoji_text_overlay():
    """Test emoji text overlay with color emojis"""
    from PIL import Image
    
    # Create test image
    test_image = Image.new('RGB', (1080, 1920), color='lightblue')
    
    # Test configuration
    config = {
        'method': 'outline',
        'outline': {'color': 'black', 'width': 3},
        'font': {
            'size': 48,
            'color': 'white',
            'weight': 'bold',
            'alignment': 'center'
        }
    }
    
    overlay = EmojiTextOverlay(config)
    result = overlay.apply_text_overlay(test_image, "Czy wiesz, że najważniejsze jest niewidoczne dla oczu? 👁️✨🎨")
    result.save('test_emoji_overlay.png')
    print("Test image saved as test_emoji_overlay.png")


if __name__ == "__main__":
    test_emoji_text_overlay()