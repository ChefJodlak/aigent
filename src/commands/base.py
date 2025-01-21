"""
Base module for command handling in the AI Agent framework.

This module provides the core functionality for:
1. Command metadata definition
2. Command registration and management
3. Command execution and variable handling

The module uses a decorator-based approach to register commands with their metadata,
making it easy to add new commands while maintaining a consistent structure.
"""

from typing import Callable, Dict, List, TypeVar, Optional, Any
from dataclasses import dataclass
from functools import wraps
from ..prompts.prompt_manager import VariableMetadata

T = TypeVar('T')

@dataclass
class CommandMetadata:
    """
    Metadata for a command in the AI Agent system.
    
    This class holds all the information needed to:
    - Identify and describe a command
    - Parse command patterns and variables
    - Execute the command handler
    - Format success and error responses
    
    Attributes:
        name (str): Unique identifier for the command
        description (str): Short description of what the command does
        explanation (str): Detailed explanation of the command's functionality
        pattern (str): Pattern string with variable placeholders (e.g., "[[COMMAND_{var}]]")
        variables (List[VariableMetadata]): List of variables used in the pattern
        example_inputs (List[str]): Example natural language inputs that should trigger this command
        handler (Callable): Function that implements the command's functionality
        result_prompt (str): Template for formatting successful results
        unsuccessful_prompt (str): Template for formatting error messages
        example_success_responses (List[Dict[str, str]]): Example successful responses
        example_failed_responses (List[Dict[str, str]]): Example error responses
    """
    name: str
    description: str
    explanation: str
    pattern: str
    variables: List[VariableMetadata]
    example_inputs: List[str]
    handler: Callable
    result_prompt: str
    unsuccessful_prompt: str
    example_success_responses: List[Dict[str, str]]
    example_failed_responses: List[Dict[str, str]]

class CommandRegistry:
    """
    Singleton registry for managing all available commands.
    
    This class maintains a centralized registry of all commands and their metadata,
    providing methods to register new commands and retrieve command information.
    
    The registry ensures that:
    - Each command has a unique name
    - All required metadata is provided
    - Commands can be easily looked up by name
    """
    
    _instance = None
    _initialized = False
    commands: Dict[str, CommandMetadata]
    
    def __new__(cls):
        """
        Create or return the singleton instance of CommandRegistry.
        
        Returns:
            CommandRegistry: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the command registry if not already initialized."""
        if not self._initialized:
            self.commands = {}
            self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'CommandRegistry':
        """
        Get the singleton instance of CommandRegistry.
        
        Returns:
            CommandRegistry: The singleton instance
        """
        if cls._instance is None:
            cls._instance = CommandRegistry()
        return cls._instance
    
    def register(self, metadata: CommandMetadata) -> None:
        """
        Register a command with its metadata.
        
        Args:
            metadata (CommandMetadata): Complete metadata for the command
        """
        self.commands[metadata.name] = metadata
    
    def get_command(self, name: str) -> Optional[CommandMetadata]:
        """
        Get command metadata by name.
        
        Args:
            name (str): Name of the command to retrieve
            
        Returns:
            Optional[CommandMetadata]: Command metadata if found, None otherwise
        """
        return self.commands.get(name)
    
    def get_all_commands(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all commands in a format suitable for configuration.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping command names to their metadata
                in a format suitable for system prompt generation
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

def command(
    registry: CommandRegistry,
    name: str,
    description: str,
    explanation: str,
    pattern: str,
    variables: List[VariableMetadata],
    example_inputs: List[str],
    example_success_responses: List[Dict[str, str]],
    example_failed_responses: List[Dict[str, str]],
    result_prompt: str,
    unsuccessful_prompt: str
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to register a function as a command.
    
    Args:
        registry (CommandRegistry): Registry to register the command in
        name (str): Unique identifier for the command
        description (str): Short description of what the command does
        explanation (str): Detailed explanation of the command's functionality
        pattern (str): Pattern string with variable placeholders
        variables (List[VariableMetadata]): List of variables used in the pattern
        example_inputs (List[str]): Example natural language inputs
        example_success_responses (List[Dict[str, str]]): Example successful responses
        example_failed_responses (List[Dict[str, str]]): Example error responses
        result_prompt (str): Template for formatting successful results
        unsuccessful_prompt (str): Template for formatting error messages
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return func(*args, **kwargs)
        
        # Format result prompt with success examples
        formatted_result_prompt = result_prompt.format(
            examples="\n\n".join(
                f"For result: {ex['result']}\nResponse:\n{ex['response']}"
                for ex in example_success_responses
            )
        )
        
        # Format unsuccessful prompt with failure examples
        formatted_unsuccessful_prompt = unsuccessful_prompt.format(
            examples="\n\n".join(
                f"For error: {ex['result']}\nResponse:\n{ex['response']}"
                for ex in example_failed_responses
            )
        )
        
        # Register the command
        metadata = CommandMetadata(
            name=name,
            description=description,
            explanation=explanation,
            pattern=pattern,
            variables=variables,
            example_inputs=example_inputs,
            handler=func,
            result_prompt=formatted_result_prompt,
            unsuccessful_prompt=formatted_unsuccessful_prompt,
            example_success_responses=example_success_responses,
            example_failed_responses=example_failed_responses
        )
        registry.register(metadata)
        return wrapper
    return decorator 