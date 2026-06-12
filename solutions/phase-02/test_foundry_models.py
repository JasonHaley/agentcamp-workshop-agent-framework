"""
Phase 2: Test Foundry Models Connection
Run with: python test_foundry_models.py

This phase verifies that your Foundry connection works correctly

Prerequisites:
- FOUNDRY_MODEL and FOUNDRY_PROJECT_ENDPOINT set in .env file
"""

import asyncio
import os
from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()


async def main():
    """Test connection to Foundry using FoundryChatClient."""

    print("🔄 Connecting to Foundry...")

    # Create an async OpenAI client pointing to GitHub Models
    client = FoundryChatClient(
        project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        model=os.getenv("FOUNDRY_MODEL"),
        credential=DefaultAzureCredential()
    )

    # Test the connectioon
    print("📤 Sending test message...")
    agent = Agent(
        client=client,
        name="HelloAgent",
        instructions="You are a friendly assistant. Keep your answers brief.",
    )
        
    result = await agent.run("Say 'Hello from Foundry!' and nothing else.")
    print(f"Agent: {result}")
    print("✅ Connection successful!")


if __name__ == "__main__":
    asyncio.run(main())