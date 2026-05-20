"""
Multi-agent workflow (LangGraph).

Explicit graph: Researcher -> Writer -> Reviewer (conditional loop).
Run: python -m examples.02_langgraph_multi_agent
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Literal, TypedDict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from shared.config import get_settings
from shared.llm import get_chat_model
from shared.tools import search_market_intel


class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    topic: str
    research_notes: str
    draft_brief: str
    review_status: str
    revision_count: int


def researcher_node(state: ResearchState) -> dict:
    settings = get_settings()
    llm = get_chat_model(settings)
    topic = state["topic"]

    # Always ground the graph in tool output (works in mock and live modes).
    tool_output = search_market_intel.invoke({"query": f"{topic} market competitors risks"})

    prompt = [
        SystemMessage(content="You are a research analyst. Summarize findings in bullet points."),
        HumanMessage(content=f"Topic: {topic}\n\nRaw notes:\n{tool_output}"),
    ]
    response = llm.invoke(prompt)
    return {"research_notes": str(response.content), "messages": [response]}


def writer_node(state: ResearchState) -> dict:
    settings = get_settings()
    llm = get_chat_model(settings)
    prompt = [
        SystemMessage(content="You are a strategy writer. Produce a stakeholder-ready brief."),
        HumanMessage(
            content=(
                f"Topic: {state['topic']}\n\nResearch:\n{state['research_notes']}\n\n"
                "Format: Market, Competition, Risks, Recommendation."
            )
        ),
    ]
    response = llm.invoke(prompt)
    return {"draft_brief": str(response.content), "messages": [response]}


def reviewer_node(state: ResearchState) -> dict:
    settings = get_settings()
    llm = get_chat_model(settings)
    prompt = [
        SystemMessage(
            content=(
                "You are a strict reviewer. Reply with EXACTLY one token: "
                "APPROVED or REVISE. Use REVISE only if the brief is missing a section."
            )
        ),
        HumanMessage(content=state["draft_brief"]),
    ]
    response = llm.invoke(prompt)
    status = "APPROVED" if "APPROVED" in str(response.content).upper() else "REVISE"
    return {
        "review_status": status,
        "revision_count": state.get("revision_count", 0) + (1 if status == "REVISE" else 0),
        "messages": [AIMessage(content=f"Review: {status}")],
    }


def route_after_review(state: ResearchState) -> Literal["writer", "end"]:
    if state.get("review_status") == "APPROVED":
        return "end"
    if state.get("revision_count", 0) >= 2:
        return "end"
    return "writer"


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("reviewer", reviewer_node)

    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_conditional_edges(
        "reviewer",
        route_after_review,
        {"writer": "writer", "end": END},
    )
    return graph.compile()


def run(topic: str | None = None) -> dict:
    settings = get_settings()
    topic = topic or settings.default_topic
    app = build_graph()

    print(f"\n=== LangGraph multi-agent | mock={settings.use_mock} ===")
    print(f"Topic: {topic}\n")

    result = app.invoke(
        {
            "messages": [HumanMessage(content=f"Create a research brief for: {topic}")],
            "topic": topic,
            "research_notes": "",
            "draft_brief": "",
            "review_status": "",
            "revision_count": 0,
        }
    )

    print("--- Research notes ---")
    print(result["research_notes"])
    print("\n--- Draft brief ---")
    print(result["draft_brief"])
    print(f"\n--- Review: {result['review_status']} (revisions: {result['revision_count']}) ---")
    return result


if __name__ == "__main__":
    run()
