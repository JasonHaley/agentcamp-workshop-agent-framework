# Phase 2: Connecting to GitHub Models

> ⏱️ **Time to complete**: 10 minutes

In this phase, we'll connect to **GitHub Models** - a free way to access AI models like GPT-4o.

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Understand what GitHub Models offers
- Create a Personal Access Token (PAT)
- Test the connection with the OpenAI library

---

## 🤖 What is GitHub Models?

GitHub Models provides **free access** to AI models directly from GitHub:

| Feature | Details |
|---------|---------|
| **Models** | GPT-4o, GPT-4o-mini, o3-mini, and more |
| **Cost** | Free tier available |
| **Access** | Via OpenAI-compatible API |
| **Auth** | GitHub Personal Access Token |

The endpoint `https://models.github.ai/inference` provides an OpenAI-compatible API.

---

## 🔑 Step 1: Create a GitHub Token

1. Go to [GitHub Settings → Tokens](https://github.com/settings/tokens)
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `agent-framework-workshop`
4. Select expiration (e.g., 30 days)
5. **No scopes needed** for GitHub Models
6. Click **"Generate token"**
7. **Copy the token immediately** (you won't see it again!)

---

## 📝 Step 2: Save Your Token

Add your token to the `.env` file:

```bash
GITHUB_TOKEN=ghp_your_token_here
```

---

## 🧪 Step 3: Test the Connection

Create a test file in a new `phase-02` folder:

```bash
mkdir -p phase-02
cd phase-02
touch test_github_models.py
```

Now open `test_github_models.py` and add this code:

```python
"""
Phase 2: Test GitHub Models Connection
Run with: python test_github_models.py
"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()


async def main():
    """Test connection to GitHub Models using OpenAI client."""

    print("🔄 Connecting to GitHub Models...")

    # Create an async OpenAI client pointing to GitHub Models
    client = AsyncOpenAI(
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.github.ai/inference",
    )

    # Test the connection
    print("📤 Sending test message...")
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "Say 'Hello from GitHub Models!' and nothing else.",
            }
        ],
    )

    result_text = response.choices[0].message.content
    print(f"📥 Response: {result_text}")
    print("✅ Connection successful!")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## ▶️ Step 4: Run the Test

```bash
python test_github_models.py
```

**Expected output:**
```
🔄 Connecting to GitHub Models...
📤 Sending test message...
📥 Response: Hello from GitHub Models!
✅ Connection successful!
```

---

## 🔍 Understanding the Code

```python
# Create OpenAI client pointing to GitHub Models
client = AsyncOpenAI(
    api_key=os.getenv("GITHUB_TOKEN"),      # Your GitHub token
    base_url="https://models.github.ai/inference",  # GitHub Models endpoint
)

# Send a message and get a response
response = await client.chat.completions.create(
    model="gpt-4o-mini",                    # Model to use
    messages=[
        {
            "role": "user",
            "content": "Your message here"
        }
    ],
)

# Extract the response text
result_text = response.choices[0].message.content
print(result_text)
```

**Key points:**
- `AsyncOpenAI` is the OpenAI client library for asynchronous requests
- `api_key` is your GitHub Personal Access Token
- `base_url` points to the GitHub Models API endpoint
- `client.chat.completions.create()` is the standard OpenAI API call
- We'll wrap this with the Agent Framework in Phase 4 to add reasoning and tool capabilities

---

## 🗂️ Project Structure

```
agent-framework-workshop/
├── .venv/
├── .env                        # Contains GITHUB_TOKEN
├── requirements.txt
└── phase-02/
    └── test_github_models.py   # Connection test
```

---

## ✅ Checkpoint

| Check | Status |
|-------|--------|
| GitHub token created | ☐ |
| Token saved in `.env` | ☐ |
| Test script runs successfully | ☐ |
| Received response from model | ☐ |

### 🎉 Connected?

You're talking to AI! Let's build a chat interface.

**Phase progression:**
- **Phase 2** (current): Raw OpenAI client - simple connection test
- **Phase 3**: Add Chainlit UI with streaming
- **Phase 4**: Introduce Microsoft Agent Framework for reasoning
- **Phase 5**: Add tool calling capabilities
- **Phase 6**: Connect to MCP servers

👉 **Next: [Phase 3: Chainlit Basics](03-chainlit-basics.md)**

---

## ❓ Common Issues

### "401 Unauthorized"
- Check your `GITHUB_TOKEN` is correct in `.env`
- Make sure there are no extra spaces around the token
- Token might have expired - generate a new one

### "Module not found"
- Make sure your virtual environment is activated
- Run `pip install -r requirements.txt` again

### "Rate limit exceeded"
GitHub Models has rate limits. Wait a few minutes and try again.

---

## 📚 Available Models

| Model | Best For |
|-------|----------|
| `gpt-4o` | Complex tasks, best quality |
| `gpt-4o-mini` | Fast, cost-effective |
| `o3-mini` | Reasoning tasks |

We use `gpt-4o-mini` for the workshop - it's fast and supports tool calling.
