import os
import yaml
import numpy as np
import cv2
import multiprocessing
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from rich.progress import track
from datetime import datetime
import subprocess
import tempfile
import shutil
from functools import partial

from .slide_renderer import SlideRenderer
from .utils import ensure_dir, get_font_path

console = Console()


def render_frame_parallel(scene_path: Path, slide_data: Dict, book_info: Dict, 
                         frame_time: float, duration: float, slide_index: int,
                         template: Dict, width: int, height: int) -> np.ndarray:
    """Static function for parallel processing - renders a single frame"""
    # Import here to avoid pickling issues
    from .slide_renderer import SlideRenderer
    
    # Create slide renderer instance
    slide_renderer = SlideRenderer(template)
    
    # Load image
    img = Image.open(scene_path).convert('RGB')
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Render text overlay based on slide type
    slide_type = slide_data.get('type', 'default')
    
    if slide_type == 'hook':
        img = slide_renderer._render_hook_slide(img, slide_data)
    elif slide_type == 'intro':
        img = slide_renderer._render_intro_slide(img, slide_data, book_info)
    elif slide_type == 'quote':
        img = slide_renderer._render_quote_slide(img, slide_data)
    elif slide_type == 'cta':
        img = slide_renderer._render_cta_slide(img, slide_data)
    else:
        img = slide_renderer._render_text_slide(img, slide_data)
    
    # Convert to numpy array for OpenCV
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # Apply Ken Burns effect if not CTA slide
    if slide_data.get('type') != 'cta' and template['animation_settings']['background_ken_burns']:
        # Ken Burns effect
        zoom_duration = duration * 0.7
        
        if frame_time < zoom_duration:
            zoom = 1.0 + (0.05 * frame_time / zoom_duration)
        else:
            zoom = 1.05
        
        # Calculate new dimensions
        new_width = int(width * zoom)
        new_height = int(height * zoom)
        
        # Resize image
        resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        
        # Crop to original dimensions (center crop)
        x_offset = (new_width - width) // 2
        y_offset = (new_height - height) // 2
        
        frame = resized[y_offset:y_offset + height, x_offset:x_offset + width]
    
    return frame


