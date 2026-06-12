"""
Phase 6: Agent with Skills (+ MCP + local tools)
Run with: chainlit run app.py -w

This phase adds file-based Skills on top of the Phase 5 MCP agent.
Skills bundle instructions (SKILL.md), deterministic scripts, and data,
and are loaded with progressive disclosure via a SkillsProvider.

Key Concepts:
- SkillsProvider.from_paths for file-based skill discovery
- A script_runner to execute bundled skill scripts
- context_providers (skills are context, not tools)

Prerequisites:
- Phase 5 completed
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from pathlib import Path
from agent_framework import Agent, MCPStreamableHTTPTool, SkillsProvider
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

from tools import TOOLS
from subprocess_script_runner import subprocess_script_runner

load_dotenv()

INSTRUCTIONS = f"""You are a helpful AI assistant named Aria.

You have access to multiple tools:
- Local tools: get_weather for weather queries
- MCP tools: Microsoft Learn documentation for technical questions

Before answering, check whether any of your available skills applies to the
request. For questions about internal data (rates, contracts, policies),
never answer from general knowledge — if a skill covers it, use it; if none
does, say so.

Guidelines:
- For weather, use get_weather
- For Azure, cloud, and Microsoft Learn documentation questions, use available MCP tools
- Be helpful and explain what you're doing
- Example: User asks "How do I create an Azure storage account using az cli?" → Use MCP tools to search Microsoft Learn documentation

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

def get_mcp_tools():
    """
    Get MCP tools from external servers.

    MCP (Model Context Protocol) allows connecting to external tool servers.
    This function configures available MCP servers that provide tools to the agent.
    """
    mcp_tools = []

    try:
        # Add Microsoft Learn MCP Server
        # This provides access to Microsoft Learn documentation search
        mcp_tools.append(
            MCPStreamableHTTPTool(
                name="microsoft_learn",
                url="https://learn.microsoft.com/api/mcp"
            )
        )
    except Exception as e:
        print(f"Warning: Could not connect to Microsoft Learn MCP server: {e}")
    return mcp_tools

def get_skills_provider():
    """Create a SkillsProvider for file-based skills.

    Discovers skills from the 'skills' directory and configures the
    subprocess_script_runner to run file-based scripts.
    """
    skills_dir = Path(__file__).parent / "skills"
    skills_provider = SkillsProvider.from_paths(
        skill_paths=str(skills_dir),
        script_runner=subprocess_script_runner,
    )
    return skills_provider

def create_agent():
    """Create a ChatAgent with local, MCP tools and skills."""
    client = get_chat_client()
    mcp_tools = get_mcp_tools()
    skills_provider = get_skills_provider()

    # Combine local tools with MCP tools
    all_tools = [*TOOLS, *mcp_tools]

    agent = Agent(
        client=client,
        name="Aria",
        description="A helpful AI assistant with local, MCP tools and skills",
        instructions=INSTRUCTIONS,
        tools=all_tools,
        context_providers=[skills_provider],
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
