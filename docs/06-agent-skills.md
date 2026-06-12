# Phase 6: Agent Skills

> ⏱️ **Time to complete**: 20 minutes

In this final phase, we'll give our agent **Skills** — self-contained folders that package domain knowledge *and* the scripts and data needed to act on it. Skills are how you teach an agent to do something reliably that it would otherwise guess at.

---

## 🎯 Learning Objectives

By the end of this phase, you will:
- Understand what an Agent Skill is and how it differs from a tool or an MCP server
- Understand the **anatomy of a skill** (`SKILL.md` + `scripts/` + `data/`)
- Add file-based skills to your agent with `SkillsProvider`
- Understand **progressive disclosure** — why skills scale better than stuffing everything into the system prompt
- Run a skill's bundled script through a **script runner**

---

## 🧩 What is an Agent Skill?

A **Skill** is a folder on disk that bundles three things:

1. **Instructions** (`SKILL.md`) — when to use the skill and how to use it, written for the model to read.
2. **Scripts** — deterministic code the agent runs instead of doing error-prone work itself (date math, table lookups, parsing).
3. **Data** — files the scripts depend on (a CSV rate card, a policy document, a template).

The agent reads the `SKILL.md`, decides whether the skill applies, and — if it does — runs the bundled script through a **script runner** and uses the output.

### Tools vs. MCP vs. Skills

You've now seen all three ways to extend an agent. They solve different problems:

| | Where it lives | Best for |
|---|---|---|
| **Tool** (Phase 4) | A Python function, in-process | A single, well-defined action (`get_weather`) |
| **MCP** (Phase 5) | A remote server over HTTP | Tools maintained by someone else, shared across apps |
| **Skill** (Phase 6) | A folder on disk (docs + scripts + data) | Packaging *domain expertise* — knowledge, deterministic scripts, and reference data together |

A tool is a verb. A skill is a **playbook**: it tells the agent *when* the capability applies, *how* to use it correctly, *how to interpret* the result, and ships the code and data to do it.

### Progressive disclosure

You could paste all of this into the system prompt — but that doesn't scale. Ten skills would mean thousands of tokens loaded on every single message, most of them irrelevant to any given question.

Skills solve this with **progressive disclosure**:

```
┌──────────────────────────────────────────────────────────┐
│  Always loaded (cheap):  name + description of each skill │
│                                                          │
│   vendor-rate-lookup     → "Look up negotiated vendor…"  │
│   contract-deadline-calc → "Compute contract renewal…"   │
└───────────────────────────┬──────────────────────────────┘
                            │  model decides a skill is relevant
                            ▼
┌──────────────────────────────────────────────────────────┐
│  Loaded on demand:  the full SKILL.md body               │
│                     + the agent runs scripts/<file>.py   │
└──────────────────────────────────────────────────────────┘
```

Only the short **description** is in context by default. The full instructions and scripts are pulled in **only when the model decides the skill is relevant** — so you can ship dozens of skills without paying for them on every turn.

---

## 📁 Step 1: Create Your Project Folder

```bash
mkdir -p phase-06
cd phase-06
```

---

## 📋 Step 2: Copy Files from Phase 5

Start with Phase 5's solution files:

```bash
cp ../phase-05/app.py .
cp ../phase-05/tools.py .
```

You now have an agent with local tools + MCP. We'll add skills on top.

---

## 🔎 Step 3: Understand the Anatomy of a Skill

A skill is just a directory with a required `SKILL.md` and any scripts/data it needs:

```
skills/
└── contract-deadline-calculator/
    ├── SKILL.md                      # required: frontmatter + instructions
    └── scripts/
        └── contract_deadlines.py     # the deterministic script
```

The **`SKILL.md`** has two parts — YAML frontmatter and a Markdown body:

```markdown
---
name: contract-deadline-calculator
description: Compute contract renewal dates, non-renewal notice deadlines, and
  days remaining with deterministic date arithmetic. Use this skill whenever the
  user asks about contract deadlines, renewal dates, notice periods... Always use
  this script instead of computing dates mentally — month-end clamping, leap
  years, and business-day counts are error-prone without it.
---

# Contract Deadline Calculator

...full instructions for the model: when to use, how to run the script,
how to interpret the output, and known limitations...
```

> 💡 **The `description` is the most important line you'll write.** It's the *only* part of the skill loaded into context by default, so it's what the model uses to decide whether to open the skill. Pack it with concrete trigger phrases ("renewal dates", "notice periods", "when do I need to act on this contract") — vague descriptions don't get matched.

---

## 🛠️ Step 4: Build Your First Skill

