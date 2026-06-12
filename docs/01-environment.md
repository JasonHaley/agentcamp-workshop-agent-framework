# Phase 1: Environment Setup

> ⏱️ **Time to complete**: 10 minutes

Let's set up your development environment for building AI agents with Microsoft Agent Framework.

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Create a Python virtual environment
- Install required packages
- Set up your project structure

---

## 📋 Prerequisites

Before starting, ensure you have:
- [ ] Python 3.10, 3.11, 3.12 or 3.13 installed
- [ ] A code editor (VS Code recommended)
- [ ] Terminal/command line access
- [ ] A GitHub account (optional)

---

## 🐍 Step 1: Verify Python Installation

Open your terminal and check your Python version:

```bash
python --version
```

You should see Python 3.10 or higher. If not, [download Python](https://www.python.org/downloads/).

> **NOTE: As of June 2026 Chainlit ***does not*** yet support 3.14**

---

## 📁 Step 2: Create Project Directory

Create a new folder for the workshop:

```bash
mkdir agent-framework-workshop
cd agent-framework-workshop
```

---

## 🔒 Step 3: Create Virtual Environment

Create an isolated Python environment:

```bash
python -m venv .venv
```

**Activate it:**

| OS | Command |
|----|---------|
| macOS/Linux | `source .venv/bin/activate` |
| Windows (CMD) | `.venv\Scripts\activate.bat` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |

**You'll know it's active when you see `(.venv)` at the start of your terminal prompt.**

> 💡 **Tip:** To exit the virtual environment later, simply run `deactivate`.

---

## 📦 Step 4: Create Requirements File

Create a file called `requirements.txt` with our core dependencies:

```bash
touch requirements.txt
```

Add the following content:

```text
# Microsoft Agent Framework
agent-framework==1.8.1

# Azure credential for Foundry (DefaultAzureCredential)
azure-identity>=1.19.0

# Web UI
chainlit>=2.11.1

# Environment variables
python-dotenv>=1.2.1

# HTTP client for tools
httpx>=0.28.0

```

---

## 📥 Step 5: Install Dependencies

Install the packages:

```bash
pip install -r requirements.txt
```

Or using `uv` (faster):

```bash
uv pip install -r requirements.txt
```

This installs:
- **agent-framework** - Microsoft's AI agent framework
- **azure-identity** - Azure credential used to authenticate to Foundry
- **chainlit** - Chat UI framework
- **python-dotenv** - Environment variable management
- **httpx** - HTTP client used by the weather tool (Phase 4+)

---

## 🔑 Step 6: Create Environment File

Create a `.env` file for secrets:

```bash
touch .env
```

NOTE: We will provide the contents to this file during the workshop


> ⚠️ **Important:** Never commit `.env` to git! Add it to `.gitignore`.

---

## 📂 Project Structure

Your folder should look like this:

```
agent-framework-workshop/
├── .venv/              # Virtual environment
├── .env                # Environment variables (secrets)
└── requirements.txt    # Dependencies
```

---

## ✅ Checkpoint

| Check | Status |
|-------|--------|
| Python 3.10+ installed | ☐ |
| Virtual environment created and activated | ☐ |
| Dependencies installed | ☐ |
| `.env` file created | ☐ |

### 🎉 Environment Ready?

You're all set up! Let's connect to the foundry models.

👉 **Next: [Phase 2: Foundry Models](02-foundry-models.md)**

---

## ❓ Common Issues

### "Python not found"
Make sure Python is in your PATH. Try `python3 --version` on macOS/Linux.

### "pip not found"
Use `python -m pip install -r requirements.txt` instead.

### Virtual environment not activating
On Windows PowerShell, you may need to run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
