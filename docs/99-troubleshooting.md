# Troubleshooting Guide

> 🆘 **Having issues?** This guide covers common problems and solutions across all phases.

---

## 🔧 General Setup Issues

### Python Version Issues

**Problem:** `Python 3.10 or higher required`

**Solution:**
```bash
# Check your Python version
python --version

# If you have multiple Python versions, use python3
python3 --version
```

Make sure you're using Python 3.10+. If not, [download a newer version](https://www.python.org/downloads/).

### Virtual Environment Not Activated

**Problem:** Packages not found even after `pip install`

**Solution:**
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# You should see (.venv) in your terminal prompt
```

### Missing .env File

**Problem:** `FileNotFoundError: .env file not found`

**Solution:**
1. Create `.env` file in your project root:
```bash
touch .env
```

2. Add required variables:
```env
GITHUB_TOKEN=ghp_your_token_here
WEATHER_API_KEY=your_api_key_here
```

3. Never commit `.env` to Git - add to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

---

## 📋 Phase-Specific Issues

### Phase 2: GitHub Models Connection

#### "401 Unauthorized"

**Causes:**
- Invalid GITHUB_TOKEN
- Token has expired
- Token doesn't have proper permissions

**Solutions:**
1. Check `.env` file has correct token with no extra spaces
2. Generate a new token at [GitHub Settings → Tokens](https://github.com/settings/tokens)
3. Make sure token is fresh (regenerate if older than 30 days)

**Debug:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
print(f"Token length: {len(token)}")  # Should be ~50+ characters
print(f"Token starts with: {token[:10]}...")
print(f"Has spaces: {' ' in token}")
```

#### "Cannot connect to models.github.ai"

**Causes:**
- Network issues
- Firewall blocking GitHub Models endpoint
- URL is incorrect

**Solutions:**
1. Check your internet connection
2. Test the endpoint manually:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://models.github.ai/inference/models
```
3. Verify URL is exactly: `https://models.github.ai/inference`

#### "Module not found: openai"

**Solution:**
```bash
pip install openai python-dotenv
```

---

### Phase 3: Chainlit Chat Interface

#### Port 8000 Already in Use

**Problem:** `Address already in use`

**Solutions:**
```bash
# Run on different port
chainlit run app.py -w --port 8001

# Or kill process using port 8000
# On macOS/Linux:
lsof -i :8000  # Find process
kill -9 PID    # Kill it

# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### Streaming Not Working

**Problem:** Responses appear all at once, not word-by-word

**Causes:**
- Not using `stream=True` in API call
- Using old OpenAI library version

**Solutions:**
```python
# Make sure you have:
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    stream=True,  # ← Must have this
)

# Iterate correctly:
async for chunk in stream:
    if chunk.choices and len(chunk.choices) > 0:
        delta = chunk.choices[0].delta.content
        if delta:
            await msg.stream_token(delta)
```

Upgrade OpenAI:
```bash
pip install --upgrade openai
```

#### "IndexError: list index out of range" on stream

**Problem:** Error on `chunk.choices[0].delta.content`

**Cause:** Some chunks don't have choices array

**Solution:** Always check before accessing:
```python
async for chunk in stream:
    # Safety check FIRST
    if chunk.choices and len(chunk.choices) > 0:
        delta = chunk.choices[0].delta.content
        if delta:
            # Now safe to use
            await msg.stream_token(delta)
```

#### Message History Not Working

**Problem:** Bot doesn't remember previous messages

**Causes:**
- Not storing messages in session
- Not retrieving messages correctly
- Starting fresh session each time

**Solutions:**
```python
# Make sure you have all three:

# 1. Initialize in @cl.on_chat_start
messages = [{"role": "system", "content": SYSTEM_PROMPT}]
cl.user_session.set("messages", messages)

# 2. Retrieve in @cl.on_message
messages = cl.user_session.get("messages")

# 3. Append and save after each response
messages.append({"role": "user", "content": message.content})
messages.append({"role": "assistant", "content": response_text})
cl.user_session.set("messages", messages)
```

---

### Phase 4: Agent Framework

#### "ModuleNotFoundError: No module named 'agent_framework'"

**Solution:**
```bash
# Install pre-release version
pip install agent-framework --pre
```

#### Agent Not Responding

**Problem:** Agent seems stuck or no response

**Causes:**
- Agent Framework not initialized correctly
- Chat client not configured properly
- Model not available

**Solutions:**
1. Test connection first with Phase 2 script
2. Check chat client is created:
```python
def get_chat_client():
    openai_client = AsyncOpenAI(
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.github.ai/inference",
    )
    return OpenAIChatClient(
        async_client=openai_client,
        model_id="gpt-4o-mini",
    )
