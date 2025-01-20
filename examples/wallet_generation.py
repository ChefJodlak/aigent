"""
Example implementation of a wallet generation command using the AI Agent framework.

This example demonstrates:
1. Command definition with metadata
2. Success and failure response examples
3. Basic command implementation
4. Agent initialization and usage

The example shows how to:
- Define a command with its metadata
- Provide example responses for success and failure cases
- Implement the command handler
- Initialize and use the AI Agent
"""

import os
import asyncio
from dotenv import load_dotenv
from src.ai_agent.agent import Agent
from src.commands.base import command, CommandRegistry, VariableMetadata

@command(
    name="generate_wallet",
    description="Generates a new cryptocurrency wallet",
    explanation="Creates a secure cryptocurrency wallet with public and private keys using industry-standard encryption. The wallet is uniquely associated with the user's ID for future reference.",
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
    example_success_responses=[
        {
            "result": "Generated example wallet with address: ajiosdaiosdiasjd",
            "response": """Great news! I've successfully generated a new cryptocurrency wallet for you. 
Your wallet address is: ajiosdaiosdiasjd

Next steps:
1. Make sure to securely store your wallet credentials
2. Consider setting up two-factor authentication
3. You can now start receiving cryptocurrencies to this wallet

Need help with anything else?"""
        },
        {
            "result": "Generated example wallet with address: xkcd123456789",
            "response": """Your new cryptocurrency wallet has been successfully created!

Wallet Details:
✓ Wallet Address: xkcd123456789
✓ Encryption: Industry-standard protocols
✓ Status: Active and ready

To get started:
1. Back up your wallet credentials
2. Review our security best practices
3. You're all set to receive crypto assets

Let me know if you need any assistance with your new wallet!"""
        }
    ],
    example_failed_responses=[
        {
            "result": "Error: Network connection failed",
            "response": """I apologize, but I wasn't able to generate your wallet at this moment due to network connectivity issues.

What happened:
- The connection to our secure wallet generation service was interrupted
- This is a temporary issue that helps maintain the security of the wallet creation process

Steps you can take:
1. Check your internet connection
2. Wait a few minutes and try again
3. If the issue persists, try using a different network

Rest assured that no partial wallet was created, and your security hasn't been compromised. Would you like to try generating the wallet again?"""
        },
        {
            "result": "Error: Rate limit exceeded",
            "response": """I apologize, but I couldn't create your wallet right now due to high system load.

Technical Details:
- Our security measures include rate limiting to prevent abuse
- The system is currently processing many wallet generation requests

Recommended actions:
1. Wait for approximately 5 minutes
2. Try your request again
3. If you need immediate assistance, contact our support team

Your security is our priority - this measure helps ensure all wallets are generated with proper security protocols. Would you like to try again in a few minutes?"""
        }
    ],
    result_prompt="""You are a cryptocurrency assistant presenting wallet generation results.
Never type a user id in the response.
Here are some example responses for different results:
{examples}

Format the current result in a similar style, but with your own unique wording.""",
    unsuccessful_prompt="""You are a cryptocurrency assistant handling wallet generation failures.
When responding to wallet generation errors:
1. Explain what went wrong with the wallet creation process
2. Provide specific reasons why the wallet generation might have failed
3. Suggest steps the user can take to resolve the issue
4. If applicable, recommend alternative approaches or timing
5. Maintain a security-conscious yet helpful tone

Here are some example responses for different errors:
{examples}

Format the current error in a similar style, but with your own unique wording.

Remember to:
- Be clear about the security implications
- Provide specific troubleshooting steps
- Reassure about data safety
- Guide towards successful retry if appropriate"""
)
def generate_wallet(user_id: str) -> str:
    """
    Example command implementation for wallet generation.
    
    This function simulates wallet generation by returning a fixed response.
    In a real implementation, this would:
    1. Generate cryptographic keys
    2. Store wallet data securely
    3. Return the wallet address
    
    Args:
        user_id (str): The unique identifier of the user requesting the wallet.
        
    Returns:
        str: A message indicating successful wallet generation with an address.
        
    Raises:
        ValueError: If the user_id is "error" (used for testing error handling).
    """
    if user_id == "error":
        raise ValueError("Simulated error for testing")
    return "Generated example wallet with address: xxxxxxxxxxxxxx"

async def main():
    """
    Example usage of the AI Agent with wallet generation command.
    
    This function demonstrates:
    1. Loading environment variables
    2. Initializing the AI Agent with a specific purpose
    3. Setting up the command registry
    4. Processing a natural language request
    5. Handling the streaming response
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize the agent with its purpose
    agent = Agent(
        agent_purpose="""I am a cryptocurrency assistant that helps users manage their digital assets.
I can create wallets, provide information about cryptocurrencies, and assist with basic operations.
I aim to make cryptocurrency management simple and accessible for all users.""",
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize commands
    registry = CommandRegistry.get_instance()
    agent.initialize_commands(registry)
    
    # Example: Generate a wallet (user_id will be appended by frontend)
    print("Testing wallet generation...")
    async for response_chunk in agent.process_input(
        "I need a new cryptocurrency wallet"
    ):
        print(response_chunk, end="", flush=True)
    print("\n")

if __name__ == "__main__":
    asyncio.run(main()) 