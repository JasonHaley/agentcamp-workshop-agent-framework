# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hands-on workshop teaching how to build AI chat agents using Microsoft Agent Framework, Chainlit, and GitHub Models. The codebase is organized into progressive phases, each building on the previous one.

## Common Commands

```bash
# Run any Chainlit app
chainlit run app.py -w

# Run specific phase solution
chainlit run solutions/phase-06/app.py -w

# Test GitHub Models connection
python solutions/phase-02/test_github_models.py

# Install dependencies
pip install -r requirements.txt
# or with uv (faster)
uv pip install -r requirements.txt
```

## Architecture

### Phase Progression
The workshop builds incrementally through 6 phases:

1. **Phase 1**: Environment setup - Python venv, dependencies
2. **Phase 2**: GitHub Models connection test - raw `AsyncOpenAI` client only (no frameworks)
3. **Phase 3**: Basic Chainlit chat with streaming - uses raw `AsyncOpenAI` with dict-based message history
4. **Phase 4**: Microsoft Agent Framework introduction - introduces `ChatAgent` with `AgentThread`
5. **Phase 5**: Tool calling - `ChatAgent` with `FunctionCallContent`/`FunctionResultContent` tool handling
6. **Phase 6**: MCP integration - combines local tools with `MCPStreamableHTTPTool` for remote servers

### Key Patterns

**Phase 2-3: Raw OpenAI Client** (no frameworks):
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.github.ai/inference",
)
# Direct API calls
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    stream=True,
)
```

**Phase 4-6: Agent Framework Chat Client**:
```python
from openai import AsyncOpenAI
from agent_framework.openai import OpenAIChatClient

openai_client = AsyncOpenAI(
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.github.ai/inference",
)
chat_client = OpenAIChatClient(
    async_client=openai_client,
    model_id="gpt-4o-mini",
)
```

**Agent Creation** (Phase 4+):
```python
from agent_framework import ChatAgent

agent = ChatAgent(
    chat_client=chat_client,
    instructions=SYSTEM_PROMPT,
    tools=TOOLS,  # Empty in Phase 4, populated in Phase 5+
    temperature=0.7,
)
```

**Thread Management** (Phase 4+, for conversation history):
```python
thread = agent.get_new_thread()
result = await agent.run("message", thread=thread)
```

**Streaming** (Phase 3: raw OpenAI, Phase 4+: agent):
```python
# Phase 3 (raw OpenAI)
async for chunk in stream:
    if chunk.choices and len(chunk.choices) > 0:
        content = chunk.choices[0].delta.content
        if content:
            await msg.stream_token(content)

# Phase 4+ (Agent Framework)
async for update in agent.run_stream("message", thread=thread):
    if update.text:
        await msg.stream_token(update.text)
```

**Tool Visualization** (Phase 5+):
```python
from agent_framework import FunctionCallContent, FunctionResultContent

if isinstance(content, FunctionCallContent):
    if content.name and content.call_id not in tool_steps:
        step = cl.Step(name=f"🔧 {content.name}", type="tool")
        await step.send()
        tool_steps[content.call_id] = step
elif isinstance(content, FunctionResultContent):
    step = tool_steps.get(content.call_id)
    if step:
        step.output = content.result
        await step.update()
```

**Tool Definition** (Phase 5+):
```python
from typing import Annotated
from pydantic import Field

def get_weather(
    city: Annotated[str, Field(description="City name")]
) -> str:
    """Docstring is critical - agent uses it to decide when to call."""
    ...
```

**MCP Tool** (Phase 6):
```python
from agent_framework import MCPStreamableHTTPTool

