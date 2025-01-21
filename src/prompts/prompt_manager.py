"""
Prompt management module for the AI Agent framework.

This module handles:
1. System prompt generation and formatting
2. Variable metadata management
3. Command prompt templates

The module ensures consistent prompt formatting and provides a structured way
to manage different types of prompts used throughout the system.
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class VariableMetadata:
    """
    Metadata for a command variable.
    
    This class defines the structure and documentation for variables
    that can be used in command patterns.
    
    Attributes:
        name (str): Name of the variable as used in patterns (e.g., 'user_id')
        description (str): Human-readable description of what the variable represents
        example (str): Example value for the variable to help users understand its format
    """
    name: str
    description: str
    example: str

@dataclass
class CommandMetadata:
    """
    Metadata for a command in the prompt management system.
    
    This class defines the structure for command metadata used in prompt generation.
    It includes all the information needed to format system prompts and handle
    command responses.
    
    Attributes:
        name (str): Unique identifier for the command
        description (str): Short description of what the command does
        explanation (str): Detailed explanation of how the command works
        pattern (str): Pattern string with variable placeholders
        variables (List[VariableMetadata]): List of variables used in the pattern
        example_inputs (List[str]): Example natural language inputs
        result_prompt (str): Template for formatting successful results
        unsuccessful_prompt (str): Template for handling command failures
    """
    name: str
    description: str
    explanation: str  # Detailed explanation of how the command works
    pattern: str
    variables: List[VariableMetadata]
    example_inputs: List[str]
    result_prompt: str  # Specific prompt for formatting this command's results
    unsuccessful_prompt: str  # Specific prompt for handling command failures

class SystemPromptManager:
    """
    Manager for system prompts in the AI Agent framework.
    
    This class is responsible for:
    - Maintaining the agent's purpose and personality
    - Formatting system prompts with command information
    - Ensuring consistent prompt structure across the system
    
    The prompt manager helps maintain a consistent voice and behavior
    for the AI agent across different interactions.
    """
    
    def __init__(self, agent_purpose: str):
        """
        Initialize the system prompt manager.
        
        Args:
            agent_purpose (str): Description of the agent's purpose and capabilities,
                               used to maintain consistent behavior
        """
        self.agent_purpose = agent_purpose
        
    def format_system_prompt(self, commands: Dict[str, Dict[str, Any]]) -> str:
        """
        Format the system prompt with available commands.
        
        This method creates a comprehensive system prompt that includes:
        1. The agent's purpose and personality
        2. Available commands and their descriptions
        3. Command patterns and variables
        4. Example inputs for each command
        
        Args:
            commands (Dict[str, Dict[str, Any]]): Dictionary mapping command names
                to their metadata, including patterns, descriptions, and examples
                
        Returns:
            str: Formatted system prompt ready for use with the language model
        """
        prompt = f"""You are an AI assistant with the following purpose:
{self.agent_purpose}

When a user's request matches one of the available commands:
1. DO NOT explain what you're going to do
2. DO NOT add any additional text or newlines
3. ONLY respond with the exact command pattern, replacing variables with their values
4. The response should be EXACTLY in the format shown in the Pattern field
5. Variable names are case-sensitive, use them exactly as shown

If the request doesn't match any command, respond naturally without using any command patterns.

Available commands:
"""
        for name, cmd in commands.items():
            prompt += f"\n• {name}:"
            prompt += f"\n  Description: {cmd['description']}"
            prompt += f"\n  Explanation: {cmd['explanation']}"
            prompt += f"\n  Pattern: {cmd['pattern']}"
            prompt += "\n  Variables:"
            for var in cmd['variables']:
                prompt += f"\n    - {var['name']}: {var['description']} (Example: {var['example']})"
            prompt += "\n  Example inputs:"
            for example in cmd['example_inputs']:
                prompt += f"\n    - {example}"
            prompt += "\n"
            
        prompt += "\nRemember: When using a command, output ONLY the command pattern with no additional text or newlines."
        return prompt
    
    def format_result_prompt(self) -> str:
        return f"""You are an AI assistant that formats command results in a user-friendly way.
Your purpose is: {self.agent_purpose}

Take the technical result and present it in a clear, concise manner that aligns with the agent's purpose.""" 