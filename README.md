# Microsoft Agent Framework + Chainlit Workshop

A hands-on workshop teaching how to build AI chat agents using **Microsoft Agent Framework**, **Chainlit**, and **Foundry Models**.

## What You'll Build

A fully functional AI chat agent with:
- Web-based chat interface (Chainlit)
- Conversation memory
- Tool calling (weather API)
- MCP (Model Context Protocol) integration
- File-based Agent Skills (instructions + scripts + data)

## Prerequisites

- Python 3.10+
- Access to a Foundry project and model deployment
- Basic Python knowledge

## Workshop Phases

| Phase | Topic | Time |
|-------|-------|------|
| 1 | Environment Setup | 10 min |
| 2 | Foundry Models Connection | 10 min |
| 3 | Chainlit Chat Interface | 15 min |
| 4 | Tool Calling | 20 min |
| 5 | MCP Integration | 15 min |
| 6 | Agent Skills | 20 min |

**Total time: ~90 minutes**

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
# Edit .env with your FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL

# Run the final solution
chainlit run solutions/phase-06/app.py -w
```

## Documentation

**Quick links:**
- **Start:** [Phase 1: Environment Setup](docs/01-environment.md)
- **Help:** [Troubleshooting Guide](docs/99-troubleshooting.md)

## Key Technologies

- **[Microsoft Agent Framework](https://github.com/microsoft/agent-framework)** - Microsoft's framework for building AI agents
- **[Chainlit](https://chainlit.io)** - Build conversational AI interfaces
- **[Foundry Models](https://learn.microsoft.com/en-us/azure/ai-foundry/)** - Access to AI models deployed in Microsoft Foundry

## License

MIT
