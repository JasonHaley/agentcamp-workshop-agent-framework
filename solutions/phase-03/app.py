"""
Phase 3: Basic Chainlit Chat with Streaming
Run with: chainlit run app.py -w

This phase builds a web-based chat interface using Chainlit
with streaming responses from Foundry.

Key Concepts:
- Chainlit decorators (@cl.on_chat_start, @cl.on_message)
- Session management (cl.user_session)
- Streaming responses with FoundryChatClient
- Message history management

Prerequisites:
- Phase 2 completed (Foundry connection verified)
- chainlit package installed
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

load_dotenv()

INSTRUCTIONS = f"""You are a helpful AI assistant named Aria.

Your capabilities:
- Answer questions on any topic
- Help with coding and technical problems
- Provide explanations and analysis
- Be friendly and conversational

Guidelines:
- Be concise but thorough
- Admit when you don't know something
- Ask clarifying questions when needed

Current date: {date.today().strftime("%B %d, %Y")}
"""

def get_chat_client():
    """Create an Agent Framework chat client using Foundry."""
    client = FoundryChatClient(
        project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        model=os.getenv("FOUNDRY_MODEL"),
        credential=DefaultAzureCredential()
    )
    return client

def create_agent():
    """Create a ChatAgent with configuration."""
    client = get_chat_client()

    agent = Agent(
        client=client,
        name="Aria",
        description="A helpful AI assistant",
        instructions=INSTRUCTIONS,
    )

    return agent


@cl.on_chat_start
async def start():
    """Initialize the chat session."""

    agent = create_agent()

    # Store message history in session
    session = agent.create_session()
    
    cl.user_session.set("agent", agent)
    cl.user_session.set("session", session)

    await cl.Message(content="👋 Hi! I'm Aria. How can I help?").send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with streaming."""
    agent = cl.user_session.get("agent")
    session = cl.user_session.get("session")
    
    await stream_agent_response(
        agent=agent,
        session=session,
        answer=cl.Message(content=""),
        message=message.content,
    )

async def stream_agent_response(agent: Agent, session, answer: cl.Message, message: str):
    """Stream the agent's response."""

    async for update in agent.run(message, session=session, stream=True):
        if update.text:
            await answer.stream_token(update.text)

    await answer.send()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)