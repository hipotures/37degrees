"""
Generator registry for dynamic plugin loading
"""

from typing import Dict, Type, Optional, List, Any
from pathlib import Path
import importlib
import inspect
import yaml
from rich.console import Console
from .base import BaseImageGenerator, GeneratorError

console = Console()


class GeneratorRegistry:
    """Registry for managing image generator plugins"""
    
    def __init__(self):
        self._generators: Dict[str, Type[BaseImageGenerator]] = {}
        self._instances: Dict[str, BaseImageGenerator] = {}
        self._config: Dict[str, Dict[str, Any]] = {}
        
    def register(self, name: str, generator_class: Type[BaseImageGenerator]) -> None:
        """Register a generator class
        
        Args:
            name: Unique name for the generator
            generator_class: Generator class (must inherit from BaseImageGenerator)
        """
        if not inspect.isclass(generator_class) or not issubclass(generator_class, BaseImageGenerator):
            raise GeneratorError(f"{generator_class} must be a subclass of BaseImageGenerator")
            
        self._generators[name] = generator_class
        console.print(f"[green]Registered generator: {name}[/green]")
    
    def unregister(self, name: str) -> None:
        """Unregister a generator
        
        Args:
            name: Name of generator to remove
        """
        if name in self._generators:
            del self._generators[name]
            if name in self._instances:
                del self._instances[name]
            if name in self._config:
                del self._config[name]
    
    def get_generator(self, name: str, config: Optional[Dict[str, Any]] = None) -> BaseImageGenerator:
        """Get a generator instance
        
        Args:
            name: Name of the generator
            config: Optional configuration override
            
        Returns:
            BaseImageGenerator instance
        """
        if name not in self._generators:
            raise GeneratorError(f"Generator '{name}' not found. Available: {self.list_available()}")
        
        # Use cached instance if exists and no custom config
        if name in self._instances and config is None:
            return self._instances[name]
        
        # Create new instance
        generator_class = self._generators[name]
        generator_config = config or self._config.get(name, {})
        
        try:
            instance = generator_class(generator_config)
            
            # Cache if using default config
            if config is None:
                self._instances[name] = instance
                
            return instance
            
        except Exception as e:
            raise GeneratorError(f"Failed to instantiate {name}: {e}")
    
    def list_available(self) -> List[str]:
        """List all registered generator names"""
        return list(self._generators.keys())
    
    def load_config(self, config_path: Path) -> None:
        """Load generator configurations from YAML file
        
        Args:
            config_path: Path to configuration YAML file
        """
        if not config_path.exists():
            console.print(f"[yellow]Config file not found: {config_path}[/yellow]")
            return
            
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            
        if 'generators' in config_data:
            self._config = config_data['generators']
            console.print(f"[green]Loaded config for {len(self._config)} generators[/green]")
    
    def auto_discover(self, package_path: str = "src.generators") -> None:
        """Auto-discover and register generators from a package
        
        Args:
            package_path: Python package path to scan
        """
        try:
            package = importlib.import_module(package_path)
            package_dir = Path(package.__file__).parent
            
            for file_path in package_dir.glob("*.py"):
                if file_path.stem in ['__init__', 'base', 'registry']:
                    continue
                    
                module_name = f"{package_path}.{file_path.stem}"
                try:
                    module = importlib.import_module(module_name)
                    
                    # Find all generator classes in module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseImageGenerator) and 
                            obj != BaseImageGenerator):
                            
                            # Register with module name as prefix
                            generator_name = file_path.stem
                            self.register(generator_name, obj)
                            
                except ImportError as e:
                    console.print(f"[yellow]Failed to import {module_name}: {e}[/yellow]")
                    
        except ImportError as e:
            console.print(f"[red]Failed to import package {package_path}: {e}[/red]")
    
    def get_info(self, name: str) -> Dict[str, Any]:
        """Get information about a generator
        
        Args:
            name: Generator name
            
        Returns:
            Dict with generator information
        """
        if name not in self._generators:
            raise GeneratorError(f"Generator '{name}' not found")
            
        generator_class = self._generators[name]
        return {
            'name': name,
            'class': generator_class.__name__,
            'module': generator_class.__module__,
            'config': self._config.get(name, {}),
            'cached': name in self._instances
        }
    
    def clear_cache(self) -> None:
        """Clear all cached generator instances"""
        self._instances.clear()
        console.print("[yellow]Cleared generator instance cache[/yellow]")
    
    def __len__(self) -> int:
        return len(self._generators)
    
    def __contains__(self, name: str) -> bool:
        return name in self._generators
    
    def __repr__(self) -> str:
        return f"<GeneratorRegistry with {len(self)} generators>"


# Global registry instance
registry = GeneratorRegistry()