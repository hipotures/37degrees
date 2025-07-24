"""
Base classes for HTML generators
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import shutil


class BaseHtmlGenerator(ABC):
    """Abstract base class for HTML generators"""
    
    def __init__(self, output_dir: Path = None):
        """Initialize generator
        
        Args:
            output_dir: Output directory for generated files
        """
        from src.config import get_config
        config = get_config()
        
        self.output_dir = output_dir or Path(config.get('paths.site_output', 'site'))
        self.templates_dir = Path(config.get('paths.templates', 'shared_assets/templates'))
        self.assets_dir = Path(config.get('paths.shared_assets', 'shared_assets'))
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def generate(self, **kwargs) -> Path:
        """Generate HTML content
        
        Returns:
            Path to generated file
        """
        pass
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render HTML template with context
        
        Args:
            template_name: Name of template file
            context: Template context variables
            
        Returns:
            Rendered HTML content
        """
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Simple template variable replacement
        html = template_content
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            html = html.replace(placeholder, str(value))
        
        return html
    
    def copy_assets(self, dest_dir: Path = None):
        """Copy static assets to output directory
        
        Args:
            dest_dir: Destination directory (default: output_dir/assets)
        """
        dest_dir = dest_dir or self.output_dir / 'assets'
        
        # Copy CSS, JS, fonts
        assets_to_copy = [
            ('css', self.assets_dir / 'css'),
            ('js', self.assets_dir / 'js'),
            ('fonts', self.assets_dir / 'fonts'),
            ('images', self.assets_dir / 'images')
        ]
        
        for name, src_path in assets_to_copy:
            if src_path.exists():
                dest_path = dest_dir / name
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(src_path, dest_path)
    
    def format_date(self, date: datetime = None) -> str:
        """Format date for display
        
        Args:
            date: Date to format (default: now)
            
        Returns:
            Formatted date string
        """
        date = date or datetime.now()
        return date.strftime("%Y-%m-%d")
    
    def get_relative_path(self, from_path: Path, to_path: Path) -> str:
        """Get relative path between two paths
        
        Args:
            from_path: Starting path
            to_path: Target path
            
        Returns:
            Relative path as string
        """
        try:
            return Path(to_path).relative_to(Path(from_path).parent).as_posix()
        except ValueError:
            # If paths don't share a common ancestor, use absolute path
            return f"/{to_path.relative_to(self.output_dir).as_posix()}"