#!/usr/bin/env python3
"""
Text overlay system with multiple rendering methods
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import re


class TextOverlay:
    """Handles text overlay with various visibility methods"""
    
    def __init__(self, config: Dict):
        """Initialize with text overlay configuration"""
        self.config = config
        self.method = config.get('method', 'outline')
        self.font_config = config.get('font', {})
        self.emoji_font = None
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
        
        # Load emoji font separately
        if not self.emoji_font or self.emoji_font.size != font_size:
            emoji_font_paths = [
                # Noto Color Emoji has full color emoji support
                "/usr/share/fonts/noto/NotoColorEmoji.ttf",
                "/usr/share/fonts/truetype/noto-color-emoji/NotoColorEmoji.ttf",
                # Segoe UI Emoji (Windows font, may be available on some systems)
                "/usr/share/fonts/truetype/segoe-ui-emoji/seguiemj.ttf",
            ]
            
            for font_path in emoji_font_paths:
                try:
                    self.emoji_font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue
        
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
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            line_width = bbox[2] - bbox[0]
            
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
    
    def draw_text_with_outline(self, draw: ImageDraw.Draw, position: Tuple[int, int], 
                              text: str, font: ImageFont.FreeTypeFont):
        """Draw text with outline"""
        outline_config = self.config.get('outline', {})
        outline_color = outline_config.get('color', 'black')
        outline_width = outline_config.get('width', 3)
        text_color = self.font_config.get('color', 'white')
        
        x, y = position
        
        # Draw outline
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color, embedded_color=True)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color, embedded_color=True)
    
    def draw_text_with_shadow(self, draw: ImageDraw.Draw, position: Tuple[int, int], 
                             text: str, font: ImageFont.FreeTypeFont):
        """Draw text with drop shadow"""
        shadow_config = self.config.get('shadow', {})
        shadow_color = shadow_config.get('color', 'rgba(0, 0, 0, 0.8)')
        offset_x = shadow_config.get('offset_x', 2)
        offset_y = shadow_config.get('offset_y', 2)
        text_color = self.font_config.get('color', 'white')
        
        x, y = position
        
        # Parse shadow color (simplified)
        if shadow_color.startswith('rgba'):
            shadow_color = (0, 0, 0, 200)  # Default semi-transparent black
        
        # Draw shadow
        draw.text((x + offset_x, y + offset_y), text, font=font, fill=shadow_color, embedded_color=True)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color, embedded_color=True)
    
    def draw_text_with_box(self, image: Image.Image, position: Tuple[int, int], 
                          text: str, font: ImageFont.FreeTypeFont) -> Image.Image:
        """Draw text with semi-transparent box background"""
        box_config = self.config.get('box', {})
        box_color = box_config.get('color', 'rgba(0, 0, 0, 0.5)')
        padding = box_config.get('padding', 20)
        border_radius = box_config.get('border_radius', 15)
        text_color = self.font_config.get('color', 'white')
        
        # Create overlay for box
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Calculate box dimensions
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x, y = position
        box_x1 = x - padding
        box_y1 = y - padding
        box_x2 = x + text_width + padding
        box_y2 = y + text_height + padding
        
        # Parse box color
        if box_color.startswith('rgba'):
            box_color = (0, 0, 0, 128)  # Default semi-transparent black
        
        # Draw rounded rectangle
        draw.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], 
                              radius=border_radius, fill=box_color)
        
        # Composite box onto image
        img_with_box = Image.alpha_composite(image.convert('RGBA'), overlay)
        
        # Draw text on top
        draw_final = ImageDraw.Draw(img_with_box)
        draw_final.text((x, y), text, font=font, fill=text_color, embedded_color=True)
        
        return img_with_box
    
    def draw_text_with_glow(self, image: Image.Image, position: Tuple[int, int], 
                           text: str, font: ImageFont.FreeTypeFont) -> Image.Image:
        """Draw text with glow effect"""
        glow_config = self.config.get('glow', {})
        glow_color = glow_config.get('color', 'white')
        intensity = glow_config.get('intensity', 0.8)
        spread = glow_config.get('spread', 10)
        text_color = self.font_config.get('color', 'white')
        
        # Create glow layer
        glow_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw_glow = ImageDraw.Draw(glow_layer)
        
        # Draw multiple layers for glow effect
        for i in range(spread, 0, -1):
            alpha = int(255 * intensity * (i / spread))
            glow_fill = (*ImageColor.getrgb(glow_color), alpha)
            
            for adj_x in range(-i, i + 1, max(1, i // 2)):
                for adj_y in range(-i, i + 1, max(1, i // 2)):
                    x, y = position
                    draw_glow.text((x + adj_x, y + adj_y), text, font=font, fill=glow_fill, embedded_color=True)
        
        # Apply blur for smoother glow
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=spread // 2))
        
        # Composite glow
        img_with_glow = Image.alpha_composite(image.convert('RGBA'), glow_layer)
        
        # Draw crisp text on top
        draw_final = ImageDraw.Draw(img_with_glow)
        draw_final.text(position, text, font=font, fill=text_color, embedded_color=True)
        
        return img_with_glow
    
    def apply_text_overlay(self, image: Image.Image, text: str) -> Image.Image:
        """Apply text overlay using configured method"""
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
        
        for i, line in enumerate(lines):
            # Get position for this line
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x, base_y = self.get_text_position(bbox, image.size)
            y = base_y + (i * line_spacing)
            
            if self.method == 'outline':
                draw = ImageDraw.Draw(result_image)
                self.draw_text_with_outline(draw, (x, y), line, font)
                
            elif self.method == 'shadow':
                draw = ImageDraw.Draw(result_image)
                self.draw_text_with_shadow(draw, (x, y), line, font)
                
            elif self.method == 'box':
                # For box method, we need to calculate box for all lines first
                if i == 0:  # Only draw box once for all lines
                    all_text = '\n'.join(lines)
                    result_image = self.draw_text_with_box(result_image, (x, y), all_text, font)
                    break  # Box method handles all lines at once
                    
            elif self.method == 'glow':
                result_image = self.draw_text_with_glow(result_image, (x, y), line, font)
                
            else:  # Default to simple text
                draw = ImageDraw.Draw(result_image)
                draw.text((x, y), line, font=font, fill=self.font_config.get('color', 'white'), embedded_color=True)
        
        return result_image.convert('RGB')


def test_text_overlay():
    """Test different text overlay methods"""
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
    
    overlay = TextOverlay(config)
    result = overlay.apply_text_overlay(test_image, "Czy wiesz, że najważniejsze jest niewidoczne dla oczu? 👁️")
    result.save('test_overlay.png')
    print("Test image saved as test_overlay.png")


if __name__ == "__main__":
    test_text_overlay()