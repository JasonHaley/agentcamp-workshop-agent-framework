# Phase 4: Adding Tools to Your Agent

> ⏱️ **Time to complete**: 20 minutes

In this phase, we'll give our agent the ability to use **tools**! We'll create a weather tool that fetches real-time data.

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Create a tool using function definitions
- Add tools to your agent
- Handle tool calls in the UI
- See real-time weather data in your chat

---

## 🔧 What is Tool Calling?

Tool calling lets the LLM:
1. **Recognize** when it needs external data
2. **Request** a function call with arguments
3. **Use** the result to formulate a response

```
User: "What's the weather in Tokyo?"
         │
         ▼
   Agent THINKS: "I need to call get_weather"
         │
         ▼
   Agent ACTS: get_weather("Tokyo")
         │
         ▼
   Tool returns: "Tokyo: 8°C, Cloudy"
         │
         ▼
   Agent responds: "It's 8°C and cloudy in Tokyo!"
```

---

## 📁 Step 1: Create Your Project Folder

```bash
mkdir -p phase-04
cd phase-04
touch app.py tools.py
```

---

## 🔑 Step 2: Get a Weather API Key

Add your WeatherAPI key to `.env`:

```bash
# Edit your .env file - add this line:
WEATHER_API_KEY=your_key_here
```

> 💡 Get a free key at [weatherapi.com](https://www.weatherapi.com/) - takes 2 minutes!

---

## 🛠️ Step 3: Create the Tool File

Create `tools.py` with our weather tool:

```python
import os
from typing import Annotated
import httpx
from pydantic import Field


def get_weather(
    city: Annotated[str, Field(description="The name of the city (e.g., 'London', 'Tokyo')")]
) -> str:
    """
    Get the current weather for a city.

    Returns current weather conditions including temperature, condition, and humidity.
    """
    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        return "Error: WEATHER_API_KEY not set in .env"

    try:
        response = httpx.get(
            "http://api.weatherapi.com/v1/current.json",
            params={"key": api_key, "q": city},
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        location = data["location"]["name"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        humidity = data["current"]["humidity"]

        return f"""Weather for {location}, {country}:
🌡️ Temperature: {temp_c}°C
☁️ Condition: {condition}
💧 Humidity: {humidity}%"""

    except httpx.HTTPStatusError:
        return f"Could not find weather for '{city}'"
    except Exception as e:
        return f"Error: {e}"


# List of tools to give to the agent
TOOLS = [get_weather]
```

**Understanding the tool definition:**

| Part | Purpose |
|------|---------|
| `Annotated[str, Field(...)]` | Describes the parameter for the LLM |
| Docstring | LLM reads this to know when to use it |
| Return string | What the agent receives back |

---

## 📝 Step 4: Create the App with Tools

Create `app.py`:

```python
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
```

## ▶️ Step 5: Run and Test

```bash
chainlit run app.py -w
```

### Test Scenarios

**Test 1: Weather (uses tool)**
```
You: What's the weather in London?
Aria: The weather in London is 7°C with cloudy skies...
```

**Test 2: Non-weather (no tool)**
```
You: What is Python?
Aria: Python is a programming language...
(No tool called)
```

**Test 3: Multiple cities**
```
You: Compare weather in Tokyo and Sydney
Aria: Tokyo is 8°C while Sydney is 22°C...
```

---

## 📋 Your Complete Files

### tools.py

```python
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
```

---

## 🗂️ Project Structure

```
phase-05/
├── app.py          # Agent with tools
└── tools.py        # Tool definitions
```

---

## 💡 Key Takeaways

The agent now:
1. **Decides** when to use a tool
2. **Calls** the tool with the right arguments
3. **Uses** the result to respond naturally

You can add more tools by:
1. Define function with type annotations
2. Add it to the `TOOLS` list
3. Update the system prompt

---

## ✅ Checkpoint

| Check | Status |
|-------|--------|
| `tools.py` created | ☐ |
| `WEATHER_API_KEY` in .env | ☐ |
| Weather query shows tool step | ☐ |
| Returns real weather data | ☐ |
| Non-weather questions work | ☐ |

### 🎉 Tools Working?

Your agent can now interact with the real world!

👉 **Next: [Phase 6: MCP Integration](06-mcp-integration.md)**

---

## ❓ Common Issues

### "WEATHER_API_KEY not set"
Add it to your `.env` file and restart Chainlit.

### Tool never gets called
- Check `tools=TOOLS` in `create_agent()`
- Make sure system prompt mentions the tool
- Try asking more directly: "Use the weather tool for Paris"

### Tool step not showing in UI
The Agent Framework handles tool calls automatically. The step visualization depends on the update contents.