class OptimizedVideoGenerator:
    """Optimized video generator using parallel processing and direct ffmpeg encoding"""
    
    def __init__(self, template_path: str):
        """Initialize video generator with template configuration"""
        self.template_path = template_path
        self.template = self._load_template()
        self.slide_renderer = SlideRenderer(self.template)
        
        # Video settings
        self.width = self.template['video_settings']['width']
        self.height = self.template['video_settings']['height']
        self.fps = self.template['video_settings']['fps']
        self.video_format = self.template['video_settings']['format']
        self.codec = self.template['video_settings']['codec']
        
        # CPU count for parallel processing
        self.cpu_count = multiprocessing.cpu_count()
        
        console.print(f"[green]Optimized Video Generator initialized[/green]")
        console.print(f"[dim]Using {self.cpu_count} CPU cores for parallel processing[/dim]")
    
    def _load_template(self) -> Dict:
        """Load YAML template file"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_book_config(self, book_yaml_path: str) -> Dict:
        """Load book-specific YAML configuration"""
        with open(book_yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    
    def _render_slide_frames_parallel(self, scene_path: Path, slide_data: Dict, 
                                    book_info: Dict, slide_index: int) -> List[np.ndarray]:
        """Render all frames for a slide in parallel"""
        duration = slide_data.get('duration', self.template['slide_defaults']['duration'])
        num_frames = int(duration * self.fps)
        
        # Create frame times
        frame_times = np.linspace(0, duration, num_frames)
        
        # Prepare arguments for parallel processing
        args = [(scene_path, slide_data, book_info, t, duration, slide_index, 
                 self.template, self.width, self.height) for t in frame_times]
        
        # Use multiprocessing to render frames in parallel
        with multiprocessing.Pool(processes=self.cpu_count) as pool:
            frames = pool.starmap(render_frame_parallel, args)
        
        return frames
    
    def generate_video(self, book_yaml_path: str, output_path: Optional[str] = None) -> str:
        """Generate video using parallel processing and direct ffmpeg encoding"""
        console.print(f"\n[bold cyan]Starting optimized video generation for: {book_yaml_path}[/bold cyan]")
        
        # Load book configuration
        book_config = self._load_book_config(book_yaml_path)
        book_info = book_config['book_info']
        
        # Set output path
        if not output_path:
            book_filename = Path(book_yaml_path).stem
            output_path = f"output/{book_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{self.video_format}"
        
        ensure_dir(Path(output_path).parent)
        
        # Get scene files
        book_dir = Path(book_yaml_path).parent
        scene_files = self._get_scene_files(book_dir, len(book_config['slides']))
        
        # Create temporary directory for frames
        with tempfile.TemporaryDirectory() as temp_dir:
            console.print("[blue]Rendering frames in parallel...[/blue]")
            
            frame_count = 0
            all_frames_paths = []
            
            # Process each slide
            for idx, (slide_data, scene_path) in enumerate(zip(book_config['slides'], scene_files)):
                console.print(f"[yellow]Processing slide {idx + 1}/{len(book_config['slides'])}[/yellow]")
                
                # Render frames in parallel
                frames = self._render_slide_frames_parallel(scene_path, slide_data, book_info, idx)
                
                # Save frames to disk
                for frame in frames:
                    frame_path = os.path.join(temp_dir, f"frame_{frame_count:06d}.png")
                    cv2.imwrite(frame_path, frame)
                    all_frames_paths.append(frame_path)
                    frame_count += 1
            
            console.print(f"[green]✓ Rendered {frame_count} frames[/green]")
            
            # Use GPU-accelerated ffmpeg if available
            ffmpeg_path = self._get_ffmpeg_path()
            
            # Build ffmpeg command
            console.print("[blue]Encoding video with ffmpeg...[/blue]")
            
            ffmpeg_cmd = [
                ffmpeg_path,
                '-y',  # Overwrite output
                '-framerate', str(self.fps),
                '-i', os.path.join(temp_dir, 'frame_%06d.png'),
                '-c:v', 'h264_nvenc' if 'nvenc' in self._get_available_encoders(ffmpeg_path) else 'libx264',
                '-preset', 'p4' if 'nvenc' in self._get_available_encoders(ffmpeg_path) else 'fast',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                output_path
            ]
            
            # Run ffmpeg
            process = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if process.returncode != 0:
                console.print(f"[red]FFmpeg error: {process.stderr}[/red]")
                raise RuntimeError("FFmpeg encoding failed")
        
        console.print(f"[bold green]✓ Video generated successfully: {output_path}[/bold green]")
        return output_path
    
    def _get_scene_files(self, book_dir: Path, num_slides: int) -> List[Path]:
        """Get scene files for all slides"""
        scenes_dirs = ['generated', 'scenes_v2', 'scenes', 'with_text']
        scene_files = []
        
        for scenes_dir in scenes_dirs:
            scenes_path = book_dir / scenes_dir
            if scenes_path.exists():
                for idx in range(num_slides):
                    patterns = [
                        f"scene_{idx:02d}_*.png",
                        f"scene_{idx}_*.png",
                        f"{idx:02d}_*.png",
                        f"*_{idx:02d}.png"
                    ]
                    
                    found = False
                    for pattern in patterns:
                        files = list(scenes_path.glob(pattern))
                        if files:
                            scene_files.append(files[0])
                            found = True
                            break
                    
                    if not found:
                        raise FileNotFoundError(f"Missing scene for slide {idx}")
                
                if len(scene_files) == num_slides:
                    break
        
        return scene_files
    
    def _get_ffmpeg_path(self) -> str:
        """Get path to ffmpeg (prefer GPU-enabled version)"""
        # For now use system ffmpeg which has NVENC support
        return "ffmpeg"
    
    def _get_available_encoders(self, ffmpeg_path: str) -> str:
        """Check available encoders"""
        try:
            result = subprocess.run(
                [ffmpeg_path, '-hide_banner', '-encoders'],
                capture_output=True,
                text=True
            )
            return result.stdout
        except:
            return ""