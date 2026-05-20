"""Deterministic offline runner when MOCK_LLM=1 (no API / no tool-binding LLM)."""

from __future__ import annotations

from shared.tools import search_market_intel, estimate_tam


def run_research_pipeline(topic: str) -> dict[str, str]:
    notes = search_market_intel.invoke({"query": f"{topic} market competitors risks"})
    tam = estimate_tam.invoke({"segment": topic})
    brief = f"""# Research Brief: {topic}

## Market
Enterprise AI coding assistant spend is growing; buyers prioritize security and IDE fit.

## Competition
Major vendors compete on integration depth, governance, and workflow automation.

## Risks
IP leakage, uneven adoption, and compliance gaps remain top enterprise concerns.

## Recommendation
Run a 90-day pilot with PR-cycle-time and defect-rate metrics. {tam}

---
Source notes:
{notes}
"""
    return {"research_notes": notes, "brief": brief}
