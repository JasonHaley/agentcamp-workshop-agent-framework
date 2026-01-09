"""
Phase 2: Test GitHub Models Connection
Run with: python test_github_models.py

This phase verifies that your GitHub Models connection works correctly
using the OpenAI library directly.

Prerequisites:
- GITHUB_TOKEN set in .env file
- openai package installed
"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()


async def main():
    """Test connection to GitHub Models using OpenAI client."""

    print("🔄 Connecting to GitHub Models...")

    # Create an async OpenAI client pointing to GitHub Models
    client = AsyncOpenAI(
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.github.ai/inference",
    )

    # Test the connection
    print("📤 Sending test message...")
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "Say 'Hello from GitHub Models!' and nothing else.",
            }
        ],
    )

    result_text = response.choices[0].message.content
    print(f"📥 Response: {result_text}")
    print("✅ Connection successful!")


if __name__ == "__main__":
    asyncio.run(main())
