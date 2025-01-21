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
    Registry for managing AI Agent commands and their metadata.
    
    The CommandRegistry serves as a central repository for all commands that an AI Agent
    can execute. It manages command registration, retrieval, and execution, providing
    a clean interface for the Agent to interact with commands.
    
    Key Features:
    1. Command Registration: Register new commands with their metadata and handlers
    2. Command Retrieval: Look up commands by name with proper error handling
    3. Command Execution: Execute commands with extracted variables
    4. Metadata Management: Store and provide access to command metadata
    5. Pattern Matching: Extract variables from command patterns in user input
    
    Each command in the registry includes:
    - Metadata: Name, description, pattern, variables, etc.
    - Handler: The function that implements the command's functionality
    - Example inputs and responses for LLM training
    - Prompts for formatting success and error responses
    
    Example Usage:
        registry = CommandRegistry()
        
        # Register a command
        registry.register(CommandMetadata(...))
        
        # Execute a command
        result = registry.execute_command("command_name", {"var": "value"})
        
        # Get command metadata
        metadata = registry.get_command("command_name")
    
    Attributes:
        commands (Dict[str, CommandMetadata]): Dictionary mapping command names
            to their complete metadata
        command_handlers (Dict[str, Callable]): Dictionary mapping command names
            to their handler functions
    """
    
    def __init__(self) -> None:
        """Initialize a new command registry."""
        self.commands: Dict[str, CommandMetadata] = {}
        self.command_handlers: Dict[str, Callable] = {}
    
    def register(self, metadata: CommandMetadata) -> None:
        """
        Register a new command with its metadata.
        
        Args:
            metadata (CommandMetadata): Complete metadata for the command
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

    def register_handler(self, command_name: str, handler: Callable) -> None:
        """
        Register a handler function for a specific command.
        
        This method associates a command name with its implementation function.
        The handler function will be called when the command is executed, with
        variables extracted from the command pattern passed as keyword arguments.
        
        Args:
            command_name (str): Name of the command to register the handler for
            handler (Callable): Function that implements the command's functionality
            
        Note:
            The handler function's signature must match the variables defined in
            the command's metadata pattern.
        """
        self.command_handlers[command_name] = handler
        
    def get_command_pattern(self, command_name: str) -> str:
        """
        Get the command pattern for a specific command.
        
        Retrieves the pattern string used to match and extract variables from
        user input for the specified command.
        
        Args:
            command_name (str): Name of the command to get the pattern for
            
        Returns:
            str: The command's pattern string if found, empty string otherwise
            
        Example:
            >>> registry.get_command_pattern("generate_wallet")
            "[[GENERATE_WALLET_{user_id}]]"
        """
        command = self.commands.get(command_name)
        return command.pattern if command else ''
        
    def extract_command(self, text: str) -> tuple[str, Dict[str, str]] | None:
        """
        Extract command and variables from text if present.
        
        Searches the input text for any registered command patterns and extracts
        variables if a match is found. The search is performed using regex pattern
        matching against all registered command patterns.
        
        Args:
            text (str): Text to search for command patterns
            
        Returns:
            tuple[str, Dict[str, str]] | None: A tuple containing:
                - command_name (str): Name of the matched command
                - variables (Dict[str, str]): Dictionary of extracted variables
                Returns None if no command pattern is matched
                
        Example:
            >>> registry.extract_command("[[GENERATE_WALLET_123]]")
            ("generate_wallet", {"user_id": "123"})
        """
        for cmd_name, cmd_info in self.commands.items():
            pattern = cmd_info.pattern.replace('{', '(?P<').replace('}', '>[^}]*)')
            match = re.search(f"\\[\\[{pattern}\\]\\]", text)
            if match:
                return cmd_name, match.groupdict()
        return None
        
    def execute_command(self, command_name: str, variables: Dict[str, str]) -> str:
        """
        Execute a command with the given variables.
        
        Calls the registered handler function for the specified command,
        passing the extracted variables as keyword arguments. The handler
        function is responsible for implementing the command's functionality.
        
        Args:
            command_name (str): Name of the command to execute
            variables (Dict[str, str]): Variables extracted from the command pattern
            
        Returns:
            str: Result message from the command execution
            
        Example:
            >>> registry.execute_command("generate_wallet", {"user_id": "123"})
            "Generated wallet with address: 0x123..."
            
        Note:
            If no handler is registered for the command, returns an error message.
            The handler function must accept the variables as keyword arguments.
        """
        handler = self.command_handlers.get(command_name)
        if not handler:
            return f"No handler registered for command: {command_name}"
        return handler(**variables) 