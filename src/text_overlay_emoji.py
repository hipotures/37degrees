#!/usr/bin/env python3
"""Text overlay with proper emoji support using pilmoji"""

from PIL import Image, ImageDraw, ImageFont
# from pilmoji import Pilmoji  # Compatibility issues, using alternative approach
from typing import Dict, Tuple, List
import os

class EmojiTextOverlay:
    def __init__(self, config: Dict):
        """Initialize with text overlay configuration"""
        self.config = config
        self.method = config.get('method', 'outline')
        self.font_config = config.get('font', {})
        
    def get_font(self, scale: float = 1.0) -> ImageFont.FreeTypeFont:
        """Load font with specified settings"""
        font_family = self.font_config.get('family', 'Arial')
        font_size = int(self.font_config.get('size', 48) * scale)
        font_weight = self.font_config.get('weight', 'bold')
        
        # Try to load system font - prioritize fonts with good Unicode support
        font_paths = [
            # Noto Sans has excellent Unicode coverage
            "/usr/share/fonts/noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            # DejaVu also has good Unicode support
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            f"/usr/share/fonts/truetype/liberation/Liberation{font_family}-{font_weight.capitalize()}.ttf",
            f"/usr/share/fonts/truetype/dejavu/DejaVu{font_family}-{font_weight.capitalize()}.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Fallback
        ]
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, font_size)
            except:
                continue
                
        # Ultimate fallback
        return ImageFont.load_default()
    
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
        
        # Calculate X position
        if alignment == 'center':
            x = (width - text_width) // 2
        elif alignment == 'left':
            x = int(width * 0.05)
        else:  # right
            x = int(width * 0.95) - text_width
        
        # Y position - upper third of image
        y = int(height * 0.15)
        
        return x, y
    
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
    
    def draw_text_with_outline_pilmoji(self, image: Image.Image, position: Tuple[int, int], 
                                      text: str, font: ImageFont.FreeTypeFont):
        """Draw text with outline effect using Pilmoji for emoji support"""
        x, y = position
        font_color = self.font_config.get('color', 'white')
        
        if self.method == 'outline':
            outline_config = self.config.get('outline', {})
            outline_color = outline_config.get('color', 'black')
            outline_width = outline_config.get('width', 3)
            
            # Draw outline first
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        with Pilmoji(image) as pilmoji:
                            pilmoji.text((x + dx, y + dy), text, font=font, fill=outline_color)
            
            # Draw main text
            with Pilmoji(image) as pilmoji:
                pilmoji.text((x, y), text, font=font, fill=font_color)
                
        elif self.method == 'shadow':
            shadow_config = self.config.get('shadow', {})
            shadow_color = shadow_config.get('color', 'rgba(0, 0, 0, 0.8)')
            offset_x = shadow_config.get('offset_x', 2)
            offset_y = shadow_config.get('offset_y', 2)
            
            # Draw shadow
            with Pilmoji(image) as pilmoji:
                pilmoji.text((x + offset_x, y + offset_y), text, font=font, fill=shadow_color)
            
            # Draw main text
            with Pilmoji(image) as pilmoji:
                pilmoji.text((x, y), text, font=font, fill=font_color)
        else:
            # Default - just draw text
            with Pilmoji(image) as pilmoji:
                pilmoji.text((x, y), text, font=font, fill=font_color)
    
    def apply_text_overlay(self, image: Image.Image, text: str) -> Image.Image:
        """Apply text overlay to image with emoji support"""
        # Create a copy to avoid modifying original
        result_image = image.copy()
        
        # Apply method-specific background
        if self.method == 'gradient':
            result_image = self.apply_gradient_overlay(result_image)
        
        # Load font
        font = self.get_font()
        
        # Get text configuration
        alignment = self.font_config.get('alignment', 'center')
        line_height = self.font_config.get('line_height', 1.4)
        
        # Wrap text
        lines = self.wrap_text(text, int(image.width * 0.9), font)
        
        # Calculate total text height
        line_bbox = font.getbbox("Ay")
        line_height_px = int((line_bbox[3] - line_bbox[1]) * line_height)
        total_height = len(lines) * line_height_px
        
        # Starting Y position (upper third of image)
        start_y = int(image.height * 0.15) - (total_height // 2)
        
        # Draw each line with emoji support
        for i, line in enumerate(lines):
            # Calculate line width for alignment
            line_bbox = font.getbbox(line)
            line_width = line_bbox[2] - line_bbox[0]
            
            # Calculate X position based on alignment
            if alignment == 'center':
                x = (image.width - line_width) // 2
            elif alignment == 'left':
                x = int(image.width * 0.05)
            else:  # right
                x = int(image.width * 0.95) - line_width
            
            y = start_y + (i * line_height_px)
            
            # Draw text with emoji support
            self.draw_text_with_outline_pilmoji(result_image, (x, y), line, font)
        
        return result_image
    
    def apply_box_overlay(self, image: Image.Image, text_bounds: Tuple[int, int, int, int]) -> Image.Image:
        """Apply semi-transparent box behind text"""
        box_config = self.config.get('box', {})
        color = box_config.get('color', 'rgba(0, 0, 0, 0.5)')
        padding = box_config.get('padding', 20)
        border_radius = box_config.get('border_radius', 15)
        
        # Expand bounds by padding
        x1, y1, x2, y2 = text_bounds
        x1 -= padding
        y1 -= padding
        x2 += padding
        y2 += padding
        
        # Create overlay
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Draw rounded rectangle
        if border_radius > 0:
            draw.rounded_rectangle([x1, y1, x2, y2], radius=border_radius, fill=color)
        else:
            draw.rectangle([x1, y1, x2, y2], fill=color)
        
        # Composite with original
        return Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')


def test_emoji_overlay():
    """Test emoji text overlay"""
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
    result = overlay.apply_text_overlay(test_image, "Czy wiesz, że najważniejsze jest niewidoczne dla oczu? 👁️")
    result.save('test_emoji_overlay.png')
    print("Test image with emoji saved as test_emoji_overlay.png")


if __name__ == "__main__":
    test_emoji_overlay()