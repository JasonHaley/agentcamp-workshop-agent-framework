"""
Phase 3: Basic Chainlit Chat with Streaming
Run with: chainlit run app.py -w

This phase builds a web-based chat interface using Chainlit
with streaming responses from GitHub Models using the OpenAI library directly.

Key Concepts:
- Chainlit decorators (@cl.on_chat_start, @cl.on_message)
- Session management (cl.user_session)
- Streaming responses with OpenAI AsyncOpenAI
- Message history management

Prerequisites:
- Phase 2 completed (GitHub Models connection verified)
- chainlit package installed
"""

import os
import chainlit as cl
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

SYSTEM_PROMPT = """You are a helpful AI assistant named Aria.
Be friendly and concise."""


def get_openai_client():
    """Create AsyncOpenAI client pointing to GitHub Models."""
    return AsyncOpenAI(
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.github.ai/inference",
    )


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    # Store message history in session
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    cl.user_session.set("messages", messages)

    await cl.Message(content="👋 Hi! I'm Aria. How can I help?").send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with streaming."""
    client = get_openai_client()
    messages = cl.user_session.get("messages")

    # Add user message to history
    messages.append({"role": "user", "content": message.content})

    # Create empty message for streaming
    msg = cl.Message(content="")
    full_response = ""

    # Stream token by token using OpenAI SDK
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices and len(chunk.choices) > 0:
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                full_response += delta_content
                await msg.stream_token(delta_content)

    await msg.send()

    # Add assistant response to history
    messages.append({"role": "assistant", "content": full_response})
    cl.user_session.set("messages", messages)
