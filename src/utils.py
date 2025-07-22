import os
import hashlib
from pathlib import Path
from typing import Tuple, Union, Optional
from PIL import Image, ImageDraw


def ensure_dir(path: Path) -> None:
    """Ensure directory exists, create if it doesn't"""
    path.mkdir(parents=True, exist_ok=True)


def get_font_path(font_family: str, weight: str = 'regular') -> str:
    """Get font file path based on family and weight"""
    font_dir = Path("shared_assets/fonts")
    
    # Map common font names to file names
    font_files = {
        'Montserrat': {
            'regular': 'Montserrat-Regular.ttf',
            'bold': 'Montserrat-Bold.ttf',
            'light': 'Montserrat-Light.ttf'
        },
        'Roboto': {
            'regular': 'Roboto-Regular.ttf',
            'bold': 'Roboto-Bold.ttf',
            'light': 'Roboto-Light.ttf'
        },
        'OpenSans': {
            'regular': 'OpenSans-Regular.ttf',
            'bold': 'OpenSans-Bold.ttf',
            'light': 'OpenSans-Light.ttf'
        }
    }
    
    # Try to find the font file
    if font_family in font_files and weight in font_files[font_family]:
        font_path = font_dir / font_files[font_family][weight]
        if font_path.exists():
            return str(font_path)
    
    # Fallback to system fonts
    system_fonts = [
        f"/usr/share/fonts/truetype/{font_family.lower()}/{font_family}-{weight.capitalize()}.ttf",
        f"/System/Library/Fonts/{font_family}.ttc",
        f"C:\\Windows\\Fonts\\{font_family.lower()}.ttf"
    ]
    
    for path in system_fonts:
        if os.path.exists(path):
            return path
    
    # If no font found, return None (will use default)
    return None


def calculate_text_position(position_config: dict, video_width: int, video_height: int) -> Tuple[int, int]:
    """Calculate absolute position from configuration"""
    x = position_config.get('x', 'center')
    y = position_config.get('y', 'center')
    
    # Handle x position
    if isinstance(x, str):
        if x == 'center':
            x = video_width // 2
        elif x == 'left':
            x = 100
        elif x == 'right':
            x = video_width - 100
    
    # Handle y position
    if isinstance(y, str):
        if y == 'center':
            y = video_height // 2
        elif y == 'top':
            y = 100
        elif y == 'bottom':
            y = video_height - 100
    
    return (int(x), int(y))


def add_text_shadow(draw: ImageDraw, text: str, position: Tuple[int, int], font, 
                   shadow_color: str, shadow_offset: int, text_color: str) -> None:
    """Add shadow effect to text"""
    # Draw shadow
    shadow_pos = (position[0] + shadow_offset, position[1] + shadow_offset)
    draw.text(shadow_pos, text, font=font, fill=shadow_color)
    
    # Draw main text
    draw.text(position, text, font=font, fill=text_color)


def generate_background_prompt_hash(prompt: str) -> str:
    """Generate unique hash for background prompt"""
    return hashlib.md5(prompt.encode()).hexdigest()[:12]


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient(size: Tuple[int, int], start_color: Union[str, Tuple], 
                   end_color: Union[str, Tuple], direction: str = 'vertical') -> Image.Image:
    """Create gradient image"""
    width, height = size
    
    # Convert colors to RGB if they're hex
    if isinstance(start_color, str):
        start_color = hex_to_rgb(start_color)
    if isinstance(end_color, str):
        end_color = hex_to_rgb(end_color)
    
    # Create new image
    gradient = Image.new('RGB', size)
    draw = ImageDraw.Draw(gradient)
    
    if direction == 'vertical':
        for y in range(height):
            ratio = y / height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    elif direction == 'horizontal':
        for x in range(width):
            ratio = x / width
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            draw.line([(x, 0), (x, height)], fill=(r, g, b))
    
    elif direction == 'diagonal':
        for y in range(height):
            for x in range(width):
                ratio = (x + y) / (width + height)
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
                draw.point((x, y), fill=(r, g, b))
    
    return gradient


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes}m {seconds:.1f}s"


def load_trending_audio_list() -> list:
    """Load list of trending audio (placeholder for actual API)"""
    # In production, this would fetch from TikTok API
    return [
        {
            'id': 'trending_001',
            'name': 'Dramatic Classical Mix',
            'duration': 30,
            'genre': 'classical'
        },
        {
            'id': 'trending_002', 
            'name': 'Epic Orchestral',
            'duration': 45,
            'genre': 'orchestral'
        }
    ]


def get_video_metadata(book_info: dict, template: dict) -> dict:
    """Generate metadata for video file"""
    return {
        'title': f"{book_info['title']} - {template['series_name']}",
        'artist': '37 stopni',
        'album': template['series_name'],
        'genre': 'Educational',
        'comment': f"Book review: {book_info['title']} by {book_info['author']}"
    }


def validate_yaml_structure(yaml_data: dict, required_fields: list) -> Tuple[bool, Optional[str]]:
    """Validate YAML file has required structure"""
    for field in required_fields:
        if field not in yaml_data:
            return False, f"Missing required field: {field}"
    return True, None


def estimate_video_size(duration: float, width: int, height: int, fps: int) -> float:
    """Estimate final video file size in MB"""
    # Rough estimation: bitrate * duration
    bitrate = 2000000  # 2 Mbps for 1080p
    size_bytes = (bitrate * duration) / 8
    size_mb = size_bytes / (1024 * 1024)
    return size_mb