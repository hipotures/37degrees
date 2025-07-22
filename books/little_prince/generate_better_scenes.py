#!/usr/bin/env python3
"""
Generate better scene backgrounds with proper contrast for text overlay
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random

# Scene definitions with better contrast considerations
SCENES = [
    {
        "name": "01_hook_invisible",
        "bg_color": "#1a1a2e",  # Dark blue background
        "accent_color": "#eab308",  # Yellow accent
        "overlay_color": "rgba(26, 26, 46, 0.85)",  # Dark semi-transparent overlay
        "elements": ["eye", "stars", "heart"]
    },
    {
        "name": "02_intro_book", 
        "bg_color": "#0f172a",  # Dark slate
        "accent_color": "#3b82f6",  # Blue accent
        "overlay_color": "rgba(15, 23, 42, 0.85)",
        "elements": ["book", "stars"]
    },
    {
        "name": "03_plot_pilot",
        "bg_color": "#134e4a",  # Dark teal
        "accent_color": "#fbbf24",  # Amber accent
        "overlay_color": "rgba(19, 78, 74, 0.85)",
        "elements": ["airplane", "desert"]
    },
    {
        "name": "04_plot_meeting",
        "bg_color": "#1e293b",  # Dark gray-blue
        "accent_color": "#f59e0b",  # Orange accent
        "overlay_color": "rgba(30, 41, 59, 0.85)",
        "elements": ["boy", "scarf"]
    },
    {
        "name": "05_theme_adults",
        "bg_color": "#312e81",  # Dark indigo
        "accent_color": "#10b981",  # Emerald accent
        "overlay_color": "rgba(49, 46, 129, 0.85)",
        "elements": ["keyholes", "figures"]
    },
    {
        "name": "06_quote_heart",
        "bg_color": "#7c2d12",  # Dark orange
        "accent_color": "#ec4899",  # Pink accent
        "overlay_color": "rgba(124, 45, 18, 0.85)",
        "elements": ["heart", "stars"]
    },
    {
        "name": "07_why_read_wisdom",
        "bg_color": "#14532d",  # Dark green
        "accent_color": "#a78bfa",  # Purple accent
        "overlay_color": "rgba(20, 83, 45, 0.85)",
        "elements": ["books", "light"]
    },
    {
        "name": "08_cta_rose",
        "bg_color": "#881337",  # Dark rose
        "accent_color": "#fde047",  # Light yellow accent
        "overlay_color": "rgba(136, 19, 55, 0.85)",
        "elements": ["rose", "glass_dome", "stars"]
    }
]

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_text_overlay_area(draw, width, height):
    """Create a semi-transparent overlay area for text"""
    # Create rounded rectangle for text area
    margin = 100
    top = height // 3
    bottom = 2 * height // 3
    
    # Draw rounded rectangle with transparency
    overlay_rect = [margin, top, width - margin, bottom]
    draw.rounded_rectangle(overlay_rect, radius=30, fill=(0, 0, 0, 180))
    
    # Add subtle border
    draw.rounded_rectangle(overlay_rect, radius=30, outline=(255, 255, 255, 100), width=3)

def draw_eye(draw, x, y, size, color):
    """Draw a stylized eye"""
    # Eye outline
    draw.ellipse([x-size, y-size//2, x+size, y+size//2], outline=color, width=3)
    # Iris
    draw.ellipse([x-size//3, y-size//4, x+size//3, y+size//4], fill=color)
    # Lashes
    for angle in [-30, -15, 0, 15, 30]:
        x2 = x + size * 1.2 * (angle/30)
        y2 = y - size * 0.7
        draw.line([x + size * (angle/30), y - size//2, x2, y2], fill=color, width=2)

def draw_book(draw, x, y, size, color):
    """Draw a simple book icon"""
    book_width = size
    book_height = size * 1.3
    
    # Book cover
    draw.rectangle([x-book_width//2, y-book_height//2, x+book_width//2, y+book_height//2], 
                   outline=color, width=3)
    # Spine
    draw.line([x-book_width//2+10, y-book_height//2, x-book_width//2+10, y+book_height//2], 
              fill=color, width=3)
    # Pages
    for i in range(3):
        offset = i * 5
        draw.line([x-book_width//2+15+offset, y-book_height//2+5, 
                   x+book_width//2-5, y-book_height//2+5+offset], 
                  fill=color, width=1)

def draw_airplane(draw, x, y, size, color):
    """Draw a simple airplane"""
    # Body
    draw.ellipse([x-size, y-size//4, x+size, y+size//4], outline=color, width=3)
    # Wings
    draw.polygon([(x, y-size//2), (x-size*1.5, y), (x, y+size//4)], outline=color, width=2)
    draw.polygon([(x, y-size//2), (x+size*1.5, y), (x, y+size//4)], outline=color, width=2)
    # Tail
    draw.polygon([(x+size*0.8, y-size//4), (x+size, y-size//2), (x+size, y)], outline=color, width=2)

def draw_heart(draw, x, y, size, color):
    """Draw a heart shape"""
    # Create heart using two circles and a triangle
    # Left bump
    draw.ellipse([x-size//2, y-size//2, x, y], fill=color)
    # Right bump
    draw.ellipse([x, y-size//2, x+size//2, y], fill=color)
    # Bottom triangle
    draw.polygon([(x-size//2, y-size//4), (x+size//2, y-size//4), (x, y+size//2)], fill=color)

def draw_rose(draw, x, y, size, color):
    """Draw a stylized rose"""
    # Petals (concentric circles)
    for i in range(3):
        petal_size = size - i * (size//4)
        draw.ellipse([x-petal_size, y-petal_size, x+petal_size, y+petal_size], 
                     outline=color, width=2)
    # Center
    draw.ellipse([x-size//4, y-size//4, x+size//4, y+size//4], fill=color)
    # Stem
    draw.line([x, y+size, x, y+size*2], fill=color, width=3)
    # Leaf
    draw.ellipse([x+5, y+size*1.3, x+size//2, y+size*1.6], outline=color, width=2)

def draw_stars(draw, width, height, count, color):
    """Draw random stars"""
    for _ in range(count):
        x = random.randint(50, width-50)
        y = random.randint(50, height-50)
        size = random.randint(3, 8)
        
        # Draw 4-pointed star
        draw.line([x-size, y, x+size, y], fill=color, width=2)
        draw.line([x, y-size, x, y+size], fill=color, width=2)

def create_scene(scene_info, width=1080, height=1920):
    """Create a scene with better contrast for text overlay"""
    # Create image with background color
    img = Image.new('RGB', (width, height), scene_info["bg_color"])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Add gradient overlay for depth
    for y in range(height):
        alpha = int(255 * (y / height) * 0.3)  # Gradient intensity
        draw.rectangle([(0, y), (width, y+1)], fill=(0, 0, 0, alpha))
    
    # Draw decorative elements
    accent_color = hex_to_rgb(scene_info["accent_color"])
    
    if "stars" in scene_info["elements"]:
        draw_stars(draw, width, height, 15, accent_color + (150,))
    
    # Draw main elements
    center_x, center_y = width // 2, height // 2
    
    if "eye" in scene_info["elements"]:
        draw_eye(draw, center_x, center_y - 200, 80, accent_color)
    
    if "book" in scene_info["elements"]:
        draw_book(draw, center_x, center_y - 200, 100, accent_color)
    
    if "airplane" in scene_info["elements"]:
        draw_airplane(draw, center_x - 200, center_y - 300, 60, accent_color)
    
    if "heart" in scene_info["elements"]:
        draw_heart(draw, center_x, center_y - 200, 80, accent_color)
    
    if "rose" in scene_info["elements"]:
        draw_rose(draw, center_x, center_y - 300, 60, accent_color)
    
    if "keyholes" in scene_info["elements"]:
        # Draw three keyholes
        for i, x_offset in enumerate([-200, 0, 200]):
            x = center_x + x_offset
            y = center_y - 200
            # Keyhole circle
            draw.ellipse([x-40, y-40, x+40, y+40], outline=accent_color, width=3)
            # Keyhole bottom
            draw.rectangle([x-15, y, x+15, y+60], fill=accent_color)
    
    if "books" in scene_info["elements"]:
        # Stack of books
        for i in range(4):
            y_offset = center_y - 300 + i * 30
            draw.rectangle([center_x-80, y_offset, center_x+80, y_offset+25], 
                         outline=accent_color, width=2)
    
    # Add text overlay area
    create_text_overlay_area(draw, width, height)
    
    # Apply subtle blur to background elements
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    
    # Redraw the text overlay area on top of blur
    draw = ImageDraw.Draw(img, 'RGBA')
    create_text_overlay_area(draw, width, height)
    
    return img

def main():
    """Generate all scenes with better contrast"""
    scenes_dir = Path("scenes_v2")
    scenes_dir.mkdir(exist_ok=True)
    
    print("Generating improved scenes with better text contrast...")
    
    for i, scene in enumerate(SCENES, 1):
        print(f"Creating scene {i}: {scene['name']}")
        img = create_scene(scene)
        img.save(scenes_dir / f"{scene['name']}.png")
    
    print(f"\n✅ Generated {len(SCENES)} improved scenes in {scenes_dir}/")

if __name__ == "__main__":
    main()