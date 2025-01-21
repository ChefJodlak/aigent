"""
Command system for the AI agent.
"""

from .base import CommandRegistry, CommandMetadata, command
from ..prompts.prompt_manager import VariableMetadata

__all__ = [
    'CommandRegistry',
    'CommandMetadata',
    'command',
    'VariableMetadata'
] 