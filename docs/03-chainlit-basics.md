# Phase 3: Building a Chat Interface with Chainlit

> ⏱️ **Time to complete**: 15 minutes

In this phase, we'll build a chat interface step by step. You'll start with a minimal app and progressively add features.

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Create a Chainlit chat app
- Connect it to a model
- Add streaming responses
- Implement conversation memory with a session

---

## 📁 Step 1: Create Your Project Folder

```bash
mkdir -p phase-03
cd phase-03
touch app.py
```

---

## 🚀 Step 2: Start with a Minimal App

Create `app.py` with just the basics - an app that echoes back what you type:

```python
import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content=f"You said: {message.content}").send()
```

**Run it:**
```bash
chainlit run app.py -w
```

Open http://localhost:8000 and type something. You should see it echoed back!

> 💡 The `-w` flag enables auto-reload when you save changes.

---

## 🤖 Step 3: Connect to the LLM

Now let's make it use AI. **Replace** your `app.py` with:

```python
import os
import chainlit as cl
from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

load_dotenv()

INSTRUCTIONS = """You are a helpful AI assistant named Aria.
Be friendly and concise."""

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
    """Handle incoming messages."""
    
    agent = cl.user_session.get("agent")
    session = cl.user_session.get("session")

    # Call the Model
    result_text = await agent.run(message.content, session=session)
    
    await cl.Message(content=result_text).send()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)

```

**What we added:**
- `get_chat_client()` - Creates an client for calling the model in Foundry
- `@cl.on_chat_start` - Runs once when the chat starts, initializes message history
- `agent.run()` - Calls the model
- `session` - stored in user session to reuse on each call

**Test it:** Ask "What is Python?" - you get a real AI response!

**Test memory:** Say "My name is Alex", then ask "What's my name?" - it remembers!

---

## ⚡ Step 4: Add Streaming

Waiting for the full response is slow. Let's stream it word-by-word for a better user experience. **Replace** the `@cl.on_message` function:

```python
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
```

**What changed:**
- `stream=True` - Enables streaming in the call
- `async for update ...` - Iterate over chunks as they arrive
- `update.text` - The text content of each chunk
- `answer.stream_token()` - Display each chunk immediately

**Test it:** Ask a longer question and watch the response appear word-by-word!

```bash
chainlit run app.py -w --port 8001
```

---

## 📋 Your Complete Code

Here's what your complete `app.py` should look like:

```python
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
```

---

## 🗂️ Project Structure

```
phase-03/
└── app.py          # Chat application
```

---

## ✅ Checkpoint

| Test | Try | Expected |
|------|-----|----------|
| Basic chat | "Hello!" | Friendly greeting |
| Memory | "I'm Alex" → "What's my name?" | "Alex" |
| Streaming | Long question | Words appear progressively |
| Identity | "What's your name?" | "Aria" |

### 🎉 All Working?

You've built a chat interface with memory and streaming!

👉 **Next: [Phase 4: Tool Calling](04-tool-calling.md)**

---

## ❓ Common Issues

### Streaming not working
- Use `stream=True` in the `agent.run()` call
- Iterate with `async for update in agent.run(message, session=session, stream=True):`
- Extract text with `update.text`

### Port 8000 in use
```bash
chainlit run app.py -w --port 8001
```
