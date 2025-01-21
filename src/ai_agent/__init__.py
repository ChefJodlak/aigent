"""
Aigent - A natural language command processing system powered by LLMs.
"""

from .agent import Agent
from ._version import version as __version__, version_tuple

__all__ = ['Agent', '__version__', 'version_tuple'] 