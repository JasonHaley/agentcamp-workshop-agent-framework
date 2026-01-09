"""
Phase 5: Agent with Tool Calling
Run with: chainlit run app.py -w

This phase adds tools to the agent, allowing it to fetch
real-time data from external APIs.

Key Concepts:
- Adding tools to ChatAgent
- Tool calling flow (think → act → observe)
- Displaying tool steps in Chainlit UI
- Combining LLM knowledge with external data

Prerequisites:
- Phase 4 completed
- WEATHER_API_KEY in .env
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agent_framework import ChatAgent, FunctionCallContent, FunctionResultContent
from agent_framework.openai import OpenAIChatClient

from tools import TOOLS

load_dotenv()

SYSTEM_PROMPT = f"""You are a helpful AI assistant named Aria.
You have access to tools that let you fetch real-time information.

Available tools:
- get_weather: Get current weather for any city

When users ask about weather, USE the get_weather tool. Don't make up weather data.
For other questions, answer from your knowledge.

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


def create_agent():
    """Create a ChatAgent with tools."""
    chat_client = get_chat_client()

    agent = ChatAgent(
        chat_client=chat_client,
        name="Aria",
        description="A helpful AI assistant with weather capabilities",
        instructions=SYSTEM_PROMPT,
        tools=TOOLS,
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
        content="👋 Hi! I'm Aria. I can check the weather for you! Try: 'What's the weather in Paris?'"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with tool support."""
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
