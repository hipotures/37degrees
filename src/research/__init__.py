"""
Research module for generating book review content using AI search APIs
"""

from .base import BaseResearchProvider, ResearchError
from .registry import ResearchRegistry, registry

__all__ = ['BaseResearchProvider', 'ResearchError', 'ResearchRegistry', 'registry']