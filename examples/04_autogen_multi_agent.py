"""
Multi-agent workflow (Microsoft AutoGen).

Conversational team: Analyst and Writer discuss until the Writer publishes the brief.
Run: python -m examples.04_autogen_multi_agent
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.config import get_settings


def _mock_conversation(topic: str) -> str:
    transcript = [
        ("Analyst", f"For '{topic}', enterprise demand is strong but security review is the gate."),
        ("Writer", "Drafting brief sections: Market, Competition, Risks, Recommendation."),
        ("Analyst", "Add a 90-day pilot recommendation with PR-cycle-time metrics."),
        ("Writer", "Final brief ready. Recommendation: controlled pilot with governance checks."),
    ]
    print("\n=== AutoGen multi-agent (mock conversation) ===\n")
    for speaker, line in transcript:
        print(f"{speaker}: {line}")
    return transcript[-1][1]


async def _run_live(topic: str, settings) -> str:
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    model_client = OpenAIChatCompletionClient(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
    )

    analyst = AssistantAgent(
        name="Analyst",
        model_client=model_client,
        system_message=(
            "You are a market analyst. Provide facts and challenge weak assumptions. "
            "Keep replies under 120 words."
        ),
    )

    writer = AssistantAgent(
        name="Writer",
        model_client=model_client,
        system_message=(
            "You are a strategy writer. Collaborate with Analyst, then produce a final brief. "
            "When done, end with: BRIEF_COMPLETE"
        ),
    )

    termination = MaxMessageTermination(6) | TextMentionTermination("BRIEF_COMPLETE")

    team = RoundRobinGroupChat([analyst, writer], termination_condition=termination)

    print(f"\n=== AutoGen multi-agent | mock={settings.use_mock} ===")
    print(f"Topic: {topic}\n")

    result = await Console(
        team.run(task=f"Create a research brief for: {topic}")
    )
    await model_client.close()
    return str(result)


def run(topic: str | None = None) -> str:
    settings = get_settings()
    topic = topic or settings.default_topic

    if settings.use_mock:
        return _mock_conversation(topic)

    return asyncio.run(_run_live(topic, settings))


if __name__ == "__main__":
    run()
