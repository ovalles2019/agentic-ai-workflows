"""Deterministic research tools used across framework demos."""

from __future__ import annotations

from langchain_core.tools import tool

# Curated snippets so demos work without live web search.
KNOWLEDGE_BASE: dict[str, str] = {
    "market": (
        "Enterprise AI coding assistant spend is growing ~35% YoY. "
        "Buyers prioritize security reviews, IDE integration, and measurable "
        "developer productivity gains."
    ),
    "competitors": (
        "Major players include GitHub Copilot, Cursor, Amazon Q Developer, "
        "and Tabnine. Differentiation often centers on context window, "
        "on-prem options, and workflow automation."
    ),
    "risks": (
        "Top risks: IP leakage, hallucinated refactors, uneven junior/senior "
        "adoption, and compliance gaps in regulated industries."
    ),
    "recommendation": (
        "Pilot with a bounded repo, define success metrics (PR cycle time, "
        "defect rate), and run security review before org-wide rollout."
    ),
}


@tool
def search_market_intel(query: str) -> str:
    """Search internal market research notes for a topic."""
    query_lower = query.lower()
    hits = [
        f"[{key}] {text}"
        for key, text in KNOWLEDGE_BASE.items()
        if key in query_lower or any(word in text.lower() for word in query_lower.split())
    ]
    if not hits:
        hits = [f"[{k}] {v}" for k, v in KNOWLEDGE_BASE.items()]
    return "\n".join(hits[:3])


@tool
def estimate_tam(segment: str) -> str:
    """Return a rough TAM estimate for a market segment (illustrative)."""
    return (
        f"Illustrative TAM for '{segment}': $4.2B (2025), "
        "assuming 2.1M paid seats at ~$19/seat/month blended."
    )


def get_research_tools():
    return [search_market_intel, estimate_tam]
