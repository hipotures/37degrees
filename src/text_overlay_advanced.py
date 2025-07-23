#!/usr/bin/env python3
"""Advanced text overlay with emoji support"""

from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Tuple, Optional, List
import os
import re
import unicodedata

class AdvancedTextOverlay:
    def __init__(self, config: Dict):
        """Initialize with text overlay configuration"""
        self.config = config
        self.method = config.get('method', 'outline')
        self.font_config = config.get('font', {})
        
    def get_fonts(self, scale: float = 1.0) -> Tuple[ImageFont.FreeTypeFont, Optional[ImageFont.FreeTypeFont]]:
        """Load main font and emoji font"""
        font_size = int(self.font_config.get('size', 48) * scale)
        
        # Main font - prioritize fonts with good Unicode support
        main_font_paths = [
            "/usr/share/fonts/noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
        
        main_font = None
        for font_path in main_font_paths:
            try:
                main_font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
        
        if not main_font:
            main_font = ImageFont.load_default()
            
        # Emoji font
        emoji_font = None
        emoji_font_paths = [
            "/usr/share/fonts/noto/NotoColorEmoji.ttf",
            "/usr/share/fonts/truetype/noto-emoji/NotoColorEmoji.ttf",
            "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf",
        ]
        
        for font_path in emoji_font_paths:
            try:
                # Color emoji fonts need special handling
                if "Color" in font_path:
                    # For color emoji, we might need to use a different approach
                    # For now, fall back to regular emoji
                    pass
                else:
                    emoji_font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
                
        return main_font, emoji_font
    
    def is_emoji(self, char: str) -> bool:
        """Check if a character is an emoji"""
        # Check Unicode categories
        category = unicodedata.category(char)
        if category in ['So', 'Sk']:  # Symbol, other; Symbol, modifier
            return True
        
        # Check specific emoji ranges
        code_point = ord(char)
        emoji_ranges = [
            (0x1F300, 0x1F6FF),  # Emoticons, Transport, etc
            (0x1F700, 0x1F77F),  # Alchemical Symbols
            (0x1F780, 0x1F7FF),  # Geometric Shapes Extended
            (0x1F800, 0x1F8FF),  # Supplemental Arrows-C
            (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            (0x1FA00, 0x1FA6F),  # Chess Symbols
            (0x1FA70, 0x1FAFF),  # Symbols and Pictographs Extended-A
            (0x2600, 0x26FF),    # Miscellaneous Symbols
            (0x2700, 0x27BF),    # Dingbats
            (0x2B50, 0x2B55),    # Stars
        ]
        
        for start, end in emoji_ranges:
            if start <= code_point <= end:
                return True
                
        return False
    
    def render_text_with_emoji(self, draw: ImageDraw.Draw, position: Tuple[int, int], 
                              text: str, main_font: ImageFont.FreeTypeFont, 
                              emoji_font: Optional[ImageFont.FreeTypeFont] = None,
                              color: str = "white", outline_color: str = "black",
                              outline_width: int = 3):
        """Render text with emoji support"""
        x, y = position
        current_x = x
        
        # If no emoji font, just use main font for everything
        if not emoji_font:
            self.draw_text_with_outline(draw, position, text, main_font, color, outline_color, outline_width)
            return
        
        # Process each character
        i = 0
        while i < len(text):
            char = text[i]
            
            # Check for emoji sequences (like 👁️)
            if i + 1 < len(text) and ord(text[i + 1]) in [0xFE0E, 0xFE0F]:
                # Variation selector
                char = text[i:i+2]
                i += 2
            else:
                i += 1
            
            # Determine which font to use
            if self.is_emoji(char[0]):
                font = emoji_font or main_font
            else:
                font = main_font
            
            # Get character width
            bbox = font.getbbox(char)
            char_width = bbox[2] - bbox[0]
            
            # Draw character with outline
            if self.method == 'outline' and outline_width > 0:
                # Draw outline
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((current_x + dx, y + dy), char, font=font, fill=outline_color)
            
            # Draw main text
            draw.text((current_x, y), char, font=font, fill=color)
            
            # Move to next character position
            current_x += char_width
    
    def draw_text_with_outline(self, draw: ImageDraw.Draw, position: Tuple[int, int], 
                              text: str, font: ImageFont.FreeTypeFont,
                              color: str = "white", outline_color: str = "black",
                              outline_width: int = 3):
        """Draw text with outline effect"""
        x, y = position
        
        # Draw outline
        if outline_width > 0:
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=color)
    
    def apply_text_overlay(self, image: Image.Image, text: str) -> Image.Image:
        """Apply text overlay to image"""
        # Create a copy to avoid modifying original
        result_image = image.copy()
        
        # Get fonts
        main_font, emoji_font = self.get_fonts()
        
        # Apply method-specific background
        if self.method == 'gradient':
            result_image = self.apply_gradient_overlay(result_image)
        
        # Create drawing context
        draw = ImageDraw.Draw(result_image)
        
        # Get text configuration
        font_color = self.font_config.get('color', 'white')
        alignment = self.font_config.get('alignment', 'center')
        line_height = self.font_config.get('line_height', 1.4)
        
        # Wrap text
        lines = self.wrap_text(text, int(image.width * 0.9), main_font)
        
        # Calculate total text height
        line_bbox = main_font.getbbox("Ay")
        line_height_px = int((line_bbox[3] - line_bbox[1]) * line_height)
        total_height = len(lines) * line_height_px
        
        # Starting Y position (upper third of image)
        start_y = int(image.height * 0.15) - (total_height // 2)
        
        # Draw each line
        for i, line in enumerate(lines):
            # Calculate line width for alignment
            line_bbox = main_font.getbbox(line)
            line_width = line_bbox[2] - line_bbox[0]
            
            # Calculate X position based on alignment
            if alignment == 'center':
                x = (image.width - line_width) // 2
            elif alignment == 'left':
                x = int(image.width * 0.05)
            else:  # right
                x = int(image.width * 0.95) - line_width
            
            y = start_y + (i * line_height_px)
            
            # Apply method-specific drawing
            if self.method == 'outline':
                outline_config = self.config.get('outline', {})
                outline_color = outline_config.get('color', 'black')
                outline_width = outline_config.get('width', 3)
                
                # Use advanced rendering with emoji support
                self.render_text_with_emoji(draw, (x, y), line, main_font, emoji_font,
                                          font_color, outline_color, outline_width)
                
            elif self.method == 'shadow':
                # Shadow effect
                shadow_config = self.config.get('shadow', {})
                shadow_color = shadow_config.get('color', 'rgba(0, 0, 0, 0.8)')
                offset_x = shadow_config.get('offset_x', 2)
                offset_y = shadow_config.get('offset_y', 2)
                
                # Draw shadow
                draw.text((x + offset_x, y + offset_y), line, font=main_font, fill=shadow_color)
                # Draw main text
                draw.text((x, y), line, font=main_font, fill=font_color)
                
            else:
                # Default - just draw text
                draw.text((x, y), line, font=main_font, fill=font_color)
        
        return result_image
    
    def wrap_text(self, text: str, max_width: int, font: ImageFont.FreeTypeFont) -> List[str]:
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