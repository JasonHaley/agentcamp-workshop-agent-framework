# Phase 5: MCP Integration

> ⏱️ **Time to complete**: 15 minutes

In this final phase, we'll add **MCP (Model Context Protocol)** tools to our agent. MCP lets you connect to external tool servers!

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Understand what MCP is
- Connect your agent to MCP servers
- Combine local tools with MCP tools
- Use the Agent Framework's MCP support

---

## 🔌 What is MCP?

**Model Context Protocol (MCP)** is an open standard for connecting AI agents to tools.

### Without MCP
Each AI app defines its own tools locally.

### With MCP
Tools are provided by external **MCP servers** that any AI app can connect to.

```
┌─────────────────────────────────────────────────┐
│                   Your Agent                    │
│                                                 │
│   ┌────────────────┐      ┌────────────────┐    │
│   │  Local Tools   │      │  MCP Client    │    │
│   │ (get_weather)  │      │                │    │
│   └────────────────┘      └────────┬───────┘    │
│                                    │            │
└────────────────────────────────────┼────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │   MCP Protocol      │
                          └──────────┬──────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
     ┌────────▼───────────┐  ┌──────▼──────┐  ┌───────────▼─────────┐
     │  Microsoft Learn   │  │  Custom     │  │   Your Own MCP      │
     │  MCP Server        │  │  MCP Server │  │   Server            │
     │ (Azure docs, etc)  │  │             │  │                     │
     └────────────────────┘  └─────────────┘  └─────────────────────┘
```

### Why MCP?
| Benefit | Description |
|---------|-------------|
| **Reusable** | One server, many apps |
| **Modular** | Add tools without code changes |
| **Standard** | Works with Claude, ChatGPT, your agent |

---

## 📁 Step 1: Create Your Project Folder

```bash
mkdir -p phase-05
cd phase-05
```

---

## 📋 Step 2: Copy Files from Phase 4

Start with Phase 5's working code:

```bash
cp ../phase-04/app.py .
cp ../phase-04/tools.py .
```

---

## 🔧 Step 3: Add MCP Tools

The Microsoft Agent Framework supports MCP through `MCPStreamableHTTPTool`. Update `app.py` to include MCP:

```python
import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

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
    """Create an Agent Framework chat client using Foundry."""
    client = FoundryChatClient(
        project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        model=os.getenv("FOUNDRY_MODEL"),
        credential=DefaultAzureCredential()
    )
    return client

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
    client = get_chat_client()
    mcp_tools = get_mcp_tools()

    # Combine local tools with MCP tools
    all_tools = [*TOOLS, *mcp_tools]

    agent = Agent(
        client=client,
        name="Aria",
        description="A helpful AI assistant with local and MCP tools",
        instructions=INSTRUCTIONS,
        tools=all_tools,
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

## 🌐 Step 4: Understanding MCP in Agent Framework

The Microsoft Agent Framework supports MCP through `MCPStreamableHTTPTool`:

```python
from agent_framework import MCPStreamableHTTPTool

# Add an MCP server tool
mcp_tool = MCPStreamableHTTPTool(
    name="microsoft_learn",
    url="https://learn.microsoft.com/api/mcp"
)

# Add to agent
agent = ChatAgent(
    chat_client=chat_client,
    tools=[mcp_tool, *local_tools]
)
```

**Key points:**
- `MCPStreamableHTTPTool` connects to external MCP servers via HTTP
- Tools are discovered automatically from the server
- Combine with local tools using list concatenation
- Use try/except when connecting to avoid startup failures if server is unavailable

### Available MCP Servers

| Server | URL | Purpose |
|--------|-----|---------|
| **Microsoft Learn** | `https://learn.microsoft.com/api/mcp` | Azure, cloud, and technical documentation |
| **Custom Servers** | `https://your-server.com/mcp` | Your own MCP-compatible servers |

---

## ▶️ Step 5: Run and Test

```bash
chainlit run app.py -w
```

### Test Scenarios

**Test 1: Local tool (weather)**
```
You: What's the weather in London?
[get_weather step appears]
Aria: It's 7°C in London...
```

