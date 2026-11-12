# Agentic AI Workflows (Single & Multi-Agent)

[![GitHub](https://img.shields.io/badge/GitHub-ovalles2019%2Fagentic--ai--workflows-181717?logo=github)](https://github.com/ovalles2019/agentic-ai-workflows)

A hands-on portfolio lab for **LangChain**, **LangGraph**, **CrewAI**, and **AutoGen**. Each example solves the same business task—produce a **market research brief**—using a different orchestration style so you can compare frameworks in interviews and on your resume.

## What you get

| Example | Framework | Pattern | Best for demonstrating |
|---------|-----------|---------|------------------------|
| `01_langchain_single_agent` | LangChain | Single ReAct agent + tools | Tool use, agent loops, minimal orchestration |
| `02_langgraph_multi_agent` | LangGraph | Researcher → Writer → Reviewer graph | Explicit state, conditional routing, retries |
| `03_crewai_multi_agent` | CrewAI | Role-based sequential crew | Task delegation, role prompts, pipelines |
| `04_autogen_multi_agent` | AutoGen | Round-robin conversation | Multi-agent dialogue, emergent collaboration |
| `05_agent_memory` | none (a JSON file) | remember / recall across two sessions | Working memory vs long-term memory |

## Quick start

```bash
git clone https://github.com/ovalles2019/agentic-ai-workflows.git
cd agentic-ai-workflows
./setup.sh
source /tmp/agentic-workflows-venv/bin/activate
```

### Run without API keys (mock mode)

```bash
export MOCK_LLM=1
python run.py all
```

### Run with OpenAI

```bash
# In .env: OPENAI_API_KEY=sk-...
unset MOCK_LLM   # or MOCK_LLM=0
python run.py langgraph --topic "Generative AI in healthcare"
```

### Run a single example

```bash
python -m examples.01_langchain_single_agent
python -m examples.02_langgraph_multi_agent
python -m examples.03_crewai_multi_agent
python -m examples.04_autogen_multi_agent
python -m examples.05_agent_memory
```

## Architecture (same problem, four styles)

```mermaid
flowchart LR
  subgraph LC [LangChain - Single Agent]
    U1[User] --> A1[ReAct Agent]
    A1 --> T1[Tools]
    A1 --> O1[Brief]
  end

  subgraph LG [LangGraph - Graph]
    U2[User] --> R[Researcher]
    R --> W[Writer]
    W --> V[Reviewer]
    V -->|revise| W
    V -->|approved| O2[Brief]
  end

  subgraph CR [CrewAI - Roles]
    U3[User] --> RA[Researcher]
    RA --> ST[Strategist]
    ST --> ED[Editor]
    ED --> O3[Brief]
  end

  subgraph AG [AutoGen - Chat]
    U4[User] --> AN[Analyst]
    AN <--> WR[Writer]
    WR --> O4[Brief]
  end
```

## Project layout

```
shared/           # Config, mock LLM, research tools, memory store
examples/         # Five runnable demos
run.py            # Menu CLI
requirements.txt
.env.example
```

## Framework cheat sheet (interview-ready)

**LangChain** — You define *one* agent that decides when to call tools. Great default for RAG + actions.

**LangGraph** — You define *nodes and edges*; state is first-class. Use when workflows have branches, loops, or human-in-the-loop.

**CrewAI** — You define *roles and tasks*; the framework sequences work. Fastest path to readable multi-agent pipelines.

**AutoGen** — Agents *talk* until termination. Strong for exploratory tasks and critique/revise loops.

## Memory (example 05)

The model does not remember. It only sees the text in this call.

| Kind | Where it lives | Still there next run? |
|------|----------------|------------------------|
| Working memory | The message list for this run | No |
| Long-term memory | `data/memory.json`, via `remember` / `recall` | Yes |

Session 2 in the demo starts with an empty message list. The rollout constraint comes back only because session 1 called `remember`. Matching is keyword overlap: the note has to share words with the query.

`get_memory_tools()` is the same shape as `get_research_tools()`. Pass both into an agent when you want one of the other four examples to read and write that file.

```bash
MOCK_LLM=1 python run.py memory
```

## Resume bullet ideas

- Built comparable **single- and multi-agent** workflows across LangChain, LangGraph, CrewAI, and AutoGen for market research automation.
- Implemented **LangGraph** conditional routing (review/revise loop) with shared tool-backed state.
- Designed **CrewAI** sequential crews with role-specific agents and task context chaining.

## Notes

- **Mock mode** uses `FakeListChatModel` for LangChain/LangGraph/CrewAI; AutoGen prints a simulated transcript.
- Tools use a **deterministic knowledge base** (no live web scraping) so demos are reliable.
- For production, add observability (LangSmith, OpenTelemetry), auth for tools, and evaluation harnesses.

## License

MIT — use freely for learning and portfolio projects.
