# Phase 3: Building a Chat Interface with Chainlit

> ⏱️ **Time to complete**: 15 minutes

In this phase, we'll build a chat interface step by step. You'll start with a minimal app and progressively add features.

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Create a Chainlit chat app
- Connect it to GitHub Models using the OpenAI library
- Add streaming responses
- Implement conversation memory with message history

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
    """Handle incoming messages."""
    client = get_openai_client()
    messages = cl.user_session.get("messages")

    # Add user message to history
    messages.append({"role": "user", "content": message.content})

    # Call the API
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    result_text = response.choices[0].message.content
    await cl.Message(content=result_text).send()

    # Add assistant response to history
    messages.append({"role": "assistant", "content": result_text})
    cl.user_session.set("messages", messages)
```

**What we added:**
- `get_openai_client()` - Creates an OpenAI client for GitHub Models
- `@cl.on_chat_start` - Runs once when the chat starts, initializes message history
- `client.chat.completions.create()` - Calls the OpenAI API
- Message history stored as a list of dicts

**Test it:** Ask "What is Python?" - you get a real AI response!

**Test memory:** Say "My name is Alex", then ask "What's my name?" - it remembers!

---

## ⚡ Step 4: Add Streaming

Waiting for the full response is slow. Let's stream it word-by-word for a better user experience. **Replace** the `@cl.on_message` function:

```python
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
```

**What changed:**
- `stream=True` - Enables streaming in the API call
- `async for chunk in stream:` - Iterate over chunks as they arrive
- `chunk.choices[0].delta.content` - The text content of each chunk
- `msg.stream_token()` - Display each chunk immediately
- Safety check: `if chunk.choices and len(chunk.choices) > 0:` - Ensure chunk has content

**Test it:** Ask a longer question and watch the response appear word-by-word!

---

## 📋 Your Complete Code

Here's what your complete `app.py` should look like:

```python
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

👉 **Next: [Phase 4: Agent Framework Agents](04-agent-framework.md)**

---

## ❓ Common Issues

### Memory not working
- Make sure you're appending messages to the list with `messages.append()`
- Verify you're getting messages from session with `cl.user_session.get("messages")`
- Confirm you're saving back with `cl.user_session.set("messages", messages)`

### Streaming not working
- Use `stream=True` in the `client.chat.completions.create()` call
- Iterate with `async for chunk in stream:`
- Check for chunks with content: `if chunk.choices and len(chunk.choices) > 0:`
- Extract text with `chunk.choices[0].delta.content`

### "IndexError: list index out of range"
Some chunks don't have content. Always check: `if chunk.choices and len(chunk.choices) > 0:` before accessing `chunk.choices[0]`

### Port 8000 in use
```bash
chainlit run app.py -w --port 8001
```
