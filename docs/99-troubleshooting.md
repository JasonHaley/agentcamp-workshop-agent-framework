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

Make sure you're using Python 3.10–3.13. (As of June 2026, Chainlit does **not** yet support 3.14.) If you need a different version, [download it here](https://www.python.org/downloads/).

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

**Problem:** The app can't find your Foundry configuration

**Solution:**
1. Create `.env` file in your project root:
```bash
touch .env
```

2. Add required variables (provided during the workshop):
```env
FOUNDRY_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/...
FOUNDRY_MODEL=gpt-4o-mini
WEATHER_API_KEY=your_api_key_here
```

3. Never commit `.env` to Git - add to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

---

## 📋 Phase-Specific Issues

### Phase 2: Foundry Models Connection

#### "ModuleNotFoundError: No module named 'azure'"

The Foundry client authenticates with `DefaultAzureCredential` from `azure-identity`.

**Solution:**
```bash
pip install azure-identity
# or reinstall everything
pip install -r requirements.txt
```

#### Authentication / credential errors

**Problem:** `DefaultAzureCredential failed to retrieve a token` or a `CredentialUnavailableError`

**Causes:**
- You aren't signed in to Azure on this machine
- The signed-in identity doesn't have access to the Foundry project

**Solutions:**
1. Sign in with the Azure CLI:
```bash
az login
```
2. Confirm you can reach the project and that your identity has permission to the deployed model.
3. Double-check `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL` in `.env` (no extra spaces or quotes).

**Debug:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
print("Endpoint:", os.getenv("FOUNDRY_PROJECT_ENDPOINT"))
print("Model:", os.getenv("FOUNDRY_MODEL"))
```

#### Model / deployment not found

**Causes:**
- `FOUNDRY_MODEL` is not the **deployment name** in your Foundry project
- The deployment is in a different project than the endpoint points to

**Solution:** Verify the deployment name in the Foundry portal and copy it exactly into `FOUNDRY_MODEL`.

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

**Cause:** Not passing `stream=True`, or not reading `update.text`

**Solution:**
```python
async for update in agent.run(message, session=session, stream=True):
    if update.text:
        await answer.stream_token(update.text)

await answer.send()
```

#### Memory Not Working

**Problem:** Bot doesn't remember previous messages

**Cause:** A fresh session is created on every message, or the session isn't reused

**Solution:** Create the session once in `@cl.on_chat_start` and reuse it on every message:
```python
# 1. Create once when the chat starts
@cl.on_chat_start
async def start():
    agent = create_agent()
    session = agent.create_session()      # ← create once
    cl.user_session.set("agent", agent)
    cl.user_session.set("session", session)

# 2. Retrieve and pass it on every message
@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")
    session = cl.user_session.get("session")   # ← reuse same session
    async for update in agent.run(message.content, session=session, stream=True):
        ...
```

---

### Phase 4: Tool Calling

#### "ModuleNotFoundError: No module named 'agent_framework'"

**Solution:**
```bash
pip install -r requirements.txt
# or directly
pip install agent-framework==1.8.1
```

#### WEATHER_API_KEY Not Set

**Problem:** `Error: WEATHER_API_KEY not set in .env`

**Solution:**
1. Get a free API key from [weatherapi.com](https://www.weatherapi.com/)
2. Add to `.env`:
```env
WEATHER_API_KEY=your_key_here
```
3. Restart Chainlit (the `-w` flag should reload).

#### Tool Never Gets Called

**Problem:** User asks a weather question but the tool doesn't execute

**Causes:**
- `tools=[]` instead of `tools=TOOLS`
- System prompt doesn't mention the tool

**Solutions:**
1. Check tools are added:
```python
agent = Agent(
    client=client,
    name="Aria",
    instructions=INSTRUCTIONS,
    tools=TOOLS,   # ← Must be TOOLS, not []
)
```
2. Mention the tool in the instructions:
```python
INSTRUCTIONS = f"""...
Available tools:
- get_weather: Get current weather for any city

When users ask about weather, USE the get_weather tool.
..."""
```
3. Try asking more directly: "Use the weather tool for London"

#### Tool Parameters Not Working

**Problem:** Tool gets called but with wrong parameters

**Cause:** Missing type annotations or unclear field descriptions

**Solution:**
```python
from typing import Annotated
from pydantic import Field

def get_weather(
    city: Annotated[str, Field(
        description="The name of the city (e.g., 'London', 'Tokyo')"
    )]
) -> str:
    """Get the current weather for a city."""
    ...
```

#### httpx.ConnectError for Weather API

**Problem:** Tool can't connect to weatherapi.com

**Solution:** Increase the timeout and check your network:
```python
response = httpx.get(
    "http://api.weatherapi.com/v1/current.json",
    params={"key": api_key, "q": city},
    timeout=15.0   # ← Increase from 10.0
)
```

---

### Phase 5: MCP Integration

#### MCP Tool Not Appearing

**Causes:**
- MCP server URL wrong
- Tool not imported
- Server not responding

**Solutions:**
1. Verify URL and import:
```python
from agent_framework import MCPStreamableHTTPTool

