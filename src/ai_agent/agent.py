import os
from typing import Optional, Dict, List, AsyncGenerator
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from ..commands.base import CommandRegistry
from ..prompts.prompt_manager import SystemPromptManager
import re

class Agent:
    """
    AI Agent that processes natural language inputs and executes corresponding commands.
    
    The Agent uses OpenAI's language models to:
    1. Understand natural language requests
    2. Match them to registered commands
    3. Execute commands with extracted variables
    4. Format responses in a user-friendly way
    
    Attributes:
        client (AsyncOpenAI): OpenAI API client for language model interactions
        command_registry (Optional[CommandRegistry]): Registry of available commands
        prompt_manager (SystemPromptManager): Manager for system prompts
    """

    def __init__(
        self,
        agent_purpose: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the AI Agent with OpenAI client configuration and purpose.
        
        Args:
            agent_purpose (str): Description of the agent's purpose and capabilities
            base_url (Optional[str]): Base URL for OpenAI API. Defaults to environment variable
            api_key (Optional[str]): OpenAI API key. Defaults to environment variable
        """
        # Configure OpenAI client
        self.client = AsyncOpenAI(
            base_url=(base_url or os.getenv("OPENAI_BASE_URL", "")).rstrip('/') + '/v1/',
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        self.command_registry: Optional[CommandRegistry] = None
        self.prompt_manager = SystemPromptManager(agent_purpose)
        
    def initialize_commands(self, command_registry: CommandRegistry) -> None:
        """
        Initialize the command registry for the agent.
        
        Args:
            command_registry (CommandRegistry): Registry containing available commands
            
        Note:
            This must be called before processing any user input.
        """
        self.command_registry = command_registry
    
    async def process_input(self, user_input: str) -> AsyncGenerator[str, None]:
        """
        Process user input through LLM and execute matching commands.
        
        Args:
            user_input (str): Natural language input from the user
            
        Yields:
            str: Response chunks from the LLM or command execution results
            
        Raises:
            RuntimeError: If command registry is not initialized
        """
        if not self.command_registry:
            raise RuntimeError("Command registry not initialized. Call initialize_commands() first.")
            
        # Accumulate full response
        full_response = ""
        async for response_chunk in self._get_llm_response(user_input):
            full_response += response_chunk
            
        # Try to extract command from the complete response
        command_result = self._extract_command(full_response)
        if command_result:
            command_name, variables = command_result
            result, success = self._execute_command(command_name, variables)
            # Get final LLM response with the result
            if success:
                async for formatted_response in self._get_llm_response_with_result(result, command_name):
                    yield formatted_response
            else:
                async for error_response in self._get_llm_error_response(result, command_name):
                    yield error_response
        else:
            yield full_response
    
    def _extract_command(self, text: str) -> Optional[tuple[str, Dict[str, str]]]:
        """
        Extract command and variables from LLM response text.
        
        Args:
            text (str): Text to extract command from
            
        Returns:
            Optional[tuple[str, Dict[str, str]]]: Tuple of (command_name, variables) if found,
                                                None if no command pattern is matched
        """
        if not self.command_registry:
            return None
            
        print(f"Attempting to match text: '{text}'")  # Debug print
        
        # Clean up the text
        text = text.strip()
        
        # Look for command pattern in square brackets
        command_match = re.search(r'\[\[(.*?)\]\]', text)
        if not command_match:
            print("No command pattern found")
            return None
            
        command_text = command_match.group(1)
        print(f"Found command text: {command_text}")
        
        # Try to match with registered commands
        for name, metadata in self.command_registry.commands.items():
            # Create pattern for variable extraction
            var_pattern = metadata.pattern.replace("[[", "").replace("]]", "")
            for var in metadata.variables:
                var_pattern = var_pattern.replace("{" + var.name + "}", f"(?P<{var.name}>[^}}]*)")
            
            print(f"Trying to match against pattern: {var_pattern}")
            match = re.match(f"^{var_pattern}$", command_text)
            
            if match:
                variables = match.groupdict()
                print(f"Found match with variables: {variables}")
                return name, variables
                
        print("No matching command found")
        return None
    
    def _execute_command(self, command_name: str, variables: Dict[str, str]) -> tuple[str, bool]:
        """
        Execute a command with the given variables.
        
        Args:
            command_name (str): Name of the command to execute
            variables (Dict[str, str]): Variables extracted from the command pattern
            
        Returns:
            tuple[str, bool]: Tuple of (result_message, success_flag)
            
        Note:
            The success_flag indicates whether the command executed successfully.
            If False, the result_message contains an error description.
        """
        if not self.command_registry:
            return "Command registry not initialized", False
            
        command = self.command_registry.get_command(command_name)
        if not command:
            return f"No handler registered for command: {command_name}", False
            
        try:
            result = command.handler(**variables)
            return result, True
        except Exception as e:
            return f"Error executing command: {str(e)}", False
    
    async def _get_llm_response(self, user_input: str) -> AsyncGenerator[str, None]:
        """
        Get streaming response from OpenAI's LLM.
        
        Args:
            user_input (str): User's natural language input
            
        Yields:
            str: Response chunks from the language model
            
        Raises:
            RuntimeError: If command registry is not initialized
        """
        if not self.command_registry:
            raise RuntimeError("Command registry not initialized")
            
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.prompt_manager.format_system_prompt(self.command_registry.get_all_commands())},
            {"role": "user", "content": user_input}
        ]
        
        model = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
        max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        async for chunk in stream:
            if chunk and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _get_llm_response_with_result(self, result: str, command_name: str) -> AsyncGenerator[str, None]:
        """
        Get streaming response with command execution result.
        
        Args:
            result (str): Result from command execution
            command_name (str): Name of the executed command
            
        Yields:
            str: Formatted response chunks from the language model
            
        Raises:
            RuntimeError: If command registry is not initialized
            ValueError: If command is not found in registry
        """
        if not self.command_registry:
            raise RuntimeError("Command registry not initialized")
            
        command = self.command_registry.get_command(command_name)
        if not command:
            raise ValueError(f"Command not found: {command_name}")
            
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": command.result_prompt},
            {"role": "user", "content": f"Format this result: {result}"}
        ]
        
        model = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
        max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        async for chunk in stream:
            if chunk and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _get_llm_error_response(self, error: str, command_name: str) -> AsyncGenerator[str, None]:
        """
        Get streaming response for error handling.
        
        Args:
            error (str): Error message from command execution
            command_name (str): Name of the command that failed
            
        Yields:
            str: Formatted error response chunks from the language model
            
        Raises:
            RuntimeError: If command registry is not initialized
            ValueError: If command is not found in registry
        """
        if not self.command_registry:
            raise RuntimeError("Command registry not initialized")
            
        command = self.command_registry.get_command(command_name)
        if not command:
            raise ValueError(f"Command not found: {command_name}")
            
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": command.unsuccessful_prompt},
            {"role": "user", "content": f"Handle this error: {error}"}
        ]
        
        model = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
        max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        async for chunk in stream:
            if chunk and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content 