```

3. Verify agent is created with tools list:
```python
agent = ChatAgent(
    chat_client=chat_client,
    name="Aria",
    instructions=SYSTEM_PROMPT,
    tools=[],  # Even if empty, must be present
    temperature=0.7,
)
```

#### Memory Not Working with Agent

**Problem:** Agent doesn't remember context between messages

**Solution:**
```python
# Threads manage memory, use them!
@cl.on_chat_start
async def start():
    agent = create_agent()
    thread = agent.get_new_thread()  # ← Must create thread
    cl.user_session.set("thread", thread)

@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")
    thread = cl.user_session.get("thread")  # ← Must retrieve

    # Must pass thread to maintain context
    async for update in agent.run_stream(message.content, thread=thread):
        ...
```

---

### Phase 5: Tool Calling

#### WEATHER_API_KEY Not Set

**Problem:** `Error: WEATHER_API_KEY not set in .env`

**Solution:**
1. Get free API key from [weatherapi.com](https://www.weatherapi.com/)
2. Add to `.env`:
```env
WEATHER_API_KEY=your_key_here
```
3. Restart Chainlit (the `-w` flag should reload)

#### Tool Never Gets Called

**Problem:** User asks weather question but tool doesn't execute

**Causes:**
- `tools=[]` instead of `tools=TOOLS`
- System prompt doesn't mention the tool
- Tool not in correct format

**Solutions:**
1. Check tools are added:
```python
agent = ChatAgent(
    ...
    tools=TOOLS,  # ← Must be TOOLS, not []
    ...
)
```

2. Mention tool in system prompt:
```python
SYSTEM_PROMPT = f"""...
Available tools:
- get_weather: Get current weather for any city

When users ask about weather, USE the get_weather tool.
..."""
```

3. Try asking more directly: "Use the weather tool for London"

#### Tool Visualization Not Showing

**Problem:** Tool calls don't appear as steps in UI

**Causes:**
- Using old `hasattr()` pattern
- Not checking for `FunctionCallContent` type
- Missing imports

**Solution:**
```python
from agent_framework import ChatAgent, FunctionCallContent, FunctionResultContent

# Correct way to detect tool calls:
if isinstance(content, FunctionCallContent):
    if content.name and content.call_id not in tool_steps:
        step = cl.Step(name=f"🔧 {content.name}", type="tool")
        await step.send()
        tool_steps[content.call_id] = step
```

#### httpx.ConnectError for Weather API

**Problem:** Tool can't connect to weatherapi.com

**Causes:**
- Network issues
- API service down
- Timeout too short

**Solution:**
```python
import httpx

# Increase timeout
response = httpx.get(
    "http://api.weatherapi.com/v1/current.json",
    params={"key": api_key, "q": city},
    timeout=15.0  # ← Increase from 10.0
)
```

#### Tool Parameters Not Working

**Problem:** Tool gets called but with wrong parameters

**Causes:**
- Parameter type annotations missing
- Field descriptions unclear

**Solution:**
```python
from typing import Annotated
from pydantic import Field

def get_weather(
    # Correct format with type and description
    city: Annotated[str, Field(
        description="The name of the city (e.g., 'London', 'Tokyo')"
    )]
) -> str:
    """Get the current weather for a city."""
    ...
```

---

### Phase 6: MCP Integration

#### MCP Tool Not Appearing

**Problem:** MCP tools not available in agent

**Causes:**
- MCP server URL wrong
- Tool not imported correctly
- Server not responding

**Solutions:**
1. Verify URL is correct:
```python
MCPStreamableHTTPTool(
    name="microsoft_learn",
    url="https://learn.microsoft.com/api/mcp"  # ← Exact URL
)
```

2. Check import:
```python
from agent_framework import MCPStreamableHTTPTool  # Must import
```

3. Test server manually:
```bash
curl https://learn.microsoft.com/api/mcp
```

#### MCP Server Connection Timeout

**Problem:** `TimeoutError` connecting to MCP server

**Causes:**
- Server is down
- Network issues
- URL incorrect

**Solution:**
```python
def get_mcp_tools():
    mcp_tools = []

    try:
        mcp_tools.append(
            MCPStreamableHTTPTool(
                name="microsoft_learn",
                url="https://learn.microsoft.com/api/mcp"
            )
        )
    except Exception as e:
        # If MCP fails, agent still works with local tools
        print(f"Warning: Could not connect to MCP: {e}")

    return mcp_tools
