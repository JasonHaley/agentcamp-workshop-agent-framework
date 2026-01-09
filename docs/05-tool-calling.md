# Phase 5: Adding Tools to Your Agent

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
mkdir -p phase-05
cd phase-05
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
```

**Key changes:**
- `FunctionCallContent` and `FunctionResultContent` - Proper imports for tool handling
- `isinstance(content, FunctionCallContent)` - Check for tool calls
- `isinstance(content, FunctionResultContent)` - Check for tool results
- `content.call_id` - Unique identifier for tracking tool steps
- `tool_steps` dict pattern - Store step references by call_id

---

## ▶️ Step 5: Run and Test

```bash
chainlit run app.py -w
```

### Test Scenarios

**Test 1: Weather (uses tool)**
```
You: What's the weather in London?
[Tool step appears]
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
[Two tool calls]
Aria: Tokyo is 8°C while Sydney is 22°C...
```

---

## 📋 Your Complete Files

### tools.py

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


TOOLS = [get_weather]
```

### app.py

```python
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
