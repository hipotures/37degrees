#!/usr/bin/env python3
"""
Scene file handler for loading and saving scene files in different formats.
Supports JSON and YAML formats with automatic format detection.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Protocol
from abc import ABC, abstractmethod


class SceneFileHandler(Protocol):
    """Protocol for scene file handlers."""
    
    def load(self, file_path: Path) -> Dict[str, Any]:
        """Load scene data from file."""
        ...
    
    def save(self, data: Dict[str, Any], file_path: Path) -> None:
        """Save scene data to file."""
        ...


class JSONSceneHandler:
    """Handler for JSON scene files."""
    
    def load(self, file_path: Path) -> Dict[str, Any]:
        """Load scene data from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save(self, data: Dict[str, Any], file_path: Path) -> None:
        """Save scene data to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


class YAMLSceneHandler:
    """Handler for YAML scene files."""
    
    def load(self, file_path: Path) -> Dict[str, Any]:
        """Load scene data from YAML file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save(self, data: Dict[str, Any], file_path: Path) -> None:
        """Save scene data to YAML file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, 
                     default_flow_style=False,
                     allow_unicode=True,
                     sort_keys=False,
                     width=120)


class SceneFileHandlerFactory:
    """Factory for creating appropriate scene file handlers."""
    
    _handlers = {
        '.json': JSONSceneHandler,
        '.yaml': YAMLSceneHandler,
        '.yml': YAMLSceneHandler
    }
    
    @classmethod
    def get_handler(cls, file_path: Path = None, format_type: str = None) -> SceneFileHandler:
        """
        Get appropriate handler based on file extension or format type.
        
        Args:
            file_path: Path to file (uses extension to determine format)
            format_type: Explicit format type ('json' or 'yaml')
            
        Returns:
            Appropriate SceneFileHandler instance
            
        Raises:
            ValueError: If format cannot be determined or is not supported
        """
        if format_type:
            format_type = format_type.lower()
            if format_type == 'json':
                return JSONSceneHandler()
            elif format_type in ('yaml', 'yml'):
                return YAMLSceneHandler()
            else:
                raise ValueError(f"Unsupported format type: {format_type}")
        
        if file_path:
            extension = file_path.suffix.lower()
            handler_class = cls._handlers.get(extension)
            if handler_class:
                return handler_class()
            else:
                raise ValueError(f"Unsupported file extension: {extension}")
        
        raise ValueError("Either file_path or format_type must be provided")
    
    @classmethod
    def load_scene(cls, file_path: Path) -> Dict[str, Any]:
        """Convenience method to load a scene file."""
        handler = cls.get_handler(file_path=file_path)
        return handler.load(file_path)
    
    @classmethod
    def save_scene(cls, data: Dict[str, Any], file_path: Path, format_type: str = None) -> None:
        """Convenience method to save a scene file."""
        handler = cls.get_handler(file_path=file_path, format_type=format_type)
        handler.save(data, file_path)