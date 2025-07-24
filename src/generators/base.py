"""
Base class for all image generators
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Tuple
from pathlib import Path
import time
from functools import wraps
from rich.console import Console

console = Console()


class GeneratorError(Exception):
    """Base exception for generator errors"""
    pass


class GeneratorConnectionError(GeneratorError):
    """Raised when generator connection fails"""
    pass


class GeneratorTimeoutError(GeneratorError):
    """Raised when generation times out"""
    pass


class GeneratorLimitError(GeneratorError):
    """Raised when API limits are reached"""
    pass


def retry_with_backoff(max_retries: int = 3, backoff_base: float = 2.0):
    """Decorator for retrying functions with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (GeneratorConnectionError, GeneratorTimeoutError) as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff_base ** attempt
                    console.print(f"[yellow]Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...[/yellow]")
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator


class BaseImageGenerator(ABC):
    """Abstract base class for image generators"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize generator with configuration
        
        Args:
            config: Generator-specific configuration
        """
        self.config = config
        self.name = self.__class__.__name__
        
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the generator service is accessible
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def generate_image(self, 
                      prompt: str, 
                      negative_prompt: str = "",
                      width: int = 1080,
                      height: int = 1920,
                      seed: int = -1,
                      **kwargs) -> Optional[str]:
        """Generate an image from prompt
        
        Args:
            prompt: Positive prompt for image generation
            negative_prompt: Negative prompt to avoid certain elements
            width: Image width in pixels
            height: Image height in pixels
            seed: Random seed (-1 for random)
            **kwargs: Additional generator-specific parameters
            
        Returns:
            Optional[str]: Image ID or path if successful, None if failed
        """
        pass
    
    @abstractmethod
    def download_image(self, image_id: str, output_path: Path) -> bool:
        """Download generated image to specified path
        
        Args:
            image_id: ID or reference to the generated image
            output_path: Path where to save the image
            
        Returns:
            bool: True if download successful, False otherwise
        """
        pass
    
    def generate_and_save(self,
                         prompt: str,
                         output_path: Path,
                         negative_prompt: str = "",
                         width: int = 1080,
                         height: int = 1920,
                         seed: int = -1,
                         **kwargs) -> bool:
        """Generate image and save it directly (convenience method)
        
        Args:
            prompt: Positive prompt for image generation
            output_path: Path where to save the image
            negative_prompt: Negative prompt to avoid certain elements
            width: Image width in pixels
            height: Image height in pixels
            seed: Random seed (-1 for random)
            **kwargs: Additional generator-specific parameters
            
        Returns:
            bool: True if generation and save successful, False otherwise
        """
        try:
            image_id = self.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                seed=seed,
                **kwargs
            )
            
            if image_id:
                return self.download_image(image_id, output_path)
            return False
            
        except GeneratorError as e:
            console.print(f"[red]Generation failed: {e}[/red]")
            return False
    
    def validate_dimensions(self, width: int, height: int) -> Tuple[int, int]:
        """Validate and adjust dimensions if needed
        
        Args:
            width: Requested width
            height: Requested height
            
        Returns:
            Tuple[int, int]: Validated (width, height)
        """
        # Default implementation - can be overridden by specific generators
        return (width, height)
    
    def get_info(self) -> Dict[str, Any]:
        """Get generator information
        
        Returns:
            Dict with generator info (name, version, capabilities, etc.)
        """
        return {
            'name': self.name,
            'class': self.__class__.__name__,
            'config': self.config
        }
    
    def __str__(self) -> str:
        return f"{self.name}({self.config.get('base_url', 'no-url')})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} at {hex(id(self))}>"