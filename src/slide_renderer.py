import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, CompositeVideoClip
from typing import Dict, Tuple, Optional, List
import textwrap
from pathlib import Path

from .utils import get_font_path, add_text_shadow, calculate_text_position


class SlideRenderer:
    def __init__(self, template: Dict):
        """Initialize slide renderer with template settings"""
        self.template = template
        self.text_settings = template['text_settings']
        self.video_settings = template['video_settings']
        
        # Load fonts
        self.fonts = self._load_fonts()
        
        # Colors
        self.color_primary = self.text_settings['color_primary']
        self.color_secondary = self.text_settings['color_secondary']
        self.shadow_color = self.text_settings['shadow_color']
        self.shadow_offset = self.text_settings['shadow_offset']
    
    def _load_fonts(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """Load font files for different text sizes"""
        font_family = self.text_settings['font_family']
        fonts = {}
        
        # Try to use system fonts that exist
        font_paths = [
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/TTF/GoogleSans-Bold.ttf"
        ]
        
        bold_font_path = None
        regular_font_path = None
        
        # Find available fonts
        for font_path in font_paths:
            if Path(font_path).exists():
                bold_font_path = font_path
                # Try to find regular version
                regular_path = font_path.replace('-Bold', '-Regular').replace('Bold', 'Regular')
                if Path(regular_path).exists():
                    regular_font_path = regular_path
                else:
                    regular_font_path = bold_font_path
                break
        
        if bold_font_path:
            try:
                fonts['title'] = ImageFont.truetype(
                    bold_font_path,
                    self.text_settings['font_size_title']
                )
                fonts['body'] = ImageFont.truetype(
                    regular_font_path,
                    self.text_settings['font_size_body']
                )
                fonts['cta'] = ImageFont.truetype(
                    bold_font_path,
                    self.text_settings['font_size_cta']
                )
                fonts['author'] = ImageFont.truetype(
                    regular_font_path,
                    self.text_settings.get('font_size_author', 55)
                )
                fonts['small'] = ImageFont.truetype(
                    regular_font_path,
                    int(self.text_settings['font_size_body'] * 0.8)
                )
                print(f"✓ Loaded font: {Path(bold_font_path).name}")
            except Exception as e:
                print(f"Error loading fonts: {e}")
                # Use large sizes even for default font
                for key, size in [('title', self.text_settings['font_size_title']), 
                                  ('body', self.text_settings['font_size_body']), 
                                  ('cta', self.text_settings['font_size_cta']), 
                                  ('small', int(self.text_settings['font_size_body'] * 0.8))]:
                    fonts[key] = ImageFont.load_default()
        else:
            print("Warning: No system fonts found, using default")
            # Use configured sizes for default font
            for key, size in [('title', self.text_settings['font_size_title']), 
                              ('body', self.text_settings['font_size_body']), 
                              ('cta', self.text_settings['font_size_cta']), 
                              ('small', int(self.text_settings['font_size_body'] * 0.8))]:
                fonts[key] = ImageFont.load_default()
        
        return fonts
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
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
    
    def _draw_text_on_image(self, image: Image.Image, text: str, font: ImageFont.FreeTypeFont,
                          position: Tuple[int, int], color: str, align: str = 'center',
                          max_width: Optional[int] = None) -> Image.Image:
        """Draw text on image with optional wrapping and shadow"""
        draw = ImageDraw.Draw(image)
        
        # Wrap text if max_width is specified
        if max_width:
            lines = self._wrap_text(text, font, max_width)
        else:
            lines = [text]
        
        # Calculate total height for centering
        line_height = font.size + 10  # Add some line spacing
        total_height = len(lines) * line_height
        
        # Adjust starting y position for vertical centering
        y = position[1] - (total_height // 2) if position[1] == self.video_settings['height'] // 2 else position[1]
        
        for line in lines:
            # Get text bbox
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Calculate x position based on alignment
            if align == 'center':
                x = position[0] - (text_width // 2) if position[0] == self.video_settings['width'] // 2 else position[0]
            elif align == 'left':
                x = position[0]
            else:  # right
                x = position[0] - text_width
            
            # Draw outline if enabled (for better contrast)
            if hasattr(self.text_settings, 'outline_width') or 'outline_width' in self.text_settings:
                outline_width = self.text_settings.get('outline_width', 4)
                outline_color = self.text_settings.get('outline_color', '#000000')
                # Draw outline by drawing text multiple times with offset
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
            
            # Draw shadow if enabled
            if self.text_settings['shadow']:
                draw.text(
                    (x + self.shadow_offset, y + self.shadow_offset),
                    line,
                    font=font,
                    fill=self.shadow_color
                )
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=color)
            
            y += line_height
        
        return image
    
    def _apply_ken_burns_effect(self, image_clip: ImageClip, duration: float) -> ImageClip:
        """Apply Ken Burns effect (slow zoom) to background"""
        if not self.template['animation_settings']['background_ken_burns']:
            return image_clip
        
        # Zoom przez pierwsze 70% czasu, potem zatrzymaj
        zoom_duration = duration * 0.7  # Zoom przez 70% czasu
        
        def zoom_func(t):
            if t < zoom_duration:
                # Zoom od 100% do 105% podczas zoom_duration
                zoom = 1.0 + (0.05 * t / zoom_duration)
            else:
                # Zatrzymaj na 105% przez resztę czasu
                zoom = 1.05
            return zoom
        
        return image_clip.resized(lambda t: zoom_func(t))
    
    def render_slide(self, slide_data: Dict, background: np.ndarray, book_info: Dict,
                    slide_index: int, total_slides: int) -> ImageClip:
        """Render a single slide with text and background"""
        slide_type = slide_data.get('type', 'default')
        
        # Create PIL image from background
        bg_image = Image.fromarray(background)
        
        # Add darkening overlay for better text readability
        overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, 100))
        bg_image.paste(overlay, (0, 0), overlay)
        
        # Get positions from template
        positions = self.text_settings['positions']
        
        # Render based on slide type
        if slide_type == 'hook':
            bg_image = self._render_hook_slide(bg_image, slide_data)
        elif slide_type == 'intro':
            bg_image = self._render_intro_slide(bg_image, slide_data, book_info)
        elif slide_type == 'quote':
            bg_image = self._render_quote_slide(bg_image, slide_data)
        elif slide_type == 'cta':
            bg_image = self._render_cta_slide(bg_image, slide_data)
        else:
            # Default text slide
            bg_image = self._render_text_slide(bg_image, slide_data)
        
        # Add slide counter
        if slide_index > 0:  # Don't show on first slide
            self._add_slide_counter(bg_image, slide_index + 1, total_slides)
        
        # Convert back to numpy array and create video clip
        slide_array = np.array(bg_image)
        duration = slide_data.get('duration', self.template['slide_defaults']['duration'])
        slide_clip = ImageClip(slide_array, duration=duration)
        
        # Apply Ken Burns effect (ale nie dla ostatniego slajdu CTA)
        if slide_type != 'cta':
            slide_clip = self._apply_ken_burns_effect(slide_clip, duration)
        
        return slide_clip
    
    def _render_hook_slide(self, image: Image.Image, slide_data: Dict) -> Image.Image:
        """Render hook slide with large, centered text"""
        text = slide_data['text']
        
        # Use title font but slightly smaller
        font = self.fonts['title']
        
        # Center position
        position = (
            self.video_settings['width'] // 2,
            self.video_settings['height'] // 2
        )
        
        # Draw text with emphasis color
        return self._draw_text_on_image(
            image, text, font, position,
            self.color_secondary,  # Use secondary color for hooks
            align='center',
            max_width=int(self.video_settings['width'] * 0.8)
        )
    
    def _render_intro_slide(self, image: Image.Image, slide_data: Dict, book_info: Dict) -> Image.Image:
        """Render intro slide with book title, author and year"""
        # For intro slide, we want to display:
        # 1. Book title (from book_info)
        # 2. Author name
        # 3. Year of publication
        
        # Calculate center position
        center_x = self.video_settings['width'] // 2
        start_y = self.video_settings['height'] // 3  # Start from upper third
        
        # Draw book title
        title_text = book_info.get('title', 'Nieznany tytuł')
        image = self._draw_text_on_image(
            image,
            title_text,
            self.fonts['title'],
            (center_x, start_y),
            self.color_primary,
            align='center',
            max_width=int(self.video_settings['width'] * 0.9)
        )
        
        # Draw author name
        author_text = book_info.get('author', 'Nieznany autor')
        author_y = start_y + self.text_settings['font_size_title'] + 30
        image = self._draw_text_on_image(
            image,
            author_text,
            self.fonts.get('author', self.fonts['small']),  # Użyj mniejszej czcionki dla autora
            (center_x, author_y),
            self.color_secondary,
            align='center',
            max_width=int(self.video_settings['width'] * 0.8)  # Ogranicz szerokość
        )
        
        # Draw year
        year_text = str(book_info.get('year', ''))
        if year_text:
            year_y = author_y + self.text_settings.get('font_size_author', 55) + 20
            image = self._draw_text_on_image(
                image,
                year_text,
                self.fonts['small'],
                (center_x, year_y),
                self.color_secondary,
                align='center'
            )
        
        return image
    
    def _render_quote_slide(self, image: Image.Image, slide_data: Dict) -> Image.Image:
        """Render quote slide with special formatting"""
        quote_text = f'"{slide_data["text"]}"'
        
        # Draw quote
        body_pos = calculate_text_position(
            self.text_settings['positions']['body'],
            self.video_settings['width'],
            self.video_settings['height']
        )
        
        image = self._draw_text_on_image(
            image,
            quote_text,
            self.fonts['body'],
            body_pos,
            self.color_primary,
            align='center',
            max_width=int(self.video_settings['width'] * 0.85)
        )
        
        # Draw author attribution if specified
        if slide_data.get('author_position') == 'bottom':
            author_pos = (
                self.video_settings['width'] // 2,
                self.video_settings['height'] - 200
            )
            image = self._draw_text_on_image(
                image,
                "— Mały Książę",
                self.fonts['small'],
                author_pos,
                self.color_secondary,
                align='center'
            )
        
        return image
    
    def _render_cta_slide(self, image: Image.Image, slide_data: Dict) -> Image.Image:
        """Render call-to-action slide"""
        # Draw CTA text
        cta_pos = calculate_text_position(
            self.text_settings['positions']['cta'],
            self.video_settings['width'],
            self.video_settings['height']
        )
        
        image = self._draw_text_on_image(
            image,
            slide_data['text'],
            self.fonts['cta'],
            cta_pos,
            self.color_secondary,  # Use secondary color for CTA
            align='center',
            max_width=int(self.video_settings['width'] * 0.85)
        )
        
        # Hashtagi usunięte - nie wyświetlamy ich na video
        # if 'hashtags' in slide_data:
        #     hashtag_text = ' '.join(slide_data['hashtags'])
        #     ...
        # Hashtagi są w opisie video na TikToku, nie na samym filmie
        
        return image
    
    def _render_text_slide(self, image: Image.Image, slide_data: Dict) -> Image.Image:
        """Render default text slide"""
        body_pos = calculate_text_position(
            self.text_settings['positions']['body'],
            self.video_settings['width'],
            self.video_settings['height']
        )
        
        return self._draw_text_on_image(
            image,
            slide_data['text'],
            self.fonts['body'],
            body_pos,
            self.color_primary,
            align='center',
            max_width=int(self.text_settings['positions']['body'].get('max_width', self.video_settings['width'] * 0.85))
        )
    
    def _add_slide_counter(self, image: Image.Image, current: int, total: int) -> None:
        """Add slide progress indicator"""
        draw = ImageDraw.Draw(image)
        
        # Position at bottom center (above TikTok UI elements)
        bar_width = 200
        bar_height = 4
        bar_x = (self.video_settings['width'] - bar_width) // 2
        bar_y = self.video_settings['height'] - 350  # Above TikTok's 320px bottom safe zone
        
        # Draw background bar
        draw.rectangle(
            [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
            fill=(255, 255, 255, 100)
        )
        
        # Draw progress
        progress_width = int(bar_width * (current / total))
        draw.rectangle(
            [bar_x, bar_y, bar_x + progress_width, bar_y + bar_height],
            fill=self.color_secondary
        )