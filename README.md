# AI Command Processing Agent

This project implements an AI agent that processes natural language commands through an LLM (OpenAI) and executes corresponding actions based on a structured command system.

## Features

- Natural language processing using OpenAI's GPT models
- Extensible command system with JSON-based configuration
- Command pattern matching and variable extraction
- Customizable system prompts
- Easy integration of new commands

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## Project Structure

```
.
├── src/
│   ├── agent.py           # Main agent implementation
│   ├── commands/
│   │   ├── command_registry.py  # Command management system
│   │   └── example_commands.py  # Example command implementations
│   └── prompts/
│       └── system_prompts.py    # LLM system prompts
├── commands.json          # Command definitions
├── main.py               # Example usage
└── requirements.txt      # Project dependencies
```

## Adding New Commands

1. Add command definition to `commands.json`:
   ```json
   {
     "command_name": {
       "command": "[[COMMAND_NAME_{VARIABLE}]]",
       "variables": ["VARIABLE"],
       "example_user_inputs": [
         "Example natural language input 1",
         "Example natural language input 2"
       ]
     }
   }
   ```

2. Implement command handler in a commands file:
   ```python
   def handle_command(variable: str) -> str:
       return f"Command result for {variable}"
   ```

3. Register the handler in the Agent initialization:
   ```python
   self.command_registry.register_handler("command_name", handle_command)
   ```

## Usage

Run the example script:
```bash
python main.py
```

Or use the Agent in your code:
```python
from src.agent import Agent

agent = Agent("commands.json")
response = agent.process_user_input("Your command here", "user_id")
print(response)
``` 