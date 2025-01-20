"""
Command Registry module for the AI Agent framework.

This module provides a centralized registry for managing commands and their metadata.
It implements a singleton pattern to ensure a single source of truth for command
information across the entire application.

Key features:
1. Singleton command registry
2. Command registration and retrieval
3. Command metadata management
4. Command lookup and validation

The registry serves as the central hub for all command-related operations,
ensuring consistency and proper command handling throughout the system.
"""

import json
from typing import Dict, Optional, Any, Callable
import re
from pathlib import Path
from dataclasses import dataclass
from .base import CommandMetadata

class CommandRegistry:
    """
    Singleton registry for managing AI Agent commands.
    
    This class implements the Singleton pattern to ensure that there is only
    one instance of the command registry throughout the application's lifecycle.
    It serves as the central repository for all command metadata and handlers.
    
    The registry provides:
    - Safe command registration
    - Command metadata retrieval
    - Command existence validation
    - Command metadata formatting for prompts
    
    Attributes:
        commands (Dict[str, CommandMetadata]): Dictionary mapping command names
            to their complete metadata
        _instance (Optional[CommandRegistry]): Singleton instance reference
        _initialized (bool): Flag to track initialization status
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls) -> 'CommandRegistry':
        """
        Create or return the singleton instance of CommandRegistry.
        
        This method implements the Singleton pattern, ensuring that only
        one instance of CommandRegistry exists in the application.
        
        Returns:
            CommandRegistry: The singleton instance of the registry
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """
        Initialize the command registry.
        
        This method is called when the registry is first created. It initializes
        the commands dictionary only once, even if __init__ is called multiple times
        due to the singleton pattern.
        """
        if not self._initialized:
            self.commands: Dict[str, CommandMetadata] = {}
            self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'CommandRegistry':
        """
        Get the singleton instance of the command registry.
        
        This class method provides a standard way to access the singleton
        instance of the registry from anywhere in the application.
        
        Returns:
            CommandRegistry: The singleton instance of the registry
        """
        if cls._instance is None:
            cls._instance = CommandRegistry()
        return cls._instance
    
    def register(self, metadata: CommandMetadata) -> None:
        """
        Register a new command with its metadata.
        
        This method adds a new command to the registry or updates an existing one.
        The command's metadata includes all necessary information for command
        execution, pattern matching, and response formatting.
        
        Args:
            metadata (CommandMetadata): Complete metadata for the command,
                including name, description, pattern, variables, and handler
        """
        self.commands[metadata.name] = metadata
    
    def get_command(self, name: str) -> Optional[CommandMetadata]:
        """
        Retrieve command metadata by name.
        
        This method safely retrieves command metadata, returning None if
        the command doesn't exist rather than raising an exception.
        
        Args:
            name (str): Name of the command to retrieve
            
        Returns:
            Optional[CommandMetadata]: Command metadata if found, None otherwise
        """
        return self.commands.get(name)
    
    def get_all_commands(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered commands in a format suitable for prompt generation.
        
        This method transforms the internal command metadata into a format
        that can be easily used to generate system prompts, including all
        necessary information about each command's usage and behavior.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary containing formatted command
                metadata for all registered commands, with command names as keys
        """
        return {
            name: {
                "pattern": cmd.pattern,
                "description": cmd.description,
                "explanation": cmd.explanation,
                "variables": [
                    {"name": var.name, "description": var.description, "example": var.example}
                    for var in cmd.variables
                ],
                "example_inputs": cmd.example_inputs
            }
            for name, cmd in self.commands.items()
        }
    
    def load_commands(self, commands_file: str) -> None:
        """Load commands from JSON configuration file."""
        with open(commands_file, 'r') as f:
            self.commands = json.load(f)
            
    def register_handler(self, command_name: str, handler: Callable) -> None:
        """Register a handler function for a specific command."""
        self.command_handlers[command_name] = handler
        
    def get_command_pattern(self, command_name: str) -> str:
        """Get the command pattern for a specific command."""
        return self.commands.get(command_name, {}).get('command', '')
        
    def extract_command(self, text: str) -> tuple[str, Dict[str, str]] | None:
        """Extract command and variables from text if present."""
        for cmd_name, cmd_info in self.commands.items():
            pattern = cmd_info['command'].replace('{', '(?P<').replace('}', '>[^}]*)')
            match = re.search(f"\\[\\[{pattern}\\]\\]", text)
            if match:
                return cmd_name, match.groupdict()
        return None
        
    def execute_command(self, command_name: str, variables: Dict[str, str]) -> str:
        """Execute a command with the given variables."""
        handler = self.command_handlers.get(command_name)
        if not handler:
            return f"No handler registered for command: {command_name}"
        return handler(**variables) 