Let's build the `contract-deadline-calculator` skill by hand to learn the format. Create the folders:

```bash
mkdir -p skills/contract-deadline-calculator/scripts
```

### 4a. The script

LLMs are notoriously bad at calendar math — month-end clamping (Jan 31 + 1 month), leap years, business-day counts. This is exactly the kind of work to push into a deterministic script. Create `skills/contract-deadline-calculator/scripts/contract_deadlines.py`:

```python
"""Contract deadline calculator skill.

Given a contract's effective date, term length, and notice period,
computes key dates deterministically -- something LLMs frequently
get wrong when doing date math "in their head".

Usage:
    python contract_deadlines.py --effective-date 2024-03-15 \
        --term-months 24 --notice-days 90

Output: JSON to stdout (easy for an agent to parse).
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta


def add_months(d: date, months: int) -> date:
    """Add calendar months, clamping to the last valid day of the month."""
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    # Clamp day (e.g., Jan 31 + 1 month -> Feb 28/29)
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)


def business_days_between(start: date, end: date) -> int:
    """Count business days (Mon-Fri) strictly between start and end."""
    if end <= start:
        return 0
    days = 0
    current = start + timedelta(days=1)
    while current <= end:
        if current.weekday() < 5:
            days += 1
        current += timedelta(days=1)
    return days


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute contract renewal deadlines.")
    parser.add_argument("--effective-date", required=True, help="Contract effective date (YYYY-MM-DD)")
    parser.add_argument("--term-months", type=int, required=True, help="Initial term length in months")
    parser.add_argument("--notice-days", type=int, required=True, help="Non-renewal notice period in calendar days")
    parser.add_argument("--as-of", default=None, help="Reference date for 'today' (YYYY-MM-DD), defaults to current date")
    args = parser.parse_args()

    try:
        effective = datetime.strptime(args.effective_date, "%Y-%m-%d").date()
        today = (datetime.strptime(args.as_of, "%Y-%m-%d").date()
                 if args.as_of else date.today())
    except ValueError as e:
        print(json.dumps({"error": f"Invalid date format: {e}"}))
        sys.exit(1)

    term_end = add_months(effective, args.term_months)
    notice_deadline = term_end - timedelta(days=args.notice_days)
    calendar_days_left = (notice_deadline - today).days
    biz_days_left = business_days_between(today, notice_deadline)

    if calendar_days_left < 0:
        status = "MISSED - notice deadline has passed; contract will auto-renew"
    elif calendar_days_left <= 30:
        status = "URGENT - act within the next 30 days"
    elif calendar_days_left <= 90:
        status = "UPCOMING - plan your renewal decision soon"
    else:
        status = "OK - no immediate action needed"

    result = {
        "effective_date": effective.isoformat(),
        "initial_term_end": term_end.isoformat(),
        "notice_deadline": notice_deadline.isoformat(),
        "notice_deadline_weekday": notice_deadline.strftime("%A"),
        "as_of": today.isoformat(),
        "calendar_days_until_deadline": calendar_days_left,
        "business_days_until_deadline": biz_days_left,
        "status": status,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

**Two conventions worth copying into your own skills:**
- **Take arguments on the CLI** (`argparse`). The script runner forwards the agent's arguments as positional CLI args.
- **Print JSON to stdout.** Structured output is trivial for the agent to parse and reason about.

### 4b. The SKILL.md

Now create `skills/contract-deadline-calculator/SKILL.md`. The body teaches the model not just *how to run* the script but *how to interpret* it for the user:

```markdown
---
name: contract-deadline-calculator
description: Compute contract renewal dates, non-renewal notice deadlines, and days remaining with deterministic date arithmetic. Use this skill whenever the user asks about contract deadlines, renewal dates, notice periods, auto-renewal windows, "when do I need to act on this contract", or any question requiring date math on contract terms (effective dates, term lengths, notice periods). Always use this script instead of computing dates mentally — month-end clamping, leap years, and business-day counts are error-prone without it.
---

# Contract Deadline Calculator

Computes the key dates for a contract's renewal cycle from three inputs: the
effective date, the initial term length, and the non-renewal notice period.
Date arithmetic must be done with the bundled script, never estimated.

## How to use

Run the bundled script with the contract's terms:

