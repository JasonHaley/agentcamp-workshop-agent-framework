# Microsoft Agent Framework + Chainlit Workshop

A hands-on workshop teaching how to build AI chat agents using **Microsoft Agent Framework**, **Chainlit**, and **GitHub Models**.

## What You'll Build

A fully functional AI chat agent with:
- Web-based chat interface (Chainlit)
- Conversation memory
- Tool calling (weather API)
- MCP (Model Context Protocol) integration

## Prerequisites

- Python 3.10+
- GitHub account (for GitHub Models access)
- Basic Python knowledge

## Workshop Phases

| Phase | Topic | Time |
|-------|-------|------|
| 1 | Environment Setup | 10 min |
| 2 | GitHub Models Connection | 10 min |
| 3 | Chainlit Chat Interface | 15 min |
| 4 | Microsoft Agent Framework Agents | 15 min |
| 5 | Tool Calling | 20 min |
| 6 | MCP Integration | 15 min |

**Total time: ~85 minutes**

## Quick Start

```bash
# Clone the repo
git clone <repo-url>
cd agent-framework-chainlit-workshop

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your GITHUB_TOKEN

# Run the final solution
chainlit run solutions/phase-06/app.py -w
```

## Documentation

**Quick links:**
- **Start:** [Phase 1: Environment Setup](docs/01-environment.md)
- **Help:** [Troubleshooting Guide](docs/07-troubleshooting.md)

## Key Technologies

- **[Microsoft Agent Framework](https://github.com/microsoft/agent-framework)** - Microsoft's framework for building AI agents
- **[Chainlit](https://chainlit.io)** - Build conversational AI interfaces
- **[GitHub Models](https://github.com/marketplace/models)** - Free access to AI models

## License

MIT