```

#### MCP Tool Never Gets Used

**Problem:** Even with MCP configured, tool never called

**Causes:**
- System prompt doesn't guide agent to use it
- Question doesn't match tool's purpose

**Solution:**
```python
SYSTEM_PROMPT = f"""...
- MCP tools: Microsoft Learn documentation for technical questions

Guidelines:
- For Azure, cloud, and technical documentation questions, use MCP tools
- Example: "How do I create an Azure storage account?" → Use MCP
..."""
```

#### Local Tools Work, MCP Tools Don't

**Problem:** get_weather works but MCP tools don't

**Causes:**
- MCP server not accessible
- Different authentication needed
- MCP server has issues

**Solution:**
- MCP is optional - agent will still work with local tools
- Check MCP server status
- Try different MCP server if available
- Proceed with local tools only if needed

---

## 🐛 Common Code Issues

### Async/Await Mistakes

**Problem:** `RuntimeError: no running event loop`

**Causes:**
- Missing `async` keyword
- Not awaiting async functions
- Wrong context

**Solution:**
```python
# ✅ Correct - use async/await
@cl.on_message
async def main(message: cl.Message):
    stream = await client.chat.completions.create(...)
    async for chunk in stream:
        ...

# ❌ Wrong - missing await
stream = client.chat.completions.create(...)
```

### Import Order Issues

**Problem:** `ImportError` for local modules

**Causes:**
- Wrong import path
- Circular imports
- File not in right location

**Solution:**
```python
# Make sure files are in same directory
phase-05/
├── app.py
└── tools.py  # ← Same level

# Import correctly
from tools import TOOLS  # ← Relative import works in same dir
```

### String Formatting Issues

**Problem:** f-string fails with special characters

**Solution:**
```python
# Escape braces in f-strings
f"""Some text with {{braces}}"""

# Or use concatenation
"Some text with " + "{braces}"
```

---

## 📊 Performance Issues

### Slow Responses

**Causes:**
- Model processing time (expected)
- Network latency
- Large conversation history

**Solutions:**
1. Use faster model:
```python
model_id="gpt-4o-mini",  # Fast but less capable
# vs
model_id="gpt-4o",       # Smarter but slower
```

2. Trim conversation history:
```python
# Keep only last 10 exchanges
messages = messages[-20:]  # Last 20 messages (10 exchanges)
```

### High Token Usage

**Problem:** Using too many tokens = higher cost/slowness

**Solutions:**
```python
# Limit conversation history
MAX_MESSAGES = 20
if len(messages) > MAX_MESSAGES:
    messages = messages[:1] + messages[-MAX_MESSAGES+1:]  # Keep system + recent

# Shorter system prompts
SYSTEM_PROMPT = "You are helpful. Answer concisely."  # Instead of very long prompt
```

---

## 🔐 Security Issues

### Token in Git

**Problem:** Accidentally committed `.env` with secret tokens

**Solution:**
```bash
# Remove from git history
git rm --cached .env
echo ".env" >> .gitignore
git commit -m "Remove .env from git"

# REGENERATE ALL TOKENS IMMEDIATELY
# - Create new GitHub token
# - Update API key (if exposed)
```

### Token Leaked in Error Messages

**Problem:** Error message shows your API key

**Solution:**
```python
except Exception as e:
    # ❌ Wrong - reveals token
    print(f"Error: {e}")

    # ✅ Correct - hides sensitive info
    print(f"Error connecting to API: {e}")
    # Log error details securely elsewhere
```

---

## 📞 Getting Help

### Enable Debug Mode

Add logging to see what's happening:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@cl.on_message
async def main(message: cl.Message):
    logger.debug(f"Received: {message.content}")
    # ... rest of code
```

### Check Chainlit Logs

```bash
# Chainlit prints detailed logs to terminal
# Watch for error messages while running:
chainlit run app.py -w
```

### Test Individual Components

```python
# Test 1: GitHub Models connection
from openai import AsyncOpenAI
import asyncio

async def test_connection():
    client = AsyncOpenAI(
        api_key="your_token",
        base_url="https://models.github.ai/inference",
    )
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}],
    )
    print(response.choices[0].message.content)

asyncio.run(test_connection())
```

### Resources

- [Chainlit Documentation](https://docs.chainlit.io)
- [Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [GitHub Models Docs](https://github.com/marketplace/models)

---

## ✅ Quick Checklist

Before asking for help, verify:

- [ ] Python 3.10+ installed (`python --version`)
- [ ] Virtual environment activated (see `(.venv)` in prompt)
- [ ] `.env` file exists with GITHUB_TOKEN
- [ ] Required packages installed (`pip list`)
- [ ] Correct phase folder (`cd phase-XX`)
- [ ] Code matches solution file exactly
- [ ] No typos in imports or function names
- [ ] Port 8000 available (or use `--port XXXX`)
- [ ] Internet connection working
- [ ] GitHub token not expired

---

**Still stuck?** Open an issue on the [repository](https://github.com/your-repo) with:
- Error message (full traceback)
- Which phase you're on
- What you were doing when it happened
- Your Python version (`python --version`)
