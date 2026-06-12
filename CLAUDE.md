# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hands-on workshop teaching how to build AI chat agents using Microsoft Agent Framework, Chainlit, and Microsoft Foundry Models. The codebase is organized into progressive phases, each building on the previous one.

## Common Commands

```bash
# Run any Chainlit app
chainlit run app.py -w

# Run specific phase solution
chainlit run solutions/phase-06/app.py -w

# Test Foundry Models connection
python solutions/phase-02/test_foundry_models.py

# Install dependencies
pip install -r requirements.txt
# or with uv (faster)
uv pip install -r requirements.txt
```

## Architecture

### Phase Progression
The workshop builds incrementally through 6 phases:

1. **Phase 1**: Environment setup - Python venv, dependencies
2. **Phase 2**: Foundry Models connection test - `Agent` + `FoundryChatClient`, no UI
3. **Phase 3**: Basic Chainlit chat with streaming and conversation memory (`session`)
4. **Phase 4**: Tool calling - a `get_weather` function tool added to the agent
5. **Phase 5**: MCP integration - combines local tools with `MCPStreamableHTTPTool` for remote servers
6. **Phase 6**: Agent Skills - file-based skills (`SKILL.md` + scripts + data) via `SkillsProvider`

> The Agent Framework is used from **Phase 2 onward** — there is no raw-OpenAI phase. Every phase uses the same `Agent` + `FoundryChatClient` foundation and adds one new capability.

### Key Patterns

**Chat Client** (every phase 2+): `FoundryChatClient` authenticated with `DefaultAzureCredential`:
```python
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

client = FoundryChatClient(
    project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
    model=os.getenv("FOUNDRY_MODEL"),
    credential=DefaultAzureCredential(),
)
```

**Agent Creation** (every phase 2+):
```python
from agent_framework import Agent

agent = Agent(
    client=client,
    name="Aria",
    description="A helpful AI assistant",
    instructions=INSTRUCTIONS,
    tools=TOOLS,                       # added Phase 4+
    context_providers=[skills_provider],  # added Phase 6
)
```

**Session Management** (Phase 3+, for conversation history) — create once per chat, reuse on every message:
```python
session = agent.create_session()
# ...store in cl.user_session, then on each message:
result = await agent.run("message", session=session)
```

**Streaming** (Phase 3+) — `agent.run(..., stream=True)`, read `update.text`:
```python
async for update in agent.run(message, session=session, stream=True):
    if update.text:
        await answer.stream_token(update.text)
await answer.send()
```

**Tool Definition** (Phase 4+):
```python
from typing import Annotated
from pydantic import Field

def get_weather(
    city: Annotated[str, Field(description="City name")]
) -> str:
    """Docstring is critical - agent uses it to decide when to call."""
    ...

TOOLS = [get_weather]
```

> The Agent Framework handles the tool-calling loop automatically. The solutions stream text only; there is no manual `FunctionCallContent`/`FunctionResultContent` step visualization.

**MCP Tool** (Phase 5+) — wrapped in try/except so the agent still works if the server is unreachable:
```python
from agent_framework import MCPStreamableHTTPTool

mcp_tool = MCPStreamableHTTPTool(
    name="microsoft_learn",
    url="https://learn.microsoft.com/api/mcp",
)
all_tools = [*TOOLS, *mcp_tool_list]
```

**Skills** (Phase 6) — skills are **context**, not tools; registered via `context_providers`:
```python
from pathlib import Path
from agent_framework import SkillsProvider
from subprocess_script_runner import subprocess_script_runner

skills_provider = SkillsProvider.from_paths(
    skill_paths=str(Path(__file__).parent / "skills"),
    script_runner=subprocess_script_runner,
)
agent = Agent(..., context_providers=[skills_provider])
```

### File Structure
- `solutions/phase-01/requirements.txt` - Dependencies
- `solutions/phase-02/test_foundry_models.py` - Connection test
- `solutions/phase-XX/app.py` - Main Chainlit application (phases 3-6)
- `solutions/phase-XX/tools.py` - Tool definitions (phases 4-6)
- `solutions/phase-06/skills/` - File-based Agent Skills (SKILL.md + scripts + data)
- `solutions/phase-06/subprocess_script_runner.py` - Runs skill scripts as subprocesses
- `docs/01-environment.md` … `docs/06-agent-skills.md` - Workshop docs (one per phase)
- `docs/99-troubleshooting.md` - Troubleshooting guide for all phases
- `README.md` - Main project overview with quick links
- `SUMMARY.md` - GitBook-style table of contents
- `CLAUDE.md` - This file (guidance for Claude Code)

