import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from moviepy import ImageClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip, VideoFileClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from rich.console import Console
from rich.progress import track
from datetime import datetime
import requests
from io import BytesIO

# Configure MoviePy to use system ffmpeg
import moviepy.config as moviepy_config
import os
moviepy_config.FFMPEG_BINARY = "/usr/bin/ffmpeg"

from .slide_renderer import SlideRenderer
from .text_animator import TextAnimator
from .utils import ensure_dir, get_font_path

console = Console()


class VideoGenerator:
    def __init__(self, template_path: str):
        """Initialize video generator with template configuration"""
        self.template_path = template_path
        self.template = self._load_template()
        self.slide_renderer = SlideRenderer(self.template)
        self.text_animator = TextAnimator(self.template)
        
        # Video settings
        self.width = self.template['video_settings']['width']
        self.height = self.template['video_settings']['height']
        self.fps = self.template['video_settings']['fps']
        self.video_format = self.template['video_settings']['format']
        self.codec = self.template['video_settings']['codec']
        
        console.print(f"[green]Video Generator initialized with template: {template_path}[/green]")
    
    def _load_template(self) -> Dict:
        """Load YAML template file"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_book_config(self, book_yaml_path: str) -> Dict:
        """Load book-specific YAML configuration"""
        with open(book_yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _generate_or_load_background(self, book_config: Dict, book_yaml_path: str) -> np.ndarray:
        """Generate AI background or load existing one"""
        background_prompt = book_config.get('background_prompt', '')
        prompt_hash = generate_background_prompt_hash(background_prompt)
        
        # Get book directory
        book_dir = Path(book_yaml_path).parent
        
        # Check if background already exists in book folder
        background_path = book_dir / "background.png"
        if not background_path.exists():
            background_path = book_dir / "background.jpg"
        
        # Also check shared backgrounds
        shared_background_path = Path(f"shared_assets/backgrounds/{prompt_hash}.png")
        
        if background_path.exists():
            console.print(f"[yellow]Loading book background: {background_path}[/yellow]")
            img = Image.open(background_path)
        elif shared_background_path.exists():
            console.print(f"[yellow]Loading shared background: {shared_background_path}[/yellow]")
            img = Image.open(shared_background_path)
        else:
            console.print(f"[blue]Generating new background for prompt: {background_prompt[:50]}...[/blue]")
            # For now, create a gradient placeholder
            # In production, this would call an AI image generation API
            img = self._create_gradient_background(book_config)
            
            # Save to book folder
            ensure_dir(book_dir)
            img.save(book_dir / "background.png")
        
        # Resize to video dimensions
        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        return np.array(img)
    
    def _create_gradient_background(self, book_config: Dict) -> Image.Image:
        """Create a gradient background as placeholder"""
        # Create gradient based on book genre
        genre = book_config['book_info'].get('genre', 'default')
        
        color_schemes = {
            'Filozoficzna baśń': [(255, 218, 185), (135, 206, 235)],  # Peach to sky blue
            'Dystopia': [(20, 20, 20), (100, 100, 100)],  # Dark gradient
            'Romans': [(255, 182, 193), (255, 105, 180)],  # Pink gradient
            'Przygodowa': [(34, 139, 34), (144, 238, 144)],  # Forest green
            'default': [(70, 130, 180), (176, 224, 230)]  # Steel blue to powder blue
        }
        
        colors = color_schemes.get(genre, color_schemes['default'])
        
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Create vertical gradient
        for y in range(self.height):
            ratio = y / self.height
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        return img
    
    def _add_audio_track(self, video_clip: VideoFileClip, book_title: str, book_yaml_path: str) -> VideoFileClip:
        """Add trending audio or fallback music to video"""
        music_settings = self.template['music_settings']
        book_dir = Path(book_yaml_path).parent
        
        # Check for book-specific audio first
        book_audio_path = book_dir / "audio" / "theme.mp3"
        if not book_audio_path.exists():
            book_audio_path = book_dir / "audio" / "music.mp3"
        
        if book_audio_path.exists():
            console.print(f"[green]Using book-specific audio: {book_audio_path}[/green]")
            audio = AudioFileClip(str(book_audio_path))
            audio = audio.subclipped(0, video_clip.duration)
            audio = audio.with_volume_scaled(music_settings['volume'])
            video_clip = video_clip.with_audio(audio)
            return video_clip
        
        if music_settings['use_trending_audio']:
            # In production, this would fetch trending TikTok audio
            console.print("[yellow]Using fallback music (trending audio API not implemented)[/yellow]")
        
        # Use fallback music from shared assets
        fallback_path = music_settings['fallback_music']
        # Update path to use shared_assets
        if fallback_path.startswith("assets/"):
            fallback_path = fallback_path.replace("assets/", "shared_assets/")
        
        if os.path.exists(fallback_path):
            audio = AudioFileClip(fallback_path)
            audio = audio.subclipped(0, video_clip.duration)
            audio = audio.with_volume_scaled(music_settings['volume'])
            video_clip = video_clip.with_audio(audio)
            console.print(f"[green]Added shared audio track to video[/green]")
        else:
            console.print(f"[yellow]No audio file found at {fallback_path}[/yellow]")
        
        return video_clip
    
    def generate_video(self, book_yaml_path: str, output_path: Optional[str] = None) -> str:
        """Generate complete TikTok video from book YAML"""
        console.print(f"\n[bold cyan]Starting video generation for: {book_yaml_path}[/bold cyan]")
        
        # Load book configuration
        book_config = self._load_book_config(book_yaml_path)
        book_info = book_config['book_info']
        
        # Set output path
        if not output_path:
            book_filename = Path(book_yaml_path).stem
            # Extract book ID from directory name (e.g., "0017_little_prince" -> "0017")
            book_dir_name = Path(book_yaml_path).parent.name
            book_id = book_dir_name.split('_')[0] if '_' in book_dir_name else ""
            
            # Generate filename with ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if book_id and book_id.isdigit():
                output_path = f"output/{book_filename}_{book_id}_{timestamp}.{self.video_format}"
            else:
                output_path = f"output/{book_filename}_{timestamp}.{self.video_format}"
        
        ensure_dir(Path(output_path).parent)
        
        # Generate slides
        slides = []
        book_dir = Path(book_yaml_path).parent
        
        # Check for generated scenes
        scenes_dirs = ['generated', 'scenes_v2', 'scenes', 'with_text']
        scene_files = []
        
        for scenes_dir in scenes_dirs:
            scenes_path = book_dir / scenes_dir
            if scenes_path.exists():
                # Try to find scene files
                for idx in range(len(book_config['slides'])):
                    # Try different naming patterns
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
                        # Use background as fallback
                        scene_files.append(None)
                
                if any(scene_files):
                    console.print(f"[green]Found scenes in {scenes_dir}[/green]")
                    # Print all scene files at once to avoid progress bar issues
                    for idx, scene_file in enumerate(scene_files):
                        if scene_file:
                            console.print(f"[blue]Using scene: {scene_file.name}[/blue]")
                    break
        
        for idx, slide_data in enumerate(book_config['slides']):
            # Merge slide settings with defaults
            slide_duration = slide_data.get('duration', self.template['slide_defaults']['duration'])
            
            # Load scene image or use background
            if idx < len(scene_files) and scene_files[idx]:
                scene_img = Image.open(scene_files[idx])
                scene_array = np.array(scene_img.resize((self.width, self.height), Image.Resampling.LANCZOS))
            else:
                raise FileNotFoundError(f"Missing AI-generated scene for slide {idx}. All scenes must be generated!")
            
            # Render slide with text
            slide_clip = self.slide_renderer.render_slide(
                slide_data=slide_data,
                background=scene_array,
                book_info=book_info,
                slide_index=idx,
                total_slides=len(book_config['slides'])
            )
            
            # Apply animations
            slide_clip = self.text_animator.apply_animations(slide_clip, slide_data)
            
            # Set duration
            slide_clip = slide_clip.with_duration(slide_duration)
            
            # Add transitions
            if idx > 0:
                transition_type = self.template['slide_defaults']['transition_type']
                transition_duration = self.template['slide_defaults']['transition_duration']
                
                if transition_type == 'fade':
                    from moviepy.video.fx import CrossFadeIn
                    slide_clip = slide_clip.with_effects([CrossFadeIn(transition_duration)])
            
            slides.append(slide_clip)
        
        # Concatenate all slides
        console.print("[blue]Concatenating slides...[/blue]")
        final_video = concatenate_videoclips(slides, method="compose")
        
        # Add audio
        final_video = self._add_audio_track(final_video, book_info['title'], book_yaml_path)
        
        # Check for GPU acceleration post-processing
        use_gpu_postprocess = False
        gpu_ffmpeg_path = "/home/xai/DEV/37degrees/tmp/ffmpeg-install/bin/ffmpeg"
        
        try:
            import subprocess
            # Check for NVIDIA GPU and custom ffmpeg
            if os.path.exists(gpu_ffmpeg_path):
                nvidia_check = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
                if nvidia_check.returncode == 0:
                    # Verify h264_nvenc is available in custom ffmpeg
                    nvenc_test = subprocess.run(
                        [gpu_ffmpeg_path, '-hide_banner', '-encoders'], 
                        capture_output=True, text=True,
                        env={**os.environ, 'LD_LIBRARY_PATH': '/home/xai/DEV/37degrees/tmp/ffmpeg-install/lib:' + os.environ.get('LD_LIBRARY_PATH', '')}
                    )
                    if 'h264_nvenc' in nvenc_test.stdout:
                        use_gpu_postprocess = True
                        console.print("[green]✓ GPU acceleration available for post-processing[/green]")
                    else:
                        console.print("[yellow]Custom FFmpeg found but h264_nvenc not available[/yellow]")
        except Exception as e:
            console.print(f"[yellow]GPU check failed: {e}[/yellow]")
        
        # Write video file
        console.print(f"[blue]Writing video to: {output_path}[/blue]")
        
        # First encode with CPU (fast)
        temp_output = output_path.replace('.mp4', '_temp.mp4')
        
        if use_gpu_postprocess:
            # Use fast CPU encoding first
            console.print("[blue]Creating temporary video with CPU encoding...[/blue]")
            final_video.write_videofile(
                temp_output,
                fps=self.fps,
                codec=self.codec,
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                preset='ultrafast',  # Fast CPU encoding
                ffmpeg_params=['-crf', '23']
            )
            
            # Then re-encode with GPU
            console.print("[green]Re-encoding with GPU acceleration...[/green]")
            gpu_env = {**os.environ, 'LD_LIBRARY_PATH': '/home/xai/DEV/37degrees/tmp/ffmpeg-install/lib:' + os.environ.get('LD_LIBRARY_PATH', '')}
            gpu_cmd = [
                gpu_ffmpeg_path,
                '-y',  # Overwrite output
                '-i', temp_output,  # Input file
                '-c:v', 'h264_nvenc',  # Use NVENC
                '-preset', 'p4',  # NVENC preset (balance quality/speed)
                '-rc', 'vbr',  # Variable bitrate
                '-cq', '23',  # Constant quality
                '-b:v', '8M',  # Target bitrate
                '-maxrate', '12M',  # Max bitrate
                '-bufsize', '16M',  # Buffer size
                '-pix_fmt', 'yuv420p',  # Pixel format
                '-c:a', 'copy',  # Copy audio without re-encoding
                output_path
            ]
            
            gpu_process = subprocess.run(gpu_cmd, env=gpu_env, capture_output=True, text=True)
            
            if gpu_process.returncode == 0:
                console.print("[green]✓ GPU encoding successful![/green]")
                # Remove temporary file
                os.remove(temp_output)
            else:
                console.print(f"[red]GPU encoding failed: {gpu_process.stderr}[/red]")
                # Rename temp file as final output
                os.rename(temp_output, output_path)
        else:
            # Use optimized CPU encoding with multi-threading
            import multiprocessing
            cpu_threads = multiprocessing.cpu_count()
            console.print(f"[yellow]Using CPU encoding (MoviePy limitation: single-threaded rendering)[/yellow]")
            
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec=self.codec,
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                preset='fast',  # Faster than medium, still good quality
                threads=cpu_threads,  # Use all CPU cores
                ffmpeg_params=[
                    '-threads', str(cpu_threads),  # Force thread count in ffmpeg
                    '-crf', '23',  # Constant quality (18-28, lower is better)
                    '-tune', 'film',  # Better for video content
                    '-movflags', '+faststart'  # Web optimization
                ]
            )
        
        # Clean up
        final_video.close()
        for slide in slides:
            slide.close()
        
        console.print(f"[bold green]✓ Video generated successfully: {output_path}[/bold green]")
        console.print(f"[dim]Duration: {final_video.duration:.1f}s[/dim]")
        
        return output_path
    
    def batch_generate(self, series_file: str = "collections/classics.yaml") -> List[str]:
        """Generate videos for all books in a series"""
        console.print(f"\n[bold cyan]Starting batch generation for series: {series_file}[/bold cyan]")
        
        # Load series configuration
        with open(series_file, 'r', encoding='utf-8') as f:
            series_config = yaml.safe_load(f)
        
        series_name = series_config['series']['name']
        books = series_config['books']
        generated_videos = []
        
        console.print(f"[blue]Series: {series_name} - {len(books)} books[/blue]")
        
        for i, book_ref in enumerate(books, 1):
            try:
                book_path = book_ref['path']
                console.print(f"\n[yellow]({i}/{len(books)}) Processing: {book_path}[/yellow]")
                output_path = self.generate_video(book_path)
                generated_videos.append(output_path)
            except Exception as e:
                console.print(f"[red]Error generating video for {book_ref['path']}: {e}[/red]")
                continue
        
        console.print(f"\n[bold green]Batch generation complete! Generated {len(generated_videos)} videos.[/bold green]")
        return generated_videos
    
    def generate_series_video(self, series_file: str, book_index: int) -> str:
        """Generate a single video from series by index"""
        # Load series configuration
        with open(series_file, 'r', encoding='utf-8') as f:
            series_config = yaml.safe_load(f)
        
        books = series_config['books']
        if book_index < 0 or book_index >= len(books):
            raise ValueError(f"Book index {book_index} out of range (0-{len(books)-1})")
        
        book_ref = books[book_index]
        return self.generate_video(book_ref['path'])