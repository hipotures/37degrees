"""
Configuration management for 37degrees project
Handles loading, validation, and environment variable substitution
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from functools import lru_cache
from rich.console import Console
from dotenv import load_dotenv

console = Console()


class ConfigError(Exception):
    """Configuration related errors"""
    pass


class Config:
    """Central configuration manager"""
    
    def __init__(self, config_path: Optional[Path] = None, env_file: Optional[Path] = None):
        """Initialize configuration
        
        Args:
            config_path: Path to main config file (default: config/settings.yaml)
            env_file: Path to .env file (default: .env in project root)
        """
        self.config_path = config_path or Path("config/settings.yaml")
        self.env_file = env_file or Path(".env")
        self._config: Dict[str, Any] = {}
        self._overrides: Dict[str, Any] = {}
        
        # Load environment variables from .env file
        self._load_env_file()
        
        # Load configuration
        self.load()
    
    def _load_env_file(self) -> None:
        """Load environment variables from .env file"""
        if self.env_file.exists():
            load_dotenv(self.env_file, override=False)
            console.print(f"[green]✓ Loaded environment variables from {self.env_file}[/green]")
        else:
            # Try to find .env in parent directories
            current = Path.cwd()
            while current != current.parent:
                env_path = current / ".env"
                if env_path.exists():
                    load_dotenv(env_path, override=False)
                    console.print(f"[green]✓ Loaded environment variables from {env_path}[/green]")
                    break
                current = current.parent
    
    def load(self) -> None:
        """Load configuration from file"""
        if not self.config_path.exists():
            console.print(f"[yellow]Config file not found: {self.config_path}, using defaults[/yellow]")
            self._config = self._get_defaults()
            return
        
        try:
            with open(self.config_path, 'r') as f:
                raw_config = yaml.safe_load(f)
            
            # Process environment variable substitution
            self._config = self._substitute_env_vars(raw_config)
            
            # Apply any overrides
            self._apply_overrides()
            
            console.print(f"[green]✓ Loaded configuration from {self.config_path}[/green]")
            
        except Exception as e:
            raise ConfigError(f"Failed to load config: {e}")
    
    def _substitute_env_vars(self, config: Any) -> Any:
        """Recursively substitute environment variables in config
        
        Supports formats:
        - ${VAR_NAME} - required variable
        - ${VAR_NAME:-default} - with default value
        """
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Find all environment variable references
            pattern = r'\$\{([^}]+)\}'
            
            def replacer(match):
                var_expr = match.group(1)
                
                # Check if default value is provided
                if ':-' in var_expr:
                    var_name, default_value = var_expr.split(':-', 1)
                    return os.getenv(var_name, default_value)
                else:
                    value = os.getenv(var_expr)
                    if value is None:
                        # Only warn for required variables (not those with defaults)
                        if ':-' not in match.group(0):
                            console.print(f"[yellow]Warning: Environment variable {var_expr} not set[/yellow]")
                        return match.group(0)  # Return original if not found
                    return value
            
            return re.sub(pattern, replacer, config)
        else:
            return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key
        
        Args:
            key: Dot-separated key (e.g., 'services.generators.default')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        # Check overrides first
        if key in self._overrides:
            return self._overrides[key]
        
        # Navigate through nested config
        parts = key.split('.')
        value = self._config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value (runtime override)
        
        Args:
            key: Dot-separated key
            value: Value to set
        """
        self._overrides[key] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section
        
        Args:
            section: Section name (e.g., 'video', 'services')
            
        Returns:
            Configuration section as dict
        """
        return self.get(section, {})
    
    def _apply_overrides(self) -> None:
        """Apply any runtime overrides to config"""
        for key, value in self._overrides.items():
            parts = key.split('.')
            target = self._config
            
            # Navigate to parent
            for part in parts[:-1]:
                if part not in target:
                    target[part] = {}
                target = target[part]
            
            # Set value
            if parts:
                target[parts[-1]] = value
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'project': {
                'name': '37degrees',
                'version': '2.0.0'
            },
            'services': {
                'generators': {
                    'default': 'invokeai',
                    'config_file': 'config/generators.yaml'
                }
            },
            'video': {
                'resolution': '1080x1920',
                'fps': 30,
                'duration_per_slide': 3.5
            },
            'paths': {
                'books_dir': 'books',
                'collections_dir': 'collections',
                'output_dir': 'output'
            },
            'development': {
                'debug': False,
                'verbose': False
            }
        }
    
    def validate(self, schema: Optional[Dict[str, Any]] = None) -> List[str]:
        """Validate configuration against schema
        
        Args:
            schema: Optional validation schema
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Basic validation
        required_sections = ['project', 'services', 'paths']
        for section in required_sections:
            if section not in self._config:
                errors.append(f"Missing required section: {section}")
        
        # Validate paths exist
        paths = self.get_section('paths')
        for name, path in paths.items():
            if name.endswith('_dir') and not Path(path).exists():
                console.print(f"[yellow]Warning: {name} does not exist: {path}[/yellow]")
        
        return errors
    
    def save(self, path: Optional[Path] = None) -> None:
        """Save current configuration to file
        
        Args:
            path: Output path (default: original config path)
        """
        output_path = path or self.config_path
        
        # Merge config with overrides
        merged_config = self._config.copy()
        self._apply_overrides()
        
        with open(output_path, 'w') as f:
            yaml.safe_dump(merged_config, f, default_flow_style=False, sort_keys=False)
        
        console.print(f"[green]Configuration saved to {output_path}[/green]")
    
    def __repr__(self) -> str:
        return f"<Config from {self.config_path}>"


# Global configuration instance
_config: Optional[Config] = None


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Get global configuration instance
    
    Returns:
        Global Config instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload configuration from file
    
    Returns:
        Reloaded Config instance
    """
    global _config
    get_config.cache_clear()
    _config = Config()
    return _config


def get(key: str, default: Any = None) -> Any:
    """Convenience function to get config value
    
    Args:
        key: Dot-separated key
        default: Default value
        
    Returns:
        Configuration value
    """
    return get_config().get(key, default)


def set_override(key: str, value: Any) -> None:
    """Set configuration override
    
    Args:
        key: Dot-separated key
        value: Value to set
    """
    get_config().set(key, value)