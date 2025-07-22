#!/usr/bin/env python3
"""
Generate scene images for Little Prince TikTok video
Each slide will have its own scene image
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

# Scene definitions based on slides
SCENES = [
    {
        "name": "01_hook_invisible",
        "description": "Abstract eye with stars and heart symbols, dreamy atmosphere",
        "colors": ["#FFE4E1", "#4169E1", "#FFD700"],
        "elements": ["eye", "stars", "heart", "clouds"]
    },
    {
        "name": "02_intro_book",
        "description": "Book opening with stars flowing out, magical atmosphere",
        "colors": ["#F0E68C", "#4682B4", "#FFA500"],
        "elements": ["open_book", "stars", "sparkles"]
    },
    {
        "name": "03_story_desert",
        "description": "Desert scene with crashed plane and small figure",
        "colors": ["#F4A460", "#87CEEB", "#FFE4B5"],
        "elements": ["desert", "plane", "boy_silhouette", "stars"]
    },
    {
        "name": "04_character_planets",
        "description": "Multiple small planets connected by dotted lines",
        "colors": ["#9370DB", "#00CED1", "#FF69B4"],
        "elements": ["planets", "paths", "stars"]
    },
    {
        "name": "05_theme_adults",
        "description": "Three planets with silhouettes: king, businessman, vain man",
        "colors": ["#708090", "#2F4F4F", "#696969"],
        "elements": ["three_planets", "adult_figures", "question_marks"]
    },
    {
        "name": "06_quote_heart",
        "description": "Large heart shape with stars inside, soft glow",
        "colors": ["#FF1493", "#FFB6C1", "#FFF0F5"],
        "elements": ["heart", "stars", "soft_glow"]
    },
    {
        "name": "07_why_read_wisdom",
        "description": "Stack of books transforming into flying birds",
        "colors": ["#32CD32", "#00FA9A", "#98FB98"],
        "elements": ["books", "birds", "transformation"]
    },
    {
        "name": "08_cta_rose",
        "description": "Beautiful rose under glass dome with sparkles",
        "colors": ["#DC143C", "#FF69B4", "#FFE4E1"],
        "elements": ["rose", "glass_dome", "sparkles"]
    }
]

def create_gradient_background(width, height, color1, color2):
    """Create a gradient background"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        ratio = y / height
        r = int(int(color1[1:3], 16) * (1-ratio) + int(color2[1:3], 16) * ratio)
        g = int(int(color1[3:5], 16) * (1-ratio) + int(color2[3:5], 16) * ratio)
        b = int(int(color1[5:7], 16) * (1-ratio) + int(color2[5:7], 16) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return img

def draw_stars(draw, width, height, count=20):
    """Draw simple stars on the image"""
    import random
    for _ in range(count):
        x = random.randint(10, width-10)
        y = random.randint(10, height-10)
        size = random.randint(2, 5)
        # Draw star as cross
        draw.line([(x-size, y), (x+size, y)], fill="white", width=2)
        draw.line([(x, y-size), (x, y+size)], fill="white", width=2)

def generate_scene_1(width, height):
    """Hook scene - Eye with invisible concept"""
    img = create_gradient_background(width, height, "#FFE4E1", "#4169E1")
    draw = ImageDraw.Draw(img)
    
    # Draw large eye outline
    eye_x, eye_y = width//2, height//2
    eye_width, eye_height = 300, 150
    draw.ellipse([eye_x-eye_width//2, eye_y-eye_height//2, 
                  eye_x+eye_width//2, eye_y+eye_height//2], 
                 outline="white", width=5)
    
    # Draw iris
    draw.ellipse([eye_x-50, eye_y-50, eye_x+50, eye_y+50], 
                 fill="#4169E1", outline="white", width=3)
    
    # Draw heart inside pupil
    heart_points = [(eye_x, eye_y-20), (eye_x-20, eye_y-35), 
                    (eye_x-30, eye_y-25), (eye_x, eye_y+10),
                    (eye_x+30, eye_y-25), (eye_x+20, eye_y-35)]
    draw.polygon(heart_points, fill="#FFD700")
    
    draw_stars(draw, width, height)
    return img

def generate_scene_2(width, height):
    """Intro scene - Magical book"""
    img = create_gradient_background(width, height, "#F0E68C", "#4682B4")
    draw = ImageDraw.Draw(img)
    
    # Draw open book
    book_x, book_y = width//2, height*2//3
    book_width, book_height = 400, 250
    
    # Left page
    draw.polygon([(book_x-book_width//2, book_y-book_height//2),
                  (book_x, book_y-book_height//2-20),
                  (book_x, book_y+book_height//2),
                  (book_x-book_width//2, book_y+book_height//2)],
                 fill="white", outline="#8B4513", width=3)
    
    # Right page
    draw.polygon([(book_x, book_y-book_height//2-20),
                  (book_x+book_width//2, book_y-book_height//2),
                  (book_x+book_width//2, book_y+book_height//2),
                  (book_x, book_y+book_height//2)],
                 fill="white", outline="#8B4513", width=3)
    
    # Stars flowing out
    for i in range(30):
        x = book_x + (i-15) * 20
        y = book_y - book_height//2 - i * 10
        draw_stars(draw, width, height//2, count=1)
    
    return img

def generate_scene_3(width, height):
    """Desert scene with plane"""
    img = create_gradient_background(width, height, "#F4A460", "#87CEEB")
    draw = ImageDraw.Draw(img)
    
    # Draw desert dunes
    for i in range(3):
        y_base = height * 2//3 + i * 50
        draw.arc([(i*300, y_base), ((i+1)*300+200, y_base+100)], 
                 start=0, end=180, fill="#DEB887", width=5)
    
    # Draw crashed plane (simple triangle)
    plane_x, plane_y = width//3, height*2//3
    draw.polygon([(plane_x, plane_y),
                  (plane_x+100, plane_y+30),
                  (plane_x+80, plane_y+50),
                  (plane_x-20, plane_y+40)],
                 fill="#708090", outline="black")
    
    # Draw small boy silhouette
    boy_x, boy_y = width*2//3, height//2
    # Head
    draw.ellipse([boy_x-15, boy_y-15, boy_x+15, boy_y+15], fill="#4169E1")
    # Body
    draw.rectangle([boy_x-10, boy_y+15, boy_x+10, boy_y+40], fill="#4169E1")
    
    draw_stars(draw, width, height//3, count=15)
    return img

def generate_scene_4(width, height):
    """Multiple planets scene"""
    img = create_gradient_background(width, height, "#9370DB", "#00CED1")
    draw = ImageDraw.Draw(img)
    
    # Draw multiple small planets
    planets = [
        (width//4, height//4, 60),
        (width*3//4, height//3, 80),
        (width//2, height//2, 70),
        (width//3, height*3//4, 65),
        (width*2//3, height*2//3, 75)
    ]
    
    # Draw dotted paths between planets
    for i in range(len(planets)-1):
        x1, y1, _ = planets[i]
        x2, y2, _ = planets[i+1]
        # Draw dotted line
        steps = 20
        for j in range(steps):
            t = j / steps
            x = x1 + (x2-x1) * t
            y = y1 + (y2-y1) * t
            draw.ellipse([x-2, y-2, x+2, y+2], fill="white")
    
    # Draw planets
    for x, y, size in planets:
        draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2],
                     fill="#FF69B4", outline="white", width=3)
    
    return img

def generate_scene_5(width, height):
    """Adults on planets scene"""
    img = create_gradient_background(width, height, "#708090", "#2F4F4F")
    draw = ImageDraw.Draw(img)
    
    # Three planets with figures
    planets = [
        (width//4, height//2, "KRÓL"),
        (width//2, height//2, "PRÓŻNY"),
        (width*3//4, height//2, "BANKIER")
    ]
    
    for x, y, label in planets:
        # Draw planet
        draw.ellipse([x-80, y-80, x+80, y+80],
                     fill="#696969", outline="white", width=3)
        
        # Draw simple figure
        draw.ellipse([x-20, y-40, x+20, y], fill="black")  # head
        draw.rectangle([x-15, y, x+15, y+40], fill="black")  # body
        
        # Draw question mark above
        try:
            draw.text((x-20, y-100), "?", fill="yellow", font=None)
        except:
            pass
    
    return img

def generate_scene_6(width, height):
    """Heart and vision scene"""
    img = create_gradient_background(width, height, "#FF1493", "#FFB6C1")
    draw = ImageDraw.Draw(img)
    
    # Draw large heart
    cx, cy = width//2, height//2
    size = 200
    
    # Heart shape (simplified)
    points = []
    for i in range(0, 360, 10):
        angle = i * 3.14159 / 180
        if i < 180:
            r = size * (1 + 0.2 * abs(90 - i) / 90)
        else:
            r = size * (1 - 0.3 * (i - 180) / 180)
        x = cx + r * 0.5 * (16 * pow(abs(angle), 3))
        y = cy - r * 0.5 * (13 * abs(angle) - 5 * abs(2*angle) - 2 * abs(3*angle) - abs(4*angle))
    
    # Simple heart
    draw.polygon([(cx, cy+size//2),
                  (cx-size//2, cy-size//4),
                  (cx-size//3, cy-size//2),
                  (cx, cy-size//4),
                  (cx+size//3, cy-size//2),
                  (cx+size//2, cy-size//4)],
                 fill="#FF1493", outline="white", width=5)
    
    # Stars inside heart
    for _ in range(10):
        import random
        x = cx + random.randint(-size//3, size//3)
        y = cy + random.randint(-size//3, size//4)
        draw.polygon([(x, y-5), (x-3, y+3), (x+3, y+3)], fill="white")
    
    return img

def generate_scene_7(width, height):
    """Books to birds transformation"""
    img = create_gradient_background(width, height, "#32CD32", "#00FA9A")
    draw = ImageDraw.Draw(img)
    
    # Draw stack of books at bottom
    book_y = height * 3//4
    for i in range(4):
        y = book_y - i * 30
        draw.rectangle([width//2-100, y, width//2+100, y+25],
                       fill="#8B4513", outline="black", width=2)
    
    # Draw birds flying up (simple V shapes)
    for i in range(8):
        x = width//2 + (i-4) * 50
        y = height//2 - i * 30
        # Bird as simple V
        draw.line([(x-15, y), (x, y-10), (x+15, y)], fill="white", width=3)
    
    return img

def generate_scene_8(width, height):
    """Rose under glass dome"""
    img = create_gradient_background(width, height, "#DC143C", "#FFE4E1")
    draw = ImageDraw.Draw(img)
    
    cx, cy = width//2, height//2
    
    # Draw glass dome
    draw.arc([(cx-150, cy-100), (cx+150, cy+100)],
             start=180, end=0, fill="white", width=3)
    draw.line([(cx-150, cy+100), (cx+150, cy+100)], fill="white", width=3)
    
    # Draw rose stem
    draw.line([(cx, cy+100), (cx, cy)], fill="green", width=5)
    
    # Draw rose (simplified)
    for i in range(3):
        size = 60 - i * 15
        draw.ellipse([cx-size//2, cy-size//2-50, cx+size//2, cy+size//2-50],
                     fill="#DC143C", outline="#8B0000", width=2)
    
    # Draw sparkles around
    for _ in range(20):
        import random
        x = cx + random.randint(-200, 200)
        y = cy + random.randint(-150, 150)
        draw.ellipse([x-3, y-3, x+3, y+3], fill="yellow")
    
    return img

def main():
    """Generate all scenes"""
    width, height = 1080, 1920  # TikTok vertical format
    scenes_dir = Path("scenes")
    scenes_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate each scene
    generators = [
        generate_scene_1, generate_scene_2, generate_scene_3, generate_scene_4,
        generate_scene_5, generate_scene_6, generate_scene_7, generate_scene_8
    ]
    
    for i, (scene_def, generator) in enumerate(zip(SCENES, generators)):
        print(f"Generating scene {i+1}: {scene_def['name']}")
        img = generator(width, height)
        output_path = scenes_dir / f"{scene_def['name']}.png"
        img.save(output_path)
        print(f"Saved: {output_path}")
    
    print("\nAll scenes generated successfully!")

if __name__ == "__main__":
    main()