"""
Phase 4: Introducing Microsoft Agent Framework
Run with: chainlit run app.py -w

This phase introduces the Agent Framework and its ChatAgent class.
The key difference from Phase 3: ChatAgent is a higher-level abstraction
built on LangGraph that can reason about tasks and use tools.

Key Concepts Introduced:
- ChatAgent: Agent abstraction with tool support
- AgentThread: Manages conversation history
- Agent reasoning: Can decide what to do next
- Prepared for tool integration (Phase 5)

Difference from Phase 3:
- Phase 3: Direct LLM calls with message history
- Phase 4: Agent loop (think → act → observe)

Prerequisites:
- Phase 3 completed
- agent-framework package installed
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

load_dotenv()

SYSTEM_PROMPT = f"""You are a helpful AI assistant named Aria.

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
    """Create a ChatAgent with configuration.

    This is the key new concept: ChatAgent replaces direct LLM calls.
    It provides agent reasoning and will support tools in Phase 5.
    """
    chat_client = get_chat_client()

    agent = ChatAgent(
        chat_client=chat_client,
        name="Aria",
        description="A helpful AI assistant",
        instructions=SYSTEM_PROMPT,
        tools=[],  # No tools yet - we'll add them in Phase 5!
        temperature=0.7,
    )

    return agent


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    agent = create_agent()
    # AgentThread maintains conversation history automatically
    thread = agent.get_new_thread()

    cl.user_session.set("agent", agent)
    cl.user_session.set("thread", thread)

    await cl.Message(content="👋 Hi! I'm Aria. How can I help?").send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages using the agent."""
    agent = cl.user_session.get("agent")
    thread = cl.user_session.get("thread")

    msg = cl.Message(content="")

    # Key change: agent.run_stream() with thread instead of llm.astream()
    async for update in agent.run_stream(message.content, thread=thread):
        if update.text:
            await msg.stream_token(update.text)

    await msg.send()
