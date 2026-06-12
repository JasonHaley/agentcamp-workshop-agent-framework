"""
Phase 4: Agent with Tool Calling
Run with: chainlit run app.py -w

This phase adds tools to the agent, allowing it to fetch
real-time data from external APIs.

Key Concepts:
- Adding tools to ChatAgent
- Tool calling flow (think → act → observe)
- Displaying tool steps in Chainlit UI
- Combining LLM knowledge with external data

Prerequisites:
- Phase 3 completed
- WEATHER_API_KEY in .env
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

from tools import TOOLS

load_dotenv()

INSTRUCTIONS = f"""You are a helpful AI assistant named Aria.
You have access to tools that let you fetch real-time information.

Available tools:
- get_weather: Get current weather for any city

When users ask about weather, USE the get_weather tool. Don't make up weather data.
For other questions, answer from your knowledge.

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
    """Create a ChatAgent with tools."""
    client = get_chat_client()

    agent = Agent(
        client=client,
        name="Aria",
        description="A helpful AI assistant",
        instructions=INSTRUCTIONS,
        tools=TOOLS,
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