**Test 2: MCP tool (Microsoft Learn documentation)**
```
You: How do I create an Azure storage account using az cli?
[microsoft_learn step appears]
Aria: To create an Azure storage account using the Azure CLI, use this command:
      az storage account create --name myaccount --resource-group mygroup --location eastus
      For more details, check the Azure documentation...
```

**Test 3: General questions (no tool needed)**
```
You: What is Python?
Aria: Python is a programming language...
```

---

## 📋 Your Complete app.py

```python
"""
Phase 5: Agent with MCP Integration
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
from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

from tools import TOOLS

load_dotenv()

INSTRUCTIONS = f"""You are a helpful AI assistant named Aria.

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
    """Create an Agent Framework chat client using Foundry."""
    client = FoundryChatClient(
        project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        model=os.getenv("FOUNDRY_MODEL"),
        credential=DefaultAzureCredential()
    )
    return client

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
    client = get_chat_client()
    mcp_tools = get_mcp_tools()

    # Combine local tools with MCP tools
    all_tools = [*TOOLS, *mcp_tools]

    agent = Agent(
        client=client,
        name="Aria",
        description="A helpful AI assistant with local and MCP tools",
        instructions=INSTRUCTIONS,
        tools=all_tools,
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
phase-06/
├── app.py          # Agent with local + MCP tools
└── tools.py        # Local tool definitions
```

---

## 💡 Key Takeaways

You now have an agent that:
1. Uses **local tools** (weather from tools.py)
2. Can use **remote MCP tools** (when configured)
3. **Combines** both seamlessly!

### Adding More MCP Servers

```python
mcp_tools = [
    MCPStreamableHTTPTool(name="server1", url="https://server1.com/mcp"),
    MCPStreamableHTTPTool(name="server2", url="https://server2.com/mcp"),
]
```

### Example: Asking About Azure CLI

```
User: How do I create an Azure storage account using az cli?

Expected Flow:
1. Agent recognizes this is an Azure/CLI question
2. Calls microsoft_learn MCP tool to search documentation
3. MCP server returns relevant Azure Storage account creation steps
4. Agent synthesizes the response with practical examples
5. User sees both weather tool AND microsoft_learn tool steps in UI

Sample Response:
"To create an Azure storage account using the Azure CLI, use this command:

az storage account create \
  --name mystorageaccount \
  --resource-group myresourcegroup \
  --location eastus \
  --sku Standard_LRS

Key parameters:
- --name: Must be unique across Azure (3-24 characters, lowercase letters and numbers only)
- --resource-group: Name of your resource group
- --location: Azure region (e.g., eastus, westus, northeurope)
- --sku: Storage account type (Standard_LRS for general use)

For more details, see the Microsoft Learn documentation..."
```

---

## ✅ Checkpoint

| Check | Status |
|-------|--------|
| Phase 4 code copied | ☐ |
| Weather queries still work | ☐ |
| MCP server configured (Microsoft Learn) | ☐ |
| Azure/documentation questions work with MCP | ☐ |
| Tool steps visualize correctly | ☐ |

### 🎉 Congratulations!

You've completed the workshop! Your agent now:
- ✅ Has a chat UI with streaming
- ✅ Remembers conversation history
- ✅ Uses local tools (weather)
- ✅ Connects to remote MCP servers (Microsoft Learn)
- ✅ Visualizes both local and MCP tool calls
- ✅ Can answer Azure/cloud documentation questions

---

## ❓ Common Issues

### MCP connection errors
Check your network can reach the MCP server URL.

### Tool not appearing
- Check the MCP server URL is correct
- Verify tools are combined: `[*TOOLS, *mcp_tools]`

### MCP tool not being used
- Check the system prompt mentions when to use the MCP tool
- Verify the MCP server URL is accessible
- Look for tool step visualization in the UI to confirm it's being called
- Try asking more directly about Azure/cloud topics

### MCP server connection errors
- Verify the server URL is correct and accessible
- Check your network connection
- The try/except block will log a warning if connection fails
- The agent will still work with just local tools

---

👉 **Next: [Phase 6: Agent Skills](06-agent-skills.md)**