MCPStreamableHTTPTool(
    name="microsoft_learn",
    url="https://learn.microsoft.com/api/mcp"   # ← Exact URL
)
```
2. Confirm tools are combined onto the agent:
```python
all_tools = [*TOOLS, *mcp_tools]
```

#### MCP Server Connection Errors

**Problem:** `TimeoutError` / connection failure to the MCP server

**Solution:** The `get_mcp_tools()` helper wraps the connection in try/except so the agent still works with local tools if the server is unreachable:
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
        print(f"Warning: Could not connect to MCP: {e}")
    return mcp_tools
```

#### MCP Tool Never Gets Used

**Problem:** Even with MCP configured, the tool is never called

**Solution:** Guide the agent in the instructions and ask Azure/cloud questions:
```python
INSTRUCTIONS = f"""...
- For Azure, cloud, and Microsoft Learn documentation questions, use available MCP tools
- Example: "How do I create an Azure storage account?" → Use MCP tools
..."""
```

---

### Phase 6: Agent Skills

#### Skills Aren't Being Discovered

- Confirm the `skills/` folder is next to `app.py` and each skill has a `SKILL.md`.
- `SkillsProvider.from_paths` must point at the `skills/` directory — check the path in `get_skills_provider()`.
- Each `SKILL.md` needs valid YAML frontmatter with `name` and `description`.

#### The Agent Answers Without Using the Skill

- Strengthen the `description` with concrete trigger phrases — that's what the model matches on.
- Make sure skills are registered via `context_providers=[skills_provider]` (skills are **context**, not `tools`).
- Make sure the "check your skills first" instruction is in `INSTRUCTIONS`.
- Ask more directly ("look up the negotiated rate for…") to confirm the skill *can* fire.

#### Script Errors / No Output

- Run the script by hand first: `python skills/<skill>/scripts/<script>.py --help`.
- The runner forwards arguments as **positional CLI args** and expects scripts to **print to stdout**.
- For data-backed skills, check relative paths (`rate_lookup.py` reads `../data/rate_card.csv`).

#### `[SKILLS]` Experimental Warning

The Skills APIs are experimental and emit a `FutureWarning`. The sample runner suppresses it with a `warnings.filterwarnings(...)` filter.

---

## 🐛 Common Code Issues

### Async/Await Mistakes

**Problem:** `RuntimeError: no running event loop`

**Solution:**
```python
# ✅ Correct - use async/await
@cl.on_message
async def main(message: cl.Message):
    async for update in agent.run(message.content, session=session, stream=True):
        ...

# ❌ Wrong - forgetting async/await on the agent call
```

### Import Order Issues

**Problem:** `ImportError` for local modules (`tools`, `subprocess_script_runner`)

**Solution:** Make sure the files are in the same directory as `app.py`:
```
phase-04/
├── app.py
└── tools.py   # ← Same level

# Import correctly
from tools import TOOLS
```

### String Formatting Issues

**Problem:** f-string fails with special characters

**Solution:**
```python
# Escape braces in f-strings
f"""Some text with {{braces}}"""
```

---

## 📊 Performance Issues

### Slow Responses

**Causes:** Model processing time, network latency, large conversation history

**Solutions:**
1. Use a faster model deployment (set `FOUNDRY_MODEL` to a smaller/faster deployment such as `gpt-4o-mini`).
2. Keep instructions concise.

---

## 🔐 Security Issues

### Secrets in Git

**Problem:** Accidentally committed `.env`

**Solution:**
```bash
git rm --cached .env
echo ".env" >> .gitignore
git commit -m "Remove .env from git"
# Rotate any exposed keys (WeatherAPI key, etc.)
```

### Script Runner is a Security Boundary (Phase 6)

The skill script runner **executes code**. The sample runs scripts as local subprocesses with a 30-second timeout — fine for a workshop on your own machine. In production, sandbox it (a container, restricted permissions, an allow-list) before running skills you didn't author.

---

## 📞 Getting Help

### Check Chainlit Logs

```bash
# Chainlit prints detailed logs to the terminal. Watch them while running:
chainlit run app.py -w
```

### Test the Connection in Isolation

Re-run the Phase 2 connection test to confirm Foundry is reachable before debugging the UI:
```bash
python solutions/phase-02/test_foundry_models.py
```

### Resources

- [Chainlit Documentation](https://docs.chainlit.io)
- [Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [Microsoft Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)

---

## ✅ Quick Checklist

Before asking for help, verify:

- [ ] Python 3.10–3.13 installed (`python --version`)
- [ ] Virtual environment activated (see `(.venv)` in prompt)
- [ ] `.env` file exists with `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL`
- [ ] Signed in to Azure (`az login`) with access to the Foundry project
- [ ] Required packages installed (`pip list`)
- [ ] Correct phase folder (`cd phase-XX`)
- [ ] Code matches the solution file
- [ ] No typos in imports or function names
- [ ] Port 8000 available (or use `--port XXXX`)
- [ ] Internet connection working