mcp_tool = MCPStreamableHTTPTool(
    name="microsoft_learn",
    url="https://learn.microsoft.com/api/mcp"
)
```

### File Structure
- `solutions/phase-XX/app.py` - Main Chainlit application for each phase
- `solutions/phase-XX/tools.py` - Tool definitions (phases 5-6)
- `docs/01-06-*.md` - Workshop documentation for each phase (6 files)
- `docs/INDEX.md` - Complete documentation index and learning guide
- `docs/07-troubleshooting.md` - Comprehensive troubleshooting guide for all phases
- `README.md` - Main project overview with quick links
- `CLAUDE.md` - This file (guidance for Claude Code)

## Environment Variables

Required in `.env`:
- `GITHUB_TOKEN` - GitHub personal access token for GitHub Models API
- `WEATHER_API_KEY` - WeatherAPI key for tool demo (phase 5+)

## Common Tasks for Claude Code

When working with this repository, you may be asked to:

1. **Compare docs with solution files** - Ensure documentation matches working code
   - Docs: `docs/XX-phase-name.md`
   - Solutions: `solutions/phase-XX/app.py` and `tools.py`
   - Use diffs to check imports, function names, patterns

2. **Fix sync issues between docs and code**
   - Solution file is the source of truth
   - Update docs to match if code changed
   - Check: imports, function signatures, streaming patterns, tool handling

3. **Debug issues in workshop phases**
   - Check solution files for working examples
   - Verify imports match (especially Phase 5: `FunctionCallContent`, `FunctionResultContent`)
   - Test individual components (use Phase 2 test script as template)

4. **Update documentation**
   - Add explanations or clarifications
   - Update code examples to match current best practices
   - Ensure all phases show correct imports and patterns
   - Keep consistency: all agents have `temperature=0.7`, all streams use safety checks

5. **Add new content**
   - New phases should follow the established pattern
   - Solution must work before documentation is written
   - Documentation should match solution file exactly in final code section
   - Add to `docs/INDEX.md` navigation

## Key Files to Know

- **Solution source of truth:** Each `solutions/phase-XX/app.py` is the reference
- **Documentation source of truth:** Phases must match solutions
- **Help first place:** `docs/07-troubleshooting.md` for user issues
- **Navigation hub:** `docs/INDEX.md` for learning paths
- **This file:** `CLAUDE.md` for technical context

## Verification Checklist

When fixing sync issues or adding features:

- [ ] Solution file (`solutions/phase-XX/`) exists and runs without errors
- [ ] Documentation (`docs/XX-*.md`) matches solution code exactly in final sections
- [ ] Imports are correct and match phase-specific patterns
- [ ] Tool handling uses `isinstance()` not `hasattr()` (Phase 5+)
- [ ] Streaming patterns include safety checks (Phase 3: `if chunk.choices and len...`)
- [ ] All agents have `temperature=0.7` (Phase 4+)
- [ ] Threads are used for memory (Phase 4+)
- [ ] `docs/INDEX.md` updated with new/changed content
- [ ] `CLAUDE.md` updated with patterns if changed

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
- Early steps show simplified code, final code adds all parameters (e.g., `temperature=0.7`)
- Code is introduced incrementally: first a minimal working version, then enhanced
- Explicit "What's new" tables comparing current phase to previous

### Code Consistency

**Phase 2-3 (Raw OpenAI):**
- No Agent Framework imports
- Direct API calls with `client.chat.completions.create()`
- Streaming with `stream=True` parameter
- Message history as dicts in lists
- Safety checks: `if chunk.choices and len(chunk.choices) > 0:`

**Phase 4-6 (Agent Framework):**
- Solution files in `solutions/phase-XX/` must match the final code in docs exactly
- All agents include `temperature=0.7` in final versions
- Streaming pattern: `async for update in agent.run_stream(...)`
- Thread management: always pass `thread=thread` for conversation history
- Tool handling: Use `isinstance(content, FunctionCallContent)` not `hasattr()`
- Tool tracking: Use `tool_steps = {}` dict with `content.call_id` as key

### Practical Elements

- Each phase folder created with `mkdir -p phase-XX && cd phase-XX && touch app.py`
- Files to create are explicitly listed (no implicit file creation)
- Virtual environment tip: mention `deactivate` to exit
- Chainlit auto-creates `chainlit.md` - no need to copy between phases
- Time estimates are realistic (total ~85 minutes tested)

### Testing Checkpoints

Each phase includes specific test scenarios:
- Concrete user inputs to try
- Expected outputs/behaviors
- Visual confirmations (e.g., "tool step appears in UI")

## Key Differences from LangChain Workshop

### Phase 2-3: Raw OpenAI
- **LangChain Workshop:** Uses `ChatOpenAI` from LangChain
- **Agent Framework Workshop:** Uses raw `AsyncOpenAI` from OpenAI library
  - Reason: Teach OpenAI library first, then wrap with Agent Framework
  - Simpler, more direct path to understanding LLMs

### Phase 4-6: Agent Framework vs LangChain

| Aspect | LangChain | Agent Framework |
|--------|-----------|-----------------|
| Agent creation | `create_agent()` helper | `ChatAgent()` class |
| Conversation history | Dict-based messages | `AgentThread` |
| Streaming | `astream()` with stream_mode | `run_stream()` |
| Tool definition | `@tool` decorator | Function with `Annotated` |
| Tool handling | `ToolCall` objects | `FunctionCallContent`/`FunctionResultContent` |
| Tool tracking | Tool name as key | `call_id` as key |
| MCP tools | `langchain-mcp-adapters` | `MCPStreamableHTTPTool` |
| Message format | LangChain messages | Dict-based messages (OpenAI format) |

### Workshop Structure
- **LangChain:** All 6 phases use LangChain
- **Agent Framework:** Phases 2-3 are framework-agnostic (raw OpenAI), then introduce Agent Framework in Phase 4
