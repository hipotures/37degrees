#!/usr/bin/env python3
"""Text overlay with Noto font that includes emoji support"""

from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Tuple, List
import os

class NotoTextOverlay:
    def __init__(self, config: Dict):
        """Initialize with text overlay configuration"""
        self.config = config
        self.method = config.get('method', 'outline')
        self.font_config = config.get('font', {})
        
    def get_font(self, scale: float = 1.0) -> ImageFont.FreeTypeFont:
        """Load font with emoji support"""
        font_size = int(self.font_config.get('size', 48) * scale)
        
        # Try to load Noto Sans with emoji fallback
        font_paths = [
            # Main text fonts
            "/usr/share/fonts/noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            # Fallback fonts with good unicode support
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except:
                    continue
                    
        # Ultimate fallback
        return ImageFont.load_default()
    
    def get_emoji_font(self, scale: float = 1.0) -> ImageFont.FreeTypeFont:
        """Load emoji-specific font"""
        font_size = int(self.font_config.get('size', 48) * scale)
        
        # Try emoji fonts
        emoji_paths = [
            "/usr/share/fonts/noto/NotoEmoji-Bold.ttf",
            "/usr/share/fonts/noto/NotoEmoji-Regular.ttf",
            "/usr/share/fonts/truetype/noto-emoji/NotoEmoji-Regular.ttf",
            # Symbola as fallback for emoji
            "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf",
            "/usr/share/fonts/truetype/symbola/Symbola.ttf",
        ]
        
        for font_path in emoji_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except:
                    continue
                    
        # Return main font as fallback
        return self.get_font(scale)
    
    def apply_gradient_overlay(self, image: Image.Image) -> Image.Image:
        """Apply darkening gradient to top of image"""
        img_copy = image.copy()
        gradient_config = self.config.get('gradient', {})
        
        width, height = image.size
        gradient_height = int(height * gradient_config.get('height_percent', 40) / 100)
        
        gradient = Image.new('RGBA', (width, gradient_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        start_opacity = int(255 * gradient_config.get('start_opacity', 0.7))
        end_opacity = int(255 * gradient_config.get('end_opacity', 0.0))
        
        for y in range(gradient_height):
            opacity = int(start_opacity - (start_opacity - end_opacity) * (y / gradient_height))
            draw.rectangle([(0, y), (width, y + 1)], fill=(0, 0, 0, opacity))
        
        img_copy.paste(gradient, (0, 0), gradient)
        return img_copy
    
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
    
    def draw_text_with_outline(self, draw: ImageDraw.Draw, position: Tuple[int, int], 
                              text: str, font: ImageFont.FreeTypeFont, emoji_font: ImageFont.FreeTypeFont):
        """Draw text with outline effect, using emoji font for emoji characters"""
        x, y = position
        font_color = self.font_config.get('color', 'white')
        
        if self.method == 'outline':
            outline_config = self.config.get('outline', {})
            outline_color = outline_config.get('color', 'black')
            outline_width = outline_config.get('width', 3)
            
            # Check if text contains emoji
            has_emoji = any(ord(char) > 0x1F000 for char in text)
            
            if has_emoji and emoji_font != font:
                # For text with emoji, we need to handle character by character
                current_x = x
                for char in text:
                    # Determine which font to use
                    if ord(char) > 0x1F000 or char in ['👁', '️', '🌟']:
                        use_font = emoji_font
                    else:
                        use_font = font
                    
                    # Get character width
                    bbox = use_font.getbbox(char)
                    char_width = bbox[2] - bbox[0]
                    
                    # Draw outline
                    for dx in range(-outline_width, outline_width + 1):
                        for dy in range(-outline_width, outline_width + 1):
                            if dx != 0 or dy != 0:
                                draw.text((current_x + dx, y + dy), char, font=use_font, fill=outline_color)
                    
                    # Draw character
                    draw.text((current_x, y), char, font=use_font, fill=font_color)
                    current_x += char_width
            else:
                # No emoji, use regular drawing
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
                
                draw.text((x, y), text, font=font, fill=font_color)
                
        elif self.method == 'shadow':
            shadow_config = self.config.get('shadow', {})
            shadow_color = shadow_config.get('color', 'rgba(0, 0, 0, 0.8)')
            offset_x = shadow_config.get('offset_x', 2)
            offset_y = shadow_config.get('offset_y', 2)
            
            draw.text((x + offset_x, y + offset_y), text, font=font, fill=shadow_color)
            draw.text((x, y), text, font=font, fill=font_color)
        else:
            draw.text((x, y), text, font=font, fill=font_color)
    
    def apply_text_overlay(self, image: Image.Image, text: str) -> Image.Image:
        """Apply text overlay to image"""
        result_image = image.copy()
        
        if self.method == 'gradient':
            result_image = self.apply_gradient_overlay(result_image)
        
        font = self.get_font()
        emoji_font = self.get_emoji_font()
        
        draw = ImageDraw.Draw(result_image)
        
        alignment = self.font_config.get('alignment', 'center')
        line_height = self.font_config.get('line_height', 1.4)
        
        lines = self.wrap_text(text, int(image.width * 0.9), font)
        
        line_bbox = font.getbbox("Ay")
        line_height_px = int((line_bbox[3] - line_bbox[1]) * line_height)
        total_height = len(lines) * line_height_px
        
        start_y = int(image.height * 0.15) - (total_height // 2)
        
        for i, line in enumerate(lines):
            line_bbox = font.getbbox(line)
            line_width = line_bbox[2] - line_bbox[0]
            
            if alignment == 'center':
                x = (image.width - line_width) // 2
            elif alignment == 'left':
                x = int(image.width * 0.05)
            else:
                x = int(image.width * 0.95) - line_width
            
            y = start_y + (i * line_height_px)
            
            self.draw_text_with_outline(draw, (x, y), line, font, emoji_font)
        
        return result_image


def test_noto_overlay():
    """Test Noto text overlay with emoji"""
    from PIL import Image
    
    # List available fonts
    print("Checking available emoji fonts:")
    emoji_paths = [
        "/usr/share/fonts/noto/NotoEmoji-Bold.ttf",
        "/usr/share/fonts/noto/NotoEmoji-Regular.ttf",
        "/usr/share/fonts/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/truetype/noto-emoji/NotoEmoji-Regular.ttf",
        "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf",
        "/usr/share/fonts/truetype/symbola/Symbola.ttf",
    ]
    
    for path in emoji_paths:
        if os.path.exists(path):
            print(f"Found: {path}")
    
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
    
    overlay = NotoTextOverlay(config)
    result = overlay.apply_text_overlay(test_image, "Czy wiesz, że najważniejsze jest niewidoczne dla oczu? 👁️")
    result.save('test_noto_overlay.png')
    print("\nTest image saved as test_noto_overlay.png")


if __name__ == "__main__":
    test_noto_overlay()