## Environment Variables

Required in `.env`:
- `FOUNDRY_PROJECT_ENDPOINT` - Microsoft Foundry project endpoint
- `FOUNDRY_MODEL` - Foundry model deployment name (e.g. `gpt-4o-mini`)
- `WEATHER_API_KEY` - WeatherAPI key for the tool demo (phase 4+)

Authentication to Foundry uses `DefaultAzureCredential` (from `azure-identity`), so the user must be signed in (e.g. `az login`).

## Common Tasks for Claude Code

When working with this repository, you may be asked to:

1. **Compare docs with solution files** - Ensure documentation matches working code
   - Docs: `docs/XX-phase-name.md`
   - Solutions: `solutions/phase-XX/app.py` and `tools.py`
   - Check imports, function names, and the streaming pattern

2. **Fix sync issues between docs and code**
   - Solution file is the source of truth
   - Update docs to match if code changed
   - Check: imports, function signatures, streaming pattern, env var names

3. **Debug issues in workshop phases**
   - Check solution files for working examples
   - Test the connection with the Phase 2 script first

4. **Update documentation**
   - Keep code examples matching the solution files exactly in the final code section
   - Ensure phase numbers, "Next" links, and project-structure folders are correct

5. **Add new content**
   - New phases should follow the established pattern
   - Solution must work before documentation is written
   - Update `README.md` and `SUMMARY.md` navigation

## Key Files to Know

- **Solution source of truth:** Each `solutions/phase-XX/app.py` is the reference
- **Documentation source of truth:** Phase docs must match the solutions
- **Help first place:** `docs/99-troubleshooting.md` for user issues
- **Navigation hubs:** `README.md` and `SUMMARY.md`
- **This file:** `CLAUDE.md` for technical context

## Verification Checklist

When fixing sync issues or adding features:

- [ ] Solution file (`solutions/phase-XX/`) exists and runs without errors
- [ ] Documentation (`docs/XX-*.md`) matches solution code in the final code section
- [ ] Imports are correct (`Agent`, `FoundryChatClient`, `DefaultAzureCredential`)
- [ ] Streaming uses `agent.run(..., stream=True)` and reads `update.text`
- [ ] Memory uses a `session` created once and reused (`agent.create_session()`)
- [ ] Phase numbers, "Next" links, and project-structure folders are consistent
- [ ] Env var names are `FOUNDRY_PROJECT_ENDPOINT` / `FOUNDRY_MODEL` (not `GITHUB_TOKEN`)
- [ ] `README.md` / `SUMMARY.md` updated with new/changed content

## Workshop Writing Guidelines

This section documents how the training materials are structured, useful for creating new workshops.

### Documentation Structure

Each phase doc (`docs/XX-phase-name.md`) follows this pattern:
1. **Header** with time estimate and learning objectives
2. **Concept explanation** with ASCII diagrams where helpful
3. **Step-by-step instructions** that build incrementally
4. **Complete code example** at the end for reference
5. **Project structure** showing expected files
6. **Checkpoint** with testable scenarios
7. **Common issues** section for troubleshooting

### Progressive Complexity

- Each phase builds on the previous one with minimal new concepts
- Early steps show a minimal working version, then enhance it
- Each phase copies the previous phase's solution as a starting point

### Code Consistency (Phase 2-6, Agent Framework + Foundry)

- Solution files in `solutions/phase-XX/` must match the final code in docs
- Client: `FoundryChatClient` with `DefaultAzureCredential`
- Agent: `agent_framework.Agent` with `client=`, `instructions=`
- Streaming pattern: `async for update in agent.run(message, session=session, stream=True)`
- Memory: create a `session` once in `@cl.on_chat_start` and reuse it on every message
- Tools (Phase 4+): plain functions with `Annotated[..., Field(...)]` params and a clear docstring
- Skills (Phase 6): registered via `context_providers`, not `tools`

### Practical Elements

- Each phase folder created with `mkdir -p phase-XX && cd phase-XX && touch app.py`
- Files to create are explicitly listed (no implicit file creation)
- Virtual environment tip: mention `deactivate` to exit
- Chainlit auto-creates `chainlit.md` - no need to copy between phases
- Time estimates are realistic (total ~90 minutes)

### Testing Checkpoints

Each phase includes specific test scenarios:
- Concrete user inputs to try
- Expected outputs/behaviors
- Visual confirmations (e.g., "skill runs the bundled script instead of guessing")