\```bash
python scripts/contract_deadlines.py \
  --effective-date 2024-03-15 \
  --term-months 24 \
  --notice-days 90
\```

| Argument | Required | Description |
|---|---|---|
| `--effective-date` | yes | Contract effective date, `YYYY-MM-DD` |
| `--term-months` | yes | Initial term length in whole months |
| `--notice-days` | yes | Non-renewal notice period in calendar days |
| `--as-of` | no | Override "today" (`YYYY-MM-DD`); defaults to the current date |

## Interpreting results for the user

- Lead with the `notice_deadline` and its weekday — that is the actionable date.
- If status is `MISSED`, state clearly that the contract will auto-renew.
- If the notice deadline falls on a weekend, recommend acting by the preceding Friday.
- Quote business days when the user is planning work; calendar days for general urgency.

## Limitations

- Assumes the notice period is measured in calendar days before the end of the initial term.
- Does not account for public holidays in business-day counts (weekends only).
```

> 📄 The full `SKILL.md` in the solution has more detail (a complete arguments table, a sample output block, and a richer "interpreting results" section). The richer the body, the better the agent uses the skill — but remember **none of it costs you tokens until the skill is actually triggered.**

---


## 📦 Step 5: Add a Second Skill (with bundled data)

Skills shine when they carry **data** the model couldn't possibly know — internal rates, private policies, proprietary tables. Copy the `vendor-rate-lookup` skill from the solution to see this:

```bash
cp -r ../../solutions/phase-06/skills/vendor-rate-lookup skills/
```

Its structure adds a `data/` folder:

```
skills/vendor-rate-lookup/
├── SKILL.md
├── scripts/
│   └── rate_lookup.py        # reads ../data/rate_card.csv
└── data/
    └── rate_card.csv         # internal negotiated rates — not public knowledge
```

The key idea is in its description:

> *"These rates are internal negotiated terms that exist ONLY in the bundled rate card — never estimate, recall, or guess a rate; always query the script."*

This is the whole point of a data-backed skill: it turns *"the model is guessing"* into *"the model is reading the company's actual rate card."* The `SKILL.md` even instructs the agent to cite the governing contract (`contract_ref`) so the answer is procurement-ready.

> 🗂️ **Two skills now coexist.** With progressive disclosure, the agent sees both descriptions, but only opens the one that matches the question — a rate question loads `vendor-rate-lookup`; a renewal question loads `contract-deadline-calculator`.

---

## ⚙️ Step 6: Add the Script Runner

A skill describes *what* to run — but something has to actually execute it. That's the **script runner**: a function you provide that takes a skill's script and arguments and runs it. Keeping this separate means *you* control how (and whether) skill code executes.

Copy the sample runner from the solution:

```bash
cp ../../solutions/phase-06/subprocess_script_runner.py .
```

