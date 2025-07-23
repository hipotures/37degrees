from moviepy import VideoClip, ImageClip
import numpy as np
from typing import Dict, Callable


class TextAnimator:
    def __init__(self, template: Dict):
        """Initialize text animator with template settings"""
        self.template = template
        self.animation_settings = template['animation_settings']
        
        # Animation functions mapping
        self.entrance_animations = {
            'slide_up': self._slide_up_animation,
            'slide_down': self._slide_down_animation,
            'slide_left': self._slide_left_animation,
            'slide_right': self._slide_right_animation,
            'fade': self._fade_animation,
            'zoom': self._zoom_animation,
            'bounce': self._bounce_animation,
            'typewriter': self._typewriter_animation
        }
        
        self.exit_animations = {
            'fade_out': self._fade_out_animation,
            'slide_up': self._slide_up_exit,
            'slide_down': self._slide_down_exit,
            'zoom_out': self._zoom_out_animation
        }
    
    def apply_animations(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Apply entrance and exit animations to clip"""
        # Get animation types
        entrance = self.animation_settings.get('text_entrance', 'fade')
        exit_anim = self.animation_settings.get('text_exit', 'fade_out')
        
        # Apply entrance animation
        if entrance in self.entrance_animations:
            clip = self.entrance_animations[entrance](clip, slide_data)
        
        # Apply exit animation
        if exit_anim in self.exit_animations:
            clip = self.exit_animations[exit_anim](clip, slide_data)
        
        # Apply special effects for specific slide types
        # Pulse effect disabled - user requested no zoom on CTA slides
        # if slide_data.get('type') == 'cta':
        #     clip = self._add_pulse_effect(clip)
        
        return clip
    
    def _slide_up_animation(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Slide up from bottom animation"""
        duration = 0.5
        
        def position_func(t):
            if t < duration:
                progress = t / duration
                # Ease out cubic
                progress = 1 - pow(1 - progress, 3)
                offset = int((1 - progress) * 100)
                return ('center', clip.h + offset)
            return ('center', 'center')
        
        return clip.with_position(position_func)
    
    def _slide_down_animation(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Slide down from top animation"""
        duration = 0.5
        
        def position_func(t):
            if t < duration:
                progress = t / duration
                # Ease out cubic
                progress = 1 - pow(1 - progress, 3)
                offset = int((1 - progress) * 100)
                return ('center', -offset)
            return ('center', 'center')
        
        return clip.with_position(position_func)
    
    def _slide_left_animation(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Slide in from right animation"""
        duration = 0.5
        
        def position_func(t):
            if t < duration:
                progress = t / duration
                # Ease out cubic
                progress = 1 - pow(1 - progress, 3)
                offset = int((1 - progress) * clip.w)
                return (clip.w + offset, 'center')
            return ('center', 'center')
        
        return clip.with_position(position_func)
    
    def _slide_right_animation(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Slide in from left animation"""
        duration = 0.5
        
        def position_func(t):
            if t < duration:
                progress = t / duration
                # Ease out cubic
                progress = 1 - pow(1 - progress, 3)
                offset = int((1 - progress) * clip.w)
                return (-offset, 'center')
            return ('center', 'center')
        
        return clip.with_position(position_func)
    
    def _fade_animation(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Simple fade in animation"""
        from moviepy.video.fx import FadeIn
        return clip.with_effects([FadeIn(0.5)])
    
    def _zoom_animation(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Zoom in animation"""
        duration = 0.5
        
        def resize_func(t):
            if t < duration:
                progress = t / duration
                # Ease out cubic
                progress = 1 - pow(1 - progress, 3)
                scale = 0.8 + (0.2 * progress)
                return scale
            return 1.0
        
        return clip.resized(resize_func)
    
    def _bounce_animation(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Bounce entrance animation"""
        duration = 0.8
        
        def position_func(t):
            if t < duration:
                progress = t / duration
                # Bounce easing
                if progress < 0.36:
                    offset = int((1 - 7.5625 * progress * progress) * 100)
                elif progress < 0.72:
                    progress -= 0.54
                    offset = int((1 - (7.5625 * progress * progress + 0.75)) * 100)
                elif progress < 0.9:
                    progress -= 0.81
                    offset = int((1 - (7.5625 * progress * progress + 0.9375)) * 100)
                else:
                    progress -= 0.955
                    offset = int((1 - (7.5625 * progress * progress + 0.984375)) * 100)
                
                return ('center', clip.h // 2 + offset)
            return ('center', 'center')
        
        return clip.with_position(position_func)
    
    def _typewriter_animation(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Typewriter effect - reveals text character by character"""
        duration = min(2.0, clip.duration * 0.6)
        
        def mask_func(get_frame, t):
            frame = get_frame(t)
            if t < duration:
                progress = t / duration
                # Calculate how much of the frame to show
                reveal_width = int(frame.shape[1] * progress)
                mask = np.zeros_like(frame)
                mask[:, :reveal_width] = frame[:, :reveal_width]
                return mask
            return frame
        
        return clip.fl(mask_func)
    
    def _fade_out_animation(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Fade out at the end"""
        from moviepy.video.fx import FadeOut
        return clip.with_effects([FadeOut(0.3)])
    
    def _slide_up_exit(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Slide up exit animation"""
        duration = 0.3
        exit_start = clip.duration - duration
        
        def position_func(t):
            if t > exit_start:
                progress = (t - exit_start) / duration
                # Ease in cubic
                progress = progress * progress * progress
                offset = int(progress * 100)
                return ('center', clip.h // 2 - offset)
            return ('center', 'center')
        
        return clip.with_position(position_func)
    
    def _slide_down_exit(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Slide down exit animation"""
        duration = 0.3
        exit_start = clip.duration - duration
        
        def position_func(t):
            if t > exit_start:
                progress = (t - exit_start) / duration
                # Ease in cubic
                progress = progress * progress * progress
                offset = int(progress * 100)
                return ('center', clip.h // 2 + offset)
            return ('center', 'center')
        
        return clip.with_position(position_func)
    
    def _zoom_out_animation(self, clip: VideoClip, slide_data: Dict) -> VideoClip:
        """Zoom out exit animation"""
        duration = 0.3
        exit_start = clip.duration - duration
        
        def resize_func(t):
            if t > exit_start:
                progress = (t - exit_start) / duration
                # Ease in cubic
                progress = progress * progress * progress
                scale = 1.0 - (0.2 * progress)
                return scale
            return 1.0
        
        return clip.resized(resize_func)
    
    def _add_pulse_effect(self, clip: VideoClip) -> VideoClip:
        """Add pulsing effect for CTA slides"""
        def resize_func(t):
            # Gentle pulsing effect
            pulse = 1.0 + 0.05 * np.sin(2 * np.pi * t)
            return pulse
        
        return clip.resized(resize_func)
    
    def create_custom_animation(self, animation_func: Callable) -> Callable:
        """Create custom animation from user-provided function"""
        def apply_animation(clip: VideoClip, slide_data: Dict) -> VideoClip:
            return animation_func(clip, slide_data, self.template)
        
        return apply_animation