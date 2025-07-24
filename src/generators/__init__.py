"""
Image generators plugin system for 37degrees
"""

from .base import BaseImageGenerator, GeneratorError
from .registry import GeneratorRegistry, registry

__all__ = ['BaseImageGenerator', 'GeneratorError', 'GeneratorRegistry', 'registry']