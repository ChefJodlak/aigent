# 🤖 Aigent

[![PyPI version](https://badge.fury.io/py/aigent.svg)](https://badge.fury.io/py/aigent)
[![Python Version](https://img.shields.io/pypi/pyversions/aigent.svg)](https://pypi.org/project/aigent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> A powerful AI agent framework for natural language command processing using LLMs.

Aigent is a Python framework that enables seamless integration of natural language commands with your applications. Built on top of OpenAI's GPT models, it provides a flexible command system that translates natural language into structured actions.

## ✨ Features

- 🎯 **Natural Language Processing**: Process user commands using state-of-the-art LLMs
- 🔧 **Extensible Command System**: Easy-to-use decorator-based command registration
- 🎨 **Customizable Prompts**: Flexible system prompt management for different use cases
- 🚀 **Async Support**: Built with asyncio for high-performance applications
- 🛠️ **Type Safety**: Full type hints and Pydantic models for robust code
- 📦 **Modern Python**: Built for Python 3.8+ with modern best practices

## 🚀 Quick Start

### Installation

```bash
pip install aigent
# or with Poetry
poetry add aigent
```

### Basic Usage

```python
from aigent import Agent

# Initialize the agent with custom parameters
agent = Agent(
    agent_purpose="Help users manage their tasks",
    base_url="https://api.openai.com/v1",
    api_key="your-api-key",
    model_name="gpt-3.5-turbo",      # Default model
    max_tokens=1000,                  # Maximum response length
    temperature=0.7,                  # Controls randomness (0.0 to 1.0)
    frequency_penalty=0.0,            # Reduces repetition (-2.0 to 2.0)
    presence_penalty=0.0              # Encourages diversity (-2.0 to 2.0)
)

# Process user input with streaming response
async def main():
    async for response in agent.process_input("Create a new task called 'Write documentation'"):
        print(response, end="", flush=True)
```

### Creating Custom Commands

The command system in Aigent is powerful and flexible. Here's a comprehensive example showing advanced features:

```python
from aigent.commands import CommandRegistry, command, VariableMetadata

# Create a command registry
registry = CommandRegistry()

@command(
    registry=registry,
    name="generate_wallet",
    description="Generates a new cryptocurrency wallet",
    explanation="Creates a secure cryptocurrency wallet with public and private keys using industry-standard encryption.",
    pattern="[[GENERATE_WALLET_{user_id}]]",
    variables=[
        VariableMetadata(
            name="user_id",
            description="Unique identifier of the user requesting the wallet",
            example="user123"
        )
    ],
    example_inputs=[
        "Please generate me a wallet",
        "Create me a new wallet",
        "I need a cryptocurrency wallet"
    ],
    # Example responses for successful operations
    example_success_responses=[
        {
            "result": "Generated wallet with address: 0x123...",
            "response": """Great news! I've generated your new cryptocurrency wallet.
            
                            Wallet Details:
                            ✓ Address: 0x123...
                            ✓ Status: Active and ready

                            Next steps:
                            1. Back up your credentials
                            2. Set up 2FA
                            3. You're ready to receive crypto!"""
        }
    ],
    # Example responses for error handling
    example_failed_responses=[
        {
            "result": "Error: Network connection failed",
            "response": """I couldn't generate your wallet due to network issues.

                            Troubleshooting steps:
                            1. Check your connection
                            2. Wait a few minutes
                            3. Try again

                            Your security wasn't compromised. Want to retry?"""
        }
    ],
    # Template for formatting successful results
    result_prompt="""You are a cryptocurrency assistant presenting wallet generation results.
Format the current result in a user-friendly way.
Examples of good responses: {examples}""",
    # Template for formatting errors
    unsuccessful_prompt="""You are a cryptocurrency assistant handling wallet generation failures.
Explain what went wrong and provide next steps.
Examples of good responses: {examples}"""
)
def generate_wallet(user_id: str) -> str:
    if user_id == "error":
        raise ValueError("Wallet generation failed")
    return f"Generated wallet with address: 0x{user_id}123..."

# Initialize agent with commands
agent = Agent(
    agent_purpose="I am a cryptocurrency assistant that helps users manage their digital assets.",
    base_url="https://api.openai.com/v1",
    api_key="your-api-key",
    model_name="gpt-3.5-turbo",
    max_tokens=1000
)
agent.initialize_commands(registry)

# Use the agent
async def main():
    async for response in agent.process_input("I need a new crypto wallet"):
        print(response, end="", flush=True)
```

Key Features Demonstrated:
- 🎯 **Rich Command Metadata**: Comprehensive command description and explanation
- 📝 **Example Inputs**: Natural language examples for better LLM understanding
- ✨ **Response Templates**: Customizable success and error message formatting
- 🔄 **Error Handling**: Structured approach to handling and presenting errors
- 🎨 **Response Examples**: Pre-defined examples for consistent output formatting
- 📚 **Type Hints**: Full type annotations for better code maintainability

## 🎯 Use Cases

- 🤖 **Chatbots**: Build conversational interfaces that can execute actions
- 🔧 **Task Automation**: Create natural language interfaces for automation tasks
- 🎮 **Game Commands**: Implement natural language controls in games
- 🏢 **Business Logic**: Wrap complex business operations in simple commands
- 🔍 **Search & Retrieval**: Create intelligent search interfaces

### Core Components

- **Agent**: The main class that processes user input and manages commands
- **CommandRegistry**: Manages the registration and execution of commands
- **SystemPromptManager**: Handles system prompts and their formatting

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/ChefJodlak/aigent.git
cd aigent

# Install dependencies with Poetry
poetry install

# Activate virtual environment
poetry shell
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

Rafal Jodełka - [@ChefJodlak](https://github.com/ChefJodlak) - rafaljodlak@gmail.com

Project Link: [https://github.com/ChefJodlak/aigent](https://github.com/ChefJodlak/aigent) 