> NOTE: This is taken from the agent framework codebase: [https://github.com/microsoft/agent-framework/blob/main/python/samples/02-agents/skills/subprocess_script_runner.py](https://github.com/microsoft/agent-framework/blob/main/python/samples/02-agents/skills/subprocess_script_runner.py)

It runs each script as a local Python **subprocess**, forwarding the agent's arguments as CLI args and capturing stdout/stderr:

```python
def subprocess_script_runner(
    skill: FileSkill, script: FileSkillScript, args: dict[str, Any] | list[str] | None = None
) -> str:
    """Run a skill script as a local Python subprocess."""
    script_path = Path(script.full_path)
    if not script_path.is_file():
        return f"Error: Script file not found: {script_path}"

    cmd = [sys.executable, str(script_path)]
    if isinstance(args, list):
        cmd.extend(args)            # forwarded as positional CLI arguments

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=30, cwd=str(script_path.parent),
    )
    output = result.stdout
    if result.stderr:
        output += f"\nStderr:\n{result.stderr}"
    return output.strip() or "(no output)"
```

> ⚠️ **Security note:** A script runner executes code. The sample runs scripts as local subprocesses with a 30-second timeout — fine for a workshop on your own machine. In production you'd sandbox this (a container, restricted permissions, an allow-list) before running skills you didn't author. **Treat the script runner as your security boundary.**

---

## 🔌 Step 7: Wire Skills into `app.py`

Now connect everything. Three small changes to `app.py`:

**1. Update the imports** — add `SkillsProvider`, `Path`, and the runner:

```python
from pathlib import Path
from agent_framework import Agent, MCPStreamableHTTPTool, SkillsProvider
from subprocess_script_runner import subprocess_script_runner
```

**2. Add a `get_skills_provider()` function** that discovers skills from the `skills/` directory:

```python
def get_skills_provider():
    """Create a SkillsProvider for file-based skills."""
    # Discovers skills from the 'skills' directory and configures the
    # subprocess_script_runner to run file-based scripts.
    skills_dir = Path(__file__).parent / "skills"
    skills_provider = SkillsProvider.from_paths(
        skill_paths=str(skills_dir),
        script_runner=subprocess_script_runner,
    )
    return skills_provider
```

**3. Register it on the agent as a context provider.** Skills are *context*, not tools — they're passed via `context_providers`, not `tools`:

```python
def create_agent():
    """Create a ChatAgent with local, MCP tools and skills."""
    client = get_chat_client()
    mcp_tools = get_mcp_tools()
    skills_provider = get_skills_provider()

    all_tools = [*TOOLS, *mcp_tools]

    agent = Agent(
        client=client,
        name="Aria",
        description="A helpful AI assistant with local, MCP tools and skills",
        instructions=INSTRUCTIONS,
        tools=all_tools,
        context_providers=[skills_provider],   # 👈 skills go here
    )

    return agent
```

**4. Nudge the agent in the system prompt** to actually consult its skills. Add this to `INSTRUCTIONS`:

```python
Before answering, check whether any of your available skills applies to the
request. For questions about internal data (rates, contracts, policies),
never answer from general knowledge — if a skill covers it, use it; if none
does, say so.
```

This is the conceptual heart of the phase: the prompt tells the agent to *prefer its skills over its own memory* for anything domain-specific. That's what stops it from confidently making up a vendor rate.

---

## ▶️ Step 8: Run and Test

```bash
chainlit run app.py -w
```

### Test Scenarios

**Test 1: Vendor rate lookup (data-backed skill)**
```
You: What's Contoso's senior consultant rate, and what would 250 hours cost?
[vendor-rate-lookup skill runs rate_lookup.py]
Aria: Contoso Consulting's Senior Consultant rate is $245/hr under MSA-2024-017.
      At 250 hours the 10% volume discount (200+ hrs) applies → $220.50/hr,
      for a total of $55,125. Cite MSA-2024-017 on procurement paperwork.
```

**Test 2: Contract deadline (deterministic date math)**
```
You: A contract was effective 2024-03-15, 24-month term, 90-day notice. When must we act?
[contract-deadline-calculator skill runs contract_deadlines.py]
Aria: The initial term ends 2026-03-15. Your non-renewal notice deadline is
      2025-12-15 (a Monday). That's the date to act on...
```

**Test 3: Skill *not* applicable (general knowledge)**
```
You: What is Python?
Aria: Python is a programming language...   (no skill triggered)
```

**Test 4: Skills + tools + MCP together (everything from Phases 4–6)**
```
You: What's the weather in Seattle?         → get_weather (local tool)
You: How do I create an Azure storage account?  → microsoft_learn (MCP)
You: What's Fabrikam's data engineer rate?  → vendor-rate-lookup (skill)
```

> ✅ **What to watch for:** ask for a rate the model *can't* know and confirm it runs the script instead of inventing a number. That's the behavior skills exist to guarantee.

---

## 📋 Your Complete `app.py`

```python
"""
Phase 6: Agent with Skills (+ MCP + local tools)
Run with: chainlit run app.py -w

This phase adds file-based Skills on top of the Phase 5 MCP agent.
Skills bundle instructions (SKILL.md), deterministic scripts, and data,
and are loaded with progressive disclosure via a SkillsProvider.

Key Concepts:
- SkillsProvider.from_paths for file-based skill discovery
- A script_runner to execute bundled skill scripts
- context_providers (skills are context, not tools)
"""

import os
from datetime import date
import chainlit as cl
from dotenv import load_dotenv
from pathlib import Path
from agent_framework import Agent, MCPStreamableHTTPTool, SkillsProvider
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

from tools import TOOLS
from subprocess_script_runner import subprocess_script_runner

load_dotenv()

INSTRUCTIONS = f"""You are a helpful AI assistant named Aria.

You have access to multiple tools:
- Local tools: get_weather for weather queries
- MCP tools: Microsoft Learn documentation for technical questions

Before answering, check whether any of your available skills applies to the
request. For questions about internal data (rates, contracts, policies),
never answer from general knowledge — if a skill covers it, use it; if none
does, say so.

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
    """Get MCP tools from external servers."""
    mcp_tools = []
    try:
        # Microsoft Learn MCP Server — Microsoft Learn documentation search
        mcp_tools.append(
            MCPStreamableHTTPTool(
                name="microsoft_learn",
                url="https://learn.microsoft.com/api/mcp"
            )
        )
    except Exception as e:
        print(f"Warning: Could not connect to Microsoft Learn MCP server: {e}")
    return mcp_tools

def get_skills_provider():
    """Create a SkillsProvider for file-based skills.

    Discovers skills from the 'skills' directory and configures the
    subprocess_script_runner to run file-based scripts.
    """
    skills_dir = Path(__file__).parent / "skills"
    skills_provider = SkillsProvider.from_paths(
        skill_paths=str(skills_dir),
        script_runner=subprocess_script_runner,
    )
    return skills_provider

def create_agent():
    """Create a ChatAgent with local, MCP tools and skills."""
    client = get_chat_client()
    mcp_tools = get_mcp_tools()
    skills_provider = get_skills_provider()

    # Combine local tools with MCP tools
    all_tools = [*TOOLS, *mcp_tools]

    agent = Agent(
        client=client,
        name="Aria",
        description="A helpful AI assistant with local, MCP tools and skills",
        instructions=INSTRUCTIONS,
        tools=all_tools,
        context_providers=[skills_provider],
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
├── app.py                          # Agent with local tools + MCP + skills
├── tools.py                        # Local tool definitions
├── subprocess_script_runner.py     # Runs skill scripts as subprocesses
└── skills/
    ├── contract-deadline-calculator/
    │   ├── SKILL.md
    │   └── scripts/
    │       └── contract_deadlines.py
    └── vendor-rate-lookup/
        ├── SKILL.md
        ├── scripts/
        │   └── rate_lookup.py
        └── data/
            └── rate_card.csv
```

---

## 💡 Key Takeaways

Your agent now has three complementary ways to extend itself:

1. **Local tools** — fast, in-process actions (`get_weather`)
2. **MCP tools** — capabilities from external servers (Microsoft Learn)
3. **Skills** — packaged domain expertise: instructions + scripts + data, loaded only when relevant

**Why skills matter:**
- **Reliability** — deterministic scripts replace error-prone "mental math" (dates, table lookups).
- **Grounding** — bundled data (the rate card) stops the model from guessing private facts.
- **Scale** — progressive disclosure means dozens of skills cost almost nothing until triggered.
- **Portability** — a skill is just a folder. Drop it in `skills/` and it's available; delete it and it's gone. No code changes.

### Adding your own skill

```
skills/my-skill/
├── SKILL.md          # name + a trigger-rich description + how-to-use body
├── scripts/          # CLI scripts that print JSON to stdout
└── data/             # optional reference files
```

Write a sharp `description`, make the script take CLI args and emit JSON, and the agent does the rest.

---

## ✅ Checkpoint

| Check | Status |
|-------|--------|
| Phase 5 code copied (`app.py`, `tools.py`) | ☐ |
| `subprocess_script_runner.py` added | ☐ |
| Both skills present under `skills/` | ☐ |
| `SkillsProvider` registered via `context_providers` | ☐ |
| System prompt nudges the agent to prefer skills | ☐ |
| Vendor rate question runs the script (no guessing) | ☐ |
| Contract deadline question returns correct dates | ☐ |
| Weather (tool) and Azure (MCP) still work | ☐ |

### 🎉 Congratulations!

You've completed the workshop! Your agent now:
- ✅ Has a streaming chat UI
- ✅ Remembers conversation history
- ✅ Uses local tools (weather)
- ✅ Connects to remote MCP servers (Microsoft Learn)
- ✅ Loads file-based skills with bundled scripts and data
- ✅ Grounds answers in real data instead of guessing

---

## ❓ Common Issues

### Skills aren't being discovered
- Confirm the `skills/` folder is next to `app.py` and each skill has a `SKILL.md`.
- `SkillsProvider.from_paths` points at the `skills/` directory — check the path in `get_skills_provider()`.
- Each `SKILL.md` needs valid YAML frontmatter with `name` and `description`.

### The agent answers without using the skill
- Strengthen the `description` with more concrete trigger phrases — that's what the model matches on.
- Make sure the "check your skills first" instruction is in `INSTRUCTIONS`.
- Ask more directly ("look up the negotiated rate for…") to confirm the skill *can* fire, then refine the wording.

### Script errors / no output
- Run the script by hand first: `python skills/<skill>/scripts/<script>.py --help`.
- The runner forwards arguments as **positional CLI args** and expects scripts to **print to stdout**.
- For data-backed skills, check relative paths (`rate_lookup.py` reads `../data/rate_card.csv`).

### `[SKILLS]` experimental warning
The Skills APIs are experimental and emit a `FutureWarning`. The sample runner suppresses it with a `warnings.filterwarnings(...)` filter — uncomment it if the warning is noisy.

---

## 🚀 What's Next?

You've built a complete, extensible agent. From here you can:
- Write skills for your own domain — runbooks, calculators, internal-data lookups
- Sandbox the script runner for production (containers, allow-lists, restricted permissions)
- Combine skills with multi-agent workflows
- Share skills as folders across projects and teammates

**Resources:**
- [Microsoft Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [Chainlit Documentation](https://docs.chainlit.io)
```
