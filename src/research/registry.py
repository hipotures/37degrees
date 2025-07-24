"""
Research provider registry for dynamic loading
"""

from typing import Dict, Type, Optional, List, Any
from pathlib import Path
import yaml
from rich.console import Console
from .base import BaseResearchProvider, ResearchError

console = Console()


class ResearchRegistry:
    """Registry for managing research providers"""
    
    def __init__(self):
        self._providers: Dict[str, Type[BaseResearchProvider]] = {}
        self._instances: Dict[str, BaseResearchProvider] = {}
        self._config: Dict[str, Dict[str, Any]] = {}
    
    def register(self, name: str, provider_class: Type[BaseResearchProvider]) -> None:
        """Register a research provider class
        
        Args:
            name: Unique name for the provider
            provider_class: Provider class (must inherit from BaseResearchProvider)
        """
        if not issubclass(provider_class, BaseResearchProvider):
            raise ResearchError(f"{provider_class} must be a subclass of BaseResearchProvider")
        
        self._providers[name] = provider_class
        console.print(f"[green]Registered research provider: {name}[/green]")
    
    def unregister(self, name: str) -> None:
        """Unregister a provider
        
        Args:
            name: Name of provider to remove
        """
        if name in self._providers:
            del self._providers[name]
            if name in self._instances:
                del self._instances[name]
            if name in self._config:
                del self._config[name]
    
    def get_provider(self, name: str, config: Optional[Dict[str, Any]] = None) -> BaseResearchProvider:
        """Get a provider instance
        
        Args:
            name: Name of the provider
            config: Optional configuration override
            
        Returns:
            BaseResearchProvider instance
        """
        if name not in self._providers:
            raise ResearchError(f"Provider '{name}' not found. Available: {self.list_available()}")
        
        # Use cached instance if exists and no custom config
        if name in self._instances and config is None:
            return self._instances[name]
        
        # Create new instance
        provider_class = self._providers[name]
        provider_config = config or self._config.get(name, {})
        
        try:
            instance = provider_class(provider_config)
            
            # Cache if using default config
            if config is None:
                self._instances[name] = instance
            
            return instance
            
        except Exception as e:
            raise ResearchError(f"Failed to instantiate {name}: {e}")
    
    def list_available(self) -> List[str]:
        """List all registered provider names"""
        return list(self._providers.keys())
    
    def load_config(self, config_data: Dict[str, Any]) -> None:
        """Load provider configurations
        
        Args:
            config_data: Dictionary with provider configurations
        """
        self._config = config_data
        console.print(f"[green]Loaded config for {len(config_data)} research providers[/green]")
    
    def get_info(self, name: str) -> Dict[str, Any]:
        """Get information about a provider
        
        Args:
            name: Provider name
            
        Returns:
            Dict with provider information
        """
        if name not in self._providers:
            raise ResearchError(f"Provider '{name}' not found")
        
        provider_class = self._providers[name]
        return {
            'name': name,
            'class': provider_class.__name__,
            'module': provider_class.__module__,
            'config': self._config.get(name, {}),
            'cached': name in self._instances
        }
    
    def clear_cache(self) -> None:
        """Clear all cached provider instances"""
        self._instances.clear()
        console.print("[yellow]Cleared research provider cache[/yellow]")
    
    def __len__(self) -> int:
        return len(self._providers)
    
    def __contains__(self, name: str) -> bool:
        return name in self._providers
    
    def __repr__(self) -> str:
        return f"<ResearchRegistry with {len(self)} providers>"


# Global registry instance
registry = ResearchRegistry()