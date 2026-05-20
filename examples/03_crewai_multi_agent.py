"""
Multi-agent workflow (CrewAI).

Role-based crew: Researcher -> Strategist -> Editor (sequential process).
Run: python -m examples.03_crewai_multi_agent
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from crewai import Agent, Crew, Process, Task

from shared.config import get_settings
from shared.llm import get_chat_model
from shared.mock_runner import run_research_pipeline
from shared.tools import get_research_tools


def run(topic: str | None = None) -> str:
    settings = get_settings()
    topic = topic or settings.default_topic

    print(f"\n=== CrewAI multi-agent | mock={settings.use_mock} ===")
    print(f"Topic: {topic}\n")

    if settings.use_mock:
        result = run_research_pipeline(topic)
        print("[Researcher] gathered tool-backed notes")
        print("[Strategist] drafted brief from notes")
        print("[Editor] polished final copy\n")
        print(result["brief"])
        return result["brief"]

    llm = get_chat_model(settings)
    tools = get_research_tools()

    researcher = Agent(
        role="Market Research Analyst",
        goal="Collect structured facts about the topic using available tools.",
        backstory="You synthesize messy market signals into crisp research notes.",
        llm=llm,
        tools=tools,
        verbose=True,
        allow_delegation=False,
    )

    strategist = Agent(
        role="Product Strategy Lead",
        goal="Turn research notes into a decision-ready brief.",
        backstory="You write for executives and focus on tradeoffs and next steps.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    editor = Agent(
        role="Executive Editor",
        goal="Polish the brief for clarity and remove redundancy.",
        backstory="You enforce tight writing and consistent section headers.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    research_task = Task(
        description=(
            f"Research '{topic}'. Use tools where helpful. "
            "Output bullet notes covering market, competitors, and risks."
        ),
        expected_output="Bullet-point research notes (max 200 words).",
        agent=researcher,
    )

    strategy_task = Task(
        description="Using the research notes, draft a brief with sections: Market, Competition, Risks, Recommendation.",
        expected_output="A structured markdown brief (max 250 words).",
        agent=strategist,
        context=[research_task],
    )

    edit_task = Task(
        description="Edit the brief for executive readability. Keep all four sections.",
        expected_output="Final polished brief ready to send to stakeholders.",
        agent=editor,
        context=[strategy_task],
    )

    crew = Crew(
        agents=[researcher, strategist, editor],
        tasks=[research_task, strategy_task, edit_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff(inputs={"topic": topic})
    output = str(result)
    print("\n--- Final output ---")
    print(output)
    return output


if __name__ == "__main__":
    run()
