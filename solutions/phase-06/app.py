"""
Phase 6: Agent with MCP Integration
Run with: chainlit run app.py -w

This phase combines local tools with MCP (Model Context Protocol)
tools from external servers.

Key Concepts:
- HostedMCPTool for external tool servers
- Combining local and MCP tools
- Extensible architecture for tool integration

Prerequisites:
- Phase 5 completed
- Understanding of MCP protocol
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agent_framework import ChatAgent, FunctionCallContent, FunctionResultContent, MCPStreamableHTTPTool
from agent_framework.openai import OpenAIChatClient

from tools import TOOLS

load_dotenv()

SYSTEM_PROMPT = f"""You are a helpful AI assistant named Aria.

You have access to multiple tools:
- Local tools: get_weather for weather queries
- MCP tools: Microsoft Learn documentation for technical questions

Guidelines:
- For weather, use get_weather
- For Azure, cloud, and Microsoft Learn documentation questions, use available MCP tools
- Be helpful and explain what you're doing
- Example: User asks "How do I create an Azure storage account using az cli?" → Use MCP tools to search Microsoft Learn documentation

Current date: {date.today().strftime("%B %d, %Y")}
"""


def get_chat_client():
    """Create an Agent Framework chat client using GitHub Models."""
    openai_client = AsyncOpenAI(
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.github.ai/inference",
    )
    return OpenAIChatClient(
        async_client=openai_client,
        model_id="gpt-4o-mini",
    )


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


def create_agent():
    """Create a ChatAgent with local and MCP tools."""
    chat_client = get_chat_client()
    mcp_tools = get_mcp_tools()

    # Combine local tools with MCP tools
    all_tools = [*TOOLS, *mcp_tools]

    agent = ChatAgent(
        chat_client=chat_client,
        name="Aria",
        description="A helpful AI assistant with local and MCP tools",
        instructions=SYSTEM_PROMPT,
        tools=all_tools,
        temperature=0.7,
    )

    return agent


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    agent = create_agent()
    thread = agent.get_new_thread()

    cl.user_session.set("agent", agent)
    cl.user_session.set("thread", thread)

    await cl.Message(
        content="👋 Hi! I'm Aria. I can check weather and access various tools!"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with local and MCP tool support."""
    agent = cl.user_session.get("agent")
    thread = cl.user_session.get("thread")

    msg = cl.Message(content="")
    tool_steps = {}

    async for update in agent.run_stream(message.content, thread=thread):
        # Handle tool invocation and results
        if update.contents:
            for content in update.contents:
                # Detect function call - only show step when we have the name (first chunk)
                if isinstance(content, FunctionCallContent):
                    # Only create step on the first chunk that has a name
                    if content.name and content.call_id not in tool_steps:
                        step = cl.Step(
                            name=f"🔧 {content.name}",
                            type="tool"
                        )
                        await step.send()
                        tool_steps[content.call_id] = step

                # Detect function result
                elif isinstance(content, FunctionResultContent):
                    step = tool_steps.get(content.call_id)
                    if step:
                        step.output = content.result
                        await step.update()

        # Stream text response
        if update.text:
            await msg.stream_token(update.text)

    await msg.send()
