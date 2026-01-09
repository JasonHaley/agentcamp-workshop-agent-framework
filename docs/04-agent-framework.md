# Phase 4: Understanding Microsoft Agent Framework

> ⏱️ **Time to complete**: 15 minutes

In this phase, we'll deepen our understanding of the Microsoft Agent Framework and prepare for adding tools.

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Understand the ChatAgent architecture
- Learn about threads and message management
- Configure agent parameters
- Prepare for tool integration

---

## 🤖 What is Microsoft Agent Framework?

The **Microsoft Agent Framework** is an open-source framework for building AI agents that can:

1. **Think** about what to do
2. **Act** using tools (APIs, functions, etc.)
3. **Observe** the results
4. **Repeat** until task is complete

```
┌─────────────────────────────────────────┐
│            Agent Loop                    │
│                                          │
│   Think ──▶ Act ──▶ Observe             │
│     ▲                   │                │
│     └───────────────────┘                │
│       (repeat until done)                │
└─────────────────────────────────────────┘
```

**In this phase**, we refine our agent WITHOUT tools to understand the architecture. **In Phase 5**, we'll add tools.

---

## 📁 Step 1: Create Your Project Folder

```bash
mkdir -p phase-04
cd phase-04
touch app.py
```

---

## 📝 Step 2: Understanding ChatAgent

The `ChatAgent` class is the core of the framework. Here's its key parameters:

```python
ChatAgent(
    chat_client=...,      # Required: The LLM client
    instructions="...",   # System prompt
    name="...",           # Agent name
    description="...",    # What the agent does
    tools=[...],          # Functions the agent can call
    temperature=0.7,      # Response randomness (0.0-2.0)
    max_tokens=...,       # Maximum response length
)
```

---

## 🔧 Step 3: Create a Refined Agent

Create `app.py` with a more structured agent:

```python
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
    """Create a ChatAgent with configuration."""
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
    thread = agent.get_new_thread()

    cl.user_session.set("agent", agent)
    cl.user_session.set("thread", thread)

    await cl.Message(content="👋 Hi! I'm Aria. How can I help?").send()


@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")
    thread = cl.user_session.get("thread")

    msg = cl.Message(content="")

    async for update in agent.run_stream(message.content, thread=thread):
        if update.text:
            await msg.stream_token(update.text)

    await msg.send()
```

---

## 🧵 Step 4: Understanding Threads

The `AgentThread` manages conversation history:

```python
# Create a new thread
thread = agent.get_new_thread()

# Use it to maintain context across messages
result1 = await agent.run("My name is Alex", thread=thread)
result2 = await agent.run("What's my name?", thread=thread)  # Returns "Alex"
```

**Key points:**
- Each user session should have its own thread
- The thread automatically stores all messages
- Passing the same thread maintains conversation context

---

## ▶️ Step 5: Run and Test

```bash
chainlit run app.py -w
```

### Test Scenarios

| Test | Expected |
|------|----------|
| "Hello!" | Friendly greeting |
| "What's your name?" | "Aria" |
| "What's today's date?" | Correct date |
| Follow-up questions | Context remembered |

---

## 💡 What Did We Gain?

Right now, the agent behaves similarly to Phase 3. **So why bother?**

The agent architecture gives us:
1. **Easy tool integration** - Just add tools to the list (Phase 5!)
2. **Built-in reasoning** - Agent can decide what to do
3. **Cleaner code** - Agent handles message flow
4. **Thread management** - Automatic conversation history

---

## 📋 Your Complete Code

```python
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
    """Create a ChatAgent with configuration."""
    chat_client = get_chat_client()

    agent = ChatAgent(
        chat_client=chat_client,
        name="Aria",
        description="A helpful AI assistant",
        instructions=SYSTEM_PROMPT,
        tools=[],
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

    await cl.Message(content="👋 Hi! I'm Aria. How can I help?").send()


@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")
    thread = cl.user_session.get("thread")

    msg = cl.Message(content="")

    async for update in agent.run_stream(message.content, thread=thread):
        if update.text:
            await msg.stream_token(update.text)

    await msg.send()
```

---

## 🗂️ Project Structure

```
phase-04/
└── app.py          # Agent-based chat
```

---

## ✅ Checkpoint

| Check | Status |
|-------|--------|
| Using `ChatAgent` class | ☐ |
| `tools=[]` (empty) | ☐ |
| Streaming works | ☐ |
| Memory works via thread | ☐ |
| Date is correct | ☐ |

### 🎉 Agent Working?

You now have a Microsoft Agent Framework agent ready for tools!

👉 **Next: [Phase 5: Adding Tools](05-tool-calling.md)**

---

## ❓ Common Issues

### "Module not found"
```bash
pip install agent-framework --pre
```

### Streaming not working
Make sure you're using `run_stream()` and iterating with `async for`.

### Thread not maintaining context
Ensure you're storing and retrieving the thread from `cl.user_session`.
