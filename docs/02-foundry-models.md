# Phase 2: Connecting to Foundry Models

> ⏱️ **Time to complete**: 10 minutes

In this phase, we'll connect to **Foundry Models**.

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Test the connection with the OpenAI model

---

## 🧪 Step 1: Test the Connection

Create a test file in a new `phase-02` folder:

```bash
mkdir -p phase-02
cd phase-02
touch test_foundry_models.py
```

Now open `test_foundry_models.py` and add this code:

```python
"""
Phase 2: Test Foundry Models Connection
Run with: python test_foundry_models.py
"""

import asyncio
import os
from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential


# Load environment variables
load_dotenv()

async def main():
    """Test connection to Foundry using FoundryChatClient."""

    print("🔄 Connecting to Foundry...")

    # Create a Foundry chat client pointing to your model deployment
    client = FoundryChatClient(
        project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        model=os.getenv("FOUNDRY_MODEL"),
        credential=DefaultAzureCredential()
    )

    # Test the connectioon
    print("📤 Sending test message...")
    agent = Agent(
        client=client,
        name="HelloAgent",
        instructions="You are a friendly assistant. Keep your answers brief.",
    )
        
    result = await agent.run("Say 'Hello from Foundry!' and nothing else.")
    print(f"Agent: {result}")
    print("✅ Connection successful!")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## ▶️ Step 2: Run the Test

```bash
python test_foundry_models.py
```

**Expected output:**
```
🔄 Connecting to Foundry...
📤 Sending test message...
Agent: Hello from Foundry!
✅ Connection successful!
```

---

## 🔍 Understanding the Code

```python
# Create Foundry client pointing
client = FoundryChatClient(
    project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
    model=os.getenv("FOUNDRY_MODEL"),
    credential=DefaultAzureCredential()
)

# Configure the agent with client and instructions
print("📤 Sending test message...")
agent = Agent(
    client=client,
    name="HelloAgent",
    instructions="You are a friendly assistant. Keep your answers brief.",
)
    
# Send a message and get a response
result = await agent.run("Say 'Hello from Foundry!' and nothing else.")
print(f"Agent: {result}")

```

**Key points:**
- `FoundryChatClient` is the client to use when accessing models deployed in Microsoft Foundry
- `model` is the deployment name
- `credential` provides the user configured with permission to the deployed model
- `agent.run()` calls the LLM
- We'll build this out more in later phases to add tools, MCP, and skills

---

## 🗂️ Project Structure

```
agent-framework-workshop/
├── .venv/
├── .env                        # Contains FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL
├── requirements.txt
└── phase-02/
    └── test_foundry_models.py   # Connection test
```

---

## ✅ Checkpoint

| Check | Status |
|-------|--------|
| Foundry access configured | ☐ |
| Access variables saved in `.env` | ☐ |
| Test script runs successfully | ☐ |
| Received response from model | ☐ |

### 🎉 Connected?

You're talking to AI! Let's build a chat interface.

**Phase progression:**
- **Phase 2** (current): Basic agent - simple connection test
- **Phase 3**: Add Chainlit UI with streaming
- **Phase 4**: Add tool calling capabilities
- **Phase 5**: Connect to MCP servers
- **Phase 6**: Add Skills to the agent

👉 **Next: [Phase 3: Chainlit Basics](03-chainlit-basics.md)**

---

## ❓ Common Issues

### "401 Unauthorized"
- Verify `.env` is populated as instructed in the Workshop

### "Module not found"
- Make sure your virtual environment is activated
- Run `pip install -r requirements.txt` again

---

## 📚 Available Models

| Model | Best For |
|-------|----------|
| `gpt-5.4` | Complex tasks, best quality |
| `gpt-4o-mini` | Fast, cost-effective |

We use `gpt-4o-mini` for the workshop - it's fast and supports tool calling.
