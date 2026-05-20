"""
Single-agent workflow (LangChain).

One ReAct-style agent orchestrates tool calls and produces the final brief.
Run: python -m examples.01_langchain_single_agent
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain.agents import create_agent

from shared.config import get_settings
from shared.llm import get_chat_model
from shared.mock_runner import run_research_pipeline
from shared.tools import get_research_tools


def run(topic: str | None = None) -> str:
    settings = get_settings()
    topic = topic or settings.default_topic

    print(f"\n=== LangChain single-agent | mock={settings.use_mock} ===")
    print(f"Topic: {topic}\n")

    if settings.use_mock:
        result = run_research_pipeline(topic)
        print("[tool] search_market_intel")
        print(result["research_notes"][:300], "...\n")
        print("[tool] estimate_tam")
        print(result["brief"])
        return result["brief"]

    model = get_chat_model(settings)
    tools = get_research_tools()
    system_prompt = (
        "You are a market research analyst. Use tools to gather facts, "
        "then write a concise executive brief with sections: Market, "
        "Competition, Risks, Recommendation. Keep it under 250 words."
    )
    agent = create_agent(model, tools, system_prompt=system_prompt)

    final_message = None
    for step in agent.stream(
        {"messages": [{"role": "user", "content": f"Research brief for: {topic}"}]},
        stream_mode="values",
    ):
        msg = step["messages"][-1]
        msg.pretty_print()
        final_message = msg

    return str(getattr(final_message, "content", final_message))


if __name__ == "__main__":
    run()
